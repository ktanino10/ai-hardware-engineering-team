# Lite-On LTST-C191KRKT Datasheet — Rev UNKNOWN

- **Manufacturer**: Lite-On Inc.
- **Part Number**: LTST-C191KRKT
- **Datasheet Title**: "LTST-C191KRKT — 0603 SMD Red LED" (per manufacturer/distributor product page)
- **Revision / Version**: UNKNOWN (not confirmed this session)
- **Publication Date**: UNKNOWN (not confirmed this session)
- **Official URL**: https://www.digikey.com/en/products/detail/liteon/LTST-C191KRKT/386837
- **Retrieved Date**: 2026-09-02
- **Local cache note**: not committed; content verified via live web search this session
- **Used for Evidence IDs**: DS-OPTO-001

## Why this citation

**Directly satisfies a real, stated design constraint, not just "any
generic 0603 LED."** `bench-imu-01-design.md`'s own parts table records
D1 as "Generic indicator LED | MPN not selected; **Vf≈2.0V assumed**" —
R5 (330Ω, the LED's own series current-limit resistor) was sized against
that 2.0V assumption. LTST-C191KRKT: red, 631nm, **Vf = 2.0V typical @
20mA**, 0603 (1608 metric) SMD package — matches the assumed forward
voltage essentially exactly. **Deliberately not** a blue/white/
high-brightness-green LED (typical Vf ≈2.8–3.4V for those colors/
technologies) — picking one of those would silently invalidate R5's
existing value without anyone re-deriving it, since the actual LED
current would end up substantially different from what R5 was sized for.
No specific color requirement is stated elsewhere in the design record
beyond "generic indicator," so red (the most common/lowest-Vf indicator
color, and the best match to the existing 2.0V assumption) is the correct
choice.
