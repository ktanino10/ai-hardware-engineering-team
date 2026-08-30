# FMEA — Failure Mode and Effects Analysis

Systemic risk register — distinct from `validation/open-issues.md`. Where
`open-issues.md` tracks concrete defects found in a specific reviewed design
snapshot, this file anticipates failure modes **before** they're observed,
across the whole system. See `docs/architecture.md` §7.2–7.3 for why these
two are kept on separate scales instead of merged.

**Elevated importance for this project**: the roadmap targets a CubeSat-class
system (`docs/architecture.md` §11). Once hardware is in orbit it cannot be
repaired — failure modes must be anticipated in advance, not just found by
review after the fact. Treat FMEA rigor as increasing as the project
approaches actual flight hardware (this template is intentionally
lightweight for the MVP benchmark; expect more formal FMECA practice later).

## Scoring

RPN = Severity × Occurrence × Detection, each scored 1–10 (10 = worst/least
detectable). This is intentionally a different scale from the Hardware
Reviewer's CRITICAL/HIGH/MEDIUM/LOW (`docs/architecture.md` §7.1) — do not
conflate the two.

## Risk Register

| FMEA ID | Component/Function | Potential Failure Mode | Potential Effect (Local/System/Mission) | Severity (1-10) | Potential Cause | Current Controls | Occurrence (1-10) | Detection (1-10) | RPN | Recommended Action | Owner | Status | Related IDs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FMEA-001 | `<e.g. IMU power rail>` | `<e.g. brown-out during motor inrush>` | `<e.g. System: MCU resets, loses attitude estimate>` | | | | | | | | | Open | `<Evidence IDs / open-issues IDs / REQ IDs>` |

## Notes

- `Related IDs` cross-references `datasheets/evidence-log.md`,
  `validation/open-issues.md`, and `requirements/traceability-matrix.md` —
  an FMEA entry can be *driven by* a Reviewer finding, or can *drive* a new
  review focus; keep both directions linked instead of duplicating text.
- Review this register at least once per design revision before Design
  Complete (`docs/architecture.md` §8, condition 4).
- Track predictive validity in `docs/evaluation.md` ("FMEA Predictive
  Validity" metric): of the real-hardware issues eventually found, how many
  were already anticipated here?
