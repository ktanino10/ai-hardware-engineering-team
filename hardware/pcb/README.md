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
ordering) plus the post-review fix rounds below, `kicad-cli pcb drc`
reports **~365-380 violations (real run-to-run non-determinism confirmed
by two independent sets of repeated runs — this session's own 4 runs:
365/373/371/365; Hardware Reviewer Cycle 7's own independent 4 runs:
379/379/370/368, against a 377 baseline re-run), 0 unconnected items
(stable/deterministic across every run by both parties, both before and
after the fix rounds)** (updated 2026-09-02, final state after Hardware
Reviewer Cycles 6 and 7 (plus a Cycle 7 follow-up) and two same-day PCB
Engineer fix rounds — see below; pre-review baseline was ~370-377, with
a transient regression to ~380-400 mid-fix, now back within the same
baseline band). The table below reflects one representative run (365):

| Category | Count | What it means |
|---|---|---|
| `solder_mask_bridge` | 202 | Different-net copper close enough that the solder mask openings would merge |
| `tracks_crossing` | 78 | Different-net traces geometrically crossing on the same layer |
| `shorting_items` | 65 | Different-net copper items geometrically touching (a true short if fabricated as-is) |
| `clearance` | 15 | General spacing below the configured minimum |
| `hole_clearance` | 4 | Via/drill spacing below the configured minimum |
| `silk_overlap` | 1 | Cosmetic silkscreen-only overlap |

**Post-review fix rounds (2026-09-02, two rounds same day)**: Hardware
Reviewer Cycle 6 (`validation/design-review.md`, commit `84db343`) found
the previous "0 unconnected items" was misleading — a `generate_pcb.py`
bug (`FindPadByNumber()` nets only the first physical pad when a
footprint legitimately has several sharing one pad number: U6's
17-sub-pad PowerPAD, J1's 4-pad USB shield, SW1's doubled terminal pads)
meant several physical pads were never netted at all, a defect class
DRC's `unconnected_items` check cannot see — ISS-033/034/035. **Round
1** fixed this by enumerating every matching physical pad and locally
bridging them to an arbitrary representative pad; this introduced a NEW
defect caught by an independent focused re-review, Hardware Reviewer
Cycle 7 (`validation/design-review.md`, commit `89a158c`): the bridge
tracks under U6's PowerPAD were redundant (all pads already share copper
via the exposed-pad land) yet crossed the unrelated `U6_ILIM` net 12
times — ISS-038. **Round 2** fixed the actual root cause: the bridging
step had picked `matching_pads[0]` (an arbitrary small 0.6×0.6mm
thermal-via pad) as its reference/hub point, so neighbour-to-neighbour
bounding-box tests against other equally-small vias never intersected
(vias 1.3mm apart don't touch each other directly), even though all of
them sit inside the much larger shared F.Cu/B.Cu exposed-pad land pads
that are also members of the same pad-number group. Selecting the
largest-bounding-box-area pad as the hub instead correctly recognizes
the land as the true connection point — U6's PowerPAD group now needs
**0** bridge tracks (was 16), while J1's shield (3 bridges) and SW1's
terminal pads (1 bridge each) — which have no single large land pad and
so still need one — are unaffected. **Independently re-verified after
each round** via a standalone pad/net audit script (not just re-trusting
the same DRC proxy that missed the original bug), and this fix round's
own claims were themselves independently re-fact-checked in a Cycle 7
follow-up pass (commit `f55d8f7`) rather than accepted at face value:
all of U6's 17 sub-pads, J1's 4 shield pads, and SW1's duplicate pads
share their correct single net; `GND`-vs-`U6_ILIM` crossings dropped
12 → **0** board-wide (this session's own first re-check had
mis-attributed one nearby, unrelated `GND`-vs-`DIR` violation as an
`ILIM` crossing — a real error, caught and corrected by the follow-up
review, not by this session catching it unprompted). Net result:
connectivity is now genuinely complete (not just DRC-proxy-silent)
**and** the total violation count (~365-380) is back within the same
band as the original ~370-377 pre-fix baseline — **not** strictly
at-or-below it as first (over-confidently) claimed; the honest framing,
per the follow-up review, is "within the baseline band," not "an
improvement." See `validation/open-issues.md` ISS-033/034/035/038 (all
RESOLVED) and ISS-036 (still OPEN — updated with the current count).

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

**Cycle 6 outcome (2026-09-02) and the fix rounds that followed**:
CONDITIONAL, with 1 CRITICAL + 5 HIGH + 2 MEDIUM findings (ISS-030
through ISS-037). This session fixed and independently re-verified
ISS-030 (CRITICAL — U1 pin 19/PA9 alternate-pin-function omission broke
the `/U6_EN` net entirely; schematic patched, ERC + netlist
re-confirmed), ISS-033/034/035 (HIGH/HIGH/MEDIUM — multi-pad
net-assignment bug; PCB script patched, independent pad/net audit
re-confirmed), and partially addressed ISS-031 (HIGH — U5's missing
EP/pin-25 schematic definition is now fixed and wired to GND, but the
footprint's own thermal-via-array gap is unchanged and still open).

**Cycle 7 (`validation/design-review.md`, commit `89a158c`)** — a
focused, narrowly-scoped Hardware Reviewer re-verification pass mirroring
this project's own Cycle-5 precedent (a CRITICAL/HIGH loop-back fix gets
an independent focused re-check, not just author self-attestation) —
**independently confirmed** the ISS-030/033/034/035 fixes were genuinely
correct (re-derived from its own ERC/netlist/DRC/pad-audit runs, not from
this session's commit message), and caught a real NEW defect in the
ISS-033/034/035 fix itself: the bridging tracks added under U6's
PowerPAD were redundant and crossed the unrelated `U6_ILIM` net 12 times
— **ISS-038 (HIGH)**. This is exactly the kind of defect an independent
review step exists to catch, and it worked as intended. ISS-038 was
fixed the same day (root cause: the bridging logic's hub-pad selection
picked an arbitrary small via instead of the actual shared copper land;
fixed by hubbing on the largest-bounding-box-area pad in each group).

**Cycle 7 follow-up (`validation/design-review.md`, commit `f55d8f7`)**
— a second, even more narrowly-scoped re-check of just the ISS-038 fix —
**confirmed the fix holds up**, but also caught **two factual errors in
this session's own first self-verification of that fix**: this session
had claimed `GND`-vs-`U6_ILIM` crossings dropped to 1 remaining
(actually 0 — the "1" was a different, pre-existing `GND`-vs-`DIR`
violation, misattributed), and had claimed the resulting violation count
was "at or below the original baseline" (the reviewer's own independent
re-runs — 379/379/370/368 against a 377 baseline re-run — show this
over-read the DRC tool's own run-to-run non-determinism; "back within
the same baseline band" is the accurate framing). Both corrected in
`validation/open-issues.md` and above once the independent check flagged
them — see the DRC status section above for the corrected final numbers.
This is disclosed plainly rather than quietly fixed, because it is a
useful, real illustration of exactly why this project requires
independent review rather than author self-attestation, twice over in
this same session.

ISS-031 (footprint thermal-via-array gap), ISS-032 (J4 GND-hijack
safety-argument gap), and ISS-036 (bulk DRC closure — the majority of
category counts remain individually unattributed) remain untouched/open.
**The board is still not declared ready to fabricate** — see
`validation/open-issues.md` for authoritative, current status per
finding, and the Design Complete gate (`tools/check_open_issues.py`)
still correctly fails on the 3 remaining open HIGH items (ISS-031,
ISS-032, ISS-036). Per the reviewer's own follow-up, §8's Design Complete
gate additionally still needs `requirements/traceability-matrix.md` fully
verified/waived, `validation/fmea.md` reviewed, and a
`validation/change-log.md` (ECO) entry for this revision — none of which
were in this session's scope to produce.
