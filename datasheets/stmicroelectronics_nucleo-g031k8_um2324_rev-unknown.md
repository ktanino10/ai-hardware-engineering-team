# STMicroelectronics NUCLEO-G031K8 User Manual (UM2324) — Rev UNKNOWN

- **Manufacturer**: STMicroelectronics
- **Part Number**: NUCLEO-G031K8 (evaluation board; reference document, not a component used in this design)
- **Datasheet Title**: UM2324 "STM32 Nucleo-32 boards" (covers the NUCLEO-G031K8 CN4 SWD debug connector pinout, among other Nucleo-32 variants)
- **Revision / Version**: UNKNOWN (not confirmed this session)
- **Publication Date**: UNKNOWN (not confirmed this session)
- **Official URL**: https://www.st.com/resource/en/user_manual/um2324-stm32-nucleo32-boards-mb1455-stmicroelectronics.pdf (per this session's search; cross-checked against SEGGER's "Connecting to STM32 Nucleo boards" wiki page and ST Community posts describing the CN4 connector's 4 pins)
- **Retrieved Date**: 2026-08-31
- **Local cache note**: not committed; content (CN4 SWD header pinout: VDD/SWCLK/GND/SWDIO, no NRST/SWO) verified via live web search this session, cross-checked across ≥2 independent sources (SEGGER wiki, ST Community, stm32-base.org)
- **Used for Evidence IDs**: DS-CONN-002, DS-TOOL-013

## Why this citation

ST's own minimal 4-pin SWD debug-header convention on its Nucleo-32 boards
(same MCU family as this design, STM32G031K8) is the precedent used for
this design's own 4-pin SWD header pinout in
`hardware/schematic/bench-imu-01-design.md` §3 (MCU block) — directly
answers the design task's question of whether a reset line or SWO is
conventionally included on a minimal SWD header (answer: no, per ST's own
reference).

## Addendum (2026-09-02) — standalone ST-LINK re-use, DS-TOOL-013

Re-consulted for the Bench-IMU-01 firmware-flashing tooling guide
(`validation/bring-up-procedure.md` §0a). ST's Nucleo-32 user-manual
convention documents that the onboard ST-LINK part can be de-coupled from
the board's own target MCU (removing/cutting the ST-LINK-to-target
jumpers) and reused standalone via CN4 to program a different, external
target — a legitimate way to obtain a genuine ST-LINK debugger for
Bench-IMU-01 at the NUCLEO-G031K8's own ~$13 price point (DS-MCU-020),
at the cost of extra setup effort (jumper removal, hand-wiring CN4 out to
the external board's own J3) versus a dedicated classic-form-factor
programmer. Not independently re-verified against the primary UM2324 PDF
this session (same confidence caveat already disclosed above for
DS-CONN-002) — corroborated via a web-search synthesis of the same UM2324
content plus community documentation (STM32-base.org, RadioShuttle) of the
same standalone-mode procedure on other Nucleo-32 boards.
