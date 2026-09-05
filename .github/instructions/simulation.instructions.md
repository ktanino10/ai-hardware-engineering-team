---
description: 'Rigid-body simulation code and evidence require explicit source/assumption provenance, correct internal reaction physics, independent numerical review and strict separation from hardware/Fusion approval.'
applyTo: 'simulation/**'
---

- Follow `docs/simulation.md`, the Simulation Engineer/Reviewer profiles
  and their focused skills. Early WIP simulation is allowed before Design
  Complete; missing actual inputs do not block a separately labeled fixture.
- Keep source intake frozen/versioned. Record hashes and whether upstream
  is main, a committed WIP branch or an explicitly uncommitted snapshot.
  Never read a live changing design as if it were the accepted source.
- Physical part facts retain their original Evidence IDs/source owners;
  do not allocate shared DS/ECO/ISS/MISS IDs here. Explicit mathematical
  fixture assumptions are not manufacturer claims. UNKNOWN is not zero.
- Distinguish synthetic reference, partial WIP design proxy and a qualified
  actual system. Do not treat solid CAD volume as actual complete mass,
  lower-bound mass, measured CG or material/process qualification.
- Articulated rotor masses/inertias must not be counted again in the
  chassis. Translate tensors to a common origin before subtraction.
- No hidden direct cube torque, fixed support, post-initialization pose
  correction, disabled contacts or keyframed motion to fabricate success.
  Render only the integrated recorded states.
- State units/frames, actuation/control/contact/solver assumptions,
  omissions, numerical tolerances and energy/momentum invariant scope.
  Log requested/applied torque, saturation and numerical failures.
- Verify local dependencies/render/viewer capabilities. No device access,
  global environment mutation, physical operation, RL fleet, FEA/SPICE or
  unsupported tool/API assumption under this initial scope.
- Store code/input/model/scenario/engine/output hashes and actual playable
  media. Source/model changes invalidate affected conclusions; generate
  new evidence versions and obtain independent re-review.
- Simulation Reviewer owns `simulation/reviews/` verdicts. Do not self-pass
  a numerical model or edit the hardware/mechanical findings backlog.
- Simulation-only controllers are not deployable firmware. Dynamics MP4s
  are not Fusion assembly-process videos or native storyboards. All
  existing physical-action, Design Complete and assembly-evidence gates remain.
