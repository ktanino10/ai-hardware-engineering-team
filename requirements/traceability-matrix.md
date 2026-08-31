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
| REQ-001 | IMU accel+gyro @ >=100 Hz ODR | U2 BMI270 | `bench-imu-01-design.md` §5.1 (I2C bus-timing budget) | Datasheet max-ODR spec check (1600 Hz accel / 6400 Hz gyro, 16-64x the floor) + I2C Fast-mode bus-timing arithmetic (≈0.3-0.4ms read vs. 10ms period at 100Hz, >95% margin) | Verified | DS-IMU-009, DS-IFACE-001. Hardware capability only — actual running-firmware ODR measurement is a physical-bring-up activity, out of scope this cycle (REQ-502) |
| REQ-002 | MCU debug/programming interface present | U1 STM32G031K8T6 + J3 header | `bench-imu-01-design.md` §4.4 | Schematic inspection: 4-pin SWD header wired per ST's own minimal debug-header reference (NUCLEO-G031K8 CN4) | Verified | DS-CONN-002, same evidence satisfies REQ-107 |
| REQ-003 | Status/heartbeat LED | D1 + R5 (330Ω) | `bench-imu-01-design.md` §7, parts list | Schematic inspection: GPIO -> current-limit resistor -> LED, standard topology | Verified | — |
| REQ-004 | Manual MCU reset button | SW1 | `bench-imu-01-design.md` §4.3, parts list | Schematic inspection: N.O. pushbutton wired to NRST per ST's recommended NRST filter circuit | Verified | DS-MCU-046 (NRST recommended circuit, AN5096) |
| REQ-005 | No onboard data logging/storage (Won't) | N/A | Parts list (`bench-imu-01-design.md` §10) | Direct parts-list inspection: no SD-card/external-flash/EEPROM storage IC appears anywhere in U1-U4/J1-J3/SW1/D1/passives | Verified — confirmed not implemented (real, checkable fact; not merely un-designed) | — |
| REQ-006 | No wireless functionality enabled (Won't) | N/A | Parts list (`bench-imu-01-design.md` §10) | Direct parts-list inspection: no radio/antenna/RF-front-end component populated; moot in this instance since the selected MCU (STM32G031) has no radio silicon at all, but the check is against populated circuitry, not silicon capability, per REQ-006's own wording | Verified — confirmed not implemented | Cross-ref bom/component-selection.md's ESP32-C3 disqualification discussion (radio present on a candidate that was NOT selected) |
| REQ-101 | USB 5 V input, 4.75-5.25 V tolerance | J1 (USB-C) + U4 (USBLC6-2SC6 ESD) + U3 (TLV75533PDBVR LDO) | `bench-imu-01-design.md` §3, power-budget.md | Datasheet AMR/ROC cross-check: LDO AMR 6.0V (DS-PWR-002), ROC 1.45-5.5V (DS-PWR-003); ESD clamp rated for USB-C transients (DS-PROT-001) | Verified, with one open, human-dispositioned caveat | DS-PWR-002, DS-PWR-003, DS-CONN-001. **ISS-002 (HIGH, ACCEPTED-RISK, human-signed 2026-09-01)**: the real-world USB-C `vSafe5V` ceiling (4.75-5.5V) is wider than REQ-101's own stated 4.75-5.25V band; at the true worst-case 5.5V input the LDO operates above its 5.5V ROC ceiling but still 0.5V under its 6.0V AMR (reduced-functionality risk, not damage risk) — human explicitly accepted this bench-use edge case rather than reopening Component Selection. See `validation/change-log.md` ECO-003 |
| REQ-102 | Single 3.3 V logic rail | U3 (TLV75533PDBVR, fixed 3.3V) | `bench-imu-01-design.md` §2.1 | Schematic inspection: one regulated rail feeds MCU + IMU + all digital I/O, no second rail/level-shifter present | Verified | DS-PWR-001 |
| REQ-103 | System budget <= 300 mA @ 3.3 V | U1+U2+U4+passives | `hardware/power-budget.md` | Per-subsystem current arithmetic, worst-case summed | Verified | power-budget.md rollup: ≈16.2 mA worst-case vs. 300 mA ceiling (≈94.6% margin) and vs. 500 mA LDO rating (≈96.8% margin, DS-PWR-003). Real bench-measured current draw remains a physical-bring-up activity (REQ-502), not required to close this row — the hardware-design-capability claim (adequate margin exists) is independently paper-verifiable and has been |
| REQ-104 | IMU digital interface: I2C or SPI | I2C2 (PB10=SCL/PB11=SDA) | `bench-imu-01-design.md` §5 | Schematic inspection + MCU alternate-function table cross-check | Verified | DS-MCU-053 (corrects the original I2C1 mislabeling per ISS-011, RESOLVED); DS-IFACE-001 (bus timing/pull-up sizing) |
| REQ-105 | USB carries power only, no data | J1 (D+/D- unpopulated) | `bench-imu-01-design.md` §3.2 | Schematic/net-list inspection: J1's D+/D- pins are not routed to any MCU pin; U4's I/O1/I/O2 ESD-clamp channels are correspondingly unpopulated (VBUS-only protection use) | Verified | DS-PROT-002 (confirms USBLC6-2SC6 VBUS pin is itself a protected node, valid for VBUS-only use) |
| REQ-106 | 4-pin UART header (TX/RX/GND/3V3) | J2 | `bench-imu-01-design.md` §6, parts list | Schematic inspection | Verified | — |
| REQ-107 | MCU-family debug header | J3 | `bench-imu-01-design.md` §4.4, parts list | Schematic inspection (same evidence as REQ-002) | Verified | DS-CONN-002 |
| REQ-201 | Ambient 0-40 degC, indoor desk/lab | U1, U2, U3, U4 (all 4 active ICs) | N/A | Datasheet Recommended Operating Condition / operating-temperature-range cross-check, all 4 active ICs individually | Verified | DS-IMU-070 (BMI270: −40 to +85°C); DS-MCU-054 (STM32G031K8T6: −40 to +85°C); DS-PWR-047 (TLV75533PDBVR: −40 to +125°C junction); DS-PROT-003 (USBLC6-2SC6: −40 to +125°C junction). **Gap closed during this Design Complete Gate pass** — only the IMU's range had been checked during Component Selection; the MCU/LDO/ESD-IC ranges were confirmed just now (2026-09-03) to close this row honestly rather than leave it under-verified |
| REQ-202 | Vibration/shock qualification (Won't / N/A) | N/A | N/A | N/A — no rotating body/motor this benchmark, `docs/architecture.md` §12 co-design trigger does not apply | Verified — confirmed not applicable | — |
| REQ-203 | ESD precautions during handling | N/A (process requirement) | N/A | `validation/bring-up-procedure.md` ESD checklist item (procedure prepared with real values this cycle, not executed — REQ-502) | Verified — procedure documented; physical execution is a future human bring-up activity, correctly out of scope this cycle | See `validation/bring-up-procedure.md` |
| REQ-301 | Single 2-layer PCB, no daughtercards | Whole board | `hardware/mechanical-interface.md` Board Outline row | Schematic/board-outline inspection: one flat rectangular board, no stacked/daughter boards anywhere in the design or the enclosure geometry | Verified | Board Outline row marked `ASSUMPTION` in the interface file (Mechanical Lead's own reasonable inference from the design doc's silence on board shape) — honestly labeled, not overclaimed as `CONFIRMED` |
| REQ-302 | PCB footprint <= 60 x 40 mm | Whole board | `hardware/mechanical-interface.md` Board Outline row | `hardware/mechanical-interface.md` board geometry check | Verified | Board is exactly 60mm x 40mm — at the requirement's ceiling, not under it; enclosure interior (`bench-imu-01-dimensional-spec.md`) is sized around this exact figure, independently confirmed via OpenSCAD compile this cycle |
| REQ-303 | Connectors/headers on <= 2 board edges | J1, J2, J3, SW1 | `hardware/mechanical-interface.md` connector location rows | Connector-location check: J1 (USB-C) on the left short edge (X=0); J2/J3 (UART/SWD headers) + SW1 (reset) all on the top long edge (Y=40) | Verified | 2 edges used (1 short + 1 long) of the 4 available, satisfying the "<=2" ceiling with one edge to spare |
| REQ-304 | >= 4 mounting holes, M2/M2.5 | MH1-MH4 | `hardware/mechanical-interface.md` mounting table | Mounting-hole table check: 4x, M2.5, ⌀2.8mm clearance holes, one per corner | Verified | MH row marked `ESTIMATE` in the interface file (exact X/Y inset is the Mechanical Lead's own proposal, not a Circuit-Engineer-confirmed PCB layout coordinate) — honestly labeled |
| REQ-305 | 2-piece, 3D-printable enclosure | Full enclosure | `hardware/mechanical/bench-imu-01-enclosure.scad`, `bench-imu-01-dimensional-spec.md` | Design artifact inspection + real OpenSCAD compile (valid manifold geometry, confirmed independently by both the Mechanical Lead and the Hardware Lead) | Verified | `bench-imu-01-dimensional-spec.md` explicitly states this row satisfied; 2 Independent Mechanical Review cycles (MISS-001 through MISS-007) passed with 0 open CRITICAL/HIGH |
| REQ-401 | No regulatory certification target (Won't) | N/A | N/A | N/A — explicitly out of scope this iteration, per REQ-401's own text | Verified — confirmed not applicable | — |
| REQ-402 | USB ESD / reverse-polarity protection | U4 (ESD only); no discrete reverse-polarity component | `bench-imu-01-design.md` §3 | Schematic inspection + Evidence ID citation | Verified — human-accepted disposition | DS-PROT-001/002 (ESD: real IC present and adequate). **ISS-004 (MEDIUM, ACCEPTED-RISK, human-signed 2026-09-03)**: reverse-polarity protection relies on USB-C's own mechanical keying (prevents normal-use plug reversal) rather than a discrete component (would additionally catch a miswired/off-brand cable). Human Chief Engineer explicitly reviewed and accepted this as sufficient for this bench-use prototype at the Design Complete Gate — see `validation/change-log.md` ECO-005 |
| REQ-501 | BOM cost target <= ~$15 USD | All parts | `bom/component-selection.md` price citations | Price rollup of the 3 highest-value ICs (individually Evidence-ID-cited) vs. remaining un-priced low-cost passives/connectors/mounting hardware | Waived — human sign-off 2026-09-03 | 3 primary ICs alone (qty-1, conservative/high-end quote): MCU $2.83 [DS-MCU-018] + IMU $4.23 [DS-IMU-012] + LDO $0.45 [DS-PWR-009] = **$7.51**, ≈50% of the $15 soft target. Remaining ~14 line items (USBLC6-2SC6 ESD IC, J1/J2/J3 connectors, SW1, D1, 14 passives, mounting hardware) were not individually priced this cycle — a full rollup is structurally blocked because J1 and D1 never received a formally-selected MPN during Circuit Design (a disclosed gap from that phase, not new). **Human Chief Engineer explicitly waived full-rollup verification of this row at the Design Complete Gate** (via `ask_user`, 2026-09-03) — REQ-501 is a "Should" (soft steer, not a hard ceiling), and the priced primary ICs already show strong margin. See `validation/change-log.md` ECO-005 |
| REQ-502 | Schedule target (Won't / N/A) | N/A | N/A | N/A — paper/document design exercise this cycle, confirmed true for the entire cycle (no PCB fabrication, no physical power-on, no physical 3D print occurred) | Verified — confirmed not applicable | — |
| REQ-007 | Motor+wheel open-loop speed control (Rev 3) | TBD (Component Selection) | TBD (Circuit Design Rev 3) | TBD | Pending | `requirements/requirements.md` §9b — torque/RPM target pending human confirmation |
| REQ-008 | Firmware RPM measurement/reporting (Rev 3) | TBD | TBD | TBD | Pending | Contingent on Component Selection finding an RPM-sensing option; see REQ-008's own contingency note |
| REQ-009 | No closed-loop/PID/IMU-reactive control (Won't, Rev 3) | N/A | N/A | N/A — explicit anti-scope, verify by firmware source inspection at handoff | Pending | Verification method: confirm no control-loop code exists in firmware bring-up deliverable |
| REQ-010 | Existing IMU readout unregressed (Rev 3) | U2 BMI270 (unchanged) | TBD | Regression check against Rev 2's already-Verified REQ-001 row | Pending | |
| REQ-108 | Motor subsystem power architecture defined (Rev 3) | TBD (Power Engineer) | `hardware/power-architecture.md` | Human HITL architecture-decision sign-off | Pending | Architecture decision gate — see `docs/architecture.md` §10 |
| REQ-109 | Motor rail budget tracked separately from REQ-103 (Rev 3) | TBD | `hardware/power-budget.md` (multi-rail) | Numeric rollup check | Pending | |
| REQ-110 | MCU PWM/drive output to motor driver (Rev 3) | TBD (Circuit Design) | TBD | Schematic/pin-table inspection | Pending | |
| REQ-111 | Motor driver overcurrent/stall protection (Rev 3) | TBD (Component Selection) | TBD | Datasheet spec check | Pending | |
| REQ-112 | RPM/tach feedback wired if available (Rev 3) | TBD | TBD | Schematic inspection | Pending | Contingent — see REQ-008 |
| REQ-204 | Vibration effect on IMU/PCB assessed (Rev 3) | All active ICs + U2 (BMI270) | TBD (Circuit Design + Mechanical Design Rev 3) | Mechanical/thermal co-design review, `docs/architecture.md` §12 | Pending | Supersedes REQ-202's Rev 2 "N/A" disposition for this revision |
| REQ-306 | Flywheel rotation clearance envelope (Rev 3) | TBD (Mechanical Design) | TBD | Mechanical Reviewer clearance check | Pending | |
| REQ-307 | Motor/flywheel mount vibration isolation from IMU (Rev 3) | TBD | TBD | Mechanical Reviewer check | Pending | |
| REQ-308 | Relaxed PCB/enclosure envelope, desk-scale sanity bound (Rev 3) | TBD | TBD | Dimensional-spec check vs. ~150mm proposed bound | Pending | Supersedes REQ-302's Rev 2 ceiling for this revision — see §9b for confirmation |
| REQ-309 | 3D-printable enclosure, piece count as needed (Rev 3) | TBD | TBD | Manufacturability self-check + Mechanical Reviewer | Pending | |
| REQ-403 | Flywheel detachment/pinch hazard mitigation (Rev 3) | TBD (Mechanical Design) | TBD | Human safety-critical-change sign-off required, `docs/architecture.md` §10 | Pending | |
| REQ-404 | Motor stall/overcurrent shutdown behavior (Rev 3) | TBD (Circuit/Firmware) | TBD | Design + firmware inspection | Pending | Companion to REQ-111 |
| REQ-503 | Rev 3 BOM cost target ≤$75-90 (Rev 3) | All parts | `bom/component-selection.md` | Price rollup, mirrors REQ-501's own method | Pending | Proposed ceiling pending human confirmation, §9b |
| REQ-504 | Schedule/no-physical-build unchanged (Rev 3) | N/A | N/A | N/A — paper/document design exercise, mirrors REQ-502 | Pending | |

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
