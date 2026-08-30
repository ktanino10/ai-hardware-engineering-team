# Bench-IMU-01 — Schematic-Equivalent Design Document

**Author**: Circuit Engineer (AI agent) · **Date**: 2026-08-31, revised 2026-09-01 · **Status**: **Revised (Rev 2)** — 3 HIGH findings from Hardware Reviewer Cycle 1 fixed, 2 additional corrections folded in; self-checked against the affected items; **ready for Hardware Reviewer re-review** (not a first review — see `validation/design-review.md` for Cycle 1's full findings and its Addendum)

## Revision changelog

**Rev 2 (2026-09-01)** — Circuit Engineer rework addressing
`validation/design-review.md` Cycle 1 findings, per
`.github/agents/circuit-engineer.agent.md` ("When you receive Hardware
Reviewer findings... address every CRITICAL and HIGH finding explicitly").
Only this document was modified; `validation/open-issues.md`,
`validation/design-review.md`, and `datasheets/evidence-log.md` are owned
by the Hardware Reviewer / Hardware Lead and are not touched here.

- **ISS-011 (HIGH, fixed)** — The IMU I2C bus on MCU pins PB10/PB11 was
  mislabeled "I2C1" throughout this document. Independent research
  (Hardware Lead, this cycle, DS-MCU-052/053) confirmed PB10/PB11 are
  actually this part's **I2C2** alternate function. Every reference
  (§2.3, §5.2, §5.3, §6, §11, §12, §14, §16) is corrected I2C1→I2C2. No
  PCB/wiring change — pins are physically unchanged; only the
  peripheral-instance label and the firmware target change. **I2C1 is
  now recorded as entirely free** (a genuine peripheral-margin
  improvement, not a regression).
- **ISS-001 (HIGH, fixed)** — The LDO (U3) EN pin connection was hedged
  ("if the exact package variant... has an active EN pin..."). Independent
  research (Hardware Lead, this cycle, TI SBVS320D Rev D) confirmed EN
  (pin 3, DBV package) is mandatory on every package variant, with no
  internal bias. §3.4 and §12 now state a firm, unconditional EN→VIN tie
  as a committed design decision, with a new explicit `EN_VIN` net.
- **ISS-002 (HIGH, addressed)** — The design's own arithmetic against
  REQ-101 was correct, but Independent Review found the real-world USB-C
  vSafe5V ceiling (4.75–5.5V) is wider than REQ-101's stated band
  (4.75–5.25V), leaving effectively zero margin against the LDO's 5.5V
  Recommended Operating Condition ceiling (though 0.5V/9% of real headroom
  remains under its 6.0V Absolute Maximum Rating — not a damage risk). New
  §3.5 analyzes this explicitly and **recommends an ACCEPTED-RISK
  disposition** (with a component-change flag as the alternative) for the
  Hardware Lead to route to the human Chief Engineer per
  `docs/architecture.md` §8. This finding is **not** closed by this
  document — the disposition decision is the Hardware Lead's/human Chief
  Engineer's to make.
- **ISS-006 (MEDIUM, corrected)** — §4.1/§4.2's BOOT0 discussion is
  corrected: BOOT0 is muxed onto **PA14** (already this design's SWCLK
  pin), not PB8. PB8 does physically exist on this package (contra this
  document's original §4.1/§16 claim) but its real function is an
  alternate I2C1_SCL pin (DS-MCU-053), unrelated to BOOT0. The design's
  final decision (no physical BOOT0 circuit, rely on the nBOOT_SEL
  default) is unchanged — only the reasoning is corrected.
- **ISS-010 (LOW, corrected)** — The MCU VDD Absolute Maximum Rating lower
  bound, previously UNKNOWN, is now resolved at **−0.3V** (confirmed by
  the Hardware Reviewer against ST DS12992 Rev4 Table 18). §1/§16 updated.
- **Out of scope this revision (unchanged, left for a later disposition
  pass)**: ISS-004, ISS-005, ISS-007, ISS-008, ISS-009. Not marked
  resolved; not touched beyond what already existed.
- **Self-check**: re-run against Hardware Reviewer checklist items 1, 2,
  6, 7, 13, and 16 (§15) — items 6/7/13 map most directly onto ISS-001/
  ISS-011/ISS-006; items 1/2 onto ISS-002/ISS-010.

## 0. Tooling honesty statement

`kicad-list_projects` returned empty this session — **no KiCad project
exists yet** for this repository. The connected KiCad MCP tools
(`extract_project_netlist`, `analyze_schematic_connections`,
`validate_project`, `run_drc_check`, `export_bom_csv`,
`generate_pcb_thumbnail`, etc.) are **read/analyze-only**: every one of
them operates on an existing `.kicad_pro`/`.kicad_sch`/`.kicad_pcb` file.
There is no tool available in this environment to create a new KiCad
project or schematic from scratch.

This document is therefore a **structured schematic-equivalent Markdown
document**, not an actual KiCad project — a net-by-net / block-by-block
description, a full MCU pin-assignment table, a parts list specific to
this design, and a design-rationale log with Evidence ID citations. This
mirrors the same tooling-honesty convention already used by the
Mechanical Lead for CAD (no verified CAD tool connected in this
environment either). It is **not** a substitute for laying the design out
in real KiCad once that tooling exists — it is the best-available
faithful representation given the current toolset, sufficient for an
independent Hardware Reviewer to review net-by-net.

This also happens to match this cycle's own stated scope: REQ-502 states
"This is a paper/document design exercise this cycle, not a production
schedule — no physical PCB fabrication or physical power-on happens in
this session." A structured document deliverable is therefore not merely
a workaround for missing tooling, but the actually-correct artifact type
for this design cycle.

Once a KiCad project exists, step 6 of my own procedure
(`.github/skills/schematic-design/SKILL.md`) requires self-checking with
`extract_schematic_netlist` / `analyze_schematic_connections` /
`validate_project` — that step is **not applicable yet** and is called out
explicitly rather than silently skipped (see §15, Hardware Reviewer
checklist item 16 discussion).

## 1. Scope and inputs (not re-litigated)

Per task framing, the following are **human-approved and not up for
re-litigation** in this design cycle. This document only flags part-level
problems discovered during design (routed to Hardware Lead / Component
Engineer per `.github/agents/circuit-engineer.agent.md` "Out of scope");
it does not unilaterally swap parts.

| Role | Part | Package | Key specs | Evidence |
|---|---|---|---|---|
| MCU (U1) | STMicroelectronics STM32G031K8T6 | LQFP-32 | Arm Cortex-M0+ ≤64MHz, 64KB Flash + 8KB SRAM, 2×I2C/2×SPI/2×UART, SWD+JTAG, no native USB | DS-MCU-012–021 |
| IMU (U2) | Bosch Sensortec BMI270 | LGA-14 (2.5×3.0×0.83mm) | 6-axis accel+gyro, I2C≤1MHz FM+ or SPI≤10MHz, VDD ROC 1.71–3.6V / AMR −0.3…+3.6V, VDDIO ROC 1.2–3.6V | DS-IMU-001–017, 070 |
| LDO (U3) | Texas Instruments TLV75533PDBVR | SOT-23-5 | Fixed 3.3V, Vin ROC 1.45–5.5V / AMR 6.0V, 500mA max, dropout typ220/max238mV@500mA, Iq 25µA | DS-PWR-001–011 |

Requirements are sourced from `requirements/requirements.md` (human
signed off) and cited by REQ-ID throughout this document. Component
candidate comparisons live in `bom/component-selection.md` and are not
repeated here except where a specific cited number (e.g. the LDO thermal
estimate) is directly reused.

**RESOLVED this revision (ISS-010)** — the STM32G031K8T6 VDD Absolute
Maximum Rating **lower bound**, carried forward from
`bom/component-selection.md` as unconfirmed, is now confirmed at
**−0.3V** (upper bound remains 4.0V, DS-MCU-012), independently verified
by the Hardware Reviewer this cycle directly against ST's primary
datasheet (DS12992 Rev4, Table 18) — see §16 item 2. Full AMR is
therefore **−0.3V to +4.0V**. The chosen operating point, 3.3V, sits
deep inside both the confirmed Recommended Operating Condition
(1.7–3.6V, DS-MCU-013) and the now-fully-confirmed AMR — no violation in
either direction, and this is no longer an open gap.

## 2. Shared resources — fixed first, serially (per SKILL.md step 1)

### 2.1 Rails

Two rails exist on this board:

- **5V (VBUS)** — pre-regulator, from the USB-C receptacle (J1), nominal
  5.0V, USB-spec tolerance 4.75–5.25V (REQ-101). Feeds: LDO (U3) input,
  ESD protection IC (U4) VBUS pin.
- **3V3** — post-regulator, LDO (U3) output, fixed 3.3V (DS-PWR-003).
  Feeds: MCU (U1) VDD/VDDA/VBAT, IMU (U2) VDD/VDDIO, both header 3V3 reference
  pins (SWD J3, UART J2), status LED (D1) via R5, I2C pull-ups (R3/R4).

Single 3.3V logic level throughout (REQ-102, "Should") — no
level-shifting circuitry anywhere in this design. USB 5V VBUS is isolated
from all logic by the LDO; USB D+/D− (which would otherwise be a
5V-tolerance concern) are unpopulated per REQ-105 (power-only port, no
data), so 5V-tolerance is moot.

### 2.2 Ground scheme

**Single ground net/plane for the whole board.** REQ-301 fixes a single
2-layer PCB (no daughtercards/stacked boards) — for a design this small
and this simple (3 active ICs, no motor/analog-precision/RF section
requiring a split or star-ground topology), a single unbroken ground
pour on one layer is the correct, standard choice, not an oversight. All
GND pins (U1 VSS×2, U2 GND+GNDIO, U3 GND, U4 GND, R1/R2 CC pull-down
returns, C1–C9 return sides, both header GND pins, LED cathode return)
tie to this one net. This is stated here explicitly per the design task's
own instruction not to leave it implicit (see also §8, Grounding block,
and §14 item 15/checklist item 11 in the self-check).

### 2.3 Pin allocation (summary; full table in §11)

Fixed once, before any sub-block was designed in detail, to avoid
rework/conflicts across blocks:

| Function | MCU pin | Confidence |
|---|---|---|
| SWDIO | PA13 | HIGH — dedicated STM32 debug pin, not an alternate function |
| SWCLK | PA14 | HIGH — dedicated STM32 debug pin, not an alternate function; also this MCU sub-family's BOOT0 boot-mode-select mux pin — corrected this revision, see §4.2 (ISS-006) |
| I2C2 SCL | PB10 | HIGH — **corrected this revision (ISS-011)**: independently confirmed against the primary AF table (DS-MCU-052, ST DS12992 Rev4 Table 16) that PB10/PB11 map to I2C2, not I2C1 as this document originally (incorrectly) stated |
| I2C2 SDA | PB11 | HIGH — as above |
| USART2 TX | PA2 | MODERATE-HIGH — very common STM32 USART2 mapping; not individually re-verified against the exact AF table this session (see §16) |
| USART2 RX | PA3 | MODERATE-HIGH — as above |
| Status LED drive | PA5 | ASSUMPTION — arbitrary free GPIO choice (also the conventional "Nucleo LED" pin on many ST boards), no AF conflict since it's used as plain GPIO output |
| NRST | NRST (pin 4) | HIGH — dedicated reset pin |
| BOOT0 | not populated this cycle | see §4.2/§4.4/§16 — **corrected this revision (ISS-006)**: BOOT0 is muxed onto PA14 (already committed to SWCLK above), not PB8; PB8 does physically exist on this package but its function is unrelated (alternate I2C1_SCL) |

This leaves **USART1 and LPUART1 both free** (only USART2 is used) —
satisfies the Component Engineer's own note that one of the MCU's 2 UART
peripherals should remain genuinely free (only 1 of 2 committed here,
comfortably; actually both USART1 and LPUART1 remain free since USART2 is
the one consumed — even better margin than "one free" required). **Also,
new this revision (ISS-011)**: since the IMU bus correctly occupies I2C2
(not I2C1 as originally labeled), **I2C1 is now recorded as entirely
free** as well — both of PB10/PB11's I2C1-sibling pin pairs (PB6/PB7
primary AF, PB8/PB9 secondary AF, DS-MCU-053) remain unused. This is a
genuine improvement in peripheral margin versus this document's original,
mistaken understanding — not a regression. See §11 for the full free-GPIO
inventory.

## 3. Block 1 — Power input + regulation

### 3.1 Connector choice: USB-C (over Micro-USB-B)

**Decision: USB-C.** Documented trade-off:

| | USB-C (chosen) | Micro-USB-B (rejected) |
|---|---|---|
| Ecosystem | Modern connector, aligned with current laptops/chargers, many of which are USB-C-only now | Legacy/declining — increasingly hard to source new cables/chargers for it |
| Insertion | Reversible/no wrong-way insertion | Must be inserted right-way-up |
| Extra parts needed | 2× 5.1kΩ CC1/CC2 pull-down-to-GND resistors (R1, R2) required for a compliant source to enable VBUS (DS-CONN-001) | None — no CC-equivalent negotiation exists |
| Precedent value | This is the repository's **first** end-to-end design cycle — sets a forward-compatible connector precedent for future boards | N/A |

The added complexity (2 resistors, one-time, ~$0.01 BOM impact) is minor
compared to Micro-USB-B's compounding disadvantage (an already-legacy
connector whose availability will only keep declining over this
project's lifetime). **R1 = R2 = 5.1kΩ**, CC1→GND and CC2→GND
respectively (DS-CONN-001 — USB-IF Type-C spec fixed Rd value for a
UFP/sink). Without these resistors, a compliant USB-C source will not
enable VBUS at all, even for a power-only sink — this is a hard functional
requirement, not an optional nicety.

Since REQ-105 restricts this port to power delivery only (no
data/enumeration), a full 24-pin SuperSpeed-capable USB-C receptacle is
not needed — a basic USB 2.0-only USB-C receptacle (VBUS, GND, CC1, CC2,
D+, D− — the electrically "used" contacts, D+/D− present on the connector
for cable compatibility but left unpopulated on this board) is sufficient
and keeps BOM cost down (supports REQ-501's soft cost target). **J1's
exact MPN is not formally selected in this design cycle** — see §10 for
the illustrative real part (GCT USB4125) used only to ground the
mechanical height estimate.

### 3.2 ESD / transient protection (REQ-402)

**Part selected: STMicroelectronics USBLC6-2SC6** (SOT-23-6, 4-line TVS
diode array), one of the three example families named in the design task
(ON Semi NUP2105L / TI TPD2E009 / STMicro USBLC6-2SC6). Real datasheet:
https://www.st.com/resource/en/datasheet/usblc6-2sc6.pdf. New metadata
record: `datasheets/stmicroelectronics_usblc6-2sc6_rev-unknown.md`.

Key specs (DS-PROT-001): clamp voltage 17V max @5A (8/20µs), standoff
voltage 5.25V (clears USB VBUS's 5.25V nominal ceiling per REQ-101 with
zero margin at the absolute worst case — see §16 flag), breakdown voltage
6V min, I/O capacitance 2.5pF typ/3.5pF max (low enough not to matter for
a power-only, non-data line anyway), SOT-23-6 package, IEC 61000-4-2
±15kV air / ±8kV contact ESD immunity rating.

Pinout/topology (DS-PROT-002): I/O1 = pins 1 & 6 (D+ channel), I/O2 =
pins 3 & 4 (D− channel), VBUS = pin 5, GND = pin 2.

**Wiring decision**: since REQ-105 is power-only (no USB data lines
connected at all), only the **VBUS (pin 5) and GND (pin 2)** channel is
wired into the signal path — VBUS routes through U4's VBUS pin before
reaching C1/U3's input, GND ties to the common ground net. **I/O1 and
I/O2 (the D+/D− clamp channels) are left unpopulated/NC** since there is
no D+/D− signal on this board to protect. This is a deliberate,
documented deviation from the part's full 4-line "typical application"
(which normally ties all 4 I/O pins to a USB data pair) — justified
because there is no data pair to protect in this design (REQ-105).

**This single real part is not run through a full ≥3-candidate Component
Selection comparison**, per the design task's own explicit instruction —
a real, datasheet-grounded single part is sufficient for this
supporting/protection role, unlike the three primary BOM parts.

### 3.3 Reverse-polarity protection (also REQ-402)

REQ-402 requires "basic transient/ESD and reverse-polarity protection
appropriate for a hand-handled connector." Transient/ESD is satisfied by
§3.2 above. For reverse-polarity: **no discrete series diode is added.**
Rationale: USB-C (like Micro-USB-B) is a **mechanically keyed** connector
— VBUS and GND are fixed to specific physical contacts regardless of
cable/plug orientation; a user cannot physically insert a compliant USB-C
plug "backwards" in a way that swaps VBUS and GND polarity (unlike, e.g.,
a bare 2-pin JST/barrel-jack connector, which genuinely can be reversed
by a user). A series Schottky diode was considered and rejected: it would
cost ~0.3–0.5V of dropout for marginal benefit given the mechanically-keyed,
non-field-deployed (bench-use, REQ-201) nature of this connector. This
trade-off is flagged explicitly for the Hardware Reviewer to challenge if
they read REQ-402's "reverse-polarity" language more broadly (e.g. to
include a mis-wired/jury-rigged power source, not just a standard cable
insertion) — see §16.

### 3.4 Regulation: TLV75533PDBVR (U3) per its own reference app circuit

VBUS (after U4's ESD channel) → **C1 = 1µF ceramic** (LDO input
decoupling) → U3 IN pin. U3 OUT pin → **C2 = 0.47µF ceramic** (LDO output
decoupling) → 3V3 rail. Both values are the **minimum** ceramic values
from TI's own reference application circuit for this exact part
(datasheet SLVSDV4) — DS-PWR reference-circuit evidence already cited in
`bom/component-selection.md`'s Power Regulator section, reused verbatim
here, no deviation.

**EN pin — fixed this revision, no longer hedged (ISS-001)**: U3's EN pin
(pin 3 on the ordered DBV/SOT-23-5 package) is **firmly and
unconditionally tied directly to VIN (U3 pin 2)** — always-enabled, per
TI's own recommended connection for an always-on application, which
matches this design's use case exactly. This is now an explicit net in
the net list (§12, `EN_VIN`) and parts-list note (§13), not a
layout-time judgment call.

This replaces this document's original hedge: *"U3's EN pin (if present
on this specific variant/package...) is tied to enable-always per the
standard reference circuit; if the exact TLV75533 package variant used
here has an active EN pin requiring a level, tie it to VIN directly...
flagged as a minor implementation detail to confirm against the literal
pinout diagram at layout time."* Independent research (Hardware Lead,
this cycle, TI SBVS320D Rev D §4 Table 4-1 pin description, §5.5
Application Information, §6.4 typical application) confirms:

- EN is a **mandatory** pin present on **every** package variant of this
  part family (DQN pin 3, DBV pin 3, DYD pin 3, DRV pin 4 — there is no
  "no-EN"/EN-less variant of this device). The original hedge's premise
  ("if the exact... variant... has an active EN pin") was not actually a
  live possibility — every ordering-option variant has one.
- The EN pin has **no internal pull-up or pull-down bias** — only
  high-impedance leakage (I_EN ≈ 10nA at EN = 5.5V). The datasheet's only
  internal "pulldown resistance" specification (≈120Ω) is the *output*
  discharge switch engaged while the device is disabled, not an EN-pin
  bias network, and must not be confused with one.
- A genuinely floating EN pin therefore leaves the enable state
  undefined: the rail could fail to enable at all (a dead board at
  bring-up, easily misdiagnosed as a different fault), or sit in the
  undefined 0.3–1.0V threshold gray zone and chatter/misbehave from
  coupled digital-switching noise on the board. This is real, undefined
  behavior — not a theoretical nitpick.

Tying EN→VIN removes this ambiguity entirely, at **zero component cost**
(one additional trace/via, no resistor, no new part). No other electrical
conclusion elsewhere in this document changes as a result — enable-always
was already the design's intended behavior; it is now a firmly committed
net rather than a deferred, hedged assumption.

AMR/ROC check: U3 Vin = 5.0V nominal (4.75–5.25V per REQ-101) is within
AMR 6.0V (DS-PWR-002) with 0.75–1.25V margin, and within ROC 1.45–5.5V
(same evidence) — but the **top of the USB tolerance band (5.25V) leaves
only ~0.25V of headroom under the 5.5V ROC ceiling**, tighter than the AMR
margin. This is noted explicitly as a real, if small, margin consideration
rather than glossed over — it does not exceed any limit against REQ-101's
own stated band. **§3.5 below addresses why this margin is actually
tighter still against the real-world USB-C spec, with this revision's
explicit disposition of that gap (ISS-002) — this is no longer left as a
silent flag.**

### 3.5 LDO input-voltage margin disposition: the real-world USB-C vSafe5V ceiling (ISS-002, new this revision)

**This entire subsection is new this revision.** §3.4's AMR/ROC check
above is arithmetically correct against REQ-101's own stated figure
(4.75–5.25V), but Independent Review found that REQ-101's figure does not
capture the actual governing specification for the connector this design
uses.

**The gap**: independent research (Hardware Lead, this cycle) established
that the real-world input voltage a spec-compliant USB-C/USB-PD source is
permitted to present — the governing "vSafe5V" range defined by the
USB-IF — is **4.75V to 5.5V**, wider than REQ-101's stated 4.75–5.25V
legacy-USB tolerance band. At that wider, genuinely spec-compliant
worst-case ceiling (5.5V), margin against the LDO's own 5.5V Recommended
Operating Condition maximum (DS-PWR-002) is **effectively zero** — not
the ≈0.25V §3.4 computes against REQ-101's narrower figure. A real,
fully-compliant USB-C charger could legitimately present a Vin at which
this design's own arithmetic no longer shows headroom.

**Why this is not a damage/safety risk**: even at the worst-case, fully
spec-compliant 5.5V input, the LDO still sits a full 0.5V (≈9%) under its
6.0V Absolute Maximum Rating (DS-PWR-002) — real headroom remains, and no
component damage is expected at 5.5V. Exceeding a Recommended Operating
Condition (as opposed to an Absolute Maximum Rating) is, per TI's own
datasheet convention, a "may not meet all specified electrical
characteristics" caveat, not a "may be damaged" one — i.e. the practical
worst case here is a regulator that is still safe but may not be fully
within its datasheet-guaranteed output tolerance/PSRR/dropout
specification at that exact instant, not a burnt part.

**My disposition recommendation**: I recommend **(a) ACCEPTED-RISK**,
routed by the Hardware Lead to the human Chief Engineer for the named
sign-off `docs/architecture.md` §8 requires ("HIGH findings may become
ACCEPTED-RISK only with named human sign-off"), for these reasons:

- The failure mode at the true worst case is a soft, bounded
  regulation-margin concern (possible minor output-tolerance/PSRR/dropout
  degradation at an edge-case input voltage that most real chargers won't
  actually reach in practice), not a hard functional or safety failure —
  the 6.0V AMR headroom means there is no damage risk to disposition
  around.
- This is explicitly a bench/prototype design (REQ-502: "paper/document
  design exercise this cycle, not a production schedule"), where a
  narrow, well-understood, bounded edge-case risk is a reasonable
  engineering trade rather than a reason to force a part change.
- The alternative — swapping the LDO — is not something I can decide or
  execute unilaterally regardless of my own judgment here (per my own
  agent instructions' "Out of scope": part selection is the Component
  Engineer's call, routed through the Hardware Lead, not mine to make
  even when I've identified a part-level concern during design).

**Option (b), noted but not chosen**: if the Hardware Lead judges the
margin unacceptable even as a bounded, non-damage risk (e.g. because this
design is expected to graduate beyond a bench prototype, where "may not
meet all specified electrical characteristics" at the input rail becomes
a real functional-reliability concern rather than an academic one), I
flag — without unilaterally implementing — that the Component Engineer
could be asked to evaluate an alternate LDO with a wider Vin ROC ceiling
(e.g. a part rated to 5.5V ROC with more headroom, or one rated well
above 5.5V/6.0V entirely) as a drop-in-footprint or near-drop-in
replacement. I have not selected or proposed a specific alternate part
number — that evaluation is the Component Engineer's, not mine, per my
own agent instructions.

**This finding is not closed by this document.** Per `docs/architecture.md`
§8, I cannot self-resolve a HIGH finding into ACCEPTED-RISK — I can only
recommend a disposition with reasoning and hand the routing decision to
the Hardware Lead (and, for ACCEPTED-RISK specifically, the human Chief
Engineer). See §16 item 10 for the tracked disposition-pending record.

## 4. Block 2 — MCU periphery

### 4.1 VDD / VDDA / VBAT pin handling and decoupling

STM32G031K8T6 LQFP-32 power-pin count (DS-MCU-046, **MODERATE
confidence** — distributor/aggregator sources datasheets.com, octopart.com,
snapeda.com converge on a structurally coherent 32-row pin table; the raw
ST PDF pin table was not independently re-parsed this session; a
lower-detail source, embeddedrelated.com, separately claimed "1 VDD / 1
VSS" which does not match the VSS=2 count below — flagged as an
unreconciled discrepancy, though VDD=1 is corroborated by both sources so
the decoupling plan below is unaffected either way):

| Pin | Number | Count | Decoupling |
|---|---|---|---|
| VDD | 17 | ×1 | **C3 = 100nF ceramic**, VDD-to-GND, placed as close to pin 17 as layout allows |
| VSS | 1, 16 | ×2 | Ground return, no decoupling cap needed (tie to GND plane) |
| VDDA | 5 | ×1 | **C4 = 100nF ceramic**, VDDA-to-GND, no ferrite bead — tied directly to the 3V3 rail (ASSUMPTION: no ADC-precision requirement exists anywhere in `requirements/requirements.md`, so a simple direct tie is a reasonable simplification rather than an oversight) |
| VBAT | 32 | ×1 | Tied directly to 3V3 rail (ASSUMPTION, standard generic-STM32 practice — no RTC coin-cell backup battery in this design, so VBAT can share the main 3V3 supply) |
| NRST | 4 | — | See §4.3 |

Only **1 VDD pin** exists on this LQFP-32 part (both sources agree on
this specific count), so the "100nF per VDD pin" generic STM32 convention
resolves to exactly one 100nF cap here (C3) — not the multi-cap fan-out
some larger STM32 packages (with 4+ VDD pins) would need. This was
verified rather than assumed generically, per the design task's explicit
instruction.

**Correction this revision (ISS-006)**: the pin-count table above (from
DS-MCU-046, distributor/aggregator sources) does **not** list a PB8/PB9
pin, which this document originally read as evidence that PB8 is not
bonded out on this package at all (see the original §4.2 reasoning this
replaces, below). Independent research (Hardware Lead, this cycle,
DS-MCU-051) found this premise was wrong: **PB8 does physically exist**
on this package, corroborated across the sources checked this cycle,
correcting the §4.1/§16 UNKNOWN this document originally carried on that
specific point. (PB8's *exact pin number* within the ranges above was not
independently re-resolved to full certainty against the primary ST PDF —
a residual, non-blocking pin-numbering detail carried forward at §16 item
1/§11, not a re-opening of the VDD/VSS decoupling analysis above, which is
unaffected either way.) PB8's real function turns out to be an alternate
I2C1_SCL mapping (DS-MCU-053), not BOOT0 — see §4.2 immediately below for
the corrected BOOT0 picture.

### 4.2 BOOT0 / nBOOT_SEL handling

This required real web research since STM32 boot-mode conventions differ
materially across families (STM32F1-era generic conventions do **not**
carry over to STM32G0).

**Corrected this revision (ISS-006)** — this subsection's original
reasoning had a factual error at its premise (see the changelog at the
top of this document): it assumed BOOT0 was multiplexed with PB8 and,
finding no PB8 in this design's pin-count research, concluded the whole
BOOT0-pin question might be moot for this exact part. Independent
research (Hardware Lead, this cycle, DS-MCU-050/051, corroborated by
RM0454 and ST Community references) corrects this on two independent
points at once:

- **BOOT0 is actually multiplexed onto PA14** on this STM32G0x0
  sub-family — not PB8. PA14 is already committed in this design as the
  SWD **SWCLK** pin (§2.3, §4.4).
- **PB8 does physically exist** on this package after all (DS-MCU-051,
  corroborated §4.1 above) — but its real alternate function is
  **I2C1_SCL** (secondary AF mapping, DS-MCU-053), entirely unrelated to
  boot-mode selection. The original UNKNOWN about whether PB8 was even
  bonded out is now resolved (it is); it was simply never the BOOT0 pin
  to begin with.

The facts that remain unchanged from the original analysis:

- **nBOOT_SEL option byte factory default = 1** (DS-MCU-044, MODERATE
  confidence — corroborated by 2 independent community sources, a Stack
  Overflow STM32G030F6 boot-mode thread and a CSDN technical blog, both
  citing the same FLASH_OPTR reset value; not independently re-confirmed
  against the raw ST RM0454 reference manual table this session). With
  `nBOOT_SEL=1`, the physical BOOT0 **pin is ignored entirely** and the
  device boots unconditionally from Main Flash per the `nBOOT0`/`nBOOT1`
  option bits — i.e., the STM32G0 boot-mode architecture is
  option-byte-driven, not physical-pin-driven, by default. This is a
  materially different scheme from STM32F1, where the BOOT0 pin's level
  is sampled directly at every reset.

**What this correction actually changes**: with BOOT0 now correctly
understood to sit on PA14 (not PB8), a dedicated physical BOOT0 circuit
was **never actually possible** on this design's pin allocation in the
first place — PA14 was committed to SWCLK before BOOT0's real location was
even known (§2.3, step 2 of `SKILL.md`'s "fix shared resources serially
first"), so there was no scenario in which a separate BOOT0 pull
circuit could have been added without giving up SWCLK. This is a
materially more complete justification than the original (mistaken)
"PB8 might not exist" reasoning, though it does **not** change the design
decision itself.

**No brick risk**: independently reconfirmed this cycle that SWD-based
recovery/reprogramming remains available **regardless of `nBOOT_SEL`'s
actual value** — the Cortex-M0+ debug port is independent of the
application boot-mode sequence, so even if the factory default assumption
above turns out wrong at bring-up, the board is recoverable via the
already-present SWD header (§4.4) without any additional hardware.

**Design decision (unchanged)**: **no physical BOOT0 pull-down resistor or
header is populated this cycle.** The design relies entirely on the
nBOOT_SEL=1 factory default (boot from Flash unconditionally); the SWD
header (§4.4) remains the primary and sufficient programming/debug path,
already required independently by REQ-002/REQ-107. This is an explicit
scope-limiting decision flagged to the Hardware Lead/Hardware Reviewer
(§16), not a silent omission — if a future firmware bring-up session
discovers the factory default is not what was assumed, or that
nBOOT_SEL needs to be reprogrammed via SWD (which is itself possible using
only the already-present SWD header, without any extra hardware, and
carries no brick risk per the point above), that is recoverable without a
board re-spin.

### 4.3 NRST decoupling + optional manual reset button (REQ-004, Could)

Per ST's own application note **AN5096** "Getting started with STM32G0
MCUs hardware development" (DS-MCU-047): the NRST pin has an internal
pull-up (~40kΩ typical) — no external pull-up resistor is needed. ST's
own recommended external circuit is a **100nF ceramic capacitor (C5) from
NRST to GND** for EMI/glitch immunity, with an **optional
normally-open pushbutton (SW1) from NRST to GND in parallel** for manual
reset. This design includes both: C5 (always populated) and SW1
(populated, satisfying REQ-004's Could-priority manual reset button). No
external debounce circuit beyond C5 is needed — C5 itself provides
adequate debounce for a manual pushbutton on a reset line (standard
practice; the MCU's own reset circuitry is not timing-sensitive to a few
extra milliseconds of bounce).

### 4.4 SWD debug header (REQ-107)

**4-pin header (J3): VDD (3V3 reference) / SWCLK / GND / SWDIO.**
Explicitly **no NRST, no SWO** on this header. This matches ST's own
minimal-header convention on the NUCLEO-G031K8 (same MCU family) CN4
connector (DS-CONN-002, corroborated by SEGGER's own "Connecting to
STM32 Nucleo boards" wiki page, ST Community posts, and stm32-base.org).
This directly answers the design task's question of whether a reset line
or SWO is conventionally included on a minimal SWD header: **no** — a
4-pin VDD/SWCLK/GND/SWDIO header is the established minimal convention,
and this design follows it exactly, satisfying REQ-107 literally (4-pin
SWD, matching "the selected MCU family's standard debug interface").
SWD (2-wire: SWDIO+SWCLK) is used rather than JTAG (5-wire) since SWD is
the lower-pin-count, more commonly used debug interface for Cortex-M0+
parts and is ST's own default recommendation; JTAG remains available on
the silicon (shared pins) but is not broken out to a header this cycle —
not required by any REQ, and would cost 3 more header pins for no
required benefit.

## 5. Block 3 — IMU interface

### 5.1 I2C vs. SPI

**Decision: I2C** (REQ-104 permits either). Rationale: simpler (2 signal
pins vs. SPI's 4), matches the most common breakout-board convention for
this exact part, and this design has no bandwidth pressure — REQ-001 only
requires ≥100Hz ODR, which even a slow I2C bus satisfies with enormous
headroom (a single 6-ax12-byte accel+gyro read at 400kHz I2C, including
register-address overhead, takes on the order of ~0.3–0.4ms — comfortably
faster than the 10ms period a 100Hz ODR requires, leaving >95% of each
period idle). SPI (≤10MHz, DS-IMU per component-selection) would be faster
still but that speed is not needed here.

### 5.2 I2C pull-up sizing (target bus speed: Fast-mode, 400kHz)

Sized using the NXP UM10204 I2C-bus specification formula (new evidence
category `DS-IFACE`, DS-IFACE-001) rather than assuming a generic 4.7kΩ
value without checking suitability:

- `tr ≈ 0.8473 × Rp × Cb` (rise-time vs. pull-up-value vs. bus-capacitance
  relationship)
- `Rp,min = (Vcc − VOL,max) / IOL` (current-sink floor)

With Vcc=3.3V, VOL,max=0.4V, IOL=3mA (Fast-mode DC spec, DS-IFACE-001):
**Rp,min ≈ 966Ω**. With an assumed bus capacitance **Cb≈50pF (ASSUMPTION**
— compact ≤60×40mm 2-layer board, single slave device, short traces,
reasoned as a generous planning estimate covering pin capacitance of both
devices plus PCB trace parasitics): **Rp,max ≈ 7.08kΩ** for a 300ns
Fast-mode rise-time budget.

**Selected: R3 = R4 = 4.7kΩ** (standard E24 value), on SCL and SDA
respectively, both to the 3V3 rail. At the assumed Cb=50pF, actual rise
time ≈**199ns** — comfortably within the 300ns budget (≈101ns/≈34%
headroom). **Sensitivity check** (documented honestly rather than
asserting blanket margin): if actual board parasitic capacitance turns
out higher than the 50pF planning estimate, 4.7kΩ remains compliant up to
**Cb≈75pF** (tr≈299ns, right at the 300ns ceiling) — if PCB layout
ultimately reveals materially more capacitance than assumed (e.g. from
unexpectedly long traces), the resistor value should drop to 3.3kΩ or
2.2kΩ at layout time. This is flagged as a layout-stage confirmation
item, not a currently-known problem.

Both the STM32G031 (**I2C2** — corrected this revision, ISS-011, was
mislabeled I2C1; Fast-mode Plus capable up to 1Mbit/s per DS-MCU-017,
which describes the part's 2×I2C peripheral count/capability generically
and applies equally to either instance since both are the same IP block)
and the BMI270 (I2C, Fast-mode Plus capable up to 1MHz, DS-IMU-007)
support Fast-mode Plus, which structurally exceeds the sink-current
capability needed for plain Fast-mode — so no per-pin current concern on
either device at the chosen 400kHz target speed.

### 5.3 IMU pin-level wiring

Full 14-pin BMI270 LGA pin function table (DS-IMU-077, traced to Bosch's
own datasheet PDF via this session's search):

| Pin | Function | This design's connection |
|---|---|---|
| 1 | SDO | **→ GND** (selects I2C address 0x68 — DS-IMU-076; simplest/default address since only one IMU is on this bus) |
| 2 | ASDx (aux I2C/SPI data) | NC — aux sensor interface unused |
| 3 | ASCx (aux I2C/SPI clock) | NC — aux sensor interface unused |
| 4 | INT1 | NC — see below |
| 5 | VDDIO | 3V3 rail, decoupled by **C7 = 100nF ceramic** |
| 6 | GNDIO | GND |
| 7 | GND | GND |
| 8 | VDD | 3V3 rail, decoupled by **C6 = 100nF ceramic** |
| 9 | INT2 | NC — see below |
| 10 | OCSB (aux SPI CS) | NC — aux sensor interface unused |
| 11 | OSDO (aux SPI SDO) | NC — aux sensor interface unused |
| 12 | CSB | **→ VDDIO** (selects I2C mode — DS-IMU-075; tying to GND or toggling would select SPI instead) |
| 13 | SCx (SCL/SCLK) | **I2C2 SCL** (MCU PB10), pulled up by R3 — corrected this revision, ISS-011 (was mislabeled I2C1 SCL) |
| 14 | SDx (SDA/SDI) | **I2C2 SDA** (MCU PB11), pulled up by R4 — corrected this revision, ISS-011 (was mislabeled I2C1 SDA) |

**INT1/INT2 deliberately left NC** — this design uses **I2C polling**
(host reads new data on a timer), not interrupt-driven acquisition. This
is a deliberate scope decision, not an omission: REQ-001's ≥100Hz ODR
target is easily satisfiable by polling (see §5.1 timing-budget analysis),
so no interrupt line is needed for this benchmark. A future cycle
targeting higher ODR or lower host CPU load could reconsider wiring
INT1/INT2 to spare MCU GPIOs (several remain free, see §11) — this would
be a low-cost future addition, not a re-spin-forcing omission.

**Decoupling**: **100nF ceramic on VDD (C6) and 100nF ceramic on VDDIO
(C7)**, each placed as close to the package as layout allows — per the
BMI270 datasheet's own §7.3.3 "Recommended Schematic," p.30 (DS-IMU-074).
No deviation from the datasheet's own recommended circuit. An optional
1µF bulk capacitor near the IMU (C9) is included for extra noise margin,
also per the same datasheet section.

### 5.4 IMU AMR/ROC compliance

VDD=VDDIO=3.3V. Within VDD AMR −0.3V…+3.6V (DS-IMU-004) and VDD ROC
1.71–3.6V. VDDIO's own ROC is 1.2–3.6V per the approved-part summary; no
separate VDDIO AMR ceiling distinct from the general ~3.6V figure was
found in prior research (DS-IMU-006 caveat carried forward, not re-resolved
this session) — 3.3V sits safely under either reading.

## 6. Block 4 — Host communication (UART header)

**4-pin header (J2): TX / RX / GND / 3V3** (REQ-106), labeled from the
board's (MCU's) own perspective: TX = PA2 = MCU's USART2 transmit output
(an external USB-serial adapter's RX connects here), RX = PA3 = MCU's
USART2 receive input (an external adapter's TX connects here). This
satisfies REQ-106 exactly ("4-pin UART header (TX, RX, GND, 3V3) for host
communication via an external USB-serial adapter").

**USART1 and LPUART1 both remain free** — the design only commits USART2.
This exceeds the Component Engineer's own note that "one" UART peripheral
should remain genuinely free (both of the *other* two remain free here,
since USART2 is the *only* one consumed of the MCU's 2 USART + 1 LPUART
complement — "2 UARTs" in the approved-part description already accounted
for USART2 as the consumed one). Similarly, on the I2C side (§5): **I2C1
is now entirely free**, new this revision — the IMU bus correctly uses
I2C2 (PB10/PB11), not I2C1 as this document originally (incorrectly)
labeled it (ISS-011, see the changelog at the top of this document and
§11). This is a genuine peripheral-margin improvement versus this
document's original, mistaken understanding, not a regression.

No external crystal is populated — the MCU runs off its internal
HSI16+PLL clock. UART bit-time tolerance at typical baud rates (e.g.
115200) is easily met by the internal RC oscillator's accuracy
class for a point-to-point, short-cable UART link; this keeps BOM
minimal (no crystal, no load caps). Documented as a decision, not an
oversight.

## 7. Block 5 — Status LED (REQ-003, Should)

**GPIO PA5 sources current** (active-high drive) through a series
resistor **R5 = 330Ω** to the LED (D1) anode; cathode returns to GND.
Assumed generic indicator LED, **Vf≈2.0V @ ~4mA (ASSUMPTION** — exact LED
MPN not selected this cycle, a generic low-cost indicator LED is a
reasonable stand-in). Current: I = (3.3V − 2.0V) / 330Ω ≈ **3.94mA** — a
modest, clearly-visible indicator current, well within any generic
STM32 GPIO's drive capability (STM32 GPIOs are conventionally rated
for tens of mA per pin in this class of device; not independently
re-verified against the STM32G031's own IOH/IOL table this session —
flagged as an ASSUMPTION in §16, though 3.94mA is such a small fraction of
any plausible GPIO current rating that this is a low-risk assumption).
Satisfies REQ-003 ("visual status/heartbeat LED", Should) — "heartbeat"
implies firmware toggles PA5 periodically, consistent with driving it as
a plain GPIO output rather than a passive always-on power-indicator LED.

## 8. Block 6 — Grounding

**Single ground plane/net for this entire design**, stated here
explicitly (not left implicit) per the design task's own instruction.
Justification: REQ-301 fixes a single 2-layer PCB; with only 3 active ICs
(MCU, IMU, LDO) plus one protection IC, no motor, no precision-analog
section, and no RF section on this board, there is no structural reason
to split ground planes or use a star-ground topology — a single
continuous ground pour on one of the two copper layers is both the
simplest and the electrically correct choice for a design at this
complexity level. Every GND-role pin across every block (§§3–7) returns
to this one net; this is restated in the full net list, §12.

## 9. Block 7 — Mechanical/Thermal co-design (checklist item 18)

**Explicitly Not Applicable.** REQ-202 states "Vibration/shock
qualification: Won't (not applicable) — No rotating body/motor in this
benchmark, so the `docs/architecture.md` §12 mechanical/thermal co-design
trigger does not apply this cycle." There is no reaction-wheel motor, fan,
or any other rotating body anywhere in this design — Bench-IMU-01 is a
static bench board (MCU + IMU + power only). This checklist item is
written down here as a determination, not silently skipped, per the
design task's own explicit instruction and per my own agent instructions'
checklist item 18.

## 10. Block 8 — Board geometry facts for the (later, separate) Mechanical Lead handoff

**I am not editing `hardware/mechanical-interface.md` — that is the
Mechanical Lead's file, in a later phase.** The following are my own
best real-engineering estimates, recorded here so the Mechanical Lead can
extract them when that phase begins, with CONFIRMED / ESTIMATE /
ASSUMPTION labels applied honestly per item.

| Fact | Value | Confidence | Basis |
|---|---|---|---|
| PCB outline/size | ~55×35mm up to the full 60×40mm REQ-302 target; **recommend designing to the full allowed envelope** for routing/assembly margin given the connector + header count | ESTIMATE | Reasoned from component count (3 ICs + 3 connectors/headers + passives) against REQ-302's stated ≤60×40mm target |
| Connector/header edges | USB-C (J1) on one short edge; UART header (J2) + SWD header (J3) both along one long edge | ESTIMATE | Satisfies REQ-303 (≤2 edges) by construction — 2 edges used total |
| Mounting holes | 4×, near each corner, inset ~3–4mm from board edges, sized for **M2.5** (hole ⌀≈2.7–2.8mm) | ESTIMATE | Satisfies REQ-304 (≥4, M2/M2.5) |
| LQFP-32 (U1) package height | ≈1.4mm nominal | **CONFIRMED** (via JEDEC MS-026 package-family standard, DS-MCU-048 — see caveat below) | JEDEC MS-026 LQFP outline family; corroborated by NXP/JCET package-family references |
| SOT-23-5 (U3) package height | ≈1.1–1.25mm typ/max | **CONFIRMED** (via JEDEC MO-178 package-family standard, DS-PWR-046 — see caveat below) | JEDEC MO-178 SOT-23 outline family; corroborated by a real Nexperia SOT-23-5 outline drawing (SOT8104-1.pdf) |
| USB-C receptacle (J1) height | ≈2.6–3.2mm (representative real part: GCT USB4125, horizontal/top-mount, = 3.16mm) | ESTIMATE (representative-part CONFIRMED, but J1's actual MPN not yet locked) | DS-CONN-003 |
| Micro-USB-B receptacle height (comparison only — not used) | ≈6.5–6.9mm (GCT USB3140=6.5mm; Würth 614105150721=6.9mm) | ESTIMATE (representative-part CONFIRMED) — **comparison-only**, this design chose USB-C | DS-CONN-004 |
| **Tallest component on the board** | **The USB-C receptacle (J1), ≈3.2mm** — clearly taller than the LQFP-32 (≈1.4mm) or the SOT-23-5 (≈1.1–1.25mm) | ESTIMATE (built from a CONFIRMED-by-representative-part height) | Confirms the design task's own hint |

**Caveat on the two "CONFIRMED" package-height rows**: these are
confirmed against the **JEDEC package-family outline standard**
(MS-026/MO-178), not against the STM32G031K8T6's or TLV75533PDBVR's own
literal mechanical drawing page — I did not independently re-pull each
part's own datasheet mechanical drawing this session. Real parts
following these outlines are expected to match the family's standard
height envelope; flagged as CONFIRMED-via-standard rather than
CONFIRMED-via-part-specific-drawing, a distinction worth preserving for
the Mechanical Lead's own rigor.

**Flag to Mechanical Lead**: the connector-type choice (USB-C vs.
Micro-USB-B) materially changes the Z-height budget for any enclosure
(REQ-305) — roughly 3.2mm vs. 6.5–6.9mm for the tallest single component
on the board. This design's USB-C choice keeps the enclosure lid
clearance requirement smaller than a Micro-USB-B design would have.

## 11. Full MCU pin-assignment table (STM32G031K8T6, LQFP-32)

Power/reset pins per DS-MCU-046/051 (MODERATE confidence overall pin
count and numbering; **PB8's existence specifically is now confirmed**,
corrected this revision, ISS-006 — see §4.1). GPIO alternate-function
assignments per §2.3: **I2C2 (PB10/PB11) is now HIGH confidence**,
corrected this revision and independently confirmed against the primary
AF table (DS-MCU-052, ISS-011); USART2 (PA2/PA3) remains MODERATE-HIGH
confidence, standard STM32 convention, not individually re-pulled from
the exact AF table this session — unchanged this revision, out of scope,
see §16.

| Pin # | Name | Function in this design | Notes |
|---|---|---|---|
| 1 | VSS | GND | Power pin |
| 2–3 | (other GPIO, unused this cycle) | NC / free | Available for future use |
| 4 | NRST | NRST net (C5 + SW1) | §4.3 |
| 5 | VDDA | 3V3 (via C4) | §4.1 |
| 6–15 | PA0–PA9 (GPIO, selected used below) | PA2=USART2_TX, PA3=USART2_RX, PA5=LED drive; others free | §2.3, §6, §7 |
| 16 | VSS | GND | Power pin |
| 17 | VDD | 3V3 (via C3) | §4.1 |
| 18–25 | PA10–PA15, PB0–PB1 (selected used below) | PA13=SWDIO, PA14=SWCLK (also this sub-family's BOOT0 mux pin, corrected this revision — ISS-006, §4.2); others free | §4.4 |
| 26–31 | PB2–PB5, PB10, PB11 (selected used below) | PB10=**I2C2**_SCL, PB11=**I2C2**_SDA — corrected this revision, ISS-011 (was labeled I2C1); others free | §5.3 |
| 32 | VBAT | 3V3 (direct tie) | §4.1 |

**PB8/PB9 note (new this revision, ISS-006)**: PB8 and PB9 are now
confirmed to physically exist on this package (DS-MCU-051/053) but are
not shown as a distinct row above — their exact pin numbers were not
independently re-resolved against the primary ST datasheet this session
(a residual, non-blocking pin-numbering uncertainty, §16 item 1); they
fall somewhere within the ranges already listed and are counted in the
free-GPIO inventory below. Their real function is the secondary AF6
mapping for **I2C1_SCL/I2C1_SDA** respectively (DS-MCU-053) — unrelated
to BOOT0, which this document originally (incorrectly) suspected.

Full free-GPIO inventory after this design's allocation (for the
Mechanical/future-firmware team's reference, not individually itemized
above): PA0, PA1, PA4, PA6, PA7, PA8, PA9, PA10, PA11, PA12, PA15, PB0,
PB1, PB2, PB3, PB4, PB5 — 17 GPIOs remain completely free, **plus PB8 and
PB9, now confirmed to exist (corrected this revision, ISS-006/DS-MCU-051
— exact pin numbers not independently re-resolved this session, §16 item
1)**, bringing the free-GPIO count to **19**. This includes both free
UART peripherals (USART1, LPUART1), SPI1/SPI2 (unused this cycle since
I2C was chosen for the IMU, §5.1), and — **new this revision (ISS-011)**
— **I2C1 in its entirety** (PB6/PB7 primary AF mapping, or PB8/PB9
secondary AF mapping, DS-MCU-053), since the IMU bus is now correctly
understood to occupy I2C2 (PB10/PB11), not I2C1 as this document
originally, mistakenly, labeled it. This is a genuine improvement in
peripheral margin versus this document's original understanding — not a
regression.

## 12. Net list summary (net-by-net)

| Net | Connects |
|---|---|
| VBUS_5V | J1 (USB-C VBUS contact) → U4 pin 5 (VBUS) → C1 → U3 IN(pin2) |
| **EN_VIN** *(new this revision, ISS-001)* | **U3 EN(pin3) → U3 IN(pin2)** — firm, unconditional direct tie (always-enabled per TI's own recommended connection, §3.4); electrically the same node as VBUS_5V at U3's IN pin, broken out as its own named net for traceability since this connection was previously hedged/unconfirmed rather than firmly committed |
| CC1 | J1 CC1 contact → R1 (5.1kΩ) → GND |
| CC2 | J1 CC2 contact → R2 (5.1kΩ) → GND |
| 3V3 | U3 OUT → C2 → U1 VDD(pin17)/VDDA(pin5, via C4)/VBAT(pin32) → U2 VDD(pin8, via C6)/VDDIO(pin5, via C7) → R3/R4 (I2C pull-ups) → R5 (LED resistor) → J2 pin "3V3" → J3 pin "VDD" |
| GND | U1 VSS(pins1,16) → U2 GND(pin7)/GNDIO(pin6) → U3 GND → U4 GND(pin2) → R1/R2 return → C1–C9 return sides → D1 cathode (via R5) → SW1 one leg → J1 shell/GND contact → J2 pin "GND" → J3 pin "GND" |
| NRST | U1 NRST(pin4) → C5 → GND; also → SW1 → GND (momentary) |
| SWDIO | U1 PA13(pin?) → J3 pin "SWDIO" |
| SWCLK | U1 PA14(pin?) → J3 pin "SWCLK" (PA14 also carries this sub-family's BOOT0 mux function — corrected this revision, ISS-006, §4.2; no separate BOOT0 net exists, see §13) |
| **I2C2_SCL** *(corrected this revision, ISS-011 — was named I2C1_SCL)* | U1 PB10 → R3 (pull-up to 3V3) → U2 SCx(pin13) |
| **I2C2_SDA** *(corrected this revision, ISS-011 — was named I2C1_SDA)* | U1 PB11 → R4 (pull-up to 3V3) → U2 SDx(pin14) |
| IMU_CSB | U2 CSB(pin12) → VDDIO (tied, selects I2C mode) |
| IMU_SDO | U2 SDO(pin1) → GND (tied, selects address 0x68) |
| UART_TX | U1 PA2 (USART2_TX) → J2 pin "TX" |
| UART_RX | U1 PA3 (USART2_RX) → J2 pin "RX" |
| LED_CTRL | U1 PA5 → R5 (330Ω) → D1 anode |
| (NC) | U4 I/O1(pins1,6), I/O2(pins3,4) — unpopulated, no D+/D− on this board (REQ-105) |
| (NC) | U2 pins 2(ASDx), 3(ASCx), 4(INT1), 9(INT2), 10(OCSB), 11(OSDO) — unpopulated, aux interface + interrupts unused this cycle (§5.3) |
| (NC) | J1 D+/D− contacts — present on the physical connector for cable compatibility, not routed to any MCU/protection pin (REQ-105) |

## 13. Parts list (this design specifically — distinct from `bom/component-selection.md`'s candidate comparison)

| Ref | Part | Value/notes |
|---|---|---|
| U1 | STMicroelectronics STM32G031K8T6 | MCU, LQFP-32 |
| U2 | Bosch Sensortec BMI270 | IMU, LGA-14 |
| U3 | Texas Instruments TLV75533PDBVR | LDO, SOT-23-5, 3.3V fixed; EN (pin 3) tied directly to VIN (pin 2) — firm this revision, §3.4/ISS-001 |
| U4 | STMicroelectronics USBLC6-2SC6 | ESD protection, SOT-23-6 |
| J1 | USB-C receptacle | MPN not formally selected; illustrative real part GCT USB4125/4105 family used for height estimate only (§10) |
| J2 | 4-pin header | UART: TX/RX/GND/3V3 (REQ-106) |
| J3 | 4-pin header | SWD: VDD/SWCLK/GND/SWDIO (REQ-107) |
| SW1 | Momentary pushbutton, N.O. | Manual reset (REQ-004, Could) |
| D1 | Generic indicator LED | MPN not selected; Vf≈2.0V assumed |
| R1, R2 | 5.1kΩ | USB-C CC1/CC2 pull-downs (DS-CONN-001) |
| R3, R4 | 4.7kΩ | I2C SCL/SDA pull-ups (§5.2) — now correctly understood as the I2C2 bus, ISS-011 |
| R5 | 330Ω | LED current-limit resistor |
| C1 | 1µF ceramic | LDO input decoupling (min per TI ref circuit) |
| C2 | 0.47µF ceramic | LDO output decoupling (min per TI ref circuit) |
| C3 | 100nF ceramic | MCU VDD decoupling |
| C4 | 100nF ceramic | MCU VDDA decoupling |
| C5 | 100nF ceramic | NRST filter (per AN5096) |
| C6 | 100nF ceramic | IMU VDD decoupling |
| C7 | 100nF ceramic | IMU VDDIO decoupling |
| C8 | 1–4.7µF (optional bulk) | Near MCU, extra margin, not strictly required |
| C9 | 1µF (optional bulk) | Near IMU, per BMI270 datasheet §7.3.3 |
| MH1–MH4 | Mounting holes | M2.5, ×4, see §10 |

**No BOOT0 pull-down resistor or header is included** — deliberate
decision, §4.2 (reasoning corrected this revision, ISS-006: BOOT0 is
muxed onto PA14/SWCLK, not PB8 as originally written; the design decision
itself is unchanged).

## 14. Mandatory 18-item checklist walkthrough (my own agent instructions)

Every item addressed explicitly; each either cites an Evidence ID/REQ-ID
or states a clear ASSUMPTION/UNKNOWN, per the design task's instruction
not to skip any.

1. **Supply Voltage** — 5V USB VBUS (REQ-101, 4.75–5.25V; real-world
   USB-C vSafe5V ceiling up to 5.5V per independent research this
   revision, ISS-002) → 3.3V regulated (DS-PWR-003). See §2.1, §3.4/§3.5
   (§3.5 now carries an explicit disposition recommendation for the
   vSafe5V margin question, not a silent gap).
2. **Logic Voltage** — single 3.3V logic throughout (REQ-102); no level
   shifting anywhere. See §2.1.
3. **Absolute Maximum Ratings** — MCU VDD AMR **−0.3V to 4.0V** (DS-MCU-012,
   lower bound resolved this revision — ISS-010, §1); IMU VDD/VDDIO
   AMR −0.3…+3.6V (DS-IMU-004); LDO Vin AMR 6.0V (DS-PWR-002). All
   satisfied at the 3.3V/5V operating points used (§3.4, §5.4), including
   at the real-world worst-case 5.5V USB-C input (§3.5) — 0.5V/9%
   headroom remains even there.
4. **Recommended Operating Conditions** — MCU VDD ROC 1.7–3.6V
   (DS-MCU-013); IMU VDD/VDDIO ROC 1.71–3.6V/1.2–3.6V; LDO Vin ROC
   1.45–5.5V (DS-PWR-002; top-end margin against the real-world USB-C
   vSafe5V ceiling is effectively zero — addressed explicitly this
   revision with a recommended ACCEPTED-RISK disposition, §3.5, ISS-002,
   not left as a silent flag). All satisfied against REQ-101's own stated
   band; §3.5 documents the residual real-world-spec margin question.
5. **Current (per-pin and total)** — full computation in
   `hardware/power-budget.md`: ≈16.2mA worst-case / ≈7.0mA typical on the
   3V3 rail vs. 300mA (REQ-103) and 500mA (DS-PWR-003) ceilings — ≈95–97%
   margin either way. See §17 below and the power-budget file itself.
6. **Thermal** — LDO reuses `bom/component-selection.md`'s own computed
   estimate: ≈71°C TJ at 40°C ambient (REQ-201)/300mA load, ≈79°C headroom
   to 150°C max — and this design's real worst-case load (≈16.2mA) is
   ~18× lower than the 300mA figure that estimate already used, so actual
   heating is lower still. See `hardware/power-budget.md` Thermal
   cross-check section. No thermal risk anywhere else on the board (MCU
   and IMU both draw single-digit-to-low-double-digit mA at 3.3V, no
   meaningful self-heating).
7. **Decoupling** — MCU: C3(VDD)/C4(VDDA); IMU: C6(VDD)/C7(VDDIO); LDO:
   C1(in)/C2(out); NRST: C5. All per each part's own recommended values
   (§4.1, §4.3, §3.4, §5.3).
8. **Pull-up/Pull-down** — I2C: R3/R4=4.7kΩ, sized per NXP UM10204
   (DS-IFACE-001, §5.2), on what is now correctly labeled the I2C2 bus
   (corrected this revision, ISS-011); USB-C CC: R1/R2=5.1kΩ per USB-IF spec
   (DS-CONN-001, §3.1); BOOT0: none populated, see §4.2/§16 (reasoning
   corrected this revision, ISS-006: BOOT0 is on PA14, not PB8); NRST: internal
   pull-up only, per AN5096 (DS-MCU-047, §4.3). Separately, not a
   resistor pull but the same "under-specified pin" category: LDO EN is
   now a firm direct tie to VIN rather than a hedge — see item 17 below
   and §3.4 (ISS-001).
9. **Protection** — ESD/transient: USBLC6-2SC6 (DS-PROT-001/002, §3.2);
   reverse-voltage: mechanically-keyed connector, no series diode
   (§3.3, flagged for Hardware Reviewer); overcurrent: none added — no
   overcurrent-prone element exists on this bench design (no motor, no
   high-current output), and USB hosts/hubs already provide upstream
   overcurrent protection per the USB spec, so an additional onboard
   fuse/PTC was not judged necessary — **flagged as a judgment call, not
   independently re-verified this session**, see §16.
10. **Power sequencing** — **none required.** Single 3V3 rail feeds MCU
    (VDD/VDDA/VBAT all tied together) and IMU (VDD/VDDIO tied together, same
    rail) simultaneously; tying VDD=VDDIO on the IMU makes any
    VDD-before-VDDIO (or vice versa) sequencing requirement moot by
    construction — there is no relative timing between two supplies that
    are electrically the same node. The LDO itself has standard monotonic
    single-rail power-up behavior (not separately cited — not a
    multi-rail/sequenced regulator).
11. **Reset** — NRST: internal pull-up + C5 filter cap + optional SW1
    pushbutton, per AN5096 (DS-MCU-047, §4.3).
12. **Interface timing** — I2C: 400kHz target, pull-ups sized for a 300ns
    rise-time budget with the sensitivity analysis in §5.2; both MCU
    (Fast-mode Plus capable, DS-MCU-017) and IMU (Fast-mode Plus capable,
    DS-IMU-007) exceed this target speed's requirements with margin.
    UART: no fixed clock requirement beyond internal-oscillator baud-rate
    tolerance (§6), judged adequate for a point-to-point link at typical
    baud rates.
13. **MCU pin function** — **re-checked this revision (ISS-011, ISS-006)**.
    Full pin table in §11, now correctly showing **I2C2** (not I2C1) on
    PB10/PB11 — independently confirmed via ST's primary AF table
    (DS-MCU-052, ST DS12992 Rev4 Table 16), upgraded from MODERATE to HIGH
    confidence for this specific pin pair. BOOT0/boot-strap pin handling
    in §4.2 corrected: BOOT0 is muxed onto **PA14** (shared with SWCLK),
    not PB8; PB8 does physically exist on this package (DS-MCU-051) but
    its function is I2C1_SCL (DS-MCU-053), unrelated to BOOT0 — the
    physical-bonding UNKNOWN that previously blocked this item is
    resolved (PB8 exists), though the nBOOT_SEL factory-default value
    itself remains community-sourced only, tracked as a residual bring-up
    verification item, not a pin-function unknown (§16). SWD dedicated
    pins (PA13/PA14) remain confirmed HIGH confidence, noting PA14's dual
    SWCLK/BOOT0-mux role explicitly. USART2 alternate-function assignment
    (PA2/PA3) remains MODERATE-HIGH confidence pending AF-table
    re-verification — unchanged this revision, out of scope for this
    cycle's HIGH-finding rework (§16).
14. **Interfaces (I2C/SPI/UART per each datasheet's recommended
    application circuit)** — I2C: BMI270's own recommended schematic
    followed exactly for decoupling/mode-select pins (§5.3, DS-IMU-074/075/076)
    — the MCU-side peripheral is **I2C2**, corrected this revision, ISS-011;
    UART: standard MCU USART2 mapping, no deviation from any datasheet
    recommendation since UART wiring is header-defined, not
    datasheet-constrained; SPI: not used (I2C chosen, §5.1).
15. **Grounding** — single ground net/plane, stated explicitly, §8/§2.2.
16. **Noise** — single solid ground pour (§8); short decoupling-cap trace
    runs recommended (<2mm, AN5096-style guidance, not independently
    re-cited beyond the NRST context); short I2C trace runs recommended
    (keeps actual bus capacitance near the §5.2 50pF planning assumption);
    linear LDO topology (vs. a switching converter) is inherently
    lower-noise, favorable for the IMU's supply quality — relevant since
    IMU measurement noise floor can be supply-noise-sensitive, though no
    specific BMI270 PSRR figure was pulled this session (ASSUMPTION that
    a linear LDO's noise floor is adequate, consistent with the
    Component Engineer's own LDO-vs-switching trade-off discussion in
    `bom/component-selection.md`).
17. **Recommended Application Circuit** — LDO: followed exactly, no
    deviation, **including EN→VIN, fixed firmly this revision (§3.4,
    ISS-001)** — previously a hedged connection, now a firm commitment
    matching TI's own always-enabled reference circuit exactly. IMU:
    followed almost exactly; INT1/INT2 left NC is
    a deliberate, logged deviation (polling instead of interrupt-driven,
    §5.3). MCU: no external crystal populated is a deliberate, logged
    deviation from a "full" application circuit that might include one
    (§6); no physical BOOT0 circuit is a deliberate, logged
    deviation/scope decision (§4.2, reasoning corrected this revision —
    ISS-006). ESD IC: D+/D− channels left unpopulated is a
    deliberate, logged deviation from the part's full 4-line typical
    application (§3.2).
18. **Mechanical/Thermal co-design** — explicitly **N/A**, §9 (REQ-202, no
    rotating body).

## 15. Self-check against the Hardware Reviewer's 16-item checklist (`.github/skills/hardware-review/SKILL.md`)

This is a **self-check only** — it does not substitute for the mandatory
independent Hardware Reviewer pass (`.github/agents/circuit-engineer.agent.md`
"Out of scope": "Declaring your own design reviewed/complete... Independent
review is mandatory regardless of how confident you are"). Intent: catch
the obvious issues myself before handoff.

1. **Voltage violation** — Not found against each part's own ROC (§14
   items 3–4). The tightest margin in the whole design is the LDO's Vin
   ROC top-end: against REQ-101's own stated 4.75–5.25V band this was
   ≈0.25V/4.5% headroom, but **corrected this revision (ISS-002)** — the
   real-world USB-C/USB-PD vSafe5V ceiling is actually up to 5.5V, i.e.
   effectively **zero margin** against the LDO's 5.5V ROC ceiling at a
   legitimate worst-case input. This is not classified as a "voltage
   violation" against the LDO's ROC in the sense of exceeding it (5.5V in
   = 5.5V ROC ceiling, not exceeding it), but the margin is thin enough
   that it is called out explicitly with its own disposition in §3.5
   rather than being silently accepted — see §16 item 10.
2. **Absolute Maximum Rating violation** — Not found. **Resolved this
   revision (ISS-010)**: MCU VDD AMR lower bound is now confirmed at
   −0.3V (Hardware Reviewer verification against ST DS12992 Rev4 Table
   18, §1) — the previous UNKNOWN that partially blocked this item is
   closed. Separately, re-verified against §3.5's ISS-002 finding: even
   at the real-world worst-case 5.5V LDO input, the LDO's 6.0V Vin AMR is
   not violated (0.5V/9% headroom remains) — this is a ROC-margin
   question (item 1 above), not an AMR violation.
3. **Current limit** — Not found. ≈16.2mA worst-case vs. 500mA LDO rating
   and 300mA REQ-103 ceiling — no pin or rail is anywhere near a limit
   (§14 item 5, `hardware/power-budget.md`).
4. **Thermal risk** — Not found. LDO TJ≈71°C at a load condition (300mA)
   18× higher than this design's real worst-case draw (§14 item 6).
5. **Missing decoupling capacitor** — Not found. Every VDD/VDDA/VBAT/VDDIO
   pin has its own cap per the relevant datasheet's own recommendation
   (§14 item 7).
6. **Floating pin** — **Corrected/resolved this revision for the LDO EN
   pin (ISS-001)**: the LDO's EN (pin 3) previously carried a hedge
   ("if the exact package variant... requires a level, tie it to VIN...
   flagged as a minor implementation detail to confirm... at layout
   time") which was, on reflection, exactly the kind of unconfirmed
   floating-pin risk this checklist item exists to catch — EN has no
   internal pull-up/pull-down (TI SBVS320D, §3.4) and a genuinely
   floating EN produces undefined output behavior. This is now a firm,
   unconditional direct tie to VIN (§3.4, §12 `EN_VIN` net) — resolved,
   not merely mitigated. IMU pins: reviewed pin-by-pin as before — all
   IMU pins are either wired
   to a net or deliberately tied off (CSB→VDDIO, SDO→GND) except INT1,
   INT2, and the aux-interface pins (ASDx/ASCx/OCSB/OSDO), which are left
   genuinely NC — this is a **deliberate, logged decision** (§5.3), not an
   accidental float, since unused digital inputs on a modern low-power
   sensor are typically internally biased/don't-care when their
   associated function is disabled (BMI270's aux interface and interrupt
   outputs are software-disabled by default) — **not independently
   re-verified against the BMI270 datasheet's own floating-pin guidance
   this session**, flagged in §16 as worth a Hardware Reviewer
   second look given "floating pin" is its own explicit checklist item.
   MCU: no floating pins — every used GPIO is wired, and unused GPIOs are
   inherently fine floating (internal weak pull config is a firmware
   concern, not a schematic-level floating-pin risk, standard practice).
   ESD IC: I/O1/I/O2 (D+/D− channels) are deliberately NC — these are TVS
   diode inputs with no signal to protect, not floating in the
   "unintended" sense the checklist targets.
7. **Incorrect pull-up/pull-down** — Not found on I2C (§5.2, sized via a
   real formula, not assumed, now correctly labeled as the I2C2 bus,
   ISS-011) or USB-C CC (§3.1, spec-fixed value). BOOT0
   pull-down deliberately omitted — logged as a scope decision (§4.2,
   **reasoning corrected this revision, ISS-006**: BOOT0 is muxed onto
   PA14/SWCLK, not PB8; the design decision to omit a physical BOOT0
   circuit and rely on nBOOT_SEL's factory default is unchanged, only the
   pin-identity reasoning behind it is now accurate), not
   an oversight, but flagged again here since "incorrect
   pull-up/pull-down" could arguably be read to include "missing one that
   should exist" — my own position is that it's not missing (relies on
   nBOOT_SEL default instead, and §4.2 now also notes this carries no
   brick risk since SWD recovery is independent of nBOOT_SEL state), but
   this is exactly the kind of judgment
   call an independent reviewer should re-examine (§16).
8. **Logic voltage mismatch** — Not found. Single 3.3V logic throughout,
   no mismatched-voltage interface anywhere (§14 item 2).
9. **Interface timing** — Not found, with the I2C sensitivity caveat
   already logged in §5.2/§14 item 12 (4.7kΩ meets the 300ns budget
   comfortably at the 50pF assumption, marginally at a 75pF worst case).
10. **Power sequencing** — Not found; structurally moot by design (§14
    item 10).
11. **Grounding** — Not found; single ground net, explicitly stated (§8).
12. **EMI/EMC risk** — No formal EMC pre-compliance target this cycle
    (REQ-401, "no specific regulatory certification target...for this
    prototype/benchmark iteration"). Reasonable practice followed: solid
    ground pour, short decoupling traces recommended, linear (not
    switching) regulator topology avoids switching-noise EMI entirely.
    No dedicated EMI filtering (ferrite beads, common-mode chokes) added
    on the USB VBUS line beyond the ESD/TVS array — judged unnecessary
    for a non-certified bench prototype; would be revisited if REQ-401's
    scope ever changes.
13. **Motor noise** — Not applicable; no motor on this board (§9).
14. **Sensor noise** — Addressed qualitatively (§14 item 16: linear LDO,
    short IMU decoupling/trace runs) but **no quantitative IMU
    noise-floor/PSRR analysis was performed this session** — flagged in
    §16 as a reasonable follow-up if IMU measurement precision becomes a
    concern in a later cycle (not currently a REQ).
15. **PCB layout concern (incl. mechanical/thermal co-design near
    rotating bodies)** — No PCB layout exists yet (no KiCad project, §0);
    board-geometry facts are recorded as estimates for the Mechanical
    Lead (§10). Mechanical/thermal co-design near rotating bodies: N/A,
    no rotating body (§9).
16. **Datasheet recommendation violation** — All four parts' own
    recommended application circuits were followed, with every deviation
    explicitly logged and justified (§14 item 17 lists all four:
    LDO=none — **now including the EN→VIN tie fixed firmly this
    revision, ISS-001**, IMU=INT1/INT2 NC, MCU=no crystal/no BOOT0
    circuit (reasoning corrected, ISS-006), ESD
    IC=D+/D− NC). No unlogged/silent deviation identified in this
    self-check.

**Self-check summary (Cycle 1, original)**: no CRITICAL or HIGH-severity issue identified by
my own pass. Several items carry an explicit residual flag for the
independent Hardware Reviewer to re-examine with fresh eyes (item 2's AMR
lower-bound UNKNOWN, item 6's IMU floating-pin judgment call, item 7's
BOOT0-pull-down scope decision, item 9's I2C capacitance sensitivity, item
14's absence of quantitative sensor-noise analysis) — these are flagged
precisely so the Hardware Reviewer knows where to look first, not because
I believe them to be actual defects.

**Re-self-check after Rev 2 fixes (this revision)**: focused re-check of
items most relevant to the three HIGH findings and the two folded-in
corrections, per my own agent instructions' handoff requirement —

- **Item 1 (Voltage) / Item 2 (AMR)** — ISS-010's AMR lower-bound UNKNOWN
  is closed. ISS-002's ROC-margin question is not silently left open: it
  now has an explicit disposition and recommendation in §3.5 (my
  recommendation: ACCEPTED-RISK, routed to the human Chief Engineer per
  `docs/architecture.md` §8 — see the handoff summary). I am not
  declaring ISS-002 resolved myself; that requires the named human
  sign-off the architecture doc specifies.
- **Item 6 (Floating pin)** — ISS-001's LDO EN pin is resolved: firm
  direct tie to VIN, no remaining hedge, matches TI's own recommended
  always-enabled connection exactly.
- **Item 7 (Incorrect pull-up/pull-down)** — ISS-006's BOOT0 reasoning is
  corrected (PA14, not PB8); the underlying design decision (no physical
  BOOT0 circuit) was already sound and remains unchanged — only the
  justification is now accurate. This item's residual flag (worth
  independent re-examination) still stands, unrelated to the correction.
- **Item 13 equivalent, §14 item 13 (MCU pin function)** — ISS-011's
  I2C1→I2C2 mislabeling is corrected everywhere I have found it
  (§2.3, §5.2, §5.3, §6, §11, §12, §13, §14); confidence for this
  specific pin pair upgraded to HIGH.
- **Item 16 (Datasheet recommendation violation)** — LDO recommended
  circuit is now followed exactly with no remaining hedge (EN→VIN firm).

No new CRITICAL or HIGH-severity issue was introduced by these fixes
themselves (verified: no new floating pin, no new AMR/ROC excursion, no
pin-table/net-list inconsistency found on this pass — see also the final
cross-section consistency check noted in the changelog at the top of
this document). ISS-002 remains, by design, an item for Hardware
Lead/Chief Engineer disposition rather than something I can close
unilaterally.

## 16. Open UNKNOWNs (for Hardware Lead / Hardware Reviewer)

**Annotation convention (new this revision)**: items below are annotated
**RESOLVED**/**CORRECTED** in place where this revision's rework closed
them, rather than being deleted or renumbered — this preserves external
cross-references that already cite specific item numbers (e.g.
`validation/design-review.md`'s "§16 UNKNOWN #2" and "§4.1/§16 UNKNOWN
#1"). A new item 10 is appended (not inserted) for the one finding
(ISS-002) that is a **known fact pending a disposition decision**, a
different category from the other items' original "unconfirmed fact"
framing.

In priority order:

1. **BOOT0/PB8 pin-bonding status — CORRECTED this revision (ISS-006).**
   Originally: "BOOT0/PB8 pin-bonding status on the exact STM32G031K8T6
   LQFP-32 package is UNKNOWN (DS-MCU-049). My own pin-count research
   (DS-MCU-046) does not show a PB8 pin in this package's pin list at
   all..." **This is now corrected, not merely re-flagged**: independent
   research this cycle (Hardware Lead, DS-MCU-051/053) confirms PB8
   *does* physically exist on this package, **and** confirms BOOT0 is not
   muxed onto PB8 at all — BOOT0 is muxed onto **PA14** (already this
   design's SWCLK pin, §4.2/§4.4), while PB8's real function is the
   secondary AF6 mapping for I2C1_SCL (DS-MCU-053). The original "PB8
   doesn't exist, so the BOOT0 question is moot" reasoning was simply
   wrong on both counts — PB8 exists, and it was never the BOOT0 pin to
   begin with. **Residual, non-blocking**: PB8/PB9's *exact pin numbers*
   within the LQFP-32 package were not independently re-resolved against
   the primary ST datasheet this session (they fall within the ranges
   already listed in §11); this does not affect the design decision below.
   **Design decision (unchanged)**: no physical BOOT0 circuit populated,
   relying on the nBOOT_SEL=1 factory default (DS-MCU-044, MODERATE
   confidence, still not independently re-verified this session) — this
   decision was always correct, now for the accurate reason. §4.2 also
   newly notes there is no brick risk from this either way, since SWD
   recovery does not depend on nBOOT_SEL state. Recommend the Hardware
   Reviewer (or a future session with access to the raw ST RM0454/datasheet
   PDF) still re-verify the nBOOT_SEL default value itself before this
   design is considered final for fabrication (not a blocker for this
   paper-design cycle, REQ-502).
2. **STM32G031K8T6 VDD Absolute Maximum Rating lower bound — RESOLVED
   this revision (ISS-010).** Originally UNKNOWN (carried forward from
   `bom/component-selection.md`, DS-MCU-012 only confirmed the 4.0V upper
   bound). **Now resolved**: the Hardware Reviewer independently verified
   the lower bound at **−0.3V** against ST DS12992 Rev4 Table 18 — see
   §1. No remaining gap on this item.
3. **STM32G031K8T6 VDD/VSS exact pin count has a moderate-confidence
   discrepancy across sources** (DS-MCU-046: 1 VDD/2 VSS from 3
   converging distributor sources vs. a separate lower-detail source
   claiming 1 VDD/1 VSS). VDD=1 is corroborated by both, so the
   decoupling plan (§4.1) is unaffected regardless of which VSS count is
   correct — flagged for completeness, not because it changes any design
   decision. **Unchanged this revision** — out of scope, not one of this
   cycle's HIGH findings or folded-in corrections.
4. **I2C1/USART2 alternate-function pin assignments — PARTIALLY RESOLVED
   this revision.** Originally: "PB10/PB11 for I2C1 SCL/SDA; PA2/PA3 for
   USART2 TX/RX were not individually re-verified against the exact
   STM32G031K8T6 alternate-function table this session... MODERATE /
   MODERATE-HIGH confidence." **The PB10/PB11 portion is now resolved,
   and it was a real mislabeling, not just an unverified assumption**:
   independent research this cycle (Hardware Lead, DS-MCU-052, ST
   DS12992 Rev4 Table 16) confirms PB10/PB11 map to **I2C2**, not I2C1
   (ISS-011) — corrected throughout this document (§2.3, §5.2, §5.3, §6,
   §11, §12, §13, §14), now HIGH confidence. Credit: Hardware Lead's
   independent re-verification resolved a genuine defect in this
   document, not merely a documentation gap. **The USART2 (PA2/PA3)
   portion remains open, unchanged this revision** — still
   MODERATE-HIGH confidence, standard STM32 convention, not individually
   re-pulled from the exact AF table; should still be confirmed against
   the real AF table (or via STM32CubeMX) before committing to a PCB
   layout. Low risk of being wrong given how conventional this mapping
   is, but not yet a closed item.
5. **BMI270 floating/NC pin guidance (INT1, INT2, ASDx, ASCx, OCSB, OSDO)
   was not independently re-verified against the BMI270 datasheet's own
   explicit floating-pin recommendations this session** — I assumed
   these are safe to leave NC when their associated function
   (aux-interface, interrupts) is software-disabled, consistent with
   common practice for this class of part, but this specific claim
   should get a fresh look from the Hardware Reviewer (flagged explicitly
   in my own self-check, §15 item 6). **Unchanged this revision** — out
   of scope, not one of this cycle's HIGH findings or folded-in
   corrections.
6. **Whether "reverse-polarity protection" in REQ-402 is satisfied by a
   mechanically-keyed connector alone, or was intended to require a
   discrete series diode regardless**, is a judgment call I made (§3.3)
   that the Hardware Reviewer or Hardware Lead may want to weigh in on —
   not a factual UNKNOWN so much as an interpretive one. **Unchanged
   this revision** — relates to ISS-004/ISS-012, explicitly out of scope
   for this cycle (Hardware Lead will route separately).
7. **Onboard overcurrent protection (e.g. a resettable PTC fuse on
   VBUS) was judged unnecessary** and not added, reasoning that USB
   hosts/hubs already provide upstream overcurrent protection — this
   judgment was not independently re-verified against any specific
   host-side spec this session (§14 item 9), flagged for the Hardware
   Reviewer. **Unchanged this revision** — relates to ISS-005, explicitly
   out of scope for this cycle.
8. **J1's exact USB-C receptacle MPN, and D1's exact LED MPN, are not
   formally selected this cycle** — both are placeholders (illustrative
   real parts cited only for the board-geometry height estimate and the
   LED forward-voltage assumption, respectively). Selecting exact MPNs is
   a follow-on BOM task, not blocking this design document. **Unchanged
   this revision** — out of scope, not one of this cycle's HIGH findings.
9. **U3's exact EN-pin behavior — RESOLVED this revision (ISS-001).**
   Originally: "not re-confirmed against the literal pinout diagram this
   session... assumed tied to always-enabled per the standard reference
   circuit; low-risk, flagged for layout-stage confirmation." **Now
   resolved, and firmly**: independent research this cycle (Hardware
   Lead, TI SBVS320D Rev D §4/§5.5/§6.4) confirms the TLV75533PDBVR's
   5-pin SOT-23-5 (DBV) package EN pin (pin 3) is mandatory (present on
   every package variant) with no internal pull-up/pull-down — a
   genuinely floating EN would produce undefined behavior. This design
   now implements a firm, unconditional direct tie from EN (pin 3) to
   VIN (pin 2), matching TI's own recommended always-enabled connection
   exactly (§3.4, §12 `EN_VIN` net, §13 parts list). No remaining hedge
   or layout-stage confirmation needed on this point.
10. **ISS-002 — LDO input-voltage margin against the real-world USB-C
    vSafe5V ceiling: known facts, pending Hardware Lead/Chief Engineer
    disposition (new this revision, not an "unconfirmed fact" UNKNOWN
    like the items above — the facts themselves are settled).** The real
    USB-C/USB-PD vSafe5V ceiling is 4.75–5.5V (wider than REQ-101's
    stated 4.75–5.25V), leaving effectively zero margin against the
    TLV75533PDBVR's 5.5V Vin Recommended Operating Condition ceiling at a
    legitimate worst-case input — though the LDO's 6.0V Absolute Maximum
    Rating still provides real headroom (0.5V/9%) even at 5.5V, so this
    is a regulation-margin concern, not a damage risk. Full disposition
    discussion and my own recommendation (ACCEPTED-RISK, per
    `docs/architecture.md` §8, requiring named human Chief Engineer
    sign-off — with option (b), an alternate-LDO evaluation, noted but
    not chosen) is in the new §3.5. **This item is explicitly not closed
    by this document** — it requires the Hardware Lead to route it for
    the human sign-off the architecture doc specifies before it can be
    marked resolved or accepted.

## 17. Power budget (summary — full detail in `hardware/power-budget.md`)

- **Worst-case total on 3V3 rail ≈16.2mA** (MCU 10.2mA@64MHz [DS-MCU-014]
  + IMU 0.685mA [DS-IMU-010] + LED ≈3.94mA [ESTIMATE] + I2C pull-ups
  worst-case ≈1.4mA [ESTIMATE]).
- **Typical total ≈7.0mA** (MCU 2.1mA@16MHz + IMU 0.685mA + LED ≈3.94mA +
  I2C pull-ups realistic ≈0.3mA).
- **Margin vs. REQ-103 (≤300mA)**: ≈283.8mA / ≈94.6% margin.
- **Margin vs. TLV75533PDBVR's 500mA rating (DS-PWR-003)**: ≈483.8mA /
  ≈96.8% margin.
- Both confirm the Component Engineer's own pre-design expectation
  ("MCU+IMU are only ~10-15mA combined") — even including the LED and
  I2C pull-ups this design adds, total draw is still an order of
  magnitude below either ceiling.
- LDO thermal: reused ≈71°C TJ estimate at 40°C ambient/300mA
  (`bom/component-selection.md`), ≈79°C headroom to 150°C max — and this
  design's real load is far below the 300mA that estimate already used,
  so actual heating is lower still.

## 18. Handoff (per `.github/agents/circuit-engineer.agent.md`)

**This is a re-handoff after Cycle 1's Hardware Reviewer findings — not a
first handoff.** See the Revision changelog at the top of this document
for the full list of what changed this cycle.

**To**: Hardware Reviewer, via Hardware Lead, for a **fresh re-review**
(not a first review) — per `.github/skills/hardware-review/SKILL.md`'s
guidance that a re-review after a fix means re-running the checklist
against the changed areas, this handoff calls out exactly which areas
changed so the re-review can focus there (§2.3, §3.4, §3.5 [new], §4.1,
§4.2, §5.2, §5.3, §6, §11, §12, §13, §14, §15, §16 — see changelog).

**Artifacts**:
- This document (`hardware/schematic/bench-imu-01-design.md`), revised —
  schematic artifact + design rationale log + self-check results
  (including the new "Re-self-check after Rev 2 fixes" pass, §15),
  combined.
- `hardware/power-budget.md` — **unchanged this cycle**; none of this
  revision's fixes (I2C relabeling, EN pin firm tie, vSafe5V disposition,
  BOOT0/PA14 correction, VDD AMR resolution) alter any current/power
  number.
- `datasheets/evidence-log.md` — Cycle 1 originally added 17 Evidence ID
  rows (DS-MCU-044–049, DS-IMU-074–077, DS-PWR-046, DS-PROT-001–002,
  DS-CONN-001–004, DS-IFACE-001) plus 7 new datasheet metadata records
  (USBLC6-2SC6, JEDEC package outline standards, NXP UM10204, USB-IF
  Type-C spec, GCT USB4125, GCT USB3140, ST NUCLEO-G031K8/UM2324) — see
  `datasheets/` directory; that history is unchanged. **Unchanged by me
  this cycle**: the Hardware Lead already appended the DS-MCU-050–053
  corrections (independent re-verification of ISS-006/ISS-011) per
  `validation/change-log.md` ECO-002, which this revision cites directly
  throughout.
- Open `UNKNOWN`s: §16 above — **4 of 9 original items resolved/corrected
  this cycle** (item 1 BOOT0/PB8 corrected — ISS-006; item 2 VDD AMR
  lower bound resolved — ISS-010; item 4 partially resolved, I2C portion
  only — ISS-011; item 9 EN-pin behavior resolved — ISS-001), **5 items
  unchanged and still open** (items 3, 5, 6, 7, 8 — all explicitly out of
  scope for this cycle), **plus 1 new item appended** (item 10, ISS-002's
  disposition — a known-facts-pending-decision record, not a fresh
  unconfirmed-fact UNKNOWN).

**On ISS-002 specifically**: I have not self-declared this resolved or
accepted anywhere in this document. §3.5 states my own engineering
recommendation (ACCEPTED-RISK) with reasoning, but per
`docs/architecture.md` §8, a HIGH finding may only become ACCEPTED-RISK
with named human Chief Engineer sign-off — that sign-off has not
happened, and is not mine to grant. I am asking the Hardware Lead to
route this finding for that decision (or, if the Hardware Lead judges a
component change is warranted instead, to route it to the Component
Engineer for an alternate-LDO evaluation — I have flagged but not chosen
between these two paths, consistent with my own agent instructions'
"Out of scope" constraint against unilaterally re-selecting a part).

No KiCad project exists to run `extract_schematic_netlist` /
`analyze_schematic_connections` / `validate_project` against (§0) — this
document is the self-check substitute for this cycle, as it was for
Cycle 1.

I have not declared this design "reviewed" or "complete" anywhere in this
document — per my own agent instructions, that determination is the
Hardware Reviewer's alone to make. I am also not marking ISS-004,
ISS-005, ISS-007, ISS-008, or ISS-009 resolved, touched, or in any way
addressed by this revision — those remain for a later disposition pass,
per the Hardware Lead's own scoping of this cycle's work.
