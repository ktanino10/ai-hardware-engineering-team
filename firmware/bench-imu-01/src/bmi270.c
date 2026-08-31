/*
 * bmi270.c -- see bmi270.h for the scope note on raw-counts-only output.
 *
 * Register addresses and the configuration-file upload protocol below are
 * all confirmed this session directly against Bosch Sensortec's own official
 * open-source driver (https://github.com/boschsensortec/BMI270_SensorAPI,
 * bmi2_defs.h + bmi270.c + bmi2.c, BSD-3-Clause) -- see
 * datasheets/evidence-log.md DS-IMU-<NNN> rows for the exact citation of
 * each address/value used here. This is deliberately NOT copied logic from
 * that driver's C files (which implement a large, general-purpose,
 * multi-feature, multi-interface abstraction this bring-up program does not
 * need) -- only the vendored config_file[] byte array itself
 * (bmi270_config_file.h) and the register-map facts are reused; the
 * sequencing code below is this project's own minimal reimplementation of
 * that same manufacturer-documented sequence.
 */
#include "bmi270.h"
#include "bmi270_config_file.h"
#include "i2c2.h"
#include "systick.h"

#define BMI270_I2C_ADDR7 0x68u /* SDO tied to GND on this board (Section 5.3, DS-IMU-076) selects 0x68, not the alternate 0x69 */

#define REG_CHIP_ID          0x00u
#define REG_ACC_X_LSB        0x0Cu /* 12-byte contiguous burst: acc X/Y/Z, gyr X/Y/Z (gyr starts at 0x12) */
#define REG_INTERNAL_STATUS  0x21u
#define REG_ACC_CONF         0x40u
#define REG_GYR_CONF         0x42u
#define REG_INIT_ADDR_0      0x5Bu
#define REG_INIT_CTRL        0x59u
#define REG_INIT_DATA        0x5Eu
#define REG_PWR_CONF         0x7Cu
#define REG_PWR_CTRL         0x7Du
#define REG_CMD              0x7Eu

#define CMD_SOFT_RESET 0xB6u

#define CHIP_ID_EXPECTED 0x24u /* Bosch's own bmi270.h: BMI270_CHIP_ID */

#define CONFIG_LOAD_STATUS_MASK 0x0Fu
#define CONFIG_LOAD_SUCCESS     0x01u

/* ACC_CONF = filter_perf(1)<<7 | bwp_normal_avg4(0b010)<<4 | odr_100hz(0x08)
 * GYR_CONF = filter_perf(1)<<7 | noise_perf(1)<<6 | bwp_normal(0b010)<<4 | odr_100hz(0x08)
 * All four component values (perf-mode bits, bandwidth-parameter encoding,
 * 100 Hz ODR encoding) are Bosch's own named constants in bmi2_defs.h
 * (BMI2_PERF_OPT_MODE, BMI2_ACC_NORMAL_AVG4/BMI2_GYR_NORMAL_MODE,
 * BMI2_ACC_ODR_100HZ/BMI2_GYR_ODR_100HZ) -- combined here into the two
 * literal register values REQ-001 needs (>=100 Hz ODR). */
#define ACC_CONF_100HZ_NORMAL_PERF 0xA8u
#define GYR_CONF_100HZ_NORMAL_PERF 0xE8u

/* PWR_CTRL: bit1=gyr_en, bit2=acc_en (aux_en=bit0, temp_en=bit3 left off --
 * this board has no aux sensor and REQ-001 doesn't need temperature). */
#define PWR_CTRL_ACC_GYR_EN 0x06u

/* 32-byte chunks divide the 8192-byte config file evenly (256 chunks, no
 * remainder), matching the chunking Bosch's own driver uses and staying
 * comfortably within the I2C2 peripheral's single-transaction NBYTES limit
 * (see i2c2.c). Word-addressed: each chunk is 16 words (32 bytes / 2). */
#define CONFIG_CHUNK_BYTES 32u

static int write_reg(uint8_t reg, uint8_t value)
{
    return i2c2_write(BMI270_I2C_ADDR7, reg, &value, 1u);
}

static int read_reg(uint8_t reg, uint8_t *value)
{
    return i2c2_read(BMI270_I2C_ADDR7, reg, value, 1u);
}

static bmi270_status_t upload_config_file(void)
{
    uint16_t index;

    for (index = 0u; index < BMI270_CONFIG_FILE_SIZE; index += CONFIG_CHUNK_BYTES)
    {
        uint16_t word_offset = (uint16_t)(index / 2u);
        uint8_t addr_bytes[2];

        addr_bytes[0] = (uint8_t)(word_offset & 0x0Fu);
        addr_bytes[1] = (uint8_t)(word_offset >> 4);

        if (i2c2_write(BMI270_I2C_ADDR7, REG_INIT_ADDR_0, addr_bytes, 2u) != 0)
        {
            return BMI270_ERR_I2C;
        }
        if (i2c2_write(BMI270_I2C_ADDR7, REG_INIT_DATA, &bmi270_config_file[index], CONFIG_CHUNK_BYTES) != 0)
        {
            return BMI270_ERR_I2C;
        }
    }

    return BMI270_OK;
}

bmi270_status_t bmi270_init(void)
{
    uint8_t chip_id = 0u;
    uint8_t status = 0u;
    bmi270_status_t rslt;
    int timeout_ms;

    /* 1. Soft reset (CMD=0xB6), then the manufacturer-specified >=2 ms
     * settle time before any further transaction. */
    if (write_reg(REG_CMD, CMD_SOFT_RESET) != 0)
    {
        return BMI270_ERR_I2C;
    }
    delay_ms(3u); /* 2 ms required, 3 ms for a small margin */

    /* 2. Confirm the part actually responds and is a BMI270 before trusting
     * anything else -- catches a wrong I2C address/dead bus/miswired part
     * immediately rather than silently uploading 8 KB to nothing. */
    if (read_reg(REG_CHIP_ID, &chip_id) != 0)
    {
        return BMI270_ERR_I2C;
    }
    if (chip_id != CHIP_ID_EXPECTED)
    {
        return BMI270_ERR_CHIP_ID;
    }

    /* 3. Disable advanced power save (the part resets into APS mode, which
     * must be off during config load) and disable the config-load flag
     * before starting the upload. */
    if (write_reg(REG_PWR_CONF, 0x00u) != 0)
    {
        return BMI270_ERR_I2C;
    }
    delay_ms(1u); /* >= the 450 us settle Bosch's own driver waits after a PWR_CONF change */
    if (write_reg(REG_INIT_CTRL, 0x00u) != 0)
    {
        return BMI270_ERR_I2C;
    }

    /* 4. Upload the vendored 8 KB configuration blob. */
    rslt = upload_config_file();
    if (rslt != BMI270_OK)
    {
        return rslt;
    }

    /* 5. Signal "config load complete" and poll INTERNAL_STATUS until the
     * device reports BMI2_CONFIG_LOAD_SUCCESS (bits[3:0] == 0x01). */
    if (write_reg(REG_INIT_CTRL, 0x01u) != 0)
    {
        return BMI270_ERR_I2C;
    }
    for (timeout_ms = 0; timeout_ms < 150; timeout_ms++)
    {
        if (read_reg(REG_INTERNAL_STATUS, &status) != 0)
        {
            return BMI270_ERR_I2C;
        }
        if ((status & CONFIG_LOAD_STATUS_MASK) == CONFIG_LOAD_SUCCESS)
        {
            break;
        }
        delay_ms(1u);
    }
    if ((status & CONFIG_LOAD_STATUS_MASK) != CONFIG_LOAD_SUCCESS)
    {
        return BMI270_ERR_CONFIG_LOAD;
    }

    /* 6. Configure ODR (>=100 Hz, REQ-001) and enable accel+gyro. Advanced
     * power save is deliberately left disabled from step 3 onward -- a
     * simpler, more predictable always-ready sensor state, appropriate for
     * a bring-up/bench context where minimizing IMU current draw was never
     * this cycle's requirement (REQ-103's 300 mA budget already has ~95%
     * margin without it, hardware/power-budget.md). */
    if (write_reg(REG_ACC_CONF, ACC_CONF_100HZ_NORMAL_PERF) != 0)
    {
        return BMI270_ERR_I2C;
    }
    if (write_reg(REG_GYR_CONF, GYR_CONF_100HZ_NORMAL_PERF) != 0)
    {
        return BMI270_ERR_I2C;
    }
    if (write_reg(REG_PWR_CTRL, PWR_CTRL_ACC_GYR_EN) != 0)
    {
        return BMI270_ERR_I2C;
    }

    return BMI270_OK;
}

int bmi270_read_sample(bmi270_sample_t *out)
{
    uint8_t raw[12];

    if (i2c2_read(BMI270_I2C_ADDR7, REG_ACC_X_LSB, raw, sizeof(raw)) != 0)
    {
        return -1;
    }

    out->acc_x = (int16_t)((uint16_t)raw[0] | ((uint16_t)raw[1] << 8));
    out->acc_y = (int16_t)((uint16_t)raw[2] | ((uint16_t)raw[3] << 8));
    out->acc_z = (int16_t)((uint16_t)raw[4] | ((uint16_t)raw[5] << 8));
    out->gyr_x = (int16_t)((uint16_t)raw[6] | ((uint16_t)raw[7] << 8));
    out->gyr_y = (int16_t)((uint16_t)raw[8] | ((uint16_t)raw[9] << 8));
    out->gyr_z = (int16_t)((uint16_t)raw[10] | ((uint16_t)raw[11] << 8));
    return 0;
}
