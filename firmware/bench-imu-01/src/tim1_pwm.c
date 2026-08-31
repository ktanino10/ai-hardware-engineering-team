#include "tim1_pwm.h"
#include "stm32g031_regs.h"

#define TIM1_PWM_ARR 799u /* 16,000,000 / 800 = 20,000 Hz exactly (DS-MCU-075) */

void tim1_pwm_init(void)
{
    TIM1->CR1 = 0u; /* disabled while configuring */
    TIM1->PSC = 0u;
    TIM1->ARR = TIM1_PWM_ARR;
    TIM1->CCR1 = 0u; /* 0% duty until commanded -- matches gpio_init()'s PA8 default-safe intent */

    /* CCMR1 CH1: OC1M=110 (PWM Mode 1: output high while CNT < CCR1, i.e.
     * duty cycle = CCR1/(ARR+1)), OC1PE=1 (preload enable -- CCR1 writes
     * take effect at the next update event, not instantaneously mid-period,
     * avoiding a glitched/torn PWM edge on the transaction boundary). */
    TIM1->CCMR1 = TIM_CCMR1_OC1PE | (6u << TIM_CCMR1_OC1M_POS);

    TIM1->CCER = TIM_CCER_CC1E; /* CC1P=0 default: active-high, matches U5 SPEED's expected polarity */
    TIM1->CR1 = TIM_CR1_ARPE;   /* ARR itself also preloaded, pairs with OC1PE above */
    TIM1->EGR = TIM_EGR_UG;     /* force an update event now so PSC/ARR/CCMR1 take effect immediately, not after a full first period */

    TIM1->BDTR = TIM_BDTR_MOE; /* REQUIRED on TIM1 (advanced-control timer): CC1 does not reach PA8 without this, unlike TIM3 */

    TIM1->CR1 |= TIM_CR1_CEN;
}

void tim1_pwm_set_duty_pct(uint32_t duty_pct)
{
    if (duty_pct > 100u)
    {
        duty_pct = 100u;
    }
    TIM1->CCR1 = duty_pct * 8u; /* 0..800 across ARR+1=800 counts -- see tim1_pwm.h for the 100%/CCR1>ARR edge-case note */
}
