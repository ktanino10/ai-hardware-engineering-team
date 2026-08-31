# Bring-up / First Power-On Procedure

Standardizes first-power-on so it isn't improvised each time. This is the
concrete artifact behind the "before first power-on of real hardware"
Human-in-the-loop gate (`docs/architecture.md` §10). MVP: Hardware Lead +
human execute this jointly. A future **Test Engineer** role
(`docs/architecture.md` §14) formally owns this once bring-up moves beyond
a one-off MVP bench test.

**Human sign-off is required before applying power. Do not skip to power-on
because the schematic/PCB "looks done".**

**This procedure is prepared with real, project-specific values for
Bench-IMU-01 (below) for the human's future physical build. Per REQ-502
and this cycle's own paper/document-design scope, it is NOT executed this
session — no physical PCB exists yet to power on.**

## 0. Project-Specific Values — Bench-IMU-01 (Rev 2, Electronics + Mechanical)

Pulled directly from `hardware/power-budget.md`, `bom/component-selection.md`,
and `hardware/schematic/bench-imu-01-design.md` — cite the source file, not
this copy, if a number ever needs re-confirming.

| Item | Value | Source |
|---|---|---|
| Input rail | USB 5V VBUS via J1 (USB-C), nominal 5.0V, tolerate 4.75–5.5V real-world `vSafe5V` range (wider than REQ-101's own 4.75–5.25V — see ISS-002/FMEA-001) | `bench-imu-01-design.md` §3, DS-CONN-001 |
| Regulated rail | Single 3.3V rail (U3, TLV75533PDBVR, fixed-output LDO) | power-budget.md, DS-PWR-001 |
| Expected 3.3V rail current draw | ≈7.0 mA typical, ≈16.2 mA worst-case | power-budget.md §"Rail Margin Summary" |
| REQ-103 system current budget | ≤300 mA @ 3.3V (actual worst-case is ≈94.6% below this ceiling) | power-budget.md |
| LDO rated max output current | 500 mA (actual worst-case draw is ≈96.8% below this) | DS-PWR-003 |
| **Recommended bench-supply current limit for first power-on** | Start at ≈50 mA (≈3x the 16.2 mA worst-case estimate — conservative headroom for measurement error, not the full 300 mA/500 mA ceiling) and raise only after rail voltage confirmed nominal | Hardware Lead's own bring-up-safety judgment, this pass |
| Power sequencing | None required — single 3.3V rail, no sequencing dependency between subsystems (MCU/IMU/LED all share the one rail) | `bench-imu-01-design.md` §2.1 |
| Boot-mode check (do this BEFORE first power-on) | Confirm BOOT0/nBOOT_SEL state matches documented intent (user Flash boot, not System Memory) — see FMEA-002/ISS-006 | `bench-imu-01-design.md` §4.2, DS-MCU-050/051 |
| Polarity-sensitive items to check | U3 LDO orientation (SOT-23-5, pin 1 marking); D1 LED polarity; J1 USB-C VBUS/GND (note: ISS-004/FMEA-005 — no discrete reverse-polarity protection exists, so a miswired cable is NOT caught by the circuit itself; visual/continuity check is the only safeguard against this specific risk) | parts list, ISS-004 |
| Interface to sanity-check | I2C2 on **PA11 (SCL)/PA12 (SDA)** — corrected 2026-09-11 per ISS-027 (was documented as PB10/PB11 through Rev 5/6, but those pins do not physically exist on this LQFP-32 package), 4.7kΩ pull-ups (R3/R4), IMU (U2, BMI270) at its I2C address | `bench-imu-01-design.md` §5, DS-MCU-073 |
| Debug/programming access | SWD via J3 (VDD/SWCLK/GND/SWDIO) | `bench-imu-01-design.md` §4.4, DS-CONN-002 |
| Known accepted residual risk | ISS-002 (LDO ROC margin, ACCEPTED-RISK) — if bench-measuring at a deliberately worst-case ~5.5V input, expect this is a known, human-accepted edge case, not a new finding | `validation/change-log.md` ECO-003 |
| Enclosure fit check (once PCB exists) | Enclosure geometry is fit to `hardware/mechanical-interface.md`'s estimates, not a confirmed real PCB layout (FMEA-007) — verify physical board dimensions/connector positions against the enclosure BEFORE final assembly, not after | `hardware/mechanical-interface.md`, `hardware/mechanical/bench-imu-01-dimensional-spec.md` |

## 0a. Firmware Flashing — Bench-IMU-01 (Phase 2, added — not executed this session)

Driver-level bring-up firmware exists
(`firmware/bench-imu-01/`, design rationale in
`firmware/bench-imu-01/bench-imu-01-firmware-design.md`) and **compiles
cleanly** with `arm-none-eabi-gcc` (verified this session — see that
document's §0/§7). **Nothing in this section has been executed**: there is
no physical Bench-IMU-01 board in this environment to flash, matching this
whole procedure's own "not executed this session" framing (REQ-502). This
section is prepared, like the rest of this file, for the human's future
physical build.

| Item | Value | Source |
|---|---|---|
| Debug/programming access | SWD via J3 (VDD/SWCLK/GND/SWDIO) — same header row already listed above | `bench-imu-01-design.md` §4.4 |
| Flashing tool | Not part of this repository's tooling today (`docs/architecture.md` §13) — use a generic SWD programmer/debugger appropriate for an Arm Cortex-M0+ part (e.g. an ST-LINK or equivalent) with the built `firmware/bench-imu-01/build/bench-imu-01.hex` or `.elf` | `docs/architecture.md` §5.4/§13 |
| Expected first-boot UART output (at 115200 8N1, on the J2 header) | A boot banner, one `RESET_REASON:` line (decoding `RCC_CSR` — expect `POWER_ON` on a first-ever flash, or `NRST_PIN(SW1_or_debugger)` if reset via SWD/reset line), then either `BMI270_INIT_OK` followed by continuous `millis,ax,ay,az,gx,gy,gz` CSV lines at ~100 Hz, or a `BMI270_INIT_FAILED: ...` line if the IMU didn't come up (check I2C2/PA11-PA12 wiring — corrected 2026-09-11, ISS-027; was PB10/PB11 through Rev 5/6 — and the BMI270's solder joints first) | `firmware/bench-imu-01/src/main.c`, `reset_reason.c` |
| Pre-flash checklist addition | Confirm the SWD debugger is configured for a Cortex-M0+ target at the expected VDD (3.3V, from J3's own VDD reference pin) before connecting — same polarity/orientation care as the rest of §1's checklist | `bench-imu-01-design.md` §4.4 |
| Known residual, non-blocking item | The I2C_TIMINGR value used by the firmware (DS-MCU-063) was cross-checked via two independent web-search-derived sources but not directly re-verified against the primary ST AN4235 PDF this session — low-risk for a bench link, worth a direct check before this firmware is considered final | `datasheets/stmicroelectronics_an4235_i2c-timing-configuration-tool.md` |

## 1. Pre-Power-On Checklist

**Rev 3 note**: the rest of this file (§0 values table, §2 sequencing, §3
measurement) is still Rev 2-scoped and has not yet been rewritten for the
Motor Driver + Reaction Wheel subsystem — that full rewrite is tracked
separately as `validation/open-issues.md` ISS-023 (MEDIUM, non-blocking,
planned for the `validation-artifacts-rev3` closeout pass, after Mechanical
Design/Review settle the physical values this file would otherwise cite).
The single item immediately below is a **targeted advance addition**, not
an oversight — it is the specific compensating safeguard a human Chief
Engineer required (2026-09-09, cross-session HITL channel) as the condition
for accepting ISS-020/ISS-021 as ACCEPTED-RISK rather than leaving Rev 3's
hardware/mechanical Design Complete blocked on firmware that hasn't been
written yet. It must remain in force even after the full Rev 3 rewrite
happens — do not let a future rewrite silently drop it.

- [ ] **MOTOR/REACTION-WHEEL SUBSYSTEM (Rev 3) — MANDATORY, DO NOT SKIP OR
      DEFER.** Before any power is ever applied to the U6/motor-rail domain
      (12V J4 input, U6 TPS26631PWPR supervisory switch, U5 DRV10983 driver,
      M1 T-Motor MN2206-13 + flywheel): confirm Firmware Bring-up has
      actually implemented, and the flashed firmware build demonstrably
      enforces, **both** REQ-405 (a bounded maximum operating/fault speed
      with tach-supervised overspeed shutdown — not just the ≥3000 RPM
      floor) **and** REQ-406 (a latched fault response — after a
      fault-retry threshold, force the motor to a safe/stopped state and
      require a deliberate re-arm, rather than relying on U5/U6's own
      auto-recovering protections to loop indefinitely). This is the
      specific, named compensating control for `validation/open-issues.md`
      **ISS-020** (no bounded speed envelope) and **ISS-021** (no latching
      fault behavior) — both dispositioned ACCEPTED-RISK, explicitly
      conditioned on this check, **not** independently resolved by hardware
      alone (see those findings' full rationale, and
      `validation/change-log.md` for the corresponding ECO). Do **not**
      proceed past this line item on the assumption that U5's Lock
      Detection/Thermal Shutdown or U6's current limit is sufficient by
      itself — per ISS-021, all of those mechanisms auto-retry/auto-recover
      by design and do not latch. If REQ-405/406 firmware cannot be
      confirmed present and functioning, **do not energize the motor rail**;
      the rest of this procedure's Rev 2 scope (MCU/IMU/logic rail) may
      still proceed independently.
- [ ] Visual inspection: correct component population and orientation
      (polarized parts, pin-1 orientation)
- [ ] Continuity check: no unintended shorts between rails/ground (per
      `hardware/power-budget.md` rail list)
- [ ] Polarity check on all polarized components (electrolytic caps,
      diodes, connectors)
- [ ] Jumper/strap configuration matches the intended boot/config mode
- [ ] Bench supply set to **current-limited** mode, with a conservative
      limit derived from `hardware/power-budget.md` (start well below the
      expected max draw)
- [ ] Expected voltage rails and tolerances documented (pull straight from
      `hardware/power-budget.md` and the relevant Evidence IDs)
- [ ] ESD precautions in place (strap/mat as appropriate)
- [ ] `requirements/traceability-matrix.md` rows this bring-up is meant to
      verify are identified in advance

## 2. Safe Power-On Sequence

1. Power on with the bench supply's current limit set conservatively.
2. Bring up rails in the order defined by the design's power-sequencing
   requirement (see the Circuit Engineer's design rationale /
   `hardware/power-budget.md`) — do not bring up all rails simultaneously
   if the design specifies a sequence.
3. At each rail, **stop and measure** before proceeding to the next:
   voltage within tolerance? current draw within budget?
4. **Abort criteria** (immediate power off): overcurrent trip, any smell of
   burning, visible smoke, a component becoming hot to the touch
   unexpectedly, or any rail voltage outside tolerance.
5. Only after all rails are confirmed nominal, proceed to functional
   bring-up (e.g. MCU boot, interface communication).

## 3. Bench Measurement Procedure

- Rail voltages at defined test points, vs. `hardware/power-budget.md`
  expected values and tolerance.
- Ripple on each rail (if measurement equipment available).
- Actual current draw per rail vs. budget.
- Thermal check (touch-check or thermal imaging if available) on
  regulators/drivers under load.
- Interface signal sanity: e.g. I2C/SPI waveform/ack check, confirm
  communication with the IMU (or other peripheral) actually establishes.

## 4. Pass/Fail Criteria

- Compare every measurement against `requirements/traceability-matrix.md`
  and the relevant datasheet Recommended Operating Conditions
  (`datasheets/evidence-log.md`), not against "it seems to work".
- Any failure reopens Circuit Design (`docs/workflow.md` Phase 4) — do not
  patch around a bring-up failure on the bench without logging it in
  `validation/open-issues.md` and, if the design changes,
  `validation/change-log.md`.

## 5. Sign-off

| Role | Name | Date | Decision |
|---|---|---|---|
| Hardware Lead | | | |
| Chief Engineer (Human) — required before power-on | | | Pending |
