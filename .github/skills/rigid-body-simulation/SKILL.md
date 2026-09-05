---
name: rigid-body-simulation
description: Build or revise reproducible rigid-body physics simulations and trajectory-derived visualization. Use whenever cube/reaction-wheel dynamics, floor-contact motion, simulated attitude feedback, physics plots/video or source-to-model intake is requested, including early WIP work before Design Complete. Keep actual-design proxies separate from synthetic fixtures and hardware qualification.
---

# Skill: Rigid-body simulation

## Procedure

1. Read `docs/simulation.md` and the Simulation Engineer profile. Confirm
   the bounded question, expected plots/video and what a result cannot
   establish. Keep FEA, production control and physical operations out.
2. Obtain a frozen source intake through Hardware Lead. Record source
   revision, hashes, coordinates, units, mass accounting and actuator
   constraints. Mark each input SOURCE / DERIVED / ASSUMPTION / UNKNOWN.
   Continue with a separate synthetic fixture when actual data is missing;
   never silently fill unknown physical values from a similar part.
3. Reuse sound existing code, but inspect its semantics first: prescribed
   rotation or Blender keyframes are not an integrated dynamics trajectory.
   Verify engine/API/render capabilities and install only declared local
   dependencies, not global tools or imagined integrations.
4. Construct a minimal free rigid body plus articulated wheel DOFs. Use
   explicit positive inertia tensors and correct origins. Subtract wheel
   mass, first moments and origin tensors from a supplied locked assembly
   before recomputing chassis CG/inertia. Keep visual meshes out of inertia
   inference unless their mass distribution is actually sourced.
5. Establish zero-input/contact and free-space internal-reaction witnesses
   before adding simulated feedback. Declare gravity, friction, contact/
   solver settings, delay/gains and torque/speed assumptions. Apply
   actuator effort through the physical joint, not a direct cube torque.
6. Integrate fixed, CPU-sized scenarios. Preserve failures and saturation;
   do not add hidden support, teleport the state or change a physical input
   merely to achieve a requested-looking animation.
7. Export time/state records, body attitude/rates, relative wheel speed,
   requested/delayed/applied torque, support/contact, energy/work and
   momentum. State which invariants apply: powered energy and dissipative
   contact are not conservative free flight.
8. Generate plots and an actual playable video from the same recorded
   samples; bind frame timestamps/state hashes. Label WIP, fixture/proxy,
   revision, assumed effects and omissions in the views themselves.
   Test macOS `mjpython` separately from offscreen rendering.
9. Run std-lib numerical regression tests and step/solver sensitivity.
   Explain tolerances as numerical regression margins, not physical
   qualification thresholds. Surface warnings/invalid inputs explicitly.
10. Commit a source/model snapshot, then produce immutable versioned
    evidence and hand it to a fresh independent Simulation Reviewer.
    Changed inputs/code invalidate affected conclusions; regenerate and
    re-review instead of editing old evidence in place.

## Output

`simulation/` code/model/runner, source intake, Japanese run/view guidance,
version-bound CSV/NPZ/JSON/plots/video and a precise handoff. Reference cases
may be useful without being an actual-design replica. Unknown actual motor/
brake/source behavior remains a fidelity gap, not a proof of incompatibility.

## Boundary examples

- "Use this 3.06 kg locked total and add three 0.1 kg wheels": derive a
  common-origin decomposition, or disclose why it cannot be derived.
- "Make the cube stand on a corner": run a labeled balance/transition
  trial and show failure if it falls; do not change the result's physics.
- "Use the resulting MP4 for the requested Fusion assembly animation":
  keep the deliverables separate and route Fusion work to Mechanical Lead.
