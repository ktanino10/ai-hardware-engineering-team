# stlink-org/stlink — Open Source STM32 Programming Toolset (`st-flash` etc.)

- **Manufacturer**: N/A — this is an independent open-source project
  (`stlink-org`, formerly `texane/stlink`), not published by
  STMicroelectronics, but purpose-built to program/debug ST's own STM32/
  STM8 silicon over SWD/JTAG. Packaged for macOS via Homebrew
  (`brew install stlink`).
- **Part Number / Family**: N/A — this is bring-up **tooling** (the
  `st-flash`/`st-info`/`st-trace`/`st-util` CLI utilities), not a
  Bench-IMU-01 BOM component. Used here specifically for its STM32G031K8T6
  (STM32G0 family) target support.
- **Datasheet Title**: N/A — GitHub repository documentation:
  `doc/supported_devices.md` (MCU family support table) and
  `doc/tutorial.md` (CLI option reference)
- **Revision / Version**: `testing` branch (both files fetched live this
  session via `web_fetch`, full raw content read directly — **HIGH
  confidence, primary-source read**, not a secondary summary). Packaged
  release actually installable via Homebrew: **stable 1.8.0**, confirmed
  bottled for macOS `arm64_sequoia`/`arm64_sonoma`/`sonoma` and
  `x86_64`/`arm64_linux` (fetched directly from Homebrew's own formula API,
  `https://formulae.brew.sh/api/formula/stlink.json`, 2026-09-02 — also a
  direct primary-source read, not a search synthesis).
- **Publication Date**: N/A (continuously-updated open-source repository)
- **Official URL**: https://github.com/stlink-org/stlink (specific files:
  `doc/supported_devices.md`, `doc/tutorial.md`); packaging metadata:
  https://formulae.brew.sh/formula/stlink
- **License**: BSD-3-Clause — open-source **tool** distribution, a
  different regime from this directory's "never commit a datasheet PDF"
  policy (`datasheets/README.md`); no manufacturer datasheet content is
  reproduced here.
- **Retrieved Date**: 2026-09-02
- **Local cache note**: Not cached locally; fetched live this session via
  `web_fetch` (both GitHub doc pages) and the Homebrew formula JSON API.
- **Used for Evidence IDs**: DS-TOOL-005, DS-TOOL-006, DS-TOOL-007

## Why this citation

This is the toolset already named as an illustrative example in this
repository's own pre-existing text (`firmware/bench-imu-01/Makefile`'s
header comment: "Flashing (e.g. via st-flash, OpenOCD, or a debugger's own
GUI)..." and `docs/architecture.md` §5.4/§13's "e.g. `st-flash`, OpenOCD").
This pass replaces that placeholder mention with a directly-verified,
primary-source-read confirmation of real STM32G0 support and exact macOS
installability/CLI syntax.

## What was directly confirmed (primary-source read, not summarized)

- `doc/supported_devices.md`'s own MCU-family table lists
  **`STM32G0 | M0+`** with **no "preliminary/limited" caveat** — unlike the
  table's own entries for STM32U0/STM32L5/STM32H5/STM32U5/STM32C5, which
  are each explicitly flagged "_preliminary, limited and partial support
  only!_". STM32G0 (which includes the STM32G031K8T6, U1) is treated as
  fully, unconditionally supported.
- The same page's own introduction states the toolset "supports several so
  called STLINK programmer boards (**and clones thereof**) which use a
  microcontroller chip to translate commands from USB to JTAG/SWD... On the
  user level there is no difference in handling or operation between these
  different revisions" — direct textual support for recommending a
  compatible ST-LINK/V2-style clone programmer as a real, working option,
  not merely an assumption.
- `doc/tutorial.md`'s own CLI option table confirms: `st-flash write
  in.bin 0x8000000` (raw binary write, available since v1.4.0);
  `--format ihex` to read/write Intel HEX files directly without manually
  specifying a flash address (available since v1.3.0); `--reset` to trigger
  a reset after flashing, where "a software reset (via `AIRCR`; since
  v1.5.1) is used, if the hardware reset failed (`NRST` pin...)" — directly
  relevant because this design's own J3 header has **no NRST pin**
  (`hardware/schematic/bench-imu-01-design.md` §4.4), so `st-flash` is
  expected to fall back to its software/AIRCR reset path automatically, a
  capability present since v1.5.1 — far below the Homebrew-packaged v1.8.0.
