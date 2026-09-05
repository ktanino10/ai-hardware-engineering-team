---
description: 'Independent review and issue-tracking artifacts must follow the finding schema, severity taxonomy, and Design Complete gating rules.'
applyTo: 'validation/**'
---

- Every finding (in `validation/design-review.md` and
  `validation/open-issues.md`) must include: Issue, Rationale, Datasheet
  Source (Evidence ID), Failure Mechanism, Affected Component, Recommended
  Fix, Severity. Do not add a finding missing any of these fields.
- Severity is one of CRITICAL / HIGH / MEDIUM / LOW, per the definitions in
  `docs/architecture.md` §7.1 — do not invent other severity labels.
- **CRITICAL findings can only reach `RESOLVED`** — never mark a CRITICAL
  finding `ACCEPTED-RISK`, regardless of schedule pressure.
- **HIGH findings** may become `ACCEPTED-RISK` only with a named human
  Chief Engineer sign-off, written rationale, and date.
- Keep `validation/open-issues.md`'s table header and column order exactly
  as documented in that file — `tools/check_open_issues.py` /
  `.github/workflows/hardware-gate.yml` parse it as a Markdown table, and a
  changed header will break the CI gate silently.
- `Source` column in `open-issues.md` must be one of `hardware-reviewer`,
  `mechanical-reviewer`, `rubber-duck`, or `human` — never merge a
  `rubber-duck` premise-review finding into a `hardware-reviewer`/
  `mechanical-reviewer` checklist finding or vice versa, and never merge
  `hardware-reviewer` and `mechanical-reviewer` findings into each other
  either (`docs/architecture.md` §5.1, extended to a third lens for the
  Mechanical discipline — `docs/architecture-evolution.md` §31).
- `validation/fmea.md` uses a different scoring scale (RPN =
  Severity×Occurrence×Detection, 1–10 each) than Reviewer findings — do not
  reuse CRITICAL/HIGH/MEDIUM/LOW there.
- A Reviewer's per-cycle report (`validation/design-review.md`, or
  Firmware's own `firmware/<board>/<board>-firmware-review.md`) may
  optionally include a non-mandatory, prose-only "Foresight notes —
  outside this cycle's scope" subsection for things noticed but not yet a
  concrete finding (`docs/architecture-evolution.md` §38). This is
  **outside** the required finding schema above and must **never** be
  turned into a `validation/open-issues.md` row or column — promote it to
  a real finding (full Issue/Rationale/Datasheet Source/Failure
  Mechanism/Affected Component/Recommended Fix/Severity) first if it
  becomes concrete enough to act on.
- Do not report or imply "Design Complete" unless all five conditions in
  `docs/architecture.md` §8 hold.
- Assembly reviews follow `docs/assembly-evidence.md`: explicitly distinguish
  an early WIP blocker review (allowed with incomplete evidence) from final
  evidence acceptance. Record the source revision and reviewed artifact
  hashes, full installed/per-stage coverage, unknowns and method limits.
  A successful structural validator, scalar sync or animation export is not
  independent geometry/safety acceptance.
- APPROVED assembly documentation requires the exact package's independent
  review, Design Complete and named safety-decision references. Preserve
  physical-action stop gates and existing risk dispositions; the requested
  Fusion native/video deliverables remain incomplete until genuinely
  delivered or an explicit human-approved alternative is recorded.
