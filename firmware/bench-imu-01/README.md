# Bench-IMU-01 Firmware

Driver-level bring-up firmware for the Bench-IMU-01 board
(`hardware/schematic/bench-imu-01-design.md`, Design Complete through Rev 5).
Full design rationale and Evidence ID citations for every decision:
[`bench-imu-01-firmware-design.md`](bench-imu-01-firmware-design.md).

This firmware now covers two independent subsystems on the same board:

## 1. IMU sensor bring-up (pre-existing, this pass fixes a critical pin defect)

- Initializes I2C2 — **PA11 (SCL) / PA12 (SDA)**, corrected this pass from
  the previous, now-confirmed-wrong PB10/PB11 (those pins do not physically
  exist on this part's actual LQFP-32 package — see
  `validation/open-issues.md` ISS-027, and §3 of the design doc for the
  full fix, now corroborated against three independent official ST sources:
  the CMSIS pin database, STM32CubeG0's NUCLEO-G031K8 I2C2 example, and the
  `stm32g0xx-hal-driver` header's `GPIO_AF6_I2C2` macro). Same I2C2
  peripheral instance, same AF6, same 400 kHz Fast-mode timing — only the
  GPIO port/pin changed.
- Brings up the BMI270 IMU (address 0x68) with its full manufacturer-mandated
  initialization sequence, including the vendored ~8 KB configuration blob.
- Reads accelerometer + gyroscope raw register counts at 100 Hz (REQ-001)
  and forwards them as CSV lines (`millis,ax,ay,az,gx,gy,gz`) over USART2
  (PA2/PA3, 115200 8N1) to the UART header (REQ-106).
- Reports the MCU's last reset cause once at boot, decoded from `RCC_CSR`.

## 2. Motor Driver + Reaction Wheel open-loop bring-up (new this pass)

Open-loop bench characterization for the Rev 3 Motor Driver subsystem (U5
DRV10983 + M1 T-Motor MN2206-13 + U6 TPS26631PWPR) — **not** a closed-loop
controller. Lets a bench operator command a PWM speed setpoint and observe
the actual measured RPM over the same UART link.

- **PA8** (TIM1_CH1 PWM, 20 kHz) → U5 SPEED. **PA6** (TIM3_CH1 input
  capture, interrupt-driven) → U5 FG tachometer, via R6. **PB1** → U5 DIR.
  **PB6/PB7** (I2C1) → U5's own commissioning/status interface. **PA9** →
  U6 SHDN (motor-rail enable; default OFF via R11's pulldown).
- **Host command grammar** (one ASCII line per command over the same
  USART2 link, any of `\r`/`\n`/`\r\n`/`\n\r` as terminator):
  - `SPD <0-100>` — set PWM duty % (rejected unless armed)
  - `DIR <0|1>` — set direction, 0=forward/1=reverse (rejected unless armed
    and duty is currently 0)
  - `STOP` — zero duty immediately (always allowed; does not disarm)
  - `REARM` — (re-)arm: power-cycle U6's SHDN, re-commission U5 over I2C1,
    clear all latched faults. **Required before the very first `SPD`
    command, and after any REQ-405/406 trip** — the motor never
    auto-resumes on its own.
- **CSV telemetry**, 5 Hz, tagged distinctly from the IMU's own untagged
  lines: `MOTOR,millis_ms,armed,fault_latched,duty_pct,dir_reverse,fg_valid,rpm,mtrlck,lock_event_count`
- **REQ-405 (overspeed shutdown)**: a latched trip (SPEED→0 and U6 SHDN→low)
  if measured RPM (via FG) exceeds **6000 RPM** — 2.0x margin above REQ-007's
  >=3000 RPM floor, 3.33-3.7x margin below the motor's ~20,000-22,200 RPM
  no-load speed. Runs continuously while armed, including during coast-down
  after a plain `STOP`. See the design doc §4.3 for the full derivation,
  including a disclosed revision from an initial 8000 RPM draft.
- **REQ-406 (latched lock-fault policy)**: 3 consecutive Lock-Detection
  events within a rolling 30 s window (read via U5's I2C1 status interface)
  → latched trip → deliberate `REARM` required, never auto-resumes. See
  design doc §4.4.
- **BEMF/FG caveat (ECO-008)**: reported RPM may look noisier, and
  Lock-Detection may nuisance-trip more easily, while transiting roughly
  500-1500 RPM (BEMF-sensing degrades in that band on this part) — an
  expected DRV10983 characteristic, disclosed via the boot banner, not a
  firmware defect and not masked by any filtering. See design doc §4.6 for
  this caveat and the separate, narrower ~103 RPM open/closed-loop
  commutation transition, kept distinct.

## What it deliberately does not do

No USB data/enumeration (REQ-105), no wireless (REQ-006), no PID/attitude
control/sensor fusion/physical-unit conversion, and — specific to this
pass's own hard scope fence — **no code path that reads the IMU and reacts
by driving the motor, or vice versa**. The two subsystems share only this
MCU, this UART link, and the main superloop; REQ-405/406 are bounded safety
cutoffs (comparable to an overcurrent shutdown), not control loops. See the
Firmware Engineer agent profile's "Out of scope" and the design doc §10
(self-check item 7) for how this was verified by inspection.

## Tooling honesty — re-verified this session

- **No physical Bench-IMU-01 board exists in this environment.** This is a
  source-code exercise, like the Mechanical Lead's CAD-tool disclosure. No
  claim of "tested," "verified on hardware," or "flashed" is made anywhere
  in this firmware or its documentation.
- **`arm-none-eabi-gcc` 16.2.0 is installed** (Homebrew,
  `brew install arm-none-eabi-gcc`) — re-confirmed present this session, not
  assumed from a prior session.
- PlatformIO and STM32CubeIDE/STM32CubeMX were checked again this session
  and remain **not** installed.
- **A real, full build was attempted this session and succeeded**: `make`
  in this directory produces `build/bench-imu-01.elf`/`.bin`/`.hex` with
  `arm-none-eabi-gcc 16.2.0`, **zero warnings under `-Wall -Wextra`**,
  covering both the pre-existing IMU firmware and every new motor-subsystem
  file added this pass. Final image: **14,752 bytes** `.text`/`.rodata`,
  **108 bytes** `.bss`, 0 bytes `.data` — comfortably within the part's
  64 KB flash / 8 KB RAM.
- The linked binary's interrupt vector table was additionally disassembled
  and cross-checked to confirm `TIM3_IRQHandler` (feeding the safety-critical
  FG/RPM measurement path) is correctly wired at the expected vector slot —
  empirical evidence from the actual compiled binary, not just a source
  read-through. See design doc §9.
- Flashing (via `st-flash`/OpenOCD/a debugger) remains outside this
  repository's tooling today (`docs/architecture.md` §13) and was not
  attempted.

## Building (if you have the toolchain)

```sh
brew install arm-none-eabi-gcc   # or your platform's equivalent package
cd firmware/bench-imu-01
make
```
