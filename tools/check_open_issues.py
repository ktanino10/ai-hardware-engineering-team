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

Diff-aware CRITICAL/HIGH exemption (added docs/architecture-evolution.md,
see the addendum introducing this): on a `pull_request` run, this script
additionally computes the PR's OWN changed-file set (via `git merge-base` +
`git diff` against PR_BASE_SHA/PR_HEAD_SHA -- see compute_pr_changed_files())
and, if that set touches none of hardware/**, bom/**, nor this gate's own
mechanism (this file / .github/workflows/hardware-gate.yml, guarded so a
change to the gate can never exempt itself -- see is_exempt_eligible()),
reports PASS regardless of pre-existing CRITICAL/HIGH findings elsewhere in
validation/open-issues.md. If the PR's own diff DOES touch
validation/open-issues.md, only the rows that diff itself added or changed
are evaluated (see compute_touched_new_lines()) -- so a PR that raises its
own brand-new unresolved CRITICAL/HIGH (the normal way a Reviewer finding
gets recorded here -- PR #38/MISS-034 touched only
validation/open-issues.md + design-review.md, zero hardware/bom) still
fails, exactly as today. Any failure to compute the diff (wrong event,
missing SHAs, a git error) fails SAFE to this script's original,
unconditional, whole-file behavior -- never a silent exemption. See
docs/architecture.md section 17.1 for the full rationale.

NOTE on `firmware/**` -- deliberately NOT one of the disqualifying prefixes,
despite section 17.1's own literal wording listing "hardware/**,
firmware/**, bom/**": `docs/workflow.md`'s Phase 8 exit criteria states
Firmware Bring-up "does *not* feed Phase 7's gate ... intentionally *not*
wired into the Design Complete Gate", and `docs/architecture.md` records
that Firmware Reviewer findings are deliberately kept in a firmware-scoped
file, not `validation/open-issues.md`, "so a firmware-only finding cannot
silently block the Design Complete Gate" (`docs/architecture-evolution.md`
section 32). This script only ever reads `validation/open-issues.md`, which
by that same design can structurally never contain a firmware finding --
disqualifying `firmware/**` here would buy no additional protection for
anything this script actually checks, while re-coupling firmware PRs to an
unrelated hardware gate that section 32 explicitly designed them out of.
Treated as a correction to section 17.1's own wording, not a silent
deviation -- see the architecture-evolution addendum for this change for
the full record.
"""
from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
OPEN_ISSUES_PATH = REPO_ROOT / "validation" / "open-issues.md"
OPEN_ISSUES_REL_PATH = "validation/open-issues.md"

EXPECTED_HEADER_PREFIX = ["ID", "Severity", "Status"]
# Used only as a plausibility check when deciding whether a row found just
# past a run of blank lines is really more of THIS table (as opposed to a
# genuinely different, unrelated table that coincidentally has the same
# column count) -- not used to filter which rows get severity/status
# checked below, which intentionally stays as loose as before.
ID_PATTERN = re.compile(r"^(ISS|MISS)-\d+$")
RESOLVED = "RESOLVED"
ACCEPTED_RISK = "ACCEPTED-RISK"

# Diff-aware exemption path sets. These two prefixes disqualify a PR from
# the exemption -- NOT validation/**, requirements/**, docs/**, firmware/**,
# etc. (see the module docstring's NOTE on firmware/** above for why that
# one is a deliberate correction to docs/architecture.md section 17.1's own
# literal wording, not an oversight). requirements/**/validation/** (other
# than open-issues.md, handled separately below) are excluded on purpose
# too: PR #39 (Requirements Engineering) touches requirements/** +
# validation/change-log.md and is one of the PRs this exemption exists to
# unblock -- disqualifying either prefix would leave it blocked, defeating
# the point.
DISQUALIFYING_PATH_PREFIXES = ("hardware/", "bom/")
# Self-referential guard, added beyond section 17.1's literal wording: a PR
# that edits the gate's OWN enforcement code touches neither hardware/ nor
# bom/, so without this it could exempt itself from scrutiny while changing
# what the gate does. These two files ARE the gate's actual runtime
# behavior (unlike, say, docs/architecture.md's *prose* description of it,
# which has no runtime effect and is not guarded this way).
GATE_MECHANISM_PATHS = frozenset(
    {
        "tools/check_open_issues.py",
        ".github/workflows/hardware-gate.yml",
    }
)


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


def parse_backlog_rows(
    text: str,
) -> tuple[list[tuple[int, list[str]]], list[str], int]:
    """Return (data rows of the Backlog table, parser warning messages,
    the table's expected column count).

    Each row is returned as `(line_no, cells)`, where `line_no` is the
    row's own 1-indexed line number in `text`. This is additive -- it does
    not change any of the scanning/gap-recovery logic below -- and exists
    so callers can restrict evaluation to only the rows a PR's own diff
    touched (the diff-aware exemption's line-scoped check; see `main()`
    and `compute_touched_new_lines()`), instead of every row in the file.

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


def evaluate_rows(
    rows: list[tuple[int, list[str]]],
    expected_ncols: int,
    only_lines: set[int] | None,
) -> tuple[list[str], list[str], int]:
    """Evaluate CRITICAL/HIGH violations among Backlog `rows`.

    When `only_lines` is None, every row is evaluated -- this is today's
    original, unconditional whole-file behavior, used whenever this PR
    isn't exemption-eligible (or isn't running against a `pull_request` at
    all). When `only_lines` is a set of line numbers, a row is evaluated
    only if its own line number is in that set; every other row is
    skipped entirely (neither a violation nor a length issue can be
    reported for it) -- this is the diff-aware exemption's line-scoped
    check, used only when this PR's own diff touches
    validation/open-issues.md but touches none of hardware/**, bom/**, nor
    this gate's own mechanism.

    Returns (violations, length_issues, rows_checked_count). The
    per-row logic itself is unchanged from before this function was
    extracted out of `main()`.
    """
    violations: list[str] = []
    length_issues: list[str] = []
    checked = 0
    for line_no, row in rows:
        if only_lines is not None and line_no not in only_lines:
            continue
        checked += 1

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

    return violations, length_issues, checked


def _run_git(args: list[str]) -> str | None:
    """Run `git <args>` from REPO_ROOT; return stripped stdout, or None on
    ANY failure (git missing, command error, commit not present locally,
    timeout, ...). Callers must treat None as "cannot determine" and fail
    SAFE -- fall back to the full whole-file check -- never as "touches
    nothing"/"exempt". Prints a warning on failure so a CI log always
    shows why the fallback happened, rather than silently doing it.
    """
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"WARNING: 'git {' '.join(args)}' could not be run: {exc}")
        return None
    if result.returncode != 0:
        print(
            f"WARNING: 'git {' '.join(args)}' failed (exit "
            f"{result.returncode}): {result.stderr.strip()}"
        )
        return None
    return result.stdout.strip()


def compute_pr_changed_files() -> tuple[str, str, list[str]] | None:
    """Return `(merge_base, head_sha, changed_files)` for this PR, or None
    if this isn't a usable `pull_request` context (wrong event, missing
    SHAs, or the diff can't be computed for any reason) -- callers must
    treat None as "run the full check", never as "touches nothing".
    `merge_base`/`head_sha` are returned alongside `changed_files` so a
    caller that also needs the line-scoped check
    (`compute_touched_new_lines()`) doesn't have to re-derive the same
    merge-base a second time.

    The diff basis is `merge-base(base_sha, head_sha)` vs. `head_sha` --
    i.e. this PR's own commits relative to where it forked from its
    target branch, matching exactly what GitHub's own PR "Files changed"
    view shows. This deliberately is NOT a plain two-dot
    `base_sha..head_sha` diff: if the target branch has advanced since
    the PR forked (routine on a shared `main`), a two-dot diff would also
    include those unrelated upstream changes as if they were part of
    this PR's own diff.

    Requires the local git history to actually contain both `base_sha`
    and `head_sha` and a computable merge-base between them -- the
    workflow's checkout step uses `fetch-depth: 0` for exactly this
    reason. Rather than silently trust that YAML stays correct, this
    function checks `git rev-parse --is-shallow-repository` up front so
    a shallow checkout fails with a clearly-named reason instead of an
    opaque `git merge-base` error.
    """
    if os.environ.get("GITHUB_EVENT_NAME") != "pull_request":
        return None

    base_sha = os.environ.get("PR_BASE_SHA", "").strip()
    head_sha = os.environ.get("PR_HEAD_SHA", "").strip()
    if not base_sha or not head_sha:
        print(
            "WARNING: GITHUB_EVENT_NAME=pull_request but PR_BASE_SHA/"
            "PR_HEAD_SHA are not both set; falling back to the full check."
        )
        return None

    is_shallow = _run_git(["rev-parse", "--is-shallow-repository"])
    if is_shallow is None:
        return None
    if is_shallow == "true":
        print(
            "WARNING: this checkout is shallow (the workflow's checkout "
            "step did not fetch full history -- expected `fetch-depth: 0`) "
            "-- cannot reliably compute a merge-base; falling back to the "
            "full check."
        )
        return None

    merge_base = _run_git(["merge-base", base_sha, head_sha])
    if merge_base is None:
        return None

    diff_output = _run_git(["diff", "--name-only", merge_base, head_sha])
    if diff_output is None:
        return None

    changed_files = [line for line in diff_output.splitlines() if line.strip()]
    return merge_base, head_sha, changed_files


def is_exempt_eligible(changed_files: list[str]) -> bool:
    """True if `changed_files` touches none of hardware/**, bom/**, nor
    this gate's own enforcement mechanism. (`firmware/**` is deliberately
    NOT included -- see the module docstring's NOTE on it.)

    The mechanism-path guard is deliberate and goes beyond
    docs/architecture.md section 17.1's literal text: without it, a PR
    that edits the gate's own code touches neither hardware/ nor bom/, so
    it could exempt ITSELF from scrutiny while changing what the gate
    does. docs/architecture.md's own *prose* description of the gate is
    not guarded the same way -- it has no runtime effect; these two files
    are the gate's actual behavior.
    """
    for f in changed_files:
        if f in GATE_MECHANISM_PATHS:
            return False
        if any(f.startswith(prefix) for prefix in DISQUALIFYING_PATH_PREFIXES):
            return False
    return True


_HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def compute_touched_new_lines(
    merge_base: str, head_sha: str, rel_path: str
) -> set[int] | None:
    """Return the set of 1-indexed line numbers, in `rel_path`'s content
    AT `head_sha`, that this PR's own diff added or changed -- derived
    from `git diff --unified=0`'s hunk headers (`@@ -a,b +c,d @@`; the new
    file's touched range is `[c, c+d-1]`, using an implicit `d=1` when
    omitted per unified-diff convention). `--unified=0` (no context lines)
    is essential: with default context, unrelated unchanged neighboring
    rows would also appear inside a hunk and be wrongly counted as
    "touched by this PR".

    A MODIFIED row (e.g. an existing HIGH's Status flipped back from
    RESOLVED/ACCEPTED-RISK to OPEN) is deliberately treated the same as a
    newly-added one here: git represents a same-position content change as
    the old line removed and the new line added, and the new line's
    position is exactly what this function reports -- there is no
    separate "added vs. modified" case to handle.

    Returns None (never an empty-but-valid set standing in for "nothing
    to worry about") if the diff can't be computed or a hunk header can't
    be parsed -- callers must fail SAFE to the full check.
    """
    diff_output = _run_git(
        ["diff", "--unified=0", merge_base, head_sha, "--", rel_path]
    )
    if diff_output is None:
        return None

    touched: set[int] = set()
    for line in diff_output.splitlines():
        if not line.startswith("@@"):
            continue
        match = _HUNK_HEADER.match(line)
        if not match:
            print(f"WARNING: could not parse diff hunk header: {line!r}")
            return None
        new_start = int(match.group(1))
        new_count = int(match.group(2)) if match.group(2) is not None else 1
        touched.update(range(new_start, new_start + new_count))
    return touched


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

    # --- Diff-aware exemption (docs/architecture.md section 17.1) ------
    # `only_lines` stays None (== "evaluate every row", today's original
    # behavior) unless we positively establish this PR is exemption-
    # eligible AND its own diff touches validation/open-issues.md, in
    # which case it becomes the set of lines THIS PR's diff touched. Any
    # inability to establish eligibility/diff falls back to None (the
    # full check) -- see compute_pr_changed_files()/
    # compute_touched_new_lines() docstrings for why that's the safe
    # default, not the exempting one.
    only_lines: set[int] | None = None

    pr_diff = compute_pr_changed_files()
    if pr_diff is None:
        pass  # not a usable pull_request context -- full check, as today
    else:
        merge_base, head_sha, changed_files = pr_diff
        if not is_exempt_eligible(changed_files):
            pass  # touches hardware/bom or the gate's own files
        elif OPEN_ISSUES_REL_PATH not in changed_files:
            print(
                "OK: this PR's changed-file set touches none of "
                "hardware/**, bom/** (firmware/** is deliberately not "
                "gated here -- docs/architecture.md section 17.1's own "
                "corrected wording), and does not modify "
                f"{OPEN_ISSUES_REL_PATH} -- exempt from the whole-file "
                "Design Complete Gate check per docs/architecture.md "
                f"section 17.1 ({len(rows)} pre-existing finding(s) in "
                "the file were not evaluated)."
            )
            return 0
        else:
            touched = compute_touched_new_lines(
                merge_base, head_sha, OPEN_ISSUES_REL_PATH
            )
            if touched is None:
                print(
                    "WARNING: could not determine which lines of "
                    f"{OPEN_ISSUES_REL_PATH} this PR's own diff touched; "
                    "falling back to the full whole-file check."
                )
            else:
                only_lines = touched
                print(
                    f"This PR modifies {OPEN_ISSUES_REL_PATH} but touches "
                    "none of hardware/**, bom/**: only the "
                    f"row(s) this PR's own diff added or changed (line(s) "
                    f"{sorted(touched) or '(none)'}) are evaluated below; "
                    "pre-existing, untouched finding(s) elsewhere in the "
                    "file are exempt per docs/architecture.md section "
                    "17.1."
                )
                print()

    violations, length_issues, checked = evaluate_rows(rows, expected_ncols, only_lines)

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

    if only_lines is not None:
        print(
            "OK: no unresolved CRITICAL / unsigned-off HIGH findings among "
            f"the {checked} row(s) this PR's own diff touched in "
            f"{OPEN_ISSUES_REL_PATH} ({len(rows) - checked} pre-existing, "
            "untouched finding(s) elsewhere in the file were not "
            "evaluated -- exempt per docs/architecture.md section 17.1)."
        )
    else:
        print(
            "OK: no unresolved CRITICAL / unsigned-off HIGH findings "
            f"({len(rows)} finding(s) checked)."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
