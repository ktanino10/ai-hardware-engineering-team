// ============================================================================
// Bench-IMU-01 -- Enclosure (Mechanical Lead, Phase 1)
// ============================================================================
// STATUS: Rev. 3 -- full redesign for the Motor Driver + Reaction Wheel
// subsystem (see bench-imu-01-dimensional-spec.md, top-of-file changelog,
// for the complete list of what changed vs. Rev 2 and why). This is a
// PROPOSAL awaiting Independent Mechanical Review, same as every prior
// revision -- see that file's Status line and this design's own agent
// definition, "Out of scope: declaring your own design reviewed/complete."
//
// TOOLING HONESTY (re-verified fresh THIS session -- do not copy the
// Rev 2 sentence below verbatim into a future revision without re-checking
// it again; tool availability is an environment fact, not a repo fact):
// no CAD/3D modeling MCP tool is connected in this environment
// (blender-get_addon_status -> "Could not connect to Blender", re-checked
// this session). HOWEVER, unlike Rev 2's original (Cycle 1) claim of "no
// local openscad/freecad binary or cadquery/solid/build123d Python library
// installed" -- which Rev 2's OWN addendum already corrected once for a
// 2021.01 binary -- THIS session independently re-found a working local
// `openscad` binary, now at version 2026.08.30 (confirmed via
// `openscad --version`, exit 0), plus a working `numpy-stl` Python library.
// Per that same Rev 2 precedent (correct a known-false statement rather than
// silently repeat it), this file's status is: a **targeted spot-check** of
// this revision's new geometry (base()/lid()/containment_cap() each
// rendered standalone, manifold-checked, and a subset of new dimensions
// bounding-box-measured from exported STL -- see
// bench-imu-01-dimensional-spec.md §0 for exactly what was and was not
// checked) was performed using this local toolchain, but this remains
// fundamentally a text/parametric OpenSCAD-SYNTAX SOURCE FILE deliverable,
// not a rendered/exported/fit-checked CAD product, and no STL/PNG/render
// artifact from this spot-check has been committed to this repository. A
// human should still render this file themselves for the authoritative
// view, e.g.:
//     openscad -o bench-imu-01-enclosure.stl bench-imu-01-enclosure.scad
// or paste it into an online OpenSCAD viewer. All "computed clearance
// checks" in the companion spec file are plain arithmetic (verified with a
// Python calculator this session), independent of and prior to this
// spot-check.
//
// Every dimension is a named variable below, each traced to one of:
//   - hardware/mechanical-interface.md (cited inline, "interface: <field>")
//   - an Evidence ID (manufacturer spec, DS-<CATEGORY>-<NNN>)
//   - an explicit ASSUMPTION or ESTIMATE made by this Mechanical Lead
// Full rationale for every value lives in the companion file
// bench-imu-01-dimensional-spec.md -- read it alongside this file; the
// comments here are brief pointers, not the full "why".
//
// Coordinate convention -- BOARD-LOCAL frame (matches
// hardware/mechanical-interface.md exactly, Rev 3): origin (0,0) at the PCB
// bottom-left corner, viewed from the top/component side. X: 0->100mm
// (PCB length, was 60mm in Rev 2). Y: 0->50mm (PCB width, was 40mm).
// This file's GLOBAL frame (used for all actual solid-modeling coordinates)
// has its own separate origin: (0,0,0) = the OVERALL ASSEMBLY's external
// bottom-left-floor corner, at the FLYWHEEL BAY end (Rev 3 NEW: the
// flywheel bay sits at global Y=0..~105, the PCB bay sits north of it at
// global Y=pcb_bay_y0..pcb_bay_y0+base_outer_y -- see Section 2c below).
// board_offset_x/y is the fixed translation from board-local XY to the PCB
// bay's OWN local global XY origin (i.e. add pcb_bay_y0 to get true global
// Y for anything board-related). Global Z=0 is the base's external bottom
// face; +Z points toward the lid/cap.
// ============================================================================

/* [Rendering / layout] */
// "assembled"    : base + PCB lid + containment cap shown in their final,
//                  closed, assembled positions (visual reference only --
//                  see the PCB/motor/flywheel reference geometry below,
//                  shown with `%` so excluded from any STL export).
// "print_layout" : all 3 printed pieces laid out side by side, each in its
//                  own natural print orientation. Starting point only --
//                  verify visually in your slicer / OpenSCAD's own view
//                  before trusting it; not rendered by this agent (beyond
//                  this session's disclosed spot-check, §0).
show_mode = "assembled"; // ["assembled", "print_layout"]

$fn = 48; // facet count for circles/cylinders -- cosmetic smoothness only,
          // does not change any stated dimension.

// ----------------------------------------------------------------------
// 1. VALUES TAKEN DIRECTLY FROM hardware/mechanical-interface.md (Rev 3)
//    (confidence labels mirror that file's own Confidence column)
// ----------------------------------------------------------------------

// --- Board Geometry (interface: A1 Board Geometry) ---
pcb_length    = 100.0; // mm, X extent. ASSUMPTION (interface file A1).
pcb_width     = 50.0;  // mm, Y extent. ASSUMPTION (interface file A1).
pcb_thickness = 1.6;   // mm, Z extent. ASSUMPTION (standard 2-layer stock,
                        // unchanged from Rev 2).

// --- Mounting holes (interface: A2 Mounting), [x, y, clearance_dia] ---
// MH-1..4 unchanged CORNER positions rescaled to the new board size; MH-5/6
// are Rev 3 NEW mid-edge standoffs near the motor zone (X=70-100), added by
// this Mechanical Lead because a 100x50mm board supported only at 4 corners
// risks excess flex/vibration transmission near the motor-driver components
// (U5/U6, D2/D3) on a board this much larger than Rev 2's 60x40mm -- good
// practice regardless of the motor ITSELF being off-board (only the motor
// is off-board; the motor-driver ELECTRONICS are still on this PCB). All
// ASSUMPTION, all sized for M2.5 (2.8mm clearance dia), same convention as
// Rev 2.
mount_holes = [
    [ 3.5,  3.5, 2.8], // MH-1 (corner)
    [96.5,  3.5, 2.8], // MH-2 (corner)
    [96.5, 46.5, 2.8], // MH-3 (corner)
    [ 3.5, 46.5, 2.8], // MH-4 (corner)
    [85.0,  3.5, 2.8], // MH-5 (Rev 3 NEW, motor-zone support)
    [85.0, 46.5, 2.8], // MH-6 (Rev 3 NEW, motor-zone support)
];

// --- Component height clearance (interface: A3 Component Height
// Clearance). TOP = 11.0mm, Rev 3: now driven by J4 (barrel jack), which
// SUPERSEDES Rev 2's 8.5mm (J2/J3-header-driven) figure as the new
// governing dimension. Per the interface file's own B3 cross-reference: if
// the motor had gone on-board, its 18.5mm body height would have become
// the new governing clearance instead (11.0mm would have been insufficient)
// -- this is one of the concrete facts that supported the off-board
// motor-mounting decision (see §5 rationale in the spec file). ---
top_component_clearance    = 11.0; // mm. ESTIMATE (interface A3, J4-driven).
bottom_component_clearance = 0.0;  // mm. ASSUMPTION (single-sided assembly,
                                    // unchanged from Rev 2).

// --- Connectors / switches / LEDs (interface: A4), board-local X, Y (mm).
//     J2/J3/SW1 X positions are UNCHANGED from Rev 2; Y now sits on the
//     new board's own top edge (50, was 40) -- same physical headers, same
//     top-edge placement convention, just a taller board. ---
j1_x = 0.0;  j1_y = pcb_width/2;  j1_ref_height = 3.2; // USB-C, opens -X.
              // j1_y computed as pcb_width/2 (=25.0) -- Rev 3 fix: Rev 2
              // hardcoded j1_y=20.0 (=40/2 at the time); this now stays
              // centered automatically if pcb_width ever changes again.
j2_x = 16.0; j2_y = pcb_width; // 4-pin UART header. Interface file A4 words
              // this as "pins point +Y" (Rev 2 said "+Z") -- resolved as a
              // non-functional wording difference describing the same
              // physical situation (component body/pins face outward at
              // the board's own top edge); not a real design conflict. See
              // dimensional-spec.md §6.
j3_x = 30.0; j3_y = pcb_width; // 4-pin SWD header, same treatment as J2.
sw1_x = 44.0; sw1_y = pcb_width; // momentary reset button.
d1_x = 10.0; d1_y = 37.5;        // status LED, top-emitting +Z (interface
                                  // file A4 gives this Y position directly,
                                  // not derived from pcb_width).
// J4: Rev 3 NEW. Barrel jack (Same Sky PJ-102AH-class, ESTIMATE per
// interface file A3/A4), horizontal, opens +X (mirrors J1 across the
// board). Height ~11.0mm is the NEW governing top_component_clearance
// figure above.
j4_x = pcb_length; j4_y = pcb_width/2; j4_ref_height = 11.0;
// MC-1: Rev 3 NEW, PROVISIONAL non-J designator (interface file's own
// term) for the motor's 3-phase-lead connection point on the PCB, in the
// motor zone (X=70-100), wire exit -Y (i.e. toward the flywheel bay, which
// this Mechanical Lead has positioned south of the PCB bay -- see §2c).
// No connector MPN specified upstream; modeled here as a simple reference
// point, not a specific footprint.
mc1_x = 92.0; mc1_y = 0.0;

// --- M1 motor (interface: B1, T-Motor MN2206-13 KV2000, DS-MTR-021
//     CONFIRMED body dimensions; bolt pattern and mounting-hole
//     thread/depth are this Mechanical Lead's own ASSUMPTION/UNKNOWN --
//     see below and the spec file §12). ---
m1_body_dia        = 27.0; // mm. CONFIRMED (DS-MTR-021).
m1_body_h          = 18.5; // mm. CONFIRMED (DS-MTR-021).
m1_shaft_dia       = 3.0;  // mm. CONFIRMED (DS-MTR-021).
m1_bolt_square     = 12.0; // mm, side of the assumed 4-hole square bolt
                            // pattern. ASSUMPTION: generic outrunner-class
                            // hobbyist convention (~16mm BCD), NOT
                            // T-Motor-specific -- interface file B1 flags
                            // this explicitly as an Open Item. Flag for
                            // pre-build verification against the real part.
m1_bolt_dia_clear  = 3.4;  // mm, M3 clearance. ASSUMPTION.
// Which side of the motor-to-platform joint is threaded (the motor's own
// base, vs. this platform) is UNKNOWN (interface file B1) -- see the
// motor_platform() module below for how this design accommodates either
// answer with the same through-hole geometry.

// --- Flywheel (interface: B2 -- no product exists; this Mechanical Lead's
//     own proposed geometry, consistent with the interface file's stated
//     target inertia and its own note that a solid disk, not a ring/rim
//     design, was assumed). MUST be machined steel -- NEVER printed
//     plastic (interface file B6; a plastic flywheel of equivalent
//     inertia would need ~28mm thickness, judged unsafe, see spec file). ---
fw_dia  = 60.0; // mm. ASSUMPTION (interface file B2 proposed swept dia).
fw_t    = 4.5;  // mm. ASSUMPTION -- derives the interface file's target
                 // inertia for a solid mild-steel disk (rho=7850kg/m^3);
                 // cross-checked this session: back-computing from fw_dia/
                 // rho/target-I gives 4.505mm, consistent with the stated
                 // 4.5mm (see spec file §7).
fw_material_rho = 7850.0; // kg/m^3, mild steel. ASSUMPTION (interface B2).

// --- Rotation clearance envelope (interface: B5, REQ-306 -- a real,
//     checked 3D keep-out volume, NOT a substitute for the REQ-403
//     containment decision below). ---
fw_radial_margin       = 8.0; // mm, beyond the disk's own radius.
                                // ASSUMPTION (interface file B5 proposal).
fw_axial_margin_per_face = 3.0; // mm, beyond the disk's own thickness, EACH
                                // face. ASSUMPTION (interface file B5).
fw_env_dia   = fw_dia + 2*fw_radial_margin;           // DERIVED = 76.0mm
fw_env_axial = fw_t + 2*fw_axial_margin_per_face;     // DERIVED = 10.5mm

// ----------------------------------------------------------------------
// 2. THIS MECHANICAL LEAD'S OWN DESIGN VALUES (this session).
//    Everything below is ASSUMPTION/ESTIMATE unless marked DERIVED
//    (computed from other named values here, not a fresh guess).
//    Full rationale for each: bench-imu-01-dimensional-spec.md.
// ----------------------------------------------------------------------

// --- Print-fit tolerance / manufacturability rule set -- UNCHANGED from
//     Rev 2; re-justified, not just copy-pasted, against the new Rev 3
//     geometry in the companion spec file §2. ---
fit_clearance = 0.2; // mm, PER SIDE. ASSUMPTION.
print_material = "PETG"; // ASSUMPTION, unchanged from Rev 2 -- if anything
                          // MORE applicable now given a motor as a heat/
                          // vibration source in the same assembly.
min_wall_t = 2.0;  // mm. ASSUMPTION, unchanged from Rev 2.
max_overhang_deg = 45;   // degrees from vertical. ASSUMPTION, unchanged.
max_bridge_span  = 10.0; // mm. ASSUMPTION, unchanged.
wall_t  = min_wall_t;
floor_t = min_wall_t;

// --- PCB-to-interior-cavity keepout (unchanged concept/value from Rev 2) --
board_xy_keepout = 1.5; // mm, per side. ASSUMPTION.

// --- PCB standoffs (unchanged formula/values from Rev 2; now 6 instances
//     at the mount_holes positions above, incl. new MH-5/6). ---
standoff_od          = 6.0;
standoff_pilot_dia   = 2.0;
standoff_h           = 6.0;
standoff_pilot_depth = 5.0;

// --- Single PCB/lid fastener type -- UNCHANGED M2.5 self-tap, used for all
//     PCB standoffs (now 6) + all 4 PCB-lid corner tabs. Reserved
//     EXCLUSIVELY for these static, low-duty joints -- Rev 3 introduces
//     two NEW, DIFFERENT fastener classes below for the motor mount and
//     the safety-critical containment cap, each re-justified on its own
//     merits rather than defaulting to this same M2.5 convention
//     everywhere (see spec file §5/§8 for the full differentiation
//     rationale). ---
screw_len = 6.0; // mm (M2.5 self-tapping). ASSUMPTION, unchanged from Rev 2.

// --- Vertical (Z) stack, PCB bay -- DERIVED unless noted ---
z_margin = 0.5; // mm. ASSUMPTION, unchanged concept/value from Rev 2.

base_interior_h = standoff_h + pcb_thickness + top_component_clearance
                  + z_margin;                     // DERIVED = 19.1mm (Rev2: 16.6)
base_total_h    = floor_t + base_interior_h;       // DERIVED = 21.1mm (Rev2: 18.6)

lid_lip_h   = 3.0;    // mm. ASSUMPTION, unchanged from Rev 2 (cap+skirt
                       // joint style explicitly reused per Hardware Lead's
                       // brief).
lid_roof_t  = wall_t;
lid_skirt_t = wall_t;

pcb_bay_total_height = base_total_h + lid_roof_t;  // DERIVED = 23.1mm
                       // (Rev 2's equivalent "total_height" was 20.6mm --
                       // this is now just ONE of the two bays' heights;
                       // see fw_bay_total_height below for the other.)

// --- XY footprint, PCB bay -- DERIVED unless noted ---
interior_x = pcb_length + 2*board_xy_keepout;      // DERIVED = 103.0mm
interior_y = pcb_width  + 2*board_xy_keepout;      // DERIVED = 53.0mm
base_outer_x = interior_x + 2*wall_t;              // DERIVED = 107.0mm
base_outer_y = interior_y + 2*wall_t;              // DERIVED = 57.0mm

lid_skirt_inner_x = base_outer_x + 2*fit_clearance;    // DERIVED = 107.4mm
lid_skirt_inner_y = base_outer_y + 2*fit_clearance;    // DERIVED = 57.4mm
lid_skirt_outer_x = lid_skirt_inner_x + 2*lid_skirt_t; // DERIVED = 111.4mm
lid_skirt_outer_y = lid_skirt_inner_y + 2*lid_skirt_t; // DERIVED = 61.4mm
lid_x0 = (base_outer_x - lid_skirt_outer_x) / 2;   // DERIVED = -2.2mm
lid_y0 = (base_outer_y - lid_skirt_outer_y) / 2;   // DERIVED = -2.2mm (this
                       // specific -2.2/-2.2 result is unchanged from Rev 2
                       // -- it depends only on wall_t/fit_clearance, both
                       // unchanged, not on the board size)

// translation from board-local (0,0) to the PCB BAY'S OWN local global XY
// (add pcb_bay_y0, §2c below, for TRUE global Y)
board_offset_x = wall_t + board_xy_keepout; // DERIVED = 3.5mm
board_offset_y = wall_t + board_xy_keepout; // DERIVED = 3.5mm

// --- J1 (USB-C) cutout, in the base's local X=0 (left) wall of the PCB
//     bay -- UNCHANGED dimensions from Rev 2 (same connector, no new data
//     to justify a change). ---
j1_cut_w = 9.5; // mm (Y-span). ESTIMATE, unchanged from Rev 2.
j1_cut_h = 6.0; // mm (Z-span). ESTIMATE, unchanged from Rev 2.
j1_cut_z = standoff_h; // mm, bottom edge of cutout vs. interior floor.

// --- J4 (barrel jack) cutout, Rev 3 NEW, mirrors J1 across the board in
//     the base's local X=pcb_length (right) wall, opens +X. Round cutout
//     (vs. J1's rectangular one) sized for a typical barrel-jack-class
//     cylindrical bushing/mounting boss. ---
j4_cut_dia = 10.0; // mm. ESTIMATE -- the interface file gives J4's height
                    // (11.0mm, ESTIMATE) but not its width/footprint; this
                    // is this Mechanical Lead's own outside-knowledge
                    // estimate of a typical PJ-102AH-class barrel jack's
                    // cylindrical portion, generously margined given the
                    // MPN itself is not locked. MUST be re-verified against
                    // the real part's datasheet drawing before build --
                    // flagged in spec file §12.
j4_cut_z = j1_cut_z; // mm, same bottom-edge reference convention as J1.

// --- Header/button bay (J2/J3/SW1), in the LID, open to the PCB bay's
//     rear (local +Y) edge -- SAME convention as Rev 2, rescaled for the
//     new board width. bay_x_min/max are numerically UNCHANGED from Rev 2
//     because J2/J3/SW1's board-local X positions did not change; only
//     bay_y_min moves (board's own top edge moved from Y=40 to Y=50). ---
bay_edge_margin = board_xy_keepout; // mm = 1.5. DERIVED, unchanged concept.
bay_x_min = (j2_x - 5) - bay_edge_margin;   // = 9.5mm, UNCHANGED vs Rev 2
bay_x_max = (sw1_x + 2.5) + bay_edge_margin; // = 48.0mm, UNCHANGED vs Rev 2
bay_y_min = (pcb_width - 6) - bay_edge_margin; // = 42.5mm (Rev2 was 32.5mm
                    // at pcb_width=40). Rev 3 hygiene fix: this formula now
                    // references pcb_width directly instead of Rev 2's
                    // hardcoded literal "40" -- a small parametric-safety
                    // improvement made while re-deriving this value for the
                    // new board size (not a functional defect in Rev 2,
                    // since Rev 2's own hardcoded 40 matched its own
                    // pcb_width=40 at the time -- but worth fixing now that
                    // a board-width change has actually happened once,
                    // so a hypothetical future Rev 4 change wouldn't
                    // silently go stale again). See reference_pcba() below
                    // for the matching fix to its own header-box sketch.

// --- D1 LED viewing hole, through the lid roof only -- UNCHANGED from
//     Rev 2 (same LED, no new data). ---
d1_hole_dia = 3.0; // mm. ESTIMATE, unchanged from Rev 2.

// --- External corner mounting tabs (PCB-lid-to-base fastening). UNCHANGED
//     formulas/values from Rev 2; repositioned to the new MH-1..4 CORNER
//     coordinates only (MH-5/6, mid-edge, do NOT get tabs -- tabs are a
//     lid-fastening feature at the 4 true corners, a separate concern from
//     how many mid-board PCB standoffs exist). ---
tab_w             = 8.0;
tab_project       = 6.0;
tab_base_t        = 5.6;
tab_pilot_depth   = 4.6;
tab_lid_t         = lid_roof_t;
tab_clear_dia     = 2.8;
lid_tab_project   = 2*min_wall_t + tab_clear_dia; // DERIVED = 6.8mm
tab_pilot_dia     = standoff_pilot_dia;
tab_chamfer_run   = tab_project;

tab_positions = [
    [ 3.5,  3.5, -1], // near MH-1, front-left
    [96.5,  3.5, -1], // near MH-2, front-right
    [96.5, 46.5, +1], // near MH-3, rear-right
    [ 3.5, 46.5, +1], // near MH-4, rear-left
];

// ----------------------------------------------------------------------
// 2b. MOTOR MOUNT (Rev 3 NEW). DECISION: off-board / bracket-mounted to
//     the enclosure BASE itself (not to the PCB) -- see spec file §5 for
//     the full 7-reason rationale (4 from the interface file's own B3
//     non-binding lean + 3 of this Mechanical Lead's own: safety/
//     containment-sizing independence from any future PCB revision,
//     motor serviceability without disturbing the PCB, and decoupling the
//     PCB's own growth path from the motor's mechanical loads). Shaft
//     orientation: VERTICAL. Hub interface: SHAFT-MOUNTED (bore + set-
//     screw collar on M1's 3mm shaft) -- consistent with the flywheel
//     being a solid disk, not a ring/bell-mount design (interface B2).
// ----------------------------------------------------------------------
motor_platform_od = m1_body_dia + 2*wall_t; // DERIVED = 31.0mm -- same
                    // "body + 2*wall_t" formula pattern as Rev 2's own
                    // standoff_od sizing; gives an annular margin around
                    // the motor body of exactly min_wall_t (2.0mm),
                    // consistent strength reasoning with the rest of this
                    // design (cross-checked: bolt-hole corner radius from
                    // the assumed 12mm-square pattern is 8.49mm, well
                    // inside the 13.5mm body radius -- see spec file §7).
motor_platform_h = 8.0; // mm. ASSUMPTION -- structural boss depth (roughly
                    // a 2-3x M3-diameter engagement-class band), justified
                    // here for STRUCTURAL RIGIDITY under continuous
                    // dynamic (rotating, vibrating) load, not for fastener
                    // engagement length (no insert is hosted in this
                    // particular joint -- see the plain-clearance-hole
                    // note below).

// Motor-to-platform fastening: 4x M3 PLAIN CLEARANCE HOLES (not heat-set
// inserts) straight through the platform, on the ASSUMED 12mm-square bolt
// pattern, ASSUMING M1's own base has captive threads (standard motor-
// manufacturer engineering for this class of part) -- screws are driven
// from whichever side turns out to be accessible; the WHICH SIDE IS
// THREADED question is UNKNOWN (interface file B1) and this design
// deliberately does not need to resolve it, because a straight through-hole
// (not a blind one) supports a screw driven from EITHER direction. Stated
// fallback if the motor side turns out to be unthreaded: add heat-set
// inserts to this platform in a future revision (the platform's own
// motor_platform_h=8.0mm already has ample depth for that contingency).
m1_mount_hole_dia_clear = m1_bolt_dia_clear; // = 3.4mm

// Hub / shaft interface
fw_hub_standoff  = fw_axial_margin_per_face; // mm = 3.0. DERIVED: reuses
                    // B5's own axial margin value directly, since this IS
                    // physically the "motor-bell-top-to-disk-bottom" gap
                    // that B5's axial margin already describes -- not a
                    // fresh, separate number.
fw_hub_collar_od = 8.0; // mm. ASSUMPTION -- generic off-the-shelf
                    // set-screw shaft-collar class part.
fw_hub_collar_h  = 6.0; // mm. ASSUMPTION.
fw_shaft_exposed_len_needed = fw_hub_collar_h + fw_hub_standoff; // DERIVED
                    // = 9.0mm -- REQUIRED but UNVERIFIED against the real
                    // M1 part's actual exposed shaft length above its
                    // bell top (interface file does not state this
                    // dimension). Flagged in spec file §12 for pre-build
                    // verification.

// ----------------------------------------------------------------------
// 2c. FLYWHEEL BAY / CONTAINMENT (Rev 3 NEW -- the REQ-403 safety
//     disposition). DECISION: real physical containment IS warranted as
//     defense-in-depth, independent of REQ-405 firmware speed-limiting
//     ever working correctly -- see spec file §5/§7 for the full
//     centrifugal-stress / stored-energy reasoning. This is a PROPOSAL for
//     Independent Mechanical Review + the human REQ-403 HITL gate, not a
//     final disposition.
// ----------------------------------------------------------------------
containment_wall_t = 2*wall_t; // mm = 4.0. ASSUMPTION -- an explicit,
                    // reasoned defense-in-depth multiplier (2x this
                    // design's own min_wall_t), NOT a calculated ballistic/
                    // penetration-rated figure (that analysis is out of
                    // Phase 1 scope -- see spec file §7 for exactly what
                    // this figure is and is not).
fw_radial_standoff = board_xy_keepout; // mm = 1.5. DERIVED/reused: same
                    // conceptual role as board_xy_keepout (a static
                    // assembly/robustness margin), layered ON TOP OF (not
                    // instead of) fw_radial_margin's own dynamic/wobble
                    // margin already baked into fw_env_dia.

fw_bay_inner_r = fw_env_dia/2 + fw_radial_standoff; // DERIVED = 39.5mm
fw_bay_outer_r = fw_bay_inner_r + containment_wall_t; // DERIVED = 43.5mm

// Containment cap fastening: 6x M3 into HEAT-SET BRASS INSERTS sunk into
// the base's own flywheel-bay flange (NOT plain self-tapped threads, and
// NOT the same choice made for the motor mount above) -- deliberately
// re-justified fastener choice, not a default: this joint is (a) fully
// plastic-to-plastic and under this Mechanical Lead's complete control on
// BOTH sides (unlike the motor mount, where the motor's own thread side is
// UNKNOWN), (b) SAFETY-CRITICAL (this cap is the containment barrier
// itself), and (c) subject to repeated access (inspection/rebuild) plus
// continuous vibration in service -- both of which degrade a self-tapped
// plastic thread's holding power over repeated cycles far more than a
// brass insert's. See spec file §5/§8.
n_cap_bolts   = 6;   // evenly spaced at 60 deg -- more evenly-distributed
                      // clamping than the PCB lid's own 4-tab convention,
                      // chosen specifically because this is the
                      // safety-critical joint.
heatset_od    = 4.6;  // mm. ASSUMPTION -- generic brass heat-set insert,
                      // NOT datasheet-sourced (no DS-FAST-* evidence exists
                      // in this repo for this part -- flagged in spec §12,
                      // mirrors Rev 2's own un-sourced screw precedent).
heatset_len   = 5.7;  // mm. ASSUMPTION, same sourcing caveat as heatset_od.

// fw_flange_project MUST be sized against the actual heat-set INSERT
// (4.6mm OD) -- NOT the smaller M3 screw shank (3.4mm) that merely passes
// through the cap side above it. This Mechanical Lead caught and corrected
// this exact error during this session's own final derivation pass (an
// earlier draft used the screw diameter and produced only 1.7mm of margin
// on each side of the insert, BELOW this design's own 2.0mm min_wall_t --
// see spec file §7 for the full before/after arithmetic).
fw_flange_project = 9.0; // mm. ASSUMPTION -- rounded up from the computed
                    // minimum (heatset_od + 2*min_wall_t = 4.6+4.0=8.6mm)
                    // to a clean number with a touch of extra margin.
flange_band_h = 8.0; // mm, Z-height of the flange band hosting the inserts.

bolt_circle_r = fw_bay_outer_r + fw_flange_project/2; // DERIVED = 48.0mm
fw_flange_or  = fw_bay_outer_r + fw_flange_project;   // DERIVED = 52.5mm
fw_flange_dia = 2*fw_flange_or;                       // DERIVED = 105.0mm
                    // (the widest single feature of the flywheel-bay
                    // assembly)

// --- Wire-passage duct (Rev 3 NEW): a small, deliberate, minimal breach of
//     the "fully enclosed" containment wall -- for M1's 3 phase leads only,
//     NOT a general-purpose access hole. Positioned LOW (well below the
//     disk's own rotation plane) at the point of closest approach between
//     the flywheel bay and the PCB bay. Explicitly distinguished from the
//     Rev 2 D1-style viewing hole (large, at disk/component height,
//     non-essential) which this Mechanical Lead deliberately did NOT carry
//     forward into the flywheel bay wall for safety reasons -- see spec
//     file §6. ---
wire_duct_dia = 5.0; // mm. ASSUMPTION -- sized only for 3 thin motor
                      // phase-lead wires + slack, not a general opening.
wire_duct_z   = 8.0; // mm, global Z of the duct's own center -- level with
                      // the motor platform's own height band (2.0-10.0mm),
                      // ~23mm below the disk's rotation zone (31.5-36.0mm).
wire_bridge_w = 12.0; // mm, X-span of a short rectangular bridge/gusset
                      // block this Mechanical Lead adds connecting the
                      // flywheel bay's own PLAIN WALL (outer radius
                      // fw_bay_outer_r=43.5mm -- NOT the wider flange band,
                      // which only exists near the very top, nowhere near
                      // this duct's low Z) to the PCB bay's own south wall.
                      // See motor_wire_bridge() below for the full
                      // bridge_y_lo/_hi derivation, including a real
                      // motor-vs-bridge collision this Mechanical Lead caught
                      // and fixed this session via render+numeric spot-check
                      // (an earlier draft anchored this block on the bay's
                      // own rotation-axis CENTER instead of the wall's outer
                      // surface, making it a 54.5mm slab that overlapped the
                      // entire motor platform/body footprint). ASSUMPTION:
                      // sized comfortably larger than duct_dia + 2*wall_t
                      // (=9.0mm minimum) for print robustness.
wire_bridge_h = wire_duct_dia + 2*wall_t; // DERIVED = 9.0mm, Z-span,
                      // centered on wire_duct_z (=> global Z [3.5,12.5],
                      // comfortably clear of both floor_t/2.0 below and the
                      // disk rotation zone above).

// --- Master XY layout: flywheel bay CENTERED on the PCB bay's own
//     X-midpoint (fw_cx = base_outer_x/2), NOT on the motor zone's own
//     X-centroid (which would be ~88.5mm). This was an explicit trade-off
//     computed and compared this session: centroid-aligned gives a
//     140x160mm-class footprint; width-centered (chosen) gives a strictly
//     smaller 107x162mm, at the cost of a longer motor-wire run
//     (~42mm along the interior floor from the wire duct to MC-1, vs. a
//     much shorter run with the centroid-aligned option) -- accepted as a
//     minor trade-off since wires are flexible and floor-routing space is
//     free, whereas footprint is the thing REQ-308 actually asks to
//     minimize. ---
fw_cx = base_outer_x / 2;              // DERIVED = 53.5mm
fw_cy = fw_flange_or;                  // DERIVED = 52.5mm (places the
                    // flange's own outer edge exactly tangent to global
                    // Y=0, the assembly's own southernmost extent)
pcb_bay_y0 = fw_cy + fw_flange_or;     // DERIVED = 105.0mm (places the PCB
                    // bay's own south wall exactly tangent to the flange's
                    // northernmost edge -- verified this session:
                    // pcb_bay_y0 - fw_cy = 52.5mm = fw_flange_or exactly,
                    // i.e. true tangency, zero overlap AND zero gap in the
                    // idealized 2D footprint -- see wire_bridge above for
                    // why a real print needs an explicit bridge feature
                    // there regardless).

// Two-tier footprint reporting, SAME convention Rev 2 established (its own
// §3 table distinguished "base outer footprint, excl. tabs" from "overall
// footprint incl. tabs" after its own MISS-003 fix changed the answer) --
// re-applied here, and EXTENDED to also catch the containment cap's own
// skirt overhang. This session's own openscad render spot-check (file
// header §0) caught the TRUE assembled envelope running larger than an
// initial hand-arithmetic-only pass had captured (which only summed the
// two bays' own solid-shell dimensions and missed the tab/skirt
// overhangs') -- corrected here, before this file was ever committed. See
// dimensional-spec.md §3/§7 for the full plain-arithmetic derivation and
// the caught-and-fixed narrative.
shell_footprint_x = base_outer_x;               // DERIVED = 107.0mm (main
                    // shell only -- PCB bay + flywheel bay walls/flange,
                    // excludes every fastener protrusion below)
shell_footprint_y = pcb_bay_y0 + base_outer_y;  // DERIVED = 162.0mm

// True assembled envelope, ALL protrusions included. X: the PCB LID's own
// skirt (lid_skirt_outer_x) turns out to be the single widest X feature in
// this whole assembly -- wider even than the containment cap's own skirt
// (fw_flange_dia+2*fit_clearance+2*wall_t = 109.4mm) -- both were checked;
// the lid wins by 2.0mm. Y: the containment cap's skirt sets the southern
// extreme (it overhangs slightly past the flywheel flange's own Y=0
// tangent point); the PCB lid's own corner tabs set the northern extreme
// (the WIDER lid_tab_project reaches further out than the base's own
// tab_project -- the same "lid tab is the true outward extreme" finding
// Rev 2 first made, re-confirmed unchanged here since neither
// tab_project/lid_tab_project changed).
assembled_envelope_x = lid_skirt_outer_x;                  // DERIVED = 111.4mm
cap_skirt_od          = fw_flange_dia + 2*fit_clearance + 2*wall_t; // = 109.4mm
assembled_envelope_y_south = fw_cy - cap_skirt_od/2;       // DERIVED = -2.2mm
assembled_envelope_y_north = pcb_bay_y0 + base_outer_y
                              + (tab_project + lid_tab_project)/2; // = 168.4mm
assembled_envelope_y  = assembled_envelope_y_north - assembled_envelope_y_south; // = 170.6mm
                    // REQ-308's ~150mm soft ceiling is exceeded by
                    // 20.6mm/13.7% on this true reading (12.0mm/8.0% on
                    // the shell-only reading above) -- an explicit,
                    // disclosed trade-off, not an oversight; see spec file
                    // §7 for the full reasoning on why this was accepted
                    // rather than further squeezed.

// Absolute Z-stack, flywheel bay (from the TRUE global bottom, Z=0)
fw_floor_top          = floor_t;                                    // 2.0
fw_motor_platform_top = fw_floor_top + motor_platform_h;            // 10.0
fw_motor_bell_top     = fw_motor_platform_top + m1_body_h;          // 28.5
fw_disk_bottom        = fw_motor_bell_top + fw_hub_standoff;        // 31.5
fw_disk_top           = fw_disk_bottom + fw_t;                      // 36.0
fw_clearance_top      = fw_disk_top + fw_axial_margin_per_face;     // 39.0
                        // (= the cap's own inner face, i.e. where the
                        // rotation-clearance keep-out volume actually ends)
fw_cap_outer_top      = fw_clearance_top + containment_wall_t;      // 43.0
fw_wall_h             = fw_clearance_top - fw_floor_top;            // 37.0
                        // (base's own cylindrical wall height, floor-top
                        // to the underside where the cap's skirt begins)
fw_bay_total_height   = fw_cap_outer_top;                           // 43.0mm

// ----------------------------------------------------------------------
// 3. MODULES -- PCB bay (base shell, standoffs, tabs; lid)
// ----------------------------------------------------------------------

module standoff() {
    difference() {
        cylinder(d = standoff_od, h = standoff_h);
        translate([0, 0, standoff_h - standoff_pilot_depth])
            cylinder(d = standoff_pilot_dia, h = standoff_pilot_depth + 1);
    }
}

module base_standoffs() {
    // Now 6 instances (MH-1..6, incl. Rev 3 NEW MH-5/6) in the PCB bay's
    // own local frame -- caller (pcb_bay_base()) translates into the
    // shared global frame via pcb_bay_y0.
    for (m = mount_holes)
        translate([board_offset_x + m[0], board_offset_y + m[1], floor_t])
            standoff();
}

module base_tab(pos) {
    // UNCHANGED formula from Rev 2 -- only the 4 corner tab_positions
    // (above) changed to match the new board size.
    tx = board_offset_x + pos[0];
    dy = pos[2];
    tab_y0 = (dy < 0) ? -tab_project : base_outer_y;
    z0     = base_total_h - tab_base_t;
    difference() {
        translate([tx - tab_w/2, tab_y0, z0])
            cube([tab_w, tab_project, tab_base_t]);
        translate([tx, tab_y0 + tab_project/2, base_total_h - tab_pilot_depth])
            cylinder(d = tab_pilot_dia, h = tab_pilot_depth + 1);
    }
    y_wall     = (dy < 0) ? 0 : base_outer_y;
    y_tab_edge = (dy < 0) ? -tab_project : base_outer_y + tab_project;
    z_bottom   = z0 - tab_chamfer_run;
    translate([tx - tab_w/2, 0, 0])
        rotate([0, 90, 0])
            linear_extrude(height = tab_w)
                polygon(points = [
                    [-z_bottom, y_wall],
                    [-z0,       y_wall],
                    [-z0,       y_tab_edge],
                ]);
}

module base_tabs() {
    for (p = tab_positions) base_tab(p);
}

module pcb_bay_shell() {
    // In the PCB BAY'S OWN local frame (Z unchanged from Rev 2's
    // base_shell(); XY unchanged from Rev 2's own convention too -- the
    // caller translates by [0, pcb_bay_y0, 0] to place it in the shared
    // global frame, §2c).
    difference() {
        cube([base_outer_x, base_outer_y, base_total_h]);
        translate([wall_t, wall_t, floor_t])
            cube([interior_x, interior_y, base_total_h - floor_t + 1]);
        // J1 (USB-C) cutout through the local X=0 wall
        translate([-1,
                    board_offset_y + j1_y - j1_cut_w/2,
                    floor_t + j1_cut_z])
            cube([wall_t + 2, j1_cut_w, j1_cut_h]);
        // J4 (barrel jack) cutout through the local X=pcb_length wall,
        // Rev 3 NEW -- round cutout, opens +X.
        translate([base_outer_x - wall_t - 1,
                    board_offset_y + j4_y,
                    floor_t + j4_cut_z + j4_cut_dia/2])
            rotate([0, 90, 0])
                cylinder(d = j4_cut_dia, h = wall_t + 2);
    }
}

module pcb_bay_base() {
    union() {
        pcb_bay_shell();
        base_standoffs();
        base_tabs();
    }
}

module lid_tab(pos) {
    tx = board_offset_x + pos[0];
    dy = pos[2];
    tab_y0  = (dy < 0) ? -tab_project : base_outer_y;
    hole_yc = tab_y0 + tab_project/2;
    cube_y0 = hole_yc - lid_tab_project/2;
    difference() {
        translate([tx - tab_w/2, cube_y0, lid_lip_h])
            cube([tab_w, lid_tab_project, lid_roof_t]);
        translate([tx, hole_yc, lid_lip_h - 1])
            cylinder(d = tab_clear_dia, h = lid_roof_t + 2);
    }
}

module lid_tabs() {
    for (p = tab_positions) lid_tab(p);
}

module lid_shell() {
    difference() {
        translate([lid_x0, lid_y0, 0])
            cube([lid_skirt_outer_x, lid_skirt_outer_y, lid_lip_h + lid_roof_t]);
        translate([lid_x0 + (lid_skirt_outer_x - lid_skirt_inner_x)/2,
                    lid_y0 + (lid_skirt_outer_y - lid_skirt_inner_y)/2,
                    -1])
            cube([lid_skirt_inner_x, lid_skirt_inner_y, lid_lip_h + 1]);
        // header/button bay: full-height notch through roof + skirt, open
        // to the LOCAL rear (+Y) face (Rev 3: bay_y_min recomputed above)
        translate([board_offset_x + bay_x_min,
                    board_offset_y + bay_y_min,
                    -1])
            cube([bay_x_max - bay_x_min,
                  (lid_y0 + lid_skirt_outer_y) - (board_offset_y + bay_y_min) + 1,
                  lid_lip_h + lid_roof_t + 2]);
        // D1 viewing hole, through the roof only
        translate([board_offset_x + d1_x, board_offset_y + d1_y, lid_lip_h - 1])
            cylinder(d = d1_hole_dia, h = lid_roof_t + 2);
    }
}

module pcb_lid() {
    union() {
        lid_shell();
        lid_tabs();
    }
}

// ----------------------------------------------------------------------
// 3b. MODULES -- Flywheel bay (motor platform, containment wall/flange,
//     wire-passage bridge; containment cap). Built in the PCB BAY'S OWN
//     local XY frame with fw_cx/fw_cy as the flywheel-bay center, Z in the
//     shared GLOBAL frame directly (both bays share Z=0). The caller
//     (base()) does NOT translate this group -- only pcb_bay_base() gets
//     translated by pcb_bay_y0, since fw_cx/fw_cy/pcb_bay_y0 were derived
//     together so that this group's own local frame IS the global frame.
// ----------------------------------------------------------------------

module motor_platform() {
    // Solid FLOOR DISC (Z=[0,fw_floor_top], radius fw_bay_outer_r -- matches
    // fw_bay_wall()'s own outer radius exactly, so the two share a full,
    // flush, full-face Z=fw_floor_top interface, the SAME stacking
    // convention used everywhere else in this design, not a fragile
    // tangent point) PLUS the raised motor-mounting boss on top of it, PLUS
    // 4x M3 plain clearance through-holes on the assumed 12mm-square bolt
    // pattern and the central shaft-clearance hole -- ALL cut full-depth,
    // from below the floor disc up through the boss top, so the
    // "straight-through, supported either way" design intent (screw
    // direction contingent on the UNKNOWN motor-thread-side -- see §2b)
    // still holds now that the floor disc sits underneath.
    //
    // CAUGHT-AND-FIXED THIS SESSION (see dimensional-spec.md §7, MISS-005 --
    // the most severe of the four errors caught this session): an earlier
    // draft had NO floor disc at all here -- just the small r=15.5mm boss,
    // Z=[fw_floor_top,fw_floor_top+motor_platform_h], with nothing filling
    // the 24.0mm-wide radial gap out to fw_bay_wall()'s own inner bore
    // (fw_bay_inner_r=39.5mm). Confirmed via an explicit openscad boolean
    // connectivity check (intersection(motor_platform(), fw_bay_wall()) =>
    // "Current top level object is empty.") that this was a REAL geometric
    // defect, not a documentation-only one: motor_platform() would have
    // been a fully disconnected, floating, unprintable island (touching
    // NEITHER the wall NOR the build-plate floor at Z=0), AND -- more
    // seriously -- the flywheel bay's own bottom would have been
    // completely open, directly defeating the REQ-403 physical-containment
    // decision this design is built around (a detached flywheel fragment
    // could simply fall out the bottom in a failure event). This is
    // exactly the class of error a disclosed render-based connectivity
    // spot-check exists to catch, vs. formula-only hand arithmetic that
    // never actually tests whether two named-variable regions truly touch.
    difference() {
        union() {
            translate([fw_cx, fw_cy, 0])
                cylinder(r = fw_bay_outer_r, h = fw_floor_top);
            translate([fw_cx, fw_cy, fw_floor_top])
                cylinder(d = motor_platform_od, h = motor_platform_h);
        }
        for (sx = [-1, 1]) for (sy = [-1, 1])
            translate([fw_cx + sx*m1_bolt_square/2,
                        fw_cy + sy*m1_bolt_square/2,
                        -1])
                cylinder(d = m1_mount_hole_dia_clear,
                          h = fw_floor_top + motor_platform_h + 2);
        // central shaft clearance (full depth, so the shaft's own
        // base/bell can seat directly on the platform top with clearance
        // all the way down, regardless of which side of M1's shaft-to-hub
        // joint protrudes)
        translate([fw_cx, fw_cy, -1])
            cylinder(d = m1_shaft_dia + 2*fit_clearance,
                      h = fw_floor_top + motor_platform_h + 2);
    }
}

module fw_bay_wall() {
    // Cylindrical containment wall, floor to the cap's underside
    // (fw_wall_h), PLUS the wider bolt flange band at its own top
    // (flange_band_h), hosting the 6 heat-set inserts.
    union() {
        difference() {
            translate([fw_cx, fw_cy, fw_floor_top])
                cylinder(d = 2*fw_bay_outer_r, h = fw_wall_h);
            translate([fw_cx, fw_cy, fw_floor_top - 1])
                cylinder(d = 2*fw_bay_inner_r, h = fw_wall_h + 2);
        }
        // flange band at the top of the wall
        difference() {
            translate([fw_cx, fw_cy, fw_clearance_top - flange_band_h])
                cylinder(d = 2*fw_flange_or, h = flange_band_h);
            translate([fw_cx, fw_cy, fw_clearance_top - flange_band_h - 1])
                cylinder(d = 2*fw_bay_outer_r, h = flange_band_h + 2);
            // 6x heat-set insert pilot holes, evenly spaced
            for (i = [0 : n_cap_bolts - 1]) {
                a = i * 360 / n_cap_bolts;
                translate([fw_cx + bolt_circle_r*cos(a),
                            fw_cy + bolt_circle_r*sin(a),
                            fw_clearance_top - heatset_len])
                    cylinder(d = heatset_od, h = heatset_len + 1);
            }
        }
    }
}

module motor_wire_bridge() {
    // Rev 3 NEW: a short rectangular gusset connecting the flywheel bay's
    // PLAIN WALL (outer radius fw_bay_outer_r -- NOT the wider flange band,
    // which per fw_bay_wall() above only exists near the very top,
    // Z in [fw_clearance_top-flange_band_h, fw_clearance_top], nowhere near
    // this duct's low Z) out to the PCB bay's own south wall.
    //
    // CAUGHT-AND-FIXED THIS SESSION (see dimensional-spec.md §7, MISS-004):
    // an earlier draft set bridge_y_lo = fw_cy (the flywheel bay's own
    // ROTATION-AXIS CENTER, not any wall surface), which made this "bridge"
    // a 54.5mm-long slab reaching all the way back across the ENTIRE motor
    // platform (max Y 68.0mm) and motor body (max Y 66.0mm) footprint --
    // i.e. a real printed-plastic obstruction sitting exactly where the
    // physical motor needs to seat. Caught by an openscad render+numeric
    // spot-check this session (echo of bridge_y_lo/_hi against
    // motor_platform_od/m1_body_dia), NOT by eyeballing the comment (which
    // already, incorrectly, described the feature as "short"). Fixed below:
    // bridge_y_lo now starts at the plain wall's OWN outer ring surface,
    // pulled in by an explicit bridge_fuse_overlap safety margin so the
    // block overlaps real ring material across its FULL width (not just a
    // single tangent line down its centerline) -- verified this session:
    // the ring's outer boundary at the bridge's own X-edges (dx=+-6mm) is
    // Y=95.58, comfortably above (i.e. further out than) the resulting
    // bridge_y_lo=94.0, so full-width overlap is guaranteed with ~1.6mm to
    // spare even at the block's corners.
    bridge_fuse_overlap = 2.0; // mm. ASSUMPTION: FDM-safe guaranteed-fusion
                      // margin pulling the bridge's start point in from the
                      // wall ring's exact (fragile, line-only-contact)
                      // tangent Y so the two solids genuinely overlap across
                      // the bridge's full width, not just a mathematical
                      // knife-edge -- see derivation above.
    bridge_y_lo = fw_cy + fw_bay_outer_r - bridge_fuse_overlap; // = 94.0mm
                      // (was, incorrectly, fw_cy=52.5mm -- see caught-and-
                      // fixed note above)
    bridge_y_hi = pcb_bay_y0 + wall_t; // = 107.0mm, a touch into the PCB
                      // bay's own wall (unchanged -- this end was always
                      // correct)
    // Resulting bridge span = 13.0mm (was, incorrectly, 54.5mm) -- verified
    // this session to clear the motor platform's own footprint (max Y
    // 68.0mm) by 26.0mm, and the motor body's own footprint (max Y 66.0mm)
    // by 28.0mm: zero interference with the real, physical motor.
    difference() {
        translate([fw_cx - wire_bridge_w/2, bridge_y_lo,
                    wire_duct_z - wire_bridge_h/2])
            cube([wire_bridge_w, bridge_y_hi - bridge_y_lo, wire_bridge_h]);
        translate([fw_cx, bridge_y_lo - 1, wire_duct_z])
            rotate([-90, 0, 0])
                cylinder(d = wire_duct_dia, h = (bridge_y_hi - bridge_y_lo) + 2);
    }
}

module base() {
    union() {
        translate([0, pcb_bay_y0, 0]) pcb_bay_base();
        motor_platform();
        fw_bay_wall();
        motor_wire_bridge();
    }
}

module containment_cap() {
    // 3rd printed piece. A shallow dome/disk top + downward skirt that
    // slips over the base's flange band (SAME cap+skirt joint style
    // reused from the PCB lid, per the Hardware Lead's brief), with 6
    // plain M3 clearance holes on the same bolt_circle_r, screws driven
    // downward into the base's heat-set inserts. This is the ONE part
    // whose installation has a hard ordering constraint -- see spec file
    // §10 assembly order: it must be installed LAST, after the flywheel is
    // on the shaft, since it seals the one remaining open access point.
    cap_skirt_h = flange_band_h; // overlaps the base's own flange band
    difference() {
        union() {
            // flat disk top, flush with the flange's own outer diameter
            translate([fw_cx, fw_cy, fw_cap_outer_top - containment_wall_t])
                cylinder(d = fw_flange_dia, h = containment_wall_t);
            // downward skirt, ID = flange OD + fit_clearance (slip fit,
            // consistent with the PCB lid's own clearance-fit convention)
            translate([fw_cx, fw_cy, fw_cap_outer_top - containment_wall_t - cap_skirt_h])
                difference() {
                    cylinder(d = fw_flange_dia + 2*fit_clearance + 2*wall_t,
                              h = cap_skirt_h);
                    translate([0, 0, -1])
                        cylinder(d = fw_flange_dia + 2*fit_clearance,
                                  h = cap_skirt_h + 2);
                }
        }
        // 6x M3 plain clearance holes, coaxial with the base's inserts
        for (i = [0 : n_cap_bolts - 1]) {
            a = i * 360 / n_cap_bolts;
            translate([fw_cx + bolt_circle_r*cos(a),
                        fw_cy + bolt_circle_r*sin(a),
                        fw_cap_outer_top - containment_wall_t - 1])
                cylinder(d = m1_bolt_dia_clear, h = containment_wall_t + 2);
        }
    }
}

// ----------------------------------------------------------------------
// 4. VISUAL-REFERENCE-ONLY GEOMETRY. All shown with the `%` background
//    modifier -- OpenSCAD excludes `%` geometry from STL export. NOT part
//    of the manufactured parts; exists purely so a human rendering this
//    file can visually sanity-check clearances. Simplified boxes/
//    cylinders -- not an accurate 3D model of the real PCBA/motor/
//    flywheel.
// ----------------------------------------------------------------------
module reference_pcba() {
    pcb_z = floor_t + standoff_h;
    color("green")
    translate([board_offset_x, board_offset_y + pcb_bay_y0, pcb_z])
        cube([pcb_length, pcb_width, pcb_thickness]);
    comp_z = pcb_z + pcb_thickness;
    // J1 USB-C
    translate([board_offset_x + j1_x - 3,
                board_offset_y + pcb_bay_y0 + j1_y - j1_cut_w/2 + 0.75,
                comp_z])
        cube([7, j1_cut_w - 1.5, j1_ref_height]);
    // J4 barrel jack (Rev 3 NEW)
    translate([board_offset_x + j4_x - 4,
                board_offset_y + pcb_bay_y0 + j4_y - j4_cut_dia/2 + 0.75,
                comp_z])
        cube([4, j4_cut_dia - 1.5, j4_ref_height]);
    // J2 / J3 headers -- Rev 3 fix: uses pcb_width directly (was Rev 2's
    // hardcoded "40"), matching the bay_y_min hygiene fix above.
    for (hx = [j2_x, j3_x])
        translate([board_offset_x + hx - 5,
                    board_offset_y + pcb_bay_y0 + pcb_width - 6, comp_z])
            cube([10, 6, top_component_clearance]);
    // SW1 reset button
    translate([board_offset_x + sw1_x,
                board_offset_y + pcb_bay_y0 + sw1_y - 2.5, comp_z])
        cylinder(d = 5, h = 5);
    // D1 LED
    translate([board_offset_x + d1_x, board_offset_y + pcb_bay_y0 + d1_y, comp_z])
        cylinder(d = 3, h = 1.2);
}

module reference_motor_flywheel() {
    // Motor body + shaft
    color("silver")
    translate([fw_cx, fw_cy, fw_motor_platform_top])
        cylinder(d = m1_body_dia, h = m1_body_h);
    color("silver")
    translate([fw_cx, fw_cy, fw_motor_bell_top])
        cylinder(d = m1_shaft_dia, h = fw_shaft_exposed_len_needed);
    // Hub collar
    color("gray")
    translate([fw_cx, fw_cy, fw_motor_bell_top])
        cylinder(d = fw_hub_collar_od, h = fw_hub_collar_h);
    // Flywheel disk (steel -- NOT printed, reference only)
    color("orange")
    translate([fw_cx, fw_cy, fw_disk_bottom])
        cylinder(d = fw_dia, h = fw_t);
    // Rotation clearance envelope (the REQ-306 keep-out volume itself,
    // wireframe-only via low alpha, NOT a manufactured feature)
    color("red", 0.15)
    translate([fw_cx, fw_cy, fw_disk_bottom - fw_axial_margin_per_face])
        cylinder(d = fw_env_dia, h = fw_env_axial);
}

// ----------------------------------------------------------------------
// 5. TOP-LEVEL ASSEMBLY / LAYOUT (Rev 3: 3 pieces)
// ----------------------------------------------------------------------
if (show_mode == "assembled") {
    base();
    translate([0, pcb_bay_y0, base_total_h - lid_lip_h]) pcb_lid();
    containment_cap();
    % reference_pcba();
    % reference_motor_flywheel();
} else if (show_mode == "print_layout") {
    // Base: natural print orientation (floor-down) -- already is one.
    translate([0, 0, 0]) base();

    // PCB lid: flip roof-down, lay out beside the base. Starting point
    // only -- verify visually before trusting it; not rendered here
    // beyond this session's disclosed §0 spot-check.
    translate([base_outer_x + 15, pcb_bay_y0, lid_lip_h + lid_roof_t])
        rotate([180, 0, 0])
            pcb_lid();

    // Containment cap: flip dome-down (its own natural print orientation,
    // flat disk face becomes the bed-adjacent face), lay out beside both.
    translate([fw_cx + fw_flange_or + 20, fw_cy, fw_cap_outer_top])
        rotate([180, 0, 0])
            containment_cap();
}

// ============================================================================
// END OF FILE -- bench-imu-01-enclosure.scad (Rev 3)
// Companion file: bench-imu-01-dimensional-spec.md (full rationale, self-
// check against the Mechanical Reviewer's 10-item checklist, open
// UNKNOWNs/ASSUMPTIONs carried forward, REQ-403 safety-disposition
// proposal).
// ============================================================================
