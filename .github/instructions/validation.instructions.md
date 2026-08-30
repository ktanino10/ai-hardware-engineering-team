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
  `rubber-duck`, or `human` — never merge a `rubber-duck` premise-review
  finding into a `hardware-reviewer` checklist finding or vice versa
  (`docs/architecture.md` §5.1).
- `validation/fmea.md` uses a different scoring scale (RPN =
  Severity×Occurrence×Detection, 1–10 each) than Reviewer findings — do not
  reuse CRITICAL/HIGH/MEDIUM/LOW there.
- Do not report or imply "Design Complete" unless all five conditions in
  `docs/architecture.md` §8 hold.
