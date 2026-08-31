#include "clock.h"
#include "stm32g031_regs.h"

void clock_init(void)
{
    /* GPIOA (PA2/PA3 USART2, PA5 LED) and GPIOB (PB10/PB11 I2C2) clocks. */
    RCC->IOPENR |= RCC_IOPENR_GPIOAEN | RCC_IOPENR_GPIOBEN;

    /* I2C2, USART2, and PWR (needed to read/clear reset-reason flags via
     * RCC_CSR at boot -- see reset_reason.c) peripheral clocks. */
    RCC->APBENR1 |= RCC_APBENR1_I2C2EN | RCC_APBENR1_USART2EN | RCC_APBENR1_PWREN;

    /* Dummy read-back: the reference manual requires a delay of at least
     * one peripheral clock cycle between enabling a peripheral clock and
     * accessing that peripheral's registers, satisfied by reading the
     * enable register back before returning. */
    (void)RCC->APBENR1;
}
