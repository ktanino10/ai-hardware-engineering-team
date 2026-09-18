# N8R8 offline evaluation source profile

[Public guide](../../../../docs/rev5-public-release/software.md) |
[日本語](../../../../docs/rev5-public-release/software.ja.md)

**NOT_FOR_FLASH / NOT EXECUTED ON HARDWARE / NOT FORMAL MODULE ADOPTION**

`rev5-n8r8-eval-m1` is an opt-in ESP-IDF project for evaluating the
ESP32-S3-DevKitC-1-N8R8 / ESP32-S3-WROOM-1-N8R8 candidate. Its CMake,
source contract, defaults, profile, measurement C/component, complete generated
pin header and vendor files are unchanged from
`3db7ea5e74bfaf7c286383d6ee29926f347a2297`.
This README is a derived public guide, not a replay of the author's build.

`EXTRA_COMPONENT_DIRS` reuses `../../measurement/main`; no acquisition C fork,
macro guard override, one-sensor adaptation, protocol or baseline pin change
is introduced. The original component's `-Wall -Wextra -Werror` remains.
`source-contract.cmake` binds eleven exact inputs. Image project/version are
`rev5_n8r8_evaluation` / `n8r8-eval-rev5-m1`; raw records retain `REV5B1` /
`rev5-m1` and cannot identify a physical module suffix.

The frozen profile selects 8 MB DIO/40 MHz flash and leaves PSRAM disabled;
the candidate's documented 8 MB Octal PSRAM is a separate physical
specification, not a build or device observation here. The manufacturer
metadata and inherited Evidence IDs are bound in
[source notes](../../../../docs/rev5-public-release/software-source-notes.json).
AMR, ROC and typical electrical characteristics are not inferred from build settings.

**GPIO35/36/37 remain reserved even with PSRAM disabled.** The eleven pins used
by this measurement application are disjoint, but the unchanged full Rev5
header assigns those three GPIOs to driver FG. Full Rev5 substitution is
**NOT_SUPPORTED**. Six-sensor raw register diagnostics are not synchronized
full-rate capture, calibrated SI, sensor fusion or control.

## Source tests without ESP-IDF

Use Python 3.9+ and an existing CMake 3.16+ from the repository root:

```sh
cmake --version
REV5_EVAL_CMAKE="$(command -v cmake)" \
REV5_EVAL_TEST_SCRATCH="$(mktemp -d)" \
  python3 -B firmware/bench-imu-01-rev5/evaluation/n8r8/tests/test_profile.py -v
```

All five tests run; there is no missing-tool skip. The unchanged dynamic test
executes only `cmake -P source-contract.cmake` against scratch copies and
checks rejection of modified application, header and component-registration
bytes. It does not configure an SDK, compile firmware or open a device.

Only the original test's XML filename was changed for public portability.
[reference/u201-pin-reference.xml](reference/u201-pin-reference.xml) is a
**derived software-test reference**, not the original native netlist: exact
attributes from eleven measurement nodes and three conflicting FG nodes,
with unrelated circuitry and the original local source path omitted.
Original hashes and the projection method are recorded; no native CAD runs
or hardware design changes are part of this export.

## Historical records and build limits

The completed independent review accepted source/profile scope and ran four
tests. Its fifth CMake test was **NOT_RUN** because the reviewer lacked CMake.
SDK/build/ELF/BIN checks were excluded. See the
[unchanged-scope review summary](../../../../docs/rev5-public-release/software-review.json)
and [new publisher/CI results](../../../../docs/rev5-public-release/software-checks.json).
Later CMake execution is not an amended independent verdict or a firmware build.

The author previously reported an offline build; no raw build receipt, SDK,
tool installation, ELF/BIN or flash artifact is included or independently
re-executed here. A separate build needs official ESP-IDF v5.5.2 commit
`30aaf64524299d3bde422ca9a2848090d1bc5d0f` and matching tools.
The profile's original comparison/fix-receipt paths and historical review
field remain as source metadata, not public runtime dependencies. The exact
source guards remain active; no nonexistent source-state claim is substituted.

Shipping revision, memory population, bridge/routing/fuses, power behavior,
six-sensor bus integrity, clocks, current, thermal behavior, stock and price
remain UNKNOWN. No device enumeration, serial, USB, monitor, JTAG, flash,
wiring, power or purchase is authorized. All NO-GO/3C8H/REQ409/strict-pro/
39UNKNOWN, P1/C1/D1, sidecar/ICD/control and human/physical holds persist;
original44=2closed42unfinished.
