// Export helper — Piece 1/5: base assembly (print-ready, isolated).
// Renders base() + bmount_flange() + rotation_index_pointer() +
// cable_anchor_tab()x2 as ONE combined solid (they print as a single job —
// see bench-imu-01-enclosure.scad's own print_layout comment, "these two
// solids now print as ONE combined job"). This is a render/export
// convenience script only — it does NOT redefine any geometry; it just
// isolates the exact same module calls already used in the parent file's
// own "print_layout" show_mode branch, via `-D 'show_mode="export"'` on the
// command line so neither the "assembled" nor "print_layout" branch in the
// parent file executes (avoiding double-rendering the whole assembly).
// Regenerate with:
//   openscad -D 'show_mode="export"' --export-format binstl -o ../bench-imu-01-base-assembly.stl export-base-assembly.scad
include <../../bench-imu-01-enclosure.scad>

translate([0, 0, bmount_flange_t]) {
    base();
    bmount_flange();
    rotation_index_pointer();
    cable_anchor_tab(false);
    cable_anchor_tab(true);
}
