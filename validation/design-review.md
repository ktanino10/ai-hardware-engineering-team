# Design Review — Cycle Report Template

One instance of this report per Hardware Reviewer **or Mechanical Reviewer**
(Phase 1 — `docs/architecture-evolution.md` §31) cycle (initial review or
a re-review after loop-back). Copy this template into a dated entry (or a
new file per cycle, e.g. `validation/design-review-2026-01-01.md`, linked
from here) — do not overwrite a previous cycle's report.

## Review Cycle Metadata

- **Design revision reviewed**: `hardware/schematic/bench-imu-01-design.md`
  (initial/first version — Author: Circuit Engineer (AI agent), Date:
  2026-08-31, Status at handoff: "Design complete, self-checked, pending
  independent Hardware Reviewer pass"), together with its companion
  `hardware/power-budget.md` rollup. This is the first-ever Hardware
  Reviewer cycle for this repository.
- **Reviewer**: Hardware Reviewer — see `.github/agents/hardware-reviewer.agent.md`.
  Independent of the Circuit Engineer role/session that authored the design.
- **Independence statement**: I did not author this design. Every checklist
  item and every one of the Circuit Engineer's 9 self-flagged UNKNOWNs
  (design doc §16) and 5 self-check residual items (§15) was independently
  re-derived this cycle against primary datasheets/reference manuals and
  fresh web research — not accepted on the strength of the Circuit
  Engineer's stated confidence or citation formatting. Primary sources
  fetched and read directly this cycle: ST STM32G031x4/x6/x8 datasheet
  (DS12992 Rev4), ST reference manual RM0454 Rev5 (STM32G0x0 series), TI
  TLV755P datasheet (SBVS320D Rev D), and Bosch BMI270 datasheet
  (BST-BMI270-DS000-08 Rev 1.6) — each read at the specific
  section/table level relevant to the claim being checked, not merely
  skimmed. Several evidence-log citations were found to be inaccurate on
  independent re-verification (see Findings); others were confirmed
  correct or even more conservative than claimed.
- **Scope**: Full design — first review cycle for Bench-IMU-01, so no
  "changed area only" narrowing applies. Covers
  `hardware/schematic/bench-imu-01-design.md` (schematic-equivalent
  artifact) and `hardware/power-budget.md` in full; `bom/component-selection.md`
  and `requirements/requirements.md` were read for context only (component
  choices themselves are out of scope — that gate already passed at
  Checkpoint B; this review covers the circuit implementation built on top
  of those approved parts).
- **Parallel sub-scans run**: None dispatched as separate sub-agent scans
  this cycle — the full 16-item checklist and all 7 user-flagged priority
  items were worked as a single integrated pass by this Hardware Reviewer,
  consistent with the agent instruction that the verdict is a single
  serial integration step owned by the Hardware Reviewer, not something to
  fragment across uncoordinated parallel opinions. Investigation was
  organized topically (power/thermal margins, boot/pin-bonding,
  interface/timing, protection/EMI) within that single pass.
- **rubber-duck premise review run in parallel?**: Y — per
  `docs/architecture.md` §5.1, a `rubber-duck` premise/assumption review is
  understood to be running in parallel this same cycle as an independent
  review lens. This report does not duplicate or pre-empt its findings;
  any `rubber-duck`-sourced rows in `validation/open-issues.md` are a
  separate, independently-tagged contribution and were not read or relied
  upon while forming this report's own conclusions.
- **KiCad tool cross-checks used**: None — no KiCad project exists yet for
  this repository this cycle (`kicad-list_projects` returns empty, per the
  design document's own §0 tooling-honesty statement, independently
  confirmed true for this review as well). `extract_schematic_netlist`,
  `analyze_schematic_connections`, `identify_circuit_patterns`, and
  `run_drc_check` were therefore not available to cross-check against; the
  Markdown schematic-equivalent document was reviewed net-by-net and
  pin-by-pin directly instead, which is the correct artifact type for this
  cycle, not a gap to penalize.

## Checklist Results

Full checklist per `.github/skills/hardware-review/SKILL.md`:

| # | Checklist item | Result | Notes |
|---|---|---|---|
| 1 | Voltage violation | Finding | ISS-002 — LDO Vin ROC top-end margin is effectively zero once the real-world USB-C vSafe5V ceiling (4.75–5.5V) is used instead of REQ-101's stated 4.75–5.25V legacy-USB figure. All other rails (single 3.3V logic rail) independently confirmed well within ROC. |
| 2 | Absolute Maximum Rating violation | Finding (documentation-only; no live violation) | No AMR is actually exceeded anywhere in the design as built. ISS-007 (BMI270 VDD/VDDIO AMR citation says 3.6V, primary datasheet says 4V — correction is in the *safe* direction) and ISS-010 (MCU VDD AMR evidence-log entry still stale) are citation-accuracy items only. |
| 3 | Current limit | Finding | ISS-005 — no onboard overcurrent protection upstream of the LDO; downstream (3V3 rail: MCU+IMU) is implicitly protected by the LDO's own internal current limit (560/720/865mA min/typ/max), a mitigating factor the design docs did not credit. Current headroom otherwise is very large (≈94.6% vs REQ-103, ≈96.8% vs the LDO's 500mA rating). |
| 4 | Thermal risk | Finding | ISS-003 — LDO thermal margin claim (`bom/component-selection.md`, reused in `hardware/power-budget.md`) uses the wrong package's θJA. The design's actual real operating point remains thermally safe regardless. |
| 5 | Missing decoupling capacitor | Pass | MCU (C3/C4), IMU (C6/C7), and LDO input/output (C1/C2) decoupling independently verified against each part's own primary-datasheet recommendation — all correct, no deviation found. |
| 6 | Floating pin | Finding | ISS-001 — LDO (U3) EN pin connection is left ambiguous/unconfirmed in the current document; independently confirmed the pin is mandatorily present (pin 3 on the ordered DBV package) with no internal bias. BMI270 unused pins (INT1/INT2/ASDx/ASCx/OCSB/OSDO) independently confirmed correct/datasheet-sanctioned — no finding on those. |
| 7 | Incorrect pull-up/pull-down | Finding (LOW/tracked) | ISS-008 — I2C pull-up (R3/R4=4.7kΩ) math and formula independently reproduced exactly; nominal margin is healthy but sensitive to actual (not-yet-known) bus capacitance. USB-C CC1/CC2 pull-downs (5.1kΩ, DS-CONN-001) and NRST internal pull-up independently confirmed correct. |
| 8 | Logic voltage mismatch | Pass | Single 3.3V rail throughout (MCU + IMU + I2C bus), no level-shifting required; independently confirmed compatible with both parts' Recommended Operating Conditions. |
| 9 | Interface timing | Pass (residual tracked under ISS-008) | I2C 400kHz target achievable with margin at the design's assumed 50pF bus capacitance; both MCU and IMU independently confirmed Fast-mode Plus capable, exceeding the target speed. |
| 10 | Power sequencing | Pass | Single-rail, simultaneous power-up (VDD=VDDIO tied on the IMU; VDD=VDDA=VBAT tied on the MCU) independently confirmed to make any sequencing requirement moot by construction — no relative timing exists between supplies that are electrically the same node. |
| 11 | Grounding | Pass | Single ground net/plane, stated explicitly and appropriate for this design's component count/complexity. |
| 12 | EMI/EMC risk | Pass | REQ-401 explicitly waives formal EMC/EMI certification for this prototype iteration; the basic mitigations taken (ESD protection IC, single ground plane, linear — not switching — LDO topology) are proportionate to that scope. |
| 13 | Motor noise | N/A | No motor or rotating actuator exists on this board — independently confirmed correct from the design's own scope (IMU sensor + MCU + USB interface only, per `docs/architecture.md` §12 co-design trigger, which does not apply here). |
| 14 | Sensor noise | Finding (LOW) | ISS-009 — LDO output capacitor (0.47µF) is below the 1µF value used throughout TI's own PSRR/output-noise typical-characteristic curves; not a datasheet violation, but a margin/characterization-coverage note given the IMU is a noise-sensitive MEMS gyroscope. |
| 15 | PCB layout concern (incl. mechanical/thermal co-design) | N/A (determination independently confirmed correct) | No rotating body exists on this board, so the mechanical/thermal co-design trigger in `docs/architecture.md` §12 does not apply — independently confirmed, not merely accepted. No physical PCB layout exists yet this cycle (no KiCad project), so trace-level layout review is not yet applicable; the qualitative layout guidance already present in the design document (short decoupling/I2C trace runs, solid ground pour) is appropriate for this design stage. |
| 16 | Datasheet recommendation violation | Finding | ISS-004 (REQ-402 reverse-polarity satisfied by USB-C mechanical keying alone, no discrete component) and ISS-006 (DS-MCU-046 BOOT0/PB8 pin-bonding citation is factually incorrect, though the design's ultimate engineering conclusion survives via a different, correct mechanism). |

## Findings

### ISS-001 — LDO (U3) EN pin connection left ambiguous; independently confirmed mandatory and unbiased

- **Issue**: The design document does not establish a firm, confirmed
  connection for U3's (TLV75533PDBVR) EN pin. §3.4 states the pin is "tied
  to enable-always... if the exact TLV75533 package variant used here has
  an active EN pin requiring a level, tie it to VIN directly," explicitly
  deferring final confirmation to layout time (§16 UNKNOWN #9), and
  assesses the residual risk as "low."
- **Rationale**: I independently fetched TI's primary TLV755P datasheet
  (SBVS320D Rev D), §4 "Pin Configuration and Functions," Table 4-1. EN is
  listed as a mandatory pin on **all four** package variants (DQN pin 3,
  DBV pin 3, DYD pin 3, DRV pin 4) — there is no "fixed-output, no-EN"
  variant of this part family. The ordered part is TLV75533PDBVR (package
  code "DBV"), so EN is definitively pin 3. §6.4 "Device Functional Modes"
  (Table 6-1) and §6.4.3 "Disabled" confirm the device is placed into
  shutdown whenever EN is driven below V_LO (0.3V max). The Electrical
  Characteristics table (§5.5) shows EN is a genuine high-impedance input
  (I_EN = 10nA leakage at EN=5.5V) with **no internal pull-up or
  pull-down bias on the pin itself** — the datasheet's only internal
  "pulldown resistance" spec (120Ω) is the *output* discharge switch
  engaged when disabled per §6.4.3, not an EN-pin bias. The Circuit
  Engineer's own uncertainty about whether the pin "is present" was
  therefore resolved in the wrong direction: the pin is always present and
  always electrically live, contrary to the hedge that treated it as
  possibly unnecessary to connect.
- **Datasheet Source**: DS-PWR-002/003 (TLV75533PDBVR electrical/AMR
  reference) — independently re-verified this cycle directly against TI
  SBVS320D Rev D §4 (Table 4-1 Pin Functions), §5.5 (Electrical
  Characteristics: V_HI/V_LO/I_EN/R_PULLDOWN), and §6.4 (Device Functional
  Modes). No existing Evidence ID in the log specifically covers the
  EN-pin pinout/bias question; recommend registering a new DS-PWR entry
  for it.
- **Failure Mechanism**: If EN is left unconnected (floating) on the
  actual physical board, its voltage is fully undetermined (no internal
  bias, high-impedance input) and will be set only by parasitic coupling,
  leakage paths, or static charge on the PCB. Depending on where it
  settles, the regulator may (a) never exceed V_HI (1V min) and thus never
  enable — the entire 3V3 rail stays at 0V, so the MCU and IMU never
  receive power (total board non-function, easily misdiagnosed as a
  dead/DOA board during bring-up), or (b) sit in the undefined 0.3–1.0V
  gray zone or drift with digital-switching noise coupled from adjacent
  traces, causing intermittent/erratic enable-disable transitions,
  spurious resets, or brownouts on the 3V3 rail.
- **Affected Component**: U3 (TLV75533PDBVR LDO regulator), pin 3 (EN).
- **Recommended Fix**: Make EN→VIN (U3 pin 3 to U3 pin 1) an explicit,
  firm, unconditional net in the design document / next schematic
  revision — remove the "if present" hedge entirely, since independent
  verification confirms the pin is always present on the ordered DBV
  package. This is a zero-cost fix (a single trace/via, already
  anticipated by the Circuit Engineer's own stated fallback) — implement
  it as documented intent, not as a layout-time judgment call.
- **Severity**: HIGH — the connection's *absence* would be a total-board
  power failure or a real reliability hazard, and the current
  documentation does not yet firmly commit to making it, despite the
  Circuit Engineer's correct instinct about what the fix should be.

### ISS-002 — LDO Vin ROC top-end margin against the real-world USB-C vSafe5V ceiling is effectively zero

- **Issue**: The design's own margin analysis (§3.4) computes ~0.25V of
  headroom between the top of REQ-101's stated USB tolerance band (5.25V)
  and the LDO's 5.5V Recommended Operating Condition ceiling. Independent
  research shows the real-world input range a USB-C-connectored board can
  see, per the governing USB-PD/Type-C specification's vSafe5V definition,
  is 4.75–5.5V — wider than REQ-101's stated 4.75–5.25V "standard USB
  VBUS range." At the wider, spec-permitted ceiling, margin against the
  LDO's own 5.5V ROC max is zero, not 0.25V.
- **Rationale**: REQ-101 is accurate for legacy USB 2.0-era VBUS tolerance,
  and the Circuit Engineer's arithmetic against REQ-101's own stated
  figure (0.25V) is correct — this is not an arithmetic error. However,
  J1 is a USB-C receptacle, and independent web research (search-engine
  synthesis citing USB-PD specification Table 7.4.3, corroborated by
  independent discussion threads on Electrical Engineering Stack Exchange
  and the Raspberry Pi forums addressing this exact
  vSafe5V-vs-legacy-tolerance question) converges on 4.75–5.5V as the
  actual permitted vSafe5V range for a USB-C/USB-PD source — a real
  possibility for whatever source a bench-use board (REQ-201) is plugged
  into over its life, not a hypothetical corner case. REQ-101 itself may
  not reflect the true governing spec for the connector actually chosen
  for this design.
- **Datasheet Source**: DS-PWR-002/003 (TLV75533PDBVR Vin ROC 1.45–5.5V,
  AMR −0.3 to 6.0V) — independently re-verified this cycle directly
  against TI SBVS320D Rev D §5.1/§5.3; citation confirmed accurate. The
  USB-C vSafe5V figure itself is not yet a formal Evidence ID in the
  log — this review's confirmation rests on corroborating secondary
  sources, not yet a direct primary-source fetch of the USB-PD
  specification text itself; recommend a follow-up primary-source citation
  be added.
- **Failure Mechanism**: Operating above the ROC ceiling but below the AMR
  ceiling does not damage the part outright (AMR is 6.0V, so a fully
  spec-compliant 5.5V source stays 0.5V under AMR), but per TI's own
  Absolute Maximum Ratings footnote: "If used outside the Recommended
  Operating Conditions but within the Absolute Maximum Ratings, the device
  may not be fully functional, and this may affect device reliability,
  functionality, performance, and shorten the device lifetime." A
  marginal, boundary-condition, or non-ideal USB-C source (a cheap
  charger, a bench PSU emulating VBUS, or a source over-regulating under
  light load) reaching close to 5.5V would leave the LDO with no buffer at
  all against its own ROC ceiling.
- **Affected Component**: U3 (TLV75533PDBVR LDO regulator), IN pin;
  indirectly, REQ-101 (input tolerance assumption).
- **Recommended Fix**: Either (a) explicitly scope REQ-101 to only the
  sources the project actually intends to support (e.g., legacy/non-PD 5V
  USB adapters capped at 5.25V, if acceptable — a decision for the
  Hardware Lead / human Chief Engineer, not the Circuit Engineer or this
  reviewer to make unilaterally), or (b) add real margin at the circuit
  level regardless of REQ-101's wording, since a bench tool (REQ-201) is
  realistically likely to encounter varied USB-C sources over its life.
- **Severity**: HIGH — realistic likelihood of encountering a
  spec-compliant corner-case source at or near the ROC ceiling over the
  product's bench-use lifetime, with zero margin at that corner (though
  not an AMR/damage violation).

### ISS-003 — LDO thermal margin claim uses the wrong package's θJA (propagates into power-budget.md)

- **Issue**: `bom/component-selection.md` (LDO recommendation section) and
  `hardware/power-budget.md` (Thermal cross-check section) both state the
  LDO's thermal resistance as θJA = 60.3°C/W and compute TJ ≈ 71°C (≈79°C
  headroom to the 150°C absolute maximum) at a 300mA validation scenario,
  40°C ambient. This θJA figure is for the wrong package.
- **Rationale**: I independently fetched TI's primary TLV755P datasheet
  (SBVS320D Rev D) §5.4 "Thermal Information," which lists θJA separately
  per package: DYD (SOT-23-5, exposed pad) EVM = 60.3°C/W; DBV (SOT-23-5,
  no exposed pad) EVM = 100.8°C/W; DBV JEDEC (standard PCB, no copper
  pour — the condition both documents' own text already claims to be
  using) = 231.1°C/W. The actual ordered part is TLV75533PDBVR — package
  code "DBV," not "DYD." The datasheet's own footnote states the EVM
  condition specifically refers to "the LP087A EVM with an exposed pad
  SOT-23-5 (DYD) layout," which does not describe the DBV package used
  here at all. Recomputing with the correct DBV/JEDEC value:
  TJ = 40°C + (0.51W × 231.1°C/W) ≈ 158°C, which **exceeds the 150°C
  absolute maximum junction temperature** at the documents' own chosen
  300mA validation scenario — the opposite of the "≈79°C headroom" the
  documents claim.
- **Datasheet Source**: DS-PWR-006 (θJA citation) / DS-PWR-008 (derived
  thermal margin) — independently re-verified this cycle directly against
  TI SBVS320D Rev D §5.4 (Thermal Information table), which shows the
  citation error plainly (wrong package column selected).
- **Failure Mechanism**: This does not endanger the design's actual,
  current real-world operating point — at the design's real worst-case
  load (≈16.2mA per `hardware/power-budget.md`'s own Subsystem Load table,
  roughly 30× lower than the 300mA validation scenario), power dissipation
  is negligible and TJ remains safely under 50°C even using the corrected,
  higher θJA. The risk is latent: this project's own roadmap
  (`docs/architecture.md` §11) anticipates future extensions (e.g., a
  motor driver) that could push the shared 3V3 rail load toward the
  reserved REQ-103 300mA ceiling — exactly the scenario the erroneous
  calculation falsely certifies as safe with ≈79°C of headroom, when the
  corrected math shows the part would actually exceed its absolute maximum
  junction temperature under that same load.
- **Affected Component**: U3 (TLV75533PDBVR LDO regulator); documentation
  in `bom/component-selection.md` and `hardware/power-budget.md`.
- **Recommended Fix**: Correct both documents' θJA citation to the
  DBV/JEDEC value (231.1°C/W, or the DBV/EVM value of 100.8°C/W if a
  specific PCB copper-pour/layout matching the EVM condition is later
  confirmed at layout time) and recompute the thermal margin at both the
  300mA validation scenario and the design's real ≈16.2mA worst-case
  load, documenting both explicitly so future load growth against REQ-103
  is evaluated against accurate thermal headroom, not the current
  erroneous figure.
- **Severity**: MEDIUM — does not endanger the current design's real
  operating point (which remains thermally safe by a wide margin even
  after correction), but the documented calculation is factually wrong and
  would mislead any future power-budget growth decision toward a false
  sense of thermal safety.

### ISS-004 — REQ-402 "reverse-polarity protection" satisfied only via USB-C mechanical keying, no discrete component

- **Issue**: REQ-402 ("Must" priority) requires "basic transient/ESD and
  reverse-polarity protection appropriate for a hand-handled connector."
  The design satisfies the ESD/transient half via U4 (USBLC6-2SC6), but
  for reverse-polarity, relies entirely on the USB-C connector's
  mechanical keying (§3.3), with no discrete protection component (e.g., a
  series Schottky diode or ideal-diode PFET).
- **Rationale**: Independent web research confirms a well-documented
  industry consensus: USB-C's mechanical keying prevents a user from
  inserting a cable backwards, but does not protect against a miswired,
  damaged, or off-brand/out-of-spec cable or adapter that delivers
  VBUS/GND on swapped or unexpected contacts — a real, if infrequent,
  documented failure mode independent of connector orientation. Whether
  keying alone is "enough" is legitimately context-dependent: many
  low-cost consumer products with tightly-controlled cable ecosystems skip
  discrete protection, while field-use, bench, or high-reliability
  products commonly add cheap protection given uncontrolled cabling. This
  board's own REQ-201 (bench-use context) suggests it will realistically
  encounter a more diverse, less-controlled set of cables and power
  sources over its life than a typical consumer product.
- **Datasheet Source**: DS-CONN-001 (USB-C mechanical/CC pull-down
  reference, independently re-verified accurate this cycle) — the
  "keying prevents reversal but not miswiring" claim itself is a general
  USB-C construction fact independently corroborated via web research this
  cycle (multiple sources), not a single canonical datasheet citation.
- **Failure Mechanism**: A miswired, damaged, or non-compliant
  cable/adapter that presents reverse polarity (or a shorted/swapped
  VBUS-GND condition) at J1 would apply a negative or otherwise
  out-of-spec voltage directly to U3's IN pin and the rest of the
  downstream circuit, with no discrete component to block or clamp it —
  U4's ESD channel (VBUS-to-GND) offers some transient/overvoltage
  clamping but is not designed as a reverse-polarity blocking element.
- **Affected Component**: J1 (USB-C connector); downstream U3 (LDO) IN pin
  and U4 (ESD protection IC).
- **Recommended Fix**: Add a low-cost reverse-polarity mitigation
  appropriate for the bench-use context — e.g., a small Schottky diode in
  series with VBUS (accepting the small forward-voltage drop) or a
  PFET-based ideal-diode circuit (lower drop, slightly higher
  cost/complexity) — sized against the board's real ≈16.2mA worst-case
  current draw, which keeps the cost/complexity of either option minimal.
- **Severity**: MEDIUM — real, documented risk given the bench-use context
  and diverse cabling, but does not affect the normal/compliant-cable case
  (the overwhelming majority of real-world use), and is inexpensive to
  close.

### ISS-005 — No onboard overcurrent protection upstream of the LDO

- **Issue**: The design adds no resettable fuse/PTC or other
  overcurrent-limiting element on VBUS upstream of U3, reasoning that USB
  hosts/hubs already provide upstream overcurrent protection per the USB
  spec (§14 item 9, §16 item 7).
- **Rationale**: This reasoning is correct for a USB-IF-compliant host or
  hub, which is indeed required by spec to implement port-level
  overcurrent protection. However, the assumption that the power source
  will always be such a compliant host/hub may not hold for a bench-use
  board (REQ-201) that could plausibly be powered from a bench power
  supply, a non-compliant/generic USB charger, or another source that
  emulates VBUS without host-side OCP — a realistic scenario for lab/bench
  equipment. Separately, and as a mitigating factor the design documents
  did not credit: U3's own datasheet specifies an internal current limit
  (ICL = 560/720/865mA min/typ/max), which does provide automatic,
  host-independent protection for everything downstream of the LDO (the
  3V3 rail feeding the MCU and IMU) regardless of the upstream source's
  behavior.
- **Datasheet Source**: DS-PWR-002/003 (TLV75533PDBVR electrical
  characteristics, ICL) — independently re-verified this cycle directly
  against TI SBVS320D Rev D §5.5 Electrical Characteristics.
- **Failure Mechanism**: If powered from a source without host-side OCP
  and a downstream short or fault occurs between J1 and U3's IN pin (i.e.,
  upstream of the LDO's own current limit), current is limited only by the
  source's own output impedance/current capability and the PCB
  trace/connector's physical current-carrying capacity — in the worst
  case, this could lead to excessive heating of the cable, connector, or
  trace, or damage to the source itself, with no onboard element to
  interrupt it.
- **Affected Component**: J1 (USB-C connector) to U3 (LDO) IN pin span; no
  discrete protection component populated in this span.
- **Recommended Fix**: Add a small resettable PTC fuse (or explicitly and
  permanently note, as an accepted-risk decision signed off by the human
  Chief Engineer, that the board is only rated for use with
  USB-IF-compliant sources) — low cost, minimal footprint impact given the
  board's low overall current draw.
- **Severity**: MEDIUM — real gap for a subset of realistic bench-use power
  sources, but downstream (the majority of the circuit) is already
  implicitly protected by the LDO's own current limit, narrowing the
  residual exposure to the upstream span only.

### ISS-006 — DS-MCU-046 (BOOT0/PB8 pin-bonding) citation is factually incorrect

- **Issue**: DS-MCU-046 is cited as showing no PB8 pin exists in the
  STM32G031K8T6's LQFP-32 pin list, used to support the design's
  conclusion that BOOT0/PB8 is a moot question and the design must rely
  entirely on the nBOOT_SEL option byte (DS-MCU-044). Independent
  verification shows PB8 does exist on this exact package.
- **Rationale**: I directly fetched the primary ST datasheet (DS12992
  Rev4, STM32G031x4/x6/x8) pin-assignment table and confirmed PB8 (along
  with PB6/PB7) is present in the LQFP-32 pin list, contradicting
  DS-MCU-046 as cited. However, this does not change the design's
  bottom-line conclusion: ST's reference manual RM0454 (STM32G0x0 series)
  Table 7 "Boot modes" and the FLASH_OPTR register description (§3.7.8)
  show that for this specific STM32G0x0 sub-family, the BOOT0 function is
  multiplexed onto pin **PA14** — not PB8 — and PA14 is already committed
  as SWCLK in this design's SWD debug header. This means no dedicated
  physical BOOT0 circuit is available regardless of whether PB8 physically
  exists, and the design's reliance on the nBOOT_SEL option byte
  (independently corroborated via RM0454's option-byte description plus a
  converging community factory-default option-byte dump for a sibling
  STM32G071 part) remains the correct, and only, practical mechanism — so
  the design's ultimate engineering conclusion (no physical BOOT0
  populated, rely on nBOOT_SEL) is right, even though it was reached via
  an incorrect premise (PB8 not existing) rather than the actually-correct
  one (BOOT0 is muxed to PA14, which is otherwise committed). Separately,
  DS-MCU-045's generic "PB8 = BOOT0" STM32-family guidance is true for
  many STM32 families but does not apply to this specific G0x0 sub-family
  without qualification, and should be annotated as such. I also
  independently confirmed (via RM0454 plus general Cortex-M SWD
  debug-port architecture, which operates independently of application
  boot-mode state) that this does **not** create a brick risk: SWD-based
  recovery/reprogramming remains available regardless of the nBOOT_SEL
  option byte's actual state, since SWD's debug-port-level access is
  designed to remain available even if the application CPU's boot sequence
  is in an unexpected state.
- **Datasheet Source**: DS-MCU-046 (citation error, corrected this cycle);
  DS-MCU-044/045/049 (nBOOT_SEL / generic PB8 guidance / bonding status) —
  independently re-verified directly against ST DS12992 Rev4 pin table and
  RM0454 Rev5 §3.7.8/Table 7 this cycle (primary sources, not distributor
  mirrors).
- **Failure Mechanism**: None for the current design (the correct
  mechanism is used regardless of the citation error) — this is a
  documentation-accuracy defect, not a live circuit defect. The residual,
  genuinely open risk is that nBOOT_SEL's factory-default value was only
  corroborated via a sibling part's community-sourced option-byte dump,
  not the exact STM32G031K8T6 part's primary reference documentation — a
  first-article bring-up check would close this definitively.
- **Affected Component**: U1 (STM32G031K8T6 MCU), BOOT0/PA14 boot-mode
  configuration; `datasheets/evidence-log.md` DS-MCU-046 entry.
- **Recommended Fix**: Correct the DS-MCU-046 evidence-log entry to
  reflect that PB8 does exist on this package, and add a note clarifying
  that BOOT0 is muxed to PA14 (not PB8) for the G0x0 sub-family, with PA14
  already committed to SWCLK. At first-article bring-up, explicitly read
  back the FLASH_OPTR register via SWD to confirm the actual nBOOT_SEL
  value before relying on the assumed factory default for any production
  run.
- **Severity**: MEDIUM — real citation/evidence-trail error worth
  correcting, and the underlying nBOOT_SEL assumption still carries
  residual (non-brick-risk) verification debt, but the design's actual
  engineering conclusion and recoverability are sound.

### ISS-007 — DS-IMU-004/006 (BMI270 VDD/VDDIO Absolute Maximum Rating) citation understates the actual ceiling

- **Issue**: DS-IMU-004/DS-IMU-006 cite the BMI270's VDD and VDDIO
  Absolute Maximum Rating ceiling as 3.6V (the same as the Recommended
  Operating Condition ceiling, with VDDIO described as sharing VDD's
  ceiling rather than having its own explicit rating).
- **Rationale**: I directly fetched the primary Bosch BMI270 datasheet
  (BST-BMI270-DS000-08 Rev 1.6), Chapter 2 "Absolute maximum ratings,"
  Table 5, which states: Voltage at Supply Pin, VDD Pin: −0.3 to 4V; VDDIO
  Pin: −0.3 to 4V (a separate, explicitly-listed row, not "shared with
  VDD's 3.6V" as the citation states). The true AMR ceiling for both VDD
  and VDDIO is 4V, one volt higher than the 3.6V previously cited.
- **Datasheet Source**: DS-IMU-004/DS-IMU-006 (citation error, corrected
  this cycle) — independently re-verified directly against Bosch
  BST-BMI270-DS000-08 Rev 1.6, Chapter 2, Table 5 "Absolute maximum
  ratings" (primary source, direct PDF fetch, superseding the evidence
  log's own "bosch-sensortec.com + alldatasheet.com mirror" sourcing
  note).
- **Failure Mechanism**: None — this is a documentation-accuracy issue
  only, and the corrected direction is benign: since the design's actual
  VDD/VDDIO operating point is the shared 3.3V rail, the corrected 4V
  ceiling gives *more* margin (0.7V) than the previously-cited 3.6V figure
  implied (0.3V), not less. There is no scenario in which this citation
  error creates hidden risk for the current design.
- **Affected Component**: U2 (BMI270 IMU), VDD/VDDIO pins;
  `datasheets/evidence-log.md` DS-IMU-004/DS-IMU-006 entries.
- **Recommended Fix**: Correct the evidence-log entries to cite VDD/VDDIO
  AMR as −0.3 to 4V (separate, explicit rows per the primary datasheet),
  and re-source both to the primary Bosch PDF directly rather than the
  aggregator-mirror sourcing currently noted.
- **Severity**: LOW — documentation-accuracy correction only; the actual
  design's margin is better than previously believed, not worse.

### ISS-008 — I2C pull-up sizing: healthy nominal margin, but sensitive to actual bus capacitance not yet known this cycle

- **Issue**: R3/R4 (4.7kΩ I2C pull-ups) are sized against an assumed bus
  capacitance (Cb) of 50pF for a 300ns Fast-mode rise-time budget at
  400kHz, leaving the design compliant only up to ≈75pF of actual Cb — no
  PCB layout exists yet this cycle to confirm the real value.
- **Rationale**: I independently reproduced all four of the design's own
  cited figures exactly (Rp,min ≈ 966Ω; Rp,max ≈ 7.08kΩ at Cb=50pF; tr ≈
  199ns at R=4.7kΩ/Cb=50pF; tr ≈ 299ns at R=4.7kΩ/Cb=75pF), and
  independently confirmed the rise-time formula used
  (tr = 0.8473 × Rp × Cb, per NXP UM10204's 30%–70%-VCC rise-time
  convention) is a legitimate, correctly-applied industry-standard
  formula. The nominal-case margin (34% headroom at the design's own 50pF
  planning assumption) is healthy, and the design's own documented
  fallback (drop to 3.3kΩ/2.2kΩ if the real Cb proves higher) is good
  practice. This is not a design error, but a legitimate residual
  verification item given the real Cb is layout-dependent and not yet
  measurable this cycle.
- **Datasheet Source**: DS-IFACE-001 (I2C rise-time/pull-up sizing
  reference, NXP UM10204) — independently re-verified this cycle via web
  research confirming the formula's derivation and standard use.
- **Failure Mechanism**: If actual PCB trace length and component loading
  push real Cb meaningfully above ≈75pF (e.g., long traces, many stubs, or
  higher-than-assumed pin capacitance), rise time would exceed the
  Fast-mode 300ns budget, degrading I2C signal integrity and potentially
  causing intermittent communication errors between U1 (MCU) and U2 (IMU)
  at the target 400kHz rate.
- **Affected Component**: R3, R4 (I2C pull-up resistors); SCL/SDA bus
  between U1 and U2.
- **Recommended Fix**: Confirm actual bus capacitance once PCB layout
  exists (trace length + component pin capacitance), and apply the
  design's own documented fallback (3.3kΩ or 2.2kΩ) if the
  measured/estimated Cb exceeds ≈75pF. Track as a layout-stage checklist
  item, not a pre-layout blocker.
- **Severity**: LOW — sound math and formula, healthy nominal margin,
  genuinely dependent on a not-yet-available layout parameter;
  appropriately a tracked follow-up rather than a current defect.

### ISS-009 — LDO output capacitor value is below TI's own PSRR/noise characterization condition

- **Issue**: C2 (LDO output capacitor) is set to 0.47µF, matching TI's
  stated minimum-for-stability value, but TI's own published PSRR and
  output-noise typical-characteristic curves (Figures 5-1 through 5-6 of
  SBVS320D Rev D) are all characterized at COUT = 1µF, not 0.47µF.
- **Rationale**: I directly fetched TI's primary TLV755P datasheet §7.1.1
  "Input and Output Capacitor Selection" and confirmed the design's
  C1=1µF/C2=0.47µF values exactly match TI's own stated minimums
  ("requires an output capacitance of 0.47μF or larger for stability,"
  "place a 1μF or greater capacitor on the input pin") — this is not a
  datasheet violation. However, §5.6 "Typical Characteristics"
  independently confirms all PSRR/noise curves use COUT=1µF as their test
  condition. Actual PSRR and output noise at COUT=0.47µF are not
  separately characterized in the datasheet and may be modestly worse at
  higher frequencies than the published typical curves suggest (PSRR
  generally degrades with lower output capacitance in linear regulators).
  This matters specifically because U2 is a noise-sensitive MEMS
  gyroscope, where supply-rail noise can couple into the measurement noise
  floor.
- **Datasheet Source**: DS-PWR-002/003 (LDO datasheet reference) —
  independently re-verified this cycle directly against TI SBVS320D Rev D
  §7.1.1 and §5.6.
- **Failure Mechanism**: None currently demonstrated — this is a
  margin/characterization-coverage note, not a datasheet violation or
  known functional defect. Worst case, if actual PSRR at C2=0.47µF is
  meaningfully worse than the datasheet's 1µF-characterized curves at
  frequencies relevant to the IMU's gyroscope noise floor, measured sensor
  noise could be modestly higher than an engineer might expect from
  reading the datasheet's typical curves alone.
- **Affected Component**: C2 (LDO output capacitor); U2 (BMI270 IMU)
  supply noise sensitivity.
- **Recommended Fix**: Consider increasing C2 to 1µF (matching TI's own
  characterization condition) at negligible cost/board-area impact, or
  explicitly bench-verify IMU output noise at C2=0.47µF once hardware
  exists, to confirm the noise floor meets the application's actual
  requirements.
- **Severity**: LOW — non-violating, precautionary margin note; no
  confirmed functional defect.

### ISS-010 — evidence-log.md DS-MCU-012 entry is stale relative to already-available primary-source data

- **Issue**: The `datasheets/evidence-log.md` entry for DS-MCU-012
  (STM32G031K8T6 VDD Absolute Maximum Rating) still states the lower bound
  is "UNKNOWN — not independently re-confirmed this session," carried
  forward from the BOM/Component Engineer phase.
- **Rationale**: I independently confirmed via the primary ST datasheet
  (DS12992 Rev4), Table 18 (Absolute Maximum Ratings), that VDD AMR is Min
  −0.3V / Max 4.0V — resolving this UNKNOWN cleanly. This is consistent
  with the design document's own §16 UNKNOWN #2, which also still carries
  this forward as open. The evidence log itself has not yet been updated
  to reflect this now-available resolution.
- **Datasheet Source**: DS-MCU-012/013 — independently re-verified this
  cycle directly against ST DS12992 Rev4, Table 18.
- **Failure Mechanism**: None — pure documentation-currency issue;
  practical risk was already assessed as low by the design document itself
  (3.3V sits well within the confirmed ROC).
- **Affected Component**: `datasheets/evidence-log.md` DS-MCU-012 entry;
  §16 UNKNOWN #2 in the design document.
- **Recommended Fix**: Update the DS-MCU-012 evidence-log entry to record
  VDD AMR Min −0.3V / Max 4.0V (per ST DS12992 Rev4 Table 18), closing
  this UNKNOWN, and mark design-document §16 UNKNOWN #2 as resolved.
- **Severity**: LOW — administrative/documentation-currency correction, no
  functional risk.

## Verdict

- **Verdict**: CONDITIONAL
- **Open CRITICAL count**: 0
- **Open HIGH count**: 3 (ISS-001, ISS-002, ISS-011 — see addendum below)
- **Next action**: Loop back to the Circuit Engineer (routing decision for
  the Hardware Lead to make) for ISS-001 (firm, unconditional LDO EN→VIN
  connection) and ISS-002 (LDO Vin ROC margin vs. the real-world USB-C
  vSafe5V ceiling) at minimum — both HIGH findings should be resolved
  before this design proceeds toward physical layout/fabrication. The four
  MEDIUM findings (ISS-003 through ISS-006) should also be addressed or
  explicitly dispositioned (`RESOLVED` / `DEFERRED` / `ACCEPTED-RISK` with
  Chief Engineer sign-off) before Design Complete per
  `docs/architecture.md` §8. The four LOW findings (ISS-007 through
  ISS-010) are documentation/tracked-item corrections that do not block
  progress but should be closed out for evidence-trail hygiene.

## Addendum — Hardware Lead conflict mediation (2026-08-31, post-verdict)

A parallel `rubber-duck` premise-review pass (run concurrently with this
Hardware Reviewer pass, per `docs/architecture.md` §5.1) surfaced a genuine
factual disagreement with this review's ISS-003 and ISS-006 findings, plus
one new finding (the I2C1-vs-I2C2 pin mapping) that this Hardware Reviewer
pass's own checklist did not independently catch. Per
`docs/workflow.md` §3 (Conflict Resolution / Deadlock Escalation Protocol),
the Hardware Lead independently re-verified the disputed claims via
real-time web research against primary/authoritative sources rather than
deferring to either side, with the following outcomes:

- **ISS-003 (this review's finding) was itself found to be in error** —
  the disputed θJA=231.1°C/W figure is real but belongs to a *different*
  package (DQN/X2SON-4) in the same TI datasheet table, not the DBV/SOT-23-5
  package this part actually orders as. The original 60.3°C/W figure and
  thermal analysis were correct all along. **ISS-003 is now marked
  RESOLVED** with no design change needed — see `validation/open-issues.md`
  for the full correction record. Recorded transparently: this is a case of
  the *reviewer's* finding being wrong, not the design.
- **ISS-006 (this review's finding) is confirmed but was incomplete** — PB8
  does exist on the package (confirmed correct), but the reason a BOOT0
  circuit is unnecessary is that BOOT0 is actually muxed onto **PA14**
  (already committed to SWCLK in this design), not PB8 — a different root
  cause than either this review or the design document originally stated,
  though the practical conclusion (no physical BOOT0 circuit needed) is
  unchanged. Evidence log corrected (DS-MCU-050/051).
- **A genuine new HIGH finding (ISS-011)** was confirmed via independent
  research: pins PB10/PB11 are labeled "I2C1" throughout the design
  document, but the STM32G031K8T6's real alternate-function table maps
  them to **I2C2** (a genuinely separate, real peripheral on this part, not
  a naming variant). This raises this cycle's **open HIGH count from 2 to
  3** (ISS-001, ISS-002, ISS-011). The underlying physical wiring is
  correct and needs no hardware change — this is a firmware-target/
  documentation-labeling defect, classified HIGH (not CRITICAL) because
  the fix is zero-hardware-impact and the failure mode, while total
  (no I2C communication if followed literally), would surface immediately
  at firmware bring-up rather than shipping silently.
- **Revised next action**: loop back to the Circuit Engineer for ISS-001,
  ISS-002, and ISS-011 (all HIGH) before this design proceeds further, per
  the same loop-back rule as the original verdict above. A fresh Hardware
  Reviewer pass is required after the fix, per
  `.github/skills/hardware-review/SKILL.md` ("re-review after a fix means
  re-running the checklist against the changed area and anything the
  change could have affected — not a partial spot-check").

This addendum itself illustrates why running an independent `rubber-duck`
premise pass in parallel with the Hardware Reviewer's checklist pass adds
real value beyond redundant checking — and why the Hardware Lead's
mediation role (independently re-verifying disputed claims rather than
simply picking a side) matters when two independent AI reviews disagree.

## Cycle 2 — Re-review after Rev 2 rework (2026-09-01)

### Review Cycle Metadata

- **Design revision reviewed**: `hardware/schematic/bench-imu-01-design.md`
  **Rev 2** (Author: Circuit Engineer (AI agent), rework commit `73215e4`
  "Circuit rework for Bench-IMU-01: fix 3 HIGH findings (Rev 2)"), which
  claims to fix the three Cycle-1 HIGH findings (ISS-001, ISS-002, ISS-011)
  plus fold in the two Cycle-1 mediation corrections (ISS-006, ISS-010).
  This is a **re-review, not a first review** — the Circuit Engineer's own
  "Rev 2 rework" changelog (top of the design document) and its own
  "Re-self-check after Rev 2 fixes" (§15) were read for orientation only,
  never accepted as a substitute for independent verification.
- **Reviewer**: Hardware Reviewer — see
  `.github/agents/hardware-reviewer.agent.md`. Independent of the Circuit
  Engineer session that performed the Rev 2 rework, and independent of the
  Hardware Lead session that mediated the Cycle 1 conflict.
- **Independence statement**: I did not treat any Rev 2 claim — the Circuit
  Engineer's own "RESOLVED this revision" language, the Hardware Lead's
  DS-MCU-050…053 evidence-log entries, or the Cycle 1 Addendum's mediation
  outcome — as self-certifying. Every one of the 3 HIGH fixes and both
  folded-in corrections was independently re-derived this cycle from
  scratch against primary/authoritative sources, and the full document was
  swept for consistency rather than spot-checked at the 5 named locations
  only, per this skill's re-review rule ("re-running the checklist against
  the changed area and anything the change could have affected — not a
  partial spot-check"). **Methodology disclosure (important honesty note,
  contrast with Cycle 1's stated method)**: direct PDF/HTML fetch of the
  primary datasheets was attempted this cycle (`web_fetch`/`curl` against
  st.com, TI, alldatasheet.com, Mouser, DigiKey, LCSC, manualslib.com) and
  was **blocked or unusable in every case** in this sandboxed environment
  (st.com closes the connection with an HTTP/2 protocol error even with a
  browser-like User-Agent; alldatasheet.com's pin tables are
  rendered-to-image, not extractable text; manualslib.com returns HTTP 403;
  distributor "PDF" links redirect to HTML wrapper pages). I therefore
  relied on the `web_search` tool's source-grounded synthesis as the
  practical independent-verification method available here, and mitigated
  the single-search-hallucination risk by cross-checking every material
  fact (PB10/PB11=I2C2, TLV75533 EN pin/bias, USB-C vSafe5V range, TLV755P
  Vin AMR/ROC, MCU VDD AMR lower bound, BOOT0=PA14, PB8 existence/function)
  with **at least two independent queries**, several of which converged on
  a specific named table/section/errata number (DS12992 Table 13/16,
  RM0454, TI SBVS320D §4/§5.5/§6.4, errata es0487) rather than a generic
  answer. This is a genuine independent re-derivation, not a re-citation of
  the design doc's or evidence-log's own claims — but it is a **weaker
  verification standard than reading the raw primary PDF directly**
  (which Cycle 1 reported doing), and that gap is disclosed here rather
  than papered over.
- **Scope**: Focused re-review of the changed areas (§3.4 EN pin, §3.5 LDO
  Vin margin/ISS-002 disposition, §4.1 VDD/decoupling + ISS-006 note, §4.2
  BOOT0/PA14, §6 UART/I2C cross-reference, §11 pin table, §12 net list,
  §13 parts list, §14 18-item checklist, §15 self-check/re-self-check, §16
  UNKNOWNs items 1–4) plus a full-document consistency sweep (exhaustive
  grep for every "I2C1"/"I2C2" occurrence — 49 total — and every
  EN-pin/hedge-language occurrence — 37 total) to catch any leftover
  inconsistency the targeted section re-reads might miss. `bom/component-selection.md`
  and `requirements/requirements.md` were re-consulted only where Rev 2
  itself cites them (e.g. REQ-101's stated band vs. the real USB-C
  vSafe5V ceiling).
- **Parallel sub-scans run**: None dispatched as separate sub-agent scans
  this cycle — worked as a single integrated pass, consistent with the
  agent instruction that the verdict is a single serial integration step
  owned by the Hardware Reviewer. Investigation was organized around the 3
  HIGH fixes + 2 corrections first, then a full 16-item checklist sweep of
  everything the changes could have affected.
- **rubber-duck premise review run in parallel?**: Not indicated as run for
  this specific Cycle 2 pass (unlike Cycle 1, where one ran concurrently
  and is what originally surfaced ISS-011). No `rubber-duck`-sourced row
  was added to `validation/open-issues.md` this cycle; this report does not
  rely on or duplicate the Cycle 1 rubber-duck findings, which are already
  fully accounted for in the existing ISS-011/ISS-012/ISS-013 rows.
- **KiCad tool cross-checks used**: None — still no KiCad project exists
  for this repository (`kicad-list_projects` not re-run this cycle since
  the design doc's own §0 tooling-honesty statement is unchanged and nothing
  in Rev 2 claims a KiCad artifact now exists); the Markdown
  schematic-equivalent document remains the correct artifact type to review
  net-by-net and pin-by-pin, as in Cycle 1.
- **Process-integrity check (new this cycle)**: Independently ran
  `git log --oneline` and `git show --stat 73215e4` to verify the Rev 2
  rework commit's own claim ("Only this document was modified;
  `validation/open-issues.md`, `validation/design-review.md`, and
  `datasheets/evidence-log.md` are owned by the Hardware Reviewer/Hardware
  Lead and are not touched here"). **Confirmed true**: the commit's file-stat
  summary shows exactly one file changed —
  `hardware/schematic/bench-imu-01-design.md` (593 insertions(+), 153
  deletions(-)) — no unauthorized edit to any validation/ or datasheets/
  file was made by the Circuit Engineer this cycle.

### Checklist Results (re-run against changed areas and anything the changes could have affected)

Full checklist per `.github/skills/hardware-review/SKILL.md`, re-run this
cycle (not a partial spot-check of only the 5 named items):

| # | Checklist item | Result | Notes |
|---|---|---|---|
| 1 | Voltage violation | Finding (unchanged disposition, technical characterization independently reconfirmed sound) | ISS-002 — independently reconfirmed via USB-PD-spec-grounded search (vSafe5V 4.75–5.5V) and TI-datasheet-grounded search (TLV755P ROC 1.45–5.5V) that the LDO's Vin ROC top-end margin is genuinely ~0 at real-world worst-case input; not a new violation, and the §3.5 disposition recommendation is technically sound — still pending human Chief Engineer sign-off (§8), not resolvable by this review. |
| 2 | Absolute Maximum Rating violation | Pass — no live violation found anywhere, independently reconfirmed | MCU VDD AMR lower bound (ISS-010: −0.3V, independently reconfirmed via ST DS12992 Table 18) and LDO Vin AMR (6.0V, independently reconfirmed via TI datasheet) both hold with margin even at ISS-002's real-world worst-case 5.5V input (0.5V/9% headroom remains — a ROC-ceiling thinness, not an AMR exceedance). ISS-010's *evidence-log.md housekeeping* is still incomplete (see Findings below) but this poses zero design risk. |
| 3 | Current limit | Pass — unaffected by rework | Rework touched only §3.4/§3.5/§4.1/§4.2/§6/§11–16 text; no new current-consuming element was added. `hardware/power-budget.md` figures (≈16.2mA worst-case vs. 300–500mA ceilings) are unchanged and re-confirmed still applicable. |
| 4 | Thermal risk | Pass — unaffected by rework | No change to load current or package; ISS-003's Cycle-1 mediation conclusion (θJA=60.3°C/W is correct for the DBV package) is unaffected by this cycle's edits and was not touched again. |
| 5 | Missing decoupling capacitor | Pass — independently confirmed the ISS-001 fix introduces no new requirement | A direct EN-to-VIN tie (the new `EN_VIN` net) is TI's own always-enabled reference configuration and needs no additional bypass/decoupling capacitor beyond the existing C1(in)/C2(out) — independently confirmed via general LDO application-circuit practice. C3/C4/C5/C6/C7 are untouched by the rework. |
| 6 | Floating pin | Pass — **RESOLVED this cycle (ISS-001), independently confirmed** | LDO (U3) EN pin: independently re-derived from TI's TLV755P/SBVS320D datasheet that EN (pin 3, DBV/SOT-23-5, the ordered package) is mandatory with no internal pull-up/pull-down bias — a floating EN is genuinely undefined, confirming the exact failure mechanism the finding described. Full-document grep (37 matches) confirms zero remaining hedge language anywhere (§3.4, §12, §13, §14, §15, §16 all consistent); the net is now a firm, unconditional EN→VIN tie. |
| 7 | Incorrect pull-up/pull-down | Pass — I2C pull-ups and BOOT0 reasoning both independently reconfirmed sound | I2C R3/R4=4.7kΩ pull-ups are physically and electrically identical before/after the ISS-011 relabeling (same pins, same resistors) — independently confirmed the relabeling changed a firmware/peripheral-instance label only, not the resistor network. BOOT0 pull-down omission's *reasoning* is independently confirmed corrected (ISS-006: BOOT0 is muxed on PA14, not PB8) while the underlying no-physical-BOOT0-circuit design decision is unchanged and remains sound (PA14 is already committed to SWCLK). |
| 8 | Logic voltage mismatch | Pass — unaffected by rework | Single 3.3V logic rail throughout; nothing in Rev 2's changes introduces or touches an interface voltage. |
| 9 | Interface timing | Pass — independently confirmed ISS-011 has zero electrical/timing impact | The I2C1→I2C2 relabeling is a pure peripheral-instance/firmware-target correction: identical physical pins (PB10/PB11), identical pull-up resistors (R3/R4=4.7kΩ), identical bus-capacitance/rise-time sensitivity analysis in §5.2. The 400kHz Fast-mode Plus timing budget is completely unaffected — independently verified, not merely assumed, by confirming no numeric or component value in §5.2 changed between Cycle 1 and Rev 2. |
| 10 | Power sequencing | Pass — unaffected by rework | Single-rail simultaneous power-up argument (VDD=VDDIO/VDDA/VBAT tied) is unchanged by this cycle's edits. |
| 11 | Grounding | Pass — unaffected by rework | Single ground net/plane statement unchanged. |
| 12 | EMI/EMC risk | Pass — unaffected by rework | REQ-401's waiver of formal EMC certification for this prototype is unchanged; no new noise source was added by the rework (EN→VIN is a DC tie, not a switching net). |
| 13 | Motor noise | N/A — unaffected | Still no motor/rotating actuator on this board. |
| 14 | Sensor noise | Pass (residual tracked under ISS-009, unchanged, out of scope this cycle) | LDO output cap value (0.47µF vs. TI's 1µF characterization condition) is untouched by this rework; ISS-009 remains OPEN/LOW, intentionally out of scope this cycle per the task. |
| 15 | PCB layout concern (incl. mechanical/thermal co-design) | N/A — unaffected | Still no KiCad project/PCB layout this cycle; still no rotating body (`docs/architecture.md` §12 co-design trigger does not apply). |
| 16 | Datasheet recommendation violation | Pass — **RESOLVED this cycle (ISS-001), ISS-006 reasoning corrected, independently confirmed** | LDO's own recommended application circuit (always-enabled EN→VIN) is now followed exactly — previously the one documented, hedged deviation. MCU's no-physical-BOOT0-circuit remains a deliberate, logged deviation, now justified for the *correct* reason (BOOT0=PA14, not PB8). No new unlogged/silent deviation found anywhere in the rework. |

### Re-verification of Cycle 1 HIGH findings and folded-in corrections

Each of the following was independently re-derived from primary/authoritative
sources this cycle — not accepted on the strength of the design document's,
evidence-log's, or Hardware Lead's own citation.

#### ISS-011 (HIGH) — I2C1→I2C2 relabeling — **independently RE-CONFIRMED, fix holds up**

- **Independent method**: Two separate web searches targeting the
  STM32G031K8T6's real alternate-function table specifically (not the
  design doc's or DS-MCU-052's citation of it), cross-checked against each
  other.
- **Result**: Both searches converge, citing ST's own DS12992 datasheet
  (Table 13/16, Alternate Function tables) and the RM0454 reference manual:
  pins **PB10/PB11 map to I2C2_SCL/I2C2_SDA via AF1**, not I2C1. The
  STM32G031 (unlike the lower-cost STM32G030) genuinely has two separate
  I2C peripheral instances — this is confirmed independently, not merely
  re-cited from DS-MCU-052. No search surfaced a contradicting claim.
- **Document consistency**: Exhaustive full-document grep for every
  occurrence of "I2C1" (28) and "I2C2" (21) — 49 total, none missed. Every
  single "I2C1" occurrence is correctly contextual (explaining the
  historical mislabel, correctly stating "I2C1 is now free," or correctly
  describing PB8's true I2C1_SCL alternate function) across §2.3, §5.2,
  §5.3, §6, §11, §12, §13, §14, §16 — including the §6 UART section, which
  the changelog specifically claimed was also touched, and the pin table
  (§11), net list (§12), and checklist item 13 (§14) the task specifically
  asked about. **No stray leftover "I2C1" label found, and "I2C1 is now
  free" is stated correctly** (true I2C1 lives on PB6/PB7 or PB8/PB9,
  confirmed unused elsewhere in this design).
- **Electrical-impact check**: Independently confirmed this is purely a
  peripheral-instance/firmware-target correction — same physical pins, same
  R3/R4 pull-ups, same §5.2 timing analysis; zero electrical characteristic
  changed (checklist item 9 above).
- **Conclusion**: Fix holds up under independent re-verification.
  `validation/open-issues.md` updated: **ISS-011 → RESOLVED** (2026-09-01).

#### ISS-001 (HIGH) — LDO EN pin — **independently RE-CONFIRMED, fix holds up**

- **Independent method**: Web search grounded specifically in TI's TLV755P
  family datasheet (SBVS320D), targeting the EN pin's mandatory/optional
  status and internal bias specifically on the DBV (SOT-23-5) package (the
  ordered TLV75533PDBVR part), cross-checked with a second query.
- **Result**: Confirmed EN (pin 3 on the DBV package) is a mandatory pin
  present on every package variant of this family, with **no internal
  pull-up or pull-down bias** — a genuinely floating EN produces
  undefined/undetermined enable behavior. This independently reconfirms the
  exact failure mechanism Cycle 1's ISS-001 finding described (dead board
  or brownout/chatter risk), from the primary source, not from the design
  doc's or Cycle-1-report's own restatement of it.
- **Document consistency**: Full-document grep for EN-pin/hedge language
  (37 matches) confirms the hedge ("if the exact package variant... has an
  active EN pin requiring a level... flagged as a minor implementation
  detail to confirm... at layout time") is **completely removed** — §3.4,
  §12 (new `EN_VIN` net), §13, §14, §15, and §16 all now consistently state
  a firm, unconditional EN→VIN tie with no remaining ambiguity anywhere.
- **Side-effect check**: Independently confirmed a direct EN-to-VIN tie
  needs no additional decoupling capacitor (checklist item 5 above) — the
  fix introduces no new gap.
- **Conclusion**: Fix holds up under independent re-verification.
  `validation/open-issues.md` updated: **ISS-001 → RESOLVED** (2026-09-01).

#### ISS-002 (HIGH) — LDO Vin ROC margin — **technical analysis independently RE-CONFIRMED sound; disposition correctly not self-resolved**

- **Independent method**: Two separate fact checks — (a) the real-world
  USB-C/USB-PD vSafe5V ceiling, via a search grounded in the USB-PD
  specification (Table 7.4.3), and (b) the TLV755P family's Vin AMR/ROC
  figures, via a search grounded in TI's own datasheet.
- **Result**: (a) vSafe5V range = **4.75–5.5V**, confirmed independently —
  matches §3.5's claim exactly (wider than REQ-101's stated 4.75–5.25V
  legacy-USB figure). (b) TLV755P Vin **AMR = 6.0V**, **ROC = 1.45–5.5V**,
  confirmed independently — matches §3.5's arithmetic exactly. This is not
  a case of re-citing DS-PWR-002/003; both governing numbers were
  independently re-derived from separate sources this cycle.
- **Technical soundness assessment**: §3.5's analysis correctly
  distinguishes two different things that are easy to conflate — an AMR
  exceedance (real damage risk; **not applicable**, since even 5.5V-in
  leaves 0.5V/9% margin under the 6.0V AMR) versus a ROC-ceiling
  exceedance (per TI's own datasheet convention, a "may not meet all
  specified electrical characteristics" caveat, not a damage risk). This
  characterization is accurate and neither overstates the finding (by
  implying damage risk that isn't there) nor understates it (by treating
  the effectively-zero ROC margin as a non-issue). The recommended
  disposition — ACCEPTED-RISK, routed to the Hardware Lead / human Chief
  Engineer per `docs/architecture.md` §8, with a component-swap
  alternative explicitly flagged but correctly left for the Hardware
  Lead/Component Engineer to decide rather than self-selected by the
  Circuit Engineer — is reasonable and appropriately scoped.
- **Authority check**: Per `docs/architecture.md` §8 and this skill's own
  "Out of scope" clause, the Hardware Reviewer **cannot** grant
  ACCEPTED-RISK for a HIGH finding; only a named human Chief Engineer
  sign-off can. Independently confirmed via `tools/check_open_issues.py`
  that the CI gate enforces exactly this rule mechanically (a HIGH finding
  must be `RESOLVED` or `ACCEPTED-RISK`, or the gate fails) — running the
  gate script against the updated backlog this cycle produces exactly one
  failure, on ISS-002, which is the correct and intended outcome right now.
- **Conclusion**: The finding's technical characterization holds up under
  independent re-verification and is sound; its disposition is correctly
  *not* something this review can close. `validation/open-issues.md`
  updated: **ISS-002 → stays OPEN** (not RESOLVED, not ACCEPTED-RISK),
  with a note that the technical analysis is sound and the disposition is
  pending human Chief Engineer sign-off. This is the one item preventing a
  clean PASS this cycle.

#### ISS-006 (MEDIUM) — BOOT0/PB8 correction — **independently RE-CONFIRMED, spot-check holds up**

- **Independent method**: Two separate web searches for the STM32G0x0
  sub-family's BOOT0 pin mapping, one specifically targeting the
  STM32G031x4/x6/x8 errata sheet (es0487), which discusses PA14/BOOT0/SWCLK
  interaction — a strong corroborating signal since it cites a real,
  specific secondary document rather than a generic/templated answer.
- **Result**: Confirmed **BOOT0 is muxed onto PA14** (shared with SWCLK)
  on this sub-family, independently of PB8. Separately confirmed PB8
  physically exists on the LQFP-32 package with real alternate function
  **I2C1_SCL (AF6)** — unrelated to boot-mode selection. Both facts match
  Rev 2 §4.1/§4.2/§11/§13's corrected claims.
- **Residual honestly reproduced, not newly introduced**: PB8's *exact*
  pin number remains genuinely ambiguous even under fresh independent
  search — one query indicated pin 30, another indicated pin 32 (shared
  with VBAT in that source). This is the **same ambiguity Rev 2 §16 item 3
  already discloses**, not a new problem, and it is immaterial to this
  design since nothing is wired to PB8 regardless of its exact pin number.
  Independently reproducing rather than resolving this ambiguity is itself
  a useful negative result: it confirms the design doc's own disclosed
  uncertainty is genuine, not a cover for an unchecked claim.
- **Conclusion**: Fix holds up under independent re-verification.
  `validation/open-issues.md` updated: **ISS-006 → RESOLVED** (2026-09-01).

#### ISS-010 (LOW) — MCU VDD AMR lower bound — **fact independently RE-CONFIRMED correct; original recommended fix found INCOMPLETE, kept OPEN**

- **Independent method**: Web search targeting the STM32G031K8T6 VDD
  Absolute Maximum Rating specifically, cross-checked against a citation of
  ST's DS12992 Table 18.
- **Result**: Confirmed VDD AMR = **−0.3V to +4.0V** — matches Rev 2 §1/§16
  item 2's claim exactly. Zero design risk either way (3.3V nominal
  operation sits deep inside both this AMR and the 1.7–3.6V ROC).
- **A genuine independent finding this cycle, not a rubber-stamp**: ISS-010's
  own title and Recommended Fix in `validation/open-issues.md` named a
  specific action — *"Update DS-MCU-012 entry to VDD AMR Min −0.3V / Max
  4.0V… mark design-doc §16 UNKNOWN #2 resolved."* Checking
  `datasheets/evidence-log.md` directly (not just the design doc's
  restatement of it) shows only the **second half** was ever done: the
  design doc's own §1/§16 UNKNOWN tracker is correctly closed with a fresh
  direct citation, but **the DS-MCU-012 row's own Value column still
  literally reads "UNKNOWN"** as of this cycle — it was never edited. This
  is consistent with (not a fault of) the Rev 2 rework, since the Circuit
  Engineer's own changelog explicitly states it does not touch
  `datasheets/evidence-log.md` (that file is owned by the Hardware
  Reviewer/Hardware Lead) — but nobody closed this specific loop before
  now.
- **Conclusion**: The underlying engineering fact is correct and poses no
  risk, so this is not a design defect — but the originally-recommended fix
  was only partially executed, so declaring it fully `RESOLVED` would
  overstate what actually happened. `validation/open-issues.md` updated:
  **ISS-010 → kept OPEN** (LOW, non-gating — does not affect the CI gate or
  the verdict below) with a note explaining the fact/fix distinction and
  recommending a trivial follow-up edit to `datasheets/evidence-log.md`'s
  DS-MCU-012 row in a future pass (out of this cycle's two-file output
  scope).

### New/residual observations this cycle

No new CRITICAL, HIGH, or MEDIUM finding was introduced by the Rev 2 rework
itself — independently checked via the full 16-item re-run above, the
process-integrity git check, and the exhaustive I2C1/I2C2 and EN-pin/hedge
greps. The only new item surfaced this cycle is the ISS-010
evidence-log.md housekeeping gap described above, which is LOW severity,
non-gating, and already folded into ISS-010's own backlog row rather than
opened as a new ID (consistent with this cycle's tightly-scoped
`validation/open-issues.md` edit list).

### Verdict

- **Verdict**: **CONDITIONAL** (not a clean PASS)
- **Open CRITICAL count**: 0
- **Open HIGH count**: 1 (ISS-002 only — ISS-001 and ISS-011 are now
  independently confirmed RESOLVED)
- **What's blocking a clean PASS, precisely**: ISS-002 alone. Its technical
  characterization is independently confirmed sound and its recommended
  disposition (ACCEPTED-RISK) is reasonable — but per `docs/architecture.md`
  §8, only a named human Chief Engineer can actually grant ACCEPTED-RISK
  for a HIGH finding, and I do not have that authority. This is not
  "further engineering work" pending — the engineering analysis is done and
  independently checked out. What remains is a **human sign-off decision**
  (accept the thin ROC margin for this bench-use context, or ask the
  Component Engineer for an LDO with a higher Vin ROC ceiling), which
  belongs with the Hardware Lead/Chief Engineer, not with another circuit
  rework loop.
- **What independently checks out (no further engineering action needed)**:
  ISS-011 (I2C1→I2C2 relabeling), ISS-001 (LDO EN pin), ISS-006
  (BOOT0/PA14 + PB8/I2C1_SCL correction) all independently re-verified
  fixed against primary/authoritative sources, with full-document
  consistency confirmed by exhaustive grep, not spot-check. ISS-010's
  underlying fact also independently checks out, though its evidence-log.md
  paperwork is a trivial, non-blocking loose end (see above).
- **Next action**: Route ISS-002 to the Hardware Lead for the human Chief
  Engineer ACCEPTED-RISK decision (or a Component-Engineer-driven LDO
  swap, if that path is preferred) per `docs/architecture.md` §8 — **no
  further Circuit Engineer rework loop is required** for ISS-001/ISS-006/
  ISS-011, which are closed. `tools/check_open_issues.py` independently
  confirms this cycle's backlog state is internally consistent: it fails
  on exactly one violation (ISS-002, HIGH, neither RESOLVED nor
  ACCEPTED-RISK) and no others, which is the intended, correct gate
  behavior right now. A trivial, non-blocking housekeeping item
  (`datasheets/evidence-log.md` DS-MCU-012 Value column) remains for a
  future pass but does not affect this verdict.

---

## Mechanical Reviewer — Cycle 1 (first-ever Mechanical review, 2026-09-02)

### Review Cycle Metadata

- **Design revision reviewed**: `hardware/mechanical/bench-imu-01-enclosure.scad`
  (full parametric OpenSCAD source, 483 lines) together with its companion
  `hardware/mechanical/bench-imu-01-dimensional-spec.md` (full rationale +
  self-check, 570 lines) — Author: Mechanical Lead (AI agent), "this
  session," Status at handoff: self-check §11 claims "10/10 PASS," §12 lists
  9 Open Items carried forward. This is the **first-ever Mechanical
  Reviewer cycle** for this repository — the pass/fail benchmark named in
  `docs/architecture-evolution.md` §24 ("Can this AI engineering system
  create a believable, buildable enclosure from real electronics
  information?"). No prior Mechanical review exists to re-review against.
- **Reviewer**: Mechanical Reviewer — see
  `.github/agents/mechanical-reviewer.agent.md`. Independent of the
  Mechanical Lead role/session that authored the design.
- **Independence statement**: I did not author this enclosure. Every one of
  the 10 checklist items, the dimensional-spec's own §7 "Computed clearance
  checks," its §8 fastener-placement table and 3-way rejected-alternatives
  comparison, its §9 manufacturability claims, its §10 assembly-order
  walkthrough, and its §11 10/10 self-check were independently re-derived
  this cycle directly from the raw values in the `.scad` file and
  cross-checked against `hardware/mechanical-interface.md` — none were
  accepted on the strength of the Mechanical Lead's stated confidence, its
  "10/10 self-check PASS" claim, or its own narrative reasoning. All
  arithmetic (Z-height stack-up, standoff/wall clearances, bay margins,
  annular-wall thicknesses around every boss, fastener engagement depths,
  the `hull()`-based gusset geometry) was independently recomputed via
  Python scripts run against numbers transcribed directly from the `.scad`
  file, not by re-reading the spec's own arithmetic and nodding along.
- **Scope**: Full design — first review cycle for the Bench-IMU-01
  enclosure, so no "changed area only" narrowing applies. Covers
  `hardware/mechanical/bench-imu-01-enclosure.scad` and
  `hardware/mechanical/bench-imu-01-dimensional-spec.md` in full,
  cross-checked against `hardware/mechanical-interface.md` in full (Board
  Geometry, Mounting, Component Height Clearance — including the corrected
  8.5mm top-side figure superseding the 3.2mm USB-C figure — Connectors/
  Switches/LEDs, Mass). `hardware/schematic/bench-imu-01-design.md` §10-§13
  was read for original Circuit Engineer context only (component-level
  decisions are out of scope this cycle — the Electronics discipline's own
  Cycle 1/Cycle 2 gate already covers those).
- **Tooling disclosure (important honesty note)**: **No OpenSCAD/CAD
  rendering or slicing tool is available in this environment.** Neither the
  Mechanical Lead's own design nor this review could render the `.scad`
  file, generate an STL, or run it through a slicer to visually/mechanically
  confirm geometry. This review is conducted entirely **from source code** —
  reading the parametric `.scad` file's raw numbers and module logic
  directly and recomputing geometry by hand/script, the same constraint the
  Mechanical Lead itself operated under. This is disclosed as a real
  methodological limitation, not papered over: at least one of this cycle's
  findings (MISS-002, the base-tab gusset) is exactly the class of defect a
  five-second look at a rendered/sliced preview would catch instantly, but
  it was still independently caught here by working through the `hull()`/
  `cube()` primitives' actual dimensions by hand.
- **Parallel sub-scans run**: None dispatched as separate sub-agent scans
  this cycle — the full 10-item checklist was worked as a single integrated
  pass by this Mechanical Reviewer, consistent with the agent instruction
  that the verdict is a single serial integration step, not something to
  fragment across uncoordinated parallel opinions.
- **rubber-duck premise review run in parallel?**: Not indicated as run for
  this cycle. No `rubber-duck`-sourced row exists in
  `validation/open-issues.md` for the Mechanical discipline as of this
  cycle; this report does not rely on or duplicate any such review.
- **KiCad / CAD tool cross-checks used**: None — `kicad-*` tools were not
  invoked, since this design has no KiCad project (no PCB layout exists yet
  for Bench-IMU-01; the enclosure is designed against the Markdown
  interface contract, not a KiCad board file) and no OpenSCAD-equivalent
  rendering tool is available in this environment (see Tooling disclosure
  above).

### Checklist Results

Full checklist per `.github/skills/mechanical-review/SKILL.md`, all 10 items
independently worked (not a partial spot-check):

| # | Checklist item | Result | Notes |
|---|---|---|---|
| 1 | PCB mounting (standoff positions/diameters, boss integrity) | **PASS** | All 4 standoffs independently recomputed at the exact MH-1..MH-4 board-local coordinates from `hardware/mechanical-interface.md` "Mounting"; ⌀6.0mm OD confirmed clear of the interior wall by exactly 2.0mm on every corner (computed from `interior_x`/`interior_y`/`board_offset_x`/`board_offset_y`, not merely re-read from the spec). Minor dead-data note: `mount_holes[i][2]` (2.8mm clearance dia) is present in the array but never read by `standoff()`/`base_standoffs()` — see MISS-006. |
| 2 | Connector accessibility (cutout position/size/orientation) | **Finding — MISS-001 (HIGH)** | J1 (USB-C) cutout and D1 (LED) hole independently recomputed and confirmed correct (J1's Y/Z cutout range checks out against its own board-local position; D1 clear of the bay by 2.5mm and of MH-4 by 9.19mm vs. a 4.5mm sum-of-radii). J2/J3/SW1-vs-header-bay margin, however, is independently found to be measured from each connector's centerline, not from the design's own assumed footprints — real margins as low as 0.0mm, not the ~6mm implied. See MISS-001. |
| 3 | Component height clearance (top + bottom vs. interface file) | **PASS** | Full Z-stack independently recomputed from the base up: `floor_t(2.0)+standoff_h(6.0)+pcb_thickness(1.6)=9.6` → `+top_component_clearance(8.5)=18.1` (header stack top) vs. `base_total_h=floor_t+standoff_h+pcb_thickness+top_component_clearance+z_margin(0.5)=18.6` (split line) → margin = 18.6−18.1 = **0.5mm exactly**, matching `z_margin` precisely and confirming no collision → `total_height=base_total_h+lid_roof_t(2.0)=20.6mm`. **This independently matches the Mechanical Lead's claimed 20.6mm total height and "header stack top sits below the split line" conclusion exactly — no error found in the single most consequential number in this design.** |
| 4 | Internal clearance/interference (parts vs. walls/each other/fasteners) | **PASS** | Rear-tab-vs-bay clearance (spec's own pre-flagged Open Item #8) independently recomputed and confirmed correct (2.5mm gap on both sides, using true edge-to-edge math). The external-corner-tab approach and its 3 rejected alternatives (§8) were independently assessed: the reasoning for rejecting the shared-riser, inward-bulging-boss, and 4-interior-boss alternatives is sound, and the chosen approach is conceptually collision-free at the PCB/bay level — see items 5/6/9 below for implementation-level defects found in how that approach was executed. |
| 5 | Fastener placement (wall thickness around every boss, no fastener conflicts) | **Findings — MISS-003 (MEDIUM), MISS-004 (MEDIUM)** | PCB standoff annular wall ((6.0−2.0)/2=2.0mm) and PCB standoff engagement depth (4.4mm of 5.0mm, 0.6mm spare) both independently confirmed adequate. Base-tab pilot-hole annular wall (3.0mm/2.0mm margins) also confirmed adequate. However: the **lid tab's** clearance-hole annular wall is independently computed at only **1.6mm**, below the design's own stated 2.0mm minimum (MISS-003); and the lid/base-tab fastener pair has **0.0mm** engagement-depth spare margin, vs. the PCB standoff's deliberate 0.6mm spare (MISS-004). |
| 6 | Wall thickness (structural + stated 3D-printability rule) | **Finding — MISS-002 (HIGH), referenced here** | The uniform 2.0mm perimeter/roof/skirt wall thickness is independently confirmed adequate everywhere it was checked (skirt, roof, floor, standoff annular wall). The base corner tab, however, is a genuine cantilevered horizontal extension of that wall whose claimed printability solution (a 45° gusset) is found to be geometrically non-functional — see MISS-002 (fully written up under item 9 below, where the printability claim itself lives). |
| 7 | Assembly order (physically achievable sequence, no trapped parts) | **PASS** | §10's walkthrough independently re-derived and confirmed logically sound: PCB population before enclosure assembly correctly avoids the "headers trapped behind the lid" trap, and the lid-tab/base-tab external fastening is correctly sequenced last. Specifically checked per this cycle's task: rear-tab screwdriver access near the header bay — the rear tabs' global X-range has no XY overlap with the bay's X-range (separated by the same 2.5mm gap as item 4), so no interference is computable from the given data; a residual, undocumented ergonomic question (whether a tall real J2/J3 header could crowd a screwdriver's approach to the adjacent rear tabs) is noted but not raised as a formal finding, since it is not independently provable either way without the real header hardware confirmed (spec's own pre-existing Open Item #1). No snap-fit/permanent joint anywhere in the design was found to contradict the "no permanent snaps or adhesive" claim; the lid-skirt-to-base-wall joint is independently confirmed a true clearance (slip) fit, not an interference fit (`lid_skirt_inner_x/y = base_outer_x/y + 2×fit_clearance`, i.e. strictly larger by construction). |
| 8 | Print-fit tolerance (single stated value, consistently applied) | **Finding — MISS-005 (LOW)** | `fit_clearance` (0.2mm/side) is independently confirmed applied correctly and consistently at the one genuine printed-part-to-printed-part mating surface in this design (the lid skirt / base wall joint) — the only place two independently-printed solids actually slide against each other. However, the design's own claim (`.scad` lines 101-104 and dimensional-spec §11 item 8) that this same value also governs "all fastener clearance-hole sizing" is independently found not to be true of the implemented code — see MISS-005. |
| 9 | Manufacturability / 3D-printability (overhangs/bridges vs. stated rule, min wall thickness) | **Finding — MISS-002 (HIGH)** | J1's cutout bridge span (9.5mm vs. the stated 10mm `max_bridge_span`) independently confirmed within rule. The lid tab's "no chamfer needed" claim is independently verified TRUE via Z-coordinate/print-orientation reasoning (lid tabs genuinely share the roof's Z-range and are bed-adjacent when the lid is printed roof-down — independently confirmed by working through the `rotate([180,0,0])`/`translate(...)` print-layout transform, which correctly places the roof at Z=0..2mm touching the bed). The base tab's "45° self-supporting chamfer/gusset," however, is independently found to be a geometrically degenerate ~0.01mm sliver — see MISS-002, the most significant finding this cycle. |
| 10 | Interface-value traceability (every dimension traced to a source or explicit assumption) | **Finding — MISS-006 (LOW)** | Extensive, essentially complete `ASSUMPTION`/`ESTIMATE`/`DERIVED` tagging independently confirmed present on nearly every declared variable. Zero literal `CONFIRMED` tags exist in the `.scad` file — independently confirmed this is *correct*, not a violation, since `hardware/mechanical-interface.md`'s own Board Geometry/Mounting/Component-Height/Connector tables are themselves all `ESTIMATE`/`ASSUMPTION` (no real KiCad board exists yet), so inheriting that label is proper propagation, not a mismatch. Connector-position lines (`j1_x`/`j2_x`/etc.) lack an inline tag but are preceded by an explicit interface-row citation comment, satisfying `.github/instructions/mechanical-design.instructions.md`'s traceability rule via its "traces to an interface-file row" clause. `j1_ref_height` (3.2mm, the superseded USB-C figure) is independently confirmed used *only* for J1's own cutout sizing/visual, never commingled with the global `top_component_clearance` (8.5mm) budget. Two harmless dead/unused array fields were found (`mount_holes[i][2]`, `tab_positions[i][1]`) — see MISS-006. |

**Summary**: 0 CRITICAL, 2 HIGH (MISS-001, MISS-002), 2 MEDIUM (MISS-003,
MISS-004), 2 LOW (MISS-005, MISS-006).

### Findings

#### MISS-001 — Header/button bay (J2/J3/SW1) clearance margin is measured from connector centerlines, not from the design's own assumed footprints

- **Issue**: The dimensional-spec (§6, §7) and the `.scad` file's own
  comments (lines 233-238) both characterize `bay_x_min`/`bay_x_max`/
  `bay_y_min` as providing a "6mm margin" around J2, J3, and SW1.
  Independently recomputing this margin against the SAME `.scad` file's own
  `reference_pcba()` module (lines 445-451), which models J2/J3 as
  10mm(X)×6mm(Y) boxes and SW1 as a ⌀5mm cylinder — not points — shows the
  real clearances are far smaller: J2's near edge to `bay_x_min` = **1.0mm**
  (not 6mm), J2/J3's far edge to `bay_y_min` = **0.0mm** (not 6mm — the bay
  boundary is drawn exactly coincident with the assumed footprint's own
  edge), and SW1's near edge to `bay_x_max` = **3.5mm** (not 6mm).
- **Rationale**: `bay_x_min = j2_x(16) − 6 = 10` and `bay_x_max = sw1_x(44) +
  6 = 50` (lines 233-234) are computed from each connector's bare
  X-coordinate — a single point — with a flat 6mm offset applied. But
  `reference_pcba()` (the SAME file's own visualization of these parts)
  independently defines J2/J3 as `cube([10, 6, top_component_clearance])`
  translated to span board-local X:[hx−5, hx+5] — i.e. J2 itself already
  occupies X:[11,21], 5mm on either side of its own centerline.
  Cross-referencing the two: the bay boundary (X=10) sits only 1.0mm
  outside J2's own assumed body edge (X=11), not 6mm — the connector's own
  footprint half-width silently consumed 5 of the intended 6mm. The same
  pattern repeats in Y: `bay_y_min = 34` is explicitly commented as "6mm
  header/switch footprint-depth allowance in from the board's Y=40 edge,"
  but `reference_pcba()`'s own J2/J3 boxes are translated to Y:[34,40] —
  meaning Y=34 IS the assumed footprint's own far edge, not a boundary 6mm
  clear of it. SW1 fares better (footprint X:[41.5,46.5] vs.
  `bay_x_max`=50 → 3.5mm real clearance) but is still well under the "6mm"
  language. This is a genuine, presently-verifiable internal inconsistency —
  it does not require the real J2/J3 hardware to be confirmed first (spec's
  own Open Item #1) to detect, since it is fully derivable from numbers
  already committed to the file; it is, however, compounded by that same
  unconfirmed-hardware risk, since a shrouded/keyed real header commonly
  exceeds a bare-pin-row's nominal footprint.
- **Datasheet Source**: `hardware/mechanical-interface.md` "Connectors,
  Switches & LEDs" table, J2/J3/SW1 rows (X/Y point positions only, no
  footprint dimension given by the interface file itself) — cross-referenced
  against `hardware/mechanical/bench-imu-01-enclosure.scad` lines 233-238
  (`bay_x_min`/`bay_x_max`/`bay_y_min` derivation) and lines 445-451
  (`reference_pcba()`'s own assumed J2/J3/SW1 footprints);
  `bench-imu-01-dimensional-spec.md` §6 ("all comfortably inside with
  margin") and §11 self-check item 2 ("PASS").
- **Failure Mechanism**: If the real J2/J3 headers or SW1's real package
  occupy anything close to the footprint this same design already assumes
  for visualization purposes, the lid's header-bay opening does not
  actually provide the 6mm of clearance its own comments and self-check
  claim — a real assembled unit could have a shrouded header body or switch
  bezel touching or overlapping the cutout's edge, requiring the bay to be
  enlarged/reworked (filing/redesign) to actually mate a cable or press the
  button without contacting the printed edge.
- **Affected Component**: Lid header/button bay cutout (`bay_x_min`,
  `bay_x_max`, `bay_y_min` in `bench-imu-01-enclosure.scad`); J2 (UART
  header), J3 (SWD header), SW1 (reset button).
- **Recommended Fix**: Recompute `bay_x_min`/`bay_x_max`/`bay_y_min` from
  each connector's own assumed (or, once available, real) footprint *edge*,
  not its centerline/point position, and re-add a genuine spare margin
  (e.g. 6mm) beyond that edge — consistent with how the tab-vs-bay
  clearance (Open Item #8) already correctly uses edge-to-edge math
  elsewhere in the same document. At minimum, reconcile the "6mm margin"
  language with the footprint `reference_pcba()` itself assumes, so the two
  don't silently disagree.
- **Severity**: HIGH — a likely functional-access failure under realistic
  conditions (a real shrouded header or switch bezel at or near the assumed
  footprint size), directly contradicting the self-check's own
  "PASS...all comfortably inside with margin" claim for this checklist
  item, and affecting 3 of the design's 5 connectors/controls.

#### MISS-002 — Base corner-tab "45° self-supporting chamfer/gusset" is geometrically non-functional (degenerate ~0.01mm sliver, not a real wedge)

- **Issue**: `base_tab()` (lines 310-335) implements its claimed "45°
  self-supporting chamfer/gusset" as `hull()` of two `cube([tab_w, 0.01,
  0.01])` blocks (lines 329-334) — both degenerately thin (0.01mm) in
  *both* the Y and Z directions, not just one. `hull()` of two such
  near-point-like clusters produces an extremely thin (~0.01mm) diagonal
  sliver, not a solid triangular wedge filling the space beneath the tab.
  This directly contradicts dimensional-spec §9.2's explicit claim ("a 45°
  self-supporting chamfer/gusset... runs from the wall face up to the tab's
  underside, keeping the whole feature within the stated `max_overhang_deg`
  rule without printed support material") and self-check §11 item 9's
  "PASS... checked against actual design features."
- **Rationale**: The nominal centerline geometry is correct —
  `tab_chamfer_run = tab_project(6.0)` (lines 267-277), giving an equal 6mm
  rise/6mm run (a true 45° slope), and both `hull()` inputs are correctly
  *positioned* at the two endpoints a real gusset should span (the wall's
  outer face at the gusset's base Z, and the tab's own outer-bottom edge at
  the tab's Z) — there is no disconnection between the gusset and either
  the wall or the tab. The defect is purely in the *cross-sectional
  thickness* of the solid produced: for `hull()` to yield a real,
  load-bearing wedge with meaningful cross-sectional area, at least one of
  the two input primitives needs genuine (non-degenerate) extent in the
  direction being spanned (Y, here). As coded, both inputs are 0.01mm in Y
  *and* Z, so the resulting hull is a thin diagonal blade far below any FDM
  printer's minimum feature size (typically ~0.4-0.8mm, i.e. one to two
  nozzle widths) — it would not print as a meaningful support structure,
  and may not even mesh/slice reliably as a distinct feature at all.
  Separately, the `.scad` file's own comment at the gusset (lines 321-325)
  already partially hedges this ("a reasonable approximation of a wedge
  gusset... this is not a load-bearing dimension... a human should feel
  free to refine the exact profile") — but this caveat was not carried
  through into the dimensional-spec's more confident §9.2 claim or into
  self-check item 9's "PASS," which state the overhang issue is fully
  addressed. The base tab itself is confirmed (via `base_total_h -
  tab_base_t` through `base_total_h`, i.e. Z:[13.6,18.6]mm in the base's own
  natural floor-down print orientation) to be a genuine 90°, 6mm-deep,
  5mm-thick horizontal overhang roughly 3/4 of the way up the base's 18.6mm
  print height — mid-print, not bed-adjacent — so it does need real support
  (printed or gusset-based) to avoid drooping/degraded print quality,
  contrary to the "without printed support material" claim.
- **Datasheet Source**: `hardware/mechanical/bench-imu-01-enclosure.scad`
  lines 267-277 (chamfer rationale comment), lines 310-335 (`base_tab()`
  implementation, especially the `hull(){ cube([tab_w,0.01,0.01]);
  cube([tab_w,0.01,0.01]); }` construct at lines 329-334);
  `bench-imu-01-dimensional-spec.md` §9.2 (explicit "without printed support
  material" claim) and §11 self-check item 9 ("PASS").
- **Failure Mechanism**: Printed exactly as coded, the base tab's
  overhanging outer 6mm × 8mm × 5mm volume has no real supporting structure
  beneath it in the model. Sliced without a human manually adding support
  material (which both the design and its self-check claim is
  unnecessary), the tab is likely to droop, print with poor surface
  quality, or partially fail to bridge at this exact location — precisely
  where the M2.5 self-tapping pilot hole for the lid-fastening screw is
  threaded. A degraded tab boss risks stripped threads, a cracked tab, or a
  lid corner that cannot be fully/reliably fastened. This affects all 4
  base tabs identically (100% of the lid-fastening mechanism's base-side
  bosses), since `base_tab()` is called identically for every entry in
  `tab_positions`.
- **Affected Component**: All 4 base corner tabs (`base_tab()` /
  `base_tabs()` in `bench-imu-01-enclosure.scad`) — the entire base-side
  half of the lid's fastening mechanism.
- **Recommended Fix**: Replace the degenerate `hull()` construct with a
  genuine solid wedge — e.g. a `linear_extrude` of a right-triangle 2D
  `polygon()` (with real rise and run matching `tab_chamfer_run`) swept
  along `tab_w`, or a `hull()` between two primitives that each have real
  (non-zero, print-resolvable) extent in Y and Z — so the gusset actually
  fills the triangular volume beneath the tab. Alternatively/additionally,
  explicitly flag in the design that the base tabs require sliced-in
  support material until the gusset geometry is corrected, rather than
  claiming the overhang is already self-supporting.
- **Severity**: HIGH — a likely, systemic print-quality/structural defect
  at the sole fastening feature on the base side of the lid joint, under
  normal/expected printing conditions (not a rare corner case), directly
  contradicting an explicit design claim and a self-check "PASS" for this
  exact checklist item.

#### MISS-003 — Lid tab's clearance-hole annular wall (1.6mm) is below the design's own stated 2.0mm minimum wall thickness

- **Issue**: The lid tab reuses the same `tab_w(8.0mm) ×
  tab_project(6.0mm)` rectangular footprint as the base tab, but with a
  larger `tab_clear_dia(2.8mm)` clearance hole (vs. the base tab's
  `tab_pilot_dia(2.0mm)` threaded pilot) centered in it. This yields a
  Y-direction (projection-depth) wall margin of `(6.0−2.8)/2 = 1.6mm` on
  both sides of the hole — below the design's own stated `min_wall_t =
  2.0mm` rule. The equivalent base-tab calculation, using the smaller
  2.0mm pilot diameter in the same footprint, gives exactly 2.0mm (right
  at, not below, the minimum).
- **Rationale**: The design applied its own minimum-wall-thickness rule
  correctly when originally sizing the base tab's footprint against its
  smaller pilot hole, but did not re-check the *same* footprint against the
  *larger* clearance hole reused for the lid tab. This is a real,
  directly-computable shortfall (not a judgment call): `tab_w`/
  `tab_project`/`tab_clear_dia`/`min_wall_t` are all named variables already
  in the file, and the arithmetic only requires combining them — it is not
  dependent on any unconfirmed real-hardware fact. This directly
  contradicts self-check §11 item 5's claim ("adequate surrounding material
  at every boss").
- **Datasheet Source**: `hardware/mechanical/bench-imu-01-enclosure.scad`
  line 112 (`min_wall_t = 2.0`), line 251 (`tab_w = 8.0`), line 252
  (`tab_project = 6.0`), line 261 (`tab_clear_dia = 2.8`);
  `bench-imu-01-dimensional-spec.md` §11 self-check item 5 ("PASS...
  adequate surrounding material at every boss").
- **Failure Mechanism**: The lid tab experiences compressive bearing stress
  from the screw head (clamping the lid down against the base tab) rather
  than radial thread-forming stress (since this is a clearance, not a
  threaded, hole) — so the practical risk is lower than a thread-cutting
  scenario, but a 1.6mm PETG wall at a fastening point is nonetheless
  thinner than the design's own declared safe minimum, raising a real (if
  bounded) risk of cracking or deforming under repeated assembly/
  disassembly or over-torquing, at all 4 lid tabs.
- **Affected Component**: All 4 lid corner tabs (`lid_tab()` /
  `lid_tabs()` in `bench-imu-01-enclosure.scad`).
- **Recommended Fix**: Either widen `tab_w`/`tab_project` for the lid tab
  specifically (a lid-side-only footprint override) to restore ≥2.0mm
  margin around the larger clearance hole, or reduce `tab_clear_dia` to the
  minimum practical M2.5 clearance size that still fits within the existing
  footprint with ≥2.0mm margin.
- **Severity**: MEDIUM — a real, clearly-quantifiable violation of the
  design's own stated minimum-wall-thickness rule at a fastening boss
  (directly analogous to this skill's own MEDIUM example, "wall thickness
  thinner than the stated 3D-printing minimum"), with a bounded failure
  mode (elevated crack/deformation risk under clamping stress, not a
  certain break) rather than a functional blocker.

#### MISS-004 — Lid/base-tab fastener pair has zero engagement-depth spare margin, unlike the PCB standoff's deliberate 0.6mm spare

- **Issue**: The single M2.5×6mm screw used throughout this design
  (`screw_len = 6.0mm`) engages 4.4mm of the PCB standoff's 5.0mm pilot
  depth (0.6mm spare) when fastening the PCB, but engages exactly 4.0mm of
  the base tab's exactly-4.0mm pilot depth (`tab_pilot_depth = 4.0mm`) when
  fastening the lid — a **0.0mm spare margin** fit, computed as: 6.0mm
  screw − 2.0mm lid-tab clearance-hole thickness (`tab_lid_t =
  lid_roof_t`) = 4.0mm available engagement, exactly equal to the 4.0mm
  pilot depth available.
- **Rationale**: The design's own comment (`.scad` lines 156-158) already
  explicitly discloses the raw numbers ("Lid tabs: passes through the lid
  tab's clearance thickness (2.0mm) and engages 4.0mm of the base tab's
  4.0mm pilot depth") and the fastener-placement table (dimensional-spec
  §8) explicitly labels this "full engagement" — a positive-sounding
  characterization of what is, numerically, a zero-tolerance condition, in
  contrast to the PCB standoff row's explicit "4.4mm engaged" (of 5.0mm)
  figure one row above it in the same table, which shows the design *does*
  know how to reason about spare margin when it chooses to. The two
  fastener applications of the identical screw are not held to the same
  margin-of-safety standard, and the zero-margin case is framed as a
  strength ("full engagement") rather than flagged as a risk.
- **Datasheet Source**: `hardware/mechanical/bench-imu-01-enclosure.scad`
  lines 151-158 (`screw_len` comment, explicitly stating both engagement
  figures) and line 256 (`tab_pilot_depth = 4.0`);
  `bench-imu-01-dimensional-spec.md` §8 fastener-placement table
  (PCB-standoff row: "4.4mm engaged"; lid/base-tab row: "full engagement").
- **Failure Mechanism**: Any positive real-world tolerance in the direction
  of a longer-than-nominal screw (a common ±0.2-0.3mm variance for M2.5
  self-tapping fasteners) or a shallower-than-nominal printed pilot hole
  would cause the screw to bottom out in the base tab's blind pilot hole
  before the lid tab is fully clamped flush against it — at that corner,
  the lid sits very slightly proud/loose rather than fully seated, a real
  but bounded fastening-quality degradation (not a broken part or a lid
  that cannot close at all), potentially recurring at any/all of the 4 lid
  corners.
- **Affected Component**: All 4 lid-to-base corner-tab fastener joints
  (`base_tab()`/`lid_tab()` in `bench-imu-01-enclosure.scad`).
- **Recommended Fix**: Either deepen `tab_pilot_depth` slightly (trading
  against the tab's own "1.0mm solid floor remaining" margin, which has its
  own room to give a little) or shorten the lid-side clearance-hole
  thickness assumption, to restore a small positive spare-engagement margin
  analogous to the PCB standoff's 0.6mm, and re-characterize the
  fastener-placement table's "full engagement" language to explicitly flag
  the margin (or lack of it) the way the standoff row already does.
- **Severity**: MEDIUM — a real, quantifiable inconsistency in
  margin-of-safety practice between two uses of the same fastener within
  the same design, with a plausible but bounded failure mode (an
  unevenly-clamped lid corner under realistic fastener-length tolerance,
  not a broken part or unusable design).

#### MISS-005 — Design's claim that `fit_clearance` governs "all fastener clearance-hole sizing" does not match the implemented code

- **Issue**: The `.scad` file's own header comment for `fit_clearance`
  (lines 101-104) states it is "THE single stated clearance allowance,
  applied at every place two parts actually mate: lid-skirt-to-base-wall
  radial gap, **and all fastener clearance-hole sizing**," and
  dimensional-spec §11 self-check item 8 repeats this claim near-verbatim
  ("0.2mm/side... applied at the lid/base skirt joint **and fastener
  clearance holes**"). Independently checked, this is not true of the code
  as implemented: `fit_clearance` (0.2mm/side) is used in exactly two
  lines (`lid_skirt_inner_x`/`lid_skirt_inner_y`, lines 186-187) — the
  lid-skirt/base-wall joint only. The fastener clearance-hole diameters
  (`mount_holes[i][2] = 2.8`, lines 62-69; `tab_clear_dia = 2.8`, line 261)
  are independent hardcoded literals that do not mathematically derive from
  `fit_clearance` at all: a strict `fit_clearance`-based clearance hole for
  an M2.5 screw (nominal 2.5mm major diameter) would compute as `2.5 +
  2×0.2 = 2.9mm`, not the 2.8mm actually used.
- **Rationale**: The 2.8mm figure is, on its own terms, a perfectly
  reasonable and independently-justified M2.5 clearance-hole size
  (`mount_holes`' own comment at line 63 cites the design.md/ISO 273
  close-to-normal-fit convention directly, 2.7-2.9mm) — there is no
  physical defect in the actual hole size chosen. The defect is that the
  code's own comment and the self-check both assert a single-variable,
  unified governance ("THE single stated clearance allowance... applied at
  every place") for a quantity that is, in fact, governed by two entirely
  separate, independently-chosen conventions (a print-to-print mating
  tolerance for the skirt joint, and a standard screw-clearance-hole
  convention for the fastener holes) — this is exactly the kind of
  silently-inconsistent traceability claim
  `.github/instructions/mechanical-design.instructions.md` warns against,
  here manifesting as a claim rather than a value blend.
- **Datasheet Source**: `hardware/mechanical/bench-imu-01-enclosure.scad`
  lines 101-104 (`fit_clearance` header comment), lines 186-187 (its only
  two actual uses), line 63 (`mount_holes` clearance-dia comment,
  independent ISO 273 convention), line 261 (`tab_clear_dia` comment);
  `bench-imu-01-dimensional-spec.md` §11 self-check item 8 ("PASS...
  applied at... fastener clearance holes").
- **Failure Mechanism**: None physical — the actual fastener clearance
  holes are correctly sized for their purpose regardless of which variable
  is credited. The risk is purely to future maintainability/traceability: a
  future edit to `fit_clearance` (e.g. tightening or loosening the stated
  print tolerance) would silently *not* propagate to the fastener
  clearance holes despite the code's own comment and self-check claiming it
  would, potentially misleading whoever makes that future change into
  believing a single-parameter update covers both cases when it does not.
- **Affected Component**: `fit_clearance` documentation/self-check claim;
  `mount_holes[i][2]` and `tab_clear_dia` (`bench-imu-01-enclosure.scad`).
- **Recommended Fix**: Either express the fastener clearance-hole diameters
  as an actual function of `fit_clearance` (if that is genuinely the
  intended governing parameter) or, more simply, correct the header
  comment and self-check item 8's wording to state that fastener clearance
  holes follow a separate, standard screw-clearance convention, distinct
  from `fit_clearance`'s print-to-print mating role — mirroring how
  `board_xy_keepout` and `z_margin` are already correctly and explicitly
  distinguished from `fit_clearance` elsewhere in the same file (lines 126,
  161-165).
- **Severity**: LOW — a documentation/self-check accuracy defect with no
  physical/functional consequence, since the actual dimension chosen
  (2.8mm) is independently reasonable on its own merits.

#### MISS-006 — Two array fields are defined but never consumed by the geometry code (dead data)

- **Issue**: `mount_holes[i][2]` (the 2.8mm PCB clearance-hole diameter,
  third column of the `mount_holes` array, lines 62-69) is never read by
  `standoff()` or `base_standoffs()` (lines 294-308), which only use
  `m[0]`/`m[1]` (X/Y). Separately, `tab_positions[i][1]` (the Y-component,
  second column of the `tab_positions` array, lines 279-288) is never read
  by `base_tab()` or `lid_tab()`, which derive the tabs' global Y-position
  purely from the direction flag `pos[2]`, not from `pos[1]`.
- **Rationale**: Both fields look load-bearing at the point they are
  declared (they read as real geometric inputs alongside the columns that
  *are* used) but are silently ignored by the code that consumes each
  array. This is not a physical defect — no incorrect geometry results from
  it — but is a genuine traceability/maintainability gap: a future editor
  changing `mount_holes[i][2]` or `tab_positions[i][1]`, expecting it to
  affect the model, would see no effect at all, and no comment currently
  flags either field as unused/vestigial.
- **Datasheet Source**: `hardware/mechanical/bench-imu-01-enclosure.scad`
  lines 62-69 (`mount_holes` array definition) vs. lines 294-308
  (`standoff()`/`base_standoffs()`, only consuming `m[0]`/`m[1]`); lines
  279-288 (`tab_positions` array definition) vs. lines 310-335
  (`base_tab()`, only consuming `pos[0]`/`pos[2]`).
- **Failure Mechanism**: None currently manifest — this is a latent
  documentation/maintainability risk, not an active geometric defect. The
  risk is a future edit silently having no effect, or a future reader
  misinterpreting either column as currently governing something it does
  not.
- **Affected Component**: `mount_holes` array, `tab_positions` array
  (`bench-imu-01-enclosure.scad`).
- **Recommended Fix**: Either wire `mount_holes[i][2]` into `standoff()`'s
  PCB-side clearance-hole modeling (if a through-hole in the PCB itself is
  ever modeled) and remove/comment `tab_positions[i][1]` as intentionally
  unused (since the tab's Y-position is fully and correctly determined by
  the direction flag alone), or add a one-line comment at each declaration
  noting the field is currently unused, so a future editor isn't misled.
- **Severity**: LOW — a style/traceability/documentation nitpick with no
  functional or manufacturability consequence.

### Verdict

- **Verdict**: CONDITIONAL
- **Open CRITICAL count**: 0
- **Open HIGH count**: 2 (MISS-001, MISS-002)
- **Independent confirmation of the design's most consequential number**:
  The full Z-height stack-up (`floor_t`+`standoff_h`+`pcb_thickness`+
  `top_component_clearance`+`z_margin`+`lid_roof_t` → `total_height`) was
  independently recomputed from the raw `.scad` values, not re-derived from
  the spec's own arithmetic, and **matches the Mechanical Lead's claimed
  20.6mm total height and "no collision, 0.5mm margin" conclusion exactly**.
  PCB mounting (item 1), component height clearance (item 3), and internal
  clearance/interference (item 4) all independently checked out with **no
  error found** — the enclosure's core architecture (does the PCB fit, do
  the standoffs land correctly, does the tallest component clear the lid)
  is sound.
- **What's blocking a clean PASS**: MISS-001 (header/button bay margin
  measured from centerlines, not the design's own assumed footprints — real
  margins as low as 0.0mm) and MISS-002 (the base tab's claimed
  self-supporting print gusset is geometrically degenerate and provides no
  real support), both HIGH. Neither is a "PCB doesn't fit" class defect,
  but both directly contradict explicit self-check "PASS" claims (§11
  items 2 and 9 respectively) and both are systemic (MISS-001 affects 3 of
  5 connectors/controls; MISS-002 affects all 4 base fastening tabs).
- **Also open, non-gating but should be dispositioned before Design
  Complete**: MISS-003 and MISS-004 (MEDIUM — lid-tab wall thickness below
  the design's own stated minimum, and zero-margin fastener engagement at
  the same tab joint), MISS-005 and MISS-006 (LOW — a
  documentation/self-check-accuracy gap around `fit_clearance`'s actual
  scope, and two harmless dead-data array fields).
- **Next action**: Loop back to the Mechanical Lead (routing decision for
  the Hardware Lead to make) for MISS-001 (recompute the bay margins from
  the connectors' own assumed footprint edges, not centerlines, and
  reconcile with the tab-vs-bay clearance's already-correct edge-to-edge
  convention) and MISS-002 (replace the degenerate `hull()` gusset with a
  genuine solid wedge, or explicitly require sliced-in support material for
  the base tabs) at minimum — both HIGH findings should be resolved before
  this design proceeds toward a physical print. The two MEDIUM findings
  (MISS-003, MISS-004) should also be addressed or explicitly dispositioned
  (`RESOLVED`/`DEFERRED`/`ACCEPTED-RISK` with Chief Engineer sign-off)
  before Design Complete per `docs/architecture.md` §8. The two LOW
  findings (MISS-005, MISS-006) are documentation/hygiene corrections that
  do not block progress.

---

## Mechanical Reviewer — Cycle 2 (Re-review after Rev 2 rework, 2026-09-03)

### Review Cycle Metadata

- **Design revision reviewed**: `hardware/mechanical/bench-imu-01-enclosure.scad`
  **Rev 2** (624 lines) together with its companion
  `hardware/mechanical/bench-imu-01-dimensional-spec.md` **Rev 2** (869
  lines) — Author: Mechanical Lead (AI agent), rework commit `7497bf2`
  ("Mechanical rework for Bench-IMU-01: fix 2 HIGH findings (Rev 2)"),
  which claims to fix all 4 Cycle-1 findings still open at the time
  (MISS-001 HIGH, MISS-002 HIGH, MISS-003 MEDIUM, MISS-004 MEDIUM). This is
  a **re-review, not a first review** — the Mechanical Lead's own Rev 2
  changelog (top of both files) and the Hardware Lead's own
  "independently re-verified by the Hardware Lead" claims embedded in the
  `7497bf2` commit message were read for orientation only, **never**
  accepted as a substitute for this Reviewer's own independent
  verification, per this cycle's explicit task instructions and this
  agent's independence mandate.
- **Reviewer**: Mechanical Reviewer — see
  `.github/agents/mechanical-reviewer.agent.md`. Independent of the
  Mechanical Lead session that performed the Rev 2 rework, and independent
  of the Hardware Lead session whose commit message asserts its own
  verification pass.
- **Independence statement**: I did not treat any Rev 2 claim — the
  Mechanical Lead's in-code "MISS-00X fix" comments, its dimensional-spec
  "Rev 2" changelog, or the Hardware Lead's commit-message arithmetic — as
  self-certifying. Every one of the 4 fixes was independently re-derived
  this cycle **from the raw `.scad` variable values themselves**
  (`j2_x`/`j3_x`/`sw1_x`/`sw1_y`/`board_offset_x`/`board_offset_y`/
  `bay_edge_margin`/`bay_x_min`/`bay_x_max`/`bay_y_min` for MISS-001;
  the `polygon()`/`rotate([0,90,0])`/`linear_extrude()` primitives
  themselves for MISS-002; `lid_tab_project`/`tab_clear_dia`/`tab_w` for
  MISS-003; `screw_len`/`tab_lid_t`/`tab_base_t`/`tab_pilot_depth`/
  `base_total_h` for MISS-004) — not by re-reading the Mechanical Lead's or
  Hardware Lead's own stated arithmetic and nodding along. Where the
  Mechanical Lead's in-code comments showed their own arithmetic
  (e.g. the rotation-transform comment at lines 425-441), that arithmetic
  was independently re-derived and, where possible, empirically tested
  against a real OpenSCAD render, rather than accepted because a comment
  existed.
- **Scope**: The 4 claimed fixes (MISS-001 through MISS-004) plus a fresh
  re-check of checklist items most likely to be affected by the rework
  (item 4 internal clearance/interference, item 5 fastener placement, item
  6 wall thickness, item 9 manufacturability, item 10 traceability),
  covering both changed files in full where the changes propagate (the bay
  cutout and D1 hole in `lid_shell()`; all 4 instances of `base_tab()`'s
  gusset and `lid_tab()`'s footprint, not only the one hand-traced
  instance). Items 1/3/7/8 are noted as carried forward/unaffected (see
  Checklist Results) since nothing in the Rev 2 diff touches PCB mounting,
  the Z-height stack-up, assembly order, or the single `fit_clearance`
  print-fit convention.
- **Tooling disclosure (significant rigor upgrade vs. Cycle 1)**: Unlike
  Cycle 1, which explicitly disclosed **no OpenSCAD/CAD rendering tool was
  available** and was conducted entirely from source-code hand arithmetic,
  this cycle had a genuine, working `openscad` CLI available (v2021.01 at
  `/opt/homebrew/bin/openscad`, confirmed via `--version` before relying on
  it) and used it extensively as independent, empirical evidence layered on
  top of (not instead of) hand re-derivation:
  - Rendered the real repo `.scad` file directly, unmodified, in both
    `show_mode="assembled"` and `show_mode="print_layout"` — both report
    **"Simple: yes"** (fully manifold, no self-intersections/errors),
    independently reproducing the Mechanical Lead's own claim rather than
    trusting it.
  - Empirically verified the `rotate([0,90,0])` coordinate-transform
    convention the MISS-002 fix's own comment claims, via a standalone
    test cube, before trusting that transform in the real gusset analysis.
  - Used a `-D 'show_mode="isolate_test"'` override (an unrecognized value
    that satisfies neither the `assembled` nor `print_layout` branch,
    yielding an empty top-level scene) together with `include
    <bench-imu-01-enclosure.scad>` wrapper files to render **individual
    modules in isolation** (`base_tab()`, the gusset construct alone,
    `lid_tab()`) for both a front-tab instance (`dy=-1`) and a rear-tab
    instance (`dy=+1`), rather than relying on hand-traced coordinates for
    only one orientation.
  - Wrote a custom Python STL parser (ASCII+binary, divergence-theorem
    signed-tetrahedron volume) — since `numpy-stl` is not installed in this
    environment — to independently measure rendered volumes and bounding
    boxes rather than trusting `openscad`'s own on-screen echo values alone.
  - Ran actual boolean `intersection()` renders (wedge vs. interior-cavity
    probe; wedge vs. pilot-hole probe; a growing 2D circle probe vs. the
    bay-cutout footprint for the D1 clearance check) rather than only
    comparing bounding boxes — a materially stronger collision test.
  - Calibrated the CGAL "Volumes: N" report's meaning first (via
    touching-cube / gapped-cube / overlapping-cube test renders) before
    relying on it to interpret `base_tab()`'s own render, to avoid
    misreading an internal bookkeeping count as a defect signal.
  This upgrade is disclosed transparently as new capability, not implied to
  have existed in Cycle 1.
- **Parallel sub-scans run**: None dispatched as separate sub-agent scans
  this cycle — worked as a single integrated pass, consistent with the
  agent instruction that the verdict is a single serial integration step.
- **rubber-duck premise review run in parallel?**: Not indicated as run for
  this cycle. No `rubber-duck`-sourced row exists for the Mechanical
  discipline in `validation/open-issues.md` as of this cycle.
- **Process-integrity check (new this cycle, mirroring the Hardware
  Reviewer's own Cycle 2 precedent)**: Independently ran `git log
  --oneline` and `git show --stat`/`--numstat 7497bf2` to verify the
  rework commit's own claim that "`validation/open-issues.md` and
  `validation/design-review.md` are not modified here." **Confirmed
  true**: the commit's file-stat summary shows exactly 2 files changed —
  `hardware/mechanical/bench-imu-01-dimensional-spec.md` (389
  insertions/89 deletions) and `hardware/mechanical/bench-imu-01-enclosure.scad`
  (170 insertions/28 deletions), totaling 559 insertions/117 deletions —
  no unauthorized edit to any `validation/` or `datasheets/` file was made
  by the Mechanical Lead this cycle.
- **KiCad / CAD tool cross-checks used**: `kicad-*` tools still not
  applicable — no KiCad project exists for this design (the enclosure is
  designed against the Markdown interface contract, not a KiCad board
  file), unchanged from Cycle 1. OpenSCAD (a genuinely available, distinct
  CAD/geometry tool) was used directly and extensively — see Tooling
  disclosure above.

### Checklist Results (re-run against changed areas and anything the changes could have affected)

| # | Checklist item | Result | Notes |
|---|---|---|---|
| 1 | PCB mounting | PASS (unaffected, carried forward) | Rev 2's diff touches only the bay/D1 cutout, the base-tab gusset, and the lid-tab footprint/fastener depths — nothing in `standoff()`/`base_standoffs()` or the `mount_holes` array changed. Independently confirmed via `git diff 208c94e 7497bf2 -- hardware/mechanical/bench-imu-01-enclosure.scad` that no standoff-related line was touched. |
| 2 | Connector accessibility (cutout position/size/orientation) | **RESOLVED — MISS-001 independently confirmed fixed** (see Findings) | J2/J3/SW1-vs-bay margins independently recomputed at a genuine, uniform 1.5mm on all 3 binding edges (was 0.0/1.0/3.5mm in Rev 1). J1/D1 were already PASS in Cycle 1 and are structurally unchanged (J1's cutout code does not appear in the Rev 2 diff at all) — **except** D1's own clearance to the now-wider bay, which independently drops to 1.0mm as a side effect; see new finding MISS-007 under item 6 below. |
| 3 | Component height clearance | PASS (unaffected, carried forward) | Rev 2 touches none of `floor_t`/`standoff_h`/`pcb_thickness`/`top_component_clearance`/`z_margin`/`lid_roof_t`. The Z-stack independently reconfirmed in Cycle 1 (18.6mm split line, 0.5mm margin, 20.6mm total height) is untouched by this rework and was not re-derived a second time this cycle since nothing in the diff could affect it. |
| 4 | Internal clearance/interference (parts vs. walls/each other/fasteners) | **PASS — independently re-verified, with one new MEDIUM finding (MISS-007) surfaced** | Gusset-vs-interior-cavity and gusset-vs-pilot-hole independently tested via actual OpenSCAD `intersection()` renders (not just bounding-box math) for **both** the front-tab and rear-tab instances — all 4 tests returned "Current top level object is empty," i.e. zero collision. Lid tab's 0.4mm/side footprint growth independently confirmed to land only in regions already solid or on a flat, bed-adjacent print layer — no new interference. Widened-bay proximity independently re-derived against all 3 neighbor classes named in this cycle's task: mounting holes/standoffs are moot (no Z-overlap with the lid-level bay cutout at all); the 4 corner tabs remain positive at 2.0mm (rear-left, down from 2.5mm) / 4.5mm (rear-right, up from 2.5mm) — a real but non-defective spacing shift, independently recomputed from `tab_positions[]`/`tab_w`/`bay_x_min`/`bay_x_max`, not accepted from the spec's own §12 Item 8 text; D1's clearance narrows to 1.0mm, independently confirmed via an OpenSCAD binary-search growing-circle probe, and **is** a genuine new problem — logged as MISS-007 (see below). It is a clearance that stays positive (not a fit failure) but registers as a checklist item 6 finding, not item 4. |
| 5 | Fastener placement (wall thickness around every boss, no conflicts) | **RESOLVED — MISS-003 and MISS-004 independently confirmed fixed**; all other bosses re-swept and confirmed unaffected | PCB standoff (2.0mm annular wall, 0.6mm engagement spare) and base-tab pilot-hole wall (3.0mm/2.0mm margins) independently re-confirmed unaffected by this rework (neither variable appears in the Rev 2 diff). Lid tab's annular wall independently recomputed at 2.0mm (Y) / 2.6mm (X), meeting the 2.0mm minimum (was 1.6mm) — MISS-003. Lid/base-tab engagement spare independently recomputed at +0.6mm (was 0.0mm), with the tab's own solid floor independently reconfirmed unchanged at 1.0mm — MISS-004. No new fastener-boss conflict found anywhere (mount-hole spacing, tab-to-tab spacing all unchanged by this rework). |
| 6 | Wall thickness (structural + stated 3D-printability rule) | **Finding — new MEDIUM (MISS-007)** | All wall thicknesses re-checked this cycle (skirt/roof/floor 2.0mm, standoff annular wall 2.0mm, base-tab pilot wall 2.0mm/3.0mm, lid-tab annular wall now 2.0mm/2.6mm) independently confirmed at or above the design's own stated `min_wall_t`=2.0mm minimum — **except** the D1-viewing-hole-to-header-bay isthmus in the lid roof, independently recomputed (and empirically probe-confirmed) at exactly **1.0mm**, below the 2.0mm minimum. This is a genuine new side effect of the MISS-001 fix (the bay's near edge moved from Y=34.0 to Y=32.5, board-local, narrowing this specific isthmus from what would have been 2.5mm to 1.0mm) — disclosed by the Mechanical Lead as a clearance/margin item (dimensional-spec §12 Open Item 8a) but not previously cross-checked against this specific wall-thickness rule. See MISS-007. |
| 7 | Assembly order (physically achievable sequence, no trapped parts) | PASS (unaffected, carried forward) | Rev 2 does not change any part's Z-range, mating sequence, or the lid-skirt/base-wall clearance-fit relationship. The Cycle 1 conclusion (PCB-population-first sequencing avoids trapped headers; external fastening is correctly last) is independently re-confirmed still applicable, since nothing in the diff bears on assembly order. |
| 8 | Print-fit tolerance (single stated value, consistently applied) | PASS (unaffected, carried forward) | `fit_clearance` (0.2mm/side) and its one genuine printed-to-printed mating surface (lid skirt / base wall) are untouched by Rev 2. MISS-005 (the pre-existing, out-of-scope documentation gap about `fit_clearance`'s claimed vs. actual scope) is intentionally not re-litigated this cycle per the task's explicit exclusion of MISS-005/006. |
| 9 | Manufacturability / 3D-printability (overhangs/bridges vs. stated rule, min wall thickness) | **RESOLVED — MISS-002 independently confirmed fixed** (most rigorously verified finding this cycle); wider lid tab independently confirmed to still print cleanly | The new gusset wedge's 45° angle independently confirmed via three separate methods (hand algebra from `tab_chamfer_run`/`tab_project`, a rendered-and-measured STL bounding box showing equal 6.0mm/6.0mm legs, and direct comparison against the stated `max_overhang_deg=45`) to sit exactly **at**, not beyond, the self-supporting limit — consistent with FDM printing floor-down with no manual support, for **both** the front-tab and rear-tab instances (not just the one hand-traced originally). The lid's wider tab footprint (0.4mm/side growth) was independently re-confirmed to be a flat, bed-adjacent, first-print-layer feature when the lid prints roof-down (`rotate([180,0,0])`), not a new Z-direction overhang — it introduces no new printability defect. J1's bridge span (9.5mm vs. 10mm `max_bridge_span`) is unchanged by this rework (confirmed not present in the Rev 2 diff) and was not re-derived a second time. The new D1 isthmus (MISS-007, see item 6) is a wall-thickness/fragility concern, not an overhang/bridge-angle concern, and is tracked there instead. |
| 10 | Interface-value traceability (every dimension traced to a source or explicit assumption) | PASS, with one process observation folded into MISS-007's writeup | All 4 fix areas independently confirmed to carry traceable `ASSUMPTION`/`DERIVED` tags and/or explicit "MISS-00X fix (Mechanical Reviewer Cycle 1, ...)" provenance comments — e.g. `bay_edge_margin` is explicitly tagged `DERIVED` and cross-references `board_xy_keepout`'s own precedent; `lid_tab_project` is explicitly tagged `DERIVED, LID TAB ONLY` with its own formula spelled out. The D1-to-bay side effect (MISS-007) is itself a **positive** traceability example — the Mechanical Lead's own in-code comment at the `bay_y_min` derivation explicitly discloses the exact 1.0mm number and cross-references dimensional-spec.md §12 Open Item 8a, rather than leaving it silent; this cycle's finding is that the disclosure was framed only as a clearance question, not cross-checked against the item-6 wall-thickness rule — a process gap, not a silent/undisclosed value. |

**Summary**: 0 CRITICAL, 0 HIGH open (both MISS-001 and MISS-002
independently confirmed RESOLVED this cycle), 0 MEDIUM open from Cycle 1
(both MISS-003 and MISS-004 independently confirmed RESOLVED this cycle),
**1 new MEDIUM (MISS-007)** independently found this cycle as a genuine
side effect of the MISS-001 fix.

### Re-verification of Cycle 1 findings

#### MISS-001 — Header/button bay (J2/J3/SW1) clearance margin — RESOLVED, independently confirmed

- **Independent re-derivation performed**: Read `reference_pcba()` (now at
  lines 576-597) directly — not the spec's or the commit message's own
  arithmetic — for the ground-truth footprint definitions: J2/J3 headers
  are modeled as `for (hx = [j2_x, j3_x]) translate([hx-5, 40-6, comp_z])
  cube([10, 6, top_component_clearance])` (lines 588-590), i.e. each spans
  board-local X:[hx−5, hx+5], Y:[34,40]; SW1 is modeled as `translate([sw1_x,
  sw1_y-2.5, comp_z]) cylinder(d=5, h=5)` (lines 592-593), i.e. a circle of
  radius 2.5mm centered at board-local (sw1_x, sw1_y−2.5) = (44, 37.5),
  spanning X:[41.5,46.5], Y:[35,40]. With `j2_x=16.0`, `j3_x=30.0`,
  `sw1_x=44.0`, `sw1_y=40.0` (lines 86/88/90) and the new
  `bay_x_min=9.5`/`bay_x_max=48.0`/`bay_y_min=32.5` (lines 269/272/276,
  each derived from a shared, newly-named `bay_edge_margin=1.5` at line
  250), I independently computed:
  - J2's own left edge (X=16−5=11) to `bay_x_min` (9.5): **1.5mm**.
  - J2/J3's shared near edge (Y=40−6=34, identical for both since the Y
    translate does not depend on `hx`) to `bay_y_min` (32.5): **1.5mm**
    (this is the binding Y-constraint; SW1's own Y-span [35,40] gives a
    more generous 2.5mm and is not binding).
  - SW1's own right edge (X=44+2.5=46.5) to `bay_x_max` (48.0): **1.5mm**.
  - J3's footprint (X:[25,35]) sits comfortably inside both X-boundaries
    with 15.5mm/13mm to spare — not a binding constraint at either edge.
  All three binding margins are independently confirmed **genuinely
  uniform and positive at exactly 1.5mm** — a real fix, not a numerical
  coincidence: symbolically, `bay_x_min = (j2_x−5) − bay_edge_margin`
  means `margin = (j2_x−5) − bay_x_min ≡ bay_edge_margin` by construction
  (the "−5" term is J2's own cube half-width, which is the SAME constant
  used in both places), and the same cancellation holds for the
  `bay_y_min`/"−6" pair and the `bay_x_max`/"+2.5" pair. This is a
  structurally sound fix as currently written, though it depends on the
  hardcoded footprint constants (5, 6, 2.5) in the `bay_*` formulas and in
  `reference_pcba()`'s own `cube()`/`cylinder()` calls being kept in
  lockstep by a future editor — they are not driven by one single shared
  variable, so this is "correct by current, verified construction," not
  "unbreakable by architecture." This nuance does not change today's
  disposition (RESOLVED) but is worth a future maintainability note.
- **New problem introduced by the fix? Two side effects found by
  independently checking every neighbor, not by re-reading the spec's own
  claims.** Per this cycle's explicit task ("does the wider bay now come
  too close to anything else — a mounting hole, a corner tab, D1?"), I
  independently re-derived the bay's proximity to the 4 mounting holes/
  standoffs, the 4 corner tabs, and D1 — each from raw `tab_positions[]`/
  `mount_holes[]`/`d1_x,d1_y` values, not from the spec's own §12 Item
  8/8a text (checked only afterward, as a cross-reference, per below).
  - **Mounting holes / standoffs: not a live constraint (moot by Z, not
    just by XY margin).** `mount_holes[]` (line 64-69) and `tab_positions[]`
    (line 369-374) share the *identical* 4 board-local XY pairs — (3.5,
    3.5), (56.5,3.5), (56.5,36.5), (3.5,36.5) — so a standoff and a corner
    tab always sit on the same XY column. But `standoff()` only occupies
    the low-Z region near the PCB/floor while the bay cutout is cut through
    the *lid roof* near the top of the assembly — the two features do not
    share a Z-range at all, so no XY proximity there can produce a real
    interference regardless of margin. (For completeness: even purely on
    XY, `standoff_od=6.0mm`, i.e. a 3.0mm radius from the shared rear-left
    XY column, gives a 3.0mm gap to `bay_x_min` — looser than the tab's own
    2.0mm below — so the standoff was never going to be the binding
    surface even if it did share Z with the bay.)
  - **Corner tabs: a real, live, positive-margin side effect —
    independently re-derived, not assumed away.** Both `base_tab()` and
    `lid_tab()` use `tx = board_offset_x + pos[0]` and a shared X-width
    `tab_w=8.0mm` (line 300; `lid_tab_project` only widens the tab's
    *Y*-footprint, not X — see MISS-003 below), so the tab's global X-span
    is independent of the MISS-001/MISS-003 fixes and identical for both
    tab types. Rear-left tab (`tab_positions[3]=[3.5,36.5,+1]`):
    `tx=3.5+3.5=7.0` → X-span `[7.0−4.0, 7.0+4.0]=[3.0,11.0]`. Bay's global
    X-span (`board_offset_x+bay_x_min` to `board_offset_x+bay_x_max` =
    `3.5+9.5` to `3.5+48.0`) = `[13.0, 51.5]`. Gap = `13.0−11.0 = 2.0mm`.
    Rear-right tab (`tab_positions[2]=[56.5,36.5,+1]`): `tx=3.5+56.5=60.0`
    → X-span `[56.0,64.0]`; gap to the bay's right edge = `56.0−51.5 =
    4.5mm`. Both independently recomputed values match the dimensional-
    spec's own disclosed §12 Item 8 numbers (2.0mm / 4.5mm, down from a
    uniform 2.5mm pre-MISS-001) — a genuine agreement found by working the
    arithmetic myself, not by copying the spec's claim. **Both remain
    positive: no tab-vs-bay collision.** This is a feature-to-feature
    *spacing* check (item 4), not a wall-thickness check (item 6): the
    material between the tab's outer edge and the bay's edge is ordinary,
    un-thinned lid-roof/wall stock (no second cutout squeezes it from the
    far side the way D1's hole does), so there is no isthmus whose cross-
    section needs to clear `min_wall_t` here — the 2.0mm rear-left figure
    coinciding numerically with `min_wall_t` is coincidental, not a wall-
    thickness violation. One residual, non-formal observation carried over
    in spirit from Cycle 1's own unresolved ergonomic note (a real,
    shrouded J2/J3 header might crowd a screwdriver's approach to the
    adjacent rear tab): that approach got very slightly tighter on the
    rear-left tab specifically (2.5mm→2.0mm) as a further knock-on of this
    same fix. Still not independently provable either way without real
    header hardware, so — consistent with how Cycle 1 left it — not
    elevated to a formal finding.
  - **D1 is affected, and is a real finding.** Independently confirmed
    (hand geometry, cross-referenced against the Mechanical Lead's own
    disclosed figure, and an OpenSCAD binary-search growing-circle probe
    test — three independent methods, see next finding) that D1's
    clearance to the bay's near edge narrows to exactly 1.0mm, below the
    design's own 2.0mm `min_wall_t`. Unlike the corner-tab case above, D1's
    hole *is* a two-sided isthmus concern (a round cutout with the bay
    cutout on one side and the lid's outer roof edge/skirt on the other,
    squeezing the material between them), so this one *does* implicate the
    wall-thickness rule. Logged as a new finding, **MISS-007** (MEDIUM) —
    see below. This does not reopen or invalidate MISS-001 itself (the
    bay-vs-connector margin problem MISS-001 actually describes is
    genuinely fixed), but it is a real, independently confirmed side effect
    of the same code change and is disclosed here in full per the
    independence mandate rather than left for a future cycle to discover.
- **Disposition**: **RESOLVED**. Independently re-verified correct and
  complete for the problem MISS-001 itself describes (bay-to-connector
  margin). The side effect on D1 is tracked separately as MISS-007 and does
  not reopen this finding.

#### MISS-002 — Base corner-tab gusset — RESOLVED, independently confirmed (most rigorously verified finding this cycle)

- **Independent re-derivation performed**: Read the replacement construct
  directly at lines 445-452 — `translate([tx-tab_w/2,0,0])
  rotate([0,90,0]) linear_extrude(height=tab_w) polygon(points=[[-z_bottom,
  y_wall], [-z0, y_wall], [-z0, y_tab_edge]])` — and independently
  re-derived, by direct matrix substitution (not by reading the inline
  comment's own claim), that `rotate([0,90,0])` maps local `(x,y,z)` to
  global `(z,y,−x)`. Confirmed this **empirically** with a standalone
  OpenSCAD test cube (`rot_test.scad`): a point placed at local (5,0,0)
  rendered at global (0,0,−5), exactly matching the derived formula and
  the code's own comment. With `tab_chamfer_run=tab_project=6.0mm`,
  `z0=base_total_h−tab_base_t=18.6−5.6=13.0`, `z_bottom=z0−tab_chamfer_run
  =7.0`, the polygon's 3 vertices — `(−7.0,y_wall)`, `(−13.0,y_wall)`,
  `(−13.0,y_tab_edge)` in the local extrude plane — form a genuine
  **non-degenerate right triangle** with legs of length 6.0mm (local-x,
  becoming global Z) and 6.0mm (local-y = global Y, `|y_tab_edge−y_wall| =
  tab_project = 6.0`), independently computed cross-sectional area =
  0.5×6.0×6.0 = **18mm²**, swept over `tab_w=8.0mm` → volume = **144mm³**
  — not the ~1e-7mm³ degenerate sliver the old `hull()` construct produced.
- **Empirical confirmation (beyond hand algebra, a rigor upgrade over
  Cycle 1)**: Using the `-D 'show_mode="isolate_test"'` override technique
  to render the real repo file's own modules in isolation (not a
  hand-copied re-implementation), I rendered the gusset wedge alone and the
  full `base_tab()` (cube+pilot-hole-cut+gusset) for **both** a front-tab
  instance (`tab_positions[0]`, `dy=−1`) and a rear-tab instance
  (`tab_positions[2]`, `dy=+1`):
  - Both renders report **"Simple: yes"** (fully manifold, no
    self-intersection) for every instance tested.
  - My own Python STL parser (signed-tetrahedron divergence-theorem volume,
    since `numpy-stl` is not installed here) measured the wedge-only STL at
    **144.0000mm³** — an exact match to the hand-derived value to 4 decimal
    places — and the combined tab+wedge STL at **398.3899mm³**, matching a
    hand cross-check (tab cube 8×6×5.6=268.8mm³ minus pilot-hole cut
    ≈14.451mm³ plus wedge 144mm³ ≈397.35–398.35mm³ depending on cylinder
    facet count) to well within the expected discretization tolerance of a
    faceted cylinder.
  - Actual boolean `intersection()` renders (not bounding-box comparison)
    of the wedge against an interior-cavity probe and against a
    pilot-hole probe, for **both** tab orientations (4 tests total), each
    returned **"Current top level object is empty"** — an empirical,
    render-based confirmation of zero collision, not an inference from
    coordinates alone.
  - Confirmed the wedge's own right-angle corner sits exactly flush with
    the tab cube's own bottom face (`z0=13.0` shared by both) and the
    wall's own outer face (`y_wall` shared with the base wall geometry),
    i.e. the wedge is correctly positioned to actually bear load between
    the wall and the tab, not merely coordinate-adjacent to them.
  - (Calibration note, for full transparency: I first verified what
    OpenSCAD's CGAL "Volumes: N" report actually means using deliberately
    constructed touching/gapped/overlapping test cubes, since a naive
    reading of "Volumes: 2" could be mistaken for "two disconnected
    pieces" — it is not; the discriminator is the Facets/Vertices count
    matching a single merged shape, which `base_tab()`'s own render shows.
    This calibration step is what makes the "Simple: yes" + volume-match
    result trustworthy rather than superficially reassuring.)
- **Print-angle re-confirmation**: The wedge's slope is independently
  confirmed to sit exactly **at** the stated `max_overhang_deg=45` limit
  (equal 6.0mm/6.0mm legs), for both tab orientations — self-supporting on
  a floor-down base print with no manual support material, matching (and
  now actually delivering) the dimensional-spec's original printability
  intent.
- **Disposition**: **RESOLVED**. This is now a genuine, correctly
  positioned, load-bearing solid wedge — independently confirmed via hand
  derivation, direct-matrix rotation verification, real OpenSCAD renders of
  the actual repo file (not a re-implementation) for both tab orientations,
  independent STL volume measurement, and actual boolean collision tests —
  the most thoroughly, multiply cross-checked finding this cycle.

#### MISS-003 — Lid tab clearance-hole annular wall — RESOLVED, independently confirmed

- **Independent re-derivation performed**: Read the new `lid_tab_project =
  2*min_wall_t + tab_clear_dia` (line 345, = 2×2.0+2.8 = **6.8mm**) and its
  use in `lid_tab()` (lines 505-519): the footprint cube is sized
  `[tab_w, lid_tab_project, lid_roof_t]`, while the clearance-hole cylinder
  (`tab_clear_dia=2.8mm`) is still centered on `hole_yc`, which is
  independently confirmed to derive from the **unchanged**, shared
  `tab_project` (6.0mm) — not from the new, wider `lid_tab_project` — via
  `hole_yc = tab_y0 + tab_project/2` (line 504). Recomputing the annular
  wall myself: Y-direction (the axis `lid_tab_project` actually governs) =
  `(lid_tab_project − tab_clear_dia)/2 = (6.8−2.8)/2 = 2.0mm` exactly,
  meeting the `min_wall_t=2.0mm` minimum (was 1.6mm before the fix,
  computed the same way with the old shared 6.0mm `tab_project`).
  X-direction = `(tab_w − tab_clear_dia)/2 = (8.0−2.8)/2 = 2.6mm`,
  unaffected by this fix and already adequate. Both meet or exceed the
  stated minimum.
- **Alignment cross-check (independently verified, not assumed)**: Because
  `hole_yc` still derives from the original `tab_project` rather than the
  new `lid_tab_project`, the lid's clearance hole remains exactly coaxial
  with the base tab's own pilot hole below it — recomputed the potential
  misalignment that *would* have resulted had the hole instead been
  centered on the wider footprint: `(lid_tab_project−tab_project)/2 =
  0.4mm`, which independently would have exceeded the clearance hole's own
  ~0.15mm/side nominal slop around an M2.5 shank and could have bound the
  screw — confirming the Mechanical Lead's choice to decouple footprint
  sizing from hole centering was the geometrically correct one, not merely
  a stated intention.
- **New interference from the wider footprint? No.** Independently traced
  the resulting 0.4mm/side growth in the lid tab's footprint and confirmed
  it lands entirely within regions that are either already solid (the
  lid's own roof slab, which the tab literally extends from) or, where it
  extends past the roof's own edge, on the flat first-print-layer (the lid
  prints roof-down per its `rotate([180,0,0])` `print_layout` transform),
  introducing no new overhang and no new collision with the header bay or
  any fastener boss.
- **Disposition**: **RESOLVED**. Independently recomputed to genuinely meet
  the 2.0mm minimum on both axes, with the fastener-hole coaxiality
  explicitly re-verified rather than assumed, and no new interference
  introduced by the footprint growth.

#### MISS-004 — Lid/base-tab fastener engagement spare — RESOLVED, independently confirmed

- **Independent re-derivation performed**: Re-derived the full Z-stack
  myself from the raw variables, not from the in-code comment's own
  stated arithmetic: `z0 = base_total_h − tab_base_t = 18.6 − 5.6 =
  13.0mm` (top of the tab cube's own bottom face is at Z=13.0; its top
  face is flush with `base_total_h`=18.6, the base/lid split line). The
  pilot-hole cylinder (`translate([...,  base_total_h − tab_pilot_depth])
  cylinder(d=tab_pilot_dia, h=tab_pilot_depth+1)`, lines 404-405) is cut
  from Z=`18.6−4.6=14.0` up through the top mating face at Z=18.6 (the
  "+1" is purely a boolean-cut clearance margin past the surface, not a
  real physical extension) — so the pilot hole's real depth, measured from
  the mating face down to its own blind bottom, is `18.6−14.0 = 4.6mm`,
  independently matching `tab_pilot_depth` exactly. The solid floor
  remaining below the hole's bottom (Z=14.0) down to the tab cube's own
  bottom (Z=13.0) is `14.0−13.0 = 1.0mm`, independently matching
  `tab_base_t − tab_pilot_depth = 5.6−4.6 = 1.0mm`.
- **Engagement-spare recomputation**: The screw (`screw_len=6.0mm`) passes
  through the separate lid tab's own thickness (`tab_lid_t=lid_roof_t=
  2.0mm`) via a clearance (non-threaded) hole, leaving `screw_len −
  tab_lid_t = 6.0−2.0 = 4.0mm` of screw available to actually engage inside
  the base tab's blind pilot hole. Comparing against the pilot hole's own
  independently-confirmed 4.6mm depth: **4.6 − 4.0 = +0.6mm of genuine
  positive spare margin** (was exactly 0.0mm before the fix, using the old
  `tab_base_t=5.0mm`/`tab_pilot_depth=4.0mm` pair) — independently matching
  the PCB standoff's own precedent spare (`standoff_pilot_depth(5.0) −
  (screw_len(6.0)−pcb_thickness(1.6)) = 5.0−4.4 = 0.6mm`, cross-checked
  fresh from `standoff_pilot_depth`/`pcb_thickness` rather than re-quoted
  from Cycle 1).
- **Floor-margin trade-off independently re-checked (not just accepted on
  the changelog's word)**: Confirmed `tab_base_t` (5.0→5.6mm) and
  `tab_pilot_depth` (4.0→4.6mm) were both increased by the identical
  +0.6mm, so the solid floor (`tab_base_t − tab_pilot_depth`) is exactly
  preserved at 1.0mm both before and after the fix — the engagement-spare
  problem was not silently solved by thinning the floor toward the ~0.4mm
  FDM minimum-feature-size range (which would have traded MISS-004 for a
  new MISS-002-like fragility defect); it was solved by growing the tab
  itself.
- **Disposition**: **RESOLVED**. Independently re-derived engagement
  arithmetic confirms a genuine +0.6mm spare (was 0.0mm), and the floor
  margin is independently confirmed preserved, not silently traded away.

### New finding this cycle

#### MISS-007 (NEW) — D1 (LED) viewing-hole-to-header-bay isthmus narrows to 1.0mm, below the design's own stated 2.0mm minimum wall thickness

- **Issue**: The MISS-001 fix correctly narrows `bay_y_min` from a
  board-local Y=34.0 (Rev 1) to Y=32.5 (Rev 2, `= 34.0 − bay_edge_margin`)
  to restore genuine margin around J2/J3/SW1 (see MISS-001 above). This
  same edge, however, is also the nearest boundary of the same cutout to
  D1's LED viewing hole, which sits at board-local `(d1_x, d1_y) =
  (10.0, 30.0)` with `d1_hole_dia = 3.0mm` (radius 1.5mm), independently
  confirmed unmoved by the Rev 2 diff. Narrowing `bay_y_min` by 1.5mm
  necessarily narrows D1's own clearance to the bay by the same 1.5mm —
  from what would have been 2.5mm down to independently-confirmed
  **1.0mm** — below this same design's own stated `min_wall_t = 2.0mm`
  (line 112).
- **Rationale**: In global coordinates, D1's center is at `(board_offset_x
  + d1_x, board_offset_y + d1_y) = (3.5+10.0, 3.5+30.0) = (13.5, 33.5)`,
  and the bay cutout's near edge is at global Y = `board_offset_y +
  bay_y_min = 3.5+32.5 = 36.0`, spanning global X:[`board_offset_x +
  bay_x_min`, `board_offset_x + bay_x_max`] = [13.0, 51.5] — an X-range
  that **contains** D1's own X=13.5 (only 0.5mm inside the bay's own left
  edge), meaning the closest point on the bay's boundary to D1 is on the
  flat Y=36.0 edge directly above it, not a corner. The gap is therefore a
  simple, non-diagonal distance: `36.0 − 33.5 − 1.5(radius) = 1.0mm`.
  Independently confirmed this is not merely a hand-arithmetic artifact via
  an **empirical binary-search probe**: a 2D circle centered on D1's own
  position, grown from a nominal radius, intersected against the bay
  cutout's own 2D footprint in OpenSCAD — the intersection is **empty**
  at a growth corresponding to a 1.00mm gap and **non-empty** at 1.01mm,
  independently pinning the true minimum gap at exactly 1.0mm via
  computational geometry, not distance-formula algebra alone. Since the
  lid roof is a full `lid_roof_t = wall_t = 2.0mm` thick at this location
  (both cutouts are full-depth in Z, cut all the way through the roof),
  this 1.0mm gap is a genuine 1.0mm-wide × 2.0mm-tall solid fin of
  material between the two openings — a real structural feature, not a
  shallow engraving — and it independently falls below the same
  `min_wall_t=2.0mm` rule this design applies (and independently verified
  to be met) at every other wall/annulus in this enclosure.
- **Was this silently introduced, or disclosed? Disclosed, but not fully
  cross-checked.** The Mechanical Lead's own `.scad` file (at the
  `bay_y_min` derivation and its trailing comment, lines 276-287) contains
  an inline comment explicitly stating this exact side effect and the
  1.0mm number, and dimensional-spec.md §12 Open Item 8a devotes explicit
  text to it,
  framing it as "the single item this Mechanical Lead would most want the
  Reviewer to look at again in this cycle." Full credit is given for that
  proactive disclosure — this is not a hidden defect. However, both the
  in-code comment and Open Item 8a frame this purely as a **margin/clearance
  adequacy** question ("still positive; is 1.0mm enough margin?"), and
  neither cross-references it against the design's own separately-stated
  `min_wall_t=2.0mm` wall-thickness rule (checklist item 6) — a rule this
  same design applies rigorously everywhere else (every other wall/annulus
  independently re-checked this cycle sits at exactly 2.0mm or above,
  never below). This finding's contribution is that specific
  cross-reference, not the discovery of a previously-unknown number.
- **Failure Mechanism**: A 1.0mm-wide, full-roof-thickness, isolated fin of
  printed plastic bridging two full-depth cutouts is a plausible FDM
  under-extrusion, warping, or handling-fracture point — thinner features
  cool and shrink asymmetrically relative to the surrounding mass and are
  more prone to snapping during print-bed removal, support-structure
  removal (if any is used elsewhere on the same print), or ordinary
  handling. In the worst case, the D1 viewing hole and the header/button
  bay opening could merge into a single larger opening (cosmetic, not
  functionally blocking — both openings remain independently usable even
  fully merged) or the fin could crack off entirely (also cosmetic at this
  specific location, since neither opening's own function depends on the
  fin remaining intact). This is a real but bounded risk, not a
  fit-blocking or fastener-blocking defect.
- **Affected Component**: D1 LED viewing hole and header/button bay cutout,
  both in the lid roof (`lid_shell()` in
  `hardware/mechanical/bench-imu-01-enclosure.scad`).
- **Recommended Fix**: Any of: (a) reduce `d1_hole_dia` from its current
  3.0mm **ESTIMATE** (per `hardware/mechanical-interface.md`, D1's real LED
  package/lens size is not yet confirmed) toward a smaller,
  still-adequate value to restore ≥2.0mm — needs Electronics/LED-datasheet
  input, since the diameter itself is not yet confirmed hardware; (b) add
  a small local reinforcement (a fillet or short rib bridging the isthmus)
  without moving either cutout; or (c) explicitly re-open and disposition
  this as an accepted, monitored exception to `min_wall_t` (e.g. a
  first-article-print watch item, directly analogous to the existing
  J1-bridge-span Open Item 9 already carried in the spec) — rather than
  leaving it addressed only under Open Item 8a's clearance-only framing.
- **Severity**: MEDIUM — directly analogous to MISS-003's precedent (a
  hole-to-edge annular/isthmus wall thickness below the design's own
  stated 2.0mm print-safe minimum). Not CRITICAL or HIGH: it does not
  block PCB fit, standoff mounting, or any fastener function, and both
  affected openings remain independently usable even in the worst-case
  failure. Does not block this cycle's verdict, per this document's own
  Cycle 1 precedent that open MEDIUM findings are non-gating (see Verdict
  below), but should be dispositioned by the Mechanical Lead before Design
  Complete.

### Verdict

- **Verdict**: **PASS**
- **Open CRITICAL count**: 0
- **Open HIGH count**: 0 (both MISS-001 and MISS-002 independently
  confirmed RESOLVED this cycle — see full re-verification above; neither
  fix was accepted on the strength of the Mechanical Lead's changelog or
  the Hardware Lead's commit-message arithmetic, both of which were
  independently re-derived from raw `.scad` values and, for MISS-002,
  additionally confirmed via genuine OpenSCAD renders, STL volume
  measurement, and actual boolean collision tests)
- **Open MEDIUM count**: 1 new (MISS-007 — see above). Both Cycle-1 MEDIUM
  findings (MISS-003, MISS-004) are independently confirmed RESOLVED this
  cycle.
- **Independent confirmation, stated plainly for both HIGH fixes**:
  - **MISS-001 holds.** The bay-to-connector margin is now a genuine,
    uniform, independently-recomputed 1.5mm at all three binding edges
    (J2/`bay_x_min`, J2+J3/`bay_y_min`, SW1/`bay_x_max`) — re-derived
    directly from `reference_pcba()`'s own footprint primitives, not
    re-read from any stated conclusion. The fix does have a real,
    independently-confirmed side effect (D1's clearance narrowing to
    1.0mm), which is disclosed in full as new finding MISS-007 rather than
    omitted — but this does not reopen MISS-001 itself.
  - **MISS-002 holds**, and is the most rigorously confirmed finding this
    cycle: independently re-derived by hand (non-degenerate 18mm²
    cross-section, 144mm³ volume, exact 45° slope) **and** confirmed
    empirically via real OpenSCAD renders of the actual repo file for
    both tab orientations ("Simple: yes" manifold geometry, STL-measured
    volume matching to within cylinder-facet-discretization tolerance, and
    actual `intersection()` renders against both the interior cavity and
    the pilot hole returning empty in all 4 tests run). This is a genuine
    solid, load-bearing wedge, not a degenerate artifact — confirmed by
    multiple independent methods, not a single check.
- **Both MEDIUM fixes also independently hold**: MISS-003's lid-tab annular
  wall is genuinely ≥2.0mm on both axes with fastener coaxiality explicitly
  re-verified; MISS-004's engagement spare is a genuine +0.6mm with the
  tab's floor margin independently confirmed preserved, not silently
  traded away.
- **Tool-based cross-check**: `python3 tools/check_open_issues.py`
  independently confirms `validation/open-issues.md`'s current state is
  internally consistent with this verdict — "OK: no unresolved CRITICAL /
  unsigned-off HIGH findings (20 finding(s) checked)" — after this cycle's
  edits (MISS-001 through MISS-004 → RESOLVED, MISS-007 added as OPEN/
  MEDIUM, which does not trip this gate).
- **What's new and still open, non-gating**: MISS-007 (MEDIUM, new this
  cycle — D1-to-bay isthmus below `min_wall_t`). Consistent with this same
  document's Cycle 1 precedent (where MISS-003/MISS-004, both MEDIUM, were
  explicitly treated as "also open, non-gating" against a PASS-track
  verdict), an open MEDIUM finding does not block a clean PASS here. It
  should still be dispositioned (`RESOLVED`/`DEFERRED`/`ACCEPTED-RISK`)
  before Design Complete per `docs/architecture.md` §8.
  MISS-005/MISS-006 (LOW) remain untouched and out of scope this cycle, per
  the task's explicit instruction.
- **Next action**: No further Mechanical Lead rework loop is required for
  MISS-001/MISS-002/MISS-003/MISS-004, which are closed. Route MISS-007 to
  the Mechanical Lead (via the Hardware Lead) for disposition before Design
  Complete — recommended fix options are listed above; none require
  another full review cycle to evaluate once a choice is made, since the
  isthmus's own geometry is otherwise fully characterized.

---

## Cycle 3 — Rev 3 Motor Driver + Reaction Wheel subsystem, first review of this scope (2026-09-05)

### Review Cycle Metadata

- **Design revision reviewed**: `hardware/schematic/bench-imu-01-design.md`
  **Rev 3** (Author: Circuit Engineer (AI agent), commit `3e2c529`), together
  with its companion `hardware/power-budget.md` (finalized this revision
  with real motor-rail numbers). **This is a first review of new scope, not
  a re-review of a prior fix cycle.** Rev 2 (the MCU+IMU+Power board) already
  passed independent review across Cycle 1 and Cycle 2 above and reached
  Design Complete/human sign-off — **that content is explicitly out of
  scope for this cycle and is not re-litigated here.** This cycle's scope is
  the new Rev 3 addition only: the Motor Driver (TI DRV10983, U5) +
  Reaction Wheel (T-Motor MN2206-13 KV2000, M1) subsystem, added in a new
  §7.5, plus the necessary touches to §1, §2.1–§2.3 (rails/ground/pin
  allocation), §8 (grounding, rewritten), §9 (mechanical/thermal
  co-design, rewritten from N/A), §10, §11 (free-GPIO inventory), §12/§13
  (net/parts lists), §14/§15 (checklists), §16/§17 (UNKNOWNs/budget).
- **Reviewer**: Hardware Reviewer — see
  `.github/agents/hardware-reviewer.agent.md`. Independent of the Circuit
  Engineer session that authored Rev 3, and independent of the Hardware
  Lead session that previously mediated Rev 2 findings.
- **Independence statement**: I did not author this design, and I did not
  anchor on the Circuit Engineer's own rationale, the design document's own
  "RESOLVED"/"CORRECTED" self-annotations, or its own severity framing for
  either of the two items it explicitly flagged for Hardware Reviewer
  attention (§16 items 17–18). Every checklist item, both flagged items, and
  every one of the ten new Rev-3-specific self-flagged UNKNOWNs (§16 items
  11–21) were independently re-derived this cycle against primary sources —
  not accepted on the strength of the design document's or evidence-log's
  own citation formatting. **Primary sources fetched and read directly this
  cycle** (full-PDF text extraction via an `r.jina.ai` reader proxy, not
  merely HTML product-page summaries): TI DRV10983 datasheet (SLVSCP6H,
  Rev H, 59 pages — Pin Functions table, Absolute Maximum Ratings,
  Recommended Operating Conditions, Thermal Information, full Electrical
  Characteristics table including UVLO/SPEED-analog/SPEED-PWM/DIR-FG/I2C/
  OCP/Lock-Detection/BEMF rows, Table 8 Default EEPROM Value, Table 11
  External Components, Table 6 Current Limit Modes, and the full revision
  history back to the original 2014 release); ST STPS3L60 datasheet
  (DS2134 Rev 7, VF electrical characteristics); ST STM32G031x4/x6/x8
  datasheet (DS12992 Rev 4, Table 11/12/18 GPIO voltage-tolerance
  classification). Two independent research threads led to concrete,
  primary-source-grounded corrections/additions to `datasheets/
  evidence-log.md` this cycle (detailed in Findings below), rather than
  passively accepting its existing entries.
- **Scope**: The Rev 3 addition only, per the task's explicit instructions —
  full new §7.5 (all 8 subsections), plus every other section Rev 3 itself
  touched (§1, §2.1–§2.3, §8, §9, §10, §11, §12, §13, §14, §15, §16, §17),
  read in full directly (not just the changelog's summary of them), plus
  `hardware/power-budget.md` in full and the Motor/Motor-Driver-IC sections
  of `bom/component-selection.md` for context (component-selection itself
  already passed Checkpoint B and is out of scope; this review covers the
  circuit implementation built on top of those approved parts). Relevant
  Rev 3 requirements (REQ-007 through REQ-010, REQ-108 through REQ-112,
  REQ-204, REQ-307, REQ-403/404) were read directly in `requirements/
  requirements.md`, not taken on the design document's paraphrase.
- **Parallel sub-scans run**: None dispatched as separate sub-agent scans
  this cycle — worked as a single integrated pass across the full 16-item
  checklist, consistent with the agent instruction that the verdict is a
  single serial integration step owned by the Hardware Reviewer, not
  something to fragment into uncoordinated topic-based opinions.
  Investigation was organized around the two headline-flagged items first
  (independently re-derived from raw datasheet numbers before reading how
  the design document or evidence-log characterized them), then a full
  16-item checklist sweep of the new §7.5 content and everything else Rev 3
  touched.
- **rubber-duck premise review run in parallel?**: Not indicated as run for
  this cycle. No `rubber-duck`-sourced row is added to `validation/
  open-issues.md` this cycle; all new rows below are tagged
  `hardware-reviewer`.
- **KiCad tool cross-checks used**: None — `kicad-list_projects` was
  re-run fresh this cycle and returned an empty list (`[]`), independently
  reconfirming no KiCad project exists for this repository, matching
  established project convention. The Markdown schematic-equivalent
  document remains the correct artifact type to review net-by-net and
  pin-by-pin, as in Cycles 1–2.
- **Process-integrity check**: Independently ran `git log --oneline` and
  `git show --stat 3e2c529` to establish exactly which files the Rev 3
  commit touched, rather than relying on the design document's own
  changelog summary. Confirmed the commit modified: `bom/
  component-selection.md` (**exactly one hunk, 2 lines** — the OCP/Lock
  Detection naming correction only), `datasheets/evidence-log.md` (27
  lines), three new datasheet metadata files (Littelfuse SMBJ16A, Same Sky
  PJ-102AH, ST STPS3L60), one updated datasheet metadata file (STM32G031,
  20 lines), `datasheets/texasinstruments_drv10983_slvscp6h.md` (59 lines),
  `hardware/power-budget.md` (74 lines), `hardware/schematic/
  bench-imu-01-design.md` (1287 lines, the bulk of the change),
  `validation/change-impact-matrix.md` (13 new lines), and `validation/
  change-log.md` (1 new line). **This single-hunk confirmation on
  `bom/component-selection.md` is itself load-bearing evidence for Finding
  ISS-014 below** — it independently proves no corresponding update to the
  motor's cell-count guidance exists anywhere in the BOM despite the design
  document's own §16 item 17 flagging a practical 3S-only recommendation.
  `git log` also confirms no commit after `3e2c529` has touched `bom/`,
  `requirements/`, `hardware/power-*.md`, `datasheets/evidence-log.md`, or
  `validation/` other than this review's own two `evidence-log.md` edits
  made earlier this session (see Findings below).

### Checklist Results

Full 16-item checklist per `.github/skills/hardware-review/SKILL.md`, run
against the Rev 3 addition specifically (items 13 and 15 are genuinely live
for the first time in this project and were not treated as pro-forma):

| # | Checklist item | Result | Notes |
|---|---|---|---|
| 1 | Voltage violation | **Finding — ISS-014 (HIGH)** | The new VM_MOTOR rail (2S–3S LiPo per J4) combined with the new series reverse-polarity diode D2 creates a real voltage-margin violation against U5's UVLO rising threshold at the 2S end of the approved motor's rated range — independently re-derived from raw datasheet numbers (below), not accepted from the design document's own framing. All other new-rail voltages (U5's internal V1P8/V3P3/VREG regulator outputs, the 5 new MCU-domain GPIOs at 3.3V) independently check out with margin. |
| 2 | Absolute Maximum Rating violation | Pass — no live AMR violation found, independently reconfirmed | Directly re-read TI's AMR table this cycle: VCC −0.3…30V, SPEED/SCL/SDA/DIR −0.3…4V, V3P3/FG −0.3…4V, V1P8 −0.3…2.5V — all new-rail/new-pin voltages in this design (VM_MOTOR clamped ≤26.0V by D3, all MCU-domain GPIOs at 3.3V) sit inside these ceilings at every corner. ISS-014 above is a **regulation/UVLO-margin problem, not an AMR exceedance** — 2S undervoltage triggers U5's own protective auto-recovering shutdown, it does not stress any pin beyond its AMR. Also independently closed this cycle: STM32G031's PB6/PB7 FT_f 5V-tolerance family-generalization gap (design doc's own §16 item 12, MODERATE confidence) — ST DS12992 Rev4 Table 18 confirms a single `−0.3V to VDD+4.0V` rule applies uniformly across every FT_xx sub-variant (FT_f/FT_fa/FT_ea/etc.), closing this as a clean PASS (not that it changes any design decision, since this design only drives 3.3V-referenced logic regardless). |
| 3 | Current limit | Pass | U5's OCP is a fixed, non-configurable 3–4A phase-to-phase hardware threshold (independently re-confirmed via the Electrical Characteristics table's own `IOC_limit` row — MIN/MAX only, no TYP column, consistent with a fixed rather than tunable characteristic); `StAccel`/`OpenLCurr` ramp/current-limit settings additionally bound any commutation transient. `hardware/power-budget.md`'s motor-rail current figures (~1.05A nominal operating point, DS-MTR-054/056) are an order of magnitude below the AMR/OCP ceiling. |
| 4 | Thermal risk | Pass, with a tracked non-blocking gap (design doc's own §16 item 21) | RθJA=36.1°C/W independently reconfirmed via the primary Thermal Information table. Qualitative margin against the 125°C junction-temperature ROC ceiling is wide at the ~1.05A nominal operating point, but a precise worst-case wattage was not computed by either the design document or this review (would require U5's own RDS(on), not independently extracted from the primary datasheet this cycle either — the Electrical Characteristics table's `rDS(on)` row, 0.25 typ/0.4 max Ω at 25°C, 0.325Ω at 85°C, **was captured this cycle** and is available for a future precise-wattage pass, but no such pass was completed here). Reasonable-but-not-exhaustive treatment, consistent with a schematic-review-scope document; not a new finding beyond the design document's own honest flag. |
| 5 | Missing decoupling capacitor | Pass — independently confirmed exact match to TI's reference circuit | C10 (10µF, VCC–GND), C11 (0.1µF/10V, VCP–VCC), C12 (0.1µF≥VCCx2, CPP–CPN), R9 (39Ω, SW–VREG linear-mode), C13 (10µF/10V, VREG–GND), C14 (1µF/5V, V1P8–GND), C15 (1µF/5V, V3P3–GND) all independently checked against TI's own Table 11 "External Components" and match exactly — no omission. U5 is confirmed the plain DRV10983 (not the Z/sleep-mode variant), so no Zener/sleep-pin-specific component is applicable or missing. |
| 6 | Floating pin | **Findings — ISS-015 (HIGH) and ISS-016 (LOW)** | **SPEED** (U5 pin 13): floats during any window where the MCU domain has not yet driven PA8, with the factory-default register state (analog mode, see ISS-015 below) making this a live, not inert, condition — the checklist-item-6 trigger for ISS-015. **DIR** (U5 pin 14): independently confirmed via the primary Pin Functions table ("DIR 14 I Direction," no bias noted) and the Electrical Characteristics table's "DIGITAL I/O (DIR INPUT AND FG OUTPUT)" section (VDIR_H/VDIR_L logic thresholds only, no pulldown/pullup parameter of any kind, unlike SPEED's own RPD_SPEED_SL) that DIR has **zero internal bias of any kind, documented or otherwise** — confirming the design document's own §16 item 13 self-flagged concern is accurate, tracked as ISS-016 (LOW, per the design document's own reasonable severity framing, independently reconfirmed — see Findings). |
| 7 | Incorrect pull-up/pull-down | Pass (no incorrect value added) — cross-refs ISS-015/016 | No pull-up/pull-down was added on SPEED or DIR, matching TI's own Table 11 reference circuit exactly (TI's reference design does not bias these pins either). This is not an "incorrect value" finding — it is a case where TI's own reference circuit's implicit assumption (a single, always-alive host system already actively driving SPEED/DIR at power-up) does not hold for this design's dual-independent-power-domain (Option A) architecture; the consequence is captured under ISS-015/ISS-016 rather than logged again here. |
| 8 | Logic voltage mismatch | Pass | All five new MCU-domain GPIOs (PA8, PA6, PB1, PB6, PB7) are 3.3V-referenced STM32G031 pins. Independently re-confirmed via the primary DRV10983 Electrical Characteristics table that every digital input threshold on U5's interface side is compatible with 3.3V CMOS drive: DIR/PWM-SPEED `VDIG_IH`≥2.2V/`VDIG_IL`≤0.6V, I2C `VI2C_H`≥2.2V/`VI2C_L`≤0.6V — no level-shifting required in either direction. |
| 9 | Interface timing | Pass, with a tracked residual already correctly out of this document's scope | PWM SPEED frequency ROC (`fPWM` = 1–100kHz) independently confirmed compatible with a PA8/TIM1_CH1 driver; no specific numeric PWM frequency is committed in this schematic-only document, appropriately deferred to firmware. The FG/BEMF low-RPM signal-reliability caveat (§7.5.7) is correctly and explicitly deferred to Firmware/FMEA per the design document's own cited human ECO-007 directive — not re-litigated here, consistent with the task's scope instructions. |
| 10 | Power sequencing | **Finding — ISS-015 (HIGH)** | Cross-domain power-up sequencing between the MCU/IMU domain (U3) and the new independently-sourced motor domain (J4→D2→D3→U5, Option A) is not hardware-enforced — the design document's own §16 item 14 already flags this fact; this review's contribution is showing the risk is materially worse than the document's own mitigation argument allows for (see ISS-015 in Findings). |
| 11 | Grounding | Pass | §8 (rewritten this revision) correctly maintains a single shared ground net/plane across both the existing MCU/IMU domain and the new motor domain under Option A — independently re-read in full, no floating or split ground plane introduced. Physical-separation/star-point layout recommendations are appropriately deferred to the PCB-layout stage, consistent with this being a schematic-equivalent, pre-layout document. |
| 12 | EMI/EMC risk | Pass | REQ-401 ("No specific regulatory certification target... for this prototype/benchmark iteration... explicitly out of scope") is a blanket waiver of **formal emissions certification**, independently re-read in full this cycle — it is not scoped to exclude motor-related content, and is not stretched by the design document to excuse skipping real schematic-level noise mitigation: §8 already treats motor-commutation switching as a genuine (if bench-prototype-bounded) new noise source and recommends physical separation/grounding practice at the layout stage, which is the practical, proportionate mitigant at this document's own scope. No new finding warranted. |
| 13 | Motor noise (genuinely live for the first time this project — not treated as pro-forma) | Pass | Commutation/BEMF-related electrical noise is addressed at the appropriate schematic-review depth: §7.5.7 correctly defers the FG signal's low-RPM BEMF-derived reliability question to Firmware/FMEA per an explicit human ECO-007 directive (not re-litigated here), and §8's grounding/physical-separation recommendation is the general mitigant for commutation-switching noise coupling into the shared ground net. No PWM-line-radiation-specific mitigation is separately called out, but the low power level of this bench reaction-wheel application and the existing general layout mitigant are judged adequate at this document's own scope; no new finding. |
| 14 | Sensor noise (coupling risk from the new motor rail into the existing IMU) | Pass | Supply-noise coupling path independently ruled out via re-reading §5.5's regression check: VM_MOTOR is sourced independently of the IMU's own 3V3 rail (no shared regulator, Option A) — confirmed, not merely re-cited. The remaining path, ground-return coupling through the single shared ground net, is appropriately deferred to the PCB-layout stage per §8, consistent with this document's own scope; not a schematic-level defect. |
| 15 | PCB layout concern, incl. mechanical/thermal co-design near a rotating body (genuinely live for the first time this project — not treated as pro-forma) | Pass, with two tracked self-flagged research gaps (design doc's own §16 items 19–20, not separately logged as new Hardware-Reviewer findings — see Findings rationale) | §9 (rewritten this revision from Rev 2's N/A) correctly identifies M1 as a genuine rotating body and substantively addresses REQ-204 (vibration effect on IMU bias) and REQ-307 (vibration-isolation mount) at the depth appropriate for a schematic-only document, explicitly deferring actual mechanical mitigation to the Mechanical Lead. Cross-references ISS-015 below as the electrical-side trigger for exactly the uncontrolled-motion hazard this checklist item and REQ-403 are concerned with. |
| 16 | Datasheet recommendation violation | Pass | TI's Table 11 reference circuit is followed exactly for every decoupling/bias component actually populated (item 5 above). The one nuance — TI's own reference circuit also omits a SPEED/DIR bias resistor, an implicit single-always-alive-host assumption this design's architecture breaks — is framed as context for ISS-015/ISS-016 rather than a separate/duplicate violation, since TI's own recommended circuit would not have caught this either. |

### Findings

#### Flagged item 1 (design doc §16 item 18, §18.1) — OCP/Lock Detection mechanism-name correction — independently CONFIRMED CORRECT, already fixed, no new issue

- **Claim under review**: the design document asserts that `bom/
  component-selection.md`'s DS-MTR-037 entry mischaracterized DRV10983's
  overcurrent protection (OCP) as "programmable via I2C…auto-retry," when
  that description in fact belongs to the separate, genuinely configurable,
  auto-retry **Lock Detection** feature — OCP itself being a fixed,
  non-configurable, condition-based-clear hardware threshold.
- **Independent verification method**: re-read the primary DRV10983
  datasheet's own Electrical Characteristics table directly this cycle (not
  the design document's or evidence-log's paraphrase of it). The
  **"OVERCURRENT PROTECTION"** section lists exactly one row: `IOC_limit`,
  "phase to phase," MIN=3A / MAX=4A, **no TYP column** — a fixed
  accuracy-banded threshold with no register/field reference anywhere
  nearby, consistent with "fixed, non-configurable." The separate
  **"LOCK DETECTION RELEASE TIME"** section (`tLOCK_OFF`=5s,
  `tLCK_ETR`=0.3s) is a genuinely distinct set of parameters tied to a
  register-configurable feature (`HWiLimitThr[2:0]`, `LockEn[5:0]`, per
  §8.3.2.4/§8.4.7) with an explicit retry timer — a materially different
  mechanism from OCP's own instantaneous, condition-based-clear behavior.
  This independently reproduces, from the raw table structure itself
  (MIN/MAX-only vs. a named retry-timer parameter), the exact distinction
  the design document and DS-MTR-058/059 already draw — not merely
  re-trusting their prose.
- **Already-fixed status independently confirmed**: `bom/
  component-selection.md`'s current DS-MTR-037 citation (line ~734) reads
  "TI DRV10983 has overcurrent protection (OCP) — see `datasheets/
  evidence-log.md` DS-MTR-037/058/059 for the corrected mechanism
  attribution" — a correction consistent with the primary-source facts
  above. `datasheets/evidence-log.md`'s own DS-MTR-037 row carries an
  in-place "CORRECTED at Circuit Design, 2026-09-04" annotation (not a
  silent overwrite) citing DS-MTR-058/059 and `validation/change-log.md`
  ECO-008. Independently confirmed via `git show --stat 3e2c529` that this
  is the **only** change `bom/component-selection.md` received in the Rev
  3 commit (one hunk, 2 lines) — a clean, minimal, correctly-scoped fix
  with no collateral edits.
- **Conclusion**: **Confirmed correct and already fixed.** No new issue
  opened; REQ-111/REQ-404 remain satisfied (Lock Detection is the genuine
  configurable auto-retry response this design actually relies on, per
  §7.5.6). Full credit to the Circuit Engineer's own research (DS-MTR-058/
  059) and to the Hardware Lead's prior independent web-search confirmation
  for catching and correctly fixing this before it reached this review.

#### Flagged item 2 (design doc §16 item 17, §7.5.2) — 2S/3S UVLO margin via new diode D2 — independently CONFIRMED, severity independently assigned **HIGH** — logged as **ISS-014**

- **Claim under review**: the design document flags that the new series
  reverse-polarity protection diode D2 (STPS3L60) may push a 2S LiPo
  source below U5's UVLO rising threshold, recommending 3S-only operation
  in practice — but does **not** self-assign a severity, leaving that
  judgment explicitly to the Hardware Reviewer.
- **Independent re-derivation from raw datasheet numbers** (not accepted
  from the design document's arithmetic): D2's forward voltage,
  independently re-read from the primary STPS3L60 datasheet (DS2134 Rev 7,
  cited as DS-PROT-005): **VF = 0.53V typ (@3A/100°C) / 0.62V max
  (@3A/25°C)**. U5's UVLO thresholds, independently re-read from the
  primary DRV10983 Electrical Characteristics table (DS-MTR-057):
  **VUVLO_R (rising/power-up) = 7 / 7.4 / 8V (min/typ/max)**; **VUVLO_F
  (falling/dropout) = 6.7 / 7.1 / 7.5V (min/typ/max)**. The motor's own
  rated source range, independently re-read from `bom/
  component-selection.md` line 494: 2S = 7.4V nominal / 8.4V full-charge;
  3S = 11.1V nominal / 12.6V full-charge.
  - **2S at nominal voltage, typical corner**: 7.4V − 0.53V = **6.87V**,
    below VUVLO_R's own **typical** 7.4V threshold — meaning a 2S pack at
    or near its nominal voltage is expected to fail to power U5 up at all
    under **typical**, not just worst-case, conditions. This is a stronger
    conclusion than "marginal": a 2S pack spends most of its practical
    discharge life at or below nominal voltage, so this is a
    likely-to-fail, not rare-corner, condition.
  - **2S at full charge, worst-case corner**: 8.4V − 0.62V = **7.78V**,
    below VUVLO_R's own **max** 8V threshold — even a freshly-charged 2S
    pack can fail to clear UVLO at the pessimistic (max-VF, max-UVLO_R)
    corner.
  - **2S mid-discharge (≈7.0V, well above a normal ~6.0V/2-cell
    end-of-discharge cutoff)**: 7.0V − 0.53V = **6.47V**, below VUVLO_F's
    own **min** 6.7V falling threshold — meaning even a 2S pack that
    somehow did power up could drop out mid-operation during ordinary,
    non-critical discharge, not only at end-of-life.
  - **3S near-cutoff (≈9.0V, ≈3.0V/cell)**: 9.0V − 0.62V (max, pessimistic
    corner) = **8.38V**, clearing both VUVLO_R's max (8V) and VUVLO_F's max
    (7.5V) — 3S remains robust throughout its entire practical discharge
    range, at every corner.
  - **Conclusion**: this independently reproduces the design document's own
    headline number (≈6.87V) but goes further — the typical-2S-nominal case
    fails against the **typical** UVLO_R threshold, not only the worst-case
    corner, and a mid-discharge dropout mechanism exists independently of
    the power-up question. **2S is non-viable as a practical matter, not
    merely "marginal"; 3S is robust throughout.**
- **Cross-document inconsistency independently found** (beyond what the
  design document or `power-budget.md` each state in isolation): the design
  document's own §7.5.2 prose states **"only a freshly-charged 2S pack
  (~8.4V) clears UVLO with any margin"** — true only when checked against
  VUVLO_R's **typical** value (7.4V: 8.4−0.53=7.87V>7.4V ✓) but **false**
  against VUVLO_R's own **max** value (8V: 8.4−0.62=7.78V<8V ✗).
  `hardware/power-budget.md`'s own Rail Margin Summary row, addressing the
  identical freshly-charged-2S scenario, reaches the **opposite, more
  pessimistic** conclusion: **"even a freshly-charged 2S pack (~8.4V, minus
  drop ≈7.8V) sits under UVLO_R's max (8V)."** Both documents are part of
  the same Rev 3 revision, authored together — this is a narrow but real,
  independently-found internal inconsistency in how optimistically the
  identical scenario is framed across two same-revision documents, worth
  tightening even though it does not change either document's ultimate
  "3S-only" recommendation.
- **Traceability gap independently confirmed via `git show --stat
  3e2c529`**: `bom/component-selection.md`'s only Rev 3 change is the
  unrelated OCP/Lock Detection fix (flagged item 1 above) — **no
  corresponding update exists anywhere in the BOM** capturing that this
  circuit implementation (as opposed to the motor itself, which remains
  validly 2S–3S rated in isolation) now has a practical 3S-only
  constraint. `requirements/requirements.md` was independently grepped for
  any 2S/3S or cell-count constraint across every Rev 3 requirement
  (REQ-007–010, REQ-108–112, REQ-204, REQ-307, REQ-403/404) — **none
  exists**. A future reader consulting only the BOM or requirements (not
  the schematic document's own prose) would have no way to learn of this
  constraint.
- **Why HIGH, not CRITICAL**: per `docs/architecture.md` §7.1, CRITICAL is
  reserved for a design that "will fail... under normal/expected operating
  conditions **as designed**." This design's own practical recommendation,
  once this finding is heeded, is 3S-only operation — under which there is
  no failure at any corner. The failure mode only manifests if a 2S source
  is used despite that recommendation, which is a realistic corner (2S is
  within the originally-approved motor's own 2S–3S rated range, so an
  operator could plausibly reach for a 2S pack absent a clearly-propagated
  constraint) rather than the design's own intended condition — squarely
  HIGH's own framing ("likely malfunction... under realistic conditions/
  corners"). The failure mechanism itself (UVLO shutdown) is also
  protective and auto-recovering, not damage-causing, and has a
  zero-added-component-cost mitigation (use 3S) — mirroring this same
  file's own precedent for comparable HIGH (not CRITICAL) classifications
  (ISS-002, ISS-011).
- **Recommended Fix**: (1) Formally propagate the "3S-only" operational
  constraint into `bom/component-selection.md` (Motor/Motor-Driver-IC
  sections) and `requirements/requirements.md` (no current requirement
  captures a cell-count constraint) so it is discoverable outside the
  schematic document's own prose; and/or (2) if 2S support is genuinely
  required, have the Component Engineer evaluate a lower-VF reverse-polarity
  solution (e.g. an ideal-diode/ORing-FET circuit, which can achieve a
  near-zero voltage drop instead of a Schottky diode's ~0.5V) — noting the
  design document itself already correctly rules out simply swapping to a
  different Schottky, since VF/reverse-leakage/voltage-rating trade off
  against each other in that same component class. Either path is a
  bounded, well-scoped fix, not an open-ended rework.
- **Severity**: **HIGH**.

#### New finding (not one of the two originally-flagged items) — SPEED pin factory-default analog mode + unguaranteed cross-domain mitigation + no hardware-enforced power-up sequencing → uncommanded-motion risk tied to REQ-403 — logged as **ISS-015**

- **Independent discovery path**: investigating checklist items 6
  (floating pin) and 10 (power sequencing) together, given the design
  document's own §16 items 13–14 already flag SPEED/DIR bias and
  cross-domain sequencing as open, unresolved-by-hardware concerns. The
  design document's own mitigation argument (§7.5.5, quoted below) leans on
  SPEED's internal pulldown and on the assumption that the register bit
  selecting SPEED's interpretation is "functionally inert" before firmware
  configures it — both of which independent re-verification against the
  primary datasheet **do not fully support**.
- **Independent fact 1 — the factory-default SPEED interpretation is
  analog mode, not the PWM mode this design intends, and analog mode is
  fully active, not inert**: directly decoded Table 8 "Default EEPROM
  Value" in the primary DRV10983 datasheet: register 0x2B (SysOpt9)
  defaults to `0x0C` = binary `0000 1100`. SysOpt9's own documented bit
  layout is bits7:6=`FGOLsel`, bits5:4=`FGcycle`, bits3:2=`KtLckThr`,
  bit1=`SpdCtrlMd`, bit0=`CLoopDis` — decoding bit1 of `0x0C` gives
  **`SpdCtrlMd`=0 = analog mode** (not PWM mode, which requires
  `SpdCtrlMd`=1 and is only reached once firmware performs an I2C/EEPROM
  write, an explicitly out-of-scope firmware/commissioning task per
  REQ-009's own scope fence). §8.4.5.2 "Analog Mode Speed Control"
  independently confirms analog mode is **fully active out of reset**, not
  inert: "If SPEED > VANA_FS, the speed command is maximum. If VANA_ZS ≤
  SPEED < VANA_FS the speed command changes linearly... If SPEED < VANA_ZS
  the speed command is to stop the motor" (VANA_FS=V(V3P3)×0.9,
  VANA_ZS=100mV). This independently corrects `datasheets/
  evidence-log.md`'s own pre-existing DS-MTR-068 entry, whose closing
  phrase asserted SPEED is "functionally inert until this register is
  configured as PWM mode" — inaccurate for the factory-default (analog)
  state, which is exactly the state U5 is in during any uncommissioned
  window. **This evidence-log inaccuracy has been corrected this cycle**
  (see the Evidence-log correction note below) and a new evidence row
  (DS-MTR-071) added recording the Table 8/§8.4.5.2 primary-source facts.
- **Independent fact 2 — the design document's own cited mitigant (SPEED's
  internal pulldown) is documented under a test condition, and a device
  variant, this design does not clearly satisfy**: the design document's
  own §7.5.5 already honestly discloses that `RPD_SPEED_SL` (an internal
  55kΩ typ SPEED-to-ground pulldown, DS-MTR-069) is "specifically...
  confirmed for the device's sleep-mode state, not asserted as a universal
  always-on default-safe bias in every power/reset condition" — correctly
  distinguishing "sleep mode" from "post-power-on, pre-firmware-init."
  Independent re-verification this cycle goes one step further and finds
  an additional gap the design document does not itself identify: in the
  primary datasheet's own Electrical Characteristics table, the
  `RPD_SPEED_SL` row is listed under the section header **"SLEEP MODE
  (DRV10983Z)"** — i.e. this parameter is textually grouped with, and only
  characterized alongside, the sleep-capable **DRV10983Z** variant's other
  sleep-mode timing parameters (`VEN_SL`, `VEX_SL`, `tEX_SL_ANA`, etc.).
  This design specifies the **plain DRV10983** (independently re-confirmed
  earlier this cycle via the design document's own parts list — no
  Zener/sleep-pin component populated), which has its own separate
  "STANDBY MODE (DRV10983)" section in the same table — and that section
  does **not** list any internal-SPEED-pulldown parameter at all. This is
  a genuine documentation/guarantee gap (TI's datasheet does not specify or
  guarantee this pulldown's value, or even confirm its presence, for the
  plain DRV10983 outside the Z-variant's sleep-mode test condition) — a
  more specific, independently-found weakening of the design document's own
  mitigation argument, stated with appropriate hedging (this does not prove
  the physical pulldown structure is absent on the plain part's silicon,
  since product variants in one package/pinout are often the same die with
  different firmware-configured feature sets — only that the datasheet does
  not document or guarantee it for the part actually specified).
- **Independent fact 3 — no supervisory gating exists, so the
  uncommissioned window is not bounded to be transient**: independently
  re-confirmed via the design document's own §13 parts list and §7.5.3 that
  the DRV10983 has **no dedicated EN or FAULT pin at all** — SPEED is the
  *only* on/off control surface on this device. D2/D3 (the new
  reverse-polarity/TVS protection on the motor rail) are both passive; no
  supervisory load switch gates U5's own VCC based on the MCU domain's
  power state. Because J1 (USB/MCU domain) and J4 (motor domain) are
  physically separate connectors under Option A with no documented required
  connection order enforced anywhere outside this schematic's own prose,
  the "uncommissioned" window (U5 powered, MCU either not yet powered or
  not yet finished with GPIO/I2C init) is not guaranteed to be short — it
  could persist indefinitely if, for example, a bench operator connects J4
  well before J1.
- **Failure mechanism**: if U5's VCC is energized before the MCU domain has
  actively driven PA8 (SPEED) low and/or completed the `SpdCtrlMd`=1 I2C
  commissioning write, U5 runs in its factory-default analog mode with an
  unbiased SPEED input. Any leakage, capacitive coupling, or other stray
  voltage appearing on SPEED that exceeds `VANA_ZS`=100mV is interpreted as
  a real, proportional, non-zero commanded speed (per §8.4.5.2's own
  transfer function above) — commutating M1 (a reaction-wheel rotor) using
  whatever generic Rm/Kt values happen to be in EEPROM (DS-MTR-070), since
  the actual T-Motor-specific values are also a firmware/commissioning task
  not yet performed in this window. This is exactly the uncommanded/
  uncontrolled rotor motion class of hazard REQ-403 (safety-critical,
  human-review-gated) is written to prevent.
- **Bounding factors honestly acknowledged (why this is HIGH, not
  CRITICAL)**: this is a plausible, evidence-grounded, but not
  deterministic failure chain — it depends on (a) a specific, non-default
  bench power-up ordering (motor domain live before or independent of the
  MCU domain; the reverse ordering, USB/MCU-first, is at least as plausible
  a bench workflow and is unaffected), (b) an unmeasured real stray voltage
  on SPEED actually clearing the 100mV threshold, and (c) the resulting
  motion is explicitly ramped and current-limited (`StAccel`/`OpenLCurr`,
  Table 6) rather than an instantaneous full-speed event, and would be
  running on generic (not motor-matched) commutation parameters, which
  bounds — without eliminating — the realistic severity of the outcome.
  This conditional, multi-factor-dependent character is squarely
  consistent with HIGH's own definition ("likely malfunction... under
  realistic conditions/corners") rather than CRITICAL's deterministic
  framing (exceeding an AMR, a reverse-voltage path that kills a part) —
  and is, if anything, a **less certain** failure chain than this
  project's own existing HIGH-classified precedent (ISS-011, a 100%
  guaranteed total interface failure under the stated conditions), which
  still did not warrant CRITICAL.
- **Recommended Fix**: given REQ-403's own explicit requirement that
  "final disposition... requires explicit human review before this cycle's
  Design Complete Gate," this finding should be routed for that human
  safety review regardless of which technical path is chosen. Concrete
  options for the Circuit Engineer to evaluate: (1) add a real external
  pulldown on SPEED sized to dominate over any realistic leakage/coupling
  and firmly hold SPEED below `VANA_ZS` whenever the MCU domain is not
  actively driving it — a deliberate, justified deviation from TI's own
  Table 11 reference circuit, since that reference circuit implicitly
  assumes a single always-alive host system this design's architecture does
  not have; (2) add a supervisory load switch gating U5's own VCC,
  sequenced to enable only once the MCU domain's own rail is confirmed
  alive, directly enforcing the missing cross-domain ordering (design
  document's own §16 item 14); or (3), as a documentation/process-only
  mitigation of last resort, explicitly specify a required operator
  power-up order and have firmware drive SPEED to a safe state at the
  earliest possible init step — noted as a weaker mitigant than either
  hardware option given REQ-403's safety-critical classification.
- **Severity**: **HIGH** (ties directly to REQ-403; recommend explicit
  escalation to human safety review given the direct safety-requirement
  tie, independent of the HIGH/CRITICAL severity-tier classification
  itself).

#### New finding — DIR floating during MCU reset/init window — logged as **ISS-016**

- **Issue**: DIR (U5 pin 14, direction-select input) has no internal or
  external bias and is not proven safe while floating during the brief
  window before the MCU's own GPIO init completes.
- **Independent verification**: confirmed directly against the primary
  DRV10983 Pin Functions table ("DIR | 14 | I | Direction" — no bias
  noted) and the Electrical Characteristics table's "DIGITAL I/O (DIR
  INPUT AND FG OUTPUT)" section, which lists only `VDIR_H`≥2.2V/
  `VDIR_L`≤0.6V logic thresholds — no pulldown/pullup parameter of any
  kind is documented for DIR anywhere in the datasheet (unlike SPEED,
  which at least has a partial, if caveated, `RPD_SPEED_SL` citation).
  This independently confirms the design document's own §16 item 13
  self-flagged claim ("DIR has no internal bias documented in the
  datasheet") is accurate, not merely asserted.
- **Rationale**: an undriven digital input can settle to an indeterminate
  logic level via leakage or coupling, risking a nondeterministic direction
  selection at first spin-up.
- **Datasheet Source**: DS-MTR-069 (DRV10983 DIR/FG/I2C digital I/O
  characteristics, Pin Functions table).
- **Failure Mechanism**: floating CMOS-style digital input settles to an
  indeterminate state under leakage/coupling; if U5 begins commutating
  before PB1 (MCU's DIR driver) is initialized, the resulting rotation
  direction is unpredictable on that specific spin-up.
- **Affected Component**: U5 (DRV10983) DIR pin; U1 (STM32G031K8T6) PB1.
- **Recommended Fix**: as the design document itself notes, TI's own Table
  11 reference circuit does not bias DIR either, so no datasheet-recommended
  component exists to add; this is best addressed at the firmware level
  (initialize PB1 to a known state as early as possible in the boot
  sequence, before U5's own VCC ramp/EEPROM load can plausibly complete) or
  accepted as a low-severity residual, since an indeterminate *direction* at
  first spin-up (as opposed to an indeterminate *speed*, ISS-015) is a
  narrower, lower-consequence hazard for a reaction-wheel application.
- **Severity**: **LOW** — bounded consequence (direction ambiguity only,
  not an uncommanded-motion trigger on its own) and no datasheet-recommended
  hardware fix exists to omit.

#### New finding — J4 (PJ-102AH) third terminal function unconfirmed — logged as **ISS-017**

- **Issue**: J4's datasheet-derived metadata record shows a 3-terminal
  barrel-jack drawing (center pin + 2 outer contacts), consistent with a
  normally-closed switch-contact design common in this connector class, but
  the specific page fetched this session did not unambiguously label which
  outer terminal is the switch contact vs. sleeve/GND. This design uses the
  center pin (+) and one outer terminal (assumed sleeve/GND); the third
  terminal is left unpopulated with its exact function unconfirmed.
- **Independent verification**: reviewed `datasheets/
  metadata` for PJ-102AH (DS-CONN-005)'s own "Known gaps" section, which
  honestly discloses this exact gap — independently confirmed no
  contradicting or clarifying information exists elsewhere in this
  design's own citations.
- **Rationale**: leaving an unidentified switch-contact terminal
  unpopulated is a safe default (it simply never activates whatever it
  would have controlled), but the ambiguity should be closed before layout
  commits to a specific footprint/pad assignment for that third terminal.
- **Datasheet Source**: DS-CONN-005 (Same Sky PJ-102AH metadata record,
  "Known gaps" section).
- **Failure Mechanism**: none under the current as-designed use (an
  unpopulated switch contact is inert); the risk is purely that a
  future/different assumption about which outer terminal is which could be
  wrong if this is revisited without re-confirming against the connector's
  own internal schematic.
- **Affected Component**: J4 (Same Sky PJ-102AH).
- **Recommended Fix**: obtain and read the connector's own internal
  schematic diagram (not just its external dimensional drawing) before PCB
  layout to confirm terminal identity with certainty.
- **Severity**: **LOW** — no current functional or safety consequence;
  pre-layout confirmation item only.

#### New finding — `datasheets/evidence-log.md` DS-MTR-059 internal inconsistency (states "5" sub-schemes, enumerates and cites a 6-bit field for 6) — logged as **ISS-018**

- **Issue**: `datasheets/evidence-log.md`'s own DS-MTR-059 entry states Lock
  Detection has "**5** independently-maskable sub-schemes," then itself
  enumerates six: Lock0 (current-limit), Lock1 (abnormal speed), Lock2
  (abnormal Kt), Lock3/Fault3 (no-motor-detected), Lock4 (open-loop-stuck),
  Lock5 (closed-loop-stuck) — and cites a 6-bit field, `LockEn[5:0]`, which
  itself implies 6 independently-maskable bits, not 5.
- **Independent verification**: directly counted the entry's own
  enumerated list (six named sub-schemes) against its own prose ("5") and
  its own cited register-field width (`[5:0]` = 6 bits) — a purely
  internal inconsistency within one evidence-log row, not a datasheet
  citation error (the design document's own §7.5.6 protection table
  correctly states "6" and is unaffected).
- **Rationale**: a future reader relying on the evidence-log's own prose
  count ("5") rather than its enumeration or register-field citation could
  under-count the protection scheme, though no design decision in this
  revision is actually affected (the design document's own count is
  already correct).
- **Datasheet Source**: DS-MTR-059 (its own text, self-inconsistent).
- **Failure Mechanism**: none — a documentation/proofreading defect with
  no electrical or functional consequence, since the design document itself
  (the artifact actually used for engineering decisions) already states the
  correct count.
- **Affected Component**: N/A (`datasheets/evidence-log.md` documentation
  only).
- **Recommended Fix**: correct DS-MTR-059's prose from "5" to "6"
  independently-maskable sub-schemes to match its own enumeration and cited
  6-bit field.
- **Severity**: **LOW** — style/documentation-accuracy nitpick, zero
  functional or design-decision impact.

#### Evidence-log correction made this cycle (not a `validation/open-issues.md` row — a datasheet-citation correction, following the established DS-MTR-037 precedent)

Independent research into ISS-015 (above) surfaced a genuine, primary-source-
verifiable inaccuracy in `datasheets/evidence-log.md`'s own pre-existing
**DS-MTR-068** entry (authored during the Rev 3 design cycle, before this
review): its closing clause asserted the SPEED pin is "functionally inert
until this register is configured as PWM mode." This is inaccurate — the
factory-default (analog-mode) state is not inert (§8.4.5.2, quoted in
ISS-015 above). Following this file's own established precedent for
qualifying rather than silently overwriting a prior entry (the existing
DS-MTR-037 "CORRECTED at Circuit Design" annotation), this cycle:

1. Appended an in-place **"QUALIFIED at Hardware Review, 2026-09-05"**
   annotation to the existing DS-MTR-068 row, explaining the inaccuracy,
   citing the new DS-MTR-071 evidence and this file's own ISS-015, and
   updating the Researcher/Date columns — the original text is preserved,
   not deleted, so the citation's history stays auditable.
2. Added a **new DS-MTR-071 row** (after DS-MTR-070) recording the primary
   Table 8 EEPROM-default decode and §8.4.5.2 analog-mode transfer function
   directly, attributed to "Hardware Reviewer (AI agent), 2026-09-05."

Both edits were verified structurally sound (consistent 9-field column
count matching every other row) before this report was written. This is
the only content edit made outside `validation/design-review.md` and
`validation/open-issues.md` this cycle, and is explicitly within this
agent's granted scope for "a genuine additional evidence-log inaccuracy...
the same way the existing Cycle 2 precedent did."

#### Items independently checked and closed this cycle with no new finding (beyond what the checklist table above already states)

- **PB6/PB7 FT_f 5V-tolerance family generalization** (design doc's own
  §16 item 12) — independently closed as a clean PASS via ST DS12992
  Rev4 Table 18 (see checklist item 2 above).
- **DRV10983 I2C address not extracted** (design doc's own §16 item 16) —
  independently agree with the design document's own self-assessment that
  this is correctly non-circuit-relevant: only one I2C1 slave exists on
  this segment, so no address conflict is possible regardless of the
  address's actual value. No finding.
- **U5 precise worst-case wattage/RDS(on)** (design doc's own §16 item 21)
  — independently attempted to close this gap this cycle by pulling
  RDS(on) directly from the primary Electrical Characteristics table
  (0.25 typ/0.4 max Ω @ 25°C, 0.325Ω @ 85°C — now available, see checklist
  item 4), but did not complete a full worst-case-wattage calculation this
  cycle. Tracked as a residual, non-blocking gap, consistent with the
  design document's own honest framing — not elevated to a new finding.
- **BMI270 bias-vs-temperature coefficient not extracted, and M1's full
  mechanical outline/mass/mounting pattern not pulled** (design doc's own
  §16 items 19–20, §9) — reviewed and agree these are genuine residual
  research gaps, but they are **prerequisites for a future Mechanical Lead
  engagement with M1's actual mount/enclosure design**, not
  electrical/schematic-level defects in this document, and no mechanical
  design for M1 yet exists for a Mechanical Reviewer to check against.
  Deliberately **not** logged as new `hardware-reviewer`-tagged ISS rows —
  doing so would overreach this review's own electrical/schematic scope
  and risk being relabeled or duplicated once the Mechanical Lead/Mechanical
  Reviewer actually engages with M1. Tracked here by direct cross-reference
  to the design document's own §16 items 19–20 instead.

### Verdict

- **Verdict**: **CONDITIONAL** (not a clean PASS, and not a FAIL — see
  "what's blocking" below for why this is a routing decision, not a rework
  dead-end)
- **Open CRITICAL count**: 0
- **Open HIGH count**: 2 (ISS-014, ISS-015 — both newly opened this cycle)
- **Open MEDIUM count**: 0 (this cycle)
- **Open LOW count**: 3 (ISS-016, ISS-017, ISS-018 — all newly opened this
  cycle)
- **Both originally-flagged headline items, independently resolved**:
  Flagged item 1 (OCP/Lock Detection naming) is **confirmed correct and
  already fixed** — no open issue. Flagged item 2 (2S/3S UVLO margin) is
  **confirmed accurate and, if anything, understated** by the design
  document's own optimistic framing at one corner — now logged as ISS-014,
  independently assigned **HIGH** (the design document explicitly left
  severity assignment to this review).
- **What's blocking a clean PASS, precisely**: ISS-014 and ISS-015. Both
  have a clear, bounded, well-scoped recommended-fix path (documentation/
  requirements propagation or a lower-VF protection topology for ISS-014;
  an external SPEED pulldown, a supervisory VCC gate, or a
  documentation/firmware mitigation for ISS-015) — this is not open-ended
  further engineering exploration, but neither is it a already-settled
  human-sign-off-only question the way Cycle 2's ISS-002 was. ISS-015
  additionally ties directly to REQ-403's own explicit human-review gate
  and should be routed there regardless of which technical mitigation is
  chosen.
- **What independently checks out (no further engineering action needed)**:
  the OCP/Lock Detection naming correction (flagged item 1) is fully closed.
  All decoupling/bias components for U5 exactly match TI's Table 11
  reference circuit. No AMR violation exists anywhere in the new Rev 3
  content. Grounding, current-limit, and thermal treatment are all sound at
  this document's own schematic-review scope. The PB6/PB7 FT-tolerance gap
  the design document itself flagged as MODERATE confidence is now
  independently closed as PASS.
- **Next action**: Route ISS-014 and ISS-015 back to the Circuit Engineer
  (via the Hardware Lead) for rework, per the Recommended Fix options
  above. Given ISS-015's direct REQ-403 tie, also flag it explicitly for
  human safety review at or before the next Design Complete Gate attempt
  for this subsystem, independent of whichever technical mitigation the
  Circuit Engineer implements. ISS-016/017/018 (LOW) do not block progress
  but should still receive an explicit disposition
  (`RESOLVED`/`DEFERRED`/`ACCEPTED-RISK`) before this subsystem's own
  Design Complete, per `docs/architecture.md` §8. No further review-cycle
  ambiguity exists on the two originally-flagged items — both are now
  independently dispositioned (one closed, one severity-assigned and
  logged) and do not require another look before a Circuit Engineer rework
  pass addresses ISS-014/ISS-015 specifically.

## Cycle 3 — Rubber-duck premise/assumption review (same Rev 3 handoff, 2026-09-05)

Run per `docs/architecture.md` §5.1, in addition to (not instead of) the
Hardware Reviewer checklist pass immediately above — same artifact, a
deliberately different lens (design premises/blind spots, not checklist
execution). Formed an independent view first before cross-checking against
the Hardware Reviewer's own Cycle 3 findings, per this project's own
established practice (the same practice that caught ISS-011 in Rev 2, when
a checklist-only pass had missed it).

### Premises specifically checked, and confirmed to hold

- **REQ-009's open-loop-only scope fence**: checked whether the I2C1
  commissioning bus, FG reporting, or U5's own internal BEMF-based
  commutation smuggle in control-loop-flavored thinking despite the
  explicit scope fence. They do not — I2C1 configures static motor
  parameters (Rm/Kt) and a control-mode register, not a runtime control
  loop; U5's internal commutation is the driver IC's own normal operating
  function, not this project's control logic. REQ-009 remains intact.
- **Option A's fault-isolation intent**: the design document is honest that
  Option A provides rail-level (not galvanic) isolation, and that the two
  domains deliberately share a ground/signal reference — this matches
  `hardware/power-architecture.md`'s own stated intent exactly, not an
  overclaim.
- **The four human-confirmed provisional defaults** (reaction-wheel target,
  no motor-type preference, budget ceiling, bare-bench-rig sizing): the
  approved motor+driver pairing and architecture have not silently drifted
  from any of these — no disagreement found. The gap found (ISS-020) is
  that the *target* itself (a floor) was never separately converted into a
  *maximum/safety envelope*, which is a different, additional question the
  original four never asked, not a violation of what was asked.

### New findings (see `validation/open-issues.md` for the full schema each)

- **ISS-019 (HIGH)** — New motor input (J4) has no bounded source envelope
  or coordinated upstream fault containment; every component in its path
  tolerates far more voltage/current than the recommended motor is
  actually qualified for. Complements ISS-014 (which is about the input
  sagging too *low*) with the upper-bound/source-fault-envelope gap.
- **ISS-020 (HIGH)** — The approved "≥3000 RPM" target has only ever been
  treated as a functional floor, never converted into a bounded maximum/
  safety envelope for commanded speed, acceleration, or mechanical
  containment. A genuine premise-challenge finding: neither Requirements
  Engineering, Component Selection, nor Circuit Design ever asked "what is
  the *maximum* speed this design must tolerate/survive," only "what is
  the minimum it must reach." Directly compounds ISS-015 (that finding is
  about *unintended* motion at power-up; this one is about *unbounded*
  motion even during normal, intended operation).
- **ISS-021 (HIGH)** — REQ-404's "shutdown behavior to prevent sustained
  overheating" is not actually satisfied by DRV10983's Lock Detection
  alone — all three of U5's own protection mechanisms (OCP, Lock
  Detection, Thermal Shutdown) are auto-recovering/auto-retrying, not
  latching. Directly challenges whether REQ-404 *as currently implemented*
  is satisfied, a different and sharper question than whether the
  mechanisms merely *exist* (which Hardware Reviewer's Cycle 3 pass already
  confirmed).
- **ISS-022 (MEDIUM)** — FG does not always represent actual RPM (can
  reflect commanded/drive frequency during open-loop startup); ECO-007's
  human directive to track the BEMF-degradation caveat in Firmware/FMEA is
  not yet fulfilled — appropriately, since neither phase has run yet this
  cycle. Recorded as a checkpoint, not a new circuit-level defect.
- **ISS-023 (MEDIUM)** — Rev 2's "no vibration/shock, single simple rail"
  validation-artifact premise (`validation/bring-up-procedure.md`,
  `validation/fmea.md`) has not yet been updated for the new subsystem —
  expected to be addressed at this cycle's own planned validation-artifact
  closeout phase, flagged here so it is not silently skipped.

### Cross-check against Hardware Reviewer's Cycle 3 findings

- **Agree, not duplicated**: ISS-014 (2S UVLO) and ISS-015 (unsafe
  uncommissioned SPEED/power-up state) — reviewed independently, no
  disagreement with severity or substance.
- **Distinct additions**: ISS-019/020/021/022/023 above are genuinely new,
  not restatements.
- **No disagreement** with ISS-016/017/018's LOW classification.

### Verdict contribution

- This pass does not issue a separate consolidated verdict (per
  `docs/architecture.md` §4: exactly one Reviewer pass owns the
  consolidated verdict — Hardware Reviewer's own Cycle 3 verdict,
  above, stands as the single verdict for this cycle) — but adds 3
  further open HIGH findings (ISS-019, ISS-020, ISS-021) to the 2
  Hardware Reviewer already opened (ISS-014, ISS-015), for **5 open HIGH,
  0 open CRITICAL** heading into Circuit Engineer's rework pass, plus 2
  further MEDIUM (ISS-022, ISS-023) tracked as checkpoints for later
  phases (Firmware Bring-up, validation-artifact closeout) rather than
  blocking Circuit Design rework specifically.
- **Next action**: all 5 open HIGH findings (ISS-014, 015, 019, 020, 021)
  route back to Circuit Engineer for rework before a fresh re-review.
  ISS-015 and ISS-020 both tie to REQ-403's safety-critical human-review
  gate regardless of technical mitigation chosen.

## Cycle 4 — Rev 5 re-review (U6 Motor-Rail Supervisory Controller): independently re-verifying closure of the 5 open HIGH findings from Cycle 3 (2026-09-08)

### Review Cycle Metadata

- **Design revisions reviewed**: `hardware/schematic/bench-imu-01-design.md`
  **Rev 4** (commit `7774d4f`, "Circuit rework Rev 4: address 5 HIGH
  findings from Independent Review Cycle 3") and **Rev 5** (commit
  `4c812ad`, "Circuit rework Rev 5: wire in TPS26631PWPR supervisory
  controller"), together with the intervening **Hardware Lead mediation**
  (commit `9410a9d`, "Hardware Lead mediation + Motor-Rail Supervisory
  Controller selection") and **human Chief Engineer approval record**
  (commit `43b3c90`, "Record human approval of TPS26631PWPR supervisory
  controller"). **This is a re-review, not a first review** — per this
  role's own skill guidance, scope is the changed areas since my own prior
  Cycle 3 pass, and anything those changes could affect, not the whole
  document from scratch. Rev 1–3 content already passed independent review
  in Cycles 1–3 and is not re-litigated here except where Rev 4/5 changed
  it (ISS-014's §7.5.2 rewrite) or where a Rev-5 addition creates a new
  interaction with it (U6 sitting electrically between the existing
  F1→D2→D3 stage and U5).
- **Reviewer**: Hardware Reviewer — see
  `.github/agents/hardware-reviewer.agent.md`. Independent of the Circuit
  Engineer session(s) that authored Rev 4/5, the Hardware Lead session that
  mediated ECO-010, the Component Engineer session that selected U6, and
  the human Chief Engineer who approved it. This is the same reviewer role
  that opened ISS-014/015 at Cycle 3; I did not treat my own prior findings
  as self-evidently satisfied by the design document's "RESOLVED"
  self-annotations and re-derived each one from scratch this cycle (see
  Findings). For ISS-019/020/021 — opened by the parallel rubber-duck pass
  at Cycle 3, not by me — I gave them the same independent, ground-up
  scrutiny as my own findings, not a lighter pass merely because I did not
  originally author them.
- **Independence statement**: Every numeric/technical claim in Rev 5's new
  §7.5.10 (U6) was re-derived this cycle directly against the **primary TI
  TPS2663x datasheet** (SLVSE94G, Sept 2018 – revised June 2024), fetched
  fresh this cycle via `curl` (5.6 MB PDF) and text-extracted via
  `pdftotext -layout` to a local working copy (`/tmp/tps2663.txt`, 3532
  lines) — not accepted from the design document's or evidence-log's own
  citation/paraphrase. This includes: the SHDN pin's guaranteed leakage
  spec and thresholds (§8.3.13, Table 5-1, Electrical Characteristics),
  the UVLO/OVP divider equations (§9.2.2.2, Equations 9–10) and all six
  resulting trip-point corners (recomputed independently from the design's
  actual R12/R13/R14 values, not copied from the design document's own
  numbers), the R(ILIM) equation (§9.2.2.1, Equation 8) and R15 sizing, the
  dV/dt inrush and turn-on-delay equations (§8.3.1, Equations 1–2, Figure
  8-3) against the design's actual C(OUT)=10µF, the Thermal Information
  table (RθJA, R(ON), IQ) and the full ΔTJ margin arithmetic, the
  Absolute Maximum Ratings and Recommended Operating Conditions tables
  (§6.1/§6.3, re-pulled fresh this cycle to independently confirm zero new
  AMR/ROC exposure — see Checklist item 2), and Table 8-1 (Device
  Operational Differences Under Different MODE Configurations) confirming
  MODE=Open→Latch-off specifically for the TPS26631 variant used here. One
  sub-claim — the STM32G0 GPIO reset-default state, relevant to a new
  question this cycle raised about PA9's pre-init state — could not be
  verified against a locally-extractable primary PDF within this cycle's
  tooling and was instead independently corroborated via `web_search`
  against ST Community forum posts and ST's own public GPIO training
  material; this is disclosed as a secondary-source verification, weaker
  than the PDF-extraction method used for every other claim in this cycle,
  and is flagged as such rather than silently presented with equal
  confidence (see Finding: ISS-015 below).
- **Scope**: Per the task's explicit framing, this cycle re-ran the
  checklist against the changed areas and anything they could affect, not
  the whole document from scratch: the Rev 4/5 "Revision changelog" entries
  themselves (top of file), §7.5.2 (ISS-014 rewrite), §7.5.5 (ISS-015/R10),
  §7.5.9 (ISS-019/F1), §7.5.10 (U6, entirely new this revision — read in
  full), §7.5.11 (ISS-020), §7.5.12 (ISS-021), §11 (MCU pin table — PA9
  commitment), §12 (net list — all new U6 nets), §13 (parts list — U6,
  R11–R15, C16/C17), §14/§15 (self-check sections, including the
  Rev-5-specific re-self-check), and §16 (residual items, specifically the
  three newly-added items 27–29 this task called out for an independent
  view, plus items 25/26 for context on ISS-020/021/019's own residuals).
  Also read directly (not paraphrased): `validation/change-log.md`
  ECO-009/010/011; `validation/open-issues.md` ISS-014/015/019/020/021 full
  rows (all 13 fields); `bom/component-selection.md`'s "Motor-Rail
  Supervisory Controller" section in full (Component Engineer comparison,
  Hardware Lead concurrence, and the human Chief Engineer's own approval
  note, including the independent ≈440kΩ SHDN-pull-up figure the human's
  own fresh web search produced); `requirements/requirements.md` REQ-108,
  REQ-403 through REQ-406 in full.
- **Parallel sub-scans run**: None dispatched as separate sub-agent scans
  this cycle. Per this role's own agent instructions, topic-based
  sub-scans (power/thermal, interface/timing, protection/EMI) may run in
  parallel, but the five re-assessments were tightly evidentially coupled
  (all hinge on the same U6 part and the same primary datasheet) and were
  worked as a single integrated pass, consistent with the verdict being a
  single serial integration step this role owns.
- **rubber-duck premise review run in parallel?**: Not run this cycle. Per
  `validation/open-issues.md`'s own Rules ("never merge/relabel" a row's
  Source), ISS-019/020/021's `Source` column remains `rubber-duck`
  unchanged in the updates below even though this Hardware Reviewer cycle
  is the one re-assessing and transitioning their disposition — the
  Hardware Lead's own mediation commit (`9410a9d`) independently confirmed
  this same division of labor in its own commit message ("validation/
  open-issues.md ISS-014/015/019/020/021 statuses are intentionally left
  OPEN by this commit — only Hardware Reviewer's own re-review transitions
  finding status").
- **KiCad tool cross-checks used**: `kicad-list_projects` re-run fresh this
  cycle, still returns `[]` — independently reconfirming no KiCad project
  exists for this repository. The Markdown schematic-equivalent document
  remains the correct artifact reviewed net-by-net (§12) and pin-by-pin
  (§11/§13), as in Cycles 1–3.
- **Process-integrity check**: Independently ran `git log --oneline` and
  `git show --stat` on all four relevant commits rather than relying on
  the design document's own changelog summary or the task's framing of
  "Rev 4"/"Rev 5" as monolithic units:
  - `7774d4f` (Rev 4) touched only `datasheets/
    littelfuse_30r500u_rev-unknown.md` (new), `hardware/power-budget.md`,
    and `hardware/schematic/bench-imu-01-design.md`. **It did not touch
    `bom/component-selection.md` or `requirements/requirements.md`** —
    meaning the design document's claim that ISS-014's constraint is
    "propagated" into those two files is **not** attributable to the Rev 4
    commit itself.
  - `9410a9d` ("Hardware Lead mediation…", same day, between Rev 4 and Rev
    5) is the commit that actually performed that propagation — its own
    message states this explicitly ("Propagated ISS-014's confirmed
    3S-only binding constraint into `bom/component-selection.md`… and
    `requirements/requirements.md` (REQ-108)"), and its diffstat confirms
    341 new lines in `bom/component-selection.md` and a 4-line change in
    `requirements/requirements.md`, consistent with a Notes-column/
    recommendation addition rather than a rewrite. This same commit added
    REQ-405/406 to `requirements/requirements.md` and
    `requirements/traceability-matrix.md`, and the entire Component
    Engineer "Motor-Rail Supervisory Controller" comparison section to the
    BOM.
  - `43b3c90` ("Record human approval…") touched only `bom/
    component-selection.md` (4 lines — the Approval table's human sign-off
    row) and `validation/change-log.md` (1 line).
  - `4c812ad` (Rev 5) touched `datasheets/evidence-log.md`, the renamed F1
    and TPS26631 datasheet metadata files, `hardware/power-budget.md`,
    `hardware/schematic/bench-imu-01-design.md`, and
    `validation/change-log.md`. **It did not touch `bom/
    component-selection.md` or `requirements/requirements.md`** — Circuit
    Engineer implemented U6 in the schematic but made no further changes to
    either file, consistent with those files already being correctly
    updated by the prior mediation commit.
  - `git log --oneline 4c812ad..HEAD` returns nothing — **Rev 5 is
    confirmed to be the current HEAD state**; nothing has changed
    underneath this review between the task's framing and this cycle's
    execution.
  - **This precisely reconciles the task's framing**: ISS-014's BOM/
    requirements propagation is real and independently confirmed present
    (see Finding below), but is correctly attributed to the Hardware
    Lead's mediation step, not to Circuit Engineer's Rev 4 rework directly
    — a correct division of labor (Circuit Engineer has no edit mandate
    over the BOM or requirements files), not a process gap.

### Checklist Results

Full 16-item checklist re-run against the Rev 4/5 changed areas and their
downstream effects. Items with no material Rev 4/5 touch-point are marked
"unaffected — carried forward from Cycle 3" rather than re-litigated from
scratch, per this cycle's re-review scope.

| # | Checklist item | Result | Notes |
|---|---|---|---|
| 1 | Voltage violation | **ISS-014 → RESOLVED; ISS-019 → RESOLVED** | §7.5.2's 2S/3S UVLO corner analysis independently re-verified arithmetically correct (unchanged since Cycle 3 — Rev 4 sharpened wording/framing, not the numbers) and now independently confirmed propagated into both `bom/component-selection.md` and `requirements/requirements.md` (see Process-integrity check above). U6's OVP/UVLO divider independently recomputed from TI's own Equations 9–10 against the design's actual R12/R13/R14 values — reproduces the claimed 8.17–8.51V UVLO / 13.49–14.30V OVP window exactly (see Finding). |
| 2 | Absolute Maximum Rating violation | Pass — independently reconfirmed, including for the new U6 | Freshly re-pulled TI's own AMR table (§6.1) and Recommended Operating Conditions table (§6.3) this cycle: IN_SYS/IN AMR = −0.3…67V (75V for a 10ms transient), ROC = 4.5–60V; OVP/dVdT/IMON/MODE/SHDN/ILIM/PLIM AMR = −0.3…5.5V. The design's actual VM_MOTOR (≤26V transient-clamped by D3, ≤~14.3V continuous once U6's own OVP acts) sits far inside both ceilings — U6 introduces **zero** new AMR/ROC exposure. R11's SHDN-node voltage (≈100mV driven low, 3.3V driven high via PA9) and the UVLO/OVP sense-pin voltages at trip (≈1.2V, per the divider's own reference-referred design) both sit comfortably inside the ±5.5V pin-group AMR. |
| 3 | Current limit | Pass — independently reconfirmed, extended to cover U6 | U5's own fixed 3–4A OCP unaffected (unchanged since Cycle 3). U6's own R(ILIM)=R15=3.57kΩ independently re-derived from TI's Equation 8 (R[kΩ]=18/I(OL)[A]) — yields a 5.04A typical / 4.69–5.40A cornered overload trip, sitting between the motor subsystem's ~1.05A nominal operating point and J4/F1's fault-current regime, a sensible defense-in-depth layer additional to F1's own PTC action. |
| 4 | Thermal risk | Pass — independently reconfirmed, including the new U6's added self-heating | U5's own thermal treatment unaffected (unchanged since Cycle 3, still a tracked non-blocking gap per the design document's own §16 item 21). U6's own ΔTJ independently recomputed from TI's Thermal Information table (RθJA=32.2°C/W for the PWP/HTSSOP-20 package) and Electrical Characteristics R(ON) (26–45mΩ across corners) — **confirms ≈7.5–13.0°C** at the design's actual ~1.05A operating current, matching `hardware/power-budget.md`'s own independent calculation and three of the four locations in the design document itself (§7.5.10, §14, §15). **Found a documentation inconsistency, not a technical one** — see new Finding ISS-024 below. |
| 5 | Missing decoupling capacitor | Pass — independently reconfirmed, extended to cover U6 | U5's own decoupling unaffected (unchanged since Cycle 3). U6's C16 (IN_SYS bypass) and C17 (dVdT) independently cross-checked against TI's own §9.2.2.5.1/§8.3.11/§9.5 recommendations (DS-PROT-029) and §8.3.1/§9.2.2.3 inrush equations (DS-PROT-028) respectively — both present, both correctly sized, no omission. |
| 6 | Floating pin | **ISS-015 → RESOLVED, with a new sub-question independently investigated and closed** | R10 (SPEED pulldown, unchanged since Rev 4) still present. New this cycle: independently investigated whether PA9 itself (U6's SHDN drive pin) is floating during the pre-GPIO-init boot window — confirmed via `web_search` (secondary-source, disclosed above) that STM32G0 GPIOs default to high-impedance Analog mode (no internal pull) after any reset, meaning R11's 10kΩ external pulldown cleanly dominates the SHDN node with full margin for the *entire* boot window, not just after firmware configures PA9. **No new floating-pin risk found on PA9.** See Finding below for the full derivation. |
| 7 | Incorrect pull-up/pull-down | **ISS-015 → RESOLVED** | R11=10kΩ independently re-derived from TI's own guaranteed ≥10µA SHDN-sink instruction (DS-PROT-024) — confirms the design's own claimed ≈8×/≈20× margins against V(SHUTF)=0.8V/V(SHUTR)=2V exactly. Sizing basis is independent of the disputed internal-pull-up-resistance figure (item 27, see Finding on residuals below), so it is robust to that open question either way. Bidirectional sanity-check independently performed: PA9 driving SHDN high (3.3V) draws only ≈330µA through R11 — trivial for any STM32 GPIO output stage, confirming the enable direction also works correctly. |
| 8 | Logic voltage mismatch | Pass — unaffected, carried forward from Cycle 3 | No new logic-level interface introduced; PA9 is a standard 3.3V STM32G0 GPIO driving a pin group (SHDN) whose own ROC/AMR (0–5V / −0.3…5.5V, confirmed this cycle) is fully compatible. |
| 9 | Interface timing | Pass — independently reconfirmed for U6's own timing | Turn-on delay independently recomputed from TI's own formula (742+49.5×C(dVdT)[nF] µs, DS-PROT-028) against C17=22nF — ≈1.83ms, an inconsequential addition to the motor domain's own power-up sequencing and well within any reasonable firmware timeout budget. No interface-timing concern found. |
| 10 | Power sequencing | **ISS-015 → RESOLVED (the cross-domain gap Cycle 3 identified)** | U6 now provides a genuine, MCU-commanded hardware gate on the entire motor domain's power (U6's OUT feeds U5's own VCC) — the MCU domain no longer merely hopes the motor domain powers up in a safe order; PA9 low (the R11-enforced, GPIO-reset-consistent default) holds the whole domain OFF until firmware deliberately enables it. This closes the specific cross-domain sequencing gap Cycle 3's ISS-015 identified, not merely SPEED's own analog level (which R10 alone already addressed at Rev 4). |
| 11 | Grounding | Pass — unaffected, carried forward from Cycle 3 | U6 sits on the existing single shared ground net; §12's net list independently confirmed U6's GND pin ties to the same ground as the rest of the board, no new ground domain introduced. |
| 12 | EMI/EMC risk | Pass — unaffected, carried forward from Cycle 3 | No new switching/noise source introduced — U6 is a linear pass-through load switch (not a DC-DC converter) in normal operation; its own inrush/dV\/dt control (Equations 1–2, independently reconfirmed) is itself an EMI-mitigation feature, not a new noise source. |
| 13 | Motor noise | Pass — unaffected, carried forward from Cycle 3 | No change to U5/M1 commutation-noise treatment. |
| 14 | Sensor noise | Pass — unaffected, carried forward from Cycle 3 | U6 sits entirely within the motor domain, upstream of U5; no new coupling path into the IMU's own 3V3 rail introduced. |
| 15 | PCB layout concern (incl. mechanical/thermal co-design) | Pass — independently reconfirmed, extended to cover U6's own thermal footprint | U6's PowerPAD/thermal-pad layout guidance (TI §9.6.2, DS-PROT-023) independently cross-checked present in §7.5.10's own layout notes; ΔTJ margin (item 4 above) confirmed wide enough that PCB copper-area layout practice, not exotic thermal design, is sufficient. No new rotating-body/mechanical interaction introduced by U6 itself (it is upstream, electrical-only). |
| 16 | Datasheet recommendation violation | Pass — independently reconfirmed | Every U6 support component (C16, C17, R11–R15) independently matches TI's own recommended application circuit and equations (DS-PROT-026 through DS-PROT-029) — no unexplained deviation found. |

### Findings

#### Re-verification of ISS-014 (2S/3S UVLO margin) — independently CONFIRMED RESOLVED

- **Claim under review**: the 2S/3S UVLO margin analysis is now a
  documented, binding 3S-only constraint, propagated into both
  `bom/component-selection.md` and `requirements/requirements.md`.
- **Independent verification method**: (1) Re-derived every corner of
  §7.5.2's own arithmetic from scratch (U5's UVLO thresholds, D2's forward
  voltage drop, F1's estimated series resistance) rather than accepting the
  design document's own restated numbers — **unchanged since my own Cycle
  3 review found this arithmetic sound**; Rev 4 sharpened the framing
  (explicitly calling out that 2S nominal fails at U5's own *typical*
  threshold, not just a worst-case corner) but did not change any
  underlying number. (2) Independently located and read the actual
  propagated text in both target files: `bom/component-selection.md` lines
  749–766 (Motor Driver IC recommendation section, an explicit 3S-only
  binding note) and `requirements/requirements.md` REQ-108's own Notes
  column (line 105) — both confirmed present, not merely claimed. (3)
  Independently used `git show --stat`/`git log` to determine **which
  commit** actually performed this propagation, rather than accepting Rev
  4's or Rev 5's own self-description — see the Process-integrity check
  above; the propagation is real but is correctly attributed to the
  Hardware Lead's `9410a9d` mediation commit, not to Circuit Engineer's Rev
  4 commit directly, which never touched either target file.
- **Result**: **RESOLVED**. Both halves of the original finding (correct
  arithmetic; binding-constraint propagation into the two places a Circuit
  Engineer or Component Engineer would actually need to see it) are now
  independently confirmed true and consistent across three separate files
  (design document, BOM, requirements).
- **Datasheet Source**: DS-MTR-023 (motor's own rated cell-count range,
  unchanged since Cycle 3); TI DRV10983 SLVSCP6H (U5's own UVLO thresholds,
  unchanged since Cycle 3); DS-PROT-006/033 (F1 series-resistance estimate,
  confirmed unchanged across the 30R500U→30R500UF swap).
- **Severity**: was HIGH (Cycle 3) — now closed, no residual severity.

#### Re-verification of ISS-015 (SPEED uncommanded-motion / cross-domain power-up risk) — independently CONFIRMED RESOLVED

- **Claim under review**: R10 (SPEED pulldown) plus the new U6 load switch
  with R11 (SHDN pulldown) together now provide both a safe SPEED level and
  a hardware-enforced default-OFF/fail-safe state for the whole motor
  domain, with PA9 as a real, complete fix (not a new floating-pin risk
  itself).
- **Independent verification method**:
  1. **R10** (§7.5.5): confirmed present and unchanged at 1kΩ since Rev 4 —
     directly closes SPEED's own analog-mode factory-default risk
     (checklist item 6/7's original trigger).
  2. **R11 sizing**: independently re-derived from TI's own guaranteed
     specification, not the design document's restated numbers. TI's own
     text (§8.3.13, quoted directly in DS-PROT-024): "a pulldown resistor
     used at the SHDN pin … must have sinking capability of at least
     10 µA" — a guaranteed worst-case leakage figure, independent of either
     of the two disputed internal-pull-up-resistance figures (see residual
     item 27 below). At R11=10kΩ, worst-case leakage current produces
     V(SHDN)=10µA×10kΩ=100mV — independently recomputed margins of ≈8×
     against V(SHUTF)=0.8V (falling/shutdown-confirm) and ≈20× against
     V(SHUTR)=2V (rising/enable, the tighter constraint for guaranteeing
     the device cannot self-enable cold), matching the design document's
     own claimed figures exactly.
  3. **PA9 pre-init state — the new question this task specifically
     raised**: independently investigated via `web_search` (ST Community
     forum threads plus ST's own public GPIO training material) whether
     STM32G0's GPIOs have a documented reset default that could leave PA9
     in a low-impedance or actively-driven state before firmware configures
     it. **Confirmed**: all STM32G0 GPIOs default to Analog mode
     (MODER=`0b11`) with no internal pull (PUPDR=`0b00`) immediately after
     any reset (power-on, NRST, or software) — a genuinely high-impedance
     state. PA9 (plain GPIO/USART1_TX/TIM1_CH2) is not one of the
     documented reset-default exceptions (unlike SWDIO/SWCLK/BOOT0/NRST).
     This means R11 cleanly dominates the SHDN node — with the same ≈8×/
     ≈20× margins computed above — for the *entire* window from power-on
     until firmware's GPIO-init code runs, not merely after it.
     **No new floating-pin risk exists on PA9 itself.**
  4. **Enable-direction sanity check** (not explicitly asked for, but a
     natural completeness check on a bidirectional pin): confirmed PA9
     driving SHDN high (3.3V) draws only ≈330µA through R11 — trivial for
     any STM32 GPIO push-pull output stage (<50Ω typical), confirming the
     mitigation works correctly in both directions, not just the fail-safe
     one.
  5. Cross-checked via TI's own Table 8-1 (DS-PROT-030) that MODE=Open (as
     wired) gives **Latch-off** specifically for the TPS26631 variant used
     here (not the auto-retry behavior some sibling TPS2663x variants
     exhibit) — an independent, chip-level defense-in-depth layer on top of
     the SHDN-based fail-safe, and confirmed the SHDN low→high toggle is
     TI's own documented latch-reset mechanism (Table 5-1), consistent with
     the design document's own claim.
- **Result**: **RESOLVED**. This closes the finding via the two strongest
  of the three Recommended Fix options my own Cycle 3 review offered (an
  external SPEED pulldown, and a supervisory VCC gate) — the third,
  weaker, documentation-only fallback is correspondingly unnecessary. The
  one honestly-disclosed residual (the 1MΩ-vs-≈440kΩ pull-up-resistance
  discrepancy) does not affect this conclusion, since R11's sizing basis
  is independent of it (see residual-items discussion below).
- **Datasheet Source**: DS-PROT-024 (SHDN guaranteed leakage/thresholds),
  DS-PROT-030 (Table 8-1 MODE behavior), plus this cycle's own
  `web_search`-based STM32G0 GPIO reset-default corroboration — now formally
  logged as **DS-MCU-067** in `datasheets/evidence-log.md` (MODERATE
  confidence, same hedge pattern as the pre-existing DS-MCU-044 entry: not
  independently re-extracted from the raw RM0454 reference-manual PDF this
  session, corroborated via web search only).
- **Affected Component**: R10, R11, U6, PA9.
- **Severity**: was HIGH (Cycle 3) — now closed, no residual severity.

#### Re-verification of ISS-019 (unbounded J4 input envelope) — independently CONFIRMED RESOLVED

- **Claim under review**: F1 (PTC fuse) plus the new U6 OVP/UVLO divider
  (R12/R13/R14) together now bound the input envelope, both for fault/
  surge conditions and continuous overvoltage, with OVP/UVLO trip points
  landing at ≈13.49–14.30V / ≈8.17–8.51V as claimed.
- **Independent verification method**: Independently extracted TI's own
  divider equations directly from the primary datasheet (§9.2.2.2,
  Equations 9–10, DS-PROT-026) rather than accepting the design document's
  restated formula, and recomputed all **six** resulting corner values
  from scratch using the design's actual resistor values (R12=887kΩ,
  R13=60.4kΩ, R14=88.7kΩ, E96 1%) and TI's own guaranteed reference
  min/typ/max values:
  - UVLO trip (rising): **8.172V / 8.339V / 8.506V** (min/typ/max)
  - OVP trip (rising): **13.737V / 14.017V / 14.298V** (min/typ/max)

  These reproduce the design document's own claimed 8.17–8.51V / 13.74–
  14.30V window to 3+ significant figures at every corner — an exact,
  independent match, not an approximate one. As a further self-check not
  explicitly required by the task, I also independently computed the
  falling (hysteresis) thresholds (UVLO≈7.575–7.991V, OVP≈12.732–13.433V)
  to confirm internally consistent, chatter-free switching behavior.
  Additionally cross-checked §12's net list against the equation topology
  used (IN_SYS→R12→UVLO-tap→R13→OVP-tap→R14→GND) — confirmed to match
  exactly, not merely assumed from the prose description.

  Separately, F1's own role (upstream fault-current/surge containment, not
  continuous-overvoltage regulation) was reconfirmed unchanged from Rev 4:
  the 30R500U→30R500UF swap shares an identical electrical spec
  (DS-PROT-033), and the honest gap the design document itself discloses
  — F1's own 10A trip current exceeds J4's 5A connector rating — remains
  present and correctly disclosed, not silently dropped; it is a
  **different** gap from the one ISS-019 opened (source/upstream fault
  coordination vs. continuous-overvoltage regulation), and U6's OVP
  function is what closes the latter, which is the gap ISS-019 was
  actually about.
- **Result**: **RESOLVED**. This closes the previously-missing
  continuous-overvoltage gap Cycle 3 identified — F1 (a PTC, not a
  precision comparator) could never have addressed sustained/continuous
  overvoltage on its own; U6's OVP pin is a true, independently-recomputed,
  correctly-implemented lockout referenced to the 9.0–13.0V design
  envelope with genuine (if not enormous — see new Finding ISS-025 below)
  margin at both ends.
- **Datasheet Source**: DS-PROT-026 (Equations 9–10, divider architecture);
  DS-PROT-033 (F1/F1-replacement spec equivalence, unchanged from Rev 4).
- **Affected Component**: F1, U6, R12, R13, R14.
- **Severity**: was HIGH (Cycle 3/rubber-duck) — now closed, no residual
  severity.

#### Re-verification of ISS-020 (no overspeed envelope) — independently CONFIRMED as the correct, honestly-disclosed OPEN disposition (not hardware-fixable)

- **Claim under review**: Circuit Engineer explicitly did not attempt a
  circuit-level fix, documenting this as a firmware-policy gap in new
  §7.5.11; Hardware Lead added new requirements REQ-405/406.
- **Independent verification method**: Read §7.5.11 directly and in full —
  confirmed the design document states plainly "No circuit-level fix
  exists for this finding, and none is invented here," correctly routing
  the gap to firmware rather than papering over it with an unjustified
  circuit trick. Independently read `requirements/requirements.md` line
  142 — confirmed REQ-405 exists, is well-formed (Priority: Must, explicit
  rationale tying the ≥3000 RPM floor to the recommended motor's own
  6–7× higher no-load speed and the ω² scaling of stored rotational
  energy, explicit tie to REQ-403's HITL gate and to Mechanical Lead's
  containment design), and is correctly attributed as "added at
  Independent Review, ISS-020." Independently confirmed via `git show
  --stat 9410a9d` that this requirement was added by the Hardware Lead's
  own mediation commit (with proper authority over that file), not
  silently invented by Circuit Engineer.
- **Result**: This finding **cannot be closed by hardware alone** — my own
  Cycle 3 review, and this cycle's independent re-check, both agree there
  is no available circuit-level mitigation for a firmware/control-policy
  question (bounding a *commanded* maximum speed requires the firmware
  loop that issues speed commands and reads FG feedback; no passive or
  supervisory-IC circuit addition can substitute for that decision).
  **Remains OPEN** — this is the correct, honest state, not a defect in
  Rev 5's hardware work. Recommend Hardware Lead/human Chief Engineer
  consider a future disposition note along the lines of "OPEN, tracked for
  Firmware Bring-up phase, hardware enabler not required for this specific
  gap" — but per `validation/open-issues.md`'s own Rules, a HIGH may only
  become `ACCEPTED-RISK` with a named human Chief Engineer sign-off,
  written rationale, and date; I am not making that disposition change
  unilaterally in this cycle's `open-issues.md` update (see below).
- **Datasheet Source**: N/A — this is a requirements/firmware-policy gap,
  not a component-level datasheet question.
- **Affected Component**: Firmware (motor speed-command loop); no hardware
  component change applicable.
- **Severity**: HIGH, unchanged — open, correctly routed, not a hardware
  defect.

#### Re-verification of ISS-021 (non-latching fault protection) — independently CONFIRMED as the correct, honestly-disclosed OPEN disposition, with a now-confirmed-sufficient hardware enabler

- **Claim under review**: Circuit Engineer flagged this as needing
  firmware (§7.5.12); U6 now provides the physical enforcement point
  (PA9/SHDN can cut U6's output) for a future firmware latch policy.
- **Independent verification method**: Read §7.5.12 directly and in
  full — confirmed the same honest "no circuit-level fix, none invented
  here" disclosure pattern as ISS-020. Independently read
  `requirements/requirements.md` line 143 — confirmed REQ-406 exists, is
  well-formed (Priority: Should, explicit rationale that none of
  DRV10983's three protection mechanisms latch, companion to REQ-404), and
  is correctly attributed to Independent Review/ISS-021. Independently
  assessed whether the *hardware enabler* itself is real and sufficient —
  this is the one part of ISS-021 that genuinely is a hardware question,
  distinct from ISS-020's pure-firmware-policy framing: PA9 driving U6's
  SHDN low does not merely lower SPEED to a safe level, it **removes power
  from U5 entirely** (U6's OUT is U5's own VCC supply) — the strongest
  physical enforcement mechanism available at this design's architecture,
  confirmed via the same R11/PA9 verification performed for ISS-015 above
  (§7.5.10/§11 wiring, guaranteed 10µA leakage spec, STM32G0 reset-default
  behavior). Additionally independently cross-checked §16 item 25's own
  self-flagged nuance — that U6's own MODE=Open overload latch (Table 8-1,
  DS-PROT-030) and any future firmware-declared Lock-Detection latch share
  the same SHDN reset line but are logically distinct fault sources, and
  that U6 exposes no register/flag (PGOOD/FLT both left floating per
  §7.5.10) letting firmware tell them apart — confirmed this is an
  accurate, not overstated, characterization of a genuine future firmware
  design consideration, not a defect in Rev 5 itself.
- **Result**: The firmware retry-counting/rolling-window/re-arm *policy*
  cannot be closed by hardware and correctly **remains OPEN**, same
  reasoning as ISS-020. The hardware **enabler** (a real, complete,
  physical means for firmware to cut power to the entire motor domain) is
  independently confirmed **real and sufficient** for whatever latch
  policy Firmware Lead eventually implements — nothing further is needed
  from Circuit Engineer on this point. Recommend the same future
  human-disposition treatment as ISS-020 (OPEN, tracked for Firmware
  Bring-up, hardware prerequisite satisfied) rather than an AI-unilateral
  `ACCEPTED-RISK` change.
- **Datasheet Source**: DS-PROT-024 (SHDN control), DS-PROT-030 (Table 8-1
  MODE=Open latch-off behavior, PGOOD/FLT pin description).
- **Affected Component**: U6, PA9 (hardware enabler, confirmed sufficient);
  firmware (policy, still undecided — no hardware component change
  applicable).
- **Severity**: HIGH, unchanged — open, correctly routed, not a hardware
  defect.

#### Residual items review (design document's own §16 items 27–29) — independent view

- **Item 27 (SHDN internal pull-up: 1MΩ vs. ≈440kΩ, neither resolved)**:
  Independently re-read TI's own Figure 8-1 (Functional Block Diagram,
  page 16 of the primary PDF) this cycle — confirms **"1 MΩ"**, matching
  the design document's own DS-PROT-025 citation, the pre-existing
  DS-PROT-013 (TI E2E community-forum citation), **and** Component
  Engineer's own independent citation in `bom/component-selection.md` line
  1067 ("internal 1MΩ pull-up to 2.7V, DS-PROT-013") — three independent
  sources agreeing on 1MΩ. The competing ≈440kΩ figure traces to exactly
  one source: the human Chief Engineer's own fresh web search, recorded
  directly in `bom/component-selection.md` line 1234's Approval-table
  entry. I do not have visibility into what the human's search actually
  found (a different die revision, a sibling-part datasheet, or a
  third-party estimate could all produce this), and I am not overruling an
  independently-conducted human research result on a question that carries
  no safety consequence either way — TI's own formal Electrical
  Characteristics table has no guaranteed min/typ/max row for this
  specific resistance at all, so neither figure is a "guaranteed spec" in
  the datasheet sense, and R11's own sizing (independently reconfirmed
  above) uses the guaranteed 10µA leakage spec instead, which dominates by
  ≈44×–100× regardless of which pull-up figure is correct. **Confirmed
  non-blocking, no new backlog row warranted** — this is an accurate,
  appropriately-humble disclosure, not a defect.
- **Item 28 (OVP margin vs. a hypothetical 4S pack, "3.4%"/"3.75%")**:
  Independently recomputed both percentages from scratch using the primary
  datasheet's own equations and adverse reference+resistor-tolerance
  combinations: reference-tolerance-only worst case (V(OVPR)_max=1.224V,
  nominal R12/R13/R14) → **14.2975V** OVP trip vs. a 4S nominal 14.8V →
  **3.4%** margin; full-stack worst case (V(OVPR)_min=1.176V **and**
  adverse ±1% resistor tolerances on all three resistors) → **13.4881V**
  OVP trip vs. the 13.0V envelope ceiling → **3.76%** margin (design
  document rounds to "3.75%" — an immaterial rounding difference,
  independently reconciled). Both figures independently reproduce exactly.
  Both are genuine, positive, non-zero margins — not violations — and this
  residual item is correctly judged non-blocking given 3S is this design's
  actual, procedurally-enforced envelope (ISS-014's own binding constraint,
  now independently confirmed propagated into the BOM/requirements this
  cycle) and 4S is already an out-of-envelope, procedural-exclusion
  scenario, not a credible normal-operation state. **This margin, while
  real and correctly computed, is narrow enough to independently warrant
  its own tracked (not blocking) backlog entry** — see new Finding ISS-025
  below; this is a considered severity judgment on my part, not a
  restatement of the design document's own framing.
- **Item 29 (dV/dt capacitor sizing basis)**: Already independently
  confirmed correct during this cycle's primary U6 verification pass — the
  design correctly derives C17=22nF from TI's own Equations 1–2 against
  this design's actual C(OUT)=10µF, not from either of TI's own worked
  examples (1mF/30mF, both 100×–3000× larger and drawn from unrelated
  application contexts). **Confirmed non-blocking, no new backlog row
  warranted.**

#### New Finding: ISS-024 — Thermal-rise changelog figure inconsistent with its own supporting calculation (LOW)

- **Issue**: The top-of-file Rev 5 "Revision changelog" summary (line 103)
  states U6's thermal rise as "ΔTJ ≈ 10–16°C," while three other locations
  within the same document (§7.5.10 line 1974, §14 line 2810, §15 line
  3158) and `hardware/power-budget.md`'s own detailed calculation all
  consistently state "≈7.5–13.0°C."
- **Rationale**: A single document should not present two different
  numeric answers to the same question; a future reader skimming only the
  changelog summary would carry away a different (and, as it happens, more
  conservative) figure than the one the design's own detailed self-checks
  and the companion power-budget document actually support.
- **Independent verification**: Independently recomputed ΔTJ from TI's own
  Thermal Information table (RθJA=32.2°C/W for the PWP/HTSSOP-20 package)
  and Electrical Characteristics R(ON) values (26/30.44/34.5mΩ min/typ/max)
  at the design's actual ~1.05A nominal operating current — reproduces
  **≈7.5–13.0°C**, confirming the *detailed* figure (§7.5.10/§14/§15/
  power-budget.md) is the technically correct one, and the changelog
  summary line is the outlier.
- **Datasheet Source**: DS-PROT-031 (Thermal Information table; R(ON)/IQ
  Electrical Characteristics rows).
- **Failure Mechanism**: None — this is a documentation-consistency defect,
  not a physical/electrical failure mode. The wrong figure, if believed,
  overstates rather than understates thermal rise, so it carries no safety
  risk in itself; the risk is purely one of an inconsistent record
  confusing a future reader or reviewer.
- **Affected Component**: U6 (documentation only — no schematic/BOM change
  needed).
- **Recommended Fix**: Circuit Engineer to correct the single changelog
  summary line (top-of-file, line 103) to match the three internally
  consistent, independently-reconfirmed occurrences ("≈7.5–13.0°C").
  Trivial, single-line, no re-analysis required.
- **Severity**: **LOW** — documentation-only, non-safety-relevant, easily
  fixed whenever Circuit Engineer next touches the document; does not
  block this cycle's verdict.

#### New Finding: ISS-025 — U6 OVP trip-point margin against a hypothetical 4S pack is real but narrow (LOW, tracked)

- **Issue**: U6's OVP trip point, at the worst-case combination of
  reference tolerance and adverse ±1% resistor tolerances on R12/R13/R14,
  clears the 13.0V envelope ceiling by only ≈3.76%; at reference-tolerance-
  only worst case, it clears a hypothetical 4S pack's nominal 14.8V by only
  ≈3.4%.
- **Rationale**: Both margins are genuine and positive — this is not a
  violation of the 9.0–13.0V envelope requirement, and is not, by itself, a
  defect in Rev 5's design. However, a margin this narrow means that any
  future revision using looser-tolerance resistors, or any real-world
  resistor drift/aging beyond the ±1% E96 tolerance assumed here, could
  erode the safety margin against a genuine field mis-connection (e.g., an
  operator plugging in a 4S pack by mistake) faster than a wider-margin
  design would. This is exactly the class of "narrow but not zero margin"
  finding worth tracking rather than either dismissing or blocking on.
- **Independent verification**: Independently recomputed both percentages
  from TI's own primary-datasheet equations (Equations 9–10) using the
  design's actual resistor values and both plausible worst-case tolerance
  combinations — reproduces the design document's own §16 item 28 figures
  (3.4%/3.75%, my own recomputation: 3.4%/3.76%) essentially exactly (see
  Residual items review above for the full derivation). This is not a new
  arithmetic finding — it is a considered severity judgment that this
  residual item, while correctly identified and disclosed by Circuit
  Engineer, deserves its own tracked backlog entry rather than remaining
  only inside a self-check narrative paragraph, given that a resistor-
  tolerance choice in a *future* revision could silently erode this margin
  without anyone re-deriving it unless it is separately tracked.
- **Datasheet Source**: DS-PROT-026 (Equations 9–10, divider architecture
  and guaranteed reference tolerance).
- **Failure Mechanism**: If a future BOM revision substitutes looser-
  tolerance (e.g., 5%) resistors for R12/R13/R14 without re-deriving the
  OVP trip point, or if resistor values drift with age/temperature beyond
  the ±1% assumed here, the worst-case OVP trip point could shift closer to
  — though based on this cycle's own arithmetic, not yet past — the 13.0V
  envelope ceiling or a 4S pack's nominal voltage, narrowing (not yet
  eliminating) the safety margin against a mis-connected battery pack.
- **Affected Component**: R12, R13, R14.
- **Recommended Fix**: No change required for the current Rev 5 E96/1%
  resistor selection — the margin is real and positive. Track for future
  consideration: (a) if a real 4S-pack mis-connection is ever judged a
  credible (not just theoretical) field scenario, consider tighter-
  tolerance (e.g., 0.1%) resistors for R12–R14 in a future revision; (b) if
  R12/R13/R14 are ever re-selected for cost or availability reasons, the
  new tolerance must be re-run through this same margin calculation before
  being approved, not assumed equivalent.
- **Severity**: **LOW** — real, quantified, non-blocking; a considered
  independent severity call (this task's own instruction to "form your own
  view," not a restatement of the design document's own framing, which
  left the severity judgment to Hardware Reviewer).

### Verdict

- **Verdict**: **CONDITIONAL** (not a clean PASS, and not a FAIL — this is
  a routing decision to Firmware Bring-up, not a rework dead-end back to
  Circuit Engineer, directly mirroring my own Cycle 3 verdict's precedent
  language for exactly this situation)
- **Open CRITICAL count**: 0
- **Open HIGH count**: 2 (ISS-020, ISS-021 — both correctly remain OPEN;
  neither is a hardware defect, both are honestly-disclosed
  firmware-policy gaps with now-confirmed-sufficient hardware enablers)
- **Open MEDIUM count**: 2 (ISS-022, ISS-023 — unaffected by this cycle's
  scope, not re-litigated; still tracked as checkpoints for Firmware
  Bring-up and validation-artifact closeout respectively, per Cycle 3)
- **Open LOW count**: 5 (ISS-016, ISS-017, ISS-018 unaffected/carried
  forward from Cycle 3; plus 2 new this cycle — ISS-024, ISS-025)
- **All 3 hardware-closable findings, independently confirmed RESOLVED this
  cycle**: ISS-014 (2S/3S UVLO margin — arithmetic and propagation both
  independently reproduced), ISS-015 (SPEED/cross-domain power-up risk —
  R10+U6/R11/PA9 independently confirmed sufficient, including a fresh,
  specifically-requested investigation of PA9's own pre-init state that
  found no new risk), ISS-019 (unbounded J4 envelope — F1+U6 OVP/UVLO
  independently recomputed from the primary datasheet's own equations,
  reproducing every claimed trip-point corner exactly).
- **2 findings correctly remain OPEN, not because of any hardware gap, but
  because they require a firmware decision hardware cannot substitute
  for**: ISS-020 (maximum commanded-speed envelope) and ISS-021 (latched-
  fault policy). Both are honestly disclosed as such in §7.5.11/§7.5.12
  (independently confirmed, not merely accepted), both have well-formed
  companion requirements (REQ-405/406, independently confirmed to exist
  and correctly reference these findings), and — the specific technical
  question this task asked me to assess for ISS-021 — U6 now independently
  confirmed to provide a real, complete, sufficient physical enforcement
  point (full power removal to U5, not merely a signal-level override) for
  whatever latch policy Firmware Lead eventually implements. **I am not
  changing either status to `ACCEPTED-RISK` in this cycle's
  `open-issues.md` update** — per that file's own Rules, only a named
  human Chief Engineer may make that disposition, with written rationale
  and a date. My own recommendation (recorded in each row's Notes) is that
  both are ripe for a human Chief Engineer to consider exactly that
  disposition — "OPEN, tracked for a specific future phase (Firmware
  Bring-up)" — precisely the treatment this task's own framing anticipated
  as reasonable for firmware-policy gaps with a confirmed hardware
  enabler, but that is a human call, not mine to make unilaterally.
- **2 new LOW findings opened this cycle, both independently derived, not
  restated from the design document's own self-flagged items**: ISS-024
  (a genuine, if minor, thermal-figure documentation inconsistency between
  the changelog summary and three other internally-consistent locations)
  and ISS-025 (a considered severity judgment that the design document's
  own §16 item 28 residual — real but narrow OVP margin against a
  hypothetical 4S pack — deserves its own tracked backlog row rather than
  remaining only inside a self-check narrative). Neither blocks this
  cycle's verdict.
- **What independently checks out with no further action needed**: every
  numeric/technical claim associated with U6 (R11 sizing, UVLO/OVP divider
  trip points at all six corners, R(ILIM)/R15, dV/dt/C17 and turn-on delay,
  thermal ΔTJ, MODE=Open latch-off behavior, AMR/ROC exposure) was
  independently re-derived against the primary TI TPS2663x datasheet this
  cycle and found to match the design document's own claims with zero
  discrepancies in any safety-critical figure. Residual items 27 and 29
  (design document's own §16) are both independently confirmed genuinely
  non-blocking.
- **Next action**: Route this Rev 5 state, and this review, to Hardware
  Lead for onward routing to Firmware Bring-up for REQ-405/406 (ISS-020/
  021's actual policy implementation) — this is not a loop-back to Circuit
  Engineer, since no further hardware rework is identified as required by
  this cycle. Recommend Hardware Lead/human Chief Engineer consider explicit
  `ACCEPTED-RISK`-style human disposition for ISS-020/021's *current,
  hardware-complete* state (distinct from the underlying firmware policy
  itself, which remains genuinely open engineering work, not a risk to be
  accepted). ISS-024/025 (LOW) do not block progress but should receive an
  explicit disposition before this subsystem's own Design Complete Gate,
  per `docs/architecture.md` §8, same as ISS-016/017/018 before them.

## Cycle 5 — ISS-026 CRITICAL fix (Rev 6) re-verification: focused pin-reassignment check (2026-09-10)

### Review Cycle Metadata

- **Design revision reviewed**: `hardware/schematic/bench-imu-01-design.md`
  **Rev 6** (commit `ef5edc4`, "Rev 6: fix ISS-026 CRITICAL — re-route IMU
  I2C bus PB10/PB11 -> PA11/PA12"). **This is a narrow, focused re-review of
  one specific CRITICAL fix, not a full re-review** — per the task's own
  explicit framing, Rev 5's motor-subsystem content (already independently
  reviewed and passed at Cycles 3/4) is out of scope and not re-litigated
  here, and ISS-020/ISS-021 correctly remain OPEN/ACCEPTED-RISK pending
  Firmware Bring-up, untouched by this cycle.
- **Reviewer**: Hardware Reviewer — see
  `.github/agents/hardware-reviewer.agent.md`. Independent of the Circuit
  Engineer session that authored Rev 6 and the Hardware Lead session that
  relayed/opened ISS-026. Did not accept the changelog's own self-check
  claims (§14 item 13, §16 item 4) at face value; re-derived each checklist
  item independently below.
- **Independence statement**: The core physical fact underlying ISS-026
  (PB10/PB11 absent from the STM32G031K8T6's actual LQFP-32 package) was
  re-derived from scratch this cycle directly against ST's own primary
  datasheet (**DS12992 Rev 4**), fetched fresh via
  `https://r.jina.ai/https://www.st.com/resource/en/datasheet/stm32g031k8.pdf`
  — not accepted from the design document's, evidence-log's, or Hardware
  Lead's own citation/paraphrase (DS-MCU-068). Table 2 (device/peripheral
  counts), Figure 7 (LQFP32 pinout), Figure 9 (LQFP48 pinout), Table 12
  (per-pin per-package assignment), and Tables 13/14 (Port A/B
  alternate-function maps) were each independently located and read. Before
  trusting my own parsing of Table 12's six-package-column layout, I
  validated the parsing methodology against a known-good, independently
  checkable row (PC13: dash×5 then "1" — LQFP48-only, physical pin 1,
  consistent with Figure 9 but not Figure 7) before applying the same
  parsing to the PB10/PB11/PA11/PA12 rows under review.
- **Scope**: Per the task's explicit framing, this cycle checked exactly
  six things: (1) the core physical fact, from a primary source,
  independently; (2) completeness — every remaining PB10/PB11 mention in
  the document is historical/annotated, not a live incorrect claim; (3) no
  new conflict — PA11/PA12 used nowhere else in the design; (4) R3/R4
  pull-up sizing (§5.2) genuinely unaffected by the pin move; (5) scope
  discipline — no file other than the schematic doc touched by the Rev 6
  commit; (6) the four checklist items specifically relevant to a
  pin-reassignment (floating pin, pull-up/pull-down, logic voltage
  mismatch, interface timing). The other 12 checklist items are not
  relevant to this narrow a change and were not re-run from scratch, per
  the task's own explicit instruction.
- **Process-integrity check**: Independently ran `git show --stat` and
  `git show --name-status` on commit `ef5edc4` rather than relying on the
  commit message's own self-reported diffstat: confirms **exactly one file
  touched** — `hardware/schematic/bench-imu-01-design.md` (201 insertions,
  29 deletions). `firmware/bench-imu-01/`, `bom/component-selection.md`,
  `requirements/requirements.md`, `hardware/mechanical-interface.md`, and
  `hardware/mechanical/` are all confirmed untouched by this commit.
  `git status` independently confirmed a clean working tree with HEAD
  exactly at `ef5edc4` — no drift between the task's framing and this
  cycle's execution.
- **KiCad tool cross-checks used**: None — no KiCad project exists for this
  repository (consistent with Cycles 1–4); the Markdown schematic-equivalent
  document remains the correct artifact, reviewed net-by-net (§12) and
  pin-by-pin (§11) as before.

### Checklist Results

Only the checklist items the task identified as relevant to a
pin-reassignment change are re-run from scratch; the remaining 12 are
unaffected by a same-peripheral/same-AF/different-GPIO-port change and are
carried forward unaffected from the Cycle 3/4 pass on Rev 5 (this fix
touches no power architecture, motor subsystem, protection, or decoupling
component).

| # | Checklist item | Result | Notes |
|---|---|---|---|
| 1 | Voltage violation | N/A — out of scope, unaffected | No voltage-domain change; same 3.3V MCU, same devices. |
| 2 | Absolute Maximum Rating violation | N/A — out of scope, unaffected | No AMR-relevant component changed. |
| 3 | Current limit | N/A — out of scope, unaffected | No current-path change. |
| 4 | Thermal risk | N/A — out of scope, unaffected | No power-dissipating component changed. |
| 5 | Missing decoupling capacitor | N/A — out of scope, unaffected | No new device added. |
| 6 | **Floating pin** | **Pass — independently confirmed** | R3/R4 (I2C pull-ups) travel with the net, not with the specific MCU pin — the bus is pulled up regardless of which GPIO terminates it. PB10/PB11 were removed from §11's pin table entirely (not left as a dangling "used but unconnected" entry), and PA11/PA12 correctly appear in the used-pin table with the pull-up-terminated bus. No floating pin introduced. |
| 7 | **Incorrect pull-up/pull-down** | **Pass — independently confirmed** | See Finding below (§5.2 re-derivation): `Rp,min=(Vcc−VOL,max)/IOL` and `tr≈0.8473×Rp×Cb` depend only on Vcc/VOL,max/IOL/Cb, none of which reference a physical pin. Independently went further than the design document's own reasoning: Table 12 shows PB10/PB11 and PA11/PA12 (LQFP32/UFQFPN32 row) share the **identical I/O structure designation "FT_fa"** — the datasheet's own basis for VOL,max/IOL — confirming, not merely assuming, that R3=R4=4.7kΩ remains correctly sized. |
| 8 | **Logic voltage mismatch** | **Pass — independently confirmed** | Port A and Port B share the same single VDD/VDDIO 3.3V I/O supply domain on this MCU; the identical "FT_fa" I/O-structure class (not port letter) is what governs electrical/logic-level behavior in ST's own datasheet. No new logic-level interface introduced by moving from Port B to Port A pins. |
| 9 | **Interface timing** | **Pass — independently confirmed** | Same I2C2 peripheral instance, same AF6 alternate-function selector (Table 13: PA11/PA12 AF6=I2C2_SCL/I2C2_SDA; Table 14: PB10/PB11 AF6=I2C2_SCL/I2C2_SDA — identical selector value on both ports). Alternate-function pad routing is a signal-routing crossbar operation; it does not alter the peripheral's own internal Fast-mode 400kHz timing-register configuration. No timing impact. |
| 10 | Power sequencing | N/A — out of scope, unaffected | No sequencing-relevant component changed. |
| 11 | Grounding | N/A — out of scope, unaffected | No ground-net change. |
| 12 | EMI/EMC risk | N/A — out of scope, unaffected | No new switching/noise source. |
| 13 | Motor noise | N/A — out of scope, unaffected | No change to motor subsystem. |
| 14 | Sensor noise | N/A — out of scope, unaffected | No new coupling path into the IMU's rail. |
| 15 | PCB layout concern | N/A — out of scope, unaffected | Pre-layout schematic-equivalent document; no board-level layout exists yet to re-check. |
| 16 | Datasheet recommendation violation | **Pass — independently confirmed** | The fix's own recommended pin choice (PA11/PA12 via AF6) matches ST's own Table 12/13 alternate-function assignment exactly — no unexplained deviation. |

### Findings

#### Re-verification of ISS-026 (IMU I2C bus PB10/PB11 → PA11/PA12) — independently CONFIRMED RESOLVED

- **Claim under review**: PB10/PB11 — where the IMU's I2C2 bus has been
  documented and firmware-implemented since Rev 2's ISS-011 fix — do not
  physically exist on the STM32G031K8T6's actual LQFP-32 package, and Rev 6
  re-routes the bus to PA11(SCL, physical pin 22)/PA12(SDA, physical pin
  23), same I2C2 peripheral, same AF6 selector, with every reference
  corrected across the document and no conflict introduced.
- **Independent verification method**:
  1. **Core physical fact**, re-derived from ST's primary datasheet
     (DS12992 Rev 4), fetched fresh this cycle: Table 2 (30 GPIOs, K-suffix/
     LQFP32-UFQFPN32 vs. 44, C-suffix/LQFP48-UFQFPN48); Figure 7 (LQFP32
     pinout — no PB10/PB11 anywhere in the 32-pad enumeration; PA11/PA12
     present); Figure 9 (LQFP48 pinout — PB10/PB11/PB12 present); Table 12
     (per-pin per-package table, six-package-column parsing independently
     validated against a known row, PC13, before use) — PB10 shows dash in
     the LQFP32/UFQFPN32 column and pin **22** only in LQFP48/UFQFPN48; PB11
     shows the same pattern with pin **23**; PA11 shows physical pin **22**
     present in the LQFP32/UFQFPN32 column itself; PA12 shows physical pin
     **23**. Table 13 (Port A AF map) confirms PA11 AF6=I2C2_SCL, PA12
     AF6=I2C2_SDA; Table 14 (Port B AF map) confirms PB10 AF6=I2C2_SCL, PB11
     AF6=I2C2_SDA — the identical selector, exactly as claimed.
  2. **Completeness**: fresh `grep -n "PB10"`/`"PB11"` pass, 43 combined
     hits across the whole document, each individually reviewed in context
     — every one is Rev 6/Rev 2 changelog narrative, or a live table/prose
     entry that correctly states PA11/PA12 as the current value with
     PB10/PB11 present only as historical/superseded annotation (§2.3 lines
     737–738, §5.3 lines 1196–1197, §5.5/§6/§7.5.4, §11's table lines
     2448–2449 plus its Rev 6 note, §12 net list lines 2543–2544, §14 item
     13, §16 item 4). No live incorrect claim found anywhere.
  3. **Conflict check**: fresh `grep -n "PA11"`/`"PA12"` pass, 27 hits each,
     every occurrence tied exclusively to the IMU's I2C2 SCL/SDA function;
     cross-checked against the motor subsystem's own PA6/PA8/PA9/PB1/PB6/
     PB7 allocations (§7.5.4) — no overlap found. Free-GPIO inventory
     arithmetic independently re-added (§11: 11 enumerated free pins +
     PB8/PB9 = 13, down from 15 with PA11/PA12 now committed) — consistent.
  4. **R3/R4 pull-up sizing** (§5.2), independently re-read in full:
     `Rp,min=(Vcc−VOL,max)/IOL` and `tr≈0.8473×Rp×Cb` depend on Vcc=3.3V,
     VOL,max=0.4V, IOL=3mA (Fast-mode DC spec) and an assumed Cb≈50pF — none
     of which reference a physical MCU pin. Beyond the design document's own
     stated reasoning, independently found that Table 12 lists PB10/PB11
     and PA11/PA12 (LQFP32/UFQFPN32 row) under the **identical I/O structure
     designation "FT_fa"** — the datasheet's own basis for VOL,max/IOL —
     confirming the two pin pairs are electrically interchangeable for this
     purpose, not merely assumed to be. R3=R4=4.7kΩ sizing is unaffected.
  5. **Scope discipline**: `git show --stat`/`--name-status ef5edc4`
     independently confirms exactly one file touched
     (`hardware/schematic/bench-imu-01-design.md`, 201 insertions/29
     deletions); `firmware/bench-imu-01/`, `bom/component-selection.md`,
     `requirements/requirements.md`, `hardware/mechanical-interface.md`, and
     `hardware/mechanical/` all confirmed untouched. `git status` clean,
     HEAD=`ef5edc4`.
  6. **Floating pin / pull-up-pull-down / logic-voltage / interface-timing**:
     see Checklist Results table above — all four independently re-derived
     as clean, not merely restated from the changelog's own self-check.
- **Result**: **RESOLVED**. Every element of the fix independently checks
  out: the core physical fact, completeness of the correction, absence of
  any new conflict, continued validity of the R3/R4 pull-up sizing, and
  scope discipline (schematic-only commit, firmware change correctly
  deferred to the already-planned Firmware Bring-up phase with a
  forward-reference note already in place).
- **Datasheet Source**: DS-MCU-068 (independently re-confirmed against the
  primary ST DS12992 Rev 4 datasheet this cycle, not merely re-cited).
- **Affected Component**: U1 (STM32G031K8T6) — PA11/PA12 (was PB10/PB11);
  R3/R4 (I2C pull-ups, endpoint only, sizing unaffected).
- **Severity**: was **CRITICAL** — now closed, no residual severity.

### Verdict

- **Verdict**: **PASS**, for this narrow, focused review scope.
- **Open CRITICAL count**: 0 (ISS-026 was the sole open CRITICAL finding on
  this document; it is independently confirmed RESOLVED this cycle).
- **Open HIGH count**: 0 net-new from this cycle; ISS-020/ISS-021 remain
  correctly OPEN/ACCEPTED-RISK pending Firmware Bring-up, per the task's own
  explicit instruction not to re-litigate them here — unaffected by, and
  unrelated to, this cycle's scope.
- **What independently checks out with no further action needed**: the core
  physical fact (re-derived from ST's primary datasheet, not merely
  re-cited), completeness of the PB10/PB11→PA11/PA12 correction across the
  document, absence of any new pin conflict, continued validity of R3/R4
  pull-up sizing (with an additional independent cross-check — identical
  "FT_fa" I/O-structure class — beyond what the design document itself
  argued), and scope discipline (verified via `git show`, not merely
  trusted from the commit message).
- **Next action**: Route to Hardware Lead. No further hardware rework
  identified — this cycle finds nothing to send back to Circuit Engineer.
  The corresponding firmware GPIO/AF/clock change (GPIOB pins 10/11 → GPIOA
  pins 11/12, same AF6, same I2C2 peripheral base address) is correctly
  deferred to, and already flagged for, the Firmware Bring-up phase.

---

## Mechanical Reviewer — Cycle 3 (Independent Review of Rev 3 Motor Driver + Reaction Wheel Enclosure Redesign, 2026-09-11)

### Review Cycle Metadata

- **Design revision reviewed**: `hardware/mechanical/bench-imu-01-enclosure.scad`
  (full parametric OpenSCAD source, 991 lines, up from Rev 2's 483) together
  with its companion `hardware/mechanical/bench-imu-01-dimensional-spec.md`
  (914 lines, up from Rev 2's 570), both at **"Rev. 3"** status — a full
  redesign adding a Motor Driver + Reaction Wheel subsystem to the previously
  Design-Complete Rev 2 board. Author: Mechanical Lead (AI agent), commit
  `c5ac653` ("Mechanical Design (Rev 3): full enclosure redesign for motor +
  flywheel"), dated 2026-08-31 (independently confirmed via `git log` this
  cycle, not assumed). Status at handoff: dimensional-spec §15 self-check
  claims "10/10 ✅" (explicitly disclosed as non-binding), §16 lists open
  items carried forward, and the design's own report to the Hardware Lead
  additionally self-discloses two items flagged specifically for this
  review's attention: a pre-existing Rev 2-origin base-tab/lid-skirt solid
  interference explicitly left unfixed (out of scope for the Rev 3 task),
  and a new borderline motor-wire bridge span (9.0–9.42mm against the
  design's own 10mm max-bridge-span rule, described as "90–94% of limit").
- **Reviewer**: Mechanical Reviewer — see
  `.github/agents/mechanical-reviewer.agent.md`. Independent of the
  Mechanical Lead role/session that authored this design. This is the first
  Mechanical Reviewer cycle to examine the **Rev 3** scope specifically
  (Rev 2's own enclosure was reviewed and closed out across Mechanical
  Reviewer Cycle 1/Cycle 2 above, both fully RESOLVED per `open-issues.md`
  MISS-001 through MISS-004; MISS-005/006/007 remain open but LOW/MEDIUM and
  non-gating, carried forward unchanged since Rev 3 did not touch that
  geometry). Rev 3 is a full redesign adding an entire new subsystem, not a
  delta on the Rev 2 geometry alone, so this cycle treats it as a full-scope
  review rather than a changed-area-only pass.
- **Independence statement**: No claim in
  `bench-imu-01-dimensional-spec.md`'s own §3/§7/§8/§11/§12/§13/§15 self-check
  was accepted on the strength of its stated confidence or its "10/10 PASS"
  self-check claim. Every arithmetic claim in scope for this cycle — REQ-306's
  radial *and* axial clearance, the full Z-height stack driving overall
  assembled height, both of the Mechanical Lead's own self-disclosed items,
  the REQ-403 containment disposition's specific claims, the new 3-piece
  assembly's joints, and the off-board motor-mounting ASSUMPTION's
  consistency — was independently re-derived this cycle directly from the
  raw, line-numbered `.scad` source and cross-checked against
  `hardware/mechanical-interface.md`, not re-read from the dimensional-spec
  document's own prose and nodded along. One self-correction is disclosed
  here for full transparency, consistent with the adversarial mandate
  applying to this reviewer's own draft conclusions and not only to the
  design document's: an early working note in this same review initially
  mis-recalled REQ-306's clearance-margin figures (+8mm radial / +3mm axial)
  as an interface-file **CONFIRMED** value; re-checking
  `hardware/mechanical-interface.md` §B5 directly (line 516) before
  finalizing any finding showed they are explicitly labeled **"Proposed
  clearance margin (ASSUMPTION)"** — the `.scad` file's own comments already
  correctly match this ASSUMPTION labeling, so this did not become a
  labeling-defect finding, but the correction itself is recorded as evidence
  the independence mandate was actually exercised, not merely asserted.
- **Scope**: Full Rev 3 design —
  `hardware/mechanical/bench-imu-01-enclosure.scad` and
  `hardware/mechanical/bench-imu-01-dimensional-spec.md` in full, cross-checked
  against `hardware/mechanical-interface.md` in full (Board Geometry, M1
  motor CONFIRMED dimensions, flywheel ASSUMPTION dimensions, REQ-306
  clearance-envelope margins, B1/B3 Open Items). `requirements/requirements.md`'s
  Rev 3 mechanical/safety requirements (REQ-306, REQ-307, REQ-308, REQ-309,
  REQ-403) read in full for acceptance-criteria context. Electronics-side
  Rev 3 changes (`hardware/schematic/` — U6 Motor-Rail Supervisory Controller,
  motor driver, etc.) were **not** re-reviewed here; that is the Electronics
  discipline's own Cycle 3/4/5 scope, already closed out above. This cycle
  takes the electrical interface as given (as published in
  `hardware/mechanical-interface.md`) and reviews only the mechanical
  response to it, per this agent's own defined scope boundary.
- **Tooling disclosure**: Unlike Mechanical Reviewer Cycle 1/Cycle 2 (which
  explicitly disclosed no OpenSCAD/CAD rendering tool was available in that
  environment), this cycle independently confirmed a real, working `openscad`
  2026.08.30 binary **is** available in this environment
  (`/opt/homebrew/bin/openscad`), together with a working Python geometry
  stack (`trimesh`/`numpy-stl`/`rtree`, installed into a scratch venv after
  the system Python's PEP-668 policy blocked a direct `pip install`). This
  materially raised the rigor available this cycle: rather than hand/formula
  tracing alone, this cycle **rendered the full assembled design** (confirmed
  an exact match to the dimensional-spec's own claimed manifold stats — Genus
  6, 4610 vertices, 9240 facets — corroborating that the stated self-check
  render is genuine, not fabricated) and separately rendered/`intersection()`
  -tested two specific sub-geometries directly — the flywheel-bay `base()`
  module alone, and a standalone reproduction of the hub-collar/disk Z-stack
  using literal values transcribed from the real file — to empirically
  confirm two findings (MISS-008, MISS-009) that would otherwise have rested
  on formula-tracing alone. Methodological note: OpenSCAD's `use <file>`
  statement imports only modules/functions, not top-level variables, so the
  two empirical sub-geometry checks used small standalone scratch `.scad`
  files with literal values hardcoded from the real file's own named
  parameters at the cited line numbers, rather than importing the real file
  directly — the literal values themselves are transcribed directly from the
  real file and cited by line number in each finding below, so this is a
  disclosed methodological detail, not a shortcut around checking the actual
  design.
- **Parallel sub-scans run**: None dispatched as separate sub-agent scans
  this cycle — the full 10-item checklist plus the task's 5 specified focus
  areas (REQ-306 arithmetic, the 2 self-disclosed items, the REQ-403
  disposition, the new 3-piece assembly joints, and the motor-mounting
  ASSUMPTION's consistency) were worked as a single integrated pass by this
  Mechanical Reviewer.
- **rubber-duck premise review run in parallel?**: Not indicated as run for
  this cycle on the Mechanical discipline. This report does not rely on or
  duplicate any such review.
- **KiCad / CAD tool cross-checks used**: None — no KiCad project exists for
  Bench-IMU-01 (unchanged since Mechanical Reviewer Cycle 1's own note); this
  cycle's CAD cross-check was instead performed with the now-available
  `openscad` binary directly against the actual `.scad` source, as described
  in Tooling disclosure above.

### Checklist Results

Full checklist per `.github/skills/mechanical-review/SKILL.md`, all 10 items
independently worked (not a partial spot-check), plus the 5 task-specified
focus areas folded into the relevant checklist rows below:

| # | Checklist item | Result | Notes |
|---|---|---|---|
| 1 | PCB mounting (standoff positions/diameters, boss integrity) | **PASS** | Independently re-derived against `hardware/mechanical-interface.md`'s Mounting table — unchanged from Rev 2's already-RESOLVED MISS-001-adjacent geometry; no Rev 3 change touched the PCB standoffs themselves. No new finding. |
| 2 | Connector accessibility (cutout position/size/orientation) | **PASS** | J1–J4/SW1/D1 cutouts independently re-checked against §10's connector table; MC-1's disclosed 42mm interior wire run (the motor/encoder connector) is honestly stated as long-but-workable in the source document and independently confirmed to be an accurate, not understated, figure. No new finding — the *routing path* for MC-1's wiring is a separate defect, see item 4/7 (MISS-009) below. |
| 3 | Component height clearance (top + bottom vs. interface file) | **FAIL — MISS-008 (CRITICAL)** | Radial clearance (checklist item 4 below) independently re-verified correct: `fw_bay_inner_r`=39.5mm vs. 38.0mm required (REQ-306), genuine +1.5mm margin beyond the interface's own ASSUMPTION-labeled +8mm radial allowance. **Vertical/axial clearance is not correct**: the Z-stack formula chain computing `fw_disk_bottom`/`fw_disk_top`/`fw_clearance_top` omits the hub collar's own height, producing a physically impossible disk position (see Finding 1). This invalidates §7's specific vertical-clearance claim and the overall-height table in §3, even though the underlying radial arithmetic and REQ-308's ~150mm envelope goal are otherwise fine. |
| 4 | Internal clearance/interference (parts vs. walls, parts vs. parts, parts vs. bosses) | **FAIL — MISS-008 (CRITICAL), MISS-009 (HIGH), MISS-010 (HIGH)** | Three independent, unrelated interference defects found: (1) flywheel disk/hub-collar solid interpenetration (MISS-008); (2) the motor-wire duct's void is never actually subtracted from the enclosure's outer solids, so the intended wire path is itself solid material (MISS-009); (3) the pre-existing, self-disclosed Rev-2-origin base-tab/lid-skirt interference (MISS-010), confirmed still present and confirmed to have no tracked backlog entry. Motor-mount bolt geometry (4×M3 at (fw_cx±6, fw_cy±6)) independently re-checked clear of both the 15.5mm platform edge (5.3mm margin) and the central shaft hole — no defect found there. Cap-fastener bolt-circle (6×M3 at r=48.0mm, 0/60/120/180/240/300°) independently re-checked clear of the wire bridge (~24.85mm at its closest, ~90°) and of everything else — no defect found there either. |
| 5 | Fastener placement (wall thickness around bosses; no conflicts) | **PASS**, with a load-verification caveat carried under item 9 | All 3 fastener classes (6×M2.5 PCB lid, 4×M3 motor mount, 6×M3-into-heat-set-inserts cap) independently re-checked for physical placement conflicts — none found; each boss has adequate surrounding wall material and no boss/fastener pair collides with another. The design's own explicit disclosure that no fastener-*load* calculation was performed (§12) is a real gap but is a rigor/verification finding, not a placement defect — tracked as MISS-011 under item 9, not here. |
| 6 | Wall thickness (structural *and* the Lead's own stated 3D-printability rule) | **Finding — MISS-010 (HIGH)** for the pre-existing tab/skirt zone; otherwise **PASS** | The containment wall itself (`containment_wall_t`=4.0mm = 2×`min_wall_t`) independently re-confirmed to meet and exceed the stated 2.0mm print-safety minimum everywhere along its continuous annulus — no thin spot found by direct radial re-measurement at every angular sample checked. The one wall-thickness-adjacent defect this cycle is MISS-010, a pre-existing solid-solid *interference* (too little clearance, not too little wall) at the base-tab/lid-skirt joint — tracked there, not duplicated here. |
| 7 | Assembly order (physically achievable sequence, nothing trapped) | **FAIL** | §14's 6-step sequence independently re-walked against the corrected-vs-as-modeled geometry: **Step 5** ("slide the flywheel disk onto the hub collar") is not physically achievable as modeled, because the disk's own modeled Z-position already overlaps the collar's modeled volume before any sliding occurs (MISS-008). **Step 4** (route the motor/encoder wiring through the wire duct before closing the PCB lid) is not physically achievable as modeled either, because the duct itself is solid material along its intended path (MISS-009). No part is found permanently trapped with zero access once these two defects are corrected — the underlying 3-piece order (Base → PCB Lid → Containment Cap) is otherwise sound and each piece independently confirmed accessible for fastening in sequence. |
| 8 | Basic print-fit tolerance (stated clearance allowance applied consistently everywhere) | **PASS** | The design's own stated 0.2mm/side `fit_clearance` independently re-checked at every piece-to-piece mating interface this Rev 3 assembly actually has: (a) base-wall/PCB-lid-skirt joint (unchanged from Rev 2, where this convention was already independently verified) — consistent; (b) the new cap-skirt/base-flange joint (§11.F) — independently re-confirmed the same 0.2mm/side allowance is applied here too, not merely asserted; no interface found where the allowance is claimed once and silently dropped elsewhere. |
| 9 | Basic manufacturability/3D-printability (overhangs/bridges within the Lead's own rule; min wall thickness everywhere) | **Finding — MISS-011 (MEDIUM)** | The self-disclosed borderline motor-wire bridge span (9.0–9.42mm) was independently re-derived from the `.scad` file's own duct-span geometry and confirmed to fall within, not beyond, the design's own stated 10mm max-bridge-span rule (94.2% of the limit at worst, not over it) — no new finding on the bridge span itself; this is disclosed correctly and does not need reclassifying. The one manufacturability finding this cycle is separate: the REQ-403 containment disposition's specific wall-thickness/fastener-retention adequacy claims rest on qualitative reasoning, not any impact-energy or pull-out-under-shock calculation, and this gap is disclosed 3 times in the source document itself (§8/§12/§13.3) but was not yet entered into the tracked backlog — MISS-011. Min wall thickness independently spot-checked at multiple points beyond the single reference wall the design document itself cites (containment wall, PCB-lid roof, cap flange, base floor) — no location found below the stated 2.0mm minimum other than the already-tracked pre-existing MISS-010 interference zone (which is an interference, not a thin-wall, defect) and Rev 2's own already-tracked MISS-007 (unchanged, LOW-adjacent-MEDIUM, non-gating, carried forward). |
| 10 | Interface-value traceability (every dimension traces to `hardware/mechanical-interface.md` or is explicitly ASSUMPTION/ESTIMATE, never silently blended with CONFIRMED) | **PASS** | Independently spot-checked the highest-stakes labels in this revision: M1 motor body dimensions (CONFIRMED, DS-MTR-021, correctly labeled throughout both the `.scad` comments and the dimensional-spec); flywheel dimensions (ASSUMPTION, correctly labeled throughout); REQ-306's own +8mm radial/+3mm axial clearance margins (ASSUMPTION per interface line 516 — see the Independence statement's self-correction above — correctly labeled as ASSUMPTION in both the `.scad` file's comments and the dimensional-spec, not silently upgraded to CONFIRMED anywhere found); the 4×M3/16mm motor bolt-pattern (the interface file's own Open Item B1, left OPEN by the Circuit Engineer) is consistently and explicitly labeled as the Mechanical Lead's own unconfirmed ASSUMPTION everywhere this cycle found it used (`.scad` header comments, dimensional-spec §4/§8/§16) — no location found where it is silently treated as settled/CONFIRMED. No mislabeling defect found. |

### Findings

#### Finding 1 — Flywheel disk Z-stack formula omits hub-collar height, producing a physically impossible disk position

- **Issue**: `fw_disk_bottom` — the parameter that positions the bottom face
  of the flywheel disk — is computed as
  `fw_motor_bell_top + fw_hub_standoff` (=28.5+3.0=31.5mm), which omits the
  hub collar's own height (`fw_hub_collar_h`=6.0mm) entirely. As modeled, the
  disk's bottom 3.0mm occupies the same space as the top 3.0mm of the hub
  collar it is supposed to rest on top of.
- **Rationale**: The same `.scad` file, elsewhere, computes the shaft length
  the motor needs to expose as
  `fw_shaft_exposed_len_needed = fw_hub_collar_h + fw_hub_standoff` (=9.0mm,
  line 392) — a formula that only makes sense if the collar sits *above* the
  standoff and the disk sits *above* the collar (i.e., additively stacked:
  standoff, then collar, then disk). `fw_disk_bottom`'s own formula
  contradicts this internally within the same file: it positions the disk as
  if the collar's height were zero, directly at the top of the standoff,
  rather than at the top of the collar. This is not a matter of
  interpretation or a rounding/tolerance question — it is an internal
  self-contradiction between two formulas in the same source file, one of
  which (line 392) treats collar height as additive and one of which (line
  565) does not.
- **Datasheet Source**: `hardware/mechanical/bench-imu-01-enclosure.scad`
  lines 384–392 (`fw_hub_standoff`=3.0mm DERIVED, `fw_hub_collar_h`=6.0mm
  ASSUMPTION, and the file's own
  `fw_shaft_exposed_len_needed = fw_hub_collar_h + fw_hub_standoff` formula)
  cross-referenced against lines 561–574 (`fw_disk_bottom`, `fw_disk_top`,
  `fw_clearance_top` — the Z-stack formula chain containing the omission);
  `bench-imu-01-dimensional-spec.md` §14 Assembly Step 5 ("slide the flywheel
  disk onto the hub collar," independently re-quoted from the source text,
  not paraphrased) and §7 (the REQ-306 vertical-clearance claim, which
  depends on the now-shown-incorrect `fw_disk_top`/`fw_clearance_top`
  values).
- **Failure Mechanism**: Empirically confirmed, not just formula-traced: a
  standalone `.scad` file was built this cycle with the exact literal Z
  values the real file's own formulas produce (collar Z=[28.5, 34.5], disk
  Z=[31.5, 36.0]) and rendered through the real `openscad` binary available
  in this environment. `intersection()` of the two solids produced a genuine,
  fully manifold overlap solid — not an empty result, not a degenerate
  sliver — with volume ≈145.0mm³ via `trimesh` (vs. 150.8mm³ by hand
  calculation, a difference within normal STL-facet-discretization tolerance,
  the same tolerance class already precedented by the RESOLVED MISS-002
  finding's own volume cross-check). The overlap's Z-bounds are exactly
  [31.5, 34.5] — precisely the disk's bottom 3.0mm and the collar's top
  3.0mm, matching the hand-derived prediction exactly. A second reading was
  also independently ruled out this cycle: one might ask whether the collar
  is simply meant to sit fully *inside* the disk's hollow bore rather than
  below it — but the collar's own height (6.0mm) exceeds the disk's own
  thickness (4.5mm), so the collar cannot be fully contained within the
  disk's Z-envelope either; there is no consistent geometric reading under
  which both parts occupy their stated positions without interference. As
  literally modeled — and as the assembly instructions' own wording requires
  (the disk must slide onto/over the collar's full height before coming to
  rest on top of it) — the disk cannot occupy the Z-position the file
  assigns it without physically colliding with the collar first.
- **Affected Component**: Flywheel disk (`fw_disk_bottom`/`fw_disk_top`);
  hub collar (`fw_hub_collar_od`/`fw_hub_collar_h`); every parameter
  downstream of `fw_disk_top` in the Z-stack (`fw_clearance_top`, the
  containment wall's own height, REQ-306's vertical-clearance claim, and the
  REQ-403 containment envelope's specific sizing).
- **Recommended Fix**: Correct `fw_disk_bottom` to
  `fw_motor_bell_top + fw_hub_standoff + fw_hub_collar_h`
  (=28.5+3.0+6.0=**37.5mm**, not the current 31.5mm), and propagate the
  resulting +6.0mm shift through `fw_disk_top` (=**42.0mm**, not 36.0mm) and
  `fw_clearance_top` (=**45.0mm**, not 39.0mm). Because the corrected
  `fw_clearance_top` (45.0mm) now exceeds the current `fw_cap_outer_top`
  (43.0mm) by 2.0mm, the cap's overall height — and therefore the assembly's
  overall Z-envelope, §3's height table, and the containment wall's own
  height — must also grow by at least 2.0mm plus wall thickness to keep the
  flywheel disk actually enclosed under corrected geometry. This is not a
  local, one-line fix: it cascades through the entire vertical stack above
  the motor bell and must be re-verified end-to-end (REQ-306 vertical
  margin, REQ-403 containment envelope, overall assembled height, and the
  §14 assembly sequence) once corrected, not just patched at the single point
  of the original error.
- **Severity**: **CRITICAL** — per `docs/architecture.md` §7.1, this design
  fails under its own normal, as-documented assembly sequence (Step 5), not
  under a rare or marginal corner case: the flywheel literally cannot be
  assembled as the design's own instructions describe without either the
  collar or the disk being forced into a physically impossible position.
  Blocks PASS.

#### Finding 2 — Motor-wire duct void is never actually subtracted from the enclosure's outer solids; the documented cable-routing path is solid material

- **Issue**: `motor_wire_bridge()`'s duct-void cylinder is only subtracted
  from that module's own local bridging cube. It is never differenced
  against `fw_bay_wall()`'s solid containment-wall annulus or
  `pcb_bay_base()`'s south wall, both of which independently occupy the same
  duct footprint along the intended cable path.
- **Rationale**: `base()` (lines 850–857) is coded as a flat `union()` of 4
  solids (floor, motor platform, flywheel-bay wall, PCB-bay base) with no
  top-level `difference()` applied anywhere for the duct void — the void
  subtraction happens only inside `motor_wire_bridge()`'s own return value,
  before that module's result is unioned (not differenced) into the rest of
  `base()`. A `union()` of an already-voided local solid with other,
  unrelated solid geometry does not project that local void through the
  other solids; each of those other solids remains fully solid wherever it
  happens to occupy the same X/Y/Z region as the intended duct.
- **Datasheet Source**: `hardware/mechanical/bench-imu-01-enclosure.scad`
  lines 770–857 (`fw_bay_wall()`, `motor_wire_bridge()`, `base()` — the
  `union()`-only construction independently confirmed directly from the
  source, not inferred); `bench-imu-01-dimensional-spec.md` §10 (connector
  accessibility table, MC-1 row, describing this as a functional wire path)
  and §14 Assembly Step 4 (routing the motor/encoder wiring through this
  duct before closing the PCB lid).
- **Failure Mechanism**: Empirically confirmed via a rendered `base()`-only
  geometry (independently re-rendered this cycle through the real `openscad`
  binary, matching `Status: NoError, Genus: 6, Vertices: 808, Facets: 1636`)
  and a `trimesh` point-containment sweep along the duct's own intended air
  path (Y=92–95mm, r=39.5–42.5mm, taken directly from the duct's own stated
  span in the source): every sampled point along this path returns **solid**,
  not void, at two independent locations along the same nominal path — the
  containment-wall annulus itself (`fw_bay_wall()`), and, a short distance
  further along the same path, the PCB bay's own south wall
  (`pcb_bay_base()`) independently re-blocking it a second time. The
  motor/encoder wiring the design's own assembly instructions direct through
  this "duct" has no physical passage to travel through as modeled; the wire
  would have to pass through solid printed plastic, which is not possible
  without post-print modification (e.g. hand-drilling) not described
  anywhere in the design.
- **Affected Component**: `motor_wire_bridge()` (local duct cutout only, not
  propagated); `fw_bay_wall()` (containment-wall annulus); `pcb_bay_base()`
  south wall; `base()` (top-level union lacking a corresponding top-level
  difference); MC-1 motor/encoder wire connector's documented routing path.
- **Recommended Fix**: Apply the duct-void subtraction at the top level of
  `base()`'s own construction — e.g. wrap the relevant portion of `base()`
  in a `difference()` that removes the duct cylinder from the union of
  `fw_bay_wall()` and `pcb_bay_base()` as well as from
  `motor_wire_bridge()`'s own local cube — then re-verify via a render plus
  a containment sweep (as independently performed in this review, not a
  visual inspection alone) that the full Y=92–95mm / r=39.5–42.5mm path is
  void end-to-end after the fix, not merely void within
  `motor_wire_bridge()`'s own local solid as it is today.
- **Severity**: **HIGH** — per `docs/architecture.md` §7.1, this is a real,
  likely-to-occur defect under completely normal assembly (not a rare
  corner case), defeating an explicitly planned wiring path (§10 MC-1, §14
  Step 4) — but it is neither an unconditional first-power-on failure of the
  board's core function nor a safety hazard, and a practical (if inferior)
  workaround exists (routing the motor/encoder wiring external to the
  enclosure rather than through the intended internal duct), consistent with
  the HIGH rather than CRITICAL definition.

#### Finding 3 — Pre-existing Rev 2-origin base-tab/lid-skirt solid interference (~190mm³) is disclosed but was never entered into the tracked backlog

- **Issue**: A genuine, ~190.06mm³ solid-solid interference between
  `base_tabs()` and `lid_shell()`'s skirt band exists at all 4 corners of
  the primary lid/base joint. This defect pre-dates Rev 3 (it is a Rev
  2-origin defect, explicitly self-disclosed as out of scope for the Rev 3
  motor/flywheel task in the design document's own §11.C, and explicitly
  flagged there for this review's attention) — but a full re-read of this
  file's entire existing backlog (ISS-001 through ISS-026, MISS-001 through
  MISS-007) confirms **no entry currently tracks it**.
- **Rationale**: The overlap sits between `base_tabs()`'s Z=[15.5, 21.1]
  (global) and `lid_shell()`'s skirt band Z=[18.1, 21.1] (global) — a
  genuine 2.0mm-deep (Y), 3.0mm-tall (Z) solid-solid interference at each of
  the 4 corners. Independently reproduced by hand from the disclosed
  geometry: 2.0mm × 3.0mm × 8mm tab width × 4 corners = 192mm³, matching the
  disclosed 190.06mm³ within normal fillet/rounding tolerance — the
  disclosed root-cause narrative and volume figure are independently
  confirmed accurate, not merely re-cited. Being disclosed in prose inside a
  design document is not the same as being tracked in
  `validation/open-issues.md` — the one backlog that actually gates Design
  Complete per `docs/architecture.md` §8 and is machine-checked by
  `tools/check_open_issues.py` — and this defect was in neither
  `ISS-001`–`ISS-026` nor `MISS-001`–`MISS-007` before this cycle.
- **Datasheet Source**: `bench-imu-01-dimensional-spec.md` §11.C (full
  root-cause narrative, self-disclosed this revision); `validation/open-issues.md`
  (full re-read this cycle, ID range ISS-001–ISS-026, MISS-001–MISS-007 —
  confirmed no existing row references this defect by geometry, component,
  or volume figure).
- **Failure Mechanism**: At each of the 4 corners, the base tab's own solid
  volume and the lid skirt's own solid volume occupy an overlapping
  2.0mm × 3.0mm region — two solids the design intends to be separate,
  mating parts cannot occupy the same space. If sliced and printed exactly
  as modeled, the lid cannot seat fully onto the base at any of the 4
  corners without either forcibly deforming/crushing ~190mm³ of printed
  material or the corner remaining proud/unseated — likely surfacing as a
  visibly non-flush lid-to-base fit and/or interference with that corner's
  own fastener engagement (the same fastener joint MISS-004 already
  addresses, RESOLVED in Rev 2). This is directly analogous in class — a
  real, fit-blocking, mating-face solid interference — to the already-
  RESOLVED MISS-002 finding (degenerate base-tab gusset, also a base-tab
  defect), not to the smaller, non-blocking MISS-007 class (a thin-but-
  independently-usable isthmus with no actual overlap).
- **Affected Component**: `base_tabs()` and `lid_shell()`'s skirt band, all
  4 corners (`bench-imu-01-enclosure.scad`) — the same base/lid mating-face
  joint MISS-002/003/004 already govern.
- **Recommended Fix**: Apply the same fix pattern already proven on this
  exact joint this project (MISS-002/003/004's resolution): resize or
  reposition either `base_tabs()`'s Z-extent/Y-position or `lid_shell()`'s
  skirt-band Z-extent so the two solids no longer share the same
  2.0mm × 3.0mm region at any of the 4 corners, then re-verify via a full
  render plus a boolean `intersection()` check (zero-volume expected)
  rather than a hand estimate alone — matching the rigor already used to
  close out MISS-002.
- **Severity**: **HIGH** — per `docs/architecture.md` §7.1, a real,
  structurally-blocking mating-face interference at all 4 corners of the
  primary lid/base joint, not a rare corner case and not merely thin or
  degraded. Assessed by direct analogy to the already-RESOLVED MISS-002
  precedent (same defect class: solid-solid interference at a load-bearing
  mating/fastening feature), not the MEDIUM MISS-007 precedent (a thin-but-
  usable isthmus, not an actual overlap). Rated HIGH and left OPEN rather
  than silently treated as already-accepted, since a HIGH finding can only
  be dispositioned RESOLVED or ACCEPTED-RISK with a named human Chief
  Engineer sign-off per this file's own Rules section — neither has happened
  for this specific defect yet, even though it has existed since Rev 2.

#### Finding 4 — REQ-403 containment disposition's specific wall-thickness/fastener-retention claims rest on qualitative reasoning, not an impact/shock calculation

- **Issue**: The REQ-403 safety disposition's reasoning for why a 4.0mm
  containment wall (=2× the design's own general-purpose print-safety
  minimum) and 6×M3 heat-set-insert cap fasteners are adequate specifically
  against a detached-flywheel impact is stated qualitatively — not derived
  from the disposition's own stated ~122J/100g kinetic-energy hazard figure
  via any impact-energy-absorption, wall-deflection-under-impact, or
  fastener-pull-out-under-shock calculation.
- **Rationale**: The document discloses this gap itself, honestly, in three
  separate places (§8, §12, §13.3) rather than silently asserting rigor it
  did not perform — this is a disclosure/verification-rigor gap on a
  safety-critical claim, not a proven physical defect (no calculation has
  been performed showing the wall or fasteners are actually inadequate
  either). REQ-403's own process is explicitly designed to have a human
  safety reviewer weigh exactly this kind of qualitative-vs-rigorous
  judgment call before Design Complete — this finding's purpose is to ensure
  that gap is visible to that reviewer via the tracked backlog, not just
  buried in three separate footnotes of a design document.
- **Datasheet Source**: `bench-imu-01-dimensional-spec.md` §8 (REQ-403
  disposition narrative and physics table — independently reproduced this
  cycle and confirmed arithmetically correct as far as it goes), §12
  (fastener-placement table, explicit "no fastener-load calculation
  performed" self-disclosure), §13.3 (explicit self-disclosed lack of
  print-orientation-vs-impact-load analysis for the cap).
- **Failure Mechanism**: Not an active/demonstrated failure — a verification
  gap. The disposition argues qualitatively ("substantially thicker than
  structural minimum," "multiple fasteners provide redundancy") rather than
  quantitatively; if the wall or fasteners were in fact inadequate against
  the stated hazard energy, the failure mode would be containment breach
  under a real detachment event — but this review found no basis, either in
  the source document or independently, to conclude they *are* inadequate,
  only that adequacy has not been demonstrated by calculation.
- **Affected Component**: Containment wall (`containment_wall_t`=4.0mm);
  6×M3 heat-set-insert cap fasteners; the REQ-403 safety disposition
  (`bench-imu-01-dimensional-spec.md` §8) as a whole.
- **Recommended Fix**: Before this proposal is brought to the human safety
  reviewer, either (a) perform a basic impact-energy/wall-deflection or
  fastener-pull-out-under-shock estimate tied to the disposition's own
  ~122J/100g figure (even an order-of-magnitude hand calculation would
  materially strengthen the disposition's credibility), or (b) explicitly
  carry the qualitative-only status forward as a named, disclosed limitation
  in the material presented to the human reviewer, so that reviewer's
  decision is made with full awareness that the specific numbers are not
  independently load-verified — only the general topology (continuous wall,
  no rotation-plane opening, independently confirmed true this cycle — see
  Positive Findings below) is.
- **Severity**: **MEDIUM** — non-gating. Per `docs/architecture.md` §7.1,
  this is a disclosed rigor/traceability gap on a proposal still pending
  human review, not an independently-demonstrated physical defect in the
  current geometry — no confirmed malfunction or hazard has been shown, only
  an absence of the calculation that would rule one out. Must still be
  explicitly surfaced to the human REQ-403 safety-review gate rather than
  silently dropped, since that gate is exactly where this class of
  qualitative-vs-rigorous judgment call belongs.

### Positive Findings

Credited explicitly, since an adversarial review should also record what
independently checks out, not only what does not:

- **REQ-403's containment-topology claim independently verified TRUE**: the
  claim that the containment design provides "a continuous 4mm wall, no
  rotation-plane opening, bolted cap" was independently re-derived from the
  containment wall's own radial/angular geometry (continuous annulus,
  r=39.5–43.5mm, Z=2.0–39.0, no gap or seam found anywhere in its angular
  sweep) and from the cap-fastener bolt-circle's own angular positions
  (0/60/120/180/240/300°, none of which coincide with or require an opening
  in the rotation plane itself). This specific claim holds up under
  independent scrutiny — it is the *specific vertical sizing* built on top
  of this correct topology (Finding 1) and the *specific load-adequacy*
  claims (Finding 4) that do not yet independently check out, not the
  topological claim itself.
- **Two of the Mechanical Lead's own self-check catches, independently
  re-confirmed as genuine and correctly fixed**: Error #3 (a wire-bridge/
  motor collision) and Error #4 (a missing floor disc) are both confirmed,
  by direct inspection of the current source, to be correctly resolved in
  the geometry as it stands today — good technique on the Mechanical Lead's
  part, simply not extended to the separate wire-duct defect this cycle
  found (MISS-009, a bug in the same general area but not the same specific
  geometry Error #3 addressed).
- **Interface-value traceability (checklist item 10) is clean**: no
  ASSUMPTION/CONFIRMED/ESTIMATE mislabeling found anywhere this cycle
  checked, including at the specific point (REQ-306 margins) where this
  reviewer's own first-pass note briefly got it wrong before independent
  re-verification — see the Independence statement above.
- **Cap-skirt/base-flange fit interface (§11.F) independently re-confirmed
  correct**: the new 3rd piece's own mating interface (Containment Cap to
  Base flange) was independently re-derived and found to correctly apply
  the same 0.2mm/side `fit_clearance` convention already used elsewhere —
  this is the newest joint in the design (introduced this revision) and it
  received the same rigor as the older, already-proven base/lid joint (see
  checklist item 8).
- **Motor-mount bolt geometry independently confirmed safe**: the 4×M3
  motor-mount bolt holes (at (fw_cx±6, fw_cy±6), radius 8.485mm from the
  platform center) are independently re-confirmed clear of both the 15.5mm
  platform edge (5.3mm margin) and the central shaft hole, and the
  off-board/bracket-mounted motor-mounting approach's own ASSUMPTION
  labeling (4×M3/16mm bolt pattern, unconfirmed) is used consistently
  throughout the design wherever this reviewer checked for it — no location
  found where it is silently treated as CONFIRMED.

### Verdict

- **Verdict**: **CONDITIONAL**
- **Open CRITICAL count**: 1 (MISS-008)
- **Open HIGH count**: 2 (MISS-009, MISS-010)
- **Open MEDIUM count (non-gating)**: 1 new this cycle (MISS-011), plus
  Rev 2's own already-open MISS-007 carried forward unchanged (untouched by
  Rev 3, not re-litigated here).
- **What independently checks out with no error found**: PCB mounting
  (item 1), connector accessibility (item 2), radial clearance under
  REQ-306 (item 3's radial half), fastener *placement* geometry across all
  3 fastener classes (item 5), print-fit tolerance applied consistently at
  every piece-to-piece interface including the new cap joint (item 8),
  interface-value traceability with no mislabeling anywhere checked
  (item 10), and — critically for the REQ-403 question this cycle was asked
  to focus on — the containment design's **topological** claim (continuous
  wall, no rotation-plane opening, bolted cap) independently verified true.
- **What's blocking a clean PASS**: MISS-008 (CRITICAL — the flywheel disk's
  own Z-stack formula omits the hub collar's height, producing a physically
  impossible disk position that is empirically confirmed, not merely
  formula-traced, and that invalidates the specific vertical-clearance
  numbers behind both REQ-306's axial claim and REQ-403's containment
  envelope sizing) and two HIGH findings (MISS-009 — the motor-wire duct is
  solid, not void, along its intended path; MISS-010 — a pre-existing,
  self-disclosed but previously untracked ~190mm³ base-tab/lid-skirt
  interference).
- **Also open, non-gating but should be dispositioned before Design
  Complete**: MISS-011 (MEDIUM — REQ-403's specific wall-thickness/
  fastener-retention claims rest on qualitative, not calculated, reasoning;
  honestly self-disclosed by the design document 3 times but not previously
  tracked).
- **Independent assessment of the REQ-403 containment proposal's
  credibility** (the specific question this cycle was asked to answer,
  since a human safety review is gated on it): The proposal's **general
  topology is credible** — the claim of a continuous, seamless containment
  wall with no rotation-plane opening and a bolted (not merely friction-fit
  or snap-fit) cap is independently re-derived from the actual geometry and
  confirmed true, not just asserted. However, the proposal's **specific
  numbers are not yet credible to bring to the human gate as currently
  written**, for two independent reasons found this cycle: first, MISS-008
  means the flywheel does not actually fit within the modeled/verified
  clearance envelope at all under the design's own stated assembly sequence
  — the specific containment-cap height and clearance figures cited in §8's
  physics table are computed against a Z-stack that is internally
  self-contradictory, so those specific numbers cannot be trusted until the
  Z-stack is corrected and the containment envelope is re-verified against
  the corrected geometry end-to-end (not just patched locally). Second,
  MISS-011 means that even once MISS-008 is fixed, the specific
  wall-thickness and fastener-retention numbers going into that human
  review still rest on qualitative, not calculated, reasoning — a gap the
  document already discloses honestly but that has not yet been closed or
  explicitly flagged for the reviewer's attention via the tracked backlog.
  **Recommendation: do not bring the REQ-403 disposition to the human safety
  reviewer yet.** Fix MISS-008 first (the containment envelope's own sizing
  is not currently verifiable at all until the flywheel's true Z-position is
  corrected), re-verify the containment envelope against the corrected
  geometry, and carry MISS-011's disclosed qualitative-only status forward
  explicitly into whatever is ultimately presented to the human — at that
  point, the topological soundness already confirmed this cycle plus a
  corrected and re-verified envelope would make for a materially more
  credible submission than what exists today.
- **Next action**: Loop back to the Mechanical Lead (routing decision for
  the Hardware Lead to make) for MISS-008 (fix the `fw_disk_bottom` formula
  and propagate the correction through the full Z-stack and containment
  envelope — CRITICAL, must be fixed before any further progress) and the
  two HIGH findings MISS-009 (make the wire duct actually void along its
  full intended path) and MISS-010 (resolve the pre-existing base-tab/
  lid-skirt interference using the same fix pattern already proven on
  MISS-002/003/004) at minimum — all three should be resolved before this
  design proceeds toward a physical print or toward the REQ-403 human safety
  review. MISS-011 (MEDIUM) should also be addressed or explicitly
  dispositioned, and in either case explicitly carried into the REQ-403
  human-review material rather than left implicit.
