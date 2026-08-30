# Design Review — Cycle Report Template

One instance of this report per Hardware Reviewer cycle (initial review or
a re-review after loop-back). Copy this template into a dated entry (or a
new file per cycle, e.g. `validation/design-review-2026-01-01.md`, linked
from here) — do not overwrite a previous cycle's report.

## Review Cycle Metadata

- **Design revision reviewed**: `<hardware/schematic ref + revision>`
- **Reviewer**: Hardware Reviewer (independent — see `.github/agents/hardware-reviewer.agent.md`)
- **Independence statement**: I did not author this design. Findings below
  were derived by re-checking each item directly against the datasheet /
  Evidence ID, not by trusting the Circuit Engineer's stated rationale.
- **Scope**: `<what was in scope for this cycle — full design, or only the changed area + affected areas after a loop-back>`
- **Parallel sub-scans run**: `<e.g. power/thermal, interface/timing, protection/EMI>`
- **rubber-duck premise review run in parallel?**: `<Y/N — if Y, see its findings tagged Source=rubber-duck in validation/open-issues.md>`
- **KiCad tool cross-checks used**: `<e.g. extract_schematic_netlist, identify_circuit_patterns, run_drc_check — or "none, no KiCad project yet">`

## Checklist Results

Full checklist per `.github/skills/hardware-review/SKILL.md`:

| # | Checklist item | Result | Notes |
|---|---|---|---|
| 1 | Voltage violation | `<Pass/Finding>` | |
| 2 | Absolute Maximum Rating violation | | |
| 3 | Current limit | | |
| 4 | Thermal risk | | |
| 5 | Missing decoupling capacitor | | |
| 6 | Floating pin | | |
| 7 | Incorrect pull-up/pull-down | | |
| 8 | Logic voltage mismatch | | |
| 9 | Interface timing | | |
| 10 | Power sequencing | | |
| 11 | Grounding | | |
| 12 | EMI/EMC risk | | |
| 13 | Motor noise | | |
| 14 | Sensor noise | | |
| 15 | PCB layout concern (incl. mechanical/thermal co-design) | | |
| 16 | Datasheet recommendation violation | | |

## Findings

For each finding with a result of "Finding" above, add full detail (also
mirrored into `validation/open-issues.md`):

### `<ISS-XXX>` — `<short title>`

- **Issue**:
- **Rationale**:
- **Datasheet Source**: `<Evidence ID>`
- **Failure Mechanism**:
- **Affected Component**:
- **Recommended Fix**:
- **Severity**: `<CRITICAL/HIGH/MEDIUM/LOW>`

## Verdict

- **Verdict**: `<PASS / FAIL / CONDITIONAL>`
- **Open CRITICAL count**: `<N>`
- **Open HIGH count**: `<N>`
- **Next action**: `<e.g. "loop back to Circuit Engineer for ISS-001, ISS-003" or "proceed to Validation">`
