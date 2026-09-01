# Requirements

Status: **APPROVED** (2026-08-30, human Chief Engineer, via ask_user "Approve all three as recommended" at the Component Selection checkpoint — see §10 Approval and `validation/change-log.md`). All 4 Open Questions in §9 were answered as-proposed; see §10a.

**Rev 3 status: APPROVED** (2026-08-31, human Chief Engineer, via the
creator/"General Chat" session — see §10a). This revision extends the base
document (Rev 1/2, above, unchanged) for the Motor Driver + Reaction Wheel
subsystem — the next two steps of the roadmap (`docs/architecture.md` §11),
taken together as one combined revision. New/changed content below is
marked "Rev 3"; nothing already approved above is altered.

Produced by `.github/skills/requirements-engineering/SKILL.md`. Every requirement
below has a stable ID referenced by `requirements/traceability-matrix.md`.
Do not delete an ID once assigned, even if the requirement is later dropped —
mark it `Withdrawn` instead, so history stays intact.

## 1. Project

- **Project name**: Bench-IMU-01 — MCU + IMU + USB Power Reference Board
- **Objective (one paragraph)**: A small, USB-powered reference/development board
  combining a general-purpose microcontroller (MCU) with a 6-axis inertial
  measurement unit (IMU), designed from scratch with no pre-existing
  component preference. It reads 3-axis acceleration and 3-axis angular rate
  from the IMU over a digital interface and makes samples available to a host
  PC over a wired serial link, powered entirely from a USB 5 V supply for
  desk/development use (not battery-powered). This is this repository's first
  real, end-to-end design cycle, and exists to benchmark the framework itself
  — both the original Electronics discipline and the newly added Mechanical
  discipline (`docs/architecture-evolution.md` §24, §27 item 5) — so the
  design should be realistic and buildable enough to support a genuine
  enclosure exercise, while keeping a plausible (not over-fit) path toward
  later attitude-control-roadmap work (`docs/architecture.md` §11) without
  adding scope for it now.
- **Benchmark / context**: "MCU + IMU + Power Supply" benchmark,
  `docs/architecture.md` §11; this is also the flagged follow-up run from
  Phase 1 (Mechanical), `docs/architecture-evolution.md` §24/§27 item 5.
- **Human-fixed constraints (not open for reinterpretation)**:
  1. Power source is a USB 5 V supply (desk/development use, not battery).
  2. Component selection starts from zero — no existing MCU/IMU/board
     preference.
- **Everything else below** (specific MCU/IMU/regulator, logic voltage,
  sample rate, interfaces, connector choices, enclosure form factor) is this
  cycle's own engineering-judgment call, made and documented by the
  appropriate specialist (Requirements Engineering here for anything
  interface/scope-level; Component Engineer for parts; Circuit Engineer for
  topology; Mechanical Lead for enclosure geometry) — not silently copied
  from the template's bracketed placeholders.

### 1a. Rev 3 scope note (new)

- **Rev 3 objective**: extend Bench-IMU-01 with a Motor Driver + Reaction
  Wheel subsystem — an open-loop-controllable motor spinning a flywheel mass,
  with its actual speed/torque bench-characterizable — per the roadmap's
  next two steps taken together (`docs/architecture.md` §11: MCU+IMU+Power →
  **Motor Driver** → **Reaction Wheel** → 1-axis → 3-axis attitude control).
  This is **not** an attitude controller: no PID, no sensor-fusion-driven or
  IMU-reactive motor control (see REQ-009). The Control Engineer's own
  future trigger ("1-axis/3-axis attitude control roadmap stage",
  `docs/architecture.md` §14) is explicitly **not** met by this revision,
  even though the hardware built here is what a future attitude-control
  stage would eventually use.
- **Human-fixed constraint #1 above ("USB 5V, not battery") governed the
  Rev 1/2 logic-only design.** Whether it extends to the new motor
  subsystem is treated as **open**, not assumed either way — see §9b. A
  dedicated power-architecture decision (`hardware/power-architecture.md`,
  owned by the Power Engineer once engaged — `docs/architecture-evolution.md`
  §33) is a separate Human-in-the-loop gate, informed by Component
  Selection's real current/voltage numbers for candidate motors/drivers,
  not decided here in Requirements Engineering.
- **Rev 2's REQ-302 (≤60×40mm PCB) and REQ-501 (~$15 BOM) ceilings are
  understood to no longer bind Rev 3 as hard constraints** — both are
  retained verbatim below as Rev 2's historical record, not deleted or
  edited, and are superseded for this revision by REQ-308/REQ-503
  respectively (see §9b for the proposed replacement figures).
- **This remains a paper/document design exercise** (REQ-504, mirrors
  REQ-502 exactly) — no physical fabrication, no physical spin test, no
  hardware-in-the-loop this cycle.

## 2. Functional Requirements

| ID | Requirement | Priority (Must/Should/Could) | Notes |
|---|---|---|---|
| REQ-001 | Read 3-axis acceleration and 3-axis angular rate (6-axis IMU) at ≥ 100 Hz output data rate | Must | Quantified from an ambiguous "IMU" goal; the ≥100 Hz figure is this cycle's own testable floor, not a re-typed template placeholder |
| REQ-002 | Provide a hardware debug/programming interface for the MCU (flash + basic debug) | Must | Firmware itself is out of scope this cycle, but the board must not be a dead end — Circuit Engineer picks the connector matching the selected MCU family's standard debug interface |
| REQ-003 | Provide a visual status/heartbeat LED | Should | Low-cost bench-use diagnostic aid |
| REQ-004 | Provide a manual reset button for the MCU | Could | Dev-use convenience, not required for core function |
| REQ-005 | Onboard data logging/storage (e.g. SD card, external flash) | Won't (this cycle) | Out of scope — keeps the benchmark to its named 3 parts (MCU + IMU + Power); revisit only if a future cycle needs it |
| REQ-006 | Any wireless (Wi-Fi/BLE/etc.) functionality actually implemented/enabled on this board | Won't (this cycle) | Applies even if a selected MCU candidate's silicon includes radio hardware — ecosystem quality is one Component Engineer scoring factor (§ component-selection SKILL), not a license to add radio circuitry now; adding wireless would be an architecture decision requiring its own HITL gate (`docs/architecture.md` §10) |
| REQ-007 *(Rev 3)* | The motor + reaction wheel subsystem shall be capable of spinning the flywheel across a commanded range of speeds via **open-loop** PWM duty-cycle / speed-setpoint control from the MCU | Must | Extends the roadmap (`docs/architecture.md` §11) to the Motor Driver + Reaction Wheel stage; "open-loop" is a deliberate scope fence — no IMU-reactive/closed-loop control this cycle, see REQ-009 |
| REQ-008 *(Rev 3)* | Firmware shall measure and report the flywheel's actual rotational speed (RPM) back to the host, using whatever RPM-sensing capability the selected motor+driver combination actually provides (e.g. integrated Hall-effect sensor, encoder, or driver tachometer/FG output) | Should | Contingent on Component Selection finding a reasonable RPM-sensing option — if none exists for the approved motor+driver, this requirement is downgraded to Won't with a documented reason, not silently dropped |
| REQ-009 *(Rev 3)* | No closed-loop attitude/orientation control, no PID, no sensor-fusion-driven or IMU-reactive motor control implemented this cycle | Won't (this cycle) | Explicit anti-scope statement, mirrors REQ-006's pattern; Control Engineer's future territory (`docs/architecture.md` §14), whose own trigger ("1-axis/3-axis attitude control roadmap stage") is deliberately not met by this revision even though the reaction wheel built here is what a future attitude-control stage would eventually use |
| REQ-010 *(Rev 3)* | The existing IMU readout capability (REQ-001) shall remain unaffected/unregressed by the new subsystem | Should | Regression-prevention check, not a new capability; Independent Review should confirm no interference (I2C bus timing, GPIO conflicts, supply-noise coupling from the new motor rail) |

## 3. Electrical Requirements

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| REQ-101 | Supply input: USB 5 V bus power, nominal 5.0 V, board must tolerate the standard USB VBUS range 4.75–5.25 V | Must | Human-fixed constraint (power source), tolerance band quantified from the USB spec rather than left as a bare "5V" |
| REQ-102 | System logic level: single 3.3 V rail for MCU + IMU + digital I/O | Should | Sharpened from the template default; keeps MCU/IMU candidate pairing simple (no level shifters) — Component/Circuit Engineer must flag if the winning parts genuinely prefer otherwise |
| REQ-103 | Total system current budget ≤ 300 mA @ 3.3 V under normal operation | Must | Feeds `hardware/power-budget.md`; regulator is selected with margin above this, not right at the edge |
| REQ-104 | IMU digital interface via I2C or SPI | Must | Final choice made by Circuit Engineer, driven by the winning IMU candidate's pin/timing constraints and MCU pin budget |
| REQ-105 | USB connector carries 5 V power delivery only in this cycle — no USB data/enumeration | Must | Documented scope decision (see §8 Assumptions): keeps MCU candidate selection interface-agnostic and avoids a firmware-layer USB-device-stack dependency that is out of scope for a hardware-only benchmark |
| REQ-106 | Provide a 4-pin UART header (TX, RX, GND, 3V3) for host communication via an external USB-serial adapter | Must | Standard "bare eval board" pattern; avoids adding a 4th BOM component category (an onboard USB-UART bridge IC) beyond the benchmark's named MCU/IMU/Power scope |
| REQ-107 | Provide a dedicated programming/debug header matching the selected MCU family's standard debug interface (e.g. 4-pin SWD for an Arm Cortex-M part) | Must | Satisfies REQ-002 at the connector level |
| REQ-108 *(Rev 3)* | A dedicated power architecture (rail count, voltage(s), physical source) shall be defined for the motor subsystem before Circuit Design begins on the power section, decided at a dedicated Power Architecture HITL gate once Component Selection provides real current/voltage numbers for candidate motors/drivers | Must | Architecture-defining, `docs/architecture.md` §10; owned by Power Engineer once engaged (`docs/architecture-evolution.md` §33) — see §9b for whether REQ-101's "USB only" human-fixed constraint is intended to extend here. **Confirmed at Circuit Design/Independent Review (ISS-014, 2026-09-05/06)**: the approved Option A motor rail is **3S-only in practice** (≈9.0–13.0V) — a 2S source does not reliably clear the driver's UVLO threshold once the added reverse-polarity protection diode's forward drop is accounted for, even though the motor itself remains independently 2S–3S rated in isolation. Any future physical build must supply a 3S-class source; 2S is not a supported configuration for this implementation. |
| REQ-109 *(Rev 3)* | Motor subsystem current/power draw shall be tracked in a rail separate from the existing 3.3 V logic budget (REQ-103, which continues to govern MCU+IMU+LED+pull-ups only, unchanged) | Must | Prevents conflating two budgets with very different scale/risk profiles; feeds `hardware/power-budget.md`'s multi-rail rollup |
| REQ-110 *(Rev 3)* | MCU shall generate a PWM (or equivalent commutation/drive signal) output to control the motor driver IC's speed/duty cycle | Must | Satisfies REQ-007 at the interface level; exact timer/pin TBD at Circuit Design |
| REQ-111 *(Rev 3)* | Motor driver IC shall include or enable overcurrent/stall protection appropriate for repeated bench testing by hand | Should | Safety-adjacent, ties to REQ-404; exact mechanism (IC-integrated vs. firmware-monitored) is a Component/Circuit Engineer decision |
| REQ-112 *(Rev 3)* | Where the selected motor+driver combination provides an RPM/tachometer feedback signal, it shall be wired to an MCU input for REQ-008 | Should | Contingent — see REQ-008's own contingency note |

## 4. Environmental Requirements

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| REQ-201 | Operating ambient temperature: 0 °C to +40 °C, indoor desk/lab use | Should | Sharpened from "UNKNOWN" using the human's own stated context ("desk/development use"); not Must since it's a working assumption, not a safety-critical bound |
| REQ-202 | Vibration/shock qualification | Won't (not applicable) | No rotating body/motor in this benchmark, so the `docs/architecture.md` §12 mechanical/thermal co-design trigger does not apply this cycle |
| REQ-203 | Standard indoor handling; ESD precautions during assembly/bring-up | Should | Ties to `validation/bring-up-procedure.md`'s existing ESD checklist item |
| REQ-204 *(Rev 3)* | Vibration exposure from the rotating flywheel/motor shall be assessed for its effect on the IMU (bias drift with temperature/vibration) and PCB-mounted connections/solder joints, per `docs/architecture.md` §12's mechanical/thermal co-design trigger | Must | Supersedes REQ-202's "Won't (not applicable)" disposition for this revision specifically — REQ-202 is retained verbatim above as Rev 2's historical record (no rotating body existed then), not deleted or edited; REQ-204 is the requirement that actually governs going forward |

## 5. Mechanical / Form Factor Constraints

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| REQ-301 | Single 2-layer PCB — no daughtercards/stacked boards | Should | Keeps the Mechanical Phase 1 benchmark tractable: one flat board is far more tractable for a first Mechanical-discipline enclosure exercise than a stacked/multi-board assembly |
| REQ-302 | Target PCB footprint ≤ 60 mm × 40 mm | Should | A concrete envelope for Circuit/Mechanical Lead to design against; refined once real component footprints are known |
| REQ-303 | External connectors/headers (USB, UART header, debug header) concentrated on ≤ 2 board edges | Should | Directly supports the benchmark's own success bar — simpler connector placement materially raises the odds of a believable, buildable enclosure (`docs/architecture-evolution.md` §24) |
| REQ-304 | ≥ 4 mounting holes sized for M2 or M2.5 fasteners | Must | Needed for enclosure standoffs; a concrete quantified default rather than "some mounting holes" |
| REQ-305 | Enclosure: 2-piece (lid + base), 3D-printable, no complex machining | Should | Matches the Mechanical Lead's documented Phase 1 scope (`.github/agents/mechanical-lead.agent.md`) |
| REQ-306 *(Rev 3)* | Enclosure shall provide a rotation clearance envelope for the flywheel across its full spin, under normal handling/vibration, with no contact against enclosure walls/lid at any point in the rotation | Must | Direct consequence of adding a spinning mass — a hard mechanical safety/function requirement, not a style preference |
| REQ-307 *(Rev 3)* | The motor + flywheel assembly's mount shall be evaluated for vibration isolation from the IMU's immediate PCB area where feasible, per `docs/architecture.md` §12 | Should | Mechanical/Thermal co-design guidance, now live rather than hypothetical (contrast REQ-202/REQ-204) |
| REQ-308 *(Rev 3)* | The original REQ-302 PCB footprint ceiling (≤60×40mm) is relaxed for Rev 3 — the new board/enclosure envelope is sized to whatever the approved motor/driver/connector selection actually needs, bounded by a soft desk-scale sanity ceiling (proposed: no single enclosure dimension much beyond ~150mm; fits comfortably on a desk; liftable one-handed) | Should | REQ-302 is retained verbatim above as Rev 2's historical record, not deleted; REQ-308 is the requirement that actually governs going forward — see §9b for confirmation of the proposed ~150mm sanity bound |
| REQ-309 *(Rev 3)* | Enclosure remains 3D-printable, no complex machining, in as many pieces as genuinely needed for motor+flywheel assembly/service access (2-piece is the Rev 2 baseline, not a hard ceiling for Rev 3) | Should | Extends REQ-305's intent to the new geometry; Mechanical Lead decides actual piece count during design |

## 6. Safety / Regulatory Constraints

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| REQ-401 | No specific regulatory certification target (e.g. FCC/CE/UKCA) for this prototype/benchmark iteration | Won't (this iteration) | Explicitly out of scope rather than silently ignored; see future Safety/Compliance Reviewer role, `docs/architecture.md` §14, if this ever targets a regulated market |
| REQ-402 | USB port includes basic transient/ESD and reverse-polarity protection appropriate for a hand-handled connector | Must | Standard good practice; ties into Circuit Engineer's "Protection" checklist item |
| REQ-403 *(Rev 3)* | The flywheel + its mount shall be designed such that, at bench-test speeds, no part of it can realistically detach and become a projectile hazard, nor present an uncontrolled pinch/contact hazard to a bench operator's fingers during normal handling | Must | Safety-critical — ties to the "safety-critical changes" HITL gate (`docs/architecture.md` §10); final disposition (e.g. any guard/shield decision) requires explicit human review before this cycle's Design Complete Gate |
| REQ-404 *(Rev 3)* | Motor driver/firmware shall implement stall/overcurrent detection and a shutdown behavior to prevent sustained overheating during bench testing | Should | Companion to REQ-111; exact split between IC-level and firmware-level detection is a Circuit/Firmware Engineer decision |
| REQ-405 *(Rev 3, new — added at Independent Review, ISS-020)* | Firmware shall enforce a maximum commanded flywheel speed and reject/clamp any command exceeding it, using the already-wired FG tachometer feedback to verify actual speed does not exceed a defined ceiling; on exceeding that ceiling, firmware shall command the motor to a safe/stopped state | Must | Discovered gap: REQ-007's "≥3000 RPM" was only ever a functional *floor*; nothing previously bounded the *maximum* — the recommended motor's own no-load speed (≈20,000 RPM up to a corrected credible worst-case of ≈25,180 RPM — DS-MTR-018 corrected/DS-MTR-080, `hardware/schematic/bench-imu-01-design.md` §7.5.13; supersedes the previously-cited, mislabeled "22,200 RPM at full-charge 3S (11.1V)" figure) is 6.7–8.4× that floor, and stored rotational energy scales with the square of speed. This is a bounded safety cutoff, not the closed-loop attitude control REQ-009 excludes (the same way an overcurrent shutdown is not itself "control"). Exact ceiling/ramp-rate/response TBD by Firmware Engineer + human safety review — ties to REQ-403's safety-critical HITL gate. Must also feed Mechanical Lead's flywheel/containment design as a real input |
| REQ-406 *(Rev 3, new — added at Independent Review, ISS-021)* | Firmware shall implement a latched-fault policy on repeated motor driver Lock Detection events (a persistent stall/jam): count qualifying retries within a rolling time window and force the motor to a safe/stopped state requiring deliberate re-arm, rather than allowing the driver IC's own indefinite auto-retry behavior to continue unsupervised | Should | Discovered gap: none of the DRV10983's three protection mechanisms (OCP, Lock Detection, Thermal Shutdown) latch — all auto-recover/auto-retry, so REQ-404's "shutdown behavior to prevent sustained overheating" is not actually satisfied by the driver IC alone. A persistent mechanical jam would otherwise produce repeated fault-current pulses/restart attempts indefinitely. Companion to REQ-404 |

## 7. Non-functional Requirements

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| REQ-501 | Component cost target: ≤ ~$15 USD total BOM cost at low-volume/prototype quantities | Should | Rough steer away from exotic/expensive parts, not a hard ceiling |
| REQ-502 | Schedule target | Won't / N/A | This is a paper/document design exercise this cycle, not a production schedule — no physical PCB fabrication or physical power-on happens in this session |
| REQ-503 *(Rev 3)* | Rev 3 total BOM cost target: proposed ≤ $75–90 USD (soft, not a hard ceiling) | Should | REQ-501 (~$15) is retained verbatim above as Rev 2's historical record; a motor+driver+flywheel subsystem realistically costs $20–50+ alone (2026 web-search-grounded ballpark, not yet datasheet-confirmed for specific candidates) — see §9b for confirmation |
| REQ-504 *(Rev 3)* | Schedule/physical-build framing unchanged from REQ-502 — this remains a paper/document design exercise this cycle: no physical PCB fabrication, no physical 3D print, no physical spin test, no physical power-on happens in this session | Won't / N/A | Mirrors REQ-502 exactly, restated for Rev 3 clarity since a spinning mass makes "no physical test" worth restating explicitly |

## 8. Assumptions

- No existing hardware/component preference exists; component selection
  starts from a clean slate (human-stated constraint).
- "Desk/development use" is read as: indoor ambient temperature, no
  vibration/shock, no waterproofing/ingress requirement.
- USB is used for power delivery only; host data/debug uses a separate UART
  header plus a separate MCU-family-appropriate debug header, rather than
  USB device firmware — keeps this a hardware-only, MCU-agnostic benchmark
  and avoids a 4th unplanned BOM category (an onboard USB-UART bridge IC).
- A single, flat, single-PCB assembly is assumed to keep the Mechanical
  Phase 1 benchmark tractable (no stacked boards/flex assemblies).
- No production/regulatory certification target for this iteration.
- A single 3.3 V logic rail is assumed for MCU+IMU compatibility; if the
  Component Engineer's winning MCU/IMU pairing genuinely prefers otherwise,
  that is a flagged deviation, not silently overridden.
- This is a paper/document design exercise: no physical PCB fabrication and
  no physical power-on happen in this session (human-stated). This applies
  to the mirrored "before mechanical fabrication" gate too — nothing is
  physically 3D-printed this session either.
  `validation/bring-up-procedure.md` is prepared with real project-specific
  values for the human's future physical build, not executed now.
- Development-ecosystem quality (SDK/samples/community) is one Component
  Engineer scoring factor among several, reflecting this project's possible
  future extension toward attitude-control work — it does not by itself
  justify choosing a part, and no attitude-control-specific feature is
  implemented now.
- **(Rev 3)** The motor is driven **open-loop** by firmware (commanded PWM
  duty cycle / speed setpoint), never by a control loop reacting to IMU
  data — REQ-009's scope fence is load-bearing for every downstream phase,
  not just a Requirements-Engineering note.
- **(Rev 3)** Whether the original "USB-powered only, not battery"
  human-fixed constraint (§1) extends to the new motor subsystem is treated
  as genuinely open (§9b) — not silently assumed to extend, and not
  silently assumed to be waived, either way.
- **(Rev 3)** The flywheel's exact mass/geometry is a Mechanical Lead design
  decision (informed by the approved motor's real torque capability and the
  human-confirmed angular-momentum target), not a Component Engineer
  candidate-comparison item — unless a specific off-the-shelf flywheel/disc
  product is sourced, in which case Component Engineer evaluates it as an
  additional candidate.
- **(Rev 3)** RPM-sensing capability (REQ-008/112) depends entirely on which
  motor+driver combination Component Selection actually finds — no specific
  sensing method is assumed in advance.

## 9. Open Questions for the Human

- Is the 0–40 °C indoor desk/lab ambient assumption (REQ-201) right, or is a
  different range wanted?
- Is the ≤ ~$15 USD BOM cost target (REQ-501) the right ballpark, or should
  it be higher/lower/uncapped for this benchmark?
- Is "USB for power only, with a separate UART header for data/debug"
  (REQ-105/106) the right reading of "USB 5 V supply for desk/development
  use" — or is actual USB-serial data transfer (requiring MCU-native USB or
  an onboard bridge IC) wanted even in this first cycle?
- Is the ≤ 60 mm × 40 mm / single-2-layer-PCB / ≤2-edges-for-connectors
  steer (REQ-301–303) a reasonable constraint to hand to Component/Circuit/
  Mechanical, or should form factor be left fully open for those specialists
  to decide organically once parts are chosen?

## 9a. Human Answers (recorded)

All four Open Questions above were answered by the human on the first pass
of this design cycle, before the accidental worktree deletion described in
`validation/change-log.md`: all four proposed defaults were **approved as
proposed, no changes** — REQ-201 (0–40 °C), REQ-501 (~$15 BOM target),
REQ-105/106 (USB power-only + separate UART header), REQ-301–303 (≤60×40 mm/
2-layer/≤2 edges). Recorded here so this file is self-contained after the
rewrite.

## 9b. Rev 3 — Open Questions for the Human (new, pending confirmation)

None of these had any prior number to anchor to (unlike §9's original four,
which each sharpened an existing ambiguous phrase) — Component Selection
cannot start on the motor/driver until at least the first is confirmed.
Proposed defaults below are this Hardware Lead's best-effort, reasoned
proposals, each web-search-grounded against real small/educational
reaction-wheel hardware (not fabricated), per
`.github/skills/requirements-engineering/SKILL.md` step 2 ("propose a
measurable version... confirm with the human — do not silently invent a
number and treat it as settled").

1. **Target reaction-wheel capability (drives REQ-007/Component Selection).**
   No prior number exists for this project. Real small/educational CubeSat-
   class reaction wheels (e.g. NanoAvionics RW0: 137 g, 20 mNms, 3.2 mNm,
   6500 RPM; AAC ClydeSpace RW222: 3–6 mNms, 2 mNm, 10000–15000 RPM; ARCSEC
   Zyra: 165 g, 27.5 mNms, 1.5 mNm) cluster around 100–200 g flywheels,
   3–30 mNms stored angular momentum, 1.5–5.9 mNm torque, 6500–15000 RPM
   (web-search-derived, not individually datasheet-verified — flagged as
   such, per the Source-of-Truth convention). **Proposed placeholder for
   this bench demonstration** (deliberately conservative vs. real flight
   hardware, since this is explicitly not flight hardware): flywheel ≈100 g
   at ≈30 mm radius, spin-up to ≥3000 RPM, storing ≈10–15 mN·m·s of angular
   momentum (I=0.5·m·r²≈4.5×10⁻⁵ kg·m² at that mass/radius; L=I·ω≈14 mN·m·s
   at 3000 RPM — arithmetic checked, not just asserted), motor delivering
   ≥5 mN·m continuous torque (reaches max speed in ≈10 s, with margin above
   the real NanoAvionics RW0's 3.2 mN·m since this is a bench part with
   friction/bearing losses not yet characterized). **Is this placeholder
   the right target, or is a different torque/RPM/momentum figure wanted?**
2. **Motor type preference (drives Component Selection's candidate set).**
   No preference stated. **Proposed**: no hard preference — Component
   Engineer compares brushed DC, brushless DC (BLDC), and stepper candidates
   on their actual merits (torque, controllability, driver complexity, cost,
   availability, RPM-sensing capability) rather than pre-selecting one. Note
   for context only, not as a constraint: real CubeSat reaction wheels
   (including the JAXA-style reference mentioned at kickoff) typically use
   BLDC motors for brushless reliability and smooth torque — that is
   someone else's design choice, not binding here unless the human wants it
   to be. **Confirm no preference, or state one (BLDC/brushed DC/stepper)?**
3. **Rev 3 BOM budget ceiling (REQ-503).** REQ-501's original ~$15 target
   was for the whole Rev 1/2 board; a motor+driver+flywheel subsystem alone
   will very likely exceed that. **Proposed**: ≤$75–90 USD total Rev 3 BOM
   (soft target, not a hard cap), given Rev 2's 3 priced primary ICs alone
   already total ~$7.51 and a reaction-wheel-capable motor+driver realistically
   runs $20–50+ at low-volume/prototype pricing (ballpark, not yet
   datasheet/distributor-confirmed for specific candidates). **Confirm this
   ceiling, propose a different one, or leave uncapped?**
4. **Physical mounting context (REQ-308).** No context stated — bare
   bench-test rig, or a size/form-factor constraint? **Proposed**: bare
   bench-test rig, no tight envelope — Rev 2's 60×40mm PCB ceiling no longer
   applies once a motor+flywheel is added (REQ-308), replaced by only a soft
   desk-scale sanity bound (no single enclosure dimension much beyond
   ~150mm; fits comfortably on a desk; liftable one-handed). **Confirm this,
   or is there an actual size constraint to design against?**

**Deliberately not asked here, and not defaulted either** — per the kickoff
task's own sequencing: the **power architecture** question (REQ-108: does
the motor rail stay within a "USB-powered only" constraint, get its own
DC-in/barrel-jack input, negotiate higher-power USB-PD, or use a battery) is
answered later, as its own dedicated HITL gate, once Component Selection
provides real current/voltage numbers for the approved motor+driver — not
guessed now with no data behind it. See `hardware/power-architecture.md`.

## 9c. Rev 3 — Provisional Adoption (autonomous, recorded honestly)

The human was asked all four §9b questions individually via `ask_user` this
session; each call returned an automatic "not available, work autonomously
and make good decisions" response rather than a substantive answer (the
human's own direction for this cycle came instead through the cross-session
"General Chat" channel, which explicitly invoked autonomous judgment for
exactly this kind of gap). Per that authorization — and per this framework's
own bias against silently blocking indefinitely on a synchronous response —
**all four proposed defaults in §9b are provisionally adopted as this
cycle's working requirements** (REQ-007's target figures, no motor-type
preference, REQ-503's ≤$75–90 ceiling, REQ-308's bare-bench-rig/~150mm
sanity bound), so Component Selection is not blocked. This is recorded here
**as provisional, not as a human sign-off** — the distinction matters: §10's
own Approval table below is Rev 1/2's real human sign-off; a matching Rev 3
sign-off has *not* yet happened and is explicitly still solicited. A
`send_session_message` summary of this exact provisional-adoption decision,
with an explicit invitation to override any of the four figures, was sent to
the creator/"General Chat" session (the channel that has actually reached
the human this cycle) immediately after this record was written. If the
human overrides any of these four values before Component Selection
concludes, this section and the affected REQ rows above get updated in
place, not silently left stale.

## 10. Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Chief Engineer (Human) | Human Chief Engineer (via creator/"General Chat" session) | 2026-08-30 | **Approved** — requirements confirmed final; proceed to Component Selection |

## 10a. Rev 3 Approval (real human sign-off received — supersedes the "provisional" framing above)

| Role | Name | Date | Decision |
|---|---|---|---|
| Hardware Lead | Hardware Lead (this session) | 2026-08-31 | Provisionally adopted all four §9b defaults after `ask_user` went unreachable this cycle (see §9c) — superseded by the real human confirmation below, received via the creator/"General Chat" session (the channel that has actually reached the human this cycle) |
| Chief Engineer (Human) | Human Chief Engineer (via creator/"General Chat" session, who relayed to and confirmed with the human directly) | 2026-08-31 | **Approved — "all four provisional defaults are approved as proposed, no changes."** This is the human's real Rev 3 Requirements sign-off, not a provisional placeholder — REQ-007's target figures, no motor-type preference, REQ-503's ≤$75–90 ceiling, and REQ-308's bare-bench-rig/~150mm sanity bound are now confirmed requirements, not open questions. Component Selection (motor + driver) proceeded against these targets and is recorded in `bom/component-selection.md`. Process note recorded for the rest of this design cycle: since `ask_user` is not reliably reaching the human this cycle, every remaining HITL gate is routed through the cross-session message channel instead (report the gate content there, wait for a reply there) rather than falling back to provisional-autonomous adoption. |
