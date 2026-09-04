---
name: pcb-layout
description: Standard procedure for taking a Design-Complete schematic to a real, DRC-clean PCB layout -- footprint assignment (CONFIRMED/ASSUMPTION labeled), board outline and layer-stackup justification, placement, current-aware routing, and DRC closure -- producing a flat order-ready BOM and a visual snapshot for independent review. Use this whenever a schematic-to-layout handoff is starting or a KiCad project needs its footprints/PCB completed.
---

# Skill: PCB Layout

## Purpose

Turn an already Design-Complete schematic into a physically buildable,
DRC-clean PCB: every symbol has a real footprint, every net is routed with
current-appropriate copper, the stack-up/outline is a justified decision
(not a default), and the fabrication-package inputs (flat BOM, visual
snapshot) are ready for independent review. This runs **after** the
Circuit Engineer's schematic has reached Design Complete
(`docs/architecture.md` §8) and **before** the Hardware Reviewer's
independent PCB-layout review (`docs/architecture.md` §10: "before PCB
fabrication").

## When to use

Whenever a project's schematic-to-layout handoff becomes a distinct phase
— either because a human explicitly requests an orderable-PCB stage, or
because a Design-Complete schematic is otherwise ready to leave the
Markdown/schematic-only stage. Not needed while a design is still iterating
at the schematic level (Circuit Engineer + Hardware Reviewer's normal
loop-back cycle, `docs/architecture.md` §2) — layout work on a design that
hasn't reached Design Complete risks being redone every time the schematic
changes.

## Inputs

- The real KiCad project (`hardware/schematic/<board>/`) and its schematic
  design document (`hardware/schematic/<board>-design.md`) — the net-by-net
  and parts-list sections are your authoritative connectivity source.
- `bom/component-selection.md`'s Approval sections — the human-approved
  part choices and their already-cited pricing/MPNs, reused, not
  re-researched.
- Any existing footprint/package decisions already on record (e.g. a prior
  KiCad-authoring session's own "Symbol/footprint decisions" table) — reuse
  and extend rather than re-deciding parts already confirmed.

## Procedure

1. **Confirm the KiCad schematic actually reflects the Design-Complete
   design before touching layout.** A schematic design document can reach
   Design Complete (Markdown/net-list level) before every circuit block in
   it is transcribed into the real KiCad project — check both against each
   other (symbol count, net list) rather than assuming the KiCad file is
   current just because the document is Design Complete. If a gap exists,
   extend the KiCad schematic first (reusing whatever programmatic
   authoring method the project already established, e.g. a
   `generate_schematic.py`-style script — re-run it, don't hand-edit the
   generated file), and re-verify with `kicad-cli sch erc` +
   `sch export netlist` before proceeding to layout.
2. **Assign every missing footprint.** For each symbol without one: find
   the part's real package from its own datasheet/mechanical drawing or a
   real distributor listing. Label CONFIRMED (matches a part-specific
   drawing, or an existing design-doc statement of package) or ASSUMPTION
   (a real judgment call — state the reasoning, e.g. "no exact package
   size was pinned down earlier in this design's history; chosen for
   package-size consistency with sibling parts on this board"). Any
   explicit electrical rating already stated for a part (e.g. a resistor's
   stated power rating) constrains which footprint is physically valid —
   check it before defaulting to whatever package size the rest of the
   board uses.
3. **Decide and justify board outline + layer stack-up.** Never default to
   a layer count or size. Real inputs to weigh: summed footprint/courtyard
   area plus assembly/routing margin, any stated board-size requirement,
   and whether the design's own record already flags a real reason a
   single/double-layer board would be inadequate (e.g. a documented
   noise-coupling concern between a switching subsystem and a
   noise-sensitive one, a documented need for a solid, low-impedance
   ground/power return). If layer count is increased beyond the minimum,
   state the specific reason(s) — do not justify a stack-up choice merely
   by asserting it's "better practice" in the abstract.
4. **Place components.** Respect any physical-separation/grouping reason
   already on record in the design document (e.g. keep a noise source
   away from a noise-sensitive part) — the *reason* should already exist
   in the schematic-stage record; you decide the concrete geometry that
   satisfies it, not whether the concern is real.
5. **Route every net.** Size trace widths for the net's real
   current-carrying requirement (a motor-phase or power net needs wider
   copper than a low-current logic signal) — do not apply one uniform
   trace width regardless of net. Where a stack-up includes dedicated
   plane layers, use via-stitching to the plane for power/ground rather
   than point-to-point traces for those nets.
6. **Run DRC to closure.** Iterate until genuinely clean, or disclose
   precisely what remains open and why — never round an incomplete result
   up to "clean." Track results over time (this project's own DRC-history
   tooling, where available) so a later session can see the trend, not
   just the latest snapshot.
7. **Generate the fabrication-package inputs**: a flat BOM (reference
   designator, manufacturer part number, footprint, quantity for one
   build, unit price) — pull already-approved parts' MPNs/pricing forward
   from `bom/component-selection.md` rather than re-deriving them, and
   source real distributor part numbers for anything not already covered
   there, flagging any part you cannot pin to a real orderable SKU as an
   explicit open item, never a silent placeholder — and a visual layout
   snapshot for the human/reviewer.
8. **Hand off to the Hardware Reviewer for independent review** — never
   self-declare "ready to fabricate." Report the actual verdict (including
   CONDITIONAL) to the Hardware Lead/human plainly.

## Output

The completed `.kicad_pcb` (footprints placed, nets routed, stack-up
defined), a DRC report/history entry, a flat order-ready BOM, a visual
snapshot attached to `validation/design-review.md` per this project's
existing convention, and a handoff to the Hardware Reviewer for independent
PCB-layout review before any fabrication-readiness claim.

## Foundational Change Cascade Checklist (revising an existing layout, not a first-time board)

Added following MISS-034's named upstream/downstream handoff failure mode
(`docs/workflow.md` §4.2/§4.2.1): **when a PCB layout revision changes a
foundational board fact that other artifacts consume as a snapshot** — board
outline, mounting-hole pattern, connector edge location/orientation, layer
count/stack-up, or any fabrication-output-driving footprint/package decision —
do not treat "the `.kicad_pcb` is updated" as sufficient. The demonstrated gap
was not that PCB failed to update itself; it was that PCB, as the upstream
Source of Truth, did not proactively push the changed geometry to downstream
consumers. Work through every category below before handoff:

1. **Explicit outbound re-handoff of board-geometry changes.** If the outline,
   hole pattern, or connector edge geometry changed from the last handed-off
   state, explicitly notify/re-trigger every downstream consumer of that
   geometry — at minimum Mechanical via `hardware/mechanical-interface.md`, and
   any board-geometry-derived drawing/fixture/manufacturing artifact that was
   previously generated from the old numbers. Do not passively assume the
   downstream discipline will notice on its own; §4.2.1 exists because that
   exact assumption already failed once.
2. **Re-derive the downstream-facing snapshot inputs from the live
   `.kicad_pcb`, not from memory or a stale side table.** For board dimensions,
   hole coordinates, and connector locations, read them back from the current
   layout file each pass before reporting them outward. The receiving-side CI
   guard (`tools/check_mechanical_pcb_sync.py`) is a useful safety net, but it
   is not a substitute for the PCB Engineer proactively re-handing-off changed
   facts when the PCB itself is what moved.
3. **Treat board-outline/mounting changes as invalidating prior mechanical
   assumptions until re-confirmed.** A previously "stable board outline"
   handoff (the Phase 8 trigger in `docs/workflow.md`) does not remain valid
   automatically after a later layout growth/resize. If you changed the
   geometry, state plainly that Mechanical must re-run its own review cycle
   against the new snapshot rather than silently inheriting the old one.
4. **Re-export fabrication outputs whenever the layout facts they encode
   changed.** A prior BOM export, pick/place, Gerber set, drill file set,
   rendered board image, or reviewer snapshot is stale the moment footprint
   assignment, stack-up/layer count, board outline, drill pattern, or placed
   content changes. Regenerate the affected outputs from the updated project;
   do not keep presenting a previously exported package as if DRC alone had
   refreshed it.
5. **Re-run DRC after any geometry/footprint/stack-up change, not only after
   copper edits.** A footprint swap, courtyard growth, hole move, edge move, or
   layer-stack change can invalidate a previously reviewed board even if the
   netlist is unchanged. The "clean/stale" state belongs to a specific board
   revision, not to the project name in the abstract.
6. **Check for silent manufacturing-data drift caused by layout-only changes.**
   If a footprint/package decision changed, confirm the flat order-ready BOM's
   footprint/MPN/SKU mapping still matches what is actually placed. If the
   stack-up changed, confirm any fab notes or layer-count assumptions in the
   handoff package were regenerated too. Do not let the board file move while
   an older BOM/fab package continues circulating unchanged.
7. **Log bounded non-updated downstream items as explicit open follow-ups, not
   silent omissions.** If a change intentionally stops short of re-exporting a
   full fab package or intentionally leaves a downstream consumer awaiting a
   separate pass, say so plainly in the handoff/open-items list. "I only
   changed the board file" is acceptable only if paired with an explicit note
   of which dependent artifacts now require refresh.

## Common failure modes to avoid

- Assuming the KiCad schematic already reflects every Design-Complete
  circuit block without checking — a Markdown design document reaching
  Design Complete does not guarantee the real KiCad project was kept in
  sync with it.
- Guessing a footprint instead of confirming it against a real
  datasheet/mechanical drawing or distributor listing, or silently
  overriding an explicit electrical rating (e.g. a stated power rating)
  for cosmetic package-size consistency with the rest of the board.
- Defaulting to a layer count/board size without a stated, real reason —
  or, conversely, inventing a noise/EMI concern that isn't actually on
  record in the design document just to justify a preferred stack-up.
- Applying one uniform trace width to every net regardless of its real
  current-carrying requirement.
- Rounding an incomplete DRC result up to "clean," or claiming a capability
  (GUI authoring, autorouting, an MCP tool) that wasn't actually verified
  connected this session.
- Self-declaring the layout "reviewed" or "ready to fabricate" instead of
  routing it through an independent Hardware Reviewer pass — the same
  Human-in-the-loop "before PCB fabrication" gate applies regardless of how
  confident the layout looks.
