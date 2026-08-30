# Electronics → Mechanical Interface

The physical/geometric contract the Electronics side hands to the Mechanical
Lead — the minimum field set needed for Phase 1
(`docs/architecture-evolution.md` §13), reusing the existing `Parameter |
Value | Unit | Source` table convention (`datasheets/README.md`,
`hardware/power-budget.md`) plus explicit `Confidence` and
`Assumption / Notes` columns, since not every mechanical fact is either a
confirmed number or a flat `UNKNOWN` the way most Electronics facts are.

**Status: populated for Bench-IMU-01** — this repository's first real,
end-to-end design cycle, and the actual benchmark run for the Mechanical
discipline (`docs/architecture-evolution.md` §24: "Can this AI engineering
system create a believable, buildable enclosure from real electronics
information?"). Populated by the Mechanical Lead directly from the Circuit
Engineer's `hardware/schematic/bench-imu-01-design.md` (Rev 2,
Hardware-Reviewer-passed, human ACCEPTED-RISK sign-off recorded) — **not**
from a KiCad project: `kicad-list_projects` was verified empty this session
(no KiCad project exists yet for this repository), so every field below is
extracted from the Circuit Engineer's own documented facts (mainly §10
"Board geometry facts for the ... Mechanical Lead handoff", plus §11 pin
table, §12 net list, §13 parts list), per the "Who fills this in" section
below, rather than from the KiCad read-only tool surface. Below, `design.md`
is shorthand for `hardware/schematic/bench-imu-01-design.md`.

Every row's `Confidence` label is this Mechanical Lead's own independent
judgment against *this file's* legend definitions below — not a verbatim
copy of the Circuit Engineer's own wording. In two places this produces a
different call than the Circuit Engineer's own document: (1) the LQFP-32
and SOT-23-5 package heights, which the Circuit Engineer's own §10 marks
`CONFIRMED` against a generic JEDEC package-*family* standard rather than
the exact part's own mechanical drawing (its own text flags this caveat and
explicitly invites the Mechanical Lead to make its own call — see the
caveat after the Component Height Clearance table); (2) the board's
tallest-component conclusion itself, once components the Circuit Engineer's
own analysis didn't size (J2/J3 headers) are accounted for — see the same
caveat.

## Who fills this in

Per `.github/agents/mechanical-lead.agent.md`, the **Mechanical Lead** is
responsible for populating this file — extracting from an existing KiCad
project via the same read-only tools already documented in
`docs/architecture.md` §5.2 (`get_project_structure`,
`extract_project_netlist`, `analyze_bom`,
`generate_pcb_thumbnail`/`generate_project_thumbnail`), or from
Circuit-Engineer-/human-supplied facts if no KiCad project exists yet. This
requires no change to the Circuit Engineer's own files or process.

## Confidence / Assumption legend

Use exactly one of these per row's `Confidence` column:

| Label | Meaning |
|---|---|
| `CONFIRMED` | From an actual KiCad project / manufacturer spec / measured value. `Source` cites the Evidence ID or the specific tool output used. |
| `ASSUMPTION` | A stated design assumption made in the absence of confirmed data. `Assumption / Notes` must say why. |
| `ESTIMATE` | A reasonable approximation (e.g. "typical PCB thickness 1.6 mm"), explicitly flagged as such. |
| `UNKNOWN` | Not yet determined. Must **not** be used as if confirmed (`docs/architecture.md` §6.1) — escalate before the Mechanical Lead relies on it for a load-bearing dimension (e.g. a mounting hole position). |

## Board Geometry

| Parameter | Value | Unit | Source | Confidence | Assumption / Notes |
|---|---|---|---|---|---|
| PCB Length | 60 | mm | `design.md` §10 ("PCB outline/size") + REQ-302 | ESTIMATE | The Circuit Engineer's own §10 estimate is a range, "~55×35mm up to the full 60×40mm REQ-302 target," with an explicit recommendation to design to "the full allowed envelope... for routing/assembly margin." This Mechanical Lead adopts the top of that range as the fixed working figure — REQ-302 is a "Should" ceiling, not a floor, so using it fully is compliant, and it maximizes downstream margin for mounting-hole inset, connector-cutout clearance, and wall thickness in the enclosure-design phase. Not CONFIRMED by an actual KiCad board outline — none exists yet (`kicad-list_projects` verified empty this session). |
| PCB Width | 40 | mm | same as above | ESTIMATE | Same reasoning as PCB Length — top of the Circuit Engineer's stated ~35–40mm range. |
| PCB Thickness | 1.6 | mm | Mechanical Lead's own engineering default — not stated anywhere in `design.md` (confirmed absent by direct search of the whole document) | ASSUMPTION | The near-universal standard PCB thickness for a design with no stated special requirement (rigidity, flex, unusual layer count, or heavy connector leverage). REQ-301 fixes layer count (2) but not thickness. 1.6mm is the default essentially every low-volume PCB fabricator ships absent a special request; revisit only if a future finding shows the USB-C receptacle's mounting tabs or the mounting-hole standoffs need a non-standard thickness for mechanical strength (no such need is evident yet). |
| Board Outline | Rectangular, 60mm × 40mm bounding box; no cutouts, notches, or castellated edges | — | Mechanical Lead's own inference from `design.md`'s silence (no non-rectangular shape, notch, or cutout is mentioned anywhere in the document — checked §0–§18 directly) + REQ-301's flat single-2-layer-PCB framing | ASSUMPTION | Not a literal Circuit-Engineer-confirmed statement — `design.md` §10's table never states board shape explicitly; this is this Mechanical Lead's own reasonable default for a first, simple 2-layer bench board with no stated mechanical keep-out or routing constraint requiring anything other than a plain rectangle. |

## Mounting

**Coordinate convention** (Mechanical Lead's own addition, needed to make
X/Y usable — not specified anywhere in `design.md`): origin `(0, 0)` at the
board's bottom-left corner, viewed from the top/component side; `X` runs
0→60mm along the PCB Length edge, `Y` runs 0→40mm along the PCB Width edge.
All X/Y values in this file use this convention.

| Hole ID | X | Y | Diameter | Unit | Source | Confidence | Notes |
|---|---|---|---|---|---|---|---|
| MH-1 | 3.5 | 3.5 | 2.8 | mm | `design.md` §10 ("Mounting holes": "4×, near each corner, inset ~3–4mm... M2.5, hole ⌀≈2.7–2.8mm") + ISO 273 metric clearance-hole convention (M2.5: close fit 2.7mm / normal fit 2.9mm) | ESTIMATE | Bottom-left corner. The Circuit Engineer gave only qualitative placement ("near each corner, inset ~3–4mm") — the X/Y here are this Mechanical Lead's own specific proposal: a symmetric 3.5mm inset from both edges (midpoint of the Circuit Engineer's stated 3–4mm range). Diameter 2.8mm is chosen at the upper end of the Circuit Engineer's stated 2.7–2.8mm range (also inside ISO 273's M2.5 close-to-normal-fit band) for slightly easier assembly clearance. This is a proposed coordinate for enclosure-design purposes, not a Circuit-Engineer-specified or KiCad-confirmed position — expect it to move once a real board layout exists. |
| MH-2 | 56.5 | 3.5 | 2.8 | mm | same as MH-1 | ESTIMATE | Bottom-right corner (60 − 3.5 = 56.5). Same reasoning as MH-1. |
| MH-3 | 56.5 | 36.5 | 2.8 | mm | same as MH-1 | ESTIMATE | Top-right corner (40 − 3.5 = 36.5). Same reasoning as MH-1. |
| MH-4 | 3.5 | 36.5 | 2.8 | mm | same as MH-1 | ESTIMATE | Top-left corner. Same reasoning as MH-1. Checked against this Mechanical Lead's own proposed connector/LED placements below (Connectors, Switches & LEDs table) for interference — clear by ≥9mm in every case. |

## Component Height Clearance

| Parameter | Value | Unit | Source | Confidence | Notes |
|---|---|---|---|---|---|
| Max component height (top side) | 8.5 | mm | Mechanical Lead's own estimate — standard 2.54mm-pitch straight pin header, assumed for J2/J3 (~6.0mm mating pin length + ~2.5mm insulator height, consistent across generic 2.54mm-pitch header manufacturer specs) | ESTIMATE | **Supersedes `design.md` §10's own "tallest component = USB-C receptacle (J1), ≈3.2mm" conclusion.** See the caveat paragraph immediately below this table for the full reasoning; short version: the Circuit Engineer's §10 analysis only sizes the components it had a concrete reason to size (LQFP-32, SOT-23-5, and the USB-C-vs-Micro-USB-B connector trade-off) — it never gives a physical header type/height for J2/J3, and a conventional straight 2.54mm pin header (the same convention as the NUCLEO-style debug header `design.md` §4.4 explicitly compares J3 to) would be taller than the USB-C receptacle. Recommend the Hardware Lead/Circuit Engineer confirm the actual J2/J3 header hardware (straight vs. right-angle, standard vs. low-profile) since it is now this enclosure's height-budget-driving fact, not the connector-type choice `design.md` itself flagged. |
| Max component height (bottom side) | 0 | mm | `design.md` §13 (parts list) | ASSUMPTION | No bottom-side components are identified anywhere in `design.md` (checked directly — no "bottom side"/"both sides"/"single-sided" statement exists anywhere in the document). This is this Mechanical Lead's own inference from that silence, not a literal Circuit-Engineer confirmation of single-sided assembly: a conventional single-sided (top-only) assembly is the standard, lowest-cost choice for a 2-layer board this size/part-count with no stated density pressure requiring bottom-side placement. This is a load-bearing assumption for how thin the enclosure's base half can be — if a future KiCad layout places anything on the bottom (e.g. for routing/density), this row must be revisited. |

**Caveat on this table's two most consequential judgment calls** (both this
Mechanical Lead's own, one diverging from and one adding to `design.md`
§10's analysis):

1. **Package-height confidence downgrade (LQFP-32, SOT-23-5).** `design.md`
   §10 marks the LQFP-32 (U1, ≈1.4mm) and SOT-23-5 (U3, ≈1.1–1.25mm) package
   heights **CONFIRMED**, citing DS-MCU-048 / DS-PWR-046 (JEDEC MS-026/
   MO-178 package-*family* outline standards) — and its own text flags the
   caveat itself: *"confirmed against the JEDEC package-family outline
   standard, not against [the part's] own literal mechanical drawing
   page... a distinction worth preserving for the Mechanical Lead's own
   rigor."* Taking up that explicit invitation: in **this file's** stricter
   4-label scheme, a family-standard-based height is not the same as a
   part-specific, manufacturer-drawing-confirmed height (`CONFIRMED`'s own
   definition above requires "an actual KiCad project / manufacturer spec /
   measured value" for *this* part). This Mechanical Lead therefore records
   both as **ESTIMATE**, not CONFIRMED, in this file specifically — this
   downgrade changes no Value cell above (neither is the tallest component
   either way), only how much weight the next phase should put on them. The
   USB-C receptacle height (≈3.2mm, DS-CONN-003) keeps `design.md`'s own
   **ESTIMATE** label unchanged — independently reviewed and agreed: it is
   explicitly a representative-part figure for an MPN not yet locked in,
   squarely an ESTIMATE by this file's own definition, never a CONFIRMED one.
2. **Header/switch/LED physical dimensions are absent from `design.md`, not
   just imprecise.** §13's parts list gives J2/J3 as "4-pin header"
   (function/pinout only), SW1 as "momentary pushbutton, N.O." (electrical
   function only), and D1 as "generic indicator LED" (Vf assumed only) —
   none carry a stated package, height, or pitch anywhere in the document
   (confirmed by direct search). This Mechanical Lead's own estimates, not
   used in the table above but flagged here for completeness: SW1 ≈5mm
   (typical 6mm through-hole tactile-switch body height) and D1 ≈1mm
   (assumed small SMD LED package, for consistency with the rest of this
   design's all-SMD IC selection — though a through-hole 5mm LED, which
   would add ≈8–9mm and become the new tallest feature on the board,
   remains a real, undecided alternative). Neither changes this table's
   Max-height conclusion (both stay under the 8.5mm header estimate above),
   but both are genuine open items, the same in kind as the header-height
   finding — see "Open items" near the end of this file.

## Connectors, Switches & LEDs (cutouts)

| Item | Type | X | Y | Orientation | Cutout needed? | Source | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|
| J1 | USB-C receptacle, power-only (no D+/D− routed, REQ-105) | 0 | 20 | Horizontal edge-mount; plug axis along X, opening faces −X (outward through the board's left short edge) | Y | `design.md` §3.1/§10/§12 (type/function); X/Y/orientation = Mechanical Lead's own proposal | ESTIMATE | Type/function is Circuit-Engineer-confirmed; `design.md` only says "one short edge" (2 candidates: X=0 or X=60) — X=0, centered at Y=20 (board's Y midpoint), is this Mechanical Lead's own specific placement choice, made for a clean, symmetric layout, not a Circuit-Engineer-specified coordinate. Cutout: side-wall opening sized for a USB-C receptacle + cable clearance; exact cutout dimensions deferred to the enclosure-design phase. J1's own MPN is not yet formally selected (`design.md` §10/§13) — height estimate rests on one representative part (DS-CONN-003). |
| J2 | 4-pin header: TX/RX/GND/3V3 (REQ-106, UART) | 16 | 40 | Vertical through-hole, pins point +Z; single row of 4 runs along X, parallel to the top edge | Y | `design.md` §6/§10/§13 (type/function); X/Y/orientation + physical header assumption = Mechanical Lead's own | ESTIMATE | `design.md` only says "along one long edge" (2 candidates: Y=0 or Y=40), together with J3 — Y=40 (top long edge), spaced from J3/SW1/the corner mounting holes, is this Mechanical Lead's own specific placement. Physical header type (straight 2.54mm pin header, ~8.5mm tall) is also this Mechanical Lead's own assumption — see the Component Height Clearance caveat above; `design.md` never states a header type. Cutout: a lid opening (or an omitted-lid region) above the header for cable/probe access. |
| J3 | 4-pin header: VDD/SWCLK/GND/SWDIO (REQ-107, SWD debug) | 30 | 40 | Same as J2 | Y | `design.md` §4.4/§10/§13 (type/function); X/Y/orientation = Mechanical Lead's own | ESTIMATE | Same reasoning as J2 — placed 14mm from J2 and 14mm from SW1 for footprint/cutout clearance, and clear of both corner mounting holes by ≥13mm. |
| SW1 | Momentary pushbutton, N.O. (REQ-004, manual reset) | 44 | 40 | Vertical actuation, cap points +Z (toward the lid) | Y | `design.md` §4.3/§13 (type/function only); X/Y/orientation/package = Mechanical Lead's own — `design.md` gives **no edge guidance at all** for SW1 | ASSUMPTION | `design.md` never states which edge/region SW1 is on (unlike J1/J2/J3, which at least got qualitative edge guidance) — placement here is entirely this Mechanical Lead's own choice (grouped near the debug headers, a common practical dev-board convention: reset-while-debugging access). Assumes a standard top-actuated through-hole tactile switch (~5mm tall; no package stated by Circuit Engineer, see Component Height Clearance caveat). Cutout call: direct finger access (a wall/lid opening sized to the button) rather than a recessed poke-hole — simpler for a bench/dev board, Phase-1 appropriate. |
| D1 | Generic indicator/status LED, Vf≈2.0V assumed (REQ-003) | 10 | 30 | Top-emitting; assumed small SMD package, light emitted in +Z (toward the lid) | Y | `design.md` §7/§13 (type/function only); X/Y/orientation/package = Mechanical Lead's own — `design.md` gives **no edge/position guidance at all** for D1 | ASSUMPTION | Same gap as SW1 — no Circuit-Engineer placement guidance at all. Placed near the USB-C/power edge, a common convention (status LED visible near the power-input side), clear of MH-4 by ≈9mm and of J1's own footprint by ≈14mm. Package assumed SMD for consistency with the rest of this design's SMD-only IC selection; a through-hole 5mm LED is a real, undecided alternative (see Component Height Clearance caveat). Cutout call: a small (~3mm) through-hole in the lid directly above D1, no engineered light-pipe — simplest Phase-1 approach; a molded light-pipe/clear window is a possible later refinement, not required now. |

## Mass

| Parameter | Value | Unit | Source | Confidence | Notes |
|---|---|---|---|---|---|
| Approximate PCB + components mass | 8–10 (≈9 typical) | g | Mechanical Lead's own calculation from Board Geometry table above + `design.md` §13 parts list + generic FR4 density reference (~1.85 g/cm³) | ESTIMATE | Bare-board estimate: 60mm × 40mm × 1.6mm × 1.85 g/cm³ ≈ 7.1g (FR4 substrate + copper, standard density figure — no per-part datasheet mass cited by `design.md`). Populated-board component-mass adder ≈1.8–2.0g, dominated by J1's USB-C metal shell (~0.5g typical for this connector class), J2+J3's two 4-pin headers (~0.3g each ≈0.6g combined), and SW1's tactile-switch body (~0.3g); the MCU (U1), IMU, LDO (U3), and passives are each individually small (well under 0.1g apiece) and contribute the small remainder. Total ≈8.9–9.1g, rounded to an 8–10g range. This is a bench-estimate for a small, low-part-count board, not a summed manufacturer-datasheet mass table — reasonable for Phase 1 / REQ-502's paper-design framing, but would need real per-part masses (from actual selected MPNs' datasheets) if the design ever needs a precise mass budget (e.g. for a handheld or mass-sensitive application — not this project). |

## Open items (not blocking — flagged for the next phase, none escalated)

None of these rise to this agent's own escalation bar ("a required field
cannot be confirmed and is **not safe** to leave as ASSUMPTION/ESTIMATE" —
`.github/agents/mechanical-lead.agent.md`): given REQ-502's explicit framing
of this cycle as a paper/document design exercise with no physical
fabrication happening, a well-reasoned ESTIMATE for each of these is the
correct and expected Phase-1 artifact, not a blocker. Recorded here purely
so the next phase (enclosure design) and any future KiCad-project creation
know exactly which figures are this Mechanical Lead's own placeholder and
should be revisited first once real layout data exists:

1. **J2/J3 physical header hardware is unconfirmed.** The 8.5mm top-side
   height budget (Component Height Clearance table) rests entirely on an
   assumed standard 2.54mm straight pin header — `design.md` never states
   header type. If the real header turns out to be low-profile, right-angle,
   or shrouded, the enclosure's Z-height budget changes materially. Owner:
   Hardware Lead/Circuit Engineer to confirm before enclosure Z-height is
   frozen.
2. **SW1 and D1 packages are unconfirmed.** Neither has a stated physical
   package anywhere in `design.md` — heights here (≈5mm, ≈1mm respectively)
   are this Mechanical Lead's own reasonable assumptions, and a through-hole
   5mm LED for D1 remains a real, undecided alternative that would exceed
   the current 8.5mm max-height figure. Owner: Circuit Engineer, once D1/SW1
   MPNs are selected.
3. **J1's exact MPN is not yet locked** (`design.md` §10/§13) — the ≈3.2mm
   height and physical footprint used anywhere in this file rest on one
   representative part (GCT USB4125, DS-CONN-003), not a final selection.
   Does not currently drive the enclosure's height budget (superseded by
   the header-height estimate above), but would matter again for the J1
   cutout's exact width/depth in the next phase. Owner: Circuit Engineer.
4. **Bottom-side = 0 components is an inference from silence, not an explicit
   Circuit-Engineer confirmation.** Revisit if a future KiCad layout places
   anything on the bottom copper layer.

## Deferred fields (not in Phase 1 — add only if a real project needs one)

Per `docs/architecture-evolution.md` §13, explicitly deferred until the
benchmark shows they're actually needed: thermal zones, antenna keep-out,
STEP/neutral 3D model reference, center of mass, battery wiring requirements,
complex keep-out zones, detailed cable-exit geometry.

## Handoff & change control

- **Produced by**: Mechanical Lead (see "Who fills this in" above).
- **Consumed by**: Mechanical Lead itself
  (`.github/skills/enclosure-design/SKILL.md`), and the Mechanical Reviewer
  for independent cross-checking (`.github/skills/mechanical-review/SKILL.md`).
- If a value here changes after Mechanical Design has started (e.g. the
  Circuit Engineer moves a connector), log it in `validation/change-log.md`
  (ECO) and check `validation/change-impact-matrix.md`'s existing
  "Mechanical" impact row — the Mechanical Design phase
  (`docs/workflow.md` Phase 9) may need to be revisited.
- Governed by `.github/instructions/mechanical-design.instructions.md`.
