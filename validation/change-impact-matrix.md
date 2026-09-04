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


### For `ECO-029` — Rev 4 free-rotation bearing mount (first Mechanical Design pass)

| Impact Domain | Impact Level (None/Low/Medium/High) | Cross-check Required? | Verification Result |
|---|---|---|---|
| Power (rail loading, `hardware/power-budget.md`) | None | N | No electrical component/rail touched — the bearing is a passive mechanical part. |
| Thermal | None | N | No thermal source added; existing motor/driver thermal picture unchanged. |
| EMI/EMC | None | N | No electrical/RF content touched. |
| Timing (interface/bus timing) | None | N | No interface/bus/peripheral timing touched. |
| Mechanical (fit, connectors, mounting; vibration if a rotating body is present — `docs/architecture.md` §12) | High | Y | **Verified in this pass**: real CG/tip-over analysis performed (rotating-assembly CG offset ≈14.3mm from bearing axis, 6.2× static tip-over margin at the chosen 120mm stand-plate diameter); a genuine manufacturability finding (internal overhang) disclosed with 3 alternatives considered; Independent Mechanical Review (Cycle 5) found the analysis itself sound but identified 2 new HIGH gaps this pass's own scope didn't originally cover (pinch-point/overhang hazard, cable-entanglement hazard) — see ECO-030 for the loop-back addressing these. |
| Grounding | None | N | No electrical grounding/return-current path touched. |
| BOM / lifecycle (does this affect other line items, e.g. shared connector) | Low | Y | Adds the bearing (already Component-Selection-approved, DS-BRG-001) as a new physical BOM line item; no existing electronic line item affected. |
| Requirements coverage (`requirements/traceability-matrix.md`) | High | Y | REQ-011/012/113/310/311 now have real design content to trace to (`bench-imu-01-enclosure.scad`/dimensional-spec §18/mechanical-interface Part C) — traceability-matrix.md rows themselves updated in the Hardware Lead's own follow-up pass (see ECO-030's own entry / same-session traceability update), not by this ECO's own Mechanical Lead author (out of that role's scope). REQ-407/408 remain open pending MISS-023/024's resolution. |

### For `ECO-030` — Rev 4.1 loop-back fix (pinch-guard + cable turn-limit) + friction-margin correction

| Impact Domain | Impact Level (None/Low/Medium/High) | Cross-check Required? | Verification Result |
|---|---|---|---|
| Power (rail loading, `hardware/power-budget.md`) | None | N | No electrical component/rail touched. |
| Thermal | None | N | No thermal source added. |
| EMI/EMC | None | N | No electrical/RF content touched. |
| Timing (interface/bus timing) | None | N | No interface/bus/peripheral timing touched. |
| Mechanical (fit, connectors, mounting; vibration if a rotating body is present — `docs/architecture.md` §12) | High | Y | **Verified in this pass, independently, twice**: the Mechanical Lead's own `pinch_guard()`/cable-turn-limit fix was re-verified by a fresh Independent Mechanical Review (Cycle 6), which re-derived the swept-radius correction (126.424mm), the guard's coverage/mass/collision-clearance, and J1/J4's cable-wrap arithmetic from raw geometry rather than trusting either prior report. Net result: MISS-024 closed (RESOLVED); MISS-023 remains OPEN/HIGH — a real, quantified residual safety gap (an 11.4mm unguarded band at the highest-velocity edge of the hazard zone, plus an unfastened/driftable guard) now reported to the human Chief Engineer as an explicit accept-or-iterate decision point, mirroring the REQ-403/MISS-016 precedent. Total system mass grew again (≈601.8g → ≈1173.4g, driven by `pinch_guard()`'s own ≈570.6g) — confirmed by both sub-agents to sit entirely on the stationary (non-bearing-loaded) side of the assembly, so the bearing's own friction-torque margin is unaffected by this specific growth (it remains keyed to the ≈405.55g rotating-assembly mass, not the ≈1173.4g total) — this was independently confirmed, not assumed. |
| Grounding | None | N | No electrical grounding/return-current path touched. |
| BOM / lifecycle (does this affect other line items, e.g. shared connector) | Low | Y | Adds cable ties (`cable_anchor_tab()`, generic commodity, no Evidence ID) as a new minor BOM item; no existing electronic line item affected. |
| Requirements coverage (`requirements/traceability-matrix.md`) | High | Y | MISS-029 (stale `bom/component-selection.md` friction-margin citation, discovered by Cycle 6) fixed same-pass by the Hardware Lead — 3 citations corrected to ≈21.5×/≈242× against the current ≈405.55g mass, independently re-verified by hand. REQ-407/408's traceability-matrix rows remain `Pending`, gated on MISS-023's own resolution — see the Hardware Lead's own traceability-matrix update this same session for the full row-by-row disposition. |

### For `ECO-031` — MISS-023 ACCEPTED-RISK disposition + Design Complete Gate (Rev 4 mechanical scope) GRANTED

| Impact Domain | Impact Level (None/Low/Medium/High) | Cross-check Required? | Verification Result |
|---|---|---|---|
| Power (rail loading, `hardware/power-budget.md`) | None | N | No electrical component/rail touched — this is a safety disposition + gate determination, not a design change. |
| Thermal | None | N | No thermal analysis, component, or rating touched. |
| EMI/EMC | None | N | No EMI/EMC analysis, layout, or component touched. |
| Timing (interface/bus timing) | None | N | No interface/bus/peripheral timing touched. |
| Mechanical (fit, connectors, mounting; vibration if a rotating body is present — `docs/architecture.md` §12) | High | Y | **Verified in this pass**: `pinch_guard()`'s design is unchanged by this ECO (this is a disposition of an already-built design, not a new geometry change); `validation/fmea.md` received a proper Rev 4 systemic-risk pass (FMEA-013 through 016) covering the guard's own ongoing drift risk, the cable-procedure human-factors risk, an honestly-disclosed dynamic-tip-over analysis gap, and the bearing-mount fastener-load gap — none of these were newly discovered by this ECO, all trace to already-open/already-dispositioned findings. |
| Grounding | None | N | No electrical grounding/return-current path touched. |
| BOM / lifecycle (does this affect other line items, e.g. shared connector) | None | N | No component added, removed, or re-specified by this ECO itself. |
| Requirements coverage (`requirements/traceability-matrix.md`) | High | Y | **Verified in this pass**: REQ-011, REQ-205, REQ-407 all moved `Pending` → `Verified — human-accepted disposition` (mirrors REQ-403's own exact wording precedent). REQ-013 remains `Pending`, explicitly disclosed as blocked on a not-yet-triggered future Firmware phase (not a mechanical-scope gap) — Design Complete is granted for Rev 4's **mechanical scope** specifically, not silently claimed as a full Electronics/Mechanical/Firmware completion the way Rev 3's ECO-025 was. |

### For `ECO-039` — Exploded-view parity fix (motor+flywheel ghosts, fastener callouts)

| Impact Domain | Impact Level (None/Low/Medium/High) | Cross-check Required? | Verification Result |
|---|---|---|---|
| Power (rail loading, `hardware/power-budget.md`) | None | N | No electrical rail touched — visualization-only. |
| Thermal | None | N | No thermal path touched. |
| EMI/EMC | None | N | Not applicable — no electrical change. |
| Timing (interface/bus timing) | None | N | Not applicable. |
| Mechanical (fit, connectors, mounting; vibration if a rotating body is present — `docs/architecture.md` §12) | None | N | No `.scad` geometry, dimension, or module body changed — the 2 new wrapper scripts duplicate existing, unchanged `reference_motor_flywheel()` primitives verbatim for a downstream Blender render only. Ghost-part world positions independently re-verified against the source `.scad` named variables (not eyeballed) before use. |
| Grounding | None | N | Not applicable. |
| BOM / lifecycle (does this affect other line items, e.g. shared connector) | None | N | No component added, removed, or re-specified. |
| Requirements coverage (`requirements/traceability-matrix.md`) | None | N | Does not reopen or affect any requirement row — the underlying Rev 4 mechanical Design Complete grant is unchanged. |

### For `ECO-040` — New Fusion-style OpenSCAD-sourced drafting sheets

| Impact Domain | Impact Level (None/Low/Medium/High) | Cross-check Required? | Verification Result |
|---|---|---|---|
| Power (rail loading, `hardware/power-budget.md`) | None | N | Not applicable — documentation-only. |
| Thermal | None | N | Not applicable. |
| EMI/EMC | None | N | Not applicable. |
| Timing (interface/bus timing) | None | N | Not applicable. |
| Mechanical (fit, connectors, mounting; vibration if a rotating body is present — `docs/architecture.md` §12) | None | N | No `.scad` geometry, dimension, or module body changed — new wrapper scripts feed the SAME existing assembled-frame module calls through `projection(cut=false)` (a rendering technique) instead of a camera. Auto-measured dimensions cross-checked against known CONFIRMED source values where available (e.g. `stand_plate`'s auto-measured ⌀56.0mm inner bore vs. `bmount_flange_ir`'s existing 28.0mm-radius value — exact match). |
| Grounding | None | N | Not applicable. |
| BOM / lifecycle (does this affect other line items, e.g. shared connector) | None | N | No component added, removed, or re-specified. |
| Requirements coverage (`requirements/traceability-matrix.md`) | None | N | Not applicable — new documentation artifact type, no requirement affected. |

### For `ECO-041` — New physics-demo SIMULATION animation + CONCEPT attitude-hold animation

| Impact Domain | Impact Level (None/Low/Medium/High) | Cross-check Required? | Verification Result |
|---|---|---|---|
| Power (rail loading, `hardware/power-budget.md`) | None | N | Not applicable — no electrical change. |
| Thermal | None | N | Not applicable. |
| EMI/EMC | None | N | Not applicable. |
| Timing (interface/bus timing) | None | N | Not applicable. |
| Mechanical (fit, connectors, mounting; vibration if a rotating body is present — `docs/architecture.md` §12) | None | N | No `.scad` geometry, dimension, or module body changed — both animations reuse the existing assembled-position STL pipeline unmodified. All physics numbers rendered are copied verbatim from `bom/component-selection.md`'s own already-approved ESTIMATE (not re-derived); the concept-demo's reference-mark position was measured directly from the existing `assembled-base-assembly.stl` binary, not guessed. |
| Grounding | None | N | Not applicable. |
| BOM / lifecycle (does this affect other line items, e.g. shared connector) | None | N | No component added, removed, or re-specified. |
| Requirements coverage (`requirements/traceability-matrix.md`) | None | N | Does not implement or claim any closed-loop control capability — REQ-009/REQ-014's existing anti-scope status is unaffected; REQ-011's single-axis figure is only read (cited), not changed. |

### For `ECO-042` — Merge `origin/main` + cross-branch ECO-ID renumbering (bookkeeping only)

| Impact Domain | Impact Level (None/Low/Medium/High) | Cross-check Required? | Verification Result |
|---|---|---|---|
| Power (rail loading, `hardware/power-budget.md`) | None | N | Not applicable — pure ID rename plus a git merge of unrelated `main` content (firmware-flashing tooling datasheets/guide); no electrical change. |
| Thermal | None | N | Not applicable. |
| EMI/EMC | None | N | Not applicable. |
| Timing (interface/bus timing) | None | N | Not applicable. |
| Mechanical (fit, connectors, mounting; vibration if a rotating body is present — `docs/architecture.md` §12) | None | N | No `.scad` geometry, dimension, or module body touched by this entry — confined to renumbering this branch's own not-yet-merged `ECO-038/039/040` (+ `ECO-040a/040b`) to `ECO-039/040/041` (+ `ECO-041a/041b`) across every citing file, resolving a genuine collision with `main`'s own real `ECO-038`. `tools/check_id_uniqueness.py` re-run after the merge: 486 IDs, 0 duplicates. |
| Grounding | None | N | Not applicable. |
| BOM / lifecycle (does this affect other line items, e.g. shared connector) | None | N | No component added, removed, or re-specified. |
| Requirements coverage (`requirements/traceability-matrix.md`) | None | N | Not applicable — no requirement touched. |

### For `ECO-052` — Resolve MISS-034: grow Bench-IMU-01 enclosure to the real 150×95mm PCB

| Impact Domain | Impact Level (None/Low/Medium/High) | Cross-check Required? | Verification Result |
|---|---|---|---|
| Power (rail loading, `hardware/power-budget.md`) | None | N | Not applicable — no electrical/power change. Bare-board mass grew (A5) but power budget is unaffected (mass, not electrical loading). |
| Thermal | None | N | Not applicable — no thermal path changed. |
| EMI/EMC | None | N | Not applicable. |
| Timing (interface/bus timing) | None | N | Not applicable. |
| Mechanical (fit, connectors, mounting; vibration if a rotating body is present — `docs/architecture.md` §12) | **High** | Y | **Verified in this pass**: the entire mechanical scope is the subject of this ECO. `pcb_length`/`pcb_width`/`mount_holes`/`tab_positions` corrected to the real board; full parametric cascade re-verified via live OpenSCAD evaluation (not hand-derivation); all 5 STLs re-exported and re-measured (`trimesh`); `containment_cap()`/`stand_plate()` independently confirmed formula-independent of the resize (byte-identical STL re-export). **Vibration/rotating-body-specific**: the rotating assembly's own max swept radius grew 126.424mm→176.259mm (confirmed 2 independent methods), degrading MISS-023's pinch-guard coverage 77.7%→35.0% — re-opened for fresh human review rather than silently carried forward or silently re-decided; `cable_service_loop_min` fixed directly (no-tradeoff item). A real, pre-existing (unrelated) `pinch_guard()` manufacturing-geometry bug (MISS-036) was also found and fixed this pass. CG/tip-over analysis (§18.3) explicitly NOT re-derived — disclosed gap (MISS-038), not silently assumed fine. |
| Grounding | None | N | Not applicable — no electrical change. |
| BOM / lifecycle (does this affect other line items, e.g. shared connector) | None | N | No component added, removed, or re-specified — enclosure geometry only. |
| Requirements coverage (`requirements/traceability-matrix.md`) | **Medium** | Y | **Verified in this pass**: REQ-308 (envelope vs. soft ~150mm ceiling) row updated — X now also exceeds the ceiling (new), Y's own overshoot grew from 13.7% to 43.7%; REQ-306 (flywheel rotation clearance) and REQ-403 (containment geometry) rows re-confirmed unaffected (formula-independent of the PCB resize, independently verified via STL re-export byte/bbox comparison, not merely re-read from a comment); REQ-407(b) (pinch-point mitigation) row updated to reflect the re-opened MISS-023 coverage-percentage change. REQ-304 (≥4 mounting holes) remains satisfied by the real 4-hole pattern. |
