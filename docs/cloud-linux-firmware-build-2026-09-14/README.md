# Linux build-prerequisite verification -- Bench-IMU-01 (2026-09-14)

Task key: `rev5-public-main-arm-build-2026-09-14`. Base: PUBLIC `main`,
starting commit **a6ebb82d712746087aa1735198f5a3778d799fd7** (verified via
`git log -1` before any change in this session).

This is a **compilation-only prerequisite** check for the existing, unchanged
public [`firmware/bench-imu-01`](../../firmware/bench-imu-01/) ARM
bare-metal target on the standard hosted Ubuntu runner. It is distinct from
[PR #76](https://github.com/ktanino10/ai-hardware-engineering-team/pull/76)'s
developer CLI/workflow-tool check, and it is **not** firmware logic design,
hardware commissioning, or safety qualification. It does not supersede or
relabel the existing macOS/Homebrew build record in
[`firmware/bench-imu-01/README.md`](../../firmware/bench-imu-01/README.md) --
that record is a prior actual build, not a declared universal toolchain pin,
and it is left in place, only supplemented with this new Linux result.

## 1. Toolchain availability (hosted Ubuntu)

Before this session, `arm-none-eabi-gcc`, `arm-none-eabi-objcopy`, and
`arm-none-eabi-size` were **not** present on the runner (`which` found
nothing for any of the three). The existing README already names "your
Linux distribution's package manager" as an acceptable alternate source to
Homebrew, so the ordinary Ubuntu-distributed packages were installed --
no custom/paid runner, external credential, or unverified mirror:

```sh
sudo apt-get update
sudo apt-get install -y gcc-arm-none-eabi binutils-arm-none-eabi
```

Installed (Ubuntu 24.04.5 LTS "noble", `apt-cache policy`):

| Package | Version | Source |
|---|---|---|
| `gcc-arm-none-eabi` | `15:13.2.rel1-2` (reports `arm-none-eabi-gcc (15:13.2.rel1-2) 13.2.1 20231009`) | Ubuntu `noble`/`universe` archive |
| `binutils-arm-none-eabi` | `2.42-1ubuntu1+23` (`arm-none-eabi-objcopy`/`arm-none-eabi-size` both report GNU Binutils `2.42`) | Ubuntu `noble`/`universe` archive |

This differs from the README's recorded macOS build (`arm-none-eabi-gcc
16.2.0` via Homebrew) -- both are legitimate distribution channels for the
same public GNU Arm Embedded toolchain family; see "Differences from the
recorded macOS build" below for the resulting, expected size delta.

## 2. Build (unchanged target, fresh task-owned output path)

The Makefile already supports overriding `BUILDDIR`, so the build was
redirected to a fresh, task-owned path outside the tracked tree instead of
using (or `clean`-ing) the default `firmware/bench-imu-01/build/`:

```sh
cd firmware/bench-imu-01
make BUILDDIR=/tmp/rev5-linux-build/build
```

No `Makefile`, linker script, or source file was edited to perform this
build -- same `CFLAGS`/`LDFLAGS`/`LDLIBS` and the same 14 `SRCS` as committed.
**Exit code: 0. Zero compiler warnings** under `-Wall -Wextra` across all 14
translation units and the final link. Full transcript:
[`build.log`](build.log).

## 3. Output verification

All three requested artifacts plus the link map were produced as real,
non-empty files in the task-owned path (not committed -- see "Storage"
below):

| File | Size (bytes) | SHA-256 |
|---|---|---|
| `bench-imu-01.elf` | 63548 | `7f320c5d694faec64cb6c6c72e85f4036133d0ed0bd6983f8ae894a06415cd88` |
| `bench-imu-01.bin` | 14844 | `e245a0d04d5688fa57ffc0ff35b5d4ed0345ae1a84758b7a3d837e5cc46f0b35` |
| `bench-imu-01.hex` | 41816 | `b4fd3a70ec598e73f23a3af8adc75b136823ad6b07c0b131f43e706a56bcb7c8` |
| `bench-imu-01.map` | 24775 | `aae47c18b7fd930929f76d52fa2be3ad9f3b74d50b127b90cfdd0886765086f7` |

`file bench-imu-01.elf`:

```
bench-imu-01.elf: ELF 32-bit LSB executable, ARM, EABI5 version 1 (SYSV), statically linked, with debug_info, not stripped
```

`arm-none-eabi-readelf -h` confirms `Class: ELF32`, `Data: 2's complement,
little endian`, `Machine: ARM` -- the expected Cortex-M0+/Thumb target, not a
host-native binary.

`arm-none-eabi-size bench-imu-01.elf`:

```
   text	   data	    bss	    dec	    hex	filename
  14844	      0	    108	  14952	   3a68	bench-imu-01.elf
```

`arm-none-eabi-readelf -S` static section placement, checked against the
**unchanged** `linker/STM32G031K8Tx_FLASH.ld` memory regions
(`FLASH: ORIGIN = 0x08000000, LENGTH = 64K`; `RAM: ORIGIN = 0x20000000,
LENGTH = 8K`):

| Section | Address | Size (bytes) | Region | Fits? |
|---|---|---|---|---|
| `.isr_vector` | `0x08000000` | 184 | FLASH | yes |
| `.text` | `0x080000b8` | 14660 | FLASH | yes |
| `.data` | `0x20000000` | 0 | RAM (load, zero-length) | yes |
| `.bss` | `0x20000000` | 108 | RAM | yes |

`.isr_vector` starts exactly at `FLASH`'s origin and `.data`/`.bss` start
exactly at `RAM`'s origin, matching the linker script's own memory map with
no change to it. Total FLASH usage (14844 bytes) is well within the 64 KB
region; total RAM usage (108 bytes) is well within the 8 KB region -- same
conclusion as the existing README's macOS record, just re-derived
independently from this build's own artifacts.

### Differences from the recorded macOS build

The README's existing macOS record: `arm-none-eabi-gcc 16.2.0`, **14,752
bytes** `.text`/`.rodata`, **108 bytes** `.bss`, 0 bytes `.data`. This Linux
build (`arm-none-eabi-gcc 13.2.1`): **14,844 bytes** combined
`.isr_vector`+`.text` (+92 bytes), **108 bytes** `.bss` (identical), 0 bytes
`.data` (identical). The `.bss` figure matches exactly; the small FLASH-side
delta is consistent with the two builds using different upstream GCC 13 vs.
16 releases (different code-generation/optimizer revisions for the same
`-Os`), not a source, flag, or linker-region change -- none of `CFLAGS`,
`LDFLAGS`, or the linker script were touched to produce this build. No flag
was retuned to chase a particular number.

## 4. No flashing / debugger / hardware execution

The Makefile's default (`all`) target and its prerequisites
(`$(BUILDDIR)/$(TARGET).elf/.bin/.hex`, `size`) only compile, link, and
`objcopy` -- there is no `flash`, `openocd`, `st-flash`, `gdb`, or serial
target anywhere in the Makefile (confirmed by inspection; the only
flash-adjacent word in the file is the linker script's own filename,
`STM32G031K8Tx_FLASH.ld`). This session ran only `make` (and `make
BUILDDIR=...`); it did not invoke a flash target, a debugger, an emulator, a
simulator, or any serial/hardware interface, and no physical Bench-IMU-01
board exists in this environment.

## 5. Storage and reproducibility

Build outputs and the full log live only in this session's task-owned
scratch path (`/tmp/rev5-linux-build/`), never committed and never uploaded
as a CI/Actions artifact -- consistent with the task's write scope. Only
this handoff document, its size/hash table, and
[`build.log`](build.log) (a small compiler-invocation transcript, no
binaries) are added to the repository. No workflow YAML, `tools/`, or root
policy file was touched. `firmware/bench-imu-01/Makefile` was **not**
modified -- the fresh-output build via the Makefile's own `BUILDDIR`
override fully reproduced the existing target with no code defect found, so
no regression was needed (per the task's own "no code defect -> documentation
is the deliverable" instruction). Reproduce with:

```sh
sudo apt-get update && sudo apt-get install -y gcc-arm-none-eabi binutils-arm-none-eabi
cd firmware/bench-imu-01
make BUILDDIR=/tmp/rev5-linux-build/build
arm-none-eabi-size /tmp/rev5-linux-build/build/bench-imu-01.elf
sha256sum /tmp/rev5-linux-build/build/bench-imu-01.{elf,bin,hex,map}
```

## Scope and unchanged holds

This confirms the existing public target compiles cleanly on hosted Ubuntu
and that its static section placement still fits the unchanged linker
memory regions. It is **not**: measured stack headroom, ISR runtime
correctness, physical timing, electrical/motor safety, flashing, hardware
bring-up, or Design Complete. No C/H source, register map, clock, pin
mapping, threshold, part choice, or linker memory limit was changed. The
existing unqualified hardware/source conditions recorded elsewhere in this
repository remain unqualified.

## Handoff for LOCAL GPT-6 Astra review

- **Starting SHA**: `a6ebb82d712746087aa1735198f5a3778d799fd7` (verified `git
  log -1` on this branch before any edit).
- **Final SHA**: recorded by the PR's own commit history (this document plus
  `build.log`; `firmware/bench-imu-01/README.md` gains one new section --
  see below).
- **Changed files**: `firmware/bench-imu-01/README.md` (new "Linux build"
  section appended); `docs/cloud-linux-firmware-build-2026-09-14/README.md`
  and `docs/cloud-linux-firmware-build-2026-09-14/build.log` (new).
  `firmware/bench-imu-01/Makefile` was **not** changed.
- **Commands/exits**: `sudo apt-get install -y gcc-arm-none-eabi
  binutils-arm-none-eabi` (exit 0); `make BUILDDIR=/tmp/rev5-linux-build/build`
  (exit 0, zero warnings).
- **Compiler/platform versions**: `arm-none-eabi-gcc (15:13.2.rel1-2)
  13.2.1 20231009`; GNU Binutils `2.42` (`objcopy`, `size`); Ubuntu 24.04.5
  LTS "noble", `x86_64` host.
- **Output hashes/sizes**: see the table in section 3 above.
- **Remaining limitations**: no physical board exists to flash or validate
  against; only static build/section-fit is confirmed, not runtime
  behavior; build outputs and log retained only in this session's scratch
  path per the task's storage constraint (a copy of `build.log` is included
  in this doc folder as the reproducibility receipt, containing only
  compiler invocation lines, no binary content).
- **User choice needed**: none -- no compilation defect was found, so no
  code change was required beyond this documentation addition.
