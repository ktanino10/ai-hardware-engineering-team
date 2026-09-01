# Change Impact Matrix

For a given change (component swap, schematic change, etc.), makes the
cross-domain ripple effects explicit **before** the change is made, instead
of discovering them after the fact. Cross-reference by ID with
`validation/change-log.md` (ECO).

## Template

### For `<ECO-XXX>` — `<change short title>`

| Impact Domain | Impact Level (None/Low/Medium/High) | Cross-check Required? | Verification Result |
|---|---|---|---|
| Power (rail loading, `hardware/power-budget.md`) | | `<Y/N>` | |
| Thermal | | `<Y/N>` | |
| EMI/EMC | | `<Y/N>` | |
| Timing (interface/bus timing) | | `<Y/N>` | |
| Mechanical (fit, connectors, mounting; vibration if a rotating body is present — `docs/architecture.md` §12) | | `<Y/N>` | |
| Grounding | | `<Y/N>` | |
| BOM / lifecycle (does this affect other line items, e.g. shared connector) | | `<Y/N>` | |
| Requirements coverage (`requirements/traceability-matrix.md`) | | `<Y/N>` | |

## Rules

- Fill this in **before** approving an ECO that isn't purely cosmetic — this
  is what "impact analysis" in the ECO template (`validation/change-log.md`)
  actually refers to when the change is non-trivial.
- Any domain marked `Medium` or `High` impact needs its `Cross-check
  Required?` set to `Y` and an actual `Verification Result` before the
  associated ECO is approved by the human Chief Engineer.
- Link back to the ECO ID so `change-log.md` and this file stay in sync
  instead of drifting apart.

### For `ECO-007` — Rev 3 motor power architecture proposal

| Impact Domain | Impact Level (None/Low/Medium/High) | Cross-check Required? | Verification Result |
|---|---|---|---|
| Power (rail loading, `hardware/power-budget.md`) | High | Y | Verified in this pass: existing 3V3 rail has 500mA capability with ≈16.2mA worst-case logic load, leaving ≈483.8mA headroom; recommended motor+driver pair needs ≈12V-class input and ≈1.05A target motor current, so a separate motor rail is structurally required. |
| Thermal | Medium | Y | Partial only at architecture level: no converter/regulator part selected here, so no new rail thermal calculation is possible yet. Must be completed after human selects the source architecture and Component Engineer sources the new power-entry/conversion parts. |
| EMI/EMC | Medium | Y | Identified as relevant: motor switching/current transients can couple into logic if a shared source is chosen, especially under Option B (USB-C PD single source). Detailed mitigation remains Circuit Engineer scope after architecture selection. |
| Timing (interface/bus timing) | Low | N | No direct logic-interface timing change made in this pass; note preserved that motor-noise coupling must not regress REQ-010. |
| Mechanical (fit, connectors, mounting; vibration if a rotating body is present — `docs/architecture.md` §12) | Medium | Y | New connector/battery implications identified qualitatively for all options; exact board/enclosure impact deferred until a source architecture and connector family are chosen. |
| Grounding | Medium | Y | Shared return-path sensitivity identified, especially for single-source architectures; detailed grounding/layout verification deferred to Circuit Engineer once architecture is approved. |
| BOM / lifecycle (does this affect other line items, e.g. shared connector) | High | Y | Verified qualitatively: every option introduces at least one new sourced power-entry/control part class competing for the remaining ≈$53–68 REQ-503 headroom after motor+driver cost. Specific BOM impact awaits Component Engineer sourcing. |
| Requirements coverage (`requirements/traceability-matrix.md`) | High | Y | Verified: this pass exists specifically to satisfy REQ-108/109 by creating the architecture-decision record and separate motor-rail budget row, but final closure still depends on the human decision. |

### For `ECO-009` — Rev 3 Circuit Design (motor driver integration)

| Impact Domain | Impact Level (None/Low/Medium/High) | Cross-check Required? | Verification Result |
|---|---|---|---|
| Power (rail loading, `hardware/power-budget.md`) | High | Y | Verified: motor-rail row finalized with real J4/PJ-102AH + DRV10983 numbers, no placeholders remaining; existing 3V3 logic rail confirmed unchanged (still ≈16.2mA worst-case vs 500mA capability) per Option A's own intent. |
| Thermal | Medium | Y | DRV10983's fixed OCP (3 MIN/4 MAX A) and Lock Detection auto-retry (5s) mechanisms confirmed from primary datasheet sections (§8.3.2.3/§8.3.2.4); U5 (DRV10983) exact wattage not independently computed from RDS(on) this pass — flagged as a residual item, not blocking. |
| EMI/EMC | Medium | Y | Motor-noise-vs-IMU concern (REQ-010/204) addressed via explicit shared-ground-reference design decision (checklist item 15) and physical-separation guidance; not a full EMC pre-compliance analysis (REQ-401, out of scope this iteration as with Rev 2). |
| Timing (interface/bus timing) | Low | Y | New PWM (PA8/TIM1_CH1) and FG-capture (PA6/TIM3_CH1) timer assignments checked against Rev 2's existing timer/peripheral usage for conflicts; none found. |
| Mechanical (fit, connectors, mounting; vibration if a rotating body is present — `docs/architecture.md` §12) | High | Y | Checklist item 18 addressed for real (no longer N/A) — new connector (J4) location/height and motor+driver placement facts recorded for the Mechanical Lead's later handoff; motor mass/mounting-interface facts explicitly flagged as unconfirmed (not guessed) pending that phase. |
| Grounding | High | Y | Verified and explicitly documented (not left implicit): single shared ground reference required across the two power domains for PWM/FG/I2C1 signaling to function, with return-current/physical-separation guidance recorded for REQ-010/204. |
| BOM / lifecycle (does this affect other line items, e.g. shared connector) | Medium | Y | New parts added: J4 (Same Sky PJ-102AH barrel jack), D2 (STPS3L60 reverse-polarity Schottky) — both real, datasheet-grounded, single-supporting-part selections mirroring Rev 2's own J1/ESD-IC precedent (no full ≥3-candidate comparison required for this class of part). |
| Requirements coverage (`requirements/traceability-matrix.md`) | High | Y | REQ-007/008/108/109/110/111/112/404/204/307 all now have a real design-artifact reference in `hardware/schematic/bench-imu-01-design.md` — traceability-matrix rows to be updated from `Pending` once Hardware Reviewer's fresh pass clears. |

### For `ECO-023` — Mechanical Lead recomputes §8's REQ-403 physics table against ECO-022's corrected motor RPM

| Impact Domain | Impact Level (None/Low/Medium/High) | Cross-check Required? | Verification Result |
|---|---|---|---|
| Power (rail loading, `hardware/power-budget.md`) | None | N | No power/rail content in this change — this ECO consumes ECO-022's already-derived V_VCC(U5)/RPM figure as a given input; it does not re-touch the voltage-drop chain (F1/D2/U6) or any power-budget row itself. |
| Thermal | None | N | No thermal analysis, component, or rating touched. |
| EMI/EMC | None | N | No EMI/EMC analysis, layout, or component touched. |
| Timing (interface/bus timing) | None | N | No interface/bus/peripheral timing touched. |
| Mechanical (fit, connectors, mounting; vibration if a rotating body is present — `docs/architecture.md` §12) | High | Y | **Verified in this pass**: §8's REQ-403 flywheel-physics table and all surrounding safety-disposition prose recomputed end-to-end from this Mechanical Lead's own rotor inertia/radius data (I=4.5×10⁻⁵ kg·m², r=0.030m, §4.1/§4.4, unchanged) at the corrected RPM (point ≈25,180, range 25,060–25,280) — independently derived, not reused from Circuit Engineer's own illustrative scaling. New point figures: ω≈2636.8 rad/s, KE≈156.44 J (≈70.4× the 3000 RPM baseline), rim tip speed≈79.11 m/s (~285 km/h), peak centrifugal stress≈20.20 MPa. Disk-burst safety factor re-checked (not assumed unchanged): now ≈12.3–12.5× (point ≈12.4×), down from the superseded ~15.9× but still comfortably non-binding — disk-burst remains not the governing failure mode. **No `.scad` geometry changed** (this ECO corrects the load case the existing geometry is judged against, not the geometry itself). **§8.1 (the MISS-011/MISS-016-adjacent bounded wall-impact estimate) intentionally left unchanged this pass** — explicit staleness flag added at the end of §8 instead of a same-pass recompute, per this ECO's own explicitly bounded task scope; left as required follow-up work. |
| Grounding | None | N | No grounding path, return-current, or layout content touched. |
| BOM / lifecycle (does this affect other line items, e.g. shared connector) | None | N | No component added, removed, or re-specified; no BOM line item affected. |
| Requirements coverage (`requirements/traceability-matrix.md`) | Medium | Y | REQ-403's traceability-matrix row (line ~53) disposition status is **unchanged** by this ECO (still `Pending` human sign-off, unaffected either way) — this ECO does not itself close or newly fail REQ-403. However, that row's own prose still quotes the now-superseded "121.60J" figure ("cannot plausibly absorb the full disclosed 121.60J hazard energy"), the same staleness class as MISS-016 and `hardware/schematic/bench-imu-01-design.md` §7.5.11 — **flagged here as an additional observation, not corrected by this ECO** (editing `requirements/traceability-matrix.md` was outside this ECO's explicit task boundary; ownership of that cross-cutting document was not delegated to this pass). MISS-016 (HIGH, OPEN, `validation/open-issues.md`) itself remains OPEN and unmodified in status by this ECO; its own quantified Method 1/Method 2 shortfall figures are now understated (computed against the old, lower energy figure) pending their own follow-up recompute against §8's new ≈154.95–157.69 J figure — flagged explicitly in §8's own new text, not resolved here. |

### For `ECO-024` — Mechanical Lead recomputes MISS-016's own Method 1/Method 2 wall-margin analysis (§8.1) + repo-wide propagation of the ECO-022/023 correction

| Impact Domain | Impact Level (None/Low/Medium/High) | Cross-check Required? | Verification Result |
|---|---|---|---|
| Power (rail loading, `hardware/power-budget.md`) | None | N | No power/rail content touched — this ECO consumes the already-derived, already-verified corrected energy/rim-speed figures as a given input; it does not re-touch the voltage-drop chain. |
| Thermal | None | N | No thermal analysis, component, or rating touched. |
| EMI/EMC | None | N | No EMI/EMC analysis, layout, or component touched. |
| Timing (interface/bus timing) | None | N | No interface/bus/peripheral timing touched. |
| Mechanical (fit, connectors, mounting; vibration if a rotating body is present — `docs/architecture.md` §12) | High | Y | **Verified in this pass**: §8.1's Method 1/Method 2 wall-impact-energy-absorption tables, both reverse cross-checks, the fastener pull-out section, the confidence ledger, and the escalation flag all recomputed against the corrected 156.44J/79.11 m/s credible-worst-case — independently spot-verified by the Hardware Lead before this ECO was logged (arithmetic reproduced exactly). Shortfall widened as predicted (≈3.26–4.30× best case, was ≈2.53×; ≈1.7–3.6 orders of magnitude typical, was ≈1.6–3.4 orders) — closes the exact staleness flag ECO-023 itself raised. No `.scad` geometry changed. |
| Grounding | None | N | No grounding path, return-current, or layout content touched. |
| BOM / lifecycle (does this affect other line items, e.g. shared connector) | None | N | No component added, removed, or re-specified; no BOM line item affected. |
| Requirements coverage (`requirements/traceability-matrix.md`) | High | Y | **Closes the gap ECO-023's own entry above flagged and left open**: REQ-403's traceability-matrix row's stale "121.60J" quote is now corrected to the current figures (this ECO); REQ-405's row and `requirements/requirements.md` line 142 (MISS-019, partial) also corrected. MISS-016 (HIGH, `validation/open-issues.md`) status is unchanged by this ECO (still OPEN at the time this ECO was logged) — its own Issue/Rationale/Notes text is updated to the final, corrected Rev 3.4 figures, ready for the human's REQ-403 review with accurate numbers (see ECO-025 for the disposition that followed the same day). |

