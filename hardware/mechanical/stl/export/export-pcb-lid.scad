// Export helper — Piece 2/5: PCB lid (print-ready, isolated).
// Renders pcb_lid() flipped roof-down (its natural print orientation, per
// the parent file's own print_layout comment). Rev 3 geometry, unchanged
// by Rev 4/4.1.
// Regenerate with:
//   openscad -D 'show_mode="export"' --export-format binstl -o ../bench-imu-01-pcb-lid.stl export-pcb-lid.scad
include <../../bench-imu-01-enclosure.scad>

rotate([180, 0, 0])
    pcb_lid();
