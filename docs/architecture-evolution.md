# Architecture Evolution — Multidisciplinary Maker Engineering Team (Proposal)

> **Status: PROPOSAL ONLY. Nothing in this document has been implemented.**
> No agent, skill, instruction, workflow, or repository setting was created,
> renamed, or modified to produce it — see "STOP Confirmation" at the end.
> Claims are cited as `[repo: <file>]` (this repo's current state),
> `[gh-docs: <topic>]` (external spec), or `[req §N]` (section N of the
> "Original Prompt" below the addendum) so an independent audit can trace
> each one. Read time target: ~10–15 min; three sections marked
> **DETAILED** get more room because Phase 1 depends on them.
>
> Tags: **[PRESERVE]** unchanged · **[ADD NOW]** documentation-only in
> *this* PR · **[CONSIDER LATER]** plausible, not yet justified ·
> **[DEFER]** postponed, with a trigger · **[DO NOT IMPLEMENT YET]** out of
> scope per the STOP CONDITION.

## 1. Current State

This repository (`ktanino10/ai-hardware-engineering-team`, public) currently
implements one engineering discipline — Electronics — across three merged
PRs:

| PR | Content |
|---|---|
| #1 | Foundation: 4 agents, 5 skills, requirements/BOM/hardware/validation templates, CI gate |
| #2 | Fixed custom-agent profiles to the real GitHub Copilot spec (`.github/agents/*.agent.md`, required `description`) |
| #3 | Fixed agent skills to the real GitHub Copilot spec (`.github/skills/*/SKILL.md`, required `name`+`description`) |

Inventory (verified against the working tree at commit `14e7881`):

| Area | Contents |
|---|---|
| Agents | `.github/agents/{hardware-lead,component-engineer,circuit-engineer,hardware-reviewer}.agent.md` |
| Skills | `.github/skills/{requirements-engineering,component-selection,datasheet-analysis,schematic-design,hardware-review}/SKILL.md` |
| Instructions | `.github/copilot-instructions.md` (repo-wide) + 3 path-scoped `.github/instructions/*.instructions.md` |
| Prompts | 4 reusable `.github/prompts/*.prompt.md` |
| Requirements | `requirements/requirements.md`, `requirements/traceability-matrix.md` |
| Datasheets | `datasheets/README.md` (metadata-only policy) + `datasheets/evidence-log.md` |
| Hardware | `hardware/{schematic,pcb}/README.md`, `hardware/power-budget.md` |
| BOM | `bom/component-selection.md` |
| Validation | `design-review.md`, `open-issues.md`, `fmea.md`, `change-log.md`, `change-impact-matrix.md`, `bring-up-procedure.md` |
| CI/Governance | `.github/workflows/hardware-gate.yml` + `tools/check_open_issues.py`, `.github/CODEOWNERS` |
| Governing docs | `docs/architecture.md` (16 §§), `docs/workflow.md` (5 §§), `docs/evaluation.md`, `docs/commands/make-circuit.md` |

## 2. What Already Works `[PRESERVE]`

- Evidence-first Source of Truth with a stable Evidence ID scheme
  (`DS-<CATEGORY>-<NNN>`) registered centrally `[repo: architecture.md §6]`.
- Independent review with a 4-level severity taxonomy and a mandatory
  loop-back on CRITICAL/HIGH `[repo: architecture.md §2, §7]`.
- A CI gate that mechanically blocks unresolved CRITICAL/unsigned-off HIGH
  findings, not just a documented policy `[repo: hardware-gate.yml,
  verified passing on PRs #1–#3]`.
- Enumerated Human-in-the-loop gates `[repo: architecture.md §10]`.
- Copyright-safe datasheet handling (metadata-only, gitignored binaries)
  `[repo: architecture.md §6.2]`.
- A documented parallel/"Fleet" execution policy `[repo: architecture.md §4]`.
- KiCad tool usage mapped per-agent, per-phase, with an explicit "not
  available today" list (ERC) so capability claims stay honest
  `[repo: architecture.md §5.2, §13]`.
- Repo customization files (agents/skills/instructions/prompts) verified
  against the actual GitHub Copilot spec, not assumed `[repo: PR #2, #3]`.

## 3. What Must Be Preserved `[PRESERVE]`

Directly required by the evolution request `[req §2, §6]`:

- Evidence/Source-of-Truth, independent review, and Human-in-the-loop as
  cross-cutting principles for **every future discipline**, not just
  Electronics `[req §2]`.
- The 4 existing Electronics agents, **as agents**, not collapsed into
  Skills — their future granularity is an evidence question, not decided
  here `[req §6]` (see §9 below).
- The CI gate mechanism and Evidence ID registry as-is.

## 4. Conflicts with Existing Docs

Two genuine tensions were found; neither is a factual contradiction.

1. **Process weight vs. "Maker Mode" mission.** Electronics already
   carries heavyweight artifacts (FMEA/RPN, ECO log, Change Impact Matrix,
   CODEOWNERS on whole directories) justified by a long-term CubeSat
   roadmap `[repo: architecture.md §7.3, §11]`. The new mission asks
   whether that's unnecessary for hobby work `[req §22]`. **Proposed
   resolution**: keep it all as default "Rigorous Mode"; document an
   opt-in lighter "Maker Mode" alongside it (§20). Nothing removed.
2. **Tool coupling vs. Tool Independence.** Circuit Engineer / Hardware
   Reviewer call KiCad tool names directly; no Agent→Capability→Adapter
   layer exists `[repo: architecture.md §5.2]` vs. the new principle
   `[req §11]`. Not a defect — tool-independence was never claimed
   achieved. **Proposed resolution**: defer any adapter until a second
   EDA/CAD tool exists (§14), per Avoid Overengineering `[req §24]`.

No other contradictions found; other new principles (Evidence, Independent
Review, HITL, severity taxonomy) restate or extend `architecture.md` §6–§10.

## 5. Updated Project Mission

The repository's mission grows one level up, without invalidating the
existing one:

- **Repo-level mission (new, this document)**: a multidisciplinary AI
  engineering team for individual makers, following
  IDEA → REQUIREMENTS → DESIGN → BUY → MAKE → TEST → UNDERSTAND → IMPROVE
  (equivalently THINK → MAKE → PROVE → LEARN) `[req §1]`.
- **Electronics-domain mission (existing, unchanged)**: "replace one AI
  writing a plausible-looking circuit" `[repo: architecture.md §1]` —
  still accurate, now understood as one discipline's mission underneath
  the repo-level one.

Classification: **ADDITIVE** — `docs/architecture.md` §1 is not edited.

## 6. Human Owns WHAT/WHY; AI Handles Much of HOW

`[req §3]`. Note: `requirements/requirements.md` already has a priority
column using MoSCoW terms (Must/Should/Could) `[repo:
requirements/requirements.md §2]`, which is functionally equivalent to the
request's MUST/SHOULD/WANT. **Recommendation**: keep the existing MoSCoW
wording (treat "WANT" ≡ "Could") rather than introduce a second, slightly
different vocabulary. MUST requirements remain immutable without a
documented conflict-search + human escalation, consistent with existing
conflict-resolution process `[repo: workflow.md §3]`.

## 7. Proposed Multidisciplinary Architecture

| Discipline | Status | Notes |
|---|---|---|
| System / Orchestrator | **[PRESERVE, renamed conceptually later]** | Still played by Hardware Lead, now across all three disciplines `[repo: hardware-lead.agent.md — unedited; orchestration guidance lives in docs/architecture.md §3/§5.3/§5.4, docs/workflow.md Phase 8-11]`. Still no separate "System Lead" — three disciplines exist now but a rename remains premature until the framework's own need grows further `[req §5, §24]`. |
| Electrical & Electronics | **[PRESERVE]** | Existing 4-agent team, unchanged. |
| Mechanical | **[IMPLEMENTED — Phase 1, see §31]** | First new discipline. Shipped: `mechanical-lead`/`mechanical-reviewer` agents, `enclosure-design`/`mechanical-review` skills, `hardware/mechanical-interface.md`. |
| Independent Reviewer | **[PRESERVE + extended]** | Existing Hardware Reviewer pattern reused for Mechanical (§13, §31) — Mechanical Reviewer is now real, sharing `validation/open-issues.md`. **Deliberately not yet extended to Firmware** (Phase 2, §32) — see §32's own reasoning for why that's a documented, reversible scope decision rather than an oversight. |
| Control / Embedded | **[SPLIT — Firmware sub-slice IMPLEMENTED Phase 2 (§32); Control Engineer sub-slice still DEFER]** | §11 (updated). The two were always distinct future roles in `docs/architecture.md` §14 with separate triggers; only Firmware's trigger ("when firmware work starts in earnest") has been met so far — Control Engineer's ("1-axis/3-axis attitude-control roadmap stage") explicitly has not. |
| Integration / Test | **[DEFER]** | §11. |
| Software/AI, Advanced Concepts, Procurement, Simulation, Visualization | **[CONSIDER LATER / DEFER]** | Only if real projects justify them `[req §5]`; see §16–21. |

## 8. Agent vs Skill vs Instruction vs Interface vs Tool Rules

Rule from the request, reproduced for reference `[req §4]`:

| If a capability mainly... | ...then it is a |
|---|---|
| Represents reusable knowledge/procedure | **Skill** |
| Requires independent responsibility/objective/isolated reasoning or review | **Agent** |
| Applies broadly as a mandatory rule | **Instruction** |
| Connects disciplines | **Interface / Contract** |
| Operates an external system | **Tool / Adapter / MCP** |

Applied retroactively to the current repo:

| Existing element | Type today | Check | Verdict |
|---|---|---|---|
| Hardware Lead | Agent | orchestration, distinct objective | Consistent |
| Hardware Reviewer | Agent | independent review | Consistent |
| Component Engineer, Circuit Engineer | Agent | not obviously "independent review"-shaped | **Open question — explicitly deferred to evidence, not resolved here** `[req §6]` (see §4 item 1's twin, §9) |
| 5 `SKILL.md` files | Skill | reusable procedure/checklist | Consistent |
| `copilot-instructions.md` + `*.instructions.md` | Instruction | repo-wide mandatory rule | Consistent |
| KiCad tool calls | Tool (direct) | operates external system | Consistent, but no adapter layer yet (§4 item 2) |
| *(proposed)* Electronics→Mechanical Interface | Interface | connects disciplines | New — see §13 |

## 9. Electronics Domain `[PRESERVE]`

No changes proposed. Full spec remains `docs/architecture.md` +
`docs/workflow.md` + the 4 agent/5 skill files. Future Electronics-adjacent
roles (Power/PCB/Firmware/Control/Test Engineer, Datasheet Specialist,
Safety/Compliance Reviewer) are already documented with introduction
triggers and are unaffected by this document `[repo: architecture.md §14]`.
The Component-Engineer/Circuit-Engineer Agent-vs-Skill question (§8) should
be evaluated empirically once there is more than one completed design
cycle to compare — using the metrics already defined in
`docs/evaluation.md`, not new ones.

## 10. Mechanical Domain `[IMPLEMENTED — Phase 1, see §31]`

Full concept list from the request `[req §7]`: spatial layout, enclosure,
mechanism, assembly, geometry, mounting, fasteners, clearances, tolerance,
interference, manufacturing constraints, material selection,
3D-print manufacturability, motion/joints.

- Start as **Skills** under one **Mechanical Lead** who owns a single
  coherent geometry/CAD state — not multiple independent mechanical
  agents corrupting the same model `[req §7]`.
- Phase 1 subset only (see §13): PCB mounting, connector accessibility,
  component-height clearance, wall thickness, fastener placement, basic
  manufacturability. The rest of the list is **[CONSIDER LATER]**, added
  only when a real project needs it.
- **Status update (Phase 1 implemented, §31)**: `.github/agents/
  mechanical-lead.agent.md` (the single geometry-state owner, per the
  bullet above) + `.github/skills/enclosure-design/SKILL.md` (its
  procedure, bundling the Phase 1 subset above into one skill) now exist.
  A second agent, **Mechanical Reviewer** (`.github/agents/
  mechanical-reviewer.agent.md` + `.github/skills/mechanical-review/SKILL.md`),
  was also added — this is not "multiple independent mechanical agents
  corrupting the same model" (still avoided: only the Lead owns geometry),
  it mirrors the *already-approved* Circuit-Engineer/Hardware-Reviewer
  2-agent split (design + independent adversarial review), consistent with
  this table's own "Independent Reviewer" row (§7) and §27 item 3.

## 11. Future Control / Embedded Domain `[DEFER — Firmware sub-slice now IMPLEMENTED, see §32]`

`[req §10]`. This section originally reserved "Control / Embedded" as one
undifferentiated future discipline. **Status update (§32)**: it has since
split into the two future roles `docs/architecture.md` §14 always listed
separately, each with its own trigger — **Firmware Engineer** ("when
firmware work starts in earnest") and **Control Engineer** ("at 1-axis/
3-axis attitude control roadmap stage"). Only Firmware Engineer's trigger
has been met (Bench-IMU-01 reached Design Complete); Control Engineer's has
not (no reaction wheel/motor/attitude-control project exists) and remains
`[DEFER]` exactly as originally written below — nothing in this section's
original Control-Engineer-relevant content changes.

Reserved as a discipline; no Control Engineer agent/skill created. Firmware
frameworks/boards (Arduino, PlatformIO, Pico SDK, ESP-IDF, ESP32,
Raspberry Pi, Jetson) are to be treated as replaceable providers, consistent
with Tool Independence (§14) — not decided now, just noted so a future
Control discipline doesn't get architecturally pinned to one board. (The
Firmware Engineer role implemented in §32 is consistent with this too — it
is bare-metal C for the specific MCU already selected during Component
Selection, not architecturally pinned to any of the frameworks named
above.)

**Integration / Test** `[DEFER]`: reserved per `[req §5]`. The existing
`validation/bring-up-procedure.md` already covers Electronics-only bring-up
`[repo: bring-up-procedure.md]`; a future cross-discipline Integration/Test
role would extend its scope, not replace it.

## 12. GitHub as Engineering Control Plane, and the Source-of-Truth Boundary `[ADD NOW — documentation only]`

`[req §12]`: the file tree remains Source of Truth for **evidence and
design state** (`requirements/`, `datasheets/evidence-log.md`, `bom/`,
`validation/`, `hardware/`), unchanged from `architecture.md` §6. GitHub
**Issues/PRs** are a complementary layer for **work-item tracking and
change history** — not a duplicate evidence store. An Issue can say
"design the IMU power rail," but its Evidence IDs still live in
`evidence-log.md`; the PR just points at the commit. Verified: Issues are
already enabled (`has_issues: true`), no setting change needed.
**[CONSIDER LATER]**: an Issue template requiring an Evidence ID field,
once volume justifies it.

## 13. Electronics → Mechanical Interface **DETAILED**

`[req §8]`, minimum set for the first benchmark only, per the request's own
instruction not to invent unneeded fields:

| Field | Why needed for the benchmark |
|---|---|
| PCB length, width, thickness | Enclosure inner dimensions |
| Board outline (bounding box acceptable for v1) | Fit check |
| Mounting hole positions + diameters | Fastener placement |
| Max component height, top and bottom | Enclosure clearance |
| Connector locations + orientation | Cutouts, cable exit |
| Switches / LEDs needing a cutout | Cutouts |
| Approximate mass | Basic mechanical sizing |
| Evidence source, assumption, confidence | Same UNKNOWN/ASSUMPTION convention as Electronics `[repo: architecture.md §6]`, extended to a new domain — not a new rule |

Explicitly **[DEFER]** for v1 (add only if the benchmark shows they're
needed): thermal zones, antenna keep-out, STEP/neutral 3D model reference,
center of mass, battery wiring requirements, complex keep-out zones,
detailed cable-exit geometry.

Implemented (Phase 1, see §31): `hardware/mechanical-interface.md`,
reusing the existing `Parameter | Value | Unit | Source` table convention
plus explicit `Confidence` and `Assumption / Notes` columns (four labels:
`CONFIRMED`/`ASSUMPTION`/`ESTIMATE`/`UNKNOWN` —
`.github/instructions/mechanical-design.instructions.md`). **Classification:
ADDITIVE** (new file only). Template only — no real project has been run
through this repo's cycle yet, so all rows are still blank (§27 item 5).

## 14. Tool / Model Independence

`[req §11, §13]`. Target shape: Agent → Domain Skill → Abstract Capability
→ Adapter → Tool/MCP/API. Today: KiCad tools are called directly by name,
no adapter layer (§4). **[DEFER]** introducing an adapter until a second
EDA or CAD tool is actually connected — building one for a single, current
tool is exactly the overengineering the request warns against `[req §24]`.
Model independence is **already true today**: no `.agent.md` file pins a
`model:` field (verified) — nothing to change `[PRESERVE]`.

### Explainable Selection `[DEFER]`

`[req §13]`. A future minimal execution-record (task, agent, skill, tool,
model, reason, alternatives, confidence, actual result) is a reasonable
future direction, not built now. No router, no registry.

## 15. Procurement `[DEFER]`

`[req §14]`. Component Engineer already partially separates "technically
appropriate" from "available/EOL/lifecycle" `[repo:
component-engineer.agent.md]`. No separate Procurement agent/skill yet;
split out only when multi-supplier comparison or BOM complexity actually
demands it. No automated purchasing, ever, without the existing "major BOM
change" human gate `[repo: architecture.md §10]`.

## 16. Simulation and Real-Hardware Validation

`[req §15]`. No simulation tool is connected today; SPICE remains Future
Integration `[repo: architecture.md §13, verified — no SPICE tool in this
session's toolset]`. The requested AI→Firmware→Device→Measurement→AI loop
is a reasonable long-term direction; the *principle* behind it — measured
data outranks AI confidence — already exists via the Source-of-Truth rule
`[repo: architecture.md §6]` and is simply **[PRESERVE]**d, not newly
added. **[DEFER]** building any bench infrastructure.

## 17. Engineering Visualization / Animation `[DEFER]`

`[req §16]`. No visualization tool connected today. Principle worth
preserving prospectively: never invent physical behavior for presentation
— a direct extension of the existing no-guessing rule `[repo:
architecture.md §6]` to visuals, once any visualization exists.

## 18. Future Digital Twin / XR `[DO NOT IMPLEMENT YET]`

`[req §17]`. No engine (Unity/Unreal/Blender or similar) is connected in
this environment — nothing is claimed available. Nothing in the current
file+Evidence-ID model appears to block a future semantic assembly model,
but this is unverified since none exists yet.

## 19. Value Engineering & Improvement `[CONSIDER LATER]`

`[req §18]`. Proposed as Skills (value-engineering, design-improvement,
next-generation-concepts) under existing disciplines — meaningful only
once at least one design revision has actually shipped to improve upon.
Not needed before Phase 1 completes.

### Advanced Concepts / Next Generation `[DEFER]`

`[req §19]`. Explicitly not implemented now, per the request. Distinct
objective from Hardware Reviewer (Reviewer finds defects in *this* design;
Advanced Concepts would challenge whether this is the right design
approach at all) — no overlap, just not yet justified with only one design
lineage in existence.

## 20. Continuous Improvement / Long-Term Learning `[DEFER]`

`[req §20]`. `docs/evaluation.md` already defines the metrics a future
learning system would consume (Evidence Coverage Rate, Reopen Rate, FMEA
Predictive Validity, etc.) `[repo: evaluation.md §2.1]` — a future learning
system should read *those*, not invent new metrics. The requested
Observe→Analyze→Propose→Sandbox→Benchmark→Independent
Review→Human Approval→Promote pipeline is, notably, a good description of
how this very document's own proposals should eventually be handled — not
built now.

## 21. Security

`[req §21]`. Verified live repository settings (via GitHub API, this
session):

| Setting | Status |
|---|---|
| Secret scanning | Enabled |
| Secret scanning push protection | Enabled |
| Dependabot security updates | Disabled |
| CodeQL | Not configured (no application code to scan yet) |
| CI workflows | 1 (`hardware-gate.yml`; no external network/credential use) |

**[PRESERVE]** existing protections. **[CONSIDER LATER]** Dependabot once
any dependency manifest exists (none today). **[ADD NOW — documentation
only]**: a one-paragraph tool-trust checklist for *future* MCP/CAD/
distributor integrations (source, permissions, filesystem/network/shell
access, credentials) — an extension of the existing HITL principle to
tool-adoption, not a new governance body `[req §21 rejects a "Security
Department"]`.

## 22. Maker Mode `[ADD NOW — documentation only, not yet written into workflow.md]`

`[req §22]`, resolving §4 item 1. Recommend defining two named tracks in a
future `docs/workflow.md` revision (not changed by this document):

| | Maker Mode | Rigorous Mode (current default) |
|---|---|---|
| Requirements | Informal, evidence still required | Full `requirements.md` + traceability matrix |
| FMEA / RPN | Skipped | Required |
| ECO | Only for non-trivial changes | Required every revision |
| Review | One independent pass | Full checklist + `rubber-duck` |
| CODEOWNERS gate | Optional (solo projects) | As configured today |
| Pre-power-on human approval | **Always required, both modes** | Always required |

Nothing existing is removed; this is a documented lighter *opt-in* path,
human-selected per project.

## 23. Repository Naming Recommendation

`[req §23]`. Considered: rename to `ai-maker-engineering-team`.

- **Advantages**: matches the broader mission (§5); avoids implying
  Electronics-only scope.
- **Disadvantages**: GitHub auto-redirects old URLs (low technical risk),
  but every existing PR description, commit message, and this very
  document's citations reference the current name; premature before any
  non-Electronics discipline exists in the repo.
- **Recommendation: DEFER.** Revisit once Phase 1 (Mechanical) ships and
  the repo demonstrably serves ≥2 disciplines. Renaming remains a
  human-approved decision either way `[req §23]`.

## 24. First Vertical Slice / Benchmark **DETAILED**

`[req §9]`. Continues the *existing* benchmark, does not replace it
`[repo: architecture.md §11, MCU + IMU + Power Supply]`:

```
Requirement (existing) → Electronics workflow (unchanged, §9 above)
  → PCB/electronics definition → Electronics→Mechanical Interface (§13)
  → Mechanical design (new) → Independent Mechanical review (new)
```

Success bar (must exceed "a box with holes") `[req §9]`:

| Must evaluate | Current capability |
|---|---|
| PCB mounting | New (Mechanical, Phase 1) |
| Connector accessibility | New |
| Component height clearance | New |
| Internal clearance / interference | New |
| Fastener placement | New |
| Wall thickness | New |
| Assembly order | New |
| Tolerance | New |
| Basic manufacturability / 3D-printability | New |

Benchmark question (verbatim from the request): *"Can this AI engineering
system create a believable, buildable enclosure from real electronics
information?"* `[req §9]` This is the Phase 1 pass/fail criterion, judged
by the human Chief Engineer, not by AI self-assessment — consistent with
existing independent-review + HITL principles.

**Status (Phase 1 PR, §31)**: the agents/skills/interface/docs needed to run
this benchmark now exist. Actually *running* it — producing a real, judged
enclosure for a real MCU+IMU+Power project — is **not done in this PR**: no
real project has entered this repo's design cycle yet (`requirements/
requirements.md` and `bom/component-selection.md` are still blank
templates), and running the benchmark would require the Electronics cycle to
run first, which is outside this PR's "Mechanical only" scope. Flagged as
the natural next PR/session (§27 item 5).

## 25. Risks

- **Scope creep** from 29 topics — mitigated by the STOP CONDITION and the
  PRESERVE/ADD NOW/CONSIDER LATER/DEFER tags throughout.
- **Process-weight mismatch** for casual hobby work — mitigated by the
  proposed Maker Mode (§22, unimplemented).
- **Naming churn** if renamed early then reversed — mitigated by DEFER (§23).
- **Fictional tool capability** claims — mitigated by continuing the
  Future Integration convention `[repo: architecture.md §13]` and §26.
- **Speculative agent proliferation** in Mechanical — mitigated by
  starting it as Skills under one Lead (§10), per `[req §24]`.

## 26. Deferred Ideas / DO NOT IMPLEMENT YET (consolidated)

Dynamic model router · capability registry · automated benchmark
infrastructure · Digital Twin / XR · Advanced Concepts Agent · automated
procurement/purchasing · multiple Mechanical sub-agents · a tool-adapter
abstraction layer (until a 2nd tool exists) · a self-rewriting learning
system · visualization/animation tooling · Value Engineering skills (until
≥1 completed revision exists) · Control/Embedded discipline · Integration/
Test agent · Issue-form templates · Dependabot (until a dependency
manifest exists) · repository rename.

## 27. Phase 1 Implementation Plan (implemented — see §31)

`[req §27]`. Scope, as approved by the human and implemented in this PR:

1. ✅ **Done.** Preserve current Electronics team — no code change (verified:
   `git diff` confirms the 4 existing agent files, 5 existing skill files,
   `.github/instructions/{hardware-design,datasheets}.instructions.md`,
   `.github/workflows/hardware-gate.yml`, `tools/check_open_issues.py`,
   `datasheets/**`, `requirements/**`, `bom/component-selection.md`,
   `hardware/{power-budget.md,schematic/README.md,pcb/README.md}`,
   `validation/{fmea.md,change-log.md,change-impact-matrix.md,
   bring-up-procedure.md}` are all byte-identical to before this PR).
2. ✅ **Done.** Added Mechanical capability as **Skills** under one
   **Mechanical Lead** agent (§10): `.github/agents/mechanical-lead.agent.md`
   + `.github/skills/enclosure-design/SKILL.md`. No CAD MCP tool was found
   verified-connected at Phase-1-implementation time (checked, not assumed —
   see §31), so the Mechanical Lead produces text/parametric output (an
   OpenSCAD-style script + a dimensional-spec table), exactly the fallback
   this item anticipated `[req §11, §24]`.
3. ✅ **Done.** Added **Mechanical Reviewer** agent, independent from the
   Mechanical Lead, mirroring the existing Hardware Reviewer pattern (§7
   discipline table): `.github/agents/mechanical-reviewer.agent.md` +
   `.github/skills/mechanical-review/SKILL.md`.
4. ✅ **Done.** Defined `hardware/mechanical-interface.md` (§13) — template
   only, no live project data (see item 5).
5. ⏳ **Not done in this PR — flagged follow-up.** Continuing the existing
   MCU+IMU+Power benchmark through to a real enclosure (§24), judged against
   the 9-point checklist in §24, requires a real Electronics design cycle to
   have run first (`requirements/requirements.md` is still a blank
   template), which is outside this PR's "Mechanical only" scope.
6. Explicitly out of scope for Phase 1 (unchanged, still deferred): Control/
   Embedded, Procurement automation, Simulation, Visualization, Digital
   Twin, model routing, repository rename, multiple Mechanical sub-agents
   (only 2 Mechanical agents exist: Lead + Reviewer, the same 2-agent
   design+independent-review shape as Electronics' Circuit Engineer +
   Hardware Reviewer).

Items 1-4 were implemented in this PR; per the STOP CONDITION and the
requester's own addendum, it still awaits an independent audit and explicit
human approval before merge (not before creation — the files already exist,
open for review, exactly as the requester's process for this document itself
anticipated).

## 28. Change Classification

| Proposed change | Classification | Reason |
|---|---|---|
| This document | ADDITIVE | New file; no existing file modified |
| Repo-level mission (§5) | ADDITIVE | `architecture.md` §1 unchanged |
| Mechanical Lead + Mechanical Reviewer (Phase 1, **implemented**, §31) | ADDITIVE | New agents; nothing removed/renamed |
| `hardware/mechanical-interface.md` (Phase 1, **implemented**, §31) | ADDITIVE | New file |
| `docs/architecture.md` / `docs/workflow.md` Phase 1 updates (§31) | ADDITIVE | New diagram nodes/rows/sections/phases only; no existing section renumbered or reworded |
| Small shared-file edits: `validation.instructions.md`, `validation/open-issues.md`, `validation/design-review.md`, `.github/CODEOWNERS`, `.github/copilot-instructions.md` (§31) | ADDITIVE / BACKWARD_COMPATIBLE | Extend an enum/placeholder/list; no existing row/rule/table schema removed or changed |
| Maker Mode documentation (§22, unimplemented) | ADDITIVE | New optional path; Rigorous Mode unchanged |
| Tool adapter layer | NOT PROPOSED NOW | Deferred to §14's trigger condition |
| Repository rename | BREAKING, if ever done | Recommended DEFERRED (§23) |
| Component/Circuit Engineer Agent-vs-Skill status | UNDETERMINED | Explicitly deferred to evidence (§9), not a proposed change |

## 29. Final Review Questions — Answered

`[req §28]`

1. **Preserves working Electronics architecture?** Yes — no Electronics
   file is modified (§3, §9).
2. **Independent Agents only where independent reasoning adds value?**
   Yes for existing/proposed reviewers (§8); Component/Circuit Engineer
   status stays an open, evidence-based question (§9).
3. **Reusable techniques as Skills instead of unnecessary Agents?** Yes —
   Mechanical starts as Skills under one Lead (§10).
4. **Tools replaceable without redesigning the architecture?** Partially
   today (no adapter yet); acceptably deferred per Avoid Overengineering
   (§14).
5. **AI models replaceable without losing project knowledge?** Yes — no
   agent pins a model; all durable knowledge is file-based (§14, §12).
6. **Can Electronics communicate enough to Mechanical?** Yes for the
   stated benchmark — minimum field set defined and now implemented as
   `hardware/mechanical-interface.md` (§13, §31).
7. **Can Mechanical exceed "a box with holes"?** That was the explicit
   Phase 1 pass bar (§24); the agents/skills/checklist needed to attempt it
   are implemented (§31) — the benchmark run itself is a flagged follow-up.
8. **Can future Control/Firmware fit naturally?** Yes — reserved,
   unblocked (§11).
9. **Can future visualization fit naturally?** Yes in principle, unbuilt,
   unblocked (§17).
10. **Can future Digital Twin/XR fit without restructuring?** Likely,
    unverified — nothing built yet (§18).
11. **Can procurement be added without supplier coupling?** Yes — no
    supplier is hard-coded anywhere today (§15).
12. **Is security appropriate for a hobby Maker environment?** Yes —
    verified protections already on, no security department proposed
    (§21).
13. **Simple enough for one person to maintain?** Existing Electronics
    discipline is already fairly detailed — this is exactly why Maker Mode
    is proposed (§4, §22).
14. **Future ideas clearly separated from current implementation?** Yes —
    every section is explicitly tagged (§26 consolidates).
15. **Does Phase 1 result in a real, testable workflow?** Yes — implemented
    (§27, §31), with a concrete pass/fail benchmark defined (§24); running
    that benchmark to a judged result is the flagged follow-up (§27 item 5).

## 30. STOP Confirmation

Per the STOP CONDITION: this document is the only file added or changed.
No agent, skill, instruction, or workflow was created or modified; the
repository was not renamed; no MCP, CAD, Mechanical, Procurement, Digital
Twin/XR, or model-routing capability was implemented. Awaiting independent
audit and explicit human approval before Phase 1 (§27) begins.

*(This section is preserved verbatim as the historical record of this
document's original, plan-only state. See §31 immediately below for what
actually changed once Phase 1 was approved and implemented.)*

## 31. Phase 1 Implementation Status (Addendum)

Added when Phase 1 (Mechanical) was actually implemented, in a separate PR
from this document's original merge — kept as an addendum rather than
rewriting §30 above, to preserve the audit trail of what this document said
*before* approval vs. what is true *after* implementation.

- **Human approval**: given, scoped explicitly to Mechanical only (per the
  kickoff instructions for that PR) — Control/Embedded, Procurement,
  Simulation, Visualization, Value Engineering, Advanced Concepts, Digital
  Twin/XR remain exactly as documented above (deferred), untouched.
- **Implemented**: §27 items 1-4 — see the ✅ markers in §27, and the status
  updates inline in §7, §10, §13, §28, §29.
- **Not implemented / flagged follow-up**: §27 item 5 (running the
  MCU+IMU+Power benchmark through to a real, judged enclosure) — no real
  project has entered this repository's design cycle yet.
- **Verified, not assumed, during implementation**: (a) the GitHub custom
  agent (`.github/agents/*.agent.md`, required `description`) and agent
  skill (`.github/skills/<name>/SKILL.md`, required `name`+`description`)
  specs were re-checked directly against current GitHub documentation — both
  unchanged since PR #2/#3, no third "fix the spec" round was needed; (b) no
  CAD/3D modeling tool is connected in this environment — a live connection
  check (`blender-get_addon_status`) failed ("Could not connect to
  Blender"), and no local `openscad`/`freecad` binary or
  `cadquery`/`solid`/`build123d` Python library is installed; see
  `docs/architecture.md` §5.3/§13 for where this is now tracked as Future
  Integration.
- **Files added**: `.github/agents/{mechanical-lead,mechanical-reviewer}.agent.md`,
  `.github/skills/{enclosure-design,mechanical-review}/SKILL.md`,
  `.github/instructions/mechanical-design.instructions.md`,
  `hardware/mechanical-interface.md`, `hardware/mechanical/README.md`, plus a
  separable repo-hygiene addition (not Mechanical-specific — guards every
  discipline's agents/skills equally): `tools/check_agent_frontmatter.py` +
  `.github/workflows/agent-frontmatter-lint.yml`, a permanent CI check that
  every `.agent.md` has a `description` and every `SKILL.md` has a matching
  `name`+`description`, so a third "wrong spec" round (after PR #2/#3) can't
  happen silently again.
- **Files edited, additively only** (nothing existing removed/reworded, no
  section renumbered): `docs/architecture.md` (§2, §3, new §5.3, §10, §13,
  §16), `docs/workflow.md` (§1 diagram, new Phase 8-10 under existing §2,
  §4, §5), `docs/architecture-evolution.md` (this document — §7, §10, §13,
  §24, §27, §28, §29), `.github/copilot-instructions.md` (Roles section),
  `.github/CODEOWNERS` (one line), `.github/instructions/
  validation.instructions.md` and `validation/{open-issues.md,
  design-review.md}` (extending the `Source` enum / genericizing two
  template lines — table headers/schemas unchanged, so
  `tools/check_open_issues.py` needed no change and still passes).
- **Confirmed untouched** (verified via `git diff` before opening the PR):
  all 4 existing `.github/agents/*.agent.md` files (including
  `hardware-lead.agent.md`, by explicit human confirmation during planning
  — Hardware Lead's cross-discipline orchestration is documented entirely in
  `docs/architecture.md`/`docs/workflow.md`, which it already treats as
  canonical), all 5 existing `SKILL.md` files,
  `.github/instructions/{hardware-design,datasheets}.instructions.md`,
  `.github/workflows/hardware-gate.yml`, `tools/check_open_issues.py`,
  `datasheets/**`, `requirements/**`, `bom/component-selection.md`,
  `hardware/{power-budget.md,schematic/README.md,pcb/README.md}`,
  `validation/{fmea.md,change-log.md,change-impact-matrix.md,
  bring-up-procedure.md}`, `docs/evaluation.md`.
- **Status**: implemented, PR opened, awaiting independent audit before
  merge — same process this document itself went through.

## 32. Phase 2 Implementation Status (Addendum — Firmware)

Added when Phase 2 (Firmware) was actually implemented, in a separate PR
from both this document's original merge and the Phase 1 (§31) addendum —
kept as its own addendum for the same reason §31 is one: preserve the
audit trail of what was true before this phase vs. after.

- **Trigger met**: `docs/architecture.md` §14's Firmware Engineer trigger
  ("when firmware work starts in earnest") was satisfied by
  `hardware/schematic/bench-imu-01-design.md` (Rev 2) reaching Design
  Complete and merging to `main` (PR #6) — a real, existing schematic with
  fixed pin/interface decisions to build driver-level bring-up firmware
  against, not a speculative addition.
- **Human approval**: given, scoped explicitly to Firmware Engineer only —
  Control Engineer, Firmware Reviewer, PCB Engineer, Power Engineer, Test
  Engineer, Datasheet Specialist, and Safety/Compliance Reviewer all remain
  exactly as `docs/architecture.md` §14 documents them (deferred, untouched
  triggers), per the kickoff scope for this PR.
- **Explicit human decision (asked via `ask_user`, not silently assumed)**:
  no Firmware Reviewer agent is introduced this round — Firmware Engineer's
  own rigorous self-check (`.github/skills/firmware-bringup/SKILL.md`'s
  checklist) stands in for independent review until a documented future
  trigger is met (a second board's firmware, or a bring-up failure traced
  to a class of defect an independent pass would likely have caught — see
  `docs/architecture.md` §14's now-added Firmware Reviewer row). This is a
  deliberate, scope-proportionality decision, not an oversight: unlike
  Mechanical (§27/§31), which mirrored the already-approved
  design+independent-review 2-agent shape from the start, Firmware's
  actual scope this round (one MCU, one bring-up program for one bench
  board) is closer in scale to the "single real supporting part, no full
  comparison needed" precedent this project already used for the ESD
  protection IC during Circuit Design than to a whole new parallel
  discipline needing its own adversarial agent immediately. A concrete,
  non-speculative trigger is recorded rather than deferred indefinitely.
- **A real, non-obvious technical reason also supported this decision**:
  this repository's `validation/open-issues.md` is one shared backlog whose
  CI gate (`tools/check_open_issues.py`) blocks on *any* open
  CRITICAL/HIGH row regardless of which reviewer wrote it — correct and
  intentional for Mechanical ("one gate, not two," since a Mechanical
  finding can mean the same physical PCB needs to change), but a Firmware
  finding is different in kind: it does not block PCB fabrication or the
  existing Design Complete Gate. Writing Firmware Reviewer findings into
  that same table as-is would let an unrelated firmware bug silently block
  unrelated hardware-only pull requests forever — a real coupling defect,
  not a style preference. Properly avoiding that would need either a
  separate firmware-scoped backlog/CI check or a `Source`-based carve-out
  in `check_open_issues.py`, neither of which is justified building yet for
  a role that doesn't exist this round.
- **Verified, not assumed, during implementation** (mirroring §31's own
  "verified, not assumed" bullet, for the same reasons):
  (a) the GitHub custom agent (`.github/agents/*.agent.md`, required
  `description`) and agent skill (`.github/skills/<name>/SKILL.md`,
  required `name`+`description`) specs were re-fetched directly from
  current GitHub documentation this session — both unchanged since PR
  #2/#3/§31, no fourth "fix the spec" round was needed;
  (b) no ARM embedded toolchain, PlatformIO, or STM32CubeIDE/CubeMX was
  pre-installed in this environment — checked, not assumed — but
  `arm-none-eabi-gcc` was confirmed **installable** via a bottled Homebrew
  formula, installed, and used to produce a real, zero-warning build (see
  `firmware/bench-imu-01/bench-imu-01-firmware-design.md` §0/§7 for the
  full account, including a genuine `-lgcc`/software-divide link error the
  real build surfaced and this session fixed — stronger evidence than
  read-through alone would have produced);
  (c) no physical Bench-IMU-01 board exists to flash or power on in this
  environment — the same tooling-honesty convention §31 established for
  Mechanical's CAD tooling, now extended to Firmware
  (`docs/architecture.md` §5.4);
  (d) the BMI270's mandatory configuration-file upload sequence (soft
  reset → disable advanced power save → chunked, word-addressed upload of
  an 8192-byte manufacturer blob → poll for load success) was independently
  confirmed against Bosch's own official open-source driver source code
  before being implemented, rather than assumed from a simplified
  description — the opaque blob itself was vendored verbatim with full
  attribution (BSD-3-Clause, already this project's own SDK-ecosystem
  evidence for this part since Component Selection, `DS-IMU-017`), never
  approximated.
- **Files added**: `.github/agents/firmware-engineer.agent.md`,
  `.github/skills/firmware-bringup/SKILL.md`,
  `.github/instructions/firmware.instructions.md`, the new top-level
  `firmware/` directory (`firmware/README.md`,
  `firmware/bench-imu-01/{README.md,
  bench-imu-01-firmware-design.md, Makefile, linker/, src/}`), three new
  datasheet metadata records
  (`datasheets/stmicroelectronics_cmsis_device_g0_master.md`,
  `datasheets/boschsensortec_bmi270_sensorapi_v2.86.1.md`,
  `datasheets/stmicroelectronics_an4235_i2c-timing-configuration-tool.md`).
- **Files edited, additively only** (nothing existing removed/reworded, no
  section renumbered): `docs/architecture.md` (§3, new §5.4, §10, §13,
  §14, §16), `docs/workflow.md` (§1 diagram, new Phase 11 under existing
  §2), `docs/architecture-evolution.md` (this document — §7, §11, §28,
  §29, this addendum), `.github/copilot-instructions.md` (Roles section),
  `.github/CODEOWNERS` (one line), `validation/bring-up-procedure.md` (new
  firmware-specific sub-section), `datasheets/evidence-log.md` (new
  `DS-MCU-055` through `DS-MCU-063` and `DS-IMU-078` through `DS-IMU-088`
  rows — additive only, no existing row edited), the existing
  `stmicroelectronics_stm32g031k8t6_rev-unknown.md` and
  `bosch-sensortec_bmi270_rev1.6.md` metadata records ("Used for Evidence
  IDs" field extended, nothing removed), and the repository root
  `README.md` (agent roster + directory layout brought current — this also
  folded in the previously-missing Mechanical Lead/Reviewer entries, a
  pre-existing gap from the Phase 1 PR, rather than compounding it by
  adding Firmware alongside a roster that still said "four agents").
- **Confirmed untouched** (verified via `git diff` before opening the PR):
  all 6 existing `.github/agents/*.agent.md` files, all 7 existing
  `SKILL.md` files, `.github/instructions/{hardware-design,datasheets,
  mechanical-design,validation}.instructions.md`,
  `.github/workflows/{hardware-gate.yml,agent-frontmatter-lint.yml}`,
  `tools/{check_open_issues.py,check_agent_frontmatter.py}`,
  `datasheets/{README.md,evidence-log.md}`'s existing rows,
  `requirements/**`, `bom/component-selection.md`,
  `hardware/**` (including `hardware/schematic/bench-imu-01-design.md`
  itself — the Firmware Engineer role's own "Out of scope" explicitly
  forbids editing Electronics artifacts), `validation/{fmea.md,
  change-log.md,change-impact-matrix.md,open-issues.md,design-review.md}`,
  `docs/evaluation.md`.
- **Aside, out of this PR's scope, flagged for whoever owns it next**:
  this session found `openscad` (`2021.01`) genuinely installed on this
  machine, which contradicts `docs/architecture.md` §5.3/§13's recorded "no
  CAD/3D modeling tool... verified" finding from the Phase 1 PR. This is
  consistent with `requirements/traceability-matrix.md`'s own REQ-302/
  REQ-305 rows, which already reference a real OpenSCAD compile having
  happened in a *later* Mechanical session than the one §31 describes — so
  this is a stale §5.3/§13 fact from an earlier point in this repository's
  history, not a new discovery this PR is responsible for reconciling. Not
  fixed here (out of scope for the Firmware-only kickoff this PR
  implements; §5.3/§13 are Mechanical-owned facts, not Firmware-owned
  ones) — left for a future Mechanical-scoped session to verify and
  correct.
- **Status**: implemented, PR opened, awaiting independent audit before
  merge — same process every prior PR in this repository's history went
  through.

## 33. Phase 3 Implementation Status (Addendum — Power Engineer)

Added when Phase 3 (Power) was actually implemented, in a separate PR from
this document's original merge and the Phase 1 (§31) / Phase 2 (§32)
addenda — kept as its own addendum for the same reason those are: preserve
the audit trail of what was true before this phase vs. after.

- **Trigger met**: `docs/architecture.md` §14's Power Engineer trigger
  ("when subsystem count / power complexity exceeds what Circuit Engineer
  can track ad hoc") was judged met by the Bench-IMU-01 Rev 3 kickoff
  (Motor Driver + Reaction Wheel subsystem) — the exact stage that trigger
  already named as its own example. This is a Hardware Lead judgment call,
  reasoned explicitly rather than defaulted into: Rev 2's power design was
  one simple rail (3.3V logic, ~16mA worst-case) that Circuit Engineer
  tracked ad hoc correctly and proportionately; Rev 3 adds a second,
  higher-current, likely-different-voltage rail, a genuine system power-
  architecture choice (the physical source for that rail) that is itself a
  Human-in-the-loop architecture decision, and motor-specific power concerns
  (stall/inrush current, possible rail enable/sequencing, brownout coupling
  between rails) that are qualitatively new, not just "one more line in a
  table."
- **Human approval**: given, scoped explicitly to standing up the Power
  Engineer discipline itself — **as its own standalone PR, implemented and
  merged before any Rev 3 hardware/mechanical/firmware design work that
  depends on it** (the human's own explicit sequencing instruction, mirroring
  how Mechanical Lead/Reviewer were created and merged before ever being
  exercised on a real design, and how Firmware Engineer was its own scoped
  PR). Control Engineer, Firmware Reviewer, PCB Engineer, Test Engineer,
  Datasheet Specialist, and Safety/Compliance Reviewer all remain exactly as
  `docs/architecture.md` §14 documents them (deferred, untouched triggers),
  per the kickoff scope for this PR.
- **Explicit human decision (asked via the Hardware Lead's own plan, not
  silently assumed)**: Power Engineer is an Electronics-adjacent addition
  (extends the original 4-agent Electronics team to 5 — Component Engineer/
  Circuit Engineer/Hardware Reviewer/Power Engineer all divide Electronics
  work under Hardware Lead — rather than a new top-level discipline the way
  Mechanical/Firmware are), and is **engaged only when the Hardware Lead
  judges a given project's power complexity warrants it**, not automatically
  for every future design — the same scope-proportionality reasoning §32
  already used to decide against introducing a Firmware Reviewer
  immediately. No independent "Power Reviewer" is introduced either: Power
  Engineer's own architecture proposal already routes through the human
  Chief Engineer as a mandatory HITL architecture-decision gate
  (`docs/architecture.md` §10) before Circuit Engineer ever implements it —
  a different, already-adversarial check (a human decision, not a self-
  approval) exists at exactly the point where Circuit Engineer/Mechanical
  Lead's own designs instead rely on an independent AI reviewer pass. This is
  recorded as the considered reason, not an oversight, mirroring how §32
  recorded its own reasoning for not adding a Firmware Reviewer.
- **Verified, not assumed, during implementation** (mirroring §31/§32's own
  "verified, not assumed" bullets, for the same reasons): the GitHub custom
  agent (`.github/agents/*.agent.md`, required `description`) and agent
  skill (`.github/skills/<name>/SKILL.md`, required `name`+`description`)
  specs were re-fetched directly from current GitHub documentation this
  session — both unchanged since PR #2/#3/§31/§32, no fifth "fix the spec"
  round was needed. The `tools` frontmatter property, `metadata` property,
  and the `agent`/`custom-agent` tool alias documented in the current spec
  were also newly reviewed this session (not previously exercised in this
  repository) — none required a change to this repository's existing
  agent-file convention (plain `name`+`description`+free-form extra fields
  such as `role`/`reports_to`/`handoff_from`/`handoff_to`/`skill`, which the
  spec neither requires nor forbids, and which `tools/
  check_agent_frontmatter.py` does not check beyond `description`).
- **A real, non-obvious reason for keeping `hardware/power-architecture.md`
  and `hardware/power-budget.md` as two separate files**: the architecture
  (which rails exist, sourced from where, decided once) and the numeric
  rollup (every subsystem's load, updated every time one is added) change on
  genuinely different cadences — collapsing them into one file would mean
  either re-litigating the architecture decision's own record every time a
  subsystem's current draw is merely re-tallied, or losing the standalone,
  audit-friendly decision record `validation/change-log.md` (ECO) entries
  already point back to for other domains. This mirrors the existing
  `requirements/requirements.md` vs. `requirements/traceability-matrix.md`
  split (a stable statement of intent vs. a living per-row status table) —
  a pattern this repository already established, not a new one invented for
  Power specifically.
- **Files added**: `.github/agents/power-engineer.agent.md`,
  `.github/skills/power-architecture/SKILL.md`,
  `hardware/power-architecture.md` (template only — no real project has
  populated it yet, mirroring exactly how `hardware/mechanical-interface.md`
  was templated in Phase 1 before Bench-IMU-01 existed, §13/§27 item 5).
- **Files edited, additively only** (nothing existing removed/reworded, no
  section renumbered): `docs/architecture.md` (§2 diagram, §3 agents table +
  role-spec list + new paragraph, §12, new Power Engineer row in §14, §16
  directory map), `docs/workflow.md` (§1 diagram, Phase 4's entry/activities
  notes, new Phase 12 section, §4 handoff-chain paragraph, §5 agent list),
  `docs/architecture-evolution.md` (this addendum), `.github/
  copilot-instructions.md` (Roles section: agent count "Seven"→"Eight", new
  Power heading + item 8), `.github/CODEOWNERS` (one new line, for the new
  architecture-decision-bearing file specifically), `README.md` (agent
  roster table + repository layout note), `docs/commands/make-circuit.md`
  (the pre-existing "Adding a new subsystem" variant note, extended to
  mention Power Engineer as an option), `hardware/power-budget.md` (its
  generic header paragraph only — the "future Power Engineer" framing
  updated to reflect implementation; the file's own Bench-IMU-01-specific
  content below that paragraph is untouched, since this PR is deliberately
  scoped to the framework addition only, not to Rev 3's actual numbers).
  **No new `.instructions.md` file was created** — `hardware/
  power-architecture.md` falls under `hardware/**`, already governed by
  `.github/instructions/hardware-design.instructions.md`'s existing Evidence-
  citation/Source-of-Truth/ECO rules, which are not a genuinely different
  rule set the way Mechanical's CONFIRMED/ASSUMPTION/ESTIMATE/UNKNOWN
  labeling and CAD-tool-honesty rules were — reusing an existing instructions
  file where the rules are already identical avoids instructions-file
  proliferation ahead of actual need, the same restraint §9 already applies
  to Component/Circuit Engineer's own Agent-vs-Skill status.
- **Confirmed untouched** (verified via `git diff` before opening the PR):
  all 7 existing `.github/agents/*.agent.md` files, all 8 existing
  `SKILL.md` files, all 5 existing `.github/instructions/*.instructions.md`
  files, `.github/workflows/{hardware-gate.yml,agent-frontmatter-lint.yml}`,
  `tools/{check_open_issues.py,check_agent_frontmatter.py}`,
  `datasheets/{README.md,evidence-log.md}` (no new Evidence category was
  needed — Power Engineer reuses the existing `PWR` category
  `docs/architecture.md` §6.3 already lists), `requirements/**`,
  `bom/component-selection.md`, every file under `hardware/schematic/`,
  `hardware/pcb/`, and `hardware/mechanical/` (Power Engineer's own "Out of
  scope" explicitly forbids editing another discipline's artifacts, the same
  restraint every other agent's profile already states), `firmware/**`,
  `validation/{fmea.md,change-log.md,change-impact-matrix.md,open-issues.md,
  design-review.md,bring-up-procedure.md}`, `docs/evaluation.md`, and
  `hardware/power-budget.md`'s own Bench-IMU-01-specific content (see above
  — only its generic header paragraph changed).
- **Status**: implemented, PR opened as its own standalone change (not
  bundled with Rev 3 hardware/mechanical/firmware work, per explicit human
  instruction), awaiting independent audit before merge — same process
  every prior PR in this repository's history went through.

## 34. KiCad Tooling Verification Status (Addendum)

Added when a real KiCad project was first created in this repository, in a
separate PR from this document's original merge and the Phase 1/2/3 (§31/
§32/§33) addenda — kept as its own addendum for the same reason those are:
preserve the audit trail of what was true before vs. after. Unlike §31-§33,
this is not a new discipline/agent-role addition — it is a **capability
verification and correction**: `docs/architecture.md` §5.2/§13 had, since
this project's inception, described KiCad MCP tooling and ERC in
conditional/hypothetical terms ("available only when a KiCad MCP server is
connected," "ERC has no dedicated tool in this toolset yet"). This addendum
records that those tools are now verified genuinely connected and actively
used, not hypothetical — with real, sometimes surprising findings from
actually exercising them for the first time.

- **Trigger met**: every prior design cycle (Bench-IMU-01 Rev 2, and the
  in-progress, separate Rev 3 motor-driver session) had produced schematics
  as structured Markdown documents, explicitly disclosing "no KiCad project
  exists yet." The human confirmed KiCad 10.0.1 + `kicad-cli` genuinely
  installed on this machine; this session independently re-verified that
  before treating KiCad as available, per this repository's own established
  discipline (`kicad-list_projects` returned `[]` — tool works, no project
  existed yet).
- **Human approval**: given, scoped explicitly to Rev 2 only (the stable,
  already-merged, already-Design-Complete baseline) — the parallel,
  in-progress Rev 3 motor-driver session's branch/files were explicitly
  out of scope and not touched.
- **Verified, not assumed, during implementation** (mirroring §31/§32/§33's
  own "verified, not assumed" bullets, for the same reasons):
  (a) every `kicad-*` MCP tool's actual behavior was tested directly against
  a real project, not assumed from its description — see the significant
  finding below;
  (b) `kicad-cli sch erc` was independently tested twice (once by the
  Hardware Lead, once again by a separate Hardware Reviewer fidelity-review
  pass) and confirmed to produce real, meaningful ERC output, correcting
  `docs/architecture.md` §5.2/§13's prior "not available" claim;
  (c) `libngspice.dylib` was found genuinely bundled with the local KiCad
  install, but `kicad-cli` has no `sim` subcommand — no scriptable
  simulation path exists; recorded precisely (bundled engine, not
  automatable) rather than either overclaiming a new capability or
  repeating the old blanket "not available" framing, per explicit guidance
  from the creator/orchestrating session.
- **Significant finding, not merely a footnote**: of the 16 `kicad-*` MCP
  tools, only 5 (`list_projects`, `get_project_structure`,
  `validate_project`, `get_drc_history_tool`, `open_project`) actually work
  in this environment. **This 5/16 split is a robust, reproducible fact**,
  independently confirmed across three separate verification passes (the
  Hardware Lead, a delegated Hardware Reviewer, and an independent PR
  auditor — three different sessions/MCP clients, identical count each
  time). **The exact client-visible error text for the other 11 is
  MCP-client-dependent, and was initially over-specified as a single
  universal fact — corrected here after the PR auditor's own independent
  pass surfaced the discrepancy**: with `ctx` omitted entirely, all 11 fail
  identically with `Input validation error: 'ctx' is a required property`
  (a client-side schema rejection — this is the *only* behavior the
  auditor's client ever produced). With a placeholder `ctx` value
  explicitly supplied, the schema check passes and each tool's real body
  executes — at which point most fail with `Context is not available
  outside of a request` (confirmed by reading the local `kicad-mcp`
  server's own source, `kicad_mcp/tools/netlist_tools.py` and siblings:
  these call `ctx.report_progress(...)`, needing a live FastMCP request
  context this environment's bridge does not supply), while `run_drc_check`
  instead correctly executes (`{"success":false,"error":"PCB file not
  found in project"}` — a correct result, not a bug) and
  `generate_project_thumbnail` fails with yet another, unrelated error
  (`'FunctionTool' object is not callable`) — all independently
  reproduced twice by the Hardware Lead. Neither observation is wrong; they
  reflect different calling patterns. The lesson generalizes beyond this
  one finding: **when reporting a tool-availability fact, distinguish what
  is robust (the count, reproduced across independent passes) from what
  may be calling-environment-specific (exact error text) — precision on
  the wrong detail is itself a form of overclaiming.** Worked around by
  using `kicad-cli` directly for the equivalent verification
  (`sch export netlist`, `sch export bom`, `sch erc`), which does not
  depend on this client-specific nuance at all — see
  `hardware/schematic/bench-imu-01/README.md` for the full account.
- **A real, non-obvious discovery this verification itself produced**:
  building the real KiCad project (checking real symbol/footprint
  availability before wiring anything) independently surfaced ISS-014 — the
  STM32G031K8T6's real LQFP-32 package has no PB10/PB11 pins at all, so the
  already-Design-Complete Rev 2 baseline's IMU I2C2 bus could not be
  physically wired as documented. This is exactly the kind of defect a
  Markdown-only review process cannot catch (it requires cross-checking a
  MCU's real physical package pinout table, a different table from the
  alternate-function table every prior review pass correctly checked
  instead) — a concrete demonstration of why this capability verification
  was worth doing, not just a formality. Full finding: `validation/
  open-issues.md` ISS-014 (CRITICAL, RESOLVED after a fidelity-scoped
  Hardware Reviewer Cycle 3 pass), `validation/change-log.md` ECO-006.
- **Files added**: `hardware/schematic/bench-imu-01/` (`bench-imu-01.
  kicad_pro`, `.kicad_sch`, `.kicad_sym`, `sym-lib-table`,
  `generate_schematic.py`, `README.md`); `datasheets/
  stmicroelectronics_stm32_open_pin_data_stm32g031k4-6-8tx.md`.
- **Files edited, additively only** (nothing existing removed/reworded, no
  section renumbered): `docs/architecture.md` (§5.2, §13, §16 directory
  map), `docs/architecture-evolution.md` (this addendum),
  `hardware/schematic/bench-imu-01-design.md` (Rev 2, corrected — new
  changelog entry, §0, §2.3, §4.1, §4.3, §5.2, §5.3, §6, §11, §12, §13,
  §14, §16, new §19 — see that document's own changelog for the full,
  itemized account), `datasheets/evidence-log.md` (new DS-MCU-064 through
  DS-MCU-067 rows), `validation/open-issues.md` (new ISS-014 row, plus a
  Hardware Reviewer Cycle 3 append to its Notes), `validation/
  design-review.md` (new Cycle 3 fidelity-review entry), `validation/
  change-log.md` (new ECO-006 row), `validation/fmea.md` (new FMEA-008
  systemic-lesson entry).
- **Confirmed untouched**: the parallel, in-progress Rev 3 motor-driver
  session's own branch/files were never read for authoritative content nor
  written to; no PCB layout was attempted (`hardware/schematic/bench-imu-01/`
  has no `.kicad_pcb` — `kicad-validate_project`'s own "Missing PCB layout
  file" finding on this project is expected and correct, not a gap); no ERC
  *MCP tool* is claimed to exist (only the raw `kicad-cli sch erc`
  capability); no SPICE automation is claimed; `requirements/
  traceability-matrix.md` was not edited (its REQ-104 row still cites the
  pre-correction PB10/PB11 fact — flagged as follow-up work, not performed
  here, to avoid a second, unrelated collision risk with the parallel Rev 3
  session's own likely edits to that same file).
- **Status**: implemented, PR opened, awaiting independent audit before
  merge — same process every prior PR in this repository's history went
  through.

