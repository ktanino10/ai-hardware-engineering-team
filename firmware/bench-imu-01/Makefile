# Makefile -- Bench-IMU-01 bring-up firmware.
#
# Requires an ARM bare-metal GCC toolchain (arm-none-eabi-gcc). This session
# verified (see firmware/README.md and firmware/bench-imu-01/README.md for
# the full tooling-honesty disclosure) that arm-none-eabi-gcc is not
# pre-installed in this environment but IS installable via Homebrew
# (`brew install arm-none-eabi-gcc`, a bottled/pre-built formula) on macOS,
# or via your Linux distribution's package manager / ARM's own
# arm-gnu-toolchain releases elsewhere.
#
# There is no physical Bench-IMU-01 board in this environment -- `make`
# builds bench-imu-01.elf/.bin/.hex; it does not flash anything. Flashing
# (e.g. via st-flash, OpenOCD, or a debugger's own GUI) is a future,
# physical-hardware activity, not part of this repository's tooling today
# (docs/architecture.md Section 13, Future Integration).

TARGET   = bench-imu-01
BUILDDIR = build

CC      = arm-none-eabi-gcc
OBJCOPY = arm-none-eabi-objcopy
SIZE    = arm-none-eabi-size

SRCS = src/startup_stm32g031xx.c \
       src/main.c \
       src/clock.c \
       src/gpio.c \
       src/systick.c \
       src/usart2.c \
       src/i2c2.c \
       src/bmi270.c \
       src/reset_reason.c \
       src/i2c1.c \
       src/tim1_pwm.c \
       src/tim3_fg.c \
       src/drv10983.c \
       src/motor.c

OBJS = $(patsubst src/%.c,$(BUILDDIR)/%.o,$(SRCS))

# -mcpu=cortex-m0plus / -mthumb: this part is an Arm Cortex-M0+ core
# (hardware/schematic/bench-imu-01-design.md Section 1 approved-part
# summary). -ffreestanding + -nostdlib: no OS, no libc startup -- this
# firmware supplies its own Reset_Handler (startup_stm32g031xx.c) and does
# not link against a C library runtime. -lgcc IS still linked back in
# deliberately (see LDFLAGS below): it supplies pure compiler-support
# intrinsics (e.g. software integer divide -- Cortex-M0+ has no hardware
# SDIV/UDIV instruction, unlike Cortex-M3/M4) with zero OS/libc dependency
# of its own; -nostdlib alone would exclude it and fail to link any code
# that divides or takes a modulus (found by this session's actual build
# attempt, not assumed up front -- see firmware/bench-imu-01/README.md).
CFLAGS  = -mcpu=cortex-m0plus -mthumb -Os -g -Wall -Wextra -std=c11 \
          -ffreestanding -fno-common -fno-builtin -Isrc -MMD -MP
LDFLAGS = -mcpu=cortex-m0plus -mthumb -T linker/STM32G031K8Tx_FLASH.ld \
          -nostdlib -Wl,--gc-sections -Wl,-Map=$(BUILDDIR)/$(TARGET).map
LDLIBS  = -lgcc

.PHONY: all clean size

all: $(BUILDDIR)/$(TARGET).elf $(BUILDDIR)/$(TARGET).bin $(BUILDDIR)/$(TARGET).hex size

$(BUILDDIR):
	mkdir -p $(BUILDDIR)

$(BUILDDIR)/%.o: src/%.c | $(BUILDDIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILDDIR)/$(TARGET).elf: $(OBJS)
	$(CC) $(LDFLAGS) $(OBJS) $(LDLIBS) -o $@

$(BUILDDIR)/$(TARGET).bin: $(BUILDDIR)/$(TARGET).elf
	$(OBJCOPY) -O binary $< $@

$(BUILDDIR)/$(TARGET).hex: $(BUILDDIR)/$(TARGET).elf
	$(OBJCOPY) -O ihex $< $@

size: $(BUILDDIR)/$(TARGET).elf
	$(SIZE) $<

clean:
	rm -rf $(BUILDDIR)

-include $(OBJS:.o=.d)
