# Maxon RE 16 Ø16mm, Graphite Brushes, 4.5W (P/N 118725) Datasheet — Version 2025

- **Manufacturer**: Maxon Motor AG / maxon group
- **Part Number**: 118725 (RE 16 Ø16mm, graphite brushes, 4.5W family; this
  specific SKU is the base motor, no gearhead/encoder combination)
- **Datasheet Title**: Catalog page PDF, "Cataloge-Page-EN-155.pdf" (maxon's
  own generated per-product catalog-page export — not a traditional
  multi-product family datasheet; exact printed title string on the page
  itself not independently re-transcribed this session beyond the filename)
- **Revision / Version**: 2025 (maxon's own catalog version year, as encoded
  in the product page/PDF metadata)
- **Publication Date**: 2025-03-21 (per this session's live product-page
  fetch)
- **Official URL**: https://www.maxongroup.us/medias/sys_master/root/9398012805150/Cataloge-Page-EN-155.pdf
  (manufacturer-hosted, live-fetched this session) — cross-referenced against
  the live maxongroup.us product page for P/N 118725 for the same figures.
- **Retrieved Date**: 2026-08-31
- **Local cache note**: not committed; content read live via web fetch this
  session, not cached to any local disk.
- **Used for Evidence IDs**: DS-MTR-001, DS-MTR-002, DS-MTR-003, DS-MTR-004,
  DS-MTR-005, DS-MTR-006, DS-MTR-007, DS-MTR-008

## Known gaps (honestly flagged, not guessed)

- Body length, shaft diameter/flat, and mounting-hole pattern beyond the
  16mm body diameter were surfaced by this session's research sub-agent
  labeled "from training data, not confirmed this session" — **not treated
  as datasheet-confirmed** and therefore **not cited with an Evidence ID**;
  the comparison table in `bom/component-selection.md` marks these
  dimensions `UNKNOWN` rather than repeating an unverified figure. Only the
  16mm body diameter (from the product family name itself, corroborated by
  the live-fetched product page) is treated as confirmed.
- This part is disqualified from this cycle's recommendation on budget
  (~2.7x the Rev 3 subsystem target) and lifecycle (NRND) grounds — see
  `bom/component-selection.md` "Motor (Reaction Wheel Drive)" section. Its
  spin-up/thermal-margin numbers remain useful reference data regardless,
  since they establish that a small brushed DC motor *can* physically meet
  the torque target for short-duration spin-up even though its continuous
  rating alone looks inadequate at first glance — a nuance worth preserving
  for any future revisit of this candidate.
