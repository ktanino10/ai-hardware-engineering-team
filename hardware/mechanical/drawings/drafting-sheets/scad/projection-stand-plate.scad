// Drafting-sheet source -- Piece 4/5: stand plate, top-down SILHOUETTE
// projection (NOT a cross-section: OpenSCAD's `projection(cut=false)`
// collapses the whole 3D solid's outer boundary onto the XY plane, i.e.
// every face's outline superimposed, matching what a real top-down
// drafting view shows: overall outline + any hole that passes fully
// through in Z). Same assembled-frame module call as
// `../../scad/assembled-stand-plate.scad` (the existing 2D orthographic-
// render wrapper) -- this script does NOT duplicate or reinterpret that
// script's geometry choice, it just feeds the identical call through
// `projection()` instead of a camera render, to get real vector/DXF data
// for `build_drafting_sheet.py` to parse and dimension.
//
// Regenerate DXF (consumed by ../build_drafting_sheet.py):
//   openscad -D 'show_mode="export"' --export-format dxf \
//     -o /tmp/stand-plate-projection.dxf projection-stand-plate.scad
include <../../../bench-imu-01-enclosure.scad>

projection(cut = false)
    stand_plate();
