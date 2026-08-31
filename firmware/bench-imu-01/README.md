# Bench-IMU-01 Firmware

Driver-level bring-up firmware for the Bench-IMU-01 board
(`hardware/schematic/bench-imu-01-design.md`, Rev 2, Design Complete). Full
design rationale, Evidence ID citations, and every decision's "why":
[`bench-imu-01-firmware-design.md`](bench-imu-01-firmware-design.md).

## What it does

- Initializes I2C2 (PB10/PB11, 400 kHz Fast-mode) and brings up the BMI270
  IMU (address 0x68) with its full manufacturer-mandated initialization
  sequence, including the vendored ~8 KB configuration blob.
- Reads accelerometer + gyroscope raw register counts at 100 Hz (REQ-001)
  and forwards them as CSV lines over USART2 (PA2/PA3, 115200 8N1) to the
  UART header (REQ-106).
- Blinks the PA5 status/heartbeat LED at 1 Hz (REQ-003).
- Reports the MCU's last reset cause once at boot, decoded from
  `RCC_CSR` — see the design doc's "REQ-004 reinterpretation" section for
  why this replaces a literal "read the reset button" implementation.

## What it deliberately does not do

No USB data/enumeration (REQ-105), no wireless (REQ-006), no unit
conversion/calibration/filtering/control-loop code (raw LSB counts only —
see the Firmware Engineer agent profile's "Out of scope").

## Tooling honesty — verified this session

- **No physical Bench-IMU-01 board exists in this environment.** This is a
  source-code exercise, like the Mechanical Lead's CAD-tool disclosure. No
  claim of "tested," "verified on hardware," or "flashed" is made anywhere
  in this firmware or its documentation.
- **`arm-none-eabi-gcc` was not pre-installed**, but was confirmed
  installable via Homebrew (`arm-none-eabi-gcc`, a bottled/pre-built
  formula — `brew install arm-none-eabi-gcc`) and was actually installed
  and used this session.
- **A real build was attempted and succeeded**: `make` in this directory
  produces `build/bench-imu-01.elf` / `.bin` / `.hex` with
  `arm-none-eabi-gcc 16.2.0`, **zero warnings under `-Wall -Wextra`**.
  Final image: 10,804 bytes of `.text`/`.rodata` (comfortably within the
  part's 64 KB flash — most of that is the mandatory, non-negotiable 8,192-
  byte BMI270 configuration blob), 4 bytes of `.bss`, 0 bytes of `.data`
  (comfortably within the part's 8 KB RAM).
- **This real build attempt found and fixed a genuine bug**: the initial
  `-nostdlib` link excluded `libgcc`, which supplies software integer-
  divide routines the Cortex-M0+ core needs (it has no hardware divide
  instruction) — the CSV-output code divides/moduluses by 10 to convert
  integers to decimal ASCII. Adding `-lgcc` back to the link fixed it. This
  is exactly the kind of real, unglamorous defect a real compile attempt
  surfaces that a "looks plausible" read-through would not have caught.
- Flashing (via `st-flash`/OpenOCD/a debugger) is not part of this
  repository's tooling today (`docs/architecture.md` §13, Future
  Integration) and was not attempted.

## Building (if you have the toolchain)

```sh
brew install arm-none-eabi-gcc   # or your platform's equivalent package
cd firmware/bench-imu-01
make
```
