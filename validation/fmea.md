# FMEA — Failure Mode and Effects Analysis

Systemic risk register — distinct from `validation/open-issues.md`. Where
`open-issues.md` tracks concrete defects found in a specific reviewed design
snapshot, this file anticipates failure modes **before** they're observed,
across the whole system. See `docs/architecture.md` §7.2–7.3 for why these
two are kept on separate scales instead of merged.

**Elevated importance for this project**: the roadmap targets a CubeSat-class
system (`docs/architecture.md` §11). Once hardware is in orbit it cannot be
repaired — failure modes must be anticipated in advance, not just found by
review after the fact. Treat FMEA rigor as increasing as the project
approaches actual flight hardware (this template is intentionally
lightweight for the MVP benchmark; expect more formal FMECA practice later).

## Scoring

RPN = Severity × Occurrence × Detection, each scored 1–10 (10 = worst/least
detectable). This is intentionally a different scale from the Hardware
Reviewer's CRITICAL/HIGH/MEDIUM/LOW (`docs/architecture.md` §7.1) — do not
conflate the two.

## Risk Register

| FMEA ID | Component/Function | Potential Failure Mode | Potential Effect (Local/System/Mission) | Severity (1-10) | Potential Cause | Current Controls | Occurrence (1-10) | Detection (1-10) | RPN | Recommended Action | Owner | Status | Related IDs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FMEA-001 | U3 (TLV75533PDBVR LDO), VIN pin | VIN briefly exceeds the LDO's 5.5V Recommended Operating Condition ceiling (staying under the 6.0V Absolute Maximum Rating) when the real USB-C `vSafe5V` tolerance reaches its own worst-case 5.5V | Local: possible reduced regulation accuracy/transient response near the ROC edge, per TI's own ROC-exceedance disclaimer — not damage. System: momentary 3.3V rail noise/drift at a rare worst-case input. Mission: none (bench/desk use) | 4 | USB source supplying at the outer edge of the USB-C `vSafe5V` spec (5.5V) rather than typical 5.0V nominal | None at circuit level (no pre-regulation/clamp before the LDO); mitigated only by most real USB sources running close to nominal in practice | 3 | 6 | 72 | Revisit if this design is ever mass-produced or exposed to a less-controlled input-source population; consider a higher-ROC-ceiling LDO or input pre-clamp at that time | Human Chief Engineer (risk already accepted 2026-09-01) | Open (accepted residual risk — accepting a risk does not remove it from this register) | ISS-002, DS-PWR-002, DS-PWR-003, REQ-101, `validation/change-log.md` ECO-003 |
| FMEA-002 | U1 (STM32G031K8T6), BOOT0/nBOOT_SEL configuration | MCU boots into System Memory (bootloader) instead of user Flash at power-up due to BOOT0 pin-vs-option-byte confusion | Local: MCU appears non-functional at power-up. System: whole board non-functional until diagnosed. Mission: N/A (bench board); recoverable via SWD | 5 | STM32G0 family allows BOOT0 behavior to be selected by physical pin OR by an internal option byte — an original design-doc error conflated the two (ISS-006) | Corrected schematic net + explicit design-doc note distinguishing pin-mode vs. option-byte mode (Rev 2, RESOLVED); SWD header (J3) provides a recovery path even if boot mode is wrong | 2 | 3 | 30 | At physical bring-up, verify BOOT0/nBOOT_SEL state matches documented intent before first power-on; add explicit check to `validation/bring-up-procedure.md` | Human (at physical bring-up) | Open (design-level cause fixed; residual assembly-time risk remains, appropriately tracked) | ISS-006, DS-MCU-050, DS-MCU-051, REQ-002, REQ-107 |
| FMEA-003 | U1<->U2 I2C bus (PB10/PB11) documentation vs. physical peripheral | Design documentation consistently labels the bus "I2C1" while PB10/PB11 are physically I2C2 — a single initial misread propagated silently through every later reference since nothing looked internally inconsistent | Local: none yet (caught pre-layout/pre-firmware). System: if undetected, firmware would initialize the wrong peripheral's registers — bus silently non-functional, a realistic multi-hour future debugging session. Mission: N/A | 6 | STM32G0 pin-to-peripheral alternate-function table misread once during initial Circuit Design; self-consistent internal documentation gave no contradiction signal | Rubber-duck's independent premise-review caught it (ISS-011) after the checklist-only Hardware Reviewer pass had already missed it in Cycle 1 — demonstrating checklist-only review has a real blind spot for this failure class; RESOLVED in Rev 2, corrected everywhere (DS-MCU-053) | 2 | 5 | 60 | Systemic lesson, not just a one-off fix: continue running both hardware-reviewer (checklist) and rubber-duck (independent premise-check) for every future revision — this cycle empirically demonstrated the checklist-only pass alone would have missed this class of error | Hardware Lead (process-level; already standing practice this cycle) | Resolved (instance fixed; entry retained for the systemic lesson's ongoing value) | ISS-011, DS-MCU-053, `validation/design-review.md` mediation addendum |
| FMEA-004 | Enclosure lid: LED viewing hole vs. widened header bay wall | The wall between D1's LED viewing hole and the Rev-2-widened header bay is only ≈1.0mm — below the Mechanical Lead's own stated 2.0mm minimum-wall-thickness rule | Local: a thin, potentially fragile/warping-prone wall section at the lid's LED cutout, or slight light-leak between LED and header-bay opening. System: cosmetic/durability nuisance, not functional or safety. Mission: N/A | 3 | Side effect of the Rev 2 fix for MISS-001 (widening the header bay for correct footprint-edge clearance) that was not re-checked against every other nearby feature's own clearance rule until Independent Mechanical Review Cycle 2 re-ran the full checklist post-fix | None yet — genuinely open, newly found (2026-09-02/03) finding, disclosed transparently as a real side effect rather than glossed over | 8 | 2 | 48 | Widen the LED cutout's offset from the header bay by >=1.0mm in the next Mechanical revision (a small, localized geometry nudge), or relocate D1 — MEDIUM/non-gating, deferrable to the next revision | Mechanical Lead (next revision) | Open | MISS-007, `hardware/mechanical/bench-imu-01-dimensional-spec.md`, REQ-003, REQ-305 |
| FMEA-005 | J1 (USB-C input), U3 (LDO) VIN | A miswired, damaged, or non-compliant USB cable presents reversed VBUS/GND at J1, unblocked by any discrete protection component | Local: LDO and/or downstream ICs could see reverse voltage on VIN with no series/ideal diode to block it. System: potential real component damage (reverse-tolerance not independently characterized this cycle). Mission: N/A | 7 | USB-C's mechanical keying prevents normal plug-reversal but does not protect against a genuinely miswired/defective/off-spec cable's internal pin assignment | Mechanical keying only (prevents the common case); no discrete circuit-level protection currently in the design (ISS-004, OPEN) | 2 | 9 | 126 | Add a low-cost discrete reverse-polarity mitigation (series Schottky diode, or ideal-diode PFET for better efficiency) sized for the ≈16.2mA worst-case draw — the single highest-RPN, lowest-cost improvement available for the next revision | Circuit Engineer (next revision) / Human Chief Engineer (decide fix-now vs. accept-as-is) | Open — **highest RPN on this register** | ISS-004, DS-CONN-001, REQ-402 |
| FMEA-006 | U2 (BMI270), supply chain | Primary IMU candidate becomes hard to source (price spike, allocation, discontinuation) before this design is ever repeat-built | Local: BOM line item unavailable. System: board cannot be repeat-built as-designed without a footprint-compatible substitute. Mission: N/A for a single bench prototype; relevant only if repeat-built | 4 | Real market observation from Component Selection: of the 4 IMU candidates researched, 2 already showed real availability friction at research time (one eval-board-only with no confirmed breakout; one effectively legacy/secondary-market-only) — supply-chain fragility is a demonstrated pattern in this exact part class, not a hypothetical | A named, real, datasheet-compatible fallback (LSM6DSOX) was already identified and human-approved during Component Selection specifically to hedge this risk | 3 | 5 | 60 | If/when repeat-built, re-confirm BMI270 stock status first; if unavailable, the already-identified LSM6DSOX fallback requires a footprint/pinout re-check before substitution (not a guaranteed drop-in) | Component Engineer (at next build) | Open | `bom/component-selection.md` IMU comparison table, REQ-001 |
| FMEA-007 | Whole-board <-> whole-enclosure geometric fit | The enclosure's internal geometry was derived from `hardware/mechanical-interface.md`'s stated/estimated component positions and heights — several explicitly marked `ASSUMPTION`/`ESTIMATE` (e.g. mounting-hole X/Y, J1/J2/J3/SW1/D1 placement; J1/D1 MPNs not yet formally selected) — because no real PCB layout exists yet | Local: a specific cutout/standoff/clearance could shift once a real PCB layout exists. System: enclosure may need a dimensional revision before physical fabrication. Mission: N/A | 5 | Structural, disclosed consequence of this cycle's own scope: paper/document design exercise, no physical PCB fabrication, no CAD/PCB-layout tool verified connected (`docs/architecture.md` §5.2/§5.3) — a known limitation, not a hidden defect | Every non-Circuit-Engineer-confirmed dimension in `hardware/mechanical-interface.md` is explicitly labeled `ASSUMPTION`/`ESTIMATE`, never silently presented as `CONFIRMED`, so the exact re-work scope is already flagged row-by-row | 10 | 2 | 100 | Before physical fabrication of either the PCB or the enclosure, produce a real PCB layout (KiCad, once connected) and re-run Independent Mechanical Review against the real component placement, re-confirming every `ASSUMPTION`/`ESTIMATE` row | Human Chief Engineer (before physical fabrication of either artifact) | Open | `hardware/mechanical-interface.md` (all ASSUMPTION/ESTIMATE rows), REQ-301–REQ-305, `docs/architecture.md` §5.2/§5.3 |
| FMEA-008 | MCU (U1) pin/peripheral assignment vs. real physical package pinout, verification process itself | A design document's pin assignment can pass both a checklist review (Hardware Reviewer) and an alternate-function-table cross-check (rubber-duck/ISS-011) while still being physically unbuildable, because "which alternate function does this pin name support" (the AF table) and "does this pin name exist as a bonded-out physical pin on this exact package" (the pin-definition/pinout-diagram table) are two separate tables in a manufacturer's datasheet, and every prior verification pass on this design checked only the first | Local: none yet (caught before any physical PCB layout or fabrication). System: if undetected until PCB layout or bring-up, a full board re-spin would be needed — no trace can connect to a pin that does not exist. Mission: N/A for a single bench prototype; would be a much more expensive discovery on a flight-committed design | 6 | A genuine, demonstrated blind spot: Component Selection, Circuit Design, 2 Hardware Reviewer cycles, 1 rubber-duck pass, and the Firmware Engineer's own independent AF-value confirmation (DS-MCU-062) all correctly verified the AF-table mapping (PB10/PB11 = I2C2 via some AF value) without ever independently cross-checking the separate physical-package-pinout table for this exact package variant | Only caught once a real KiCad project was built and real symbol/footprint data (sourced from ST's own official machine-readable pin database, not a distributor aggregator) was checked pin-by-pin against the design — the first time in this design's history that a *physical, tool-derived* pin table was cross-checked against the documented one, rather than another AF-table-only pass | 4 | 3 | 72 | Systemic lesson, not just a one-off fix: whenever a real KiCad project exists (or is being newly created) for a design, cross-check the schematic's MCU symbol's real, physically-bonded pin list against the design document's stated pin table as a distinct verification step from AF-table checking — this cycle empirically demonstrated that AF-table verification alone, however careful, does not catch a physical-pin-non-existence defect on a pin-count-reduced package | Hardware Lead (process-level; recommend making this an explicit Hardware Reviewer checklist item once a KiCad project exists for a design) | Open | ISS-027 (renumbered 2026-09-11 from "ISS-014" during the main-branch merge, ECO-014 — see `validation/change-log.md`), DS-MCU-064/067, `validation/design-review.md` (this pass's entry) |
| FMEA-009 | Motor+flywheel subsystem: flywheel detachment/containment (Rev 3) | Hub-collar coupling loses grip on M1's shaft (vibration, installation error, or a lower-quality assumed generic set-screw collar — no datasheet exists for its retention strength), releasing the 100g disk as a rigid projectile at whatever speed the motor is spinning | Local: direct laceration/impact hazard to a bench operator (up to ~285 km/h rim speed / ~156-158J at M1's corrected, path-drop-accounted credible-worst-case no-load speed — DS-MTR-018 corrected/DS-MTR-080, `hardware/schematic/bench-imu-01-design.md` §7.5.13 — supersedes the previously-cited ~250km/h/~122J figures, which used a mislabeled voltage basis; REQ-405's firmware ceiling is a compensating control, not a guarantee, until independently hardware-confirmed). System: enclosure/PCB damage from an internal impact. Mission: N/A (bench-test only) | 9 | Bulk-material stress is not the risk (~12.4x safety factor vs. yield even at the corrected no-load speed, down from the superseded ~15.9x but still comfortably non-binding) — the risk is an entirely unquantified (UNKNOWN-strength) mechanical coupling, combined with a motor whose real achievable speed is currently bounded only by its own physical no-load limit (corrected credible worst-case ≈25,180 RPM, up from the superseded ~20,000-22,200 RPM figure), not yet by software, since REQ-405 has not been independently hardware-confirmed | Mechanical Lead's containment cap proposal (4.0mm continuous 360° wall, no rotation-plane opening, genuinely bolted 6xM3, not snap/friction-fit) — independently confirmed credible (both topology and specific numbers) by 2 Independent Mechanical Review cycles; explicitly NOT a certified containment/ballistic analysis (MISS-011). MISS-016's own quantified wall-margin shortfall (HIGH, open) widens further against these corrected, higher figures. Firmware REQ-405 (6000 RPM ceiling) exists at the source level but is not yet hardware-confirmed | 3 | 4 | 108 | (1) Obtain the human Chief Engineer's own explicit REQ-403 safety sign-off on the containment proposal (currently the paused HITL gate this entry itself is written to inform — not to substitute for); (2) once physical hardware exists, source a real, datasheet-specified hub collar (replacing the current generic ASSUMPTION) and independently confirm its retention torque/pull-off strength; (3) hardware-confirm REQ-405's overspeed ceiling actually trips before any physical spin test at meaningful RPM | Human Chief Engineer (REQ-403 sign-off); Mechanical Lead (hub collar sourcing, future); Firmware Engineer/human (hardware confirmation, future) | Open — **new, highest RPN on this register** | REQ-403, REQ-405, ISS-020, MISS-016, `hardware/mechanical/bench-imu-01-dimensional-spec.md` §8, `validation/design-review.md` Mechanical Reviewer Cycle 3/4 |
| FMEA-010 | Motor+driver subsystem: stall/sustained-overcurrent (Rev 3) | A mechanical bind or jam on the flywheel/motor causes repeated stall/overcurrent events; without a policy that actually stops trying (not just auto-retries), each cycle dissipates real heat in U5, M1, and D2 indefinitely | Local: thermal stress on U5/M1/D2 from repeated fault-current pulses; possible component degradation over many cycles. System: sustained heat near the motor rail, adjacent to the PCB's other components. Mission: N/A (bench-test only) | 5 | All 3 of U5's own hardware protections (OCP, Lock Detection, Thermal Shutdown) are auto-recovering/auto-retrying by design (DS-MTR-058/059/060) — none of them, alone, implements a shutdown that stays off until an operator acknowledges it (ISS-021's own finding) | Firmware REQ-406 (3 Lock-Detection events / rolling 30s window -> latch, SPEED->0 + U6 SHDN->low, deliberate REARM required) closes the actual gap — exists at the source level, self-checked against `.github/skills/firmware-bringup/SKILL.md`, not yet independently reviewed (no Firmware Reviewer role exists yet) or hardware-confirmed | 3 | 4 | 60 | Hardware-confirm REQ-406's latch policy actually trips and stays latched (not just auto-clears) once physical hardware exists, before any extended bench-test run; consider whether a future Firmware Reviewer role (`docs/architecture.md` §14) should independently re-check this specific safety-critical logic rather than relying on self-check alone | Human/Firmware Engineer (hardware confirmation, future); Hardware Lead (Firmware Reviewer trigger reassessment, ongoing) | Open | REQ-404, REQ-406, ISS-021, `firmware/bench-imu-01/src/motor.c` |
| FMEA-011 | Motor+flywheel subsystem: vibration-coupled IMU bias drift (Rev 3) | The spinning flywheel's residual imbalance/vibration couples through the shared enclosure/PCB structure into the IMU (U2), corrupting its accel/gyro readings whenever the motor is powered, without the operator necessarily realizing the readings are degraded rather than genuinely representing motion | Local: IMU data quality degrades during motor operation, silently if not flagged. System: any future consumer of this board's IMU data (e.g. a future attitude-control stage) would need to know motor-on periods are less trustworthy. Mission: N/A this cycle (raw IMU readout only, REQ-009's own scope fence) but directly relevant to the project's own roadmap (`docs/architecture.md` §11) | 4 | REQ-307's own vibration-isolation assessment concluded "not fully feasible within this phase's scope" — the off-board motor mount + spatial separation are partial/incidental mitigation only, not a validated isolation mechanism, and no actual vibration-coupling measurement has been performed (no physical hardware exists) | Physical/spatial separation (off-board mount) only; explicitly disclosed as partial, not solved, in `hardware/mechanical/bench-imu-01-dimensional-spec.md`'s own vibration-isolation discussion | 6 | 7 | 168 | Once physical hardware exists, perform a real motor-on vs. motor-off IMU noise/bias comparison (the exact check ISS-023 originally flagged as missing from `validation/bring-up-procedure.md`) before trusting IMU data gathered during motor operation for any future purpose | Human (at physical bring-up, future) | Open — **new, highest RPN on this register**, driven by Detection=7 (no real measurement exists yet to know how bad this actually is) | REQ-204, REQ-307, ISS-023, `hardware/mechanical/bench-imu-01-dimensional-spec.md` |
| FMEA-012 | Motor-rail wiring/connector (Rev 3): J4 and MC-1 motor phase-wire routing | J4 (barrel jack) or the motor's own 3-phase wire-lead pigtail (routed through the enclosure's wire duct, MC-1 in `hardware/mechanical-interface.md`) suffers a loose/intermittent connection or insulation damage at the duct's edges, given this is a wire-lead connection (not a PCB-soldered footprint) crossing between the off-board motor mount and the PCB | Local: intermittent motor operation, or a short/ground-fault if wire insulation is damaged at a duct edge. System: could couple noise/transients into the shared ground net spanning both power domains (§8). Mission: N/A (bench-test only) | 5 | The motor's off-board mounting decision (Mechanical Lead) means this design has a genuine wire-lead crossing this project's prior revisions never needed — MISS-009's own finding (the wire duct void being only locally, not globally, subtracted) shows this exact interface has already had one real geometry defect caught by review | MISS-009 fixed (duct now genuinely open along its full path, independently re-verified via a 2,516-point sweep); no strain-relief/grommet or wire-insulation spec has been separately assessed at the duct's edges | 3 | 6 | 90 | At physical assembly, add strain relief/a grommet at the duct's edges if the routed wire shows any chafing risk against the duct's own printed edges; re-inspect this specific interface during any future Independent Mechanical Review cycle that touches the wire-duct geometry again | Mechanical Lead (at physical assembly, future) | Open | MISS-009, `hardware/mechanical/bench-imu-01-dimensional-spec.md`, `hardware/mechanical-interface.md` (MC-1) |
| FMEA-013 | Free-rotation mechanism (Rev 4.1): `pinch_guard()` positional drift | The unfastened, desk-resting guard ring (explicitly disclosed as unkeyed to `stand_plate()`) shifts out of its designed flush position over repeated handling/bumps, widening the already-accepted 11.4mm residual gap or opening a new gap elsewhere around the ring | Local: reduced/degraded pinch-hazard coverage below the already-accepted 77.7% (MISS-023). System: N/A. Mission: N/A (bench-test) | 6 | The guard's own design explicitly has no positive retention/locating feature (disclosed `bench-imu-01-dimensional-spec.md` §18.12.7/§18.16) — it sits flush against `stand_plate()` by gravity/friction alone | None — genuinely open; no positional-drift detection or retention mechanism exists | 5 | 6 | 180 | If this rig sees repeated/extended use, add a positive retention/locating feature (registration pins/clips) to `pinch_guard()`/`stand_plate()` in a future revision — already named as an available future refinement in MISS-023's own ACCEPTED-RISK disposition, not a new ask | Mechanical Lead (future revision, if warranted) | Open — accepted alongside MISS-023, `validation/change-log.md` ECO-031 | MISS-023, REQ-407, REQ-205, ECO-031 |
| FMEA-014 | Free-rotation mechanism (Rev 4.1): cable turn-limit procedure not followed | Operator does not track the 3-turn limit / `rotation_index_pointer()` witness mark and continues rotating past it, winding the external J1/J4 tether until it yanks the connector or binds the mechanism | Local: connector-shell/solder-joint damage at J1/J4, or a jammed/stalled rotation. System: loss of the existing wired power/data link (REQ-101/105/106). Mission: N/A (bench-test) | 4 | A real human-factors risk — nothing in the mechanism itself enforces the limit; a distracted operator could miss the visual witness mark | `rotation_index_pointer()` (visual turn-counting witness mark) + documented 3-turn/re-centering procedure (§18.13) — a procedural, not automated, control | 4 | 5 | 80 | Consider a future firmware-side rotation-count tracking (using the already-onboard IMU gyro, REQ-013) that warns/limits before the mechanical turn-limit is reached — an available future enhancement, not required this cycle since REQ-113's own text explicitly authorizes the procedural-only mitigation as its Must-priority default | Firmware Engineer (future, if engaged for Rev 4's own control-adjacent work — not yet triggered) | Open — inherent to the accepted procedural (not automated) mitigation; MISS-024 itself is RESOLVED at the design level | MISS-024, REQ-113, REQ-012 |
| FMEA-015 | Free-rotation assembly (Rev 4/4.1): tip-over under dynamic disturbance | The computed static tip-over margin (6.2x-12.17x, `bench-imu-01-dimensional-spec.md` §18.3) covers a simple static horizontal bump force only — an abrupt reaction-wheel torque reversal or a dynamic/resonant disturbance interacting with an uneven desk surface has not been separately modeled and could in principle behave differently than the static case | Local: the whole assembly tips/falls off the desk. System: potential damage to the board/motor/flywheel from the fall itself. Mission: N/A (bench-test) | 5 | No dynamic/resonance analysis has been performed this cycle — an honest, disclosed analysis gap, not a confirmed problem | Large static margin (6.2x-12.17x) provides some real cushion against an unmodeled dynamic effect, though not a substitute for an actual dynamic analysis | 2 | 7 | 70 | If/when firmware speed-increment testing (REQ-013) begins, start with the smallest commanded speed steps and observe the platform's actual response before committing to any larger/faster torque reversal — an empirical, incremental approach, consistent with REQ-013's own already-established mitigation | Human (at physical bring-up, future) / Firmware Engineer (implementing the speed-increment behavior) | Open — a genuine analysis gap, not yet a confirmed problem | REQ-012, REQ-013, REQ-407, `bench-imu-01-dimensional-spec.md` §18.3 |
| FMEA-016 | Free-rotation mechanism (Rev 4): bearing-mount self-tapping fastener load | Self-tapped PETG threads at the 4 bearing-mount pilot holes (`bmount_flange()`/`stand_plate()`) strip/loosen under the joint's actual static+dynamic load, since no pull-out/shear calculation was performed (MISS-025, MEDIUM, OPEN) | Local: the bearing's own top or bottom plate detaches from its printed mount, potentially dropping/destabilizing the whole rotating assembly. System: loss of REQ-011's core function, possible fall. Mission: N/A (bench-test) | 6 | Self-tapping into PETG is a well-precedented joint class in this project (e.g. `base_tab()`), but this specific joint's own load was never calculated — an unquantified, not obviously severe, risk | Generous wall thickness by construction around each pilot hole (§18.1.1), but no load calculation exists to confirm adequacy | 3 | 5 | 90 | Perform a basic pull-out/shear calculation for this joint (generic PETG self-tap literature values exist, mirroring how MISS-011 was eventually addressed for the containment-cap joint) before repeated/extended physical use — MISS-025's own already-recorded Recommended Fix | Mechanical Lead (future pass, if this rig sees repeated/extended use) | Open — mirrors MISS-025's own disposition (MEDIUM, non-gating, OPEN) | MISS-025, REQ-011, `bench-imu-01-dimensional-spec.md` §18.8 |

## Review Log

**2026-09-03 — Bench-IMU-01, Rev 2 (Electronics) / Rev 2 (Mechanical), Hardware Lead, first FMEA pass for this revision.**

All 7 entries above are design-specific — each traces to a real fact,
finding, or process observation from this actual design cycle (5 trace to
existing `open-issues.md` findings: ISS-002, ISS-006, ISS-011, ISS-004,
MISS-007; 2 are new systemic-risk observations surfaced for the first time
during this FMEA pass: FMEA-006 IMU supply-chain risk, drawn directly from
real availability friction already seen for 2 of 4 IMU candidates during
Component Selection; FMEA-007 the inherent paper-design-vs.-real-PCB-layout
gap, drawn from this cycle's own disclosed tooling limitation). None are
generic placeholder entries.

**RPN range**: 30–126. Highest: **FMEA-005 (RPN 126, reverse-polarity
protection)** — notably, this is a MEDIUM-severity finding in the
Reviewer/open-issues.md taxonomy (non-gating for Design Complete) but scores
the highest RPN here, precisely because RPN and Reviewer-severity are
different scales measuring different things (`docs/architecture.md`
§7.2–7.3) — a real, useful illustration of why the framework keeps them
separate rather than conflating "not gating" with "not worth fixing soon."
Second-highest: FMEA-007 (RPN 100, driven by Occurrence=10 — a near-certainty
given no real PCB layout exists yet — offset by low Detection=2 since the
gap is already fully disclosed, not hidden).

**No entry required a design change during this FMEA pass itself** — this
pass is a review/anticipation step, not a new review cycle; entries tied to
already-open findings (ISS-004, MISS-007) keep their existing disposition
and owner from `validation/open-issues.md`, they are not re-litigated here.

**Condition 4 of the Design Complete Gate** (`docs/architecture.md` §8: "FMEA
reviewed for this revision") is satisfied by this pass.

**2026-09-11 — Bench-IMU-01, Rev 3 (Electronics/Mechanical/Firmware),
Hardware Lead, FMEA closeout pass for this revision.**

FMEA-008 was brought in via the `origin/main` merge (ECO-014) — one
Circuit-Engineer-authored row, otherwise untouched by this branch's own
Rev 3 work until this pass. Its own citation of "ISS-014" was found stale
during this closeout (that number was renumbered to **ISS-027** during
the merge, per ECO-014's own renumbering map) — corrected in place, not
silently, per this file's own evidence-integrity convention.

**5 new entries added, all design-specific** (per ISS-023's own flag that
this project's Rev 1/2 "no vibration/shock, single simple rail"
validation-artifact premise needed updating once a real rotating body
existed): FMEA-009 (flywheel detachment/containment — the REQ-403
safety-critical hazard this whole revision has been building toward
mitigating), FMEA-010 (motor stall/sustained-overcurrent, tied to
REQ-404/406's latching-policy gap), FMEA-011 (vibration-coupled IMU bias
drift — a real, disclosed-as-partial mitigation risk, not a solved
problem), FMEA-012 (motor-rail wire-lead/connector risk, specific to the
off-board motor-mounting decision this revision introduced). None are
generic placeholders — each traces to a real Rev 3 finding, requirement,
or disclosed engineering trade-off already on record in
`validation/open-issues.md`, `requirements/requirements.md`, or the
Mechanical Lead's own dimensional-spec document.

**RPN range this pass**: 60–168. Highest: **FMEA-011 (RPN 168, IMU bias
drift)** — driven by Detection=7, since no physical hardware exists yet
to actually measure how bad the coupling is; this is an honest
reflection of genuine uncertainty, not an inflated number. Second:
**FMEA-009 (RPN 108, flywheel containment)** — the entry most directly
tied to REQ-403's still-pending human safety sign-off; this FMEA entry
is written to **inform** that gate, not substitute for it. As with the
Rev 2 pass's own FMEA-005 finding, note that FMEA-011's high RPN does not
correspond to a CRITICAL/HIGH Reviewer-severity finding — REQ-307's own
"Should"/"where feasible" wording and the honest "assessed, partial
mitigation" disposition are non-gating for Design Complete, illustrating
again why this project keeps the two scales separate.

**No entry required a design change during this pass** — same rule as
the Rev 2 pass; FMEA-009/010's own driving findings (REQ-403's pending
sign-off, REQ-405/406's firmware-source-level-but-not-hardware-confirmed
status) keep their existing disposition from `validation/open-issues.md`
and `requirements/traceability-matrix.md`, not re-litigated here.

**Condition 4 of the Design Complete Gate** is satisfied for Rev 3 by
this pass — independent of REQ-403's own still-separate, still-pending
human sign-off (Design Complete Gate condition 2 — every HIGH/CRITICAL
RESOLVED or ACCEPTED-RISK — remains the gating condition for that
decision, not this FMEA review).

**2026-09-15 — Bench-IMU-01 Rev 4/4.1 (Mechanical: free-rotation support
mechanism), Hardware Lead, FMEA pass for this revision.**

**4 new entries added, all design-specific**, covering the systemic risks
the new free-rotation mechanism introduces beyond the point-in-time
findings already tracked in `validation/open-issues.md`: FMEA-013
(`pinch_guard()` positional drift — the systemic, ongoing-risk counterpart
to MISS-023's own point-in-time ACCEPTED-RISK disposition: even though the
human has accepted the guard's *current* residual gap, the guard's own lack
of a retention feature means that gap could realistically widen further
over the rig's service life, not just stay fixed at 11.4mm), FMEA-014
(cable turn-limit procedure not followed — the systemic human-factors risk
behind MISS-024's design-level RESOLVED disposition: a procedural, not
automated, mitigation is only as reliable as the operator's own attention),
FMEA-015 (tip-over under dynamic disturbance — an honestly-disclosed
analysis gap: the computed 6.2x-12.17x margins are static-bump figures, not
a dynamic/resonance model, since no such model has been built this cycle),
FMEA-016 (bearing-mount self-tapping fastener load — the systemic
counterpart to MISS-025's own already-open, non-gating MEDIUM finding).
None are generic placeholders — each traces to a real Rev 4/4.1 finding,
requirement, or disclosed engineering trade-off already on record in
`validation/open-issues.md`, `requirements/requirements.md`, or the
Mechanical Lead's own dimensional-spec document (§18).

**RPN range this pass**: 70-180. Highest: **FMEA-013 (RPN 180,
`pinch_guard()` positional drift)** — the same illustration this file's own
prior passes have already made twice (FMEA-005/FMEA-011): a finding that is
non-gating/ACCEPTED-RISK in the Reviewer/open-issues.md severity taxonomy
can still carry the highest RPN here, because RPN and Reviewer-severity
measure genuinely different things (`docs/architecture.md` §7.2-7.3) — the
point of keeping FMEA is precisely to keep watching a risk the human has
already, correctly, accepted at the design-review level, not to treat
"accepted" as "no longer worth tracking."

**No entry required a design change during this pass** — same rule as
prior passes; FMEA-013/014's own driving findings (MISS-023's ACCEPTED-RISK
disposition, MISS-024's RESOLVED disposition) keep their existing status
from `validation/open-issues.md`, not re-litigated here.

**Condition 4 of the Design Complete Gate** is satisfied for this Rev 4
mechanical revision by this pass — independent of MISS-023's own
already-separate, already-closed human ACCEPTED-RISK sign-off (Design
Complete Gate condition 2, `validation/change-log.md` ECO-031), which
remains the gating condition for that specific decision, not this FMEA
review.

## Notes

- `Related IDs` cross-references `datasheets/evidence-log.md`,
  `validation/open-issues.md`, and `requirements/traceability-matrix.md` —
  an FMEA entry can be *driven by* a Reviewer finding, or can *drive* a new
  review focus; keep both directions linked instead of duplicating text.
- Review this register at least once per design revision before Design
  Complete (`docs/architecture.md` §8, condition 4).
- Track predictive validity in `docs/evaluation.md` ("FMEA Predictive
  Validity" metric): of the real-hardware issues eventually found, how many
  were already anticipated here?
