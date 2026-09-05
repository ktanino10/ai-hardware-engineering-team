---
description: 'Mechanical/assembly artifacts require source-linked WIP versus approved evidence, full installed/per-stage coverage, requested Fusion native/video delivery, dimension confidence labels and runtime tooling honesty.'
applyTo: 'hardware/mechanical/**,hardware/mechanical-interface.md,visualization/assembly-viewer/**'
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
  (`docs/architecture.md` §5.3). Verify model authoring, Animation authoring,
  native save/reopen and video export separately; no historical "no CAD"
  claim is a permanent instruction. Unavailable execution permits source/
  planning output with a precise blocker, not a delivered-animation claim.
- Follow `docs/assembly-evidence.md`: generate **WIP - NOT ASSEMBLY READY**
  assembly planning/animation and installed/per-stage evidence during
  design; release **APPROVED** documentation only after independent evidence
  acceptance, Design Complete and named safety decisions. Incomplete WIP
  evidence allows early blocker review, never final readiness.
- Maintain the current revision manifest with source commit, hashes,
  artifact status, owner and next action, selected by the assembly's
  `current.json` pointer. Referenced report/source changes also invalidate
  the current package; preserve historical manifests unchanged.
  Include populated/mated PCBs,
  actual mounting/insulation, all required sensors/boards/drivers/power,
  motors/hubs/swept envelopes, fasteners, retained harnesses and actual
  insertion/seating/removal/tool access. Scalar sync, a bare board or an
  attractive export is insufficient.
- Fusion Animation is the standard for applicable multi-part assemblies;
  an explicit request requires genuine native storyboards and published
  playable video, or a named human-approved alternative. Never relabel
  another renderer's output. Experimental/unverified `fusion_*` MCP tools
  are not a production path; public API support must be assessed per
  operation, not inferred from a missing tool or search result.
- A visualization pass cannot silently redesign geometry or move an
  installed pose to hide a gap. Route source correction through its owner.
  Distinguish intentional fused-print/contact/process fits from forbidden
  overlap; disclose sampled-path limits. Animation is not collision,
  support-removal, strength, safety or functionality proof.
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
