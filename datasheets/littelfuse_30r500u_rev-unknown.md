# Littelfuse 30R Series (30R500U) Resettable PPTC Datasheet — Rev "GD.04/09/25"

- **Manufacturer**: Littelfuse, Inc.
- **Part Number**: 30R500U (from the 30R Series family datasheet, which
  covers 30R090U through 30R900U in one document — radial-leaded PPTC
  resettable fuses)
- **Datasheet Title**: "Resettable PPTC Datasheet" / "30R Series Radial
  Leaded" (as printed on the document's own header/footer)
- **Revision / Version**: document control code "Revised: GD. 04/09/25"
  printed on the document itself — recorded verbatim as the
  best-available identifier, not a conventional "Rev N" number (hence
  this file's own "rev-unknown" naming, matching the convention already
  used for T-Motor's MN2206-13 2000KV datasheet)
- **Publication Date**: "© 2025 Littelfuse, Inc." on each page; not
  independently distinguished this session from the revision control
  code above (same bundled date/revision convention as the SMBJ Series
  datasheet, DS-PROT-004's source)
- **Official URL**: https://www.littelfuse.com/assetdocs/littelfuse_ptc_30r_datasheet?assetguid=46bd151a-f029-4cec-aeef-2614869244f4
  (manufacturer-hosted datasheet PDF, confirmed reachable and
  text-extractable this session via an `r.jina.ai` reader proxy, same
  approach already used for DS-PROT-004/005's source documents)
- **Retrieved Date**: 2026-09-06
- **Local cache note**: not committed; content read live via the
  `r.jina.ai` text-extraction proxy this session; full Electrical
  Characteristics table and Temperature Rerating (Ihold-derating) table
  captured directly from the primary document; not cached to any local
  disk.
- **Used for Evidence IDs**: DS-PROT-006

## Key extracted figures (30R500U row, Electrical Characteristics table)

| Parameter | Value |
|---|---|
| I hold (hold current, 20°C still air) | 5.00 A |
| I trip (trip current, 20°C still air) | 10.00 A |
| V max | 30 Vdc |
| I max (max fault current @ V max) | 40 A |
| P d (typ., dissipated when tripped) | 3.0 W |
| Max Time-To-Trip: Current / Time | 25.00 A / 14.50 sec |
| R min (initial, un-soldered) | 0.010 Ω |
| R 1max (post-trip, measured 1hr after trip @ 20°C) | 0.050 Ω |
| Agency approvals | UL/CSA-class marks present (both "X" columns) |

## Temperature Rerating (Ihold derating vs. ambient), 30R500U row

| Ambient | -40°C | -20°C | 0°C | 20°C | 40°C | 50°C | 60°C | 70°C | 85°C |
|---|---|---|---|---|---|---|---|---|---|
| Hold current (A) | 7.25 | 6.50 | 5.75 | 5.00 | 4.15 | 3.85 | 3.40 | 3.05 | 2.60 |

Used in `bench-imu-01-design.md` §7.5.9 to confirm F1's derated hold
current remains at/above this design's ≤3A worst-case motor current
through the datasheet's own 70°C point, dropping below 3A only between
70°C and 85°C ambient (≈71.7°C by linear interpolation between those two
published points) — comfortably above REQ-201's 40°C ambient design
target.

Environmental spec (same document, separate table): operating temperature
range −40°C to +85°C; maximum device surface temperature in tripped state
125°C.

## Why this part / why not a lower- or higher-rated 30R-series sibling

Selected as the new PTC resettable fuse for the motor power input (J4)
on Bench-IMU-01 Rev 4 (`bench-imu-01-design.md` §7.5.9, ISS-019). Sized
against this design's own **Ihold ≥ nominal current, Itrip reasonably
close to (not wildly above) the ≤3A absolute-worst-case current** goal,
using the same 30R-series family table for a same-document comparison:

| Part | Ihold | Itrip | Fits this design? |
|---|---|---|---|
| 30R400U | 4.00A | 8.00A | Ihold too close to the ≈1.05A nominal/≤3A worst-case pair — less headroom before a nuisance trip during a legitimate 3A transient (e.g. start-up) |
| **30R500U (chosen)** | **5.00A** | **10.00A** | Ihold clears the ≤3A worst-case with ≈40% headroom (avoiding nuisance trips on legitimate worst-case current), while Itrip (10A) still trips well before J4's own mechanical failure point |
| 30R600U | 6.00A | 12.00A | Larger unnecessary headroom above the ≤3A worst-case current; no benefit for this design's own current profile, and a higher initial/post-trip resistance is not needed |

30R500U was judged the best fit for a design whose real operating current
(≈1.05A nominal, ≤3A absolute worst-case, DS-MTR-056) sits well below its
own 5.0A rated hold current, while still tripping at a genuinely
fault-level current (10.0A) rather than an implausibly high one.

## Known gaps (honestly flagged, not guessed)

- **Itrip (10.00A) exceeds J4's own 5.0A connector rating** (DS-CONN-005)
  — F1 is not a precisely-matched current limiter for J4 itself; a fault
  current between J4's 5.0A rating and F1's 10.0A trip point would
  exceed J4's own rating before F1 trips. F1's real protective value is
  against genuine short-circuit-level fault currents (well above 10A,
  tripping in seconds per its own time-to-trip curve), not as a tight
  bound on J4's own rating — flagged in `bench-imu-01-design.md` §7.5.9/
  §16 (a true input eFuse/active current-limiting stage would close this
  gap, not selected this revision as it is judged an architecturally
  significant addition).
- **No max-initial resistance figure is published** — only R min
  (initial, un-soldered) and R 1max (post-trip) are given; this design's
  §7.5.2/§7.5.9 UVLO-margin analysis therefore uses an ESTIMATE (0.02Ω
  assumed in-circuit resistance × 3A ≈ 0.06V added worst-case drop), not
  a datasheet-sourced max-initial figure — flagged for Hardware Reviewer
  to confirm or tighten (`bench-imu-01-design.md` §16 item 26).
- **"Time to trip" (14.5 sec typical at the datasheet's own 25.00A test
  current) is not the same as the trip time at F1's own 10.00A Itrip
  threshold** — the datasheet's single published time-to-trip data point
  is at a much higher test current (25A) than F1's own minimum trip
  current (10A); trip time at currents just above 10A would be
  substantially longer (PPTC devices trip faster at higher overcurrent
  ratios) — not independently modeled or curve-read this session, treated
  as a residual gap rather than assumed favorable.
