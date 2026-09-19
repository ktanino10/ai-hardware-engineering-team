# Offline synthetic IMU disagreement

[English usage and provenance](../../docs/rev5-offline-tools-release/README.md) |
[日本語](../../docs/rev5-offline-tools-release/README.ja.md)

**SYNTHETIC ONLY / NOT SENSOR HEALTH OR CONTROL APPROVAL**

The original CLI, four estimator/helper modules, 14 tests and one-bias fixture
are byte-preserved. Python 3.9+ and its standard library suffice; run from the
repository root, including in a public-file checkout without Git history.

```sh
python3 -B -S -m unittest discover -s simulation/imu_disagreement/tests -v
out="$(mktemp -d)"
python3 -B -S -m simulation.imu_disagreement \
  --config docs/rev5-six-imu-fault-study-2026-09-13/author/run-001/one-bias/config.json \
  --samples docs/rev5-six-imu-fault-study-2026-09-13/author/run-001/one-bias/samples.jsonl \
  --output-dir "$out/report"
```

The CLI writes `report.json` with input/implementation hashes and `report.md`.
It refuses existing output directories. Exit 0 means comparable synthetic
records, not health; exit 2 means unresolved input/comparison or an output
error. A partial output directory is not success. Inputs are bounded, trusted
offline files loaded into memory.

`report.analyze(config, binary_lines)` calls the unchanged `Estimator.step`.
Its `_sample` observation hook copies validated body gyros without changing
upstream validation, clocks, continuity, acceleration or orientation behavior.
The wrapper does not emit orientation or connect it to control. The private
hook is an implementation detail of the included, pinned Python helper,
not a private file or stable plugin API.

Spread is maximum Euclidean residual from the equal body-gyro mean.
Fewer than two accepted contributors have null spread/residuals, never a
healthy zero error. Presence differs from acceptance; invalid continuity
stays invalid. Shared bias can hide behind zero spread, and 3-vs-3 cannot
identify truth. No health threshold, auto-exclusion, calibration or control
is introduced. Synthetic SI/body/exact-clock qualifications and all existing
engineering/physical holds remain.

See the linked guides for the actual example summary, C1-only aggregate,
immutable source/review attribution, original NOT_RUN boundaries and focused
publication checks. The blocked firmware PR and existing visual releases
are not altered by this independent offline slice.
