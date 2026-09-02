// Drawing helper — reference ONLY, not a printed piece. Bought BC Precision
// 4LS-3 lazy-susan bearing (DS-BRG-001, datasheets/evidence-log.md),
// rendered via the parent file's own reference_bearing() simplified
// single-cylinder stand-in (NOT a detailed model of the real 2-plate +
// captive-ball-race part). Used ONLY for the Blender exploded-assembly view,
// so the render shows what physically occupies the gap between
// stand_plate() and bmount_flange() instead of leaving an unexplained empty
// space — not used for any of the 5 printed-piece 2D drawings, since this
// is not one of the 5 printed pieces. No color() override here: keep
// reference_bearing()'s own internal color("silver") so it visually reads
// as a distinct bought/metal part, not a printed PETG piece.
// Regenerate assembled-position STL (for Blender import):
//   openscad -D 'show_mode="export"' --backend=manifold --export-format binstl \
//     -o /tmp/assembled-reference-bearing.stl assembled-reference-bearing.scad
include <../../bench-imu-01-enclosure.scad>

reference_bearing();
