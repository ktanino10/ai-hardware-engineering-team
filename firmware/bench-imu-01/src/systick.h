/*
 * systick.h -- 1 ms system tick using the Cortex-M0+ core's SysTick timer.
 *
 * Used for: the status/heartbeat LED's blink period (REQ-003 -- "heartbeat
 * implies firmware toggles PA5 periodically" per hardware/schematic/
 * bench-imu-01-design.md Section 7), the CSV timestamp field emitted over
 * UART, and simple busy-wait delays during BMI270 bring-up (e.g. the
 * datasheet-mandated >=2 ms wait after a soft reset).
 *
 * SysTick is an ARM Cortex-M architectural peripheral at a fixed address
 * (0xE000E010), not an ST-specific fact -- see stm32g031_regs.h.
 */
#ifndef BENCH_IMU_01_SYSTICK_H
#define BENCH_IMU_01_SYSTICK_H

#include <stdint.h>

/* Configures SysTick for a 1 ms period at the 16 MHz HSI16 core clock
 * (clock.c leaves the MCU on its default HSI16, no PLL) and enables its
 * interrupt. Must be called after clock_init(). */
void systick_init(void);

/* Milliseconds since systick_init() was called. Wraps at ~49.7 days
 * (uint32_t) -- not a concern for a bench bring-up session. */
uint32_t millis(void);

/* Busy-wait delay, built on millis(). */
void delay_ms(uint32_t ms);

#endif /* BENCH_IMU_01_SYSTICK_H */
