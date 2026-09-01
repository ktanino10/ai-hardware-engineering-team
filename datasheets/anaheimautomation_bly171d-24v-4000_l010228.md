# Anaheim Automation BLY171D-24V-4000 (BLY17 Series) Datasheet — Rev UNKNOWN

- **Manufacturer**: Anaheim Automation, Inc.
- **Part Number**: BLY171D-24V-4000 (BLY17 series, 24V winding, 4000 RPM
  rated speed, "D" = with driver-compatible 5-wire Hall/motor-lead harness)
- **Datasheet Title**: "BLY17 Series Spec Sheet"
- **Revision / Version**: Document number **L010228** (no separate
  letter-revision found this session)
- **Publication Date**: UNKNOWN (not printed/found on the fetched pages this
  session)
- **Official URL**: https://anaheimautomation.com/media/anaheim/files/manuals/brushless/L010228_-_BLY17_Series_Spec_Sheet.pdf
  (manufacturer-hosted; also cross-checked against a mirrored copy on
  analog.com, consistent with the primary)
- **Retrieved Date**: 2026-08-31
- **Local cache note**: not committed; content read live via web fetch this
  session, not cached to any local disk.
- **Used for Evidence IDs**: DS-MTR-009, DS-MTR-010, DS-MTR-011, DS-MTR-012,
  DS-MTR-013, DS-MTR-014, DS-MTR-015, DS-MTR-016

## Known gaps (honestly flagged, not guessed)

- Pole count (needed for exact Hall-edge-per-mechanical-revolution firmware
  math) was not found on the fetched spec sheet pages this session —
  recorded as `UNKNOWN` in `bom/component-selection.md`, not assumed.
- Peak/intermittent torque figure (~219 mN·m / 31 oz-in) is only partially
  confirmed — the spec sheet's peak-torque row was legible but the exact
  duration/duty-cycle basis for "peak" was not.
- This part is not the recommended candidate this cycle (see
  `bom/component-selection.md` "Motor (Reaction Wheel Drive)" section) —
  mass (~299g, ~3x the 100g flywheel target) and price (~73-87% of the
  whole Rev 3 subsystem budget alone) are the deciding factors, not any
  electrical inadequacy; it is in fact heavily over-specified on torque
  (~12.6x the 5 mN·m target) and is the only candidate with integrated Hall
  sensors, so it remains a reasonable fallback if the recommended candidate
  fails bring-up.
