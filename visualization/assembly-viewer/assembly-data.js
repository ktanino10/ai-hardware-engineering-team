/*
 * assembly-data.js — Real part list + layout for Bench-IMU-01's 3D assembly
 * viewer. Every dimension/role/source below is grounded in this repo's own
 * real files:
 *   - hardware/mechanical/assembly-instructions.md (assembly order, parts list)
 *   - hardware/mechanical/bench-imu-01-enclosure.scad (dimensional source of truth)
 *   - hardware/mechanical/stl/*.stl (real printed-part geometry, converted to
 *     OBJ for this viewer — same files used for the mechanical drawings)
 *   - bom/component-selection.md / bom/bench-imu-01-fab-bom.csv (purchased parts)
 * Laid out as an exploded stack (Y-up, mm) matching the real, already-reviewed
 * exploded-view order in hardware/mechanical/drawings/exploded/ — not an
 * arbitrary arrangement.
 *
 * sourceUpAxis:'z' — this project's OpenSCAD/STL export pipeline is Z-up
 * (see bench-imu-01-enclosure.scad's own documented GLOBAL frame: "Global
 * Z=0 is the base's external bottom face; +Z points toward the lid/cap"),
 * but this viewer's scene is Y-up (parts are stacked along Y, above).
 * Every mesh part sourced from that pipeline needs its Z-up geometry
 * converted to Y-up (assembly-render.js's applyAxisFix()) or it renders
 * with its real height on the wrong (horizontal) axis. The PCB mesh is
 * from a KiCad glTF/GLB export, already Y-up per the glTF spec, and is
 * deliberately NOT flagged.
 *
 * quadrant:N — this part's mesh is one physical segment, printed/molded N
 * times and assembled into one full radially-symmetric part (see the
 * Pinch Guard's own row below and export-pinch-guard-quadrant.scad's
 * "print x4 total" note) — assembly-render.js's buildRadialAssembly()
 * replicates the loaded segment N times around the vertical axis to
 * reconstruct the real assembled shape; it is not stored as N separate
 * meshes.
 *
 * ---- Additive fields below (Assemble/Explode + part-detail-modal pass) ----
 * Every field above this line is UNCHANGED from the original viewer — the
 * `y` field in particular keeps its original per-part VALUES (still used as
 * a relative-order signal), even though assembly-render.js now also reads
 * it for a different purpose (see that file's computeExplodedLayout()).
 *
 * stackGroup / stackIndex — real assembly adjacency, from
 * hardware/mechanical/assembly-instructions.md's own build sequence (§4.1-
 * §4.6), used ONLY by the new "assembled" contact-stack layout:
 *   'spine'  (StandPlate -> Bearing -> BaseAssembly, the shared column)
 *   'guard'  (PinchGuard — assembled "around the stand plate" per
 *             instructions §4.5 step 8, i.e. same height as StandPlate,
 *             not near the flywheel bay as its large radius might suggest)
 *   'pcbBay' (PCB -> PcbLid, rising from the spine's own top)
 *   'flywheelBay' (Motor -> HubCollar -> Flywheel -> ContainmentCap,
 *             rising from the spine's own top, on the OTHER side)
 * stackIndex orders parts bottom-to-top within their own group.
 *
 * cadModules — the REAL OpenSCAD module name(s) implementing this part in
 * bench-imu-01-enclosure.scad, confirmed by `grep -n "^module "` on that
 * file (not guessed), with the exact line number for a direct GitHub deep
 * link. `referenceOnly:true` marks a module that is a VISUALIZATION STAND-
 * IN for a purchased part (e.g. reference_motor_flywheel()), not that
 * part's own real design deliverable — confirmed via the drawing-helper
 * scripts' own header comments in hardware/mechanical/drawings/scad/.
 * cadFile — used instead of cadModules for the one part (PCB) with no
 * OpenSCAD module at all; points at its real KiCad source file.
 *
 * drawing2d — real front/side/top PNG filenames under
 * hardware/mechanical/drawings/2d/, confirmed via `ls` on that directory —
 * present for exactly 5 parts (PinchGuard, StandPlate, BaseAssembly,
 * PcbLid, ContainmentCap). Every other part deliberately has NO drawing2d
 * field; assembly-render.js shows an explicit, honest "N/A" disclosure
 * instead of a broken image.
 *
 * draftingSheet — real dimensioned drafting-sheet PDF/PNG (under
 * hardware/mechanical/drawings/drafting-sheets/) + the SCAD projection
 * script that generated it (under that directory's own scad/ subfolder),
 * confirmed present for only 3 of the 5 drawing2d parts (StandPlate,
 * PcbLid, ContainmentCap) — BaseAssembly and PinchGuard have none.
 *
 * datasheet — { file, officialUrl } for the 2 purchased parts that DO have
 * a real datasheet metadata record with a stated "Official URL" field
 * (Bearing, Motor) — read directly from those files, not fabricated.
 * HubCollar/Flywheel deliberately have no datasheet field: neither is
 * sourced to a specific vendor/MPN anywhere in this repo (their own
 * `source` field already discloses this; confirmed no match by grepping
 * datasheets/evidence-log.md for either part name).
 *
 * evidenceIds — [{id, line}] real rows in datasheets/evidence-log.md this
 * part's own purchase/spec claim can be traced to, with the real line
 * number for a direct GitHub deep link (`?plain=1#L<n>`, stable across
 * future appends since this is a strictly append-only log and each row is
 * one physical line). Motor's DS-MTR-017 is cross-referenced from its own
 * datasheet metadata record's "Used for Evidence IDs" list, not copied
 * from this file's own pre-existing `source` text (which cites
 * bom/component-selection.md instead) — disclosed in the modal, not
 * presented as if it were already here.
 */

// Real repo URL bases for outbound GitHub links. Mirrors
// visualization/dashboard/dashboard-live.js's own RAW_BASE constant
// exactly (same name, same value) — deliberately reusing that already-
// established convention rather than inventing a new one. Reason it
// exists at all (confirmed by reading that file, not assumed):
// .github/workflows/deploy-pages.yml uploads ONLY the visualization/
// folder to GitHub Pages, so a relative link like `../../hardware/...`
// would 404 once deployed even though it resolves fine when testing
// locally from a repo-root static server. RAW_BASE serves actual file
// bytes (used for <img> src on 2D drawings/drafting-sheet PNGs); BLOB_BASE
// opens GitHub's own file viewer (used for "view source" links, PDFs, and
// evidence-log/datasheet links); TREE_BASE opens GitHub's own directory
// listing (used for the top-level "browse source" links).
export const RAW_BASE  = 'https://raw.githubusercontent.com/ktanino10/ai-hardware-engineering-team/main/';
export const BLOB_BASE = 'https://github.com/ktanino10/ai-hardware-engineering-team/blob/main/';
export const TREE_BASE = 'https://github.com/ktanino10/ai-hardware-engineering-team/tree/main/';

// Real, cited (not arbitrary) horizontal half-separation, in mm, between
// the PCB-bay branch (PCB, PcbLid) and the flywheel-bay branch (Motor,
// HubCollar, Flywheel, ContainmentCap) in the new "assembled" layout only
// (assembly-render.js's computeAssembledLayout()) — without it, both
// branches would render stacked directly on top of one another, which
// looks wrong (on the real object they sit side by side in two separate
// bays). Derived from bench-imu-01-enclosure.scad's own GLOBAL-frame
// variables, not guessed: fw_cy=52.5mm (flywheel-bay center, line ~731)
// vs. pcb_bay_y0=105.0mm + base_outer_y=102.0mm => PCB-bay center
// ~=156.0mm (line ~735/400) — half of that ~103.5mm gap, rounded.
// Disclosed ASSUMPTION (see README "Known limitations"): BaseAssembly's
// own measured-mesh bounding-box center (computed at runtime from the real
// OBJ) is treated as coincident with the true SCAD-frame midpoint between
// those two bay centers — a simplification, not a byte-exact derivation
// of every intervening tab/pointer offset.
export const ASSEMBLED_LAYOUT = { baySeparationHalfZ: 52 };

export const PARTS = [
  // ---- 3D-printed parts (real OBJ geometry, converted from the real STL files) ----
  { id:'PinchGuard', mesh:'bench-imu-01-pinch-guard-quadrant.obj', quadrant:4, sourceUpAxis:'z',
    category:'print3d', y:0,
    name:'Pinch Guard (×4 quadrants)', ref:'—',
    dims:'176.3mm outer radius ring (was 115mm), 4× identical 90° quadrants',
    role:'Mitigation for the flywheel-bay pinch hazard (REQ-407(b)). All 4 quadrants are geometrically identical (confirmed by direct module inspection, ECO-032). REV 5 history: coverage vs. the rotating hazard band dropped from ~77.7% to ~35.0% as a side effect of the Bench-IMU-01 board resize (MISS-034) growing the rotating envelope — MISS-023 re-opened pending fresh human review (validation/open-issues.md). A real, pre-existing quadrant-cutting geometry bug (MISS-036, unrelated to the resize) was found and fixed the same pass — this mesh has the correct, full-intended material. **RESOLVED, same session**: the human Chief Engineer directly decided full geometric closure ("完全カバーを選んでください") — pinch_guard_or grown 115.0mm to 176.3mm, now covering 100% of the hazard band with 0.0mm residual gap, re-verified via direct boolean CSG non-overlap with the complete rotating envelope. Mass grew 570.6g to 1629.080g as a direct, human-decided consequence.',
    source:'3D-printed, PETG (assumption). STL: bench-imu-01-pinch-guard-quadrant.stl',
    stackGroup:'guard', stackIndex:0,
    cadModules:[{ name:'pinch_guard(quadrant = -1)', line:1916 }],
    drawing2d:{ front:'pinch-guard-front.png', side:'pinch-guard-side.png', top:'pinch-guard-top.png' } },
  { id:'StandPlate', mesh:'bench-imu-01-stand-plate.obj', sourceUpAxis:'z',
    category:'print3d', y:28,
    name:'Stand Plate', ref:'—',
    dims:'120 × 120 × 6mm (stand_plate_or=60mm, stand_plate_t=6mm)',
    role:'Stationary base — the piece that actually contacts the desk. Bolts to the bearing\'s stationary (bottom) plate. The system\'s true mechanical ground plane.',
    source:'3D-printed, PETG (assumption). STL: bench-imu-01-stand-plate.stl',
    stackGroup:'spine', stackIndex:0,
    cadModules:[{ name:'stand_plate()', line:1871 }],
    drawing2d:{ front:'stand-plate-front.png', side:'stand-plate-side.png', top:'stand-plate-top.png' },
    draftingSheet:{ pdf:'bench-imu-01-stand-plate-drafting-sheet.pdf', png:'bench-imu-01-stand-plate-drafting-sheet.png', scad:'projection-stand-plate.scad' } },
  { id:'Bearing', mesh:null, primitive:'cylinder', dOuter:101.6, dInner:55.1, h:7.9,
    category:'purchase', y:49,
    name:'Bearing: BC Precision 4LS-3', ref:'—',
    dims:'101.6mm OD × 55.1mm ID × 7.9mm thick',
    role:'Lazy-susan bearing — lets the base assembly (and everything mounted to it) rotate freely relative to the stationary stand plate. Reference-only in the printed BOM (not printed/exported).',
    source:'Purchased, ≈$13. datasheets/evidence-log.md DS-BRG-001',
    stackGroup:'spine', stackIndex:1,
    cadModules:[{ name:'reference_bearing()', line:2160, referenceOnly:true, referenceNote:'visualization stand-in only (a single simplified cylinder) — not this part\'s own real design, since it is purchased, not printed' }],
    datasheet:{ file:'datasheets/bcprecision_4ls-3-lazy-susan-turntable-bearing_web-product-page.md', officialUrl:'https://www.bcprecision.com/products/4-lazy-susan-turntable-bearings' },
    evidenceIds:[{ id:'DS-BRG-001', line:353 }] },
  { id:'BaseAssembly', mesh:'bench-imu-01-base-assembly.obj', sourceUpAxis:'z',
    category:'print3d', y:95,
    name:'Base Assembly', ref:'—',
    dims:'173 × 213 × 51mm bounding box (combined single print)',
    role:'Rotating base: base() fused with the bearing-mount flange, rotation-index pointer, and 2× cable-anchor tabs — one combined print job, not 4 separate pieces. Houses the PCB bay above and mounts to the bearing below.',
    source:'3D-printed, PETG (assumption). STL: bench-imu-01-base-assembly.stl. Note: this piece has a disclosed, still-open manufacturability caveat (internal overhang at the base/flange transition needs slicer support).',
    stackGroup:'spine', stackIndex:2,
    cadModules:[
      { name:'base()', line:1749 },
      { name:'bmount_flange()', line:1810 },
      { name:'rotation_index_pointer()', line:2040 },
      { name:'cable_anchor_tab(is_j4 = false)', line:2071 },
      { name:'cable_anchor_tab(is_j4 = true)', line:2071 } ],
    drawing2d:{ front:'base-assembly-front.png', side:'base-assembly-side.png', top:'base-assembly-top.png' } },
  { id:'PCB', mesh:'PCB_BenchIMU01.obj',
    category:'print3d', y:134, purchaseNote:false,
    name:'PCB — Bench-IMU-01 Rev 3', ref:'—',
    dims:'150 × 95mm, real KiCad board outline (exact match to hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb)',
    role:'STM32G031 MCU + BMI270 IMU + DRV10983 motor driver + TPS26631 eFuse supervisor. See the Circuit &amp; Current-Flow Viewer for full net-by-net detail.',
    source:'Real KiCad PCB export (kicad-cli pcb export glb), not a placeholder board outline.',
    stackGroup:'pcbBay', stackIndex:0,
    cadFile:{ label:'Real KiCad PCB source (no OpenSCAD module — this part is not modeled in bench-imu-01-enclosure.scad at all)', path:'hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb' } },
  { id:'PcbLid', mesh:'bench-imu-01-pcb-lid.obj', sourceUpAxis:'z',
    category:'print3d', y:158,
    name:'PCB Lid', ref:'—',
    dims:'161.4 × 114.8 × 5mm',
    role:'PCB retention lid — closes over the PCB bay. Secured with 4× M2.5 self-tap screws into the base assembly\'s corner tabs. REV 5 (MISS-034): resized to actually exceed the real 150×95mm PCB\'s own footprint in both X and Y, as a lid must — this is the exact PCB-vs-lid physical-fit mismatch that originally exposed MISS-034 in this viewer (the PCB used to be wider than its own lid).',
    source:'3D-printed, PETG (assumption). STL: bench-imu-01-pcb-lid.stl',
    stackGroup:'pcbBay', stackIndex:1,
    cadModules:[{ name:'pcb_lid()', line:1543 }],
    drawing2d:{ front:'pcb-lid-front.png', side:'pcb-lid-side.png', top:'pcb-lid-top.png' },
    draftingSheet:{ pdf:'bench-imu-01-pcb-lid-drafting-sheet.pdf', png:'bench-imu-01-pcb-lid-drafting-sheet.png', scad:'projection-pcb-lid.scad' } },
  { id:'Motor', mesh:null, primitive:'cylinder', dOuter:27.5, h:22,
    category:'purchase', y:178,
    name:'Motor: T-Motor MN2206-13 KV2000', ref:'M1',
    dims:'≈27.5mm dia × 22mm (estimated envelope)',
    role:'Sensorless 3-phase BLDC outrunner — spins the reaction-wheel flywheel. Paired with the TI DRV10983 sensorless driver on the PCB. Recommended candidate after a 4-way motor-type comparison (brushed DC / sensored BLDC / sensorless BLDC / stepper) — see bom/component-selection.md.',
    source:'Purchased, ≈$18.99, T-Motor/RC drone shops. bom/component-selection.md Motor Approval.',
    stackGroup:'flywheelBay', stackIndex:0,
    cadModules:[{ name:'reference_motor_flywheel()', line:2137, referenceOnly:true, referenceNote:'visualization stand-in only (motor-body primitive of this shared module, per assembled-reference-motor-body.scad\'s own header comment) — not this part\'s own real design, since it is purchased, not printed' }],
    datasheet:{ file:'datasheets/tmotor_mn2206-13-2000kv_rev-unknown.md', officialUrl:'https://uav-en.tmotor.com/Multirotor/Motors/navigato/' },
    evidenceIds:[{ id:'DS-MTR-017', line:235, note:'primary spec-table citation for this motor; several related rows (DS-MTR-018/079/080, etc.) also exist in the same log — this is one representative row, not the only one, cross-referenced from the motor\'s own datasheet metadata record rather than copied from this part\'s own `source` field above (which cites bom/component-selection.md instead)' }] },
  { id:'HubCollar', mesh:null, primitive:'cylinder', dOuter:8.0, h:6.0,
    category:'purchase', y:197,
    name:'Hub Collar', ref:'—',
    dims:'≈8.0mm OD × 6.0mm height (generic set-screw shaft collar)',
    role:'Couples the motor shaft to the flywheel disk. Its retention strength against the flywheel\'s spin loads is carried as an explicit UNKNOWN in the source dimensional spec — the actual open safety question behind the REQ-403 containment requirement.',
    source:'Purchased, generic set-screw shaft-collar class part — not sourced to a specific vendor/MPN anywhere in this repo (disclosed ASSUMPTION).',
    stackGroup:'flywheelBay', stackIndex:1,
    cadModules:[{ name:'reference_motor_flywheel()', line:2137, referenceOnly:true, referenceNote:'visualization stand-in only (hub-collar primitive of this shared module, per assembled-reference-flywheel-rotor.scad\'s own header comment) — no dedicated hub-collar module exists anywhere in bench-imu-01-enclosure.scad' }] },
  { id:'Flywheel', mesh:null, primitive:'disk', d:60.0, h:4.5,
    category:'purchase', y:208,
    name:'Flywheel Disk', ref:'—',
    dims:'60.0mm dia × 4.5mm thick, ≈100g (mild steel density assumption)',
    role:'The spinning reaction mass. Its momentum exchange with the enclosure is the entire point of this board — see the Circuit &amp; Current-Flow Viewer\'s Mode 2/3 for how (and how not yet) it is actually controlled.',
    source:'Purchased — no specific catalog part cited anywhere in this repo (disclosed ASSUMPTION); source your own disk matching this mass/diameter.',
    stackGroup:'flywheelBay', stackIndex:2,
    cadModules:[{ name:'reference_motor_flywheel()', line:2137, referenceOnly:true, referenceNote:'visualization stand-in only (flywheel-disk primitive of this shared module, per assembled-reference-flywheel-rotor.scad\'s own header comment) — not this part\'s own real design, since it is purchased, not printed' }] },
  { id:'ContainmentCap', mesh:'bench-imu-01-containment-cap.obj', sourceUpAxis:'z',
    category:'print3d', y:220,
    name:'Containment Cap', ref:'—',
    dims:'109.4 × 109.4 × 12mm',
    role:'Flywheel-bay safety enclosure — installed LAST, per REQ-403. Secured with 6× M3 screws into heat-set brass inserts (Ruthex RX-M3×5.7). This part\'s own retention margin against a flywheel failure is tracked as ACCEPTED-RISK (ISS-036), not fully resolved.',
    source:'3D-printed, PETG (assumption). STL: bench-imu-01-containment-cap.stl',
    stackGroup:'flywheelBay', stackIndex:3,
    cadModules:[{ name:'containment_cap()', line:1768 }],
    drawing2d:{ front:'containment-cap-front.png', side:'containment-cap-side.png', top:'containment-cap-top.png' },
    draftingSheet:{ pdf:'bench-imu-01-containment-cap-drafting-sheet.pdf', png:'bench-imu-01-containment-cap-drafting-sheet.png', scad:'projection-containment-cap.scad' } },
];

// Screws — small purchased hardware, positioned near their real joints
// (approximate offsets from each parent part's center, matching the real
// fastener table in assembly-instructions.md §5, not arbitrary clutter).
export const SCREWS = [
  { group:'StandPlate', count:4, y:40, radius:42, dia:3.0, len:8, label:'M3 — bearing → stand plate' },
  { group:'PcbLid', count:4, y:150, radius:40, dia:2.2, len:6, label:'M2.5 self-tap — PCB lid → base corner tabs' },
  { group:'ContainmentCap', count:6, y:230, radius:48, dia:3.0, len:8, label:'M3 → Ruthex RX-M3×5.7 heat-set insert' },
];

// Seed camera VIEWING DIRECTION/ANGLE (not a literal fixed position/target
// any more — assembly-render.js's frameCameraToScene() computes the real
// combined bounding sphere of every loaded part at runtime and derives the
// actual distance/target from that, so the framing keeps working after any
// future part-geometry change instead of needing another manual re-tune).
// This value only supplies the direction from target to camera (i.e. the
// pleasant near-isometric look angle originally chosen), and is the
// fallback position/target if the runtime bounding-box computation ever
// comes back empty.
export const CAMERA_START = { pos:[330, 230, 420], target:[0, 108, 0] };
