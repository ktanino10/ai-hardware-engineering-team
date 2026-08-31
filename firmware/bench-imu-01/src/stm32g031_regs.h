/*
 * stm32g031_regs.h -- Minimal, hand-written STM32G031K8T6 peripheral register
 * definitions for Bench-IMU-01 bring-up firmware.
 *
 * This is NOT a vendored copy of ST's CMSIS-Device header (that file defines
 * every peripheral on the whole STM32G0 family and would be far more than
 * this small bring-up program needs). It is a minimal, purpose-built subset,
 * covering only the peripherals this board's schematic actually uses:
 * RCC, GPIOA, GPIOB, I2C2, USART2, plus the Cortex-M0+ core's SysTick.
 * Rev 3 (Motor Driver + Reaction Wheel subsystem) added I2C1 (U5 DRV10983
 * commissioning/status bus), TIM1 (SPEED PWM), and TIM3 (FG tachometer
 * input capture) -- see the Rev 3-labelled sections below.
 *
 * Every base address, register offset, and bit position below was
 * independently confirmed THIS SESSION directly against STMicroelectronics'
 * own official CMSIS-Device header for this exact part family
 * (https://github.com/STMicroelectronics/cmsis_device_g0,
 * Include/stm32g031xx.h, master branch) -- not derived from memory, not
 * guessed. See datasheets/evidence-log.md for the DS-MCU-<NNN> Evidence ID
 * rows this file's constants map to; see
 * datasheets/stmicroelectronics_cmsis_device_g0_rev-unknown.md for the
 * source's metadata record.
 *
 * Register field names below mirror ST's own CMSIS naming so this file reads
 * naturally against ST reference-manual (RM0454) tables.
 */
#ifndef BENCH_IMU_01_STM32G031_REGS_H
#define BENCH_IMU_01_STM32G031_REGS_H

#include <stdint.h>

#define __IO volatile

/* ---------------------------------------------------------------------- */
/* Memory map (DS-MCU-<NNN>: cmsis_device_g0 Include/stm32g031xx.h,        */
/* "Peripheral_memory_map" section)                                       */
/* ---------------------------------------------------------------------- */
#define FLASH_BASE_ADDR   0x08000000UL /* 64 KB on the K8 variant */
#define SRAM_BASE_ADDR    0x20000000UL /* 8 KB on this part */
#define PERIPH_BASE       0x40000000UL
#define IOPORT_BASE       0x50000000UL
#define APBPERIPH_BASE    (PERIPH_BASE)
#define AHBPERIPH_BASE    (PERIPH_BASE + 0x00020000UL)

#define USART2_BASE  (APBPERIPH_BASE + 0x00004400UL) /* 0x40004400 */
#define I2C1_BASE    (APBPERIPH_BASE + 0x00005400UL) /* 0x40005400 -- Rev 3 Motor Driver subsystem: U5 (DRV10983) commissioning/status bus, PB6(SCL)/PB7(SDA), DS-MCU-074. Distinct instance from I2C2 below. */
#define I2C2_BASE    (APBPERIPH_BASE + 0x00005800UL) /* 0x40005800 -- IMU bus (BMI270). NOT I2C1 (0x40005400): the schematic's IMU bus is I2C2, corrected from an original I2C1 mislabeling caught by Hardware Reviewer (ISS-011, hardware/schematic/bench-imu-01-design.md Section 2.3/Section 5.2). Using the wrong base address here would silently reproduce that exact defect at the firmware layer. As of Rev 3/ISS-027 (see GPIOA_BASE/GPIOB_BASE note below), this bus's *pins* are PA11(SCL)/PA12(SDA) -- the peripheral instance/base address itself is unaffected by that pin correction. */
#define RCC_BASE     (AHBPERIPH_BASE + 0x00001000UL) /* 0x40021000 */
#define GPIOA_BASE   (IOPORT_BASE + 0x00000000UL)    /* 0x50000000 */
#define GPIOB_BASE   (IOPORT_BASE + 0x00000400UL)    /* 0x50000400 -- Rev 3: now used for DIR(PB1)/I2C1 SCL+SDA(PB6/PB7), not the IMU bus (see ISS-027 below) */

/* ---------------------------------------------------------------------- */
/* TIM1/TIM3 base addresses (DS-MCU-075) -- Rev 3 Motor Driver subsystem:  */
/* TIM1 drives SPEED PWM (PA8/TIM1_CH1), TIM3 captures the FG tachometer   */
/* signal (PA6/TIM3_CH1). TIM1 is on APB2 (RCC->APBENR2, previously       */
/* unused by this firmware); TIM3 is on APB1 (RCC->APBENR1, alongside     */
/* I2C1/I2C2/USART2 already used here).                                   */
/* ---------------------------------------------------------------------- */
#define TIM3_BASE (APBPERIPH_BASE + 0x00000400UL) /* 0x40000400 */
#define TIM1_BASE (APBPERIPH_BASE + 0x00012C00UL) /* 0x40012C00 */

/* ---------------------------------------------------------------------- */
/* GPIO (DS-MCU-<NNN>: GPIO_TypeDef, offsets confirmed against the CMSIS   */
/* header -- identical layout for GPIOA/GPIOB)                            */
/* ---------------------------------------------------------------------- */
typedef struct
{
    __IO uint32_t MODER;   /* 0x00 mode: 00=input 01=output 10=AF 11=analog */
    __IO uint32_t OTYPER;  /* 0x04 output type: 0=push-pull 1=open-drain */
    __IO uint32_t OSPEEDR; /* 0x08 */
    __IO uint32_t PUPDR;   /* 0x0C pull-up/down: 00=none 01=pull-up 10=pull-down */
    __IO uint32_t IDR;     /* 0x10 input data (read-only in practice) */
    __IO uint32_t ODR;     /* 0x14 output data */
    __IO uint32_t BSRR;    /* 0x18 atomic bit set/reset */
    __IO uint32_t LCKR;    /* 0x1C */
    __IO uint32_t AFR[2];  /* 0x20/0x24 -- AFR[0]=AFRL (pins 0-7), AFR[1]=AFRH (pins 8-15), 4 bits/pin */
    __IO uint32_t BRR;     /* 0x28 */
} GPIO_TypeDef;

#define GPIOA ((GPIO_TypeDef *)GPIOA_BASE)
#define GPIOB ((GPIO_TypeDef *)GPIOB_BASE) /* Rev 3: DIR(PB1)/I2C1 SCL+SDA(PB6/PB7) -- see GPIOB_BASE above and clock.c's RCC_IOPENR_GPIOBEN enable. This define was silently dropped by the origin/main merge (main's own Rev-2-only scope correctly has no GPIOB user, so it deleted this cleanly with no conflict marker) -- restored here because motor.c/gpio.c's Rev 3 motor subsystem genuinely dereferences GPIOB. */

/* ---------------------------------------------------------------------- */
/* RCC (DS-MCU-<NNN>: RCC_TypeDef, offsets confirmed against the CMSIS     */
/* header)                                                                 */
/* ---------------------------------------------------------------------- */
typedef struct
{
    __IO uint32_t CR;         /* 0x00 */
    __IO uint32_t ICSCR;      /* 0x04 */
    __IO uint32_t CFGR;       /* 0x08 */
    __IO uint32_t PLLCFGR;    /* 0x0C -- unused: this design runs on default HSI16, no PLL (see clock.c) */
    __IO uint32_t RESERVED0;  /* 0x10 */
    __IO uint32_t RESERVED1;  /* 0x14 */
    __IO uint32_t CIER;       /* 0x18 */
    __IO uint32_t CIFR;       /* 0x1C */
    __IO uint32_t CICR;       /* 0x20 */
    __IO uint32_t IOPRSTR;    /* 0x24 */
    __IO uint32_t AHBRSTR;    /* 0x28 */
    __IO uint32_t APBRSTR1;   /* 0x2C */
    __IO uint32_t APBRSTR2;   /* 0x30 */
    __IO uint32_t IOPENR;     /* 0x34 -- I/O port clock enables (GPIOAEN/GPIOBEN) */
    __IO uint32_t AHBENR;     /* 0x38 */
    __IO uint32_t APBENR1;    /* 0x3C -- I2C2EN / USART2EN / PWREN live here */
    __IO uint32_t APBENR2;    /* 0x40 */
    __IO uint32_t IOPSMENR;   /* 0x44 */
    __IO uint32_t AHBSMENR;   /* 0x48 */
    __IO uint32_t APBSMENR1;  /* 0x4C */
    __IO uint32_t APBSMENR2;  /* 0x50 */
    __IO uint32_t CCIPR;      /* 0x54 */
    __IO uint32_t RESERVED2;  /* 0x58 */
    __IO uint32_t BDCR;       /* 0x5C */
    __IO uint32_t CSR;        /* 0x60 -- reset-reason flags (REQ-004/SW1->NRST reporting, see reset_reason.c) */
} RCC_TypeDef;

#define RCC ((RCC_TypeDef *)RCC_BASE)

/* RCC_IOPENR bit positions (DS-MCU-058) */
#define RCC_IOPENR_GPIOAEN (1UL << 0)
#define RCC_IOPENR_GPIOBEN (1UL << 1) /* Rev 3: GPIOB now used for DIR(PB1)/
 * I2C1 SCL+SDA(PB6/PB7) -- see GPIOB_BASE/clock.c. This define was silently
 * dropped by the origin/main merge (correct for main's own GPIOB-free Rev-2
 * scope, but wrong here) and is restored because clock.c's
 * RCC->IOPENR |= RCC_IOPENR_GPIOAEN | RCC_IOPENR_GPIOBEN would otherwise
 * fail to compile. The IMU's own I2C2 bus no longer needs GPIOB (it moved
 * to PA11/PA12 on GPIOA, ISS-027) -- GPIOBEN is enabled for the motor
 * subsystem's pins, not the IMU. */

/* RCC_APBENR1 bit positions */
#define RCC_APBENR1_TIM3EN    (1UL << 1)  /* Rev 3: TIM3 (FG tachometer input capture, PA6) */
#define RCC_APBENR1_USART2EN  (1UL << 17)
#define RCC_APBENR1_I2C1EN    (1UL << 21) /* Rev 3: I2C1 (U5 DRV10983 commissioning/status bus, PB6/PB7), DS-MCU-074 */
#define RCC_APBENR1_I2C2EN    (1UL << 22)
#define RCC_APBENR1_PWREN     (1UL << 28)

/* RCC_APBENR2 bit positions (Rev 3: first use of this register by this
 * firmware -- previously only APBENR1/IOPENR were used) */
#define RCC_APBENR2_TIM1EN (1UL << 11) /* TIM1 (SPEED PWM, PA8), DS-MCU-075 */

/* RCC_CSR reset-reason flag bit positions (cleared together by RMVF) */
#define RCC_CSR_RMVF     (1UL << 23) /* write 1 to clear all *RSTF flags below */
#define RCC_CSR_OBLRSTF  (1UL << 25) /* option byte loader reset */
#define RCC_CSR_PINRSTF  (1UL << 26) /* NRST pin reset -- this is SW1 (REQ-004) or a debugger reset */
#define RCC_CSR_PWRRSTF  (1UL << 27) /* BOR/POR (power) reset */
#define RCC_CSR_SFTRSTF  (1UL << 28) /* software (NVIC AIRCR.SYSRESETREQ) reset */
#define RCC_CSR_IWDGRSTF (1UL << 29) /* independent watchdog reset */
#define RCC_CSR_WWDGRSTF (1UL << 30) /* window watchdog reset */
#define RCC_CSR_LPWRRSTF (1UL << 31) /* illegal low-power mode entry reset */

/* ---------------------------------------------------------------------- */
/* I2C (DS-MCU-<NNN>: I2C_TypeDef, "I2C peripheral v2" generation shared   */
/* across STM32 F0/G0/L0/L4 -- offsets/bit positions confirmed against the */
/* CMSIS header)                                                          */
/* ---------------------------------------------------------------------- */
typedef struct
{
    __IO uint32_t CR1;      /* 0x00 */
    __IO uint32_t CR2;      /* 0x04 */
    __IO uint32_t OAR1;     /* 0x08 */
    __IO uint32_t OAR2;     /* 0x0C */
    __IO uint32_t TIMINGR;  /* 0x10 */
    __IO uint32_t TIMEOUTR; /* 0x14 */
    __IO uint32_t ISR;      /* 0x18 */
    __IO uint32_t ICR;      /* 0x1C */
    __IO uint32_t PECR;     /* 0x20 */
    __IO uint32_t RXDR;     /* 0x24 */
    __IO uint32_t TXDR;     /* 0x28 */
} I2C_TypeDef;

#define I2C2 ((I2C_TypeDef *)I2C2_BASE)
/* Rev 3: I2C1 (U5 DRV10983 commissioning/status bus, PB6/PB7). Same
 * "I2C peripheral v2" IP block as I2C2 above -- reuses I2C_TypeDef as-is,
 * no separate struct needed (DS-MCU-074). */
#define I2C1 ((I2C_TypeDef *)I2C1_BASE)

#define I2C_CR1_PE (1UL << 0)

#define I2C_CR2_RD_WRN  (1UL << 10)
#define I2C_CR2_START   (1UL << 13)
#define I2C_CR2_STOP    (1UL << 14)
#define I2C_CR2_AUTOEND (1UL << 25)
#define I2C_CR2_SADD_POS   0
#define I2C_CR2_NBYTES_POS 16

#define I2C_ISR_TXIS  (1UL << 1)
#define I2C_ISR_RXNE  (1UL << 2)
#define I2C_ISR_NACKF (1UL << 4)
#define I2C_ISR_STOPF (1UL << 5)
#define I2C_ISR_TC    (1UL << 6)
#define I2C_ISR_BUSY  (1UL << 15)

/* I2C_TIMINGR for Fast-mode (400 kHz) at a 16 MHz PCLK -- ST's own
 * published example value (AN4235 Table 11 "I2C timings for 16 MHz PCLK",
 * cross-checked this session against a second, independent source):
 * PRESC=0, SCLDEL=3, SDADEL=1, SCLH=3, SCLL=9 -> 0x00310309. This is the
 * standard ST-published value for exactly this clock/speed combination, not
 * independently re-derived from the UM10204 formula this session (the
 * schematic's own R3/R4 pull-up sizing in hardware/schematic/
 * bench-imu-01-design.md Section 5.2 already did that derivation for the
 * *analog* bus timing; this is the *digital* peripheral timing register,
 * a related but separate calculation ST provides pre-computed). */
#define I2C2_TIMINGR_400KHZ_AT_16MHZ 0x00310309UL

/* ---------------------------------------------------------------------- */
/* TIM1 / TIM3 (DS-MCU-075: TIM_TypeDef, offsets/bit positions confirmed   */
/* against the CMSIS device header, `datasheets/                          */
/* stmicroelectronics_cmsis_device_g0_master.md`) -- Rev 3 Motor Driver    */
/* subsystem. One unified struct services both instances per ST's own     */
/* CMSIS convention; TIM1 additionally uses RCR/BDTR (advanced-control     */
/* timer, needed for SPEED PWM's break/main-output-enable gating), TIM3    */
/* does not (general-purpose timer, FG input capture only leaves those two */
/* registers unused -- harmless, not read/written by tim3_fg.c).          */
/* ---------------------------------------------------------------------- */
typedef struct
{
    __IO uint32_t CR1;   /* 0x00 */
    __IO uint32_t CR2;   /* 0x04 */
    __IO uint32_t SMCR;  /* 0x08 */
    __IO uint32_t DIER;  /* 0x0C */
    __IO uint32_t SR;    /* 0x10 */
    __IO uint32_t EGR;   /* 0x14 */
    __IO uint32_t CCMR1; /* 0x18 */
    __IO uint32_t CCMR2; /* 0x1C */
    __IO uint32_t CCER;  /* 0x20 */
    __IO uint32_t CNT;   /* 0x24 */
    __IO uint32_t PSC;   /* 0x28 */
    __IO uint32_t ARR;   /* 0x2C */
    __IO uint32_t RCR;   /* 0x30 -- TIM1 only (repetition counter) */
    __IO uint32_t CCR1;  /* 0x34 */
    __IO uint32_t CCR2;  /* 0x38 */
    __IO uint32_t CCR3;  /* 0x3C */
    __IO uint32_t CCR4;  /* 0x40 */
    __IO uint32_t BDTR;  /* 0x44 -- TIM1 only (break and dead-time) */
} TIM_TypeDef;

#define TIM1 ((TIM_TypeDef *)TIM1_BASE) /* SPEED PWM, PA8/CH1 */
#define TIM3 ((TIM_TypeDef *)TIM3_BASE) /* FG tachometer input capture, PA6/CH1 */

#define TIM_CR1_CEN   (1UL << 0)
#define TIM_CR1_ARPE  (1UL << 7)

#define TIM_EGR_UG (1UL << 0)

/* CCMR1 channel-1 field positions/widths -- same register serves either a
 * PWM-output role (TIM1) or an input-capture role (TIM3); only the fields
 * relevant to each module's own use are exercised by tim1_pwm.c/tim3_fg.c
 * respectively, but all are recorded here since they share one struct. */
#define TIM_CCMR1_CC1S_POS  0   /* 00 = output, 01 = IC1 on TI1 (used by tim3_fg.c) */
#define TIM_CCMR1_OC1PE     (1UL << 3)  /* output-compare 1 preload enable (used by tim1_pwm.c, pairs with ARPE) */
#define TIM_CCMR1_OC1M_POS  4   /* 3-bit field; 0b110 = PWM mode 1 (used by tim1_pwm.c) */
#define TIM_CCMR1_IC1PSC_POS 2  /* input-capture 1 prescaler; 00 = capture every edge (used by tim3_fg.c) */
#define TIM_CCMR1_IC1F_POS  4   /* input-capture 1 filter; 0000 = no filter (used by tim3_fg.c) */

#define TIM_CCER_CC1E (1UL << 0) /* capture/compare 1 output or capture enable */
#define TIM_CCER_CC1P (1UL << 1) /* capture/compare 1 polarity: 0 = rising edge (used by tim3_fg.c, FG's own default active edge) */

#define TIM_SR_UIF   (1UL << 0)
#define TIM_SR_CC1IF (1UL << 1) /* set on a new IC1 capture event; reading CCR1 clears it (standard ARM/STM32 timer IP behaviour) */

#define TIM_BDTR_MOE (1UL << 15) /* main output enable -- TIM1 only; CC1 output does not reach the pin until this is set */

/* DIER (DMA/interrupt enable register) -- Rev 3 addition, DS-MCU-076.
 * CC1IE mirrors SR_CC1IF's own bit position (bit 1), the standard STM32
 * timer-IP convention of "DIER bit N enables the interrupt for the event
 * that sets SR bit N" -- used only by tim3_fg.c, to make FG capture
 * interrupt-driven (see tim3_fg.h's own header comment for why pure
 * polling was rejected: at ~20,000 RPM the FG period is ~0.43ms, far
 * shorter than any safe main-loop poll interval, so a poll could silently
 * miss/coalesce edges and under-report RPM -- dangerous for REQ-405's
 * overspeed cutoff, which depends on RPM being trustworthy). Not used by
 * tim1_pwm.c (PWM output generation needs no interrupt). */
#define TIM_DIER_CC1IE (1UL << 1)

/* ---------------------------------------------------------------------- */
/* USART (DS-MCU-<NNN>: USART_TypeDef, offsets/bit positions confirmed     */
/* against the CMSIS header)                                              */
/* ---------------------------------------------------------------------- */
typedef struct
{
    __IO uint32_t CR1;  /* 0x00 */
    __IO uint32_t CR2;  /* 0x04 */
    __IO uint32_t CR3;  /* 0x08 */
    __IO uint32_t BRR;  /* 0x0C */
    __IO uint32_t GTPR; /* 0x10 */
    __IO uint32_t RTOR; /* 0x14 */
    __IO uint32_t RQR;  /* 0x18 */
    __IO uint32_t ISR;  /* 0x1C */
    __IO uint32_t ICR;  /* 0x20 */
    __IO uint32_t RDR;  /* 0x24 */
    __IO uint32_t TDR;  /* 0x28 */
    __IO uint32_t PRESC;/* 0x2C */
} USART_TypeDef;

#define USART2 ((USART_TypeDef *)USART2_BASE)

#define USART_CR1_UE (1UL << 0)
#define USART_CR1_RE (1UL << 2)
#define USART_CR1_TE (1UL << 3)
/* M0=0, M1=0 (CR1 bit 28, not used here) => default 8 data bits.
 * OVER8=0 (CR1 bit 15, not set) => default oversampling by 16, the standard
 * BRR = fCK / baud formula used in usart2.c. Both left at their reset
 * default of 0 -- no bit macro needed for "leave at reset default". */

#define USART_ISR_RXNE (1UL << 5)
#define USART_ISR_TC   (1UL << 6)
#define USART_ISR_TXE  (1UL << 7)

/* ---------------------------------------------------------------------- */
/* Cortex-M0+ core peripheral: SysTick. Fixed ARM architectural address    */
/* (0xE000E010), not vendor-specific -- same on every Cortex-M part, per   */
/* the ARMv6-M Architecture Reference Manual, not an ST-specific fact.     */
/* ---------------------------------------------------------------------- */
typedef struct
{
    __IO uint32_t CTRL;
    __IO uint32_t LOAD;
    __IO uint32_t VAL;
    __IO uint32_t CALIB;
} SysTick_TypeDef;

#define SysTick ((SysTick_TypeDef *)0xE000E010UL)

#define SysTick_CTRL_ENABLE    (1UL << 0)
#define SysTick_CTRL_TICKINT   (1UL << 1)
#define SysTick_CTRL_CLKSOURCE (1UL << 2) /* 1 = processor clock (HSI16), not an external reference */
#define SysTick_CTRL_COUNTFLAG (1UL << 16)

/* ---------------------------------------------------------------------- */
/* Cortex-M0+ core peripheral: NVIC (Nested Vectored Interrupt Controller) */
/* -- Rev 3 addition, DS-MCU-076. Fixed ARM architectural address          */
/* (0xE000E100), not vendor-specific -- same class of fact as SysTick's   */
/* own address above (ARMv6-M Architecture Reference Manual). Cortex-M0+  */
/* implements a SIMPLIFIED NVIC vs. M3/M4/M7: only one 32-bit ISER        */
/* register exists (covering IRQn 0-31), because M0+ supports at most 32  */
/* external interrupts -- there is no ISER1..ISER7 array to index here,   */
/* unlike larger Cortex-M parts. This firmware only ever needs to enable   */
/* one interrupt (TIM3, for FG tachometer capture -- tim3_fg.c), so a      */
/* single bare register define is used rather than a full NVIC_TypeDef    */
/* struct, matching this file's existing minimal/hand-written style       */
/* (compare SysTick above, which likewise omits IP/IPR fields this        */
/* firmware never touches). TIM3's IRQn=16 (DS-MCU-076, confirmed         */
/* directly against the CMSIS `IRQn_Type` enum) is NOT defined here as a   */
/* generic "IRQn" enum -- it is used directly, once, in tim3_fg.c's own   */
/* init function, with a comment pointing back to this evidence row,      */
/* since this firmware has no other interrupt sources needing a shared    */
/* IRQn table. */
/* ---------------------------------------------------------------------- */
#define NVIC_ISER (*(__IO uint32_t *)0xE000E100UL)

#define TIM3_IRQn 16 /* DS-MCU-076: cmsis_device_g0 IRQn_Type, "TIM3_IRQn = 16" */

#endif /* BENCH_IMU_01_STM32G031_REGS_H */
