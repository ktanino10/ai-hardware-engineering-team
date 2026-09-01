# Texas Instruments DRV10983 Datasheet — Rev UNKNOWN (SLVSCP6H)

- **Manufacturer**: Texas Instruments
- **Part Number**: DRV10983 (also sold as DRV10983Q1 automotive-grade
  variant, not the variant considered here)
- **Datasheet Title**: "DRV10983 Sensorless Sinusoidal-Drive BLDC Motor
  Driver" (as titled on TI's own product page)
- **Revision / Version**: Literature number **SLVSCP6**, this session's
  live TI product-page fetch showed a "H" revision suffix context
  (**SLVSCP6H**) but the PDF's own cover-page revision letter was not
  independently re-transcribed byte-for-byte this session (the PDF itself
  was binary/not text-extractable via this session's tooling) — recorded
  as the best-available identifier, not to be treated as a byte-for-byte
  confirmed revision letter.
- **Publication Date**: UNKNOWN (not confirmed this session — TI's page
  showed a "PRODUCTION DATA" status marker, not a print date)
- **Official URL**: https://www.ti.com/lit/ds/symlink/drv10983.pdf (URL
  confirmed to resolve to a real TI-hosted document this session; TI's own
  HTML product page at ti.com/product/DRV10983 was live-fetched and is the
  actual source of the specific numeric/feature claims below, since the PDF
  itself could not be text-extracted this session)
- **Retrieved Date**: 2026-08-31
- **Local cache note**: not committed; content read live via web fetch of
  TI's HTML product/EVM pages this session, not the raw PDF text; not
  cached to any local disk.
- **Used for Evidence IDs**: DS-MTR-032, DS-MTR-033, DS-MTR-034, DS-MTR-035,
  DS-MTR-036, DS-MTR-037, DS-MTR-038, DS-MTR-039, DS-MTR-040, DS-MTR-041,
  plus DS-MTR-052 through DS-MTR-071 (added by the Circuit Engineer/Hardware
  Reviewer during Bench-IMU-01 Rev 3 schematic design, 2026-09-04/05 — see
  the Update note below), plus DS-MTR-072 through DS-MTR-076 (added by the
  Firmware Engineer during Bench-IMU-01 Rev 3 motor bring-up firmware,
  2026-09-10 — see the second Update note near the end of this file), plus
  DS-MTR-077/DS-MTR-078 (added by the Firmware Engineer closing Firmware
  Reviewer Finding 1, HIGH, PR #14, 2026-09-12 — see the third Update note
  at the end of this file)

## Update (Circuit Engineer, 2026-09-04, Bench-IMU-01 Rev 3)

**The "Known gaps" section immediately below is now largely superseded —
left in place for history, not deleted, per this repository's evidence
transparency convention (see the STM32G031K8T6 metadata record's own
"Correction note" for the same pattern).** This session successfully
retrieved and read the **full primary PDF** (not just TI's HTML product
page) via an `r.jina.ai` text-extraction reader proxy fetching
https://www.ti.com/lit/ds/symlink/drv10983.pdf directly — the prior
session's "binary/not text-extractable" limitation was a tooling gap, now
resolved, not a genuine document-availability problem. The full 24-pin
pinout, Absolute Maximum Ratings table, Recommended Operating Conditions
table, thermal information table (θJA = 36.1°C/W), Electrical
Characteristics table (I2C address, protection thresholds), full register
map, and the Typical Application section's external-components table and
reference schematic were all read directly this session. Notably, this
also **corrects** DS-MTR-037's prior characterization: the DRV10983's
overcurrent protection (OCP) is a **fixed, non-configurable** hardware
threshold (3-4A, immediate Hi-Z, auto-clearing) — distinct from the
**configurable, auto-retry** Lock/Stall Detection feature
(`HWiLimitThr[2:0]`, 5s retry timer) which DS-MTR-037 had conflated with
OCP itself. See DS-MTR-058/059 in `datasheets/evidence-log.md` for the
corrected, separated citations, and
`hardware/schematic/bench-imu-01-design.md` §7.5.5 for the full protection
mechanism write-up (REQ-111/404). This correction is flagged for the
Hardware Reviewer/Hardware Lead to reconcile with
`bom/component-selection.md`'s own DS-MTR-037 citation, which is not
modified here (out of this agent's scope per
`.github/agents/circuit-engineer.agent.md` — BOM/component-selection
content is not touched by the Circuit Engineer).

## Known gaps (honestly flagged, not guessed) — mostly historical, see Update above

- ~~Package thermal resistance (theta-JA) and the exact thermal-shutdown
  threshold/behavior were not available from the HTML pages fetched this
  session — recorded as `UNKNOWN`.~~ **Resolved 2026-09-04**: θJA =
  36.1°C/W (DS-MTR-055), confirmed directly from the datasheet's own
  thermal information table. ~~Package body dimensions (24-HTSSOP) beyond
  the pin count/pitch were likewise not independently confirmed.~~ Full
  24-pin HTSSOP pinout with exposed thermal pad (tied to GND) is now
  confirmed (DS-MTR-052); exact millimeter body-outline dimensions were
  still not independently extracted this session (not needed for any
  design decision beyond the already-known pin/pitch count).
- This is the **recommended driver candidate**, paired with the T-Motor
  MN2206-13 2000KV motor recommendation — see
  `bom/component-selection.md` "Motor Driver IC" section for full
  compatibility/trade-off reasoning. Its data here is now **primary-PDF
  verified** (upgraded from the prior HTML-product-page-only confidence
  level) as of the 2026-09-04 Update above.

## Update (Firmware Engineer, 2026-09-10, Bench-IMU-01 Rev 3 motor bring-up firmware)

Re-fetched the primary PDF this session (same `r.jina.ai` text-extraction
proxy, same URL already cited above) to extract the register-level facts
needed to actually write `drv10983.c`, none of which were yet captured by
DS-MTR-032–071: the I2C slave address (0x52, DS-MTR-072), the
DevCtrl/EECtrl register-mode-vs-EEPROM-commit mechanics including the
0xB6/eeWrite EEPROM-programming key (DS-MTR-073 — decisive evidence for
this firmware's register-mode-only design choice, since this board's motor
rail voltage can never reach the EEPROM-write precondition), the FaultCode
(0x1E) bit layout (DS-MTR-074), the MotorSpeed1/2 registers together with
TI's own explicit "up to 6% error, use FG instead" guidance (DS-MTR-075 —
the primary-source justification for this firmware using the FG/TIM3
tachometer, not an I2C speed-register read, as REQ-405's actual overspeed-
enforcement measurement), and the full Op2ClsThr numeric table (DS-MTR-076,
supplementing DS-MTR-063's already-established qualitative mechanism with
the concrete Hz range and this part's factory-default value). All five new
rows cite this same datasheet record; no new metadata file was needed.

## Update (Firmware Engineer, 2026-09-12, Firmware Reviewer Finding 1 loop-back fix)

Re-read the already-cached primary-PDF text (same `r.jina.ai` extraction
already used for the 2026-09-10 Update above, same URL) to source two more
register-level facts needed for REQ-405's **command-side** ceiling — the
fix for the first-ever Firmware Reviewer cycle's Finding 1 (HIGH, PR #14,
`firmware/bench-imu-01/bench-imu-01-firmware-review.md`): §8.4.5.3
"Digital PWM Input Mode Speed Control" (pages 29–30), confirming the
firmware's `SPD` value maps **linearly, with no offset**, onto U5's own
internal Speed Command (DS-MTR-077, new); and §8.3.3 "Motor Speed Control"
(pages 16–17), confirming peak output amplitude = VCC × (PWM_DCO/100) with
AVS/current-limit/closed-loop-accelerate only ever able to *reduce* actual
output relative to that linear estimate, never increase it (DS-MTR-078,
new). Combined with this datasheet's own already-cited DS-MTR-017 (M1's
KV=2000 RPM/V rating) and this design's own 13.0V worst-case `VM_MOTOR`
envelope (`hardware/schematic/bench-imu-01-design.md` §7.5.9/§7.5.10, not
part of this datasheet record), these two new rows are the primary
evidence behind `motor.c`'s new `MOTOR_MAX_CMD_DUTY_PCT`=23 command-side
reject threshold — see `firmware/bench-imu-01/src/motor.h` and
`firmware/bench-imu-01/bench-imu-01-firmware-design.md` §4.3 for the full
derivation, its confidence marking, and its disclosed load-dependence
limitation. Both new rows cite this same datasheet record; no new metadata
file was needed.
