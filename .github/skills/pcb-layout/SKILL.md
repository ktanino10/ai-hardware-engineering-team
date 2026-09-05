---
name: pcb-layout
description: Prepare bounded WIP PCB physical interfaces before Design Complete when assembly evidence needs them, then perform full layout, routing and DRC closure from the approved schematic. Use for source-grounded board-envelope/mount/connector planning or schematic-to-layout handoff; keep WIP preparation separate from independently reviewed fabrication release.
---

# Skill: PCB Layout

## Purpose

Provide PCB physical facts early enough to resolve assembly interfaces, then
turn a Design-Complete schematic into a physically buildable,
DRC-clean PCB: every symbol has a real footprint, every net is routed with
current-appropriate copper, the stack-up/outline is a justified decision
(not a default), and the fabrication-package inputs (flat BOM, visual
snapshot) are ready for independent review. **Full layout/routing** runs after the
Circuit Engineer's schematic has reached Design Complete
(`docs/architecture.md` §8) and **before** the Hardware Reviewer's
independent PCB-layout review (`docs/architecture.md` §10: "before PCB
fabrication"). The bounded WIP path below runs before that gate without
waiving schematic ownership, source requirements or physical-action holds.

## When to use

Whenever a project's schematic-to-layout handoff becomes a distinct phase
— either because a human explicitly requests an orderable-PCB stage, or
because a Design-Complete schematic is otherwise ready to leave the
Markdown/schematic-only stage. Also use the **scoped WIP preparation** path
when Hardware Lead needs actual populated-board, mounting or connector
geometry for assembly evidence before Design Complete. Do not expand that
exception into general routing or a fabrication-ready claim while the
schematic is still iterating.

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

## Scoped WIP physical-interface preparation

1. Identify the Circuit Engineer-owned source revision, approved part
   choices, relevant interfaces and the bounded facts Hardware Lead needs
   (`docs/workflow.md` Phase 4a). Check that the real KiCad snapshot reflects
   the facts being used; send schematic/connectivity corrections back to
   Circuit Engineer. Do not fill missing facts with guessed dimensions.
2. Source package/footprint dimensions and populate physical envelopes on
   both board faces, including fully mated connectors, mounting/insulation
   and insertion/tool-access allowances. Prepare provisional outline,
   hole/mount and placement geometry only as needed for assembly planning;
   distinguish sourced dimensions, engineering allocations and UNKNOWNs.
3. Hand off revision-linked **WIP - NOT ASSEMBLY READY** geometry and
   measurements to Mechanical Lead via Hardware Lead, including owners/
   next actions for missing interfaces and the actual routing/DRC state.
   Use `docs/assembly-evidence.md`; do not present a bare board rectangle
   or an unrouted mock-up as a verified complete PCB.
4. Request early independent blocker review as useful and regenerate affected
   evidence after source changes. Stop this scoped path before general
   routing or fabrication release. Architecture, part/topology, major BOM and
   safety decisions still require their existing named human approvals.

## Full-layout procedure

1. **Confirm the KiCad schematic actually reflects the Design-Complete
   design before general routing/full layout.** This condition does not block
   the scoped WIP preparation above. A schematic design document can reach
   Design Complete (Markdown/net-list level) before every circuit block in
   it is transcribed into the real KiCad project — check both against each
   other (symbol count, net list) rather than assuming the KiCad file is
   current just because the document is Design Complete. If a gap exists,
   route it to Circuit Engineer to update its owned schematic using the
   established authoring method and re-verify with available ERC/netlist
   tooling before proceeding. Do not silently edit connectivity in PCB work.
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

For scoped WIP: revision-linked populated/mated envelopes, provisional
outline/mount/placement geometry, confidence labels, explicit missing
interfaces/owners and routing/DRC limitations for early assembly/blocker review.
This is not a completed layout or permission to fabricate.

For full layout: the completed `.kicad_pcb` (footprints placed, nets routed, stack-up
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
   handoff (a finalized Phase 8 input, not a WIP entry prerequisite) does not remain valid
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
