# Bench-IMU-01 — Schematic-Equivalent Design Document

**Author**: Circuit Engineer (AI agent) · **Date**: 2026-08-31 · **Status**: Design complete, self-checked, pending independent Hardware Reviewer pass (mandatory, not yet performed — see `.github/agents/circuit-engineer.agent.md` "Out of scope")

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

**Carried-forward open item from `bom/component-selection.md`**: the
STM32G031K8T6 VDD Absolute Maximum Rating **lower bound** was never
confirmed (only the 4.0V upper bound is confirmed, DS-MCU-012). This
session's research did not resolve it either — it remains UNKNOWN (see
§16). It does not block this design because the chosen operating point,
3.3V, sits deep inside the confirmed Recommended Operating Condition
(1.7–3.6V, DS-MCU-013), which is by construction a subset of the
Absolute Maximum range — so the missing AMR lower bound cannot plausibly
be violated by a 3.3V design.

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
| SWCLK | PA14 | HIGH — dedicated STM32 debug pin, not an alternate function |
| I2C1 SCL | PB10 | MODERATE — standard STM32G0 I2C1 AF mapping; not individually re-verified against the exact AF table this session (see §16) |
| I2C1 SDA | PB11 | MODERATE — as above |
| USART2 TX | PA2 | MODERATE-HIGH — very common STM32 USART2 mapping; not individually re-verified against the exact AF table this session (see §16) |
| USART2 RX | PA3 | MODERATE-HIGH — as above |
| Status LED drive | PA5 | ASSUMPTION — arbitrary free GPIO choice (also the conventional "Nucleo LED" pin on many ST boards), no AF conflict since it's used as plain GPIO output |
| NRST | NRST (pin 4) | HIGH — dedicated reset pin |
| BOOT0 | not populated this cycle | see §4.4 / §16 — genuinely UNKNOWN whether even bonded out on this package |

This leaves **USART1 and LPUART1 both free** (only USART2 is used) —
satisfies the Component Engineer's own note that one of the MCU's 2 UART
peripherals should remain genuinely free (only 1 of 2 committed here,
comfortably; actually both USART1 and LPUART1 remain free since USART2 is
the one consumed — even better margin than "one free" required).

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
here, no deviation. U3's EN pin (if present on this specific
variant/package — the "fixed 3.3V, no adjustable EN function needed"
variant is assumed per the approved part's own fixed-output selection) is
tied to enable-always per the standard reference circuit; if the exact
TLV75533 package variant used here has an active EN pin requiring a
level, tie it to VIN directly (always-enabled) — **flagged as a
minor implementation detail to confirm against the literal pinout
diagram** at layout time, not expected to change any electrical
conclusion in this document.

AMR/ROC check: U3 Vin = 5.0V nominal (4.75–5.25V per REQ-101) is within
AMR 6.0V (DS-PWR-002) with 0.75–1.25V margin, and within ROC 1.45–5.5V
(same evidence) — but the **top of the USB tolerance band (5.25V) leaves
only ~0.25V of headroom under the 5.5V ROC ceiling**, tighter than the AMR
margin. This is noted explicitly as a real, if small, margin consideration
rather than glossed over — it does not exceed any limit, but it is the
tightest margin anywhere in this design (see §16 and self-check §15 item 1).

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

### 4.2 BOOT0 / nBOOT_SEL handling

This required real web research since STM32 boot-mode conventions differ
materially across families (STM32F1-era generic conventions do **not**
carry over to STM32G0).

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
- **BOOT0 is multiplexed with GPIO PB8** on STM32G0 parts where PB8 is
  bonded out (DS-MCU-045, HIGHER confidence — 5 independent sources
  converge on this, generically for the G0 family / cited example
  STM32G071).
- **Unresolved discrepancy, flagged as UNKNOWN (DS-MCU-049)**: this
  design's own LQFP-32 pinout research (DS-MCU-046, §4.1 above) does
  **not** show a PB8 pin anywhere in the 32-pin package's pin list (it
  shows PB0,1,2,3,4,5,10,11 but no PB6/PB7/PB8/PB9). If accurate, this
  would mean the BOOT0-shared GPIO is **not even bonded out on this
  specific 32-pin package**, making the whole BOOT0-pin question moot for
  this exact part — the option byte would be the *only* boot-mode control
  mechanism that physically exists on this device, independent of
  whatever the generic G0-family PB8 guidance says for larger packages.
  However, this conclusion rests on a distributor-sourced pin table, not
  the primary ST datasheet pin table, so it is presented as
  best-current-understanding with residual uncertainty, not a fully
  closed item.

**Design decision**: **no physical BOOT0 pull-down resistor or header is
populated this cycle.** The design relies entirely on the nBOOT_SEL=1
factory default (boot from Flash unconditionally); the SWD header (§4.4)
remains the primary and sufficient programming/debug path, already
required independently by REQ-002/REQ-107. This is an explicit
scope-limiting decision flagged to the Hardware Lead/Hardware Reviewer
(§16), not a silent omission — if a future firmware bring-up session
discovers the factory default is not what was assumed, or that
nBOOT_SEL needs to be reprogrammed via SWD (which is itself possible using
only the already-present SWD header, without any extra hardware), that is
recoverable without a board re-spin.

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

Both the STM32G031 (I2C1, Fast-mode Plus capable up to 1Mbit/s, DS-MCU-017)
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
| 13 | SCx (SCL/SCLK) | **I2C1 SCL** (MCU PB10), pulled up by R3 |
| 14 | SDx (SDA/SDI) | **I2C1 SDA** (MCU PB11), pulled up by R4 |

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
for USART2 as the consumed one).

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

Power/reset pins per DS-MCU-046 (MODERATE confidence, see §4.1); GPIO
alternate-function assignments per §2.3 (MODERATE/MODERATE-HIGH
confidence, standard STM32 conventions, not individually re-pulled from
the exact AF table this session — see §16).

| Pin # | Name | Function in this design | Notes |
|---|---|---|---|
| 1 | VSS | GND | Power pin |
| 2–3 | (other GPIO, unused this cycle) | NC / free | Available for future use |
| 4 | NRST | NRST net (C5 + SW1) | §4.3 |
| 5 | VDDA | 3V3 (via C4) | §4.1 |
| 6–15 | PA0–PA9 (GPIO, selected used below) | PA2=USART2_TX, PA3=USART2_RX, PA5=LED drive; others free | §2.3, §6, §7 |
| 16 | VSS | GND | Power pin |
| 17 | VDD | 3V3 (via C3) | §4.1 |
| 18–25 | PA10–PA15, PB0–PB1 (selected used below) | PA13=SWDIO, PA14=SWCLK; others free | §4.4 |
| 26–31 | PB2–PB5, PB10, PB11 (selected used below) | PB10=I2C1_SCL, PB11=I2C1_SDA; others free | §5.3 |
| 32 | VBAT | 3V3 (direct tie) | §4.1 |

Full free-GPIO inventory after this design's allocation (for the
Mechanical/future-firmware team's reference, not individually itemized
above): PA0, PA1, PA4, PA6, PA7, PA8, PA9, PA10, PA11, PA12, PA15, PB0,
PB1, PB2, PB3, PB4, PB5 — 17 GPIOs remain completely free, including both
free UART peripherals (USART1, LPUART1) and SPI1/SPI2 (unused this
cycle since I2C was chosen for the IMU, §5.1).

## 12. Net list summary (net-by-net)

| Net | Connects |
|---|---|
| VBUS_5V | J1 (USB-C VBUS contact) → U4 pin 5 (VBUS) → C1 → U3 IN |
| CC1 | J1 CC1 contact → R1 (5.1kΩ) → GND |
| CC2 | J1 CC2 contact → R2 (5.1kΩ) → GND |
| 3V3 | U3 OUT → C2 → U1 VDD(pin17)/VDDA(pin5, via C4)/VBAT(pin32) → U2 VDD(pin8, via C6)/VDDIO(pin5, via C7) → R3/R4 (I2C pull-ups) → R5 (LED resistor) → J2 pin "3V3" → J3 pin "VDD" |
| GND | U1 VSS(pins1,16) → U2 GND(pin7)/GNDIO(pin6) → U3 GND → U4 GND(pin2) → R1/R2 return → C1–C9 return sides → D1 cathode (via R5) → SW1 one leg → J1 shell/GND contact → J2 pin "GND" → J3 pin "GND" |
| NRST | U1 NRST(pin4) → C5 → GND; also → SW1 → GND (momentary) |
| SWDIO | U1 PA13(pin?) → J3 pin "SWDIO" |
| SWCLK | U1 PA14(pin?) → J3 pin "SWCLK" |
| I2C1_SCL | U1 PB10 → R3 (pull-up to 3V3) → U2 SCx(pin13) |
| I2C1_SDA | U1 PB11 → R4 (pull-up to 3V3) → U2 SDx(pin14) |
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
| U3 | Texas Instruments TLV75533PDBVR | LDO, SOT-23-5, 3.3V fixed |
| U4 | STMicroelectronics USBLC6-2SC6 | ESD protection, SOT-23-6 |
| J1 | USB-C receptacle | MPN not formally selected; illustrative real part GCT USB4125/4105 family used for height estimate only (§10) |
| J2 | 4-pin header | UART: TX/RX/GND/3V3 (REQ-106) |
| J3 | 4-pin header | SWD: VDD/SWCLK/GND/SWDIO (REQ-107) |
| SW1 | Momentary pushbutton, N.O. | Manual reset (REQ-004, Could) |
| D1 | Generic indicator LED | MPN not selected; Vf≈2.0V assumed |
| R1, R2 | 5.1kΩ | USB-C CC1/CC2 pull-downs (DS-CONN-001) |
| R3, R4 | 4.7kΩ | I2C SCL/SDA pull-ups (§5.2) |
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
decision, §4.2.

## 14. Mandatory 18-item checklist walkthrough (my own agent instructions)

Every item addressed explicitly; each either cites an Evidence ID/REQ-ID
or states a clear ASSUMPTION/UNKNOWN, per the design task's instruction
not to skip any.

1. **Supply Voltage** — 5V USB VBUS (REQ-101, 4.75–5.25V) → 3.3V regulated
   (DS-PWR-003). See §2.1, §3.4.
2. **Logic Voltage** — single 3.3V logic throughout (REQ-102); no level
   shifting anywhere. See §2.1.
3. **Absolute Maximum Ratings** — MCU VDD AMR upper 4.0V confirmed
   (DS-MCU-012, lower bound UNKNOWN, carried forward, §1); IMU VDD/VDDIO
   AMR −0.3…+3.6V (DS-IMU-004); LDO Vin AMR 6.0V (DS-PWR-002). All
   satisfied at the 3.3V/5V operating points used (§3.4, §5.4).
4. **Recommended Operating Conditions** — MCU VDD ROC 1.7–3.6V
   (DS-MCU-013); IMU VDD/VDDIO ROC 1.71–3.6V/1.2–3.6V; LDO Vin ROC
   1.45–5.5V (DS-PWR-002, tight top-end margin flagged §3.4/§16). All
   satisfied.
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
   (DS-IFACE-001, §5.2); USB-C CC: R1/R2=5.1kΩ per USB-IF spec
   (DS-CONN-001, §3.1); BOOT0: none populated, see §4.2/§16; NRST: internal
   pull-up only, per AN5096 (DS-MCU-047, §4.3).
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
13. **MCU pin function** — full pin table in §11; BOOT0/boot-strap pin
    handling in §4.2 (flagged UNKNOWN re: physical bonding on this exact
    package); SWD dedicated pins (PA13/PA14) confirmed HIGH confidence;
    I2C/UART alternate-function assignments flagged MODERATE/MODERATE-HIGH
    confidence pending AF-table re-verification (§16).
14. **Interfaces (I2C/SPI/UART per each datasheet's recommended
    application circuit)** — I2C: BMI270's own recommended schematic
    followed exactly for decoupling/mode-select pins (§5.3, DS-IMU-074/075/076);
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
    deviation (§3.4). IMU: followed almost exactly; INT1/INT2 left NC is
    a deliberate, logged deviation (polling instead of interrupt-driven,
    §5.3). MCU: no external crystal populated is a deliberate, logged
    deviation from a "full" application circuit that might include one
    (§6); no physical BOOT0 circuit is a deliberate, logged deviation/scope
    decision (§4.2). ESD IC: D+/D− channels left unpopulated is a
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

1. **Voltage violation** — Not found. All operating points sit inside
   each part's own ROC (§14 items 3–4). The tightest margin in the whole
   design is the LDO's Vin ROC top-end (5.25V actual vs. 5.5V ceiling,
   ≈0.25V/4.5% headroom, §3.4) — small but not a violation.
2. **Absolute Maximum Rating violation** — Not found, with one caveat:
   MCU VDD AMR lower bound is UNKNOWN (never independently confirmed, §1) —
   cannot fully close this item for that one specific parameter, though
   the risk is judged low since 3.3V sits deep inside the confirmed ROC.
3. **Current limit** — Not found. ≈16.2mA worst-case vs. 500mA LDO rating
   and 300mA REQ-103 ceiling — no pin or rail is anywhere near a limit
   (§14 item 5, `hardware/power-budget.md`).
4. **Thermal risk** — Not found. LDO TJ≈71°C at a load condition (300mA)
   18× higher than this design's real worst-case draw (§14 item 6).
5. **Missing decoupling capacitor** — Not found. Every VDD/VDDA/VBAT/VDDIO
   pin has its own cap per the relevant datasheet's own recommendation
   (§14 item 7).
6. **Floating pin** — Reviewed pin-by-pin: all IMU pins are either wired
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
   real formula, not assumed) or USB-C CC (§3.1, spec-fixed value). BOOT0
   pull-down deliberately omitted — logged as a scope decision (§4.2), not
   an oversight, but flagged again here since "incorrect
   pull-up/pull-down" could arguably be read to include "missing one that
   should exist" — my own position is that it's not missing (relies on
   nBOOT_SEL default instead), but this is exactly the kind of judgment
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
    LDO=none, IMU=INT1/INT2 NC, MCU=no crystal/no BOOT0 circuit, ESD
    IC=D+/D− NC). No unlogged/silent deviation identified in this
    self-check.

**Self-check summary**: no CRITICAL or HIGH-severity issue identified by
my own pass. Several items carry an explicit residual flag for the
independent Hardware Reviewer to re-examine with fresh eyes (item 2's AMR
lower-bound UNKNOWN, item 6's IMU floating-pin judgment call, item 7's
BOOT0-pull-down scope decision, item 9's I2C capacitance sensitivity, item
14's absence of quantitative sensor-noise analysis) — these are flagged
precisely so the Hardware Reviewer knows where to look first, not because
I believe them to be actual defects.

## 16. Open UNKNOWNs (for Hardware Lead / Hardware Reviewer)

In priority order:

1. **BOOT0/PB8 pin-bonding status on the exact STM32G031K8T6 LQFP-32
   package is UNKNOWN** (DS-MCU-049). My own pin-count research
   (DS-MCU-046) does not show a PB8 pin in this package's pin list at
   all, which — if accurate — would mean the whole BOOT0-pin question is
   moot for this exact part (option byte `nBOOT_SEL` would be the only
   boot-mode control mechanism that physically exists). This was not
   resolved against the primary ST datasheet PDF this session (only
   distributor/aggregator mirrors). **Design decision taken despite this
   UNKNOWN**: no physical BOOT0 circuit populated, relying on the
   nBOOT_SEL=1 factory default (DS-MCU-044, itself only MODERATE
   confidence). Recommend the Hardware Reviewer (or a future session with
   access to the raw ST RM0454/datasheet PDF) re-verify both the pin-bonding
   question and the nBOOT_SEL default before this design is considered
   final for fabrication (not a blocker for this paper-design cycle,
   REQ-502).
2. **STM32G031K8T6 VDD Absolute Maximum Rating lower bound is UNKNOWN**
   (carried forward from `bom/component-selection.md`, not resolved this
   session either, DS-MCU-012 only confirms the 4.0V upper bound). Low
   practical risk (3.3V sits deep inside the confirmed ROC) but formally
   still an open gap.
3. **STM32G031K8T6 VDD/VSS exact pin count has a moderate-confidence
   discrepancy across sources** (DS-MCU-046: 1 VDD/2 VSS from 3
   converging distributor sources vs. a separate lower-detail source
   claiming 1 VDD/1 VSS). VDD=1 is corroborated by both, so the
   decoupling plan (§4.1) is unaffected regardless of which VSS count is
   correct — flagged for completeness, not because it changes any design
   decision.
4. **I2C1/USART2 alternate-function pin assignments (PB10/PB11 for I2C1
   SCL/SDA; PA2/PA3 for USART2 TX/RX) were not individually re-verified
   against the exact STM32G031K8T6 alternate-function table this
   session** — these are very standard STM32 conventions (MODERATE /
   MODERATE-HIGH confidence per §2.3) but should be confirmed against
   the real AF table (or via STM32CubeMX) before committing to a PCB
   layout. Low risk of being wrong given how conventional these mappings
   are across the STM32 family, but not yet a closed item.
5. **BMI270 floating/NC pin guidance (INT1, INT2, ASDx, ASCx, OCSB, OSDO)
   was not independently re-verified against the BMI270 datasheet's own
   explicit floating-pin recommendations this session** — I assumed
   these are safe to leave NC when their associated function
   (aux-interface, interrupts) is software-disabled, consistent with
   common practice for this class of part, but this specific claim
   should get a fresh look from the Hardware Reviewer (flagged explicitly
   in my own self-check, §15 item 6).
6. **Whether "reverse-polarity protection" in REQ-402 is satisfied by a
   mechanically-keyed connector alone, or was intended to require a
   discrete series diode regardless**, is a judgment call I made (§3.3)
   that the Hardware Reviewer or Hardware Lead may want to weigh in on —
   not a factual UNKNOWN so much as an interpretive one.
7. **Onboard overcurrent protection (e.g. a resettable PTC fuse on
   VBUS) was judged unnecessary** and not added, reasoning that USB
   hosts/hubs already provide upstream overcurrent protection — this
   judgment was not independently re-verified against any specific
   host-side spec this session (§14 item 9), flagged for the Hardware
   Reviewer.
8. **J1's exact USB-C receptacle MPN, and D1's exact LED MPN, are not
   formally selected this cycle** — both are placeholders (illustrative
   real parts cited only for the board-geometry height estimate and the
   LED forward-voltage assumption, respectively). Selecting exact MPNs is
   a follow-on BOM task, not blocking this design document.
9. **U3's exact EN-pin behavior on this specific TLV75533PDBVR
   package/variant was not re-confirmed against the literal pinout
   diagram this session** (§3.4) — assumed tied to always-enabled per the
   standard reference circuit; low-risk, flagged for layout-stage
   confirmation.

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

**To**: Hardware Reviewer, via Hardware Lead.

**Artifacts**:
- This document (`hardware/schematic/bench-imu-01-design.md`) — schematic
  artifact + design rationale log + self-check results, combined.
- `hardware/power-budget.md` — updated with real per-subsystem numbers.
- `datasheets/evidence-log.md` — 17 new Evidence ID rows appended
  (DS-MCU-044–049, DS-IMU-074–077, DS-PWR-046, DS-PROT-001–002,
  DS-CONN-001–004, DS-IFACE-001).
- 7 new datasheet metadata records created (USBLC6-2SC6, JEDEC package
  outline standards, NXP UM10204, USB-IF Type-C spec, GCT USB4125, GCT
  USB3140, ST NUCLEO-G031K8/UM2324) — see `datasheets/` directory.
- Open `UNKNOWN`s: §16 above (9 items, in priority order).

No KiCad project exists to run `extract_schematic_netlist` /
`analyze_schematic_connections` / `validate_project` against (§0) — this
document is the self-check substitute for this cycle.

I have not declared this design "reviewed" or "complete" anywhere in this
document — per my own agent instructions, that determination is the
Hardware Reviewer's alone to make.
