// Drawing helper — Piece 5/5: pinch guard, ASSEMBLED-FRAME position, FULL
// RING (quadrant = -1, the default) — NOT the single print-ready quadrant
// used by hardware/mechanical/stl/export/export-pinch-guard-quadrant.scad.
// The real installed part is 4 identical printed quadrants joined into one
// ring (per that export script's own note, confirmed by direct module
// inspection, not re-verified here — validation/change-log.md ECO-032); this
// file renders the assembled FULL ring for 2D/exploded-view purposes, since
// that's how it actually sits in the finished rig. MISS-023/REQ-407(b)
// mitigation — human ACCEPTED-RISK, a partial (~77.7%-by-area) hazard-band
// mitigation, not a complete guard (validation/open-issues.md MISS-023).
// Regenerate 2D drawing, e.g. top view:
//   openscad --projection=ortho --render --autocenter --viewall \
//     --imgsize=1600,1200 --camera=0,0,0,0,0,0,300 \
//     -o ../2d/pinch-guard-top.png assembled-pinch-guard.scad
// Regenerate assembled-position STL (for Blender import):
//   openscad --backend=manifold --export-format binstl \
//     -o /tmp/assembled-pinch-guard.stl assembled-pinch-guard.scad
include <../../bench-imu-01-enclosure.scad>

color("gainsboro")
    pinch_guard();
