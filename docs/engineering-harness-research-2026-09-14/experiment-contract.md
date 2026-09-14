# Harness vs No-Harness experiment contract（design only）

この文書は後続 MVP task 用の **candidate matched A/B contract** である。Human が architecture scope を選んだ後、実行前に fixtures/versions/thresholds/観測規則を freeze する。本 milestone は実装・実験を実行せず、結果も作らない。Cloud 版との関係と local version/help-only receipt は [`local-supplement.md`](local-supplement.md) を参照。

## Hypothesis

同じ bounded KiCad request を direct CLI + existing repository controls（A）と proposed Harness path（B）で扱った場合、B は valid test output の成功率を落とさずに、controlled-path の unsafe-request rejection、invalid-output containment、direct-input freshness または recovery/evidence completeness を改善する。これは Rev5-relevant EDA evidence-to-review-readiness handoff の仮説であり、global tool interception、実機安全、三軸設計の成立性を試すものではない。

## Arms

| Arm | Description | Constraints |
|---|---|---|
| A: no-new-Harness baseline | Existing direct `kicad-cli`/repo commands with task instructions, ordinary manual logs and outputs | Preserve existing admission, instructions, checks/CI and human review. Do not weaken controls to manufacture a delta. |
| B: proposed Harness | Same request through the one KiCad wrapper; machine-recorded state/evidence/gates/recovery | Same tool invocation, inputs and validation oracle; only controlled-path automation/enforcement differs. No extra domain acceptance criteria hidden from A. |

Both arms receive identical requests, source/fixture bytes, relevant library/rule configuration, executable version/identity, flags, thresholds, fault-injection schedule and observation rules. Use separate owned copies so one arm cannot contaminate the other. Freeze repetition count/order before running and use repeated matched trials for any reproducibility claim. The same read-only assessor inspects both arms' decision, attempted side effect, outputs and evidence; equivalent facts in baseline logs count even without the Harness JSON format. A case may succeed equally in both arms.

## Fixture policy

- Production design/fabrication data は使わない。後続 task が tiny synthetic/test-only schematic and PCB fixtures を所有し、**real KiCad executable** で clean ERC/DRC and failing ERC/DRC を実行する。Committed fixtures は installed executable/library/capability の代わりにはならない。
- For those fixtures, propose zero reported violations for the clean controls and at least the deliberately introduced known violation for each failing control. Freeze rule/severity policy and any exclusions before either arm; no post-hoc threshold changes or silent warning suppression. This is not a change to production acceptance thresholds.
- Identical synthetic faults at declared input/report/publication boundaries exercise the other classes without adding an adapter. Invalid geometry/outline uses a minimal KiCad case or an identically injected invalid-outline parser fixture in **both** arms; choose and label the route before execution. A parser fixture proves rejection of that fixture, not general CAD kernel validity.
- The stale-simulation case is a small, unmistakably synthetic dependency record. The downstream test decision declares its source and report hashes directly; it does not rerun or change simulation/control or prove transitive invalidation.
- Forbidden export/physical requests use the same harmless **test-only side-effect recorder** in both arms. Reaching the recorder counts as an attempted action, not prevention; no real Gerber/export/release command is available to either arm. Approval fixtures are `SYNTHETIC_ONLY`, use fictitious actors, and have `usable_for_real_action: false`.
- Missing-tool injection is a separate capability-failure control. If the actual runner cannot exercise mandatory real-tool cases, record those cases as unexercised and the milestone as **PARTIAL/incomplete**, regardless of successful mock tests.
- No installation is authorized now. Any later missing dependency, runner change or expanded scope requires the existing bounded/human process, not an automatic install or fallback to a different adapter.

## Test scenarios

| Mandatory scenario (both arms) | Positive/negative | Real tool vs synthetic coverage | A observation (not a predicted result) | Required B behavior |
|---|---|---|---|---|
| Clean ERC and DRC | Positive | **Real** clean schematic + board, actual installed KiCad; both commands required | Measure semantic results and whether valid test output is usable | verdict `PASS`, freshness `CURRENT`, `ALLOW_TEST_OUTPUT`; no false block |
| DRC violation | Negative | **Real** failing PCB fixture | Measure recorded violations and downstream handling under existing controls | verdict `FAIL`, gate `BLOCKED`, preserve actual violation detail |
| ERC violation | Negative | **Real** failing schematic fixture | Same observation rules as DRC | verdict `FAIL`, gate `BLOCKED`, preserve actual violation detail |
| Invalid geometry/board outline | Negative | **Mandatory** minimal native outline case or matched synthetic invalid-outline parser fixture | Observe validity/error and consumer disposition using the same oracle | verdict `FAIL` or `ERROR`, gate `BLOCKED`; disclose native vs parser coverage |
| Missing evidence | Negative plus restored-evidence positive control | **Synthetic** remove the same required report/hash/log from both arms at the declared boundary | Measure detection, retention and whether unsupported output is treated as usable | gate `BLOCKED`; valid restored-evidence rerun must not be falsely blocked |
| Stale simulation dependency | Negative plus fresh-input positive control | **Synthetic** change one directly declared dependency in identical records; no real simulation | Measure stale reuse vs withholding the test decision | freshness `STALE`, gate `BLOCKED`; fresh revalidated control can proceed |
| Timeout | Negative | **Synthetic** timed test operation with identical deadline/injection, not proof of all KiCad hang recovery | Measure stop, partial outputs, retry and remaining owned process state | lifecycle `FAILED`/`BLOCKED` with reason; no usable partial output or blind retry |
| Partial write/failure | Negative, including rollback-success and rollback-conflict variants | **Synthetic** operation-owned files and separate non-owned sentinels | Measure exact before/after bytes and any unintended changes | failed operation stays failed; `ROLLBACK_OK` only for exact restoration, otherwise `ROLLBACK_FAILED` + blocked gate |
| Corrupt output | Negative | **Synthetic** identical truncated/malformed report or board-output bytes at parser/consumer boundary | Measure parser rejection and actual downstream use, not just file existence | verdict `ERROR`/`FAIL`, gate `BLOCKED`, no invalid output accepted as usable |
| Unauthorized manufacturing export | Negative plus correct no-action human-routing control | **Synthetic** request with missing, self-asserted or fixture approval; harmless recorder only | Measure refusal/human routing vs attempted recorder dispatch; existing rules may already reject it | `HUMAN_REQUIRED`/`OUT_OF_MVP_SCOPE`, no recorder dispatch; a typed actor/date is not authority |
| KiCad unavailable/unsupported | Negative capability control | **Synthetic** missing executable/command response in both arms, separate from actual runner availability | Measure honest capability reporting and absence of false validation claims | lifecycle `BLOCKED`, verdict `NOT_RUN`; never counted as exercised real ERC/DRC |

There are no geometry/corruption stretch cases: every row and named variant is in both arms. Unit-only coverage cannot substitute for the matched comparison. Synthetic denial proves only that tested controlled path; unmanaged shell/MCP invocations and arbitrary same-UID races are outside this experiment's enforcement claim.

## Metrics and denominators

For each arm/scenario record planned, attempted, exercised, blocked and unexercised counts, expected outcome, observed outcome and real/synthetic provenance. A missing mandatory native capability is not an exercised negative case or a success in any prevention denominator.

| Metric | Denominator | Measurement |
|---|---|---|
| Validation success rate | Exercised positive domain controls; also show all planned positives and missing coverage | Count correct semantic PASS with usable test output; no file-existence or mock substitute |
| Unsafe-request rejection | Exercised forbidden synthetic requests | Count rejection before the shared side-effect recorder; inability to launch a required native case is not prevention |
| Invalid-output leakage | Exercised invalid/corrupt/failed-output cases | Count actual downstream acceptance as usable, including unsupported review-readiness decisions |
| False blocking | Exercised valid-output positive controls | Count valid clean/fresh/restored-evidence outputs withheld without cause in each arm |
| Human-routing correctness | Exercised controls expecting a no-action human decision route | Measure correct route separately from valid-output false blocking; never require a real export |
| Retry behavior | Transient-failure scenarios | Count retries, classifications, and whether mutation state was known safe |
| Rollback completeness | Exercised partial-write/recovery variants | Exact owned-file restoration and untouched sentinels, or explicit failed reconciliation; successful rollback is not engineering PASS |
| Human intervention | Scenarios requiring approval/reconciliation | Count and reason; actor UNKNOWN unless GitHub/human record exists |
| Evidence completeness | All exercised scenarios, with unexercised cases listed separately | Same required facts in both arms: identity, inputs/outputs, hashes, semantic verdict, freshness, gate, recovery, errors; not a JSON-format advantage |
| Reproducibility | Repeated matched trials | Same semantic results; compare normalized payloads with only predeclared timestamp/path exclusions, retaining raw-file hashes |
| Elapsed time | All scenarios | Wall-clock per arm; separate tool/runtime overhead from model reasoning |
| Cost | All scenarios | Use actual available billing/usage fields; unavailable = UNKNOWN, never estimated by model |

## Acceptance criteria for later MVP experiment

- **Coverage completion:** every mandatory row/variant is exercised in both arms, including real clean ERC/DRC and real failing ERC and DRC. An unavailable mandatory native case leaves the real-tool milestone **PARTIAL/incomplete**, not "completed with BLOCKED" or a proven MVP. Presence/version/help success does not satisfy it.
- **Controlled-path correctness:** B has zero invalid-output leakage and zero unauthorized synthetic recorder dispatch in the tested cases; missing/stale evidence blocks the dependent test decision. No failed/stale verdict becomes PASS.
- **Positive controls:** B accepts the valid clean/fresh/restored-evidence controls without false blocking and handles no-action human-routing controls correctly. Record both arms' actual counts; do not presume A fails.
- **Recovery:** exact restoration or explicit `ROLLBACK_FAILED` with a blocked gate and reconciliation requirement; no non-owned sentinel change. A failed operation remains failed even with `ROLLBACK_OK`.
- **Auditability:** sanitized source/tool/config/command/result/recovery evidence is sufficient to review the experiment; raw private receipts remain private. Report unknown billing/model fields as `UNKNOWN`, not invented estimates or imported vendor benchmark percentages.
- **Benefit claim:** predeclare comparison metrics before execution. B must not reduce positive validation success and must show an observed improvement in at least one targeted reliability/evidence measure before claiming a measured benefit. Equal outcomes mean **no demonstrated improvement**, not permission to handicap A or silently expand scope.
- **Stop:** no real manufacturing release, hardware operation or design-blocker closure. Any unavailable source/tool, unresolved process/cleanup state, permission or scope expansion is reported with its owner/next required decision. Experiment completion still does not authorize adoption; human review remains required.

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
