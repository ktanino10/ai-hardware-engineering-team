# Bench-IMU-01 — Schematic-Equivalent Design Document

**Author**: Circuit Engineer (AI agent) · **Date**: 2026-08-31, revised 2026-09-01, **Rev 2 Design Complete 2026-09-03** (`validation/change-log.md` ECO-005), **pin-bonding correction adopted** (ECO-006, see the "Rev 2, corrected" changelog entry below), revised 2026-09-04, revised 2026-09-06, revised 2026-09-08, **revised 2026-09-02 — F2 added (ISS-032 loop-back fix, PCB Engineer at explicit Chief Engineer direction, see §7.5.9 and the parts-list table)** · **Status**: **Revised (Rev 5)** — Motor Driver + Reaction Wheel subsystem (§7.5) added in Rev 3 and iterated through two loop-back rework cycles (Rev 4: F1 PTC fuse + binding 9.0–13.0V VM_MOTOR envelope + SPEED pulldown, addressing Independent Review Cycle 3's 5 HIGH findings; Rev 5: U6 TPS26631PWPR supervisory controller, closing the residual continuous-OVP/power-up-sequencing gap), **plus a corrected MCU pin-identity fix (ISS-027)**: no separate VDDA pin (combined with VDD at physical pin 4), no VBAT pin at all on this package, one combined VSS/VSSA pin (physical pin 5), NRST sharing physical pin 6 with GPIO PF2, and the IMU's I2C2 bus on **PA11(SCL)/PA12(SDA)** rather than the non-existent PB10/PB11. This more complete fix was independently surfaced by this repository's first real KiCad project (`hardware/schematic/bench-imu-01/`, tool-verified via `kicad-cli` ERC/netlist export) and is adopted here **in place of** this branch's own earlier, narrower attempt at the same defect class (previously tracked on this branch as "Rev 6"/ISS-026, I2C2 pins only — see the "Rev 2, corrected" entry below for why that narrower fix is superseded, not kept alongside this one). See §19 for the dedicated pin-correction handoff. **Plus one further loop-back fix, 2026-09-02**: F2, a second PTC resettable fuse in J4's ground return leg, closing Hardware Reviewer finding ISS-032 (HIGH) — narrowed the D2 safety-argument claim to what it actually covers (external reverse-polarity only, not an internal J4 pin-mapping error) and added independent protection for the case D2 cannot cover; see the corrected §7.5.9 text and parts-list row below. Authored by the PCB Engineer, not the Circuit Engineer, at the explicit direction of the human Chief Engineer coordinating this cross-branch task — a deliberate, disclosed exception to this project's normal role boundary (PCB Engineer does not normally redesign circuit topology), not a silent scope violation. **Ready for a fresh Hardware Reviewer pass**: a first review of the Rev 3–5 motor subsystem, a fidelity-scoped re-review of the corrected pin areas (not a full Design-Complete re-litigation — see ISS-027), and independent verification of the F2 fix specifically (not yet independently reviewed as of this edit).

## Revision changelog

**Rev 5 (2026-09-08)** — Circuit Engineer loop-back rework implementing
`bom/component-selection.md`'s newly human-approved "Motor-Rail Supervisory
Controller" recommendation, per `.github/agents/circuit-engineer.agent.md`
("Process" steps 1–7) and the explicit task directive to wire U6 = TI
TPS26631PWPR between the existing F1→D2→D3 protection stage and U5 VCC.

- **U6 = TPS26631PWPR (HTSSOP-20/"PWP") added** as a series load-switch/eFuse
  between D3 and U5 VCC, implementing the load-switch function §7.5.10 had
  previously only flagged (Rev 4). Confirmed Component-Engineer-approved
  before use (`.github/agents/circuit-engineer.agent.md` "Process" step 1) —
  see `bom/component-selection.md`'s Approval table, both the Component
  Engineer's proposal row (2026-09-08) and the human Chief Engineer's
  "Approved" row.
- **New EN/SHDN pull-down R11 = 10 kΩ** added from U6's SHDN pin to GND,
  inverting the part's internal SHDN pull-up (defaults the device **ON**) to
  the required default-**OFF**/fail-safe direction per REQ-403 and this
  document's own prior §7.5.10 spec. Primary sizing basis is TI's own
  **guaranteed** Electrical Characteristics spec — I(SHDN) leakage current
  max = 10 µA at V(SHDN) = 0 V, plus TI's own explicit application-note text:
  "To assert SHDN low, the pulldown must have sinking capability of at least
  10 µA" (SLVSE94G §8.3.13) — not on the internal pull-up's own resistance
  value, which is **not a guaranteed datasheet spec** (see next bullet).
  R11 = 10 kΩ gives a worst-case V(SHDN) ≈ 100 mV at the guaranteed 10 µA
  leakage max, ≈8× below the guaranteed V(SHUTF) = 0.8 V shutdown-confirm
  threshold and ≈20× below the guaranteed V(SHUTR) = 2 V enable threshold —
  both from TI's own Electrical Characteristics table. See §7.5.10 for the
  full derivation.
- **SHDN internal pull-up resistance discrepancy found and reconciled**:
  the task's own framing (independently re-confirmed by the human via a
  fresh web search this session) cites "a genuine internal ≈440 kΩ EN
  pull-up." This session's own direct visual read of TI's datasheet Figure
  8-1 functional block diagram shows **"1 MegΩ"** at the SHDN node — and
  this matches the pre-existing Component-Engineer-recorded evidence row
  **DS-PROT-013** (citing a TI E2E forum post) and the pre-existing
  Component Engineer datasheet metadata file, both of which already state
  1 MΩ, not 440 kΩ. **Neither figure is a guaranteed Electrical
  Characteristics table spec** — TI's datasheet shows 1 MΩ only in the
  functional (illustrative) block diagram, with no formal min/typ/max table
  row for this resistance — so this is not treated as a blocking
  discrepancy: R11's primary sizing basis (above) does not depend on either
  figure, and R11 = 10 kΩ dominates comfortably under **both** candidate
  values (440 kΩ → ≈44× the pull-down; 1 MΩ → ≈100× the pull-down). Flagged
  for Hardware Reviewer awareness; see §16 new item.
- **New OVP/UVLO resistor divider R12 = 887 kΩ / R13 = 60.4 kΩ / R14 =
  88.7 kΩ** (all E96, 1%) added, referenced to §7.5.9's 9.0–13.0 V J4 input
  envelope, per TI's own datasheet divider architecture (SLVSE94G §9.2.2.2–
  9.2.2.5): IN_SYS/IN —[R12]— UVLO pin —[R13]— OVP pin —[R14]— GND. Trip
  points computed from TI's own guaranteed reference voltages (V(UVLOR) =
  1.176/1.200/1.224 V, V(OVPR) = 1.176/1.200/1.224 V min/typ/max): UVLO
  rising trips at 8.17–8.51 V (worst-case 5.49% below the 9.0 V floor), OVP
  rising trips at 13.74–14.30 V (worst-case 5.67% above the 13.0 V ceiling).
  Divider string current 8.69–12.55 µA across the envelope, 2.9×–4.2× above
  TI's own explicit "must be 20× the leakage current" design floor (SLVSE94G
  §9.2.2, using the guaranteed ±150 nA I(UVLO)/I(OVP) leakage spec). Full
  derivation, hysteresis (falling-threshold) behavior, and full-stack
  (reference **and** resistor tolerance both adverse) worst-case figures in
  §7.5.10.
- **New R(ILIM) = R15 = 3.57 kΩ** (E96, 1%) sets U6's overload trip point to
  4.69–5.40 A (min–max), clearing U5's own 3–4 A OCP with margin and sitting
  below F1's 10 A PTC trip — a three-tier protection hierarchy (U5 OCP → U6
  overload → F1 PTC). Per TI's own R(ILIM) equation and tested-value table
  (SLVSE94G §7/§9).
- **New dVdT capacitor C17 = 22 nF** sets U6's inrush-current-limiting ramp
  rate, sized against **this design's own real downstream capacitance**
  (C10 = 10 µF, reused — no new output capacitor added) rather than TI's own
  1 mF worked-example scenario, which does not transfer to this design
  (flagged explicitly to prevent a copy-the-datasheet-example error). Gives
  ≈22 mA worst-case inrush (negligible) and adds a fixed ≈1.83 ms UVLO/OVP
  turn-on delay (PGTH tied low, §7.5.10).
- **New input bypass capacitor C16 = 1 µF** added at U6 IN/IN_SYS, per TI's
  own explicit recommendation ("TI recommends a minimum of 1 µF for C(IN)
  ... to limit the slew rates during surge testing," SLVSE94G §9.2.2.5.1) —
  a new component this revision (not foreseen when §7.5.10 was first
  flagged in Rev 4).
- **MCU enable pin PA9 committed** (final, not tentative) as U6's SHDN
  drive — the same pin this document's own Rev 4 §11 note had already
  earmarked tentative. Re-confirmed still free this revision before commit;
  free-GPIO count drops from 16 to 15 (§11).
- **F1 swapped: Littelfuse 30R500U → 30R500UF.** Independently confirmed
  this session (fresh web search) to be the manufacturer's own direct
  replacement for the now-obsolete 30R500U flagged in **DS-PROT-009** —
  same "30R Series Radial Leaded" datasheet PDF, same electrical spec table
  (Ihold=5A/Itrip=10A/Vmax=30Vdc/Imax=40A), same package/footprint, RoHS3-
  compliant construction, and confirmed **Active**/orderable on
  littelfuse.com. Parts list, net list, and the datasheet metadata record
  (renamed in place: `datasheets/littelfuse_30r500u_rev-unknown.md` →
  `datasheets/littelfuse_30r500uf_rev-unknown.md`) all updated; no
  electrical analysis elsewhere in this document changes as a result
  (§7.5.9's F1 protection-envelope analysis is unaffected — same part,
  different orderable suffix).
- **`hardware/power-budget.md` updated**: U6 adds a negligible IQ(ON) =
  1.38/1.7 mA (typ/max) or IQ(OFF) = 21/60 µA (typ/max) draw on VM_MOTOR
  (device-state-dependent, not additive) plus ≈8.7–12.6 µA divider bias
  current; R11 adds ≈330 µA on the 3V3 rail whenever PA9 drives SHDN high.
  Both rails' margins remain effectively unchanged at the stated precision;
  see `hardware/power-budget.md` for the updated figures and a new U6
  thermal cross-check (ΔTJ ≈ 10–16 °C at ≤3 A worst-case, comfortably below
  T(TSD) = 165 °C).
- **New self-check subsections** added to §14 ("Rev 5 motor-domain
  re-check") and §15 ("Re-self-check after Rev 5 fixes") covering the new
  U6 stage against this document's own 18-item mandatory-check list and the
  Hardware Reviewer's 16-item checklist respectively.
- **§16 UNKNOWNs**: item 22 (the flagged supervisory controller) annotated
  **RESOLVED/IMPLEMENTED**; four new residual items added (SHDN pull-up
  discrepancy, OVP worst-case-corner trip point, PGTH/MODE design choices'
  interaction with ISS-021's still-undecided firmware latch policy, and the
  dVdT/C(OUT) sizing basis) — none of these block handoff, all flagged for
  Hardware Reviewer awareness.
- **ISS-020/ISS-021 explicitly NOT resolved by this revision** — per the
  task's own explicit instruction, these remain genuine firmware-policy
  gaps (§7.5.11/§7.5.12, unchanged this revision). U6's SHDN pin (driven by
  the now-committed PA9) gives firmware a real, physical enforcement point
  for ISS-021's eventual latch — cycling SHDN also resets a latched-off U6
  fault condition (TI SLVSE94G Table 5-1, SHDN pin description) — but the
  policy of *when* to latch is firmware's decision alone, not implemented
  here.
- New Evidence IDs **DS-PROT-023 through DS-PROT-033**
  (`datasheets/evidence-log.md`) and new change record **ECO-012**
  (`validation/change-log.md`).

**Rev 4 (2026-09-06)** — Circuit Engineer loop-back rework addressing
`validation/design-review.md` Cycle 3 findings (Hardware Reviewer +
rubber-duck, both reviewing Rev 3's Motor Driver + Reaction Wheel
subsystem in parallel), per `.github/agents/circuit-engineer.agent.md`
("When you receive Hardware Reviewer findings... address every CRITICAL
and HIGH finding explicitly — do not silently drop one"). Cycle 3 returned
**CONDITIONAL, 0 CRITICAL, 5 HIGH** (ISS-014, ISS-015, ISS-019, ISS-020,
ISS-021) — all 5 are addressed below; **none silently dropped**. ISS-016/
017/018 (LOW) and ISS-022/023 (MEDIUM) are **not** among the 5 HIGH
findings routed to this rework cycle and are untouched. Per this
document's own established precedent (Rev 2/Rev 3), `bom/component-
selection.md`, `requirements/requirements.md`, `hardware/power-
architecture.md`'s Decision table, `hardware/mechanical-interface.md`,
`validation/open-issues.md`, and `validation/design-review.md` are
**not** touched by this agent; `hardware/power-budget.md` **is** updated
(F1/R10 numeric effects, plus the ISS-014 cross-document reconciliation
the Hardware Reviewer found); `datasheets/evidence-log.md` **is**
appended to (one new row, **DS-PROT-006**, for the new F1 part —
ISS-015's own evidence needs are already met by existing rows
DS-MTR-068/069/071, cited directly below, not re-derived from scratch);
`validation/change-log.md` gains a new **ECO-010** row.

- **ISS-014 (HIGH, fixed — scope/documentation correction; residual
  flagged)** — §7.5.2's 2S/3S paragraph is rewritten. The prior framing
  ("only a freshly-charged 2S pack... clears UVLO with any margin") is
  corrected: the Hardware Reviewer independently re-derived the same
  source figures (D2 VF=0.53V typ/0.62V max, DS-PROT-005; U5
  VUVLO_R=7/7.4/8V min/typ/max, DS-MTR-057) and found 2S actually fails
  **at the typical corner** (6.87V < 7.4V typ) — a likely, not merely
  worst-case, outcome — and also found this document's own prior wording
  disagreed with `hardware/power-budget.md`'s Rail Margin Summary on the
  identical scenario. Both documents now state one precise,
  corner-explicit conclusion: **3S-only is recorded as this design's
  binding practical constraint**, not a soft recommendation, and the
  typical-corner failure is stated as the headline (not the worst-case
  corner alone). New §7.5.9's F1 (PTC fuse, below) adds further series
  resistance, narrowing the 3S margin from ≈0.38V to ≈0.32V at the
  near-cutoff corner — still adequate, quantified explicitly rather than
  left unstated. **Flagged, not self-resolved** (per this agent's own
  "Out of scope" instructions): (a) propagating the 3S-only constraint
  into `bom/component-selection.md`/`requirements/requirements.md` — both
  outside this agent's edit scope, routed to Hardware Lead; (b) the
  Hardware Reviewer's own alternate-fix suggestion, evaluating a
  lower-VF ideal-diode/ORing-FET reverse-polarity topology if 2S support
  is later required — an architecturally significant part-class change,
  routed to Component Engineer via Hardware Lead, not self-selected.
- **ISS-015 (HIGH, fixed — external pulldown added; residual flagged)** —
  §7.5.5's prior "deliberate non-addition of an external pulldown" stance
  is reversed, citing the Hardware Reviewer's own primary-source findings
  directly rather than re-deriving them: **DS-MTR-071** (new evidence row
  added by the Hardware Reviewer this cycle) decodes U5's factory-default
  EEPROM value (Table 8, register 0x2B=0x0C) to `SpdCtrlMd`=0=**analog
  mode**, and §8.4.5.2 confirms analog mode is fully active, not inert,
  out of reset — directly correcting this document's own superseded
  reasoning (**DS-MTR-068**, qualified in place by the Hardware Reviewer,
  2026-09-05). The same review additionally found that the internal
  `RPD_SPEED_SL` pulldown this document previously cited as a partial
  mitigant (**DS-MTR-069**) is documented **only** under the primary
  datasheet's "SLEEP MODE (DRV10983Z)" table section — the plain
  **DRV10983** actually specified in this design (no sleep-pin/Zener
  component populated, confirmed against §13's own parts list) has a
  separate "STANDBY MODE (DRV10983)" section with **no pulldown parameter
  listed at all**, a more specific weakening of this document's prior
  "partial mitigant" framing than previously acknowledged. New **R10 =
  1kΩ 0603** resistor, SPEED net to common ground (§8) — sized (ASSUMPTION,
  no specific SPEED-pin leakage figure exists in the datasheet) to hold
  SPEED many multiples below VANA_ZS=100mV against realistic pin
  leakage/coupling current, independent of MCU firmware state. This is an
  explicit, acknowledged deviation from TI's own Table 11 reference
  circuit (which lists no external SPEED pull component, per DS-MTR-071's
  own cross-check) — justified because that reference circuit assumes a
  single always-alive host system, which this design's dual-independent-
  power-domain (Option A) architecture does not have. **Flagged, not
  self-resolved**: (a) a supervisory load switch gating U5's own VCC on
  the MCU domain's power state — new **§7.5.10** specifies the
  function/ratings needed (architecturally significant, routed to
  Component Engineer via Hardware Lead, not self-selected); (b) REQ-403's
  own explicit human-safety-review gate applies regardless of the
  technical path chosen — flagged for that review, not self-granted here.
- **ISS-019 (HIGH, fixed — binding envelope + PTC fuse added; residual
  flagged)** — New **§7.5.9** defines a binding J4 input envelope —
  **9.0–13.0V** (3S near-cutoff to 3S full-charge + ~3% headroom),
  explicitly excluding 4S packs or an incorrectly-set bench supply —
  where none existed before (the prior "~12V-class" framing was
  descriptive, not a bound). New **F1 = Littelfuse 30R500U** radial-leaded
  PTC resettable fuse (**DS-PROT-006**), placed J4(+) → **F1** → D2 → D3
  → U5 VCC, adds coordinated upstream fault containment against
  short-circuit-level fault current that none of J4/D2/D3/U5's own
  protection previously provided upstream of U5's own internal,
  downstream-only OCP. Honestly scoped: F1's own trip current
  (Itrip=10.00A) exceeds J4's own 5.0A connector rating — its real
  protective value is against genuine short-circuit-level faults, not a
  precisely-matched current limiter for J4 itself; this gap is why a true
  input eFuse/active-OVP stage is flagged, not claimed closed, below. D3
  (SMBJ16A, 16.0V standoff/26.0V max clamp, unchanged) remains correctly
  scoped as a transient-only backstop, not a continuous-overvoltage
  bound — this document does not overclaim TVS capability. **Flagged, not
  self-resolved**: (a) true hardware-enforced continuous input
  over-voltage lockout needs an active comparator+switch stage — unified
  with ISS-015's flagged supervisory controller in the new §7.5.10 rather
  than recommending a second, redundant part; (b) recording the
  9.0–13.0V envelope in `validation/bring-up-procedure.md`'s future
  motor-rail section — that file is not edited by this agent (ambiguous
  ownership), flagged instead.
- **ISS-020 (HIGH, addressed — no schematic-level fix exists; firmware
  requirement flagged)** — New **§7.5.11** records the finding as-is (a
  genuine premise-level gap, not a circuit defect): REQ-007's "≥3000 RPM"
  has only ever been a functional floor; M1's own no-load speed
  (DS-MTR-018 corrected/DS-MTR-080, §7.5.13, ≈20,000 RPM up to a
  corrected credible worst-case of ≈25,180 RPM) is 6.7–8.4× that floor,
  with stored rotational energy ≈44–70× higher at no-load than at the
  3000 RPM target. No component, connection, or protection circuit in this
  design's own scope can bound a *commanded* maximum speed — that is a
  firmware policy question (a maximum operating/fault speed, a commanded
  ramp-rate limit, and a tach-supervised overspeed shutdown using the
  already-wired FG signal, §7.5.4), not a hardware one, and this document
  does not invent one. Explicitly **not** the REQ-009-prohibited
  closed-loop attitude-control logic — a bounded safety cutoff is a
  different class of behavior than attitude control, the same way an
  overcurrent shutdown is not "control" in the excluded sense. **Flagged
  for Hardware Lead mediation**, ties to REQ-403's safety-critical
  human-review gate: this document proposes ~6000 RPM (2× the floor) only
  as a numeric anchor for discussion, not a decision — the actual maximum
  is Firmware/Mechanical Lead's/the human's call, and must in turn feed
  Mechanical Lead's flywheel/containment design as a real input.
- **ISS-021 (HIGH, addressed — no schematic-level fix exists; firmware
  requirement flagged, hardware enabler flagged)** — New **§7.5.12**
  records the finding: U5's own three protection mechanisms (OCP/
  DS-MTR-058, Lock Detection/DS-MTR-059, Thermal Shutdown/DS-MTR-060) are
  all auto-recovering/auto-retrying by design — none latch — so
  REQ-404's own "shutdown behavior to prevent sustained overheating" is
  not actually satisfied by relying on them alone: a persistent mechanical
  jam would cause repeated fault-current pulses and repeated
  auto-restarts indefinitely, each dissipating real heat (D2 alone
  dissipates ≈1.86W at a 3A/0.62V worst-case fault current, DS-PROT-005)
  with no design-level cutoff that ever actually stops trying. No passive
  circuit change closes this gap — it requires a **firmware-level
  latched-fault policy** (count consecutive Lock Detection retries,
  Status register bit4/MtrLck, within a rolling window over the
  already-wired I2C1 bus, §7.5.4; force SPEED to a safe/stopped state
  after a threshold; require a deliberate re-arm) — flagged as a new
  firmware requirement, not implemented here (REQ-009 fence). **Hardware
  note, not a fix**: the same §7.5.10 flagged supervisory switch (ISS-015)
  could additionally serve as the actual VCC-cutting enforcement
  mechanism once firmware declares a latched-fault condition —
  cross-referenced, not a third redundant part. REQ-404 is a "Should," not
  a "Must" — noted, but this does not reduce the obligation to address
  this HIGH finding explicitly.
- **New §7.5.9–§7.5.12** — appended after §7.5.8, using this document's
  own established decimal-numbering, append-don't-renumber convention
  (Rev 3's own precedent); §7.5.1–§7.5.8 are otherwise unchanged by this
  addition (only §7.5.2 and §7.5.5 receive the in-place corrections above,
  and §7.5.8's closing paragraph is updated to reflect the severity
  correction and the new §7.5.10 cross-reference).
- **Power budget (REQ-109)** — `hardware/power-budget.md`'s VM_MOTOR
  Supply Capability row gains F1; its Subsystem Load table gains R10's own
  negligible worst-case 3V3-domain load (≈3.3mA, an atypical/instantaneous
  100%-duty-cycle-held case, the same treatment already used for the
  I2C pull-ups' own worst-case row); its Rail Margin Summary's 2S/3S row
  is rewritten to state the same corrected, corner-explicit conclusion as
  this document's own §7.5.2 — the cross-document inconsistency the
  Hardware Reviewer found is now closed.
- **§11/§12/§13** — corrected phrasing (self-check catch): R10 and F1 are
  *not* added as new rows to §11's MCU pin-assignment table — neither
  consumes an MCU pin, both being passive, in-line/shunt parts on
  already-wired nets — §11 instead gains an explanatory "Rev 4 note"
  confirming this and stating the free-GPIO count (16) is therefore
  unchanged. §12's net list does gain both: F1 is inserted into the
  existing VM_MOTOR path, and a new SPEED-pulldown branch is added for
  R10. §13's parts list gains new **R10**/**F1** rows.
- **§16** — items 14 and 17 are annotated in place per this document's
  own established convention (§16's own "Annotation convention," introduced
  in Rev 3); new items 22–26 are appended for this revision's own residual
  flags (the §7.5.10 supervisory switch, the §7.5.9 continuous-OVP gap,
  the `bring-up-procedure.md` envelope note, and the two new firmware
  requirements from ISS-020/021).
- **Self-check**: re-run against Hardware Reviewer checklist items 1, 3,
  6, 7, 8, 9, and 10 (§15) — items 1/10 map to ISS-014's UVLO/
  power-sequencing correction, items 6/7/10 to ISS-015's pulldown/
  supervisory-switch flag, item 9/3 to ISS-019's protection stage. See
  §14/§15 for the item-by-item record.

**Rev 3 (2026-09-04)** — Circuit Engineer addition of the Motor Driver +
Reaction Wheel subsystem, authorized by `validation/change-log.md` ECO-008
(both HITL gates granted 2026-08-31: component approval of T-Motor
MN2206-13 KV2000 + TI DRV10983 in `bom/component-selection.md`, and Option
A power-architecture approval in `hardware/power-architecture.md`). This is
an **addition cycle**, not a fix cycle — nothing Design-Complete in Rev 2 is
reopened. New content is concentrated in a new **§7.5** (inserted between
the existing §7 LED block and §8 Grounding, using decimal numbering so
every existing §8–§18 anchor/cross-reference in this document and in
`validation/`, `datasheets/`, and other agents' files stays valid), with
necessary additive touches to §1, §2, §5, §8, §9, §10, §11, §12, §13, §14,
§15, §16, §17, and §18 as flagged below. `hardware/power-budget.md`'s
placeholder Rev 3 motor-rail row is finalized alongside this revision (see
its own changelog). Per this design's own precedent, `bom/component-
selection.md`, `requirements/requirements.md`, `hardware/power-
architecture.md`'s Decision table, `hardware/mechanical-interface.md`, and
`validation/open-issues.md`/`validation/design-review.md` are **not**
touched by this agent; `datasheets/evidence-log.md` **is** appended to
(consistent with this agent's mandate to cite Evidence IDs), gaining rows
DS-MTR-052 through DS-MTR-070, DS-MCU-069 through DS-MCU-071, DS-CONN-005,
and DS-PROT-004/005 (25 new rows, 282 total, zero duplicates).

- **New power input (REQ-108)** — A second, independent, dedicated
  ~12V-class motor power input is added: **J4** (Same Sky PJ-102AH barrel
  jack, DS-CONN-005) → **D2** (ST STPS3L60 Schottky, series
  reverse-polarity protection, DS-PROT-005) → **D3** (Littelfuse SMBJ16A
  TVS, transient/surge protection, DS-PROT-004) → **U5** (TI DRV10983)
  VCC. Chosen the same way Rev 2 chose J1/the ESD IC (§3.1/§3.2
  precedent): a single, real, datasheet-grounded part per supporting role,
  no ≥3-candidate comparison, per this project's own established
  threshold for supporting (non-primary-BOM) parts. This rail is
  electrically independent of the existing USB-derived 5V/3.3V logic
  rail — Option A's fault-isolation intent (`hardware/power-
  architecture.md`) is preserved; see §7.5 and §8 (grounding) for how the
  two domains still share a *signal-reference* ground without being
  power-tied.
- **New MCU pin allocation (REQ-007/110, REQ-008/112)** — Five pins are
  newly consumed from Rev 2's free-GPIO inventory (§11): **PA8**
  (TIM1_CH1, SPEED/PWM output, HIGH confidence), **PA6** (TIM3_CH1 input
  capture, FG tach input, HIGH confidence), **PB1** (GPIO push-pull
  output, DIR, HIGH confidence), **PB6**/**PB7** (I2C1_SCL/SDA, HIGH
  confidence) — real DRV10983 pinout confirmed pin-by-pin
  (DS-MTR-052): no dedicated enable or fault pin exists on this part (a
  generic H-bridge driver pin set was **not** assumed); enable/disable is
  via the SPEED command itself (zero = stop), and fault visibility is
  I2C-register-only or inferred from FG held high. I2C1 (PB6/PB7),
  previously recorded as fully free surplus margin from ISS-011's Rev 2
  correction, is now consumed — reframed from "optional future tuning"
  to **required for motor-parameter commissioning** (Rm phase-resistance
  and Kt BEMF-constant registers must be programmed for this specific
  motor pairing to commutate correctly at all — DS-MTR-070) and for
  setting `SpdCtrlMd`=1 (PWM mode) for REQ-007 (DS-MTR-068). Wiring the
  bus is this design's job; programming those values is a firmware/
  commissioning task (REQ-009 fence preserved).
- **Grounding (checklist item 15/11; REQ-010, REQ-204)** — Addressed
  explicitly, not left implicit: §8 is rewritten for a two-domain
  treatment. The two power rails (existing USB-derived logic, new
  dedicated motor input) remain independently sourced per Option A, but
  **must** share one common ground reference at a single star point for
  the PWM/FG/I2C1 signals between MCU and driver to be valid logic
  signals at all. Return-current routing and REQ-010/REQ-204 noise
  isolation from the IMU are discussed as their own consideration, not
  bundled silently into the rail-independence statement.
- **Protection (REQ-111/404)** — DRV10983's real protection mechanisms
  confirmed from its own datasheet (5 distinct mechanisms: OCP, Lock
  Detection, UVLO, Thermal Shutdown, Voltage-Surge/AVS —
  DS-MTR-057/058/059/060/061), not assumed to be "on" by default. A
  correction against `bom/component-selection.md`'s DS-MTR-037 is found
  and flagged narratively in §7.5.6 and in `datasheets/
  texasinstruments_drv10983_slvscp6h.md`'s own Update section — **not**
  self-assigned a new ISS number (per this document's own established
  precedent that `validation/open-issues.md`/`validation/design-
  review.md` are Hardware-Reviewer/Hardware-Lead-owned registries; ISS
  numbers ISS-001 through ISS-013 already exist and none were self-minted
  by this agent in Rev 2 either).
- **ECO-008 directive (BEMF/FG low-RPM degradation)** — The human
  directive that this caveat must be tracked in the Firmware bring-up
  plan / `validation/fmea.md` (not just the comparison report) is
  respected: this is primarily a firmware/FMEA item, out of this agent's
  scope to resolve. One concrete circuit-level fact **is** found and
  recorded per the agent instructions' "flag it in your design rationale"
  guidance: the FG output's open-loop behavior is I2C-register-
  configurable (`FGOLsel[1:0]`, DS-MTR-062) and the open-to-closed-loop
  transition threshold is likewise register-set (`Op2ClsThr[4:0]`,
  DS-MTR-063) — real, named hooks a firmware engineer can use, wired and
  available via this design's I2C1 bus, but not configured by this
  circuit design (REQ-009 fence).
- **Mechanical/Thermal co-design (checklist item 18/15; REQ-204/307)** —
  §9 flips from Rev 2's correct "Explicitly Not Applicable" (no rotating
  body existed) to real content: the motor is a rotating body. Electrical
  -side facts relevant to vibration-induced solder-joint/connector stress
  and to thermal/vibration proximity effects on the IMU's bias stability
  are recorded for the Mechanical Lead's later attention — this document
  does not design the mechanical mitigation itself.
- **Power budget (REQ-109)** — `hardware/power-budget.md`'s placeholder
  Rev 3 motor-rail row is finalized with this design's actual connector
  (PJ-102AH) and real DRV10983+motor worst-case current figures, tracked
  as its own rail, not folded into REQ-103's 3.3V logic budget.
- **Self-check**: re-run against the full 18-item Circuit Engineer
  checklist (§14) and the 16-item Hardware Reviewer checklist (§15),
  explicitly re-covering items 1–9 for the new motor domain. **Precise
  N/A→real-content flips** (the only items that were genuinely Not
  Applicable in Rev 2): §14 item 18 (Mechanical/Thermal), §15 item 13
  (Motor noise) and the "near rotating bodies" portion of item 15 (PCB
  layout/mechanical-thermal co-design). **Re-checked/updated, not
  flipped** (these were already applicable in Rev 1/2, just extended for
  the new motor domain or two-domain system): §14 item 13 (MCU pin
  function — re-checked for ISS-011/ISS-006 plus the new motor pins) and
  §15 item 11 (Grounding — updated for the new two-power-domain
  treatment, §8). See §14/§15 for the item-by-item record.

**Rev 2, corrected (2026-08-31, post-Design-Complete)** — Circuit Engineer
correction addressing **ISS-027 (severity pending independent Hardware
Reviewer classification — recommended CRITICAL, see rationale below)**,
discovered by the Hardware Lead while independently verifying real KiCad
symbol/footprint availability for this repository's first real KiCad project
(`hardware/schematic/bench-imu-01/`) — **not** found by a Markdown-only
checklist or premise review, because it requires cross-checking the MCU's
*physical package pinout* table specifically, a different table from the
alternate-function table every prior review pass (Hardware Reviewer Cycles
1/2, rubber-duck, and the Firmware Engineer's own DS-MCU-062) correctly
checked instead.

- **ISS-027 (new)** — Independent research this cycle (Hardware Lead, ST's
  own official machine-readable pin database, `STMicroelectronics/
  STM32_open_pin_data` GitHub repo, `mcu/STM32G031K(4-6-8)Tx.xml` —
  DS-MCU-064) established that **PB10 and PB11 do not exist as pins
  anywhere on the STM32G031K8T6's actual LQFP-32 package**. ISS-011's own
  fix (I2C1→I2C2 relabeling) correctly identified the *peripheral instance*
  these physical pins would map to via the alternate-function table, but
  neither that fix nor either Hardware Reviewer cycle independently
  cross-checked whether PB10/PB11 are *physically bonded out* on this
  specific 32-pin package at all — a separate table in ST's own data from
  the alternate-function table, and the actual root cause of this defect.
  **This means the IMU I2C bus as previously documented cannot be
  physically wired on the real part** — a materially more serious defect
  than ISS-011's pure labeling correction, since no PCB trace can connect to
  a pin that does not exist.
  - **The real fix**: I2C2 remains the correct peripheral instance (no
    change needed there) — it is simply reachable via different physical
    pins on this package: **PA11 (I2C2_SCL, physical pin 22) and PA12
    (I2C2_SDA, physical pin 23)**, the default (no remap required) state of
    ST's own documented "dual-pad" pin-sharing feature on this small
    package (DS-MCU-067). Neither PA11 nor PA12 conflicts with any other
    net already committed in this design. Chosen over rerouting to true
    I2C1 pins (PB6/PB7 or PB8/PB9, both confirmed real and unused,
    DS-MCU-053) specifically because keeping the I2C2 *peripheral instance*
    unchanged minimizes the blast radius of the already-merged Firmware
    Bring-up code (PR #7), which initializes I2C2's own peripheral
    registers correctly — only its GPIO pin/AF configuration needs a
    follow-up fix (**not performed in this document/PR** — flagged for a
    separate Firmware follow-up task).
  - **Also corrected, same primary source (DS-MCU-064/065/066)**: this
    package has no separate VDDA pin (physical pin 4 is a single combined
    "VDD/VDDA" pin) and no separate VBAT pin at all (VBAT is not bonded out
    on this package); NRST is not a fully dedicated pin — it shares
    physical pin 6 with GPIO PF2 (factory default = NRST function,
    MODERATE confidence, community-sourced, not independently re-verified
    against the primary option-byte table this session — same confidence
    class as this document's existing nBOOT_SEL disclosure). §2.3, §4.1,
    §11, §12 updated throughout. This closes the moderate-confidence VDD/VSS
    pin-count discrepancy this document already disclosed at the (former)
    §16 item 3 — resolved in favor of the "1 VDD/1 VSS" reading, not the
    "1 VDD/2 VSS" reading.
  - **Self-check**: full-document search for every "PB10"/"PB11" occurrence
    (17 found) — historical changelog prose describing the ISS-011 fix
    itself is left as accurate history (not rewritten); every *current,
    active* design statement (pin tables, net list, checklist, parts list)
    is corrected to PA11/PA12. No other net, component, or requirement
    changes as a result of this fix — same physical topology intent (a
    pulled-up, 2-wire I2C bus from the MCU to the IMU), different physical
    MCU pins only.
  - **Not resolved by this document**: final severity classification
    (recommended CRITICAL per `docs/architecture.md` §7.1 — "design will
    fail... as designed" describes this defect precisely, more so than
    ISS-011's own HIGH classification, since no hardware rework can make
    the *previously documented* pins work at all) is the Hardware
    Reviewer's call, not mine to self-assign. See `validation/
    open-issues.md` ISS-027 and `validation/change-log.md` ECO-006.

**Rev 2 (2026-09-01)** — Circuit Engineer rework addressing
`validation/design-review.md` Cycle 1 findings, per
`.github/agents/circuit-engineer.agent.md` ("When you receive Hardware
Reviewer findings... address every CRITICAL and HIGH finding explicitly").
Only this document was modified; `validation/open-issues.md`,
`validation/design-review.md`, and `datasheets/evidence-log.md` are owned
by the Hardware Reviewer / Hardware Lead and are not touched here.

- **ISS-011 (HIGH, fixed)** — The IMU I2C bus on MCU pins PB10/PB11 was
  mislabeled "I2C1" throughout this document. Independent research
  (Hardware Lead, this cycle, DS-MCU-052/053) confirmed PB10/PB11 are
  actually this part's **I2C2** alternate function. Every reference
  (§2.3, §5.2, §5.3, §6, §11, §12, §14, §16) is corrected I2C1→I2C2. No
  PCB/wiring change — pins are physically unchanged; only the
  peripheral-instance label and the firmware target change. **I2C1 is
  now recorded as entirely free** (a genuine peripheral-margin
  improvement, not a regression — later re-consumed by the Rev 3 motor
  subsystem, see below). **(Note added by the "Rev 2, corrected" entry
  immediately above, ISS-027): the "PB10/PB11" pin identification above
  was itself factually wrong — those two pins do not exist at all on
  this part's actual LQFP-32 package (nor do a separate VDDA pin, a VBAT
  pin, or a second VSS pin exist; NRST also shares its pad with PF2 —
  all corrected in that same entry). This was not caught until the more
  complete, primary-source-based correction described in the "Rev 2,
  corrected" entry immediately above (ISS-027), which moved the IMU's
  I2C2 bus to PA11/PA12 instead. This branch had independently begun a
  narrower version of this same fix (previously tracked here as "Rev
  6"/ISS-026, moving only the I2C2 pins and not the other power/reset
  pin-identity errors); that narrower fix is superseded by, and folded
  into, the "Rev 2, corrected" entry above. The peripheral-identity
  correction made here in Rev 2 (I2C1→I2C2) remains correct and
  unaffected — see that entry and §16 item 4.)**
- **ISS-001 (HIGH, fixed)** — The LDO (U3) EN pin connection was hedged
  ("if the exact package variant... has an active EN pin..."). Independent
  research (Hardware Lead, this cycle, TI SBVS320D Rev D) confirmed EN
  (pin 3, DBV package) is mandatory on every package variant, with no
  internal bias. §3.4 and §12 now state a firm, unconditional EN→VIN tie
  as a committed design decision, with a new explicit `EN_VIN` net.
- **ISS-002 (HIGH, addressed)** — The design's own arithmetic against
  REQ-101 was correct, but Independent Review found the real-world USB-C
  vSafe5V ceiling (4.75–5.5V) is wider than REQ-101's stated band
  (4.75–5.25V), leaving effectively zero margin against the LDO's 5.5V
  Recommended Operating Condition ceiling (though 0.5V/9% of real headroom
  remains under its 6.0V Absolute Maximum Rating — not a damage risk). New
  §3.5 analyzes this explicitly and **recommends an ACCEPTED-RISK
  disposition** (with a component-change flag as the alternative) for the
  Hardware Lead to route to the human Chief Engineer per
  `docs/architecture.md` §8. This finding is **not** closed by this
  document — the disposition decision is the Hardware Lead's/human Chief
  Engineer's to make.
- **ISS-006 (MEDIUM, corrected)** — §4.1/§4.2's BOOT0 discussion is
  corrected: BOOT0 is muxed onto **PA14** (already this design's SWCLK
  pin), not PB8. PB8 does physically exist on this package (contra this
  document's original §4.1/§16 claim) but its real function is an
  alternate I2C1_SCL pin (DS-MCU-053), unrelated to BOOT0. The design's
  final decision (no physical BOOT0 circuit, rely on the nBOOT_SEL
  default) is unchanged — only the reasoning is corrected.
- **ISS-010 (LOW, corrected)** — The MCU VDD Absolute Maximum Rating lower
  bound, previously UNKNOWN, is now resolved at **−0.3V** (confirmed by
  the Hardware Reviewer against ST DS12992 Rev4 Table 18). §1/§16 updated.
- **Out of scope this revision (unchanged, left for a later disposition
  pass)**: ISS-004, ISS-005, ISS-007, ISS-008, ISS-009. Not marked
  resolved; not touched beyond what already existed.
- **Self-check**: re-run against Hardware Reviewer checklist items 1, 2,
  6, 7, 13, and 16 (§15) — items 6/7/13 map most directly onto ISS-001/
  ISS-011/ISS-006; items 1/2 onto ISS-002/ISS-010.

## 0. Tooling honesty statement

`kicad-list_projects` returned empty this session — **no KiCad project
exists yet** for this repository. The connected KiCad MCP tools
(`extract_project_netlist`, `analyze_schematic_connections`,
`validate_project`, `run_drc_check`, `export_bom_csv`,
`generate_pcb_thumbnail`, etc.) are **read/analyze-only**: every one of
them operates on an existing `.kicad_pro`/`.kicad_sch`/`.kicad_pcb` file.
There is no tool available in this environment to create a new KiCad
project or schematic from scratch.

This document is therefore a **structured schematic-equivalent Markdown
document**, not an actual KiCad project — a net-by-net / block-by-block
description, a full MCU pin-assignment table, a parts list specific to
this design, and a design-rationale log with Evidence ID citations. This
mirrors the same tooling-honesty convention already used by the
Mechanical Lead for CAD (no verified CAD tool connected in this
environment either). It is **not** a substitute for laying the design out
in real KiCad once that tooling exists — it is the best-available
faithful representation given the current toolset, sufficient for an
independent Hardware Reviewer to review net-by-net.

This also happens to match this cycle's own stated scope: REQ-502 states
"This is a paper/document design exercise this cycle, not a production
schedule — no physical PCB fabrication or physical power-on happens in
this session." A structured document deliverable is therefore not merely
a workaround for missing tooling, but the actually-correct artifact type
for this design cycle.

Once a KiCad project exists, step 6 of my own procedure
(`.github/skills/schematic-design/SKILL.md`) requires self-checking with
`extract_schematic_netlist` / `analyze_schematic_connections` /
`validate_project` — that step is **not applicable yet** and is called out
explicitly rather than silently skipped (see §15, Hardware Reviewer
checklist item 16 discussion).

**Update (2026-08-31, post-Design-Complete)**: the above described this
document's authoring context at the time — **it no longer reflects this
repository's current tooling state.** A real KiCad project for this design
now exists at `hardware/schematic/bench-imu-01/` (this repository's first),
built and independently tool-verified against this document per
`docs/architecture-evolution.md` §34. Building that real project is exactly
what surfaced ISS-027 (see the "Rev 2, corrected" changelog entry above) —
concrete evidence that "sufficient for an independent Hardware Reviewer to
review net-by-net" (this section's own claim, above) had a real limit: a
Markdown-only review, however careful, cannot catch a physical
package-pin-bonding defect that only a real schematic-capture tool
surfaces. This document remains the authoritative net-by-net rationale
log; the KiCad project is the physically-verifiable artifact built from
it, not a replacement for its rationale.

## 1. Scope and inputs (not re-litigated)

Per task framing, the following are **human-approved and not up for
re-litigation** in this design cycle. This document only flags part-level
problems discovered during design (routed to Hardware Lead / Component
Engineer per `.github/agents/circuit-engineer.agent.md` "Out of scope");
it does not unilaterally swap parts.

| Role | Part | Package | Key specs | Evidence |
|---|---|---|---|---|
| MCU (U1) | STMicroelectronics STM32G031K8T6 | LQFP-32 | Arm Cortex-M0+ ≤64MHz, 64KB Flash + 8KB SRAM, 2×I2C/2×SPI/2×UART, SWD+JTAG, no native USB | DS-MCU-012–021 |
| IMU (U2) | Bosch Sensortec BMI270 | LGA-14 (2.5×3.0×0.83mm) | 6-axis accel+gyro, I2C≤1MHz FM+ or SPI≤10MHz, VDD ROC 1.71–3.6V / AMR −0.3…+3.6V, VDDIO ROC 1.2–3.6V | DS-IMU-001–017, 070 |
| LDO (U3) | Texas Instruments TLV75533PDBVR | SOT-23-5 | Fixed 3.3V, Vin ROC 1.45–5.5V / AMR 6.0V, 500mA max, dropout typ220/max238mV@500mA, Iq 25µA | DS-PWR-001–011 |
| Motor driver (U5) — **new Rev 3** | Texas Instruments DRV10983 | HTSSOP-24 (PWP) | Sensorless 3-phase BLDC driver, VCC ROC 8/24(typ)/28V (AMR −0.3…30V), 2A continuous / 3A peak per phase, integrated I2C-configurable OCP/Lock/UVLO/Thermal/AVS protection, PWM or analog SPEED input, hardware FG tach output | DS-MTR-052–070 |
| Motor (M1) — **new Rev 3** | T-Motor MN2206-13 KV2000 | Sensorless BLDC, reaction-wheel form factor | 2S–3S (7.4–12.6V), ≈1.05A derived current need for 5mN·m target, 18A continuous rating, no integrated RPM sensor (FG tach comes from the driver's BEMF sensing, not the motor itself) | DS-MTR-001–051 (Component-Engineer-approved candidate research), human-signed-off via ECO-008 |

Requirements are sourced from `requirements/requirements.md` (human
signed off) and cited by REQ-ID throughout this document. Component
candidate comparisons live in `bom/component-selection.md` and are not
repeated here except where a specific cited number (e.g. the LDO thermal
estimate, or the DRV10983/T-Motor margin figures) is directly reused.

**New this revision (Rev 3)** — the Motor driver (U5) and Motor (M1) rows
above were Component-Engineer-approved and human-signed-off via ECO-008
(`validation/change-log.md`) before this design cycle began, per this
agent's own instructions not to proceed on an unconfirmed part. All
pinout/register/protection-circuit facts needed to actually wire U5 were
extracted fresh from TI's primary datasheet (SLVSCP6H) this revision —
see §7.5 for the full treatment.

**RESOLVED this revision (ISS-010)** — the STM32G031K8T6 VDD Absolute
Maximum Rating **lower bound**, carried forward from
`bom/component-selection.md` as unconfirmed, is now confirmed at
**−0.3V** (upper bound remains 4.0V, DS-MCU-012), independently verified
by the Hardware Reviewer this cycle directly against ST's primary
datasheet (DS12992 Rev4, Table 18) — see §16 item 2. Full AMR is
therefore **−0.3V to +4.0V**. The chosen operating point, 3.3V, sits
deep inside both the confirmed Recommended Operating Condition
(1.7–3.6V, DS-MCU-013) and the now-fully-confirmed AMR — no violation in
either direction, and this is no longer an open gap.

## 2. Shared resources — fixed first, serially (per SKILL.md step 1)

### 2.1 Rails

Two rails exist on this board:

- **5V (VBUS)** — pre-regulator, from the USB-C receptacle (J1), nominal
  5.0V, USB-spec tolerance 4.75–5.25V (REQ-101). Feeds: LDO (U3) input,
  ESD protection IC (U4) VBUS pin.
- **3V3** — post-regulator, LDO (U3) output, fixed 3.3V (DS-PWR-003).
  Feeds: MCU (U1) VDD/VDDA (combined pin, physical pin 4 — no separate
  VDDA pin and no VBAT pin exist on this package, ISS-027, see §4.1), IMU
  (U2) VDD/VDDIO, both header 3V3 reference pins (SWD J3, UART J2), status
  LED (D1) via R5, I2C pull-ups (R3/R4).
- **VM_MOTOR (~12V-class) — new Rev 3, envelope bounded Rev 4** —
  independent input, from the new barrel jack (J4), through a new PTC
  resettable fuse (F1, Rev 4), series reverse-polarity diode D2 and TVS
  D3, to the DRV10983 (U5) VCC pins. M1 itself remains rated 2S–3S per
  REQ-108/Option A/`bom/component-selection.md` (unedited, unchanged) —
  but **this design's own added series protection diode (D2) narrows the
  practical operating recommendation to 3S-only, now stated as a binding
  constraint with a bounded 9.0–13.0V source envelope (§7.5.2/§7.5.9,
  ISS-014/ISS-019), not merely 2S–3S in the abstract**. **Electrically
  independent of the 5V/3V3 rails above — no shared regulator, no shared
  source** (Option A's fault-isolation intent, `hardware/power-
  architecture.md`). U5's own internal step-down regulator is configured
  in **linear mode** (§7.5.3) specifically so it cannot supply the
  MCU/IMU domain, per the task's explicit constraint. See §7.5 for the
  full power-input block and §17/`hardware/power-budget.md` for the
  numeric budget.

Single 3.3V logic level throughout (REQ-102, "Should") — no
level-shifting circuitry anywhere in this design for the MCU/IMU domain.
USB 5V VBUS is isolated from all logic by the LDO; USB D+/D− (which would
otherwise be a 5V-tolerance concern) are unpopulated per REQ-105
(power-only port, no data), so 5V-tolerance is moot for that domain. The
new VM_MOTOR domain operates at up to 28V (U5's AMR ceiling, DS-MTR-053)
internally, but the **signal-level** pins this design's MCU actually
touches (U5's SPEED/DIR/SCL/SDA/FG pins) are a separate, low-voltage
digital I/O group with their own ROC (−0.1 to 3.3 nominal/3.6V max,
DS-MTR-054) — cross-domain voltage compatibility for those specific
signal pins is analyzed pin-by-pin in §7.5.4, not assumed.

### 2.2 Ground scheme

**Single ground net/plane for the whole board — now spanning two
independent power domains, addressed explicitly (updated this
revision).** REQ-301 fixes a single 2-layer PCB (no daughtercards/stacked
boards) — for a design this small (3 active ICs in Rev 2; +1 driver IC
and 1 motor connector in Rev 3, still a single small board, no
analog-precision/RF section requiring a split or star-ground topology), a
single unbroken ground pour on one layer remains the correct, standard
choice, not an oversight. All GND pins (U1 VSS×2, U2 GND+GNDIO, U3 GND,
U4 GND, R1/R2 CC pull-down returns, C1–C9 return sides, both header GND
pins, LED cathode return, and — **new Rev 3** — U5 GND/PGND×2/SWGND, M1's
motor-frame return where applicable, J4's sleeve/shield return, D2/D3
return sides) tie to this one net. **New Rev 3 nuance, not present in
Rev 2**: the two power *rails* (5V/3V3 vs. VM_MOTOR) are deliberately
independent sources (Option A), but they still tie to this **same**
ground net/plane — ground is shared even though power is not. This is
necessary (not optional) for the PWM/FG/I2C1 signals crossing between U1
and U5 to be valid logic signals at all (a signal referenced to one
ground and read against a different, unconnected ground is undefined).
§8 (Grounding block) gives the full two-domain treatment this task
requires, including return-current routing and REQ-010/REQ-204 noise
isolation for the IMU — this is stated here explicitly per the design
task's own instruction not to leave it implicit (see also §14 item 15/
checklist item 11 in the self-check).

### 2.3 Pin allocation (summary; full table in §11)

Fixed once, before any sub-block was designed in detail, to avoid
rework/conflicts across blocks:

| Function | MCU pin | Confidence |
|---|---|---|
| SWDIO | PA13 | HIGH — dedicated STM32 debug pin, not an alternate function |
| SWCLK | PA14 | HIGH — dedicated STM32 debug pin, not an alternate function; also this MCU sub-family's BOOT0 boot-mode-select mux pin — corrected this revision, see §4.2 (ISS-006) |
| I2C2 SCL | PA11 | HIGH — **corrected this revision (ISS-027)**: independently confirmed against ST's own official pin database (DS-MCU-064/067) that PB10/PB11 (this table's own prior entry, itself already a Rev 2/ISS-011 correction) **do not exist on this package at all** — real I2C2_SCL on this LQFP-32 part is PA11 (physical pin 22, default/unremapped state), no conflict with any other net in this design |
| I2C2 SDA | PA12 | HIGH — as above (DS-MCU-064/067); real I2C2_SDA is PA12 (physical pin 23, default/unremapped state) |
| USART2 TX | PA2 | MODERATE-HIGH — very common STM32 USART2 mapping; not individually re-verified against the exact AF table this session (see §16) |
| USART2 RX | PA3 | MODERATE-HIGH — as above |
| Status LED drive | PA5 | ASSUMPTION — arbitrary free GPIO choice (also the conventional "Nucleo LED" pin on many ST boards), no AF conflict since it's used as plain GPIO output |
| NRST | PF2/NRST shared pin (physical pin 6) | MODERATE — **corrected this revision (ISS-027)**: this is not a fully dedicated reset-only pin as previously stated (which also cited the wrong pin number, 4); ST's own pin database names it "PF2 - NRST" (DS-MCU-066), a shared pad whose factory-default state is the NRST function (GPIO PF2 is reachable only via a dedicated option-byte reconfiguration, not used here) — MODERATE confidence since the factory-default claim is community-sourced, not independently re-verified against the primary option-byte table this session |
| BOOT0 | not populated this cycle | see §4.2/§4.4/§16 — **corrected this revision (ISS-006)**: BOOT0 is muxed onto PA14 (already committed to SWCLK above), not PB8; PB8 does physically exist on this package but its function is unrelated (alternate I2C1_SCL) |
| **SPEED/PWM (new Rev 3)** | **PA8** | **HIGH** (pin name/AF) — TIM1_CH1, AF2, confirmed against DS-MCU-069/Table 13; physical LQFP-32 pin number MODERATE (deferred to layout, see §16) |
| **FG tach input (new Rev 3)** | **PA6** | **HIGH** (pin name/AF) — TIM3_CH1 input-capture, AF1, FT_ea 5V-tolerant, confirmed DS-MCU-069/071/Table 13; physical pin number MODERATE |
| **DIR (new Rev 3)** | **PB1** | **HIGH** — plain GPIO push-pull output, no AF conflict; physical pin number MODERATE |
| **I2C1 SCL (new Rev 3)** | **PB6** | **HIGH** (pin name/AF) — AF6, confirmed DS-MCU-070/Table 14; physical pin number MODERATE; FT_f/Fm+-capable per general-family generalization — MODERATE confidence specifically on the Fm+ tolerance claim, not independently re-confirmed against a Table-18 FT_f line item this session (§16) |
| **I2C1 SDA (new Rev 3)** | **PB7** | **HIGH** (pin name/AF) — AF6, confirmed DS-MCU-070/Table 14; same physical-pin-number and Fm+-tolerance caveats as PB6 above |

This leaves **USART1 and LPUART1 both free** (only USART2 is used) —
satisfies the Component Engineer's own note that one of the MCU's 2 UART
peripherals should remain genuinely free (only 1 of 2 committed here,
comfortably; actually both USART1 and LPUART1 remain free since USART2 is
the one consumed — even better margin than "one free" required). **Rev 2
update (ISS-011)**: since the IMU bus correctly occupies I2C2 (not I2C1
as originally labeled), I2C1 was recorded as entirely free at that time.
**Pin-identity correction (ISS-027)**: the IMU's I2C2 bus itself was later
found to be on PA11/PA12, not the non-existent PB10/PB11 as previously
labeled (see the "Rev 2, corrected" changelog entry) — this does not
change the I2C1-is-a-separate-peripheral conclusion above, only the
physical pins the IMU's own I2C2 bus uses. **Rev 3 update**: the I2C1
margin identified above is now **consumed** — PB6/PB7 (I2C1 SCL/SDA) are
wired to U5 for motor-parameter commissioning and `SpdCtrlMd`
configuration (DS-MTR-070/068; not merely "optional future tuning" — see
§7.5.4). PB8/PB9 (I2C1's secondary AF pair, DS-MCU-053, both
independently confirmed to physically exist) remain unused and free. See
§11 for the full, updated free-GPIO inventory.

## 3. Block 1 — Power input + regulation

### 3.1 Connector choice: USB-C (over Micro-USB-B)

**Decision: USB-C.** Documented trade-off:

| | USB-C (chosen) | Micro-USB-B (rejected) |
|---|---|---|
| Ecosystem | Modern connector, aligned with current laptops/chargers, many of which are USB-C-only now | Legacy/declining — increasingly hard to source new cables/chargers for it |
| Insertion | Reversible/no wrong-way insertion | Must be inserted right-way-up |
| Extra parts needed | 2× 5.1kΩ CC1/CC2 pull-down-to-GND resistors (R1, R2) required for a compliant source to enable VBUS (DS-CONN-001) | None — no CC-equivalent negotiation exists |
| Precedent value | This is the repository's **first** end-to-end design cycle — sets a forward-compatible connector precedent for future boards | N/A |

The added complexity (2 resistors, one-time, ~$0.01 BOM impact) is minor
compared to Micro-USB-B's compounding disadvantage (an already-legacy
connector whose availability will only keep declining over this
project's lifetime). **R1 = R2 = 5.1kΩ**, CC1→GND and CC2→GND
respectively (DS-CONN-001 — USB-IF Type-C spec fixed Rd value for a
UFP/sink). Without these resistors, a compliant USB-C source will not
enable VBUS at all, even for a power-only sink — this is a hard functional
requirement, not an optional nicety.

Since REQ-105 restricts this port to power delivery only (no
data/enumeration), a full 24-pin SuperSpeed-capable USB-C receptacle is
not needed — a basic USB 2.0-only USB-C receptacle (VBUS, GND, CC1, CC2,
D+, D− — the electrically "used" contacts, D+/D− present on the connector
for cable compatibility but left unpopulated on this board) is sufficient
and keeps BOM cost down (supports REQ-501's soft cost target). **J1's
exact MPN is not formally selected in this design cycle** — see §10 for
the illustrative real part (GCT USB4125) used only to ground the
mechanical height estimate.

### 3.2 ESD / transient protection (REQ-402)

**Part selected: STMicroelectronics USBLC6-2SC6** (SOT-23-6, 4-line TVS
diode array), one of the three example families named in the design task
(ON Semi NUP2105L / TI TPD2E009 / STMicro USBLC6-2SC6). Real datasheet:
https://www.st.com/resource/en/datasheet/usblc6-2sc6.pdf. New metadata
record: `datasheets/stmicroelectronics_usblc6-2sc6_rev-unknown.md`.

Key specs (DS-PROT-001): clamp voltage 17V max @5A (8/20µs), standoff
voltage 5.25V (clears USB VBUS's 5.25V nominal ceiling per REQ-101 with
zero margin at the absolute worst case — see §16 flag), breakdown voltage
6V min, I/O capacitance 2.5pF typ/3.5pF max (low enough not to matter for
a power-only, non-data line anyway), SOT-23-6 package, IEC 61000-4-2
±15kV air / ±8kV contact ESD immunity rating.

Pinout/topology (DS-PROT-002): I/O1 = pins 1 & 6 (D+ channel), I/O2 =
pins 3 & 4 (D− channel), VBUS = pin 5, GND = pin 2.

**Wiring decision**: since REQ-105 is power-only (no USB data lines
connected at all), only the **VBUS (pin 5) and GND (pin 2)** channel is
wired into the signal path — VBUS routes through U4's VBUS pin before
reaching C1/U3's input, GND ties to the common ground net. **I/O1 and
I/O2 (the D+/D− clamp channels) are left unpopulated/NC** since there is
no D+/D− signal on this board to protect. This is a deliberate,
documented deviation from the part's full 4-line "typical application"
(which normally ties all 4 I/O pins to a USB data pair) — justified
because there is no data pair to protect in this design (REQ-105).

**This single real part is not run through a full ≥3-candidate Component
Selection comparison**, per the design task's own explicit instruction —
a real, datasheet-grounded single part is sufficient for this
supporting/protection role, unlike the three primary BOM parts.

### 3.3 Reverse-polarity protection (also REQ-402)

REQ-402 requires "basic transient/ESD and reverse-polarity protection
appropriate for a hand-handled connector." Transient/ESD is satisfied by
§3.2 above. For reverse-polarity: **no discrete series diode is added.**
Rationale: USB-C (like Micro-USB-B) is a **mechanically keyed** connector
— VBUS and GND are fixed to specific physical contacts regardless of
cable/plug orientation; a user cannot physically insert a compliant USB-C
plug "backwards" in a way that swaps VBUS and GND polarity (unlike, e.g.,
a bare 2-pin JST/barrel-jack connector, which genuinely can be reversed
by a user). A series Schottky diode was considered and rejected: it would
cost ~0.3–0.5V of dropout for marginal benefit given the mechanically-keyed,
non-field-deployed (bench-use, REQ-201) nature of this connector. This
trade-off is flagged explicitly for the Hardware Reviewer to challenge if
they read REQ-402's "reverse-polarity" language more broadly (e.g. to
include a mis-wired/jury-rigged power source, not just a standard cable
insertion) — see §16.

### 3.4 Regulation: TLV75533PDBVR (U3) per its own reference app circuit

VBUS (after U4's ESD channel) → **C1 = 1µF ceramic** (LDO input
decoupling) → U3 IN pin. U3 OUT pin → **C2 = 0.47µF ceramic** (LDO output
decoupling) → 3V3 rail. Both values are the **minimum** ceramic values
from TI's own reference application circuit for this exact part
(datasheet SLVSDV4) — DS-PWR reference-circuit evidence already cited in
`bom/component-selection.md`'s Power Regulator section, reused verbatim
here, no deviation.

**EN pin — fixed this revision, no longer hedged (ISS-001)**: U3's EN pin
(pin 3 on the ordered DBV/SOT-23-5 package) is **firmly and
unconditionally tied directly to VIN (U3 pin 2)** — always-enabled, per
TI's own recommended connection for an always-on application, which
matches this design's use case exactly. This is now an explicit net in
the net list (§12, `EN_VIN`) and parts-list note (§13), not a
layout-time judgment call.

This replaces this document's original hedge: *"U3's EN pin (if present
on this specific variant/package...) is tied to enable-always per the
standard reference circuit; if the exact TLV75533 package variant used
here has an active EN pin requiring a level, tie it to VIN directly...
flagged as a minor implementation detail to confirm against the literal
pinout diagram at layout time."* Independent research (Hardware Lead,
this cycle, TI SBVS320D Rev D §4 Table 4-1 pin description, §5.5
Application Information, §6.4 typical application) confirms:

- EN is a **mandatory** pin present on **every** package variant of this
  part family (DQN pin 3, DBV pin 3, DYD pin 3, DRV pin 4 — there is no
  "no-EN"/EN-less variant of this device). The original hedge's premise
  ("if the exact... variant... has an active EN pin") was not actually a
  live possibility — every ordering-option variant has one.
- The EN pin has **no internal pull-up or pull-down bias** — only
  high-impedance leakage (I_EN ≈ 10nA at EN = 5.5V). The datasheet's only
  internal "pulldown resistance" specification (≈120Ω) is the *output*
  discharge switch engaged while the device is disabled, not an EN-pin
  bias network, and must not be confused with one.
- A genuinely floating EN pin therefore leaves the enable state
  undefined: the rail could fail to enable at all (a dead board at
  bring-up, easily misdiagnosed as a different fault), or sit in the
  undefined 0.3–1.0V threshold gray zone and chatter/misbehave from
  coupled digital-switching noise on the board. This is real, undefined
  behavior — not a theoretical nitpick.

Tying EN→VIN removes this ambiguity entirely, at **zero component cost**
(one additional trace/via, no resistor, no new part). No other electrical
conclusion elsewhere in this document changes as a result — enable-always
was already the design's intended behavior; it is now a firmly committed
net rather than a deferred, hedged assumption.

AMR/ROC check: U3 Vin = 5.0V nominal (4.75–5.25V per REQ-101) is within
AMR 6.0V (DS-PWR-002) with 0.75–1.25V margin, and within ROC 1.45–5.5V
(same evidence) — but the **top of the USB tolerance band (5.25V) leaves
only ~0.25V of headroom under the 5.5V ROC ceiling**, tighter than the AMR
margin. This is noted explicitly as a real, if small, margin consideration
rather than glossed over — it does not exceed any limit against REQ-101's
own stated band. **§3.5 below addresses why this margin is actually
tighter still against the real-world USB-C spec, with this revision's
explicit disposition of that gap (ISS-002) — this is no longer left as a
silent flag.**

### 3.5 LDO input-voltage margin disposition: the real-world USB-C vSafe5V ceiling (ISS-002, new this revision)

**This entire subsection is new this revision.** §3.4's AMR/ROC check
above is arithmetically correct against REQ-101's own stated figure
(4.75–5.25V), but Independent Review found that REQ-101's figure does not
capture the actual governing specification for the connector this design
uses.

**The gap**: independent research (Hardware Lead, this cycle) established
that the real-world input voltage a spec-compliant USB-C/USB-PD source is
permitted to present — the governing "vSafe5V" range defined by the
USB-IF — is **4.75V to 5.5V**, wider than REQ-101's stated 4.75–5.25V
legacy-USB tolerance band. At that wider, genuinely spec-compliant
worst-case ceiling (5.5V), margin against the LDO's own 5.5V Recommended
Operating Condition maximum (DS-PWR-002) is **effectively zero** — not
the ≈0.25V §3.4 computes against REQ-101's narrower figure. A real,
fully-compliant USB-C charger could legitimately present a Vin at which
this design's own arithmetic no longer shows headroom.

**Why this is not a damage/safety risk**: even at the worst-case, fully
spec-compliant 5.5V input, the LDO still sits a full 0.5V (≈9%) under its
6.0V Absolute Maximum Rating (DS-PWR-002) — real headroom remains, and no
component damage is expected at 5.5V. Exceeding a Recommended Operating
Condition (as opposed to an Absolute Maximum Rating) is, per TI's own
datasheet convention, a "may not meet all specified electrical
characteristics" caveat, not a "may be damaged" one — i.e. the practical
worst case here is a regulator that is still safe but may not be fully
within its datasheet-guaranteed output tolerance/PSRR/dropout
specification at that exact instant, not a burnt part.

**My disposition recommendation**: I recommend **(a) ACCEPTED-RISK**,
routed by the Hardware Lead to the human Chief Engineer for the named
sign-off `docs/architecture.md` §8 requires ("HIGH findings may become
ACCEPTED-RISK only with named human sign-off"), for these reasons:

- The failure mode at the true worst case is a soft, bounded
  regulation-margin concern (possible minor output-tolerance/PSRR/dropout
  degradation at an edge-case input voltage that most real chargers won't
  actually reach in practice), not a hard functional or safety failure —
  the 6.0V AMR headroom means there is no damage risk to disposition
  around.
- This is explicitly a bench/prototype design (REQ-502: "paper/document
  design exercise this cycle, not a production schedule"), where a
  narrow, well-understood, bounded edge-case risk is a reasonable
  engineering trade rather than a reason to force a part change.
- The alternative — swapping the LDO — is not something I can decide or
  execute unilaterally regardless of my own judgment here (per my own
  agent instructions' "Out of scope": part selection is the Component
  Engineer's call, routed through the Hardware Lead, not mine to make
  even when I've identified a part-level concern during design).

**Option (b), noted but not chosen**: if the Hardware Lead judges the
margin unacceptable even as a bounded, non-damage risk (e.g. because this
design is expected to graduate beyond a bench prototype, where "may not
meet all specified electrical characteristics" at the input rail becomes
a real functional-reliability concern rather than an academic one), I
flag — without unilaterally implementing — that the Component Engineer
could be asked to evaluate an alternate LDO with a wider Vin ROC ceiling
(e.g. a part rated to 5.5V ROC with more headroom, or one rated well
above 5.5V/6.0V entirely) as a drop-in-footprint or near-drop-in
replacement. I have not selected or proposed a specific alternate part
number — that evaluation is the Component Engineer's, not mine, per my
own agent instructions.

**This finding is not closed by this document.** Per `docs/architecture.md`
§8, I cannot self-resolve a HIGH finding into ACCEPTED-RISK — I can only
recommend a disposition with reasoning and hand the routing decision to
the Hardware Lead (and, for ACCEPTED-RISK specifically, the human Chief
Engineer). See §16 item 10 for the tracked disposition-pending record.

## 4. Block 2 — MCU periphery

### 4.1 VDD / VDDA / VBAT pin handling and decoupling

**Corrected this revision (ISS-027)** — see the full correction note below
the table; the pin-count/numbering in this section was wrong on several
points, now resolved against ST's own official pin database rather than
the distributor/aggregator sources originally cited.

STM32G031K8T6 LQFP-32 power-pin table, per ST's own official CubeMX pin
database (DS-MCU-064/065, **HIGH confidence** — primary-source-equivalent,
see `datasheets/stmicroelectronics_stm32_open_pin_data_stm32g031k4-6-8tx.md`;
supersedes the original DS-MCU-046 distributor/aggregator-sourced table,
which had the wrong pin numbers and incorrectly assumed a separate VDDA/VBAT
pin existed):

| Pin | Number | Count | Decoupling |
|---|---|---|---|
| VDD/VDDA (combined — see correction note) | 4 | ×1 | **C3 = 100nF ceramic**, VDD-to-GND, placed as close to pin 4 as layout allows. **C4 = 100nF ceramic** (originally specified as a separate "VDDA decoupling" cap) is kept in parallel at the same physical pin/net, per the design's original intent of separate VDD/VDDA decoupling — harmless redundancy now that both functions share one pin, not removed so as to preserve the original two-capacitor BOM/rationale |
| VSS/VSSA (combined — see correction note) | 5 | ×1 | Ground return, no decoupling cap needed (tie to GND plane) — **only one ground pin on this MCU, not two as originally stated** |
| VBAT | **does not exist as a separate pin on this package** | — | No net/cap needed — VBAT is not bonded out at all on this LQFP-32 part (see correction note); the original "tie to 3V3" ASSUMPTION is moot, not merely unconfirmed |
| NRST | 6 (shared PF2/NRST pad) | — | See §4.3 |

Only **1 VDD pin** (combined with VDDA) exists on this LQFP-32 part, so the
"100nF per VDD pin" generic STM32 convention resolves to exactly one
physical decoupling node here (C3 and C4 both land on it) — not the
multi-cap fan-out some larger STM32 packages (with 4+ VDD pins) would need.

**Correction this revision (ISS-027)**: the table above previously cited
VDD=pin 17, VSS=pins 1 and 16 (×2), VDDA=pin 5, VBAT=pin 32, and NRST=pin 4
— sourced from distributor/aggregator pages (DS-MCU-046) that were
**already flagged in this document as MODERATE confidence and not
independently re-parsed against the raw ST PDF**. Independent research this
cycle (Hardware Lead, ST's own official machine-readable pin database,
`STMicroelectronics/STM32_open_pin_data` GitHub repository, DS-MCU-064/065)
found the real picture is different in every respect: there is no separate
VDDA pin at all (pin 4 is a single combined "VDD/VDDA" pin); there is no
separate VBAT pin at all (VBAT is not bonded out on this package — a fact,
not an ASSUMPTION, once a design needs it, that would require a different
package); there is only one ground pin, not two (pin 5, combined
"VSS/VSSA"); and NRST shares physical pin 6 with GPIO PF2 rather than being
a fully dedicated pin at pin 4 (see §4.3/§2.3 for the NRST correction in
full). **This also resolves this document's own previously-disclosed §16
item 3 moderate-confidence discrepancy** ("1 VDD/2 VSS" vs. a lower-detail
source's "1 VDD/1 VSS" claim) — in favor of the lower-detail source having
been right all along: there genuinely is only one VSS pin on this package.
None of these corrections change the decoupling *design* (still one 100nF
cap effectively at the combined VDD/VDDA node, still no cap needed on the
single ground pin, still no VBAT circuitry needed) — only the pin
*identities/numbers* were wrong. This is a separate, independently-found
correction from ISS-006's original PB8/PB9-existence finding (still valid,
retained below).

**Correction from a prior revision (ISS-006, retained)**: the pin-count
table above (from DS-MCU-046, distributor/aggregator sources) does **not**
list a PB8/PB9 pin, which this document originally read as evidence that
PB8 is not bonded out on this package at all (see the original §4.2
reasoning this replaces, below). Independent research (Hardware Lead, this
cycle, DS-MCU-051) found this premise was wrong: **PB8 does physically
exist** on this package, corroborated across the sources checked this
cycle, correcting the §4.1/§16 UNKNOWN this document originally carried on
that specific point — also now independently reconfirmed against the
primary-source pin table (DS-MCU-064): PB8 is physical pin 32. PB8's real
function turns out to be an alternate I2C1_SCL mapping (DS-MCU-053), not
BOOT0 — see §4.2 immediately below for the corrected BOOT0 picture.

### 4.2 BOOT0 / nBOOT_SEL handling

This required real web research since STM32 boot-mode conventions differ
materially across families (STM32F1-era generic conventions do **not**
carry over to STM32G0).

**Corrected this revision (ISS-006)** — this subsection's original
reasoning had a factual error at its premise (see the changelog at the
top of this document): it assumed BOOT0 was multiplexed with PB8 and,
finding no PB8 in this design's pin-count research, concluded the whole
BOOT0-pin question might be moot for this exact part. Independent
research (Hardware Lead, this cycle, DS-MCU-050/051, corroborated by
RM0454 and ST Community references) corrects this on two independent
points at once:

- **BOOT0 is actually multiplexed onto PA14** on this STM32G0x0
  sub-family — not PB8. PA14 is already committed in this design as the
  SWD **SWCLK** pin (§2.3, §4.4).
- **PB8 does physically exist** on this package after all (DS-MCU-051,
  corroborated §4.1 above) — but its real alternate function is
  **I2C1_SCL** (secondary AF mapping, DS-MCU-053), entirely unrelated to
  boot-mode selection. The original UNKNOWN about whether PB8 was even
  bonded out is now resolved (it is); it was simply never the BOOT0 pin
  to begin with.

The facts that remain unchanged from the original analysis:

- **nBOOT_SEL option byte factory default = 1** (DS-MCU-044, MODERATE
  confidence — corroborated by 2 independent community sources, a Stack
  Overflow STM32G030F6 boot-mode thread and a CSDN technical blog, both
  citing the same FLASH_OPTR reset value; not independently re-confirmed
  against the raw ST RM0454 reference manual table this session). With
  `nBOOT_SEL=1`, the physical BOOT0 **pin is ignored entirely** and the
  device boots unconditionally from Main Flash per the `nBOOT0`/`nBOOT1`
  option bits — i.e., the STM32G0 boot-mode architecture is
  option-byte-driven, not physical-pin-driven, by default. This is a
  materially different scheme from STM32F1, where the BOOT0 pin's level
  is sampled directly at every reset.

**What this correction actually changes**: with BOOT0 now correctly
understood to sit on PA14 (not PB8), a dedicated physical BOOT0 circuit
was **never actually possible** on this design's pin allocation in the
first place — PA14 was committed to SWCLK before BOOT0's real location was
even known (§2.3, step 2 of `SKILL.md`'s "fix shared resources serially
first"), so there was no scenario in which a separate BOOT0 pull
circuit could have been added without giving up SWCLK. This is a
materially more complete justification than the original (mistaken)
"PB8 might not exist" reasoning, though it does **not** change the design
decision itself.

**No brick risk**: independently reconfirmed this cycle that SWD-based
recovery/reprogramming remains available **regardless of `nBOOT_SEL`'s
actual value** — the Cortex-M0+ debug port is independent of the
application boot-mode sequence, so even if the factory default assumption
above turns out wrong at bring-up, the board is recoverable via the
already-present SWD header (§4.4) without any additional hardware.

**Design decision (unchanged)**: **no physical BOOT0 pull-down resistor or
header is populated this cycle.** The design relies entirely on the
nBOOT_SEL=1 factory default (boot from Flash unconditionally); the SWD
header (§4.4) remains the primary and sufficient programming/debug path,
already required independently by REQ-002/REQ-107. This is an explicit
scope-limiting decision flagged to the Hardware Lead/Hardware Reviewer
(§16), not a silent omission — if a future firmware bring-up session
discovers the factory default is not what was assumed, or that
nBOOT_SEL needs to be reprogrammed via SWD (which is itself possible using
only the already-present SWD header, without any extra hardware, and
carries no brick risk per the point above), that is recoverable without a
board re-spin.

### 4.3 NRST decoupling + optional manual reset button (REQ-004, Could)

**Note (ISS-027 cross-reference)**: this MCU's NRST function is
implemented on a shared PF2/NRST pad (physical pin 6, not a fully
dedicated NRST-only pin) — see §2.3/§4.1 for the pin-identity correction.
The circuit design below (internal pull-up, C5 filter cap, optional SW1)
is unaffected by that correction; only the physical pin number changed.

Per ST's own application note **AN5096** "Getting started with STM32G0
MCUs hardware development" (DS-MCU-047): the NRST pin has an internal
pull-up (~40kΩ typical) — no external pull-up resistor is needed. ST's
own recommended external circuit is a **100nF ceramic capacitor (C5) from
NRST to GND** for EMI/glitch immunity, with an **optional
normally-open pushbutton (SW1) from NRST to GND in parallel** for manual
reset. This design includes both: C5 (always populated) and SW1
(populated, satisfying REQ-004's Could-priority manual reset button). No
external debounce circuit beyond C5 is needed — C5 itself provides
adequate debounce for a manual pushbutton on a reset line (standard
practice; the MCU's own reset circuitry is not timing-sensitive to a few
extra milliseconds of bounce).

### 4.4 SWD debug header (REQ-107)

**4-pin header (J3): VDD (3V3 reference) / SWCLK / GND / SWDIO.**
Explicitly **no NRST, no SWO** on this header. This matches ST's own
minimal-header convention on the NUCLEO-G031K8 (same MCU family) CN4
connector (DS-CONN-002, corroborated by SEGGER's own "Connecting to
STM32 Nucleo boards" wiki page, ST Community posts, and stm32-base.org).
This directly answers the design task's question of whether a reset line
or SWO is conventionally included on a minimal SWD header: **no** — a
4-pin VDD/SWCLK/GND/SWDIO header is the established minimal convention,
and this design follows it exactly, satisfying REQ-107 literally (4-pin
SWD, matching "the selected MCU family's standard debug interface").
SWD (2-wire: SWDIO+SWCLK) is used rather than JTAG (5-wire) since SWD is
the lower-pin-count, more commonly used debug interface for Cortex-M0+
parts and is ST's own default recommendation; JTAG remains available on
the silicon (shared pins) but is not broken out to a header this cycle —
not required by any REQ, and would cost 3 more header pins for no
required benefit.

## 5. Block 3 — IMU interface

### 5.1 I2C vs. SPI

**Decision: I2C** (REQ-104 permits either). Rationale: simpler (2 signal
pins vs. SPI's 4), matches the most common breakout-board convention for
this exact part, and this design has no bandwidth pressure — REQ-001 only
requires ≥100Hz ODR, which even a slow I2C bus satisfies with enormous
headroom (a single 6-ax12-byte accel+gyro read at 400kHz I2C, including
register-address overhead, takes on the order of ~0.3–0.4ms — comfortably
faster than the 10ms period a 100Hz ODR requires, leaving >95% of each
period idle). SPI (≤10MHz, DS-IMU per component-selection) would be faster
still but that speed is not needed here.

### 5.2 I2C pull-up sizing (target bus speed: Fast-mode, 400kHz)

Sized using the NXP UM10204 I2C-bus specification formula (new evidence
category `DS-IFACE`, DS-IFACE-001) rather than assuming a generic 4.7kΩ
value without checking suitability:

- `tr ≈ 0.8473 × Rp × Cb` (rise-time vs. pull-up-value vs. bus-capacitance
  relationship)
- `Rp,min = (Vcc − VOL,max) / IOL` (current-sink floor)

With Vcc=3.3V, VOL,max=0.4V, IOL=3mA (Fast-mode DC spec, DS-IFACE-001):
**Rp,min ≈ 966Ω**. With an assumed bus capacitance **Cb≈50pF (ASSUMPTION**
— compact ≤60×40mm 2-layer board, single slave device, short traces,
reasoned as a generous planning estimate covering pin capacitance of both
devices plus PCB trace parasitics): **Rp,max ≈ 7.08kΩ** for a 300ns
Fast-mode rise-time budget.

**Selected: R3 = R4 = 4.7kΩ** (standard E24 value), on SCL and SDA
respectively, both to the 3V3 rail. At the assumed Cb=50pF, actual rise
time ≈**199ns** — comfortably within the 300ns budget (≈101ns/≈34%
headroom). **Sensitivity check** (documented honestly rather than
asserting blanket margin): if actual board parasitic capacitance turns
out higher than the 50pF planning estimate, 4.7kΩ remains compliant up to
**Cb≈75pF** (tr≈299ns, right at the 300ns ceiling) — if PCB layout
ultimately reveals materially more capacitance than assumed (e.g. from
unexpectedly long traces), the resistor value should drop to 3.3kΩ or
2.2kΩ at layout time. This is flagged as a layout-stage confirmation
item, not a currently-known problem.

Both the STM32G031 (**I2C2** — corrected this revision, ISS-011, was
mislabeled I2C1; Fast-mode Plus capable up to 1Mbit/s per DS-MCU-017,
which describes the part's 2×I2C peripheral count/capability generically
and applies equally to either instance since both are the same IP block)
and the BMI270 (I2C, Fast-mode Plus capable up to 1MHz, DS-IMU-007)
support Fast-mode Plus, which structurally exceeds the sink-current
capability needed for plain Fast-mode — so no per-pin current concern on
either device at the chosen 400kHz target speed.

### 5.3 IMU pin-level wiring

Full 14-pin BMI270 LGA pin function table (DS-IMU-077, traced to Bosch's
own datasheet PDF via this session's search):

| Pin | Function | This design's connection |
|---|---|---|
| 1 | SDO | **→ GND** (selects I2C address 0x68 — DS-IMU-076; simplest/default address since only one IMU is on this bus) |
| 2 | ASDx (aux I2C/SPI data) | NC — aux sensor interface unused |
| 3 | ASCx (aux I2C/SPI clock) | NC — aux sensor interface unused |
| 4 | INT1 | NC — see below |
| 5 | VDDIO | 3V3 rail, decoupled by **C7 = 100nF ceramic** |
| 6 | GNDIO | GND |
| 7 | GND | GND |
| 8 | VDD | 3V3 rail, decoupled by **C6 = 100nF ceramic** |
| 9 | INT2 | NC — see below |
| 10 | OCSB (aux SPI CS) | NC — aux sensor interface unused |
| 11 | OSDO (aux SPI SDO) | NC — aux sensor interface unused |
| 12 | CSB | **→ VDDIO** (selects I2C mode — DS-IMU-075; tying to GND or toggling would select SPI instead) |
| 13 | SCx (SCL/SCLK) | **I2C2 SCL** (MCU PA11), pulled up by R3 — corrected this revision, ISS-027 (was PB10, which does not exist on this package; ISS-011 had already corrected the peripheral-instance label to I2C2 but not this pin-existence defect) |
| 14 | SDx (SDA/SDI) | **I2C2 SDA** (MCU PA12), pulled up by R4 — corrected this revision, ISS-027 (was PB11, which does not exist on this package; see the "Rev 2, corrected" changelog entry) |

**INT1/INT2 deliberately left NC** — this design uses **I2C polling**
(host reads new data on a timer), not interrupt-driven acquisition. This
is a deliberate scope decision, not an omission: REQ-001's ≥100Hz ODR
target is easily satisfiable by polling (see §5.1 timing-budget analysis),
so no interrupt line is needed for this benchmark. A future cycle
targeting higher ODR or lower host CPU load could reconsider wiring
INT1/INT2 to spare MCU GPIOs (several remain free, see §11) — this would
be a low-cost future addition, not a re-spin-forcing omission.

**Decoupling**: **100nF ceramic on VDD (C6) and 100nF ceramic on VDDIO
(C7)**, each placed as close to the package as layout allows — per the
BMI270 datasheet's own §7.3.3 "Recommended Schematic," p.30 (DS-IMU-074).
No deviation from the datasheet's own recommended circuit. An optional
1µF bulk capacitor near the IMU (C9) is included for extra noise margin,
also per the same datasheet section.

### 5.4 IMU AMR/ROC compliance

VDD=VDDIO=3.3V. Within VDD AMR −0.3V…+3.6V (DS-IMU-004) and VDD ROC
1.71–3.6V. VDDIO's own ROC is 1.2–3.6V per the approved-part summary; no
separate VDDIO AMR ceiling distinct from the general ~3.6V figure was
found in prior research (DS-IMU-006 caveat carried forward, not re-resolved
this session) — 3.3V sits safely under either reading.

### 5.5 REQ-010 regression check (new Rev 3) — IMU capability unaffected by the motor addition

REQ-010 requires that the existing IMU readout (REQ-001) "shall remain
unaffected/unregressed" by the Rev 3 motor addition. Checked explicitly,
not assumed:

- **Bus**: the IMU stays on I2C2 (**PA11/PA12, corrected via the "Rev 2,
  corrected" pin-identity fix, ISS-027** — was PB10/PB11 through Rev 5;
  this branch's own earlier, narrower "Rev 6"/ISS-026 attempt at the same
  underlying defect is superseded by that more complete fix, see the "Rev
  2, corrected" changelog entry); the new motor subsystem's I2C1 (PB6/PB7,
  §7.5.4) is a **physically distinct peripheral instance** on different
  pins — no bus sharing, no address collision, no added bus traffic or
  timing contention on the IMU's own bus. (This Rev 3 regression-check
  conclusion itself is unaffected by the pin-identity correction: I2C1/
  PB6-PB7 and I2C2/PA11-PA12 remain two distinct peripherals on
  non-overlapping pins.)
- **GPIO**: the five newly-consumed pins (PA8, PA6, PB1, PB6, PB7, §2.3)
  do not overlap any Rev 2 net (I2C2 — **PA11/PA12 as of the "Rev 2,
  corrected" fix, was PB10/PB11 through Rev 5, ISS-027** —, USART2 PA2/PA3,
  LED PA5, SWD PA13/PA14, NRST) — confirmed against the full pin table
  (§11) before allocation, per SKILL.md's "fix shared resources serially
  first" step; re-confirmed since that pin-identity fix that PA11/PA12
  also do not overlap any of these five Rev 3 motor pins (§11, "Rev 2,
  corrected" note).
- **Supply-noise coupling**: the IMU's 3V3 supply is unchanged (still the
  LDO's output, §2.1) and the new VM_MOTOR rail is a **separate source**
  (Option A) — no shared regulator through which motor-switching ripple
  could couple onto the IMU's supply rail. Ground-return coupling (a
  different, real mechanism, since both domains do share one ground net)
  is addressed in §8, not dismissed here.
- **Vibration**: a genuinely new physical effect (REQ-204), addressed in
  §9 — not an electrical "regression" of the IMU's own interface, but a
  new environmental factor the IMU didn't previously have to tolerate.

**Conclusion**: no bus/pin/supply-noise regression found at the interface
level from this addition. The remaining, real cross-domain coupling paths
(common-ground return current, motor-vibration-driven mechanical/thermal
effects) are distinct concerns, tracked in §8 and §9 respectively rather
than folded silently into this regression check.

## 6. Block 4 — Host communication (UART header)

**4-pin header (J2): TX / RX / GND / 3V3** (REQ-106), labeled from the
board's (MCU's) own perspective: TX = PA2 = MCU's USART2 transmit output
(an external USB-serial adapter's RX connects here), RX = PA3 = MCU's
USART2 receive input (an external adapter's TX connects here). This
satisfies REQ-106 exactly ("4-pin UART header (TX, RX, GND, 3V3) for host
communication via an external USB-serial adapter").

**USART1 and LPUART1 both remain free** — the design only commits USART2.
This exceeds the Component Engineer's own note that "one" UART peripheral
should remain genuinely free (both of the *other* two remain free here,
since USART2 is the *only* one consumed of the MCU's 2 USART + 1 LPUART
complement — "2 UARTs" in the approved-part description already accounted
for USART2 as the consumed one). Similarly, on the I2C side (§5): **I2C1
Similarly, on the I2C side (§5): **I2C1 was freed by the Rev 2 IMU-bus
relabeling but is now consumed by the motor subsystem** — the IMU bus
correctly uses I2C2 (**PA11/PA12**, corrected via ISS-027 — mistakenly
documented as the non-existent PB10/PB11 through Rev 2; see the "Rev 2,
corrected" changelog entry and §11), not I2C1 as this document originally
(incorrectly) labeled it (ISS-011, see the changelog and §11) — a genuine
peripheral-margin improvement at the time, not a regression. That freed
I2C1 margin is, in turn, consumed as of Rev 3 by the motor subsystem's
commissioning bus on PB6/PB7 (§7.5.4, §11); only PB8/PB9 (I2C1's
alternate pin pair) remain free today.

No external crystal is populated — the MCU runs off its internal
HSI16+PLL clock. UART bit-time tolerance at typical baud rates (e.g.
115200) is easily met by the internal RC oscillator's accuracy
class for a point-to-point, short-cable UART link; this keeps BOM
minimal (no crystal, no load caps). Documented as a decision, not an
oversight.

## 7. Block 5 — Status LED (REQ-003, Should)

**GPIO PA5 sources current** (active-high drive) through a series
resistor **R5 = 330Ω** to the LED (D1) anode; cathode returns to GND.
Assumed generic indicator LED, **Vf≈2.0V @ ~4mA (ASSUMPTION** — exact LED
MPN not selected this cycle, a generic low-cost indicator LED is a
reasonable stand-in). Current: I = (3.3V − 2.0V) / 330Ω ≈ **3.94mA** — a
modest, clearly-visible indicator current, well within any generic
STM32 GPIO's drive capability (STM32 GPIOs are conventionally rated
for tens of mA per pin in this class of device; not independently
re-verified against the STM32G031's own IOH/IOL table this session —
flagged as an ASSUMPTION in §16, though 3.94mA is such a small fraction of
any plausible GPIO current rating that this is a low-risk assumption).
Satisfies REQ-003 ("visual status/heartbeat LED", Should) — "heartbeat"
implies firmware toggles PA5 periodically, consistent with driving it as
a plain GPIO output rather than a passive always-on power-indicator LED.

## 7.5 Block 5.5 — Motor Driver + Reaction Wheel subsystem (new Rev 3)

Inserted as decimal-numbered §7.5 (between §7 Status LED and §8
Grounding) specifically so every existing §8–§18 cross-reference already
in this document, and every external reference to those anchors from
`validation/`, `datasheets/`, and other files, remains valid — no
renumbering. Implements REQ-007/110 (PWM speed-setpoint interface),
REQ-008/112 (FG tach wiring), REQ-108 (Option A architecture), REQ-109
(separate rail tracking), REQ-111/404 (protection), REQ-204/307
(mechanical/thermal, see §9), on the Component-Engineer-approved,
human-signed-off (ECO-008) T-Motor MN2206-13 KV2000 + TI DRV10983 pairing
(§1). **REQ-009 fence respected throughout**: this section wires an
interface and records commissioning-relevant facts; it contains no
control-loop logic, no PID, no sensor-fusion-driven behavior.

### 7.5.1 New power input: connector choice

**J4 = Same Sky (formerly CUI Devices) PJ-102AH**, a 2.0mm-center-pin,
right-angle, through-hole barrel jack, rated **24Vdc / 5.0A**
(DS-CONN-005). Chosen the same way Rev 2 chose J1 (USB-C) and U4 (the ESD
IC, §3.1/§3.2): a single, real, datasheet-grounded part for a supporting
role, no ≥3-candidate comparison — per this project's own established
threshold ("a real, datasheet-grounded single part is sufficient for
this supporting role"). A barrel jack is the conventional choice for a
bench-test DC power input at this voltage/current class (readily
available mating plugs from bench supplies and LiPo-balance-charger
accessories); PJ-102AH was selected specifically for having a
primary-manufacturer datasheet with a complete, unambiguous ratings table
(unlike several alternatives whose distributor listings lacked a
directly-fetchable primary datasheet this session).

Rated 24V/5.0A gives **~2× voltage margin** over this design's actual
~12V-nominal (2S–3S, 7.4–12.6V per the approved motor's own class,
`bom/component-selection.md`) input and **>4× current margin** over the
worst-case ≤3A motor-rail draw (DS-CONN-005, §17/`hardware/
power-budget.md`). The connector's rating is a **safety ceiling for the
part itself**, not a specification of the external supply the user
plugs in — exactly as Rev 2's own J1 (USB-C receptacle) does not imply
this design specifies or BOMs a USB charger. Center pin = **+**, one
outer terminal = **sleeve/GND**; the datasheet's drawing shows a third
terminal consistent with a normally-closed switch contact (common in
this connector class, e.g. for auto-disconnecting an internal battery
when external power is plugged in) — **deliberately left unpopulated**,
since no requirement calls for power-presence detection this cycle
(flagged as a residual layout-time detail, not a blocking unknown, in the
PJ-102AH metadata file and §16).

### 7.5.2 Protection topology and routing to U5 VCC

Because a barrel jack, unlike the keyed USB-C receptacle, **genuinely can
be reverse-plugged or fed a wrong-polarity supply by a user** (mirroring
Rev 2's own §3.3 rationale for why USB-C itself needs no reverse-polarity
diode), this input gets its own protection stage that Rev 2's USB-C input
does not need:

**J4 (+) → D2 (STPS3L60, series) → D3 (SMBJ16A, shunt TVS) → U5 (VCC,
pins 23/24)**, with J4 sleeve/GND now through **F2** (new, see below), and
D2/D3 return sides and U5's GND/PGND/SWGND all tied to the single common
ground net (§8).

- **D2 = STMicroelectronics STPS3L60** (60V/3A power Schottky rectifier,
  SMB package, DS-PROT-005), in series, blocks reverse-polarity input.
  A Schottky (not a standard silicon diode) was chosen for its lower
  forward-voltage drop, minimizing both conduction loss and the voltage
  "tax" subtracted from the already-modest motor-rail headroom. 60V/3A
  rating comfortably exceeds the DRV10983's own absolute-maximum 3A
  startup/locked-motor current (DS-MTR-056) without being a current
  bottleneck.
- **D3 = Littelfuse SMBJ16A** unidirectional TVS (16.0V standoff / 26.0V
  max clamping voltage @ IPP, SMB package, DS-PROT-004), shunt-connected
  across VCC/GND downstream of D2, absorbs transient surges (e.g. from
  motor-deceleration energy return, or supply-side transients) before
  they reach U5's VCC pin. Chosen over the same-family SMBJ18A
  specifically because SMBJ16A's 26.0V clamp leaves 4.0V/13% margin under
  the DRV10983's 30V VCC absolute maximum rating (DS-MTR-053), versus
  SMBJ18A's tighter 0.8V/3% margin (DS-PROT-004) — a meaningfully safer
  choice for the same package/cost class. Unidirectional (not
  bidirectional) is correct here since D3 sits downstream of D2's
  reverse-blocking action, never itself exposed to reverse polarity.
- **F2 = Littelfuse 30R500UF (new this revision, PCB Engineer at explicit
  Chief Engineer direction, ISS-032 loop-back fix, 2026-09-02)** — a
  second instance of F1's own PTC resettable fuse, now in series between
  J4's sleeve/GND pin and the shared ground net. **Corrected safety
  argument, narrowed to what each element actually covers** (Hardware
  Reviewer finding ISS-032, HIGH): D2's series reverse-polarity
  protection sits in the tip/VM_MOTOR leg and only ever protects against
  an *external* failure mode (a user physically plugging in a
  reverse-polarity supply) — it does nothing for an *internal* failure
  mode, where this design's own J4 pin-mapping ASSUMPTION (§7.5.9 below)
  turns out to be wrong regardless of what the user does. Before this
  fix, J4's sleeve/GND pin tied directly to the shared ground net with no
  protection in that leg at all — if the internal mapping were reversed,
  the barrel jack's full +9-13V supply would be applied directly to the
  board's shared ground reference (used by U1/U2/U3/J1's USB-C GND as
  well) with nothing to stop it. F2 makes this safe *regardless* of which
  physical pin the connector's tip/sleeve actually turns out to be,
  without needing to resolve that ASSUMPTION first: in normal (correctly-
  mapped) operation it simply passes the board's ordinary ground-return
  current (well within its 5A hold rating for this design's ≤3A worst
  case, the same margin F1 already relies on, DS-PROT-006); in the fault
  case (mapping reversed), it sees the full supply rail driving into the
  low-impedance ground plane, trips well below its 40A fault rating, and
  then strongly current-limits in its tripped state — turning an
  indefinite, unprotected hijack into a brief, self-limiting,
  automatically-resettable event. J4's tip/sleeve pin-mapping itself
  remains an open ASSUMPTION, unchanged by this fix, still flagged for
  human verification against the real mechanical drawing before
  fabrication (§7.5.9) — this fix removes the need to resolve it before
  the board can be considered safe either way, it does not resolve it.



**Corrected this revision (ISS-014, HIGH) — 2S is not a viable practical
option through the added diode; 3S-only is a binding constraint**:
combining two datasheet facts not previously cross-checked together
reveals a real, quantitative constraint, independently re-derived by the
Hardware Reviewer against the same two source figures this document
already cited. D2's forward drop is 0.53V typ (@3A/100°C) to 0.62V max
(@3A/25°C) (DS-PROT-005 — real drop at this design's actual ~1.05A
nominal current is expected to be somewhat lower still, so these figures
are used conservatively). U5's UVLO rising (power-up) threshold is
VUVLO_R = 7/7.4/8V min/typ/max, and its UVLO falling (drop-out) threshold
is VUVLO_F = 6.7/7.1/7.5V min/typ/max (both DS-MTR-057).

Stacking these at every relevant corner, not just one:

- **2S nominal (7.4V) − 0.53V typ drop = 6.87V, below VUVLO_R typ
  (7.4V)** — fails to power up **at the typical corner**, not merely a
  rare worst-case one. This is now the headline result; the prior
  revision's framing cited only a single corner and understated the
  likelihood of failure.
- **2S full-charge (8.4V) − 0.62V max drop = 7.78V, below VUVLO_R max
  (8V)** — even a freshly-charged 2S pack does not reliably clear UVLO at
  the worst-case (cold-diode, high-current) corner. The prior claim that
  a freshly-charged 2S pack "clears UVLO with any margin" is **incorrect
  at the max corner and is retracted**.
- **2S mid-discharge (7.0V) − 0.53V typ drop = 6.47V, below VUVLO_F min
  (6.7V)** — a 2S pack that did manage to start up would drop out well
  before reaching a normally-discharged voltage, so 2S offers no usable
  runtime margin even in the best case.
- **3S near-cutoff (9.0V) − 0.62V max drop = 8.38V, above VUVLO_R max
  (8V) by 0.38V** — 3S remains robust even at the simultaneous
  worst-case combination of coldest diode drop and near-cutoff pack
  voltage.

**3S-only is recorded as this design's binding practical constraint**,
not a soft recommendation — 2S is expected to fail under normal
(typical-corner) conditions, not just an edge case. This is a consequence
of adding the (well-justified) series protection diode, not a defect in
the motor/driver selection itself, and is not remedied by changing D2
(STPS3L60 is already a low-VF choice; a lower-VF option would trade off
reverse-leakage/voltage rating and was not judged worth chasing for a
single-diode voltage-margin gain against a 2S edge case — flagged below
for Component Engineer to evaluate, not self-selected). New §7.5.9's F1
(PTC resettable fuse, added this revision for ISS-019) adds an estimated
~0.06V further series drop at the 3S near-cutoff/worst-case corner
(ESTIMATE, no Evidence ID — the datasheet publishes only Rmin initial and
R1max post-trip resistance, not a max-initial figure; 0.02Ω assumed
in-circuit resistance × 3A is a reasonable estimate, not a sourced
figure), narrowing the 3S margin to **≈0.32V (8.32V vs. 8.0V VUVLO_R
max)** — still adequate, and now stated quantitatively rather than left
unstated.

**Cross-document consistency, corrected this revision**: `hardware/
power-budget.md`'s Rail Margin Summary previously stated the opposite
framing for this identical scenario (2S "sits under UVLO_R's max,"
implying 2S might still work at the typical corner) — the Hardware
Reviewer's Cycle 3 finding was exactly this disagreement between the two
documents. Both documents now state the same corner-explicit conclusion
above; see `hardware/power-budget.md`'s Rail Margin Summary (updated this
revision) for the mirrored statement.

**Flagged, not self-resolved** (Hardware Lead mediation per this agent's
"Out of scope" instructions): (a) propagating this 3S-only constraint
into `bom/component-selection.md`/`requirements/requirements.md` — both
outside this agent's edit scope; (b) evaluating a lower-VF ideal-diode/
ORing-FET reverse-polarity topology if 2S support is later required — an
architecturally significant part-class change, Component Engineer's call,
not self-selected here (§16 item 17).

### 7.5.3 U5's internal regulator: configured so it cannot power the MCU/IMU domain

The DRV10983 integrates a step-down regulator that can be configured
**buck mode** (external inductor, up to 100mA external load, "can also be
used to provide power for an external circuit such as a microcontroller")
or **linear mode** (external resistor replacing the inductor). This
design uses **linear mode**, configured via **R9 = 39Ω ¼W** between U5's
SW and VREG pins (DS-MTR-065's Table 11 reference value), specifically
**because** Table 10's own Recommended Operating Conditions state linear
mode's external-load current capability is **0mA** (DS-MTR-064) — not
merely "this design chooses not to route it there," but a
datasheet-stated structural guarantee that this regulator mode cannot
supply an external load. This directly satisfies the task's explicit
constraint that U5's own internal regulator "must not be tapped to power
the MCU/IMU domain, which stays exactly as Rev 2" — the MCU/IMU domain's
3V3 rail continues to come exclusively from U3 (TLV75533PDBVR), unchanged
from Rev 2, with **no electrical connection whatsoever** between U5's
VREG/V1P8/V3P3 outputs and the U3-derived 3V3 rail.

**U5's own V3P3 output (5mA max load, DS-MTR-069) is used only to bias
this design's own new pull-up resistors** (R6/R7/R8, §7.5.4/§7.5.5) —
this is a few-hundred-microamp biasing function, not "powering a domain,"
and is explicitly distinct from the higher-current VREG output this
paragraph constrains. Three pull-ups (SCL/SDA/FG) at worst case
simultaneously low draw ≈3×0.7mA≈2.1mA, comfortably under V3P3's own 5mA
ceiling.

**Decoupling and external components**, per DRV10983's own Table 11
reference circuit (DS-MTR-065, checklist item 17 — no deviation): C10 =
10µF (VCC–GND), C11 = 0.1µF/10V (VCP–VCC), C12 = 0.1µF rated ≥VCC×2
(CPP–CPN), R9 = 39Ω ¼W (SW–VREG, linear-mode select, per above), C13 =
10µF/10V (VREG–GND), C14 = 1µF/5V (V1P8–GND), C15 = 1µF/5V (V3P3–GND).
All placed close to U5's package per standard practice; no deviation from
TI's own recommended values.

### 7.5.4 MCU pin allocation and DRV10983 signal-pin wiring

DRV10983's real 24-pin HTSSOP pinout was pulled from its primary
datasheet pin-by-pin (DS-MTR-052) specifically to avoid assuming a
generic H-bridge pin set — confirmed: **no dedicated enable or fault
pin exists on this part.** Enable/disable is via the SPEED command
itself (commanding zero speed), and fault visibility is I2C-register-only
(Status register 0x10) or inferred from FG held high during a lock
condition. The signal pins actually needed are SPEED, DIR, SCL, SDA, and
FG — five pins, matching this design's five newly-allocated MCU pins:

| U5 pin (DRV10983) | Function | MCU pin | Peripheral | Confidence |
|---|---|---|---|---|
| 13 (SPEED) | Speed command (PWM, this design — §7.5.5) | **PA8** | TIM1_CH1 (AF2) | HIGH (pin name/AF, DS-MCU-069/Table 13); physical LQFP-32 pin number now also HIGH (§11, DS-MCU-064) |
| 14 (DIR) | Direction command | **PB1** | Plain GPIO, push-pull output | HIGH (no AF conflict); physical pin number now also HIGH (§11, DS-MCU-064) |
| 12 (FG) | Tach/speed-indicator output (open-drain, DS-MTR-069) | **PA6** | TIM3_CH1 input-capture (AF1) | HIGH (pin name/AF, DS-MCU-069/071/Table 13); FT_ea 5V-tolerant (cross-domain safety, DS-MCU-071); physical pin number now also HIGH (§11, DS-MCU-064) |
| 10 (SCL) | I2C1 clock | **PB6** | I2C1_SCL (AF6) | HIGH (pin name/AF, DS-MCU-070/Table 14); physical pin number now also HIGH (§11, DS-MCU-064); Fm+/FT_f tolerance is a MODERATE-confidence family generalization, not independently re-confirmed against a Table-18 FT_f line item this session (§16) |
| 11 (SDA) | I2C1 data | **PB7** | I2C1_SDA (AF6) | HIGH (pin name/AF, DS-MCU-070/Table 14); same physical-pin-number (now HIGH, §11) and Fm+-tolerance caveats as SCL |

**PA8 chosen for SPEED/PWM** because TIM1 is this MCU's advanced/
motor-control-oriented timer and PA8 is TIM1_CH1 — a natural fit, and
confirmed genuinely free in Rev 2's own inventory (§11 before this
revision). **PA6 chosen for FG** specifically for its confirmed FT_ea
5V-tolerance (DS-MCU-071) — even with the MCU domain fully unpowered
(VDD=0), U5's V3P3-referenced FG pull-up (≤3.6V max, DS-MTR-053) sits
within PA6's VDD+4.0V=4.0V absolute ceiling with no significant
forward-injection path, per the same analysis already used to validate
this pin (§7.5.6 continues this point for the pull-up sizing itself).
**PB1 chosen for DIR** as a plain free GPIO — no AF requirement since DIR
is a simple push-pull digital command, not a timer/analog function.
**PB6/PB7 chosen for I2C1** because they are this MCU's I2C1 primary AF
pair (DS-MCU-070), and — critically — I2C1 was recorded as entirely free
margin after Rev 2's own ISS-011 correction (§2.3); no conflict with the
IMU's I2C2 bus (**PA11/PA12 as of the "Rev 2, corrected" pin-identity fix
— was PB10/PB11 as originally documented through Rev 5; ISS-027 moved the
IMU bus off PB10/PB11 because those pins do not exist on this package,
but this Rev 3 PB6/PB7 allocation was never on PB10/PB11 in the first
place, so this conclusion is unaffected**),
which remains completely untouched by the motor subsystem either way.

**Pull-up resistors** (per DRV10983's own Table 11 reference circuit,
DS-MTR-065 — checklist item 17, no deviation): **R6 = 4.75kΩ** (FG, pin
12), **R7 = 4.75kΩ** (SCL, pin 10), **R8 = 4.75kΩ** (SDA, pin 11) — all
three referenced to **U5's own V3P3 output** (§7.5.3), a deliberate
cross-domain choice (not the MCU's 3V3), justified by the FT-pin
tolerance analysis above/DS-MCU-071. This differs from the IMU's I2C2
pull-up sizing method (§5.2, an NXP UM10204-formula derivation assuming
an MCU-side 3.3V pull-up rail) because this bus's pull-up reference is
the driver's own V3P3 domain, a different electrical context — reusing
TI's own recommended reference-circuit value directly is the more
appropriate and more conservative choice here (checklist item 17: follow
the datasheet's own recommended application circuit).

### 7.5.5 SPEED/DIR interpretation and I2C commissioning requirement

**SPEED's interpretation (analog vs. PWM) is register-selected, not
fixed in hardware**: `SpdCtrlMd`=0 selects analog-voltage mode
(full-speed = V(V3P3)×0.9, zero-speed = 100mV); `SpdCtrlMd`=1 selects
PWM-digital mode (VDIG_IH≥2.2V, VDIG_IL≤0.6V, input frequency 1–100kHz)
(DS-MTR-068). **REQ-007 (PWM/duty-cycle speed-setpoint control) requires
`SpdCtrlMd`=1** — this design wires PA8/TIM1_CH1 to drive SPEED as a PWM
signal, but the pin is functionally inert as a *PWM* input until
`SpdCtrlMd` is actually set to 1 via I2C or EEPROM (a firmware/
commissioning task, REQ-009 fence preserved — this document wires the
interface, it does not perform the configuration).

**The I2C1 bus is more than optional future tuning — it is this design's
practical commissioning path**, upgraded in framing this revision from
earlier assumptions: DRV10983 requires motor-specific **Rm (phase
resistance, 7-bit register, 9.67mΩ/LSB, 0–18.5Ω range)** and **Kt (BEMF
constant, 7-bit register, 0–1760mV/Hz range)** parameters for correct
sensorless commutation (DS-MTR-070). The device *can* run from its
integrated EEPROM's stored defaults with **zero I2C connection ever
made** — but generic EEPROM defaults are very unlikely to match the
T-Motor MN2206-13 KV2000's actual Rm/Kt, so correct/optimized commutation
for this specific motor pairing practically requires programming these
registers at least once via I2C (register-mode writes bypass the EEPROM
defaults, DS-MTR-070). **Wiring PB6/PB7 is this design's job; measuring
and writing the actual Rm/Kt values, and setting `SpdCtrlMd`=1, is a
firmware/commissioning task** — consistent with REQ-009's fence (motor-
parameter values are not closed-loop control logic).

**DIR** has no internal bias documented in the datasheet (only SPEED's
pulldown was called out, DS-MTR-069) but is actively driven by MCU PB1 as
a push-pull output — the practical floating-at-MCU-reset window (before
firmware initializes PB1) is a low-severity residual concern (worst
case: an undefined direction command during a window when SPEED's own
bias — R10, below, added this revision — already tends toward zero
commanded speed) — noted in §16, not treated as requiring an added
component (ISS-016, LOW, out of this revision's rework scope).

**Corrected this revision (ISS-015, HIGH) — the prior "deliberate
non-addition" stance for a SPEED pulldown is reversed; a real external
pulldown is added.** Cycle 3 review (Hardware Reviewer + rubber-duck)
found this section's own prior reasoning insufficient on two independent
grounds, both accepted here rather than re-argued:

1. **The factory-default SPEED state is analog mode, not inert.**
   `SpdCtrlMd`'s factory-default EEPROM value (Table 8, register
   0x2B=0x0C, decoding bit1=0=analog mode) means U5 boots into **analog**
   mode, not PWM mode, in any uncommissioned window — and per the same
   datasheet's §8.4.5.2, analog mode is fully active out of reset, not
   inert: it interprets any voltage on SPEED as a real, proportional
   commanded speed (stop below VANA_ZS=100mV, ramping linearly to full
   speed at/above VANA_FS=V(V3P3)×0.9) (**DS-MTR-071**, added by the
   Hardware Reviewer this cycle). This directly corrects — and
   supersedes — this section's own prior reliance on **DS-MTR-068**'s
   closing phrase (qualified in place by the Hardware Reviewer,
   2026-09-05, not deleted, so the correction stays auditable) that
   called SPEED "functionally inert until [PWM mode] is configured":
   that phrasing is accurate only for the *PWM-mode* interpretation, not
   for the pin's real, active behavior in its own factory-default analog
   state.
2. **The internal pulldown this section previously relied on as a
   partial mitigant does not clearly cover the part actually specified.**
   `RPD_SPEED_SL` (55kΩ typ, DS-MTR-069) is listed in the primary
   datasheet's Electrical Characteristics table under the section header
   **"SLEEP MODE (DRV10983Z)"** — textually grouped with, and
   characterized alongside, the sleep-capable **DRV10983Z** variant's own
   sleep-mode parameters. This design specifies the **plain DRV10983**
   (confirmed via §13's own parts list — no Zener/sleep-pin component
   populated), which has a separate **"STANDBY MODE (DRV10983)"** section
   in the same table that does **not** list any internal-SPEED-pulldown
   parameter at all. This does not prove the physical pulldown structure
   is absent on the plain part's silicon (variants in one package are
   often the same die with different firmware-configured feature sets) —
   only that the datasheet neither documents nor guarantees it for the
   part actually specified here, a more specific weakening of this
   section's own prior "partial mitigant" framing than previously
   acknowledged.

**Fix**: new **R10 = 1kΩ, 0603**, wired from the SPEED net to common
ground (§8) — a real external pulldown, not relying on any internal/
undocumented bias. Sized (ASSUMPTION, no datasheet SPEED-pin leakage
figure exists to size precisely against) so that any realistic pin
leakage or stray capacitive/coupling current produces a voltage far below
VANA_ZS=100mV across 1kΩ, dominating over leakage currents many times
larger than a typical CMOS-class input would present. This is an
explicit, acknowledged deviation from TI's own Table 11 reference
circuit, which lists no external SPEED pull component (independently
cross-checked by the Hardware Reviewer via DS-MTR-071) — justified
because Table 11 implicitly assumes a single always-alive host system,
which this design's dual-independent-power-domain (Option A) architecture
does not have (the Hardware Reviewer's own Recommended Fix option 1). R10
draws from the **3V3 rail**, not VM_MOTOR, only while MCU's PA8 GPIO
drives HIGH; see `hardware/power-budget.md` for the added worst-case load
(§17).

**Bounding factor, honestly retained from the Hardware Reviewer's own
finding** (this fix reduces risk — it does not retroactively make the
underlying hazard chain hypothetical): even before this fix, any
resulting motion would have been ramped/current-limited (`StAccel`/
`OpenLCurr`, Table 6, per DS-MTR-071's own cross-check) using
generic/unmatched commutation parameters, not an instantaneous
full-speed event. R10 is added specifically so this bounding factor is
no longer the *only* thing standing between the factory-default
analog-mode state and an actual uncommanded-motion event.

**Flagged, not self-resolved** (Hardware Lead mediation, per this
agent's "Out of scope" instructions): (a) a supervisory load switch
gating U5's own VCC on the MCU domain's power state — the Hardware
Reviewer's own Recommended Fix option 2, which would directly enforce
the missing cross-domain power-up ordering rather than only bounding
SPEED's voltage — specified as a new part's required function in new
**§7.5.10** below, routed to Component Engineer via Hardware Lead as an
architecturally significant choice, not self-selected; (b) REQ-403's own
explicit requirement that final disposition of this class of finding
receive human safety review before any Design Complete gate — this
applies regardless of which technical fix is chosen, and is not
something this agent can self-grant (`docs/architecture.md` §8).

### 7.5.6 Protection (REQ-111/404) — DRV10983's real mechanisms confirmed

Five **distinct** protection mechanisms are confirmed directly from the
DRV10983's own datasheet (not assumed to be "on" by default):

| Mechanism | Trigger | Response | Evidence |
|---|---|---|---|
| Overcurrent Protection (OCP) | IOC_limit = 3 MIN/4 MAX A, phase-to-phase, fixed/non-configurable | Hi-Z output, auto-clears once overcurrent condition is no longer present (condition-based, not a fixed retry timer) | DS-MTR-058 |
| Lock Detection | 6 independently-maskable sub-schemes (`LockEn[5:0]`) — current-limit (`HWiLimitThr`), abnormal speed, abnormal Kt, no-motor-detected, open-/closed-loop-stuck | Hi-Z output, auto-**retry** after tLOCK_OFF=5s | DS-MTR-059 |
| Undervoltage Lockout (UVLO) | VUVLO_F=6.7/7.1/7.5V falling, VUVLO_R=7/7.4/8V rising | Shuts down below threshold, auto-recovers above | DS-MTR-057 |
| Thermal Shutdown | TSDN=150°C, 10°C hysteresis | Shuts down, auto-recovers on cooling | DS-MTR-060 |
| Voltage Surge (AVS) | Mechanical AVS (motor-deceleration energy return) | Clamps/limits VCC surge | DS-MTR-061 |

All five are hardware-automatic (no firmware polling required for the
protection itself to engage) — satisfying REQ-111's "Should" for
built-in overcurrent/stall protection suitable for repeated bench
testing without added circuitry. I2C read access to the Status register
(0x10) additionally lets firmware **distinguish which** mechanism
tripped (OCP=bit5, MtrLck=bit4, OverTemp=bit7) rather than only
observing "FG held high" generically — valuable for REQ-404's
stall-detection/shutdown behavior, though that behavior itself is a
firmware-level concern (REQ-009 fence).

**Correction found against `bom/component-selection.md` — flagged
narratively, not self-numbered as a new ISS**: that document's DS-MTR-037
describes DRV10983 overcurrent protection as "programmable via I2C…
auto-retry." Primary-datasheet verification this revision shows that
description in fact applies to **Lock Detection** (DS-MTR-059, genuinely
configurable/auto-retry), not to **OCP** itself (DS-MTR-058, fixed
threshold, condition-based auto-clear, not a retry timer). Per this
document's own established precedent (`validation/open-issues.md`/
`validation/design-review.md` are Hardware-Reviewer/Hardware-Lead-owned
registries, not touched by this agent, and no ISS number has ever been
self-assigned by the Circuit Engineer in this project), this correction
is recorded here and in `datasheets/
texasinstruments_drv10983_slvscp6h.md`'s own Update section, **not**
by editing `bom/component-selection.md` and **not** by inventing a new
ISS number — for the Hardware Reviewer/Hardware Lead to log formally in
their own registry if they concur. The correction does not change this
design's actual wiring or component choice — both mechanisms exist and
both are hardware-automatic; only the *description* of which mechanism
does what was imprecise upstream.

### 7.5.7 ECO-008 directive — BEMF/FG low-RPM degradation

ECO-008 (`validation/change-log.md`) carries a human directive that the
DRV10983/T-Motor pairing's BEMF-derived FG signal typically degrades
below ~500–1500 RPM, and that this caveat **must** be tracked in the
Firmware bring-up plan and/or `validation/fmea.md` — not resolved here.
Respecting that directive (this is primarily a Firmware Engineer/FMEA
item), this design nonetheless records the one concrete **circuit-level**
fact found that substantiates and gives firmware real hooks for that
concern, per this agent's own instructions ("if there's a real
circuit-level mitigation or note worth recording... flag it... don't
silently omit it"):

- **`FGOLsel[1:0]`** (register, SysOpt9 0x2B bits 7:6, DS-MTR-062)
  configures FG's behavior during open-loop operation: by default (00),
  FG toggles at the **commanded drive frequency** during open-loop
  (which is not yet BEMF-sensed speed — the datasheet's own words: "this
  may not reflect the actual motor speed"), or can be configured to hold
  FG high during open-loop instead (01/10 settings).
- **`Op2ClsThr[4:0]`** (register, SysOpt4 0x26 bits 7:3, DS-MTR-063) sets
  the open-to-closed-loop transition threshold — below it, commutation is
  forced/open-loop (Align+IPD, then Accelerate, per the datasheet's own
  state-machine description) and is not BEMF-dependent at all, meaning
  motor **starting** never relies on a valid BEMF-derived FG reading;
  only FG's fidelity as a *speed-feedback* signal during that specific
  low-RPM phase is reduced.

Both registers are reachable via this design's I2C1 bus (§7.5.4/§7.5.5)
— wired and available, not configured by this circuit design (REQ-009
fence). Routed to Firmware bring-up/FMEA per the human directive, with
these two named, real register hooks recorded here so that work does not
have to rediscover them from scratch.

### 7.5.8 Power-up sequencing (checklist item 10)

DRV10983's own recommended power-up connection order is 1) GND, 2) VCC,
3) PWM(SPEED), 4) FG — with the datasheet noting that once VCC>2.2V the
FG/PWM order no longer matters, but explicitly cautioning to "ensure FG ≤
VCC at all times" (DS-MTR-066). Because Option A deliberately makes the
MCU/IMU domain and the U5/motor domain **independently sourced** (no
shared regulator, no defined mutual power-up ordering), there is no
hardware guarantee that the MCU's GPIOs are already initialized before
U5's VCC ramps, or vice versa.

**Severity corrected this revision (ISS-015, HIGH)**: this cross-domain
sequencing gap was previously framed here as "real, if low-severity" —
that framing is retracted. Cycle 3 review found the same gap ties
directly to REQ-403 (safety-critical, human-review-gated) precisely
because, absent any supervisory gating, the "uncommissioned" window (U5
powered, MCU either not yet powered or not yet finished with GPIO/I2C
init) is not bounded to be short — it could persist indefinitely
depending on bench connection order, during which U5 runs in its
factory-default active analog SPEED mode (§7.5.5, DS-MTR-071). New R10
(§7.5.5, this revision) now firmly bounds SPEED's own voltage during this
window regardless of sequencing, which is this revision's actual fix for
the voltage-level part of the hazard — but R10 does **not** itself
enforce a power-up *order*, only a safe SPEED *level* whenever the MCU
side is not actively driving it. Directly enforcing the missing
cross-domain ordering (rather than only bounding SPEED's level) would
require a supervisory component — **flagged in Rev 4's §7.5.10, now
implemented as U6 in §7.5.10 below (Rev 5)**, not added as a passive fix
here, consistent with §7.5.5's own disposition of this same finding.

### 7.5.9 J4 input envelope and upstream fault containment (new, ISS-019)

**Fixed this revision (ISS-019, HIGH) — a binding source voltage/current
envelope is defined, and a new upstream protection part is added.** Prior
revisions described VM_MOTOR informally as "~12V-class, 2S–3S LiPo"
without ever stating a bound every part in the path is checked against,
and without any protection element upstream of U5's own internal,
downstream-only OCP (§7.5.6) — a fault between J4 and U5 (e.g. a shorted
or reverse-inserted external supply lead) had no coordinated
containment: J4 is rated 5.0A (DS-CONN-005), D2 is rated for its own
repetitive/surge figures (DS-PROT-005), D3 clamps transients only
(DS-PROT-004) — none of these is a deliberately-chosen fault-current-
limiting element; each is simply rated high enough not to be the binding
constraint on its own.

**Binding voltage envelope: 9.0V to 13.0V.** Lower bound (9.0V) is 3S's
own near-cutoff voltage (§7.5.2); upper bound (13.0V) is 3S's own
full-charge voltage (12.6V) plus ~3% headroom for a slightly-miscalibrated
bench supply, while remaining well clear of a 4S pack's own nominal
(14.8V) or full-charge (16.8V) voltage. This is a **binding constraint**,
not a description — an operator connecting a 4S pack, or a bench supply
mis-set above 13.0V, is outside this design's qualified input envelope.
This does not change D3's own role: D3 remains a transient/surge-only
backstop at 26.0V max clamp (DS-PROT-004) — it is not repurposed as, nor
claimed to be, a continuous-overvoltage bound; a sustained 4S connection
would sit below D3's own clamp voltage and would not be caught by D3 at
all, which is exactly why a true continuous-OVP stage is flagged below,
not claimed solved by D3.

**New F1 = Littelfuse 30R500UF** *(swapped from 30R500U this revision,
Rev 5 — see below)*, a radial-leaded PTC (polymeric
positive-temperature-coefficient) resettable fuse (**DS-PROT-006**):
Ihold=5.00A, Itrip=10.00A, Vmax=30Vdc, Imax=40A (fault current),
Rmin=0.010Ω (initial), R1max=0.050Ω (post-trip). Placement: J4(+) →
**F1** → D2 (anode) → D3 (shunt) → **U6 (Rev 5)** → U5 VCC — upstream of
both existing protection parts, closest to the actual external-fault
entry point.

**Swap rationale (Rev 5, independently confirmed this session via web
search, DS-PROT-032):** the previously-specified 30R500U is obsolete
(no live distributor stock, per Component Engineer's own prior-session
finding, DS-PROT-009); Littelfuse's own current product listing gives
**30R500UF** as the direct, manufacturer-recommended replacement —
Active/orderable status, RoHS3-compliant construction — with no change
to any electrical or mechanical rating (same document family as
DS-PROT-006, confirmed specifically for the electrical/mechanical
identity claim under **DS-PROT-033** below).
Ihold (5.00A) sits above this design's own ≤3A worst-case operating
current (§7.5.4 item 5) with margin, so F1 will not nuisance-trip under
any expected operating condition, including U5's own OCP fault condition
(IOC_limit=3 MIN/4 MAX A, DS-MTR-058) — F1 is a slower-acting,
higher-threshold backstop behind U5's own internal protection, not a
replacement for it.

**Honestly scoped, not overclaimed**: F1's own Itrip (10.00A) exceeds
J4's own 5.0A connector rating (DS-CONN-005) — F1 is not a precisely-
matched current limiter for J4 itself, and a fault current between 5A
and 10A would exceed J4's own rating before F1 trips. F1's real
protective value is against genuine short-circuit-level fault currents
(well above 10A, tripping in seconds per its own time-to-trip curve),
not as a tight bound on J4's own rating — this gap is exactly why a true
input eFuse/active current-limiting stage is flagged below, not claimed
closed by F1 alone.

**Thermal derating (ambient)**: per Littelfuse's own published Ihold
temperature-derating table (30R500 row — shared by 30R500U and 30R500UF,
same datasheet PDF, DS-PROT-006/DS-PROT-033: 5.00A@20°C baseline, 3.85A@50°C,
3.40A@60°C, 3.05A@70°C, 2.60A@85°C), F1's derated hold current remains
**at or above** this design's ≤3A worst-case current through the
datasheet's own 70°C point (3.05A), dropping below 3A somewhere between
70°C and 85°C — interpolating linearly between those two published
points, ≈71.7°C. Comfortably above REQ-201's 40°C ambient design target
either way, with no bench-top ambient scenario expected to approach this
limit.

**Series-drop impact already incorporated in §7.5.2, not a separate
concern**: F1 adds an estimated ~0.06V further worst-case series drop
(ESTIMATE, no Evidence ID — the datasheet publishes only Rmin initial and
R1max post-trip resistance, not a max-initial figure; 0.02Ω assumed
in-circuit resistance × 3A) — already folded into §7.5.2's corrected
3S-margin figure (≈0.32V), not double-counted here.

**Flagged in Rev 4, resolved this revision (a) / still flagged (b)**:
(a) a true hardware-enforced continuous input overvoltage lockout — F1
and D3 together bound fault currents and transients respectively, but
neither bounds a sustained, out-of-envelope DC input voltage (e.g. a 4S
pack held connected) — **this is now closed by U6's OVP function
(§7.5.10, Rev 5)**, an active comparator+switch stage referenced to this
same 9.0–13.0V envelope, unified with ISS-015's load-switch function and
ISS-021's latched-cutoff enforcement point in the same part rather than
three separately-specified components; (b) recording the 9.0–13.0V
envelope in `validation/bring-up-procedure.md`'s eventual motor-rail
bring-up section — that document is not edited by this agent, still
flagged for whoever owns it next (§16).

### 7.5.10 U6 = TPS26631PWPR — supervisory motor-rail protection controller (IMPLEMENTED this revision, Rev 5 — closes ISS-015/019 residuals, gives ISS-021 its hardware enforcement point)

**Part identity and human approval.** Rev 4 deliberately specified only
function and ratings here, judging a controller that actively gates U5's
VCC architecturally significant and out of this agent's own
part-selection scope. Component Engineer subsequently proposed **U6 = TI
TPS26631PWPR** (TPS2663x family, 20-pin HTSSOP/"PWP", 4.5–60V IN, 6A,
integrated OVP/UVLO/adjustable-current-limit eFuse/load-switch), and the
human Chief Engineer approved it (`bom/component-selection.md`
"Motor-Rail Supervisory Controller" §Approval: "**Approved — 'TPS26631PWPR
confirmed.'**"), directing "Circuit Engineer to implement: the load
switch + external EN pull-down (fail-safe-OFF direction) + OVP/UVLO
dividers, in a new Rev 5." Confirmed approved before use, per this
agent's own "Process" step 1. Placement: **F1 → D2 → D3 → U6 → U5 VCC
(pins 23/24)** — one part serving all three of Rev 4's flagged uses
(load-switch/ISS-015, continuous OVP lockout/ISS-019 residual,
firmware-commandable cutoff/ISS-021's enforcement point), not three
separately-specified redundant components.

**Pinout and connections** (TI SLVSE94G Table 5-1, **DS-PROT-023**; pin
numbers below are the PWP/20-pin column): pins 1–3 **IN** and pins 18–20
**OUT** are each tied together in parallel per TI's own instruction ("Do
not leave any of the IN and OUT pins un-connected," §8.3.11) — IN ties to
D3's downstream node, OUT ties to U5 VCC and the existing **C10** (10µF);
pin 6 **IN_SYS** ties directly to IN (no external reverse-polarity FET —
see below); pin 7 **UVLO** and pin 8 **OVP** are the new divider taps
(below); pin 9 **GND** and the **PowerPAD** both go to the ground plane —
TI's own pin description requires the PowerPAD be soldered to the GND
plane *in addition to* pin 9, not as a substitute for it (**DS-PROT-023**);
pin 10 **dVdT** gets new **C17** (below); pin 11 **ILIM** gets new **R15**
(below); pin 12 **MODE** is left open (below); pin 13 **SHDN** gets new
**R11** and the MCU drive (below); pin 16 **PGTH** ties to GND (below);
pins 14/15/17 (**IMON/FLT/PGOOD**) and pins 4/5 (**B_GATE/DRV**) are left
floating (below).

**Load-switch function (ISS-015) — IN_SYS/IN tied together, no external
reverse-polarity FET.** TI's own §8.3.11 guidance: "If the external
N-channel FET is not used then connect IN_SYS and IN together and leave
B_GATE and DRV pins floating" (**DS-PROT-023**) — this design does not add
Q1/Q2 (TI's own optional external reverse-polarity FETs, §9.4 "Dos and Do
Nots") because reverse-polarity protection is already provided upstream
by the existing series Schottky **D2** (§7.5.9) — adding TI's optional
FETs here would be redundant, not a gap. B_GATE's own pull-down
(Rpd_BGATE = 800/1010/1200 kΩ min/typ/max) and DRV are both left
unconnected accordingly. U6's own OUT/C(OUT) decoupling reuses the
**existing C10 (10µF)** — no new output capacitor is added; C10 already
sits on the U5-VCC node U6's OUT now feeds directly.

**EN/SHDN pull-down — new R11 = 10 kΩ, SHDN pin (13) to GND.** SHDN low =
OFF (TI Table 5-1: "Pulling SHDN low makes the device...enter into low
power shutdown mode"); the part's own internal pull-up defaults it high
(ON) absent an external pull-down — inverted here to the required
default-OFF/fail-safe direction per REQ-403, exactly as Rev 4's §7.5.10
spec required.

*Primary sizing basis (guaranteed spec, not an assumed resistor value)*:
TI's own Electrical Characteristics table gives **I(SHDN) leakage current
= 10 µA max at V(SHDN) = 0 V** (a real, guaranteed, tested limit — not a
typical/illustrative figure), and TI's own application text states
explicitly: **"To assert SHDN low, the pulldown must have sinking
capability of at least 10 µA"** (SLVSE94G §8.3.13, **DS-PROT-024**). With
R11 = 10 kΩ sinking this guaranteed 10 µA worst case, the resulting
V(SHDN) ≈ 10 µA × 10 kΩ = **100 mV** — measured against TI's own
guaranteed SHDN thresholds (**DS-PROT-024**): V(SHUTF) = 0.8 V (falling/
shutdown-confirm threshold) → **≈8× margin**; V(SHUTR) = 2 V (rising/
enable threshold, the tighter constraint for guaranteeing the device
cannot self-enable from a cold, undriven start) → **≈20× margin**. R11's
ceiling for TI's own 10 µA/0.8 V requirement is 80 kΩ; 10 kΩ sits 8× below
that ceiling, chosen (rather than something smaller, e.g. 1 kΩ) to limit
the ≈330 µA the MCU's 3V3 rail must additionally source whenever PA9
drives SHDN high (§17/`hardware/power-budget.md`) — a different design
driver than R10's own 1 kΩ (§7.5.5, an analog-level SPEED pulldown
against U5's own input impedance, not a digital logic pin against this
part's own leakage spec); the two are not expected to match.

*SHDN internal pull-up resistance — discrepancy found and reconciled, not
blocking.* The task's own framing (independently re-confirmed by the
human via a fresh web search, `bom/component-selection.md`'s Approval
table) cites "a genuine internal ≈440 kΩ EN pull-up." This session's own
direct visual read of TI's Figure 8-1 functional block diagram shows
**"1 MegΩ"** at the SHDN node, pulling up to an internal 2.7V rail
(**DS-PROT-025**) — matching the pre-existing **DS-PROT-013** (a TI E2E
forum citation, recorded by Component Engineer before this revision) and
the pre-existing Component Engineer datasheet metadata file, both of
which already state 1 MΩ. **Neither figure is a guaranteed Electrical
Characteristics table spec** — TI shows 1 MΩ only in the functional
(illustrative) block diagram, with no formal min/typ/max table row for
this specific resistance (**DS-PROT-025**) — which is a plausible reason
different sources report different figures. Not treated as blocking:
R11's sizing basis above uses only guaranteed specs, independent of
either figure; as a secondary, non-blocking corroboration, R11 = 10 kΩ
still dominates by ≈44× (using 440 kΩ) or ≈100× (using 1 MΩ) at the
resistor-ratio level either way. Flagged for Hardware Reviewer/Component
Engineer awareness — see §16.

**OVP/UVLO resistor divider — new R12 = 887 kΩ, R13 = 60.4 kΩ, R14 = 88.7
kΩ (all E96, 1%)**, referenced to §7.5.9's 9.0–13.0V binding envelope, per
TI's own divider architecture (SLVSE94G §9.2.2.2, **DS-PROT-026**):
**IN_SYS/IN —[R12]— UVLO (pin 7) —[R13]— OVP (pin 8) —[R14]— GND**. TI's
own Equations 9–10: V(OVPR) = [R14/(R12+R13+R14)]·V(OV), V(UVLOR) =
[(R13+R14)/(R12+R13+R14)]·V(UV) — independently re-derived from scratch
against this design's own target trip points (not copied from TI's own
worked example, which targets a different, 24V-class envelope) and
verified by back-substitution.

*Trip points, using TI's own guaranteed reference voltages* (V(UVLOR) =
V(OVPR) = 1.176/1.200/1.224 V min/typ/max, **DS-PROT-026**):
- **UVLO rising**: 8.1721 / 8.3388 / 8.5056 V (min/typ/max, reference
  tolerance only, resistors ideal). All three sit below the 9.0V floor —
  **honestly scoped, not overclaimed**: this means U6 may turn on
  slightly before VM_MOTOR technically reaches the nominal 3S-near-cutoff
  floor (encroachment up to ≈0.83V in the worst corner), which is a minor
  conservatism gap against the *stated* 9.0V design intent, not a safety
  violation — no downstream part is at risk operating down to ≈8.2V, U5's
  own UVLO (§7.5.2) is the part that actually matters for low-voltage
  safety and is unchanged by U6.
- **OVP rising**: 13.7368 / 14.0171 / 14.2975 V (min/typ/max, reference
  tolerance only). All three sit above the 13.0V ceiling with margin — the
  safety-relevant direction (blocking a 4S pack or an out-of-envelope
  bench supply from reaching U5): worst-case-max trip (14.2975V) still
  leaves **0.503V/3.4% clearance** below a 4S pack's own nominal 14.8V
  (sanity check — a 4S pack is correctly rejected before it is ever
  mistaken for being in-envelope).
- **Full-stack worst case** (TI's ±2% reference tolerance **and** ±1%
  resistor tolerance both stacked adversely — a more conservative bound
  than reference-tolerance-alone above): UVLO = 8.6527V (0.3473V/3.86%
  margin below the 9.0V floor); OVP = 13.4881V (0.4881V/3.75% margin above
  the 13.0V ceiling). Both directions retain positive, real margin even
  under this doubly-adverse assumption.
- **Hysteresis (falling thresholds)**: using V(UVLOF)/V(OVPF) =
  1.09/1.122/1.15V min/typ/max, UVLO falling ≈7.57–7.99V and OVP
  falling/recovery ≈12.73–13.43V — normal, expected hysteresis behavior
  (prevents chatter at either boundary), not a flaw; both hysteresis bands
  sit clear of each other with no overlap risk within the 9–13V envelope.
- **Divider bias current**: 8.69–12.55µA across the 9–13V envelope,
  2.9×–4.2× above TI's own explicit design floor — "the resistor string
  current, I(R123) must be chosen to be 20x greater than the leakage
  current of UVLO and OVP pins" (SLVSE94G §9.2.2.2, **DS-PROT-026**), using
  TI's own guaranteed ±150nA I(UVLO)/I(OVP) leakage spec (20×150nA = 3µA
  floor).

**R(ILIM) — new R15 = 3.57 kΩ (E96, 1%).** TI's own Equation 8, R(ILIM) =
18/I(OL) kΩ (**DS-PROT-027**), against this design's own protection
hierarchy needs — U5's OCP already trips at 3–4A (DS-MTR-058) and F1's
PTC trips at 10A (DS-PROT-006/033); R15 = 3.57kΩ (the nearest E96 value
below TI's own tested 4.02kΩ table row, chosen to bias toward a higher,
not lower, overload trip current so U6 never nuisance-trips ahead of U5's
own OCP) gives **I(OL) ≈ 4.69/5.04/5.40A (min/typ/max)** — 17.2% above
U5's 4A OCP max at U6's own worst-case-low trip, and comfortably below
F1's 10A PTC — a clean three-tier hierarchy: **U5 OCP (3–4A) → U6 overload
(4.69–5.40A) → F1 PTC (10A)**, each backstopping the one before it rather
than racing it.

**dVdT capacitor — new C17 = 22 nF, dVdT pin (10) to GND.** TI's own
Equations 1–2 (**DS-PROT-028**): I(INRUSH) = C(OUT)·V(IN)/t(dVdT),
t(dVdT) = 20.8×10³·V(IN)·C(dVdT) → combined, **I(INRUSH) =
C(OUT)/(20.8×10³·C(dVdT))**, independent of V(IN). **Sized against this
design's own real downstream capacitance — C(OUT) = the existing C10 =
10µF, reused, not a new part** — deliberately *not* copied from TI's own
worked-example scenario, which targets C(OUT) = 1mF (1000µF, TI's own
Figure 8-3 caption and §9.2.2.3 worked example, **DS-PROT-028**) for a
15W-DC-DC-converter buffer-capacitor use case ≈100× larger than this
design's own C10 — flagged explicitly to prevent a copy-the-datasheet-
example error (an earlier draft of this section briefly conflated the
two before this was caught and corrected). With C(OUT)=10µF, C17=22nF:
**I(INRUSH) ≈ 21.9mA** (negligible against any protection threshold in
this design), transient inrush dissipation (TI's Equation 3,
P(D,INRUSH)=0.5·V(IN)·I(INRUSH)) ≈99–142mW across the 9–13V envelope for
only the ≈5ms ramp duration (thermally negligible — see thermal
paragraph below), sitting 2.2× above the C(dVdT)≥10nF ROC floor.

**PGTH tied to GND (pin 16) — deliberate, forces every turn-on through
the slow/controlled ramp.** TI's own Timing Requirements table
(**DS-PROT-028**): with V(PGTH) < V(PGTHF) (guaranteed true whenever PGTH
is grounded, since V(PGTHF)=1.09–1.15V min–max), turn-on always takes the
slower, C(dVdT)-scaled path — UVLO_ton(dly) = 742+49.5×C(dVdT)[nF] µs,
OVP_ton(dly) = 150+49.5×C(dVdT)[nF] µs — rather than the fast,
C(dVdT)-independent bypass path available when V(PGTH) > V(PGTHF)
(70–251µs / 58–225µs). With C17=22nF this adds a fixed ≈1.83ms delay on
every turn-on (cold power-up **and** OVP-recovery) — negligible, and a
deliberate trade-off (safety/inrush-control over speed) called out
explicitly since PGTH's nominal purpose (a PGOOD-threshold comparator
input) is not otherwise used here (PGOOD itself is left floating, below)
— PGTH is repurposed purely as a "always take the controlled-ramp path"
configuration bit. Flagged for Hardware Reviewer awareness — see §16.

**New input bypass capacitor C16 = 1 µF, IN/IN_SYS to GND.** Satisfies
three separate, consistent TI recommendations simultaneously
(**DS-PROT-029**): (a) "TI recommends a minimum of 1 µF for C(IN) ... to
limit the slew rates during surge testing" (§9.2.2.5.1, the most
stringent applicable figure — this is the one C16 is sized against); (b)
"Connect a minimum of a 0.1-µF capacitor across IN_SYS and GND" (§8.3.11);
(c) a general "input ceramic bypass capacitor higher than 0.1µF" if the
supply is more than a few inches away (§9.5). A new component this
revision — not foreseen when §7.5.10 was first flagged in Rev 4.

**MODE (pin 12) left open — latch-off overload response, not
auto-retry.** TI's own Table 8-1 (device-specific row for TPS26631,
**DS-PROT-030**): with MODE = Open, on an overload the device applies
active current limiting (2× for tCB(dly), then 1× for up to
tCL_PLIM(dly)) then **latches OFF**; "Latch reset by toggling SHDN low to
high or UVLO low to high or power cycling IN_SYS." (The alternative,
MODE shorted to GND, auto-retries after t(TSD_retry) instead — not chosen
here.) This is a deliberate design choice, not a default: it means U6
itself will not silently auto-retry through a persistent overload the way
U5's own OCP does (§7.5.6) — and it creates a useful synergy with the
already-committed PA9/SHDN signal: the **same pin** that firmware drives
to enable/disable U6 (ISS-015) and that firmware would drive low to
enforce an eventual latched-fault policy (ISS-021, §7.5.12) can **also**
reset a MODE-Open-induced overload latch, by toggling SHDN low-to-high
(TI Table 5-1's own SHDN pin description independently confirms this:
"Cycling SHDN pin voltage resets the device that has latched off due to a
fault condition," **DS-PROT-024**) — one physical control point serving
all three functions, not three separate signals. Flagged for Hardware
Reviewer/Firmware Lead awareness: this interacts with ISS-021's *still
entirely undecided* firmware latch policy (§7.5.12, unchanged this
revision) and should be revisited once that policy is actually designed
— see §16.

**PGOOD/FLT/IMON left floating (unused this revision).** All three are
explicitly supported floating configurations per TI's own guidance
(**DS-PROT-030**): "If PGOOD is unused then connect to GND or leave it
floating"; "FLT can be left open or connected to GND when not used";
IMON is left open in TI's own standard characterization condition
(R(ILIM)=30kΩ, IMON=PGOOD=FLT=OPEN, throughout the Electrical
Characteristics tables). Not wired to firmware this revision — a
possible future opportunity (e.g. FLT as a fast fault-status read
distinct from the FG-based motor-status path, §7.5.4) is noted but not
required by any currently-open issue; IMON in particular must never gain
a bypass capacitor if used later (TI: "must not have a bypass capacitor
to avoid delay in the current monitoring information").

**Decoupling, thermal, and quiescent current.** No new IN/OUT capacitors
beyond C16 (new, IN/IN_SYS) and the reused C10 (OUT, unchanged) — see
above. Thermal: RθJA = 32.2°C/W (PWP/HTSSOP-20 package, **DS-PROT-031**);
R(ON) = 26/30.44/34.5mΩ (min/typ/max, TJ=25°C) rising to 33–45mΩ
(min–max, TJ=85°C) — steady-state conduction dissipation at this design's
own ≤3A worst-case operating current is **0.234–0.310W** (25°C-row) to
**0.297–0.405W** (85°C-row, the more conservative corner), giving
ΔTJ≈7.5–13.0°C via RθJA — using the conservative 85°C-row/45mΩ corner:
TJ≈53°C at REQ-201's 40°C ambient design target, **72°C margin below the
125°C ROC ceiling, 97°C below the 150°C AMR ceiling, and 112°C below
T(TSD)=165°C's auto-recovering thermal-shutdown backstop**
(**DS-PROT-031**). IQ(ON)=1.38/1.7mA, IQ(OFF)=21/60µA (typ/max,
**DS-PROT-031**) — both negligible against VM_MOTOR's own scale; full
figures and rail-margin impact in `hardware/power-budget.md` (§17).

**MCU enable pin — PA9 committed (final, not tentative).** Re-confirmed
still free this revision (§11) before commit — the same pin Rev 4's
§7.5.10 had only tentatively earmarked. Direct connection to SHDN (pin
13), no series resistor — R11 alone sets the pull-down; PA9 driving high
sources the enable current directly. Free-GPIO count drops from 16 to 15
(§11).

**Residual items for Hardware Reviewer** (not blocking, all newly
recorded in §16): the SHDN pull-up discrepancy (above); the OVP
worst-case-corner trip point sitting only 3.4% clear of a 4S pack in the
full-stack-worst-case corner; PGTH/MODE's interaction with ISS-021's
still-undecided firmware latch policy; the dVdT/C(OUT) sizing basis
(this design's own 10µF, not TI's 1mF example).

### 7.5.11 Flagged: maximum commanded speed / overspeed envelope (new, ISS-020 — firmware requirement, no schematic-level fix)

**No circuit-level fix exists for this finding, and none is invented
here.** REQ-007's "≥3000 RPM" (`bom/component-selection.md`) has only
ever been stated as a functional floor — a minimum the design must be
capable of reaching — not a ceiling on *commanded* speed. M1's own
no-load speed is approximately 20,000 RPM (M1's own 10V-test-condition
reference point) up to a corrected, path-drop-accounted credible
worst-case of ≈25,180 RPM at this design's own qualified 13.0V envelope
ceiling (**DS-MTR-018 corrected/DS-MTR-080, §7.5.13** — supersedes the
previously-cited, mislabeled "22,200 RPM at full-charge 3S (11.1V)"
figure) — **6.7–8.4×** REQ-007's floor — and because stored rotational
kinetic energy scales with the square of angular velocity, M1 stores
roughly **44–70×** the rotational energy at no-load that it would at
the 3000 RPM floor. Nothing in this design's own schematic scope (U5,
M1, J4, D2, D3, F1, R10, the flagged §7.5.10 controller) can bound a
*commanded* maximum speed — that requires a firmware policy comparing a
live tachometer reading against a chosen ceiling and taking action,
which is compute/logic, not a passive or even active analog protection
circuit.

**What already exists to support this**: the FG (tachometer/speed
feedback) signal is already wired (§7.5.4, R6 pull-up, MCU
PA6/TIM3_CH1) — the sensing prerequisite for any firmware-side overspeed
policy already exists in hardware; only the *policy* (a chosen ceiling,
a response) is missing, and that is explicitly a firmware concern.

**Explicitly not the REQ-009-prohibited closed-loop control**: a bounded
safety cutoff that stops the motor once a measured speed exceeds a fixed
ceiling is categorically different from closed-loop attitude/rate
control (REQ-009's own fence) — the same way this design's own existing
overcurrent-shutdown behavior (§7.5.6) is not itself "control" in the
prohibited sense. This distinction is asserted here for Hardware Lead/
human-reviewer confirmation, not unilaterally decided as settled.

**Flagged for Hardware Lead mediation, ties to REQ-403**: this document
proposes **~6000 RPM (2× REQ-007's own floor) only as a numeric anchor
for discussion**, not a decision — per `validation/open-issues.md`'s own
ISS-020 Recommended Fix framing, the actual maximum commanded speed,
maximum commanded acceleration/ramp rate, and the overspeed-response
behavior (e.g. force SPEED to a safe/stopped state, using the same FG
feedback path) are Firmware Lead's and the human safety reviewer's call,
not this agent's. Whatever ceiling is ultimately chosen must also feed
Mechanical Lead's own flywheel/containment design as a real input
(`docs/architecture.md` §12's mechanical/thermal co-design mandate, §9
below) — a lower firmware-enforced ceiling directly reduces the
containment energy Mechanical Lead must design against.

### 7.5.12 Flagged: latched-fault shutdown policy for REQ-404 (new, ISS-021 — firmware requirement, hardware enabler cross-referenced)

**No circuit-level fix exists for this finding either — U5's own three
protection mechanisms are all auto-recovering by design, which is not
itself a defect, but is a real gap against REQ-404's own intent.** §7.5.6
already confirms OCP (DS-MTR-058), Lock Detection (DS-MTR-059), and
Thermal Shutdown (DS-MTR-060) as U5's three relevant protection
mechanisms — Cycle 3 review correctly observes that **none of the three
latch**: OCP auto-clears once the overcurrent condition is no longer
present, Lock Detection auto-retries after tLOCK_OFF=5s, and Thermal
Shutdown auto-recovers on cooling. REQ-404's own "shutdown behavior to
prevent sustained overheating" is not actually satisfied by relying on
these alone: a persistent mechanical jam (e.g. a fouled bearing, a
mechanical interference with M1's rotor) would not be resolved by any of
the three — it would instead produce **repeated fault-current pulses and
repeated auto-restarts indefinitely**, each dissipating real heat, with
no design-level mechanism that ever actually stops trying. D2 alone
dissipates approximately 1.86W at a 3A/0.62V-max worst-case fault
current (DS-PROT-005) — a real, non-trivial, repeating thermal event
under this failure mode, not a hypothetical one.

**Fix requires firmware, not a passive circuit change**: a **latched-
fault policy** — count consecutive Lock Detection events (Status
register bit4, `MtrLck`) within a rolling time window over the
already-wired I2C1 bus (§7.5.4); once a threshold count is reached
within the window, force SPEED to a safe/stopped state and **require a
deliberate re-arm** (e.g. an explicit firmware command or a power-cycle)
before resuming — rather than allowing U5's own indefinite auto-retry
behavior to continue unsupervised. This is flagged as a new, explicit
firmware requirement, not implemented here (REQ-009's own fence: this is
a schematic-level document, and the actual retry-counting/state-machine
logic is firmware, not a circuit).

**Hardware note, not a fix**: §7.5.10's **U6 (TPS26631PWPR, implemented
this revision, Rev 5)** — the same supervisory controller wired for
ISS-015/ISS-019 — now gives firmware the **physical enforcement point**
this policy will eventually need: firmware can drive PA9/SHDN low to
physically remove U5's VCC once it declares a latched-fault condition.
**This is not a resolution of ISS-021 itself** — the retry-counting,
rolling-window, and re-arm *policy* above remains entirely undecided and
is not implemented, invented, or defaulted by this hardware revision;
U6 only ensures the mechanism to act on that policy, once designed,
already exists in silicon rather than needing a future hardware
revision. One part serving three purposes (ISS-015/019/021's enforcement
point), not three separate/redundant parts across three separate
findings.

**REQ-404 is a "Should," not a "Must"** (confirmed against `requirements/
requirements.md`'s own exact wording) — noted for completeness, not used
to reduce the obligation to address this HIGH finding explicitly,
consistent with this agent's own instructions to address every HIGH
finding regardless of the underlying requirement's own priority tier.

### 7.5.13 M1 true credible-worst-case no-load speed — DS-MTR-018 voltage-label correction and a required new input for Mechanical Lead (new, Circuit Engineer independent cross-check of the Firmware Reviewer's REQ-405 verification)

**Trigger, and this agent's own discipline applied, not a borrowed
conclusion.** While independently verifying the Firmware Engineer's REQ-405
command-side duty-cycle-ceiling derivation (§12 addendum,
`firmware/bench-imu-01/bench-imu-01-firmware-design.md` — correctly cites
"this design's own 13.0V worst-case `VM_MOTOR` envelope," §7.5.9 above), the
Firmware Reviewer flagged that **DS-MTR-018** (`datasheets/evidence-log.md`,
Component Selection era) may mislabel its own voltage basis. Per this
agent's own "Process" step 1 (confirm parts/datasheet facts independently,
never proceed on an unconfirmed claim) and this task's own explicit
instruction not to just accept another role's analysis, every figure below
was independently re-derived from primary sources this session — the
Firmware Reviewer's report was a trigger to look, not a substitute for
looking.

**Finding, independently confirmed:** DS-MTR-018 labels its own ~22,200 RPM
figure "at full-charge 3S (11.1V)". That label is wrong — **11.1V is 3S's
nominal voltage** (3.7V/cell × 3 cells), **not** its full-charge voltage.
Full-charge 3S is **12.6V** (4.2V/cell × 3 cells). This is independently
confirmed three ways this session (not merely taken on the Reviewer's own
report): (1) this evidence log's own very next row, **DS-MTR-017**, already
states the correct range ("7.4-11.1V nominal, 8.4-12.6V full-charge") — the
error was never cross-checked against the entry immediately above it; (2)
the T-Motor metadata record's own "Known gaps" section independently states
"3S full charge (~12.6V)"; (3) a fresh web search this session, plus a
second independent retailer re-fetch (**DS-MTR-079**), both confirm the
standard 3.7V-nominal/4.2V-full-charge per-cell LiPo convention. The 22,200
RPM figure itself was never arithmetically wrong (it is exactly
KV×11.1V=22,200) — only its label was. **Fixed in `datasheets/evidence-log.md`
this session**: DS-MTR-018 annotated in place (original figure kept, not
deleted, per this file's own evidence-integrity convention — see
DS-MCU-062 for the established precedent this follows).

**Why this matters beyond a label fix, and why it is this role's place to
carry it further:** DS-MTR-018 predates this design's own motor
power-input circuit (F1/D2/D3/U6, all added later, §7.5.2/§7.5.9/§7.5.10) —
it is a simple `KV × V` estimate with no circuit-path accounting at all,
because at the time it was written there was no circuit path yet to
account for. Today there is one, and it is this role's own place (not
Component Engineer's, not Mechanical Lead's) to re-derive what voltage
actually reaches M1's terminals through it. §7.5.11 above already flags
that Mechanical Lead's flywheel/containment design needs a real no-load-
speed input — a corrected, but still label-only, 12.6V figure would give
KV×12.6V=25,200 RPM, but that still is not this design's own real answer:
it ignores both (a) the 13.0V envelope this design actually qualifies
inputs against (12.6V **plus** ~3% bench-supply headroom, §7.5.9 — a wider,
binding ceiling, not merely 12.6V), and (b) the real series voltage drops
between J4 and U5's actual VCC pin that only exist because F1/D2/U6 do.
Both are corrected together below.

**Direction of conservatism — the opposite bound from §7.5.2/§7.5.10's own
existing drop analyses, stated explicitly so this is not misread as
duplicating or contradicting them.** §7.5.2's UVLO-margin analysis and
§7.5.10's thermal analysis both deliberately use *maximum* VF/resistance at
this design's *worst-case operating current* (≤3A) — because those
analyses ask "could voltage dip too low / could heat rise too high."
This question is the mirror image: "what is the *most* voltage that could
credibly reach M1, for a worst-case stored-energy/containment estimate" —
which requires *minimum* resistance, the *lowest* credible VF, and the
motor's actual (much lower) no-load current, not the ≤3A figure used
elsewhere. Reusing the 0.53–0.62V/"0.02Ω assumed" figures from §7.5.2 here
would *understate* true worst-case RPM, the wrong direction of error for
this specific question — so they are deliberately not reused as-is.

**Path and inputs, each confidence-marked (`CONFIRMED` / `ASSUMPTION` /
`ESTIMATE` / `UNKNOWN`, this project's convention):**

| Step | Value used | Confidence | Basis |
|---|---|---|---|
| J4 input ceiling | 13.0V | `CONFIRMED` | This design's own established, binding `VM_MOTOR`/J4 envelope ceiling (§7.5.9) |
| F1 (Littelfuse 30R500UF) resistance | Rmin = 0.010Ω | `CONFIRMED` | DS-PROT-006/033 — minimum (not R1max/"0.02Ω assumed"), since this question wants the least drop, opposite of §7.5.2's own use of this same part |
| D2 (STPS3L60) forward drop | VF ≈ 0.35–0.45V | `ESTIMATE` | DS-PROT-005 (curve exists, 3A-only tabulated) + DS-PROT-034 (Figure 13 low-level curve confirmed to exist this session, but its exact values could not be extracted from the vector graphic) — reasoned low-current estimate, not a pixel-read value; see below |
| D3 (SMBJ16A) | 0V series drop | `CONFIRMED` | Shunt TVS topology, not series — confirmed directly from the schematic net list (§7.5.2/§2.1) |
| U6 (TPS26631) on-resistance | R(ON)min = 0.026Ω | `CONFIRMED` | DS-PROT-031, TJ=25°C row minimum (not the 85°C/45mΩ conservative-thermal corner used at §7.5.10) |
| M1 true no-load current | ≈0.3A (sensitivity-checked to 0.6A) | `CONFIRMED` (0.3A figure) / `ASSUMPTION` (that true operating-voltage no-load current does not exceed ~2× that) | T-Motor's own stated Io=0.3A at its 10V test condition (DS-MTR-018, independently re-confirmed via a second retailer, DS-MTR-079); no manufacturer Io-vs-voltage curve exists for this SKU, so a 2× sensitivity bound is used rather than assuming the 10V-test-point figure holds unchanged at ~12.6V |
| M1 KV | 2000 RPM/V | `CONFIRMED` | DS-MTR-017, independently re-confirmed via DS-MTR-079 |
| VCC→output-voltage relationship | Linear, no further correction needed at 100% duty (the no-load-speed convention) | `CONFIRMED` | TI's own DRV10983 equation, "peak output amplitude = VCC × (PWM_DCO/100)" (DS-MTR-078, already established by Firmware's own REQ-405 work) |

**Resulting computation:** total series drop (F1 + D2 + U6, D3 contributing
0V) ≈ 0.36–0.46V across the D2-VF `ESTIMATE` range, essentially unaffected
by the current sensitivity check (F1+U6 together contribute only 11–22mV
even at the 0.6A upper bound — the answer is dominated by the D2-VF
uncertainty, not the current assumption). This gives:

- **V_VCC(U5) ≈ 12.54–12.64V, point estimate ≈12.59V** (13.0V minus the
  ≈0.36–0.46V total drop).
- **RPM = KV × V_VCC ≈ 25,060–25,280, point estimate ≈25,180 RPM.**

**Cross-check (reassuring, not the primary derivation):** a naive
label-fix-only recompute — KV × 12.6V (full-charge voltage, no envelope
headroom, no path drops at all) — gives 25,200 RPM, landing within ~20 RPM
of this section's own detailed point estimate. This is a coincidence (the
~3% envelope headroom §7.5.9 deliberately adds happens to be of similar
magnitude to the real path drop this section subtracts), not a
substitute for the detailed derivation above, which remains the
authoritative figure because it is the only one that actually accounts for
both real effects rather than cancelling them out by omitting both.

**Comparison to the existing (corrected-label) DS-MTR-018 figure:** the
point estimate (≈25,180 RPM) is **≈13.4% higher** than 22,200 RPM (range
≈12.9–13.9% across the confidence bounds above). Because stored rotational
kinetic energy scales with ω² (already the convention §7.5.11/ISS-020 and
Mechanical Lead's own §8 use), this is **≈29% more stored kinetic energy**
at the credible worst case (range ≈27–30%), not merely a proportional
13–14% increase. Illustratively, against Mechanical Lead's own already-
published §8 figures at 22,200 RPM (I=4.5×10⁻⁵kg·m², rim speed 69.74m/s,
121.60J) — offered here only as a courtesy cross-reference, **not as a
substitute for Mechanical Lead's own recomputation**, since the rotor
inertia and rim radius are that role's own data, not this role's to
assert: the corrected point estimate scales to ≈156J stored energy
(range ≈155–158J) and ≈79.1m/s rim speed (range ≈78.7–79.4m/s, ≈283–286
km/h) at the same rotor geometry.

**Relationship to Firmware's own REQ-405 work — complementary, not
contradictory, and not this role's to touch.** DS-MTR-078 (Firmware's own
evidence) uses the 13.0V J4-envelope figure directly as "VCC" in its own
command-ceiling derivation, without subtracting the F1/D2/U6 path drops
derived here. That is not an error in Firmware's own, separately-scoped
work — REQ-405's command-side ceiling is a firmware policy constant with
its own conservatism margin (`motor.h`/§4.3), and treating the
higher-than-actual J4 figure as VCC there is itself conservative in
*that* context (it only makes Firmware's own commanded-ceiling more, not
less, conservative). This section's more precise, path-drop-corrected VCC
figure is a *distinct* number for a *distinct* question (the physical,
uncommanded no-load speed the motor can reach on its own, for a
containment/energy estimate) — not a claim that Firmware's file needs a
fix, and `firmware/bench-imu-01/` is not touched by this section or this
session.

**Handoff to Mechanical Lead — required new input, not applied by this
role.** Mechanical Lead's flywheel physics table
(`hardware/mechanical/bench-imu-01-dimensional-spec.md` §8) currently uses
the pre-correction 20,000/22,200 RPM figures from DS-MTR-018 for its own
"no-load-low"/"no-load-high" columns, feeding stored energy, rim speed,
and peak centrifugal stress — which in turn is the physics basis for the
open REQ-403 containment-wall disposition and the open MISS-016 HIGH
finding on containment-wall margin. **This section's corrected
credible-worst-case figure (V_VCC(U5)≈12.54–12.64V, point ≈12.59V;
RPM≈25,060–25,280, point ≈25,180 — DS-MTR-080) is a required new input for
that table.** Consistent with this agent's own "Out of scope" boundary
(mechanical/enclosure files are Mechanical Lead's domain, not edited here),
`hardware/mechanical/bench-imu-01-dimensional-spec.md`,
`bench-imu-01-manufacturing-spec.md`, and every `.scad` file are left
untouched by this section — Mechanical Lead (or Hardware Lead, dispatching
Mechanical Lead) is expected to consume the figures above, recompute §8's
table and any downstream REQ-403/MISS-016 disposition text against them,
and independently verify the rotor-inertia/rim-radius scaling shown
illustratively above rather than trusting it uncross-checked, mirroring
this section's own "don't just trust a report" discipline.

**Evidence IDs newly recorded or relied on this section**: DS-MTR-017
(KV, `CONFIRMED`), DS-MTR-018 (annotated/corrected this session), DS-MTR-079
(new — independent T-Motor re-confirmation), DS-PROT-005/034 (D2 VF,
`ESTIMATE` at low current), DS-PROT-006/033 (F1 Rmin, `CONFIRMED`),
DS-PROT-031 (U6 R(ON)min, `CONFIRMED`), DS-MTR-078 (VCC×duty relationship,
`CONFIRMED`), DS-MTR-080 (new — this section's own aggregated derivation,
the single citation Mechanical Lead's handoff should trace back to).

## 8. Block 6 — Grounding

**Single ground plane/net for this entire design, now explicitly spanning
two independent power domains** — updated this revision (Rev 2's
single-domain framing is superseded by this section; see §2.2 for the
short pointer added there). Stated here explicitly per the design task's
own instruction not to leave this implicit.

**What stays true from Rev 2**: REQ-301 fixes a single 2-layer PCB; a
single continuous ground pour on one copper layer is still the simplest
and electrically correct choice for a board at this complexity level (5
active ICs total after Rev 3: MCU, IMU, LDO, ESD-protection IC, motor
driver) — there is still no analog-precision or RF section that would
independently justify a split-plane/multi-point-star topology on
grounding grounds alone. Every GND-role pin across every block (§§3–7.5)
returns to this **one** net; restated in the full net list, §12.

**What is new and must be stated as its own decision (per the design
task's point 3)**: the two power **rails** are deliberately independent
sources (5V/3V3 logic via U3, VM_MOTOR via J4→D2→D3→U5 — Option A's
fault-isolation intent, `hardware/power-architecture.md`), but they are
**not** independent at the **ground** reference — both domains' GND pins
tie to the same single ground net/plane described above. This is a
deliberate, necessary choice, not a contradiction of Option A's
fault-isolation intent:

- **Why common ground is required, not optional**: the PWM (SPEED),
  tach (FG), and I2C1 (SCL/SDA) signals crossing between U1 (MCU) and U5
  (driver) are single-ended digital signals — their voltage levels are
  only meaningful relative to a shared 0V reference. Without a common
  ground, "logic high" on U5's FG output would be undefined relative to
  U1's own GND, and none of REQ-007/008/110/112's interface wiring would
  actually function. Option A's fault-isolation intent is about the
  **power** rails (a fault on the motor rail should not directly damage
  or brown out the logic rail's regulator, and vice versa) — it was never
  a requirement for galvanic isolation of the *signal* reference, which
  would need opto-isolators or digital isolators neither REQ-108 nor
  `hardware/power-architecture.md` calls for.
- **Return-current consideration (REQ-010, REQ-204)**: the motor domain's
  return current (up to ≈3A transient during start-up/lock, DS-MTR-056/
  058; ≈1.05A nominal) shares the same physical ground pour as the IMU's
  own low-level analog/digital return currents. This is a real potential
  noise-coupling path (ground-bounce / IR-drop across the shared copper)
  distinct from the supply-noise-coupling path already ruled out in §5.5
  (since the rails themselves don't share a regulator). **Layout-level
  mitigation recommended for the Mechanical/PCB layout stage** (this
  document is schematic-equivalent, not a layout, per §0): route the
  motor input (J4), its protection stage (D2/D3), and U5's high-current
  VCC/PGND/phase-output area as a single, compact group with a short,
  direct return path back to the star point, physically separated from
  the IMU (U2) and its decoupling caps, rather than letting the motor
  domain's return current path run underneath or adjacent to the IMU's
  footprint. A single star-ground tie-in point (where the logic domain's
  main return and the motor domain's main return both meet the shared
  pour) is recommended over letting the two domains' return currents mix
  at multiple, arbitrary points across the plane.
- **REQ-204/EMI**: the same physical separation recommendation reduces
  both conducted return-current coupling and radiated near-field coupling
  from U5's switching phase outputs (U/V/W, commutated at the PWM/
  commutation frequency) reaching the IMU's sensitive analog front-end —
  addressed here as a grounding/layout consideration; the vibration
  (mechanical) side of REQ-204 is addressed separately in §9, not
  conflated with this electrical-noise consideration.

**Net result**: one ground net/plane, as in Rev 2, but now carrying an
explicit rationale for *why* that remains correct even though a second,
independently-sourced power rail has been added — not an unexamined
carry-forward of the Rev 2 statement.

## 9. Block 7 — Mechanical/Thermal co-design (checklist item 18)

**No longer Not Applicable — flipped to real content this revision**
(REQ-204/307 supersede REQ-202's Rev 2 disposition for this revision
specifically; REQ-202 itself is retained verbatim elsewhere as Rev 2's
historical record, not deleted or edited). Rev 2 correctly determined
this item was N/A because no rotating body existed; that reasoning no
longer applies now that a reaction-wheel motor (M1) is part of this
design. Per this agent's own instructions and the design task, this
section **records electrical-side facts relevant to the Mechanical
Lead's later attention — it does not perform the mechanical mitigation
design itself** (that is explicitly the Mechanical Lead's role, not
this agent's).

- **The motor is a genuine rotating body (REQ-204)**: M1 (T-Motor
  MN2206-13 KV2000) drives a reaction-wheel flywheel at speed, which is a
  sustained vibration source for as long as the wheel spins — qualitatively
  different from any Rev 2 component (none of which move). REQ-307 asks
  that the motor+flywheel mount be evaluated for vibration isolation from
  the IMU's PCB area "where feasible" — a mechanical/mounting decision,
  not a circuit one, but flagged here as a live, real consideration
  (not skipped as N/A the way Rev 2 correctly could).
- **Vibration-induced solder-joint/connector stress (checklist item 18)**:
  sustained vibration is a known long-term fatigue mechanism for
  solder joints (particularly larger/heavier through-hole parts and any
  connector under mechanical load) and for connector retention (J4, the
  new barrel jack, is a through-hole part that will see repeated
  plug/unplug mechanical stress **in addition to** any board-borne
  vibration from M1). This design does not add mechanical reinforcement
  itself (e.g. adhesive/strain-relief) — flagged as a Mechanical Lead
  consideration, since the actual mounting/isolation solution is
  mechanical-domain, not a schematic-level fix.
- **Thermal/vibration relevance to the IMU (REQ-204, REQ-010 overlap)**:
  the BMI270's accelerometer/gyroscope bias is a well-known
  temperature-sensitive parameter for MEMS IMUs generally (bias drift
  with die temperature is a standard MEMS IMU characteristic; the
  BMI270's own specific bias-vs-temperature coefficient was not
  independently re-extracted from its datasheet this revision — flagged
  as a residual research gap in §16, not fabricated). U5 (the motor
  driver) and M1 (the motor) are both real, non-trivial heat sources
  during sustained operation (U5 dissipates from I²R and switching
  losses at up to ~1–3A; M1 dissipates from winding resistance at the
  same current) — **physical placement/thermal separation between the
  motor+driver group and the IMU is a real, non-cosmetic consideration**
  for bias stability, in addition to the vibration-isolation point above.
  This is exactly the `docs/architecture.md` §12 mechanical/thermal
  co-design trigger REQ-202 correctly found inapplicable in Rev 2 and
  which now genuinely applies.
- **U6 (Rev 5) is a minor, not a materially new, addition to this heat
  group**: §7.5.10 confirms U6's own steady-state conduction dissipation
  (0.234–0.405W depending on R(ON) test corner) is an order of magnitude
  below U5's own (which dominates the motor-domain heat budget) — U6 sits
  physically adjacent to U5/M1 in the same motor-domain group (§12's net
  list places it electrically between D3 and U5), so it does not
  introduce a new, separate thermal zone requiring its own IMU-separation
  analysis; the existing U5/M1-vs-IMU separation consideration above
  already covers it.
- **Facts recorded for the Mechanical Lead handoff** (§10 continues this
  with physical placement/geometry specifics): M1's mass/mounting
  interface, U5's package/thermal characteristics, and J4's mounting
  style are the concrete electrical-side inputs the Mechanical Lead needs
  to design the actual isolation/mounting solution — this design does not
  presume or design that solution.

## 10. Block 8 — Board geometry facts for the (later, separate) Mechanical Lead handoff

**I am not editing `hardware/mechanical-interface.md` — that is the
Mechanical Lead's file, in a later phase.** The following are my own
best real-engineering estimates, recorded here so the Mechanical Lead can
extract them when that phase begins, with CONFIRMED / ESTIMATE /
ASSUMPTION labels applied honestly per item.

| Fact | Value | Confidence | Basis |
|---|---|---|---|
| PCB outline/size | ~55×35mm up to the full 60×40mm REQ-302 target; **recommend designing to the full allowed envelope** for routing/assembly margin given the connector + header count | ESTIMATE | Reasoned from component count (3 ICs + 3 connectors/headers + passives) against REQ-302's stated ≤60×40mm target |
| Connector/header edges | USB-C (J1) on one short edge; UART header (J2) + SWD header (J3) both along one long edge | ESTIMATE | Satisfies REQ-303 (≤2 edges) by construction — 2 edges used total |
| Mounting holes | 4×, near each corner, inset ~3–4mm from board edges, sized for **M2.5** (hole ⌀≈2.7–2.8mm) | ESTIMATE | Satisfies REQ-304 (≥4, M2/M2.5) |
| LQFP-32 (U1) package height | ≈1.4mm nominal | **CONFIRMED** (via JEDEC MS-026 package-family standard, DS-MCU-048 — see caveat below) | JEDEC MS-026 LQFP outline family; corroborated by NXP/JCET package-family references |
| SOT-23-5 (U3) package height | ≈1.1–1.25mm typ/max | **CONFIRMED** (via JEDEC MO-178 package-family standard, DS-PWR-046 — see caveat below) | JEDEC MO-178 SOT-23 outline family; corroborated by a real Nexperia SOT-23-5 outline drawing (SOT8104-1.pdf) |
| USB-C receptacle (J1) height | ≈2.6–3.2mm (representative real part: GCT USB4125, horizontal/top-mount, = 3.16mm) | ESTIMATE (representative-part CONFIRMED, but J1's actual MPN not yet locked) | DS-CONN-003 |
| Micro-USB-B receptacle height (comparison only — not used) | ≈6.5–6.9mm (GCT USB3140=6.5mm; Würth 614105150721=6.9mm) | ESTIMATE (representative-part CONFIRMED) — **comparison-only**, this design chose USB-C | DS-CONN-004 |
| **Tallest component on the board** | **The USB-C receptacle (J1), ≈3.2mm** — clearly taller than the LQFP-32 (≈1.4mm) or the SOT-23-5 (≈1.1–1.25mm) | ESTIMATE (built from a CONFIRMED-by-representative-part height) | Confirms the design task's own hint |
| **Barrel jack (J4) — new Rev 3** | Right-angle THT, mating-plug insertion depth 9.5mm (DS-CONN-005); overall body height above the PCB **not independently extracted this session** — right-angle THT barrel jacks of this class are typically taller than J1's SMD/top-mount USB-C receptacle | **ASSUMPTION/UNKNOWN** (insertion depth is CONFIRMED per DS-CONN-005; body height is not) | Flagged for Mechanical Lead to pull directly from PJ-102AH's own mechanical drawing before finalizing enclosure Z-height (§10 flag below) — **J4 may in fact be the new tallest component on the board, superseding J1**, pending that confirmation |
| **HTSSOP-24 (U5, DRV10983) package height — new Rev 3** | ≈1.1–1.2mm typ (JEDEC MO-153 HTSSOP family envelope) | **CONFIRMED-via-standard** (same caveat as the LQFP-32/SOT-23-5 rows above: family-standard, not U5's own part-specific drawing, not independently re-pulled this session) | JEDEC MO-153 HTSSOP outline family |
| **Motor (M1, T-Motor MN2206-13 KV2000) size/mass/mounting — new Rev 3** | Stator nominally ⌀22mm×6mm (standard BLDC "XXYY" size-code convention: 22=stator diameter mm, 06=stator height mm) — mass, full outline, shaft diameter, and mounting-hole pattern **not independently pulled from T-Motor's own mechanical drawing this session** | **ASSUMPTION** (size-code convention) / **UNKNOWN** (mass, mounting pattern) | Flagged for Mechanical Lead to obtain directly from T-Motor's own mechanical drawing/CAD file — needed before REQ-307's vibration-isolation mount can be designed; this design's own electrical-side scope stops at flagging the need (§9) |

**Caveat on the two "CONFIRMED" package-height rows**: these are
confirmed against the **JEDEC package-family outline standard**
(MS-026/MO-178), not against the STM32G031K8T6's or TLV75533PDBVR's own
literal mechanical drawing page — I did not independently re-pull each
part's own datasheet mechanical drawing this session. Real parts
following these outlines are expected to match the family's standard
height envelope; flagged as CONFIRMED-via-standard rather than
CONFIRMED-via-part-specific-drawing, a distinction worth preserving for
the Mechanical Lead's own rigor. The same caveat applies to the new U5
HTSSOP-24 row above (MO-153).

**Flag to Mechanical Lead**: the connector-type choice (USB-C vs.
Micro-USB-B) materially changes the Z-height budget for any enclosure
(REQ-305) — roughly 3.2mm vs. 6.5–6.9mm for the tallest single component
on the board. This design's USB-C choice keeps the enclosure lid
clearance requirement smaller than a Micro-USB-B design would have.

**New Rev 3 flags to Mechanical Lead**:

- **J4 (barrel jack) placement**: recommend placing J4 on a board edge
  distinct from J1 (USB-C) if the enclosure design benefits from
  separating the two power-input access points; not a hard requirement
  from this design, purely a layout-convenience note. J4's exact edge/
  position is not yet fixed in this schematic-equivalent document (no
  physical layout exists yet, §0).
- **U5+M1 physical grouping vs. IMU (U2) separation**: per §9's
  mechanical/thermal co-design finding, the Mechanical Lead should plan
  for physical distance/isolation between the motor+driver group (U5,
  M1, and their high-current traces/connector J4) and the IMU (U2) —
  both for vibration-isolation (REQ-307) and for thermal separation
  (§9's bias-drift-with-temperature concern). This design does not fix
  a specific distance/placement itself (that is layout/mechanical-domain
  work), only flags the need.
- **M1 is off-board or on-board?** — **UNKNOWN, not resolved this
  session**: whether the reaction-wheel motor mounts directly to this
  PCB, to a separate mechanical structure connected only by wire, or
  some hybrid, is a Mechanical Lead decision this document does not
  presume. If wired (not board-mounted), the wire run itself is a minor
  additional consideration (length/gauge for the ≤3A worst-case current,
  and connector choice at the wire-to-board interface) not designed here
  — flagged in §16.

## 11. Full MCU pin-assignment table (STM32G031K8T6, LQFP-32)

**Corrected this revision (ISS-027)**: the table below is now sourced
directly from ST's own official machine-readable CubeMX pin database
(DS-MCU-064, HIGH confidence, primary-source-equivalent — see
`datasheets/stmicroelectronics_stm32_open_pin_data_stm32g031k4-6-8tx.md`),
superseding the original MODERATE-confidence distributor/aggregator-sourced
table (DS-MCU-046/051), which had several real errors beyond the
already-corrected PB8/PB9-existence point (ISS-006): wrong VDD/VSS/NRST pin
numbers, a nonexistent separate VDDA pin, a nonexistent VBAT pin, and —
most importantly — a nonexistent PB10/PB11 pin pair where the IMU's I2C2
bus was previously documented. GPIO alternate-function assignments per
§2.3: **I2C2 (now correctly PA11/PA12, not PB10/PB11) is HIGH confidence**
(DS-MCU-064/067); USART2 (PA2/PA3) remains MODERATE-HIGH confidence,
standard STM32 convention, not individually re-pulled from the exact AF
table this session — unchanged this revision, out of scope, see §16.
**Rev 3/Rev 5 motor-domain pins merged into this corrected table below**:
PA6, PA8, PB1, PB6, PB7 (Rev 3, §7.5.4) and PA9 (Rev 5, §7.5.10) are
consumed by the motor subsystem — pin **names**/AF numbers for all six
are HIGH confidence (DS-MCU-069/070/071, Tables 13/14, this branch's own
citations); their physical LQFP-32 **pin numbers**, previously only
MODERATE confidence/deferred to layout, are now resolved to HIGH
confidence directly from this same primary-source table (see the pin
rows below and §16 item 11).

| Pin # | Name | Function in this design | Notes |
|---|---|---|---|
| 1 | PB9 | Free (also I2C1_SDA secondary-AF option, DS-MCU-053 — unused) | |
| 2 | PC14-OSC32_IN | Free (no external 32kHz crystal populated, §6) | |
| 3 | PC15-OSC32_OUT | Free (as above) | |
| 4 | VDD/VDDA (combined) | 3V3 (via C3 + C4) | §4.1 — corrected this revision, was two separate claimed pins (17, 5) |
| 5 | VSS/VSSA (combined) | GND | §4.1 — corrected this revision, was claimed as two pins (1, 16) |
| 6 | PF2-NRST (shared pad) | NRST net (C5 + SW1) | §4.3 — corrected this revision, was claimed as pin 4 |
| 7 | PA0 | Free | |
| 8 | PA1 | Free (also I2C1_SMBA option — unused) | |
| 9 | PA2 | USART2_TX | §6 |
| 10 | PA3 | USART2_RX | §6 |
| 11 | PA4 | Free | |
| 12 | PA5 | LED drive | §7 |
| 13 | **PA6** | **FG tach input (new Rev 3)** — TIM3_CH1 input-capture, AF1, FT_ea 5V-tolerant (DS-MCU-069/071) | §7.5.4 |
| 14 | PA7 | Free | |
| 15 | PB0 | Free | |
| 16 | **PB1** | **DIR (new Rev 3)** — plain GPIO push-pull output | §7.5.4 |
| 17 | PB2 | Free | |
| 18 | **PA8** | **SPEED/PWM output (new Rev 3)** — TIM1_CH1, AF2 (DS-MCU-069) | §7.5.4 |
| 19 | **PA9** | **U6 enable (new Rev 5)** — SHDN drive, direct tie; external R11 = 10kΩ pulldown lives on the SHDN node itself, not in series with PA9 | §7.5.10 |
| 20 | PC6 | Free | |
| 21 | PA10 (default/unremapped state — this design does not engage PINREMAP) | Free (also I2C1_SDA primary-AF option, DS-MCU-053 — unused) | |
| 22 | PA11 (default/unremapped state) | **I2C2_SCL** — corrected this revision, ISS-027 (was claimed as nonexistent PB10) | §5.3 |
| 23 | PA12 (default/unremapped state) | **I2C2_SDA** — corrected this revision, ISS-027 (was claimed as nonexistent PB11) | §5.3 |
| 24 | PA13 | SWDIO | §4.4 |
| 25 | PA14-BOOT0 | SWCLK (also this sub-family's BOOT0 mux pin, ISS-006, §4.2) | §4.4 |
| 26 | PA15 | Free | |
| 27 | PB3 | Free | |
| 28 | PB4 | Free | |
| 29 | PB5 | Free (also I2C1_SMBA option — unused) | |
| 30 | **PB6** | **I2C1 SCL (new Rev 3)** — AF6 (DS-MCU-070); motor-parameter commissioning bus, consumed (was free/I2C1_SCL primary-AF option pre-Rev-3) | §7.5.4 |
| 31 | **PB7** | **I2C1 SDA (new Rev 3)** — AF6 (DS-MCU-070); same bus as PB6 above | §7.5.4 |
| 32 | PB8 | Free (also I2C1_SCL secondary-AF option, DS-MCU-053 — unused) | |

**PB8/PB9 note (superseded this revision)**: the previous revision's note
here (ISS-006) correctly established that PB8/PB9 physically exist but
could not independently resolve their *exact* pin numbers this cycle. The
new primary source (DS-MCU-064) resolves this fully and with HIGH
confidence: PB9 is physical pin 1, PB8 is physical pin 32 (both shown in
the table above) — this residual §16 item 1 gap is now closed. Both
remain free/unused in this design; PB6/PB7 (not PB8/PB9) are this
design's chosen I2C1 pin pair, consumed by the motor subsystem above.

Full free-GPIO inventory after this design's allocation (for the
Mechanical/future-firmware team's reference; every pin not itemized with a
specific function above): **PB9, PC14, PC15, PA0, PA1, PA4, PA7, PB0, PB2,
PC6, PA10, PA15, PB3, PB4, PB5, PB8 — 16 GPIO-capable pins remain
completely free**. This includes both free UART peripherals (USART1,
LPUART1), SPI1/SPI2 (unused this cycle since I2C was chosen for the IMU,
§5.1), and PB8/PB9 (I2C1's secondary AF pair, both confirmed to exist and
remain unused). I2C1's *primary* AF pair (PB6/PB7) is, by contrast,
consumed by the motor subsystem as of Rev 3 (see above) — not free.

**Rev 3 note — 5 motor-domain pins consumed against this corrected
table's own baseline**: this corrected, primary-source table's own
Rev-2-baseline free-GPIO count is **22** (the full 32-pin enumeration
above, less the power/reset/debug/UART/LED/IMU-bus pins already
committed) — a genuine, HIGH-confidence improvement over this document's
original, less-complete table (which had omitted PC6/PC14/PC15 entirely
and miscounted several power pins). Rev 3's motor subsystem consumes 5 of
those 22 (PA6, PA8, PB1, PB6, PB7), dropping the free count to **17**.

**Rev 4 note — no new MCU pin consumed by this revision's own fixes**:
R10 (§7.5.5, ISS-015) is a passive pulldown on the already-wired SPEED
net (PA8) and consumes no additional pin; F1 (§7.5.9, ISS-019) is a
passive in-line part on VM_MOTOR and has no MCU connection at all. The
free-GPIO count above (17, as it stood after Rev 3) is unchanged by
Rev 4 itself. **PA9 was tentatively noted, not committed or wired**, as
an available candidate for the then-flagged §7.5.10 supervisory switch's
enable line, pending Component Engineer/Hardware Lead adoption of that
part.

**Rev 5 note — PA9 now committed (final, not tentative)**: Component
Engineer proposed, and the human Chief Engineer approved, **U6 =
TPS26631PWPR** (`bom/component-selection.md`), so this revision
implements the §7.5.10 supervisory switch and commits its enable line.
**PA9 was re-confirmed still free** before commit (no other Rev 3/Rev 4
allocation touched it) and is now wired directly to U6's SHDN pin
(pin 13) — no series resistor; the external pull-down (R11 = 10kΩ, see
§7.5.10) lives on the SHDN node itself, not in series with PA9. The
free-GPIO count therefore drops from 17 to **16** this revision, matching
the inventory above.

**Note on PA11/PA12 and this branch's own, now-retired "Rev 6" pin
migration**: this branch had independently begun a narrower version of
this same pin-identity fix (previously tracked on this branch as "Rev
6"/ISS-026, moving only the IMU's I2C2 bus from the mistaken PB10/PB11 to
PA11/PA12) before the more complete correction adopted above (ISS-027 —
also fixing the VDD/VDDA/VBAT/VSS/NRST pin-identity errors this branch's
own Rev 6 fix never caught) superseded it; see the "Rev 2, corrected"
changelog entry. Because this corrected table places I2C2 on PA11/PA12
from its own Rev-2-baseline outset (they were never counted among the 22
free pins above to begin with — they were always the IMU's I2C2 pins,
just misidentified as the nonexistent PB10/PB11 until this correction),
no separate "PA11/PA12 committed, free count drops by 2" step is needed
in the Rev 3→5 accounting above. This corrected free-GPIO trajectory
(22 → 17 → 17 → 16) supersedes this branch's own prior, narrower
accounting (which had tracked 21 → 16 → 16 → 15 → 13, with that last,
now-retired step being the superseded Rev 6 fix itself).

## 12. Net list summary (net-by-net)

| Net | Connects |
|---|---|
| VBUS_5V | J1 (USB-C VBUS contact) → U4 pin 5 (VBUS) → C1 → U3 IN(pin2) |
| **EN_VIN** *(new this revision, ISS-001)* | **U3 EN(pin3) → U3 IN(pin2)** — firm, unconditional direct tie (always-enabled per TI's own recommended connection, §3.4); electrically the same node as VBUS_5V at U3's IN pin, broken out as its own named net for traceability since this connection was previously hedged/unconfirmed rather than firmly committed |
| CC1 | J1 CC1 contact → R1 (5.1kΩ) → GND |
| CC2 | J1 CC2 contact → R2 (5.1kΩ) → GND |
| 3V3 | U3 OUT → C2 → U1 VDD/VDDA(pin4, combined — via C3+C4)/no VBAT pin on this package (corrected this revision, ISS-027; see §4.1) → U2 VDD(pin8, via C6)/VDDIO(pin5, via C7) → R3/R4 (I2C pull-ups) → J2 pin "3V3" → J3 pin "VDD" — **corrected this revision**: previously listed "→ R5 (LED resistor)" as though R5 sat on the 3V3 net itself; R5 is a series resistor between PA5 and D1's anode (see the separate LED_CTRL/LED_A rows below) and was never actually part of this net — a documentation-only inconsistency independently caught by Hardware Reviewer Cycle 3's fidelity review, LOW severity, no electrical impact (the real KiCad project already implements the correct topology) |
| GND | U1 VSS/VSSA(pin5, single combined pin — corrected this revision, ISS-027; was claimed as pins 1,16) → U2 GND(pin7)/GNDIO(pin6) → U3 GND → U4 GND(pin2) → R1/R2 return → C1–C9 return sides → D1 cathode (via R5) → SW1 one leg → J1 shell/GND contact → J2 pin "GND" → J3 pin "GND" → **(new Rev 3, §8) J4 sleeve/GND contact → D2/D3 return sides → U5 GND(pin8)/PGND(pins15,16)/SWGND(pin5) → C10–C15 return sides** → **(new Rev 5, §7.5.10) U6 GND(pin9) *and* PowerPAD (both, per TI's own instruction — the pad is not a substitute for pin 9) → R11/R14/R15/C16/C17 return sides → U6 PGTH(pin16) tie — single common ground net spanning both power domains, §8** |
| NRST | U1 NRST(pin6, shared PF2/NRST pad — corrected this revision, ISS-027; was claimed as pin 4) → C5 → GND; also → SW1 → GND (momentary) |
| SWDIO | U1 PA13(pin24) → J3 pin "SWDIO" |
| SWCLK | U1 PA14(pin25) → J3 pin "SWCLK" (PA14 also carries this sub-family's BOOT0 mux function — corrected this revision, ISS-006, §4.2; no separate BOOT0 net exists, see §13) |
| **I2C2_SCL** *(corrected this revision, ISS-027 — was PB10, which does not exist on this package; ISS-011 had already corrected the peripheral-instance label to I2C2)* | U1 PA11(pin22) → R3 (pull-up to 3V3) → U2 SCx(pin13) |
| **I2C2_SDA** *(corrected this revision, ISS-027 — was PB11, which does not exist on this package)* | U1 PA12(pin23) → R4 (pull-up to 3V3) → U2 SDx(pin14) |
| IMU_CSB | U2 CSB(pin12) → VDDIO (tied, selects I2C mode) |
| IMU_SDO | U2 SDO(pin1) → GND (tied, selects address 0x68) |
| UART_TX | U1 PA2 (USART2_TX) → J2 pin "TX" |
| UART_RX | U1 PA3 (USART2_RX) → J2 pin "RX" |
| LED_CTRL / LED_A | U1 PA5 → R5(pin1) [net **LED_CTRL**]; R5(pin2) → D1 anode [net **LED_A**] — **corrected this revision**: R5 is a series resistor, so these are two distinct electrical nets, not one combined "U1 PA5 → R5 → D1 anode" path as previously written (a single shared net spanning both sides of R5 would incorrectly short across it); matches the real KiCad project's own net split, independently confirmed by Hardware Reviewer Cycle 3 |
| (NC) | U4 I/O1(pins1,6), I/O2(pins3,4) — unpopulated, no D+/D− on this board (REQ-105) |
| (NC) | U2 pins 2(ASDx), 3(ASCx), 4(INT1), 9(INT2), 10(OCSB), 11(OSDO) — unpopulated, aux interface + interrupts unused this cycle (§5.3) |
| (NC) | J1 D+/D− contacts — present on the physical connector for cable compatibility, not routed to any MCU/protection pin (REQ-105) |
| **VM_MOTOR** *(new Rev 3, envelope/protection extended Rev 4, U6 supervisory stage implemented Rev 5)* | J4 center-pin(+) contact → **F1 (Littelfuse 30R500UF, PTC resettable fuse — swapped from 30R500U this revision, Rev 5, DS-PROT-006/033)** → D2 anode(STPS3L60, series reverse-polarity protection) → D2 cathode → D3 (SMBJ16A, shunt TVS, cathode-to-VM_MOTOR/anode-to-GND) → **U6 IN(pins1–3)/IN_SYS(pin6, tied to IN) — new Rev 5, §7.5.10** → U6 OUT(pins18–20) → U5 VCC(pins23,24) → C10 (10µF, VCC–GND, reused as U6's own OUT decoupling) |
| **U6_EN** *(new Rev 5, §7.5.10)* | U1 PA9 → U6 SHDN(pin13) — direct connection, no series resistor; **also → R11 (10kΩ) → GND**, external pull-down inverting U6's internal SHDN pull-up to the required default-OFF/fail-safe direction (REQ-403) |
| **U6_UVLO_TAP** *(new Rev 5, §7.5.10)* | U6 IN_SYS(pin6) → R12 (887kΩ) → U6 UVLO(pin7) |
| **U6_OVP_TAP** *(new Rev 5, §7.5.10)* | U6 UVLO(pin7) → R13 (60.4kΩ) → U6 OVP(pin8) → R14 (88.7kΩ) → GND |
| **U6_ILIM** *(new Rev 5, §7.5.10)* | U6 ILIM(pin11) → R15 (3.57kΩ) → GND |
| **U6_dVdT** *(new Rev 5, §7.5.10)* | U6 dVdT(pin10) → C17 (22nF) → GND |
| **U6_IN_BYPASS** *(new Rev 5, §7.5.10)* | U6 IN(pins1–3)/IN_SYS(pin6) → C16 (1µF) → GND |
| (NC) | U6 B_GATE(pin4), DRV(pin5) — floating, no external reverse-polarity FET used (D2 already covers this upstream, §7.5.10); U6 MODE(pin12) — floating, selects Latch-off overload response (Table 8-1); U6 PGOOD(pin17), FLT(pin15), IMON(pin14) — floating, all explicitly sanctioned by TI's own guidance, §7.5.10; U6 PGTH(pin16) → GND, forces the controlled-ramp turn-on path, §7.5.10 |
| **SPEED_PWM** *(new Rev 3, external pulldown added Rev 4)* | U1 PA8 (TIM1_CH1, AF2) → U5 SPEED(pin13) — PWM duty-cycle command, `SpdCtrlMd`=1 required (I2C-configured, firmware-owned, REQ-007/REQ-009 scope fence); **also → R10 (1kΩ, new Rev 4, ISS-015) → GND**, a real external pulldown holding SPEED near zero-command whenever PA8 is not actively driven (§7.5.5) |
| **DIR** *(new Rev 3, §7.5.4)* | U1 PB1 (plain GPIO, push-pull output) → U5 DIR(pin14) |
| **FG_TACH** *(new Rev 3, §7.5.4)* | U5 FG(pin12, open-drain) → R6 (4.75kΩ, pull-up to U5's own V3P3, pin9) → U1 PA6 (TIM3_CH1 input-capture, AF1, FT_ea 5V-tolerant) |
| **I2C1_SCL** *(new Rev 3, §7.5.4 — a different bus from the IMU's I2C2, not to be confused with the pre-Rev-3 I2C1/I2C2 mislabeling corrected under ISS-011)* | U1 PB6 (AF6) → R7 (4.75kΩ, pull-up to U5's own V3P3, pin9) → U5 SCL(pin10, open-drain) |
| **I2C1_SDA** *(new Rev 3, §7.5.4)* | U1 PB7 (AF6) → R8 (4.75kΩ, pull-up to U5's own V3P3, pin9) → U5 SDA(pin11, open-drain) |
| **U5_V3P3** *(new Rev 3, §7.5.3 — driver's own internal low-current reference output, distinct from the board's main 3V3 rail; no electrical connection between the two, per Option A)* | U5 V3P3(pin9) → R6/R7/R8 (pull-up references) → C15 (1µF/5V, V3P3–GND) |
| **U5_VREG/V1P8** *(new Rev 3, §7.5.3 — driver's own internal logic supply, linear mode, powers U5's internal circuitry only; explicitly NOT connected to the board's 3V3 rail or any MCU/IMU pin, per Option A/REQ-108)* | U5 SW(pin4) → R9 (39Ω ¼W, linear-mode select) → U5 VREG(pin6) → C13 (10µF/10V, VREG–GND) → U5-internal → V1P8(pin7) → C14 (1µF/5V, V1P8–GND) |
| **U5_CHARGE_PUMP** *(new Rev 3, §7.5.3 — internal gate-drive charge pump network, no MCU/external connection)* | U5 VCP(pin1) → C11 (0.1µF/10V, VCP–VCC) ; U5 CPP(pin2) → C12 (0.1µF ≥VCC×2 rating, CPP–CPN) → U5 CPN(pin3) |
| **MOTOR_PHASE_U/V/W** *(new Rev 3, §7.5 — 3-phase motor drive, no MCU involvement)* | U5 U(pins17,18) → M1 phase U; U5 V(pins19,20) → M1 phase V; U5 W(pins21,22) → M1 phase W |

## 13. Parts list (this design specifically — distinct from `bom/component-selection.md`'s candidate comparison)

| Ref | Part | Value/notes |
|---|---|---|
| U1 | STMicroelectronics STM32G031K8T6 | MCU, LQFP-32 |
| U2 | Bosch Sensortec BMI270 | IMU, LGA-14 |
| U3 | Texas Instruments TLV75533PDBVR | LDO, SOT-23-5, 3.3V fixed; EN (pin 3) tied directly to VIN (pin 2) — firm this revision, §3.4/ISS-001 |
| U4 | STMicroelectronics USBLC6-2SC6 | ESD protection, SOT-23-6 |
| J1 | USB-C receptacle | MPN not formally selected; illustrative real part GCT USB4125/4105 family used for height estimate only (§10) |
| J2 | 4-pin header | UART: TX/RX/GND/3V3 (REQ-106) |
| J3 | 4-pin header | SWD: VDD/SWCLK/GND/SWDIO (REQ-107) |
| SW1 | Momentary pushbutton, N.O. | Manual reset (REQ-004, Could) |
| D1 | Generic indicator LED | MPN not selected; Vf≈2.0V assumed |
| R1, R2 | 5.1kΩ | USB-C CC1/CC2 pull-downs (DS-CONN-001) |
| R3, R4 | 4.7kΩ | I2C SCL/SDA pull-ups (§5.2) — now correctly understood as the I2C2 bus, ISS-011 |
| R5 | 330Ω | LED current-limit resistor |
| C1 | 1µF ceramic | LDO input decoupling (min per TI ref circuit) |
| C2 | 0.47µF ceramic | LDO output decoupling (min per TI ref circuit) |
| C3 | 100nF ceramic | MCU VDD decoupling |
| C4 | 100nF ceramic | MCU VDDA decoupling |
| C5 | 100nF ceramic | NRST filter (per AN5096) |
| C6 | 100nF ceramic | IMU VDD decoupling |
| C7 | 100nF ceramic | IMU VDDIO decoupling |
| C8 | 1–4.7µF (optional bulk) | Near MCU, extra margin, not strictly required |
| C9 | 1µF (optional bulk) | Near IMU, per BMI270 datasheet §7.3.3 |
| MH1–MH4 | Mounting holes | M2.5, ×4, see §10 |
| **U5** *(new Rev 3)* | Texas Instruments DRV10983 | Sensorless 3-phase BLDC driver, HTSSOP-24 (PWP), exposed pad tied to GND; internal regulator configured for linear mode (§7.5.3) |
| **M1** *(new Rev 3)* | T-Motor MN2206-13 KV2000 | Sensorless BLDC reaction-wheel motor, 2S–3S; Component-Engineer-approved, human-signed-off via ECO-008 |
| **J4** *(new Rev 3)* | Same Sky PJ-102AH | Right-angle THT barrel jack, 2.0mm center pin (DS-CONN-005 — outer barrel diameter not independently confirmed this session, commonly paired with 2.0mm-center-pin jacks of this class but not asserted as a specific number here), 24V/5.0A rated, center-pin = (+) |
| **D2** *(new Rev 3)* | ST STPS3L60 | Schottky diode, 60V/3A, series reverse-polarity protection, VF=0.53V typ/0.62V max @3A/25°C (DS-PROT-005) |
| **D3** *(new Rev 3)* | Littelfuse SMBJ16A | Unidirectional TVS, SMB, 16.0V standoff/26.0V max clamp, shunt surge protection (DS-PROT-004) |
| **R6** *(new Rev 3)* | 4.75kΩ | FG pull-up, referenced to U5's own V3P3 (pin9), per DS-MTR-065 Table 11 |
| **R7** *(new Rev 3)* | 4.75kΩ | I2C1 SCL pull-up, referenced to U5's own V3P3, per DS-MTR-065 Table 11 |
| **R8** *(new Rev 3)* | 4.75kΩ | I2C1 SDA pull-up, referenced to U5's own V3P3, per DS-MTR-065 Table 11 |
| **R9** *(new Rev 3)* | 39Ω ¼W | U5 SW–VREG linear-mode-select resistor, per DS-MTR-065 Table 11 |
| **C10** *(new Rev 3)* | 10µF ceramic | U5 VCC–GND decoupling, per DS-MTR-065 Table 11 |
| **C11** *(new Rev 3)* | 0.1µF/10V ceramic | U5 VCP–VCC (charge pump), per DS-MTR-065 Table 11 |
| **C12** *(new Rev 3)* | 0.1µF, rated ≥VCC×2 | U5 CPP–CPN (charge pump), per DS-MTR-065 Table 11 |
| **C13** *(new Rev 3)* | 10µF/10V ceramic | U5 VREG–GND, per DS-MTR-065 Table 11 |
| **C14** *(new Rev 3)* | 1µF/5V ceramic | U5 V1P8–GND, per DS-MTR-065 Table 11 |
| **C15** *(new Rev 3)* | 1µF/5V ceramic | U5 V3P3–GND, per DS-MTR-065 Table 11 |
| **R10** *(new Rev 4, ISS-015)* | 1kΩ, 0603 | SPEED external pulldown to GND — added this revision, reversing Rev 3's "deliberate non-addition" stance; see §7.5.5 |
| **F1** *(new Rev 4, ISS-019; MPN swapped Rev 5)* | Littelfuse 30R500UF | Radial-leaded PTC resettable fuse, Ihold=5.00A/Itrip=10.00A/Vmax=30Vdc/Imax=40A, in-line on VM_MOTOR upstream of D2/D3 (DS-PROT-006/033) — **swapped from 30R500U this revision (Rev 5)**: same datasheet/electrical/mechanical spec, RoHS3-compliant construction, Active/orderable status (30R500U's own manufacturer-recommended direct replacement); see §7.5.9 |
| **F2** *(new, PCB Engineer at explicit Chief Engineer direction, ISS-032 loop-back fix, 2026-09-02)* | Littelfuse 30R500UF (identical MPN to F1) | Second radial-leaded PTC resettable fuse, in-line between J4's sleeve/GND pin and the shared ground net — protects against an *internal* J4 pin-mapping error (this design's own schematic/footprint assumption being wrong) that D2's series diode, sitting in the opposite leg, cannot cover; makes the worst case safe regardless of which physical pin is actually tip vs. sleeve, without needing to resolve that ASSUMPTION; see the corrected safety-argument text above |
| **U6** *(new Rev 5, ISS-015/019/021)* | Texas Instruments TPS26631PWPR | eFuse/load-switch supervisory controller, HTSSOP-20 (PWP), exposed pad (PowerPAD) tied to GND in addition to pin 9; Component-Engineer-proposed, human-approved (`bom/component-selection.md`); see §7.5.10 |
| **R11** *(new Rev 5)* | 10kΩ | U6 SHDN external pull-down (fail-safe-OFF direction), sized against TI's guaranteed 10µA leakage spec; see §7.5.10 |
| **R12** *(new Rev 5)* | 887kΩ, E96 1% | U6 IN_SYS–UVLO divider leg (top), OVP/UVLO trip-point network; see §7.5.10 |
| **R13** *(new Rev 5)* | 60.4kΩ, E96 1% | U6 UVLO–OVP divider leg (middle); see §7.5.10 |
| **R14** *(new Rev 5)* | 88.7kΩ, E96 1% | U6 OVP–GND divider leg (bottom); see §7.5.10 |
| **R15** *(new Rev 5)* | 3.57kΩ, E96 1% | U6 ILIM current-limit-set resistor, sets I(OL)≈4.69–5.40A; see §7.5.10 |
| **C16** *(new Rev 5)* | 1µF ceramic | U6 IN/IN_SYS input bypass, per TI's own ≥1µF surge-immunity recommendation; see §7.5.10 |
| **C17** *(new Rev 5)* | 22nF ceramic | U6 dVdT ramp-rate-setting capacitor, sized against this design's own C(OUT)=10µF (reused C10); see §7.5.10 |

**No BOOT0 pull-down resistor or header is included** — deliberate
decision, §4.2 (reasoning corrected this revision, ISS-006: BOOT0 is
muxed onto PA14/SWCLK, not PB8 as originally written; the design decision
itself is unchanged).

**No DRV10983 EN or FAULT pin/component is included** — there is none on
this part (§7.5.4); enable/disable is via the SPEED command itself, and
fault visibility is I2C-register-only or inferred from FG held high
(§7.5.6), consistent with the real pinout (DS-MTR-052) rather than an
assumed generic H-bridge-driver pin set.

**External SPEED pull-down resistor added this revision (R10, ISS-015)**
— reversing Rev 3's "deliberate non-addition" stance, §7.5.5: Cycle 3
review found the datasheet's own Table 11 reference circuit's omission
of one, and the internal `RPD_SPEED_SL`'s sleep-mode-only/DRV10983Z-only
documentation (55kΩ typ, DS-MTR-069), were not adequate mitigants given
the factory-default SPEED state is fully active analog mode, not inert
(DS-MTR-071) — see §7.5.5 for the full corrected reasoning.

## 14. Mandatory 18-item checklist walkthrough (my own agent instructions)

Every item addressed explicitly; each either cites an Evidence ID/REQ-ID
or states a clear ASSUMPTION/UNKNOWN, per the design task's instruction
not to skip any.

1. **Supply Voltage** — 5V USB VBUS (REQ-101, 4.75–5.25V; real-world
   USB-C vSafe5V ceiling up to 5.5V per independent research this
   revision, ISS-002) → 3.3V regulated (DS-PWR-003). See §2.1, §3.4/§3.5
   (§3.5 now carries an explicit disposition recommendation for the
   vSafe5V margin question, not a silent gap).
2. **Logic Voltage** — single 3.3V logic throughout (REQ-102); no level
   shifting anywhere. See §2.1.
3. **Absolute Maximum Ratings** — MCU VDD AMR **−0.3V to 4.0V** (DS-MCU-012,
   lower bound resolved this revision — ISS-010, §1); IMU VDD/VDDIO
   AMR −0.3…+3.6V (DS-IMU-004); LDO Vin AMR 6.0V (DS-PWR-002). All
   satisfied at the 3.3V/5V operating points used (§3.4, §5.4), including
   at the real-world worst-case 5.5V USB-C input (§3.5) — 0.5V/9%
   headroom remains even there.
4. **Recommended Operating Conditions** — MCU VDD ROC 1.7–3.6V
   (DS-MCU-013); IMU VDD/VDDIO ROC 1.71–3.6V/1.2–3.6V; LDO Vin ROC
   1.45–5.5V (DS-PWR-002; top-end margin against the real-world USB-C
   vSafe5V ceiling is effectively zero — addressed explicitly this
   revision with a recommended ACCEPTED-RISK disposition, §3.5, ISS-002,
   not left as a silent flag). All satisfied against REQ-101's own stated
   band; §3.5 documents the residual real-world-spec margin question.
5. **Current (per-pin and total)** — full computation in
   `hardware/power-budget.md`: ≈16.2mA worst-case / ≈7.0mA typical on the
   3V3 rail vs. 300mA (REQ-103) and 500mA (DS-PWR-003) ceilings — ≈95–97%
   margin either way. See §17 below and the power-budget file itself.
6. **Thermal** — LDO reuses `bom/component-selection.md`'s own computed
   estimate: ≈71°C TJ at 40°C ambient (REQ-201)/300mA load, ≈79°C headroom
   to 150°C max — and this design's real worst-case load (≈16.2mA) is
   ~18× lower than the 300mA figure that estimate already used, so actual
   heating is lower still. See `hardware/power-budget.md` Thermal
   cross-check section. No thermal risk anywhere else on the board (MCU
   and IMU both draw single-digit-to-low-double-digit mA at 3.3V, no
   meaningful self-heating).
7. **Decoupling** — MCU: C3(VDD)/C4(VDDA); IMU: C6(VDD)/C7(VDDIO); LDO:
   C1(in)/C2(out); NRST: C5. All per each part's own recommended values
   (§4.1, §4.3, §3.4, §5.3).
8. **Pull-up/Pull-down** — I2C: R3/R4=4.7kΩ, sized per NXP UM10204
   (DS-IFACE-001, §5.2), on what is now correctly labeled the I2C2 bus
   (corrected this revision, ISS-011); USB-C CC: R1/R2=5.1kΩ per USB-IF spec
   (DS-CONN-001, §3.1); BOOT0: none populated, see §4.2/§16 (reasoning
   corrected this revision, ISS-006: BOOT0 is on PA14, not PB8); NRST: internal
   pull-up only, per AN5096 (DS-MCU-047, §4.3). Separately, not a
   resistor pull but the same "under-specified pin" category: LDO EN is
   now a firm direct tie to VIN rather than a hedge — see item 17 below
   and §3.4 (ISS-001).
9. **Protection** — ESD/transient: USBLC6-2SC6 (DS-PROT-001/002, §3.2);
   reverse-voltage: mechanically-keyed connector, no series diode
   (§3.3, flagged for Hardware Reviewer); overcurrent: none added — no
   overcurrent-prone element exists on this bench design (no motor, no
   high-current output), and USB hosts/hubs already provide upstream
   overcurrent protection per the USB spec, so an additional onboard
   fuse/PTC was not judged necessary — **flagged as a judgment call, not
   independently re-verified this session**, see §16.
10. **Power sequencing** — **none required.** Single 3V3 rail feeds MCU
    (VDD/VDDA combined into one physical pin, no separate VBAT pin exists
    on this package — corrected this revision, ISS-027, §4.1) and IMU (VDD/VDDIO tied together, same
    rail) simultaneously; tying VDD=VDDIO on the IMU makes any
    VDD-before-VDDIO (or vice versa) sequencing requirement moot by
    construction — there is no relative timing between two supplies that
    are electrically the same node. The LDO itself has standard monotonic
    single-rail power-up behavior (not separately cited — not a
    multi-rail/sequenced regulator).
11. **Reset** — NRST: internal pull-up + C5 filter cap + optional SW1
    pushbutton, per AN5096 (DS-MCU-047, §4.3).
12. **Interface timing** — I2C: 400kHz target, pull-ups sized for a 300ns
    rise-time budget with the sensitivity analysis in §5.2; both MCU
    (Fast-mode Plus capable, DS-MCU-017) and IMU (Fast-mode Plus capable,
    DS-IMU-007) exceed this target speed's requirements with margin.
    UART: no fixed clock requirement beyond internal-oscillator baud-rate
    tolerance (§6), judged adequate for a point-to-point link at typical
    baud rates.
13. **MCU pin function** — **re-checked this revision (ISS-011, ISS-006,
    ISS-027)**.
    Full pin table in §11, now correctly showing **I2C2** on **PA11/PA12**
    (physical pins 22/23) — corrected this revision (ISS-027): the
    previous revision's PB10/PB11 assignment, while correctly labeled
    I2C2 by ISS-011's own fix, does not exist as a physical pin pair on
    this package at all (independently confirmed via ST's own official
    pin database, DS-MCU-064/067, HIGH confidence). This branch had
    independently begun a narrower version of this same fix (tracked as
    "Rev 6"/ISS-026/DS-MCU-073), moving only the I2C2 pins; the correction
    above supersedes it in full, additionally fixing the VDD/VDDA/VBAT/VSS/NRST
    pin-identity errors that fix never caught (see the "Rev 2, corrected"
    changelog entry). BOOT0/boot-strap pin
    handling
    in §4.2 corrected: BOOT0 is muxed onto **PA14** (shared with SWCLK),
    not PB8; PB8 does physically exist on this package (DS-MCU-051,
    confirmed at physical pin 32 per DS-MCU-064) but
    its function is I2C1_SCL (DS-MCU-053), unrelated to BOOT0 — the
    physical-bonding UNKNOWN that previously blocked this item is
    resolved (PB8 exists), though the nBOOT_SEL factory-default value
    itself remains community-sourced only, tracked as a residual bring-up
    verification item, not a pin-function unknown (§16). SWD dedicated
    pins (PA13/PA14) remain confirmed HIGH confidence, noting PA14's dual
    SWCLK/BOOT0-mux role explicitly, and now independently reconfirmed at
    physical pins 24/25 (DS-MCU-064). USART2 alternate-function assignment
    (PA2/PA3) remains MODERATE-HIGH confidence pending AF-table
    re-verification — unchanged this revision, out of scope for this
    cycle's HIGH-finding rework (§16). NRST is now known to share a
    physical pad with PF2 (pin 6), not a dedicated pin at pin 4 as
    previously stated (§4.1/§4.3, ISS-027).
14. **Interfaces (I2C/SPI/UART per each datasheet's recommended
    application circuit)** — I2C: BMI270's own recommended schematic
    followed exactly for decoupling/mode-select pins (§5.3, DS-IMU-074/075/076)
    — the MCU-side peripheral is **I2C2**, corrected this revision, ISS-011;
    UART: standard MCU USART2 mapping, no deviation from any datasheet
    recommendation since UART wiring is header-defined, not
    datasheet-constrained; SPI: not used (I2C chosen, §5.1).
15. **Grounding** — single ground net/plane, stated explicitly, §8/§2.2.
16. **Noise** — single solid ground pour (§8); short decoupling-cap trace
    runs recommended (<2mm, AN5096-style guidance, not independently
    re-cited beyond the NRST context); short I2C trace runs recommended
    (keeps actual bus capacitance near the §5.2 50pF planning assumption);
    linear LDO topology (vs. a switching converter) is inherently
    lower-noise, favorable for the IMU's supply quality — relevant since
    IMU measurement noise floor can be supply-noise-sensitive, though no
    specific BMI270 PSRR figure was pulled this session (ASSUMPTION that
    a linear LDO's noise floor is adequate, consistent with the
    Component Engineer's own LDO-vs-switching trade-off discussion in
    `bom/component-selection.md`).
17. **Recommended Application Circuit** — LDO: followed exactly, no
    deviation, **including EN→VIN, fixed firmly this revision (§3.4,
    ISS-001)** — previously a hedged connection, now a firm commitment
    matching TI's own always-enabled reference circuit exactly. IMU:
    followed almost exactly; INT1/INT2 left NC is
    a deliberate, logged deviation (polling instead of interrupt-driven,
    §5.3). MCU: no external crystal populated is a deliberate, logged
    deviation from a "full" application circuit that might include one
    (§6); no physical BOOT0 circuit is a deliberate, logged
    deviation/scope decision (§4.2, reasoning corrected this revision —
    ISS-006). ESD IC: D+/D− channels left unpopulated is a
    deliberate, logged deviation from the part's full 4-line typical
    application (§3.2).
18. **Mechanical/Thermal co-design** — **no longer N/A this revision** —
    real content in §9 (REQ-204/307: M1 is a genuine rotating body).

### Rev 3 motor-domain re-check (items 1–9, 13, 15–17)

Per this revision's design task, items 1–9 are explicitly re-checked
against the **new motor domain** (U5/M1/J4/D2/D3), not merely carried
forward by assumption:

1. **Supply Voltage (motor domain)** — VM_MOTOR sourced from J4, ROC
   8/24(typ)/28V at U5's VCC per its own datasheet (DS-MTR-054/056);
   this design's target source class is a 3S LiPo/DC source (≈11.1V
   nominal, ≈9–12.6V practical range) — comfortably inside ROC with
   substantial margin both directions. **2S sources (≈6.0–8.4V) are
   flagged as marginal-to-non-viable through the added series diode
   (D2)'s ~0.53–0.62V drop against U5's own 7/7.4/8V UVLO rising
   threshold — practical recommendation: 3S-only operation (§7.5.2,
   flagged for Hardware Reviewer, not self-resolved)**.
2. **Logic Voltage (motor domain)** — U5's own digital I/O (SPEED/DIR/
   SCL/SDA/FG) all operate at U5's own internal V3P3-referenced logic
   levels (VIH≥2.2V/VIL≤0.6V, DS-MTR-068/069) — compatible with the
   MCU's 3.3V logic (§7.5.4); no level-shifting needed, same conclusion
   as the existing logic domain, independently re-verified for this new
   cross-IC interface specifically.
3. **Absolute Maximum Ratings (motor domain)** — VCC AMR −0.3 to 30V
   (DS-MTR-053); U/V/W/SW outputs −1 to 30V; SPEED/SCL/SDA/DIR/FG −0.3
   to 4V. TVS (D3) clamps at 26.0V max, 4.0V/13% margin under the 30V
   VCC AMR ceiling (DS-PROT-004) — satisfied.
4. **Recommended Operating Conditions (motor domain)** — see item 1
   above; TJ ROC −40 to 125°C (DS-MTR-054), same as item 6 below.
5. **Current (motor domain, per-pin and total)** — U5 phase current 2A
   continuous/3A peak (DS-MTR-052/058); M1 derived need ≈1.05A nominal
   for the 5mN·m target, 18A continuous motor rating (component-selection
   research, well above what this driver would ever deliver — the driver,
   not the motor, is the practical current ceiling). J4's own 5.0A rating
   provides >4× margin over the ≈1.05A nominal / ≤3A absolute-worst-case
   figure. Full computation in the updated `hardware/power-budget.md`
   (§17).
6. **Thermal (motor domain)** — U5 RθJA=36.1°C/W (DS-MTR-055); at a
   conservatively-estimated worst-case internal dissipation (well under
   1W at ≈1.05A nominal operation, order-of-magnitude below the current
   AMR), junction-temperature rise stays far below the 125°C ROC ceiling
   with wide margin — not computed to a precise worst-case wattage this
   session (no continuous-stall-current operating scenario is expected
   in normal use, thanks to item 13's Lock Detection protection), flagged
   as a reasonable-but-not-exhaustive thermal treatment in §16. M1's own
   winding-temperature behavior is Component-Engineer/motor-datasheet
   territory, not independently re-derived here.
7. **Decoupling (motor domain)** — C10–C15, all per U5's own Table 11
   reference circuit (DS-MTR-065), no deviation (§7.5.3).
8. **Pull-up/Pull-down (motor domain)** — R6/R7/R8 (FG/SCL/SDA,
   4.75kΩ each, referenced to U5's own V3P3 per DS-MTR-065); no external
   SPEED pull-down added, deliberate, evidence-based (§7.5.5, DS-MTR-069).
9. **Protection (motor domain)** — 5 distinct mechanisms confirmed from
   U5's real datasheet (OCP, Lock Detection, UVLO, Thermal Shutdown, AVS
   — §7.5.6, DS-MTR-057/058/059/060/061), plus the added external series
   diode (D2, reverse-polarity) and shunt TVS (D3, surge) on the new
   power input (§7.5.2). **REQ-111/404 satisfied** — the specific
   mechanism relied on for overcurrent/stall protection is confirmed to
   be **Lock Detection** (auto-retry, I2C-configurable via `LockEn[5:0]`/
   `HWiLimitThr[2:0]`), not OCP (fixed, non-retrying) — a correction
   against `bom/component-selection.md`'s DS-MTR-037 description, flagged
   narratively for Hardware Reviewer/Hardware Lead reconciliation (§7.5.6,
   not self-resolved, no new ISS number self-assigned per this agent's
   scope).

13. **MCU pin function (motor domain)** — PA8 (TIM1_CH1/SPEED), PA6
    (TIM3_CH1/FG), PB1 (DIR), PB6/PB7 (I2C1 SCL/SDA) — all HIGH confidence
    on name/AF (DS-MCU-069/070), now also HIGH on physical LQFP-32 pin
    number (§11, DS-MCU-064; previously MODERATE, resolved as a byproduct
    of the "Rev 2, corrected" pin-identity fix, ISS-027, see §16 item 11).
15. **Grounding (motor domain)** — addressed as its own explicit decision,
    §8 — common ground net now deliberately spans both power domains,
    with return-current/layout guidance for REQ-010/REQ-204.
16. **Noise (motor domain)** — §8's return-current/physical-separation
    guidance (REQ-010, REQ-204); §5.5's REQ-010 regression check
    (independent rails, no shared bus/pin, decoupled per §7.5.3);
    linear-mode internal regulator (not switching/buck mode) chosen
    partly because it needs no external inductor, avoiding one more
    potential switching-noise source on this board (§7.5.3) — though the
    driver's own 3-phase commutation of M1 remains an inherent, expected
    noise source regardless of regulator mode, addressed via physical/
    ground separation, not elimination.
17. **Recommended Application Circuit (motor domain)** — U5's own Table
    11 reference circuit followed with **no deviation** (§7.5.3/§7.5.4;
    linear mode vs. buck mode is a choice **between two configurations
    TI's own datasheet documents**, not a deviation from either).

### Rev 4 motor-domain re-check (items 1, 3, 8, 9, 10 — Cycle 3 rework)

Per this cycle's 5 HIGH findings (ISS-014, ISS-015, ISS-019, ISS-020,
ISS-021), the following items are re-checked against **this revision's
fixes**, superseding or extending (not silently replacing) the "Rev 3
motor-domain re-check" conclusions immediately above wherever the
conclusion actually changed:

1. **Supply Voltage (motor domain) — SHARPENED (ISS-014).** The Rev 3
   re-check above already flagged 2S as "marginal-to-non-viable"; this
   revision corrects that to a precise, corner-by-corner result:
   2S **fails at the typical corner already** (7.4V nominal − D2's 0.53V
   typ VF = 6.87V, below U5's 7.4V typ VUVLO_R, DS-MTR-057) — not merely
   a rare worst case. 3S clears UVLO at every corner, margin ≈0.38V
   (near-cutoff 9.0V − 0.62V max VF = 8.38V vs. 8V max VUVLO_R), narrowing
   to ≈0.32V once new F1's own estimated ≈0.06V added drop is included.
   **New binding envelope: 9.0–13.0V (§7.5.9, ISS-019)**, replacing the
   previously-unbounded source assumption; enforced by new F1 in-line
   ahead of D2/D3.
3. **Absolute Maximum Ratings (motor domain) — EXTENDED (ISS-019).** New
   F1 (Littelfuse 30R500U, DS-PROT-006): Vmax=30Vdc, comfortably inside
   U5's own 30V VCC AMR ceiling with no added margin risk (F1 sits
   upstream in series, not across VCC, so its own Vmax is a rating on
   the part itself, not an added voltage at U5); Imax=40A, non-binding
   given J4/U5's own much lower operating currents. The new 9.0–13.0V
   envelope sits well inside every AMR already checked in the Rev 3
   re-check above — no AMR margin is newly put at risk by this
   revision's additions.
8. **Pull-up/Pull-down (motor domain) — REVERSED (ISS-015).** The Rev 3
   re-check above stated "no external SPEED pull-down added, deliberate,
   evidence-based (§7.5.5, DS-MTR-069)" — Cycle 3 review found that
   position inadequately evidenced once DS-MTR-071 (Table 8/§8.4.5.2)
   confirmed SPEED's factory-default state is active analog mode, not
   inert, and that the cited `RPD_SPEED_SL` pulldown is documented only
   for the DRV10983Z's sleep mode, not the plain DRV10983 actually
   specified. **This revision reverses that stance**: new **R10** (1kΩ,
   0603) is now wired SPEED→GND as a real external pulldown (§7.5.5,
   §12, §13). R6/R7/R8 (FG/SCL/SDA pull-ups) are unchanged.
9. **Protection (motor domain) — EXTENDED (ISS-019) and CAVEATED
   (ISS-021).** The Rev 3 re-check above already confirmed 5 internal
   mechanisms (OCP/Lock Detection/UVLO/Thermal Shutdown/AVS) plus D2/D3
   externally. **New this revision**: F1 adds a 6th protective element
   (PTC resettable fuse, fault-current magnitude/duration bounding,
   §7.5.9) on the same input path as D2/D3. **Caveat newly surfaced**:
   none of OCP, Lock Detection, or Thermal Shutdown **latch** — all
   auto-recover once the fault condition clears (DS-MTR-058/059/060) —
   so REQ-404's "Should"-priority "shutdown behavior to prevent sustained
   overheating" is **not fully satisfied by U5's hardware alone**
   (ISS-021, §7.5.12); a firmware-side latched-fault policy is now an
   explicit new requirement, not a hardware gap this hardware checklist
   item can itself close.
10. **Power sequencing (motor domain) — NEW ITEM this revision
    (ISS-015).** Not included in the Rev 3 motor-domain re-check above
    (a gap in that revision's own walkthrough scope, corrected here).
    U5's own datasheet recommends a GND→VCC→SPEED→FG connection order and
    cautions "ensure FG ≤ VCC at all times" (DS-MTR-066); this design's
    two power domains (MCU/IMU via J1, motor via J4) are independently
    sourced (Option A) with no hardware-enforced ordering between them.
    **This revision's fix**: R10 (item 8 above) bounds SPEED's own
    voltage regardless of which domain powers up first, removing the
    specific uncommanded-motion hazard Cycle 3 flagged. **Residual gap,
    honestly retained, not overclaimed as closed**: R10 fixes SPEED's
    *level*, not the power-up *order* itself — U5's VCC can still ramp
    before the MCU domain is alive, with no component forcing a specific
    sequence across J1/J4. Full ordering enforcement needs the flagged
    §7.5.10 supervisory load-switch (architecturally significant, routed
    to Component Engineer via Hardware Lead, not added this revision).

### Rev 5 motor-domain re-check (items 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 17 — U6 implementation)

Per this revision's own task (implement the now-human-approved U6 =
TPS26631PWPR), the following items are re-checked against **U6's own
addition specifically**, superseding or extending (not silently
replacing) the "Rev 4 motor-domain re-check" conclusions immediately
above wherever the conclusion actually changed. Full derivations are in
§7.5.10 — this subsection summarizes and cross-references rather than
repeating them.

1. **Supply Voltage (motor domain) — UNCHANGED, U6 checked against the
   existing envelope.** U6's own IN/IN_SYS pins sit on the same
   VM_MOTOR node already bounded to 9.0–13.0V (§7.5.9); U6's own ROC
   floor for IN_SYS (4.5V) sits well below the 9.0V floor, so U6 itself
   never becomes the binding voltage-margin constraint.
2. **Logic Voltage — CHECKED, compatible.** U6's SHDN pin ROC is
   0–5V (**DS-PROT-030**), directly compatible with the MCU's 3.3V logic
   (PA9) with no level-shifting needed — same single-3.3V-logic
   principle as the rest of this design (§2.1, REQ-102).
3. **Absolute Maximum Ratings — CHECKED, clear margin.** U6's IN_SYS AMR
   is −60V to 67V (75V/10ms transient) (**DS-PROT-030**) — the 9.0–13.0V
   envelope sits nowhere near either bound; SHDN/UVLO/OVP/dVdT/ILIM/MODE
   pin AMRs (§7.5.10 pinout) are all satisfied by their respective
   grounded/biased/logic-level connections.
4. **Recommended Operating Conditions — CHECKED, clear margin.** IN_SYS
   ROC 4.5–60V comfortably contains 9.0–13.0V; ILIM resistance ROC
   3–30kΩ contains R15=3.57kΩ; C(dVdT) ROC ≥10nF is satisfied by
   C17=22nF (§7.5.10).
5. **Current (per-pin and total) — RESOLVED, three-tier hierarchy now
   real.** R15 sets U6's own overload trip at 4.69–5.40A
   (min/typ/max) — 17.2% above U5's own 3–4A OCP ceiling at U6's
   worst-case-low corner, and clear of F1's 10A PTC trip — closing the
   previously-informal "U5 OCP, then F1 PTC" pairing into a real
   3-tier hierarchy (§7.5.10).
6. **Thermal (junction temp, derating, power dissipation) — CHECKED, wide
   margin.** U6's own conduction dissipation at this design's ≤3A
   worst-case (0.234–0.405W depending on R(ON) test corner) gives
   ΔTJ≈7.5–13.0°C — TJ≈53°C at REQ-201's 40°C ambient target in the
   conservative corner, 72°C/97°C/112°C margin below the ROC/AMR/T(TSD)
   ceilings respectively (§7.5.10).
7. **Decoupling — RESOLVED, new C16 added.** C16 (1µF, IN/IN_SYS–GND)
   satisfies three independent TI recommendations simultaneously
   (§7.5.10); U6's OUT-side decoupling reuses the existing C10 — no new
   output capacitor needed.
8. **Pull-up/Pull-down — RESOLVED, new R11 added.** R11 (10kΩ,
   SHDN–GND) inverts U6's internal SHDN pull-up to the required
   default-OFF/fail-safe direction, sized against TI's own guaranteed
   10µA leakage spec with 8×–20× margin against the SHUTF/SHUTR
   thresholds (§7.5.10 — full derivation, including the SHDN pull-up
   resistance discrepancy finding).
9. **Protection — RESOLVED (ISS-019's residual gap closed).** U6's OVP/
   UVLO divider (R12/R13/R14) closes the "sustained out-of-envelope DC
   input voltage" gap Rev 4's own re-check (item 9 above) explicitly
   left open — trip points 8.17–8.51V (UVLO rising) and 13.74–14.30V
   (OVP rising), both with real margin against the 9.0–13.0V envelope
   (§7.5.10). U6's MODE=Open latch-off behavior is a **new, additional**
   protection layer beyond U5's own three auto-recovering mechanisms —
   still not a full resolution of ISS-021's firmware latch policy (that
   remains undecided, §7.5.12 unchanged), but it is now the concrete
   device-level building block that policy would act through.
10. **Power sequencing — RESOLVED (ISS-015's residual gap closed).**
    Rev 4's own re-check (item 10 above) explicitly stated "Full
    ordering enforcement needs the flagged §7.5.10 supervisory
    load-switch... not added this revision." **This revision adds it**:
    U6's own default-OFF/fail-safe behavior (SHDN pulled low by R11
    whenever PA9 is undriven, i.e. whenever the MCU domain is unpowered
    or not yet initialized) now hardware-enforces that U5's VCC cannot
    energize ahead of a deliberate MCU-domain command, directly closing
    the cross-domain power-up-order gap Hardware Reviewer's own
    Recommended Fix option 2 asked for (§7.5.10).
13. **MCU pin function — RESOLVED, PA9 committed.** PA9 re-confirmed
    free and committed to U6's SHDN drive (§11) — no conflict with any
    alternate function used elsewhere in this design.
17. **Recommended Application Circuit — CHECKED, adherence confirmed,
    deviations justified.** IN_SYS tied to IN (no external
    reverse-polarity FET — D2 already covers this, a justified deviation
    from TI's optional Q1/Q2 circuit, not an omission); B_GATE/DRV/
    PGOOD/FLT/IMON floating (all explicitly sanctioned); PGTH tied to
    GND (a deliberate configuration choice, not TI's only option,
    justified in §7.5.10); PowerPAD soldered to GND in addition to pin 9
    (per TI's own instruction, not a substitute). Full detail and
    citations in §7.5.10.

## 15. Self-check against the Hardware Reviewer's 16-item checklist (`.github/skills/hardware-review/SKILL.md`)

This is a **self-check only** — it does not substitute for the mandatory
independent Hardware Reviewer pass (`.github/agents/circuit-engineer.agent.md`
"Out of scope": "Declaring your own design reviewed/complete... Independent
review is mandatory regardless of how confident you are"). Intent: catch
the obvious issues myself before handoff.

1. **Voltage violation** — Not found against each part's own ROC (§14
   items 3–4). The tightest margin in the whole design is the LDO's Vin
   ROC top-end: against REQ-101's own stated 4.75–5.25V band this was
   ≈0.25V/4.5% headroom, but **corrected this revision (ISS-002)** — the
   real-world USB-C/USB-PD vSafe5V ceiling is actually up to 5.5V, i.e.
   effectively **zero margin** against the LDO's 5.5V ROC ceiling at a
   legitimate worst-case input. This is not classified as a "voltage
   violation" against the LDO's ROC in the sense of exceeding it (5.5V in
   = 5.5V ROC ceiling, not exceeding it), but the margin is thin enough
   that it is called out explicitly with its own disposition in §3.5
   rather than being silently accepted — see §16 item 10.
2. **Absolute Maximum Rating violation** — Not found. **Resolved this
   revision (ISS-010)**: MCU VDD AMR lower bound is now confirmed at
   −0.3V (Hardware Reviewer verification against ST DS12992 Rev4 Table
   18, §1) — the previous UNKNOWN that partially blocked this item is
   closed. Separately, re-verified against §3.5's ISS-002 finding: even
   at the real-world worst-case 5.5V LDO input, the LDO's 6.0V Vin AMR is
   not violated (0.5V/9% headroom remains) — this is a ROC-margin
   question (item 1 above), not an AMR violation.
3. **Current limit** — Not found. ≈16.2mA worst-case vs. 500mA LDO rating
   and 300mA REQ-103 ceiling — no pin or rail is anywhere near a limit
   (§14 item 5, `hardware/power-budget.md`).
4. **Thermal risk** — Not found. LDO TJ≈71°C at a load condition (300mA)
   18× higher than this design's real worst-case draw (§14 item 6).
5. **Missing decoupling capacitor** — Not found. Every VDD/VDDA/VBAT/VDDIO
   pin has its own cap per the relevant datasheet's own recommendation
   (§14 item 7).
6. **Floating pin** — **Corrected/resolved this revision for the LDO EN
   pin (ISS-001)**: the LDO's EN (pin 3) previously carried a hedge
   ("if the exact package variant... requires a level, tie it to VIN...
   flagged as a minor implementation detail to confirm... at layout
   time") which was, on reflection, exactly the kind of unconfirmed
   floating-pin risk this checklist item exists to catch — EN has no
   internal pull-up/pull-down (TI SBVS320D, §3.4) and a genuinely
   floating EN produces undefined output behavior. This is now a firm,
   unconditional direct tie to VIN (§3.4, §12 `EN_VIN` net) — resolved,
   not merely mitigated. IMU pins: reviewed pin-by-pin as before — all
   IMU pins are either wired
   to a net or deliberately tied off (CSB→VDDIO, SDO→GND) except INT1,
   INT2, and the aux-interface pins (ASDx/ASCx/OCSB/OSDO), which are left
   genuinely NC — this is a **deliberate, logged decision** (§5.3), not an
   accidental float, since unused digital inputs on a modern low-power
   sensor are typically internally biased/don't-care when their
   associated function is disabled (BMI270's aux interface and interrupt
   outputs are software-disabled by default) — **not independently
   re-verified against the BMI270 datasheet's own floating-pin guidance
   this session**, flagged in §16 as worth a Hardware Reviewer
   second look given "floating pin" is its own explicit checklist item.
   MCU: no floating pins — every used GPIO is wired, and unused GPIOs are
   inherently fine floating (internal weak pull config is a firmware
   concern, not a schematic-level floating-pin risk, standard practice).
   ESD IC: I/O1/I/O2 (D+/D− channels) are deliberately NC — these are TVS
   diode inputs with no signal to protect, not floating in the
   "unintended" sense the checklist targets.
7. **Incorrect pull-up/pull-down** — Not found on I2C (§5.2, sized via a
   real formula, not assumed, now correctly labeled as the I2C2 bus,
   ISS-011) or USB-C CC (§3.1, spec-fixed value). BOOT0
   pull-down deliberately omitted — logged as a scope decision (§4.2,
   **reasoning corrected this revision, ISS-006**: BOOT0 is muxed onto
   PA14/SWCLK, not PB8; the design decision to omit a physical BOOT0
   circuit and rely on nBOOT_SEL's factory default is unchanged, only the
   pin-identity reasoning behind it is now accurate), not
   an oversight, but flagged again here since "incorrect
   pull-up/pull-down" could arguably be read to include "missing one that
   should exist" — my own position is that it's not missing (relies on
   nBOOT_SEL default instead, and §4.2 now also notes this carries no
   brick risk since SWD recovery is independent of nBOOT_SEL state), but
   this is exactly the kind of judgment
   call an independent reviewer should re-examine (§16).
8. **Logic voltage mismatch** — Not found. Single 3.3V logic throughout,
   no mismatched-voltage interface anywhere (§14 item 2).
9. **Interface timing** — Not found, with the I2C sensitivity caveat
   already logged in §5.2/§14 item 12 (4.7kΩ meets the 300ns budget
   comfortably at the 50pF assumption, marginally at a 75pF worst case).
10. **Power sequencing** — Not found; structurally moot by design (§14
    item 10).
11. **Grounding** — Not found; single ground net, explicitly stated (§8),
    **now updated this revision to explicitly address a two-power-domain
    system** — the motor rail (VM_MOTOR) and logic rail (3V3) are
    independently sourced (Option A), but deliberately share the same
    ground reference so the PWM/FG/I2C1 signals crossing between U1 and
    U5 remain valid single-ended logic (§8, full rationale). No
    grounding violation found; the two-domain rationale is itself the
    new content, not a defect.
12. **EMI/EMC risk** — No formal EMC pre-compliance target this cycle
    (REQ-401, "no specific regulatory certification target...for this
    prototype/benchmark iteration"). Reasonable practice followed: solid
    ground pour, short decoupling traces recommended, linear (not
    switching) regulator topology avoids switching-noise EMI entirely.
    No dedicated EMI filtering (ferrite beads, common-mode chokes) added
    on the USB VBUS line beyond the ESD/TVS array — judged unnecessary
    for a non-certified bench prototype; would be revisited if REQ-401's
    scope ever changes. **New Rev 3**: the motor domain adds a real,
    non-zero EMI source (U5's 3-phase commutation of M1) — mitigated by
    physical/ground separation guidance (§8), not by added filtering
    components; same "no formal EMC target this cycle" REQ-401
    disposition applies to the motor domain as well, not re-litigated
    per-subsystem.
13. **Motor noise** — **No longer Not Applicable this revision.** M1 (via
    U5's 3-phase commutation) is a real electrical-noise source. Addressed
    via: (a) REQ-010 regression check confirming no shared bus/pin/rail
    with the IMU (§5.5); (b) §8's physical-separation/return-current
    grounding guidance; (c) U5's own full decoupling network (C10–C15,
    §7.5.3) at the source; (d) linear-mode regulator choice avoiding an
    additional switching-noise source. No quantitative conducted/radiated
    noise measurement was performed this session (no PCB layout exists
    yet, §0) — flagged in §16 as a Hardware-Reviewer/layout-stage item,
    not fabricated as already-resolved.
14. **Sensor noise** — Addressed qualitatively (§14 item 16: linear LDO,
    short IMU decoupling/trace runs) but **no quantitative IMU
    noise-floor/PSRR analysis was performed this session** — flagged in
    §16 as a reasonable follow-up if IMU measurement precision becomes a
    concern in a later cycle (not currently a REQ). **New Rev 3 overlap
    with item 13 above**: the motor domain is now an additional
    potential sensor-noise contributor to watch for (not just the
    logic-rail supply-noise question this item originally addressed) —
    cross-referenced, not duplicated, in §5.5/§9.
15. **PCB layout concern (incl. mechanical/thermal co-design near
    rotating bodies)** — No PCB layout exists yet (no KiCad project, §0);
    board-geometry facts are recorded as estimates for the Mechanical
    Lead (§10, now including new Rev 3 rows for J4/U5/M1). **Mechanical/
    thermal co-design near rotating bodies: no longer N/A this
    revision** — M1 is a genuine rotating body; real content recorded in
    §9 (vibration-induced solder-joint/connector stress, thermal
    relevance to the IMU's bias stability) and flagged for the
    Mechanical Lead's later attention, not designed/mitigated by this
    agent.
16. **Datasheet recommendation violation** — All four parts' own
    recommended application circuits were followed, with every deviation
    explicitly logged and justified (§14 item 17 lists all four:
    LDO=none — **now including the EN→VIN tie fixed firmly this
    revision, ISS-001**, IMU=INT1/INT2 NC, MCU=no crystal/no BOOT0
    circuit (reasoning corrected, ISS-006), ESD
    IC=D+/D− NC). No unlogged/silent deviation identified in this
    self-check. **New Rev 3**: U5's own Table 11 reference circuit
    (DS-MTR-065) followed with no deviation — linear mode is one of two
    configurations the datasheet itself documents, not a departure from
    either (§14 item 17 motor-domain re-check).

**Self-check summary (Cycle 1, original)**: no CRITICAL or HIGH-severity issue identified by
my own pass. Several items carry an explicit residual flag for the
independent Hardware Reviewer to re-examine with fresh eyes (item 2's AMR
lower-bound UNKNOWN, item 6's IMU floating-pin judgment call, item 7's
BOOT0-pull-down scope decision, item 9's I2C capacitance sensitivity, item
14's absence of quantitative sensor-noise analysis) — these are flagged
precisely so the Hardware Reviewer knows where to look first, not because
I believe them to be actual defects.

**Re-self-check after Rev 2 fixes (Rev 2 cycle)**: focused re-check of
items most relevant to the three HIGH findings and the two folded-in
corrections, per my own agent instructions' handoff requirement —

- **Item 1 (Voltage) / Item 2 (AMR)** — ISS-010's AMR lower-bound UNKNOWN
  is closed. ISS-002's ROC-margin question is not silently left open: it
  now has an explicit disposition and recommendation in §3.5 (my
  recommendation: ACCEPTED-RISK, routed to the human Chief Engineer per
  `docs/architecture.md` §8 — see the handoff summary). I am not
  declaring ISS-002 resolved myself; that requires the named human
  sign-off the architecture doc specifies.
- **Item 6 (Floating pin)** — ISS-001's LDO EN pin is resolved: firm
  direct tie to VIN, no remaining hedge, matches TI's own recommended
  always-enabled connection exactly.
- **Item 7 (Incorrect pull-up/pull-down)** — ISS-006's BOOT0 reasoning is
  corrected (PA14, not PB8); the underlying design decision (no physical
  BOOT0 circuit) was already sound and remains unchanged — only the
  justification is now accurate. This item's residual flag (worth
  independent re-examination) still stands, unrelated to the correction.
- **Item 13 equivalent, §14 item 13 (MCU pin function)** — ISS-011's
  I2C1→I2C2 mislabeling is corrected everywhere I have found it
  (§2.3, §5.2, §5.3, §6, §11, §12, §13, §14); confidence for this
  specific pin pair upgraded to HIGH.
- **Item 16 (Datasheet recommendation violation)** — LDO recommended
  circuit is now followed exactly with no remaining hedge (EN→VIN firm).

No new CRITICAL or HIGH-severity issue was introduced by these fixes
themselves (verified: no new floating pin, no new AMR/ROC excursion, no
pin-table/net-list inconsistency found on this pass — see also the final
cross-section consistency check noted in the changelog at the top of
this document). ISS-002 remains, by design, an item for Hardware
Lead/Chief Engineer disposition rather than something I can close
unilaterally.

**Rev 3 motor-domain self-check (this revision)**: items 1–9 re-checked
against the new motor domain in full in §14's own "Rev 3 motor-domain
re-check" subsection (not duplicated verbatim here) — summary: no
CRITICAL or HIGH-severity issue identified by my own pass. Two findings
are flagged narratively for Hardware Reviewer/Hardware Lead attention,
neither self-resolved nor assigned a self-minted ISS number (per this
agent's scope, `.github/agents/circuit-engineer.agent.md` "Out of
scope"):

- **The OCP/Lock Detection correction** (item 9 above; §7.5.6) — the
  real overcurrent/stall protection mechanism is Lock Detection
  (auto-retry), not OCP (fixed, non-retrying) as `bom/component-
  selection.md`'s DS-MTR-037 description states. REQ-111/404 is still
  satisfied (Lock Detection is a genuine, configurable, auto-retry
  overcurrent/stall response), but the specific mechanism-name
  attribution should be reconciled between the two documents by
  Hardware Reviewer/Hardware Lead.
- **The 2S/3S UVLO finding** (item 1 above; §7.5.2) — a 2S source
  through the added series protection diode (D2) lands close to or
  below U5's UVLO rising threshold; practical recommendation is 3S-only
  operation, even though the Component-Engineer-approved motor (M1) is
  itself rated for 2S–3S. This is a consequence of the protection
  topology added this revision, not a flaw in the original part
  selection — flagged for Hardware Reviewer awareness and for whoever
  ultimately specifies the field power source.

No new CRITICAL or HIGH-severity issue is believed to have been
introduced by this revision's additions themselves (no floating pin
introduced — DIR's lack of an internal/external bias is flagged as a
low-severity residual, §16; no AMR/ROC excursion at the recommended 3S
operating point; no pin-table/net-list inconsistency found across
§7.5/§11/§12/§13 on this pass).

**Re-self-check after Rev 4 fixes (Cycle 3 rework)**: focused re-check
of items most relevant to this cycle's 5 HIGH findings (ISS-014, ISS-015,
ISS-019, ISS-020, ISS-021), per my own agent instructions' handoff
requirement —

- **Item 1 (Voltage violation)** — ISS-014's UVLO margin finding is
  corrected to its precise corner-by-corner result (§7.5.2, §14's new
  "Rev 4 motor-domain re-check" item 1): 3S-only is now stated as a
  **binding constraint**, not a soft recommendation; `hardware/
  power-budget.md`'s Rail Margin Summary is reconciled to the identical
  conclusion, closing the cross-document inconsistency Cycle 3 found. Not
  self-declared "resolved" in the sense of eliminating the constraint —
  the 2S/3S split is inherent to the added series-diode topology, and is
  flagged (not closed) for Hardware Lead/Component Engineer to decide
  whether an alternate topology is warranted (§16 items 17/22).
- **Item 3 (Current limit)** — ISS-019's unbounded J4 source envelope is
  closed with a new binding 9.0–13.0V envelope plus **F1** (PTC
  resettable fuse, §7.5.9). Residual, honestly retained: F1 bounds
  fault-current magnitude/duration, not continuous overvoltage — not
  overclaimed as full current-limiting (§16 items 22/23).
- **Item 4 (Thermal risk)** — ISS-021's finding that REQ-404's "shutdown
  behavior to prevent sustained overheating" is not fully satisfied by
  U5's own non-latching Thermal Shutdown/Lock Detection/OCP (all
  auto-recover, DS-MTR-058/059/060) is independently reconfirmed this
  session, not merely carried over from the reviewers' own finding. Not
  resolvable at the hardware level alone: a firmware latched-fault
  requirement is now specified (§7.5.12), flagged for Firmware Lead; the
  flagged §7.5.10 supervisory switch is noted as a candidate hardware
  backstop if firmware-only latching is later judged insufficient.
- **Item 6 (Floating pin) / Item 7 (Incorrect pull-up/pull-down)** —
  ISS-015's SPEED-pin risk is fixed with new **R10** (1kΩ, a real
  external pulldown, §7.5.5), reversing Rev 3's inadequately-evidenced
  "no external pulldown needed" position once DS-MTR-071 confirmed the
  factory-default state is active analog mode, not inert. R6/R7/R8
  (FG/SCL/SDA pull-ups) are unchanged, not re-opened.
- **Item 10 (Power sequencing)** — newly checked this cycle (Rev 3's own
  self-check did not cover this item — a gap in that revision's scope,
  corrected here via §14's new item 10). R10 bounds SPEED's own voltage
  regardless of power-up order, removing the specific uncommanded-motion
  hazard; the underlying cross-domain power-up-*order* gap itself is
  **not** eliminated and remains flagged for the §7.5.10 supervisory
  switch (§16 items 14/22).

**ISS-020 does not map to a specific item on this 16-item circuit-level
checklist** — a maximum-commanded-speed/overspeed ceiling is a
system-level operating-envelope/firmware-safety question, not a voltage,
AMR, current, thermal, pin-bias, sequencing, grounding, noise, layout, or
datasheet-deviation circuit defect. It is addressed via §7.5.11/§16 item
24 (flagged for Firmware Lead and tied to REQ-403's human-review gate),
deliberately not folded into this checklist so as not to mischaracterize
a firmware/policy gap as a circuit-level finding.

No new CRITICAL or HIGH-severity issue is believed to have been
introduced by this revision's own fixes themselves: R10 draws a small,
quantified, non-rail-threatening addition from 3V3 (§17); F1 sits well
within U5's own VCC AMR and within J4's connector rating; no new floating
pin, pin-table, or net-list inconsistency was found across §7.5/§11/§12/
§13 on this pass (§12/§13 cross-checked directly against §7.5.5/§7.5.9's
new component additions).

**Re-self-check after Rev 5 fixes (U6 implementation)**: per this
revision's own task instruction, a full, explicit pass of all 16 items
specifically against the new U6 stage (a new *active* IC — the first one
this design adds beyond U1–U5 — so every item genuinely applies, not just
the ones a passive part would typically touch):

1. **Voltage violation** — Not found. U6's IN/IN_SYS sit on VM_MOTOR,
   already bounded 9.0–13.0V (§7.5.9); U6's own ROC (IN_SYS 4.5–60V)
   contains this envelope with wide margin on both sides (§14's Rev 5
   re-check item 1).
2. **Absolute Maximum Rating violation** — Not found. IN_SYS AMR −60V to
   67V (75V/10ms transient) is nowhere near the 9–13V envelope; every
   other pin's AMR is satisfied by its grounded/biased/logic connection
   (§7.5.10 pinout; §14 item 3).
3. **Current limit** — Not found; **improved**. New R15 gives U6 its own
   overload trip (4.69–5.40A) sitting cleanly between U5's OCP (3–4A) and
   F1's PTC (10A) — a real 3-tier hierarchy where an informal 2-tier
   pairing existed before (§14 item 5).
4. **Thermal risk** — Not found. Conduction dissipation 0.234–0.405W
   (R(ON) test-corner dependent) gives ΔTJ≈7.5–13.0°C; 72°C+ margin below
   every relevant ceiling at REQ-201's 40°C ambient target (§14 item 6).
5. **Missing decoupling capacitor** — Not found; **new C16 added**
   (1µF, IN/IN_SYS–GND), satisfying three independent TI recommendations;
   OUT-side reuses existing C10 (§14 item 7).
6. **Floating pin** — **Present by design, each individually justified,
   not accidental.** B_GATE, DRV, MODE, PGOOD, FLT, and IMON are all left
   floating — every one of these is an **explicitly TI-sanctioned**
   floating configuration (§7.5.10 cites the exact datasheet text for
   each), not an unexamined omission the way a genuinely accidental
   floating pin would be. This is the one item on this checklist where
   U6 has more floating pins than any prior part in this design, so it is
   called out explicitly rather than silently passed.
7. **Incorrect pull-up/pull-down** — Not found; **new R11 added and
   independently re-derived from scratch this session** (10kΩ, sized
   against TI's guaranteed 10µA SHDN leakage spec, 8×–20× margin). The
   SHDN internal-pull-up-resistance discrepancy (1MΩ per this agent's own
   datasheet read vs. ≈440kΩ per the task/human's independent web
   search) is flagged as a residual item (§16) — not blocking, since
   R11's sizing basis doesn't depend on either figure, but recorded
   transparently rather than silently resolved in favor of one source.
8. **Logic voltage mismatch** — Not found. SHDN ROC is 0–5V, directly
   compatible with the MCU's 3.3V logic (PA9) — same single-3.3V-logic
   principle used throughout this design (§14 item 2).
9. **Interface timing** — Not found as a violation; **a deliberate,
   explained design choice exists**. PGTH tied to GND forces every
   turn-on through the C(dVdT)-scaled delay path (≈1.83ms with C17=22nF)
   rather than the faster fixed-delay alternative — negligible in
   absolute terms, but flagged so Hardware Reviewer can confirm this
   trade-off (safety/inrush-control over speed) is acceptable given no
   currently-open issue demands a faster U6 turn-on (§7.5.10).
10. **Power sequencing** — **Resolved, not just "not found."** This is
    the item U6 exists specifically to close: ISS-015's cross-domain
    power-up-order gap, open since Rev 3 and explicitly still open after
    Rev 4 (§14's own Rev 4 re-check item 10), is now hardware-enforced by
    U6's default-OFF/fail-safe behavior (§14's Rev 5 re-check item 10).
11. **Grounding** — Not found. U6 GND (pin 9) **and** the PowerPAD are
    both tied to the ground plane, per TI's own explicit instruction that
    the pad is not a substitute for the pin (§7.5.10, §12's GND net row).
12. **EMI/EMC risk** — Not found; **U6 is itself a mitigant, not a new
    risk**. TI's own text states the controlled inrush/dVdT function
    "helps to eliminate conductive and radiative interferences" — this
    design's own choice to ground PGTH (forcing the controlled-ramp path
    on every turn-on, not just relying on the fast-path default) leans
    further into this benefit, not away from it.
13. **Motor noise** — Not applicable to U6 specifically; U6 does not
    touch the 3-phase motor lines (§7.5's own MOTOR_PHASE_U/V/W net,
    unchanged this revision). Rev 3's own finding stands unmodified.
14. **Sensor noise** — Not applicable to U6; no electrical path between
    U6 and the IMU domain exists (separate power domains, §8). Rev 3's
    own finding stands unmodified.
15. **PCB layout concern** — Two new, concrete layout requirements this
    revision, both recorded for the Mechanical Lead/layout handoff: (a)
    all three IN pins and all three OUT pins must be physically ganged
    together per TI's own explicit instruction (§7.5.10); (b) the
    PowerPAD must be soldered to the ground plane, item 11 above.
16. **Datasheet recommendation violation** — Not found. IN_SYS tied to
    IN, B_GATE/DRV floating, C(IN)≥1µF, PowerPAD-to-GND — all per TI's own
    recommended application circuit (§7.5.10). The one deliberate
    **deviation** — omitting TI's optional external reverse-polarity
    Q1/Q2 FETs — is explicitly justified (D2 already provides that
    function upstream), not an unexamined gap, satisfying this agent's
    own instruction that "deviations must be justified and logged."

**No new CRITICAL or HIGH-severity issue is believed to have been
introduced by U6's own addition.** The one item flagged as genuinely
open (item 7's SHDN pull-up-resistance discrepancy) does not change any
sizing decision in this design and is recorded for Hardware Reviewer/
Component Engineer awareness, not as a blocking defect — full detail and
five further residual items in §16.

## 16. Open UNKNOWNs (for Hardware Lead / Hardware Reviewer)

**Annotation convention (new this revision)**: items below are annotated
**RESOLVED**/**CORRECTED** in place where this revision's rework closed
them, rather than being deleted or renumbered — this preserves external
cross-references that already cite specific item numbers (e.g.
`validation/design-review.md`'s "§16 UNKNOWN #2" and "§4.1/§16 UNKNOWN
#1"). A new item 10 is appended (not inserted) for the one finding
(ISS-002) that is a **known fact pending a disposition decision**, a
different category from the other items' original "unconfirmed fact"
framing.

In priority order:

1. **BOOT0/PB8 pin-bonding status — CORRECTED this revision (ISS-006).**
   Originally: "BOOT0/PB8 pin-bonding status on the exact STM32G031K8T6
   LQFP-32 package is UNKNOWN (DS-MCU-049). My own pin-count research
   (DS-MCU-046) does not show a PB8 pin in this package's pin list at
   all..." **This is now corrected, not merely re-flagged**: independent
   research this cycle (Hardware Lead, DS-MCU-051/053) confirms PB8
   *does* physically exist on this package, **and** confirms BOOT0 is not
   muxed onto PB8 at all — BOOT0 is muxed onto **PA14** (already this
   design's SWCLK pin, §4.2/§4.4), while PB8's real function is the
   secondary AF6 mapping for I2C1_SCL (DS-MCU-053). The original "PB8
   doesn't exist, so the BOOT0 question is moot" reasoning was simply
   wrong on both counts — PB8 exists, and it was never the BOOT0 pin to
   begin with. **Residual item RESOLVED this pass (ISS-027)**: PB8/PB9's
   *exact pin numbers* are now confirmed with HIGH confidence against ST's
   own official pin database (DS-MCU-064) — PB9 is physical pin 1, PB8 is
   physical pin 32 (§11) — closing the "not independently re-resolved"
   gap this item previously carried.
   **Design decision (unchanged)**: no physical BOOT0 circuit populated,
   relying on the nBOOT_SEL=1 factory default (DS-MCU-044, MODERATE
   confidence, still not independently re-verified this session) — this
   decision was always correct, now for the accurate reason. §4.2 also
   newly notes there is no brick risk from this either way, since SWD
   recovery does not depend on nBOOT_SEL state. Recommend the Hardware
   Reviewer (or a future session with access to the raw ST RM0454/datasheet
   PDF) still re-verify the nBOOT_SEL default value itself before this
   design is considered final for fabrication (not a blocker for this
   paper-design cycle, REQ-502).
2. **STM32G031K8T6 VDD Absolute Maximum Rating lower bound — RESOLVED
   this revision (ISS-010).** Originally UNKNOWN (carried forward from
   `bom/component-selection.md`, DS-MCU-012 only confirmed the 4.0V upper
   bound). **Now resolved**: the Hardware Reviewer independently verified
   the lower bound at **−0.3V** against ST DS12992 Rev4 Table 18 — see
   §1. No remaining gap on this item.
3. **STM32G031K8T6 VDD/VSS exact pin count discrepancy — RESOLVED this
   pass (ISS-027).** Originally a moderate-confidence discrepancy across
   sources (DS-MCU-046: 1 VDD/2 VSS from 3 converging distributor sources
   vs. a separate lower-detail source claiming 1 VDD/1 VSS), flagged for
   completeness but not thought to change any design decision. **Now
   resolved with HIGH confidence** against ST's own official pin database
   (DS-MCU-064/065): the lower-detail source was actually right — there is
   only **one** VSS pin (physical pin 5, combined "VSS/VSSA"), not two.
   This also revealed the 3-source "convergence" was itself wrong on VDD's
   own pin *number* (claimed 17; real is 4, combined "VDD/VDDA") and on
   the existence of separate VDDA (does not exist) and VBAT (does not
   exist) pins — a materially larger correction than this item originally
   anticipated. See §4.1/§11/§12 for the corrected pin table and net list.
4. **I2C1/USART2 alternate-function pin assignments — the I2C portion
   corrected TWICE now; see ISS-027.** Originally: "PB10/PB11 for I2C1
   SCL/SDA; PA2/PA3 for
   USART2 TX/RX were not individually re-verified against the exact
   STM32G031K8T6 alternate-function table this session... MODERATE /
   MODERATE-HIGH confidence." A prior revision (ISS-011) corrected the
   *peripheral-instance label* from I2C1 to I2C2 on these same pins,
   citing DS-MCU-052/ST DS12992 Rev4 Table 16, and marked this item
   "resolved" — **that resolution was itself incomplete**: it corrected
   which peripheral the pins mapped to, but never independently
   cross-checked whether PB10/PB11 are physically bonded out on this
   32-pin package at all (a different table in ST's own data). Independent
   research this pass (Hardware Lead, ST's own official pin database,
   DS-MCU-064/067) found they are **not** — this package has no PB10/PB11
   pin at all. **Now corrected a second time, and now HIGH confidence for
   the right reason**: I2C2_SCL/SDA are physically PA11/PA12 (pins 22/23,
   default/unremapped state) — corrected throughout this document (§2.3,
   §5.2, §5.3, §6, §11, §12, §13, §14). Credit for the *original* AF-table
   correction (I2C1→I2C2) stands — that fact remains true and useful, it
   was simply insufficient on its own to guarantee physical buildability.
   **The USART2 (PA2/PA3) portion remains open, unchanged this
   revision** — still
   MODERATE-HIGH confidence, standard STM32 convention, not individually
   re-pulled from the exact AF table; should still be confirmed against
   the real AF table (or via STM32CubeMX) before committing to a PCB
   layout. Low risk of being wrong given how conventional this mapping
   is, but not yet a closed item — though independently corroborated at
   least at the pin-*number* level this pass (PA2=physical pin 9,
   PA3=physical pin 10, DS-MCU-064).
5. **BMI270 floating/NC pin guidance (INT1, INT2, ASDx, ASCx, OCSB, OSDO)
   was not independently re-verified against the BMI270 datasheet's own
   explicit floating-pin recommendations this session** — I assumed
   these are safe to leave NC when their associated function
   (aux-interface, interrupts) is software-disabled, consistent with
   common practice for this class of part, but this specific claim
   should get a fresh look from the Hardware Reviewer (flagged explicitly
   in my own self-check, §15 item 6). **Unchanged this revision** — out
   of scope, not one of this cycle's HIGH findings or folded-in
   corrections.
6. **Whether "reverse-polarity protection" in REQ-402 is satisfied by a
   mechanically-keyed connector alone, or was intended to require a
   discrete series diode regardless**, is a judgment call I made (§3.3)
   that the Hardware Reviewer or Hardware Lead may want to weigh in on —
   not a factual UNKNOWN so much as an interpretive one. **Unchanged
   this revision** — relates to ISS-004/ISS-012, explicitly out of scope
   for this cycle (Hardware Lead will route separately).
7. **Onboard overcurrent protection (e.g. a resettable PTC fuse on
   VBUS) was judged unnecessary** and not added, reasoning that USB
   hosts/hubs already provide upstream overcurrent protection — this
   judgment was not independently re-verified against any specific
   host-side spec this session (§14 item 9), flagged for the Hardware
   Reviewer. **Unchanged this revision** — relates to ISS-005, explicitly
   out of scope for this cycle.
8. **J1's exact USB-C receptacle MPN, and D1's exact LED MPN, are not
   formally selected this cycle** — both are placeholders (illustrative
   real parts cited only for the board-geometry height estimate and the
   LED forward-voltage assumption, respectively). Selecting exact MPNs is
   a follow-on BOM task, not blocking this design document. **Unchanged
   this revision** — out of scope, not one of this cycle's HIGH findings.
9. **U3's exact EN-pin behavior — RESOLVED this revision (ISS-001).**
   Originally: "not re-confirmed against the literal pinout diagram this
   session... assumed tied to always-enabled per the standard reference
   circuit; low-risk, flagged for layout-stage confirmation." **Now
   resolved, and firmly**: independent research this cycle (Hardware
   Lead, TI SBVS320D Rev D §4/§5.5/§6.4) confirms the TLV75533PDBVR's
   5-pin SOT-23-5 (DBV) package EN pin (pin 3) is mandatory (present on
   every package variant) with no internal pull-up/pull-down — a
   genuinely floating EN would produce undefined behavior. This design
   now implements a firm, unconditional direct tie from EN (pin 3) to
   VIN (pin 2), matching TI's own recommended always-enabled connection
   exactly (§3.4, §12 `EN_VIN` net, §13 parts list). No remaining hedge
   or layout-stage confirmation needed on this point.
10. **ISS-002 — LDO input-voltage margin against the real-world USB-C
    vSafe5V ceiling: known facts, pending Hardware Lead/Chief Engineer
    disposition (new this revision, not an "unconfirmed fact" UNKNOWN
    like the items above — the facts themselves are settled).** The real
    USB-C/USB-PD vSafe5V ceiling is 4.75–5.5V (wider than REQ-101's
    stated 4.75–5.25V), leaving effectively zero margin against the
    TLV75533PDBVR's 5.5V Vin Recommended Operating Condition ceiling at a
    legitimate worst-case input — though the LDO's 6.0V Absolute Maximum
    Rating still provides real headroom (0.5V/9%) even at 5.5V, so this
    is a regulation-margin concern, not a damage risk. Full disposition
    discussion and my own recommendation (ACCEPTED-RISK, per
    `docs/architecture.md` §8, requiring named human Chief Engineer
    sign-off — with option (b), an alternate-LDO evaluation, noted but
    not chosen) is in the new §3.5. **This item is explicitly not closed
    by this document** — it requires the Hardware Lead to route it for
    the human sign-off the architecture doc specifies before it can be
    marked resolved or accepted.

**New this revision (Rev 3) — motor subsystem items 11–20:**

11. **Physical LQFP-32 pin numbers for the 5 new motor-domain pins
    (PA8/PA6/PB1/PB6/PB7) — RESOLVED (folded in from the "Rev 2,
    corrected" pin-identity fix, ISS-027).** Originally MODERATE
    confidence (pin **names**/AF numbers HIGH via DS-MCU-069/070, but
    their placement within the 32 physical package pin numbers not
    independently re-resolved this session, the same residual category as
    the existing PB8/PB9 pin-numbering gap, item 1 above). ST's own
    official CubeMX pin database (DS-MCU-064, obtained independently this
    pass for the unrelated ISS-027 pin-identity correction, §11) turns out
    to also settle this item as a byproduct — it enumerates all 32
    physical pin positions by name, confirming PA6=13, PB1=16, PA8=18,
    PB6=30, PB7=31 at the same HIGH confidence as the rest of that
    table. No blocker for this paper-design cycle remains on this point;
    confirmed, not just deferred, before layout.
12. **PB6/PB7's Fm+ (400kHz+ I2C)/FT_f 5V-tolerance classification is a
    MODERATE-confidence family generalization** — confirmed as AF6=I2C1
    (DS-MCU-070/Table 14), but not independently re-confirmed against a
    specific Table-18 FT_f line item this session the way PA6/FT_ea was
    (DS-MCU-071). Low risk (this design only requires 3.3V-referenced
    operation, well within any STM32G0 GPIO's basic ROC regardless of
    FT/Fm+ classification specifics) but flagged for completeness.
13. **DIR pin has no internal or external bias and is not proven safe if
    floating during MCU reset/init** — low-severity residual concern: an
    undriven DIR input on U5 during the brief window before the MCU's
    GPIO init completes could latch an indeterminate direction on first
    spin-up. No component was added to mitigate this (would need a
    pull-up/pull-down that isn't in TI's own Table 11 reference circuit
    either) — flagged for Hardware Reviewer/firmware awareness rather
    than resolved with hardware.
14. **Cross-domain power-up sequencing is not hardware-enforced — SPEED's
    voltage is now bounded regardless of sequencing (ISS-015, this
    revision), but the ordering gap itself is not eliminated.** Originally:
    "the MCU/IMU domain (via U3) and the motor domain (via J4→D2→D3→U5)
    are independently sourced per Option A, so there is no guarantee about
    which powers up first relative to the other... Bounded somewhat by
    SPEED's partial internal pulldown (RPD_SPEED_SL, DS-MTR-069)... but
    not a complete guarantee." Cycle 3 review found this partial mitigant
    inadequate (the factory-default SPEED state is fully active analog
    mode, not inert, DS-MTR-071; `RPD_SPEED_SL` is documented only for the
    DRV10983Z variant's sleep mode, not the plain DRV10983 actually
    specified) and escalated this to HIGH, tying it to REQ-403 (ISS-015).
    **This revision's fix**: new R10 (1kΩ, real external pulldown to
    ground, §7.5.5) now firmly bounds SPEED's own voltage during any
    uncommissioned window, independent of power-up order. **What remains
    open**: R10 bounds SPEED's *level*, it does not itself enforce a
    power-up *order* — U5's own VCC can still ramp before the MCU domain
    is alive, and no component forces a specific sequence across the two
    intentionally-independent connectors (J1, J4). Directly enforcing the
    missing order requires a supervisory switch — **flagged in new
    §7.5.10**, routed to Component Engineer via Hardware Lead as an
    architecturally significant addition, not resolved by this revision's
    passive fix alone.
15. **PJ-102AH (J4)'s 3rd terminal is left unpopulated, its exact function
    not confirmed** — the datasheet's own drawing shows 3 terminals
    (center pin + 2 outer), consistent with a normally-closed
    switch-contact design common in this connector class, but the
    specific datasheet page fetched this session did not include an
    internal schematic unambiguously labeling which outer terminal is
    the switch contact vs. sleeve/GND (DS-CONN-005 metadata file, "Known
    gaps" section). This design uses the center pin (+) and one outer
    terminal (assumed sleeve/GND); the third terminal is left
    unpopulated. Low risk (leaving a switch contact unpopulated is a
    safe default — it simply never activates whatever it would have
    controlled) but flagged for layout-time confirmation.
16. **DRV10983's I2C address was not extracted from the datasheet this
    session** — does not affect this design's hardware wiring (only one
    I2C1 slave exists on this segment, so no address conflict is
    possible regardless of its value), deferred as a firmware-relevant
    detail, not a circuit-relevant one.
17. **2S vs. 3S source viability through the added protection diode
    (D2) — SHARPENED and CORRECTED this revision (ISS-014).** Originally:
    "a 2S source (≈7.4V nominal) minus D2's ~0.53–0.62V forward drop
    lands at ≈6.87V, close to or below U5's UVLO rising threshold
    (7/7.4/8V min/typ/max, DS-MTR-057)... Recorded as a practical '3S-only
    operation recommended' finding... not a flaw in the Component-
    Engineer-approved motor selection... but a consequence of this
    revision's own added series protection diode." Cycle 3 review found
    this framing understated the finding on two counts: (a) 2S actually
    fails **at the typical corner** (6.87V < 7.4V typ), not merely a
    close/marginal case; (b) this document's own prior wording ("only a
    freshly-charged 2S pack clears UVLO with any margin") disagreed with
    `hardware/power-budget.md`'s own Rail Margin Summary on the identical
    scenario — an unresolved cross-document inconsistency. **This
    revision's fix**: §7.5.2 is rewritten with corner-by-corner numbers
    (typical, max, near-cutoff) and now states **3S-only as a binding
    practical constraint**, not a soft recommendation; `hardware/
    power-budget.md`'s Rail Margin Summary is reconciled to state the
    identical conclusion. New F1 (§7.5.9, ISS-019) narrows the 3S margin
    further, from ≈0.38V to ≈0.32V — quantified, not left unstated. Still
    flagged for Hardware Reviewer/Hardware Lead to confirm the operational
    recommendation, and **flagged, not self-resolved**, for propagation
    into `bom/component-selection.md`/`requirements/requirements.md`
    (both outside this agent's edit scope) and for Component Engineer to
    evaluate a lower-VF ideal-diode/ORing-FET topology if 2S support is
    later required.
18. **The OCP/Lock Detection mechanism-name correction** — this design's
    research (DS-MTR-058/059) finds that `bom/component-selection.md`'s
    DS-MTR-037 description of DRV10983 overcurrent protection as
    "programmable via I2C…auto-retry" in fact describes the **Lock
    Detection** feature, not **OCP** itself (which is a fixed,
    non-configurable, non-retrying, condition-based-clear mechanism).
    REQ-111/404 is still satisfied (Lock Detection is the genuine
    configurable auto-retry response relied on), but the two documents'
    mechanism-name attribution should be reconciled. `bom/component-
    selection.md` is not edited by this agent (out of Circuit Engineer
    scope, per this agent's own instructions) — flagged for Hardware
    Reviewer/Hardware Lead to log formally if they concur.
19. **BMI270's own bias-vs-temperature coefficient was not independently
    re-extracted from its datasheet this session** (§9) — MEMS IMU bias
    drift with die temperature is a well-known general characteristic,
    cited qualitatively, but the BMI270's own specific figure was not
    pulled to quantify how much thermal separation from U5/M1 is actually
    needed. Flagged as a residual research gap for whoever (Hardware
    Reviewer, or a future session) wants to turn §9's qualitative
    flag into a quantitative thermal-separation spec for the Mechanical
    Lead.
20. **M1's mass, full mechanical outline, shaft diameter, and
    mounting-hole pattern were not independently pulled from T-Motor's
    own mechanical drawing this session** (§10) — only the standard
    BLDC "XXYY" size-code convention (⌀22mm×6mm stator, ASSUMPTION) is
    recorded. Needed by the Mechanical Lead before REQ-307's
    vibration-isolation mount can be designed; this design's own
    electrical-side scope stops at flagging the need. Related: whether
    M1 mounts directly to this PCB or to a separate mechanical structure
    (off-board, wired) is also UNKNOWN/not resolved this session — a
    Mechanical Lead decision, §10.
21. **U5's precise worst-case power dissipation/junction-temperature rise
    was not computed to an exact wattage this session** (§14 motor-domain
    re-check item 6) — RθJA=36.1°C/W is confirmed (DS-MTR-055), and the
    qualitative margin against the 125°C ROC junction-temperature ceiling
    is wide (well under 1W at ≈1.05A nominal operation, an order of
    magnitude below the current AMR), but a precise figure would require
    the integrated FET bridge's own RDS(on) — **not independently
    extracted for the DRV10983 specifically this session** (a same-family
    alternate candidate, DRV10970, has a recorded ~400mΩ combined figure,
    DS-MTR-044, but that number belongs to a different part and is
    deliberately not borrowed here to avoid misattributing it to U5). Flagged
    as a reasonable-but-not-exhaustive thermal treatment for the Hardware
    Reviewer, to be tightened if a precise figure is later needed (e.g. for
    a sustained-near-stall duty-cycle use case beyond this design's nominal
    ≈1.05A operating point).
22. **RESOLVED/IMPLEMENTED this revision (Rev 5) — §7.5.10's supervisory
    motor-rail protection controller is now U6 = TPS26631PWPR, selected,
    approved, and wired.** Originally: "§7.5.10's flagged supervisory
    motor-rail protection controller is not yet a selected part... Its
    required function and ratings are specified..., but no MPN is
    chosen... routed to Component Engineer via Hardware Lead for a real
    comparison, not selected unilaterally by this agent." This is now
    resolved: Component Engineer proposed TPS26631PWPR; the human Chief
    Engineer approved it (`bom/component-selection.md`, "Approved —
    'TPS26631PWPR confirmed.'"); this revision implements the load-switch
    (ISS-015), OVP/UVLO divider (ISS-019 residual), and PA9/SHDN enable
    line (also ISS-021's physical enforcement point, §7.5.12) — see
    §7.5.10 for full derivation. ISS-015's cross-domain power-up-ordering
    gap and ISS-019's continuous-overvoltage gap are now both closed at
    the hardware level (§14's Rev 5 re-check, items 9 and 10). **Residual,
    not fully closed by this item's resolution**: ISS-021's firmware latch
    *policy* remains entirely undecided — see item 25 below, unchanged in
    substance this revision.
23. **The 9.0–13.0V VM_MOTOR input envelope (§7.5.9, new Rev 4) is still
    not yet recorded in `validation/bring-up-procedure.md`** — unaffected
    by this revision's U6 addition (U6 hardware-enforces the envelope,
    §7.5.10, but does not substitute for documenting it in that
    separately-owned procedure). That document still has no motor-rail
    section as of this revision and is not edited by this agent
    (ambiguous ownership between Hardware Reviewer, Hardware Lead, and a
    future firmware/bring-up owner). Flagged so whoever authors that
    section includes this bound, and now also U6's own trip points
    (§7.5.10) as the hardware behavior bring-up testing should expect to
    observe.
24. **Maximum commanded speed / overspeed ceiling is undecided** (new
    this revision — ISS-020, §7.5.11). This document proposes ~6000 RPM
    (2× REQ-007's own floor) only as a numeric anchor for discussion, not
    a decision. The actual ceiling, commanded ramp-rate limit, and
    overspeed-response behavior are Firmware Lead's/the human safety
    reviewer's call, and the chosen ceiling must also feed Mechanical
    Lead's flywheel/containment design. Ties to REQ-403's human-review
    gate — this item cannot be closed by this agent alone. **Unaffected
    by Rev 5** — explicitly not addressed with a circuit trick this
    revision, per this revision's own task instruction; remains a
    firmware-policy gap.
25. **Firmware latched-fault policy for REQ-404 is undecided/
    unimplemented** (new this revision — ISS-021, §7.5.12). The required
    behavior is specified (count consecutive Lock Detection events,
    Status bit4/`MtrLck`, within a rolling window over the existing I2C1
    bus; force SPEED to a safe/stopped state; require deliberate re-arm),
    but this is a firmware requirement, not something a schematic-level
    document can itself close. Flagged for Firmware Lead. **Updated Rev
    5**: the candidate hardware enforcement point (item 22 above) is now
    specified and selected — **U6, driven by the already-committed
    PA9/SHDN line** (§7.5.10/§11) — but the actual retry-counting,
    rolling-window, and re-arm *policy* remains entirely undecided and is
    **explicitly not implemented, invented, or defaulted by this hardware
    revision** (per this revision's own task instruction not to resolve
    ISS-021 with a circuit trick). A related nuance newly surfaced this
    revision, also for Firmware Lead's awareness: U6's own MODE=Open
    setting (§7.5.10) gives U6 *its own*, independent overload latch
    (distinct from any future firmware-declared latch) — both are reset
    by the same SHDN low-to-high toggle, which is convenient, but
    firmware will need to distinguish "U6 latched on its own overload
    event" from "firmware declared a Lock-Detection-based fault" if the
    two are ever meant to be logged/handled differently; U6 provides no
    register or flag (PGOOD/FLT are both left floating) that would let
    firmware directly tell these apart.
26. **F1's own added series resistance is an ESTIMATE, not a datasheet-
    sourced figure** (new this revision — ISS-019, §7.5.2/§7.5.9).
    Littelfuse's own datasheet publishes only Rmin (initial) and R1max
    (post-trip) resistance, not a max-initial figure; the ~0.06V drop used
    in this revision's UVLO-margin analysis assumes 0.02Ω in-circuit
    resistance × 3A — a reasonable but unverified estimate, not a sourced
    figure. **Confirmed unchanged by the Rev 5 30R500U→30R500UF swap**:
    the two parts share the same datasheet/electrical specification
    (§7.5.9, DS-PROT-033), so this estimate applies equally to the new
    MPN. Flagged for Hardware Reviewer to confirm or tighten if a more
    precise figure becomes available (e.g. a manufacturer datasheet
    revision, or a bench measurement at bring-up).
27. **U6's internal SHDN pull-up resistance — two different figures in
    circulation, neither a guaranteed spec** (new this revision, §7.5.10).
    This agent's own read of TI's Figure 8-1 functional block diagram
    shows "1 MΩ" (matching the pre-existing DS-PROT-013 TI E2E forum
    citation and Component Engineer's own datasheet metadata record); the
    task/human's independent web search instead cites "≈440kΩ". Neither
    figure appears in TI's formal Electrical Characteristics table (no
    guaranteed min/typ/max row exists for this specific resistance) —
    this plausibly explains the discrepancy without requiring either
    source to be wrong. **Not blocking**: R11's own sizing (§7.5.10) is
    derived from TI's guaranteed 10µA SHDN leakage spec, independent of
    either pull-up figure, and dominates the divider by ≈44×–100× either
    way. Flagged for Hardware Reviewer/Component Engineer awareness —
    worth a direct TI query or E2E-forum confirmation if a future
    revision needs a tighter bound (e.g. a lower-power variant design).
28. **U6's OVP trip point full-stack-worst-case margin against a 4S pack
    is real but not large** (new this revision, §7.5.10). Reference-
    tolerance-only worst case (14.2975V) clears a 4S pack's nominal
    14.8V by 3.4%; full-stack worst case (reference **and** ±1% resistor
    tolerance both adverse, 13.4881V) clears the 13.0V envelope ceiling
    by only 3.75%. Both remain positive margins, not violations, but
    neither is a wide margin — flagged so Hardware Reviewer can judge
    whether this design's own E96/1% resistor choice is adequate or
    whether tighter-tolerance (e.g. 0.1%) resistors would be warranted
    for R12–R14 in a future revision, particularly if a real 4S-pack
    mis-connection is judged a credible, not just theoretical, field
    scenario.
29. **U6's dVdT capacitor (C17) is sized against this design's own real
    C(OUT), not against either of TI's own worked-example scenarios**
    (new this revision, §7.5.10). TI's own datasheet illustrates the
    dVdT/inrush-current equation at C(OUT)=1mF (a 15W-DC-DC-converter
    buffer-capacitor use case, §9.2.2.3) and, in a separate figure
    caption, at C(OUT)=30mF — both roughly 100×–3000× larger than this
    design's own real C(OUT)=10µF (the existing C10, reused, not a new
    output capacitor). C17=22nF was independently derived from TI's own
    Equations 1–2 against this design's actual 10µF, not copied from
    either TI example. Flagged only so Hardware Reviewer can independently
    verify this distinction was made correctly (an earlier internal draft
    of this section briefly conflated the two before being caught and
    corrected this session) — not because the final C17 value itself is
    in doubt.
30. **ISS-027 — final severity classification pending independent
    Hardware Reviewer determination (new this pass; renumbered from this
    section's own former item 11 to avoid colliding with the Rev 3
    motor-subsystem items 11–20 above — content unchanged apart from the
    ISS-014→ISS-027 renumbering applied consistently across this
    document).** The facts themselves are settled (see the "Rev 2,
    corrected" changelog entry at the top of this document, and
    §2.3/§4.1/§11/§12): the previously documented PB10/PB11 I2C2 pins do
    not exist on this package; the real pins are PA11/PA12; VDD/VDDA are
    one combined pin (4), VSS/VSSA are one combined pin (5), VBAT does not
    exist, and NRST shares a pad with PF2 (pin 6). I have applied the fix
    and recommend **CRITICAL** (`docs/architecture.md` §7.1 — "design will
    fail... as designed", which a non-existent pin describes more
    precisely than ISS-011's own HIGH classification did), but per my own
    agent instructions this classification is the Hardware Reviewer's to
    make, not mine to self-assign. See `validation/open-issues.md`
    ISS-027.

## 17. Power budget (summary — full detail in `hardware/power-budget.md`)

**3V3 logic rail (Rev 2/Rev 3 figures below unchanged; new Rev 4 addition
called out separately — REQ-103):**

- **Worst-case total on 3V3 rail ≈16.2mA** (MCU 10.2mA@64MHz [DS-MCU-014]
  + IMU 0.685mA [DS-IMU-010] + LED ≈3.94mA [ESTIMATE] + I2C pull-ups
  worst-case ≈1.4mA [ESTIMATE]).
- **Typical total ≈7.0mA** (MCU 2.1mA@16MHz + IMU 0.685mA + LED ≈3.94mA +
  I2C pull-ups realistic ≈0.3mA).
- **New Rev 4: R10 (SPEED pulldown, ISS-015) adds ≈0–3.3mA, PWM-duty-cycle
  dependent** (3.3V high-level ÷ 1kΩ). PA8 drives SPEED_PWM as a
  TIM1_CH1 PWM output, not a static level, so R10's own draw is not
  constant — 0mA whenever PA8 is instantaneously low, up to 3.3mA
  worst-case whenever it is instantaneously high. Using the standard
  conservative worst-case-superposition convention this budget already
  applies to every other rail entry (all worst-case figures assumed
  simultaneous, not the real expected coincidence), the worst-case 3V3
  total becomes **≈19.5mA**; a representative mid-duty (~50%) typical
  addition of ≈1.65mA brings the typical total to **≈8.65mA**.
- **New Rev 5: R11 (U6 SHDN pulldown, §7.5.10) adds ≈330µA when PA9 is
  driven high** (3.3V ÷ 10kΩ) — a static GPIO output (not PWM, unlike
  PA8/R10), so unlike R10 this is not a duty-cycle-dependent figure: 0mA
  whenever PA9 is held low (U6 disabled, the fail-safe default state)
  and a steady ≈330µA whenever PA9 is held high (U6 enabled, the normal
  motor-running state). Folded into both totals as a continuous addition
  (the condition under which the motor subsystem is actually usable),
  bringing the worst-case 3V3 total to **≈19.83mA** and the typical total
  to **≈8.98mA**. (U6's own IQ and OVP/UVLO-divider bias current draw
  from **VM_MOTOR**, not 3V3 — tracked separately in the VM_MOTOR rail
  section below, never folded into this 3V3 total.)
- **Margin vs. REQ-103 (≤300mA)**: ≈280.2mA / ≈93.4% margin (was ≈93.5%
  pre-R11 / ≈94.6% pre-R10 — negligibly reduced each time).
- **Margin vs. TLV75533PDBVR's 500mA rating (DS-PWR-003)**: ≈480.2mA /
  ≈96.0% margin (was ≈96.1% pre-R11 / ≈96.8% pre-R10).
- Both still confirm the Component Engineer's own pre-design expectation
  ("MCU+IMU are only ~10-15mA combined") — even including the LED, I2C
  pull-ups, and now R10, total draw remains an order of magnitude below
  either ceiling.
- LDO thermal: reused ≈71°C TJ estimate at 40°C ambient/300mA
  (`bom/component-selection.md`), ≈79°C headroom to 150°C max — and this
  design's real load (even with R10) is far below the 300mA that estimate
  already used, so actual heating is lower still.

**VM_MOTOR rail (new Rev 3, sharpened/extended this revision — REQ-109,
tracked entirely separately from the 3V3 budget above, never folded in):**

- **Connector: J4 = Same Sky PJ-102AH**, rated 24V/5.0A (DS-CONN-005) —
  finalizes the placeholder row that `hardware/power-budget.md` previously
  carried as "TBD."
- **New Rev 4: bounded source envelope, 9.0–13.0V (ISS-019, §7.5.9)** —
  derived from the 3S-only conclusion below (9.0V = 3S near-cutoff) and
  a 3S full-charge ceiling plus headroom (13.0V ≥ 12.6V + ~3%); excludes
  4S and above. Enforced by **F1 (Littelfuse 30R500UF PTC resettable
  fuse, DS-PROT-006/033 — MPN swapped from the obsolete 30R500U this
  revision, Rev 5, same datasheet/electrical/mechanical spec, §7.5.9)**
  in-line ahead of D2/D3, bounding fault-current magnitude/duration
  rather than precisely limiting steady-state current (F1's 10.00A Itrip
  exceeds J4's own 5.0A rating — an honestly-scoped gap, not overclaimed
  as precision current-limiting).
- **New Rev 5: continuous (non-fault) overvoltage lockout — now
  provided, closing the gap F1/D3 always left open (ISS-019 residual,
  §16 item 22 RESOLVED).** New **U6 (TPS26631PWPR, §7.5.10)** adds a
  continuous OVP comparator referenced to this same 9.0–13.0V envelope
  via its own resistor divider (R12/R13/R14): OVP trips at 13.7368V
  (min) / 14.0171V (typ) / 14.2975V (max) referenced-tolerance-only, or
  13.4881V full-stack worst case (reference **and** resistor tolerance
  both adverse) — all above the 13.0V ceiling, all below a 4S pack's
  14.8V nominal (3.4–3.75% clearance, §16 item 28). UVLO trips at
  8.1721V (min) / 8.3388V (typ) / 8.5056V (max) referenced-tolerance-only,
  or 8.6527V full-stack worst case — all below the 9.0V floor. U6 also
  now gives ISS-015's cross-domain power-up ordering gap a hardware
  enforcement point (default-OFF load-switch, §14's Rev 5 re-check item
  9) and ISS-021's eventual firmware latch a physical actuation point
  (PA9/SHDN, §7.5.12) — the firmware latch *policy* itself remains
  undecided (§16 item 25, unchanged this revision).
- **New Rev 5: U6's own current draw on VM_MOTOR — small, non-material
  to the rail margin.** IQ(ON)=1.38mA typ/1.7mA max (device operating,
  load-switch closed); IQ(OFF)=21µA typ/60µA max (SHDN low, device
  disabled); OVP/UVLO divider bias current 8.69–12.55µA (continuous,
  regardless of SHDN state, since the divider taps IN_SYS directly).
  Combined worst case ≈1.76mA — under 0.06% of J4's 5.0A connector
  rating and under 0.06% of U5's own 3–4A OCP window; not a material
  change to any VM_MOTOR margin figure computed elsewhere in this
  section. (R11's own ≈330µA, when SHDN is driven high by PA9, is a 3V3
  logic-rail draw, not a VM_MOTOR draw — tracked in the 3V3 rail section
  above instead, consistent with this budget's own convention of never
  folding the two rails together.)
- **Motor+driver worst-case current: ≈1.05A nominal** (derived target for
  5mN·m, Kt≈4.77mN·m/A) **/ ≤3A absolute worst-case** (TI's own
  start-up/locked-motor ceiling, DS-MTR-056) — this 3A figure sits right
  at U5's own fixed OCP threshold (3 MIN/4 MAX A, DS-MTR-058), i.e. TI
  itself designed the protection point around this same realistic worst
  case.
- **Margin vs. J4's own rating**: ≈2.0A / ≈40% (3A worst-case vs. 5.0A
  connector rating) — comfortable margin at the connector/protection-path
  level.
- **Margin vs. U5's OCP threshold**: ≈0–1A / 0–25% at the MIN threshold —
  tight, but expected: this is a protection trip point TI sized close to
  the real worst case, not a rail-capacity ceiling meant to have wide
  margin.
- **Practical source-class recommendation: 3S only — SHARPENED this
  revision to a binding constraint, not a soft recommendation
  (ISS-014, §7.5.2, §16 item 17).** A 2S source fails UVLO margin at its
  **typical** corner already (7.4V nominal − D2's 0.53V typ VF = 6.87V,
  below U5's 7.4V typ VUVLO_R), not merely in a rare worst case as
  previously stated here — this revision corrects that understatement.
  3S clears UVLO at every corner (near-cutoff 9.0V − 0.62V max VF =
  8.38V > 8V max VUVLO_R), with margin narrowing from ≈0.38V to ≈0.32V
  once F1's own estimated ≈0.06V added drop is included. This remains a
  consequence of this design's own added series protection diode, not a
  flaw in the Component-Engineer-approved motor selection (M1 is validly
  rated 2S–3S) — flagged for propagation into `bom/component-
  selection.md`/`requirements/requirements.md` (outside this agent's
  edit scope).
- **Protection mechanisms for REQ-111/404 — none latch (ISS-021,
  §7.5.12, §16 item 25).** OCP (fixed, condition-based-clear,
  DS-MTR-058), Lock Detection (I2C-configurable, auto-retry after 5s,
  DS-MTR-059), and Thermal Shutdown (auto-recover, DS-MTR-060) all
  self-clear once the fault condition subsides — none of the three
  latches off. REQ-404's "Should"-priority "shutdown behavior to prevent
  sustained overheating" is therefore **not fully satisfied by hardware
  alone**; this revision specifies (but, as a firmware behavior, cannot
  itself implement) a firmware-side latched-fault policy counting
  consecutive Lock Detection events. This also corrects the prior
  mechanism-name attribution in `bom/component-selection.md`'s DS-MTR-037
  (flagged for Hardware Reviewer/Hardware Lead reconciliation, §16 item
  18 — not edited by this agent).
- **Thermal**: U5 RθJA=36.1°C/W (DS-MTR-055) against a 125°C ROC ceiling —
  qualitatively wide margin at ≈1.05A nominal, not computed to a precise
  worst-case wattage this session (RDS(on) not independently extracted for
  this specific part, §16 item 21). D2's own worst-case fault-condition
  dissipation (≈1.86W at 3A/0.62V, §7.5.2) is a separate, already-bounded
  figure from a prior revision.
- **Field DC source itself (battery pack/bench supply/adapter) is not a
  specified component** — an operational choice outside this schematic's
  parts list, the same convention Rev 2 already used for J1's upstream
  "USB host." The 3S-class/9.0–13.0V bound above is this revision's
  explicit constraint on whatever that source turns out to be.
- Full numeric detail, all four tables (Supply Capability, Subsystem Load,
  Rail Margin Summary, both Thermal cross-checks), updated this revision
  in `hardware/power-budget.md` (F1 added to Supply Capability, R10 added
  to Subsystem Load, Rail Margin Summary reconciled to state the
  identical 3S-only conclusion as §7.5.2 above — closing the
  cross-document inconsistency Cycle 3 review found).

## 18. Handoff (per `.github/agents/circuit-engineer.agent.md`)

**This is a re-handoff after Cycle 1's Hardware Reviewer findings — not a
first handoff.** See the Revision changelog at the top of this document
for the full list of what changed this cycle.

**To**: Hardware Reviewer, via Hardware Lead, for a **fresh re-review**
(not a first review) — per `.github/skills/hardware-review/SKILL.md`'s
guidance that a re-review after a fix means re-running the checklist
against the changed areas, this handoff calls out exactly which areas
changed so the re-review can focus there (§2.3, §3.4, §3.5 [new], §4.1,
§4.2, §5.2, §5.3, §6, §11, §12, §13, §14, §15, §16 — see changelog).

**Artifacts**:
- This document (`hardware/schematic/bench-imu-01-design.md`), revised —
  schematic artifact + design rationale log + self-check results
  (including the new "Re-self-check after Rev 2 fixes" pass, §15),
  combined.
- `hardware/power-budget.md` — **unchanged this cycle**; none of this
  revision's fixes (I2C relabeling, EN pin firm tie, vSafe5V disposition,
  BOOT0/PA14 correction, VDD AMR resolution) alter any current/power
  number.
- `datasheets/evidence-log.md` — Cycle 1 originally added 17 Evidence ID
  rows (DS-MCU-044–049, DS-IMU-074–077, DS-PWR-046, DS-PROT-001–002,
  DS-CONN-001–004, DS-IFACE-001) plus 7 new datasheet metadata records
  (USBLC6-2SC6, JEDEC package outline standards, NXP UM10204, USB-IF
  Type-C spec, GCT USB4125, GCT USB3140, ST NUCLEO-G031K8/UM2324) — see
  `datasheets/` directory; that history is unchanged. **Unchanged by me
  this cycle**: the Hardware Lead already appended the DS-MCU-050–053
  corrections (independent re-verification of ISS-006/ISS-011) per
  `validation/change-log.md` ECO-002, which this revision cites directly
  throughout.
- Open `UNKNOWN`s: §16 above — **4 of 9 original items resolved/corrected
  this cycle** (item 1 BOOT0/PB8 corrected — ISS-006; item 2 VDD AMR
  lower bound resolved — ISS-010; item 4 partially resolved, I2C portion
  only — ISS-011; item 9 EN-pin behavior resolved — ISS-001), **5 items
  unchanged and still open** (items 3, 5, 6, 7, 8 — all explicitly out of
  scope for this cycle), **plus 1 new item appended** (item 10, ISS-002's
  disposition — a known-facts-pending-decision record, not a fresh
  unconfirmed-fact UNKNOWN).

**On ISS-002 specifically**: I have not self-declared this resolved or
accepted anywhere in this document. §3.5 states my own engineering
recommendation (ACCEPTED-RISK) with reasoning, but per
`docs/architecture.md` §8, a HIGH finding may only become ACCEPTED-RISK
with named human Chief Engineer sign-off — that sign-off has not
happened, and is not mine to grant. I am asking the Hardware Lead to
route this finding for that decision (or, if the Hardware Lead judges a
component change is warranted instead, to route it to the Component
Engineer for an alternate-LDO evaluation — I have flagged but not chosen
between these two paths, consistent with my own agent instructions'
"Out of scope" constraint against unilaterally re-selecting a part).

No KiCad project exists to run `extract_schematic_netlist` /
`analyze_schematic_connections` / `validate_project` against (§0) — this
document is the self-check substitute for this cycle, as it was for
Cycle 1.

I have not declared this design "reviewed" or "complete" anywhere in this
document — per my own agent instructions, that determination is the
Hardware Reviewer's alone to make. I am also not marking ISS-004,
ISS-005, ISS-007, ISS-008, or ISS-009 resolved, touched, or in any way
addressed by this revision — those remain for a later disposition pass,
per the Hardware Lead's own scoping of this cycle's work.

### 18.1 Rev 3 handoff (this revision — Motor Driver + Reaction Wheel addition)

**This is a new-subsystem handoff, not a re-review of a prior fix cycle.**
Rev 2 above (Cycle 2) was Design-Complete and human-approved before this
revision began; none of its content was reopened except where this
addition genuinely required it (§2.1–§2.3 rails/ground-scheme/pin
allocation, §11 free-GPIO inventory, §12/§13 net/parts lists, §14/§15
checklists, §16/§17 UNKNOWNs/budget). See the Revision changelog at the
top of this document for the complete list of what Rev 3 changed, section
by section.

**To**: Hardware Reviewer, via Hardware Lead, for a **first review of the
Rev 3 motor subsystem addition** — per `.github/skills/hardware-review/
SKILL.md`, this is new-block review, not a fix re-check, so the full
16-item checklist applies to the new content, not just the changed-area
subset. Areas touched this revision: §1, §2.1–§2.3, §5.5 [new], §7.5
[new, 8 subsections], §8 [rewritten], §9 [rewritten, N/A→real], §10
[additions], §11 [additions + a transparently-flagged Rev 2 bookkeeping
gap], §12 [additions], §13 [additions], §14 [item 18 flipped + new
motor-domain re-check subsection], §15 [items 11/13/15/16 rewritten + new
motor-domain self-check subsection], §16 [11 new items, 11–21], §17
[new VM_MOTOR summary].

**Artifacts**:
- This document (`hardware/schematic/bench-imu-01-design.md`), revised to
  Rev 3 — schematic artifact + design rationale log + self-check results
  (§14/§15, including the new Rev 3 motor-domain re-check/self-check
  subsections), combined.
- `hardware/power-budget.md` — **finalized this revision**: the
  previously-placeholder VM_MOTOR row ("TBD"/"specific connector...still
  to be sourced") now carries real numbers — J4=Same Sky PJ-102AH
  (24V/5.0A, DS-CONN-005), motor+driver worst-case ≈1.05A nominal/≤3A
  absolute-worst-case, full Supply Capability / Subsystem Load / Rail
  Margin Summary tables, plus a new U5 thermal cross-check section. No
  `TBD` rows remain in that file for this revision's subsystem.
- `datasheets/evidence-log.md` — **+25 new rows this revision**
  (DS-MTR-052 through DS-MTR-070 [19 rows, DRV10983 pin/AMR/ROC/thermal/
  5-protection-mechanism/register-map/reference-circuit research],
  DS-MCU-069/070/071 [3 rows, STM32G031 PA8/PA6/PB1/PB6/PB7 pin/AF
  confirmations], DS-CONN-005 [J4/PJ-102AH], DS-PROT-004/005 [D3/SMBJ16A,
  D2/STPS3L60]) — verified against no duplicate row IDs. **No new
  datasheet metadata files created**: all 25 rows cite the metadata
  records already registered at `datasheets/texasinstruments_drv10983_
  slvscp6h.md`, `datasheets/tmotor_mn2206-13-2000kv_rev-unknown.md`,
  `datasheets/samesky_pj-102ah_rev1-05.md`, `datasheets/littelfuse_
  smbj16a_rev4.md`, and `datasheets/stmicroelectronics_stps3l60_ds2134-
  rev7.md`, per the task's explicit instruction not to duplicate
  already-registered parts' metadata records. One citation-precision fix
  made to the STPS3L60 metadata file this revision (an internal
  cross-reference correction, not a new fact).
- Open `UNKNOWN`s: §16 above — **11 new items appended this revision**
  (items 11–21, none renumbering or deleting the 10 pre-existing Rev
  1→2 items, per this section's own established "annotate/append, don't
  renumber" convention). Two of these are the headline findings I am
  flagging most strongly for Hardware Reviewer/Hardware Lead attention
  (neither self-resolved, no ISS number self-assigned, per my own
  agent instructions' scope):
  1. **Item 18 — OCP/Lock Detection mechanism-name correction**:
     `bom/component-selection.md`'s DS-MTR-037 attributes DRV10983's
     I2C-programmable auto-retry overcurrent behavior to "OCP"; this
     revision's primary-source research (DS-MTR-058/059) finds that
     description actually belongs to the separate **Lock Detection**
     feature, not OCP itself (which is fixed/non-configurable). REQ-111/
     404 is still satisfied either way (Lock Detection is the genuine
     mechanism relied on) — this is a documentation-attribution issue for
     Hardware Reviewer/Hardware Lead to reconcile, not a functional gap.
  2. **Item 17 — 2S/3S UVLO finding**: this revision's own added series
     protection diode (D2) creates a voltage-margin issue at 2S that did
     not exist before the diode was added — practical recommendation is
     **3S-only operation**, even though the Component-Engineer-approved
     motor (M1) is validly rated across the full 2S–3S range. Not a part-
     selection flaw; a consequence of this revision's own protection
     addition, flagged for Hardware Reviewer/Hardware Lead to confirm or
     revisit.
  Remaining 9 new items (11–16, 19–21) are lower-severity residual
  research gaps or interpretive judgment calls, itemized in full in §16
  — none are believed to block a paper-design review, all are flagged
  rather than silently assumed.

**On the ECO-008 human directive (FG degradation below ~500–1500 RPM)**:
tracked per the task's request. This revision found a genuine
circuit-adjacent, register-level fact worth recording rather than
treating this as purely a firmware/FMEA item: `FGOLsel[1:0]`
(DS-MTR-062) and `Op2ClsThr[4:0]` (DS-MTR-063) are the specific
DRV10983 configuration registers governing FG behavior during open-loop
operation and the open-to-closed-loop transition threshold, respectively
— both are I2C/EEPROM-configurable, and this design's SCL/SDA wiring
(§7.5.4) exists specifically so they can be tuned post-assembly without
hardware rework. No register value is set by this document (REQ-009
scope fence — wiring the interface, not writing configuration/control
logic); the finding is recorded here as the concrete substantiation ECO-008
asked for, for Firmware Engineer/FMEA attention.

**Constraints confirmed respected this revision**: `bom/component-
selection.md`, `requirements/requirements.md`, `hardware/power-
architecture.md`'s Decision table, `hardware/mechanical-interface.md`,
and everything under `hardware/mechanical/`/`firmware/` were read-only
references, never edited. No control-loop code or logic of any kind was
introduced (REQ-009) — every SPEED/DIR/FG/I2C reference in this document
describes wiring and commissioning-time configuration, not a runtime
control algorithm.

No KiCad project exists to run `extract_schematic_netlist` /
`analyze_schematic_connections` / `validate_project` against (§0) — this
document, including its Rev 3 additions, is the self-check substitute for
this revision too, consistent with Rev 1 and Rev 2.

### 18.2 Rev 4 handoff (this revision — Independent Review Cycle 3 rework)

**This is a loop-back rework/re-review handoff, not a new-subsystem
handoff.** Independent Review Cycle 3 (Hardware Reviewer + rubber-duck,
run in parallel against Rev 3's Motor Driver + Reaction Wheel addition)
raised 5 open HIGH findings (ISS-014, ISS-015, ISS-019, ISS-020,
ISS-021), all against Rev 3's own new content. Per this agent's own
instructions ("When you receive Hardware Reviewer findings"), every one
is addressed explicitly below — none silently dropped. See the Revision
changelog at the top of this document for the complete list of what Rev
4 changed, section by section.

**To**: Hardware Reviewer, via Hardware Lead, for a **fresh re-review**
of the changed areas — per `.github/skills/hardware-review/SKILL.md`'s
re-review guidance, this handoff calls out exactly what changed so the
re-review can focus there, rather than re-running the full 16-item
checklist against unchanged content. Areas touched this revision: Status
line, changelog, §2.1, §7.5.2 [rewritten], §7.5.5 [rewritten], §7.5.8
[closing paragraph rewritten], §7.5.9–§7.5.12 [new], §11, §12, §13, §14
[new Rev 4 motor-domain re-check subsection], §15 [new Re-self-check
after Rev 4 fixes subsection], §16 [items 14/17 annotated in place, items
22–26 appended], §17.

**Disposition of all 5 Cycle 3 HIGH findings** (full reasoning in the
cited sections; summarized here per this agent's own report-back
obligation):

1. **ISS-014 (2S/3S UVLO margin)** — **FIXED** as a documentation/scope
   correction: §7.5.2 now states corner-by-corner numbers and elevates
   3S-only from a soft recommendation to a **binding constraint**;
   `hardware/power-budget.md`'s Rail Margin Summary is reconciled to the
   same conclusion, closing the cross-document inconsistency Cycle 3
   found. **Also flagged** (§16 items 17/22): propagation into `bom/
   component-selection.md`/`requirements/requirements.md` (outside this
   agent's edit scope) and an alternate lower-VF diode/ORing-FET topology
   evaluation, both routed to Hardware Lead/Component Engineer. The 2S/3S
   conclusion itself is **unchanged — 3S-only was already this
   document's practical position** — but is now stated with the
   precision (typical-corner failure, not just worst-case) Cycle 3
   correctly demanded.
2. **ISS-015 (SPEED uncommanded-motion risk)** — **FIXED**: new **R10**
   (1kΩ, real external pulldown, §7.5.5) bounds SPEED's voltage
   regardless of power-up order, superseding the inadequate internal-
   pulldown/Table-11 rationale Cycle 3 correctly rejected (DS-MTR-071
   confirms factory-default active analog mode). **Also flagged**
   (§16 items 14/22): the underlying cross-domain power-up-*order* gap
   is bounded, not eliminated, by a level-clamp alone — full closure
   needs the flagged §7.5.10 supervisory load-switch (architecturally
   significant, routed to Component Engineer via Hardware Lead, not
   selected by this agent) — and REQ-403's own human-review gate is
   independent of and not satisfied by this hardware fix alone.
3. **ISS-019 (unbounded J4 envelope)** — **FIXED**: new **F1** (Littelfuse
   30R500U PTC resettable fuse, DS-PROT-006) in-line ahead of D2/D3, plus
   an explicit, binding 9.0–13.0V source envelope (§7.5.9) replacing the
   previously-unbounded assumption. **Also flagged** (§16 items 22/23):
   F1 bounds fault magnitude/duration, not continuous overvoltage — that
   residual gap is routed to the same flagged §7.5.10 supervisory
   controller, and the new envelope needs recording in `validation/
   bring-up-procedure.md` (not edited by this agent).
4. **ISS-020 (no overspeed/max-speed envelope)** — **FLAGGED, not fixed
   in hardware** (§7.5.11, §16 item 24): M1's no-load speed (≈20,000–
   22,200 RPM, DS-MTR-018) is 6–7× REQ-007's 3000 RPM floor with no
   maximum ever defined. This is judged a firmware/human-safety-review
   decision (a maximum commanded-speed ceiling, ramp-rate limit, and
   overspeed-response policy), not a schematic-level fix — no component
   added, no ceiling unilaterally decided by this agent. Explicitly tied
   to REQ-403's human-review gate; also feeds Mechanical Lead's
   containment design once decided. Routed to Hardware Lead for
   mediation/routing to Firmware Lead and the human safety reviewer.
5. **ISS-021 (no latching, REQ-404 not satisfied)** — **FLAGGED, not
   fixed in hardware** (§7.5.12, §16 item 25): independently confirmed
   this revision that none of U5's three protection mechanisms (OCP,
   Lock Detection, Thermal Shutdown — DS-MTR-058/059/060) latch; all
   auto-recover once the fault condition clears. REQ-404's "Should"-
   priority shutdown-behavior intent is not satisfiable by U5's hardware
   alone. This revision specifies the required firmware behavior (count
   consecutive Lock Detection events, force SPEED safe, require
   deliberate re-arm) as an explicit new firmware requirement, and notes
   the flagged §7.5.10 supervisory switch as a candidate hardware
   enforcement point if firmware-only latching is judged insufficient —
   but does not implement firmware or unilaterally declare this closed.

**Net new firmware requirements this revision** (neither existed before
Cycle 3): (a) an overspeed/maximum-commanded-speed shutdown policy
(ISS-020, §7.5.11); (b) a latched-fault retry-counting policy on Lock
Detection events (ISS-021, §7.5.12). Both are explicitly firmware-side,
consistent with this document's REQ-009 scope fence (wiring/interfaces,
not control logic) — flagged for Firmware Lead, not implemented here.

**Artifacts**:
- This document (`hardware/schematic/bench-imu-01-design.md`), revised
  to Rev 4 — schematic artifact + design rationale log + self-check
  results (§14's new "Rev 4 motor-domain re-check" subsection, §15's new
  "Re-self-check after Rev 4 fixes" subsection), combined.
- `hardware/power-budget.md` — **updated this revision**: Supply
  Capability's VM_MOTOR row gains F1; Subsystem Load gains R10's
  ≈0–3.3mA 3V3-rail addition; Rail Margin Summary's 2S/3S conclusion is
  reconciled to state the identical corner-by-corner result as §7.5.2
  above (the cross-document inconsistency Cycle 3 flagged is closed).
- `datasheets/evidence-log.md` — **+1 new row this revision**
  (**DS-PROT-006**, Littelfuse 30R500U, F1) — verified against no
  duplicate row IDs. **+1 new datasheet metadata file**:
  `datasheets/littelfuse_30r500u_rev-unknown.md` (F1 is a genuinely new
  part this revision, unlike Rev 3's parts which all cited
  already-registered metadata records).
- Open `UNKNOWN`s: §16 above — **2 pre-existing items annotated in place**
  (item 14: RESOLVED IN PART, SPEED level now bounded, ordering gap
  remains open and routed to §7.5.10; item 17: SHARPENED/CORRECTED to the
  precise corner-by-corner 3S-only finding), **5 new items appended**
  (items 22–26: the flagged §7.5.10 supervisory controller; the
  bring-up-procedure.md envelope-recording gap; ISS-020's undecided
  overspeed ceiling; ISS-021's undecided firmware latched-fault policy;
  F1's own estimated, not datasheet-sourced, added series resistance) —
  none renumbered or deleted, per this section's own established
  "annotate/append, don't renumber" convention.

**Constraints confirmed respected this revision**: `bom/component-
selection.md`, `requirements/requirements.md`, `hardware/power-
architecture.md`'s Decision table, `hardware/mechanical-interface.md`,
`validation/open-issues.md`, `validation/design-review.md`, and
everything under `hardware/mechanical/`/`firmware/` were read-only
references, never edited. No new component was selected outside the
"single supporting part, no full comparison" class this document's own
task scope permits: **R10** (a resistor) and **F1** (a fixed-threshold
PTC fuse) are exactly that class, consistent with how D2/D3/J4 were
selected in Rev 3. The one component that would be architecturally
significant — the §7.5.10 supervisory load-switch/OVP/latch controller
serving ISS-015/019/021's residual hardware-enforcement gaps — is
deliberately **not** selected here; only its required function and
ratings are specified, and its actual sourcing is routed to Component
Engineer via Hardware Lead, per this agent's own "Out of scope"
constraint against unilaterally selecting architecturally significant
parts.

**On mediation**: ISS-020 and ISS-021 are flagged, not hardware-fixed,
because I judge them to be firmware/human-safety-review decisions rather
than schematic-level gaps — this is my own engineering judgment, backed
by the cited evidence (DS-MTR-018 no-load speed figures; DS-MTR-058/059/
060 non-latching behavior), not an assertion. Per my own agent
instructions, I am not unilaterally dismissing either finding — both are
routed to the Hardware Lead for mediation if the Hardware Reviewer
disagrees with treating them as flag-only rather than requiring a
hardware interlock.

No KiCad project exists to run `extract_schematic_netlist` /
`analyze_schematic_connections` / `validate_project` against (§0) — this
document, including its Rev 4 additions, is the self-check substitute for
this revision too, consistent with Rev 1, Rev 2, and Rev 3.

### 18.3 Rev 5 handoff (this revision — U6 supervisory controller implementation, Cycle 4 rework)

Per this cycle's loop-back task: implement the now-human-approved U6 =
TPS26631PWPR (`bom/component-selection.md` "Motor-Rail Supervisory
Controller" §Approval), and swap F1's obsolete MPN. Both completed —

1. **ISS-015 (cross-domain power-up ordering, SPEED risk)** — **hardware
   enforcement point now added.** U6's default-OFF/fail-safe load-switch
   (R11=10kΩ pull-down dominating SHDN's internal pull-up, §7.5.10) means
   U5's VCC is only energized once firmware deliberately drives PA9 high
   — closing the gap R10 alone (Rev 4) could not: R10 only bounded
   SPEED's *voltage* if U5 was already powered, it never gated *whether*
   U5 was powered relative to MCU boot order.
2. **ISS-019 (unbounded VM_MOTOR envelope) — residual continuous-OVP/
   UVLO gap now closed.** F1 (Rev 4) bounded only fault-current
   magnitude/duration; U6's own continuous OVP/UVLO comparator, referenced
   to the identical 9.0–13.0V envelope via R12/R13/R14 (real TI Eq9/Eq10
   divider design, not an approximation), now also enforces the envelope
   continuously, independent of any fault event.
3. **ISS-021 (no latching, REQ-404 not satisfied) — still FLAGGED, not
   fixed in hardware, exactly as this revision's own task instruction
   required.** U6 gives firmware a physical actuation point (PA9/SHDN)
   for an eventual latched cutoff, and MODE=Open gives U6 its own
   independent overload-latch behavior as a bonus — but the actual
   retry-counting/rolling-window/re-arm *policy* is not decided, invented,
   or defaulted by this revision. §16 item 25 is updated to reflect U6's
   availability as the enforcement point, not to declare the policy gap
   closed.
4. **ISS-020 (undecided overspeed ceiling)** — **untouched, as required.**
   No circuit trick was applied; this remains entirely a firmware/human-
   safety-review decision (§16 item 24, unchanged in substance).
5. **F1 obsolescence** — **resolved.** Littelfuse 30R500U → 30R500UF,
   independently confirmed this session (web search) to be the same
   datasheet/electrical/mechanical part (Ihold=5A/Itrip=10A/Vmax=30Vdc/
   Imax=40A/package/footprint identical), differing only in RoHS3-
   compliant construction, and Active/orderable status — 30R500U's own
   manufacturer-recommended direct replacement (§7.5.9, DS-PROT-033).

**Artifacts**:
- This document (`hardware/schematic/bench-imu-01-design.md`), revised
  to Rev 5 — schematic artifact + design rationale log + self-check
  results (§14's new "Rev 5 motor-domain re-check" subsection, §15's new
  "Re-self-check after Rev 5 fixes" subsection — a full, explicit pass of
  all 16 items against U6 specifically, per this cycle's own task
  instruction), combined.
- `hardware/power-budget.md` — **updated this revision**: Supply
  Capability's VM_MOTOR row's F1 MPN corrected to 30R500UF; Subsystem
  Load gains U6's IQ/divider-bias-current (VM_MOTOR) and R11's ≈330µA
  (3V3, mirroring R10's own precedent); a new U6 thermal cross-check
  added alongside the existing U5/LDO ones; Rail Margin Summary
  reconciled to note U6's now-continuous OVP/UVLO enforcement.
- `datasheets/evidence-log.md` — **new rows this revision**: DS-PROT-023
  through DS-PROT-033 inclusive (U6 pinout/PowerPAD, SHDN thresholds/
  leakage/design-rule, SHDN pull-up figure + "not a guaranteed spec"
  finding, UVLO/OVP electrical characteristics + Eq9/10 + 20×-leakage
  design rule, R(ILIM) Eq8, dVdT/inrush Eq1–2 + Fig 8-3's C(OUT)=1mF
  citation + PGTH timing, C(IN) triple-citation, MODE/PGOOD/FLT/IMON/AMR/
  ROC tables, thermal RθJA/R(ON)/T(TSD)/IQ, F1's 30R500UF Active/RoHS3/
  manufacturer-recommended-replacement swap rationale, and F1's
  30R500U/30R500UF electrical-and-mechanical identity confirmation) —
  verified against no duplicate row IDs.
- `datasheets/texasinstruments_tps26631pwpr_unknown-rev.md` — **"Known
  gaps" section updated in place** this revision to record which gaps
  this session's own research closed (SHDN pull-up figure now traced to
  an illustrative-only diagram, not a missing spec; C(OUT) ambiguity
  resolved as two distinct, unrelated TI citations) versus which remain
  open.
- `datasheets/littelfuse_30r500u_rev-unknown.md` → **renamed** to
  `datasheets/littelfuse_30r500uf_rev-unknown.md` this revision (`git
  mv`, preserving file history), content updated in place to record the
  MPN swap, RoHS3/Active-status confirmation, and the same Evidence IDs
  this file already served plus DS-PROT-033.
- Open `UNKNOWN`s: §16 above — **1 pre-existing item resolved in place**
  (item 22: the flagged supervisory controller is now U6, selected,
  approved, and implemented — historical original text preserved
  inline, not deleted), **1 pre-existing item's cross-reference updated
  for accuracy without changing its substance** (item 25: notes U6 is now
  the specified/selected enforcement point, but the firmware policy
  itself remains exactly as undecided as before), **2 pre-existing items
  confirmed unaffected** (items 24/26, explicitly noted as such), **4 new
  items appended** (items 27–29 plus this list itself: the SHDN pull-up
  resistance discrepancy; the OVP full-stack-worst-case margin nuance;
  the dVdT/C(OUT) sizing-basis distinction) — none renumbered or deleted,
  per this section's own established "annotate/append, don't renumber"
  convention.

**Constraints confirmed respected this revision**: `bom/component-
selection.md`, `requirements/requirements.md`, `hardware/power-
architecture.md`'s Decision table, `hardware/mechanical-interface.md`,
`validation/open-issues.md`, `validation/design-review.md`, and
everything under `hardware/mechanical/`/`firmware/` were read-only
references, never edited. **No new component was selected outside this
revision's own task scope**: U6's MPN was fixed by the task instruction
itself (already Component-Engineer-proposed and human-approved before
this session began) — this agent's own role this revision was
implementation (divider/pull-down/R(ILIM)/dVdT sizing, pin allocation,
net-list/parts-list integration), not part selection; F1's replacement
MPN (30R500UF) is the same manufacturer's own direct-replacement part for
an already-approved part, not a new part-selection decision, consistent
with how this agent's "Out of scope" constraint is scoped to
*architecturally significant* new selections.

**On the SHDN pull-up discrepancy (§16 item 27)**: this is disclosed, not
silently resolved in favor of either the task/human's ≈440kΩ figure or
this agent's own 1MΩ datasheet-diagram read, because neither is a
guaranteed Electrical Characteristics spec — R11's own sizing rests on a
different, guaranteed spec (10µA leakage) that is robust regardless of
which pull-up figure is correct. Flagged for Hardware Reviewer/Component
Engineer awareness, not as a blocking defect.

No KiCad project exists to run `extract_schematic_netlist` /
`analyze_schematic_connections` / `validate_project` against (§0) — this
document, including its Rev 5 additions, is the self-check substitute for
this revision too, consistent with Rev 1 through Rev 4.

## 19. Handoff — ISS-027 pin correction (2026-08-31, post-Design-Complete)

**This is a post-Design-Complete correction, not part of the original Rev
2 rework cycle §18 describes above (left unmodified as accurate history).**
Rev 2 reached Design Complete 2026-09-03 (`validation/change-log.md`
ECO-005) under the review rigor available at that time — Markdown-only,
no real KiCad project existed yet. This repository's first real KiCad
project for this design (`hardware/schematic/bench-imu-01/`) then
independently surfaced ISS-027 (§2.3/§4.1/§11/§12, and the "Rev 2,
corrected" changelog entry at the top of this document) — a genuine
physical-pin-bonding defect that no Markdown-only review, however careful,
could have caught, because it requires cross-checking the MCU's real
package pinout table against the design, not just the alternate-function
table.

**To**: Hardware Reviewer, via Hardware Lead, for a **fidelity-scoped
independent review** — not a full Design Complete re-litigation. The
Reviewer should confirm this document's corrected pin claims (§2.3, §4.1,
§11, §12) actually match the real KiCad project built from it (using the
KiCad tools directly, not re-reading this document's own claims), and
independently classify ISS-027's severity per `docs/architecture.md` §7.1.
Areas needing re-review: §0, §2.3, §4.1, §4.3, §5.2, §5.3, §6, §11, §12,
§13, §14 item 10/13, §15 (unchanged — this correction was not
self-checked against the Hardware Reviewer's 16-item checklist as a fresh
pass; that is deliberately left to the delegated Reviewer instead, given
the narrow, well-understood nature of this specific fix), §16 items 1, 3,
4, 30. (This document's own Motor Driver + Reaction Wheel subsystem, §18.1
through §18.3 above, is unrelated to this correction and was already
independently reviewed on its own track — see the Revision changelog.)

**What did *not* change**: no requirement, no component selection, no
electrical topology/rail/decoupling/protection decision, no already-settled
voltage/thermal/timing margin from the original Rev 2 cycle. This is a
pin-*identity* correction only — same physical bus topology (a
pulled-up, 2-wire I2C link from the MCU to the IMU), same peripheral
instance (I2C2), same pull-up values, same power/thermal numbers
(`hardware/power-budget.md` remains unchanged).

**Artifacts**:
- This document, corrected (see the "Rev 2, corrected" changelog entry).
- `hardware/schematic/bench-imu-01/` — the new real KiCad project, built
  on these corrected pins, independently tool-verified.
- `datasheets/evidence-log.md` — DS-MCU-064 through DS-MCU-067 added.
- `datasheets/stmicroelectronics_stm32_open_pin_data_stm32g031k4-6-8tx.md`
  — new datasheet metadata record (ST's own official pin-database source).
- `validation/open-issues.md` — ISS-027 (this finding).
- `validation/change-log.md` — ECO-006.

**Flagged, not fixed here**: `firmware/bench-imu-01/` (Phase 2, PR #7,
already merged) initializes GPIOB pins 10/11 for I2C2 (DS-MCU-062) — this
firmware will need a follow-up fix (GPIOA pins 11/12 instead) once this
correction is reviewed and accepted. Firmware Bring-up does not gate the
Design Complete process (`docs/architecture.md` §14/`docs/workflow.md`
Phase 11), so this is explicitly out of scope for this correction, not an
oversight.
