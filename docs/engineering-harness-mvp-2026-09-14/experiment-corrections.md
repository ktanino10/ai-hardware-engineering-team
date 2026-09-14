# EH-001 / EH-002 correction successor

**Candidate-stage author correction record, not a rewritten independent
verdict.** The limited independent review of
`8562b6e7bc383c373c3af3bf8a42929ebba7ddba` returned `needs_correction`:
EH-001 MEDIUM (9/10) and EH-002 MEDIUM (10/10), both
`static_code_supported`. Its raw response, 48-input snapshot and normal
terminal receipt remain privately sealed and unchanged. The reviewer was
the fresh `code-review` context
`bfe592f9-793b-497b-b99a-16fceb0e5920`, not the implementation author.

Normal correction task: `engineering-harness-review-correction-2026-09-15`,
run `e4408b81-4a18-4208-bc2c-fa6cc09c04c9`, source `8562b6e`, adopted
configuration `8a237bb4ef8db300d81c57b3ce11fddcd9d2cabe`. The privately
hash-verified review is explicitly non-Git intake, not fabricated committed
dependency history. No earlier DONE record is reopened.

## Reproduction and narrow corrections

| Finding as independently reported | New author reproduction | Correction |
|---|---|---|
| EH-001, MEDIUM 9/10: final truncating `write_text` can erase the accumulated public trial stream during catchable cancellation while reporting retention | Native-independent regression executes the real `main` / `_run_experiment` accumulation and finalization. Native work and trial production are controlled fixtures, not a mock of the whole runner. Interrupting the actual truncating-open boundary left **0 of 120** accumulated rows. | Append-only `TrialStream` records both completed and skipped rows. No final truncating rewrite occurs. On cancellation, report observed bytes/hash, complete records, partial tail and whether the acknowledged byte prefix is retained; missing/unreadable/replaced output is not reported as retained. |
| EH-002, MEDIUM 10/10: failed child launch counts as exercised timeout coverage | At the real synthetic timeout boundary, `Popen` raises `OSError(EAGAIN)` before starting a child. Both A and B safely block but originally report `exercised=true`. | Timeout credit requires a started child, observed timeout, reaped exit, matching timeout reason and verified owned cleanup/receipt. An unsuccessful injection is unexercised/PARTIAL even when its gate blocks correctly. |

[experiment-correction-witness.json](experiment-correction-witness.json)
separately binds the new reproduction/regression observations and raw private
log hashes. The original independent findings remain static findings at
their original source; they are not relabeled as having run these witnesses.

The finalization regression interrupts the actual accumulated-stream
boundary; after the fix it interrupts summary entry, with all 120 rows
still intact and no truncating attempt. Additional native-independent
regressions interrupt the sixth append and verify the five acknowledged
rows plus an explicitly reported partial tail, remove the stream before
cancellation and require a false retention result, and check that skipped
rows are appended rather than reconstructed at the end. Catchable operator
cancellation still exits 130 and stops subsequent work. No uncatchable
signal, parent-death or arbitrary same-UID protection is claimed.

Timeout regressions cover failed start in both arms, individually missing
start/timeout/reaped-exit/cleanup prerequisites, a real short-lived test
Python timeout positive, and changed timeout/error facts in the
reproducibility comparison. Transport facts are retained in each new trial;
the variable private process-receipt hash is separate from that semantic
projection. No core/native-adapter change was necessary.

## Measurement and review boundaries

Only `tools/tests/test_engineering_harness_experiment.py` changes executable
behavior; the related English/Japanese guides and this source-linked record
are updated. The original plan, 20 scenarios, three repetitions per arm,
native fixtures/inputs, flags, domain thresholds, fault schedule and strong
scripted A baseline remain unchanged. A new literal public output directory,
`experiment-review-corrections/`, isolates the corrected candidate's
measurement from both earlier packages. Its frozen input record identifies
the corrected assessor/finalization revision and the added transport-fact
projection, rather than pretending the assessor implementation is unchanged.

The two old campaigns are historical and byte-identical. Both exercised
120/120 trials with equal A/B reliability outcomes and
**NO_DEMONSTRATED_RELIABILITY_IMPROVEMENT**. The review did not invalidate
their actual timeout receipts or reinstate the earlier fixed owned-child
cancellation defect. These corrections make future coverage and interruption
reporting truthful; they do not manufacture a favorable benchmark delta.

After the correction candidate is committed, the identical successor
campaign is separately admitted. At most one EH-001/EH-002 delta follow-up
is requested from the **same** reviewer, with a source-specific disposition
preserved separately from the original findings. Author regression success
is not independent acceptance. Output audits remain deterministic
post-run consistency checks, not electrical/mechanical safety certification.

No new worker/factory, adapter, installation, CI exemption, supplier action,
production document, real export/manufacturing, simulation/control change
or physical action is included. Current PR remains experimental; merge and
human production/hardware adoption are not authorized by this work.
