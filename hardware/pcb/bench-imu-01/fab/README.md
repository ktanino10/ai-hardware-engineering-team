# `bench-imu-01/fab/` — Fabrication package

This directory holds the actual **submittable manufacturing files** for the
Bench-IMU-01 Rev 3-5 PCB layout — the files a fab house (JLCPCB, PCBWay, OSH
Park, etc.) needs to actually build the board, as distinct from the KiCad
project files (`../bench-imu-01.kicad_pcb` / `.kicad_pro`) one level up,
which are the *editable design source*, not something you upload to place an
order.

**This is a read-only export of the already-approved, already-merged board**
(PR #17, commit `9a46e2e`). No geometry, footprint, routing, or stack-up
decision was made or changed to produce this package — see
`validation/change-log.md` ECO-036 for the formal record of this export.

## What's in this directory

| File | What it is |
|---|---|
| `bench-imu-01-gerbers.zip` | RS-274X Gerbers (all 11 fab layers) + Excellon drill files (PTH/NPTH) + drill maps + a Gerber job file, flat inside the zip (no wrapper folder) — upload this single file to a fab house |
| `bench-imu-01-positions.csv` | Pick-and-place (CPL) position file, both board sides, mm units — for assembly houses |
| `README.md` | This file |

### Inside `bench-imu-01-gerbers.zip` (16 files, verified)

| File | Layer / purpose |
|---|---|
| `bench-imu-01-F_Cu.gtl` | Top copper (F.Cu, signal) |
| `bench-imu-01-In1_Cu.g1` | Inner layer 1 (In1.Cu, **dedicated GND plane/routing layer**) |
| `bench-imu-01-In2_Cu.g2` | Inner layer 2 (In2.Cu, signal) |
| `bench-imu-01-B_Cu.gbl` | Bottom copper (B.Cu, signal) |
| `bench-imu-01-F_Paste.gtp` / `-B_Paste.gbp` | Solder paste stencil layers, top/bottom |
| `bench-imu-01-F_Silkscreen.gto` / `-B_Silkscreen.gbo` | Silkscreen legend, top/bottom |
| `bench-imu-01-F_Mask.gts` / `-B_Mask.gbs` | Solder mask, top/bottom |
| `bench-imu-01-Edge_Cuts.gm1` | Board outline |
| `bench-imu-01-job.gbrjob` | Gerber X2 job file (machine-readable stack-up summary) |
| `bench-imu-01-PTH.drl` / `-NPTH.drl` | Excellon drill files, plated / non-plated holes, separated |
| `bench-imu-01-PTH-drl_map.pdf` / `-NPTH-drl_map.pdf` | Human-readable drill maps |

## Exact commands used (reproducible)

Run from the repo root, against the current
`hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb`. If the design ever
changes, re-run these exact commands to regenerate the package — never
hand-edit the exported files.

```sh
# Gerbers — RS-274X, all layers a fab house needs
kicad-cli pcb export gerbers \
  --output <staging-dir> \
  --layers F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb

# Drill files — Excellon, plated/non-plated separated, with a map
kicad-cli pcb export drill \
  --output <staging-dir> \
  --format excellon \
  --excellon-separate-th \
  --generate-map \
  hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb

# Pick-and-place position file — both sides, CSV, mm
kicad-cli pcb export pos \
  --output hardware/pcb/bench-imu-01/fab/bench-imu-01-positions.csv \
  --format csv \
  --units mm \
  --side both \
  hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb

# Zip the Gerber+drill staging dir flat (no wrapper folder) into the package
cd <staging-dir> && zip -X -j bench-imu-01-gerbers.zip ./*
```

`<staging-dir>` is a scratch directory outside the repo — the loose Gerber/
drill files themselves are intentionally **not** committed individually,
only the zip (and the position CSV, kept unzipped since assembly houses
typically want it as a directly-readable file).

## Verification performed before committing

- **Format**: spot-checked `bench-imu-01-F_Cu.gtl`/`-In1_Cu.g1` headers —
  genuine RS-274X (`%FSLAX46Y46*%`, `G04 Gerber Fmt 4.6...`), not a
  placeholder/stub. `bench-imu-01-PTH.drl`/`-NPTH.drl` genuine Excellon
  (`M48`/`FMAT,2`/`METRIC`).
- **Layer count**: `bench-imu-01-job.gbrjob`'s own `GeneralSpecs.LayerNumber`
  field reports **4** copper layers (L1/Top, L2/Inr, L3/Inr, L4/Bot) —
  matches the board's actual F.Cu/In1.Cu/In2.Cu/B.Cu stack-up (confirmed
  directly against the `.kicad_pcb` file's own `(layers ...)` section, not
  assumed).
- **Board size**: job file reports **150.15 × 95.15mm** (includes the
  Edge.Cuts stroke width); independently cross-checked a second way by
  parsing the `.kicad_pcb` file's own Edge.Cuts rectangle directly —
  **150.0 × 95.0mm** nominal outline (the 0.15mm/axis difference is the cut
  line's own stroke width, not a discrepancy). Both consistent with
  `hardware/pcb/README.md`'s documented "150mm x 95mm" board outline
  decision.
- **Drill counts**: 101 plated holes (vias + component through-holes), 6
  non-plated holes.
- **Position file**: 49 placed-component rows. This is intentionally fewer
  than the BOM's 51 line items / 53 total footprint instances — the 4x M2.5
  mounting-hole footprints (`MH1`-`MH4`, one BOM line, qty 4) are mechanical
  drill points with no part actually placed by assembly equipment, and
  KiCad's `MountingHole_*` library footprints are marked "exclude from
  position files" by default. 53 (kicad_pcb footprints) − 4 (mounting
  holes) = 49, reconciled exactly.
- **Zip integrity**: `unzip -l` confirms 16/16 expected files;
  `unzip -t` reports "No errors detected in compressed data" for all 16.
- **Position file integrity**: MD5-verified identical between the export
  staging location and the committed copy.
- **No design-file drift**: `git diff --stat` confirms this export touched
  only new files under this `fab/` directory (plus one `validation/
  change-log.md` row) — `bench-imu-01.kicad_pcb`, `.kicad_pro`,
  `generate_pcb.py`, the schematic, and `validation/open-issues.md` are all
  byte-for-byte unchanged.

## What this package does — and does NOT — claim

**This package is submittable to a fab house, but it is not a claim that
placing a real fabrication order has been authorized.** Producing these
files is the same class of action as the Mechanical Lead's STL export
(`validation/change-log.md` ECO-032) — a derived-artifact export of an
already-approved design, not a new engineering or purchasing decision.
Actually spending money with a real vendor remains a separate human action.

**This package reflects the board exactly as the human Chief Engineer
accepted it — not as a "fully clean" design:**

- `validation/open-issues.md` **ISS-036 (HIGH) is `ACCEPTED-RISK`**, not
  `RESOLVED`. At disposition time, **~350-365 DRC violations remained**,
  none individually triaged/resolved/justified — the Chief Engineer's own
  instruction was literally "Accept risk" (`validation/change-log.md`
  ECO-035), a disclosed, real trade-off, not a claim that the layout is
  clean. **Do not read this fabrication package as "DRC-clean" or "fully
  verified" — it is not.** See `hardware/pcb/README.md`'s own "DRC status"
  section and `validation/open-issues.md` ISS-036 for the authoritative,
  itemized violation breakdown and rationale.
- The project-wide Design Complete gate (`docs/architecture.md` §8) is a
  broader claim than this PCB-layout scope covers — e.g.
  `requirements/traceability-matrix.md` still shows an open item outside
  Electronics/PCB scope (Rev 4 firmware, REQ-013) per ECO-035's own notes.
  This README makes no claim about that broader gate.

### BOM sourcing (`bom/bench-imu-01-fab-bom.csv`) — resolved 2026-09-02, updated from the original 24 OPEN ITEM rows

**Update, same day, following Kyosuke's direct request to resolve BOM
sourcing**: all 24 of the rows this section originally described as
"OPEN ITEM" are now **CONFIRMED** with real, currently-orderable
manufacturer part numbers, each backed by a new Evidence ID in
`datasheets/evidence-log.md` (`DS-CONN-007/008`, `DS-SW-001`,
`DS-OPTO-001`, `DS-PASS-001` through `-005`, `DS-FAST-004/005`) and its
own metadata record under `datasheets/`. See `validation/change-log.md`
ECO-037 for the full change record. **Not resolved by this pass**: the
one pre-existing, unrelated `OPEN ITEM` note on U4 (real MPN already
selected; only its unit price wasn't independently re-quoted) — untouched,
out of scope for this update, exactly as it was before.

Real parts were consolidated where a single, appropriately-rated SKU
safely covers several BOM rows at once (a higher voltage rating always
covers a lower stated minimum — standard, not corner-cutting, practice):

| Real part | Covers | Why this rating |
|---|---|---|
| GCT USB4105-GF-A (J1) | J1 | Matches this exact footprint's own embedded KiCad tags; base part (no `-060`/`-120` thin-board suffix) fits this board's standard 1.6mm thickness; confirmed in stock (DigiKey/Mouser) vs. the sibling `USB4105-15-A` variant, which is not normally stocked |
| Sullins PREC004SAAN-RC | J2, J3 | Bare/unshrouded 2.54mm header — matches the plain KiCad footprint; deliberately not a shrouded/locking family (wrong physical footprint) |
| Omron/Aratas B3F-1000 | SW1 | Standard 6mm THT tactile switch |
| Lite-On LTST-C191KRKT | D1 | Red, Vf=2.0V typ — matches the design doc's own "Vf≈2.0V assumed" basis for R5's value; a blue/white/high-brightness-green LED would have silently invalidated that assumption |
| Samsung CL10B104KB8NNNC (100nF/0603/X7R/**50V**) | C3,C4,C5,C6,C7,C11,C12 | 50V clears C11's stated 10V minimum and C12's real ≥26V requirement (design's actual VM_MOTOR/VCC ceiling is 13.0V, not the datasheet's abstract 28V, so "≥VCC×2" = ≥26V here) |
| Samsung CL10B105KB8NNNC (1µF/0603/X7R/**50V**) | C1,C8,C9,C14,C15,C16 | 50V clears C14/C15's stated 5V minimum and C16's existing "≥16-25V rated" note |
| Samsung CL10B474KB8NNNC (0.47µF/0603/X7R/50V) | C2 | Same 3.3V-logic-domain family, no special requirement |
| Samsung CL21A106KAYNNNE (10µF/0805/X5R/**25V**) | C10, C13 | Matches `hardware/pcb/README.md`'s own stated "≥16-25V-class" target for these positions |
| Murata GRM1885C1H223JA01D (22nF/0603/**C0G**) | C17 | C0G (not X7R) chosen deliberately: C17 sets a timing/ramp-rate characteristic (U6 dVdT), where C0G's low tempco/tight tolerance is the more appropriate dielectric |
| Essentra 50M025045P005 (screw) / Würth 971050154 (optional standoff) | MH1 | Generic M2.5 hardware; screw is nylon (disclosed) — a metal/steel equivalent is an equally valid substitute, no material requirement stated by the design |

**Honestly disclosed, not silently smoothed over, in the process**:
- An initial search pass mis-stated Samsung CL10B105KB8NNNC's voltage
  rating as 25V; independently re-checked via 2 follow-up targeted
  searches and corrected to the actual 50V before citing it anywhere.
- A DigiKey search for CL10B474KB8NNNC surfaced a similar but distinct
  sibling part (`CL10B474KA8NNNC`, "A8" not "B8") — the correct "B8" part
  number was independently re-confirmed via Octopart/GlobalSpec rather
  than conflating the two.
- **DC-bias derating checked at this design's real ~9-13V operating
  point for C10/C13, not just their 25V nameplate rating** (per this
  task's own explicit instruction): Samsung's own published derating
  curve for this series shows only ~50-60% of nominal capacitance
  remaining at ~12V DC bias (≈5-6µF effective, not the full 10µF
  nameplate). This is a real, disclosed characteristic — consistent
  with, not contradicting, the existing design record's own reason for
  choosing 0805 over 0603 in the first place — not a new problem
  introduced by this sourcing pass, and not independently re-designed
  here (that would be a schematic-level decoupling-network change,
  outside a BOM-sourcing task's scope).
- A targeted search for a metal (steel/brass) M2.5 screw did not
  converge on one specific, confidently-verified distributor listing
  this session — rather than cite an uncertain metal-screw MPN, the one
  genuinely confirmed real part (nylon) is cited instead, with the
  material trade-off disclosed plainly rather than implied away.
- Several capacitor prices could not be confirmed to a single exact
  figure this session (disclosed as a range, or left blank with "not
  independently re-sourced," per each row's own Notes column) — real
  MPN/spec confirmation was prioritized over price precision.

**Still true, unchanged by this update**: this package reflects the board
exactly as ISS-036 ACCEPTED-RISK left it (see the section above) — BOM
sourcing and DRC/layout status are independent facts; resolving the BOM
does not change, and is not being represented as changing, the board's
DRC/ISS-036 status in any way.

## Regenerating this package

If `bench-imu-01.kicad_pcb` is ever revised, this entire `fab/` directory is
stale and must be regenerated from the new board file using the exact
commands above — never hand-patch an existing Gerber/drill/position file to
reflect a design change.
