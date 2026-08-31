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

## Design: Bench-IMU-01 Rev 5 (Circuit Engineer, 2026-09-08 — Independent Review Cycle 4 rework: U6 = TPS26631PWPR supervisory eFuse/load-switch added upstream of U5, F1 swapped to the active 30R500UF, continuous OVP/UVLO lockout now enforced)

Full design rationale, net-by-net detail, and self-check live in
`hardware/schematic/bench-imu-01-design.md` (§7.5 for the motor subsystem,
§7.5.9–§7.5.12 for Rev 4's Cycle 3 rework additions, §7.5.10 for Rev 5's
U6 implementation, §17 for its own power-budget summary cross-reference).
`hardware/power-architecture.md` carries the Option A topology decision
record that precedes this file's own multi-rail numeric rollup. This file
holds only the numeric power-budget rollup, per this file's own stated
purpose.

## Supply Capability

| Rail | Source | Nominal Voltage | Max Current Capability | Source (Evidence ID) |
|---|---|---|---|---|
| 5V (VBUS, pre-regulator) | USB-C VBUS via J1, upstream of U3 | 5.0 V (4.75–5.25 V per REQ-101 / USB spec) | Host/cable-dependent; USB spec floor for a standard-power port is 500 mA, well above this design's actual draw | DS-PWR-002 (LDO Vin ROC 1.45–5.5 V accepts this range) |
| 3V3 | U3 = TLV75533PDBVR (LDO), fixed 3.3 V output | 3.3 V | 500 mA max rated output | DS-PWR-003 |
| **VM_MOTOR (9.0–13.0V bounded envelope, 3S-only — sharpened/extended Rev 4, continuous OVP/UVLO added Rev 5)** | **J4 = Same Sky PJ-102AH** (right-angle THT barrel jack, 2.0mm center pin=+, DS-CONN-005) → **F1** (Littelfuse 30R500UF, PTC resettable fuse, MPN swapped Rev 5 from the obsolete 30R500U, DS-PROT-006/032/033) → **D2** (STPS3L60, series reverse-polarity Schottky, DS-PROT-005) → **D3** (SMBJ16A, shunt TVS, DS-PROT-004) → **U6** (new Rev 5: TPS26631PWPR, supervisory load-switch/eFuse controller, DS-PROT-023–031) → U5 VCC | J4/F1/D2/D3/U6 path is rated for up to 24 V (J4's own connector rating, DS-CONN-005) and clamped at 26.0 V max by D3 (DS-PROT-004) — well inside U5's 30 V VCC AMR (DS-MTR-053) and U6's own 67V AMR (DS-PROT-030). This design's source class is a binding 9.0–13.0V envelope, 3S-only (ISS-014/ISS-019, `bench-imu-01-design.md` §7.5.2/§7.5.9) — not a soft recommendation. 2S is **not viable**: it fails UVLO margin at its typical corner already (see the Rail Margin Summary row below). **New Rev 5**: U6 now actively enforces both ends of this envelope continuously (not just at transient/surge level) via its own OVP/UVLO resistor divider (R12/R13/R14) — closing the gap the Rev 4 revision of this file flagged as a residual "no continuous/steady-state OVP" item (see Rail Margin Summary below) | J4 itself is rated **5.0 A** (DS-CONN-005); F1 adds Ihold=5.00A/Itrip=10.00A/Vmax=30Vdc/Imax=40A bounding fault-current magnitude/duration upstream of D2/D3 (honestly scoped: F1's own 10.00A Itrip exceeds J4's own 5.0A rating, so F1 is not a precisely-matched limiter for J4 itself — protective value is against short-circuit-level faults). U6 adds its own adjustable overload current limit (R15=3.57kΩ → I(OL)≈4.69/5.04/5.40A min/typ/max, DS-PROT-027) sitting between U5's own OCP (3-4A) and F1's Itrip (10A) in the protection hierarchy. **The actual field DC source plugged into J4 (a battery pack, bench supply, or wall adapter) is an operational choice outside this schematic's own parts list** — the same convention already used for the 5V row above, where the upstream "USB host" is external to this design, not a specified component. Any 3S-class source rated ≥3 A continuous, within the 9.0–13.0V envelope, comfortably covers this design's absolute-worst-case draw | DS-CONN-005, DS-PROT-004, DS-PROT-005, DS-PROT-006, DS-PROT-023–033, DS-MTR-053/054/056/057 |

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
| **3V3** | **New Rev 5: U6 SHDN external pulldown (R11 = 10kΩ, §7.5.10)** | **≈330 µA when PA9 is driven high** (0 mA when PA9 is held low — the fail-safe default) | **≈330 µA** (3.3V/10kΩ — a static GPIO level, not PWM, so typical=worst-case unlike R10) | derived, `bench-imu-01-design.md` §7.5.10/§17 | R11 is wired on U6's SHDN/enable net (U1 PA9 → U6 SHDN) but physically draws from the **3V3 rail**, not VM_MOTOR, since PA9 is a 3.3V-logic MCU GPIO. Sized to dominate U6's own internal SHDN pull-up (≈440kΩ–1MΩ depending on source, DS-PROT-025) by 44–100×, while resting on a separate, guaranteed 10µA-leakage datasheet spec (DS-PROT-024) rather than either pull-up figure. Folded into both totals below as a continuous (non-duty-cycle) addition, since PA9 is held high throughout normal motor-enabled operation |
| 3V3 | (excluded from this table, see note) LDO (U3) own quiescent current | 25 µA | 25 µA | DS-PWR-005 | This is regulator overhead drawn from the 5V input side, not a 3V3 rail load — excluded from the 3V3 sum to avoid double-counting; noted here for completeness only |
| 3V3 | (excluded from this table, see note) ESD protection IC (U4, USBLC6-2SC6) quiescent current | <10 µA | <10 µA | ESTIMATE | Drawn from 5V VBUS upstream of the LDO, not the 3V3 rail — excluded from the 3V3 sum for the same reason as the LDO's own Iq; ESTIMATE since USBLC6-2SC6's own quiescent-current figure was not independently pulled this session (typical for this TVS-diode-array part class is low-single-digit µA or less) |
| **3V3** | **Subtotal (MCU + IMU + LED + I2C pull-ups + R10 + R11, Rev 5)** | **≈8.98 mA typical** (2.1+0.685+3.94+0.3+1.65+0.33) | **≈19.83 mA worst-case** (10.2+0.685+3.94+1.4+3.3+0.33) | derived, see rows above | This is the number checked against REQ-103 and against the LDO's 500 mA rating below. **New Rev 5**: R11 added ≈330µA (both typical and worst-case, being a static level) vs. the prior (Rev 4) ≈8.65 mA typical/≈19.5 mA worst-case subtotal — a small, non-rail-threatening addition, continuing the same negligible-impact pattern R10 established in Rev 4 |
| **VM_MOTOR** | **New Rev 5: U6 (TPS26631PWPR) own current draw** | **≈1.38 mA typ (IQ(ON), device enabled) + ≈10.6 µA typ (OVP/UVLO divider bias, always present)** ≈ **1.39 mA typ combined** | **≈1.7 mA max (IQ(ON)) + ≈12.55 µA max (divider bias)** ≈ **1.76 mA max combined**; **≈60 µA max (IQ(OFF)) + ≈12.55 µA max (divider bias)** ≈ **≈73 µA max combined when disabled (SHDN low)** | DS-PROT-031 (IQ(ON)/IQ(OFF)), DS-PROT-026 (divider bias, derived from R12/R13/R14=887k/60.4k/88.7kΩ against the 1.176–1.224V reference) | Divider bias current flows continuously regardless of SHDN state (the divider taps IN_SYS directly, ahead of the internal load-switch), while IQ(ON) vs. IQ(OFF) depends on whether U6 is enabled. Combined worst case ≈1.76 mA is **under 0.06%** of J4's 5.0A connector rating and **under 0.06%** of U5's own 3–4A OCP window — not material to any VM_MOTOR margin figure below. (R11's own ≈330µA is a **3V3** rail draw, tracked in the row above instead — never double-counted here.) |
| **VM_MOTOR (Rev 3 baseline, latching caveat added Rev 4)** | Motor + driver subsystem (**M1** = T-Motor MN2206-13 KV2000, **U5** = TI DRV10983) | **≈1.05 A nominal** (derived target current to produce 5 mN·m from Kt≈4.77 mN·m/A) | **≤3 A absolute worst-case** (TI's own datasheet-stated ceiling "during start-up or a locked-motor condition," Table 10 Recommended Application Range) | DS-MTR-020 (nominal derivation, Component-Engineer research) / DS-MTR-056 (3A worst-case ceiling) | U5's own fixed hardware OCP threshold (IOC_limit = 3 MIN/4 MAX A phase-to-phase, DS-MTR-058) sits right at/just above this 3A figure — consistent with 3A being the realistic worst case TI itself designed the part around, not an arbitrary ceiling. **New Rev 5**: U6's own adjustable overload current limit (R15=3.57kΩ → I(OL)≈4.69/5.04/5.40A, DS-PROT-027) now sits between this 3–4A OCP figure and F1's 10A Itrip, completing a 3-tier protection hierarchy. **Lock Detection** (I2C-configurable, auto-retry after 5s, DS-MTR-059) — not OCP — is the mechanism actually relied on for REQ-111/404's stall/overcurrent protection; see `hardware/schematic/bench-imu-01-design.md` §7.5.6 for the full mechanism table and the correction this finding implies for `bom/component-selection.md`'s DS-MTR-037 description. **Rev 4 caveat (ISS-021)**: OCP, Lock Detection, and Thermal Shutdown (DS-MTR-058/059/060) all **auto-recover; none latch** — REQ-404's "Should"-priority shutdown-behavior intent is not fully satisfied by U5's hardware alone; a firmware latched-fault policy remains an explicit requirement, `bench-imu-01-design.md` §7.5.12. **Rev 5 note**: U6 now gives that eventual firmware latch a physical actuation point (PA9/SHDN) — it does not implement the latch policy itself (§16 item 25, unchanged; ISS-020/ISS-021 remain open firmware-policy items, not resolved by this hardware addition). **Not separately broken out**: U5's own driver-logic/no-load quiescent current — a distinct figure from the motor phase current above — was not independently extracted from the datasheet's Electrical Characteristics this session; expected to be small relative to the 1.05–3A range already budgeted, but flagged as a residual research gap (§16 item in the design doc) rather than assumed to be zero. |

## Rail Margin Summary

| Rail | Total Max Load | Supply Capability | Margin | Status |
|---|---|---|---|---|
| 3V3 vs. REQ-103 budget (Rev 5: includes R10 + new R11) | ≈19.83 mA worst-case | 300 mA (REQ-103 ceiling) | ≈280.2 mA (≈93.4%) | OK — very large margin (was ≈93.5% pre-R11) |
| 3V3 vs. regulator capability (Rev 5: includes R10 + new R11) | ≈19.83 mA worst-case | 500 mA (DS-PWR-003, TLV75533PDBVR rated max) | ≈480.2 mA (≈96.0%) | OK — very large margin (was ≈96.1% pre-R11) |
| VM_MOTOR rail vs. J4 connector rating | 3 A absolute worst-case | 5.0 A (DS-CONN-005, J4/PJ-102AH rated max) | 2.0 A (≈40%) | OK — comfortable margin at the connector/protection-path level |
| VM_MOTOR rail vs. F1 (PTC fuse) hold current (Rev 5: MPN now 30R500UF, same rating, DS-PROT-006/032/033) | 3 A absolute worst-case | 5.00 A Ihold @20°C ambient, derating to 3.05A @70°C (DS-PROT-006) | 2.0 A (≈40%) @20°C, narrowing to ≈0.05A (≈1.7%) @70°C ambient | **OK at typical bench ambient (20–25°C); tight-but-still-positive at 70°C ambient** — F1's Ihold stays ≥3A through the datasheet's own 70°C table point, only derating below the 3A worst-case current between 70°C and 85°C ambient (≈71.7°C interpolated crossing). Not a concern for a benchtop project's expected ambient range, flagged for completeness (`bench-imu-01-design.md` §7.5.9). MPN swap to 30R500UF this revision is electrically/mechanically identical (DS-PROT-033) — this row's figures are unchanged by the swap |
| **New Rev 5: VM_MOTOR rail vs. U6 (TPS26631PWPR) overload current limit** | 3 A absolute worst-case | 4.69/5.04/5.40 A min/typ/max (I(OL), set via R15=3.57kΩ, DS-PROT-027) | ≈1.69–2.40 A (≈36–44%) at the min corner | OK — U6's overload trip sits comfortably above the 3A worst-case motor current and below F1's 10A Itrip, completing a 3-tier hierarchy: **U5 OCP (3–4A, first line) → U6 overload (4.69–5.40A, second line) → F1 PTC (10A, last-resort fault-current bound)**. Deliberately biased toward the nearest E96 value below TI's own tested 4.02kΩ table row (raising, not lowering, the trip current) so U6 does not pre-empt U5's own OCP as the primary protection mechanism |
| VM_MOTOR rail vs. driver's own OCP threshold | 3 A absolute worst-case | 3 MIN/4 MAX A (DS-MTR-058, U5's fixed hardware OCP threshold) | ≈0–1 A (0–25%) at the MIN threshold | Tight but by design — TI sized OCP to activate right around this same realistic worst case, not as a wide-margin ceiling; this is expected/normal for this protection mechanism, not a design deficiency (it is a protection trip point, not a rail-capacity ceiling) |
| **2S vs. 3S source viability through the added series diode (D2) — corrected/sharpened Rev 4 (ISS-014); unaffected by Rev 5's U6 addition** | n/a (voltage-margin question, not a current-load one) | 2S near-nominal ≈7.4V minus D2's ~0.53V **typical** forward drop (@3A/100°C) ≈6.87V, vs. U5's UVLO rising threshold VUVLO_R **typical** = 7.4V (DS-MTR-057); 3S near-cutoff ≈9.0V minus D2's ~0.62V **max** forward drop (@3A/25°C) ≈8.38V, vs. VUVLO_R **max** = 8V, minus F1's ~0.06V ESTIMATE added series drop ≈8.32V | **2S fails at the TYPICAL corner, not just a worst-case/rare corner** — 6.87V < 7.4V typ. **3S clears UVLO at every corner**, margin ≈0.38V before F1, narrowing to ≈0.32V with F1's estimated drop included | **3S-only is the binding constraint, not a soft recommendation.** A 3S source (≈11.1V nominal, ≈9.0–12.6V practical discharge range, the design's stated 9.0–13.0V envelope's lower bound) clears UVLO across its full discharge range even with F1's added drop. This is a consequence of this design's own added protection diode (D2) plus PTC fuse (F1), not a flaw in the Component-Engineer-approved 2S–3S-rated motor (M1) — see `bench-imu-01-design.md` §7.5.2 for the full corner-by-corner analysis. **Rev 5 note**: this row analyzes U5's own internal UVLO pin — a separate, downstream mechanism from U6's own UVLO divider (row below), which now trips first (8.17–8.65V full range) in most scenarios since it sits electrically upstream of U5 |
| VM_MOTOR rail vs. recommended 3S field-source class, within the 9.0–13.0V bounded envelope (Rev 4; continuous enforcement added Rev 5) | 3 A absolute worst-case | Any real 3S-class source (LiPo pack or bench supply) rated ≥3 A continuous, within 9.0–13.0V — a low bar for this source class | Positive in the general case | **Class-level statement only** — the exact field DC source plugged into J4 is an operational choice outside this schematic's own parts list (mirrors the 5V row's "host/cable-dependent" treatment above), not independently benchmarked against one specific named supply this session. **New Rev 5 — the prior "no continuous/steady-state OVP" gap is now CLOSED**: U6's own OVP/UVLO resistor divider (R12=887kΩ/R13=60.4kΩ/R14=88.7kΩ) actively and continuously enforces both ends of the 9.0–13.0V envelope, not just the transient/surge level D3's TVS clamp already covered (26.0V threshold). OVP trips at 13.7368/14.0171/14.2975V (min/typ/max, reference-tolerance-only) or 13.4881V (full-stack worst case, reference+resistor both adverse) — all above 13.0V, all below a 4S pack's 14.8V nominal (3.4–3.75% clearance, flagged as a residual margin nuance, `bench-imu-01-design.md` §16 item 28). UVLO trips at 8.1721/8.3388/8.5056V (min/typ/max) or 8.6527V (full-stack worst case) — all below 9.0V. Was `bench-imu-01-design.md` §16 item 22 (RESOLVED this revision) |

The existing 3V3 margins still comfortably confirm the Component Engineer's
own pre-design expectation in `bom/component-selection.md` ("MCU+IMU are only
~10-15mA combined") — the full logic load including LED, I2C pull-ups,
R10, and new Rev 5 R11 (≈19.83 mA worst-case) is still an order of
magnitude below either ceiling.

For Rev 3, **the motor rail was finalized as a connector/topology choice**:
J4 (Same Sky PJ-102AH) is the selected connector, rated 24V/5.0A
(DS-CONN-005) — far in excess of this design's real need. REQ-109's
separate-tracking requirement is satisfied (the motor rail is never folded
into REQ-103's 3V3 budget above). **Rev 4 (Cycle 3 rework) sharpened this
further**: the one item Rev 3 had left as a "recommendation" — the source
class plugged into J4 — became a **binding 9.0–13.0V envelope, 3S-only**
(ISS-014/ISS-019), not a soft preference; 2S is confirmed non-viable at
its typical corner, not just a rare worst case (see the Rail Margin
Summary row above). The exact **field DC source** (battery pack, bench
supply, or adapter) plugged into J4 remains an operational choice outside
this schematic's own parts list, the same way J1's upstream USB host is
external to this design — but it must fall within the stated envelope.
F1 (a PTC fuse) bounds fault-current magnitude/duration upstream of
D2/D3. **Rev 4 flagged that no continuous/steady-state OVP existed to
actively enforce the 13.0V upper bound — Rev 5 closes this gap**: new
U6 (TPS26631PWPR) adds a continuous OVP/UVLO lockout referenced to this
same 9.0–13.0V envelope via its own resistor divider, in addition to
providing the load-switch function itself (series pass element,
controlled by PA9/SHDN, default-OFF/fail-safe per REQ-403). See the
Rail Margin Summary row above and `bench-imu-01-design.md` §7.5.9/
§7.5.10/§16 (item 22, RESOLVED this revision).

## Thermal cross-check (LDO, U3)

Reusing the thermal-margin numbers already computed in
`bom/component-selection.md`'s Power Regulator section (not recomputed
here — same part, same board-level assumptions): at a conservative
worst-case 300 mA load (REQ-103's own ceiling, ~15× this design's actual
≈19.83 mA draw, Rev 5 figure including R10+R11) and 40 °C ambient, estimated
TJ ≈71 °C against a 150 °C TJ,max — ≈79 °C headroom. Since this design's
real 3V3 load (≈19.83 mA worst-case) is far below the 300 mA figure that
thermal estimate already used, actual junction heating in this design is
lower still than the already-comfortable ~71 °C estimate (power
dissipation in a linear LDO scales with output current at fixed
Vin−Vout, so ≈19.83 mA of load dissipates roughly 1/15th the power of the
300 mA case). No thermal risk.

## Thermal cross-check (motor driver, U5) — added Rev 4

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

## Thermal cross-check (supervisory eFuse controller, U6) — new Rev 5

U6 (TI TPS26631PWPR, HTSSOP-20/PWP) has RθJA = 32.2°C/W specifically for
the PWP package column (DS-PROT-031), against a 125°C junction-temperature
Recommended Operating Condition ceiling and a 150°C Absolute Maximum
Rating (both DS-PROT-031). Conduction dissipation at this design's
current levels, using R(ON)=26/30.44/34.5 mΩ (25°C row) to 33–45 mΩ
(85°C row, the conservative corner):

| Current | P = I²·R(ON), 25°C row (min/typ/max R(ON)) | P = I²·R(ON), 85°C row (min/max R(ON), conservative) |
|---|---|---|
| ≈1.05A nominal | 0.029/0.034/0.038 W | 0.036/0.050 W |
| ≤3A absolute worst-case | 0.234/0.274/0.310 W | 0.297/0.405 W |

Using the conservative 85°C-row/worst-case-current corner (0.405W) and
RθJA=32.2°C/W: ΔTJ ≈ 0.405 × 32.2 ≈ 13.0°C above ambient. At REQ-201's
40°C ambient design target, TJ ≈ 53°C — comfortable margin: ≈72°C below
the 125°C ROC ceiling, ≈97°C below the 150°C AMR, ≈112°C below the 165°C
typical Thermal Shutdown threshold (T(TSD), DS-PROT-031). U6's own IQ
(≤1.7mA max, DS-PROT-031) and OVP/UVLO divider bias current (≤12.55µA,
DS-PROT-026) contribute negligible additional self-heating (well under
1.7mA×13V≈22mW combined, over an order of magnitude below the conduction
term above). No thermal risk; PowerPAD soldered directly to the GND
plane per TI's own layout instruction (DS-PROT-023) as the primary
thermal-relief path, consistent with `bench-imu-01-design.md` §7.5.10
and its §15 Rev 5 self-check.

## Notes

- "Margin" should reflect the project's own de-rating policy (e.g. don't
  load a rail past 80% of its rated max) — record the policy here once the
  human sets it; until then treat any rail without explicit margin policy
  as needing human confirmation before Design Complete. For Bench-IMU-01
  this was a moot/low-stakes gap for the original logic rail: margin is
  ≈93.4–96.0% of either ceiling (Rev 5, after R11's small addition — was
  ≈93.5–96.1% pre-Rev 5/post-Rev 4, ≈94.6–96.8% pre-Rev 4), far outside
  any plausible de-rating threshold. The motor rail's margin against its
  own connector (≈40%) and driver OCP threshold (0–25%) are tighter but
  consistent with how TI itself sized the driver's protection
  thresholds — see the Rail Margin Summary above.
- Cross-reference this file's Evidence IDs from
  `requirements/traceability-matrix.md` rows covering power requirements.
- Rev 3 motor subsystem addition: do **not** fold motor current into REQ-103's
  3V3 logic budget. Keep the logic rail and motor rail numerically separate
  per REQ-109 and cross-reference the architecture decision in
  `hardware/power-architecture.md`. **This is now satisfied** — see the
  VM_MOTOR rows above, tracked entirely separately from the 3V3 rows.
- The connector-specific numbers in this file (J4 = Same Sky PJ-102AH,
  24V/5.0A) are final for this revision. **Rev 4 (Cycle 3 rework) added**:
  F1 (originally Littelfuse 30R500U PTC fuse, DS-PROT-006) in series ahead
  of D2/D3, and sharpened the source class from a "recommendation" to a
  **binding 9.0–13.0V envelope, 3S-only**. **Rev 5 adds**: F1's MPN
  swapped to the active **30R500UF** (same electrical/mechanical spec,
  DS-PROT-032/033), and new **U6 (TPS26631PWPR)** inserted between D3 and
  U5 VCC, implementing the load-switch function (default-OFF/fail-safe,
  REQ-403) plus a continuous OVP/UVLO lockout referenced to the same
  9.0–13.0V envelope. If a future revision changes the connector, motor,
  driver, or protection-path part, this file's Supply Capability,
  Subsystem Load, and Rail Margin Summary tables must all be updated
  together, not just one.
- **Rev 4 residual gap — RESOLVED Rev 5**: Rev 4 flagged that no
  continuous/steady-state OVP existed upstream of F1/D3 to actively
  enforce the 9.0–13.0V envelope's upper bound in real time (D3's TVS
  clamp is a transient/surge protector at a much higher 26.0V threshold,
  not a steady-state limiter). **Rev 5's U6 closes this gap**: its own
  OVP/UVLO resistor divider (R12/R13/R14) continuously enforces both the
  9.0V floor and 13.0V ceiling. See the Rail Margin Summary above and
  `bench-imu-01-design.md` §7.5.9/§7.5.10/§16 item 22 (RESOLVED).
- **New Rev 5 residual items** (non-blocking, flagged for Hardware
  Reviewer per `bench-imu-01-design.md` §16 items 27–29): (a) U6's SHDN
  internal pull-up resistance is cited as 1MΩ by this design's own
  datasheet research (Figure 8-1) vs. ≈440kΩ independently found via a
  fresh web search this same engagement — neither is a guaranteed spec,
  and R11's own sizing does not depend on either figure, but the
  discrepancy itself is unresolved; (b) U6's OVP full-stack-worst-case
  trip point (13.4881V) sits only 3.4–3.75% below a 4S pack's 14.8V
  nominal — a real but not urgent margin nuance; (c) U6's own dVdT
  capacitor (C17=22nF) is sized against this design's real C(OUT)=10µF,
  a genuinely different operating point from TI's own worked examples in
  the datasheet (which use C(OUT)=1mF) — flagged to prevent a future
  reviewer from assuming a copy error. None of these three are treated
  as blocking this revision.
