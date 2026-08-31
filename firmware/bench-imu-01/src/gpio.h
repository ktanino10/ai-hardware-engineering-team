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
 * PA11/PA12 -- corrected this revision (ISS-014): the IMU bus was previously
 * documented/configured on PB10/PB11, which do not exist as physical pins
 * anywhere on this MCU's real LQFP-32 package (DS-MCU-064/067). The real,
 * physically-wirable I2C2 pins are PA11 (physical pin 22) and PA12
 * (physical pin 23) -- same I2C2 peripheral instance, default/unremapped
 * state, no conflict with this design's other pin usage. Corrected in
 * hardware/schematic/bench-imu-01-design.md (Rev 2, corrected) and this
 * firmware to match.
 *
 * PA11/PA12 are configured open-drain (I2C is a wired-AND bus; the schematic
 * already provides the external 4.7 kOhm pull-ups R3/R4, Section 5.2 -- this
 * firmware must not add internal pull-ups or drive push-pull, either of
 * which would fight the bus).
 */
#ifndef BENCH_IMU_01_GPIO_H
#define BENCH_IMU_01_GPIO_H

void gpio_init(void);

/* Status/heartbeat LED (D1 via R5, PA5, active-high drive per Section 7). */
void led_set(int on);
void led_toggle(void);

#endif /* BENCH_IMU_01_GPIO_H */
