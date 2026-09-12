# Cube rigid-body simulator — WIP

[English](simulator.md) | [日本語](../simulation/README.md) | [Guide index](README.md)

English reading edition of the existing [Japanese run guide](../simulation/README.md).
This uses MuJoCo to compute a free rigid cube, floor contact and three
independent reaction wheels. **It is not physical feasibility, safety or
Design Complete approval.** The controller is simulation-only; this is not
Fusion assembly-process animation.

For the ten-second startup trials, see [spin-up and finite braking](startup.md).
The recorded index is `simulation/evidence/startup-v4/index.html`.
The synthetic mechanism and incomplete design proxy are separate cases;
XYZ reactions come from internal braking and floor contact. Blender replay
and CERN ROOT exchange have separate roles.

The [earlier review](../simulation/reviews/r2b/review.md) covers its named
version. The public source records a bounded independent recheck of
`7192a73f7f93534e246ccbc6aafac76985e7fb3c`
([closure record](https://github.com/ktanino10/ai-hardware-engineering-team/pull/70#issuecomment-5555340145))
after marker-transform, mesh, effective-FPS and source-binding fixes.
That is not physical feasibility, established airborne jumping, sustained
balance or Fusion acceptance. The recorded Blender package is
`simulation/evidence/blender-replay-v7/startup-mechanism-fixture/`.

## Local execution

From the repository root, with Python 3.14 and ffmpeg available. Install
the pinned dependencies only into this directory's virtual environment.

```sh
python3 -m venv simulation/.venv
simulation/.venv/bin/python -m pip install -r simulation/requirements-lock.txt
cd simulation
.venv/bin/python -m cube_sim preflight
.venv/bin/python -m cube_sim run --scenario three-wheel --output runs/my-three-wheel --video
```

Open `runs/my-three-wheel/motion.mp4`, `plots.png` and `trajectory.csv`.
Use a new output name every time; never overwrite evidence.
`trajectory.npz` stores states, `model.xml` is the executed MJCF model, and
`input.json`, `scenario.json`, `manifest.json` bind inputs, versions and hashes.

On macOS use MuJoCo's `mjpython`, not ordinary Python, for native replay:

```sh
.venv/bin/mjpython -m cube_sim replay runs/my-three-wheel
# On Linux use .venv/bin/python instead of mjpython.
.venv/bin/python -m unittest discover -s tests -v
```

Replay shows recorded states, not real-time control or a hardware connection.
White wheel markers retain computed angles, so sampling may make fast
rotation look stationary or reversed. Read speed from the plots/CSV.

## Run and view a suite

Regenerate both models across seven scenarios with videos, plots and
numerical sensitivity results. `--allow-proxy` acknowledges incomplete
design and assumed actuation/contact; it is not physical permission.

```sh
# From simulation/; use an output directory that does not exist.
.venv/bin/python -m cube_sim suite --allow-proxy --output runs/my-suite
.venv/bin/python -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/runs/my-suite/index.html`.
The historical short recordings are at
`http://127.0.0.1:8765/evidence/initial-v1/index.html`.
Stop the server with Ctrl+C. This local evidence viewer does not upload
designs to a CDN or cloud.

## Frozen Rev5 intake

`simulation/intake/rev5-v1.json` contains the already-published numerical
extract and hashes for frozen WIP source
`3633eb5d03d6db7c90b582e53180414087b33519`.
The original guide records checks of the 21-file package's hashes/sizes
and mass/CG/inertia extract. That commit is not main or a completed product.
This reading edition uses only the public extract; it neither retrieves
that branch nor duplicates or modifies its CAD.

`models/rev5-proxy.json` is deterministically derived by
`cube_sim.intake.derive_proxy()`. The input **3.06427779784 kg already includes
three rotors**. Mass, first moment and inertia are subtracted about one
origin to obtain about 2.76427779784 kg of chassis, then three 0.1 kg rotors
are restored as separate DOFs. An independent addition of printed parts,
whole-motor surrogates and bare board is compared. This does not make the
input complete: unknown rotor/stator splitting is not invented; whole
motor surrogates are explicitly fixed to the chassis.

```sh
# From simulation/.
.venv/bin/python -m cube_sim run --config models/rev5-proxy.json --allow-proxy \
  --scenario vertex-balance --output runs/my-proxy-vertex --video
.venv/bin/python -m cube_sim derive-proxy --output runs/rederived-proxy.json
```

Actual total mass/CG, battery, populated boards, hubs, wiring, retention,
motor torque/speed/current curves, DRV10983 braking and floor properties
remain unknown. A faithful actual-driver model is not available.
The proxy explicitly uses the reference case's ideal torque/contact
assumptions; it is not tuned to succeed and 3000 rpm is not a safety limit.
Earlier fixed-edge momentum insufficiency is not a proof that every
possible trajectory is impossible.

## Initial model boundaries

`models/reference.json` is `SYNTHETIC_REFERENCE`: uniform-cube-equivalent
1 kg chassis inertia plus three 100 g cylinder rotors, total 1.3 kg.
The chassis mass excludes the rotors. This is not actual hardware weight.
Units are SI; world Z is up; body centre is the local origin; rotor axes
are body +X/+Y/+Z. Quaternion order is `w,x,y,z`, rotating body to world.
Soft box/plane contact, friction and stiffness are uncalibrated assumptions.

The initial integrator is 2 ms RK4. The public guide records
timestep-proportional free-space linear momentum error with implicitfast,
reduced to about 6×10^-16 kg m/s with RK4 in that comparison.
This is numerical evidence, not measured contact calibration.
Motors are `motor joint=... gear=1` on chassis/rotor hinges, not external
body torques, fixed pivots or pose correction. Reverse torque is ideal
bidirectional actuation, not DRV10983 BRAKE. Speed cutoff removes outward
effort, not velocity, and does not guarantee a physical RPM bound.
Body linear velocity is world-frame; angular velocity is body-frame.
Relative wheel speed is hinge `qvel`; absolute axial speed adds the
corresponding body angular-rate component.

Scenarios: `rest`, `fall`, `one-wheel`, `three-wheel`, `edge-balance`,
`vertex-balance`, `face-to-vertex-attempt`.
Edge/vertex trials are pre-positioned. Falling, slipping and saturation
are valid outcomes; they are not hidden to manufacture success.
A complete face-to-edge-to-vertex transition has not been demonstrated.

## Evidence and interpretation

`verify` checks current code/model/intake bindings as well as output hashes.
Use `--historical` only to inspect old results as historical records.
Changed inputs/code need a newly named run and independent Simulation
Reviewer assessment. Do not overwrite old evidence with a new renderer.

```sh
# From simulation/.
.venv/bin/python -m cube_sim verify evidence/initial-v1/reference/three-wheel --historical
.venv/bin/python -m cube_sim witnesses --output runs/my-numerics.json
```

CSV/plots are 100 Hz; 25 fps video uses exact recorded rows.
`video-frames.csv` binds timestamps and state hashes. Contact count,
normal force, penetration, slip, saturation and overspeed are recorded,
but do not bound between-sample impact peaks.
Rigid potential/kinetic energy is compared with motor/passive/constraint
work using stage-consistent RK4 work integration. The initial endpoint
trapezoid issue, correction and residuals are described in [startup](startup.md).
Do not require energy conservation in dissipative contact or interpret
constraint work as brake heat or structural strength.

The [simulation contract](simulation.md) defines units, tolerances and
responsibilities. Step/solver comparisons are model sensitivity, not
experimental identification. Failed short balance/transition trials cannot
establish universal physical impossibility.

## References

- [MuJoCo passive viewer](https://mujoco.readthedocs.io/en/stable/python.html#passive-viewer)
- [Actuation and transmission](https://mujoco.readthedocs.io/en/stable/computation/index.html#actuation-model)
- [Explicit inertial tensors](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-inertial)
- [No inertia inference from render geometry](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-inertiafromgeom)
- [Soft contact and friction](https://mujoco.readthedocs.io/en/stable/computation/index.html#soft-contact-model)
- [Subtree angular momentum](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreeangmom)

The source guide's API verification date is 2026-09-05, not a check performed
by this translation. Older `hardware/mechanical/drawings/physics-demo/`
prescribes Blender motion and `concept-demo/` uses idealized keyframes;
neither is reused as the current three-axis dynamics trajectory.
