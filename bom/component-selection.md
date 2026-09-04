# Component Selection

Produced by `.github/skills/component-selection/SKILL.md`. One section per
part-level need. Compare **at least 3 candidates** when feasible; if fewer,
state why explicitly.

## MCU

- **Driving requirement(s)**: REQ-001 (≥100 Hz IMU ODR forwarding), REQ-002/107
  (hardware debug/programming interface), REQ-101 (USB 5 V input, 4.75–5.25 V),
  REQ-102 (single 3.3 V logic rail), REQ-103 (≤300 mA @ 3.3 V system budget —
  MCU is one load among several), REQ-104 (I2C or SPI to IMU), REQ-105 (USB
  power-only, no data/enumeration used), REQ-106 (4-pin UART header for host
  comms), REQ-006 (no wireless functionality actually implemented even if
  silicon has it), REQ-201 (0–40 °C ambient), REQ-301/302 (single 2-layer PCB,
  ≤60×40 mm target), REQ-501 (whole-board BOM ≤~$15 USD, soft).
- **Constraints**: single 3.3 V rail (no level-shifter budget); small-batch/
  hand-assembly-plausible package strongly preferred; low-volume pricing
  (qty 1 / qty 100); no wireless functionality to be used even if present on
  the silicon.

### Candidate Comparison

*(4 candidates compared — exceeds the ≥3 minimum, no sole-source
justification needed.)*

| Parameter | Candidate A — Raspberry Pi RP2040 | Candidate B — STMicroelectronics STM32G031K8T6 | Candidate C — Espressif ESP32-C3 | Candidate D — Nordic Semiconductor nRF52840 |
|---|---|---|---|---|
| Manufacturer | Raspberry Pi Ltd | STMicroelectronics | Espressif Systems | Nordic Semiconductor ASA |
| Part Number | RP2040 (QFN-56 bare die; practical form is the Raspberry Pi Pico module) | STM32G031K8T6 (LQFP-32) | ESP32-C3 (QFN-32-EP, base/bare-die SKU) | NRF52840-QIAA-R (aQFN-73) |
| Core / architecture | Dual-core Arm Cortex-M0+, up to 133 MHz [DS-MCU-004] | Arm Cortex-M0+, up to 64 MHz [DS-MCU-014] | Single-core RISC-V (RV32IMC), up to 160 MHz [DS-MCU-024] | Arm Cortex-M4F (FPU), up to 64 MHz, + separate BLE/802.15.4 radio co-processor [DS-MCU-039] |
| Supply Voltage — Absolute Maximum Rating | IOVDD −0.3 to +3.63 V [DS-MCU-001] | VDD 4.0 V (upper bound only — lower bound `UNKNOWN`, not independently re-confirmed) [DS-MCU-012] | VDD 3.6 V — **same value as ROC max, zero overshoot margin** [DS-MCU-022] | VDD −0.3 to +3.9 V [DS-MCU-033] |
| Supply Voltage — Recommended Operating Condition | IOVDD 1.8–3.3 V; DVDD (core) generated on-chip from IOVDD, nominal ~1.1 V, no external regulation needed [DS-MCU-002], [DS-MCU-003] | VDD 1.7–3.6 V [DS-MCU-013] | VDD 3.0–3.6 V, typical 3.3 V [DS-MCU-023] | VDD 1.7–3.6 V, nominal 3.0 V in datasheet; separate VDDH pin (2.5–5.5 V) exists for direct-USB power, unused in this design [DS-MCU-034], [DS-MCU-035] |
| Current Consumption (test condition) | ~5.1 mA @48 MHz / ~13.7 mA @133 MHz, both cores active, FFT from SRAM, IOVDD=3.3 V, ~25 °C — rail/domain figure flagged for re-verification before power-budget lock, does not change this recommendation [DS-MCU-004] | ~2.1 mA @16 MHz / ~6.4–10.2 mA @64 MHz, VDD=3.0 V, Ta=25 °C, code from Flash, peripherals disabled [DS-MCU-014] | ~20–30 mA CPU-active, radio off, @160 MHz/3.3 V/~25 °C; light sleep ~1.2 mA [DS-MCU-024] | ~52 µA/MHz CoreMark-from-flash, VDD=3.0 V, ~25 °C, DC-DC enabled → ≈3.3 mA @64 MHz [DS-MCU-039] |
| Package | QFN-56, 7×7 mm, 0.4 mm pitch, bare die — not hand-solder-practical; Pico module (castellated, ~21×51 mm) is the practical hand-solderable path but eats ~35% of the REQ-302 footprint target [DS-MCU-005] | LQFP-32, 7×7 mm, 0.8 mm pitch — hand-solderable, no BGA in family [DS-MCU-015] | QFN-32-EP, 5×5 mm, 0.45 mm pitch, exposed pad — reflow-only; ESP32-C3-MINI-1 module is castellated/hand-solderable (+$1–2) [DS-MCU-025] | aQFN-73, 7×7 mm, dual-row, 0.4 mm pitch — **no leaded/LQFP package exists in this family at all**; not practical for hand-soldering [DS-MCU-036] |
| On-chip memory / peripherals | Zero on-chip flash — **requires an external QSPI NOR flash IC** (extra BOM line + 6-pin routing); 264 KB SRAM; 2×I2C, 2×SPI, 2×UART, SWD debug, native USB 1.1 host+device (present, unused), 8×PIO [DS-MCU-006], [DS-MCU-007] | Fully self-contained: 64 KB Flash + 8 KB SRAM on-chip; 2×I2C (FM+, 1 Mbit/s), 2×SPI (32 Mbit/s), 2×UART (1 USART+1 LPUART), SWD+JTAG debug, no native USB [DS-MCU-016], [DS-MCU-017] | Base/bare SKU has no embedded flash (external SPI-NOR needed, or must deliberately choose an embedded-flash SKU e.g. ESP32-C3FH4); **exactly 1 general-purpose I2C controller (zero margin)**, 1–2×SPI, 2×UART, JTAG via GPIO or USB-Serial/JTAG bridge (debug-only, not general USB device) [DS-MCU-026], [DS-MCU-027], [DS-MCU-028] | Fully self-contained: 1 MB Flash + 256 KB RAM on-chip; 2×I2C(TWI), 3×SPI (incl. 1×QSPI), 2×UARTE, SWD only (no JTAG), native USB 2.0 FS device (present, unused) [DS-MCU-037], [DS-MCU-038] |
| Price @ Qty 1 / Qty 100 (USD) | DigiKey $2.10/$1.67; LCSC $0.993/$0.764 — bare chip only, excludes mandatory external flash IC [DS-MCU-008] | DigiKey $2.53–2.83; Mouser $2.83 (qty1) — cheapest **all-in** cost of the non-radio candidates once RP2040's/ESP32-C3's external flash is priced back in [DS-MCU-018] | Mouser/DigiKey $1.07; LCSC $1.23 (qty1) — base SKU; embedded-flash SKU price not independently pulled [DS-MCU-029] | Mouser $7.20; DigiKey $6.62 (qty1) — **3–6× the cost of the other 3**, driven entirely by an unused BLE/802.15.4 radio complex; could alone consume ~45% of the REQ-501 $15 soft target [DS-MCU-040] |
| Lifecycle / EOL status | Active — Raspberry Pi's own published commitment: production until at least January 2041 [DS-MCU-009] | Active — ST PCNs extending into 2025–2026 indicate ongoing production [DS-MCU-019] | Active, no EOL notice found [DS-MCU-030] | Active — Nordic's current flagship BLE/Thread/Zigbee/Matter part [DS-MCU-041] |
| Reference design available? | Y — Raspberry Pi Pico, official $4 dev board, SWD header, USB connector, castellated pads [DS-MCU-010] | Y — NUCLEO-G031K8, official ST eval board (~$13), onboard ST-LINK/V2 SWD debugger [DS-MCU-020] | Y — ESP32-C3-DevKitM-1/DevKitC-02 official boards; Seeed XIAO ESP32C3, SparkFun Pro Micro ESP32-C3 third-party [DS-MCU-031] | Y — nRF52840-DK (~$40–50, onboard J-Link SWD); nRF52840 Dongle (~$10) [DS-MCU-042] |
| SDK / sample code / docs ecosystem | Official C/C++ SDK (CMake), most-complete MicroPython port, CircuitPython, mature Arduino-Pico community core, Zephyr support; extremely large/active hobbyist community, excellent official docs [DS-MCU-011] | STM32CubeG0 official HAL/LL + STM32CubeIDE (free), STM32Duino Arduino core, PlatformIO, full Zephyr support (ST is a top-tier Zephyr contributor, 220+ boards); large, mature professional ecosystem [DS-MCU-021] | ESP-IDF (official, FreeRTOS-based, mature), Arduino-ESP32 (official), MicroPython, Zephyr support; extremely large IoT/maker community, but much of its size is radio/IoT-specific and not relevant to a non-radio board [DS-MCU-032] | nRF Connect SDK (Zephyr-based, official, mature), legacy nRF5 SDK, arduino-nRF5 community core, Adafruit Bluefruit line; Nordic is a primary Zephyr upstream contributor; strong professional/BLE community, thinner hobbyist/Arduino community than A/C [DS-MCU-043] |
| Known risks | Zero on-chip flash under any configuration is a real BOM/routing-complexity risk not present in the original research brief; the practical low-volume implementation path (the Pico module) trades footprint budget (REQ-302) for assembly safety. | STM32G031K8T6 VDD Absolute Maximum Rating's exact lower bound is `UNKNOWN` this pass (only the 4.0 V upper bound independently re-confirmed) — flag for Circuit Engineer's Phase 3 datasheet-verification pass, do not assume −0.3 V by convention. | Genuine peripheral-margin risk: exactly 1 general-purpose I2C bus with zero headroom for a future 2nd I2C device. Mandatory, easy-to-miss SKU decision (embedded-flash vs. base/bare die) must be made explicit at BOM-lock. | Flagged high-risk for cost and package fit specifically for this project: no hand-solderable package exists in the family at all, and its price alone could consume ~45% of the soft $15 whole-board BOM target, entirely to pay for a radio complex REQ-006 prohibits using. |

### Cross-check note — flagged discrepancy (not silently resolved)

A supplementary Component Engineer verification pass on RP2040 current
consumption surfaced a possible reading different from the original research
figure: the original figure (used above, DS-MCU-004, ~13.7 mA @133 MHz) is
the total drawn from the 3.3 V IOVDD input rail; a second independent pass
surfaced ~23–25 mA typical on the internal 1.1 V DVDD core domain alone
(a different, lower-voltage rail generated on-chip from IOVDD), with a
board-level "practical total" estimate of ~30–35 mA for a Pico board. These
are plausibly not contradictory (DVDD is stepped down on-chip from IOVDD, so
a ~25 mA load at 1.1 V could reasonably correspond to roughly ~10–13 mA drawn
from the 3.3 V input) but this reconciliation was **not independently
re-verified against the primary datasheet table this session** — it is the
Component Engineer's own plausibility reasoning, not a re-verified fact.
**Action requested**: Circuit Engineer should re-pull the exact IOVDD-input-
referenced row directly from RP2040 datasheet Table 627 (§5.5) before
finalizing `hardware/power-budget.md`. **Does not change this
recommendation**: even the higher end of the range (~35 mA) is ~11.7% of the
REQ-103 300 mA budget, comfortable regardless of which figure is exact.

### Recommendation

- **Recommended candidate**: **B — STMicroelectronics STM32G031K8T6** (LQFP-32).
- **Rationale** (success probability for *this* design, not peak spec):
  1. Fully satisfies every driving requirement with comfortable margin —
     2×I2C/2×SPI (REQ-104), 2×UART with one genuinely free (REQ-106), SWD
     debug matching REQ-107's own literal example (REQ-002/107) — no
     peripheral-margin risk at all, unlike Candidate C.
  2. Fully self-contained (64 KB flash + 8 KB SRAM on-chip) — the simplest
     BOM/routing story of the 4, directly supporting REQ-301/302 (single
     2-layer, ≤60×40 mm) and REQ-501 (~$15 BOM) by avoiding an entire extra
     component category (external flash IC) that both RP2040 and ESP32-C3's
     base SKU require.
  3. LQFP-32 is the most assembly-practical package of the 4 for a
     small-batch, hand-assembled first design cycle — no bare-die-vs-module
     trade-off (RP2040, ESP32-C3), no leaded-package-doesn't-exist problem
     (nRF52840).
  4. Widest AMR–ROC voltage margin of the 4 (4.0 V AMR vs. 3.6 V ROC
     ceiling) — most forgiving of real-world 3.3 V rail behavior from a
     USB-derived supply (REQ-101/102).
  5. No radio silicon at all — the cleanest possible fit to REQ-006, with
     zero "paid-for-but-unused" capability, unlike Candidates C and D.
  6. Mature, professional-grade ecosystem (STM32CubeIDE/HAL, Zephyr,
     STM32Duino, PlatformIO) with a cheap ($13), genuinely working official
     reference design (NUCLEO-G031K8) — de-risks bring-up for this
     repository's first-ever end-to-end design cycle.
  7. Mid-pack quoted price ($2.53–2.83 @qty1) is actually the cheapest
     **all-in ("subsystem") cost** of the non-radio candidates once RP2040's
     and (base-SKU) ESP32-C3's mandatory external flash IC is counted back
     in.
  8. Active lifecycle with ongoing ST PCN activity; mainstream ST
     General-Purpose family with a long track record of multi-decade
     support for this MCU class.
- **Trade-offs accepted**:
  - RP2040's larger hobbyist/maker mindshare, dual-core, and PIO peripheral —
    no requirement calls for bit-banged custom peripherals or dual-core
    parallelism, and a single Cortex-M0+ @64 MHz has wide margin against
    REQ-001's ≥100 Hz IMU sample-rate floor plus UART forwarding.
  - Any path to onboard Wi-Fi/BLE (only C/D have this) — explicitly
    acceptable: REQ-006 forbids using it this cycle, and any future wireless
    need is its own architecture decision / fresh HITL-gated cycle, not
    something to pre-solve by over-provisioning today's MCU choice.
  - RP2040's raw distributor-price floor on the bare chip — largely illusory
    once its mandatory external flash IC is priced in.
  - Slightly less "future-roadmap ecosystem breadth" than RP2040's
    MicroPython-level rapid-prototyping story — partially offset by STM32's
    own motor-control-oriented adjacent families being arguably a better fit
    for the roadmap's later motor-driver/attitude-control stages, though this
    is the Component Engineer's own judgment call, offered for the Hardware
    Lead/human to weigh, not asserted as settled.
- **Open `UNKNOWN`s**:
  1. STM32G031K8T6 VDD Absolute Maximum Rating's exact lower bound — only the
     4.0 V upper bound independently re-confirmed this session; re-confirm at
     Circuit Engineer's Phase 3 datasheet-verification stage, do not assume
     −0.3 V by convention.
  2. RP2040 current-consumption rail/domain ambiguity (see Cross-check note
     above) — resolve before `hardware/power-budget.md` is finalized.
  3. Live distributor stock quantities/lead times were not pulled for any of
     the 4 candidates this session (only listing/price-tier data, which
     confirms the part is actively sold, not real-time stock count) —
     recommend a live stock check immediately before BOM lock.
  4. ESP32-C3 embedded-flash SKU (e.g. ESP32-C3FH4) pricing not
     independently pulled — relevant only if overridden toward Candidate C.
  5. Exact decoupling-capacitor values/placement and crystal-vs-internal-RC
     clocking choice for STM32G031K8T6 are correctly deferred to the Circuit
     Engineer/schematic-design stage.

### Escalation flags

No candidate is disqualified outright — all 4 are electrically and
functionally viable. Flagged explicitly rather than silently omitted:
**nRF52840 (D)** — high-risk for cost and package fit for this specific
project (see Known risks). **ESP32-C3 (C)** — genuine peripheral-margin risk
(exactly 1 I2C) and a mandatory SKU decision that must not be left implicit.
**RP2040 (A)** — BOM/routing-complexity risk (zero on-chip flash under any
configuration).

**HITL gate**: the MCU is an architecture-defining component for this entire
board (`docs/architecture.md` §10). This recommendation is a *proposal*
only — Circuit Engineer must not begin schematic work until Chief Engineer
(human) approval is recorded below.

### Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Component Engineer | Component Engineer (AI agent) | 2026-08-30 | Proposed — STM32G031K8T6 |
| Hardware Lead | Hardware Lead (this session) | 2026-08-30 | Concur — recommend approval |
| Chief Engineer (Human) — required if architecture-defining/major component | Human Chief Engineer | 2026-08-30 | **Approved** — "Approve all three as recommended" (Checkpoint B, recorded via ask_user; independently re-confirmed after the worktree-restore incident, see `validation/change-log.md` ECO-001) |

---

### Rev 5 re-evaluation (3-axis/6-IMU/3-brake scale) — MCU switch recommended

> **Per REQ-508**, this section is an explicit, individual re-justification
> of whether the incumbent (STM32G031K8T6) should be carried forward
> unchanged at Rev 5's new scale — not a silent "it worked before"
> assumption. **Conclusion: it should NOT be carried forward.** This is
> **not** a JAXA-parts-copy decision (`requirements/requirements.md` §1c) —
> PSoC 5LP (the JAXA reference's own MCU) was never seriously considered;
> the candidates below are independently chosen modern parts evaluated on
> their own real 2026 merits.

- **Driving requirement(s)**: REQ-015 (3-axis PWM/speed-setpoint control —
  3 motor PWM channels + direction/enable GPIOs, ideally hardware-timer
  matched), REQ-016 (6-IMU sensor fusion — bus/pin budget, resolved below
  to need only **1 shared SPI bus + 6 CS lines**, not 3 independent I²C
  buses, per the IMU Rev 5 re-evaluation's own SDO/address finding), REQ-017
  (real-time closed-loop 3-axis PID — needs meaningfully more compute
  headroom than the incumbent's 64MHz Cortex-M0+), REQ-018 (3× momentum/
  saturation monitoring via timer input-capture, mirroring the existing
  1-axis FG-tach pattern), REQ-019 (3× brake control output — resolved
  below to need no new GPIO class, since the Rev 5 Brake re-evaluation's own
  primary recommendation reuses the existing motor driver's own BRAKE
  control line, not a separate coil driver), REQ-020 (wireless — Must for
  the jump/stand operating mode; native MCU wireless directly satisfies
  this without a separate BOM line), REQ-102 (single 3.3V logic rail,
  unchanged), REQ-507 (≤$450-800+ soft BOM ceiling — MCU cost is a small
  fraction of this budget, unlike Rev 1-4's much tighter ~$15 target).
- **Constraints**: must remain a real, currently-produced (2026), realistically-
  sourceable part — this project has twice been burned by picking parts
  with severe real availability problems (RP2040's own external-flash
  requirement; ICM-42688-P's 45-54 week lead time, both flagged in this
  file's own prior IMU/MCU comparisons) — real distributor stock/lifecycle
  checks are mandatory, not assumed from "it's popular."

#### Candidate Comparison

*(5 candidates compared, including the incumbent — exceeds the ≥3 minimum.)*

| Parameter | Candidate A — STM32G031K8T6 (incumbent) — ⚠ DISQUALIFIED | Candidate B — Espressif ESP32-S3 — ✅ RECOMMENDED | Candidate C — STMicroelectronics STM32F411CET6 | Candidate D — STMicroelectronics STM32H723ZG | Candidate E — Nordic nRF52840 |
|---|---|---|---|---|---|
| Core / clock | Cortex-M0+, 64MHz [DS-MCU-014] | Dual-core Xtensa LX7, 240MHz [DS-MCU-078] | Cortex-M4F, 100MHz [DS-MCU-086] | Cortex-M7 (DP-FPU), 550MHz [DS-MCU-092] | Cortex-M4F, 64MHz [DS-MCU-037] |
| On-chip flash/RAM | 64KB/8KB [DS-MCU-016] | Package-dependent (external QSPI flash + PSRAM typical for dev modules) [DS-MCU-079] | 512KB/128KB [DS-MCU-087] | 1MB/564KB [DS-MCU-093] | 1MB/256KB [DS-MCU-038] |
| I2C / SPI / UART | 2/2/2 [DS-MCU-017] | 2 I2C / 4 SPI (2 typically reserved for flash/PSRAM, 2 general-purpose) / 3 UART [DS-MCU-080] | 3/5/3 [DS-MCU-088] | up to 5/6/6 [DS-MCU-094] | 2 TWI/3 (incl. QSPI)/2 UARTE [DS-MCU-039] |
| Timers/PWM/capture | 11 timers, 1 advanced motor timer [DS-MCU-017] | 2× MCPWM (motor-control-specific PWM peripheral), LEDC 8-ch PWM, pulse counter, 4 general timers [DS-MCU-081] | Up to 11 timers [DS-MCU-089] | 24 timers (17×16-bit incl. 5 Stop-mode-capable, 4×32-bit, 2 watchdogs, 1 SysTick) [DS-MCU-095] | GPIO-mux'd PWM via PPI/timers, exact motor-control-specific peripheral count not confirmed this session |
| Built-in wireless | No | **Wi-Fi 802.11 b/g/n + Bluetooth LE 5 (incl. Long Range/Coded PHY)** [DS-MCU-082] | No | No | BLE 5/Thread/Zigbee/802.15.4 (no Wi-Fi) [DS-MCU-039] |
| Package | LQFP-32, hand-solderable [DS-MCU-015] | QFN-56 (module variants e.g. ESP32-S3-WROOM are hand-solderable) [DS-MCU-083] | UFQFPN-48; no LQFP48 confirmed for this exact SKU this session | LQFP-144-class, larger [DS-MCU-096] | aQFN-73/QFN-48/WLCSP — no leaded package in this family [DS-MCU-040] |
| 3.3V rail compatibility | 1.7-3.6V [DS-MCU-013] | 3.0-3.6V operating range [DS-MCU-084] | 1.7-3.6V [DS-MCU-090] | 1.62-3.6V [DS-MCU-097] | 1.7-3.6V [DS-MCU-034] |
| Lifecycle / EOL | Active [DS-MCU-019] | Active [DS-MCU-085] | Active — DigiKey-listed for the closely-related CEU6 SKU, not independently re-confirmed for the exact CET6 ordering code this session [DS-MCU-091] | Active/Production per most recent datasheet revision found [DS-MCU-098] | Active [DS-MCU-041] |
| Reference design | NUCLEO-G031K8 [DS-MCU-020] | Espressif ESP32-S3-DevKitC/DevKitM official boards; extensive third-party modules | ST F4 Discovery/Nucleo ecosystem | ST H7 Nucleo/eval ecosystem | nRF52840-DK, nRF52840 Dongle [DS-MCU-042] |
| Ecosystem | STM32CubeIDE/HAL, Zephyr, PlatformIO [DS-MCU-021] | ESP-IDF (official, FreeRTOS-based), Arduino-ESP32, MicroPython, Zephyr — very large community | STM32CubeIDE/HAL, Zephyr, PlatformIO | STM32CubeIDE/HAL, Zephyr, PlatformIO | nRF Connect SDK/Zephyr, thinner hobbyist community than ESP32 [DS-MCU-043] |
| Price/pricing note | ~$2.53-2.83 qty1 [DS-MCU-018] | **Live 2026 qty1/qty100 distributor pricing UNKNOWN this session** — automated distributor fetches were blocked; prior-generation ESP32/ESP32-C3 parts in this project's own history have been in the low-single-digit-dollar range, offered as context only, not as this specific SKU's confirmed price | **Live 2026 pricing UNKNOWN this session** | **Live 2026 pricing UNKNOWN this session** | ~$6.62-7.20 qty1 (prior repo data, not re-verified live this session) [DS-MCU-040] |
| Known risks | **DISQUALIFIED**: only 2 I2C/2 SPI, 8KB SRAM, 64MHz M0+ — insufficient compute/peripheral margin for REQ-016/017 even with the IMU's SPI-bus resolution; no wireless | Exact orderable module SKU (flash/PSRAM/package tradeoff) not yet narrowed — a Circuit Design-stage decision, not resolved here. Live pricing/stock genuinely unconfirmed this session (flagged honestly, not glossed over) | Real, credible fallback if wireless-via-MCU is rejected — but needs an external wireless module (adds a REQ-020 BOM line), and live 2026 pricing/stock unconfirmed this session | Likely overkill for this project's actual control-loop demands; larger/costlier package; live pricing/stock unconfirmed this session | No leaded package in family (a real assembly-practicality concern this project's own Rev 1-4 MCU comparison already flagged for this same part); no Wi-Fi if that's ever wanted; higher cost than ESP32-S3 for weaker peripheral count |

#### Success-probability ranking

| Rank | Candidate | Verdict |
|---|---|---|
| 1 | **ESP32-S3 (B)** | Best overall system fit: dual-core 240MHz gives real REQ-017 control-loop headroom, MCPWM peripheral is purpose-built for motor control (REQ-015), built-in Wi-Fi+BLE directly satisfies REQ-020 with zero extra wireless BOM line, and the IMU Rev 5 finding (BMI270 over SPI, 1 bus + 6 CS) removes the "only 2 I2C" concern that would otherwise be a real weakness. Mature ecosystem (ESP-IDF, Zephyr, huge community). |
| 2 | **STM32F411CET6 (C)** | Best fallback if the team prefers ST toolchain continuity over an architecture change, or if ESP32-S3's real-world stock/pricing turns out unfavorable at Circuit Design time — needs an external wireless module (see Wireless section) to satisfy REQ-020. |
| 3 (not recommended, real option) | **STM32H723ZG (D)** | Technically the strongest margin of all 5, but likely disproportionate cost/package complexity for this project's actual control-loop demands — a legitimate escalation path only if REQ-017's real control-loop rate ends up demanding it. |
| 4 (not recommended) | **nRF52840 (E)** | BLE-only (no Wi-Fi) with weaker peripheral count than ESP32-S3 at a higher cost; no hand-solderable package — this project's own Rev 1-4 MCU comparison already flagged this exact weakness for this exact part. |
| 5 (disqualified) | **STM32G031K8T6 (A, incumbent)** | Insufficient I2C/SPI/SRAM/clock margin for the new 3-axis/6-IMU/wireless scope — REQ-508's required re-justification concludes this part cannot be carried forward. |

#### Recommendation

- **Recommended candidate**: **B — Espressif ESP32-S3**, replacing the
  incumbent STM32G031K8T6.
- **Rationale**:
  1. Directly satisfies REQ-020 (wireless, now Must) with zero additional
     wireless-module BOM line — the single biggest simplification versus
     every other candidate.
  2. MCPWM (Motor Control PWM) is a peripheral class purpose-built for
     REQ-015's 3-axis motor control — not a generic timer repurposed for
     PWM.
  3. Dual-core 240MHz gives genuine headroom for REQ-017's real-time
     closed-loop 3-axis attitude control, which the incumbent's single
     64MHz Cortex-M0+ almost certainly could not sustain alongside 6-IMU
     sensor fusion.
  4. The IMU Rev 5 re-evaluation's own finding (BMI270 ×6 over a single
     shared SPI bus + 6 CS lines, not 3 independent I2C buses) removes
     what would otherwise be ESP32-S3's one real weakness (only 2 native
     I2C controllers) — the two Rev 5 findings interlock favorably.
  5. Mature, very large ecosystem (ESP-IDF, Arduino-ESP32, Zephyf support,
     extensive real-world motor-control and IMU-fusion prior art).
- **Trade-offs accepted**:
  - Giving up STM32 toolchain continuity (this project's Rev 1-4 firmware
    is STM32CubeIDE/HAL-based) — a real, non-trivial re-platforming cost
    for the Firmware Engineer's next phase, explicitly disclosed here, not
    glossed over.
  - Live 2026 distributor pricing/stock could not be independently
    confirmed this session (automated fetches were blocked) — flagged as
    an open UNKNOWN, not assumed favorable.
  - Exact orderable module SKU (onboard flash/PSRAM size, package) is not
    narrowed here — a Circuit Design-stage decision.
- **Open `UNKNOWN`s**:
  1. Live 2026 qty-1/qty-100 pricing and real distributor stock for
     ESP32-S3 (and all other non-incumbent candidates) — not independently
     confirmed this session; re-verify before BOM lock.
  2. Exact ESP32-S3 module SKU (flash/PSRAM size, package variant) — a
     Circuit Design-stage decision.
  3. Exact GPIO/pin-mux sufficiency for the full Rev 5 pin budget (3×motor
     PWM + 3×brake control + 3×tach capture + 1 shared SPI + 6 CS + UART +
     debug) against ESP32-S3's real pin count — needs a full pin-planning
     pass at Circuit Design, not resolved here.
  4. STM32H723ZG's real necessity — only relevant if REQ-017's actual
     control-loop rate, once characterized, exceeds ESP32-S3's real
     headroom (an escalation path, not assumed needed).

#### Escalation flags

1. **Architecture-defining decision — requires Hardware Lead + human Chief
   Engineer approval** (`docs/architecture.md` §10), same as the original
   Rev 1 MCU decision. This is a platform/toolchain change (STM32→
   Espressif/ESP-IDF), which is a materially larger decision than a
   same-family part swap.
2. **Firmware re-platforming cost is real and should be weighed explicitly**
   — the existing Rev 1-4 firmware (`firmware/bench-imu-01/`) is
   STM32CubeIDE/HAL-based; switching to ESP32-S3 means the Firmware
   Engineer's next phase starts from a different toolchain, not an
   incremental extension. Flagged for the human's own weighing, not
   decided here.
3. **Live pricing/stock genuinely unconfirmed this session** for every
   non-incumbent candidate — re-verify before BOM lock, per this project's
   own Source-of-Truth discipline (do not assume favorable pricing/stock
   just because a part is popular).

#### Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Component Engineer | Component Engineer (AI agent, via parallel research sub-agent) | 2026-09-04 | Proposed — switch to ESP32-S3, disqualify incumbent STM32G031K8T6 per REQ-508 |
| Hardware Lead | Hardware Lead (this session) | 2026-09-04 | Concur — recommend approval, with the firmware re-platforming cost and live-pricing UNKNOWNs explicitly flagged for human weighing |
| Chief Engineer (Human) — required, architecture-defining component (`docs/architecture.md` §10) | Human Chief Engineer | 2026-09-04 | **Approved** — "確定" (Kyosuke's own direct plain-text reply, turn 616, `session_store_sql` session `7fab99ef-5578-4d79-a9c2-b24dbcfe93be`, `2026-09-04T16:00:16.240Z`), in direct reply to a specific question naming this exact recommendation by name (turn 614, `2026-09-04T15:54:20.062Z`) — both turns independently re-verified by this session directly against the raw turn history, not accepted from a relayed summary alone. Approves the ESP32-S3 MCU switch (over the incumbent STM32G031K8T6) as recommended. |

---

## IMU (3-axis accelerometer + 3-axis gyroscope)

- **Driving requirement(s)**: REQ-001 (≥100 Hz ODR, 3-axis accel + 3-axis
  gyro), REQ-102 (single 3.3 V logic rail — both VDD and VDDIO), REQ-103
  (≤300 mA total system current budget — IMU must be a small fraction),
  REQ-104 (I2C or SPI), REQ-201 (0–40 °C ambient), REQ-501 (~$15 soft
  whole-board BOM target — IMU should be a modest fraction).
- **Constraints**: single 3.3 V rail with no separate low-voltage domain
  available for a digital-IO supply below ~3 V (rules out any candidate
  whose VDDIO ceiling is below ~3.3 V); 14-pin LGA-class package footprint
  strongly preferred for board-area consistency with the 3 compliant
  candidates; low-volume/prototype-quantity pricing basis; part must be
  realistically sourceable within the project's schedule — not merely "in
  production" on paper.

### Candidate comparison

*(4 candidates compared — exceeds the ≥3 minimum; Candidate D is included
specifically as an architecture-mismatch comparison point, not because it
was ever a live contender once its VDDIO limitation was confirmed.)*

| Parameter | Candidate A — Bosch Sensortec BMI270 | Candidate B — TDK InvenSense ICM-42688-P | Candidate C — STMicroelectronics LSM6DSOX | Candidate D — TDK InvenSense ICM-20948 *(comparison only — DISQUALIFIED)* |
|---|---|---|---|---|
| **Manufacturer** | Bosch Sensortec | TDK InvenSense | STMicroelectronics | TDK InvenSense |
| **Part Number** | BMI270 | ICM-42688-P | LSM6DSOX | ICM-20948 |
| **Type / Axes** | 6-axis (accel+gyro) | 6-axis (accel+gyro) | 6-axis (accel+gyro) | 9-axis (adds magnetometer) — **not a REQ-001 requirement** |
| **Accelerometer FSR** | ±2 to ±16 g, programmable [DS-IMU-001] | ±2 to ±16 g, programmable [DS-IMU-018] | ±2 to ±16 g, programmable [DS-IMU-035] | `UNKNOWN` — not confirmed this session [DS-IMU-052] |
| **Gyroscope FSR** | ±125 to ±2000 dps, 5 ranges [DS-IMU-002] | ±15.6 to ±2000 dps, 8 ranges — finest granularity [DS-IMU-019] | ±125 to ±2000 dps, 5 ranges [DS-IMU-036] | ±250 to ±2000 dps, 4 ranges [DS-IMU-053] |
| **VDD — Recommended Operating Condition** | 1.71–3.6 V [DS-IMU-003] | 1.71–3.6 V [DS-IMU-020] | 1.71–3.6 V [DS-IMU-037] | 1.71–3.6 V [DS-IMU-055] |
| **VDD — Absolute Maximum Rating** | −0.3 to +3.6 V [DS-IMU-004] | 3.6 V (same as ROC max) [DS-IMU-021] | 3.6 V (same as ROC max) [DS-IMU-038] | `UNKNOWN` exact ceiling beyond the 1.71–3.6 V ROC [DS-IMU-056] |
| **VDDIO — Recommended Operating Condition** | 1.2–3.6 V — broadest floor of the 4 [DS-IMU-005] | 1.71–3.6 V (same as VDD) [DS-IMU-022] | 1.62–3.6 V [DS-IMU-039] | ⚠️ **1.71–1.95 V ONLY — INCOMPATIBLE with REQ-102's single 3.3 V rail** without added level-shifting hardware [DS-IMU-057] |
| **VDDIO — Absolute Maximum Rating** | No separate ceiling below 3.6 V [DS-IMU-006] | No separate ceiling below 3.6 V [DS-IMU-023] | No separate ceiling below 3.6 V [DS-IMU-040] | ⚠️ **2.0 V** — a nominal 3.3 V rail exceeds this by 1.3 V (65% over Absolute Maximum); datasheet warns of **permanent damage** [DS-IMU-058] |
| **Operating Temperature Range** | −40 °C to +85 °C [DS-IMU-070] | −40 °C to +85 °C [DS-IMU-071] | −40 °C to +85 °C [DS-IMU-072] | Likely −40 °C to +85 °C but not independently confirmed for this specific part — lower confidence [DS-IMU-073] |
| **Digital Interface — I2C** | ≤1 MHz (FM+) [DS-IMU-007] | ≤1 MHz (FM+) [DS-IMU-024] | ≤400 kHz (FM) — slowest of the 4, still far more than sufficient [DS-IMU-041] | ≤400 kHz (FM) [DS-IMU-059] |
| **Digital Interface — SPI** | ≤10 MHz, 3-/4-wire [DS-IMU-008] | ≤24 MHz, Mode 0/3 — fastest of the 4 [DS-IMU-025] | ≤10 MHz, 3-/4-wire [DS-IMU-042] | ≤7 MHz [DS-IMU-060] |
| **Max ODR — Accel / Gyro** | 1600 Hz / 6400 Hz [DS-IMU-009] | 32,000 Hz / 32,000 Hz — highest of the 4 [DS-IMU-026] | 6660 Hz / 6660 Hz [DS-IMU-043] | 4500 Hz / 9000 Hz (+ Mag 100 Hz) [DS-IMU-061] |
| **Typical Current Consumption** | 685 µA, full-performance mode, both axes active [DS-IMU-010] | 0.88 mA, Low-Noise mode, both axes active, VDD=1.8 V [DS-IMU-027] | 0.55 mA (IddHP), combo High-Performance mode; exact ODR test condition `UNKNOWN` [DS-IMU-044] | 3.11 mA full 9-axis mode; ~68.9 µA accel-only [DS-IMU-062] |
| **Package** | 14-pin LGA, 2.5×3.0×0.83 mm [DS-IMU-011] | 14-pin LGA, 2.5×3.0×0.91 mm [DS-IMU-028] | 14-pin LGA, 2.5×3.0×0.83 mm [DS-IMU-045] | 24-pin QFN, 3.0×3.0×1.0 mm — larger footprint, more pins [DS-IMU-063] |
| **Price @ Qty 1 / Qty 100 (USD)** | $4.23/$3.17 (DigiKey) [DS-IMU-012]; $3.71/$3.11 (Mouser) [DS-IMU-013] — cheapest of the 4 | $4.91/$3.70 (DigiKey) [DS-IMU-029]; $5.43/$3.70 (Mouser) [DS-IMU-030] — list price only, part cannot currently be bought | $5.30/~$3.99 est. (DigiKey) [DS-IMU-046]; ~$4.84/~$3.64 est. (Mouser) [DS-IMU-047] | ~$8.25/~$6.30, limited last-buy stock (DigiKey) [DS-IMU-064]; obsolete/no standard pricing (Mouser) [DS-IMU-065] — most expensive of the 4 |
| **Lifecycle / EOL status** | Active, no EOL/NRND [DS-IMU-014] | Active/in-production per distributor listings [DS-IMU-031] | Active; used in the official Arduino Nano RP2040 Connect [DS-IMU-048] | ⚠️ **OBSOLETE / NRND** — formally marked Obsolete at both DigiKey and Mouser, last-buy inventory only [DS-IMU-066] |
| **Availability (stock / lead time)** | High stock — 60,000+ units, no lead-time concern [DS-IMU-015] | ⚠️ **ZERO stock at both DigiKey and Mouser**, 45–54-week lead times pointing to mid/late 2027 [DS-IMU-032] | Stock on hand at DigiKey as of mid-2024; possible 24-week lead times at some inventory levels — real but materially smaller risk than B's [DS-IMU-049] | Last-buy/EOL inventory only [DS-IMU-067] |
| **Reference design available?** | Y — SparkFun 6DoF IMU Breakout - BMI270 (Qwiic, 1.8 V and 3.3 V) [DS-IMU-016] | Y (eval-board only) — TDK QCIOT-ICM42688P; community open-hardware breakouts; no confirmed SparkFun/Adafruit breakout [DS-IMU-033] | Y — Adafruit LSM6DSOX 6 DoF Breakout ($11.95, STEMMA QT); onboard official Arduino Nano RP2040 Connect [DS-IMU-050] | Y (legacy/secondary-market only) [DS-IMU-068] |
| **SDK / sample code / docs ecosystem** | Good — official Bosch C driver (BSD-3-Clause, GitHub, MCU-agnostic) + SparkFun Arduino library [DS-IMU-017] | Fair — community-only Arduino libraries, no first-party library found [DS-IMU-034] | **Best of the 4** — 4 distinct well-maintained Arduino libraries incl. official Arduino-brand library + official ST STM32Cube driver [DS-IMU-051] | Fair, declining — community libraries exist but investment winding down given EOL [DS-IMU-069] |
| **Known risks** | None material for this design; broadest VDDIO floor (1.2 V) gives the most future headroom. | **Severe, real supply-chain risk** — confirmed zero stock at 2 major distributors, 45–54-week lead times into mid/late 2027. Electrically excellent and fully 3.3 V-compatible, but **not realistically sourceable on this project's timeline.** | Minor: some qty-100 pricing figures are estimates; a prior note flagged possible 24-week lead times at some inventory levels — worth a fresh stock check before BOM lock, nowhere near Candidate B's severity. | **Disqualifying, on 3 independent grounds**: (1) VDDIO 1.71–1.95 V ROC / 2.0 V AMR incompatible with REQ-102's single 3.3 V rail without added level-shifting hardware; (2) formally Obsolete/NRND at both major distributors; (3) unrequested 9-axis magnetometer adds cost/complexity with zero REQ-001 benefit. |

**Note**: all 4 candidates clear REQ-001's ≥100 Hz ODR floor and REQ-103's
current budget with very large margin — these were never differentiators.
The real differentiators were VDDIO/rail compatibility (REQ-102),
lifecycle/availability, cost, and ecosystem maturity.

### Success-probability ranking

| Rank | Candidate | Verdict |
|---|---|---|
| 1 | **BMI270 (A)** | Best overall success probability: fully compliant, cheapest, cleanest/freshest confirmed stock, official cross-platform driver, broadest VDDIO floor. No risk flags. |
| 2 | **LSM6DSOX (C)** | Equally requirement-compliant; most mature multi-library ecosystem and proven in a shipping Arduino product; slightly higher cost and a slower (but still sufficient) I2C bus; stock data slightly older/less clean than A's. Designated fallback / second-source. |
| 3 (not recommended) | **ICM-42688-P (B)** | Best raw electrical specs of the 4, but confirmed zero stock at both DigiKey and Mouser, 45–54-week lead times pointing to mid/late 2027 availability — a severe, real, demand-driven shortage, not a footnote. |
| 4 (rejected) | **ICM-20948 (D)** | VDDIO incompatible with the single 3.3 V rail; formally Obsolete/NRND; unrequested 9-axis magnetometer adds cost/complexity for no REQ-001 benefit. Not a viable candidate for a new design. |

### Recommendation

- **Recommended candidate**: **A — Bosch Sensortec BMI270**, with **C —
  STMicroelectronics LSM6DSOX** explicitly designated as the fallback /
  second-source candidate.
- **Rationale**: BMI270 satisfies every driving requirement (REQ-001, 102,
  103, 104, 201) with comfortable margin, is the cheapest of the 4
  candidates, has the cleanest and most current stock confirmation
  (60,000+ units, no caveats), and its ecosystem centers on an official
  Bosch-maintained, BSD-3-Clause, MCU-agnostic C driver — not tied to any one
  MCU family, which matters since MCU selection happened in a parallel,
  independent Component Engineer call this same cycle. Its VDDIO floor
  (1.2 V) is also the broadest of the 4, giving the most headroom if a
  future revision ever needed a lower logic-level domain. LSM6DSOX is an
  extremely close second — named as the explicit fallback so the Hardware
  Lead has a pre-vetted, fully-compliant second source if BMI270's currently
  healthy stock picture ever changes before layout, a prudent practice given
  how badly two of the other three candidates in this exact comparison were
  bitten by supply issues.
- **Trade-offs accepted**:
  - Giving up ICM-42688-P's substantially higher max ODR (32 kHz vs.
    1.6/6.4 kHz), finer gyro FSR granularity, and faster SPI — none of which
    REQ-001 (≥100 Hz) requires; a deliberate peak-spec-for-success-
    probability trade in exchange for a part that can actually be bought and
    delivered on a normal schedule instead of ~a year from now.
  - Giving up LSM6DSOX's broader multi-library ecosystem maturity and real-
    product track record in exchange for BMI270's slightly lower price and
    cleaner/fresher stock data — a close call, which is exactly why LSM6DSOX
    is retained as the named fallback rather than dropped.
  - BMI270's I2C is faster than LSM6DSOX's (1 MHz vs. 400 kHz) — a minor
    incidental win, not a driver of the recommendation.
- **Open `UNKNOWN`s** (carried forward explicitly):
  1. ICM-20948 accelerometer FSR and VDD Absolute Maximum Rating exact
     ceiling — genuinely unconfirmed; moot given disqualification.
  2. ICM-20948's VDDIO Absolute Maximum Rating of 2.0 V is sourced from a
     single datasheet-aggregator page (not independently cross-checked
     against a second raw-datasheet mirror) — carries slightly lower
     individual confidence than the directly manufacturer-quoted 1.71–1.95 V
     Recommended Operating Condition figure, though both agree on the same
     disqualifying conclusion.
  3. LSM6DSOX's typical current-consumption figure (0.55 mA) has its
     Vdd/temperature test condition confirmed (1.8 V/25 °C) but not its ODR
     — genuinely unresolved.
  4. LSM6DSOX qty-100 pricing at both DigiKey and Mouser are estimates, not
     confirmed break prices — worth a fresh distributor check before BOM
     lock.
  5. LSM6DSOX current stock levels are a mid-2024-dated data point, not
     re-checked this session — a fresh stock check is recommended before
     final BOM lock even though no red flag was found.

### Escalation flags

1. **Candidate D (ICM-20948) is formally recommended for rejection**, on
   three independent, compounding grounds: VDDIO incompatibility (confirmed
   via a direct manufacturer-datasheet quote, cross-checked across 3
   independent sources), formal Obsolete/NRND status, and an unrequested
   9-axis magnetometer.
2. **Candidate B (ICM-42688-P) carries a severe, real availability risk**
   weighed heavily against recommending it as primary despite the best raw
   electrical specs in the comparison — confirmed zero stock, 45–54-week
   lead times into mid/late 2027.

**HITL gate**: IMU selection is a major/architecture-defining component
decision per `docs/architecture.md` §10 — Chief Engineer (human) sign-off is
required before the Circuit Engineer begins schematic work against it.

### Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Component Engineer | Component Engineer (AI agent) | 2026-08-30 | Proposed — BMI270 (fallback: LSM6DSOX) |
| Hardware Lead | Hardware Lead (this session) | 2026-08-30 | Concur — recommend approval |
| Chief Engineer (Human) — required if architecture-defining/major component | Human Chief Engineer | 2026-08-30 | **Approved** — "Approve all three as recommended" (Checkpoint B, recorded via ask_user; independently re-confirmed after the worktree-restore incident, see `validation/change-log.md` ECO-001) |

---

### Rev 5 re-evaluation (6-IMU, 3-axis scale) — BMI270 reused ×6, architecture changed to SPI

> **Per REQ-508**, this is an explicit, individual re-justification of
> whether BMI270 (already validated in Rev 1-4, with an official
> BSD-3-Clause driver already integrated into `firmware/bench-imu-01/`)
> should be used ×6, rather than switching to MPU-6050 (the JAXA
> reference's own part) without a real reason
> (`requirements/requirements.md` §1c item 2). **Conclusion: reuse BMI270
> ×6, but change the wiring architecture from I2C to SPI** — a materially
> different outcome than "just use the same part again unchanged," driven
> by a real datasheet finding below.

- **Driving requirement(s)**: REQ-016 (3-axis attitude estimation via
  sensor fusion across 6 IMUs, 2 per axis, "using as many I²C buses as the
  finally-selected IMU part's own address/pin constraints require" — this
  section resolves that open constraint), REQ-508 (individual
  re-justification, not silent reuse).
- **Constraints**: the JAXA reference design's own 3-separate-I2C-bus
  architecture exists specifically because MPU-6050 has only a 2-address
  I2C limit (AD0 pin) — this section must independently verify whether
  BMI270 shares that exact constraint, not assume it does or doesn't
  merely because both are 6-axis IMUs.

#### Critical finding: BMI270 DOES share MPU-6050's 2-address I2C limit — but supports SPI

Re-confirmed directly from this repository's own already-registered
Evidence IDs (not re-derived from scratch, since this project already
extracted this exact fact during Rev 1-4 Circuit Design — **DS-IMU-076**:
"BMI270 SDO pin sets the LSB of the 7-bit I2C device address: SDO tied to
GND → address 0x68; SDO tied to VDDIO → address 0x69"), cross-checked
against the official Bosch driver source itself (**DS-IMU-078**: the same
two address constants, `BMI2_I2C_PRIM_ADDR`/`BMI2_I2C_SEC_ADDR`, 0x68/0x69).
**BMI270 has exactly 2 selectable I2C addresses — identical in kind to
MPU-6050's own AD0-pin 2-address scheme.** A pure-I2C architecture for 6
BMI270 devices would therefore need the same **3 separate I2C buses** the
JAXA reference design uses, for the same underlying electrical reason —
this is a case where the JAXA reference's own architectural choice turns
out to be independently correct once verified, not a coincidence of
copying it.

**However**, BMI270 also supports SPI (already established in this
project's own MCU comparison table above, DS-IMU-008: "≤10 MHz, 3-/4-wire"),
and SPI's addressing model is fundamentally different — each device gets
its own dedicated chip-select (CS) line rather than sharing an address
space. **This means 6× BMI270 can be wired over a single shared SPI bus
(SCLK/MOSI/MISO) plus 6 individual CS lines**, avoiding the need for 3
separate I2C buses entirely. 6 CS lines are ordinary GPIO — a far smaller
pin-budget item than 3 full I2C bus pairs (SCL+SDA×3 = 6 pins vs. SPI's
3 shared + 6 CS = 9 pins — SPI uses slightly *more* total pins in this
specific comparison, but every candidate MCU has far more spare GPIO than
spare dedicated-I2C-peripheral instances, making the SPI approach the
practically easier one to route and matching the MCU Rev 5
recommendation's own already-limited I2C count).

#### Candidate Comparison

*(3 candidates compared — meets the ≥3 minimum.)*

| Parameter | Candidate A — Bosch Sensortec BMI270 (incumbent) — ✅ RECOMMENDED | Candidate B — TDK InvenSense MPU-6050 (JAXA reference part) | Candidate C — STMicroelectronics LSM6DSOX (existing documented fallback) |
|---|---|---|---|
| I2C address mechanism | SDO pin, 2 addresses (0x68/0x69) [DS-IMU-076, DS-IMU-078] | AD0 pin, 2 addresses (0x68/0x69) — the well-known constraint that drove the JAXA reference's own 3-bus architecture | SA0/SDO pin, 2 addresses (0x6A/0x6B), same class of constraint — not independently re-confirmed from a primary datasheet this session, existing repo prior research is the basis |
| SPI support | Yes, ≤10MHz [DS-IMU-008] — enables the 1-bus+6-CS architecture below | **No** (MPU-6050 itself is I2C-only; the SPI-capable variant is the separate MPU-6000 part, not this one) | Yes, ≤10MHz (already established in this project's original IMU comparison) |
| 6-device wiring implication | **1 shared SPI bus + 6 CS** (recommended) or 3 I2C buses (fallback) | **3 I2C buses required** (no SPI alternative for this exact part) | 1 shared SPI bus + 6 CS (same architecture as BMI270) or 3 I2C buses |
| Current lifecycle/EOL (2026) | Active, no EOL/NRND [DS-IMU-014] | **Not independently re-confirmed to a clean, current, primary-source lifecycle statement this session** — this is an old-generation part; its current 2026 production status carries real risk not previously flagged in this project | Active; used in the official Arduino Nano RP2040 Connect [DS-IMU-048] |
| Existing project integration | **Already validated in Rev 1-4**; official Bosch BSD-3-Clause driver already integrated into `firmware/bench-imu-01/` — reusing avoids re-qualifying sensor/driver risk across 6 devices | None — would require a full new driver integration ×6, discarding existing validated firmware | Named fallback in the original IMU comparison, but never actually integrated into firmware |
| Qty-6 pricing/stock | Prior repo data ≈$3.17-4.23/unit at qty-1 [DS-IMU-012/013]; **live qty-6/qty-100 pricing and current stock not independently re-verified this session** | **Live 2026 pricing/stock not cleanly re-verified this session** — automated distributor fetches were partially blocked | **Live 2026 pricing/stock not independently re-verified this session** |
| Known risks | Live qty-6 pricing/stock genuinely unconfirmed this session (flagged, not glossed over) | Old part, unclear current 2026 lifecycle status, no SPI alternative forces the less pin-flexible 3-I2C-bus architecture, zero existing project integration to reuse | Never actually integrated into this project's firmware despite being named fallback since Rev 1 |

#### Success-probability ranking

| Rank | Candidate | Verdict |
|---|---|---|
| 1 | **BMI270 ×6 (A)** | Best success probability: reuses an already-validated part + already-integrated driver, avoiding 6× new sensor/driver qualification risk. Real datasheet confirms its 2-address I2C limit matches MPU-6050's own constraint, but its SPI support (already established in this project) provides a cleaner 6-device wiring path than the JAXA reference's own I2C-only part allows. |
| 2 (not recommended, real fallback) | **LSM6DSOX (C)** | Electrically comparable, same SPI-based 6-device wiring path available, but has never been actually integrated into this project's firmware — switching now would mean discarding the already-working BMI270 driver integration for no clear gain. |
| 3 (rejected) | **MPU-6050 (B)** | The JAXA reference's own part, evaluated fresh per this project's own anti-copy discipline — same 2-address I2C limit as BMI270 but with **no SPI alternative**, forcing the less pin-efficient 3-separate-I2C-bus architecture; unclear current 2026 lifecycle status; zero existing project integration to build on. No real advantage found over the incumbent. |

#### Recommendation

- **Recommended candidate**: **A — Bosch Sensortec BMI270 ×6**, wired over
  **a single shared SPI bus with 6 individual chip-select lines** (not 3
  separate I2C buses, and not MPU-6050).
- **Rationale**:
  1. **Real re-justification, not silent reuse** (REQ-508): BMI270's own
     2-address I2C constraint was independently re-verified from this
     project's already-registered Evidence IDs before concluding SPI is
     the better architecture — this is not "it worked before, keep it."
  2. Reuses an already-validated part with an already-integrated,
     official BSD-3-Clause driver — avoids 6× new sensor/driver
     qualification risk that a switch to MPU-6050 or LSM6DSOX would
     introduce with no offsetting benefit.
  3. BMI270's SPI support (already established in this project's own
     prior Component Selection) provides a materially better 6-device
     wiring path (1 shared bus + 6 CS) than the JAXA reference's own
     MPU-6050, which is I2C-only and would force the full 3-bus
     architecture regardless of MCU choice.
  4. This interlocks favorably with the MCU Rev 5 recommendation (ESP32-S3,
     which has only 2 native I2C controllers) — the SPI architecture
     removes what would otherwise be a real MCU peripheral-count concern.
- **Trade-offs accepted**:
  - Giving up MPU-6050's status as "what the reference design used" — a
    deliberate, evidence-based rejection per this project's own explicit
    anti-copy instruction, not an oversight.
  - Live qty-6/qty-100 pricing and current stock were not independently
    re-verified this session for any of the 3 candidates — flagged
    honestly as an open UNKNOWN, not assumed favorable.
- **Open `UNKNOWN`s**:
  1. Live 2026 qty-6/qty-100 pricing and current distributor stock for
     BMI270 (and MPU-6050/LSM6DSOX) — not independently re-verified this
     session; re-verify before BOM lock.
  2. MPU-6050's current 2026 lifecycle/EOL status — not cleanly
     re-confirmed from a primary source this session; moot given
     rejection, but flagged for completeness.
  3. Exact SPI bus timing/CS-switching overhead for 6 devices sharing one
     bus at whatever sample rate the final control loop needs — a
     Circuit Design/Firmware Engineer-stage characterization, not
     resolved here.

#### Escalation flags

1. **Not an architecture-defining component decision in the same sense as
   the MCU** (the part itself is unchanged, already human-approved in
   Rev 1) — but the **wiring architecture change (I2C→SPI)** is a real,
   non-trivial Circuit Design input that should be confirmed before
   schematic work begins on the 6-IMU subsystem, per this project's own
   practice of flagging architecture-relevant findings even when the
   underlying part choice itself doesn't change.
2. **Live pricing/stock genuinely unconfirmed this session** — re-verify
   before BOM lock.

#### Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Component Engineer | Component Engineer (AI agent, via parallel research sub-agent) | 2026-09-04 | Proposed — reuse BMI270 ×6, switch wiring architecture to SPI (1 bus + 6 CS) |
| Hardware Lead | Hardware Lead (this session) | 2026-09-04 | Concur — recommend approval; SPI architecture change flagged for Circuit Design awareness |
| Chief Engineer (Human) | Human Chief Engineer | 2026-09-04 | **Approved** — "確定" (Kyosuke's own direct plain-text reply, turn 616, `session_store_sql` session `7fab99ef-5578-4d79-a9c2-b24dbcfe93be`, `2026-09-04T16:00:16.240Z`), in direct reply to a specific question naming this exact recommendation by name (turn 614, `2026-09-04T15:54:20.062Z`) — both turns independently re-verified by this session directly against the raw turn history, not accepted from a relayed summary alone. Approves BMI270 ×6 over a shared SPI bus + 6 CS lines as recommended. |

---

## Power Regulator (5V USB to 3.3V rail)

- **Driving requirement(s)**: REQ-101 (USB 5 V input, 4.75–5.25 V tolerance),
  REQ-102 (single 3.3 V logic rail), REQ-103 (≤300 mA @ 3.3 V system budget —
  regulator selected with real margin above this, not at the edge), REQ-201
  (0–40 °C ambient — thermal margin checked at 40 °C worst case), REQ-402
  (USB port transient/ESD/reverse-polarity protection — separate circuitry
  from the regulator; built-in regulator protection noted where evidenced),
  REQ-501 (≤~$15 total BOM, soft — regulator should be a small fraction).
- **Constraints**: USB 5 V bus power only (human-fixed constraint); fixed
  3.3 V output, no adjustable/resistor-divider topology needed; indoor
  desk/lab ambient 0–40 °C, no vibration/shock; low-volume/prototype
  quantities; single 2-layer PCB, ≤60×40 mm footprint target — informs
  package/hand-assembly weighting; paper design exercise this cycle, no
  physical build/power-on this session.

### Candidate Comparison

*(4 candidates compared — exceeds the ≥3 minimum; no sole-source
justification needed.)*

| Parameter | Candidate A — TI TLV75533PDBVR (LDO) | Candidate B — Microchip MCP1700T-3302E/TT (LDO) — ⚠ DISQUALIFIED | Candidate C — Generic/Multi-Source AMS1117-3.3 (LDO) — ⚠ HIGH RISK | Candidate D — TI TPS62082DSGR (Sync. Buck) |
|---|---|---|---|---|
| Manufacturer | Texas Instruments | Microchip Technology | Multi-source / generic (originally Advanced Monolithic Systems; also produced by UMW, Shenzhen Slkormicro, GOODWORK, unbranded sources) | Texas Instruments |
| Part Number | TLV75533PDBVR | MCP1700T-3302E/TT | AMS1117-3.3 (no single canonical manufacturer) | TPS62082DSGR |
| Topology | Linear LDO | Linear LDO | Linear LDO | Synchronous step-down (buck), TI DCS-Control, ~2 MHz [DS-PWR-035] |
| Output Voltage Accuracy | ±1% @ TJ=85°C [DS-PWR-001] | Typ ±0.4% @25°C; Max ±3% over −40 to +125°C [DS-PWR-012] | ~±3% (3.201–3.399V across temp) [DS-PWR-024] | `UNKNOWN` — exact tolerance % not confirmed this session; no value assumed |
| Input Voltage — Absolute Maximum Rating | 6.0 V [DS-PWR-002] | 6.0 V [DS-PWR-013] | 15 V per original AMS datasheet; clone variants may state a different (often lower) figure [DS-PWR-025] | −0.3 V to 7 V [DS-PWR-036] |
| Input Voltage — Recommended Operating Condition | 1.45–5.5 V [DS-PWR-002] | 2.3–6.0 V [DS-PWR-013] — **ROC max exactly equals AMR max, zero buffer** | Cited up to 12 V for sustained operation [DS-PWR-025] | 2.3–6.0 V [DS-PWR-036] — 1 V buffer to AMR max |
| USB range (4.75–5.25V, REQ-101) fit | ✅ Comfortably within ROC, well under AMR | ✅ Within ROC/AMR but zero-buffer ceiling | ✅ Within either cited interpretation | ✅ Comfortably within ROC, well under AMR |
| Max Rated Output Current | 500 mA [DS-PWR-003] | **250 mA** [DS-PWR-014] | 1 A (thermal-limited in practice) [DS-PWR-026] | 1.2 A [DS-PWR-037] |
| Current margin vs. REQ-103 (300 mA) | 500÷300 = 1.67× headroom (60% of rated max used) | **250 mA < 300 mA budget — DISQUALIFYING** | 1000÷300 = 3.33× headroom (30% used) | 1200÷300 = 4× headroom (25% used) |
| Dropout Voltage @ rated Iout, Vout=3.3V | Typ 220 mV/Max 238 mV @ 500 mA [DS-PWR-004]; at Vin=4.75V/3.3V out, headroom ≈1.45V | Typ 178 mV/Max 350 mV @ 250 mA, TA=25°C [DS-PWR-015] | Typ 1.1V/Max 1.3V @ 0.8A [DS-PWR-027] — notably higher than A/B, still ample headroom | N/A — synchronous buck; dropout not the relevant spec [DS-PWR-035] |
| Efficiency @ ~1A load, 5V→3.3V | N/A — linear LDO; theoretical max ≈ Vout/Vin ≈ 66% | N/A (same) | N/A (same) | ~94% typical @ 1A load [DS-PWR-038] |
| Quiescent Current Iq | 25 µA typ, no-load, Vin=3.6V [DS-PWR-005] | 1.6 µA typ/4.0 µA max, no-load, Vin=5.0V [DS-PWR-016] — lowest of all 4, secondary to disqualification | 5 mA typ/11 mA max, no-load [DS-PWR-028] — dramatically higher than A/B | 6.5 µA typical, Snooze/light-load PFM [DS-PWR-039] |
| Package | SOT-23-5 [DS-PWR-006] | SOT-23-3, no exposed pad [DS-PWR-017] | SOT-223-3, no exposed pad [DS-PWR-029] | 8-WSON 2×2mm, exposed thermal pad [DS-PWR-040] |
| Package θJA | 60.3°C/W, standard PCB, no copper pour [DS-PWR-006] | ≈336°C/W (no exposed pad) [DS-PWR-017] | ≈90°C/W bare PCB; 55–80°C/W with copper pour [DS-PWR-029] | ≈60°C/W, standard 2-layer PCB [DS-PWR-040] |
| Junction Temp Absolute Max Rating | 150°C [DS-PWR-007] | 125°C [DS-PWR-018] | ≈165°C (thermal shutdown threshold) [DS-PWR-030] | `UNKNOWN` — not confirmed this session |
| Derived Thermal Margin @ TA=40°C, 300 mA load | Max PD budget=(150−40)/60.3≈1.82W. Actual PD=510mW. Est. TJ≈**71°C** — ~79°C headroom [DS-PWR-008] | Max PD budget=(125−40)/336≈253mW. Actual PD at rated 250mA=425mW — **exceeds budget even at rated current** [DS-PWR-019] | PD@300mA=510mW. Est. TJ≈**86°C** — numerically within limits, but thermal-shutdown reliability itself subject to clone risk [DS-PWR-031] | Est. loss≈63mW at 300mA/990mW output; est. TJ≈**44°C** — far cooler than any LDO, but cannot express as %-of-budget since TJmax `UNKNOWN` [DS-PWR-041] |
| Regulator's own built-in protection (context for REQ-402) | `UNKNOWN` this session — REQ-402's USB-port protection remains separate Circuit-Engineer-owned circuitry regardless | `UNKNOWN` — same caveat | Thermal shutdown ≈165°C evidenced, but reliability subject to clone risk | `UNKNOWN` — same caveat |
| Hand-Assembly / Package Solderability | Standard leaded SMD, hand-solderable [DS-PWR-006] | Standard leaded SMD, hand-solderable [DS-PWR-017] | Larger leaded SMD, easy hand assembly [DS-PWR-029] | **Exposed thermal pad CANNOT be reliably hand-soldered — requires reflow/hot-air/hot-plate** [DS-PWR-042] |
| Multi-Source / Clone Risk | Low — genuine single-source TI part [DS-PWR-010] | Low — genuine single-source Microchip part [DS-PWR-021] | **HIGH — produced/marked by dozens of manufacturers under identical marking; documented variance in silicon quality, dropout, thermal-shutdown reliability, and max Vin rating** [DS-PWR-023] | Low — genuine single-source TI part [DS-PWR-044] |
| Price @ Qty 1 / Qty 100 (USD) | $0.45/$0.2396 (DigiKey); $0.42/$0.226 (Mouser) [DS-PWR-009] | $0.38–0.51/~$0.39 (DigiKey); $0.51/$0.398 (Mouser) [DS-PWR-020] | ~$0.30/~$0.16 (DigiKey, UMW brand); gray-market as low as $0.02–0.04, not recommended [DS-PWR-032] | $1.76/$1.04 (DigiKey and Mouser both) [DS-PWR-043] |
| % of REQ-501 ≤~$15 soft BOM target (qty100) | ≈1.5–1.6% | ≈2.6% (moot — disqualified) | ≈1.1% (genuine risk aside) | ≈6.9% (qty1: ≈11.7%) |
| Lifecycle / EOL status | Active [DS-PWR-010] | Active (Octopart projects through ~2034) [DS-PWR-021] | Active as a commodity item; clone/quality-consistency risk is the dominant concern [DS-PWR-033] | Active [DS-PWR-044] |
| Reference design available? | Y — TI SLVSDV4, ceramic-only (CIN=1µF, COUT=0.47µF min) [DS-PWR-011] | Y — simplest possible LDO circuit (CIN/COUT=1.0µF ceramic each) [DS-PWR-022] | Y, but requires a 22µF solid tantalum (or equivalent low-ESR ceramic) output cap [DS-PWR-034] | Y — TI SLVSB80, formal EVM with BOM/layout files [DS-PWR-045] |
| SDK / sample code / docs ecosystem | Excellent — clearly separates AMR/ROC, load/line regulation + PSRR curves [DS-PWR-011] | Very clean, but oriented around battery/wearable use cases [DS-PWR-022] | Variable/inconsistent between clone-manufacturer datasheets [DS-PWR-034] | Excellent — efficiency curves, WEBENCH-compatible design tool [DS-PWR-045] |
| Known risks | Low overall risk; minor open item on the 1.45V ROC minimum's exact basis (does not affect recommendation). | **DISQUALIFIED**: 250 mA rated max < REQ-103's 300 mA budget; own package thermal budget exceeded even at rated 250 mA. | **HIGH RISK — not recommended despite adequate raw specs.** Multi-manufacturer/clone market means the part that actually ships on a PO is not guaranteed to match the datasheet read. | Low electrical/technical risk but real DFM risk: WSON pad requires reflow/hot-air, incompatible with hand-iron assembly. ~4× unit price of the LDO alternatives. |

### Recommendation

- **Recommended candidate**: **A — Texas Instruments TLV75533PDBVR**.
- **Rationale** (success probability first, peak spec second): meets every
  driving requirement with real, quantified margin — REQ-101 (ROC/AMR both
  clear USB's 4.75–5.25 V with buffer), REQ-102 (fixed 3.3 V output, no
  resistor divider to get wrong), REQ-103 (500 mA rated ÷ 300 mA budget =
  1.67× headroom), REQ-201 (thermal margin computed explicitly at TA=40°C:
  estimated TJ≈71°C vs. 150°C max, ~79°C of headroom on a bare PCB with no
  copper-pour improvement). Proven, simple reference design using
  ceramic-only capacitors — no exotic tantalum dependency (unlike Candidate
  C). Genuine single-source TI part with confirmed Active lifecycle. SOT-23-5
  is trivially hand-solderable with a standard iron — no reflow/hot-air
  dependency (unlike Candidate D's WSON pad), which matters concretely since
  this project's physical build happens later, under assembly
  equipment/method not yet controlled for. Price (~1.5–3% of the REQ-501
  target) is a small fraction as expected of a supporting component.
  Simplicity is a genuine engineering virtue here, not just a fallback: an
  LDO has fewer component types (no inductor), no switching-noise/EMI
  concern to manage near a sensitive 6-axis IMU's ADC. Because this is
  USB-powered (not battery/efficiency-constrained), a buck converter's
  efficiency advantage solves a problem this project doesn't have.
  REQ-402 note: none of the 4 candidates' regulator ICs have a *confirmed*
  built-in ESD/transient/reverse-polarity protection feature relevant to the
  USB connector itself — this remains a separate Circuit-Engineer-owned
  protection network (e.g. TVS diode) regardless of which regulator is
  chosen; not a point against Candidate A specifically.
- **Trade-offs accepted**:
  - *vs. Candidate B (MCP1700)*: gives up B's much lower Iq — not a real
    trade-off since B is independently disqualified on two grounds (current
    rating below budget, own thermal budget exceeded at rated current).
  - *vs. Candidate C (AMS1117-3.3)*: gives up a marginally lower qty-100 unit
    price (~$0.07/unit, under 0.5% of the whole-board target) and a higher
    absolute current headroom — in exchange for eliminating a documented
    clone/counterfeit/quality-consistency risk entirely and avoiding an added
    tantalum-class output cap. Building this repo's first real design-cycle
    power rail on a part whose actual shipped silicon varies by reel is a
    bad trade against a savings that doesn't meaningfully move the ≤$15
    target.
  - *vs. Candidate D (TPS62082)*: gives up substantially better efficiency
    (~94% vs. an LDO's ~66% theoretical ceiling) and a larger absolute
    thermal cushion — in exchange for ~4× lower unit price, avoiding the
    WSON exposed-pad package's reflow/hot-air assembly requirement (a real
    DFM risk given the physical build happens later, under conditions not
    yet controlled for), avoiding an inductor and its associated EMI/layout
    considerations near a sensitive 6-axis IMU, and avoiding two open
    UNKNOWNs (exact output accuracy, TJ max). Candidate A already clears its
    own thermal budget with ~79°C of headroom using the simpler, cheaper,
    easier-to-assemble part.
- **Open `UNKNOWN`s**:
  - Candidate D's exact output voltage accuracy tolerance and TJ max — not
    confirmed this session; closing this gap is a prerequisite before D
    could be seriously re-considered on thermal grounds.
  - Candidate A's Vin ROC minimum (1.45 V) not independently re-confirmed
    against the literal TI PDF table (only a mirror site cross-checked) —
    does not change the recommendation (USB's 4.75 V floor clears either
    interpretation).
  - Exact stock quantity/lead time for all 4 candidates not confirmed
    numerically this session (only qty1/qty100 pricing-tier listings).
  - Built-in overcurrent/thermal-shutdown protection: only Candidate C had an
    explicit thermal-shutdown-threshold figure surfaced; no equivalent
    confirmation found for A, B, or D.

### Escalation flags

1. **Candidate B (MCP1700T-3302E/TT) is explicitly DISQUALIFIED** — 250 mA
   rated max output current is below REQ-103's 300 mA system budget, and its
   own package thermal budget is exceeded by actual dissipation even at its
   own rated 250 mA at TA=40°C ambient. Two independent, quantified
   disqualifiers.
2. **Candidate C (AMS1117-3.3) is flagged HIGH RISK** on clone/manufacturing-
   consistency grounds, weighing heavily against recommending it despite raw
   specs that look adequate on paper.
3. **HITL-gate judgment call**: a 5V→3.3V regulator selection is not
   architecture-defining in the way an MCU/IMU silicon choice is (it does
   not constrain firmware, interfaces, or the digital design) — standard
   Hardware Lead review is likely sufficient without a separate Chief
   Engineer sign-off, but this is the Hardware Lead's call to make per
   `docs/architecture.md` §10, not the Component Engineer's to unilaterally
   decide.

### Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Component Engineer | Component Engineer (AI agent) | 2026-08-30 | Proposed — TLV75533PDBVR |
| Hardware Lead | Hardware Lead (this session) | 2026-08-30 | Concur — recommend approval; not treated as requiring separate Chief Engineer sign-off per Escalation flag 3, but reported alongside MCU/IMU per the human's explicit "report all three" instruction |
| Chief Engineer (Human) — required if architecture-defining/major component | Human Chief Engineer | 2026-08-30 | **Approved** — "Approve all three as recommended" (Checkpoint B, recorded via ask_user; independently re-confirmed after the worktree-restore incident, see `validation/change-log.md` ECO-001) |

---

## Motor (Reaction Wheel Drive)

> **Rev 3 addition.** This section and "Motor Driver IC" below were produced
> together in one pass, per this task's own instruction — the motor-type
> decision and driver-IC decision are coupled (a driver family only makes
> sense against a specific motor commutation type), so they were reasoned
> about jointly even though they are recorded as two separate sections
> mirroring this file's existing per-part-need structure. **The target this
> comparison is designed against (REQ-007's flywheel mass/radius/RPM/torque
> figures, and the "no motor-type preference" framing) is itself only a
> *provisional*, not-yet-human-confirmed default** —
> `requirements/requirements.md` §9b/§9c. If the human changes those figures
> materially, the torque-margin conclusions below should be revisited, not
> assumed to still hold.

- **Driving requirement(s)**: REQ-007 (open-loop PWM/speed-setpoint control
  of the flywheel — the core functional need), REQ-008 (measure and report
  actual RPM back to the host, contingent on whatever RPM-sensing capability
  the selected motor+driver combination actually provides — this is why RPM-
  sensing capability is scored as its own comparison criterion below, a new
  criterion specific to this task), REQ-009 (open-loop only — no closed-loop/
  PID/sensor-fusion control this cycle, which de-weights "smoothest possible
  commutation for precision control" relative to what a real flight reaction
  wheel would need), REQ-108/109 (a dedicated power architecture and a
  separate motor-rail current budget will be defined by the Power Engineer
  once engaged, directly consuming the real current/voltage numbers in the
  comparison table below — this is the primary reason these numbers must be
  datasheet-grounded, not rough guesses), REQ-110 (MCU shall generate a PWM
  or equivalent drive signal — informs which control interfaces count as a
  "clean" match), REQ-111/404 (driver-level overcurrent/stall protection —
  more a driver-selection criterion, but the motor's own stall-current
  behavior feeds it), REQ-112 (wire any available RPM/tach signal to the
  MCU), REQ-204/307 (vibration exposure and isolation from the IMU — motor
  mass and mounting matter), REQ-306/403 (rotation clearance and projectile/
  pinch-hazard safety — shaft interface and mounting matter), REQ-503 (Rev 3
  ≤$75–90 USD total subsystem soft budget — this motor is one line item
  within that, not the whole budget).
- **Constraints**: bench-test, open-loop-only hardware — not a flight
  reaction wheel, so real flight-heritage brushless preference is *context*,
  not a binding constraint (§9b Q2); no motor-type preference stated —
  brushed DC, BLDC, and stepper are compared on merit; flywheel target
  ≈100 g at ≈30 mm radius, spin-up to ≥3000 RPM, storing ≈10–15 mN·m·s,
  motor delivering ≥5 mN·m continuous torque (arithmetic re-verified this
  session: I = 0.5·m·r² ≈ 4.5×10⁻⁵ kg·m² at 100 g/30 mm, L = I·ω ≈ 14.1
  mN·m·s at 3000 RPM — consistent with `requirements/requirements.md` §9b's
  own figures); real bearing/friction losses not yet characterized (per
  §9b's own caveat) — torque-margin conclusions below assume the datasheet/
  derived torque figures are available *at the shaft*, before any such
  losses; Rev 3 soft budget ≤$75–90 total for the whole new subsystem
  (motor + driver + flywheel + connectors + wiring), not just the motor;
  no existing rail on this board is assumed adequate for a motor load —
  that is exactly the open question this comparison's real numbers feed
  into the Power Engineer's upcoming HITL gate, not an assumption made here.

### Candidate Comparison

*(4 candidates compared, across all 3 motor types per the "no preference"
constraint — exceeds the ≥3 minimum, no sole-source justification needed.)*

| Parameter | Candidate A — Maxon RE 16 Ø16mm 118725 (Brushed DC) — ⚠ DISQUALIFIED | Candidate B — Anaheim Automation BLY171D-24V-4000 (Sensored BLDC) | Candidate C — T-Motor MN2206-13 KV2000 (Sensorless BLDC) — ✅ RECOMMENDED | Candidate D — SOYO SY28STH32-0674A / Pololu #1205 (Stepper) — ⚠ DISQUALIFIED |
|---|---|---|---|---|
| Manufacturer | Maxon Motor AG / maxon group | Anaheim Automation, Inc. | T-Motor (Nanjing Tiger Motor Technology) | SOYO (sold as Pololu item #1205) |
| Part Number | 118725 | BLY171D-24V-4000 | MN2206-13 KV2000 (Navigator series) | SY28STH32-0674A |
| Motor type | Brushed DC, graphite brushes | 3-phase BLDC, **sensored** (integrated Hall) | 3-phase BLDC, **sensorless** (outrunner), 12N14P | 2-phase hybrid stepper, NEMA11 |
| Rated / nominal voltage | 4.8 V nominal [DS-MTR-001] | 24 V DC [DS-MTR-009] | 2S–3S LiPo, 7.4–11.1 V nominal / 8.4–12.6 V full-charge — no single stated max terminal voltage, rated by cell count [DS-MTR-017] | 3.8 V rated [DS-MTR-025] |
| No-load current / speed | 105 mA / 12,700 RPM @ 4.8 V [DS-MTR-001] | N/A (BLDC rated by load point, not no-load) — derived no-load speed ≈8,889 RPM from Ke [DS-MTR-011] | 0.3 A @ 10 V; derived no-load speed ≈20,000 RPM @10V / ≈22,200 RPM @11.1V (derived from KV, not directly published) [DS-MTR-018] | N/A (stepper — no-load current concept doesn't apply the same way) |
| Stall / max current | Stall current 7.56 A, stall torque 26.3 mN·m [DS-MTR-002] | Rated current ≈1.08 A **derived** from ~26W/24V, not directly published [DS-MTR-010] | Max continuous current 18 A (180 s rating); theoretical stall current ≈135 A (not a practical operating point) [DS-MTR-019, DS-MTR-020] | Rated current 670 mA/phase [DS-MTR-025] |
| Torque available at ≥5 mN·m target | Continuous (nominal) rating only 2.15 mN·m @ 11,200 RPM/0.72 A — **below target on a continuous-duty basis**, but ≈20.1 mN·m available at 3000 RPM under short-term spin-up conditions from the speed-torque line, with only ≈2°C estimated winding temperature rise over a 2.83 s spin-up [DS-MTR-003, DS-MTR-004, DS-MTR-006] | Rated **continuous** torque 62.8 mN·m @ 4000 RPM — **12.6× the target**, heavily over-specified [DS-MTR-010]; peak (intermittent) torque ≈219 mN·m also legible on the same spec sheet, though the exact duration/duty-cycle basis defining "peak" was not confirmed this session [DS-MTR-012] | No manufacturer torque figure published (normal for a hobbyist multirotor motor). **Derived** Kt = 60/(2π·KV) = 4.77 mN·m/A ⇒ only ≈1.05 A needed for 5 mN·m — ample headroom vs. the 18 A continuous rating [DS-MTR-020] | **Marginal/unconfirmed.** Holding torque 58.8 mN·m @ 3.8 V/670 mA is a *low-speed/static* figure only [DS-MTR-026]; at the 3000 RPM/10 kHz step rate, winding L/R time constant (0.75 ms) is 7.5× the 0.10 ms step period — only ≈12.5% of holding torque realistically available (≈7.4 mN·m theoretical, borderline) at rated voltage; a 24 V chopper drive improves this to an estimated 5–20 mN·m, "marginal at best" — **no manufacturer torque-speed curve exists to confirm** [DS-MTR-030, DS-MTR-031] |
| Max rated / mechanical speed | 16,000 RPM max permissible mechanical speed [DS-MTR-004] | 4000 RPM rated (this is the sheet's *rated* operating point, not a hard ceiling) [DS-MTR-011] | No published max; 3000 RPM target is only 13–20% of the ≈20,000–22,200 RPM derived no-load speed — "a very gentle operating condition" [DS-MTR-018] | 200 steps/rev at 1.8°/step; RPM is entirely a function of commanded step rate, not an intrinsic motor ceiling [DS-MTR-026] |
| Torque/speed constants | Kt = 3.48 mN·m/A, Ke = 2750 RPM/V [DS-MTR-004] | Ke = 2.7 V/kRPM ⇒ derived ≈370 RPM/V KV-equivalent [DS-MTR-009] | KV = 2000 RPM/V (published); Kt = 4.77 mN·m/A (**derived**, not published) [DS-MTR-017, DS-MTR-020] | Coil resistance 5.6 Ω/phase, inductance 4.2 mH/phase [DS-MTR-025] |
| Mass | 40 g [DS-MTR-005] | ≈299 g (0.66 lb) — **≈3× the 100 g flywheel target alone**, mechanically awkward [DS-MTR-013] | **30 g** — lightest of all 4 candidates [DS-MTR-021] | 110 g [DS-MTR-027] |
| Package / dimensions / shaft | Body Ø16 mm confirmed; length/shaft/mounting pattern **UNKNOWN this session** — a research sub-agent's figures for these were self-flagged "from training data," not independently re-verified, so they are not repeated here as if confirmed [DS-MTR-005] | 42 mm² NEMA17 frame × 40.4 mm length, pole count **UNKNOWN** [DS-MTR-013] | Ø27 mm × 18.5 mm overall; stator Ø22 mm × 6 mm; 3 mm shaft; outrunner (flywheel can mount directly to the rotating bell, maximizing inertia per gram) [DS-MTR-021] | NEMA11, 28×28 mm × ≈32 mm length; 5 mm D-flat shaft; rotor inertia **UNKNOWN** [DS-MTR-027] |
| **RPM-sensing capability** (new criterion) | **None integrated** on this base SKU — encoder-combination SKUs exist only as separate paid accessories ($30–80+); external bolt-on encoder (e.g. magnetic AS5600, optical US Digital) is a realistic DIY option [DS-MTR-005] | **Yes — 3× integrated Hall-effect sensors**, 5-wire harness, 5 V logic (needs level-shifting or open-drain/pull-up confirmation for a 3.3 V MCU input) — the only candidate with native integrated sensing [DS-MTR-014] | **None integrated** (sensorless outrunner) — but the paired driver IC (see Motor Driver IC section) supplies a hardware FG output derived from back-EMF; reliable BEMF detection typically degrades below ≈500–1500 RPM, a caveat for spin-up specifically, not the 3000 RPM steady-state point [DS-MTR-022] | **None integrated**; no confirmed encoder-equipped sibling SKU found — a stepper's own commanded step count is a form of "sensing" only if steps are never lost, which the torque-margin finding above makes a real risk at this RPM [DS-MTR-028] |
| Lifecycle / EOL | **NRND** (Not Recommended for New Designs), verbatim [DS-MTR-007] | Active, no EOL notice found [DS-MTR-015] | Active (older 1400KV sibling appears discontinued; no EOL notice for this 2000KV variant) [DS-MTR-023] | Active/in-stock at Pololu [DS-MTR-029] |
| Availability / lead time | In stock at maxongroup.us direct store [DS-MTR-008] | Up to 90-day factory-direct lead time; faster 3rd-party (Radwell, eBay) alternates exist [DS-MTR-016] | In stock, ships immediately (Graves RC Hobbies) [DS-MTR-023] | In stock (Pololu direct; cross-listed at DigiKey) [DS-MTR-029] |
| Reference design / prior art | None found for continuous-spin/reaction-wheel use | None found for this exact SKU; NEMA17-class BLDCs used generically in academic reaction-wheel literature [DS-MTR-016] | **Exceptionally strong** — 2 GitHub CubeSat reaction-wheel projects built around this exact motor or a close sibling, plus a Charles' Labs build and an Embry-Riddle academic platform [DS-MTR-024] | None found for continuous-spin/reaction-wheel use |
| Ecosystem / driver compatibility | Standard brushed H-bridge driver family (see Motor Driver IC section's footnote) | Compatible with sensored-BLDC drivers (e.g. DRV8313, MCF8315A, A4931 — noted by research, not carried into the formal driver comparison since this motor isn't recommended) | Mature sensorless-BLDC ecosystem: BLHeli_32/AM32 ESCs, VESC, SimpleFOC, and the paired driver IC below | Standard stepper chopper-driver family (not researched in depth this session since this motor is disqualified on physics grounds before reaching driver pairing) |
| Price @ qty 1 | **$209.52** (qty 1–4); $184.82 (qty 5–19); $155.93 (qty 20–49) [DS-MTR-008] | **$65.00** (qty 1); $62.18 (qty 10); $50.16 (qty 25) [DS-MTR-015] | **$18.99** (qty 1) [DS-MTR-023] | **$39.92** (qty 1); $37.52 (qty 5); $35.27 (qty 25) [DS-MTR-029] |
| % of Rev 3 $75–90 subsystem budget (qty 1, low end) | ≈279% — **motor alone exceeds the entire subsystem budget** | ≈87% — consumes nearly the whole subsystem budget alone | ≈25% — leaves ≈$50–65 headroom for driver + flywheel + PCB + connectors + wiring | ≈53% |
| Known risks / disqualifying factors | **DISQUALIFIED**: price ≈2.7× over budget; NRND lifecycle; zero native RPM-sensing path; no reaction-wheel reference design. Continuous torque rating alone reads below target (though short-term spin-up torque and thermal margin are adequate) — not the primary disqualifier, budget/lifecycle are. | Not disqualified on electrical/functional grounds — heavily over-specified on torque, native Hall sensing is a real strength — but mass (≈3× the flywheel itself) and price (≈87% of the whole subsystem budget) make it a poor fit versus Candidate C. Retained as the strongest **fallback** candidate if Candidate C's sensorless RPM-sensing path fails at bring-up. | Low technical risk identified; open items are the derived (not manufacturer-published) torque constant and the sensorless BEMF low-speed detection floor during spin-up (both addressed in Recommendation below). | **DISQUALIFIED**: well-cited physics (L/R time-constant analysis) shows continuous torque at the 3000 RPM target is marginal-to-infeasible with an ordinary driver; zero native RPM-sensing path; no reaction-wheel reference design found; no published torque-speed curve to even confirm the marginal estimate. |

*A cheaper Pololu brushed-DC alternative (item #1117) was informally
surfaced during research as a potential lower-cost brushed-DC option, but
was found to fail the torque margin (back-calculated stall torque only
≈3.6–7 mN·m against the 5 mN·m target) and has no manufacturer datasheet —
not viable, and not added as a formal 5th candidate since it fails on its
own merits rather than adding a genuinely new trade-off to weigh.*

**Correction note (2026-09-13, MISS-019, LOW, non-safety-degrading):**
the "≈22,200 RPM @11.1V" and "≈20,000–22,200 RPM" figures in the table
rows above (lines 495, 498) remain arithmetically correct as *derived
KV×V* estimates at the specific voltages stated — they are not deleted
or wrong on their own terms. However, 11.1V was elsewhere mislabeled
"full-charge 3S" when it is actually 3S's *nominal* voltage (full-charge
is 12.6V); the design's own later-established, real 9.0–13.0V `VM_MOTOR`
qualified envelope (`hardware/schematic/bench-imu-01-design.md` §7.5.9)
implies a corrected, higher credible-worst-case no-load speed of
≈25,180 RPM once real circuit-path voltage drops are also accounted for
(§7.5.13, DS-MTR-018 corrected/DS-MTR-080). This does not change this
section's own Component Selection-era recommendation or trade-off
analysis (Candidate C remains the correct choice on every criterion
compared here), and the error direction is non-safety-degrading — REQ-007's
3000 RPM target is an even *smaller* fraction of the true no-load speed
than stated ("13–20%" understates how gentle the target operating point
actually is). See §7.5.13 and `validation/open-issues.md` MISS-019 for
the full correction; not re-litigated in the table above per this
document's own convention of preserving the original decision record.

### Recommendation

- **Recommended candidate**: **C — T-Motor MN2206-13 KV2000 (sensorless
  BLDC)**.
- **Motor-type elimination reasoning (the coupling point with the Motor
  Driver IC section below)**: brushed DC and stepper are **both eliminated
  as a type**, not just as individual SKUs — brushed DC's best-fitting real
  candidate (Maxon) is disqualified on budget/lifecycle grounds and brushed
  DC as a type has zero native RPM-sensing path requiring an added external
  encoder regardless of which specific brushed motor is chosen; stepper's
  well-cited L/R time-constant physics makes continuous torque at the 3000
  RPM target marginal-to-infeasible with an ordinary driver, independent of
  which specific stepper SKU is chosen, and also has zero native RPM-sensing
  path. This leaves **BLDC as the only motor type still in contention**,
  which is why the Motor Driver IC section below formally compares only
  BLDC/sensorless-BLDC driver ICs (with H-bridge brushed-DC drivers
  mentioned only as a footnote for process transparency, per this task's own
  instruction to match the driver comparison to the surviving motor type).
- **Rationale** (success probability first, peak spec second):
  1. **Budget fit is decisive, not marginal.** At $18.99, Candidate C
     consumes only ≈25% of the Rev 3 subsystem's $75–90 soft ceiling,
     leaving ≈$50–65 for the driver IC, flywheel machining, PCB, connectors,
     and wiring. Candidates A and B alone consume 279% and 87% of that same
     budget respectively — either would force cuts elsewhere in the
     subsystem or blow the ceiling outright.
  2. **Mass is the lightest of all 4 candidates (30 g)** — directly helps
     REQ-306 (rotation clearance envelope) and REQ-307 (vibration isolation
     from the IMU) by keeping the rotating assembly's total mass/inertia
     budget dominated by the flywheel itself (≈100 g) rather than by the
     motor, and helps REQ-308's soft desk-scale enclosure bound.
  3. **Torque margin is real and generous, not assumed.** The derived
     torque constant (Kt = 4.77 mN·m/A) means only ≈1.05 A is needed to
     produce the 5 mN·m target — against an 18 A continuous rating, this is
     roughly 17× current headroom. Even granting meaningful uncertainty in
     the derivation (it is *derived* from KV, not a manufacturer-published
     torque figure — see Open UNKNOWNs), the margin is large enough to
     absorb real bearing/friction losses that requirements.md's own §9b
     explicitly flags as not yet characterized.
  4. **Direct, repeated reaction-wheel/CubeSat project heritage is the
     strongest differentiator versus every other candidate.** Two
     independent GitHub projects (`yiqiangjizhang/CubeSat-Reaction-Wheel-
     control`, `Thissp97/Reaction-Wheel-for-CubeSat`) plus a Charles' Labs
     build and an Embry-Riddle academic platform have already run this
     exact motor (or a close KV sibling) as a continuous-spin reaction
     wheel — this is direct evidence the part *works* in this exact
     application, not just that its datasheet numbers look adequate on
     paper. None of the other 3 candidates have any reaction-wheel-specific
     prior art at all.
  5. **RPM-sensing gap is real but has a credible resolution, not a silent
     gap.** Candidate C itself has no integrated Hall sensor or encoder —
     but the recommended paired driver IC (TI DRV10983, see Motor Driver IC
     section) provides a hardware FG output pin derived from back-EMF
     sensing, which is judged an adequate REQ-008/112 answer at the 3000
     RPM steady-state operating point. This is not free of risk — see Open
     UNKNOWNs below and the Motor Driver IC section's own escalation flags.
  6. This recommendation deliberately does **not** chase Candidate B's
     "real" integrated Hall sensors or Candidate A's mature, well-
     characterized-at-low-speed brushed DC control simplicity, because
     both lose on cost/mass/lifecycle grounds that matter more for this
     specific project's success than peak sensing fidelity — consistent
     with this role's "success probability first, peak spec second"
     mandate.
- **Trade-offs accepted**:
  - *vs. Candidate A (Maxon, brushed DC)*: gives up a mature, simple,
    well-understood brushed-DC control scheme (no commutation electronics
    needed beyond a basic H-bridge) — in exchange for eliminating an NRND
    lifecycle risk and a price point that alone exceeds the entire Rev 3
    subsystem budget. Not a close call.
  - *vs. Candidate B (Anaheim, sensored BLDC)*: gives up **native, direct
    Hall-effect RPM sensing** (a real, meaningful capability Candidate C
    lacks) and gives up a large, confirmed torque margin (62.8 mN·m
    continuous vs. Candidate C's ≈1.05 A-derived need) — in exchange for
    ≈3.4× lower price, ≈10× lower mass, and direct reaction-wheel project
    heritage that Candidate B does not have. This is the trade-off most
    worth revisiting if Candidate C's sensorless RPM-sensing path proves
    unreliable at bring-up (see Escalation flags) — Candidate B is recorded
    here specifically as that fallback.
  - *vs. Candidate D (SOYO/Pololu stepper)*: gives up native, precise
    open-loop position control via commanded step count (in principle, if
    no steps are ever lost) — in exchange for avoiding a well-cited,
    unresolved risk that the stepper cannot deliver its target torque at
    all at the required RPM, and gaining a motor type with an actual
    continuous-high-speed-spin design intent (BLDC) rather than one
    optimized for low-speed positioning torque.
- **Open `UNKNOWN`s**:
  - The core torque figure this recommendation rests on (Kt = 4.77 mN·m/A,
    ⇒ ≈1.05 A needed for 5 mN·m) is a **derived** estimate from the
    published KV constant, not a manufacturer-stated torque number — no
    stall/peak torque or torque-speed curve is published for this SKU at
    all (normal for a multirotor-market motor). The margin is large enough
    (≈17× on current) that this is judged low-risk, but it is not the same
    confidence level as a directly-published torque figure.
  - Whether the paired driver's BEMF-derived FG signal will be clean/
    monotonic specifically during the 0→3000 RPM spin-up ramp for *this*
    motor+driver combination is not resolvable from datasheets alone — no
    hardware has been built yet. Flagged as a bring-up validation item for
    Circuit Engineer/Firmware, not a blocking issue for this recommendation.
  - Real bearing/friction losses for whatever bearing/shaft/flywheel-mount
    solution Mechanical Lead eventually designs are not yet characterized
    (per requirements.md §9b's own caveat) — the ≈17× current margin is
    judged large enough to absorb a reasonable range of such losses, but
    this has not been bench-verified (REQ-504 — no physical build this
    cycle).
  - Candidate A's package dimensions beyond body diameter (length, shaft,
    mounting pattern) and Candidate B's pole count are recorded `UNKNOWN`
    in the table above rather than guessed — not blocking since neither is
    the recommended candidate, but would need to be closed before either
    could be seriously re-considered as a fallback.

### Escalation flags

1. **Architecture-defining / major component decision — requires Hardware
   Lead + human Chief Engineer approval before Circuit Engineer uses this**
   (`docs/architecture.md` §10). This is explicitly **not self-approved**;
   see Approval table below.
2. **The target this comparison is designed against is itself only
   provisionally adopted, not human-confirmed** — `requirements/
   requirements.md` §9b/§9c records the flywheel/torque/RPM figures and the
   "no motor-type preference" framing as the Hardware Lead's own proposed
   defaults, adopted autonomously after `ask_user` went unanswered this
   cycle, with the human's real sign-off still open and solicited. If the
   human changes any of those figures materially, this comparison's torque-
   margin conclusions (especially the derived-Kt margin analysis for
   Candidate C) should be re-checked, not assumed to still hold.
3. **New ~12 V rail requirement for the Power Engineer.** The recommended
   motor+driver pairing (Candidate C + TI DRV10983, see Motor Driver IC
   section) needs to run from approximately 12 V to clear the driver's 8 V
   minimum input with real margin — Candidate C's own 2S-nominal (7.4 V)
   rating undershoots that minimum. Rev 1/2 of this board has only a single
   3.3 V rail (via the existing TLV75533 LDO, REQ-102). **This is a
   structural change to the power architecture, not a decision made here**
   — it is flagged for the Power Engineer's own HITL-gated rail-topology/
   sourcing proposal (`hardware/power-architecture.md`,
   `.github/agents/power-engineer.agent.md`), per REQ-108's own contingency
   for exactly this kind of finding.
4. **Fallback path recorded, not silently discarded.** If Candidate C's
   sensorless RPM-sensing path (BEMF-derived FG signal from the paired
   driver) proves unreliable at physical bring-up, Candidate B (Anaheim
   BLY171D-24V-4000, native Hall sensors) is the recorded fallback — at the
   cost of ≈3.4× price, ≈10× mass, and a driver-IC change (see Motor Driver
   IC section's DRV10970 comparison, which is Hall-sensor-compatible).

### Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Component Engineer | Component Engineer (AI agent) | 2026-08-31 | Proposed — T-Motor MN2206-13 KV2000 (sensorless BLDC), paired with TI DRV10983 (see Motor Driver IC section) |
| Hardware Lead | Hardware Lead (this session) | 2026-08-31 | Concur — recommend approval. Independently re-verified the load-bearing arithmetic this candidate rests on: Kt = 60/(2π·2000 RPM/V) = 4.77 mN·m/A (confirmed by direct substitution); current need for 5 mN·m target = 5/4.77 ≈ 1.05 A (confirmed); margin vs. 18 A continuous rating ≈17.1× (confirmed); flywheel target itself (100 g/30 mm/3000 RPM ⇒ I≈4.5×10⁻⁵ kg·m², L=I·ω≈14.1 mN·m·s) independently re-derived and matches both this file's and `requirements/requirements.md` §9b's figures. Toshiba TC78B009FTG evidence-quality disqualifier is well-reasoned (existence not in doubt — 3 simultaneous live distributor listings — but no primary-source datasheet text was actually read this session, correctly not treated as a blocking "no datasheet found" escalation). Escalation flag 3 (new ~12 V rail requirement) is the key finding — routing to Power Engineer now for the architecture proposal before this recommendation goes to the human. |
| Chief Engineer (Human) — required if architecture-defining/major component | Human Chief Engineer (via creator/"General Chat" session) | 2026-08-31 | **Approved** — "T-Motor MN2206-13 KV2000 + TI DRV10983, as recommended." Human independently re-verified this session: a fresh web search on both parts' specs matched this file's citations exactly, and the Kt/current-margin arithmetic was independently recomputed in Python (Kt=4.77 mN·m/A, 1.05A needed, 17.2× motor margin, 1.9× driver margin — all matching). Directive: the BEMF-sensing-degrades-below-500–1500-RPM caveat must appear as a real, tracked item in the Firmware bring-up plan and/or `validation/fmea.md`, not just this comparison report. |

---

### Rev 5 re-evaluation (3-axis scale, ×3) — T-Motor MN2206-13 KV2000 retained, maxon EC45 flat DISQUALIFIED (NRND)

> **Per REQ-508**, this is an explicit, individual re-justification of
> whether the already-approved T-Motor MN2206-13 KV2000 should be used ×3
> (one per axis), rather than switching to maxon EC45 flat (the JAXA
> reference design's own motor, part 200142) without a real reason
> (`requirements/requirements.md` §1c item 3). **Conclusion: retain
> T-Motor MN2206-13 KV2000 ×3.** maxon EC45 flat is independently
> disqualified on a real, primary-source lifecycle finding — not
> rejected merely because it's "the JAXA part."

- **Driving requirement(s)**: REQ-015 (3× independently-driven reaction
  wheels), REQ-508 (individual re-justification), REQ-021 (Cubli-style
  hard-brake maneuver — now human-confirmed Must — motivates checking
  whether the existing pairing has real headroom for a more aggressive,
  short-duration torque/current event, not just steady-state 5mN·m).

#### New finding this session: does the existing pairing have hard-brake headroom?

Independently re-derived from already-established project figures (Kt =
4.77 mN·m/A for T-Motor MN2206-13, `bom/component-selection.md`'s own
Motor section above) against the paired driver's real current rating
(TI DRV10983: 2A continuous / 3A peak per phase, DS-MTR-034 above):

```
2A continuous × 4.77 mN·m/A ≈ 9.5 mN·m  (≈1.9× the old 5mN·m steady target)
3A peak       × 4.77 mN·m/A ≈ 14.3 mN·m (≈2.9× the old 5mN·m steady target)
```

**Real, demonstrated short-duration torque headroom exists** — but this
is current/torque headroom only, not a claim about braking *dynamics*.
DRV10983 is a sensorless speed-control IC; sensorless commutation depends
on back-EMF, which is intrinsically weaker/less observable as RPM falls
during a braking event — a genuine, disclosed limitation on *how
controllably* the pairing can execute a fast, repeatable hard-brake, not
on raw torque capability. See the Motor Driver IC section's own Rev 5
subsection below for the driver-architecture implications.

#### Candidate Comparison

*(3 candidates compared — meets the ≥3 minimum.)*

| Parameter | Candidate A — T-Motor MN2206-13 KV2000 (incumbent) — ✅ RECOMMENDED | Candidate B — maxon EC 45 flat (200142, JAXA reference part) — ⚠ DISQUALIFIED | Candidate C — (no credible third motor candidate identified this session) |
|---|---|---|---|
| Sensing | Sensorless (outrunner) [DS-MTR-022] | **Hall-sensored** [DS-MTR-082] | N/A |
| Kt (torque constant) | 4.77 mN·m/A derived [DS-MTR-020] | 25.4 mN·m/A published [DS-MTR-083] — much higher torque per amp | N/A |
| Rated/continuous torque | N/A published; 18A continuous current rating [DS-MTR-019] | 57.1 mN·m continuous, 2.16A continuous current [DS-MTR-084] | N/A |
| No-load / nominal speed | ≈20,000-25,180 RPM derived credible-worst-case [DS-MTR-018 corrected] | 4390 RPM no-load / 3050 RPM nominal [DS-MTR-085] — far lower top speed | N/A |
| Rotor inertia | Not published/confirmed [known UNKNOWN, carried forward from original comparison] | 92.5 g·cm² = 9.25×10⁻⁶ kg·m² published [DS-MTR-086] — real figure available, but this is a genuinely larger, heavier rotor | N/A |
| Mass | 30g [DS-MTR-021] | 75g [DS-MTR-087] — 2.5× heavier | N/A |
| **Lifecycle/EOL** | Active [DS-MTR-023] | **NRND (Not Recommended for New Designs)** — stated directly on maxon's own current product page [DS-MTR-088] | N/A |
| Price | $18.99 qty1 (prior repo data) [DS-MTR-023] | **Live 2026 qty-3 pricing not independently confirmed this session** — the kickoff's own presented ≈$80-125/axis estimate was NOT independently re-verified against a live maxon/distributor page this session (flagged honestly, not silently repeated as confirmed) | N/A |
| Known risks | Live qty-3 pricing/stock not independently re-verified this session (flagged) | **Disqualifying**: formally NRND on maxon's own current product page — a real, primary-source lifecycle risk for a new design, independent of any cost consideration | No credible third candidate found meeting this session's rigor bar (exact part + real 2026 price/stock + primary-source electrical/mechanical data) — recorded honestly per this project's own "if fewer exist, document why" convention rather than inventing a weak filler candidate |

#### Success-probability ranking

| Rank | Candidate | Verdict |
|---|---|---|
| 1 | **T-Motor MN2206-13 KV2000 ×3 (A, incumbent)** | Real, demonstrated short-duration torque headroom (≈1.9-2.9× the old steady target) against the paired driver's own current rating; already validated in this project; no lifecycle risk. The one open concern (sensorless commutation's braking-dynamics fidelity) is a driver-architecture question, not a motor-choice problem — addressed in the Motor Driver IC section below, not by switching motors. |
| 2 (rejected) | **maxon EC45 flat 200142 (B)** | Technically compelling on paper (Hall sensing, high Kt, real published rotor inertia) — but **formally NRND on maxon's own current product page**, a real disqualifying lifecycle finding for a new Rev 5 design, independent of its ≈4× cost premium (which itself was never independently re-verified this session). This is the JAXA reference's own part, evaluated fresh per this project's own anti-copy discipline, and found to have a real, primary-source reason for rejection — not rejected merely for being the reference part. |

#### Recommendation

- **Recommended candidate**: **A — T-Motor MN2206-13 KV2000 ×3** (one per
  axis), retaining the already-approved Rev 3 part.
- **Rationale**:
  1. **Real re-justification performed** (REQ-508): the existing
     pairing's torque/current headroom was independently re-derived
     against a more aggressive event than the original steady-state 5mN·m
     target, confirming real margin (≈1.9-2.9×) rather than assuming it.
  2. **maxon EC45 flat is independently disqualified on a real, primary-
     source lifecycle finding (NRND)** — not merely "the more expensive
     option" or "not what we already have." This is exactly the kind of
     evidence-grounded disqualification this project's own culture
     requires, distinguishing "we're keeping the cheaper part" from "we
     checked the alternative and it's genuinely unsuitable for a new
     design."
  3. Reuses an already-validated, already-approved part — avoids
     re-qualifying 3× new motor hardware with no offsetting benefit once
     the JAXA reference part is disqualified on its own real merits.
- **Trade-offs accepted**:
  - Giving up maxon's Hall-sensored observability and much higher Kt — a
    real technical advantage in principle, but moot given the NRND
    disqualification; if hard-brake control fidelity genuinely proves
    inadequate with the sensorless incumbent at Circuit Design/bring-up
    time, this trade-off should be revisited against a **different**,
    non-NRND Hall-sensored motor, not by resurrecting the disqualified
    maxon part.
  - No credible third motor candidate was found this session meeting this
    project's own rigor bar — documented honestly per the skill's own
    "if fewer exist, document why" convention, rather than inventing a
    weak filler candidate.
- **Open `UNKNOWN`s**:
  1. Live 2026 qty-3 pricing and current stock for T-Motor MN2206-13 KV2000
     — not independently re-verified this session; re-verify before BOM
     lock.
  2. maxon EC45 flat's real current pricing was never independently
     confirmed this session even though it's disqualified anyway (moot,
     flagged for completeness).
  3. T-Motor MN2206-13's rotor inertia — still not published/confirmed (a
     pre-existing UNKNOWN carried forward from the original Rev 3
     comparison, not resolved this session either).
  4. Manufacturer guidance on repeated hard-brake/momentum-dump duty
     cycling for this motor — not found from a primary source; genuinely
     new territory for this project.

#### Escalation flags

1. **Not a switch, but a real re-justification with a genuine new finding**
   (NRND disqualification of the alternative) — worth the human's
   awareness even though the practical outcome (keep the incumbent) is
   the "boring" one, per this project's own discipline of not silently
   equating "we didn't switch" with "we didn't check."
2. **Hard-brake control-dynamics confidence remains only moderate** — see
   the Motor Driver IC section's own Rev 5 subsection for the driver-
   architecture implications and the DRV8316 escalation path.

#### Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Component Engineer | Component Engineer (AI agent, via parallel research sub-agent) | 2026-09-04 | Proposed — retain T-Motor MN2206-13 KV2000 ×3; maxon EC45 flat disqualified (NRND) |
| Hardware Lead | Hardware Lead (this session) | 2026-09-04 | Concur — recommend approval; hard-brake control-dynamics confidence flagged as only moderate, routed to Motor Driver IC section's own escalation |
| Chief Engineer (Human) | Human Chief Engineer | 2026-09-04 | **Approved** — "確定" (Kyosuke's own direct plain-text reply, turn 616, `session_store_sql` session `7fab99ef-5578-4d79-a9c2-b24dbcfe93be`, `2026-09-04T16:00:16.240Z`), in direct reply to a specific question naming this exact recommendation by name (turn 614, `2026-09-04T15:54:20.062Z`) — both turns independently re-verified by this session directly against the raw turn history, not accepted from a relayed summary alone. Approves retaining T-Motor MN2206-13 KV2000 ×3 and disqualifying maxon EC45 flat (NRND) as recommended. |

---

## Motor Driver IC

> **Rev 3 addition, coupled to the Motor section above.** Per the Motor
> section's own "Motor-type elimination reasoning," brushed DC and stepper
> are both eliminated as motor *types*, leaving only BLDC in contention —
> so this comparison covers only sensorless/sensored-BLDC driver ICs, not
> every driver family that exists. H-bridge (brushed-DC) driver ICs were
> researched in parallel this session (TI DRV8871, TI DRV8833, Allegro
> A4950) but are not carried into the formal comparison below and have no
> assigned Evidence IDs or datasheet metadata records, since no fact about
> them is actually relied upon anywhere in this file — recorded here only
> for process transparency, per this task's own instruction that the driver
> comparison should match whichever motor type(s) survive.

- **Driving requirement(s)**: REQ-110 (MCU shall generate a PWM/commutation
  drive signal to control the motor driver IC's speed/duty cycle — this is
  the primary control-interface fit criterion below), REQ-111 (motor driver
  IC shall include or enable overcurrent/stall protection appropriate for
  repeated bench testing by hand) together with its companion REQ-404
  (motor driver/firmware shall implement stall/overcurrent detection and a
  shutdown behavior to prevent sustained overheating during bench testing —
  REQ-111/404 are scored together below since they describe the same
  protection need split across IC vs. firmware), REQ-008/112 (RPM/tach
  feedback shall be wired to an MCU input where the motor+driver combination
  provides one — this is why tach/FG output availability is scored
  explicitly below, directly following on from the Motor section's finding
  that the recommended motor itself has no integrated sensing), REQ-108/109
  (the driver's own supply-voltage range and current rating are themselves
  primary inputs to the Power Engineer's upcoming rail/topology decision —
  same "real numbers, not guesses" mandate as the Motor section), REQ-503
  (Rev 3 ≤$75–90 USD total subsystem soft budget — the driver is a second
  line item within that, alongside the motor).
- **Constraints**: must be electrically and functionally compatible with
  the motor type(s) still in contention after the Motor section's own
  comparison — concretely, this means **sensorless-BLDC-capable** drivers
  are the primary fit (matching the recommended T-Motor MN2206-13), with
  Hall-sensored-BLDC-only drivers scored but expected to be a poor fit
  given the recommended motor has no Hall sensors to wire to one; supply
  voltage range must cover a realistic operating point for the recommended
  motor (2S–3S LiPo range, 7.4–12.6V, with an actual target rail still
  pending the Power Engineer's own decision — see Motor section Escalation
  flag 3); control interface should map cleanly onto a bare MCU PWM output
  (REQ-110) without requiring protocol translation hardware for basic
  open-loop operation (REQ-007/009); package must be at least partially
  hand-solderable given this project's small-batch/bench-assembly context
  (mirrors the MCU/Regulator sections' own package-assembly scoring);
  Rev 3 soft budget shared with the motor, not a separate ceiling.

### Candidate Comparison

*(3 candidates compared — meets the ≥3 minimum; all 3 are sensorless-or-
Hall-sensored 3-phase BLDC driver ICs, the only motor type still in
contention per the Motor section above.)*

| Parameter | Candidate A — TI DRV10983 — ✅ RECOMMENDED | Candidate B — TI DRV10970 | Candidate C — Toshiba TC78B009FTG |
|---|---|---|---|
| Manufacturer | Texas Instruments | Texas Instruments | Toshiba Electronic Devices & Storage |
| Part Number | DRV10983 | DRV10970 | TC78B009FTG |
| Motor-type compatibility | **Sensorless** 3-phase BLDC — direct match to the recommended T-Motor MN2206-13 (sensorless, DS-MTR-022) [DS-MTR-035] | **Requires Hall-effect sensors** on the motor — hard incompatibility with the recommended sensorless T-Motor MN2206-13 [DS-MTR-045] | Sensorless 3-phase BLDC per secondary-source claim — would also match the T-Motor, but this claim is **not primary-source-confirmed this session** [DS-MTR-050] |
| Supply voltage range (VM) | 8–28 V [DS-MTR-032] | 5–18 V — **hard ceiling incompatible with a 24V-nameplate motor** such as the Anaheim BLY171D-24V-4000, though not with the recommended T-Motor [DS-MTR-042] | Up to 30 V operating (36 V absolute maximum per a distributor listing) — the widest range of the 3, would cover either motor candidate [DS-MTR-049] |
| Max current rating (per phase) | 2 A continuous / 3 A peak — against the T-Motor's derived ≈1.05 A need (DS-MTR-020), this is ≈2× continuous-current margin [DS-MTR-034] | 1 A RMS continuous / 1.5 A peak — the most current-limited of the 3 candidates [DS-MTR-044] | 3 A maximum — highest of the 3, but continuous-vs-peak distinction **UNKNOWN this session** [DS-MTR-049] |
| Integrated power stage | Fully-integrated on-die power MOSFETs for all 6 switches — no external FETs needed [DS-MTR-035] | Integrated FETs, combined R_DS(on) ≈400 mΩ [DS-MTR-044] | On-die MOSFET integration **not independently confirmed this session** (typical for this device class, but not verified against a primary source) [DS-MTR-050] |
| Integrated logic regulator | **Yes** — integrated buck regulator generates the device's own 3.3V or 5V logic supply, confirming direct compatibility with this project's existing 3.3V MCU domain with no separate level-shifting hardware needed [DS-MTR-033] | Dedicated VIO pin confirms 3.3V logic-level compatibility, but no evidence of an integrated regulator generating that supply on-die [DS-MTR-043] | **UNKNOWN this session** — not extractable from secondary sources |
| Control interface | PWM duty cycle, analog voltage, or I2C — PWM path maps directly onto REQ-110 with no protocol translation needed; I2C available for optional tuning/telemetry, not required for basic open-loop speed control (REQ-007/009) [DS-MTR-036] | Hardware PWM + FR (direction) pins only — no I2C [DS-MTR-046] | PWM, analog, or I2C per secondary-source claim — **not primary-source-confirmed** [DS-MTR-050] |
| Overcurrent / stall / thermal protection (REQ-111/404) | **Two distinct mechanisms, corrected at Circuit Design (2026-09-04) — see `datasheets/evidence-log.md` DS-MTR-037's own correction annotation and DS-MTR-058/059**: (1) OCP is a **fixed, non-configurable** hardware trip (3 MIN/4 MAX A phase current), Hi-Z output, auto-clears once the fault condition itself clears — not a timed retry [DS-MTR-058]; (2) **Lock Detection** is the genuinely programmable-via-I2C, auto-retry (5s) mechanism this row originally (incorrectly) attributed to OCP — it covers stall/locked-rotor and 4 other fault classes [DS-MTR-059]. Both together satisfy REQ-111/404's substantive protection requirement; only the original mechanism-to-feature-name mapping was wrong, not the underlying "protection exists" conclusion. Exact thermal-shutdown threshold/behavior remains **UNKNOWN** (not extractable from the fetched pages this session) [DS-MTR-037] | Overcurrent protection plus locked-rotor/stall detection via absence of expected Hall-switching transitions, auto-retry timing set by an external capacitor on a RETRY pin [DS-MTR-046] | ALERT pin reported for abnormality/lock detection per secondary-source claim; specific OCP/TSD thresholds **UNKNOWN this session**, **not primary-source-confirmed** [DS-MTR-050] |
| Tach / FG output (REQ-008/112) | **Yes — hardware FG pin**, TI's own page states verbatim: "Motor speed feedback is available through either the FG pin or I2C." This is the key finding resolving REQ-008/112 for the sensorless T-Motor, since the motor itself has no integrated sensor — the driver supplies the RPM path instead. Low-RPM (spin-up) FG reliability below the BEMF-detection floor is a residual, datasheet-unresolvable integration risk [DS-MTR-038] | **Yes — hardware FG pin plus a separate dedicated RD (rotor-lock) output** — arguably the richest fault/speed signal set of the 3, but only usable given this part's own Hall-sensor requirement [DS-MTR-047] | FG output reported (open-drain, ≈5 mA sink, needs an external pull-up) plus a separate ALERT pin, per secondary-source claim — **not primary-source-confirmed** [DS-MTR-050] |
| Package / hand-solderability | 24-pin HTSSOP w/ exposed pad, 0.65mm lead pitch — leads hand-solderable with a fine-tip iron and flux; exposed pad itself needs reflow/hot-air for full rated thermal performance (partial, not full, hand-assembly constraint). θJA and exact body dimensions **UNKNOWN this session** [DS-MTR-039] | 24-pin TSSOP w/ exposed pad — same hand-solderability profile as Candidate A [DS-MTR-048] | WQFN-36 — no exposed leads at all, the **hardest to hand-solder of all 3 candidates** (realistically needs a reflow oven or hot-air rework station, not a hand iron) |
| Lifecycle / EOL | Active / "PRODUCTION DATA" per TI's own product page [DS-MTR-040] | Active [DS-MTR-048] | Active — confirmed only via simultaneous distributor stock, not a manufacturer lifecycle statement (no primary Toshiba page read this session) [DS-MTR-051] |
| Availability / lead time | In stock: DigiKey 6,500 units, Mouser 6,316 units (checked 2026-08-31) [DS-MTR-040] | In stock: DigiKey 5,130 units, Mouser 2,186 units (checked 2026-08-31) [DS-MTR-048] | In stock: DigiKey 3,808 units, Mouser 693 units, Arrow 4,000 units (checked 2026-08-31) — this 3-distributor stock breadth is itself the strongest evidence the part and its datasheet genuinely exist, despite this session's inability to read the datasheet's primary text [DS-MTR-051] |
| Reference design / EVM | **DRV10983EVM confirmed** — supports 8–28V input, PWM/analog speed control, USB2ANY-based I2C GUI for configuration/telemetry [DS-MTR-041] | **DRV10970EVM confirmed** [DS-MTR-048] | No confirmed evaluation board found this session |
| Price @ qty 1 | **≈$2.58** (DigiKey, PWPR cut-tape); ≈$2.57 (qty 100) [DS-MTR-040] | **≈$1.48–1.53** (DigiKey) — cheapest of the 3 [DS-MTR-048] | ≈$2.66 (DigiKey/Mouser); ≈$1.50 (qty 100) [DS-MTR-051] |
| Known risks / disqualifying factors | Thermal-shutdown threshold and θJA not confirmed this session (flagged, not blocking — see Open UNKNOWNs) | **DISQUALIFIED for this pairing**: hard Hall-sensor requirement is incompatible with the recommended sensorless T-Motor MN2206-13; also its 18V ceiling would exclude the Anaheim fallback motor's 24V nameplate rating if that fallback were ever exercised. Not a flaw in the IC itself — simply the wrong sensing-topology fit for this cycle's recommended motor. | **Not selected as primary recommendation.** Raw specs (widest voltage range, highest current rating) look competitive or better than Candidate A on paper, but the entire electrical/functional profile rests on a **secondary-source synthesis** this session could not independently verify against a primary Toshiba document (404 on the direct PDF link, a Mouser page timeout, and a JS-rendered Toshiba product page unreadable to this session's tooling) — see `datasheets/toshiba_tc78b009ftg_rev-unknown.md`'s own "Confidence flag" section. This is an evidence-quality gap, not a specification gap, and is why Candidate A is recommended over Candidate C despite comparable on-paper specs. |

### Recommendation

- **Recommended candidate**: **A — TI DRV10983**, paired with the Motor
  section's recommended **T-Motor MN2206-13 KV2000**.
- **Compatibility reasoning (motor+driver pairing, not two independent
  picks)**:
  1. **Voltage match**: the T-Motor is rated for 2S–3S LiPo operation
     (7.4–12.6V across nominal-to-full-charge). The DRV10983's 8–28V input
     range comfortably covers the upper half of that window with margin,
     but **undershoots the T-Motor's 2S-nominal 7.4V** — this pairing is
     only sound at a **≈12V-class operating point** (3S-equivalent), which
     is why the Motor section's Escalation flags explicitly call out a new
     ~12V rail requirement for the Power Engineer, rather than assuming the
     motor's own "nominal" voltage is what will actually be supplied.
     **Binding constraint confirmed at Circuit Design/Independent Review
     (2026-09-05/06, ISS-014, `hardware/schematic/bench-imu-01-design.md`
     Rev 4 §7.5.2)**: the reverse-polarity protection diode Circuit Design
     added to the motor input (D2) narrows this further — a 2S source
     fails to clear the DRV10983's own UVLO threshold at *typical*, not
     just worst-case, conditions once D2's forward drop is accounted for.
     **This design is 3S-only in practice, not merely "3S-equivalent
     preferred"** — 2S operation is not a supported configuration for this
     specific implementation, even though the T-Motor itself remains
     independently rated for 2S in isolation. See `hardware/
     power-budget.md`'s Rail Margin Summary for the exact corner-by-corner
     numbers.
  2. **Current match**: the T-Motor's derived torque-current need (≈1.05A
     for the 5 mN·m target, Kt = 4.77 mN·m/A) sits well inside the
     DRV10983's 2A continuous / 3A peak rating — roughly 2× continuous
     headroom on top of the ≈17× headroom already identified against the
     motor's own 18A continuous rating in the Motor section. Two
     independent margins, both generous.
  3. **Control-interface match**: the DRV10983 accepts a bare PWM duty-
     cycle input, which is exactly what REQ-110 specifies the MCU shall
     generate — no protocol-translation hardware (e.g. a separate I2C
     level shifter) is required for basic open-loop operation, keeping
     REQ-009's open-loop-only scope fence easy to honor in firmware.
  4. **Commutation-scheme match**: both parts are sensorless (180°
     sinusoidal BEMF on the driver side, standard outrunner BEMF on the
     motor side) — no Hall-sensor wiring harness is needed between the two,
     simplifying the physical interconnect versus the disqualified
     Candidate B pairing.
  5. **RPM-sensing resolution**: the DRV10983's hardware FG pin is the
     mechanism that resolves REQ-008/112 for this pairing, since the
     T-Motor itself has no integrated sensor (established in the Motor
     section). This is the single most load-bearing cross-section finding
     in this whole task — it is why the motor and driver had to be chosen
     together rather than independently.
  6. **Logic-supply convenience**: the DRV10983's integrated buck regulator
     can generate 3.3V/5V logic on-die, which may simplify (though does not
     eliminate the need for) the Power Engineer's new-rail design — this is
     offered as a data point for that HITL gate, not a decision made here.
- **Rationale** (success probability first, peak spec second):
  1. **Evidence quality, not raw specs, is the deciding factor between
     Candidate A and Candidate C.** Candidate C (Toshiba) has a nominally
     wider voltage range (up to 30V vs. 28V) and higher current rating (3A
     vs. 2A) — on paper, arguably the "stronger" part. But every one of
     those figures rests on a secondary-source synthesis this session could
     not verify against Toshiba's own primary documentation (three
     independent access failures: a 404 on the direct PDF, a Mouser page
     timeout, and a JS-rendered product page this session's tooling could
     not read). Candidate A's equivalent facts (voltage range, current
     rating, control interface, FG output) were all confirmed via a
     directly-fetched, readable TI page this same session. For a
     recommendation feeding directly into the Power Engineer's HITL gate,
     confirmed-primary-source numbers are judged more valuable than
     nominally-higher but secondary-source-only numbers.
  2. **Package/assembly risk favors Candidate A.** Candidate C's WQFN-36
     package has no exposed leads at all and realistically needs a reflow
     oven or hot-air rework station — a meaningfully worse fit for this
     project's small-batch/hand-assembly context than Candidate A's
     HTSSOP-24, whose leads are hand-solderable even though its exposed pad
     still benefits from reflow.
  3. **Reference design availability favors Candidate A decisively.** A
     confirmed DRV10983EVM exists with documented PWM/analog/I2C support;
     no evaluation board could be confirmed for Candidate C this session.
     For a first-time motor-driver bring-up on bench-test hardware, a real
     EVM meaningfully de-risks firmware/hardware bring-up.
  4. **Candidate B is disqualified on a hard compatibility fact, not a
     preference.** Its Hall-sensor requirement is incompatible with the
     recommended sensorless T-Motor; pairing them would require either
     switching to the Anaheim BLY171D fallback motor (see Motor section
     Escalation flag 4) or abandoning Candidate B, not a tunable trade-off.
     Its lowest-of-the-3 price (≈$1.48–1.53) and richest fault-signal set
     (FG **and** RD pins) are real strengths, recorded here specifically as
     the paired fallback if the Anaheim motor is ever substituted in.
- **Trade-offs accepted**:
  - *vs. Candidate B (TI DRV10970)*: gives up the lowest price of the 3
    candidates and the richest fault-signal set (FG **and** RD pins) — in
    exchange for sensorless compatibility with the recommended motor, which
    Candidate B cannot provide at all without a motor substitution.
  - *vs. Candidate C (Toshiba TC78B009FTG)*: gives up a nominally wider
    voltage range and higher current rating — in exchange for confirmed
    primary-source data, a meaningfully easier hand-assembly package, and a
    confirmed EVM. If a future session obtains and reads Toshiba's primary
    datasheet PDF and the figures hold up, Candidate C would be worth
    re-scoring — it is not disqualified on a hard technical fact the way
    Candidate B is, only on an evidence-quality and assembly-risk basis.
- **Open `UNKNOWN`s**:
  - DRV10983's exact thermal-shutdown threshold/behavior and θJA/package
    body dimensions were not extractable from the pages fetched this
    session — not judged blocking given the generous current margin
    already identified, but should be closed before Circuit Engineer
    finalizes thermal layout.
  - Whether the DRV10983's FG signal will be clean/monotonic specifically
    during this pairing's 0→3000 RPM spin-up ramp (below the typical BEMF-
    detection floor of ≈500–1500 RPM) is not resolvable from a datasheet —
    flagged as a bring-up validation item for Circuit Engineer/Firmware,
    cross-referenced from the Motor section.
  - Toshiba TC78B009FTG's entire profile in this comparison is secondary-
    source-only and explicitly not relied upon for the final
    recommendation — see this section's Escalation flags below and
    `datasheets/toshiba_tc78b009ftg_rev-unknown.md`'s own Confidence flag
    section.

### Escalation flags

1. **Architecture-defining / major component decision — requires Hardware
   Lead + human Chief Engineer approval before Circuit Engineer uses this**
   (`docs/architecture.md` §10), same as the Motor section — this is one
   coupled motor+driver recommendation, not two independent ones, and is
   explicitly **not self-approved**; see Approval table below.
2. **Evidence-confidence gap for Candidate C (Toshiba TC78B009FTG) — flagged
   explicitly, not treated as a silent gap or as a full "no datasheet
   found" escalation.** This session could not read Toshiba's primary
   datasheet PDF (404 on the direct link), a Mouser distributor page
   (request timeout), or Toshiba's own product page (JavaScript-rendered,
   unreadable to this session's fetch tooling). All of Candidate C's
   figures in the table above instead come from a secondary, AI-synthesized
   web-search source cross-referencing an alldatasheet.jp mirror. This is
   **not** escalated as a "no datasheet can be found" stop condition per
   this role's own escalation triggers, because the part and a genuine
   datasheet demonstrably exist — three independent live distributors
   (DigiKey, Mouser, Arrow) stock it as an active production part, which
   would not be true of a fictitious or unavailable part. The gap is
   recorded as a confidence/verification gap, not an existence gap, and is
   the deciding reason Candidate C was not recommended over Candidate A
   despite nominally competitive specs. A future session with working
   access to Toshiba's primary PDF should re-verify before this part is
   reconsidered for anything beyond a documented fallback.
3. **New ~12V rail requirement — repeated from the Motor section, applies
   equally to this driver.** The DRV10983's 8–28V input range only clears
   its own minimum with real margin at a ≈12V-class operating point, not at
   the T-Motor's 2S-nominal 7.4V. Rev 1/2 of this board has only a single
   3.3V rail. Flagged for the Power Engineer's own HITL-gated rail-topology
   proposal, not decided here.
4. **Thermal numbers remain partially incomplete for all 3 candidates**
   (θJA UNKNOWN for Candidate A/B, full thermal profile UNKNOWN for
   Candidate C) — flagged explicitly because the Power Engineer's own
   agent definition calls for real thermal data per candidate, and this is
   the one dimension where this comparison could not fully deliver it from
   the sources available this session. Does not block the recommendation
   given the generous current margins already identified, but should be
   closed before Circuit Engineer finalizes the driver's PCB thermal
   layout (copper pour sizing, via stitching under the exposed pad).

### Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Component Engineer | Component Engineer (AI agent) | 2026-08-31 | Proposed — TI DRV10983, paired with T-Motor MN2206-13 KV2000 (see Motor section) |
| Hardware Lead | Hardware Lead (this session) | 2026-08-31 | Concur — recommend approval. The motor+driver compatibility reasoning (voltage/current/control-interface/commutation-scheme match) is sound and the DRV10983's FG-pin RPM path is a well-justified resolution for REQ-008/112 given the motor itself has no integrated sensor. Same evidence-quality-over-raw-spec reasoning against Candidate C (Toshiba) as the Motor section — agree this is the right call for a first-time bring-up. Routing the ~12V rail requirement (Escalation flag 3) to Power Engineer now. |
| Chief Engineer (Human) — required if architecture-defining/major component | Human Chief Engineer (via creator/"General Chat" session) | 2026-08-31 | **Approved** — "T-Motor MN2206-13 KV2000 + TI DRV10983, as recommended" (same sign-off as the Motor section above — one coupled decision, independently re-verified by the human this session). |

---

### Rev 5 re-evaluation (3-axis scale, ×3) — TI DRV10983 retained as baseline; TI DRV8316 flagged as an escalation path for hard-brake fidelity

> **Per REQ-508**, this is an explicit, individual re-justification of
> whether the already-approved TI DRV10983 should be used ×3 (one per
> axis, alongside the retained T-Motor MN2206-13 KV2000 — see Motor
> section's own Rev 5 subsection above). **Conclusion: retain DRV10983 ×3
> as the baseline recommendation**, with TI DRV8316 named as a documented
> escalation path if bench characterization of REQ-021's hard-brake
> maneuver shows the incumbent's sensorless commutation is inadequate.

- **Driving requirement(s)**: REQ-015 (3× motor driver channels),
  REQ-019/REQ-021 (electromagnetic brake / Cubli-style hard-brake maneuver
  — this section's own new finding, below, is that the incumbent driver
  already has a **documented brake mode that can satisfy REQ-019 with no
  new brake hardware at all**), REQ-508 (individual re-justification).

#### New finding this session: REQ-019 (brake) may not need new hardware at all

A dedicated parallel research effort into electromagnetic brake candidates
(full detail in the new Brake section below) found that **TI DRV10983
already has a documented dynamic-braking mode**: setting the BRAKE bit
turns on all three low-side MOSFETs simultaneously, shorting the motor's
own phase windings to dissipate its stored kinetic energy — no separate
brake coil, no flyback-diode circuit, no new mechanical part. Worked
braking-torque-vs-time arithmetic (τ = ΔL/Δt, I_wheel=4.5×10⁻⁵ kg·m² from
this project's own already-established flywheel figure):

```
At 3000 RPM (ω=314.16 rad/s), L = I·ω ≈ 0.01414 N·m·s
  Stop in 50ms  → τ ≈ 0.283 N·m
  Stop in 100ms → τ ≈ 0.141 N·m
  Stop in 500ms → τ ≈ 0.028 N·m
At 6000 RPM (ω=628.32 rad/s), L = I·ω ≈ 0.02827 N·m·s
  Stop in 50ms  → τ ≈ 0.565 N·m
  Stop in 100ms → τ ≈ 0.283 N·m
```

This is a genuinely different, better outcome than the kickoff's own
framing assumed ("Electromagnetic brake — entirely new subsystem... needs
its own from-scratch Component Selection and Circuit Design") — see the
new Brake section below for the full candidate comparison and why dynamic
braking is recommended over a discrete electromagnetic brake component.

#### Candidate Comparison

*(4 candidates compared — exceeds the ≥3 minimum.)*

| Parameter | Candidate A — TI DRV10983 (incumbent) — ✅ RECOMMENDED (baseline) | Candidate B — TI DRV10970 | Candidate C — TI DRV8316 (escalation path) | Candidate D — onsemi MC33035 |
|---|---|---|---|---|
| Motor-type compatibility | Sensorless BLDC [DS-MTR-035] — matches retained T-Motor MN2206-13 | Requires Hall sensors — incompatible with the retained sensorless motor [DS-MTR-045] | Sensored **or** sensorless BLDC, MCU-controlled [DS-MTR-089] | Sensored BLDC controller (needs external MOSFET power stage) |
| Documented brake mode | **Yes** — BRAKE bit shorts all 3 low-side MOSFETs [DS-MTR-093] | Not confirmed this session | Yes, supports brake modes as part of its broader sensored/sensorless FOC control authority [DS-MTR-090] | Requires external power-stage design to implement any brake behavior |
| Control architecture | Integrated "appliance" sensorless speed controller — limited external control authority [DS-MTR-036] | Similar integrated appliance architecture, Hall-based | **MCU has direct control authority** — supports sensored/sensorless FOC/sinusoidal/trapezoid, external current sensing [DS-MTR-091] | Discrete controller IC, MCU/external logic drives commutation directly |
| Current rating | 2A continuous/3A peak per phase [DS-MTR-034] | 1A RMS/1.5A peak — too current-limited for this application [DS-MTR-044] | Higher-current family (3.0A class per TI's own product family framing) [DS-MTR-092] | Depends entirely on external MOSFET stage chosen |
| Price | ≈$2.58 qty1 (prior repo data) [DS-MTR-040] | ≈$1.48-1.53 qty1 (prior repo data) [DS-MTR-048] | **Live 2026 pricing not independently confirmed this session** | ≈$2.77 (onsemi's own product-page snippet, this session) |
| Known risks | Sensorless commutation's braking-dynamics fidelity is only moderately confident (back-EMF observability degrades at low speed during a braking event) — a real, disclosed limitation, not a blocking defect | **DISQUALIFIED**: hard Hall-sensor requirement incompatible with the retained sensorless motor (same disqualification as the original Rev 3 comparison) | Needs materially more firmware/control complexity (external FOC control loop) than the incumbent's integrated appliance approach — a real cost of the escalation path, not a free upgrade | Adds discrete power-stage design burden; not an attractive fit for this project's integrated-driver preference |

#### Success-probability ranking

| Rank | Candidate | Verdict |
|---|---|---|
| 1 | **TI DRV10983 (A, incumbent, baseline)** | Already has a real, documented brake mode satisfying REQ-019 with zero new hardware; real current/torque headroom for the required braking-torque range (0.028-0.283 N·m per the worked arithmetic above, comfortably inside its 2-3A capability against the retained motor's 4.77 mN·m/A Kt). The one open question (braking *dynamics* fidelity for a repeatable, controlled Cubli-style maneuver) is a real, disclosed limitation, not disqualifying — best resolved by bench characterization, not by pre-emptively switching. |
| 2 (documented escalation path, not primary) | **TI DRV8316 (C)** | The technically stronger choice if bench testing shows the incumbent's sensorless brake dynamics are inadequate — direct MCU control authority and sensored/FOC support would give materially better control over the braking event, at the cost of real added firmware/control complexity. Named explicitly so this path doesn't have to be re-discovered later. |
| 3 (rejected) | **TI DRV10970 (B)** | Same disqualification as the original Rev 3 comparison — Hall-sensor-only, incompatible with the retained sensorless motor. |
| 4 (not attractive) | **onsemi MC33035 (D)** | Real, historically-proven part, but requires a full discrete power-stage design this project's integrated-driver preference doesn't need. |

#### Recommendation

- **Recommended candidate**: **A — TI DRV10983 ×3**, retaining the
  already-approved Rev 3 part, **using its own documented BRAKE bit
  (dynamic braking) to satisfy REQ-019 — no new brake hardware
  recommended at this stage.**
- **Rationale**:
  1. **A genuinely simpler outcome than the kickoff's own framing
     anticipated** — REQ-019 (electromagnetic brake, "entirely new
     subsystem") may be satisfiable by a firmware-only change to an
     already-approved, already-owned part, not a new mechanical/electrical
     subsystem at all.
  2. The worked braking-torque arithmetic shows the actual torque needed
     (0.028-0.283 N·m across a 50-500ms/3000-6000RPM sweep) is well within
     what the existing motor+driver pairing's current rating can deliver.
  3. **DRV8316 is named as a real, credible escalation path** — not
     silently omitted — for if bench characterization (a future phase,
     not this one) shows the incumbent's sensorless dynamics are
     genuinely inadequate for a controlled, repeatable hard-brake
     maneuver.
- **Trade-offs accepted**:
  - Deferring a firm answer on braking-dynamics fidelity to a future
    bench-characterization phase, rather than resolving it here with no
    real hardware to test against — an honest "UNKNOWN until tested"
    disclosure, not a guess.
  - Not adopting DRV8316 now, even though it's technically stronger,
    because doing so would add real firmware/control complexity before
    there's real evidence the simpler incumbent approach is inadequate —
    consistent with this project's own "speed to a physical result"
    precedent (§9f in `requirements/requirements.md`).
- **Open `UNKNOWN`s**:
  1. Actual measured braking torque/stop-time for DRV10983's BRAKE mode on
     the real MN2206-13+flywheel system — **UNKNOWN until bench-tested**;
     this is the single most important open item for REQ-019/REQ-021's
     eventual validation.
  2. Live 2026 qty-3 pricing/stock for DRV10983 — not independently
     re-verified this session.
  3. DRV8316's live 2026 pricing/stock — not independently confirmed this
     session; moot unless the escalation path is actually exercised.

#### Escalation flags

1. **REQ-019's own scope may have just gotten materially smaller** — flag
   this explicitly for the human/Hardware Lead's own awareness, since the
   kickoff's own framing assumed a full new brake subsystem; this finding
   changes that assumption in the project's favor (simpler, cheaper), but
   should be confirmed, not silently adopted.
2. **Real bench characterization of the BRAKE-mode stop-time/torque is a
   load-bearing open item** for REQ-021's eventual safety analysis
   (REQ-409) — flagged here so it isn't lost by the time Mechanical Review
   happens.
3. **DRV8316's escalation path requires materially more firmware/control
   complexity** — a real cost, disclosed here so it isn't treated as a
   free upgrade if it's later exercised.

#### Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Component Engineer | Component Engineer (AI agent, via parallel research sub-agents — motor/driver and brake research combined for this finding) | 2026-09-04 | Proposed — retain TI DRV10983 ×3 as baseline (satisfies REQ-019 via documented BRAKE mode, no new brake hardware); TI DRV8316 named as escalation path |
| Hardware Lead | Hardware Lead (this session) | 2026-09-04 | Concur — recommend approval; bench characterization of BRAKE-mode dynamics flagged as a load-bearing open item for REQ-409's future safety analysis |
| Chief Engineer (Human) | Human Chief Engineer | 2026-09-04 | **Approved** — "確定" (Kyosuke's own direct plain-text reply, turn 616, `session_store_sql` session `7fab99ef-5578-4d79-a9c2-b24dbcfe93be`, `2026-09-04T16:00:16.240Z`), in direct reply to a specific question naming this exact recommendation by name (turn 614, `2026-09-04T15:54:20.062Z`) — both turns independently re-verified by this session directly against the raw turn history, not accepted from a relayed summary alone. Approves retaining TI DRV10983 ×3 as baseline, with TI DRV8316 as the named escalation path, as recommended. **This approval authorizes the design direction, not a safety determination**: real bench-measured BRAKE-mode stop-time/torque (REQ-021/REQ-409) remains `UNKNOWN until bench-tested`, unchanged by this approval — see the Electromagnetic Brake section's own Approval row for the same caveat, stated once and not duplicated in full here. |

---

## Motor-Rail Supervisory Controller

> **Rev 4 addition — routed by Circuit Engineer via Hardware Lead, not
> self-selected.** Independent Review of the Rev 3 motor driver subsystem
> found 3 HIGH findings (ISS-015 uncommanded-motion risk, ISS-019 unbounded
> input envelope, ISS-021 non-latching faults — `validation/open-issues.md`).
> Circuit Engineer's Rev 4 update (`hardware/schematic/bench-imu-01-design.md`
> §7.5.10) specifies the required function and ratings for a resolving part
> in full, but deliberately does not select a specific MPN — judging an
> *active* supervisory switch (the first active, not passive, protection
> element in this design) to be "a more architecturally significant choice"
> than the single-part, no-full-comparison class used for D2/D3/F1, and
> routing the selection here instead. This section is that routed selection.

- **Driving requirement(s)** (verified against `requirements/requirements.md`
  and `validation/open-issues.md` directly, not just this task's summary):
  1. **REQ-403** (Rev 3, **Must**, safety-critical/human-review-gated — the
     flywheel + mount shall not present a projectile or pinch/contact
     hazard). This part's **function #1** (default-OFF/fail-safe load-switch
     gating) is the hardware fix for **ISS-015**'s uncommanded-motion
     finding, which ties directly to REQ-403 in that finding's own text:
     DRV10983's SPEED pin factory-defaults to *active* analog-mode
     interpretation, not inert (DS-MTR-068/071), and nothing in the current
     design bounds cross-domain power-up sequencing. ISS-015's own
     Recommended Fix option 2 reads, verbatim: "add a supervisory load
     switch gating U5's VCC, enabled only once the MCU domain's own rail is
     confirmed alive" — precisely this part's role.
  2. **REQ-404** (Rev 3, Should — motor driver/firmware shall implement
     stall/overcurrent detection and a shutdown behavior to prevent
     sustained overheating). **ISS-021** found none of U5's 3 internal
     protections (OCP, Lock Detection, Thermal Shutdown) actually latch, so
     REQ-404's "shutdown" clause is not genuinely satisfied by the driver IC
     alone — this part's **function #3** (firmware-commandable latched
     cutoff) is the literal fix ISS-021's own Recommended Fix proposes:
     "...and/or a supervisory switch cuts U5's VCC ... requiring a
     deliberate re-arm." **ISS-019**'s finding (no coordinated input
     overvoltage protection upstream of U5) also bears on REQ-404, since an
     unbounded input voltage is itself a latent overheating/damage risk —
     this part's **function #2** closes that gap.
  3. **REQ-405** (Rev 3, Must, new at Independent Review from ISS-020 —
     firmware shall enforce a maximum commanded speed and command the motor
     to a safe/stopped state on exceeding it). An indirect but real tie:
     this part's enable pin is what gives firmware a genuine **physical**
     mechanism to enforce "safe/stopped state," rather than relying solely
     on a soft SPEED=0 PWM command that may not survive every fault path.
     Closing ISS-020's own max-speed/ramp-rate logic remains a Firmware/
     Mechanical Lead deliverable (§7.5.11) — not something this component
     alone resolves.
  4. **REQ-406** (Rev 3, Should, new at Independent Review **directly from
     ISS-021** — firmware shall implement a latched-fault policy on
     repeated Lock Detection events, forcing a safe/stopped state requiring
     deliberate re-arm). The most direct tie of the four: REQ-406 was
     written specifically to codify ISS-021's finding, and this part's
     function #3 is the hardware enabler §7.5.12 cross-references for
     REQ-406's firmware policy to have physical teeth, not just a software
     no-op against a driver that would auto-retry regardless.
  5. **REQ-503** (Rev 3, Should — ≤$75–90 USD **whole-board** soft budget).
     This part is a new incremental line item against that same ceiling —
     see the Recommendation section's headroom calculation below.
- **Constraints** (from §7.5.10, re-verified against the primary document
  this session, not just this task's own summary of it):
  - **Function coverage**: a single part (or a small, clearly-justified
    2-part combination) must provide all 3 of: (1) load-switch gating of
    U5's VCC with default-OFF/fail-safe logic when the enable input is
    undriven or the MCU domain is unpowered; (2) continuous overvoltage
    lockout referenced to the 9.0–13.0V binding envelope (§7.5.9),
    disabling the switch if VM_MOTOR is sensed outside it; (3) a
    firmware-commandable enable input the latched-cutoff policy (§7.5.12)
    can drive low on a declared fault, requiring deliberate re-arm.
  - **Ratings**: continuous current ≥3A (this design's own ≤3A worst-case
    operating current, §7.5.4 item 5, with margin); voltage rating ≥16V
    minimum, ideally ≥30V (covering the 9.0–13.0V envelope with margin and
    ideally matching U5's own 30V VCC absolute maximum, DS-MTR-053, so the
    switch itself is never the weakest link); low on-resistance, target
    ≤35mΩ or so, to avoid eroding the already-narrow 3S/UVLO margin
    (§7.5.2, ≈0.26V — corrected 2026-09-02, ISS-040: was ≈0.32V before
    F2's own added series drop, ISS-032 loop-back fix) any further than
    F1/D2/F2 already do; default-OFF/
    fail-safe logic sense (enable HIGH=ON) — a hard requirement per §7.5.10,
    not a preference, given REQ-403.
  - **Package / hand-solderability**: this project's own established,
    repeatedly-applied preference for hand-solderable leaded packages
    (every Rev 1–3 part selection has scored this explicitly — see e.g. the
    Motor Driver IC section's WQFN-36 disqualification-adjacent finding
    above) applies with the same weight here.
  - **Budget**: REQ-503's ≤$75–90 soft ceiling is a **whole-board** figure,
    confirmed via REQ-503's own requirements.md text and surrounding
    rationale — not a motor-subsystem-only ceiling. The Recommendation
    section's headroom calculation below therefore accounts for
    MCU+IMU+Regulator+Motor+Driver+J4+D2+D3+F1, not just this new part in
    isolation.
  - **Lifecycle/availability/reference-design**: scored per this role's
    standard process (`.github/skills/component-selection/SKILL.md`).

### Candidate Comparison

*(3 candidates compared — meets the ≥3 minimum. Candidates A and B are
dedicated eFuse/power-load-switch ICs with integrated OVP, the first real
candidate class this task's own framing called for; Candidate C is a
discrete high-side MOSFET plus a separate hot-swap/sequencing controller
(functionally the "separate comparator/OVP IC" the task's framing named),
the second class. Vendor diversity was genuinely attempted, not just
formally gestured at, but did not survive contact with the actual spec
set: onsemi's NIS5132 was ruled out as 18V-max/NRND, its NCV891330 as the
wrong device class (not a load-switch/eFuse), and its FPF2700 as lacking
adjustable OVP and being current-limited to 2A; ADI/Maxim's MAX17608/
MAX17615 were ruled out as too low-current, and its MAX17525 as
VQFN/TDFN-only with thin OVP documentation. No viable cross-vendor
single-chip alternative meeting the full spec set was found — all 3 final
candidates below are TI parts, a real research finding, not a shortcut.)*

| Parameter | Candidate A — TI TPS26631PWPR — ✅ RECOMMENDED | Candidate B — TI TPS259822ONRGER (TPS25982 family) | Candidate C — TI LM5069MM-1/NOPB + Infineon IRLZ44NPBF |
|---|---|---|---|
| Device class | Integrated eFuse / power-load-switch IC (single chip) [DS-PROT-010] | Integrated eFuse / power-load-switch IC (single chip) [DS-PROT-015] | Discrete high-side N-channel MOSFET (IRLZ44NPBF) switched/sequenced by a separate hot-swap controller (LM5069MM-1/NOPB) — a 2-part combination [DS-PROT-017][DS-PROT-019] |
| Operating voltage / absolute max | 4.5–60V operating / 67V AMR — wide margin over both the 9.0–13.0V envelope and U5's own 30V VCC AMR [DS-PROT-010] | 2.7–24V operating / 30V AMR — closely matches, essentially without margin, U5's own 30V VCC AMR; narrowest margin of the 3 [DS-PROT-015] | LM5069: 9–80V operating, widest range of the 3; IRLZ44N: 55V VDS — both comfortably exceed the envelope with margin [DS-PROT-017][DS-PROT-019] |
| Integrated / effective R_DS(on) | 31mΩ (integrated FET) — meets the ≤35mΩ target with headroom [DS-PROT-010] | 2.7mΩ — best-in-class of all 3 by a wide margin [DS-PROT-015] | ≈22mΩ @ VGS≈10V (IRLZ44N, gate charge-pumped by LM5069's own drive output) — also comfortably under target [DS-PROT-019] |
| Adjustable current-limit range | 0.6–6A via RILIM resistor — comfortably spans this design's ≥3A need [DS-PROT-010] | 2–15A — widest range of the 3 [DS-PROT-015] | Fully adjustable via an external current-sense resistor — any limit achievable, at the cost of an added sense resistor and its own power dissipation [DS-PROT-017] |
| Continuous OVP mechanism (**function #2**) | Adjustable "OVP Cut Off" via external resistor divider on a **separate, independent OVP pin** — a true lockout, not a clamp; optional factory-preset 34.3V alternative exists but is not used here (this design needs its own ≈13V threshold) [DS-PROT-011] | Adjustable, but via the **same physical EN/UVLO pin** as the enable/UVLO function — a combined, dual-purpose node, not 2 independent pins [DS-PROT-015] | Adjustable via a **separate, independent** external resistor divider referenced to LM5069's internal 2.5V reference — a true lockout, genuinely independent of the UVLO divider [DS-PROT-017] |
| UVLO mechanism | Adjustable, separate/independent pin from OVP [DS-PROT-010][DS-PROT-011] | Same EN/UVLO pin as OVP — less independent; interacting resistor-divider design [DS-PROT-015] | Adjustable via a second, fully independent external resistor divider (separate from OVLO) [DS-PROT-017] |
| Autonomous overload fault-response (secondary/defense-in-depth layer — see Recommendation for the primary function #3 mechanism) | MODE pin selects latch-off vs. auto-retry; TPS26631 specifically defaults to auto-retry with 2×IOL pulse-current tolerance (≤25.5ms) — a genuine fit for motor-inrush current profiles [DS-PROT-011][DS-PROT-012] | Latch-off / auto-retry selectable [DS-PROT-015] | LM5069-1 variant **natively latches** on an overload fault (the sibling "-2" variant auto-restarts instead, not used here) [DS-PROT-017] |
| Default-OFF/fail-safe native pin bias (**function #1** — the hard REQ-403-driven requirement) | SHDN pin: internal 1MΩ pull-up to 2.7V, **floating defaults ON** — needs an external pull-down resistor to invert (standard, low-risk, well-precedented mitigation; Circuit Engineer's job to size) [DS-PROT-013] | EN/UVLO pin: **no internal bias at all** — floating is **undefined**, not merely wrong-direction; also needs an external pull-down, complicated by the pin's dual EN+UVLO duty [DS-PROT-016] | LM5069's enable/UVLO comparator: **floating natively defaults OFF** — the cleanest native match of the 3, no external resistor needed purely to invert an opposing bias [DS-PROT-018] |
| Function coverage summary (per §7.5.10's 3 functions) | **All 3 met.** #1 via SHDN + a required external pull-down resistor; #2 via the independent OVP pin/divider; #3 via SHDN driven low by firmware (MODE-pin auto-retry as a secondary layer) | **All 3 met**, but #1's mitigation is less clean (undefined float, not just wrong-direction) and #2 shares a pin with UVLO — both real design-cleanliness costs vs. Candidate A | **All 3 met**, with #1 satisfied **natively** (no extra resistor needed purely for default-off) and #2/UVLO on fully independent dividers — the most "by-the-book" hot-swap-controller implementation of the 3, at the cost of 2 parts instead of 1 and a higher unit price |
| Package / hand-solderability | HTSSOP-20 ("PWP") — leaded, hand-solderable, matches this project's established package preference [DS-PROT-014] | **VQFN-24 ("RGE") ONLY — no HTSSOP/SOIC/other leaded option exists for this family**, independently confirmed via a dedicated search this session — a real DFM/hand-assembly risk per this project's repeatedly-applied preference [DS-PROT-016] | LM5069 in VSSOP-10 ("MME") + IRLZ44N in TO-220 — both leaded/through-hole; TO-220 is arguably the single easiest package to hand-solder anywhere in this whole comparison [DS-PROT-018][DS-PROT-019] |
| Lifecycle / availability | In stock at DigiKey, ships same day (checked 2026-09-08); no explicit manufacturer "Active"/"NRND" statement independently re-read this session [DS-PROT-014] | Live TI ordering/part-details page found and in stock per prior research; no explicit "Active"/"NRND" statement independently re-read this session [DS-PROT-016] | LM5069MM-1/NOPB: live DigiKey listing found and priced [DS-PROT-018]; IRLZ44NPBF: Active/current, widely available, not obsolete, per Infineon's own product page [DS-PROT-019] |
| Reference design / EVM | **TPS26630-33EVM confirmed** — TI's own EVM documentation explicitly states TPS26631RGE can be substituted onto this board "when specifically evaluating the TPS26631," a direct, named-part confirmation [DS-PROT-020] | **No exact-part EVM found.** TPS259824OEVM (a close sibling device) is the nearest published stand-in, described as "pin- and function-compatible for most use cases" — real but secondary evidence, not a named-part confirmation [DS-PROT-021] | **LM5069EVM-627 confirmed** for the controller portion, with onboard UVLO/OVLO/current-limit/fault-timer adjustment jumpers directly relevant to this design's divider-sizing needs — covers LM5069 only, not the complete 2-part combination as this design would build it [DS-PROT-022] |
| Price @ qty 1 | **$4.52** (TPS26631PWPR, DigiKey, cut-tape) + ≈$0.15–0.30 in low-value support resistors (SHDN pull-down, RILIM, OVP/UVLO dividers) ⇒ **≈$4.7–4.8 total**; $3.43 (qty 10), $2.86 (qty 100) for the chip alone [DS-PROT-014] | **$4.29** (TPS259822ONRGER, DigiKey) + similar support-resistor cost ⇒ **≈$4.4–4.6 total** [DS-PROT-016] | **$4.39** (LM5069MM-1/NOPB) + **$1.80** (IRLZ44NPBF) + ≈$0.30–0.60 in passives (2 independent resistor dividers + a current-sense resistor — more parts than Candidates A/B need) ⇒ **≈$6.5–6.8 total**, priciest and highest parts-count of the 3 [DS-PROT-018][DS-PROT-019] |
| Known risks / disqualifying factors | Required external pull-down resistor for default-OFF is a real, but low-risk and well-precedented, added mitigation (see Escalation flags). Exact UVLO/OVP threshold ranges, PGOOD/FLT fault-reporting granularity, and thermal data (θJA) not confirmed this session (flagged, not blocking — see Open UNKNOWNs) | **Package is a real, project-relevant disadvantage**: VQFN-24-only, no leaded option, against this project's own repeated hand-solderability preference. Combined EN/UVLO pin is a design-cleanliness cost (harder to tune UVLO and default-off state independently). Best raw R_DS(on)/current-limit-range of the 3, but not enough to outweigh the package risk given this project's own established precedent (mirrors the WSON regulator and WQFN-36 driver non-selections) | **Not disqualified on any hard technical fact** — every function is met, several more cleanly than Candidate A (native default-off, fully independent dividers). Not recommended primarily on **parts-count and price**: 2 ICs instead of 1, more passives (2 full dividers + a current-sense resistor vs. Candidate A's simpler pull-down/RILIM/one divider set), and the highest unit price of the 3 (≈$6.5–6.8 vs. ≈$4.7–4.8) — a real but not dramatic (~$2/unit, not ~2×) price gap that was weighed carefully, not glossed over |

### Recommendation

- **Recommended candidate**: **A — TI TPS26631PWPR** (TPS2663x family),
  gating U5's (TI DRV10983) VCC supply.
- **Whole-board BOM budget headroom (REQ-503)**: REQ-503's ≤$75–90 USD
  ceiling is scoped to the **whole board**, not just this new part or even
  just the motor subsystem (confirmed directly against `requirements.md`'s
  own text and surrounding rationale). Summing the parts already committed
  and priced elsewhere in this file — MCU ≈$2.83 [DS-MCU-018], IMU ≈$4.23
  [DS-IMU-012], Regulator ≈$0.45 [DS-PWR-009], Motor ≈$18.99 [DS-MTR-023],
  Motor Driver IC ≈$2.58 [DS-MTR-040] — plus the motor-rail parts already
  specified in the design document's own parts list and freshly priced
  this cycle — J4 ≈$0.77 [DS-CONN-006], D2 ≈$0.48 [DS-PROT-007], D3
  ≈$0.273 [DS-PROT-008], F1 ≈$1.62 (a **pricing proxy** via the active
  30R500UF replacement, since the document's own specified 30R500U appears
  obsolete — Escalation flag 5) [DS-PROT-009] — gives a **whole-board
  committed subtotal of ≈$32.22** before this new part. Adding Candidate
  A's own **≈$4.7–4.8** total (chip + support resistors, from the
  Candidate Comparison table's Price row) brings the running whole-board
  subtotal to **≈$37.0**, leaving **≈$38–53 of headroom** against REQ-503's
  $75–90 ceiling. This figure explicitly **excludes**: (1) not-yet-itemized
  trivial passives elsewhere on the board (a real but likely small, <$2–3,
  unaccounted gap — honestly flagged, not guessed away); (2) PCB
  fabrication, enclosure, and any connectors/wiring beyond J4; (3)
  assembly/labor. None of these are judged large enough to threaten even
  the $75 floor of REQ-503's range, but they are not zero, and are
  recorded here rather than silently assumed away.
- **Function-coverage confirmation (the 3 required functions from §7.5.10,
  addressed explicitly since this is the safety-relevant crux of the whole
  task)**:
  1. **Function #1 — load-switch gating, default-OFF/fail-safe**: **Met,
     with one required added part.** TPS26631's SHDN pin natively biases
     the switch **ON** when floating (internal 1MΩ pull-up to 2.7V,
     DS-PROT-013) — the *opposite* of REQ-403's fail-safe direction. This
     is not a disqualifying flaw, but it does mean Circuit Engineer **must**
     add an external pull-down resistor from SHDN to GND, sized to reliably
     override the internal pull-up, so that an unpowered MCU domain or a
     tri-stated/unconfigured GPIO reliably reads SHDN low (switch OFF) while
     an active-high GPIO drive can still easily override it (switch ON).
     This is a standard, low-risk, well-understood biasing technique — not
     a novel workaround — but it is a genuinely required schematic addition,
     not something to silently assume away. **Flagged explicitly in
     Escalation flags below.**
  2. **Function #2 — continuous OVP referenced to 9.0–13.0V**: **Met
     natively.** TPS26631's OVP pin supports an adjustable "OVP Cut Off"
     via an external resistor divider — a true lockout (the switch
     disables outside the programmed window), not merely a transient
     clamp, and **independent** of the UVLO pin (unlike Candidate B). This
     directly closes ISS-019's residual gap (no coordinated input
     overvoltage protection existed upstream of U5). Exact divider values
     to hit the 9.0–13.0V window are Circuit Engineer's to size — the
     mechanism itself is confirmed present and adjustable.
  3. **Function #3 — firmware-commandable latched cutoff**: **Met, via a
     reframing worth stating explicitly.** This function is fundamentally a
     **firmware-implemented policy** — the MCU drives SHDN low and holds it
     low until a deliberate re-arm event, exactly as REQ-406/§7.5.12
     describe — not necessarily an autonomous hardware-native latch feature
     of the chip itself. All 3 candidates in this comparison satisfy this
     via nothing more than a simple, always-available enable/SHDN/UVLO
     pin; TPS26631's own MODE-pin-selectable auto-retry behavior is a
     valuable **secondary, defense-in-depth** layer (it independently
     bounds the inrush/overload response even before firmware ever gets
     involved), not the primary mechanism this function relies on. This
     reframing matters because it means function #3 does **not** meaningfully
     differentiate the 3 candidates — Candidate C's native hardware latch
     (LM5069-1) is a nice-to-have, not a requirement-closing advantage,
     since firmware has to implement the counted-retries/deliberate-re-arm
     policy (REQ-406) regardless of which candidate is chosen.
- **Rationale** (success probability first, peak spec second):
  1. **Package/hand-solderability is the single most decisive factor
     against Candidate B.** TPS25982's best-in-class 2.7mΩ R_DS(on) and
     2–15A current-limit range are genuinely superior on paper, but it is
     **only available in a 24-pin VQFN package** — no leaded alternative
     exists for this family. This project has repeatedly, consistently
     scored leadless QFN/WSON/DFN packages as a real hand-assembly risk
     (the WSON regulator candidate and the WQFN-36 motor-driver candidate
     were both scored down partly on this same basis) — this is not a new
     standard invented for this part, it is this project's own established
     precedent applied consistently.
  2. **Single-chip simplicity favors Candidate A over Candidate C.**
     Candidate C (LM5069 + IRLZ44N) meets every function, several of them
     more cleanly than Candidate A (a natively default-OFF enable pin, and
     fully independent UVLO/OVLO dividers instead of Candidate A's
     independent-but-still-two-pins design) — it is a genuinely strong,
     not merely "adequate," alternative. But it is 2 ICs instead of 1, needs
     more passives (2 full resistor dividers plus a current-sense resistor,
     versus Candidate A's pull-down + RILIM + one divider set), and is the
     most expensive of the 3 (≈$6.5–6.8 vs. ≈$4.7–4.8 per unit) — more BOM
     lines and more resistor-divider engineering surface for Circuit
     Engineer to get right, for a price premium that is real (~$2/unit)
     though not dramatic (not ~2× as an earlier, less-precisely-sourced
     LM5069 price estimate had suggested — see the LM5069 datasheet
     record's own correction note).
  3. **Direct applications-section fit is corroborating, not decisive,
     evidence.** TI's own TPS2663x datasheet Applications section names
     "Motor drives – CNC, encoder supply" explicitly (DS-PROT-012) — a
     genuine, on-point signal this device class is marketed for exactly
     this use case. This is treated as supporting evidence alongside the
     package/simplicity/price reasoning above, not as the primary
     justification on its own.
  4. **Reference design availability favors Candidate A over Candidate B.**
     A real, TI-published EVM (TPS26630-33EVM) exists and explicitly names
     TPS26631 as a supported substitution (DS-PROT-020) — stronger evidence
     than Candidate B's close-sibling-only EVM stand-in (DS-PROT-021).
     Candidate C's LM5069EVM-627 (DS-PROT-022) is also real and relevant,
     but covers only the controller half of a 2-part combination.
- **Trade-offs accepted**:
  - *vs. Candidate B (TI TPS259822ONRGER / TPS25982)*: gives up
    substantially better R_DS(on) (31mΩ vs. 2.7mΩ) and a wider adjustable
    current-limit range (0.6–6A vs. 2–15A, though both comfortably cover
    this design's actual ≥3A need) — in exchange for a hand-solderable
    leaded package instead of a VQFN-only part, and independent (not
    shared) OVP/UVLO pins.
  - *vs. Candidate C (TI LM5069MM-1/NOPB + Infineon IRLZ44NPBF)*: gives up
    a natively default-OFF enable pin (requiring an added external
    pull-down resistor instead) and fully independent UVLO/OVLO dividers
    (Candidate A's UVLO and OVP pins are independent of each other, but
    each individually still shares board-level design attention with the
    same single-chip architecture) — in exchange for a single-chip
    solution with fewer BOM lines, less resistor-divider engineering
    surface, and a lower unit price (≈$4.7–4.8 vs. ≈$6.5–6.8).
- **Open `UNKNOWN`s** (deferred to Circuit Engineer's detailed design
  phase, not blocking this recommendation):
  - Exact UVLO pin threshold range/accuracy and OVP pin threshold
    range/accuracy for TPS26631 — needed to actually size the resistor
    dividers for the 9.0–13.0V envelope — **UNKNOWN this session**; a
    working primary-PDF read (this session's tooling could not
    text-extract the datasheet PDF) would close this.
  - Exact resistor-divider topology — whether OVP/UVLO can reasonably share
    any sense network or need fully separate dividers — is a genuine
    Circuit-Engineer-level schematic decision, explicitly **not** decided
    here.
  - PGOOD/FLT pin exact fault-reporting granularity (which specific fault
    classes each pin reports, timing) — **UNKNOWN this session**, relevant
    to how firmware distinguishes an OVP-triggered shutdown from a
    current-limit-triggered one.
  - Thermal data (θJA, package power dissipation limits) — **UNKNOWN this
    session**, same caveat pattern already applied to DRV10983/DRV10970 in
    the Motor Driver IC section above.
  - Exact SHDN pull-down resistor value — intentionally left to Circuit
    Engineer, since it depends on board-level leakage/coupling assumptions
    this role has no basis to guess at.

### Escalation flags

1. **Architecture-defining / major component decision — requires Hardware
   Lead + human Chief Engineer approval before Circuit Engineer uses this**
   (`docs/architecture.md` §10). This recommendation is explicitly **not
   self-approved** — see Approval table below, both rows marked Pending.
2. **Safety-relevant, not merely architecturally-significant** — this part
   directly closes 3 HIGH Independent Review findings (ISS-015/019/021)
   tied to REQ-403 (safety-critical, human-review-gated) and its companion
   REQ-404/405/406. The same elevated scrutiny REQ-403's own HITL gate
   calls for elsewhere in this design applies to this component choice.
3. **Evidence-category taxonomy deviation — flagged, not silently
   substituted.** This task's own framing suggested filing new Evidence IDs
   under `PWR` or `MTR`. This section instead uses a **new `PROT` category**
   (DS-PROT-007 through DS-PROT-022 this cycle), for a specific, stated
   reason: `PWR` has, in this project's history to date, been used
   exclusively for voltage-conversion parts (LDO/buck regulators); `MTR`
   has been used exclusively for parts intrinsic to the motor's own drive
   electronics (the motor and its driver IC, per `docs/architecture.md`
   §6.3's own "MTR (motor driver)" definition). `PROT` was already
   established in this same design cycle specifically for this same
   VM_MOTOR rail's protection components (D2/D3/F1) — a supervisory
   gating/OVP controller is a more precise semantic fit there than either
   suggested option. Category codes are not role-exclusive in this
   project's history (multiple agent roles have added rows to the same
   category before), so this is a considered judgment call, not a process
   violation — **flagged here explicitly for Hardware Lead to confirm or
   override**, not treated as a foregone conclusion.
4. **Required external pull-down resistor on SHDN — a real, required
   schematic addition, not a hidden assumption.** TPS26631's native SHDN
   bias is backwards relative to this design's fail-safe requirement (see
   Recommendation, function #1). The mitigation is standard and low-risk,
   but it must actually appear in Circuit Engineer's schematic — recorded
   here so it cannot be silently dropped between this recommendation and
   implementation.
5. **Incidental finding — F1 (Littelfuse 30R500U) appears obsolete.**
   Discovered while sourcing real prices for the already-committed
   motor-subsystem parts to compute this section's BOM headroom figure
   (below); no live distributor stock/pricing could be found for the exact
   30R500U part number specified in the design document's parts list. The
   active replacement, 30R500UF, was used only as a **pricing proxy**
   (DS-PROT-009) — this is **not** a substitution of the design document's
   own specified part, which is out of this role's edit scope to change.
   Flagged for Hardware Lead/Circuit Engineer awareness; may warrant a
   future-revision part re-selection.
6. **Remaining technical UNKNOWNs must be closed before Circuit Engineer
   finalizes the schematic** (see Recommendation's Open UNKNOWNs list) —
   most notably the exact UVLO/OVP threshold ranges needed to size the
   9.0–13.0V divider network, and thermal data for PCB layout purposes.

### Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Component Engineer | Component Engineer (AI agent) | 2026-09-08 | Proposed — TI TPS26631PWPR (TPS2663x family), gating U5's VCC, with a required external SHDN pull-down resistor (Escalation flag 4) and Circuit-Engineer-sized OVP/UVLO resistor dividers per §7.5.10. See Escalation flags 1–3 for items requiring Hardware Lead/human confirmation before this is used downstream. |
| Hardware Lead | Hardware Lead (this session) | 2026-08-31 | Concur — recommend approval. Function coverage (default-OFF/fail-safe load-switch gating, continuous OVP referenced to the 9.0–13.0V envelope, firmware-commandable latch enforcement point) confirmed against §7.5.10's requirements; the SHDN native-bias caveat is real and must be addressed at Circuit Design (external pull-down). |
| Chief Engineer (Human) — required if architecture-defining/major component | Human Chief Engineer (via creator/"General Chat" session) | 2026-08-31 | **Approved — "TPS26631PWPR confirmed."** Human independently re-verified via fresh web search: TPS25982 confirmed genuinely QFN-only (no HTSSOP variant exists, e.g. TPS259824LNRGET/TPS259827ONRGET); TPS26631PWPR confirmed 20-pin HTSSOP eFuse (4.5–60V, 6A, OVP/UVLO/adjustable current limit) at ≈$4.52/unit (close to this file's ≈$4.70–4.80 figure — a pricing-tier/date difference, not a discrepancy) with a genuine internal ≈440kΩ EN pull-up, independently confirming the "defaults ON, needs external pull-down for fail-safe" caveat exactly as flagged. Circuit Engineer to implement: the load switch + external EN pull-down (fail-safe-OFF direction) + OVP/UVLO dividers, in a new Rev 5. |

## Free-Rotation Support Mechanism (1-Axis Attitude Rig)

> **Rev 4 addition.** This section is a **new mechanism category**, not a
> new electronic part — the first non-electronic subsystem this file has
> ever compared. It exists because Rev 3's own mechanical design mounts the
> board+motor+flywheel assembly **rigidly** to a fixed bench enclosure
> (confirmed via repo-wide search: zero "pivot"/"gimbal"/"free-rotat[ing]"
> mentions anywhere in `hardware/mechanical/**` before this revision) — so
> no reaction-wheel torque could ever produce an observable attitude change
> under that design. This section compares candidate mechanisms; it does
> **not** perform Mechanical Design/CAD work on whichever one is chosen —
> that is explicitly deferred to a future phase, after human architecture
> approval (`requirements/requirements.md` §1b).
>
> **Revised 2026-09-01 per direct human priority clarification**
> (`requirements/requirements.md` §9f): the actual driving goal is **speed
> to a real, physical, demonstrable result** — 1-axis was deliberately
> chosen over 3-axis specifically because it's the *faster* path to
> something real, not just the more careful one. This section is scored
> accordingly: fastest-to-build (bolt-on-ready, no custom fabrication, no
> long lead time) is weighed **above** peak friction margin, and this
> section itself is kept lean rather than an exhaustive options survey.
> Rev 3's already-approved motor+flywheel selection is unaffected — not
> reopened or re-litigated anywhere below.

- **Driving requirement(s)**: REQ-011 (the core capability — free rotation
  about ≥1 axis, friction low enough for a measurable response), REQ-012
  (angular-travel target, still an open human question), REQ-113 (rotating
  electrical interface compatible with the chosen mechanism), REQ-310 (real
  assembly mass/footprint the mechanism must accommodate), REQ-311
  (integrates additively with the already-Design-Complete Rev 3 enclosure),
  REQ-407/408 (new hazard shapes; explicit non-extension of REQ-403/
  MISS-016's disposition), REQ-505 (soft BOM ceiling, proposed ≤$30–50).
- **Constraints**: bench-test prototype, not flight hardware — a real
  micro-gravity-style free-floating rig is not required (requirements.md §8
  Assumptions); total rotating-assembly mass is a fresh ESTIMATE this
  revision computed since Rev 3 never estimated the enclosure's own plastic
  mass (worked below); the reaction wheel's own torque output is already
  fixed by Rev 3's approved Component Selection (REQ-007's ≥5 mN·m
  continuous target, T-Motor MN2206-13 KV2000, Kt=4.77 mN·m/A — see Motor
  section above) — **not re-litigated or reopened here**, only used as the
  "torque budget" candidate mechanisms are compared against; REQ-505's soft
  ≤$30–50 ceiling is separate from REQ-503's already-spent Rev 3 motor-
  subsystem budget; **speed to a physical, demonstrable result is the
  primary scoring criterion this pass** (human-confirmed, §9f above),
  ahead of peak friction margin.

### Worked figures this comparison depends on (shown once, referenced below)

**Total rotating-assembly mass (ESTIMATE, new this revision)**: Rev 3's
board+motor+flywheel subtotal is ≈149–150g, CONFIRMED-derivation
(`hardware/mechanical-interface.md` §B7). The enclosure's own plastic mass
was never estimated in Rev 3 (explicitly excluded there as "additional").
This revision computes a first fresh estimate: treating the real assembled
envelope (111.4×170.6×49.0mm, `bench-imu-01-dimensional-spec.md`) as a
thin bounding-box shell at the design's own established `min_wall_t`=2.0mm
[`bench-imu-01-enclosure.scad` line 209] —

```
surface area  = 2×(111.4×170.6) + 2×(111.4×49.0) + 2×(170.6×49.0) mm²
              = 38009.7 + 10917.2 + 16718.8 = 65645.7 mm² ≈ 656.5 cm²
volume        = 656.5 cm² × 0.20 cm ≈ 131.3 cm³
mass          = 131.3 cm³ × 1.27 g/cm³ (Prusament PETG density [DS-MTL-004])
              ≈ 167g (gross bounding-box figure)
```

Real cutouts (connector/LED/header-bay openings) reduce this; real internal
ribs/bosses/tabs add back — judged to roughly offset, so this revision
proposes **≈130–170g** for the enclosure alone. **Total rotating-assembly
ESTIMATE: ≈280–320g**, call it **~300g representative**, up to a
conservative **~350g** bound. This is the same figure recorded in
`requirements/requirements.md` REQ-310 — shown here with full working since
Component Selection is where mechanism candidates actually get compared
against it.

**Platform angular-rate physics finding (ESTIMATE, new this revision,
independently cross-checked by the creator/"General Chat" session)**: using
the same conservation-of-angular-momentum relation this project's own Motor
section already implicitly relies on (ω_platform = −(I_wheel/I_platform)·
ω_wheel, the identical equation the Charles' Labs precedent below documents
for its own build) —

```
I_wheel    = 4.5×10⁻⁵ kg·m² (established, flywheel §9b/B2)
I_platform ≈ m_platform × r_gyration²   (rectangular-plate approximation,
             m_platform ≈ 200g = board+motor+enclosure, EXCLUDING the
             flywheel's own separately-counted inertia;
             r_gyration = sqrt((a²+b²)/12), a=0.1114m, b=0.1706m
             = sqrt(0.041514/12) ≈ 0.0588m)
           ≈ 0.200 kg × (0.0588 m)² ≈ 6.9×10⁻⁴ kg·m²

ratio I_wheel/I_platform ≈ 0.065  (≈1:15)
```

Illustrative operating points (ω_wheel → ω_platform):

| Commanded wheel speed | ω_wheel (rad/s) | ω_platform (rad/s) | ω_platform (°/s) |
|---|---|---|---|
| 30 RPM (≈1% of REQ-007's 3000 RPM ceiling) | 3.14 | 0.204 | ≈12°/s — gentle, easily observed |
| 300 RPM (≈10% of ceiling) | 31.4 | 2.04 | ≈117°/s — brisk but manageable |
| 3000 RPM (REQ-007's full ceiling) | 314.2 | 20.4 | ≈1170°/s (≈3.25 rev/s) — extreme if commanded all at once |

The creator/"General Chat" session independently re-derived this across a
broader 250–450g mass / 0.06–0.08m characteristic-radius sweep, getting
inertia ratios of ≈1:20–1:64 and platform rates of ≈280–900°/s at the full
3000 RPM point — same order of magnitude, confirming this is not an
arithmetic error. **This is why REQ-012/013 propose small, deliberately
incremented speed commands rather than driving straight to REQ-007's
ceiling**, and why REQ-407 flags a fast-spinning free platform as a new
hazard shape. It also answers this task's own question of whether the
onboard IMU gyro suffices: BMI270's programmable FSR (±125 to ±2000 dps
across 5 ranges [DS-IMU-002]) comfortably spans the full ≈12–1170°/s
illustrative range — the sensor is not a gap; FSR range selection (start
wide, narrow once characterized) is the real practical consideration.

### Candidate Comparison

*(4 candidates compared — exceeds the ≥3 minimum. Candidate D's treatment
below is intentionally condensed relative to A/B/C, per the human's own
"keep this lean" instruction — it was never a realistic contender for this
bench cycle on cost/complexity grounds alone, so it doesn't need the same
depth as the 3 candidates actually in contention.)*

| Parameter | Candidate A — BC Precision 4LS-3 "Lazy Susan" turntable bearing — ✅ RECOMMENDED | Candidate B — Dual 608ZZ ball-bearing vertical-shaft pivot (documented alternative) | Candidate C — Torsion wire/fiber suspension | Candidate D — Air bearing — ⚠ NOT RECOMMENDED (condensed) |
|---|---|---|---|---|
| Source / manufacturer | BC Precision (retail turntable-bearing hardware) [DS-BRG-001] | BC Precision (608ZZ miniature ball bearing ×2) [DS-BRG-002] + generic M8 threaded rod/nuts (hardware-store item, not individually sourced) | Generic thin steel/fishing-line wire or fiber (no single manufacturer — a material choice, not a product) | EyasSat commercial unit [DS-BRG-005] or a DIY 3D-printed build + air compressor |
| Type / mechanism | Full-diameter ring ball bearing, two stamped plates + captive ball race, mounts flat under a platform | 2× deep-groove ball bearings on a vertical M8 shaft — a custom-built point pivot | Thin wire/fiber the whole assembly hangs from; twists rather than spins on bearings | Thin compressed-air film between precision-fit surfaces |
| Size / bore or race diameter | 4 in (≈101.6mm) nominal OD; race/ball-circle diameter ESTIMATE ≈90mm (not manufacturer-published); 2.170 in center hole; 5/16 in (≈7.9mm) thick [DS-BRG-001] | 8mm bore × 22mm OD × 7mm width each [DS-BRG-002] | Wire diameter a free design choice (thinner = lower friction/stiffness, weaker) — no fixed size | Not detailed on the product listing [DS-BRG-005] |
| Load capacity | 300 lb (≈1334.5N) [DS-BRG-001] | Static (basic) load 1370N, dynamic 3300N, **each** [DS-BRG-002] | Depends on wire gauge/material — a real design variable, not fixed | Not load-capacity-limited at this scale (air-film pressure, not a bearing rating) |
| **Load-capacity margin vs. ≈300g (2.943N) representative assembly weight** | ≈453× (1334.5N/2.943N) | ≈466× (1370N/2.943N, static) | N/A (not a bearing-load question) | N/A |
| **Estimated friction torque** (SKF/Koyo simplified bearing-friction model, M=0.5·μ·P·d, μ≈0.0013 typical for deep-groove ball bearings [DS-BRG-003]; P=3.978N at the current ≈405.55g actual rotating-assembly mass — updated 2026-09-15 per MISS-029, cross-referencing `bench-imu-01-dimensional-spec.md` §18.3/C3's Rev 4/4.1 figures rather than this section's own original ≈300g placeholder; applied as a simplification — a true thrust-loaded calc remains a refinement for a future pass, not resolved here) | M ≈ 0.5×0.0013×3.978N×90mm ≈ **0.233 mN·m** (ESTIMATE, race-diameter figure itself is an estimate) | M ≈ 0.5×0.0013×3.978N×8mm ≈ **0.021 mN·m** (ESTIMATE) — best of all 4, ≈11× lower than Candidate A because torque scales with bore diameter for the same load | Negligible by physical design (no rolling-element friction at all) — but a **restoring torque** exists instead (wire's own torsional stiffness), a fundamentally different limiting factor, magnitude UNKNOWN until a specific wire is chosen | Negligible by design |
| **Margin vs. REQ-007's ≥5 mN·m torque budget** | ≈21.5× (5/0.233) | ≈242× (5/0.021) — best margin of the 2 bearing candidates | Not comparable the same way — see restoring-torque note above; a wire loose enough for negligible restoring torque may not support the current ≈405.55g weight rigidly, a real design trade-off | Not a limiting factor |
| Continuous/multi-turn rotation capability | Yes — full 360°, unlimited, matches REQ-012's proposed default directly | Yes — full 360°, unlimited (with a suitable tether/slip-ring per REQ-113) | **No** — bounded twist only (a few full turns at most before wire damage/plastic deformation); cannot sustain the extreme ≈1170°/s continuous-spin scenario the physics finding above shows is possible at REQ-007's full ceiling | Yes |
| Custom design/build work required | **None** — bolt-on-ready, complete off-the-shelf assembly; platform simply sits on top | **Real** — needs a Mechanical-Lead-designed shaft/mount in a future phase; the assembly's CG must sit near the shaft axis, a genuine integration constraint given Rev 3's off-center two-bay footprint (flagged, not resolved here) | **Real** — needs a suspension-point fixture above the rig and a way to route the tether; simpler geometry than B but a taller support structure | **Substantial** — precision air-gap surfaces + air supply, well beyond this project's demonstrated (3D-printing-only) fabrication capability |
| Reference design / prior art | None found for reaction-wheel/attitude-demo use specifically — a generic-purpose turntable bearing | **Exceptionally strong, directly analogous** — Charles' Labs' own "Reaction Wheel Attitude Control" one-axis satellite-simulator build uses exactly this (2× 608ZZ bearings on an M8 threaded rod) for its free-spinning platform [DS-BRG-004] — the closest real-world precedent found for this project's own exact goal | General physics-demonstration precedent for angular-momentum conservation exists, but no specific powered-reaction-wheel build using this exact suspension approach was found this session | Real, at professional/research scale — EyasSat targets CubeSat ADCS coursework [DS-BRG-005]; full commercial testbeds run $90,000–$185,000 [DS-BRG-006] |
| Price | **$13** (qty 1) [DS-BRG-001] | **≈$15.50** (2× $7.75 bearings) + ≈$3–5 hardware store M8 rod/nuts ≈ **$18–21** [DS-BRG-002] | ≈$0–5 (wire/fiber spool, likely already on hand) | **$1,249** commercial [DS-BRG-005]; DIY still realistically "a few hundred dollars" once a compressor is counted |
| % of proposed REQ-505 ≤$30–50 ceiling | ≈26–43% | ≈36–70% (at qty-1, no-discount pricing) | ≈0–17% | **≥2,500%** commercial; DIY still likely 500–1,000%+ |
| Known risks / disqualifying factors | Oversized/generic for this scale — "suggested top diameter 12–25 in" is a stability *suggestion* for the bearing's typical (much heavier furniture-class) use case, not a hard requirement at ≈300g; open integration question for the future Mechanical Design phase, not resolved here. No reaction-wheel-specific prior art — a deliberate trade-off this round, per §9f | Requires the assembly's CG to sit near the shaft axis — a real, currently-unresolved integration constraint. Not disqualifying, but a genuine future-design-work cost, which is why A is now primary this round | **Not primary this cycle**: cannot do continuous/multi-turn rotation, which the physics finding above shows may genuinely be needed; also complicates the electrical tether. Retained as a low-cost first-sanity-check option only | **Not viable this cycle on cost/complexity grounds** — real gold-standard fidelity, but ≥25–80× this section's proposed BOM ceiling and needs fabrication capability this project hasn't demonstrated. The opposite of "fast," so disqualified quickly rather than analyzed exhaustively |

### Success-probability ranking (revised 2026-09-01 — scored for speed-to-physical-result first, per §9f)

| Rank | Candidate | Verdict |
|---|---|---|
| 1 | **A — Lazy susan bearing** | **Fastest realistic path to a physical, demonstrable result.** Complete off-the-shelf assembly, bolt-on-ready — zero custom design/fabrication step between ordering it and mounting the existing Rev 3 enclosure on top. Comfortable friction margin (≈21.5×, recomputed 2026-09-15 per MISS-029 against the current ≈405.55g actual rotating-assembly mass, was ≈29× at this section's original ≈300g placeholder) and load capacity, no special sourcing/lead-time risk. No reaction-wheel-specific precedent, and no reaction-wheel-project heritage the way B has, but that's a peak-spec trade this round's own priority explicitly asks to give up. |
| 2 | **B — Dual 608ZZ pivot** | Best friction margin (≈327×) and the only candidate with a direct, already-adjacent real-world precedent (Charles' Labs' one-axis reaction-wheel demo uses this exact approach) — but requires a **future custom shaft/mount design** step (CG-alignment against Rev 3's off-center footprint still unresolved) before it's physically buildable. Slower to an actual result than A; kept as the documented alternative if A's margin or geometry ever proves inadequate. |
| 3 | **C — Torsion suspension** | Near-zero friction/cost, but structurally cannot do continuous/multi-turn rotation — the physics finding above suggests that may matter once commanded speeds rise. Worth keeping in mind as an even-simpler first sanity-check rig, not the primary pick. |
| 4 (not recommended this cycle) | **D — Air bearing** | The real gold-standard, but ≥25× this section's proposed budget and needs fabrication capability this project hasn't demonstrated — the opposite of "fast." Aspirational future option only. |

### Recommendation

- **Recommended candidate**: **A — Lazy susan turntable bearing**, on
  speed-to-a-physical-result grounds (human-confirmed priority, §9f) — with
  **B — Dual 608ZZ ball-bearing vertical-shaft pivot** explicitly retained
  as the documented alternative if A's margin or the enclosure's actual
  fit against a 4"-diameter bearing proves inadequate once tried.
- **Rationale** (speed to a physical result first this round, per §9f —
  not this file's usual "success probability first, peak spec second"
  framing, which would have favored B; see Trade-offs below for why B is
  still worth keeping on record):
  1. **Zero custom design/fabrication step.** A is a complete, ready-made
     assembly — order it, and the existing Rev 3 enclosure can be mounted
     flat on top with no shaft/mount design phase in between. B needs a
     Mechanical-Lead-designed shaft/mount first, with an unresolved
     CG-alignment question against Rev 3's off-center two-bay footprint —
     a real, additional design step before it's buildable at all.
  2. **Margin is still comfortable, just not the largest.** ≈0.233 mN·m
     estimated friction vs. REQ-007's ≥5 mN·m target is a ≈21.5× margin
     (recomputed 2026-09-15 per MISS-029 against the current ≈405.55g actual
     rotating-assembly mass, once Rev 4/4.1's bearing+flange+stand-plate+
     turn-limit hardware are counted — was ≈29× at this section's original
     ≈300g placeholder) — smaller than B's ≈242×, but nowhere near a
     binding constraint.
  3. **No special sourcing/lead-time risk.** $13, in stock, standard retail
     hardware — directly matches the "no long lead times" steer.
  4. **Still meets REQ-011/012's full-rotation intent** without a slip ring
     (continuous/unlimited, same as B; unlike Candidate C).
- **Trade-offs accepted** (why B remains documented, not dropped):
  - Gives up B's ≈11× better friction margin and its direct Charles' Labs
    precedent — worth revisiting if A's margin or physical fit turns out
    inadequate once actually tried.
  - Gives up Candidate C's near-zero cost/friction — in exchange for
    continuous/multi-turn rotation, which the physics finding above
    suggests may matter at anything beyond the gentlest commanded speeds.
  - Gives up Candidate D's research-grade fidelity — not a close call at
    this project's stage/budget.
- **Open UNKNOWNs** (carried forward, trimmed to what's still load-bearing):
  1. Candidate A's actual ball-race diameter (used as ≈90mm in the friction
     estimate) is not manufacturer-published — an ESTIMATE, not confirmed.
  2. The friction model itself (SKF/Koyo M=0.5·μ·P·d) is a generic
     radially-loaded rule-of-thumb applied to what is primarily a thrust
     load here — order-of-magnitude only, refine once Mechanical Design
     actually sizes the mounting.
  3. Whether Rev 3's off-center enclosure footprint sits comfortably on a
     4"-diameter bearing (vs. the product page's own "suggested top
     diameter 12"–25"" stability note) is genuinely untested — flagged for
     the future Mechanical Design phase, not resolved here.
  4. REQ-012 (angular-travel target) and REQ-505 (BOM ceiling) remain open
     human questions (`requirements/requirements.md` §9d) — this
     recommendation is robust to either proposed default holding.

### Escalation flags

1. **Architecture-defining decision — requires Hardware Lead + human Chief
   Engineer approval before any Mechanical Design/CAD work starts**
   (`docs/architecture.md` §10). This recommendation is explicitly **not
   self-approved** — see Approval table below, human row marked Pending.
   Mirrors `hardware/power-architecture.md`'s own "recommendation, not a
   decision" framing, per this task's own explicit instruction.
2. **Safety-relevant, not merely architecturally-significant.** A
   free-rotation mechanism is a **new hazard shape** distinct from REQ-403's
   already-dispositioned flywheel-containment risk (REQ-407/408) — tip-over,
   pinch points at the pivot, tether entanglement, and (per the physics
   finding above) a possibly fast-spinning free platform. None of these are
   resolved by this Component Selection pass; they are flagged for the
   future Mechanical Design phase and a fresh safety review before physical
   build, per REQ-407/408.
3. **New Evidence category introduced — `DS-BRG-NNN` (bearing/mechanical-
   rotation-hardware), flagged not silently substituted.** No existing
   category (`MTR`, `CONN`, `FAST`, `MTL`, etc.) is a precise semantic fit
   for a bearing/pivot/turntable component — mirrors this same file's own
   precedent of introducing `PROT` in the Motor-Rail Supervisory Controller
   section above for the same reason (a genuinely new component class, not
   a role-exclusive naming convention).
4. **Candidate A's race-diameter figure and the thrust-vs-radial friction
   model are both flagged ESTIMATEs, not confirmed numbers** (Open UNKNOWNs
   1–2) — real enough to rank the 4 candidates against each other with
   confidence (the margins are wide), but not precise enough to be a final
   engineering sign-off figure without the future Mechanical Design phase's
   own refinement.

### Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Component Engineer | Component Engineer (AI agent) | 2026-09-01 (revised same day, per human speed-priority clarification §9f) | Proposed — **Candidate A** (lazy susan turntable bearing), with Candidate B (dual 608ZZ ball-bearing vertical-shaft pivot) as the named documented alternative. Revised from an earlier same-day draft that had recommended B primary/A fallback on peak-friction-margin grounds, before the human's speed-to-physical-result priority was confirmed — recorded honestly, not silently overwritten (see `validation/change-log.md` ECO-027). See Escalation flags 1–3 for items requiring Hardware Lead/human confirmation before either is used downstream. |
| Hardware Lead | Hardware Lead (this session) | 2026-09-01 | Concur — recommend A as primary, B as documented alternative, for review. Friction-margin arithmetic independently re-verified (0.5×0.0013×2.943×90 ≈ 0.1722 mN·m for A; 0.5×0.0013×2.943×8 ≈ 0.0153 mN·m for B — both confirmed by direct substitution, unchanged from the prior draft). This is an architecture-level decision — routed to the human Chief Engineer via cross-session message, not self-approved. |
| Chief Engineer (Human) — required, architecture decision (`docs/architecture.md` §10) | Human Chief Engineer (Kyosuke), via creator/"General Chat" session | 2026-09-01 | **Approved — "Candidate A (lazy-susan turntable bearing, BC Precision 4LS-3, $13) — confirmed, matching your own revised recommendation."** This is the real human architecture decision, not a placeholder — Candidate A is now the approved mechanism; Candidate B remains documented as the alternative (not selected, not deleted). REQ-505's BOM ceiling is separately waived (see `requirements/requirements.md` §9g) — did not affect this decision since A already cleared the proposed ceiling by a wide margin. **Mechanical Design is authorized to proceed next** — integrate Candidate A into a new Bench-IMU-01 enclosure revision, per Mechanical Lead + Independent Mechanical Review process, same rigor as Rev 3. Other scope fences (no control loop/PID/attitude estimation, no 2nd/3rd wheel, no Control Engineer) remain active. |

---

## Electromagnetic Brake (Rapid Momentum-Dump / Cubli-Style Hard-Brake)

> **Rev 5 addition.** This is a **new subsystem category**, requested by
> the kickoff as if it would need "its own from-scratch Component
> Selection" and "its own Circuit Design (brake driver circuit, flyback
> diode protection for the inductive coil, MOSFET low-side switch)" —
> mirroring the JAXA/Mitani reference design's 3× discrete electromagnetic
> brakes. **The single most consequential finding in this entire Rev 5
> Component Selection pass is that this assumption does not hold**: the
> already-approved TI DRV10983 driver (see "Motor Driver IC" section
> above) has a documented **BRAKE bit** that shorts all three motor phase
> windings via its own internal low-side MOSFETs — the exact
> "MOSFET switching an inductive load" physics that
> `ktanino10/attitude-control-study`'s own `en/reference/interfaces.md`
> describes conceptually, except applied to the motor's own windings
> (which are themselves inductors) rather than to a separate, dedicated
> brake coil. **This section is the formal, from-scratch Component
> Selection record REQ-508 requires** — comparing that no-new-hardware
> path against real discrete electromagnetic-brake candidates — not a
> decision to skip Component Selection because a shortcut was found.

- **Driving requirement(s)**: REQ-019 (electromagnetic brake / rapid
  momentum-dump capability, new this revision), REQ-021 (Cubli-style
  jump-and-balance maneuver — human-confirmed **Must**, §9j — the maneuver
  this brake capability exists to serve), REQ-409 (safety analysis of the
  hard-brake maneuver — this section's own recommendation directly affects
  what that future analysis must characterize), REQ-508 (individual
  re-justification; the JAXA reference's own discrete-brake choice is
  architectural inspiration, not a parts list to transcribe).
- **Constraints**: braking torque/response-time requirements are derived
  from this project's own already-established flywheel inertia figure
  (100 g at 30 mm radius ⇒ I ≈ 4.5×10⁻⁵ kg·m², per the Motor section above
  and `requirements/requirements.md` §9b), not a fresh guess; the brake
  must act on a system already committed to the T-Motor MN2206-13 KV2000 +
  TI DRV10983 pairing (Motor / Motor Driver IC sections above, both
  retained this revision) — any brake solution must be compatible with
  that already-approved pairing, not assume a clean slate; real 2026
  pricing/stock for any *new* discrete part could not be reliably
  confirmed this session (automated distributor fetches repeatedly
  blocked), recorded honestly as `UNKNOWN`, not glossed over.

#### Worked braking-torque-vs-time arithmetic

Using this project's own already-established flywheel inertia
(I_wheel ≈ 4.5×10⁻⁵ kg·m², independently re-derived multiple times already
in this file from `requirements/requirements.md` §9b's own 100 g/30 mm
figures — not re-derived differently here) and the standard angular-
momentum braking relation τ = ΔL/Δt = I·Δω/Δt:

```
At 3000 RPM (ω = 314.16 rad/s):  L = I·ω ≈ 0.01414 N·m·s
  Stop in 50 ms  → τ ≈ 0.283 N·m
  Stop in 100 ms → τ ≈ 0.141 N·m
  Stop in 500 ms → τ ≈ 0.028 N·m
At 6000 RPM (ω = 628.32 rad/s):  L = I·ω ≈ 0.02827 N·m·s
  Stop in 50 ms  → τ ≈ 0.565 N·m
  Stop in 100 ms → τ ≈ 0.283 N·m
```

This range (≈0.03–0.57 N·m depending on speed/stop-time target) is the
concrete target any brake candidate below is measured against. Note this
is **torque required of the braking mechanism**, not the same figure as
the motor's own continuous-drive torque target (5 mN·m, an order of
magnitude smaller) — braking a spinning mass and driving it are different
physical demands, and this section does not conflate them.

#### Candidate Comparison

*(2 real, independently-verified candidates compared. Per this skill's own
"if fewer exist, document why" convention: a third architecturally-distinct
path — a discrete, purpose-built brake coil driven by its own dedicated
external MOSFET low-side switch + flyback diode, i.e. literally building
the circuit the kickoff's own text anticipated — was considered but is
**not listed as a separate candidate** here, because it is not a different
component choice from Candidate B below; it is the Circuit Design
implementation Candidate B would require if it were ever selected. Folding
it in as a nominal "Candidate C" would double-count the same underlying
part choice rather than add real comparison value.)*

| Parameter | Candidate A — TI DRV10983's own BRAKE bit (existing driver, no new part) — ✅ RECOMMENDED | Candidate B — Ogura MCNB series spring-applied electromagnetic brake (discrete, new part) — documented fallback |
|---|---|---|
| New hardware required | **None** — firmware-only change to the already-approved, already-owned driver IC | New discrete brake unit ×3 (one per axis), new mounting/shaft-coupling hardware, new driver circuit (flyback diode + MOSFET low-side switch, per the kickoff's own anticipated design) |
| Mechanism | Shorts all 3 motor phase windings via 3 internal low-side MOSFETs simultaneously — resistive/back-EMF dynamic braking [DS-MTR-093] | Spring-applied, electromagnetically-released friction disc brake: **power-OFF engages** the brake (spring force), **power-ON (12/24VDC coil) releases** it — a fail-safe-to-engaged behavior, opposite in failure direction from a normally-open design [DS-BRK-001] |
| Response/engagement time | **UNKNOWN until bench-tested** — no primary-source figure found for *this specific driver's* dynamic-braking stop-time; the worked arithmetic above gives the *required* torque, not a datasheet-confirmed *achieved* stop-time | Spring-applied brakes are typically millisecond-scale mechanical engagement once actuated, but this project's own exact shaft-bore/torque-variant compatibility with the 3mm T-Motor MN2206-13 shaft was **not independently confirmed from a primary source this session** [DS-BRK-002] |
| Torque capability vs. this project's ≈0.03–0.57 N·m target | Bounded by the driver's own current rating (2A continuous/3A peak per phase) against the retained motor's Kt=4.77 mN·m/A — the same current/torque headroom already re-derived in the Motor Driver IC section's Rev 5 subsection (≈9.5–14.3 mN·m available torque budget at the motor itself; actual *braking* torque delivered depends on back-EMF/short-circuit dynamics, not a simple Kt multiplication, and is part of the bench-test unknown above) | Ogura MCNB family spans a real published torque range across its size variants — the general product family is credible for this torque class, but the **specific variant/torque rating needed for this project's exact application was not narrowed to one SKU this session** [DS-BRK-003] |
| Failure-mode behavior | If driver power is lost, brake is **not engaged** (windings float) — same failure direction as the existing design already has for normal motor operation; no *new* failure mode introduced | **Fail-safe**: spring engages the brake automatically on power loss — a genuinely different, arguably safer failure-mode property than Candidate A, relevant to REQ-403/REQ-409's safety framing |
| Integration/mass/mounting impact | **Zero** new mechanical integration — uses the motor's own existing shaft/rotor, no new part to mount | Requires a real mechanical mounting solution (shaft coupling, bracket) per axis ×3 — a new Mechanical Design task, not just a BOM addition |
| Price / lifecycle | $0 incremental (firmware-only, already-owned driver) | Real 2026 qty-3 pricing/stock **not independently confirmed this session** (automated distributor fetches partially blocked); family exists across Electromate/MISUMI distributor listings [DS-BRK-004] |
| Known risks | **Bench-characterization is a real, load-bearing open item, not a formality** — this is a firmware-controlled dynamic-braking mode on an "appliance-style" sensorless driver IC, and its actual stop-time/torque/repeatability on the real motor+flywheel system is genuinely unverified; if bench testing shows it inadequate for REQ-021's repeatable hard-brake maneuver, escalate to TI DRV8316 (see Motor Driver IC section's own escalation path) before reaching for a discrete brake | Adds real cost, mass, mounting complexity, and a new driver circuit (flyback diode + MOSFET) across 3 axes for a capability that may not be needed at all if Candidate A proves adequate |

#### Success-probability ranking

| Rank | Candidate | Verdict |
|---|---|---|
| 1 | **A — TI DRV10983's own BRAKE bit** | Zero incremental cost, mass, or mechanical integration; reuses an already-approved, already-owned part; the required torque range (≈0.03–0.57 N·m) is plausible against the driver's own current rating. The one real gap — bench-confirmed stop-time/torque/repeatability — is exactly the kind of `UNKNOWN` this project's own culture requires disclosing rather than guessing at, not a reason to reach for more hardware pre-emptively. |
| 2 (documented fallback) | **B — Ogura MCNB series** | A real, credible discrete-brake path if bench testing shows Candidate A inadequate — notably with a genuinely different (arguably safer) fail-safe-on-power-loss behavior worth keeping in mind for REQ-409's eventual safety analysis. Not adopted now because it adds real cost/mass/mounting/circuit-design burden this project's own "speed to a physical result" precedent (§9f) argues against paying unless proven necessary. |

#### Recommendation

- **Recommended candidate**: **A — no new brake hardware.** Use TI
  DRV10983's own documented BRAKE bit (dynamic braking via all 3 low-side
  MOSFETs) to satisfy REQ-019, pending bench characterization.
- **Rationale**:
  1. This is a genuinely better outcome than the kickoff's own framing
     anticipated, found by evaluating the JAXA reference's own
     conceptual reasoning (why a MOSFET can brake an inductive load)
     against **this project's actual already-selected hardware**, rather
     than assuming a separate brake coil was needed just because JAXA
     used one.
  2. Zero incremental BOM cost, mass, or mechanical-integration burden —
     directly favorable to a bench-test prototype's schedule and budget,
     consistent with this project's repeatedly-stated priorities.
  3. A real, named fallback (Candidate B) exists and is not silently
     omitted if bench testing proves Candidate A inadequate.
- **Trade-offs accepted**:
  - Giving up Candidate B's fail-safe-on-power-loss property — a real,
    disclosed safety-relevant difference, explicitly flagged for REQ-409's
    future safety analysis rather than silently dropped.
  - Deferring a firm answer on braking dynamics/repeatability to a future
    bench-characterization phase — an honest `UNKNOWN until tested`
    disclosure, not a guess, and not this phase's job to resolve (this is
    Component Selection, not bench validation).
- **Open `UNKNOWN`s**:
  1. **Actual measured stop-time/torque/repeatability of DRV10983's BRAKE
     mode on the real motor+flywheel system** — the single most important
     open item, load-bearing for REQ-021/REQ-409's eventual safety
     analysis. Not estimated; must be bench-tested.
  2. Ogura MCNB's exact shaft-bore/torque-variant compatibility with this
     project's 3mm motor shaft — not independently confirmed this session.
  3. Live 2026 qty-3 pricing/stock for Ogura MCNB (moot unless the
     fallback path is actually exercised).
- **Escalation flags**:
  1. **REQ-019's own scope may have just gotten materially smaller** than
     the kickoff assumed — flagged explicitly for the human's own
     awareness, since this changes a "new subsystem, new Circuit Design"
     assumption into "a firmware change to an already-approved part,
     pending bench test." This is a real scope change, not a decision this
     Component Selection phase can finalize on its own.
  2. **Bench characterization of BRAKE-mode stop-time/torque is safety-
     relevant** (REQ-409) and must not be estimated or assumed adequate —
     kept `UNKNOWN` here deliberately.
  3. If bench testing shows Candidate A inadequate, the escalation path is
     **first** to TI DRV8316 (Motor Driver IC section's own Rev 5
     subsection — a driver-level fix retaining "no new brake hardware"),
     and only **then**, if that also proves inadequate, to Candidate B
     here or an equivalent discrete brake — this ordering is a
     recommendation, not a finalized decision.

#### Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Component Engineer | Component Engineer (AI agent, via parallel research sub-agent) | 2026-09-04 | Proposed — no new brake hardware; reuse TI DRV10983's own BRAKE bit; Ogura MCNB documented as discrete-brake fallback |
| Hardware Lead | Hardware Lead (this session) | 2026-09-04 | Concur — recommend approval for the Component-Selection-level recommendation; explicitly **not** approving REQ-019's scope reduction as a done deal, nor treating BRAKE-mode adequacy as proven — both routed to the human below |
| Chief Engineer (Human) — required: (a) this is a new-subsystem-avoiding architecture decision, (b) REQ-019's scope may be materially reduced from what was approved at kickoff | Human Chief Engineer | 2026-09-04 | **Approved** — "確定" (Kyosuke's own direct plain-text reply, turn 616, `session_store_sql` session `7fab99ef-5578-4d79-a9c2-b24dbcfe93be`, `2026-09-04T16:00:16.240Z`), in direct reply to a specific question naming this exact recommendation by name (turn 614, `2026-09-04T15:54:20.062Z`) — both turns independently re-verified by this session directly against the raw turn history, not accepted from a relayed summary alone. Approves proceeding with TI DRV10983's own BRAKE bit (no new brake hardware) as the primary design direction, with Ogura MCNB documented as the discrete-brake fallback, as recommended. **This approval authorizes the design direction — it is explicitly not a safety determination.** REQ-021's Cubli-style hard-brake maneuver's real stop-time, torque, and repeatability on the actual motor+flywheel system remain `UNKNOWN until bench-tested`; this approval does not certify BRAKE-mode adequacy for that maneuver, and REQ-409's eventual safety analysis (Mechanical Reviewer, once the real design is finalized) is not pre-empted or waived by this record. |

---

## Wireless Remote-Control Link

> **Rev 5 addition.** New subsystem category — Rev 1-4 had no wireless
> requirement at all (USB-tethered bench rig only). REQ-020 (wireless)
> became a **Must** once the human confirmed REQ-021's jump-and-balance
> maneuver (§9j): an untethered maneuver cannot rely on a USB cable for
> command/telemetry. This section's recommendation is **directly coupled**
> to the MCU Rev 5 recommendation above (ESP32-S3) — if ESP32-S3 is
> approved, its own built-in Wi-Fi+BLE radio satisfies REQ-020 with **zero
> additional wireless-module BOM line**; this section exists to document
> that coupling explicitly and to name a real, independent fallback module
> in case the MCU decision changes.

- **Driving requirement(s)**: REQ-020 (wireless remote-control link — now
  **Must**, §9j), REQ-021 (the untethered jump/stand maneuver that drives
  REQ-020's urgency), REQ-508 (individual re-justification — the JAXA
  reference design used a UART-based wireless remote link as a discrete
  module; this project's own newly-selected MCU may make that unnecessary,
  evaluated fresh rather than assumed).
- **Constraints**: must support a command/telemetry link sufficient for
  remote control of the jump/stand maneuver (not a high-bandwidth
  streaming requirement); must not require an external module if the
  selected MCU already provides equivalent capability; real 2026
  pricing/stock for any candidate module could not be reliably confirmed
  this session (flagged honestly, not glossed over).

#### Candidate Comparison

*(3 candidates compared — meets the ≥3 minimum. Candidate A is not a
discrete part but the MCU's own built-in radio, evaluated on the same
comparison axes as a fair alternative to adding a separate module.)*

| Parameter | Candidate A — ESP32-S3's own built-in Wi-Fi+BLE (native, no separate module) — ✅ RECOMMENDED, conditional on MCU Rev 5 approval | Candidate B — Renesas/Dialog DA14531MOD (BLE UART-bridge module, e.g. MikroE "BLE TINY Click") — documented fallback | Candidate C — generic nRF24L01+-class simple 2.4GHz UART bridge module |
|---|---|---|---|
| Radio capability | Wi-Fi 802.11 b/g/n + Bluetooth LE 5 (incl. Long Range/Coded PHY) [DS-MCU-082] | Bluetooth LE 5.x, UART/AT-command interface via CodeLess firmware [DS-RF-001] | Proprietary 2.4GHz, not a standard protocol — no phone/tablet interoperability without custom app work on the remote-control side (a real practicality concern for a "remote-control link" this project's own README-level framing implies a human operator using) |
| Incremental BOM cost | **$0** — already part of the MCU module | Real per-unit module price **not independently confirmed this session** (MikroE's own $18 dev-board price was found, but that is a full breakout board, not a bare-module unit price — flagged honestly rather than repeated as if it were the real BOM-line cost) [DS-RF-002] | Typically ~$1-2/module per common hobbyist-market listings (not independently re-verified from a primary distributor this session) |
| Integration effort | **Lowest** — same MCU already selected for compute; no new UART wiring, no new firmware driver, no new footprint | Requires a dedicated UART connection, a new firmware driver (AT-command or CodeLess protocol), and a new PCB footprint/antenna keep-out | Requires a dedicated UART/SPI connection, a new firmware driver, and a new PCB footprint/antenna keep-out; no standard phone-side BLE stack applies |
| Standard protocol / phone-app interoperability | Yes — BLE is natively supported by iOS/Android; Wi-Fi enables a full IP-based remote-control app if desired | Yes — BLE, same phone/tablet interoperability property as Candidate A | **No** — proprietary 2.4GHz protocol has no built-in phone-side support; a custom receiver/bridge would be needed for anything beyond a matching hobbyist transmitter module |
| Lifecycle/EOL | Active [DS-MCU-085] | Not independently re-confirmed to a clean, current lifecycle statement this session | Not independently re-confirmed to a clean, current lifecycle statement this session; broad hobbyist-market genericness makes exact manufacturer/lifecycle tracking difficult |
| Known risks | **Entirely contingent on the MCU Rev 5 recommendation (ESP32-S3) being approved** — if a different MCU is ultimately selected, this candidate does not exist and Candidate B becomes the primary path | Real per-unit bare-module pricing/range not independently confirmed this session; adds a real new PCB footprint/antenna-keepout design task regardless of MCU choice | No standard protocol support undermines the "remote-control" use case's likely need for a phone/tablet-side control app; weaker sourcing/lifecycle traceability than a named manufacturer part |

#### Success-probability ranking

| Rank | Candidate | Verdict |
|---|---|---|
| 1 (conditional) | **A — ESP32-S3 native Wi-Fi+BLE** | Zero incremental BOM cost, zero new firmware driver category, zero new PCB footprint — directly follows from the MCU Rev 5 recommendation above. This is the clearly correct choice **if and only if** ESP32-S3 is approved as the MCU; it is not a standalone recommendation independent of that decision. |
| 2 (documented fallback) | **B — DA14531MOD-class BLE bridge** | The correct fallback if a different MCU (e.g. STM32F411CET6) is ultimately selected — real BLE capability, standard phone-app interoperability, from a named manufacturer part with real (if not fully re-verified) documentation. |
| 3 (not recommended) | **C — generic 2.4GHz UART bridge** | Lacks standard-protocol phone/tablet interoperability, which likely matters for a human-operated "remote-control" use case; weaker sourcing/lifecycle traceability than a named manufacturer part. Not disqualified outright, but clearly inferior to B for this project's actual use case. |

#### Recommendation

- **Recommended candidate**: **A — ESP32-S3's own built-in Wi-Fi+BLE radio**,
  **conditional on the MCU Rev 5 recommendation (ESP32-S3) being approved.**
  If a different MCU is ultimately selected, this recommendation
  automatically falls back to **B — DA14531MOD-class BLE bridge module**,
  not to Candidate C.
- **Rationale**:
  1. This decision is not independent of the MCU choice — presenting it
     as if it were would misrepresent the actual coupling between the two
     Rev 5 findings. Recording that coupling explicitly, rather than
     picking a wireless part in isolation, is the honest way to record
     this recommendation.
  2. If ESP32-S3 is approved, the zero-incremental-cost/zero-new-firmware-
     driver/zero-new-footprint outcome is strictly better than any
     discrete module path, on every axis compared.
  3. A real, named fallback (B) exists and is not silently omitted if the
     MCU decision goes a different way.
- **Trade-offs accepted**:
  - This recommendation's validity was, at the time it was written, entirely
    contingent on the MCU decision — explicitly disclosed then, not hidden
    behind a confident-sounding standalone recommendation. **Update
    (2026-09-04): the MCU decision (ESP32-S3) is now Approved** — see this
    section's own Approval table below — so this recommendation's
    condition is now satisfied, not merely disclosed as pending.
  - Real per-unit pricing for Candidate B (the fallback) was not
    independently confirmed this session — acceptable since it is not
    the primary path, but flagged for re-verification before it would
    ever actually be needed.
- **Open `UNKNOWN`s**:
  1. Real per-unit bare-module pricing for DA14531MOD-class modules (the
     fallback path) — not independently confirmed this session.
  2. Exact wireless protocol/range/latency requirements for the actual
     jump/stand remote-control use case — not yet specified at a level of
     detail this section could design against; likely a Circuit
     Design/Firmware-stage refinement, not a Component-Selection-stage gap.
- **Escalation flags**:
  1. **This recommendation is conditional, not standalone** — the human's
     MCU decision determines which candidate (A or B) actually applies;
     both should be reviewed together, not as independent approvals.

#### Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Component Engineer | Component Engineer (AI agent, via parallel research sub-agent) | 2026-09-04 | Proposed — ESP32-S3 native Wi-Fi+BLE if MCU recommendation approved; DA14531MOD-class BLE bridge as fallback |
| Hardware Lead | Hardware Lead (this session) | 2026-09-04 | Concur — recommend approval, explicitly conditional on the MCU Rev 5 decision; both should be reviewed as one coupled decision |
| Chief Engineer (Human) — required: key-component decision, coupled to the MCU decision above | Human Chief Engineer | 2026-09-04 | **Approved** — "確定" (Kyosuke's own direct plain-text reply, turn 616, `session_store_sql` session `7fab99ef-5578-4d79-a9c2-b24dbcfe93be`, `2026-09-04T16:00:16.240Z`), in direct reply to a specific question naming this exact recommendation by name (turn 614, `2026-09-04T15:54:20.062Z`) — both turns independently re-verified by this session directly against the raw turn history, not accepted from a relayed summary alone. Approves ESP32-S3's native Wi-Fi+BLE (with DA14531MOD-class BLE bridge documented as the fallback) as recommended, consistent with the MCU decision above. |
