// Export helper — Piece 5/5: pinch guard, ONE quadrant (print-ready,
// isolated; print x4 total — MISS-023 fix, Rev 4.1).
// Renders a single 90-degree quadrant (index 0) of pinch_guard(), Z/XY-
// normalized to sit flat at this export's own origin (matches the parent
// file's own print_layout transform). All 4 quadrants are geometrically
// IDENTICAL (pinch_guard()'s own module body is a perfectly rotationally-
// symmetric ring cut at four evenly-spaced 90-degree angles — verified by
// direct inspection of the module definition, not assumed) — this single
// STL is the print file for all 4 physical copies needed, not one of four
// different shapes. See hardware/mechanical/stl/README.md.
// Regenerate with:
//   openscad -D 'show_mode="export"' --export-format binstl -o ../bench-imu-01-pinch-guard-quadrant.stl export-pinch-guard-quadrant.scad
include <../../bench-imu-01-enclosure.scad>

translate([-fw_cx, -fw_cy, -stand_plate_bottom_z])
    pinch_guard(0);
