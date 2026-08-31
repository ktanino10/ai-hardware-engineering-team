#include "tim3_fg.h"
#include "stm32g031_regs.h"
#include "systick.h"

/* See tim3_fg.h for the full PSC=159/10 us-tick wraparound-safety
 * rationale and the RPM-formula derivation; only the numeric constants and
 * the interrupt implementation live here. */
#define TIM3_FG_RPM_CONST 857143UL /* round(60 * 100000 / 7); 7 pole pairs, 100 kHz (10 us) tick rate */
#define TIM3_FG_STALE_MS  250u
/* 250 ms sits comfortably inside the 655.36 ms single-wrap-safe window at
 * PSC=159 (a ~2.6x margin) -- tim3_fg_is_valid() always goes false, using
 * the independent millis() clock, well before a real capture-to-capture
 * interval could reach the point where the 16-bit counter itself would
 * have wrapped and silently corrupted a stored delta. It is also
 * comfortably above the FG period at any operationally relevant RPM
 * (500 RPM -> ~17.2 ms period; even 100 RPM -> ~85.7 ms), so normal
 * slow-speed/spin-up operation is never spuriously flagged stale.
 * (Note, and a second independent reason PSC=159 was chosen over the
 * originally-considered PSC=15/1 us-tick alternative: under that finer
 * tick, this same 250 ms constant would have EXCEEDED its 65.536 ms
 * wraparound period -- staleness detection would then arrive too late to
 * catch a wraparound that had already silently corrupted a reading, which
 * is exactly backwards from what a staleness check must guarantee.) */

/* Plain `volatile uint32_t` statics, individually, not a packed struct --
 * matches systick.c's own g_millis treatment. Each field is a single
 * naturally-aligned 32-bit word, atomically read/written on this
 * single-core Cortex-M0+, so the ISR and the accessor functions below
 * cannot observe a torn value; no extra locking is needed for a
 * single-priority-level bring-up program with no nested nesting between
 * TIM3's and SysTick's interrupts beyond what the NVIC already handles
 * safely on its own. */
static volatile uint32_t s_last_ccr1;
static volatile uint32_t s_last_rpm;
static volatile uint32_t s_last_capture_ms;
static volatile uint8_t  s_has_captured;

void TIM3_IRQHandler(void); /* referenced from the vector table in startup_stm32g031xx.c */

void tim3_fg_init(void)
{
    TIM3->PSC = 159u;                         /* 16 MHz / 160 = 100 kHz, 10 us/tick */
    TIM3->ARR = 0xFFFFu;                      /* free-running over the full 16-bit range */
    TIM3->CCMR1 = (1u << TIM_CCMR1_CC1S_POS); /* CC1S=01: IC1 mapped on TI1 (PA6) */
    TIM3->CCER = TIM_CCER_CC1E;               /* capture enabled; CC1P=0 (reset default) = rising edge, FG's own active edge */
    TIM3->EGR = TIM_EGR_UG;                   /* force PSC/ARR to load immediately (same pattern as tim1_pwm.c); also clears CNT, harmless before any real capture has occurred */
    TIM3->DIER = TIM_DIER_CC1IE;              /* enable the CC1 capture interrupt (DS-MCU-076) */
    NVIC_ISER = (1UL << TIM3_IRQn);           /* unmask TIM3's IRQ at the NVIC (IRQn 16, DS-MCU-076) -- configure everything above first, unmask last */
    TIM3->CR1 = TIM_CR1_CEN;                  /* start counting -- last step of all, after the interrupt path is fully wired */
}

void TIM3_IRQHandler(void)
{
    /* Reading CCR1 both retrieves the captured tick value AND clears
     * CC1IF as a hardware side effect (DS-MCU-075) -- no separate
     * flag-clear write is needed or correct to add here. */
    uint32_t captured = TIM3->CCR1;
    /* Wraparound-safe 16-bit modular subtraction, done in a wider (32-bit)
     * intermediate then masked back down -- see tim3_fg.h for why this is
     * only safe up to the 655.36 ms single-wrap window (PSC=159). */
    uint32_t delta = (captured - s_last_ccr1) & 0xFFFFu;

    if (s_has_captured && delta != 0u)
    {
        s_last_rpm = TIM3_FG_RPM_CONST / delta;
    }
    /* If this is the very first capture ever (s_has_captured==0) or, in
     * the vanishingly unlikely case, two captures land on the identical
     * tick (delta==0), there is no physically meaningful instantaneous
     * RPM to compute from a single edge alone -- s_last_rpm is simply
     * left at its previous value (0 on the very first capture, since it
     * is zero-initialized static storage) rather than risking a
     * divide-by-zero. */

    s_last_ccr1 = captured;
    s_last_capture_ms = millis();
    s_has_captured = 1u;
}

uint32_t tim3_fg_get_rpm(void)
{
    if (!s_has_captured)
    {
        return 0u;
    }
    return s_last_rpm;
}

uint32_t tim3_fg_is_valid(void)
{
    if (!s_has_captured)
    {
        return 0u; /* never captured a single edge -- nothing to trust yet */
    }
    return ((millis() - s_last_capture_ms) <= TIM3_FG_STALE_MS) ? 1u : 0u;
}

uint32_t tim3_fg_last_capture_ms(void)
{
    return s_last_capture_ms;
}
