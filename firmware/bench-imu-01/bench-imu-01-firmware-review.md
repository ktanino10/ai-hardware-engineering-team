# Bench-IMU-01 Firmware Review

**Reviewer**: Firmware Reviewer (fallback invocation)  
**Date**: 2026-09-01  
**Scope reviewed**: `firmware/bench-imu-01/README.md`, `bench-imu-01-firmware-design.md`, all `src/*.c`/`*.h`, `Makefile`, `linker/STM32G031K8Tx_FLASH.ld`, `hardware/schematic/bench-imu-01-design.md`, `requirements/requirements.md` (REQ-405/406), and `datasheets/evidence-log.md` entries cited by the firmware.  
**Build/tooling status**: Independently rebuilt with `arm-none-eabi-gcc (GCC) 16.2.0`; inspected linked output with `arm-none-eabi-objdump`/`nm`. No hardware, flashing, or HIL validation performed.

## Verdict

**PASS** — the prior **HIGH** firmware defect (Finding 1, REQ-405 command-side ceiling omission) is now **RESOLVED** by an independently verified command-side reject layer plus the unchanged FG-based reactive shutdown. Firmware findings do **not** block the Design Complete gate; with no open CRITICAL/HIGH finding found in this re-review, this cycle no longer blocks the `before flashing firmware to real hardware for the first time` HITL checkpoint on firmware-review grounds alone.

## Checklist results

1. **Pin/peripheral-instance fidelity** — Confirmed against the current schematic: IMU bus on **I2C2 PA11/PA12**; motor pins **PA8 / PA6 / PB1 / PB6 / PB7 / PA9** match `hardware/schematic/bench-imu-01-design.md` §5.3, §7.5.4, and the corrected pin table.
2. **Register/base-address and bitfield correctness** — Spot-checked and independently corroborated against `datasheets/stmicroelectronics_cmsis_device_g0_master.md` and the evidence log: `I2C2_BASE=0x40005800`, `I2C1_BASE=0x40005400`, `TIM1_BASE=0x40012C00`, `TIM3_BASE=0x40000400`, AF selections, RCC enable bits, and TIM3 IRQ number all align with DS-MCU-056/074/075/076.
3. **Clock configuration correctness** — Confirmed. Firmware leaves the MCU on reset-default HSI16; USART2 BRR, I2C TIMINGR reuse, TIM1 20 kHz PWM, and TIM3 10 µs tick are all internally consistent with 16 MHz.
4. **Manufacturer-mandated sequence completeness** — BMI270 init sequence and DRV10983 MSB-then-LSB speed-read sequence are implemented with appropriate ordering. REARM re-commissions DRV10983 after rail repower as required.
5. **Vendored opaque data provenance** — Confirmed for `bmi270_config_file.h`: Bosch source file, version, byte count, and BSD-3-Clause license are recorded.
6. **Safety-critical logic correctness (REQ-405/406)** — Confirmed. REQ-405 now has both a genuine command-side reject on over-ceiling `SPD` inputs and the pre-existing FG-measured reactive shutdown layer; REQ-406’s latch behavior remains implemented consistently: trips set `s_fault_latched=1`, clear `s_armed`, and only `REARM` clears the latched state.
7. **Premise review** — Re-derived independently rather than trusting the firmware narrative: the corrected PA11/PA12 IMU wiring and the separate I2C1 motor bus are both real in the current schematic.
8. **Scope-boundary compliance** — Confirmed. No PID, sensor fusion, unit conversion, USB data stack, or wireless code found.
9. **Tooling-honesty compliance** — Confirmed. Source correctly states build-only verification and no hardware validation. I independently rebuilt the firmware this review.
10. **Evidence traceability** — Mostly good. Cited Evidence IDs resolve in `datasheets/evidence-log.md` and match the claims spot-checked during review.

## Finding status update

### Finding 1 — RESOLVED
- **Original Issue**: REQ-405 required firmware to **reject or clamp any command exceeding the maximum commanded flywheel speed**, but the prior revision accepted `SPD <0-100>` with no command-side ceiling tied to the 6000 RPM limit.
- **Independent verification rationale**: `cmd_spd()` now rejects any input `val > MOTOR_MAX_CMD_DUTY_PCT` before changing `s_duty_pct` or calling `tim1_pwm_set_duty_pct()`, emitting `SPD_REJECTED reason=exceeds_cmd_duty_ceiling`. I independently re-derived the ceiling rather than trusting the design note: DRV10983 §8.4.5.3 states the speed command is proportional to PWM input duty cycle (DS-MTR-077); DRV10983 §8.3.3 states peak output amplitude scales as `VCC × (PWM_DCO/100)` and the named internal limiting features can only reduce, not increase, actual output relative to that bound (DS-MTR-078); M1 is rated KV = 2000 RPM/V (DS-MTR-017); and the schematic binds `VM_MOTOR` to 9.0–13.0 V with 13.0 V explicitly in-envelope (§7.5.9/§7.5.10). Therefore `ceiling_duty_pct = floor(6000 / (2000 × 13.0) × 100) = floor(23.0769...) = 23`. Sanity check: 23% gives an upper-bound estimate of 5980 RPM; 24% gives 6240 RPM, so 23% is the largest integer percentage that honestly stays at or below the 6000 RPM ceiling under the stated conservative assumptions.
- **Code-path confirmation**: This is a genuine **input-command** reject layer, not a control loop or error-term manipulation. The rejection happens inside `cmd_spd()` before PWM is updated. The pre-existing `check_overspeed()` FG-based shutdown remains separately active as the reactive backstop.
- **Datasheet Source**: REQ-405; DS-MTR-017; DS-MTR-077; DS-MTR-078; `hardware/schematic/bench-imu-01-design.md` §7.5.9/§7.5.10.
- **Affected Component**: `firmware/bench-imu-01/src/motor.c` / `motor.h`, affecting U5 DRV10983 + M1 motor subsystem.
- **Resolution verdict**: **CLOSED**

## Additional findings from this re-review

- None. No new CRITICAL/HIGH/MEDIUM/LOW defect was found in the changed area.

## REQ-405 / REQ-406 line-by-line conclusion

- **REQ-405**: **Holds up in this re-review.** The actual overspeed trip path still exists and is latched: while armed, `motor_tick()` always calls `check_overspeed()`, which trips to safe-state on `rpm > 6000`, on FG loss after prior validity, or on FG-never-valid after the bounded spin-up timeout. In addition, `cmd_spd()` now implements the requirement’s explicit command-side `reject/clamp any command exceeding` clause by rejecting `SPD` inputs above the independently re-derived 23% duty ceiling before updating PWM.
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

Finding 1 is genuinely closed on independent re-verification. I found no new CRITICAL/HIGH findings, and the firmware rebuild completed cleanly. From a Firmware Reviewer standpoint, this cycle is **PASS** and no longer blocks the `before flashing firmware` HITL gate on the previously open REQ-405 issue.
