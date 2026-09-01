/*
 * gpio.h -- GPIO pin muxing for Bench-IMU-01, matching the schematic's
 * pin-assignment table exactly (hardware/schematic/bench-imu-01-design.md
 * Section 2.3 "Pin allocation" and Section 11 "Full MCU pin-assignment
 * table"). Every pin below is cited back to that table -- this file does
 * not invent or re-derive a pin assignment.
 *
 *   PA2  = USART2_TX (AF1)  -- J2 UART header "TX"      (Section 6)
 *   PA3  = USART2_RX (AF1)  -- J2 UART header "RX"      (Section 6)
 *   PA5  = status/heartbeat LED (D1), plain GPIO output  (Section 7)
 *   PA11 = I2C2_SCL  (AF6)  -- IMU bus, R3 external pull-up already on board
 *   PA12 = I2C2_SDA  (AF6)  -- IMU bus, R4 external pull-up already on board
 *
 * PA11/PA12 (NOT PB10/PB11 -- see below) are configured open-drain (I2C is a
 * wired-AND bus; the schematic already provides the external 4.7 kOhm
 * pull-ups R3/R4, Section 5.2 -- this firmware must not add internal
 * pull-ups or drive push-pull, either of which would fight the bus).
 *
 * CORRECTED PIN ASSIGNMENT (this cycle): the IMU I2C2 bus was previously
 * configured on PB10/PB11 in this firmware. That was wrong: PB10/PB11 are
 * not bonded out on the STM32G031K8T6's actual LQFP-32/UFQFPN32 package --
 * CRITICAL defect ISS-027 (validation/open-issues.md), RESOLVED at the
 * hardware/schematic level and confirmed by primary package/pinout evidence
 * (DS-MCU-073), independently re-derived a second time and corroborated
 * against two further official ST sources by origin/main's own parallel fix
 * for this same defect (DS-MCU-068/077 -- see gpio.c's PA11/PA12 AF6
 * comment). The corrected, real wiring is PA11(SCL)/PA12(SDA) -- same
 * I2C2 peripheral instance, same AF6 alternate-function value; only the
 * port letter and pin numbers changed. i2c2.c/h needed no changes (they are
 * peripheral-register-level, not GPIO-pin-level).
 *
 *   Rev 3 motor subsystem (DRV10983 U5 + TPS26631PWPR U6), Section 7.5:
 *   PA8  = TIM1_CH1  (AF2)  -- SPEED (PWM command to U5)
 *   PA6  = TIM3_CH1  (AF1)  -- FG tach input from U5 (R6 external pull-up)
 *   PB1  = DIR, plain GPIO output -- direction command to U5
 *   PB6  = I2C1_SCL  (AF6)  -- U5 commissioning/status bus
 *   PB7  = I2C1_SDA  (AF6)  -- U5 commissioning/status bus
 *   PA9  = U6 SHDN, plain GPIO output -- motor rail enable (active HIGH;
 *          R11 external pulldown makes LOW/floating the fail-safe default,
 *          REQ-403; this firmware drives PA9 explicitly LOW at boot to
 *          preserve that intent once the pin becomes a driven output)
 */
#ifndef BENCH_IMU_01_GPIO_H
#define BENCH_IMU_01_GPIO_H

void gpio_init(void);

/* Status/heartbeat LED (D1 via R5, PA5, active-high drive per Section 7). */
void led_set(int on);
void led_toggle(void);

/* Rev 3 motor subsystem plain-GPIO command pins (motor.c owns the actual
 * DIR/SHDN policy -- these are just the register-level pin drivers,
 * mirroring led_set()'s BSRR-based atomic set/reset pattern). */

/* PB1 = DIR to U5. `reverse`=0 drives PB1 LOW (forward, this firmware's
 * default convention), nonzero drives PB1 HIGH (reverse). */
void motor_dir_set(int reverse);

/* PA9 = U6 SHDN. `enable`=0 drives PA9 LOW (motor rail OFF, the REQ-403
 * fail-safe state), nonzero drives PA9 HIGH (motor rail ON). */
void motor_shdn_set(int enable);

#endif /* BENCH_IMU_01_GPIO_H */
