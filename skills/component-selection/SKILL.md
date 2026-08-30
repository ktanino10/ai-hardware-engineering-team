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
   and run `skills/datasheet-analysis/SKILL.md` against it.
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

## Output format

`bom/component-selection.md`, per its template.

## Common failure modes to avoid

- Picking based on marketing copy or a single headline spec instead of the
  actual datasheet.
- Ignoring EOL/lifecycle status because the part "looks good today".
- Ignoring SDK/tooling/reference-design maturity — a part with perfect specs
  but no usable reference design or driver support can sink a schedule.
- Comparing fewer than 3 candidates without documenting why.
