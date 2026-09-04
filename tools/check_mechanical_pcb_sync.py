#!/usr/bin/env python3
"""CI gate: cross-check a mechanical enclosure's board-geometry constants
against the real PCB layout they are supposed to fit.

This exists directly because of MISS-034 (CRITICAL, validation/open-issues.md):
`hardware/mechanical/bench-imu-01-enclosure.scad` recorded `pcb_length`=100.0
and `pcb_width`=50.0, a Rev 3 PROPOSAL, for over 2 days and 3 merged PRs after
the real PCB was laid out at 150x95mm -- no tool caught the drift, only a
scheduled audit loop measuring real geometry by hand. See docs/workflow.md
section 4.2.1 ("Cross-Discipline Handoff Snapshot Drift") for the general
failure mode this is a concrete, narrow instance of.

Unlike tools/check_open_issues.py's or tools/check_id_uniqueness.py's own
free-text/table parsing, the two facts compared here are both small,
structured, numeric quantities from two machine-generated file formats (an
OpenSCAD `.scad` source and a KiCad `.kicad_pcb` s-expression file) -- an
exact comparison, not the fuzzy "does an old value's numeric string still
appear somewhere" grep this repo's own docs/workflow.md section 4.2
explicitly judges unreliable for free-text prose. That is what makes this a
reasonable CI check where the general case (section 4.2) is deliberately
left as a human process convention instead.

What this checks, for every `(board_scad, board_kicad_pcb)` pair discovered
under hardware/mechanical/*.scad / hardware/pcb/*/*.kicad_pcb (today, exactly
one pair: bench-imu-01):
  1. `pcb_length`/`pcb_width` in the `.scad` file match the real board's
     `Edge.Cuts` `gr_rect` outline, within a small floating-point tolerance.
  2. The `.scad` file's `mount_holes` array (count and X/Y positions) matches
     the real board's own `MountingHole_*` footprint positions exactly (as a
     set -- ordering is not significant), within tolerance.

Deliberately NOT checked here (out of this tool's own narrow scope, same
scope MISS-034 itself drew, see MISS-037): connector/component cutout
positions (J1-J4/SW1/D1/etc.) against the real PCB's own placement -- that
would need real footprint/courtyard geometry, not just two scalar pairs and
a hole list, and is a materially larger, separate undertaking (tracked
separately, not silently subsumed into this tool's name).

Discovery convention: this script pairs a `.scad` file
`hardware/mechanical/<name>-enclosure.scad` with a `.kicad_pcb` file
`hardware/pcb/<name>/<name>.kicad_pcb` by matching the `<name>` stem. A
`.scad` file with no matching PCB project (or vice versa) is skipped, not
an error -- not every mechanical design necessarily has a KiCad project yet
(this repo's own Phase 1 explicitly allows a paper-design-only cycle).
"""
from __future__ import annotations

import pathlib
import re
import sys
from typing import NamedTuple

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
MECHANICAL_DIR = REPO_ROOT / "hardware" / "mechanical"
PCB_DIR = REPO_ROOT / "hardware" / "pcb"

# Floating-point comparison tolerance, mm. Both source formats store plain
# decimal literals (no unit ambiguity), so this only needs to absorb
# formatting/rounding noise, not a real unit-conversion error band.
TOLERANCE_MM = 0.01


class BoardOutline(NamedTuple):
    length_x: float
    width_y: float


class MountHole(NamedTuple):
    x: float
    y: float


def find_project_pairs() -> list[tuple[str, pathlib.Path, pathlib.Path]]:
    """Returns (name, scad_path, kicad_pcb_path) for every enclosure `.scad`
    file that has a same-named KiCad project directory. Both directories are
    optional/may not exist yet (a fresh checkout of a docs-only branch, or a
    project with no mechanical/PCB work yet) -- that is not itself an error,
    just zero pairs found."""
    pairs = []
    if not MECHANICAL_DIR.is_dir() or not PCB_DIR.is_dir():
        return pairs
    for scad_path in sorted(MECHANICAL_DIR.glob("*-enclosure.scad")):
        name = scad_path.name[: -len("-enclosure.scad")]
        kicad_pcb_path = PCB_DIR / name / f"{name}.kicad_pcb"
        if kicad_pcb_path.is_file():
            pairs.append((name, scad_path, kicad_pcb_path))
    return pairs


def parse_scad_board(scad_text: str) -> tuple[BoardOutline, list[MountHole]] | None:
    """Extracts `pcb_length`/`pcb_width` (first top-level assignment of each
    -- the parametric source of truth this whole file's cascade is derived
    from, matching bench-imu-01-enclosure.scad's own Section 1 convention)
    and the `mount_holes` array's [x, y, ...] entries."""
    length_m = re.search(r"^\s*pcb_length\s*=\s*([0-9.]+)\s*;", scad_text, re.MULTILINE)
    width_m = re.search(r"^\s*pcb_width\s*=\s*([0-9.]+)\s*;", scad_text, re.MULTILINE)
    if not length_m or not width_m:
        return None
    outline = BoardOutline(length_x=float(length_m.group(1)), width_y=float(width_m.group(1)))

    holes_m = re.search(r"mount_holes\s*=\s*\[(.*?)\];", scad_text, re.DOTALL)
    holes: list[MountHole] = []
    if holes_m:
        # Each entry looks like `[ 8.0,  8.0, 2.8]` (whitespace/comments vary).
        for entry in re.finditer(r"\[\s*([0-9.]+)\s*,\s*([0-9.]+)\s*,\s*[0-9.]+\s*\]", holes_m.group(1)):
            holes.append(MountHole(x=float(entry.group(1)), y=float(entry.group(2))))
    return outline, holes


def parse_kicad_board(pcb_text: str) -> tuple[BoardOutline, list[MountHole]] | None:
    """Extracts the real board outline from the Edge.Cuts `gr_rect` and every
    `MountingHole_*` footprint's own `(at X Y ...)` position. Deliberately a
    small, targeted regex parser (mirroring this repo's own
    hardware/mechanical/drawings/drafting-sheets/build_drafting_sheet.py
    precedent of a small hand-written parser over a full s-expression
    library dependency) -- sufficient for these two specific, narrow facts,
    not a general KiCad file parser."""
    outline = None
    # Find every gr_rect block and check whether its own nested layer is
    # Edge.Cuts (a gr_rect can appear on other layers too, e.g. F.CrtYd).
    for m in re.finditer(
        r"\(gr_rect\s*\(start\s+([0-9.\-]+)\s+([0-9.\-]+)\)\s*\(end\s+([0-9.\-]+)\s+([0-9.\-]+)\)"
        r"(?:(?!\(gr_).)*?\(layer\s+\"([^\"]+)\"\)",
        pcb_text,
        re.DOTALL,
    ):
        if m.group(5) == "Edge.Cuts":
            x0, y0, x1, y1 = (float(m.group(i)) for i in (1, 2, 3, 4))
            outline = BoardOutline(length_x=abs(x1 - x0), width_y=abs(y1 - y0))
            break
    if outline is None:
        return None

    holes: list[MountHole] = []
    for fp_block in re.finditer(
        r'\(footprint\s+"MountingHole[^"]*".*?(?=\n\t\(footprint\s|\Z)', pcb_text, re.DOTALL
    ):
        at_m = re.search(r"\(at\s+([0-9.\-]+)\s+([0-9.\-]+)", fp_block.group(0))
        if at_m:
            holes.append(MountHole(x=float(at_m.group(1)), y=float(at_m.group(2))))
    return outline, holes


def close(a: float, b: float) -> bool:
    return abs(a - b) <= TOLERANCE_MM


def match_hole_sets(scad_holes: list[MountHole], real_holes: list[MountHole]) -> list[str]:
    """Order-independent comparison (mount_holes' own array order in the
    .scad has no required correspondence to KiCad's own footprint-placement
    order in the file) -- greedily pairs each scad hole with its closest
    unmatched real hole. Returns a list of human-readable problem
    descriptions (empty if every hole matches within TOLERANCE_MM)."""
    problems = []
    if len(scad_holes) != len(real_holes):
        problems.append(
            f"hole count mismatch: .scad mount_holes has {len(scad_holes)}, "
            f"real board has {len(real_holes)} MountingHole footprint(s)"
        )
        return problems  # count mismatch already makes a 1:1 pairing meaningless
    remaining = list(real_holes)
    for sh in scad_holes:
        best = min(remaining, key=lambda rh: (rh.x - sh.x) ** 2 + (rh.y - sh.y) ** 2, default=None)
        if best is None or not (close(sh.x, best.x) and close(sh.y, best.y)):
            nearest = f" (nearest real hole: {best})" if best else ""
            problems.append(f".scad hole {sh} has no matching real board hole within {TOLERANCE_MM}mm{nearest}")
        else:
            remaining.remove(best)
    return problems


def main() -> int:
    pairs = find_project_pairs()
    if not pairs:
        # DELIBERATE FAIL-LOUD, not a silent pass (found and fixed this session,
        # adversarially, by an independent cross-session review -- a genuine
        # near-miss, not hypothetical): "zero pairs discovered" must not exit 0.
        # Unlike tools/check_open_issues.py's own "if not spec.path.exists():
        # return" tolerance (a specific, individually-optional file legitimately
        # not existing yet), this script's OWN discovery mechanism finding
        # NOTHING to check is a different, more concerning signal in this repo's
        # current and foreseeable state -- MECHANICAL_DIR/PCB_DIR are always
        # expected to contain at least the bench-imu-01 pair. A silent exit 0
        # here would mean this gate goes green at the exact moment it has lost
        # the ability to see the thing it guards (a directory rename, a glob
        # pattern no longer matching a future project's naming, an invocation
        # from an unexpected working directory) -- indistinguishable from "I
        # checked and it was fine" unless this is loud. If a genuinely
        # zero-pairs repository state is ever legitimate (e.g. a fresh
        # docs-only checkout with no mechanical/PCB work yet at all), that is
        # a real enough exception to require a human/CI maintainer to
        # explicitly adjust this script at that time, not a default this
        # script should assume silently.
        print(
            "check_mechanical_pcb_sync: FAIL -- discovered ZERO (enclosure .scad, "
            "KiCad project) pairs to check, in a repository state where at least "
            "one (bench-imu-01) is expected to exist. Treating this as a failure, "
            "not a silent pass, since a passing check that verified nothing is "
            "worse than no check at all -- see this function's own comment for "
            "the reasoning and how to update this script if a zero-pairs state "
            "is ever genuinely expected."
        )
        return 1

    exit_code = 0
    for name, scad_path, kicad_pcb_path in pairs:
        scad_rel = scad_path.relative_to(REPO_ROOT)
        pcb_rel = kicad_pcb_path.relative_to(REPO_ROOT)
        print(f"Checking {scad_rel} against {pcb_rel} ...")

        scad_parsed = parse_scad_board(scad_path.read_text())
        if scad_parsed is None:
            print(f"  SKIP: could not find pcb_length/pcb_width in {scad_rel} (unexpected file shape)")
            continue
        real_parsed = parse_kicad_board(kicad_pcb_path.read_text())
        if real_parsed is None:
            print(f"  SKIP: could not find an Edge.Cuts gr_rect outline in {pcb_rel} (unexpected file shape)")
            continue

        scad_outline, scad_holes = scad_parsed
        real_outline, real_holes = real_parsed

        problems = []
        if not close(scad_outline.length_x, real_outline.length_x):
            problems.append(
                f"pcb_length={scad_outline.length_x}mm in {scad_rel} != real board X extent "
                f"{real_outline.length_x}mm from {pcb_rel}'s own Edge.Cuts"
            )
        if not close(scad_outline.width_y, real_outline.width_y):
            problems.append(
                f"pcb_width={scad_outline.width_y}mm in {scad_rel} != real board Y extent "
                f"{real_outline.width_y}mm from {pcb_rel}'s own Edge.Cuts"
            )
        problems.extend(match_hole_sets(scad_holes, real_holes))

        if problems:
            exit_code = 1
            print(f"  FAIL ({len(problems)} problem(s)):")
            for p in problems:
                print(f"    - {p}")
        else:
            print(
                f"  OK: board outline {scad_outline.length_x}x{scad_outline.width_y}mm and "
                f"{len(scad_holes)} mounting hole(s) match the real KiCad project exactly."
            )

    if exit_code != 0:
        print(
            "\nMechanical<->PCB sync check FAILED -- a mechanical enclosure's own recorded "
            "board geometry no longer matches the real PCB layout. This is exactly the class "
            "of defect MISS-034 was (validation/open-issues.md) -- see docs/workflow.md "
            "section 4.2.1 for the resolution convention: re-run the Electronics-to-Mechanical "
            "handoff (docs/workflow.md Phase 8) against the real outline/hole pattern before "
            "merging."
        )
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
