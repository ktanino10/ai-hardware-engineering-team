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
Backlog/Log table by matching its header row) generalized across all
three files, with line numbers tracked so a collision report names both
duplicate rows precisely instead of just a bare count. Unlike a naive
"stop at the first blank/non-table line after the header" rule, a lone
stray blank line accidentally inserted between two data rows does not by
itself end the table here -- see parse_table_rows()'s docstring for why
that distinction was added (it fixes a real incident, not a hypothetical
one: 7 stray blank lines in validation/change-log.md silently truncated
ECO scanning to 12 of 26 real rows all session, on this branch and on
`main`, with the original stop-at-first-blank-line version of this
function).
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


def parse_table_rows(
    text: str,
    header_prefix: list[str],
    id_pattern: re.Pattern[str] | None = None,
    source_label: str = "",
) -> tuple[list[tuple[int, list[str]]], list[str]]:
    """Return ((1-based line number, cells) rows, warning messages) for the
    first Markdown table whose header matches header_prefix.

    Locating the RIGHT table (as opposed to an unrelated one, e.g. an SLA
    policy table or a template section elsewhere in the file) is done by
    matching the header row's own leading cells against header_prefix --
    unchanged from the original design.

    Deciding where that table's data ROWS actually END is the part this
    function hardens. A genuine end-of-table boundary is a real section
    break: a non-blank line that is not itself a table row (typically a
    Markdown heading, e.g. "## Notes"), or EOF. A lone blank line between
    two otherwise-adjacent data rows is NOT, by itself, treated as a
    boundary: scanning looks past the whole run of blank lines, and if a
    well-formed row follows -- same column count as the header, AND (when
    id_pattern is given) an ID cell that actually matches this namespace's
    own ID pattern or is a recognized placeholder -- the gap is treated as
    a stray/accidental blank line: it is skipped (with a warning recorded,
    never silently) and scanning continues past it. The id_pattern check
    matters on its own: column count alone isn't a safe enough signal, since
    a genuinely different, unrelated table (e.g. a differently-scoped
    two-column table elsewhere) could coincidentally share the same column
    count as the real data table and get wrongly merged in without it.

    This distinction matters because the previous version of this function
    stopped scanning, unconditionally and silently, at the FIRST line that
    didn't start with "|" after the header -- whether that line was a real
    section boundary or just a stray blank line accidentally inserted
    between two data rows. That silently truncated `validation/change-log.md`
    ECO scanning to only 12 of 26 real rows for an entire session (7 stray
    blank lines had accumulated between ECO-012 and later rows, the first
    one right after ECO-012) -- with zero warning that anything was wrong,
    on this branch *and* on `main` itself. See ECO-033 / the commit that
    introduced this hardening for the full incident writeup.
    """
    lines = text.splitlines()

    header_idx = None
    header_cells: list[str] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = _split_row(stripped)
        if cells[: len(header_prefix)] == header_prefix:
            header_idx = i
            header_cells = cells
            break

    if header_idx is None:
        return [], []

    expected_ncols = len(header_cells)
    label = f"{source_label}: " if source_label else ""

    j = header_idx + 1
    if j < len(lines) and lines[j].strip().startswith("|"):
        if _is_separator_row(_split_row(lines[j])):
            j += 1

    rows: list[tuple[int, list[str]]] = []
    warnings: list[str] = []
    while j < len(lines):
        stripped = lines[j].strip()

        if stripped.startswith("|"):
            cells = _split_row(stripped)
            if any(cell != "" for cell in cells):
                rows.append((j + 1, cells))
            j += 1
            continue

        if stripped == "":
            # Could be a legitimate end-of-table blank line (e.g. right
            # before a "## Notes" heading or EOF) or a stray gap
            # accidentally inserted between two data rows. Look past the
            # *whole* run of blank lines to see which.
            gap_start = j
            k = j
            while k < len(lines) and lines[k].strip() == "":
                k += 1
            if k < len(lines):
                next_stripped = lines[k].strip()
                if next_stripped.startswith("|"):
                    next_cells = _split_row(next_stripped)
                    id_cell = next_cells[0] if next_cells else ""
                    id_plausible = (
                        id_pattern is None
                        or _is_placeholder(id_cell)
                        or bool(id_pattern.match(id_cell))
                    )
                    if (
                        len(next_cells) == expected_ncols
                        and not _is_separator_row(next_cells)
                        and id_plausible
                    ):
                        n_blank = k - gap_start
                        warnings.append(
                            f"{label}line {gap_start + 1}: skipped "
                            f"{n_blank} stray blank line(s) between table "
                            f"rows (table resumes at line {k + 1}) -- "
                            "remove the blank line(s); a stray blank line "
                            "here previously truncated scanning silently."
                        )
                        j = k
                        continue
            # Not followed by more of the same table -- a genuine
            # end-of-table blank line (heading or EOF next). Stop, no
            # warning: this is the normal, expected shape.
            break

        # A non-blank line that isn't a table row at all (typically a
        # heading) always ends the table -- unambiguous, no warning needed.
        break

    return rows, warnings


def _snippet(cells: list[str]) -> str:
    text = " | ".join(cells)
    if len(text) > SNIPPET_MAX_LEN:
        text = text[: SNIPPET_MAX_LEN - 3] + "..."
    return text


def check_namespace(spec: NamespaceSpec) -> tuple[int, list[str], list[str]]:
    """Return (well-formed IDs checked, violation messages, parser warnings)
    for one namespace."""
    if not spec.path.exists():
        return 0, [], []  # nothing to check yet, mirrors check_open_issues.py's tolerance

    text = spec.path.read_text(encoding="utf-8")
    rel_path = spec.path.relative_to(REPO_ROOT)
    rows, parse_warnings = parse_table_rows(
        text, spec.header_prefix, id_pattern=spec.id_pattern, source_label=str(rel_path)
    )

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

    violations: list[str] = []
    for id_value, occurrences in seen.items():
        if len(occurrences) < 2:
            continue
        detail = "\n".join(f"    line {ln}: {snip}" for ln, snip in occurrences)
        violations.append(
            f"Duplicate {id_value} in {rel_path} ({len(occurrences)} rows):\n{detail}"
        )
    return checked, violations, parse_warnings


def main() -> int:
    total_checked = 0
    all_violations: list[str] = []
    all_warnings: list[str] = []

    for spec in NAMESPACES:
        checked, violations, parse_warnings = check_namespace(spec)
        total_checked += checked
        all_violations.extend(violations)
        all_warnings.extend(parse_warnings)

    if all_warnings:
        print(
            "Parser warning(s) -- recovered automatically, but please clean "
            "these up (each is a stray blank line inside a data table):"
        )
        for w in all_warnings:
            print(f"  - {w}")
        print()

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
