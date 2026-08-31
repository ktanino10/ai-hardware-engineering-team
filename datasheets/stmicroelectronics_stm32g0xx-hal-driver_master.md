# STMicroelectronics stm32g0xx-hal-driver — Official HAL Driver Source (GPIO Extended header)

- **Manufacturer**: STMicroelectronics
- **Part Number / Family**: STM32G0 series (device-agnostic HAL driver
  source; this project uses it only for the `GPIO_AF6_I2C2` alternate-
  function macro definition, applicable to the STM32G031K8T6, U1)
- **Document Title**: N/A — this is not a datasheet PDF, it is
  STMicroelectronics' own official, redistributable open-source **HAL
  (Hardware Abstraction Layer) driver source code** for the STM32G0 series
  (`stm32g0xx_hal_gpio_ex.h`, the GPIO HAL Extended module header), not a
  scanned/typeset manufacturer document.
- **Revision / Version**: `master` branch, commit `289ef6c8ff0922878e99d253f29be76851f8f28e`
  (as fetched this session); the specific file used
  (`Inc/stm32g0xx_hal_gpio_ex.h`) was itself last modified at commit
  `3e7e57636112b59a7c88babb18de3070262a51ae` (2022-07-01)
- **Publication Date**: file's own header states "Copyright (c) 2018 STMicroelectronics"
- **Official URL**: https://github.com/STMicroelectronics/stm32g0xx-hal-driver
  (specific file used: `Inc/stm32g0xx_hal_gpio_ex.h`)
- **License**: per the file's own header, "licensed under terms that can be
  found in the LICENSE file in the root directory of this software
  component" (an Apache-2.0-style permissive license typical of ST's HAL
  driver packages) — this is redistributable **source code**, a different
  regime from this directory's "never commit a datasheet PDF" policy (see
  `datasheets/README.md`); no datasheet PDF content is reproduced anywhere
  in this repository as a result of using this source, and no code from
  this file is vendored into this repository — only the single numeric
  macro value it defines is cited.
- **Retrieved Date**: this session (Firmware Engineer, Bench-IMU-01 ISS-014
  firmware follow-up fix)
- **Local cache note**: fetched and grepped via the GitHub API this session,
  not committed to this repository
- **Used for Evidence IDs**: DS-MCU-069 (`datasheets/evidence-log.md`)

## Why this source, and its evidentiary standing

This is ST's own officially-published HAL driver header — the actual source
code STM32CubeMX/STM32CubeIDE link against when a project selects
`GPIO_AF6_I2C2` for a pin's alternate function. It originates directly from
the manufacturer (STMicroelectronics is the repository owner/publisher) and
is the authoritative numeric definition behind the symbolic name used in
`datasheets/stmicroelectronics_stm32cubeg0_master.md`'s example. Treated as
**primary-source-equivalent** for this repository's evidence model
(`docs/architecture.md` §6.1).

## What this source resolved

Confirms, repeated identically across all eight per-package `#if defined(...)`
variants in the file (this part's LQFP-32 package falls under one of them):

```c
#define GPIO_AF6_I2C2          ((uint8_t)0x06)  /*!< I2C2 Alternate Function mapping */
```

i.e. `GPIO_AF6_I2C2` is numerically `0x06` — directly confirming the AF
register value this firmware's `gpio.c` writes (`set_af(GPIOA, 11u, 6u)` /
`set_af(GPIOA, 12u, 6u)`) is correct for I2C2 on PA11/PA12, independently of
and corroborating `datasheets/stmicroelectronics_stm32cubeg0_master.md`'s
symbolic-name example.
