# firmware/

Driver-level bring-up firmware for boards designed in `hardware/`, owned by
the **Firmware Engineer** discipline (`.github/agents/firmware-engineer.agent.md`,
`.github/skills/firmware-bringup/SKILL.md`). Introduced per
`docs/architecture.md` §14's trigger ("when firmware work starts in
earnest") once `hardware/schematic/bench-imu-01-design.md` reached Design
Complete — see `docs/architecture-evolution.md` §32 for the addendum
documenting this discipline's introduction.

## Scope

Register-level peripheral initialization and driver bring-up matching a
board's actual schematic pin/interface decisions. **Not** in scope here
(see the agent profile's "Out of scope" for the full list and reasoning):
control loops, PID, sensor fusion, calibration/physical-unit conversion
(Control Engineer's future territory, `docs/architecture.md` §14 — not yet
triggered), USB device/data firmware or wireless where requirements exclude
them.

## Directory layout

```
firmware/
  README.md                                This file
  <board>/
    README.md                               Board-specific build/tooling-status summary
    <board>-firmware-design.md               Design rationale doc (Evidence-ID-cited,
                                              mirrors hardware/schematic/<board>-design.md's style)
    Makefile
    linker/<part>_FLASH.ld
    src/*.c, *.h
```

One subdirectory per board, named after that board's schematic (e.g.
`bench-imu-01/` for `hardware/schematic/bench-imu-01-design.md`) — mirrors
how `hardware/mechanical/` names its own artifacts per board.

## Tooling honesty (repository-wide statement for this discipline)

Verified each session, not assumed carried-over from a prior one
(`docs/architecture.md` §5.4): whether an ARM embedded toolchain
(`arm-none-eabi-gcc`), PlatformIO, or a vendor IDE (STM32CubeIDE/CubeMX or
equivalent) is installed or installable, and whether a physical board
exists to flash/power on. Each board subdirectory's own `README.md` states
what was actually verified/exercised for that board, this session — never
assume a build or hardware capability without checking first.
