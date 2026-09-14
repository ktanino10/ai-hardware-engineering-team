# Engineering Harness MVP: one native KiCad adapter

**Implementation/test scope approved; production adoption is not approved.**
The parent recorded the human's Alternative A choice at
2026-09-14T23:00:17+09:00 against
[`8a237bb`](https://github.com/ktanino10/ai-hardware-engineering-team/tree/8a237bb4ef8db300d81c57b3ce11fddcd9d2cabe/docs/engineering-harness-research-2026-09-14).
This successor leaves all six approved research files, existing engineering
verdicts, simulation/control code and human/physical gates unchanged.
It implements a Rev5-relevant EDA evidence-to-review-readiness seam only on
new synthetic fixtures. No fixture result closes a real Rev5 blocker.

## Small implemented boundary

`tools/engineering_harness.py` keeps operation lifecycle, semantic verdict,
direct-input freshness, gate/reasons and recovery as separate fields.
`ALLOW_TEST_OUTPUT` is test-only: successful execution, semantic PASS,
current frozen inputs/config/tool/policy and intact report/log evidence are
all required. A second decision check compares current inputs and retained
evidence before offering the report to a test consumer. Historical-only
verification means freshness UNKNOWN/not checked, not automatically STALE.
The existing simulator's historical/current commands are neither called nor
replaced.

The only native adapter is `tools/engineering_harness_adapters/kicad.py`.
It verifies the selected executable hash/version and ERC/DRC help, then
uses an argument list (never a shell) with fixed JSON/severity/exit flags.
The core permits only the manifest-declared test inputs under
`tools/tests/fixtures/engineering_harness/`, bound to immutable Git bytes.
No MCP dependency, generic plugin/server, transitive graph or authority
service is added. The native report parser checks schema/version/source,
severity/default-check policy, result collections and exit/report agreement.

Owned output directories have an explicit marker and snapshots. Conditional
restore refuses mismatched paths, symlinks, hardlinks, ownership or written
bytes; failed operations stay failed even when recovery is `ROLLBACK_OK`.
Original failed reports and logs are retained separately from restored
publication outputs. Uncertain process cleanup disables restore and leaves
the operation blocked. The caller must preserve and reconcile those files,
not reset them to obtain a passing result.

These controls apply only to the wrapper's invocation/output path under
cooperative-workspace assumptions. They are **not an OS sandbox, global
tool interception, protection from arbitrary same-UID namespace mutation,
or authenticated evidence/approval**. Unmanaged clients can bypass them.
Actor/date/approval JSON never enables export, fabrication, purchase,
power-on, flashing, save-board or refill-zones. Such requests return
`HUMAN_REQUIRED` / `OUT_OF_MVP_SCOPE` without dispatch.

## Commands and existing reuse

The core uses the standard library on Python 3.11 or later; the recorded
experiment pins the actually available CPython 3.14.3. The native-independent
regressions use the existing unittest runner:

```sh
PYTHONPATH=tools python3 -m unittest discover -s tools/tests -p 'test_engineering_harness*.py'
```

The implementation reuses `agent_workflow.repo_path` and existing evidence
hash/Git/duplicate-key primitives. It does not modify admission, assembly
validation, CI, agent profiles or required checks. Normal `agent_workflow`
reservation and terminal receipts still surround commissioned work; the
Harness's task/run links are provenance, not authorization. No package
installation is necessary or authorized.

A test-only CLI request contains exactly:

```json
{
  "scope": "SYNTHETIC_ONLY",
  "operation": "drc",
  "task_id": "<admitted-task>",
  "run_id": "<normal-run-id>",
  "source_revision": "<full-frozen-candidate-commit>",
  "config_revision": "8a237bb4ef8db300d81c57b3ce11fddcd9d2cabe",
  "inputs": [
    "tools/tests/fixtures/engineering_harness/manifest.json",
    "tools/tests/fixtures/engineering_harness/clean.kicad_pcb",
    "tools/tests/fixtures/engineering_harness/clean.kicad_pro"
  ],
  "configuration": ["docs/work-execution.md"],
  "native_inputs": [
    "tools/tests/fixtures/engineering_harness/clean.kicad_pcb",
    "tools/tests/fixtures/engineering_harness/clean.kicad_pro"
  ],
  "input_name": "tools/tests/fixtures/engineering_harness/clean.kicad_pcb",
  "tool": {
    "sha256": "04d9e61cad2e80cf7ad6c3da06417a6d7e8e2cdd23efc99957a1184e604d6657",
    "version": "10.0.1"
  },
  "timeout": 20
}
```

The example is a minimal API shape, not the full experiment input list;
the actual plan additionally binds implementation, helpers, policy and
fixtures. Use a new owned scratch directory and the preflighted binary:

```sh
python3 tools/engineering_harness.py <request.json> \
  --workspace .agent-work/<admitted-task>/<new-operation> \
  --kicad-cli <verified-native-cli>
```

Exit 0 means only an allowed current **test output**; exit 2 means blocked
or human routing. Catchable caller cancellation exits **130**, stops further
dispatch, and retains interruption/partial-state receipts. Known owned
processes are terminated/reaped or cleanup is explicitly unverified;
uncatchable SIGKILL, default SIGTERM and general parent-death protection
are not promised. See [the cancellation follow-up](cancellation-followup.md).
Caller-supplied identities are not human authentication.
Requests cannot add native arguments, exports or production input paths.
There is deliberately no automatic retry in this MVP. Every attempt and
zero retry count is recorded; successful transient retry recovery is not
claimed.

## Frozen matched experiment

[`experiment-plan.json`](experiment-plan.json) specializes the approved
[comparison contract](../engineering-harness-research-2026-09-14/experiment-contract.md):
20 cases covering all 11 rows and named positive/recovery variants,
three repetitions in each arm (120 planned trials). The invalid-geometry
row uses the same native DRC adapter on a minimal open-outline PCB.
The other synthetic faults are explicit and identical in A/B; no native
test is replaced by mock success.

The candidate commit is supplied at execution rather than embedded
self-referentially in its own plan. Code, fixtures, tool identity,
Python version, severity/default-check policy, fault schedule, A/B order
and assessor are frozen **before** final trials. File generation and
fixture-development commands are not final observations.

Arm A is a **scripted policy-following direct-CLI reference**, not a trial
of real humans/models. It retains normal admission/instructions and
unchanged repo checks/gates, parses the same domain reports and rehearses
explicit owner snapshot/conditional restore with ordinary files. Arm B
adds the new controlled wrapper. Both use the same safe process transport,
flags, report oracle and read-only metric assessor. This deliberately strong
baseline is not forced to export, ignore stale inputs or lose recoverable
files. Equivalent log facts count independently of format. Baseline repair
is a synthetic owner-procedure rehearsal, **not production recovery or a
measured human action**.

After the implementation task is terminal, reserve a distinct experiment
task on the candidate with exact inputs and result/scratch writes. Then:

```sh
PYTHONPATH=tools python3 tools/tests/test_engineering_harness_experiment.py --run \
  --candidate <frozen-commit> --task-id <admitted-experiment-task> --run-id <normal-run-id> \
  --private-root .agent-work/<admitted-experiment-task>/<new-campaign> \
  --public-dir docs/engineering-harness-mvp-2026-09-14/experiment \
  --kicad-cli <verified-native-cli>
```

The command checks its normal RUNNING reservation and frozen inputs.
It creates result directories exclusively, never overwrites a previous
campaign, and returns exit 2/PARTIAL if mandatory native coverage or
cleanup cannot be established. A new campaign requires a relevant changed
input/decision and normal admission, not a renamed retry.

The original `experiment/` package belongs to candidate `ca0f276` and stays
unchanged. The cancellation-fixed successor uses the **same plan, cases,
rules, oracle and repetition/order**, but a new candidate and normal
reservation, with `--public-dir` set to
`docs/engineering-harness-mvp-2026-09-14/experiment-cancellation-successor`.
Cancellation regression/witness tests are separate from those matched
measurements; they are not added to the benchmark to create an advantage.

The limited independent review of `8562b6e` subsequently returned
**needs_correction**, with EH-001 (MEDIUM, 9/10) and EH-002 (MEDIUM, 10/10).
The original static findings and both completed campaigns stay unchanged.
The [experiment correction record](experiment-corrections.md) describes
new native-independent reproductions and the narrow runner changes.
Completed and skipped trial rows are now append-only; cancellation reports
observed stream bytes/hash, complete records, partial tail and whether the
acknowledged prefix is actually retained. A missing stream is not reported
as retained.

Timeout coverage now requires the intended child to have started, timed out,
been reaped, and have a verified owned-cleanup receipt. A safe BLOCKED response
to failed launch is **unexercised/PARTIAL**, not timeout success. Actual
timeout/error/start/cleanup facts participate in reproducibility; raw private
receipt hashes do not. The corrected candidate is measured separately under
`experiment-review-corrections/`, preserving the original 20 cases,
three repetitions, fixtures, rule thresholds and fault schedule. The
corrected assessor/finalization source is explicitly recorded in that
campaign's frozen inputs; no favorable A/B delta is presumed.

Final evidence belongs in `experiment/`: frozen input/config/tool hashes,
preflight facts, sanitized actual reports/logs, every trial's coverage and
measurements, metrics, and a human-readable summary. Raw environment,
absolute paths, process/snapshot receipts and unsanitized hashes stay in
ignored task-owned storage. Published artifact hashes are distinguished
from hashes of those private raw bytes. Only the native report's `date` is
removed for reproducibility comparison; original/raw hashes remain recorded.

## Completion and stops

Implementation delivery and experiment completion use separate normal
receipts. A completed comparison needs real nonempty clean ERC and DRC,
known real failing ERC and DRC, the native outline case and every matched
injection/positive/recovery case. Unexercised cases remain counted;
unit success or missing-tool BLOCKED never makes this milestone complete.
Equal reliability results mean **no demonstrated improvement**. Timing
is descriptive, process time is not isolated engine CPU time, and
billing/backend-model identity remain UNKNOWN when not exposed.

The clean fixtures have zero reported violations under the frozen policy,
not every possible electrical/PCB check. The native default ignored checks
are explicitly listed; no parity, thermal, component, assembly, physical
or general geometry acceptance follows. Fontconfig warnings observed during
development are retained as runtime observations, not suppressed ERC rules.

Stop for missing native prerequisites, uncertain owned-process cleanup,
conflicting ownership, changed frozen inputs or broader permission/scope.
No installation, extra workflow dispatch, paid service, GUI/native-app
automation, production document, real manufacturing export or physical
action is part of this delivery. Human review is required before any
production adoption.
