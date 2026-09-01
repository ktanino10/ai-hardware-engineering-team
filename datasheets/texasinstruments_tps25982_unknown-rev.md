# Texas Instruments TPS25982 Datasheet — Rev UNKNOWN

- **Manufacturer**: Texas Instruments
- **Part Number**: TPS25982 family — specifically the **TPS259822ONRGER**
  orderable variant (24-pin VQFN "RGE" package, tape & reel). A sibling
  orderable variant, TPS259827ONRGER, was also seen in distributor listings
  (same package, different current-limit-range/OVP factory-trim option
  per the part-number suffix) but was not separately researched this
  session since the package/pricing conclusion is the same either way.
- **Datasheet Title**: "TPS25982 2.7-V to 24-V, 2.7-mΩ, 15-A eFuse with
  Hot-Swap..." (title as seen via a distributor-hosted datasheet mirror;
  full title not independently re-transcribed from a primary TI PDF this
  session).
- **Revision / Version**: UNKNOWN.
- **Publication Date**: UNKNOWN.
- **Official URL**: https://www.ti.com/lit/gpn/TPS25982 (TI's own generic
  part-number literature link).
- **Retrieved Date**: 2026-09-08.
- **Local cache note**: not committed; content read this session via TI's
  own product/ordering page (ti.com/product/TPS25982, including its
  part-details page for TPS259827ONRGER) and a Mouser new-products listing
  page for the TPS25982 family — no direct PDF read was possible this
  session (same binary/non-text-extractable limitation as other parts in
  this evidence set).
- **Used for Evidence IDs**: DS-PROT-015, DS-PROT-016, DS-PROT-021.

## Key extracted figures

| Parameter | Value | Note |
|---|---|---|
| Operating input voltage | 2.7 V – 24 V | |
| Absolute maximum input voltage | 30 V | closely matches U5's own 30 V VCC absolute maximum rating (DS-MTR-053) — essentially zero extra margin between the switch's own ceiling and the load IC's own ceiling, unlike Candidate A's TPS2663x (67 V AMR, wide margin over U5) |
| Integrated FET R_DS(on) | 2.7 mΩ | best-in-class of all 3 candidates by a wide margin — would all but eliminate any 3S/UVLO-margin erosion concern from switch resistance (ISS-014 context) |
| Adjustable current limit range | 2 A – 15 A | comfortably spans this design's ≥3 A need, widest range of the 3 candidates |
| Overvoltage protection | Adjustable, set via the same physical **EN/UVLO** pin as the enable/UVLO function (a combined, dual-purpose pin rather than 2 independent pins) | requires more careful resistor-divider design than Candidate A's separate SHDN/UVLO/OVP pins, since the enable-logic threshold and the UVLO/OVP thresholds interact on the same node |
| Undervoltage lockout | Same EN/UVLO pin as above | see above — a real design-cleanliness disadvantage vs. Candidate A |
| Fault-response mode select | Latch-off / auto-retry selectable | |
| Package | **VQFN-24 ("RGE") only** — no HTSSOP, SOIC, or other leaded package option found for this family this session (confirmed via a dedicated follow-up search of TI's own ordering/part-details pages) | a real, project-relevant hand-solderability disadvantage per this project's established, repeatedly-applied preference against leadless QFN/WSON/DFN packages (see e.g. the WSON regulator candidate and the WQFN-36 motor-driver candidate, both non-selected partly on this basis) |
| Price (TPS259822ONRGER) | ≈$4.29 (DigiKey, qty 1) | prior-session figure, not re-verified with a fresh search this pass; treated as a reasonably reliable estimate given it was itself sourced from a live distributor listing |
| Lifecycle / availability | Live TI ordering/part-details page found and in stock per prior-session research; no explicit "Active"/"NRND" statement independently re-read this session | |

## EN/UVLO pin native bias — the critical default-state caveat

TPS25982's combined **EN/UVLO** pin has **no internal pull-up or
pull-down bias** per the datasheet's own explicit warning that this pin
must not be left floating (prior-session finding). This means a floating
EN/UVLO pin is in an **undefined** state — worse than Candidate A's
"defined-but-wrong-direction" native bias, in the sense that there is no
documented default behavior to reason about at all absent an external
resistor. Achieving default-OFF/fail-safe (REQ-403) requires Circuit
Engineer to add an external pull-down resistor, similar in principle to
Candidate A's mitigation, but complicated by this pin's dual EN+UVLO
duty — the same resistor network used to guarantee a default-off state
also directly sets the UVLO threshold, so the two functions cannot be
tuned fully independently the way Candidate A's separate SHDN and UVLO
pins allow.

## Reference design / EVM

**No TPS25982-specific EVM found this session.** TI's closest published
evaluation module is the **TPS259824OEVM**, built for the close sibling
device TPS259824O and described in secondary-source summaries as "pin-
and function-compatible for most use cases" with TPS25982 — a reasonable
stand-in, but not a device-specific confirmation the way the TPS26630-33
EVM is for Candidate A (which explicitly names TPS26631 as a supported
substitution). Recorded as a real, if secondary, disadvantage for this
candidate on this scoring dimension. Checked this session (DS-PROT-021).

## Known gaps (honestly flagged, not guessed)

- No independent primary-datasheet PDF read this session — all figures
  above come from TI's own HTML product/ordering pages and a Mouser
  listing page, corroborating but not replacing a full datasheet read.
- Exact EN/UVLO pin threshold voltage and its relationship to the OVP
  function (how the two are actually differentiated on one pin — e.g. by
  direction of crossing, or by a separate internal comparator on the same
  node) is **UNKNOWN this session** — this is exactly the kind of detail
  that would need to be nailed down before Circuit Engineer could safely
  use this pin, and is one of the reasons this candidate is judged
  design-cleanliness-inferior to Candidate A even though its raw R_DS(on)
  and current-limit-range specs are superior.
- Thermal data (θJA) **UNKNOWN this session**.
- Reference design / EVM: see the dedicated section above — resolved to
  "no exact-part EVM, close-family stand-in exists" rather than left as a
  blank UNKNOWN.
