# Polymaker — PolyMax(TM) PETG Technical Data Sheet (Rev V5.4)

- **Manufacturer**: Polymaker
- **Part Number**: PolyMax(TM) PETG filament (1.75mm / 2.85mm)
- **Datasheet Title**: PolyMax PETG TDS
- **Revision / Version**: V5.4 (per the PDF's own filename,
  `PolyMax_PETG_TDS_EN_V5.4.pdf`, linked from Polymaker's own wiki page).
- **Publication Date**: UNKNOWN (PDF link query string date-stamped
  2024-11-18, which is a CDN/hosting timestamp, not necessarily the
  document's own publication date).
- **Official URL**: wiki.polymaker.com/polymaker-products/more-about-our-products/documents/technical-data-sheets/petg-pet/polymax-tm-petg
  (HTML wiki page mirroring the TDS table; PDF itself at
  cdn.shopify.com/s/files/1/0548/7299/7945/files/PolyMax_PETG_TDS_EN_V5.4.pdf)
  — **this session directly fetched the HTML wiki page and read its full
  "MECHANICAL PROPERTIES" table directly** (genuine primary-source read,
  not a search-engine summary — unlike the Prusament PETG citation,
  DS-MTL-001, whose underlying PDF could not be parsed by this session's
  tools).
- **Retrieved Date**: 2026-09-13
- **Local cache note**: not committed; content read live via direct web
  fetch this session, not cached to any local disk.
- **Used for Evidence IDs**: DS-MTL-002

## Key figures (directly read from the fetched table, ISO 179/ISO 527 methods)

| Property | X-Y (in-plane) | Z (through-layer) |
|---|---|---|
| Notched Charpy impact strength | 11.6 ± 0.8 kJ/m² | 2.4 ± 0.6 kJ/m² |
| Tensile strength | 37.9 ± 1.4 MPa | 29.4 ± 1.0 MPa |
| Young's modulus | 1684 ± 135 MPa | 1603 ± 40 MPa |
| Elongation at break | 5.22 ± 1.5 % | 3.10 ± 0.51 % |

## Why this reference matters here

A second, independent, brand-different PETG material-property source for
this project's MISS-011 wall-impact estimate, complementing
`datasheets/prusament_petg_tds-2021-10.md` (DS-MTL-001). Two points stand
out:

1. The **X-Y/Z anisotropy ratio here (≈4.8x on notched Charpy) is
   substantially larger** than Prusament's own published ≈2x split — real
   brand-to-brand variation exists, so this project's wall-impact estimate
   correctly treats the anisotropy figure as a range/order-of-magnitude
   input, not a single precise constant.
2. Polymaker's own **tensile strength (X-Y: 37.9 MPa) is notably lower**
   than both Prusament's published figure (~46-50 MPa) and CNC Kitchen's
   own independently-measured PETG (~50 MPa, `datasheets/cnckitchen_petg-threaded-insert-pullout-test_web-article.md`,
   DS-FAST-002) — a real, checkable illustration that "PETG" is not one
   single material property set; different commercial filament brands
   genuinely vary by ~30%+ on this property. This project's wall-impact
   estimate (§8.1 of `bench-imu-01-dimensional-spec.md`) uses a range
   spanning multiple brands for exactly this reason, rather than treating
   any single brand's figure as universally representative of "PETG."

## Known gaps (honestly flagged, not guessed)

- Standard ISO 179 Charpy/ISO 527 tensile test speeds are quasi-static —
  far below the REQ-403 event's ≈69.74 m/s effective impact speed. Same
  ductile-to-brittle high-strain-rate caveat as DS-MTL-001 applies.
- This is one specific commercial PETG brand/formulation; the design does
  not commit to this specific brand (Manufacturing Engineer's spec names
  PETG or nylon-class material generically, not a specific brand).
