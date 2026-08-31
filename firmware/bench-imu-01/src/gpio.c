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

    /* PA11 = I2C2_SCL, PA12 = I2C2_SDA, both AF6 on this part (DS-MCU-073,
     * cross-corroborated DS-MCU-067). CORRECTED pin assignment: PB10/PB11
     * (this firmware's previous configuration) are NOT bonded out on the
     * STM32G031K8T6's actual LQFP-32/UFQFPN32 package -- confirmed CRITICAL
     * defect ISS-027 (validation/open-issues.md, RESOLVED at hardware/
     * schematic level; corrected schematic hardware/schematic/
     * bench-imu-01-design.md Section 5/7.5.4/Section 11 pin table now
     * specifies PA11/PA12). Same I2C2 peripheral instance, same AF6 value,
     * same open-drain treatment as before -- only the port letter and pin
     * numbers change (GPIOB->GPIOA, 10/11->11/12); I2C2's own base address
     * in stm32g031_regs.h is unaffected (still correctly I2C2, not I2C1 --
     * that is a separate, already-resolved defect, ISS-011). Open-drain:
     * required for I2C, and consistent with the schematic's own external
     * R3/R4 pull-ups -- do not enable an internal pull-up here, it would
     * work against R3/R4's calculated value (Section 5.2). */
    set_moder(GPIOA, 11u, GPIO_MODER_AF);
    set_af(GPIOA, 11u, 6u);
    set_open_drain(GPIOA, 11u, 1);
    set_moder(GPIOA, 12u, GPIO_MODER_AF);
    set_af(GPIOA, 12u, 6u);
    set_open_drain(GPIOA, 12u, 1);

    /* --- Rev 3 motor subsystem (DRV10983 U5 + TPS26631PWPR U6) ---------- */
    /* All 5 pins below are cited to DS-MCU-069/070/071 (Circuit Engineer,
     * 2026-09-04) and hardware/schematic/bench-imu-01-design.md Section 7.5
     * -- see motor.h/tim1_pwm.h/tim3_fg.h/i2c1.h for the peripheral-level
     * rationale behind each. This function only performs the pin muxing;
     * peripheral (TIM1/TIM3/I2C1) register configuration lives in their own
     * driver modules, matching this file's existing division of labour
     * (gpio.c mux only, i2c2.c/usart2.c own their peripheral registers). */

    /* PA8 = TIM1_CH1 (AF2) -- SPEED (PWM command to U5). Push-pull (a PWM
     * drive output, not a bus), no pull needed. */
    set_moder(GPIOA, 8u, GPIO_MODER_AF);
    set_af(GPIOA, 8u, 2u);

    /* PA6 = TIM3_CH1 (AF1) -- FG tach input from U5, R6 external pull-up
     * already on the schematic (Section 7.5.4/7.5.9) since U5's FG output is
     * open-drain. Configured as an input via the AF mux (TIM3 owns the
     * input-capture direction internally); no internal pull enabled here,
     * matching the same "do not fight an already-sized external pull"
     * discipline as the I2C bus pins above. */
    set_moder(GPIOA, 6u, GPIO_MODER_AF);
    set_af(GPIOA, 6u, 1u);

    /* PB1 = DIR (plain GPIO output to U5). Push-pull, default LOW at boot
     * (motor.c's default direction convention; see motor.h). */
    set_moder(GPIOB, 1u, GPIO_MODER_OUTPUT);
    set_open_drain(GPIOB, 1u, 0);
    GPIOB->ODR &= ~(1u << 1); /* DIR = 0 at boot, matches CCR1=0 (stopped) */

    /* PB6 = I2C1_SCL, PB7 = I2C1_SDA (both AF6) -- U5's own commissioning/
     * status I2C bus. Open-drain, no internal pull (schematic Section 7.5.4
     * places its own external pull-ups on this bus, same reasoning as the
     * I2C2 bus above). */
    set_moder(GPIOB, 6u, GPIO_MODER_AF);
    set_af(GPIOB, 6u, 6u);
    set_open_drain(GPIOB, 6u, 1);
    set_moder(GPIOB, 7u, GPIO_MODER_AF);
    set_af(GPIOB, 7u, 6u);
    set_open_drain(GPIOB, 7u, 1);

    /* PA9 = U6 (TPS26631PWPR) SHDN -- plain GPIO output, push-pull. Default
     * LOW at boot (motor rail OFF): R11's external pulldown already makes
     * this the hardware default before firmware ever runs (DS-MCU-072 --
     * PA9 resets to Analog/no-pull, R11 dominates with ~8x/~20x margin), and
     * this firmware preserves that fail-safe intent (REQ-403) by driving PA9
     * LOW explicitly rather than leaving it floating/Analog once GPIO clock
     * + MODER take effect, so there is never a window where PA9 is
     * configured as an output with an unintended HIGH/undefined level. */
    set_moder(GPIOA, 9u, GPIO_MODER_OUTPUT);
    set_open_drain(GPIOA, 9u, 0);
    GPIOA->ODR &= ~(1u << 9); /* SHDN = LOW (motor rail disabled) at boot */
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

void motor_dir_set(int reverse)
{
    if (reverse)
    {
        GPIOB->BSRR = (1u << 1);        /* set PB1 */
    }
    else
    {
        GPIOB->BSRR = (1u << (1 + 16)); /* reset PB1 (BSRR upper half) */
    }
}

void motor_shdn_set(int enable)
{
    if (enable)
    {
        GPIOA->BSRR = (1u << 9);        /* set PA9 */
    }
    else
    {
        GPIOA->BSRR = (1u << (9 + 16)); /* reset PA9 (BSRR upper half) */
    }
}
