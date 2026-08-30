---
description: 'Run an independent, adversarial Hardware Reviewer pass against a Circuit Engineer handoff and produce a severity-classified verdict.'
agent: agent
---

Act as the **Hardware Reviewer** (`agents/hardware-reviewer.agent.md`),
following `skills/hardware-review/SKILL.md`. You did not design this
circuit — verify every claim directly against the datasheet/Evidence ID
yourself; do not trust the Circuit Engineer's stated rationale at face
value.

Design/handoff to review: ${input:target:path to the schematic/KiCad project or design rationale log}

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
4. Write a full cycle report into `validation/design-review.md` and roll
   findings into `validation/open-issues.md` (tag `Source: hardware-reviewer`).
5. Give one consolidated verdict: PASS (no open CRITICAL) / FAIL /
   CONDITIONAL.

Output: the verdict, the count of open CRITICAL/HIGH findings, and the
updated `validation/open-issues.md` diff.
