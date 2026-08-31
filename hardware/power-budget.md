# System Power Budget

Aggregates every subsystem's current/power draw against the supply's
capability, per rail, with margin. Maintained by the Circuit Engineer as
part of `.github/skills/schematic-design/SKILL.md` for a simple single-rail
design; the **Power Engineer** role (Phase 3 of the multidisciplinary
evolution, `docs/architecture-evolution.md` §33) formally owns this file
once complexity grows past the benchmark and is engaged for a given
project/revision (`.github/agents/power-engineer.agent.md` "When this role
is engaged") — see also `hardware/power-architecture.md` for the rail-
topology/source decision record that precedes this file's own multi-rail
numeric rollup.

Update this file every time a subsystem is added (e.g. a Motor Driver /
Reaction Wheel later on the roadmap, `docs/architecture.md` §11) — do not
let it silently go stale.

## Design: Bench-IMU-01 (first entry, Circuit Engineer, 2026-08-31)

Full design rationale, net-by-net detail, and self-check live in
`hardware/schematic/bench-imu-01-design.md`. This file holds only the
numeric power-budget rollup, per this file's own stated purpose.

## Supply Capability

| Rail | Source | Nominal Voltage | Max Current Capability | Source (Evidence ID) |
|---|---|---|---|---|
| 5V (VBUS, pre-regulator) | USB-C VBUS via J1, upstream of U3 | 5.0 V (4.75–5.25 V per REQ-101 / USB spec) | Host/cable-dependent; USB spec floor for a standard-power port is 500 mA, well above this design's actual draw | DS-PWR-002 (LDO Vin ROC 1.45–5.5 V accepts this range) |
| 3V3 | U3 = TLV75533PDBVR (LDO), fixed 3.3 V output | 3.3 V | 500 mA max rated output | DS-PWR-003 |

## Subsystem Load

All subsystem loads below are on the regulated **3V3 rail** (the rail
REQ-103's ≤300 mA budget explicitly applies to). The 5V/VBUS side has no
separate subsystem budget table because, upstream of the LDO, the only
loads are the LDO's own quiescent current and the ESD-protection IC's
quiescent current — both are regulator/protection overhead, not a
"subsystem," and both are individually negligible (noted below rather than
tabulated as a subsystem row).

| Rail | Subsystem | Typical Current | Max Current | Source (Evidence ID) | Notes |
|---|---|---|---|---|---|
| 3V3 | MCU (U1, STM32G031K8T6) | 2.1 mA @16 MHz | 10.2 mA @64 MHz | DS-MCU-014 | VDD=3.0 V/Ta=25 °C test condition per datasheet; this design runs VDD=3.3 V, so real draw may differ slightly from the cited figure — not re-characterized at 3.3 V this session, ASSUMPTION that the difference is immaterial at this current scale |
| 3V3 | IMU (U2, BMI270) | 0.685 mA | 0.685 mA | DS-IMU-010 | Combined accel+gyro, full-performance mode (highest-power BMI270 mode; typ. figure used as both typical and max since no separate max was cited) |
| 3V3 | Status LED (D1) + series resistor R5 | ~3.94 mA | ~3.94 mA | ESTIMATE | R5=330 Ω, assumed generic LED Vf≈2.0 V, GPIO PA5 sourcing: I=(3.3−2.0)/330Ω≈3.94 mA. Exact LED MPN not yet selected — ESTIMATE, not a datasheet figure |
| 3V3 | I2C pull-ups (R3, R4 = 4.7 kΩ each, SCL+SDA) | ~0.3 mA (realistic average, bus mostly idle-high or toggling) | ~1.4 mA (worst case, both lines simultaneously held low — atypical/instantaneous, not sustained) | ESTIMATE | Per-line worst case = 3.3 V / 4.7 kΩ ≈0.70 mA; ×2 lines = 1.4 mA if both were low simultaneously, which does not happen in normal I2C operation (SCL/SDA are pulled low only during clock-low/ACK phases, not continuously) — realistic average draw is much lower |
| 3V3 | (excluded from this table, see note) LDO (U3) own quiescent current | 25 µA | 25 µA | DS-PWR-005 | This is regulator overhead drawn from the 5V input side, not a 3V3 rail load — excluded from the 3V3 sum to avoid double-counting; noted here for completeness only |
| 3V3 | (excluded from this table, see note) ESD protection IC (U4, USBLC6-2SC6) quiescent current | <10 µA | <10 µA | ESTIMATE | Drawn from 5V VBUS upstream of the LDO, not the 3V3 rail — excluded from the 3V3 sum for the same reason as the LDO's own Iq; ESTIMATE since USBLC6-2SC6's own quiescent-current figure was not independently pulled this session (typical for this TVS-diode-array part class is low-single-digit µA or less) |
| **3V3** | **Subtotal (MCU + IMU + LED + I2C pull-ups only)** | **≈7.0 mA typical** (2.1+0.685+3.94+0.3) | **≈16.2 mA worst-case** (10.2+0.685+3.94+1.4) | derived, see rows above | This is the number checked against REQ-103 and against the LDO's 500 mA rating below |

## Rail Margin Summary

| Rail | Total Max Load | Supply Capability | Margin | Status |
|---|---|---|---|---|
| 3V3 vs. REQ-103 budget | ≈16.2 mA worst-case | 300 mA (REQ-103 ceiling) | ≈283.8 mA (≈94.6%) | OK — very large margin |
| 3V3 vs. regulator capability | ≈16.2 mA worst-case | 500 mA (DS-PWR-003, TLV75533PDBVR rated max) | ≈483.8 mA (≈96.8%) | OK — very large margin |

Both margins comfortably confirm the Component Engineer's own
pre-design expectation in `bom/component-selection.md` ("MCU+IMU are only
~10-15mA combined") — the full subsystem load including LED and I2C
pull-ups (≈16.2 mA worst-case) is still an order of magnitude below either
ceiling. No rail is MARGINAL or EXCEEDED.

## Thermal cross-check (LDO, U3)

Reusing the thermal-margin numbers already computed in
`bom/component-selection.md`'s Power Regulator section (not recomputed
here — same part, same board-level assumptions): at a conservative
worst-case 300 mA load (REQ-103's own ceiling, ~18–20× this design's actual
≈16.2 mA draw) and 40 °C ambient, estimated TJ ≈71 °C against a 150 °C
TJ,max — ≈79 °C headroom. Since this design's real 3V3 load (≈16.2 mA
worst-case) is far below the 300 mA figure that thermal estimate already
used, actual junction heating in this design is lower still than the
already-comfortable ~71 °C estimate (power dissipation in a linear LDO
scales with output current at fixed Vin−Vout, so ≈16.2 mA of load
dissipates roughly 1/18th the power of the 300 mA case). No thermal risk.

## Notes

- "Margin" should reflect the project's own de-rating policy (e.g. don't
  load a rail past 80% of its rated max) — record the policy here once the
  human sets it; until then treat any rail without explicit margin policy
  as needing human confirmation before Design Complete. For Bench-IMU-01
  this is a moot/low-stakes gap: margin is ≈95–97% of either ceiling, far
  outside any plausible de-rating threshold, so the missing formal policy
  does not block this design's Rail Margin Summary from reading OK.
- Cross-reference this file's Evidence IDs from
  `requirements/traceability-matrix.md` rows covering power requirements.
- Next subsystem addition (e.g. a Motor Driver / Reaction Wheel per
  `docs/architecture.md` §11) must add its own Subsystem Load rows here and
  re-check the Rail Margin Summary — do not let this file go stale.
