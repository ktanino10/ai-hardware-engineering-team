// Export helper — Piece 4/5: stand plate (print-ready, isolated).
// Renders stand_plate() — new, Rev 4 — Z-normalized to sit flat at this
// export's own Z=0 (matches the parent file's own print_layout Z-shift by
// -stand_plate_bottom_z). No rotation needed — a uniform annulus, prints
// flat, either face down (see stand_plate()'s own header comment: no
// internal-overhang concern, unlike the base+flange combo).
// Regenerate with:
//   openscad -D 'show_mode="export"' --export-format binstl -o ../bench-imu-01-stand-plate.stl export-stand-plate.scad
include <../../bench-imu-01-enclosure.scad>

translate([0, 0, -stand_plate_bottom_z])
    stand_plate();
