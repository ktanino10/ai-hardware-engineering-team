# Bench-IMU-01 — Enclosure Dimensional Spec & Design Rationale

**Status:** Rev. 3 — drafted by Mechanical Lead, **not yet reviewed**. This
document does not declare itself reviewed or complete; it is the design
package handed to Independent Mechanical Review, and after that clears, the
REQ-403 disposition proposal in §8 goes to the human as a HITL gate. Nothing
in this file should be read as "approved."

**Changelog vs. Rev 2** (Rev 2 was Design-Complete; this is a full redesign,
not a patch — the flywheel's rotation-clearance envelope alone, ⌀76mm,
already exceeds the entire Rev 2 board width of 40mm, so no Rev 2 coordinate
could simply be extended):

- Board grew from 60×40mm (Rev 2) to 100×50mm (Rev 3) to host the new Motor
  Driver + Reaction Wheel subsystem (`hardware/mechanical-interface.md` A2).
  All new geometry is re-derived from the Rev 3 interface file; no Rev 2
  coordinate is reused unchanged except where the underlying board region
  (the original 0–60mm "sensor zone") itself did not move.
- Piece count: **2 → 3.** Rev 2 was Base + Lid. Rev 3 is **Base + PCB Lid +
  Containment Cap** — a third piece added specifically to give the flywheel
  bay a dedicated, removable, physically containing top (see §5 item 10 and
  §8 for why REQ-309's 2-piece baseline was not treated as a ceiling).
- New: a second enclosure bay (the "flywheel bay") housing the motor,
  flywheel, and a rotation-clearance keep-out volume, joined to the existing
  PCB bay by a wire-passage duct. This bay did not exist in Rev 2 at all.
- New: off-board/bracket-mounted motor (§6) — the motor is **not** a
  PCB-footprint part; it mounts to a raised platform molded into the base,
  not to the board.
- New connectors/holes relative to Rev 2: J4 (barrel jack, motor supply),
  MC-1 (motor phase-wire pigtail, wire-lead not PCB-trace per the interface
  file), MH-5/MH-6 (dedicated motor-driver-zone mounting holes). J1/J2/J3/SW1/D1
  carry over from Rev 2 in identity, re-positioned only by the board's own
  Y-rescale (see §10).
- New fastener classes: Rev 2 used one class (M2.5 self-tapping, PCB lid to
  base). Rev 3 adds **plain M3 clearance** (motor-to-platform, direction
  reversible) and **M3-into-heat-set-insert** (containment cap to base
  flange) — three classes total, each justified separately in §12.
- Envelope grew from Rev 2's base-outer 67.0×47.0mm (true assembled,
  including tabs/lid-skirt overhang, ≈71.4×59.8mm; total height 20.6mm) to
  Rev 3's 107×162mm shell-only footprint / 111.4×170.6×43.0mm true assembled
  envelope (§3) — driven by the flywheel bay's own footprint and height, not
  by the PCB bay, which only grew to 107×57mm (still smaller than the
  flywheel bay's own 87×87mm footprint).
- New: REQ-403 safety disposition proposed — **physical containment**
  (§8), not clearance-plus-firmware-limiting alone. This is new because Rev 2
  had no rotating mass; Rev 3 introduces one for the first time.
- New: REQ-306 rotation-clearance keep-out (§7) and REQ-307 vibration
  isolation disposition (§9) — neither applied to Rev 2, which had no motor.
- Verification: this revision's own build/check process caught and fixed 4
  geometric defects (2 of them collisions that would have caused genuine
  print/assembly failures or a safety-relevant open gap), correctly
  dismissed 2 false-alarm findings, and flagged (without fixing, as
  out-of-scope for this task) one pre-existing Rev 2 defect plus one new
  borderline-but-compliant finding — all itemized in §11.
- Rev 2's proven conventions carried forward and **re-justified against the
  new geometry** (not assumed to still fit): 2.0mm minimum wall thickness,
  0.2mm/side fit clearance, external-tab lid fastening with M2.5 self-tapping
  screws for the PCB lid, cap+skirt joint style (now used twice — PCB lid
  and containment cap both use it).

**Author:** Mechanical Lead (this session).
**Companion file:** `hardware/mechanical/bench-imu-01-enclosure.scad` (Rev 3,
991 lines) — every dimension in this document is a named variable in that
file; the two must be read together.
**Authoritative input:** `hardware/mechanical-interface.md` (Rev 3, 686
lines, fixed input — not edited by this task). Requirements traced:
`requirements/requirements.md` REQ-306, REQ-307, REQ-308, REQ-309, REQ-403,
REQ-405. Safety context: `validation/open-issues.md` ISS-020.

---

## 0. Tooling honesty

Re-verified fresh in this session, not assumed from a prior revision or from
the task brief's own claim:

- `blender-get_addon_status` → **"Could not connect to Blender."** No live
  CAD/3D-modeling MCP connection exists in this environment. This matches
  the task brief.
- However, a local `openscad` **2026.08.30** binary (`/opt/homebrew/bin/openscad`)
  **is** installed and working, along with Python `numpy-stl` 3.2.0 and
  `trimesh` 4.11.5. This **contradicts** the task brief's claim of "no local
  `openscad`/`freecad`/`cadquery` toolchain" — flagged here rather than
  silently corrected, per this project's own tooling-honesty discipline. No
  `freecad`, `cadquery`, `solid`, or `build123d` was found.
- What this means in practice: this design **was** rendered and geometrically
  validated locally this session — `openscad -o out.stl bench-imu-01-enclosure.scad`
  produces a manifold mesh (CGAL Status: NoError, Genus 6, 4610 vertices,
  9240 facets), and `trimesh`/`numpy-stl` were used for boolean-intersection
  interference checks between parts (§11). This is a **real geometric
  check**, not an eyeball estimate — but it is still **not** a substitute for
  a physical print-and-fit test, a structural (FEA) analysis, or a CAD-native
  fillet/draft/tolerance-stack review. No STL was exported into the repo (the
  deliverable remains the parametric `.scad` source plus this spec); no claim
  of fabrication or physical fit-check is made anywhere in this document.
- The `.scad` file's own header (lines 11–38) carries the identical
  disclosure, so a reader of either file alone gets the same honest picture.

---

## 1. Scope recap

Per `.github/agents/mechanical-lead.agent.md`, Phase 1 scope is: enclosure/
spatial layout, PCB mounting, connector accessibility, component-height
clearance, internal clearance/interference, fastener placement, wall
thickness, assembly order, and basic print-fit tolerance +
manufacturability. Out of scope (explicitly deferred, `docs/architecture-evolution.md`
§10/§13): statistical tolerance stack-up, motion/joints/hinges, advanced
material selection beyond stating an assumed print material, thermal zones,
antenna keep-out, STEP/neutral 3D model, center of mass, battery wiring,
detailed cable-exit geometry. This revision adds three new topics to the
Phase-1 checklist that Rev 2 never had to address: a rotation-clearance
keep-out (REQ-306), a motor-mounting-method decision, and a safety-critical
containment disposition (REQ-403) — all still within Phase 1's existing
"internal clearance / component-height clearance / basic manufacturability"
categories, just applied to a new, moving, energy-storing component.

---

## 2. Print-fit tolerance & manufacturability rules

Carried forward from Rev 2 **and explicitly re-justified** against the new
geometry (per this task's instruction not to assume Rev 2's conventions
still fit unchanged):

| Rule | Value | Re-justification for Rev 3 |
|---|---|---|
| Fit clearance (mating parts, per side) | **0.2mm** | Same FDM-fit allowance as Rev 2. Re-checked against the new, larger mating interfaces: PCB-lid skirt/base (unchanged formula), and the **new** containment-cap skirt/base-flange interface (105.4mm ID vs. 105.0mm OD — same 0.2mm/side result at 10× the diameter, so the allowance is diameter-independent and still appropriate). |
| Minimum wall thickness (FDM) | **2.0mm** | Unchanged rule. Re-checked at every new Rev 3 wall: flywheel-bay wall (`containment_wall_t`=4.0mm, 2× minimum, justified by containment duty in §8, not just print rules), heat-set-insert flange material each side of the insert bore (2.2mm, §12), and the motor-wire-bridge duct-bore wall (exactly 2.0mm in Z — the one place Rev 3 sits at the rule's exact floor, flagged in §11/§13). |
| Overhang requiring support | **>45° from vertical** | Unchanged rule of thumb. Applied to new features: the motor-platform boss (vertical cylinder, 0° overhang, fine), the containment-cap dome/flange transition (vertical wall + flat flange, no overhang), and the wire-bridge block (flat horizontal underside — evaluated as a bridge, not an overhang; see next row). |
| Maximum unsupported bridge span | **10.0mm** | Unchanged rule (same as Rev 2's own J1-cutout precedent). Re-checked at the **new** motor-wire bridge: true unsupported span is 9.0mm (bridge center) to 9.416mm (bridge edges) — within the rule, but at 90.0–94.2% of it. Disclosed, not silently passed over (§11/§13), mirroring Rev 2's own disclosed-but-accepted 9.5mm/95%-of-limit J1 bridge. |
| Print material | **PETG** (`ASSUMPTION`, per `hardware/mechanical-interface.md` B6) | Not a Mechanical Lead decision — inherited from the interface file's own stated assumption, cited here rather than re-derived. PETG's practical layer-adhesion strength is part of why the flywheel-bay wall was set to 2× minimum (4.0mm) rather than 1× — a plastic wall in a containment role should not rely on the thinnest print-safe wall available. If PLA is used instead, this containment margin should be re-examined (PLA is more brittle under impact than PETG). |

No advanced tolerance stack-up (multi-part statistical accumulation) is
performed — this remains explicitly out of Phase 1 scope. Every check in
this document is a single-interface, deterministic clearance computation.

---

## 3. Overall envelope

Two ways of reading "footprint," both reported (same convention Rev 2 used
for its own two-tier reporting, extended here across two bays):

| Reading | X | Y | Z (height) | vs. REQ-308 (~150mm-class, "relaxed... generous soft ceiling... not to be over-engineered against") |
|---|---|---|---|---|
| **Shell-only** (both bay footprints as designed, tabs/skirt overhang excluded) | 107.0mm | 162.0mm | — | Y is 8.0% over the ~150mm reading |
| **True assembled** (includes PCB-lid tab projection and containment-cap flange, the actual outermost physical extent) | 111.4mm | 170.6mm | 43.0mm | Y is 13.7% over the ~150mm reading |

REQ-308 explicitly frames ~150mm as a relaxed, generous **soft** ceiling, not
a hard limit, and explicitly cautions against over-engineering to hit it
exactly. 8–14% over is judged acceptable given: (a) the flywheel's own
rotation-clearance diameter (76mm) plus a structurally-justified 4mm
containment wall plus a 9mm flange projection for the cap-bolt bosses is a
real physical lower bound, not a padding choice — the flywheel bay's own
minimum footprint is 2×(43.5+9.0) = 105.0mm across; (b) the PCB bay's own
107mm side was inherited from the interface file's own board width (§4), not
from the Mechanical Lead's discretion. The Y-dimension overrun is
acknowledged as a genuine, disclosed trade-off (see §10 for the alternative
layout that was considered and rejected), not something silently absorbed.

Total height (43.0mm) is set entirely by the **flywheel bay's** own Z-stack
(§7), which is more than double the PCB bay's own height (23.1mm) — the two
bays are side-by-side (not stacked), so the assembly's overall height is the
taller of the two, not their sum.

---

## 4. Full dimensional parameter tables

### 4.1 Interface-traced values (from `hardware/mechanical-interface.md`)

| Parameter | Value | Unit | Confidence | Source |
|---|---|---|---|---|
| `pcb_length` | 100 | mm | CONFIRMED | Interface A2 |
| `pcb_width` | 50 | mm | CONFIRMED | Interface A2 |
| `pcb_thickness` | 1.6 | mm | CONFIRMED | Interface A2 (standard 2-layer stack, unchanged from Rev 2) |
| `top_component_clearance` | 11 | mm | CONFIRMED | Interface A3 — tallest top-side part is J4 barrel jack (per interface's own component-height table) |
| `bottom_component_clearance` | 0 | mm | CONFIRMED | Interface A3 — no bottom-side components populated |
| Board mounting holes MH-1..4 | (3.5,3.5), (96.5,3.5), (96.5,46.5), (3.5,46.5), ⌀2.8mm clearance (M2.5) | mm | CONFIRMED | Interface A1 (corner pattern, unchanged in kind from Rev 2, repositioned for the new 100×50 outline) |
| Board mounting holes MH-5/6 | (85,3.5), (85,46.5), ⌀2.8mm clearance (M2.5) | mm | CONFIRMED | Interface A1 — added specifically near the motor-driver zone for extra board rigidity close to the new high-current/switching components |
| J1 (existing header) | (0,25), 9.5×6mm cutout, ref. height 3.2mm | mm | CONFIRMED | Interface A4, unchanged position/size from Rev 2 |
| J2, J3 (existing headers) | (16,50), (30,50) | mm | CONFIRMED | Interface A4, unchanged from Rev 2 |
| SW1 (button) | (44,50) | mm | CONFIRMED | Interface A4, unchanged from Rev 2 |
| D1 (LED) | (10,37.5) | mm | CONFIRMED | Interface A4 — Y-position rescaled from Rev 2's 30mm by the same 1.25× board-width growth ratio applied to all original sensor-zone parts |
| J4 (barrel jack, motor supply) | (100,25), edge-mounted | mm | CONFIRMED position / **ESTIMATE cutout diameter** | Interface A4 for position; `j4_cut_dia`=10.0mm is this Mechanical Lead's own outside-knowledge estimate for a generic 5.5/2.1mm barrel jack, no datasheet cited in the interface file — flagged for pre-build re-verification |
| MC-1 (motor phase-wire pigtail) | (92,0), bottom edge, wire exit −Y | mm | CONFIRMED | Interface A4 — **wire-lead, not PCB-trace**, per interface's explicit note; this is a board-edge exit point, not a component footprint |
| M1 motor body | ⌀27mm × 18.5mm height, ⌀3mm shaft | mm | CONFIRMED | Interface B1, `DS-MTR-021` |
| M1 mounting-bolt pattern | 12mm square, 4× holes | mm | **ASSUMPTION** | Interface B1 flags this as an open item — no confirmed datasheet bolt-pattern; a generic hobbyist-brushless-outrunner convention is assumed here, explicitly flagged NOT T-Motor-specific |
| Flywheel disk | ⌀60mm × 4.5mm, mild steel, ρ=7850 kg/m³ | mm / kg/m³ | **ASSUMPTION** | Interface B2 — back-computed against the electrical team's target rotational inertia; 4.505mm recomputed vs. 4.5mm stated is a consistency check, not an independent confirmation |
| Rotation clearance envelope | ⌀76mm × 10.5mm axial | mm | CONFIRMED (derivation) | Interface B5 — `fw_radial_margin`=8mm, `fw_axial_margin_per_face`=3mm, both interface-stated safety margins around the disk's own swept volume |
| Print material | PETG | — | ASSUMPTION | Interface B6 |
| Total assembly mass | ≈149–150g (board ≈19–20g populated + motor ≈30g + flywheel 100g, enclosure plastic itself is additional) | g | ESTIMATE | Interface A5/B1/B2/B7 — context only, not a driving mechanical dimension at this scale; no structural deflection/FEA analysis performed (out of Phase 1 scope) |

### 4.2 PCB-bay own-design values (formulas unchanged from Rev 2; only resulting numbers changed because the board itself grew)

| Parameter | Value | Unit | Confidence | Rationale |
|---|---|---|---|---|
| `fit_clearance` | 0.2 | mm | Carried, re-justified §2 | FDM fit allowance |
| `min_wall_t`/`wall_t`/`floor_t` | 2.0 | mm | Carried, re-justified §2 | Minimum FDM wall |
| `board_xy_keepout` | 1.5 | mm | DERIVED | Same margin rule as Rev 2, applied around the new 100×50 outline |
| `standoff_od` | 6.0 | mm | DERIVED | Unchanged formula (2× `standoff_pilot_dia` + wall margin) |
| `standoff_pilot_dia` | 2.0 | mm | Carried | Self-tap pilot for M2.5, unchanged |
| `standoff_h` | 6.0 | mm | DERIVED | = `bottom_component_clearance`(0) + margin — same formula as Rev 2, coincidentally close in value only because Rev 2's own bottom clearance was also small |
| `screw_len` | 6.0 | mm | Carried | M2.5 self-tap screw length, unchanged |
| `z_margin` | 0.5 | mm | Carried | Same stack-up margin convention as Rev 2 |
| `base_interior_h` | 19.1 | mm | DERIVED | = `standoff_h` + `pcb_thickness` + `top_component_clearance` + `z_margin` = 6.0+1.6+11.0+0.5 |
| `base_total_h` | 21.1 | mm | DERIVED | = `base_interior_h` + `floor_t` |
| `lid_lip_h` | 3.0 | mm | Carried | Unchanged skirt-overlap depth |
| `lid_roof_t`/`lid_skirt_t` | 2.0 | mm | Carried | = `min_wall_t` |
| `pcb_bay_total_height` | 23.1 | mm | DERIVED | = `base_total_h` + `lid_roof_t` |
| `interior_x` / `interior_y` | 103 / 53 | mm | DERIVED | = `pcb_length`/`pcb_width` + 2×`board_xy_keepout` |
| `base_outer_x` / `base_outer_y` | 107 / 57 | mm | DERIVED | = interior + 2×`wall_t` |
| `lid_skirt_inner_x` / `_y` | 107.4 / 57.4 | mm | DERIVED | = `base_outer` + 2×`fit_clearance` |
| `lid_skirt_outer_x` / `_y` | 111.4 / 61.4 | mm | DERIVED | = skirt-inner + 2×`lid_skirt_t` |
| `board_offset_x` / `_y` | 3.5 / 3.5 | mm | DERIVED | = `wall_t` + `board_xy_keepout` |
| `j1_cut_w`/`_h`/`_z` | 9.5 / 6 / 6 | mm | Carried | Unchanged from Rev 2 — same connector, same size |
| `j4_cut_dia`/`_z` | 10 / 6 | mm | **ESTIMATE** | New Rev 3 cutout — see §4.1 flag |
| `bay_edge_margin` | 1.5 | mm | Carried | Unchanged component-keepout-to-bay-wall rule |
| `bay_x_min`/`_max` | 9.5 / 48.0 | mm | DERIVED | Numerically **unchanged from Rev 2** — governed entirely by the original sensor-zone parts (J2 at X=16, SW1 at X=44), whose X-positions did not move when the board grew in length |
| `bay_y_min` | 42.5 | mm | DERIVED | Rescaled from Rev 2's 32.5mm by the board's own Y-growth |
| Tab positions (corners only) | (3.5,3.5,dy−1), (96.5,3.5,dy−1), (96.5,46.5,dy+1), (3.5,46.5,dy+1) | mm | DERIVED | Repositioned to the new board corners; same 4-corner convention as Rev 2 |
| `tab_w`/`tab_project`/`tab_base_t` | 8 / 6 / 5.6 | mm | Carried | Unchanged tab geometry |

### 4.3 Motor-mount own-design values (new in Rev 3)

| Parameter | Value | Unit | Confidence | Rationale |
|---|---|---|---|---|
| `motor_platform_od` | 31.0 | mm | DERIVED | = `m1_body_dia`(27) + 2×`wall_t`(2.0) — the boss is sized to comfortably enclose the motor body's own footprint plus a minimum print-safe wall |
| `motor_platform_h` | 8.0 | mm | ESTIMATE | Chosen to lift the motor body clear of the flywheel-bay floor disc so the flywheel itself (mounted above the motor) sits at the height needed for its own clearance envelope — see §7 Z-stack |
| `m1_mount_hole_dia_clear` | 3.4 | mm | Carried convention | Standard M3 clearance-hole diameter (same clearance-fit convention Rev 2 used for M2.5 at 2.8mm, scaled up to M3) |
| `m1_bolt_square` | 12.0 | mm | **ASSUMPTION** | See §4.1 flag — generic hobbyist convention, not datasheet-confirmed |
| Bolt-hole corner radius | 8.485 | mm | DERIVED | = √(6²+6²) from the assumed 12mm-square pattern's center |
| Margin, bolt-hole to motor-body edge | 5.015 | mm | DERIVED | = 13.5(`m1_body_dia`/2) − 8.485 — pattern is physically plausible under the motor body |
| Margin, bolt clearance-hole outer edge to platform-boss edge | 5.315 | mm | DERIVED | = 15.5(`motor_platform_od`/2) − (8.485+1.7) |
| Shaft clearance-hole radius | 1.7 | mm | DERIVED | = (`m1_shaft_dia`(3.0)+2×`fit_clearance`)/2 |
| Gap, shaft-hole edge to nearest bolt-hole edge | 5.085 | mm | DERIVED | No overlap between the two hole families |
| `fw_hub_standoff` | 3.0 | mm | ESTIMATE | Gap between motor bell-top and the bottom face of the hub collar, for tool/wrench clearance when tightening the collar's set screw |
| `fw_hub_collar_od`/`_h` | 8.0 / 6.0 | mm | **ASSUMPTION** | Generic set-screw shaft-collar dimensions; no specific manufacturer part selected/cited — flagged as an open item in §16 |
| `fw_shaft_exposed_len_needed` | 9.0 | mm | DERIVED (minimum requirement) | = `fw_hub_standoff`(3)+`fw_hub_collar_h`(6) — this is the **minimum** shaft length M1 must expose above its bell for this mounting scheme to work; M1's actual exposed shaft length is UNKNOWN (not in the interface file) and must be confirmed before build |

### 4.4 Flywheel bay / containment own-design values (new in Rev 3)

| Parameter | Value | Unit | Confidence | Rationale |
|---|---|---|---|---|
| `fw_dia` | 60.0 | mm | ASSUMPTION (interface B2) | Flywheel disk diameter |
| `fw_radial_margin` | 8.0 | mm | CONFIRMED (interface B5) | Safety margin beyond the disk's own swept radius |
| `fw_env_dia` | 76.0 | mm | DERIVED | = `fw_dia` + 2×`fw_radial_margin` — the actual REQ-306 rotation-clearance keep-out diameter |
| `fw_axial_margin_per_face` | 3.0 | mm | CONFIRMED (interface B5) | Axial safety margin, each face of the disk |
| `fw_env_axial` | 10.5 | mm | DERIVED | = `fw_t`(4.5) + 2×`fw_axial_margin_per_face` |
| `fw_radial_standoff` | 1.5 | mm | ESTIMATE | Extra gap between the rotation-clearance envelope's own outer radius and the containment wall's inner face — a "keep-out beyond the keep-out," so a small manufacturing/assembly offset can't put the wall inside the safety margin itself |
| `fw_bay_inner_r` | 39.5 | mm | DERIVED | = `fw_env_dia`/2 (38.0) + `fw_radial_standoff`(1.5) |
| `containment_wall_t` | 4.0 | mm | ESTIMATE (2× `min_wall_t`) | Deliberately thicker than the print-safe minimum — this wall's job is containment (§8), not just enclosure, so it is sized above the manufacturability floor on purpose |
| `fw_bay_outer_r` | 43.5 | mm | DERIVED | = `fw_bay_inner_r` + `containment_wall_t` |
| `fw_flange_project` | 9.0 | mm | ESTIMATE | Radial width of the bolted flange band, sized to comfortably host 6 heat-set inserts around the circumference with adequate wall material each side (§12) |
| `bolt_circle_r` | 48.0 | mm | DERIVED | = `fw_bay_outer_r` + `fw_flange_project`/2 — centered in the flange band |
| `fw_flange_or` | 52.5 | mm | DERIVED | = `fw_bay_outer_r` + `fw_flange_project` |
| `fw_flange_dia` | 105.0 | mm | DERIVED | = 2×`fw_flange_or` — the base's own flange OD that the containment cap's skirt slides over |
| `n_cap_bolts` | 6 | — | ESTIMATE | Even spacing (60° apart) around the flange, judged adequate for a cap whose job is to stay closed under a low-probability, low-bulk-stress event (§8) — not a computed fastener-load calculation (out of Phase 1 scope) |
| `heatset_od`/`_len` | 4.6 / 5.7 | mm | **ASSUMPTION** | Generic brass heat-set insert dimensions (common M3 size); no specific manufacturer part selected — flagged in §16 |
| Margin, insert bore to flange inner/outer edge | 2.2 / 2.2 | mm | DERIVED | Both exceed `min_wall_t`(2.0) by 0.2mm — tight but compliant (§12) |
| `flange_band_h` | 8.0 | mm | ESTIMATE | Z-height of the bolted flange band, sized to give the heat-set insert (5.7mm) a full depth of solid material plus a margin above it (2.3mm) below the cap's own top surface |
| `wire_duct_dia` | 5.0 | mm | ESTIMATE | Sized for a small pigtail of 2–3 motor-phase wires (18–22 AWG class), no specific wire gauge confirmed |
| `wire_bridge_w`/`_h` | 12.0 / 9.0 | mm | DERIVED | `_h` = `wire_duct_dia` + 2×`wall_t` (duct bore + minimum wall both sides, by construction — leaves **zero** spare in Z, see §11/§13) |
| `bridge_fuse_overlap` | 2.0 | mm | ESTIMATE | Introduced this revision specifically to fix Error #3 (§11) — ensures the wire-bridge block's inner face is planted solidly inside the flywheel-bay wall rather than stopping at the bay's own center |
| Z-stack: `fw_floor_top` | 2.0 | mm | DERIVED | = `floor_t` |
| Z-stack: `fw_motor_platform_top` | 10.0 | mm | DERIVED | = `fw_floor_top` + `motor_platform_h`(8.0) |
| Z-stack: `fw_motor_bell_top` | 28.5 | mm | DERIVED | = `fw_motor_platform_top` + `m1_body_h`(18.5) |
| Z-stack: `fw_disk_bottom`/`_top` | 31.5 / 36.0 | mm | DERIVED | = `fw_motor_bell_top` + `fw_hub_standoff`(3.0) as the bottom face; `_top` = `_bottom` + `fw_t`(4.5) |
| Z-stack: `fw_clearance_top` | 39.0 | mm | DERIVED | = `fw_disk_top` + `fw_axial_margin_per_face`(3.0) |
| Z-stack: `fw_cap_outer_top`/`fw_bay_total_height` | 43.0 / 43.0 | mm | DERIVED | Cap adds 4.0mm of dome/flange material above the clearance envelope's own top |

---

## 5. Design rationale by checklist item

Numbered to match the Mechanical Reviewer's own 10-item checklist (§15
reproduces it verbatim for the self-check):

1. **PCB mounting** — 6 standoffs (`base_standoffs()`) at MH-1..6, unchanged
   mechanism from Rev 2 (heat-formed/self-tap pilot bosses), now 6 instead of
   4 because the interface file added MH-5/6 for rigidity near the new
   motor-driver zone.
2. **Connector accessibility** — see §10, all cutouts sized/positioned from
   interface-file coordinates; the one new judgment call (the ~42mm wire run
   from the duct to MC-1's actual position) is disclosed there, not buried.
3. **Component-height clearance** — `top_component_clearance`=11mm and
   `bottom_component_clearance`=0mm both taken directly from the interface
   file (A3), driving `base_interior_h`/`lid_lip_h` unchanged in formula from
   Rev 2.
4. **Internal clearance/interference** — see §11 for the full computed
   record (4 fixed defects, 2 dismissed false alarms, 1 flagged pre-existing
   issue, 1 new borderline finding).
5. **Fastener placement** — see §12; 3 fastener classes now, each justified
   by the joint it serves, not by copying Rev 2's single class onto new
   joints that have different duty.
6. **Wall thickness** — 2.0mm minimum held everywhere except by deliberate,
   disclosed exception (flywheel-bay wall at 4.0mm for containment duty; the
   wire-bridge duct wall sits at exactly 2.0mm, §11/§13).
7. **Assembly order** — see §14; re-derived from scratch for 3 pieces, not
   copied from Rev 2's 2-piece sequence.
8. **Basic print-fit tolerance** — 0.2mm/side, applied consistently at both
   mating interfaces (PCB lid/base, containment cap/base flange), §2.
9. **Basic manufacturability/3D-printability** — §13; every new feature
   checked against the same overhang/bridge/wall rules as Rev 2, not given a
   pass by association with a previously-reviewed design.
10. **Interface-value traceability** — §4.1 traces every board-geometry
    number to its interface-file source; §16 lists everything that is this
    Mechanical Lead's own ASSUMPTION/ESTIMATE rather than an interface fact.

Two items unique to this revision, not on the Reviewer's original 10-item
list because Rev 2 had no rotating mass, are addressed as dedicated sections
rather than folded into the above: **§6 motor-mounting-method decision**,
**§7 rotation clearance / REQ-306**, **§8 REQ-403 safety disposition**, **§9
vibration isolation / REQ-307 disposition**. The piece-count decision (item
10 above, REQ-309) is expanded on here: Rev 2's 2-piece construction was
explicitly framed by the requirement as a baseline, not a ceiling: adding a
3rd piece (the containment cap) was a deliberate design decision, not a
default, and is justified entirely by §8's containment reasoning — without
the REQ-403 containment need, a 2-piece design (motor/flywheel bay open on
top, or covered by an extension of the PCB lid) would likely have sufficed
for the "enclosure" requirement alone.

---

## 6. Motor-mounting-method decision

**Decision: off-board (bracket/platform)-mounted, not a PCB-footprint
part.** The motor mounts to a raised cylindrical platform (`motor_platform()`)
molded directly into the enclosure base, using its own 4-bolt pattern into
that platform — not to the PCB. Electrical connection to U5 (motor driver)
is via a wire-lead pigtail (MC-1, board-edge exit at (92,0)), not a
PCB-mounted connector footprint that the motor plugs into directly. This
matches the interface handoff's own non-binding lean and the constraint that
MC-1 is explicitly a wire-lead connection, not a PCB trace.

**Why not on-PCB mounting:** the motor's own footprint (⌀27mm body) and
its bolt pattern would need to sit directly over/adjacent to the PCB, but
the flywheel's rotation-clearance envelope (⌀76mm — see §7) is already
larger than the entire 50mm board width. Any on-PCB motor mount would force
either (a) the flywheel's swept volume to overhang the PCB edge, or (b) the
PCB to be enlarged specifically to host the motor footprint under the
flywheel — both of which subordinate the board's own routing/component
layout to a purely mechanical constraint that the interface file's own B5
derivation already treats as enclosure-side, not board-side. An off-board
platform decouples the two: the PCB's own footprint is sized by its
electronics (100×50mm per A2), and the motor/flywheel subsystem is sized by
its own physics (§7), and the two are joined only by a wire and a duct.

**Why vertical shaft, motor below / flywheel above:** this places the
flywheel's own mass directly above its rotating support (the motor's bell
and shaft), which is the geometrically simplest and lowest-part-count way to
stack the disk on the shaft with a hub collar, and it means the flywheel's
own weight loads the shaft axially/rotationally in the same way the motor
was designed for (most small BLDC/hobby motors expect an axial mounted load
on a vertical or near-vertical shaft in this class of application) rather
than a cantilevered horizontal arrangement that would impose a bending
moment on the shaft the motor's own bearings may not be rated for. No
motor-bearing load rating is in the interface file (UNKNOWN) — the vertical
arrangement is the more conservative choice given that unknown, not a
datasheet-confirmed one.

**Why a shaft-mounted hub collar, not the bell-mount/ring-geometry
alternative:** the interface file (B2) explicitly flags a second, real
alternative — mounting the flywheel directly to the motor's own rotating
outrunner bell (a ring/annulus shape around the bell rather than a solid
disk on the shaft) — and explicitly cautions that this alternative would
have a **higher** true moment of inertia than the solid-disk figure this
whole design (and the electrical team's own target) is built around. This
design does **not** adopt the bell-mount alternative, for three reasons: (1)
it would silently change the flywheel's own moment of inertia away from the
value the electrical/control side is presumably targeting, without being
asked to make that trade; (2) a shaft-mounted hub collar is a simpler,
better-understood mechanical interface for a paper-design exercise — its
failure mode (a set-screw loosening) is at least nameable, whereas a
bell-mount's attachment method to a specific motor's specific bell geometry
is not specified anywhere in the interface file; (3) the interface file
presents the solid-disk/shaft-mount geometry as the **primary** proposal,
with the bell-mount flagged as an alternative, not a preference — so this
design follows the primary proposal. This is disclosed here as an explicit
choice, not a silent omission of the alternative.

**Consequence for U5 wiring:** because the motor sits ~42mm away (in X) from
MC-1's actual board-edge position (see §10), the motor's 3-phase wire
pigtail must run along the interior floor between the flywheel bay's wire
duct and the PCB bay. This is a real, disclosed trade-off from choosing a
width-centered flywheel-bay layout over a motor-zone-centroid-aligned one
(§10) — it does not affect the mounting-method decision itself, only the
wire-routing distance.

---

## 7. Rotation clearance envelope / REQ-306

REQ-306 requires the enclosure design to provide a real, checked 3D keep-out
around the flywheel's swept volume — not an eyeballed gap. This design's
keep-out is the volume between `fw_env_dia`=76.0mm (radial) and
`fw_env_axial`=10.5mm (axial), both taken directly from the interface file's
own stated margins (B5: 8mm radial, 3mm axial per face) around the disk's
actual physical envelope (⌀60×4.5mm). This is a real solid modeled in the
`.scad` file as `fw_clearance_zone()` (rendered as a translucent reference
volume, not a physical part) and used as the actual sizing driver for the
containment wall's own inner radius — i.e., the keep-out is not just
documented, it is the dimension the containment structure is built around:

- `fw_bay_inner_r` = `fw_env_dia`/2 + `fw_radial_standoff` = 38.0+1.5 = 39.5mm
  — the containment wall's inner face sits 1.5mm beyond the keep-out's own
  outer radius, so the wall itself never physically encroaches into the
  keep-out volume, with margin.
- Vertically, `fw_clearance_top`=39.0mm is the keep-out's own top face; the
  containment cap's structure begins only above that, at 39.0–43.0mm.

**Sanity checks performed (§11 has the full record):** the motor platform
boss (radius 15.5mm) and its bolt/shaft holes sit entirely inside the
keep-out's own inner radius (39.5mm) with 24.0mm of clear radial gap between
the platform's own edge and the containment wall — this gap is exactly what
the missing-floor defect (Error #4, §11) required a floor disc to span, and
it is now filled with solid material, not left open. The disk's own radius
(30.0mm) plus the required 8.0mm interface-mandated margin (=38.0mm) is
checked against the wall's inner face (39.5mm) with the additional 1.5mm
standoff explicitly by construction, not by coincidence.

This keep-out is a **clearance decision**, answering "can the flywheel spin
without hitting anything in normal operation." It is explicitly **not** a
substitute for the REQ-403 containment decision (§8), which answers a
different question: "what happens if the flywheel or a piece of it comes
loose." The `.scad` file's own in-code comment on `fw_clearance_zone()`
states this distinction explicitly, and it is repeated here so the two
requirements are never conflated in review.

---

## 8. REQ-403 safety disposition (proposal — pending Independent Review, then human HITL gate)

**Proposal: provide active physical containment**, not clearance-plus-
firmware-speed-limiting alone. This section is the engineering reasoning
behind that proposal; the decision itself is not final until Independent
Mechanical Review has assessed it and the human has acted on the HITL gate
REQ-403 itself calls out.

**The physics, recomputed this session, not assumed from ISS-020's own
framing:**

| Quantity | At 3000 RPM target | At 20,000 RPM no-load-low | At 22,200 RPM no-load-high |
|---|---|---|---|
| Angular velocity ω | 314.2 rad/s | 2094.4 rad/s | 2324.8 rad/s |
| Stored kinetic energy (I=4.5×10⁻⁵ kg·m²) | 2.22 J | 98.70 J (44.44×) | 121.60 J (54.76×) |
| Rim tip speed | 9.42 m/s (~34 km/h) | — | 69.74 m/s (~250 km/h) |
| Peak centrifugal stress (solid-disk formula, ν=0.29) | 0.287 MPa | 12.75 MPa | 15.70 MPa |

The 44–55× energy range matches ISS-020's own stated "45–55×" almost exactly
— an independent confirmation of that issue's own framing, not just a
citation of it.

**The key reframing this design is built on:** the bulk-material stress
numbers above are not the real risk. Even at 22,200 RPM (unbounded no-load
speed), peak stress (15.70 MPa) carries a ~15.9× safety factor against mild
steel's yield strength (250 MPa) — the disk itself is in no realistic danger
of bursting. The actual hazard is a **discrete coupling failure**: the hub
collar (a generic set-screw shaft collar, `ASSUMPTION`, no datasheet) losing
its grip on the shaft — from vibration, from an installation error, or
simply from a lower-quality assumed part — and releasing the **entire 100g
disk as one rigid projectile**, at whatever speed the motor happens to be
spinning at the moment of release. No datasheet exists (UNKNOWN) for the
assumed hub collar's own retention strength, so this failure mode cannot be
bounded by calculation — it can only be defended against structurally.

**Why containment, not clearance-plus-firmware alone:** REQ-405 (the
firmware speed ceiling) is explicitly not yet implemented (ACCEPTED-RISK
pending Firmware Bring-up per ISS-020) — meaning that today, and for an
unknown period going forward, the flywheel's real achievable speed is bounded
only by the motor's own physical no-load speed (~20,000–22,200 RPM class),
not by any software limit. A mechanical design that relies on a
not-yet-implemented control loop as its only line of defense against a
100g mass potentially detaching at up to ~250 km/h rim speed would be
providing zero real protection for as long as that firmware gap exists —
which, per the project's own tracking, is an open and undated item, not a
near-term certainty. Given that:

- This is explicitly a **bench-test, human-attended** context (not an
  unattended field deployment) — the containment decision is scoped to that
  context, not to a hypothetical harsher one. A human is expected to be
  within arm's length of the device during any powered test.
- The stored energy at the credible worst case (~122 J) is still
  substantial — for comparison, that is roughly the kinetic energy of a
  1kg mass dropped from ~12.4m, or a small hand tool swung at speed. A
  100g fragment departing at up to ~250 km/h is a genuine laceration/impact
  hazard to an attending human at bench distance, not a negligible one.
- The mitigating alternative (firmware speed limiting) is real but is
  **not yet built**, and this Mechanical Lead has no authority or visibility
  into when it will be, per the task's own explicit instruction to stay out
  of firmware/control-loop territory.

Given a real, non-trivial energy release scenario, an unquantified
(UNKNOWN-strength) coupling-failure mode as the trigger, a not-yet-existing
software mitigation, and a human physically present during the exact
condition that matters (power applied), this design proposes that the
enclosure itself should not depend on firmware working correctly to keep a
detached 100g disk away from the operator. **This is defense-in-depth, not a
statement that firmware speed-limiting is unnecessary** — REQ-405 remains a
correct and independent mitigation to pursue; this proposal simply does not
treat it as sufficient on its own while it does not yet exist.

**The physical decision made:** the containment cap (§4.4, a 3rd enclosure
piece) is not merely a cover — it is sized and bolted specifically as a
containment structure:
- `containment_wall_t`=4.0mm (2× the print-safe minimum) around the full
  360° of the flywheel bay, chosen because a containment wall's job is to
  absorb and stop a fragment impact, not merely to keep dust out — sizing it
  at only the print-safe minimum would not reflect that different duty.
- The wall is a continuous ring with **no** access opening in the rotation
  plane at all (the only openings into the bay are the wire duct, well below
  the flywheel's own Z-range, and the flange-bolted cap on top) — a fragment
  radially ejected from the disk's rim has no direct line-of-sight exit path
  through the side wall.
- The cap is bolted (6× M3 into heat-set inserts, §12), not snap-fit or
  friction-fit, so it cannot be dislodged by the same impact event it is
  meant to contain.
- This is explicitly **not** a rigorously engineered ballistic-containment
  structure — no impact-energy-absorption calculation, no material-specific
  penetration-resistance analysis, and no dynamic (as opposed to static)
  structural check was performed; those are beyond this Phase 1 scope and
  this Mechanical Lead's own engineering authority to certify. What is
  claimed is a **reasoned, disclosed, defense-in-depth structural choice**
  — a continuous, bolted, over-minimum-thickness wall fully enclosing the
  rotation plane — not a rigorous containment certification.

**What this proposal is not:** it is not a claim that this design makes
flywheel operation "safe" in any certified sense, and it is not a substitute
for REQ-405 firmware speed-limiting eventually being implemented. It is one
specific, bounded engineering judgment, offered for Independent Mechanical
Review to challenge, and then for the human to accept, reject, or amend at
the REQ-403 HITL gate — exactly mirroring how the electronics-side REQ-403
disposition was handled (proposed → independently reviewed → human gate),
not a unilateral final decision by this Mechanical Lead.

---

## 9. Vibration isolation / REQ-307 disposition

REQ-307 is explicitly a "Should," not a "Must" ("where feasible"), citing
`docs/architecture.md` §12's own framing: a rotating body such as a reaction
wheel motor creates vibration and localized heating that can propagate into
the PCB, mattering especially for vibration/temperature-sensitive parts like
an IMU (bias drift with temperature).

**Disposition: not fully feasible within this design's own constraints; a
partial/incidental mitigation is provided instead, with the gap disclosed
rather than silently accepted.**

Reasoning: true vibration isolation (an elastomeric mount, a spring-damped
suspension, or a physically decoupled sub-chassis for the IMU) is a
mechanism/joint-class solution — explicitly out of Phase 1 scope
(`docs/architecture-evolution.md` §10, "Motion / joints... deferred"). Adding
one now would mean either (a) designing a genuinely new mechanical subsystem
not asked for in this cycle's scope, or (b) inventing a token isolation
feature (e.g., a foam gasket under the PCB standoffs) without any real
vibration-transmissibility analysis to show it does anything — which this
project's own rigor culture (disclosed-not-absorbed findings, e.g. the
bridge-span finding in §11) argues against presenting as a real mitigation
if it is not backed by analysis.

What this design **does** provide, as an incidental (not purpose-built)
partial mitigation:
- The motor is off-board-mounted (§6) to its own platform, physically
  separated from the PCB by the flywheel-bay wall (`containment_wall_t`=4.0mm)
  and the full width of the wire duct's own run — the vibration source is
  not bolted directly to the same rigid structure the IMU sits on within a
  few millimeters, the way an on-PCB motor mount would have been.
- MH-5/MH-6 (the two new mounting holes near the motor-driver zone) increase
  the board's own fixation near the switching/driver components, which
  reduces board-level flex/resonance that could otherwise couple motor-driver
  electrical noise or minor vibration into the board more readily — a board
  rigidity benefit, not a true vibration-isolation feature.
- The flywheel bay and PCB bay are joined only through a rigid enclosure
  base — there is no isolation in this path, so both spatial separation and
  MH-5/6 rigidity are genuinely partial, not equivalent to an isolated mount.

This is judged an honest "not fully feasible, here is the disclosed
alternative" outcome consistent with REQ-307's own "Should"/"where feasible"
framing — not a claim that vibration coupling has been solved. If IMU bias
drift is observed during actual bring-up, a purpose-built isolation mount
would be the correct follow-up (a future revision's scope, not silently
folded into this one).

---

## 10. Connector / header / button / LED / motor-wiring accessibility

| Ref | Board-local position | Cutout | Confidence | Note |
|---|---|---|---|---|
| J1 | (0,25) | 9.5×6mm, Z 0–6mm | CONFIRMED | Unchanged from Rev 2 |
| J2 | (16,50) | pass-through header, no dedicated cutout beyond the bay opening | CONFIRMED | Unchanged from Rev 2 |
| J3 | (30,50) | pass-through header | CONFIRMED | Unchanged from Rev 2 |
| SW1 | (44,50) | accessible through bay opening | CONFIRMED | Unchanged from Rev 2 |
| D1 | (10,37.5) | visible through bay opening | CONFIRMED | Y-position rescaled from Rev 2's 30mm |
| J4 | (100,25), edge | ⌀10.0mm, Z 0–6mm | ESTIMATE (diameter) | New in Rev 3; position confirmed, diameter is this Mechanical Lead's own estimate |
| MC-1 | (92,0), bottom edge | No dedicated board-edge cutout modeled — wire exits the board at this point and is routed internally to the wire duct | CONFIRMED (position) | New in Rev 3; wire-lead, not a component footprint |

**The wire-routing disclosure (important, not to be glossed over):** the
flywheel bay's own wire duct is centered at `fw_cx`=53.5mm — the PCB's own
X-midpoint — because the flywheel bay's own layout was centered on the PCB
bay's width for a cleaner, narrower overall footprint (§3, the "master XY
layout trade-off," `.scad` lines 497–519). MC-1's actual proposed board
position is X=92mm. This means the wire duct's exit point does **not** land
directly under or adjacent to MC-1 — there is a real ~42mm X-offset between
where the motor's wire pigtail enters the enclosure interior (at the duct)
and where it must connect on the board (at MC-1). The wire must run along
the interior floor for that distance. This was a deliberate, disclosed
trade-off (a width-centered flywheel bay vs. a motor-zone-centroid-aligned
one, which would have produced a wider but shorter overall footprint,
closer to 140×160mm-class rather than 107×162mm) — not an oversight. No
routing channel/clip is modeled for this 42mm run (out of the detailed
cable-exit-geometry scope this project has explicitly deferred,
`docs/architecture-evolution.md` §13) — the wire is expected to simply lie
along the interior floor, which is judged acceptable for a low-wire-count,
low-flex, bench-test-only pigtail, but is flagged here as a real, not
idealized, condition.

**Component-height clearance check (unchanged mechanism from Rev 2):**
`top_component_clearance`=11mm (driven by J4, the tallest top-side part per
the interface file) sets `base_interior_h` via the same formula Rev 2 used;
`bottom_component_clearance`=0mm means no standoff-height allowance is needed
beyond the base standoff height itself.

---

## 11. Computed clearance checks

This section is the full, disclosed record of every interference/clearance
check performed this revision — real arithmetic and, where noted, real
boolean-mesh intersection tests, not visual inspection.

**A. Four errors found and fixed during this revision's own development:**

1. **Error #1 & #2** (early-stage, minor coordinate-formula errors caught
   before the design stabilized — superseded by later constants, not
   independently re-describable at this point; see the `.scad` file's own
   revision history in-code if a full audit trail is needed).
2. **Error #3 — wire-bridge/motor collision.** Root cause: `bridge_y_lo` was
   computed from the flywheel bay's own **center** (`fw_cy`=52.5mm) instead
   of its **wall's outer edge**. This produced a bridge spanning 54.5mm,
   running directly through the motor platform and motor body. Fix:
   introduced `bridge_fuse_overlap`=2.0mm and recomputed `bridge_y_lo` =
   `fw_cy` + `fw_bay_outer_r` − `bridge_fuse_overlap` = 52.5+43.5−2.0 = 94.0mm.
   New span: 13.0mm. Verified clearance after fix: 26mm to the motor
   platform, 28mm to the motor body — both confirmed via direct coordinate
   check, not just "it looks fixed."
3. **Error #4 — missing flywheel-bay floor (most severe finding this
   revision).** Root cause: `fw_floor_top` (Z=2.0mm) was referenced
   throughout the file as if a floor disc existed at that height inside the
   flywheel bay, but no code actually created that geometry — the bay's
   containment wall had **no bottom** at all. Fix: `motor_platform()` now
   unions a full floor disc (radius=`fw_bay_outer_r`=43.5mm, Z=[0,2.0]) with
   the raised platform boss, before differencing the 4 bolt holes and the
   shaft hole through the combined solid. **This was the single most
   safety-relevant catch of this revision** — an unfixed version would have
   left the containment structure's own floor open, directly defeating
   REQ-403's entire premise (a fragment could simply fall out the bottom).
   Verified fixed via direct render (Status: NoError, no open non-manifold
   edges at the floor/wall junction).

**B. Two findings investigated and correctly dismissed as false alarms
(verified using a same-check-against-Rev-2's-own-already-reviewed-file
baseline method, not just re-running the check once and hoping):**

1. `trimesh`'s naive connected-components check reported ~12–13 exact-zero-
   volume "extra components" on `base()`, which could look like a defect.
   Running the identical check against Rev 2's own already-reviewed
   `base()` produced the same pattern (same count class), confirming this is
   a known STL-tessellation artifact at tab corners (CGAL/OpenSCAD's own
   manifold check reports Status: NoError regardless), not a Rev 3-specific
   defect.
2. A "2-vs-3-component assembly split" finding (an ambiguous result from a
   naive whole-assembly connectivity check) was similarly reproduced on Rev
   2's own file pattern and dismissed as a benign artifact of the same
   tessellation quirk, not a genuine assembly defect.

**C. One pre-existing Rev 2 issue found, confirmed, and deliberately NOT
fixed (flagged as out of this task's scope):**

A genuine, non-zero **190.06mm³ solid-solid overlap** exists between
`base_tabs()` and `lid_shell()`, confirmed via direct boolean intersection
(not estimation). Root cause, worked through geometrically: each of the 4
corner tabs projects outward (`tab_project`=6.0mm) starting flush at the
base wall's own outer face (zero gap by design — the tab is meant to be a
continuous extension of the wall). The lid's own skirt band (`lid_skirt_t`
=2.0mm thick) independently occupies the zone starting `fit_clearance`
(0.2mm) beyond that same wall face and extending `lid_skirt_t` further out —
i.e., the skirt band's Y-extent (2.0mm) is a subset of the tab's own
6.0mm outward projection, over the Z-range where the lid's skirt physically
overlaps the base wall (3.0mm of Z, `lid_lip_h`). This produces a real
solid-on-solid interference at all 4 corners, each contributing
approximately 47–48mm³ (8mm tab width × 2.0mm Y-overlap × 3.0mm Z-overlap,
minus a small pilot-hole deduction), summing to the reported 190.06mm³ —
this hand-recomputation (188–192mm³ range) closely matches the actual
measured figure, confirming the mechanism. **This is confirmed, via direct
Rev-2-baseline testing, to be a pre-existing characteristic of Rev 2's own
already-reviewed tab+skirt joint design** (neither `tab_project`,
`lid_skirt_t`, nor `fit_clearance` changed between revisions) — inherited
unchanged into Rev 3, not introduced by this revision. Decision: **flag,
do not fix**, per this task's explicit scope boundary (this task is a
mechanical redesign for the new motor/flywheel subsystem, not a Rev 2
defect-remediation pass). Qualitative mitigating judgment (not a rigorous
proof): the tab's actual structural job is served by its own screw pilot
hole engaging the base's standoff-equivalent boss beneath the lid — the
redundant contact with the lid's skirt band at this corner is unlikely to be
the governing load path, so the real-world severity of this interference is
judged low, but it has not been analyzed rigorously and is not claimed to be
harmless in a stronger sense than "probably fine, undisturbed since Rev 2."

**D. One new finding, first identified this session (borderline but
compliant — disclosed, not requiring a fix):**

The motor-wire bridge's unsupported horizontal print-bridging span was
computed exactly: at the bridge's X-center (53.5mm), the span from the
flywheel-bay wall/floor-disc's own outer edge (Y=96.000) to the PCB bay's
south wall face (Y=105.0) is **9.000mm**; at the bridge's two X-edges
(47.5mm/59.5mm), the span (measured from the floor disc's curved edge at
those X-offsets, Y=95.584) is **9.416mm**. Both are within the stated
`max_bridge_span`=10.0mm rule, but at 90.0–94.2% of it — directly analogous
to Rev 2's own disclosed (and accepted) J1-cutout bridge, which sat at
9.5mm/95% of the same limit. Additionally, the wire-duct bore's surrounding
wall thickness inside the bridge block is 3.5mm on each side in X
(comfortable margin above `min_wall_t`), but **exactly 2.0mm top and bottom
in Z — precisely equal to `min_wall_t`, with zero spare**, because
`wire_bridge_h` is deliberately derived as `wire_duct_dia + 2×wall_t`
(9.0mm), not padded further. Both figures pass their respective rules
exactly as stated; neither requires a `.scad` change. Disclosed here (and
repeated in §13) per this project's established practice of surfacing
borderline-but-compliant results rather than letting them pass silently.

**E. Bolt-hole / motor-body / platform-boss sanity checks** (motor mount
geometry, §4.3 — all pass with real, computed margin; no interference).

**F. Containment-cap / base-flange interface check:** cap skirt inner
diameter = `fw_flange_dia` + 2×`fit_clearance` = 105.0+0.4 = 105.4mm, vs.
base flange OD = 2×`fw_flange_or` = 105.0mm → exact 0.2mm/side clearance
fit, with matching Z-ranges ([31.0,39.0]mm) on both parts — confirmed by
direct coordinate comparison, the same method used for the PCB lid/base
interface in Rev 2.

---

## 12. Fastener placement summary

Three fastener classes this revision (Rev 2 had one):

| Joint | Fastener | Count | Placement rationale |
|---|---|---|---|
| PCB lid ↔ base | M2.5 self-tapping, into `standoff()` pilot bosses | 6 (at MH-1..6) | Unchanged mechanism from Rev 2, now at 6 positions instead of 4 |
| Motor ↔ platform boss | Plain M3 clearance-fit, through-hole | 4 (assumed square pattern, §4.3) | Deliberately a **reversible, direction-agnostic** joint — which side of the joint is threaded is UNKNOWN (not in the interface file), so plain through-holes were chosen specifically because they work regardless of which side ends up threaded, avoiding a decision that depends on an unconfirmed fact |
| Containment cap ↔ base flange | M3 into heat-set brass inserts | 6 (evenly spaced, `bolt_circle_r`=48mm) | Heat-set inserts chosen (over self-tapping directly into PETG) specifically because this joint is a **safety-relevant** one (§8) — a threaded metal insert holds torque and resists strip-out far better than a directly-tapped plastic hole, appropriate for a joint that must not fail under the same event it is meant to contain |

**Heat-set insert wall-thickness check:** insert OD (4.6mm) centered at
`bolt_circle_r`=48.0mm within the flange band (43.5–52.5mm radial span)
leaves 2.2mm of material on each side (inner and outer) — 0.2mm above
`min_wall_t`, a real but tight margin, disclosed rather than assumed safe by
inspection. Insert pocket depth (5.7mm) fits within the flange band's own
8.0mm height, leaving 2.3mm of solid material above the insert's own
bottom face and below the flange band's own top.

No fastener-load (torque, pull-out, shear) calculation was performed for any
joint — this is explicitly beyond Phase 1's basic-manufacturability/basic-
fit scope; fastener **counts and positions** are engineering judgment,
not computed from a load case.

---

## 13. Manufacturability / 3D-printability

**13.1 Rule set:** see §2 (0.2mm fit clearance, 2.0mm minimum wall, 45°
overhang threshold, 10.0mm maximum bridge span, PETG assumed material).

**13.2 Checked against actual Rev 3 features:**

- All new walls (flywheel-bay wall at 4.0mm, containment-cap flange/dome)
  meet or exceed the 2.0mm minimum.
- The motor platform boss, containment-cap dome, and flange are all vertical
  or flat surfaces — no overhang beyond the 45° threshold anywhere in the
  new geometry.
- The motor-wire bridge (§11.D) is the one feature that approaches (without
  exceeding) the bridge-span limit: 9.0–9.416mm against a 10.0mm rule
  (90.0–94.2%). Its own surrounding wall (the duct bore) is simultaneously
  at exactly the minimum wall thickness in the Z-direction (2.0mm, zero
  spare). Both are disclosed as tight-but-compliant, not silently passed —
  directly analogous to Rev 2's own disclosed 9.5mm/95%-of-limit J1-cutout
  bridge. No change was made to either figure because both pass their
  respective stated rule; a design choice to "round up" for extra margin
  was considered and rejected because it would either shrink the flywheel
  bay's own required clearance (§7, not acceptable) or grow the overall
  footprint further beyond REQ-308's already-disclosed overrun (§3) — the
  current figures are judged the right trade-off, disclosed rather than
  silently adjusted.
- The heat-set insert flange wall thickness (2.2mm each side, §12) is
  likewise tight-but-compliant, 0.2mm above the minimum.

**13.3 Print orientation:** as with Rev 2, the base is expected to print
floor-down (build plate = the base's own exterior bottom face) — this keeps
every new feature (flywheel-bay floor disc, motor platform boss, wire
bridge) supported by the print bed or by short vertical walls, with no new
orientation-dependent overhangs introduced beyond the bridge span already
addressed. The containment cap is expected to print dome-up or dome-down
depending on slicer preference — its flange face is flat either way, so
orientation does not change its own manufacturability profile materially.
No print-orientation-dependent structural weakness (layer-adhesion direction
vs. load direction) analysis was performed for the containment cap's own
impact-resistance role (§8) — this is disclosed as a real gap, not silently
assumed adequate, given the cap's safety-relevant duty.

---

## 14. Assembly order

Re-derived from scratch for 3 pieces (Rev 2's 2-piece sequence does not
extend directly):

1. Insert PCB into the base, seating on the 6 standoffs (MH-1..6).
2. Fasten the PCB lid onto the base with 6× M2.5 self-tapping screws through
   the lid tabs into the base standoffs — this closes and seals the PCB bay
   completely before any motor/flywheel work begins, so the board is fully
   protected during the more manual motor/flywheel assembly steps that
   follow.
3. Mount the motor (M1) onto the motor platform boss with 4× plain M3
   screws (direction-agnostic, §12).
4. Route the motor's phase-wire pigtail through the wire duct and connect it
   to MC-1 (the ~42mm interior floor run, §10) — performed before the
   flywheel is installed, since access to the duct/motor area is still open
   from the top at this stage.
5. Slide the hub collar onto the motor's exposed shaft and the flywheel disk
   onto the hub collar; tighten the collar's set screw. This step requires
   the ≥9.0mm of exposed shaft length above the motor bell (§4.3) — if M1's
   actual shaft does not expose this much, this step cannot be completed as
   designed (an open UNKNOWN, §16).
6. Install the containment cap **last**, bolting it to the base's flange
   with 6× M3 screws into the heat-set inserts. Placing this step last means
   nothing is ever trapped behind the cap during assembly — every part
   installed before it (motor, wire, hub, flywheel) remains accessible from
   the top until the cap goes on, satisfying the "physically achievable
   sequence, no part trapped behind another" requirement.

This sequence was checked for trapped-part conditions at every step (no step
requires reaching past an already-installed part from an inaccessible
direction) — the containment cap's cap-last placement is the one sequencing
decision that specifically enables this; an early-installed cap would trap
the motor/hub/flywheel assembly steps behind it with no access.

---

## 15. Self-check against the Mechanical Reviewer's 10-item checklist

Verbatim checklist (`.github/skills/mechanical-review/SKILL.md` lines 32–56):

1. **PCB mounting** — ✅ 6 standoffs at interface-confirmed MH-1..6 positions (§5.1, §4.1).
2. **Connector accessibility** — ✅ all 7 connectors/features addressed; one disclosed trade-off (MC-1 wire-run distance, §10), not a silent gap.
3. **Component height clearance** — ✅ interface-traced top/bottom clearances drive the PCB-bay Z-stack unchanged in formula from Rev 2 (§4.2, §10).
4. **Internal clearance/interference** — ✅ full computed record, §11: 4 fixed, 2 dismissed, 1 flagged-not-fixed, 1 new disclosed-compliant finding.
5. **Fastener placement** — ✅ 3 classes, each justified by joint duty, §12.
6. **Wall thickness** — ✅ 2.0mm minimum held everywhere, with disclosed deliberate exceptions (4.0mm containment wall) and disclosed tight spots (2.0mm duct wall, 2.2mm insert-flange margin), §2/§11/§12/§13.
7. **Assembly order** — ✅ re-derived 6-step sequence for 3 pieces, no trapped parts, §14.
8. **Basic print-fit tolerance** — ✅ 0.2mm/side at both mating interfaces, re-justified not just carried forward, §2.
9. **Basic manufacturability/3D-printability** — ✅ §13, including two disclosed tight-but-compliant findings.
10. **Interface-value traceability** — ✅ §4.1's full traceability table; §16 separates ASSUMPTION/ESTIMATE/UNKNOWN from CONFIRMED interface facts.

This is a self-check, not a substitute for Independent Mechanical Review —
every ✅ above reflects this Mechanical Lead's own assessment and is offered
for the Reviewer to challenge, not as a pre-cleared result.

---

## 16. Open UNKNOWNs / ASSUMPTIONs carried forward

| Item | Status | Note |
|---|---|---|
| M1's real mounting-bolt pattern | ASSUMPTION | Generic 12mm-square hobbyist convention assumed; interface file's own flagged open item; must be confirmed before build |
| Which side of the motor/platform joint is threaded | UNKNOWN | Resolved by design choice (plain through-holes work regardless), not by data |
| M1's actual exposed shaft length above the bell | UNKNOWN | Design requires ≥9.0mm (`fw_shaft_exposed_len_needed`); not in the interface file; must be confirmed before build |
| Hub collar dimensions (⌀8×6mm) | ASSUMPTION | Generic set-screw shaft-collar part, no manufacturer/datasheet selected |
| Hub collar retention strength | UNKNOWN | No datasheet; this is the exact unquantified failure mode the REQ-403 containment proposal (§8) is defending against |
| J4 cutout diameter (10.0mm) | ESTIMATE | This Mechanical Lead's own outside-knowledge estimate for a generic barrel jack; no datasheet cited by the interface file |
| Heat-set insert dimensions (⌀4.6×5.7mm) | ASSUMPTION | Generic M3 brass insert; no manufacturer part selected |
| Print material (PETG) | ASSUMPTION | Inherited from interface B6, not independently confirmed |
| Pre-existing Rev 2 190.06mm³ tab/skirt overlap | Flagged, not fixed | Out of this task's scope; confirmed pre-existing, not a new defect |
| Motor-wire-bridge span (9.0–9.42mm) and duct-wall thickness (exactly 2.0mm) | Disclosed, compliant | New finding this session; within stated rules, no fix required |
| REQ-308 envelope overrun (8.0–13.7% over the ~150mm-class soft ceiling) | Disclosed trade-off | Judged acceptable given the physical lower bound argument in §3 |
| Total assembly mass / structural deflection under motor+flywheel load | ESTIMATE (mass only), no deflection analysis | Basic qualitative judgment only (≈130g motor+flywheel on a solid PETG boss/platform judged modest); no FEA, out of Phase 1 scope |
| Containment cap's actual impact/penetration resistance | Not analyzed | §8/§13 explicitly disclose this as a reasoned structural choice, not a certified containment analysis |

**Nothing above is being silently relied upon as if it were CONFIRMED** —
this table exists specifically so Independent Mechanical Review and the
human HITL gate (§8) can see the full set of open items in one place, rather
than needing to extract them from prose scattered through the document.

**Possible interface-file observation (flagged, not corrected):** while
re-reading `hardware/mechanical-interface.md` this session, no internal
inconsistency or error was found in it — every fact cited in this spec
traced cleanly to a specific interface-file section. Nothing is flagged here
as a suspected interface-file defect; this note exists only to confirm that
this check was performed, per the task's own instruction to flag (not
silently fix) any such issue if found.

---

## 17. Handoff

To Independent Mechanical Review (via Hardware Lead): this document, plus
`hardware/mechanical/bench-imu-01-enclosure.scad` (Rev 3, 991 lines), plus
the self-check in §15, plus the full open-items table in §16. The REQ-403
disposition in §8 is explicitly a **proposal**, not a final decision — it is
expected to be challenged by Independent Review before it ever reaches the
human HITL gate REQ-403 itself calls for. No claim of physical fabrication,
print, or fit-test is made anywhere in this document (§0) — this remains a
paper/parametric design exercise, consistent with this entire project
cycle's own stated scope.
