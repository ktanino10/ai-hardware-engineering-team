# Texas Instruments DRV10983 Datasheet — Rev UNKNOWN (SLVSCP6H)

- **Manufacturer**: Texas Instruments
- **Part Number**: DRV10983 (also sold as DRV10983Q1 automotive-grade
  variant, not the variant considered here)
- **Datasheet Title**: "DRV10983 Sensorless Sinusoidal-Drive BLDC Motor
  Driver" (as titled on TI's own product page)
- **Revision / Version**: Literature number **SLVSCP6**, this session's
  live TI product-page fetch showed a "H" revision suffix context
  (**SLVSCP6H**) but the PDF's own cover-page revision letter was not
  independently re-transcribed byte-for-byte this session (the PDF itself
  was binary/not text-extractable via this session's tooling) — recorded
  as the best-available identifier, not to be treated as a byte-for-byte
  confirmed revision letter.
- **Publication Date**: UNKNOWN (not confirmed this session — TI's page
  showed a "PRODUCTION DATA" status marker, not a print date)
- **Official URL**: https://www.ti.com/lit/ds/symlink/drv10983.pdf (URL
  confirmed to resolve to a real TI-hosted document this session; TI's own
  HTML product page at ti.com/product/DRV10983 was live-fetched and is the
  actual source of the specific numeric/feature claims below, since the PDF
  itself could not be text-extracted this session)
- **Retrieved Date**: 2026-08-31
- **Local cache note**: not committed; content read live via web fetch of
  TI's HTML product/EVM pages this session, not the raw PDF text; not
  cached to any local disk.
- **Used for Evidence IDs**: DS-MTR-032, DS-MTR-033, DS-MTR-034, DS-MTR-035,
  DS-MTR-036, DS-MTR-037, DS-MTR-038, DS-MTR-039, DS-MTR-040, DS-MTR-041

## Known gaps (honestly flagged, not guessed)

- Package thermal resistance (theta-JA) and the exact thermal-shutdown
  threshold/behavior were not available from the HTML pages fetched this
  session — recorded as `UNKNOWN`. Package body dimensions (24-HTSSOP)
  beyond the pin count/pitch were likewise not independently confirmed.
- This is the **recommended driver candidate**, paired with the T-Motor
  MN2206-13 2000KV motor recommendation — see
  `bom/component-selection.md` "Motor Driver IC" section for full
  compatibility/trade-off reasoning. Its data here is TI HTML-product-page
  verified (higher confidence than the Toshiba TC78B009FTG candidate in
  this same comparison, whose equivalent facts are only secondary-source
  confirmed this session) but is still one level below a literal
  page-numbered PDF-table citation — flagged honestly rather than
  overstated.
