---
description: 'Firmware bring-up artifacts require schematic pin/interface traceability, Evidence-ID-grounded register-level facts, explicit tooling/compilation-status honesty, and no scope creep into control-loop/sensor-fusion territory.'
applyTo: 'firmware/**'
---

- Every pin/peripheral-instance fact (which GPIO, which I2C/SPI/UART
  *instance number*) must trace to the actual schematic design document
  (`hardware/schematic/<board>-design.md`) -- never re-derived, assumed, or
  copied from a task description without checking it against the real
  schematic first.
- Every register-level numeric claim (base address, clock-enable bit
  position, alternate-function value, timing-register preset) must cite an
  Evidence ID (`DS-<CATEGORY>-<NNN>`, `datasheets/evidence-log.md`), reusing
  the existing category for that component (e.g. `DS-MCU-`, `DS-IMU-`) --
  not a bare, uncited claim, and not a new "firmware" evidence category.
- If a design's IMU/sensor bus is a specific peripheral instance (e.g. I2C2,
  not I2C1), firmware code must target that exact instance's real register
  base address -- getting this wrong reproduces, at the firmware layer, the
  exact class of defect an independent schematic review is meant to catch.
- Do not claim compilation, flashing, or hardware validation that wasn't
  actually verified this session (`docs/architecture.md` Section 5.4). State
  plainly whether firmware was compiled (with which toolchain/version) or is
  source-complete-but-uncompiled -- never imply more than what was actually
  exercised.
- Manufacturer-mandated initialization sequences (register pokes in a
  specific order, settle-time delays, opaque configuration-blob uploads)
  must follow the manufacturer's own documented sequence exactly. Opaque
  calibration/microcode data that cannot be derived must be vendored
  verbatim from the manufacturer's own official, permissively-licensed
  driver source, with full attribution (source, version, license) in its
  own clearly-labeled file -- never approximated or interpolated. This is a
  different regime from `datasheets/README.md`'s "never commit a datasheet
  PDF" rule, which governs copyrighted manufacturer PDF documents, not
  redistributable open-source driver code.
- No USB device/data-stack code, and no wireless code, where the
  requirements exclude them -- check the actual requirement text, not an
  assumption about what the selected MCU's silicon could technically do.
- No control-loop, PID, sensor-fusion, calibration, or physical-unit-
  conversion code -- that scope belongs to a future Control Engineer role
  (`docs/architecture.md` Section 14) whose trigger ("1-axis/3-axis
  attitude-control roadmap stage") is not met by a bring-up task. Raw
  register counts are a complete, legitimate deliverable on their own.
  The approved simulation-only controller belongs under `simulation/`
  (`docs/simulation.md`), not here; it grants no deployable-control scope.
- Do not silently reinterpret a requirement to match the actual schematic
  wiring, or vice versa, when they disagree (e.g. a "manual reset button"
  requirement that turns out to be wired to a hardware reset pin rather
  than a GPIO). Implement against the real schematic and document the
  discrepancy.
- No independent Firmware Reviewer agent exists yet
  (`docs/architecture-evolution.md` Section 32) -- self-check against
  `.github/skills/firmware-bringup/SKILL.md`'s checklist is mandatory and
  stands in for independent review; do not skip it or treat it as a
  formality.
- Any non-cosmetic change under `firmware/**` needs a
  `validation/change-log.md` (ECO) entry if it changes something already
  reviewed/handed off, same rule as `hardware/**`/`bom/**`
  (`.github/instructions/hardware-design.instructions.md`).
