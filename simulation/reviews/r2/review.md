# R2 — Bounded independent startup, diagnostics and adapter review

**Verdict: CONDITIONAL for the named WIP numerical/evidence scope.**

**SIM-R1-001 is RESOLVED for the corrected RK4 diagnostic implementation at
`560c702` and the new evidence.** The startup model genuinely spins from rest
and applies finite internal brake effort. Current MuJoCo outputs, the delivered
Blender-v4 replay and native ROOT data reproduce the scoped checks below.

There are **three open MEDIUM defects** (two Blender verification/provenance
defects and one CI test-portability defect) and **one LOW synthetic-input
provenance defect**. No CRITICAL/HIGH physics defect was identified.
The currently delivered Blender poses/video were independently
checked despite the checker defects; this does **not** validate its future
verification/encoding pipeline. Correct the defects before relying on those
automated receipts for new or changed evidence.

The synthetic contact-gap candidate remains
**NUMERICALLY_UNRESOLVED_CONTACT_ENVELOPE**, not resolved physical flight.
No stable balance, capture, second jump, real brake/motor capability, physical
feasibility/safety, Design Complete, firmware, procurement or Fusion approval
is granted.

## 1. Reviewer, frozen scope and methods

- **Reviewer:** GitHub Copilot, independent Simulation Reviewer in the same
  independent R1 reasoning context. I did not author the implementation or fix
  it during this review. The real profile/skill contract is used even though
  the role is not registered in this tool schema.
- **Date:** 2026-09-06 JST. Main witness execution:
  2026-09-05 16:11:26–16:15:06 UTC.
- **Reviewed HEAD:** `08adc390a391acb5ad654be7cd279a14f1e780a4`,
  branch `ktanino10-cube-physics-simulation`.
- **Physics/diagnostics/model source:**
  `560c70279c0916068abd9a54b76db4f0f920c990`.
- **Blender final framing source:**
  `bfb5ffbc7f9ad2878fd52f4ce8544ada54ebc428`.
- **Secondary mechanism source:** `ktanino10/attitude-control-study`,
  `a927d1ae3409ba143631077824cdf3c904ea27b9`.
- Tracked tree was clean before reviewer writes. Only R2 review files and
  reviewer-R2 scratch were written. R1, implementation, models and all
  historical/current delivered evidence remain unchanged. No agents/factory,
  commits/PR/merge operations, physical work or global toolchain changes.

R1's established source/mass/inertia review is reused. **I did not repeat the
STL or old frozen-bundle research.** The three newly cited mechanism-note
files were hash-verified at the supplied commit. Their startup description is
secondary guidance, not manufacturer torque/brake data; its ideal
instantaneous-lock/fixed-pivot argument was not substituted for free-contact
system dynamics. No figures/PDFs were copied or note code executed.

### Surface disposition

| Surface | Assessment |
|---|---|
| RK4 work/impulse correction | Reviewed, independently corroborated; R1 finding resolved |
| Optional finite-brake startup, annular fixture, changed diagnostics | Reviewed; conditional fixture behavior, not hardware validation |
| `evidence/startup-v3/`: three runs, six movies, plots, maps, summaries, 48-row numerics | Reviewed; all three full runs rerun exactly |
| Blender adapter and `blender-replay-v4/startup-mechanism-fixture/` | Source reviewed; native file independently reopened, all 250 poses/geometry checked, rendered/decoded agreement checked; two defects below |
| `root/` and three `root-v3/` exports | Source reviewed; compiled export and independent native readback exercised; no JIT/graphics claim |
| STARTUP/README/simulation contract/current landing | Reviewed for scope, duration, classification and approval boundaries |
| Linux CI run `33976353506` on frozen HEAD | Log independently verified; 29/30 passed, one cross-platform bitwise-baseline failure; SIM-R2-004 |
| R1/`initial-v1` | Preserved; only the bounded old fall witness used to assess R1-001 |
| Blender-v1 | Historical three-second Cycles comparison; excluded as a current ≥10-second deliverable and **never R1-reviewed** |
| Blender-v3 | Superseded tight-framing version; excluded from current framing acceptance |
| Live/unsaved Blender scenes, PyROOT, RDataFrame, Cling frontend, ROOT graphics, physical/Fusion work | Not exercised/approved by R2 |

### Durable reproducibility

- [`witness.py`](witness.py): bounded physics, artifacts, numerical sensitivity,
  source hashes, media and adapter-positive/negative experiments.
- [`inspect_blend.py`](inspect_blend.py): independent native world-pose,
  annular-geometry and framing check plus the wrong-center negative witness.
- [`inspect_root.cxx`](inspect_root.cxx): independent read-only scalar-tree
  reader; no reuse of the exporter's branch-address/readback implementation.
- [`witness.json`](witness.json): all numerical values, 95 in-scope file hashes,
  unchanged R1 hashes, reviewer source hashes, native/movie checks and false
  acceptance witnesses.
- [`ci-portability.json`](ci-portability.json): subsequent independently
  retrieved CI run/head binding, job-log hash and sanitized failure/runtime
  excerpts for SIM-R2-004. The original local witness remains unchanged.

From repository root:

```sh
mkdir -p simulation/runs/reviewer-r2/test-work
(
  cd simulation
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests \
  TMPDIR="$PWD/runs/reviewer-r2/test-work" \
  MPLCONFIGDIR="$PWD/runs/reviewer-r2/mpl-cache" \
  .venv/bin/python -m unittest -v test_quadrature test_startup
)
PYTHONDONTWRITEBYTECODE=1 simulation/.venv/bin/python \
  simulation/reviews/r2/witness.py
```

**Observed:** all **9 targeted new tests** passed in 76.669 s. The independent
witness completed, including the expected negative-test false acceptances.
`witness_complete` means the experiments completed, **not** blanket acceptance.
The full old test suite/STL investigation was not repeated.

**Subsequent CI evidence:** [run 33976353506](https://github.com/ktanino10/ai-hardware-engineering-team/actions/runs/33976353506),
job `101333623262`, is bound to the same frozen `08adc390` HEAD. I retrieved
its metadata and job log rather than relying only on the author's report.
Ubuntu x64/Python 3.14.7 ran **30 tests: 29 passed, one failed**. The sole
failure is the historical cross-platform `assert_array_equal` in
`test_quadrature.py:21`; maximum absolute `qpos` disagreement is
**2.2565283×10⁻¹⁴**. This does not contradict the local same-runtime exact
reproductions. It is not failure of the work/residual/startup guards and
**does not reopen SIM-R1-001**. Linux execution was CI's, not a claimed local
Linux rerun by this reviewer.

Existing runtimes were verified: MuJoCo 3.12.0; Blender 5.1.1 standalone;
ROOT 6.38.04 with `root-config` and `c++`; ffmpeg/ffprobe. Blender ran with
`--background --factory-startup --threads 2 --python-exit-code 1`, exclusively
in a separate process. The user's unsaved application was not accessed.
The ROOT Python wrapper was inspected, not invoked into its default
`runs/root-build`; equivalent compile/export commands were confined to R2
scratch.

## 2. SIM-R1-001 disposition — RESOLVED, not waived

The changed `integration.advance` captures the four **actual** RK4 evaluation
states read-only, removes the callback in `finally`, reevaluates their
forces/warmstarts in a separate `MjData`, and integrates with 1:2:2:1 weights.
This matches the engine's documented evaluation order. Pre-existing callbacks
are rejected without replacement. I tested both this rejection and cleanup
after an injected step exception.

Most importantly, the new calculation matches **R1's previously independent
stage-work values**, not just the new author's tests:

| Old proxy fall timestep | R2 maximum all-step energy/work residual | Difference from R1 independent stage-work result |
|---|---:|---:|
| 2 ms | 0.041276785492084 J | 8.89×10⁻¹⁶ J |
| 1 ms | 0.008584363641517 J | 8.89×10⁻¹⁶ J |
| 0.5 ms | 0.001445799730837 J | 0 J |

At 2 ms **all old physical arrays are identical**; only the corrected work
accounting and added diagnostic fields differ. The maximum all-step,
recorded-grid and final residuals are distinguished; method and explicit
uncalibrated/not-physically-qualified status are present. This is correction
and demonstrated convergence, not hiding the residual or loosening its bound.

The nonzero remaining values are integrator/solver errors, not physical
dissipation. Resolution applies to the corrected RK4 path/new evidence, **not
retroactive accuracy of the old endpoint-work records in `initial-v1`**.
The historical R1 report is intentionally left untouched.

## 3. Genuine startup and internal-brake accounting

### Changed model and force path

The reference and Rev5 proxy retain their old body, wheels and floor law.
The 100 mm fixture is distinct: 0.1 kg uniform body plus three 0.08 kg annuli;
its mass totals 0.34 kg. I independently checked:

```text
I_axis = m(R_outer² + R_inner²)/2 = 0.000113 kg m²
I_transverse = I_axis/2 + m h²/12 = 0.000056606666667 kg m²
```

The visual mesh does not supply mass; positive analytical inertias remain
explicit. Geometry/centers are assumptions, not adopted hardware. The
synthetic provenance wording defect in §7 does not change those actual
numbers or the visibly distinct model classification.

The three delivered startup cases start with **all nine velocities zero** on
a face. Motor speed feedback runs, then coasts, then finite rotor-joint dry
friction engages. Only rotor DOF friction-loss entries 6–8 change; no free-root
friction, external applied force, equality pivot or velocity/pose reset was
found. Brake ramp capacity is held over each integration step; halving the
step separately checks this discretization. The requested 5 ms capacity
comparison is not a forced stopping time.

For an independent **force-path diagnostic**, not a startup initialization,
I placed three already-moving hinges in free space with body rate zero and
applied dry-friction capacities `(0.012,0.010,0.008) N m`. Speeds
`(40,−30,20) rad/s` give hinge efforts `(-0.012,+0.010,-0.008) N m`.
With R1's directly aggregated locked inertia `J` and axial matrix `D`:

```text
alpha_body = -(J-D)^-1 tau
alpha_relative = D^-1 tau - alpha_body
```

Predicted body acceleration is approximately
`(+1.1092078655,−0.9320046433,+0.7380783184) rad/s²`.
Body/hinge acceleration errors were **7.0×10⁻¹⁵ / 9.7×10⁻¹³ rad/s²**.
Free-root constraint force/torque stayed zero. Over 0.15 s the independent
linear/angular momentum drifts were **5.30×10⁻⁹ kg m/s / 4.68×10⁻¹⁰ N m s**.
These meet the new finite-brake test's `1e-8` margin, but **are not the tighter
R1 smooth-free-space `1e-10` result**; finite constraint-solve error remains.

### Actual outputs independently reproduced

All three full ten-second runs reran with **every NPZ array and XML identical**.
Every one of the **87 CSV columns × 2,189 rows per case** matched NPZ.
Direct part-wise kinetic/potential energy, linear momentum and COM angular
momentum sums agreed with logged values; worst errors were
**2.67×10⁻¹⁴ J**, **1.95×10⁻¹⁶ kg m/s**, and **1.14×10⁻¹⁵ N m s**.

| Measured quantity | Reference 240 mm | Partial Rev5 240 mm | Synthetic 100 mm |
|---|---:|---:|---:|
| Pre-brake relative X speed, rpm | 3000.0000 | 3000.0000 | 2999.6769 |
| Pre-brake relative X axial momentum, N m s | 0.01413717 | 0.01413717 | 0.03549617 |
| First observed `<1 rad/s`, after ramp start | 6.0 ms | 6.0 ms | 5.9 ms |
| Maximum rotation from initial | 0.028959° | 0.001674° | 113.803239° |
| Maximum all-step energy residual | 3.791×10⁻⁶ J | 3.778×10⁻⁶ J | 1.079×10⁻⁵ J |
| Maximum COM-H/ground-impulse residual | 8.807×10⁻¹⁰ N m s | 1.067×10⁻¹⁰ N m s | 1.748×10⁻⁹ N m s |
| Modeled brake dissipation | 2.219880 J | 2.220622 J | 5.371298 J |
| Floor contact work on assembly | −0.001138 J | −0.000877 J | −0.203954 J |

The 20 ms motor FIFO, zero-start spin-up, 3.5 s brake command, 3.52 s ramp
start and finite capacity sequence are observable in the records. The 3000
rpm value remains **target-only**, not rated/safe. No actual driver or
manufacturer brake waveform has been qualified.

The brake's generalized work is a **subset of total constraint work**.
Subtracting brake work isolates floor work; adding it a second time would
produce a spurious multi-joule energy error. COM angular impulse correctly
uses the free-root world moment translated from body origin to total COM.
The floor can exchange angular impulse, so total wheel momentum cannot simply
be assigned to the body using the secondary note's instantaneous fixed-pivot
idealization.

Reference and proxy fail to reach edge attitude. The synthetic fixture visits
the edge-attitude band and tumbles. That observation is **not capture, stable
balance, a second jump or evidence that the actual Rev5 mechanism is
universally impossible**.

## 4. Tiny gap: criterion, timing and sensitivity

I independently transformed all eight box corners for every recorded state.
The candidate criterion is exactly: **zero geometric contacts**, total normal
force **≤1e-8 N**, and **every corner >0.1 mm** above the plane.
It is not merely zero loaded-contact count.

For the original synthetic model:

- Maximum minimum-corner height: **0.182298916 mm**.
- Consecutive qualifying observations: **183**, from **3.5391 to 3.5573 s**.
- Observed span: **18.2 ms**, not `183 × 0.1 ms = 18.3 ms`.
- Adjacent nonqualifying samples: **3.5390 and 3.5574 s**.
- These brackets are observations, not continuous-clearance proof.
- Recorded impact penetration: **3.379251 mm**.

Separate diagnostic comparisons through 4.1 s:

| Comparison | Maximum gap of tested box | First candidate observed span | Max rotation |
|---|---:|---:|---:|
| 0.1 ms, Newton 50 | 0.182299 mm | 18.2 ms | 113.803° |
| 0.05 ms, Newton 50 | 0.181758 mm | 18.1 ms | 113.758° |
| 0.1 ms, Newton 100 | 0.182299 mm | 18.2 ms | 113.803° |
| 0.1 ms, CG 100 | 0.182307 mm | 18.2 ms | 113.938° |
| Contact margin +0.1 mm | 0.280017 mm | 26.8 ms; additional intervals | 113.798° |
| Contact margin +0.2 mm | 0.377757 mm | 26.5 ms; additional intervals | 113.713° |
| Collision-box envelope +0.2 mm per side | 0.173587 mm | 16.7 ms | 112.263° |

These are **reviewer sensitivity experiments**, not changes to frozen inputs
or tuning for success. Margin changes shift where the soft law generates
force and therefore change the dynamics, not just the Boolean threshold.
The expanded-box run initially has the corresponding small penetration
because the nominal initialization is retained; it settles during the
three-second spin-up. Its gap is measured against the **expanded** box.

At fixed geometry the tiny numerical candidate is reproducible under the
tested refinement, but contact assumptions materially affect gap and event
duration. Applying just **0.2 mm unmodeled-envelope uncertainty** to the
original trajectory makes maximum residual clearance **−0.01770 mm**;
the displayed **2 mm capsule radius** exceeds the candidate by an order of
magnitude. Actual envelope uncertainty is UNKNOWN. **Retain the unresolved
status; do not call this resolved physical flight.**

The half-step energy residual through 4.1 s drops from `1.0720e-5` to
`1.1105e-6 J`. CG gives `1.0904e-4 J`, exceeding the author's `5e-5 J`
startup Newton regression guard even though the gap is similar: **do not
generalize that energy-accuracy margin to every solver**.
Separately thinning the half-step output from 1,599 to 519 rows leaves final
state and all-step work residual exactly unchanged. Output thinning is not
integration refinement.

## 5. Actual movies, plots and Blender replay

All **six MuJoCo movies** decoded without error: H.264, 960×720,
**250 frames / 25 fps / 10 seconds**. Exact source-row pose hashes and times
were checked across all maps:

- Full motion covers **[0,10) simulated seconds**, real-time playback.
- Detail covers **[3.48,3.58) simulated seconds** in ten playback seconds:
  **100× slow**, explicitly labeled. Its last frame is 3.5796 s, not ten
  simulated seconds.

Selected first/brake/last decoded scenes were independently rendered from
their recorded states; maximum mean absolute RGB discrepancy was **0.881**
on the 0–255 scale, consistent with lossy encoding. Both plot types for all
three cases regenerated **byte-for-byte**. I inspected decoded contact sheets
and the actual startup plot. Model size/mass labels distinguish the 100 mm
fixture from the 240 mm cases; the views say **“no loaded contacts,” not
“airborne.”** No padding, looping or hand-authored success pose was identified.

For Blender-v4 I independently reopened the actual native file and checked
all **250 integer frames**, including:

- body world position/rotation;
- all three rotor parent/center mappings;
- analytical axis rotations and **all 192 annular vertices per rotor**;
- unit scales, absence of Blender rigid-body dynamics;
- camera XY-follow/fixed-initial-Z behavior and frame containment.

Maximum center and annular world-vertex errors were **3.08×10⁻⁸ m** and
**4.72×10⁻⁸ m**; maximum rotation-matrix component error was **4.18×10⁻⁷**,
within the declared `1e-6` display precision. Minimum screen margins for cube
corners were left/right/bottom/top **29.79% / 31.34% / 15.23% / 8.13%**.
I rerendered the native frames and compared seven decoded movie scenes:
RGB mean absolute error **0.750–0.981**. Thus the delivered v4 framing and
integer-frame poses are supported independently of its deficient checker.

Bindings include:

- Native `.blend`:
  `4c287479d3b27d7697b25d545d6b2a50b5d31a6599a4dae62e0b7b2e3e0f760f`.
- Blender MP4:
  `9caa50e686d343fcfe66a6b9f15cc00f9a74b246bda794ecb816be36fb9401c9`.
- Referenced synthetic source manifest:
  `50b708b89e91e33c8371618cc40f382fef868ba95ff35f662e1d7f0da4d67dd9`.

**Between-frame interpolation was not validated as physics.** Blender is
record replay, not an independent dynamics simulation or Fusion artifact.
Native background reopen/render was exercised; interactive GUI playback and
the user's live scenes were not.

## 6. CERN ROOT: native data interoperability only

The exporter uses stable, preallocated double storage for its branch
addresses, fills/writes before that storage dies, and resets addresses before
cleanup. Its CSV checks reject missing/duplicate/invalid column names,
nonfinite/nonnumeric values, wrong row width and nonincreasing time.

I compiled the existing exporter in R2 scratch and independently read **both
the delivered and regenerated files** with `inspect_root.cxx`. It uses scalar
leaves rather than the author's branch-address verification. For all three:

- **2,189 × 87 source values**, plus `sample_dt_s`, read back exactly;
- second tree: **80 bins × 3 double fields**, edges and duration weights
  independently checked;
- total weights **9.999999999990033 s**; final row has zero weight;
- dense braking window contributes **0.120000000000253 s**, not one vote per
  high-rate row.

| Case | Time-weighted mean X rpm | Naïve row mean X rpm |
|---|---:|---:|
| Reference | 942.443924 | 1015.273417 |
| Partial Rev5 | 942.444179 | 1015.284787 |
| Synthetic | 779.590874 | 939.582783 |

These are descriptive **left-hold** statistics, not brake-work reintegration.
ROOT binary hashes differ between fresh exports because metadata/UUIDs can
change; numerical equality was checked rather than demanding binary identity.

The native programs again emitted the documented missing-header/Cling
diagnostics while returning successful native reads/exports. Logs retain
those messages. **No successful Cling frontend, RDataFrame, PyROOT, TCanvas
or ROOT PNG operation is claimed**. No global SDK repair/install was
attempted. ROOT is data exchange/analysis, never the dynamics engine.

## 7. New findings and required corrections

### SIM-R2-001 — MEDIUM — Native checker ignores rotor world position/geometry

- **Location:** `simulation/blender/check_replay.py:29–46`.
- **Status:** OPEN; affects reliance on the native “poses match” receipt.
- **Evidence:** the checker compares root translation/orientation and each
  rotor's **local quaternion only**. It never checks rotor center, parent
  transform, scale or mesh orientation/geometry.
- **Repeatable witness:** `inspect_blend.py` first validates the delivered
  file independently, then saves a scratch copy with
  `WHEEL_X_REPLAY.location.x += 0.01`. Running the author's checker on that
  copy still reports **NATIVE_REOPEN_POSES_MATCH_COMPUTED_RECORDS, 250 frames**.
  See `witness.json.blender.negative_wrong_wheel_center`.
- **Impact:** a rotor rendered **10 mm from its recorded/model center** can
  receive a “matching poses” receipt. This is not an accusation that the
  delivered v4 file has that defect; R2's independent check establishes that
  the unmutated file is correct.
- **Requested fix:** compare complete expected world transforms, including
  all three centers, parenting, scales and fixed annulus/cylinder axis
  alignment; validate source input/map bindings before comparison. Add a
  negative regression that shifts a rotor center and must fail. Independently
  re-review the corrected checker/receipt before trusting future receipts.

### SIM-R2-002 — MEDIUM — Encoder accepts changed CSV under old provenance

- **Location:** `simulation/blender/encode_replay.py:18–21,29–32,43–49,61–68`.
- **Status:** OPEN; affects source/media provenance and truthful annotations.
- **Evidence:** the encoder reads the supplied CSV without comparing it with
  `provenance["trajectory_csv_sha256"]` or validating the supplied run against
  its recorded source manifest. It then copies old source identifiers into
  the new output manifest.
- **Repeatable witness:** `witness.py:native_blender()` changes every X speed
  to **12345 rad/s** in a **scratch copy only**, retaining correctly rendered
  source poses and original provenance. Core `verify_current` rejects that
  CSV; the Blender encoder nevertheless exits **0** and creates a new movie
  with false speed labels while claiming the original source manifest hash
  `50b708b8…`.
  Original CSV SHA is
  `8dfd08796a46a2a3a9429447c11523c7e05239f362e2cdd0fa4dee816814d59c`;
  mutated CSV SHA is
  `9e74c6e64116704fc6f7019d17545e725ebb29b30d81d9ea9d288ce780e35b03`.
  Results are under `witness.json.blender.negative_changed_source_csv`.
- **Impact:** a stale or wrong run passed to the second pipeline stage can
  generate credible source labels for different numerical annotations. The
  actual delivered MP4 was separately checked and is not claimed corrupted.
- **Requested fix:** fail closed **before writing output** on source
  manifest/CSV/input/scenario/map mismatches. Validate frame count, row
  index/time/pose correspondence, FPS and ≥10-second requirement at this
  boundary too. Bind the bytes actually used; do not simply propagate old
  hashes. Add mutation/wrong-run regression tests and independently re-review.

### SIM-R2-003 — LOW — Synthetic provenance falsely says base mass/floor unchanged

- **Location:** `simulation/cube_sim/braking.py:114–117`;
  `models/startup-mechanism-fixture.json` and its recorded `input.json`,
  `provenance.actuation_and_contact`.
- **Status:** OPEN; a metadata contradiction, not an identified physics bug.
- **Evidence/reproduction:** compare this field with its referenced
  `base_model` (`reference.json`). The field says **“Base mass moments and
  floor law are unchanged”**, but the synthetic branch changes side
  240→100 mm, body mass 1→0.1 kg, wheel mass/geometry/inertia/centers, and
  floor friction 0.6→1.2. Those changes are otherwise explicitly disclosed.
- **Impact:** machine/human provenance consumers receive mutually
  inconsistent derivation claims even though visible identity and actual
  parameters are correct.
- **Requested fix:** use fixture-specific provenance describing the changed
  assumed geometry/moments/friction and the base file's role as a template.
  Retain the unchanged-base statement only for the actual reference/proxy
  startup derivatives. Version affected metadata/evidence rather than
  editing historical records in place.

### SIM-R2-004 — MEDIUM — Cross-platform bitwise archive comparison breaks CI

- **Location:** `simulation/tests/test_quadrature.py:13–21`, particularly line
  21's `assert_array_equal(result[key], old[key])` against the committed
  macOS `initial-v1` archive.
- **Status:** OPEN; test portability/CI failure, **not** a physics or
  contact-energy-threshold defect.
- **Evidence:** frozen-HEAD run `33976353506`, job `101333623262`, reports
  29 passes and this sole failure on Ubuntu x64/Python 3.14.7. For `qpos`,
  1,922/2,010 elements differ bitwise, but the maximum absolute difference
  is only **2.2565283e-14**. Large relative differences in near-zero entries
  are not meaningful physical errors. Exact head, log SHA-256 and excerpts
  are preserved in `ci-portability.json`.
- **Reproduction:** inspect that run's failed-test log, or run the existing
  unmodified test on the recorded Linux environment. Its purpose is observer
  noninterference, but it confounds that with cross-platform bit identity.
- **Impact:** the default Linux CI job fails despite all other energy,
  contact, startup, XYZ and sensitivity guards passing. This must be fixed
  before treating the revision's CI as passing.
- **Requested surgical correction:** compare observer-enabled integration
  with ordinary `mj_step`/`mj_forward` **on the same runtime and identical
  inputs**, retaining bitwise equality for their physical trajectories.
  Separately compare historical cross-platform `qpos`/`qvel` using explicit,
  tight, justified numerical tolerances. Keep the energy/residual criteria
  unchanged; do not regenerate historical evidence, skip the regression or
  replace the same-runtime noninterference check with a loose comparison.
- **Re-review disposition:** the proposed test-only split is appropriate.
  Verify the same-runtime control and historical comparison locally and in
  Linux CI, then request a bounded test-only recheck. No physics/model/media
  revision is justified by this roundoff-sized mismatch.

## 8. Limits and handoff

- Current first-kick behavior is valid only for the explicitly modeled inputs.
  Actual brake timing/capacity, motor/source/regen, complete Rev5 mass and
  hardware contact/envelope data remain unknown.
- The tiny box gap is reproducible numerically under tested step refinement,
  but insufficient to establish physical flight. Contact-margin/envelope and
  solver-energy sensitivity remain material.
- Finite brake constraint residuals are measurable and must not be equated
  with R1's tighter unconstrained invariants or physical heat/impact accuracy.
- Blender-v4 is independently supported **as delivered**, but its automatic
  acceptance/encoding path requires SIM-R2-001/002 corrections. Native ROOT
  data exchange passes without implying interpreter/graphics health.
- Correct SIM-R2-001/002, the synthetic provenance statement and the
  SIM-R2-004 test-portability defect, then request
  a **bounded recheck** of those changes and newly bound outputs. Do not
  change the physical model to manufacture success or reuse this verdict for
  an unreviewed revision.

**R1 remains unchanged; no shared hardware finding or human gate is closed.**
