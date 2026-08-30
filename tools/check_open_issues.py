#!/usr/bin/env python3
"""CI gate for validation/open-issues.md.

Enforces the Design Complete rule from docs/architecture.md section 8:
  - A CRITICAL finding may only be Status=RESOLVED.
  - A HIGH finding must be Status=RESOLVED or Status=ACCEPTED-RISK.
Any other combination fails the check.

This intentionally parses only the "Backlog" table (the one whose header
starts with "ID | Severity | Status"), stopping at the first blank line
after the separator row -- so the illustrative example row inside the
fenced code block later in the template is never parsed as real data.

Keep this in sync with the table header documented in
validation/open-issues.md and .github/instructions/validation.instructions.md.
If that header/column order changes, update EXPECTED_HEADER_PREFIX below.
"""
from __future__ import annotations

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
OPEN_ISSUES_PATH = REPO_ROOT / "validation" / "open-issues.md"

EXPECTED_HEADER_PREFIX = ["ID", "Severity", "Status"]
RESOLVED = "RESOLVED"
ACCEPTED_RISK = "ACCEPTED-RISK"


def _split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_separator_row(cells: list[str]) -> bool:
    return all(set(cell) <= {"-", " ", ":"} and cell != "" for cell in cells)


def parse_backlog_rows(text: str) -> list[list[str]]:
    """Return each data row of the Backlog table as a list of cell strings."""
    lines = text.splitlines()

    header_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = _split_row(stripped)
        if cells[: len(EXPECTED_HEADER_PREFIX)] == EXPECTED_HEADER_PREFIX:
            header_idx = i
            break

    if header_idx is None:
        return []

    j = header_idx + 1
    if j < len(lines) and lines[j].strip().startswith("|"):
        if _is_separator_row(_split_row(lines[j])):
            j += 1

    rows: list[list[str]] = []
    while j < len(lines):
        line = lines[j].strip()
        if not line.startswith("|"):
            break  # first blank/non-table line ends the Backlog table
        cells = _split_row(line)
        if any(cell != "" for cell in cells):
            rows.append(cells)
        j += 1
    return rows


def main() -> int:
    if not OPEN_ISSUES_PATH.exists():
        print(f"OK: {OPEN_ISSUES_PATH} not found, nothing to check.")
        return 0

    text = OPEN_ISSUES_PATH.read_text(encoding="utf-8")
    rows = parse_backlog_rows(text)

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
