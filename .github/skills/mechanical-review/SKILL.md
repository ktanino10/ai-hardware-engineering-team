---
name: mechanical-review
description: Checklist and failure-analysis procedure for an independent, adversarial mechanical review of an enclosure design -- PCB mounting, connector accessibility, component-height clearance, internal clearance, fastener placement, wall thickness, assembly order, print-fit tolerance, and basic manufacturability/3D-printability. Use this whenever reviewing a mechanical/enclosure design that was not authored by the reviewer.
---

# Skill: Mechanical Review

## Purpose

Checklist and failure-analysis procedure for an **independent**, adversarial
mechanical review — the standard operating procedure behind
`.github/agents/mechanical-reviewer.agent.md`. Mirrors
`.github/skills/hardware-review/SKILL.md`'s structure and rigor, re-derived
for mechanical/enclosure concerns instead of electrical ones.

## When to use

Every time the Mechanical Lead hands off an enclosure design (initial or
after a loop-back fix). Re-review after a fix means re-running the checklist
against the changed area and anything the change could have affected — not a
partial spot-check.

## Independence rule

You are not checking your own work. Do not accept the Mechanical Lead's
stated rationale as fact — verify each claim directly against
`hardware/mechanical-interface.md` and the actual `.scad`/dimensional-spec
values yourself. Actually compute clearances where you can (interior
dimension minus wall thickness minus standoff height, etc.) rather than
trusting a verbal "it fits."

## Checklist (work through all of these; not a sample)

1. PCB mounting — hole positions/diameters vs. the interface file; standoff
   height and boss integrity.
2. Connector accessibility — cutout position/size/orientation vs. the
   interface file's connector locations; nothing blocked by a wall or
   another part.
3. Component height clearance — top and bottom, vs. the interface file's max
   component height fields.
4. Internal clearance / interference — parts vs. walls, parts vs. each
   other, parts vs. fastener bosses.
5. Fastener placement — adequate wall thickness around every screw boss;
   fastener doesn't conflict with a component or another fastener.
6. Wall thickness — adequate for structural integrity **and** for the
   Mechanical Lead's own stated 3D-printability rule.
7. Assembly order — a physically achievable sequence; no part trapped behind
   another with no access to insert/remove it.
8. Basic print-fit tolerance — the stated clearance allowance is actually
   applied consistently at every mating interface.
9. Basic manufacturability / 3D-printability — overhangs/bridges within the
   Mechanical Lead's own stated printability rule; minimum wall thickness
   actually met everywhere.
10. Interface-value traceability — every dimension traces to an interface
    row/Evidence ID or is explicitly `ASSUMPTION`/`ESTIMATE`
    (`.github/instructions/mechanical-design.instructions.md`).

## Failure analysis — for each potential issue found, work out

- What actually happens physically if this ships as-is (the **failure
  mechanism** — not just "violates the interface spec," but *how* it fails:
  board can't seat flush, lid won't close, boss cracks under screw torque,
  part collides with wall, etc.)
- Under what conditions it manifests (always vs. only at the printer's actual
  tolerance/warping extremes)
- Whether it's a **design** defect (fixable by the Mechanical Lead) vs. an
  **interface** defect (the electronics-side facts themselves were wrong or
  incomplete — needs to go back through the Hardware Lead / Circuit Engineer)

## Finding record format (mandatory fields)

- **Issue**
- **Rationale**
- **Datasheet Source** (Evidence ID, or the specific
  `hardware/mechanical-interface.md` row)
- **Failure Mechanism**
- **Affected Component**
- **Recommended Fix**
- **Severity**: CRITICAL / HIGH / MEDIUM / LOW

Severity definitions: `docs/architecture.md` §7.1 (reused verbatim from
Hardware Reviewer — not redefined). Mechanical-flavored examples:

| Severity | Example |
|---|---|
| CRITICAL | The PCB physically does not fit inside the stated enclosure interior dimensions |
| HIGH | A connector cutout is misaligned, requiring drilling/rework to access the port |
| MEDIUM | Wall thickness thinner than the stated 3D-printing minimum, risking warping |
| LOW | Assembly order not documented, or a fastener spec left unlabeled |

## Output

- `validation/design-review.md`: this cycle's full report (scope, checklist
  results, findings, verdict) — a new dated instance of the same template
  Hardware Reviewer uses.
- `validation/open-issues.md`: living backlog update — add new findings,
  update status of previously open ones. Tag `Source` as `mechanical-reviewer`
  (distinct from `hardware-reviewer` and `rubber-duck` —
  `docs/architecture.md` §5.1, `.github/instructions/validation.instructions.md`).

## Verdict rule

- **PASS**: no open CRITICAL finding.
- **FAIL / CONDITIONAL**: any open CRITICAL or HIGH — route back to
  Mechanical Lead via the Hardware Lead.
- Design Complete is never declared with an unresolved CRITICAL, regardless
  of verdict wording (`docs/architecture.md` §8) — this applies identically
  whether the CRITICAL came from Hardware Reviewer or Mechanical Reviewer,
  since both write to the same `validation/open-issues.md`.

## Common failure modes to avoid

- Anchoring on the Mechanical Lead's confidence or stated rationale instead
  of re-deriving the answer.
- Downgrading a CRITICAL to keep the process moving.
- Checking only one representative wall/boss/clearance instead of every
  instance — a wall thickness rule stated once can still be violated
  somewhere else in the same design.
- Treating "the interface file says so" as automatically correct without
  checking whether the interface file itself marked that value `ASSUMPTION`/
  `ESTIMATE`/`UNKNOWN` rather than `CONFIRMED`.
