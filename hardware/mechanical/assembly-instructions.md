# Bench-IMU-01 — Assembly Instructions (Rev 3 + Rev 4/4.1, Mechanical scope)

## 0. Scope, status, and how to use this document

This is a **build procedure for an already Design-Complete mechanical
design** — Bench-IMU-01 Rev 3 (original enclosure) plus Rev 4/4.1 (the
free-rotation support mechanism, `validation/change-log.md` ECO-029
through ECO-031, mechanical-scope Design Complete **GRANTED**). It does
**not** redesign, resize, or reinterpret any dimension — every step below
is derived from the assembly-order analyses already on record in
`hardware/mechanical/bench-imu-01-dimensional-spec.md` §14 (Rev 3, 6
steps) and §18.9 (Rev 4 addendum, steps 7–10), extended here only to add
the physical build detail (fastener call-outs, tools, real part
cross-references) those sections assumed a reader already had. Where this
document adds a judgment call not explicit in the source, it is marked
`ASSUMPTION` with its reasoning, per this project's own convention
(`.github/instructions/mechanical-design.instructions.md`).

**Companion visuals**: `hardware/mechanical/drawings/` — 2D orthographic
views of each part (`drawings/2d/`) and an exploded assembly view
(`drawings/exploded/bench-imu-01-exploded-view.png`). See
`drawings/README.md` for how those were generated.

**This document does not re-open, re-verify, or dispute any prior
Mechanical Reviewer finding.** It restates existing dispositions (§1
below) for the benefit of whoever is physically building the rig, who may
not have read the full validation history.

## 1. Safety notices — read before starting

Two safety-relevant dispositions apply to this build. Both are **human
Chief-Engineer ACCEPTED-RISK, defense-in-depth mitigations — neither is a
proven-adequate or complete solution.** Do not oversell either to whoever
operates the finished rig.

1. **Flywheel containment (REQ-403 / `validation/open-issues.md`
   `MISS-016`, Rev 3, ECO-024/025).** The containment wall
   (`fw_bay_wall()`, part of piece 1) and the containment cap (piece 3)
   are sized as a defense-in-depth measure only. The project's own bounded
   hand-calculation (`bench-imu-01-dimensional-spec.md` §8.1) found the
   wall's local material can absorb only a fraction of the disclosed
   credible worst-case hub-collar-release energy (≈156.44 J at ≈79.11 m/s
   rim speed) — **the wall is not shown to fully contain that event.**
   Build and use this rig accordingly: human-attended operation only
   (REQ-205), no bystanders directly over the flywheel bay during
   spin-tests, and treat REQ-405's firmware speed ceiling (a separate,
   Firmware-side mitigation, not built here) as load-bearing, not optional.
2. **Rotating-overhang pinch hazard (REQ-407(b) / `MISS-023`, Rev 4/4.1,
   ECO-030/031).** The rotating assembly's farthest point sweeps a
   **126.424 mm** radius from the bearing axis. The pinch guard (piece 5,
   the 4-quadrant ring) only covers the **60.0–115.0 mm** band — **≈77.7%
   of the true hazard band by area**, leaving an explicit **11.4 mm
   residual gap at the outer, highest-tangential-velocity edge**, and the
   guard itself is **not fastened down** (rests in place; could drift with
   handling). Do not present the guard as a complete pinch guard to an
   operator. Keep the desk area within the full 126.424 mm radius clear of
   fingers/loose objects while the platform is spinning, guard or no guard.

Both dispositions are recorded with full reasoning in `validation/open-issues.md`
(`MISS-016`, `MISS-023`) and `validation/change-log.md` (ECO-024/025,
ECO-030/031) — read those before deciding this build is fit for any
purpose beyond the bench/lab context REQ-201/REQ-205 already scope it to.

## 2. Parts and hardware list

### 2.1 Printed pieces

Material: PETG (`ASSUMPTION` — `bench-imu-01-enclosure.scad`'s own
`print_material`); see `hardware/mechanical/bench-imu-01-manufacturing-spec.md`
for the containment-relevant pieces' process recommendations.

| # | STL file | Print qty | What it is |
|---|---|---|---|
| 1 | `bench-imu-01-base-assembly.stl` | 1 | Rotating base: `base()` (Rev 3 enclosure) fused with `bmount_flange()` (bearing mount), `rotation_index_pointer()`, and `cable_anchor_tab()`×2 — **one combined print job**, not 4 separate pieces |
| 2 | `bench-imu-01-pcb-lid.stl` | 1 | PCB retention lid |
| 3 | `bench-imu-01-containment-cap.stl` | 1 | Flywheel bay containment cap — safety part, see §1.1 |
| 4 | `bench-imu-01-stand-plate.stl` | 1 | Stationary base plate; bolts to the bearing's bottom (stationary) plate; the piece that contacts the desk |
| 5 | `bench-imu-01-pinch-guard-quadrant.stl` | **4** | One 90° quadrant; print 4 copies — all 4 are geometrically identical (confirmed by direct module inspection, `validation/change-log.md` ECO-032; not re-verified here) — together they form the full guard ring, see §1.2 |

Full print-orientation/manufacturability notes: `hardware/mechanical/stl/README.md`.
**Note the internal-overhang caveat on piece 1** (needs slicer-generated
internal support material at the base/flange transition — a real,
disclosed, still-open manufacturability finding, not resolved by this
document).

### 2.2 Purchased / non-printed hardware

| Item | Source / part | Qty | Confidence |
|---|---|---|---|
| Lazy-susan bearing | BC Precision 4LS-3, ≈$13, 101.6 mm OD × 55.1 mm ID × 7.9 mm thick, 2× stamped steel plates + captive ball race (`datasheets/evidence-log.md` `DS-BRG-001`) | 1 | CONFIRMED (product-page spec) |
| Reaction-wheel motor (M1) | T-Motor MN2206-13 KV2000 (`bom/component-selection.md` Motor Approval; ≈$18.99 per `bom/bench-imu-01-fab-bom.csv` on the PCB branch) | 1 | CONFIRMED |
| Flywheel disk | ≈100 g, `fw_dia`=60.0 mm (`ASSUMPTION`, `bench-imu-01-enclosure.scad`) | 1 | ASSUMPTION — no specific catalog part cited anywhere in this repo; source your own disk matching this mass/diameter |
| Hub collar | Generic set-screw shaft-collar class part, ≈8.0 mm OD × 6.0 mm height (`fw_hub_collar_od`/`fw_hub_collar_h`, `ASSUMPTION`) | 1 | ASSUMPTION — not sourced to a specific vendor/MPN anywhere in this repo; its own retention strength is carried as `UNKNOWN` in the source design (§8 of the dimensional spec) — this is the actual open safety question behind §1.1, not a detail this document can close |
| Heat-set brass inserts | Ruthex RX-M3×5.7, M3, 5.7 mm length, ≈4.6 mm knurled OD (`DS-FAST-001`) | 6 | CONFIRMED (matches `heatset_od`/`heatset_len` almost exactly) |

## 3. Tools required

- Phillips/hex driver sized for M2.5 and M3 self-tapping/machine screws.
- Heat-set insert installation tool (soldering iron with insert tip, or a
  plain soldering iron tip used carefully) — for the 6 brass inserts in
  piece 1's flywheel-bay flange, **before** final assembly (inserts must be
  installed into the printed part, not improvised mid-build).
- Small hex/Allen key for the hub collar's set screw (size depends on the
  specific set-screw part sourced — `UNKNOWN`, see §2.2).
- Zip ties (2×, small) for the cable-anchor tabs.
- No torque wrench or specified torque value exists for any joint in this
  build — see §4.7.

## 4. Assembly procedure

Steps 4.1–4.4 below extend `bench-imu-01-dimensional-spec.md` §14's
existing 6-step Rev 3 sequence (unchanged in substance, just given fastener/
tooling detail here). Steps 4.5–4.7 extend §18.9's Rev 4 addendum
(steps 7–10 there), which explicitly treats the completed Rev 3
sub-assembly (§14's steps 1–6) **as one already-finished unit** before it
begins — so by the time you reach §4.5, piece 1 already carries the fully
closed PCB bay, motor, flywheel, and containment cap.

### 4.1 PCB bay (source §14 steps 1–2) — ⚠ PLACEHOLDER, board not yet built

> **This step cannot be physically performed yet.** Bench-IMU-01's PCB
> layout is still in progress on a separate, still-open branch
> (`ktanino10-bench-imu-01-rev3-pcb-layout`; `validation/open-issues.md`
> `ISS-036` unresolved) — no fabricated, populated board exists in this
> repository as of this writing. The steps below describe the *mechanical*
> interface as designed; do not attempt a real build of this step until a
> real board exists, and do not treat any PCB-side mounting-hole detail
> below as fabrication-confirmed.

1. Seat the PCB on piece 1's 6 internal standoffs (`mount_holes` MH-1..6:
   4 corners + 2 mid-edge motor-zone supports, all sized for M2.5
   clearance).
2. Place the PCB lid (piece 2) over the PCB bay, roof-up (its *installed*
   orientation — distinct from its print orientation, which is flipped
   roof-down for the printer). Fasten with **4× M2.5 self-tapping screws**
   through the lid's 4 corner tabs into piece 1's corner standoffs
   (`screw_len`=6.0 mm).
   - **Cross-reference note, not a design defect**: the source dimensional
     spec's own §14 step 2 text says "6× M2.5 self-tapping screws"; direct
     inspection of `bench-imu-01-enclosure.scad`'s own `tab_positions`
     array finds exactly **4** corner tab positions with their own
     dedicated screw holes, and the PCB branch's own
     `bom/bench-imu-01-fab-bom.csv` independently lists its `MH1` mounting
     hardware line item as **"quantity is 4 (one per mounting hole),
     MH1–MH4."** This document follows the 4-screw geometry actually
     modeled and independently cross-referenced; the "6" in the existing
     dimensional-spec prose is judged to be a minor, pre-existing
     documentation-precision gap (in the same low-severity class as this
     project's own already-logged `MISS-018`/`MISS-026`-style findings),
     not a new geometric defect — flagged here for transparency, not
     silently "corrected" in that other document.
   - The 2 mid-edge standoffs (MH-5/6) are PCB support/registration points
     only — no separate lid fastener lands there.

### 4.2 Motor mount (source §14 step 3)

3. Mount the motor (M1) onto piece 1's motor platform boss with **4× plain
   M3 screws**. Orientation: **direction-agnostic** (any rotational
   clocking of the motor works — `bench-imu-01-dimensional-spec.md` §12).

### 4.3 Motor wiring (source §14 step 4)

4. Route the motor's phase-wire pigtail through piece 1's wire duct and
   connect it to MC-1 (the PCB-side terminal block, ≈42 mm interior floor
   run). Do this **before** installing the flywheel — the duct/motor area
   is still open from the top at this stage.

### 4.4 Flywheel install + final enclosure closure (source §14 steps 5–6)

5. Slide the hub collar onto the motor's exposed shaft, then the flywheel
   disk onto the hub collar. Tighten the collar's set screw (no torque
   spec exists for this joint — see §4.7). Requires ≥9.0 mm of exposed
   motor shaft above the motor bell; if your actual M1 unit exposes less,
   this step cannot be completed as designed (an open, disclosed `UNKNOWN`
   in the source design, §16).
6. Install the containment cap (piece 3) **last** of the core-enclosure
   steps — bolt it to piece 1's flywheel-bay flange with **6× M3 screws**
   into the 6 heat-set brass inserts (§2.2; inserts must already be
   installed in the printed flange — see §3). Orientation: dome/disk-top
   face up, skirt down, slipping over the flange band (distinct from its
   print orientation, flipped dome-down for the printer). Placing this
   step last means nothing installed before it (motor, wire, hub, flywheel)
   is ever trapped behind the cap.

**At the end of §4.4, the Rev 3 core enclosure (piece 1 + 2 + 3, fully
populated) is a complete sub-assembly.** Steps 4.5–4.7 below treat it as
one unit, per `bench-imu-01-dimensional-spec.md` §18.9's own explicit
framing — everything below can also be prepared in parallel with §4.1–4.4,
since it does not depend on the PCB/motor/flywheel being installed yet.

### 4.5 Stationary side: stand plate + pinch guard

Source: §18.9 step 7, plus the Rev 4.1 pinch-guard placement.

7. Bolt the bearing's **bottom (stationary)** plate to the stand plate
   (piece 4) with **4× `#6` self-tapping screws** (2.8 mm pilot holes,
   ≈5.0 mm engagement depth into PETG). This fastener choice is an
   `ASSUMPTION` — a generic lazy-susan-hardware-class convention
   (`datasheets/evidence-log.md` `DS-BRG-007`), **not this specific
   bearing SKU's own confirmed hole pattern** (unpublished by the
   manufacturer). Verify hole positions against your actual bearing before
   drilling/screwing if they don't line up with the printed pilot holes.
   - **No torque calculation exists for this joint** — `validation/open-issues.md`
     `MISS-025` (OPEN, MEDIUM, non-blocking) explicitly flags that no
     fastener-load calc was ever performed for this joint, despite it
     carrying the full rotating-assembly weight across the rotation duty
     cycle. Snug, hand-tight is the only guidance this project can honestly
     give — do not over-torque into PETG.
8. Assemble the pinch guard (piece 5) around the stand plate at this same
   step: fit the 4 printed quadrants edge-to-edge to form the full ring,
   resting flush against the stand plate's outer edge (60.0 mm radius) —
   **not fastened to anything**, just placed. See §1.2 for what this guard
   does and does not protect against.

### 4.6 Rotating side: base assembly to bearing (source §18.9 step 8)

9. Flip the completed Rev 3 sub-assembly (§4.1–4.4's finished piece
   1+2+3) **upside-down** — a handling instruction, not a structural
   concern; nothing is trapped or blind at this step. Bolt the bearing's
   **top (rotating)** plate to the new mounting flange on the underside of
   piece 1, using the same **4× `#6` self-tapping screw** spec as §4.5
   step 7 (same `ASSUMPTION`/`DS-BRG-007` caveat applies).

### 4.7 Mating the two halves + cable routing

Source: §18.9 steps 9–10, plus the Rev 4.1 cable anchoring.

10. Rest/engage the two halves together via the bearing's own captive
    ball race — this is what physically unites the stationary stand-plate
    assembly (§4.5) with the rotating base assembly (§4.6). Not itself a
    blind or inaccessible fastening step.
11. Route the external tether (motor power / USB-UART service loop) through
    the coaxial bore (`bmount_flange_ir`/`stand_plate_ir` = 28.0 mm radius,
    continuous through flange → bearing → stand plate) just before or
    during this final stacking step.
12. Anchor the tether's external service loop to the two `cable_anchor_tab()`
    features (near J1 and J4, fused to piece 1's own wall) with a small
    zip-tie through each 3.0 mm through-hole — this is a **partial**
    strain-relief mitigation for REQ-407(c)/`MISS-024` (RESOLVED for
    REQ-113's explicit "several full turns" scope, §18.16), not a
    continuous/slip-ring solution. **Observe the 3-turn limit** before
    manually re-centering the platform (use `rotation_index_pointer()`,
    the small tab on piece 1's north wall, sighted against a fixed desk
    landmark, to track turn count) — specify at least a **2.5 m** external
    service-loop length.

**Build complete.** The rig is now ready for bring-up per
`validation/bring-up-procedure.md` (once a real PCB exists — see §4.1) and
the safety notices in §1 above.

## 5. Fastener summary table

| Joint | Fastener | Qty | Confidence | Torque | Source |
|---|---|---|---|---|---|
| PCB lid → base (corner tabs) | M2.5 self-tapping, 6.0 mm long | 4 | CONFIRMED (geometry) / see §4.1 count note | UNKNOWN | `.scad` `tab_positions`, `screw_len`; fab-bom.csv `MH1` |
| Motor (M1) → motor platform | M3, plain | 4 | ASSUMPTION | UNKNOWN | dimensional-spec §12 |
| Hub collar set screw | Generic set-screw, size unspecified | 1 | ASSUMPTION | UNKNOWN | `.scad` `fw_hub_collar_*` |
| Containment cap → base flange | M3, into Ruthex RX-M3×5.7 brass heat-set inserts | 6 | CONFIRMED (insert match) | UNKNOWN | `.scad` `n_cap_bolts`; `DS-FAST-001` |
| Bearing (stationary plate) → stand plate | `#6` self-tapping, 2.8 mm pilot, ≈5.0 mm depth | 4 | ASSUMPTION (bearing-class convention, not this SKU) | UNKNOWN — `MISS-025` OPEN | `.scad` `bmount_bolt_circle_r`/`bmount_pilot_*`; `DS-BRG-007` |
| Bearing (rotating plate) → mounting flange | Same spec as above | 4 | ASSUMPTION | UNKNOWN — `MISS-025` OPEN | Same |
| Pinch guard → (nothing) | None — rests in place | 0 | N/A | N/A | `.scad` `pinch_guard()` header comment |
| Cable anchor tabs | Zip-tie through 3.0 mm hole | 2 | ASSUMPTION | N/A | `.scad` `cable_anchor_hole_dia` |

**No torque value is specified anywhere in this project's source design
for any joint.** Where this table says `UNKNOWN`, that is a real, disclosed
gap (mirrors `MISS-025`), not an oversight of this document — hand-tighten
firmly but do not over-torque self-tapping joints into PETG.

## 6. Cross-references

- `hardware/mechanical/bench-imu-01-dimensional-spec.md` §14 (Rev 3
  assembly order), §18.9 (Rev 4 addendum), §18.12–§18.17 (Rev 4.1 pinch
  guard / cable anchor rationale).
- `hardware/mechanical/bench-imu-01-enclosure.scad` — source geometry for
  every dimension cited above.
- `hardware/mechanical/stl/README.md` — print orientation, qty, and
  manufacturability notes per piece.
- `hardware/mechanical/bench-imu-01-manufacturing-spec.md` — FDM process
  recommendations for the two REQ-403 safety-critical printed pieces.
- `hardware/mechanical-interface.md` Part C — bearing/free-rotation
  interface facts (C1–C9).
- `bom/component-selection.md` — Free-Rotation Support Mechanism section
  (bearing candidate comparison) and Motor/Motor Driver sections.
- `bom/bench-imu-01-fab-bom.csv` (on the separate, still-open
  `ktanino10-bench-imu-01-rev3-pcb-layout` branch — read-only reference,
  not merged) — PCB-side mounting-hardware line item (`MH1`).
- `validation/open-issues.md` `MISS-016`, `MISS-023`, `MISS-024`,
  `MISS-025` — full reasoning behind every disposition/caveat in this
  document.
- `validation/change-log.md` ECO-024/025 (REQ-403 disposition), ECO-029
  through ECO-031 (Rev 4/4.1 design + review + disposition), ECO-032 (STL
  export).

## 7. Open items this document does not resolve

- PCB not yet fabricated (§4.1) — placeholder only.
- Hub collar retention strength — `UNKNOWN`, the actual technical question
  behind the REQ-403 containment disposition (§1.1); this document cannot
  close it.
- Bearing-to-flange/stand-plate fastener load — no calculation exists
  (`MISS-025`, OPEN/MEDIUM); this document only reports the geometry as
  designed, it does not certify the joint.
- Bearing's own real mounting-hole pattern — unpublished by the
  manufacturer; the 4-hole/plate pattern used throughout is a generic
  bearing-class convention (`DS-BRG-007`), not a confirmed fact about this
  specific SKU. Verify against the physical part before drilling.
