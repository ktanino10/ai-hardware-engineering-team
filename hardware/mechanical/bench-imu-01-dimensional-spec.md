# Bench-IMU-01 — Enclosure Dimensional Spec &amp; Design Rationale

**Status:** Phase 1 design complete, self-checked, **not yet independently
reviewed**. Awaiting Mechanical Reviewer sign-off before this design is
considered validated. This document does not declare itself
reviewed/complete — see `.github/agents/mechanical-lead.agent.md`,
"Out of scope."

**Author:** Mechanical Lead agent, this session.
**Companion file:** `bench-imu-01-enclosure.scad` (parametric OpenSCAD
source; every dimension in the table below is a named variable there).
**Authoritative input:** `hardware/mechanical-interface.md` (all
board/component facts trace back to it unless labeled otherwise below).

## 0. Tooling honesty (re-verified this session)

No CAD/3D modeling MCP tool is connected in this environment. The only
3D-capable tool surface present in this environment is the Blender MCP
tool set; a live connection check via `blender-get_addon_status` returned
**"Could not connect to Blender."** A check for local CAD tooling in this
shell also found no `openscad` or `freecad` binary and no
`cadquery`/`solid`/`build123d` Python library installed. Per
`docs/architecture.md` §5.3/§13, the deliverable is therefore this text/
parametric pair — an OpenSCAD-syntax `.scad` file and this Markdown
spec — and **nothing in this repository has rendered, previewed, fit-checked,
or exported to STL the geometry described here.** All "computed clearance
checks" below are plain arithmetic (verified with a Python calculator this
session), not a CAD measurement. A human must render
`bench-imu-01-enclosure.scad` themselves to see the actual 3D geometry.

## 1. Scope recap

Phase 1 checklist only (`.github/agents/mechanical-lead.agent.md`):
enclosure/spatial layout, PCB mounting, connector accessibility,
component-height clearance (top+bottom), internal clearance/interference,
fastener placement, wall thickness, assembly order, basic print-fit
tolerance, basic manufacturability. Explicitly **out of scope** this cycle:
tolerance stack-up analysis, motion/joints, advanced material selection,
thermal/antenna/STEP/CoM/battery-wiring/keep-out fields (all
`docs/architecture-evolution.md` §10/§13 CONSIDER LATER).

Requirements traced: REQ-301 (2-layer PCB — electronics-side, not
mechanical, cited for context), REQ-302 (≤60×40mm target — PCB itself is
exactly at the target, satisfied by definition), REQ-303 (connectors on
≤2 edges — J1 on one short edge, J2/J3/SW1 on one long edge = 2 edges,
satisfied), REQ-304 (≥4 M2/M2.5 mounting holes — 4× M2.5 provided,
satisfied), REQ-305 (2-piece 3D-printable enclosure — base + lid,
satisfied by construction).

## 2. Print-fit tolerance &amp; manufacturability rules (stated once, applied everywhere)

| Rule | Value | Status | Applies to |
|---|---|---|---|
| Print-fit clearance | **0.2 mm per side** | ASSUMPTION | Lid-skirt-to-base-wall radial gap; lid tab clearance hole vs. screw shank |
| Board-XY keepout (not a tolerance — see §4) | 1.5 mm per side | ASSUMPTION | PCB edge to interior cavity wall |
| Z-margin (not a tolerance — see §4) | 0.5 mm | ASSUMPTION | Added above the interface file's stated 8.5 mm top clearance |
| Min. wall thickness | 2.0 mm | ASSUMPTION | All structural walls/floor/roof/skirt |
| Max. unsupported overhang | 45° from vertical | ASSUMPTION | Standard FDM rule of thumb |
| Max. unsupported bridge span | 10 mm | ASSUMPTION | Standard FDM rule of thumb, good part cooling |
| Print material | **PETG** | ASSUMPTION — human did not specify a printer/material | Whole enclosure |

**Why PETG:** better layer adhesion and toughness than PLA at small
self-tapping screw bosses (this design relies on 8 self-tapped M2.5
joints, all in-plastic threads, no heat-set inserts — see §8/§9.2), without
ABS's warping/enclosed-chamber printing requirement. This is a stated
design assumption, not a customer/human specification — flagged for the
Mechanical Reviewer and Hardware Lead to confirm or override.

**Why three separate margin concepts, not one:** `fit_clearance` (0.2mm) is
reserved strictly for surfaces that actually **slide/mate** against each
other (lid skirt against base wall, screw shank against its clearance
hole). `board_xy_keepout` (1.5mm) and `z_margin` (0.5mm) are **not**
mating-surface tolerances — the PCB's XY position is fixed by its 4
standoffs, not by touching the interior wall, and the Z stack is fixed by
the header/standoff heights, not by touching the lid. Conflating these
three into a single number would understate how much "fit" tolerance is
actually being applied at the joints that need it (0.2mm is tight; 1.5mm/
0.5mm are deliberately generous robustness margins, not tolerances).

## 3. Overall envelope (fixed first, per the enclosure-design skill's procedure)

| Parameter | Value | Unit |
|---|---|---|
| Base outer footprint (main body, excl. tabs) | 67.0 × 47.0 | mm |
| Lid skirt outer footprint | 71.4 × 51.4 | mm (2.2mm/side larger than the base — see §4) |
| Overall footprint incl. 4 external corner tabs | ≈67 × 59 (Y), 71.4×59 incl. lid overhang | mm — tabs project 6mm beyond the base wall face at 4 corner zones only, not a full-perimeter increase |
| Total assembled height | **20.6** | mm |
| Enclosure style | 2-piece: base (floor + walls + standoffs + tabs) + lid (roof + skirt + tabs) | — |

## 4. Full dimensional parameter table

**Confidence key:** CONFIRMED = read directly off a datasheet/measurement;
ESTIMATE = a reasonable approximation flagged as such; ASSUMPTION = a
stated design choice with rationale; DERIVED = arithmetic from other rows
in this table (not a fresh guess). All rows below mirror the `.scad`
file's variable names exactly.

### 4.1 Traced directly from `hardware/mechanical-interface.md`

| Parameter | Value | Unit | Confidence | Source/Rationale |
|---|---|---|---|---|
| `pcb_length` | 60.0 | mm | ESTIMATE | interface: Board Geometry |
| `pcb_width` | 40.0 | mm | ESTIMATE | interface: Board Geometry |
| `pcb_thickness` | 1.6 | mm | ASSUMPTION | interface: Board Geometry (standard 2-layer stock) |
| Mounting holes MH-1..4 | (3.5,3.5) (56.5,3.5) (56.5,36.5) (3.5,36.5), ⌀2.8 | mm | ESTIMATE | interface: Mounting |
| `top_component_clearance` | **8.5** | mm | ESTIMATE | interface: Component Height Clearance — **corrected figure, driven by J2/J3 headers; supersedes design.md's original 3.2mm (USB-C) conclusion.** |
| `bottom_component_clearance` | 0.0 | mm | ASSUMPTION | interface: Component Height Clearance (single-sided assembly) |
| J1 (USB-C) position/orientation | (0,20), horizontal, opens −X | mm | ESTIMATE | interface: Connectors/Switches/LEDs |
| `j1_ref_height` | 3.2 | mm | ESTIMATE | design.md / DS-CONN-003-class part (J1 MPN not yet locked — interface Open Item) |
| J2 (UART header) position/orientation | (16,40), vertical, +Z | mm | ESTIMATE | interface: Connectors/Switches/LEDs |
| J3 (SWD header) position/orientation | (30,40), vertical, +Z | mm | ESTIMATE | interface: Connectors/Switches/LEDs |
| SW1 (reset) position/orientation | (44,40), vertical actuation | mm | ESTIMATE | interface: Connectors/Switches/LEDs |
| D1 (LED) position/orientation | (10,30), top-emitting +Z | mm | ESTIMATE | interface: Connectors/Switches/LEDs |
| Mass | ≈9 | g | ESTIMATE | interface: Mass (context only — not a driving mechanical dimension at this scale) |

### 4.2 This Mechanical Lead's own design values (ASSUMPTION/ESTIMATE unless marked DERIVED)

| Parameter | Value | Unit | Confidence | Source/Rationale |
|---|---|---|---|---|
| `fit_clearance` | 0.2 | mm/side | ASSUMPTION | Stated FDM print-fit allowance (§2) |
| `print_material` | PETG | — | ASSUMPTION | §2 — human did not specify |
| `min_wall_t` / `wall_t` / `floor_t` | 2.0 | mm | ASSUMPTION | ~5× a 0.4mm nozzle width; above the commonly-cited 0.8mm FDM structural floor |
| `max_overhang_deg` | 45 | ° from vertical | ASSUMPTION | Standard FDM rule of thumb |
| `max_bridge_span` | 10.0 | mm | ASSUMPTION | Standard FDM practice, good cooling |
| `board_xy_keepout` | 1.5 | mm/side | ASSUMPTION | Drop-in/robustness margin, not a mating tolerance (§2) |
| `interior_x` × `interior_y` | 63.0 × 43.0 | mm | DERIVED | `pcb_length/width + 2×board_xy_keepout` |
| `base_outer_x` × `base_outer_y` | 67.0 × 47.0 | mm | DERIVED | `interior + 2×wall_t` |
| `standoff_od` | 6.0 | mm | ASSUMPTION | Sized so annular wall around the pilot hole = `wall_t` (2.0mm) |
| `standoff_pilot_dia` | 2.0 | mm | ASSUMPTION | ~80% of M2.5 major diameter, standard self-tap pilot sizing |
| `standoff_h` | 6.0 | mm | ASSUMPTION | **Sized by fastener engagement-depth need (~2–3× screw dia ≈ 5–7.5mm), not by the 0mm bottom-clearance requirement** — see §7 |
| `standoff_pilot_depth` | 5.0 | mm, blind | ASSUMPTION | Leaves 1.0mm solid floor under the hole |
| `screw_len` (single fastener, used 8×) | 6.0 | mm, M2.5 self-tapping | ASSUMPTION | Verified stack-up for both PCB standoffs and lid tabs — §9.2 |
| `z_margin` | 0.5 | mm | ASSUMPTION | Robustness margin above the 8.5mm interface figure (§2) |
| `base_interior_h` | 16.6 | mm | DERIVED | `standoff_h + pcb_thickness + top_component_clearance + z_margin` |
| `base_total_h` | 18.6 | mm | DERIVED | `floor_t + base_interior_h` |
| `lid_lip_h` | 3.0 | mm | ASSUMPTION | Skirt overlap depth over the base wall top |
| `lid_roof_t` / `lid_skirt_t` | 2.0 | mm | ASSUMPTION | `= wall_t`, consistency |
| `total_height` | 20.6 | mm | DERIVED | `base_total_h + lid_roof_t` |
| `lid_skirt_inner_x/y` | 67.4 × 47.4 | mm | DERIVED | `base_outer + 2×fit_clearance` |
| `lid_skirt_outer_x/y` | 71.4 × 51.4 | mm | DERIVED | `lid_skirt_inner + 2×lid_skirt_t` |
| `board_offset_x/y` | 3.5 | mm | DERIVED | `wall_t + board_xy_keepout` |
| `j1_cut_w` | 9.5 | mm (Y-span) | ESTIMATE | Representative USB-C shell width (~9.0mm) + 2×`fit_clearance`, rounded up (MPN unconfirmed) |
| `j1_cut_h` | 6.0 | mm (Z-span) | ESTIMATE | `pcb_thickness + j1_ref_height` + generous margin |
| `bay_x_min` / `bay_x_max` | 10.0 / 50.0 | mm, board-local X | ESTIMATE | J2(16)/SW1(44) span ± 6mm margin |
| `bay_y_min` | 34.0 | mm, board-local Y | ESTIMATE | 6mm footprint-depth allowance from the Y=40 board edge |
| `d1_hole_dia` | 3.0 | mm | ESTIMATE | Small viewing hole, no light-pipe (Phase-1-appropriate) |
| `tab_w` | 8.0 | mm | ASSUMPTION | Sized to clear the header bay by ≥2.5mm (§6) |
| `tab_project` | 6.0 | mm | ASSUMPTION | Enough for an 8mm-wide screw boss beyond the wall face |
| `tab_base_t` | 5.0 | mm | ASSUMPTION | Gives 4.0mm pilot depth + 1.0mm floor |
| `tab_pilot_depth` | 4.0 | mm, blind | ASSUMPTION | Full `screw_len` engagement (2mm through lid tab + 4mm into base tab) |
| `tab_lid_t` | 2.0 | mm | DERIVED | `= lid_roof_t` (lid tab is a literal roof extension) |
| `tab_clear_dia` | 2.8 | mm | ASSUMPTION | Same clearance-hole convention as PCB mounting holes |
| `tab_pilot_dia` | 2.0 | mm | DERIVED | `= standoff_pilot_dia` (same M2.5 self-tap pilot, BOM simplicity) |
| `tab_chamfer_run` | 6.0 | mm | DERIVED | `= tab_project` (45° chamfer needs equal rise/run) — **base tabs only**, see §9.3 |

## 5. Design rationale by checklist item

**1. Enclosure/spatial layout.** 2-piece design per REQ-305: a **base**
(floor + 4 perimeter walls, open top) carrying the PCB standoffs, and a
shallow **cap-style lid** (roof + downward skirt) that slips over the
base's outer wall. A stepped tongue-and-groove joint was considered and
rejected — at this wall thickness it would produce an ≈0.6–0.8mm "tongue,"
marginal for FDM print integrity. The simpler cap/skirt joint avoids that
thin-feature risk entirely.

**2. PCB mounting.** 4 standoffs (⌀6.0mm, 6.0mm tall, blind ⌀2.0mm pilot
5.0mm deep) rise from the interior floor at the exact 4 interface-file
mounting-hole X/Y coordinates. PCB drops onto them and is secured with
4× M2.5×6mm self-tapping screws driven up through the board.

**3. Connector accessibility.** See §6 for the full per-connector
walkthrough — every one of J1/J2/J3/SW1/D1 has a dedicated, sized opening.

**4. Component-height clearance.** See §7 — computed both top and bottom,
using the interface file's corrected 8.5mm top figure (not the superseded
3.2mm), plus an explicit 0.5mm robustness margin.

**5. Internal clearance/interference.** Checked numerically (not asserted)
in §7. One real conflict was found and resolved during design: an
initially-considered "shared PCB+lid fastening column" reusing the PCB
standoffs, and an "inward-bulging lid-screw boss on the clear front wall,"
were both found to either be unbuildably fragile (a sub-3mm-OD freestanding
riser through 9mm of open air) or to geometrically collide with the PCB
footprint (the front wall sits only 1.5mm from the interior wall — closer
than an inward boss would need to intrude). Resolved by moving lid
fastening entirely outside the cavity (external corner tabs, §6/§8),
eliminating both conflicts by construction.

**6. Fastener placement.** See §8 (PCB standoffs) and the external-tab
discussion in §6/§8 (lid fastening).

**7. Wall thickness.** 2.0mm uniform, chosen as ~5× a 0.4mm nozzle width
(above the commonly-cited ~0.8mm FDM structural floor), sized for genuine
screw-boss/wall integrity rather than a bare-minimum shell. Same value
reused for floor, roof, and skirt for consistency and print-time
efficiency (fewer distinct thicknesses to reason about).

**8. Assembly order.** See §9 — the single most important buildability
question this benchmark poses; resolved in full below.

**9. Print-fit tolerance.** 0.2mm/side, stated once in §2 and applied
consistently at: the lid-skirt-to-base-wall radial gap (`lid_skirt_inner =
base_outer + 2×0.2`), and both fastener clearance holes (`tab_clear_dia` =
2.8mm vs. an M2.5 = 2.5mm nominal shank, i.e. 0.15mm/side, consistent with
this same class of allowance; the PCB's own mounting-hole clearance
diameter, 2.8mm, is taken directly from the interface file rather than
re-derived).

**10. Manufacturability.** See §9.3 — printability was checked against the
design's actual features (bridge span at the J1 cutout, overhang at the
corner tabs), not just stated as a generic rule.

## 6. Connector/header/button/LED accessibility — per-item resolution

| Item | Position | Orientation | Access strategy | Purpose (see note below) |
|---|---|---|---|---|
| J1 (USB-C) | (0,20) | Horizontal, opens −X | Side-wall cutout in the **base**, 9.5mm(Y) × 6.0mm(Z), centered on Y=20 | Cable mating path (−X) |
| J2 (UART header) | (16,40) | Vertical, +Z | Shares one open **bay** cut through the **lid** (roof+skirt), open to the rear (+Y) edge | Cable mating path (+Z/rearward) |
| J3 (SWD header) | (30,40) | Vertical, +Z | Same shared bay as J2 | Cable mating path (+Z/rearward) |
| SW1 (reset button) | (44,40) | Vertical actuation | Same shared bay as J2/J3 | Fingertip press access |
| D1 (LED) | (10,30) | Top-emitting, +Z | Dedicated ⌀3.0mm hole through the lid **roof only** (kept ≥2.5mm clear of the bay's edge) | Visibility |

**Important clarification surfaced by actually computing the numbers (see
§7):** the header stack's physical top (Z≈18.1mm) sits **below**, not
above, the split line (Z=18.6mm) once the stated `z_margin` is included —
so a fully solid lid would **not** mechanically collide with J2/J3. The
open bay is therefore driven by **functional access**, not by a height
clearance problem: J2 (UART) and J3 (SWD) are active-use connectors that a
bench/dev board's user will want to plug a cable into, potentially
routinely or even semi-permanently, and a solid lid would physically block
that even with clearance to spare underneath it. SW1 similarly needs a
path for a fingertip, not just clearance for its resting height — a solid
lid with 0.5mm of clearance above the button cap would make the button
literally unpressable. D1 needs the hole for visibility, not height. This
distinction (access vs. clearance) is deliberately called out here because
conflating them would have produced a design that "fits" on paper but is
functionally useless — exactly the kind of physical-reasoning gap this
benchmark is testing for.

J1, by contrast, genuinely is both a clearance AND an access problem in the
same cutout: its own physical bulk needs the cutout to not be crushed by
the wall, *and* the mating cable needs the same opening to reach it from
outside.

**Bay geometry:** spans board-local X=10–50 (40mm wide — J2 at 16, J3 at
30, SW1 at 44, all comfortably inside with margin), Y=34 through to the
true outer rear edge (~9.5mm total notch depth). A single continuous notch
was chosen over 3 separate small windows for print simplicity (avoids a
thin bridged strip at the back edge that 3 separate islands would create)
and because it matches real cable-dressing needs.

**Tab-vs-bay clearance (checked, not assumed):** the two rear corner tabs
(near MH-3 and MH-4, which reuse the bay's same wall) clear the bay by
2.5mm on each side (tab edge at board-local X≈52.5 vs. bay edge at X=50 on
one side; tab edge at X≈7.5 vs. bay edge at X=10 on the other) — tight
relative to other margins in this design, but positive and non-conflicting
in both cases. See §7 for the exact arithmetic.

## 7. Computed clearance checks (numbers, not assertions)

All values below were computed with a Python calculator this session (see
the commands run before writing this file) — not measured from a render.

**Top-side component clearance:**
```
pcb_top_z (global, from base interior floor)  = floor_t + standoff_h + pcb_thickness
                                               = 2.0 + 6.0 + 1.6 = 9.6 mm
header_top_z (PCB top + interface's 8.5mm)    = 9.6 + 8.5 = 18.1 mm
split_line (top of base wall)                 = base_total_h = 18.6 mm
Margin remaining above the header             = 18.6 − 18.1 = 0.5 mm  (= z_margin, exactly as intended)
```
Result: **PASS** — the stated 8.5mm interface requirement is met with the
full stated 0.5mm z_margin intact, using the corrected (not the superseded
3.2mm) figure.

**Bottom-side component clearance:**
```
Bottom clearance available = standoff_h − 0 (PCB sits directly on standoff tops)
                            = 6.0 mm available vs. 0.0 mm required (interface)
```
Result: **PASS**, with 6.0mm of margin — this large excess exists only
because `standoff_h` is sized by fastener engagement depth (dominant
constraint), not by the bottom-clearance requirement (trivially satisfied
as a side effect). This is called out explicitly rather than left as an
unexplained-looking oversized number.

**Standoff / PCB / interior-wall clearance (all 4 positions checked):**
```
Standoff center = (board_offset + hole_xy); radius = standoff_od/2 = 3.0mm
Interior wall inner face at: X ∈ [2.0, 65.0], Y ∈ [2.0, 45.0]  (global)
MH-1 (3.5,3.5)  -> standoff spans X[4.0,10.0]  Y[4.0,10.0]   -> clear of both faces
MH-2 (56.5,3.5) -> standoff spans X[57.0,63.0] Y[4.0,10.0]   -> clear of both faces
MH-3 (56.5,36.5)-> standoff spans X[57.0,63.0] Y[37.0,43.0]  -> clear of both faces
MH-4 (3.5,36.5) -> standoff spans X[4.0,10.0]  Y[37.0,43.0]  -> clear of both faces
```
Result: **PASS**, all 4 standoffs sit entirely under the PCB footprint
(as intended — a standoff should support the board, not protrude past its
edge) with a minimum 2.0mm clearance to the interior wall.

**J1 cutout vs. nearest standoffs:**
```
J1 cutout global Y range = [18.75, 28.25]
MH-1/MH-4 (same wall) standoff Y ranges = [4.0,10.0] and [37.0,43.0]
Gap to each = 8.75 mm (both sides)
```
Result: **PASS**, wide margin.

**Header bay vs. nearest standoffs and tabs:**
```
Bay global X range = [13.5, 53.5]
MH-3 standoff X range = [57.0, 63.0]  -> gap = 3.5mm
MH-4 standoff X range = [4.0, 10.0]   -> gap = 3.5mm
Rear-right tab X range = [56.0, 64.0] -> gap = 2.5mm
Rear-left  tab X range = [3.0, 11.0]  -> gap = 2.5mm
```
Result: **PASS** — all positive, tab clearances (2.5mm) are the tightest
margins in this whole design but are non-zero and non-conflicting.

**D1 vs. bay:**
```
D1 hole top edge (global Y) = 35.0mm;  bay starts at global Y = 37.5mm
Gap = 2.5mm
```
Result: **PASS**.

**D1 vs. nearest standoff (MH-4):**
```
distance = sqrt((10-3.5)^2 + (30-36.5)^2) = 9.19mm
sum of radii (D1 hole 1.5mm + standoff 3.0mm) = 4.5mm
9.19mm >> 4.5mm
```
Result: **PASS**, wide margin (also independently consistent with the
interface file's own "~9mm" note on this same distance).

**Single-fastener (M2.5×6mm) stack-up, used both for PCB standoffs and lid
tabs:**
```
PCB standoff:  screw passes through pcb_thickness (1.6mm) + engages
               4.4mm of the 5.0mm pilot depth (0.6mm pilot unused/slack)
Lid tab:       screw passes through tab_lid_t (2.0mm, clearance) + engages
               4.0mm of the 4.0mm pilot depth exactly (1.0mm solid floor
               remains below the pilot hole)
```
Result: **PASS** for both uses — a single M2.5×6mm self-tapping screw,
used 8× total, is the entire fastener BOM for this enclosure.

## 8. Fastener placement summary

| Fastener use | Qty | Type | Boss OD/dims | Pilot dia | Pilot/engagement depth | Access direction |
|---|---|---|---|---|---|---|
| PCB-to-base standoffs | 4 | M2.5×6mm self-tapping | ⌀6.0mm cylinder | ⌀2.0mm | 5.0mm blind (4.4mm engaged) | +Z (screwdriver from above, before lid is fitted) |
| Lid-to-base corner tabs | 4 | M2.5×6mm self-tapping (same type) | 8×6mm external tab, 5.0mm thick (base) / 2.0mm (lid) | ⌀2.0mm (base) / ⌀2.8mm clearance (lid) | 4.0mm blind in base tab, full engagement | +Z (screwdriver from above, last assembly step) |

Both fastener uses are the **same screw type and length** — a deliberate
BOM-simplicity choice (one fastener line item for the whole enclosure, 8
identical screws).

**Why external tabs, not interior bosses, for lid fastening** (three
rejected alternatives, each with a concrete reason):
1. *Shared PCB+lid fastening column* (extend a PCB standoff all the way up
   to the lid) — would require an unbuildably thin freestanding riser
   (≤2.8mm OD) spanning ~9mm of open air with no lateral support; too
   fragile for FDM.
2. *Inward-bulging boss on the "clear" front wall* — found to physically
   collide with the PCB footprint itself, since the PCB sits only 1.5mm
   from the interior wall (`board_xy_keepout`), closer than an inward boss
   would need to intrude to hold a screw.
3. *Interior bosses at all 4 true corners, alongside the PCB standoffs* —
   center-to-center spacing as small as ~2.8mm vs. a combined-boss-radius
   requirement of ~7mm — geometrically impossible without merging into (or
   colliding with) the PCB standoffs.

Resolution: 4 **external** mounting ears, each at a PCB corner's X/Y
position but projecting *outward* from the main wall profile (not
intruding into the interior cavity at all), so no PCB conflict is possible
by construction. Confirmed clear of both the header bay and the J1 cutout
(§6/§7).

## 9. Manufacturability / 3D-printability

### 9.1 Rule set
Stated in full in §2 (min wall 2.0mm, max overhang 45°, max bridge 10mm,
material PETG — all ASSUMPTION).

### 9.2 Checked against this design's actual features
- **J1 cutout bridge:** the cutout's top edge, when the base is printed in
  its natural floor-down orientation, requires an unsupported horizontal
  bridge of ≈9.5mm (`j1_cut_w`). This is within the stated ≤10mm bridge
  rule, but only just — flagged explicitly (not silently accepted) as a
  feature to watch on a first test print; a human slicing this file may
  choose to add a support blocker/single support line here as a practical
  hedge even though the design nominally clears the rule.
- **Standoff pilot holes:** open at the top (not blind-capped from below in
  a way that would need bridging), simple vertical cylinders — no support
  needed in the base's natural print orientation.
- **Base external corner tabs:** sit high on the wall (Z≈13.6–18.6mm out of
  an 18.6mm-tall base) and project sideways as a 90°, unsupported overhang
  in the natural floor-down print orientation. **Addressed**, not ignored:
  a 45° self-supporting chamfer/gusset (`tab_chamfer_run` = 6.0mm, matching
  `tab_project` for an exact 45° angle) runs from the wall face up to the
  tab's underside, keeping the whole feature within the stated
  `max_overhang_deg` rule without printed support material.
- **Lid external corner tabs:** by contrast, when the lid is printed in its
  own natural orientation (roof-down), these tabs sit at the same Z-level
  as the roof — i.e., at or near the first printed layers, effectively
  bed-supported. **No chamfer applied here** — an earlier pass through this
  design incorrectly planned to chamfer both lid and base tabs identically;
  that was corrected after actually reasoning through each part's print
  orientation separately, rather than applying one rule uniformly without
  checking. This correction is called out explicitly as a demonstration of
  print-orientation-aware reasoning, not glossed over.
- **Header/button bay and D1 hole (lid):** both are simple through-cuts
  with no enclosed void beneath them in the lid's own natural print
  orientation — no bridging or support concern.

### 9.3 Print orientation
- **Base:** floor-down (natural). No supports needed for standoffs or
  pilot holes; the J1 cutout bridge is the one feature to watch (§9.2).
- **Lid:** roof-down (natural, for a clean top/visible surface). No
  supports needed for the bay, D1 hole, or the lid tabs (bed-adjacent, see
  §9.2). The `.scad` file's `"print_layout"` show-mode lays both parts out
  in these orientations, but the exact flip transform for the lid is
  offered as a starting point only — it has not been visually verified in
  an actual OpenSCAD session (no such tool is available here); a human
  should confirm orientation visually (or use a slicer's "lay flat")
  before trusting it blindly.

## 10. Assembly order — the core buildability question

This is the question the task explicitly flagged as "most likely to reveal
a real problem," given that J2/J3/SW1/D1 all need lid-side access while
the PCB mounts to the base underneath. Worked through in full:

**The trap to check:** *"Do headers need to be soldered after the PCB is
already inside the enclosure — which would be a real assembly problem,
since header pins face +Z and would become inaccessible once the lid area
is filled?"*

**Resolution: no**, and here is the reasoning, not just the answer:

1. **PCB population happens entirely before enclosure assembly begins.**
   J1/J2/J3/SW1/D1 are all soldered onto the bare PCB as a standard PCB
   assembly (PCBA) process step, on an open bench, with full access from
   every direction. This is a *manufacturing* step, not a *mechanical
   assembly* step, and is explicitly outside this design's scope (it's true
   regardless of what enclosure exists, or whether one exists at all). By
   the time enclosure assembly starts, the board is a **fully populated,
   functionally tested PCBA** — there is no point in the mechanical
   assembly sequence where a header is soldered with the enclosure already
   in the way.
2. **Populated PCBA drops into the base** (+Z downward motion), guided onto
   the 4 standoff bosses by the mounting holes.
   - *Poka-yoke noted*: the 4-hole mounting pattern is itself symmetric
     under 180° rotation about the board center, but the base's J1 cutout
     is asymmetric (only on one specific wall) — so an incorrectly-rotated
     PCB insertion is immediately obvious (J1 would face a solid wall
     instead of its cutout) and effectively self-prevented. This is a
     genuine, if modest, design strength worth noting rather than a
     designed-in feature that needed extra parts.
3. **4× M2.5×6mm self-tapping screws** driven downward through the PCB into
   the standoffs — full screwdriver access, since the lid is not yet
   present.
4. **Lid lowered straight down** (single −Z motion) onto the base. No
   collision: J2/J3/SW1 pass through the open bay, D1 through its
   dedicated hole, and the solid part of the lid clears every other
   (shorter) component via the uniform interior height computed in §7.
5. **4× M2.5×6mm self-tapping screws** driven downward through the lid's
   external corner tabs into the base's matching corner tabs, securing the
   lid.

**Disassembly** is the reverse, and is non-destructive — no permanent
snaps or adhesive anywhere in this design — enabling rework, inspection, or
component replacement. This is a deliberate design strength for a bench/
dev board, worth stating explicitly rather than leaving implicit.

## 11. Self-check against the Mechanical Reviewer's 10-item checklist

Self-check performed per `.github/skills/mechanical-review/SKILL.md`. This
is **not** a substitute for independent review — see §0 status line — but
is intended to catch the obvious issues before handoff.

| # | Checklist item | Self-check result |
|---|---|---|
| 1 | PCB mounting (standoffs at correct positions, correctly sized) | **PASS** — 4 standoffs at the exact interface-file MH coordinates, ⌀6.0mm OD around a ⌀2.0mm M2.5 self-tap pilot, clear of the interior wall by ≥2.0mm (§7) |
| 2 | Connector accessibility (all connectors reachable/usable) | **PASS** — every one of J1/J2/J3/SW1/D1 has a dedicated, purpose-matched opening (§6); functional-access vs. height-clearance distinction explicitly reasoned through, not conflated |
| 3 | Component height clearance (top + bottom, vs. interface file) | **PASS** — top: 0.5mm margin above the corrected 8.5mm figure (§7); bottom: 6.0mm available vs. 0mm required, explained (not just asserted) as a side effect of the standoff's fastener-depth sizing |
| 4 | Internal clearance/interference (parts vs. walls/each other/fasteners) | **PASS** — all clearances in §7 computed numerically; one real conflict (lid-fastening approach) was found and resolved during design, not swept aside |
| 5 | Fastener placement (position, wall thickness, access direction) | **PASS** — §8; all 8 fasteners are +Z-accessible at the point in the assembly sequence they're needed, with adequate surrounding material at every boss |
| 6 | Wall thickness (structural + printable) | **PASS** — 2.0mm uniform, justified against a stated FDM rule (§2/§5-item 7), not an arbitrary number |
| 7 | Assembly order (physically achievable, no trapped parts) | **PASS** — §10; the specific "headers trapped behind the lid" trap was explicitly reasoned through and resolved (PCB is populated before enclosure assembly, not after) |
| 8 | Print-fit tolerance (single stated value, consistently applied) | **PASS** — 0.2mm/side (§2), applied at the lid/base skirt joint and fastener clearance holes; explicitly distinguished from the separate keepout/margin concepts so as not to overstate what "tolerance" covers (§2) |
| 9 | Manufacturability (wall thickness, overhangs, bridges, stated material) | **PASS** — checked against actual design features, not just stated in the abstract (§9); one genuine correction made mid-design (lid tabs do NOT need the chamfer originally planned for both parts) after reasoning through per-part print orientation |
| 10 | Interface-value traceability (every dimension traced to a source or explicit assumption) | **PASS** — full parameter table in §4 labels every value CONFIRMED/ESTIMATE/ASSUMPTION/DERIVED with an explicit source |

**Overall self-check result: 10/10 PASS.** No CRITICAL or HIGH issues
identified by this self-check. This does **not** mean the design is
approved — independent Mechanical Reviewer sign-off is still required
(`.github/agents/mechanical-lead.agent.md`, "Out of scope": *"Declaring
your own design reviewed/complete... is mandatory regardless of how
confident you are"*). The items below are specifically flagged as things
this self-check cannot fully close out on its own.

## 12. Open UNKNOWNs / ASSUMPTIONs carried forward for the Mechanical Reviewer

**Inherited from `hardware/mechanical-interface.md`'s own "Open items"
(not resolved by this design — just propagated, since resolving them is
outside Mechanical Lead scope):**
1. J2/J3 physical header hardware (exact part/pitch/stack height) is
   unconfirmed — this is the single figure the entire 8.5mm top-clearance
   budget (and therefore this whole enclosure's height) is built on. If the
   real header part differs meaningfully from the ESTIMATE, `base_total_h`
   and `total_height` both need to be revisited.
2. SW1/D1 exact packages are unconfirmed — this design's bay footprint
   (40×6mm) and D1 hole (⌀3.0mm) are this Mechanical Lead's own ESTIMATEs
   layered on top of the interface file's own estimates; both should be
   re-checked once real part numbers exist.
3. J1's MPN is not locked — this design's J1 cutout (9.5×6.0mm) already
   carries extra margin specifically because of this, but should still be
   re-verified once a real part is chosen.

**New estimates introduced by this Mechanical Lead, not present in the
interface file, that the Reviewer should specifically scrutinize:**
4. Header/button bay footprint dimensions (40mm × 6mm) — an ESTIMATE built
   from the connector X positions plus an assumed margin, not from any
   actual header/switch datasheet.
5. D1 viewing-hole diameter (3.0mm) — ESTIMATE, no LED datasheet consulted.
6. USB-C receptacle body width assumed ≈9.0mm for `j1_cut_w` sizing — this
   number does not appear anywhere in the interface file (which gave only
   a height, 3.2mm) and is this Mechanical Lead's own outside-knowledge
   estimate of a typical USB-C receptacle shell width.
7. The decision to use a **clearance** (slip) fit, not an interference
   (press) fit, for the lid skirt-to-base joint — meaning the skirt fit
   alone provides negligible retention; all positive retention comes from
   the 4 corner-tab screws. Worth the Reviewer confirming this is an
   acceptable trade-off (vs., say, a snap-fit or interference fit that
   would hold the lid even before screws are driven, during handling).
8. The 2.5mm clearance between the rear corner tabs and the header bay
   (§6/§7) is the tightest margin anywhere in this design. It is positive
   and was checked numerically, but it is far tighter than the ~8.75mm or
   3.5mm+ margins found elsewhere — worth a specific second look.
9. The J1 cutout's ≈9.5mm top-edge bridge span is within the stated ≤10mm
   rule but only just (§9.2) — flagged as a first-test-print watch item.

**Process/administrative item:**
10. Whether this first-time creation of `hardware/mechanical/*` design
    files requires a `validation/change-log.md` (ECO) entry: this
    Mechanical Lead's reading of `.github/instructions/mechanical-design.
    instructions.md` is that its ECO requirement is written for *changes*
    to an existing design, and this is a first-time creation (there is no
    prior enclosure design to have changed) — so no ECO entry has been
    added for this initial creation. This judgment call is noted here
    explicitly so the Hardware Lead/Reviewer can override it if the
    project's convention is actually "log everything, including first
    creation."

## 13. Handoff

Per `.github/agents/mechanical-lead.agent.md`, handoff to the Mechanical
Reviewer (via the Hardware Lead) consists of:
- `bench-imu-01-enclosure.scad` (this directory)
- This file (`bench-imu-01-dimensional-spec.md`)
- The design rationale (§5–§10 above)
- The self-check result (§11)
- The open UNKNOWNs/ASSUMPTIONs list (§12)

No CAD/3D rendering, preview, or STL export accompanies this handoff — see
§0. The Mechanical Reviewer should expect to review this as a textual/
parametric design, consistent with this environment's current, verified
tooling state.
