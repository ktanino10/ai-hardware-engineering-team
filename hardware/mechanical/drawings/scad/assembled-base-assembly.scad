// Drawing helper — Piece 1/5: base assembly, ASSEMBLED-FRAME position (NOT
// the print_layout orientation used by hardware/mechanical/stl/export/
// export-base-assembly.scad). Renders base() + bmount_flange() +
// rotation_index_pointer() + cable_anchor_tab()x2 exactly as the parent
// file's own `show_mode == "assembled"` branch calls them (bare, no
// translate) — every one of these modules already bakes in its own correct
// global (fw_cx, fw_cy, Z) position internally, per that branch's own
// comment. This file does NOT invent any coordinate; it only isolates the
// same 5 calls the parent file's own assembled view already makes, for (a)
// per-part 2D orthographic projection and (b) an assembled-position STL
// export for Blender exploded-view import. Color is cosmetic only (STL is
// color-less; this only affects the 2D PNG renders).
// Regenerate 2D drawing, e.g. top view:
//   openscad --projection=ortho --render --autocenter --viewall \
//     --imgsize=1600,1200 --camera=0,0,0,0,0,0,300 \
//     -o ../2d/base-assembly-top.png assembled-base-assembly.scad
// Regenerate assembled-position STL (for Blender import):
//   openscad --backend=manifold --export-format binstl \
//     -o /tmp/assembled-base-assembly.stl assembled-base-assembly.scad
include <../../bench-imu-01-enclosure.scad>

color("gainsboro") {
    base();
    bmount_flange();
    rotation_index_pointer();
    cable_anchor_tab(false);
    cable_anchor_tab(true);
}
