---
name: schematic-design
description: Standard procedure for designing a schematic from Component-Engineer-approved parts, datasheet-extracted constraints, and manufacturer reference designs, with rationale recorded for each design decision. Use this whenever designing or revising a circuit schematic.
---

# Skill: Schematic Design

## Purpose

Standard procedure for going from Component-Engineer-approved parts +
datasheet-extracted constraints (+ manufacturer reference designs) to a
defensible schematic, with every decision's "why" recorded.

## Preconditions

- Parts are approved (`bom/component-selection.md`).
- `.github/skills/datasheet-analysis/SKILL.md` has been run for each part in use;
  relevant parameters have Evidence IDs (or are explicitly `UNKNOWN`, in
  which case escalate before relying on them).

## Procedure

1. **Fix shared resources first, serially**: power rails, ground scheme,
   pin allocation. This must happen before any sub-block design starts, or
   parallel sub-blocks can silently conflict (`docs/architecture.md` §4).
2. **Design each sub-block** (e.g. power supply, MCU periphery, sensor
   interface) against the full mandatory checklist — see
   `.github/agents/circuit-engineer.agent.md` for the exact list (supply/logic
   voltage, Absolute Max Ratings, Recommended Operating Conditions,
   current, thermal, decoupling, pull-up/down, protection, power
   sequencing, reset, interface timing, MCU pin function, interface
   protocol timing, grounding, noise, recommended application circuit,
   mechanical/thermal co-design). Sub-blocks are parallel-safe once step 1
   is fixed.
3. **Record the "why" for every decision**, tied to an Evidence ID — e.g.
   "100 nF decoupling cap placed within 5 mm of VDD pin per [DS-MCU-004],
   §7.2 Recommended Application Circuit" not just "added decoupling cap".
4. **Update `hardware/power-budget.md`** with this design's current/power
   draw per rail.
5. **Integrate sub-blocks serially.** Re-check cross-block interactions:
   shared rail loading (does the combined draw still fit the supply's
   budget?), ground return paths, any timing dependency across blocks.
6. **Self-check against the Hardware Reviewer's checklist**
   (`.github/skills/hardware-review/SKILL.md`) before handing off — the goal is to
   catch the obvious issues yourself so independent review finds the
   subtler ones, not to skip review.
7. **Where a KiCad project exists**, self-check with
   `extract_schematic_netlist` / `analyze_schematic_connections` /
   `validate_project` (`docs/architecture.md` §5.2) to confirm the actual
   netlist matches your stated design intent.
8. **Hand off** to the Hardware Reviewer: schematic artifact + design
   rationale log + self-check results + `hardware/power-budget.md` update +
   any open `UNKNOWN`s.

## Handling Hardware Reviewer findings (loop-back)

Address every CRITICAL/HIGH finding explicitly: fix and record the fix
(with the new Evidence ID if applicable), or state why you believe it
doesn't apply (with evidence) and let the Hardware Lead mediate rather than
unilaterally dismissing it. Log the change in `validation/change-log.md`
(ECO) if the design actually changes.


## Foundational Change Cascade Checklist (revising an existing schematic, not first-pass design)

The ordinary procedure above makes the current schematic internally
well-reasoned, but `docs/workflow.md` §4.2/§4.2.1 shows that internal
consistency is not enough once upstream facts move. Electronics already has
its own dated examples: `ISS-024` (a stale U6 thermal-rise figure surviving in
a changelog summary after the corrected value existed elsewhere), `MISS-021`
(stale motor-energy/RPM numbers propagating into downstream artifacts), and
`MISS-029` (a stale load-bearing figure lingering in
`bom/component-selection.md`). **Whenever you are changing an existing
schematic because a foundational upstream fact changed** (approved part swap,
new datasheet revision, corrected Evidence ID meaning, pin reassignment, rail
envelope change, package/footprint correction), do not treat "the schematic
now reflects the new fact" as sufficient. Additionally:

1. **Re-read the live upstream authority this pass depends on.** For a
   component-driven change, confirm the current `bom/component-selection.md` +
   `datasheets/evidence-log.md` entries still match the live datasheet/manufacturer
   source; for a layout/netlist-driven change, re-extract from the current
   KiCad project or netlist tool output rather than trusting a previously-made
   snapshot note. Mirrors `docs/workflow.md` §4.2.1's "re-derive from the live
   upstream file, not the snapshot" rule in schematic form.
2. **Trace every place the changed fact is cited, not only the symbol/net you
   edited.** If you change a rail limit, current draw, thermal figure, timing
   constraint, pin assignment, or application-circuit recommendation, check
   the design rationale log, `hardware/power-budget.md`,
   `requirements/traceability-matrix.md`, `validation/open-issues.md`, and any
   top-of-file/changelog summary prose for stale restatements. `ISS-024` is the
   warning that a one-line summary can stay wrong while the detailed analysis
   is right.
3. **Treat pin/net changes as downstream-interface changes, not purely local
   edits.** A corrected MCU pin assignment, reset net, fault line, or power-
   enable signal requires re-checking any dependent firmware assumptions, PCB
   layout handoff, connector tables, and reviewer notes that cite the old
   assignment. A schematic can be internally correct and still strand a stale
   downstream consumer.
4. **Reconcile every derived calculation that used the old fact.** If the
   change touches current, voltage, thermal dissipation, timing, or source
   envelope, re-compute dependent tables/ranges rather than carrying forward
   previous numbers with only local text edits. Update
   `hardware/power-budget.md` as part of the same pass, not as a future
   courtesy task.
5. **Check whether any prior finding disposition or requirement verification
   was made against the superseded value.** If a `RESOLVED`, `PENDING`, or
   `ACCEPTED-RISK` note was justified using the old number/configuration, flag
   it for fresh reviewer attention instead of assuming the old disposition
   still covers the revised schematic.
6. **State bounded non-updates explicitly.** If a nearby figure or sub-block is
   unaffected, say why (e.g. independent formula/input, unchanged source)
   rather than leaving reviewers to guess whether it was checked. The goal is
   to prevent §4.2's stale-citation class from hiding in the untouched prose
   around an otherwise-correct schematic edit.

## Output

Schematic artifact (and/or KiCad project) + design rationale log +
self-check results + `hardware/power-budget.md` update.

## Common failure modes to avoid

- Designing sub-blocks in parallel before shared rails/ground/pins are
  fixed.
- Copying a reference design without checking it actually matches your
  supply voltage / logic levels / operating conditions.
- Treating your own self-check as a substitute for independent review.
- Leaving a decoupling/pull-up/protection choice with no cited rationale.
