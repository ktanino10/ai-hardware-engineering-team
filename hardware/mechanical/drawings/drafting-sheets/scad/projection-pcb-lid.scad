// Drafting-sheet source -- Piece 2/5: PCB lid, top-down SILHOUETTE
// projection. See `projection-stand-plate.scad` (sibling script) for the
// full "why projection(cut=false), not a camera render" rationale. Same
// assembled-frame translate + module call as
// `../../scad/assembled-pcb-lid.scad`:
//   translate([0, pcb_bay_y0, base_total_h - lid_lip_h]) pcb_lid();
// (the translate only affects the Z/Y placement baked into the source
// module call already used elsewhere in this project -- not invented here.)
//
// Regenerate DXF (consumed by ../build_drafting_sheet.py):
//   openscad -D 'show_mode="export"' --export-format dxf \
//     -o /tmp/pcb-lid-projection.dxf projection-pcb-lid.scad
include <../../../bench-imu-01-enclosure.scad>

projection(cut = false)
    translate([0, pcb_bay_y0, base_total_h - lid_lip_h])
        pcb_lid();
