# Texas Instruments LM5069 Datasheet — Rev UNKNOWN (SNVS452-class)

- **Manufacturer**: Texas Instruments (originally National Semiconductor).
- **Part Number**: LM5069 family — specifically the **LM5069MM-1/NOPB**
  orderable variant (10-pin VSSOP, marked package code "MME"; also seen
  listed under the reel-only ordering code LM5069MMX-1/NOPB). The **"-1"**
  suffix denotes the **latch-off** overload-fault-response variant, as
  distinct from **LM5069MM-2/NOPB** ("-2", auto-restart) — the "-1"
  variant is the one relevant to this design's latching requirement and
  is the only one cited here; the "-2" variant was not further researched
  since it does not fit function #3's latching need without additional
  external logic.
- **Datasheet Title**: "LM5069 Positive High Voltage Hot Swap / Inrush
  Current Controller with Power Limiting" (title as seen via a mirrored
  copy of the datasheet; literature number pattern **SNVS452**-class per
  a mirrored PDF filename `snvs452d.pdf` seen this session — not
  independently re-confirmed against TI's own literature portal this
  session, so recorded as "SNVS452-class" rather than a confirmed exact
  revision letter).
- **Revision / Version**: UNKNOWN (see above).
- **Publication Date**: UNKNOWN.
- **Official URL**: https://www.ti.com/product/LM5069 (TI's own product
  page).
- **Retrieved Date**: 2026-09-08.
- **Local cache note**: not committed; content read this session via TI's
  own product page, an alldatasheet.com HTML mirror of the LM5069MM-2
  datasheet pages (same base datasheet family as the "-1" variant cited
  here), and a third-party PDF mirror — no direct primary-PDF read of the
  "-1" variant's own datasheet pages was independently performed this
  session; the "-1"/"-2" distinction itself is stated on TI's own product
  page and is a standard, well-documented TI convention for this device
  family.
- **Used for Evidence IDs**: DS-PROT-017, DS-PROT-018, DS-PROT-022.

## Key extracted figures

| Parameter | Value | Note |
|---|---|---|
| Operating input voltage | 9 V – 80 V | widest voltage range of the 3 candidates; comfortably covers this design's 9.0–13.0 V envelope with large margin on both ends |
| Overload-fault response | **LM5069-1: latches off**, requires input power-cycle or EN/UVLO-pin toggle to reset; LM5069-2: auto-restarts | "-1" variant selected to match function #3's latching intent at the hardware-autonomous level (see this record's own note on how this compares to the firmware-driven mechanism, in the parent BOM section) |
| Undervoltage lockout (UVLO) | Adjustable via an external resistor divider from VIN to GND, referenced against an internal 2.5 V reference; independent of the OVLO divider | |
| Overvoltage lockout (OVLO) | Adjustable via a **separate, independent** external resistor divider, same 2.5 V internal reference | UVLO and OVLO are confirmed genuinely independent (2 separate divider networks), a design-cleanliness advantage over Candidate B's shared EN/UVLO pin |
| Current limiting | Via an external current-sense resistor between VIN and the controller's sense pins — fully adjustable to any current limit needed, at the cost of an added sense resistor and its own power dissipation | |
| Gate drive | Charge-pumps the external MOSFET's gate to approximately 12 V above the source/output node, regardless of VIN — ensures full logic-level-independent enhancement of the external FET even at low input voltages within the 9–80 V range | |
| Package | 10-pin VSSOP ("MME") — leaded, hand-solderable | |
| Price (LM5069MM-1/NOPB) | $4.39 (DigiKey, qty 1, cut-tape/Digi-Reel); volume pricing down to ≈$1.90 (qty 500) | checked 2026-09-08; **supersedes** an earlier, less-precisely-sourced ≈$6.88 estimate from a prior research pass this same engagement — the $4.39 figure is tied to a specific, confirmed orderable part number and live DigiKey listing and is treated as the more reliable number |
| Lifecycle / availability | Live DigiKey listing found and priced (checked 2026-09-08); no explicit manufacturer "Active"/"NRND" statement independently re-read this session |

## UVLO/ON (enable) pin native bias

The device's enable comparator (referred to informally here as
"UVLO/ON," since enable and undervoltage-lockout share the same
functional gate on this device) has a rising enable threshold above
approximately 2.5 V (the same internal reference used for the UVLO/OVLO
dividers), and — per this session's research — **floating/undriven
leaves the device in its OFF (disabled) state**, natively matching this
design's default-OFF/fail-safe requirement (REQ-403) **without needing an
external pull resistor purely to invert an opposing internal bias**, the
one respect in which this candidate is cleaner than Candidates A and B.
This is not independently re-verified against a primary datasheet
pin-description table this session (see Known gaps) — recorded with the
same confidence level as the rest of this record's secondary-sourced
figures, not elevated above them.

## Reference design / EVM

TI's **LM5069EVM-627** confirmed this session as a real, published
evaluation module for the LM5069 controller, with onboard jumpers/test
points specifically for adjusting UVLO, OVLO, current/power limit, and
fault timers — directly relevant to this design's own §7.5.10 divider-
sizing needs (constraint 2, continuous OVP referenced to 9.0–13.0V).
This EVM covers the LM5069 controller portion only, not the complete
LM5069 + external-FET + current-sense-resistor combination as this
design would actually build it (see the companion IRLZ44N record —
generic discrete MOSFETs have no dedicated EVM, none expected/needed).
TI's own datasheet is additionally described (via the same secondary
sources) as including typical-application schematics showing the UVLO/
OVLO divider networks and their governing equations — a further positive
sign for Circuit-Engineer-phase implementation, though not independently
confirmed as motor-supply-specific this session. Checked this session
(DS-PROT-022).

## Known gaps (honestly flagged, not guessed)

- No independent primary-datasheet PDF read of the LM5069-1 variant
  specifically this session — the "-1"/"-2" latch/auto-restart
  distinction is stated clearly and consistently across TI's own product
  page and secondary sources, but the exact pin-level mechanics of how
  "-1" achieves its latch (e.g., whether the latch applies only to a
  current-limit-timeout fault, or also extends to OVLO/UVLO excursions)
  is **UNKNOWN this session** — flagged explicitly in the parent BOM
  section's Recommendation reasoning, since this affects how much of
  function #3's latching behavior is provided natively by the chip versus
  needing to be implemented in firmware regardless of which candidate is
  chosen (see that section's discussion).
- Exact current-sense-resistor sizing methodology, gate-resistor/timing-
  capacitor values, and thermal data (θJA) are **UNKNOWN this session** —
  deferred to Circuit Engineer's detailed design phase.
- This candidate requires an external N-channel MOSFET (see the
  companion `infineon_irlz44npbf_unknown-rev.md` record) and additional
  passives beyond the 2 resistor dividers (current-sense resistor,
  gate-related components) not individually priced this session beyond a
  rough order-of-magnitude estimate in the parent BOM section.
