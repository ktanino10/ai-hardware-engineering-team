// Drawing helper — reference ONLY, not a printed piece, not one of the 5
// manufactured pieces. The ROTATING half of the bought motor + flywheel:
// the motor's exposed shaft, the hub collar, and the flywheel disk itself
// — see `assembled-reference-motor-body.scad` (sibling script) for the
// stationary motor-body/housing half. Added this pass to close a real
// documentation gap: see that sibling script's header comment for the
// full "why this exists now" rationale (`drawings/README.md`'s prior
// deliberate-omission note being reversed, per this task's own request).
//
// Geometry: duplicates ONLY the shaft + hub-collar + flywheel-disk
// primitives from the parent file's own `reference_motor_flywheel()`
// module (Section 4, `bench-imu-01-enclosure.scad`) — same variables,
// nothing invented. Deliberately excludes that module's motor-body
// primitive (stationary, see sibling script) and its rotation-clearance
// keep-out cylinder (`fw_env_dia`/`fw_env_axial` — a translucent
// annotation volume marking a keep-out zone, not a physical object;
// including it in an STL export would merge it into opaque solid
// geometry, misrepresenting an annotation as a part).
//
// Stator/rotor split rationale: `assembly-instructions.md` §4.4 step 5
// explicitly describes sliding the hub collar onto "the motor's exposed
// shaft," then the flywheel disk onto the hub collar — this whole group
// is the motor's rotating output, which is what the reaction-wheel
// physics (`bom/component-selection.md` — I_wheel = 4.5e-5 kg*m^2) is
// actually about. This group is therefore the FLYWHEEL/ROTOR in both the
// exploded view and the physics-demo animation (`../physics-demo/`),
// distinct from the stationary motor-body group (sibling script), which
// moves with the platform instead.
//
// Regenerate assembled-position STL (for Blender import):
//   openscad -D 'show_mode="export"' --backend=manifold --export-format binstl \
//     -o /tmp/assembled-reference-flywheel-rotor.stl assembled-reference-flywheel-rotor.scad
include <../../bench-imu-01-enclosure.scad>

module reference_flywheel_rotor_only() {
    // Shaft (silver) — same translate + cylinder as
    // reference_motor_flywheel()'s 2nd primitive.
    color("silver")
    translate([fw_cx, fw_cy, fw_motor_bell_top])
        cylinder(d = m1_shaft_dia, h = fw_shaft_exposed_len_needed);
    // Hub collar (gray) — same translate + cylinder as
    // reference_motor_flywheel()'s 3rd primitive.
    color("gray")
    translate([fw_cx, fw_cy, fw_motor_bell_top])
        cylinder(d = fw_hub_collar_od, h = fw_hub_collar_h);
    // Flywheel disk (orange, steel -- NOT printed, reference only) — same
    // translate + cylinder as reference_motor_flywheel()'s 4th primitive.
    color("orange")
    translate([fw_cx, fw_cy, fw_disk_bottom])
        cylinder(d = fw_dia, h = fw_t);
}

reference_flywheel_rotor_only();
