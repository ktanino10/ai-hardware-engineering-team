# Spin-up and finite braking — ten-second trials

[English](startup.md) | [日本語](../simulation/STARTUP.md) | [Simulator](simulator.md)

English edition of the public [startup guide](../simulation/STARTUP.md).
That guide records a user-supplied
[attitude-control-study](https://github.com/ktanino10/attitude-control-study/tree/a927d1ae3409ba143631077824cdf3c904ea27b9)
as the context for separating **rest → stored wheel momentum → independent
braking → face-to-edge motion** from pre-positioned PD trials.
An ideal instantaneous lock/fixed pivot equation is not applied wholesale
to the freely contacting cube. This edition does not fetch additional sources.

## Run and view

```sh
cd simulation
.venv/bin/python -m cube_sim startup-suite --allow-proxy --output runs/my-startup-suite
.venv/bin/python -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/runs/my-startup-suite/index.html`; stop with Ctrl+C.
The published record is `simulation/evidence/startup-v4/index.html`.
Each normal movie integrates and displays **ten simulated seconds at real
time**, without repetition or still-frame padding. The separate
`brake-detail.mp4` is explicitly **100× slow motion**, showing 0.1 simulated
seconds over ten playback seconds. Both use the same recorded states.

| Case | Preserved inputs / explicit assumptions | Interpretation |
|---|---|---|
| `startup-reference` | Original 240 mm / 1.3 kg mathematical reference mass and inertia | Startup added to the original synthetic reference |
| `startup-rev5-proxy` | Frozen 240 mm / 3.06428 kg partial solid-CAD-equivalent mass and inertia | Incomplete design proxy; battery, full population and driver capacity unknown |
| `startup-mechanism-fixture` | Separate 100 mm / 0.34 kg synthetic model: 0.1 kg body, three 0.08 kg annuli, outer/inner radii 40/35 mm, thickness 4 mm, assumed friction 1.2 | Mathematical mechanism example, not Rev5, an article replica, or adopted parts/material |

Annular inertia is `Iaxis=m(Ro²+Ri²)/2`,
`Itransverse=Iaxis/2+mh²/12`. This is a separate case, not an undisclosed
increase to actual-proxy inertia.
Face separation, visiting an edge, all corners leaving the floor and
sustained inverted balance are different events.
Candidate gaps require no geometric contact, normal force ≤1e-8 N and
all corners >0.1 mm; contiguous sampled intervals/durations are recorded.
Approximately 0.18 mm is labeled **numerically unresolved** relative to
contact/geometry uncertainty, not established airborne jumping.
Sampling does not prove every intervening instant; step/solver/envelope
sensitivity needs independent review. Capture control and a second
vertex-directed jump are not implemented.

## Change real model inputs, not recorded poses

`simulation/models/startup-*.json` are reproducible input files.
Compare a copy with a new case name; do not rewrite frozen evidence or
physical source-of-truth files. The current synthetic input is
`startup-mechanism-fixture-v2.json`. R2 corrected provenance wording only,
not physics/control parameters. Its reference file is a software template,
not inherited mass/shape/floor-friction data for the small fixture.

| Input | Meaning |
|---|---|
| `scenario.startup.target_rad_s` | Signed XYZ wheel targets; zero axes are not driven |
| `actuation.torque_limit_nm` | Per-axis ideal motor limit |
| `actuation.independent_brake.capacity_nm` | Per-axis independent brake capacity |
| `scenario.startup.engagement_delay_s` / `ramp_s` | Assumed command delay / capacity ramp |
| `contact.sliding_friction` | Uncalibrated floor friction; variations remain assumptions |

**No direct upward force or XYZ impulse is applied to the cube.**
Motor action is internal hinge torque; braking is finite dry-friction
constraint on the same hinge. Floor reactions/impulses are computed
results. No speed reset, fixed pivot or pose correction manufactures motion.

3000 rpm is an old analytical **target only**, not rated/safe RPM.
The standard program commands spin until 3 s, commands braking at 3.5 s,
then ramps capacity over 1 ms after an assumed 20 ms delay.
`Iaxis*target_omega/5 ms` is a hypothetical comparison capacity, not an
enforced five-millisecond stop. Actual model stopping time uses relative
speed <1 rad/s. This does not verify DRV10983 BRAKE, current, restart,
regeneration, holding or latency.

## Work, momentum, step size and output grid

R1's `SIM-R1-001` identified endpoint-trapezoid work accounting inconsistent
with RK4 stages. Current diagnostics record the four real states read-only,
reevaluate forces in separate MjData and integrate with 1:2:2:1 weights.
The trajectory is not rewritten; unchanged falling trajectories are
compared. `summary.json` separates maximum all-step, maximum recorded-grid
and final residuals, method and uncalibrated status. Remaining solver/
integrator error is not removed or hidden by a threshold.

Startup integration is 0.1 ms, ordinary output 10 ms, and the
3.48–3.60 s braking window records every 0.1 ms.
A 0.05 ms integration comparison and 1 ms output thinning are separate
experiments. `brake_work` is a subset of constraint work, not an extra
energy term. Floor work is constraint work minus brake work; COM angular
momentum change is compared with external floor angular impulse.
Virtual brake dissipation is not hardware temperature/strength.

[Blender](../simulation/blender/README.md) renders the same trajectory;
[CERN ROOT](../simulation/root/README.md) provides columnar exchange and
time-weighted analysis. Neither grants hardware/Fusion acceptance.
Keep the original fourteen short R1 cases in `evidence/initial-v1/` as
history; startup, accounting corrections, Blender and ROOT have separate
versions and independent review.
