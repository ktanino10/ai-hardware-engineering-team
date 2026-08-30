# Requirements Traceability Matrix (RTM)

Connects Requirements -> Component -> Circuit -> Test on a single line, so
coverage can be checked at a glance. Initialized by
`.github/skills/requirements-engineering/SKILL.md` (Status starts `Pending` for every
row); updated as Component Selection, Circuit Design, and Validation
progress.

Design Complete requires 100% `Verified` (or an explicit human `Waived`
disposition) — `docs/architecture.md` §8.

| Requirement ID | Requirement (short) | Satisfied by (component) | Circuit/schematic ref | Verification method | Status | Related IDs |
|---|---|---|---|---|---|---|
| REQ-001 | IMU accel+gyro @ >=100 Hz ODR | TBD — IMU (Component Selection) | TBD — sensor interface block | Datasheet ODR spec check; bench measurement (future physical bring-up) | Pending | |
| REQ-002 | MCU debug/programming interface present | TBD — MCU (Component Selection) | TBD — debug header block | Schematic inspection: header wired per MCU datasheet | Pending | |
| REQ-003 | Status/heartbeat LED | TBD | TBD — indicator block | Schematic inspection | Pending | |
| REQ-004 | Manual MCU reset button | TBD | TBD — reset block | Schematic inspection | Pending | |
| REQ-005 | No onboard data logging/storage (Won't) | N/A | N/A | N/A — explicitly out of scope this cycle | Pending | |
| REQ-006 | No wireless functionality enabled (Won't) | N/A | N/A | Schematic inspection — confirm no radio circuitry populated even if MCU silicon has it | Pending | |
| REQ-101 | USB 5 V input, 4.75-5.25 V tolerance | TBD — connector + protection (Circuit Design) | TBD — power input block | Datasheet check (protection/regulator input range); bench measurement (future) | Pending | |
| REQ-102 | Single 3.3 V logic rail | TBD — regulator (Component Selection) | TBD — power block | Schematic inspection; bench measurement (future) | Pending | |
| REQ-103 | System budget <= 300 mA @ 3.3 V | TBD | TBD — power block | `hardware/power-budget.md` arithmetic; bench measurement (future) | Pending | |
| REQ-104 | IMU digital interface: I2C or SPI | TBD — IMU + MCU pairing | TBD — sensor interface block | Schematic inspection | Pending | |
| REQ-105 | USB carries power only, no data | TBD — connector | TBD — power input block | Schematic inspection — confirm D+/D- not routed to MCU data pins | Pending | |
| REQ-106 | 4-pin UART header (TX/RX/GND/3V3) | TBD | TBD — comms header block | Schematic inspection | Pending | |
| REQ-107 | MCU-family debug header | TBD | TBD — debug header block | Schematic inspection | Pending | |
| REQ-201 | Ambient 0-40 degC, indoor desk/lab | TBD — all parts | N/A | Datasheet Recommended Operating Condition cross-check, all parts | Pending | |
| REQ-202 | Vibration/shock qualification (Won't / N/A) | N/A | N/A | N/A — no rotating body this benchmark | Pending | |
| REQ-203 | ESD precautions during handling | N/A (process) | N/A | `validation/bring-up-procedure.md` checklist | Pending | |
| REQ-301 | Single 2-layer PCB, no daughtercards | TBD | TBD — board outline | Schematic/board-outline inspection | Pending | |
| REQ-302 | PCB footprint <= 60 x 40 mm | TBD | TBD — board outline | `hardware/mechanical-interface.md` board geometry check | Pending | |
| REQ-303 | Connectors/headers on <= 2 board edges | TBD | TBD — board outline | `hardware/mechanical-interface.md` connector location check | Pending | |
| REQ-304 | >= 4 mounting holes, M2/M2.5 | TBD | TBD — board outline | `hardware/mechanical-interface.md` mounting table check | Pending | |
| REQ-305 | 2-piece, 3D-printable enclosure | TBD — Mechanical Lead | N/A | `hardware/mechanical/` design artifact inspection | Pending | |
| REQ-401 | No regulatory certification target (Won't) | N/A | N/A | N/A — explicitly out of scope this iteration | Pending | |
| REQ-402 | USB ESD / reverse-polarity protection | TBD | TBD — power input block | Schematic inspection + Evidence ID citation | Pending | |
| REQ-501 | BOM cost target <= ~$15 USD | TBD | N/A | `bom/component-selection.md` price rollup | Pending | |
| REQ-502 | Schedule target (Won't / N/A) | N/A | N/A | N/A — paper/document design exercise this cycle | Pending | |

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
