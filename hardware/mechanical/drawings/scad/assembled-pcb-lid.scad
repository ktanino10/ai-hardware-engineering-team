// Drawing helper — Piece 2/5: PCB lid, ASSEMBLED-FRAME position (NOT the
// print_layout flip used by hardware/mechanical/stl/export/export-pcb-lid.scad).
// Renders pcb_lid() with the exact same translate the parent file's own
// `show_mode == "assembled"` branch applies:
//   translate([0, pcb_bay_y0, base_total_h - lid_lip_h]) pcb_lid();
// — not an invented coordinate. Roof-up, as installed, sitting on top of
// the base's PCB bay.
// Regenerate 2D drawing, e.g. top view:
//   openscad --projection=ortho --render --autocenter --viewall \
//     --imgsize=1600,1200 --camera=0,0,0,0,0,0,300 \
//     -o ../2d/pcb-lid-top.png assembled-pcb-lid.scad
// Regenerate assembled-position STL (for Blender import):
//   openscad --backend=manifold --export-format binstl \
//     -o /tmp/assembled-pcb-lid.stl assembled-pcb-lid.scad
include <../../bench-imu-01-enclosure.scad>

color("gainsboro")
    translate([0, pcb_bay_y0, base_total_h - lid_lip_h])
        pcb_lid();
