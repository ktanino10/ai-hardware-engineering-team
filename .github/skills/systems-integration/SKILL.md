---
name: systems-integration
description: Standard procedure for resolving a genuine cross-discipline engineering trade-off (Electrical vs. Mechanical vs. Firmware) using verified-constraint-vs-assumption, change cost/risk, validated-work preservation, and ripple-effect criteria, plus the methodology for proactively auditing cross-discipline interface contracts for drift. Use this whenever Hardware Lead's conflict mediation identifies a substantive technical trade-off between disciplines, or when auditing an interface-contract file (e.g. hardware/mechanical-interface.md) against its live upstream Source of Truth.
---

# Skill: Systems Integration

## Purpose

Turn "two disciplines each have a defensible position and disagree about
which one changes" into a reasoned, evidence-grounded recommendation — the
standard operating procedure behind
`.github/agents/systems-engineer.agent.md`. This is the technical-criteria
layer `docs/workflow.md` §3 (Conflict Resolution / Deadlock Escalation
Protocol) routes into once its own mediation step has confirmed a
disagreement is a genuine cross-discipline engineering trade-off, not a
communication misunderstanding or a missing-evidence gap that mediation alone
already resolves.

This skill also covers the companion activity of proactively auditing an
existing cross-discipline interface contract (e.g.
`hardware/mechanical-interface.md`) for drift against its own upstream Source
of Truth — the failure mode this role exists because of (see Worked example
below) is not "the two sides disagreed openly," it is "the two sides silently
stopped agreeing and nobody noticed."

## When to use

1. **Trade-off resolution**: Hardware Lead's mediation
   (`docs/workflow.md` §3 step 2) has determined a disagreement between two
   discipline leads is a genuine engineering trade-off — each side rests on
   something real, and resolving it means one side's artifact must actually
   change — not a case where one side is simply missing evidence the other
   already has.
2. **Interface-contract audit**: periodically, or triggered by a relevant
   upstream change (a PCB re-layout, a schematic pin reassignment, a firmware
   register-map change), verify that a snapshot interface-contract file still
   matches the live upstream fact it was populated from.

Not needed for: a disagreement mediation alone resolves (e.g. one side simply
hadn't seen the other's evidence yet); a finding about a single discipline's
own internal design quality (that's Hardware/Mechanical/Firmware Reviewer's
job, not a cross-discipline boundary question).

## The four trade-off criteria

Apply in this order — do not skip to "which is cheaper to change" before
checking which side is actually real:

1. **Verified constraint vs. unvalidated assumption.** Which side rests on a
   real, independently confirmed physical/electrical fact (a fabricated PCB's
   actual `Edge.Cuts` outline, a datasheet Absolute Maximum Rating, a
   measured dimension) versus a soft assumption, a convenience default, or a
   proposal that was never actually validated against the thing it's
   supposed to match? The side resting on the unvalidated assumption is the
   one that should generally yield — not because it is "wrong" in some moral
   sense, but because it was never actually anchored to reality in the first
   place.
2. **Cost and risk of changing each side.** Not just engineering effort —
   what has already been independently reviewed, validated, or fabricated on
   each side, and how much of that would be invalidated by each possible
   resolution? A side that is still paper/parametric-only carries a very
   different change cost than a side that has already been fabricated and
   independently reviewed.
3. **Preserve already-validated work where possible.** Between resolutions
   that are otherwise comparable on criteria 1–2, prefer the one that
   revalidates the smallest amount of previously-signed-off design — a
   corollary of criterion 2, stated as its own explicit step because it is
   easy to under-weight "how much re-review this triggers" against a purely
   dimensional/cost comparison.
4. **Explicitly surface ripple effects before deciding, not after.** A change
   on one side (enlarging an enclosure, moving a connector, reassigning a
   pin) can silently invalidate downstream claims that were correct under the
   old configuration — a previously accepted hazard-radius calculation, an
   envelope reading, a firmware assumption about a register's reset value.
   List what else the candidate resolution touches as part of the
   recommendation itself, not as a surprise discovered later. This is the
   single most commonly skipped step — see the Worked example below for what
   it costs to skip it even when the rest of the analysis is sound.

**If the trade-off is still contested after applying all four** — genuinely
comparable cost/risk on both sides, or the decision is safety-relevant or
architecture-level regardless of how clearly the criteria resolve — escalate
to the human Chief Engineer via Hardware Lead per
`docs/architecture.md` §10. This role recommends; it does not have final
authority on anything safety-relevant or architecture-level, no matter how
one-sided the technical analysis looks.

## Worked example: MISS-034 (CRITICAL, `validation/open-issues.md`)

**The conflict, as it would have looked routed through this skill (it wasn't
— no Systems Engineer role existed yet; this is the retrospective case study
that motivated creating one):**

- **Mechanical Lead's artifact**: `hardware/mechanical/bench-imu-01-enclosure.scad`
  and `hardware/mechanical-interface.md` A1/A2, both recording a 100×50mm
  board (`pcb_length`/`pcb_width`), populated `2026-08-31` (commit `350ac36`)
  from what was, at that time, a genuine proposal.
- **Electronics' artifact**: the real PCB, laid out `2026-09-02` (commit
  `a454b0c`) at 150×95mm — a legitimate Electronics-side change, sized from
  real footprint/courtyard area under REQ-308's relaxed ceiling.
- **The conflict**: the board (150mm) is longer in X than the *entire* base
  assembly (123mm) the enclosure provides — physically impossible to
  assemble. Someone has to change: either the enclosure grows to fit the real
  board, or the board shrinks back toward the enclosure's assumption.

**Applying the criteria:**

1. **Verified constraint vs. assumption**: the PCB's 150×95mm was
   independently cross-checked three ways — the real KiCad project's own
   `Edge.Cuts` layer, `generate_pcb.py`'s `BOARD_W`/`BOARD_H` constants, and
   `hardware/pcb/README.md`'s own stated outline — a verified, fabricated
   constraint. The enclosure's 100×50mm was a `350ac36`-era proposal that
   predated the real layout and was never re-confirmed against it. Criterion
   1 alone already points to Mechanical yielding.
2. **Cost/risk of changing each side**: the PCB was a real, laid-out, DRC-
   relevant KiCad project — re-shrinking it would invalidate real routing/
   placement work. The enclosure was still `.scad`/STL-only, not yet
   fabricated — its own governing instructions
   (`docs/architecture.md` §10) require human sign-off before mechanical
   fabrication, so nothing physical had been committed to the old dimensions
   yet. Changing the enclosure is strictly cheaper and lower-risk than
   changing the board.
3. **Preserve validated work**: growing the enclosure preserves 100% of the
   Electronics-side work (the real board); shrinking the board would have
   discarded real, already-reviewed layout work to match a proposal that was
   never itself verified. Criterion 3 agrees with criteria 1–2.
4. **Ripple effects — surfaced, not discovered later**: growing the enclosure
   to 150×95mm was not dimensionally free. The actual, dated record shows two
   real ripple effects that *did* surface, both correctly caught by the
   Foresight-checklist discipline this same review cycle already carries,
   not by this skill (which did not yet exist):
   - **MISS-023 (HIGH) re-opened** from a prior human `ACCEPTED-RISK`: that
     sign-off had been reasoned against a 126.424mm hazard-band radius and
     77.7% pinch-guard coverage computed for the *old* geometry, which the
     rescale invalidated. Carrying the old acceptance forward silently would
     have been the real defect.
   - **MISS-047 (MEDIUM, resolved)**: the assembled-envelope calculation had
     never included the pinch-guard's own footprint at all, a pre-existing
     gap that only became visually obvious once the resize made the guard
     dominate the envelope reading.
   Had this skill's criterion 4 been applied *before* finalizing the resize —
   rather than these two being found afterward by separate, later review
   passes — both would have been anticipated as explicit "what this also
   touches" items in the original recommendation, which is exactly the
   discipline this criterion exists to force.

**The actual resolution, and why the human still decided it**: even with the
technical picture this clear, `validation/open-issues.md`'s own MISS-034 entry
is explicit that "which side moves ... is a Chief-Engineer-level
architecture/scope decision, explicitly reserved per `docs/architecture.md`
§10, not a reviewer's call and not an autonomous-loop call" — and growing a
mechanical enclosure is independently a "before mechanical fabrication" HITL
gate item regardless. Kyosuke's decision was to grow the enclosure, not the
PCB — the same conclusion criteria 1–3 above reach. **The value this skill
adds is not overriding that human authority; it is making sure the decision
brief that reaches the human is already this well-reasoned**, with the
ripple effects named up front rather than discovered one Mechanical Reviewer
cycle at a time.

**Still open, a live pointer for future use of this skill**: MISS-037
(MEDIUM, OPEN) — connector/component cutout positions (J1–J4/SW1/D1) were
carried forward from the same superseded board-local layout scheme and have
still never been independently re-verified against the real PCB's own
placement. A future Systems Engineer interface-drift audit (below) is a
natural way to close this, rather than waiting for another unrelated task to
stumble into it the way MISS-034 itself was found.

## Interface-drift-detection methodology

`docs/workflow.md` §4.2.1 ("Cross-Discipline Handoff Snapshot Drift") already
names the general shape of this problem: a snapshot handoff file is populated
once from an upstream Source of Truth that can keep changing after the
snapshot is taken, and §4.2's own general remedy (grep for an old value's
numeric string) is reactive and only fires once someone happens to notice.
Where the upstream Source of Truth is itself machine-readable, that same
section already prescribes the narrower, exact-comparison alternative:
`tools/check_mechanical_pcb_sync.py` is the one working, CI-wired instance of
this today (`.github/workflows/mechanical-pcb-sync-check.yml`, currently
**advisory**, not a required status check, by its own explicit documented
choice — "revisit if this class of drift recurs").

**This skill does not re-author that mechanism, or duplicate the
"Foundational Change Cascade Checklist" content already present in
`power-architecture`, `mechanical-review`, `enclosure-design`, `pcb-layout`,
`firmware-bringup`, `firmware-review`, `schematic-design`,
`component-selection`, and `manufacturing-process-specification`'s own SKILL
files.** Those stay exactly where they are — each discipline's own periodic
audit question ("does a machine-readable upstream Source of Truth exist for a
fact I snapshot, and is there a check that it still matches?") is that
discipline's own job to keep asking, per `docs/workflow.md` §4.2.1's own
closing paragraph. This role's distinct job is:

1. **Notice when a cross-discipline boundary has no such mechanism at all**,
   not just whether an existing one still runs correctly. MISS-037 (still
   OPEN) is a live example: `check_mechanical_pcb_sync.py` deliberately does
   not cover connector/component cutout positions (out of its own stated
   narrow scope), so that boundary currently has zero automated protection.
2. **Periodically re-derive the facts an interface-contract file records
   directly from the live upstream source**, for facts no automated check
   yet covers — read the real KiCad project / schematic yourself rather than
   trusting the snapshot, exactly as Mechanical Reviewer's own "Foundational
   Change Cascade Checklist" item 1 already requires of itself when reviewing
   a resize.
3. **Make the informed call on scope/required-status changes** to an
   existing mechanism — e.g. whether repeated drift incidents justify
   promoting `mechanical-pcb-sync-check.yml` from advisory to required, or
   whether a new sibling check is warranted for a boundary like MISS-037's —
   and recommend it to Hardware Lead. Do not build new CI machinery
   speculatively ahead of a demonstrated need (mirrors this project's own
   standing caution against over-engineering ahead of actual demonstrated
   necessity, `docs/architecture.md` §14 / `docs/architecture-evolution.md`
   §42's own "premature to build new CI machinery for a problem about to
   resolve itself" reasoning).
4. **Report a real drift finding through the existing channel for that
   boundary** — the discipline's own Reviewer (e.g. `mechanical-reviewer` for
   an Electronics⇔Mechanical finding, matching MISS-034's own actual `Source`
   tag) — rather than inventing a new `validation/open-issues.md` `Source`
   value.

## Output

This role has no dedicated tracking file of its own. Its work lands in the
same places every other mediated cross-discipline outcome in this project
already does:

- **`validation/change-log.md`** (ECO) — when a trade-off recommendation
  results in a change to something already designed.
- **`validation/open-issues.md`** — when an interface-drift audit surfaces a
  real finding, logged through the existing discipline Reviewer's own
  `Source` tag, or when a recommendation resolves/reclassifies an existing
  finding (mirrors `docs/architecture.md` §9's existing rule for recording
  conflict-resolution outcomes generally).
- A short decision brief to the human Chief Engineer (via Hardware Lead) —
  positions, criteria applied, recommendation — whenever the trade-off is
  still contested or is itself safety-relevant/architecture-level.

## Common failure modes to avoid

- Treating "the criteria clearly favor one side" as license to finalize a
  safety-relevant or architecture-level decision yourself — MISS-034's own
  actual resolution shows the technical picture being completely clear did
  not change who was authorized to decide.
- Applying criterion 2 (cost/risk) before criterion 1 (verified vs.
  assumption) — a side can be cheap to change and still be the *correct*
  side, if the other side is the one resting on an unverified assumption;
  don't let "cheaper" substitute for "more correct."
- Listing ripple effects as a caveat after recommending a resolution, instead
  of as part of deciding between resolutions in the first place — criterion
  4 exists specifically because MISS-023/MISS-047 show what happens when
  ripple effects are found after the fact instead of before.
- Duplicating a discipline's own "Foundational Change Cascade Checklist"
  content instead of pointing to it — this skill's interface-drift section
  is about noticing gaps between disciplines' own mechanisms, not replacing
  what already exists inside each one.
- Inventing a new `validation/open-issues.md` `Source` tag for a finding this
  role surfaces — route it through the existing Reviewer for that boundary
  instead.
