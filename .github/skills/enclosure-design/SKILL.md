---
name: enclosure-design
description: Design or revise a physically buildable enclosure from sourced interfaces, with early WIP installed/per-stage assembly evidence, real mounting/wiring/tool access and Fusion assembly planning before final readiness. Use whenever creating or revising a mechanical assembly, enclosure, or its physical interfaces; verify tooling at runtime.
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
- Discover current model/animation/save/export capabilities using
  `.github/skills/mechanical-visualization/SKILL.md`; do not treat a
  historical no-CAD observation as current. Source/text-only output is
  an honest WIP fallback, not a completed assembly package.

## Procedure

1. **Confirm the interface data.** Read `hardware/mechanical-interface.md` in
   full. For UNKNOWN dependencies, route source investigation or a concrete
   alternative through Hardware Lead; stop relying on that value, not all
   WIP evidence generation. Preserve human architecture/safety decisions
   (`docs/architecture.md` §10); do not substitute a guessed number.
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
8. **Plan and inspect the build before final readiness.** Use
   `.github/skills/mechanical-visualization/SKILL.md` and
   `docs/assembly-evidence.md` to generate WIP instructions, component/
   coordinate mapping, full installed and per-stage evidence, and requested
   Fusion Animation. Include populated/mated electronics, all required
   sensors/boards/drivers/power, motors/hubs/swept envelopes, mounting/
   insulation, fasteners, retained wiring and insertion/seating/removal/
   tool access. Record unknowns and path-check limits, not cosmetic
   installed-pose fixes. Visualization cannot silently change this design.
9. **Self-check against the Mechanical Reviewer's checklist**
   (`.github/skills/mechanical-review/SKILL.md`) before handing off — the
   goal is to catch the obvious issues yourself so independent review finds
   the subtler ones, not to skip review.
10. **Hand off** to the Mechanical Reviewer: source + dimensional table +
    rationale + self-check + revision-linked assembly manifest and open
    UNKNOWN/capability blockers. Request early blocker review even if
    incomplete; APPROVED documentation remains behind independent acceptance,
    Design Complete and named safety gates.

## Handling Mechanical Reviewer findings (loop-back)

Address every CRITICAL/HIGH finding explicitly: fix and record the fix (with
an updated Evidence ID/interface reference if applicable), or state why you
believe it doesn't apply (with evidence) and let the Hardware Lead mediate
rather than unilaterally dismissing it. Log the change in
`validation/change-log.md` (ECO) if the design actually changes, and check
`validation/change-impact-matrix.md`'s existing "Mechanical" impact row if
the fix could ripple back into Electronics.

## Foundational Change Cascade Checklist (revising an existing design)

Added following MISS-034 (CRITICAL, `validation/open-issues.md`): the
enclosure was dimensioned around a 100×50mm PCB proposal for two days and
three merged PRs after the real board was laid out at 150×95mm — nothing
caught the drift until a scheduled audit measured real geometry by hand.
See `docs/workflow.md` §4.2/§4.2.1 for the general failure mode. **Whenever
you are revising an existing enclosure because a foundational physical fact
changed (a board outline, a mounting-hole pattern, a purchased component's
confirmed dimension) — not designing from scratch — work through every
category below, not only the file where the fact itself lives:**

1. **The parametric cascade in the `.scad` file itself.** Change the root
   variable(s) only, then re-render (`openscad --backend=manifold --render`)
   and independently re-derive every DERIVED value that depends on it — via
   a live `echo()`/`include<>` dump against the actual file, not hand
   arithmetic — before touching any downstream document. Distinguish
   variables that are genuine formulas (which cascade automatically once the
   root changes) from ones that only *look* related but are independent
   hardcoded literals (e.g. a mid-assembly axis-centering constant, a
   different subsystem's own geometry) — verify which is which by tracing
   the actual formula, not by assuming symmetry.
2. **Exported binaries** (STL/OBJ/etc.). Re-export every affected piece
   using this project's own documented wrapper-script convention
   (`hardware/mechanical/stl/export/*.scad` or equivalent), then
   independently re-measure the real output (`trimesh`/`numpy-stl`
   bounding box + volume, not the `.scad` source's own claimed numbers) —
   confirm both what changed AND what a formula-independence claim says did
   *not* change (a real re-measurement, e.g. comparing byte sizes/bounding
   boxes before and after, is stronger evidence than a comment claiming
   independence).
3. **Visualizations and drawings** derived from those binaries (2D
   orthographic renders, exploded views, drafting sheets, Fusion native
   storyboards/published videos, 3D viewers). Some
   are regenerable with the same toolchain used for the `.scad`/STL work
   (e.g. pure OpenSCAD CLI); others may depend on a separately-verified tool
   (e.g. Blender via MCP) that might not be connected this session — check
   per-session, per `docs/architecture.md` §5.3/§13's own convention, and
   disclose honestly (do not fabricate updated pixel/render output for a
   tool you could not actually invoke). Update source/artifact hashes in
   the current revision manifest and invalidate affected acceptance.
4. **Safety-margin-dependent constants that are measured, not formulas.**
   A hardcoded-but-empirically-measured constant (e.g. a rotating envelope's
   own max radius, obtained by rendering and measuring a mesh rather than by
   a closed-form equation) does NOT automatically update when its own
   inputs change — it must be re-measured with the same method that
   produced it originally. Explicitly ask: does anything this design change
   affects feed into a *previously measured* (not formula-derived) safety or
   clearance constant elsewhere in the same file?
5. **Already-human-accepted risk dispositions computed against the OLD
   numbers.** If step 4 turns up a materially changed safety-relevant
   constant, check whether any `ACCEPTED-RISK` finding in
   `validation/open-issues.md` was signed off against the specific old
   numbers — per this project's own REQ-408 precedent ("a disposition does
   not auto-extend" to a materially different configuration), do not treat
   a prior sign-off as still covering a new, more severe picture. Re-open
   the finding with the new numbers and a concrete remedy trade-off table
   for fresh human review, rather than silently carrying the old acceptance
   forward or silently re-deciding it yourself.
6. **The interface-file snapshot's own re-verification against its live
   upstream Source of Truth**, not just internal consistency. Where the
   upstream fact comes from a machine-readable file (a KiCad project, a
   generated BOM), re-derive it directly from that file this pass — do not
   only check that your own downstream numbers are internally consistent
   with each other, since the entire MISS-034 defect was internally
   consistent within Mechanical the whole time. Where a targeted automated
   check exists for this pair of facts (see `tools/check_mechanical_pcb_sync.py`
   for the current board-outline/mounting-hole instance), run it yourself
   before handoff rather than waiting for CI.
7. **Anything explicitly out of this pass's own bounded scope.** A resize
   fix does not obligate re-deriving every other field that happens to sit
   near the changed one (e.g. connector/component cutout positions, a
   from-scratch CG/tip-over re-sweep) — but log what you deliberately did
   NOT re-derive as a new, separate, honestly-scoped finding (cross-
   referencing any FMEA entry that already anticipated the gap), not a
   silent omission.

## Output

`.scad` file + dimensional-spec table (both under `hardware/mechanical/`) +
design rationale log + self-check results + the WIP assembly evidence
manifest/package in `docs/assembly-evidence.md`, referencing
`hardware/mechanical-interface.md`. Release is a later, explicitly gated state.

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
