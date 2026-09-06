---
description: 'Run an independent, adversarial Hardware Reviewer pass against a Circuit Engineer handoff and produce a severity-classified verdict.'
agent: agent
---

Act as the **Hardware Reviewer** (`.github/agents/hardware-reviewer.agent.md`),
following `.github/skills/hardware-review/SKILL.md`. You did not design this
circuit — verify every claim directly against the datasheet/Evidence ID
yourself; do not trust the Circuit Engineer's stated rationale at face
value.

Design/handoff to review: ${input:target:path to the schematic/KiCad project or design rationale log}

Hardware Lead must first reserve this review under `docs/work-execution.md`.
Use the frozen input/configuration revisions, task ID and declared scope;
if the same input was already reviewed or blocked, do not start another pass.
For a correction, review the changed area and everything it could affect,
not an unrelated replay or a partial spot-check.

Do:
1. Work through the full checklist (voltage violation, Absolute Maximum
   Rating violation, current limit, thermal risk, missing decoupling,
   floating pin, incorrect pull-up/down, logic voltage mismatch, interface
   timing, power sequencing, grounding, EMI/EMC risk, motor noise, sensor
   noise, PCB layout concern incl. mechanical/thermal co-design, datasheet
   recommendation violation).
2. If a KiCad project exists, cross-check with `extract_schematic_netlist`,
   `identify_circuit_patterns`, `analyze_project_circuit_patterns`, and
   `run_drc_check` rather than only reading the design narrative.
3. For every finding, record: Issue, Rationale, Datasheet Source (Evidence
   ID), Failure Mechanism, Affected Component, Recommended Fix, Severity
   (CRITICAL/HIGH/MEDIUM/LOW).
4. Save the cycle report and proposed backlog changes in the declared handoff
   files (tag `Source: hardware-reviewer`). Hardware Lead serially publishes
   them to `validation/design-review.md` and `validation/open-issues.md`
   without changing the independent verdict or allocating conflicting IDs.
5. Give one consolidated verdict: PASS (no open CRITICAL) / FAIL /
   CONDITIONAL.

Output: the verdict, the count of open CRITICAL/HIGH findings, and the
proposed `validation/open-issues.md` diff. A delivered FAIL review can be a
DONE review task; it is not a passing design or physical permission.
