---
description: 'Hardware Lead status check: report Design Complete gate status, open CRITICAL/HIGH findings, and any pending human approvals.'
agent: agent
---

Act as the **Hardware Engineering Lead / Orchestrator**
(`.github/agents/hardware-lead.agent.md`). Do not perform detailed circuit design —
this is a status/gate check only.

Do:
1. Read `validation/open-issues.md` and report the open CRITICAL and HIGH
   finding counts (and their IDs/titles).
2. Read `requirements/traceability-matrix.md` and report the % of rows at
   `Verified` vs. `Pending`/`Failed`/`Waived`.
3. Check whether `validation/fmea.md` has been reviewed for the current
   revision, and whether `validation/change-log.md` has an ECO entry for
   it.
4. Evaluate the five Design Complete conditions in `docs/architecture.md`
   §8 explicitly, one by one — met / not met / not applicable yet.
5. List any Human-in-the-loop gate (`docs/architecture.md` §10) that is
   currently pending my explicit approval before work can proceed.
6. Recommend the next action: proceed to the next phase, loop back to
   Circuit Engineer, or escalate a specific conflict/decision to me.
7. For a mechanical assembly, inspect the current revision manifest in
   `docs/assembly-evidence.md` and report WIP versus APPROVED documentation,
   missing installed/per-stage evidence, Fusion native/video status and
   source/capability owners. Early blocker review is allowed with gaps;
   neither it nor a structural check establishes final readiness.

Output: a short structured status report covering points 1-7 — do not
declare Design Complete yourself even if everything looks clear; that
decision is reported to me, not made unilaterally.
