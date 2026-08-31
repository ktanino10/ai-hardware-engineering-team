# Texas Instruments TPS26631 (TPS2663x family) Datasheet — Rev UNKNOWN

- **Manufacturer**: Texas Instruments
- **Part Number**: TPS26631 — specifically the **TPS26631PWPR** orderable
  variant (HTSSOP-20 "PWP" package, tape & reel). Part of the shared
  **TPS2663x** datasheet family covering TPS26630/31/32/33, which differ in
  default overload-fault response (latch-off vs. auto-retry), 2×IOL
  pulse-current support, and PLIM (output power limiting) — not in their
  core voltage/current-limit/OVP/UVLO architecture. See "Family variant
  differences" below.
- **Datasheet Title**: "TPS2663x 60-V, 6-A Power Limiting, Surge Protection
  Industrial eFuse" (one combined datasheet covers all 4 family members).
- **Revision / Version**: UNKNOWN (literature number **SLVSFxx**-class not
  independently transcribed this session — the PDF itself was not
  text-extractable via this session's tooling; see Local cache note).
- **Publication Date**: UNKNOWN (not confirmed this session).
- **Official URL**: https://www.ti.com/lit/ds/symlink/tps2663.pdf
  (TI's own literature symlink for the TPS2663x family datasheet; a mirrored
  copy was also seen hosted at
  `https://www.mouser.com/datasheet/2/405/1/tps2663-1951129.pdf`).
- **Retrieved Date**: 2026-09-08.
- **Local cache note**: not committed; content read this session via (1)
  TI's own product page (ti.com/product/TPS26631), (2) an alldatasheet.com
  HTML mirror of the TPS26630 variant of the same combined datasheet
  (`alldatasheet.com/html-pdf/2231317/TI2/TPS26630/63/1/TPS26630.html`),
  and (3) a TI E2E community forum post
  ("TPS2663: Difference between TPS26630 and TPS26631",
  e2e.ti.com/support/power-management-group/power-management/f/
  power-management-forum/1354964) corroborating the SHDN pin's internal
  pull-up behavior — no direct PDF byte-for-byte read was possible this
  session (binary/non-text-extractable via this session's `web_fetch`
  tooling, same limitation already logged against several other parts in
  this evidence set, e.g. DS-MTR-040's DRV10983 citation).
- **Used for Evidence IDs**: DS-PROT-010, DS-PROT-011, DS-PROT-012,
  DS-PROT-013, DS-PROT-014, DS-PROT-020, DS-PROT-023, DS-PROT-024,
  DS-PROT-025, DS-PROT-026, DS-PROT-027, DS-PROT-028, DS-PROT-029,
  DS-PROT-030, DS-PROT-031.
- **Rev 5 addendum (Circuit Engineer, 2026-09-08)**: this session obtained
  a directly text-extractable copy of the full combined datasheet
  (literature number **SLVSE94G**, confirmed from the extracted text
  itself — resolving the "Revision / Version: UNKNOWN" limitation above
  for citation purposes going forward, though the field above is left
  as Component Engineer originally recorded it per this log's
  point-in-time convention) and cross-verified its internal page
  numbering against the PDF's own "Submit Document Feedback   N" footer
  text. This closed several gaps flagged below and is the basis for
  DS-PROT-023 through DS-PROT-031 (see `datasheets/evidence-log.md`),
  used for §7.5.10/§7.5.9 of `hardware/schematic/bench-imu-01-design.md`
  Rev 5.

## Family variant differences (TPS26630 / 31 / 32 / 33)

All four share the same pinout and the same core adjustable-UVLO /
adjustable-OVP-cutoff / adjustable-current-limit architecture. They differ
only in:

| Variant | Default overload-fault response (MODE pin still overrides) | 2×IOL pulse-current support (≤25.5 ms) | PLIM (output power limiting) | Factory-preset 34.3 V OVP option (tie OVP→GND) |
|---|---|---|---|---|
| TPS26630 | Latch-off | No | No | Yes |
| **TPS26631 (recommended)** | Auto-retry | **Yes** | No | Yes |
| TPS26632 | Latch-off | No | Yes | No |
| TPS26633 | Auto-retry | Yes | Yes | No |

TPS26631 was selected within the family specifically because (a) its
2×IOL pulse-current tolerance is a genuine functional fit for a motor
driver's start-up inrush current profile (TI's own applications list
names "Motor drives – CNC, encoder supply" explicitly, see below), (b) it
does not need PLIM (26632/26633's differentiator) for this application,
and (c) it is the one family member with a real, confirmed HTSSOP-20
("PWPR") orderable part number and live DigiKey pricing found this
session — TPS26630/32/33's availability specifically in a leaded package
was not confirmed with equal confidence.

## Key extracted figures

| Parameter | Value | Note |
|---|---|---|
| Operating input voltage | 4.5 V – 60 V | |
| Absolute maximum input voltage | 67 V | comfortably exceeds even U5's own 30 V VCC absolute maximum rating (DS-MTR-053) |
| Integrated FET R_DS(on) | 31 mΩ | |
| Adjustable current limit range | 0.6 A – 6 A (via RILIM pin resistor) | comfortably spans this design's ≥3 A need |
| Overvoltage protection | Adjustable "OVP Cut Off" via external resistor divider on the OVP pin — a true lockout (switch disables), not merely a clamp; OR an optional factory-preset 34.3 V cutoff by tying OVP directly to GND (TPS26630/31 only) | this design needs its own custom ≈13 V threshold, so the factory 34.3 V preset is **not** used — the adjustable-divider path is the one relied upon |
| Undervoltage lockout | Adjustable via a separate, independent UVLO pin (own external resistor divider) | confirmed as a genuinely separate pin from OVP, not a shared/dual-purpose pin |
| Fault-response mode select | MODE pin: latch-off or auto-retry, user-selectable regardless of the part's factory default | |
| Package | HTSSOP-20 ("PWP"), leaded — hand-solderable, matching this project's established package preference | |
| Applications (per TI's own datasheet Applications section) | "Factory automation and control – PLC, DCS, HMI, I/O modules, sensor hubs; **Motor drives – CNC, encoder supply**; Electronic circuit breakers" | direct, on-point evidence this device class is marketed for exactly this design's use case |
| Price (TPS26631PWPR) | $4.52 (DigiKey, qty 1, cut-tape); $3.43 (qty 10); $2.86 (qty 100) | checked 2026-09-08 |
| Lifecycle / availability | In stock at DigiKey, ships same day per DigiKey's own listing (checked 2026-09-08) — no explicit manufacturer lifecycle statement (e.g. "Active"/"NRND") was independently re-read this session; live in-stock status at a major distributor is treated as strong-but-indirect evidence of active production, not a substitute for a direct lifecycle statement |

## SHDN pin native bias — the critical default-state caveat

TPS2663x's **SHDN** pin (the logic-level enable input) has an internal
**1 MΩ pull-up to a 2.7 V internal rail**, with a rising enable threshold
of approximately 2 V, per a TI E2E community forum post directly
addressing this question (semi-primary source; not independently
re-confirmed against the PDF's own pin-description table this session).
This means **a floating/undriven SHDN pin defaults the device ON** — the
*opposite* of this design's default-OFF/fail-safe requirement (REQ-403).

Achieving default-OFF therefore requires Circuit Engineer to add an
**external pull-down resistor** from SHDN to GND, sized to reliably
override the internal 1 MΩ pull-up (a standard, low-risk, well-understood
biasing technique — not a novel or fragile workaround) so that SHDN reads
reliably low whenever no active MCU drive is present (MCU unpowered, GPIO
tri-stated, or GPIO not yet configured during boot), while still being
easily overridable by an active-high push-pull GPIO drive when the MCU
does want the switch enabled. This is flagged here as a **required
external component**, not a hidden assumption — the exact resistor value
is Circuit Engineer's schematic-level decision, not this record's.

**Rev 5 addendum (Circuit Engineer, 2026-09-08, DS-PROT-025)**: the full
datasheet's own Figure 8-1 (Functional Block Diagram, page 16) confirms
the same **1 MΩ** figure as this section's E2E-forum source — but only
in the illustrative block diagram, with **no corresponding row in the
formal Electrical Characteristics table**. The human/task independently
re-confirmed a different figure, **≈440 kΩ**, via a fresh web search this
same engagement (`bom/component-selection.md` Approval table). Both
figures point the same direction (native default-ON, needing an external
pull-down to invert to default-OFF per REQ-403) and neither is a
guaranteed datasheet spec, so the discrepancy does not change the
default-OFF requirement itself. Circuit Engineer's actual pull-down
sizing (R11 = 10 kΩ, this design) is **not** based on either pull-up
figure — it is based on the datasheet's own separately-guaranteed SHDN
leakage/pulldown-sizing spec instead (§8.3.13, page 28: pulldown must
sink ≥10 µA; DS-PROT-024), which is robust regardless of which pull-up
figure is correct (10 kΩ dominates a 440 kΩ–1 MΩ pull-up by 44–100×).
The 1 MΩ-vs-440 kΩ discrepancy itself remains an open, non-blocking
item flagged for Hardware Reviewer/Component Engineer awareness (see
design doc §16 item 27) — not resolved in favor of either source here.

## Reference design / EVM

TI's **TPS26630-33EVM** is a real, published evaluation module for this
family. Its default installed configuration evaluates TPS26630RGE/
TPS26633RGE, but TI's own EVM documentation explicitly states the user
"can substitute the TPS26631RGE for TPS26630RGE when specifically
evaluating the TPS26631" — i.e. **TPS26631 is an explicitly documented,
supported substitution on this same board**, not merely an inference
from family membership. A second, narrower EVM (TPS2663-166EVM) also
exists, covering TPS26633/TPS16630 specifically on 2 separate channels —
not the primary citation here since it does not name TPS26631. Checked
this session (DS-PROT-020).

## Known gaps (honestly flagged, not guessed)

- No independent read of the datasheet's own numbered Absolute Maximum
  Ratings / Electrical Characteristics tables was possible this session
  (PDF not text-extractable); all figures above come from TI's own HTML
  product page, an alldatasheet.com text mirror of the same combined
  family datasheet, and a TI E2E forum post — multiple independent
  sources, but none is a direct page-numbered PDF read.
  **RESOLVED (Rev 5, Circuit Engineer, 2026-09-08)**: a directly
  text-extractable copy of the full SLVSE94G PDF was obtained and its
  page numbering cross-verified against the PDF's own footer text this
  session (see Rev 5 addendum above). AMR/ROC tables read directly from
  page 2; Electrical Characteristics tables read directly from pages
  6–8. See DS-PROT-023 through DS-PROT-031.
- Exact UVLO pin threshold range/accuracy and OVP pin threshold
  range/accuracy (needed to size the actual resistor dividers for this
  design's 9.0–13.0 V envelope) are **UNKNOWN this session** — deferred to
  Circuit Engineer's detailed design phase, which will need the full
  primary datasheet (or a working PDF-reading pass) to size the dividers
  correctly.
  **RESOLVED (Rev 5, Circuit Engineer, 2026-09-08)**: §9.2.2.2 (page 31)
  read directly, giving Equations 9–10 and the guaranteed
  V(UVLOR)/V(OVPR) = 1.176/1.200/1.224 V (min/typ/max) reference values,
  hysteresis, and ±150 nA guaranteed leakage, plus TI's own 20×-leakage
  divider-current design rule. Used to independently re-derive
  R12=887 kΩ/R13=60.4 kΩ/R14=88.7 kΩ against this design's own
  9.0–13.0 V envelope, using the exact guaranteed reference/hysteresis/
  leakage values directly rather than an assumed placeholder. See
  DS-PROT-026 and design doc §7.5.10.
- PGOOD/FLT pin exact fault-reporting behavior (which specific fault
  classes each pin reports, timing) is **UNKNOWN this session** beyond
  the pin names themselves — relevant to how firmware distinguishes an
  OVP-triggered shutdown from a current-limit-triggered one, deferred to
  Circuit Engineer/Firmware Engineer.
  **PARTIALLY ADDRESSED, still open (Rev 5, Circuit Engineer,
  2026-09-08)**: Circuit Engineer's Rev 5 design leaves PGOOD/FLT/IMON
  floating (sanctioned by TI's own standard Electrical Characteristics
  test condition, which uses IMON=PGOOD=FLT=OPEN throughout — see
  DS-PROT-030) rather than wiring them to the MCU, because this design's
  MCU-GPIO budget and the firmware-side fault-differentiation policy are
  both outside this revision's scope (ISS-020/ISS-021 remain open
  firmware-policy items per design doc §7.5.11/§7.5.12 — see
  `validation/open-issues.md`). This sidesteps rather than resolves the
  original informational gap: the exact per-pin fault-class timing is
  still not transcribed here, and would need to be if/when firmware
  wiring to PGOOD/FLT is added in a future revision.
- Thermal data (θJA, package power dissipation limits) **UNKNOWN this
  session** — should be closed before Circuit Engineer finalizes PCB
  copper-pour/thermal layout, same caveat pattern already applied to
  DRV10983 (DS-MTR-039) and DRV10970 (DS-MTR-048) in the Motor Driver
  section.
  **RESOLVED (Rev 5, Circuit Engineer, 2026-09-08)**: Thermal
  Information table (page 2) gives RθJA=32.2°C/W for the PWP
  (HTSSOP-20) package specifically; Electrical Characteristics table
  (pages 6–7) gives R(ON)=26/30.44/34.5 mΩ (25°C)/33–45 mΩ (85°C) and
  T(TSD)=165°C typ. Full conduction-loss/ΔTJ/margin analysis against
  ROC(125°C)/AMR(150°C)/T(TSD)(165°C) completed in design doc §7.5.10
  and re-checked in §15's Rev 5 self-check. See DS-PROT-031.
