#include "usart2.h"
#include "stm32g031_regs.h"
#include <stdint.h>

void usart2_init(void)
{
    /* BRR = fCK / baud, the standard STM32 USART formula for the default
     * 16x-oversampling mode (OVER8=0, CR1 bit 15 left at its reset value of
     * 0 -- not explicitly written here). fCK = 16 MHz (HSI16, no PLL,
     * clock.c). BRR = 16,000,000 / 115200 = 138.9 -> 139 (achieves
     * 115,107.9 baud actual, ~0.08% error -- well within standard UART
     * tolerance for a short point-to-point link, consistent with the
     * schematic's own Section 6 rationale that HSI16's tolerance is
     * adequate at typical baud rates without an external crystal). */
    USART2->BRR = 139u;

    /* 8 data bits, no parity, 1 stop bit is the USART's reset-default frame
     * format (CR1 M0/M1 = 0, CR2 STOP = 0) -- nothing to configure for 8N1
     * specifically, only enable the peripheral, transmitter, and receiver. */
    USART2->CR1 = USART_CR1_UE | USART_CR1_TE | USART_CR1_RE;
}

void usart2_write_byte(uint8_t b)
{
    while ((USART2->ISR & USART_ISR_TXE) == 0)
    {
        /* wait for the transmit data register to be empty */
    }
    USART2->TDR = b;
}

void usart2_write_str(const char *s)
{
    while (*s != '\0')
    {
        usart2_write_byte((uint8_t)*s);
        s++;
    }
}

void usart2_write_u32(uint32_t v)
{
    char buf[10]; /* max 10 digits for a 32-bit unsigned value */
    int i = 0;

    if (v == 0u)
    {
        usart2_write_byte('0');
        return;
    }

    while (v > 0u)
    {
        buf[i++] = (char)('0' + (v % 10u));
        v /= 10u;
    }
    while (i > 0)
    {
        i--;
        usart2_write_byte((uint8_t)buf[i]);
    }
}

void usart2_write_i32(int32_t v)
{
    if (v < 0)
    {
        usart2_write_byte('-');
        /* Cast through uint32_t to safely negate INT32_MIN as well. */
        usart2_write_u32((uint32_t)(-(int64_t)v));
    }
    else
    {
        usart2_write_u32((uint32_t)v);
    }
}

int usart2_read_byte(uint8_t *out)
{
    if ((USART2->ISR & USART_ISR_RXNE) == 0u)
    {
        return 0;
    }
    *out = (uint8_t)USART2->RDR; /* reading RDR clears RXNE */
    return 1;
}
