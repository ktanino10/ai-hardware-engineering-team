# CNC Kitchen — "Helicoils, Threaded Insets and Embedded Nuts in 3D Prints: Strength Assessment" (web article, Rev UNKNOWN)

- **Manufacturer**: N/A — this is an independent, third-party physical test
  article/blog post (CNC Kitchen, a well-known independent
  engineering-testing publisher), not a manufacturer's own datasheet. Cited
  the same way `datasheets/orientalmotor_basics-of-stepper-motors_web-article.md`
  is cited for a non-manufacturer technical reference.
- **Part Number**: N/A — tests multiple threading methods (direct-thread,
  Ruthex heat-set insert, Helicoil, side-pocket nut, bottom-pocket nut) in
  M3, on the author's own DIY "Universal Test Machine."
- **Datasheet Title**: "Helicoils, Threaded Insets and Embedded Nuts in 3D
  Prints: Strength Assessment" (cnckitchen.com blog article; exact title as
  browsed this session).
- **Revision / Version**: UNKNOWN (web article, not a versioned document).
- **Publication Date**: UNKNOWN (article references testing "PLA... this
  time... PETG" as a follow-up to a prior video/article).
- **Official URL**: cnckitchen.com/blog/helicoils-threaded-insets-and-embedded-nuts-in-3d-prints-strength-amp-strength-assessment
  — **directly fetched and read in full live this session** (not a
  search-engine summary; the actual article prose, including its numeric
  results, was read directly).
- **Retrieved Date**: 2026-09-13
- **Local cache note**: not committed; content read live via direct web
  fetch this session, not cached to any local disk.
- **Used for Evidence IDs**: DS-FAST-002

## Why this reference matters here (and why it is this project's PRIMARY fastener evidence)

This is the single most directly-comparable real data point available for
this design's MISS-011 fastener pull-out estimate, because the test's own
conditions match this project's actual context on every relevant axis:
**M3** thread size, **PETG** print material (this design's own Manufacturing
Engineer spec proposes PETG or nylon-class material), **Ruthex-brand
heat-set insert** (matching `datasheets/ruthex_rx-m3x5-7_rev-unknown.md`,
DS-FAST-001, almost exactly on OD/length), and **axial pull-out** loading
(the same load direction relevant to a fragment striking the underside of
`containment_cap()`).

## Key figures extracted (read directly from the article's own prose)

- Test method: flat PETG test coupons, 4 perimeters, 100% infill, printed on
  a Prusa printer; 3 samples tested per threading method; loaded to failure
  on the author's own "Universal Test Machine" (a purpose-built axial-pull
  tensile rig), all methods tested at the same pull rate for comparability.
- **Ruthex M3 heat-set insert in PETG: average pull-out failure load ≈119 kg
  ≈1167 N** (3-sample average; insert "ripped out" at this load).
- For context/cross-check, the same article's other methods in the same
  PETG batch: direct-thread-into-plastic ≈118 kg (≈1157 N, threads sheared);
  Helicoil ≈120 kg (≈1177 N, threads sheared); side-pocket embedded nut ≈86
  kg (≈844 N, weakest); bottom-pocket embedded nut ≈166 kg (≈1628 N,
  strongest, but a different mechanical arrangement not used by this
  design). The insert, direct-thread, and Helicoil results cluster tightly
  (≈1150–1180 N) despite different failure mechanisms, which is itself a
  useful corroboration of internal consistency.
- The article's own author-measured PETG tensile strength figure, used in
  its own follow-on shear/strength-prediction calculation: **≈50 MPa** —
  independently cross-checks the ~46–50 MPa figure reported for Prusament
  PETG's own published TDS (`datasheets/prusament_petg_tds-2021-10.md`,
  DS-MTL-001), from a completely independent (physical-test, not marketing
  datasheet) source.
- The article explicitly notes PETG performed **worse** than PLA in the same
  test methodology (a prior article/video) — i.e. this figure is not a
  best-case/cherry-picked number for PETG specifically.

## Known gaps (honestly flagged, not guessed)

- Small sample size (n=3 per method) — a real physical test, but not a
  statistically large population; a legitimate scatter band around this
  average should be assumed, not treated as a precise, non-varying number.
- Test coupon geometry (flat plate, "special holders" on a bench rig) is
  not identical to this design's actual `containment_cap()` boss geometry
  (surrounding wall thickness, boss diameter, edge distance to the part
  perimeter all differ) — this is a good **proxy** for single-insert
  pull-out capacity in printed PETG, not a direct substitute for a test of
  this exact part's own geometry.
- Load rate/strain rate of the "Universal Test Machine" pull test is not
  stated in ratio to the disclosed REQ-403 impact event's much higher
  effective strain rate (69.74 m/s rim speed) — the same
  quasi-static-vs-high-strain-rate caveat already disclosed for the Charpy/
  Izod-based wall estimate (§8.1 of `bench-imu-01-dimensional-spec.md`)
  likely also applies here, direction not independently re-derived for
  fasteners specifically.
