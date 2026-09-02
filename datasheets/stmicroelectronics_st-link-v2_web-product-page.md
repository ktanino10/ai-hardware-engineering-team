# STMicroelectronics ST-LINK/V2 — Official Product Page

- **Manufacturer**: STMicroelectronics
- **Part Number**: ST-LINK/V2 (in-circuit debugger/programmer tool —
  bring-up/production **tooling**, not a component placed on the
  Bench-IMU-01 BOM)
- **Datasheet Title**: N/A — this is STMicroelectronics' own official
  product page for the ST-LINK/V2 tool, not a datasheet PDF
- **Revision / Version**: N/A (web page; hardware itself is a fixed,
  long-production tool with no revision letter tracked here)
- **Publication Date**: UNKNOWN (undated web page)
- **Official URL**: https://www.st.com/en/development-tools/st-link-v2.html
- **Retrieved Date**: 2026-09-02
- **Local cache note**: Not cached locally. A direct `web_fetch` of this
  exact URL timed out this session (`TimeoutError`) — the citation below is
  based on a web-search synthesis that itself quotes/cites this same
  official ST URL alongside corroborating authorized-distributor listings
  (Mouser, DigiKey, RS Online) for the price point. **MODERATE-HIGH
  confidence** (ST's own product-selector/compatibility claim for "all
  STM32 families" is extremely well-established/uncontroversial industry
  knowledge, independently corroborated by the STLINK-V3MINI UM2502 record
  below and by the open-source `stlink-org/stlink` toolset's own explicit
  STM32G0 support statement, DS-TOOL-005) — not a direct primary-page fetch
  this session specifically.
- **Used for Evidence IDs**: DS-TOOL-001, DS-TOOL-002

## Why this citation

ST-LINK/V2 is STMicroelectronics' own long-running, widely-deployed
in-circuit debugger/programmer for the entire STM32 (and STM8) portfolio —
this is the tool referenced generically in
`validation/bring-up-procedure.md` §0a's original text ("e.g. an ST-LINK or
equivalent") before this pass replaced that placeholder with a concrete,
sourced recommendation. Used here as evidence that a genuine,
ST-manufactured SWD programmer is a real, currently-purchasable option for
Bench-IMU-01's STM32G031K8T6 (U1) via its J3 header (SWD: VDD/SWCLK/GND/
SWDIO, `hardware/schematic/bench-imu-01-design.md` §4.4).
