#!/usr/bin/env python3
"""
Bench-IMU-01 -- CONCEPT attitude-hold demonstration animation (Blender
Python API).

THIS IS A CONCEPT, NOT A LITERAL CAPABILITY OF THIS RIG. Bench-IMU-01
rotates about exactly ONE (vertical/yaw) axis (`requirements/requirements.md`
REQ-011, `hardware/mechanical-interface.md`) -- there is no pitch/roll
degree of freedom, so literal "inversion"/tumble recovery is physically
impossible on this hardware. Per this task's own explicit reinterpretation:
this animation instead shows "a deviation from a reference attitude, held
by the reaction wheel returning the platform to that reference attitude" --
the single-axis analog of the eventual attitude-control concept. It is also
explicitly IDEALIZED, not a specific control-law's simulated response: no
closed-loop attitude controller (PID or otherwise) is implemented anywhere
in this project (`requirements/requirements.md` REQ-009/REQ-014, explicit
anti-scope statements) -- this animation cannot and does not claim to show
a particular controller's actual computed response, only an illustrative
"disturbance -> correction -> hold" beat using a smooth, generic ease
curve.

## Reference-attitude witness mark

Reuses the existing `rotation_index_pointer()` feature already modeled in
`bench-imu-01-enclosure.scad` (Rev 4.1, MISS-024 mitigation) -- a small
witness tab fused to the rotating base's own north wall, already intended
by its own source-file comment to be "sighted... against any convenient
FIXED external landmark." This animation adds exactly that fixed landmark:
a new, clearly-marked (bright green) reference-mark object placed at the
pointer's own real rest-position world coordinates (measured directly from
the `assembled-base-assembly.stl` binary -- (fw_cx, fw_cy + 115.5) -- not
guessed), so "pointer visually aligned with the mark" corresponds exactly
to "platform at its reference/rest rotation," and any deviation is
immediately visible as the two features separating.

## What this animation shows (idealized beats, EASE_IN_OUT bezier
## throughout -- deliberately NOT the constant-rate LINEAR keyframing
## `../physics-demo/build_physics_demo_animation.py` uses, since here
## nothing is claimed to be a precise rate)

1. Hold at reference (pointer aligned with the fixed mark).
2. EXTERNAL DISTURBANCE (explicitly NOT caused by the reaction wheel --
   the flywheel visually stays at rest through this phase): platform eases
   to +35 deg off reference.
3. Hold at the disturbed attitude (pointer visibly misaligned from the
   fixed mark).
4. CORRECTION: the flywheel eases up to a stylized spin (illustrative
   only, not to the real 1:15 ratio scale used in the physics-demo
   animation) and back down to rest, symmetric ease-in-out, while the
   platform eases back to exactly 0 deg (reference) -- a single bezier
   segment's own natural "zero velocity at both endpoints, peak in the
   middle" shape does this without needing a hand-authored 3-segment
   trapezoid.
5. Final hold at reference (pointer re-aligned with the fixed mark).

Reuses the same assembled-position STL pipeline and PLATFORM/WHEEL/STATIC
grouping technique as `../physics-demo/build_physics_demo_animation.py`
(see that script's own docstring for the stator/rotor parenting details) --
only the keyframe values/interpolation and the reference-mark object
differ.

## Regeneration steps

Same pipeline shape as `../physics-demo/build_physics_demo_animation.py`:
build scene -> chunked render -> `annotate_concept_demo_frames.py`
(Pillow: CONCEPT title card + persistent watermark + outro) -> ffmpeg
encode (same 2-pass MP4 + palette-GIF technique documented in
`../animation/build_assembly_animation.py`'s own header).
"""

import math

import bpy
import mathutils

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
STL_DIR = "/tmp/bench-exploded-stl"
FRAMES_DIR = "/tmp/concept-demo-frames/raw"
FPS = 24
RESOLUTION = (1280, 960)

FW_CX, FW_CY = 53.5, 52.5  # bench-imu-01-enclosure.scad: fw_cx/fw_cy, the real rotation axis

# rotation_index_pointer()'s own real rest-position tip, measured directly
# from assembled-base-assembly.stl's binary vertex data this task (X=fw_cx
# exactly, Y=168.0 -- i.e. radius 115.5mm from (FW_CX,FW_CY), pointing due
# +Y at rotation_euler.z=0) -- NOT read off the .scad source formula.
POINTER_REST_XY = (53.5, 168.0)
POINTER_RADIUS = POINTER_REST_XY[1] - FW_CY  # 115.5mm

PLATFORM_PARTS = [
    "assembled-base-assembly",
    "assembled-pcb-lid",
    "assembled-containment-cap",
    "assembled-reference-motor-body",
]
WHEEL_PARTS = ["assembled-reference-flywheel-rotor"]
STATIC_PARTS = ["assembled-stand-plate", "assembled-pinch-guard", "assembled-reference-bearing"]
ALL_PARTS = PLATFORM_PARTS + WHEEL_PARTS + STATIC_PARTS

COLOR_MAP = {
    "assembled-base-assembly":    (0.35, 0.55, 0.80),
    "assembled-pcb-lid":          (0.45, 0.75, 0.45),
    "assembled-containment-cap":  (0.90, 0.55, 0.20),
    "assembled-stand-plate":      (0.55, 0.55, 0.58),
    "assembled-pinch-guard":      (0.80, 0.25, 0.30),
    "assembled-reference-bearing":       (0.75, 0.76, 0.78),
    "assembled-reference-motor-body":    (0.22, 0.23, 0.27),
    "assembled-reference-flywheel-rotor": (0.62, 0.18, 0.68),
}

DISTURBANCE_DEG = 35.0
DISTURBANCE_RAD = math.radians(DISTURBANCE_DEG)
WHEEL_STYLIZED_PEAK = 3 * 2 * math.pi  # 3 full turns, illustrative only

# --- Timeline (seconds -> frames @ FPS=24) ---------------------------------
def f(t_seconds):
    return 1 + round(t_seconds * FPS)

T_REF_HOLD_END = 1.5
T_DISTURB_END = 3.0
T_DISTURBED_HOLD_END = 4.0
T_CORRECTION_END = 7.0
T_FINAL_HOLD_END = 9.0

FRAME_REF_HOLD_END = f(T_REF_HOLD_END)
FRAME_DISTURB_END = f(T_DISTURB_END)
FRAME_DISTURBED_HOLD_END = f(T_DISTURBED_HOLD_END)
FRAME_CORRECTION_END = f(T_CORRECTION_END)
FRAME_FINAL_HOLD_END = f(T_FINAL_HOLD_END)

TIMELINE = {
    "ref_hold_end": FRAME_REF_HOLD_END,
    "disturb_end": FRAME_DISTURB_END,
    "disturbed_hold_end": FRAME_DISTURBED_HOLD_END,
    "correction_end": FRAME_CORRECTION_END,
    "final_hold_end": FRAME_FINAL_HOLD_END,
}


def make_mat(name, color, metallic=0.0, roughness=0.4, alpha=1.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        m.blend_method = 'BLEND'
    return m


def get_fcurves(obj):
    """Blender 5.x layered-action F-curve access (see
    ../animation/build_assembly_animation.py's own docstring for why)."""
    action = obj.animation_data.action
    fcurves = []
    for layer in action.layers:
        for strip in layer.strips:
            for channelbag in strip.channelbags:
                fcurves.extend(channelbag.fcurves)
    return fcurves


def keyframe_rot_z(obj, frame, angle_rad):
    obj.rotation_euler = (0.0, 0.0, angle_rad)
    obj.keyframe_insert(data_path="rotation_euler", index=2, frame=frame)


def ease(obj):
    """EASE_IN_OUT bezier (matches ../animation/build_assembly_animation.py's
    own convention) -- deliberately NOT the physics-demo's LINEAR keying,
    since nothing here is claimed to be a precise constant rate."""
    for fc in get_fcurves(obj):
        fc.extrapolation = 'CONSTANT'
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.easing = 'EASE_IN_OUT'


def build_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    imported = {}
    for p in ALL_PARTS:
        path = f"{STL_DIR}/{p}.stl"
        before = set(bpy.data.objects.keys())
        bpy.ops.wm.stl_import(filepath=path, forward_axis='Y', up_axis='Z')
        after = set(bpy.data.objects.keys())
        new_name = list(after - before)[0]
        obj = bpy.data.objects[new_name]
        obj.name = p
        imported[p] = obj

    for name, color in COLOR_MAP.items():
        obj = imported[name]
        alpha = 1.0
        metallic = 0.0
        if name == "assembled-reference-bearing":
            metallic, alpha = 0.9, 0.75
        elif name in ("assembled-reference-motor-body", "assembled-reference-flywheel-rotor"):
            metallic, alpha = 0.7, 0.85
        mat = make_mat(f"mat_{name}", color, metallic=metallic, alpha=alpha)
        obj.data.materials.clear()
        obj.data.materials.append(mat)

    bpy.context.view_layer.update()

    platform_pivot = bpy.data.objects.new("PlatformPivot", None)
    platform_pivot.location = (FW_CX, FW_CY, 0)
    bpy.context.scene.collection.objects.link(platform_pivot)
    wheel_pivot = bpy.data.objects.new("WheelPivot", None)
    wheel_pivot.location = (FW_CX, FW_CY, 0)
    bpy.context.scene.collection.objects.link(wheel_pivot)
    bpy.context.view_layer.update()

    def parent_keep_transform(obj, pivot):
        obj.parent = pivot
        obj.matrix_parent_inverse = pivot.matrix_world.inverted()

    for name in PLATFORM_PARTS:
        parent_keep_transform(imported[name], platform_pivot)
    for name in WHEEL_PARTS:
        parent_keep_transform(imported[name], wheel_pivot)

    # --- Keyframe rotation (see module docstring for the 5-beat shape) --
    keyframe_rot_z(platform_pivot, 1, 0.0)
    keyframe_rot_z(platform_pivot, FRAME_REF_HOLD_END, 0.0)
    keyframe_rot_z(platform_pivot, FRAME_DISTURB_END, DISTURBANCE_RAD)
    keyframe_rot_z(platform_pivot, FRAME_DISTURBED_HOLD_END, DISTURBANCE_RAD)
    keyframe_rot_z(platform_pivot, FRAME_CORRECTION_END, 0.0)
    keyframe_rot_z(platform_pivot, FRAME_FINAL_HOLD_END, 0.0)
    ease(platform_pivot)

    keyframe_rot_z(wheel_pivot, 1, 0.0)
    keyframe_rot_z(wheel_pivot, FRAME_REF_HOLD_END, 0.0)
    keyframe_rot_z(wheel_pivot, FRAME_DISTURB_END, 0.0)  # wheel at rest during EXTERNAL disturbance
    keyframe_rot_z(wheel_pivot, FRAME_DISTURBED_HOLD_END, 0.0)
    keyframe_rot_z(wheel_pivot, FRAME_CORRECTION_END, WHEEL_STYLIZED_PEAK)  # spins up then back to ~0 rate (ease-in-out)
    keyframe_rot_z(wheel_pivot, FRAME_FINAL_HOLD_END, WHEEL_STYLIZED_PEAK)  # holds final angle (rate already ~0 by FRAME_CORRECTION_END)
    ease(wheel_pivot)

    # --- Ground plane -----------------------------------------------------
    bpy.ops.mesh.primitive_plane_add(size=400, location=(FW_CX, FW_CY, -14))
    ground = bpy.context.active_object
    ground.name = "GroundPlane"
    ground.data.materials.append(make_mat("mat_ground", (0.78, 0.78, 0.80), roughness=0.8))

    # --- Fixed reference-attitude mark (bright green flag), placed at the
    # pointer's own measured rest position, slightly beyond its radius so
    # the two features read as clearly distinct but close together when
    # aligned. NOT a physical part -- a visualization aid, like the
    # physics-demo's own fixed tick.
    mark_x, mark_y = FW_CX, FW_CY + POINTER_RADIUS + 8
    bpy.ops.mesh.primitive_cylinder_add(radius=2.0, depth=26, location=(mark_x, mark_y, -14 + 13))
    mark = bpy.context.active_object
    mark.name = "ReferenceAttitudeMark"
    mark.data.materials.append(make_mat("mat_mark", (0.15, 0.85, 0.25), roughness=0.5))

    # --- Camera: mostly top-down (mirrors ../physics-demo/'s own choice) --
    cam_data = bpy.data.cameras.new("ConceptCam")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 300
    cam_obj = bpy.data.objects.new("ConceptCam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    cam_dir = mathutils.Vector((0.12, -0.12, 1.5)).normalized()
    cam_obj.location = mathutils.Vector((FW_CX, FW_CY, 0)) + cam_dir * 300
    cam_data.clip_start = 0.1
    cam_data.clip_end = 900
    target = bpy.data.objects.new("AimTarget", None)
    target.location = (FW_CX, FW_CY, 0)
    bpy.context.scene.collection.objects.link(target)
    con = cam_obj.constraints.new('TRACK_TO')
    con.target = target
    con.track_axis = 'TRACK_NEGATIVE_Z'
    con.up_axis = 'UP_Y'
    bpy.context.scene.camera = cam_obj

    # --- Lighting --------------------------------------------------------
    key = bpy.data.lights.new("KeySun", type='SUN'); key.energy = 4.0
    key_obj = bpy.data.objects.new("KeySun", key); key_obj.rotation_euler = (0.7, 0.15, 0.6)
    bpy.context.scene.collection.objects.link(key_obj)
    fill = bpy.data.lights.new("FillSun", type='SUN'); fill.energy = 1.3
    fill_obj = bpy.data.objects.new("FillSun", fill); fill_obj.rotation_euler = (1.3, -0.2, -2.1)
    bpy.context.scene.collection.objects.link(fill_obj)

    world = bpy.context.scene.world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.60, 0.61, 0.63, 1)

    scene = bpy.context.scene
    scene.view_settings.view_transform = 'Standard'
    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError:
        scene.render.engine = 'BLENDER_EEVEE'
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = FRAME_FINAL_HOLD_END
    scene.frame_current = 1

    print("Scene built. Timeline:", TIMELINE)


def render_frame_sequence(frame_start=None, frame_end=None):
    import os
    os.makedirs(FRAMES_DIR, exist_ok=True)
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = f"{FRAMES_DIR}/f_"
    scene.render.resolution_x = RESOLUTION[0]
    scene.render.resolution_y = RESOLUTION[1]
    scene.render.resolution_percentage = 100
    if frame_start is not None:
        scene.frame_start = frame_start
    if frame_end is not None:
        scene.frame_end = frame_end
    bpy.ops.render.render(animation=True)
    print(f"Rendered frames {scene.frame_start}-{scene.frame_end} to {FRAMES_DIR}")


def ensure_scene():
    if "PlatformPivot" not in bpy.data.objects:
        build_scene()
    else:
        print("Scene already present, reusing.")


if __name__ == "__main__":
    build_scene()
    render_frame_sequence()
    print("Done. Now run annotate_concept_demo_frames.py, then encode with ffmpeg.")
