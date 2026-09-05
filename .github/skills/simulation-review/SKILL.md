---
name: simulation-review
description: Independently review a rigid-body simulation's actual implementation and recorded results. Use for physics-model acceptance, reaction-wheel/contact/control trials, source or inertia revisions, numerical invariants and trajectory/video agreement; never substitute this for mechanical, firmware or real-hardware safety review.
---

# Skill: Simulation review

## Independent procedure

1. Load the Simulation Reviewer profile and `docs/simulation.md`. Work in
   a fresh reasoning context, not the model author's self-check. Establish
   exact model/code/input/run scope before assessing any claimed success.
2. Inspect actual model XML/code and primary engine documentation. Verify
   SI units, orientation conventions, COM reference points, tensor
   symmetry/positive principal moments/triangle inequalities and mass
   accounting. Independently recompute an articulated decomposition where
   the upstream source provides a locked total.
3. Trace the actuator transmission and force paths. Confirm internal
   effort conserves whole-system momentum in a suitable free-space case.
   Independently derive initial acceleration from mass/inertia, not the
   engine's own mass matrix alone. Check signs in a rotated frame.
4. Inspect initial contacts, loaded support, gravity, friction and contact
   softness/solver assumptions. No hidden pivot or suppressed contact.
   Account for motor work and contact dissipation rather than asserting
   energy conservation in the wrong experiment.
5. Run tests plus representative actual scenarios. Compare timestep and
   solver changes; distinguish numerical convergence from physical model
   validity. Preserve a numerical witness and the inputs that reproduce it.
6. Inspect feedback, delay, saturation, overspeed and failure reporting.
   A geometric corner orientation need not balance an off-centre CG.
   Ideal torque/reverse torque is not qualified hardware braking, current
   delivery, thermal dissipation or real-time firmware.
7. Compare recorded CSV/NPZ states with plots and exact video-frame
   timestamps/state hashes. Decode/play the video; do not accept a render
   script as delivered video or visual plausibility as dynamics evidence.
8. Verify source/model/output hashes and check stale/mutated inputs are
   surfaced. Preserve historical results as historical. Do not demand
   live hardware readiness just to review early WIP evidence.
9. Record findings and fidelity gaps separately. Route model/code defects
   back to Simulation Engineer; route physical implications to Hardware
   Lead without editing CAD/BOM/shared findings or accepting risk.

## Record format and verdict

Store `simulation/reviews/<review-id>/review.md` plus machine-readable
repeatable witnesses. Include reviewer identity, reviewed revisions/hashes,
scope, commands/results, independent derivation, visual agreement, findings,
fidelity gaps and a scoped PASS / CONDITIONAL / FAIL.

Each finding: simulation-local ID, severity CRITICAL/HIGH/MEDIUM/LOW,
file/lines or output sample, evidence, consequence, reproduction, requested
fix, status and re-review disposition. Open CRITICAL/HIGH defects prevent
reliance on affected conclusions. A PASS for plumbing never certifies
strength, containment, physical feasibility, Design Complete or Fusion
assembly documentation.

## Adversarial checks

Challenge at least one premise, not only stated equations: a partial mass
presented as complete, wrong COM origin subtraction, an unavailable driver
BRAKE command, a successful-looking animation from a different trajectory,
or source changes hidden behind an unchanged "PASS" label.
