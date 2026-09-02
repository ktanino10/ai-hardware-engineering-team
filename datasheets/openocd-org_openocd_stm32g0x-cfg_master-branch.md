# OpenOCD — `tcl/target/stm32g0x.cfg` (master branch) + Homebrew packaging

- **Manufacturer**: N/A — OpenOCD is an independent open-source project
  (not STMicroelectronics-authored), but this specific target-config script
  is written to interoperate with ST's own STM32G0 silicon over SWD.
  Packaged for macOS via Homebrew (`brew install openocd`, formula alias
  `open-ocd`).
- **Part Number / Family**: N/A — bring-up **tooling** (an OpenOCD target
  configuration script), not a Bench-IMU-01 BOM component. Used here for
  its STM32G0-family target support (covers the STM32G031K8T6, U1).
- **Datasheet Title**: N/A — raw project source file,
  `tcl/target/stm32g0x.cfg`
- **Revision / Version**: `master` branch, fetched live and read in full
  this session via `web_fetch`
  (`raw.githubusercontent.com/openocd-org/openocd/master/tcl/target/stm32g0x.cfg`)
  — **HIGH confidence, direct primary-source read**, not a secondary
  summary. Packaged release actually installable via Homebrew: **stable
  0.12.0**, confirmed bottled for macOS `arm64_tahoe`/`arm64_sequoia`/
  `arm64_sonoma`/`sonoma`/`arm64_ventura`/`ventura`/`arm64_monterey`/
  `monterey`/`arm64_big_sur`/`big_sur` and Linux (fetched directly from
  Homebrew's own formula API,
  `https://formulae.brew.sh/api/formula/open-ocd.json`, 2026-09-02 — also a
  direct primary-source read).
- **Publication Date**: N/A (continuously-updated open-source repository)
- **Official URL**: https://openocd.org/ ;
  https://github.com/openocd-org/openocd (specific file:
  `tcl/target/stm32g0x.cfg`); packaging metadata:
  https://formulae.brew.sh/formula/openocd
- **License**: GPL-2.0-or-later — open-source **tool** distribution, a
  different regime from this directory's "never commit a datasheet PDF"
  policy (`datasheets/README.md`); no manufacturer datasheet content is
  reproduced here.
- **Retrieved Date**: 2026-09-02
- **Local cache note**: Not cached locally; fetched live this session via
  `web_fetch` (the raw `.cfg` file) and the Homebrew formula JSON API.
- **Used for Evidence IDs**: DS-TOOL-009, DS-TOOL-010

## Why this citation

OpenOCD is cited in `validation/bring-up-procedure.md` §0a as the
third flashing-software alternative (alongside `st-flash` and
STM32CubeProgrammer), notable because it additionally provides a live GDB
server for interactive debugging (not just one-shot flashing) using the
same ST-LINK/compatible-clone hardware.

## What was directly confirmed (primary-source read, not summarized)

The actual, current `tcl/target/stm32g0x.cfg` file, in full:

- Declares `transport select swd` with the comment "stm32g0 devices support
  SWD transports only" — an explicit, unambiguous STM32G0-family target
  script (not a generic/guessed config).
- Sets `set _CPUTAPID 0x0bc11477` with the comment "Section 37.5.5 —
  corresponds to Cortex-M0+", matching the STM32G031K8T6's own Arm
  Cortex-M0+ core (`hardware/schematic/bench-imu-01-design.md` §1
  approved-part summary, DS-MCU-012–021).
- Configures `reset_config srst_nogate` and, when not using a
  hardware-adapter (HLA) probe, `cortex_m reset_config sysresetreq` — i.e.
  OpenOCD's own mainline config for this exact MCU family already assumes
  a software/core-level reset path may be needed, not only a hardware SRST/
  NRST line. This directly matches Bench-IMU-01's own J3 header, which has
  **no NRST pin** (`hardware/schematic/bench-imu-01-design.md` §4.4) — the
  same practical situation `stlink-org/stlink`'s own AIRCR software-reset
  fallback addresses (DS-TOOL-006).
