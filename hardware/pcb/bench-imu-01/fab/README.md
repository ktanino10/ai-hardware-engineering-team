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

### BOM open items (`bom/bench-imu-01-fab-bom.csv`) — disclosed plainly, not resolved

The flat BOM has **24 "OPEN ITEM" rows out of 51 total line items**. These
are **not treated as resolved here** (per this project's own
"disclose, don't silently invent" convention) — but they are not uniform in
severity either; breaking them down honestly:

| Category | Count | Refs | What it actually means |
|---|---|---|---|
| Generic, multi-source passives/connectors/hardware | 21 | C1-C17 (ceramic caps, various values/packages), J2/J3 (2.54mm pin headers), SW1 (6mm THT switch), D1 (0603 LED), MH1-4 (M2.5 mounting hardware, 1 BOM line) | Standard, low-cost parts stocked by essentially every distributor under many interchangeable manufacturer SKUs. Package/value is already pinned down; only the *specific* manufacturer/exact orderable code wasn't picked, because doing so wouldn't be a meaningful engineering decision — any compliant SKU works. Sourceable at order time with no design input needed. |
| Already-selected part, pricing only not re-confirmed | 1 | U4 (USBLC6-2SC6 ESD protection) | Has a real manufacturer (STMicroelectronics) **and** a real MPN already — flagged `OPEN ITEM` only because this session didn't independently re-quote its unit price, not because the part itself is undecided. |
| Genuine open sourcing decision | 1 | J1 (USB-C receptacle) | The schematic's own design document explicitly states J1's exact MPN was never formally selected (footprint is illustrative, matched for pin count/height only against the GCT USB4105 family). This is the one BOM row that needs an actual sourcing decision — picking a specific 16-pin USB2.0-only USB-C receptacle MPN — before or at order time. |

**None of these 24 rows are being resolved to a specific manufacturer SKU by
this export** (out of scope per the task that produced this package) — they
are disclosed here in full, with their real distribution across
"trivially generic" vs. "one real gap" so a human placing an order knows
exactly what does and doesn't still need a sourcing call, rather than
either silently implying full BOM readiness or treating all 24 as equally
blocking.

## Regenerating this package

If `bench-imu-01.kicad_pcb` is ever revised, this entire `fab/` directory is
stale and must be regenerated from the new board file using the exact
commands above — never hand-patch an existing Gerber/drill/position file to
reflect a design change.
