# Contributor and agent entry point

[English](AGENTS.md) | [日本語](AGENTS.ja.md)

This repository contains a hardware-development framework, its design
artifacts, Python checks, embedded C firmware and a scoped simulator. It is
not one application with a universal build command.

## Read only the context needed

1. Read [the common policy](.github/copilot-instructions.md) and applicable
   `.github/instructions/*.instructions.md`. This guide is an index, not a
   second copy of role definitions or safety rules.
2. For engineering work, load the assigned profile in `.github/agents/` and
   its relevant skills. Use [bounded execution](docs/work-execution.md) for
   specialist dispatch. A direct, small tooling/documentation edit does not
   require spawning the engineering team.
3. Read the actual frozen inputs and relevant sections of
   [the workflow](docs/workflow.md). Historical rationale lives in
   `docs/architecture-evolution.md`; do not preload it for every task.

## Find the source of truth

| Work | Entry point |
|---|---|
| Goals, requirements and traceability | `requirements/` |
| Component facts and candidate decisions | `datasheets/` metadata/evidence log and `bom/` |
| Circuits, PCB, power and mechanical models | `hardware/`; preserve their distinct owners and source revisions |
| Driver-level firmware | [firmware/README.md](firmware/README.md) and the target board README |
| Rigid-body simulation | [simulation/README.md](simulation/README.md) and [its scope](docs/simulation.md) |
| Reviews, findings and engineering change history | `validation/`; ECO history is `validation/change-log.md`, not a duplicate root changelog |
| Agent/workflow tooling | `tools/`, `tools/tests/`, `.github/workflows/` |

## Use the existing commands

Run from the intended repository worktree. Python and Git are prerequisites;
metadata/instruction checks also need PyYAML, installed by the existing CI job.
Use the current environment; install a dependency only when needed, not as a
generic setup ritual.

| Changed scope | Command |
|---|---|
| Agent/skill metadata | `python3 tools/check_agent_frontmatter.py` |
| Work contracts, instructions and onboarding | `PYTHONPATH=tools python3 -m unittest discover -s tools/tests -p 'test_*workflow*.py'` |
| Shared Python check/evidence behavior | `PYTHONPATH=tools python3 -m unittest discover -s tools/tests` |
| Canonical Evidence/Issue/ECO namespaces | `python3 tools/check_id_uniqueness.py` |
| Supported mechanical/PCB dimensional pairing | `python3 tools/check_mechanical_pcb_sync.py` |

Choose the smallest applicable scope. These are bookkeeping/software checks,
not native CAD inspection, electrical qualification or physical approval.
For firmware, simulation and native CAD, use their existing scoped instructions
and actual tool availability; do not launch renders or hardware tools for a
workflow-only edit. CI remains in the existing individual workflows, not a
second generic `ci.yml`.

## Finish a contribution

Use the [maintenance matrix](.github/copilot-instructions.md#maintenance-matrix)
to update affected consumers, not every document. Preserve unrelated work and
old evidence. Submit a focused branch/PR using
[the template](.github/PULL_REQUEST_TEMPLATE.md), with actual results and
remaining blockers. A local commit, a pushed branch, a merged PR, task `DONE`
and design/physical approval are different states; report each only from
its own evidence. Never clear a real finding just to make CI green.
