# Bench-IMU-01 — Enclosure Dimensional Spec & Design Rationale

**Status: Rev. 3.4 — recomputes §8.1's own Method 1/Method 2 wall-impact and
fastener pull-out analysis (Charpy/fracture-toughness, yield-strength
plastic-work, confidence ledger, escalation flag) plus §15 item 6's
cross-reference against the Rev 3.3-corrected credible-worst-case energy
figures (≈156.44J/≈79.11 m/s point estimate; range ≈154.95–157.69J/
≈78.73–79.42 m/s); NO `.scad` geometry changed this revision — this is the
final piece of the premise-correction chain flagged by Rev 3.3's own
MISS-016 staleness note, closing out `validation/open-issues.md` MISS-016's
"actual recompute explicitly deferred" item (the open-issues.md entry itself
is intentionally left for the Hardware Lead to update, not edited by this
revision).** Rev 3.3 (previous revision) recomputed §8's own REQ-403 physics
table against a corrected credible-worst-case motor RPM input but explicitly
deferred §8.1's own recompute to a follow-up. Rev 3.2 before that added a
bounded MISS-011 estimate attempt (§8.1). Rev 3.1 before that fixed Independent
Mechanical Review Cycle 3's 1 CRITICAL (MISS-008) and 2 HIGH (MISS-009,
MISS-010) findings, in both the `.scad` file and this document. MISS-011
(MEDIUM, non-gating) was carried forward in Rev 3.1 **disclosed, not
fixed**, then addressed by Rev 3.2's own §8.1 analysis (proposed RESOLVED,
pending Independent Review). Rev 3.2 itself was a Mechanical-Lead-authored
**analysis-only** addition attempting MISS-011's Recommended Fix path (a): a
bounded, order-of-magnitude wall-impact/penetration and fastener pull-out
estimate against the disclosed REQ-403 hazard figure (§8.1) — not a `.scad`
change, and explicitly **not** a self-certified closure of MISS-011
(proposed only, pending independent Mechanical Reviewer cross-check — this
Mechanical Lead is not independent of its own estimate). This document still
does not declare itself reviewed/complete — see
`.github/agents/mechanical-lead.agent.md`, "Out of scope" — a fresh
Independent Mechanical Review pass on this revision (now including the
Rev 3.4-recomputed §8.1) is
the required next step; after that clears, the REQ-403 disposition proposal
in §8 goes to the human as a HITL gate. Nothing in this file should be read
as "approved."

**Rev. 4 status note (new, additive layer on top of the Rev 3.4 baseline
above — nothing above this note is edited)**: Rev 3 (through Rev 3.4) covers
a rigid, bench-fixed enclosure that reached Design Complete. The roadmap's
next stage, "1-axis attitude control" (`docs/architecture.md` §11), requires
the whole Rev 3 assembly to rotate freely about a vertical axis, using a
human-approved BC Precision 4LS-3 lazy-susan turntable ball bearing
(`bom/component-selection.md`, "Free-Rotation Support Mechanism," Candidate
A). This Rev 4 layer adds a new mounting flange, a new 4th printed piece (a
fixed stand plate), and the supporting CG/tip-over analysis and
manufacturability findings — entirely as **new** material, in a new
`## 18. Rev 4` section below (after §17) and a new changelog block
immediately below this note. **Every existing section (§0–§17) and the
entire Status paragraph above are unchanged, byte-for-byte, by this
addition** — a deliberate, disclosed departure from this file's own
established Rev 3.1–3.4 convention of rewriting the single top-of-file
Status paragraph each revision; the stricter, zero-deletion approach was
chosen here instead specifically because this task's own governing
instruction (REQ-311; `.github/agents/mechanical-lead.agent.md`) requires
Rev 3's existing content to remain provably, byte-for-byte unmodified
(verified via `git diff` showing zero deletions to this file this
revision). As with every prior revision, this document does not declare
itself reviewed/complete — a fresh Independent Mechanical Review pass,
this time covering the new §18 content specifically, is the required next
step.

**Rev. 4 changelog (this revision, Mechanical Lead; new `.scad` geometry —
see that file's own Rev 4 block for the full variable-level detail):**

- **Added `hardware/mechanical-interface.md` Part C** (bearing physical
  facts, new flange/stand-plate design facts, CG/tip-over analysis,
  fastener justification, tether-routing confirmation, assembly-order
  addendum) — see that file for the interface-level summary of everything
  below.
- **Added a new mounting flange** beneath the existing floor
  (`bmount_flange()`), spanning `bmount_flange_or`=52.5mm (reusing
  `fw_flange_or`) down to `bmount_flange_ir`=28.0mm, `bmount_flange_t`=6.0mm
  thick, with 4× ASSUMPTION-pattern pilot holes on a 40.0mm bolt circle —
  see §18.2.
- **Added a new 4th printed piece**, a fixed stand plate (`stand_plate()`),
  sized via a from-scratch CG/tip-over analysis (not the bearing's own
  generic 12–25in "suggested top diameter"): `stand_plate_or` = 60.0mm
  (120mm diameter), chosen from a radius sweep for a ≈6.2× static margin —
  see §18.3.
- **Performed and disclosed a full CG/tip-over analysis** (§18.3): Rev 3's
  own analytic plastic mass (≈207.9g) is found materially higher than
  `bom/component-selection.md`'s own bounding-shell estimate (130–170g) for
  the same enclosure — disclosed as a real, hand-verified discrepancy, not
  silently reconciled. Total system mass (rotating assembly + bearing +
  stand plate) computed at ≈601.8g, roughly double the human's own working
  ≈280–320g estimate — attributed to the plastic-mass finding and the new
  parts, not a computation error.
- **Found and disclosed a genuine manufacturability caveat**: the fused
  base+flange print has a ~56mm-diameter hidden internal overhang requiring
  slicer-generated internal support material — not a clean pass; see
  §18.4/§18.5 for the full analysis and 3 rejected alternatives.
- **Confirmed REQ-113's tether routing** needs no new cutout — the
  bearing's own center hole plus the new flange/stand-plate bores are
  coaxial and unobstructed by the new mounting geometry (§18.6).
- **Registered Evidence ID DS-BRG-007** (generic lazy-susan mounting-hole
  convention, `datasheets/evidence-log.md`), used as the ASSUMPTION basis
  for the new flange's bolt pattern (this SKU's own pattern is not
  published — see §18.1/§18.2).
- **Self-checked against the Mechanical Reviewer's 10-item checklist**
  (§18.7) — recorded with explicit PASS/caveat framing per item, **not** a
  self-declared "reviewed" or "approved" status; an independent Mechanical
  Reviewer pass is still required next.
- **Not logged as an ECO** in `validation/change-log.md`, and
  `requirements/traceability-matrix.md` is not updated — both are the
  Hardware Lead's responsibility after this handoff, per this Mechanical
  Lead's own explicit task scope this cycle; flagged here, not silently
  skipped.
- **Out of this revision's edit scope, unchanged:** `hardware/schematic/**`,
  `firmware/**`, all of Rev 3's own existing `.scad` modules/dimensions
  (`base()`, `pcb_lid()`, `containment_cap()`, and every variable defined
  before the new Rev 4 block), §0–§17 of this file, and Parts A/B of
  `hardware/mechanical-interface.md`.

**Rev. 3.4 changelog (this revision, Mechanical Lead, analysis-only — no
`.scad` change; closes the numeric-recompute portion of MISS-016,
`validation/open-issues.md`):**

- **Recomputed §8.1.1's sanity-check re-derivation** to use the Rev
  3.3-corrected v_rim≈79.11 m/s (was 69.74 m/s), reproducing §8's own
  156.44J/4.5×10⁻⁵ kg·m² table figures (was 121.60J) to rounding — I
  (moment of inertia) and mass/radius are unchanged, only the RPM-derived
  rim speed and resulting energy actually moved, as expected.
- **Recomputed §8.1.2's Method 1 (Charpy/fracture-toughness) table**: same
  material Charpy figures (2.4–12 kJ/m², unchanged — material properties
  don't change), same 4.5/15/30/60mm engagement-length sweep, against the
  new 156.44J denominator. New "% of budget" column: 0.028%–0.14% (4.5mm),
  0.092%–0.46% (15mm), 0.18%–0.92% (30mm), 0.37%–1.84% (60mm) — every figure
  moved down from the Rev-3.2/3.3 values (0.036%–0.18%/0.12%–0.59%/
  0.24%–1.18%/0.47%–2.37%), because the same fixed absorption is now a
  smaller share of a larger budget. Reverse cross-check (engagement length
  to consume the entire budget): now 3,259–16,296mm (1,313%–6,566% of the
  248.19mm wall circumference), up from 2,533–12,667mm (1,021%–5,104%).
- **Recomputed §8.1.2's Method 2 (yield-strength-limited plastic work)
  table**: same yield figures (37.9–50 MPa, unchanged), same sweep, against
  the new 156.44J denominator and 79.11 m/s rim speed where referenced. New
  "% of budget" column: 1.7%–2.3% (4.5mm), 5.8%–7.7% (15mm), 11.6%–15.3%
  (30mm), **23.3%–30.7%** (60mm) — down from 2.2%–3.0%/7.5%–9.9%/
  15.0%–19.7%/**29.9%–39.5%**. Reverse cross-check: now 196–258mm
  (79%–104% of the wall circumference — the upper bound now *exceeds* 100%,
  a new qualitative fact not present at the superseded energy figure), up
  from 152–201mm (61%–81%).
- **Updated the "Verdict — wall" prose**: "well under half" still holds
  numerically (if anything more so — 23.3%–30.7% vs. the old 29.9%–39.5%),
  but the best-case shortfall multiple widened from the previously-stated
  "~2.5–3×" to a precisely recomputed **≈3.26×–4.30×**, and the
  typical/localized shortfall widened from "one to somewhat over three
  orders of magnitude" (≈42×–2,778×) to **≈54×–3,621× (≈1.7 to ≈3.6
  orders of magnitude)**. The shortfall widened at every
  engagement length and by both methods — it did not narrow anywhere, as
  MISS-016 itself predicted.
- **Updated the "Real-world intuition comparable" baseball paragraph**: the
  116.0J baseball-pitch comparable was "within 5%" of the old 121.60J
  budget (≈95.4%); against the corrected 156.44J budget it is now only
  ≈74.15% of the budget — the credible-worst-case event is now
  appreciably more energetic than a hard-thrown pitch (≈1.35× one), not a
  near-match to one.
- **Recomputed §8.1.3's fastener pull-out section**: the "deliberately
  pessimistic hypothetical" now applies the full 156.44J (was 121.60J)
  directly to the cap joint; the force-vs-stopping-distance table's
  required-force values and break-even distances were recomputed
  accordingly (e.g. the 6,000N-ideal break-even grew from ≈20.3mm to
  ≈26.1mm). **New qualitative finding**: at the 50mm stopping distance, the
  3,000N-reduced-sharing scenario flips from within capacity (≈0.81×) to
  marginally over capacity (≈1.04×) — the 6,000N-ideal scenario remains
  within capacity at 50mm (≈0.52×, was ≈0.41×).
- **Updated §8.1.4's confidence ledger**: the disk-parameter row and the
  overall-wall-verdict row now cite the Rev 3.4 figures; every other row
  (wall geometry, insert dimensions, Charpy/tensile figures as published,
  load-sharing assumptions, etc.) is unchanged, since none of those
  underlying facts moved.
- **Updated §8.1.6's escalation flag** to cite the same recomputed shortfall
  multiples (≈3.26×–4.30× best case; ≈1.7–3.6 orders of magnitude typical).
- **Updated §15 item 6's "Rev 3.2 note" and its "Rev 3.2 addendum"
  cross-reference** to the same recomputed figures, completing the
  cross-reference Rev 3.3 explicitly deferred ("§15 item 6's existing 'Rev
  3.2 note' and §8.1 itself still quote the superseded 121.60J/69.74 m/s
  figures — both are necessarily part of the same follow-up recompute...
  not edited separately here to avoid partially updating §8.1-dependent
  content piecemeal" — Rev 3.3 changelog, above).
- **No confidence-marking TYPE was changed** — every `CONFIRMED`/
  `ASSUMPTION`/`ESTIMATE`/`DERIVED`/`UNKNOWN` label in §8.1 and §15 item 6
  is exactly as it was before this revision; only the numeric values inside
  cells that already carried those markings were recomputed.
- **No `.scad` geometry was changed** and no new design decision was made —
  this revision is a pure numeric recompute of an existing estimate against
  an already-corrected input, per this task's explicit scope. The
  wall-thickness/topology question remains a separate, already-flagged
  decision for the Hardware Lead/human at the REQ-403 gate (§8.1.6).
- **Not logged as a new ECO** in `validation/change-log.md`: no `.scad`
  design change occurs in this revision (analysis-only numeric recompute of
  an existing estimate), so per this Mechanical Lead's own standing
  instruction to log an ECO "if the design actually changes," no entry was
  added — noting this as a judgment call the Hardware Lead may wish to
  override, since Rev 3.2/3.3 (also analysis-only) were logged as ECO-021/
  ECO-023 respectively.
- `validation/open-issues.md` is explicitly **not** touched by this revision
  (per this task's own scope) — the recomputed figures above are reported
  back for the Hardware Lead to fold into MISS-016's own row.
- **Out of this revision's edit scope, unchanged:** `bench-imu-01-manufacturing-
  spec.md` (already fixed separately for MISS-021), all `.scad` files,
  `hardware/schematic/`, `firmware/`, `bom/`, `requirements/`.

**Rev. 3.3 changelog (this revision, Mechanical Lead, analysis-only — no
`.scad` change; consumes Circuit Engineer's DS-MTR-018 correction,
`hardware/schematic/bench-imu-01-design.md` §7.5.13):**

- **Independently re-verified** Circuit Engineer's DS-MTR-018
  voltage-label correction and its derived corrected credible-worst-case
  motor no-load speed (RPM≈25,060–25,280, point ≈25,180 — supersedes the
  old, correctly-arithmetic-but-mislabeled 22,200 RPM figure) before using
  it: re-read DS-MTR-017/018/079/080 and DS-PROT-005/006/031/033/034
  directly in `datasheets/evidence-log.md`, hand-reproduced the KV×V_VCC
  and F1/U6/D2 voltage-drop arithmetic, and independently reconfirmed the
  11.1V-nominal-vs-12.6V-full-charge LiPo convention from a fourth, separate
  source. **Verdict: agree**, with one immaterial (~20 RPM, ~0.08%)
  arithmetic wrinkle noted in §8 that changes no conclusion.
- **Recomputed §8's physics table** (angular velocity, stored kinetic
  energy, rim tip speed, peak centrifugal stress) at the corrected RPM,
  from this Mechanical Lead's own rotor inertia/radius data (I=4.5×10⁻⁵
  kg·m², r=0.030m, §4.1/§4.4, unchanged) — independently derived, not a
  reuse of Circuit Engineer's own illustrative scaling (which the result
  closely matches). New point-estimate figures: ω≈2636.8 rad/s, KE≈156.44 J
  (≈70.4× the 3000 RPM baseline, was 54.76×), rim tip speed≈79.11 m/s
  (~285 km/h, was ~250 km/h), peak stress≈20.20 MPa. The full range
  (25,060–25,280 RPM) is disclosed alongside the point estimate, not just
  the point estimate alone.
- **Re-checked the disk-burst safety factor**: yield(250 MPa)/peak-stress
  is now ≈12.3–12.5× (point ≈12.4×), down from the superseded ~15.9× (as
  expected, since stress rose with the corrected RPM) but still comfortably
  non-binding — disk-burst was never, and is still not, the governing
  failure mode; the discrete hub-collar-release/projectile hazard remains
  the actual reasoning behind the containment proposal.
- **Updated REQ-403 safety-disposition prose** throughout §8 (the
  "~20,000–22,200 RPM class"/"~250 km/h" framing, the "~122 J dropped from
  ~12.4m" illustrative comparison, and the now-false "44–55× matches
  ISS-020" cross-check) to the corrected figures.
- **Added an explicit MISS-016 staleness flag** at the end of §8: MISS-016
  (HIGH, OPEN, `validation/open-issues.md`) cites §8.1's own Method 1/Method
  2 wall-impact-energy estimates, both computed against the now-superseded
  121.60J figure — those estimates are now stale and **can only widen, not
  narrow**, once recomputed against the corrected ≈154.95–157.69J figure.
  **§8.1 itself is NOT recomputed this revision** (separate, already-flagged
  scope, per this task's own explicit instruction) — flagged as required
  follow-up work only.
- **No `.scad` geometry was changed.** This revision corrects the *load
  case* the existing geometry is judged against, not the geometry itself —
  the wall-thickness/topology question raised by MISS-016 remains a
  separate, already-flagged decision for the human at the REQ-403 gate.
- Logged as `ECO-023` in `validation/change-log.md`, with a corresponding
  `validation/change-impact-matrix.md` entry. `validation/open-issues.md`
  is explicitly **not** touched by this revision (per this task's own
  scope) — the MISS-016 staleness connection is recorded only in §8's own
  text above, per this task's explicit instruction not to silently leave it
  unstated.
- **Observations flagged, not fixed (out of this revision's edit scope):**
  (1) `hardware/schematic/bench-imu-01-design.md` §7.5.11's own "roughly
  45–55×" ISS-020 framing is now stale for the same reason as the sentence
  fixed in §8 below, but that document is outside this Mechanical Lead's
  edit scope. (2) §15 item 6's existing "Rev 3.2 note" and §8.1 itself
  still quote the superseded 121.60J/69.74 m/s figures — both are
  necessarily part of the same follow-up recompute called out in the new
  MISS-016 flag in §8, not edited separately here to avoid partially
  updating §8.1-dependent content piecemeal.

**Rev. 3.2 changelog (this revision, Mechanical Lead, analysis-only — no
`.scad` change; `validation/open-issues.md` MISS-011):**

- Added **§8.1** ("MISS-011 closure attempt"): a bounded, order-of-magnitude
  engineering estimate for (1) whether the 4.0mm `containment_wall_t` is in
  a plausible/implausible range for absorbing the disclosed 121.60J impact
  locally, via two independent hand-calc methods across a sensitivity range
  of engagement-width assumptions, and (2) whether the 6×M3 heat-set-insert
  fastener capacity is adequate against a reasoned range of loading
  scenarios for `containment_cap()`. Every number is confidence-marked
  (CONFIRMED/ASSUMPTION/ESTIMATE/UNKNOWN) per
  `.github/instructions/mechanical-design.instructions.md`. 6 new Evidence
  IDs registered (`DS-FAST-001`..`DS-FAST-003`, `DS-MTL-001`..`DS-MTL-003`)
  in `datasheets/evidence-log.md` for the real, independently-checkable
  third-party sources used (manufacturer filament TDS data, an independent
  physical fastener pull-out test, a real commercial insert part number).
- **No `.scad` geometry was changed.** `containment_wall_t` remains 4.0mm,
  `n_cap_bolts` remains 6 — this Mechanical Lead does not unilaterally
  redesign geometry on the strength of its own estimate. §8.1 ends with a
  clearly-labeled "Escalation flag for Hardware Lead" callout — a distinct,
  separately-routed concern this estimate surfaced, not a MISS-011 closure
  claim.
- §12 and §16 updated with minimal cross-references to §8.1 (their own
  existing content otherwise unchanged). §15's Rev 3.1 self-check items 5
  and 6 (fastener placement, wall thickness) each got a short "Rev 3.2 note"
  pointing to §8.1's margin finding, plus a short addendum after the
  section's closing paragraph — the pre-existing Rev 3.1 self-check content
  itself is otherwise unchanged.
- `validation/open-issues.md` MISS-011's Notes column updated to describe
  this attempt and its result; **Status intentionally left OPEN, not
  self-resolved** — proposed only as ready for Mechanical Reviewer's
  independent cross-check, exactly as the Circuit Engineer never self-closes
  a Hardware Reviewer finding (`docs/workflow.md` §3).

**Rev. 3.1 changelog (this revision vs. Cycle 3), each finding fixed in both
the `.scad` file and this spec document — `validation/design-review.md`
"Mechanical Reviewer — Cycle 3 (Independent Review of Rev 3 Motor Driver +
Reaction Wheel Enclosure Redesign, 2026-09-11)", `validation/open-issues.md`
MISS-008..011:**

- **MISS-008 (CRITICAL)** — `fw_disk_bottom`'s own formula omitted
  `fw_hub_collar_h`(6.0mm), even though `fw_shaft_exposed_len_needed`
  elsewhere in the same file already treated the collar height as additive —
  a genuine ~145mm³ manifold overlap between the hub collar and the disk
  (confirmed by the Reviewer via a rendered `intersection()`, and
  independently reproduced by this Mechanical Lead as ~150mm³ before the
  fix), meaning the flywheel could not physically be assembled per this
  design's own Step 5 ("slide disk onto hub collar," §14). Fixed:
  `fw_disk_bottom` = `fw_motor_bell_top` + `fw_hub_standoff` +
  `fw_hub_collar_h` (was missing the last term). This is **not a one-line
  fix in effect** — it cascades a uniform +6.0mm through the entire
  downstream Z-stack: `fw_disk_bottom` 31.5→37.5mm, `fw_disk_top`
  36.0→42.0mm, `fw_clearance_top` 39.0→45.0mm, `fw_cap_outer_top`/
  `fw_bay_total_height` 43.0→49.0mm, and — a further second-order cascade
  found and verified while re-deriving this document, not called out by the
  Reviewer's own finding text — the flange band's and containment cap's
  skirt's own Z-ranges (§11.F) shift identically, from [31.0,39.0]mm to
  [37.0,45.0]mm. Re-verified empty (zero-volume) via `intersection()` after
  the fix. See §3, §4.4, §7, §8, §11.G, §14.
- **MISS-009 (HIGH)** — `base()` was a flat `union()`; the wire-duct void for
  MC-1's phase-wire routing was subtracted only inside
  `motor_wire_bridge()`'s own local `cube()`, never globally — the Reviewer
  confirmed via a rendered `base()` + point-containment sweep that the duct
  path was solid plastic at two independent locations (the containment-wall
  annulus and the PCB-bay south wall), defeating the documented wire route
  and Assembly Step 4. Fixed: `motor_wire_bridge()` split into
  `motor_wire_bridge_solid()` (geometry only) and a standalone
  `motor_wire_duct_void()`, with `base()` restructured into
  `difference(){ union(){...} motor_wire_duct_void(); }` so the void is
  subtracted once, globally, from the whole assembly. A second, independent
  1.0mm shortfall in the void's own near-end anchor (found by this
  Mechanical Lead while implementing the fix, distinct from the Reviewer's
  literal finding) was also corrected (`wire_duct_y_lo` 93.0→91.0mm) — without
  it, the scope-fix alone would still have left a thin un-breached membrane
  at the duct's mouth. Re-verified via a 7-point containment sweep (open at
  the duct centerline/PCB-bay wall/former-shortfall point; solid at
  off-axis controls). See §11.G.
- **MISS-010 (HIGH)** — a pre-existing Rev 2 base-tab/lid-skirt interference
  (190.06mm³, §11.C) that this Mechanical Lead had previously flagged but
  deliberately not fixed as out-of-scope was independently re-confirmed
  present by the Reviewer, who judged it in-scope this cycle since the
  geometry was already being reworked. Fixed: a new `tab_relief_margin`
  (1.0mm) variable and a relief-notch cut into `lid_shell()`'s skirt band at
  each of the 4 `tab_positions`, sized to clear `base_tab()`'s outward
  projection with margin, capped in Z at exactly `lid_lip_h` so the roof
  above each tab is untouched. Re-verified via `intersection()` (volume
  0.0mm³, only a benign flush-face artifact at the tab-top/lid-underside
  mating plane remains) and an 8-point containment sweep (solid tab
  material, void notch, at all 4 corners) plus negative controls confirming
  the skirt is still intact mid-span and the roof is still intact above
  each tab. See §11.C (updated), §11.G.
- **MISS-011 (MEDIUM, non-gating)** — REQ-403's 4mm containment-wall
  thickness and 6× M3 cap fasteners are a qualitative engineering judgment,
  not backed by an impact-energy or fastener pull-out/shear calculation.
  **Not fixed this revision** — carried forward explicitly as a disclosed
  limitation (§8, §12, §16); this was never a gating finding and this
  revision does not attempt the calculation it would require.
- Every fix above was verified empirically this session using real,
  locally-available tooling (`openscad`, `trimesh`, `numpy` — §0) — rendered
  geometry, boolean `intersection()` tests, and point-containment sweeps —
  not hand arithmetic alone, mirroring the Reviewer's own methodology. Final
  full-assembly render after all 3 fixes together: Status NoError, Genus 8,
  4618 vertices, 9264 facets (§0).
- **Not addressed in this revision, on purpose:** the topology argument
  behind the REQ-403 containment proposal (§8) — continuous wall, no
  rotation-plane opening, bolted cap — was independently confirmed **TRUE**
  by the Reviewer and is unchanged by this rework; only the containment
  envelope's own *numbers* needed correcting (MISS-008), and that
  re-derivation is now complete (§8, §11.G).

**Changelog vs. Rev 2** (Rev 2 was Design-Complete; this is a full redesign,
not a patch — the flywheel's rotation-clearance envelope alone, ⌀76mm,
already exceeds the entire Rev 2 board width of 40mm, so no Rev 2 coordinate
could simply be extended):

- Board grew from 60×40mm (Rev 2) to 100×50mm (Rev 3) to host the new Motor
  Driver + Reaction Wheel subsystem (`hardware/mechanical-interface.md` A2).
  All new geometry is re-derived from the Rev 3 interface file; no Rev 2
  coordinate is reused unchanged except where the underlying board region
  (the original 0–60mm "sensor zone") itself did not move.
- Piece count: **2 → 3.** Rev 2 was Base + Lid. Rev 3 is **Base + PCB Lid +
  Containment Cap** — a third piece added specifically to give the flywheel
  bay a dedicated, removable, physically containing top (see §5 item 10 and
  §8 for why REQ-309's 2-piece baseline was not treated as a ceiling).
- New: a second enclosure bay (the "flywheel bay") housing the motor,
  flywheel, and a rotation-clearance keep-out volume, joined to the existing
  PCB bay by a wire-passage duct. This bay did not exist in Rev 2 at all.
- New: off-board/bracket-mounted motor (§6) — the motor is **not** a
  PCB-footprint part; it mounts to a raised platform molded into the base,
  not to the board.
- New connectors/holes relative to Rev 2: J4 (barrel jack, motor supply),
  MC-1 (motor phase-wire pigtail, wire-lead not PCB-trace per the interface
  file), MH-5/MH-6 (dedicated motor-driver-zone mounting holes). J1/J2/J3/SW1/D1
  carry over from Rev 2 in identity, re-positioned only by the board's own
  Y-rescale (see §10).
- New fastener classes: Rev 2 used one class (M2.5 self-tapping, PCB lid to
  base). Rev 3 adds **plain M3 clearance** (motor-to-platform, direction
  reversible) and **M3-into-heat-set-insert** (containment cap to base
  flange) — three classes total, each justified separately in §12.
- Envelope grew from Rev 2's base-outer 67.0×47.0mm (true assembled,
  including tabs/lid-skirt overhang, ≈71.4×59.8mm; total height 20.6mm) to
  Rev 3's 107×162mm shell-only footprint / 111.4×170.6×49.0mm true assembled
  envelope (§3; height corrected to 49.0mm in the Rev 3.1 rework above — see
  MISS-008) — driven by the flywheel bay's own footprint and height, not
  by the PCB bay, which only grew to 107×57mm (still smaller than the
  flywheel bay's own 87×87mm footprint).
- New: REQ-403 safety disposition proposed — **physical containment**
  (§8), not clearance-plus-firmware-limiting alone. This is new because Rev 2
  had no rotating mass; Rev 3 introduces one for the first time.
- New: REQ-306 rotation-clearance keep-out (§7) and REQ-307 vibration
  isolation disposition (§9) — neither applied to Rev 2, which had no motor.
- Verification: this revision's own build/check process caught and fixed 4
  geometric defects (2 of them collisions that would have caused genuine
  print/assembly failures or a safety-relevant open gap), correctly
  dismissed 2 false-alarm findings, flagged (without fixing, as
  out-of-scope for this task) one pre-existing Rev 2 defect, and disclosed
  one new borderline-but-compliant finding — all itemized in §11. **Update,
  Rev 3.1:** the flagged pre-existing Rev 2 defect (the base-tab/lid-skirt
  overlap) was subsequently fixed in the Rev 3.1 review-driven rework above
  (MISS-010) — see §11.C, §11.G.
- Rev 2's proven conventions carried forward and **re-justified against the
  new geometry** (not assumed to still fit): 2.0mm minimum wall thickness,
  0.2mm/side fit clearance, external-tab lid fastening with M2.5 self-tapping
  screws for the PCB lid, cap+skirt joint style (now used twice — PCB lid
  and containment cap both use it).

**Author:** Mechanical Lead (Rev 3 drafted in a prior session; Rev 3.1
review-driven rework in this session).
**Companion file:** `hardware/mechanical/bench-imu-01-enclosure.scad` (Rev
3.1, 1208 lines) — every dimension in this document is a named variable in
that file; the two must be read together.
**Authoritative input:** `hardware/mechanical-interface.md` (Rev 3, 686
lines, fixed input — not edited by this task). Requirements traced:
`requirements/requirements.md` REQ-306, REQ-307, REQ-308, REQ-309, REQ-403,
REQ-405. Safety context: `validation/open-issues.md` ISS-020.

---

## 0. Tooling honesty

Re-verified fresh in this session, not assumed from a prior revision or from
the task brief's own claim:

- `blender-get_addon_status` → **"Could not connect to Blender."** No live
  CAD/3D-modeling MCP connection exists in this environment. This matches
  the task brief.
- However, a local `openscad` **2026.08.30** binary (`/opt/homebrew/bin/openscad`)
  **is** installed and working, along with Python `numpy-stl` 3.2.0 and
  `trimesh` 4.11.5. This **contradicts** the task brief's claim of "no local
  `openscad`/`freecad`/`cadquery` toolchain" — flagged here rather than
  silently corrected, per this project's own tooling-honesty discipline. No
  `freecad`, `cadquery`, `solid`, or `build123d` was found.
- What this means in practice: this design **was** rendered and geometrically
  validated locally this session — `openscad -o out.stl bench-imu-01-enclosure.scad`
  produces a manifold mesh (CGAL Status: NoError, Genus 6, 4610 vertices,
  9240 facets), and `trimesh`/`numpy-stl` were used for boolean-intersection
  interference checks between parts (§11). This is a **real geometric
  check**, not an eyeball estimate — but it is still **not** a substitute for
  a physical print-and-fit test, a structural (FEA) analysis, or a CAD-native
  fillet/draft/tolerance-stack review. No STL was exported into the repo (the
  deliverable remains the parametric `.scad` source plus this spec); no claim
  of fabrication or physical fit-check is made anywhere in this document.
- The `.scad` file's own header (lines 11–38) carries the identical
  disclosure, so a reader of either file alone gets the same honest picture.

**Rev 3.1 addendum (this session) — tooling re-verified, render stats
updated, not silently carried forward stale:** the same `openscad`
2026.08.30 / `trimesh` 4.11.5 / `numpy` 2.4.4 toolchain was confirmed
working again this session (plus a scratch venv for `numpy-stl`/`rtree`,
needed only because system `pip` is PEP-668-blocked — no capability
change). All three Cycle 3 fixes (MISS-008/009/010) were verified using it:
rendered full-assembly checks, `intersection()` boolean tests, and
point-containment sweeps at 7–8 probe points per finding — the same
methodology the Reviewer itself used, not a lighter-weight spot-check. The
render statistics quoted above (Genus 6, 4610 vertices, 9240 facets) are
**stale** — kept verbatim here for the audit trail, not silently rewritten —
and describe the pre-fix Rev 3 file. The current, post-fix file was
re-rendered fresh this session and authoritatively reports **Status:
NoError, Genus 8, 4618 vertices, 9264 facets** (`openscad -o out.stl
bench-imu-01-enclosure.scad`, checked directly, not inferred). No attempt is
made here to attribute the vertex/facet/Genus delta to a specific one of the
3 fixes individually — that breakdown was not isolated this session and is
not asserted. No STL was exported into the repository by this session
either — same disclosure as above, unchanged.

---

## 1. Scope recap

Per `.github/agents/mechanical-lead.agent.md`, Phase 1 scope is: enclosure/
spatial layout, PCB mounting, connector accessibility, component-height
clearance, internal clearance/interference, fastener placement, wall
thickness, assembly order, and basic print-fit tolerance +
manufacturability. Out of scope (explicitly deferred, `docs/architecture-evolution.md`
§10/§13): statistical tolerance stack-up, motion/joints/hinges, advanced
material selection beyond stating an assumed print material, thermal zones,
antenna keep-out, STEP/neutral 3D model, center of mass, battery wiring,
detailed cable-exit geometry. This revision adds three new topics to the
Phase-1 checklist that Rev 2 never had to address: a rotation-clearance
keep-out (REQ-306), a motor-mounting-method decision, and a safety-critical
containment disposition (REQ-403) — all still within Phase 1's existing
"internal clearance / component-height clearance / basic manufacturability"
categories, just applied to a new, moving, energy-storing component.

---

## 2. Print-fit tolerance & manufacturability rules

Carried forward from Rev 2 **and explicitly re-justified** against the new
geometry (per this task's instruction not to assume Rev 2's conventions
still fit unchanged):

| Rule | Value | Re-justification for Rev 3 |
|---|---|---|
| Fit clearance (mating parts, per side) | **0.2mm** | Same FDM-fit allowance as Rev 2. Re-checked against the new, larger mating interfaces: PCB-lid skirt/base (unchanged formula), and the **new** containment-cap skirt/base-flange interface (105.4mm ID vs. 105.0mm OD — same 0.2mm/side result at 10× the diameter, so the allowance is diameter-independent and still appropriate). |
| Minimum wall thickness (FDM) | **2.0mm** | Unchanged rule. Re-checked at every new Rev 3 wall: flywheel-bay wall (`containment_wall_t`=4.0mm, 2× minimum, justified by containment duty in §8, not just print rules), heat-set-insert flange material each side of the insert bore (2.2mm, §12), and the motor-wire-bridge duct-bore wall (exactly 2.0mm in Z — the one place Rev 3 sits at the rule's exact floor, flagged in §11/§13). |
| Overhang requiring support | **>45° from vertical** | Unchanged rule of thumb. Applied to new features: the motor-platform boss (vertical cylinder, 0° overhang, fine), the containment-cap dome/flange transition (vertical wall + flat flange, no overhang), and the wire-bridge block (flat horizontal underside — evaluated as a bridge, not an overhang; see next row). |
| Maximum unsupported bridge span | **10.0mm** | Unchanged rule (same as Rev 2's own J1-cutout precedent). Re-checked at the **new** motor-wire bridge: true unsupported span is 9.0mm (bridge center) to 9.416mm (bridge edges) — within the rule, but at 90.0–94.2% of it. Disclosed, not silently passed over (§11/§13), mirroring Rev 2's own disclosed-but-accepted 9.5mm/95%-of-limit J1 bridge. |
| Print material | **PETG** (`ASSUMPTION`, per `hardware/mechanical-interface.md` B6) | Not a Mechanical Lead decision — inherited from the interface file's own stated assumption, cited here rather than re-derived. PETG's practical layer-adhesion strength is part of why the flywheel-bay wall was set to 2× minimum (4.0mm) rather than 1× — a plastic wall in a containment role should not rely on the thinnest print-safe wall available. If PLA is used instead, this containment margin should be re-examined (PLA is more brittle under impact than PETG). |

No advanced tolerance stack-up (multi-part statistical accumulation) is
performed — this remains explicitly out of Phase 1 scope. Every check in
this document is a single-interface, deterministic clearance computation.

---

## 3. Overall envelope

Two ways of reading "footprint," both reported (same convention Rev 2 used
for its own two-tier reporting, extended here across two bays):

| Reading | X | Y | Z (height) | vs. REQ-308 (~150mm-class, "relaxed... generous soft ceiling... not to be over-engineered against") |
|---|---|---|---|---|
| **Shell-only** (both bay footprints as designed, tabs/skirt overhang excluded) | 107.0mm | 162.0mm | — | Y is 8.0% over the ~150mm reading |
| **True assembled** (includes PCB-lid tab projection and containment-cap flange, the actual outermost physical extent) | 111.4mm | 170.6mm | 49.0mm | Y is 13.7% over the ~150mm reading |

REQ-308 explicitly frames ~150mm as a relaxed, generous **soft** ceiling, not
a hard limit, and explicitly cautions against over-engineering to hit it
exactly. 8–14% over is judged acceptable given: (a) the flywheel's own
rotation-clearance diameter (76mm) plus a structurally-justified 4mm
containment wall plus a 9mm flange projection for the cap-bolt bosses is a
real physical lower bound, not a padding choice — the flywheel bay's own
minimum footprint is 2×(43.5+9.0) = 105.0mm across; (b) the PCB bay's own
107mm side was inherited from the interface file's own board width (§4), not
from the Mechanical Lead's discretion. The Y-dimension overrun is
acknowledged as a genuine, disclosed trade-off (see §10 for the alternative
layout that was considered and rejected), not something silently absorbed.
The X/Y figures above are unaffected by the Rev 3.1 fixes (MISS-008 is a
Z-only correction; MISS-009's void and MISS-010's relief notches are both
internal/inset and never touch an outer boundary) — only the height column
changed.

**Total height corrected, Rev 3.1 (MISS-008):** 43.0mm → **49.0mm**, set
entirely by the **flywheel bay's** own Z-stack (§7, §4.4), which is more
than double the PCB bay's own height (23.1mm) — the two bays are
side-by-side (not stacked), so the assembly's overall height is the taller
of the two, not their sum. The pre-fix 43.0mm figure was itself computed
from a Z-stack that omitted `fw_hub_collar_h` in `fw_disk_bottom` (MISS-008)
— every downstream figure derived from it, including this overall height,
was therefore stale until the fix cascaded through. See §4.4 and §11.G for
the full corrected derivation.

---

## 4. Full dimensional parameter tables

### 4.1 Interface-traced values (from `hardware/mechanical-interface.md`)

| Parameter | Value | Unit | Confidence | Source |
|---|---|---|---|---|
| `pcb_length` | 100 | mm | CONFIRMED | Interface A2 |
| `pcb_width` | 50 | mm | CONFIRMED | Interface A2 |
| `pcb_thickness` | 1.6 | mm | CONFIRMED | Interface A2 (standard 2-layer stack, unchanged from Rev 2) |
| `top_component_clearance` | 11 | mm | CONFIRMED | Interface A3 — tallest top-side part is J4 barrel jack (per interface's own component-height table) |
| `bottom_component_clearance` | 0 | mm | CONFIRMED | Interface A3 — no bottom-side components populated |
| Board mounting holes MH-1..4 | (3.5,3.5), (96.5,3.5), (96.5,46.5), (3.5,46.5), ⌀2.8mm clearance (M2.5) | mm | CONFIRMED | Interface A1 (corner pattern, unchanged in kind from Rev 2, repositioned for the new 100×50 outline) |
| Board mounting holes MH-5/6 | (85,3.5), (85,46.5), ⌀2.8mm clearance (M2.5) | mm | CONFIRMED | Interface A1 — added specifically near the motor-driver zone for extra board rigidity close to the new high-current/switching components |
| J1 (existing header) | (0,25), 9.5×6mm cutout, ref. height 3.2mm | mm | CONFIRMED | Interface A4, unchanged position/size from Rev 2 |
| J2, J3 (existing headers) | (16,50), (30,50) | mm | CONFIRMED | Interface A4, unchanged from Rev 2 |
| SW1 (button) | (44,50) | mm | CONFIRMED | Interface A4, unchanged from Rev 2 |
| D1 (LED) | (10,37.5) | mm | CONFIRMED | Interface A4 — Y-position rescaled from Rev 2's 30mm by the same 1.25× board-width growth ratio applied to all original sensor-zone parts |
| J4 (barrel jack, motor supply) | (100,25), edge-mounted | mm | CONFIRMED position / **ESTIMATE cutout diameter** | Interface A4 for position; `j4_cut_dia`=10.0mm is this Mechanical Lead's own outside-knowledge estimate for a generic 5.5/2.1mm barrel jack, no datasheet cited in the interface file — flagged for pre-build re-verification |
| MC-1 (motor phase-wire pigtail) | (92,0), bottom edge, wire exit −Y | mm | CONFIRMED | Interface A4 — **wire-lead, not PCB-trace**, per interface's explicit note; this is a board-edge exit point, not a component footprint |
| M1 motor body | ⌀27mm × 18.5mm height, ⌀3mm shaft | mm | CONFIRMED | Interface B1, `DS-MTR-021` |
| M1 mounting-bolt pattern | 12mm square, 4× holes | mm | **ASSUMPTION** | Interface B1 flags this as an open item — no confirmed datasheet bolt-pattern; a generic hobbyist-brushless-outrunner convention is assumed here, explicitly flagged NOT T-Motor-specific |
| Flywheel disk | ⌀60mm × 4.5mm, mild steel, ρ=7850 kg/m³ | mm / kg/m³ | **ASSUMPTION** | Interface B2 — back-computed against the electrical team's target rotational inertia; 4.505mm recomputed vs. 4.5mm stated is a consistency check, not an independent confirmation |
| Rotation clearance envelope | ⌀76mm × 10.5mm axial | mm | CONFIRMED (derivation) | Interface B5 — `fw_radial_margin`=8mm, `fw_axial_margin_per_face`=3mm, both interface-stated safety margins around the disk's own swept volume |
| Print material | PETG | — | ASSUMPTION | Interface B6 |
| Total assembly mass | ≈149–150g (board ≈19–20g populated + motor ≈30g + flywheel 100g, enclosure plastic itself is additional) | g | ESTIMATE | Interface A5/B1/B2/B7 — context only, not a driving mechanical dimension at this scale; no structural deflection/FEA analysis performed (out of Phase 1 scope) |

### 4.2 PCB-bay own-design values (formulas unchanged from Rev 2; only resulting numbers changed because the board itself grew)

| Parameter | Value | Unit | Confidence | Rationale |
|---|---|---|---|---|
| `fit_clearance` | 0.2 | mm | Carried, re-justified §2 | FDM fit allowance |
| `min_wall_t`/`wall_t`/`floor_t` | 2.0 | mm | Carried, re-justified §2 | Minimum FDM wall |
| `board_xy_keepout` | 1.5 | mm | DERIVED | Same margin rule as Rev 2, applied around the new 100×50 outline |
| `standoff_od` | 6.0 | mm | DERIVED | Unchanged formula (2× `standoff_pilot_dia` + wall margin) |
| `standoff_pilot_dia` | 2.0 | mm | Carried | Self-tap pilot for M2.5, unchanged |
| `standoff_h` | 6.0 | mm | DERIVED | = `bottom_component_clearance`(0) + margin — same formula as Rev 2, coincidentally close in value only because Rev 2's own bottom clearance was also small |
| `screw_len` | 6.0 | mm | Carried | M2.5 self-tap screw length, unchanged |
| `z_margin` | 0.5 | mm | Carried | Same stack-up margin convention as Rev 2 |
| `base_interior_h` | 19.1 | mm | DERIVED | = `standoff_h` + `pcb_thickness` + `top_component_clearance` + `z_margin` = 6.0+1.6+11.0+0.5 |
| `base_total_h` | 21.1 | mm | DERIVED | = `base_interior_h` + `floor_t` |
| `lid_lip_h` | 3.0 | mm | Carried | Unchanged skirt-overlap depth |
| `lid_roof_t`/`lid_skirt_t` | 2.0 | mm | Carried | = `min_wall_t` |
| `pcb_bay_total_height` | 23.1 | mm | DERIVED | = `base_total_h` + `lid_roof_t` |
| `interior_x` / `interior_y` | 103 / 53 | mm | DERIVED | = `pcb_length`/`pcb_width` + 2×`board_xy_keepout` |
| `base_outer_x` / `base_outer_y` | 107 / 57 | mm | DERIVED | = interior + 2×`wall_t` |
| `lid_skirt_inner_x` / `_y` | 107.4 / 57.4 | mm | DERIVED | = `base_outer` + 2×`fit_clearance` |
| `lid_skirt_outer_x` / `_y` | 111.4 / 61.4 | mm | DERIVED | = skirt-inner + 2×`lid_skirt_t` |
| `board_offset_x` / `_y` | 3.5 / 3.5 | mm | DERIVED | = `wall_t` + `board_xy_keepout` |
| `j1_cut_w`/`_h`/`_z` | 9.5 / 6 / 6 | mm | Carried | Unchanged from Rev 2 — same connector, same size |
| `j4_cut_dia`/`_z` | 10 / 6 | mm | **ESTIMATE** | New Rev 3 cutout — see §4.1 flag |
| `bay_edge_margin` | 1.5 | mm | Carried | Unchanged component-keepout-to-bay-wall rule |
| `bay_x_min`/`_max` | 9.5 / 48.0 | mm | DERIVED | Numerically **unchanged from Rev 2** — governed entirely by the original sensor-zone parts (J2 at X=16, SW1 at X=44), whose X-positions did not move when the board grew in length |
| `bay_y_min` | 42.5 | mm | DERIVED | Rescaled from Rev 2's 32.5mm by the board's own Y-growth |
| Tab positions (corners only) | (3.5,3.5,dy−1), (96.5,3.5,dy−1), (96.5,46.5,dy+1), (3.5,46.5,dy+1) | mm | DERIVED | Repositioned to the new board corners; same 4-corner convention as Rev 2 |
| `tab_w`/`tab_project`/`tab_base_t` | 8 / 6 / 5.6 | mm | Carried | Unchanged tab geometry |
| `tab_relief_margin` | 1.0 | mm | **ASSUMPTION, new Rev 3.1 (MISS-010 fix)** | Y-direction margin added on each side of `lid_skirt_t`(2.0mm) when sizing the relief notch `lid_shell()` now cuts at each of the 4 `tab_positions`, so the notch (4.0mm total Y) clears `base_tab()`'s outward projection with margin rather than exactly at the boundary — same "small explicit cut-tool overshoot" convention already used throughout this file (e.g. the existing "+1"/"+2" pattern on cylinder/cube heights elsewhere), not a newly-invented rule. See §11.C, §11.G. |

### 4.3 Motor-mount own-design values (new in Rev 3)

| Parameter | Value | Unit | Confidence | Rationale |
|---|---|---|---|---|
| `motor_platform_od` | 31.0 | mm | DERIVED | = `m1_body_dia`(27) + 2×`wall_t`(2.0) — the boss is sized to comfortably enclose the motor body's own footprint plus a minimum print-safe wall |
| `motor_platform_h` | 8.0 | mm | ESTIMATE | Chosen to lift the motor body clear of the flywheel-bay floor disc so the flywheel itself (mounted above the motor) sits at the height needed for its own clearance envelope — see §7 Z-stack |
| `m1_mount_hole_dia_clear` | 3.4 | mm | Carried convention | Standard M3 clearance-hole diameter (same clearance-fit convention Rev 2 used for M2.5 at 2.8mm, scaled up to M3) |
| `m1_bolt_square` | 12.0 | mm | **ASSUMPTION** | See §4.1 flag — generic hobbyist convention, not datasheet-confirmed |
| Bolt-hole corner radius | 8.485 | mm | DERIVED | = √(6²+6²) from the assumed 12mm-square pattern's center |
| Margin, bolt-hole to motor-body edge | 5.015 | mm | DERIVED | = 13.5(`m1_body_dia`/2) − 8.485 — pattern is physically plausible under the motor body |
| Margin, bolt clearance-hole outer edge to platform-boss edge | 5.315 | mm | DERIVED | = 15.5(`motor_platform_od`/2) − (8.485+1.7) |
| Shaft clearance-hole radius | 1.7 | mm | DERIVED | = (`m1_shaft_dia`(3.0)+2×`fit_clearance`)/2 |
| Gap, shaft-hole edge to nearest bolt-hole edge | 5.085 | mm | DERIVED | No overlap between the two hole families |
| `fw_hub_standoff` | 3.0 | mm | ESTIMATE | Gap between motor bell-top and the bottom face of the hub collar, for tool/wrench clearance when tightening the collar's set screw |
| `fw_hub_collar_od`/`_h` | 8.0 / 6.0 | mm | **ASSUMPTION** | Generic set-screw shaft-collar dimensions; no specific manufacturer part selected/cited — flagged as an open item in §16 |
| `fw_shaft_exposed_len_needed` | 9.0 | mm | DERIVED (minimum requirement) | = `fw_hub_standoff`(3)+`fw_hub_collar_h`(6) — this is the **minimum** shaft length M1 must expose above its bell for this mounting scheme to work; M1's actual exposed shaft length is UNKNOWN (not in the interface file) and must be confirmed before build |

### 4.4 Flywheel bay / containment own-design values (new in Rev 3)

| Parameter | Value | Unit | Confidence | Rationale |
|---|---|---|---|---|
| `fw_dia` | 60.0 | mm | ASSUMPTION (interface B2) | Flywheel disk diameter |
| `fw_radial_margin` | 8.0 | mm | CONFIRMED (interface B5) | Safety margin beyond the disk's own swept radius |
| `fw_env_dia` | 76.0 | mm | DERIVED | = `fw_dia` + 2×`fw_radial_margin` — the actual REQ-306 rotation-clearance keep-out diameter |
| `fw_axial_margin_per_face` | 3.0 | mm | CONFIRMED (interface B5) | Axial safety margin, each face of the disk |
| `fw_env_axial` | 10.5 | mm | DERIVED | = `fw_t`(4.5) + 2×`fw_axial_margin_per_face` |
| `fw_radial_standoff` | 1.5 | mm | ESTIMATE | Extra gap between the rotation-clearance envelope's own outer radius and the containment wall's inner face — a "keep-out beyond the keep-out," so a small manufacturing/assembly offset can't put the wall inside the safety margin itself |
| `fw_bay_inner_r` | 39.5 | mm | DERIVED | = `fw_env_dia`/2 (38.0) + `fw_radial_standoff`(1.5) |
| `containment_wall_t` | 4.0 | mm | ESTIMATE (2× `min_wall_t`) | Deliberately thicker than the print-safe minimum — this wall's job is containment (§8), not just enclosure, so it is sized above the manufacturability floor on purpose |
| `fw_bay_outer_r` | 43.5 | mm | DERIVED | = `fw_bay_inner_r` + `containment_wall_t` |
| `fw_flange_project` | 9.0 | mm | ESTIMATE | Radial width of the bolted flange band, sized to comfortably host 6 heat-set inserts around the circumference with adequate wall material each side (§12) |
| `bolt_circle_r` | 48.0 | mm | DERIVED | = `fw_bay_outer_r` + `fw_flange_project`/2 — centered in the flange band |
| `fw_flange_or` | 52.5 | mm | DERIVED | = `fw_bay_outer_r` + `fw_flange_project` |
| `fw_flange_dia` | 105.0 | mm | DERIVED | = 2×`fw_flange_or` — the base's own flange OD that the containment cap's skirt slides over |
| `n_cap_bolts` | 6 | — | ESTIMATE | Even spacing (60° apart) around the flange, judged adequate for a cap whose job is to stay closed under a low-probability, low-bulk-stress event (§8) — not a computed fastener-load calculation (out of Phase 1 scope) |
| `heatset_od`/`_len` | 4.6 / 5.7 | mm | **ASSUMPTION** | Generic brass heat-set insert dimensions (common M3 size); no specific manufacturer part selected — flagged in §16 |
| Margin, insert bore to flange inner/outer edge | 2.2 / 2.2 | mm | DERIVED | Both exceed `min_wall_t`(2.0) by 0.2mm — tight but compliant (§12) |
| `flange_band_h` | 8.0 | mm | ESTIMATE | Z-height of the bolted flange band, sized to give the heat-set insert (5.7mm) a full depth of solid material plus a margin above it (2.3mm) below the cap's own top surface |
| `wire_duct_dia` | 5.0 | mm | ESTIMATE | Sized for a small pigtail of 2–3 motor-phase wires (18–22 AWG class), no specific wire gauge confirmed |
| `wire_bridge_w`/`_h` | 12.0 / 9.0 | mm | DERIVED | `_h` = `wire_duct_dia` + 2×`wall_t` (duct bore + minimum wall both sides, by construction — leaves **zero** spare in Z, see §11/§13) |
| `bridge_fuse_overlap` | 2.0 | mm | ESTIMATE | Introduced this revision specifically to fix Error #3 (§11) — ensures the wire-bridge block's inner face is planted solidly inside the flywheel-bay wall rather than stopping at the bay's own center |
| Z-stack: `fw_floor_top` | 2.0 | mm | DERIVED | = `floor_t` |
| Z-stack: `fw_motor_platform_top` | 10.0 | mm | DERIVED | = `fw_floor_top` + `motor_platform_h`(8.0) |
| Z-stack: `fw_motor_bell_top` | 28.5 | mm | DERIVED | = `fw_motor_platform_top` + `m1_body_h`(18.5) |
| Z-stack: `fw_disk_bottom`/`_top` | 37.5 / 42.0 | mm | DERIVED | = `fw_motor_bell_top` + `fw_hub_standoff`(3.0) + `fw_hub_collar_h`(6.0) as the bottom face (**corrected Rev 3.1, MISS-008** — the pre-fix formula omitted `+fw_hub_collar_h`, silently overlapping the disk with the hub collar it must clear; see §11.G); `_top` = `_bottom` + `fw_t`(4.5) |
| Z-stack: `fw_clearance_top` | 45.0 | mm | DERIVED | = `fw_disk_top` + `fw_axial_margin_per_face`(3.0) (was 39.0mm pre-fix; shifted +6.0mm by the MISS-008 correction above) |
| Z-stack: `fw_cap_outer_top`/`fw_bay_total_height` | 49.0 / 49.0 | mm | DERIVED | Cap adds 4.0mm of dome/flange material above the clearance envelope's own top (was 43.0/43.0mm pre-fix; shifted +6.0mm by the MISS-008 correction above). The flange band and containment-cap skirt's own Z-range (§11.F) shifts identically, from [31.0,39.0]mm to [37.0,45.0]mm. |

---

## 5. Design rationale by checklist item

Numbered to match the Mechanical Reviewer's own 10-item checklist (§15
reproduces it verbatim for the self-check):

1. **PCB mounting** — 6 standoffs (`base_standoffs()`) at MH-1..6, unchanged
   mechanism from Rev 2 (heat-formed/self-tap pilot bosses), now 6 instead of
   4 because the interface file added MH-5/6 for rigidity near the new
   motor-driver zone.
2. **Connector accessibility** — see §10, all cutouts sized/positioned from
   interface-file coordinates; the one new judgment call (the ~42mm wire run
   from the duct to MC-1's actual position) is disclosed there, not buried.
3. **Component-height clearance** — `top_component_clearance`=11mm and
   `bottom_component_clearance`=0mm both taken directly from the interface
   file (A3), driving `base_interior_h`/`lid_lip_h` unchanged in formula from
   Rev 2.
4. **Internal clearance/interference** — see §11 for the full computed
   record (4 fixed defects, 2 dismissed false alarms, 1 flagged pre-existing
   issue, 1 new borderline finding).
5. **Fastener placement** — see §12; 3 fastener classes now, each justified
   by the joint it serves, not by copying Rev 2's single class onto new
   joints that have different duty.
6. **Wall thickness** — 2.0mm minimum held everywhere except by deliberate,
   disclosed exception (flywheel-bay wall at 4.0mm for containment duty; the
   wire-bridge duct wall sits at exactly 2.0mm, §11/§13).
7. **Assembly order** — see §14; re-derived from scratch for 3 pieces, not
   copied from Rev 2's 2-piece sequence.
8. **Basic print-fit tolerance** — 0.2mm/side, applied consistently at both
   mating interfaces (PCB lid/base, containment cap/base flange), §2.
9. **Basic manufacturability/3D-printability** — §13; every new feature
   checked against the same overhang/bridge/wall rules as Rev 2, not given a
   pass by association with a previously-reviewed design.
10. **Interface-value traceability** — §4.1 traces every board-geometry
    number to its interface-file source; §16 lists everything that is this
    Mechanical Lead's own ASSUMPTION/ESTIMATE rather than an interface fact.

Two items unique to this revision, not on the Reviewer's original 10-item
list because Rev 2 had no rotating mass, are addressed as dedicated sections
rather than folded into the above: **§6 motor-mounting-method decision**,
**§7 rotation clearance / REQ-306**, **§8 REQ-403 safety disposition**, **§9
vibration isolation / REQ-307 disposition**. The piece-count decision (item
10 above, REQ-309) is expanded on here: Rev 2's 2-piece construction was
explicitly framed by the requirement as a baseline, not a ceiling: adding a
3rd piece (the containment cap) was a deliberate design decision, not a
default, and is justified entirely by §8's containment reasoning — without
the REQ-403 containment need, a 2-piece design (motor/flywheel bay open on
top, or covered by an extension of the PCB lid) would likely have sufficed
for the "enclosure" requirement alone.

---

## 6. Motor-mounting-method decision

**Decision: off-board (bracket/platform)-mounted, not a PCB-footprint
part.** The motor mounts to a raised cylindrical platform (`motor_platform()`)
molded directly into the enclosure base, using its own 4-bolt pattern into
that platform — not to the PCB. Electrical connection to U5 (motor driver)
is via a wire-lead pigtail (MC-1, board-edge exit at (92,0)), not a
PCB-mounted connector footprint that the motor plugs into directly. This
matches the interface handoff's own non-binding lean and the constraint that
MC-1 is explicitly a wire-lead connection, not a PCB trace.

**Why not on-PCB mounting:** the motor's own footprint (⌀27mm body) and
its bolt pattern would need to sit directly over/adjacent to the PCB, but
the flywheel's rotation-clearance envelope (⌀76mm — see §7) is already
larger than the entire 50mm board width. Any on-PCB motor mount would force
either (a) the flywheel's swept volume to overhang the PCB edge, or (b) the
PCB to be enlarged specifically to host the motor footprint under the
flywheel — both of which subordinate the board's own routing/component
layout to a purely mechanical constraint that the interface file's own B5
derivation already treats as enclosure-side, not board-side. An off-board
platform decouples the two: the PCB's own footprint is sized by its
electronics (100×50mm per A2), and the motor/flywheel subsystem is sized by
its own physics (§7), and the two are joined only by a wire and a duct.

**Why vertical shaft, motor below / flywheel above:** this places the
flywheel's own mass directly above its rotating support (the motor's bell
and shaft), which is the geometrically simplest and lowest-part-count way to
stack the disk on the shaft with a hub collar, and it means the flywheel's
own weight loads the shaft axially/rotationally in the same way the motor
was designed for (most small BLDC/hobby motors expect an axial mounted load
on a vertical or near-vertical shaft in this class of application) rather
than a cantilevered horizontal arrangement that would impose a bending
moment on the shaft the motor's own bearings may not be rated for. No
motor-bearing load rating is in the interface file (UNKNOWN) — the vertical
arrangement is the more conservative choice given that unknown, not a
datasheet-confirmed one.

**Why a shaft-mounted hub collar, not the bell-mount/ring-geometry
alternative:** the interface file (B2) explicitly flags a second, real
alternative — mounting the flywheel directly to the motor's own rotating
outrunner bell (a ring/annulus shape around the bell rather than a solid
disk on the shaft) — and explicitly cautions that this alternative would
have a **higher** true moment of inertia than the solid-disk figure this
whole design (and the electrical team's own target) is built around. This
design does **not** adopt the bell-mount alternative, for three reasons: (1)
it would silently change the flywheel's own moment of inertia away from the
value the electrical/control side is presumably targeting, without being
asked to make that trade; (2) a shaft-mounted hub collar is a simpler,
better-understood mechanical interface for a paper-design exercise — its
failure mode (a set-screw loosening) is at least nameable, whereas a
bell-mount's attachment method to a specific motor's specific bell geometry
is not specified anywhere in the interface file; (3) the interface file
presents the solid-disk/shaft-mount geometry as the **primary** proposal,
with the bell-mount flagged as an alternative, not a preference — so this
design follows the primary proposal. This is disclosed here as an explicit
choice, not a silent omission of the alternative.

**Consequence for U5 wiring:** because the motor sits ~42mm away (in X) from
MC-1's actual board-edge position (see §10), the motor's 3-phase wire
pigtail must run along the interior floor between the flywheel bay's wire
duct and the PCB bay. This is a real, disclosed trade-off from choosing a
width-centered flywheel-bay layout over a motor-zone-centroid-aligned one
(§10) — it does not affect the mounting-method decision itself, only the
wire-routing distance.

---

## 7. Rotation clearance envelope / REQ-306

REQ-306 requires the enclosure design to provide a real, checked 3D keep-out
around the flywheel's swept volume — not an eyeballed gap. This design's
keep-out is the volume between `fw_env_dia`=76.0mm (radial) and
`fw_env_axial`=10.5mm (axial), both taken directly from the interface file's
own stated margins (B5: 8mm radial, 3mm axial per face) around the disk's
actual physical envelope (⌀60×4.5mm). This is a real solid modeled in the
`.scad` file as `fw_clearance_zone()` (rendered as a translucent reference
volume, not a physical part) and used as the actual sizing driver for the
containment wall's own inner radius — i.e., the keep-out is not just
documented, it is the dimension the containment structure is built around:

- `fw_bay_inner_r` = `fw_env_dia`/2 + `fw_radial_standoff` = 38.0+1.5 = 39.5mm
  — the containment wall's inner face sits 1.5mm beyond the keep-out's own
  outer radius, so the wall itself never physically encroaches into the
  keep-out volume, with margin.
- Vertically, `fw_clearance_top`=45.0mm is the keep-out's own top face; the
  containment cap's structure begins only above that, at 45.0–49.0mm.
  **(Corrected Rev 3.1, MISS-008:** these were 39.0mm / 39.0–43.0mm pre-fix,
  computed from a `fw_disk_bottom`/`fw_disk_top` that itself omitted
  `fw_hub_collar_h` and so sat 6.0mm too low; the axial keep-out margin
  itself (`fw_axial_margin_per_face`=3.0mm) was never wrong, only the disk
  position it's measured from. See §4.4, §11.G.)

**Sanity checks performed (§11 has the full record):** the motor platform
boss (radius 15.5mm) and its bolt/shaft holes sit entirely inside the
keep-out's own inner radius (39.5mm) with 24.0mm of clear radial gap between
the platform's own edge and the containment wall — this gap is exactly what
the missing-floor defect (Error #4, §11) required a floor disc to span, and
it is now filled with solid material, not left open. The disk's own radius
(30.0mm) plus the required 8.0mm interface-mandated margin (=38.0mm) is
checked against the wall's inner face (39.5mm) with the additional 1.5mm
standoff explicitly by construction, not by coincidence.

This keep-out is a **clearance decision**, answering "can the flywheel spin
without hitting anything in normal operation." It is explicitly **not** a
substitute for the REQ-403 containment decision (§8), which answers a
different question: "what happens if the flywheel or a piece of it comes
loose." The `.scad` file's own in-code comment on `fw_clearance_zone()`
states this distinction explicitly, and it is repeated here so the two
requirements are never conflated in review.

---

## 8. REQ-403 safety disposition (proposal — pending Independent Review, then human HITL gate)

**Proposal: provide active physical containment**, not clearance-plus-
firmware-speed-limiting alone. This section is the engineering reasoning
behind that proposal; the decision itself is not final until Independent
Mechanical Review has assessed it and the human has acted on the HITL gate
REQ-403 itself calls out.

**The physics, recomputed this session, not assumed from ISS-020's own
framing:**

**Rev 3.3 correction (this revision) — the RPM input is corrected, not the
formulas below:** the "22,200 RPM no-load-high" column used through Rev 3.2
is superseded. Circuit Engineer found and fixed a real premise error in
`datasheets/evidence-log.md` DS-MTR-018 (its own ~22,200 RPM figure was
mislabeled "full-charge 3S (11.1V)"; 11.1V is actually 3S's *nominal*
voltage — full-charge is 12.6V) and, accounting for this design's own 13.0V
`VM_MOTOR` envelope ceiling (§7.5.9) and the real J4→F1→D2→D3→U6→U5 series
voltage drops, independently re-derived the true credible-worst-case
no-load speed as RPM≈25,060–25,280 (point ≈25,180) — new §7.5.13,
`hardware/schematic/bench-imu-01-design.md`, Evidence ID DS-MTR-080.

**Independent verification performed before using this input (not accepted
on report alone):** this Mechanical Lead re-read DS-MTR-017/018/079/080 and
DS-PROT-005/006/031/033/034 directly in `datasheets/evidence-log.md`,
hand-reproduced the KV(2000 RPM/V)×V_VCC arithmetic and the F1/U6/D2
voltage-drop chain from those primary citations, and independently
re-confirmed the 11.1V-nominal-vs-12.6V-full-charge LiPo convention from a
fourth, separate source (a web search on standard LiPo per-cell voltages).
**Verdict: agree** — the derivation is sound, the cited Evidence IDs are
real (not asserted), and the conclusion holds. One immaterial arithmetic
wrinkle found on independent recheck: the stated range's low bound
(25,060 RPM) is very slightly inconsistent with the stated point estimate
(25,180) — an exact recompute puts the true low bound at ≈25,078–25,080 RPM
(the point estimate is exactly the midpoint of 25,080 and 25,280, not of
25,060 and 25,280). This is a ≈20 RPM (≈0.08%) discrepancy, well inside
D2's own VF `ESTIMATE` uncertainty band, and changes no conclusion below;
the disclosed 25,060–25,280 RPM bracket is retained throughout this section
for consistency with the source derivation.

**Every figure below at "≈25,180 RPM" is this Mechanical Lead's own
independent recomputation**, from its own rotor inertia/radius data
(I=4.5×10⁻⁵ kg·m², r=0.030m, §4.1/§4.4, unchanged this revision) using the
same ω/KE/rim-speed/stress formulas already in use in this table since
Rev 3.1 (re-verified against the old 3000/20,000/22,200 RPM values before
reuse) — not a reuse of Circuit Engineer's own illustrative "≈156J/≈79.1m/s"
scaling figures, which independently and closely match this Mechanical
Lead's own result but are not this section's authoritative source (Circuit
Engineer is explicitly not authoritative for this section's own rotor
inertia/radius inputs).

| Quantity | At 3000 RPM target | At 20,000 RPM (M1's 10V-test-condition no-load speed — reference point only, NOT the credible worst case, unaffected by this correction) | At ≈25,180 RPM credible worst case (point estimate; **Rev 3.3**, supersedes the old 22,200 RPM figure — DS-MTR-080, §7.5.13) |
|---|---|---|---|
| Angular velocity ω | 314.2 rad/s | 2094.4 rad/s | 2636.8 rad/s |
| Stored kinetic energy (I=4.5×10⁻⁵ kg·m²) | 2.22 J | 98.70 J (44.44×) | 156.44 J (≈70.4×) |
| Rim tip speed | 9.42 m/s (~34 km/h) | — | 79.11 m/s (~285 km/h) |
| Peak centrifugal stress (solid-disk formula, ν=0.29) | 0.287 MPa | 12.75 MPa | 20.20 MPa |

`ESTIMATE` (the entire "≈25,180 RPM" column) — inherits D2's VF `ESTIMATE`
via the RPM input, combined with this table's own pre-existing
`ASSUMPTION`/`ESTIMATE` disk mass/geometry inputs (§4.1, §4.4); the same
confidence class as the figures it supersedes, not a new or weaker
category. **Range disclosure across the full credible RPM bracket
(25,060–25,280), not just the point estimate:** KE spans ≈154.95–157.69 J
(≈69.8×–71.0× the 3000 RPM baseline, point ≈70.4×); rim tip speed spans
≈78.73–79.42 m/s (≈283.4–285.9 km/h); peak stress spans ≈20.01–20.36 MPa.
Relative to the superseded 121.60 J / 15.70 MPa / 69.74 m/s / 22,200 RPM
figures, this is a ≈12.9–13.9% increase in RPM/ω/rim-speed (point ≈13.4%)
and a ≈27.4–29.7% increase in KE/stress (point ≈28.65%) — energy and stress
scale with ω², so they move super-linearly relative to the RPM correction
itself. The ≈29% KE increase independently reproduces Circuit Engineer's
own "≈29%" figure in §7.5.13, computed here from this Mechanical Lead's own
data rather than copied from it.

The old "44–55× energy range matches ISS-020's own stated '45–55×' almost
exactly" cross-check (Rev 3.1–3.2 text) is **stale as of this correction**:
the credible-worst-case multiplier is now ≈69.8×–71.0× (point ≈70.4×) the
3000 RPM baseline, not ≈45–55×. Observation, not a fix made here:
`hardware/schematic/bench-imu-01-design.md` §7.5.11's own "roughly 45–55×"
framing is now stale for the same reason and is out of this Mechanical
Lead's edit scope — Circuit Engineer/Hardware Lead own updating that
document.

**The key reframing this design is built on:** the bulk-material stress
numbers above are not the real risk. **Re-checked at the corrected RPM
(Rev 3.3):** even at ≈25,180 RPM credible worst case (point estimate; range
20.01–20.36 MPa across 25,060–25,280 RPM), peak stress (≈20.20 MPa) carries
a ~12.4× safety factor against mild steel's yield strength (250 MPa) —
range ≈12.3–12.5× — down from the superseded ~15.9× figure (as expected,
since stress rose ≈28.65% at the point estimate), but the disk itself
remains in no realistic danger of bursting: disk-burst was never the
binding constraint, and this correction does not change that conclusion.
`ESTIMATE` (inherits the RPM input's `ESTIMATE` class, above). The actual
hazard is a **discrete coupling failure**: the hub collar (a generic
set-screw shaft collar, `ASSUMPTION`, no datasheet) losing its grip on the
shaft — from vibration, from an installation error, or simply from a
lower-quality assumed part — and releasing the **entire 100g disk as one
rigid projectile**, at whatever speed the motor happens to be spinning at
the moment of release — now up to ≈25,280 RPM/≈79.4 m/s credible worst
case, not ≈22,200 RPM/≈69.7 m/s. No datasheet exists (UNKNOWN) for the
assumed hub collar's own retention strength, so this failure mode cannot be
bounded by calculation — it can only be defended against structurally.

**Why containment, not clearance-plus-firmware alone:** REQ-405 (the
firmware speed ceiling) is explicitly not yet implemented (ACCEPTED-RISK
pending Firmware Bring-up per ISS-020) — meaning that today, and for an
unknown period going forward, the flywheel's real achievable speed is
bounded only by the motor's own physical no-load speed, now corrected to
the **~25,060–25,280 RPM class** (was ~20,000–22,200 RPM class through Rev
3.2 — see the corrected physics table above), not by any software limit. A
mechanical design that relies on a not-yet-implemented control loop as its
only line of defense against a 100g mass potentially detaching at up to
~285 km/h rim speed (was ~250 km/h) would be providing zero real protection
for as long as that firmware gap exists — which, per the project's own
tracking, is an open and undated item, not a near-term certainty. Given
that:

- This is explicitly a **bench-test, human-attended** context (not an
  unattended field deployment) — the containment decision is scoped to that
  context, not to a hypothetical harsher one. A human is expected to be
  within arm's length of the device during any powered test.
- The stored energy at the credible worst case (~156 J, point estimate;
  range ≈155–158 J across 25,060–25,280 RPM — was ~122 J through Rev 3.2)
  is still substantial — for comparison, that is roughly the kinetic
  energy of a 1kg mass dropped from ~16.0m (was ~12.4m), or a small hand
  tool swung at speed. A 100g fragment departing at up to ~285 km/h (was
  ~250 km/h) is a genuine laceration/impact hazard to an attending human at
  bench distance, not a negligible one — more so, not less so, than
  previously disclosed.
- The mitigating alternative (firmware speed limiting) is real but is
  **not yet built**, and this Mechanical Lead has no authority or visibility
  into when it will be, per the task's own explicit instruction to stay out
  of firmware/control-loop territory.

Given a real, non-trivial energy release scenario, an unquantified
(UNKNOWN-strength) coupling-failure mode as the trigger, a not-yet-existing
software mitigation, and a human physically present during the exact
condition that matters (power applied), this design proposes that the
enclosure itself should not depend on firmware working correctly to keep a
detached 100g disk away from the operator. **This is defense-in-depth, not a
statement that firmware speed-limiting is unnecessary** — REQ-405 remains a
correct and independent mitigation to pursue; this proposal simply does not
treat it as sufficient on its own while it does not yet exist.

**The physical decision made:** the containment cap (§4.4, a 3rd enclosure
piece) is not merely a cover — it is sized and bolted specifically as a
containment structure:
- `containment_wall_t`=4.0mm (2× the print-safe minimum) around the full
  360° of the flywheel bay, chosen because a containment wall's job is to
  absorb and stop a fragment impact, not merely to keep dust out — sizing it
  at only the print-safe minimum would not reflect that different duty.
- The wall is a continuous ring with **no** access opening in the rotation
  plane at all (the only openings into the bay are the wire duct, well below
  the flywheel's own Z-range, and the flange-bolted cap on top) — a fragment
  radially ejected from the disk's rim has no direct line-of-sight exit path
  through the side wall.
- The cap is bolted (6× M3 into heat-set inserts, §12), not snap-fit or
  friction-fit, so it cannot be dislodged by the same impact event it is
  meant to contain.
- This is explicitly **not** a rigorously engineered ballistic-containment
  structure — no impact-energy-absorption calculation, no material-specific
  penetration-resistance analysis, and no dynamic (as opposed to static)
  structural check was performed; those are beyond this Phase 1 scope and
  this Mechanical Lead's own engineering authority to certify. What is
  claimed is a **reasoned, disclosed, defense-in-depth structural choice**
  — a continuous, bolted, over-minimum-thickness wall fully enclosing the
  rotation plane — not a rigorous containment certification.

**Independent Mechanical Review Cycle 3 verdict on this proposal, and
disposition (Rev 3.1):** the Reviewer's own verdict on this containment
proposal was explicitly **split** between its topology and its numbers.
**Topology — independently confirmed TRUE, unchanged by this rework:** the
continuous 360° wall with no rotation-plane opening, and the bolted
(not snap-fit) cap, were both confirmed as described above; nothing in this
subsection needed to change. **Numbers — NOT credible at Cycle 3 time,
because MISS-008 meant the flywheel did not fit the modeled envelope at
all:** the pre-fix `fw_disk_bottom` formula omitted `fw_hub_collar_h`,
producing a modeled disk that overlapped its own hub collar by ~145mm³ — a
containment envelope built around a disk position that could not physically
exist as drawn is not a credible envelope, regardless of how sound the
surrounding wall topology is. **This is now fixed:** `fw_disk_bottom` is
corrected (§4.4, §11.G), the whole downstream Z-stack has been re-derived
end-to-end (not left at pre-fix values), and the containment envelope's
actual current numbers are `fw_clearance_top`=45.0mm (was 39.0mm),
`fw_cap_outer_top`/`fw_bay_total_height`=49.0mm (was 43.0/43.0mm), with the
flange band and cap skirt's own Z-range shifting identically to [37.0,45.0]mm
(was [31.0,39.0]mm, §11.F). The `containment_wall_t`(4.0mm), the continuous-
ring topology, the 6×M3-into-heat-set-insert bolting, and the qualitative
(not load-calculated) fastener-adequacy judgment (MISS-011, see below) are
otherwise **unchanged** by this fix; only the Z-positions of the envelope
moved, not its wall thickness or fastening scheme.

**MISS-011 (MEDIUM, non-gating) — carried forward, not resolved this
revision:** the Reviewer separately noted that this section's own
`containment_wall_t`(4.0mm)/6×M3-fastener adequacy claim is qualitative
engineering judgment, not backed by an impact-energy-absorption or fastener
pull-out/shear calculation. This was already disclosed above ("no impact-
energy-absorption calculation... was performed") and in §12/§13/§16 before
Cycle 3 — the Reviewer's finding confirms the existing disclosure was
accurate, it does not add a new gap. Per the task scope for this rework,
this is explicitly **not** resolved this revision (that calculation is a
real, separate piece of engineering work, not a quick follow-on to the three
gating fixes above) — it remains an open, disclosed limitation.

**What this proposal is not:** it is not a claim that this design makes
flywheel operation "safe" in any certified sense, and it is not a substitute
for REQ-405 firmware speed-limiting eventually being implemented. It is one
specific, bounded engineering judgment, offered for Independent Mechanical
Review to challenge, and then for the human to accept, reject, or amend at
the REQ-403 HITL gate — exactly mirroring how the electronics-side REQ-403
disposition was handled (proposed → independently reviewed → human gate),
not a unilateral final decision by this Mechanical Lead.

**Rev 3.3 staleness flag for MISS-016 (HIGH, OPEN) — recompute performed in
Rev 3.4, see §8.1:** `validation/open-issues.md` MISS-016 (the
containment-wall energy-absorption shortfall) cites this document's own
§8.1.2 Method 1/Method 2 wall-impact estimates as its evidence. As of Rev
3.3 these were computed against the now-superseded 121.60 J / 69.74 m/s /
22,200 RPM
figures; Rev 3.3 itself flagged this as required follow-up, not performed
in that revision. **Rev 3.4 has since performed that recompute** — see
§8.1.2 for the full recomputed Method 1/Method 2 tables and reverse
cross-checks. Summary of what changed: Method 1 (was ~0.5–2.4% of budget,
now ≈0.03%–1.84%) and Method 2 (was ~30–40% of budget, now
≈1.7%–30.7%) shortfall percentages, and the "~2.5–3× short" / "1 to 3+
orders of magnitude short" conclusions (now precisely **≈3.26×–4.30× short
at best, ≈1.7–3.6 orders of magnitude short typically**), were all stale as
of Rev 3.3: they had been computed against an energy figure Rev 3.3 itself
showed to be ≈27.4–29.7% too low (point ≈28.65%). Because
the containment wall's energy-absorption capacity did not change (no
`.scad` geometry was touched in Rev 3.3 or Rev 3.4) while the demanded energy went
up, **MISS-016's shortfall widened, exactly as this flag predicted it
would — it did not narrow anywhere**, once §8.1 was recomputed against the
corrected ≈154.95–157.69 J
(point ≈156.44 J) figure in Rev 3.4. §15 item 6's existing "Rev 3.2 note"
(which
also quoted the same superseded 121.60J figure) was part of that same
follow-up and was updated together with §8.1 in Rev 3.4, to avoid partially
updating §8.1-dependent content piecemeal. `validation/open-issues.md`
itself is intentionally **not** updated by Rev 3.4 either (same scope
boundary as Rev 3.3) — the recomputed figures are reported back for the
Hardware Lead to fold into MISS-016's own row. (Incidental
citation note, not a defect requiring action: the task instruction that
prompted Rev 3.3 described MISS-016's Method 1/2 figures as living in
`bench-imu-01-manufacturing-spec.md` §8.1 — that file is untouched and is
not where MISS-016's analysis actually lives; MISS-016's real cited
evidence, per `validation/open-issues.md` line 89, is this same document's
own §8.1.2, consistent with how this flag is written.)

### 8.1 MISS-011 closure attempt: bounded wall-impact and fastener pull-out estimates (Rev 3.2, 2026-09-13; **numeric recompute against the corrected energy budget: Rev 3.4, 2026-09-13, MISS-016**)

**What this subsection is and is not.** MISS-011 (MEDIUM, non-gating, see
§12/§16 and `validation/open-issues.md`) flags that the 4.0mm
`containment_wall_t` / 6×M3 fastener adequacy judgment above is qualitative,
not backed by any impact-energy or pull-out calculation. Its own Recommended
Fix names two legitimate closure paths: (a) a basic impact-energy/
wall-deflection or fastener-pull-out-under-shock-load estimate, or (b)
explicitly carrying the qualitative-only status forward as a disclosed
limitation. Path (b) has already been satisfied since Rev 3.1 — this
subsection is a bounded attempt at path (a). It is **not** a certification,
**not** a FEA/simulation result, and **not** authority to change
`containment_wall_t`, the fastener count, or any other `.scad` geometry — no
`.scad` file was touched to produce this subsection. Every number below is
individually confidence-marked per `.github/instructions/mechanical-design.
instructions.md`; the full ledger is in §8.1.6.

**Tooling honesty, re-verified this session.** No CAD/3D/FEA MCP tool is
connected in this environment: `blender-get_addon_status` was called again
this session and returned "Could not connect to Blender," matching every
prior check in this project. No local `openscad` Python-scriptable solid-
modeling library, `cadquery`, `build123d`, or FEA solver is available either.
This subsection is therefore hand-derived closed-form engineering estimation
(energy-density scaling and yield-limited work, both textbook-level, not
FEA), exactly as the task scoped it — `CONFIRMED` (tool-absence re-verified
2026-09-13, mirrors every earlier check in this document and in
`hardware/mechanical/bench-imu-01-manufacturing-spec.md`).

#### 8.1.1 Threat-model framing used for this estimate

§8 above already establishes the load case: **the entire 100g disk
detaching as one rigid projectile** (line ~621), at up to 156.44J of stored
rotational kinetic energy (≈25,180 RPM credible-worst-case, point estimate;
range ≈154.95–157.69J across 25,060–25,280 RPM — **Rev 3.4**, supersedes the
old 121.60J/22,200-RPM-no-load-high figure per §8's own Rev 3.3 correction),
not a small fragment. As an independent sanity check before relying on this
figure further, it was re-derived from first principles rather than copied:
for a solid disk, KE_rotational = ¼·m·v_rim² (equivalent to ½Iω² with
I=½mr²). Using the disclosed m=0.100kg, v_rim=79.11 m/s: ¼×0.100×79.11² =
**156.46 J**, and I=½×0.100×0.030² = **4.5×10⁻⁵ kg·m²** — both reproduce
the existing table's figures (§8, "The physics" table, Rev 3.3) to rounding,
the same way the superseded 69.74 m/s check reproduced the old 121.60J
figure to rounding. `CONFIRMED` (independently re-derived, matches existing
document; re-verified this cycle against the Rev 3.3-corrected inputs —
**Rev 3.4**, mass/radius/I unchanged, only the RPM-derived rim speed and
resulting energy actually moved).

Because the flywheel's rotation axis is vertical (Z) and `fw_bay_wall()` is
the cylindrical wall surrounding the disk radially, the disk's **rim/edge**
faces this wall — a radial-ejection event striking `fw_bay_wall()` is
naturally an edge-on (rim-first) impact against that wall, not a flat/
broadside one (a flat/broadside impact would instead load the axial
surfaces — `base()` below and `containment_cap()` above — a materially
different scenario already reflected in `bench-imu-01-manufacturing-spec.md`
treating `fw_bay_wall()` as the **primary** containment surface for radial
ejection and `containment_cap()` as **secondary/backup**. `CONFIRMED`
(geometric fact from the `.scad` axis/wall layout) feeding an `ASSUMPTION`
(edge-on is the representative failure geometry modeled here, not a
guarantee no other release geometry is possible).

#### 8.1.2 Wall impact / penetration estimate

**Method 1 — notched-impact (Charpy) energy-density scaling.** Treats the
wall as absorbing energy only through fracture toughness across a local
punch-through area: `E_frac[J] = specific_toughness[kJ/m²] ×
(containment_wall_t[mm] × w[mm]) / 1000`, where `w` is an assumed
characteristic engagement length (the punch-through crack front's real
combined axial+circumferential geometry is a fracture-mechanics detail
beyond this bounded estimate — `w` is swept across a physically-anchored
range rather than picked as one number). Lower anchor `w`=4.5mm = the
disk's own thickness (`fw_t`, `ASSUMPTION` — §4.1 disk row; `.scad` line 178
agrees) — the minimum a clean edge-on hit engages. Upper anchor `w`=60mm =
the disk's own diameter (`fw_dia`, `ASSUMPTION` — §4.4 line 404; `.scad`
line 177 agrees) — a generous stand-in for a smeared/tumbling/
multi-contact worst case. Material figures used (`ESTIMATE`-applicability,
`CONFIRMED`-as-published — see §8.1.6):

| Material (source) | Notched Charpy | Provenance |
|---|---|---|
| PETG, Prusament (DS-MTL-001) | ~6 kJ/m² (X-Y) / ~3 kJ/m² (Z) | AI-search-summary; PDF URL confirmed live, content unparsed |
| PETG, Polymaker PolyMax (DS-MTL-002) | 11.6±0.8 kJ/m² (X-Y) / 2.4±0.6 kJ/m² (Z) | Directly fetched & read HTML TDS table |
| Nylon PA12, Fiberlogy (DS-MTL-003) | ~12 kJ/m² | AI-search-summary; PDF URL confirmed live, content unparsed |

**Rev 3.4 — recomputed against the corrected 156.44J denominator, same
material Charpy figures (material properties don't change), same
engagement-length sweep.** The absolute E_frac joule figures below are
therefore **unchanged** from Rev 3.2/3.3 — only the "% of budget" column
moves, because the budget itself grew:

| Engagement `w` | Area (t×w) | E_frac range (all materials above) | % of 156.44J |
|---|---|---|---|
| 4.5mm (disk thickness) | 18.0mm² | 0.043–0.216 J | 0.028%–0.14% |
| 15mm | 60.0mm² | 0.144–0.720 J | 0.092%–0.46% |
| 30mm (disk radius) | 120.0mm² | 0.288–1.440 J | 0.18%–0.92% |
| 60mm (disk diameter) | 240.0mm² | 0.576–2.880 J | 0.37%–1.84% |

(Was, against the superseded 121.60J: 0.036%–0.18% / 0.12%–0.59% /
0.24%–1.18% / 0.47%–2.37% respectively — every figure moved down, because a
larger, unchanged-numerator-over-larger-denominator fraction is smaller, not
because the wall got any better at absorbing energy.)

Reverse cross-check — engagement length needed to consume the *entire*
156.44J via fracture toughness alone, at a fixed 4.0mm depth: **3,259–16,296mm**
(was 2,533–12,667mm against the superseded 121.60J), i.e. **1,313%–6,566% of
the wall's own full inner circumference (248.19mm, `DERIVED` from
`fw_bay_inner_r`=39.5mm, §4.4 line 410; `.scad` line 467
agrees)** — was 1,021%–5,104% — several times all the way around the
wall, now more times than before. This is not a physically meaningful
"localized puncture," it is a mathematical statement that
fracture-toughness-only absorption cannot come close to the disclosed
energy at any localized footprint — and comes even less close than
previously computed, now that the energy denominator is larger and the
wall's own absorption capacity has not changed. `ESTIMATE` (method + range),
arithmetic itself `CONFIRMED` by direct computation (**Rev 3.4** recompute).

**Method 2 — yield-strength-limited local plastic work.** Treats the wall
as absorbing energy through plastic deformation up to its own thickness
before local failure: `E_abs[J] = yield[MPa] × (t×w) × δ[mm] / 1000`, with
deformation depth δ optimistically bounded at the full 4.0mm wall thickness
(i.e. assumes the material can plastically work through its *entire* depth
before losing containment — a generous assumption in the design's favor).

| Material (source) | Tensile yield | Provenance |
|---|---|---|
| PETG, Prusament (DS-MTL-001) | ~46–50 MPa | AI-search-summary |
| PETG, measured (DS-FAST-002, CNC Kitchen) | ~50 MPa | Directly fetched & read (cross-validates Prusament) |
| PETG, Polymaker PolyMax X-Y (DS-MTL-002) | 37.9±1.4 MPa | Directly fetched & read HTML TDS table |
| Nylon PA12, Fiberlogy (DS-MTL-003) | ~45 MPa | AI-search-summary |

**Rev 3.4 — recomputed against the corrected 156.44J denominator, same
tensile-yield figures.** The absolute E_abs joule figures are **unchanged**
from Rev 3.2/3.3 — only the "% of budget" column moves:

| Engagement `w` | Area (t×w) | E_abs range | % of 156.44J |
|---|---|---|---|
| 4.5mm | 18.0mm² | 2.73–3.60 J | 1.7%–2.3% |
| 15mm | 60.0mm² | 9.10–12.00 J | 5.8%–7.7% |
| 30mm | 120.0mm² | 18.19–24.00 J | 11.6%–15.3% |
| 60mm (disk diameter) | 240.0mm² | 36.38–48.00 J | **23.3%–30.7%** |

(Was, against the superseded 121.60J: 2.2%–3.0% / 7.5%–9.9% / 15.0%–19.7% /
**29.9%–39.5%** respectively.)

Reverse cross-check — engagement length needed at δ=4.0mm to consume the
*entire* 156.44J: **196–258mm** depending on material (was 152–201mm
against the superseded 121.60J), i.e. **79%–104% of the wall's full
circumference** would need to plastically yield through its whole thickness
simultaneously (was **61%–81%**) — the upper bound now *exceeds* the wall's
entire circumference (104% > 100%), a new qualitative fact: even wrapping
the assumed-full-depth plastic-yield zone all the way around the wall's
entire inner circumference would not, at the lower-yield-strength material
bound, be enough to consume the corrected energy budget. `ESTIMATE` (method
+ range), arithmetic `CONFIRMED` by direct computation (**Rev 3.4**
recompute).

**Real-world intuition comparable.** A regulation baseball (0.145kg) at
40 m/s (~144 km/h, a hard-thrown pitch) carries 116.0J. Against the
corrected 156.44J budget this is now only **≈74% of the disclosed energy**
(**Rev 3.4** — was "within 5%" of the superseded 121.60J figure, i.e.
≈95.4%): the credible-worst-case release is now appreciably more energetic
than a single hard-thrown pitch, roughly **1.35×** a baseball pitch's energy,
not a near-match to one. A person would not casually assume a 4mm plastic
wall reliably stops an impact more energetic than a hard-thrown baseball
without testing; this is offered as an intuition check, not a calculation.
`ESTIMATE` (illustrative only).

**Caveats — three simplifications, not all pointing the same direction:**
1. *High strain rate (non-conservative bias):* the cited Charpy/tensile
   figures are quasi-static or low-rate test data. Most thermoplastics
   (PETG and PA12 included) trend toward **lower** toughness / more
   brittle behavior at high strain rates, and this containment event
   (≈79.11 m/s rim speed, **Rev 3.4** — was 69.74 m/s) is a far higher rate
   than any standard Charpy or tensile test. Real performance is plausibly
   **worse** than modeled here. `ASSUMPTION` (directional, not quantified —
   no high-rate data located for these specific materials).
2. *FDM print vs. TDS coupon (non-conservative bias):* the cited figures
   are manufacturer TDS values, generally measured on well-controlled
   (often injection-molded or ideally-printed) specimens — not
   necessarily this project's own eventual print run. `bench-imu-01-
   manufacturing-spec.md` already documents this gap in detail (6-
   perimeter/100%-infill recommendations exist specifically because a
   real print can otherwise underperform bulk material figures). Real
   performance is plausibly **worse** than modeled here, compounding
   caveat 1. `ASSUMPTION`.
3. *Impact angle, small-fragment sub-case only (conservative bias):* for
   a small rim fragment released tangentially (not the whole-disk case
   above) and traveling in a straight line to the wall, basic tangent-
   geometry gives an impact angle of asin(30mm/39.5mm) ≈ **49.4° from the
   wall's local normal** — an oblique, not square, hit. An oblique hit
   delivers a smaller normal (penetrating) energy fraction than a square
   hit; Methods 1–2 above assume a square hit throughout, so are
   plausibly **conservative** (pessimistic) relative to this specific
   sub-case. This is illustrative geometry for one simplified sub-case,
   not a correction factor applied to the whole-disk numbers above.
   `ESTIMATE` (exact trigonometry given the stated simplifying
   assumptions; the assumptions themselves are simplifications).

**Verdict — wall (Rev 3.4, recomputed against the corrected 156.44J
budget).** Across both methods and the full physically-anchored
engagement-length sweep, local-material energy absorption accounts for
**well under half of the disclosed 156.44J even in the most generous
plausible case** (Method 2, 60mm engagement: ≈23.3%–30.7%, was ≈29.9%–39.5%;
Method 1 at the same engagement: under ≈1.9%, was under 2.5%) — if anything
a *stronger* "well under half" than before, since the same fixed absorption
capacity is now a smaller fraction of a larger budget. The most favorable
defensible number these methods support is now **precisely ≈3.26×–4.30×
short of the full budget** (Method 2, largest engagement; was ≈2.53×–3.34×,
described loosely as "~2.5–3×" against the superseded figure — the
shortfall widened, as expected, it did not narrow); more typical/localized
engagement assumptions or fracture-toughness-only reasoning put the
shortfall at **≈54×–3,621× (≈1.7 to ≈3.6 orders of
magnitude)** — was ≈42×–2,778× (≈1.6 to ≈3.4 orders). The
qualitative conclusion is unchanged in kind — "well under half," "several
times short at best, orders of magnitude short typically" — but every
underlying number moved in the worse direction, precisely as the larger,
corrected energy denominator against an unchanged absorption capacity
requires; none of it narrowed. This does not prove the
wall fails outright — global structural response (does the whole ring
flex/redirect the impact rather than a small zone absorbing it locally?),
strain-rate-specific data, and the actual as-printed material properties
are all outside what a closed-form estimate can capture, and caveat 3 above
points the other way for one specific sub-case. But it does **not support
an affirmative "4.0mm is adequate" claim** either — now less so than before.
**This is flagged separately to the Hardware Lead in §8.1.6 — it is not
resolved by this subsection and no geometry has been changed.**

#### 8.1.3 Fastener pull-out estimate

**Single-insert pull-out capacity.** Real, checkable published/measured
data for M3 brass heat-set inserts in PETG-class plastic (dimensions
matching this design's assumed `heatset_od`=4.6mm/`heatset_len`=5.7mm,
`ASSUMPTION` — §4.4 line 418; `.scad` lines 485/489 agree — closely
matching the real Ruthex RX-M3x5.7 part, DS-FAST-001):

| Source | Insert / plastic | Pull-out (avg) | Provenance |
|---|---|---|---|
| CNC Kitchen (DS-FAST-002) | Ruthex M3 heat-set, PETG | ≈119 kg ≈ **1,167 N** (n=3) | Directly fetched & read primary source |
| CNC Kitchen (DS-FAST-002) | Direct-thread-into-PETG (no insert) | ≈1,157 N | Same article, same read |
| CNC Kitchen (DS-FAST-002) | Heli-coil, PETG | ≈1,177 N | Same article, same read |
| Sculpteo guide (DS-FAST-003) | M3-class insert, MJF PA12 | ≈1,258 N | AI-search-summary; page fetched, table not renderable |

A conservative round figure of **1,000 N per insert** is used below
(below all four cited values, so it does not cherry-pick the best case).
`CONFIRMED` (as published/measured for the cited real products); `ASSUMPTION`
for applicability (this project has not finalized its actual insert brand
or print material).

**6-insert capacity scenarios** (`n_cap_bolts`=6, `ESTIMATE` — §4.4 line 417;
`.scad` line 481):

| Load-sharing assumption | Total capacity | Basis |
|---|---|---|
| Ideal / even sharing across all 6 | 6,000 N | `ASSUMPTION` (no data on real sharing efficiency for this joint) |
| Reduced / ~3-bolt-effective (uneven load, cap flex) | 3,000 N | `ASSUMPTION` (engineering judgment, not a citation) |
| Pessimistic / ~2-bolt-effective | 2,000 N | `ASSUMPTION` (engineering judgment, not a citation) |

**Load-path reasoning.** `bench-imu-01-manufacturing-spec.md` establishes
`fw_bay_wall()` as the **primary** containment surface for radial ejection
and `containment_cap()` as **secondary/backup** (its skirt is only 2.0mm vs.
the wall's 4.0mm, §8 above). This means the cap's fasteners are not the
first line of defense against a direct radial hit — their realistic loading
scenario is an **attenuated** one: whatever residual energy/force reaches
the cap joint after the primary wall has already engaged (deflected,
locally absorbed, or redirected) some fraction of the event, not
necessarily the full undiminished 156.44J (**Rev 3.4** — was 121.60J).
Quantifying that attenuation
fraction precisely would require a multi-body impact simulation this
environment cannot run — `UNKNOWN` (not estimated further here) — but
qualitatively, **any** realistic secondary/attenuated load is smaller than
the full-direct-hit hypothetical below, so the fastener margin is better
than the worst-case framing suggests.

**Force vs. assumed stopping/crush distance** (work-energy, `F = E/δ`,
deliberately pessimistic hypothetical: full 156.44J applied directly to the
cap joint alone, ignoring any wall attenuation; **Rev 3.4** — recomputed
against the corrected budget, was 121.60J):

| Assumed stopping distance δ | Required force F | vs. 6,000N ideal | vs. 3,000N reduced |
|---|---|---|---|
| 1 mm (near-rigid stop) | 156,440 N | 26.1× over | 52.1× over |
| 5 mm | 31,288 N | 5.21× over | 10.4× over |
| 20 mm | 7,822 N | 1.30× over | 2.61× over |
| 50 mm | 3,129 N | 0.52× (within capacity) | **1.04× over** |
| 100 mm | 1,564 N | 0.26× (within capacity) | 0.52× (within capacity) |

(Was, against the superseded 121.60J: 121,600N/20.3×/40.5× (1mm);
24,320N/4.05×/8.1× (5mm); 6,080N/~1.01×(break-even≈20.3mm)/2.03× (20mm);
2,432N/0.41×/0.81× (50mm); 1,216N/0.20×/0.41× (100mm).)

New break-even points (ratio = 1.0×): **≈26.1mm** for the 6,000N
ideal-sharing capacity (was ≈20.3mm); **≈52.1mm** for the 3,000N
reduced-sharing capacity (was ≈40.5mm — not previously called out as a
named break-even in this table because the 50mm row still cleared it).
**New qualitative finding, not present at the superseded energy figure:**
at the previously-assumed 50mm stopping distance, the 3,000N-reduced
scenario is now marginally **over** capacity (≈1.04×) rather than within it
(was ≈0.81×, within capacity) — the 6,000N-ideal scenario remains within
capacity at 50mm (≈0.52×, was ≈0.41×).

`δ` (assumed stopping/crush distance) is genuinely `UNKNOWN` without
physical testing or FEA — swept rather than asserted. `ESTIMATE` (method +
range); arithmetic `CONFIRMED` by direct computation.

**Verdict — fasteners (Rev 3.4, recomputed against the corrected 156.44J
budget).** For the deliberately pessimistic full-direct-hit
hypothetical, 6×M3 capacity (ideal sharing) is adequate only if the joint
can give/crush over ≳26mm before failing (was ≳20mm) — plausible for a joint
with some
give (o-ring/gasket compliance, local plastic deformation of the cap or
skirt) but not `CONFIRMED`. For the **realistic, attenuated secondary-role
loading** the load-path reasoning above supports, the margin is
meaningfully better than this worst-case framing, because the actual force
reaching the cap joint is very likely smaller than the full 156.44J
hypothetical. Unlike the wall estimate (short by ≈3.26×–4.30× at best to
≈54×–3,621× more typically, across all engagement assumptions — was ~2.5×
to orders of magnitude), the fastener estimate is
**plausible for its realistic/secondary loading role**, and only
**marginal-to-inadequate for a hypothetical, pessimistic full-direct-hit
scenario that the cap is not actually designed to be the primary defense
against** — the required crush distance for adequacy under that
hypothetical grew (≳20mm→≳26mm for the ideal-sharing case), and the
3,000N-reduced-sharing case now turns marginally inadequate at a
previously-comfortable 50mm crush distance, both consistent with a larger,
unchanged-capacity-against-larger-demand shortfall, not a narrower one.

#### 8.1.4 Confidence ledger

| Item | Value(s) | Confidence |
|---|---|---|
| Disk mass, diameter, thickness, rim speed, stored energy | 100g / 60.0mm / 4.5mm / 79.11 m/s / 156.44J (**Rev 3.4**, was 69.74 m/s / 121.60J) | `ESTIMATE` (mass — §4.1 total-mass row) / `ASSUMPTION` (diameter `fw_dia` — §4.4 line 404) / `ASSUMPTION` (thickness `fw_t` — §4.1 disk row) / `ESTIMATE` (rim speed — derived from the two `ASSUMPTION` values at left) / `ESTIMATE` (stored energy — derived from mass+diameter); the re-derivation arithmetic itself is `CONFIRMED` to match §8's own Rev-3.3-corrected table (§8.1.1) |
| `containment_wall_t`, `fw_bay_inner_r`, wall height | 4.0mm / 39.5mm / 43.0mm | `ESTIMATE` (`containment_wall_t` — §4.4 line 411) / `DERIVED` (`fw_bay_inner_r` — §4.4 line 410; `.scad` line 467 agrees) / `DERIVED` (wall height `fw_wall_h` — computed from other `DERIVED` Z-stack values, §4.4) |
| Heat-set insert dimensions, bolt count | 4.6mm OD / 5.7mm len / 6× M3 | `ASSUMPTION` (insert OD/len — §4.4 line 418; `.scad` lines 485/489 agree) / `ESTIMATE` (bolt count — §4.4 line 417) |
| Charpy/tensile figures as published (per material) | see §8.1.2 tables | `CONFIRMED`-as-published; `ASSUMPTION`-applicability (final print material/brand not yet chosen) |
| Insert pull-out figures as published/measured | 1,157–1,258 N range, 1,000N used | `CONFIRMED`-as-published/measured; `ASSUMPTION`-applicability |
| Engagement length `w`, deformation depth δ, stopping distance δ (fastener) | swept ranges, §8.1.2/§8.1.3 | `UNKNOWN` (true values need physical testing/FEA) — swept, not asserted |
| 6-bolt load-sharing efficiency (ideal/reduced/pessimistic) | 6,000 / 3,000 / 2,000 N | `ASSUMPTION` (engineering judgment, no citation) |
| Cap-joint attenuation fraction vs. full direct hit | not quantified | `UNKNOWN` (qualitative reasoning only, needs multi-body simulation to bound) |
| High-strain-rate and FDM-vs-TDS-coupon directional bias | non-conservative (real performance likely worse) | `ASSUMPTION` (directional, not quantified) |
| Oblique-impact-angle directional bias (small-fragment sub-case) | conservative (real performance for that sub-case likely better) | `ESTIMATE` (exact geometry given stated simplifications) |
| Overall wall verdict | short by ≈3.26×–4.30× (best case) to ≈54×–3,621× / ≈1.7–3.6 orders of magnitude (typical) — **Rev 3.4**, was ~2.5× / 1–3+ orders | `ESTIMATE` (engineering judgment, not a pass/fail certification) |
| Overall fastener verdict | plausible for realistic/secondary role; marginal-to-inadequate for hypothetical full-direct-hit | `ESTIMATE` (engineering judgment, not a pass/fail certification) |

#### 8.1.5 Tooling honesty — what this could not do

No physical testing and no FEA/simulation tool exists in this environment
(re-confirmed §8.1 opening). This means: no actual stress concentration,
dynamic/high-rate material response, global structural (whole-ring)
response, real print-quality effect, or multi-body cap-attenuation
fraction could be computed — only closed-form, textbook-level estimates
bounded by sensitivity sweeps. This mirrors the Manufacturing Engineer's
own honest "cannot certify without physical testing" conclusion in
`bench-imu-01-manufacturing-spec.md` — this subsection reaches the same
kind of honest, bounded (not falsely precise) conclusion for the mechanical
side specifically, rather than forcing an unsupported pass/fail number.

#### 8.1.6 Escalation flag for the Hardware Lead (distinct from MISS-011)

**This is a new finding, separate from MISS-011's own closure, and this
Mechanical Lead has NOT changed any `.scad` geometry in response to it —
per this task's explicit scope, that decision belongs to the Hardware
Lead / human, not to this agent unilaterally.** §8.1.2's wall estimate
does not support an affirmative "4.0mm containment_wall_t is adequate for
the disclosed 156.44J load case" claim under either estimation method
(**Rev 3.4** — recomputed against the corrected budget; was 121.60J),
across the full physically-anchored engagement-length range — the best
defensible case is now precisely ≈3.26×–4.30× short of the full energy
budget (was ≈2.5–3×), and
more typical assumptions put the shortfall at ≈1.7 to ≈3.6 orders of
magnitude (was one to several orders of magnitude). The shortfall widened
across the board, consistent with an unchanged absorption capacity measured
against a larger, corrected energy denominator — it did not narrow at any
engagement length or by either method. This does not prove the wall fails (see caveats and limits
in §8.1.2/§8.1.5), and it does not change the existing REQ-403 disposition
above (containment is still better than no containment, and this was
already an explicitly non-certified, human-gated proposal). It is raised
here so the Hardware Lead can decide, with the human, whether this
warrants: (a) proceeding as-is with this margin now disclosed
quantitatively rather than only qualitatively, (b) commissioning actual
physical drop/impact testing before relying on this design for powered
operation above a certain speed, or (c) revisiting `containment_wall_t`
or the containment topology — a decision this Mechanical Lead is
deliberately not making unilaterally.

#### 8.1.7 Disposition and handoff

This subsection is a **proposed, bounded engineering estimate**, offered
for Independent Mechanical Review to challenge — it is not self-certified
or self-resolved. Per the same convention used throughout this project
(no discipline closes its own reviewer-sourced finding), **MISS-011's
Status remains OPEN**; `validation/open-issues.md` is updated only to
note that a defensible estimate now exists and is proposed as ready for
the Mechanical Reviewer's independent cross-check (see also §8.1.6's
distinct escalation, which is a new item for the Hardware Lead, not part
of MISS-011 itself).

---

## 9. Vibration isolation / REQ-307 disposition

REQ-307 is explicitly a "Should," not a "Must" ("where feasible"), citing
`docs/architecture.md` §12's own framing: a rotating body such as a reaction
wheel motor creates vibration and localized heating that can propagate into
the PCB, mattering especially for vibration/temperature-sensitive parts like
an IMU (bias drift with temperature).

**Disposition: not fully feasible within this design's own constraints; a
partial/incidental mitigation is provided instead, with the gap disclosed
rather than silently accepted.**

Reasoning: true vibration isolation (an elastomeric mount, a spring-damped
suspension, or a physically decoupled sub-chassis for the IMU) is a
mechanism/joint-class solution — explicitly out of Phase 1 scope
(`docs/architecture-evolution.md` §10, "Motion / joints... deferred"). Adding
one now would mean either (a) designing a genuinely new mechanical subsystem
not asked for in this cycle's scope, or (b) inventing a token isolation
feature (e.g., a foam gasket under the PCB standoffs) without any real
vibration-transmissibility analysis to show it does anything — which this
project's own rigor culture (disclosed-not-absorbed findings, e.g. the
bridge-span finding in §11) argues against presenting as a real mitigation
if it is not backed by analysis.

What this design **does** provide, as an incidental (not purpose-built)
partial mitigation:
- The motor is off-board-mounted (§6) to its own platform, physically
  separated from the PCB by the flywheel-bay wall (`containment_wall_t`=4.0mm)
  and the full width of the wire duct's own run — the vibration source is
  not bolted directly to the same rigid structure the IMU sits on within a
  few millimeters, the way an on-PCB motor mount would have been.
- MH-5/MH-6 (the two new mounting holes near the motor-driver zone) increase
  the board's own fixation near the switching/driver components, which
  reduces board-level flex/resonance that could otherwise couple motor-driver
  electrical noise or minor vibration into the board more readily — a board
  rigidity benefit, not a true vibration-isolation feature.
- The flywheel bay and PCB bay are joined only through a rigid enclosure
  base — there is no isolation in this path, so both spatial separation and
  MH-5/6 rigidity are genuinely partial, not equivalent to an isolated mount.

This is judged an honest "not fully feasible, here is the disclosed
alternative" outcome consistent with REQ-307's own "Should"/"where feasible"
framing — not a claim that vibration coupling has been solved. If IMU bias
drift is observed during actual bring-up, a purpose-built isolation mount
would be the correct follow-up (a future revision's scope, not silently
folded into this one).

---

## 10. Connector / header / button / LED / motor-wiring accessibility

| Ref | Board-local position | Cutout | Confidence | Note |
|---|---|---|---|---|
| J1 | (0,25) | 9.5×6mm, Z 0–6mm | CONFIRMED | Unchanged from Rev 2 |
| J2 | (16,50) | pass-through header, no dedicated cutout beyond the bay opening | CONFIRMED | Unchanged from Rev 2 |
| J3 | (30,50) | pass-through header | CONFIRMED | Unchanged from Rev 2 |
| SW1 | (44,50) | accessible through bay opening | CONFIRMED | Unchanged from Rev 2 |
| D1 | (10,37.5) | visible through bay opening | CONFIRMED | Y-position rescaled from Rev 2's 30mm |
| J4 | (100,25), edge | ⌀10.0mm, Z 0–6mm | ESTIMATE (diameter) | New in Rev 3; position confirmed, diameter is this Mechanical Lead's own estimate |
| MC-1 | (92,0), bottom edge | No dedicated board-edge cutout modeled — wire exits the board at this point and is routed internally to the wire duct | CONFIRMED (position) | New in Rev 3; wire-lead, not a component footprint |

**The wire-routing disclosure (important, not to be glossed over):** the
flywheel bay's own wire duct is centered at `fw_cx`=53.5mm — the PCB's own
X-midpoint — because the flywheel bay's own layout was centered on the PCB
bay's width for a cleaner, narrower overall footprint (§3, the "master XY
layout trade-off," `.scad` lines 497–519). MC-1's actual proposed board
position is X=92mm. This means the wire duct's exit point does **not** land
directly under or adjacent to MC-1 — there is a real ~42mm X-offset between
where the motor's wire pigtail enters the enclosure interior (at the duct)
and where it must connect on the board (at MC-1). The wire must run along
the interior floor for that distance. This was a deliberate, disclosed
trade-off (a width-centered flywheel bay vs. a motor-zone-centroid-aligned
one, which would have produced a wider but shorter overall footprint,
closer to 140×160mm-class rather than 107×162mm) — not an oversight. No
routing channel/clip is modeled for this 42mm run (out of the detailed
cable-exit-geometry scope this project has explicitly deferred,
`docs/architecture-evolution.md` §13) — the wire is expected to simply lie
along the interior floor, which is judged acceptable for a low-wire-count,
low-flex, bench-test-only pigtail, but is flagged here as a real, not
idealized, condition.

**Component-height clearance check (unchanged mechanism from Rev 2):**
`top_component_clearance`=11mm (driven by J4, the tallest top-side part per
the interface file) sets `base_interior_h` via the same formula Rev 2 used;
`bottom_component_clearance`=0mm means no standoff-height allowance is needed
beyond the base standoff height itself.

---

## 11. Computed clearance checks

This section is the full, disclosed record of every interference/clearance
check performed this revision — real arithmetic and, where noted, real
boolean-mesh intersection tests, not visual inspection.

**A. Four errors found and fixed during this revision's own development:**

1. **Error #1 & #2** (early-stage, minor coordinate-formula errors caught
   before the design stabilized — superseded by later constants, not
   independently re-describable at this point; see the `.scad` file's own
   revision history in-code if a full audit trail is needed).
2. **Error #3 — wire-bridge/motor collision.** Root cause: `bridge_y_lo` was
   computed from the flywheel bay's own **center** (`fw_cy`=52.5mm) instead
   of its **wall's outer edge**. This produced a bridge spanning 54.5mm,
   running directly through the motor platform and motor body. Fix:
   introduced `bridge_fuse_overlap`=2.0mm and recomputed `bridge_y_lo` =
   `fw_cy` + `fw_bay_outer_r` − `bridge_fuse_overlap` = 52.5+43.5−2.0 = 94.0mm.
   New span: 13.0mm. Verified clearance after fix: 26mm to the motor
   platform, 28mm to the motor body — both confirmed via direct coordinate
   check, not just "it looks fixed."
3. **Error #4 — missing flywheel-bay floor (most severe finding this
   revision).** Root cause: `fw_floor_top` (Z=2.0mm) was referenced
   throughout the file as if a floor disc existed at that height inside the
   flywheel bay, but no code actually created that geometry — the bay's
   containment wall had **no bottom** at all. Fix: `motor_platform()` now
   unions a full floor disc (radius=`fw_bay_outer_r`=43.5mm, Z=[0,2.0]) with
   the raised platform boss, before differencing the 4 bolt holes and the
   shaft hole through the combined solid. **This was the single most
   safety-relevant catch of this revision** — an unfixed version would have
   left the containment structure's own floor open, directly defeating
   REQ-403's entire premise (a fragment could simply fall out the bottom).
   Verified fixed via direct render (Status: NoError, no open non-manifold
   edges at the floor/wall junction).

**B. Two findings investigated and correctly dismissed as false alarms
(verified using a same-check-against-Rev-2's-own-already-reviewed-file
baseline method, not just re-running the check once and hoping):**

1. `trimesh`'s naive connected-components check reported ~12–13 exact-zero-
   volume "extra components" on `base()`, which could look like a defect.
   Running the identical check against Rev 2's own already-reviewed
   `base()` produced the same pattern (same count class), confirming this is
   a known STL-tessellation artifact at tab corners (CGAL/OpenSCAD's own
   manifold check reports Status: NoError regardless), not a Rev 3-specific
   defect.
2. A "2-vs-3-component assembly split" finding (an ambiguous result from a
   naive whole-assembly connectivity check) was similarly reproduced on Rev
   2's own file pattern and dismissed as a benign artifact of the same
   tessellation quirk, not a genuine assembly defect.

**C. One pre-existing Rev 2 issue found and confirmed in Rev 3 — flagged,
not fixed, at Rev 3 authoring time; fixed in this Rev 3.1 rework:**

A genuine, non-zero **190.06mm³ solid-solid overlap** exists between
`base_tabs()` and `lid_shell()`, confirmed via direct boolean intersection
(not estimation). Root cause, worked through geometrically: each of the 4
corner tabs projects outward (`tab_project`=6.0mm) starting flush at the
base wall's own outer face (zero gap by design — the tab is meant to be a
continuous extension of the wall). The lid's own skirt band (`lid_skirt_t`
=2.0mm thick) independently occupies the zone starting `fit_clearance`
(0.2mm) beyond that same wall face and extending `lid_skirt_t` further out —
i.e., the skirt band's Y-extent (2.0mm) is a subset of the tab's own
6.0mm outward projection, over the Z-range where the lid's skirt physically
overlaps the base wall (3.0mm of Z, `lid_lip_h`). This produces a real
solid-on-solid interference at all 4 corners, each contributing
approximately 47–48mm³ (8mm tab width × 2.0mm Y-overlap × 3.0mm Z-overlap,
minus a small pilot-hole deduction), summing to the reported 190.06mm³ —
this hand-recomputation (188–192mm³ range) closely matches the actual
measured figure, confirming the mechanism. **This is confirmed, via direct
Rev-2-baseline testing, to be a pre-existing characteristic of Rev 2's own
already-reviewed tab+skirt joint design** (neither `tab_project`,
`lid_skirt_t`, nor `fit_clearance` changed between revisions) — inherited
unchanged into Rev 3, not introduced by this revision. Original (Rev 3)
decision: **flag, do not fix**, per that task's explicit scope boundary
(that task was a mechanical redesign for the new motor/flywheel subsystem,
not a Rev 2 defect-remediation pass). Qualitative mitigating judgment (not a
rigorous proof) offered at the time: the tab's actual structural job is
served by its own screw pilot hole engaging the base's standoff-equivalent
boss beneath the lid — the redundant contact with the lid's skirt band at
this corner is unlikely to be the governing load path, so the real-world
severity of this interference was judged low, but it was not analyzed
rigorously and was not claimed to be harmless in a stronger sense than
"probably fine, undisturbed since Rev 2."

**Update, Rev 3.1 (MISS-010, HIGH — Independent Mechanical Review Cycle 3):**
the Reviewer independently re-confirmed this exact interference still
present in Rev 3, and judged it **in-scope for this cycle** (unlike the
original Rev 3 task's own scope boundary) since this geometry was already
being reworked for MISS-008/009. **Fixed:** a new `tab_relief_margin`
(1.0mm) variable and a relief-notch cut into `lid_shell()`'s skirt band at
each of the 4 `tab_positions` — sized `tab_w`+2×`fit_clearance` (8.4mm) in
X and `lid_skirt_t`+2×`tab_relief_margin` (4.0mm) in Y, capped in Z at
exactly `lid_lip_h` with a 1.0mm overshoot below Z=0 only (so the fix never
intrudes into the roof above each tab). Verified empirically: a fresh
`intersection()` of `base_tabs()` and `lid_shell()` returns a mesh whose
`trimesh`-computed volume is exactly **0.0mm³** (the only remaining vertices
sit on a single flush Z-plane at the tab-top/lid-underside mating face — a
benign coincident-face artifact, not residual overlap; cross-checked against
vertex-coordinate spread, not just OpenSCAD's own non-empty top-level report
of the intersection). An 8-point containment sweep (2 X-offset probes per
corner, avoiding each tab's own 1mm-radius pilot hole) confirms genuinely
solid tab material and a genuinely open notch at all 4 corners. Negative
controls confirm the skirt band remains intact at clean mid-span perimeter
points (just outside each new notch) and that the roof directly above each
tab is untouched (no over-cutting). See §4.2 (`tab_relief_margin` row) and
§11.G below for the full record.

**D. One new finding, first identified this session (borderline but
compliant — disclosed, not requiring a fix):**

The motor-wire bridge's unsupported horizontal print-bridging span was
computed exactly: at the bridge's X-center (53.5mm), the span from the
flywheel-bay wall/floor-disc's own outer edge (Y=96.000) to the PCB bay's
south wall face (Y=105.0) is **9.000mm**; at the bridge's two X-edges
(47.5mm/59.5mm), the span (measured from the floor disc's curved edge at
those X-offsets, Y=95.584) is **9.416mm**. Both are within the stated
`max_bridge_span`=10.0mm rule, but at 90.0–94.2% of it — directly analogous
to Rev 2's own disclosed (and accepted) J1-cutout bridge, which sat at
9.5mm/95% of the same limit. Additionally, the wire-duct bore's surrounding
wall thickness inside the bridge block is 3.5mm on each side in X
(comfortable margin above `min_wall_t`), but **exactly 2.0mm top and bottom
in Z — precisely equal to `min_wall_t`, with zero spare**, because
`wire_bridge_h` is deliberately derived as `wire_duct_dia + 2×wall_t`
(9.0mm), not padded further. Both figures pass their respective rules
exactly as stated; neither requires a `.scad` change. Disclosed here (and
repeated in §13) per this project's established practice of surfacing
borderline-but-compliant results rather than letting them pass silently.

**E. Bolt-hole / motor-body / platform-boss sanity checks** (motor mount
geometry, §4.3 — all pass with real, computed margin; no interference).

**F. Containment-cap / base-flange interface check:** cap skirt inner
diameter = `fw_flange_dia` + 2×`fit_clearance` = 105.0+0.4 = 105.4mm, vs.
base flange OD = 2×`fw_flange_or` = 105.0mm → exact 0.2mm/side clearance
fit, with matching Z-ranges (**[37.0,45.0]mm, corrected Rev 3.1 — was
[31.0,39.0]mm pre-MISS-008-fix; both the flange band and the cap skirt
derive their Z-position from `fw_clearance_top`/`fw_cap_outer_top`, so both
shifted rigidly +6.0mm together and remain exactly matched post-fix**) on
both parts — confirmed by direct coordinate comparison, the same method
used for the PCB lid/base interface in Rev 2, and re-confirmed this Rev 3.1
via a fresh `echo()` of both Z-ranges directly from the corrected `.scad`
file (not recomputed by hand) to avoid a second arithmetic slip on top of
the one MISS-008 already found.

**G. Rev 3.1 rework — Independent Mechanical Review Cycle 3 findings fixed
this revision (MISS-008 CRITICAL, MISS-009 HIGH, MISS-010 HIGH):**

This subsection is the single authoritative record of the three Cycle-3
gating fixes, cross-referenced from the header changelog, §3, §4.4, §7, §8,
and §11.C above; those sections summarize for their own local context, this
subsection is where the full derivation lives.

- **MISS-008 (CRITICAL) — flywheel disk overlapped its own hub collar.**
  Root cause: `fw_disk_bottom`'s formula computed the disk's bottom face as
  `fw_motor_bell_top + fw_hub_standoff` only, omitting `+fw_hub_collar_h`
  (6.0mm) — even though this same file's `fw_shaft_exposed_len_needed`
  formula elsewhere already treated the collar height as additive, i.e. the
  omission was an internal inconsistency within the file's own logic, not
  merely a missing margin. The Reviewer rendered a literal `intersection()`
  of the modeled disk solid and the modeled hub-collar solid and measured a
  real, non-zero **~145mm³ manifold overlap** at Z=[31.5,34.5]mm — meaning
  the disk could not physically be slid onto the collar as Assembly Step 5
  describes, because the two solids already occupied the same space in the
  model. **Fix:** `fw_disk_bottom` = `fw_motor_bell_top` + `fw_hub_standoff`
  + `fw_hub_collar_h` (37.5mm, was 31.5mm). This single formula change
  cascades rigidly: `fw_disk_top` 36.0→42.0mm, `fw_clearance_top`
  39.0→45.0mm, `fw_cap_outer_top`/`fw_bay_total_height` 43.0→49.0mm,
  `fw_wall_h` 37.0→43.0mm — **and, checked explicitly this revision beyond
  what the Reviewer's finding text named, the flange band's own Z-position**
  (`fw_bay_wall()`) **and the containment cap's own skirt Z-position**
  (`containment_cap()`) **both also derive from `fw_clearance_top`/
  `fw_cap_outer_top` and so both shift identically, from [31,39]mm to
  [37,45]mm** (§11.F). Verified: a fresh `intersection()` of the corrected
  disk and hub-collar solids returns an empty mesh (0 facets); a full-
  assembly re-render after the fix reports `Status: NoError`.
- **MISS-009 (HIGH) — wire duct void never subtracted globally.** Root
  cause: `base()` was a flat `union()`, and the wire-duct clearance bore was
  only cut inside `motor_wire_bridge()`'s own local cube — never subtracted
  from the containment-wall annulus or the PCB-bay south wall that the duct
  path actually has to cross. The Reviewer's rendered `base()` + point-
  containment sweep found the duct path solid at two independent locations,
  defeating the documented wire route and Assembly Step 4 outright (not a
  tight-but-passable clearance issue — genuinely solid, unroutable plastic).
  **Fix:** split the bridge into `motor_wire_bridge_solid()` (the block
  itself) and a separately-scoped `motor_wire_duct_void()` (the bore, now a
  top-level module reusable anywhere it needs to be subtracted), hoisted the
  bridge's Y-span variables to top-level scope so both the wall annulus and
  the south wall can reference the exact same coordinates as the bridge
  block, and restructured `base()` into a `difference()` that subtracts
  `motor_wire_duct_void()` globally, once, from the whole assembly — not
  locally inside one sub-module. A second, independently-discovered 1mm
  near-end shortfall in the duct's own modeled length (`wire_duct_y_lo`
  93.0→91.0mm) was fixed in the same pass, since it was found while directly
  verifying this fix and left unfixed would have reintroduced a (smaller)
  version of the same class of defect. Verified: a 7-point containment sweep
  along the full documented wire path (containment-wall annulus, PCB-bay
  south wall, and the bridge block itself) confirms every point is void
  (open), not solid.
- **MISS-010 (HIGH) — pre-existing Rev 2 tab/skirt interference, disclosed
  but not fixed at Rev 3 time.** See §11.C above for the full root-cause
  derivation and the fix now applied (`tab_relief_margin`, relief-notch cut
  into `lid_shell()` at all 4 `tab_positions`). Not repeated here to avoid
  two divergent copies of the same derivation; §11.C is the canonical
  record for this finding.
- **Full-assembly regression check, all three fixes together:** a single
  fresh render of the complete corrected `.scad` file (not three separate
  partial renders) reports `Status: NoError`, **Genus 8, 4618 vertices, 9264
  facets**. This is the authoritative current figure, re-confirmed directly
  via OpenSCAD's own CGAL-based render this revision (not inferred from any
  earlier partial or intermediate render) — see §0's Rev 3.1 addendum for
  why this document deliberately does not attempt to attribute the specific
  vertex/facet/Genus delta to any one of the three fixes individually (that
  breakdown was investigated and found not reliably attributable with the
  tooling available this session — trimesh's own genus computation assumes
  a single watertight solid and does not apply cleanly to this multi-body
  assembly).

---

## 12. Fastener placement summary

Three fastener classes this revision (Rev 2 had one):

| Joint | Fastener | Count | Placement rationale |
|---|---|---|---|
| PCB lid ↔ base | M2.5 self-tapping, into `standoff()` pilot bosses | 6 (at MH-1..6) | Unchanged mechanism from Rev 2, now at 6 positions instead of 4 |
| Motor ↔ platform boss | Plain M3 clearance-fit, through-hole | 4 (assumed square pattern, §4.3) | Deliberately a **reversible, direction-agnostic** joint — which side of the joint is threaded is UNKNOWN (not in the interface file), so plain through-holes were chosen specifically because they work regardless of which side ends up threaded, avoiding a decision that depends on an unconfirmed fact |
| Containment cap ↔ base flange | M3 into heat-set brass inserts | 6 (evenly spaced, `bolt_circle_r`=48mm) | Heat-set inserts chosen (over self-tapping directly into PETG) specifically because this joint is a **safety-relevant** one (§8) — a threaded metal insert holds torque and resists strip-out far better than a directly-tapped plastic hole, appropriate for a joint that must not fail under the same event it is meant to contain |

**Heat-set insert wall-thickness check:** insert OD (4.6mm) centered at
`bolt_circle_r`=48.0mm within the flange band (43.5–52.5mm radial span)
leaves 2.2mm of material on each side (inner and outer) — 0.2mm above
`min_wall_t`, a real but tight margin, disclosed rather than assumed safe by
inspection. Insert pocket depth (5.7mm) fits within the flange band's own
8.0mm height, leaving 2.3mm of solid material above the insert's own
bottom face and below the flange band's own top.

No fastener-load (torque, shear) calculation was performed for any joint —
this is explicitly beyond Phase 1's basic-manufacturability/basic-fit scope;
fastener **counts and positions** are engineering judgment, not computed
from a load case. **(Tagged MISS-011, MEDIUM, non-gating — Independent
Mechanical Review Cycle 3:** the Reviewer separately flagged this exact gap
for the containment-cap joint specifically, given its safety-relevant duty
(§8); the finding confirms this disclosure was already accurate rather than
revealing a new one, and it is explicitly carried forward unresolved this
revision — see §8's MISS-011 paragraph and §16.) **Rev 3.2 update:** a
bounded, non-certifying **pull-out** estimate for the containment cap's 6×M3
heat-set-insert joint specifically has since been attempted at §8.1 (real
published/measured pull-out data compared against a work-energy force
estimate for the disclosed REQ-403 load case). Torque and shear still have
no calculation of any kind for any joint — §8.1 narrows, but does not close,
this gap.

---

## 13. Manufacturability / 3D-printability

**13.1 Rule set:** see §2 (0.2mm fit clearance, 2.0mm minimum wall, 45°
overhang threshold, 10.0mm maximum bridge span, PETG assumed material).

**13.2 Checked against actual Rev 3 features:**

- All new walls (flywheel-bay wall at 4.0mm, containment-cap flange/dome)
  meet or exceed the 2.0mm minimum.
- The motor platform boss, containment-cap dome, and flange are all vertical
  or flat surfaces — no overhang beyond the 45° threshold anywhere in the
  new geometry.
- The motor-wire bridge (§11.D) is the one feature that approaches (without
  exceeding) the bridge-span limit: 9.0–9.416mm against a 10.0mm rule
  (90.0–94.2%). Its own surrounding wall (the duct bore) is simultaneously
  at exactly the minimum wall thickness in the Z-direction (2.0mm, zero
  spare). Both are disclosed as tight-but-compliant, not silently passed —
  directly analogous to Rev 2's own disclosed 9.5mm/95%-of-limit J1-cutout
  bridge. No change was made to either figure because both pass their
  respective stated rule; a design choice to "round up" for extra margin
  was considered and rejected because it would either shrink the flywheel
  bay's own required clearance (§7, not acceptable) or grow the overall
  footprint further beyond REQ-308's already-disclosed overrun (§3) — the
  current figures are judged the right trade-off, disclosed rather than
  silently adjusted.
- The heat-set insert flange wall thickness (2.2mm each side, §12) is
  likewise tight-but-compliant, 0.2mm above the minimum.
- **Rev 3.1 addendum — MISS-010 relief notches checked for manufacturability
  impact, none found:** the 4 new relief notches (§11.C/§11.G) are small,
  local features — each spans only `tab_w`+2×`fit_clearance` (8.4mm) in X
  at its own tab's position (not a cut running around the full skirt
  perimeter), fully removes the skirt band's own material within that local
  X-span (in Y, `notch_h`=`lid_skirt_t`+2×`tab_relief_margin`=4.0mm, wider
  than the 2.0mm skirt band it clears), and is capped in Z at exactly
  `lid_lip_h`=3.0mm (with a harmless 1.0mm overshoot below the skirt band's
  own already-open bottom face) so the roof above is never touched. Outside
  those 4 local X-spans, the skirt band's own 2.0mm cross-section is
  completely unchanged — this is a local relief, not a general thinning of
  the skirt. The notches remove material rather than adding any new
  overhang, unsupported span, or thin-wall condition, and they do not touch
  the roof or reduce any wall below `min_wall_t` anywhere the skirt band
  still exists. No manufacturability rule from §13.1 is newly challenged by
  this fix.

**13.3 Print orientation:** as with Rev 2, the base is expected to print
floor-down (build plate = the base's own exterior bottom face) — this keeps
every new feature (flywheel-bay floor disc, motor platform boss, wire
bridge) supported by the print bed or by short vertical walls, with no new
orientation-dependent overhangs introduced beyond the bridge span already
addressed. The containment cap is expected to print dome-up or dome-down
depending on slicer preference — its flange face is flat either way, so
orientation does not change its own manufacturability profile materially.
No print-orientation-dependent structural weakness (layer-adhesion direction
vs. load direction) analysis was performed for the containment cap's own
impact-resistance role (§8) — this is disclosed as a real gap, not silently
assumed adequate, given the cap's safety-relevant duty. **(Related to, but
distinct from, MISS-011** — MISS-011 is specifically about the missing
fastener-load calculation (§12); this print-orientation/layer-adhesion gap
is a second, separately-disclosed limitation on the same cap, not itself
formally tracked under the MISS-011 tag, and not resolved this revision
either.)

---

## 14. Assembly order

Re-derived from scratch for 3 pieces (Rev 2's 2-piece sequence does not
extend directly):

1. Insert PCB into the base, seating on the 6 standoffs (MH-1..6).
2. Fasten the PCB lid onto the base with 6× M2.5 self-tapping screws through
   the lid tabs into the base standoffs — this closes and seals the PCB bay
   completely before any motor/flywheel work begins, so the board is fully
   protected during the more manual motor/flywheel assembly steps that
   follow.
3. Mount the motor (M1) onto the motor platform boss with 4× plain M3
   screws (direction-agnostic, §12).
4. Route the motor's phase-wire pigtail through the wire duct and connect it
   to MC-1 (the ~42mm interior floor run, §10) — performed before the
   flywheel is installed, since access to the duct/motor area is still open
   from the top at this stage.
5. Slide the hub collar onto the motor's exposed shaft and the flywheel disk
   onto the hub collar; tighten the collar's set screw. This step requires
   the ≥9.0mm of exposed shaft length above the motor bell (§4.3) — if M1's
   actual shaft does not expose this much, this step cannot be completed as
   designed (an open UNKNOWN, §16).
6. Install the containment cap **last**, bolting it to the base's flange
   with 6× M3 screws into the heat-set inserts. Placing this step last means
   nothing is ever trapped behind the cap during assembly — every part
   installed before it (motor, wire, hub, flywheel) remains accessible from
   the top until the cap goes on, satisfying the "physically achievable
   sequence, no part trapped behind another" requirement.

**Rev 3.1 re-verification note:** Steps 4 and 5 above are the two steps the
Cycle 3 review specifically called into question (MISS-009 for Step 4's wire
route, MISS-008 for Step 5's "slide disk onto hub collar"), and both are now
re-verified physically achievable in the corrected model. Step 4: the wire
duct void is confirmed open (not solid) along its full documented path by
the 7-point sweep in §11.G. Step 5: the disk and hub-collar solids are
confirmed non-overlapping (empty `intersection()`, §11.G) — the disk can now
be modeled as actually sliding onto the collar rather than already occupying
its space. `fw_shaft_exposed_len_needed`(9.0mm) itself is unchanged by this
fix (it already correctly included the collar height before Rev 3.1 — this
was the very inconsistency that exposed the `fw_disk_bottom` bug in the
first place, §11.G) — M1's actual exposed shaft length remains a separate,
pre-existing open UNKNOWN (§16), not created or resolved by this rework.

This sequence was checked for trapped-part conditions at every step (no step
requires reaching past an already-installed part from an inaccessible
direction) — the containment cap's cap-last placement is the one sequencing
decision that specifically enables this; an early-installed cap would trap
the motor/hub/flywheel assembly steps behind it with no access.

---

## 15. Self-check against the Mechanical Reviewer's 10-item checklist

Verbatim checklist (`.github/skills/mechanical-review/SKILL.md` lines 32–56).
Re-run in full this Rev 3.1 rework, not just against the 3 named findings —
per the task's own instruction to self-check for second-order effects, each
item below states both the pre-existing Rev 3 assessment and what Rev 3.1
specifically re-checked or changed.

1. **PCB mounting** — ✅ 6 standoffs at interface-confirmed MH-1..6 positions
   (§5.1, §4.1). **Rev 3.1 re-check:** unaffected — none of the 3 fixes touch
   PCB-bay standoff geometry.
2. **Connector accessibility** — ✅ all 7 connectors/features addressed; one
   disclosed trade-off (MC-1 wire-run distance, §10), not a silent gap.
   **Rev 3.1 re-check (MISS-009):** the wire route itself — not just its
   *distance*, but whether it is physically open at all — was the actual
   defect; the duct void is now confirmed subtracted globally and open along
   its full path (§11.G), so this checklist item's ✅ is now backed by a
   verified-open path, not merely a documented route that turned out to be
   solid plastic.
3. **Component height clearance** — ✅ interface-traced top/bottom clearances
   drive the PCB-bay Z-stack unchanged in formula from Rev 2 (§4.2, §10).
   **Rev 3.1 re-check (MISS-008):** this item also covers the flywheel disk's
   own axial clearance (`fw_clearance_top`, §4.4/§7) — a "component" in the
   same checklist sense — which was NOT previously ✅ in any credible sense
   at Cycle 3 review time, since the disk overlapped its own hub collar in
   the modeled geometry. Now corrected end-to-end (§4.4, §7, §11.G); this
   item's ✅ now covers both Z-stacks (PCB-bay and flywheel-bay), not just
   the PCB-bay one the original Rev 3 phrasing focused on.
4. **Internal clearance/interference** — ✅ full computed record, §11: **7
   fixed** (4 self-caught during Rev 3 authoring, §11.A + 3 from Independent
   Review Cycle 3, §11.G: MISS-008/009/010), 2 dismissed (§11.B), **0
   flagged-not-fixed** (was 1 at Rev 3 authoring time — the tab/skirt
   overlap, §11.C — now fixed this revision, so this bucket is empty), 1
   disclosed-compliant finding (§11.D, wire-bridge span, unchanged/unrelated
   to Cycle 3). MISS-011 is a separate, non-clearance disclosure (fastener-
   load calculation gap) and is not counted in this bucket — see item 5.
5. **Fastener placement** — ✅ 3 classes, each justified by joint duty, §12.
   **Rev 3.1 re-check:** the heat-set insert's own flange-band Z-position
   shifted +6.0mm along with the rest of the containment structure (§11.G),
   but its radial geometry (bolt circle radius, wall margins each side,
   pocket depth vs. band height) is entirely unchanged by a pure Z-shift, so
   the existing insert wall-thickness/pocket-depth check (§12) remains valid
   as originally computed — re-confirmed, not silently assumed still true.
   MISS-011 (fastener-load calculation gap, MEDIUM, non-gating) is now
   explicitly tagged in §12/§8 and carried forward, not resolved this
   revision. **Rev 3.2 note:** a bounded, non-certifying pull-out-vs-load
   estimate for this specific joint has since been attempted at §8.1 —
   result: plausible for the joint's realistic/secondary loading role,
   marginal-to-inadequate only for a hypothetical full-direct-hit worst
   case. This narrows but does not close MISS-011 (still OPEN, proposed
   for Mechanical Reviewer cross-check, not self-resolved) and does not
   upgrade this checklist item's own ✅, which remains about placement/
   duty-justification, not load-certification.
6. **Wall thickness** — ✅ 2.0mm minimum held everywhere, with disclosed
   deliberate exceptions (4.0mm containment wall) and disclosed tight spots
   (2.0mm duct wall, 2.2mm insert-flange margin), §2/§11/§12/§13. **Rev 3.1
   re-check:** none of the 3 fixes change any wall's own thickness (MISS-008
   is a pure Z-shift; MISS-009 restructures how a pre-existing void is
   subtracted, not its bore diameter or surrounding wall dimensions;
   MISS-010 removes material locally at 4 tab positions, §13) — this item's
   figures are unchanged and were re-confirmed unchanged, not left unchecked.
   **Rev 3.2 note (numerically refreshed in Rev 3.4 — see §8.1.2):** this
   item's own ✅ is about structural-adequacy-in-
   general and manufacturability, not a load-specific certification for
   the containment wall specifically — §8.1's bounded estimate finds the
   4.0mm `containment_wall_t` does **not** carry an affirmative "adequate
   against the disclosed 156.44J load case" claim (short by precisely
   ≈3.26×–4.30×
   in the best case, was "roughly 2.5×", to ≈1.7–3.6 orders of magnitude
   under more typical
   assumptions, was "1–3+ orders of magnitude" — the shortfall widened once
   §8.1 was recomputed against the Rev-3.3-corrected energy figure, it did
   not narrow). This is escalated separately to the Hardware Lead (§8.1.6)
   and does not itself flip this checklist item's ✅ (2.0mm-minimum/
   manufacturability holds regardless), but the Reviewer should read this
   item together with §8.1, not in isolation.
7. **Assembly order** — ✅ re-derived 6-step sequence for 3 pieces, no
   trapped parts, §14. **Rev 3.1 re-check:** Steps 4 (wire routing) and 5
   (disk-onto-collar) — the two steps Cycle 3 specifically called into
   question — are now re-verified physically achievable against the
   corrected model (§14's Rev 3.1 re-verification note, §11.G).
8. **Basic print-fit tolerance** — ✅ 0.2mm/side at both mating interfaces,
   re-justified not just carried forward, §2. **Rev 3.1 re-check:** the
   containment-cap/base-flange interface's own 0.2mm/side radial fit (§11.F)
   is a diametral relationship, unaffected by the pair's identical +6.0mm
   Z-shift; re-confirmed via direct `.scad` `echo()` this revision rather
   than assumed invariant.
9. **Basic manufacturability/3D-printability** — ✅ §13, including two
   disclosed tight-but-compliant findings (wire-bridge span, insert-flange
   margin — both unchanged by this rework). **Rev 3.1 re-check (MISS-010):**
   the new relief-notch geometry was explicitly checked for new
   manufacturability risk and none was found (§13.2 addendum) — it removes
   material locally rather than introducing any new overhang, bridge span,
   or sub-minimum wall condition.
10. **Interface-value traceability** — ✅ §4.1's full traceability table;
    §16 separates ASSUMPTION/ESTIMATE/UNKNOWN from CONFIRMED interface
    facts. **Rev 3.1 re-check:** the one new parameter introduced by this
    rework, `tab_relief_margin`, is tagged `ASSUMPTION` (§4.2, tied to the
    same pre-existing "small explicit cut-tool overshoot" convention used
    throughout this file, not a freshly-invented untraced rule) — no new
    value was left silently untagged.

This is a self-check, not a substitute for Independent Mechanical Review —
every ✅ above reflects this Mechanical Lead's own assessment and is offered
for the Reviewer to challenge, not as a pre-cleared result. In particular,
items 1, 2, 6, 8, and 10 above are re-confirmed **unaffected/still-valid**
claims, not re-derivations from scratch — they are included here precisely
so the Reviewer can see this Mechanical Lead did not silently skip checking
whether the 3 fixes had second-order effects on the other 7 checklist items,
not because those items themselves were expected to change.

**Rev 3.2 addendum to this self-check:** the "unaffected/still-valid" framing
above describes items 5 and 6's status **against the 3 Rev-3.1 fixes**
specifically (MISS-008/009/010) — that part remains true. It does **not**
mean items 5/6 are unaffected by Rev 3.2's own new §8.1 content: both now
carry a "Rev 3.2 note" (above) flagging that §8.1's bounded estimate finds a
real, disclosed margin concern on the containment wall, separately escalated
to the Hardware Lead. Read items 5 and 6 together with §8.1, not as still
fully "clean" in the load-adequacy sense — their ✅ marks continue to certify
only what this checklist item has always meant (placement/duty-justification
for item 5; minimum-thickness/manufacturability for item 6), not a new
load-certification neither item ever claimed to provide.

---

## 16. Open UNKNOWNs / ASSUMPTIONs carried forward

| Item | Status | Note |
|---|---|---|
| M1's real mounting-bolt pattern | ASSUMPTION | Generic 12mm-square hobbyist convention assumed; interface file's own flagged open item; must be confirmed before build |
| Which side of the motor/platform joint is threaded | UNKNOWN | Resolved by design choice (plain through-holes work regardless), not by data |
| M1's actual exposed shaft length above the bell | UNKNOWN | Design requires ≥9.0mm (`fw_shaft_exposed_len_needed`); not in the interface file; must be confirmed before build |
| Hub collar dimensions (⌀8×6mm) | ASSUMPTION | Generic set-screw shaft-collar part, no manufacturer/datasheet selected |
| Hub collar retention strength | UNKNOWN | No datasheet; this is the exact unquantified failure mode the REQ-403 containment proposal (§8) is defending against |
| J4 cutout diameter (10.0mm) | ESTIMATE | This Mechanical Lead's own outside-knowledge estimate for a generic barrel jack; no datasheet cited by the interface file |
| Heat-set insert dimensions (⌀4.6×5.7mm) | ASSUMPTION | Generic M3 brass insert; no manufacturer part selected |
| Print material (PETG) | ASSUMPTION | Inherited from interface B6, not independently confirmed |
| Pre-existing Rev 2 190.06mm³ tab/skirt overlap | **RESOLVED, Rev 3.1** (was: Flagged, not fixed) | Was out of the original Rev 3 task's scope, confirmed pre-existing not new; independently re-confirmed by Independent Mechanical Review Cycle 3 (MISS-010, HIGH) and judged in-scope for this rework since this geometry was already being reworked for MISS-008/009 — fixed via `tab_relief_margin` relief-notch cut, verified via empty-volume `intersection()` + 8-point containment sweep. See §11.C, §11.G. No longer an open item as of Rev 3.1. |
| Motor-wire-bridge span (9.0–9.42mm) and duct-wall thickness (exactly 2.0mm) | Disclosed, compliant | Identified during Rev 3 authoring; within stated rules, no fix required; unrelated to and unchanged by the Rev 3.1 Cycle-3 rework |
| REQ-308 envelope overrun (8.0–13.7% over the ~150mm-class soft ceiling) | Disclosed trade-off | Judged acceptable given the physical lower bound argument in §3. **Rev 3.1 note:** this overrun figure was for X/Y footprint only, which is unaffected by the Cycle-3 fixes (all 3 are Z-only/internal/inset); not recomputed, since nothing changed that it depends on. |
| Total assembly mass / structural deflection under motor+flywheel load | ESTIMATE (mass only), no deflection analysis | Basic qualitative judgment only (≈130g motor+flywheel on a solid PETG boss/platform judged modest); no FEA, out of Phase 1 scope |
| Wall impact/penetration and cap fastener pull-out under the REQ-403 load case | **Bounded estimate attempted, Rev 3.2 (§8.1); figures numerically refreshed, Rev 3.4** — still not certified/resolved | §8/§13 disclose the 4.0mm wall / 6×M3 fastener choice as reasoned structural judgment, not a certified containment analysis. **Tagged MISS-011 (MEDIUM, non-gating)** — Independent Mechanical Review Cycle 3 confirmed this gap for both the wall and the fastener side of the containment-cap joint (no pull-out/shear calculation, §12). **Rev 3.2:** a bounded, closed-form wall-impact estimate (two methods) and a fastener pull-out-vs-load estimate were attempted at §8.1, using real published/measured material and fastener data (6 new Evidence IDs, `datasheets/evidence-log.md`). **Rev 3.4:** recomputed against the Rev-3.3-corrected 156.44J/79.11 m/s credible-worst-case energy figure (was 121.60J/69.74 m/s); the shortfall widened, it did not narrow. Wall: does not support an affirmative "adequate" claim (short by ≈3.26×–4.30× best case to ≈1.7–3.6 orders of magnitude typical, method-dependent — was ~2.5× best case to 1–3+ orders of magnitude) — separately escalated to the Hardware Lead at §8.1.6, no geometry changed. Fasteners: plausible for the realistic/secondary loading role, marginal-to-inadequate only for a hypothetical full-direct-hit worst case (the required crush distance for adequacy under that hypothetical grew from ≳20mm to ≳26mm, Rev 3.4). Proposed as ready for Independent Mechanical Review's cross-check; **not self-resolved** — MISS-011 Status remains OPEN in `validation/open-issues.md`. |

**Nothing above is being silently relied upon as if it were CONFIRMED** —
this table exists specifically so Independent Mechanical Review and the
human HITL gate (§8) can see the full set of open items in one place, rather
than needing to extract them from prose scattered through the document.
**Rev 3.1 note on table scope:** the tab/skirt overlap row above is kept in
this table (rather than deleted now that it's resolved) so the fix is
visible in place against its own prior "flagged, not fixed" history, per
this project's established practice of not silently removing a previously-
disclosed item without a visible trail; it is the one row in this table that
is no longer actually open as of this revision — every other row remains a
genuinely open item.

**Possible interface-file observation (flagged, not corrected):** while
re-reading `hardware/mechanical-interface.md` this session, no internal
inconsistency or error was found in it — every fact cited in this spec
traced cleanly to a specific interface-file section. Nothing is flagged here
as a suspected interface-file defect; this note exists only to confirm that
this check was performed, per the task's own instruction to flag (not
silently fix) any such issue if found.

---

## 17. Handoff

To Independent Mechanical Review (via Hardware Lead), Rev 3.1: this
document, plus `hardware/mechanical/bench-imu-01-enclosure.scad` (**Rev
3.1, 1208 lines** — was Rev 3, 991 lines), plus the self-check in §15
(re-run against all 10 checklist items, not just the 3 fixed findings),
plus the full open-items table in §16 (now showing the tab/skirt overlap
resolved, MISS-011 explicitly tagged on the containment-cap row). This
package specifically addresses Independent Mechanical Review Cycle 3's
CONDITIONAL verdict: MISS-008 (CRITICAL), MISS-009 (HIGH), and MISS-010
(HIGH) are fixed with real, empirically-verified geometry changes (§11.G is
the full record); MISS-011 (MEDIUM, non-gating) is carried forward
explicitly disclosed, not resolved, per the task's own stated scope for this
rework cycle.

The REQ-403 disposition in §8 is explicitly a **proposal**, not a final
decision — it is expected to be challenged by Independent Review before it
ever reaches the human HITL gate REQ-403 itself calls for. Rev 3.1
specifically re-derived the proposal's *numbers* end-to-end against the
MISS-008-corrected Z-stack (§8's own Cycle-3-verdict paragraph); the
proposal's *topology* argument was independently confirmed TRUE by the
Reviewer and is otherwise unchanged.

No claim of physical fabrication, print, or fit-test is made anywhere in
this document (§0) — this remains a paper/parametric design exercise,
consistent with this entire project cycle's own stated scope. All 3 fixes
were verified this session via real, locally-available tooling
(`openscad` direct CGAL rendering, `trimesh`/`numpy` boolean-intersection
and point-containment scripting) — not hand-arithmetic alone, and not
claimed beyond what that tooling actually confirmed (§0).

**Process note for the Hardware Lead, not a design finding:** this Rev 3.1
rework is a non-cosmetic design change (real geometry shifted, a new void
module was added, new relief-notch geometry was cut) that would normally
warrant a `validation/change-log.md` ECO entry alongside it. This task's own
explicit scope constrained this Mechanical Lead to editing only this
document and the `.scad` file — `validation/change-log.md` was off-limits
this cycle. This document's own new "Rev. 3.1 changelog" block (near the
top of this file) contains everything an ECO entry would normally capture
(root cause, before/after numbers, verification method); flagging here only
so the Hardware Lead can decide whether to have that ECO entry created
through the appropriate channel, rather than this rework silently skipping
the project's own normal change-tracking convention.

---

## 18. Rev 4 — Free-rotation support mechanism

**18.0 Scope and status.** Everything in §0–§17 above (the Rev 3.4 baseline)
is unchanged, byte-for-byte, by this section — see the Rev 4 status note and
changelog near the top of this file for why this revision uses a
zero-deletion, additive-section approach instead of this file's own
Rev 3.1–3.4 convention of rewriting the top-of-file Status paragraph each
time. This section documents the full engineering derivation and
verification behind `hardware/mechanical-interface.md`'s new "Part C" (the
interface-level summary) and `bench-imu-01-enclosure.scad`'s new "2B. REV 4"
/ "3B. MODULES" blocks (the actual geometry). Nothing here should be read as
"reviewed" or "approved" — a fresh Independent Mechanical Review pass
covering this section specifically is the required next step
(`.github/agents/mechanical-lead.agent.md`, "Out of scope").

**18.1 Bearing physical facts.** Source: BC Precision 4LS-3 lazy-susan
turntable ball bearing, Evidence ID **DS-BRG-001**
(`datasheets/bcprecision_4ls-3-lazy-susan-turntable-bearing_web-product-page.md`).
Human-approved as Candidate A, not re-litigated here
(`bom/component-selection.md`, "Free-Rotation Support Mechanism").

| Parameter | Value | Unit | Confidence | Rationale |
|---|---|---|---|---|
| Outer diameter (`brg_od`) | 101.6 (nominal 4in) | mm | **CONFIRMED** | DS-BRG-001 spec block |
| Center-hole diameter (`brg_id`) | 55.1 (2.170in) | mm | **CONFIRMED** | Same source |
| Overall thickness (`brg_t`) | 7.9 (5/16in) | mm | **CONFIRMED** | Same source |
| Load capacity (`brg_load_cap_kg`) | 136.1 (300lb) | kg | **CONFIRMED** | Same source |
| Mounting-hole count/spacing per plate | 4 holes, evenly spaced (`n_bmount_bolts`) | — | **ASSUMPTION** | Not published for this SKU; generic lazy-susan-hardware-class convention, Evidence ID **DS-BRG-007** (new this revision, §18.1.1) |
| Screw class implied by that convention (`brg_screw_major_dia`) | 3.5 (#6 major dia.) | mm | **ASSUMPTION** | Same DS-BRG-007 source; screw-size implication adapted for a PETG target rather than the source's own wood-screw pilot-hole figure — see `bmount_pilot_dia` derivation, §18.2 |
| Bearing mass (`brg_mass_est`) | ≈130 (129.1 computed) | g | **ESTIMATE** (chain of estimates) | No manufacturer weight published; derived analytically from CONFIRMED OD/ID plus two further sub-estimates (steel plate gauge ≈1.2mm, ball race 24×≈6mm balls) — see full build-up in `hardware/mechanical-interface.md` C1. Falls within an inconsistent 77–160g web-search range for comparable 4in bearings (weak corroboration only, not treated as confirmation) |
| "Suggested top diameter" | 12–25 | in | **CONFIRMED** (as a published generic suggestion) | Same source — a heavy-furniture stability rule of thumb, **explicitly not used** to size the stand plate at this rig's ~600g scale; see §18.3 for the actual computed sizing method used instead |

**18.1.1 Evidence ID DS-BRG-007 — provenance summary** (full text in
`datasheets/evidence-log.md` and the new
`datasheets/lily-bearing_lazy-susan-hardware-kit_web-article.md` file, both
registered this revision, §18.11). A lazy-susan-hardware retailer
(lily-bearing.com, "Lazy Susan Hardware Kit: What's Inside and How to
Install") describes 4 evenly-spaced mounting holes per plate as the generic
convention for this bearing class, sized for #6 wood/self-tapping screws with
≈4mm (5/32in) pilot holes, and independently states the same 300lb
load-capacity figure DS-BRG-001 states for a 4in-class bearing (a real
cross-check that this is an applicable convention for this bearing class,
not an unrelated citation). Flagged explicitly as **a generic convention for
this bearing class, not this SKU's own confirmed hole pattern** — this SKU's
own hole positions are not published anywhere found this session and must be
verified against the physical part before manufacture (not a blocking
escalation this cycle, since no physical prototyping is happening, REQ-502 —
mirrors the same treatment already given to M1's own motor bolt-pattern
ASSUMPTION, `hardware/mechanical-interface.md` B1). Because the true hole
positions are unknown, §18.2's new mounting geometry is deliberately a solid
annular band (not discrete bosses at hard-coded positions), so a real hole
can be field-drilled anywhere within the band regardless of how the actual
part's pattern compares to this default.

**18.2 New mounting flange (`bmount_flange()`).** Bolts the bearing's top
(rotating) plate to the underside of the existing flywheel-bay floor. A
genuinely new solid feature, unioned onto `motor_platform()`'s existing floor
disc — no existing Rev 3 module is modified, resized, or removed.

| Parameter | Value | Unit | Confidence | Rationale |
|---|---|---|---|---|
| Outer radius (`bmount_flange_or`) | 52.5 | mm | **DERIVED** | Reuses `fw_flange_or` exactly — already spans past the bearing's own 50.8mm radius with margin; reusing a named existing dimension keeps the design internally legible rather than inventing a new, close-but-different value |
| Inner radius (`bmount_flange_ir`) | 28.0 | mm | **ASSUMPTION** | Clears the bearing's 27.55mm ID radius with working margin; doubles as the coaxial tether bore (§18.6) |
| Thickness (`bmount_flange_t`) | 6.0 | mm | **ASSUMPTION** | Hosts a 5.0mm blind pilot hole with a 1.0mm margin, mirroring `standoff_h`/`standoff_pilot_depth` (6.0/5.0mm) exactly |
| CSG fuse-overlap into existing floor (`bmount_fuse_overlap`) | 1.0 | mm | **ASSUMPTION** | Mirrors the existing `bridge_fuse_overlap` (2.0mm) convention already used elsewhere in this file — ensures genuine volumetric overlap at the join, not a knife-edge coincident-face touch (verified non-empty this session, §18.5) |
| Bolt-circle radius (`bmount_bolt_circle_r`) | 40.0 | mm | **ASSUMPTION** | Default pattern only (DS-BRG-007's hole count, not this SKU's confirmed positions); sits mid-band between 28.0mm and 52.5mm, clear of both the bore and the outer edge |
| Pilot-hole diameter (`bmount_pilot_dia`) | 2.8 | mm | **ASSUMPTION** | = 0.8× a #6 screw's 3.5mm major diameter (ANSI/ASME B1.1), the same 80% pilot-to-major ratio already used by `standoff_pilot_dia`/M2.5 (2.0/2.5mm = 80%) |
| Pilot-hole depth (`bmount_pilot_depth`) | 5.0 | mm | **ASSUMPTION** | = `bmount_flange_t` − 1.0mm blind margin, identical pattern to `standoff_pilot_depth` |
| Mass (this feature only) | ≈47.1 | g | **ESTIMATE** (computed) | `V_gross`=37,176mm³, `V_net`=37,053mm³ (after pilot-hole/bore subtraction) × PETG 1.27g/cm³; see §18.3 for the full mass model |
| Position | Centered at (`fw_cx`,`fw_cy`) = (53.5, 52.5) | mm | **DECIDED** (design choice) | Reuses the flywheel-bay's existing center — the only Z=0 location with existing solid floor material to fuse against; see §18.3 for why this is not the assembly's true computed CG, and how that offset is carried into the stand-plate sizing instead |

**Geometric non-interference check (computed, not assumed).** The existing
floor disc (`motor_platform()`) is a solid disc of radius `fw_bay_outer_r`
=43.5mm — strictly between the new flange's inner (28.0mm) and outer
(52.5mm) radii. So: (a) in the 28.0–43.5mm band, the new flange genuinely
fuses against pre-existing solid material (a real bonded joint, confirmed
non-empty by `intersection()`, §18.5); (b) in the 43.5–52.5mm band, the
flange adds new material where nothing existed before (purely additive,
zero interference by construction); (c) the floor disc's own pre-existing
small cuts (4× M3 motor-mount clearance holes at ≈8.5mm radius, the central
≈3.4mm shaft-clearance hole) all sit well inside the new flange's 28.0mm
bore — entirely outside the new flange's own solid material, so nothing
about the new flange touches, narrows, or otherwise affects them. The new
40.0mm bolt-circle for the flange's own 4 pilot holes is checked against both
edges: 40.0 + (2.8/2) = 41.4mm inner-clear of the 43.5mm outer floor-disc
edge (2.1mm margin) and 40.0 − (2.8/2) = 38.6mm outer-clear of the 28.0mm
bore (10.6mm margin) — both comfortably inside the annulus that has solid
material to drill into, confirmed by direct radial arithmetic, not merely
asserted.

**18.3 CG / tip-over analysis and stand-plate sizing.** Full analytic
primitive decomposition of every existing Rev 3 solid (floor disc,
motor-platform boss, flywheel-bay wall tube, existing flange band,
wire-bridge net, containment-cap disk+skirt, PCB-bay floor/wall/roof, 6
standoffs, 4 lid tabs — each at its own real modeled geometry, not a
bounding-box or surface-area proxy), converted to mass at PETG's 1.27g/cm³
density (`bom/component-selection.md`'s PETG TDS citation), summed with the
existing point masses (M1 motor 30g CONFIRMED, flywheel 100g ASSUMPTION,
populated PCB 19.5g ESTIMATE, each at its own interface-file position). Full
script: `/tmp/rev4_check/cg_analysis.py` (scratch, not part of the repo
deliverable — the numbers below are the authoritative record).

| Quantity | Value | Confidence |
|---|---|---|
| Rev 3 plastic mass (analytic, all existing solids; 2.0% void-fraction deduction for secondary cutouts) | ≈207.9g | ESTIMATE (computed) |
| Rev 3 plastic-only CG | X=53.72, Y=72.71, Z=26.30mm | ESTIMATE (computed) |
| Rev 3 point-mass subtotal | 149.5g | mixed CONFIRMED/ASSUMPTION/ESTIMATE, per-item (§18.1 table style; see interface.md B7) |
| **Rev 3 total mass** (plastic + points) | **357.4g**, CG=(53.63, 68.68, 28.51)mm | ESTIMATE |
| New flange mass (§18.2) | ≈47.1g | ESTIMATE (computed) |
| **Rotating-assembly total** (Rev 3 total + new flange; excludes bearing + stand plate, which do not rotate) | **404.5g**, CG=(53.61, 66.80, 24.85)mm | ESTIMATE |
| Horizontal offset of rotating CG from bearing axis (53.5, 52.5) (`r_rot`) | **≈14.30mm** (X negligible, +0.11mm; Y dominant, +14.30mm) | DERIVED |
| Bearing mass (on-axis; does not affect `r_rot`) | ≈130g | ESTIMATE (§18.1) |

**A disclosed discrepancy, not silently reconciled.** The analytic method
above finds Rev 3's own plastic mass at ≈207.9g — materially higher than
`bom/component-selection.md`'s own bounding-shell-surface-area estimate
(130–170g) for the same enclosure. The largest single contributor (the
flywheel-bay wall tube, ≈44,849mm³) was independently hand-verified this
session against the exact cylindrical-annulus volume formula to rule out a
computation bug. Most likely explanation: a generic "outer-shell-area ×
wall-thickness" proxy under-counts this enclosure's doubled-up-thickness
features (the 4mm containment wall over its full height, the existing
flange band, the containment cap's own disk+skirt) — judged that the
analytic method here is the more accurate of the two, not the bounding-shell
estimate, but disclosed as a real finding for the Hardware Lead/Reviewer to
weigh, not silently reconciled either way. As a positive cross-check
despite this discrepancy: the computed Rev 3 CG_y (68.68mm) does fall inside
the supervising session's own independently-derived 63–78mm bracketing
range (63mm components-only, 70–78mm with a rough plastic-split estimate).

**Why the flange is centered on the flywheel-bay's existing axis (53.5,
52.5) rather than the true computed CG (Y≈68.7mm):** no wider Z=0 floor
exists anywhere else in the Rev 3 geometry to structurally carry a
differently-centered flange — the flywheel-bay axis is the only position
where the new flange genuinely fuses against pre-existing solid floor
material (§18.2's non-interference check). This turns the CG-to-axis offset
into a disclosed, quantified design trade-off (`r_rot`≈14.30mm above),
carried forward directly into the stand-plate's own tip-over sizing below,
rather than an unexamined choice.

**Tip-over methodology.** Because the stand plate is a full circle centered
on the same bearing axis the rotating assembly orbits, the combined system's
overall CG-to-axis horizontal offset (`d_offset` = m_rotating·r_rot /
m_total) is **constant regardless of rotation angle** — this is what
justifies a circular (not rectangular or directionally-biased) stand-plate
shape: stability is genuinely angle-invariant here, not just checked at one
worst-case angle. A sweep of candidate stand-plate outer radii was computed,
tracking static margin (stand radius / `d_offset`), system CG height above
the new ground plane, and the approximate horizontal bump force at CG
height needed to begin tipping (`F_tip`, a simple moment-balance about the
stand edge — not compared against any cited "typical bump force" standard,
presented as a computed figure for the Hardware Lead/Reviewer's own
judgment):

| R_stand (mm) | m_stand (g) | W_total (g) | d_offset (mm) | Static margin | h_cg (mm) | F_tip (N) | F_tip (gf) |
|---|---|---|---|---|---|---|---|
| 50.0 | 40.9 | 575.4 | 10.05 | 5.0× | 33.9 | 6.65 | 677.8 |
| 55.0 | 53.5 | 588.0 | 9.83 | 5.6× | 33.3 | 7.83 | 798.5 |
| **60.0** | **67.3** | **601.8** | **9.61** | **6.2×** | **32.6** | **9.13** | **931.1** |
| 65.0 | 82.2 | 616.7 | 9.38 | 6.9× | 31.8 | 10.57 | 1077.1 |
| 70.0 | 98.4 | 632.9 | 9.14 | 7.7× | 31.1 | 12.15 | 1238.1 |
| 75.0 | 115.7 | 650.2 | 8.89 | 8.4× | 30.4 | 13.89 | 1415.8 |
| 80.0 | 134.3 | 668.8 | 8.65 | 9.3× | 29.6 | 15.81 | 1612.1 |

**Decision: `stand_plate_or` = 60.0mm (120mm diameter), ASSUMPTION/DECIDED.**
Chosen from the sweep as the point where static margin (6.2×) is already
comfortable while the footprint stays well clear of ballooning past the
existing 111.4×170.6mm assembled envelope — every larger candidate buys
progressively less margin-per-mm of added radius (diminishing returns visible
in the table) for a footprint that starts to rival the enclosure's own
existing envelope. This is a qualitative judgment call, not an
independently-cited/certified safety-factor standard; disclosed as such, not
presented as a pass/fail against any external rule. **Not** matched to the
bearing's own generic 12–25in "suggested top diameter" (§18.1) — that figure
is a heavy-furniture stability rule of thumb for a vastly different load
class, and a stand plate anywhere near it (305–635mm) would itself blow well
past the enclosure's own existing footprint for no benefit at this rig's
scale; this section's own computed sweep, not that suggestion, is what
actually sizes the part.

| Parameter | Value | Unit | Confidence | Rationale |
|---|---|---|---|---|
| Outer radius (`stand_plate_or`) | 60.0 | mm | **DECIDED** (from sweep above) | See decision rationale above |
| Inner radius (`stand_plate_ir`) | 28.0 (=`bmount_flange_ir`) | mm | **DERIVED** | Keeps the tether channel continuous/coaxial start to finish, §18.6 |
| Thickness (`stand_plate_t`) | 6.0 | mm | **ASSUMPTION** | Mirrors `bmount_flange_t` |
| Bolt-circle radius | 40.0 (=`bmount_bolt_circle_r`) | mm | **DERIVED** | Same default-pattern caveat as §18.2 |
| Mass (this feature only, at chosen radius) | ≈67.3 | g | **ESTIMATE** (computed) | From the sweep table above |
| **Total system mass** (rotating assembly + bearing + stand plate) | **≈601.8** | g | **ESTIMATE** | Roughly double the human's own working ≈280–320g estimate — attributed to the higher analytic plastic-mass finding above plus the new flange/bearing/stand-plate mass the original estimate did not yet include, **not** a computation error (largest single contributor independently hand-verified) |

**Geometric manufacturability check on the stand plate itself.** At 60.0mm
outer / 28.0mm inner radius, the 40.0mm bolt-circle sits 20mm inside the
outer edge and 12mm outside the inner bore — both generous margins, no
manufacturability concern. Unlike the new flange (§18.2/§18.4), the stand
plate is a uniform-cross-section annulus for its entire thickness — nothing
else fuses to or overlaps it — so it has **no** analogous internal-overhang
concern; it prints flat, either face down, with zero support needed.

**18.4 Manufacturability finding: internal overhang (caught and disclosed
this session, not silently passed over).** Because the new flange's own bore
(r<28mm) is hollow for its full height, while the pre-existing floor disc
directly above it (old Z≥0) is a solid, un-bored disc across r=0–43.5mm, the
transition between the two — where the flange's open bore meets the
existing disc's solid underside — is an internal, **hidden** transition
spanning roughly a 56mm-diameter circle (minus the disc's own small
pre-existing holes) with nothing directly beneath it in the flange's own
printed layers. This does **not** meet this file's own §2/§13.1 rule set
(0.2mm fit clearance, 2.0mm minimum wall, 45° overhang threshold, 10.0mm
maximum bridge span, PETG assumed material) on its own — a 56mm unsupported
span is far beyond the 10.0mm bridge-span rule and well past any reasonable
self-supporting overhang angle for a flat disc underside.

**Three alternatives considered and rejected:**

1. **Taper/widen the flange's own bore near the top** — does not help,
   because the actual problem is the *existing* disc's own broad, un-bored
   underside, which this population is not permitted to modify (REQ-311).
2. **Print the whole base+flange assembly upside-down** (using the existing
   cap-mounting flange band as the new bed face) — shrinks this specific
   problem but breaks several *other* already-validated Rev 3 features that
   depend on floor-down printing (standoffs, wire bridge, §13.3) — a
   strictly worse trade overall, not a net improvement.
3. **Print the flange as a fully separate, adhesively-bonded piece** —
   avoids the issue entirely but turns it into an un-asked-for 5th printed
   piece, contradicting this task's own "4 total pieces" framing, for a
   hidden, non-mating, non-precision surface — judged not worth the
   piece-count increase for a purely cosmetic/internal benefit.

**Decision: keep the flange fused to the base as one print job**, and
disclose the need for slicer-generated internal support material for this
one internal region as a genuine, confirmed manufacturability caveat — **not
a clean pass**. This is judged acceptable because the transition is entirely
internal to the tether-cable bore (not a visible, mating, or precision
surface) and the support material is reachable and removable through the
bore's own 56mm-diameter straight-through opening (not a blind/enclosed
cavity that would trap unremovable support material inside a finished
part). This caveat is carried into the self-check (§18.7, item 9) as an
explicit non-clean-pass, not folded silently into a blanket "manufacturable"
claim.

**18.5 Render / verification results (this session).** Tooling used:
`openscad` CLI (`/opt/homebrew/bin/openscad`, v2026.08.30 — direct CGAL-based
manifold/Genus checking, the same authoritative tool this file's own Rev 3.1
rework relied on, §11.G) plus `trimesh`/`numpy-stl`/`scipy`/`networkx`
(installed this session into a scratch virtualenv, `/tmp/scratch_venv`, for
supplementary boolean-intersection/volume/edge-topology checks — mirrors the
Rev 3.1 rework's own use of `trimesh`/`numpy` scripting, §17). No claim of
physical fabrication, print, or fit-test is made anywhere in this section —
this remains a paper/parametric design exercise (§0).

| Check | Result |
|---|---|
| Full file, default "assembled" `show_mode` | OpenSCAD: **NoError, manifold, Genus 8**, 5770 vertices, 11568 facets |
| `bmount_flange()` alone | OpenSCAD: **NoError, manifold, Genus 1** (correct — one through-bore; 4 blind pilot holes correctly add no genus, confirming they don't accidentally punch through) |
| `stand_plate()` alone | OpenSCAD: **NoError, manifold, Genus 1**; trimesh: **watertight=True**, euler=0 (consistent with Genus 1), volume=52,599.94mm³ |
| `base()` + `bmount_flange()` (as unioned in "assembled" mode) | OpenSCAD: **NoError, manifold, Genus 8** — same Genus as `base()` alone (topologically expected: the flange's bore widens a region that already pierced `base()`'s own floor, rather than adding an independent new handle) |
| `intersection(base(), bmount_flange())` | **Non-empty**: manifold, Genus 1, volume=3,456.27mm³ — proves the two solids genuinely share volume (the `bmount_fuse_overlap` dip is real and working), not merely touching/floating faces |
| Full file, `show_mode="print_layout"` (4 disjoint printable pieces) | OpenSCAD: **NoError, manifold**, Genus 19 (aggregate across 4 disjoint bodies — base+flange fused, pcb_lid, containment_cap, and the new stand_plate at its own disjoint layout position), 5889 vertices, 11850 facets |

**Inclusion-exclusion volume cross-check (a stronger, more direct proof of
CSG correctness than raw facet/vertex counts).** An unexpected finding during
this session's verification: `base()+bmount_flange()`'s vertex/facet counts
(960/1964) are an *exact* arithmetic sum of the two standalone pieces' own
counts (800+160, 1644+320) — surprising at first glance for a genuine
boolean union with real volumetric overlap, since a proper CSG union would
typically re-triangulate/dedupe at the shared boundary rather than simply
concatenate. Rather than accept this as reassurance on its own, the union
was cross-checked against the mathematically rigorous inclusion-exclusion
identity, `volume(A∪B) = volume(A) + volume(B) − volume(A∩B)`, using the
independently-exported STLs:

```
volume(base)              = 110,364.12 mm³
volume(bmount_flange)     =  42,962.45 mm³
volume(base ∩ bmount_flange) = 3,456.27 mm³
--------------------------------------------
predicted volume(union) = 110,364.12 + 42,962.45 − 3,456.27 = 149,870.30 mm³
measured  volume(union), test_base_flange.stl              = 149,870.30 mm³
difference: 0.00 mm³ (0.000%)
```

This is an exact match — strong, computed proof that the CSG union is being
performed correctly (the overlap volume is accounted for exactly once, not
double-counted or omitted), independent of and stronger than the
facet/vertex-count coincidence above. The facet/vertex-count coincidence
itself is left as an unexplained but harmless curiosity (most likely a
byproduct of how CGAL happens to triangulate this specific, largely flat/
coplanar overlap region for this geometry) — not pursued further, since the
volume-based proof already settles the correctness question the count
coincidence had raised.

**`base()`'s own trimesh `watertight=False` flag — diagnosed, confirmed
pre-existing, not a Rev 4 defect.** `base()` alone, exported to STL and
reloaded via `trimesh.load()`, reports `watertight=False` (`euler_number=−6`)
despite OpenSCAD's own independent CGAL-based check reporting "NoError,
manifold, Genus 8" for the identical geometry. This was diagnosed, not left
as an open question:

- **Confirmed byte-identical to pre-Rev-4 Rev 3**: `base()` extracted
  directly from `git show HEAD:hardware/mechanical/bench-imu-01-enclosure.scad`
  (i.e. the committed Rev 3 file, before any of this session's edits) was
  independently re-exported and re-checked — identical result
  (`watertight=False`, `euler_number=−6`, same vertex/facet counts). This is
  a **pre-existing Rev 3 characteristic**, not something introduced or
  affected by this revision's additions — `base()`'s own module body is
  untouched by this population.
- **Root-caused, not just asserted as an artifact**: edge-topology analysis
  (`trimesh.edges_sorted` face-count histogram) found **zero** true boundary
  edges (edges used by only 1 face — the classic "open hole" signature) and
  **zero** odd-count edges; winding is confirmed consistent
  (`is_winding_consistent=True`) and zero faces are degenerate. The actual
  cause: **16 of 2450 unique edges (0.65%) are each shared by 4 faces instead
  of the expected 2** — the signature of a small number of coincident/
  T-junction-style duplicate tessellation seams (most likely where two
  similar-radius circular cut features in this design produce near-identical
  boundary segments after CGAL's internal polygon triangulation, which then
  export as separate-but-coincident triangles in the STL face-soup format).
  This is a genuine STL-export/tessellation quirk, not an open hole, not a
  winding/normal defect, and not a torn/missing region.
- **Authoritative check still passes.** This project's already-established
  practice (§11.G, Rev 3.1) treats OpenSCAD's own CGAL-based exact-arithmetic
  manifold check as authoritative over any third-party mesh tool's
  STL-reload-based heuristics — consistent with that practice, and given the
  root-cause above shows no genuine topological defect (no true holes, no
  winding inconsistency, no degenerate geometry), this is recorded as a
  **disclosed, diagnosed, non-blocking observation**, not a design defect.
  It does not affect the volume-based inclusion-exclusion proof above (that
  proof's arithmetic matched exactly regardless of this flag).

**18.6 Tether routing (REQ-113) — confirmed, no new cutout needed.** Checked
explicitly this session, not assumed: the bearing's own ≈55.1mm center hole,
this file's new flange bore (`bmount_flange_ir`=28.0mm radius) and the new
stand plate's own bore (`stand_plate_ir`=28.0mm radius, same axis) are all
coaxial and confirmed unobstructed — the §18.2 non-interference check above
shows none of the new mounting-boss/pilot-hole geometry intrudes into this
bore at any point. No new cutout in the existing base is required — the
existing enclosure's own connectors (J1 USB-C, J4 barrel jack, §10) remain
externally accessible on the PCB bay's side walls exactly as in Rev 3,
unchanged, which alone is sufficient to satisfy REQ-113 (a simple hanging
service loop from J1/J4 needs zero new geometry). The coaxial bore is
confirmed available as a **supplementary** path (e.g. useful if a future
revision wants to bring power up through the rotation axis instead of around
the side) but is not itself required this cycle. **One disclosed limitation,
not created by this population but confirmed unchanged by it**: a wire
entering via this coaxial bore can only continue further into the
flywheel-bay's interior through the pre-existing, unchanged ≈3.4mm-diameter
motor-shaft-clearance hole (`motor_platform()`, dead center) — a real
bottleneck for that specific path, disclosed rather than silently assumed
away, though not blocking since J1/J4 remain accessible regardless.

**18.7 Self-check against the Mechanical Reviewer's 10-item checklist**
(`.github/agents/mechanical-reviewer.agent.md`, "Mandatory checklist,"
verbatim items 1–10). This is a self-check, not a substitute for Independent
Mechanical Review — every mark below reflects this Mechanical Lead's own
assessment, offered for the Reviewer to challenge, not a pre-cleared result.

1. **PCB mounting** — N/A to this Rev 4 population (no PCB-mounting geometry
   is touched or added). Pre-existing Rev 3 PCB mounting (§5.1, §4.1) is
   confirmed unaffected — none of the new geometry is anywhere near the PCB
   bay.
2. **Connector accessibility** — ✅ J1/J4 (§10) are unaffected — the new
   geometry is entirely on the underside of the flywheel bay, nowhere near
   the PCB-bay side walls. **Caveat, not a gap**: the tether path through
   the new coaxial bore is a supplementary path only, not itself required
   for REQ-113 — see §18.6.
3. **Component height clearance** — ✅ the bearing (7.9mm CONFIRMED
   thickness) and its own mounting geometry sit entirely below the existing
   Rev 3 Z=0 floor, in newly-added territory that did not previously exist —
   there is no pre-existing component whose clearance this could infringe.
   The new Z-stack (flange 6.0mm + bearing 7.9mm + stand plate 6.0mm =
   19.9mm below old Z=0) is a straightforward named-variable sum, not a
   clearance computation against a pre-existing part.
4. **Internal clearance/interference** — ✅ against the new geometry only
   (Rev 3's own internals are unchanged, per this checklist item's own scope
   for this task). Checked and computed, not asserted: the flange/floor-disc
   overlap is confirmed non-empty via `intersection()` (§18.5, real fuse,
   not a floating touch); the new bolt-circle (40.0mm) is confirmed clear of
   both the floor-disc's outer edge (2.1mm margin) and the flange's own bore
   (10.6mm margin) by direct radial arithmetic (§18.2); the flange/stand-
   plate bore is confirmed clear of all pre-existing small cuts (M1
   clearance holes, shaft hole) by radial-containment reasoning (§18.2).
5. **Fastener placement** — ✅ caveat disclosed, not a silent gap. Wall
   thickness around each of the 4 new pilot holes is generous by
   construction (annular-band design, §18.1.1) rather than tightly
   optimized; no fastener conflicts with any other fastener or component
   (bolt-circle sits mid-band, clear of both bore and edge). **Caveat**: no
   fastener-load (torque/shear/pull-out) calculation was performed for this
   joint (§18.8) — consistent with this being explicitly out of Phase 1
   scope, mirroring the already-disclosed MISS-011 gap on the containment-cap
   joint (§12, §16) — flagged, not silently assumed adequate.
6. **Wall thickness** — ✅ `bmount_flange_t`/`stand_plate_t` (6.0mm each)
   both exceed `min_wall_t` (2.0mm) with generous margin. **Caveat, fully
   disclosed, not a clean pass**: the fused base+flange print has a genuine
   internal-overhang manufacturability finding (§18.4) that is a wall/support
   condition, not a wall-thickness condition per se — recorded under item 9
   below, not conflated with this item's own thickness-adequacy scope.
7. **Assembly order** — ✅ re-derived 4-step addendum (§18.9) extending the
   existing 6-step Rev 3 sequence (§14); no step requires reaching past an
   already-installed part from an inaccessible direction (§18.9's own
   explicit check).
8. **Basic print-fit tolerance** — ✅ `fit_clearance`(0.2mm/side) is this
   file's existing, unchanged basic tolerance allowance; no new mating
   interface was introduced by this revision that requires a print-fit
   clearance in the same sense as the containment-cap/base-flange interface
   (§11.F) — the new bearing joints are direct-fastener joints (screw into a
   pilot hole), not a sliding/press-fit mating pair, so this item's ✅ here
   specifically means "no inconsistency was introduced," not "a new
   clearance value was newly applied."
9. **Basic manufacturability/3D-printability** — **caveat, not a clean
   pass, disclosed explicitly**: the fused base+flange internal-overhang
   finding (§18.4) is a real, confirmed manufacturability issue requiring
   slicer-generated internal support material — three alternatives were
   considered and rejected (§18.4) before deciding to keep the fused design
   with this disclosed caveat. The stand plate itself has no analogous
   issue (uniform cross-section, prints flat, §18.3). This item is
   deliberately marked as a caveat rather than ✅, since a genuine rule
   violation (56mm span vs. the 10.0mm bridge-span rule) exists and is not
   fully resolved, only mitigated with a disclosed workaround.
10. **Interface-value traceability** — ✅ every new dimension in §18.1–§18.4
    above is tagged CONFIRMED/ASSUMPTION/ESTIMATE/DERIVED/DECIDED with a
    stated rationale, and traces either to DS-BRG-001, the new DS-BRG-007,
    or an explicit named-precedent (`standoff_h`, `standoff_pilot_depth`,
    `bridge_fuse_overlap`, `standoff_pilot_dia`) — no value is silently
    blended with a CONFIRMED one. `hardware/mechanical-interface.md`'s new
    Part C mirrors this same tagging discipline at the interface-fact level.

**Net self-check result: 8 of 10 items ✅ without caveat, 1 N/A (PCB
mounting), 1 disclosed caveat (item 9, internal-overhang manufacturability
finding) and 2 items (5, 6) carrying a disclosed-but-non-blocking caveat
each.** This is offered to the Independent Mechanical Reviewer as a starting
point for adversarial re-verification, not as a self-declared "reviewed" or
"approved" result.

**18.8 Fastener class — bearing-to-flange / bearing-to-stand-plate joints.**
**Decision**: self-tapping screws directly into PETG, mirroring the existing
`base_tab()`/PCB-lid joint precedent (M2.5 self-tap), rather than the
containment cap's heat-set-brass-insert precedent (§12). **Justification,
stated explicitly per this file's own established practice of re-justifying
each new joint class rather than defaulting silently**: the containment
cap's insert joint is safety-relevant and repeatedly accessed/re-torqued
over the product's life — it must resist strip-out under exactly the hazard
event it exists to contain (§8, §12). The new bearing joints are neither:
they are not defending against a specific disclosed hazard event the way the
cap is, and they are assembled once, not repeatedly opened/closed. **One
caveat disclosed, not glossed over**: unlike the PCB lid tabs (which only
carry the lid's own small mass), this joint carries the full weight of the
rotating assembly in shear/tension across the rotation duty cycle — a
different loading character than the lid-tab precedent it otherwise mirrors.
This is a first-cycle engineering judgment call, not an independently
load-tested conclusion — no fastener-load (torque/shear/pull-out)
calculation was performed for this joint, consistent with this being
explicitly out of Phase 1 scope (mirrors the already-disclosed MISS-011 gap
on the containment-cap joint, §12, §16) and flagged again at §18.10 below as
a Rev 4 open item, not silently carried forward unflagged.

**18.9 Assembly-order addendum.** Extends (does not replace) the existing
Rev 3 6-step sequence (§14). The Rev 3 sub-assembly (steps 1–6) is unchanged
and is treated as a single completed unit here:

7. Bolt the bearing's **bottom (stationary) plate** to the new stand plate —
   fully accessible, flat, done separately from the rest of the assembly.
8. With the completed Rev 3 sub-assembly held upside-down (a handling
   instruction, not a structural concern — nothing is trapped or blind at
   this step), bolt the bearing's **top (rotating) plate** to the new
   mounting flange on the underside of the base.
9. Rest/engage the two halves together via the bearing's own captive ball
   race — this is what physically unites the fixed stand-plate assembly
   (step 7) with the rotating base assembly (step 8); not itself a blind or
   inaccessible fastening step.
10. Route the tether (§18.6) through the coaxial bore just before or during
    this final stacking step.

**Trapped-part check**: no step in this addendum requires reaching past an
already-installed part from an inaccessible direction. Steps 7 and 8 are
each performed on a separate sub-assembly (stand plate alone; base assembly
alone, inverted) before the two are joined at step 9 — there is no sequence
dependency that could trap one half behind the other, mirroring the same
"last-step, nothing trapped" reasoning already established for the
containment cap in the Rev 3 sequence (§14).

**18.10 Open UNKNOWNs / ASSUMPTIONs added this revision.** Extends (does not
edit) §16's existing table — kept as a separate table here per this
revision's own zero-deletion approach to the rest of this file.

| Item | Status | Note |
|---|---|---|
| Bearing's own mounting-hole count/spacing/size | ASSUMPTION | DS-BRG-007, a generic bearing-class convention, not this SKU's confirmed pattern — must be verified against the physical part before manufacture (§18.1.1) |
| Bearing mass (≈130g) | ESTIMATE (chain of estimates) | Built from CONFIRMED OD/ID plus two further sub-estimates (plate gauge, ball race); not a single measurement — see build-up in interface.md C1 |
| Rev 3's own analytic plastic mass (≈207.9g) vs. `bom/component-selection.md`'s bounding-shell estimate (130–170g) | Disclosed discrepancy, not reconciled | Judged the analytic figure more accurate (largest contributor hand-verified) — flagged for the Hardware Lead/Reviewer to weigh, §18.3 |
| Total system mass (≈601.8g) vs. the human's own working estimate (≈280–320g) | Disclosed, ~2× higher | Attributed to the plastic-mass finding above plus new parts, not a computation error — §18.3 |
| Fused base+flange internal overhang (~56mm unsupported span) | **Disclosed manufacturability caveat, mitigated not resolved** | Requires slicer-generated internal support material; 3 alternatives considered and rejected — §18.4, self-check item 9 |
| Bearing-to-flange / bearing-to-stand-plate fastener load (torque/shear/pull-out under the rotating assembly's full weight) | UNKNOWN — no calculation performed | Explicitly out of Phase 1 scope, mirrors the existing MISS-011 gap on the containment-cap joint — §18.8 |
| Stand-plate static-margin "comfortable" judgment (6.2× at 60.0mm) | Qualitative judgment call, not a certified safety factor | No independently-cited bump-force/tip-over standard was used as a pass/fail threshold — §18.3 |
| `base()`'s own trimesh `watertight=False` flag | **Diagnosed, confirmed pre-existing (not Rev-4-caused), non-blocking** | Root-caused to 16 coincident/T-junction-style STL tessellation edges, not a true hole; OpenSCAD's own CGAL manifold check (this project's authoritative tool) passes cleanly — §18.5 |
| `base()`'s trimesh watertightness root cause — which specific pair of coincident features produces the 16 flagged edges | UNKNOWN (not pursued further) | Diagnostic depth judged sufficient for a Phase 1 paper-design self-check (no true hole, consistent winding, no degenerate faces, byte-identical to pre-existing Rev 3) — further localization would be disproportionate effort, §18.5 |

**18.11 Handoff (Rev 4).** To Independent Mechanical Review (via Hardware
Lead): `hardware/mechanical-interface.md`'s new Part C (interface-level
summary), `bench-imu-01-enclosure.scad`'s new "2B. REV 4"/"3B. MODULES"
blocks plus `reference_bearing()` and the `show_mode` updates (the actual
geometry — file now 1597 lines, up from the Rev 3 baseline's 1208), this
§18 (the full engineering derivation/verification), and the self-check in
§18.7 (offered for challenge, not a pre-cleared result). **Confirmed via
`git diff` across all three edited files this revision**
(`hardware/mechanical-interface.md`, `bench-imu-01-enclosure.scad`, this
document): Rev 3's existing content is unmodified except for one disclosed,
intentional touch — a single pre-existing `.scad` line
(`translate([0,0,0]) base();` in the "print_layout" `show_mode` branch,
changed to a Z-shifted combined `base()+bmount_flange()` call) so that
visualization mode accurately reflects that these two pieces now print as
one job; no module body, dimension, or variable definition anywhere in Rev
3's existing geometry was altered. This package does not resolve, and does
not attempt to resolve, the already-open MISS-011 gap (§16) or the
Rev 3.4 REQ-403 wall-impact/fastener-pull-out disposition (§8, §8.1) — both
remain exactly as Rev 3.4 left them, carried forward unchanged, not
re-litigated by this Rev 4 population. **Not logged as an ECO** in
`validation/change-log.md`, and `requirements/traceability-matrix.md` is not
updated — both are the Hardware Lead's responsibility after this handoff,
per this Mechanical Lead's own explicit task scope this cycle. As with every
prior revision, nothing in this section should be read as "approved" — a
fresh Independent Mechanical Review pass, covering this new §18 content
specifically, is the required next step before any human HITL gate.

---

**18.12 Rev 4.1 — MISS-023 (HIGH): REQ-407(b) pinch-point/rotating-overhang
hazard — assessment and fix.** Extends §18 additively (does not edit
§18.0–§18.11 above). Responds to Independent Mechanical Review Cycle 5,
Finding 1 (`validation/design-review.md`, "Mechanical Reviewer — Cycle 5,"
2026-09-14) / `validation/open-issues.md` row MISS-023. Full requirement
text: REQ-407(b) ("pinch points at the pivot/mechanism interface...shall be
assessed and mitigated before physical build," Must, safety-critical) and
REQ-408 (a fresh safety review is required for this new physical
configuration before its own Design-Complete-equivalent sign-off).

**18.12.1 Independent re-verification of the swept envelope — corrects the
Reviewer's own hand-derived figure.** The Cycle 5 Reviewer computed the
rotating assembly's farthest point as `assembled_envelope_y_north` (168.4mm)
minus `fw_cy` (52.5mm) = **≈115.9mm**, a pure **Y-axis** distance from the
bearing axis to the northmost point. This Mechanical Lead did not take that
figure on faith and independently re-derived it from the actual 3D geometry
rather than reusing either the Reviewer's or the original Rev 4 pass's own
number:

- Built an isolated-solid wrapper `.scad` (`include` + `show_mode` override,
  not `use`, so every named variable/module stays live) that unions **only**
  the solids that physically rotate with the bearing's own top plate —
  `base()`, `pcb_lid()`, `containment_cap()`, `bmount_flange()` — and
  explicitly **excludes** the stationary `stand_plate()`.
- Rendered with `openscad --backend=manifold` (**NoError, manifold, Genus
  10**, 5408 vertices, 10852 facets).
- Computed the true Euclidean (X,Y) distance of every mesh vertex from the
  bearing axis (`fw_cx`=53.5mm, `fw_cy`=52.5mm) with **both** `trimesh` and
  `numpy-stl` independently — the two tools agreed exactly.

**Result: true max radius = 126.424mm**, at vertex (104.0, 168.4, 21.1) — a
`base_tab()` corner tab (the same physical feature the Reviewer identified),
but the Reviewer's own figure missed that this corner's X-coordinate (104.0)
is **53.5mm off-axis** (not 0, as a pure-Y measurement implicitly assumes) as
well as Y. The true figure is **~9%/+10.5mm larger** than the Reviewer's own
115.9mm — meaning the hazard the Reviewer flagged was itself an
**under-estimate**, not an over-estimate; this is disclosed plainly rather
than quietly using the smaller, more convenient number. `rotating_env_max_r`
= 126.424 is recorded as a named `.scad` constant (line 890) rather than
silently re-embedding either figure, so `cable_wrap_circumference` (§18.13)
stays derived/re-computable from one traceable source.

**18.12.2 Height-clearance floor — the other half of "is this actually a
pinch hazard everywhere in that band."** A radius alone doesn't establish a
hazard — the rotating assembly must also occupy a height range that a
finger/hand/object at desk level could actually reach. Using the same
isolated rotating-solid mesh, face-centroid Z was swept in 1mm radius bins
across the entire candidate guard band (`stand_plate_or`=60.0mm through
`rotating_env_max_r`=126.424mm):

| Radius bin (mm) | Global min Z (mm, old-Rev-3-Z=0 frame) | Desk-relative height (mm) |
|---|---|---|
| 60–61 | 0.000 | 19.9 |
| 73–75 | 0.000 | 19.9 |
| 92–93 | 0.000 | 19.9 |
| 121–122 | 0.000 | 19.9 |

The global minimum holds at **exactly** desk-relative 19.9mm across every
sampled bin (converting via `stand_plate_bottom_z`=−19.9mm, the confirmed
desk plane, line 869) — a genuine floor, not a single-radius coincidence.
The limiting feature is the PCB-bay wall's own floor-level corner (global
Z=0, `base()`'s own pre-existing floor), **not** the taller `base_tab()`
corner tabs a first glance might suspect — those sit well above this floor
(z0=15.5mm in the old frame → desk-relative 35.4mm). Recorded as
`pinch_hazard_min_z_clear`=19.9 (line 902).

**18.12.3 Mitigation design: `pinch_guard()` (new module, line 1587) — a
5th printed piece.** A stationary annular guard, flush-adjacent to (not
fastened to, not overlapping) `stand_plate()`'s own outer edge
(`pinch_guard_ir` = `stand_plate_or` = 60.0mm by reference, line 930),
desk-resting, uniform height `pinch_guard_h` = `pinch_hazard_min_z_clear` −
`pinch_guard_z_margin` = 19.9 − 5.0 = **14.9mm** (line 948).
`pinch_guard_z_margin`=5.0mm (line 924) is an explicit **ASSUMPTION**, not a
certified safety factor — a stated engineering margin against real-world
variance (FDM sag/warp, desk unevenness, `stand_plate()`'s own manufacturing
tolerance), same honesty class as §18.3's own disclosed "comfortable, not
certified" tip-over margin. By construction (guard top strictly below the
confirmed global-minimum rotating-envelope height, at every radius in its
own band and every rotation angle — height doesn't vary with angle, so this
argument is angle-invariant) the guard **cannot** contact the rotating
assembly.

**Outer-radius sizing — explicit coverage-vs-footprint trade-off table**
(hazard annulus area = π·(126.424²−60.0²) = 38,902.4mm²; computed this
session, not reused from memory):

| `pinch_guard_or` (mm) | Coverage of hazard band | Residual radial gap (mm) | Assembled diameter (mm) |
|---:|---:|---:|---:|
| 70 | 10.5% | 56.4 | 140 |
| 90 | 36.3% | 36.4 | 180 |
| 100 | 51.7% | 26.4 | 200 |
| 110 | 68.6% | 16.4 | 220 |
| **115 (chosen)** | **77.7%** | **11.4** | **230** |
| 120 | 87.2% | 6.4 | 240 |
| 126.424 (full closure) | 100.0% | 0.0 | 252.8 |

**115.0mm was chosen**, not the full 126.424mm, for two stated reasons: (1)
diminishing returns — each further ~5mm of radius past 115mm buys
progressively less coverage while directly growing the benchtop footprint;
(2) sizing exactly to the theoretical max with **zero** margin is itself a
manufacturability/tolerance risk (any real print variance or flex could then
put the guard's own edge into contact with the rotating tab at its exact
worst-case angle) — the same class of reasoning this file already applies
elsewhere (never size a stationary clearance feature with zero margin
against a moving part). This is a **DECIDED**, disclosed judgment call, not
a derived optimum — a different, equally-defensible choice (e.g. 120mm) was
available and is recorded in the table for the Reviewer/Hardware Lead to
challenge.

**18.12.4 Manufacturability: 4-quadrant print split, no invented
printer-bed-size assumption.** `pinch_guard(quadrant)` (default `-1` = full
ring, used in "assembled" `show_mode`) draws quadrants 0–3 for
"print_layout" via `intersection()` with an exact 3-point triangle polygon
per 90° wedge (no faceting/approximation error beyond the ring's own
pre-existing `$fn`). This project has **no documented printer-bed-size
assumption anywhere** (re-confirmed this session, not assumed) — rather than
invent one, each quadrant's own bounding box (~115×115mm) is kept small
enough to be printable on virtually any consumer FDM printer, sidestepping
the question entirely.

**18.12.5 Verification performed this session (tool-based, not hand-math
alone).** Tooling: `openscad` CLI (v2026.08.30, re-confirmed present this
session — see §18.14) plus `trimesh`/`numpy-stl` (same scratch environment
Rev 4 used).

| Check | Result |
|---|---|
| `pinch_guard()` (full ring) vs. the **complete** updated rotating envelope (including this session's own new `rotation_index_pointer()`/`cable_anchor_tab()` additions — see §18.13.4/.5 re-verification below), `intersection()` | **Empty** ("Current top level object is empty") — zero shared volume, confirmed by direct boolean CSG, not inferred from the height-floor argument alone |
| `pinch_guard()` vs. `stand_plate()`, `intersection()` | Non-degenerate-looking output (96 facets) but **volume = −5.68×10⁻¹³ mm³** (i.e. exactly zero to floating-point precision; the negative sign and the accompanying negative Genus (−23) are themselves the signature of a degenerate zero-volume coincident-face mesh, not a real solid) — confirms a true **flush, non-overlapping** boundary, not an accidental interference |
| 1mm-wide test ring straddling the r=60mm boundary vs. `stand_plate()`, `intersection()` | Volume = 1123.05mm³ = **49.65%** of the full test ring's volume (2261.95mm³) — within faceting tolerance of the theoretically-expected exact 50% split, independently confirming the boundary sits precisely at r=60.0mm (no gap, no overlap) |

**18.12.6 Residual-gap disclosure and REQ-205 keep-clear-zone warning
(backstops what the guard alone does not close).** An **11.4mm residual
radial gap** remains between `pinch_guard_or` (115.0mm) and
`rotating_env_max_r` (126.424mm) — disclosed here explicitly, not folded
silently into a blanket "hazard mitigated" claim. This is backstopped by an
explicit operational warning, tightening REQ-205's existing human-attended-
operation requirement with a **hazard-zone-specific** instruction (REQ-205
itself invites exactly this: "operation shall remain human-attended...given
the new tip-over/entanglement/fast-spin hazard shapes"):

> **⚠ KEEP-CLEAR ZONE (new, Rev 4.1).** While the free-rotation mechanism is
> powered, could be commanded, or has residual spin-down motion, keep
> fingers, hands, hair, tools, and loose objects clear of the narrow annular
> band **beyond `pinch_guard`'s own outer edge** (radius >115mm, out to
> ≈126mm, from the bearing axis, at desk height) — this specific band is
> **not** covered by the physical guard. The guard itself (60–115mm radius)
> is the primary mitigation for the wider hazard band; this warning is the
> stated mitigation for the residual 11.4mm gap the guard does not close.

**18.12.7 Honest closure assessment (stated plainly, not overclaimed).**
`pinch_guard()` is a **real, verified, physical mitigation** — it converts
77.7% of the previously fully-unguarded hazard-band area into a
mechanically-guarded zone, confirmed via actual boolean-CSG collision
checking (§18.12.5), not merely asserted. It is **not** a complete/hermetic
closure of MISS-023: an 11.4mm annular gap remains, mitigated only
procedurally (§18.12.6), and the guard is a separate, unfastened,
desk-resting part (touching `stand_plate()` at r=60mm, not keyed/bonded to
it) — a disclosed limitation, not an oversight, so it could in principle
drift out of alignment over time/handling. **This Mechanical Lead's own
assessment: MISS-023 should be considered partially closed by geometry, with
the residual gap closed only by a procedural warning — not a full,
no-caveats resolution.** See §18.17 for the specific handoff recommendation.

---

**18.13 Rev 4.1 — MISS-024 (HIGH): REQ-407(c)/REQ-113 cable-entanglement/
strain hazard — assessment and fix.** Extends §18 additively. Responds to
Cycle 5 Finding 2 / MISS-024. Full requirement text: REQ-407(c) ("cable/
tether entanglement or strain at the rotating joint...shall be assessed and
mitigated before physical build," Must, safety-critical), REQ-113 (tether
"sized for several full turns before requiring manual re-centering"), and
REQ-012 ("at least ±180°, ideally continuous/unlimited rotation" — the
normal-operation exposure that makes this hazard non-rare).

**18.13.1 J1/J4 rotating-connector geometry — exact position, not
approximate.** J1 (USB-C) and J4 (barrel jack) are mounted on `base()`'s own
PCB-bay side walls (`pcb_bay_shell()`, lines 1091 ff.) — confirmed both
CONNECTORS now **rotate**, tracing the same topology the Reviewer identified:
the bearing's top (rotating) plate mates to `bmount_flange()`, which fuses
to `base()`'s own underside; the bearing's bottom (stationary) plate mates
to `stand_plate()`. Independently recomputed from the source variables
(`j1_x`/`j1_y`/`j4_x`/`j4_y`, `board_offset_x`/`_y`=3.5mm, `pcb_bay_y0`
=105.0mm, `pcb_width`=50.0mm ⟹ `j1_y`=`j4_y`=25.0mm), not taken from either
the Reviewer's or the original Rev 4 pass's prose:

| Connector | Global (X, Y) | Radius from bearing axis (53.5, 52.5) | Angle |
|---|---|---:|---:|
| J1 (USB-C) | (0.0, 133.5) | 97.073mm | 123.44° |
| J4 (barrel jack) | (107.0, 133.5) | 97.073mm | 56.56° |

Both sit at the **same** radius (mirror-symmetric about north/90°, 66.88°
apart from each other) — a confirmed geometric coincidence of this board's
own symmetric connector placement (interface.md A1/A2), not a new
Rev 4.1 design choice.

**18.13.2 Cable-wrap/turn-count derivation — conservative (safe-direction)
model, stated as such.** Rather than model the cable winding at the
connectors' own radius (97.073mm — which would under-estimate the cable
consumed per turn if the cable instead drapes against the rotating body's
own outer surface), this uses `rotating_env_max_r` (126.424mm, §18.12.1) as
the winding radius — deliberately the **larger**, safer-direction
assumption:

```
cable_wrap_circumference = 2·π·rotating_env_max_r = 2·π·126.424 = 794.345 mm/turn
```

(`.scad` line 978, `= 2 * PI * rotating_env_max_r` — kept derived, not a
second hardcoded copy of 126.424; `PI`'s validity as a built-in OpenSCAD
constant was confirmed this session via a standalone test script before
relying on it.)

**18.13.3 Mitigation: quantified turn-count limit + service-loop spec +
re-centering procedure (procedural, not geometric — and deliberately
NOT a hard mechanical stop).**

- **`pinch_guard_turn_limit` = 3** full turns, single direction, before
  **mandatory manual re-centering** (line 982) — a DECIDED value mirroring
  REQ-113's own qualitative "several full turns" language against a
  practical, storable service-loop length.
- **`cable_service_loop_min` = 2.5 meters**, each of J1's and J4's external
  service loops (line 1000) — exact requirement for 3 turns is
  794.345mm × 3 = **2.3830m**; the stated 2.5m leaves **117mm (4.91%)
  spare**, not a razor-thin margin.
- **Re-centering procedure (new, this pass):** the operator manually rotates
  the platform back to the reference (index-pointer-aligned) orientation
  after observing `pinch_guard_turn_limit` turns accumulated in one
  direction, before continuing further same-direction rotation. This is a
  **human-procedural** control, consistent with REQ-013's own already-planned
  small-speed-step, human-observed bring-up procedure — it adds no new
  sensing/firmware requirement and does not touch `firmware/**` (out of this
  pass's scope fence).
- **Explicitly rejected: a hard mechanical rotation-limit stop.** One of the
  Reviewer's own offered options ("a mechanical hard stop") was considered
  and rejected: a true kinematic hard stop would cap total rotation at a
  fixed number of turns **permanently**, directly defeating REQ-011/012's
  own stated purpose (enabling free rotation, "ideally continuous/
  unlimited"). A procedural/monitoring control (turn-count + visual index +
  documented re-centering) is judged the correct category of fix — it bounds
  the hazard without permanently foreclosing the capability the mechanism
  exists to provide.

**18.13.4 Mitigation: `rotation_index_pointer()` (new module, line 1639) —
visual turn-counting aid.** A small triangular pointer tab, fused to the
**rotating** base's own north (PCB-bay-side, far/+Y) wall exterior, centered
at `fw_cx` (53.5mm — confirmed exactly `base_outer_x`/2, a design
coincidence, not an assumption). Purpose: the operator sights this pointer
against any convenient fixed external landmark (a desk mark, the cable's own
resting position) once per full turn while manually tracking count toward
the 3-turn limit. Clearance, independently recomputed this session (not
reused from a prior, less precise "~46mm" recollection):

- Pointer spans bay-local X=[49.5, 57.5] (`rot_pointer_w`=8.0mm centered at
  `fw_cx`).
- Nearest `base_tab()` corner tabs (the 2 of 4 sharing this same north wall)
  span X=[3,11] and [96,104] (`tab_w`=8.0mm, centered at
  `board_offset_x`+{3.5,96.5}={7.0,100.0}).
- **Clearance: exactly 38.5mm on each side.**
- Z-range [7.55, 13.55] (old frame; centered on `base_total_h/2`) is clear of
  both `pcb_lid()`'s own lowest point (18.1mm) and the corner tabs' own Z
  range ([15.5, 21.1]) — no overlap with either.

**Re-verified this session (not assumed unaffected) that adding this
rotating feature does not change `rotating_env_max_r` or invalidate
`pinch_hazard_min_z_clear`**, since both figures are load-bearing inputs to
`pinch_guard`'s own sizing (§18.12) and this feature is itself part of the
rotating assembly:

- Isolated the pointer + both anchor tabs alone (excluding all pre-existing
  rotating solids) and measured directly: max radius reached = **115.500mm**
  (the pointer's own tip) — **less than** `rotating_env_max_r` (126.424mm),
  so the headline figure is unchanged; the pointer's slight (0.5mm) reach
  *past* `pinch_guard_or` (115.0mm) is not a defect — it means the pointer
  tip is visible/usable as a witness mark from outside the guard's own rim,
  which is functionally necessary for it to work as an index.
- Desk-relative height range of the pointer + both anchor tabs, measured
  directly: **[26.9, 33.45]mm** — comfortably above `pinch_guard`'s own top
  (14.9mm desk-relative) by a **12.0mm** minimum margin, confirming these new
  features do not introduce any point lower than the pre-existing 19.9mm
  floor (re-confirmed via the same 1mm-bin radius sweep against the updated
  rotating solid — global minimum in-band remained exactly Z=0.000, i.e.
  desk-relative 19.9mm, unchanged).
- Direct boolean `intersection()` of the full updated rotating envelope
  (including these 2 new features) against `pinch_guard()`: **empty** — see
  §18.12.5 table.

**18.13.5 Mitigation: `cable_anchor_tab(is_j4)` (new module, line 1670) —
strain-relief zip-tie anchor, one near J1, one near J4.** A small tab with a
vertical through-hole, so a standard zip-tie can anchor the external service
loop close to the connector rather than relying on the connector's own
solder joints/housing to react pull force — directly targets the Reviewer's
own named "yanks the connector" failure mode. Positioned at bay-local
Y=`cable_anchor_yc`=15.0mm (spans Y=[11,19]):

- Clearance to the existing J1 cutout's own Y-span [23.75, 33.25]: **4.75mm**.
- Clearance to the bay's own front edge (Y=0): **11.0mm**.
- Z-center=`cable_anchor_zc`=10.0mm, spans [7,13] — well below `pcb_lid()`'s
  own lowest point (18.1mm) regardless of X-projection distance, so no lid
  collision is possible.
- `cable_anchor_hole_dia`=3.0mm reuses this file's own existing
  `d1_hole_dia` precedent value for a small pass-through hole, sized for a
  standard small cable-tie — a generic commodity item, not a
  datasheet-specified part (consistent with this file's own established
  practice of not inventing an Evidence ID for a truly generic, non-critical
  fastener class — mirrors §18.8's own self-tapping-screw treatment).

**Self-caught wall-thickness violation, found and fixed before handoff (this
pass's own analogue of Rev 4's internal-overhang finding — caught by
re-checking this module's own printability, not just its clearance to
neighboring parts).** An earlier draft value of `cable_anchor_project`
(the tab's projection depth, i.e. its dimension in the direction the
through-hole is bored) = 4.0mm left only (4.0−3.0)/2 = **0.5mm** of wall
around the 3.0mm hole in that direction — a real, confirmed violation of
this file's own `min_wall_t`=2.0mm rule (§2/§13.1), not a hypothetical
concern. **Fixed within this same session, before this design was ever
handed off**: `cable_anchor_project` increased to **8.0mm**, leaving
(8.0−3.0)/2 = **2.5mm** of wall each side (a 0.5mm/25% margin above the
2.0mm minimum). Re-verified after the fix: both `show_mode`s still render
**NoError, manifold**, identical Genus/vertex/facet counts to before the
fix (expected — a scalar resize, not a topology change); the boolean
collision check against `pinch_guard()` remains **empty**; the max radius
contribution from this feature moved from ≈91.75mm to ≈94.31mm (still
comfortably under both `pinch_guard_or`=115mm and `rotating_env_max_r`
=126.424mm — no new clearance issue introduced). This is disclosed here
explicitly, in the same spirit as §18.4's own internal-overhang write-up,
rather than silently corrected with no record.

**18.13.6 Alternative considered and rejected: routing through the
coaxial bore instead of/in addition to fixing J1/J4 directly.** The
Reviewer's own recommended fix suggested reconsidering whether the
already-provisioned coaxial bore (interface.md C6, ≈55mm bore through
`bmount_flange()`/the bearing/`stand_plate()`) is "the better long-term
routing path," since a wire routed coaxially down the rotation axis itself
does not wind the way an external, side-mounted J1/J4 cable does. This was
considered, not dismissed reflexively — and **rejected for this pass**,
for a reason the Reviewer's own recommendation already anticipates
("this may not be a full fix on its own"): the bore is geometrically
unobstructed (§18.6) but is **~81mm away from J1/J4's own actual physical
location** (radius 97.073mm at their own angles vs. the bore sitting on the
rotation axis itself, radius 0). J1/J4 themselves are fixed, pre-existing
Rev 3 connector positions on `base()`'s own side walls (out of this pass's
scope to relocate — REQ-311/this task's own scope fence forbids touching
Rev 3 geometry) — routing a NEW internal wire from the bore to J1/J4's
existing pads would require either (a) an internal PCB-level rework (out of
Mechanical scope entirely, and would touch `hardware/schematic/**`, expressly
forbidden this pass) or (b) a slip-ring/rotary electrical union at the bore
itself, which is an unsourced, un-selected component (no candidate part,
datasheet, or Evidence ID exists for one anywhere in this project) — adopting
one now would be a new, unreviewed component decision far outside this
pass's "fix the 2 HIGH findings with additive geometry/procedure" scope.
**Flagged as CONSIDER LATER** (a genuine future-revision opportunity, not
silently dropped) rather than attempted this pass.

**18.13.7 Honest closure assessment (stated plainly, not overclaimed).**
The combination of a quantified turn-count limit, a service-loop length
specification with disclosed margin, a physical visual index feature, and
physical strain-relief anchor points is a **real, bounded, proceduralized
mitigation** — it gives an operator a concrete, actionable way to avoid the
failure modes the Reviewer identified (yanked connector, bound mechanism,
entangled user) under **bounded** (≤3-turn, then re-center) operation. **It
does not, and cannot, achieve REQ-012's own aspirational "ideally
continuous/unlimited" rotation case** — that would require either a slip
ring (rejected this pass, §18.13.6) or an operator who never lets the
platform accumulate more than 3 turns in one direction without re-centering,
which is a procedural discipline, not a hardware guarantee. **This
Mechanical Lead's own assessment: MISS-024 should be considered closed for
the REQ-113 "several full turns, bounded use" case (which this fix directly
and quantifiably satisfies), but explicitly NOT closed for REQ-012's own
"ideally continuous/unlimited" aspiration** (which REQ-113 itself already
treats as contingent/deferred — "a slip-ring/rotary electrical interface is
deferred unless bring-up shows genuinely continuous, unlimited multi-turn
rotation is required," line 162) — this pass's fix is consistent with, not
short of, what REQ-113 itself actually mandates. See §18.17 for the specific
handoff recommendation.

---

**18.14 Render/verification results (Rev 4.1, this session).** Tooling: same
as Rev 4 (`openscad` CLI v2026.08.30 — **re-confirmed present this session
via a fresh `openscad --version` check, not assumed carried over from the
prior pass's own confirmation**; `trimesh`/`numpy-stl` in a scratch Python
environment). No claim of physical fabrication, print, or fit-test is made —
this remains a paper/parametric design exercise, same as every prior
revision.

| Check | Result |
|---|---|
| Full file, "assembled" `show_mode` | OpenSCAD: **NoError, manifold, Genus 10**, 6128 vertices, 12292 facets |
| Full file, "print_layout" `show_mode` (now 5 disjoint printable pieces: base+flange+pointer+2 anchor tabs fused as piece 1, pcb_lid, containment_cap, stand_plate, and pinch_guard's 4 quadrants) | OpenSCAD: **NoError, manifold, Genus 17**, 6241 vertices, 12546 facets |
| Isolated rotating envelope (`base()`+`pcb_lid()`+`containment_cap()`+`bmount_flange()`+`rotation_index_pointer()`+`cable_anchor_tab()`×2), alone | OpenSCAD: **NoError, manifold, Genus 10**, 5408 vertices, 10852 facets |
| `rotation_index_pointer()`+`cable_anchor_tab()`×2, isolated alone (no pre-existing geometry) | OpenSCAD: **NoError, manifold, Genus 0**, 214 vertices, 424 facets |
| `intersection()`: full rotating envelope (incl. new features) vs. `pinch_guard()` (full ring) | **Empty** — zero shared volume, direct CSG proof |
| `intersection()`: `stand_plate()` vs. `pinch_guard()` | Volume ≈ 0 (−5.68×10⁻¹³mm³, degenerate/negative-Genus signature) — confirms exact flush boundary, no overlap |
| 1mm test-ring at the r=60mm boundary vs. `stand_plate()`, `intersection()` | 49.65% of the full test-ring volume — matches the theoretically-expected 50% split for an exact boundary |

All checks pass with **no new errors** introduced by this pass's geometry.
Genus/vertex/facet counts for the full-file renders are **identical before
and after** the mid-session `cable_anchor_project` wall-thickness fix
(§18.13.5) — expected, since that fix was a scalar dimension resize, not a
topology change.

**18.15 Self-check addendum against the Mechanical Reviewer's 10-item
checklist (Rev 4.1 scope only — extends, does not replace, §18.7's own
Rev 4 self-check above).**

1. **PCB mounting** — N/A, unchanged from §18.7 item 1 (no PCB-mounting
   geometry touched by this pass either).
2. **Connector accessibility** — **this is the item MISS-024 is actually
   about.** §18.7's own original mark (✅, "J1/J4 remain externally
   accessible... unchanged") was **true but incomplete** — exactly the
   Reviewer's own correct distinction (physical accessibility ≠
   entanglement/strain safety). This pass adds the assessment that was
   missing: J1/J4 remain physically accessible (still true, unchanged) AND
   the entanglement/strain question is now assessed with a disclosed,
   bounded/proceduralized fix (§18.13) — marked ✅ for the bounded-use case
   REQ-113 actually requires, explicitly **not** ✅ for REQ-012's own
   "unlimited" aspiration (§18.13.7).
3. **Component height clearance** — ✅. `pinch_guard_h` sized with a stated
   5.0mm margin below the tool-confirmed 19.9mm rotating-envelope floor
   (§18.12.2); `rotation_index_pointer()`/`cable_anchor_tab()` independently
   confirmed (not assumed) to sit at desk-relative height 26.9–33.45mm,
   clear of `pinch_guard`'s own top by a 12.0mm minimum margin (§18.13.4).
4. **Internal clearance/interference** — ✅, and checked more rigorously than
   Rev 4's own equivalent item: a direct boolean `intersection()` (not hand
   radial arithmetic alone) confirms zero shared volume between
   `pinch_guard()` and the complete rotating envelope, and confirms the
   `pinch_guard()`/`stand_plate()` boundary is exactly flush (§18.12.5,
   §18.14).
5. **Fastener placement** — N/A/✅ for `pinch_guard()` (a freestanding,
   unfastened, desk-resting piece — same category as `stand_plate()`, no new
   fastener joint introduced). `cable_anchor_tab()`'s own through-hole is
   for a zip-tie, not a threaded fastener — a different category with no
   pilot-hole/wall-thickness-around-a-screw concern in the usual sense, but
   see item 9 below for the *general* wall-thickness check this module still
   required and initially failed.
6. **Wall thickness** — **caveat, disclosed, not silently passed**:
   `cable_anchor_tab()`'s own through-hole initially left only 0.5mm of wall
   in one direction against this file's own 2.0mm `min_wall_t` rule — caught
   and fixed within this same session (§18.13.5) before handoff, not left
   for the Reviewer to find. `pinch_guard()`'s own wall (55.0mm radial
   thickness) has no such concern.
7. **Assembly order** — ✅, unaffected. `pinch_guard()` and the
   `rotation_index_pointer()`/`cable_anchor_tab()` features add to, but do
   not reorder, the existing §18.9 sequence: the guard rests around the
   stand plate at the same assembly step the stand plate itself is placed
   (both stationary, desk-resting, no fastener order dependency); the
   pointer/anchor tabs are fused to the base+flange print job (piece 1) and
   need no separate assembly step at all.
8. **Basic print-fit tolerance** — ✅, unaffected — no new
   sliding/press-fit mating interface is introduced by this pass (the
   `pinch_guard`/`stand_plate` boundary is a touching-not-mating flush
   contact, not a press fit); `fit_clearance` (0.2mm/side) remains this
   file's own unchanged basic tolerance allowance.
9. **Basic manufacturability/3D-printability** — ✅ **for this pass's own
   new geometry specifically** (distinct from §18.7 item 9's own still-open
   Rev 4 internal-overhang caveat, which this pass neither touches nor
   resolves): `pinch_guard()`'s 4-quadrant print split avoids inventing an
   undocumented printer-bed-size assumption (§18.12.4); the
   `cable_anchor_tab()` wall-thickness violation was caught and fixed
   (§18.13.5) rather than shipped with a silent caveat.
10. **Interface-value traceability** — ✅. Every new Section 2C variable is
    tagged CONFIRMED/ASSUMPTION/DERIVED/DECIDED with a stated rationale
    (`.scad` lines 876–1049); nothing is silently blended with a CONFIRMED
    value. `hardware/mechanical-interface.md` Part C is updated to match
    (§18.16 below notes what changed there).

**Net Rev 4.1 self-check result: 7 of 10 items ✅ without caveat (1, 3, 4, 5,
7, 8, 10), 1 unaffected N/A carried from §18.7 (item 1), 1 item (2) marked ✅
for a bounded scope with an explicit, honest exclusion stated, and 1 item (6)
carrying a disclosed-and-already-fixed caveat.** Offered to the Independent
Mechanical Reviewer for adversarial re-verification, not as a self-declared
"reviewed" or "approved" result — same standing offer as §18.7's own closing
line.

**Process observation (not a self-graded item, a note for the Hardware
Lead):** MISS-023/024 both fell through the original Rev 4 self-check
specifically because **none of this checklist's 10 items is itself a
safety-hazard/REQ-407 assessment** — items 1–10 are mechanical-design-quality
checks (mounting, clearance, fasteners, tolerance, manufacturability,
traceability), not safety-hazard checks. Item 2's own accessibility-vs-
entanglement conflation (this section, item 2) is a symptom of that gap, not
a one-off oversight. This Mechanical Lead is not proposing a checklist change
unilaterally (that document belongs to the Mechanical Reviewer's own agent
definition) — flagging it here so the Hardware Lead can decide whether a
recurring "safety-hazard-shape assessment" item is worth adding to that
checklist for future revisions, so a similar gap doesn't require an
Independent Review cycle to catch next time.

**18.16 Open UNKNOWNs/ASSUMPTIONs added this pass (extends, does not edit,
§18.10's own table).**

| Item | Status | Note |
|---|---|---|
| `pinch_guard()` not fastened/keyed to `stand_plate()` | **Disclosed limitation, not an oversight** | Could drift out of alignment over time/handling since the two are only touching, not bonded/keyed — §18.12.3, §18.12.7 |
| `pinch_guard`'s 11.4mm residual radial gap | **Disclosed partial closure** | Backstopped only by a procedural keep-clear-zone warning (§18.12.6), not by any further geometry this pass |
| `rotation_index_pointer()` is a convenience witness mark, not a precision index | ASSUMPTION | No fixed external reference point is provided by this design (deliberately not paired with a mark on `pinch_guard()`, which would require the guard to be rotationally keyed — an undelivered feature) — §18.13.4 |
| Cable-tie/zip-tie size for `cable_anchor_tab()`'s hole | ASSUMPTION (generic commodity hardware, no Evidence ID) | 3.0mm hole reuses `d1_hole_dia`'s own precedent; treated the same as this file's own generic-fastener precedent (§18.8), not a datasheet-tracked part — §18.13.5 |
| Coaxial-bore routing as the long-term REQ-113/REQ-012 solution | **CONSIDER LATER, not delivered this pass** | Would require either PCB-level rework (out of Mechanical scope, touches `hardware/schematic/**`) or a slip-ring/rotary union (unsourced, unselected, no candidate part or Evidence ID exists) — §18.13.6 |
| REQ-012's "ideally continuous/unlimited" rotation aspiration | **Explicitly NOT achieved by this pass's fix** | This pass closes the bounded/"several full turns" case REQ-113 actually mandates; unlimited rotation remains contingent on a future slip-ring decision REQ-113 itself already defers — §18.13.7 |
| Mechanical Reviewer's 10-item checklist has no explicit safety-hazard/REQ-407 assessment item | **Process observation, not self-graded** | Root cause of why MISS-023/024 were absent from the original Rev 4 self-check — flagged for the Hardware Lead's discretion, not unilaterally acted on (checklist ownership is the Mechanical Reviewer's) — §18.15 |

**18.17 Handoff (Rev 4.1).** To Independent Mechanical Review (via Hardware
Lead): this §18.12–§18.16 content, the `.scad` file's new "2C."/"3C." Rev 4.1
blocks plus the `show_mode` updates (file now **2014 lines**, counted
directly via `wc -l` this session, not estimated). **Pre-existing line-count
discrepancy noticed, disclosed, and deliberately NOT corrected this pass**
(not this Mechanical Lead's content to edit): the Rev 4 end-of-file banner's
own text (`.scad`, "grown from 1208 to 1526 lines") and §18.11 above ("file
now 1597 lines") disagree with each other about the Rev 4 baseline's own
final size — both predate this pass, and this Mechanical Lead has no
snapshot to adjudicate which figure was accurate at the time either was
written; flagged here rather than silently used to back-calculate a
Rev-4.1-only delta that could be wrong by ~70 lines either way. What IS
independently confirmed this session is the file's own **current** total
(2014, via `wc -l`) and — via direct review of every edit-tool call issued
this session against this file, since Rev 4 was itself never separately
committed (`git log` confirms the last commit touching this file is Rev 3's
own "2cbe846," so a plain `git diff` conflates Rev 4's and this pass's own
Rev 4.1 edits together and cannot, by itself, isolate one from the other) —
that this pass's own edits are exclusively new lines: new Section 2C
variables, new Section 3C modules, new additive sibling calls inside the
existing `show_mode` branches, and this new end-of-file addendum, with the
sole exception below. `hardware/mechanical-interface.md`'s corresponding
new Part C entries (if any) are noted in that file's own change notes. No
Rev 3 or Rev 4 module body,
dimension, or variable definition was resized, moved, or removed, with the
sole disclosed exception of `cable_anchor_project`, which is itself a
**Rev 4.1** value (defined earlier in this same session/pass, not a Rev 3 or
Rev 4 value), corrected once before handoff (§18.13.5). **This Mechanical
Lead's own recommended disposition, for the Hardware Lead to weigh (not a
self-declared resolution)**:

- **MISS-023**: recommend moving to a **partially-resolved / re-verify**
  state, not a full RESOLVED — the physical guard closes 77.7% of the hazard
  band with a tool-verified zero-collision fit, but the residual 11.4mm gap
  is closed only procedurally (§18.12.6/.7). Whether that residual-gap
  disposition is acceptable is a judgment call for the Hardware Lead/human,
  not something this Mechanical Lead can unilaterally declare closed.
- **MISS-024**: recommend moving to **RESOLVED for the REQ-113 "several full
  turns" scope**, with an explicit standing note (not a new open issue) that
  REQ-012's own "unlimited" aspiration remains contingent on a future
  slip-ring decision that REQ-113 itself already treats as deferred, not
  newly discovered by this pass (§18.13.6/.7).

Neither disposition should be read as this Mechanical Lead declaring its own
work reviewed or approved — a **fresh Independent Mechanical Review pass**,
specifically covering this Rev 4.1 geometry (not a re-review of Rev 4's
already-closed items), is the required next step before any human HITL gate,
exactly as §18.11 already stated for Rev 4 and as this pass's own end-of-file
`.scad` banner restates for Rev 4.1. **Not logged as an ECO** in
`validation/change-log.md`, and `validation/open-issues.md`/
`validation/design-review.md` are not edited by this Mechanical Lead — both
are the Hardware Lead's responsibility after this handoff, per this task's
own explicit scope.

