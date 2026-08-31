# STMicroelectronics CMSIS-Device G0 — Official Register-Definition Header

- **Manufacturer**: STMicroelectronics
- **Part Number / Family**: STM32G0 series (this project uses the
  `stm32g031xx.h` device-specific header for the STM32G031K8T6, U1)
- **Document Title**: N/A — this is not a datasheet PDF, it is
  STMicroelectronics' own official, redistributable open-source **CMSIS
  Device Peripheral Access Layer header source code** (register struct
  definitions, base addresses, and bit-position macros for every STM32G0
  peripheral), not a scanned/typeset manufacturer document.
- **Revision / Version**: `master` branch, as fetched this session (no
  pinned commit hash recorded — the memory map / peripheral register layout
  for a shipped, unchanged-since-release part like the STM32G031K8T6 is not
  expected to change upstream; re-fetch and diff if ever in doubt)
- **Publication Date**: file's own header states "Copyright (c) 2018-2021
  STMicroelectronics"
- **Official URL**: https://github.com/STMicroelectronics/cmsis_device_g0
  (specific file used:
  `Include/stm32g031xx.h`, fetched via
  `https://raw.githubusercontent.com/STMicroelectronics/cmsis_device_g0/master/Include/stm32g031xx.h`)
- **License**: per the file's own header, "licensed under terms that can be
  found in the LICENSE file in the root directory of this software
  component" (an Apache-2.0-style permissive license typical of ST's CMSIS
  packages) — this is redistributable **source code**, a different regime
  from this directory's "never commit a datasheet PDF" policy (see
  `datasheets/README.md`); no datasheet PDF content is reproduced anywhere
  in this repository as a result of using this source.
- **Retrieved Date**: this session (Bench-IMU-01 firmware bring-up,
  Firmware Engineer)
- **Local cache note**: fetched and grepped locally this session for
  register struct layouts/base addresses/bit-position macros, not committed
  to this repository (only the small, purpose-built subset actually needed
  is hand-written into `firmware/bench-imu-01/src/stm32g031_regs.h`, citing
  this record)
- **Used for Evidence IDs**: DS-MCU-055 through DS-MCU-061, and DS-MCU-074/
  DS-MCU-075 (see `datasheets/evidence-log.md`) — STM32G031K8T6 peripheral
  memory map (FLASH/SRAM/RCC/GPIOA/GPIOB/I2C1/I2C2/USART2 base addresses),
  GPIO/RCC/I2C/USART register-struct offsets, and RCC clock-enable/
  reset-reason bit positions used by the Bench-IMU-01 bring-up firmware.
  Rev 3 (Motor Driver subsystem, 2026-09-10) added DS-MCU-074 (I2C1 base
  address + RCC_APBENR1_I2C1EN, reusing the generic I2C_TypeDef struct
  already covered above) and DS-MCU-075 (TIM1/TIM3 base addresses, the
  TIM_TypeDef struct, and RCC_APBENR1_TIM3EN/RCC_APBENR2_TIM1EN), for the
  new PA8/TIM1 PWM-speed-command and PA6/TIM3 FG-tachometer-capture
  peripherals. (The GPIO alternate-function *values* for I2C2, DS-MCU-062,
  and for I2C1/TIM1/TIM3, DS-MCU-074/075's own AF cross-checks, come from
  the part's datasheet/pin-database/web-corroboration, not this CMSIS
  header — this header defines register structs/addresses, not the
  pin-to-AF mapping table.)
- **Cross-check note**: the RCC_IOPENR/RCC_APBENR1/RCC_CSR bit positions
  cited from this source were independently cross-checked this session
  against a second, independent source (a web search summarizing STM32G0
  RM0444/RM0454 register tables, corroborated by the long-established
  open-source libopencm3 project's own independently-derived STM32G0
  register definitions) before being used — both agreed exactly.
