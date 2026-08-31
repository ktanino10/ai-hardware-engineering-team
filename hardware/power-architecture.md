# System Power Architecture

The system-level power-tree / rail-topology proposal and decision record —
which physical rails exist, at what nominal voltage, sourced from where, and
why — owned by the **Power Engineer** (Phase 3 of the multidisciplinary
evolution, `docs/architecture-evolution.md` §33) once a project's power
complexity exceeds what the Circuit Engineer tracks ad hoc directly in
`hardware/power-budget.md` alone (`docs/architecture.md` §12/§14).

**Status: template only** — no real project has populated this file yet.
This mirrors exactly how `hardware/mechanical-interface.md` was introduced in
Phase 1 before any real project ran through the Mechanical discipline
(`docs/architecture-evolution.md` §13/§27 item 5): the structure/convention
is defined now; the actual rows are filled in the first time a project
engages the Power Engineer.

## Relationship to `hardware/power-budget.md`

These are two different artifacts, kept separate on purpose:

- **This file** is the *architecture* record — the options considered, their
  trade-offs, and the human Chief Engineer's decision on rail topology and
  physical source(s). It changes rarely: only when the rail topology itself
  changes (e.g. a new subsystem forces a new physical input), not every time
  a subsystem's current draw is merely re-tallied.
- **`hardware/power-budget.md`** is the *numeric rollup* — every subsystem's
  current/power draw against each rail's supply capability, with margin. It
  is updated every time a subsystem is added, per its own existing header
  note, regardless of whether the architecture itself changed.

## Who fills this in

Per `.github/agents/power-engineer.agent.md`, the **Power Engineer** is
responsible for populating this file, once engaged (see that file's "When
this role is engaged" — a Hardware Lead judgment call per project/revision,
not automatic for every design). Until Power Engineer is engaged for a given
project, `hardware/power-budget.md` alone remains sufficient and this file
stays a template, per `docs/architecture.md` §12's original framing
("Circuit Engineer maintains `hardware/power-budget.md`... until [system
complexity grows past the benchmark]").

## Architecture Options (template)

Fill in one row per real, named option considered — **never fewer than 2**
when a new rail/physical input is genuinely required (`.github/skills/
power-architecture/SKILL.md`). If an existing rail already has adequate
headroom for the new subsystem, state that directly instead of inventing
options nobody would pick.

| Option | Description | Real current/voltage basis (Evidence ID) | Pros | Cons | Recommended? |
|---|---|---|---|---|---|
| `<Option A>` | | | | | |
| `<Option B>` | | | | | |

## Rail Sequencing / Coupling Notes (template)

Document any rail-enable ordering, inrush-handling, or brownout-coupling
concern between rails here — leave explicitly `N/A` if genuinely none apply
(e.g. fully independent, separately-sourced rails with no shared return-path
concern), rather than an empty silence that reads as "not considered."

## Decision

| Role | Name | Date | Decision |
|---|---|---|---|
| Power Engineer | | | Proposed — `<option>` |
| Hardware Lead | | | |
| Chief Engineer (Human) — required, this is an architecture decision (`docs/architecture.md` §10) | | | |

## Handoff & change control

- **Produced by**: Power Engineer, once engaged (see "Who fills this in").
- **Consumed by**: Circuit Engineer (implements the approved architecture
  into the actual schematic), Component Engineer (sources any new part the
  approved architecture requires, e.g. a converter IC for a new rail).
- If the approved architecture changes after Circuit Design has started
  (e.g. a later subsystem addition exceeds the approved headroom), log it in
  `validation/change-log.md` (ECO) and check `validation/
  change-impact-matrix.md`'s Power row before human re-approval — same rule
  as any other non-cosmetic `hardware/**` change
  (`.github/instructions/hardware-design.instructions.md`).
- Governed by `.github/instructions/hardware-design.instructions.md`
  (`hardware/**` scope already covers this file — no separate instructions
  file was created for Power Engineer specifically, since its evidence/ECO
  rules are identical to the rest of `hardware/**`, not a genuinely
  different rule set the way Mechanical's CONFIRMED/ASSUMPTION/ESTIMATE/
  UNKNOWN labeling and CAD-tool-honesty rules were).
