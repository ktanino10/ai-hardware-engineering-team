/*
 * motor.c -- see motor.h for the full scope fence, command grammar, CSV
 * schema, REQ-405/406 rationale (including the disclosed 8000->6000 RPM
 * ceiling revision), and BEMF/FG caveat discussion. Only the
 * implementation, the exact numeric derivations, and a few
 * implementation-only design notes (the ring-buffer trace, the RX
 * line-buffering state machine, the status-register caching rationale)
 * live here.
 *
 * No libc string functions are used anywhere in this file (parse_uint(),
 * match_verb_with_arg(), match_bare_word() are hand-rolled), matching this
 * codebase's existing convention (usart2.c's own hand-rolled
 * usart2_write_u32()/usart2_write_i32()).
 */
#include "motor.h"
#include "drv10983.h"
#include "gpio.h"
#include "systick.h"
#include "tim1_pwm.h"
#include "tim3_fg.h"
#include "usart2.h"

/* ------------------------------------------------------------------- *
 * Safety-relevant constants -- see motor.h for the full rationale
 * behind every one of these numbers.
 * ------------------------------------------------------------------- */

/* REQ-405 ceiling. Chosen 6000 RPM: 2.0x margin above REQ-007's >=3000 RPM
 * floor, 3.33-3.7x margin below M1's ~20,000-22,200 RPM no-load speed.
 * Aligns with (does not merely coincide with) the schematic's own Section
 * 7.5.11 "~6000 RPM, 2x the floor" discussion anchor -- see motor.h for
 * the full disclosed reasoning, including this module's own internal
 * first-pass draft of 8000 RPM before that anchor was found and weighed. */
#define MOTOR_OVERSPEED_CEILING_RPM 6000u

/* REQ-406 policy: 3 consecutive qualifying Lock-Detection edges within a
 * rolling 30 s window. Sanity-checked against U5's own tLOCK_OFF=5s
 * auto-retry period (DS-MTR-059): 3 retry cycles need >=15s, leaving
 * comfortable margin inside 30s. */
#define MOTOR_LOCKOUT_FAULT_COUNT 3u
#define MOTOR_LOCKOUT_WINDOW_MS   30000u

/* Bounded grace period after a 0->nonzero SPD command during which "FG has
 * not captured a single edge yet" is treated as a normal spin-up
 * transient rather than a fault. 3000 ms is a firmware-only judgment call
 * (no datasheet gives an expected open-loop ramp time for this specific
 * motor+flywheel+duty-cycle combination) -- chosen to comfortably exceed
 * any plausible ramp time for this bench setup; revisit if real-hardware
 * timing is later measured and found to need more margin. */
#define MOTOR_FG_SPINUP_GRACE_MS 3000u

/* Minimum interval between I2C1 status-register polls for the REQ-406
 * lock-fault check. 50 ms is far slower than I2C1's own transaction time
 * (microseconds) and far faster than anything REQ-406's 30 s window needs
 * -- a firmware-only pacing choice, not a datasheet-derived figure. */
#define MOTOR_STATUS_POLL_MS 50u

/* CSV telemetry period, 5 Hz -- fast enough for a bench operator to watch
 * RPM settle after a SPD change, slow enough not to flood a 115200 baud
 * link shared with the IMU's own 100 Hz CSV stream. */
#define MOTOR_CSV_PERIOD_MS 200u

/* Delay inside REARM between driving SHDN high and attempting to
 * commission U5 over I2C1. NOT datasheet-derived (confirmed this session:
 * datasheets/evidence-log.md's DS-PROT-010 through DS-PROT-031 rows for
 * U6/TPS26631PWPR cover electrical specs, OVP/UVLO, current-limit,
 * inrush-current *equations*, thermal, and MODE/latch behavior -- none
 * cite a specific turn-on/soft-start ramp TIME). Supporting, non-binding
 * evidence found this session: DS-PROT-028's own inrush-control turn-on
 * timing formula, evaluated at this design's own C17=22nF
 * (UVLO_ton(dly) = 742 + 49.5*22 = 1831 us on the slower of its two
 * documented paths), works out to a low single-digit number of
 * milliseconds for U6's own ramp -- this firmware's 100 ms choice is
 * roughly a 50x margin over that figure, which is reassuring but is NOT
 * itself how 100 ms was derived; 100 ms is simply a generously
 * conservative round number chosen to also cover U5's own separate,
 * not-independently-timed post-power-up I2C-readiness delay. Revisit if
 * real-hardware timing is later measured. */
#define MOTOR_REARM_POWERUP_DELAY_MS 100u

/* Host command line buffer. 32 bytes comfortably covers the longest real
 * command ("SPD 100\r\n", 10 bytes) many times over. */
#define MOTOR_RXBUF_LEN 32u

/* ------------------------------------------------------------------- *
 * State (all touched only from ordinary (non-ISR) call context --
 * motor_tick()/motor_handle_rx_byte(), both called only from main.c's
 * superloop, never from an interrupt -- so plain, non-volatile statics
 * are correct here with no atomicity concerns, unlike tim3_fg.c's own
 * ISR-shared state).
 * ------------------------------------------------------------------- */
static uint8_t  s_armed;
static uint8_t  s_fault_latched;
static uint32_t s_duty_pct;
static uint8_t  s_dir_reverse;

/* REQ-405 spin-up-grace-period bookkeeping (see check_overspeed()). */
static uint32_t s_duty_became_nonzero_ms;
static uint8_t  s_ever_fg_valid_since_spinup;

/* REQ-406 lock-event ring buffer, size MOTOR_LOCKOUT_FAULT_COUNT so the
 * buffer capacity and the trip threshold can never drift apart. See
 * check_lock_faults() for the hand-verified ring-buffer trace. */
static uint32_t s_lock_event_ts[MOTOR_LOCKOUT_FAULT_COUNT];
static uint32_t s_lock_event_next_idx;
static uint32_t s_lock_event_filled_count;
static uint8_t  s_was_locked;

/* Cached last-known Status register, populated only by check_lock_faults()
 * while armed. emit_csv_line() consumes this cache instead of issuing its
 * own separate I2C1 read -- avoids doubling I2C1 traffic, and guarantees
 * the CSV's mtrlck field always matches exactly what the safety logic
 * itself most recently observed rather than a second, independently-timed
 * read a few milliseconds apart. */
static uint8_t s_last_status_reg;
static uint8_t s_have_status_reg;

static uint32_t s_last_status_poll_ms;
static uint32_t s_next_csv_ms; /* accumulating target, matching main.c's own next_blink_ms/next_sample_ms pattern -- avoids cumulative drift in the CSV's own timestamp column */

/* Host command RX line buffering. */
static uint8_t  s_rx_buf[MOTOR_RXBUF_LEN];
static uint32_t s_rx_len;
static uint8_t  s_rx_overflow;
static uint8_t  s_last_rx_byte;

/* ------------------------------------------------------------------- *
 * Hand-rolled ASCII parsing helpers (no libc).
 * ------------------------------------------------------------------- */

/* Parses `len` ASCII decimal digits (unsigned, no sign, at least one
 * digit, every character '0'-'9') into *out. Returns 1 on success, 0 on
 * any malformed input. Capped at 9 input digits -- comfortably more than
 * any real argument this protocol ever accepts ("100" is the longest
 * legitimate value) while still rejecting a pathological digit flood
 * before it could overflow a uint32_t. */
static int parse_uint(const uint8_t *s, uint32_t len, uint32_t *out)
{
    uint32_t val = 0u;
    uint32_t i;

    if (len == 0u || len > 9u)
    {
        return 0;
    }
    for (i = 0u; i < len; i++)
    {
        if (s[i] < (uint8_t)'0' || s[i] > (uint8_t)'9')
        {
            return 0;
        }
        val = (val * 10u) + (uint32_t)(s[i] - (uint8_t)'0');
    }
    *out = val;
    return 1;
}

/* If `line` begins with `verb` followed by exactly one ASCII space,
 * points *out_arg at the remaining bytes and sets *out_arg_len, returning
 * 1. Returns 0 on any mismatch (wrong verb, no argument present). */
static int match_verb_with_arg(const uint8_t *line, uint32_t len, const char *verb,
                                const uint8_t **out_arg, uint32_t *out_arg_len)
{
    uint32_t vlen = 0u;
    uint32_t i;

    while (verb[vlen] != '\0')
    {
        vlen++;
    }
    if (len <= vlen)
    {
        return 0; /* too short to hold "verb " plus at least one argument byte */
    }
    for (i = 0u; i < vlen; i++)
    {
        if (line[i] != (uint8_t)verb[i])
        {
            return 0;
        }
    }
    if (line[vlen] != (uint8_t)' ')
    {
        return 0;
    }

    *out_arg = &line[vlen + 1u];
    *out_arg_len = len - vlen - 1u;
    return 1;
}

/* Returns 1 if `line` is exactly the bare word `word` (no argument, no
 * trailing space). */
static int match_bare_word(const uint8_t *line, uint32_t len, const char *word)
{
    uint32_t wlen = 0u;
    uint32_t i;

    while (word[wlen] != '\0')
    {
        wlen++;
    }
    if (len != wlen)
    {
        return 0;
    }
    for (i = 0u; i < wlen; i++)
    {
        if (line[i] != (uint8_t)word[i])
        {
            return 0;
        }
    }
    return 1;
}

/* ------------------------------------------------------------------- *
 * Shared safety-trip path (REQ-405 and REQ-406 both call this).
 * ------------------------------------------------------------------- */

/* Forces the motor to a safe/stopped state (SPEED duty -> 0 AND U6's SHDN
 * -> low, both asserted together -- see motor.h's "COAST-DOWN DISCLOSED
 * LIMITATION" for why both, not just one), latches (clears s_armed, sets
 * s_fault_latched), and reports the reason. A deliberate LATCHING
 * response (not just a momentary zero-then-auto-resume) for both REQ-405
 * and REQ-406 -- see motor.h for why an unlatched response would risk
 * oscillation/thrashing at the ceiling boundary. Recovery requires an
 * explicit REARM (cmd_rearm()) -- never automatic. */
static void trip_safe_state(const char *reason)
{
    tim1_pwm_set_duty_pct(0u);
    motor_shdn_set(0);
    s_duty_pct = 0u;
    s_armed = 0u;
    s_fault_latched = 1u;

    usart2_write_str("MOTOR_TRIP reason=");
    usart2_write_str(reason);
    usart2_write_str(" -- REARM required\r\n");
}

/* ------------------------------------------------------------------- *
 * REQ-405 -- overspeed check.
 * ------------------------------------------------------------------- */

/* Runs whenever armed, REGARDLESS of s_duty_pct (a deliberate refinement:
 * gating this check on "duty != 0" would miss a flywheel coasting down
 * above the ceiling after a plain STOP command, while SHDN is still high
 * and U5/FG are both still fully powered and valid -- STOP alone must not
 * be able to defeat this check). Only the secondary "FG currently
 * invalid" sub-branch below is gated on duty, since an invalid FG reading
 * with zero commanded duty is the ordinary, benign at-rest case. */
static void check_overspeed(uint32_t now)
{
    if (!s_armed)
    {
        return;
    }

    if (tim3_fg_is_valid())
    {
        uint32_t rpm = tim3_fg_get_rpm();

        s_ever_fg_valid_since_spinup = 1u;
        if (rpm > MOTOR_OVERSPEED_CEILING_RPM)
        {
            trip_safe_state("req405_overspeed");
        }
        return;
    }

    if (s_duty_pct == 0u)
    {
        /* FG invalid (stale or never captured) with nothing commanded --
         * the ordinary at-rest case (e.g. freshly armed, motor stopped).
         * Not a fault. */
        return;
    }

    if (s_ever_fg_valid_since_spinup)
    {
        /* FG WAS valid earlier in this spin-up and has since gone stale
         * while duty is still nonzero -- a real regression (FG wiring
         * fault, R6 pull-up failure, U5 fault), not a spin-up transient.
         * Zero grace period: this is exactly the kind of condition
         * REQ-405 must not silently tolerate. */
        trip_safe_state("req405_fg_lost_after_valid");
        return;
    }

    /* FG has never been valid since the current 0->nonzero duty
     * transition. Could be an ordinary, brief spin-up transient (the
     * first FG edge has not arrived yet) or a genuine fault (FG never
     * arrives). Bounded grace period before treating silence as a fault. */
    if ((now - s_duty_became_nonzero_ms) >= MOTOR_FG_SPINUP_GRACE_MS)
    {
        trip_safe_state("req405_fg_never_valid_spinup_timeout");
    }
}

/* ------------------------------------------------------------------- *
 * REQ-406 -- latched lock-fault check.
 * ------------------------------------------------------------------- */

/* Ring-buffer trace (N = MOTOR_LOCKOUT_FAULT_COUNT = 3), hand-verified:
 *   Event A: ts[0]=tA; next_idx=1; filled=1.
 *   Event B: ts[1]=tB; next_idx=2; filled=2.
 *   Event C: ts[2]=tC; next_idx=0; filled=3 -> check: oldest = ts[next_idx=0] = tA. Correct (tA is oldest of {tA,tB,tC}).
 *   Event D (buffer already full): ts[0]=tD (overwrites tA); next_idx=1;
 *     filled stays 3 -> check: oldest = ts[next_idx=1] = tB. Correct (tB
 *     is oldest of the now-current {tB,tC,tD}).
 * i.e. the slot the *next* write would overwrite always holds the oldest
 * of the currently-retained N timestamps -- the standard ring-buffer
 * property this logic relies on. */
static void check_lock_faults(uint32_t now)
{
    uint8_t status_reg;
    uint8_t is_locked;

    if (!s_armed)
    {
        s_have_status_reg = 0u; /* not currently polled -- CSV must report "NA", not a stale last value */
        return;
    }

    if ((now - s_last_status_poll_ms) < MOTOR_STATUS_POLL_MS)
    {
        return;
    }
    s_last_status_poll_ms = now;

    if (drv10983_read_status(&status_reg) != 0)
    {
        /* I2C1 read failure -- reported, but deliberately does NOT
         * auto-trip: a communication failure (transient bus glitch,
         * timing issue) is a different failure mode than an actual motor
         * lock fault, and REQ-406 exists to police the latter. Retried on
         * the very next poll. */
        s_have_status_reg = 0u;
        usart2_write_str("MOTOR_I2C1_STATUS_READ_ERROR\r\n");
        return;
    }
    s_last_status_reg = status_reg;
    s_have_status_reg = 1u;

    is_locked = (status_reg & DRV10983_STATUS_MTRLCK) ? 1u : 0u;

    if (is_locked && !s_was_locked)
    {
        /* A NEW qualifying edge (0->1). A continuously-asserted bit across
         * polls is one ongoing event, not repeated new events -- s_was_locked
         * is what prevents double-counting a single sustained lock. */
        uint8_t fault_reg = 0u;

        if (drv10983_read_fault_code(&fault_reg) == 0)
        {
            usart2_write_str("LOCK_EVENT fault_code_bits=");
            usart2_write_u32((uint32_t)fault_reg);
            usart2_write_str("\r\n");
        }
        else
        {
            usart2_write_str("LOCK_EVENT fault_code_bits=NA(i2c1_read_failed)\r\n");
        }

        s_lock_event_ts[s_lock_event_next_idx] = now;
        s_lock_event_next_idx = (s_lock_event_next_idx + 1u) % MOTOR_LOCKOUT_FAULT_COUNT;
        if (s_lock_event_filled_count < MOTOR_LOCKOUT_FAULT_COUNT)
        {
            s_lock_event_filled_count++;
        }

        if (s_lock_event_filled_count == MOTOR_LOCKOUT_FAULT_COUNT)
        {
            uint32_t oldest_ts = s_lock_event_ts[s_lock_event_next_idx];

            if ((now - oldest_ts) <= MOTOR_LOCKOUT_WINDOW_MS)
            {
                trip_safe_state("req406_lock_fault_threshold");
            }
        }
    }

    s_was_locked = is_locked;
}

/* ------------------------------------------------------------------- *
 * CSV telemetry.
 * ------------------------------------------------------------------- */

/* Schema (see motor.h for the full column rationale):
 *   MOTOR,millis_ms,armed,fault_latched,duty_pct,dir_reverse,fg_valid,rpm,mtrlck,lock_event_count
 * "NA" (not a fabricated 0) is used for rpm (when FG invalid) and mtrlck
 * (when not currently armed/polled) -- reporting a fabricated 0 in place
 * of "unknown" could be misread as an affirmative "confirmed zero
 * RPM"/"confirmed not locked", which would be false and, for mtrlck
 * specifically, actively misleading about safety-relevant state. */
static void emit_csv_line(uint32_t now)
{
    usart2_write_str("MOTOR,");
    usart2_write_u32(now);
    usart2_write_str(",");
    usart2_write_u32((uint32_t)s_armed);
    usart2_write_str(",");
    usart2_write_u32((uint32_t)s_fault_latched);
    usart2_write_str(",");
    usart2_write_u32(s_duty_pct);
    usart2_write_str(",");
    usart2_write_u32((uint32_t)s_dir_reverse);
    usart2_write_str(",");

    if (tim3_fg_is_valid())
    {
        usart2_write_str("1,");
        usart2_write_u32(tim3_fg_get_rpm());
    }
    else
    {
        usart2_write_str("0,NA");
    }
    usart2_write_str(",");

    if (s_have_status_reg)
    {
        usart2_write_u32((s_last_status_reg & DRV10983_STATUS_MTRLCK) ? 1u : 0u);
    }
    else
    {
        usart2_write_str("NA");
    }
    usart2_write_str(",");
    usart2_write_u32(s_lock_event_filled_count);
    usart2_write_str("\r\n");
}

/* ------------------------------------------------------------------- *
 * Host command handlers.
 * ------------------------------------------------------------------- */

static void cmd_spd(uint32_t val)
{
    if (!s_armed)
    {
        usart2_write_str("SPD_REJECTED reason=not_armed\r\n");
        return;
    }

    if (s_duty_pct == 0u && val != 0u)
    {
        /* True 0->nonzero transition: (re)start REQ-405's spin-up
         * grace-period bookkeeping fresh for this new spin-up attempt. */
        s_duty_became_nonzero_ms = millis();
        s_ever_fg_valid_since_spinup = 0u;
    }

    s_duty_pct = val;
    tim1_pwm_set_duty_pct(val);
    usart2_write_str("SPD_OK\r\n");
}

/* DIR is rejected unless duty_pct==0 -- a firmware-only policy (no
 * datasheet requires this). It exists because this bring-up pass has not
 * verified DRV10983's own commutation state machine is safe to reverse
 * while the motor is being actively driven, and this characterization
 * tool has no operational need to reverse under load. */
static void cmd_dir(uint32_t val)
{
    if (!s_armed)
    {
        usart2_write_str("DIR_REJECTED reason=not_armed\r\n");
        return;
    }
    if (s_duty_pct != 0u)
    {
        usart2_write_str("DIR_REJECTED reason=duty_not_zero\r\n");
        return;
    }

    s_dir_reverse = (uint8_t)val;
    motor_dir_set((int)val);
    usart2_write_str("DIR_OK\r\n");
}

/* Always available, even while disarmed (a harmless no-op in that case).
 * Zeroes commanded duty ONLY -- does not disarm, drop SHDN, or require
 * REARM. An operator convenience distinct from a safety trip (note
 * check_overspeed() keeps running afterward regardless, to catch a
 * flywheel coasting down above the ceiling even after STOP). */
static void cmd_stop(void)
{
    s_duty_pct = 0u;
    tim1_pwm_set_duty_pct(0u);
    usart2_write_str("STOP_OK\r\n");
}

/* The single unified arm/re-arm action -- used identically for the very
 * first arm after boot and for recovery after any REQ-405/406 trip (see
 * motor.h for why this symmetry was deliberately chosen). */
static void cmd_rearm(void)
{
    drv10983_status_t status;

    /* Force a known-safe starting point regardless of current state --
     * idempotent even if called while already armed and fine. */
    tim1_pwm_set_duty_pct(0u);
    motor_shdn_set(0);
    s_duty_pct = 0u;

    /* Re-power the motor rail, then give U6's own inrush-limited turn-on
     * ramp and U5's own post-power-up I2C-readiness time to complete
     * before attempting to commission over I2C1 -- see
     * MOTOR_REARM_POWERUP_DELAY_MS above for the full, honestly-disclosed
     * non-datasheet-derived justification for the 100 ms figure. */
    motor_shdn_set(1);
    delay_ms(MOTOR_REARM_POWERUP_DELAY_MS);

    /* Re-commission U5 into PWM speed-control mode -- mandatory every SHDN
     * low->high transition, since U5 itself loses all power (and forgets
     * any prior register-mode commissioning) whenever SHDN is low
     * (drv10983.h's own re-invocation contract). This SHDN toggle also
     * incidentally exercises U6's own documented fault-reset mechanism
     * (DS-PROT-024: "Cycling SHDN pin voltage resets the device that has
     * latched off due to a fault condition") -- so this single REARM
     * sequence uniformly recovers from BOTH this firmware's own REQ-405/
     * 406 latched trips AND U6's own independent hardware overload latch
     * (DS-PROT-030), without motor.c needing to know or care which
     * condition actually caused the rail to be off. A deliberate,
     * favorable design coherence worth recording, not a coincidence this
     * file relies on silently. */
    status = drv10983_commission();
    if (status != DRV10983_OK)
    {
        motor_shdn_set(0);
        usart2_write_str("REARM_FAILED reason=");
        usart2_write_str((status == DRV10983_ERR_I2C) ? "i2c_error" : "verify_mismatch");
        usart2_write_str("\r\n");
        /* Deliberately does NOT set s_fault_latched: a failed REARM
         * *attempt* is a failed recovery, not itself a new safety trip.
         * The operator may simply try REARM again. */
        return;
    }

    /* Commissioning succeeded. U5 has just been fully power-cycled
     * (SHDN low->high) -- every field below describing "the current
     * spin-up/fault session" must be reset here, since the device state
     * they described no longer exists. (A real bug caught and fixed
     * during this module's own design: leaving
     * s_ever_fg_valid_since_spinup=1 from a PREVIOUS session here would
     * remove REQ-405's spin-up grace period on every future spin-up
     * attempt after the first, since check_overspeed() would then treat
     * "FG not yet valid" as an immediate-trip regression instead of a
     * normal transient -- the motor would become unable to ever spin up
     * again after a single trip+REARM cycle.) */
    s_armed = 1u;
    s_fault_latched = 0u;
    s_dir_reverse = 0u;
    motor_dir_set(0); /* reset to a known default (forward) rather than preserving a possibly-forgotten pre-fault direction */
    s_ever_fg_valid_since_spinup = 0u;
    s_lock_event_next_idx = 0u;
    s_lock_event_filled_count = 0u;
    s_was_locked = 0u;
    s_have_status_reg = 0u;
    s_last_status_poll_ms = 0u; /* force check_lock_faults() to poll fresh on the very next motor_tick(), rather than waiting up to MOTOR_STATUS_POLL_MS */

    usart2_write_str("REARM_OK\r\n");
}

/* ------------------------------------------------------------------- *
 * Command dispatch.
 * ------------------------------------------------------------------- */

static void process_line(const uint8_t *line, uint32_t len)
{
    const uint8_t *arg;
    uint32_t arg_len;
    uint32_t val;

    if (len == 0u)
    {
        return; /* a bare blank line is silently ignored, not an error */
    }

    if (match_verb_with_arg(line, len, "SPD", &arg, &arg_len))
    {
        if (!parse_uint(arg, arg_len, &val) || val > 100u)
        {
            usart2_write_str("ERR bad_spd_value\r\n");
            return;
        }
        cmd_spd(val);
        return;
    }

    if (match_verb_with_arg(line, len, "DIR", &arg, &arg_len))
    {
        if (!parse_uint(arg, arg_len, &val) || (val != 0u && val != 1u))
        {
            usart2_write_str("ERR bad_dir_value\r\n");
            return;
        }
        cmd_dir(val);
        return;
    }

    if (match_bare_word(line, len, "STOP"))
    {
        cmd_stop();
        return;
    }

    if (match_bare_word(line, len, "REARM"))
    {
        cmd_rearm();
        return;
    }

    usart2_write_str("ERR unknown_command\r\n");
}

/* ------------------------------------------------------------------- *
 * Public API.
 * ------------------------------------------------------------------- */

void motor_init(void)
{
    s_armed = 0u;
    s_fault_latched = 0u;
    s_duty_pct = 0u;
    s_dir_reverse = 0u;

    s_duty_became_nonzero_ms = 0u;
    s_ever_fg_valid_since_spinup = 0u;

    s_lock_event_next_idx = 0u;
    s_lock_event_filled_count = 0u;
    s_was_locked = 0u;

    s_last_status_reg = 0u;
    s_have_status_reg = 0u;
    s_last_status_poll_ms = 0u;

    s_rx_len = 0u;
    s_rx_overflow = 0u;
    s_last_rx_byte = 0u;

    /* Defensive re-assertion of the hardware-safe state -- gpio_init()/
     * tim1_pwm_init() already default this way (SHDN low via R11's
     * external pulldown, PWM duty 0, DIR forward), but asserting it again
     * here explicitly documents the intended state at the moment motor.c
     * takes ownership, rather than silently relying on another module's
     * own default. */
    motor_shdn_set(0);
    tim1_pwm_set_duty_pct(0u);
    motor_dir_set(0);

    s_next_csv_ms = millis();

    usart2_write_str("\r\n--- Rev 3 Motor Driver + Reaction Wheel: open-loop bring-up ---\r\n");
    usart2_write_str("Scope: open-loop bench characterization ONLY. No PID, no attitude control, no sensor fusion, no IMU cross-wiring.\r\n");
    usart2_write_str("REQ-405 overspeed ceiling: ");
    usart2_write_u32(MOTOR_OVERSPEED_CEILING_RPM);
    usart2_write_str(" RPM (latched trip; REARM required to resume).\r\n");
    usart2_write_str("REQ-406 lock-fault policy: ");
    usart2_write_u32(MOTOR_LOCKOUT_FAULT_COUNT);
    usart2_write_str(" qualifying Lock-Detection events within ");
    usart2_write_u32(MOTOR_LOCKOUT_WINDOW_MS / 1000u);
    usart2_write_str("s -> latched trip; REARM required to resume.\r\n");
    usart2_write_str("NOTE (ECO-008): reported RPM may look visibly noisier, and Lock-Detection events may nuisance-trip more easily, while transiting roughly 500-1500 RPM (BEMF-sensing degrades in that band) -- an expected DRV10983/BEMF characteristic, not a firmware defect.\r\n");
    usart2_write_str("Disarmed at boot -- send REARM to arm.\r\n");
    usart2_write_str("Commands: SPD <0-100>, DIR <0|1>, STOP, REARM\r\n");
    usart2_write_str("MOTOR,millis_ms,armed,fault_latched,duty_pct,dir_reverse,fg_valid,rpm,mtrlck,lock_event_count\r\n");
}

void motor_handle_rx_byte(uint8_t b)
{
    uint8_t is_term = (b == (uint8_t)'\r' || b == (uint8_t)'\n') ? 1u : 0u;

    if (is_term)
    {
        /* Treat \r\n or \n\r as ONE line-ending event: if the immediately
         * preceding byte was the OTHER terminator character, this byte is
         * just the second half of that same CRLF/LFCR pair -- consume it
         * without dispatching a second, spurious empty line. Also
         * correctly handles bare-CR-only or bare-LF-only terminals (each
         * byte terminates its own line, since s_last_rx_byte will not
         * match the "other" terminator in that case). */
        uint8_t was_term_pair = ((s_last_rx_byte == (uint8_t)'\r' && b == (uint8_t)'\n') ||
                                  (s_last_rx_byte == (uint8_t)'\n' && b == (uint8_t)'\r'))
                                     ? 1u
                                     : 0u;
        s_last_rx_byte = b;

        if (was_term_pair)
        {
            return;
        }

        if (s_rx_overflow)
        {
            usart2_write_str("ERR line_too_long\r\n");
            s_rx_overflow = 0u;
        }
        else
        {
            process_line(s_rx_buf, s_rx_len);
        }
        s_rx_len = 0u;
        return;
    }

    s_last_rx_byte = b;

    if (s_rx_overflow)
    {
        return; /* already discarding this over-long line until its terminator */
    }

    if (s_rx_len >= MOTOR_RXBUF_LEN)
    {
        s_rx_overflow = 1u;
        return;
    }

    s_rx_buf[s_rx_len] = b;
    s_rx_len++;
}

void motor_tick(uint32_t now_ms)
{
    /* Safety checks run every call, unconditionally -- never rate-limited
     * or skipped, unlike the CSV telemetry below. */
    check_overspeed(now_ms);
    check_lock_faults(now_ms);

    if ((int32_t)(now_ms - s_next_csv_ms) >= 0)
    {
        emit_csv_line(now_ms);
        s_next_csv_ms += MOTOR_CSV_PERIOD_MS;
    }
}
