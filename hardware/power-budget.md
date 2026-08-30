# System Power Budget

Aggregates every subsystem's current/power draw against the supply's
capability, per rail, with margin. Maintained by the Circuit Engineer as
part of `skills/schematic-design/SKILL.md` (MVP); a future **Power Engineer**
role formally owns this once complexity grows past the benchmark
(`docs/architecture.md` §12/§14).

Update this file every time a subsystem is added (e.g. a Motor Driver /
Reaction Wheel later on the roadmap, `docs/architecture.md` §11) — do not
let it silently go stale.

## Supply Capability

| Rail | Source | Nominal Voltage | Max Current Capability | Source (Evidence ID) |
|---|---|---|---|---|
| `<e.g. 3V3>` | `<e.g. regulator part number>` | `<V>` | `<A>` | `<DS-PWR-xxx>` |

## Subsystem Load

| Rail | Subsystem | Typical Current | Max Current | Source (Evidence ID) | Notes |
|---|---|---|---|---|---|
| `<3V3>` | `<MCU>` | `<mA>` | `<mA>` | `<DS-MCU-xxx>` | |
| `<3V3>` | `<IMU>` | `<mA>` | `<mA>` | `<DS-IMU-xxx>` | |

## Rail Margin Summary

| Rail | Total Max Load | Supply Capability | Margin | Status |
|---|---|---|---|---|
| `<3V3>` | `<sum of Max Current above>` | `<from Supply Capability table>` | `<capability - load>` | `<OK / MARGINAL / EXCEEDED>` |

## Notes

- "Margin" should reflect the project's own de-rating policy (e.g. don't
  load a rail past 80% of its rated max) — record the policy here once the
  human sets it; until then treat any rail without explicit margin policy
  as needing human confirmation before Design Complete.
- Cross-reference this file's Evidence IDs from
  `requirements/traceability-matrix.md` rows covering power requirements.
