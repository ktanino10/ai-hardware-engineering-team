# Samsung Electro-Mechanics CL10B (0603, X7R, 50V) Series Datasheet — Rev UNKNOWN

- **Manufacturer**: Samsung Electro-Mechanics
- **Part Number**: CL10B104KB8NNNC (100nF); CL10B105KB8NNNC (1µF); CL10B474KB8NNNC (0.47µF) — same 0603/X7R/50V case-size/dielectric/voltage family, differing only in the capacitance-code digits of the part number (`104`=100nF, `105`=1µF, `474`=0.47µF per Samsung's own EIA capacitance-code convention)
- **Datasheet Title**: "CL Series — General-Purpose MLCC, 0603, X7R" (per manufacturer/distributor product pages)
- **Revision / Version**: UNKNOWN (not confirmed this session)
- **Publication Date**: UNKNOWN (not confirmed this session)
- **Official URL**: https://www.digikey.com/en/products/detail/samsung-electro-mechanics/CL10B104KB8NNNC/3886658 (100nF); https://www.digikey.com/en/products/detail/samsung-electro-mechanics/CL10B105KB8NNNC/3886673 (1µF); https://octopart.com/part/samsung/CL10B474KB8NNNC (0.47µF — exact DigiKey numeric product-ID suffix not independently re-confirmed this session; a DigiKey search for this exact string surfaced a similar but distinct sibling part, `CL10B474KA8NNNC` — note the "A8" vs "B8" — so the 0.47µF citation relies on Octopart/GlobalSpec's independent confirmation that `CL10B474KB8NNNC` [with "B8"] is itself a real, separate, valid Samsung part number rather than a DigiKey listing page)
- **Retrieved Date**: 2026-09-02
- **Local cache note**: not committed; content verified via live web search this session
- **Used for Evidence IDs**: DS-PASS-001 (100nF), DS-PASS-002 (1µF), DS-PASS-003 (0.47µF)

## Why this citation

**Voltage rating independently re-verified, not taken from a single
unverified search answer.** An initial search pass mis-stated
CL10B105KB8NNNC's rating as "25V" — this was independently re-checked via
2 follow-up, more targeted searches, both confirming the actual rating is
**50V** (the "B8" segment of Samsung's own part-numbering scheme is a
voltage-class code, consistently 50V across all 3 capacitance values in
this family — cross-checked on 104/105/474 alike). Flagging this
correction explicitly rather than silently using the first (wrong)
figure.

**Consolidation rationale**: rather than sourcing a separate real MPN
for every one of this board's 0603 general-purpose decoupling caps, one
50V-rated family is used across every 0603 X7R position that has no
stricter individually-stated requirement, since a higher voltage rating
always safely covers a lower stated minimum:
- **100nF (CL10B104KB8NNNC)** covers C3, C4, C5, C6, C7 (no stated
  voltage requirement beyond the 3.3V logic domain they sit on), **and**
  C11 (design doc: "0.1µF/10V," `bench-imu-01-design.md` line 1602 —
  50V ≥ 10V) **and** C12 (design doc: "rated ≥VCC×2" — this design's own
  actual VM_MOTOR/U5-VCC ceiling is 13.0V per §7.5.9, so the real
  requirement is ≥26V; 50V clears this with real margin).
- **1µF (CL10B105KB8NNNC)** covers C1, C8, C9 (3.3V logic domain, no
  special requirement), C14/C15 (design doc: "1µF/5V" — 50V ≥ 5V), and
  C16 (existing BOM note: "≥16-25V rated" — 50V clears this too).
- **0.47µF (CL10B474KB8NNNC)** covers C2 (3.3V logic domain, no special
  requirement).
