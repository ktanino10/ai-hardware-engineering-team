# Requirements

Status: **APPROVED** (2026-08-30, human Chief Engineer, via ask_user "Approve all three as recommended" at the Component Selection checkpoint — see §10 Approval and `validation/change-log.md`). All 4 Open Questions in §9 were answered as-proposed; see §10a.

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

## 2. Functional Requirements

| ID | Requirement | Priority (Must/Should/Could) | Notes |
|---|---|---|---|
| REQ-001 | Read 3-axis acceleration and 3-axis angular rate (6-axis IMU) at ≥ 100 Hz output data rate | Must | Quantified from an ambiguous "IMU" goal; the ≥100 Hz figure is this cycle's own testable floor, not a re-typed template placeholder |
| REQ-002 | Provide a hardware debug/programming interface for the MCU (flash + basic debug) | Must | Firmware itself is out of scope this cycle, but the board must not be a dead end — Circuit Engineer picks the connector matching the selected MCU family's standard debug interface |
| REQ-003 | Provide a visual status/heartbeat LED | Should | Low-cost bench-use diagnostic aid |
| REQ-004 | Provide a manual reset button for the MCU | Could | Dev-use convenience, not required for core function |
| REQ-005 | Onboard data logging/storage (e.g. SD card, external flash) | Won't (this cycle) | Out of scope — keeps the benchmark to its named 3 parts (MCU + IMU + Power); revisit only if a future cycle needs it |
| REQ-006 | Any wireless (Wi-Fi/BLE/etc.) functionality actually implemented/enabled on this board | Won't (this cycle) | Applies even if a selected MCU candidate's silicon includes radio hardware — ecosystem quality is one Component Engineer scoring factor (§ component-selection SKILL), not a license to add radio circuitry now; adding wireless would be an architecture decision requiring its own HITL gate (`docs/architecture.md` §10) |

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

## 4. Environmental Requirements

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| REQ-201 | Operating ambient temperature: 0 °C to +40 °C, indoor desk/lab use | Should | Sharpened from "UNKNOWN" using the human's own stated context ("desk/development use"); not Must since it's a working assumption, not a safety-critical bound |
| REQ-202 | Vibration/shock qualification | Won't (not applicable) | No rotating body/motor in this benchmark, so the `docs/architecture.md` §12 mechanical/thermal co-design trigger does not apply this cycle |
| REQ-203 | Standard indoor handling; ESD precautions during assembly/bring-up | Should | Ties to `validation/bring-up-procedure.md`'s existing ESD checklist item |

## 5. Mechanical / Form Factor Constraints

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| REQ-301 | Single 2-layer PCB — no daughtercards/stacked boards | Should | Keeps the Mechanical Phase 1 benchmark tractable: one flat board is far more tractable for a first Mechanical-discipline enclosure exercise than a stacked/multi-board assembly |
| REQ-302 | Target PCB footprint ≤ 60 mm × 40 mm | Should | A concrete envelope for Circuit/Mechanical Lead to design against; refined once real component footprints are known |
| REQ-303 | External connectors/headers (USB, UART header, debug header) concentrated on ≤ 2 board edges | Should | Directly supports the benchmark's own success bar — simpler connector placement materially raises the odds of a believable, buildable enclosure (`docs/architecture-evolution.md` §24) |
| REQ-304 | ≥ 4 mounting holes sized for M2 or M2.5 fasteners | Must | Needed for enclosure standoffs; a concrete quantified default rather than "some mounting holes" |
| REQ-305 | Enclosure: 2-piece (lid + base), 3D-printable, no complex machining | Should | Matches the Mechanical Lead's documented Phase 1 scope (`.github/agents/mechanical-lead.agent.md`) |

## 6. Safety / Regulatory Constraints

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| REQ-401 | No specific regulatory certification target (e.g. FCC/CE/UKCA) for this prototype/benchmark iteration | Won't (this iteration) | Explicitly out of scope rather than silently ignored; see future Safety/Compliance Reviewer role, `docs/architecture.md` §14, if this ever targets a regulated market |
| REQ-402 | USB port includes basic transient/ESD and reverse-polarity protection appropriate for a hand-handled connector | Must | Standard good practice; ties into Circuit Engineer's "Protection" checklist item |

## 7. Non-functional Requirements

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| REQ-501 | Component cost target: ≤ ~$15 USD total BOM cost at low-volume/prototype quantities | Should | Rough steer away from exotic/expensive parts, not a hard ceiling |
| REQ-502 | Schedule target | Won't / N/A | This is a paper/document design exercise this cycle, not a production schedule — no physical PCB fabrication or physical power-on happens in this session |

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

## 10. Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Chief Engineer (Human) | Human Chief Engineer (via creator/"General Chat" session) | 2026-08-30 | **Approved** — requirements confirmed final; proceed to Component Selection |
