# Change Log — Engineering Change Orders (ECO)

Tracks what changed, why, and under whose approval, every time the design
is revised. This is what makes hardware revisions auditable after the fact —
"just editing" a schematic/PCB/BOM post-fabrication without a recorded ECO
is not acceptable practice here.

One entry per change. Design Complete requires an ECO entry for the current
revision (`docs/architecture.md` §8, condition 5).

## ECO Template

### `<ECO-XXX>` — `<short title>`

- **Date**:
- **Revision**: from `<rev>` to `<rev>`
- **Changed**: `<component / schematic / PCB / BOM — be specific>`
- **Why**: `<driving Finding ID(s) from open-issues.md, FMEA ID(s), or requirement change>`
- **Impact analysis**: `<affected subsystems; re-test needed? re-review needed?>`
- **Approved by**: `<human Chief Engineer name>` — `<date>`
- **Related IDs**: `<open-issues / FMEA / requirement / Evidence IDs>`

## Log

| ECO ID | Date | Revision (from -> to) | Changed | Why | Approved by | Related IDs |
|---|---|---|---|---|---|---|
| ECO-001 | 2026-08-30 | N/A (content-restoration event, not a design revision) | Nothing design-wise changed. `requirements/requirements.md`, `requirements/traceability-matrix.md`, `bom/component-selection.md`, `datasheets/evidence-log.md`, and 12 `datasheets/*.md` metadata records were re-written to disk verbatim from the Hardware Lead AI agent's own conversation context, after this session's worktree directory was accidentally deleted from disk during an independent audit (a human/creator-session operational error, not caused by this session). No requirement, component recommendation, or Evidence ID was altered during the rewrite. | Human-caused accidental deletion of the session worktree (confirmed independently by this session via 3 separate tool failures — bash process spawn, `view` "path does not exist", `get_changes_overview` git error — before any recovery action was taken) while the human/creator session was independently auditing the just-completed Component Selection phase (Checkpoint B). Uncommitted work at the time of deletion had never been committed to git (a process gap this ECO also serves to flag/close — see Notes). | Human Chief Engineer (via the creator/"General Chat" session), who both caused the incident and directed the recovery; restoration content independently spot-checked by the human against 5 key claims (ICM-20948 VDDIO range, ESP32-C3 I2C count, MCP1700 current limit, STM32G031K8T6 VDD AMR, BMI270 VDDIO range) prior to the incident, and the rewritten files were verified byte-count-identical to the pre-deletion versions by the Hardware Lead AI agent after rewriting. | Evidence IDs unaffected: DS-MCU-001..043, DS-IMU-001..073, DS-PWR-001..045 (all re-registered identically). Component Selection Checkpoint B approval (`bom/component-selection.md` Approval tables) unaffected — it was recorded via a tool call independent of the deleted files and remains valid. |

## Notes

- Also use this log to record the outcome of a Conflict Resolution /
  Deadlock Escalation (`docs/workflow.md` §3) whenever it changes something
  already designed.
- `docs/evaluation.md` uses ECO count per revision cycle as a "Change
  Churn" proxy for design stability/rework — keep entries granular enough
  for that to be meaningful (don't bundle unrelated changes into one ECO).
