/*
 * i2c2.h -- I2C2 polling-mode driver for the IMU bus (PA11=SCL, PA12=SDA --
 * corrected this revision, ISS-014; was previously PB10/PB11, which do not
 * exist as physical pins on this package's real LQFP-32 package, see
 * gpio.c/gpio.h and stm32g031_regs.h for the full correction),
 * hardware/schematic/bench-imu-01-design.md Section 5. Fast-mode, 400 kHz,
 * matching the schematic's own R3/R4 pull-up sizing target (Section 5.2).
 *
 * Deliberately I2C2, not I2C1 -- see stm32g031_regs.h's I2C2_BASE comment
 * and gpio.c's PA11/PA12 AF6 comment for why this specific fact gets triple
 * emphasis in this codebase: it is the exact class of defect (ISS-011,
 * ISS-014) an independent review caught in the schematic itself.
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
