---
name: mechanical-review
description: Independently review mechanical geometry and revision-linked assembly evidence, including full installed/per-stage fit, retention, wiring, tool access and genuine Fusion native/video deliverables. Use for early WIP blocker reviews as well as final assembly acceptance; incomplete evidence never counts as readiness.
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

Also review DESIGN-STAGE WIP assembly plans/animations before Design
Complete, even when some evidence is incomplete: finding those blockers
early is the purpose. State the scope and missing evidence explicitly;
this is not final assembly acceptance (`docs/assembly-evidence.md`).

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
11. Manufacturing process specification (safety-critical/structural parts
    only) — for any part flagged safety-critical or structural (not
    cosmetic/fit-only), verify a Manufacturing Engineer process
    specification (infill %/pattern, wall/perimeter count, print
    orientation, material —
    `.github/skills/manufacturing-process-specification/SKILL.md`) actually
    exists and is internally consistent with the part's own disclosed load
    case, rather than assuming the CAD model's stated wall thickness alone
    guarantees the fabricated part has that much solid material. This is
    the independent check on Manufacturing Engineer's own output — do not
    accept its stated rationale as fact; re-derive whether the specified
    process plausibly matches the part's actual load path yourself.
12. Revision-linked assembly evidence — run
    `tools/check_assembly_evidence.py --manifest <current-manifest>` and
    inspect all contents required by `docs/assembly-evidence.md`. Cover the
    complete installed inventory and every insertion/seating/fastening/
    wiring/removal stage, including populated/mated PCBs and insulation,
    all required sensors/boards/drivers/power, motors/bells/hubs/swept
    envelopes, fasteners, retained harnesses and actual tool access.
    A scalar outline/hole match, bare board rectangle, render or export
    result is insufficient. Verify unit/part/hash/transform consistency,
    separate source dimensions from allocations/UNKNOWNs, and classify
    intentional fused-print unions, bearing contacts and qualified process
    interference separately from forbidden separate-part overlap.
    Record collision/path-check methods, sampling/tolerances and untested
    intervals. Animation is not proof of continuous clearance, support
    removal, strength, safety or functionality.

## Foresight checklist

The checklist above verifies the correctness of what the Mechanical Lead
actually claims — it is reactive by design. This checklist is different in
kind: this project's own history shows real defects get missed not because
a reviewer checked something wrong, but because nobody thought to check it
at all until an unrelated, downstream task stumbled into it (`MISS-007`,
found only while independently re-verifying an unrelated fix's side
effects; `MISS-001`'s own centerline-vs-footprint gap). Apply it whenever
you are asked to review or sanity-check *any* artifact that represents this
project's physical geometry — not only a formal `.scad` handoff, but also a
visualization, an exploded/assembly view, a technical drawing, or any other
downstream representation of the same physical parts
(`.github/skills/mechanical-visualization/SKILL.md`).

1. Physical interference, checked for real, not assumed absent — not just
   against a wall or fastener boss (checklist item 4 already covers that
   inside the Mechanical Lead's own model), but part-vs-part across the
   *whole* assembly, including in any downstream artifact (a rendered
   exploded view, an animation, a drawing) that repositions or represents
   the same parts. A task whose literal request was "produce a
   visualization," not "check for interference," does not excuse skipping
   this.
2. Simplified/approximate models don't quietly distort a real relationship
   — where a downstream representation approximates a part or assembly
   (e.g. treating a nested/inserted assembly as if it were simple
   flat-stacked plates), does that distort the *real* nesting/insertion
   relationship the authoritative source actually specifies (the real
   insertion depth/clearance in
   `hardware/mechanical/assembly-instructions.md`, the `.scad` file's own
   dimensions, or the dimensional-spec table)? A simplification chosen
   purely for rendering convenience must never silently become a new,
   uncorrected claim about how the physical parts actually fit together.
3. Scale/axis-transform sanity — whenever geometry crosses a unit,
   coordinate-convention, or tool boundary (mm vs. m, a different
   up-axis/handedness convention, an export/import step between tools), was
   basic consistency actually verified (e.g. an independently-derived
   bounding-box or dimension cross-check) rather than assumed correct?
   Generalizes this skill's own "verify the imported parts' real
   assembled-frame alignment before touching anything" rule beyond just its
   Fusion, Blender or any other tool boundary.

Also ask yourself, explicitly, at the end of every review: is there
anything within scope that nobody explicitly asked you to check, but that
you should have noticed anyway? This is the same habit that found
`MISS-007` — noticing a second effect while checking a first one, not
because the task asked for it. If something looks worth a future look but
isn't yet a concrete-enough finding for *this* handoff, record it under the
optional "Foresight notes" subsection (see Output) rather than silently
dropping it.

## Foundational Change Cascade Checklist (reviewing a resize/revision, not a first-time design)

Added following MISS-034 (CRITICAL) — a 100×50mm board proposal survived
three merged PRs after the real 150×95mm board existed, undetected by any
review cycle, because every cycle checked internal self-consistency, never
"has anything this design depends on changed since the last time someone
looked?" (`docs/workflow.md` §4.2/§4.2.1). **When reviewing a fix that was
triggered by a foundational physical fact changing (not a from-scratch
design), do not treat your mandatory checklist above as sufficient by
itself — it verifies internal consistency, which MISS-034 already proves
is not the same thing as correctness.** Additionally:

1. **Re-derive the root fact yourself, from the same upstream Source of
   Truth the Lead cited — do not just check that the Lead's own numbers are
   internally consistent with each other.** If a machine-readable upstream
   file exists (a KiCad project, a datasheet), read it yourself; if a
   targeted automated check exists for this class of fact (e.g.
   `tools/check_mechanical_pcb_sync.py`), run it yourself rather than
   trusting that the Lead ran it.
2. **Independently re-render/re-measure at least one exported binary
   (STL/etc.), not just the `.scad` source.** A clean render is not the
   same claim as a correct one — actually measure the bounding box/volume
   yourself (`trimesh`/`numpy-stl` or equivalent) and compare to what the
   Lead's own report claims.
3. **Check every hardcoded-but-empirically-measured constant that could be
   affected**, not only formula-derived ones. A rotating-envelope radius, a
   measured minimum clearance height, or any other "we rendered it once and
   wrote down the number" constant does not auto-update — confirm the Lead
   actually re-measured it (or explicitly, correctly argued it's
   unaffected) rather than silently carrying the old number forward.
4. **Check whether any `ACCEPTED-RISK` disposition in
   `validation/open-issues.md` was signed off against numbers this change
   just altered.** If so, per this project's own REQ-408 precedent, that
   acceptance does not auto-extend to the new configuration — the Lead
   should have re-opened it with a fresh trade-off presentation, not left
   it silently marked accepted, and not silently re-decided it themselves
   either (only a named human Chief Engineer sign-off can accept a HIGH
   finding).
5. **Verify a formula-independence claim by actually diffing output, not by
   trusting the comment that says so.** "This part's geometry doesn't
   depend on the changed input" is a testable claim (re-render it and
   compare bytes/bounding box/volume to the pre-change version) — test it,
   don't just read it.
6. **Check that anything explicitly left out of scope was actually logged
   as a new, separate finding, not silently dropped.** A resize fix
   legitimately does not have to re-derive every adjacent field, but a
   deliberately-bounded scope should leave a visible trace (a new
   MISS-XXX, or a cross-reference to an existing FMEA entry), not a silent
   gap discoverable only by someone else re-doing the same investigation.

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
| LOW | Non-blocking labeling omission in an otherwise evidenced assembly sequence |

## Output

- `validation/design-review.md`: this cycle's full report (scope, checklist
  results, findings, verdict) — a new dated instance of the same template
  Hardware Reviewer uses. State early WIP blocker review vs final
  acceptance; identify the exact source revision and artifact hashes.
- `validation/open-issues.md`: living backlog update — add new findings,
  update status of previously open ones. Tag `Source` as `mechanical-reviewer`
  (distinct from `hardware-reviewer` and `rubber-duck` —
  `docs/architecture.md` §5.1, `.github/instructions/validation.instructions.md`).
- Optionally, within that same `validation/design-review.md` cycle entry, a
  **"Foresight notes — outside this cycle's scope"** subsection — prose
  only, non-mandatory, never a `validation/open-issues.md` row
  (`.github/instructions/validation.instructions.md`).

## Verdict rule

- Final assembly acceptance requires complete, independently inspected
  evidence and source interfaces. Inspect the saved/reopened Fusion native
  storyboards and genuinely played published video when requested; only a
  named human-approved alternative changes that workflow requirement.
  Early WIP review remains permitted but cannot be promoted to final
  readiness on the strength of a clean structural checker result.
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
