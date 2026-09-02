# STMicroelectronics STLINK-V3MINI — User Manual (UM2502)

- **Manufacturer**: STMicroelectronics
- **Part Number**: STLINK-V3MINI (tiny-probe in-circuit debugger/programmer
  tool — bring-up/production **tooling**, not a Bench-IMU-01 BOM component)
- **Datasheet Title**: UM2502 "STLINK-V3MODS and STLINK-V3MINI mini
  debuggers/programmers for STM32 microcontrollers"
- **Revision / Version**: UNKNOWN (not independently re-confirmed this
  session against the primary PDF)
- **Publication Date**: UNKNOWN (not confirmed this session)
- **Official URL**: https://www.st.com/resource/en/user_manual/um2502-stlink-v3mods-and-stlink-v3mini-debuggerprogrammer-tiny-probes-for-stm32-microcontrollers-stmicroelectronics.pdf
  (product page: https://www.st.com/en/development-tools/stlink-v3mini.html)
- **Retrieved Date**: 2026-09-02
- **Local cache note**: Not cached locally. A direct `web_fetch` of the ST
  data-brief PDF timed out this session (`TimeoutError`); this citation is
  based on a web-search synthesis that quotes UM2502's own STDC14 connector
  pinout table (pins 13/14 = VCP_RX/VCP_TX) and cross-references an ST
  Community forum post independently describing the same STDC14
  VCP-UART-bridge pin assignment. **MODERATE-HIGH confidence** — not a
  direct primary-PDF fetch this session.
- **Used for Evidence IDs**: DS-TOOL-003, DS-TOOL-004

## Why this citation

STLINK-V3MINI is STMicroelectronics' own newer, genuine, in-circuit
debugger/programmer — notably **cheaper than the older ST-LINK/V2**
(DS-TOOL-002 vs. DS-TOOL-004 pricing) and adds a Virtual COM Port (VCP)
UART bridge on the same USB connection, which could in principle stand in
for a separate USB-UART adapter on Bench-IMU-01's J2 header. Cited here to
support both its official STM32 compatibility claim and the practical
caveat that its own debug connector (STDC14, 14-pin/0.05" pitch) does not
directly mate with this design's 2.54mm-pitch J3 header without an
adapter cable or hand-wiring — a real trade-off disclosed in
`validation/bring-up-procedure.md` §0a rather than glossed over.
