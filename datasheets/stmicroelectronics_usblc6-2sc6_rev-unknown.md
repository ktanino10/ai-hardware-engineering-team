# STMicroelectronics USBLC6-2SC6 Datasheet — Rev UNKNOWN

- **Manufacturer**: STMicroelectronics
- **Part Number**: USBLC6-2SC6
- **Datasheet Title**: UNKNOWN (exact printed cover-page title not independently re-confirmed against the raw PDF this session). Functional description: "Very low capacitance double rail-to-rail ESD protection" TVS diode array in SOT-23-6, marketed for USB 2.0 D+/D- line protection.
- **Revision / Version**: UNKNOWN (not confirmed this session)
- **Publication Date**: UNKNOWN (not confirmed this session)
- **Official URL**: https://www.st.com/resource/en/datasheet/usblc6-2sc6.pdf (manufacturer-hosted datasheet PDF, surfaced directly in this session's research)
- **Retrieved Date**: 2026-08-31
- **Local cache note**: not committed; content verified via live web search this session (part identity, key electrical specs, and pinout/topology each cross-checked across ≥2 independent sources — components101.com, speed-up.ai schematic/layout guide, and the manufacturer's own datasheet URL surfaced by search).
- **Used for Evidence IDs**: DS-PROT-001, DS-PROT-002, DS-PROT-003 (added by the Hardware Lead during Design Complete Gate traceability closeout, 2026-09-03 — confirms −40 to +125 °C junction operating temperature range against REQ-201)

## Why this part

Selected as the real, well-documented, commonly-used USB ESD-protection
device for the Bench-IMU-01 USB port (REQ-402), per the Circuit Engineer's
design task framing — one of the three named example families (ON Semi
NUP2105L / TI TPD2E009 / STMicro USBLC6-2SC6). Not run through a full
≥3-candidate Component Selection comparison (per task instruction, a single
real, datasheet-grounded part is sufficient for this supporting/protection
role). See `hardware/schematic/bench-imu-01-design.md` §3 (Power block) for
the applied wiring (VBUS/GND channel only; D+/D- channel pins left
unpopulated since REQ-105 carries USB power only, no data).
