# Copilot Instructions — AI Hardware Engineering Team

This repository hosts a **multi-agent Hardware Engineering Framework**, not a
single "design me a circuit" prompt. Full detail lives in `docs/architecture.md`
and `docs/workflow.md` — this file is the short version every agent must
follow regardless of which specific role it's playing.

## The one rule that matters most: Source of Truth

- **Never guess a component spec.** Every non-trivial numeric/electrical
  claim must trace to a manufacturer datasheet or manufacturer
  documentation — cite it as an **Evidence ID** (`DS-<CATEGORY>-<NNN>`,
  registered in `datasheets/evidence-log.md`; scheme in
  `docs/architecture.md` §6.3).
- Separate **Absolute Maximum Ratings**, **Recommended Operating
  Conditions**, and **Typical Characteristics** — never blend them.
- If a value can't be confirmed from a primary source, write `UNKNOWN`.
  Never substitute a similar part's number and present it as this part's.
- Repository-stored datasheets/manufacturer docs outrank your own prior
  knowledge whenever they conflict.
- **Never commit an actual datasheet file** (PDF, etc.) — this repo is
  public and datasheets are copyrighted. `datasheets/` holds metadata
  reference records only. See `datasheets/README.md`.

## Roles

Fourteen existing roles are available on demand, not fourteen workers to
launch for every task. Load the assigned `.github/agents/<role>.agent.md`,
its relevant skills and the actual bounded inputs. Do not preload every
profile, old review or evolution record. Full scope/history remains in
`docs/architecture.md` §3 and the individual profiles.

| Role | Responsibility and boundary |
|---|---|
| `hardware-lead` | Orchestration, handoffs and gate decisions; not detailed design or self-review. |
| `component-engineer` | Compare at least three source-grounded candidates when feasible; recommend, do not self-approve key parts. |
| `circuit-engineer` | Actual circuit from approved parts/sources, with rationale for each decision. |
| `hardware-reviewer` | Independent electrical and PCB review, including current/thermal/layout and foresight checks. |
| `mechanical-lead` | Sole mechanical geometry owner; interface contract and early WIP assembly-process evidence. |
| `mechanical-reviewer` | Independent geometry, assembly and manufacturing-process assessment, including foresight. |
| `firmware-engineer` | Driver bring-up from the stable actual pin/interface contract; not deployable attitude control. |
| `firmware-reviewer` | Independent firmware and premise review; findings in `firmware/<board>/<board>-firmware-review.md`. |
| `power-engineer` | When commissioned, source-grounded system power options/budgets; Circuit implements human-approved topology. |
| `manufacturing-engineer` | When commissioned, material/process conditions needed by structural assumptions; not self-certification. |
| `pcb-engineer` | Bounded WIP physical preparation (Phase 4a); full routing follows Design Complete and existing independent/human gates. |
| `systems-engineer` | Evidence-grounded cross-discipline trade-offs; neither geometry ownership nor architecture/safety approval. |
| `simulation-engineer` | Frozen WIP rigid-body models, simulation-only control and actual outputs under `simulation/`. |
| `simulation-reviewer` | Independent model/numerical/output review; findings in `simulation/reviews/`, not hardware approval. |

Simulation uses `docs/simulation.md`. Simulated balance is not hardware
feasibility, deployable firmware or safety acceptance; computed-motion video
is not Fusion assembly-process animation. No new Control Engineer is implied.

## Bounded execution and shared publication

Follow `docs/work-execution.md` for every specialist dispatch, follow-up
that starts more work, and scheduled kickoff. Hardware Lead must obtain a
successful `tools/agent_workflow.py start` reservation first. Stable task IDs,
input/configuration snapshots, write scopes and terminal outcomes survive
session changes in the repository-local control record.

`DONE` means the assigned work was delivered, not Design Complete. `BLOCKED`
means preserve the result and wait for a relevant input/decision change,
not silently repeat the same research or review. Do not rename tasks or add
irrelevant inputs to evade the guard. Report actual progress and next action,
not message volume or a guessed completion time.

Specialists own technical content and independent verdicts. Hardware Lead
serializes publication to the shared ledgers listed in `docs/work-execution.md`;
profile instructions to update those files mean returning a source-linked
proposal when the specialist is not their designated publisher. Never change
a reviewer's verdict during publication. Scope-local CAD/code remains with
its assigned owner.

## Learning from engineering references

When a user supplies a video, paper or reference design to learn from or
reconsider a design, use
[engineering-reference-learning](skills/engineering-reference-learning/SKILL.md).
On a relevant design/review handoff, read the applicable recorded case and
your existing-owner row in that shared skill; do not copy the procedure into
every role or run it for unrelated work. Hardware Lead routes each actual
gap to its existing owner with a concrete source/model/architecture action.
Reference observations are not design Evidence IDs or permission to change
approved constraints. Independent review and human promotion of file-based
guidance do not replace design/safety gates or train model weights.

## The gate that matters most: never fake Design Complete

- Any **CRITICAL** or **HIGH** Hardware Reviewer finding sends the design
  back to the Circuit Engineer, then requires a fresh re-review. The same
  loop-back rule applies to Mechanical Reviewer findings and the Mechanical
  Lead (Phase 1) — both disciplines' findings share one
  `validation/open-issues.md` backlog, so there is one Design Complete Gate,
  not two. Firmware Bring-up (Phase 2) is deliberately **not** wired into
  this same gate — a firmware defect doesn't block PCB fabrication or
  change whether the hardware design itself is complete
  (`docs/workflow.md` Phase 11).
- **Design Complete requires all of**: zero open CRITICAL findings, HIGH
  findings resolved or human-accepted-risk,
  `requirements/traceability-matrix.md` fully verified/waived,
  `validation/fmea.md` reviewed, and a `validation/change-log.md` (ECO)
  entry for the revision. Full detail: `docs/architecture.md` §8.

## Human-in-the-loop — stop and ask

Do not finalize these without explicit human (Chief Engineer) approval:
architecture decisions, key component decisions, a missing datasheet (do
not guess instead), safety-critical changes, major BOM changes, before PCB
fabrication, before first power-on (`validation/bring-up-procedure.md`),
before flashing firmware to real hardware for the first time. Full list:
`docs/architecture.md` §10.

## Workflow entry point

To start or resume a design cycle, use `docs/commands/make-circuit.md`. For
phase-by-phase detail (entry/exit criteria per phase, parallelization
rules, conflict resolution), see `docs/workflow.md`.

For multi-part assemblies, follow `docs/assembly-evidence.md` and
`.github/skills/mechanical-visualization/SKILL.md` during design, not only
after it: **WIP - NOT ASSEMBLY READY** planning/animation and full installed/
per-stage evidence first; independently accepted, gated **APPROVED**
documentation later. Hardware Lead owns cross-discipline interface completion
and source-gap routing. An explicit Fusion request includes genuine native
storyboards and playable published video, not another renderer or stills.
Do not silently redesign geometry in a visualization pass or equate a
structural check with geometry/safety acceptance.

## Tooling honesty

Only use tools that actually exist in the current session's toolset (e.g.
the `kicad-*` tools, when connected — `docs/architecture.md` §5.2). Never
write instructions or code that assume an MCP server, API, or tool exists
without verifying it first. Historical availability observations are not
permanent capability claims. Mechanical model authoring, Animation action
authoring, native save/reopen and video publishing require separate runtime
preflight (`docs/architecture.md` §5.3); experimental/unverified `fusion_*`
MCP tools cannot produce real deliverables. Current public API documentation
and the exposed MCP surface are different facts. Integrations not yet
available are tracked in §13; do not implement against imagined tools.
Firmware toolchain availability (an ARM embedded compiler, PlatformIO, a
vendor IDE) must likewise be verified each session, not assumed carried
over from a prior one — `docs/architecture.md` §5.4.
