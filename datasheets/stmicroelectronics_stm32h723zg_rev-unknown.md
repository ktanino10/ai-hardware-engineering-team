# STMicroelectronics STM32H723ZG Datasheet

- **Manufacturer**: STMicroelectronics
- **Part Number**: STM32H723ZG (LQFP-144, 1MB flash variant)
- **Datasheet Title**: STM32H723xE/G, STM32H725xE/G, STM32H730xB/Value line,
  STM32H733xG — Arm Cortex-M7 32-bit MCU
- **Revision / Version**: UNKNOWN (not independently re-confirmed this
  session — the live web search that sourced the facts below cited a
  November 2023-dated datasheet revision as the most recent it found, but
  this session did not itself open/re-confirm the PDF's own cover-page
  revision letter)
- **Publication Date**: UNKNOWN (see above — November 2023 reported by a
  secondary source, not independently confirmed against the primary PDF
  this session)
- **Official URL**: https://www.st.com/en/microcontrollers-microprocessors/stm32h723zg.html
  (a direct fetch of this URL was attempted this session and timed out;
  the facts below are sourced from a live web search returning excerpts
  from ST's own datasheet as mirrored/quoted by third-party distributor
  and datasheet-aggregator pages, not a direct read of the primary ST PDF)
- **Retrieved Date**: 2026-09-04
- **Local cache note**: Not cached locally; content derived from a live web
  search this session (ST's own product page fetch timed out), not a
  locally-stored PDF copy. This is a lower confidence level than this
  file's sibling Rev 5 records that did successfully fetch a primary
  product page directly — flagged honestly, not glossed over. Every
  numeric claim below should be treated as "credible per multiple
  aggregator/distributor sources quoting the ST datasheet," not
  "independently re-verified against the primary PDF."
- **Used for Evidence IDs**: DS-MCU-092 through DS-MCU-098 (Rev 5 MCU
  Component Selection, candidate — not recommended, "likely overkill"
  per `bom/component-selection.md`'s own Rev 5 MCU subsection)

## Key facts (this session, via live web search of distributor/aggregator
## sources quoting ST's own STM32H723ZG datasheet)

- **Core/clock**: Arm Cortex-M7 with double-precision FPU, up to 550MHz;
  32KB/32KB L1 instruction/data cache; 0-wait-state execution from
  embedded Flash/TCM.
- **Flash/RAM**: Up to 1MB Flash (ECC-enabled); 564KB total RAM (128KB TCM
  RAM + 432KB system RAM + 4KB backup SRAM, all ECC-protected).
- **Package**: LQFP-144, 20mm × 20mm.
- **Communication peripherals**: Up to 5 I2C (Fast-mode+, SMBus/PMBus-
  compatible); up to 6 SPI (plus up to 5 more via USART in synchronous
  mode, 4 with duplex I2S); 6 USART/UART/LPUART; 3× FDCAN; 2× SAI; USB OTG
  FS; Ethernet; SDMMC; Octo-SPI.
- **Timers**: 24 timers total — 17× 16-bit timers (5 available in Stop
  mode) + 4× 32-bit timers + 2 watchdogs + 1 SysTick; all advanced timers
  support PWM/input-capture/output-compare/encoder modes. **Correction
  note**: `bom/component-selection.md`'s Rev 5 MCU subsection originally
  described this as "4×32-bit, 12×16-bit, 2 dedicated motor-control"
  (summing to 18, not the correct total of 24) — that breakdown did not
  match this fact once independently re-verified via this search and has
  been corrected in the comparison table to match the figures recorded
  here.
- **Operating voltage**: 1.62V–3.6V.
- **Lifecycle status**: Reported as "Production"/actively supported as of
  the most recent datasheet revision found (November 2023) by the sources
  this search returned — no EOL/NRND notice found for this specific part
  this session.

## Known gaps (honestly flagged, not guessed)

- The primary ST PDF itself was not directly opened this session (the
  direct product-page fetch timed out) — all facts above are sourced from
  a live web search returning distributor/aggregator excerpts that
  themselves quote the ST datasheet, not from this session's own direct
  read of the primary document. This is a real, disclosed confidence gap
  relative to this file's sibling Rev 5 datasheet records.
- Exact ADC/DAC/analog peripheral counts, price, and real 2026 distributor
  stock were not the focus of this fact-finding pass (this candidate is
  not the Rev 5 recommendation) and are recorded as `UNKNOWN` in the
  consuming Component Selection section rather than guessed.
