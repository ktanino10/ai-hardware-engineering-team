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

## Design: Bench-IMU-01 Rev 3 (Circuit Engineer, 2026-09-04 — motor-rail numbers finalized this pass; Power Engineer role not yet engaged for this project per this file's own note above)

Full design rationale, net-by-net detail, and self-check live in
`hardware/schematic/bench-imu-01-design.md` (§7.5 for the motor subsystem,
§17 for its own power-budget summary cross-reference).
`hardware/power-architecture.md` carries the Option A topology decision
record that precedes this file's own multi-rail numeric rollup. This file
holds only the numeric power-budget rollup, per this file's own stated
purpose.

## Supply Capability

| Rail | Source | Nominal Voltage | Max Current Capability | Source (Evidence ID) |
|---|---|---|---|---|
| 5V (VBUS, pre-regulator) | USB-C VBUS via J1, upstream of U3 | 5.0 V (4.75–5.25 V per REQ-101 / USB spec) | Host/cable-dependent; USB spec floor for a standard-power port is 500 mA, well above this design's actual draw | DS-PWR-002 (LDO Vin ROC 1.45–5.5 V accepts this range) |
| 3V3 | U3 = TLV75533PDBVR (LDO), fixed 3.3 V output | 3.3 V | 500 mA max rated output | DS-PWR-003 |
| **VM_MOTOR (~12V-class, Rev 3 — finalized this revision)** | **J4 = Same Sky PJ-102AH** (right-angle THT barrel jack, 2.0mm center pin=+, DS-CONN-005) → **D2** (STPS3L60, series reverse-polarity Schottky, DS-PROT-005) → **D3** (SMBJ16A, shunt TVS, DS-PROT-004) → U5 VCC | J4/D2/D3 path is rated for up to 24 V (J4's own connector rating, DS-CONN-005) and clamped at 26.0 V max by D3 (DS-PROT-004) — well inside U5's 30 V VCC AMR (DS-MTR-053). **This design's recommended real-world source class is 3S (≈11.1 V nominal, ≈9–12.6 V practical discharge range)** — see the 2S/3S UVLO finding in the Rail Margin Summary below; 2S is flagged marginal-to-non-viable specifically because of D2's added forward-voltage drop | J4 itself is rated **5.0 A** (DS-CONN-005), far above this design's actual worst-case need (see Subsystem Load below). **The actual field DC source plugged into J4 (a battery pack, bench supply, or wall adapter) is an operational choice outside this schematic's own parts list** — the same convention already used for the 5V row above, where the upstream "USB host" is external to this design, not a specified component. Any 3S-class source rated ≥3 A continuous (a low bar for real 3S battery packs or bench supplies) comfortably covers this design's absolute-worst-case draw | DS-CONN-005, DS-PROT-004, DS-PROT-005, DS-MTR-053/054/056/057 |

## Subsystem Load

All subsystem loads below are on the regulated **3V3 rail** (the rail
REQ-103's ≤300 mA budget explicitly applies to) **except** the new Rev 3
motor subsystem, which REQ-109 explicitly requires to be tracked on its own
separate rail. The 5V/VBUS side still has no separate subsystem budget table
for Rev 2 logic loads because, upstream of the LDO, the only baseline loads
are the LDO's own quiescent current and the ESD-protection IC's quiescent
current — both are regulator/protection overhead, not a standalone
"subsystem."

| Rail | Subsystem | Typical Current | Max Current | Source (Evidence ID) | Notes |
|---|---|---|---|---|---|
| 3V3 | MCU (U1, STM32G031K8T6) | 2.1 mA @16 MHz | 10.2 mA @64 MHz | DS-MCU-014 | VDD=3.0 V/Ta=25 °C test condition per datasheet; this design runs VDD=3.3 V, so real draw may differ slightly from the cited figure — not re-characterized at 3.3 V this session, ASSUMPTION that the difference is immaterial at this current scale |
| 3V3 | IMU (U2, BMI270) | 0.685 mA | 0.685 mA | DS-IMU-010 | Combined accel+gyro, full-performance mode (highest-power BMI270 mode; typ. figure used as both typical and max since no separate max was cited) |
| 3V3 | Status LED (D1) + series resistor R5 | ~3.94 mA | ~3.94 mA | ESTIMATE | R5=330 Ω, assumed generic LED Vf≈2.0 V, GPIO PA5 sourcing: I=(3.3−2.0)/330Ω≈3.94 mA. Exact LED MPN not yet selected — ESTIMATE, not a datasheet figure |
| 3V3 | I2C pull-ups (R3, R4 = 4.7 kΩ each, SCL+SDA) | ~0.3 mA (realistic average, bus mostly idle-high or toggling) | ~1.4 mA (worst case, both lines simultaneously held low — atypical/instantaneous, not sustained) | ESTIMATE | Per-line worst case = 3.3 V / 4.7 kΩ ≈0.70 mA; ×2 lines = 1.4 mA if both were low simultaneously, which does not happen in normal I2C operation (SCL/SDA are pulled low only during clock-low/ACK phases, not continuously) — realistic average draw is much lower |
| 3V3 | (excluded from this table, see note) LDO (U3) own quiescent current | 25 µA | 25 µA | DS-PWR-005 | This is regulator overhead drawn from the 5V input side, not a 3V3 rail load — excluded from the 3V3 sum to avoid double-counting; noted here for completeness only |
| 3V3 | (excluded from this table, see note) ESD protection IC (U4, USBLC6-2SC6) quiescent current | <10 µA | <10 µA | ESTIMATE | Drawn from 5V VBUS upstream of the LDO, not the 3V3 rail — excluded from the 3V3 sum for the same reason as the LDO's own Iq; ESTIMATE since USBLC6-2SC6's own quiescent-current figure was not independently pulled this session (typical for this TVS-diode-array part class is low-single-digit µA or less) |
| **3V3** | **Subtotal (MCU + IMU + LED + I2C pull-ups only)** | **≈7.0 mA typical** (2.1+0.685+3.94+0.3) | **≈16.2 mA worst-case** (10.2+0.685+3.94+1.4) | derived, see rows above | This is the number checked against REQ-103 and against the LDO's 500 mA rating below |
| **VM_MOTOR (Rev 3 — finalized this revision)** | Motor + driver subsystem (**M1** = T-Motor MN2206-13 KV2000, **U5** = TI DRV10983) | **≈1.05 A nominal** (derived target current to produce 5 mN·m from Kt≈4.77 mN·m/A) | **≤3 A absolute worst-case** (TI's own datasheet-stated ceiling "during start-up or a locked-motor condition," Table 10 Recommended Application Range) | DS-MTR-020 (nominal derivation, Component-Engineer research) / DS-MTR-056 (3A worst-case ceiling) | U5's own fixed hardware OCP threshold (IOC_limit = 3 MIN/4 MAX A phase-to-phase, DS-MTR-058) sits right at/just above this 3A figure — consistent with 3A being the realistic worst case TI itself designed the part around, not an arbitrary ceiling. **Lock Detection** (I2C-configurable, auto-retry after 5s, DS-MTR-059) — not OCP — is the mechanism actually relied on for REQ-111/404's stall/overcurrent protection; see `hardware/schematic/bench-imu-01-design.md` §7.5.6 for the full mechanism table and the correction this finding implies for `bom/component-selection.md`'s DS-MTR-037 description. **Not separately broken out**: U5's own driver-logic/no-load quiescent current — a distinct figure from the motor phase current above — was not independently extracted from the datasheet's Electrical Characteristics this session; expected to be small relative to the 1.05–3A range already budgeted, but flagged as a residual research gap (§16 item in the design doc) rather than assumed to be zero. |

## Rail Margin Summary

| Rail | Total Max Load | Supply Capability | Margin | Status |
|---|---|---|---|---|
| 3V3 vs. REQ-103 budget | ≈16.2 mA worst-case | 300 mA (REQ-103 ceiling) | ≈283.8 mA (≈94.6%) | OK — very large margin |
| 3V3 vs. regulator capability | ≈16.2 mA worst-case | 500 mA (DS-PWR-003, TLV75533PDBVR rated max) | ≈483.8 mA (≈96.8%) | OK — very large margin |
| 12V-class motor rail vs. J4 connector rating | 3 A absolute worst-case | 5.0 A (DS-CONN-005, J4/PJ-102AH rated max) | 2.0 A (≈40%) | OK — comfortable margin at the connector/protection-path level |
| 12V-class motor rail vs. driver's own OCP threshold | 3 A absolute worst-case | 3 MIN/4 MAX A (DS-MTR-058, U5's fixed hardware OCP threshold) | ≈0–1 A (0–25%) at the MIN threshold | Tight but by design — TI sized OCP to activate right around this same realistic worst case, not as a wide-margin ceiling; this is expected/normal for this protection mechanism, not a design deficiency (it is a protection trip point, not a rail-capacity ceiling) |
| 2S vs. 3S source viability through the added series diode (D2) | n/a (voltage-margin question, not a current-load one) | 2S source ≈7.4V nominal (≈6.0–8.4V realistic range) minus D2's ~0.53–0.62V forward drop ≈ 6.8–6.9V nominal, vs. U5's UVLO rising threshold VUVLO_R = 7/7.4/8V min/typ/max (DS-MTR-057) | **Marginal-to-non-viable at 2S** — even a freshly-charged 2S pack (~8.4V, minus drop ≈7.8V) sits under UVLO_R's max (8V); 2S sags below every UVLO_R threshold well before end-of-discharge | **FLAGGED — practical recommendation is 3S-only operation.** A 3S source (≈11.1V nominal, ≈9–12.6V practical range) minus the same diode drop stays comfortably clear of UVLO across its full discharge range. This is a consequence of this revision's own added protection diode (D2), not a flaw in the Component-Engineer-approved 2S–3S-rated motor (M1) — see `bench-imu-01-design.md` §7.5.2/§16 item 17 |
| 12V-class motor rail vs. recommended 3S field-source class | 3 A absolute worst-case | Any real 3S-class source (LiPo pack or bench supply) rated ≥3 A continuous — a low bar for this source class | Positive in the general case | **Class-level statement only** — the exact field DC source plugged into J4 is an operational choice outside this schematic's own parts list (mirrors the 5V row's "host/cable-dependent" treatment above), not independently benchmarked against one specific named supply this session |

The existing 3V3 margins still comfortably confirm the Component Engineer's
own pre-design expectation in `bom/component-selection.md` ("MCU+IMU are only
~10-15mA combined") — the full logic load including LED and I2C pull-ups
(≈16.2 mA worst-case) is still an order of magnitude below either ceiling.

For Rev 3, **the motor rail is now finalized, not left open**: J4 (Same
Sky PJ-102AH) is the selected connector, rated 24V/5.0A (DS-CONN-005) —
far in excess of this design's real need. REQ-109's separate-tracking
requirement is satisfied (the motor rail is never folded into REQ-103's
3V3 budget above). The one genuinely open numeric item is the **exact
field DC source** (battery pack, bench supply, or adapter) plugged into
J4 — an operational choice outside this schematic's own parts list, the
same way J1's upstream USB host is external to this design — with a
**practical recommendation of 3S-class operation only** (not the full
2S–3S range the motor itself is rated for) flowing from the added series
protection diode's forward-voltage drop against the driver's UVLO
threshold (see the Rail Margin Summary row above).

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

## Thermal cross-check (motor driver, U5) — new this revision

U5 (TI DRV10983, HTSSOP-24/PWP) has RθJA = 36.1°C/W (DS-MTR-055) against a
125°C junction-temperature Recommended Operating Condition ceiling
(DS-MTR-054). At this design's ≈1.05A nominal operating current — an
order of magnitude below the 3A absolute-worst-case/OCP-threshold
region — internal power dissipation (dominated by I²R conduction loss in
the integrated FET bridge) is qualitatively well under 1W, which would
correspond to a junction-temperature rise well under 36°C above ambient
even at RθJA's full value — comfortable margin at any reasonable ambient
temperature this bench design would see. **This is not computed to a
precise worst-case wattage this session**: doing so would require the
integrated FET bridge's own RDS(on), which was not independently
extracted for the DRV10983 specifically (see the design document's §16
item 21 for why a same-family alternate part's figure was deliberately
not substituted in). Thermal Shutdown (150°C, DS-MTR-060) provides a
hardware backstop regardless. No thermal risk expected at this design's
nominal operating point; flagged as a reasonable-but-not-exhaustive
treatment, not a rigorously bounded one, for the Hardware Reviewer.

## Notes

- "Margin" should reflect the project's own de-rating policy (e.g. don't
  load a rail past 80% of its rated max) — record the policy here once the
  human sets it; until then treat any rail without explicit margin policy
  as needing human confirmation before Design Complete. For Bench-IMU-01
  this was a moot/low-stakes gap for the original logic rail: margin is
  ≈95–97% of either ceiling, far outside any plausible de-rating threshold.
  The new Rev 3 motor rail's margin against its own connector (≈40%) and
  driver OCP threshold (0–25%) are tighter but consistent with how TI
  itself sized the driver's protection thresholds — see the Rail Margin
  Summary above.
- Cross-reference this file's Evidence IDs from
  `requirements/traceability-matrix.md` rows covering power requirements.
- Rev 3 motor subsystem addition: do **not** fold motor current into REQ-103's
  3V3 logic budget. Keep the logic rail and motor rail numerically separate
  per REQ-109 and cross-reference the architecture decision in
  `hardware/power-architecture.md`. **This is now satisfied** — see the
  VM_MOTOR rows above, tracked entirely separately from the 3V3 rows.
- The connector-specific numbers in this file (J4 = Same Sky PJ-102AH,
  24V/5.0A) are now final for this revision. If a future revision changes
  the connector, motor, or driver part, this file's Supply Capability,
  Subsystem Load, and Rail Margin Summary tables must all be updated
  together, not just one.
