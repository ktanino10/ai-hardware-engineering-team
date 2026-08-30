# AI Hardware Engineering Team

A reusable, multi-agent **Hardware Engineering Framework** built on GitHub
Copilot: specialized AI agents (not one AI doing everything) carry a
hardware design from requirements through independent review, with every
non-trivial claim grounded in manufacturer datasheets and every major
decision gated by explicit human approval.

This is not "have an AI write a plausible-looking circuit." It's a process:
different agents own different responsibilities so mistakes get caught by a
*different* reasoning pass than the one that made them, and every decision
leaves an evidence trail a human can audit later.

## Start here

- **Read first**: [`docs/architecture.md`](docs/architecture.md) — the
  full architecture: agent roles, evidence model, severity taxonomies,
  Design Complete gate, Human-in-the-loop gates, future roles/integrations.
- **Then**: [`docs/workflow.md`](docs/workflow.md) — phase-by-phase
  process, parallelization rules, conflict resolution.
- **To start a design cycle**: [`docs/commands/make-circuit.md`](docs/commands/make-circuit.md)
  has a copy-pasteable kickoff prompt.

## The four agents (MVP)

| Agent | Spec |
|---|---|
| Hardware Engineering Lead / Orchestrator | [`.github/agents/hardware-lead.agent.md`](.github/agents/hardware-lead.agent.md) |
| Component Engineer | [`.github/agents/component-engineer.agent.md`](.github/agents/component-engineer.agent.md) |
| Circuit Engineer | [`.github/agents/circuit-engineer.agent.md`](.github/agents/circuit-engineer.agent.md) |
| Hardware Reviewer (independent) | [`.github/agents/hardware-reviewer.agent.md`](.github/agents/hardware-reviewer.agent.md) |

## Repository layout

```
.github/            Copilot instructions, path-scoped rules, custom agent
                     profiles, reusable prompts, CI gate workflow, CODEOWNERS
skills/              Standard procedures (requirements engineering,
                     component selection, datasheet analysis, schematic
                     design, hardware review)
requirements/        Requirements + requirements traceability matrix
datasheets/          Datasheet METADATA only (never the actual copyrighted
                     files — see datasheets/README.md) + Evidence ID log
hardware/            Schematic / PCB artifacts + system power budget
bom/                 Component selection / comparison records
validation/          Reviews, open issues, FMEA, change log (ECO), change
                     impact matrix, bring-up procedure
docs/                Architecture, workflow, evaluation methodology,
                     standard kickoff prompt
tools/               CI gate parser script
```

## Key principles

- **Source of Truth**: never guess a spec. Every number traces to a
  manufacturer datasheet (Evidence ID), or is marked `UNKNOWN`.
- **Independent review**: the Hardware Reviewer did not design the circuit
  and actively tries to break it.
- **No fake completion**: a design cannot be marked complete with an
  unresolved CRITICAL finding — enforced by both process and CI
  (`.github/workflows/hardware-gate.yml`).
- **Human-in-the-loop**: architecture, key components, safety-critical
  changes, major BOM changes, pre-fabrication, and pre-power-on all require
  explicit human approval. AI is the Engineering Assistant; the human is
  the Chief Engineer.

## Benchmark project

First benchmark: **MCU + IMU + Power Supply**. Long-term roadmap (not built
yet): MCU + IMU → Motor Driver → Reaction Wheel → 1-axis → 3-axis attitude
control → a standing "Cube" — see `docs/architecture.md` §11. The framework
itself stays reusable for any embedded/robotics/IoT hardware project, not
just this one.

