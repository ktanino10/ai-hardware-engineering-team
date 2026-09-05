# Rigid-body simulation contract

This is the **user-approved initial physics lane**, not a physical design
release. It adds two roles: Simulation Engineer and independent Simulation
Reviewer. It covers a free rigid cube, floor contact/friction, three actual
rotor DOFs and a small simulation-only attitude controller. It does not add
a third Control Engineer or authorize deployable control firmware, FEA,
thermal/SPICE simulation, broad optimization, physical operation or a
certified digital twin. See [Japanese run/view instructions](../simulation/README.md).

## Entry, ownership and evidence states

Start during requirements/interface/design work, **before Design Complete**.
Hardware Lead obtains frozen inputs from the current source owners and
routes gaps; simulation does not create a second CAD, PCB, schematic or BOM.
Systems Engineer retains cross-discipline trade-off judgment.

| Label | Meaning | Permitted conclusion |
|---|---|---|
| `SYNTHETIC_REFERENCE` | Explicit mathematical fixture, not sourced as an actual populated assembly | Numerical plumbing and behavior of that fixture only |
| `WIP_DESIGN_PROXY` | Frozen design facts/moments plus identified omissions and assumptions | Conditional behavior of that incomplete proxy |
| Actual-driver/system case blocked | Required mass/actuator/contact data not established | Missing evidence, not proven universal incompatibility |

Both runnable labels remain `WIP_SIMULATION_NOT_HARDWARE_OR_ASSEMBLY_APPROVAL`.
Review acceptance is scoped to numerical implementation, never a transition
to an APPROVED assembly manifest. No simulation-only finding silently changes
the five Design Complete conditions or closes a hardware/mechanical finding.

The engineer owns `simulation/cube_sim/`, inputs, numerical tests and
`simulation/evidence/<version>/`; the reviewer owns
`simulation/reviews/<review-id>/`. Use simulation-local finding IDs.
Route hardware implications through Hardware Lead and the existing source
owners, Evidence IDs and human decisions. Do not consume their shared IDs.

## Minimum model contract

Record the following, with SOURCE / DERIVED / ASSUMPTION / UNKNOWN confidence:

- Source commit/branch status and file hashes; input/model/scenario version.
- World/body/inertial frames, SI units, quaternion order, positive axes.
- Mass inventory, exclusions, COM and symmetric positive inertia tensors
  about named points. Positive principal moments also satisfy triangle
  inequalities. Render geometry does not silently provide inertia.
- Internal rotor joints and actuation transmission, relative versus absolute
  wheel speed, command versus delivered torque, cutoff/delay semantics.
- Gravity, collision proxy, contact/friction/solver/integrator parameters,
  initial state, controller gains and the modeled objective.
- Omissions, expected numerical witnesses and tolerances, and what an
  observed failure or apparent success can actually establish.

For a locked input `(M, c, I_C)`, work about one origin:

```text
P(r) = (r dot r) Identity - r r^T
I_O = I_C + M P(c)
M_base = M - sum(m_wheel)
first_base = M c - sum(m_wheel c_wheel)
I_O_base = I_O - sum(I_C_wheel + m_wheel P(c_wheel))
c_base = first_base / M_base
I_C_base = I_O_base - M_base P(c_base)
```

Recompose the locked mass/COM/tensor as a witness. The initial Rev5 proxy
also checks the residual chassis independently by adding the supplied
prints-only moments, whole-motor surrogates and bare laminate. This proves
consistency with that **partial analytical input**, not actual mass, infill,
CG, installed fit or rotating motor-bell inertia.

## Initial implementation choices

MuJoCo's freejoint body has three hinge-child rotor bodies. `motor` joint
transmission with `gear=1` applies internal generalized torque; equal and
opposite body reaction follows the coupled dynamics. No direct base torque,
equality pivot, contact suppression in ground trials or pose adjustment
after initialization is allowed. The free-space witnesses explicitly turn
gravity/contact off; they are not jump demonstrations.

The reference uniform cube and cylinders have closed-form inertias.
The Rev5 case freezes source-owner WIP commit
`3633eb5d03d6db7c90b582e53180414087b33519` and the supplied numerical intake;
it uses **3.0642777978399987 kg partial locked total**, decomposed into about
**2.76427779784 kg chassis plus three 0.1 kg target rotors**. It is neither
a physical lower bound nor a complete populated mass. Unknown battery/
electronics/hub/harness/retention and motor rotor/stator split remain explicit.
The box collision proxy and mass-moment representation are not replacement CAD.

Ideal bidirectional torque/reverse torque, 20 ms command FIFO and the
reference torque/speed-cutoff values are simulation assumptions, unchanged
when applied to the proxy. They do not describe actual DRV10983 braking,
current, stop/hold/restart or source/regen behavior. There is no generic
on-demand runtime BRAKE bit here. A speed cutoff removes outward motor
effort, not velocity; external motion/discrete steps can exceed it.

The controller is sampled PD on the quaternion attitude error, with no
state estimator, gravity/gyro feedforward, translational capture strategy,
wheel desaturation or real-time firmware. Edge/vertex trials are initially
pre-positioned; geometric targets do not necessarily align an asymmetric
proxy's COM over support. A separate face-to-vertex attempt starts on a face.
No scenario is tuned or required to succeed.

The initial solver is Newton with elliptic friction cone, condim 3
(normal plus two sliding directions), no rolling/torsional resistance.
RK4 at 2 ms was chosen after a small free-space experiment found
timestep-linear translational momentum drift with implicitfast; the
documented solver/time-step comparison is numerical evidence, not
calibration. Soft-contact parameters are unmeasured assumptions and can
produce millimetre-scale impact penetration. No material deformation,
restitution, impact-load or containment inference is justified.

## Run/evidence contract and invalidation

Each immutable run contains `input.json`, `scenario.json`, executable
`model.xml`, `trajectory.npz`, human-readable `trajectory.csv`, `summary.json`,
`plots.png`, `motion.mp4`, `video-frames.csv` and `manifest.json`.
The manifest binds code/revision, dependency/engine versions, source intake,
model and every output hash. Uncommitted model/code is labeled as such.
The 100 Hz state grid is shared by CSV and plots; 25 fps video uses exact
recorded rows without pose/time interpolation. Frame maps include state
hashes; terminal state is in the trajectory, not an extra video frame.

Log quaternion attitude, body-frame/angular-world rates, relative wheel
rates, requested/delayed/applied torque, saturation/cutoff/overspeed,
absolute axial wheel rates, loaded contact count/normal force/penetration/
point slip speed, rigid potential/kinetic
energy, actuator/passive/constraint work and total COM angular momentum.
These sampled records do not bound inter-sample impact or torque peaks.
Energy conservation is appropriate for unforced free space, not powered or
dissipative-contact trials. Motor work uses relative joint speed; contact
work is not electrical/brake heat or a structural load qualification.

`verify` checks bound outputs and current implementation/model/intake hashes;
`verify --historical` checks archived outputs only. A changed source,
decomposition, contact law, controller or solver invalidates the affected
conclusion until regenerated and re-reviewed. Preserve old versions and
record the new intake's relationship to the old one. An upstream WIP
snapshot does not automatically become current/main when a branch advances.

These are the revision/evidence principles of [the assembly contract](assembly-evidence.md),
not its schema or acceptance: **no `current.json` or fabricated assembly
manifest is created for simulation**. MuJoCo video is dynamics visualization.
The separately requested genuine Fusion assembly-process storyboards and
published video remain a different, mandatory deliverable for that workflow.

## Review and numerical tolerances

A fresh reviewer examines equations, source confidence, actual code and
actual trajectories/media; reruns representative cases; and records scoped
findings plus unresolved fidelity gaps. Open simulation CRITICAL/HIGH
defects block reliance on affected results and require engineer correction
and independent re-review. A conditional modeling conclusion cannot accept
hardware risk or authorize a physical action.

The small std-lib tests use these regression margins, not acceptance
criteria for a manufactured cube:

| Witness | Numerical margin and rationale |
|---|---|
| Initial inertia/acceleration and frame/mass recomposition | 1e-10 acceleration, 1e-12 to 1e-14 tensor/frame comparisons: floating-point algebra against independent closed forms |
| Free-space linear/angular momentum | 1e-10 kg m/s or N m s: well above observed RK4 roundoff, far below applied impulse |
| Powered free-space rigid energy minus actuator work | 1e-7 J: regression guard for the declared sampled input and trapezoidal work integration |
| Quaternion norm / deterministic replay | 1e-12 norm; identical same-runtime recorded arrays |
| Passive rest | Weight within 1e-3 N, penetration below 0.2 mm: regression envelope of this uncalibrated soft-contact fixture |
| Step/solver sensitivity | 2/1/0.5 ms; Newton 50/100 and CG 100 iterations. Free-space final state within 1e-8; rest/drop final height within 10 micrometres / 1 mm; drop penetration below 10 mm. These are model-regression guards, not physical contact bounds |

Near unstable edge/vertex trials, sensitivity is reported rather than
claiming every detailed contact path converges. The fixed short trials
retain their failure outcome across the compared settings. No optimization,
physical feasibility theorem or new component recommendation follows.
