# Bench-IMU-01 — Firmware Bring-up Design Document

**Author**: Firmware Engineer (AI agent) · **Status**: Source-complete,
self-checked, compiles cleanly with `arm-none-eabi-gcc` 16.2.0 (re-verified
present this session) — not run on real hardware (none exists in this
environment). Mirrors the evidence-citation and rationale discipline of
`hardware/schematic/bench-imu-01-design.md`, adapted for firmware.
**Updated in a later session** to add REQ-405's command-side ceiling (a
Firmware Reviewer Finding 1 fix) — that later session's own tooling
re-verification and build result are recorded separately in §12, rather
than silently blended into this paragraph's own "this session" claims.

**Revision covered by this document**: three deliverables landed across two
sessions:

1. A fix for a CRITICAL, now-hardware/schematic-confirmed IMU I2C2 GPIO
   defect (§3) — unrelated to item 2, bundled into the same bring-up pass
   at the Hardware Lead's request. The GPIOA-port/pin correction itself was
   independently re-derived and reached a second time, in a separate
   parallel effort (origin/main's own narrower, Rev-2-only fix for this same
   defect, tracked there as "ISS-014" — this repository's own, unrelated,
   already-RESOLVED ISS-014 is a 2S/3S UVLO-margin diode finding, so all
   references to that parallel effort's fix are translated to this
   repository's actual ID, ISS-027, throughout this document). That parallel
   effort also surfaced two further official ST sources corroborating the
   AF6 alternate-function value (DS-MCU-068, DS-MCU-077) that this document
   now cites alongside its own DS-MCU-073/067 — see §3.
2. Open-loop bring-up/characterization firmware for the new Rev 3 Motor
   Driver + Reaction Wheel subsystem (§7), including REQ-405/406 safety
   behavior, against `hardware/schematic/bench-imu-01-design.md`'s Rev 5
   (Design-Complete) wiring. Item 2 has no counterpart in the parallel
   effort above, which only ever had the Rev 2 (IMU + MCU + power) baseline
   in scope — this is why that effort's own fix, correct for its own
   narrower scope, removed GPIOB support entirely; that removal is NOT
   carried into this document or this firmware, since Rev 3's motor
   subsystem genuinely uses GPIOB (PB1/PB6/PB7, §7.5).
3. A fix for **Finding 1 (HIGH)** from the first-ever Firmware Reviewer
   cycle (PR #14, `bench-imu-01-firmware-review.md`): REQ-405's
   command-side clause ("reject/clamp any command exceeding [the
   ceiling]") was not implemented — only the feedback-side (reactive,
   FG-measured) trip was. This is a **separate, later session** from
   items 1–2 above (added after this document's own §0/§9/§10/§11 were
   written, which is why those sections' own "this session" language is
   left as the accurate historical record of *that* session, not silently
   edited to describe this one). The resulting technical content is
   folded directly into §4.3/§7.6 (where a reader looking for "the
   REQ-405 section" would already look); that later session's own
   tooling/build/self-check account lives in **§12**.

## 0. Tooling honesty statement

Re-verified fresh **this session** (not assumed from any prior session's
result, per this project's own tooling-honesty discipline):

- `arm-none-eabi-gcc` 16.2.0 is present at `/opt/homebrew/bin/arm-none-eabi-gcc`.
- PlatformIO and STM32CubeIDE/STM32CubeMX are **not** installed.
- **No physical Bench-IMU-01 board exists in this environment** (checked via
  `system_profiler SPUSBDataType` — no ST-Link/serial USB device present).
  This remains a source-code exercise, the same tooling-honesty convention
  `docs/architecture.md` §5.3 established for the Mechanical Lead's CAD
  tooling, extended to Firmware (§5.4). No claim of "tested," "verified on
  hardware," or "flashed" is made anywhere in this document or the firmware
  source.
- A **real, full clean build was attempted this session** covering both the
  pre-existing IMU firmware and every new file added for this pass, and it
  **succeeded**: zero warnings under `-Wall -Wextra -std=c11`, zero errors.
  See §9 for the full account, including an empirical vector-table
  sanity-check of the new interrupt-driven FG capture path (a genuinely
  stronger check than reading the source alone).

This document is therefore the schematic-equivalent artifact for firmware: a
structured, Evidence-ID-cited account of every register-level decision,
sufficient for a future independent reader (or a future Firmware Reviewer,
if that role is ever introduced — see §10) to check this work against
primary sources.

## 1. Scope and inputs (not re-litigated)

Per `.github/agents/firmware-engineer.agent.md`, this firmware's scope is
driver-level bring-up only: peripheral initialization and register-level
configuration matching `hardware/schematic/bench-imu-01-design.md`'s actual
pin/interface decisions. Every pin/peripheral fact below is extracted from
that document (now Design-Complete through Rev 5, including the merged
pin-identity correction — read in full, top revision banner included, before
any code in this pass was written), not re-derived or assumed.

| Fact | Value | Schematic source |
|---|---|---|
| MCU | STM32G031K8T6, Cortex-M0+, LQFP-32, 64KB Flash/8KB SRAM | §1 |
| IMU bus | **I2C2**, corrected to **PA11=SCL, PA12=SDA** (was PB10/PB11 — see §3; PB10/PB11 do not exist on this part's actual LQFP-32 package). Peripheral instance itself was separately corrected earlier from an original I2C1 mislabeling (ISS-011) — a different defect, unaffected by this pin fix. | §2.3, §5.2, §5.3, §11 (post-correction), ISS-011, ISS-027 |
| IMU address/mode | I2C address 0x68 (SDO→GND); I2C mode (CSB→VDDIO) | §5.3, DS-IMU-075/076 |
| IMU acquisition | Polled, not interrupt-driven (INT1/INT2 left NC) | §5.3 |
| Host UART | USART2 (PA2=TX, PA3=RX), header J2 | §6 |
| Status LED | PA5, active-high drive via R5 to D1 | §7 |
| "Manual reset button" (REQ-004) | SW1 wired directly NRST→GND — **not** a GPIO | §4.3 |
| MCU clock | Internal HSI16, no external crystal; exact target frequency deliberately left open by the schematic | §6 |
| BOOT0 | No physical circuit; relies on `nBOOT_SEL=1` factory default | §4.2 |
| **Motor SPEED (Rev 3)** | **PA8**, TIM1_CH1, AF2 — PWM duty-cycle command to U5 (DRV10983) SPEED pin | §7.5, §7.5.2 |
| **Motor FG tachometer (Rev 3)** | **PA6**, TIM3_CH1, AF1 — U5's FG output via R6 pull-up, input-capture | §7.5, §7.5.6 |
| **Motor DIR (Rev 3)** | **PB1**, plain GPIO output — direction command to U5 DIR pin | §7.5, §7.5.3 |
| **Motor commissioning bus (Rev 3)** | **PB6=SCL, PB7=SDA**, I2C1, AF6 — U5's own commissioning/status interface | §7.5, §7.5.4, DS-MTR-071 |
| **Motor rail enable (Rev 3)** | **PA9** — U6 (TPS26631PWPR) SHDN; default/floating state is OFF via R11's external pulldown | §7.5, §7.5.9, REQ-403 |

Explicitly out of scope this cycle
(`.github/agents/firmware-engineer.agent.md` "Out of scope"): USB
data/enumeration (REQ-105 — D+/D− unpopulated), any wireless (REQ-006), and
anything Control-Engineer-flavored (control loops, attitude control, sensor
fusion, physical-unit conversion — `docs/architecture.md` §14's 1-axis/
3-axis attitude-control trigger is not met by this bench board). This
constraint now also explicitly covers the new motor subsystem: no code
anywhere in this firmware reads the IMU and reacts by driving the motor, or
vice versa — the two subsystems are wired independently on the schematic and
kept functionally independent in this firmware too (see §4.9 for how this
was strengthened at the failure-mode level, not just the normal-operation
level).

## 2. Correcting a scope assumption: REQ-004 / SW1 is not a GPIO

*(Unchanged from the prior firmware pass — recorded here for continuity.)*

The task framing for the original firmware cycle assumed the "manual reset
button" (REQ-004) would be a GPIO firmware could read. Re-reading the actual
schematic (§4.3) shows SW1 is wired **directly from NRST to GND**, in
parallel with the always-populated NRST filter capacitor C5. Pressing SW1
causes a **hardware** MCU reset; there is no GPIO pin for firmware to poll.
Per `.github/skills/firmware-bringup/SKILL.md`'s own guidance ("if the
schematic and a task description disagree, the schematic wins"), this
firmware instead reads `RCC_CSR`'s reset-reason flags at boot, reports the
result over UART, then clears the flags (`reset_reason.c`) — a real,
standard STM32 technique (DS-MCU-059), not an invented substitute.

## 3. Correcting a firmware defect: IMU I2C2 GPIO pins (PB10/PB11 → PA11/PA12)

This is the first of this pass's two deliverables, and is unrelated to the
new motor subsystem below — bundled into the same bring-up pass at the
Hardware Lead's explicit request.

**The defect**: the existing firmware (`gpio.c`, `gpio.h`, `clock.c`,
`clock.h`, `i2c2.h`) configured **GPIOB pins 10 and 11** as I2C2's SCL/SDA
alternate function. This is now confirmed **wrong**: `validation/open-issues.md`
ISS-027 (CRITICAL, RESOLVED at the hardware/schematic level) found that
**PB10/PB11 do not physically exist as broken-out pins on the
STM32G031K8T6's actual LQFP-32 package** — this device family only exposes
PB10/PB11 on larger packages (e.g. LQFP-48+); the 32-pin package this
board actually uses does not bond those pads out at all. The original
firmware (and, transitively, the original schematic net names it was
written against) were both wrong about this before ISS-027's correction.

**The fix, re-verified directly against the corrected schematic itself this
session** (not merely trusted from a task-prompt summary, per this agent's
own pin-traceability mandate — §2.3/§5.2/§5.3/§11 and the document's own
top revision-history banner were all re-read this session): the corrected
schematic re-assigns the IMU's I2C2 bus to **PA11 (SCL) / PA12 (SDA)**.

**What did and did not change** — this is a GPIO-port/pin-level correction
only:

- **Unchanged**: the I2C2 *peripheral instance* itself — base address
  `0x40005800`, register layout, the `TIMINGR=0x00310309` 400 kHz-at-16 MHz
  timing value, the polling-mode (no-interrupt) driver logic in `i2c2.c`.
  None of this depends on which GPIO pins happen to be muxed to the
  peripheral's I/O.
- **Unchanged**: the alternate-function number, **AF6** — this device
  family multiplexes I2C2_SCL/I2C2_SDA to AF6 on several different
  candidate pin pairs by design; AF6 on PA11/PA12 maps to
  I2C2_SCL/I2C2_SDA exactly as AF6 on PB10/PB11 was believed to (confirmed
  against the part's own AF table, DS-MCU-057/DS-MCU-062, not assumed by
  analogy).
- **Changed**: only the GPIO **port** (GPIOB → GPIOA) and **pin numbers**
  (10/11 → 11/12). `gpio.c`'s `gpio_init()` now configures PA11/PA12 with
  the same MODER=`10` (alternate function), OTYPER=`1` (open-drain — I2C is
  a wired-AND bus; the schematic's external pull-ups R3/R4 remain
  unchanged), PUPDR=`00` (no internal pull, matching the external-pull-up
  rationale), and AFR nibble=`0110` (AF6) pattern the old PB10/PB11 code
  used — both pin-number pairs (10/11 and 11/12) fall in the "high"
  alternate-function register (`AFR[1]`/AFRH) on this part, so no
  AFR-register-split subtlety was introduced by the port/pin change.
- `clock.c` needed **no change** for this fix: `RCC_IOPENR`'s `GPIOAEN`
  (bit 0) was already enabled (PA2/PA3/PA5 already used GPIOA), so no new
  clock-enable bit was needed — only `GPIOBEN` remains enabled for its own,
  unrelated reason (PB1/PB6/PB7, the new Rev 3 motor pins, below).

**Evidence**: DS-MCU-073 (new this session) independently confirms the
STM32G031K8T6 LQFP-32 pinout omits PB10/PB11 entirely and confirms
PA11/PA12=AF6=I2C2_SCL/I2C2_SDA — see `datasheets/evidence-log.md`.

This same GPIO-port/pin defect and fix were independently re-derived a
second time, in parallel, by a narrower effort scoped only to this board's
Rev 2 (IMU + MCU + power) baseline (tracked there under a locally-numbered
"ISS-014" — not this repository's own, unrelated, already-RESOLVED ISS-014
diode/UVLO finding; every such reference is translated to this
repository's actual ID, ISS-027, throughout this document). That parallel
effort reached the identical PA11/PA12/AF6 conclusion via ST's own pin
database, then went one step further and independently corroborated the
AF6 alternate-function value against **two further official
STMicroelectronics sources** this repository's evidence trail did not
previously have: (a) STMicroelectronics' own `STM32CubeG0` official
firmware-example repository's CubeMX-generated MSP file for the
**NUCLEO-G031K8** board — the same exact STM32G031K8T6 part this design
uses — which configures I2C2 on `GPIOA` pins 11/12 with
`GPIO_InitStruct.Alternate = GPIO_AF6_I2C2` (**DS-MCU-068**); (b)
STMicroelectronics' own `stm32g0xx-hal-driver` header
(`Inc/stm32g0xx_hal_gpio_ex.h`), which defines `GPIO_AF6_I2C2` as the
literal numeric value `0x06` (**DS-MCU-077** — renumbered from that
parallel effort's own local "DS-MCU-069", which collided with this
repository's pre-existing, unrelated DS-MCU-069 Rev-3 motor pin-allocation
citation). Both are additive corroboration, not a contradiction: they agree
with DS-MCU-073/067 on every fact that matters (port, pins, AF value), so
nothing about this fix's conclusion changes — see `src/gpio.c`'s PA11/PA12
comment and `src/gpio.h` for where these citations live at the code level.

That parallel effort's own fix was correct for its own narrower scope but
is **not** carried into this document or this firmware: because its scope
never included the Rev 3 motor subsystem, its own version of `clock.c`/
`clock.h`/`stm32g031_regs.h` removed `GPIOB_BASE`/`GPIOB`/
`RCC_IOPENR_GPIOBEN` entirely, reasoning (correctly, for a Rev-2-only board)
that "GPIOB is no longer used anywhere in this board's real pin allocation."
That reasoning does not hold for this board as this document describes it:
Rev 3's motor subsystem genuinely uses GPIOB (PB1=DIR, PB6/PB7=I2C1 to the
motor driver, §7.5) — this document's own §4.1/§7.5 and `src/gpio.c`/
`src/clock.c`/`src/stm32g031_regs.h` all keep GPIOB fully intact.

**Pre-existing staleness, flagged in an earlier pass — now fixed** (outside
this specific defect's own edit scope, but recorded here since this section
previously stated these were outstanding; a subsequent citation-hygiene
pass, `validation/change-log.md` ECO-016, has since corrected all three):

- `DS-MCU-062`'s evidence-log text now carries a correction annotation
  cross-referencing `DS-MCU-064`/`DS-MCU-073`/`DS-MCU-068`/`DS-MCU-077`
  instead of standing alone as a stale "PB10/PB11=AF6" claim.
- `validation/open-issues.md` ISS-026's own text now cites `DS-MCU-073`
  (the row that actually exists) instead of a dangling `DS-MCU-068`
  reference.
- `validation/bring-up-procedure.md`'s pre-power-on checklist now instructs
  the operator to check I2C2/PA11-PA12 wiring, with an ISS-027 note, in
  both places it previously said PB10/PB11.

**Independent verification of this fix, from the parallel effort** (its own
adversarial, from-first-principles re-derivation, run against its own
narrower Rev-2-only scope — not a formal Firmware Reviewer gate, which
still does not exist, `docs/architecture-evolution.md` §32): it
independently re-fetched ST's official pin database and confirmed PA11
(pin 22)/PA12 (pin 23) = I2C2_SCL/SDA; independently re-fetched both new
official ST sources above and confirmed AF6 (`0x06`); independently checked
its own `git diff` against every derived fact (GPIO port/base address, AF
value, RCC enable bit, AFRH bit-field math for pins 11/12, I2C2 base
address unchanged, no collateral change to USART2/LED pins); independently
rebuilt its own (Rev-2-only) firmware and confirmed via objdump that its
own compiled output's pins 11/12 resolve to exactly MODER=AF, AF=6,
OTYPER=open-drain; and full-text-scanned its own updated documents for any
stale PB10/PB11 claim presented as a current fact, finding none. Its
verdict was **CONFIRMED CORRECT**, zero findings — genuinely independent
corroboration, not a re-read of anyone else's claims.

One part of that independent check does **not** carry over unmodified to
*this* document, and is called out explicitly rather than silently
adopted: that effort's own objdump run additionally confirmed GPIOB's base
address was **absent** from its own (Rev-2-only) compiled output — true
and correct for its own narrower scope, since it has no motor subsystem to
need GPIOB for anything. That specific absence claim does **not** hold for
*this* document's own build: GPIOB's base address (`0x50000400`) legitimately
remains present and reachable in this branch's compiled output, because
PB1/PB6/PB7 (Rev 3's motor subsystem, §7.5) still require it — only the IMU's
own I2C2 pins no longer reference GPIOB. §9 below re-runs the equivalent
objdump check against *this* branch's own build, confirming both facts
simultaneously: no I2C2-related GPIOB reference remains, and GPIOB itself
is still very much present for the motor subsystem.

## 4. Firmware-level decisions (schematic leaves these open; recorded here with rationale)

### 4.1 MCU clock: HSI16, no PLL (16 MHz)

*(Unchanged.)* The schematic (§6) fixes "no external crystal, runs off
internal HSI16+PLL" but not an exact target frequency. **Decision: run on
the default HSI16 with no PLL (16 MHz)** — the part's power-on-reset clock
state, needing zero additional clock-tree register writes, keeping every
timing-register constant in this firmware single-valued. Rev 3's new
peripherals (TIM1, TIM3, I2C1) all derive their own timing from this exact
same, unchanged 16 MHz PCLK/HCLK — I2C1 reuses I2C2's own
`I2C2_TIMINGR_400KHZ_AT_16MHZ` constant verbatim (both buses run at 16 MHz),
and TIM1's/TIM3's own prescalers (§7.2/§7.4 below) are both derived from
this same clock. No re-litigation of the clock decision was needed for Rev
3 — it was already adequate for everything this pass adds.

### 4.2 Host communication framing: 115200 8N1, CSV lines

*(Unchanged, extended.)* The schematic (§6) only cites "115200" as an
example baud rate, without fixing it. **Decision: 115200 baud, 8N1**, line
format `millis,ax,ay,az,gx,gy,gz\r\n` for IMU data — ASCII CSV, raw signed
16-bit register counts. A simple, human-readable format was chosen over an
invented binary protocol per `.github/skills/firmware-bringup/SKILL.md`
("don't over-engineer this").

Rev 3 reuses this **exact same physical link** — no new UART, no new baud
rate. Two design choices keep the two independent subsystems' telemetry
distinguishable on one shared terminal session without inventing a new
protocol:

- The motor subsystem's own CSV lines carry a leading `MOTOR,` tag (vs. the
  IMU's untagged `millis,ax,ay,...` lines), so a human (or a simple script)
  can `grep` or visually separate the two streams trivially.
- The motor subsystem's host command grammar (`SPD <0-100>`, `DIR <0|1>`,
  `STOP`, `REARM`, one command per line, `\r`/`\n`/`\r\n`/`\n\r` all
  accepted as line terminators) is deliberately just as plain-ASCII/
  human-typable as the existing CSV output — the same "don't invent a
  binary protocol without a concrete reason" rationale extended to the new
  write direction (host→MCU) this pass adds for the first time.

### 4.3 REQ-405 overspeed ceiling: 6000 RPM

REQ-405 requires enforcing "a maximum commanded/actual flywheel speed"; per
`requirements/requirements.md`, the exact ceiling is explicitly left as
"TBD by Firmware Engineer + human safety review" — a firmware-level
decision this pass had to make and record, not a value already fixed
elsewhere.

**Inputs weighed**:

- REQ-007's own floor: the reaction wheel must reach **≥3000 RPM**.
- The motor's own no-load speed range, per the schematic's own citation:
  **~20,000–22,200 RPM**.
- REQ-405's own stated rationale is fundamentally about **stored rotational
  energy**, which scales with the **square** of RPM (KE ∝ ω²) — a ceiling
  set at 2× the floor stores 4× the energy, not 2×; a ceiling at 3× the
  floor stores 9×, etc. This quadratic scaling is the single most important
  fact shaping this decision, not a linear "pick something in the middle"
  judgment.
- `hardware/schematic/bench-imu-01-design.md` §7.5.11 itself already
  proposes "~6000 RPM (2× REQ-007's own floor)" explicitly **as a numeric
  anchor for discussion, not a decision** — i.e., the schematic author
  already did the same quadratic-energy reasoning and floated a candidate
  number, but correctly declined to make it the firmware's decision for it.
- `hardware/mechanical-interface.md` (read this pass) confirms the
  Mechanical Lead's own flywheel/containment sizing is **currently based
  only on the 3000 RPM target**, and explicitly flags (lines 564–569) that
  it is waiting on this firmware ceiling decision as a real, quadratic-
  impact input for its next design phase.

**Decision: 6000 RPM.** Margin check, both directions:
- Above the 3000 RPM floor: 6000/3000 = **2.0×** RPM → **4.0×** stored
  energy.
- Below the motor's no-load range: 20000/6000 ≈ **3.33×**, 22200/6000 =
  **3.7×** RPM → the ceiling stores only about **1/11th to 1/14th**
  (1/11.1 to 1/13.7) of the motor's own no-load kinetic energy.

**Disclosed revision, not silently substituted**: this module's own
internal first-pass draft (earlier in this same session, before
`hardware/schematic/bench-imu-01-design.md` §7.5.11 and
`hardware/mechanical-interface.md`'s forward-dependency note were both
found and weighed) had independently converged on **8000 RPM** instead —
also a defensible number (2.67× the floor, 7.1× energy; 2.5–2.775× below
no-load, 1/6.25–1/7.7 of no-load energy). The ceiling was revised **down**
to 6000 RPM once the schematic's own non-binding anchor was found, for
three reasons, all disclosed here rather than quietly overwritten:
1. Both 6000 and 8000 RPM adequately clear the two-sided margin bar this
   decision needs to clear (comfortably above the floor, comfortably below
   no-load).
2. Given REQ-405's rationale is fundamentally about quadratically-scaling
   stored energy, and two candidate numbers both adequately satisfy the
   margin requirement, choosing the **lower** of the two is the more
   defensible safety-engineering choice (less stored energy at the ceiling,
   strictly less risk if the ceiling is ever reached) — there was no
   engineering reason to prefer the higher number once both were shown
   adequate.
3. Adopting the schematic's own already-published anchor (rather than an
   independently-derived different number) keeps this decision consistent
   with a number the Hardware discipline had already floated, rather than
   introducing an unexplained discrepancy between two independently-derived
   candidates for the same number.

**New downstream input this creates**: `hardware/mechanical-interface.md`'s
flywheel/containment sizing is presently based only on the 3000 RPM
*target*, not any ceiling. **6000 RPM is now a real, decided input** for the
Mechanical Lead's next containment-design phase — given the quadratic
energy relationship, this is a materially different design load than 3000
RPM (4× the stored energy), and should be picked up explicitly, not assumed
unchanged from a prior mechanical-interface revision.

**Enforcement logic** (`motor.c`'s `check_overspeed()`) — see §7.6 below for
the full detail, including the coast-down case and the spin-up FG-validity
grace period this required. This is the **feedback-side** enforcement only
— see below for the command-side layer added in a later session.

**Command-side ceiling, added in a later session** (closes Firmware
Reviewer Finding 1, HIGH, PR #14, `bench-imu-01-firmware-review.md` — see
§12 for that session's own tooling/build account): REQ-405's own literal
text has **two** distinct clauses — (a) **command-side**, "enforce a
maximum commanded flywheel speed and reject/clamp any command exceeding
it"; (b) **feedback-side**, "using the already-wired FG tachometer
feedback to verify actual speed does not exceed a defined ceiling...
command the motor to a safe/stopped state." Everything above in this
section is clause (b) — **reactive**, triggered only after FG measurement
confirms an actual overspeed. Clause (a) was not implemented until this
later session: `SPD` accepted any 0–100 duty-cycle value with no RPM-tied
ceiling of its own, so a host commanding `SPD 100` would drive the motor
open-loop toward whatever RPM that duty cycle produces — potentially far
above 6000 RPM if lightly/un-loaded, given M1's own ~20,000–22,200 RPM
no-load speed above — before `check_overspeed()` eventually caught it
after the fact.

**Decision: `MOTOR_MAX_CMD_DUTY_PCT` = 23%**, enforced by a new check
inside `cmd_spd()` (`motor.c`) that **rejects**
(`SPD_REJECTED reason=exceeds_cmd_duty_ceiling`) — not silently clamps —
any `SPD` command above it, **in addition to** (never instead of) the
existing reactive `check_overspeed()` path above. The full derivation
(with Evidence IDs) also lives in `motor.h`'s own header comment, this
document's established convention for where the detailed, primary-
source-quoted rationale lives (see §7.6); in summary:

- TI DRV10983 §8.4.5.3 "Digital PWM Input Mode Speed Control" (pages
  29–30, **DS-MTR-077**, new this session): "The speed command is
  proportional to the PWM input duty cycle" — the firmware's existing
  0–100 `SPD` value already maps linearly onto U5's own internal Speed
  Command, with no nonzero offset in this digital-PWM mode.
- TI DRV10983 §8.3.3 "Motor Speed Control" (pages 16–17, **DS-MTR-078**,
  new this session): peak output amplitude = VCC × (PWM_DCO/100); the
  same section discloses that U5's own AVS/acceleration-current-limit/
  closed-loop-accelerate functions can only **reduce** actual output
  relative to this linear estimate, never increase it — so treating
  amplitude as exactly proportional is a conservative upper bound, not an
  optimistic one.
- Combined with this project's own already-established KV-based
  no-load-speed convention (**DS-MTR-017/018**: KV=2000 RPM/V, no extra
  derating, matching M1's own published ~20,000–22,200 RPM no-load
  figures exactly) and this design's own binding worst-case `VM_MOTOR`
  envelope of **13.0V** (`hardware/schematic/bench-imu-01-design.md`
  §7.5.9 — U6's OVP does not trip anywhere within this envelope per
  §7.5.10, so 13.0V is a real, reachable worst case, not a theoretical
  one): `RPM(duty%)` is bounded above by approximately `KV × 13.0V ×
  (duty%/100) = 260 × duty%`. Solving `260 × duty% ≤ 6000` gives `duty% ≤
  23.08` → **23%** (floored for conservatism; 24% → 6240 RPM would exceed
  the ceiling).

**Confidence, marked explicitly**: the DRV10983 proportionality
statements, M1's KV rating, and the 13.0V worst-case envelope are each
**HIGH-confidence, directly-cited primary-source facts**. The
**arithmetic combination** of these facts into a single 23% duty ceiling
is a **reasoned engineering derivation**, not itself a number printed in
any one source — disclosed as such, not presented as a datasheet-quoted
figure.

**Honest limitation, disclosed**: duty-to-RPM is load-dependent for a
sensorless BLDC — real (loaded, non-worst-case-voltage) operation will
reach a lower RPM at a given duty than this no-load/worst-case estimate,
so this ceiling is a **defense-in-depth bound, not a guarantee** (the same
sense in which a fuse rating is a bound, not a promise) and may in
practice be more restrictive than strictly necessary. REQ-007's own ≥3000
RPM floor remains comfortably inside the 23%-duty no-load-equivalent
estimate (5980 RPM), so no required characterization capability is lost.
The existing reactive `check_overspeed()` path remains the authoritative,
measurement-based enforcement of the actual 6000 RPM limit, completely
unaffected by this new, additional, pre-emptive layer.

### 4.4 REQ-406 latched-fault policy: 3 events / 30 s rolling window, unified REARM

REQ-406 requires "detect and respond to motor lock conditions... to prevent
sustained fault conditions from going unaddressed," implemented as a
software layer distinct from (not a duplicate of, and explicitly not
relying solely on) U5/U6's own hardware-level auto-recovery behavior — per
ISS-021's own finding, U5's/U6's own auto-retry/auto-reset behavior is
exactly what REQ-406 exists to not rely on alone.

**Decision**: count consecutive Lock-Detection **rising edges** (a
continuously-asserted lock condition across multiple polls is one ongoing
event, not repeated new events — edge-detected via a `s_was_locked` latch
in `motor.c`) via U5's own status register, polled over I2C1 every 50 ms
while armed. **3** qualifying events within a rolling **30 second** window
→ latch a safe/stopped state (SPEED duty → 0 **and** U6's SHDN → low) →
require a deliberate **REARM** host command before resuming; never
auto-resumes on its own.

- **Why 3 events, not 1**: a single transient lock (e.g. momentary
  mechanical interference during bench handling) is plausible and
  recoverable; requiring 3 distinguishes a *repeating* problem worth
  latching the whole rail off for from an isolated one-off. Deliberately
  NOT tuned to be more lenient than this — nuisance-tripping somewhat more
  often in the ECO-008 BEMF-degraded band (§4.6) is an accepted, disclosed
  cost of not weakening this safety check (see §4.6).
- **Why 30 s**: sanity-checked against U5's own documented `tLOCK_OFF`≈5s
  auto-retry period (DS-MTR-059) — 3 of U5's own retry cycles need ≥15s,
  leaving comfortable margin inside a 30s window; short enough that a
  bench operator isn't left waiting an unreasonably long time to see the
  latch actually trip during characterization testing.
- **Why a unified REARM (not separate "clear fault" vs. "arm" commands)**:
  the very same host action — SHDN low→high, then re-commission U5 over
  I2C1 — is both the correct recovery action after this firmware's own
  REQ-405/406 trip **and** happens to also be U5/U6's own documented
  fault-reset mechanism. Specifically, `datasheets/evidence-log.md`'s
  `DS-PROT-024` ("Cycling SHDN pin voltage resets the device that has
  latched off due to a fault condition") and `DS-PROT-030` (reset via SHDN
  toggle low-to-high, UVLO toggle, or IN_SYS power-cycle) mean this single
  REARM sequence uniformly recovers from **both** this firmware's own
  latched trips **and** U6's own independent hardware overload latch (a
  different, REQ-404/overcurrent-protection-tier condition) — without
  `motor.c` needing to know or care which condition actually caused the
  rail to be off. A deliberate, favorable design coherence discovered and
  relied upon this pass, not a coincidence left undocumented.
- **Why REARM re-commissions U5 from scratch**: U5 is fully unpowered by
  SHDN going low (whether by firmware's own trip or by U6's own hardware
  latch), so it necessarily forgets its prior register-mode commissioning
  — REARM must always fully repeat `drv10983_commission()`, not merely
  toggle SHDN.
- **`MOTOR_REARM_POWERUP_DELAY_MS`=100 ms** (the pause between driving SHDN
  high and attempting I2C1 commissioning): **not** itself a datasheet-cited
  figure — no evidence-log row specifies U5's own post-power-up
  I2C-readiness delay, or U6's own precise turn-on-to-output-stable timing.
  Supporting (not determinative) evidence found this session: `DS-PROT-028`
  gives U6's own inrush-control turn-on-delay equation; evaluated at this
  board's own C17=22 nF (the slower of U6's two documented soft-start
  paths), `UVLO_ton(dly) = 742 + 49.5×22 ≈ 1831 µs ≈ 1.83 ms` — this
  firmware's chosen 100 ms is roughly a **50×** margin over that figure,
  which is reassuring but is explicitly **not** how 100 ms was derived; 100
  ms is a generously conservative round number chosen to also cover U5's
  own separate, not-independently-timed I2C-readiness delay. Flagged
  honestly as a firmware-only judgment call, revisit if real-hardware
  timing is later measured.
- **Ring-buffer correctness** (`s_lock_event_ts[MOTOR_LOCKOUT_FAULT_COUNT]`,
  a 3-element ring buffer sized directly from the same
  `MOTOR_LOCKOUT_FAULT_COUNT` constant as the trip threshold, so the two
  can never drift apart): hand-traced this pass — after each write, the
  slot the *next* write would overwrite always holds the oldest of the
  currently-retained 3 timestamps, the standard ring-buffer property this
  logic depends on. See `motor.c`'s own inline comment for the full 4-event
  trace.

### 4.5 FG capture design: interrupt-driven, not polled

**Decision**: TIM3 CH1's FG input-capture is serviced from `TIM3_IRQHandler`
(interrupt-driven), not by polling `TIM3->CCR1`/a capture flag from the
main superloop.

**Why polling was rejected** (a real design flaw this pass discovered, not
a stylistic preference): at the motor's higher operating speeds, FG edges
can arrive faster than the main superloop is guaranteed to revisit a
polling check (the superloop also services BMI270 sampling, USART2 RX
drain, and the REQ-406 I2C1 status poll, none of which are bounded to
complete faster than a high-RPM FG period). A missed capture-compare event
under pure polling would silently corrupt the derived RPM into a **falsely
low** reading — the single most dangerous failure mode for a check
(REQ-405) whose entire job is to catch *high* RPM. Interrupt-driven capture
(TIM_DIER_CC1IE unmasked, NVIC_ISER bit for `TIM3_IRQn`=16 set) guarantees
every capture event is serviced as it occurs, independent of whatever else
the superloop happens to be doing.

- **PSC=159** (10 µs/tick, derived from the unchanged 16 MHz clock, §4.1):
  chosen so the capture-to-capture interval counter has enough dynamic
  range to represent both very low RPM (long intervals) and the ceiling's
  own 6000 RPM (short intervals) without overflow, while still resolving
  RPM with adequate precision — see `tim3_fg.c`'s own header comment for
  the exact interval-to-RPM formula and its wraparound-safety
  justification.
- **Staleness detection** (`TIM3_FG_STALE_MS`=250 ms,
  `tim3_fg_is_valid()`): a capture event that hasn't refreshed within 250
  ms is reported as "not currently valid" rather than a stale, misleadingly
  "current-looking" RPM number — this is what lets `check_overspeed()`
  distinguish "motor genuinely stopped" from "FG signal has gone missing
  while something is still commanded," which matters for both the
  coast-down case (§4.8) and the spin-up grace period below.

### 4.6 Two distinct FG/BEMF caveats, both tracked (not conflated)

Two separate phenomena affect FG-based RPM measurement reliability, at two
different points in a spin-up, and this pass deliberately keeps them
distinct rather than treating them as one caveat:

1. **`Op2ClsThr` ≈103 RPM open/closed-loop commutation transition**
   (`DS-MTR-062`/`DS-MTR-063`/`DS-MTR-076`, schematic §7.5.7): a narrow
   band right at spin-up, below which U5 runs open-loop commutation before
   switching to closed-loop (BEMF-sensed) commutation. Resolved for this
   firmware's purposes by observation: by the time RPM is high enough to
   matter for REQ-405/REQ-406 (thousands of RPM), U5 has long since
   transitioned to closed-loop commutation: this transition only affects
   the very earliest instant of spin-up, which is already covered by the
   `MOTOR_FG_SPINUP_GRACE_MS`=3000 ms grace window (§7.6) for an unrelated
   reason (FG simply hasn't captured its first edge yet).
2. **ECO-008's own broader 500–1500 RPM BEMF-sensing-degrades caveat**
   (`validation/change-log.md` ECO-008, schematic §7.5.7): a **wider** band
   that persists **in closed-loop operation**, unlike (1). Tracked
   explicitly per ECO-008's own directive that this "must show up as a
   real, non-hand-waved item in the firmware bring-up plan":
   - **Does not threaten the 6000 RPM ceiling itself** — the degradation
     described is signal noise/jitter in BEMF sensing, not a systematic
     frequency multiplication/division error that could make an
     above-ceiling RPM misreport as below-ceiling.
   - **CSV RPM readings may look visibly noisier** while transiting this
     band — disclosed to the operator via the boot banner
     (`motor_init()`'s printed banner), not silently hidden, and not
     "fixed" with any smoothing/filtering (which would itself risk masking
     a genuine overspeed reading — out of scope per this pass's hard
     "no control-loop-flavored math" fence in any case).
   - **Lock-Detection may nuisance-trip somewhat more often** while
     transiting this band — deliberately **NOT** suppressed or
     specially-cased in `check_lock_faults()`. Suppressing fault detection
     in a specific RPM band to reduce nuisance trips would directly
     undermine REQ-406's own safety purpose; this is disclosed as expected,
     accepted behavior (via the boot banner) rather than coded around.

### 4.7 REQ-405 coast-down limitation, disclosed

`check_overspeed()` runs whenever the motor subsystem is armed, **regardless
of commanded duty** — not gated on `duty_pct != 0`. This is a deliberate
refinement, not an oversight: gating the check on nonzero duty would miss a
flywheel **coasting down** above the ceiling immediately after a plain
`STOP` command, while SHDN is still high and U5/FG are both still fully
powered and reporting validly. `STOP` alone must not be able to defeat
REQ-405.

**Disclosed limitation**: this only holds while FG is actually valid. If FG
capture itself has stopped being serviceable (e.g. SHDN has already been
dropped, or the FG signal path itself has failed) there is no live
tachometer signal left to check against — this is an inherent property of
software running on the same rail it's trying to police (once power is
truly removed from U5, there is nothing left for firmware to read), not a
gap in this logic's design. `motor.c`'s overspeed check correctly
distinguishes "FG currently invalid with zero duty" (the ordinary, benign
at-rest case) from "FG was valid and has since gone invalid with duty still
commanded nonzero" (treated as a fault, zero grace period) — see §7.6 for
the exact state machine.

### 4.8 Spin-up FG-validity grace period: `MOTOR_FG_SPINUP_GRACE_MS`=3000 ms

A bounded grace period after a 0→nonzero `SPD` command, during which "FG has
not yet captured a single edge" is treated as a normal, momentary spin-up
transient rather than an immediate fault. 3000 ms is a **firmware-only**
judgment call — no datasheet gives an expected open-loop ramp time for this
specific motor+flywheel+duty-cycle combination — chosen to comfortably
exceed any plausible bench ramp time; revisit if real-hardware timing is
later measured and found to need more margin. Once FG has been observed
valid even once during the current spin-up, this grace period no longer
applies for that spin-up (see §7.6): a *regression* from valid to invalid
with duty still nonzero is always treated as an immediate fault, not a
transient.

### 4.9 `main.c`: keeping the IMU and motor subsystems independent, including at the failure-mode level

The pre-existing (Rev ≤2) `main.c` looped forever
(`for (;;) { led_toggle(); delay_ms(100); }`) if `bmi270_init()` failed —
harmless when the IMU was the only subsystem on the board, but a genuine bug
once a second, functionally-independent subsystem (Rev 3's motor driver)
exists: a BMI270 bring-up failure would have silently prevented the motor
subsystem from ever initializing at all, a much stronger (and unintended)
form of coupling between the two subsystems than merely "no code path reads
one and drives the other." **Fixed**: a `bmi_ok` flag now gates only the
IMU-specific sampling branch; the LED heartbeat switches to a faster,
distinct blink rate (`LED_BLINK_FAST_MS`=100 ms) while `!bmi_ok`, preserving
the same "firmware alive, IMU degraded" visual signal the old permanent
fast-blink loop gave a bench operator, without costing the rest of the
board's availability. `i2c1_init()`/`tim1_pwm_init()`/`tim3_fg_init()`/
`motor_init()` are all called unconditionally, never gated on `bmi_ok`.

## 5. Peripheral bring-up detail (register-level facts, all Evidence-ID-cited)

All register base addresses, struct offsets, and bit positions below were
independently confirmed against STMicroelectronics' own official
CMSIS-Device header for this part family
(`datasheets/stmicroelectronics_cmsis_device_g0_master.md`) — not from
memory, not guessed. See `firmware/bench-imu-01/src/stm32g031_regs.h` for
the full set of definitions and their inline Evidence citations.

| Peripheral | Key facts | Evidence |
|---|---|---|
| Memory map | FLASH_BASE=0x08000000 (64K), SRAM_BASE=0x20000000 (8K) | DS-MCU-055 |
| Base addresses | RCC=0x40021000, GPIOA=0x50000000, GPIOB=0x50000400, USART2=0x40004400, I2C2=0x40005800 | DS-MCU-056 |
| GPIO/RCC struct layout | MODER/OTYPER/PUPDR/ODR/BSRR/AFR offsets; RCC IOPENR/APBENR1/APBENR2/CSR offsets | DS-MCU-057 |
| RCC clock-enable bits | GPIOAEN=bit0, GPIOBEN=bit1 (IOPENR); USART2EN=bit17, I2C2EN=bit22, PWREN=bit28 (APBENR1) | DS-MCU-058 |
| RCC reset-reason bits | PINRSTF=bit26, PWRRSTF=bit27, SFTRSTF=bit28, IWDGRSTF=bit29, WWDGRSTF=bit30, RMVF=bit23 (CSR) | DS-MCU-059 |
| I2C register layout/bits | CR1/CR2/ISR offsets and fields (SADD, START, STOP, NBYTES, AUTOEND, TXIS, RXNE, NACKF, STOPF, TC, BUSY) | DS-MCU-060 |
| USART register layout/bits | CR1/ISR/BRR offsets and fields (UE, RE, TE, RXNE, TC, TXE) | DS-MCU-061 |
| GPIO alternate functions | PA2/PA3=AF1 (USART2), **PA11/PA12=AF6 (I2C2, corrected — §3)**, independently re-corroborated against two further official ST sources (STM32CubeG0's NUCLEO-G031K8 I2C2 example, `stm32g0xx-hal-driver`'s `GPIO_AF6_I2C2` numeric definition) | DS-MCU-062 (correction cross-referenced), DS-MCU-073, DS-MCU-068, DS-MCU-077 |
| I2C timing (400 kHz @ 16 MHz) | TIMINGR=0x00310309 (ST's own published value, AN4235 Table 11) | DS-MCU-063 |
| **I2C1 base/RCC (Rev 3)** | I2C1_BASE=0x40005400; RCC_APBENR1_I2C1EN=bit21; PB6/PB7=AF6 | DS-MCU-074 |
| **TIM1 base/RCC (Rev 3)** | TIM1_BASE=0x40012C00; RCC_APBENR2_TIM1EN=bit11; PA8=AF2 | DS-MCU-075 |
| **TIM3 base/RCC/IRQ (Rev 3)** | TIM3_BASE=0x40000400; RCC_APBENR1_TIM3EN=bit1; PA6=AF1; TIM3_IRQn=16; NVIC_ISER=0xE000E100; TIM_DIER_CC1IE=bit1 | DS-MCU-076 |

`gpio.c` configures the I2C2 (post-fix, PA11/PA12) and I2C1 (PB6/PB7) pins
identically: **open-drain** (not push-pull) — I2C is a wired-AND bus, and
the schematic provides external pull-ups for both buses (R3/R4 for I2C2,
and the schematic's own I2C1 pull-up provisioning for U5's commissioning
bus). `i2c1.c` is a direct structural mirror of `i2c2.c` (same "I2C
peripheral v2" IP block, same polling-mode/no-interrupt design), instance
renamed I2C2→I2C1 throughout, reflecting that these are two independent
peripheral instances serving two functionally-independent subsystems, not
a shared bus. Both drivers' polling-mode (no-interrupt) design also matches
the fact that no I2C interrupt of either instance is unmasked at the NVIC
(`startup_stm32g031xx.c`).

## 6. BMI270 driver detail

*(Unchanged from the prior firmware pass.)* All register addresses and the
exact chunked-upload protocol are sourced from Bosch's own official driver
(DS-IMU-078 through DS-IMU-088) — see `bmi270.c` for the full implementation
and inline citations: soft reset → CHIP_ID check → disable advanced power
save → disable config-load flag → upload the 8192-byte configuration blob
in 32-byte, word-addressed chunks → finalize + poll `INTERNAL_STATUS` →
configure ODR (100 Hz) + enable sensors → 12-byte burst sample read. This
firmware's IMU behavior is unaffected by either of this pass's two
deliverables, other than the I2C2 GPIO pin correction in §3 (the peripheral
instance and all register-level BMI270 behavior are identical).

## 7. Motor Driver + Reaction Wheel (U5 DRV10983 + U6 TPS26631PWPR) bring-up detail

All facts below are sourced from the DRV10983 datasheet (SLVSCP6H) and the
TPS26631PWPR datasheet, both already logged in `datasheets/evidence-log.md`
(DS-MTR-* and DS-PROT-* rows) — cross-checked against the schematic's own
citations of the same rows (§7.5.x), not re-derived independently.

### 7.1 GPIO/pin roles (recap from §1)

| Pin | Peripheral | Role |
|---|---|---|
| PA8 | TIM1_CH1 (AF2), PWM out | SPEED — duty-cycle speed command to U5 |
| PA6 | TIM3_CH1 (AF1), input capture | FG — tachometer feedback from U5, via R6 pull-up |
| PB1 | Plain GPIO out | DIR — direction command to U5 |
| PB6/PB7 | I2C1 (AF6) | U5's commissioning/status interface |
| PA9 | Plain GPIO out | U6 SHDN — motor-rail enable; default/floating = OFF (R11 pulldown, REQ-403 fail-safe intent) |

`gpio_dir_set(int reverse)`/`motor_shdn_set(int enable)` (`gpio.c`) are
simple `BSRR` accessors, matching the existing `led_toggle()`-style
convention in this codebase. Polarity: `motor_dir_set(1)` = reverse (PB1
high), `motor_dir_set(0)` = forward (PB1 low, the power-on-reset default);
`motor_shdn_set(1)` = enable (PA9 high), `motor_shdn_set(0)` = disable (PA9
low, the power-on-reset/default-safe state, matching R11's own pulldown
intent even before firmware runs).

### 7.2 SPEED PWM (TIM1 CH1, `tim1_pwm.c`)

20 kHz PWM (above the audible range, and comfortably inside U5's own
accepted PWM-input frequency range per its datasheet), 0–100% duty,
`tim1_pwm_set_duty_pct()` internally clamps out-of-range input as a first,
trivial layer of input sanitization — the substantive, FG-measurement-based
enforcement (REQ-405) lives in `motor.c`, not here.

### 7.3 FG tachometer capture (TIM3 CH1, `tim3_fg.c`)

Interrupt-driven (§4.5) input capture, PSC=159 (10 µs/tick). RPM is derived
from the elapsed ticks between consecutive rising-edge captures inside
`TIM3_IRQHandler`; `tim3_fg_get_rpm()` returns the most recently computed
value, `tim3_fg_is_valid()` reports whether a capture has refreshed within
`TIM3_FG_STALE_MS`=250 ms. All ISR-shared state uses `volatile`
qualification (unlike `motor.c`'s own plain statics, which are touched only
from non-ISR context) — see `tim3_fg.c`'s own header comment for the
interval→RPM formula.

### 7.4 U5 (DRV10983) commissioning sequence (`drv10983.c`, over I2C1)

Implements U5's manufacturer-mandated EEPROM commissioning sequence
(`drv10983_commission()`), sourced from DS-MTR-071 (Table 8's register map)
and the schematic's own citation of it:

1. Write `SysOpt9` (register `0x2B`) with the `SpdCtrlMd` bit set for
   PWM speed-control mode, target value **`0x0E`** (the register's own
   default `0x0C` with bit 1 set) — **a carried-over arithmetic error
   (0x4E) was caught and corrected during this session's own design work,
   before it ever reached committed code** (confirmed via `grep`; recorded
   here transparently as a concrete self-check-rigor example, not smoothed
   over).
2. Verify-readback the register after writing it — `drv10983_commission()`
   returns `DRV10983_ERR_VERIFY` (distinct from `DRV10983_ERR_I2C`) if the
   readback doesn't match, so a REARM failure can be reported to the
   operator with the correct, distinguishing reason.
3. `drv10983_read_status()` (Status register) / `drv10983_read_fault_code()`
   (FaultCode register) — both single-byte reads, used by `motor.c`'s
   REQ-406 lock-fault check.
4. `drv10983_read_motor_speed_raw()` — confirmed this session (re-fetched
   from the primary DRV10983 PDF directly) that `MotorSpeed1`/`MotorSpeed2`
   requires **two separate sequential single-byte reads** (MSB then LSB),
   not one multi-byte burst read — implemented accordingly. (Not currently
   consumed by `motor.c`, which derives RPM from FG capture instead — kept
   available as a driver-level primitive since it is part of U5's real
   register interface, for a future consumer if ever needed, but not wired
   into this pass's own safety/telemetry logic to avoid an unused/
   speculative dependency.)

`DRV10983_STATUS_MTRLCK = (1u<<4)` — the Lock-Detection bit polled by
`motor.c`'s `check_lock_faults()`.

### 7.5 U6 (TPS26631PWPR) supervisory switch

Firmware only ever drives SHDN as a simple GPIO (§7.1) — U6's own internal
current-limit/OVP/UVLO/thermal protection logic (REQ-404) is autonomous
hardware behavior, not something firmware configures or polls a register
for. The only firmware-relevant U6 facts are its default-OFF power-up state
(already a hardware fact, R11) and its documented SHDN-toggle fault-reset
behavior (`DS-PROT-024`/`DS-PROT-030`, §4.4) which `cmd_rearm()` relies on.

### 7.6 REQ-405/406 orchestration (`motor.c`)

`motor.c` is the orchestration layer above the register-level drivers above
— it never touches `stm32g031_regs.h` or I2C1 directly, only calls into
`gpio.h`/`tim1_pwm.h`/`tim3_fg.h`/`drv10983.h`/`usart2.h`. Public API:
`motor_init()`, `motor_handle_rx_byte(uint8_t)`, `motor_tick(uint32_t
now_ms)`. See `motor.h`'s own extensive header comment for the full design
rationale (this document summarizes it; `motor.h` is the more detailed
reference) and `motor.c`'s inline comments for the exact state machine.

**`check_overspeed(now)`** (REQ-405, feedback-side/reactive), runs every
`motor_tick()` while armed, regardless of commanded duty (§4.7):
```
if FG valid:      remember "FG has been valid this spin-up"; trip if RPM > 6000.
if duty == 0:      benign at-rest case, no action.
if FG was valid earlier this spin-up, now invalid: trip immediately (zero grace).
else (FG never valid yet this spin-up): trip only after MOTOR_FG_SPINUP_GRACE_MS (3000 ms) of continued invalidity.
```

**`cmd_spd()`'s command-side ceiling** (REQ-405, pre-emptive — added in a
later session, closes Firmware Reviewer Finding 1; see §4.3/§12): rejects
(`SPD_REJECTED reason=exceeds_cmd_duty_ceiling`) any `SPD` value above
`MOTOR_MAX_CMD_DUTY_PCT`=23 **before** it is ever applied to
`tim1_pwm_set_duty_pct()` — independent of, and in addition to,
`check_overspeed()`'s own post-hoc, FG-measurement-based trip above. See
§4.3 for the full duty-to-RPM derivation and its disclosed confidence and
limitations.

**`check_lock_faults(now)`** (REQ-406), rate-limited to `MOTOR_STATUS_POLL_MS`
=50 ms while armed: polls U5's Status register over I2C1, edge-detects a
new Lock-Detection assertion, records it into a 3-slot ring buffer, and
trips once 3 events are recorded within `MOTOR_LOCKOUT_WINDOW_MS`=30000 ms.
An I2C1 read failure is reported but does **not** itself trip REQ-406 (a
communication fault is a different failure class than an actual motor lock
— see §4.4). The Status register read here is **cached**
(`s_last_status_reg`/`s_have_status_reg`) and reused by the CSV emitter
below, rather than issuing a second, separately-timed I2C1 read — this
guarantees the CSV's reported lock state always matches exactly what the
safety logic itself most recently observed, and avoids doubling I2C1 bus
traffic.

**`trip_safe_state(reason)`**: shared by both REQ-405 and REQ-406 —
`tim1_pwm_set_duty_pct(0)`, `motor_shdn_set(0)`, latches (`s_armed=0`,
`s_fault_latched=1`), reports `MOTOR_TRIP reason=<reason> -- REARM
required`. Always **latching**, never a momentary zero-then-auto-resume —
an unlatched response would risk oscillating right at the ceiling boundary
(repeatedly tripping and un-tripping as measured RPM hovers near 6000 RPM),
which is worse than a single deliberate latch requiring a human decision to
clear.

**Host command grammar** (one line per command, `SPD`/`DIR` with an
argument, `STOP`/`REARM` bare):

| Command | Effect | Rejected when |
|---|---|---|
| `SPD <0-100>` | Sets PWM duty %; a 0→nonzero transition (re)starts the REQ-405 spin-up grace window | Not armed, or requested duty > `MOTOR_MAX_CMD_DUTY_PCT`=23 (REQ-405 command-side ceiling, §4.3/§7.6 — added in a later session) |
| `DIR <0\|1>` | Sets direction (0=forward, 1=reverse) | Not armed, or duty≠0 (firmware-only policy — commutation-direction-reversal-under-load has not been verified safe this bring-up pass) |
| `STOP` | Zeroes duty only — does NOT disarm/drop SHDN/require REARM | Never (always allowed, idempotent no-op if already stopped) |
| `REARM` | SHDN low→high, `delay_ms(100)`, re-commission U5, reset all latch/spin-up/fault-history state, arm | Reports `REARM_FAILED reason=i2c_error\|verify_mismatch` on commissioning failure; does not itself latch a new fault |

**A critical latent bug caught and fixed during this pass's own design
work, before ever reaching committed code**: `cmd_rearm()`'s success path
must reset `s_ever_fg_valid_since_spinup` (and `s_was_locked`, the ring
buffer, and the cached status-register fields) to their startup defaults.
If `s_ever_fg_valid_since_spinup` were left `true` from a previous spin-up,
the very next spin-up attempt after any REARM would receive **zero** grace
period (since the "was valid, now isn't" branch is zero-grace by design)
and would immediately trip on the first check after a nonzero `SPD` command
— because FG has not captured its first edge of the new spin-up yet. Left
unfixed, this would have made the motor **permanently unable to spin up
again** after a single fault-and-REARM cycle. Caught by hand-tracing the
REARM path against every piece of state `check_overspeed()`/
`check_lock_faults()` reads, before writing `motor.c` to disk.

**CSV telemetry** (`emit_csv_line()`, every `MOTOR_CSV_PERIOD_MS`=200 ms,
5 Hz):
```
MOTOR,millis_ms,armed,fault_latched,duty_pct,dir_reverse,fg_valid,rpm,mtrlck,lock_event_count
```
`"NA"` (not a fabricated `0`) is used for `rpm` when FG is invalid and for
`mtrlck` when not currently armed/polled — reporting a fabricated `0` could
be misread as an affirmative "confirmed zero RPM"/"confirmed not locked,"
which would be false and, for `mtrlck` specifically, actively misleading
about safety-relevant state.

**Host command RX parsing**: hand-rolled (no libc, matching this codebase's
existing convention — `usart2.c`'s own hand-rolled `usart2_write_u32()`).
`\r`, `\n`, `\r\n`, and `\n\r` are all accepted as line terminators; a
CRLF/LFCR pair is recognized and its second byte suppressed (not
double-dispatched as a spurious empty line); an over-long line is
discarded with `ERR line_too_long` reported at its terminator; a bare blank
line is silently ignored.

**Disclosed RX-reliability limitation**: `main.c` drains USART2 RX with a
plain, non-blocking polling read (`usart2_read_byte()`), the same
discipline used elsewhere in this firmware, deliberately **not** promoted
to an interrupt-driven RX path the way TIM3's FG capture was (§4.5) —
because, unlike FG capture (where polling was *proven* unreliable at
speed), a human operator typing short bench commands has no comparable
high-rate/missed-edge risk. USART2's single-byte hardware RX buffer means
at most one byte could theoretically be lost if two arrive back-to-back
while the superloop happens to be inside `check_lock_faults()`'s I2C1 poll;
the worst case is a desynced/garbled command line (recoverable by retyping
it), and none of REQ-405/406's own safety behavior depends on RX
reliability — only on the independently-serviced FG/status sensing paths.
An accepted, disclosed simplification, not an oversight.

## 8. Main loop

`main.c`: `clock_init()` → `gpio_init()` → `usart2_init()` →
`systick_init()` → report reset reason (§2) → `i2c2_init()` →
`bmi270_init()` (§6; failure now only disables IMU sampling and switches
the heartbeat blink rate, per §4.9 — it no longer blocks anything) →
`i2c1_init()` → `tim1_pwm_init()` → `tim3_fg_init()` → `motor_init()` (all
four unconditional). The superloop, every pass: LED heartbeat (rate
depending on `bmi_ok`), IMU sampling at 100 Hz if `bmi_ok` (unchanged from
Rev ≤2), `motor_tick(now)` (REQ-405/406 checks + 5 Hz CSV, §7.6,
unconditional), then drain all currently-available USART2 RX bytes into
`motor_handle_rx_byte()`.

## 9. Real build attempt (this session)

`arm-none-eabi-gcc` 16.2.0 was re-confirmed present this session (§0). A
full clean build (`make clean && make all`) was run covering **all**
source files — the pre-existing IMU firmware plus every file added this
pass (`i2c1.c`, `tim1_pwm.c`, `tim3_fg.c`, `drv10983.c`, `motor.c`, plus the
modified `gpio.c`/`clock.c`/`stm32g031_regs.h`/`startup_stm32g031xx.c`/
`i2c2.c`/`usart2.c`/`main.c`).

**Result: succeeded, zero warnings, zero errors** — captured stdout and
stderr separately and confirmed both contain no "warning"/"error" text, not
merely "the exit code was 0." Final image (`arm-none-eabi-size`):
**14,752 bytes `.text`/`.rodata`**, **108 bytes `.bss`**, **0 bytes
`.data`** — comfortably within the STM32G031K8T6's 64 KB flash / 8 KB RAM
(DS-MCU-055). `motor.c` alone compiles to 2,844 bytes `.text` / 88 bytes
`.bss` when checked standalone.

**An additional empirical check performed this session, beyond "it
compiles"**: because `TIM3_IRQHandler` feeds the safety-critical FG/RPM
measurement path, the linked ELF's `.isr_vector` section was disassembled
(`arm-none-eabi-objdump -s -j .isr_vector`) and cross-checked against
`arm-none-eabi-nm`'s reported address for `TIM3_IRQHandler`
(`0800089c`). The vector table's word at byte offset `0x80` (vector index
32 = 16 core exceptions + `TIM3_IRQn`=16, matching `startup_stm32g031xx.c`'s
own vector-table placement) reads `0x0800089d` — exactly
`TIM3_IRQHandler`'s address with the expected Cortex-M "Thumb bit" (bit 0)
set, confirming the interrupt is correctly wired end-to-end in the actual
linked binary, not merely "looks right in the source."

**A further check performed this session, specifically for this merge's own
GPIOA/GPIOB coexistence claim (§3)**: `arm-none-eabi-objdump -d` was run
against the linked `.elf` and grepped for both port base addresses.
`GPIOB_BASE` (`0x50000400`) appears in the literal pool **inside
`gpio_init()`'s own disassembly** (used for the PB1/PB6/PB7 motor pins) and
again inside `motor_dir_set()`/`motor_shdn_set()` — confirmed present and
reachable, not stripped. `GPIOA_BASE` (`0x50000000`) does not appear as a
literal-pool word at all; instead, `gpio_init()`'s first two instructions
(`movs r3, #160` / `lsls r3, r3, #23`) synthesize it directly
(`0xA0 << 23 == 0x50000000`) — a compiler optimization (page-aligned
constants are cheaper to build with a shift than to spend a 4-byte literal
pool slot on), not an indication it is missing; independently confirmed via
`python3 -c "print(hex(0xA0 << 23))"` → `0x50000000`. `arm-none-eabi-nm`
also confirms `gpio_init`, `motor_dir_set`, `motor_shdn_set`, `i2c1_init`,
`i2c1_write`, `i2c1_read`, and `motor_tick` all link successfully. Finally,
`grep -rn "PB10\|PB11" src/` finds only correctly-framed historical/
corrective comments explaining the old, wrong pin assignment and why it
changed — no current-fact claim anywhere in source that the IMU (or
anything else) still uses PB10/PB11.

This firmware was **not** flashed to real hardware — none exists in this
environment (§0).

## 10. Self-check against `.github/skills/firmware-bringup/SKILL.md`'s checklist

1. **Pin/peripheral instance fidelity** — every Rev 3 pin (PA6/PA8/PA9/
   PB1/PB6/PB7) and the corrected IMU I2C2 pins (PA11/PA12) re-verified
   directly against the schematic document itself this session, not from a
   task-prompt summary; I2C1/I2C2 base addresses confirmed distinct
   (0x40005400 vs 0x40005800). PA11/PA12=AF6 additionally cross-confirmed
   against two further official ST sources (STM32CubeG0's NUCLEO-G031K8
   I2C2 example, `stm32g0xx-hal-driver`'s `GPIO_AF6_I2C2` definition,
   DS-MCU-068/077 — see §3), not assumed by convention or carried over from
   the prior (incorrect) PB10/PB11 citation. ✅
2. **Clock configuration correctness** — HSI16/16 MHz unchanged and stated;
   TIM1/TIM3 prescalers and I2C1's TIMINGR all derived from/verified
   against this same, single clock source. ✅
3. **Manufacturer-mandated sequence completeness** — BMI270's full sequence
   unaffected by this pass; U5's EEPROM commissioning sequence (SysOpt9/
   SpdCtrlMd) implemented per DS-MTR-071, including a caught-and-corrected
   arithmetic error (§7.4) before it reached committed code. ✅
4. **Vendored opaque data provenance** — unaffected by this pass (no new
   opaque calibration blob introduced; U5's commissioning is ordinary
   register writes, not an opaque binary upload). N/A this pass. ✅
5. **Register bitfield correctness** — every new RCC/GPIO/I2C1/TIM1/TIM3/
   DRV10983 constant traces to a DS-MCU-/DS-MTR- Evidence ID in
   `datasheets/evidence-log.md`; no uncited numeric register fact
   introduced. ✅
6. **Host communication framing consistency** — 115200/8N1 unchanged; the
   motor subsystem's new `MOTOR,` CSV tag and command grammar are both
   documented consistently across this document, `motor.h`, and (pending)
   `README.md`. ✅
7. **Scope-boundary compliance** — no PID/attitude-control/sensor-fusion
   code anywhere; no code path reads the IMU and drives the motor or vice
   versa (verified by inspection: `motor.c` never includes `bmi270.h` or
   references any IMU symbol, and `bmi270.c`/`main.c`'s IMU branch never
   references any motor symbol other than the two independent, side-by-side
   calls in `main()`). REQ-405/406 are bounded safety cutoffs, not control
   loops — neither computes an error term between a desired and an actual
   orientation/attitude. ✅
8. **Tooling-honesty compliance** — §0/§9 state exactly what was
   re-verified, built, and NOT run on hardware this session; no overstated
   claim found on re-read. ✅
9. **Evidence traceability** — every new register constant added this pass
   traces to a specific Evidence ID row; the previously-flagged staleness
   (DS-MCU-062's stale text, ISS-026's dangling DS-MCU-068 citation,
   `validation/bring-up-procedure.md`'s stale PB10/PB11 mentions) has since
   been corrected by a separate citation-hygiene pass (`validation/
   change-log.md` ECO-016) — re-confirmed fixed on this re-read, not
   silently assumed. ✅
10. **Requirement-vs-schematic consistency** — REQ-004/SW1 discrepancy
    (§2, pre-existing) and the ISS-027 IMU-pin defect (§3, this pass) are
    both documented as discrepancies-found-and-resolved-against-the-real-
    schematic, not silently reconciled. ✅
11. **REQ-405/406 safety-ceiling/policy reasoning is explicit, not
    arbitrary** (new checklist item this pass, specific to this cycle's
    safety-relevant deliverables) — §4.3/§4.4 both show numeric derivation,
    margin checks in both directions, and an honestly-disclosed revision
    where applicable. ✅

**Verdict**: self-check clean, no findings requiring rework. No independent
Firmware Reviewer exists yet (`docs/architecture-evolution.md` §32) — per
that section's documented scope decision, this self-check stands in for
independent review this round; per this agent's own escalation triggers,
the growing safety-relevant surface area (this pass adds two real
latched-safety behaviors on top of the prior pass's pure sensor bring-up)
is flagged to the Hardware Lead in the final report as a candidate reason
to consider introducing that role before the next firmware cycle, not
silently absorbed as "more of the same." **On the IMU I2C2 pin fix
specifically** (§3): an additional, ad hoc independent verification pass
was separately run against just that fix by a parallel effort (not a
formal Firmware Reviewer gate, which still does not exist) — its
from-first-principles re-derivation is folded into §3's own evidence
account above rather than kept as a separate section, since it re-confirms
(not contradicts) everything §3 already states.

## 11. Handoff

**To**: Hardware Lead. **Artifacts**: this document; the firmware source
tree (`firmware/bench-imu-01/{src,linker,Makefile}`), including new files
`i2c1.h/c`, `tim1_pwm.h/c`, `tim3_fg.h/c`, `drv10983.h/c`, `motor.h/c`;
`firmware/bench-imu-01/README.md` (updated); new Evidence ID rows
`DS-MCU-073` through `DS-MCU-076` and `DS-MTR-072` through `DS-MTR-076`
(`datasheets/evidence-log.md` — added in a prior window this session, not
this document's own edit scope to re-verify further here); a draft
`validation/change-log.md` ECO entry (delivered in this pass's final report
for the Hardware Lead to add, per that file's ownership). **Also
incorporated this pass** (from a parallel effort's independent
re-derivation of the same IMU I2C2 pin fix, folded into §3 above rather
than kept separate): Evidence ID rows `DS-MCU-068` (unchanged number) and
`DS-MCU-077` (renumbered from that effort's own local "DS-MCU-069", which
collided with this document's pre-existing DS-MCU-069 motor pin-allocation
citation) in `datasheets/evidence-log.md`; two new datasheet metadata
records, `datasheets/stmicroelectronics_stm32cubeg0_master.md` and
`datasheets/stmicroelectronics_stm32g0xx-hal-driver_master.md` — all
already resolved/committed as part of this same merge, outside this
document's own edit scope to re-verify further here.

**Open items / escalations**:
- **New downstream input for Mechanical Lead**: the REQ-405 6000 RPM
  ceiling (§4.3) is new, decided, quadratic-impact input for
  `hardware/mechanical-interface.md`'s flywheel/containment sizing, which
  is currently based only on the 3000 RPM target. Flagged, not resolved
  here (out of this role's scope).
- **Pre-existing staleness, not fixed by this pass** (§3): `DS-MCU-062`'s
  stale PB10/PB11 text; ISS-026's dangling `DS-MCU-068` citation;
  `validation/bring-up-procedure.md` line 42's stale PB10/PB11 checklist
  item.
- **Pre-existing citation typo, not fixed by this pass**: `DS-MTR-062`'s
  own text cites "ECO-007" where "ECO-008" is the correct BEMF-caveat ECO
  (found while researching §4.6/§7.6).
- The AN4235 TIMINGR value (`DS-MCU-063`) remains flagged at
  moderate-not-highest confidence from the prior firmware pass (unchanged
  this pass).
- **REQ-405/406 real-hardware timing judgment calls, flagged for
  revisit once real hardware exists**: `MOTOR_FG_SPINUP_GRACE_MS`=3000 ms
  and `MOTOR_REARM_POWERUP_DELAY_MS`=100 ms are both firmware-only,
  non-datasheet-derived choices (§4.4/§4.8) — reasoned and disclosed, not
  arbitrary, but not empirically measured either.
- **Growing safety-relevant surface area**: flagged above (§10) as a
  candidate reason to consider a Firmware Reviewer role before the next
  cycle, per this agent's own escalation triggers.
- No independent Firmware Reviewer role exists yet — see
  `docs/architecture-evolution.md` §32 for the documented future trigger.

I have not declared this firmware "tested" or "hardware-verified" anywhere
in this document — per §0, no physical board exists this session.

## 12. Addendum: REQ-405 command-side ceiling (Firmware Reviewer Finding 1 fix, later session)

**This section covers a separate, later session** from the rest of this
document (§§0–11 above), responding to the first-ever Firmware Reviewer
cycle's own review of the firmware §§0–11 describe (PR #14,
`firmware/bench-imu-01/bench-imu-01-firmware-review.md`) — the exact
"Firmware Reviewer role" §10/§11 above flagged as not-yet-existing. §§0, 9,
10, and 11 above are left exactly as that earlier session wrote them — an
accurate record of what was verified/self-checked/handed off *then* —
rather than silently edited to describe a different session's own work;
this addendum is where *this* session's own tooling re-verification, fix,
and build result are recorded, following this document's own "disclosed
revision, not silently substituted" convention (§4.3's 8000→6000 RPM
revision is this document's own precedent for that pattern).

**Finding addressed**: Finding 1 (HIGH) — REQ-405's own literal text has
two clauses, command-side ("reject/clamp any command exceeding [the
ceiling]") and feedback-side ("verify actual speed does not exceed a
defined ceiling... command the motor to a safe/stopped state"). Only the
feedback-side clause was implemented (`check_overspeed()`); the
command-side clause was not — `cmd_spd()` accepted any 0–100 duty-cycle
value with no RPM-tied ceiling of its own. Full technical content
(derivation, Evidence IDs, confidence marking, honest limitation) is
folded directly into §4.3 above and `motor.h`'s own header comment, not
duplicated here — §4.3 is "the REQ-405 section" a future reader would look
at first, so that is where it belongs.

**Tooling honesty, re-verified fresh this session** (not assumed from §0's
own prior-session result, per this project's own tooling-honesty
discipline): `arm-none-eabi-gcc` 16.2.0 confirmed present again (same
toolchain/version as §0). `make clean && make` re-run over the full
source tree. **Result: succeeded, zero warnings, zero errors** —
stdout/stderr both checked directly for "warning"/"error" text, not
inferred from exit code alone. Still not flashed to real hardware — none
exists in this environment (unchanged from §0).

**Self-check against `.github/skills/firmware-bringup/SKILL.md`'s
checklist, for this change specifically** (not a full re-run of every item
in §10, which remains that earlier session's own accurate account of its
own, different, deliverables — only the items this specific change
actually touches):
- **Register bitfield/datasheet correctness**: the two new register-level
  facts this change relies on (DS-MTR-077, DS-MTR-078) trace to specific
  DRV10983 datasheet sections and page numbers, added to
  `datasheets/evidence-log.md` — no uncited numeric claim introduced. ✅
- **Scope-boundary compliance**: the new check is a static threshold
  compare against a fixed constant (`val > MOTOR_MAX_CMD_DUTY_PCT` inside
  `cmd_spd()`) with no error term, no integrator, and no continuous
  adjustment of output based on measured feedback — a clamp/reject on the
  *input* command, categorically distinct from closed-loop control,
  matching `motor.h`'s own scope-fence framing (top of that file, "no
  controller, no error term, no integrator"). ✅
- **Existing behavior preserved**: the existing reactive
  `check_overspeed()`/`trip_safe_state()` path and all REQ-406 logic were
  confirmed byte-for-byte unchanged by direct re-read of the modified
  files, not assumed from the size of the diff alone. ✅
- **Evidence traceability**: `datasheets/evidence-log.md` and
  `datasheets/texasinstruments_drv10983_slvscp6h.md`'s own metadata record
  both updated for the two new Evidence IDs this change introduces. ✅
- **Not self-declared resolved**: this finding is **not** marked RESOLVED
  in `bench-imu-01-firmware-review.md` by this session — that document is
  the Firmware Reviewer's own artifact, not this role's to edit. A fresh,
  independent Firmware Reviewer confirmation pass is the correct next
  step, per this project's standard reviewer-loop-back-then-reverify
  pattern, flagged to the Hardware Lead in this session's own final report
  rather than decided here. ✅

**Handoff addendum**: new Evidence ID rows `DS-MTR-077`/`DS-MTR-078`
(`datasheets/evidence-log.md`), plus a corresponding update to
`datasheets/texasinstruments_drv10983_slvscp6h.md`'s own metadata record.
No file outside `firmware/bench-imu-01/src/motor.c`,
`firmware/bench-imu-01/src/motor.h`, this document, and the evidence-log
files above was modified by this session. **Open item, same as flagged in
§11 above and not yet resolved**: no independent Firmware Reviewer role
existed when §§0–11 were written; one now does (it is what produced
Finding 1 in the first place), and the Hardware Lead is expected to
dispatch a fresh instance of it to confirm this specific fix before
Finding 1 is marked resolved — this session does not make that
determination itself.
