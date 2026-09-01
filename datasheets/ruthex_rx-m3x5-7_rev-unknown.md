# Ruthex RX-M3x5.7 Brass Heat-Set Threaded Insert — Product Page (Rev UNKNOWN)

- **Manufacturer**: Ruthex (Ruthex GmbH), Germany
- **Part Number**: RX-M3x5.7 (order code GE-M3x57-001), 100-piece pack
- **Datasheet Title**: No formal PDF datasheet found/published for this SKU
  this session — dimensional and material spec is presented directly on the
  manufacturer's own product page (not a downloadable document), the same
  situation already accepted for `datasheets/tmotor_mn2206-13-2000kv_rev-unknown.md`.
- **Revision / Version**: UNKNOWN — product-page spec table, not a
  versioned document.
- **Publication Date**: UNKNOWN
- **Official URL**: Ruthex's own product page (ruthex.de, RX-M3x5.7
  listing) — **directly fetched and read live this session** (not inferred
  from a search-engine summary). Confirms: M3 thread, 5.7mm insert length,
  ~4.6mm knurled OD, brass construction, intended for FDM-printed
  thermoplastics (PLA/PETG/ABS/Nylon-class), installed via soldering
  iron/heat-set method.
- **Retrieved Date**: 2026-09-13
- **Local cache note**: not committed; content read live via direct web
  fetch this session, not cached to any local disk.
- **Used for Evidence IDs**: DS-FAST-001

## Why this reference matters here

This design's own `.scad` source (`bench-imu-01-enclosure.scad`) specifies
`heatset_od`=4.6mm / `heatset_len`=5.7mm as an **ASSUMPTION** (not tied to a
specific purchased part number) for the 6× M3 heat-set inserts used to
fasten `containment_cap()` over the flywheel bay. This real, commercially
available part (Ruthex RX-M3x5.7) matches those assumed dimensions almost
exactly — a striking, honest corroboration that the design's assumed
insert geometry corresponds to a real, purchasable component, not an
arbitrary or physically-unrealistic guess. This does **not** upgrade the
design's own `heatset_od`/`heatset_len` fields from ASSUMPTION to CONFIRMED
(no purchase order or BOM line ties this specific part number to this
project), but it does support treating **this part's own published pull-out
performance** (see `datasheets/cnckitchen_petg-threaded-insert-pullout-test_web-article.md`,
DS-FAST-002, which tests this exact insert brand) as a reasonable,
checkable proxy for the design's assumed insert.

## Known gaps (honestly flagged, not guessed)

- No manufacturer-published pull-out or torque-out force rating appears on
  Ruthex's own product page itself — the pull-out figure used in this
  project's MISS-011 estimate comes from an independent third-party physical
  test (DS-FAST-002/DS-FAST-003), not from Ruthex's own marketing material.
- No fatigue, temperature-derating, or vibration-loosening data published.
