# Command: `make-circuit` — Start a New Circuit Design Cycle

Use this when you (the human Product Owner / Chief Engineer) want to start a
new hardware design cycle and don't want to write the orchestration
instructions from scratch each time.

## 1. Before you run this

Write (or update) your requirements in `requirements/requirements.md` first.
Even a rough draft is fine — Phase 1 (Requirements Engineering) will help
sharpen it. If you don't have a requirements file yet, say so in your prompt
and the Hardware Lead will start there.

## 2. Standard kickoff prompt (copy-paste and adjust the bracketed parts)

```
You are acting as the Hardware Engineering Lead / Orchestrator for this
repository (see .github/agents/hardware-lead.agent.md and .github/copilot-instructions.md).

Requirements are in requirements/requirements.md[, updated for: <what changed>].

Use docs/workflow.md to identify the next dependency-resolving deliverable.
For this run, commission only: <one bounded objective or an explicitly agreed set>.
Do not interpret the full design lifecycle as permission to run indefinitely.

Rules:
- Follow docs/work-execution.md. Before each specialist invocation or
  work-starting follow-up, create its contract and successfully reserve it
  with tools/agent_workflow.py start. Include source/configuration commits,
  relevant inputs, write scopes, deliverables, dependencies, done_when and
  stop_when. A refusal means no dispatch; do not rename the task to bypass it.
- Do not perform detailed circuit design yourself; delegate to the
  Component Engineer, Circuit Engineer, and Hardware Reviewer custom agents
  (.github/agents/*.agent.md) — invoke them natively where supported, or via
  the task tool passing each the relevant .github/agents/*.agent.md +
  .github/skills/*/SKILL.md content explicitly.
- Never guess a component spec. Cite Evidence IDs (datasheets/evidence-log.md)
  for every non-trivial numeric claim. Mark anything unconfirmed as UNKNOWN
  and escalate to me rather than guessing.
- Parallelize candidate research and independent sub-blocks per
  docs/architecture.md section 4; keep integration, requirements sign-off,
  and the review verdict serial. Activate only roles needed now, not every role.
- Resolve upstream interface/source decisions before polishing affected
  downstream evidence. Re-review changed and affected scope after an actual
  fix; an unchanged open finding is not a reason to replay the same review.
- Specialists return shared-ledger proposals; Hardware Lead alone serializes
  canonical publication, without altering independent verdicts.
- Stop and ask me for explicit approval at every Human-in-the-loop gate in
  docs/architecture.md section 10 (architecture decisions, key component
  decisions, missing datasheet, safety-critical changes, major BOM changes,
  before PCB fabrication, before first power-on). Do not proceed past a gate
  without my explicit go-ahead.
- Do not mark the design Design Complete unless every condition in
  docs/architecture.md section 8 holds (no open CRITICAL, HIGH resolved or
  accepted-risk with my sign-off, traceability matrix fully verified/waived,
  FMEA reviewed, ECO logged).
- Save each bounded outcome as DONE or BLOCKED using tools/agent_workflow.py.
  Neither state supplies design/safety acceptance. Once the commissioned work
  is terminal, report and end; do not create new research or patrol work.

Report back to me:
  - the delivered result and current action,
  - remaining blockers, their owners and any specific decision needed,
  - the next stopping boundary and estimated time, or UNKNOWN,
  - and the actual open CRITICAL/HIGH count when it changes.
Use the recorded task status and source-linked results, not comment volume.
```

## 3. Using this with `save_workflow` (scheduled/recurring kickoff)

If the current Copilot surface actually exposes a saved-workflow/scheduling
feature, paste the bounded prompt above into it. Verify that capability at
runtime; a historical `save_workflow` tool name is not a guarantee that it is
available now. This document creates no schedule.

Every scheduled invocation must consult the same repository-local guard.
When inputs and decisions have not changed, report no new dispatch and end
without waking workers. Disable recurring work when its agreed objective is
met; do not use scheduled prompts as an unlimited retry loop.

## 4. Variants

- **Early rigid-body physics / cube simulator**: "Have Hardware Lead
  provide a frozen source intake to Simulation Engineer and run a bounded
  WIP cube/floor/three-wheel experiment using `docs/simulation.md`.
  Do not wait for Design Complete or invent missing actual actuator/mass
  data. Use separate synthetic reference and incomplete design-proxy
  cases, export real trajectories/plots/video, and have a fresh Simulation
  Reviewer inspect the implementation and actual outputs. Simulated
  feedback is not deployable firmware, physical approval or Fusion
  assembly-process animation."

- **Resuming after a Reviewer loop-back**: replace the kickoff paragraph
  with "Resume the design cycle for `requirements/requirements.md`. The last
  Hardware Reviewer verdict was <PASS/FAIL/CONDITIONAL>; open findings are in
  validation/open-issues.md. The changed input/decision is <source-linked delta>.
  Commission <bounded correction>, then independent review of its changed and
  affected scope." — keep the same Rules and Report-back
  sections from §2.
- **Adding a new subsystem to an existing design** (e.g. Motor Driver on top
  of the MCU+IMU+Power benchmark): note explicitly that
  `hardware/power-budget.md` must be updated and re-checked against supply
  capability as part of Circuit Design, and that this likely qualifies as a
  "major BOM change" / architecture decision HITL gate. If the new
  subsystem's power needs may not fit the existing rail(s), consider
  whether Power Engineer should be engaged first
  (`.github/agents/power-engineer.agent.md`, Phase 3 —
  `docs/architecture-evolution.md` §33) to propose the rail architecture
  (`hardware/power-architecture.md`) before Circuit Design starts on the
  power section — this is the Hardware Lead's judgment call per project,
  not automatic for every subsystem addition.
- **Starting WIP Mechanical/assembly planning from identified interfaces**
  (Phase 1 of the multidisciplinary evolution —
  `docs/architecture-evolution.md` §31; `docs/workflow.md` Phase 8-10): when
  required physical interfaces are identified, add to the kickoff:
  "Have Hardware Lead route missing PCB facts through scoped WIP physical
  preparation (Phase 4a), not wait for Design Complete or general routing.
  Use source-linked provisional inputs with explicit gaps; finalized board
  dimensions still require confirmed sources. Have Mechanical Lead populate
  `hardware/mechanical-interface.md` and design an enclosure
  (`.github/agents/mechanical-lead.agent.md`), then get an independent
  Mechanical Reviewer pass (`.github/agents/mechanical-reviewer.agent.md`)
  before Design Complete. Begin WIP assembly-process planning/animation and
  full installed/per-stage evidence early using
  `docs/assembly-evidence.md`, even while explicitly unresolved inputs are
  being sourced. Verify current tool capabilities per operation; deliver
  requested Fusion native storyboards and playable published video, or
  record a precise capability blocker and prepared handoff, not a silent
  substitute. Release APPROVED documentation only after independent
  acceptance, Design Complete and named safety decisions."
