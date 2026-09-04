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
 */

export const PARTS = [
  // ---- 3D-printed parts (real OBJ geometry, converted from the real STL files) ----
  { id:'PinchGuard', mesh:'bench-imu-01-pinch-guard-quadrant.obj', quadrant:4, sourceUpAxis:'z',
    category:'print3d', y:0,
    name:'Pinch Guard (×4 quadrants)', ref:'—',
    dims:'176.3mm outer radius ring (was 115mm), 4× identical 90° quadrants',
    role:'Mitigation for the flywheel-bay pinch hazard (REQ-407(b)). All 4 quadrants are geometrically identical (confirmed by direct module inspection, ECO-032). REV 5 history: coverage vs. the rotating hazard band dropped from ~77.7% to ~35.0% as a side effect of the Bench-IMU-01 board resize (MISS-034) growing the rotating envelope — MISS-023 re-opened pending fresh human review (validation/open-issues.md). A real, pre-existing quadrant-cutting geometry bug (MISS-036, unrelated to the resize) was found and fixed the same pass — this mesh has the correct, full-intended material. **RESOLVED, same session**: the human Chief Engineer directly decided full geometric closure ("完全カバーを選んでください") — pinch_guard_or grown 115.0mm to 176.3mm, now covering 100% of the hazard band with 0.0mm residual gap, re-verified via direct boolean CSG non-overlap with the complete rotating envelope. Mass grew 570.6g to 1629.080g as a direct, human-decided consequence.',
    source:'3D-printed, PETG (assumption). STL: bench-imu-01-pinch-guard-quadrant.stl' },
  { id:'StandPlate', mesh:'bench-imu-01-stand-plate.obj', sourceUpAxis:'z',
    category:'print3d', y:28,
    name:'Stand Plate', ref:'—',
    dims:'120 × 120 × 6mm (stand_plate_or=60mm, stand_plate_t=6mm)',
    role:'Stationary base — the piece that actually contacts the desk. Bolts to the bearing\'s stationary (bottom) plate. The system\'s true mechanical ground plane.',
    source:'3D-printed, PETG (assumption). STL: bench-imu-01-stand-plate.stl' },
  { id:'Bearing', mesh:null, primitive:'cylinder', dOuter:101.6, dInner:55.1, h:7.9,
    category:'purchase', y:49,
    name:'Bearing: BC Precision 4LS-3', ref:'—',
    dims:'101.6mm OD × 55.1mm ID × 7.9mm thick',
    role:'Lazy-susan bearing — lets the base assembly (and everything mounted to it) rotate freely relative to the stationary stand plate. Reference-only in the printed BOM (not printed/exported).',
    source:'Purchased, ≈$13. datasheets/evidence-log.md DS-BRG-001' },
  { id:'BaseAssembly', mesh:'bench-imu-01-base-assembly.obj', sourceUpAxis:'z',
    category:'print3d', y:95,
    name:'Base Assembly', ref:'—',
    dims:'173 × 213 × 51mm bounding box (combined single print)',
    role:'Rotating base: base() fused with the bearing-mount flange, rotation-index pointer, and 2× cable-anchor tabs — one combined print job, not 4 separate pieces. Houses the PCB bay above and mounts to the bearing below.',
    source:'3D-printed, PETG (assumption). STL: bench-imu-01-base-assembly.stl. Note: this piece has a disclosed, still-open manufacturability caveat (internal overhang at the base/flange transition needs slicer support).' },
  { id:'PCB', mesh:'PCB_BenchIMU01.obj',
    category:'print3d', y:134, purchaseNote:false,
    name:'PCB — Bench-IMU-01 Rev 3', ref:'—',
    dims:'150 × 95mm, real KiCad board outline (exact match to hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb)',
    role:'STM32G031 MCU + BMI270 IMU + DRV10983 motor driver + TPS26631 eFuse supervisor. See the Circuit &amp; Current-Flow Viewer for full net-by-net detail.',
    source:'Real KiCad PCB export (kicad-cli pcb export glb), not a placeholder board outline.' },
  { id:'PcbLid', mesh:'bench-imu-01-pcb-lid.obj', sourceUpAxis:'z',
    category:'print3d', y:158,
    name:'PCB Lid', ref:'—',
    dims:'161.4 × 114.8 × 5mm',
    role:'PCB retention lid — closes over the PCB bay. Secured with 4× M2.5 self-tap screws into the base assembly\'s corner tabs. REV 5 (MISS-034): resized to actually exceed the real 150×95mm PCB\'s own footprint in both X and Y, as a lid must — this is the exact PCB-vs-lid physical-fit mismatch that originally exposed MISS-034 in this viewer (the PCB used to be wider than its own lid).',
    source:'3D-printed, PETG (assumption). STL: bench-imu-01-pcb-lid.stl' },
  { id:'Motor', mesh:null, primitive:'cylinder', dOuter:27.5, h:22,
    category:'purchase', y:178,
    name:'Motor: T-Motor MN2206-13 KV2000', ref:'M1',
    dims:'≈27.5mm dia × 22mm (estimated envelope)',
    role:'Sensorless 3-phase BLDC outrunner — spins the reaction-wheel flywheel. Paired with the TI DRV10983 sensorless driver on the PCB. Recommended candidate after a 4-way motor-type comparison (brushed DC / sensored BLDC / sensorless BLDC / stepper) — see bom/component-selection.md.',
    source:'Purchased, ≈$18.99, T-Motor/RC drone shops. bom/component-selection.md Motor Approval.' },
  { id:'HubCollar', mesh:null, primitive:'cylinder', dOuter:8.0, h:6.0,
    category:'purchase', y:197,
    name:'Hub Collar', ref:'—',
    dims:'≈8.0mm OD × 6.0mm height (generic set-screw shaft collar)',
    role:'Couples the motor shaft to the flywheel disk. Its retention strength against the flywheel\'s spin loads is carried as an explicit UNKNOWN in the source dimensional spec — the actual open safety question behind the REQ-403 containment requirement.',
    source:'Purchased, generic set-screw shaft-collar class part — not sourced to a specific vendor/MPN anywhere in this repo (disclosed ASSUMPTION).' },
  { id:'Flywheel', mesh:null, primitive:'disk', d:60.0, h:4.5,
    category:'purchase', y:208,
    name:'Flywheel Disk', ref:'—',
    dims:'60.0mm dia × 4.5mm thick, ≈100g (mild steel density assumption)',
    role:'The spinning reaction mass. Its momentum exchange with the enclosure is the entire point of this board — see the Circuit &amp; Current-Flow Viewer\'s Mode 2/3 for how (and how not yet) it is actually controlled.',
    source:'Purchased — no specific catalog part cited anywhere in this repo (disclosed ASSUMPTION); source your own disk matching this mass/diameter.' },
  { id:'ContainmentCap', mesh:'bench-imu-01-containment-cap.obj', sourceUpAxis:'z',
    category:'print3d', y:220,
    name:'Containment Cap', ref:'—',
    dims:'109.4 × 109.4 × 12mm',
    role:'Flywheel-bay safety enclosure — installed LAST, per REQ-403. Secured with 6× M3 screws into heat-set brass inserts (Ruthex RX-M3×5.7). This part\'s own retention margin against a flywheel failure is tracked as ACCEPTED-RISK (ISS-036), not fully resolved.',
    source:'3D-printed, PETG (assumption). STL: bench-imu-01-containment-cap.stl' },
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
