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
| Overcurrent / stall / thermal protection (REQ-111/404) | Overcurrent protection programmable via I2C with auto-retry; stall inferred from I2C status register + FG-signal silence. Exact thermal-shutdown threshold/behavior **UNKNOWN this session** (not extractable from the fetched pages) [DS-MTR-037] | Overcurrent protection plus locked-rotor/stall detection via absence of expected Hall-switching transitions, auto-retry timing set by an external capacitor on a RETRY pin [DS-MTR-046] | ALERT pin reported for abnormality/lock detection per secondary-source claim; specific OCP/TSD thresholds **UNKNOWN this session**, **not primary-source-confirmed** [DS-MTR-050] |
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
