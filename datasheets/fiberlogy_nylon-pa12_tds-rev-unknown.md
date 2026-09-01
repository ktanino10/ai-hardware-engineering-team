# Fiberlogy — Nylon PA12 Technical Data Sheet (Rev UNKNOWN)

- **Manufacturer**: Fiberlogy
- **Part Number**: Fiberlogy Nylon PA12 filament (1.75mm / 2.85mm)
- **Datasheet Title**: FIBERLOGY_NYLONPA12_TDS
- **Revision / Version**: UNKNOWN
- **Publication Date**: UNKNOWN
- **Official URL**: fiberlogy.com/app/uploads/2026/05/FIBERLOGY_NYLONPA12_TDS.pdf
  — **this session directly fetched this exact URL and confirmed it
  resolves to a genuine, live manufacturer PDF** (valid PDF file structure
  observed), but the content stream is compressed binary that this
  session's fetch tool cannot parse into readable text/tables. A companion
  HTML product page (fiberlogy.com/en/filaments/nylon-en/nylon-pa12-en/)
  was also directly fetched but its qualitative marketing text did not
  include the numeric properties table (likely rendered separately/via
  script). **The specific numeric figures below were therefore obtained via
  an AI-assisted web search that cited this TDS as its source, not by this
  session directly reading the rendered table** — the same honestly-
  disclosed provenance limitation as DS-MTL-001 (Prusament PETG).
- **Retrieved Date**: 2026-09-13
- **Local cache note**: not committed; URL verified live this session, PDF
  content not locally cached/parsed.
- **Used for Evidence IDs**: DS-MTL-003

## Key figures used (provenance as disclosed above — treat as ESTIMATE-tier, not directly-verified CONFIRMED)

- Notched Charpy impact strength @ 23°C: **≈12 kJ/m²** (ISO 179).
- Tensile strength @ yield: **≈45 MPa** (ISO 527).

## Why this reference matters here

Provides the nylon-class-material data point for this project's MISS-011
wall-impact estimate (§8.1 of `bench-imu-01-dimensional-spec.md`) — nylon
(PA12) is one of the two candidate print materials the Manufacturing
Engineer's own process spec proposes (alongside PETG), and its notably
higher notched-Charpy figure (~12 kJ/m²) vs. PETG's XY figures (~6-11.6
kJ/m² across brands) is used as the "most generous, best-case" input in the
estimate's material-property range — explicitly labeled as such, not
presented as the figure the design commits to.

## Known gaps (honestly flagged, not guessed)

- Numbers not independently read from the primary PDF by this session (see
  provenance note above) — a human should re-fetch and visually confirm the
  table before treating these as fully CONFIRMED.
- No separate X-Y/Z anisotropy split was found/reported for this specific
  material (unlike the PETG citations, which do report a split) — UNKNOWN
  whether nylon PA12's own anisotropy ratio for this property is smaller,
  similar, or larger than PETG's; not assumed either way.
- Same quasi-static-vs-high-strain-rate caveat as the PETG citations
  applies (standard ISO 179 test speed is far below the REQ-403 event's
  ≈69.74 m/s effective impact speed).
