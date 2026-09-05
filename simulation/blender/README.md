# Blender companion — computed-state replay

This optional path uses **Blender 5.1.1 / Cycles CPU or Workbench** to render the same
recorded MuJoCo poses. It is **not an independent Blender/Bullet physics
simulation**, physical CAD, hardware approval, or Fusion assembly animation.
The source trajectory is never changed to produce a successful-looking motion.

The live Blender application's existing unsaved scene is not reset or saved.
Author and reopen the native file in an isolated background process first.
Only append the resulting named replay scene to the live application when
the user requests viewing it; retain every existing scene and object.

From the repository root, using the Blender binary found by runtime preflight:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --threads 4 --python-exit-code 1 \
  --python simulation/blender/render_replay.py -- \
  --run simulation/evidence/startup-v3/startup-mechanism-fixture \
  --output simulation/runs/my-blender-replay --engine workbench --animation

/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup simulation/runs/my-blender-replay/replay.blend \
  --threads 4 --python-exit-code 1 --python simulation/blender/check_replay.py -- \
  --run simulation/evidence/startup-v3/startup-mechanism-fixture \
  --output simulation/runs/my-blender-replay/native-check.json

simulation/.venv/bin/python simulation/blender/encode_replay.py \
  --run simulation/evidence/startup-v3/startup-mechanism-fixture \
  --render simulation/runs/my-blender-replay
```

Open `replay.blend` in Blender or play `blender-motion.mp4`. `preview.png`,
`provenance.json`, `native-check.json` and `manifest.json` bind the source
records, scripts, native file, frame mapping and output hashes.
Raw `frames/` images are regenerable render intermediates, not separate
physics evidence. Keep them local rather than adding them to the PR.
New published clips require at least ten seconds of recorded motion.
Workbench is a lightweight display renderer, not a different physics engine.
The earlier three-second Cycles comparison is historical, not the current
duration-compliant deliverable. Model identity, size and mathematical mass
are labeled so the small synthetic annular fixture is not mistaken for Rev5.

Blender frame 1 corresponds to recorded time 0. Every integer rendered
frame copies the source video map's exact pose; intermediate keyframe
interpolation is not physics evidence. The reopening check compares all
rendered body/wheel poses at a 1e-6 positional/quaternion-component margin
for Blender float32 display precision, not physical qualification.
Wheel markers may alias at video frame rate; the original CSV holds speed.
Display edges and cylinders are mass-free visual proxies, not a new
mechanical assembly source of truth.

Official APIs used: [render operators](https://docs.blender.org/api/5.1/bpy.ops.render.html),
[native libraries](https://docs.blender.org/api/5.1/bpy.types.BlendDataLibraries.html),
[object transforms](https://docs.blender.org/api/5.1/bpy.types.Object.html).
The existing repository's Blender 5 layered F-curve traversal convention is
reused. Material/world `use_nodes` remain supported in 5.1 but issue a
scheduled-removal warning for Blender 6; recheck that API before migrating.
