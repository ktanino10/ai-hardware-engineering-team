# Cancellation-fixed successor: unchanged matched comparison

**120/120 planned trials exercised; A and B again had equal reliability
outcomes. NO_DEMONSTRATED_RELIABILITY_IMPROVEMENT.** The separate cancellation
defect was reproduced and fixed; it was not added to this benchmark to
manufacture an A/B advantage.

| Provenance | Value |
|---|---|
| Frozen successor candidate | `ad5542b43890980bc28c3e589c1a33eb2fdd7394` |
| Configuration | `8a237bb4ef8db300d81c57b3ce11fddcd9d2cabe` |
| Cancellation-fix normal run | `f1b1739e-b02d-4a61-a382-42959ca57354`, DONE |
| Distinct successor experiment normal run | `ff3bcf86-6872-432e-a955-c47d69917d73` |
| Actual measurement window | 2026-09-14T15:24:04.950711Z to 15:25:18.458549Z (2026-09-15 00:24:04 to 00:25:18 JST) |
| Runtime | Darwin/arm64, CPython 3.14.3, native KiCad 10.0.1 |
| Experiment outcome | Exit 0, COMPLETE; no stop reason |

The [original plan](../experiment-plan.json), fixtures, domain rules,
severities, default ignored checks, faults, report oracle, 20 cases and
three-repetition A/B order are byte-identical to the first campaign. Changed
implementation/test bytes are bound to the new candidate in
[frozen-inputs.json](frozen-inputs.json). The
[original ca0f276/7f381cb campaign](../experiment/summary.md) remains
unchanged, with its own outcome and normal DONE record.

## Actual outcomes

| Per-arm measurement | A: strong scripted direct reference | B: wrapper |
|---|---:|---:|
| Planned / attempted / exercised | 60 / 60 / 60 | 60 / 60 / 60 |
| Correct expected outcomes | 60/60 | 60/60 |
| Native domain invocations | 15 | 15 |
| Valid positive-control success | 12/12 | 12/12 |
| False blocking | 0/12 | 0/12 |
| Invalid-output acceptance | 0/30 | 0/30 |
| Forbidden synthetic requests rejected before recorder | 12/12 | 12/12 |
| Exact restore / explicit conflicting-writer refusal | 3 / 3 of 6 | 3 / 3 of 6 |
| Upstream evidence complete at decision time | 57/60 | 57/60 |
| Reproducible scenarios across three repetitions | 20/20 | 20/20 |
| Active trial elapsed, summed | 10.926 s | 10.808 s |
| Native/fault process elapsed component, summed | 9.712 s | 8.943 s |
| Common input-copy/binding setup, separately summed | 24.764 s | 24.154 s |
| Retries / actual human interventions | 0 / 0 | 0 / 0 |
| Synthetic no-action human routes | 12 | 12 |

Each native case ran three times per arm: clean nonempty ERC and DRC each
reported zero violations (exit 0); failing ERC reported two
`pin_not_connected` errors, failing DRC one `tracks_crossing` error, and
the native open-outline fixture one `invalid_outline` error (exit 5).
These are actual domain reports, not load/parse errors called intended
violations. No mandatory native case was missing or replaced by a mock.

The other rows remain explicitly synthetic: missing/restored logs,
stale/fresh direct dependency and historical-only mode, timeout, partial
write/restore/conflict, corrupt output, forbidden requests/approval fixtures
and missing/unsupported capability observations. The three deliberate
missing-log cases per arm account for 57/60 upstream completeness; each
correctly blocked. Historical-only freshness was UNKNOWN/not checked,
never automatically STALE or a current decision approval.

The campaign took approximately 73.51 seconds including setup and evidence
handling. These small timing differences are descriptive, not a performance
or cost advantage. Billing and backend-model identity remain UNKNOWN.
A is a scripted policy-following owner procedure, not a live human/model
trial; its conditional restoration is not manual cleanup credited as
production recovery. Equal reliability metrics remain a no-benefit result.

## Cancellation disposition, separately evidenced

The [cancellation witness and follow-up](../cancellation-followup.md)
record an actual caller SIGINT while waiting on a short-lived owned child.
Before the fix, the child remained alive after unwind and no process receipt
existed. After the fix, owned cleanup and interruption receipts were
preserved, cancellation propagated, and witness-owner cleanup was not needed.
**111 focused tests** passed before freezing this successor, including
transport, adapter, core CLI and campaign interruption behavior.

The CLIs exit 130 and stop later dispatch on catchable cancellation;
partial state is retained, and uncertain cleanup stays explicit. No
uncatchable SIGKILL, default SIGTERM, general parent-death or unrestricted
same-UID protection is promised. No cancellation case was added to the
120-trial denominator. These regressions fix the concrete reliability
finding without changing what the unchanged A/B experiment measured.

## Evidence and limits

[trials.jsonl](trials.jsonl), [metrics.json](metrics.json),
[preflight.json](preflight.json) and
[artifact-manifest.json](artifact-manifest.json) bind the small sanitized
public reports/logs and their distinct public hashes. Raw private hashes
are labeled separately. Report reproducibility removes only the predeclared
`date` field; source/config/tool/result facts are not normalized away.

The [ownership/cleanup consistency check](ownership-cleanup-audit.json)
verified 39 actually started owned subprocess receipts (30 native domain
commands, three preflights and six synthetic timeouts), all associated
temporary runtime directories absent, 120 unchanged sentinels, no forbidden
recorder dispatch and 12 exact restoration/conflict-preservation witnesses.
Failed operations remained failed. This is deterministic post-run
consistency checking by the same coordinator, **not independent engineering
review, a global jobs-zero claim or an OS sandbox guarantee**.

Native clean results cover only the stated fixture rules/defaults; no
schematic/PCB parity, ratings, thermal, assembly, manufacturability or real
Rev5 blocker is accepted. Fontconfig warnings during ERC remain disclosed
in the public log summaries with raw private hashes. No new dependency,
adapter, worker, GUI, production document, real export/physical action,
simulation/control edit or canonical-ledger change occurred. Independent
review and human production adoption remain outstanding; the separate
documentation-inventory integration does not change these outcomes.
