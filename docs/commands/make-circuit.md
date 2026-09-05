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

Orchestrate the full design cycle end to end:
  Requirements Engineering -> Component Selection -> Datasheet Verification
  -> Circuit Design -> Independent Review -> Validation
per docs/workflow.md, looping Circuit Design <-> Independent Review whenever
a CRITICAL or HIGH finding is open (docs/architecture.md sections 7-8).

Rules:
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
  and the review verdict serial.
- Stop and ask me for explicit approval at every Human-in-the-loop gate in
  docs/architecture.md section 10 (architecture decisions, key component
  decisions, missing datasheet, safety-critical changes, major BOM changes,
  before PCB fabrication, before first power-on). Do not proceed past a gate
  without my explicit go-ahead.
- Do not mark the design Design Complete unless every condition in
  docs/architecture.md section 8 holds (no open CRITICAL, HIGH resolved or
  accepted-risk with my sign-off, traceability matrix fully verified/waived,
  FMEA reviewed, ECO logged).

Report back to me:
  - what phase you're in and why,
  - anything you need my approval on right now,
  - and a running summary of validation/open-issues.md status
    (open CRITICAL/HIGH count) whenever it changes.
```

## 3. Using this with `save_workflow` (scheduled/recurring kickoff)

If you want this kickoff to run automatically on a schedule or on demand
without retyping it (e.g. "every time I add a new requirements revision,
re-run the design cycle check"), use this app's workflow feature
(`save_workflow` / the workflow editor in the UI) and paste the prompt from
§2 above as the workflow's `prompt`. This document only prepares the prompt
text — actually registering a saved workflow (name, schedule, project) is
something you do yourself through the app's UI/tools; nothing here creates
or manages a workflow automatically.

## 4. Variants

- **Resuming after a Reviewer loop-back**: replace the kickoff paragraph
  with "Resume the design cycle for `requirements/requirements.md`. The last
  Hardware Reviewer verdict was <PASS/FAIL/CONDITIONAL>; open findings are in
  validation/open-issues.md. Address open CRITICAL/HIGH findings via the
  Circuit Engineer, then re-review." — keep the same Rules and Report-back
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
