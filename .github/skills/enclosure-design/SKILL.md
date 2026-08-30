---
name: enclosure-design
description: Standard procedure for designing a physically buildable enclosure/mechanical structure from the Electronics->Mechanical Interface contract, covering PCB mounting, connector accessibility, component-height clearance, internal clearance, fastener placement, wall thickness, assembly order, and basic 3D-printability, producing text/parametric output when no CAD tool is connected. Use this whenever designing or revising a mechanical enclosure.
---

# Skill: Enclosure Design

## Purpose

Standard procedure for going from a populated `hardware/mechanical-interface.md`
to a defensible, physically buildable enclosure design, with every dimension's
"why" recorded — the standard operating procedure behind
`.github/agents/mechanical-lead.agent.md`. Scoped to the Phase 1 subset only
(`docs/architecture-evolution.md` §10/§13): spatial layout, PCB mounting,
connector accessibility, component-height clearance, internal clearance,
fastener placement, wall thickness, assembly order, basic print-fit
tolerance, and basic manufacturability/3D-printability.

## Preconditions

- `hardware/mechanical-interface.md` is populated (or you populate it
  yourself as the first step — see `.github/agents/mechanical-lead.agent.md`,
  "Populating hardware/mechanical-interface.md") with at least: board
  outline, mounting hole positions, max component height (top+bottom), and
  connector locations. Any field you cannot confirm is `UNKNOWN`/
  `ASSUMPTION`/`ESTIMATE`, never a silent guess
  (`.github/instructions/mechanical-design.instructions.md`).
- No CAD/3D modeling MCP tool is connected in this environment (verified —
  see `docs/architecture.md` §5.3/§13) — plan to produce text/parametric
  output, not a rendered model.

## Procedure

1. **Confirm the interface data.** Read `hardware/mechanical-interface.md` in
   full. If a needed field is `UNKNOWN`, stop and escalate
   (`docs/architecture.md` §10) rather than substitute a guessed number.
2. **Fix the enclosure's overall envelope first, serially**: outer
   dimensions, wall split (lid/base), wall thickness. This is the mechanical
   equivalent of fixing shared rails/ground/pins before sub-block design in
   `.github/skills/schematic-design/SKILL.md` — later checklist items depend
   on this being stable.
3. **Design against the full mandatory checklist** — see
   `.github/agents/mechanical-lead.agent.md` for the exact list (enclosure/
   spatial layout, PCB mounting, connector accessibility, component-height
   clearance top+bottom, internal clearance/interference, fastener placement,
   wall thickness, assembly order, basic print-fit tolerance, basic
   manufacturability/3D-printability).
4. **State a single, explicit print-fit clearance allowance** (e.g. "+0.2 mm
   per side") and apply it consistently everywhere two parts mate. This is
   the *basic* Phase 1 answer to tolerance — do not attempt a full tolerance
   stack-up analysis (deferred, `docs/architecture-evolution.md` §10/§13).
5. **State a single, explicit manufacturability rule set** you're designing
   against (minimum wall thickness, maximum unsupported overhang angle,
   maximum unsupported bridge span, assumed print material) as an
   `ASSUMPTION` if the human hasn't specified a printer/material — do not
   silently assume one without saying so.
6. **Record the "why" for every dimension**, tied to a
   `hardware/mechanical-interface.md` row, an Evidence ID (for any mechanical
   part's manufacturer spec, e.g. a heat-set insert — reuse
   `.github/skills/datasheet-analysis/SKILL.md` and the `DS-<CATEGORY>-<NNN>`
   scheme), or an explicit `ASSUMPTION`/`ESTIMATE`.
7. **Produce the parametric artifact**: an OpenSCAD-syntax `.scad` file under
   `hardware/mechanical/`, every dimension as a named variable — plus a
   structured `Parameter | Value | Unit | Source/Rationale` Markdown table as
   the always-readable fallback. Do not claim it has been rendered/previewed
   unless a verified-connected tool actually did so.
8. **Self-check against the Mechanical Reviewer's checklist**
   (`.github/skills/mechanical-review/SKILL.md`) before handing off — the
   goal is to catch the obvious issues yourself so independent review finds
   the subtler ones, not to skip review.
9. **Hand off** to the Mechanical Reviewer: `.scad` file + dimensional-spec
   table + design rationale log + self-check results + any open `UNKNOWN`s.

## Handling Mechanical Reviewer findings (loop-back)

Address every CRITICAL/HIGH finding explicitly: fix and record the fix (with
an updated Evidence ID/interface reference if applicable), or state why you
believe it doesn't apply (with evidence) and let the Hardware Lead mediate
rather than unilaterally dismissing it. Log the change in
`validation/change-log.md` (ECO) if the design actually changes, and check
`validation/change-impact-matrix.md`'s existing "Mechanical" impact row if
the fix could ripple back into Electronics.

## Output

`.scad` file + dimensional-spec table (both under `hardware/mechanical/`) +
design rationale log + self-check results, referencing
`hardware/mechanical-interface.md`.

## Common failure modes to avoid

- Designing fastener bosses/cutouts before the overall envelope (outer
  dimensions, wall thickness) is fixed — later changes can silently
  invalidate earlier placements.
- Stating a print-fit clearance allowance once and then not actually applying
  it at every mating surface.
- Claiming a dimension "should fit" without checking it against the actual
  numbers in `hardware/mechanical-interface.md`.
- Treating your own self-check as a substitute for independent review.
- Implying a CAD tool rendered or validated the design when none is
  connected — say "text/parametric output, not yet rendered" instead.
