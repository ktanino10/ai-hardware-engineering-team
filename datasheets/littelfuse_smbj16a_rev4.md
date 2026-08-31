# Littelfuse SMBJ Series (SMBJ16A) TVS Diode Datasheet — Rev 4 (JC.07/04/25)

- **Manufacturer**: Littelfuse, Inc.
- **Part Number**: SMBJ16A (unidirectional variant, from the SMBJ series
  family datasheet, which covers SMBJ5.0A through SMBJ170A/CA in one
  document)
- **Datasheet Title**: "SMBJ Series — Surface Mount Silicon TVS Diode
  600W Peak / SMB" (as printed on the document's own header)
- **Revision / Version**: document control code "JC.07/04/25 v4" printed
  on the document itself — recorded verbatim as the best-available
  identifier; not a conventional "Rev N" number
- **Publication Date**: not independently distinguished this session from
  the revision control code above (Littelfuse's own doc-control convention
  bundles date and revision together); treated as UNKNOWN as a separate
  field
- **Official URL**: https://www.littelfuse.com/assetdocs/tvs-diodes-smbj-series-datasheet?assetguid=ba555e99-a12d-4f72-a0b6-86b06c67171e
  (manufacturer-hosted datasheet PDF, confirmed reachable and
  text-extractable this session via an `r.jina.ai` reader proxy). **Note
  for future sessions**: an initially-guessed simpler URL pattern
  (`/asset/uploaded-assets/.../smbj.pdf`-style) 404'd; the real working
  path was only found via a `web_search` first — Littelfuse's actual URL
  pattern uses an `assetdocs/<slug>?assetguid=<guid>` structure, not a
  simple static path.
- **Retrieved Date**: 2026-09-04
- **Local cache note**: not committed; content read live via the
  `r.jina.ai` text-extraction proxy this session, full electrical
  characteristics table captured directly from the primary document; not
  cached to any local disk.
- **Used for Evidence IDs**: DS-PROT-004

## Why this part / why not SMBJ18A

Selected as the transient-voltage-suppression (TVS) diode for the new
~12V-class motor power input on Bench-IMU-01 Rev 3 (see
`bench-imu-01-design.md` §7.5.2). Two same-family part numbers were
directly compared using this same datasheet (both are in the same
document, same package, same price class):

| Part | Standoff V_R | Max clamp V_C @ I_PP | Margin under DRV10983's 30V AMR |
|---|---|---|---|
| SMBJ16A (chosen) | 16.0V min | **26.0V max** | 4.0V / 13% |
| SMBJ18A (rejected) | 18.0V min | **29.2V max** | 0.8V / 3% |

SMBJ18A's clamping voltage leaves only 0.8V of margin under the
DRV10983's 30V VCC Absolute Maximum Rating (DS-MTR-053) — too tight to be
a confident design choice, since the TVS's own clamp voltage is itself
only a typical/max test-condition figure, not an absolute guarantee under
every real-world transient shape. SMBJ16A's 26.0V clamp leaves a
meaningfully larger 4.0V/13% margin while its 16.0V standoff voltage still
sits safely above this design's ~12V nominal / ~14V realistic-worst-case
motor rail (§7.5.1), so it does not clip normal operation either.

## Known gaps (honestly flagged, not guessed)

- This is a **unidirectional** device (conducts/clamps in one direction
  only, blocks like a normal diode in the other) — appropriate here since
  it sits downstream of the series reverse-polarity-blocking diode
  (STPS3L60, DS-PROT-005) in this design's topology, not exposed to
  reverse polarity itself. A bidirectional variant (SMBJ16CA) exists in
  the same family but was not needed given the topology chosen (§7.5.2).
- IEC 61000-4-2 ESD rating (±30kV air/±30kV contact) was noted but is not
  directly relied upon for any REQ in this design cycle (no formal EMC
  pre-compliance target this cycle, REQ-401) — recorded for completeness,
  not as a load-bearing citation.
