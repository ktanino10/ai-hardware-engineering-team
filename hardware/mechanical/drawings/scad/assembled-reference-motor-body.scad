// Drawing helper — reference ONLY, not a printed piece, not one of the 5
// manufactured pieces. Bought T-Motor MN2206-13 KV2000 (`bom/component-
// selection.md` Motor Approval), the STATOR/mounting-housing half only —
// see `assembled-reference-flywheel-rotor.scad` (sibling script) for the
// rotating shaft + hub collar + flywheel disk half. Added this pass to
// close a real documentation gap: the exploded view previously omitted
// the motor/flywheel entirely (`drawings/README.md`'s prior "deliberately
// left out... judged to add clutter" note) even though
// `assembly-instructions.md` §4.2/§4.4 documents mounting them as real
// build steps, and the bearing (also a bought, non-printed part) was
// already shown as a reference ghost. This restores parity with that
// precedent rather than leaving the gap.
//
// Geometry: duplicates ONLY the "motor body" cylinder from the parent
// file's own `reference_motor_flywheel()` module (Section 4,
// `bench-imu-01-enclosure.scad`) — same variables, nothing invented.
// Deliberately excludes that module's shaft/hub-collar/flywheel-disk
// primitives (those belong to the ROTATING group, see the sibling
// script) and its rotation-clearance keep-out cylinder (`fw_env_dia`/
// `fw_env_axial` — a translucent annotation volume marking a keep-out
// zone, not a physical object; including it in an STL export would merge
// it into opaque solid geometry, misrepresenting an annotation as a part).
//
// Stator/rotor split rationale: the motor body is fastened to
// `motor_platform()` with 4× plain M3 screws (`assembly-instructions.md`
// §4.2/§5 fastener table) — whatever is bolted down to the platform does
// not rotate relative to it, regardless of the motor's own internal
// stator/bell construction. This group is therefore part of the ROTATING
// PLATFORM assembly (moves together with base()/pcb_lid()/
// containment_cap(), NOT the flywheel) for both the exploded view and the
// physics-demo animation (`../physics-demo/`).
//
// Regenerate assembled-position STL (for Blender import):
//   openscad -D 'show_mode="export"' --backend=manifold --export-format binstl \
//     -o /tmp/assembled-reference-motor-body.stl assembled-reference-motor-body.scad
include <../../bench-imu-01-enclosure.scad>

module reference_motor_body_only() {
    // Motor body only (silver) — same single translate + cylinder as
    // reference_motor_flywheel()'s first primitive, byte-for-byte same
    // variables (fw_cx, fw_cy, fw_motor_platform_top, m1_body_dia, m1_body_h).
    color("silver")
    translate([fw_cx, fw_cy, fw_motor_platform_top])
        cylinder(d = m1_body_dia, h = m1_body_h);
}

reference_motor_body_only();
