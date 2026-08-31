# STMicroelectronics STM32CubeG0 — Official Firmware Package (CubeMX-generated examples)

- **Manufacturer**: STMicroelectronics
- **Part Number / Family**: STM32G0 series (this project uses the
  NUCLEO-G031K8 example, which targets the STM32G031K8T6 — the identical
  part number used by U1 on Bench-IMU-01)
- **Document Title**: N/A — this is not a datasheet PDF, it is
  STMicroelectronics' own official, redistributable open-source **STM32Cube
  firmware package for the STM32G0 series** (`STM32CubeG0`), specifically a
  CubeMX-generated project example's MSP (MCU Support Package)
  initialization source file, not a scanned/typeset manufacturer document.
- **Revision / Version**: `master` branch, commit `446ebe396489ca75679caa80887d7257efe92e3d`
  (as fetched this session); the specific file used
  (`Projects/NUCLEO-G031K8/Examples_MIX/I2C/I2C_OneBoard_ComSlave7_10bits_IT/Src/stm32g0xx_hal_msp.c`)
  was itself last modified at commit `a019f83e7693348cf50f1466756ea985d3a96163`
  (2023-12-22)
- **Publication Date**: file's own header states "Copyright (c) 2019-2020 STMicroelectronics"
- **Official URL**: https://github.com/STMicroelectronics/STM32CubeG0
  (specific file used:
  `Projects/NUCLEO-G031K8/Examples_MIX/I2C/I2C_OneBoard_ComSlave7_10bits_IT/Src/stm32g0xx_hal_msp.c`)
- **License**: per the file's own header, "licensed under terms that can be
  found in the LICENSE file in the root directory of this software
  component" — this is redistributable **source code** (a CubeMX-generated
  project example ST ships and documents for exactly this purpose), a
  different regime from this directory's "never commit a datasheet PDF"
  policy (see `datasheets/README.md`); no datasheet PDF content is
  reproduced anywhere in this repository as a result of using this source,
  and no code from this file is vendored into this repository — only the
  pin/AF facts it demonstrates are cited.
- **Retrieved Date**: this session (Firmware Engineer, Bench-IMU-01 ISS-014
  firmware follow-up fix)
- **Local cache note**: fetched and reviewed in full via the GitHub API this
  session, not committed to this repository
- **Used for Evidence IDs**: DS-MCU-068 (`datasheets/evidence-log.md`)

## Why this source, and its evidentiary standing

This is ST's own officially-published, CubeMX-generated example project for
the **exact same MCU part** (STM32G031K8T6) used on the NUCLEO-G031K8
official development board — not a third-party aggregator, tutorial, or
community post. It originates directly from the manufacturer
(STMicroelectronics is the repository owner/publisher) and demonstrates the
real, working GPIO/AF configuration CubeMX itself generates for this part's
I2C2 peripheral. Treated as **primary-source-equivalent** for this
repository's evidence model (`docs/architecture.md` §6.1), on the same
footing as the manufacturer's own CMSIS-Device header
(`datasheets/stmicroelectronics_cmsis_device_g0_master.md`) already used
elsewhere in this codebase.

## What this source resolved

Independently confirms, for the exact same STM32G031K8T6 part this design
uses, that I2C2's `HAL_I2C_MspInit()` configuration:

```c
__HAL_RCC_GPIOA_CLK_ENABLE();
/**I2C2 GPIO Configuration
PA11 [PA9]     ------> I2C2_SCL
PA12 [PA10]     ------> I2C2_SDA
*/
GPIO_InitStruct.Pin = GPIO_PIN_11|GPIO_PIN_12;
GPIO_InitStruct.Mode = GPIO_MODE_AF_OD;
GPIO_InitStruct.Pull = GPIO_PULLUP;
GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
GPIO_InitStruct.Alternate = GPIO_AF6_I2C2;
HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
```

i.e. **GPIOA** (not GPIOB) clock-enabled, pins **11/12**, alternate function
**`GPIO_AF6_I2C2`**, open-drain mode (`GPIO_MODE_AF_OD`) — corroborating
`hardware/schematic/bench-imu-01-design.md`'s ISS-014 correction and
directly resolving the AF-number question this repository's firmware needed
answered (the pin database used for DS-MCU-064/067,
`STM32_open_pin_data`, lists which *signals* are available at each physical
pin but does not itself encode alternate-function *numbers*). See
`datasheets/stmicroelectronics_stm32g0xx-hal-driver_master.md` for the
independent confirmation that `GPIO_AF6_I2C2` is numerically `0x06`.
