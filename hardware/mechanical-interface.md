# Electronics → Mechanical Interface

The physical/geometric contract the Electronics side hands to the Mechanical
Lead — the minimum field set needed for Phase 1
(`docs/architecture-evolution.md` §13), reusing the existing `Parameter |
Value | Unit | Source` table convention (`datasheets/README.md`,
`hardware/power-budget.md`) plus explicit `Confidence` and
`Assumption / Notes` columns, since not every mechanical fact is either a
confirmed number or a flat `UNKNOWN` the way most Electronics facts are.

**Status: template only.** No real project has been run through this
repository's design cycle yet (`requirements/requirements.md` and
`bom/component-selection.md` are still blank templates), so there is no live
data to fill in here yet — this file defines the contract's shape for the
first project that does.

## Who fills this in

Per `.github/agents/mechanical-lead.agent.md`, the **Mechanical Lead** is
responsible for populating this file — extracting from an existing KiCad
project via the same read-only tools already documented in
`docs/architecture.md` §5.2 (`get_project_structure`,
`extract_project_netlist`, `analyze_bom`,
`generate_pcb_thumbnail`/`generate_project_thumbnail`), or from
Circuit-Engineer-/human-supplied facts if no KiCad project exists yet. This
requires no change to the Circuit Engineer's own files or process.

## Confidence / Assumption legend

Use exactly one of these per row's `Confidence` column:

| Label | Meaning |
|---|---|
| `CONFIRMED` | From an actual KiCad project / manufacturer spec / measured value. `Source` cites the Evidence ID or the specific tool output used. |
| `ASSUMPTION` | A stated design assumption made in the absence of confirmed data. `Assumption / Notes` must say why. |
| `ESTIMATE` | A reasonable approximation (e.g. "typical PCB thickness 1.6 mm"), explicitly flagged as such. |
| `UNKNOWN` | Not yet determined. Must **not** be used as if confirmed (`docs/architecture.md` §6.1) — escalate before the Mechanical Lead relies on it for a load-bearing dimension (e.g. a mounting hole position). |

## Board Geometry

| Parameter | Value | Unit | Source | Confidence | Assumption / Notes |
|---|---|---|---|---|---|
| PCB Length | | mm | | | |
| PCB Width | | mm | | | |
| PCB Thickness | | mm | | | |
| Board Outline | `<bounding box acceptable for v1 — attach coordinates or a sketch reference if available>` | | | | |

## Mounting

| Hole ID | X | Y | Diameter | Unit | Source | Confidence | Notes |
|---|---|---|---|---|---|---|---|
| MH-1 | | | | mm | | | |

## Component Height Clearance

| Parameter | Value | Unit | Source | Confidence | Notes |
|---|---|---|---|---|---|
| Max component height (top side) | | mm | | | |
| Max component height (bottom side) | | mm | | | |

## Connectors, Switches & LEDs (cutouts)

| Item | Type | X | Y | Orientation | Cutout needed? | Source | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|
| | `<connector / switch / LED>` | | | | `<Y/N>` | | | |

## Mass

| Parameter | Value | Unit | Source | Confidence | Notes |
|---|---|---|---|---|---|
| Approximate PCB + components mass | | g | | | |

## Deferred fields (not in Phase 1 — add only if a real project needs one)

Per `docs/architecture-evolution.md` §13, explicitly deferred until the
benchmark shows they're actually needed: thermal zones, antenna keep-out,
STEP/neutral 3D model reference, center of mass, battery wiring requirements,
complex keep-out zones, detailed cable-exit geometry.

## Handoff & change control

- **Produced by**: Mechanical Lead (see "Who fills this in" above).
- **Consumed by**: Mechanical Lead itself
  (`.github/skills/enclosure-design/SKILL.md`), and the Mechanical Reviewer
  for independent cross-checking (`.github/skills/mechanical-review/SKILL.md`).
- If a value here changes after Mechanical Design has started (e.g. the
  Circuit Engineer moves a connector), log it in `validation/change-log.md`
  (ECO) and check `validation/change-impact-matrix.md`'s existing
  "Mechanical" impact row — the Mechanical Design phase
  (`docs/workflow.md` Phase 9) may need to be revisited.
- Governed by `.github/instructions/mechanical-design.instructions.md`.
