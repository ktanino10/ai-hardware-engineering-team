# TDK InvenSense ICM-20948 Datasheet — Rev 1.3

- **Manufacturer**: TDK InvenSense (TDK Corporation)
- **Part Number**: ICM-20948
- **Datasheet Title**: ICM-20948 — World's Lowest Power 9-Axis MEMS MotionTracking™ Device (title phrase directly confirmed this session via an alldatasheet.com HTML mirror of the datasheet's own page-1 text: "World's Lowest Power 9-Axis MEMS MotionTracking Device" — high confidence, a direct quote of the document itself, not a third-party paraphrase)
- **Revision / Version**: 1.3 — Document Number DS-000189 directly confirmed this session via a fetch of the alldatasheet.com HTML mirror of the datasheet's own page-1 text ("Document Number: DS-000189"); the specific "Rev 1.3" label itself came from a follow-up web-search synthesis rather than a direct quote — moderate-to-high confidence
- **Publication Date**: 2017-06-02 (per search-derived source citing the document's own release-date marking; not independently re-confirmed against the raw PDF cover page this session — moderate confidence)
- **Official URL**: https://www.invensense.tdk.com/en-us/products/9-axis/icm-20948 (manufacturer product page, directly fetched this session; manufacturer's canonical PDF URL not directly captured this session — detailed extraction relied on the alldatasheet.com mirror cited in the evidence log)
- **Retrieved Date**: 2026-08-30
- **Local cache note**: not committed; content verified via live web search this session, cross-checked across ≥2 independent sources per critical fact (the VDDIO disqualification fact specifically was cross-checked across 3 independent sources — see DS-IMU-057 in `datasheets/evidence-log.md`)
- **Used for Evidence IDs**: DS-IMU-052 through DS-IMU-069, DS-IMU-073

## Status note (per this repo's evidence rules)

This part is disqualified for use in the Bench-IMU-01 design (formally
Obsolete/NRND at major distributors, and its VDDIO ceiling of 1.71–1.95 V is
incompatible with the project's single 3.3 V logic rail without added
level-shifting hardware — see `bom/component-selection.md` "IMU" section).
Retained here only as a documented comparison point, per
`.github/skills/component-selection/SKILL.md`'s requirement to show the
comparison work, not because this part is in active use.
