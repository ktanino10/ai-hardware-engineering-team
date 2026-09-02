# STMicroelectronics STM32CubeProgrammer — Official Product/Documentation Pages

- **Manufacturer**: STMicroelectronics
- **Part Number**: N/A — this is official ST **software tooling**
  (STM32CubeProgrammer, GUI + CLI `STM32_Programmer_CLI`), not a
  Bench-IMU-01 BOM component
- **Datasheet Title**: N/A — official ST product page + the official
  STM32CubeProgrammer online documentation site
- **Revision / Version**: Online documentation observed at version 2.23.0
  (`dev.st.com/stm32cube-docs/prog/2.23.0/...`); exact currently-shipping
  installer version not independently re-confirmed this session
- **Publication Date**: UNKNOWN (continuously-updated ST tool/doc site)
- **Official URL**: https://www.st.com/en/development-tools/stm32cubeprog.html
  (download requires a free myST account registration); documentation:
  https://dev.st.com/stm32cube-docs/prog/2.23.0/en/index.html
- **Retrieved Date**: 2026-09-02
- **Local cache note**: Not cached locally. Direct `web_fetch` of
  `st.com/en/development-tools/stm32cubeprog.html` timed out this session
  (`TimeoutError`); this citation is based on a web-search synthesis
  quoting the official ST download/doc pages plus ST Community forum
  threads describing real, first-hand macOS install experiences (including
  a documented Java/JRE-related install friction point on macOS Ventura/
  Monterey). **MODERATE confidence** on the exact current macOS install
  friction points specifically (community-forum-sourced, not ST's own
  release notes) — **HIGH confidence** on STM32CubeProgrammer being ST's
  official, actively-maintained flashing tool covering the full STM32
  portfolio (an extremely well-established, uncontroversial fact — it is
  the same tool STM32CubeIDE itself calls for flash operations).
- **Used for Evidence IDs**: DS-TOOL-008

## Why this citation

STM32CubeProgrammer is STMicroelectronics' own official, currently-shipping
flash/program tool, offered as an alternative to the open-source
`st-flash` (DS-TOOL-005/006/007) for anyone who prefers ST's own supported
channel, a GUI, or more complete option-byte/advanced-feature coverage.
Cited in `validation/bring-up-procedure.md` §0a as the "official ST tool"
alternative alongside `st-flash` and OpenOCD, with its macOS-specific
install trade-offs (myST account requirement, occasional Java-related
friction reported by other users) disclosed rather than omitted.
