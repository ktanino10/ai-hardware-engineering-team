# Oriental Motor — "Basics of Stepper Motors" (technical reference article) — Rev UNKNOWN

- **Manufacturer**: Oriental Motor U.S.A. Corp. (technical reference /
  application-note-style article, not a specific part's datasheet — cited
  the same way `datasheets/nxp_um10204_i2c-bus-specification_rev-unknown.md`
  is cited for a protocol specification rather than a single IC)
- **Part Number**: N/A — general stepper-motor physics/technology reference,
  not tied to one SKU
- **Datasheet Title**: "Basics of Stepper Motors" (Oriental Motor's own
  technical library article; exact page title as browsed this session)
- **Revision / Version**: UNKNOWN (web article, not a versioned document)
- **Publication Date**: UNKNOWN
- **Official URL**: Oriental Motor technical library (orientalmotor.com
  "Basics of Stepper Motors" article) — reached via web search this session;
  corroborated by a second, independent secondary source, a Linear Motion
  Tips article discussing stepper motor torque-speed curve characteristics
  and winding electrical time-constant effects at high step rates (both
  sources agree on the underlying mechanism: winding inductance limits
  current rise time at high step rates, reducing available torque well
  below the low-speed/holding-torque figure)
- **Retrieved Date**: 2026-08-31
- **Local cache note**: not committed; content read via web search this
  session, not cached to any local disk.
- **Used for Evidence IDs**: DS-MTR-030, DS-MTR-031

## Why this reference matters here

Used to support this session's own **derived** (not manufacturer-published)
estimate that the SOYO SY28STH32-0674A stepper candidate's continuous torque
at the 3000 RPM / 10 kHz commanded step-rate operating point is materially
below its 3.8V-rated holding torque, because the winding's L/R electrical
time constant (0.75 ms, from the motor's own datasheet-cited resistance/
inductance, see `datasheets/soyo_sy28sth32-0674a_rev-unknown.md`) is ~7.5x
longer than the 0.10 ms step period at that speed — current, and therefore
torque, cannot fully develop between steps. This is general stepper-motor
electromagnetics, not a claim about this specific SKU's own tested
performance (no per-SKU torque-speed curve was published/found) — flagged as
a derived estimate everywhere it is used in `bom/component-selection.md`.
