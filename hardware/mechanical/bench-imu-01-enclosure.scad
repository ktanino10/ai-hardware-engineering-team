// ============================================================================
// Bench-IMU-01 -- Enclosure (Mechanical Lead, Phase 1)
// ============================================================================
// TOOLING HONESTY (per docs/architecture.md §5.3/§13 and this session's own
// re-verification): no CAD/3D modeling MCP tool is connected in this
// environment (blender-get_addon_status -> "Could not connect to Blender");
// no local `openscad`/`freecad` binary or `cadquery`/`solid`/`build123d`
// Python library is installed either. This file has NOT been rendered,
// previewed, exported to STL, or fit-checked by this agent. It is a
// text/parametric OpenSCAD-SYNTAX SOURCE FILE ONLY. A human must open or
// render it themselves, e.g.:
//     openscad -o bench-imu-01-enclosure.stl bench-imu-01-enclosure.scad
// or paste this file into an online OpenSCAD viewer, to see or validate the
// actual 3D geometry. All internal consistency below was checked with plain
// arithmetic (see bench-imu-01-dimensional-spec.md, "Computed clearance
// checks"), not by rendering.
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
// hardware/mechanical-interface.md exactly): origin (0,0) at the PCB
// bottom-left corner, viewed from the top/component side. X: 0->60mm
// (PCB length). Y: 0->40mm (PCB width).
// This file's GLOBAL frame (used for all actual solid-modeling coordinates)
// has its own separate origin: (0,0,0) = the enclosure's external
// bottom-left-floor corner. board_offset_x/y (below) is the fixed
// translation from board-local XY to global XY. Global Z=0 is the base's
// external bottom face; +Z points toward the lid.
// ============================================================================

/* [Rendering / layout] */
// "assembled"    : base + lid shown in their final, closed, assembled
//                  positions (visual reference only -- see the PCB/component
//                  reference geometry below, shown with `%` so it is
//                  excluded from any STL export).
// "print_layout" : base (floor-down, its natural print orientation) and lid
//                  (flipped roof-down, its natural print orientation) laid
//                  out side by side. The lid's flip transform is a starting
//                  point only -- verify visually in your slicer / OpenSCAD's
//                  own view before trusting it; not rendered by this agent.
show_mode = "assembled"; // ["assembled", "print_layout"]

$fn = 48; // facet count for circles/cylinders -- cosmetic smoothness only,
          // does not change any stated dimension.

// ----------------------------------------------------------------------
// 1. VALUES TAKEN DIRECTLY FROM hardware/mechanical-interface.md
//    (confidence labels mirror that file's own Confidence column)
// ----------------------------------------------------------------------

// --- Board Geometry (interface: "Board Geometry") ---
pcb_length    = 60.0; // mm, X extent. ESTIMATE.
pcb_width     = 40.0; // mm, Y extent. ESTIMATE.
pcb_thickness = 1.6;  // mm, Z extent. ASSUMPTION (standard 2-layer stock).

// --- Mounting holes (interface: "Mounting"), [x, y, clearance_dia] ---
// MH-1..MH-4, all ESTIMATE, all sized for M2.5 (2.8mm clearance dia).
mount_holes = [
    [ 3.5,  3.5, 2.8], // MH-1
    [56.5,  3.5, 2.8], // MH-2
    [56.5, 36.5, 2.8], // MH-3
    [ 3.5, 36.5, 2.8], // MH-4
];

// --- Component height clearance (interface: "Component Height Clearance")
// TOP = 8.5mm, driven by the J2/J3 header stack height. This EXPLICITLY
// SUPERSEDES design.md's original 3.2mm (USB-C-driven) figure per the
// interface file's own corrected finding -- do not revert this to 3.2mm.
top_component_clearance    = 8.5; // mm. ESTIMATE (corrected figure).
bottom_component_clearance = 0.0; // mm. ASSUMPTION (single-sided assembly).

// --- Connectors / switches / LEDs (interface: "Connectors/Switches/LEDs"),
//     board-local X, Y (mm) ---
// J1: USB-C receptacle, power only. Horizontal, plug axis along X,
//     opens -X (through the board's left short edge). Representative
//     component height ~3.2mm (design.md / DS-CONN-003-class part; J1's
//     own MPN is not yet locked -- interface file Open Item).
j1_x = 0.0;  j1_y = 20.0;  j1_ref_height = 3.2;
// J2: 4-pin UART header. Vertical through-hole, pins/body face +Z.
j2_x = 16.0; j2_y = 40.0;
// J3: 4-pin SWD header. Vertical through-hole, pins/body face +Z.
j3_x = 30.0; j3_y = 40.0;
// SW1: momentary reset button. Vertical actuation, cap faces +Z.
sw1_x = 44.0; sw1_y = 40.0;
// D1: status LED, top-emitting, +Z.
d1_x = 10.0; d1_y = 30.0;

// ----------------------------------------------------------------------
// 2. THIS MECHANICAL LEAD'S OWN DESIGN VALUES (this session).
//    Everything below is ASSUMPTION/ESTIMATE unless marked DERIVED
//    (computed from other named values here, not a fresh guess).
//    Full rationale for each: bench-imu-01-dimensional-spec.md.
// ----------------------------------------------------------------------

// --- Print-fit tolerance: THE single stated clearance allowance, applied
//     at every place two parts actually mate: lid-skirt-to-base-wall
//     radial gap, and all fastener clearance-hole sizing. ---
fit_clearance = 0.2; // mm, PER SIDE. ASSUMPTION.

// --- Manufacturability rule set (ASSUMPTION, stated explicitly since the
//     human specified no printer/material) ---
print_material    = "PETG"; // ASSUMPTION. Chosen over PLA for better layer
                             // adhesion/toughness at small self-tapping
                             // screw bosses; chosen over ABS to avoid an
                             // enclosed-chamber / warping requirement.
min_wall_t        = 2.0;  // mm. ASSUMPTION: nominal thickness used for
                           // every structural wall in this design -- well
                           // above the commonly-cited ~0.8mm FDM structural
                           // floor (2 perimeters @ 0.4mm nozzle); chosen for
                           // real screw-boss/wall integrity, not a bare
                           // minimum shell.
max_overhang_deg  = 45;   // degrees from vertical, unsupported. ASSUMPTION:
                           // standard FDM rule of thumb.
max_bridge_span   = 10.0; // mm, unsupported. ASSUMPTION: common FDM
                           // practice with adequate part cooling.

wall_t  = min_wall_t; // mm. Base perimeter walls, lid roof, lid skirt.
floor_t = min_wall_t; // mm. Base floor slab. Same rationale as wall_t.

// --- PCB-to-interior-cavity keepout. NOT the same thing as fit_clearance:
//     the PCB's XY position is fixed by its 4 standoffs, not by contact
//     with this wall, so this is a generous drop-in/assembly and
//     robustness margin, not a tight mating tolerance. ---
board_xy_keepout = 1.5; // mm, per side. ASSUMPTION.

// --- PCB standoffs (support + fastening, at the 4 mount_holes positions) ---
standoff_od         = 6.0; // mm. ASSUMPTION: sized so the annular wall
                            // around the pilot hole equals wall_t (2.0mm):
                            // (6.0 - 2.0)/2 = 2.0mm -- consistent strength
                            // reasoning with the rest of the enclosure.
standoff_pilot_dia  = 2.0; // mm. ASSUMPTION: ~80% of M2.5's 2.5mm major
                            // diameter, standard self-tapping-into-
                            // thermoplastic pilot sizing guidance.
standoff_h          = 6.0; // mm. ASSUMPTION -- sized by the M2.5
                            // self-tapping thread ENGAGEMENT-DEPTH need
                            // (dominant constraint; common guidance is
                            // ~2-3x screw diameter, i.e. ~5-7.5mm), NOT by
                            // the bottom-clearance requirement (0mm, which
                            // is trivially satisfied many times over as a
                            // side effect). See dimensional-spec.md.
standoff_pilot_depth = 5.0; // mm, blind. ASSUMPTION: leaves 1.0mm of solid
                            // print material below the hole (no through-
                            // hole marking the external bottom face).

// --- Single fastener type/length used EVERYWHERE in this design (BOM
//     simplicity, verified by stack-up arithmetic in the spec file) ---
screw_len = 6.0; // mm (M2.5 self-tapping/thread-forming). ASSUMPTION.
                 // PCB standoffs: passes through pcb_thickness (1.6mm) and
                 // engages ~4.4mm of the 5.0mm pilot depth.
                 // Lid tabs: passes through the lid tab's clearance
                 // thickness (2.0mm) and engages 4.0mm of the base tab's
                 // 4.0mm pilot depth (see tab_pilot_depth below).

// --- Vertical (Z) stack -- DERIVED unless noted ---
z_margin = 0.5; // mm. ASSUMPTION: extra robustness margin ABOVE the
                 // interface file's stated 8.5mm top clearance, absorbing
                 // standoff/PCB/print vertical tolerance stack-up. Distinct
                 // from fit_clearance (that governs sliding/mating
                 // surfaces; this governs a functional keep-clear zone).

base_interior_h = standoff_h + pcb_thickness + top_component_clearance
                  + z_margin;                    // DERIVED = 16.6mm
base_total_h    = floor_t + base_interior_h;      // DERIVED = 18.6mm

lid_lip_h   = 3.0;    // mm. ASSUMPTION: skirt overlap depth over the base
                       // wall's top -- provides alignment + a friction/
                       // slip fit (positive retention is via the corner-
                       // tab screws, not this fit -- see spec file).
lid_roof_t  = wall_t; // mm. ASSUMPTION: = wall_t for consistency.
lid_skirt_t = wall_t; // mm. ASSUMPTION: = wall_t for consistency.

total_height = base_total_h + lid_roof_t;         // DERIVED = 20.6mm

// --- XY footprint -- DERIVED unless noted ---
interior_x = pcb_length + 2*board_xy_keepout;     // DERIVED = 63.0mm
interior_y = pcb_width  + 2*board_xy_keepout;     // DERIVED = 43.0mm
base_outer_x = interior_x + 2*wall_t;             // DERIVED = 67.0mm
base_outer_y = interior_y + 2*wall_t;             // DERIVED = 47.0mm

lid_skirt_inner_x = base_outer_x + 2*fit_clearance;   // DERIVED = 67.4mm
lid_skirt_inner_y = base_outer_y + 2*fit_clearance;   // DERIVED = 47.4mm
lid_skirt_outer_x = lid_skirt_inner_x + 2*lid_skirt_t; // DERIVED = 71.4mm
lid_skirt_outer_y = lid_skirt_inner_y + 2*lid_skirt_t; // DERIVED = 51.4mm
// NOTE: the lid's main skirt footprint is therefore 2.2mm/side larger than
// the base's outer footprint (an intentional, documented "cap overhangs
// base slightly" cosmetic trade-off -- see spec file). The 4 external
// corner tabs (below) are positioned relative to base_outer_x/y directly,
// NOT relative to this larger lid skirt footprint, so lid and base tabs
// align regardless of the skirt overhang.
lid_x0 = (base_outer_x - lid_skirt_outer_x) / 2; // DERIVED = -2.2mm
lid_y0 = (base_outer_y - lid_skirt_outer_y) / 2; // DERIVED = -2.2mm

// translation from board-local (0,0) to global XY (base floor's
// bottom-left corner = global (0,0))
board_offset_x = wall_t + board_xy_keepout; // DERIVED = 3.5mm
board_offset_y = wall_t + board_xy_keepout; // DERIVED = 3.5mm

// --- J1 (USB-C) cutout, in the base's X=0 (left) wall ---
// Purpose: FUNCTIONAL ACCESS -- the mating USB-C cable plug must be able
// to insert from outside the enclosure (-X direction), not just clear J1's
// own physical bulk.
j1_cut_w = 9.5; // mm (Y-span). ESTIMATE: representative USB-C receptacle
                 // shell width (~9.0mm) + 2x fit_clearance, rounded up
                 // slightly given J1's MPN is not yet locked (interface
                 // file Open Item).
j1_cut_h = 6.0; // mm (Z-span). ESTIMATE: deliberately generous --
                 // pcb_thickness (1.6) + j1_ref_height (3.2) + margin --
                 // so the cutout clears the connector regardless of
                 // exactly how its shell sits relative to the PCB surface.
j1_cut_z = standoff_h; // mm, bottom edge of cutout, referenced to the
                        // interior floor face, aligned to the PCB's BOTTOM
                        // surface (extra margin vs. aligning to PCB top).

// --- Header/button bay: ONE continuous open notch in the LID (roof AND
//     skirt), open to the board's Y=40 (rear) outer edge, spanning J2+J3+
//     SW1. Purpose: FUNCTIONAL ACCESS. A height-stack check (see spec
//     file) shows the header top (Z=18.1mm) actually sits BELOW the split
//     line (Z=18.6mm) with the stated z_margin -- so a solid lid would NOT
//     collide with the headers. The bay exists because J2/UART and
//     J3/SWD are ACTIVE-USE connectors needing an ongoing cable mating
//     path from outside the case, and SW1 needs a path for a fingertip to
//     press it -- not because of a Z-height collision. This is a
//     deliberately single, wide notch (vs. 3 separate small cutouts) for
//     print simplicity (avoids a thin bridged strip at the back edge) and
//     because it matches real cable-dressing needs (a debug cable can
//     exit up or backward through the open notch). ---
bay_x_min = 10.0; // mm, board-local X. ESTIMATE: J2 (x=16) margin - 6mm.
bay_x_max = 50.0; // mm, board-local X. ESTIMATE: SW1 (x=44) margin + 6mm.
bay_y_min = 34.0; // mm, board-local Y. ESTIMATE: 6mm header/switch
                   // footprint-depth allowance in from the board's Y=40
                   // edge (the bay's other, open, edge is that same
                   // board/enclosure edge itself).

// --- D1 LED viewing hole, through the lid roof only. Purpose: FUNCTIONAL
//     ACCESS (visibility) -- a solid lid would hide the LED entirely. ---
d1_hole_dia = 3.0; // mm. ESTIMATE: small viewing hole, no light-pipe
                    // (Phase-1-appropriate; interface file's own note).

// --- External corner mounting tabs (lid-to-base fastening). These are
//     EXTERNAL (project outward beyond the main wall profile), not
//     interior bosses -- see spec file for why interior options (shared
//     PCB+lid fastening column; inward-bulging boss on the clear wall;
//     4th interior corner boss) were all rejected as unbuildable or
//     PCB-colliding. ---
tab_w             = 8.0; // mm, along the wall. ASSUMPTION.
tab_project       = 6.0; // mm, beyond the main wall's outer face. ASSUMPTION.
tab_base_t        = 5.0; // mm, base-side tab thickness. ASSUMPTION -- sized
                          // to give a 4.0mm pilot depth (below) with a
                          // 1.0mm solid floor remaining.
tab_pilot_depth   = 4.0; // mm, blind. ASSUMPTION (see screw_len note above
                          // for the full engagement arithmetic).
tab_lid_t         = lid_roof_t; // mm. Lid-side tab thickness = lid_roof_t
                                 // -- the lid tab is a literal lateral
                                 // extension of the roof at 4 XY spots.
tab_clear_dia     = 2.8; // mm, lid tab through-hole. ASSUMPTION: same
                          // clearance-hole convention as the PCB mounting
                          // holes.
tab_pilot_dia     = standoff_pilot_dia; // mm, base tab pilot hole -- same
                                         // M2.5 self-tap pilot as the
                                         // standoffs (BOM simplicity).
// 45-deg self-supporting chamfer run for BASE tabs only. Lid tabs sit at
// the SAME Z-level as the lid roof, which is the first-printed layer when
// the lid is printed in its natural roof-down orientation -- i.e. lid tabs
// are effectively at bed level and need no chamfer. Base tabs, by
// contrast, sit near the TOP of the base wall (high up, mid-print, when
// the base is printed floor-down) and DO need this support feature to stay
// within max_overhang_deg. (An earlier draft of this design mistakenly
// planned to chamfer both -- corrected after checking actual print
// orientation for each part; see spec file.)
tab_chamfer_run = tab_project; // mm. A 45-deg chamfer needs equal
                                 // rise/run, so this run = tab_project.

// tab center positions, board-local XY (reuse mount_holes XY exactly, so
// lid and base tabs are trivially co-axial) with an explicit outward
// projection direction: -1 = projects toward -Y (front wall extension),
// +1 = projects toward +Y (rear wall extension).
tab_positions = [
    [ 3.5,  3.5, -1], // near MH-1, front-left
    [56.5,  3.5, -1], // near MH-2, front-right
    [56.5, 36.5, +1], // near MH-3, rear-right
    [ 3.5, 36.5, +1], // near MH-4, rear-left
];

// ----------------------------------------------------------------------
// 3. MODULES
// ----------------------------------------------------------------------

module standoff() {
    // Solid cylinder with a blind pilot hole, extruded from Z=0 (its own
    // local frame -- caller translates to the interior floor face).
    difference() {
        cylinder(d = standoff_od, h = standoff_h);
        translate([0, 0, standoff_h - standoff_pilot_depth])
            cylinder(d = standoff_pilot_dia, h = standoff_pilot_depth + 1);
    }
}

module base_standoffs() {
    for (m = mount_holes)
        translate([board_offset_x + m[0], board_offset_y + m[1], floor_t])
            standoff();
}

module base_tab(pos) {
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
    // 45-deg self-supporting chamfer/gusset under the tab (see rationale
    // at tab_chamfer_run above). Modeled as a hull() between two thin
    // slivers -- a reasonable approximation of a wedge gusset; a human
    // reviewing this in an actual OpenSCAD session should feel free to
    // refine the exact profile, this is not a load-bearing dimension.
    y_wall     = (dy < 0) ? 0 : base_outer_y;
    y_tab_edge = (dy < 0) ? -tab_project : base_outer_y + tab_project;
    z_bottom   = z0 - tab_chamfer_run;
    hull() {
        translate([tx - tab_w/2, y_wall, z_bottom])
            cube([tab_w, 0.01, 0.01]);
        translate([tx - tab_w/2, y_tab_edge, z0])
            cube([tab_w, 0.01, 0.01]);
    }
}

module base_tabs() {
    for (p = tab_positions) base_tab(p);
}

module base_shell() {
    difference() {
        // solid outer block: floor + walls, full height
        cube([base_outer_x, base_outer_y, base_total_h]);

        // interior cavity: hollow from the interior floor face all the way
        // through the top (the base has no ceiling -- only the lid does)
        translate([wall_t, wall_t, floor_t])
            cube([interior_x, interior_y, base_total_h - floor_t + 1]);

        // J1 (USB-C) cutout through the X=0 wall
        translate([-1,
                    board_offset_y + j1_y - j1_cut_w/2,
                    floor_t + j1_cut_z])
            cube([wall_t + 2, j1_cut_w, j1_cut_h]);
    }
}

module base() {
    union() {
        base_shell();
        base_standoffs();
        base_tabs();
    }
}

module lid_tab(pos) {
    // Built in the SAME global XY frame as base_tab (both use
    // board_offset_*/base_outer_* directly) so the two align exactly.
    // Z is LID-LOCAL (0 = skirt bottom); this tab sits flush with the
    // roof, i.e. it is a lateral extension of the roof at 4 XY spots.
    tx = board_offset_x + pos[0];
    dy = pos[2];
    tab_y0 = (dy < 0) ? -tab_project : base_outer_y;
    difference() {
        translate([tx - tab_w/2, tab_y0, lid_lip_h])
            cube([tab_w, tab_project, lid_roof_t]);
        translate([tx, tab_y0 + tab_project/2, lid_lip_h - 1])
            cylinder(d = tab_clear_dia, h = lid_roof_t + 2);
    }
}

module lid_tabs() {
    for (p = tab_positions) lid_tab(p);
}

module lid_shell() {
    // Lid-local frame: Z=0 at the skirt's bottom edge; XY matches the
    // GLOBAL frame directly (lid_x0/lid_y0 below only re-center the
    // larger skirt footprint -- they do NOT offset the coordinate system
    // board_offset_x/y already established).
    difference() {
        translate([lid_x0, lid_y0, 0])
            cube([lid_skirt_outer_x, lid_skirt_outer_y, lid_lip_h + lid_roof_t]);

        // hollow the skirt's interior (Z=0..lid_lip_h), leaving the roof
        // (Z=lid_lip_h..lid_lip_h+lid_roof_t) solid
        translate([lid_x0 + (lid_skirt_outer_x - lid_skirt_inner_x)/2,
                    lid_y0 + (lid_skirt_outer_y - lid_skirt_inner_y)/2,
                    -1])
            cube([lid_skirt_inner_x, lid_skirt_inner_y, lid_lip_h + 1]);

        // header/button bay: full-height notch through roof + skirt, open
        // to the rear (+Y) face
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

module lid() {
    union() {
        lid_shell();
        lid_tabs();
    }
}

// ----------------------------------------------------------------------
// 4. VISUAL-REFERENCE-ONLY GEOMETRY (the PCB and its tallest components).
//    All shown with the `%` background modifier -- OpenSCAD excludes `%`
//    geometry from STL export. This is NOT part of the manufactured parts;
//    it exists purely so a human rendering this file can visually
//    sanity-check clearances. Component footprints/heights here are the
//    same ESTIMATEs used for the cutout sizing above, simplified to boxes/
//    cylinders -- do not treat this as an accurate 3D model of the PCBA.
// ----------------------------------------------------------------------
module reference_pcba() {
    pcb_z = floor_t + standoff_h;
    // PCB slab
    color("green")
    translate([board_offset_x, board_offset_y, pcb_z])
        cube([pcb_length, pcb_width, pcb_thickness]);
    comp_z = pcb_z + pcb_thickness;
    // J1 USB-C (horizontal, opens -X) -- simple box, side-referenced
    translate([board_offset_x + j1_x - 3, board_offset_y + j1_y - j1_cut_w/2 + 0.75,
                comp_z])
        cube([7, j1_cut_w - 1.5, j1_ref_height]);
    // J2 / J3 headers (vertical, +Z) -- simple boxes, ~2.54mm pitch x4
    for (hx = [j2_x, j3_x])
        translate([board_offset_x + hx - 5, board_offset_y + 40 - 6, comp_z])
            cube([10, 6, top_component_clearance]);
    // SW1 reset button -- simple cylinder
    translate([board_offset_x + sw1_x, board_offset_y + sw1_y - 2.5, comp_z])
        cylinder(d = 5, h = 5);
    // D1 LED -- simple cylinder
    translate([board_offset_x + d1_x, board_offset_y + d1_y, comp_z])
        cylinder(d = 3, h = 1.2);
}

// ----------------------------------------------------------------------
// 5. TOP-LEVEL ASSEMBLY / LAYOUT
// ----------------------------------------------------------------------
if (show_mode == "assembled") {
    base();
    translate([0, 0, base_total_h - lid_lip_h]) lid();
    % reference_pcba();
} else if (show_mode == "print_layout") {
    // Base: already in its natural print orientation (floor-down).
    translate([0, 0, 0]) base();

    // Lid: flip roof-down (its natural print orientation) and lay it out
    // beside the base. This transform is a starting point only -- verify
    // visually in OpenSCAD / your slicer (e.g. a "lay flat" helper) before
    // trusting it; it has not been rendered by this agent.
    translate([base_outer_x + 15, 0, lid_lip_h + lid_roof_t])
        rotate([180, 0, 0])
            lid();
}

// ============================================================================
// END OF FILE -- bench-imu-01-enclosure.scad
// Companion file: bench-imu-01-dimensional-spec.md (full rationale, self-
// check against the Mechanical Reviewer's 10-item checklist, open
// UNKNOWNs/ASSUMPTIONs carried forward).
// ============================================================================
