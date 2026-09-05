# R1 — Independent cube simulation review

**Verdict: CONDITIONAL for the initial numerical-model scope.**

The free-body/three-rotor dynamics, source decomposition, frame conventions,
controller plumbing and sampled-state/media linkage pass the checks below.
There are **no identified CRITICAL or HIGH implementation defects**.
**SIM-R1-001, MEDIUM, remains open:** the contact-work diagnostic has substantial
quadrature error and must not support quantitative contact energy, dissipation
or efficiency conclusions. The independently reproduced failed/falling trials
remain valid observations of these particular, explicitly incomplete models.

This is **not** actual-hardware feasibility/safety acceptance, Design Complete,
permission for physical action, control-firmware approval, or Fusion
assembly-process/native-storyboard acceptance.

## 1. Reviewer, boundary and reproducibility

- Reviewer: **GitHub Copilot, fresh independent Simulation Reviewer**, invoked
  through the general-purpose agent because the new role is not registered in
  the running tool schema. I loaded its real profile, skill, path instruction
  and `docs/simulation.md`. I did not author the reviewed implementation.
- Review date: **2026-09-05**. This review owns only `simulation/reviews/r1/`;
  experiments were confined to `simulation/runs/reviewer-r1/`.
- Branch: `ktanino10-cube-physics-simulation`.
- Base: `dd7e4b4a7f4ccd838edeb93b9cc9aac86dc1375d`.
- Reviewed HEAD: `848005a0a63ebc2d9931bea60251e98d40c0296d`.
- Implementation/model snapshot:
  `6636b95b78bb14b94acda53a413d39f6baa8688a`. The subsequent reviewed commit
  changes outputs, not `cube_sim/`, models or intake.
- The tracked working tree was clean before reviewer writes. No implementation,
  model, archived evidence, hardware, BOM, registry, validation, workflow or
  branch changes were made. No delegation, commits, PR operations, device
  access, old-script execution or external design uploads occurred.
- At the final scope check, concurrent untracked `simulation/blender/` and
  `simulation/evidence/blender-replay-v1/` appeared. R1 did not create, inspect
  or assess those files. They are excluded from this verdict; all tracked
  reviewed files still matched their recorded hashes.

### Intended startup maneuver — follow-up scope clarification

On **2026-09-05 at 23:36 JST**, the user clarified the intended startup as
**high-speed spin-up followed by stop/braking**, and supplied
`https://github.com/ktanino10/attitude-control-study` as a mechanism source.
That new repository was **not accessed or investigated by R1**. The reviewed
commits and numerical witnesses above remain unchanged.

The existing one-/three-wheel pulses start with stationary wheels in **free
space**, use modest ideal torque and then reverse it; they are not a
source-grounded, high-speed, floor-contact spin-up/brake maneuver. The edge/
vertex PD cases are prepositioned, and the face attempt is direct attitude PD,
not a spin-up/brake sequence. Their limited wheel momentum and failed outcomes
neither establish nor disprove the feasibility of the newly clarified
mechanism. **R1 does not accept that intended maneuver as implemented or
tested.** A separately frozen, source-grounded case and its actual outputs
require a subsequent independent review.

The **23:42 JST** follow-up reports a separate ephemeral spin-up/finite dry
hinge-friction startup prototype and an isolated background Blender replay
path. Neither was exercised or assessed by R1. The reported 3000 rpm remains
a target-only analysis point, not a qualified speed. The new Blender path is
described by its author as rendering recorded MuJoCo states, not native Blender
dynamics or Fusion evidence; R1's media checks and verdict do not extend to it.
The unsaved interactive Blender scene was not accessed by this reviewer.

### Durable witnesses

- [`witness.py`](witness.py): independently authored, repeatable calculations
  and experiments.
- [`witness.json`](witness.json): numerical results, exact reviewed-file/output
  SHA-256 inventory, witness self-hash, environment, primary-source hashes,
  mutation checks and video comparisons.

The witness independently integrates the frozen STL's volume moments; it
does **not** import the old screening script or the author's inertia,
quaternion, momentum, energy or CSV calculation helpers. It uses the actual
MuJoCo engine and reviewed runner where explicitly testing their behavior.
It is not an independent implementation of a contact physics engine.

Commands, from the repository root:

```sh
mkdir -p simulation/runs/reviewer-r1/test-work
(
  cd simulation
  PYTHONDONTWRITEBYTECODE=1 \
  TMPDIR="$PWD/runs/reviewer-r1/test-work" \
  MPLCONFIGDIR="$PWD/runs/reviewer-r1/mpl-cache" \
  .venv/bin/python -m unittest discover -s tests -v
)
PYTHONDONTWRITEBYTECODE=1 simulation/.venv/bin/python \
  simulation/reviews/r1/witness.py
git diff --check
```

**Observed:** all 21 existing tests passed; the independent witness completed
all assertions. Passing the author's tests was corroboration, not acceptance.
Python 3.14.3, MuJoCo 3.12.0, NumPy 2.5.2, Matplotlib 3.11.1 and Pillow 12.3.0
were exercised on macOS arm64. The witness verifies reviewed-file hashes again
after running. A future implementation change requires a new review; the
strict HEAD check intentionally prevents silently reusing R1 against it.

### Principal bindings

| Input | SHA-256 |
|---|---|
| `simulation/models/reference.json` | `b34b181117b7a12cf8e8356bcf1a57321deab20726d12249f39badaaba889c1f` |
| `simulation/models/rev5-proxy.json` | `7c08f26532fc2365e935f1fd1761b6cc5eb1662ad3a17dafbe7ad2439e363b6a` |
| `simulation/intake/rev5-v1.json` | `dd14031121c6f40fcbcb974a82231e49eaf6d4e9c79d0d3fc0f41ad2887bcc76` |
| dependency lock | `46a9c69d790ca27c38135aefa26e08d683a1e7536080b93840a90b61cbd89cb7` |
| original intake bundle `manifest.json` | `1f94e5fdf89d8e1df234e9dec4db7ea32568e30671ba9a841293cf9d79d55999` |
| original `INTAKE.txt` | `bef4cfd724089d818b6083070dd2853c40b23100bdac6826157f3742a47233a2` |
| original `baseline/results.json` | `a181bc328b61ecdad52a0b8acdcc6e7cc5c0e5c4748b680ec8fcad0aa5e44c36` |
| original `baseline/screen.py` — read only | `fc8b4dd6e013afc834b37649414e6230b5689e5c28a9b67a0ec2b6fec7d3bd88` |

The original bundle was read only at its expressly authorized session-files
path. Its three source files referenced by the intake were hash/size checked.
The frozen WIP source is `3633eb5d03d6db7c90b582e53180414087b33519`, **not main
or release**. No live other worktree was read. The different candidate-L study
was neither investigated nor executed.

## 2. Primary semantics checked

I read actual official documentation, including the **3.12.0-tagged source**
of the documentation and `engine_forward.c`, rather than relying on search
summaries. Download hashes are in `witness.json`.

- [Actuation/transmission](https://mujoco.readthedocs.io/en/stable/computation/index.html#actuation-model):
  actuator output maps through transmission moment arms to generalized
  forces. The three `motor` hinge transmissions have unit gear.
- [Explicit inertials](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-inertial-fullinertia):
  `fullinertia` order is diagonal XYZ, then XY/XZ/YZ; the compiler diagonalizes
  the tensor. The inertial position is the COM.
- [Inertia inference](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-inertiafromgeom):
  `false` prevents the visual geoms from contributing inferred mass/inertia.
- [Subtree angular momentum](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreeangmom):
  about the whole subtree COM, expressed globally.
- [Solver/contact parameters](https://mujoco.readthedocs.io/en/stable/modeling.html#solver-parameters)
  and [soft-contact semantics](https://mujoco.readthedocs.io/en/stable/computation/index.html#soft-contact-model):
  positive `solref` means time constant/damping ratio; soft friction is not
  strict maximum-dissipation Coulomb contact.
- [Exact RK4 implementation](https://github.com/google-deepmind/mujoco/blob/3.12.0/src/engine/engine_forward.c):
  four state evaluations; intermediate evaluations skip sensors, not
  dynamics. The read-only stage recorder respects that ordering.
- [Passive viewer](https://mujoco.readthedocs.io/en/stable/python.html#passive-viewer):
  macOS requires `mjpython`. **I did not exercise native GUI replay**; the
  media checks below are full video decoding plus image/record comparisons.

## 3. Mass, tensors, units and source versus assumption

**PASS for the two declared mathematical inputs.**

The coordinate contract is SI; body-origin positions and body-frame angular
rates are distinguished from world translation and world momentum. The
quaternion is unit `wxyz`, body-to-world. I checked three distinct positive
body-axis rotor joints, free root `nq=10, nv=9, nu=3`, no equality pivot,
zero external applied-force arrays and no root actuator effort. Ground-trial
contacts are enabled; only explicitly free-space trials disable them.

### Independent source/decomposition calculation

The copied prints-only STL contains **51,230 triangles**. Independently
summing signed tetrahedron volume, first moments and second moments, with
one mm→m conversion and the **assumed** 1270 kg/m³ density, gives:

- printed mass: **2.632097797839991 kg**;
- COM: **(0.007233981039601316, 0.007254108324892235,
  0.005787144820075161) m**;
- maximum tensor disagreement with the frozen printed aggregate:
  **6.25×10⁻¹⁶ kg·m²**.

Adding three whole-motor uniform-cylinder surrogates and the bare homogeneous
laminate independently, rather than subtracting the author's wheel result,
gives chassis mass **2.764277797839991 kg**, COM approximately
**(0.007693237482, 0.007864991921, 0.005259664983) m**, and a tensor within
**6.32×10⁻¹⁶ kg·m²** of the proxy chassis. Adding the articulated wheels
recomposes the supplied **3.0642777978399987 kg locked partial assembly**,
its first moments and full centroidal tensor to floating-point precision.

The subtraction/addition is about a common origin:
`I_O = I_C + m[(r·r)1 − rrᵀ]`; only afterward is the residual chassis
recentered. I found no wheel mass double-counting or subtraction of
incompatible centroidal tensors.

Proxy chassis principal moments are
**(0.037947299075, 0.038302660288, 0.039269823341) kg·m²**.
All four bodies in each model have positive principal moments satisfying
triangle inequalities. Reconstructing the proxy's compiled full tensor
differs from its declared tensor by at most **2.34×10⁻¹³ kg·m²**.

**Premise challenged:** matching those moments does not make this a complete
physical cube. The source is prints plus explicit analytical additions.
The whole motor surrogate stays on the chassis; the actual rotating
bell/stator split is unknown. Population, battery, hubs, retention and
harness are not established. Neither a measured mass/CG nor a physical
lower bound follows. The intake, model and views retain those distinctions.
I did not independently qualify the actual motor or driver.

## 4. Internal reaction, independent acceleration and free-space invariants

For axisymmetric rotors at rest, independently aggregated locked inertia
`J` about the **whole assembly COM**, and axial rotor matrix
`D = diag(I_axis)`, angular momentum and hinge equations give:

```text
H_body = J ω + D ṡ
0 = J α + D s̈                 (no external moment)
τ = D(α + s̈)                  (hinge motor effort)
α = −(J − D)⁻¹ τ
s̈ = D⁻¹ τ − α
a_body-origin,world = −R(α × c_whole)
```

This uses part masses/tensors and parallel axes, **not the engine mass
matrix as the prediction**. With `τ=(0.009,−0.007,0.011) N·m`:

| Model | Predicted body α, rad/s² | Predicted relative rotor acceleration, rad/s² |
|---|---|---|
| Reference | (−0.8296064725, +0.6549117157, −1.0151712460) | (+200.8296064725, −156.2104672713, +245.4596156905) |
| Rev5 proxy | (−0.2204619599, +0.1775570204, −0.2734625330) | (+200.2204619599, −155.7331125759, +244.7179069775) |

Identity, 90° world-Z rotation and an oblique rotation were tested, with
nonzero rotor angles. Maximum body/joint acceleration differences were
**1.51×10⁻¹² / 2.08×10⁻¹² rad/s²**. The predicted world translational
acceleration of the off-COM body origin also matches. Positive X-wheel
effort gives the appropriate opposing body rotation, including negative
world-Y response in the rotated sign test.

A separate **0.6 s** free-space experiment starts with nonzero world
translation, oblique body rotation and three spinning wheels. Momentum is
summed directly over body COM velocities, spin tensors and orbital terms.
Initial momentum is deliberately **not zero**, so a zero-valued sensor
could not pass. A 100 ms stationary zero-input test is exact.

| Independent maximum error/drift | Reference | Rev5 proxy |
|---|---:|---:|
| Linear momentum drift, kg·m/s | 1.39×10⁻¹¹ | 1.91×10⁻¹¹ |
| COM angular momentum drift, N·m·s | 2.22×10⁻¹¹ | 2.01×10⁻¹¹ |
| Rigid energy − motor work, J | 2.23×10⁻¹² | 2.71×10⁻¹² |
| Direct kinetic/potential energy vs engine, J | 5.00×10⁻¹⁶ | 6.33×10⁻¹⁵ |
| Quaternion norm error | 1.12×10⁻¹⁵ | 1.12×10⁻¹⁵ |

Declared numerical tolerances are `1e-10` for momentum, `1e-7 J` for powered
free-space work closure and `1e-12` for quaternion norm. These are regression
limits, not hardware tolerances. This evidence supports genuine internal
reaction rather than a hidden externally torqued cube.

## 5. Contact, controller and interpretation of failures

Independent transformed-corner calculations confirm the initial clearances:
zero for rest/prepositioned/face-attempt cases and 0.12 m for the drop.
Initial velocities are zero. Edge and vertex starting heights are
**0.1696022474 m** and **0.2077616874 m**; the face-attempt height is
**0.1200000000 m**. Those are different initial-condition experiments,
not a demonstrated sequence of transitions.

Rest supports weight: **12.753000 N** for the reference and
**30.050299866 N** for the proxy, with errors below `1e-3 N`.
Maximum recorded rest penetration is approximately **0.0479 / 0.0489 mm**.
Independent rigid-point velocities agree with the engine contact Jacobian;
the recorded XY point-slip calculation is appropriate for this horizontal
floor. Contact-frame force·velocity agrees with generalized constraint
power to numerical precision.

The contact law is Newton/RK4, elliptic cone, `condim=3`, sliding coefficient
0.6, `solref=(0.01 s,1)` and `solimp=(0.9,0.95,0.001 m)` with the engine's
remaining defaults. There is no rolling or torsional resistance. These are
uncalibrated assumptions. Proxy drop/vertex sampled penetration reaches
**5.041 / 3.335 mm** at 2 ms. Rest-height agreement does not validate impacts.

I independently recomputed commands from quaternion error/body rates and
checked the **20 ms FIFO**, ±0.02 N·m clipping, cutoff flags and applied
effort on archived rows. A separate rotated free-space PD trial reduces
error from **0.035 to 0.0139205 rad** in 1.2 s. This checks feedback sign,
not deployable control capability.

The 80 rad/s cutoff removes outward effort, not velocity. For example,
the proxy face attempt reaches **80.8888889 rad/s**, and its vertex case
reaches approximately **86.115/81.845/86.892 rad/s**. Such overspeed is
exposed, not silently clamped. The reference vertex run also contains five
axis-samples of permitted reversing effort while over the cutoff.
No actual DRV10983 runtime BRAKE, torque/current capability, regeneration,
latency qualification or thermal interpretation follows.

| 3-second case | Reference final attitude error | Proxy final attitude error | Correct interpretation |
|---|---:|---:|---|
| Edge balance | 45.0007° | 45.0009° | Departed the prepositioned target |
| Vertex balance | 54.8659° | 55.4306° | Fell from the prepositioned target |
| Face-to-vertex attempt | 54.7366° | 54.7372° | Target not reached |

These failures are not bugs merely because the objective is unmet. PD lacks
capture/translation strategy, feedforward, state estimation and desaturation.
A geometric target also need not balance the asymmetric proxy's COM.

## 6. Open numerical finding

### SIM-R1-001 — MEDIUM — Contact-work quadrature is not quantitatively reliable

- **Location:** `simulation/cube_sim/runner.py:76–78,110–114,160–162`;
  contact-work fields in `trajectory.csv`/NPZ and the energy plots.
- **Status:** OPEN; returned to Simulation Engineer for the correction below.
- **Affected scope:** contact work, dissipation and energy-budget conclusions.
  This is not a finding of fake motion, incorrect internal reaction or a
  physical incompatibility of the proposed hardware.
- **Witness:** `witness.py:contact_energy()` and
  `witness.json.contact_energy_diagnostics`; actual proxy fall
  `trajectory.npz` SHA
  `c6fc99ea063818ced4240a7a9e7356fcb5d476fcc2ffb301cafe327a1a26cfda`.
  All other per-output bindings are under
  `archived_artifacts["rev5-proxy/fall"].outputs`.

**Evidence and cause.** The runner uses endpoint trapezoidal force-power
integration while the dynamics use four RK4 evaluations. During an impact,
endpoint powers can miss the large intermediate contact force.
At the proxy drop's **0.156→0.158 s** step, the four constraint powers are
approximately **0, −1201.5405, −747.6823, −559.6590 W**.
The all-step trapezoid residual reaches **−0.8313792 J**; the 100 Hz archive
shows **−0.7920505 J** at 0.160 s. The final summary alone is
**−0.3160858 J** and understates the largest excursion.

I attached a read-only recorder to the actual RK4 stage evaluations, then
evaluated their powers in a separate `MjData` after each step. The state
trajectory was not changed. Stage-consistent quadrature substantially
reduces the residual:

| Proxy case | Step | Max archived-grid endpoint-work residual, J | Max all-step RK4-stage-work residual, J |
|---|---:|---:|---:|
| Fall | 2 ms | 0.792050 | 0.041277 |
| Fall | 1 ms | 0.570607 | 0.008584 |
| Fall | 0.5 ms | 0.189044 | 0.001446 |
| Vertex balance | 2 ms | 0.517960 | 0.016437 |
| Vertex balance | 1 ms | 0.106115 | 0.004673 |
| Vertex balance | 0.5 ms | 0.158539 | 0.001060 |

The **remaining** stage-work residual decreases with timestep and is not
zero. It is integration error/uncertainty, not qualified material loss.
CG at 2 ms reproduces the large endpoint-work residual closely; more
solver iterations alone do not solve the quadrature problem.

This conclusion is not inferred solely from two engine energy fields.
I independently recomputed rigid kinetic/potential energy and its
instantaneous time derivative. The small difference between `dE/dt` and
generalized force power is accounted for by `vᵀ(Ma+b−f)` from the finite
constraint solve; the unexplained difference is below **6.4×10⁻¹⁰ W**.
The mass matrix here is used only to identify the solver residual, not to
predict the independent acceleration/momentum checks in §4.

**Impact and severity.** Nonconservative contact does not excuse violation
of the mechanical work identity once constraint force·velocity is included.
Nor does omitted stored soft-contact energy excuse this particular
endpoint-versus-stage discrepancy. However, current plots expose the
residual, documentation rejects contact-energy qualification, and the
qualitative failed outcomes persist across 2/1/0.5 ms and Newton/CG.
Therefore this is **MEDIUM**, not a CRITICAL/HIGH rejection of the initial
free-body/contact visualization lane.

**Requested correction before quantitative reliance:**

1. Use stage-consistent work accumulation, or another documented quadrature
   with demonstrated contact accuracy, without changing physical parameters
   to seek a successful trial.
2. Report the quadrature method and **maximum plus final** energy/work
   residual, with a machine-readable contact-energy accuracy/qualification
   status. Distinguish sampling, quadrature, integrator and solver errors.
3. Preserve `initial-v1` as historical evidence; create new source/output
   versions if implementing the correction. Obtain a fresh independent
   re-review of contact energy/work before relying on those quantities.

**Current disposition:** qualitative motion and failure observations may be
used under this conditional verdict. No quantitative contact work, heat,
efficiency, impact or energy-transfer acceptance is granted.

## 7. Actual evidence, plots, videos and stale-data behavior

For **all 14 archived runs**, I checked the gallery's nested manifest hashes,
all output hashes, current code/model/intake/lock correspondence, every
CSV column against NPZ (**62 columns**), independent attitude/rate/energy/
momentum calculations, summary outcomes, and every frame-map timestamp and
little-endian float64 pose hash. Video rows are `0,4,8,…` at 25 fps;
the terminal trajectory state is intentionally not an extra frame.

I independently reran **reference/three-wheel** and **proxy/fall,
proxy/vertex-balance, proxy/face-to-vertex-attempt**: every recorded NPZ
array and the executable XML matched exactly. Four corresponding archived
plots regenerated **byte-for-byte** in reviewer scratch. I visually inspected
the actual proxy fall and vertex energy/motion plots, not just their scripts.

The same four MP4s were fully decoded with ffmpeg, counted with ffprobe and
checked as H.264 **960×720, 25 fps**, with the expected 50/75 frames.
First, middle and last decoded scenes were compared against direct
MuJoCo rendering of the independently selected recorded states:

| Video | Scene mean absolute RGB error, range over three frames | Middle frame versus full preview mean RGB error |
|---|---:|---:|
| Reference three-wheel | 0.5655–0.6016 | 0.8695 |
| Proxy fall | 0.6167–0.7042 | 0.8891 |
| Proxy vertex-balance | 0.5943–0.6650 | 0.9786 |
| Proxy face attempt | 0.5846–0.5882 | 0.9833 |

Those errors are consistent with lossy H.264, not a different trajectory.
I inspected the decoded contact sheet. The free-space cube changes attitude;
the proxy drop settles on a face; the proxy vertex falls onto a face with
visible failure/limit labels; the face attempt stays face-supported while
its wheels saturate. WIP/classification/source labels are present. Tracking
camera and marker aliasing are disclosed. **This is decoded-video inspection,
not a claim of native GUI playback.**

In an isolated scratch copy, changing code, selected model, frozen intake or
dependency lock rejects `verify_current` while retaining historical output
readability. Corrupting CSV or MP4 rejects both current and historical
verification. Removing XML rejects verification; reusing a run directory
refuses overwrite. Originals were unchanged.
These are hash-consistency checks against the recorded/Git-bound manifests,
not a claim that self-editable hashes provide authentication against someone
rewriting both evidence and its trust anchors.

## 8. Unresolved fidelity gaps, distinct from SIM-R1-001

1. **Actual system input remains incomplete.** Unknown population, battery,
   hubs/retention, harness, actual rotor/stator split and real mass/CG/inertia
   remain source-owner work. Numerical recomposition cannot resolve them.
2. **Contact law is not calibrated.** Friction, compliance, restitution and
   impact loading remain unknown. This soft-contact law can even have local
   positive tangential power: the independent stage probe observed maxima
   of **0.04664 W** in the proxy fall and **2.40858 W** in its vertex trial
   at 2 ms. This matches the documented non-strict-complementarity limitation;
   it is not proven real surface behavior or a brake-heat estimate.
3. **Impact/path accuracy remains limited.** The unchanged final failure
   classifications and near-identical settled heights do not establish
   convergence of every unstable/contact trajectory, force peak or bounce.
   The contact-work finding is a separate numerical diagnostic issue, not
   a replacement for physical calibration.
4. **Ideal actuator and controller remain fixtures.** Bidirectional effort,
   cutoff and delay are not MN2206/DRV10983 application qualification.
   No production control, source/regen, thermal, containment or strength
   conclusion is supported.
5. **Media and integration boundaries remain intact.** Review of the new
   roles, skills, architecture/workflow/firmware boundary edits found no
   contradiction that promotes simulation into hardware approval or creates
   the third Control Engineer role. Genuine requested Fusion assembly-process
   storyboards and published video remain separate and unassessed here.

**Handoff:** Simulation Engineer owns SIM-R1-001's numerical correction;
Hardware Lead routes the physical fidelity gaps to existing source owners.
No shared hardware finding is closed or risk accepted by R1.
