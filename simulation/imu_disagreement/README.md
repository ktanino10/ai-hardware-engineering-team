# Offline synthetic IMU disagreement

[Public guide](../../docs/rev5-public-release/software.md) |
[日本語](../../docs/rev5-public-release/software.ja.md)

**SYNTHETIC ONLY / NOT SENSOR HEALTH OR CONTROL APPROVAL**

This public subset exports the original disagreement CLI/API and its exact
minimal estimator/helper dependencies. The Python implementation and original
14 tests are byte-identical to source
`a7b935d1fc199d4bfcb68c8c2218c7649fd7fc91`. This README is a derived public guide.
Python 3.9+ and its standard library suffice; run from the repository root.

```sh
python3 -B -m unittest discover -s simulation/imu_disagreement/tests -v
out="$(mktemp -d)"
python3 -B -m simulation.imu_disagreement \
  --config docs/rev5-six-imu-fault-study-2026-09-13/author/run-001/one-bias/config.json \
  --samples docs/rev5-six-imu-fault-study-2026-09-13/author/run-001/one-bias/samples.jsonl \
  --output-dir "$out/report"
```

Only the exact synthetic one-bias config and 1,201 sample records are included
from the older study, not its full campaign, truth or fault-label sidecars.
The CLI writes input and implementation hashes to `report.json`, plus a
Markdown explanation. Existing output directories are refused. Exit 0 means
comparison was available for every record under the synthetic input contract,
not accuracy or health; exit 2 means unresolved input/comparison or output error.
A partially written directory is not a completed report.

`report.analyze(config, binary_lines)` calls the unchanged `Estimator.step`.
Its `_sample` observation hook copies validated body gyros without changing
the returned sample or upstream validity/clock/continuity policy. "Private
helper" means a Python implementation detail, not an unavailable private file:
all four imported estimator/helper modules are included. No second estimator,
health threshold, selector, weight or calibration is added.

Spread is the maximum Euclidean distance from the existing equal-weight
body-gyro mean, not standard deviation. Residuals require two contributors;
one sensor retains its mean but has null spread/residuals. Invalid or absent
comparisons stay null, never zero/healthy. Presence and rejection are distinct.
Malformed UTF-8 preserves a valid prefix but latches invalid continuity.
Summary statistics are comparable-record weighted, not time weighted.

Common bias can have zero spread; 3-vs-3 ambiguity cannot identify truth.
The internal estimator still runs its existing acceleration/orientation path,
but this wrapper does not emit orientation or connect it to control.
Real register logs, unqualified clocks, missing calibration/extrinsics and
unsupported units are rejected, not repaired. Physical precision and timing
remain UNKNOWN. Inputs are bounded, trusted offline files read into memory.

The original independent review passed this limited wrapper scope and its
14 tests. It did not qualify real sensors or controls. The
[review summary](../../docs/rev5-public-release/software-review.json) and
[new publication checks](../../docs/rev5-public-release/software-checks.json)
are separate. All NO-GO, sidecar/ICD/control, original44=2closed42unfinished and
human/physical holds remain. First-party publication does not invent a license.
