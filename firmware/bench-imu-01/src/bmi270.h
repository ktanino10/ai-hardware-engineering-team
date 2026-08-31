/*
 * bmi270.h -- BMI270 driver for Bench-IMU-01: the manufacturer-mandated
 * initialization sequence (soft reset, configuration-file upload, status
 * poll) plus polled accelerometer/gyroscope register reads over I2C2.
 *
 * Scope boundary (Firmware Engineer, this cycle -- see
 * .github/agents/firmware-engineer.agent.md "Out of scope"): this driver
 * returns RAW signed 16-bit register counts, not physical units (g / dps).
 * Converting counts to physical units requires the sensor's configured
 * full-scale range and its LSB-per-unit sensitivity, and meaningfully using
 * that data (filtering, calibration, sensor fusion) is Control-Engineer-
 * flavored work -- explicitly deferred until that discipline's own trigger
 * is met (docs/architecture.md Section 14; the 1-axis/3-axis attitude
 * control roadmap stage is NOT met by this bench board). Raw counts are a
 * legitimate, complete "driver-level bring-up" deliverable on their own:
 * they prove the sensor, bus, and initialization sequence actually work.
 */
#ifndef BENCH_IMU_01_BMI270_H
#define BENCH_IMU_01_BMI270_H

#include <stdint.h>

/* Result of bmi270_init(). */
typedef enum
{
    BMI270_OK = 0,
    BMI270_ERR_CHIP_ID,     /* CHIP_ID register did not read the expected value */
    BMI270_ERR_I2C,         /* an I2C transaction failed (NACK/bus error/timeout) */
    BMI270_ERR_CONFIG_LOAD, /* INTERNAL_STATUS never reported config-load success */
} bmi270_status_t;

typedef struct
{
    int16_t acc_x, acc_y, acc_z; /* raw accelerometer counts */
    int16_t gyr_x, gyr_y, gyr_z; /* raw gyroscope counts */
} bmi270_sample_t;

/* Runs the full manufacturer-mandated bring-up sequence: soft reset, CHIP_ID
 * check, configuration-file upload (bmi270_config_file.h, vendored verbatim
 * from Bosch's official driver), ACC_CONF/GYR_CONF at >=100 Hz ODR
 * (REQ-001), and PWR_CTRL enabling the accelerometer + gyroscope. Assumes
 * i2c2_init() has already been called. Blocking; can take on the order of
 * tens of milliseconds (config upload + init poll). */
bmi270_status_t bmi270_init(void);

/* Reads one accel+gyro sample via a single 12-byte burst read starting at
 * ACC_X_LSB (0x0C) -- accel X/Y/Z then gyro X/Y/Z are contiguous registers
 * on this part (confirmed this session against Bosch's own register map,
 * ACC_X_LSB=0x0C, GYR_X_LSB=0x12). Returns 0 on success, -1 on I2C failure. */
int bmi270_read_sample(bmi270_sample_t *out);

#endif /* BENCH_IMU_01_BMI270_H */
