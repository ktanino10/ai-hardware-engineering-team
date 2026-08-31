/*
 * tim1_pwm.h -- TIM1 PWM driver for the SPEED command line to U5 (DRV10983),
 * PA8/TIM1_CH1 (hardware/schematic/bench-imu-01-design.md Section 7.5.4).
 *
 * DRV10983's SPEED pin, in this schematic's PWM-speed-control-mode wiring
 * (SysOpt9.SpdCtrlMd=1, see drv10983.c), reads duty cycle as the commanded
 * speed setpoint: this driver only produces the PWM waveform -- it has no
 * concept of "RPM" or any control logic. That belongs to motor.c (the
 * open-loop speed-setpoint/RPM-report characterization routine and the
 * REQ-405/406 safety logic), which is the only caller of this module.
 *
 * PWM frequency: 20 kHz. This board's own schematic notes (Section 7.5.4)
 * only specify the SPEED pin's PWM nature, not an exact frequency -- like
 * the host UART baud rate, this is a Firmware Engineer decision this cycle.
 * 20 kHz is chosen because: (1) SPEED is a logic-level duty-cycle command
 * into U5's own internal low-pass/de-glitch input filter, not a switching
 * power stage in its own right (U5's internal FET switching runs at its own
 * separate, much higher frequency, unaffected by this choice) -- 20 kHz is
 * simply a conventional, unremarkable rate for this class of "duty cycle as
 * an analog-equivalent command" interface, comfortably fast enough that U5's
 * input filtering sees a clean average duty cycle rather than a sluggish
 * one; (2) it divides the 16 MHz HSI16 core clock evenly
 * (16,000,000 / 20,000 = 800), giving an exact, round PWM period with no
 * residual timing error to account for.
 *
 * PSC=0, ARR=799 (800 counts, 0..799 inclusive) at 16 MHz -> exactly 20 kHz.
 * CCR1 = duty_pct * 8 for integer duty_pct in [0, 100] (0 -> 0/800 = 0%,
 * 100 -> 800/800 = 100%; note CCR1=800 with ARR=799 in PWM Mode 1 correctly
 * yields a permanent-high, i.e. true 100%, output per the standard
 * TIMx_CCRx > TIMx_ARR edge-case behaviour of this timer IP).
 *
 * TIM1 is an advanced-control timer: unlike TIM3 (a general-purpose timer),
 * its channel outputs do not reach their pins unless BDTR.MOE (main output
 * enable) is also set -- this is required, not optional, and is easy to
 * forget (a fact independently re-confirmed this session, DS-MCU-075).
 */
#ifndef BENCH_IMU_01_TIM1_PWM_H
#define BENCH_IMU_01_TIM1_PWM_H

#include <stdint.h>

/* Configures TIM1 CH1 for 20 kHz PWM Mode 1 output on PA8, output disabled
 * (0% duty) until tim1_pwm_set_duty_pct() is called. Must be called after
 * gpio_init() (PA8 AF2 mux) and clock_init() (RCC_APBENR2_TIM1EN). */
void tim1_pwm_init(void);

/* Sets the SPEED PWM duty cycle, 0-100 inclusive. Values outside this range
 * are clamped (defensive input sanitization -- REQ-405's first, trivial
 * enforcement layer; see motor.c for the substantive, FG-measurement-based
 * enforcement layer). */
void tim1_pwm_set_duty_pct(uint32_t duty_pct);

#endif /* BENCH_IMU_01_TIM1_PWM_H */
