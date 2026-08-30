# Skill: Requirements Engineering

## Purpose

Turn a rough, possibly ambiguous statement of intent into a requirements
document that Component Selection can actually act on. This runs **before**
Component Selection (`docs/workflow.md` Phase 1).

## When to use

At the start of a design cycle, or whenever requirements change materially
(new subsystem, changed constraint, changed target environment).

## Inputs

- Whatever the human Product Owner has said, in any form (a sentence, a
  bullet list, a half-finished spec).
- Prior `requirements/requirements.md`, if updating rather than starting
  fresh.

## Procedure

1. **Detect ambiguity.** Flag statements that can't be tested/verified as
   written (e.g. "low power", "fast enough", "small"). List each as an open
   question.
2. **Quantify.** For each flagged item, propose a measurable, testable
   version with units and tolerance (e.g. "low power" → "average current
   draw ≤ 50 mA at 3.3 V over a 1-minute duty cycle"). Confirm the proposed
   number with the human — do not silently invent a number and treat it as
   settled.
3. **Prioritize.** Classify each requirement (e.g. Must / Should / Could /
   Won't, or Critical / Important / Nice-to-have). Priority affects trade-off
   decisions later (Component Selection, Conflict Resolution).
4. **Detect conflicts and gaps.** Check for:
   - Requirements that contradict each other (e.g. a cost ceiling
     incompatible with a stated performance floor)
   - Missing categories: electrical (voltage rails, current budget,
     interfaces), environmental (temperature range, vibration if
     applicable), mechanical/form factor, safety/regulatory,
     non-functional (cost target, schedule)
5. **Write `requirements/requirements.md`** using its template. Every
   requirement gets a stable ID (e.g. `REQ-001`) so
   `requirements/traceability-matrix.md` can reference it later.
6. **Initialize `requirements/traceability-matrix.md`** with one row per
   requirement, `Status = Pending`.
7. **Get human sign-off.** Requirements sign-off is not parallel-safe and is
   a HITL checkpoint in spirit (it seeds every downstream architecture/
   component decision) — confirm with the human before treating requirements
   as final.

## Output

`requirements/requirements.md` (filled in) + `requirements/
traceability-matrix.md` (initialized) + an explicit list of remaining open
questions for the human, if any.

## Common failure modes to avoid

- Quietly resolving an ambiguous requirement without flagging that you did
  so — the human should see and confirm the quantification, not discover it
  three phases later baked into a component choice.
- Treating "requirements engineering" as a one-time step — re-run it (at
  least the quantify/conflict-check parts) whenever requirements change.
- Skipping environmental/mechanical/safety categories because the human only
  mentioned electrical function.
