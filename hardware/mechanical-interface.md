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

**Rev 4 addendum (additive only — Parts A/B and everything else above/below
this note are unchanged from Rev 3)**: Rev 3's enclosure (board + motor +
flywheel, rigidly bench-mounted) reached Design Complete. The roadmap's next
stage, "1-axis attitude control" (`docs/architecture.md` §11), requires the
whole Rev 3 assembly to rotate freely about a vertical axis. Requirements
Engineering and Component Selection for the free-rotation mechanism are
already human-approved (`requirements/requirements.md` §1b/§9f/§9g,
REQ-011/012/113/205/310/311/407/408; `bom/component-selection.md`'s
"Free-Rotation Support Mechanism" section) — the human has approved
**Candidate A: BC Precision 4LS-3 lazy-susan turntable ball bearing**. This
population adds **Part C** below (after Part B) recording that bearing's own
physical facts and the new mounting geometry designed around it, mirroring
exactly how Part B was added over Part A in Rev 3: a new, self-contained
Part, with its own confidence labels, leaving Parts A and B byte-for-byte as
they were. Date: 2026-09-10 (Part C addition). Author: Mechanical Lead (AI
agent).

**Rev 4.1 addendum (additive only — Rev 4's own Part C content, C1–C8, and
everything above/below this note are unchanged)**: Independent Mechanical
Review Cycle 5 of the Rev 4 free-rotation mechanism returned verdict
CONDITIONAL with 2 blocking HIGH findings — MISS-023 (REQ-407(b) pinch-
point/rotating-overhang hazard, never assessed) and MISS-024 (REQ-407(c)/
REQ-113 cable-entanglement/strain hazard for J1/J4, never assessed, since
both connectors now rotate with the bearing's top plate). This population
adds **C9** below (after C8), recording the new physical facts from this
Mechanical Lead's own fix for both findings — a new stationary guard ring
(`pinch_guard`) plus small rotating turn-counting/strain-relief features —
mirroring exactly how C1–C8 were added in Rev 4: new, self-contained
content, its own confidence labels, leaving C1–C8 byte-for-byte as they
were. Full engineering derivation lives in `bench-imu-01-dimensional-
spec.md` §18.12–§18.17. Date: 2026-09-14 (C9 addition). Author: Mechanical
Lead (AI agent).

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
| Length (X-axis) | 150 | mm | **REV 5 FIX (MISS-034, CRITICAL)**: read directly from the real KiCad project's own `Edge.Cuts` layer, `hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb`: `(gr_rect (start 0 0) (end 150 95))`. Independently cross-checked against `generate_pcb.py`'s own `BOARD_W = 150.0` constant and `hardware/pcb/README.md`'s own "Board outline: 150mm x 95mm" statement. Supersedes this row's own prior 100mm PROPOSAL (see "Board growth rationale — Rev 5 correction" below) | **CONFIRMED** |
| Width (Y-axis) | 95 | mm | Same source as Length above: real KiCad `Edge.Cuts` `(end 150 95)`, cross-checked against `generate_pcb.py`'s `BOARD_H = 95.0` and `hardware/pcb/README.md` | **CONFIRMED** |
| Thickness | 1.6 | mm | Unchanged from Rev 2 (standard FR4 thickness). Rev 3's motor-rail traces likely use heavier copper weight for current capacity, but that is an Electronics-domain layer-stackup detail that does not change overall board Z-thickness — not restated here. The real board's own layer stack-up/thickness was not independently re-confirmed this pass (out of MISS-034's own scope: board outline + hole pattern, not every A1/A3 field) | ASSUMPTION |
| Board area | 14,250 | mm² | 150 × 95. **REV 5 FIX**: was 5,000mm² (100×50 proposal) | Derived |
| Diagonal | ≈177.55 | mm | √(150²+95²) = √31,525 = 177.5528... **REV 5 FIX**: was ≈111.8mm. Independently re-verified by Mechanical Reviewer Cycle 11 (`validation/design-review.md`), which caught this row's own initial "≈177.8mm" arithmetic imprecision (Finding 4) — corrected here | Derived |

**Board growth rationale — Rev 5 correction (MISS-034)**: the "Board growth
rationale" paragraph immediately below this one is the ORIGINAL Rev 3 text,
preserved unedited for its own historical record (it explains why this file
once *proposed* 100×50mm) — it is now **superseded, not currently
accurate**, and must not be read as describing the real board. What
actually happened, per `validation/open-issues.md` MISS-034's own
chronology: this file's 100×50mm proposal (committed `350ac36`) was a
genuine, reasonable Rev 3 estimate at the time, but the real PCB layout
that followed (`a454b0c`) sized the board from **real, summed
footprint/courtyard area** for all 47+ actual components (not this file's
own component-*count* heuristic) under REQ-308's same relaxed ceiling,
landing at 150×95mm/14,250mm² — a **2.85×** area increase over Rev 2
(60×40mm/2,400mm²), not the 2.08× this file had proposed. No re-handoff
back to this file followed at the time; this Rev 5 pass is that re-handoff,
run per `docs/workflow.md` Phase 8. Both the length (150mm) and diagonal
(≈177.8mm) now sit **outside** REQ-308's own ~150mm soft desk-scale sanity
ceiling — see §3 "Overall envelope" re-check in
`bench-imu-01-dimensional-spec.md` for the full, honestly-disclosed
assessment (REQ-308 is a soft/"should" bound, not a hard ceiling, and this
was accepted as a real, disclosed trade-off, not silently passed over).

**Board growth rationale (ORIGINAL Rev 3 text, superseded — see the
correction immediately above; preserved unedited per this project's
additive-only historical-record convention, why 100×50mm, not some other
size)**: Rev 2 was
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
| MH-1 | 8 | 8 | 2.8mm (M2.5 clearance) | Through-hole | Bottom-left. **REV 5 FIX (MISS-034, CRITICAL)**: real KiCad `MountingHole_2.7mm_M2.5` footprint position, `hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb` (raw `(at 8 8)`), independently re-derivable from `generate_pcb.py`'s own `BOARD_MARGIN(5.0) + 3.0` formula. Supersedes this row's own prior 3.5mm-inset PROPOSAL | **CONFIRMED** |
| MH-2 | 142 | 8 | 2.8mm (M2.5 clearance) | Through-hole | Bottom-right. Real KiCad footprint `(at 142 8)` = `BOARD_W(150) - BOARD_MARGIN(5.0) - 3.0` | **CONFIRMED** |
| MH-3 | 142 | 87 | 2.8mm (M2.5 clearance) | Through-hole | Top-right. Real KiCad footprint `(at 142 87)` = `(BOARD_W-8, BOARD_H(95)-BOARD_MARGIN-3.0)` | **CONFIRMED** |
| MH-4 | 8 | 87 | 2.8mm (M2.5 clearance) | Through-hole | Top-left. Real KiCad footprint `(at 8 87)` = `(8, BOARD_H-BOARD_MARGIN-3.0)` | **CONFIRMED** |

**REV 5 FIX (MISS-034)**: the real board has exactly **4** mounting holes —
independently counted directly in the raw `.kicad_pcb` file this session (4
instances of footprint `MountingHole_2.7mm_M2.5`, at the 4 coordinates
above). The prior **MH-5/MH-6** rows (a Rev 3 "motor zone" mid-edge pair,
proposed for extra rigidity near the then-hypothesized on-board
motor-driver hot zone) **do not exist on the real board** and are removed,
not merely repositioned — there is no real second hole pair, because the
"motor zone" concept itself does not describe the real board (the real M1
is a 3-pin phase-wire terminal block for an OFF-board motor, per
`hardware/pcb/bench-imu-01/generate_pcb.py`'s own `PLACEMENT` dict, not an
on-board motor-driver hot zone needing extra local stiffening). REQ-304's
own floor ("≥4 mounting holes") remains satisfied by the real 4-hole
pattern alone, same as it was intended to be before MH-5/6 were proposed as
an enhancement beyond that floor.

**MISS-043 correction (2026-09-04) to the paragraph immediately above**:
describing MH-5/6 as a "(now-moot) enhancement" when this file was first
corrected for MISS-034 was itself an incomplete framing, flagged by a
cross-session review (PR #41/MISS-035, independently corroborated) — only
the "motor zone" FRAMING was fictional; the underlying PHYSICAL CONCERN
Rev 3's own MH-5/6 comment stated ("a board supported only at 4 corners
risks excess flex/vibration transmission") is **not moot** — if anything
it is stronger now, since the real board (150mm) is 50% longer than the
100mm Rev 3 proposal that first raised it, with no mid-span mounting hole
anywhere on the real board to bolt a real standoff into (adding one would
be an Electronics-side PCB revision, out of this file's own Mechanical
scope). `bench-imu-01-enclosure.scad` now adds a **passive (non-fastened)
mid-span support pad** (`mid_span_support()`, ASSUMPTION) that the board
simply rests on at its own physical midpoint, as a partial mitigation that
does not require a PCB revision — deliberately undersized 0.4mm below the
4 real standoffs' own height (`mid_support_gap`, MISS-045 — biases the
pad toward a benign "travel limiter" role rather than an at-rest preload
that a real, in-spec board bow could otherwise turn harmful) — see
`bench-imu-01-dimensional-spec.md`'s own new subsection for the full
rationale, and MISS-043/MISS-045 (`validation/open-issues.md`) for the
complete disclosure, including this mitigation's own real limitations (not
fastened, no real vibration/FEA analysis performed, the 0.4mm height bias
not independently verified by a manufacturing-process-level analysis, not
a substitute for a true fastened mid-span mounting point).

All four holes assume M2.5 screws with a standard 0.3mm/side clearance
(2.5+0.3×2=3.1mm → rounded to a common 2.8mm clearance-drill convention,
unchanged reasoning from Rev 2) — **note, disclosed not silently
corrected**: the real footprint's own name ("`MountingHole_2.7mm_M2.5`")
implies the real PCB's own drill is 2.7mm nominal, slightly smaller than
this file's own 2.8mm clearance-hole assumption; this is a trivial (0.1mm),
non-blocking difference between two different holes (the PCB's own drill
vs. the enclosure standoff's own pilot-hole clearance target) — not
reconciled further this pass, out of MISS-034's own scope (board outline +
hole PATTERN, not exact drill-diameter cross-referencing). PCB material
sufficient annular ring around each hole — not independently re-verified
this revision, carried forward as an ASSUMPTION.

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
| Bare PCB substrate | 42.2g | ESTIMATE | **REV 5 FIX (MISS-034, CRITICAL)**: 150mm × 95mm × 1.6mm × 1.85g/cm³ (standard FR4 density, same method/density as Rev 2/3) = 22.8cm³ × 1.85g/cm³ = 42.18g, rounded. Was 14.8g (100mm×50mm×1.6mm proposal) — the prior figure's own "2.08× area growth vs. Rev 2's 7.1g" framing is now superseded: the real board is a **2.85×** area increase over Rev 2 (60×40mm), giving 42.18g/2.85≈14.8g cross-check against Rev 2's own 7.1g×2×... — more directly, 42.18g/7.1g=5.94×, consistent with (150×95)/(60×40)=5.94× exactly, i.e. this recompute is internally consistent against Rev 2's own bare-board figure by the real area ratio, not the stale proposal's ratio |
| Rev 2 components (U1–U4, J1–J3, SW1, D1, R1–R5, C1–C9) | ≈1.8–2.0g | ESTIMATE (carried forward) | Unchanged from Rev 2's own figure — component masses don't change with board area |
| Rev 3–5 components (U5, U6, J4, D2, D3, F1, R6–R15, C10–C17) | ≈2.5–3.0g | ESTIMATE | Unchanged from the prior estimate — component masses don't change with board area. J4 (barrel jack, metal-bodied) dominates at ≈1.5g; U5/U6 (HTSSOP) ≈0.15–0.2g each; D2/D3 (SMB) ≈0.1g each; F1 (radial PTC, epoxy body) ≈0.3–0.4g; R6–R15/C10–C17 (small SMD) negligible individually, ≈0.1–0.15g combined |
| **Subtotal: populated board assembly** | **≈46.5–47.2g** | ESTIMATE | Sum of the above three rows. **REV 5 FIX**: was ≈19–20g, +≈27.4g driven entirely by the bare-substrate correction above |

**Reconciliation against the current total system mass baseline (REV 5,
MISS-034)**: this file's own Part C (Rev 4/4.1 free-rotation mechanism)
already independently reconciled the FULL assembled-system mass at
**≈1173.4g** (`hardware/mechanical/bench-imu-01-dimensional-spec.md` §18,
cross-checked against `validation/design-review.md`'s own Cycle 6
independent re-render, agreeing to within 0.05g) — this is the figure this
bare-board recompute must be consistent with, **not** a stale ≈300g figure
that appears in unrelated prose elsewhere in this repo (e.g.
`bom/component-selection.md`'s own friction-torque margin calc, tracked
separately as MISS-029, RESOLVED, and `requirements/requirements.md`
REQ-310's own "~300g representative" wording — neither of those describes
this board's own mass, and neither is touched by this fix). The +≈27.4g
bare-board increase computed above shifts the ≈1173.4g total to
**≈1200.8g** (+2.33%) — see `bench-imu-01-dimensional-spec.md`'s own Rev 5
changelog for the full arithmetic and an explicit check that this small
shift does not materially affect the bearing friction-torque margin
(driven by rotating-assembly mass, not total mass) or the stand-plate
CG/tip-over safety margin (a ≈6.2× margin at the old mass; a 2.33% mass
increase moves this to ≈6.06×, still enormously non-binding) — not
re-derived from scratch, since the shift is small enough that a
proportional check is adequate and honestly disclosed as such, not a full
re-sweep of `bench-imu-01-dimensional-spec.md` §18.3's own CG/tip-over
analysis.

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

# Part C — Free-rotation support mechanism (new, Rev 4)

**Why this needs its own part, not just new table rows**: Parts A and B both
describe facts about **components mounted to, or contained within, a rigid,
bench-fixed enclosure**. Part C is different in the same qualitative way
Part B was different from Part A: it describes a **bought mechanical
hardware component** (not a PCB part, not a custom-machined bracket) that
introduces a genuinely new axis of motion — the *entire* Rev 3 assembly (not
a motor's internal rotor) rotating freely about a vertical axis relative to
the bench — plus a new physical piece count (a 4th printed part) and a new
fastener class this file has not previously needed to justify. Per
`requirements/requirements.md` §1b/§9f/§9g and REQ-011/012/113/205/310/311/
407/408 (human-approved; not re-litigated here) and `bom/component-selection.md`'s
"Free-Rotation Support Mechanism" section, the human has approved **Candidate
A: BC Precision 4LS-3 lazy-susan turntable ball bearing** as the mechanism.
This part records that bearing's own physical facts and the new mounting
geometry the Mechanical Lead has designed around it — **additively**, per
`.github/agents/mechanical-lead.agent.md`'s explicit instruction: nothing in
Parts A/B or in the existing `.scad` file's Rev 3 modules is edited, resized,
or removed by this population. Everything in Part C is either a new fact
about a bought part, or a new solid feature that extends *outward/downward*
from the existing Rev 3 geometry.

## C1. Bearing (free-rotation mechanism) physical facts

**Source**: BC Precision 4LS-3 lazy-susan turntable ball bearing, product
page, Evidence ID **DS-BRG-001** (`datasheets/evidence-log.md`,
`datasheets/bcprecision_4ls-3-lazy-susan-turntable-bearing_web-product-page.md`).

| Parameter | Value | Unit | Confidence | Notes |
|---|---|---|---|---|
| Overall/nominal size (OD) | 4 (≈101.6) | in (mm) | **CONFIRMED** | DS-BRG-001 product-page spec block |
| Center hole diameter (thru both plates) | 2.170 (≈55.1) | in (mm) | **CONFIRMED** | Same source |
| Overall thickness (both plates + captive ball race) | 5/16 (≈7.9) | in (mm) | **CONFIRMED** | Same source |
| Load capacity | 300 (≈136.1) | lb (kg) | **CONFIRMED** | Same source |
| Construction | 2× stamped galvanized-steel plates (rotating top + stationary bottom) joined by a captive ball race | — | **CONFIRMED** | Same source |
| Price | $13 | USD | **CONFIRMED** | Same source — REQ-501's ≤$15 target context (not this file's concern to re-litigate, see `bom/component-selection.md`) |
| "Suggested top diameter" | 12–25 | in | **CONFIRMED** (as a published generic suggestion) | Same source — a stability rule of thumb for the bearing's typical **heavy-furniture lazy-susan** use case; **explicitly NOT treated as a requirement at this rig's ~600g scale** (see C3/C4 — this file sizes the actual stand-plate footprint from a computed CG/tip-over analysis instead, per the task's own explicit direction not to just match this generic figure) |
| Mounting-hole count/spacing, per plate | Not published by the manufacturer | — | **UNKNOWN → ASSUMPTION** (see provenance below) | Generic lazy-susan-hardware-class convention adopted instead — Evidence ID **DS-BRG-007** |
| Bearing mass (both plates + ball race) | ≈130 | g | **ESTIMATE** (see provenance below) | No manufacturer weight found anywhere consulted this session |

**Bolt-pattern provenance (why ASSUMPTION, heavily hedged — mirrors B1's own
"Bolt pattern — provenance" template)**: DS-BRG-001's own product page does
not state a mounting-hole count, spacing, or size for either plate. A web
search this session found a specific, cross-checkable claim from a
lazy-susan-hardware retailer (lily-bearing.com, "Lazy Susan Hardware Kit:
What's Inside and How to Install") describing the **generic convention** for
this class of turntable bearing: **4 mounting holes evenly spaced per
plate**, sized for **#6 wood/self-tapping screws** with **≈4mm (5/32in)
pilot holes** (that source's own recommendation is for screwing into
*wood*, i.e. furniture — this file adapts the screw-size implication, not
the pilot-hole size itself, for a PETG target; see C2). The same source
independently states a 300lb load-capacity figure for a 4in-class bearing,
which matches DS-BRG-001's own stated capacity exactly — an independent
cross-validation that this is a real, applicable convention for this bearing
class, not an unrelated citation. This is recorded here as **Evidence ID
DS-BRG-007**, explicitly flagged as **a generic convention for this bearing
*class*, not this specific SKU's own confirmed hole pattern** — this SKU's
own hole positions are not published and were not found anywhere this
session. **This must be verified against the actual physical part before
any mounting boss position is finalized for manufacture** (no physical
prototyping is happening this cycle, REQ-502, so this is not treated as a
blocking escalation — it is a starting-point ASSUMPTION sufficient for
paper-design geometry, exactly as B1's own motor bolt-pattern ASSUMPTION is
treated). Because the true hole positions are unknown, the new mounting
geometry (C2/C4) is deliberately a **solid annular band**, not discrete
bosses at hard-coded positions — this makes the design robust to the real
bearing's actual hole pattern differing from the modeled default (a hole can
be field-drilled anywhere within the band), rather than betting the whole
design on an unverified assumption being exactly right.

**Bearing-mass provenance (why ESTIMATE, and why it is a chain of
estimates)**: no manufacturer weight is published on DS-BRG-001, and a web
search this session returned internally inconsistent figures for "a single
4in lazy-susan bearing" (some sources implying ≈77g, others ≈160g) — too
inconsistent to cite as a source, so **not treated as corroboration**. This
file instead derives its own analytic estimate from the bearing's own
CONFIRMED dimensions (OD 101.6mm, ID 55.1mm) plus two further sub-estimates:
stamped steel plate gauge (≈1.2mm, ESTIMATE — thin stamped galvanized steel
is visually/functionally consistent with the product photos but not itself
measured or cited) and ball-race size/count (24× ≈6mm steel balls,
ESTIMATE). Build-up: 2 plates (annular stampings, OD 101.6mm/ID 55.1mm,
1.2mm gauge, steel density 7.85×10⁻³ g/mm³) ≈107.8g + ball race (24× 6mm
steel balls) ≈21.3g → **≈130g total (rounded from 129.1g)**. This falls
within the ambiguous 77–160g web-search range (weak corroboration only —
that range is wide enough that almost any plausible figure would fall
inside it, so this is not claimed as confirmation, only as "not
contradicted"). **This is a chain of estimates, not a single measurement**:
flagged explicitly so the Reviewer/Hardware Lead can see it is built on two
further unverified sub-assumptions (plate gauge, ball count/size), not
independently measured as a whole.

## C2. New mounting flange (added below the existing `base()` floor, Rev 4)

This is a genuinely **new solid feature**, unioned onto the underside of the
existing flywheel-bay floor (`motor_platform()`'s own floor disc, part of
`base()`) — it does not modify, resize, or remove any existing Rev 3 module.
It bolts the bearing's **top (rotating) plate** to the existing Rev 3
assembly.

| Parameter | Value | Unit | Confidence | Rationale |
|---|---|---|---|---|
| Outer radius (`bmount_flange_or`) | 52.5 | mm | **DERIVED** | Reuses the existing `fw_flange_or` value exactly — this radius already spans past the bearing's own 50.8mm (101.6mm OD /2) radius with margin, and reusing an existing named dimension (rather than inventing a new, close-but-different one) keeps the design's own internal consistency legible |
| Inner radius (`bmount_flange_ir`) | 28.0 | mm | **ASSUMPTION** | Clears the bearing's own 55.1mm ID (27.55mm radius) with a small working margin; also serves as the coaxial tether pass-through bore (see C6) |
| Thickness, new territory below existing Z=0 (`bmount_flange_t`) | 6.0 | mm | **ASSUMPTION** | Judged adequate to host a 5.0mm-deep blind pilot hole (below) with a 1.0mm margin, mirroring this file's own `standoff_h`/`standoff_pilot_depth` (6.0/5.0mm) precedent |
| Deliberate CSG fuse-overlap into existing floor material | 1.0 | mm | **ASSUMPTION** | Mirrors the existing `.scad` file's own `bridge_fuse_overlap`(2.0mm) convention — ensures the new flange has genuine volumetric overlap with the pre-existing floor disc for a robust union, not a knife-edge coincident-face touch |
| Bolt-circle radius for the 4 mounting screws (`bmount_bolt_circle_r`) | 40.0 | mm | **ASSUMPTION** | Default/documented pattern only (DS-BRG-007's hole count, not this SKU's confirmed positions) — sits roughly mid-band between the flange's inner (28.0mm) and outer (52.5mm) radii, a sensible default that avoids both the bore and the outer edge; **must be verified against the real bearing before manufacture** |
| Pilot-hole diameter (`bmount_pilot_dia`) | 2.8 | mm | **ASSUMPTION** | = 0.8× a #6 machine screw's standard 3.5mm major diameter (ANSI/ASME B1.1, a standard reference figure) — the same 80% pilot-to-major-diameter ratio already used by this design's own `standoff_pilot_dia`/M2.5 self-tap joint (2.0mm/2.5mm = 80%), applied here for consistency rather than inventing a new ratio |
| Pilot-hole depth (`bmount_pilot_depth`) | 5.0 | mm | **ASSUMPTION** | = `bmount_flange_t` − 1.0mm blind margin, numerically identical in pattern to the existing `standoff_pilot_depth` = `standoff_h` − 1.0mm |
| Mass (this feature only) | ≈47.1 | g | **ESTIMATE** (computed) | See C3 for the full mass/CG methodology |
| Position | Centered at (`fw_cx`,`fw_cy`) = (53.5, 52.5) — reuses the existing flywheel-bay center | mm | **DECIDED** (design choice, not a data fact) | See C3 — chosen deliberately over the assembly's own true computed CG, because no wider Z=0 floor exists anywhere else to structurally carry a differently-centered flange; the resulting CG-to-axis offset is a disclosed, quantified input to the stand-plate sizing (C3/C4), not an oversight |

**Geometric non-interference check (performed, not assumed)**: the existing
flywheel-bay floor disc (`motor_platform()`) is a solid disc of radius
`fw_bay_outer_r`=43.5mm — strictly smaller than the new flange's own outer
radius (52.5mm) and strictly larger than the new flange's own inner radius
(28.0mm). This means: (a) in the radial band 28.0–43.5mm, the new flange
genuinely fuses against already-solid existing material (a real bonded
joint, not a coincident-face touch); (b) in the radial band 43.5–52.5mm, the
new flange adds genuinely new material where nothing existed before (safe,
purely additive); (c) the existing floor disc's own small cut features (4×
M3 motor-mount clearance holes at ≈8.5mm radius from center, and the central
≈3.4mm motor-shaft-clearance hole) all sit well inside the new flange's own
28.0mm bore — i.e., entirely outside the new flange's own solid material —
so nothing about the new flange touches, narrows, or otherwise affects those
pre-existing cuts.

**Manufacturability finding — caught and disclosed this session, not
silently passed over**: because the new flange's own bore (r<28mm) is
hollow for its full height, while the pre-existing floor disc directly above
it (old Z≥0) is solid across r=0–43.5mm (a full disc, not itself
bored out), the transition between the two — where the flange's own open
bore meets the existing disc's solid underside — is an internal,
**hidden** transition that spans roughly a 56mm-diameter circle (minus the
disc's own small pre-existing holes) with **nothing directly beneath it**
in the flange's own printed layers. This does **not** meet this design's own
stated 45°-overhang / 10mm-bridge-span manufacturability rules on its own.
Three alternatives were considered and rejected: (1) tapering/widening the
flange's own bore near the top does not help, because the problem is the
*existing* disc's own broad, un-bored underside, which this population is
not permitted to modify; (2) printing the whole base+flange assembly
upside-down (existing cap-mounting flange band as the new bed face) shrinks
this specific problem but breaks several *other* already-validated Rev 3
features that depend on floor-down printing (standoffs, wire bridge) — a
strictly worse trade; (3) printing the flange as a fully separate,
adhesively-bonded piece avoids the issue entirely but turns it into an
un-asked-for 5th printed piece, contradicting the task's own "4 total
pieces" framing, for a hidden, non-mating, non-precision surface. **Given
this transition is entirely internal to the tether-cable bore — not a
visible, mating, or precision surface — the disclosed resolution is to
print the fused base+flange piece with slicer-generated support material
enabled for this one internal region** (support is reachable and removable
through the bore's own 56mm-diameter straight-through opening — not a
blind/enclosed cavity). This is recorded as a genuine, confirmed
manufacturability caveat, not a clean pass — see `bench-imu-01-dimensional-
spec.md` §18 for the full analysis and the self-check record.

## C3. CG / tip-over analysis (new, Rev 4)

**Methodology**: full analytic primitive decomposition of every existing
Rev 3 solid (floor disc, motor-platform boss, flywheel-bay wall tube, flange
band, wire-bridge net, containment-cap disk+skirt, PCB-bay floor/wall/roof,
6 standoffs and 4 lid tabs at their real interface-file positions), each
volume computed from its own exact modeled geometry (not a bounding-box or
surface-area proxy), converted to mass at PETG's density (1.27g/cm³, per
`bom/component-selection.md`'s own Rev-3-era PETG TDS citation), then summed
with the existing point masses (M1 motor 30g CONFIRMED, flywheel 100g
ASSUMPTION, populated PCB 19.5g ESTIMATE, all at their own interface-file
positions). This was independently computed this session — not copied from
the supervising session's own rougher, components-only estimate — and cross-
checked against it as a sanity bound (see below).

**A real, disclosed discrepancy**: this analytic method finds Rev 3's own
plastic mass to be **≈207.9g**, materially higher than `bom/component-
selection.md`'s own bounding-shell-surface-area estimate (130–170g) for the
same enclosure. At least one large contributor (the flywheel-bay wall tube,
≈44,849mm³) was independently hand-verified via the exact annulus-volume
formula to rule out a computation bug. The most likely explanation: a
generic "outer-shell-area × wall-thickness" proxy under-counts doubled-up-
thickness features this enclosure actually has (the 4mm containment wall
over its full height, the added flange band, and the containment cap's own
disk+skirt) — i.e., the analytic method is judged **more accurate**, not the
bounding-shell estimate, but this is disclosed as a genuine finding for the
Hardware Lead/Reviewer to weigh, not silently reconciled.

| Quantity | Value | Confidence |
|---|---|---|
| Rev 3 plastic mass (analytic, all existing solids) | ≈207.9g | ESTIMATE (computed, see above) |
| Rev 3 total mass (plastic + M1 + flywheel + populated PCB) | **357.4g**, CG=(53.63, 68.68, 28.51)mm | ESTIMATE — CG_y falls within the supervising session's own 63–78mm bracketing range, a positive cross-check despite the plastic-mass discrepancy |
| New flange mass (C2) | ≈47.1g | ESTIMATE (computed) |
| **Rotating assembly total** (Rev 3 total + new flange; excludes the bearing and stand plate, which do not rotate) | **404.5g**, CG=(53.61, 66.80, 24.85)mm | ESTIMATE |
| Horizontal offset of rotating CG from the bearing's own axis (53.5, 52.5) | **r_rot ≈ 14.30mm** (X-component negligible, +0.11mm; Y-component dominant, +14.30mm) | DERIVED from the above |
| Bearing mass (does not rotate relative to itself; on-axis, does not affect r_rot) | ≈130g | ESTIMATE (C1) |
| Stand-plate mass at the chosen radius (C4) | ≈67.3g | ESTIMATE (computed) |
| **Total system mass** (rotating assembly + bearing + stand plate) | **≈601.8g** | ESTIMATE |

**Why the flange is centered on the existing flywheel-bay axis (53.5, 52.5)
rather than the true computed CG (Y≈68.7mm)**: no wider Z=0 floor exists
anywhere else in the Rev 3 geometry to structurally carry a bearing centered
further toward the PCB bay — reusing the flywheel bay's own existing center
is the only position where the new flange can genuinely fuse against
existing solid floor material per C2's own non-interference check. This
turns the CG-to-axis offset into a disclosed, quantified **design trade-off**
(the 14.3mm r_rot above), sized directly into the stand-plate's own tip-over
margin (C4) rather than an unexamined choice.

**Total system mass vs. the human's own working estimate (≈280–320g,
`requirements/requirements.md`/`bom/component-selection.md`)**: the computed
figure (≈601.8g) is roughly double. This is disclosed prominently, not
smoothed over — it is attributed mainly to the higher analytic plastic-mass
finding above (≈208g vs. an ≈130–170g estimate) plus the new flange/bearing/
stand-plate mass the original estimate did not yet include, **not** to an
error in this computation (the largest single contributor was independently
hand-verified). This materially changes the tip-over analysis's own starting
point and is exactly why C4's stand-plate sizing uses this file's own
freshly-computed total, not the earlier rough figure.

## C4. New fixed stand plate (4th printed piece, Rev 4)

Bolts to the bearing's **bottom (stationary) plate**; this is the piece that
actually contacts the desk. Sized from an actual computed tip-over analysis,
**not** matched to the bearing's own generic "12–25in suggested top
diameter" (C1) — that suggestion is a heavy-furniture stability rule of
thumb for a very different load class and is not applicable at this rig's
~600g scale.

**Tip-over methodology**: because the stand plate is a full circle centered
on the same bearing axis the rotating assembly orbits, the combined system's
overall CG-to-axis horizontal offset (`d_offset` = m_rotating·r_rot /
m_total) is **constant regardless of rotation angle** — a key finding that
validates a circular (rather than, say, a rectangular or a directionally-
biased) stand-plate shape: stability here is genuinely angle-invariant, not
just checked at one worst-case angle. A sweep of candidate stand-plate outer
radii (50–80mm) was computed, tracking static margin (stand radius /
`d_offset`), system CG height above the new ground plane, and the
approximate horizontal bump force at CG height needed to begin tipping
(`F_tip`).

| Parameter | Value | Unit | Confidence |
|---|---|---|---|
| Outer radius (`stand_plate_or`) | 60.0 | mm | **DECIDED** (from the sweep, see below) |
| Inner radius (`stand_plate_ir`) | 28.0 | mm | **DERIVED** — matches `bmount_flange_ir` exactly, keeping the tether channel continuous/coaxial start to finish |
| Thickness (`stand_plate_t`) | 6.0 | mm | **ASSUMPTION**, mirrors `bmount_flange_t` |
| Bolt-circle radius | 40.0 | mm | **DERIVED**, reuses `bmount_bolt_circle_r` — same default-pattern caveat as C2 |
| CG-to-axis offset, chosen design (`d_offset`) | ≈9.61 | mm | DERIVED (constant at all rotation angles, see above) |
| Static margin (stand radius / `d_offset`) | **≈6.2×** | — | Judged a comfortable, though not independently-cited/standard-referenced, margin against an accidental bench nudge — a qualitative judgment call, not a certified pass |
| System CG height above new ground | ≈32.6 | mm | DERIVED |
| Approx. horizontal force to begin tipping (`F_tip`) | ≈9.13N (≈931 gram-force) | — | DERIVED from the above; not compared against any cited "typical bump force" standard — presented as a computed figure for the Hardware Lead/Reviewer's own judgment |

**Why 60.0mm and not the bearing's own 12–25in (305–635mm) suggestion**: at
this design's actual ≈602g total system mass and ≈9.6mm CG offset, a
120mm-diameter stand plate already yields a 6.2× static margin — a
stand plate anywhere near the bearing's own generic furniture-scale
suggestion would be wildly, unnecessarily oversized for this rig (and would
itself blow well past the existing enclosure's own [**REV 5 (MISS-034,
2026-09-04) DISCLOSURE, Mechanical Reviewer Cycle 11 Finding 3**: this
figure was 111.4×170.6mm at the time this Part C3/C4 analysis was
originally written (Rev 4) — the enclosure's own CURRENT assembled
footprint is 161.4×215.6mm, per `bench-imu-01-dimensional-spec.md` §3
(Rev 5). 120mm remains comfortably smaller than BOTH the old and current
figures in both dimensions, so this section's own qualitative conclusion
is unaffected — but the ≈602g mass/≈9.61mm CG-offset/6.2× margin numbers
elsewhere in this same C3/C4 section are themselves ALSO now stale relative
to Rev 5 (and, separately, relative to Rev 4.1's own later `pinch_guard()`
mass addition) — this is the same gap already tracked in full at MISS-038
(`validation/open-issues.md`), not re-derived here] 111.4×170.6mm assembled
footprint in one dimension). This is exactly the outcome the task's own
framing anticipated: the generic suggestion is for a completely different
load class and use case, and this file's own computed analysis — not that
suggestion — is what actually sizes the part.

**Geometric manufacturability check**: at 60.0mm outer / 28.0mm inner
radius, the 40.0mm bolt-circle sits 20mm inside the outer edge and 12mm
outside the inner bore — both generous margins, no manufacturability
concern. Unlike the new flange (C2), the stand plate is a **uniform-cross-
section annulus for its entire thickness** — nothing else attaches to or
fuses with it — so it has **no** analogous internal-overhang concern; it
prints flat, either face down, with zero support needed.

## C5. Fastener class — bearing-to-flange / bearing-to-stand-plate joints

**Decision**: self-tapping screws directly into PETG, mirroring the
existing `base_tab()`/PCB-lid joint precedent (M2.5 self-tap), rather than
the containment cap's heat-set-brass-insert precedent. **Justification,
stated explicitly rather than defaulted silently** (per this file's own
established practice of re-justifying each new joint class): the
containment cap's insert joint is safety-relevant and repeatedly
accessed/re-torqued over the product's life (B1-style reasoning, mirrored
from the `.scad` file's own §12 fastener table) — it must resist strip-out
under exactly the hazard event it exists to contain. The new bearing joints
are neither: they are not defending against a specific disclosed hazard
event the way the cap is, and they are **assembled once**, not repeatedly
opened/closed. **One caveat disclosed, not glossed over**: unlike the PCB
lid tabs (which only carry the lid's own small mass), this joint carries
the **full weight of the rotating assembly** in shear/tension across the
rotation duty cycle — a different loading character than the lid-tab
precedent it otherwise mirrors. This is flagged as a first-cycle engineering
judgment call, not an independently load-tested conclusion — no
fastener-load (torque/shear/pull-out) calculation was performed for this
joint, consistent with this being explicitly out of Phase 1's scope
(mirrors the existing, already-disclosed MISS-011 gap on the containment-cap
joint in `bench-imu-01-dimensional-spec.md`).

## C6. Electrical tether routing (REQ-113) — confirmed, no new cutout needed

REQ-113 calls for a flexible service-loop tether (not a slip ring) for any
electrical connections crossing the rotating interface. **Checked explicitly
this session, not assumed**: the bearing's own ≈55.1mm center hole, this
file's new flange bore (`bmount_flange_ir`=28.0mm radius) and the new stand
plate's own bore (`stand_plate_ir`=28.0mm radius, same axis) are all
coaxial and unobstructed — confirmed via the C2 non-interference check
above, which shows none of the new mounting-boss/pilot-hole geometry
intrudes into this bore at any point. **No new cutout in the existing base
is required** for a tether entering along this axis — the existing
enclosure's own connectors (J1 USB-C, J4 barrel jack) remain externally
accessible on the PCB bay's own side walls exactly as in Rev 3, unchanged,
which is itself already sufficient to satisfy REQ-113 literally (a simple
hanging service loop from J1/J4, needing zero new geometry at all, is the
simplest reading of the requirement). The coaxial bore through the bearing's
own axis is confirmed available as a **supplementary** path (e.g., useful if
a future revision wants to bring power up through the base's own rotation
axis instead of around the side), but is not itself required to satisfy
REQ-113 this cycle. **One disclosed limitation, not created by this
population but confirmed unchanged by it**: a wire entering via this
coaxial bore can only continue further into the flywheel-bay's own interior
(above the existing floor) through the pre-existing, unchanged
≈3.4mm-diameter motor-shaft-clearance hole (`motor_platform()`, dead
center) — a real bottleneck for that specific path, disclosed here rather
than silently assumed away, though not itself a blocking issue since J1/J4
remain externally accessible regardless of how this bore is used.

## C7. Assembly-order addendum (new, Rev 4)

Extends (does not replace) the existing Rev 3 6-step sequence
(`bench-imu-01-dimensional-spec.md` §14). The Rev 3 sub-assembly (steps 1–6)
is unchanged and is treated as a single completed unit here:

7. Bolt the bearing's **bottom (stationary) plate** to the new stand plate —
   fully accessible, flat, done separately from the rest of the assembly.
8. With the completed Rev 3 sub-assembly held upside-down (a handling
   instruction, not a structural concern — nothing is trapped or blind at
   this step), bolt the bearing's **top (rotating) plate** to the new
   mounting flange on the underside of the base.
9. Rest/engage the two halves together via the bearing's own captive ball
   race — this is what physically unites the fixed stand-plate assembly
   (steps 7) with the rotating base assembly (step 8); it is not itself a
   blind or inaccessible fastening step.
10. Route the tether (C6) through the coaxial bore just before or during
    this final stacking step.

No step in this addendum requires reaching past an already-installed part
from an inaccessible direction — see `bench-imu-01-dimensional-spec.md`
§18 for the full re-derivation and self-check.

## C8. Total system mass (Part A/B subtotal + Part C additions)

| Item | Mass | Confidence | Notes |
|---|---|---|---|
| Rev 3 total (Part A/B subtotal, B7) | ≈149–150g (components only) / ≈357.4g (components + this file's own computed enclosure plastic, C3) | ESTIMATE | See C3 for why this file's own plastic-mass figure diverges from B7's own components-only framing |
| New mounting flange (C2) | ≈47.1g | ESTIMATE | |
| Bearing (C1) | ≈130g | ESTIMATE | |
| New stand plate (C4) | ≈67.3g | ESTIMATE | |
| **Total system mass** | **≈601.8g** | ESTIMATE | Roughly double the human's own working ≈280–320g estimate — disclosed prominently in C3, attributed mainly to the higher analytic plastic-mass finding, not an error |

## C9. Rev 4.1 additions — MISS-023/MISS-024 mitigation geometry (new
interface facts)

Populated by this Mechanical Lead in response to Independent Mechanical
Review Cycle 5's 2 blocking HIGH findings (`validation/open-issues.md`
MISS-023, MISS-024; `validation/design-review.md`'s "Mechanical Reviewer —
Cycle 5" entry). Extends Part C additively — C1–C8 above are unchanged. Full
engineering rationale/derivation lives in
`bench-imu-01-dimensional-spec.md` §18.12/§18.13; this section states the
resulting interface-level facts only.

**MISS-023 fix — `pinch_guard`, a new 5th printed piece (stationary):**

| Parameter | Value | Unit | Confidence | Rationale |
|---|---|---|---|---|
| True max swept radius of the rotating assembly (`rotating_env_max_r`) | 126.424 | mm | **DERIVED** (tool-verified, direct mesh measurement, not hand geometry) | Independently re-computed this pass — corrects the Cycle 5 Reviewer's own hand-derived 115.9mm figure, which measured only a pure Y-axis distance and missed the governing corner's X-offset; the true figure is larger (more conservative), not smaller — spec §18.12.1 |
| Guard inner radius (`pinch_guard_ir`) | 60.0 | mm | **DERIVED** = `stand_plate_or` exactly (C4) | Flush-adjacent to, not overlapping or fastened to, the existing stand plate — verified via direct boolean intersection (≈0 shared volume) — spec §18.12.5 |
| Guard outer radius (`pinch_guard_or`) | 115.0 | mm | **DECIDED** from an explicit coverage-vs-footprint trade-off (77.7% hazard-band coverage, 11.4mm residual radial gap, 230mm assembled diameter) | Not sized to full theoretical closure (126.424mm) deliberately — see spec §18.12.3 for the full table and the margin-vs-coverage reasoning |
| Guard height (`pinch_guard_h`) | 14.9 | mm | **DERIVED** = 19.9mm confirmed rotating-envelope height floor − 5.0mm stated margin | Height floor independently re-derived via direct mesh measurement (not assumed carried over) — spec §18.12.2 |
| Residual unguarded radial gap | 11.4 | mm | **DISCLOSED, not fully closed** | Backstopped by an operational keep-clear-zone warning (REQ-205 tightening), not by further geometry this pass — spec §18.12.6 |
| Mass (this feature only) | ≈570.6 | g | **ESTIMATE** (computed from the exact modeled/mesh volume, same method as C2/C3) | 449,258mm³ solid PETG @ 1.27g/cm³ — see mass-rollup note below; this is the single heaviest new part this pass introduces, larger than the bearing (C1), flange (C2), and stand plate (C4) combined |
| Print approach | 4 separate 90° quadrants (assembled ring only touches, not fastened) | — | **DECIDED** | Avoids inventing an undocumented printer-bed-size assumption (none exists anywhere in this project) — each quadrant's own bounding box (~115×115mm) is small enough for virtually any consumer FDM printer — spec §18.12.4 |

**MISS-024 fix — bounded/proceduralized cable-entanglement mitigation
(no new cutout; small features added to the existing rotating base print
job):**

| Parameter | Value | Unit | Confidence | Rationale |
|---|---|---|---|---|
| J1 (USB-C) radius/angle from bearing axis | 97.073mm / 123.44° | — | **DERIVED** (re-computed from source variables, not reused from the Reviewer's prose) | spec §18.13.1 |
| J4 (barrel jack) radius/angle from bearing axis | 97.073mm / 56.56° | — | **DERIVED** | Same method — mirror-symmetric to J1 about north, a pre-existing Rev 3 board-layout coincidence, not a new design choice — spec §18.13.1 |
| Turn-count limit before mandatory manual re-centering (`pinch_guard_turn_limit`) | 3 | full turns, one direction | **DECIDED**, mirrors REQ-113's own "several full turns" language | spec §18.13.3 |
| Minimum external service-loop length, each of J1/J4 (`cable_service_loop_min`) | 2.5 | m | **DECIDED**, sized against the 3-turn limit (exact requirement 2.383m) with 117mm/4.91% spare | spec §18.13.2/.3 |
| `rotation_index_pointer()` — visual turn-counting witness mark | new feature, fused to the rotating base's own north wall | — | **ASSUMPTION** (a convenience aid, not a precision index; no fixed external reference point is provided) | spec §18.13.4 |
| `cable_anchor_tab()` ×2 — zip-tie strain-relief anchor near J1 and near J4 | new feature, fused to the rotating base's own wall | — | **ASSUMPTION** (generic small-cable-tie hardware, no Evidence ID — mirrors this file's own C5 generic-fastener precedent) | spec §18.13.5 |
| Re-centering procedure | Human-procedural: operator manually rotates the platform back to the index-aligned reference orientation after `pinch_guard_turn_limit` turns, before continuing further same-direction rotation | — | **DECIDED** (procedural control, not new firmware/sensing — `firmware/**` untouched) | spec §18.13.3 |
| Coaxial-bore routing (C6) as the long-term fix instead | Considered, rejected this pass | — | **DECIDED** (rejected) | J1/J4 are fixed Rev 3 connector positions ≈81mm from the bore's own axis; routing a new wire from the bore to J1/J4 needs either PCB-level rework (out of Mechanical scope) or an unsourced slip-ring (no candidate part/Evidence ID exists) — flagged CONSIDER LATER, not delivered — spec §18.13.6 |
| REQ-012 "ideally continuous/unlimited" rotation aspiration | Not achieved by this fix | — | **DISCLOSED** (not fully closed) | This fix closes the bounded, "several full turns" case REQ-113 itself actually mandates; unlimited rotation remains contingent on a future slip-ring decision REQ-113 itself already defers — spec §18.13.7 |

**Mass-rollup note (extends, does not edit, C8's own table above):**
`pinch_guard`'s own mass (≈570.6g) plus `rotation_index_pointer()` +
`cable_anchor_tab()`×2 (≈1.1g combined, computed from the exact mesh
volume — negligible next to `pinch_guard`) add **≈571.6g** to C8's own
prior ≈601.8g total, giving an **updated total system mass of ≈1173.4g**.
This roughly **doubles the system mass again** — disclosed prominently
here, in the same spirit as C8's own "roughly double the human's own
estimate" disclosure, not buried. The dominant contributor by far is
`pinch_guard`'s own solid annulus volume (449,258mm³) — computed on
**exactly the same solid-CAD-volume-times-density basis** every other row
in C8 uses (i.e., this is not a print-time, infill-adjusted filament-mass
estimate; a real single-material FDM print of a purely-protective,
non-structural guard ring like this would very plausibly use partial
infill in practice, which this file has no established methodology for
modeling anywhere, so none is invented here either — flagged as a genuine
**CONSIDER LATER** opportunity if material/print-time economy becomes a
real constraint in a future revision, not attempted this pass, since
REQ-505's BOM ceiling is explicitly waived for this cycle and
`pinch_guard`'s sizing was driven entirely by the coverage-vs-footprint
trade-off (spec §18.12.3), not by mass).

**One-line, non-exhaustive observation on C3's tip-over analysis (flagged
for the Reviewer/Hardware Lead's own discretion, not re-derived this
pass — out of this pass's 2 assigned findings):** `pinch_guard` is
stationary, desk-resting, and coaxial with (adds zero net horizontal CG
offset relative to) the existing bearing axis. Adding its mass to
`m_total` while `m_rotating` and `r_rot` (C4's own tip-over formula
inputs) are unchanged can only **decrease** `d_offset` and thereby
**improve** — never worsen — the already-large (≈6.2×) static margin C4
computed. `pinch_guard` is **not**, however, a fastened structural
extension of `stand_plate` (C4's own 60.0mm stability radius still applies
unchanged) — it is a separate, unfastened, merely-adjacent part (§18.12.7),
so this is a favorable but informal observation, not a claim that the
tip-over stability radius itself has grown to 115mm. A full C3 re-derivation
including this new mass is left for whoever next revisits that section,
since it is not required to close either MISS-023 or MISS-024.

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

**New for Rev 4 (Part C addition):**
13. **Bearing mounting-hole count/spacing** (DS-BRG-007) — ASSUMPTION only,
    a generic lazy-susan-hardware-class convention (4 holes/plate, #6
    screws), not this specific SKU's own confirmed pattern (the manufacturer
    does not publish it). Verify against the physical part before
    finalizing bolt-hole positions for manufacture (C1/C2).
14. **Bearing mass** (≈130g) — ESTIMATE built from a chain of further
    sub-estimates (stamped-plate gauge ≈1.2mm, ball race 24×⌀6mm), not a
    manufacturer figure or a physical measurement; weak/wide (77–160g),
    non-citation-grade web corroboration only (C1).
15. **Rev 3 plastic-mass discrepancy** — this population's own analytic
    computation (≈207.9g) is materially higher than `bom/component-
    selection.md`'s own bounding-shell estimate (130–170g) for the same Rev
    3 enclosure. Largest contributor hand-verified to rule out a computation
    bug; judged an under-count in the bounding-shell proxy method, not an
    error in this file's own figure — flagged for the Hardware Lead/Reviewer
    to weigh, not silently reconciled (C3).
16. **New mounting-flange internal support-material requirement** — a
    genuine, confirmed manufacturability finding (not a tight-but-compliant
    case): the fused base+flange print has a ~56mm-diameter hidden internal
    overhang at the transition between the new flange's own bore and the
    pre-existing floor disc's solid underside, needing slicer-generated
    internal support (removable through the bore's own opening). See C2 and
    `bench-imu-01-dimensional-spec.md` §18 for the full analysis; three
    alternative fixes were considered and rejected there.
17. **Bearing-joint fastener load (torque/shear/pull-out)** — no calculation
    performed; the self-tapping-into-PETG choice (C5) is a first-cycle
    engineering judgment mirroring the lower-duty PCB-lid-tab precedent, not
    an independently load-tested conclusion for a joint that (unlike the
    lid tabs) carries the full rotating-assembly weight across the rotation
    duty cycle.
18. **Static tip-over margin standard** — the computed 6.2× static margin
    and ≈9.13N tip force (C4) are presented as computed figures only; no
    independently-cited numeric standard (e.g. a regulatory or industry bump-
    force spec) was found or applied to judge whether 6.2× is "enough" —
    this remains a qualitative judgment call for the Hardware Lead/Reviewer.
19. **Total system mass vs. the human's own working estimate** — this
    population's own computed total (≈601.8g) is roughly double the
    ≈280–320g figure carried in `requirements/requirements.md`/`bom/
    component-selection.md`. Disclosed prominently in C3; attributed to the
    higher analytic plastic-mass finding (item 15) and the new flange/
    bearing/stand-plate masses, not to a computation error.

**New for Rev 4.1 (Part C addition — MISS-023/MISS-024 mitigation, C9):**
20. **`pinch_guard` not fastened/keyed to `stand_plate`** — the two parts
    only touch (flush-adjacent at r=60mm), confirmed via direct boolean
    intersection to be non-overlapping and non-interfering, but nothing
    bonds or keys them together; the guard could in principle drift out of
    rotational/radial alignment over time or handling. Disclosed as a
    limitation, not an oversight (C9).
21. **11.4mm residual unguarded radial gap** (`pinch_guard_or`=115.0mm vs.
    `rotating_env_max_r`=126.424mm) — mitigated only by an operational
    keep-clear-zone warning (tightening REQ-205), not by further geometry
    this pass. Whether this residual-gap disposition is acceptable is a
    judgment call for the Hardware Lead/human, not resolved unilaterally
    here (C9).
22. **Turn-count re-centering is a human-procedural control, not a sensed
    or firmware-enforced one** — nothing measures or limits actual turn
    count; the 3-turn limit and re-centering procedure rely entirely on
    operator discipline. Consistent with this task's own scope fence (no
    firmware/control-loop work), but flagged so it is not mistaken for an
    automated safeguard (C9).
23. **Cable-tie/zip-tie size for `cable_anchor_tab()`'s hole** — a generic
    commodity-hardware assumption (3.0mm hole, no Evidence ID), not a
    datasheet-specified part, mirroring this file's own C5 generic-fastener
    precedent (C9).
24. **Coaxial-bore/slip-ring routing as the long-term REQ-113/REQ-012
    solution** — considered and explicitly rejected for this pass (would
    need either PCB-level rework, out of Mechanical scope, or an unsourced,
    unselected slip-ring component); flagged CONSIDER LATER, not delivered
    (C9).
25. **REQ-012's "ideally continuous/unlimited" rotation aspiration** — this
    pass's fix closes the bounded, "several full turns" case REQ-113 itself
    actually mandates, but explicitly does NOT achieve unlimited rotation;
    that remains contingent on a future slip-ring decision REQ-113 itself
    already treats as deferred (C9).
26. **Updated total system mass (≈1173.4g, up from ≈601.8g)** —
    `pinch_guard`'s own solid-volume mass (≈570.6g) dominates; computed on
    the same solid-CAD-volume-times-density basis as every other mass
    figure in this file (not a print-time, infill-adjusted filament-mass
    estimate — a real print of this purely-protective, non-structural part
    would very plausibly use partial infill in practice, reducing actual
    material/cost/print-time well below this figure, but this file has no
    established methodology for modeling that discount). Flagged as a
    CONSIDER LATER opportunity for a lighter/ribbed redesign if material
    economy becomes a real constraint in a future revision — not attempted
    this pass (C9).
27. **Mechanical Reviewer's 10-item self-check checklist has no explicit
    safety-hazard/REQ-407 assessment item** — a process observation, not a
    new mechanical fact: this is judged the root cause of why MISS-023/024
    were both absent from the original Rev 4 self-check. Flagged for the
    Hardware Lead's discretion (checklist ownership belongs to the
    Mechanical Reviewer's own agent definition, not this Mechanical Lead) —
    see `bench-imu-01-dimensional-spec.md` §18.15.

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

**Rev 4 note on the "motion/joints" deferral above**: Part C integrates a
**bought, off-the-shelf single-axis rotational bearing** (BC Precision
4LS-3) — not a custom-designed hinge, sliding mechanism, or multi-link
kinematic linkage. This is understood as the human's explicit, project-
specific authorization (`docs/architecture.md` §11's roadmap stage,
requirements/component-selection already approved per the Rev 4 task brief)
to bring this one specific "motion" capability into active scope for
Bench-IMU-01, not a unilateral decision by this Mechanical Lead to reopen
the generic deferral above. The generic deferral continues to apply as the
default for any *other* motion/joint need (e.g. a custom hinge or linkage)
unless a future project similarly authorizes it. Advanced statistical
tolerance stack-up analysis remains deferred and untouched by this
addition — Part C's fastener/fit dimensions use the same single, basic
fit-clearance allowance (`fit_clearance`=0.2mm/side) as the rest of the
`.scad` file, nothing more advanced.

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

---

**Rev 4 addendum to Handoff & change control (Part C addition only — the
above Rev 3 handoff text is unchanged)**: Part C was populated by the
Mechanical Lead from the human-approved `requirements/requirements.md`
(§1b/§9f/§9g) and `bom/component-selection.md` ("Free-Rotation Support
Mechanism") records, DS-BRG-001, and this session's own new DS-BRG-007
evidence record, then used to design the corresponding Rev 4 additions to
`hardware/mechanical/bench-imu-01-enclosure.scad` and
`hardware/mechanical/bench-imu-01-dimensional-spec.md` (§18) — see that
spec file's own §18 for the full CG/tip-over analysis, self-check, and open
items in dimensional-parameter form; this file (Part C) is the interface-
level summary of the same facts.

**Process note, flagged rather than actioned (mirrors the Rev 3 note
above)**: per `.github/agents/mechanical-lead.agent.md`'s explicit scope for
this task, ECO logging (`validation/change-log.md`) and traceability-matrix
updates (`requirements/traceability-matrix.md`) are the Hardware Lead's
responsibility after this handoff, not this Mechanical Lead's — neither file
has been touched this session. This is flagged here as a likely necessary
follow-up action, not silently skipped without note.

**This addendum's own assessment of what comes next**: this Mechanical
Lead's own self-check (see `bench-imu-01-dimensional-spec.md` §18's
self-check subsection) is **not** a substitute for independent review. Per
this Mechanical Lead's own governing agent file, a separate Mechanical
Reviewer pass is required next, regardless of how confident this population
is in its own numbers — several items above (the unpublished bolt pattern,
the bearing-mass estimate chain, the disclosed plastic-mass discrepancy, and
the internal-support-material manufacturability finding) are exactly the
kind of finding that pass exists to stress-test independently.
