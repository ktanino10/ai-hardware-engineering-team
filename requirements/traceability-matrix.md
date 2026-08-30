# Requirements Traceability Matrix (RTM)

Connects Requirements -> Component -> Circuit -> Test on a single line, so
coverage can be checked at a glance. Initialized by
`skills/requirements-engineering/SKILL.md` (Status starts `Pending` for every
row); updated as Component Selection, Circuit Design, and Validation
progress.

Design Complete requires 100% `Verified` (or an explicit human `Waived`
disposition) — `docs/architecture.md` §8.

| Requirement ID | Requirement (short) | Satisfied by (component) | Circuit/schematic ref | Verification method | Status | Related IDs |
|---|---|---|---|---|---|---|
| REQ-001 | `<short description>` | `<part / bom/component-selection.md row>` | `<schematic block / sheet ref>` | `<test/measurement method>` | Pending | `<Evidence IDs / open-issues IDs / FMEA IDs>` |

## Status values

- `Pending` — not yet designed/tested against.
- `Verified` — confirmed by the stated verification method, with evidence
  (bench measurement, DRC pass, etc.) recorded.
- `Failed` — verification attempted and failed; must reopen the
  corresponding Circuit Design phase (`docs/workflow.md` Phase 4).
- `Waived` — human Chief Engineer explicitly accepted not verifying this
  requirement for this revision, with written rationale (record who/when/why
  in the Related IDs column or `validation/change-log.md`).

## Notes

- Add a row per requirement ID from `requirements/requirements.md`, even if
  several requirements map to the same component/circuit block.
- `Related IDs` is where this matrix connects to `datasheets/evidence-log.md`
  (Evidence IDs), `validation/open-issues.md` (finding IDs), and
  `validation/fmea.md` (FMEA IDs) — keep it populated so a reviewer can
  actually follow the chain instead of just trusting the Status column.
