# Change Impact Matrix

For a given change (component swap, schematic change, etc.), makes the
cross-domain ripple effects explicit **before** the change is made, instead
of discovering them after the fact. Cross-reference by ID with
`validation/change-log.md` (ECO).

## Template

### For `<ECO-XXX>` — `<change short title>`

| Impact Domain | Impact Level (None/Low/Medium/High) | Cross-check Required? | Verification Result |
|---|---|---|---|
| Power (rail loading, `hardware/power-budget.md`) | | `<Y/N>` | |
| Thermal | | `<Y/N>` | |
| EMI/EMC | | `<Y/N>` | |
| Timing (interface/bus timing) | | `<Y/N>` | |
| Mechanical (fit, connectors, mounting; vibration if a rotating body is present — `docs/architecture.md` §12) | | `<Y/N>` | |
| Grounding | | `<Y/N>` | |
| BOM / lifecycle (does this affect other line items, e.g. shared connector) | | `<Y/N>` | |
| Requirements coverage (`requirements/traceability-matrix.md`) | | `<Y/N>` | |

## Rules

- Fill this in **before** approving an ECO that isn't purely cosmetic — this
  is what "impact analysis" in the ECO template (`validation/change-log.md`)
  actually refers to when the change is non-trivial.
- Any domain marked `Medium` or `High` impact needs its `Cross-check
  Required?` set to `Y` and an actual `Verification Result` before the
  associated ECO is approved by the human Chief Engineer.
- Link back to the ECO ID so `change-log.md` and this file stay in sync
  instead of drifting apart.
