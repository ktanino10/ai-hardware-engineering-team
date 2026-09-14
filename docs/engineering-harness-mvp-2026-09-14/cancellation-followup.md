# Catchable cancellation follow-up

**Confirmed and narrowly corrected:** after a catchable caller SIGINT raised
`KeyboardInterrupt` inside `run_process.wait()`, the original transport
unwound while its separately-sessioned child was still alive, without
`process.json`. The parent identified this concrete concern in frozen code;
the [owned witness](cancellation-witness.json) reproduced it against
`7f381cb`/`ca0f276` using a short-lived test Python child, not KiCad or a user
process. The witness owner then terminated/reaped only that known child.
That manual witness cleanup is explicitly **not transport recovery**.

Normal follow-up task: `engineering-harness-cancellation-fix-2026-09-15`,
run `f1b1739e-b02d-4a61-a382-42959ca57354`, source
`7f381cb3f68e7adf8fff34484df3ab1ecafb3f4c`, configuration
`8a237bb4ef8db300d81c57b3ce11fddcd9d2cabe`. The already published original
120-trial campaign and its normal DONE receipt are not reopened or rewritten.

## Minimal disposition

- The transport now uses a `finally` path after obtaining the child handle.
  Timeout or catchable caller interruption targets only that Popen-created
  process group, waits/reaps it, and records observed cleanup. Missing group
  observations or an interrupted/failed cleanup remain unverified, not an
  invented empty process list.
- `ProcessInterrupted` retains the available process receipt and remains a
  `KeyboardInterrupt`. Logs remain saved; the adapter records and retains
  its partial runtime rather than publishing it or resuming work.
- Core and experiment CLIs return **130** for caller cancellation. The
  experiment records PARTIAL, preserves the partial trial stream, and does
  not dispatch later cases. Cleanup/receipt uncertainty stays visible.
- Regression tests cover controlled `KeyboardInterrupt`, actual caller
  SIGINT, uncertain owned cleanup, retained adapter state, and CLI/campaign
  stop behavior. The after-fix real SIGINT witness reaped the child,
  retained the process receipt and needed no witness-owner cleanup.

This is not general OS supervision. Uncatchable SIGKILL, default SIGTERM,
parent death, arbitrary same-UID mutation or interruption before a reliable
Popen handle exists are not covered guarantees. Any uncertainty is a stop
and reconciliation condition. No unknown/user PID, GUI, production design,
physical action, extra adapter, installation or worker is involved.

## Preserve the comparison's meaning

The original [campaign](experiment/summary.md) remains byte-identical:
120/120 exercised, equal strong scripted-reference outcomes,
**NO_DEMONSTRATED_RELIABILITY_IMPROVEMENT**. Its bounded result did not
include cancellation coverage and never justified a broader interruption
guarantee.

The successor freezes changed code at a new commit and uses a separately
admitted `experiment-cancellation-successor/` output. It repeats the same
20 cases, three repetitions and two arms with the original plan/fixtures/
physics/rules unchanged. The additional cancellation witness/regressions
remain outside the A/B denominator. Neither new tests nor a later campaign
retrospectively changes the original observations.

Output auditing here and in the original package means **deterministic
post-run consistency checking by the same coordinator**: actual reports,
hashes, output bytes and scoped cleanup receipts were compared. Earlier
wording such as "independently checked" does not mean a separate engineering
reviewer accepted this work. Independent engineering/code acceptance and
human production adoption remain outstanding.
