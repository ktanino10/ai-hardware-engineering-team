# Texas Instruments DRV10970 Datasheet — Rev UNKNOWN (SLVSCU7A)

- **Manufacturer**: Texas Instruments
- **Part Number**: DRV10970
- **Datasheet Title**: "DRV10970 Sensored Sinusoidal-Drive BLDC Motor
  Driver" (as titled on TI's own product page)
- **Revision / Version**: Literature number **SLVSCU7**, this session's
  live TI product-page fetch showed an "A" revision suffix context
  (**SLVSCU7A**) — same caveat as the DRV10983 record: not independently
  re-transcribed byte-for-byte against the raw PDF cover page this session.
- **Publication Date**: UNKNOWN (TI page showed "PRODUCTION DATA" status,
  not a print date)
- **Official URL**: https://www.ti.com/lit/ds/symlink/drv10970.pdf (URL
  confirmed to resolve to a real TI-hosted document this session; the
  specific numeric/feature claims below come from TI's live-fetched HTML
  product page, same caveat as DRV10983 above)
- **Retrieved Date**: 2026-08-31
- **Local cache note**: not committed; content read live via web fetch of
  TI's HTML product/EVM pages this session, not the raw PDF text; not
  cached to any local disk.
- **Used for Evidence IDs**: DS-MTR-042, DS-MTR-043, DS-MTR-044, DS-MTR-045,
  DS-MTR-046, DS-MTR-047, DS-MTR-048

## Known gaps (honestly flagged, not guessed)

- Package thermal resistance (theta-JA) and exact thermal-shutdown
  threshold were not available from the HTML pages fetched this session —
  recorded as `UNKNOWN`.
- This part is **not** the recommended driver candidate — its hardware
  requirement for Hall-effect sensors on the motor is fundamentally
  incompatible with this cycle's recommended sensorless T-Motor
  MN2206-13 2000KV motor (see `bom/component-selection.md` "Motor Driver
  IC" section). It remains a real, well-documented option worth
  reconsidering only if a future revision instead adopts a Hall-sensored
  BLDC motor (e.g. the Anaheim BLY171D-24V-4000 candidate in the motor
  comparison), and even then its 18V absolute maximum input would need
  re-checking against that motor's 24V nameplate rating.
