// Drawing helper — Piece 4/5: stand plate, ASSEMBLED-FRAME position (NOT
// the Z-normalized-to-print-bed position used by hardware/mechanical/stl/
// export/export-stand-plate.scad). Renders stand_plate() bare, exactly as
// the parent file's own `show_mode == "assembled"` branch calls it — this
// is the true system ground plane (stand_plate_bottom_z, the lowest point
// of the whole rig, per §18's Global Z-stack).
// Regenerate 2D drawing, e.g. top view:
//   openscad --projection=ortho --render --autocenter --viewall \
//     --imgsize=1600,1200 --camera=0,0,0,0,0,0,300 \
//     -o ../2d/stand-plate-top.png assembled-stand-plate.scad
// Regenerate assembled-position STL (for Blender import):
//   openscad --backend=manifold --export-format binstl \
//     -o /tmp/assembled-stand-plate.stl assembled-stand-plate.scad
include <../../bench-imu-01-enclosure.scad>

color("gainsboro")
    stand_plate();
