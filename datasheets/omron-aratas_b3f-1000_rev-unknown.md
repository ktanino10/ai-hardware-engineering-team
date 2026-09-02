# Omron (now Aratas) B3F-1000 Datasheet — Rev UNKNOWN

- **Manufacturer**: Omron Electronic Components — DigiKey's own current
  listing shows this part transitioned to "Aratas (Formerly Omron
  Components)" as the manufacturer of record; same physical part, a
  manufacturer-name/ownership transition, not a different component —
  disclosed here rather than silently picking one name
- **Part Number**: B3F-1000
- **Datasheet Title**: "B3F Series — 6mm Tactile Switch, SPST-NO, Through-Hole" (per manufacturer/distributor product page)
- **Revision / Version**: UNKNOWN (not confirmed this session)
- **Publication Date**: UNKNOWN (not confirmed this session)
- **Official URL**: https://www.digikey.com/en/products/detail/aratas-formerly-omron-components/B3F-1000/33150
- **Retrieved Date**: 2026-09-02
- **Local cache note**: not committed; content verified via live web search this session
- **Used for Evidence IDs**: DS-SW-001

## Why this citation

Real, currently-orderable, standard 6mm×6mm through-hole momentary
tactile pushbutton switch, SPST-NO (normally-open) — matches SW1's stated
role exactly: "Momentary N.O. pushbutton (6mm THT)" tied to MCU NRST for
manual reset (`bench-imu-01-design.md`: "also → SW1 → GND (momentary)" on
the NRST net). 100gf actuation force is a standard/typical value for this
switch class, no special force requirement stated in the design record.
