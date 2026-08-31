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
 *   PB10 = I2C2_SCL  (AF6)  -- IMU bus, R3 external pull-up already on board
 *   PB11 = I2C2_SDA  (AF6)  -- IMU bus, R4 external pull-up already on board
 *
 * PB10/PB11 are configured open-drain (I2C is a wired-AND bus; the schematic
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
