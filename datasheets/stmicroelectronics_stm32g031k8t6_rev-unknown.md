# STMicroelectronics STM32G031K8T6 Datasheet — Rev UNKNOWN

- **Manufacturer**: STMicroelectronics
- **Part Number**: STM32G031K8T6
- **Datasheet Title**: STM32G031K8 / STM32G031x4/x6/x8 datasheet (exact printed title not independently re-extracted this session)
- **Revision / Version**: UNKNOWN (not independently confirmed this session — ST datasheets carry a DocID/Rev number on the cover that was not captured in the sources consulted)
- **Publication Date**: UNKNOWN (not independently confirmed this session)
- **Official URL**: https://www.st.com/resource/en/datasheet/stm32g031k8.pdf (manufacturer-hosted datasheet PDF); cross-referenced against https://www.st.com/en/microcontrollers-microprocessors/stm32g031k8.html (manufacturer product page)
- **Retrieved Date**: 2026-08-30
- **Local cache note**: not committed; content verified via live web search this session, cross-checked across ≥2 independent sources per critical fact (ST's own product/datasheet pages + 2 independent mirror sites for the VDD AMR/ROC figures, Table 6 and Table 18 references)
- **Used for Evidence IDs**: DS-MCU-012, DS-MCU-013, DS-MCU-014, DS-MCU-015, DS-MCU-016, DS-MCU-017, DS-MCU-018, DS-MCU-019, DS-MCU-020, DS-MCU-021, DS-MCU-044, DS-MCU-045, DS-MCU-046, DS-MCU-047, DS-MCU-048, DS-MCU-049 (the last six added during Bench-IMU-01 schematic design, 2026-08-31 — BOOT0/nBOOT_SEL behavior, LQFP32 pinout/VDD-VSS-VDDA-VBAT count, NRST recommended circuit, LQFP-32 package height, and the BOOT0/PB8 pin-bonding UNKNOWN), plus DS-MCU-050, DS-MCU-051, DS-MCU-052, DS-MCU-053 (added by the Hardware Lead during Independent Review conflict mediation, 2026-08-31 — corrects DS-MCU-045/046's BOOT0-pin and PB8-existence claims, and corrects the design document's I2C1-vs-I2C2 pin mapping per `validation/open-issues.md` ISS-006/ISS-011), plus DS-MCU-054 (added by the Hardware Lead during Design Complete Gate traceability closeout, 2026-09-03 — confirms −40 to +85 °C operating temperature range against REQ-201), plus DS-MCU-062 (added by the Firmware Engineer during Bench-IMU-01 firmware bring-up, 2026-08-31 — confirms the PA2/PA3=AF1/PB10-PB11=AF6 alternate-function values the firmware's GPIO driver relies on), plus DS-MCU-064, DS-MCU-065, DS-MCU-066 (added by the Circuit Engineer during Bench-IMU-01 Rev 3 schematic design, 2026-09-04 — see the Update note below), plus DS-MCU-067 (added by the Hardware Reviewer during Independent Review Cycle 4, 2026-09-08), plus DS-MCU-068 (added by the Hardware Lead, 2026-09-09 — corrects DS-MCU-052's implicit PB10/PB11 package-bonding assumption, see the Correction note below)

## Correction note (Hardware Lead, 2026-08-31)

Two facts in this record's earlier-cited evidence (DS-MCU-045, DS-MCU-046) were
found to be incomplete/incorrect during Independent Review and have been
superseded, not silently overwritten — see DS-MCU-050/051/052/053 in
`datasheets/evidence-log.md` for the corrected facts, and
`validation/open-issues.md` ISS-006/ISS-011 for the full finding record. This
is a routine, expected part of independent review catching upstream errors —
recorded transparently per this repository's evidence-integrity conventions.

## Update (Circuit Engineer, 2026-09-04, Bench-IMU-01 Rev 3)

This session directly retrieved and read ST's primary datasheet **DS12992
Rev 4** (https://www.st.com/resource/en/datasheet/stm32g031k8.pdf) via an
`r.jina.ai` text-extraction reader proxy — the same primary document
DS-MCU-050 through DS-MCU-053 already cite, now independently re-consulted
for a different purpose (Rev 3's new motor-interface pin allocation, not a
correction this time). Specifically extracted: **Table 12** ("Pin
definition") for the full package pinout, and **Tables 13 through 17**
(alternate-function mapping tables, one per GPIO port) for exact AF
numbers. New findings, all used to allocate PA8 (PWM), PA6 (FG input), PB1
(DIR), and PB6/PB7 (optional I2C1 tuning bus) for the new motor-driver
interface block — see `hardware/schematic/bench-imu-01-design.md` §7.5.4
for the full pin-allocation rationale, and DS-MCU-064/065/066 in
`datasheets/evidence-log.md` for the specific citations. This Update does
not correct or supersede any prior fact in this record — it is a pure
addition of new facts about previously-uninvestigated pins/tables.

## Correction note (Hardware Lead, 2026-09-09) — CRITICAL

**PB10/PB11 do not physically exist on this part's actual LQFP-32
package.** This is a correction to an implicit assumption carried by
DS-MCU-052 (which correctly identified the *peripheral* mapping — I2C2,
not I2C1 — but never separately checked whether the specific GPIO pads
PB10/PB11 are bonded out on the specific ordered package) and by the
firmware-facing DS-MCU-062 (which correctly recorded the AF6 alternate-
function *value* without checking pin-level package bonding either).
Independently re-derived this session directly from the same primary
datasheet (DS12992 Rev 4) Circuit Engineer's 2026-09-04 Update above
already had open in this exact session — Table 2, Figure 7 vs. Figure 9,
and Table 12's own per-package pin-number columns all concur: PB10/PB11
exist only on the LQFP48/UFQFPN48 (48-pin) package, not on LQFP32/UFQFPN32
(the STM32G031K8T6's actual 32-pin package this design uses). See
**DS-MCU-068** in `datasheets/evidence-log.md` for the full citation and
`validation/open-issues.md` **ISS-026** (CRITICAL) for the finding record
and recommended fix (re-route the IMU I2C bus to PA11/PA12, both
confirmed present on this package and free in this design). This is a
real, previously-undetected defect dating to the original Rev 2 baseline
(Electronics PR #6) — recorded transparently per this repository's
evidence-integrity conventions, same as the Hardware Lead's 2026-08-31
correction note above.
