// Drawing helper — Piece 3/5: containment cap, ASSEMBLED-FRAME position
// (NOT the print_layout flip used by hardware/mechanical/stl/export/
// export-containment-cap.scad). Renders containment_cap() bare, exactly as
// the parent file's own `show_mode == "assembled"` branch calls it — the
// module already bakes in its own correct global (fw_cx, fw_cy, Z)
// position. This is the flywheel safety-containment piece — REQ-403/
// MISS-016, human ACCEPTED-RISK (Rev 3, ECO-024/025) — installed LAST in
// the real assembly sequence (dimensional-spec.md §14, step 6).
// Regenerate 2D drawing, e.g. top view:
//   openscad --projection=ortho --render --autocenter --viewall \
//     --imgsize=1600,1200 --camera=0,0,0,0,0,0,300 \
//     -o ../2d/containment-cap-top.png assembled-containment-cap.scad
// Regenerate assembled-position STL (for Blender import):
//   openscad --backend=manifold --export-format binstl \
//     -o /tmp/assembled-containment-cap.stl assembled-containment-cap.scad
include <../../bench-imu-01-enclosure.scad>

color("gainsboro")
    containment_cap();
