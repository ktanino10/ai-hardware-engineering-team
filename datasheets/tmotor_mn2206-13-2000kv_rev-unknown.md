# T-Motor (Nanchang Dajiang Innovation... / T-MOTOR brand) MN2206-13 KV2000 Datasheet — Rev UNKNOWN

- **Manufacturer**: T-Motor (Nanjing Tiger Motor Technology, marketed as
  T-MOTOR / TMOTOR), Navigator Series
- **Part Number**: MN2206-13 KV2000 (12N14P stator/rotor configuration, 2000
  RPM/V winding)
- **Datasheet Title**: No formal PDF datasheet found/published for this SKU
  this session — spec table is presented directly on the manufacturer's own
  product page (not a downloadable document).
- **Revision / Version**: UNKNOWN — product-page spec table, not a
  versioned document
- **Publication Date**: UNKNOWN
- **Official URL**: https://uav-en.tmotor.com/Multirotor/Motors/navigato/
  (manufacturer's own product page, live-fetched this session) —
  cross-verified against 3 independent retailer listings (Graves RC Hobbies,
  GetFPV, RC-Hobby-Store-type resellers) for consistency on KV, voltage
  range, current, and mass figures.
- **Retrieved Date**: 2026-08-31
- **Local cache note**: not committed; content read live via web fetch/search
  this session, not cached to any local disk.
- **Used for Evidence IDs**: DS-MTR-017, DS-MTR-018, DS-MTR-019, DS-MTR-020,
  DS-MTR-021, DS-MTR-022, DS-MTR-023, DS-MTR-024

## Known gaps (honestly flagged, not guessed)

- No manufacturer-published stall torque, stall current, or
  continuous/peak torque-vs-RPM curve exists for this SKU — this is normal
  for hobbyist multirotor motors (they are rated in current/power/KV, not
  torque, since the target application is propeller load, not a geared/
  direct-drive torque load). The torque figure used in this comparison
  (**derived**, K_t = 60/(2*pi*KV) = 4.77 mN*m/A) is this project's own
  arithmetic from the published KV constant, not a manufacturer-stated
  number — flagged as "derived" everywhere it is used, never presented as a
  direct datasheet figure.
- No single maximum terminal voltage is published; the part is rated by
  LiPo cell-count range (2S-3S) rather than an absolute voltage ceiling.
  This project's recommended ~12V operating rail (driven by the paired
  driver IC's 8V minimum, not by this motor) sits within the "3S full
  charge" (~12.6V) range this motor is designed for.
- This is the **recommended candidate** — see
  `bom/component-selection.md` "Motor (Reaction Wheel Drive)" section for
  full rationale (budget fit, mass, direct reaction-wheel/CubeSat project
  heritage, torque margin).
