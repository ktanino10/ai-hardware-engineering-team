# FTDI FT232R — "FT232R USB UART IC" Datasheet

- **Manufacturer**: Future Technology Devices International Ltd. (FTDI)
- **Part Number**: FT232R (FT232RL = the LQFP-32 package variant commonly
  used on hobbyist USB-to-TTL-serial breakout boards)
- **Datasheet Title**: "FT232R USB UART IC" (DS_FT232R)
- **Revision / Version**: UNKNOWN (a web search surfaced a candidate "Rev.
  2.16, May 2020" reference, but this was not independently re-confirmed
  against the primary PDF this session — recorded as UNKNOWN per this
  project's own no-guessing rule rather than stated as fact)
- **Publication Date**: UNKNOWN (see above)
- **Official URL**: https://ftdichip.com/document/usb-ic-data-sheets/
  (FTDI's own index page for all current USB IC datasheets, including
  FT232R; a candidate direct PDF path was reported as
  `ftdichip.com/wp-content/uploads/.../DS_FT232R.pdf` but the exact
  date-stamped subpath was not independently confirmed this session)
- **Retrieved Date**: 2026-09-02
- **Local cache note**: Not cached locally; not directly fetched this
  session. Citation is based on a web-search synthesis describing FTDI's
  official macOS VCP (Virtual COM Port) driver support and the FT232R's
  configurable logic-level I/O (dependent on the specific breakout board's
  own VCCIO wiring — some boards ship as fixed 3.3V or fixed 5V SKUs,
  others are jumper-selectable), plus community/vendor discussion of a
  known counterfeit-chip risk on ultra-low-cost FTDI-branded listings.
  **MODERATE confidence** overall (not a direct primary-PDF fetch this
  session); this claim governs a bench debug-adapter choice, not a
  Bench-IMU-01 BOM part.
- **Used for Evidence IDs**: DS-TOOL-012

## Why this citation

FT232R-based USB-to-UART modules are presented in
`validation/bring-up-procedure.md` §0a as the higher-cost, historically
most driver-mature alternative to a CP2102-based module (DS-TOOL-011) for
Bench-IMU-01's J2 header — both are viable options; FTDI's own official VCP
driver has a long macOS support track record, offset by a higher unit price
and known counterfeit-chip risk on some third-party listings.
