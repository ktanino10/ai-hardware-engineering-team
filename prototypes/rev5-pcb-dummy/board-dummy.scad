// WIP NONFUNCTIONAL DUMMY -- NOT ASSEMBLY / PRINT / SAFETY APPROVAL.
// Units: mm. Frozen source: a361a6177525650abb9092f3c68fdd2be55da0de.
// Authority: hardware/pcb/bench-imu-01-rev5/bench-imu-01-rev5.kicad_pcb.
// Native Edge.Cuts is exactly one gr_rect, UUID:
// fc391778-6887-50ec-aa10-e4c86da02b16. Use its centerline, not stroke width.
// Preserve numeric X/Y, origin and orientation: no mirror/scale/compensation.
native_edge_start_mm = [0, 0];
native_edge_end_mm = [150, 95];
native_outline_mm = [
    [native_edge_start_mm[0], native_edge_start_mm[1]],
    [native_edge_end_mm[0], native_edge_start_mm[1]],
    [native_edge_end_mm[0], native_edge_end_mm[1]],
    [native_edge_start_mm[0], native_edge_end_mm[1]]
];
// CONFIRMED native general/thickness; nominal VISUAL surrogate only.
nominal_visual_thickness_mm = 1.6;
// CONFIRMED MH1, MH2, MH3, MH4: F.Cu, angle 0, local pad at [0,0].
mount_centers_mm = [[8, 8], [142, 8], [8, 87], [142, 87]];
mount_diameters_mm = [2.7, 2.7, 2.7, 2.7];
// ASSUMPTION: numerical tessellation choice, NOT a print-fit tolerance.
hole_segments = 256;
// ASSUMPTION: visual slab bottom Z=0; +Z extrudes nominal thickness.
// 2D subtraction before extrusion makes full-depth openings, no cutter cap.
linear_extrude(height = nominal_visual_thickness_mm, center = false)
    difference() {
        polygon(points = native_outline_mm);
        for (i = [0 : len(mount_centers_mm) - 1])
            translate(mount_centers_mm[i])
                circle(d = mount_diameters_mm[i], $fn = hole_segments);
    }
