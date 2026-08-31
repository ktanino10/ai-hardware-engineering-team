---
name: power-architecture
description: Standard procedure for defining a system-level, multi-rail power architecture (topology, physical source, sequencing) across subsystems once complexity exceeds ad hoc tracking, aggregating real per-subsystem current/voltage/thermal data into named architecture options for human decision. Use this whenever a new subsystem's power needs may not fit an existing rail, or when subsystem count/power complexity is judged to exceed what Circuit Engineer can track ad hoc in hardware/power-budget.md alone.
---

# Skill: Power Architecture

## Purpose

Turn "we're adding a subsystem with real power needs" into a decided,
evidence-grounded power tree: how many rails, at what voltage, sourced from
where, with what margin — before the Circuit Engineer starts implementing a
specific regulator/converter circuit. This runs **after** Component Selection
has produced real current/voltage/thermal numbers for the new subsystem's
candidate parts, and **before** Circuit Design begins on the power section
(`docs/workflow.md`).

## When to use

Whenever the Hardware Lead judges a project's power complexity has grown
past what Circuit Engineer tracked ad hoc in `hardware/power-budget.md`
alone (`docs/architecture.md` §14's own example: "at Motor Driver / Reaction
Wheel stage"). Not needed for a simple single-rail design — that stays
Circuit Engineer's direct responsibility, exactly as before this skill
existed.

## Inputs

- Component Engineer's real current/voltage/thermal figures for the new
  subsystem's candidate parts (`bom/component-selection.md`), each already
  Evidence-ID-cited.
- The existing `hardware/power-budget.md` (current rail(s), supply
  capability, existing subsystem loads, existing margin).
- Any human-stated hard constraint on the power source (e.g. "must stay
  single-cable powered," or "a second connector/battery is fine") — do not
  assume one exists if it hasn't been stated; ask rather than guess.

## Procedure

1. **Aggregate what already exists.** Tabulate every existing subsystem's
   load against the existing rail(s)' supply capability — reuse
   `hardware/power-budget.md`'s own prior numbers, don't re-derive them.
2. **Add the new subsystem's real worst-case draw** (from Component
   Selection, per candidate still in contention) and check: does real
   headroom exist on an existing rail, or is a new rail/new physical input
   structurally required? Show the arithmetic (worst-case sum vs. rated
   capability vs. any governing requirement ceiling), not just a verdict.
3. **If an existing rail suffices**, say so plainly with the numbers —
   introducing a new rail when none is needed is its own kind of
   over-engineering.
4. **If a new rail/input is required, generate ≥2 real, named architecture
   options** — not a single default. Typical axes to consider (use only the
   ones that actually apply; don't invent options nobody would pick):
   - Keep the existing source logic-only and add a second, independent
     physical input (e.g. DC barrel jack, a second connector) dedicated to
     the new subsystem.
   - Negotiate a higher-power mode from the existing source if the
     interface supports it (e.g. USB Power Delivery), if within realistic
     reach of the actual current/voltage the new subsystem needs.
   - Introduce a battery, if consistent with the project's stated use case.
   For each option, state real trade-offs: cost/BOM impact, added
   connector(s), protection/regulation implications, and anything the
   option would take away from an already-approved requirement (e.g. "no
   longer purely USB-powered").
5. **Check rail-sequencing/coupling concerns**, when relevant: could a
   fault or inrush transient on the new rail brown out an existing rail if
   they share a source or return path? Does the new rail need independent
   enable logic?
6. **Present the options to the human Chief Engineer** for the architecture
   decision (`docs/architecture.md` §10) — do not self-select an option.
   Record the options and the decision in `hardware/power-architecture.md`.
7. **Update `hardware/power-budget.md`** for the approved architecture:
   full multi-rail load table, supply capability per rail, margin summary,
   same format this project already uses.
8. **Flag any new part-sourcing need** (e.g. a converter IC for the new
   rail) back to the Component Engineer via the Hardware Lead — this skill
   defines what the rail must deliver; the actual part comparison is
   Component Selection's job.
9. **Hand off to Circuit Engineer** with the approved architecture and the
   updated power budget for implementation into the real schematic.

## Output

`hardware/power-architecture.md` (options considered + recorded human
decision) + `hardware/power-budget.md` (updated multi-rail numeric rollup)
+ any flagged follow-on Component Selection need, handed to the Hardware
Lead/Circuit Engineer.

## Common failure modes to avoid

- Picking an architecture option yourself and presenting it to the human as
  a fait accompli instead of a decision — this is always a HITL architecture
  gate (`docs/architecture.md` §10), not a recommendation you can finalize.
- Re-deriving or guessing a subsystem's current/voltage draw instead of
  reusing Component Selection's already-Evidence-ID-cited numbers.
- Silently assuming an existing human-fixed constraint (e.g. "USB-powered
  only") extends to a brand-new subsystem without checking — a constraint
  scoped to the original design may or may not have been intended to bind a
  later addition; ask rather than assume either way.
- Treating this as a one-time step for a whole project — re-run it whenever
  a subsequent subsystem addition could plausibly exceed the
  already-approved architecture's headroom.
