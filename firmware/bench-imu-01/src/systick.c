#include "systick.h"
#include "stm32g031_regs.h"

static volatile uint32_t g_millis;

void SysTick_Handler(void); /* referenced from the vector table in startup_stm32g031xx.c */

void systick_init(void)
{
    /* 16,000,000 Hz / 1000 = 16000 cycles per 1 ms tick; SysTick reloads
     * from (LOAD + 1) cycles, so LOAD = 16000 - 1. */
    SysTick->LOAD = 16000u - 1u;
    SysTick->VAL = 0u;
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE | SysTick_CTRL_TICKINT | SysTick_CTRL_ENABLE;
}

void SysTick_Handler(void)
{
    g_millis++;
}

uint32_t millis(void)
{
    return g_millis;
}

void delay_ms(uint32_t ms)
{
    uint32_t start = millis();
    while ((millis() - start) < ms)
    {
        /* busy-wait; fine for a single-threaded bring-up program */
    }
}
