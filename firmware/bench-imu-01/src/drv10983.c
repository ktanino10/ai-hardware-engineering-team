/*
 * drv10983.c -- see drv10983.h for the scope note.
 *
 * Register addresses/bit layouts and the register-mode-vs-EEPROM-commit
 * mechanics below are all confirmed this session directly against Texas
 * Instruments' own primary datasheet (SLVSCP6H, Rev H, re-fetched live via
 * r.jina.ai text extraction of the official ti.com PDF, including a
 * targeted re-fetch this session of Section 8.4.11.2.1's exact wording to
 * settle the two-byte-readback ordering question below) -- see
 * datasheets/evidence-log.md DS-MTR-072 through DS-MTR-076 for the exact
 * citation of each address/value used here.
 */
#include "drv10983.h"
#include "i2c1.h"

#define DRV10983_I2C_ADDR7 0x52u /* fixed slave address, not pin-strappable ("slave address 101 0010"); DS-MTR-072 */

#define REG_STATUS      0x10u
#define REG_MOTORSPEED1 0x11u /* MSB -- DS-MTR-075 */
#define REG_MOTORSPEED2 0x12u /* LSB -- DS-MTR-075 */
#define REG_FAULTCODE   0x1Eu
#define REG_EECTRL      0x03u
#define REG_SYSOPT9     0x2Bu

/* EECtrl (0x03): bit6=SIdata ("Set to 1 to enable the writing to the
 * configuration registers"). Writing 0x40 sets SIdata=1 and leaves
 * sleepDis/eeRefresh/eeWrite all 0 -- eeWrite (bit4) is deliberately NEVER
 * set by this firmware: an actual EEPROM commit also requires
 * DevCtrl.enProgKey=0xB6 first (DS-MTR-073) AND the motor rail reaching an
 * EEPROM-write voltage precondition this design's 2S-3S (~7.4-12.6V) rail
 * can never reach -- register-mode-only is not merely this firmware's
 * preference, it is the only mode this hardware is physically capable of
 * using, which is why commissioning must be re-run every SHDN low->high
 * transition instead of being a one-time EEPROM-programming step. */
#define EECTRL_SIDATA_ONLY 0x40u

/* SysOpt9 (0x2B) bit layout (DS-MTR-071): bits7:6=FGOLsel, bits5:4=FGcycle,
 * bits3:2=KtLckThr, bit1=SpdCtrlMd, bit0=CLoopDis. Factory-default EEPROM
 * value (Table 8) = 0x0C = 0b0000_1100 -- decoded bit-by-bit: FGOLsel
 * (bits7:6)=00, FGcycle (bits5:4)=00, KtLckThr (bits3:2)=11, SpdCtrlMd
 * (bit1)=0 (analog mode), CLoopDis (bit0)=0. This firmware needs PWM
 * speed-control mode (SpdCtrlMd=1) and nothing else changed, so the target
 * value is the factory default with ONLY bit1 forced to 1:
 *
 *   0b0000_1100 (0x0C default)
 * | 0b0000_0010 (bit1, SpdCtrlMd)
 * = 0b0000_1110 (0x0E target)
 *
 * (Re-derive this yourself before trusting it -- 0x0C | (1<<1) = 0x0E. An
 * earlier internal draft of this design mis-stated this target as 0x4E;
 * that number never reached any committed file, but is flagged here
 * explicitly as a caught-before-shipping arithmetic error, precisely the
 * kind of register-level mistake this project's Evidence ID discipline
 * exists to catch by forcing the derivation to be shown, not just
 * asserted.) */
#define SYSOPT9_DEFAULT         0x0Cu
#define SYSOPT9_SPDCTRLMD_BIT   (1u << 1)
#define SYSOPT9_PWM_MODE_TARGET (SYSOPT9_DEFAULT | SYSOPT9_SPDCTRLMD_BIT) /* = 0x0E */

static int write_reg(uint8_t reg, uint8_t value)
{
    return i2c1_write(DRV10983_I2C_ADDR7, reg, &value, 1u);
}

static int read_reg(uint8_t reg, uint8_t *value)
{
    return i2c1_read(DRV10983_I2C_ADDR7, reg, value, 1u);
}

drv10983_status_t drv10983_commission(void)
{
    uint8_t readback = 0u;

    /* 1. Unlock register-mode writes (SIdata=1). */
    if (write_reg(REG_EECTRL, EECTRL_SIDATA_ONLY) != 0)
    {
        return DRV10983_ERR_I2C;
    }

    /* 2. Write SysOpt9 with SpdCtrlMd=1 (PWM mode), all else at factory
     * default (see the derivation above the REG_SYSOPT9 #defines). */
    if (write_reg(REG_SYSOPT9, SYSOPT9_PWM_MODE_TARGET) != 0)
    {
        return DRV10983_ERR_I2C;
    }

    /* 3. Read SysOpt9 back to actually confirm the write took effect,
     * rather than assuming a NACK-free write means the value stuck --
     * mirrors bmi270_init()'s own CHIP_ID/INTERNAL_STATUS defensive-check
     * philosophy. A commissioning failure here means U5 is still in analog
     * speed-control mode, which motor.c's PWM-duty commands would not
     * actually control -- worth surfacing explicitly to motor.c rather
     * than silently proceeding as though PWM mode were active. */
    if (read_reg(REG_SYSOPT9, &readback) != 0)
    {
        return DRV10983_ERR_I2C;
    }
    if (readback != SYSOPT9_PWM_MODE_TARGET)
    {
        return DRV10983_ERR_VERIFY;
    }

    return DRV10983_OK;
}

int drv10983_read_status(uint8_t *status_reg)
{
    return read_reg(REG_STATUS, status_reg);
}

int drv10983_read_fault_code(uint8_t *fault_reg)
{
    return read_reg(REG_FAULTCODE, fault_reg);
}

int drv10983_read_motor_speed_raw(uint16_t *speed_hz_x10)
{
    uint8_t msb = 0u, lsb = 0u;

    /* Deliberately TWO separate single-byte reads, MSB register first, NOT
     * one 2-byte burst read starting at 0x11. TI's own datasheet (Section
     * 8.4.11.2.1 "Two-Byte Register Readback", re-confirmed verbatim this
     * session) documents this as an explicit 2-step sequence backed by a
     * hardware latch: "To ensure valid data is read when reading a two
     * register value, use the following sequence. 1. Read the MSB. 2. Read
     * the LSB... When the MSB is read, the controller takes a snapshot of
     * the LSB [into MotorSpeedBuffer[7:0]]... When the LSB is read, the
     * value of MotorSpeedBuffer[7:0] is sent." Reading the MSB register as
     * its own complete transaction is what the datasheet documents as
     * triggering that snapshot; this firmware does not assume (and has not
     * verified against silicon) that an auto-incrementing burst read
     * triggers the identical latch behavior, so it follows the datasheet's
     * literal two-step sequence instead of a plausible-but-unconfirmed
     * shortcut. This register pair is diagnostic-only (see drv10983.h) so
     * the extra I2C transaction this costs is immaterial. DS-MTR-075. */
    if (read_reg(REG_MOTORSPEED1, &msb) != 0)
    {
        return -1;
    }
    if (read_reg(REG_MOTORSPEED2, &lsb) != 0)
    {
        return -1;
    }

    *speed_hz_x10 = (uint16_t)(((uint16_t)msb << 8) | (uint16_t)lsb);
    return 0;
}
