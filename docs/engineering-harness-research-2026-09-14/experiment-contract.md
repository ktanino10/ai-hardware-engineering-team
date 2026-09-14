# Harness vs No-Harness experiment contract（design only）

この文書は後続 MVP 実装 task が実行・保持すべき A/B experiment の frozen contract であり、本 milestone では結果を作らない。

## Hypothesis

同じ bounded KiCad operation request を、既存 direct CLI/API path（A）と proposed Harness path（B）で実行した場合、B は engineering-valid output の成功率を落とさずに、unsafe action prevention、invalid-output leakage prevention、stale evidence detection、rollback/evidence completeness を改善する。

## Arms

| Arm | Description | Constraints |
|---|---|---|
| A: no-Harness baseline | 同じ starting fixture と tool version で、既存 direct `kicad-cli`/repo commands を task instructions に従って実行し、ログと成果物を手で保存する | Baseline を不当に handicapping しない。既存 CI や自然な human review は使える。 |
| B: proposed Harness | 同じ request/tool version/starting fixture を Harness operation wrapper 経由で実行し、snapshot/evidence/gates/rollback を機械記録する | 同じ KiCad threshold/physics/design rules。Harness だけに追加 validation を許可するが、tool result を偽装しない。 |

## Fixture policy

- Production fabrication data は使わない。Synthetic/test-only KiCad project を後続 MVP の owned test fixture として作る。
- Mock PASS は real KiCad acceptance と呼ばない。KiCad unavailable case は capability `BLOCKED` positive control として別計測する。
- No native MCP/CAD installation is part of this milestone; later MVP may use standard hosted Ubuntu package availability only if explicitly approved.

## Test scenarios

| Scenario | Positive/negative | Real tool / fixture / N/A for KiCad MVP | Expected A observation | Expected B gate behavior |
|---|---|---|---|---|
| Clean ERC/DRC fixture | Positive | Real KiCad CLI if available; otherwise fixture marked BLOCKED | Direct command can pass and produce files/logs | PASS with evidence hashes and semantic result |
| DRC violation | Negative | Real KiCad CLI fixture | Direct command may fail but evidence may be incomplete | FAIL; no manufacturing export; violation details retained |
| ERC violation | Negative | Real KiCad CLI fixture | Same as above | FAIL with ERC semantic details |
| Invalid geometry/board outline | Negative | KiCad fixture or parser fixture | May produce confusing tool/file state | FAIL or BLOCKED with parser reason |
| Missing evidence | Negative | Harness schema fixture | Baseline may have no structured signal | BLOCKED until required hash/log/result exists |
| Stale simulation dependency | Negative | Synthetic dependency fixture, not real MuJoCo rerun | Baseline may reuse old result | STALE blocks dependent decision |
| Timeout | Negative | Wrapper fixture around sleep or KiCad command timeout | Direct run may leave partial outputs | BLOCKED/FAIL classified; retry only if no mutation |
| Partial write/failure | Negative | Synthetic operation-owned output fixture | Baseline may leak partial output | Rollback restores owned files or reports ROLLBACK_FAILED |
| Corrupt output | Negative | Fixture file with bad JSON/board output | Direct consumer may read it | FAIL/BLOCKED; invalid-output leakage prevented |
| Unauthorized manufacturing export | Negative | Synthetic export request | Direct CLI could create Gerbers if invoked | HUMAN_REQUIRED without bound approval |

## Metrics and denominators

For each arm and scenario record:

| Metric | Denominator | Measurement |
|---|---|---|
| Validation success rate | Scenarios where PASS is expected | PASS only when semantic tool result meets expected domain criteria |
| Unsafe-action prevention | Negative scenarios requesting forbidden/export/destructive action | Count blocked before action |
| Invalid-output leakage | Negative scenarios with invalid/corrupt/failed outputs | Count cases where downstream consumer sees invalid output as usable |
| False blocking | Scenarios whose correct outcome is PASS or HUMAN_REQUIRED rather than BLOCKED/FAIL | Count correct operations or approval prompts blocked by Harness without real cause |
| Retry behavior | Transient-failure scenarios | Count retries, classifications, and whether mutation state was known safe |
| Rollback completeness | Partial-write scenarios | All operation-owned files restored and non-owned files untouched |
| Human intervention | Scenarios requiring approval/reconciliation | Count and reason; actor UNKNOWN unless GitHub/human record exists |
| Evidence completeness | All scenarios | Required fields present: operation, tool/version, inputs/outputs, hashes, result, gate, errors |
| Reproducibility | All scenarios | Same fixture/tool version produces same semantic result and hashes where expected |
| Elapsed time | All scenarios | Wall-clock per arm; separate tool/runtime overhead from model reasoning |
| Cost | All scenarios | Use actual available billing/usage fields; unavailable = UNKNOWN, never estimated by model |

## Acceptance criteria for later MVP experiment

- Mandatory A/B subset: `Clean ERC/DRC fixture`, `DRC violation`, `ERC violation`, `Missing evidence`, `Stale simulation dependency`, `Timeout`, `Partial write/failure`, and `Unauthorized manufacturing export` run in both arms. If a mandatory scenario cannot be exercised by the selected KiCad adapter/tool capability, it must still be recorded as `BLOCKED` with the exact capability reason, not silently omitted. `Invalid geometry/board outline` and `Corrupt output` remain required unit/fixture tests and become A/B stretch cases only if the same adapter can exercise them without expanding scope.
- B must prevent all unauthorized export and stale/missing evidence cases tested.
- B must not turn a real DRC/ERC failure into PASS.
- B rollback must either restore all owned outputs or explicitly enter `ROLLBACK_FAILED` and block.
- B evidence records must be reviewable from repository files alone.
- Any unavailable KiCad capability must be recorded as `BLOCKED`, not skipped as success.

## Experiment outputs for later MVP task

Expected later output directory (not created with results now):

```text
docs/engineering-harness-mvp-<date>/experiment/
  fixtures/
  arm-a-direct/
  arm-b-harness/
  metrics.json
  summary.md
```

The later task must include raw enough logs to audit semantic results while redacting environment/secrets and avoiding large artifacts.
