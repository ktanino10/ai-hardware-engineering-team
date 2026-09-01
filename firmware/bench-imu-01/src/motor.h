/*
 * motor.h -- Rev 3 Motor Driver + Reaction Wheel open-loop bring-up/
 * characterization module (U5 DRV10983, M1 T-Motor MN2206-13, U6
 * TPS26631PWPR). Orchestrates tim1_pwm.c (SPEED/PA8), tim3_fg.c (FG
 * tachometer/PA6), i2c1.c + drv10983.c (U5 commissioning/status/PB6-PB7),
 * and gpio.c's motor_dir_set()/motor_shdn_set() (DIR/PA9-SHDN... DIR is
 * actually PB1, SHDN is PA9 -- see gpio.c) into one safety-gated,
 * host-commanded characterization routine.
 *
 * =========================================================================
 * HARD SCOPE FENCE (.github/agents/firmware-engineer.agent.md's own "Out of
 * scope" section, restated here because this is the single file where a
 * scope violation would actually happen):
 *
 * This module is OPEN-LOOP ONLY. It:
 *   - accepts a host-commanded PWM duty-cycle / speed setpoint and applies
 *     it directly to SPEED (tim1_pwm_set_duty_pct()) -- no controller, no
 *     error term, no integrator;
 *   - reports measured RPM (tim3_fg_get_rpm()) back to the host verbatim;
 *   - enforces exactly two bounded safety cutoffs (REQ-405 overspeed,
 *     REQ-406 latched lock-fault) -- each is a threshold-compare-and-stop
 *     action, categorically different from closed-loop control the same
 *     way an overcurrent shutdown is not itself "control" (schematic
 *     Section 7.5.11, asserted there for Hardware Lead/human-reviewer
 *     confirmation, repeated here for the same reason).
 *
 * It NEVER:
 *   - computes an error between a desired and an actual RPM/speed and feeds
 *     that back into the SPEED command (that would be closed-loop speed
 *     control -- out of scope);
 *   - reads any IMU data (bmi270.c) or writes any IMU register from this
 *     file, or is read from/written to by main.c's IMU sampling path in
 *     any way that couples the two subsystems' *behavior* -- the IMU and
 *     motor subsystems share only the physical MCU and the UART transport
 *     (distinguished by the "MOTOR," CSV tag below), never program logic.
 *     No function in this file takes IMU data as an input, and no function
 *     in bmi270.c/main.c's IMU path takes motor data as an input.
 *   - implements attitude/orientation control, sensor fusion, or PID of any
 *     kind. If a future change to this file would require computing an
 *     error term between a desired and an actual *orientation*, that
 *     change belongs to a future Control Engineer role
 *     (docs/architecture.md Section 14), not here.
 * =========================================================================
 *
 * HOST COMMAND GRAMMAR (ASCII, CRLF- or LF-terminated, matching this
 * board's existing human-readable-over-binary framing convention --
 * usart2.h's own already-stated rationale for 115200/8N1 applies equally
 * here: no reason to invent a binary protocol for a bench characterization
 * tool an operator drives from a plain serial terminal):
 *
 *   SPD <0-100>   Set commanded duty cycle (percent). Rejected (no PWM
 *                 change) if disarmed, fault-latched, or above
 *                 MOTOR_MAX_CMD_DUTY_PCT -- REQ-405's COMMAND-SIDE
 *                 ceiling (see the dedicated section below for its
 *                 derivation), a check distinct from and in addition to
 *                 the 0-100 syntax-range check, which is unchanged. A
 *                 true 0->nonzero transition resets REQ-405's spin-up
 *                 grace-period bookkeeping (see check_overspeed() in
 *                 motor.c).
 *   DIR <0|1>     Set direction (0=forward, 1=reverse per gpio.c's
 *                 motor_dir_set() polarity). Rejected unless duty_pct==0
 *                 -- a firmware-only policy (no datasheet requires this;
 *                 it exists because DRV10983's own commutation state
 *                 machine is not verified safe to reverse under load in
 *                 this bring-up pass, and this is a characterization tool
 *                 with no operational need to reverse-under-load).
 *   STOP          Zero commanded duty immediately. Does NOT disarm, drop
 *                 SHDN, or require REARM -- an always-available operator
 *                 convenience, distinct from a safety trip. (Note the
 *                 REQ-405 overspeed check still runs after STOP -- see
 *                 "coast-down" caveat below.)
 *   REARM         The single unified arm/re-arm action, used identically
 *                 for the very first arm after boot and for recovery after
 *                 a REQ-405/406 trip (see "why unified" in motor.c). Drives
 *                 duty to 0, brings SHDN high, waits
 *                 MOTOR_REARM_POWERUP_DELAY_MS, re-runs
 *                 drv10983_commission(), and on success clears all latch
 *                 state and arms. On failure, drops SHDN again and reports
 *                 failure WITHOUT setting the fault-latched state (a failed
 *                 REARM attempt is a failed *recovery*, not itself a new
 *                 safety trip -- see motor.c).
 *
 * Each command produces exactly one plaintext ack/error line: SPD_OK,
 * SPD_REJECTED reason=..., DIR_OK, DIR_REJECTED reason=..., STOP_OK,
 * REARM_OK, REARM_FAILED reason=..., ERR unknown_command, ERR
 * bad_..._value, ERR line_too_long.
 *
 * CSV TELEMETRY: periodic lines tagged with a leading literal "MOTOR,"
 * field, sharing USART2 with the pre-existing untagged IMU CSV stream
 * (main.c). This is a necessary, disclosed, minimal adaptation of "the
 * existing CSV-style reporting mechanism" (this module's own task
 * description) -- not a new protocol, just a discriminator column so a
 * host-side script/human can tell the two interleaved streams apart on one
 * shared UART. Schema (see motor.c's motor_init() header line and
 * emit_csv_line()):
 *
 *   MOTOR,millis_ms,armed,fault_latched,duty_pct,dir_reverse,fg_valid,rpm,mtrlck,lock_event_count
 *
 * `armed` and `fault_latched` are BOTH present because together they
 * encode three real, distinct states a bench operator needs to
 * distinguish: never-armed-since-boot (armed=0,fault_latched=0),
 * armed-and-running (armed=1,fault_latched=0), and
 * tripped-awaiting-rearm (armed=0,fault_latched=1) -- collapsing these to
 * one field would lose information an operator characterizing a fault
 * condition needs. `mtrlck` and `rpm` read "NA" (not a fabricated 0/false)
 * whenever the value is not currently meaningful (disarmed -- U5's status
 * bus is not being polled -- or FG invalid, respectively): reporting a
 * fabricated 0 in place of "unknown" could be misread by a human operator
 * as an affirmative "confirmed not locked"/"confirmed zero RPM", which is
 * false and, for `mtrlck` specifically, actively unsafe to imply.
 *
 * =========================================================================
 * REQ-405 (maximum commanded/actual speed) -- CEILING DECISION, IN FULL
 * (a real engineering judgment call this module makes explicitly, per this
 * module's own task description; requirements.md's REQ-405 text itself
 * states "Exact ceiling/ramp-rate/response TBD by Firmware Engineer + human
 * safety review" -- this file's rationale below, surfaced again in the
 * Firmware Engineer's handoff report, IS that review's input):
 *
 *   MOTOR_OVERSPEED_CEILING_RPM = 6000 RPM.
 *
 * Known reference points (bom/component-selection.md, cited in the
 * schematic's own Section 7.5.11 verbatim): REQ-007's floor is >=3000 RPM
 * (a functional MINIMUM the design must reach, never stated as a ceiling);
 * M1's own no-load speed is ~20,000-22,200 RPM. Because stored rotational
 * kinetic energy scales with the SQUARE of angular velocity (REQ-405's own
 * stated rationale, and the schematic's Section 7.5.11 own framing: M1
 * "stores roughly 45-55x the rotational energy at no-load that it would at
 * the 3000 RPM floor" -- independently re-verified here:
 * (20000/3000)^2=44.4, (22200/3000)^2=54.8, matching), the choice of
 * ceiling is fundamentally an ENERGY decision, not just an RPM number, and
 * the ceiling chosen here directly sets the stored-energy figure Mechanical
 * Lead's not-yet-designed flywheel/containment structure (REQ-403) must be
 * sized against (`hardware/mechanical-interface.md` Section B5/B2 -- as of
 * this writing, explicitly flagged there as sized only against the 3000
 * RPM *target*, waiting on this exact decision as "a real input").
 *
 *   Margin ABOVE the 3000 RPM floor:  6000/3000  = 2.0x  (4x the stored
 *     energy of the floor) -- a real, non-trivial characterization range
 *     above the minimum functional target, enough to verify the
 *     duty-cycle-to-RPM relationship has comfortable headroom before
 *     reaching 3000 RPM (e.g. confirming 3000 RPM is reached well under
 *     100% duty), without needing to approach the motor's own structural
 *     regime to do so.
 *   Margin BELOW the no-load range:   20000/6000 = 3.33x,
 *                                     22200/6000 = 3.7x  (only ~1/11th to
 *     1/14th of the stored energy the motor could hold at its own
 *     structural no-load limit) -- comfortably conservative.
 *
 *   DISCLOSED REVISION (shown, not hidden, because this is exactly the
 *   kind of self-check this bring-up pass is supposed to perform): this
 *   module's first-pass internal reasoning independently converged on
 *   8000 RPM (2.67x above the floor, 2.5-2.78x below no-load -- a
 *   defensible number by the same two-sided-margin logic above). Before
 *   finalizing, `hardware/mechanical-interface.md` and the schematic's own
 *   Section 7.5.11 were (re-)read in full, which surfaced two facts that
 *   changed the conclusion: (1) Section 7.5.11 itself already proposes
 *   "~6000 RPM (2x REQ-007's own floor) only as a numeric anchor for
 *   discussion, not a decision" -- i.e. a domain expert (Circuit Engineer)
 *   had already reasoned through this exact trade-off and floated 6000;
 *   (2) `mechanical-interface.md` confirms no containment structure has
 *   been designed against ANY ceiling yet, so whichever number is chosen
 *   here directly and quadratically sets a real downstream engineering
 *   burden. Given REQ-405's entire justification is the quadratic-with-
 *   speed energy risk, and 6000 RPM already satisfies both margin
 *   requirements (a real, non-marginal amount above the floor; a real,
 *   comfortable amount below no-load) with no identified characterization
 *   need this bench tool actually has to explore RPM between 6000 and
 *   8000, preferring the LOWER of two adequately-reasoned candidates is
 *   the more defensible safety choice -- it is not "arbitrary", it is
 *   "when the deciding rationale is itself about minimizing energy, and
 *   two candidate numbers both clear the bar, take the smaller one". This
 *   module therefore adopts 6000 RPM, aligning with (not merely
 *   coincidentally near) the schematic's own already-published anchor,
 *   rather than an independently-derived 8000. Flagged prominently in the
 *   handoff report as new, quadratic-impact input for Mechanical Lead's
 *   next containment-design phase.
 *
 * REQ-405 RESPONSE: latches (drops to a safe/stopped state AND requires
 * REARM), rather than momentarily zeroing duty and allowing automatic
 * resumption. This is a deliberate choice beyond the task's literal
 * wording (only REQ-406 explicitly says "deliberate re-arm"): an unlatched
 * response would let an unchanged SPD setpoint immediately re-trigger the
 * same overspeed condition the instant the measured RPM dips back under
 * the ceiling, producing oscillation/thrashing at the boundary rather than
 * a clean, deliberate stop -- see trip_safe_state() in motor.c, which both
 * REQ-405 and REQ-406 share.
 *
 * REQ-405 "COAST-DOWN" DISCLOSED LIMITATION: trip_safe_state() (used by
 * both REQ-405 and REQ-406) drops U6's SHDN low, which fully de-energizes
 * U5 -- FG then goes stale (tim3_fg_is_valid() false) within
 * TIM3_FG_STALE_MS regardless of the flywheel's own actual (mechanically
 * longer) coast-down time. This firmware has ZERO tachometer visibility
 * during coast-down after any trip. This is an accepted, disclosed
 * limitation, not an oversight: (a) no active-braking capability exists in
 * this open-loop scope, and adding one would be scope creep beyond
 * characterization bring-up; (b) fully de-energizing the rail (vs. leaving
 * SHDN high and trusting U5 to honor a zero SPEED command while still
 * powered) is the more conservative, REQ-403-fail-safe-consistent choice
 * -- relying on the driver IC alone to honor a stop command while still
 * powered is exactly the "trust the hardware's own auto-recovering
 * protections alone" pattern REQ-406 exists to NOT rely on. The task's own
 * "SPEED->0 and/or SHDN->low" wording permits either; asserting both
 * together was a deliberate choice for the more conservative option, this
 * limitation accepted as its cost. The REQ-405 check itself still runs
 * continuously whenever armed (see check_overspeed() in motor.c) --
 * specifically so a flywheel coasting down above the ceiling after a plain
 * STOP command (SHDN still high, U5 still powered, FG still valid) is
 * still caught even though duty is already 0.
 *
 * REQ-405 COMMAND-SIDE CEILING (NEW -- closes Firmware Reviewer Finding 1,
 * HIGH, first-ever Firmware Reviewer cycle, PR #14,
 * bench-imu-01-firmware-review.md):
 *
 * REQ-405's own literal text has TWO distinct clauses: (a) COMMAND-side --
 * "enforce a maximum commanded flywheel speed and reject/clamp any
 * command exceeding it"; (b) FEEDBACK-side -- "using the already-wired FG
 * tachometer feedback to verify actual speed does not exceed a defined
 * ceiling... command the motor to a safe/stopped state". Everything above
 * this point (CEILING DECISION, RESPONSE, COAST-DOWN) is clause (b) --
 * REACTIVE, triggered only after FG measurement confirms an actual
 * overspeed. Before this revision, clause (a) was NOT implemented:
 * cmd_spd() accepted any 0-100 duty-cycle value with no RPM-tied ceiling
 * of its own, so a host commanding SPD 100 would drive the motor
 * open-loop toward whatever RPM that duty cycle produces -- potentially
 * far above 6000 RPM if lightly/un-loaded, per M1's own ~20,000-22,200
 * RPM no-load speed above -- before check_overspeed() eventually caught it
 * after the fact. This section adds clause (a) as a genuinely new,
 * PRE-EMPTIVE layer, in ADDITION to (never instead of) clause (b).
 *
 *   MOTOR_MAX_CMD_DUTY_PCT = 23 (percent, see motor.c). Any SPD command
 *   above this is REJECTED (SPD_REJECTED reason=exceeds_cmd_duty_ceiling)
 *   by cmd_spd(), not silently clamped to it -- consistent with this
 *   module's own existing convention of rejecting an out-of-policy
 *   request explicitly (e.g. DIR) rather than silently substituting a
 *   different value, and satisfying REQ-405's own "reject/clamp" wording
 *   (the requirement's own "/" permits either; reject was chosen for
 *   host-visible auditability -- a host that queries what happened gets
 *   an explicit answer, not a silently-substituted number it might not
 *   notice).
 *
 *   DERIVATION (this fix's own task framing offered two options -- derive
 *   a real, evidence-grounded duty-to-RPM ceiling, or escalate honestly
 *   if none could be derived; this derivation was judged sufficiently
 *   evidence-grounded, so no escalation was made):
 *
 *   1. TI DRV10983 (U5) Section 8.4.5.3 "Digital PWM Input Mode Speed
 *      Control" (datasheets/texasinstruments_drv10983_slvscp6h.md, pages
 *      29-30, DS-MTR-077): verbatim, "The PWM duty cycle applied to the
 *      SPEED pin can be varied from 0 to 100%. The speed command is
 *      proportional to the PWM input duty cycle." I.e. this firmware's
 *      existing 0-100 SPD command (applied verbatim to the SPEED pin via
 *      tim1_pwm_set_duty_pct(), unchanged by this fix) drives a DIRECTLY
 *      PROPORTIONAL internal Speed Command -- TI's own explicit
 *      statement, not an assumption this firmware invents.
 *   2. TI DRV10983 Section 8.3.3 "Motor Speed Control" (same datasheet,
 *      pages 16-17, DS-MTR-078): verbatim, "The output amplitude is
 *      determined by the magnitude of VCC and the PWM duty cycle output
 *      (PWM_DCO)... The maximum amplitude is reached when PWM_DCO is at
 *      100%. The peak output amplitude is VCC. When the PWM_DCO is at
 *      50%, the peak amplitude is VCC/2." I.e. peak motor phase-voltage
 *      amplitude = VCC x (PWM_DCO/100), a direct, datasheet-stated
 *      proportionality.
 *      CAVEAT, from the same DS-MTR-078 section, disclosed rather than
 *      glossed over: "The Speed Command may not always be equal to the
 *      PWM_DCO because DRV10983 has implemented the AVS function..., the
 *      acceleration current limit function..., and the closed loop
 *      accelerate function... These functions can limit the PWM_DCO."
 *      All three named functions can only REDUCE actual output relative
 *      to what commanded duty cycle implies, never increase it -- so
 *      treating amplitude as if it were exactly proportional (this
 *      derivation's own simplification) is a worst-case/upper-bound
 *      assumption on the SAFE side, not an optimistic one.
 *   3. Standard BLDC steady-state physics, the SAME method already used
 *      and accepted elsewhere in this project for M1's own no-load-speed
 *      figures (DS-MTR-018: ~20,000 RPM @10V / ~22,200 RPM @11.1V, both
 *      exactly KV x V with KV=2000 RPM/V, DS-MTR-017, no extra derating):
 *      at low/no load current, applied voltage amplitude approximately
 *      equals BEMF, so RPM_no_load ~= KV x V_applied. (DRV10983's own
 *      Section 8.4.3.6 Equation 2, "BEMF = Kt x speed (Hz)", page 27,
 *      confirms the same underlying physical relationship in the
 *      driver's own terms -- not a new assumption introduced here.)
 *   4. Combining 1-3: RPM(duty_pct) is bounded above by KV x
 *      VCC_worst_case x (duty_pct/100) -- an upper bound, not an
 *      equality, per item 2's own caveat.
 *   5. VCC_worst_case = 13.0V -- this design's OWN already-established,
 *      binding, qualified VM_MOTOR input envelope ceiling
 *      (hardware/schematic/bench-imu-01-design.md Section 7.5.9: binding
 *      voltage envelope 9.0V to 13.0V, "a binding constraint, not a
 *      description"; U6's own OVP does not trip anywhere within this
 *      envelope per Section 7.5.10, so 13.0V is a real, reachable
 *      worst-case operating voltage, not a theoretical one). Using the
 *      FULL J4-connector envelope ceiling as the assumed VCC at U5,
 *      rather than a lower post-series-drop estimate (F1/D2/U6 all drop
 *      some additional voltage per the schematic), is a further
 *      deliberate conservatism: real delivered voltage at U5 is somewhat
 *      LOWER than 13.0V, so using 13.0V un-reduced over-estimates (never
 *      under-estimates) achievable RPM for a given duty -- the safe
 *      direction for a ceiling.
 *   6. KV = 2000 RPM/V, M1's own T-Motor-published rating (DS-MTR-017),
 *      used at face value (not derated) -- the same convention already
 *      established by DS-MTR-018, not a new methodology invented for
 *      this fix.
 *
 *   ARITHMETIC: ceiling_duty_pct = floor(MOTOR_OVERSPEED_CEILING_RPM /
 *   (KV x VCC_worst_case) x 100) = floor(6000 / (2000 x 13.0) x 100) =
 *   floor(6000/26000 x 100) = floor(23.0769...) = 23. Sanity check: 23%
 *   -> 2000x13.0x0.23 = 5980 RPM (<=6000, OK); 24% -> 2000x13.0x0.24 =
 *   6240 RPM (>6000, correctly rejected) -- 23 is the largest integer
 *   percent that clears the ceiling.
 *
 *   CONFIDENCE, MARKED EXPLICITLY (.github/instructions/
 *   firmware.instructions.md's evidence-citation discipline, applied to a
 *   derived value exactly as it would be to a raw register field):
 *     - HIGH confidence, directly-cited primary-source facts: the
 *       duty-proportional-to-speed-command statement (DS-MTR-077); the
 *       VCC/PWM_DCO output-amplitude relationship (DS-MTR-078); M1's own
 *       published KV=2000 RPM/V (DS-MTR-017); this design's own
 *       schematic-derived 13.0V worst-case envelope (Section 7.5.9).
 *     - REASONED ENGINEERING JUDGMENT, not a number printed in any single
 *       source: the ARITHMETIC COMBINATION of the above (steps 3-6) --
 *       the 23% figure itself is DERIVED, not directly published.
 *       Disclosed here exactly that way: neither TI nor T-Motor publish
 *       "23%" themselves, this module's own reasoning does.
 *
 *   HONEST LIMITATION, DISCLOSED (this is a DEFENSE-IN-DEPTH bound, NOT a
 *   guarantee -- exactly like a fuse rating is a bound, not a promise):
 *   duty-to-RPM is fundamentally LOAD-DEPENDENT for a sensorless BLDC --
 *   the real reaction-wheel flywheel load, and any real supply voltage
 *   below the assumed 13.0V worst case, will make ACTUAL RPM at a given
 *   duty LOWER than this ceiling's own no-load/worst-case-voltage
 *   estimate, likely significantly so. In practice this command-side
 *   ceiling may therefore be noticeably MORE RESTRICTIVE than strictly
 *   necessary to characterize up to 6000 RPM under typical (loaded,
 *   non-worst-case-voltage) bench conditions -- an accepted cost of a
 *   conservative bound, not a defect: under-permitting is far safer than
 *   over-permitting here. REQ-007's own >=3000 RPM floor remains
 *   comfortably inside this ceiling's own no-load-equivalent estimate
 *   (5980 RPM at duty=23%), so no characterization capability required by
 *   an approved requirement is lost -- only some amount of exploratory
 *   headroom between the floor and this design's own 6000 RPM ceiling
 *   that REQ-405 never promised in the first place. check_overspeed()'s
 *   existing FG-measured REACTIVE path (documented above) remains the
 *   authoritative, closed-loop-measurement-based enforcement of the
 *   actual 6000 RPM limit and is completely unaffected by (and
 *   independent of) this command-side layer -- this ceiling is a SECOND,
 *   pre-emptive line of defense, not a replacement for the first.
 *
 * =========================================================================
 * REQ-406 (latched lock-fault policy) -- POLICY IN FULL:
 *
 *   3 consecutive qualifying Lock-Detection rising-edge events (Status
 *   register bit4 MtrLck, DS-MTR-059/DRV10983_STATUS_MTRLCK) within a
 *   rolling 30-second window -> trip_safe_state() (same latch/REARM
 *   mechanism as REQ-405, shared code path).
 *
 *   Edge-detected (a continuously-asserted MtrLck bit across polls counts
 *   as ONE ongoing event, not repeated new events -- see s_was_locked in
 *   motor.c) so a single sustained lock condition cannot itself trip the
 *   3-event threshold by being polled multiple times.
 *
 *   30-second window sanity-checked against U5's own documented
 *   auto-retry period tLOCK_OFF=5s (DS-MTR-059, schematic Section
 *   7.5.12): 3 of U5's own auto-retry cycles need >=15s minimum to occur,
 *   leaving the 30s window comfortable margin to actually observe 3 real
 *   retry-triggered re-lock events rather than requiring an implausibly
 *   fast repeat rate.
 *
 *   FaultCode register (0x1E) is read only on the new-event edge (not
 *   every poll) and reported over CSV/UART as a decimal LOCK_EVENT line
 *   (matching DS-MTR-074's own "read by this firmware on each new
 *   qualifying Lock-Detection edge" framing already logged for that
 *   citation).
 *
 * =========================================================================
 * BEMF/FG CAVEATS -- TWO DISTINCT PHENOMENA, NOT ONE (both must be
 * documented honestly, not conflated, per this module's own task
 * description and ECO-008's own directive):
 *
 * (1) Op2ClsThr open/closed-loop transition (DS-MTR-062/063/076): below
 *     U5's own factory-default Op2ClsThr threshold (SysOpt4=0x7A ->
 *     Op2ClsThr field value 15 -> 12 Hz electrical -> ~103 RPM mechanical,
 *     DS-MTR-076), U5 uses forced/open-loop commutation that is NOT
 *     BEMF-dependent at all -- FG in this narrow band reflects the
 *     COMMANDED drive frequency, "may not reflect actual motor speed"
 *     (DS-MTR-062). This window is narrow (0-~103 RPM) and does not
 *     threaten REQ-405/406: by the time RPM approaches either the 6000 RPM
 *     ceiling or the ECO-008 band below, the motor has necessarily already
 *     transitioned to closed-loop (BEMF-sensed) operation.
 *
 * (2) ECO-008's own broader 500-1500 RPM BEMF-signal-degradation caveat
 *     (`validation/change-log.md` ECO-008, schematic Section 7.5.7): a
 *     DIFFERENT, WIDER effect that persists even in confirmed
 *     closed-loop/BEMF-sensed operation -- NOT explained away by the
 *     Op2ClsThr reasoning above. This module's honest conclusions, none of
 *     which are hand-waved:
 *       (a) Does NOT threaten the REQ-405 ceiling: BEMF degradation in
 *           this band manifests as noise/imprecision in the FG signal, not
 *           a systematic ~5-16x frequency multiplication that could alias
 *           a real 500-1500 RPM reading into a false >=6000 RPM reading.
 *           No code change is needed or made to REQ-405's logic for this
 *           reason.
 *       (b) DOES mean CSV-reported RPM may look visibly noisier to a bench
 *           operator specifically while characterizing in the 500-1500 RPM
 *           band -- this is disclosed as an operator-facing note in
 *           motor_init()'s boot banner (a documentation/UX matter, not a
 *           code-behavior change, matching ECO-008's own directive that
 *           this "must appear as a tracked item in the firmware bring-up
 *           plan", which this file and the design-rationale doc both are).
 *       (c) COULD plausibly cause more frequent Lock-Detection
 *           nuisance-trips while transiting that RPM band. Deliberately
 *           NOT special-cased or suppressed in check_lock_faults() --
 *           doing so would undermine REQ-406's actual safety purpose,
 *           since a real lock condition could also genuinely occur in that
 *           same band and must not be masked. Documented here as an
 *           expected, non-firmware-bug operational characteristic a bench
 *           operator may observe, not treated as a defect to be coded
 *           around.
 * =========================================================================
 */
#ifndef BENCH_IMU_01_MOTOR_H
#define BENCH_IMU_01_MOTOR_H

#include <stdint.h>

/* Initializes all motor.c state to its post-boot default (disarmed, zero
 * duty, forward direction, no fault latched, empty lock-event history),
 * defensively re-asserts the hardware-safe state (SHDN low, PWM duty 0,
 * DIR forward) even though gpio_init()/tim1_pwm_init() already default this
 * way, and prints the boot banner + CSV header line over USART2. Must be
 * called after gpio_init(), clock_init(), systick_init(), tim1_pwm_init(),
 * tim3_fg_init(), i2c1_init(), and usart2_init().
 *
 * Starts DISARMED -- a REARM command is required even for the very first
 * arm after boot, not only after a fault. This is a deliberate symmetry
 * decision (treating "just booted" the same as "just recovered from a
 * trip" is one code path instead of two), even though REQ-406 only
 * strictly requires no-auto-resume-*after-a-fault*. */
void motor_init(void);

/* Feeds one received host command byte into the line-buffering command
 * parser. Call once per byte returned by usart2_read_byte() in main.c's
 * poll loop. Recognizes CR/LF as the line terminator; a line longer than
 * MOTOR_RXBUF_LEN-1 characters is discarded with an "ERR line_too_long"
 * response (bounded buffer, no overflow). */
void motor_handle_rx_byte(uint8_t b);

/* Must be called once per main-loop iteration with the current millis()
 * value. Runs the REQ-405 overspeed check and the REQ-406 lock-fault
 * check (every call -- these are safety checks, not rate-limited), and
 * emits one periodic CSV telemetry line at MOTOR_CSV_PERIOD_MS cadence. */
void motor_tick(uint32_t now_ms);

#endif /* BENCH_IMU_01_MOTOR_H */
