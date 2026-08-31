# SOYO SY28STH32-0674A (sold as Pololu item #1205) Datasheet — Rev UNKNOWN

- **Manufacturer**: SOYO (part-number prefix "SY" is this OEM stepper
  motor family's own convention); no independent SOYO manufacturer web
  portal was found hosting this document this session — the only located
  copy is distributor-hosted (see Official URL). This is analogous to this
  repo's existing `generic_ams1117-3.3_multi-source.md` precedent for a
  part whose canonical manufacturer portal could not be independently
  confirmed.
- **Part Number**: SY28STH32-0674A (Pololu catalog/resale number: item
  #1205)
- **Datasheet Title**: UNKNOWN — exact printed title on the PDF's own cover
  was not extracted this session (binary PDF, not text-rendered by this
  session's tooling); filename itself is `SY28STH32-0674A.pdf`.
- **Revision / Version**: UNKNOWN
- **Publication Date**: UNKNOWN
- **Official URL**: https://www.pololu.com/file/0J686/SY28STH32-0674A.pdf
  (distributor-hosted OEM document, linked directly from Pololu's own
  product page for item #1205)
- **Retrieved Date**: 2026-08-31
- **Local cache note**: not committed; not independently text-extracted this
  session (binary PDF) — the numeric specs cited here come from Pololu's own
  product-page transcription of the same document's key parameters, plus
  this session's web search, not a direct read of the PDF's raw text/tables.
- **Used for Evidence IDs**: DS-MTR-025, DS-MTR-026, DS-MTR-027, DS-MTR-028,
  DS-MTR-029

## Known gaps (honestly flagged, not guessed)

- Rotor inertia is not published on the accessible pages/product listing —
  recorded as `UNKNOWN`.
- No torque-vs-speed curve is published; this session's assessment of
  continuous torque available at the 3000 RPM / 10 kHz step-rate operating
  point is a **derived estimate** from winding L/R time-constant physics
  (see `datasheets/orientalmotor_basics-of-stepper-motors_web-article.md`
  and DS-MTR-030/031), not a manufacturer-stated figure — flagged as such
  everywhere it is used.
- This part is **not** the recommended candidate this cycle — see
  `bom/component-selection.md` "Motor (Reaction Wheel Drive)" section
  (marginal-to-infeasible continuous torque at the 3000 RPM target per the
  L/R time-constant analysis, zero native RPM-sensing path, no reaction-
  wheel/continuous-spin reference design found for this exact SKU).
