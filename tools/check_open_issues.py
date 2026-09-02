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
    """Split a Markdown table row into cells, respecting GFM's own escape
    convention for a literal pipe inside a cell (``\\|``) -- an escaped
    pipe does NOT separate cells, unlike a bare one. A naive
    ``.split("|")`` (the previous implementation) wrongly inflates the
    apparent column count of a row containing legitimately-escaped prose.
    The escape-aware scan runs over the WHOLE line, including its
    boundary delimiters, rather than pre-stripping them with a naive
    ``.strip("|")`` first -- that would remove ANY ``|`` characters from
    the string's edges with no escape-awareness, corrupting a cell whose
    content legitimately ends in an escaped pipe with nothing between it
    and the row's real closing delimiter. Splitting first and then
    dropping exactly the one leading and one trailing EMPTY artifact cell
    the boundary delimiters produce (by position) avoids this. Kept in
    sync with the identical fix in `tools/check_id_uniqueness.py`'s own
    `_split_row` -- see that one's docstring for the real, concrete
    example this fixes.
    """
    stripped = line.strip()
    cells: list[str] = []
    current: list[str] = []
    i = 0
    while i < len(stripped):
        ch = stripped[i]
        if ch == "\\" and i + 1 < len(stripped) and stripped[i + 1] == "|":
            current.append("|")  # literal pipe, not a cell separator
            i += 2
            continue
        if ch == "|":
            cells.append("".join(current).strip())
            current = []
            i += 1
            continue
        current.append(ch)
        i += 1
    cells.append("".join(current).strip())
    if cells and cells[0] == "":
        cells = cells[1:]
    if cells and cells[-1] == "":
        cells = cells[:-1]
    return cells


def _is_separator_row(cells: list[str]) -> bool:
    return all(set(cell) <= {"-", " ", ":"} and cell != "" for cell in cells)


def _is_placeholder(id_cell: str) -> bool:
    return not id_cell or id_cell.startswith("<") or id_cell.startswith("ISS-XXX")


def parse_backlog_rows(text: str) -> tuple[list[list[str]], list[str], int]:
    """Return (data rows of the Backlog table, parser warning messages,
    the table's expected column count).

    The expected column count is returned so callers (see `main()`) can
    validate a row's actual length before trusting fixed-position
    indexing into it (`row[1]` for Severity, `row[2]` for Status) --
    found necessary by independent code review: a row whose own internal
    pipe-boundary shifts for any reason (e.g. a human accidentally
    deletes one `|` while hand-editing -- the exact class of manual-
    editing mistake this whole hardening effort exists to catch) can
    silently merge Severity and Status into one cell. Since neither
    "CRITICAL"/"HIGH" would then exactly match that merged string,
    `main()`'s severity checks would silently fall through to nothing --
    a live, concretely-demonstrated false PASS of this exact gate, one
    function downstream of the parser's own hardening.

    The ONLY thing treated as a genuine, unconditional end-of-table
    boundary is a real section break: a Markdown heading line (starts with
    "#") or EOF. Anything else that isn't itself a well-formed data row of
    this exact table -- a blank line, a run of several, a malformed row,
    stray prose, or any mix -- is NOT by itself treated as ending the
    table: scanning skips forward over the whole contiguous run of such
    lines and keeps looking, all the way up to the next real heading or
    EOF, for a row that IS a well-formed continuation (same column count
    as the header, not a separator row, and an ID cell matching
    ISS-/MISS- or a recognized placeholder). If one is found, the skipped
    span is treated as an accidental gap: it's skipped, a warning is
    recorded (never silently), and scanning resumes. If a heading or EOF
    is reached first, that's the genuine end -- scanning stops, but a
    warning is still recorded if the span leading up to it contained
    anything non-blank.

    The previous version of this function stopped scanning, unconditionally
    and silently, at the first line that didn't start with "|" after the
    header -- whether that was a real section boundary or just a stray
    blank line accidentally inserted between two data rows. See this
    file's module docstring for the real incident (in the near-identical
    tools/check_id_uniqueness.py parser) that motivated hardening this
    mirrored parser the same way before it could bite here too. A first
    hardening pass fixed that exact shape but an independent code review
    found it still silently truncated scanning -- with zero warning -- if
    a single MALFORMED (not blank) row sat between the gap and the next
    real row: concretely demonstrated, against this exact file/function,
    to make `main()` print a clean `OK` and exit 0 while hiding a real,
    unresolved HIGH finding. This version closes that gap by continuing to
    look past ANY non-qualifying, non-heading content -- not just blank
    lines, and not just one line's worth of it -- before concluding the
    table has genuinely ended.
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
        return [], [], 0

    expected_ncols = len(header_cells)

    j = header_idx + 1
    if j < len(lines) and lines[j].strip().startswith("|"):
        if _is_separator_row(_split_row(lines[j])):
            j += 1

    def is_real_row(line_stripped: str) -> bool:
        if not line_stripped.startswith("|"):
            return False
        cells = _split_row(line_stripped)
        if len(cells) != expected_ncols or _is_separator_row(cells):
            return False
        id_cell = cells[0] if cells else ""
        return _is_placeholder(id_cell) or bool(ID_PATTERN.match(id_cell))

    def id_plausible_row(line_stripped: str) -> bool:
        """Weaker than is_real_row: doesn't require the right column
        count, only that the line's own first cell (unaffected by a
        formatting defect elsewhere in the row, e.g. a stray unescaped
        '|' in a later free-text cell) matches ISS-/MISS- or is a
        recognized placeholder. Prevents a row that IS genuinely meant as
        real data, but fails the strict check for some other reason, from
        being silently swallowed as anonymous gap filler.
        """
        if not line_stripped.startswith("|"):
            return False
        cells = _split_row(line_stripped)
        if not cells or _is_separator_row(cells):
            return False
        id_cell = cells[0]
        return _is_placeholder(id_cell) or bool(ID_PATTERN.match(id_cell))

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

        if stripped.startswith("#"):
            break  # an actual Markdown heading is an unambiguous section end

        # A blank line OR some other non-table content (a malformed row,
        # stray prose, etc.) that is NOT a heading. Skip forward over a
        # whole contiguous run of such lines and see whether a real row
        # reappears on the other side, up to the next genuine heading or
        # EOF.
        gap_start = j
        k = j
        saw_nonblank = False
        while k < len(lines):
            k_stripped = lines[k].strip()
            if k_stripped.startswith("|") and (
                is_real_row(k_stripped) or id_plausible_row(k_stripped)
            ):
                break
            if k_stripped.startswith("#"):
                break
            if k_stripped != "":
                saw_nonblank = True
            k += 1

        resumed = lines[k].strip() if k < len(lines) else ""
        if resumed.startswith("|") and (is_real_row(resumed) or id_plausible_row(resumed)):
            n_skipped = k - gap_start
            kind = "non-blank/malformed" if saw_nonblank else "blank"
            if is_real_row(resumed):
                warnings.append(
                    f"line {gap_start + 1}: skipped {n_skipped} {kind} line(s) "
                    f"between Backlog table rows (table resumes at line "
                    f"{k + 1}) -- clean this up; a gap like this here "
                    "previously could silently truncate scanning."
                )
            else:
                # id_plausible_row but NOT is_real_row: the resumed row
                # itself is malformed (e.g. wrong column count). It WILL
                # still be added as a normal row by the main loop next
                # iteration (any "|"-prefixed line is, unconditionally) --
                # but name the malformation explicitly so it's never
                # missed.
                resumed_cells = _split_row(resumed)
                warnings.append(
                    f"line {gap_start + 1}: skipped {n_skipped} {kind} "
                    f"line(s), then found a row with ID '{resumed_cells[0]}' "
                    f"at line {k + 1} that has {len(resumed_cells)} cell(s) "
                    f"(expected {expected_ncols}) -- possible internal "
                    "formatting corruption (e.g. an unescaped '|' in a "
                    "free-text cell); counted anyway since its ID looks "
                    "genuine, but PLEASE FIX this row's own formatting."
                )
            j = k
            continue

        # Genuine end (heading or EOF), no real continuation found. Warn
        # anyway if anything non-blank was skipped to reach it.
        if saw_nonblank:
            warnings.append(
                f"line {gap_start + 1}: found non-blank content that isn't "
                "a valid Backlog row, right before what looks like the "
                "table's real end (a heading or end of file) -- if this "
                "was meant to be a data row, it's malformed and was NOT "
                "counted; please check nothing real was missed here."
            )
        break

    return rows, warnings, expected_ncols


def main() -> int:
    if not OPEN_ISSUES_PATH.exists():
        print(f"OK: {OPEN_ISSUES_PATH} not found, nothing to check.")
        return 0

    text = OPEN_ISSUES_PATH.read_text(encoding="utf-8")
    rows, parse_warnings, expected_ncols = parse_backlog_rows(text)

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
    length_issues: list[str] = []
    for row in rows:
        issue_id = row[0] if row else ""
        if not issue_id or issue_id.startswith("<") or issue_id.startswith("ISS-XXX"):
            continue  # placeholder row, not a real finding

        if len(row) != expected_ncols:
            # Do NOT trust fixed-position indexing (row[1]=Severity,
            # row[2]=Status) into a row whose own column count doesn't
            # match the table's header -- found by independent code
            # review: an accidentally-deleted "|" merging Severity and
            # Status into one cell would otherwise silently defeat BOTH
            # severity checks below (neither "CRITICAL" nor "HIGH" would
            # exactly match the merged string, so neither branch fires),
            # a live, concretely-demonstrated false PASS of this exact
            # gate. Fail loudly and specifically instead of guessing.
            length_issues.append(
                f"{issue_id}: row has {len(row)} cell(s), expected "
                f"{expected_ncols} -- cannot reliably determine this "
                "finding's Severity/Status; fix the row's own "
                "formatting (likely a missing or extra '|')"
            )
            continue

        severity, status = row[1].upper(), row[2].upper()
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

    if length_issues:
        print(
            "Hardware gate FAILED - cannot verify these Backlog row(s) "
            "(malformed, wrong column count):"
        )
        for li in length_issues:
            print(f"  - {li}")
        print()

    if violations:
        print("Hardware gate FAILED - Design Complete cannot proceed:")
        for v in violations:
            print(f"  - {v}")
        print(
            "\nSee docs/architecture.md section 8 (Design Complete Gate) and "
            "validation/open-issues.md for the resolution rules."
        )
        return 1

    if length_issues:
        return 1

    print(
        "OK: no unresolved CRITICAL / unsigned-off HIGH findings "
        f"({len(rows)} finding(s) checked)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
