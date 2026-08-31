# Bosch Sensortec BMI270_SensorAPI — Official Open-Source Driver

- **Manufacturer**: Bosch Sensortec GmbH
- **Part Number**: BMI270 (U2)
- **Document Title**: N/A — this is not the datasheet PDF (already recorded
  separately as `datasheets/bosch-sensortec_bmi270_rev1.6.md`). This record
  is for Bosch's own official, redistributable open-source **register-map
  header and reference driver source code**, a distinct citable source from
  the datasheet PDF.
- **Revision / Version**: v2.86.1, dated 2023-05-03 (per `bmi270.c`'s own
  file header: `@version v2.86.1`, `@date 2023-05-03`)
- **Publication Date**: 2023-05-03 (per the file header above)
- **Official URL**: https://github.com/boschsensortec/BMI270_SensorAPI
  (specific files used: `bmi2_defs.h` — register-address constants;
  `bmi270.c` — the `bmi270_config_file[]` array and the
  soft-reset/config-load reference sequence; `bmi2.c` — the
  `write_config_file`/`upload_file` chunked-upload algorithm; `bmi270.h` —
  the `BMI270_CHIP_ID` expected value)
- **License**: BSD-3-Clause (full text reproduced in
  `firmware/bench-imu-01/src/bmi270_config_file.h`, per that license's own
  redistribution terms) — already this project's own SDK-ecosystem evidence
  for this part during Component Selection (see DS-IMU-017,
  `bom/component-selection.md`: "official Bosch C driver (BSD-3-Clause,
  GitHub, MCU-agnostic)")
- **Retrieved Date**: this session (Bench-IMU-01 firmware bring-up,
  Firmware Engineer)
- **Local cache note**: fetched locally this session to (a) independently
  count the configuration-file blob's exact byte length (8192, confirmed
  against `dev->config_size = sizeof(bmi270_config_file)` in the same
  upstream file) rather than trusting a remembered figure, and (b) extract
  the exact register addresses/upload algorithm below. The 8192-byte blob
  itself IS committed, verbatim, to
  `firmware/bench-imu-01/src/bmi270_config_file.h` — this is permitted and
  expected under this record's BSD-3-Clause license (redistribution in
  source form, with the copyright notice and license text retained, both of
  which that file reproduces in full) and is a different situation from a
  copyrighted datasheet PDF.
- **Used for Evidence IDs**: DS-IMU-078 through DS-IMU-088 (see
  `datasheets/evidence-log.md`) — BMI270 I2C address (0x68, corroborating
  the schematic's own SDO-tied-to-GND citation, DS-IMU-076), CHIP_ID
  expected value, the register addresses for CMD/PWR_CONF/PWR_CTRL/
  INIT_CTRL/INIT_ADDR_0/INIT_ADDR_1/INIT_DATA/INTERNAL_STATUS/ACC_CONF/
  GYR_CONF/ACC_X_LSB/GYR_X_LSB, the soft-reset command value and mandatory
  initialization sequence (including the configuration-file upload
  protocol), the ACC_CONF/GYR_CONF encoding for a >=100 Hz ODR + normal
  power mode, and the PWR_CTRL accelerometer/gyroscope-enable bit
  positions.
