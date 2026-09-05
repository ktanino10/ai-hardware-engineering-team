---
description: 'Schematic, PCB, and BOM artifacts require evidence citations, Source-of-Truth precedence, and no guessed values.'
applyTo: 'hardware/**,bom/**'
---

- Every numeric design choice tied to a component (voltage, current,
  decoupling value, pull-up/down value, timing margin, etc.) must cite an
  Evidence ID (`DS-<CATEGORY>-<NNN>`) registered in
  `datasheets/evidence-log.md` — not a bare claim.
- Explicitly distinguish Absolute Maximum Ratings, Recommended Operating
  Conditions, and Typical Characteristics when citing a value — never blend
  them.
- Unconfirmed values are `UNKNOWN`, never a guess or an inference from a
  similar part.
- Do not finalize a schematic/PCB/BOM change past a Hardware Reviewer
  verdict with an open CRITICAL finding (`validation/open-issues.md`) —
  see the Design Complete gate, `docs/architecture.md` §8.
- Any non-cosmetic change to `hardware/**` or `bom/**` needs a
  `validation/change-log.md` (ECO) entry, and — if it has cross-domain
  effects (power/thermal/EMI/timing/mechanical) — a filled-in
  `validation/change-impact-matrix.md` entry before human approval.
- Keep `hardware/power-budget.md` current whenever a subsystem's
  current/power draw changes.
- For integrated assembly changes, provide the actual populated/mated
  PCB/module envelopes, mounts, connector/power interfaces and source
  references to Mechanical Lead via Hardware Lead. Sourceable gaps require
  investigation or a concrete alternative, not indefinite human approval.
  Link changed inputs/artifacts in the revision manifest described by
  `docs/assembly-evidence.md`; WIP evidence is allowed before Design
  Complete but does not authorize final readiness or physical operations.
- Deviating from a datasheet's Recommended Application Circuit is allowed
  but must be justified and cited, not silent.
