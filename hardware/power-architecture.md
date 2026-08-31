# System Power Architecture

The system-level power-tree / rail-topology proposal and decision record —
which physical rails exist, at what nominal voltage, sourced from where, and
why — owned by the **Power Engineer** (Phase 3 of the multidisciplinary
evolution, `docs/architecture-evolution.md` §33) once a project's power
complexity exceeds what the Circuit Engineer tracks ad hoc directly in
`hardware/power-budget.md` alone (`docs/architecture.md` §12/§14).

## Relationship to `hardware/power-budget.md`

These are two different artifacts, kept separate on purpose:

- **This file** is the *architecture* record — the options considered, their
  trade-offs, and the human Chief Engineer's decision on rail topology and
  physical source(s). It changes rarely: only when the rail topology itself
  changes (e.g. a new subsystem forces a new physical input), not every time
  a subsystem's current draw is merely re-tallied.
- **`hardware/power-budget.md`** is the *numeric rollup* — every subsystem's
  current/power draw against each rail's supply capability, with margin. It
  is updated every time a subsystem is added, per its own existing header
  note, regardless of whether the architecture itself changed.

## Who fills this in

Per `.github/agents/power-engineer.agent.md`, the **Power Engineer** is
responsible for populating this file, once engaged (see that file's "When
this role is engaged" — a Hardware Lead judgment call per project/revision,
not automatic for every design). Until Power Engineer is engaged for a given
project, `hardware/power-budget.md` alone remains sufficient and this file
stays a template, per `docs/architecture.md` §12's original framing
("Circuit Engineer maintains `hardware/power-budget.md`... until [system
complexity grows past the benchmark]").

## Design: Bench-IMU-01 Rev 3 (Power Engineer, 2026-08-31)

### Existing-rail aggregation (why a new rail is structurally required)

- Existing logic rail only: **3V3 = 500 mA max** from U3 = TLV75533PDBVR
  [DS-PWR-003].
- Existing logic worst-case load already recorded in `hardware/power-budget.md`:
  **≈16.2 mA worst-case** [DS-MCU-014, DS-IMU-010, DS-PWR-003].
- Remaining current headroom on that rail: **≈483.8 mA** (= 500 − 16.2 mA).
- Recommended motor+driver pair's real new load basis:
  - Motor target current for 5 mN·m: **≈1.05 A** at the shaft, derived from
    Kt = 4.77 mN·m/A for T-Motor MN2206-13 KV2000 [DS-MTR-017, DS-MTR-020].
  - Driver continuous capability: **2 A continuous / 3 A peak per phase** for
    TI DRV10983 [DS-MTR-034].
  - Driver input range: **8–28 V**, so the pair only works at an
    approximately-12V-class operating point, not on the existing 5V/3V3 rails
    [DS-MTR-032].
- Therefore the existing rail is structurally insufficient in **both**
  dimensions:
  1. **Voltage mismatch**: 3.3 V logic rail and 5 V USB VBUS are both below the
     ≈12 V class operating point needed to clear the driver's 8 V minimum with
     real margin [DS-MTR-032].
  2. **Current-scale mismatch**: the existing rail's full remaining headroom
     (≈483.8 mA) is less than half the motor's **≈1.05 A target current**, and
     only ~24% of the driver's 2 A continuous rating [DS-PWR-003, DS-MTR-020,
     DS-MTR-034].

A **separate motor rail** is therefore required; extending the existing 3V3
logic rail is not a viable option.

## Architecture Options

| Option | Description | Real current/voltage basis (Evidence ID) | Pros | Cons | Recommended? |
|---|---|---|---|---|---|
| **Option A — Dual-input board: keep existing USB 5V logic input, add a second dedicated ~12V-class motor input** | Preserve Rev 2's existing USB-powered 3V3 logic rail exactly as-is, and add a physically separate motor-power input (for example a barrel jack or a second dedicated power connector) feeding a new motor rail specified to support the DRV10983 + MN2206 pair at approximately 12 V class. | Existing logic remains ≈16.2 mA worst-case on 3V3 vs 500 mA capability [DS-PWR-003]. New motor rail sized around ≈12 V and ≥1.05 A target load, with driver-side capability up to 2 A continuous / 3 A peak [DS-MTR-020, DS-MTR-032, DS-MTR-034]. | Cleanest electrical isolation between logic and motor power; easiest to prevent motor brownout/stall transients from pulling down the logic rail; preserves Rev 2 behavior for MCU/IMU bring-up; no dependence on USB-PD negotiation. Lowest integration risk for first bench bring-up. | Gives up single-cable convenience; adds at least one new connector and associated protection/inrush design; board is no longer purely USB-powered as a complete system. New connector/power-entry part must be sourced later. | **Yes — RECOMMENDED** |
| **Option B — Single-connector USB-C Power Delivery sink for both logic and motor** | Replace the simple 5V-only USB input assumption with a USB-C PD sink architecture that negotiates a higher-voltage contract from one connector, then derives both the motor rail and the existing 3V3 logic rail from that negotiated input. | Motor pair needs ≈12 V class because driver VM min is 8 V and motor is intended for 3S-equivalent operation in this pairing [DS-MTR-017, DS-MTR-032]. Current target remains ≈1.05 A at motor load, with rail sizing prudently nearer the driver's 2 A continuous capability [DS-MTR-020, DS-MTR-034]. | Keeps a true single-cable bench setup; avoids a second external supply connector; can satisfy both rails from one upstream source if the PD contract is available. | Adds a PD sink / trigger / policy controller part plus contract/fallback behavior complexity; if only plain 5V is present, the motor rail cannot meet the driver's voltage requirement; motor and logic now share one upstream source so inrush/fault isolation must be engineered more carefully. New PD-control part must be sourced later. | **Maybe** |
| **Option C — Battery-backed motor rail (e.g. 3S LiPo) with USB retained for logic or charging/service only** | Add a battery source dedicated to the motor rail, with the 3S LiPo voltage range aligning naturally with the motor's own 3S operating range; existing USB 5V input can remain for logic/programming or be repurposed around the battery architecture. | Motor's published operating range is 2S–3S LiPo, 7.4–11.1 V nominal / 8.4–12.6 V full-charge [DS-MTR-017]. Driver VM is 8–28 V [DS-MTR-032], so a 3S pack clears the driver's minimum across most of discharge, unlike 2S. Motor target current remains ≈1.05 A, with driver rated to 2 A continuous / 3 A peak [DS-MTR-020, DS-MTR-034]. | Electrically natural fit to the motor's published rating; excellent transient capability for motor surges; no dependence on USB source capability or PD support. | This is an explicit departure from the original desk/bench "USB 5V, not battery" framing of Rev 1/2, even though Rev 3 left extension of that constraint open [REQ-101 context, REQ-108]. Adds battery safety/charging/protection questions and bench-handling complexity. Requires new battery connector/power-management parts to be sourced later. | **No** |

### Option trade-off notes

- **Budget impact against REQ-503**:
  - Already-selected motor + driver consume **≈$21.57** total
    (= $18.99 + ≈$2.58) [DS-MTR-023, DS-MTR-040].
  - Remaining soft budget headroom is therefore **≈$53.43–68.43** against the
    approved **$75–90** Rev 3 target [REQ-503].
  - **Option A** adds one power-entry connector plus whatever upstream
    protection / enable / filtering Circuit Engineer later implements around
    that entry. This is a real BOM hit, but likely the smallest architectural
    complexity increase.
  - **Option B** adds a USB-C PD sink / trigger / policy-controller function,
    and likely still needs upstream protection / inrush control. This consumes
    more BOM and design complexity than Option A before the actual motor-power
    stage is even built.
  - **Option C** adds a battery connector and battery-management/protection
    path; it is the largest scope departure and likely the most cross-domain
    cost/risk addition, despite being electrically plausible.
- **What each option gives up from Rev 1/2**:
  - **Option A**: gives up "single connector powers the whole system".
  - **Option B**: gives up Rev 2's simple 5V-only USB power-entry assumption.
  - **Option C**: gives up the original non-battery bench-power framing most
    strongly of all 3 options.

## Rail Sequencing / Coupling Notes

- A motor-rail stall, startup surge, or fault should be assumed capable of
  producing supply droop and conducted noise at a scale irrelevant to the
  existing ≈16.2 mA logic rail but significant to a shared upstream source,
  because the new subsystem operates at roughly **1–2 A continuous-class** with
  higher transient demand [DS-MTR-020, DS-MTR-034].
- Therefore the new motor rail should be treated as needing **independent
  enable / inrush / fault containment**, regardless of which option is chosen:
  this is especially important for **Option B**, where logic and motor share
  one negotiated upstream source.
- **Option A** is intrinsically best isolated: a motor-rail brownout or short
  is least likely to collapse the 3V3 logic rail if the physical sources are
  separate, though shared ground-return/layout care is still required at
  Circuit Design.
- **Option B** is the most coupling-sensitive: PD source droop, cable IR drop,
  or rail startup behavior could affect both the motor rail and the 3V3 logic
  derivation unless explicit power-path sequencing and bulk/inrush design are
  added.
- **Option C** decouples logic from motor transients well if USB and battery
  remain separate, but introduces battery hot-plug / charging-state / low-pack
  conditions as new sequencing states not present in Rev 2.

## Recommendation (not a decision)

**Power Engineer recommendation only**: **Option A — dual-input board with the
existing USB 5V logic input preserved and a new dedicated ~12V-class motor
input added**.

Why this is the strongest recommendation for the human to consider first:

1. It is the **lowest integration-risk** path for a first Rev 3 bench build:
   the logic rail remains exactly the already-understood Rev 2 architecture,
   while the motor rail is added as a separate power domain.
2. It is the **best at fault isolation**: motor startup/stall behavior is less
   likely to disturb MCU/IMU operation than in a single-source shared-input
   architecture.
3. It avoids silently betting Rev 3 success on **USB-PD contract availability**
   or on a battery-management expansion that materially changes the project
   framing.

This is a **recommendation, not an approval or decision**. Per REQ-108 and
`docs/architecture.md` §10, the Chief Engineer (human) must choose the
architecture.

## New part-sourcing needs to route back to Component Engineer after human decision

- **Option A**: source a dedicated motor-power input connector family and any
  associated entry/protection parts required by the approved rail spec.
- **Option B**: source a USB-C PD sink / trigger / policy-controller solution
  and any associated entry/protection parts required by the approved rail spec.
- **Option C**: source a battery connector / battery-protection / charging-path
  solution appropriate to the approved battery architecture.

No specific part number is selected here; that remains Component Engineer's
scope.

## Decision

| Role | Name | Date | Decision |
|---|---|---|---|
| Power Engineer | Power Engineer (AI agent) | 2026-08-31 | Proposed — **Option A recommended; no architecture selected** |
| Hardware Lead | Hardware Lead (this session) | 2026-08-31 | Concur with Option A recommendation — relayed all 3 options to human Chief Engineer at the dedicated Power Architecture HITL gate |
| Chief Engineer (Human) — required, this is an architecture decision (`docs/architecture.md` §10) | Human Chief Engineer (via creator/"General Chat" session) | 2026-08-31 | **Approved — Option A**: keep USB 5V logic-only exactly as Rev 2, add a second dedicated ~12V-class motor input (e.g. barrel jack). Rationale: lowest integration risk, best fault isolation between motor and logic rails (relevant given the IMU's noise sensitivity is already a live design concern), consistent with the already-approved bare-bench-test-rig/no-tight-envelope mounting context — no need for USB-PD negotiation complexity (Option B) or to walk back REQ-101's original USB-only framing with a battery (Option C) when a simple second connector solves it cleanly. Circuit Engineer to implement: existing 3.3V logic rail unchanged; new dedicated motor-power input + ~12V motor rail added as a separate power domain. |

## Handoff & change control

- **Produced by**: Power Engineer, once engaged (see "Who fills this in").
- **Consumed by**: Circuit Engineer (implements the approved architecture
  into the actual schematic), Component Engineer (sources any new part the
  approved architecture requires, e.g. a converter IC for a new rail).
- If the approved architecture changes after Circuit Design has started
  (e.g. a later subsystem addition exceeds the approved headroom), log it in
  `validation/change-log.md` (ECO) and check `validation/
  change-impact-matrix.md`'s Power row before human re-approval — same rule
  as any other non-cosmetic `hardware/**` change
  (`.github/instructions/hardware-design.instructions.md`).
- Governed by `.github/instructions/hardware-design.instructions.md`
  (`hardware/**` scope already covers this file — no separate instructions
  file was created for Power Engineer specifically, since its evidence/ECO
  rules are identical to the rest of `hardware/**`, not a genuinely
  different rule set the way Mechanical's CONFIRMED/ASSUMPTION/ESTIMATE/
  UNKNOWN labeling and CAD-tool-honesty rules were).
