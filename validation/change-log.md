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
| ECO-002 | 2026-08-31 | N/A (conflict-mediation/evidence-correction event, not yet a circuit-design revision — the actual circuit rework this triggers is tracked as its own future ECO once the Circuit Engineer completes it) | Corrected the evidence record following a genuine factual disagreement between the parallel Hardware Reviewer and rubber-duck Independent Review passes on `hardware/schematic/bench-imu-01-design.md`. Corrected: (1) `validation/open-issues.md` ISS-003 — reclassified RESOLVED, the Hardware Reviewer's own θJA package-confusion claim was itself wrong (confused TI's DQN/X2SON-4 231.1°C/W row with the design's actual DBV/SOT-23-5 60.3°C/W row in the same datasheet table); original design was correct, no design change needed. (2) `validation/open-issues.md` ISS-006 — confirmed but root cause corrected: BOOT0 is muxed onto PA14 (already committed to SWCLK), not PB8 as both the design document and the Hardware Reviewer's citation trail assumed; PB8 does exist on the package (contra the design document's DS-MCU-046) but is unrelated to BOOT0. (3) Added `validation/open-issues.md` ISS-011 (new, HIGH) — confirmed via independent research that MCU pins PB10/PB11, labeled "I2C1" throughout the design document, actually map to the STM32G031K8T6's I2C2 alternate function, not I2C1 — a genuine defect the Hardware Reviewer's own checklist pass did not catch, first surfaced by the parallel rubber-duck pass. `datasheets/evidence-log.md` DS-MCU-050 through DS-MCU-053 added to carry the corrected facts; DS-MCU-045/046 annotated (not silently overwritten) with correction pointers. | Two independent Independent-Review passes (Hardware Reviewer checklist + rubber-duck premise review), run in parallel per `docs/architecture.md` §5.1, produced conflicting factual claims about the same MCU's pin/peripheral mapping and package thermal data. Per `docs/workflow.md` §3 (Conflict Resolution / Deadlock Escalation Protocol), the Hardware Lead did not simply defer to either side — it independently re-verified every disputed claim via real-time web research against primary/authoritative sources (TI's own datasheet thermal table, ST's own reference-manual/pinout/AF-table data) before recording an outcome. | Hardware Lead (AI agent), acting as mediator per its designated role in `docs/workflow.md` §3 — not a human-approval item itself (no requirement/component/design decision changed by this ECO; it corrects the evidence trail feeding the next Circuit Engineer rework cycle, which will carry its own ECO and its own approval record). | `validation/open-issues.md` ISS-003, ISS-006, ISS-011; `datasheets/evidence-log.md` DS-MCU-045, DS-MCU-046, DS-MCU-050, DS-MCU-051, DS-MCU-052, DS-MCU-053; `validation/design-review.md` addendum. |

## Notes

- Also use this log to record the outcome of a Conflict Resolution /
  Deadlock Escalation (`docs/workflow.md` §3) whenever it changes something
  already designed.
- `docs/evaluation.md` uses ECO count per revision cycle as a "Change
  Churn" proxy for design stability/rework — keep entries granular enough
  for that to be meaningful (don't bundle unrelated changes into one ECO).
