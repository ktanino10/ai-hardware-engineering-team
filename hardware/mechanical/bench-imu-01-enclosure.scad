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
// hardware/mechanical-interface.md exactly, REV 5 FIX MISS-034): origin
// (0,0) at the PCB bottom-left corner, viewed from the top/component side.
// X: 0->150mm (PCB length, real KiCad board -- was a Rev 3 100mm PROPOSAL,
// itself was 60mm in Rev 2). Y: 0->95mm (PCB width, real KiCad board --
// was a Rev 3 50mm PROPOSAL, itself was 40mm in Rev 2).
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
//
// REV 4 STATUS ADDENDUM (new, additive only -- everything above this
// addendum is Rev 3, UNCHANGED, and remains the authoritative record of
// what Rev 3 is and how it was verified):
//
// This file now ALSO contains the Rev 4 free-rotation support mechanism: a
// human-approved BC Precision 4LS-3 lazy-susan turntable ball bearing
// (bom/component-selection.md, Candidate A) integrated via a NEW mounting
// flange fused below the existing base() floor (Section 2B/3B) plus a NEW
// 4th printed piece, a fixed stand plate, sized from a from-scratch
// CG/tip-over analysis. This is a PROPOSAL awaiting Independent Mechanical
// Review, same as Rev 3 above -- see bench-imu-01-dimensional-spec.md
// Section 18 for the full rationale, and hardware/mechanical-interface.md
// Part C for the interface-level summary.
//
// ADDITIVE-ONLY CONFIRMATION: every Rev 3 module body, dimension, and
// variable definition above is byte-for-byte unchanged (verified via `git
// diff` showing zero deleted content lines across this whole file). The
// ONE pre-existing line touched anywhere in this file is a single
// print_layout DISPLAY-position Z-shift on the `base()` call in Section 5
// (not a change to base()'s own module body/dimensions) -- see that line's
// own comment for the full justification.
//
// TOOLING HONESTY (re-verified fresh THIS session, independently of the
// Rev 3 paragraph above): same environment facts hold -- no CAD/3D
// modeling MCP tool connected (blender-get_addon_status -> "Could not
// connect to Blender"), local `openscad` CLI v2026.08.30 present and used
// for a targeted spot-check of the NEW Rev 4 geometry specifically (see
// bench-imu-01-dimensional-spec.md Section 18.5 for exactly what was and
// was not checked). No STL/render artifact from this spot-check has been
// committed to this repository.
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
// REV 5 FIX (MISS-034, CRITICAL): pcb_length/pcb_width below were a Rev 3
// PROPOSAL (100x50mm) that was superseded when the real board was laid out
// at 150x95mm -- confirmed this session directly from the real KiCad
// project's own Edge.Cuts layer (`hardware/pcb/bench-imu-01/
// bench-imu-01.kicad_pcb`: `(gr_rect (start 0 0) (end 150 95))`), with no
// re-handoff back to Mechanical ever recorded. See
// bench-imu-01-dimensional-spec.md's own Rev 5 changelog entry and
// hardware/mechanical-interface.md A1/A2 (now CONFIRMED, not ASSUMPTION)
// for the full re-derivation. This one root value is now CONFIRMED, not
// ASSUMPTION -- it is read directly from the real board file, not proposed.
pcb_length    = 150.0; // mm, X extent. CONFIRMED (real KiCad Edge.Cuts).
pcb_width     = 95.0;  // mm, Y extent. CONFIRMED (real KiCad Edge.Cuts).
pcb_thickness = 1.6;   // mm, Z extent. ASSUMPTION (standard 2-layer stock,
                        // unchanged from Rev 2 -- the real board's actual
                        // layer stack-up/thickness was not independently
                        // re-confirmed this pass, out of MISS-034's own
                        // scope).

// --- Mounting holes (interface: A2 Mounting), [x, y, clearance_dia] ---
// REV 5 FIX (MISS-034): the Rev 3 MH-1..6 six-hole scheme below (4 corner
// holes + 2 Rev-3-invented "motor-zone" mid-edge holes, MH-5/6) does not
// match the real board -- the real KiCad project has exactly 4
// `MountingHole_2.7mm_M2.5` footprints, independently confirmed this
// session by counting footprint instances directly in the real
// `bench-imu-01.kicad_pcb` (4 found, at raw `(at ...)` coordinates
// (8,8)/(142,8)/(8,87)/(142,87) -- these equal `generate_pcb.py`'s own
// `BOARD_MARGIN(5.0) + 3.0` / `BOARD_W(150)-5.0-3.0` / `BOARD_H(95)-5.0-3.0`
// formula, i.e. independently re-derivable from that script too, not just
// read off the raw file once). MH-5/6 (and the "motor zone" concept that
// motivated them) do not correspond to anything on the real board -- there
// is no second mounting-hole pair near the real M1 (which is a 3-pin
// phase-wire terminal block on the real board, not a Rev 3-imagined
// on-board motor-driver hot zone needing extra local stiffening). Reduced
// to the real 4-hole, 134x79mm pattern. Clearance kept at 2.8mm (this
// design's own established M2.5-clearance convention, unchanged) --
// NOTE, disclosed not silently corrected: the real footprint's own name
// ("2.7mm") implies a slightly smaller nominal PCB drill than this
// enclosure design's own 2.8mm standoff-clearance assumption; a trivial,
// non-blocking 0.1mm difference between two different holes (the PCB's own
// drill vs. this standoff's pilot clearance) -- not reconciled further,
// out of MISS-034's own scope (board outline + hole PATTERN, not exact
// drill-diameter cross-referencing).
mount_holes = [
    [  8.0,  8.0, 2.8], // MH-1 (corner, real board)
    [142.0,  8.0, 2.8], // MH-2 (corner, real board)
    [142.0, 87.0, 2.8], // MH-3 (corner, real board)
    [  8.0, 87.0, 2.8], // MH-4 (corner, real board)
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

// --- PCB standoffs (unchanged formula/values from Rev 2; 4 instances at
//     the mount_holes positions above -- REV 5 FIX (MISS-034): back to 4,
//     matching the real board's own 4 mounting holes; Rev 3's MH-5/6 never
//     existed on the real board, see the mount_holes note above). ---
standoff_od          = 6.0;
standoff_pilot_dia   = 2.0;
standoff_h           = 6.0;
standoff_pilot_depth = 5.0;

// --- Mid-span passive support pad (NEW, REV 5, MISS-043; height revised MISS-045) ---
// MH-5/MH-6's own removal above (real board has only 4 holes) did NOT
// remove the PHYSICAL CONCERN that originally motivated them: Rev 3's own
// comment (now-removed, quoted for the record in MISS-043) justified
// MH-5/6 because "a board supported only at 4 corners risks excess
// flex/vibration transmission near the motor-driver components" -- and
// the real board (150mm) is 50% LONGER than the 100mm Rev 3 proposal that
// raised that concern in the first place, so the underlying physical
// worry is, if anything, stronger now, not weaker (independently flagged
// by a sibling session's own PR #41/MISS-035 finding; see MISS-043 for
// the full disclosure and this repo's own precedent that a mid-span
// concern must be addressed, not silently dropped, when its enabling
// hole disappears). This design does NOT have a real mid-span PCB
// mounting hole to bolt a standoff into (the real board only has the 4
// corner holes) -- adding one would be an Electronics-side PCB revision,
// out of this Mechanical-only pass's own scope. What IS in this pass's
// own scope: a PASSIVE (non-fastened) support pad the board simply RESTS
// on, at the board's own physical mid-point, reducing (not eliminating)
// unsupported-span sag/flex there.
//
// Placement-safety citation CORRECTED, MISS-045 (independently found:
// the original citation below, `bottom_component_clearance`=0, does not
// itself cover through-hole lead/via protrusion, which is what actually
// occupies the space directly under a populated board -- a real gap in
// the original justification, not merely an imprecise phrasing). The
// citation that actually covers this hazard, re-derived directly from the
// raw `.kicad_pcb` this pass: of the board's 10 through-hole footprints,
// the nearest to this pad's own board-local center (75, 47.5) is
// `SW_PUSH_6mm` at (60, 58), 18.31mm away -- versus this pad's own
// 3.0mm radius, a wide margin; separately, 0 of the board's 42 vias fall
// within 9.0mm of that same center. `bottom_component_clearance`=0 (no
// bottom-side SMT components) remains true and is retained as
// supporting context, but is not by itself the check that rules out a
// physical collision.
//
// HEIGHT rationale CORRECTED, MISS-045 (independently found: the
// original "MUST equal standoff_h exactly" reasoning below assumed a
// perfectly flat board, which is not a real manufacturing condition).
// IPC-6012 permits up to 0.75% bow/twist (this board uses SMT
// components, so the SMT figure applies, not the 1.5% through-hole-only
// figure) measured across a board's largest dimension -- over this
// board's 150mm, that is up to +/-1.125mm of IN-SPEC deviation from
// flat, concentrated (by construction) at the mid-point, exactly where
// this pad sits. A pad at EXACTLY the same height as the 4 corner
// standoffs is not the safe choice this originally assumed: if the real
// board bows upward at center, the pad never contacts anything (merely
// inert -- harmless); but if it bows DOWNWARD at center, the pad
// contacts FIRST, and tightening the 4 real corner fasteners afterward
// forces the board to flex OVER the pad -- a permanent pre-load that
// itself introduces the exact mid-span flex stress this feature exists
// to relieve. The two error directions are NOT symmetric (too-short is
// merely inert; too-tall is actively harmful), so nominal-exact is the
// wrong target -- the design should bias into the benign (too-short)
// direction. Fixed by undersizing this pad by `mid_support_gap` (below)
// relative to `standoff_h`, so it acts as a passive TRAVEL LIMITER that
// only engages once real sag exceeds the disclosed in-spec bow band,
// rather than a preload at rest. Residual, disclosed limitation (not
// silently accepted): this is a CAD-level design bias, not a
// manufacturing-process-verified one -- whether a real FDM print
// reliably realizes this exact 0.4mm gap (first-layer squish, bed-level
// variance, per-print calibration drift) has not been separately
// verified by a Manufacturing-Engineer-level process analysis; flagged
// as a candidate for that discipline's review, not resolved here.
mid_support_dia = standoff_od; // mm = 6.0. ASSUMPTION -- reuses the
                    // existing standoff diameter for a consistent
                    // print-boss family, not independently sized.
mid_support_gap = 0.4; // mm, ASSUMPTION, new MISS-045. Deliberate
                    // undersizing below `standoff_h`, chosen from the
                    // middle of a 0.3-0.5mm suggested range -- small
                    // relative to the disclosed +/-1.125mm in-spec bow
                    // band (so it still meaningfully caps deflection
                    // well before the unsupported span's own full sag
                    // potential is reached), but large enough to clear
                    // ordinary dimensional noise between this pad and
                    // the 4 standoffs (both printed in the same part, at
                    // the same nominal height, from the same datum --
                    // so print-to-print Z-accuracy is NOT the dominant
                    // term here; real board bow is).
mid_support_h   = standoff_h - mid_support_gap; // mm = 5.6 (was 6.0,
                    // exactly `standoff_h` -- MISS-045). DERIVED.


// --- Single PCB/lid fastener type -- UNCHANGED M2.5 self-tap, used for all
//     PCB standoffs (4) + all 4 PCB-lid corner tabs. Reserved
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
interior_x = pcb_length + 2*board_xy_keepout;      // DERIVED = 153.0mm (was 103.0mm pre-Rev-5)
interior_y = pcb_width  + 2*board_xy_keepout;      // DERIVED = 98.0mm (was 53.0mm pre-Rev-5)
base_outer_x = interior_x + 2*wall_t;              // DERIVED = 157.0mm (was 107.0mm pre-Rev-5)
base_outer_y = interior_y + 2*wall_t;              // DERIVED = 102.0mm (was 57.0mm pre-Rev-5)

lid_skirt_inner_x = base_outer_x + 2*fit_clearance;    // DERIVED = 157.4mm (was 107.4mm pre-Rev-5)
lid_skirt_inner_y = base_outer_y + 2*fit_clearance;    // DERIVED = 102.4mm (was 57.4mm pre-Rev-5)
lid_skirt_outer_x = lid_skirt_inner_x + 2*lid_skirt_t; // DERIVED = 161.4mm (was 111.4mm pre-Rev-5)
lid_skirt_outer_y = lid_skirt_inner_y + 2*lid_skirt_t; // DERIVED = 106.4mm (was 61.4mm pre-Rev-5)
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
//     formulas/values from Rev 2; repositioned to the real MH-1..4 CORNER
//     coordinates -- REV 5 FIX (MISS-034): MH-5/6 never existed on the
//     real board (see mount_holes note above), so the "MH-5/6 do not get
//     tabs" carve-out is now moot, not just inapplicable. ---
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
    [  8.0,  8.0, -1], // near MH-1, front-left
    [142.0,  8.0, -1], // near MH-2, front-right
    [142.0, 87.0, +1], // near MH-3, rear-right
    [  8.0, 87.0, +1], // near MH-4, rear-left
];

// Rev 3.1 FIX (MISS-010, HIGH -- Independent Mechanical Review Cycle 1
// (Rev 3), validation/design-review.md "Mechanical Reviewer -- Cycle 3",
// Finding 3): a genuine, non-zero 190.06mm^3 solid-solid overlap between
// base_tabs() and lid_shell()'s own skirt band exists at all 4 tab corners
// (confirmed by direct boolean intersection this session -- see the
// rationale block at lid_shell() below for the full geometric derivation).
// This was disclosed by this Mechanical Lead as a pre-existing, inherited
// Rev 2 characteristic in an earlier Rev 3 report ("flagged, not fixed, out
// of scope") but was not, at that time, entered into
// validation/open-issues.md's own tracked backlog -- the Reviewer's Cycle 3
// pass added it there as MISS-010 and required it be fixed this cycle,
// since this Mechanical Lead is already reworking this exact geometry
// class. tab_relief_margin below is the fix's only new parameter -- see
// lid_shell() for how it is used.
tab_relief_margin = 1.0; // mm. ASSUMPTION: same "small explicit overshoot"
                  // convention used throughout this file for cut-tool
                  // oversizing (e.g. the "+1"/"+2" pattern on cylinder/cube
                  // heights elsewhere) -- guarantees the relief notch (see
                  // lid_shell()) fully clears the skirt band's own Y-extent
                  // with margin on the open-air side, so no coincident/
                  // tangent cut face is left at the skirt's own outer
                  // (Y=lid_y0 or Y=lid_y0+lid_skirt_outer_y) face. Applied
                  // only on the open-air side of each notch; the inner-face
                  // side of the skirt band coincides exactly with the
                  // notch's own boundary by construction (see derivation),
                  // which is the same kind of exact-coincident boolean
                  // face already used safely elsewhere in this file (e.g.
                  // the flywheel floor/wall Z=fw_floor_top interface).

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
                    // physically the SAME clearance gap B5's axial margin
                    // already describes -- not a fresh, separate number.
                    // Rev 3.1 correction (MISS-008, see §7 of the companion
                    // spec file): this is the gap between the TOP of the
                    // hub collar and the BOTTOM of the flywheel disk --
                    // i.e. the collar sits directly on fw_motor_bell_top
                    // (see reference_motor_flywheel() below, unchanged),
                    // then this standoff gap, then the disk (see
                    // fw_disk_bottom below). The Rev 3 comment here
                    // previously (incorrectly) called this "the
                    // motor-bell-top-to-disk-bottom gap" outright, which is
                    // what led fw_disk_bottom to omit fw_hub_collar_h
                    // entirely (MISS-008, CRITICAL) -- the TRUE
                    // motor-bell-top-to-disk-bottom gap is
                    // fw_hub_collar_h + fw_hub_standoff (=9.0mm), exactly
                    // the quantity fw_shaft_exposed_len_needed below
                    // already, correctly, computes.
fw_hub_collar_od = 8.0; // mm. ASSUMPTION -- generic off-the-shelf
                    // set-screw shaft-collar class part.
fw_hub_collar_h  = 6.0; // mm. ASSUMPTION.
fw_shaft_exposed_len_needed = fw_hub_collar_h + fw_hub_standoff; // DERIVED
                    // = 9.0mm -- REQUIRED but UNVERIFIED against the real
                    // M1 part's actual exposed shaft length above its
                    // bell top (interface file does not state this
                    // dimension). Flagged in spec file §12 for pre-build
                    // verification. This formula was ALWAYS correct -- it is
                    // the formula MISS-008 used as the independent proof
                    // that fw_disk_bottom (below) was wrong, since the two
                    // formulas contradicted each other within this same
                    // file until the Rev 3.1 fix below.

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
                      // ~29.5mm below the disk's rotation zone (37.5-42.0mm
                      // post Rev-3.1/MISS-008 fix; was ~23mm below the old,
                      // incorrect 31.5-36.0mm zone -- the duct's own Z
                      // itself is unaffected by that fix, only the disk's
                      // position moved further away, i.e. this only grows
                      // the existing margin, never shrinks it).
wire_bridge_w = 12.0; // mm, X-span of a short rectangular bridge/gusset
                      // block this Mechanical Lead adds connecting the
                      // flywheel bay's own PLAIN WALL (outer radius
                      // fw_bay_outer_r=43.5mm -- NOT the wider flange band,
                      // which only exists near the very top, nowhere near
                      // this duct's low Z) to the PCB bay's own south wall.
                      // See the bridge_y_lo/bridge_y_hi derivation and
                      // motor_wire_bridge_solid()/motor_wire_duct_void()
                      // below (Rev 3.1: split from a single
                      // motor_wire_bridge() module per the MISS-009 fix)
                      // for the full derivation, including a real
                      // motor-vs-bridge collision this Mechanical Lead caught
                      // and fixed in an earlier Rev 3 session via
                      // render+numeric spot-check (an earlier draft anchored
                      // this block on the bay's own rotation-axis CENTER
                      // instead of the wall's outer
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
// REV 5 DISCLOSURE (MISS-043, 2026-09-04, flagged by independent
// cross-session review): the numbers in the paragraph immediately above
// are BOTH stale after the MISS-034 PCB resize, but only ONE side is
// honestly re-derivable this pass. The CHOSEN option's own real footprint
// is corrected below (157x207mm = 32,499mm^2, computed from this file's
// own current base_outer_x/shell_footprint_y -- see those variables'
// own updated comments) -- the pre-Rev-5 "107x162mm" figure understated
// it by ~47%, not a rounding difference. The REJECTED "centroid-aligned"
// alternative's own "~88.5mm motor-zone X-centroid" and "140x160mm-class"
// figures CANNOT be honestly recomputed here: both depend on the Rev 3
// "motor zone" concept (a proposed X=70-100mm zone on the superseded
// 100x50mm board), which MISS-037 (`validation/open-issues.md`) already
// separately flags as not describing the real board's own actual
// component placement at all. Re-deriving a real, current centroid-aligned
// comparison would require first resolving MISS-037's own broader gap
// (real connector/component positions), not something this narrower
// annotation fix can respond to in isolation. **Net effect: whether
// width-centering still wins on footprint at the real 150x95mm scale is
// UNVERIFIED in either direction** -- the conclusion is preserved as
// this file's own historical decision (still fully valid: `fw_cx`'s own
// formula centers on the PCB bay regardless of board size, so nothing
// about the actual built geometry depends on this comparison being
// re-checked), but the comparison itself should not be read as
// re-confirmed at the current scale.
fw_cx = base_outer_x / 2;              // DERIVED = 78.5mm (was 53.5mm pre-Rev-5)
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
shell_footprint_x = base_outer_x;               // DERIVED = 157.0mm (was
                    // 107.0mm pre-Rev-5; main shell only -- PCB bay +
                    // flywheel bay walls/flange, excludes every fastener
                    // protrusion below)
shell_footprint_y = pcb_bay_y0 + base_outer_y;  // DERIVED = 207.0mm (was 162.0mm pre-Rev-5)

// True assembled envelope, ALL protrusions included. X: the PCB LID's own
// skirt (lid_skirt_outer_x) turns out to be the single widest X feature in
// this whole assembly -- wider even than the containment cap's own skirt
// (fw_flange_dia+2*fit_clearance+2*wall_t = 109.4mm) -- both were checked;
// the lid wins by 2.0mm (REV 5: now by 52.0mm, since lid_skirt_outer_x
// grew with the board while the containment cap's own skirt did not).
// Y: the containment cap's skirt sets the southern
// extreme (it overhangs slightly past the flywheel flange's own Y=0
// tangent point); the PCB lid's own corner tabs set the northern extreme
// (the WIDER lid_tab_project reaches further out than the base's own
// tab_project -- the same "lid tab is the true outward extreme" finding
// Rev 2 first made, re-confirmed unchanged here since neither
// tab_project/lid_tab_project changed).
assembled_envelope_x = lid_skirt_outer_x;                  // DERIVED = 161.4mm (was 111.4mm pre-Rev-5)
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
// Rev 3.1 FIX (MISS-008, CRITICAL -- Independent Mechanical Review Cycle 1
// (Rev 3), validation/design-review.md "Mechanical Reviewer -- Cycle 3",
// Finding 1): fw_disk_bottom below previously read
// `fw_motor_bell_top + fw_hub_standoff` (=31.5mm), which OMITTED
// fw_hub_collar_h (=6.0mm) entirely -- an internal self-contradiction
// against this same file's own fw_shaft_exposed_len_needed formula above
// (`fw_hub_collar_h + fw_hub_standoff`), which already, correctly, treats
// the collar height as additive between the motor bell top and the disk.
// Empirically confirmed (both by the Reviewer and independently
// re-confirmed by this Mechanical Lead this revision, via a standalone
// openscad intersection() of the two literal solids at their pre-fix
// modeled coordinates: collar Z=[28.5,34.5], disk Z=[31.5,36.0], overlap
// volume ~150.4mm^3 this session / ~145.0mm^3 Reviewer's trimesh figure /
// ~150.8mm^3 hand-calc, all within normal STL-facet-discretization
// tolerance of each other) that the pre-fix disk position physically
// collided with the hub collar it is supposed to rest on top of, making
// the flywheel unassemblable per this file's own §14 Assembly Step 5.
// FIXED by adding the missing `+ fw_hub_collar_h` term below -- every
// downstream value in this Z-stack is a FORMULA (not a hardcoded number),
// so the +6.0mm correction cascades automatically through fw_disk_top,
// fw_clearance_top, fw_cap_outer_top, fw_wall_h and fw_bay_total_height at
// render time; the trailing "// N.N" comments below have been updated to
// the new, correct values so they stay human-readable without re-deriving
// them by hand. This re-verified, corrected Z-stack is re-checked
// end-to-end against REQ-306 (vertical clearance) and REQ-403 (containment
// envelope sizing) in dimensional-spec.md §7/§8 -- see that file's own
// Rev 3.1 changelog entry for the full re-derivation, not just this one
// formula in isolation.
fw_floor_top          = floor_t;                                    // 2.0
fw_motor_platform_top = fw_floor_top + motor_platform_h;            // 10.0
fw_motor_bell_top     = fw_motor_platform_top + m1_body_h;          // 28.5
fw_disk_bottom        = fw_motor_bell_top + fw_hub_standoff
                          + fw_hub_collar_h;                        // 37.5
                        // (was 31.5 pre-fix, MISS-008 -- see note above.
                        // This now correctly stacks: motor bell top, then
                        // the hub collar's own full height, THEN the
                        // fw_hub_standoff gap, then the disk -- matching
                        // fw_shaft_exposed_len_needed's own additive
                        // formula above, order-of-addition doesn't matter.)
fw_disk_top           = fw_disk_bottom + fw_t;                      // 42.0
                        // (was 36.0 pre-fix)
fw_clearance_top      = fw_disk_top + fw_axial_margin_per_face;     // 45.0
                        // (was 39.0 pre-fix; = the cap's own inner face,
                        // i.e. where the rotation-clearance keep-out
                        // volume actually ends)
fw_cap_outer_top      = fw_clearance_top + containment_wall_t;      // 49.0
                        // (was 43.0 pre-fix -- the full +6.0mm shift, not
                        // merely the +2.0mm that would just barely stop
                        // the clearance envelope from poking out the cap's
                        // old top; the cap must still have a full
                        // containment_wall_t of material ABOVE the
                        // corrected clearance_top, hence the full +6.0mm)
fw_wall_h             = fw_clearance_top - fw_floor_top;            // 43.0
                        // (was 37.0 pre-fix; base's own cylindrical wall
                        // height, floor-top to the underside where the
                        // cap's skirt begins)
fw_bay_total_height   = fw_cap_outer_top;                           // 49.0mm
                        // (was 43.0mm pre-fix)

// ----------------------------------------------------------------------
// 2B. REV 4 -- FREE-ROTATION SUPPORT MECHANISM (new, additive only).
//     Everything in Sections 1-2 above is Rev 3, UNCHANGED. This block adds
//     a bought BC Precision 4LS-3 lazy-susan turntable ball bearing
//     (human-approved, bom/component-selection.md "Free-Rotation Support
//     Mechanism," Candidate A), a new mounting flange fused BELOW the
//     existing base()'s own floor (extends -Z into previously-empty
//     territory only -- does not resize/move/remove any Rev 3 solid), and
//     a new 4th printed piece (a fixed stand plate). Full rationale,
//     CG/tip-over analysis, and self-check: bench-imu-01-dimensional-spec.md
//     Section 18. Interface-level summary: hardware/mechanical-interface.md
//     Part C.
// ----------------------------------------------------------------------

// --- Bearing (BC Precision 4LS-3) physical facts ---
brg_od = 101.6; // mm. CONFIRMED (DS-BRG-001, "4in" nominal OD).
brg_id = 55.1;  // mm. CONFIRMED (DS-BRG-001, 2.170in center hole, thru
                // both plates -- this is the coaxial REQ-113 tether bore).
brg_t  = 7.9;   // mm. CONFIRMED (DS-BRG-001, 5/16in overall thickness,
                // both plates + captive ball race).
brg_load_cap_kg = 136.1; // kg (= 300lb). CONFIRMED (DS-BRG-001). Not used
                // in any modeled dimension below -- recorded here only for
                // traceability alongside the other bearing facts.
brg_mass_est = 130.0; // g. ESTIMATE, NOT a manufacturer figure -- no
                // weight is published anywhere on DS-BRG-001. Derived this
                // session from a further chain of estimates (2x stamped
                // galvanized-steel plates @ ~1.2mm gauge ESTIMATE + a
                // ~24x6mm steel ball race ESTIMATE); weak/wide (~77-160g),
                // non-citation-grade web corroboration only. See
                // hardware/mechanical-interface.md Part C1 for the full
                // derivation -- flagged explicitly as a chain of estimates,
                // not a measurement.
brg_screw_major_dia = 3.5; // mm. CONFIRMED reference figure only (a
                // standard #6 machine-screw major diameter, ANSI/ASME
                // B1.1) -- NOT itself a bearing-specific fact; used solely
                // to DERIVE bmount_pilot_dia below.
n_bmount_bolts = 4; // count. ASSUMPTION (Evidence ID DS-BRG-007) --
                // generic lazy-susan-hardware-CLASS mounting convention (4
                // holes evenly spaced per plate), NOT this specific SKU's
                // own confirmed pattern -- DS-BRG-001's own product page
                // does not publish a hole count/spacing for either plate.
                // See hardware/mechanical-interface.md Part C1 for the
                // full provenance/hedging. Because the true hole positions
                // are unknown, bmount_flange()/stand_plate() below are
                // modeled as continuous ANNULAR bands, not discrete bosses
                // at hard-coded points -- a real hole can be field-drilled
                // anywhere on the modeled bolt circle regardless of
                // whether this default count/spacing is exactly right.

// --- New mounting flange (added below the existing base() floor) ---
bmount_flange_or = fw_flange_or; // DERIVED = 52.5mm. Reuses the existing
                // flange-band radius exactly (rather than inventing a new,
                // close-but-different value) -- already clears the
                // bearing's own 50.8mm OD radius (brg_od/2) with margin.
bmount_flange_ir = 28.0; // mm. ASSUMPTION -- clears the bearing's own
                // 27.55mm ID radius (brg_id/2) with a small working
                // margin; also serves as the coaxial REQ-113 tether
                // pass-through bore (hardware/mechanical-interface.md Part
                // C6). Verified this session (see bmount_flange() below)
                // to sit entirely inside fw_bay_outer_r (43.5mm) and
                // entirely outside every existing motor_platform() cutout
                // (m1_bolt_square/2 + m1_mount_hole_dia_clear/2 ~= 7.7mm
                // from center; the central shaft hole is smaller still) --
                // no interference with any Rev 3 cutout.
bmount_flange_t = 6.0; // mm. ASSUMPTION -- sized to host a
                // bmount_pilot_depth-deep blind pilot hole with a 1.0mm
                // margin, mirroring this file's own standoff_h /
                // standoff_pilot_depth (6.0mm/5.0mm) precedent above.
bmount_fuse_overlap = 1.0; // mm. ASSUMPTION -- mirrors this file's own
                // bridge_fuse_overlap (2.0mm) convention: a deliberate
                // volumetric overlap INTO the pre-existing floor disc's
                // own solid material (Z=[0,+bmount_fuse_overlap] instead of
                // a knife-edge touch at Z=0), so the new flange achieves a
                // genuine CSG union with motor_platform()'s own floor
                // disc, not a fragile coincident-face join. A smaller
                // margin than bridge_fuse_overlap is judged adequate here
                // because this joint is a full annular band fusing against
                // a full solid disc, not a narrow bridge fusing against a
                // curved wall's tangent line -- a materially more
                // forgiving geometry for boolean robustness.
bmount_bolt_circle_r = 40.0; // mm. ASSUMPTION -- default/documented
                // pattern only (DS-BRG-007's hole COUNT, not this SKU's
                // own confirmed hole POSITIONS); sits mid-band between
                // bmount_flange_ir (28.0mm) and bmount_flange_or (52.5mm).
                // MUST be verified against the real bearing before
                // manufacture -- see hardware/mechanical-interface.md Part
                // C1/C2.
bmount_pilot_dia = 2.8; // mm. ASSUMPTION = 0.8 * brg_screw_major_dia
                // (3.5mm) -- same 80% pilot-to-major-diameter ratio as
                // this file's own standoff_pilot_dia/M2.5 self-tap joint
                // (2.0/2.5 = 80%), applied here for consistency rather
                // than inventing a new ratio.
bmount_pilot_depth = 5.0; // mm. ASSUMPTION = bmount_flange_t - 1.0mm
                // blind margin, numerically identical in pattern to
                // standoff_pilot_depth = standoff_h - 1.0mm above. Reused
                // as-is for the stand plate's own mirror-case pilot holes
                // below (same fastener class/joint, see C5).

// MANUFACTURABILITY FINDING, caught and disclosed this session (NOT a
// clean pass -- see bmount_flange() module below for the full geometric
// reasoning, and bench-imu-01-dimensional-spec.md Section 18.4/18.5 for
// the complete analysis + 3 rejected alternatives): motor_platform()'s own
// floor disc (fw_bay_outer_r=43.5mm radius) is SOLID all the way to its
// own center (minus its small M1-mount/shaft cutouts, all well inside
// bmount_flange_ir=28.0mm). Because bmount_flange() is hollow for its full
// height at r<bmount_flange_ir, fusing it directly beneath that disc
// creates a hidden internal transition -- solid disc material directly
// above an open bore -- spanning a ~56mm diameter (2*bmount_flange_ir),
// which exceeds this file's own max_overhang_deg (45 deg from vertical)
// and max_bridge_span (10.0mm) rules by a wide margin when printed
// floor-down (the ONLY viable orientation -- flipping would break the
// existing standoffs, which need floor-down printing). Resolution adopted:
// keep the flange fused with the base as ONE continuous print job
// (preserves the "4 total printed pieces" framing and the additive-only
// constraint), but require slicer-generated INTERNAL SUPPORT MATERIAL for
// this one hidden, non-mating, non-precision internal surface -- fully
// reachable/removable through the bore's own straight-through opening, not
// a blind cavity. This is recorded as a genuine, confirmed manufacturability
// caveat on the combined base+flange print, not a silent/clean pass.

// --- New 4th printed piece: fixed stand plate ---
stand_plate_or = 60.0; // mm. DECIDED from a from-scratch CG/tip-over
                // radius sweep (50-80mm candidates), NOT matched to
                // DS-BRG-001's own generic "12-25in suggested top
                // diameter" (that figure is a heavy-furniture stability
                // rule of thumb for a completely different load class, not
                // applicable at this rig's ~600g computed scale). Chosen
                // for a ~6.2x static margin (stand_plate_or / computed CG
                // offset) -- see hardware/mechanical-interface.md Part
                // C3/C4 and bench-imu-01-dimensional-spec.md Section 18.3
                // for the full analysis, all intermediate numbers, and the
                // disclosed Rev-3-plastic-mass-estimate discrepancy that
                // total mass is computed against.
stand_plate_ir = bmount_flange_ir; // DERIVED = 28.0mm -- keeps the REQ-113
                // tether pass-through bore continuous/coaxial all the way
                // from the flange through the bearing to the stand plate.
stand_plate_t = 6.0; // mm. ASSUMPTION, mirrors bmount_flange_t. Unlike the
                // flange, the stand plate is a uniform-cross-section
                // annulus for its ENTIRE thickness (fuses/mates with
                // nothing else) -- no analogous internal-overhang
                // manufacturability concern; prints flat, either face
                // down, no support needed.
stand_bolt_circle_r = bmount_bolt_circle_r; // DERIVED = 40.0mm -- same
                // default bolt pattern as the flange (hardware/mechanical-
                // interface.md Part C4). Geometric check: sits 20.0mm
                // inside stand_plate_or and 12.0mm outside stand_plate_ir,
                // both generous margins -- no manufacturability concern.

// --- Global Z-stack, free-rotation mechanism (continues below the
//     existing Z=0 = old base floor; matches the flywheel-bay Z-stack's
//     own "every value a formula, not a hardcoded number" convention
//     above) ---
brg_top_z    = -bmount_flange_t;           // DERIVED = -6.0mm. Bearing's
                // own top (ROTATING) plate sits flush against the new
                // flange's own bottom face.
brg_bottom_z = brg_top_z - brg_t;          // DERIVED = -13.9mm. Bearing's
                // own bottom (STATIONARY) plate.
stand_plate_top_z    = brg_bottom_z;               // DERIVED = -13.9mm --
                // stand plate's own top face sits flush against the
                // bearing's own bottom (stationary) plate.
stand_plate_bottom_z = stand_plate_top_z - stand_plate_t; // DERIVED
                // = -19.9mm (old Z=0 frame). This is the new system's true
                // ground plane -- see hardware/mechanical-interface.md
                // Part C3 for the full CG/tip-over numbers computed
                // against it.

// ----------------------------------------------------------------------
// 2C. REV 4.1 -- MITIGATIONS FOR INDEPENDENT MECHANICAL REVIEW CYCLE 5's
//     2 BLOCKING HIGH FINDINGS (validation/design-review.md "Mechanical
//     Reviewer -- Cycle 5"; validation/open-issues.md MISS-023/MISS-024).
//     Everything in Sections 1-2B above (Rev 3 AND Rev 4) is UNCHANGED --
//     this is a new, additive sub-revision responding to that review, not
//     a rework. Full derivation/rationale/tables for every number below:
//     bench-imu-01-dimensional-spec.md Sections 18.12 (MISS-023) and 18.13
//     (MISS-024). This block states only the decided values plus a brief
//     pointer, matching this file's own established convention.
// ----------------------------------------------------------------------

// --- MISS-023 (HIGH): REQ-407(b) pinch-point/rotating-overhang hazard was
//     never assessed. Fix: a new stationary annular guard, pinch_guard()
//     below. ---
rotating_env_max_r = 176.259; // mm. REV 5 RE-MEASURED (MISS-034 side
                // effect, this session): was 126.424mm (Rev 4.1 figure,
                // quoted below unchanged for its own history) -- the
                // Rev 5 PCB-bay resize (100x50mm -> real 150x95mm) grows
                // the rotating assembly's own farthest point (still a PCB
                // LID corner tab, per the note below) outward by
                // +49.8mm/+39.4%. Re-measured with the exact same method
                // Rev 4.1 used (see the ORIGINAL Rev 4.1 note immediately
                // below, unedited, for that method's own full description)
                // -- re-run fresh this session against the resized
                // assembled-frame STLs, independently confirmed by BOTH
                // `trimesh` and `numpy-stl` agreeing to <0.001mm. **This
                // change directly stales MISS-023's own ACCEPTED-RISK
                // coverage-percentage numbers (77.7% -> 35.0% for the
                // SAME, unchanged pinch_guard_or=115.0mm) -- see MISS-023's
                // own re-opened entry in validation/open-issues.md and
                // pinch_guard_or's own comment below. Per this project's
                // established REQ-408 "a disposition does not auto-extend
                // to a materially changed input" precedent, this was NOT
                // silently treated as still-covered by the old sign-off.**
                //
                // ORIGINAL Rev 4.1 note (unedited, describes the method that
                // was re-run unchanged this session): CONFIRMED via a
                // dedicated isolated-rotating-solid mesh analysis: unioned
                // ONLY the solids that actually rotate with the bearing's
                // top plate
                // (base(), pcb_lid(), containment_cap(), bmount_flange() --
                // EXCLUDES the stationary stand_plate()), rendered with
                // `openscad --backend=manifold` (manifold, NoError), then
                // measured max XY-distance from the bearing axis (fw_cx,
                // fw_cy) independently with BOTH the `trimesh` and
                // `numpy-stl` Python libraries, which agreed exactly. This
                // CORRECTS the Cycle 5 Reviewer's own hand-derived 115.9mm
                // figure, which used a pure Y-axis distance and missed the
                // actual farthest point's (a base_tab() corner) own
                // X-offset from the bearing axis -- the true Euclidean
                // distance is ~9%/+10.5mm larger. See spec 18.12 for the
                // full method and both tools' output. NOT used to size any
                // geometry directly below (see pinch_guard_or's own, more
                // conservative, sizing decision) -- kept as a named,
                // traceable constant so cable_wrap_circumference below
                // stays derived/re-computable rather than a second,
                // independently-hardcoded copy of the same figure.
pinch_hazard_min_z_clear = 19.9; // mm. REV 5 RE-VERIFIED (this session, NOT
                // assumed unchanged just because it looks Z-only): re-ran
                // the SAME face-centroid, 1mm-radius-bin height sweep
                // against the resized rotating assembly's real STLs, over
                // the NEW radius range [60, 176.259]mm. Result: still
                // exactly 19.9mm -- confirmed for a real physical reason,
                // not a coincidence: this floor is set by the PCB bay
                // wall's own floor-level corner sitting at global Z=0 (the
                // base's own external bottom face), which is independent of
                // the bay's XY footprint -- growing the PCB bay in X/Y
                // does not move its own floor plane in Z. Original Rev 4.1
                // method description (unedited): CONFIRMED via a fine
                // (1mm-radius-bin, face-centroid-sampled -- denser than
                // vertex-only sampling) height-vs-radius sweep of the SAME
                // isolated rotating solid above: the GLOBAL MINIMUM height
                // of the rotating envelope above the desk plane, over
                // every point with radius in [stand_plate_or,
                // rotating_env_max_r] (i.e. every radius a stationary
                // guard could occupy), confirmed to hold at this SAME
                // value across multiple distinct radius bins -- a genuine
                // floor, not a single-radius coincidence. The true limiting
                // feature is the PCB-bay wall's own floor-level corner, NOT
                // the base_tab() tabs as a first glance at "tallest
                // features" might suggest. See spec 18.12.
pinch_guard_z_margin = 5.0; // mm. ASSUMPTION -- an explicit safety
                // clearance margin between pinch_guard()'s own top edge
                // and pinch_hazard_min_z_clear, deliberately separate from
                // fit_clearance above (which governs mating-part print
                // fit, not clearance to a moving/rotating hazard -- a
                // different concern at a different scale).
pinch_guard_ir = stand_plate_or; // mm. DERIVED = 60.0mm -- flush-adjacent
                // to the existing stand plate's own outer edge (a
                // touching, non-overlapping boundary). By design the two
                // remain SEPARATE, unfastened, desk-resting parts this
                // pass (not unioned/keyed together) -- a disclosed
                // limitation; see spec 18.12.
pinch_guard_or = 176.3; // mm. GROWN this session (was 115.0mm) --
                // **human Chief Engineer (Kyosuke) DIRECT DECISION**,
                // verbatim: "完全カバーを選んでください" ("please choose
                // full coverage"), relayed via the cross-session HITL
                // channel and recorded in MISS-023's own resolved entry
                // in validation/open-issues.md with full citation. This
                // selects the trade-off table's own "176.3mm / 100% /
                // 0mm gap / ~1268g[NOTE: re-verify, see below]" row
                // (candidates 115/130/140/150/157.9/165/176.3mm were
                // presented; this is the full-closure end of that same,
                // already-reviewed table -- not a newly-invented number).
                // 176.3mm is a small, deliberate round-up from the
                // confirmed 176.259mm swept radius (rotating_env_max_r
                // above) -- chosen to exactly match the pre-reviewed
                // table entry rather than introduce an unreviewed value;
                // note the actual non-overlap guarantee is Z-based, not
                // radial (pinch_guard_h is independently bounded below
                // pinch_hazard_min_z_clear -- see that constant's own
                // comment), so this 0.041mm margin is not itself load-
                // bearing for collision-avoidance, only a clean round
                // number matching the reviewed table. VERIFIED this
                // session (not assumed from the table's own earlier
                // ESTIMATE): re-rendered full_ring() and re-confirmed
                // EMPTY boolean intersection with the complete rotating
                // envelope (same method Cycle 6/this session's own
                // MISS-023 re-opening used); recomputed coverage = 100%,
                // residual gap = 0mm (guard_or now exceeds
                // rotating_env_max_r by construction); recomputed mass
                // via direct STL export + trimesh (see
                // dimensional-spec.md 18.12 for the actual measured
                // figure, NOT the table's own earlier back-of-envelope
                // estimate, which this session's real measurement may
                // differ from slightly).
pinch_guard_h = pinch_hazard_min_z_clear - pinch_guard_z_margin; // mm.
                // DERIVED = 14.9mm. By construction (a stated margin below
                // the CONFIRMED global-minimum rotating-envelope height
                // above) this guard cannot contact the rotating assembly
                // at ANY radius in [pinch_guard_ir, pinch_guard_or] or ANY
                // rotation angle. Uniform height (no shelf/rim step) --
                // the global-floor confirmation above means a stepped
                // profile is unnecessary.
pinch_guard_quadrant_margin = 10.0; // mm. ASSUMPTION -- residual radial
                // safety margin the print_layout quadrant-cutting tool's
                // chord keeps beyond pinch_guard_or at the wedge's own
                // angular midpoint, on top of the geometrically-exact
                // r_cut = pinch_guard_or/cos(half_angle) minimum (see
                // pinch_guard()'s own SELF-CAUGHT FIX comment -- this
                // variable's role changed this session: it used to be
                // added directly to pinch_guard_or as if that alone
                // guaranteed full coverage, which a real re-measurement
                // showed it did not).

// --- NEW finding, this session (MISS-047): assembled_envelope_x/_y above
//     (Section 2B, defined before pinch_guard_or exists -- OpenSCAD's own
//     strictly sequential top-down variable evaluation, confirmed
//     empirically this session, does not allow referencing pinch_guard_or
//     there) have NEVER included pinch_guard()'s own footprint in the
//     "true assembled envelope" reading, a gap present since Rev 4.1 (the
//     guard's own introduction) and NOT specific to this session's
//     changes -- re-checked: even at the OLD pinch_guard_or=115.0mm, the
//     guard's own diameter (230.0mm) already exceeded
//     assembled_envelope_x (161.4mm), meaning that reading was already
//     wrong before this session touched anything. This went unnoticed
//     because the gap was small relative to the guard's own prior size
//     and no prior review's own REQ-308 check happened to compare
//     against the guard specifically. Impossible to keep ignoring now
//     that MISS-023's own full-closure fix (176.3mm) makes the guard the
//     overwhelmingly dominant feature. Fixed here (not by hand-editing
//     assembled_envelope_x/_y above, which would break their own
//     documented "shell/lid/cap-only" reading that other, still-valid
//     history/citations point at) by defining the TRUE overall envelope
//     as a further min()/max() reduction against the guard's own
//     independently-computed circular footprint -- so this stays
//     parametrically correct even if pinch_guard_or is ever revised
//     again, rather than hardcoding "the guard always wins" as a new
//     silent assumption.
guard_envelope_x_min = fw_cx - pinch_guard_or; // mm
guard_envelope_x_max = fw_cx + pinch_guard_or; // mm
guard_envelope_y_min = fw_cy - pinch_guard_or; // mm
guard_envelope_y_max = fw_cy + pinch_guard_or; // mm
true_assembled_envelope_x_min = min(lid_x0, guard_envelope_x_min); // mm
true_assembled_envelope_x_max = max(lid_x0 + lid_skirt_outer_x, guard_envelope_x_max); // mm
true_assembled_envelope_x = true_assembled_envelope_x_max - true_assembled_envelope_x_min; // mm. DERIVED = 352.6mm (was 161.4mm reading above, now superseded -- see this block's own header comment)
true_assembled_envelope_y_min = min(assembled_envelope_y_south, guard_envelope_y_min); // mm
true_assembled_envelope_y_max = max(assembled_envelope_y_north, guard_envelope_y_max); // mm
true_assembled_envelope_y = true_assembled_envelope_y_max - true_assembled_envelope_y_min; // mm. DERIVED = 352.6mm (was 215.6mm reading above, now superseded)
                // Both readings now come out to the SAME 352.6mm value --
                // not a coincidence, but a direct consequence of
                // pinch_guard_or (176.3mm) alone exceeding, in EVERY
                // direction from its own center (fw_cx, fw_cy), the
                // distance to every other feature's own previously-
                // computed extreme point (confirmed by the min()/max()
                // calls above resolving to the guard's own bounds in
                // every case, not asserted) -- the guard is a full,
                // XY-symmetric circle, so once its radius exceeds every
                // other feature's own max reach from that same center,
                // it alone defines a symmetric square bounding envelope.
                // See dimensional-spec.md 3 for the REQ-308 disclosure
                // this now requires (352.6mm is far beyond the ~150mm
                // soft ceiling -- flagged explicitly, not silently
                // passed through, exactly as this fix's own task brief
                // requires).

// --- MISS-024 (HIGH): REQ-407(c)/REQ-113 cable-entanglement/strain hazard
//     for J1/J4 (mounted on base()'s PCB-bay walls, which now rotate with
//     the bearing's top plate) was never assessed. Fix: a quantified
//     turn-count limit + service-loop spec (procedural), a visual turn-
//     counting index pointer, and a strain-relief cable-tie anchor point
//     near each connector (both new, additive geometry). ---
cable_wrap_circumference = 2 * PI * rotating_env_max_r; // mm. DERIVED
                // ~= 1107.52mm (REV 5: was 794.345mm pre-MISS-034-resize --
                // this is a pure formula of rotating_env_max_r, so it
                // cascaded automatically once that constant was
                // re-measured above; no separate edit needed here beyond
                // this comment's own updated numbers).
                // CONSERVATIVE (safe-direction) model: this
                // assumes the externally-routed J1/J4 cable winds at the
                // rotating assembly's own LARGEST reachable radius
                // (rotating_env_max_r), not the smaller radius of the J1/
                // J4 connectors themselves (~97.1mm, computed in spec
                // 18.13) -- the cable more plausibly drapes against/winds
                // around the rotating body's own outermost accessible
                // surface than stays pulled taut at the connector's own
                // radius, so this OVER-estimates (never under-estimates)
                // cable consumed per turn, the safe direction for a limit
                // meant to prevent running out of slack. See spec 18.13.
pinch_guard_turn_limit = 3; // full turns, single direction, before
                // mandatory manual re-centering. DECIDED -- balances
                // REQ-113's own qualitative "several full turns" language
                // against a practical, storable service-loop length
                // (cable_service_loop_min below). This is a PROCEDURAL
                // constraint, NOT a hardware limit switch/hard stop --
                // a hard mechanical stop would defeat REQ-011/012's own
                // continuous-rotation purpose, so this is deliberately
                // the correct category of fix (monitoring/procedure, not
                // a kinematic limit). See spec 18.13 for the re-centering
                // procedure and the honest disclosure that this does NOT
                // achieve REQ-012's aspirational "ideally continuous/
                // unlimited" rotation case.
cable_service_loop_min = 3.75; // meters. REV 5 FIX (MISS-034 side effect,
                // this session): was 2.5m, DECIDED against the OLD
                // cable_wrap_circumference (794.345mm) with a 4.7% margin
                // over the exact 2.383m requirement. The Rev 5 PCB-bay
                // resize grew rotating_env_max_r (+39.4%), which pushed the
                // exact requirement to `pinch_guard_turn_limit *
                // cable_wrap_circumference` = 3*1.10752m = 3.3226m -- the
                // OLD 2.5m spec is now 0.823m SHORT of that, not
                // "comfortably above" it. This is an unambiguous,
                // safe-direction, no-geometry-tradeoff fix (a longer
                // recommended service loop has no downside, unlike
                // pinch_guard_or's own footprint/mass trade-off below) --
                // applied directly rather than left as an open question.
                // New value gives 3.75-3.3226=0.427m/12.9% spare, a
                // comparable-or-better margin than the original 4.7%. NOT
                // a modeled/geometric dimension (no reasonable enclosure-
                // scale feature enforces a cable length) -- recorded here,
                // rather than only in prose, purely so the numeric chain
                // from rotating_env_max_r through to this operational
                // requirement stays in one traceable, re-computable place.
rot_pointer_w        = 8.0; // mm. ASSUMPTION -- small visual turn-counting
                // index marker on the rotating base's own north wall
                // (rotation_index_pointer() below); dimensions are not
                // derived from any requirement, only checked for
                // clearance against neighboring features (see module).
rot_pointer_project  = 6.0; // mm. How far the pointer projects outward
                // from the wall face (+Y).
rot_pointer_h        = 6.0; // mm. Pointer height (Z), centered on the
                // wall's own mid-height.
cable_anchor_project    = 8.0; // mm. ASSUMPTION -- small strain-relief
                // zip-tie anchor tab, one near J1 and one near J4
                // (cable_anchor_tab() below); a simple, conceptual
                // mitigation feature (targets the "yanks the connector"
                // failure mode directly), not a precision part --
                // dimensions are not derived from any requirement, only
                // checked for clearance against the existing J1/J4
                // cutouts and pcb_lid(). SELF-CAUGHT CORRECTION (within
                // this same session, before handoff): an earlier draft
                // value of 4.0mm here left only (4.0-3.0)/2=0.5mm of wall
                // around cable_anchor_hole_dia's own through-hole in this
                // projection direction -- a genuine violation of this
                // file's own min_wall_t=2.0mm rule (§2/§13.1), caught by
                // re-checking this module's own printability rather than
                // only its clearance-to-other-parts. 8.0mm leaves
                // (8.0-3.0)/2=2.5mm of wall each side -- a 0.5mm margin
                // above the 2.0mm minimum. See spec 18.13 for the full
                // disclosure (this is this pass's own analogue of the Rev
                // 4 internal-overhang finding -- self-caught and fixed
                // pre-handoff here, rather than left for the Reviewer to
                // find).
cable_anchor_w          = 8.0; // mm. Tab width (Y).
cable_anchor_h          = 6.0; // mm. Tab height (Z).
cable_anchor_hole_dia   = 3.0; // mm. ASSUMPTION -- reuses d1_hole_dia's
                // own precedent value elsewhere in this file for a "small
                // pass-through hole," large enough for a standard small
                // cable-tie.
cable_anchor_yc = 15.0; // mm, PCB-bay-local Y (same frame as the existing
                // J1/J4 cutout translate values in pcb_bay_shell() above)
                // -- clears the J1 cutout's own Y-span [23.75, 33.25] by
                // 4.75mm, and the bay's own front edge (Y=0) by 11.0mm.
                // Used for BOTH the J1-side and J4-side anchor tabs (J1
                // and J4 share the same bay-local Y, j1_y = j4_y).
cable_anchor_zc = 10.0; // mm, global/bay-local Z (a shared frame -- see
                // Section 3b's own header comment) -- centered well below
                // pcb_lid()'s own lowest point (base_total_h - lid_lip_h =
                // 18.1mm), so no collision with the lid is possible
                // regardless of how far the tab projects in X.

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

module mid_span_support() {
    // NEW, REV 5 (MISS-043). A solid (no pilot hole -- nothing fastens
    // here) cylindrical pad, exactly `standoff_h` tall, that the board
    // simply RESTS on at its own physical mid-span. See this module's own
    // constants (mid_support_dia/_h) above for the full rationale: this
    // is a passive flex/sag mitigation addressing the physical concern
    // that originally motivated Rev 3's MH-5/6, which the real 4-hole
    // board has no mounting hole to bolt a real standoff into.
    cylinder(d = mid_support_dia, h = mid_support_h);
}

module base_standoffs() {
    // 4 instances (MH-1..4, the real board's own mounting-hole pattern --
    // REV 5 FIX, MISS-034: Rev 3's MH-5/6 never existed on the real board)
    // in the PCB bay's own local frame -- caller (pcb_bay_base()) translates
    // into the shared global frame via pcb_bay_y0.
    for (m = mount_holes)
        translate([board_offset_x + m[0], board_offset_y + m[1], floor_t])
            standoff();
    // NEW, REV 5 (MISS-043): one passive mid-span support pad, centered on
    // the board's own physical midpoint (pcb_length/2, pcb_width/2) --
    // the point of greatest expected sag for a plate supported only at
    // its 4 corners, and confirmed clear of any real component (interface
    // A3: bottom_component_clearance=0, no bottom-side parts populated).
    translate([board_offset_x + pcb_length/2, board_offset_y + pcb_width/2, floor_t])
        mid_span_support();
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

        // Rev 3.1 FIX (MISS-010, HIGH): tab-relief notches, one per
        // base_tabs() corner, cut through the skirt band ONLY (not the
        // roof above it -- unlike the header/button-bay notch above, this
        // is deliberately NOT a full-height cut). Root cause of the defect
        // this fixes: base_tab()'s cube starts flush at the base wall's own
        // outer face (Y=0 or Y=base_outer_y, LOCAL to pcb_bay_base()) and
        // projects outward the FULL tab_project (6.0mm); independently,
        // lid_shell()'s own skirt band occupies a fit_clearance (0.2mm) gap
        // beyond that same wall face plus a further lid_skirt_t (2.0mm) --
        // i.e. the ENTIRE skirt band footprint at a tab's X position is a
        // subset of that tab's own 6.0mm outward projection, over the full
        // lid_lip_h (3.0mm) of shared Z. Confirmed this session via direct
        // coordinate comparison: tab global Y=[99,105] (front) / [162,168]
        // (rear) vs. skirt band global Y=[102.8,104.8] (front/south) /
        // [162.2,164.2] (rear/north, by the same construction on the
        // opposite side) -- each skirt band is fully contained inside its
        // corresponding tab's Y-range, over shared Z=[18.1,21.1] (global) =
        // Z=[0,lid_lip_h] (local to this module) -- a real 8mm(tab width) x
        // 2.0mm(skirt band width) x 3.0mm(lid_lip_h) = 48.0mm^3 solid-solid
        // interference at each of the 4 corners (matches the ~190.06mm^3
        // total reported by the Reviewer, and this Mechanical Lead's own
        // prior 188-192mm^3 hand-recomputation, to within discretization
        // noise). Fix: notch out the skirt band's own material at each
        // tab's X position (widened by tab_relief_margin per side so the
        // notch is guaranteed slightly larger than the tab itself, the same
        // "clear the mating part with margin" logic already used for the
        // containment-cap/base-flange fit elsewhere in this design, see
        // dimensional-spec.md); a true fastening/alignment joint would
        // simply route the skirt AROUND each tab rather than colliding with
        // it -- this is that same relief in solid-model form, not a
        // reduction of either feature's own functional dimension.
        for (p = tab_positions) {
            tx = board_offset_x + p[0];
            dy = p[2];
            // Y-span: the skirt band on the SIDE this tab sits on, widened
            // by tab_relief_margin toward open air only (the inner-cutout
            // side of the band already coincides exactly with this notch's
            // own boundary by construction -- an exact coincident face,
            // the same convention used safely elsewhere in this file).
            notch_y0 = (dy < 0)
                ? lid_y0 - tab_relief_margin
                : lid_y0 + lid_skirt_outer_y - lid_skirt_t - tab_relief_margin;
            notch_h  = lid_skirt_t + 2*tab_relief_margin;
            translate([tx - tab_w/2 - fit_clearance, notch_y0, -1])
                cube([tab_w + 2*fit_clearance, notch_h, lid_lip_h + 1]);
                // Z: local [-1, lid_lip_h] -- 1mm overshoot below the skirt
                // band's own bottom (Z=0, already this module's own open
                // bottom face, so harmless), capped at EXACTLY lid_lip_h on
                // top so the roof above (Z>lid_lip_h) is never touched.
        }
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

// Rev 3.1 FIX (MISS-009, HIGH -- Independent Mechanical Review Cycle 1
// (Rev 3), validation/design-review.md "Mechanical Reviewer -- Cycle 3",
// Finding 2): bridge_fuse_overlap/bridge_y_lo/bridge_y_hi hoisted from
// motor_wire_bridge()'s own local scope (where they lived pre-fix) to
// top-level/file scope, so BOTH the solid bridge block
// (motor_wire_bridge_solid(), below) and the new, separately-and-globally
// subtracted duct void module (motor_wire_duct_void(), further below) can
// share the exact same Y-span numbers -- this sharing is the mechanism the
// fix actually depends on, not just cosmetic reorganization.
bridge_fuse_overlap = 2.0; // mm. ASSUMPTION: FDM-safe guaranteed-fusion
                  // margin pulling the bridge's start point in from the
                  // wall ring's exact (fragile, line-only-contact) tangent
                  // Y so the two solids genuinely overlap across the
                  // bridge's full width, not just a mathematical knife-edge.
                  // (Unchanged value from Rev 3 pre-fix -- this margin
                  // itself was never wrong; only its SCOPE and the
                  // separate duct-void span below needed fixing. This was
                  // originally caught-and-fixed in an earlier Rev 3 session
                  // per MISS-004: an earlier draft had set bridge_y_lo =
                  // fw_cy, the flywheel bay's own ROTATION-AXIS CENTER,
                  // making the "bridge" a 54.5mm-long slab reaching all the
                  // way back across the motor platform/body footprint --
                  // that defect is unrelated to and already resolved prior
                  // to this MISS-009 fix.)
bridge_y_lo = fw_cy + fw_bay_outer_r - bridge_fuse_overlap; // = 94.0mm
bridge_y_hi = pcb_bay_y0 + wall_t; // = 107.0mm, a touch into the PCB bay's
                  // own south wall thickness.
// Resulting bridge span = 13.0mm -- verified this session (again, distinct
// from and unaffected by the MISS-009 fix below) to clear the motor
// platform's own footprint (max Y 68.0mm) by 26.0mm, and the motor body's
// own footprint (max Y 66.0mm) by 28.0mm: zero interference with the real,
// physical motor.

// Rev 3.1 FIX (MISS-009 continued): the duct VOID's own Y-span is now
// derived independently, from the flywheel bay wall's TRUE inner bore
// (fw_cy + fw_bay_inner_r = 92.0mm) -- NOT from bridge_y_lo (=94.0mm, the
// BRIDGE BLOCK's own recessed start point, already pulled 2.0mm inside the
// wall's OUTER face by bridge_fuse_overlap above). The pre-fix void used
// `bridge_y_lo - 1` (=93.0mm) as its near-end anchor, which is 1.0mm SHORT
// of the wall's true inner bore at Y=92.0mm. This second, independent
// defect (found by this Mechanical Lead while implementing the MISS-009
// fix, distinct from the Reviewer's own literal finding text) means that
// even after fixing the global-subtraction SCOPE bug below, that 1.0mm
// shortfall would still have left a thin, un-breached membrane of solid
// material sealing the duct's mouth exactly where it opens into the
// flywheel bay's own interior -- still defeating the wire route.
// duct_breach_margin below is the same KIND of guaranteed-clean-boolean
// margin as bridge_fuse_overlap above, just applied in the opposite
// direction: instead of guaranteeing genuine SOLID fusion across a joint,
// it guarantees a genuine VOID breach past each bounding wall face, not a
// knife-edge tangency CGAL could render ambiguously.
duct_breach_margin = 1.0; // mm. ASSUMPTION: same class/size of margin as
                  // bridge_fuse_overlap's underlying principle (this
                  // design's existing convention for a "safe/clean
                  // boolean" margin), applied here so the void genuinely
                  // breaches past each bounding wall face with margin to
                  // spare, rather than stopping exactly tangent to it.
wire_duct_y_lo = fw_cy + fw_bay_inner_r - duct_breach_margin; // = 91.0mm
                  // (pre-fix anchor was bridge_y_lo - 1 = 93.0mm -- 1.0mm
                  // SHORT of the wall's true inner bore at Y=92.0mm; see
                  // note above)
wire_duct_y_hi = bridge_y_hi + duct_breach_margin; // = 108.0mm (same
                  // numeric value as pre-fix -- this end was already
                  // safely past the PCB bay's own interior-facing wall
                  // surface at Y=107.0mm, so only the near end needed
                  // correcting)
// Resulting void length = 17.0mm (was, pre-fix, 15.0mm).

module motor_wire_bridge_solid() {
    // Rev 3 NEW, renamed + split Rev 3.1 (MISS-009): this is now a
    // SOLID-ONLY module (no local difference()/void here any more) -- split
    // out of the old combined motor_wire_bridge() so base() below can union
    // it with every other solid BEFORE the single, global void subtraction
    // happens. See motor_wire_duct_void() and base() below.
    //
    // A short rectangular gusset connecting the flywheel bay's PLAIN WALL
    // (outer radius fw_bay_outer_r -- NOT the wider flange band, which per
    // fw_bay_wall() above only exists near the very top, Z in
    // [fw_clearance_top-flange_band_h, fw_clearance_top], nowhere near this
    // duct's low Z) out to the PCB bay's own south wall.
    translate([fw_cx - wire_bridge_w/2, bridge_y_lo,
                wire_duct_z - wire_bridge_h/2])
        cube([wire_bridge_w, bridge_y_hi - bridge_y_lo, wire_bridge_h]);
}

module motor_wire_duct_void() {
    // Rev 3.1 FIX (MISS-009, HIGH): the actual wire-passage void, now a
    // standalone module subtracted GLOBALLY in base() below -- see base()'s
    // own top-level difference() -- instead of being subtracted only
    // inside the old combined motor_wire_bridge() module's own LOCAL
    // difference(), which left fw_bay_wall()'s annulus AND
    // pcb_bay_base()'s south wall fully solid at this exact location even
    // though the void geometrically overlapped both (independently
    // confirmed by the Mechanical Reviewer via a rendered base() +
    // point-containment sweep, Cycle 3 Finding 2, and independently
    // re-confirmed by this Mechanical Lead this session -- see the
    // companion spec file §7 for the empirical point-containment results).
    // Spans wire_duct_y_lo to wire_duct_y_hi (see derivation above), fully
    // breaching BOTH the flywheel bay wall's annulus (true inner bore at
    // Y=92.0mm, outer face at Y=96.0mm) and the PCB bay's south wall
    // (Y=105.0-107.0mm), not merely the bridge block sitting between them.
    translate([fw_cx, wire_duct_y_lo, wire_duct_z])
        rotate([-90, 0, 0])
            cylinder(d = wire_duct_dia, h = wire_duct_y_hi - wire_duct_y_lo);
}

module base() {
    // Rev 3.1 FIX (MISS-009, HIGH): base() is now a difference(), not a
    // flat union() as it was pre-fix -- the wire-passage void
    // (motor_wire_duct_void()) is subtracted ONCE, globally, from the union
    // of every solid that occupies its footprint (pcb_bay_base(),
    // motor_platform(), fw_bay_wall(), motor_wire_bridge_solid()), so the
    // duct is a real, continuous, open channel through the ENTIRE assembly
    // at this location, not just through the bridge block in isolation.
    difference() {
        union() {
            translate([0, pcb_bay_y0, 0]) pcb_bay_base();
            motor_platform();
            fw_bay_wall();
            motor_wire_bridge_solid();
        }
        motor_wire_duct_void();
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
// 3B. MODULES -- Rev 4 free-rotation support mechanism (new, additive
//     only). See Section 2B above for the full variable-level rationale.
// ----------------------------------------------------------------------

module bmount_flange() {
    // NEW, Rev 4. 4th-piece-adjacent mounting flange, fused BELOW
    // motor_platform()'s own floor disc (Section 3 above, UNCHANGED) so
    // the combined base+flange spans the bearing's own 101.6mm OD top
    // (ROTATING) plate. Extends ONLY into new (-Z) territory below the
    // pre-existing Z=0 floor, plus a small dip (bmount_fuse_overlap) UP
    // into the floor disc's own solid material for a genuine CSG union --
    // does not resize/move/remove motor_platform(), fw_bay_wall(), or any
    // other Rev 3 solid.
    //
    // MANUFACTURABILITY CAVEAT, caught and disclosed this session (NOT a
    // clean pass): this flange is hollow for its full height at
    // r < bmount_flange_ir, directly BENEATH motor_platform()'s own floor
    // disc, which is SOLID all the way to its own center (aside from its
    // small M1-mount/shaft cutouts, all well inside bmount_flange_ir).
    // Printed floor-down (the only viable orientation -- flipping would
    // break the existing standoffs, which need floor-down printing), this
    // creates a hidden internal transition -- solid disc material directly
    // above an open ~56mm-diameter bore (2*bmount_flange_ir) -- exceeding
    // this file's own max_overhang_deg (45 deg)/max_bridge_span (10.0mm)
    // rules by a wide margin. Resolution adopted: keep the flange fused as
    // ONE continuous print job with the base (preserves the "4 total
    // printed pieces" framing and the additive-only constraint), but
    // require slicer-generated INTERNAL SUPPORT MATERIAL for this one
    // hidden, non-mating, non-precision surface -- fully reachable/
    // removable through the bore's own straight-through opening (NOT a
    // blind cavity). 3 alternatives considered and rejected this session
    // (taper the bore -- doesn't help, the disc's own broad interior
    // remains unsupported regardless; flip print orientation -- breaks
    // the existing standoffs; fully separate bolt-on piece -- contradicts
    // the "4 total pieces" framing and would need an existing-module
    // edit to add mating features to motor_platform() itself). See
    // bench-imu-01-dimensional-spec.md Section 18.4/18.5 for the complete
    // write-up.
    difference() {
        // outer solid disc, Z=[-bmount_flange_t, +bmount_fuse_overlap]
        // (old Z=0 frame) -- reuses fw_flange_or as its own OD (Section 2B)
        translate([fw_cx, fw_cy, -bmount_flange_t])
            cylinder(r = bmount_flange_or, h = bmount_flange_t + bmount_fuse_overlap);
        // coaxial bore -- doubles as the REQ-113 tether pass-through
        // (confirmed non-interfering with the pilot holes below; see
        // hardware/mechanical-interface.md Part C6)
        translate([fw_cx, fw_cy, -bmount_flange_t - 1])
            cylinder(r = bmount_flange_ir, h = bmount_flange_t + bmount_fuse_overlap + 2);
        // 4x blind pilot holes for the bearing's own top-plate screws,
        // open at the flange's own BOTTOM face (where the screw enters,
        // from below), blind bmount_pilot_depth upward -- mirrors
        // standoff()'s own blind-pilot-hole pattern above (open face /
        // blind end, 1.0mm nominal margin at the blind end), just
        // inverted in Z since this part's own "outward" face is its
        // underside, not its top.
        for (i = [0 : n_bmount_bolts - 1]) {
            a = i * 360 / n_bmount_bolts;
            translate([fw_cx + bmount_bolt_circle_r*cos(a),
                        fw_cy + bmount_bolt_circle_r*sin(a),
                        -bmount_flange_t - 1])
                cylinder(d = bmount_pilot_dia, h = bmount_pilot_depth + 1);
        }
    }
}

module stand_plate() {
    // NEW, Rev 4 -- the 4th printed piece. A fixed, flat annulus that
    // bolts to the bearing's own bottom (STATIONARY) plate and is what
    // actually contacts the desk. Sized from a from-scratch CG/tip-over
    // analysis (Section 2B above; full write-up: hardware/mechanical-
    // interface.md Part C3/C4 and bench-imu-01-dimensional-spec.md
    // Section 18.3), NOT matched to DS-BRG-001's own generic "12-25in
    // suggested top diameter" (a heavy-furniture rule of thumb, a
    // different load class than this ~600g rig). Unlike bmount_flange(),
    // this is a UNIFORM-cross-section annulus for its entire thickness --
    // fuses/mates with nothing else -- so it has no analogous internal-
    // overhang manufacturability concern; prints flat, either face down,
    // no support material needed.
    difference() {
        // outer solid disc, Z=[stand_plate_bottom_z, stand_plate_top_z]
        translate([fw_cx, fw_cy, stand_plate_bottom_z])
            cylinder(r = stand_plate_or, h = stand_plate_t);
        // coaxial bore, continuous with bmount_flange_ir through the
        // bearing's own center hole (REQ-113, Part C6)
        translate([fw_cx, fw_cy, stand_plate_bottom_z - 1])
            cylinder(r = stand_plate_ir, h = stand_plate_t + 2);
        // 4x blind pilot holes for the bearing's own bottom-plate screws,
        // open at the plate's own TOP face (Z=stand_plate_top_z, where the
        // screw enters from above), blind downward -- mirrors standoff()'s
        // own blind-pilot-hole pattern exactly (open top / blind bottom,
        // 1.0mm nominal margin remaining at the blind end above the
        // plate's own true bottom face).
        for (i = [0 : n_bmount_bolts - 1]) {
            a = i * 360 / n_bmount_bolts;
            translate([fw_cx + stand_bolt_circle_r*cos(a),
                        fw_cy + stand_bolt_circle_r*sin(a),
                        stand_plate_top_z - bmount_pilot_depth])
                cylinder(d = bmount_pilot_dia, h = bmount_pilot_depth + 1);
        }
    }
}

// ----------------------------------------------------------------------
// 3C. MODULES -- Rev 4.1 mitigations for Independent Mechanical Review
//     Cycle 5's 2 blocking HIGH findings (MISS-023, MISS-024). See
//     Section 2C above for every dimension's rationale, and bench-imu-
//     01-dimensional-spec.md Sections 18.12/18.13 for the full write-up.
//     stand_plate() immediately above (Section 3B, Rev 4) is UNCHANGED.
// ----------------------------------------------------------------------

module pinch_guard(quadrant = -1) {
    // NEW, Rev 4.1 (MISS-023 fix); GROWN to full closure this session
    // (MISS-023's own final resolution, human Chief Engineer decision --
    // see pinch_guard_or's own comment above for the full citation). A
    // 5th printed piece: a STATIONARY annular guard, desk-resting,
    // flush-adjacent to (NOT fastened to, NOT overlapping)
    // stand_plate()'s own outer edge. Now covers the COMPLETE
    // [stand_plate_or, rotating_env_max_r] = [60.0, 176.259]mm annular
    // hazard band (pinch_guard_or=176.3mm exceeds rotating_env_max_r by
    // construction, per the human's own "full coverage" decision) -- 0mm
    // residual radial gap, 100% coverage, superseding the earlier
    // partial-closure (11.4mm gap @ 115.0mm, then a further-degraded
    // 61.3mm gap @ the same 115.0mm after the Rev 5 PCB resize) history
    // recorded in MISS-023's own resolved entry.
    //
    // quadrant = -1 (default) draws the FULL ring, used in the
    // "assembled" show_mode for visual/clearance sanity-checking.
    // quadrant = 0..3 draws only that 90-degree segment, used in
    // "print_layout". **CORRECTED, MISS-048** (independently found by a
    // cross-session review, immediately after this same session's own
    // full-closure resize): the ORIGINAL version of this comment (at
    // pinch_guard_or=115.0mm) claimed each printed piece's own bounding
    // box was "small enough to be printable on virtually any consumer
    // FDM printer" -- that claim does NOT survive the resize unedited.
    // Each quadrant's own real bounding box is now
    // pinch_guard_or x pinch_guard_or = 176.3 x 176.3mm (was
    // 115.0 x 115.0mm) -- confirmed via direct STL export + `trimesh`,
    // not asserted. This still fits many common consumer FDM print beds
    // (a frequent class is ~220-250mm square) but does NOT fit some
    // smaller/older/compact models (a frequent class is ~180mm square) --
    // "virtually any" was true at 115mm and is simply no longer an
    // honest claim at 176.3mm. This Mechanical Lead deliberately still
    // avoids INVENTING a specific minimum-bed-size requirement (none is
    // documented anywhere in this repository, and inventing one now would
    // be exactly the kind of unsourced constraint this file's own
    // established convention avoids) -- kept at 4 quadrants this pass, a
    // deliberate choice disclosed as such (re-splitting into more/smaller
    // segments, e.g. 6 or 8, was considered and would restore a
    // universally-small per-piece footprint at zero coverage/mass cost,
    // but was NOT done this pass, trading a real fit-on-my-printer
    // question for a real seam-count-on-a-safety-guard question -- see
    // MISS-048, `validation/open-issues.md`, for the full disclosure and
    // the 3 options considered). A builder with a smaller print bed
    // should check their own printer's own build volume against this
    // real 176.3mm figure before printing, rather than trust the
    // superseded "virtually any" framing. The 2 straight
    // radial cut edges are exact (bounded by
    // planes through the origin at the wedge's own a0/a1 angles). The
    // 3rd (chord/far) edge of the cutting polygon is NOT itself a source
    // of faceting/approximation error beyond the ring's own pre-existing
    // cylinder facet count (unchanged from stand_plate()'s own $fn
    // convention) -- but an EARLIER version of this comment additionally,
    // and WRONGLY, implied that edge was "exact" for the ring's own
    // outer radius at every angle; it is not, unless `r_cut` is sized
    // correctly (see the SELF-CAUGHT FIX comment below, at this
    // module's own quadrant-cut branch, for the real, once-shipped bug
    // this corrects).
    module full_ring() {
        translate([fw_cx, fw_cy, stand_plate_bottom_z])
            difference() {
                cylinder(r = pinch_guard_or, h = pinch_guard_h);
                translate([0, 0, -1])
                    cylinder(r = pinch_guard_ir, h = pinch_guard_h + 2);
            }
    }
    if (quadrant < 0) {
        full_ring();
    } else {
        a0 = quadrant * 90;
        a1 = a0 + 90;
        // SELF-CAUGHT FIX (new, this session -- pre-existing since Rev 4.1,
        // independent of and unrelated to the Rev 5/MISS-034 PCB resize;
        // found while independently re-rendering/re-measuring pinch_guard()
        // for MISS-034's own rotating-envelope re-verification, per this
        // project's Foresight-checklist habit of noticing a second effect
        // while checking a first one, not because this pass's task asked
        // for it -- mirrors the MISS-007/MISS-008/MISS-009/MISS-010
        // precedent).
        //
        // BUG: the old `r_cut = pinch_guard_or + pinch_guard_quadrant_margin`
        // (=125.0mm) sized the two OUTER CORNER vertices of the cutting
        // triangle correctly, but the STRAIGHT CHORD connecting those two
        // corners is not equidistant from the origin at every angle in
        // between -- at the wedge's own angular midpoint (45 deg into a
        // 90 deg quadrant) the chord sits only `r_cut*cos(45)`=88.39mm from
        // the origin, 26.61mm INSIDE `pinch_guard_or`=115.0mm. The claimed
        // "2 straight radial cut edges are exact... no faceting/
        // approximation error" was true only for those 2 radial edges
        // themselves (which are exact) -- it did not hold for the 3rd
        // (chord/hypotenuse) edge, which silently bit a real, confirmed
        // chunk out of each quadrant's own outer ring material, all along
        // the outer band nearest each quadrant's own 45-degree midpoint.
        // Independently re-measured this session (3 methods: OpenSCAD's
        // own manifold/CGAL volume-adjacent stats, `trimesh`, and a
        // from-scratch divergence-theorem triangle-sum in `numpy-stl`, all
        // agreeing to <0.001mm3): the pre-fix quadrant STL's real volume
        // was 72,803.19mm3 against an ideal quarter-annulus of
        // 112,635.9mm3 -- a genuine ~35.4% material shortfall per printed
        // quadrant (was NOT reflected in this design's own previously
        // recorded ~570.6g full-ring mass figure, which was computed by
        // rendering the FULL ring (`quadrant=-1`) directly and is
        // therefore itself correct -- the bug was specific to the
        // quadrant-SPLIT print pieces actually shipped/measured for
        // print_layout, not to the full-ring reference figure).
        // FIX: derive `r_cut` from the wedge's own half-angle so the
        // chord's closest approach to the origin (`r_cut*cos(half_angle)`)
        // clears `pinch_guard_or` with `pinch_guard_quadrant_margin` to
        // spare, instead of assuming (incorrectly) that sizing only the 2
        // corner vertices to `r_cut` was sufficient.
        half_angle = (a1 - a0) / 2;
        r_cut = pinch_guard_or / cos(half_angle) + pinch_guard_quadrant_margin;
        intersection() {
            full_ring();
            translate([fw_cx, fw_cy, stand_plate_bottom_z - 1])
                linear_extrude(height = pinch_guard_h + 2)
                    polygon(points = [
                        [0, 0],
                        [r_cut*cos(a0), r_cut*sin(a0)],
                        [r_cut*cos(a1), r_cut*sin(a1)],
                    ]);
        }
    }
}

module rotation_index_pointer() {
    // NEW, Rev 4.1 (MISS-024 mitigation). A small radial pointer tab,
    // fused to the ROTATING base's own north (PCB-bay-side, far/+Y) wall
    // exterior, centered on that wall's own centerline (X = fw_cx, which
    // is EXACTLY base_outer_x/2 -- a confirmed design coincidence, not an
    // assumption) -- 38.5mm clear of the nearest base_tab() corner tab in
    // either direction (2 of the 4 corner tabs share this same wall).
    // Purpose: a simple, low-tech visual turn-counting aid -- the
    // operator sights this pointer against any convenient FIXED external
    // landmark (e.g. a mark on the desk, the cable's own resting
    // position) once per full turn while manually tracking count toward
    // pinch_guard_turn_limit, before the mandatory manual re-centering
    // (spec 18.13). Deliberately NOT paired with a fixed witness mark on
    // pinch_guard() itself -- that would require the guard ring to be
    // rotationally keyed/fixed in place, a separate, undelivered feature
    // (see spec 18.13 UNKNOWNs). Attached to the rotating base -- part of
    // the SAME print job as base()/bmount_flange(), not a separate piece.
    // Z-centered at the wall's own mid-height (base_total_h/2), comfortably
    // clear of pcb_lid() (whose own lowest point is 18.1mm, vs. this
    // pointer's own top at ~13.55mm) and of the corner tabs (whose own Z
    // range, [15.5, base_total_h], does not overlap this pointer's).
    translate([fw_cx, pcb_bay_y0 + base_outer_y,
                base_total_h/2 - rot_pointer_h/2])
        linear_extrude(height = rot_pointer_h)
            polygon(points = [
                [-rot_pointer_w/2, 0],
                [ rot_pointer_w/2, 0],
                [ 0,               rot_pointer_project],
            ]);
}

module cable_anchor_tab(is_j4 = false) {
    // NEW, Rev 4.1 (MISS-024 partial mitigation). A simple, additive
    // strain-relief anchor point near J1 (is_j4 = false) or J4
    // (is_j4 = true), so a zip-tie can anchor the cable's own external
    // service loop close to the connector instead of relying on the
    // connector's own solder joints/housing to react any pull force --
    // directly targets the "yanks the connector" failure mode named in
    // the Cycle 5 review. A simple conceptual feature (a small tab with a
    // vertical through-hole), not a precision part. Positioned at
    // bay-local Y = cable_anchor_yc (4.75mm clear of the existing J1/J4
    // cutouts' own Y-span, 11.0mm clear of the bay's own front edge) and
    // Z = cable_anchor_zc (well below pcb_lid()'s own lowest point, so no
    // lid collision regardless of X projection distance) -- see Section
    // 2C for the full clearance derivation. Attached to the rotating
    // base -- part of the SAME print job as base()/bmount_flange(), not a
    // separate piece.
    x0 = is_j4 ? base_outer_x : (-cable_anchor_project);
    translate([x0,
                pcb_bay_y0 + cable_anchor_yc - cable_anchor_w/2,
                cable_anchor_zc - cable_anchor_h/2])
        difference() {
            cube([cable_anchor_project, cable_anchor_w, cable_anchor_h]);
            translate([cable_anchor_project/2, cable_anchor_w/2, -1])
                cylinder(d = cable_anchor_hole_dia, h = cable_anchor_h + 2);
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

module reference_bearing() {
    // NEW, Rev 4. Simplified single-cylinder stand-in for the bought BC
    // Precision 4LS-3 bearing itself (NOT printed/modeled in detail --
    // the real part is two stamped plates + a captive ball race) --
    // mirrors reference_motor_flywheel()'s own simplification convention
    // above. Visual sanity-check only (%-marked, excluded from STL export
    // like every other module in this Section 4).
    color("silver")
    translate([fw_cx, fw_cy, brg_bottom_z])
        cylinder(d = brg_od, h = brg_t);
}

// ----------------------------------------------------------------------
// 5. TOP-LEVEL ASSEMBLY / LAYOUT (Rev 3: 3 pieces; Rev 4 adds a 4th, the
//    free-rotation stand plate, below -- base()'s own module body is
//    UNCHANGED, only this section's calls are extended)
// ----------------------------------------------------------------------
if (show_mode == "assembled") {
    base();
    translate([0, pcb_bay_y0, base_total_h - lid_lip_h]) pcb_lid();
    containment_cap();
    % reference_pcba();
    % reference_motor_flywheel();
    // --- Rev 4 additions below (pure addition -- nothing above this line
    //     in this branch was changed). All three new calls are bare/
    //     untranslated because bmount_flange(), stand_plate(), and
    //     reference_bearing() each already bake in their own correct
    //     global (fw_cx, fw_cy, Z) position internally, same convention
    //     as base()/containment_cap() above. ---
    bmount_flange();
    stand_plate();
    % reference_bearing();
    // --- Rev 4.1 additions below (Cycle 5 MISS-023/MISS-024 HIGH-finding
    //     fixes -- pure addition, nothing above this line in this branch
    //     was changed). All four new calls are bare/untranslated for the
    //     same reason as the Rev 4 calls immediately above: each module
    //     already bakes in its own correct global position internally. ---
    pinch_guard();               // MISS-023: stationary guard ring (5th
                                  // printed piece, full ring in this view)
    rotation_index_pointer();     // MISS-024: turn-counting visual aid
    cable_anchor_tab(false);      // MISS-024: J1-side strain-relief anchor
    cable_anchor_tab(true);       // MISS-024: J4-side strain-relief anchor
} else if (show_mode == "print_layout") {
    // Base + Rev 4 mounting flange: NEW, Rev 4 -- these two solids now
    // print as ONE combined job. This is the ONE pre-existing line in
    // this whole file touched by the Rev 4 work (disclosed explicitly in
    // the Rev 4 self-check/handoff report) -- base()'s own MODULE BODY
    // above (Section 3) is completely UNCHANGED byte-for-byte; only this
    // print_layout DISPLAY position is adjusted, by the flange's own
    // thickness, so the combined piece's true lowest point (the flange's
    // own bottom face, the new build-plate-adjacent face) sits at this
    // view's Z=0 reference, instead of base()'s old standalone-piece
    // floor. No manufactured dimension changes; this is a display-only Z
    // shift for a layout view this file's own header already caveats as
    // "starting point only... not rendered/verified precisely" (§0/top of
    // file). Requires slicer-generated INTERNAL SUPPORT MATERIAL for the
    // hidden internal overhang at the base/flange transition -- see
    // bmount_flange()'s own header comment above for the full finding.
    translate([0, 0, bmount_flange_t]) {
        base();
        bmount_flange();
        // Rev 4.1 NEW: additive sibling calls only (the 2 pre-existing
        // calls above and this translate's own [0,0,bmount_flange_t]
        // argument are UNCHANGED) -- rotation_index_pointer() and both
        // cable_anchor_tab() calls are small features fused to base()'s
        // own wall, part of this SAME combined print job, not new pieces.
        rotation_index_pointer();
        cable_anchor_tab(false);
        cable_anchor_tab(true);
    }

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

    // Rev 4 NEW: stand plate (4th printed piece). Uniform annulus, no flip
    // needed (see stand_plate()'s own header comment -- no internal-
    // overhang concern, unlike the base+flange combo above). Laid out at
    // a fresh, disjoint spot (negative-Y quadrant, clear of all 3 other
    // pieces' own Y-footprints above -- starting point only, same §0
    // caveat as the rest of this print_layout branch).
    translate([0, -(fw_cy + stand_plate_or + 20), -stand_plate_bottom_z])
        stand_plate();

    // Rev 4.1 NEW: pinch guard (5th printed piece -- MISS-023 fix), laid
    // out as its 4 individual 90-degree quadrants (see pinch_guard()'s own
    // header comment for why -- no printer-bed-size assumption is known
    // for this project or invented here). Each quadrant's own internal
    // fw_cx/fw_cy/stand_plate_bottom_z bake-in is cancelled first (inner
    // translate, so the piece sits flat at this view's own Z=0), then the
    // whole [0, 2*pinch_guard_or] square bounding box (a conservative,
    // same-for-all-4-quadrants box, big enough to contain whichever
    // corner that particular quadrant occupies -- see the module's own
    // per-quadrant footprint note) is placed in a fresh row at X=280
    // onward, clear of every other piece above (the widest of which, the
    // flipped PCB lid, reaches X=233.4) -- starting point only, same §0
    // caveat as the rest of this print_layout branch.
    for (i = [0 : 3])
        translate([280 + i * (2*pinch_guard_or + 15), pinch_guard_or, 0])
            translate([-fw_cx, -fw_cy, -stand_plate_bottom_z])
                pinch_guard(i);
}

// ============================================================================
// END OF FILE -- bench-imu-01-enclosure.scad (Rev 3)
// Companion file: bench-imu-01-dimensional-spec.md (full rationale, self-
// check against the Mechanical Reviewer's 10-item checklist, open
// UNKNOWNs/ASSUMPTIONs carried forward, REQ-403 safety-disposition
// proposal).
// ============================================================================

// ============================================================================
// REV 4 ADDENDUM TO END-OF-FILE BANNER (new, additive only -- the Rev 3
// banner immediately above is unchanged).
//
// This file now also contains the Rev 4 free-rotation support mechanism
// (Section 2B variables, Section 3B modules bmount_flange()/stand_plate(),
// Section 4's reference_bearing(), and the corresponding Section 5
// show_mode additions) -- grown from 1208 to 1526 lines. Everything from
// Rev 3 (Sections 1-2, 3, 4's original two reference modules, and every
// pre-existing line inside Section 5) is UNCHANGED, EXCEPT for the one
// disclosed print_layout DISPLAY-only Z-shift on the base() call (see that
// line's own comment in Section 5 above for the full justification) -- no
// manufactured Rev 3 dimension, wall, bay, or module body was resized,
// moved, or removed.
//
// Companion files for the Rev 4 addition specifically:
//   - hardware/mechanical-interface.md, Part C (bearing physical facts,
//     CG/tip-over analysis, fastener justification, tether-routing
//     confirmation, assembly-order addendum).
//   - bench-imu-01-dimensional-spec.md, Section 18 (dimensional tables,
//     full CG/tip-over write-up, manufacturability check including the
//     disclosed internal-overhang finding, self-check against the
//     Mechanical Reviewer's 10-item checklist).
//
// Tooling honesty (re-verified this session, not assumed carried over):
// no CAD/3D modeling MCP tool is connected in this environment (a live
// connection check against blender-get_addon_status returned "Could not
// connect to Blender"). The local `openscad` CLI (v2026.08.30) IS present
// and was used to spot-check this file's render validity (NoError,
// manifold) -- see bench-imu-01-dimensional-spec.md Section 18.5 for the
// specific checks run against the Rev 4 geometry. No STL export, fit
// check, or physical print has been produced or claimed.
//
// This Rev 4 addition has NOT been independently reviewed. Per this
// project's own process (Mechanical Lead agent file, Mechanical Reviewer
// agent file), a separate Mechanical Reviewer pass is required next and
// has not yet occurred -- do not treat this file as reviewed/approved.
// ============================================================================

// ============================================================================
// REV 4.1 ADDENDUM TO END-OF-FILE BANNER (new, additive only -- the Rev 3
// banner and the Rev 4 addendum immediately above are both unchanged).
//
// STALENESS NOTE on the Rev 4 addendum immediately above: its final
// sentence ("This Rev 4 addition has NOT been independently reviewed...")
// is now STALE. That review DID occur -- Independent Mechanical Review
// Cycle 5 (validation/design-review.md, "Mechanical Reviewer -- Cycle 5")
// -- and returned verdict CONDITIONAL, with 2 blocking HIGH findings
// (MISS-023, MISS-024; plus 1 MEDIUM and 3 LOW, non-blocking, NOT
// addressed by this pass -- see validation/open-issues.md). This Rev 4.1
// addendum is this Mechanical Lead's fix pass for the 2 blocking HIGH
// findings only. Per this same additive-only discipline, the stale
// sentence above is NOT edited in place -- this note supersedes it.
// A FRESH independent review of THIS Rev 4.1 geometry is required next,
// exactly as that stale sentence still correctly implies for whatever is
// newest in the file -- do not treat Rev 4.1 as reviewed/approved either.
//
// This file now also contains the Rev 4.1 mitigations for Cycle 5's 2
// HIGH findings (Section 2C variables; Section 3C modules pinch_guard(),
// rotation_index_pointer(), cable_anchor_tab(); the corresponding Section
// 5 show_mode additions) -- grown from 1526 to 1916 lines. Everything
// from Rev 3 and Rev 4 (Sections 1-2, 2B, 3, 3B, 4's three reference/
// mitigation modules from before this pass, and every pre-existing line
// inside Section 5) is UNCHANGED, EXCEPT for 2 additional disclosed
// print_layout DISPLAY-only additions (both purely ADDITIVE, no existing
// line edited): (1) 3 new sibling calls (rotation_index_pointer(),
// cable_anchor_tab(false), cable_anchor_tab(true)) added inside the SAME
// pre-existing translate([0,0,bmount_flange_t]) {base(); bmount_flange();}
// block that Rev 4 had already (and disclosed) touched once for its own
// Z-shift -- this pass adds no further change to that block's own 2
// pre-existing calls or its translate argument, only new sibling lines
// alongside them; and (2) a brand new translate/for-loop block laying out
// pinch_guard()'s 4 print quadrants, appended after stand_plate()'s own
// pre-existing layout call. No manufactured Rev 3 or Rev 4 dimension,
// wall, bay, or module body was resized, moved, or removed by this pass.
// The ONE Rev-4-OWNED value this pass DID resize is disclosed explicitly:
// none. (pinch_guard_ir reuses stand_plate_or by reference, not by
// editing stand_plate_or's own value -- stand_plate_or itself is
// untouched.)
//
// Piece count: Rev 4 was 4 total printed pieces. This pass adds a 5th
// (pinch_guard(), itself split into 4 print-layout quadrants for bed-
// size-agnostic printability -- see that module's own header comment).
// rotation_index_pointer() and cable_anchor_tab() are NOT additional
// pieces -- both are small features fused to the existing base()+
// bmount_flange() combined print job (piece 1).
//
// Companion files for the Rev 4.1 addition specifically:
//   - bench-imu-01-dimensional-spec.md, Section 18.12 (MISS-023 pinch-
//     point assessment + pinch_guard() fix, full coverage/trade-off
//     table, honest partial-closure disclosure) and 18.13 (MISS-024
//     cable-entanglement assessment + turn-count/service-loop/index-
//     pointer/anchor-tab fix, honest disclosure that REQ-012's aspirational
//     "unlimited" rotation is not achieved).
//   - hardware/mechanical-interface.md, Part C (new facts, if any, from
//     this pass -- see that file's own Rev 4.1 entries).
//
// Tooling honesty (re-verified this session, not assumed carried over):
// no CAD/3D modeling MCP tool is connected in this environment (a live
// connection check against blender-get_addon_status returned "Could not
// connect to Blender" -- re-checked fresh this session, not copied
// forward). The local `openscad` CLI (v2026.08.30) IS present and was
// used to render/verify this pass's new geometry -- see bench-imu-01-
// dimensional-spec.md Section 18.12/18.13 for the specific checks run.
// No STL export, fit check, or physical print has been produced or
// claimed for the Rev 4.1 geometry either.
//
// HONEST SELF-ASSESSMENT (stated here, not just in the handoff report, so
// it travels with the file): MISS-023 is only PARTIALLY closed by
// pinch_guard() alone -- it covers ~77.7% of the exposed hazard-band area
// with an 11.4mm residual radial gap at the outer edge, backstopped by a
// documented keep-clear-zone warning (spec 18.12), not a hermetic
// mechanical seal. MISS-024 is bounded/proceduralized (a turn-count limit
// + service-loop spec + index pointer + anchor tabs), not a full
// realization of REQ-012's own aspirational "ideally continuous/
// unlimited" rotation case. Neither finding should be closed as a "full,
// no-caveats fix" -- see the handoff report to the Hardware Lead for the
// complete, itemized assessment.
//
// This Rev 4.1 addition has NOT been independently reviewed. A fresh
// Mechanical Reviewer pass against this geometry is required next and has
// not yet occurred -- do not treat this file as reviewed/approved.
// ============================================================================
