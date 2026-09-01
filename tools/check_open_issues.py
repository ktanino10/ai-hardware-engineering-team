#!/usr/bin/env python3
"""CI gate for validation/open-issues.md.

Enforces the Design Complete rule from docs/architecture.md section 8:
  - A CRITICAL finding may only be Status=RESOLVED.
  - A HIGH finding must be Status=RESOLVED or Status=ACCEPTED-RISK.
Any other combination fails the check.

This intentionally parses only the "Backlog" table (the one whose header
starts with "ID | Severity | Status") -- so the illustrative example row
inside the fenced code block later in the template is never parsed as
real data. Unlike a naive "stop at the first blank line after the header"
rule, a lone stray blank line accidentally inserted between two data rows
does not by itself end the table here: see parse_backlog_rows()'s
docstring. This mirrors a real, previously-latent bug found and fixed in
tools/check_id_uniqueness.py (2026-09, bench-imu-01-rev3 branch): that
script's near-identical parser silently truncated `validation/change-log.md`
ECO scanning to 12 of 26 real rows for an entire session because of 7
stray blank lines -- this script parses the very same file
(`validation/open-issues.md`) for the actual Design Complete gate, so it
carried the identical latent risk (never triggered here only because this
file's Backlog table happened to have no stray blank line in it at the
time) and is hardened the same way as a direct consequence, not a
coincidence.

Keep this in sync with the table header documented in
validation/open-issues.md and .github/instructions/validation.instructions.md.
If that header/column order changes, update EXPECTED_HEADER_PREFIX below.
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
OPEN_ISSUES_PATH = REPO_ROOT / "validation" / "open-issues.md"

EXPECTED_HEADER_PREFIX = ["ID", "Severity", "Status"]
# Used only as a plausibility check when deciding whether a row found just
# past a run of blank lines is really more of THIS table (as opposed to a
# genuinely different, unrelated table that coincidentally has the same
# column count) -- not used to filter which rows get severity/status
# checked below, which intentionally stays as loose as before.
ID_PATTERN = re.compile(r"^(ISS|MISS)-\d+$")
RESOLVED = "RESOLVED"
ACCEPTED_RISK = "ACCEPTED-RISK"


def _split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_separator_row(cells: list[str]) -> bool:
    return all(set(cell) <= {"-", " ", ":"} and cell != "" for cell in cells)


def _is_placeholder(id_cell: str) -> bool:
    return not id_cell or id_cell.startswith("<") or id_cell.startswith("ISS-XXX")


def parse_backlog_rows(text: str) -> tuple[list[list[str]], list[str]]:
    """Return (data rows of the Backlog table, parser warning messages).

    A genuine end-of-table boundary is a real section break: a non-blank
    line that is not itself a table row (typically a Markdown heading), or
    EOF. A lone blank line between two otherwise-adjacent data rows is NOT,
    by itself, treated as a boundary: scanning looks past the whole run of
    blank lines, and if a well-formed row follows -- same column count as
    the header, AND an ID cell that looks like a real ISS-/MISS- ID or a
    recognized placeholder -- the gap is treated as a stray/accidental
    blank line: it is skipped (with a warning recorded, never silently)
    and scanning continues past it.

    The previous version of this function stopped scanning, unconditionally
    and silently, at the first line that didn't start with "|" after the
    header -- whether that was a real section boundary or just a stray
    blank line accidentally inserted between two data rows. See this
    file's module docstring for the real incident (in the near-identical
    tools/check_id_uniqueness.py parser) that motivated hardening this
    mirrored parser the same way before it could bite here too.
    """
    lines = text.splitlines()

    header_idx = None
    header_cells: list[str] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = _split_row(stripped)
        if cells[: len(EXPECTED_HEADER_PREFIX)] == EXPECTED_HEADER_PREFIX:
            header_idx = i
            header_cells = cells
            break

    if header_idx is None:
        return [], []

    expected_ncols = len(header_cells)

    j = header_idx + 1
    if j < len(lines) and lines[j].strip().startswith("|"):
        if _is_separator_row(_split_row(lines[j])):
            j += 1

    rows: list[list[str]] = []
    warnings: list[str] = []
    while j < len(lines):
        stripped = lines[j].strip()

        if stripped.startswith("|"):
            cells = _split_row(stripped)
            if any(cell != "" for cell in cells):
                rows.append(cells)
            j += 1
            continue

        if stripped == "":
            # Could be a legitimate end-of-table blank line (e.g. right
            # before a heading or EOF) or a stray gap accidentally
            # inserted between two data rows. Look past the *whole* run
            # of blank lines to see which.
            gap_start = j
            k = j
            while k < len(lines) and lines[k].strip() == "":
                k += 1
            if k < len(lines):
                next_stripped = lines[k].strip()
                if next_stripped.startswith("|"):
                    next_cells = _split_row(next_stripped)
                    id_cell = next_cells[0] if next_cells else ""
                    id_plausible = _is_placeholder(id_cell) or bool(
                        ID_PATTERN.match(id_cell)
                    )
                    if (
                        len(next_cells) == expected_ncols
                        and not _is_separator_row(next_cells)
                        and id_plausible
                    ):
                        n_blank = k - gap_start
                        warnings.append(
                            f"line {gap_start + 1}: skipped {n_blank} "
                            "stray blank line(s) between Backlog table "
                            f"rows (table resumes at line {k + 1}) -- "
                            "remove the blank line(s); a stray blank "
                            "line here previously truncated scanning "
                            "silently in a near-identical parser."
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


def main() -> int:
    if not OPEN_ISSUES_PATH.exists():
        print(f"OK: {OPEN_ISSUES_PATH} not found, nothing to check.")
        return 0

    text = OPEN_ISSUES_PATH.read_text(encoding="utf-8")
    rows, parse_warnings = parse_backlog_rows(text)

    if parse_warnings:
        print(
            "Parser warning(s) -- recovered automatically, but please "
            "clean these up (each is a stray blank line inside the "
            "Backlog table):"
        )
        for w in parse_warnings:
            print(f"  - {w}")
        print()

    violations: list[str] = []
    for row in rows:
        if len(row) < 3:
            continue
        issue_id, severity, status = row[0], row[1].upper(), row[2].upper()
        if not issue_id or issue_id.startswith("<") or issue_id.startswith("ISS-XXX"):
            continue  # placeholder row, not a real finding

        if severity == "CRITICAL" and status != RESOLVED:
            violations.append(
                f"{issue_id}: CRITICAL finding is not RESOLVED "
                f"(status={status or 'EMPTY'})"
            )
        elif severity == "HIGH" and status not in (RESOLVED, ACCEPTED_RISK):
            violations.append(
                f"{issue_id}: HIGH finding is neither RESOLVED nor "
                f"ACCEPTED-RISK (status={status or 'EMPTY'})"
            )

    if violations:
        print("Hardware gate FAILED - Design Complete cannot proceed:")
        for v in violations:
            print(f"  - {v}")
        print(
            "\nSee docs/architecture.md section 8 (Design Complete Gate) and "
            "validation/open-issues.md for the resolution rules."
        )
        return 1

    print(
        "OK: no unresolved CRITICAL / unsigned-off HIGH findings "
        f"({len(rows)} finding(s) checked)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
