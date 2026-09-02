#!/usr/bin/env python3
"""
Bench-IMU-01 -- Exploded Assembly View generator (Blender Python API).

Regenerates `bench-imu-01-exploded-view.png` from the 8 assembled-position
STLs produced by the wrapper scripts in `../scad/assembled-*.scad`. Written
against Blender 5.1 (bpy.ops.wm.stl_import); run inside Blender via its
Scripting tab, `blender --background --python build_exploded_view.py`, or
paste into a Blender MCP `execute_blender_code` call.

Does NOT touch bench-imu-01-enclosure.scad or any other source geometry --
purely a downstream visualization step, per this project's own read-only
convention for generated artifacts.

**Revision note**: the motor (M1) + flywheel reference ghosts
(`assembled-reference-motor-body`/`assembled-reference-flywheel-rotor`, 2 of
the 8 parts below) are NEW as of this pass. An earlier revision of this
script/README deliberately left them out ("judged to add clutter"); that
call is reversed here now that the omission was flagged as inconsistent with
the bearing (also a bought/non-printed part) already being shown as a
reference ghost, and with `assembly-instructions.md` §4.2/§4.4 documenting
mounting them as real build steps. See `../README.md`'s exploded-view
section for the full disclosure.

## Regeneration steps (full pipeline, from a clean checkout)

1. Export the 8 assembled-position STLs (one per real printed piece, plus the
   bearing/motor-body/flywheel-rotor reference ghosts) -- NOT the print-ready
   STLs in `hardware/mechanical/stl/`, which use a different, print-bed-
   convenience orientation:

   cd hardware/mechanical/drawings/scad
   for f in assembled-base-assembly assembled-pcb-lid assembled-containment-cap \
            assembled-stand-plate assembled-pinch-guard assembled-reference-bearing \
            assembled-reference-motor-body assembled-reference-flywheel-rotor; do
     openscad -D 'show_mode="export"' --backend=manifold --export-format binstl \
       -o /tmp/$f.stl $f.scad
   done

2. Edit STL_DIR below to point at wherever you exported them (e.g. /tmp).

3. Run this script inside Blender (see options above).

## Key lessons learned building this (so the next person doesn't re-discover
## them the hard way):

- Each wrapper script's module call(s) already match the parent .scad file's
  own `show_mode == "assembled"` branch exactly (see each wrapper's own
  header comment) -- the STL's mesh vertices already encode the real,
  correct assembled-frame world position. No manual repositioning is
  needed or should be applied to the imported meshes themselves.
- A flat "ground plane" reference object, if you add one, MUST be moved
  below the true lowest Z of the EXPLODED (not just assembled) scene. It is
  very easy to bury the bottom-most exploded pieces (stand_plate,
  pinch_guard) underneath an opaque ground plane that was only sized for
  the pre-explode assembly -- this was the single biggest bug hunted down
  while building this script (parts existed and were positioned correctly,
  but were invisible, hidden behind the ground plane from any elevated
  camera angle).
- For an orthographic camera, a lateral (XY) stagger between exploded
  groups is only visually useful if it has a component PERPENDICULAR to
  the camera's own azimuth direction -- an offset parallel to the view
  direction is invisible (it just changes depth/occlusion order, not
  screen position). This script's offsets are deliberately chosen
  perpendicular to CAM_DIRECTION's own (X,Y) component.
- Prefer a real `bpy.ops.render.render(write_still=True)` over
  `get_viewport_screenshot` for anything where the camera/view state was
  just changed by script -- the interactive viewport does not reliably
  reflect script-driven view changes without extra redraw handling, while
  a real render always uses the current scene/camera state directly.
"""

import bpy
import mathutils

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
STL_DIR = "/tmp"  # <-- point this at your exported assembled-position STLs
OUTPUT_PATH = None  # set to an absolute path, or leave None to just render in-memory

PARTS = [
    "assembled-base-assembly",
    "assembled-pcb-lid",
    "assembled-containment-cap",
    "assembled-stand-plate",
    "assembled-pinch-guard",
    "assembled-reference-bearing",
    # NEW this pass: motor (M1) + flywheel, previously omitted entirely (see
    # this pass's own commit message / drawings/README.md for the honest
    # "why re-added now" disclosure). Split into the stationary motor-body
    # (bolted to the platform, moves WITH assembled-base-assembly/pcb-lid/
    # containment-cap in the physics-demo animation) and the rotating
    # shaft+hub+flywheel-disk group, mirroring
    # `assembled-reference-motor-body.scad`/`assembled-reference-flywheel-
    # rotor.scad`'s own header comments for the stator/rotor split rationale.
    "assembled-reference-motor-body",
    "assembled-reference-flywheel-rotor",
]

# Distinct per-part colors -- doubles as an implicit legend (also drawn as a
# real legend strip in the final PNG via a separate PIL post-process step,
# not part of this script).
COLOR_MAP = {
    "assembled-base-assembly":    (0.35, 0.55, 0.80),  # blue
    "assembled-pcb-lid":          (0.45, 0.75, 0.45),  # green
    "assembled-containment-cap":  (0.90, 0.55, 0.20),  # orange
    "assembled-stand-plate":      (0.55, 0.55, 0.58),  # neutral gray
    "assembled-pinch-guard":      (0.80, 0.25, 0.30),  # red
}
BEARING_COLOR = (0.75, 0.76, 0.78)  # silver, translucent (reference only)

# Reference-only ("bought part, not printed") ghost colors -- same
# translucent/metallic treatment convention as BEARING_COLOR above, so these
# read visually as "reference," not as one of the 5 printed pieces.
REFERENCE_GHOST_COLORS = {
    "assembled-reference-motor-body":     (0.22, 0.23, 0.27),  # charcoal (motor can)
    "assembled-reference-flywheel-rotor": (0.62, 0.18, 0.68),  # purple/magenta (flywheel
    # mass) -- deliberately NOT gold/orange, which visually collided with
    # assembled-containment-cap's own orange in an intermediate render this
    # pass (confirmed, not assumed) and could be mistaken for it.
}

# Explode offsets -- ARTIFICIAL visualization distances chosen purely to
# separate pieces clearly; NOT real assembly clearances. Primarily along Z
# (matching the .scad file's own real Z-stack order), with a lateral (X,Y)
# stagger perpendicular to CAM_DIRECTION's own azimuth so pieces read as
# clearly separated from an isometric angle, not just occluding each other.
#
# The 2 new motor/flywheel ghosts needed a LARGER offset than a naive
# Z-stack interpolation would suggest: they start out physically INSIDE
# `fw_bay_wall()`, a cylindrical wall of `base()` (unmoved, radius up to
# ~43.5mm around fw_cx/fw_cy) reaching up to `fw_wall_h`=43.0mm -- a small
# offset leaves them still visually trapped inside that wall's silhouette
# from every camera angle tried (confirmed by an intermediate render pass
# during this task, not assumed). Fixed with a large, mostly-+X offset:
# +X decomposes into a mix of both perpendicular-to-camera screen shift
# AND a toward-camera depth component (CAM_DIRECTION's own (X,-Y) azimuth),
# clearing the wall radius in both screen position and depth ordering, plus
# enough +Z to clear the wall's own 43mm rim height.
OFFSETS = {
    "assembled-pinch-guard":       (-45, -45, -35),
    "assembled-stand-plate":       (-25, -25, -22),
    "assembled-reference-bearing": (-16, -16, -18),
    "assembled-base-assembly":     (0, 0, 0),      # anchor, unmoved
    "assembled-reference-motor-body":     (65, 15, 24),
    "assembled-reference-flywheel-rotor": (95, 25, 38),
    "assembled-pcb-lid":           (12, 12, 22),
    "assembled-containment-cap":   (25, 25, 38),
}

CAM_DIRECTION = mathutils.Vector((1.0, -1.0, 0.4)).normalized()
CAM_DISTANCE = 700
ORTHO_MARGIN = 0.95  # ortho_scale = bbox_diagonal * ORTHO_MARGIN (< 1 = tighter crop)


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


def world_bbox(objs):
    pts = []
    for o in objs:
        for c in o.bound_box:
            pts.append(o.matrix_world @ mathutils.Vector(c))
    xs = [v.x for v in pts]; ys = [v.y for v in pts]; zs = [v.z for v in pts]
    bmin = mathutils.Vector((min(xs), min(ys), min(zs)))
    bmax = mathutils.Vector((max(xs), max(ys), max(zs)))
    return bmin, bmax


def main():
    # Clear any pre-existing mesh/light objects (start from a clean slate;
    # keeps whatever camera setup already exists if re-run interactively).
    for obj in list(bpy.data.objects):
        if obj.type in ('MESH', 'LIGHT'):
            bpy.data.objects.remove(obj, do_unlink=True)

    imported = {}
    for p in PARTS:
        path = f"{STL_DIR}/{p}.stl"
        before = set(bpy.data.objects.keys())
        bpy.ops.wm.stl_import(filepath=path, forward_axis='Y', up_axis='Z')
        after = set(bpy.data.objects.keys())
        new_name = list(after - before)[0]
        obj = bpy.data.objects[new_name]
        obj.name = p
        imported[p] = obj

    # Materials
    for name, color in COLOR_MAP.items():
        obj = imported[name]
        mat = make_mat(f"mat_{name}", color)
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    bearing = imported["assembled-reference-bearing"]
    mat_bearing = make_mat("mat_bearing", BEARING_COLOR, metallic=0.9, roughness=0.2, alpha=0.75)
    bearing.data.materials.clear()
    bearing.data.materials.append(mat_bearing)
    # Reference-only ghosts (motor body + flywheel rotor) -- same
    # translucent/metallic "bought part, not printed" treatment as the
    # bearing above, so all 3 read visually as reference geometry.
    for name, color in REFERENCE_GHOST_COLORS.items():
        obj = imported[name]
        mat = make_mat(f"mat_{name}", color, metallic=0.7, roughness=0.35, alpha=0.85)
        obj.data.materials.clear()
        obj.data.materials.append(mat)

    # Apply explode offsets (absolute location -- these objects have no other
    # transform applied, since STL import keeps world coords in mesh data).
    for name, (x, y, z) in OFFSETS.items():
        imported[name].location = (x, y, z)
    bpy.context.view_layer.update()

    # Ground plane -- sized and positioned AFTER the explode, safely below
    # the true lowest exploded point (see "Key lessons learned" above).
    bmin, bmax = world_bbox(imported.values())
    ground_z = bmin.z - 5
    bpy.ops.mesh.primitive_plane_add(size=600, location=((bmin.x + bmax.x) / 2, (bmin.y + bmax.y) / 2, ground_z))
    ground = bpy.context.active_object
    ground.name = "GroundPlane"
    ground.data.materials.append(make_mat("mat_ground", (0.75, 0.75, 0.76), roughness=0.8))

    # Camera (orthographic), framed from the real exploded bounding box.
    center = (bmin + bmax) / 2
    size = bmax - bmin
    cam_data = bpy.data.cameras.new("ExplodedCam")
    cam_data.type = 'ORTHO'
    cam_obj = bpy.data.objects.new("ExplodedCam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    cam_obj.location = center + CAM_DIRECTION * CAM_DISTANCE
    cam_data.clip_start = 0.1
    cam_data.clip_end = 3000
    cam_data.ortho_scale = size.length * ORTHO_MARGIN
    target = bpy.data.objects.new("AimTarget", None)
    target.location = center
    bpy.context.scene.collection.objects.link(target)
    con = cam_obj.constraints.new('TRACK_TO')
    con.target = target
    con.track_axis = 'TRACK_NEGATIVE_Z'
    con.up_axis = 'UP_Y'
    bpy.context.scene.camera = cam_obj

    # Lighting
    key = bpy.data.lights.new("KeySun", type='SUN'); key.energy = 4.0
    key_obj = bpy.data.objects.new("KeySun", key); key_obj.rotation_euler = (0.9, 0.2, 0.7)
    bpy.context.scene.collection.objects.link(key_obj)
    fill = bpy.data.lights.new("FillSun", type='SUN'); fill.energy = 1.0
    fill_obj = bpy.data.objects.new("FillSun", fill); fill_obj.rotation_euler = (1.3, -0.3, -2.2)
    bpy.context.scene.collection.objects.link(fill_obj)
    rim = bpy.data.lights.new("RimSun", type='SUN'); rim.energy = 1.2
    rim_obj = bpy.data.objects.new("RimSun", rim); rim_obj.rotation_euler = (2.0, 0.3, 2.6)
    bpy.context.scene.collection.objects.link(rim_obj)

    world = bpy.context.scene.world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.56, 0.58, 1)

    scene = bpy.context.scene
    scene.view_settings.view_transform = 'Standard'
    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError:
        scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 2000
    scene.render.resolution_y = 1500
    scene.render.resolution_percentage = 100

    if OUTPUT_PATH:
        scene.render.filepath = OUTPUT_PATH
        bpy.ops.render.render(write_still=True)
        print("Rendered to", OUTPUT_PATH)
    else:
        print("Scene built. Set OUTPUT_PATH and re-run render, or render manually.")


if __name__ == "__main__":
    main()
