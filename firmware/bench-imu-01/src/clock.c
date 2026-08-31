#include "clock.h"
#include "stm32g031_regs.h"

void clock_init(void)
{
    /* GPIOA only -- PA2/PA3 (USART2), PA5 (LED), and PA11/PA12 (I2C2).
     * Corrected this revision (ISS-014): the IMU's I2C2 bus previously lived
     * on PB10/PB11, which do not physically exist on this package; the real
     * pins (PA11/PA12) are also on GPIOA, so GPIOB is no longer used
     * anywhere in this board's real pin allocation and its clock is
     * deliberately not enabled here. */
    RCC->IOPENR |= RCC_IOPENR_GPIOAEN;

    /* I2C2, USART2, and PWR (needed to read/clear reset-reason flags via
     * RCC_CSR at boot -- see reset_reason.c) peripheral clocks. */
    RCC->APBENR1 |= RCC_APBENR1_I2C2EN | RCC_APBENR1_USART2EN | RCC_APBENR1_PWREN;

    /* Dummy read-back: the reference manual requires a delay of at least
     * one peripheral clock cycle between enabling a peripheral clock and
     * accessing that peripheral's registers, satisfied by reading the
     * enable register back before returning. */
    (void)RCC->APBENR1;
}
