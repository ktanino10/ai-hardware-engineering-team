/*
 * STM32G031K8Tx_FLASH.ld -- minimal linker script for Bench-IMU-01 bring-up
 * firmware.
 *
 * Memory sizes are the approved-part summary's own figures
 * (hardware/schematic/bench-imu-01-design.md Section 1: "64KB Flash + 8KB
 * SRAM") -- independently re-confirmed this session directly against ST's
 * official CMSIS-Device header (cmsis_device_g0, stm32g031xx.h):
 * FLASH_BASE=0x08000000, SRAM_BASE=0x20000000, SRAM_SIZE_MAX=0x2000 (8 KB).
 * The STM32G031K8T6's "K8" suffix denotes 64 KB Flash per ST's standard
 * part-numbering convention (already the figure the approved-part table
 * cites).
 */
MEMORY
{
  FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 64K
  RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 8K
}

/* Top of RAM, used as the initial stack pointer (vector table entry 0). */
_estack = ORIGIN(RAM) + LENGTH(RAM);

SECTIONS
{
  .isr_vector :
  {
    . = ALIGN(4);
    KEEP(*(.isr_vector))
    . = ALIGN(4);
  } > FLASH

  .text :
  {
    . = ALIGN(4);
    *(.text)
    *(.text*)
    *(.rodata)
    *(.rodata*)
    . = ALIGN(4);
  } > FLASH

  /* Symbols consumed by startup_stm32g031xx.c's Reset_Handler to copy
   * initialized-data from Flash to RAM. */
  _sidata = LOADADDR(.data);

  .data :
  {
    . = ALIGN(4);
    _sdata = .;
    *(.data)
    *(.data*)
    . = ALIGN(4);
    _edata = .;
  } > RAM AT> FLASH

  .bss :
  {
    . = ALIGN(4);
    _sbss = .;
    *(.bss)
    *(.bss*)
    *(COMMON)
    . = ALIGN(4);
    _ebss = .;
  } > RAM

  /DISCARD/ :
  {
    *(.comment)
    *(.ARM.attributes)
  }
}
