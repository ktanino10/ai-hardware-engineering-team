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

## Design: Bench-IMU-01 Rev 4 (Circuit Engineer, 2026-09-06 — Independent Review Cycle 3 rework: motor-rail envelope bound + PTC fuse added, 2S/3S conclusion sharpened, SPEED pulldown added)

Full design rationale, net-by-net detail, and self-check live in
`hardware/schematic/bench-imu-01-design.md` (§7.5 for the motor subsystem,
§7.5.9–§7.5.12 for this revision's Cycle 3 rework additions, §17 for its
own power-budget summary cross-reference).
`hardware/power-architecture.md` carries the Option A topology decision
record that precedes this file's own multi-rail numeric rollup. This file
holds only the numeric power-budget rollup, per this file's own stated
purpose.

## Supply Capability

| Rail | Source | Nominal Voltage | Max Current Capability | Source (Evidence ID) |
|---|---|---|---|---|
| 5V (VBUS, pre-regulator) | USB-C VBUS via J1, upstream of U3 | 5.0 V (4.75–5.25 V per REQ-101 / USB spec) | Host/cable-dependent; USB spec floor for a standard-power port is 500 mA, well above this design's actual draw | DS-PWR-002 (LDO Vin ROC 1.45–5.5 V accepts this range) |
| 3V3 | U3 = TLV75533PDBVR (LDO), fixed 3.3 V output | 3.3 V | 500 mA max rated output | DS-PWR-003 |
| **VM_MOTOR (9.0–13.0V bounded envelope, 3S-only — sharpened/extended Rev 4)** | **J4 = Same Sky PJ-102AH** (right-angle THT barrel jack, 2.0mm center pin=+, DS-CONN-005) → **F1** (Littelfuse 30R500U, PTC resettable fuse, new Rev 4, DS-PROT-006) → **D2** (STPS3L60, series reverse-polarity Schottky, DS-PROT-005) → **D3** (SMBJ16A, shunt TVS, DS-PROT-004) → U5 VCC | J4/F1/D2/D3 path is rated for up to 24 V (J4's own connector rating, DS-CONN-005) and clamped at 26.0 V max by D3 (DS-PROT-004) — well inside U5's 30 V VCC AMR (DS-MTR-053). **Rev 4: this design's source class is now a binding 9.0–13.0V envelope, 3S-only** (ISS-014/ISS-019, `bench-imu-01-design.md` §7.5.2/§7.5.9) — not a soft recommendation. 2S is **not viable**: it fails UVLO margin at its typical corner already (see the Rail Margin Summary row below, corrected this revision) | J4 itself is rated **5.0 A** (DS-CONN-005); **new F1** adds Ihold=5.00A/Itrip=10.00A/Vmax=30Vdc/Imax=40A bounding fault-current magnitude/duration upstream of D2/D3 (honestly scoped: F1's own 10.00A Itrip exceeds J4's own 5.0A rating, so F1 is not a precisely-matched limiter for J4 itself — protective value is against short-circuit-level faults). **The actual field DC source plugged into J4 (a battery pack, bench supply, or wall adapter) is an operational choice outside this schematic's own parts list** — the same convention already used for the 5V row above, where the upstream "USB host" is external to this design, not a specified component. Any 3S-class source rated ≥3 A continuous, within the 9.0–13.0V envelope, comfortably covers this design's absolute-worst-case draw | DS-CONN-005, DS-PROT-004, DS-PROT-005, DS-PROT-006, DS-MTR-053/054/056/057 |

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
| **3V3** | **New Rev 4: SPEED external pulldown (R10 = 1kΩ, ISS-015)** | **~1.65 mA** (representative mid-duty (~50%) illustrative figure — genuinely PWM-duty-cycle dependent, not a fixed draw) | **~3.3 mA** (worst case, PA8/TIM1_CH1 instantaneously high: 3.3V/1kΩ) | derived, `bench-imu-01-design.md` §7.5.5/§17 | R10 is wired on the motor-domain's SPEED net (U1 PA8 → U5 SPEED, §12) but physically draws from the **3V3 rail**, not VM_MOTOR, since PA8 is a 3.3V-logic MCU GPIO — current only flows while PA8 drives instantaneously high; 0 mA whenever PA8 is instantaneously low. Added this revision to fix ISS-015 (uncommanded-motion risk); negligible relative to REQ-103's 300 mA budget |
| 3V3 | (excluded from this table, see note) LDO (U3) own quiescent current | 25 µA | 25 µA | DS-PWR-005 | This is regulator overhead drawn from the 5V input side, not a 3V3 rail load — excluded from the 3V3 sum to avoid double-counting; noted here for completeness only |
| 3V3 | (excluded from this table, see note) ESD protection IC (U4, USBLC6-2SC6) quiescent current | <10 µA | <10 µA | ESTIMATE | Drawn from 5V VBUS upstream of the LDO, not the 3V3 rail — excluded from the 3V3 sum for the same reason as the LDO's own Iq; ESTIMATE since USBLC6-2SC6's own quiescent-current figure was not independently pulled this session (typical for this TVS-diode-array part class is low-single-digit µA or less) |
| **3V3** | **Subtotal (MCU + IMU + LED + I2C pull-ups + R10, Rev 4)** | **≈8.65 mA typical** (2.1+0.685+3.94+0.3+1.65) | **≈19.5 mA worst-case** (10.2+0.685+3.94+1.4+3.3) | derived, see rows above | This is the number checked against REQ-103 and against the LDO's 500 mA rating below. **New Rev 4**: R10 added ≈1.65 mA typical/≈3.3 mA worst-case vs. the prior (Rev 2/3) ≈7.0 mA typical/≈16.2 mA worst-case subtotal — a small, non-rail-threatening addition |
| **VM_MOTOR (Rev 3 baseline, latching caveat added Rev 4)** | Motor + driver subsystem (**M1** = T-Motor MN2206-13 KV2000, **U5** = TI DRV10983) | **≈1.05 A nominal** (derived target current to produce 5 mN·m from Kt≈4.77 mN·m/A) | **≤3 A absolute worst-case** (TI's own datasheet-stated ceiling "during start-up or a locked-motor condition," Table 10 Recommended Application Range) | DS-MTR-020 (nominal derivation, Component-Engineer research) / DS-MTR-056 (3A worst-case ceiling) | U5's own fixed hardware OCP threshold (IOC_limit = 3 MIN/4 MAX A phase-to-phase, DS-MTR-058) sits right at/just above this 3A figure — consistent with 3A being the realistic worst case TI itself designed the part around, not an arbitrary ceiling. **Lock Detection** (I2C-configurable, auto-retry after 5s, DS-MTR-059) — not OCP — is the mechanism actually relied on for REQ-111/404's stall/overcurrent protection; see `hardware/schematic/bench-imu-01-design.md` §7.5.6 for the full mechanism table and the correction this finding implies for `bom/component-selection.md`'s DS-MTR-037 description. **Rev 4 caveat (ISS-021)**: OCP, Lock Detection, and Thermal Shutdown (DS-MTR-058/059/060) all **auto-recover; none latch** — REQ-404's "Should"-priority shutdown-behavior intent is not fully satisfied by U5's hardware alone; a firmware latched-fault policy is now an explicit new requirement, `bench-imu-01-design.md` §7.5.12. **Not separately broken out**: U5's own driver-logic/no-load quiescent current — a distinct figure from the motor phase current above — was not independently extracted from the datasheet's Electrical Characteristics this session; expected to be small relative to the 1.05–3A range already budgeted, but flagged as a residual research gap (§16 item in the design doc) rather than assumed to be zero. |

## Rail Margin Summary

| Rail | Total Max Load | Supply Capability | Margin | Status |
|---|---|---|---|---|
| 3V3 vs. REQ-103 budget (Rev 4: includes new R10) | ≈19.5 mA worst-case | 300 mA (REQ-103 ceiling) | ≈280.5 mA (≈93.5%) | OK — very large margin |
| 3V3 vs. regulator capability (Rev 4: includes new R10) | ≈19.5 mA worst-case | 500 mA (DS-PWR-003, TLV75533PDBVR rated max) | ≈480.5 mA (≈96.1%) | OK — very large margin |
| VM_MOTOR rail vs. J4 connector rating | 3 A absolute worst-case | 5.0 A (DS-CONN-005, J4/PJ-102AH rated max) | 2.0 A (≈40%) | OK — comfortable margin at the connector/protection-path level |
| **New Rev 4: VM_MOTOR rail vs. F1 (PTC fuse) hold current** | 3 A absolute worst-case | 5.00 A Ihold @20°C ambient, derating to 3.05A @70°C (DS-PROT-006) | 2.0 A (≈40%) @20°C, narrowing to ≈0.05A (≈1.7%) @70°C ambient | **OK at typical bench ambient (20–25°C); tight-but-still-positive at 70°C ambient** — F1's Ihold stays ≥3A through the datasheet's own 70°C table point, only derating below the 3A worst-case current between 70°C and 85°C ambient (≈71.7°C interpolated crossing). Not a concern for a benchtop project's expected ambient range, flagged for completeness (`bench-imu-01-design.md` §7.5.9) |
| VM_MOTOR rail vs. driver's own OCP threshold | 3 A absolute worst-case | 3 MIN/4 MAX A (DS-MTR-058, U5's fixed hardware OCP threshold) | ≈0–1 A (0–25%) at the MIN threshold | Tight but by design — TI sized OCP to activate right around this same realistic worst case, not as a wide-margin ceiling; this is expected/normal for this protection mechanism, not a design deficiency (it is a protection trip point, not a rail-capacity ceiling) |
| **2S vs. 3S source viability through the added series diode (D2) — corrected/sharpened Rev 4 (ISS-014)** | n/a (voltage-margin question, not a current-load one) | 2S near-nominal ≈7.4V minus D2's ~0.53V **typical** forward drop (@3A/100°C) ≈6.87V, vs. U5's UVLO rising threshold VUVLO_R **typical** = 7.4V (DS-MTR-057); 3S near-cutoff ≈9.0V minus D2's ~0.62V **max** forward drop (@3A/25°C) ≈8.38V, vs. VUVLO_R **max** = 8V, minus new F1's ~0.06V ESTIMATE added series drop ≈8.32V | **2S fails at the TYPICAL corner, not just a worst-case/rare corner** — 6.87V < 7.4V typ. **3S clears UVLO at every corner**, margin ≈0.38V before F1, narrowing to ≈0.32V with F1's estimated drop included | **3S-only is now the binding constraint, not a soft recommendation.** A 3S source (≈11.1V nominal, ≈9.0–12.6V practical discharge range, now the design's stated 9.0–13.0V envelope's lower bound) clears UVLO across its full discharge range even with F1's added drop. This is a consequence of this design's own added protection diode (D2) plus new PTC fuse (F1), not a flaw in the Component-Engineer-approved 2S–3S-rated motor (M1) — see `bench-imu-01-design.md` §7.5.2 for the full corner-by-corner analysis |
| VM_MOTOR rail vs. recommended 3S field-source class, within the new 9.0–13.0V bounded envelope (Rev 4) | 3 A absolute worst-case | Any real 3S-class source (LiPo pack or bench supply) rated ≥3 A continuous, within 9.0–13.0V — a low bar for this source class | Positive in the general case | **Class-level statement only** — the exact field DC source plugged into J4 is an operational choice outside this schematic's own parts list (mirrors the 5V row's "host/cable-dependent" treatment above), not independently benchmarked against one specific named supply this session. **No continuous/steady-state OVP exists** upstream of F1/D3 to actively enforce the 13.0V upper bound in real time — it is a stated operating envelope, not an actively-clamped one (D3's TVS clamp is a transient/surge protector at a much higher 26.0V threshold, not a steady-state limiter) — flagged, `bench-imu-01-design.md` §16 item 22-adjacent note |

The existing 3V3 margins still comfortably confirm the Component Engineer's
own pre-design expectation in `bom/component-selection.md` ("MCU+IMU are only
~10-15mA combined") — the full logic load including LED, I2C pull-ups, and
new Rev 4 R10 (≈19.5 mA worst-case) is still an order of magnitude below
either ceiling.

For Rev 3, **the motor rail was finalized as a connector/topology choice**:
J4 (Same Sky PJ-102AH) is the selected connector, rated 24V/5.0A
(DS-CONN-005) — far in excess of this design's real need. REQ-109's
separate-tracking requirement is satisfied (the motor rail is never folded
into REQ-103's 3V3 budget above). **Rev 4 (Cycle 3 rework) sharpens this
further**: the one item Rev 3 had left as a "recommendation" — the source
class plugged into J4 — is now a **binding 9.0–13.0V envelope, 3S-only**
(ISS-014/ISS-019), not a soft preference; 2S is confirmed non-viable at
its typical corner, not just a rare worst case (see the Rail Margin
Summary row above). The exact **field DC source** (battery pack, bench
supply, or adapter) plugged into J4 remains an operational choice outside
this schematic's own parts list, the same way J1's upstream USB host is
external to this design — but it must now fall within the stated
envelope. A new PTC fuse (F1) bounds fault-current magnitude/duration
upstream of D2/D3, though no continuous/steady-state OVP exists to
actively enforce the 13.0V upper bound (see the Rail Margin Summary row
above and `bench-imu-01-design.md` §7.5.9/§16).

## Thermal cross-check (LDO, U3)

Reusing the thermal-margin numbers already computed in
`bom/component-selection.md`'s Power Regulator section (not recomputed
here — same part, same board-level assumptions): at a conservative
worst-case 300 mA load (REQ-103's own ceiling, ~15× this design's actual
≈19.5 mA draw, Rev 4 figure including R10) and 40 °C ambient, estimated
TJ ≈71 °C against a 150 °C TJ,max — ≈79 °C headroom. Since this design's
real 3V3 load (≈19.5 mA worst-case) is far below the 300 mA figure that
thermal estimate already used, actual junction heating in this design is
lower still than the already-comfortable ~71 °C estimate (power
dissipation in a linear LDO scales with output current at fixed
Vin−Vout, so ≈19.5 mA of load dissipates roughly 1/15th the power of the
300 mA case). No thermal risk.

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
  ≈93.5–96.1% of either ceiling (Rev 4, after R10's small addition — was
  ≈94.6–96.8% pre-Rev 4), far outside any plausible de-rating threshold.
  The motor rail's margin against its own connector (≈40%) and driver OCP
  threshold (0–25%) are tighter but consistent with how TI itself sized
  the driver's protection thresholds — see the Rail Margin Summary above.
- Cross-reference this file's Evidence IDs from
  `requirements/traceability-matrix.md` rows covering power requirements.
- Rev 3 motor subsystem addition: do **not** fold motor current into REQ-103's
  3V3 logic budget. Keep the logic rail and motor rail numerically separate
  per REQ-109 and cross-reference the architecture decision in
  `hardware/power-architecture.md`. **This is now satisfied** — see the
  VM_MOTOR rows above, tracked entirely separately from the 3V3 rows.
- The connector-specific numbers in this file (J4 = Same Sky PJ-102AH,
  24V/5.0A) are final for this revision. **Rev 4 (Cycle 3 rework) adds**:
  F1 (Littelfuse 30R500U PTC fuse, DS-PROT-006) in series ahead of D2/D3,
  and sharpens the source class from a "recommendation" to a **binding
  9.0–13.0V envelope, 3S-only**. If a future revision changes the
  connector, motor, driver, or protection-path part, this file's Supply
  Capability, Subsystem Load, and Rail Margin Summary tables must all be
  updated together, not just one.
- **New Rev 4 residual gap**: no continuous/steady-state OVP exists
  upstream of F1/D3 to actively enforce the 9.0–13.0V envelope's upper
  bound in real time (D3's TVS clamp is a transient/surge protector at a
  much higher 26.0V threshold, not a steady-state limiter) — the envelope
  is a stated operating constraint, not an actively-enforced one. Flagged
  for Hardware Lead awareness, not fixed this revision (`bench-imu-01-design.md`
  §16 near items 22–26).
