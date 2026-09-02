#!/usr/bin/env python3
"""
Bench-IMU-01 -- Physics-based angular-momentum-conservation SIMULATION
animation (Blender Python API).

THIS IS A SIMULATION / PREDICTION, NOT A MEASUREMENT. No PCB has been
fabricated/populated yet (`assembly-instructions.md` Sec 4.1 placeholder;
366 unresolved DRC items on the still-open PCB-layout branch) and no
firmware has ever been flashed to real hardware. Every number this
animation renders is copied verbatim from the already-approved ESTIMATE
in `bom/component-selection.md` ("Platform angular-rate physics finding" +
its illustrative operating-point table) -- nothing here is re-derived or
newly invented. See this directory's own README section for the full
future-real-hardware-test success-criteria writeup this animation's own
outro card also states on-screen.

## What this animation shows

Reuses the same assembled-position STL pipeline as
`../exploded/build_exploded_view.py` (now including the motor-body/
flywheel-rotor ghosts added this same task), but at TRUE ASSEMBLED
positions (no explode offsets) and grouped into 3 rigid-body pivots:

- PLATFORM (base-assembly + pcb-lid + containment-cap + motor-body ghost):
  the part that actually rotates in reaction, per
  `hardware/mechanical-interface.md`/REQ-011's own single (vertical/yaw)
  axis. Rendered at the REAL, physically-accurate predicted rate every
  stage (12 deg/s then ~117 deg/s) -- this is the actual quantity of
  physical interest for a conservation-of-angular-momentum demonstration,
  so it is never sped up or slowed down for legibility.
- WHEEL (flywheel-rotor ghost only -- the hub collar + flywheel disk,
  per `assembled-reference-flywheel-rotor.scad`'s own stator/rotor split
  rationale): Stage 1 (30 RPM = 180 deg/s) is ALSO rendered at its true
  real-time rate (180 deg/s / 24fps = 7.5 deg/frame -- smooth, no aliasing
  concern). Stage 2 (300 RPM = 1800 deg/s) would be 75 deg/frame at this
  project's 24fps convention -- a genuine strobe/aliasing problem, verified
  by an intermediate render this task, not assumed -- so Stage 2's WHEEL
  visual spin is a disclosed, stylized 720 deg/s indicator instead (4x
  Stage 1's rate, not the true 10x/1800 deg/s). The numeric caption always
  states the true predicted values regardless of the stylized visual rate.
- STATIC (stand-plate + pinch-guard + reference-bearing): stationary,
  per `assembly-instructions.md` Sec 4.5's own "true system ground plane"
  framing -- unchanged position throughout.

Rotation is implemented via 2 Empty pivots (`PlatformPivot`/`WheelPivot`)
positioned at the real rotation axis (`fw_cx`,`fw_cy` = (53.5, 52.5) --
the flywheel bay's own rotation-axis center, same value
`bench-imu-01-enclosure.scad` uses throughout), with each relevant mesh
parented to its pivot via "keep transform" (`matrix_parent_inverse`, so
parenting does not visually move any mesh -- Blender does not do this
automatically on a plain `obj.parent = x` assignment). All rotation
keyframes use LINEAR interpolation (not the default BEZIER) so each
stated "hold" segment is an EXACTLY constant angular rate matching the
caption, not an eased approximation.

## Regeneration steps (full pipeline, from a clean checkout)

1. Export the 8 assembled-position STLs exactly as
   `../exploded/build_exploded_view.py`'s own docstring documents (same
   command, same STL_DIR convention).
2. Edit STL_DIR/OUTPUT paths below, run this script inside Blender
   (Scripting tab, `blender --background --python ...`, or a Blender MCP
   `execute_blender_code` call) to build the scene + keyframe the
   animation, then call `render_frame_sequence()` (chunked -- see
   `../animation/build_assembly_animation.py`'s own "Key lessons learned"
   for why PNG-sequence-then-ffmpeg beats Blender's own FFMPEG muxer when
   driving Blender via a tool with a practical per-call time budget).
3. Run `annotate_physics_demo_frames.py` (Pillow post-process, this same
   directory) to add the SIMULATION watermark, per-stage numeric captions,
   and the title/outro cards, and to assemble the final numbered frame
   sequence.
4. Encode with `ffmpeg` (same 2-pass MP4 + palette-GIF technique as
   `../animation/build_assembly_animation.py`'s own header).
"""

import math

import bpy
import mathutils

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
STL_DIR = "/tmp/bench-exploded-stl"
FRAMES_DIR = "/tmp/physics-demo-frames/raw"
FPS = 24
RESOLUTION = (1280, 960)

FW_CX, FW_CY = 53.5, 52.5  # bench-imu-01-enclosure.scad: fw_cx/fw_cy, the real rotation axis

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

# --- Real physics (verbatim from bom/component-selection.md's own
# "Platform angular-rate physics finding" -- an approved ESTIMATE, not
# re-derived here) ----------------------------------------------------------
I_WHEEL = 4.5e-5     # kg*m^2
I_PLATFORM = 6.9e-4   # kg*m^2
RATIO = I_WHEEL / I_PLATFORM  # ~0.06522, ~1:15

def rpm_to_rads(rpm):
    return rpm * 2 * math.pi / 60.0

OMEGA_WHEEL_1 = rpm_to_rads(30)     # Stage 1: 30 RPM
OMEGA_PLATFORM_1 = RATIO * OMEGA_WHEEL_1
OMEGA_WHEEL_2 = rpm_to_rads(300)    # Stage 2: 300 RPM
OMEGA_PLATFORM_2 = RATIO * OMEGA_WHEEL_2

# Stylized (disclosed, NOT to true angular-rate scale) Stage-2 wheel visual
# rate -- true 1800 deg/s would alias badly at this project's 24fps
# convention (confirmed by an intermediate render this task). Stage 1's
# wheel (180 deg/s) needed no stylization -- rendered at its true rate.
WHEEL_VISUAL_RATE_2 = math.radians(720)

# --- Timeline (seconds -> frames @ FPS=24) ---------------------------------
def f(t_seconds):
    return 1 + round(t_seconds * FPS)

T_STAGE1_START, T_STAGE1_END = 0.0, 4.0
T_PAUSE_END = 5.0
T_STAGE2_START, T_STAGE2_END = 5.0, 9.0
T_OUTRO_END = 12.0

FRAME_STAGE1_START = f(T_STAGE1_START)
FRAME_STAGE1_END = f(T_STAGE1_END)
FRAME_PAUSE_END = f(T_PAUSE_END)
FRAME_STAGE2_START = f(T_STAGE2_START)
FRAME_STAGE2_END = f(T_STAGE2_END)
FRAME_OUTRO_END = f(T_OUTRO_END)

# Exported for the annotation post-process script (stage boundaries + real
# numbers, so captions/frame ranges never drift out of sync with the
# keyframes actually inserted below).
TIMELINE = {
    "stage1_start": FRAME_STAGE1_START, "stage1_end": FRAME_STAGE1_END,
    "pause_end": FRAME_PAUSE_END,
    "stage2_start": FRAME_STAGE2_START, "stage2_end": FRAME_STAGE2_END,
    "outro_end": FRAME_OUTRO_END,
    "omega_wheel_1": OMEGA_WHEEL_1, "omega_platform_1": OMEGA_PLATFORM_1,
    "omega_wheel_2": OMEGA_WHEEL_2, "omega_platform_2": OMEGA_PLATFORM_2,
    "ratio": RATIO,
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


def linearize(obj):
    for fc in get_fcurves(obj):
        fc.extrapolation = 'CONSTANT'
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'


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

    # All parts at TRUE assembled positions -- no explode offsets (this is
    # a physics demo of the real device, not an assembly-order visual).
    bpy.context.view_layer.update()

    # Pivots at the real rotation axis (FW_CX, FW_CY); Z arbitrary (rotation
    # about Z doesn't depend on the pivot's own Z position).
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

    # --- Keyframe rotation ---------------------------------------------
    # PLATFORM: negative direction (reaction, opposite the wheel).
    ang = 0.0
    keyframe_rot_z(platform_pivot, FRAME_STAGE1_START, ang)
    ang -= OMEGA_PLATFORM_1 * (T_STAGE1_END - T_STAGE1_START)
    keyframe_rot_z(platform_pivot, FRAME_STAGE1_END, ang)
    keyframe_rot_z(platform_pivot, FRAME_PAUSE_END, ang)  # 1s hold/pause
    ang -= OMEGA_PLATFORM_2 * (T_STAGE2_END - T_STAGE2_START)
    keyframe_rot_z(platform_pivot, FRAME_STAGE2_END, ang)
    keyframe_rot_z(platform_pivot, FRAME_OUTRO_END, ang)  # final hold
    linearize(platform_pivot)

    # WHEEL: positive direction. Stage 1 true rate, Stage 2 stylized rate
    # (see module docstring).
    ang = 0.0
    keyframe_rot_z(wheel_pivot, FRAME_STAGE1_START, ang)
    ang += OMEGA_WHEEL_1 * (T_STAGE1_END - T_STAGE1_START)
    keyframe_rot_z(wheel_pivot, FRAME_STAGE1_END, ang)
    keyframe_rot_z(wheel_pivot, FRAME_PAUSE_END, ang)  # 1s hold/pause
    ang += WHEEL_VISUAL_RATE_2 * (T_STAGE2_END - T_STAGE2_START)
    keyframe_rot_z(wheel_pivot, FRAME_STAGE2_END, ang)
    keyframe_rot_z(wheel_pivot, FRAME_OUTRO_END, ang)  # final hold
    linearize(wheel_pivot)

    # --- Ground plane + fixed reference tick (visual aid only) ---------
    bpy.ops.mesh.primitive_plane_add(size=400, location=(FW_CX, FW_CY, -14))
    ground = bpy.context.active_object
    ground.name = "GroundPlane"
    ground.data.materials.append(make_mat("mat_ground", (0.78, 0.78, 0.80), roughness=0.8))

    # A thin fixed vertical post, NOT a physical part -- purely a "12
    # o'clock" visual reference landmark placed OUTSIDE the device's own
    # footprint (radius 130mm > pinch_guard's own 115mm max radius) so
    # rotation is easy to judge against a stationary landmark without any
    # risk of being occluded by (or occluding) real geometry. A first
    # attempt at this (a thin radial cylinder lying flat near the ground)
    # was confirmed, via an intermediate render this task, to be nearly
    # buried by the ground plane and/or hidden under the stationary
    # pinch-guard ring -- fixed by standing it upright, clear of every
    # other object, instead (mirrors this project's own "verify, don't
    # eyeball" convention for the exploded view's own ground-plane bug).
    bpy.ops.mesh.primitive_cylinder_add(
        radius=1.8, depth=22, location=(FW_CX, FW_CY + 130, -14 + 11))
    tick = bpy.context.active_object
    tick.name = "FixedReferenceTick"
    tick.data.materials.append(make_mat("mat_tick", (0.85, 0.15, 0.15), roughness=0.6))

    # --- Camera: mostly top-down (rotation is the whole point), slight tilt
    cam_data = bpy.data.cameras.new("PhysicsCam")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 300
    cam_obj = bpy.data.objects.new("PhysicsCam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    cam_dir = mathutils.Vector((0.35, -0.35, 1.15)).normalized()
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
    scene.frame_start = FRAME_STAGE1_START
    scene.frame_end = FRAME_OUTRO_END
    scene.frame_current = FRAME_STAGE1_START

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


if __name__ == "__main__":
    build_scene()
    render_frame_sequence()
    print("Done. Now run annotate_physics_demo_frames.py, then encode with ffmpeg.")
