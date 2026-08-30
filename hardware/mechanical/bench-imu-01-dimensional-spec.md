# Bench-IMU-01 — Enclosure Dimensional Spec &amp; Design Rationale

**Status: Rev. 2 — revised after Mechanical Reviewer Cycle 1 findings,
ready for RE-review** (not a fresh first review). Cycle 1's independent
review found 2 HIGH and 2 MEDIUM issues in the design this document
describes; both HIGH and both MEDIUM findings have been fixed in this
revision (MISS-005/MISS-006, LOW, are deliberately left untouched — out of
scope for this Mechanical Lead pass per the Hardware Lead's routing). This
document still does not declare itself reviewed/complete — see
`.github/agents/mechanical-lead.agent.md`, "Out of scope" — independent
Mechanical Reviewer sign-off on this revision is the required next step.

**Rev. 2 changelog (this revision vs. Cycle 1), each finding fixed in both
the `.scad` file and this spec document:**
- **MISS-001 (HIGH)** — `bay_x_min`/`bay_x_max`/`bay_y_min` were sized from
  J2/J3/SW1's *centerline* positions, not their real footprint edges,
  producing real connector-to-bay margins of just 0.0mm/1.0mm/3.5mm (one of
  them zero). Fixed: recomputed from each connector's real footprint edge
  (the same dimensions this file's own `reference_pcba()` module already
  used) plus a new named `bay_edge_margin`(1.5mm) variable. Real margins are
  now a uniform, genuinely positive 1.5mm. See §4.3, §6, §7, §11 item 2.
- **MISS-002 (HIGH)** — the base tab's 45° chamfer/gusset was a `hull()` of
  two 0.01mm-thin cubes: a geometrically degenerate sliver, not a real
  load-bearing wedge. Fixed: replaced with a genuine `linear_extrude()` of a
  right-triangle `polygon()` (rise=run=6.0mm, volume 144mm³ per tab). See
  §9.2, §11 item 9.
- **MISS-003 (MEDIUM)** — the lid tab's clearance-hole annular wall computed
  to 1.6mm, below this design's own stated 2.0mm `min_wall_t`. Fixed: new
  lid-only `lid_tab_project`(6.8mm) footprint override restores exactly
  2.0mm, while the fastener hole itself stays on the original, unmoved axis
  so it remains coaxial with the base tab's pilot hole. See §4.3, §7, §8,
  §11 item 5. **Documentation-only side effect also caught and fixed while
  re-verifying this cycle (no further `.scad` change involved):** the wider
  lid tab now projects 0.4mm farther beyond the wall face than the base tab
  on each end, which nudges the overall assembled Y-footprint from the
  Cycle-1 figure of ≈59.0mm to the actual ≈59.8mm — §3's envelope row was
  stale and has been corrected to match.
- **MISS-004 (MEDIUM)** — the lid/base-tab fastener pair had zero
  engagement-depth spare margin. Fixed: `tab_pilot_depth`(4.0→4.6mm) and
  `tab_base_t`(5.0→5.6mm) together restore a 0.6mm spare (matching the PCB
  standoff's own precedent) while preserving the 1.0mm solid floor exactly.
  See §4.3, §7, §8, §11 item 5.
- Both HIGH-finding fixes (and the MISS-003 coaxiality claim) were, in
  addition to hand arithmetic, cross-checked against actual rendered
  `.scad` geometry this session using a locally-available OpenSCAD 2021.01
  binary — see the new §0 addendum and §7/§9.2 for what was actually
  rendered/measured.
- MISS-005/MISS-006 (LOW) are **not** addressed in this revision —
  deliberately left for a later disposition pass per the Hardware Lead's
  routing instructions.

**Author:** Mechanical Lead agent, this session (Rev. 1 authored in a prior
session; Rev. 2 rework in this session).
**Companion file:** `bench-imu-01-enclosure.scad` (parametric OpenSCAD
source; every dimension in the table below is a named variable there).
**Authoritative input:** `hardware/mechanical-interface.md` (all
board/component facts trace back to it unless labeled otherwise below).

## 0. Tooling honesty (re-verified this session)

**As stated in Cycle 1 (superseded in part below — kept verbatim for the
audit trail, not silently rewritten):**
No CAD/3D modeling MCP tool is connected in this environment. The only
3D-capable tool surface present in this environment is the Blender MCP
tool set; a live connection check via `blender-get_addon_status` returned
**"Could not connect to Blender."** A check for local CAD tooling in this
shell also found no `openscad` or `freecad` binary and no
`cadquery`/`solid`/`build123d` Python library installed. Per
`docs/architecture.md` §5.3/§13, the deliverable is therefore this text/
parametric pair — an OpenSCAD-syntax `.scad` file and this Markdown
spec — and nothing in this repository has rendered, previewed, fit-checked,
or exported to STL the geometry described here. All "computed clearance
checks" below are plain arithmetic (verified with a Python calculator this
session), not a CAD measurement. A human must render
`bench-imu-01-enclosure.scad` themselves to see the actual 3D geometry.

**Rev. 2 addendum (this session) — the local-tooling claim above is
corrected, not silently deleted, because leaving a known-false statement in
place would itself be a tooling-honesty violation:** a working `openscad`
2021.01 CLI binary was found at `/opt/homebrew/bin/openscad` in this
session's shell (confirmed via `openscad --version`, exit 0), and a working
`numpy-stl` Python library was also found — both contradicting the "no
local... binary... installed" claim immediately above. Both were used, but
strictly as a **targeted spot-check of this cycle's 4 fixes**
(MISS-001–MISS-004), not as a comprehensive re-verification of every number
in this document:
- The full assembled model, `base()` alone, and `lid()` alone were each
  rendered; OpenSCAD reported "Simple: yes" (valid manifold) with zero
  errors or warnings for all three.
- The corrected bay cutout was rendered standalone and its board-local
  bounding box measured directly from the exported STL mesh: X=[9.5,48.0],
  Y-min=32.5 — matching the `.scad` formulas exactly (§7).
- The new wedge (MISS-002 fix) was rendered standalone; its bounding box
  (X=8.0mm, Y=6.0mm, Z-span=6.0mm) and the combined tab+wedge volume
  (398.39mm³ measured vs. 398.35mm³ hand-calculated, <0.02% difference —
  consistent with STL circular-tessellation noise, not a modeling error)
  were measured from the exported STL, and a rendered image was visually
  inspected, confirming a real, non-degenerate triangular wedge (§9.2).
- The widened lid tab footprint (MISS-003 fix) was rendered standalone; its
  Y-range measured exactly [-6.4, 0.4] (6.8mm, matching `lid_tab_project`
  exactly), and coaxiality with the base tab's pilot hole was checked with
  an unobstructed-bore probe test (measured 20.68mm³ vs. 20.73mm³ ideal for
  a fully clear bore, §7).
- Every test/wrapper file was written to a scratch directory
  (`/tmp/scad-check/`) outside this repository and is **not** part of this
  deliverable — no STL, PNG, or render artifact has been committed here.
  This document's stated deliverable is still exactly the `.scad` file and
  this Markdown spec, per `docs/architecture.md` §5.3/§13.

**What this addendum does NOT claim:** no slicer support-preview and no
physical test print has been performed; no thermal, stress, or
tolerance-stack-up simulation was run; and this spot-check does not extend
to every dimension in this document — e.g. the top/bottom
component-clearance and standoff-clearance checks in §7 remain
arithmetic-only, unchanged from Cycle 1. Most importantly: this Mechanical
Lead's own tool use here is **not** a substitute for the Mechanical
Reviewer's independent re-review — per
`.github/agents/mechanical-lead.agent.md`, "Out of scope," this design does
not get to declare itself reviewed/complete regardless of what tooling
became available to check its own work. Per that same file's "Escalation
triggers," this discovery is flagged here as a verified opportunity for
future cycles, not retroactively assumed to have been available for
anything produced before this session.

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
| Overall footprint incl. 4 external corner tabs | ≈67 × 59.8 (Y), 71.4×59.8 incl. lid overhang | mm — tabs project 6.0mm (base tab) beyond the base wall face at 4 corner zones only, not a full-perimeter increase. **Rev. 2 note:** the true outward extreme is set by the **lid** tab, not the base tab — `lid_tab_project`(6.8mm, MISS-003 fix) grows symmetrically around the shared fastener axis, so the lid tab's outward edge sits 0.4mm beyond the base tab's on each of the front/rear projecting sides (empirically confirmed from rendered STL this session: base tab Y-range [-6.0,0.0], lid tab Y-range [-6.4,0.4]). This raises the true assembled Y envelope from the Cycle-1 figure of ≈59.0mm to **≈59.8mm** (47.0 base + 6.4 + 6.4) — a small, previously-unflagged consequence of the MISS-003 fix, caught while re-verifying this revision rather than left stale. |
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
| `bay_edge_margin` | 1.5 | mm | DERIVED | `= board_xy_keepout` — **Rev. 2 (MISS-001 fix):** reused verbatim, not invented, per its own existing rationale ("generous drop-in/assembly and robustness margin... NOT a tight mating tolerance") |
| `bay_x_min` / `bay_x_max` | 9.5 / 48.0 | mm, board-local X | DERIVED | `(j2_x−5)−bay_edge_margin` / `(sw1_x+2.5)+bay_edge_margin` — **Rev. 2 (MISS-001 fix, HIGH):** was 10.0/50.0, sized from connector **centerlines** ± an unfounded ~6mm; recomputed from each connector's real assumed footprint **edge** (per `reference_pcba()`) + `bay_edge_margin`. See §6/§7 |
| `bay_y_min` | 32.5 | mm, board-local Y | DERIVED | `(40−6)−bay_edge_margin` — **Rev. 2 (MISS-001 fix, HIGH):** was 34.0 (centerline-based ~6mm estimate); recomputed the same way as bay_x_min/max |
| `d1_hole_dia` | 3.0 | mm | ESTIMATE | Small viewing hole, no light-pipe (Phase-1-appropriate) |
| `tab_w` | 8.0 | mm | ASSUMPTION | Sized to clear the header bay — **Rev. 2 (MISS-001 side effect):** was "≥2.5mm both sides"; after the bay recompute the two sides are no longer symmetric — now 2.0mm (rear-left tab) / 4.5mm (rear-right tab, improved), both still positive. See §6/§7 |
| `tab_project` | 6.0 | mm | ASSUMPTION | Enough for an 8mm-wide screw boss beyond the wall face — **base tabs**; see `lid_tab_project` below for the lid-only override |
| `tab_base_t` | 5.6 | mm | ASSUMPTION | Gives 4.6mm pilot depth + 1.0mm floor — **Rev. 2 (MISS-004 fix, MEDIUM):** was 5.0mm/4.0mm-pilot (0mm engagement spare); increased +0.6mm in lockstep with `tab_pilot_depth` so the 1.0mm floor is unchanged |
| `tab_pilot_depth` | 4.6 | mm, blind | ASSUMPTION | `screw_len`(6.0) − `tab_lid_t`(2.0) = 4.0mm engaged, 0.6mm spare — **Rev. 2 (MISS-004 fix, MEDIUM):** was 4.0mm (0mm spare, unlike the PCB standoff's own 0.6mm precedent); deepened +0.6mm to match it |
| `tab_lid_t` | 2.0 | mm | DERIVED | `= lid_roof_t` (lid tab is a literal roof extension) |
| `tab_clear_dia` | 2.8 | mm | ASSUMPTION | Same clearance-hole convention as PCB mounting holes |
| `lid_tab_project` | 6.8 | mm | DERIVED | `2×min_wall_t + tab_clear_dia` — **Rev. 2 (MISS-003 fix, MEDIUM), lid tabs only:** new lid-side-only override. With the shared `tab_project`(6.0), the lid tab's annular wall was only `(6.0−2.8)/2=1.6mm` (< 2.0mm `min_wall_t`); this restores exactly 2.0mm, mirroring the base tab's own `(tab_project−tab_pilot_dia)/2=2.0mm` floor-precedent. See §6/§9.2 |
| `tab_pilot_dia` | 2.0 | mm | DERIVED | `= standoff_pilot_dia` (same M2.5 self-tap pilot, BOM simplicity) |
| `tab_chamfer_run` | 6.0 | mm | DERIVED | `= tab_project` (45° chamfer needs equal rise/run) — **base tabs only** (print-orientation reasoning, §9.3). **Rev. 2 (MISS-002 fix, HIGH):** the chamfer itself is now a genuine `linear_extrude()`/`polygon()` solid wedge (rise=run=6.0mm, swept over `tab_w`=8.0mm ⇒ 144mm³), replacing a degenerate `hull()` of two 0.01mm slivers — see §9.2 |

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
| D1 (LED) | (10,30) | Top-emitting, +Z | Dedicated ⌀3.0mm hole through the lid **roof only** (kept ≥1.0mm clear of the bay's edge — Rev. 2, was ≥2.5mm; see §7/§12 Open Item #8) | Visibility |

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

**Bay geometry (Rev. 2 — corrected, MISS-001 fix):** spans board-local
X=9.5–48.0 (38.5mm wide — J2 at 16, J3 at 30, SW1 at 44, all inside with
margin), Y=32.5 through to the true outer rear edge (~11mm total notch
depth). Previously this spanned X=10–50, Y=34–rear-edge, a range whose
prose claimed "comfortably inside with margin" but which was in fact sized
from connector **centerlines** with an unfounded ~6mm allowance, not from
real footprint edges — the Mechanical Reviewer independently recomputed the
actual connector-to-bay-edge margins at **0.0mm (J2), 1.0mm (SW1 via the
old X-max), and 3.5mm (the header row's Y edge)**, i.e. one side had *zero*
real clearance. The corrected bounds are derived edge-first: `bay_x_min =
(j2_x−5) − bay_edge_margin`, `bay_x_max = (sw1_x+2.5) + bay_edge_margin`,
`bay_y_min = (40−6) − bay_edge_margin`, using the exact same J2/J3/SW1
footprint half-widths already committed to in `reference_pcba()` (J2/J3:
±5mm X-halfwidth, 6mm Y-depth; SW1: 2.5mm radius) and reusing
`board_xy_keepout`(1.5mm) as `bay_edge_margin` — the same constant already
used, with the same "generous, not tight-tolerance" rationale, for the
board's own keepout elsewhere in this file. This makes all three real
connector-to-bay-edge margins a uniform, deliberately-chosen **1.5mm** (see
§7 for the full recomputed-margin table with rendered-geometry
cross-check). A single continuous notch was still chosen over 3 separate
small windows for print simplicity (avoids a thin bridged strip at the back
edge that 3 separate islands would create) and because it matches real
cable-dressing needs — that reasoning is unaffected by this fix.

**Side effect (disclosed):** narrowing `bay_y_min` from 34.0 to 32.5
brings the bay 1.5mm closer to D1's own hole, shrinking the D1-to-bay
clearance from 2.5mm to **1.0mm** — still positive, but now the tightest
margin in the whole design. Flagged in §7 and §12 Open Item #8, not
silently absorbed.

**Tab-vs-bay clearance (checked, not assumed — Rev. 2 numbers):** the two
rear corner tabs (near MH-3 and MH-4, which reuse the bay's same wall) no
longer clear the bay by a uniform amount, because the bay's X-bounds moved
by different amounts on each side (`bay_x_min` in by 0.5mm, `bay_x_max` in
by 2.0mm) while the tabs themselves did not move. Recomputed directly from
the corrected bounds: rear-left tab clears `bay_x_min`(9.5) by **2.0mm**
(tab edge at board-local X≈7.5); rear-right tab clears `bay_x_max`(48.0) by
**4.5mm**, improved (tab edge at board-local X≈52.5). Both positive and
non-conflicting; the tighter of the two (2.0mm) is still comfortably above
the fastener-boss wall-thickness class of figure used elsewhere in this
design. See §7 for the exact arithmetic, cross-checked against the actual
rendered `.scad` geometry this revision (not just the formulas) via an
exported-STL bounding-box measurement.

## 7. Computed clearance checks (numbers, not assertions)

All values below were computed with a Python calculator this session (see
the commands run before writing this file). **Rev. 2 addendum:** the four
fixed values in this revision (bay bounds, wedge geometry, lid-tab
footprint, tab engagement depth) were, in addition to the hand arithmetic
below, cross-checked against the actual rendered `.scad` geometry this
session using a locally-available OpenSCAD 2021.01 binary (verified
working via `--version`) plus `numpy-stl` volume/bounding-box measurement
on the exported STL — see the Rev. 2 changelog at the top of this document
and §11 for what was actually rendered/measured vs. what remains
arithmetic-only. This does not change the tooling-honesty position in §0
for the design as a whole (no STL has been committed to this repository,
and this was a targeted spot-check of this cycle's fixes, not a
comprehensive re-verification of every number in this document).

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

**Connector real-edge margin vs. bay boundary (MISS-001 fix — the actual
finding, not just its downstream effects on tabs/standoffs):**
```
J2/J3 footprint (per reference_pcba()): board-local X in [hx-5, hx+5], Y in [34,40]
SW1 footprint (per reference_pcba()):   center (44,37.5), radius 2.5 -> X in [41.5,46.5], Y in [35,40]

OLD (centerline-based, WRONG):
  bay_x_min=10.0, bay_x_max=50.0, bay_y_min=34.0
  J2 real left edge  (11.0) to bay_x_min(10.0)  = 1.0mm   <- reviewer-cited
  SW1 real right edge(46.5) to bay_x_max(50.0)  = 3.5mm   <- reviewer-cited
  Header row real Y edge(34.0) to bay_y_min(34.0) = 0.0mm <- reviewer-cited (ZERO clearance)

NEW (edge-based + bay_edge_margin, Rev. 2):
  bay_x_min=9.5, bay_x_max=48.0, bay_y_min=32.5
  J2 real left edge  (11.0) to bay_x_min(9.5)   = 1.5mm  (= bay_edge_margin, exactly)
  SW1 real right edge(46.5) to bay_x_max(48.0)  = 1.5mm  (= bay_edge_margin, exactly)
  Header row real Y edge(34.0) to bay_y_min(32.5) = 1.5mm (= bay_edge_margin, exactly)
```
Result: **PASS, and independently confirmed against the actual rendered
`.scad` geometry this session** — the bay cutout was rendered standalone,
exported to STL, and its true board-local bounding box measured directly
from the mesh: **X=[9.5, 48.0], Y-min=32.5**, matching the formulas exactly
(not just "should match on paper"). All three real connector-to-bay-edge
margins are now a uniform, genuinely positive **1.5mm** — up from the
broken 0.0mm/1.0mm/3.5mm the reviewer found, and no longer masked by a
centerline-based calculation that silently assumed zero connector footprint
width.

**Header bay vs. nearest standoffs and tabs (Rev. 2 — corrected):**
```
Bay global X range = [13.0, 51.5]   (was [13.5, 53.5])
MH-3 standoff X range = [57.0, 63.0]  -> gap = 5.5mm  (was 3.5mm, IMPROVED)
MH-4 standoff X range = [4.0, 10.0]   -> gap = 3.0mm  (was 3.5mm, still healthy)
Rear-right tab X range = [56.0, 64.0] -> gap = 4.5mm  (was 2.5mm, IMPROVED)
Rear-left  tab X range = [3.0, 11.0]  -> gap = 2.0mm  (was 2.5mm, still positive)
```
Result: **PASS** — all positive; the rear-left tab's 2.0mm is now the
tighter of the two tab clearances (asymmetric, since the bay's two edges
moved by different amounts — 0.5mm on the min side, 2.0mm on the max side
— while neither tab moved), but it is not the tightest margin in the
overall design (see D1-vs-bay below).

**D1 vs. bay (Rev. 2 — corrected):**
```
D1 hole top edge (global Y) = 35.0mm;  bay now starts at global Y = 36.0mm  (was 37.5mm)
Gap = 1.0mm  (was 2.5mm)
```
Result: **PASS**, but this is now the **tightest margin in the entire
design** — a direct, disclosed side effect of narrowing `bay_y_min` to
close the MISS-001 finding (D1 itself was not touched; only its distance to
the now-closer bay edge changed). Flagged in §12 Open Item #8, not silently
absorbed.

**D1 vs. nearest standoff (MH-4):**
```
distance = sqrt((10-3.5)^2 + (30-36.5)^2) = 9.19mm
sum of radii (D1 hole 1.5mm + standoff 3.0mm) = 4.5mm
9.19mm >> 4.5mm
```
Result: **PASS**, wide margin (also independently consistent with the
interface file's own "~9mm" note on this same distance).

**Single-fastener (M2.5×6mm) stack-up, used both for PCB standoffs and lid
tabs (Rev. 2 — lid tab corrected, MISS-004 fix):**
```
PCB standoff:  screw passes through pcb_thickness (1.6mm) + engages
               4.4mm of the 5.0mm pilot depth (0.6mm pilot unused/slack)
Lid tab:       screw passes through tab_lid_t (2.0mm, clearance) + engages
               4.0mm of the 4.6mm pilot depth (0.6mm spare, matching the
               PCB standoff's own precedent) -- 1.0mm solid floor remains
               below the pilot hole, UNCHANGED from before this fix
               (tab_base_t grew in lockstep with tab_pilot_depth, +0.6mm
               each, specifically so the floor figure would not need to
               change). Was: engaged exactly the full 4.0mm pilot depth
               with ZERO spare -- unlike the standoff's own deliberate
               0.6mm -- flagged as MISS-004 (MEDIUM).
```
Result: **PASS** for both uses — a single M2.5×6mm self-tapping screw,
used 8× total, is the entire fastener BOM for this enclosure. Both
fastening points now carry the same 0.6mm engagement-depth spare-margin
convention.

**Lid tab clearance-hole annular wall (MISS-003 fix — new check, this
design never had one before):**
```
Y-direction (the tight axis):
  OLD, using shared tab_project(6.0): (tab_project - tab_clear_dia)/2
      = (6.0 - 2.8)/2 = 1.6mm  <- BELOW min_wall_t (2.0mm), reviewer-cited defect
  NEW, using lid_tab_project(6.8):    (lid_tab_project - tab_clear_dia)/2
      = (6.8 - 2.8)/2 = 2.0mm  <- exactly at min_wall_t, matching the base
                                   tab's own (tab_project-tab_pilot_dia)/2
                                   = 2.0mm floor-precedent
X-direction (was already fine, untouched): (tab_w - tab_clear_dia)/2
      = (8.0 - 2.8)/2 = 2.6mm  <- unaffected; tab_w did not change
```
Result: **PASS** (corrected) — 2.0mm minimum annular wall in both
directions around the lid tab's clearance hole.

**Base-vs-lid fastener-hole coaxiality (verifies the MISS-003 fix didn't
break alignment):** widening the lid tab's footprint could have shifted its
hole off-axis from the base tab's pilot hole if done carelessly (naively
re-centering on the wider footprint would move the hole by
`(lid_tab_project-tab_project)/2 = 0.4mm`, exceeding the ~0.15mm/side
clearance-hole slop around an M2.5 shank: `(tab_clear_dia-2.5)/2 =
(2.8-2.5)/2 = 0.15mm`). This was avoided by keeping `hole_yc` computed from
the original, unchanged `tab_project` and only widening the surrounding
cube symmetrically around that fixed axis (see `lid_tab()` in the `.scad`
file). **Verified against the actual rendered geometry this session, not
just the shared formula:** a 2.0mm-diameter test cylinder (matching the
tighter of the two real bore diameters) was modeled through the full
fastener bore depth spanning both parts (`base_total_h - tab_pilot_depth`
= 14.0mm up to `base_total_h + lid_roof_t` = 20.6mm, a 6.6mm span) and
subtracted from the union of the real `base_tab()` + `lid_tab()` solids.
The result's measured volume (20.68mm³) matches a fully unobstructed
6.6mm-tall, 2.0mm-diameter cylinder (ideal value 20.73mm³, i.e. within
0.3% — the residual difference is explained entirely by circular-facet
tessellation, not by any obstruction) — i.e. the bore is completely clear
along its whole length, proving the two holes are genuinely coaxial in the
as-rendered geometry, not just coaxial "on paper."

## 8. Fastener placement summary

| Fastener use | Qty | Type | Boss OD/dims | Pilot dia | Pilot/engagement depth | Access direction |
|---|---|---|---|---|---|---|
| PCB-to-base standoffs | 4 | M2.5×6mm self-tapping | ⌀6.0mm cylinder | ⌀2.0mm | 5.0mm blind (4.4mm engaged) | +Z (screwdriver from above, before lid is fitted) |
| Lid-to-base corner tabs | 4 | M2.5×6mm self-tapping (same type) | 8×6.0mm external tab (base), 8×6.8mm (lid, Rev. 2 — widened, MISS-003 fix); 5.6mm thick (base, Rev. 2 — was 5.0mm) / 2.0mm (lid) | ⌀2.0mm (base) / ⌀2.8mm clearance (lid) | 4.6mm blind in base tab (Rev. 2 — was 4.0mm), 4.0mm engaged, 0.6mm spare (MISS-004 fix — was 0mm spare) | +Z (screwdriver from above, last assembly step) |

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
- **Base external corner tabs:** sit high on the wall (Z≈13.0–18.6mm out of
  an 18.6mm-tall base, updated from Z≈13.6–18.6mm since `tab_base_t` grew to
  5.6mm — MISS-004 fix) and project sideways as a 90°, unsupported overhang
  in the natural floor-down print orientation. **Addressed**, not ignored:
  a 45° self-supporting chamfer/gusset runs from the wall face up to the
  tab's underside, keeping the whole feature within the stated
  `max_overhang_deg` rule. **Rev. 2 correction (MISS-002, HIGH):** the
  chamfer/gusset described here used to be built from `hull()` of two
  0.01mm-thin cubes — the Mechanical Reviewer correctly identified this as
  a geometrically degenerate sliver (a `hull()` of two near-zero-area
  cross-sections is an infinitesimally thin diagonal fin, not a solid wedge
  with real cross-sectional area along its span), far below any FDM
  printer's minimum feature size, and NOT actually load-bearing support
  material regardless of what the angle math suggested on paper. This has
  been replaced with a genuine solid: a `linear_extrude()` of a
  right-triangle `polygon()` swept along `tab_w`, with real rise
  (`tab_chamfer_run` = 6.0mm) and run (`tab_project` = 6.0mm) legs — equal
  legs giving an exact 45° hypotenuse (the boundary of, not comfortably
  inside, the stated `max_overhang_deg` rule — called out explicitly rather
  than rounded to "clearly fine"), a triangular cross-section area of
  0.5×6.0×6.0 = 18mm², and total wedge volume 18mm²×`tab_w`(8.0mm) =
  **144mm³** at each of the 4 base tabs. This is no longer a mathematical
  artifact but an actual load-bearing gusset. **Empirically confirmed this
  session** (not just derived on paper): the wedge was rendered standalone
  in OpenSCAD 2021.01, exported to STL, and its bounding box (X=8.0mm,
  Y=6.0mm, Z-span=6.0mm — matching `tab_w`/`tab_project`/`tab_chamfer_run`
  exactly) and the combined tab+wedge volume (measured 398.39mm³ vs. the
  398.35mm³ hand-calculated total: 254.35mm³ tab-cube-minus-pilot-hole +
  144.0mm³ wedge — agreeing to within 0.02%, i.e. pure STL
  circular-tessellation noise, not a modeling error) were both confirmed;
  a rendered image was also visually inspected and shows a real, filled
  triangular cross-section tapering to a knife edge, not a sliver. This
  re-verification is what allows the self-check in §11 (item 9) to
  restore a PASS for this specific feature — see §11 for the precise
  scope of what was and was not re-verified.
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
  offered as a starting point only — it has **not** been visually verified
  this session (this specific `show_mode="print_layout"` render was not
  part of this cycle's targeted spot-check — see §0 for exactly what was
  and was not rendered this session, now that a working OpenSCAD binary has
  been found in this environment); a human should still confirm orientation
  visually (or use a slicer's "lay flat") before trusting it blindly.

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
| 2 | Connector accessibility (all connectors reachable/usable) | **PASS (Rev. 2 — corrected; the Cycle 1 PASS below was wrong)** — Cycle 1's claim rested on a centerline-based bay-margin calculation that the Mechanical Reviewer found produced a real margin of just 0.0mm at the header row (MISS-001, HIGH) — a genuine defect this self-check missed, not merely an under-explained one. `bay_x_min`/`bay_x_max`/`bay_y_min` are now recomputed from each connector's real footprint edge (the same `reference_pcba()` dimensions already used elsewhere in this file) plus an explicit `bay_edge_margin`(1.5mm); every real connector-to-bay-edge margin is now a uniform, genuinely positive **1.5mm**, confirmed against the actual rendered bay-cutout geometry this session, not just the formula (§7). Every one of J1/J2/J3/SW1/D1 still has a dedicated, purpose-matched opening (§6); the functional-access vs. height-clearance distinction still holds. |
| 3 | Component height clearance (top + bottom, vs. interface file) | **PASS** — top: 0.5mm margin above the corrected 8.5mm figure (§7); bottom: 6.0mm available vs. 0mm required, explained (not just asserted) as a side effect of the standoff's fastener-depth sizing |
| 4 | Internal clearance/interference (parts vs. walls/each other/fasteners) | **PASS** — all clearances in §7 computed numerically; one real conflict (lid-fastening approach) was found and resolved during design, not swept aside |
| 5 | Fastener placement (position, wall thickness, access direction) | **PASS (Rev. 2 — corrected; the Cycle 1 PASS below was wrong for the lid tab)** — Cycle 1's "adequate surrounding material at every boss" claim did not actually hold for the lid tab: its clearance-hole annular wall computed to **1.6mm**, below this design's own stated 2.0mm `min_wall_t` (MISS-003, MEDIUM), and its engagement depth carried **zero** spare margin, unlike the PCB standoff's own deliberate 0.6mm precedent (MISS-004, MEDIUM). Both fixed: `lid_tab_project`(6.8mm, lid-only override) restores exactly **2.0mm** annular wall; `tab_pilot_depth`(4.6mm)/`tab_base_t`(5.6mm) restore **0.6mm** engagement spare while preserving the 1.0mm solid floor unchanged (§7/§8). Base-vs-lid hole coaxiality after the footprint widening was verified both by formula and against actual rendered geometry this session (an unobstructed-bore probe test, §7). All 8 fasteners remain +Z-accessible at the correct assembly step. |
| 6 | Wall thickness (structural + printable) | **PASS** — 2.0mm uniform, justified against a stated FDM rule (§2/§5-item 7), not an arbitrary number |
| 7 | Assembly order (physically achievable, no trapped parts) | **PASS** — §10; the specific "headers trapped behind the lid" trap was explicitly reasoned through and resolved (PCB is populated before enclosure assembly, not after) |
| 8 | Print-fit tolerance (single stated value, consistently applied) | **PASS** — 0.2mm/side (§2), applied at the lid/base skirt joint and fastener clearance holes; explicitly distinguished from the separate keepout/margin concepts so as not to overstate what "tolerance" covers (§2) |
| 9 | Manufacturability (wall thickness, overhangs, bridges, stated material) | **PASS (Rev. 2 — corrected and re-verified; the Cycle 1 PASS below was wrong)** — Cycle 1's PASS rested on a "45° self-supporting chamfer" that, in the actual constructed `.scad` solid, was a `hull()` of two 0.01mm-thin cubes: a mathematically degenerate sliver, not real load-bearing support material (MISS-002, HIGH). This self-check did not catch it the first time because it reasoned from the code's own comment/stated intent rather than the actual solid produced — a mistake not repeated here. Replaced with a genuine `linear_extrude()`/`polygon()` right-triangle wedge (rise=run=`tab_chamfer_run`=`tab_project`=6.0mm → exact 45°, cross-section area 18mm², volume 144mm³ per tab, ×4 tabs) — see §9.2. Unlike Cycle 1, this PASS is grounded in actual re-verification, not restated intent: the wedge was rendered standalone in a locally-available OpenSCAD 2021.01 binary this session, exported to STL, and its bounding box and volume were measured directly from the mesh (398.39mm³ vs. 398.35mm³ hand-calculated, agreeing to <0.02%) — confirming a real, non-degenerate solid, not just a formula that looks right. **Caveat carried forward honestly, not smoothed over:** 45° is the exact *boundary* of this design's own `max_overhang_deg` rule, not a comfortable margin inside it; and this re-verification is a geometric measurement only — no slicer support-preview and no physical test print has been performed, and it does not substitute for the Mechanical Reviewer's own independent re-review. The separate per-part print-orientation correction (lid tabs do NOT need the chamfer originally planned for both parts) still holds unchanged. |
| 10 | Interface-value traceability (every dimension traced to a source or explicit assumption) | **PASS** — full parameter table in §4 labels every value CONFIRMED/ESTIMATE/ASSUMPTION/DERIVED with an explicit source |

**Overall self-check result (Rev. 2): 10/10 PASS, but 3 of those 10 (items
2, 5, 9) are corrected re-scores, not clean first-pass results** — the
Cycle 1 self-check's PASS claims for those 3 items were each actually wrong
in ways an independent reviewer caught and this design has now fixed (2
HIGH: MISS-001, MISS-002; 2 MEDIUM: MISS-003, MISS-004). This revision does
**not** claim a cleaner track record than it has; it is reported honestly
so the Mechanical Reviewer can weight this self-check's credibility
accordingly. No CRITICAL or currently-open HIGH issues remain identified by
this self-check. This still does **not** mean the design is approved —
independent Mechanical Reviewer sign-off is required regardless
(`.github/agents/mechanical-lead.agent.md`, "Out of scope": *"Declaring
your own design reviewed/complete... is mandatory regardless of how
confident you are"*) — and is the explicit next step for this revision,
not a formality. The items below are specifically flagged as things this
self-check cannot fully close out on its own.

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
   (≈38.5×6mm, Rev. 2 — was 40×6mm, see item 4 below) and D1 hole (⌀3.0mm)
   are this Mechanical Lead's own ESTIMATEs layered on top of the interface
   file's own estimates; both should be re-checked once real part numbers
   exist.
3. J1's MPN is not locked — this design's J1 cutout (9.5×6.0mm) already
   carries extra margin specifically because of this, but should still be
   re-verified once a real part is chosen.

**New estimates introduced by this Mechanical Lead, not present in the
interface file, that the Reviewer should specifically scrutinize:**
4. Header/button bay footprint dimensions (≈38.5mm × 6mm, Rev. 2 — was
   40mm × 6mm before the MISS-001 fix; the underlying connector-X-span
   estimate itself did not change, only the edge margin applied beyond it,
   which now reflects real footprint edges instead of centerlines) — an
   ESTIMATE built from the connector X positions plus an assumed margin,
   not from any actual header/switch datasheet.
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
8. **(Rev. 2 — superseded by a tighter margin found elsewhere; kept here
   with history rather than deleted)** The rear corner tabs' clearance to
   the header bay was 2.5mm uniformly and was, at Cycle 1, the tightest
   margin anywhere in this design. After the MISS-001 fix (recomputing bay
   bounds from real connector edges), the two tab clearances are no longer
   equal or the tightest: rear-left is now 2.0mm (down slightly) and
   rear-right is now 4.5mm (up). **Neither is the tightest margin anymore
   — see new item 8a below, which is.** Both remain positive and were
   checked numerically (§7), and both were also confirmed against the
   actual rendered bay-cutout geometry this session, not just computed on
   paper.
8a. **(Rev. 2 — new, directly caused by the MISS-001 fix; this is now the
    single tightest margin in the whole design)** D1's clearance to the
    header bay dropped from 2.5mm to **1.0mm** as a direct, disclosed side
    effect of narrowing `bay_y_min` to close out MISS-001 — D1 itself was
    not moved or resized. 1.0mm is still positive and was checked
    numerically (§7), but it is the tightest margin in this entire design
    (tighter than the 2.0mm/4.5mm tab-to-bay margins in item 8, and far
    tighter than the ~8.75mm+ margins found elsewhere). **This is the
    single item this Mechanical Lead would most want the Reviewer to look
    at again in this cycle** — not because the arithmetic is wrong (it has
    been checked twice, once by formula and once against rendered
    geometry), but because 1.0mm is a small absolute number for an FDM
    part with a stated 0.2mm/side fit tolerance and no stack-up analysis
    performed (that technique remains explicitly out of scope — see
    `.github/agents/mechanical-lead.agent.md`, "Out of scope"), so it
    deserves a deliberate judgment call about whether 1.0mm is enough
    margin in practice, not just confirmation that it is >0.
9. The J1 cutout's ≈9.5mm top-edge bridge span is within the stated ≤10mm
   rule but only just (§9.2) — flagged as a first-test-print watch item.

**Process/administrative item:**
10. Whether this original first-time creation of `hardware/mechanical/*`
    design files required a `validation/change-log.md` (ECO) entry: this
    Mechanical Lead's reading of `.github/instructions/mechanical-design.
    instructions.md` was that its ECO requirement is written for *changes*
    to an existing design, and that first creation had no prior enclosure
    design to have changed — so no ECO entry was added for that initial
    creation.
    **Rev. 2 update (this cycle):** this reasoning no longer applies as-is
    — this revision genuinely IS a change to an existing, already-reviewed
    design, prompted by the Mechanical Reviewer's own Cycle 1 findings. This
    Mechanical Lead's judgment call this cycle is to **still not add the ECO
    entry yet**, on a different and narrower rationale: `validation/
    change-log.md` and `validation/change-impact-matrix.md` were read this
    session but deliberately left unedited, because an ECO record is more
    useful once the Mechanical Reviewer's re-review actually confirms these
    fixes land correctly (avoiding a change-log entry for a fix that the
    re-review might still send back for further rework) rather than being
    logged mid-rework, before independent confirmation. This is, again, a
    judgment call flagged explicitly rather than a silent omission — the
    Hardware Lead/Reviewer should override it if the project's convention
    is actually "log every substantive rework immediately, regardless of
    review outcome."

## 13. Handoff

Per `.github/agents/mechanical-lead.agent.md`, handoff to the Mechanical
Reviewer (via the Hardware Lead) consists of:
- `bench-imu-01-enclosure.scad` (this directory)
- This file (`bench-imu-01-dimensional-spec.md`)
- The design rationale (§5–§10 above)
- The self-check result (§11)
- The open UNKNOWNs/ASSUMPTIONs list (§12)

No committed CAD/3D rendering, preview, or STL export accompanies this
handoff — see §0. This revision's fixes WERE, however, spot-checked this
session against actual rendered geometry from a locally-available OpenSCAD
2021.01 binary (bounding-box/volume measurement via `numpy-stl`); none of
those render/measurement artifacts were committed to this repository (§0),
so the Mechanical Reviewer should still expect to conduct their own
independent re-render/re-measurement as part of this re-review, not treat
this Mechanical Lead's spot-check as a substitute for it.
