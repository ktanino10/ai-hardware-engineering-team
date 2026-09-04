---
name: component-selection
description: Standard procedure for comparing and recommending electronic components from a requirement, comparing at least 3 candidates on datasheet-verified electrical specs, package, lifecycle/EOL risk, availability, reference designs, and development ecosystem. Use this whenever selecting or recommending a part for a hardware design.
---

# Skill: Component Selection

## Purpose

Standard procedure for turning a requirement into a datasheet-grounded part
recommendation that maximizes the probability this project succeeds — not
necessarily the highest-peak-spec part.

## When to use

Whenever a new part is needed, or an existing part choice is challenged
(e.g. by a Hardware Reviewer finding or an EOL notice).

## Inputs

- `requirements/requirements.md` (the specific requirement(s) driving this
  part need).
- Constraints: cost ceiling, temperature range, size/form factor, expected
  production volume, schedule.

## Procedure

1. **Derive the concrete need** from requirements (e.g. "3-axis
   accelerometer + gyroscope, I2C or SPI, ≤ 3.6 V supply").
2. **Search for candidates.** Identify **at least 3** when feasible. If
   fewer exist (genuine sole-source), document why in
   `bom/component-selection.md` rather than silently comparing fewer.
   Independent candidate research is parallel-safe
   (`docs/architecture.md` §4) — use `explore`/`research` sub-agents per
   candidate.
3. **Retrieve each candidate's datasheet.** Register it as a metadata record
   in `datasheets/` (never commit the actual PDF — `datasheets/README.md`)
   and run `.github/skills/datasheet-analysis/SKILL.md` against it.
4. **Build the comparison table** in `bom/component-selection.md`:
   electrical specs (`Parameter | Min | Typ | Max | Unit | Source`, Evidence
   ID per row), package, price at the expected quantity, lifecycle/EOL
   status, availability (stock/lead time), reference design availability,
   SDK/sample-code/documentation ecosystem maturity.
5. **Score for success probability, not peak spec.** Weigh: does it have a
   working reference design, mature tooling, acceptable EOL risk, actual
   stock — not just "best number in the datasheet". A part with a slightly
   worse spec but a proven reference design and long lifecycle often wins.
6. **Identify UNKNOWNs and risks.** Anything not confirmed by a primary
   source is `UNKNOWN`, not a guess.
7. **Draft a recommendation** with explicit rationale and trade-offs.
8. **Escalate to the human** if: no datasheet can be found for a serious
   candidate, this is a first-time architecture-defining component, or the
   decision has major cost/schedule impact (`docs/architecture.md` §10).
9. **Record the outcome** in `bom/component-selection.md`, including
   approval status.


## Foundational Change Cascade Checklist (revising an existing recommendation, not making a first pick)

`docs/workflow.md` §4.2/§4.2.1 documents this repository's recurring
"stale load-bearing figure propagation" failure mode: a root fact gets fixed
in its home artifact, but downstream citations and decisions keep silently
carrying the old value. Electronics has real precedent here too — not just
hypotheticals. `MISS-029` shows `bom/component-selection.md` itself carried a
stale friction-torque margin after the rotating assembly mass changed, and
`MISS-021`/`ISS-024` show the same pattern elsewhere in the discipline.
**Whenever you are revising an already-issued recommendation because a
foundational fact changed** (part substitution, datasheet revision, corrected
Evidence ID, corrected package/mechanical drawing, lifecycle/EOL status
change), do not stop at updating the comparison table row itself. Also:

1. **Re-derive every recommendation-driving claim from the current primary
   source, not from your own prior write-up.** If the datasheet revision or
   manufacturer drawing changed, re-run `.github/skills/datasheet-analysis/SKILL.md`
   from the live source and update `datasheets/evidence-log.md` before
   touching downstream artifacts; do not let the old Evidence ID prose stand
   in for a fresh read of the new source.
2. **Sweep every downstream artifact that cites the changed fact, not only
   `bom/component-selection.md`.** At minimum ask: does this changed number or
   conclusion also appear in the schematic/design rationale,
   `hardware/power-budget.md`, `requirements/traceability-matrix.md`,
   `validation/open-issues.md`, or a reviewer finding/disposition note? This
   is the Electronics analogue of §4.2.1's snapshot-drift seam: a corrected
   recommendation with stale downstream citations is still a live defect.
3. **Separate "part unchanged, citation corrected" from "part choice itself
   changed."** A repaired Evidence ID or clarified datasheet note may require
   only citation propagation; a real part substitution or materially changed
   operating limit requires re-checking the Circuit Engineer's implementation,
   not just the BOM prose. State explicitly which case you are in.
4. **Re-check package/footprint-affecting facts as cross-discipline facts, not
   only procurement facts.** If the package code, pinout variant, exposed pad,
   connector geometry, or mounting dimensions changed, flag that the Circuit
   Engineer and Hardware Reviewer must re-verify the live schematic/PCB
   against the current source rather than assuming the prior implementation
   still fits the recommendation.
5. **Re-check accepted reviewer dispositions that were signed off against the
   old fact.** If a prior trade-off, waiver, or `ACCEPTED-RISK` note cited the
   superseded spec/status, it does not auto-extend to the new configuration;
   call it out for fresh review rather than silently inheriting the old
   disposition.
6. **Record the propagation sweep in the changed artifact, not just in your
   head.** Per `docs/workflow.md` §4.2's own resolution convention, a revision
   is not complete merely because the source row is corrected; leave an
   auditable trace of what dependent artifacts were checked/updated or why a
   cited field was unaffected.

## Output format

`bom/component-selection.md`, per its template.

## Common failure modes to avoid

- Picking based on marketing copy or a single headline spec instead of the
  actual datasheet.
- Ignoring EOL/lifecycle status because the part "looks good today".
- Ignoring SDK/tooling/reference-design maturity — a part with perfect specs
  but no usable reference design or driver support can sink a schedule.
- Comparing fewer than 3 candidates without documenting why.
