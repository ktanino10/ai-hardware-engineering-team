# Bring-up / First Power-On Procedure

Standardizes first-power-on so it isn't improvised each time. This is the
concrete artifact behind the "before first power-on of real hardware"
Human-in-the-loop gate (`docs/architecture.md` §10). MVP: Hardware Lead +
human execute this jointly. A future **Test Engineer** role
(`docs/architecture.md` §14) formally owns this once bring-up moves beyond
a one-off MVP bench test.

**Human sign-off is required before applying power. Do not skip to power-on
because the schematic/PCB "looks done".**

## 1. Pre-Power-On Checklist

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
