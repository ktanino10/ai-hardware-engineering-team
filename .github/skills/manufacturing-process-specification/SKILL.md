---
name: manufacturing-process-specification
description: Standard procedure for specifying the additive-manufacturing (FDM/3D-printing) PROCESS parameters -- infill percentage/pattern, wall/perimeter count, print orientation relative to the part's expected load direction, and material choice -- a mechanical part needs to actually achieve the physical properties its CAD design assumes, with explicit priority on safety-critical/structural parts and honest escalation when FDM itself is not an adequate process for the claimed purpose. Use this whenever a mechanical design includes a part whose function depends on real structural/material properties once fabricated, not just CAD-geometric fit.
---

# Skill: Manufacturing Process Specification

## Purpose

Turn a CAD model's geometric claim (e.g. "this wall is 4.0mm thick, solid")
into a specified, evidence-grounded manufacturing **process** — infill
percentage/pattern, wall/perimeter count, print orientation, material —
that actually gives the fabricated part a defensible chance of having the
physical properties the geometry assumes. This is the standard operating
procedure behind `.github/agents/manufacturing-engineer.agent.md`. It runs
**after** the Mechanical Lead has produced a design (`.scad` file +
dimensional-spec table) and **before** the Mechanical Reviewer's
independent cross-check.

## The core distinction this skill exists to close

A CAD/OpenSCAD model's dimensions are **geometric** facts — they describe
the shape a slicer is told to fill. Whether the physically printed part
actually has solid material where the geometry says it should, or a sparse
internal lattice, is decided entirely by **process parameters set at
slicing time**: infill density and pattern, how many solid perimeter walls
surround that infill, which way the part sits on the build plate (and
therefore which direction its layer lines run relative to the load it will
see in service), and which filament material is loaded. None of this is
visible in, or derivable from, the CAD geometry alone. A slicer's own
default infill (commonly 15–25% for a general-purpose profile) can leave a
nominally "4.0mm solid" wall mostly air unless the process is deliberately
specified otherwise.

## When to use

Whenever the Mechanical Lead / Hardware Lead has flagged a part as
safety-critical or structural — its function depends on real
structural/material properties once fabricated, not just holding a shape or
passing a screw. Not needed for a purely cosmetic or fit-only enclosure
wall; that stays covered by the Mechanical Lead's own existing basic
print-fit/manufacturability rule (minimum wall thickness for printability,
overhang angle, bridge span).

## Inputs

- The Mechanical Lead's `.scad` file and dimensional-spec table for the part
  in question (`hardware/mechanical/`).
- The part's actual disclosed load case: what specifically must not happen
  (e.g. fragment escape, structural collapse, an uncontrolled pinch
  contact), and under what real, stated energy/force/direction — sourced
  from the design's own derivation or the governing requirement text. Never
  invent or re-derive this number yourself; if it doesn't exist, that is a
  finding (see "When FDM is not adequate" below), not something to
  reason around.
- Any human-stated constraint on material/printer (e.g. "must print on an
  already-owned PLA-only printer") — do not assume one exists if it hasn't
  been stated.

## Procedure

1. **Classify the part.** Confirm it is genuinely safety-critical/
   structural, not cosmetic/fit-only, before applying this level of rigor.
2. **Extract the actual disclosed load case** — magnitude, direction, and
   what failure would concretely look like. If no real number exists
   anywhere in the design documents, stop and record that gap explicitly
   (`UNKNOWN`, escalate per `docs/architecture.md` §10) rather than
   inventing a load case to reason against.
3. **Specify infill percentage and pattern.**
   - Higher infill increases both bulk strength and impact-energy
     absorption, with diminishing returns above roughly 50–60% — several
     independent sources converge on this range for FDM structural parts
     (e.g. *"3D Print Infill Percentage and Patterns for Maximum
     Strength,"* 3dmag.com; *"Optimizing Impact Toughness in 3D-Printed PLA
     Structures,"* MDPI *Eng* 2024, 5(1):27; *"The Influence of Printing
     Parameters on the Impact Strength of FDM 3D..."*, MDPI *Eng* 2025,
     6(1):14).
   - Pattern matters independently of density: honeycomb and triangle
     infill patterns consistently outperform simple line/grid patterns for
     impact-energy absorption in the same literature.
   - A typical general-purpose slicer default (roughly 15–25% infill) is
     **not** an adequate default for a safety-critical part — state the
     chosen percentage/pattern explicitly and why.
4. **Specify wall/perimeter (shell) count.** Multiple independent sources
   (e.g. *"How Many Walls (Perimeters) Should You Use?,"* ucuz3d.com;
   *"Optimizing 3D Printing: Shells and Infill Analysis,"* thevirtualfoundry.com)
   converge that increasing perimeter count improves strength/impact
   resistance more per gram of material than increasing infill density
   alone, because the continuous outer shell(s) carry most of the load
   directly. A commonly cited baseline for functional parts is 3–4
   perimeters; treat a safety-critical part as warranting the higher end of
   that range (or more), not the slicer default (often 2).
5. **Specify print orientation relative to the load direction.** FDM parts
   are strongly anisotropic: in-plane (XY, within a layer) tensile strength
   is commonly reported at roughly 80–100% of the base material's bulk
   strength, while across-layer (Z-axis) strength commonly drops to roughly
   60–80% or lower, because inter-layer bonds are weaker than the polymer's
   own intra-layer molecular entanglement (e.g. *"Anisotropy Explained: FDM
   3D Prints Are Weaker on the Z-Axis,"* mlc-cad.com; *"Why 3D Prints Break
   Between Layers,"* hotean.com). Identify the load's real expected
   direction from the design (e.g. a radial impact against a cylindrical
   containment wall) and specify which axis must carry that load in-plane
   rather than across layer lines — an otherwise-correct infill/wall
   specification can still fail in service if the part is printed in the
   wrong orientation, since orientation is invisible in the CAD geometry
   itself.
6. **Specify material, only where structurally relevant.** PLA has good
   layer adhesion but is brittle with poor impact toughness — cracks
   propagate along layer lines under shock. PETG offers excellent layer
   adhesion with moderate-to-good impact toughness and is a reasonable
   general-purpose upgrade for a structural part. ABS offers good impact
   toughness but is more warp-sensitive, which can itself degrade layer
   adhesion if the print environment isn't controlled. Nylon offers the
   best combination of impact toughness and layer adhesion among common FDM
   materials but is hygroscopic and harder to print reliably without
   moisture control (comparison consistent with e.g. *"In-Depth Comparison
   of Material Properties: PLA vs ABS vs PETG,"* salesplastics.com;
   *"Filament Impact Resistance: PLA vs PETG vs PC vs Nylon,"* filaments.ai-driven.ai).
   Do not name one brand as self-evidently correct — once a specific
   product is being decided, compare real candidates against their own
   manufacturer technical data sheets, the same rigor Component Selection
   already applies to electronic parts.
7. **Mark every specified value's confidence** — `CONFIRMED` (traced to a
   specific manufacturer filament technical data sheet via an Evidence ID,
   once a real product is named), `ASSUMPTION` (a stated engineering
   judgment made in the absence of a part-specific test), `ESTIMATE`
   (reasoned from general FDM literature but not validated against the
   actual part's geometry), or `UNKNOWN` — per
   `.github/instructions/mechanical-design.instructions.md`. Treat almost
   every process recommendation from this skill as `ESTIMATE`, not
   `CONFIRMED`, unless the actual fabricated part has itself been physically
   tested (see below) — literature values are characterized for standard
   test coupons (tensile/flexural bars), not the specific complex geometry
   and load case at hand.
8. **Assess and state whether FDM is adequate for the claimed purpose at
   all**, independent of which parameters were chosen — see "When FDM is
   not adequate" below.
9. **Record the specification** as its own document under
   `hardware/mechanical/` (e.g. `<board>-manufacturing-spec.md`), separate
   from the Mechanical Lead's own `.scad`/dimensional-spec files.
10. **Hand off to the Mechanical Reviewer** for the independent cross-check
    — never self-certify.

## Evidence for process claims

- A **specific filament product's own mechanical properties** (e.g. "this
  exact PETG's Izod impact rating") is a manufacturer claim like any
  component datasheet — cite it with a proper Evidence ID
  (`DS-<CATEGORY>-<NNN>`, registered in `datasheets/evidence-log.md`) once a
  real project names a specific product, reusing the existing open-ended
  category list (`docs/architecture.md` §6.3) rather than inventing a new
  citation scheme.
- **General FDM process/material science** that isn't tied to one
  manufacturer's specific product (e.g. "increasing perimeter count
  generally improves impact strength more than infill density alone," or
  "Z-axis layer adhesion is FDM's weakest load direction") is cited the same
  way any engineering claim is cited outside a component datasheet: a real,
  checkable source (title/publisher/URL), not asserted from memory. This
  skill's own Procedure section above cites the specific sources used to
  ground it — verify or refresh them rather than trusting this file at face
  value if the literature has moved on.
- **Be honest about the gap between literature and the actual part**:
  published FDM strength-vs-process data is almost always characterized on
  standard test coupons under controlled lab conditions, not on the
  specific, often more complex geometry and load case an actual mechanical
  part presents. Treat every process recommendation as reasoned-but-
  unverified for the actual part (`ESTIMATE`) unless real, physical testing
  of that exact printed part has been performed.

## Foundational Change Cascade Checklist (revising an existing process spec, not writing the first one)

Added following this project's already-documented manufacturing precedent
`MISS-021` (`validation/open-issues.md`): after the Rev 3.3 motor-voltage/RPM
correction, `bench-imu-01-manufacturing-spec.md` still cited the superseded
121.60 J / 69.74 m/s / 22,200 RPM figures in six places until a later audit
found and corrected them. This is the Manufacturing discipline's own concrete
instance of the broader snapshot-drift failure mode now documented in
`docs/workflow.md` §4.2/§4.2.1: a downstream handoff artifact stayed
internally consistent with *itself* while silently drifting out of sync with
its live upstream Source of Truth. **Whenever you are revising an existing
manufacturing/process document because a governing load-case fact changed —
energy, RPM, mass, geometry, threat path, or which surface is primary vs.
secondary — do not only patch the one sentence that first exposed the issue.
Re-verify every category below against the *current* upstream figure(s):**

1. **The load-case table and every repeated citation of it.** If the current
   process spec quotes RPM, energy, mass, tip speed, launch radius, impact
   direction, or names a specific governing requirement, grep the whole file
   and re-check every repeated occurrence — not just the first table row or
   summary paragraph. `MISS-021` exists precisely because six stale copies of
   the same superseded figures survived one upstream correction.
2. **Each process rationale keyed to the old number, not just the number
   itself.** Re-read every infill / pattern / perimeter / orientation /
   material rationale and ask: does this paragraph argue "100% infill because
   121.60 J," "upright orientation because the primary strike is radial at
   69.74 m/s," or otherwise depend on the prior magnitude or threat picture?
   A numerical edit alone is not enough if the prose still reflects the old
   severity or old failure mechanism.
3. **Geometry-sensitive manufacturing assumptions.** If the upstream change is
   geometric (for example a resize like `MISS-034`, longer unsupported spans,
   a moved wall, a different flange width, altered mass distribution, or a
   new primary load path), re-check whether wall-count, top/bottom-solid-layer
   guidance, print orientation, or material rationale still matches the *new*
   geometry rather than the shape that existed when the process spec was first
   written. Manufacturing recommendations are downstream of geometry even
   though they do not edit the geometry.
4. **Primary-vs-secondary containment/load-path claims.** If the document says
   one printed feature intercepts the hazard first and another is only backup,
   re-derive that statement from the current upstream geometry/load-case
   artifact rather than carrying it forward by habit. A geometry or threat-path
   revision can invalidate which surface is actually load-bearing first, which
   in turn changes which part most needs conservative shells/orientation.
5. **Adequacy/disclaimer sections tied to the old severity picture.** Re-check
   the "FDM adequate or not?" conclusion and the human-escalation wording
   against the new governing figures. A higher corrected hazard can make a
   formerly borderline recommendation clearly prototype-only; a lower corrected
   hazard may still not make it validated, but the prose should reflect the
   real current reason, not stale caution language copied forward.
6. **Upstream re-verification from the live Source of Truth, not from a stale
   snapshot note.** Per `docs/workflow.md` §4.2/§4.2.1, do not trust the last
   downstream document that mentioned the figures. Re-open the current source
   artifact that owns the load case (`hardware/mechanical/...-dimensional-spec.md`,
   requirement text, schematic-side correction, or equivalent) and re-copy from
   there this pass. If a figure has mixed-confidence inputs (`ASSUMPTION` /
   `ESTIMATE` / `UNKNOWN`), preserve that lineage honestly instead of upgrading
   certainty while touching the numbers.
7. **Anything deliberately left out of the re-verification pass.** If you
   conclude a foundational upstream change does *not* require reworking some
   adjacent manufacturing claim, say so explicitly in the document handoff or
   review notes with the reason ("board resize changed enclosure footprint but
   not the flywheel containment load case"). Do not leave it as a silent
   omission for a later audit to rediscover.

## When FDM is not adequate — escalate, do not rubber-stamp

Do not let a written process specification imply a safety requirement is
"solved." For a part whose claimed purpose is containment or mitigation of a
genuinely hazardous energy or force (e.g. a detached-fragment impact, a
machine-guard-class hazard):

- Industry certification practice does not treat FDM material properties as
  transferable from a generic filament data sheet to an arbitrary printed
  part — safety bodies have created FDM/additive-manufacturing-specific
  certification pathways (e.g. UL's additive-manufacturing certification
  program) precisely because the same nominal material can behave
  differently depending on printer, process, and even individual print run,
  and these pathways require physical testing of the actual
  printer+material+process combination, not a paper specification alone.
- Machine-guarding standards (e.g. ISO 12100's treatment of guards against
  ejected parts/fragments) likewise expect the guard's actual containment
  capability to be verified, typically through physical testing, not
  inferred from a material's generic published properties.
- **No tool available in this framework's environment can perform that
  physical/destructive testing** — the same tooling-honesty discipline
  already applied to CAD rendering (`docs/architecture.md` §5.3) and
  firmware compilation (`docs/architecture.md` §5.4) applies here: state
  plainly that this skill produces a specified, literature-grounded
  engineering **recommendation**, not a certified or validated containment
  rating.
- **Escalate to the human Chief Engineer explicitly**, disclosing this
  limitation in the same material presented for the decision, so the human
  approves (or rejects, or requests real testing before proceeding) with
  full awareness — this is always a Safety-critical-changes
  Human-in-the-loop gate (`docs/architecture.md` §10), never something this
  role can resolve alone. A bad-but-specified manufacturing process is not
  an improvement over an honestly-disclosed unknown; do not let this skill
  rubber-stamp a fundamentally inadequate manufacturing method just because
  a process was written down.

## Output

- `hardware/mechanical/<board>-manufacturing-spec.md` (or equivalent,
  Manufacturing-Engineer-owned document): infill %/pattern, wall/perimeter
  count, print orientation, material — each with its rationale, its
  confidence marking, and its source citation.
- An explicit statement of whether FDM is adequate for the part's claimed
  purpose at all, and any escalation that statement triggers.
- Handoff to the Mechanical Reviewer for independent cross-check.

## Common failure modes to avoid

- Specifying only infill percentage and treating the job as done — wall
  count and print orientation each independently affect whether the part
  achieves its assumed properties, and a high infill percentage does not
  compensate for a thin shell or a badly chosen orientation.
- Presenting a literature-grounded recommendation as `CONFIRMED` — it is
  `ESTIMATE` at best until the actual fabricated part has been physically
  tested, which this framework cannot do.
- Treating a written process specification as equivalent to a safety
  certification or as "solving" a safety requirement — it is an engineering
  judgment call for the human to weigh, not a substitute for real testing.
- Inventing a load case to reason against when the design documents never
  actually quantified one — record the absence honestly instead.
- Self-certifying the specification instead of routing it to the
  Mechanical Reviewer for independent cross-check.
