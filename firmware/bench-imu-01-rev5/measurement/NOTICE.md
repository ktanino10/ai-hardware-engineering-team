# Third-party provenance for the public source subset

This notice is a derived public edition. No new license is assigned to
first-party project code.

- `vendor/bosch/{bmi2.c,bmi2.h,bmi2_defs.h,bmi270.c,bmi270.h,LICENSE}`:
  copyright 2023 Bosch Sensortec GmbH; **BSD-3-Clause**. Byte-identical files
  from official BMI270_SensorAPI v2.86.1, commit
  `d270cdee303b2ed9ea4c43fb7064da8ded8a48b4`. Copyright, disclaimer and
  non-endorsement clauses remain intact, including file headers.
  The configuration array in `bmi270.c` is unchanged, not approximated or shortened.
- [vendor/bosch/provenance.json](vendor/bosch/provenance.json) retains actual
  official source URLs, exact file hashes and configuration-blob identity.
  The full [Bosch license](vendor/bosch/LICENSE) is included.
- ESP-IDF v5.5.2, commit `30aaf64524299d3bde422ca9a2848090d1bc5d0f`,
  is an **external dependency**, not an SDK snapshot in this export.
  Its top-level Apache-2.0 license remains verbatim in
  [licenses/ESP-IDF-LICENSE](licenses/ESP-IDF-LICENSE).
  Independently obtained SDK/toolchain components may have additional
  notices; this file does not grant rights beyond their actual licenses.

No ELF/BIN, SDK/tool installation, source-lock host inventory or raw build
log is distributed. This is not a binary-distribution release. Any future
binary distribution requires its complete applicable SDK/runtime/component
notices as well as Bosch's binary redistribution notice.
No manufacturer datasheet PDF or raw user upload is included.
