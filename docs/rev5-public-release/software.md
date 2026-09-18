# Rev5 public software follow-up

[English](software.md) | [日本語](software.ja.md) | [Original v2 release](README.md)

**DERIVED_PUBLIC_EXPORT / WIP / NOT_FOR_FLASH**

This is a finite software publication, not completion of Rev5. The existing
[whole-assembly v2](https://ktanino10.github.io/ai-hardware-engineering-team/rev5-full-assembly-v2/index.html)
and its original release manifest are unchanged. No active v3 or Blender work
is included.

## Included and withheld

| Surface | Public result | Remaining boundary |
| --- | --- | --- |
| C1 readiness | [Derived aggregate summary](software-c1-summary.json): 10 exact catalogue candidates, 2 unknown-product requirements, 23 gaps, 103 source observations | **0 adopted**, quantity **UNKNOWN**, purchase readiness **CLOSED**, not orderable. The CLI, production dataset and sealed private power-return input closure are withheld. The summary is not a replacement input dataset. |
| Synthetic IMU disagreement | [CLI and API](../../simulation/imu_disagreement/README.md), unchanged minimal estimator/helper closure, original 14 tests and exact synthetic one-bias config/samples | Offline synthetic SI/body-frame/exact-clock gyro reporting only. No real-data, health, auto-exclusion, weighting, calibration or control qualification. |
| N8R8 evaluation | [Opt-in source profile](../../firmware/bench-imu-01-rev5/evaluation/n8r8/README.md), unchanged measurement/pin/vendor inputs, licenses and portable source tests | **NOT_FOR_FLASH**. The measurement subset does not resolve the full Rev5 **FG35/36/37 conflict**, even with PSRAM disabled. No SDK, tool installation, ELF/BIN or device evidence is distributed. |

The original 44 items remain **2 closed / 42 unfinished**. Complete BOM and
motor power are **NOT_DONE**. NO-GO / 3C8H / REQ409 / strict-pro / 39UNKNOWN,
P1/C1/D1, RRT, sidecar/ICD/control and every human/physical hold remain.
Publication grants no purchase, wiring, assembly, energization, first flash,
motor operation, fabrication or safety approval.

## Run from a public checkout

Use Python 3.9+ from the repository root. These new Python surfaces use only
the standard library; the broader simulator's dependencies are not required.
No private Git object, original review receipt or hidden file is needed.

```sh
python3 -B -m unittest discover -s simulation/imu_disagreement/tests -v
python3 -B -m unittest discover -s tools/tests -p 'test_rev5_public_software.py' -v

out="$(mktemp -d)"
python3 -B -m simulation.imu_disagreement \
  --config docs/rev5-six-imu-fault-study-2026-09-13/author/run-001/one-bias/config.json \
  --samples docs/rev5-six-imu-fault-study-2026-09-13/author/run-001/one-bias/samples.jsonl \
  --output-dir "$out/report"
```

The preserved fixture has 1,201 synthetic records. The CLI writes a fresh
`report.json` and `report.md`; existing output directories are refused.
Exit 0 means all records were comparable under declared synthetic assumptions,
**not healthy or accurate**. Exit 2 reports unsupported input, invalid continuity,
empty input or insufficient contributors. Output errors are explicit; partial
output is not a successful report. The input/output are memory-resident and
bounded, not an untrusted-stream or resource-exhaustion qualification.

The report copies the original estimator's equal-weight body-gyro mean and
maximum Euclidean residual, not standard deviation. At least two accepted
contributors are needed for spread/residuals; unavailable is null, not zero.
Common bias may have zero spread; a 3-vs-3 split cannot identify the correct
group. Summaries are per-record, not time-weighted, and never consult truth or
fault-label sidecars. Internal orientation is neither emitted nor used for control.

## N8R8 checks without an SDK

The five source/profile tests need an **already available CMake 3.16+** and a
fresh scratch directory. They do not configure ESP-IDF, compile firmware or
touch hardware. Missing CMake is an unmet prerequisite, never a skipped pass.

```sh
cmake --version
REV5_EVAL_CMAKE="$(command -v cmake)" \
REV5_EVAL_TEST_SCRATCH="$(mktemp -d)" \
  python3 -B firmware/bench-imu-01-rev5/evaluation/n8r8/tests/test_profile.py -v
```

The original dynamic test is unchanged: it accepts the eleven frozen inputs,
then confirms CMake rejects altered application, pin-header and component
registration bytes. The only portability edit in the original test file is
the pin-reference filename. Assertions and the CMake test body are preserved.

The [U201 reference](../../firmware/bench-imu-01-rev5/evaluation/n8r8/reference/u201-pin-reference.xml)
is **explicitly derived**, not a complete native netlist. It retains the exact
native net/node attributes for 11 measurement pins and the 3 conflicting FG
pins; local source paths and unrelated circuitry are omitted. Its original
native-netlist hash, projection method and exact pin rows are in
[source notes](software-source-notes.json). No hardware design was moved,
modified or approved to change a gate's applicability.

The full generated pin header is unchanged, including the conflicting FG
assignments. The source/profile's historical N8R2 labels, raw `REV5B1` /
`rev5-m1` identity and old review-status field are also unchanged; they do not
identify an actual module suffix or supersede the separate review summary.
The profile selects N8R8 evaluation, not full Rev5 replacement.

An ESP-IDF build is a different, **not run in this publication** operation.
It requires the exact official SDK commit
`30aaf64524299d3bde422ca9a2848090d1bc5d0f` (v5.5.2) and its matching independently
obtained toolchain. No installer, SDK snapshot or flash instructions are added.
Source guards are not relaxed to accommodate an unavailable SDK.

## Review versus new publication evidence

[software-review.json](software-review.json) is a sanitized, hash-bound summary
of completed independent review `5d70e3126a5008904ff3d32ccdcda28cd26f1e29`
(technical result `7b033d9fb7675ac1d2a6847cfc73b40422d52568`).
All three limited source scopes were **PASS**, with **0 new concrete defects**
and **36 unit tests RUN/PASS**: C1 18, IMU 14, N8R8 4.

That review's fifth N8R8 dynamic CMake test remains **NOT_RUN** because the
reviewer host lacked CMake. SDK/build/ELF/BIN/device checks were **excluded**.
Original author build receipts are **AUTHOR_REPORTED**, not fresh independent
execution. No raw private reviewer or tool logs are published.

[software-checks.json](software-checks.json) records new publisher/CI evidence
separately. Any later CMake success is not a correction of the old NOT_RUN,
an independent review of the public packaging, a firmware build, or hardware
acceptance. The existing simulation workflow runs the new scoped checks in
addition to its unchanged numerical regression command. All required check
names, hardware gate logic and branch protection remain unchanged.

## Provenance, rights and reproduction limits

[software-intake.json](software-intake.json) freezes the positive source
allowlist; [software-manifest.json](software-manifest.json) binds the actual
public files and distinguishes byte-identical code/data from derived prose,
source metadata and the test-path edit. Only selected immutable blobs were
exported onto public-main ancestry; no private branch was merged.

First-party code and synthetic fixtures are owner-authorized project work.
No new repository or downstream license is invented. The genuine Bosch
BSD-3-Clause license, notices, source provenance and unmodified configuration
blob are retained. ESP-IDF is external; its license is retained, not its SDK.
See [third-party notices](../../firmware/bench-imu-01-rev5/measurement/NOTICE.md).

Evidence IDs inside the frozen code refer to their **original source snapshot**.
Selected manufacturer metadata and original evidence-row meanings are provided
in the source notes; they are not new allocations in the public canonical
ledger or new manufacturer verification. The original measurement
`source-lock.json`, private build/fix receipts, comparison packet and complete
native design history are deliberately absent. Their strings in unchanged
metadata are historical locators, not executable dependencies or fetched
fallbacks. Public tests do not pretend to reproduce those historical audits.

Excluded: sealed C1 inputs, raw uploads/screenshots, original manufacturer
documents, account/provider/reviewer/host logs, SDK/tool snapshots, flash
binaries, native CAD/media, held sidecar/control and active v3/Blender work.
This release cannot reconstruct the original private source history, regenerate
native CAD or certify the physical machine.

## Publication and rollback

The Pages workflow still uploads `visualization/` as its root. EN/JA landing
pages link to these GitHub-hosted software guides; the CLI is not a browser
application. PR CI, normal merge, exact remote file read-back and actual Pages
deployment/navigation are separate observations, recorded by their real URLs.
A local document or passing local test is not evidence of merge or deployment.

Rollback is a normal reviewed revert of this follow-up, with the same required
checks and Pages deployment. Preserve the earlier v2 release. Never reset
shared history, weaken a gate, or describe a revert as deployed before read-back.
