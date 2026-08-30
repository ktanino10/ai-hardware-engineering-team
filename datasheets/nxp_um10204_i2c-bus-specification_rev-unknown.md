# NXP UM10204 — I2C-bus Specification and User Manual — Rev UNKNOWN

- **Manufacturer**: NXP Semiconductors (original Philips I2C-bus specification, now maintained/published by NXP)
- **Part Number**: N/A — this is an interface/protocol standard document, not a component part number
- **Datasheet Title**: "I2C-bus specification and user manual" (UM10204)
- **Revision / Version**: UNKNOWN (specific UM10204 revision number not independently confirmed this session)
- **Publication Date**: UNKNOWN (not confirmed this session)
- **Official URL**: https://www.nxp.com/docs/en/user-guide/UM10204.pdf (NXP's own hosted copy, surfaced by this session's search)
- **Retrieved Date**: 2026-08-31
- **Local cache note**: not committed; content (pull-up sizing formula and Fast-mode timing/current parameters) verified via live web search this session
- **Used for Evidence IDs**: DS-IFACE-001

## Why this citation

This is the industry-standard reference for I2C bus electrical timing,
used to size the SCL/SDA pull-up resistors for the BMI270 IMU interface in
`hardware/schematic/bench-imu-01-design.md` §4 (IMU Interface block) — not
a fact from either the STM32G031K8T6 or BMI270 datasheet directly (both
datasheets state their *own* I2C peripheral's max clock speed and pin
current capability, DS-MCU-017 / DS-IMU-007, but neither restates the
bus-level pull-up-sizing formula itself; that lives in the I2C-bus
specification, not in either device's own datasheet).

New Evidence category `DS-IFACE` introduced this session (alongside
`DS-PROT` and `DS-CONN`) for interface/protocol-standard citations that
don't belong to a single component's own datasheet — extending the
category list already anticipated as open-ended by `docs/architecture.md`
§6.3 ("`MCU`, `IMU`, `PWR`, `CONN`, `SNS`, `MTR`, …").
