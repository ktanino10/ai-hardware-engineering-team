# Bounded agent work

[English](work-execution.md) | [日本語](work-execution.ja.md) | [Guide index](README.md)

This is the execution contract for `docs/workflow.md`, not another engineering
discipline or a replacement for independent review. Use one coordinator and
only specialists needed by the next dependency-resolving deliverable.
Parallel work must have independent inputs and non-overlapping write scopes.
Do not run all role profiles simply because they exist.

## Before invoking a worker

Hardware Lead records one stable task ID per bounded objective. Freeze the
relevant input files and adopted configuration at immutable Git commits;
do not merge new configuration into an active writer's checkout. Give the
worker the contract, its role/needed skills, source references and affected
scope, not the whole conversation or every historical audit.

Create a JSON contract in the session workspace or ignored `.agent-work/`:

```json
{
  "schema_version": 1,
  "id": "example-interface",
  "owner": "circuit-engineer",
  "objective": "Resolve one explicitly commissioned interface",
  "source_revision": "<full source commit ID>",
  "config_revision": "<full adopted configuration commit ID>",
  "inputs": ["requirements/requirements.md"],
  "writes": [".agent-work/example-interface"],
  "deliverables": [".agent-work/example-interface/handoff.json"],
  "done_when": "Deliver the proposed interface, source basis and remaining limitations",
  "stop_when": "A required source, capability or human decision is unavailable",
  "depends_on": []
}
```

Replace the example inputs with **all actual load-bearing inputs**, including
scoped decision/tool-capability records where relevant. Use narrow source
contracts rather than a giant unrelated history. `writes` contains literal
repository-relative files/directories, not globs; all deliverables must be
within it. A report-only worker can use `.agent-work/<task>/`. This scratch
handoff is not a published engineering record.

For `depends_on`, each producer's declared deliverables must also appear at
the same repository-relative paths in the consumer's `inputs`. Commit those
deliverables before choosing the consumer's `source_revision`; a worktree at
that snapshot must contain the recorded bytes. The guard checks both the
producer's saved files and the consumer's frozen copies. A dependency name
alone does not authorize reading some other worktree or a stale local copy.
Use durable repository paths for deliverables intended as dependency inputs;
ignored scratch reports remain coordinator handoffs, not dependency sources.

From the worker's intended worktree, the coordinator runs:

```sh
python3 tools/agent_workflow.py start /absolute/path/task.json --session coordinator-id
```

Only after exit **0** may the coordinator invoke that specialist once using
the tools actually exposed by its Copilot surface. Retain the returned
`run_id`. The script reserves work; it does **not** invoke, monitor or stop
an agent, install hooks, or change App settings. Custom frontmatter such as
`handoff_to` describes a role, not an executable dependency scheduler.

The guard refuses:

- An already `RUNNING` task or overlapping writers, including across linked
  Git worktrees. Read/write conflicts in the same worktree are also rejected;
  readers on other frozen worktrees may continue on their declared snapshot.
  Scope comparison conservatively treats case/Unicode aliases as identical
  and rejects symlink paths, including on case-insensitive macOS filesystems.
- A dependency without a `DONE` handoff or with missing/changed saved outputs.
- A task previously `DONE` or `BLOCKED` for the same relevant input content
  and dependency handoffs. A new timestamp, session, configuration revision
  or unrelated commit does not make those inputs new.
- Missing/dirty input snapshots or configuration differing from
  `config_revision`. `AGENTS.md`, `.github/`, architecture/workflow/execution instructions,
  the kickoff and the guard itself are checked.

Do not rename the task, delete state, or add irrelevant inputs to bypass a
refusal. Rework needs changed relevant evidence or a recorded human decision.
A genuinely different question gets its own task and explicit dependencies.
An infrastructure repair is a separate bounded task; do not hide it as another
unchanged design review.

## Progress and termination

Record a concise update when a deliverable/decision/blocker changes:

```sh
python3 tools/agent_workflow.py progress RUN_ID --session coordinator-id \
  --summary "Completed X; Y remains" --next-action "Owner/action for Y; estimate UNKNOWN"
python3 tools/agent_workflow.py status
```

Report to the user: **delivered result, current action, remaining blocker and
owner, next boundary/estimate (or UNKNOWN)**. State source/configuration
revisions and unresolved safety holds when material. Count actual resolved
interfaces/findings, not messages, commits or tool calls. Before a long native
operation, disclose its intended output and stopping boundary. Do not invent
an ETA or start a polling/heartbeat agent just to generate activity.

At the bounded handoff, the same coordinator records one terminal result:

```sh
python3 tools/agent_workflow.py finish RUN_ID --session coordinator-id --state DONE \
  --summary "Bounded result saved; independent acceptance remains separate" \
  --next-action "Hand this frozen result to its independent reviewer"
```

Use `--state BLOCKED` instead when a declared stop condition applies, preserving
any partial outputs and stating the **specific changed input/decision needed**.
`DONE` requires every declared deliverable to exist; both terminal states
record hashes of readable regular outputs. `BLOCKED` records explicit errors
for missing, invalid or unreadable outputs and releases the attempt without
repairing or following those paths; `DONE` still rejects them. Hardware Lead must still assess `done_when`:
file existence alone cannot establish that engineering acceptance was met.
`BLOCKED` closes this attempt; it is not an instruction to keep asking or retry.
After all commissioned tasks are terminal, report and end the run. Do not
begin new research, reviewer cycles or patrols without a new commission.

Keep these states separate:

| State | Meaning |
|---|---|
| `RUNNING` | Reserved work with a coordinator; not proof a process is alive. |
| `DONE` | This task's bounded result was delivered. A review can finish with FAIL. |
| `BLOCKED` | This attempt stopped with explicit unmet prerequisites. |
| Design Complete / APPROVED / physical permission | Existing independent and human gates only; never supplied by this tool. |

A review follows a frozen implementation. Re-review covers the changed area
and everything it can affect, as the existing review skills require; do not
replay unchanged numerical/render/source work merely to refresh a timestamp.
Never relabel an old review as acceptance of a changed package.

## One publisher for shared records

Specialists remain the technical authors. They return proposed rows, source
references and verdicts in their scoped handoffs. Hardware Lead reserves a
separate serial publication task before updating:

`datasheets/evidence-log.md`, `validation/open-issues.md`,
`validation/design-review.md`, `validation/change-log.md`,
`requirements/traceability-matrix.md`, `bom/component-selection.md`.

Allocate/reserve canonical IDs once in that integration worktree, publish
reviewer-authored content without changing its meaning, and run the existing
ID/gate checks. Other workers wait for the resulting committed source handoff;
they must not invent IDs or edit these ledgers concurrently. Content ownership
and independent severity/risk decisions do not transfer to the publisher.
Scope-local geometry/code stays with its owner; this rule does not make the
Lead its designer. Other shared files use the same declared write-scope guard.

## Persistence, recovery and limits

State is stored at `<git-common-dir>/agent-workflow/state.sqlite3`, shared by
linked worktrees on this machine, not in committed design files or a chat's
ephemeral todos. `status --history` retains prior attempts; normal `status`
shows the latest attempt per task. Planned but unreserved tasks may use
session todos, but recorded execution state must come from this tool.
Independent clones/machines do not share this database: designate one
dispatch coordinator and publish durable handoffs through Git there.

Status is **recorded state, not live telemetry**. If the App stops, inspect the
actual worker and saved files first. A `RUNNING` reservation never expires
automatically. After confirming the worker is no longer writing, use its
recorded coordinator ID and worktree to close it as `BLOCKED`, with recovery
evidence and next action. Never clear a live reservation to force a retry.
Missing/corrupt state is not permission to assume old work finished.

The guard is an admission check, not an OS permission boundary: callers must
use it before every work-starting dispatch/follow-up, and workers must honor
their scopes. It cannot intercept arbitrary App actions or unmanaged agents.
Existing sessions are not automatically imported or redirected. Adopt this
configuration at a safe handoff/new session, not by rewriting live state.

Agree any time/credit/concurrency ceiling with the user; do not silently
choose one or change their model. Apply supported runtime limits separately.
A soft credit cap is not a guaranteed timer or engineering completion rule.
No hardware gate exemption, required check, merge, fabrication, energization,
first flash, spin/jump or risk waiver is introduced here.
