#include "gpio.h"
#include "stm32g031_regs.h"

#define GPIO_MODER_INPUT  0x0u
#define GPIO_MODER_OUTPUT 0x1u
#define GPIO_MODER_AF     0x2u
#define GPIO_MODER_ANALOG 0x3u

static void set_moder(GPIO_TypeDef *port, unsigned pin, unsigned mode)
{
    port->MODER = (port->MODER & ~(0x3u << (pin * 2u))) | (mode << (pin * 2u));
}

static void set_af(GPIO_TypeDef *port, unsigned pin, unsigned af)
{
    unsigned idx = pin / 8u;       /* 0 = AFRL (pins 0-7), 1 = AFRH (pins 8-15) */
    unsigned shift = (pin % 8u) * 4u;
    port->AFR[idx] = (port->AFR[idx] & ~(0xFu << shift)) | ((af & 0xFu) << shift);
}

static void set_open_drain(GPIO_TypeDef *port, unsigned pin, int open_drain)
{
    if (open_drain)
    {
        port->OTYPER |= (1u << pin);
    }
    else
    {
        port->OTYPER &= ~(1u << pin);
    }
}

void gpio_init(void)
{
    /* PA5: plain push-pull output for the status/heartbeat LED (D1/R5). */
    set_moder(GPIOA, 5u, GPIO_MODER_OUTPUT);
    set_open_drain(GPIOA, 5u, 0);
    GPIOA->ODR &= ~(1u << 5); /* start LED off */

    /* PA2 = USART2_TX, PA3 = USART2_RX, both AF1 on this part
     * (confirmed this session against ST's alternate-function table for
     * STM32G0; matches the schematic's own PA2/PA3 USART2 assignment,
     * Section 6). USART pins are push-pull, not open-drain. */
    set_moder(GPIOA, 2u, GPIO_MODER_AF);
    set_af(GPIOA, 2u, 1u);
    set_moder(GPIOA, 3u, GPIO_MODER_AF);
    set_af(GPIOA, 3u, 1u);

    /* PB10 = I2C2_SCL, PB11 = I2C2_SDA, both AF6 on this part (confirmed
     * this session -- this is the pin pair the schematic's Hardware
     * Reviewer independently re-verified maps to I2C2, not I2C1, correcting
     * ISS-011; getting this AF value right, on top of the correct I2C2
     * register base address in stm32g031_regs.h, is the firmware-layer half
     * of not repeating that defect). Open-drain: required for I2C, and
     * consistent with the schematic's own external R3/R4 pull-ups -- do not
     * enable an internal pull-up here, it would work against R3/R4's
     * calculated value (Section 5.2). */
    set_moder(GPIOB, 10u, GPIO_MODER_AF);
    set_af(GPIOB, 10u, 6u);
    set_open_drain(GPIOB, 10u, 1);
    set_moder(GPIOB, 11u, GPIO_MODER_AF);
    set_af(GPIOB, 11u, 6u);
    set_open_drain(GPIOB, 11u, 1);
}

void led_set(int on)
{
    if (on)
    {
        GPIOA->BSRR = (1u << 5);        /* set PA5 */
    }
    else
    {
        GPIOA->BSRR = (1u << (5 + 16)); /* reset PA5 (BSRR upper half) */
    }
}

void led_toggle(void)
{
    GPIOA->ODR ^= (1u << 5);
}
