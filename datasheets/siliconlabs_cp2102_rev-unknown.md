# Silicon Labs CP2102/CP2109 — "Single-Chip USB to UART Bridge" Datasheet

- **Manufacturer**: Silicon Laboratories (Silicon Labs)
- **Part Number**: CP2102 (this datasheet covers the CP2102 and its
  successor-family sibling CP2109 together, per Silicon Labs' own combined
  "CP2102/9" document naming)
- **Datasheet Title**: "CP2102/9: Single-Chip USB to UART Bridge" (combined
  datasheet)
- **Revision / Version**: UNKNOWN (not independently re-confirmed this
  session against the primary PDF)
- **Publication Date**: UNKNOWN (not confirmed this session)
- **Official URL**: https://www.silabs.com/documents/public/data-sheets/cp2102-9.pdf
  (product page: https://www.silabs.com/interface/usb-bridges/classic/device.cp2102)
- **Retrieved Date**: 2026-09-02
- **Local cache note**: Not cached locally; not directly fetched this
  session. Citation is based on a web-search synthesis quoting the official
  Silicon Labs product/datasheet URL, cross-corroborated by two independent
  third-party module-vendor manuals (SparkFun's own CP2102 breakout-board
  documentation, and a ShillehTek CP2102 module manual) that both
  independently describe the same jumper-selectable 3.3V/5V VCCIO behavior.
  **MODERATE-HIGH confidence** on the 3.3V/5V-selectable logic-level claim
  (multiply corroborated); this claim is not itself safety- or
  design-critical (it governs a bench debug-adapter setting, not a
  Bench-IMU-01 BOM part) — not a direct primary-PDF fetch this session.
- **Used for Evidence IDs**: DS-TOOL-011

## Why this citation

CP2102-based USB-to-UART modules are recommended in
`validation/bring-up-procedure.md` §0a as the primary USB-serial adapter
option for Bench-IMU-01's J2 header (TX/RX/GND/3V3, fixed 3.3V logic per
`hardware/schematic/bench-imu-01-design.md` §6). The CP2102's own VCCIO pin
is commonly wired on hobbyist breakout modules to a 3.3V/5V selector
jumper — meaning a CP2102 module set to 3.3V matches J2's logic level
directly, with no external level-shifting needed.
