/*
 * tim3_fg.h -- TIM3 input-capture driver for U5 (DRV10983)'s FG (tachometer)
 * output, PA6/TIM3_CH1, via R6's pull-up (hardware/schematic/
 * bench-imu-01-design.md Section 7.5.4). This is the FG *signal-capture*
 * layer only: it converts raw edge-to-edge timer ticks into an RPM number.
 * motor.c is the only caller, and owns all RPM-derived *decisions*
 * (REQ-405 overspeed cutoff, CSV reporting, the BEMF-degraded-zone caveat)
 * -- this file has no notion of "safe" or "unsafe" speed.
 *
 * -----------------------------------------------------------------------
 * WHY INTERRUPT-DRIVEN, NOT POLLED (a real design correction made during
 * this bring-up pass -- the first implementation attempt was a polled
 * design and was rejected before being finished; see DS-MCU-076):
 *
 * FG is a fixed-duty square wave whose frequency is proportional to actual
 * electrical RPM (7 pole pairs, per the schematic/DS-MTR-05x's own no-load
 * speed derivation). At this motor's structural top speed (~20,000 RPM
 * no-load, DS-MTR-05x), FG's electrical frequency is
 * 20000 * 7 / 60 =~ 2333 Hz, i.e. a period of only ~0.43 ms. A capture
 * register (TIM3->CCR1) latches only the *most recent* edge's timer count
 * -- if the main superloop polls it on any period slower than the FG
 * period (and every practical superloop period this firmware could offer,
 * even the 1 ms SysTick tick, is slower once RPM climbs past ~4300 RPM),
 * one or more real edges between polls are silently overwritten and lost.
 * The computed "delta" then spans several true FG periods rather than one,
 * so the resulting RPM = 857143 / delta comes out FALSELY LOW -- exactly
 * backwards from safe: REQ-405's overspeed cutoff trusts this RPM number
 * to detect and react to an overspeed condition, so a measurement method
 * that can under-report RPM at the exact moment overspeed detection matters
 * most is not acceptable for a safety-relevant reading.
 *
 * The fix is to let TIM3's own capture-compare-1 interrupt (DIER.CC1IE,
 * NVIC IRQn 16, DS-MCU-076) read CCR1 and compute the delta the instant
 * each capture event occurs, in TIM3_IRQHandler() below -- this is
 * correct at any RPM up to the timer's own maximum capture rate (many
 * orders of magnitude above anything this motor can physically produce),
 * because it is not gated by superloop timing at all. motor.c's polling
 * loop only ever reads the *already-computed* result
 * (tim3_fg_get_rpm()/tim3_fg_is_valid()) -- no RPM math happens outside
 * the ISR.
 *
 * This is NOT a reversal of this codebase's "polling, not interrupt-driven"
 * philosophy for IMU data acquisition (schematic Section 5.3 -- an
 * unrelated design choice specific to the BMI270 sensor-read path) and has
 * direct, working precedent in this same firmware's pre-existing
 * SysTick_Handler ISR (systick.c). Two ISRs in a ~15-source-file bring-up
 * program is a modest, well-justified addition, not a wholesale
 * architecture change.
 * -----------------------------------------------------------------------
 *
 * TIMER CONFIGURATION (PSC=159, i.e. 10 us/tick -- a deliberate choice over
 * the finer-grained PSC=15/1 us-tick alternative, see the wraparound-safety
 * trade-off below):
 *   TIM3 is a 16-bit counter (CNT/ARR/CCR1 all 16-bit, DS-MCU-075). At
 *   PSC=159 (100 kHz tick rate, exact division of the 16 MHz HSI16 core
 *   clock: 16,000,000 / 160 = 100,000), ARR=0xFFFF gives a free-running
 *   wraparound period of 65536 * 10 us = 655.36 ms -- i.e. the counter can
 *   go a full 655 ms between captures before a *single* wraparound would
 *   corrupt the unsigned-subtraction delta (a second wraparound within one
 *   capture-to-capture interval would silently alias to a too-small delta,
 *   which is the double-wrap failure mode this margin exists to avoid).
 *   655.36 ms corresponds to a mechanical RPM floor of
 *   60 / (655.36e-3 * 7) =~ 13 RPM (7 pole pairs) -- comfortably below any
 *   realistic sustained low-RPM dwell point for this motor (even a slow,
 *   controlled spin-up ramp does not linger for hundreds of milliseconds
 *   per single electrical revolution at such a low speed).
 *
 *   The originally-considered PSC=15 (1 us/tick) alternative was rejected:
 *   its wraparound period is only 65536 * 1 us = 65.5 ms, single-wrap-safe
 *   only down to ~131 RPM mechanical -- too close to the
 *   BEMF-degraded-below-500-1500-RPM zone (ECO-008) and the FG-staleness
 *   floor below for comfortable margin, leaving a real (if narrow) gap
 *   where a double-wrap could alias to a plausible-looking but wrong RPM
 *   value without tripping the staleness timeout in tim3_fg_is_valid().
 *   The trade-off accepted by choosing the coarser PSC=159 tick is worse
 *   quantization resolution at high RPM (~1-2% error at 8000-20000 RPM,
 *   vs. sub-1% with the finer tick) -- judged acceptable for an open-loop
 *   bench-characterization tool and for a safety CUTOFF that already
 *   carries engineered margin (REQ-405's own ceiling, motor.c, sits well
 *   below the motor's structural limit specifically to absorb this kind
 *   of measurement slack).
 *
 *   RPM formula: rpm = 857143 / delta_ticks, where 857143 ~= round(60 * 100000 / 7)
 *   (RPM = freq_elec_Hz * 60 / 7; freq_elec_Hz = 100000 / delta_ticks at a
 *   100 kHz/10 us tick rate). Reference points computed and checked this
 *   session: 500 RPM -> ~500.1 RPM, 1500 -> ~1501.1, 3000 -> ~2997,
 *   8000 -> ~8011, 20000 -> ~19933 (all within ~0.1-2% of the nominal
 *   input, consistent with the resolution trade-off above).
 */
#ifndef BENCH_IMU_01_TIM3_FG_H
#define BENCH_IMU_01_TIM3_FG_H

#include <stdint.h>

/* Configures TIM3 CH1 for input-capture-on-rising-edge on PA6, with its
 * capture-compare-1 interrupt enabled at the NVIC (IRQn 16). Must be
 * called after gpio_init() (PA6 AF1 mux) and clock_init()
 * (RCC_APBENR1_TIM3EN), and after systick_init() (the ISR timestamps
 * captures using millis()). */
void tim3_fg_init(void);

/* Most recently computed RPM from FG's capture-to-capture period, updated
 * only inside TIM3_IRQHandler(). Meaningless (stale) if tim3_fg_is_valid()
 * is false -- always check validity before using this value, especially
 * for any safety decision (motor.c's REQ-405 logic). Reports 0 mechanical
 * RPM if FG has never captured a single edge since tim3_fg_init(). */
uint32_t tim3_fg_get_rpm(void);

/* True if FG has captured at least one edge within the last
 * TIM3_FG_STALE_MS milliseconds (see .c file) -- i.e. the motor is either
 * stopped (no edges at all -- also reports invalid, see .c file for the
 * zero-RPM-vs-never-captured distinction) or FG has gone silent for longer
 * than any single real electrical period could explain at any RPM this
 * motor can produce. motor.c treats "not valid" as "cannot currently trust
 * an RPM number" -- this is deliberately conservative for a safety
 * feature: REQ-405's own FG-invalid-while-nonzero-duty-commanded sub-clause
 * (motor.c) treats a stale/never-captured reading as a fault condition
 * requiring a safe-state response, not as "assume everything is fine". */
uint32_t tim3_fg_is_valid(void);

/* Timestamp (millis()) of the most recent capture event, or 0 if none has
 * ever occurred. Exposed for motor.c's own staleness/spin-up-window
 * bookkeeping (e.g. distinguishing "motor commanded to spin but FG hasn't
 * produced its first edge yet" from "FG was valid and has since gone
 * stale"). */
uint32_t tim3_fg_last_capture_ms(void);

#endif /* BENCH_IMU_01_TIM3_FG_H */
