#include "clock.h"
#include "stm32g031_regs.h"

void clock_init(void)
{
    /* GPIOA (PA2/PA3 USART2, PA5 LED, PA6/PA8/PA9 motor, PA11/PA12 I2C2) and
     * GPIOB (PB1/PB6/PB7 motor) clocks. GPIOB is enabled for the Rev 3 motor
     * subsystem's DIR/I2C1 pins -- it is NOT needed by the IMU bus any more
     * (I2C2 moved from PB10/PB11 to PA11/PA12 this cycle, ISS-027 -- the
     * same GPIO-port/pin fix independently arrived at, and corroborated
     * against two further official ST sources, by origin/main's own
     * parallel fix, DS-MCU-068/077; see gpio.h and gpio.c). If the motor
     * subsystem is ever removed, this GPIOBEN bit would need to be
     * reconsidered, not left enabled "just in case". */
    RCC->IOPENR |= RCC_IOPENR_GPIOAEN | RCC_IOPENR_GPIOBEN;

    /* I2C2 (IMU), I2C1 (DRV10983 U5 commissioning/status), USART2 (host
     * link), and PWR (needed to read/clear reset-reason flags via RCC_CSR
     * at boot -- see reset_reason.c) peripheral clocks, all on APB1. */
    RCC->APBENR1 |= RCC_APBENR1_I2C2EN | RCC_APBENR1_I2C1EN | RCC_APBENR1_USART2EN |
                    RCC_APBENR1_PWREN | RCC_APBENR1_TIM3EN;

    /* TIM1 (SPEED PWM generation) is on APB2, a separate enable register. */
    RCC->APBENR2 |= RCC_APBENR2_TIM1EN;

    /* Dummy read-back: the reference manual requires a delay of at least
     * one peripheral clock cycle between enabling a peripheral clock and
     * accessing that peripheral's registers, satisfied by reading the
     * enable register back before returning. */
    (void)RCC->APBENR1;
    (void)RCC->APBENR2;
}
