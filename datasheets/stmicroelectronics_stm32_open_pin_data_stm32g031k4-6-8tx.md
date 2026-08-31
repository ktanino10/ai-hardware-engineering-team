# STMicroelectronics STM32_open_pin_data (STM32G031K(4-6-8)Tx) — Machine-Readable Pin Database

- **Manufacturer**: STMicroelectronics
- **Part Number**: STM32G031K4Tx / STM32G031K6Tx / STM32G031K8Tx (one shared XML file covers all 3 flash-size variants of this LQFP-32 package — pin/peripheral layout is identical across them)
- **Datasheet Title**: N/A — not a PDF datasheet. This is ST's own official, machine-readable CubeMX/MXDB pin-database source file (`mcu/STM32G031K(4-6-8)Tx.xml`), published in ST's own open-source `STM32_open_pin_data` GitHub repository — the literal source data STM32CubeMX itself is generated from.
- **Revision / Version**: `DBVersion="V3.0"` (per the XML file's own `<Mcu>` root attribute); repository commit SHA `a72a549fdbebe004a81dd7d601992e6562591dd3` (as fetched this session)
- **Publication Date**: 2024 (per the file's own copyright header: "Copyright (c) 2024 STMicroelectronics")
- **Official URL**: https://github.com/STMicroelectronics/STM32_open_pin_data/blob/main/mcu/STM32G031K(4-6-8)Tx.xml
- **Retrieved Date**: 2026-08-31
- **Local cache note**: not committed; content fetched live via the GitHub API this session, full raw XML content reviewed in full (not excerpted/summarized before extraction)
- **Used for Evidence IDs**: DS-MCU-064, DS-MCU-065, DS-MCU-066, DS-MCU-067

## Why this source, and its evidentiary standing

This is ST's own officially-published, machine-readable pin/peripheral database —
not a third-party aggregator, distributor summary, or community post. It
originates directly from the manufacturer (STMicroelectronics is the repository
owner/publisher) and is materially *less* error-prone to extract structured
facts from than a PDF table, since it is already structured XML, not prose/table
layout requiring visual parsing. It is treated as **primary-source-equivalent**
for this repository's evidence model (`docs/architecture.md` §6.1) — on the same
footing as the manufacturer's own PDF datasheet.

**Disclosed limitation**: two independent attempts to fetch the actual PDF
datasheet (`https://www.st.com/resource/en/datasheet/stm32g031k8.pdf`, the same
URL already cited by `datasheets/stmicroelectronics_stm32g031k8t6_rev-unknown.md`)
directly this session both failed with a network timeout. This GitHub-hosted
source was used instead — disclosed here rather than silently substituted, per
this repository's Source-of-Truth honesty convention.

## What this source resolved

This source directly resolves a discrepancy discovered independently this
session (while verifying real KiCad symbol/footprint availability for a new
KiCad project) between `hardware/schematic/bench-imu-01-design.md` (Rev 2,
already Design Complete, PR #6)'s stated MCU pin table and the real
STM32G031K8T6 LQFP-32 package — specifically: no PB10/PB11 pin exists on this
package at all (the IMU I2C bus as documented cannot be physically wired), no
separate VDDA/VBAT pins exist, and NRST shares a pin with GPIO PF2. See
`validation/open-issues.md` ISS-014 and `validation/change-log.md` ECO-006 for
the full finding and fix record.
