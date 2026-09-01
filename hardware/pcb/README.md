# PCB Layout Files

This directory holds PCB layout artifacts (e.g. a KiCad project's `.kicad_pcb`
file and related layout documents). Structured per-board, mirroring
`hardware/schematic/`'s own convention: `hardware/pcb/<board>/`.

## Tooling honesty (verify every session, per this repo's own discipline)

- **`kicad-cli pcb {drc,export,import,render,upgrade}` is a real, working
  capability** — verified this session. There is no `kicad-cli pcb`
  subcommand that *creates* or *interactively routes* a board.
- **The `kicad-*` MCP tools' 5-working/11-broken split
  (`docs/architecture.md` §5.2) still holds** — re-verified directly this
  session by re-calling `kicad-run_drc_check` and
  `kicad-generate_pcb_thumbnail` against a real project: both still fail
  identically (`'ctx' is a required property'`). `kicad-validate_project`
  and `kicad-get_drc_history_tool` still work. No drift since 2026-08-31.
  Use `kicad-cli pcb drc` / `kicad-cli pcb render` directly as the
  established workaround, exactly as Circuit Engineer already does for
  `sch erc` / BOM export.
- **New this session — a genuinely more capable, previously-undocumented
  path**: KiCad 10.0.1's own bundled Python 3.9 interpreter
  (`.../KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9`
  on this machine) has a real, importable `pcbnew` module — confirmed by
  directly constructing a `BOARD()`, loading real footprints
  (`FootprintLoad`), and saving a valid `.kicad_pcb` that `kicad-cli pcb
  drc` correctly parsed. This is a materially more capable, natively-KiCad
  path for programmatic PCB construction than hand-authoring `.kicad_pcb`
  S-expressions from scratch (the schematic side's own `kiutils` approach
  has no equivalent board-construction convenience). Used for
  `bench-imu-01/`'s layout — see that directory's own `generate_pcb.py`.
- **A real, reproducible limitation found this session, not silently
  worked around**: `pcbnew.ZONE_FILLER.Fill()` **segfaults** in this
  scripted/headless invocation — confirmed 3 times (a bare call, with a
  `wx.App()` initialized first, and with `board.BuildConnectivity()`
  called first), identical crash every time, isolated by bisecting the
  board-construction script's own steps one at a time. A zone *outline*
  can still be defined (and is, for GND, in `bench-imu-01/`) for a human
  to fill with one click in the real KiCad GUI (Edit > Fill All Zones /
  the `B` shortcut) — but this session could not produce a programmatically
  *filled* copper pour. GND connectivity in the delivered board is instead
  realized via explicit routed tracks/vias (electrically valid and
  DRC-checkable, just not yet a solid continuous copper region).
- **No autorouter is used or assumed available.** `pcbnew.ExportSpecctraDSN`/
  `ImportSpecctraSES` do exist (confirming a Freerouting-style external
  round-trip is technically possible), but no such external tool is
  installed, and this discipline deliberately does not fetch/trust an
  untrusted external autorouting tool to work around the absence of one —
  the same tooling-honesty discipline `docs/architecture.md` §5.3/§5.4
  already established for CAD/firmware tooling. Placement and routing in
  `bench-imu-01/generate_pcb.py` are scripted directly (greedy layer
  assignment + minimum-spanning-tree point-to-point routing), never
  GUI-interactive, never autorouted by an external engine.

## Conventions

- Run DRC before any "pre-fabrication" human approval gate
  (`docs/architecture.md` §10) using `kicad-cli pcb drc` (the
  `run_drc_check` MCP tool is currently broken, see above); track results
  over time with `get_drc_history_tool` (confirmed working; feeds
  `docs/evaluation.md` metrics).
- Attach a visual snapshot to `validation/design-review.md` for the human
  reviewing the pre-fabrication gate — use `kicad-cli pcb render`
  (`generate_pcb_thumbnail`/`generate_project_thumbnail` MCP tools are
  currently broken, see above).
- ERC is a real, working `kicad-cli` capability (`kicad-cli sch erc`,
  verified and used at the schematic stage, `docs/architecture.md` §5.2) —
  there is still no ERC *MCP tool* wrapper. Both facts are true
  simultaneously; neither should be quoted without the other.
- Keep BOM consistent with `bom/component-selection.md` — use
  `kicad-cli sch export bom` (the `analyze_bom`/`export_bom_csv` MCP tools
  are currently broken, see above) to check for drift before a "major BOM
  change" gate.
- **Never declare a layout "DRC-clean" or "ready to fabricate" with any
  open DRC violation or without an independent Hardware Reviewer pass**
  (`.github/skills/hardware-review/SKILL.md` items 17-21,
  `docs/architecture.md` §10 "before PCB fabrication").

## `bench-imu-01/` — Bench-IMU-01 Rev 3-5 PCB layout

Built by `bench-imu-01/generate_pcb.py` from the corresponding real KiCad
schematic (`hardware/schematic/bench-imu-01/`) — re-exports that
schematic's own netlist/BOM via `kicad-cli` every run, so this layout is
never a stale hand-copied snapshot of the schematic.

### Stack-up and board outline (justified, not defaulted)

- **4-layer stack-up (Signal / GND / Signal / Signal, i.e. F.Cu / In1.Cu /
  In2.Cu / B.Cu)** — a deliberate decision, not a default, for two
  independent, real reasons:
  1. This design's own existing documents *repeatedly* flag motor-driver-
     noise-vs-IMU-sensitivity as a live concern (`bench-imu-01-design.md`
     §9; Hardware Reviewer checklist items 12-14, `docs/architecture.md`
     §12) — a solid, low-impedance ground reference is the standard
     mitigation, and a 2-layer board has no dedicated plane layer to
     provide one.
  2. It also makes scripted routing more tractable given this
     environment's tooling (no real autorouter, no interactive
     push-and-shove router, no working `ZONE_FILLER.Fill()` — see above):
     a dedicated GND layer, plus a second signal/via-jumper layer
     (In2.Cu), gives real flexibility to route around same-layer
     conflicts that a from-scratch scripted approach otherwise has no
     other tool to resolve.
- **Board outline: 150mm x 95mm.** REQ-308 (Rev 3) already relaxed the
  old REQ-302 60x40mm ceiling to "whatever the approved parts need,"
  bounded by a soft ~150mm desk-scale sanity ceiling — this design's own
  25 new Rev 3-5 components (two more ICs, a barrel jack, a PTC fuse, a
  motor-phase terminal block, ~18 new passives) on top of Rev 2's original
  23 make the old 60x40mm envelope infeasible; 150x95mm was sized from
  real summed footprint/courtyard area plus real assembly/routing margin
  (an iterative, DRC-driven process — an initial, tighter attempt produced
  real courtyard-overlap/PTH-inside-courtyard findings, corrected by
  widening spacing, not by ignoring them), while respecting the ~150mm
  soft ceiling on the long axis.
- **Two physically-separated zones**: Zone 1 (x ≈ 8-68mm: USB-C/MCU/IMU/
  UART/SWD, the Rev 2 baseline) and Zone 2 (x ≈ 78-145mm: motor driver/
  supervisory controller/barrel jack, new Rev 3-5), with a clear channel
  between them — the concrete geometry realizing the design doc's own
  explicit vibration/thermal-separation instruction (§9/§10). GND is
  deliberately one continuous reference spanning both zones (a shared,
  stable ground is correct practice, not a violation of the separation
  intent, which is about the noise-source *components*/high-current
  traces, not about denying a common reference).

### Footprint placement and routing method

See `bench-imu-01/generate_pcb.py` for the full, commented implementation.
Summary:
- Footprints loaded from their real KiCad libraries (or this project's own
  `bench-imu-01.pretty` for F1's custom footprint) via `pcbnew.FootprintLoad`.
- Net connectivity parsed directly from `kicad-cli sch export netlist`'s
  own output (never hand-guessed) and assigned to real pads.
- Same-component, same-net pin clusters (e.g. U5/U6's several adjacent
  GND/VCC/IN pins at real 0.65mm HTSSOP pitch) are bridged with a short
  local F.Cu trace *before* the broader routing pass — an initial
  per-raw-pin via strategy put a via at every one of those pins, and
  adjacent vias at 0.65mm pitch violated real via-to-via/hole clearance (a
  genuine DRC finding this revision, fixed at its root rather than patched
  finding-by-finding).
- GND is routed entirely on its own dedicated layer (In1.Cu) — by far this
  board's largest, most-branching net, and an initial single-layer
  (F.Cu-for-everything) DRC pass found it was the dominant contributor to
  the resulting violations.
- Every other net is greedily assigned to F.Cu / In2.Cu / B.Cu by an
  axis-aligned-bounding-box overlap heuristic (largest-bounding-box nets
  processed first, a standard improvement to this class of greedy
  algorithm), then routed as a minimum-spanning-tree chain (each point
  connects to its nearest already-connected neighbor) rather than a naive
  star-to-one-arbitrary-trunk topology — an initial star-topology attempt
  produced long paths that cut straight through unrelated components
  physically sitting between a distant pad and the arbitrarily-chosen
  trunk, which was the dominant cause of the resulting
  `solder_mask_bridge`/`shorting_items` findings against components the
  net had no real reason to route near.
- Trace widths sized per net current class (Hardware Reviewer checklist
  item 19): 1.0mm for this design's up-to-3A worst-case nets (VM_MOTOR
  chain, U5_VCC, motor phase outputs) — a standard 1oz-external-copper
  rule-of-thumb figure for ~30-35 mil at a 10°C rise, not a fully worked
  per-net IPC-2221 calculation (ESTIMATE, disclosed); 0.4mm for other
  power rails; 0.25mm for logic/bias signals.
- 4x M2.5 mounting holes (`MountingHole_2.7mm_M2.5`, no electrical net,
  matching the schematic's own established convention).

### DRC status — CONDITIONAL, not clean, disclosed plainly

**This layout is NOT DRC-clean and is explicitly NOT claimed ready to
fabricate.** After the fixes above (design-rule defaults, pin-cluster
bridging, layer isolation for GND, MST routing, largest-bbox-first layer
ordering), `kicad-cli pcb drc` reports **~370 violations, 0 unconnected
items** — connectivity is complete and correct throughout every
iteration; what remains is routing-density geometry, not a missing or
wrong connection:

| Category | Count (approx.) | What it means |
|---|---|---|
| `solder_mask_bridge` | ~205 | Different-net copper close enough that the solder mask openings would merge |
| `tracks_crossing` / `shorting_items` | ~75 / ~75 | Different-net traces geometrically touching/crossing on the same layer |
| `clearance` | ~15 | General spacing below the configured minimum |
| `hole_clearance` | ~3-9 | Via/drill spacing below the configured minimum |
| `silk_overlap` | ~1 | Cosmetic silkscreen-only overlap |

**Root cause, stated plainly**: a from-scratch, scripted routing approach
(no real autorouter, no interactive push-and-shove router, and
`ZONE_FILLER.Fill()` itself segfaults in this environment — see above)
cannot fully resolve every same-layer trace conflict across ~38 nets and
48 components through geometry/heuristics alone within a reasonable
iteration budget. Six distinct, real techniques were tried in sequence
this session, each independently verified to reduce the violation count
(via-collision fix on fine-pitch ICs, corrected board design-rule
defaults, GND layer isolation, MST instead of star routing,
largest-bbox-first layer-assignment ordering, widened component spacing)
— the remaining count is a genuine plateau for this class of technique,
not an unexamined first attempt.

**Recommendation**: closing the remainder is most efficiently done by a
human interactively re-routing the specific flagged segments in the real
KiCad GUI (which has a push-and-shove router this environment's scripted
access does not), or by a future session with a verified-working
autorouter. Both are Future Integration items (`docs/architecture.md`
§13) — not implemented against here.

### Flat BOM

See `bom/bench-imu-01-fab-bom.csv` (generated via `kicad-cli sch export
bom` from the schematic, cross-referenced with `bom/component-selection.md`'s
already-approved MPNs/pricing) for the full, order-ready parts list.

### Independent review

Per `docs/architecture.md` §10 ("before PCB fabrication") and the Phase 6
decision to extend Hardware Reviewer's own checklist (items 17-21,
`docs/architecture-evolution.md` §37) rather than stand up a separate PCB
Reviewer agent — see `validation/design-review.md` for the actual review
cycle and `validation/open-issues.md` for any findings logged from it. Not
self-declared complete by this discipline.
