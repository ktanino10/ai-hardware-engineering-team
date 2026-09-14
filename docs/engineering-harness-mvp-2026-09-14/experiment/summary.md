# Frozen test-only MVP comparison results

**The working MVP completed all 120 planned trials. Reliability outcomes
were equal: no improvement over the strong scripted baseline was
demonstrated.** This validates the implemented controlled test path on the
recorded fixtures/runtime, not production adoption, physical safety,
general tool reliability or closure of a real Rev5 blocker.

## Provenance and execution stages

| Record | Actual value |
|---|---|
| Approved proposal / configuration | `8a237bb4ef8db300d81c57b3ce11fddcd9d2cabe` |
| Frozen implementation, fixtures and plan | [`ca0f276ffd51781e7e88cc44274787fbdd4237e7`](https://github.com/ktanino10/ai-hardware-engineering-team/commit/ca0f276ffd51781e7e88cc44274787fbdd4237e7) |
| Implementation task / normal run | `engineering-harness-mvp-implementation-2026-09-14` / `bccd7b67-0442-40da-b25a-37d6f2281ad4`, normal `DONE` after candidate commit |
| Distinct frozen experiment task / normal run | `engineering-harness-mvp-experiment-2026-09-14` / `0d5ee0a7-e571-41b3-9c7e-d3cdb6502628` |
| Final trial window | 2026-09-14T14:51:42.516330Z to 2026-09-14T14:52:56.994896Z (23:51:42 to 23:52:56 JST) |
| Actual runtime | Darwin/arm64, CPython 3.14.3, native KiCad 10.0.1 |
| Experiment command outcome | Exit 0; `experiment_status=COMPLETE`, no stop reason |
| Publication scope | Existing draft PR #78 only; no merge or force push |

The implementation's normal admission consumed the prior local correction's
actual six document hashes. Its eight declared delivered files then became
the normal experiment dependency, with all remaining code/fixture/config
inputs also frozen. The historical documentation run
`e02cf813-b7a4-424b-a3e9-acc4536b74c9` stayed DONE; no Cloud execution history
was invented or imported. The experiment's terminal receipt is emitted
after this package is finalized and published, and its exact hashes are
returned in the session handoff; it is not a self-hash or engineering
approval inside this report.

Code and fixtures were not edited during measurements. Fixture-development
checks and the **106 passing focused unit/admission/evidence regressions**
preceded the candidate commit and are not counted as final trials:

```sh
PYTHONPATH=tools:tools/tests python3 -m unittest \
  test_engineering_harness test_engineering_harness_experiment \
  test_agent_workflow test_assembly_evidence -q
```

## Mandatory actual native coverage

Each native case ran three times in A and three times in B with the same
input bytes, installed executable, flags, severity/default-check policy and
common report oracle. All are genuine domain reports, not parse/load errors
relabeled as the intended violation.

| Case | Actual result per invocation | A runs | B runs |
|---|---|---:|---:|
| Nonempty clean ERC | Exit 0, zero reported violations; two connected custom passive terminals | 3 | 3 |
| Nonempty clean DRC | Exit 0, zero reported violations; outline, four test pads and two separate pad-anchored nets | 3 | 3 |
| Failing ERC | Exit 5, two `pin_not_connected` errors | 3 | 3 |
| Failing DRC | Exit 5, one `tracks_crossing` error | 3 | 3 |
| Invalid geometry / open outline | Exit 5, one `invalid_outline` error using the same DRC adapter | 3 | 3 |

The native geometry row needs no parser-only substitute or second adapter.
The remaining faults/controls are explicitly synthetic: missing/restored
log evidence; stale/fresh direct dependency and historical-only mode;
owned Python timeout; partial-write restore and conflicting-writer variants;
truncated output; missing/self-asserted/matching synthetic approvals and
no-action human routing; missing/unsupported capability observations.
All 11 required rows and 20 named cases were exercised in **both** arms.
Nothing was skipped or counted as successful prevention because a native
tool was unavailable.

Clean means zero reported violations under the frozen KiCad policy,
**not all possible checks enabled**. The exact native default ignored-check
lists are in [frozen-inputs.json](frozen-inputs.json). No project exclusions
were added. The synthetic schematic and board are independent witnesses;
schematic/PCB parity, component ratings, thermal/mechanical validity,
manufacturability and real three-axis design acceptance were not assessed.
ERC also emitted Fontconfig warnings; these were retained privately and
explicitly summarized in public logs, not treated as erased ERC findings.

## Measured A/B outcomes

Arm A is a scripted, policy-following direct-CLI reference with ordinary
owner inspection and explicit conditional test-output restore. Arm B uses
the new wrapper. A was not required to dispatch forbidden actions, omit
existing instructions/checks, accept stale evidence or lose recoverable
files. Neither arm is a measurement of an actual human or live model.

| Measurement | A: direct reference | B: wrapper |
|---|---:|---:|
| Planned / attempted / exercised | 60 / 60 / 60 | 60 / 60 / 60 |
| Correct expected outcomes | 60/60 | 60/60 |
| Native domain invocations | 15 | 15 |
| Valid positive-control success | 12/12 | 12/12 |
| False blocking of valid outputs | 0/12 | 0/12 |
| Invalid-output acceptance by the test consumer | 0/30 | 0/30 |
| Forbidden synthetic requests rejected before recorder | 12/12 | 12/12 |
| Exact owned-file restoration in recovery variants | 3/6 | 3/6 |
| Explicit conflicting-writer refusal in recovery variants | 3/6 | 3/6 |
| Upstream evidence complete at decision time | 57/60 | 57/60 |
| Scenarios reproducible across all three repetitions | 20/20 | 20/20 |
| Automatic retries | 0 | 0 |
| Actual human interventions during trials | 0 | 0 |
| Synthetic no-action human routes | 12 | 12 |
| Active trial elapsed time, summed | 11.734 s | 12.536 s |
| Native/fault process elapsed component, summed | 10.122 s | 10.317 s |
| Common input-copy/binding setup, summed separately | 23.747 s | 23.889 s |

The three intentionally missing-log trials per arm explain 57/60 upstream
completeness; they all blocked correctly. Restored-evidence positives
first observed BLOCKED with the log absent, then allowed the restored valid
test evidence. Fresh positives were allowed; changed direct dependencies
were STALE; historical-only checks left current freshness UNKNOWN/not
checked and did not support a current decision.

`ROLLBACK_OK` never turned a failed operation into PASS. All 12 combined
partial-write witnesses retained the original failure; six restored exact
prior bytes and six preserved the conflicting writer's bytes with a
blocked gate. Baseline restoration is a scripted owner-procedure rehearsal,
not manual cleanup counted as production recovery.

The complete campaign lasted approximately 74.48 seconds including setup,
preflight and evidence handling. Timing differences are descriptive only;
three fixture repetitions do not establish a general performance advantage.
Process time includes process observation/management, not isolated engine
CPU time. Billing and backend-model identity are **UNKNOWN**. No vendor
benchmark percentages, guessed costs or model self-certification enter
these measurements.

**Interpretation:** the wrapper provides a persistent, tested way to apply
the declared controls, but this comparison shows no reliability advantage
over an already careful direct procedure. Do not claim a better AI/model,
automatic production adoption or broader benefit from equal results.

## Auditable artifacts and cleanup

- [experiment-plan.json](../experiment-plan.json) fixes requests, faults,
  thresholds, repetition/order and observation rules before execution.
- [frozen-inputs.json](frozen-inputs.json) binds code, sources, configuration,
  policy and actual tool identity; [preflight.json](preflight.json) remains
  distinct from actual domain results.
- [trials.jsonl](trials.jsonl) records every planned trial, including
  native/synthetic provenance, current gates, direct-input changes, timings,
  raw private hashes and separate sanitized public artifact hashes.
- [metrics.json](metrics.json) contains the measured numerators/denominators
  and the explicit `NO_DEMONSTRATED_RELIABILITY_IMPROVEMENT` conclusion.
- [ownership-cleanup-audit.json](ownership-cleanup-audit.json) contains
  independently checked recovery hashes and scoped process/cleanup witnesses.
- [artifact-manifest.json](artifact-manifest.json) binds the public package
  without self-hashing its own manifest.

The process audit covers **39 actually started owned subprocesses**:
30 native domain invocations, three native preflight commands and six
synthetic timeout processes. The six timeouts targeted only the process
groups created for those tests. All 39 records show reaped completion and
no remaining members in their owned group at observation; all associated
temporary runtime directories were removed and their absence rechecked.
All 120 non-owned-within-test-area sentinels remained unchanged, and no
forbidden side-effect recorder was reached. This is **not a global jobs-zero
claim or an OS sandbox guarantee**. Operation outputs, snapshots, logs and
failed-state receipts remain in private task-owned storage for audit; they
were not discarded as cosmetic cleanup.

Native report reproducibility excludes only `date`, as predeclared.
Original report/log hashes are retained alongside hashes of the sanitized
public bytes; neither is mislabeled as the other. No raw absolute paths,
environment/process dumps, credentials, supplier documents, large binary
assets or native applications were uploaded.

## Unchanged approval boundary

No GUI automation, installation, MCP integration, production document,
real export/manufacturing, power-on, flash, simulation/control change or
real design promotion occurred. The implementation uses POSIX process
facilities and was exercised only on the stated runtime/tool version;
other platforms and versions are not validated by this package.
The direct-only dependency model does not detect undeclared/transitive
changes. Optional wrappers do not stop unmanaged clients or arbitrary
same-UID writers. Typed approval fields do not authenticate a human.

Independent review and human production-adoption review remain outstanding.
Existing engineering verdicts, Design Complete conditions and all
human/physical gates are unchanged. No additional work or adapter is
automatically commissioned by these results.

## Separate required-check observation at the frozen candidate

The required **Check agent/skill frontmatter** check was not green at
`ca0f276`. Its [actual CI run](https://github.com/ktanino10/ai-hardware-engineering-team/actions/runs/34858276484/job/104023437684)
failed the existing bilingual documentation inventory test
`test_every_reader_readme_and_markdown_path_is_classified`: the six research
documents already on this PR and the two new MVP/fixture READMEs were not
registered (eight failing subtests in a 45-test workflow suite). This is a
documentation integration failure, separate from the 106 focused tests and
the native comparison above; it is not hidden as an ERC/DRC failure or a
claim that all CI passed.

Registering these reader surfaces and their substantive Japanese reading
editions requires write scope outside the approved implementation/experiment
paths. That narrow permission was requested from the parent before editing
the inventory. Any authorized follow-up must preserve the frozen code,
fixtures, plan and measured evidence, and must not weaken the test or
workflow. This paragraph records the candidate's historical check state;
a later fix needs its own normal task and current CI evidence.
