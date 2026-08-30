---
description: 'Mechanical/enclosure artifacts require Electronics->Mechanical Interface traceability, explicit CONFIRMED/ASSUMPTION/ESTIMATE/UNKNOWN marking for every dimension, and no claimed CAD-tool capability that is not verified connected.'
applyTo: 'hardware/mechanical/**,hardware/mechanical-interface.md'
---

- Every dimension in an enclosure design must trace to a
  `hardware/mechanical-interface.md` row, an Evidence ID
  (`DS-<CATEGORY>-<NNN>`, `datasheets/evidence-log.md`) for a mechanical
  part's manufacturer spec, or be explicitly marked `ASSUMPTION`/`ESTIMATE`
  with a stated rationale — never blended silently with a `CONFIRMED` value.
- `hardware/mechanical-interface.md` uses four confidence labels, not just
  `UNKNOWN`: `CONFIRMED` (from an actual KiCad project / datasheet / measured
  value — cite the source), `ASSUMPTION` (a stated design choice made in the
  absence of confirmed data — state why), `ESTIMATE` (a reasonable
  approximation, explicitly flagged), `UNKNOWN` (not yet determined — do not
  use as if confirmed, per `docs/architecture.md` §6.1).
- Do not claim a CAD/3D modeling tool rendered, previewed, or validated a
  design unless a tool connection was actually verified in that session
  (`docs/architecture.md` §5.3/§13) — the verified default state today is "no
  CAD/3D tool connected," so the primary artifact is text/parametric (an
  OpenSCAD-syntax `.scad` file + a dimensional-spec Markdown table).
- Any non-cosmetic change under `hardware/mechanical/` or to
  `hardware/mechanical-interface.md` needs a `validation/change-log.md` (ECO)
  entry, and — since it may have cross-domain effects — a filled-in
  `validation/change-impact-matrix.md` entry (its existing "Mechanical" row)
  before human approval, same rule as `hardware/**`/`bom/**`
  (`.github/instructions/hardware-design.instructions.md`).
- Mechanical Reviewer findings are recorded in the same
  `validation/open-issues.md` backlog Hardware Reviewer uses, tagged
  `Source: mechanical-reviewer` — do not create a separate backlog file.
- Do not finalize a mechanical design past a Mechanical Reviewer verdict with
  an open CRITICAL finding — same Design Complete gate as Electronics
  (`docs/architecture.md` §8; the gate is shared, not duplicated, since both
  disciplines' findings live in one `validation/open-issues.md`).
- A basic, explicitly stated print-fit clearance allowance and
  manufacturability rule set (minimum wall thickness, overhang angle, bridge
  span) is required for Phase 1; a full statistical tolerance stack-up
  analysis is deliberately out of scope until a real project needs it
  (`docs/architecture-evolution.md` §10/§13).
