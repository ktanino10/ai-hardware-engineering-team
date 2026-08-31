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
 */
#ifndef BENCH_IMU_01_CLOCK_H
#define BENCH_IMU_01_CLOCK_H

/* Enables the GPIOA/GPIOB/I2C2/USART2/PWR peripheral clocks this board's
 * schematic actually uses. Does not touch RCC_CR/RCC_CFGR/RCC_PLLCFGR --
 * the MCU is already running on HSI16 at reset, so there is deliberately
 * nothing else to configure for the clock source itself. */
void clock_init(void);

#endif /* BENCH_IMU_01_CLOCK_H */
