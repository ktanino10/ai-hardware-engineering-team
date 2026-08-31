# Electronics → Mechanical Interface

**Status**: **Rev 3 — full re-population, not an incremental patch.** Populated
by the Mechanical Lead (AI agent) from `hardware/schematic/bench-imu-01-design.md`
**Rev 5** (status line: "ready for Hardware Reviewer re-review focused on the
new U6 stage" — i.e. Rev 5's newest sub-block, the U6 supervisory controller,
has not yet cleared its own Hardware-Reviewer gate as of this population;
this is an Electronics-side review-status fact, noted here for traceability,
not something this handoff task blocks on or resolves), `bom/component-selection.md`
(Motor / Motor Driver IC / Motor-Rail Supervisory Controller sections), and
`requirements/requirements.md` Rev 3 (REQ-301–309, REQ-403–406, §9b/§9c).
Date: 2026-09-09 (this population). Author: Mechanical Lead (AI agent).

**Why this is a full re-population and not a patch**: Rev 2 of this file
described a single static sensor/MCU board — every dimension in it was a
component footprint or a board edge. Rev 3 adds a **Motor Driver + Reaction
Wheel subsystem** (M1 = T-Motor MN2206-13 KV2000, U5 = TI DRV10983, U6 = TI
TPS26631PWPR, J4 = Same Sky PJ-102AH barrel jack, plus 15 supporting passives/
protection parts across Rev 3–5) that is different **in kind**, not just in
degree: M1 is very likely not a PCB-mounted part at all (see Part B), it
connects via wire leads rather than PCB traces, and it drives a spinning mass
whose relevant "keep-out" is a **swept volume through a full rotation**
(REQ-306), a category of fact this file has never needed before. Rather than
awkwardly append motor rows to a document architecture built for a static
board, this revision restructures the file into **Part A** (the static
sensor/MCU board, carried forward from Rev 2 and resized for Rev 3's board
growth) and **Part B** (the motor + reaction-wheel subsystem, entirely new).
Every Rev 2 fact that is still valid is carried forward with its original
sourcing intact; nothing is silently dropped.

**Scope note**: This file records physical **facts and constraints** for the
next phase (enclosure/mechanical design) to consume. It does not itself
design an enclosure, a motor mount, or a flywheel — those are explicitly
out of scope for this population task (see `.github/agents/mechanical-lead.agent.md`)
and are left for a later session. Where a fact does not yet exist (e.g. no
flywheel product has been selected), this file states the Mechanical Lead's
own reasoned engineering assumption for the next phase to adopt, verify, or
override — not a placeholder.

## Who fills this in

The Mechanical Lead populates this file by reading `hardware/schematic/
bench-imu-01-design.md` (specifically §9 "Mechanical/thermal co-design" and
§10 "Board geometry facts," which the Circuit Engineer writes specifically
for this handoff), `bom/component-selection.md` for component-level
manufacturer facts not restated in the schematic doc, `requirements/
requirements.md` for the constraints this file's facts must satisfy, and (if
a KiCad project exists) the read-only KiCad MCP tools (`get_project_structure`,
`extract_project_netlist`, `analyze_bom`, `generate_pcb_thumbnail`). **No
KiCad project exists for this design as of this population** (`kicad-list_projects`
returns empty) — every fact below is sourced from the schematic-equivalent
design document and manufacturer data, not a KiCad footprint/placement file.
Where a physical fact genuinely isn't determined anywhere upstream, the
Mechanical Lead records its own best engineering judgment, labeled per the
legend below — never a silent guess presented as fact.

## Confidence / assumption legend

- **CONFIRMED** — an actual KiCad project value, a manufacturer datasheet/
  product-page spec, or a measured value. Cite the source.
- **ASSUMPTION** — a stated design choice made in the absence of confirmed
  data. State why.
- **ESTIMATE** — a reasonable approximation, explicitly flagged as such.
- **UNKNOWN** — not yet determined. Must not be relied on as if confirmed;
  escalate before treating it as load-bearing.

As in Rev 2: every Confidence label below is this Mechanical Lead's own
independent judgment against this legend, not a verbatim copy of the Circuit
Engineer's own labels for the same fact where the two sources overlap. Where
this file's label diverges from the schematic document's own framing, that
divergence is called out explicitly (see B1) rather than silently presented
as agreement.

---

# Part A — Static sensor/MCU board (carried forward from Rev 2, resized for Rev 3)

This part covers the same ground as Rev 2's entire file: the sensor/MCU board
that already existed before this revision. All Rev 2 component placements
(U1–U4, J1–J3, SW1, D1, R1–R5, C1–C9) are **unchanged in relative layout**;
only the board's own overall size grows, and the mounting-hole positions and
top-edge component Y-coordinates are rescaled to track the new edges (see
below). Nothing about the sensor/MCU circuit itself changed electrically in
Rev 3–5 (confirmed: `bench-imu-01-design.md` §13 lists U1–U4/J1–J3/SW1/D1/
R1–R5/C1–C9/MH1–4 with no Rev 3+ tag; all "new" tags are on the motor
subsystem).

## A1. Board geometry

| Parameter | Value | Unit | Source / Rationale | Confidence |
|---|---|---|---|---|
| Board outline shape | Rectangle | — | Carried forward from Rev 2; no cutouts/notches/castellated edges. A two-lobed or dog-bone outline (sensor lobe + motor lobe) was considered and rejected as over-engineering for this phase — a plain rectangle with internal zoning (below) is simpler to print/mount and still satisfies REQ-308 | ASSUMPTION |
| Length (X-axis) | 100 | mm | See "Board growth rationale" below | ASSUMPTION |
| Width (Y-axis) | 50 | mm | See "Board growth rationale" below | ASSUMPTION |
| Thickness | 1.6 | mm | Unchanged from Rev 2 (standard FR4 thickness). Rev 3's motor-rail traces likely use heavier copper weight for current capacity, but that is an Electronics-domain layer-stackup detail that does not change overall board Z-thickness — not restated here | ASSUMPTION |
| Board area | 5,000 | mm² | 100 × 50 | Derived |
| Diagonal | ≈111.8 | mm | √(100²+50²) | Derived |

**Board growth rationale (why 100×50mm, not some other size)**: Rev 2 was
60×40mm (2,400mm²) holding 23 real components (4 ICs + 3 connectors/header +
1 switch + 1 LED + 5 resistors + 9 capacitors, excluding mounting holes).
Rev 3–5 add 25 new reference designators (U5, M1, J4, D2, D3, R6–R9, C10–C15
in Rev 3 = 15 items; R10, F1 in Rev 4 = 2 items; U6, R11–R15, C16–C17 in Rev 5
= 8 items — verified against `bench-imu-01-design.md` §13's exact parts list),
bringing the total to 47–48 real components depending on whether M1 is
counted as board-mounted (see Part B — this is exactly the open question
that makes the count ambiguous). That is a **2.04×–2.09× component-count
increase**. This file proposes **100×50mm = 5,000mm², a 2.08× area increase**
— chosen to track the component-count growth rather than an arbitrary
round number, with the arithmetic checked against both bounds of the
component-count ratio. Both the length and width, and the diagonal, remain
well clear of REQ-308's relaxed ~150mm soft desk-scale sanity ceiling, with
considerable headroom. **REQ-308 explicitly relaxes the old 60×40mm ceiling
for this reason** — this file is not violating a hard requirement by growing
the board, it is exercising the room REQ-308 deliberately created.

**Board zoning (new for Rev 3, ASSUMPTION)**: to keep REQ-307's vibration-
isolation and §9's thermal-separation guidance concrete at the layout level
(this file does not design the isolation itself — see B3/B5 — but a sensible
zone layout is a cheap, low-risk first step any enclosure design will want),
this file proposes three X-axis zones spanning the board's full 50mm width:

| Zone | X-range | Width | Contents |
|---|---|---|---|
| Sensor zone | 0–60mm | 60mm | All Rev 2 components: U1–U4, J1–J3, SW1, D1, R1–R5, C1–C9, MH1/MH4 (left-hand pair) |
| Buffer/isolation gap | 60–70mm | 10mm | Deliberately empty — physical separation between the sensor/MCU domain and the motor-driver domain, responding to §9's vibration+thermal separation guidance and REQ-307 |
| Motor zone | 70–100mm | 30mm | U5, U6, J4, D2, D3, F1, R6–R15, C10–C17, MH2/MH3 (right-hand pair), MH5/MH6 (new) |

This zoning is a **layout proposal for the next phase**, not a claim that it
by itself satisfies REQ-307 (vibration isolation is a mechanical-mounting
question — see B3 — not solved by PCB layout alone). It is offered because
it costs nothing to state now and materially simplifies the next phase's
starting point.

## A2. Mounting

**Coordinate convention** (unchanged from Rev 2): origin (0,0) at the
board's bottom-left corner as viewed from the component side, X increasing
right, Y increasing up (toward the top edge), matching typical KiCad/EDA
convention. All coordinates below are board-relative, in mm.

**Rescaling rule applied to carry Rev 2 coordinates forward**: Rev 2's
interior/centered component positions (J1, J2, J3, SW1, D1) are scaled by
the width ratio 50/40 = **1.25×** in Y only (X is unchanged — the board only
grew in width/Y and length/X-extension, the original 0–60mm X-span is
untouched). This preserves each component's *relative* position on the
board (e.g. J1 was exactly Y-centered in Rev 2 at Y=20 of a 0–40 range;
at Y=25 it is exactly Y-centered in the new 0–50 range) rather than
leaving them at stale absolute coordinates that would no longer mean what
they meant in Rev 2. Mounting holes, which are defined relative to the
board *edge* (an inset distance, not a proportional interior position),
are recalculated fresh against the new edges rather than scaled.

| Hole | X | Y | Diameter | Type | Rationale | Confidence |
|---|---|---|---|---|---|---|
| MH-1 | 3.5 | 3.5 | 2.8mm (M2.5 clearance) | Through-hole | Bottom-left, 3.5mm inset from both edges — unchanged rule from Rev 2 | ASSUMPTION |
| MH-2 | 96.5 | 3.5 | 2.8mm (M2.5 clearance) | Through-hole | Bottom-right, 3.5mm inset from the new right/bottom edges | ASSUMPTION |
| MH-3 | 96.5 | 46.5 | 2.8mm (M2.5 clearance) | Through-hole | Top-right, 3.5mm inset from the new right/top edges | ASSUMPTION |
| MH-4 | 3.5 | 46.5 | 2.8mm (M2.5 clearance) | Through-hole | Top-left, 3.5mm inset from the new left/top edges | ASSUMPTION |
| **MH-5** *(new)* | 85 | 3.5 | 2.8mm (M2.5 clearance) | Through-hole | New — bottom edge of the motor zone, near its X-centroid (70–100mm zone, midpoint 85mm) | ASSUMPTION |
| **MH-6** *(new)* | 85 | 46.5 | 2.8mm (M2.5 clearance) | Through-hole | New — top edge of the motor zone, mirrors MH-5 | ASSUMPTION |

**Why two new mounting holes**: REQ-304's floor is "≥4 mounting holes,
positioned at corners or edges for support" — MH-1–4 alone already satisfy
that floor on the new 100×50mm outline. MH-5/MH-6 are proposed **beyond**
the floor specifically because Rev 3 introduces a new vibration source
(M1, however it ends up mounted — see Part B) roughly 15–30mm from the
nearest original corner hole; two additional anchor points straddling the
motor zone give the board firmer, more local support against motor-induced
vibration in that region, directly serving REQ-307. This is this
Mechanical Lead's own judgment call, not dictated by any upstream document
— flagged as ASSUMPTION accordingly, open to revision once an actual motor-
mounting decision (Part B) makes the true vibration path concrete.

All six holes assume M2.5 screws with a standard 0.3mm/side clearance
(2.5+0.3×2=3.1mm → rounded to a common 2.8mm clearance-drill convention,
unchanged reasoning from Rev 2), and PCB material sufficient annular ring
around each hole — not independently re-verified this revision, carried
forward as an ASSUMPTION.

## A3. Component height clearance

| Component | Height above PCB | Confidence | Source / Rationale |
|---|---|---|---|
| J4 (Same Sky PJ-102AH barrel jack) | ≈11.0mm | **ESTIMATE** | See "J4 height — provenance" below. **New tallest board-side component as of Rev 3**, superseding the Rev 2 figure below |
| J2/J3 (4-pin headers) | ≈8.5mm | ESTIMATE (carried forward from Rev 2) | Standard 0.1" pin header, unpopulated-mate height estimate; Rev 2's own governing figure, now superseded by J4 above but retained as a secondary reference candidate (see caveat below) |
| J1 (USB-C receptacle) | ≈3.2mm | ESTIMATE (carried forward from Rev 2) | GCT USB4125/4105-family illustrative height, MPN not formally selected (`bench-imu-01-design.md` §13) |
| U5 (TI DRV10983) | ≈1.1–1.2mm | ESTIMATE | HTSSOP-24 (PWP) package, JEDEC MO-153-family standard body height envelope — non-driving |
| U6 (TI TPS26631PWPR) | ≈1.1–1.2mm | ESTIMATE | HTSSOP-20 (PWP) package, same JEDEC family — non-driving |
| D2 (ST STPS3L60) | ≈2.1mm | ESTIMATE | SMB (DO-214AA) package, standard-family body height — non-driving |
| D3 (Littelfuse SMBJ16A) | ≈2.1mm | ESTIMATE | SMB (DO-214AA) package, same family — non-driving |
| F1 (Littelfuse 30R500UF) | **not determined** | **UNKNOWN** | See "F1 — a newly surfaced gap" below |
| R6–R15, C10–C17 | <1mm each | ASSUMPTION | Standard small SMD passive packages (0603-class per R10's explicit 0603 callout in §13; others not individually specified but presumed the same design-wide convention) — negligible, non-driving, consistent with Rev 2's treatment of R1–R5/C1–C9 |
| **Bottom side (all components)** | 0 | ASSUMPTION (carried forward) | No bottom-side placements found anywhere in Rev 2 or the Rev 3–5 additions; re-checked this revision against the full §13 parts list, nothing contradicts this |

**Governing clearance conclusion**: **≈11.0mm** top-side clearance should be
budgeted for the sensor/MCU + motor-driver board region specifically because
of J4, pending the caveats immediately below.

**J4 height — provenance (why ESTIMATE, not CONFIRMED)**: `bench-imu-01-design.md`
§10 explicitly flags "J4 may be the new tallest component, pending
confirmation" without resolving it — this file's own job is to resolve it
as far as reasonably possible. This session: (a) the manufacturer's current
Rev 1.05 datasheet (`datasheets/samesky_pj-102ah_rev1-05.md`, DS-CONN-005)
gives only electrical ratings and a 9.5mm mating-plug insertion depth — its
mechanical drawing's actual dimension figures are embedded as vector
graphics, not extractable as text, even via a direct fetch; (b) a web search
returned a specific claim of H=11.0mm/L=14.4mm/W=9.0mm, attributed to a
DigiKey-adjacent listing; (c) a second, independent web search corroborated
the same 11.0mm figure via a different (mirror) site; (d) that mirror site
turned out to host an **older Rev 1.02 (2016)** version of the same CUI/
Same Sky datasheet — its OCR'd dimension text contains "11.0" paired with
"0.433" (11.0mm ≈ 0.433in, an internally-consistent metric/imperial pair,
i.e. not an arbitrary number) alongside a "9.0" width figure, giving
genuine partial corroboration that 11.0mm is a real datasheet figure and
not a hallucination — but this is an older hardware revision than the one
currently cited (Rev 1.05, which shows a slightly different insertion
depth, 9.5mm vs. that older document's own figures, confirming some minor
spec drift between revisions), and no drawing was visually confirmed. **Net
call: ESTIMATE, not CONFIRMED** — flagged for re-verification against a
physical sample or the current Rev 1.05 drawing's actual vector content
before the enclosure's Z-height is finalized. If 11.0mm later proves wrong,
the fallback governing figure is the 8.5mm J2/J3 header estimate, which
remains independently valid regardless of J4's outcome.

**F1 — a newly surfaced gap**: F1 (Littelfuse 30R500UF) is described in its
own datasheet family as a **"30R Series Radial Leaded"** resettable PTC
fuse — i.e. a through-hole part with two wire leads and a disc-shaped body,
mechanically unlike every other Rev 3–5 addition (all of which are small
SMD parts). Neither the Circuit Engineer's design document nor the
Component Engineer's evidence log (`datasheets/evidence-log.md`, DS-PROT-006/
032/033) recorded a body diameter, thickness, or standoff height for this
part — only its electrical ratings. This file surfaces that as a genuine,
previously-unflagged gap: **F1's height above the board is UNKNOWN.**
Judgment call: general familiarity with this class of radial PTC fuse
(compact epoxy-coated discs, typically well under 10mm across and a few mm
thick for this current rating) makes it plausible F1 does not exceed J4's
~11.0mm estimate or M1's height if on-board (Part B) — but this is a
plausibility judgment, not a confirmed or even estimated number, and this
file declines to invent one. Not pursued further this session because it is
judged unlikely to change the governing conclusion; flagged for a fresh
manufacturer-drawing lookup before the enclosure Z-height is finalized.

**Cross-reference to Part B**: if M1 ends up mounted directly to this board
(against this Mechanical Lead's own non-binding leaning — see B3), its own
18.5mm overall body height (CONFIRMED, DS-MTR-021) would exceed every figure
in this table and become the new governing clearance dimension, growing the
top-side clearance budget from ~11mm to ~18.5mm-plus. This is exactly the
kind of consequence that makes the Part B mounting-method question
consequential rather than academic, and is not resolved here.

## A4. Connectors, switches & LEDs (cutouts)

| Ref | Type | X | Y | Orientation | Notes | Confidence |
|---|---|---|---|---|---|---|
| J1 | USB-C receptacle | 0 | 25 | Horizontal edge-mount; plug axis along X, opening faces −X | Left edge, Y-centered (25 = midpoint of new 0–50mm range, preserving Rev 2's exact-center placement under the 1.25× rescale) | ESTIMATE (carried forward from Rev 2, rescaled) |
| J2 | 4-pin header (UART) | 16 | 50 | Vertical, pins point +Y | Top edge (rescaled Y: 40×1.25=50). Rev 2 already placed this exactly at the board's then-top edge (Y=40 of a 0–40mm board) — the rescale preserves that same "exactly at the top edge" relationship on the new 0–50mm board, it is not a new decision to move it onto the edge | ESTIMATE (carried forward from Rev 2, rescaled) |
| J3 | 4-pin header (SWD) | 30 | 50 | Vertical, pins point +Y | Top edge, same rescale/edge relationship as J2 | ESTIMATE (carried forward from Rev 2, rescaled) |
| SW1 | Momentary pushbutton | 44 | 50 | Top-accessible | Top edge, same rescale/edge relationship as J2. Rev 2 gave **no** edge/position guidance for SW1 at all — its placement (grouped near the debug headers) was, and remains, this Mechanical Lead's own unconstrained choice | ASSUMPTION (carried forward from Rev 2, rescaled) |
| D1 | Indicator LED | 10 | 37.5 | Top-visible | Interior position, rescaled (30×1.25=37.5). Rev 2 gave **no** position guidance for D1 either — placement near the power-input edge was, and remains, this Mechanical Lead's own unconstrained choice | ASSUMPTION (carried forward from Rev 2, rescaled) |
| **J4** *(new)* | Barrel jack (Same Sky PJ-102AH) | 100 | 25 | Horizontal edge-mount; plug axis along X, opening faces +X | Right edge, Y-centered — mirrors J1's role/style on the opposite short edge. 2.0mm center pin per DS-CONN-005; outer barrel diameter not independently confirmed this session (commonly paired with 2.0mm-center-pin jacks of this class, per the schematic doc's own §13 caveat — not asserted as a specific cutout diameter here) | ASSUMPTION |
| **MC-1** *(new, Mechanical-Lead-proposed — NOT a Circuit Engineer reference designator)* | Motor phase-wire connector (proposed) | 92 | 0 | Bottom edge of motor zone, pins/wire exit −Y | Provisional placement only, contingent on the still-open motor-mounting decision (Part B). If a future schematic revision formally adopts a connector here, the Circuit Engineer would assign it a real "J"-number — "MC-1" is deliberately not J-prefixed to avoid colliding with any future Circuit-Engineer-assigned designator | ASSUMPTION, explicitly provisional |

**Cutout sizing**: as in Rev 2, none of the above have been sized to an
exact cutout dimension (e.g. a precise USB-C or barrel-jack panel cutout
profile) — that is enclosure-design-phase work. This file records position,
orientation, and the connector's identity/rough envelope so that phase can
size cutouts correctly.

## A5. Mass (sensor/MCU board + all Rev 3–5 populated components, excluding M1 and the flywheel)

| Item | Mass | Confidence | Rationale |
|---|---|---|---|
| Bare PCB substrate | 14.8g | ESTIMATE | 100mm × 50mm × 1.6mm × 1.85g/cm³ (standard FR4 density, same method/density as Rev 2) = 8.0cm³ × 1.85g/cm³. Scales consistently with the 2.08× board-area growth vs. Rev 2's own 7.1g bare-board figure |
| Rev 2 components (U1–U4, J1–J3, SW1, D1, R1–R5, C1–C9) | ≈1.8–2.0g | ESTIMATE (carried forward) | Unchanged from Rev 2's own figure |
| Rev 3–5 components (U5, U6, J4, D2, D3, F1, R6–R15, C10–C17) | ≈2.5–3.0g | ESTIMATE | J4 (barrel jack, metal-bodied) dominates at ≈1.5g; U5/U6 (HTSSOP) ≈0.15–0.2g each; D2/D3 (SMB) ≈0.1g each; F1 (radial PTC, epoxy body) ≈0.3–0.4g; R6–R15/C10–C17 (small SMD) negligible individually, ≈0.1–0.15g combined |
| **Subtotal: populated board assembly** | **≈19–20g** | ESTIMATE | Sum of the above three rows |

M1 and the flywheel are deliberately **excluded** from this table and
carried separately in Part B, because their mass may or may not load this
PCB at all, depending on the still-open mounting decision (B3). The combined
total assembly mass (this subtotal + M1 + flywheel) is given in B7.

---

# Part B — Motor + reaction-wheel subsystem (new, Rev 3)

**Why this needs its own part, not just new table rows**: everything in
Part A is a component with a fixed footprint soldered to a fixed place on a
board — the kind of fact this file has always recorded. M1 and its flywheel
are qualitatively different: M1 is very likely not solder-mounted at all,
its counterpart (the flywheel) is not yet a selected product, and the
relevant keep-out is not a static footprint but a **swept volume through a
full rotation** (REQ-306) — a category of spatial fact this file has never
needed to express before. Each section below states plainly what is
confirmed, what is this Mechanical Lead's own reasoned assumption, and what
is a genuinely open question for the next phase or for escalation.

## B1. Motor (M1) physical facts

**Source**: T-Motor MN2206-13 KV2000, product-page dimensions/mass block,
`datasheets/tmotor_mn2206-13-2000kv_rev-unknown.md`, Evidence ID **DS-MTR-021**
(`datasheets/evidence-log.md`).

| Parameter | Value | Unit | Confidence | Notes |
|---|---|---|---|---|
| Overall body diameter | 27 | mm | **CONFIRMED** | Manufacturer product-page spec block (DS-MTR-021) |
| Overall body height (bell + stator stack) | 18.5 | mm | **CONFIRMED** | Same source |
| Stator diameter | 22 | mm | **CONFIRMED** | Same source — see divergence note below |
| Stator height | 6 | mm | **CONFIRMED** | Same source |
| Shaft diameter | 3 | mm | **CONFIRMED** | Same source |
| Mass | 30 | g | **CONFIRMED** | Same source |
| Motor architecture | Outrunner (rotating bell/case, stationary stator core) | — | **CONFIRMED** | DS-MTR-017/DS-MTR-021 |
| Mounting-hole bolt pattern | 4× M3 screws, ~16mm bolt circle diameter, ~12mm square spacing | — | **ASSUMPTION** — heavily hedged | See "Bolt pattern — provenance" below |
| Mounting-hole depth/thread | Not determined | — | **UNKNOWN** | Not found in any source consulted this session |

**Confidence divergence note (per this file's own legend, stated explicitly
rather than silently)**: `bench-imu-01-design.md` §10's own table treats the
stator dimension figure as an **ASSUMPTION**, reasoned from the part
number's own "XXYY" stator-size naming convention (22mm×6mm from "2206").
This file labels the same 22×6mm figure **CONFIRMED** instead, because
DS-MTR-021 itself directly states the stator dimensions as part of the same
manufacturer product-page block that gives the overall body size and mass —
i.e., it is not solely inferred from the naming convention, it is also
directly stated on the same cited source as the other (uncontested-CONFIRMED)
figures in this table. The naming-convention match is a welcome independent
corroboration of the same number, not a contradiction. Per this file's own
precedent (Rev 2's header, and the legend above), the Mechanical Lead's
confidence label is its own independent judgment where sources overlap —
this is such a case, presented explicitly rather than silently overriding
the schematic document's own framing.

**Caveat on evidentiary class**: DS-MTR-021's source is described as a
"Product page dimensions/mass block" — i.e., the manufacturer's own retail
product page spec table, not a downloadable PDF mechanical drawing with
dimensioned views. This still qualifies as CONFIRMED under this file's own
legend ("manufacturer spec" — a manufacturer's own published product-page
specification is exactly that), but it is a materially different
evidentiary class from a formal dimensioned drawing, and is noted here for
transparency, mirroring how Rev 2 distinguished JEDEC-family package
envelopes from part-specific drawings.

**Bolt pattern — provenance (why ASSUMPTION, heavily hedged)**: this
figure was not found in any repository source (it is absent from
DS-MTR-017 through DS-MTR-024, the complete evidence-log breakdown for this
part). A web search this session returned a specific claim (4× M3, 16mm
bolt circle, 12mm square spacing) explicitly described as a "standard mini
quadcopter/multirotor motor" mounting convention for motors in this general
size/frame class — not a T-Motor manufacturer drawing for this specific
SKU. This file records it as a **starting-point ASSUMPTION only**,
sufficient for early enclosure/bracket sketching, but it **must be verified
against the actual physical part, an official T-Motor CAD file, or a
purchased sample's own measured bolt pattern before any enclosure screw-boss
position is finalized for manufacture.** This is not treated as unsafe to
leave as an ASSUMPTION at this stage (no physical prototyping is happening
this cycle — REQ-502's paper-design-cycle framing — and the figure does not
block any design activity that follows, it only needs revisiting before
physical commitment), so it is not escalated as a blocker.

## B2. Flywheel physical facts (assumed design — no product exists yet)

No flywheel product has been selected or specified anywhere upstream — the
target in `requirements/requirements.md` §9b (≈100g mass at ≈30mm radius,
≥3000 RPM, human-approved per §9c) is a **performance target**, not a
physical part. This file proposes a concrete, reasoned geometry consistent
with that target, for the next phase to adopt, refine, or override.

| Parameter | Value | Unit | Confidence | Rationale |
|---|---|---|---|---|
| Target mass | 100 | g | CONFIRMED (as a target) | `requirements/requirements.md` §9b, human-approved §9c |
| Target radius | 30 | mm | CONFIRMED (as a target) | Same source |
| Target angular momentum | ≈14.1 at 3000 RPM | mN·m·s | CONFIRMED (as a target, derived) | §9b's own I=0.5·m·r² solid-disk-formula reasoning, independently re-verified: I = 0.5 × 0.1kg × (0.03m)² = 4.5×10⁻⁵kg·m²; L = I·ω at 3000 RPM (ω=314.2rad/s) ≈ 14.1×10⁻³N·m·s |
| **Proposed geometry** | Solid disk, ⌀60mm × 4.5mm thick | — | **ASSUMPTION** | Derived below |
| **Proposed material** | Mild steel (ρ≈7,850kg/m³) | — | **ASSUMPTION** | See "Material choice" below |
| Center bore / hub interface | Not modeled | — | **UNKNOWN** | Depends on the shaft/hub attachment method, itself unresolved (see below) |

**Geometry derivation**: for a solid disk of mass m and radius r, thickness
t = m/(ρ·π·r²). At m=100g (0.1kg), r=30mm (0.03m), ρ=7,850kg/m³ (mild
steel): t = 0.1 / (7,850 × π × 0.0009) = 0.1/22.19 ≈ **4.5mm**. This exactly
reproduces the target I=4.5×10⁻⁵kg·m² by construction (solid-disk formula),
so the ≥3000 RPM / ≈14.1mN·m·s target is met by definition at this geometry.

**Material choice — why steel, not aluminum/brass/printed plastic**: for a
*fixed* target mass and radius, disk thickness scales inversely with
density. Alternatives computed on the same basis: aluminum (ρ≈2,700) →
≈13.1mm thick; brass (ρ≈8,400) → ≈4.2mm thick (very close to steel); PLA/
PETG (ρ≈1,250 average) → ≈28.3mm thick. Two reasons drive the steel choice:
(1) **Safety**: a 3D-printed plastic disk this thick, spinning at ≥3000 RPM,
carries genuine interlaminar/layer-adhesion weakness under centrifugal
stress — directly relevant to REQ-403 (flywheel detachment/pinch-hazard
mitigation, human-review-gated). **This file explicitly states the flywheel
must NOT be assumed 3D-printed**, unlike the enclosure itself, which
REQ-309 does permit to be 3D-printed. (2) **Compactness**: steel's higher
density directly minimizes the disk's axial thickness for the same target
mass/radius, which matters because it minimizes the axial dimension of the
rotation clearance envelope (B5) that the enclosure must accommodate.
Aluminum/brass remain physically plausible alternatives (brass in
particular is a close second on thickness) but are not selected here as the
primary proposal; this is a design proposal for the next phase, not a
final material specification.

**Explicitly not modeled — flagged for the next phase**: (a) if the next
phase instead builds an annular/ring geometry rather than a solid disk
(physically natural for direct bell-mounting, per `bom/component-selection.md`'s
own framing — "outrunner (flywheel can mount directly to the rotating bell,
maximizing inertia per gram)," line ~501), the true moment of inertia would
exceed this solid-disk figure (ring I≈m·r² vs. disk I≈0.5·m·r² for the same
mass/radius) — very likely still comfortably covered given the motor's own
~17.2× continuous-torque margin over the disk-based target (`bom/component-selection.md`
Motor Approval table), but flagged as a real modeling consideration, not
silently assumed equivalent; (b) a center bore/hub interface for shaft
mounting is not modeled at all — genuinely unresolved, tied to the same
open mounting-method question as B3; (c) M1's own body radius (13.5mm) sits
comfortably inside this flywheel's 30mm target radius (≈16.5mm of disk
extends beyond the motor body on each side if bell-mounted), a basic
geometric plausibility check, not a design conclusion.

## B3. Motor mounting interface — OPEN ITEM, not resolved in this document

**What the schematic document says, verbatim** (`bench-imu-01-design.md` §10):

> "M1 is off-board or on-board? — UNKNOWN, not resolved this session:
> whether the reaction-wheel motor mounts directly to this PCB, to a
> separate mechanical structure connected only by wire, or some hybrid, is
> a Mechanical Lead decision this document does not presume."

§16 item 20 repeats the same open status. The Circuit Engineer has
deliberately and explicitly left this decision to the Mechanical Lead — it
is not an oversight or a gap in the schematic document, it is a considered
hand-off.

**This Mechanical Lead's own non-binding leaning (not a decision made in
this document)**: off-board / bracket-mounted is more physically sensible,
for four reasons: (1) M1 is a screw-mount part by its own manufacturer
convention (§B1's bolt-pattern discussion), not a reflow/PCB-footprint
part — nothing about it is designed to be soldered down; (2) a 1.6mm FR4
PCB is a poor structural choice for cantilevering a spinning mass under
sustained vibration — FR4 is not selected or rated for this kind of
mechanical duty; (3) REQ-307's vibration-isolation requirement is
substantially easier to satisfy with a motor mount that is mechanically
separate from the sensor board than with one that shares the same rigid
substrate; (4) `bom/component-selection.md`'s own "flywheel mounts to the
rotating bell" framing implies a bolt-on interface that is naturally
serviced by a dedicated bracket, not a PCB pad. **This is a leaning, not a
decision** — the actual mounting method is enclosure-design work, out of
scope for this population task, and is left open here.

**Escalation assessment (this Mechanical Lead's own judgment, per the
escalation triggers in `.github/agents/mechanical-lead.agent.md`)**: this
question does **not** need Hardware-Lead/human escalation as a blocking gap
at this handoff-population stage. It is squarely within the Mechanical
Lead's own delegated design authority (the schematic document says so
explicitly), and properly belongs to the *next* phase (actual enclosure/
mount design), not this one. It **is** safety-relevant — it bears directly
on REQ-403 (flywheel detachment/pinch-hazard mitigation) and REQ-306
(rotation clearance) — so whichever way it is eventually decided, that
decision must still pass REQ-403's own separate, already-established
human-review gate before Design Complete. That gate is a pre-existing
structural requirement in `requirements/requirements.md`, not a new
escalation this file is introducing.

**Consequence noted for the next phase**: whichever way this is decided
has material downstream effects already surfaced in this file — it changes
the governing top-side height-clearance figure (A3: 11.0mm vs. 18.5mm-plus
if on-board), it determines whether M1's 30g mass loads the sensor/MCU PCB
directly (A5/B7), and it determines where MC-1's provisional connector
position (A4) is even relevant (a wire-to-bracket motor needs a board-edge
connector; a PCB-mounted motor might not).

## B4. Motor phase wiring / connector

**Confirmed electrical fact**: U5 (DRV10983) pins 17–22 connect to M1's 3
phase leads via the `MOTOR_PHASE_U/V/W` net (`bench-imu-01-design.md` §12).
M1 is confirmed **sensorless** (DS-MTR-022 — 3 phase leads only, no separate
Hall-sensor harness), so exactly 3 conductors are involved, no more.

**Confirmed as a genuine gap**: no connector or wiring hardware for these 3
leads is specified anywhere upstream — it is absent from the complete Rev
3–5 parts list (`bench-imu-01-design.md` §13).

**Proposed physical routing (ASSUMPTION, contingent on the B3 off-board
leaning)**: if M1 is off-board, its 3 phase leads need some physical
transition from loose wire to the PCB edge. This file proposes a small
keyed/locking 3-pin connector (e.g., JST-XH class or similar) at the board
edge (provisionally placed as **MC-1**, A4) as a reasonable default —
keying prevents an accidental phase-swap during assembly/rework, which
would otherwise just reverse rotation direction (a nuisance, not a safety
issue, given the driver is commutation-agnostic to lead order) but is still
worth avoiding for assembly repeatability. A real, undecided alternative is
flagged explicitly: this motor class is RC-industry-conventionally supplied
with **unkeyed bullet connectors** (3.5mm or similar), which some builders
prefer specifically because they allow a deliberate phase-swap to reverse
rotation direction without re-soldering. Both are physically reasonable;
neither is selected as final here — this is a next-phase decision, flagged
with its trade-off stated rather than silently resolved.

**If M1 turns out to be on-board instead**, this section's proposed
connector becomes moot — phase leads would instead need a direct solder-tab
or through-hole termination pattern near U5's own footprint, which is not
designed here either (Electronics-domain PCB layout work, not Mechanical).

## B5. Rotation clearance envelope (REQ-306)

**Requirement being served**: REQ-306 — the flywheel's full rotation must
clear the enclosure at every point, with real margin. This is a
categorically new kind of keep-out for this file: every previous height/
clearance fact in Part A describes a **static** footprint; this describes a
**swept volume through 360° of rotation**.

**Nominal swept volume** (no margin): for a well-balanced, concentric disk
rotating about its own central axis, the swept volume is identical to its
own static footprint — a cylinder of the flywheel's own diameter and
thickness, coaxial with the rotation axis. Per B2's proposed geometry:
**⌀60mm × 4.5mm thick.**

**Proposed clearance margin (ASSUMPTION)**: this file proposes the
enclosure keep out a materially larger volume than the nominal swept
cylinder:

| Direction | Nominal | Proposed margin | Proposed clearance envelope |
|---|---|---|---|
| Radial | 30mm radius (⌀60mm) | +8mm (≈27% of radius) | ≥38mm radius (**⌀76mm**) |
| Axial (each face) | 4.5mm total thickness | +3mm per face | **≥10.5mm total thickness** |

**Rationale for the margin figures**: this is a reasoned starting proposal
for the next phase, not a rigorously derived vibration-analysis result (no
such analysis exists or is in scope this session). The radial margin
accounts for four stacking factors: (a) manufacturing/concentricity
tolerance in the flywheel itself; (b) bearing/shaft runout in M1; (c)
dynamic-imbalance-induced wobble — likely the dominant term in practice for
an unbalanced hobbyist-grade disk with no balancing step planned; (d)
motor-mount compliance under vibration (REQ-307) allowing the whole
assembly to shift slightly relative to the enclosure. The axial margin is
smaller because axial runout for a disk this thin is typically a lesser
contributor than radial wobble, but is still included rather than assumed
zero.

**Explicitly not a substitute for REQ-403**: this clearance envelope is a
*geometric* keep-out proposal — it answers "how much space must be empty
around the flywheel." It does **not** address REQ-403's separate,
human-review-gated question of containment/detachment/pinch-hazard
mitigation (e.g., whether a physical guard or shroud is needed in addition
to clearance, what happens if the flywheel does detach). Both must be
satisfied; this section only speaks to the first.

**Position/orientation — UNKNOWN, tied to B3**: where this clearance
cylinder sits within the enclosure, and whether its axis is vertical or
horizontal, depends entirely on the still-open motor-mounting decision
(B3) and is not determined here.

**A load-bearing cross-check worth flagging now**: the proposed clearance
**diameter (⌀76mm) is larger than this file's own proposed PCB width
(50mm, A1)**. This means the enclosure's overall footprint in whatever
plane the flywheel spins will very likely be driven by the flywheel's own
swept volume, not by the sensor/MCU board's outline — regardless of how
the B3 mounting question resolves. Even accounting for wall thickness and
a small margin (a plausible flywheel bay might need roughly 76mm + 2×
(2–3mm wall) + 2×(2–3mm clearance) ≈ 86–88mm across), this remains well
within REQ-308's ~150mm ceiling — no requirement is violated — but it is a
concrete, quantified reason this file's own assessment (see close-out
below) is that the next phase looks like a full enclosure redesign rather
than a scoped addition bolted onto the Rev 2 box.

**Forward reference**: REQ-405 states firmware's eventual maximum-speed
ceiling "must also feed Mechanical Lead's flywheel/containment design as a
real input" — that firmware policy does not yet exist (`bench-imu-01-design.md`
§7.5.11/§7.5.12, unchanged through Rev 5), so this envelope is sized against
the ≥3000 RPM *target*, not a confirmed operating ceiling. Flagged as a
dependency for the next phase to track, not resolved here.

## B6. Print material assumptions

Per `.github/agents/mechanical-lead.agent.md`'s own guidance ("state the
assumed print material as an explicit ASSUMPTION if the human hasn't
specified one; do not silently pick a material and present it as decided"),
this file records two distinct material assumptions rather than one,
because they are governed by different considerations:

| Item | Assumed material | Confidence | Rationale |
|---|---|---|---|
| Enclosure | PLA or PETG (unspecified which, TBD next phase) | ASSUMPTION | REQ-309 explicitly permits/expects a 3D-printed enclosure ("3D-printable, piece count as needed") — no human specification of which filament exists yet; both are common FDM materials, the choice between them (PETG's better thermal/UV/impact tolerance vs. PLA's easier printing) is left to the next phase |
| Flywheel | Mild steel (NOT 3D-printed) | ASSUMPTION | See B2 — this is a **safety-relevant divergence** from the enclosure's own print-material assumption, not an oversight: a spinning flywheel under centrifugal load is a fundamentally different mechanical duty than a static enclosure wall, and 3D-printed plastic's interlaminar weakness makes it an inappropriate choice here regardless of what the enclosure itself is made of |

## B7. Total assembly mass (Part A subtotal + M1 + flywheel)

| Item | Mass | Confidence | Notes |
|---|---|---|---|
| Populated board assembly (Part A, A5 subtotal) | ≈19–20g | ESTIMATE | See A5 |
| M1 (motor) | 30g | **CONFIRMED** | DS-MTR-021. Loads the sensor/MCU PCB directly only if on-board (B3, unresolved) |
| Flywheel (proposed geometry) | 100g | ASSUMPTION | B2 target/proposed geometry (mass is the fixed target the geometry was derived to hit, by construction) |
| **Total assembly (excl. enclosure/bracket/fasteners)** | **≈149–150g** | ESTIMATE | Sum of the above three rows, regardless of how B3 resolves (the same three masses exist in the assembly either way; B3 only changes *which structure* carries M1's mass, not whether it exists) |

---

## Open items

Carried forward and expanded significantly for Rev 3. None of these are
treated as blocking this handoff-population task; each is flagged for the
phase where it becomes load-bearing.

**From Rev 2 (still open):**
1. J1 (USB-C receptacle) MPN not formally selected — height estimate
   (≈3.2mm) is illustrative only (`bench-imu-01-design.md` §13).
2. D1 (indicator LED) MPN not selected — Vf assumed only, no physical
   package/height confirmed.
3. Mounting-hole annular-ring adequacy not independently re-verified this
   revision.

**New for Rev 3 (this population):**
4. **J4 body height (≈11.0mm)** — ESTIMATE only, web-search-derived with
   partial older-revision corroboration; verify against the current Rev
   1.05 drawing or a physical sample before finalizing enclosure Z-height
   (A3).
5. **F1 physical size** — genuinely UNKNOWN, not previously flagged by
   anyone upstream; judged unlikely to be governing but not confirmed
   (A3).
6. **M1 mounting-hole bolt pattern** — ASSUMPTION only, sourced from a
   general hobbyist-motor-class web search, not a T-Motor-specific
   drawing; verify before finalizing enclosure/bracket screw-boss
   positions (B1).
7. **Motor mounting interface (on-board vs. off-board vs. hybrid)** — the
   single largest open item this revision. Explicitly and deliberately
   left open by the Circuit Engineer for the Mechanical Lead to decide in
   the next (enclosure-design) phase; this file records a non-binding
   leaning (off-board) but does not decide it. Safety-relevant via
   REQ-403/REQ-306; not itself an escalation trigger at this stage (see
   B3's full assessment) but must pass REQ-403's human-review gate
   whenever it is decided.
8. **Flywheel design** — no product exists; this file proposes a concrete
   geometry/material (steel, ⌀60mm×4.5mm disk) as a reasoned starting
   point for the next phase, explicitly not a final specification (B2).
9. **Motor phase-wire connector** — proposed (MC-1, keyed 3-pin) but
   contingent on item 7 above; an unkeyed-bullet-connector alternative is
   flagged as a live, undecided option (B4).
10. **Rotation clearance envelope margins** (+8mm radial / +3mm axial) —
    reasoned proposal, not a vibration-analysis result; flagged for
    verification once real hardware/measured runout exists (B5).
11. **Rotation envelope position/orientation within the enclosure** —
    UNKNOWN, dependent on item 7.
12. **Firmware max-speed ceiling** (REQ-405) — does not yet exist; the
    rotation envelope (B5) is sized against the ≥3000 RPM target, not a
    confirmed operating ceiling.

## Deferred fields

Unchanged from Rev 2, per `docs/architecture-evolution.md` §13 — still
explicitly out of scope until a real project need arises: thermal zones (as
a formal analysis — the qualitative sensor/motor separation in A1's zoning
and §9's guidance are not a substitute), antenna keep-out, STEP/neutral 3D
model reference, center of mass, battery wiring requirements, complex
keep-out zones beyond what B5 introduces for the flywheel specifically,
detailed cable-exit geometry beyond the rough positions given in A4/B4.
Advanced statistical tolerance stack-up analysis and motion/joint design
remain deferred per `docs/architecture-evolution.md` §10 (this file's own
basic print-fit tolerance allowance is Phase 1 enclosure-design work, not
yet performed since no `.scad`/dimensional-spec file exists yet — out of
scope for this population task).

## Handoff & change control

This file is maintained by the Mechanical Lead and read (not edited) by the
Circuit Engineer (confirmed via `bench-imu-01-design.md` §18.1–18.3, which
records that this file was never touched across Rev 2 through Rev 5). The
next consumer is the Mechanical Lead's own future enclosure-design session
(`.scad` + dimensional-spec table), and ultimately the Mechanical Reviewer.

**Process note, flagged rather than actioned**: a change of this scope
(full re-population, driven by a major new subsystem) would normally
warrant a `validation/change-log.md` (ECO) entry and a
`validation/change-impact-matrix.md` update under this project's own
change-control norms. **This task's explicit scope constraint is "your only
output this task is `hardware/mechanical-interface.md`"** — so neither of
those files has been touched this session. This is flagged here for the
Hardware Lead's attention as a likely follow-up action, not silently
skipped without note.

**This file's own assessment of what comes next**: given B5's finding that
the flywheel's proposed rotation clearance diameter (⌀76mm) exceeds this
file's own proposed board width (50mm), and given B3's open mounting-method
question changes where in the enclosure that clearance volume must even
live, the next phase (actual enclosure design) reads as a **full redesign**
of the Rev 2 enclosure, not a scoped addition to it. The Rev 2 box was
sized around a 60×40mm static board with no moving parts; nothing about
that box's proportions, wall layout, or assembly sequence can be assumed to
survive the addition of a rotating mass whose own keep-out volume is
larger than the board itself.
