#!/usr/bin/env python3
"""CI gate for duplicate IDs in this repo's shared, cross-branch namespaces.

Three files use a flat, monotonically-increasing ID namespace that any
session/branch can append rows to:
  - `ECO-<NNN>`            in validation/change-log.md
  - `ISS-<NNN>`/`MISS-<NNN>` in validation/open-issues.md
  - `DS-<CATEGORY>-<NNN>`  in datasheets/evidence-log.md (architecture.md §6.3)

When two branches diverge from the same baseline and each independently
appends a new row to one of these files, each branch can only see its own
view of the namespace at allocation time -- it has no way to know what a
sibling branch is concurrently allocating. If both pick the same
next-available number for unrelated content, the result is a genuine ID
collision once the branches merge. Git's own merge does **not** catch this:
two branches each appending a new table row is a clean, non-conflicting
text merge (different/independent lines) even though the result now has two
different rows sharing one ID -- the collision is semantic, not textual.

This is not hypothetical: this repository's own bench-imu-01-rev3 branch
merged `main` twice and produced this exact class of collision both times
(ECO-006..012 / ISS-014 / DS-MCU-064..068 the first time; a second,
different DS-MCU-069 collision the second time, since the first merge's
renumbering had already claimed that slot) -- see validation/change-log.md
ECO-014/ECO-018 on that branch, and docs/workflow.md section 4.1 for the
resolution convention this check exists to make easy to enforce.

Mirrors tools/check_open_issues.py's parsing approach (find the real
Backlog/Log table by matching its header row, stop at the first blank/
non-table line after it) generalized across all three files, with line
numbers tracked so a collision report names both duplicate rows precisely
instead of just a bare count.
"""
from __future__ import annotations

import pathlib
import re
import sys
from typing import NamedTuple

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

# Max characters of a row's content shown per collision line, so a report
# stays readable even though real rows in this repo can be very long
# free-text paragraphs.
SNIPPET_MAX_LEN = 160


class NamespaceSpec(NamedTuple):
    label: str
    path: pathlib.Path
    header_prefix: list[str]
    id_pattern: re.Pattern[str]


NAMESPACES: list[NamespaceSpec] = [
    NamespaceSpec(
        label="ECO",
        path=REPO_ROOT / "validation" / "change-log.md",
        header_prefix=["ECO ID", "Date"],
        id_pattern=re.compile(r"^ECO-\d+$"),
    ),
    NamespaceSpec(
        label="Open Issues",
        path=REPO_ROOT / "validation" / "open-issues.md",
        header_prefix=["ID", "Severity", "Status"],
        id_pattern=re.compile(r"^(ISS|MISS)-\d+$"),
    ),
    NamespaceSpec(
        label="Evidence ID",
        path=REPO_ROOT / "datasheets" / "evidence-log.md",
        header_prefix=["Evidence ID", "Datasheet metadata record"],
        id_pattern=re.compile(r"^DS-[A-Z]+-\d+$"),
    ),
]


def _split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_separator_row(cells: list[str]) -> bool:
    return all(set(cell) <= {"-", " ", ":"} and cell != "" for cell in cells)


def _is_placeholder(id_cell: str) -> bool:
    """True for template/illustrative rows, e.g. `<ECO-XXX>` or `ISS-XXX`."""
    return not id_cell or id_cell.startswith("<") or "XXX" in id_cell.upper()


def parse_table_rows(text: str, header_prefix: list[str]) -> list[tuple[int, list[str]]]:
    """Return (1-based line number, cells) for each data row of the first
    Markdown table whose header matches header_prefix, stopping at the
    first blank/non-table line after the header -- so an unrelated table
    earlier in the file (e.g. an SLA policy table) or a template section
    elsewhere is never mistaken for the real data table.
    """
    lines = text.splitlines()

    header_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = _split_row(stripped)
        if cells[: len(header_prefix)] == header_prefix:
            header_idx = i
            break

    if header_idx is None:
        return []

    j = header_idx + 1
    if j < len(lines) and lines[j].strip().startswith("|"):
        if _is_separator_row(_split_row(lines[j])):
            j += 1

    rows: list[tuple[int, list[str]]] = []
    while j < len(lines):
        line = lines[j].strip()
        if not line.startswith("|"):
            break  # first blank/non-table line ends the data table
        cells = _split_row(line)
        if any(cell != "" for cell in cells):
            rows.append((j + 1, cells))
        j += 1
    return rows


def _snippet(cells: list[str]) -> str:
    text = " | ".join(cells)
    if len(text) > SNIPPET_MAX_LEN:
        text = text[: SNIPPET_MAX_LEN - 3] + "..."
    return text


def check_namespace(spec: NamespaceSpec) -> tuple[int, list[str]]:
    """Return (well-formed IDs checked, violation messages) for one namespace."""
    if not spec.path.exists():
        return 0, []  # nothing to check yet, mirrors check_open_issues.py's tolerance

    text = spec.path.read_text(encoding="utf-8")
    rows = parse_table_rows(text, spec.header_prefix)

    seen: dict[str, list[tuple[int, str]]] = {}
    checked = 0
    for line_no, cells in rows:
        if not cells:
            continue
        id_cell = cells[0]
        if _is_placeholder(id_cell) or not spec.id_pattern.match(id_cell):
            continue  # not a well-formed ID for this namespace; format checks are out of scope here
        checked += 1
        seen.setdefault(id_cell, []).append((line_no, _snippet(cells)))

    rel_path = spec.path.relative_to(REPO_ROOT)
    violations: list[str] = []
    for id_value, occurrences in seen.items():
        if len(occurrences) < 2:
            continue
        detail = "\n".join(f"    line {ln}: {snip}" for ln, snip in occurrences)
        violations.append(
            f"Duplicate {id_value} in {rel_path} ({len(occurrences)} rows):\n{detail}"
        )
    return checked, violations


def main() -> int:
    total_checked = 0
    all_violations: list[str] = []

    for spec in NAMESPACES:
        checked, violations = check_namespace(spec)
        total_checked += checked
        all_violations.extend(violations)

    if all_violations:
        print("ID uniqueness check FAILED - duplicate IDs in a shared namespace:")
        for v in all_violations:
            print(f"  - {v}")
        print(
            "\nThis is a cross-branch merge hazard, not a design defect: two "
            "branches diverged from the same baseline and each independently "
            "allocated the same next-available ID for unrelated content. See "
            "docs/workflow.md section 4.1 for the resolution convention -- "
            "renumber one side to the next free ID in the union of both "
            "namespaces, grep the WHOLE repo (not just the defining file) for "
            "every stale citation of the old ID, then re-run this check."
        )
        return 1

    print(
        f"OK: no duplicate IDs found across {len(NAMESPACES)} namespace(s) "
        f"({total_checked} ID(s) checked)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
