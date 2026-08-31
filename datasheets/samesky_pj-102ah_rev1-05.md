# Same Sky PJ-102AH Datasheet — Rev 1.05

- **Manufacturer**: Same Sky, Inc. (formerly CUI Devices — brand
  transition; part is the same PJ-102AH originally released under the CUI
  Devices name, now hosted on Same Sky's own domain)
- **Part Number**: PJ-102AH
- **Datasheet Title**: "PJ-102AH DC Power Connectors" (as printed on the
  document's own header)
- **Revision / Version**: 1.05
- **Publication Date**: 2024-09-12 (printed on the document itself)
- **Official URL**: https://www.sameskydevices.com/product/resource/pj-102ah.pdf
  (manufacturer-hosted datasheet PDF, confirmed reachable and
  text-extractable this session via an `r.jina.ai` reader proxy — the raw
  PDF binary stream itself is not directly text-extractable by this
  session's `web_fetch` tool, consistent with this project's experience
  with other manufacturer PDFs this cycle)
- **Retrieved Date**: 2026-09-04
- **Local cache note**: not committed; content read live via the
  `r.jina.ai` text-extraction proxy this session, full specification table
  captured directly from the primary document (not a secondary/distributor
  mirror); not cached to any local disk.
- **Used for Evidence IDs**: DS-CONN-005

## Why this part

Selected as the new ~12V-class motor power input connector for Bench-IMU-01
Rev 3, per `hardware/power-architecture.md`'s approved Option A (ECO-008).
This is a supporting-component decision (not a major/architecture-defining
one), consistent with this project's own Rev 2 precedent for J1/the ESD IC
(`.github/skills/schematic-design/SKILL.md`, `bench-imu-01-design.md` §3.1)
— "a real, datasheet-grounded single part is sufficient for this
supporting role, no full ≥3-candidate comparison needed." A standard
2.1mm/2.0mm-class barrel jack is the conventional choice for a bench-power
DC input at this voltage/current class; PJ-102AH was chosen as a
well-documented, primary-datasheet-verified representative part with
adequate voltage/current headroom for this design's actual load (see
`bench-imu-01-design.md` §7.5.1 for the full reasoning and the
DS-CONN-005 citation for the specific numbers relied upon).

## Known gaps (honestly flagged, not guessed)

- The datasheet's own drawing shows 3 terminals (center pin + 2 additional
  terminals), consistent with a normally-closed switch-contact barrel jack
  design (common in this connector class, used for e.g. auto-disconnecting
  an internal battery when an external adapter is plugged in). The
  datasheet page fetched this session did not include a full internal
  schematic diagram explicitly labeling which of the 2 non-center
  terminals is the switch contact vs. the sleeve/ground return — this
  design uses the center pin (+) and one outer terminal as sleeve/GND, and
  deliberately leaves the switch-contact terminal (if present) unpopulated
  since no requirement calls for power-presence detection (see
  `bench-imu-01-design.md` §7.5.1). This is flagged as a residual detail
  to confirm against the datasheet's mechanical drawing (not reproduced
  here per this repository's copyright policy) at layout time, not a
  blocking unknown for this paper-design cycle (REQ-502).
- Mating-plug specifications (the datasheet also documents compatible plug
  part numbers/dimensions) were not exhaustively extracted this session —
  only the receptacle's own electrical/mechanical ratings were captured,
  since a specific plug MPN is a BOM/assembly-stage decision, not a
  schematic-level one.
