# JEDEC Package Outline Standards (MS-026, MO-178) — Multi-Revision

- **Manufacturer**: JEDEC Solid State Technology Association (standards body, not a component manufacturer)
- **Part Number**: N/A — these are package *outline family* standards, not a single manufacturer's part
- **Datasheet Title**: JEDEC MS-026 "Plastic Quad Flatpack (LQFP)" and JEDEC MO-178 "Plastic Small Outline Transistor (SOT-23)" package outline standards
- **Revision / Version**: UNKNOWN (specific MS-026/MO-178 revision letter not independently confirmed this session)
- **Publication Date**: UNKNOWN (not confirmed this session)
- **Official URL**: https://www.jedec.org (standards body's own site; specific outline drawings typically mirrored by component manufacturers, e.g. NXP's SOT358-1 page at https://www.nxp.com/packages/SOT358-1 for LQFP32, and Nexperia's SOT8104-1.pdf at https://assets.nexperia.com/documents/package-information/SOT8104-1.pdf for SOT-23-5)
- **Retrieved Date**: 2026-08-31
- **Local cache note**: not committed; content verified via live web search this session, cross-checked across ≥2 independent manufacturer mirror pages per package family (NXP + JCET for LQFP; Nexperia for SOT-23-5)
- **Used for Evidence IDs**: DS-MCU-048 (LQFP-32 body height, ~1.4mm nominal), DS-PWR-046 (SOT-23-5 body height, ~1.1–1.25mm typ/max)

## Why this citation

Used for the board-geometry/mechanical-estimate handoff in
`hardware/schematic/bench-imu-01-design.md` §10 — package *heights* are a
generic outline-family (JEDEC) fact, not something restated in the
STM32G031K8T6 or TLV75533PDBVR electrical datasheets themselves (those
datasheets typically reference the outline drawing by name/number rather
than reprint JEDEC's own dimension table). Real manufacturer packages
following these outlines (the STM32G031K8T6's LQFP-32 and the
TLV75533PDBVR's SOT-23-5/DBV) are expected to match the family's standard
height envelope; this was **not** independently re-verified against each
part's own literal mechanical drawing this session (flagged as a
CONFIRMED-via-standard, not CONFIRMED-via-part-specific-drawing,
distinction in the design document).
