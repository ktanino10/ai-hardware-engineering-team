/*
 * startup_stm32g031xx.c -- minimal Cortex-M0+ reset/vector-table startup for
 * Bench-IMU-01, written in C (not assembly) to keep this small bring-up
 * firmware's toolchain-risk surface as low as possible -- the
 * function-pointer vector table + explicit .data/.bss copy loop below is a
 * standard, well-established technique for Cortex-M parts and needs no
 * assembler-specific syntax.
 *
 * Vector table layout (table index -> meaning) is the ARMv6-M architectural
 * exception table (indices 0-15, fixed for every Cortex-M0+ part, not
 * ST-specific) followed by STM32G031's own device interrupt list (index 16+,
 * confirmed this session against ST's official CMSIS header,
 * cmsis_device_g0/Include/stm32g031xx.h "IRQn_Type" -- sized through index
 * 16+29 to cover every IRQn that header defines for this part, even though
 * this polling-only firmware never unmasks any of them at the NVIC).
 */
#include <stdint.h>

extern uint32_t _estack;
extern uint32_t _sidata;
extern uint32_t _sdata;
extern uint32_t _edata;
extern uint32_t _sbss;
extern uint32_t _ebss;

void Reset_Handler(void);
void Default_Handler(void);
extern void SysTick_Handler(void); /* real implementation in systick.c */

int main(void);

typedef void (*isr_handler_t)(void);

__attribute__((section(".isr_vector"))) const isr_handler_t g_pfnVectors[] = {
    (isr_handler_t)&_estack, /* 0:  initial stack pointer */
    Reset_Handler,           /* 1 */
    Default_Handler,         /* 2:  NMI -- never triggered by anything this firmware configures */
    Default_Handler,         /* 3:  HardFault -- a real fault here means a genuine firmware bug; looping in
                              *     Default_Handler is a deliberately simple, honest "something is wrong,
                              *     stop" rather than attempting fault recovery this small bring-up program
                              *     has no use for. */
    0, 0, 0, 0, 0, 0, 0,     /* 4-10: reserved on Cortex-M0+ */
    Default_Handler,         /* 11: SVCall -- unused, no RTOS/supervisor calls in this firmware */
    0, 0,                    /* 12-13: reserved */
    Default_Handler,         /* 14: PendSV -- unused */
    SysTick_Handler,         /* 15: SysTick -- the real 1 ms tick handler (systick.c) */
    /* Device interrupts (IRQn 0.. per stm32g031xx.h); all Default_Handler
     * since this firmware polls I2C2/USART2 rather than using interrupts,
     * matching the schematic's own polled-acquisition design decision
     * (hardware/schematic/bench-imu-01-design.md Section 5.3). */
    Default_Handler, /* 16: IRQ0  WWDG */
    Default_Handler, /* 17: IRQ1  PVD */
    Default_Handler, /* 18: IRQ2  RTC_TAMP */
    Default_Handler, /* 19: IRQ3  FLASH */
    Default_Handler, /* 20: IRQ4  RCC */
    Default_Handler, /* 21: IRQ5  EXTI0_1 */
    Default_Handler, /* 22: IRQ6  EXTI2_3 */
    Default_Handler, /* 23: IRQ7  EXTI4_15 */
    0,                /* 24: IRQ8  reserved on this part */
    Default_Handler, /* 25: IRQ9  DMA1_Channel1 */
    Default_Handler, /* 26: IRQ10 DMA1_Channel2_3 */
    Default_Handler, /* 27: IRQ11 DMA1_Ch4_5_DMAMUX1_OVR */
    Default_Handler, /* 28: IRQ12 ADC1 */
    Default_Handler, /* 29: IRQ13 TIM1_BRK_UP_TRG_COM */
    Default_Handler, /* 30: IRQ14 TIM1_CC */
    Default_Handler, /* 31: IRQ15 TIM2 */
    Default_Handler, /* 32: IRQ16 TIM3 */
    Default_Handler, /* 33: IRQ17 LPTIM1 */
    Default_Handler, /* 34: IRQ18 LPTIM2 */
    Default_Handler, /* 35: IRQ19 TIM14 */
    0,                /* 36: IRQ20 reserved on this part */
    Default_Handler, /* 37: IRQ21 TIM16 */
    Default_Handler, /* 38: IRQ22 TIM17 */
    Default_Handler, /* 39: IRQ23 I2C1 (combined with EXTI23) */
    Default_Handler, /* 40: IRQ24 I2C2 -- polled, not enabled at the NVIC (i2c2.c) */
    Default_Handler, /* 41: IRQ25 SPI1 */
    Default_Handler, /* 42: IRQ26 SPI2 */
    Default_Handler, /* 43: IRQ27 USART1 */
    Default_Handler, /* 44: IRQ28 USART2 -- polled, not enabled at the NVIC (usart2.c) */
    Default_Handler, /* 45: IRQ29 LPUART1 (combined with EXTI28) */
};

void Reset_Handler(void)
{
    uint32_t *src;
    uint32_t *dst;

    /* Copy .data's initial values out of Flash into RAM. */
    src = &_sidata;
    dst = &_sdata;
    while (dst < &_edata)
    {
        *dst++ = *src++;
    }

    /* Zero .bss. */
    dst = &_sbss;
    while (dst < &_ebss)
    {
        *dst++ = 0u;
    }

    main();

    /* main() is not expected to return (it is an infinite loop, see
     * main.c). If it somehow does, stop rather than run off into undefined
     * memory. */
    for (;;)
    {
    }
}

void Default_Handler(void)
{
    for (;;)
    {
        /* Deliberately do nothing else -- see the HardFault_Handler comment
         * above in the vector table for why this firmware doesn't attempt
         * fault recovery. */
    }
}
