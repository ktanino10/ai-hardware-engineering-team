# R2a — Bounded closure recheck

**Verdict: CONDITIONAL.** The four original R2 defects are corrected as
specified below. One **new MEDIUM counterexample within the changed native
geometry checker**, SIM-R2A-001, still permits a false full-geometry receipt.
There is no newly identified dynamics defect and no reason to rerun or tune
the physics model to address it.

## Scope and preserved evidence

- Independent reviewer: GitHub Copilot, continuing the independent R1/R2
  Simulation Reviewer context; not the implementation author.
- Date: **2026-09-06 JST**.
- Frozen HEAD: `8c626ecb55983005b157da48a4a7a7f3982a23a9`.
- Adapter/runtime correction:
  `a9109f376e70b28788a4b99348cf3d39b2af2da3`.
- Test-only correction:
  `21a5344db9c19a9b54abaf23509662af4a7dbc71`.
- Current output scope: `startup-v4`, `blender-replay-v5`, `root-v4`.
- **R1 and R2 reports/witnesses remain unchanged.** No implementation,
  historical evidence, dynamics parameters, live Blender scene, Git history,
  PR or physical hardware was changed. No agents/factory were used.

This is only a closure recheck: no startup integration, old mesh research,
full R1/R2 physics rerun, ROOT capability reinvestigation or new physical
acceptance. The small requested quadrature regression tests were exercised.

## Finding dispositions

| Finding | Disposition and independent evidence |
|---|---|
| **SIM-R2-001** — original rotor-transform checker defect | **RESOLVED for the original defect.** The real delivered native file passes. Independently saved 10 mm rotor displacement, rotor scale and fixed mesh-axis mutations each reject without a success receipt. The new related display-edge defect is tracked separately as SIM-R2A-001 below. |
| **SIM-R2-002** — changed CSV encoded with stale provenance | **RESOLVED.** A changed-12345-rad/s CSV and a different valid run both reject before movie/preview/manifest creation. Stale provenance, changed native bytes and changed PNG bytes also reject before output. A fresh positive native receipt permits an actual successful encoding. |
| **SIM-R2-003** — false unchanged-base claim for synthetic fixture | **RESOLVED.** New fixture provenance identifies the base as a software template and explicitly declares changed body/wheel geometry, moments and friction. The current selector and recorded input use `startup-mechanism-fixture-v2.json`. |
| **SIM-R2-004** — cross-platform bitwise archive comparison | **RESOLVED.** Bitwise observer/nonobserver comparison is now same-runtime. Separate historical `qpos/qvel` tolerances are `1e-10/1e-9`, `rtol=0`; energy/residual assertion ASTs are unchanged. Local targeted tests and verified Linux CI are green. |

Resolution of the original four findings does **not** mean that no
implementation finding remains: SIM-R2A-001 is OPEN.
SIM-R1-001's earlier resolution and the R2 fidelity qualifications are unchanged.

## Repeatable witnesses

- [`witness.py`](witness.py): parameter/record identity, test/CI verification,
  encoder positive/negative checks, native invocation and bounded ROOT
  old/new record comparison.
- [`native_witness.py`](native_witness.py): independent world-transform
  check and saved-file mutations, in background Blender only.
- [`witness.json`](witness.json): exact source/output and R1/R2 hashes,
  measured outcomes, failures and CI bindings.

Run from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 simulation/.venv/bin/python \
  simulation/reviews/r2a/witness.py
```

The script creates scratch only under `simulation/runs/reviewer-r2a/`.
It invokes the existing Blender executable with
`--background --factory-startup --threads 2 --python-exit-code 1`.
The ROOT identity comparison reuses the previously reviewed independent
`simulation/reviews/r2/inspect_root.cxx` reader, compiled into R2a scratch.
Neither helper touches a live application or repairs a toolchain.
Witness completion means the experiments completed, including the recorded
false-acceptance counterexample; it is not an automatic PASS.

## Positive closure observations

### Parameters and rebinding

For all three cases, JSON-normalized `body`, `wheels`, `contact`, `integration`,
`gravity_m_s2`, `actuation` and `scenario` are **identical** between
`startup-v3` and `startup-v4`. All **30 NPZ arrays per case** compare exactly;
CSV files are byte-identical. The original and new synthetic model's physical
fields likewise match. Only provenance/selection changed.

The dynamics implementation files `integration.py`, `model.py`, `runner.py`,
`scenarios.py`, `geometry.py` and `numerics.py` have no diff from the R2
boundary. All current run output hashes and the new source bindings were
checked. The six startup movies remain 250 frames at 25 fps, ten seconds
each; the separately labeled detail is still 100× playback of 0.1 simulated
seconds, not ten simulated seconds.

### Native and encoding boundaries

The delivered Blender-v5 file independently reopens; body and rotor world
matrices were compared over **250 frames**, maximum component error
**6.5566×10⁻⁷**, within the declared `1e-6` display margin. Source/schema-2
provenance and the complete new production checker also pass.

Independent saved-file negative outcomes:

| Mutation | Result |
|---|---|
| Rotor center +10 mm | Rejected: center error `0.0100000017 m`; no receipt |
| Rotor Y scale ×1.1 | Rejected: scale error `0.1000000222`; no receipt |
| Fixed X mesh axis changed to identity | Rejected: orientation error `0.7653668354`; no receipt |

The encoder's shared source contract now checks the actual source files,
map poses/times, frame count/FPS and duration before encoding. I used my
fresh positive native receipt, validated all 250 PNG hashes, and actually
reencoded/decoded the movie. It is **byte-identical to the delivered MP4**:

`183b8cf349dddd528758ac8635274125b324a605d13b84cae7ba664bc587b9e8`.

The delivered native SHA is
`b8f10b344627ebeb214caac4a2b816e5cd71d8be9d42b157199366f635e5838f`.

Changed CSV, wrong valid run, stale schema provenance, changed native file
and changed PNG each exited nonzero with the expected source/receipt/hash
error and **no movie, preview or manifest written**. These tests used otherwise
valid complete render prerequisites, not missing-file failures that might
mask an acceptance bug.

### ROOT identity and CI

Both native ROOT trees compare exactly between `root-v3` and `root-v4`, for
all three cases: **2,189 rows × 88 columns** and **80 weighted bins**.
New source CSV/manifest bindings and output hashes match. This is record
identity, not a renewed claim that Cling, graphics, PyROOT or RDataFrame work.
Their documented operation-level limits remain.

All **7 local targeted tests** (`test_quadrature`, `test_blender_contract`)
passed. GitHub CI metadata was independently retrieved:

- [33978039216](https://github.com/ktanino10/ai-hardware-engineering-team/actions/runs/33978039216):
  `21a5344…`, **success**.
- [33978690760](https://github.com/ktanino10/ai-hardware-engineering-team/actions/runs/33978690760):
  `a9109f3…`, **success**.
- [33978933402](https://github.com/ktanino10/ai-hardware-engineering-team/actions/runs/33978933402):
  frozen `8c626ec…`, **success**.

## SIM-R2A-001 — MEDIUM — Display-edge parent inverse bypasses geometry acceptance

**Status: OPEN.** This is in the newly expanded geometry-checking boundary,
not an additional physics or mesh-design investigation.

- **Location:** `simulation/blender/check_replay.py:87–95` checks edge local
  location/scale/quaternion and mesh bounds. Its per-frame world-transform
  loop checks root and rotors, not displayed cube edges.
- **Cause:** Blender's `matrix_parent_inverse` affects an object's world
  transform without changing those local properties. The checker does not
  reject or account for it on display edges.
- **Saved-file witness:** `native_witness.py` opens the delivered file in an
  isolated process, adds 0.01 m X translation to one
  `Visual_cube_edge.matrix_parent_inverse`, saves a scratch `.blend`, and
  reopens it. The displayed edge shifts **0.0099999999 m** in world space,
  while its checked local properties and source provenance remain unchanged.
  The production checker still writes
  **`NATIVE_REOPEN_TRANSFORMS_GEOMETRY_AND_SOURCES_MATCH` for 250 frames**.
  See `witness.json.native_recheck.saved_mutations` entry
  `display-edge-parent-inverse`.
- **Impact:** a false full-geometry native receipt can still be issued for a
  visibly wrong cube envelope. This does **not** mean the delivered v5 file
  is displaced, nor that dynamics changed. The encoder's independent
  native/render-receipt hash check is another barrier; this witness does not
  claim to bypass that barrier or corrupt the delivered movie.
- **Requested minimal correction:** for fixed source-renderer children,
  either reject nonidentity `matrix_parent_inverse` explicitly or validate
  their complete expected world transforms at checked frames. Cover the
  corresponding fixed display-edge/rotation-marker transform invariant, not
  just rotor pivots. Add a saved parent-inverse displacement negative test
  requiring rejection with no success receipt.
- **Re-review:** only that checker/negative test and newly bound receipt
  need a further bounded check. No dynamics, parameter, trajectory, ROOT or
  old-mesh investigation is requested.

## Continuing limits

The tiny contact-gap candidate remains unresolved against contact/envelope
uncertainty. The startup remains a first-kick fixture demonstration, without
capture/stable balance/second-jump proof. Actual motor/brake/source capability,
physical feasibility/safety, hardware gates and Fusion/native assembly
acceptance remain outside these numerical/visualization receipts.

**Current handoff:** the four original fixes are corroborated; correct the
remaining fixed-visual-child transform check before claiming complete native
geometry acceptance.
