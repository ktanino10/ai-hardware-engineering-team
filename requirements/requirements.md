# Requirements

Status: **APPROVED** (2026-08-30, human Chief Engineer, via ask_user "Approve all three as recommended" at the Component Selection checkpoint — see §10 Approval and `validation/change-log.md`). All 4 Open Questions in §9 were answered as-proposed; see §10a.

**Rev 3 status: APPROVED** (2026-08-31, human Chief Engineer, via the
creator/"General Chat" session — see §10a). This revision extends the base
document (Rev 1/2, above, unchanged) for the Motor Driver + Reaction Wheel
subsystem — the next two steps of the roadmap (`docs/architecture.md` §11),
taken together as one combined revision. New/changed content below is
marked "Rev 3"; nothing already approved above is altered.

**Rev 5 scope-decision status: APPROVED** (2026-09-04, human Chief Engineer,
via the creator/"General Chat" session — see §1c and §10c). The human has
approved committing now to the full 3-axis reaction-wheel attitude-control
"Cube" — the long-term roadmap's final destination
(`docs/architecture.md` §11) — rather than continuing to validate 1-axis
first, including the real cost/complexity trade-off this implies (an
estimated ≈$450–800+ total BOM, a 5–9× jump over Rev 3/4's ≈$75–90
ceiling), presented to and approved by the human before this session began.
This is **Rev 5 of the same Bench-IMU-01 project** (not a new repository),
extending the already-Design-Complete Rev 1–4.1 work. **This status line
covers only the scope/budget decision itself** — the detailed Rev 5
requirements below (REQ-015–021, REQ-114–115, REQ-206, REQ-312, REQ-409,
REQ-507–509) and §9h's Open Questions are this session's own proposed
draft, not yet themselves signed off; see §10c for the honest, staged
distinction (mirrors Rev 4's own §9f/§9g/§10b practice of never
overclaiming a full sign-off before it has actually happened).

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

### 1b. Rev 4 scope note (new)

- **Rev 4 objective**: add a **free-rotation support mechanism** — the
  physical means by which the already-Design-Complete Rev 3 assembly
  (board + motor + flywheel + enclosure) can rotate about at least one axis
  with low enough friction that the reaction wheel's own already-approved
  torque output (REQ-007, `bom/component-selection.md` Motor section) can
  produce a measurable angular response. This is the next roadmap step
  (`docs/architecture.md` §11: MCU+IMU+Power → Motor Driver → Reaction
  Wheel → **1-axis attitude control** → 3-axis attitude control) — but only
  its physical precondition. **Confirmed via repo-wide search this
  session**: zero mentions of "pivot"/"gimbal"/"bearing-as-pivot"/
  "free-rotat[ing]" exist anywhere in `hardware/mechanical/**` before this
  revision — Rev 3's enclosure mounts the whole assembly rigidly to the
  bench, so no reaction-wheel torque could ever have produced an observable
  attitude change under that design.
- **This is not a control-loop/attitude-control revision.** No PID, no
  attitude estimation/sensor fusion, no closed-loop pointing, no second/
  third reaction wheel, and no Control Engineer introduction happen this
  cycle — see REQ-014's explicit anti-scope statement, which mirrors
  REQ-009's own pattern from Rev 3. The Control Engineer's own future
  trigger ("1-axis/3-axis attitude control roadmap stage",
  `docs/architecture.md` §14) is **still not met** by this revision either —
  this revision only builds the physical precondition that trigger will
  eventually depend on.
- **Scope of this revision is itself narrow**: Requirements Engineering +
  Component Selection only. No Mechanical Design/CAD (`.scad`) work happens
  this cycle — the specific mechanism to build is flagged as an
  architecture-level Human-in-the-loop decision (`docs/architecture.md`
  §10, mirrors `hardware/power-architecture.md`'s own "recommendation, not
  a decision" precedent) in `bom/component-selection.md`'s new section, not
  resolved here.
- **REQ-403/MISS-016 (Rev 3's flywheel-containment ACCEPTED-RISK
  disposition, `validation/open-issues.md`) is explicitly NOT reopened by
  this revision.** REQ-408 below states plainly that its disposition does
  not automatically extend to the new free-rotating configuration a support
  mechanism introduces — that is a fresh review for whenever a mechanism is
  actually chosen and integrated, not a retroactive edit to Rev 3's already
  human-signed-off gate.
- **Mass/footprint this revision designs against** (real, sourced, not
  guessed): the existing Rev 3 board+motor+flywheel subtotal is ≈149–150g
  (`hardware/mechanical-interface.md` §B7, ESTIMATE). The enclosure's own
  plastic mass was **never estimated** in Rev 3 (that file explicitly
  excludes it, "additional") — this revision computes a first fresh
  ESTIMATE for it, since no downstream Component Selection can reason about
  mechanism load capacity without at least an order-of-magnitude total
  figure. See REQ-310's Notes for the worked calculation.

### 1c. Rev 5 scope note (new)

- **Rev 5 objective**: commit now to the roadmap's full destination
  (`docs/architecture.md` §11: MCU+IMU+Power → Motor Driver → Reaction
  Wheel → 1-axis attitude control → **3-axis attitude control → a standing
  "Cube"**) — a full 3-axis reaction-wheel attitude-control module, rather
  than continuing to validate 1-axis first. This is a **major scope
  expansion**, human-approved with full awareness of the cost/complexity
  trade-off (see header status line above) — that decision itself is not
  re-litigated here; this note records it and surfaces the genuinely open
  engineering sub-questions it leaves (§9h).
- **Inspiration, explicitly not a parts list to copy.** This revision's
  conceptual shape is inspired by `ktanino10/attitude-control-study`
  (CC BY 4.0), the human's own study notes summarizing Shinji Mitani
  (JAXA)'s 3-part Transistor Gijutsu (CQ Publishing) series, June–August
  2020, "Equations of Motion and Microcontroller Control of an XYZ 3-Axis
  Attitude Control Module" — which itself documents a real build: 6×
  MPU-6050 IMUs (2 per I²C bus × 3 buses, driven by MPU-6050's own
  2-address-per-bus ceiling), 3× orthogonal reaction wheels on 3× maxon
  EC45 flat BLDC motors, 3× electromagnetic brakes for rapid
  momentum-dump/"jump onto a vertex" maneuvers (the Cubli mechanism —
  Gajamohan et al., IROS 2012 / ECC 2013, ETH Zürich — which that article
  itself cites as its own primary reference), 1× PSoC 5LP MCU (Cortex-M3 +
  UDB + FreeRTOS), a wireless remote-control link, and 2× 7.4V LiPo
  batteries in a ≈10cm cube. **None of these specific part choices are
  adopted here.** Every part — including the 4 already approved in Rev
  1–4 — is subject to independent, from-scratch Component Selection
  (next PR) against real 2026 candidates/datasheets/stock for this
  project's own requirements and budget, per this framework's own
  Source-of-Truth culture (`docs/architecture.md` §6.1) and this file's own
  §1 "Human-fixed constraints" precedent ("component selection starts from
  zero — no existing... preference"). Where the JAXA article's own
  *reasoning* (not its parts) genuinely informs a requirement below, it is
  cited by name, never presented as if independently re-derived when it
  wasn't.
- **What Component Selection (next PR) must re-evaluate from scratch, not
  silently carry forward**:
  1. **MCU** — the current STM32G031K8T6 (Rev 1–4, chosen for a
     single-IMU/single-motor/USB-only scope) almost certainly cannot scale
     to 6 IMUs + 3 motor drivers + 3 brake outputs + wireless + a
     real-time multi-axis control loop (2×I2C/2×SPI total, 8KB SRAM, a
     single 64MHz Cortex-M0+ — see `bom/component-selection.md`'s own MCU
     table). Flagged explicitly for a fresh, honest Component Selection
     pass against modern candidates (STM32 F4/H7-class, RP2040, ESP32-S3,
     etc.) on real peripheral count/RTOS support/compute headroom/
     toolchain maturity/cost — not assumed inadequate without a real
     comparison, and not assumed PSoC 5LP is the answer just because JAXA
     used it (REQ-508).
  2. **IMU** — evaluate whether BMI270 (already Rev 1–4 validated and
     already integrated into `firmware/bench-imu-01/`) should simply be
     used ×6, rather than switching to MPU-6050 without a real reason.
     BMI270's own I²C multi-address/bus-sharing behavior is **not
     verified this session** (REQ-016's own Notes) — a real datasheet
     check, not an assumption that it shares MPU-6050's exact 2-address
     constraint, is Component Selection's job next.
  3. **Motor + Driver** — evaluate whether the already-validated,
     already-Design-Complete T-Motor MN2206-13 KV2000 + TI DRV10983
     pairing (≈$18.99+$2.58 = ≈$21.57/axis, `bom/component-selection.md`
     Motor/Motor Driver IC sections) should be used ×3, rather than maxon
     EC45 flat (≈$80–125/axis — per the cost/complexity comparison already
     presented for this scope decision, not independently re-verified
     against a maxon datasheet this session) — a premium that needs its
     own justification (torque margin, brake-stop load tolerance,
     Hall-sensor quality) or should be rejected in favor of scaling the
     cheaper, already-proven part (REQ-508).
  4. **Electromagnetic brake** (REQ-019) — an entirely new subsystem, no
     Rev 1–4 part or circuit provides this. Needs its own from-scratch
     Component Selection and Circuit Design (brake driver, flyback-diode
     protection for the inductive coil, low-side MOSFET switch — see
     `ktanino10/attitude-control-study`'s own inductive-load-switching
     reasoning for the physics, not specific parts).
  5. **Wireless module** (REQ-020) — new Component Selection: a simple
     UART-bridge BLE/2.4GHz module vs. a WiFi/BLE peripheral built into
     whichever new MCU candidate wins item 1 above — evaluate both.
- **Power architecture is reopened, not just extended (new finding this
  session).** Rev 3's human-approved Option A
  (`hardware/power-architecture.md`) is a **tethered** architecture: the
  existing USB 5V logic rail unchanged, plus a *physically separate,
  barrel-jack-tethered* ~12V-class motor input — battery (Option C) was
  explicitly considered and rejected at that gate. A 3-motor+3-brake "Cube"
  that is meant to (eventually) stand itself up on a vertex is likely
  physically incompatible with a barrel-jack tether during that maneuver.
  This is flagged for a fresh Power Engineer pass (REQ-115) — not decided
  here, and not assumed either way (§9h Q4).
- **Control Engineer's documented trigger is met, but the discipline is
  stood up in the next PR, not this one.** `docs/architecture.md` §14
  already names **Control Engineer** (control-loop design, e.g. attitude
  control loops) with trigger "at 1-axis/3-axis attitude control roadmap
  stage" — **met by this revision** (REQ-017). Firmware Engineer's own
  scope explicitly excludes control loops/sensor fusion/unit conversion
  (`.github/agents/firmware-engineer.agent.md` "Out of scope") precisely
  so this boundary would stay clean once the trigger was actually met —
  this is that moment. Per this project's own established practice
  (`docs/architecture.md` §3's own account of how Power Engineer/
  Manufacturing Engineer/Firmware Reviewer/PCB Engineer were each
  introduced), the new `.github/agents/control-engineer.agent.md` +
  skill + README/architecture-evolution.md updates land **with** the
  agent's actual introduction — its own next PR, per the expected
  multi-PR sequence below — not pre-emptively during Requirements.
- **Expected shape of this effort**: multiple sequential PRs, each its own
  independently-reviewable unit, mirroring how Rev 3 needed several PRs and
  Rev 4 needed its own sequence — **Requirements (this PR) → Control
  Engineer discipline introduction → Component Selection (MCU/IMU/Motor/
  Driver/Brake/Wireless) → Circuit Design → Mechanical redesign (3-wheel
  cube frame) → PCB layout → Firmware**. This PR does not start
  Component Selection or any later phase — see the REQ Notes below for
  what's explicitly flagged for that later work instead of decided now.
- **Safety stakes are explicitly escalated, not silently assumed
  unchanged.** REQ-403's containment requirement and its `ACCEPTED-RISK`
  disposition (MISS-016, `validation/open-issues.md`) were written for
  **one** flywheel. Three simultaneous flywheels plus hard electromagnetic
  braking for momentum-dump/future aggressive maneuvers is a materially
  different, higher-energy hazard shape — a **new** requirement (REQ-409)
  is added for this, explicitly not reopening or editing REQ-403/MISS-016
  themselves, and flagged for the Mechanical Reviewer's existing Foresight
  checklist (`docs/architecture.md` §3, `docs/architecture-evolution.md`
  §38) with extra rigor once a real mechanical design exists to review.

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
| REQ-011 *(Rev 4)* | The Rev 3 assembly (board + motor + flywheel + enclosure) shall be mounted on a free-rotation support mechanism enabling rotation about at least one (vertical/yaw) axis, with mechanism friction low enough that the reaction wheel's already-approved torque output (REQ-007) can produce a measurable angular response | Must | This is the physical precondition for the roadmap's next stage (`docs/architecture.md` §11/§14) — see §1b. Component Selection compares candidate mechanisms in `bom/component-selection.md`'s new Free-Rotation Support Mechanism section; the specific choice is a human architecture decision, not resolved here |
| REQ-012 *(Rev 4)* | Angular-travel target for the support mechanism: propose **at least ±180°, ideally continuous/unlimited rotation** | Should | No prior anchor exists for this figure (same situation as Rev 3's own §9b) — proposed default, not silently assumed; see §9d. Driven by a fresh back-of-envelope finding this revision (worked in full in `bom/component-selection.md`'s new section): using I_platform≈6.9×10⁻⁴ kg·m² (ESTIMATE, rectangular-plate approximation against the real ≈111×171mm assembled footprint, excludes the flywheel's own I) against the flywheel's established I=4.5×10⁻⁵ kg·m², the inertia ratio is ≈1:15 (independently cross-checked by the Hardware Lead's own creator session across a 250–450g/0.06–0.08m assumption sweep at ≈1:20–1:64, same order of magnitude) — meaning a full spin-up to REQ-007's 3000 RPM ceiling could drive the free platform to an extreme angular rate (several hundred to ≈1170°/s, ESTIMATE) if commanded all at once, while a gentle ~30 RPM command yields a comfortably observable ≈12°/s. This motivates REQ-013's speed-increment guidance and REQ-407's new hazard flag, not just the angular-travel number itself |
| REQ-013 *(Rev 4)* | The onboard IMU gyroscope (already satisfying REQ-001, BMI270 approved) shall be the primary means of measuring the free-rotating assembly's angular-rate response; no new external angular-rate reference is added this cycle unless bring-up shows the onboard gyro is inadequate. Firmware/bring-up procedure shall command the reaction wheel through small, deliberately increasing speed steps (well below REQ-007's 3000 RPM ceiling) the first time the platform is free to rotate, rather than commanding the full ceiling immediately | Should | BMI270's gyro FSR is programmable ±125 to ±2000 dps across 5 ranges [DS-IMU-002] — comfortably covers the full range of illustrative platform rates worked out under REQ-012 (≈12°/s to ≈1170°/s), so the sensor itself is not a gap; FSR range selection (start wide, e.g. ±2000dps, then narrow once the response is characterized) is the actual practical consideration, not sensor adequacy. The "small speed steps" behavior is a safety-motivated firmware/procedure requirement, not a new sensing capability — ties to REQ-407 |
| REQ-014 *(Rev 4)* | No closed-loop attitude/orientation control, no PID, no attitude estimation/sensor-fusion, no second/third reaction wheel, and no Control Engineer introduction implemented or triggered this cycle — this revision is the free-rotation **support mechanism** (Requirements + Component Selection) only | Won't (this cycle) | Explicit anti-scope statement, mirrors REQ-009's exact pattern from Rev 3. Control Engineer's own future trigger ("1-axis/3-axis attitude control roadmap stage", `docs/architecture.md` §14) remains **not met** by this revision — this revision only builds the physical precondition that trigger will eventually depend on |
| REQ-015 *(Rev 5)* | The system shall provide open-loop-capable PWM/speed-setpoint control of 3 independently-driven reaction wheels, one per orthogonal axis (X/Y/Z), extending REQ-007's single-axis capability to all 3 axes | Must | Final electromechanical scale-out step of the roadmap (`docs/architecture.md` §11). **§9h Q1's conditional confirmation has now LAPSED — §9h Q2 answered YES (§9j), the condition it was conditional on.** The steady-state torque-reuse default no longer applies. The real per-axis torque/momentum target now requires a **fresh impulsive-torque derivation** (ΔL/Δt over the electromagnetic brake's actual engagement time) once Component Selection (next PR) has real brake response-time data — not a figure this Requirements phase can derive without that data. Do not silently continue citing the old ≥5mN·m/≥3000RPM steady-state figure as though it still governs |
| REQ-016 *(Rev 5)* | The system shall estimate 3-axis attitude (orientation) via sensor fusion (e.g. complementary or Kalman filter) across 6 IMUs, 2 per axis, using as many I²C buses as the finally-selected IMU part's own address/pin constraints require | Must | JAXA/`attitude-control-study`'s own build uses 3 buses × 2 IMUs specifically because MPU-6050 has only a 2-address (AD0-pin) ceiling per bus — cited as conceptual inspiration only; whether the already-approved BMI270 shares that same constraint (or a different one) is **not verified this session** and must be independently confirmed at Component Selection/Datasheet Verification (next PR), not assumed. New capability this revision explicitly authorizes — see REQ-017 |
| REQ-017 *(Rev 5)* | The system shall implement closed-loop attitude control (e.g. per-axis PID or equivalent) commanding the 3 reaction wheels from the REQ-016 attitude estimate | Must | **Explicitly supersedes REQ-009 (Rev 3) and REQ-014 (Rev 4)'s "no closed-loop/PID/sensor-fusion control this cycle" anti-scope fences** — both retained verbatim above as historical record of Rev 3/4's own deliberate scope limits, not deleted or edited, mirroring exactly how REQ-501→REQ-503 and REQ-302→REQ-308 were superseded without erasure. This is the literal trigger condition `docs/architecture.md` §14 names for introducing Control Engineer ("at 1-axis/3-axis attitude control roadmap stage") — met by this revision; the discipline itself is stood up in the next PR (§1c) |
| REQ-018 *(Rev 5)* | The system shall monitor each reaction wheel's stored angular momentum/speed and detect approach toward saturation (e.g. Hall-sensor pulse counting or the existing tach/FG feedback pattern established by REQ-008/112) | Should | Prerequisite for any desaturation/momentum-dump behavior (REQ-019); extends REQ-008's single-axis RPM-reporting pattern to a 3-axis momentum-budget concept — a wheel at its speed ceiling can no longer produce useful torque in that direction |
| REQ-019 *(Rev 5)* | The system shall provide an electromagnetic brake per axis, capable of a controlled rapid momentum-dump (desaturation) maneuver | Must | Entirely new subsystem — no existing Rev 1–4 part or circuit provides this (§1c item 4). Torque/response-time requirements are to be derived from the flywheel inertia already established in `bom/component-selection.md`'s Free-Rotation Support Mechanism section (I_wheel≈4.5×10⁻⁵ kg·m², already computed — reuse it, don't re-derive) during Component Selection (next PR), not guessed here. See REQ-409 for the safety implications of 3 simultaneous braked flywheels |
| REQ-020 *(Rev 5)* | The system shall provide a wireless remote-control link (UART-bridge module or MCU-native radio) for commanding maneuvers and monitoring status without a physical tether | **Must, upgraded from Should** | **Upgraded per §9h Q2 answered YES (§9j)**: the assembly now must physically move untethered during the jump/stand maneuver, so *some* non-tether command/telemetry link is necessary for at least that operating mode — a bare wired USB/UART tether cannot survive the jump. Whether this needs to be a persistent, full-featured wireless link or a narrower solution adequate only for the jump/stand window is Component Selection's call (next PR); the requirement itself is now Must for that mode, no longer a pure nice-to-have. Still deliberately reverses REQ-006's "no wireless functionality actually implemented even if silicon has it" scope fence for this revision, as before |
| REQ-021 *(Rev 5, revised — §9h Q2 ANSWERED)* | The system shall be capable of the Cubli-style maneuver: spin up 1+ reaction wheels, then hard-brake to transfer momentum, causing the assembly to jump onto an edge/vertex and balance there | **Must** | **§9h Q2 ANSWERED — YES. This maneuver IS an in-scope Rev 5 deliverable, not deferred.** Independently verified (not accepted on a relayed message alone) directly against the creator/"General Chat" session's own turn history via `session_store_sql` — session `7fab99ef-5578-4d79-a9c2-b24dbcfe93be`, turn 415, timestamp `2026-09-03T23:49:20.372Z`. Kyosuke's own words (verbatim, in the same message that also addressed MISS-034): "...本体を立たせるところもやりたいです" ("...I also want to do the part where the body stands up"). **Supersedes this row's own prior "proposed Won't (this cycle), NOT YET FINALIZED" disposition** — see new §9j for the full record, the exact verbatim quote, and the cascading updates this triggers (REQ-015, REQ-115, REQ-020, REQ-409, REQ-507) |

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
| REQ-113 *(Rev 4)* | Any electrical connections crossing the rotating interface (motor power, motor phase wires, USB/UART tether per REQ-101/105/106) shall use a method compatible with the chosen free-rotation mechanism — a flexible service-loop tether (sized for several full turns before requiring manual re-centering) is the proposed default for bounded/near-continuous use; a slip-ring/rotary electrical interface is deferred unless bring-up shows genuinely continuous, unlimited multi-turn rotation is required | Must | Mirrors REQ-008/112's own "contingent on what's actually needed" pattern rather than over-specifying a slip ring up front. This is also a **new hazard shape** (cable entanglement/strain at a now-rotating joint) — see REQ-407 |
| REQ-114 *(Rev 5)* | A multi-rail power budget shall be defined and tracked for 3 simultaneous motor+driver channels and 3 simultaneous electromagnetic-brake channels, separate from the existing 3.3V logic budget (REQ-103) and the existing single-motor rail bookkeeping (REQ-109) | Must | Directly triggers Power Engineer re-engagement (`docs/architecture-evolution.md` §33) for a fresh multi-rail `hardware/power-budget.md` pass once Component Selection provides real per-channel current/voltage numbers (next PR) — not sized here |
| REQ-115 *(Rev 5)* | The physical power source architecture (Rev 3's approved tethered Option A: USB 5V logic + barrel-jack ~12V motor rail, `hardware/power-architecture.md`) shall be **re-evaluated**, not assumed to extend unchanged, given the new 3-motor+3-brake simultaneous load and the roadmap's now-in-scope untethered "stand on a vertex" maneuver | Must | **Update — §9h Q2 is now ANSWERED YES (§9j): the jump/stand maneuver IS in scope, not merely an eventual possibility.** A barrel-jack tether is physically incompatible with an untethered jump/stand event, so battery power (Rev 3's own explicitly-rejected Option C) is now **very likely a hard requirement**, not merely a live option to keep open — the earlier "tethered-only is acceptable for now" off-ramp (§9h Q4) no longer applies. Power Engineer still owns the actual battery chemistry/capacity/rail selection (a recommendation, not a decision, mirroring `hardware/power-architecture.md`'s own established pattern) — not decided here, still routed to a fresh Power Engineer HITL gate, but that gate's own option set has narrowed |

## 4. Environmental Requirements

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| REQ-201 | Operating ambient temperature: 0 °C to +40 °C, indoor desk/lab use | Should | Sharpened from "UNKNOWN" using the human's own stated context ("desk/development use"); not Must since it's a working assumption, not a safety-critical bound |
| REQ-202 | Vibration/shock qualification | Won't (not applicable) | No rotating body/motor in this benchmark, so the `docs/architecture.md` §12 mechanical/thermal co-design trigger does not apply this cycle |
| REQ-203 | Standard indoor handling; ESD precautions during assembly/bring-up | Should | Ties to `validation/bring-up-procedure.md`'s existing ESD checklist item |
| REQ-204 *(Rev 3)* | Vibration exposure from the rotating flywheel/motor shall be assessed for its effect on the IMU (bias drift with temperature/vibration) and PCB-mounted connections/solder joints, per `docs/architecture.md` §12's mechanical/thermal co-design trigger | Must | Supersedes REQ-202's "Won't (not applicable)" disposition for this revision specifically — REQ-202 is retained verbatim above as Rev 2's historical record (no rotating body existed then), not deleted or edited; REQ-204 is the requirement that actually governs going forward |
| REQ-205 *(Rev 4)* | Reconfirm REQ-201's indoor desk/lab, 0–40°C ambient context for the free-rotating rig specifically; operation shall remain human-attended (no unattended free-spin operation) given the new tip-over/entanglement/fast-spin hazard shapes this revision introduces (REQ-407) | Should | Restates/extends REQ-201 rather than replacing it (mirrors how REQ-204 extended REQ-202) — no reason found to change the underlying bench/lab context itself, but "human-attended" is now a safety-relevant qualifier it wasn't before, since a free-rotating rig with an energized flywheel is a materially different hazard shape than Rev 3's fixed-mount rig |
| REQ-206 *(Rev 5)* | Reconfirm REQ-205's human-attended, no-unattended-operation constraint, escalated: 3 simultaneous flywheels plus hard electromagnetic braking is a materially higher-energy hazard profile than Rev 4's single-flywheel free-rotation rig | Must | Extends REQ-205 rather than replacing it (mirrors how REQ-204/REQ-205 each extended their predecessor without deleting it). Upgraded from REQ-205's "Should" to "Must" given the escalated energy/hazard shape this revision introduces — ties to REQ-409's new safety requirement |

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
| REQ-310 *(Rev 4)* | The free-rotation support mechanism shall accommodate the real, sourced total rotating-assembly mass with margin | Must | **Real figures, not guessed**: Rev 3 board+motor+flywheel subtotal ≈149–150g (`hardware/mechanical-interface.md` §B7, ESTIMATE). Enclosure plastic mass was never estimated in Rev 3 (excluded there as "additional") — this revision's own fresh ESTIMATE: bounding-shell surface area of the real assembled envelope (111.4×170.6×49.0mm, `bench-imu-01-dimensional-spec.md`) × the enclosure's own established `min_wall_t`=2.0mm [ASSUMPTION, `bench-imu-01-enclosure.scad` line 209] × Prusament PETG's published 1.27 g/cm³ density [DS-MTL-004] ≈ 656.5cm² × 0.20cm × 1.27g/cm³ ≈ 167g gross bounding-box figure — real cutouts (connector/LED/header-bay openings) reduce this somewhat, real internal ribs/bosses/tabs add back, judged to roughly offset, so this revision proposes **≈130–170g** for the enclosure alone. **Total rotating-assembly ESTIMATE: ≈280–320g**, call it ~300g representative, up to a conservative ~350g bound. Both Component-Selection bearing candidates' load ratings (300 lb / ≈1370–3300N) exceed even the 350g bound by >400×, so load capacity is not a differentiator between mechanism candidates — friction torque is (see `bom/component-selection.md`) |
| REQ-311 *(Rev 4)* | The chosen mechanism shall integrate by **adding to**, not editing, the already-Design-Complete Rev 3 enclosure geometry (`bench-imu-01-enclosure.scad`/`bench-imu-01-dimensional-spec.md`) — e.g. a new mounting boss/plate on the existing base's underside, not a redesign of Rev 3's own bays/walls | Should | A future Mechanical Design revision (Rev 4 of the enclosure) is anticipated once a mechanism is human-approved — explicitly **not done this cycle** (see §1b). Flagged now so the next phase doesn't have to re-derive this constraint from scratch |
| REQ-312 *(Rev 5)* | The enclosure shall be redesigned as a 3-orthogonal-reaction-wheel "cube" frame providing a rotation clearance envelope for all 3 flywheels simultaneously, under normal handling/vibration, with no contact against frame walls at any point in any wheel's rotation | Must | High-level constraint only — mirrors REQ-306's exact pattern for the single-wheel case. Real geometry (frame dimensions, per-wheel bay layout, mounting) is explicitly deferred to a future Mechanical Lead pass (a later PR, per §1c's expected sequence), not designed here. **Open dependency, independently verified this session (not merely relayed): `validation/open-issues.md` MISS-034 (CRITICAL, OPEN, merged to `main` via PR #38) already establishes that `hardware/mechanical-interface.md`'s current 100×50mm PCB basis is stale — the real board (`hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb` `Edge.Cuts`) is 150×95mm with a 134×79mm M2.5 mounting-hole pattern.** Any future Mechanical Design pass for this REQ must start from the real board geometry, not the superseded figure — see §9h for the full note. **Update (§9j)**: Kyosuke has since given a decision *criterion* for MISS-034 (choose whichever of grow-enclosure/shrink-PCB has fewer technical obstacles) — not yet reflected as a landed fix in `validation/open-issues.md` as of this writing. A dedicated fix session is reported in progress, independent of this branch. This row is **not** updated to claim MISS-034 is resolved; that remains `validation/open-issues.md`'s own record, owned elsewhere, not edited here |

## 6. Safety / Regulatory Constraints

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| REQ-401 | No specific regulatory certification target (e.g. FCC/CE/UKCA) for this prototype/benchmark iteration | Won't (this iteration) | Explicitly out of scope rather than silently ignored; see future Safety/Compliance Reviewer role, `docs/architecture.md` §14, if this ever targets a regulated market |
| REQ-402 | USB port includes basic transient/ESD and reverse-polarity protection appropriate for a hand-handled connector | Must | Standard good practice; ties into Circuit Engineer's "Protection" checklist item |
| REQ-403 *(Rev 3)* | The flywheel + its mount shall be designed such that, at bench-test speeds, no part of it can realistically detach and become a projectile hazard, nor present an uncontrolled pinch/contact hazard to a bench operator's fingers during normal handling | Must | Safety-critical — ties to the "safety-critical changes" HITL gate (`docs/architecture.md` §10); final disposition (e.g. any guard/shield decision) requires explicit human review before this cycle's Design Complete Gate |
| REQ-404 *(Rev 3)* | Motor driver/firmware shall implement stall/overcurrent detection and a shutdown behavior to prevent sustained overheating during bench testing | Should | Companion to REQ-111; exact split between IC-level and firmware-level detection is a Circuit/Firmware Engineer decision |
| REQ-405 *(Rev 3, new — added at Independent Review, ISS-020)* | Firmware shall enforce a maximum commanded flywheel speed and reject/clamp any command exceeding it, using the already-wired FG tachometer feedback to verify actual speed does not exceed a defined ceiling; on exceeding that ceiling, firmware shall command the motor to a safe/stopped state | Must | Discovered gap: REQ-007's "≥3000 RPM" was only ever a functional *floor*; nothing previously bounded the *maximum* — the recommended motor's own no-load speed (≈20,000 RPM up to a corrected credible worst-case of ≈25,180 RPM — DS-MTR-018 corrected/DS-MTR-080, `hardware/schematic/bench-imu-01-design.md` §7.5.13; supersedes the previously-cited, mislabeled "22,200 RPM at full-charge 3S (11.1V)" figure) is 6.7–8.4× that floor, and stored rotational energy scales with the square of speed. This is a bounded safety cutoff, not the closed-loop attitude control REQ-009 excludes (the same way an overcurrent shutdown is not itself "control"). Exact ceiling/ramp-rate/response TBD by Firmware Engineer + human safety review — ties to REQ-403's safety-critical HITL gate. Must also feed Mechanical Lead's flywheel/containment design as a real input |
| REQ-406 *(Rev 3, new — added at Independent Review, ISS-021)* | Firmware shall implement a latched-fault policy on repeated motor driver Lock Detection events (a persistent stall/jam): count qualifying retries within a rolling time window and force the motor to a safe/stopped state requiring deliberate re-arm, rather than allowing the driver IC's own indefinite auto-retry behavior to continue unsupervised | Should | Discovered gap: none of the DRV10983's three protection mechanisms (OCP, Lock Detection, Thermal Shutdown) latch — all auto-recover/auto-retry, so REQ-404's "shutdown behavior to prevent sustained overheating" is not actually satisfied by the driver IC alone. A persistent mechanical jam would otherwise produce repeated fault-current pulses/restart attempts indefinitely. Companion to REQ-404 |
| REQ-407 *(Rev 4)* | New hazard shapes introduced by free rotation itself — (a) tip-over risk (a rig that can now rotate is less rigidly anchored to the bench than Rev 3's fixed mount), (b) pinch points at the pivot/mechanism interface, (c) cable/tether entanglement or strain at the rotating joint (REQ-113), (d) a possibly fast-spinning free platform if the reaction wheel is commanded to a large fraction of its speed range with the platform free (REQ-012's physics finding) — shall be assessed and mitigated before physical build | Must | Safety-critical — ties to the "safety-critical changes" HITL gate (`docs/architecture.md` §10), same gate class as REQ-403. These are genuinely **new** hazard shapes, not a restatement of REQ-403/404's flywheel-specific hazards — see REQ-408 |
| REQ-408 *(Rev 4)* | REQ-403/MISS-016's existing disposition (ACCEPTED-RISK, flywheel containment, `validation/open-issues.md`) does **not** automatically extend to cover the new physical configuration a free-rotation mechanism introduces — a fresh safety review is required once a specific mechanism is chosen and physically integrated, before that configuration's own Design-Complete-equivalent sign-off | Must | Explicit, per this task's own instruction not to assume Rev 3's disposition silently covers a new configuration. REQ-403/MISS-016 themselves are **not reopened or edited** by this revision |
| REQ-409 *(Rev 5, new — not an edit to REQ-403)* | The aggregate stored rotational energy across 3 simultaneous reaction wheels, plus the new hazard of hard electromagnetic braking (rapid momentum transfer, now realized in an actual jump/balance maneuver — REQ-021), shall be assessed and mitigated as its own safety analysis before this revision's Design-Complete-equivalent sign-off | Must | Safety-critical — ties to the "safety-critical changes" HITL gate (`docs/architecture.md` §10), same gate class as REQ-403/407. **Explicitly does not reopen or edit REQ-403/MISS-016** (`validation/open-issues.md`, single-flywheel containment, human `ACCEPTED-RISK` 2026-09-13) — that disposition covered exactly one flywheel at Rev 3/4's speeds and is left untouched. REQ-409 is the fresh requirement that actually governs the 3-flywheel + braking hazard shape going forward. Flagged for the Mechanical Reviewer's existing Foresight checklist (`docs/architecture.md` §3, `docs/architecture-evolution.md` §38) with **extra rigor**, once a real mechanical design exists to review — not resolved here. **§9h Q5 CONFIRMED via creator/"General Chat" session (§9i)**: framing pitched correctly, neither over- nor under-claiming. **Update — §9h Q2 is now ANSWERED YES (§9j): the jump/stand maneuver is a REAL, in-scope Rev 5 deliverable, not a hypothetical future capability.** The Foresight-checklist flag must now be read as covering an actual, physically-realized kinematic event (the assembly leaving contact with its support and impacting a vertex/edge) — structurally and energetically more demanding than 3 wheels merely spinning in place. This raises, not lowers, the rigor already called for; REQ-403/MISS-016 remain untouched |

## 7. Non-functional Requirements

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| REQ-501 | Component cost target: ≤ ~$15 USD total BOM cost at low-volume/prototype quantities | Should | Rough steer away from exotic/expensive parts, not a hard ceiling |
| REQ-502 | Schedule target | Won't / N/A | This is a paper/document design exercise this cycle, not a production schedule — no physical PCB fabrication or physical power-on happens in this session |
| REQ-503 *(Rev 3)* | Rev 3 total BOM cost target: proposed ≤ $75–90 USD (soft, not a hard ceiling) | Should | REQ-501 (~$15) is retained verbatim above as Rev 2's historical record; a motor+driver+flywheel subsystem realistically costs $20–50+ alone (2026 web-search-grounded ballpark, not yet datasheet-confirmed for specific candidates) — see §9b for confirmation |
| REQ-504 *(Rev 3)* | Schedule/physical-build framing unchanged from REQ-502 — this remains a paper/document design exercise this cycle: no physical PCB fabrication, no physical 3D print, no physical spin test, no physical power-on happens in this session | Won't / N/A | Mirrors REQ-502 exactly, restated for Rev 3 clarity since a spinning mass makes "no physical test" worth restating explicitly |
| REQ-505 *(Rev 4)* | Free-rotation mechanism BOM ceiling: **no ceiling imposed this cycle** — Human Chief Engineer explicitly waived the originally-proposed ≤$30–50 soft target (2026-09-01, via creator/"General Chat" session, §9g), separate from REQ-503's already-spent Rev 3 motor-subsystem budget | Won't (this cycle) | **Explicitly waived by the human, not silently dropped or overlooked** — mirrors this project's own anti-silent-drop discipline for a withdrawn/superseded requirement (e.g. REQ-005/006's "Won't" pattern; REQ-501/502 retained verbatim as historical record when superseded, not deleted). The originally-proposed ≤$30–50 default (§9d) is retained above/in history, not edited away — Candidate A's actual $13 price remains far under it regardless, so the waiver has no practical effect on the already-made mechanism choice; it confirms cost is not a gating factor for any future mechanism-adjacent decision this cycle |
| REQ-506 *(Rev 4)* | Mirrors REQ-502/504 exactly, **narrowed scope**: this requirement governs *physical* fabrication/purchase/testing only — no physical mechanism purchase, no physical 3D print, no physical spin test happens yet | Won't / N/A | Restated for Rev 4 clarity. **Does not block Mechanical Design/CAD work itself** — per Kyosuke's own explicit direction (2026-09-01, §9g), Mechanical Design (integrating the human-approved Candidate A mechanism into a new enclosure revision) is now authorized as the next phase; this requirement's original Notes text ("before any Mechanical Design/CAD work") is superseded by that direction and restated here accurately, not silently left stale |
| REQ-507 *(Rev 5)* | Rev 5 total BOM cost target: ≤ $450–800+ USD (soft, not a hard ceiling) — **re-opened for re-check, no longer simply CONFIRMED-as-final** | Should | Reflects the cost/complexity trade-off already presented to and approved by the human Chief Engineer as part of this scope decision (see header status line, §1c) — a 5–9× jump over Rev 3/4's ≈$75–90 ceiling, driven by 3× maxon-or-equivalent-class motors, 6× IMUs, 3× electromagnetic brakes, and a likely MCU upgrade. §9h Q3 CONFIRMED via creator/"General Chat" session (§9i). **Re-opened, not silently left as final (§9j)**: this figure was estimated before §9h Q2 was answered YES. A battery pack (now very likely required, REQ-115) and a brake/structural capability sized for real impulsive jump loads (not steady-state, REQ-015) were not part of the original comparison this ceiling was based on. The figure may need to move upward — flagged for re-confirmation once Component Selection (next PR) has real battery/brake cost data, not assumed to still hold as-is |
| REQ-508 *(Rev 5)* | Component Selection (next PR) shall write an explicit, individual, written re-justification for every Rev 1–4 part it carries forward unchanged at the new 3-axis/6-IMU/3-brake scale — "this is what the reference design used" is not by itself an adequate justification | Must | Testable/auditable process requirement, mirrors REQ-006's own "testable even though it's about what's populated, not silicon capability" pattern. Directly operationalizes §1c's "do not blindly copy JAXA's parts" instruction into something Independent Review can actually check for (a missing re-justification is a discoverable, checkable gap, not just a vague intention) |
| REQ-509 *(Rev 5)* | Schedule/physical-build framing unchanged from REQ-502/504/506 — this remains a paper/document design exercise this cycle: no physical PCB fabrication, no physical 3D print, no physical motor/brake purchase, no physical power-on happens in this session | Won't / N/A | Mirrors REQ-502/504/506 exactly, restated for Rev 5 clarity given the scale of the new subsystems being planned |

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
- **(Rev 4)** The free-rotation support mechanism's own mass/footprint is
  not yet counted in REQ-310's ≈280–320g rotating-assembly ESTIMATE — it is
  a new, small addition on top of it, not itself part of the rotating mass
  (a properly designed pivot's rotor-side hardware is typically negligible
  mass, e.g. a bearing's inner race + a short shaft stub — quantified once
  a specific mechanism is human-approved and a Mechanical Design pass
  actually sizes it).
- **(Rev 4)** "Free rotation" in REQ-011 means rotation relative to a fixed
  bench-mounted base/stand — the rig does not need to be untethered/
  free-floating in the sense a real on-orbit spacecraft is; REQ-113's
  service-loop tether is an accepted, deliberate departure from true
  micro-gravity-style free-floating, consistent with this being a bench
  demonstration, not flight hardware (mirrors the "not flight hardware"
  framing already established in §9b for the reaction wheel itself).

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

## 9d. Rev 4 — Open Questions for the Human (new, pending confirmation)

Same situation as Rev 3's own §9b: neither figure below had a prior anchor
to sharpen — both are this Hardware Lead's best-effort, reasoned proposals,
per `.github/skills/requirements-engineering/SKILL.md` step 2 ("propose a
measurable version... confirm with the human — do not silently invent a
number and treat it as settled").

1. **Angular-travel target (REQ-012).** Proposed: at least ±180°, ideally
   continuous/unlimited rotation, achieved initially via a flexible
   service-loop tether (REQ-113) rather than a slip ring, deferring the
   slip ring's added cost/complexity unless bring-up shows it's genuinely
   needed. **Is this the right target, or is a smaller bounded range (e.g.
   a torsion-suspension-compatible ±30–90°) actually sufficient/preferred
   for this cycle's demonstration goal?** This materially affects which
   Component Selection candidate wins — see `bom/component-selection.md`'s
   new Free-Rotation Support Mechanism section.
2. **Free-rotation mechanism BOM ceiling (REQ-505).** Proposed: ≤$30–50 USD
   soft target, separate from REQ-503's already-spent Rev 3 motor-subsystem
   budget. **Confirm this ceiling, propose a different one, or leave
   uncapped?**

**Deliberately not asked here, and not defaulted either** — per this
task's own explicit instruction: which specific mechanism candidate to
build (`bom/component-selection.md`'s new section, Candidates A–D) is an
architecture-level decision requiring explicit human approval before any
Mechanical Design/CAD work begins (mirrors the Power Architecture HITL
gate, `hardware/power-architecture.md`) — not answered, defaulted, or
provisionally adopted here.

## 9e. Rev 4 — Provisional status update (creator/"General Chat" session review)

The creator/"General Chat" session reviewed this Rev 4 plan before drafting
began and independently re-derived the REQ-012 platform-angular-rate
physics finding itself (across a 250–450g mass / 0.06–0.08m
characteristic-radius sweep, getting inertia ratios of ≈1:20–1:64 and
platform rates of ≈280–900°/s at a full 3000 RPM wheel command — the same
order of magnitude as, and independent confirmation of, this Hardware
Lead's own ≈1:15/≈1170°/s estimate) and explicitly approved proceeding with
drafting. This confirms the finding is sound and the approach is endorsed,
but is **not** the same thing as the human Chief Engineer's own Requirements
sign-off (§9d's two Open Questions, and the Component Selection candidate
choice, remain genuinely open) — see §10b.

## 9f. Rev 4 — Human priority clarification: speed to a physical result (new)

After the above was drafted and reported back, the human (relayed via the
creator/"General Chat" session, 2026-09-01) confirmed the actual driving
goal for this stage of the roadmap: **speed to a real, physical,
demonstrable 1-axis attitude-response result**, not the most thorough or
elaborate mechanism. He had initially considered starting directly at
3-axis, and was talked out of it — correctly, per real-world CubeSat ADCS
testbed precedent, which itself recommends starting with 1-axis — but
specifically **because 1-axis is the *faster* path to something real
working**, not merely the more careful/cautious one. This is recorded here
precisely (mirrors §9c/9e's own practice of recording human input exactly,
not paraphrased into something else) because it is a real steer, not a
restatement of anything already written:

- **Do not reopen or second-guess Rev 3's already-approved motor+flywheel
  selection** (`bom/component-selection.md` Motor/Motor Driver sections) —
  unaffected by this clarification, use as-is.
- **Favor the cheapest/simplest-to-source free-rotation mechanism that is
  good enough**, over anything requiring specialized fabrication or long
  lead times — this directly affects which Component Selection candidate is
  recommended primary (see the updated Recommendation in
  `bom/component-selection.md`'s Free-Rotation Support Mechanism section:
  Candidate A, a bolt-on-ready off-the-shelf bearing needing zero custom
  design work, is now primary over Candidate B, which has a better friction
  margin but needs a future custom shaft/mount design step first — slower
  to an actual physical result).
- **Keep the Requirements + Component Selection deliverable itself lean and
  focused**, not an exhaustive survey of every possible option — Candidate
  D (air bearing)'s treatment was trimmed accordingly; the core comparison
  and worked figures (mass ESTIMATE, friction margins, physics finding) are
  unchanged, since those are reusable engineering facts, not "extra options
  exploration".
- **The existing scope fence is unchanged**: no control loop/PID/attitude
  estimation this round (REQ-014), and the actual mechanism choice remains
  an explicit human decision point (§10b), not decided here — "faster" does
  not mean "AI decides for you," it means the options presented are
  themselves biased toward what can actually be built quickly once a choice
  is made.

## 9g. Rev 4 — Human decisions received: mechanism choice + Open Questions resolved (new)

Kyosuke's actual decisions on §9d's two Open Questions and the Free-Rotation
Support Mechanism candidate choice, received directly and relayed via the
creator/"General Chat" session, 2026-09-01:

1. **REQ-012 (angular-travel target)**: **Approved as proposed** — ≥180°,
   ideally continuous/unlimited rotation. No wording change to REQ-012
   itself.
2. **REQ-505 (mechanism BOM ceiling)**: **Waived** — no ceiling imposed
   this cycle; cost is not to gate this decision. REQ-505's own row above
   is updated to `Won't (this cycle)` recording this as an explicit human
   waiver, not a silent drop.
3. **Mechanism choice**: **Candidate A — BC Precision 4LS-3 lazy-susan
   turntable bearing — confirmed**, matching the Hardware Lead's own
   revised (post-§9f) recommendation. See `bom/component-selection.md`'s
   Free-Rotation Support Mechanism Approval table for the full record.

**Kyosuke also authorized the next phase**: Mechanical Design — integrating
Candidate A into a new revision of the Bench-IMU-01 enclosure — is now
in scope (it was explicitly out of scope for this task through §9f). The
other scope fences remain active and unchanged: no control loop/PID/
attitude estimation, no 2nd/3rd reaction wheel, no Control Engineer
introduction (REQ-014 continues to govern). Mechanical Lead + Independent
Mechanical Review are to be used per this repo's established process,
mirroring Rev 3's own mechanical rigor — with a plan reported back before
substantial CAD work begins, the same Human-in-the-loop pattern already
used throughout this revision.

## 9h. Rev 5 — Open Questions for the Human (new, pending confirmation)

Same situation as every prior revision's own §9b/§9d: proposed defaults
below are this session's best-effort, reasoned proposals per
`.github/skills/requirements-engineering/SKILL.md` step 2 ("propose a
measurable version... confirm with the human — do not silently invent a
number and treat it as settled"), not silent assumptions. The
scope/cost-complexity trade-off decision itself is **already approved**
(header status line, §1c) — these 5 questions are the genuinely open
sub-questions that decision leaves.

1. **Per-axis torque/momentum target (REQ-015).** Proposed: reuse Rev 3's
   already-approved target unchanged per axis (≥5 mN·m continuous,
   ≥3000 RPM, T-Motor-MN2206-13-class — `bom/component-selection.md` Motor
   section) for all 3 axes, since 3 independent single-axis wheels don't
   need a *higher per-axis* target merely because there are 3 of them.
   **This changes if Q2 below resolves "yes, the jump-and-balance maneuver
   is in scope"** — that maneuver's rapid brake-transfer physics is a
   fundamentally different calculation (impulsive torque, not steady-state
   torque) and would need its own fresh derivation, not reuse of REQ-007's
   steady-torque figure. Confirm the per-axis-unchanged default, or state a
   different target?
2. **Is the Cubli-style jump-and-balance maneuver itself an in-scope Rev 5
   deliverable?** Proposed default: **no — deferred** (REQ-021). Rev 5's
   own scope is the 3-axis attitude-hold/momentum-management hardware +
   control-loop capability (REQ-015–019); the jump maneuver is a
   materially harder, later capability, mirroring this project's own
   repeated "favor the faster/leaner path to a real result" precedent
   (§9f) rather than front-loading the hardest capability. Confirm
   deferring it, or is the jump maneuver itself the point of committing to
   3-axis now?
3. **Rev 5 BOM ceiling (REQ-507).** Proposed: ≤$450–800+ USD soft target,
   reflecting the cost/complexity comparison already presented for this
   scope decision. Confirm this figure, or propose a different one?
4. **Wireless (REQ-020) and power-source architecture (REQ-115).**
   Proposed: wireless is **Should**, not Must, parallel to the existing
   UART/USB tether (not a replacement for it this cycle). Proposed: Power
   Engineer's fresh pass should treat **battery power as a live option
   again** — Rev 3's Option C (battery) was explicitly rejected in favor
   of a tethered barrel-jack motor rail, but that reasoning assumed a
   fixed-mount, non-jumping rig; an eventual untethered maneuver is likely
   incompatible with any tether at all. Confirm this reasoning, **or**
   state that a tethered-only "3-axis attitude-hold demonstration, no jump
   maneuver" mode is acceptable for the foreseeable future (which would
   let Power Engineer keep extending Option A instead of reopening the
   battery question) — this materially changes Power Engineer's own next
   scope.
5. **Safety requirement rigor (REQ-409).** Is the proposed framing (a
   fresh, standalone safety requirement for the aggregate 3-flywheel +
   braking hazard, explicitly not reopening REQ-403/MISS-016's own
   single-flywheel disposition, flagged for the Mechanical Reviewer's
   Foresight checklist with extra rigor once a real design exists) pitched
   at the right level — neither overclaiming a hazard that hasn't been
   analyzed yet, nor underclaiming the real jump in stakes 3 simultaneous
   energized flywheels plus hard braking represents versus Rev 4's single
   free-spinning wheel?

**Deliberately not asked here, and not defaulted either** — per this
project's own established sequencing (mirrors Rev 3's §9b closing note and
Rev 4's §9d closing note): the actual Component Selection candidates
(MCU/IMU/Motor/Driver/Brake/Wireless — §1c items 1–5) and the actual Power
Architecture decision (REQ-115) are answered later, at their own dedicated
phases/HITL gates, once real datasheet/current/voltage numbers exist — not
guessed now with no data behind them.

**Note — a real, independently-verified cross-branch dependency for REQ-312
(added after `main` was merged into this branch mid-session, per an
automated overnight-check-in cross-session message; the specific claim was
independently re-verified against `origin/main` before being recorded here,
not taken on the sender's word — one part of that message's own framing
["main is currently green"; PR #38 "deliberately unmerged"] was checked and
found to be **incorrect**: PR #38 is in fact already merged to `main`
(2026-09-03T17:31:43Z) and `main`'s tip currently fails `hardware-gate` for
exactly this reason — see the reply sent to that session and to the
creator/"General Chat" session for the full correction).** `validation/
open-issues.md` **MISS-034** (CRITICAL, OPEN) establishes that `hardware/
mechanical-interface.md`'s current PCB basis (100×50mm) is stale — the real,
already-laid-out board is **150×95mm** with a **134×79mm** M2.5
mounting-hole pattern (`hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb`
`Edge.Cuts`) — put concretely by `validation/design-review.md`'s own
"Mechanical Reviewer — Cycle 10" entry, the real board's 150mm X extent is
larger than the *entire* current base-assembly STL's own measured bounding
box (123.0mm X), so it does not fit under any operating condition, not a
tolerance/corner case. This is **not** a Rev 5 finding and is **not resolved, silently
dispositioned, or pre-empted by this revision** — which side moves (grow the
enclosure, or re-lay-out the board) is an explicit Chief-Engineer
architecture/scope decision (`docs/architecture.md` §10). It is recorded
here only so that whichever future PR actually performs REQ-312's
3-orthogonal-wheel cube-frame Mechanical Design starts from the real board
geometry above, not the superseded 100×50mm figure `mechanical-interface.md`
still shows today — inheriting MISS-034's own stale-basis defect into a
brand-new design would be a foreseeable, avoidable repeat of exactly the
failure mode MISS-034 itself describes.

## 9i. Rev 5 — Creator-session confirmation of §9h Q1/Q3/Q4/Q5; Q2 reserved for the human (new)

The creator/"General Chat" session reviewed PR #39 and §9h in full and
responded on delegated authority for 4 of the 5 Open Questions, explicitly
declining to decide the 5th on the human's behalf — mirroring this
project's own established practice (e.g. §9c's "provisional adoption,"
§9e/§9f/§9g's own staged pattern) of routing sequencing/technical judgment
calls through the creator session while reserving genuinely consequential
calls for the human Chief Engineer directly.

- **Q1 (per-axis torque target, REQ-015) — CONFIRMED**: reuse Rev 3's
  target unchanged (≥5mN·m, ≥3000RPM) for all 3 axes, **conditional on Q2
  staying "deferred."** If Q2 ever flips to "jump maneuver in scope," this
  figure needs a fresh impulsive-torque derivation, not steady-state
  reuse.
- **Q2 (Cubli-style jump-and-balance maneuver in/out of scope, REQ-021) —
  EXPLICITLY NOT DECIDED, reserved for the human Chief Engineer.** The
  creator session's own reasoning, recorded here in substance (not
  paraphrased into something else, mirroring this file's own §9e/§9f
  practice): this is the one genuinely consequential question in this
  set, not a technical default — it determines whether Rev 5 takes on
  JAXA's single most hazardous, most complex, most iconic capability
  (impulsive brake-transfer dynamics, the entire reason the reference
  design has electromagnetic brakes + battery power at all) or defers it.
  **Verified, not hearsay** (upgraded from an earlier "reportedly" hedge
  after independently querying the creator/"General Chat" session's own
  turn history, `session_store_sql`, session `7fab99ef-5578-4d79-a9c2-
  b24dbcfe93be`, turn 387, timestamp `2026-09-03T17:03:59Z`): the human
  Chief Engineer's own message, verbatim, reads — 「私が作りたいのは
  JAXAの方です。今の私の回路とJAXAのものを比較してよりいいものができるなら
  それを考えてみてください。そして全てやり直しても構いません。」 ("What I
  want to build is the JAXA one. Compare my current circuit with JAXA's
  and if you can make something better, consider it. And it is fine to
  redo everything.") — which means the conservative deferral (REQ-021's
  own proposed default) cannot be safely assumed to be what he wants just
  because it is the lower-risk engineering choice. **This same message's
  "fine to redo everything" clause is deliberately NOT recorded here as
  bearing on MISS-034's disposition** (which side moves, enclosure vs.
  board — `docs/architecture.md` §10) — it is cited only for Q2's own
  narrower context (the human's own stated build target), not as
  pre-authorization for any architecture decision. **REQ-021 therefore
  remains an explicitly proposed working default, not a finalized
  requirement** — used so downstream
  Requirements-phase work isn't blocked, but with three binding
  conditions until the human actually answers: (a) REQ-021's own row
  keeps its "proposed/working default only — pending human confirmation"
  language, not silently upgraded to a settled `Won't`; (b) no
  irreversible downstream design choice may foreclose a future "yes" —
  concretely, Power Engineer's future pass must not rule out battery
  power entirely (REQ-115), and Component Selection's future brake
  sizing must not assume steady-state-only torque; (c) this question
  must be surfaced again, prominently, at this project's next natural
  human-facing checkpoint (expected: the Component Selection approval
  gate, next PR).
- **Q3 (BOM ceiling, REQ-507) — CONFIRMED**: ≤$450–800+ USD soft target,
  as proposed — matches the real cost comparison the human already saw
  and approved when he made the underlying scope decision (header status
  line, §1c).
- **Q4 (wireless + power architecture, REQ-020/REQ-115) — CONFIRMED as
  written**: wireless stays **Should**, not Must; Power Engineer's
  eventual fresh pass keeps battery power a live option, **not
  re-foreclosed**, precisely because Q2 is not yet settled — Power
  Engineer must not commit to "tethered-only forever" while Q2 remains
  open.
- **Q5 (safety requirement rigor, REQ-409) — CONFIRMED**: framing is
  pitched correctly, neither over- nor under-claiming, correctly
  deferred to a real mechanical design + the Mechanical Reviewer's
  Foresight checklist.

**PR #39's own merge/approval status**: the creator session is explicitly
holding on merging/approving PR #39 until the human has a chance to weigh
in on Q2 specifically (or confirms deferring is fine) — this is the
human's call, not forced through on the strength of the other 4
confirmations. Recorded here so a future reader does not mistake "4 of 5
questions confirmed" for "this PR is ready to merge."

## 9j. Rev 5 — Human decision received: §9h Q2 = YES; MISS-034 decision criterion given (new)

Kyosuke's own answer, relayed via the creator/"General Chat" session and
**independently verified by this session directly against that session's
own turn history** (`session_store_sql`, session
`7fab99ef-5578-4d79-a9c2-b24dbcfe93be`, turn 415, timestamp
`2026-09-03T23:49:20.372Z`) — not accepted on the strength of a relayed
summary alone. A first relay of this same decision arrived without a
verifiable citation and was explicitly declined pending independent
confirmation (see the turn immediately following 415 in that same
session's history); this section is written only after that confirmation
succeeded, mirroring the same discipline §9i's own "reportedly" upgrade
already established.

**Verbatim (Kyosuke's own message, turn 415):**

> 1についてはなるべく障害が少ない方を選んでみて、拡大する方が作りやすい気もします。小さくする方が簡単ならそっちにして、どちらの方が障害が多いかで決めて、
>
> 本体を立たせるところもやりたいです。

("For #1 [MISS-034], try choosing whichever option has fewer obstacles —
I feel like the enlarging approach might be easier to build. If making it
smaller is easier, go with that instead; decide based on which has more
obstacles. I also want to do the part where the body stands up.")

- **§9h Q2 — ANSWERED: YES.** "本体を立たせるところもやりたいです" ("I also
  want to do the part where the body stands up") is a direct, unambiguous
  answer: the Cubli-style jump-and-balance maneuver **is** an in-scope
  Rev 5 deliverable, not deferred. REQ-021 updated accordingly (now
  Must, no longer a proposed default) — see REQ-021's own row for the
  current requirement text.
- **MISS-034 — a decision *criterion* was given, not a specific verdict**
  (recorded precisely, not flattened into "the human decided X," mirroring
  this file's own §9e/§9f practice of quoting real input exactly rather
  than paraphrasing it into something else): Kyosuke asked that whichever
  option (grow the enclosure vs. shrink/re-lay-out the PCB) has **fewer
  technical obstacles** be chosen, stating a lean toward enlarging
  "feeling easier to build" but explicitly open to the other path if it
  is actually simpler — he did not simply say "grow it." The creator/
  "General Chat" session's own reply (same turn) reports comparing the
  two paths concretely (enlarging: 2 parametric CAD value changes, does
  not touch the already-DRC-verified PCB; shrinking: a 2.85× area
  reduction requiring electrical redesign, DRC re-verification, and
  component-placement-failure risk) and adopting **enlarge** as
  satisfying Kyosuke's own stated criterion, with a dedicated fix session
  reported underway, independent of this branch. **This revision does
  not itself disposition MISS-034** — that remains
  `validation/open-issues.md`'s own record, owned by whichever session
  performs that fix, not edited here (REQ-312's Notes are updated only to
  reflect that a fix is reported in progress, not that it has landed).
- **Cascading updates made to this file as a direct consequence of Q2 =
  YES** (each REQ's own row carries the full detail; summarized here for
  a single point of reference): **REQ-015** (per-axis torque/momentum
  target — the steady-state-reuse default has lapsed; needs a fresh
  impulsive-torque derivation once real brake response-time data exists);
  **REQ-115** (power architecture — battery is now very likely a hard
  requirement, not merely a kept-open option); **REQ-020** (wireless —
  upgraded to Must for the jump/stand maneuver's own operating mode);
  **REQ-409** (safety — the Foresight-checklist flag now covers a real,
  physically-realized kinematic event, not a hypothetical future
  capability); **REQ-507** (BOM ceiling — re-opened for re-confirmation,
  not assumed to still hold once battery + jump-rated brake/structural
  costs are real numbers).
- **What this does NOT do**: it does not itself perform Component
  Selection, Circuit Design, or Mechanical Design for any of the above —
  those remain later PRs, per §1c's own expected sequence. It does not
  touch REQ-403/MISS-016 (still exclusively about the single,
  already-dispositioned Rev 3/4 flywheel) or edit MISS-034's own
  disposition text in `validation/open-issues.md`.

## 10. Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Chief Engineer (Human) | Human Chief Engineer (via creator/"General Chat" session) | 2026-08-30 | **Approved** — requirements confirmed final; proceed to Component Selection |

## 10a. Rev 3 Approval (real human sign-off received — supersedes the "provisional" framing above)

| Role | Name | Date | Decision |
|---|---|---|---|
| Hardware Lead | Hardware Lead (this session) | 2026-08-31 | Provisionally adopted all four §9b defaults after `ask_user` went unreachable this cycle (see §9c) — superseded by the real human confirmation below, received via the creator/"General Chat" session (the channel that has actually reached the human this cycle) |
| Chief Engineer (Human) | Human Chief Engineer (via creator/"General Chat" session, who relayed to and confirmed with the human directly) | 2026-08-31 | **Approved — "all four provisional defaults are approved as proposed, no changes."** This is the human's real Rev 3 Requirements sign-off, not a provisional placeholder — REQ-007's target figures, no motor-type preference, REQ-503's ≤$75–90 ceiling, and REQ-308's bare-bench-rig/~150mm sanity bound are now confirmed requirements, not open questions. Component Selection (motor + driver) proceeded against these targets and is recorded in `bom/component-selection.md`. Process note recorded for the rest of this design cycle: since `ask_user` is not reliably reaching the human this cycle, every remaining HITL gate is routed through the cross-session message channel instead (report the gate content there, wait for a reply there) rather than falling back to provisional-autonomous adoption. |

## 10b. Rev 4 Approval (real human sign-off received — supersedes the "pending" framing above)

| Role | Name | Date | Decision |
|---|---|---|---|
| Hardware Lead | Hardware Lead (this session) | 2026-09-01 | **Proposed** — Rev 4 free-rotation-support requirements (REQ-011–014, REQ-113, REQ-205, REQ-310–311, REQ-407–408, REQ-505–506) drafted per `.github/skills/requirements-engineering/SKILL.md`. Both §9d Open Questions (angular-travel target, mechanism BOM ceiling) and the Component Selection mechanism choice (`bom/component-selection.md`'s new Free-Rotation Support Mechanism section) are explicitly routed to the human Chief Engineer for review, not silently adopted — reported via cross-session message per this file's own §10a-established process note (`ask_user` not reliably reaching the human this cycle). |
| Creator/"General Chat" session | — | 2026-09-01 | Reviewed the plan for this revision before drafting began, independently re-verified the REQ-012 physics finding (§9e), and approved proceeding — this is process endorsement of the approach, not the human Chief Engineer's own Requirements sign-off |
| Chief Engineer (Human), via creator/"General Chat" session | Human Chief Engineer | 2026-09-01 | Priority clarification received (§9f): speed to a physical, demonstrable result is the actual goal; do not reopen the motor/flywheel selection; favor the simplest/fastest-to-source mechanism; keep the deliverable lean. **Not yet the Requirements sign-off itself** — §9d's two Open Questions and the mechanism choice remain open |
| Hardware Lead | Hardware Lead (this session) | 2026-09-01 | Revised the Component Selection recommendation accordingly (Candidate A now primary — see `bom/component-selection.md`) and trimmed the deliverable per §9f. Still routed to the human for the actual mechanism decision, not self-approved |
| Chief Engineer (Human) — real Requirements sign-off, via creator/"General Chat" session | Human Chief Engineer (Kyosuke) | 2026-09-01 | **Approved.** REQ-012: approved as proposed (≥180°, ideally continuous), no change. REQ-505: waived — no BOM ceiling this cycle (row updated to `Won't (this cycle)`, explicit waiver recorded, not a silent drop). **Mechanism choice: Candidate A (BC Precision 4LS-3 lazy-susan bearing) confirmed** — see `bom/component-selection.md`'s own Approval table. Full record: §9g. **Also authorized the next phase**: Mechanical Design (integrating Candidate A into a new enclosure revision) is now in scope — other scope fences (no control loop/PID/attitude estimation, no 2nd/3rd wheel, no Control Engineer) remain active. This is the human's real Rev 4 Requirements sign-off, not a provisional placeholder. |

## 10c. Rev 5 Approval (staged — mirrors Rev 4's own §9f/§9g/§10b honesty pattern)

| Role | Name | Date | Decision |
|---|---|---|---|
| Chief Engineer (Human), via creator/"General Chat" session | Human Chief Engineer (Kyosuke) | 2026-09-04 | **Approved — scope/budget decision.** Commit now to the full 3-axis reaction-wheel "Cube" destination (`docs/architecture.md` §11), including the presented cost/complexity trade-off (≈$450–800+ estimated BOM, a 5–9× jump over Rev 3/4's ≈$75–90 ceiling). This decision was made with full awareness of the trade-offs, presented as a comparison before approval — not re-litigated by this session. **Does not by itself approve** the detailed REQ-015–021/114–115/206/312/409/507–509 draft or §9h's proposed defaults below — those are this session's own proposal, routed for confirmation next. |
| Hardware Lead | Hardware Lead (this session) | 2026-09-04 | **Proposed** — Rev 5 requirements (REQ-015–021, REQ-114–115, REQ-206, REQ-312, REQ-409, REQ-507–509) drafted per `.github/skills/requirements-engineering/SKILL.md`, extending/superseding Rev 3/4 content without deleting any prior ID (REQ-009/014 retained verbatim, superseded by REQ-017; REQ-403 retained verbatim, extended by REQ-409). §9h's 5 Open Questions are explicitly routed to the human Chief Engineer for review, not silently adopted — reported via `ask_user` and/or the cross-session message channel to the creator/"General Chat" session, mirroring the process note established at §10a. |
| Creator/"General Chat" session | — | 2026-09-04 | Reviewed PR #39 and §9h in full; **confirmed Q1/Q3/Q4/Q5 on delegated authority** (per-axis torque target, BOM ceiling, wireless/power-architecture reasoning, safety-REQ rigor — see §9i for the full record). **Explicitly declined to decide Q2** (whether the Cubli-style jump-and-balance maneuver is in scope) on the human's behalf — reserved for the human Chief Engineer directly, since the human has, verbatim (§9i), described this whole revision as "what I want to build is the JAXA one," and that maneuver is that design's signature demonstration. This is process/technical-judgment endorsement for 4 of 5 questions, **not** the human Chief Engineer's own Requirements sign-off, and **not** a merge/approval of PR #39 — the creator session is explicitly holding on that until Q2 is resolved (§9i) |
| Chief Engineer (Human) — real §9h Q2 sign-off, via creator/"General Chat" session, independently verified by this session against that session's own turn history before being recorded | Human Chief Engineer (Kyosuke) | 2026-09-04 | **Answered — YES.** "本体を立たせるところもやりたいです" ("I also want to do the part where the body stands up") — the Cubli-style jump-and-balance maneuver (REQ-021) is confirmed in scope for Rev 5, no longer deferred. Full record, verbatim quote, verification method, and cascading REQ updates (REQ-015/020/115/409/507): §9j. This is the human's own real, verified Q2 sign-off — not a provisional placeholder, and not accepted into this document until independently confirmed against the primary turn-history source. Separately, and not dispositioned here: Kyosuke also gave a decision *criterion* for MISS-034 (choose whichever of grow-enclosure/shrink-PCB has fewer technical obstacles) — see §9j for why this is recorded as a criterion, not a specific verdict, and why MISS-034's own disposition remains `validation/open-issues.md`'s record, not this file's. |
