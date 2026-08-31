# STMicroelectronics AN4235 — I2C Timing Configuration Tool for STM32 (App Note)

- **Manufacturer**: STMicroelectronics
- **Part Number / Family**: applies generically to STM32 parts using the
  "I2C peripheral v2" IP block (shared across F0/G0/L0/L4 families,
  including this project's STM32G031K8T6, U1)
- **Datasheet Title**: "I2C timing configuration tool for STM32 family
  devices" (application note AN4235)
- **Revision / Version**: not independently re-confirmed this session
  (cited via a cross-checked web search summary, not a direct PDF fetch —
  see Cross-check note below)
- **Publication Date**: UNKNOWN this session
- **Official URL**: https://www.st.com/resource/en/application_note/an4235-i2c-timing-configuration-tool-for-stm32-family-devices-stmicroelectronics.pdf
- **Retrieved Date**: this session, via a web search summarizing this
  document's Table 11 ("I2C timings for 16 MHz PCLK"), not a direct PDF
  fetch
- **Local cache note**: not committed (and not directly downloaded this
  session either — see Cross-check note)
- **Used for Evidence IDs**: DS-MCU-063 (see `datasheets/evidence-log.md`)
  — the STM32 I2C_TIMINGR register value for Fast-mode (400 kHz) at a
  16 MHz peripheral clock (`0x00310309`), used by
  `firmware/bench-imu-01/src/stm32g031_regs.h`.
- **Cross-check note (lower confidence than this project's usual
  direct-fetch standard, flagged honestly rather than overstated)**: this
  session did not directly fetch/parse the AN4235 PDF itself (a PDF binary,
  not a page `web_fetch` renders cleanly). The `0x00310309` value was
  obtained via a web search whose summary explicitly cited "AN4235 Table
  11" with the same PRESC/SCLDEL/SDADEL/SCLH/SCLL field breakdown
  (0/3/1/3/9) that composes to that exact 32-bit value, and separately
  corroborated by an ST Community forum post on computing this same
  register. Two independently-phrased search results agreed on the same
  literal value. This is consistent with this project's own established
  practice of citing a search-derived fact with an explicit confidence
  note rather than silently treating it as PDF-page-verified (see, for
  precedent, `datasheets/bosch-sensortec_bmi270_rev1.6.md`'s own "moderate
  confidence... not independently re-confirmed against the raw PDF" style
  disclosures). If this figure is ever safety- or fabrication-relevant
  (it is not, for a paper/source-code bring-up exercise), it should be
  re-verified against the primary PDF or an ST CubeMX-generated value
  before being relied upon further.
