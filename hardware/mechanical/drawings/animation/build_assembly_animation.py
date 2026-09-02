#!/usr/bin/env python3
"""
Bench-IMU-01 -- Assembly Animation generator (Blender Python API).

Extends `../exploded/build_exploded_view.py`'s scene (same 6 parts, same
materials/camera/lighting/ground-plane) with keyframed animation: each part
moves from its EXPLODED position back to its true ASSEMBLED position
(location (0,0,0) -- see that script's own header for why), staggered
across 4 stages that follow the real build order documented in
`../../assembly-instructions.md`, not an arbitrary order. Renders a PNG
frame sequence, then hands off to `ffmpeg` (confirmed installed this
session, v8.1, libx264) to encode an MP4 and a palette-optimized GIF.

Written against Blender 5.1. Run inside Blender via its Scripting tab,
`blender --background --python build_assembly_animation.py`, or paste into
a Blender MCP `execute_blender_code` call, **after** first running
`build_exploded_view.py` (or otherwise ensuring the same 6 named objects
already exist in the scene at their exploded positions).

## Regeneration steps (full pipeline)

1. Run `../exploded/build_exploded_view.py` first (imports the 6 STLs,
   sets materials/camera/lighting/ground plane, applies the static explode
   offsets) -- this script assumes that scene already exists.
2. Edit `FRAMES_DIR` below.
3. Run this script inside Blender. It keyframes the animation and renders
   the full PNG frame sequence to `FRAMES_DIR` (chunked internally is NOT
   done by this script -- see "Chunking" below if running via an MCP tool
   call with a practical per-call time budget).
4. Encode to MP4 + GIF:

   ffmpeg -y -framerate 24 -i "$FRAMES_DIR/f_%04d.png" \
     -c:v libx264 -pix_fmt yuv420p -crf 20 -movflags +faststart \
     bench-imu-01-assembly-animation.mp4

   ffmpeg -y -framerate 24 -i "$FRAMES_DIR/f_%04d.png" \
     -vf "fps=12,scale=640:-1:flags=lanczos,palettegen=stats_mode=diff" \
     /tmp/anim-palette.png
   ffmpeg -y -framerate 24 -i "$FRAMES_DIR/f_%04d.png" -i /tmp/anim-palette.png \
     -filter_complex "fps=12,scale=640:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3" \
     -loop 0 bench-imu-01-assembly-animation.gif

## Key lessons learned building this (so the next person doesn't
## re-discover them the hard way)

- **Blender 5.x's Action data model changed** (the 4.4+ "layered
  animation" system) -- `obj.animation_data.action.fcurves` no longer
  exists. The correct path is:
  `action.layers[0].strips[0].channelbags[i].fcurves` (a strip can have
  multiple channelbags, one per animation "slot"; for a single object with
  its own dedicated action, there is normally exactly one channelbag with
  all of that object's F-curves in it). See `get_fcurves()` below.
- **Render `bpy.ops.render.render(animation=True)` in chunks** if calling
  from a tool with a practical per-call time budget: at ~1.4s/frame (960x720,
  EEVEE, this scene's complexity), 180 frames is ~4 minutes in one shot --
  fine as a single local script run, but this project rendered it as 6
  chunks of 30 frames each (~41s/chunk) when driving Blender via MCP tool
  calls, by repeatedly setting `scene.frame_start`/`scene.frame_end` to a
  sub-range and calling `render(animation=True)` again -- Blender's PNG
  sequence output naturally supports this (each frame is an independent
  file), unlike trying to "resume" a single video/FFMPEG-muxed output
  across multiple calls.
- **Encode video with `ffmpeg` from the rendered PNG sequence, not
  Blender's own FFMPEG muxer**, specifically *because* of the chunking
  above -- Blender's `image_settings.file_format='FFMPEG'` output must be
  produced in one continuous `render(animation=True)` call (or it
  overwrites/restarts), which conflicts with chunked rendering. Rendering
  to PNG frames (resumable, chunkable) then a single `ffmpeg` encode pass
  over the complete sequence avoids that conflict entirely, and was
  confirmed to work identically well.
- **Extrapolation matters**: set each F-curve's `extrapolation = 'CONSTANT'`
  so a part correctly *holds* its exploded position before its stage
  starts, and holds its assembled position after its stage ends, rather
  than drifting linearly forever in either direction (Blender's default is
  already 'CONSTANT' for new curves, but this script sets it explicitly
  rather than relying on the default).
"""

import bpy

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
FRAMES_DIR = "/tmp/anim-frames"  # <-- point this wherever you want PNG frames written
FPS = 24
RESOLUTION = (960, 720)

# Real assembled-frame exploded offsets -- must match build_exploded_view.py's
# own OFFSETS exactly (this script reads each object's CURRENT location as
# the "exploded" starting point, so as long as build_exploded_view.py has
# already run and left the scene in its exploded state, this is automatic;
# the values are restated here only for documentation/clarity).
EXPLODED_POSITIONS = {
    "assembled-pinch-guard":       (-45, -45, -35),
    "assembled-stand-plate":       (-25, -25, -22),
    "assembled-reference-bearing": (-16, -16, -18),
    "assembled-pcb-lid":           (12, 12, 22),
    "assembled-containment-cap":   (25, 25, 38),
}

# Staggered arrival schedule (object, stage_start_frame, stage_end_frame) --
# direction is EXPLODED -> ASSEMBLED (parts fly together). Order follows the
# real build sequence in ../../assembly-instructions.md, not an arbitrary
# one: (1) PCB lid -- an early core-enclosure step (Sec 4.1); (2) containment
# cap -- the LAST core-enclosure step (Sec 4.4); (3) stand plate + pinch
# guard together -- the source document places these "at the same assembly
# step" as a parallel subassembly (Sec 4.5); (4) bearing last -- the final
# connecting piece, mirroring "mate the two halves" being the last step
# (Sec 4.6/4.7). `assembled-base-assembly` never moves -- it is the
# substrate/anchor everything else attaches to.
SCHEDULE = [
    ("assembled-pcb-lid",           15, 45),
    ("assembled-containment-cap",   55, 85),
    ("assembled-stand-plate",       95, 125),
    ("assembled-pinch-guard",       95, 125),
    ("assembled-reference-bearing", 135, 165),
]
FRAME_END_HOLD = 180  # final hold at fully-assembled through this frame


def get_fcurves(obj):
    """Blender 5.x layered-action F-curve access (see docstring above)."""
    action = obj.animation_data.action
    fcurves = []
    for layer in action.layers:
        for strip in layer.strips:
            for channelbag in strip.channelbags:
                fcurves.extend(channelbag.fcurves)
    return fcurves


def keyframe_location(obj, frame, loc):
    obj.location = loc
    obj.keyframe_insert(data_path="location", frame=frame)


def build_animation():
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = FRAME_END_HOLD
    scene.frame_current = 1

    for name, start_f, end_f in SCHEDULE:
        obj = bpy.data.objects[name]
        obj.animation_data_clear()
        exploded_loc = EXPLODED_POSITIONS[name]
        keyframe_location(obj, start_f, exploded_loc)
        keyframe_location(obj, end_f, (0, 0, 0))
        for fc in get_fcurves(obj):
            fc.extrapolation = 'CONSTANT'
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.easing = 'EASE_IN_OUT'

    bpy.context.view_layer.update()
    scene.frame_set(1)
    print(f"Animation keyframed: frames 1-{FRAME_END_HOLD} @ {FPS}fps")


def render_frame_sequence(frame_start=None, frame_end=None):
    """Render a PNG sequence. Call repeatedly with different (frame_start,
    frame_end) sub-ranges if chunking (see docstring). Omit both to render
    the full 1..FRAME_END_HOLD range in one call."""
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
    build_animation()
    render_frame_sequence()  # full range in one call; chunk manually if needed
    print("Done. Now encode with ffmpeg -- see this script's own module docstring.")
