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
| FMEA-008 | MCU (U1) pin/peripheral assignment vs. real physical package pinout, verification process itself | A design document's pin assignment can pass both a checklist review (Hardware Reviewer) and an alternate-function-table cross-check (rubber-duck/ISS-011) while still being physically unbuildable, because "which alternate function does this pin name support" (the AF table) and "does this pin name exist as a bonded-out physical pin on this exact package" (the pin-definition/pinout-diagram table) are two separate tables in a manufacturer's datasheet, and every prior verification pass on this design checked only the first | Local: none yet (caught before any physical PCB layout or fabrication). System: if undetected until PCB layout or bring-up, a full board re-spin would be needed — no trace can connect to a pin that does not exist. Mission: N/A for a single bench prototype; would be a much more expensive discovery on a flight-committed design | 6 | A genuine, demonstrated blind spot: Component Selection, Circuit Design, 2 Hardware Reviewer cycles, 1 rubber-duck pass, and the Firmware Engineer's own independent AF-value confirmation (DS-MCU-062) all correctly verified the AF-table mapping (PB10/PB11 = I2C2 via some AF value) without ever independently cross-checking the separate physical-package-pinout table for this exact package variant | Only caught once a real KiCad project was built and real symbol/footprint data (sourced from ST's own official machine-readable pin database, not a distributor aggregator) was checked pin-by-pin against the design — the first time in this design's history that a *physical, tool-derived* pin table was cross-checked against the documented one, rather than another AF-table-only pass | 4 | 3 | 72 | Systemic lesson, not just a one-off fix: whenever a real KiCad project exists (or is being newly created) for a design, cross-check the schematic's MCU symbol's real, physically-bonded pin list against the design document's stated pin table as a distinct verification step from AF-table checking — this cycle empirically demonstrated that AF-table verification alone, however careful, does not catch a physical-pin-non-existence defect on a pin-count-reduced package | Hardware Lead (process-level; recommend making this an explicit Hardware Reviewer checklist item once a KiCad project exists for a design) | Open | ISS-014, DS-MCU-064/067, `validation/design-review.md` (this pass's entry) |

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
