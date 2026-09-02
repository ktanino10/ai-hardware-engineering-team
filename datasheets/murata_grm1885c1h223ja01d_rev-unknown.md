# Murata GRM1885C1H223JA01D Datasheet — Rev UNKNOWN

- **Manufacturer**: Murata Manufacturing
- **Part Number**: GRM1885C1H223JA01D
- **Datasheet Title**: "GRM188 Series — General-Purpose MLCC, 0603, C0G (NP0)" (per manufacturer/distributor product page)
- **Revision / Version**: UNKNOWN (not confirmed this session)
- **Publication Date**: UNKNOWN (not confirmed this session)
- **Official URL**: https://www.digikey.com/en/products/detail/murata-electronics/GRM1885C1H223JA01D (product ID 490-13371-1-ND per this session's search — exact numeric DigiKey product-detail URL suffix not independently re-fetched this session)
- **Retrieved Date**: 2026-09-02
- **Local cache note**: not committed; content verified via live web search this session
- **Used for Evidence IDs**: DS-PASS-005

## Why this citation

22nF, 0603, **C0G (NP0)** dielectric, 50V — real, currently-listed part.
C0G/NP0 chosen over X7R for C17 specifically because C17 is a
timing/ramp-rate-setting capacitor (U6's dVdT pin, setting the
inrush-current-limiting ramp rate — `bench-imu-01-design.md` §7.5.10),
not a simple bypass/decoupling cap: C0G/NP0's near-zero
temperature-coefficient and tighter tolerance make it the more
appropriate dielectric choice for a value that directly sets a timing
characteristic, versus X7R's larger temperature/DC-bias-dependent
capacitance variation. The existing BOM note already permitted either
("generic X7R/C0G") — this citation exercises the C0G option specifically
for that reason, not arbitrarily.
