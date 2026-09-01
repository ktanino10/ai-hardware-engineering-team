# Prusa Research — Prusament PETG Technical Data Sheet (TDS 2021-10, Rev UNKNOWN edition)

- **Manufacturer**: Prusa Research / Prusa Polymers (Prusament brand)
- **Part Number**: Prusament PETG filament (all standard colors, 1.75mm)
- **Datasheet Title**: Prusament PETG Technical Data Sheet
- **Revision / Version**: "2021_10" per the document's own filename
  (`PETG_Prusament_TDS_2021_10_EN.pdf`); UNKNOWN whether a newer edition has
  since been published.
- **Publication Date**: October 2021 (inferred from filename convention;
  not independently confirmed against an in-document date field).
- **Official URL**: prusament.com/wp-content/uploads/2022/10/PETG_Prusament_TDS_2021_10_EN.pdf
  — **this session directly fetched this exact URL and confirmed it
  resolves to a genuine, live manufacturer PDF** (valid PDF file structure
  observed). However, the PDF's internal content stream is compressed
  binary (FlateDecode) that this session's fetch tool cannot parse into
  readable text/tables. **The specific numeric figures below were therefore
  obtained via an AI-assisted web search that cited this exact PDF as its
  source, not by this session directly reading the rendered table.** This
  is an important, honestly-disclosed distinction: the *document's
  existence and URL* are directly verified; the *specific numbers* are a
  second-hand (search-engine-mediated) transcription.
- **Retrieved Date**: 2026-09-13
- **Local cache note**: not committed; URL verified live this session, PDF
  content not locally cached/parsed.
- **Used for Evidence IDs**: DS-MTL-001, DS-MTL-004

## Key figures used (provenance as disclosed above — treat as ESTIMATE-tier, not directly-verified CONFIRMED)

- Notched Charpy impact strength (printed-part test, not raw pellet):
  **≈6±1 kJ/m²** with the print's layer lines oriented horizontally/in-plane
  (XY) relative to the impact, vs. **≈3±1 kJ/m²** with layers oriented
  vertically (Z) relative to the impact — i.e. a ≈2x anisotropy between
  print orientations for the same material.
- Tensile strength at yield (printed-part test, ISO 527-type method):
  **≈46–50 MPa.**
- **(DS-MTL-004, added 2026-09-01, Rev 4 free-rotation-mechanism task)**
  Filament density / specific gravity: **1.27 g/cm³**. Same disclosed
  provenance caveat as the figures above — obtained via an AI-assisted web
  search citing this same TDS PDF, not by this session directly parsing the
  rendered table (this PDF's compressed content stream remains unparseable
  by this session's fetch tool, per the note above). Used in
  `requirements/requirements.md` REQ-310 and `bom/component-selection.md`'s
  Free-Rotation Support Mechanism section to estimate the Rev 3 enclosure's
  own never-previously-computed plastic mass (bounding-shell-volume method,
  ESTIMATE, not a precise figure).

## Why this reference matters here

Provides the "reasonably strong/typical PETG" end of this project's
material-property range used in the MISS-011 wall-impact estimate (§8.1 of
`bench-imu-01-dimensional-spec.md`). The disclosed XY-vs-Z anisotropy split
directly echoes — and gives a first real number to — this same document's
own already-disclosed §13.3 Z-print-orientation strength-anisotropy gap,
which until this citation was a qualitative concern without an attached
figure.

## Known gaps (honestly flagged, not guessed)

- Numbers not independently read from the primary PDF by this session (see
  provenance note above) — a human should re-fetch and visually confirm the
  table before treating these as fully CONFIRMED.
- Charpy notched-impact and tensile-yield figures reflect standard
  quasi-static test speeds (typically ~1-4 m/s for impact, much slower for
  tensile) — **not** the REQ-403 event's much higher ≈69.74 m/s effective
  impact speed. Most thermoplastics become more brittle (less
  energy-absorbing) at high strain rate, so extrapolating this quasi-static
  figure to the real event likely over-states, not under-states, real
  energy absorption — a non-conservative-direction caveat, disclosed in
  §8.1.
