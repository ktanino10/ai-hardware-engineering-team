# Samsung Electro-Mechanics CL21A106KAYNNNE Datasheet — Rev UNKNOWN

- **Manufacturer**: Samsung Electro-Mechanics
- **Part Number**: CL21A106KAYNNNE
- **Datasheet Title**: "CL21A Series — General-Purpose MLCC, 0805, X5R" (per manufacturer/distributor product page)
- **Revision / Version**: UNKNOWN (not confirmed this session)
- **Publication Date**: UNKNOWN (not confirmed this session)
- **Official URL**: https://www.digikey.com/en/products/detail/samsung-electro-mechanics/CL21A106KAYNNNE/3888549 ; also listed at LCSC (https://www.lcsc.com/product-detail/C15850.html)
- **Retrieved Date**: 2026-09-02
- **Local cache note**: not committed; content verified via live web search this session
- **Used for Evidence IDs**: DS-PASS-004

## Why this citation

**10µF, 0805, X5R, 25V** — real, currently-listed part (DigiKey + LCSC,
cross-checked across 2 distributors) matching this board's own stated
target for C10/C13: `hardware/schematic/bench-imu-01/README.md` line 118
states "10µF (U5 VCC/VREG decoupling, **≥16-25V-class rail**)," 0805
package, "**ASSUMPTION, deliberately not 0603** — 10µF ceramic at this
voltage class faces real DC-bias capacitance derating in an 0603 case
size... 0805 is the more reliable, still-small choice." 25V is the top of
that stated range, chosen deliberately for margin rather than the bare
minimum.

**DC-bias derating checked at this design's actual operating voltage, not
just the part's nominal/rated figure (per this session's own task
instruction)**: this design's real VM_MOTOR/U5-VCC operating envelope is
bounded 9.0–13.0V (`bench-imu-01-design.md` §7.5.9), not the part's 25V
rating. Samsung's own published DC-bias derating curve for this
series/case/dielectric combination (X5R, 0805, 25V-rated, 10µF nominal)
shows substantial capacitance loss well below the rated voltage —
approximately 50–60% of nominal remaining at ~12V DC bias (i.e., roughly
5–6µF effective, not the full 10µF nameplate value), continuing to
~20–40% remaining (≈2–4µF) if biased all the way to the full 25V rating.
**This is a real, disclosed characteristic, not a defect newly introduced
by this sourcing pass** — it is the same underlying physical effect the
existing design record already flagged as its reason for choosing 0805
over 0603 in the first place (0805's larger dielectric volume derates
less severely than 0603 would at the same value/voltage/DC-bias point,
not "not at all"). Recorded here so a future reader sees the actual
expected effective capacitance at this board's real operating point, not
just the 10µF nameplate figure. Not independently re-derived from a
different, higher-capacitance-margin part in this pass — that would be a
schematic-level (DRV10983 decoupling network) re-design, out of scope for
a BOM-sourcing task.
