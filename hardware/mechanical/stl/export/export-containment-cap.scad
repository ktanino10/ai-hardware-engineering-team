// Export helper — Piece 3/5: containment cap (print-ready, isolated).
// Renders containment_cap() flipped dome-down (its natural print
// orientation, per the parent file's own print_layout comment). Rev 3
// geometry, unchanged by Rev 4/4.1. This is the flywheel safety-containment
// piece — REQ-403/MISS-016, human ACCEPTED-RISK (Rev 3, ECO-024/025).
// Regenerate with:
//   openscad -D 'show_mode="export"' --export-format binstl -o ../bench-imu-01-containment-cap.stl export-containment-cap.scad
include <../../bench-imu-01-enclosure.scad>

rotate([180, 0, 0])
    containment_cap();
