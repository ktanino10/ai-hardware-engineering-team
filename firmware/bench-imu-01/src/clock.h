/*
 * clock.h -- system clock bring-up for Bench-IMU-01.
 *
 * Design decision (Firmware Engineer, this cycle): run entirely on the
 * STM32G031K8T6's default HSI16 (16 MHz internal RC oscillator), no PLL.
 * hardware/schematic/bench-imu-01-design.md Section 6 confirms "no external
 * crystal is populated -- the MCU runs off its internal HSI16+PLL clock" but
 * deliberately leaves the exact target frequency to firmware. HSI16-with-no-
 * PLL (i.e. 16 MHz, the part's power-on-reset default -- no clock-tree
 * registers need to change at all) is chosen because: (a) it needs zero
 * additional clock-configuration risk, since it's already the reset-default
 * state; (b) it keeps the I2C2 TIMINGR and USART2 BRR constants in this
 * firmware simple, single-frequency values instead of a family of them; (c)
 * REQ-001's >=100 Hz ODR and REQ-106's UART link have no headroom requirement
 * that would need the part's higher clock ceiling (up to 64 MHz).
 *
 * REVALIDATED (Rev 3 motor subsystem, this cycle): the new TIM1 (SPEED PWM),
 * TIM3 (FG input capture), and I2C1 (U5 commissioning bus) peripherals all
 * derive from this same 16 MHz HSI16 with no fractional-prescaler headaches
 * -- 16 MHz / 800 = an exact 20 kHz for TIM1's PWM period, 16 MHz / 160 = an
 * exact 100 kHz (10 us/tick) for TIM3's capture counter (PSC=159 -- chosen
 * over a finer PSC=15/1 us-tick alternative for wraparound-safety margin at
 * low RPM; see tim3_fg.h for the full trade-off analysis), and I2C1 reuses
 * I2C2's already-validated 400 kHz-at-16 MHz TIMINGR constant verbatim (same
 * silicon IP block, same bus clock). There is no motor-subsystem requirement
 * that would justify revisiting this clock choice, so it is being
 * deliberately reaffirmed, not silently inherited without re-examination.
 */
#ifndef BENCH_IMU_01_CLOCK_H
#define BENCH_IMU_01_CLOCK_H

/* Enables the GPIOA/GPIOB/I2C1/I2C2/TIM1/TIM3/USART2/PWR peripheral clocks
 * this board's schematic actually uses. GPIOB is enabled for the Rev 3
 * motor subsystem's PB1/PB6/PB7 pins -- it is NOT needed for the IMU's I2C2
 * bus, which lives on PA11/PA12 (corrected this cycle, ISS-027, from a
 * previously-configured PB10/PB11 pair that does not physically exist on
 * this package -- independently corroborated by origin/main's own parallel
 * fix, DS-MCU-068/077). Does not touch RCC_CR/RCC_CFGR/RCC_PLLCFGR -- the
 * MCU is already running on HSI16 at reset, so there is deliberately
 * nothing else to configure for the clock source itself. */
void clock_init(void);

#endif /* BENCH_IMU_01_CLOCK_H */
