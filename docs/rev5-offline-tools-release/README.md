# Rev5 offline tools release

[English](README.md) | [日本語](README.ja.md) | [Public entry](https://ktanino10.github.io/ai-hardware-engineering-team/)

**SYNTHETIC ONLY / NOT SENSOR HEALTH OR CONTROL APPROVAL**

This independently runnable slice contains the existing IMU disagreement CLI,
four estimator/helper modules, its unchanged 14 tests, the exact synthetic
one-bias fixture, and a **C1 aggregate summary only**. It contains no firmware
or C1 production tool. It is separate from the blocked full-software
[PR #80](https://github.com/ktanino10/ai-hardware-engineering-team/pull/80),
not a fix, suppression or clearance of that PR's firmware alerts.

## Run the existing example

Use Python 3.9+ from a public checkout's repository root. Only the Python
standard library is needed; no package install, Git history, network, SDK,
device, truth sidecar or private source is required at runtime.

```sh
python3 -B -S -m unittest discover -s simulation/imu_disagreement/tests -v
out="$(mktemp -d)"
python3 -B -S -m simulation.imu_disagreement \
  --config docs/rev5-six-imu-fault-study-2026-09-13/author/run-001/one-bias/config.json \
  --samples docs/rev5-six-imu-fault-study-2026-09-13/author/run-001/one-bias/samples.jsonl \
  --output-dir "$out/report"
```

`-S` disables site packages to make the standard-library-only boundary explicit.
The new output directory contains `report.json` and `report.md`. Existing
directories are refused; a partially written directory is not a completed
report. Exit **0** means every record was comparable under the synthetic
contract, not healthy or accurate. Exit **2** means unresolved input/comparison
or an output error; inspect the report and stderr rather than accepting a
partial result. The CLI reads bounded, trusted offline input into memory.

The preserved fixture has **1,201 comparable records**, no unresolved records,
maximum spread approximately **0.1 rad/s**, and sample-weighted mean spread
approximately **0.08334721 rad/s**. These are fixture outputs, not sensor
specifications. [example-summary.json](example-summary.json) retains the actual
summary in the existing report shape without publishing a large duplicate
record stream. Full reports include input and implementation SHA-256 hashes
and the Python version; their whole-file hash can vary with that version or
input path spelling. Compare the source/input hashes and numerical meaning,
not a cross-version byte-hash promise.

## Interpret the report

`records` retains accepted IDs, separately observed presence/absence, rejection
reasons, input time labels, body-frame gyro mean, Euclidean residual vectors
and their norms. Spread is the **maximum Euclidean distance from the existing
equal-weight mean**, not standard deviation or orientation error.

| Contributors / validity | Output meaning |
| --- | --- |
| At least two accepted, valid contributors | `COMPARABLE_SYNTHETIC`; residuals and spread available |
| One accepted, valid contributor | Mean retained; spread/residuals `null`, comparison `UNRESOLVED` |
| Zero accepted, or invalid continuity/input | Unavailable comparison stays `null`, never zero/healthy |

Presence does not imply acceptance. Malformed UTF-8 keeps a valid prefix but
latches invalid continuity; missing, stale, duplicate, reset, out-of-order
and gap cases retain the original rejection policy. Summaries are
comparable-record weighted, not time weighted; no interpolation repairs gaps.
Shared bias can produce zero spread. A 3-vs-3 split does not identify truth.

Only declared synthetic SI units, body-frame transforms, calibrated-identity
inputs and exact synthetic clocks are supported. Physical accuracy, latency
and calibration remain **UNKNOWN**. The unchanged helper still runs its
existing acceleration/orientation path internally; this wrapper neither emits
orientation nor connects it to control. No health threshold, auto-exclusion,
weight, calibration, attitude/control or sidecar behavior has been added.

## C1 is a summary, not a purchasing dataset

The byte-preserved [C1 JSON](../rev5-public-release/software-c1-summary.json)
records **10 catalogue candidates, 2 unknown-product requirements, 23 gaps,
103 source observations and 0 adopted candidates**. Quantity is **UNKNOWN**,
purchase readiness is **CLOSED**, and physical permission is **NOT_GRANTED**.
These dated observations are not live catalogue checks or additive part
quantities. The private sealed C1 inputs, CLI and production closure are not
included or reconstructed. This JSON is not a replacement input dataset or
an orderable BOM.

## Provenance, checks and publication boundary

[intake.json](intake.json) freezes the coordinator-selected objective and
positive source-object list. All 11 code/test/fixture/summary exports come
unchanged from public commit
`6a86f5e71934c78435ca31f3f696da48de5ddd5a`; the Python and fixture bytes also
retain the original authored revision recorded in [provenance.json](provenance.json).
[manifest.json](manifest.json) binds the finite export and derived reader/CI
files; its own hash is bound by its containing Git commit, not recursively.
No full source branch or private ancestry is merged.

The original limited independent review passed the IMU wrapper scope and
14 tests. Its attribution, broader historical test counts and explicit
**NOT_RUN** distinctions are preserved in the provenance record and linked
immutable public review summary. This publication's closure checks and
example are **publisher/CI evidence, not a new independent review**.

```sh
python3 -B -S -m unittest discover -s tools/tests -p 'test_rev5_offline_publication.py' -v
```

The focused check covers hashes, safe exact paths, imports, the unchanged
14-test suite, an isolated public-file-only execution, missing-helper failure,
synthetic semantics, C1 boundaries, EN/JA links and preservation of v2/v3/media.
Existing numerical CI is retained; the offline step is additive.
[checks.json](checks.json) is the local PR-opening check snapshot, not proof of
a later PR merge or Pages deployment. Those require their own dated remote
readback. Pages still publishes only `visualization/`; landing links use real
GitHub documentation URLs, not paths outside the deployed site root.

The released [v3 plus six Blender clips](../rev5-v3-media-release/README.md)
and [v2](../rev5-public-release/README.md) remain byte-preserved. No firmware,
vendor/Bosch/CRT/N8R8/SDK, private C1 closure, raw source notes, native CAD,
media, device or serial work is included. Owner-authorized first-party
publication does not invent a project or downstream license. Rollback is a
normal reviewed revert of this slice followed by unchanged required CI and
the existing Pages workflow, not a protection override.

**Unchanged holds:** original44 = **2 closed / 42 unfinished**; WIP /
NOT ASSEMBLY READY / NO-GO / 3C8H / REQ409 / strict-pro / 39UNKNOWN;
P1/C1/D1; held control/sidecar/ICD and all source, human and physical gates.
This finite software publication grants no assembly, purchase, fabrication,
power-on, flash, motor-operation or safety permission.
