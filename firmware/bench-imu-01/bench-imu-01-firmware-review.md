# Bench-IMU-01 Firmware Review

**Reviewer**: Firmware Reviewer (fallback invocation)  
**Date**: 2026-09-01  
**Scope reviewed**: `firmware/bench-imu-01/README.md`, `bench-imu-01-firmware-design.md`, all `src/*.c`/`*.h`, `Makefile`, `linker/STM32G031K8Tx_FLASH.ld`, `hardware/schematic/bench-imu-01-design.md`, `requirements/requirements.md` (REQ-405/406), and `datasheets/evidence-log.md` entries cited by the firmware.  
**Build/tooling status**: Independently rebuilt with `arm-none-eabi-gcc (GCC) 16.2.0`; inspected linked output with `arm-none-eabi-objdump`/`nm`. No hardware, flashing, or HIL validation performed.

## Verdict

**FAIL** — one open **HIGH** firmware defect was found. Firmware findings do **not** block the Design Complete gate, but this finding **does** block the `before flashing firmware to real hardware for the first time` HITL checkpoint until resolved or explicitly accepted as risk.

## Checklist results

1. **Pin/peripheral-instance fidelity** — Confirmed against the current schematic: IMU bus on **I2C2 PA11/PA12**; motor pins **PA8 / PA6 / PB1 / PB6 / PB7 / PA9** match `hardware/schematic/bench-imu-01-design.md` §5.3, §7.5.4, and the corrected pin table.
2. **Register/base-address and bitfield correctness** — Spot-checked and independently corroborated against `datasheets/stmicroelectronics_cmsis_device_g0_master.md` and the evidence log: `I2C2_BASE=0x40005800`, `I2C1_BASE=0x40005400`, `TIM1_BASE=0x40012C00`, `TIM3_BASE=0x40000400`, AF selections, RCC enable bits, and TIM3 IRQ number all align with DS-MCU-056/074/075/076.
3. **Clock configuration correctness** — Confirmed. Firmware leaves the MCU on reset-default HSI16; USART2 BRR, I2C TIMINGR reuse, TIM1 20 kHz PWM, and TIM3 10 µs tick are all internally consistent with 16 MHz.
4. **Manufacturer-mandated sequence completeness** — BMI270 init sequence and DRV10983 MSB-then-LSB speed-read sequence are implemented with appropriate ordering. REARM re-commissions DRV10983 after rail repower as required.
5. **Vendored opaque data provenance** — Confirmed for `bmi270_config_file.h`: Bosch source file, version, byte count, and BSD-3-Clause license are recorded.
6. **Safety-critical logic correctness (REQ-405/406)** — **REQ-405 is NOT fully satisfied** due to one HIGH defect below. REQ-406’s latch behavior is otherwise implemented consistently: trips set `s_fault_latched=1`, clear `s_armed`, and only `REARM` clears the latched state.
7. **Premise review** — Re-derived independently rather than trusting the firmware narrative: the corrected PA11/PA12 IMU wiring and the separate I2C1 motor bus are both real in the current schematic.
8. **Scope-boundary compliance** — Confirmed. No PID, sensor fusion, unit conversion, USB data stack, or wireless code found.
9. **Tooling-honesty compliance** — Confirmed. Source correctly states build-only verification and no hardware validation. I independently rebuilt the firmware this review.
10. **Evidence traceability** — Mostly good. Cited Evidence IDs resolve in `datasheets/evidence-log.md` and match the claims spot-checked during review.

## High-severity finding(s)

### Finding 1
- **Issue**: REQ-405 says firmware shall **reject or clamp any command exceeding the maximum commanded flywheel speed**, but `SPD <0-100>` is accepted purely as a duty-cycle request with no command-side ceiling enforcement tied to the defined maximum speed.
- **Rationale**: The implemented overspeed logic only reacts **after** FG reports actual RPM above 6000 (`check_overspeed()` in `motor.c`). `cmd_spd()` accepts any value 0–100 when armed and immediately applies it via `tim1_pwm_set_duty_pct(val)`. There is no command-level clamp/reject based on the defined maximum speed, no bounded mapping from command to the approved ceiling, and no proof that `SPD 100` cannot request a speed above the approved 6000 RPM limit before feedback catches it.
- **Datasheet Source**: `requirements/requirements.md` REQ-405; schematic §7.5.11/firmware design §4.3 define the 6000 RPM ceiling, but do not change REQ-405’s explicit `reject/clamp any command exceeding it` wording.
- **Failure Mechanism**: A host can command `SPD 100`, which the firmware treats as an unconstrained open-loop request. The motor may accelerate above the approved ceiling until FG feedback detects the overspeed and trips safe-state. That behavior is reactive-only and does not satisfy the requirement’s explicit preventive `reject/clamp` clause.
- **Affected Component**: `firmware/bench-imu-01/src/motor.c` (`cmd_spd()`, `check_overspeed()`), affecting U5 DRV10983 + M1 motor subsystem.
- **Recommended Fix**: Add an explicit command-side enforcement layer tied to the approved maximum-speed policy. Examples: define the allowed command range in terms of the approved ceiling and reject/clamp `SPD` requests above that bound, or document and implement a calibrated duty-limit policy that is itself traceably bounded to the 6000 RPM ceiling. Keep the existing FG-based trip as the second safety layer, not the only one.
- **Severity**: **HIGH**

## Medium/low findings summary

- **LOW**: `motor.c`/`tim3_fg.c` use subtraction on millisecond timestamps without documenting rollover handling in the review-facing comments. The unsigned arithmetic is standard and acceptable, but the safety-path commentary could be crisper about wraparound assumptions.
- **LOW**: Some comments cite corroborating sources (e.g. DS-MCU-067) that were not part of this review scope’s primary spot-check set; the core checked claims still resolved correctly in the evidence log.

## REQ-405 / REQ-406 line-by-line conclusion

- **REQ-405**: **Does not fully hold up.** The actual overspeed trip path exists and is latched: while armed, `motor_tick()` always calls `check_overspeed()`, which trips to safe-state on `rpm > 6000`, on FG loss after prior validity, or on FG-never-valid after the bounded spin-up timeout. However, the code does **not** implement the requirement’s explicit command-side `reject/clamp any command exceeding` clause; it only performs post-factum feedback-based shutdown.
- **REQ-406**: **Holds up in source review.** `check_lock_faults()` edge-detects new lock events, tracks them in a 3-entry ring buffer over a 30 s window, and calls the shared latched safe-state path on threshold. The latch is not auto-cleared by the main loop, ISR path, STOP command, or initialization path; only `cmd_rearm()` clears `s_fault_latched` and re-arms. No alternate code path was found that silently clears the latch.

## Independent build / compiled-output verification

I **did** independently rebuild the firmware.

- `make clean && make` succeeded with `arm-none-eabi-gcc (GCC) 16.2.0` and produced `build/bench-imu-01.elf/.bin/.hex`.
- `arm-none-eabi-nm` confirmed key symbols including `TIM3_IRQHandler`, `gpio_init`, `i2c1_init`, `i2c2_init`, `tim1_pwm_init`, and `motor_tick`.
- `arm-none-eabi-objdump -d` confirmed the linked image contains the expected peripheral base-address literals:
  - `0x40005800` (I2C2)
  - `0x40005400` (I2C1)
  - `0x40012c00` (TIM1)
  - `0x40000400` (TIM3)
  - `0x50000400` (GPIOB)
- `TIM3_IRQHandler` is present in the vector table path and disassembles as a real handler reading TIM3 CCR1 and dividing by the compiled RPM constant `0x000d1437` (857143), consistent with the source formula.

## Final note to Hardware Lead

Route back to Firmware Engineer for REQ-405 correction. No CRITICAL findings were found, but the open HIGH means this review cycle is **FAIL** and should not pass the `before flashing firmware` HITL gate unchanged.
