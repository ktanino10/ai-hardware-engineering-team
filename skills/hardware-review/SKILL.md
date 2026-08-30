# Skill: Hardware Review

## Purpose

Checklist and failure-analysis procedure for an **independent**,
adversarial hardware review — the standard operating procedure behind
`.github/agents/hardware-reviewer.agent.md`.

## When to use

Every time the Circuit Engineer hands off a design (initial or after a
loop-back fix). Re-review after a fix means re-running the checklist against
the changed area and anything the change could have affected — not a
partial spot-check.

## Independence rule

You are not checking your own work. Do not accept the Circuit Engineer's
stated rationale as fact — verify each claim directly against the
datasheet/Evidence ID yourself. If a KiCad project exists, verify with tools
(`extract_schematic_netlist`, `identify_circuit_patterns`,
`analyze_project_circuit_patterns`, `run_drc_check` —
`docs/architecture.md` §5.2) rather than only the design rationale log.

## Checklist (work through all of these; not a sample)

1. Voltage violation
2. Absolute Maximum Rating violation
3. Current limit
4. Thermal risk
5. Missing decoupling capacitor
6. Floating pin
7. Incorrect pull-up/pull-down
8. Logic voltage mismatch
9. Interface timing
10. Power sequencing
11. Grounding
12. EMI/EMC risk
13. Motor noise
14. Sensor noise
15. PCB layout concern (including mechanical/thermal co-design near
    rotating bodies — `docs/architecture.md` §12)
16. Datasheet recommendation violation

Topic-based sub-scans (e.g. power/thermal vs. interface/timing vs.
protection/EMI) may run in parallel. Consolidating them into one verdict is
always a serial step owned by a single Reviewer pass
(`docs/architecture.md` §4).

## Failure analysis — for each potential issue found, work out

- What actually happens electrically/physically if this ships as-is
  (the **failure mechanism** — not just "this violates the datasheet", but
  *how* it fails: overheats, latches up, resets randomly, corrupts data,
  etc.)
- Under what conditions it manifests (always vs. only at temperature/
  voltage/current corners)
- Whether it's a **design** defect (fixable by the Circuit Engineer) vs. a
  **component** defect (needs to go back through Component Engineer)

## Finding record format (mandatory fields)

- **Issue**
- **Rationale**
- **Datasheet Source** (Evidence ID)
- **Failure Mechanism**
- **Affected Component**
- **Recommended Fix**
- **Severity**: CRITICAL / HIGH / MEDIUM / LOW

Severity definitions: `docs/architecture.md` §7.1.

## Output

- `validation/design-review.md`: this cycle's full report (scope, checklist
  results, findings, verdict).
- `validation/open-issues.md`: living backlog update — add new findings,
  update status of previously open ones. Tag `Source` as
  `hardware-reviewer` (as distinct from `rubber-duck` premise-review
  findings, which use the same backlog but a different `Source` tag —
  `docs/architecture.md` §5.1).

## Verdict rule

- **PASS**: no open CRITICAL finding.
- **FAIL / CONDITIONAL**: any open CRITICAL or HIGH — route back to Circuit
  Engineer via the Hardware Lead.
- Design Complete is never declared with an unresolved CRITICAL, regardless
  of verdict wording (`docs/architecture.md` §8).

## Common failure modes to avoid

- Anchoring on the designer's confidence or stated rationale instead of
  re-deriving the answer.
- Downgrading a CRITICAL to keep the process moving — if new evidence
  changes the classification, say so explicitly with that evidence.
- Treating "the reference design does this" as automatically correct — the
  Circuit Engineer's implementation might deviate from the reference design
  in ways that matter.
