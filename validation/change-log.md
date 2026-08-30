# Change Log — Engineering Change Orders (ECO)

Tracks what changed, why, and under whose approval, every time the design
is revised. This is what makes hardware revisions auditable after the fact —
"just editing" a schematic/PCB/BOM post-fabrication without a recorded ECO
is not acceptable practice here.

One entry per change. Design Complete requires an ECO entry for the current
revision (`docs/architecture.md` §8, condition 5).

## ECO Template

### `<ECO-XXX>` — `<short title>`

- **Date**:
- **Revision**: from `<rev>` to `<rev>`
- **Changed**: `<component / schematic / PCB / BOM — be specific>`
- **Why**: `<driving Finding ID(s) from open-issues.md, FMEA ID(s), or requirement change>`
- **Impact analysis**: `<affected subsystems; re-test needed? re-review needed?>`
- **Approved by**: `<human Chief Engineer name>` — `<date>`
- **Related IDs**: `<open-issues / FMEA / requirement / Evidence IDs>`

## Log

| ECO ID | Date | Revision (from -> to) | Changed | Why | Approved by | Related IDs |
|---|---|---|---|---|---|---|
| ECO-001 | | | | | | |

## Notes

- Also use this log to record the outcome of a Conflict Resolution /
  Deadlock Escalation (`docs/workflow.md` §3) whenever it changes something
  already designed.
- `docs/evaluation.md` uses ECO count per revision cycle as a "Change
  Churn" proxy for design stability/rework — keep entries granular enough
  for that to be meaningful (don't bundle unrelated changes into one ECO).
