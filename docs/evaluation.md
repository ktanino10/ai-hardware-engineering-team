# Evaluation: Does This Framework Actually Improve Design Quality?

The point of separating agents is worthless if it cannot be shown to reduce
design mistakes and increase traceability compared to a single AI agent doing
the same task. This document defines how to measure that, once there is more
than one design cycle to compare.

## 1. Experiment Design

Run the **same** `requirements/requirements.md` through two conditions on
comparable hardware (start with the MCU + IMU + Power Supply benchmark,
architecture.md §11):

- **Condition A — Single Agent**: one AI agent, no role separation, no
  independent review, does requirements→component→circuit design directly.
- **Condition B — Multi-Agent**: this framework (Requirements Engineering →
  Component Selection → Datasheet Verification → Circuit Design →
  Independent Review → Validation, with loop-back).

Keep the requirements, target parts pool, and available datasheets identical
between conditions so the only variable is the process.

## 2. Metrics

| Metric | Definition | Data source |
|---|---|---|
| Datasheet violations | # of design decisions that contradict a datasheet's Absolute Maximum Rating or Recommended Operating Condition, found at any point (self-review, independent review, or later) | `validation/open-issues.md`, `validation/design-review.md` |
| ERC error count | # of schematic-level electrical rule check errors (once an ERC tool is integrated — currently Future Integration, architecture.md §13) | future ERC tool output |
| DRC error count | # of PCB design-rule-check errors | `kicad-run_drc_check` / `kicad-get_drc_history_tool` |
| Reviewer finding count | Total independent-review findings, all severities | `validation/open-issues.md` |
| CRITICAL finding count | Findings classified CRITICAL | `validation/open-issues.md` |
| Human-found design mistakes | Issues a human catches that no agent flagged first | `validation/open-issues.md` (tag `found-by: human`) |
| Revision count | # of ECO entries for the design | `validation/change-log.md` |
| Simulation failure count | Once SPICE is integrated (Future Integration) | future SPICE tool output |
| Real-hardware issue count | Issues found during/after `validation/bring-up-procedure.md` | `validation/open-issues.md` (tag `phase: bring-up`) |
| Time to Design Complete | Wall-clock time from Requirements sign-off to the Design Complete Gate passing | `validation/change-log.md` timestamps |

### 2.1 Additional metrics proposed for this framework specifically

| Metric | Definition | Why it matters here |
|---|---|---|
| Evidence Coverage Rate | % of design decisions/findings that cite a valid Evidence ID (vs. unsupported claims) | Directly measures whether the Source-of-Truth principle (architecture.md §6) is actually being followed, not just stated |
| Unknown Resolution Rate | % of parameters initially marked `UNKNOWN` that are later resolved with a real citation before Design Complete | Measures whether "don't guess" is holding up under schedule pressure, or whether UNKNOWNs are quietly ignored |
| Reopen Rate | % of findings marked `RESOLVED` that are later reopened | Proxy for whether fixes were genuine or superficial |
| FMEA Predictive Validity | Of the real-hardware issues found (row above), what fraction were already anticipated in `validation/fmea.md` before bring-up? | Measures whether the systemic risk process actually predicts real failures, vs. FMEA being paperwork |
| Requirement Coverage Rate | % of `requirements/traceability-matrix.md` rows at `Verified` (not `Waived`) at Design Complete | Measures real closure vs. hand-waved closure |
| Change Churn | ECO count per design revision cycle | Proxy for design stability / how much rework the process causes or prevents |

## 3. How to Log Data Without Extra Overhead

All of the above are already fields in artifacts this framework produces
(`validation/open-issues.md`, `validation/fmea.md`, `validation/change-log.md`,
`requirements/traceability-matrix.md`). Evaluation is a matter of querying
those files/tables after a design cycle, not a separate parallel logging
system. When these are eventually machine-readable (e.g. exported to the
session SQL database or CSV), computing the table above becomes a script;
until then, compute it by hand per design cycle.

## 4. Reporting

After each design cycle (single-agent or multi-agent), fill in the metrics
table above and attach it to that cycle's closing entry in
`validation/change-log.md`, so comparisons across cycles/conditions stay in
one auditable place.
