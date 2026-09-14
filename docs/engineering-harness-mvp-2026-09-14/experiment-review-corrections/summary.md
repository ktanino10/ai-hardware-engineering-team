# Corrected-assessor campaign: EH-001 / EH-002

**All 120 planned trials were exercised with the corrected runner. Both
arms again had equal reliability outcomes:
NO_DEMONSTRATED_RELIABILITY_IMPROVEMENT.** Correcting evidence retention and
coverage accounting does not imply a favorable A/B delta or production
approval.

| Provenance | Actual value |
|---|---|
| Frozen corrected candidate / assessor revision | `c7764e126380e94ed7012545a84b68cd5a5de1eb` |
| Adopted configuration | `8a237bb4ef8db300d81c57b3ce11fddcd9d2cabe` |
| Correction normal run | `e4408b81-4a18-4208-bc2c-fa6cc09c04c9`, DONE for author delivery |
| Separately admitted campaign | `527e0424-03e6-4600-8036-cdd9b800050d` |
| Same-reviewer targeted delta run | `0118b4b9-d007-47bd-b537-1c6faaca04dc` |
| Actual measurement window | 2026-09-14T16:50:08.126283Z to 16:51:20.618236Z (2026-09-15 01:50:08 to 01:51:20 JST) |
| Runtime | Darwin/arm64, CPython 3.14.3, native KiCad 10.0.1 |
| Campaign command result | Exit 0, COMPLETE, no stop reason |

The original plan's 20 scenarios, three repetitions per arm, fixtures,
native inputs/flags, domain thresholds, fault schedule and strong scripted
reference baseline remain unchanged. This is a new assessor/finalization
implementation, not an unchanged-code rerun: [frozen-inputs.json](frozen-inputs.json)
explicitly identifies EH-001/EH-002, append-only completion, timeout
prerequisites and the added `transport_facts` reproducibility projection.
The variable private process-receipt hash is retained but is not a semantic
reproducibility value.

## Reproductions and regression evidence

The original independent review at `8562b6e` remains `needs_correction`,
EH-001 MEDIUM 9/10 and EH-002 MEDIUM 10/10, static-code-supported.
The [author correction record](../experiment-corrections.md) and
[witness receipt](../experiment-correction-witness.json) record later,
separate native-independent executions rather than rewriting that finding
history:

- The actual accumulated-stream finalization path lost 120 records when
  interrupted during its old truncating write. The corrected path retains
  all 120 and performs no truncating rewrite; interruption during an append
  retains the acknowledged prefix and reports the partial tail accurately.
- A timeout child launch raising `Popen` `OSError(EAGAIN)` was previously
  counted as exercised in A and B. Both now leave the failed injection
  unexercised/PARTIAL even though BLOCKED is the correct safe reaction.
- Forty-nine focused core/runner tests and six existing bilingual checks
  passed before freezing the candidate. These are not native campaign
  observations or an independent verdict.

Only the experiment runner/regression file changed executable behavior.
Core/native-adapter code, original native fixtures and plan were not
modified. Capture of a real start, timeout, reaped exit, matching reason and
verified cleanup is now mandatory before the timeout row gets coverage
credit; timeout/error/start/cleanup facts are also compared across repeats.

## Actual matched outcomes

| Measurement, per arm | A | B |
|---|---:|---:|
| Planned / attempted / exercised | 60 / 60 / 60 | 60 / 60 / 60 |
| Correct expected outcomes | 60/60 | 60/60 |
| Actual native domain invocations | 15 | 15 |
| Positive-control success | 12/12 | 12/12 |
| False blocking | 0/12 | 0/12 |
| Invalid-output acceptance | 0/30 | 0/30 |
| Forbidden synthetic requests rejected before recorder | 12/12 | 12/12 |
| Exact restore / explicit conflict refusal | 3 / 3 of 6 | 3 / 3 of 6 |
| Upstream evidence complete at decision time | 57/60 | 57/60 |
| Reproducible scenarios, including transport facts | 20/20 | 20/20 |
| Automatic retries / actual human interventions | 0 / 0 | 0 / 0 |
| Synthetic no-action human routes | 12 | 12 |
| Active trial elapsed, summed | 11.950 s | 11.248 s |
| Native/fault process elapsed component, summed | 10.894 s | 9.306 s |
| Common input-copy/binding setup, separately summed | 22.925 s | 22.722 s |

Each native case ran three times per arm. Clean nonempty ERC and DRC each
reported zero violations, exit 0. Failing ERC reported two
`pin_not_connected` errors, failing DRC one `tracks_crossing` error, and the
open-outline PCB one `invalid_outline` error, exit 5. These are intended
domain outcomes, not parse/load errors counted as validation coverage.

All six timeout trials in this campaign have an actual positive started
child identity in the private receipt, `timed_out=true`, a reaped exit,
`error=TIMEOUT`, and verified owned cleanup. None was a failed-start
substitute. Public [trials.jsonl](trials.jsonl) retains the corresponding
stable `transport_facts`, coverage reasons and separate private receipt
hash. The stream has 120 complete newline-terminated records in exactly the
frozen schedule, with no final rewrite.

The other missing/restored-evidence, stale/fresh/historical-only, partial
write/conflict, corrupt-output, forbidden-request and capability cases
remain labeled synthetic. The three deliberate missing-log cases per arm
explain 57/60 upstream completeness, and all correctly blocked. Historical
integrity alone remained UNKNOWN/not checked for current freshness.
Successful rollback never promoted a failed operation to PASS.

Elapsed time is descriptive only (approximately 72.49 seconds for the full
campaign including setup/evidence); process time is not isolated engine CPU
time. Billing and backend-model identity remain UNKNOWN. A is a strong
scripted policy-following reference, not a live human/model trial. Equal
outcomes do not demonstrate improved AI handling or authorize broader use.

## Review, preservation and limits

The original `ca0f276` campaign and `ad5542b` cancellation-successor campaign
are byte-identical, with their own 120-trial outcomes and no-benefit
conclusion. They are not invalidated or relabeled by these defects or this
measurement. The old independent raw response and 48-input snapshot remain
privately sealed.

The one authorized EH-001/EH-002 follow-up to the **same** reviewer is
preserved separately in [review-disposition.json](review-disposition.json).
It is a source-specific delta disposition, not a replacement of the old
findings, another full-MVP review or the author's own acceptance decision.
The reviewer classified **both findings as addressed at `c7764e1`**, found
no high-confidence directly coupled new defect, and recommended
**keep_experimental**. This was static inspection of the corrected source
and regression design, not independent execution of the author's tests or
this campaign. The original MEDIUM severities/confidences and
`needs_correction` recommendation remain attached to `8562b6e`. Refer to the
separate record for the reviewer's exact rationale and limits.

[ownership-stream-audit.json](ownership-stream-audit.json) records
deterministic post-run consistency checks by the coordinator: all 30 native
reports, six actual timeout receipts, 39 scoped subprocess receipts, 120
unchanged sentinels, 12 restoration/conflict witnesses, stream hash/order
and removed runtime directories. This is not independent engineering
review, a global jobs-zero claim, OS isolation or physical acceptance.
Raw private hashes and sanitized public artifact hashes remain distinct.
[artifact-manifest.json](artifact-manifest.json) binds the public package
without self-hashing its own manifest.

No benchmark expansion, baseline weakening, new worker, adapter, install,
CI exemption, supplier action, production project, native geometry change,
simulation/control edit, real export/manufacturing or physical operation
occurred. Catchable cancellation remains exit 130 with retained partial
evidence; no SIGKILL/default-SIGTERM/general-parent-death guarantee is made.
The test-only MVP remains experimental and subject to independent/human
scope limits, with no merge or production/hardware adoption permission.
