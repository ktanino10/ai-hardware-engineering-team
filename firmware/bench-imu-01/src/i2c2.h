/*
 * i2c2.h -- I2C2 polling-mode driver for the IMU bus (PA11=SCL, PA12=SDA,
 * hardware/schematic/bench-imu-01-design.md Section 5/7.5.4/Section 11).
 * Fast-mode, 400 kHz, matching the schematic's own R3/R4 pull-up sizing
 * target (Section 5.2).
 *
 * CORRECTED PIN ASSIGNMENT (ISS-027, CRITICAL, RESOLVED): this bus's pins
 * were originally PB10(SCL)/PB11(SDA), which was a defect -- those two pads
 * do not physically exist on the STM32G031K8T6's actual LQFP-32 package.
 * The corrected, real pins are PA11(SCL)/PA12(SDA), same I2C2 peripheral
 * instance, same AF6 alternate-function value -- only the GPIO port/pin
 * changed (see gpio.c's PA11/PA12 AF6 comment and stm32g031_regs.h's
 * I2C2_BASE comment). This file itself (the I2C2 protocol layer: TIMINGR/
 * CR2/ISR/TXDR/RXDR register sequencing) needed ZERO changes for this fix
 * -- it is entirely GPIO-agnostic; only gpio.c/gpio.h/clock.c/clock.h
 * (pin muxing and clock enables) needed the actual pin-level correction.
 *
 * Deliberately I2C2, not I2C1 -- see stm32g031_regs.h's I2C2_BASE comment
 * for why this specific fact gets emphasis in this codebase: it is the
 * exact class of defect (ISS-011) an independent Hardware Reviewer caught
 * in the schematic itself. (Rev 3 also added a *second*, textually-similar
 * but functionally distinct I2C1 bus, i2c1.c/h, for the motor driver U5's
 * own commissioning/status interface on PB6/PB7 -- do not confuse the two;
 * they are different peripheral instances serving different subsystems.)
 *
 * Polling-mode (no interrupts), matching the schematic's own polled-
 * acquisition design decision (Section 5.3: "this design uses I2C polling
 * ... not interrupt-driven acquisition" -- INT1/INT2 are left NC).
 *
 * Register-level facts (SADD/RD_WRN/START/STOP/NBYTES/AUTOEND field
 * positions, ISR flag positions, and the 400 kHz/16 MHz TIMINGR value) are
 * all sourced in stm32g031_regs.h, cited to DS-MCU-<NNN> there.
 */
#ifndef BENCH_IMU_01_I2C2_H
#define BENCH_IMU_01_I2C2_H

#include <stdint.h>

void i2c2_init(void);

/* Writes `reg` followed by `len` data bytes to `addr7` (7-bit address, NOT
 * pre-shifted) in a single START..STOP transaction. `len` must satisfy
 * 1 + len <= 255 (I2C_CR2 NBYTES is 8 bits). Returns 0 on success, -1 on
 * NACK/bus error/timeout. */
int i2c2_write(uint8_t addr7, uint8_t reg, const uint8_t *data, uint16_t len);

/* Writes `reg` (register pointer, no payload), then issues a repeated START
 * to read `len` bytes back from `addr7`. `len` must satisfy len <= 255.
 * Returns 0 on success, -1 on NACK/bus error/timeout. */
int i2c2_read(uint8_t addr7, uint8_t reg, uint8_t *data, uint16_t len);

#endif /* BENCH_IMU_01_I2C2_H */
