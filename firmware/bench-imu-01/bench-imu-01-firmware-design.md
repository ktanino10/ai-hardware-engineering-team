# Bench-IMU-01 — Firmware Bring-up Design Document

**Author**: Firmware Engineer (AI agent) · **Date**: 2026-08-31, corrected
2026-09-08 (ISS-014 firmware follow-up) · **Status**: Source-complete,
self-checked, compiles cleanly with `arm-none-eabi-gcc` 16.2.0 (re-verified
this session) — not run on real hardware (none exists in this environment).
Mirrors the evidence-citation and rationale discipline of
`hardware/schematic/bench-imu-01-design.md`, adapted for firmware.

## Changelog — 2026-09-08 correction (ISS-014 firmware follow-up)

This board's schematic (`hardware/schematic/bench-imu-01-design.md`) was
corrected on 2026-08-31 (ECO-006) when independent research found that the
STM32G031K8T6's real LQFP-32 package has **no PB10/PB11 pins at all** — the
IMU's I2C2 bus, as this firmware originally configured it (PR #7), targeted
a physically nonexistent pin pair. That schematic fix reassigned the bus to
the real, physically-existing **PA11 (I2C2_SCL, physical pin 22) / PA12
(I2C2_SDA, physical pin 23)**, same I2C2 peripheral instance, and was
explicitly flagged at the time as a firmware follow-up not yet performed
(`validation/open-issues.md` ISS-014 Notes; `validation/change-log.md`
ECO-006's own "Not fixed by this ECO" disclosure).

This revision performs that follow-up fix:

- Independently re-verified the pin/AF mapping from primary sources before
  touching any code (not merely trusting the schematic's own citation, and
  explicitly not trusting an unverified claim of a prior Evidence ID
  "DS-MCU-068" that turned out **not to actually exist** in
  `datasheets/evidence-log.md` before this session — a good illustration of
  why this repository's independence discipline requires re-deriving facts
  rather than trusting a secondhand citation):
  1. Re-fetched ST's own official pin database
     (`STMicroelectronics/STM32_open_pin_data`,
     `mcu/STM32G031K(4-6-8)Tx.xml`, the same primary source DS-MCU-067
     already cites) directly this session and confirmed `<Pin Position="22">`
     (name `PA11 [PA9]`, default/unremapped state) carries signal
     `I2C2_SCL`, and `<Pin Position="23">` (`PA12 [PA10]`) carries
     `I2C2_SDA` — corroborating DS-MCU-067 independently, not just
     re-reading it.
  2. That pin database does not itself encode alternate-function *numbers*
     (only which signals are available at each pin), so the AF6 value
     needed a separate primary source. Found and independently verified
     against **two further official STMicroelectronics sources**, both new
     to this repository's evidence trail (DS-MCU-068, DS-MCU-069): (a)
     STMicroelectronics' own `STM32CubeG0` official firmware-example
     repository's CubeMX-generated MSP file for the **NUCLEO-G031K8**
     board — the same exact STM32G031K8T6 part this design uses — which
     configures I2C2 on `GPIOA` pins 11/12 with
     `GPIO_InitStruct.Alternate = GPIO_AF6_I2C2`; (b) STMicroelectronics'
     own `stm32g0xx-hal-driver` header (`Inc/stm32g0xx_hal_gpio_ex.h`),
     which defines `GPIO_AF6_I2C2` as the literal numeric value `0x06`.
     Together these confirm AF6 is correct for PA11/PA12 I2C2 — the same AF
     number the (now-corrected) PB10/PB11 assignment used, but this was
     verified fresh, not assumed to carry over.
- `src/gpio.c`/`src/gpio.h`: GPIO configuration moved from GPIOB pins 10/11
  to **GPIOA pins 11/12**, same AF6, same open-drain configuration (I2C2
  peripheral instance and register base address were already correct and
  unchanged — only the GPIO port/pin/AF-mux target changes).
- `src/clock.c`/`src/clock.h`: `RCC_IOPENR_GPIOBEN` removed from
  `clock_init()` — GPIOB is no longer used anywhere in this board's real
  pin allocation (every pin this firmware configures — PA2, PA3, PA5, PA11,
  PA12 — is now on GPIOA), so enabling its clock would be dead, misleading
  configuration.
- `src/stm32g031_regs.h`: removed the now-unused `GPIOB_BASE`/`GPIOB`/
  `RCC_IOPENR_GPIOBEN` definitions (this header's own stated purpose is "a
  minimal, purpose-built subset ... covering only the peripherals this
  board's schematic actually uses" — keeping a genuinely-unused GPIOB
  definition around would contradict that and risk a future re-introduction
  of this exact defect).
- Rebuilt with `arm-none-eabi-gcc` 16.2.0 this session: succeeds, zero
  warnings under `-Wall -Wextra`, identical image size to before (10,804
  bytes `.text`/`.rodata`, 4 bytes `.bss`, 0 bytes `.data` — a pure pin/port
  relabeling changes no code size). Disassembly spot-check confirms the
  GPIOB base address (`0x50000400`) no longer appears anywhere in the
  linked binary, and every GPIO access in `gpio_init()`/`led_set()`/
  `led_toggle()` now resolves through the single GPIOA base
  (`0x50000000`).
- See `validation/open-issues.md` ISS-014 (Notes) and
  `validation/change-log.md` (new ECO entry) for the formal record.

## 0. Tooling honesty statement

Verified this session, not assumed:

- `arm-none-eabi-gcc` was **not** pre-installed, but **was** confirmed
  installable via a bottled Homebrew formula (`arm-none-eabi-gcc` 16.2.0,
  with its dependency `arm-none-eabi-binutils`) and was installed and used
  this session.
- PlatformIO (`pip3 show platformio`) and STM32CubeIDE/STM32CubeMX were
  checked and are **not** installed in this environment.
- **No physical Bench-IMU-01 board exists in this environment** — this is a
  source-code exercise, the same tooling-honesty convention
  `docs/architecture.md` §5.3 established for the Mechanical Lead's CAD
  tooling, now extended to Firmware (§5.4). No claim of "tested," "verified
  on hardware," or "flashed" is made anywhere in this document or the
  firmware source.
- A real build **was** attempted and **succeeded**: see §7 for the full
  account, including a genuine link error the real build surfaced and this
  session fixed (not a hypothetical — an actual `-lgcc`/software-divide
  linker failure).

This document is therefore the schematic-equivalent artifact for firmware:
a structured, Evidence-ID-cited account of every register-level decision,
sufficient for a future independent reader (or a future Firmware Reviewer,
if that role is ever introduced — see §8) to check this work against
primary sources, the same way the schematic document is written for the
Hardware Reviewer.

## 1. Scope and inputs (not re-litigated)

Per `.github/agents/firmware-engineer.agent.md`, this firmware's scope is
driver-level bring-up only: peripheral initialization and register-level
configuration matching `hardware/schematic/bench-imu-01-design.md` Rev 2
(Design Complete)'s actual pin/interface decisions. Every pin/peripheral
fact below is extracted from that document, not re-derived or assumed —
see the citation next to each one.

| Fact | Value | Schematic source |
|---|---|---|
| MCU | STM32G031K8T6, Cortex-M0+, LQFP-32, 64KB Flash/8KB SRAM | §1 |
| IMU bus | **I2C2** (PA11=SCL, PA12=SDA) — peripheral instance corrected from an original I2C1 mislabeling (ISS-011); GPIO pins corrected again this revision from PB10/PB11, which do not physically exist on this package (ISS-014) | §2.3, §5.2, §5.3, §11 |
| IMU address/mode | I2C address 0x68 (SDO→GND); I2C mode (CSB→VDDIO) | §5.3, DS-IMU-075/076 |
| IMU acquisition | Polled, not interrupt-driven (INT1/INT2 left NC) | §5.3 |
| Host UART | USART2 (PA2=TX, PA3=RX), header J2 | §6 |
| Status LED | PA5, active-high drive via R5 to D1 | §7 |
| "Manual reset button" (REQ-004) | SW1 wired directly NRST→GND, in parallel with the always-populated C5 filter cap — **not** a GPIO | §4.3, confirmed again in `requirements/traceability-matrix.md` REQ-004 row |
| MCU clock | Internal HSI16, no external crystal; exact target frequency deliberately left open by the schematic | §6 |
| BOOT0 | No physical circuit; relies on `nBOOT_SEL=1` factory default | §4.2 |

Explicitly out of scope this cycle (`.github/agents/firmware-engineer.agent.md`
"Out of scope"): USB data/enumeration (REQ-105 — D+/D− unpopulated), any
wireless (REQ-006), and anything Control-Engineer-flavored (control loops,
sensor fusion, physical-unit conversion — `docs/architecture.md` §14's
1-axis/3-axis attitude-control trigger is not met by this bench board).

## 2. Correcting a scope assumption: REQ-004 / SW1 is not a GPIO

The task framing for this firmware cycle assumed the "manual reset button"
(REQ-004) would be a GPIO firmware could read. Re-reading the actual
schematic (§4.3) shows SW1 is wired **directly from NRST to GND**, in
parallel with the always-populated NRST filter capacitor C5 — this is
confirmed a second time in `requirements/traceability-matrix.md`'s own
REQ-004 row ("N.O. pushbutton wired to NRST per ST's recommended NRST
filter circuit"). Pressing SW1 causes a **hardware** MCU reset; there is no
GPIO pin for firmware to poll.

Per `.github/skills/firmware-bringup/SKILL.md`'s own guidance ("if the
schematic and a task description disagree, the schematic wins... implement
against the real schematic and document the discrepancy"), this firmware
does **not** implement a nonexistent GPIO-button read. Instead, it
implements the closest legitimate, firmware-observable behavior actually
tied to REQ-004: at boot, it reads `RCC_CSR`'s reset-reason flags (decoding
`PINRSTF` — NRST pin, i.e. SW1 or a debugger — separately from power-on,
software, and watchdog resets), reports the result over UART, then clears
the flags (`reset_reason.c`). This is a real, standard STM32 technique, not
an invented substitute — see DS-MCU-059.

## 3. Firmware-level decisions (schematic leaves these open; recorded here with rationale)

### 3.1 MCU clock: HSI16, no PLL (16 MHz)

The schematic (§6) fixes "no external crystal, runs off internal
HSI16+PLL" but not an exact target frequency. **Decision: run on the
default HSI16 with no PLL (16 MHz)** — this is the part's power-on-reset
clock state, so it needs zero additional clock-tree register writes (lowest
risk), and it keeps the I2C2/USART2 timing-register constants in this
firmware single-valued rather than a family of them for different
frequencies. Neither REQ-001's 100 Hz ODR floor nor REQ-106's UART link has
a headroom requirement that would need this part's higher clock ceiling
(up to 64 MHz). See `clock.c`.

### 3.2 Host communication framing: 115200 8N1, CSV lines

The schematic (§6) only cites "115200" as an example baud rate the internal
oscillator's tolerance can support, without fixing it. **Decision: 115200
baud, 8 data bits, no parity, 1 stop bit** — the ubiquitous USB-serial-
adapter default, needing no special host-side configuration, and matching
the schematic's own example. **Line format**: `millis,ax,ay,az,gx,gy,gz\r\n`
— ASCII CSV, raw signed 16-bit register counts (not physical units). A
simple, human-readable format was chosen over an invented binary protocol
per `.github/skills/firmware-bringup/SKILL.md` step 7 ("don't over-engineer
this"); raw counts (not g/dps) keeps this firmware inside "driver-level
bring-up" scope rather than creeping into unit-conversion/calibration,
which is Control-Engineer-flavored (§1). See `usart2.c`, `main.c`.

### 3.3 BMI270 initialization: the real, full sequence, including its vendored configuration blob

Independently confirmed this session (Bosch's own official
`BMI270_SensorAPI` driver — see `datasheets/boschsensortec_bmi270_sensorapi_v2.86.1.md`)
that the BMI270 will not produce valid accelerometer/gyroscope data until a
specific, mandatory sequence completes: soft reset → disable advanced power
save → disable config-load flag → upload an **8192-byte manufacturer
configuration blob** in 32-byte, word-addressed chunks → re-enable the
config-load flag → poll `INTERNAL_STATUS` until it reports success (DS-IMU-080
through DS-IMU-083). This is not an optional nicety or a simplification
target — every one of Bosch's own example integrations does this, and
skipping any step leaves the data registers reading zero.

**Decision: implement the real, full sequence, vendoring the 8192-byte
blob verbatim** from Bosch's official driver (BSD-3-Clause — DS-IMU-084,
DS-IMU-088) into its own clearly-attributed file
(`bmi270_config_file.h`), rather than a simplified partial bring-up that
stops at, e.g., a `CHIP_ID` check alone. This is the only way to actually
satisfy REQ-001 ("read accelerometer + gyroscope data") for this
specific part — a `CHIP_ID`-only bring-up would prove the bus works but
not that the sensor produces data. See §4 and §6 for the full detail.

### 3.4 Advanced power save left disabled after initialization

Bosch's own driver typically re-enables "advanced power save" after
configuration load, for battery-powered use cases. **Decision: leave it
disabled** — this is a bench/bring-up context (REQ-201, REQ-502), not a
battery product; REQ-103's 300 mA budget already has ~95% margin without
any IMU-side power optimization (`hardware/power-budget.md`), and a
simpler, always-ready sensor state reduces bring-up-time complexity. This
is a firmware-level, revisable decision, not a hardware constraint.

## 4. Peripheral bring-up detail (register-level facts, all Evidence-ID-cited)

All register base addresses, struct offsets, and bit positions below were
independently confirmed this session directly against STMicroelectronics'
own official CMSIS-Device header for this part family
(`datasheets/stmicroelectronics_cmsis_device_g0_master.md`) — not from
memory, not guessed — with RCC bit positions specifically cross-checked
against a second, independent source. See `firmware/bench-imu-01/src/
stm32g031_regs.h` for the full set of definitions and their inline Evidence
citations.

| Peripheral | Key facts | Evidence |
|---|---|---|
| Memory map | FLASH_BASE=0x08000000 (64K), SRAM_BASE=0x20000000 (8K) | DS-MCU-055 |
| Base addresses | RCC=0x40021000, GPIOA=0x50000000, USART2=0x40004400, **I2C2=0x40005800 (not I2C1=0x40005400)** | DS-MCU-056 |
| GPIO/RCC struct layout | MODER/OTYPER/PUPDR/ODR/BSRR/AFR offsets; RCC IOPENR/APBENR1/CSR offsets | DS-MCU-057 |
| RCC clock-enable bits | GPIOAEN=bit0 (IOPENR; GPIOB is not used by this board's real pin allocation, ISS-014, so its enable bit is deliberately not set); USART2EN=bit17, I2C2EN=bit22, PWREN=bit28 (APBENR1) | DS-MCU-058 |
| RCC reset-reason bits | PINRSTF=bit26, PWRRSTF=bit27, SFTRSTF=bit28, IWDGRSTF=bit29, WWDGRSTF=bit30, RMVF=bit23 (CSR) | DS-MCU-059 |
| I2C register layout/bits | CR1/CR2/ISR offsets and fields (SADD, START, STOP, NBYTES, AUTOEND, TXIS, RXNE, NACKF, STOPF, TC, BUSY) | DS-MCU-060 |
| USART register layout/bits | CR1/ISR/BRR offsets and fields (UE, RE, TE, RXNE, TC, TXE) | DS-MCU-061 |
| GPIO alternate functions | PA2/PA3=AF1 (USART2), **PA11/PA12=AF6 (I2C2)** — corrected this revision from PB10/PB11 (ISS-014); AF6 value independently re-confirmed against two further official ST sources (STM32CubeG0's NUCLEO-G031K8 I2C2 example, `stm32g0xx-hal-driver`'s `GPIO_AF6_I2C2` numeric definition) | DS-MCU-062, DS-MCU-068, DS-MCU-069 |
| I2C timing (400 kHz @ 16 MHz) | TIMINGR=0x00310309 (ST's own published value, AN4235 Table 11) | DS-MCU-063 |

`gpio.c` configures PA11/PA12 **open-drain** (not push-pull) — I2C is a
wired-AND bus, and the schematic already provides the external 4.7 kΩ
pull-ups R3/R4 (§5.2); an internal pull-up or push-pull drive here would
fight the bus. `i2c2.c` implements polling-mode (no interrupts), matching
the schematic's own polled-acquisition decision (§5.3) and the fact that no
I2C2 interrupt is unmasked at the NVIC (`startup_stm32g031xx.c`).

## 5. BMI270 driver detail

All register addresses and the exact chunked-upload protocol below are
sourced from Bosch's own official driver (DS-IMU-078 through DS-IMU-088) —
see `bmi270.c` for the full implementation and inline citations.

1. **Soft reset**: write `0xB6` to `CMD` (0x7E), wait ≥2 ms (DS-IMU-080).
2. **CHIP_ID check**: read register 0x00, expect `0x24` (DS-IMU-079) —
   catches a wrong I2C address/dead bus/miswired part immediately, before
   attempting to upload 8 KB to nothing.
3. **Disable advanced power save**: write `0x00` to `PWR_CONF` (0x7C),
   settle delay (DS-IMU-081).
4. **Disable config-load flag**: write `0x00` to `INIT_CTRL` (0x59).
5. **Upload the configuration blob**: for each 32-byte chunk (256 chunks,
   8192 bytes ÷ 32, no remainder), write the chunk's *word offset*
   (byte index ÷ 2) as two bytes to `INIT_ADDR_0`/`INIT_ADDR_1`
   (0x5B/0x5C), then burst-write the chunk to `INIT_DATA` (0x5E)
   (DS-IMU-082) — this word-addressed, per-chunk-addressed protocol is
   required because the device's internal address pointer does not
   auto-increment across separate I2C transactions.
6. **Finalize**: write `0x01` to `INIT_CTRL`, then poll `INTERNAL_STATUS`
   (0x21) until `(status & 0x0F) == 0x01` (DS-IMU-083), up to a 150 ms
   software timeout (an engineering safety margin, not itself a cited
   datasheet figure).
7. **Configure ODR + enable sensors**: `ACC_CONF` (0x40) = `0xA8`,
   `GYR_CONF` (0x42) = `0xE8` (performance-optimized, normal bandwidth,
   100 Hz ODR — DS-IMU-085), `PWR_CTRL` (0x7D) = `0x06` (accel+gyro enable
   — DS-IMU-086), satisfying REQ-001's ≥100 Hz floor.
8. **Sample read**: a single 12-byte burst read from `ACC_X_LSB` (0x0C)
   returns accel X/Y/Z followed by gyro X/Y/Z — contiguous registers on
   this part (DS-IMU-087), so one I2C transaction per sample.

## 6. Main loop

`main.c`: `clock_init()` → `gpio_init()` → `usart2_init()` →
`systick_init()` → report reset reason (§2) → `i2c2_init()` →
`bmi270_init()` (§5). If BMI270 init fails, the firmware reports which
step failed over UART and blinks the LED fast forever (a deliberately
distinct pattern from the normal 1 Hz heartbeat, so a bench operator can
tell "firmware alive, sensor didn't come up" apart from "board dead")
rather than silently hanging or producing garbage samples. On success, the
main loop polls the BMI270 every 10 ms (100 Hz, satisfying REQ-001) and
emits one CSV line per sample, and toggles the heartbeat LED every 500 ms
(REQ-003).

## 7. Real build attempt (this session)

Original build (2026-08-31): `arm-none-eabi-gcc` was installed via Homebrew
(`brew install arm-none-eabi-gcc`, a bottled/pre-built formula — succeeded,
no compilation-from-source needed) and `make` was run in
`firmware/bench-imu-01/`.

**First attempt failed** with a genuine linker error:
`undefined reference to '__aeabi_uidivmod'`/`'__aeabi_uidiv'` in
`usart2_write_u32`. Root cause: the Cortex-M0+ core has no hardware integer
divide instruction, so the compiler emits calls to software divide routines
normally supplied by `libgcc` — and the Makefile's original `-nostdlib`
linker flag excluded `libgcc` along with the C library. **Fix**: added
`-lgcc` back to the link command (`libgcc` has zero OS/libc dependency of
its own — it is pure compiler-support arithmetic, safe to link even in a
fully freestanding image). This is recorded here deliberately, not
smoothed over: it is exactly the kind of concrete, non-obvious defect a
real build attempt finds that a read-through would not have.

**Second attempt succeeded**: zero warnings under `-Wall -Wextra`. Final
image (`arm-none-eabi-size`): 10,804 bytes `.text`/`.rodata` (of which
8,192 bytes — 76% — is the mandatory BMI270 configuration blob, DS-IMU-084;
the actual driver logic is small), 4 bytes `.bss`
(one `uint32_t` millisecond counter, `systick.c`), 0 bytes `.data`. Both
figures sit comfortably within the STM32G031K8T6's 64 KB flash / 8 KB RAM
(DS-MCU-055). This was **not** flashed to real hardware — none exists in
this environment (§0).

**Re-verified this session (2026-09-08, ISS-014 firmware follow-up)**: ran
`make clean && make` again after the GPIOB→GPIOA/PB10-PB11→PA11-PA12 pin
fix (see Changelog above). Build succeeds again, again zero warnings under
`-Wall -Wextra`, with the **identical** `.text`/`.bss`/`.data` byte counts
as before (10,804/4/0) — expected, since relabeling which GPIO port/pins
are configured changes no instruction count on this architecture. As an
additional, non-cosmetic regression check (not performed in the original
build write-up), `arm-none-eabi-objdump -d` was run against the linked
`.elf` and grepped for the old GPIOB base address: **`0x50000400` (GPIOB)
no longer appears anywhere in the compiled binary**, and every GPIO access
in `gpio_init()`/`led_set()`/`led_toggle()` now resolves through the single
GPIOA base address (`0x50000000`) — direct, compiled-code confirmation
that the fix took effect, not just a source-level read-through. Still
**not** flashed to real hardware — none exists in this environment (§0).

## 8. Self-check against `.github/skills/firmware-bringup/SKILL.md`'s checklist

1. **Pin/peripheral instance fidelity** — I2C2 base address (0x40005800)
   used throughout, verified distinct from I2C1 (0x40005400); PA11/PA12
   AF6 (corrected this revision from PB10/PB11, which do not physically
   exist on this package — ISS-014) confirmed against the part's own pin
   database and cross-confirmed against two further official ST sources
   (STM32CubeG0's NUCLEO-G031K8 I2C2 example, `stm32g0xx-hal-driver`'s
   `GPIO_AF6_I2C2` definition), not assumed by convention or carried over
   from the prior (incorrect) PB10/PB11 citation. ✅
2. **Clock configuration correctness** — HSI16/16 MHz stated and actually
   left unconfigured-from-reset (no PLL registers touched); I2C TIMINGR and
   USART BRR both computed for 16 MHz specifically. ✅
3. **Manufacturer-mandated sequence completeness** — full BMI270 sequence
   implemented per §5, cross-checked against the official driver's own
   `write_config_file`/`bmi2_soft_reset` logic, not a prose summary alone. ✅
4. **Vendored opaque data provenance** — `bmi270_config_file.h` traces to
   Bosch's official driver, exact file/version/date, BSD-3-Clause text
   reproduced in full, byte count independently re-counted (8192). ✅
5. **Register bitfield correctness** — every RCC/GPIO/I2C/USART/BMI270
   constant traces to a DS-MCU-/DS-IMU- Evidence ID in
   `datasheets/evidence-log.md`. ✅
6. **Host communication framing consistency** — 115200/8N1 stated in this
   document, `usart2.c`, and `README.md` all agree; the CSV header line
   the firmware actually transmits states plainly that values are raw
   counts, not physical units. ✅
7. **Scope-boundary compliance** — no USB/wireless code anywhere; no unit
   conversion/filtering/control-loop code (`bmi270_read_sample()` returns
   raw `int16_t` counts only). ✅
8. **Tooling-honesty compliance** — §0/§7 state exactly what was
   installed, built, and NOT run on hardware; no overstated claim found on
   re-read. ✅
9. **Evidence traceability** — spot-checked every register constant in
   `stm32g031_regs.h`/`bmi270.c` against its Evidence ID row; no
   uncited numeric register fact found. ✅
10. **Requirement-vs-schematic consistency** — REQ-004/SW1 discrepancy
    documented in §2 rather than silently reconciled. ✅

**Verdict**: self-check clean, no findings requiring rework. No
independent Firmware Reviewer exists yet
(`docs/architecture-evolution.md` §32) — per that section's documented
scope decision, this self-check stands in for independent review this
round. **2026-09-08 ISS-014 follow-up**: an additional, ad hoc independent
verification pass was requested for this specific pin/AF correction (not a
formal Firmware Reviewer gate, which still does not exist) — see the new
"§10 Independent verification" below for its outcome.

## 9. Handoff

**To**: Hardware Lead. **Artifacts**: this document; the firmware source
tree (`firmware/bench-imu-01/{src,linker,Makefile}`); `firmware/README.md`
and `firmware/bench-imu-01/README.md` (tooling-honesty summaries); new
Evidence ID rows DS-MCU-055 through DS-MCU-063 and DS-IMU-078 through
DS-IMU-088 (`datasheets/evidence-log.md`); three new datasheet metadata
records (`datasheets/stmicroelectronics_cmsis_device_g0_master.md`,
`datasheets/boschsensortec_bmi270_sensorapi_v2.86.1.md`,
`datasheets/stmicroelectronics_an4235_i2c-timing-configuration-tool.md`).
**2026-09-08 ISS-014 follow-up addition**: new Evidence ID rows DS-MCU-068,
DS-MCU-069; two new datasheet metadata records
(`datasheets/stmicroelectronics_stm32cubeg0_master.md`,
`datasheets/stmicroelectronics_stm32g0xx-hal-driver_master.md`); updated
`validation/open-issues.md` (ISS-014 Notes) and `validation/change-log.md`
(new ECO entry).

**Open items**:
- The AN4235 TIMINGR value (DS-MCU-063) was cross-checked via two
  independent web-search-derived sources but not directly fetched from the
  primary PDF this session — flagged at moderate-not-highest confidence in
  its own metadata record; low-risk for a paper/source-code cycle, worth a
  direct PDF re-check before real hardware bring-up.
- The 150 ms software timeout for the BMI270 config-load poll (§5 step 6)
  is an engineering safety margin, not itself a cited datasheet figure —
  flagged as such, not presented as a manufacturer-specified value.
- No independent Firmware Reviewer role exists yet — see
  `docs/architecture-evolution.md` §32 for the documented future trigger.

I have not declared this firmware "tested" or "hardware-verified" anywhere
in this document — per §0, no physical board exists this session.

## 10. Independent verification (2026-09-08, ISS-014 firmware follow-up)

An ad hoc, adversarial verification pass (not a formal Firmware Reviewer
gate, which still does not exist — `docs/architecture-evolution.md` §32)
was run against this fix, deliberately instructed to re-derive every fact
from primary sources itself rather than trust this document's own
citations. Summary of its independent findings (full report retained in
this session's record):

- Independently re-fetched ST's official pin database and confirmed PA11
  (pin 22)/PA12 (pin 23) = I2C2_SCL/SDA; independently re-fetched both new
  official ST sources (STM32CubeG0's NUCLEO-G031K8 example,
  `stm32g0xx-hal-driver`'s header) and confirmed AF6 (`0x06`), cross-checked
  against the exact same commit SHAs recorded in DS-MCU-068/069.
- Independently checked the actual `git diff` against every one of its own
  derived facts (GPIO port/base address, AF value, RCC enable bit,
  AFRH bit-field math for pins 11/12, I2C2 base address unchanged, no
  collateral change to USART2/LED pins) — all matched.
- Independently rebuilt the firmware (`make clean && make`): succeeded,
  zero warnings, identical image size. Independently confirmed via three
  separate methods (objdump+grep, a raw byte-pattern scan of the ELF, and a
  native, non-ARM re-execution of `gpio.c`'s exact bit-manipulation helper
  functions against a mock register struct) that the GPIOB base address is
  absent from the compiled output and the bit values written for pins
  11/12 are exactly MODER=AF, AF=6, OTYPER=open-drain.
- Full-text-scanned (not spot-checked) the updated design doc and README
  for any stale PB10/PB11 claim presented as a current fact — found none;
  all remaining PB10/PB11 mentions are correctly-framed historical/
  corrective narrative.
- Verified the new evidence-log rows/datasheet metadata records accurately
  reflect its own independent fetches, and that `validation/open-issues.md`
  (row/column count unchanged, `tools/check_open_issues.py` still passes)
  and the new `change-log.md` ECO entry are accurate.

**Verdict: CONFIRMED CORRECT.** Zero findings (no CRITICAL/HIGH/MEDIUM/LOW
issues raised) — an independent, from-first-principles re-derivation, not a
re-read of this document's own claims. Scoped strictly to firmware-register
correctness; does not reopen or comment on Bench-IMU-01's Design Complete
status (already granted, ECO-005) or ISS-014's schematic-level RESOLVED/
CRITICAL disposition (already independently confirmed by a prior Hardware
Reviewer Cycle-3 pass, unaffected by this firmware-only fix).
