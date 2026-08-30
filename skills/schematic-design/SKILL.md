# Skill: Schematic Design

## Purpose

Standard procedure for going from Component-Engineer-approved parts +
datasheet-extracted constraints (+ manufacturer reference designs) to a
defensible schematic, with every decision's "why" recorded.

## Preconditions

- Parts are approved (`bom/component-selection.md`).
- `skills/datasheet-analysis/SKILL.md` has been run for each part in use;
  relevant parameters have Evidence IDs (or are explicitly `UNKNOWN`, in
  which case escalate before relying on them).

## Procedure

1. **Fix shared resources first, serially**: power rails, ground scheme,
   pin allocation. This must happen before any sub-block design starts, or
   parallel sub-blocks can silently conflict (`docs/architecture.md` §4).
2. **Design each sub-block** (e.g. power supply, MCU periphery, sensor
   interface) against the full mandatory checklist — see
   `agents/circuit-engineer.agent.md` for the exact list (supply/logic
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
   (`skills/hardware-review/SKILL.md`) before handing off — the goal is to
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
