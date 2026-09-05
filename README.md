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
- **For assemblies**: [`docs/assembly-evidence.md`](docs/assembly-evidence.md)
  defines early WIP assembly evidence, requested Fusion native/video
  deliverables and separately gated approved documentation.
- **For cube physics**: [`simulation/README.md`](simulation/README.md) has
  Japanese run/view instructions for the working three-wheel MuJoCo
  simulator; [`docs/simulation.md`](docs/simulation.md) defines its WIP
  source/evidence and independent-review boundaries.

## The agents (14)

| Discipline | Agent | Spec |
|---|---|---|
| Electronics | Hardware Engineering Lead / Orchestrator | [`.github/agents/hardware-lead.agent.md`](.github/agents/hardware-lead.agent.md) |
| Electronics | Component Engineer | [`.github/agents/component-engineer.agent.md`](.github/agents/component-engineer.agent.md) |
| Electronics | Circuit Engineer | [`.github/agents/circuit-engineer.agent.md`](.github/agents/circuit-engineer.agent.md) |
| Electronics | Hardware Reviewer (independent) | [`.github/agents/hardware-reviewer.agent.md`](.github/agents/hardware-reviewer.agent.md) |
| Electronics *(Phase 3)* | Power Engineer | [`.github/agents/power-engineer.agent.md`](.github/agents/power-engineer.agent.md) |
| Electronics *(Phase 6)* | PCB Engineer | [`.github/agents/pcb-engineer.agent.md`](.github/agents/pcb-engineer.agent.md) |
| Mechanical *(Phase 1)* | Mechanical Lead | [`.github/agents/mechanical-lead.agent.md`](.github/agents/mechanical-lead.agent.md) |
| Mechanical *(Phase 1)* | Mechanical Reviewer (independent) | [`.github/agents/mechanical-reviewer.agent.md`](.github/agents/mechanical-reviewer.agent.md) |
| Mechanical *(Phase 4)* | Manufacturing Engineer | [`.github/agents/manufacturing-engineer.agent.md`](.github/agents/manufacturing-engineer.agent.md) |
| Firmware *(Phase 2)* | Firmware Engineer | [`.github/agents/firmware-engineer.agent.md`](.github/agents/firmware-engineer.agent.md) |
| Firmware *(Phase 5)* | Firmware Reviewer (independent) | [`.github/agents/firmware-reviewer.agent.md`](.github/agents/firmware-reviewer.agent.md) |
| Cross-discipline *(Phase 7)* | Systems Engineer | [`.github/agents/systems-engineer.agent.md`](.github/agents/systems-engineer.agent.md) |
| Simulation *(initial rigid-body scope)* | Simulation Engineer | [`.github/agents/simulation-engineer.agent.md`](.github/agents/simulation-engineer.agent.md) |
| Simulation *(initial rigid-body scope)* | Simulation Reviewer (independent) | [`.github/agents/simulation-reviewer.agent.md`](.github/agents/simulation-reviewer.agent.md) |

Electronics is the original 4-agent MVP, extended to 6 with the Power
Engineer (Phase 3, engaged only when a project's power complexity warrants
it) and PCB Engineer (Phase 6, schematic-to-layout handoff — independent
review is Hardware Reviewer's own extended checklist, not a separate PCB
Reviewer agent). Mechanical and Firmware were added later as new top-level
disciplines, once each one's own trigger condition was met (never
speculatively), and each has since grown its own second agent (Manufacturing
Engineer extending Mechanical Reviewer's checklist; Firmware Reviewer as a
genuinely new independent reviewer) — see `docs/architecture.md` §3/§14 and
`docs/architecture-evolution.md` §31/§32/§33/§35/§36/§37.
Systems Engineering owns boundary judgment (§44). The Simulation pair (§45)
adds early rigid-body calculations and visualization, including a
simulation-only controller, without adding a production Control Engineer.

## Repository layout

```
.github/            Copilot instructions, path-scoped rules, custom agent
                     profiles, agent skills, reusable prompts, CI gate
                     workflow, CODEOWNERS
requirements/        Requirements + requirements traceability matrix
datasheets/          Datasheet METADATA only (never the actual copyrighted
                     files — see datasheets/README.md) + Evidence ID log
hardware/            Schematic / PCB artifacts + system power budget +
                     power architecture (Phase 3) + Electronics->Mechanical
                     interface + mechanical/ design artifacts (Phase 1)
bom/                 Component selection / comparison records
firmware/            Driver-level bring-up firmware, one subdirectory per
                     board (Phase 2)
simulation/          Rigid-body model/runner, frozen WIP intake, numerical
                     tests, plotted/video evidence and independent reviews
validation/          Reviews, open issues, FMEA, change log (ECO), change
                     impact matrix, bring-up procedure
docs/                Architecture, workflow, evaluation methodology,
                     standard kickoff prompt
tools/               CI gate parser scripts
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

First benchmark: **MCU + IMU + Power Supply**. The roadmap progresses through
motor drivers, reaction wheels and 1-axis/3-axis attitude control toward a
standing "Cube" — see `docs/architecture.md` §11. Current WIP work includes
a three-axis cube design and a runnable, separately labeled simulator;
neither is a claim of built/qualified hardware. The framework
itself stays reusable for any embedded/robotics/IoT hardware project, not
just this one.
