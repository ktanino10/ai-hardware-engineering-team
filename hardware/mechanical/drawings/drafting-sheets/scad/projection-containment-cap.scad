// Drafting-sheet source -- Piece 3/5: containment cap, top-down SILHOUETTE
// projection. See `projection-stand-plate.scad` (sibling script) for the
// full "why projection(cut=false), not a camera render" rationale. Same
// assembled-frame module call as `../../scad/assembled-containment-cap.scad`.
//
// Regenerate DXF (consumed by ../build_drafting_sheet.py):
//   openscad -D 'show_mode="export"' --export-format dxf \
//     -o /tmp/containment-cap-projection.dxf projection-containment-cap.scad
include <../../../bench-imu-01-enclosure.scad>

projection(cut = false)
    containment_cap();
