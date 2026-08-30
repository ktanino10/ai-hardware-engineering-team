# Open Issues — Living Finding Backlog

This is the single persistent backlog of Hardware Reviewer, Mechanical
Reviewer (Phase 1 — `docs/architecture-evolution.md` §31), and `rubber-duck`
findings across all review cycles — one shared backlog across disciplines,
not one per discipline. `validation/design-review.md` is the per-cycle
report; this file is what actually gates Design Complete
(`docs/architecture.md` §8) and what CI checks
(`.github/workflows/hardware-gate.yml` + `tools/check_open_issues.py`).

**Keep the table header and column order below exactly as-is** — the CI
gate script parses this file as a Markdown table.

## SLA Policy

*(Set by the human Chief Engineer per project — the framework does not
hard-code day counts.)*

| Severity | Target time to resolution |
|---|---|
| CRITICAL | SLA: [human sets] |
| HIGH | SLA: [human sets] |
| MEDIUM | SLA: [human sets] |
| LOW | SLA: [human sets] |

## Rules

- **CRITICAL** can only reach `RESOLVED` — never `ACCEPTED-RISK`
  (`docs/architecture.md` §8).
- **HIGH** may become `ACCEPTED-RISK` only with a named human Chief Engineer
  sign-off, written rationale, and date (recorded in the `Notes` column or
  cross-referenced to `validation/change-log.md`).
- **MEDIUM/LOW** don't block Design Complete but should still get a
  disposition (`RESOLVED` / `DEFERRED` / `ACCEPTED-RISK`) before archiving a
  revision.
- `Source` distinguishes which review lens found it: `hardware-reviewer`
  (Electronics checklist/failure-mode review), `mechanical-reviewer`
  (Mechanical checklist/failure-mode review, Phase 1 —
  `docs/architecture-evolution.md` §31), or `rubber-duck` (premise/
  assumption review) — see `docs/architecture.md` §5.1. Never merge/relabel
  one as another.

## Backlog

| ID | Severity | Status | Title | Component | Datasheet Source (Evidence ID) | Failure Mechanism | Recommended Fix | Source | SLA Target | Opened | Resolved | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

*(No open findings yet — this table intentionally has no data rows in the
template. Add one row per finding. Example row, for format reference only —
do not leave example rows in the live table:)*

```
| ISS-001 | CRITICAL | OPEN | VDD exceeds Absolute Max under cold-start inrush | U3 (IMU) | DS-IMU-007 | Cold-start inrush pushes VDD above Absolute Maximum Rating, risking latch-up | Add inrush-limiting resistor per datasheet Recommended Application Circuit | hardware-reviewer | SLA: [human sets] | 2026-01-01 | | |
```
