#include "i2c2.h"
#include "stm32g031_regs.h"

/* Generous software timeout for any single wait-loop below, so a wedged bus
 * (e.g. no IMU present/miswired) cannot hang the firmware forever -- it
 * fails the transaction instead. Not derived from a datasheet timing spec;
 * simply "large enough to never legitimately trip at 400 kHz, small enough
 * to fail fast" -- an engineering judgment call, not a cited fact. */
#define I2C2_WAIT_LIMIT 100000

void i2c2_init(void)
{
    I2C2->CR1 = 0u; /* peripheral disabled while configuring TIMINGR, per RM0454 */
    I2C2->TIMINGR = I2C2_TIMINGR_400KHZ_AT_16MHZ;
    I2C2->CR1 = I2C_CR1_PE;
}

static int wait_flag_set(volatile uint32_t *reg, uint32_t mask)
{
    int guard = I2C2_WAIT_LIMIT;
    while (((*reg) & mask) == 0u)
    {
        if (--guard <= 0)
        {
            return -1;
        }
    }
    return 0;
}

int i2c2_write(uint8_t addr7, uint8_t reg, const uint8_t *data, uint16_t len)
{
    uint16_t nbytes = (uint16_t)(1u + len); /* register-pointer byte + payload */
    uint16_t i;

    if (nbytes > 255u)
    {
        return -1; /* exceeds this peripheral's single-transaction NBYTES limit */
    }

    while ((I2C2->ISR & I2C_ISR_BUSY) != 0u)
    {
        /* wait for a previous transaction to fully release the bus */
    }

    I2C2->CR2 = ((uint32_t)addr7 << (I2C_CR2_SADD_POS + 1)) | ((uint32_t)nbytes << I2C_CR2_NBYTES_POS) |
                I2C_CR2_AUTOEND | I2C_CR2_START;

    if (wait_flag_set(&I2C2->ISR, I2C_ISR_TXIS) < 0)
    {
        return -1;
    }
    I2C2->TXDR = reg;

    for (i = 0u; i < len; i++)
    {
        if (wait_flag_set(&I2C2->ISR, I2C_ISR_TXIS) < 0)
        {
            return -1;
        }
        I2C2->TXDR = data[i];
    }

    if (wait_flag_set(&I2C2->ISR, I2C_ISR_STOPF) < 0)
    {
        return -1;
    }
    I2C2->ICR = I2C_ISR_STOPF; /* clear STOPF (write-1-to-clear on the ICR alias) */
    return 0;
}

int i2c2_read(uint8_t addr7, uint8_t reg, uint8_t *data, uint16_t len)
{
    uint16_t i;

    if (len > 255u)
    {
        return -1;
    }

    while ((I2C2->ISR & I2C_ISR_BUSY) != 0u)
    {
        /* wait for the bus to be free */
    }

    /* Phase 1: write the register pointer, software END (no AUTOEND) so the
     * bus is held for a repeated START instead of releasing it. */
    I2C2->CR2 = ((uint32_t)addr7 << (I2C_CR2_SADD_POS + 1)) | (1u << I2C_CR2_NBYTES_POS) | I2C_CR2_START;

    if (wait_flag_set(&I2C2->ISR, I2C_ISR_TXIS) < 0)
    {
        return -1;
    }
    I2C2->TXDR = reg;

    if (wait_flag_set(&I2C2->ISR, I2C_ISR_TC) < 0)
    {
        return -1;
    }

    /* Phase 2: repeated START into a read of `len` bytes, AUTOEND generates
     * the final STOP automatically. */
    I2C2->CR2 = ((uint32_t)addr7 << (I2C_CR2_SADD_POS + 1)) | ((uint32_t)len << I2C_CR2_NBYTES_POS) |
                I2C_CR2_RD_WRN | I2C_CR2_AUTOEND | I2C_CR2_START;

    for (i = 0u; i < len; i++)
    {
        if (wait_flag_set(&I2C2->ISR, I2C_ISR_RXNE) < 0)
        {
            return -1;
        }
        data[i] = (uint8_t)I2C2->RXDR;
    }

    if (wait_flag_set(&I2C2->ISR, I2C_ISR_STOPF) < 0)
    {
        return -1;
    }
    I2C2->ICR = I2C_ISR_STOPF;
    return 0;
}
