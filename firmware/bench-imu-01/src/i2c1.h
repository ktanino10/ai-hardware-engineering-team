/*
 * i2c1.h -- I2C1 polling-mode driver for the Rev 3 Motor Driver subsystem's
 * commissioning/status bus to U5 (DRV10983), PB6=SCL, PB7=SDA
 * (hardware/schematic/bench-imu-01-design.md Section 7.5.4). Fast-mode,
 * 400 kHz, reusing the exact same I2C2_TIMINGR_400KHZ_AT_16MHZ constant as
 * the IMU bus (both buses run the same 16 MHz PCLK, so the same
 * ST-published TIMINGR value applies to both -- see stm32g031_regs.h).
 *
 * This is a direct structural mirror of i2c2.c/h (same "I2C peripheral v2"
 * IP block, same polling-mode/no-interrupt design, same wait-with-timeout
 * discipline) with the instance renamed I2C2->I2C1 throughout. Deliberately
 * a SEPARATE peripheral instance from I2C2 (the IMU bus), not a shared bus:
 * the schematic wires U5's commissioning interface to PB6/PB7 (I2C1), not
 * PA11/PA12 (I2C2) -- these are two independent I2C buses on two different
 * hardware peripheral instances, serving two functionally-independent
 * subsystems (IMU vs. motor driver) per this firmware's own scope fence
 * (no cross-wiring between the IMU and motor subsystems).
 *
 * Register-level facts (I2C1_BASE, reuse of the generic I2C_TypeDef struct,
 * PB6/PB7=AF6, RCC_APBENR1_I2C1EN) are all sourced in stm32g031_regs.h,
 * cited to DS-MCU-074 there.
 */
#ifndef BENCH_IMU_01_I2C1_H
#define BENCH_IMU_01_I2C1_H

#include <stdint.h>

void i2c1_init(void);

/* Writes `reg` followed by `len` data bytes to `addr7` (7-bit address, NOT
 * pre-shifted) in a single START..STOP transaction. `len` must satisfy
 * 1 + len <= 255 (I2C_CR2 NBYTES is 8 bits). Returns 0 on success, -1 on
 * NACK/bus error/timeout. */
int i2c1_write(uint8_t addr7, uint8_t reg, const uint8_t *data, uint16_t len);

/* Writes `reg` (register pointer, no payload), then issues a repeated START
 * to read `len` bytes back from `addr7`. `len` must satisfy len <= 255.
 * Returns 0 on success, -1 on NACK/bus error/timeout. */
int i2c1_read(uint8_t addr7, uint8_t reg, uint8_t *data, uint16_t len);

#endif /* BENCH_IMU_01_I2C1_H */
