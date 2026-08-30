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
