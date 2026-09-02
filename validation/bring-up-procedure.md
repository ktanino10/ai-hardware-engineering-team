# Bring-up / First Power-On Procedure

Standardizes first-power-on so it isn't improvised each time. This is the
concrete artifact behind the "before first power-on of real hardware"
Human-in-the-loop gate (`docs/architecture.md` §10). MVP: Hardware Lead +
human execute this jointly. A future **Test Engineer** role
(`docs/architecture.md` §14) formally owns this once bring-up moves beyond
a one-off MVP bench test.

**Human sign-off is required before applying power. Do not skip to power-on
because the schematic/PCB "looks done".**

**This procedure is prepared with real, project-specific values for
Bench-IMU-01 (below) for the human's future physical build. Per REQ-502
and this cycle's own paper/document-design scope, it is NOT executed this
session — no physical PCB exists yet to power on.**

## 0. Project-Specific Values — Bench-IMU-01 (Rev 2, Electronics + Mechanical)

Pulled directly from `hardware/power-budget.md`, `bom/component-selection.md`,
and `hardware/schematic/bench-imu-01-design.md` — cite the source file, not
this copy, if a number ever needs re-confirming.

| Item | Value | Source |
|---|---|---|
| Input rail | USB 5V VBUS via J1 (USB-C), nominal 5.0V, tolerate 4.75–5.5V real-world `vSafe5V` range (wider than REQ-101's own 4.75–5.25V — see ISS-002/FMEA-001) | `bench-imu-01-design.md` §3, DS-CONN-001 |
| Regulated rail | Single 3.3V rail (U3, TLV75533PDBVR, fixed-output LDO) | power-budget.md, DS-PWR-001 |
| Expected 3.3V rail current draw | ≈7.0 mA typical, ≈16.2 mA worst-case | power-budget.md §"Rail Margin Summary" |
| REQ-103 system current budget | ≤300 mA @ 3.3V (actual worst-case is ≈94.6% below this ceiling) | power-budget.md |
| LDO rated max output current | 500 mA (actual worst-case draw is ≈96.8% below this) | DS-PWR-003 |
| **Recommended bench-supply current limit for first power-on** | Start at ≈50 mA (≈3x the 16.2 mA worst-case estimate — conservative headroom for measurement error, not the full 300 mA/500 mA ceiling) and raise only after rail voltage confirmed nominal | Hardware Lead's own bring-up-safety judgment, this pass |
| Power sequencing | None required — single 3.3V rail, no sequencing dependency between subsystems (MCU/IMU/LED all share the one rail) | `bench-imu-01-design.md` §2.1 |
| Boot-mode check (do this BEFORE first power-on) | Confirm BOOT0/nBOOT_SEL state matches documented intent (user Flash boot, not System Memory) — see FMEA-002/ISS-006 | `bench-imu-01-design.md` §4.2, DS-MCU-050/051 |
| Polarity-sensitive items to check | U3 LDO orientation (SOT-23-5, pin 1 marking); D1 LED polarity; J1 USB-C VBUS/GND (note: ISS-004/FMEA-005 — no discrete reverse-polarity protection exists, so a miswired cable is NOT caught by the circuit itself; visual/continuity check is the only safeguard against this specific risk) | parts list, ISS-004 |
| Interface to sanity-check | I2C2 on **PA11 (SCL)/PA12 (SDA)** — corrected 2026-09-11 per ISS-027 (was documented as PB10/PB11 through Rev 5/6, but those pins do not physically exist on this LQFP-32 package), 4.7kΩ pull-ups (R3/R4), IMU (U2, BMI270) at its I2C address | `bench-imu-01-design.md` §5, DS-MCU-073 |
| Debug/programming access | SWD via J3 (VDD/SWCLK/GND/SWDIO) | `bench-imu-01-design.md` §4.4, DS-CONN-002 |
| Known accepted residual risk | ISS-002 (LDO ROC margin, ACCEPTED-RISK) — if bench-measuring at a deliberately worst-case ~5.5V input, expect this is a known, human-accepted edge case, not a new finding | `validation/change-log.md` ECO-003 |
| Enclosure fit check (once PCB exists) | Enclosure geometry is fit to `hardware/mechanical-interface.md`'s estimates, not a confirmed real PCB layout (FMEA-007) — verify physical board dimensions/connector positions against the enclosure BEFORE final assembly, not after | `hardware/mechanical-interface.md`, `hardware/mechanical/bench-imu-01-dimensional-spec.md` |

## 0a. Firmware Flashing — Bench-IMU-01 (Phase 2; tooling guide added 2026-09-02 — still NOT executed this session)

Driver-level bring-up firmware exists
(`firmware/bench-imu-01/`, design rationale in
`firmware/bench-imu-01/bench-imu-01-firmware-design.md`) and **compiles
cleanly** with `arm-none-eabi-gcc` (verified this session — see that
document's §0/§7). **Nothing in this section has been executed**: there is
no physical Bench-IMU-01 board in this environment, no SWD programmer or
USB-UART adapter has actually been purchased/connected, and no firmware has
actually been flashed — matching this whole procedure's own "not executed
this session" framing (REQ-502). §0a.1–§0a.5 below replace this section's
prior placeholder ("flashing tool not part of this repository's tooling")
with a concrete, evidence-cited **tooling-procurement guide** for the
human's own future physical build — it remains paper research, not a
tool-capability claim about this AI session (`docs/architecture.md` §5.4/
§13 still correctly state no flashing tool is connected to this session
itself). Flashing real hardware for the first time remains gated behind
the "before flashing firmware to real hardware" Human-in-the-loop gate
(`docs/architecture.md` §10).

### 0a.1 SWD programmer options

Bench-IMU-01's J3 header is a bare, unshrouded 4-position 2.54mm-pitch pin
header (Sullins PREC004SAAN-RC, DS-CONN-008), wired **VDD/SWCLK/GND/SWDIO
only — no NRST, no SWO** (`bench-imu-01-design.md` §4.4, DS-CONN-002). Any
programmer connected here needs female-socket ("Dupont") jumper wires (or
an equivalent adapter) matched **by signal name, not by wire color or
physical position** — clone-programmer pinout silkscreens vary by seller.

| Option | Type | Approx. price (qty1) | STM32G0/Cortex-M0+ evidence | Notes |
|---|---|---|---|---|
| STMicroelectronics **ST-LINK/V2** (genuine) | Official ST tool | ~$25 (DigiKey/Mouser/ST eStore) | DS-TOOL-001, DS-TOOL-002 | Classic 20-pin IDC header ships with flying-lead/Dupont adapter cables — mates directly with J3's 2.54mm pitch, no adapter needed |
| STMicroelectronics **STLINK-V3MINI** (genuine) | Official ST tool | ~$9–11 (DigiKey/Mouser) — **cheaper than ST-LINK/V2** | DS-TOOL-003, DS-TOOL-004 | Also provides a Virtual COM Port (VCP) UART bridge (STDC14 pins 13/14) that could stand in for a separate USB-UART adapter (§0a.3) — **but** its STDC14 connector (14-pin, 0.05" pitch) does not directly mate with J3's 2.54mm pitch; needs ST's own adapter board or hand-wiring |
| Generic **"ST-LINK V2" compatible clone** (e.g. widely-sold "ST-LINK V2 Mini") | Third-party clone | Amazon ~$7–15; AliExpress ~$3–4 | DS-TOOL-005 | Explicitly named as supported by the open-source `stlink-org/stlink` toolset ("STLINK programmer boards and clones thereof... no difference in handling or operation") — not an ST-authorized/warrantied product |
| *(Bonus)* **NUCLEO-G031K8** official eval board's onboard ST-LINK, used standalone | Official ST board, repurposed | ~$13 (DS-MCU-020) | DS-TOOL-013, DS-CONN-002 | Same MCU family already used as this design's own SWD-header reference (DS-CONN-002); requires removing the board's own ST-LINK-to-target jumpers per its user manual, then wiring its CN4 (same VDD/SWCLK/GND/SWDIO convention) out to J3 — more setup effort, but a genuine ST-LINK/V3 debugger plus a spare eval board for the same low price |

**Recommendation**: a classic ST-LINK V2-form-factor unit is the simplest
match for J3's plain 2.54mm header. Buy the **genuine STMicroelectronics
ST-LINK/V2** (~$25) for official ST vendor support, or a **~$5–10
compatible clone** if minimizing cost for this one-off bench build is the
priority (accepting no ST warranty/support channel) — both are expected to
work identically with all three flashing-software options in §0a.2, per
DS-TOOL-005.

### 0a.2 Flashing software options (macOS)

| Tool | macOS install | STM32G0 support evidence | Interface | Trade-offs |
|---|---|---|---|---|
| **`st-flash`** (`stlink-org/stlink`, open source) | `brew install stlink` (stable **1.8.0**, bottled for macOS Sequoia/Sonoma, ARM64+Intel — confirmed via Homebrew's own formula API) | DS-TOOL-005, DS-TOOL-006, DS-TOOL-007 | CLI only | Simplest single command; matches this repo's own `firmware/bench-imu-01/Makefile` header-comment example; community-maintained, not ST-official |
| **STM32CubeProgrammer** | Official ST installer (`st.com`), requires a free myST account; GUI + CLI (`STM32_Programmer_CLI`) | DS-TOOL-008 | GUI + CLI | ST's own official tool, most complete feature set (option bytes, etc.); heavier install, some macOS Java/security-permission friction reported in ST's own community forum |
| **OpenOCD** | `brew install openocd` (stable **0.12.0**, bottled for macOS Sequoia/Sonoma/Ventura/Monterey/Big Sur, ARM64+Intel — confirmed via Homebrew's own formula API) | DS-TOOL-009, DS-TOOL-010 | CLI + live GDB server | Adds interactive GDB debugging beyond one-shot flashing; more setup (interface + target `.cfg` pair) |

**Important — J3 has no NRST pin** (§4.4): whichever tool is used, expect
it to fall back to a **software reset** rather than a hardware NRST pulse.
This is not a guess — both `st-flash` (AIRCR software reset, supported
since v1.5.1, DS-TOOL-006) and OpenOCD's own mainline `stm32g0x.cfg`
(`reset_config srst_nogate` + `cortex_m reset_config sysresetreq` when no
hardware-adapter probe is used, DS-TOOL-010) explicitly document this exact
fallback path for this MCU family.

**Recommendation**: `st-flash` for the simplest one-shot flash (matches
this repository's own existing Makefile-comment example); STM32CubeProgrammer
if the human prefers ST's own official/most full-featured tool; OpenOCD if
interactive GDB debugging (not just flashing) will also be wanted.

### 0a.3 USB-UART adapter for J2 (3.3V logic)

J2 is a 4-pin, 2.54mm-pitch header (same MPN as J3, DS-CONN-008): **TX
(PA2)/RX(PA3)/GND/3V3**, fixed at 3.3V logic (`bench-imu-01-design.md` §6)
— the adapter's own logic-level setting must be 3.3V, not 5V.

| Option | Approx. price (qty1) | Logic level | macOS driver | Evidence |
|---|---|---|---|---|
| **CP2102-based module** (Silicon Labs) | ~$3–6 | 3.3V/5V jumper-selectable on most modules | Official Silicon Labs VCP driver | DS-TOOL-011 |
| **FTDI FT232R/FT232RL-based module** | ~$15–20 (genuine) | Depends on the specific module (fixed-3.3V, fixed-5V, or jumper-selectable SKUs all exist) | Official FTDI VCP driver, long macOS track record | DS-TOOL-012 |

**Recommendation**: a **CP2102-based module**, set to 3.3V — cheapest,
widely available, and directly matches J2's fixed-3.3V logic. An FTDI
FT232R-based module is an equally valid, historically very reliable
alternative at higher cost; watch for counterfeit-chip risk on
ultra-cheap FTDI-branded listings (DS-TOOL-012).

### 0a.4 End-to-end procedure: build → flash → verify (for the future physical build — not run this session)

```sh
# 1) Build (already verified working this session — arm-none-eabi-gcc required)
cd firmware/bench-imu-01
make                                    # -> build/bench-imu-01.{elf,bin,hex}

# 2) Wire the SWD programmer to J3, matching signal names (VDD/SWCLK/GND/SWDIO)
#    — no NRST/SWO on this header; confirm 3.3V VDD reference before connecting.

# 3a) Flash with st-flash (brew install stlink):
st-flash --format ihex write build/bench-imu-01.hex
# or, using the raw binary + explicit STM32 flash base address:
st-flash write build/bench-imu-01.bin 0x08000000

# 3b) ...or with STM32CubeProgrammer:
STM32_Programmer_CLI -c port=SWD -w build/bench-imu-01.hex

# 3c) ...or with OpenOCD:
openocd -f interface/stlink.cfg -f target/stm32g0x.cfg \
        -c "program build/bench-imu-01.hex verify reset exit"

# 4) Wire the USB-UART adapter (set to 3.3V) to J2: adapter TX -> J2 RX(PA3),
#    adapter RX -> J2 TX(PA2), adapter GND -> J2 GND. Find its device path:
ls /dev/cu.usbserial-*                  # (prefer cu.* over tty.* for `screen`)

# 5) Open the serial console at 115200 8N1:
screen /dev/cu.usbserial-XXXX 115200    # Ctrl-A then K, then Y, to exit
```

Compare the resulting output against §0a.5's expected first-boot sequence
below (boot banner → `RESET_REASON:` → `BMI270_INIT_OK` → CSV telemetry).

### 0a.5 Debug access, expected output, and known residual items

| Item | Value | Source |
|---|---|---|
| Debug/programming access | SWD via J3 (VDD/SWCLK/GND/SWDIO) — same header row already listed above | `bench-imu-01-design.md` §4.4 |
| Flashing tool | See §0a.1–§0a.2 above for the evidence-cited programmer/software recommendation (previously: "not part of this repository's tooling today" — that placeholder is now replaced by this concrete guide; still not exercised by this AI session itself, `docs/architecture.md` §5.4/§13) | This file §0a.1–§0a.4 |
| Expected first-boot UART output (at 115200 8N1, on the J2 header) | A boot banner, one `RESET_REASON:` line (decoding `RCC_CSR` — expect `POWER_ON` on a first-ever flash, or `NRST_PIN(SW1_or_debugger)` if reset via SWD/reset line), then either `BMI270_INIT_OK` followed by continuous `millis,ax,ay,az,gx,gy,gz` CSV lines at ~100 Hz, or a `BMI270_INIT_FAILED: ...` line if the IMU didn't come up (check I2C2/PA11-PA12 wiring — corrected 2026-09-11, ISS-027; was PB10/PB11 through Rev 5/6 — and the BMI270's solder joints first) | `firmware/bench-imu-01/src/main.c`, `reset_reason.c` |
| Pre-flash checklist addition | Confirm the SWD debugger is configured for a Cortex-M0+ target at the expected VDD (3.3V, from J3's own VDD reference pin) before connecting — same polarity/orientation care as the rest of §1's checklist | `bench-imu-01-design.md` §4.4 |
| Known residual, non-blocking item | The I2C_TIMINGR value used by the firmware (DS-MCU-063) was cross-checked via two independent web-search-derived sources but not directly re-verified against the primary ST AN4235 PDF this session — low-risk for a bench link, worth a direct check before this firmware is considered final | `datasheets/stmicroelectronics_an4235_i2c-timing-configuration-tool.md` |

## 1. Pre-Power-On Checklist

**Rev 3 note**: the rest of this file (§0 values table, §2 sequencing, §3
measurement) is still Rev 2-scoped and has not yet been rewritten for the
Motor Driver + Reaction Wheel subsystem — that full rewrite is tracked
separately as `validation/open-issues.md` ISS-023 (MEDIUM, non-blocking,
planned for the `validation-artifacts-rev3` closeout pass, after Mechanical
Design/Review settle the physical values this file would otherwise cite).
The single item immediately below is a **targeted advance addition**, not
an oversight — it is the specific compensating safeguard a human Chief
Engineer required (2026-09-09, cross-session HITL channel) as the condition
for accepting ISS-020/ISS-021 as ACCEPTED-RISK rather than leaving Rev 3's
hardware/mechanical Design Complete blocked on firmware that hasn't been
written yet. It must remain in force even after the full Rev 3 rewrite
happens — do not let a future rewrite silently drop it.

- [ ] **MOTOR/REACTION-WHEEL SUBSYSTEM (Rev 3) — MANDATORY, DO NOT SKIP OR
      DEFER.** Before any power is ever applied to the U6/motor-rail domain
      (12V J4 input, U6 TPS26631PWPR supervisory switch, U5 DRV10983 driver,
      M1 T-Motor MN2206-13 + flywheel): confirm Firmware Bring-up has
      actually implemented, and the flashed firmware build demonstrably
      enforces, **both** REQ-405 (a bounded maximum operating/fault speed
      with tach-supervised overspeed shutdown — not just the ≥3000 RPM
      floor) **and** REQ-406 (a latched fault response — after a
      fault-retry threshold, force the motor to a safe/stopped state and
      require a deliberate re-arm, rather than relying on U5/U6's own
      auto-recovering protections to loop indefinitely). This is the
      specific, named compensating control for `validation/open-issues.md`
      **ISS-020** (no bounded speed envelope) and **ISS-021** (no latching
      fault behavior) — both dispositioned ACCEPTED-RISK, explicitly
      conditioned on this check, **not** independently resolved by hardware
      alone (see those findings' full rationale, and
      `validation/change-log.md` for the corresponding ECO). Do **not**
      proceed past this line item on the assumption that U5's Lock
      Detection/Thermal Shutdown or U6's current limit is sufficient by
      itself — per ISS-021, all of those mechanisms auto-retry/auto-recover
      by design and do not latch. If REQ-405/406 firmware cannot be
      confirmed present and functioning, **do not energize the motor rail**;
      the rest of this procedure's Rev 2 scope (MCU/IMU/logic rail) may
      still proceed independently.
- [ ] **FLYWHEEL CONTAINMENT STRUCTURE (Rev 3) — MANDATORY, DO NOT SKIP OR
      DEFER.** Before the flywheel is ever spun (i.e. before any nonzero
      `SPD` command is issued, even at low duty), physically confirm: (1)
      the containment cap (`containment_cap()`) is installed and its 6×M3
      fasteners are torqued into the base's heat-set inserts — **not**
      merely rested in place; (2) the base's own cylindrical wall
      (`fw_bay_wall()`, the primary containment surface per
      `validation/open-issues.md` **MISS-013**'s own determination) shows no
      visible print defect (delamination, layer separation, a short/aborted
      print) at the flywheel-bay location; (3) the as-built print actually
      matches `hardware/mechanical/bench-imu-01-manufacturing-spec.md`'s
      specified process (material, infill %, perimeter count) as closely as
      the actual printer/slicer allows — **do not spin the flywheel on a
      print sliced with unverified/default settings**, since the entire
      REQ-403 safety argument depends on this. This is the physical
      precondition for the human Chief Engineer's own **REQ-403**
      ACCEPTED-RISK disposition (`validation/open-issues.md` **MISS-016**,
      `validation/change-log.md` **ECO-025**): that disposition explicitly
      accepts the containment structure as a **defense-in-depth mitigation,
      not validated/certified containment** — a calculated, human-accepted
      energy-absorption shortfall of ≈3.26–4.30× (best case) to ≈1.7–3.6
      orders of magnitude (typical) remains open and unresolved by physical
      testing (**MISS-022**, tracked, not yet performed). Do **not** treat a
      clean Design Complete Gate as evidence the containment has been proven
      adequate — it has explicitly not been. If the containment structure
      cannot be visually/physically confirmed installed and matching its
      specified process, **do not spin the flywheel at any commanded speed**
      — even REQ-007's own 3000 RPM floor already carries real stored
      rotational energy (§8's own physics table).
- [ ] Visual inspection: correct component population and orientation
      (polarized parts, pin-1 orientation)
- [ ] Continuity check: no unintended shorts between rails/ground (per
      `hardware/power-budget.md` rail list)
- [ ] Polarity check on all polarized components (electrolytic caps,
      diodes, connectors)
- [ ] Jumper/strap configuration matches the intended boot/config mode
- [ ] Bench supply set to **current-limited** mode, with a conservative
      limit derived from `hardware/power-budget.md` (start well below the
      expected max draw)
- [ ] Expected voltage rails and tolerances documented (pull straight from
      `hardware/power-budget.md` and the relevant Evidence IDs)
- [ ] ESD precautions in place (strap/mat as appropriate)
- [ ] `requirements/traceability-matrix.md` rows this bring-up is meant to
      verify are identified in advance

## 2. Safe Power-On Sequence

1. Power on with the bench supply's current limit set conservatively.
2. Bring up rails in the order defined by the design's power-sequencing
   requirement (see the Circuit Engineer's design rationale /
   `hardware/power-budget.md`) — do not bring up all rails simultaneously
   if the design specifies a sequence.
3. At each rail, **stop and measure** before proceeding to the next:
   voltage within tolerance? current draw within budget?
4. **Abort criteria** (immediate power off): overcurrent trip, any smell of
   burning, visible smoke, a component becoming hot to the touch
   unexpectedly, or any rail voltage outside tolerance.
5. Only after all rails are confirmed nominal, proceed to functional
   bring-up (e.g. MCU boot, interface communication).

## 3. Bench Measurement Procedure

- Rail voltages at defined test points, vs. `hardware/power-budget.md`
  expected values and tolerance.
- Ripple on each rail (if measurement equipment available).
- Actual current draw per rail vs. budget.
- Thermal check (touch-check or thermal imaging if available) on
  regulators/drivers under load.
- Interface signal sanity: e.g. I2C/SPI waveform/ack check, confirm
  communication with the IMU (or other peripheral) actually establishes.

## 4. Pass/Fail Criteria

- Compare every measurement against `requirements/traceability-matrix.md`
  and the relevant datasheet Recommended Operating Conditions
  (`datasheets/evidence-log.md`), not against "it seems to work".
- Any failure reopens Circuit Design (`docs/workflow.md` Phase 4) — do not
  patch around a bring-up failure on the bench without logging it in
  `validation/open-issues.md` and, if the design changes,
  `validation/change-log.md`.

## 5. Sign-off

| Role | Name | Date | Decision |
|---|---|---|---|
| Hardware Lead | | | |
| Chief Engineer (Human) — required before power-on | | | Pending |
