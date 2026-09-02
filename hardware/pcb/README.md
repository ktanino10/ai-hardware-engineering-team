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
  **Correction/nuance (Chief Engineer, 2026-09-02, independently testing
  during the ISS-036 review)**: running `pcbnew.ZONE_FILLER(board).Fill(...)`
  against the *committed* board — which has one small pre-existing F.Cu
  zone, distinct from the GND-on-In1.Cu-as-discrete-tracks situation this
  session's own ISS-036 analysis is about — succeeded 4/4 times, no
  segfault. So the segfault is not universally reproducible across every
  possible zone/board state; it may be more state- or environment-dependent
  than "hard tooling wall" implies, similar to this project's own already-
  disclosed DRC run-to-run non-determinism. The Chief Engineer also
  confirmed filling that one pre-existing (unrelated) zone doesn't move
  the DRC needle either way (378 vs 380, noise-band) — so this is a real,
  useful data point about reproducibility, not a missed fix: the actual
  GND-on-In1.Cu zone this design would need filled to solve ISS-036's
  via-through-GND-layer root cause was not the zone tested, and remains
  unverified either way. Recorded here for whoever picks this up next,
  rather than left as a stale, overstated "confirmed segfault" claim.
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
  item 19): 1.0mm for this design's motor-domain nets (VM_MOTOR chain,
  U5_VCC, motor phase outputs) — sized against DRV10983's **continuous**
  2A/phase rating (DS-MTR-034), not its 3A start-up/locked-rotor figure
  (DS-MTR-056), a real continuous-vs-fault distinction, not an
  interchangeable pair. Per the IPC-2221 external-layer formula
  (`I = 0.048 x dT^0.44 x A^0.725`, 1oz copper), 2A at a 10°C rise needs
  ≈31 mil (≈0.79mm) — 1.0mm (≈39mil) provides real margin above that,
  independently re-derived and cross-checked against a published
  IPC-2221 reference table this cycle (ESTIMATE/rule-of-thumb, not a
  fully worked per-net thermal/copper-pour-proximity calculation, but
  now with the correct current basis and rise target, not conflated with
  each other). **Corrected (Hardware Reviewer finding ISS-037, MEDIUM)**:
  this section previously cited "~30-35 mil at a 10°C rise" for a 3A
  worst-case current — that specific figure is actually closer to the
  width needed at a ~20°C rise for 3A (independently verified: ≈35.5 mil
  at 3A/20°C vs. ≈54 mil at 3A/10°C), a real internal inconsistency, not
  a rounding difference; 0.4mm for other power rails; 0.25mm for
  logic/bias signals.
- **Trace-width consistency, not just magnitude (also ISS-037)**: the
  routing script's same-component pin-cluster bridging step (used for
  fine-pitch multi-pin-same-net clusters, e.g. U5's two physical pins per
  motor phase and its two VCC pins) previously hard-coded a flat 0.25mm
  width for every bridge regardless of net class, producing a narrow
  ~0.25mm "stub" immediately at the pad on 5 motor-domain nets
  (`MOTOR_PHASE_U/V/W`, `U5_VCC`, `VM_MOTOR`) even though the rest of
  each net was correctly sized at 1.0mm — a trace is only as strong as
  its narrowest point, so this defeated the sizing above. Fixed: the
  bridging step now selects its width the same way the main routing step
  already does (by net current class), so every segment of a given net
  is sized consistently. Independently re-verified via a standalone
  per-net trace-width audit: all 5 previously-affected nets are now
  uniformly 1.0mm end to end (one apparent "0.6mm" segment on
  `VM_MOTOR_F1` found during this audit is a via's drill/annular
  diameter, not a track segment — confirmed by object type, not a
  stub-width defect).
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

### Continued iteration (2026-09-02, per Chief Engineer disposition after independently auditing PR #17)

The Chief Engineer independently re-verified the CONDITIONAL PR above (own
DRC re-run, own status spot-check, own BOM MPN spot-check — all matched)
and gave explicit authority to keep closing findings rather than stop at
CONDITIONAL. This round:

- **ISS-031 (HIGH) — RESOLVED.** The remaining half (footprint's missing
  thermal-via array) is fixed: U5's footprint switched to a real, standard
  KiCad library part with an 18-via thermal array, independently
  re-verified (ERC, pad/net audit, DRC). See the ISS-031 fix commit and
  `validation/open-issues.md` for full detail.
- **ISS-037 (MEDIUM) — RESOLVED.** Both the IPC-2221 citation math and the
  5-net trace-width stub-segment bug are fixed and independently
  re-verified (a standalone per-net trace-width audit, DRC re-run). See
  the ISS-037 fix commit.
- **ISS-032 (HIGH) — a genuine design-level fix attempted, NOT yet marked
  RESOLVED.** Per the Chief Engineer's explicit request, a real circuit
  fix was attempted before considering escalation: **F2**, a second
  Littelfuse 30R500UF PTC resettable fuse (identical to F1), now in series
  between J4's sleeve/GND pin and the shared ground net. This makes the
  worst case safe regardless of which physical J4 pin actually turns out
  to be tip vs. sleeve, without needing to resolve that ASSUMPTION —
  exactly the property the Chief Engineer asked whether a second
  protective element could achieve. Full reasoning, component selection,
  and the corrected/narrowed safety-argument text are in
  `hardware/schematic/bench-imu-01-design.md` §7.5.9. Self-verified this
  session (ERC clean; a pad/net audit confirms F2's own connectivity; DRC
  stays within the baseline band, 369-380 violations across repeated
  runs, 0 unconnected) — but **this project's own established convention
  is that the fixing author does not self-declare a finding RESOLVED; the
  independent reviewer does, after their own re-verification** (confirmed
  this cycle by checking how ISS-026 was actually closed: the Rev 6 fix
  commit itself left the finding's status untouched, and only the
  subsequent Cycle-5 reviewer commit set it to RESOLVED). `ISS-032`'s
  Status is therefore intentionally left **OPEN** in
  `validation/open-issues.md`, with the fix and this session's own
  verification recorded in its Notes column, pending independent review.
  This is a genuine electrical-topology change (normally Circuit-Engineer
  scope, not PCB Engineer) — made here only because the human Chief
  Engineer coordinating this cross-branch task explicitly directed it as
  a deliberate, disclosed exception, not a silent role-boundary violation.
- **ISS-036 (HIGH) — real root-cause analysis added, not yet individually
  triaged/fixed.** Used `kicad-cli pcb drc --format json`, parsed
  programmatically, to break the bulk violation counts down by net-pair
  and item-type rather than leave them as one undifferentiated number.
  Headline finding: **61% of `shorting_items` involve GND** and would
  very likely be genuine electrical faults if fabricated as-is (e.g. 8x
  `VBUS_5V`-vs-`GND`, 5x `3V3`-vs-`GND`) — confirming the HIGH severity
  classification is evidence-backed, not an unexamined suspicion. Of
  those, **48% are a specific, identified root cause**: ordinary
  through-vias (any non-GND net) physically crossing In1.Cu — the
  dedicated GND layer — at points where a GND track also runs there,
  because GND is routed as discrete tracks (not a filled zone with
  automatic net-based via clearance, since `ZONE_FILLER.Fill()` still
  segfaults in this environment). Getting that tool working, or adding a
  dedicated post-routing via-relocation pass, is the single most
  tractable next step — **not attempted this session**: moving an
  already-placed via risks silently disconnecting whatever track
  segments terminate there, a real regression risk judged not worth
  taking without a wider verification budget than remained this session.
  See `validation/open-issues.md` ISS-036 for the full breakdown
  (net-pair table, item-type percentages, and the `tracks_crossing`
  100%-track-vs-track finding).

Design Complete gate status after this round: still fails, now on only 2
open HIGH items (ISS-032 pending review, ISS-036 root-caused but not yet
fixed), down from 3. Board still not declared ready to fabricate.

### ISS-036 real fix: GND is now an actual filled zone on In1.Cu (2026-09-02, Kyosuke's explicit go-ahead to resume real engineering work)

Kyosuke woke, was given the honest choice (accept the current risk, or
wait for a future dedicated session), and chose to make that "later" now
— explicitly authorizing a real attempt at option (a) from ISS-036's own
Notes: get `pcbnew.ZONE_FILLER.Fill()` working against the actual
GND-on-In1.Cu zone (not the unrelated F.Cu zone the Chief Engineer's own
earlier re-test happened to use).

**The segfault is real, but it isn't what it looked like.** Re-isolated
exactly when `Fill()` crashes vs. works, since the prior record looked
like unexplained flakiness (worked for the Chief Engineer, didn't for the
original session). It is not flaky: `Fill()` against this exact
zone/board segfaults **100% of the time** (3/3 attempts, including two
different placements within `generate_pcb.py`'s own construction — right
after the zone is declared, and again after every net's tracks/vias are
already placed; ordering isn't the variable) when called in the **same
process** that incrementally built the board via the `pcbnew` Python API.
It succeeds **100% of the time** (15+ direct calls across this session's
testing) against a board freshly reloaded via `pcbnew.LoadBoard()` from
an already-saved `.kicad_pcb` file — and a minimal from-scratch
reproduction (a single zone, no other complexity) doesn't crash
in-process either, so this is specific to *this* real, complex board's
in-memory construction state, not zone-filling in general. This
reconciles every prior conflicting report without needing to invoke
"non-deterministic": the Chief Engineer's own successful re-test loaded a
saved file; the original segfault reports were always from in-process
construction.

**Fix implemented in `generate_pcb.py` itself** (not a one-off hand
patch — regeneratable, per this project's own convention): build the
board exactly as before (GND still routed as explicit discrete tracks on
In1.Cu, the known-safe baseline — unconditionally, so a valid, fully
connected board is guaranteed regardless of what happens next), save it,
then reload that just-written file fresh into a brand new `BOARD` object
and attempt the fill there. If it succeeds (confirmed via
`zone.IsFilled()`, not just the return value), remove the now-redundant
discrete GND tracks on In1.Cu (vias stay — still needed to bring an F.Cu
pad down to the zone) and re-save. If the fill doesn't succeed for any
reason (a non-crashing failure, or if a future environment's segfault
turns out not to be fully eliminated), the script falls back to the
original, known-safe discrete-track behavior automatically — a real
segfault would still crash the whole script (Python cannot catch that),
but only *after* a valid, fully-connected board is already safely on
disk from the first save, never leaving a broken half-fixed board
committed.

**Verified, not just claimed — real DRC data, apples-to-apples:**

| Board | shorting_items (5 runs) | tracks_crossing (5 runs) | clearance (5 runs) | Unconnected |
|---|---|---|---|---|
| Pre-fix (actual last-committed board, backed up before this work) | 76-77 | 69-70 | 18 (constant) | 0 (all 5) |
| Control (unmodified script, freshly re-run — isolates regen noise from the fix itself) | 74-75 | 69-70 | 16-17 | 0 (all 5) |
| **Fixed (modified script, freshly re-run — the real committed state)** | **61-62** | 81-82 | 11 | 0 (all 5) |

Comparing **fixed against control** (both freshly regenerated, the only
apples-to-apples pairing — isolates the fix's own effect from ordinary
regeneration noise, which the pre-fix-vs-control gap shows is real but
small): **`shorting_items` drops ~17%, zero overlap across 5/5 runs each
side** — this is the category ISS-036 itself calls "closest to
representing an already-existing physical short," and it's the one this
fix's root-cause (via-through-GND-track punctures on In1.Cu) directly
targets. GND's own involvement in `tracks_crossing` is flat-to-slightly-
better (15/69 control vs. 12/82 fixed) — the increase in that category is
entirely among *other* net pairs, not GND-related, and the leading (not
fully confirmed) explanation is that KiCad's DRC engine appears to
suppress reporting more than one violation type at the same physical
location: removing a GND track that was co-located with an unrelated
tracks_crossing defect may simply have stopped masking a pre-existing
defect between two *other* nets, rather than created a new one. Whatever
the exact mechanism, **0 unconnected items in every single run, both
before and after** — GND connectivity is fully preserved (independently
confirmed: every GND pad and every GND via in this design's actual
footprint set falls inside the zone's poured area, so removing the
redundant tracks never orphans anything).

This is a genuine, reproducible, right-priority trade-off — unlike the
earlier reverted detour-based attempt (which improved `tracks_crossing`
at the cost of *worsening* `shorting_items`, the wrong category to trade
away), this fix improves the more safety-relevant category and completes
this design's own originally-intended stack-up decision (a real GND pour,
not a workaround) rather than adding a new one. It does **not** fully
close ISS-036: ~365-380 total violations remain, and the resolution bar
("every violation individually triaged") is not yet met — this is real,
verified, honest partial progress on the single most safety-relevant
category, not a claim of closure. Sent for independent Hardware Reviewer
verification before any RESOLVED/partial-closure disposition; PCB
Engineer does not self-declare this finding's status, same standing
convention as every other finding this session.

**Fresh Hardware Reviewer pass — verdict CONFIRMED (2026-09-02).** A
dedicated reviewer independently re-derived every key claim via their own
tooling: loaded the board directly in `pcbnew` (zone filled, 0 residual
In1.Cu GND tracks, all 29 GND vias inside the zone, 53 footprints
unchanged), independently re-ran DRC 15 times (0 unconnected every run,
`shorting_items`/`tracks_crossing`/every other category matching this
fix's own figures with no undisclosed regression), and read the
crash-safety code directly (confirmed the save-before-reload ordering
really does mean a hypothetical future segfault would leave a valid file
already on disk). No blocking finding.

### ISS-036 mechanism-level triage of the remaining violations (2026-09-02)

With the zone fix in place, re-triaged all 61 current `shorting_items`
violations by actual geometric mechanism (DRC's own JSON `pos`/
`description` fields cross-referenced against this design's own known
component placements), not just by net-pair percentages as the earlier
analysis did — a genuine further step into ISS-036's own "individually
triaged" resolution bar:

| Category | Count | Disposition |
|---|---|---|
| Benign (`<no net>` mechanical/unused pad on one side) | 3 (5%) | Confirmed harmless |
| `via_vs_inner_layer_copper` — 2 distinct instances, not one pocket (correction below) | 4 (7%) | Same mechanism class as this fix, different net/layer — see below |
| `via_vs_track_outer_layer` (F.Cu/B.Cu) | 28 (46%) | Disclosed autorouter-class gap (14 of these match the already-documented U5/U6 0.65mm fine-pitch package-proximity pattern, geometrically confirmed within 8mm of each IC's placed center) |
| `track_vs_pad` | 22 (36%) | Same disclosed gap |
| `track_vs_track` | 4 (7%) | Same disclosed gap |

**Correction (2026-09-02, per the Chief Engineer's own independent
re-verification — confirmed identically across 3 fresh DRC runs on
re-check)**: the 4-item `via_vs_inner_layer_copper` bucket was originally
described here as one uniform pocket "near J1" — that's only true for 3
of the 4. A GND through-via (spanning every copper layer, including
In2.Cu) sits directly on or immediately beside a `VBUS_5V` track routed
on In2.Cu near J1's own VBUS pad and a via cluster at
(29.9,25)/(45.9,25)mm — **3 instances**, all in that same location. **The
4th is a separate instance**: `I2C1_SDA` (via) vs `I2C1_SCL` (track) on
In2.Cu at (107.1,80.9)mm — 4.1mm from U5's placed center (110,78),
nowhere near J1 at all. Same underlying mechanism (a through-via of one
net conflicting with a different net's track on a shared inner layer),
but plausibly also related to the same 0.65mm fine-pitch
package-proximity characteristic already documented for U5/U6 in the
`via_vs_track_outer_layer` row above (U5's own I2C pins are physically
adjacent) — it just happens to manifest here as a via-vs-inner-layer-
track shape rather than the outer-layer via-vs-track/track-vs-pad shape
that pattern otherwise covers. **Not attempted this cycle, either
instance**: In2.Cu carries several different nets (unlike In1.Cu's single
dedicated GND net), so the "declare one zone, fill it" technique that
fixed the In1.Cu case doesn't directly generalize here — a real fix would
need a per-via, per-net clearance/reroute pass, exactly the class of
change the earlier reverted detour attempt already demonstrated produces
an unreliable mixed result on this board's actual geometry (see above).
Flagged as 2 specific, well-scoped candidates (J1-area ×3, U5-area ×1)
for the same future dedicated session Kyosuke already authorized for
option (b) (whole-board-aware routing), not attempted ad-hoc here.

Net effect: confirms, with actual mechanism-level evidence rather than
net-pair percentages alone, that the bulk of what remains (54 of 61,
89%) is the already-disclosed autorouter-class routing-density gap this
design has carried since its first DRC pass — not a fresh class of
defect — while narrowing the "still needs a real answer" subset to 2
specific, named, geometrically-distinct instances (not one pocket) with
an identified mechanism. Does not claim to have individually resolved
any of these 58 non-benign items; ISS-036 remains correctly OPEN and the
gate correctly still fails.

### ISS-036 whole-board-aware reroute fix (2026-09-02, Kyosuke's explicit "build real whole-board-aware routing capability now" go-ahead)

Kyosuke authorized resuming full engineering effort on option (b) from the
prior round: a real fix needs genuine whole-board collision awareness
before committing any route change, replacing the earlier reverted
detour's single-obstacle-only visibility. Built a dedicated
whole-board-aware collision-checking tool for this purpose, using
`pcbnew`'s own `SHAPE.Collide`/`SEG.Collide`/`SEG.Distance` geometry
primitives — the same geometry engine KiCad's own DRC uses internally,
not a hand-rolled distance approximation — to check every candidate
reroute path against the board's **entire** other-net copper set (all
tracks, vias, and pads on the same layer, not just the one obstacle being
routed around) before accepting it.

**The 4 named `via_vs_inner_layer_copper` targets from the prior triage:**

| Target | Result |
|---|---|
| J1-area cluster: GND through-via (at U3's pin 2) vs `VBUS_5V` In2.Cu track | **Fixed** — whole-board-clear detour found |
| J1-area cluster: GND through-via (at U4's pin 2) vs `VBUS_5V` In2.Cu track's bend point | **Fixed** — whole-board-clear detour found (both of the original bend's 2 segments replaced by 1 new path) |
| J1-area cluster (3rd instance, same mechanism) | **Fixed** — see above, all 3 J1-area instances resolved together |
| U5-area: `I2C1_SDA` via vs `I2C1_SCL` track, 4.1mm from U5 | **Confirmed genuinely intractable, not merely unattempted** |

The U5-area instance was directly measured, not assumed: the two vias are
placed at U5's own 0.65mm pin pitch, and with the design's 0.6mm via
diameter, the physical gap between their copper edges is only **0.05mm**
— below any usable clearance for a track to pass through regardless of
routing technique. This is a hard physical constraint (confirms, not
contradicts, the fine-pitch-package-proximity mechanism already
documented above), not a routing-algorithm artifact like the 3 J1-area
instances were.

**Integrated into `generate_pcb.py`** via a new `REROUTE_OVERRIDE` list +
`_apply_reroute_overrides()` function, mirroring the existing
`INNER_LAYER_OVERRIDE` convention already used for the zone-fill logic:
each entry names a net and the source track segment(s) to remove (matched
by net name + rounded endpoint position, in either direction — not object
identity or UUID, since a fresh script execution creates entirely new
Python/KiCad objects with new random UUIDs every run, even for
geometrically identical content) plus the verified replacement path. If a
listed source segment can no longer be found (the routing algorithm's own
output has since changed), the function prints a loud warning and skips
that entry rather than silently no-op'ing or partially applying it.

**Attempted the same whole-board-aware technique against the remaining
~54 outer-layer (F.Cu/B.Cu) violations** via an automated batch script
trying single-bend and localized step-over detours, from both sides of
each conflict, at search widths up to 9mm: yielded 1 additional fix (a
`VM_MOTOR` track near J4, also folded into `REROUTE_OVERRIDE` above) and
then a genuine plateau — 4 further iterations found 0 additional tractable
fixes, not a search-parameter limit. This confirms, with a real
multi-iteration search rather than a single attempt, the prior triage's
own characterization: these violations sit in genuinely dense board
regions (a substantial fraction confirmed via direct geometric distance
check to fall close to U5's or U6's placed center, matching the
already-documented 0.65mm-fine-pitch package-proximity pattern; the
remainder in busy shared routing corridors) where a local single-track
detour cannot find clearance at any tested search width or side. Per Kyosuke's own explicit
framing ("you don't need to build a general-purpose autorouter from
scratch"; "it's fine if this doesn't reach zero violations"), a placement
change for U5/U6 was considered but **not attempted this round**: U5's own
placement was already the subject of a prior, deliberate fix (ISS-031's
thermal-via array), and shifting it now risks silently reopening that
fix's own clearances/via alignment without a wider verification budget
than this round allows — documented here as a scoped candidate for a
future session, not silently declined.

**Verified via real, repeated DRC** (`kicad-cli pcb drc`, 3 fresh runs
each, before vs. after):

| Category | Before (3 runs) | After (3 runs) |
|---|---|---|
| Total violations | 370–371 | 361–367 |
| `shorting_items` | 61–62 | 56–58 |
| `tracks_crossing` | 81–82 | 71–72 |
| `clearance` | 11 | 16–17 |
| `hole_clearance` | 3 | 6 |
| `solder_mask_bridge` | 212–213 | 209–216 |
| `silk_overlap` | 1 | 1 |
| `unconnected_items` | 0 | 0 |

Directly confirmed (not inferred from the count alone) that all 3
targeted J1-area instances are gone from the fresh DRC output, and the
4th (U5-area) remains present as a 4-entry DRC signature per run (1
`clearance` + 3 `shorting_items`, all via-vs-track/via-vs-via pairings
between the two conflicting vias and their own connected tracks on B.Cu/
In2.Cu) — this exact 4-entry signature was already present before this
round's changes (see Cycle 9 correction below), not new reporting
granularity this round introduced.

**Correction (2026-09-02, Hardware Reviewer Cycle 9 independent
verification)**: this section originally claimed the U5-area conflict is
"now reported as 3 separate DRC entries per run rather than 1" — Cycle 9
independently searched the pre-round baseline (commit `19ffb16`) and found
the identical 4-entry set (not 3, and not new) already present there, same
net names/positions/lengths, across all 3 baseline runs. The "rather than
1" framing was inaccurate; corrected above. This does not affect the
underlying intractability conclusion, which Cycle 9 independently
reconfirmed via its own two-method distance check. Cycle 9 also could not
exactly reproduce the "14 of ~54... within 8mm" figure above (obtained 11,
6, or 16 depending on which reasonable counting rule is used, never
exactly 14) — the qualitative clustering claim holds, the specific number
did not reproduce and has been softened above accordingly. Neither
correction changes ISS-036's OPEN status, the confirmed fixes, or the
confirmed pre-existing clearance/hole_clearance findings — both are
narrative/documentation-precision issues in this file, not hardware
defects, caught by Cycle 9's own from-scratch re-derivation rather than by
trusting this file's numbers. Full detail: `validation/design-review.md`
Hardware Reviewer — Cycle 9 (Findings HWR9-B, HWR9-C; see also HWR9-A, an
incidental, fully pre-existing/benign `shorting_items` triage-bucket gap
this reviewer separately surfaced, unrelated to this round's own changes
and already explained by already-open ISS-017).

**The `clearance` (11→16–17) and `hole_clearance` (3→6) increases were
each individually, directly re-verified — not inferred from the count
delta.** Enumerated every unique `clearance`/`hole_clearance` violation
pair across the 3 fresh "after" runs (19 unique pairs total), and for each
one, located the exact same two objects (matched by net name + endpoint
position + track length, all three required to agree — length as a
disambiguator specifically because position+net alone can match the wrong
one of several similarly-placed same-net tracks) in **both** the current
board and a pristine pre-round baseline, then computed the clearance
between them using `GetEffectiveShape()` on both sides (the same
width-aware method DRC itself uses — not a bare `SEG` centerline, which
silently drops the track's own half-width from the result and was an
error caught mid-investigation this round, see below). Every single pair
resolved to a **unique** match in both boards and showed **numerically
identical** clearance values in both (e.g. `GND` vs a `CC1` via at exactly
0.150mm in both boards) — conclusively confirming all 19 are pre-existing
conditions that DRC was already not surfacing before this round's fix
(most likely deprioritized behind a co-located, now-resolved
`shorting_items` violation at the same object — the same report-masking
phenomenon already documented for the zone-fill fix's own
`tracks_crossing` increase above), not new problems this round's reroutes
introduced.

**Process note, disclosed rather than omitted**: an earlier, less
rigorous same-day comparison attempt — matching objects across two
*separately regenerated* boards by net+position alone (no length
disambiguator), and computing clearance via a bare `pcbnew.SEG` built
from a track's endpoints compared against the other object's
`GetEffectiveShape()` (asymmetric, and missing the track's own
half-width) — produced a false "6 genuinely new clearance violations"
result. Caught before committing by re-deriving every flagged pair with
the corrected, symmetric, width-aware method above, checked directly
against the real committed boards rather than trusting the first
comparison's own output; the correction is recorded here rather than
silently discarding the wrong intermediate conclusion, matching this
project's own established practice of disclosing a caught methodology
error (e.g. the ISS-036 UUID-instability lesson embedded in
`_apply_reroute_overrides`'s own matching design above).

**Net effect**: a genuine, real, whole-board-verified reduction in
`shorting_items` (the category this finding itself identifies as closest
to an actual physical short) — 3 of the 4 named `via_vs_inner_layer_copper`
targets resolved plus 1 additional outer-layer fix, 4 fixes total — with
zero confirmed new violations in any category. Sent for independent
Hardware Reviewer verification before any partial-closure claim (same
standing convention as every prior round on this finding). ISS-036
remains correctly OPEN: ~355–370 total violations remain, and this
finding's own resolution bar ("every violation individually triaged") is
still not met — the 4th `via_vs_inner_layer_copper` instance is confirmed
intractable (not resolved), and the ~54 outer-layer violations remain a
disclosed, evidenced autorouter/placement-class gap, not attempted
further this round per Kyosuke's own explicit framing that reaching zero
is not required.

### ISS-036 solder_mask_bridge sweep — 2 more whole-board-aware fixes (2026-09-02, continued per explicit request to keep pushing)

`solder_mask_bridge` is by far the largest untriaged DRC category
(209–226 instances across runs — more than the `shorting_items` (49–58),
`clearance` (14–17), and `hole_clearance` (3–6) categories combined) and
had never been deep-dived before this round; the earlier mechanism-level
triage covered `shorting_items` only. Root-caused first, then attacked
with the same whole-board-aware technique already validated on
`via_vs_inner_layer_copper`.

**What this violation actually means**: 209 of 211 instances are
track-vs-pad conflicts where a different-net track passes close enough
to an unrelated pad that their solder-mask apertures merge into one
shared opening — a real solder-bridging risk on the physical board if
fabricated as-is, not a cosmetic DRC nag (KiCad's own solder-mask-web
computation: aperture expansion 0.05mm each side + minimum web width
0.1mm means any two different-net copper features closer than roughly
the same ~0.2mm design clearance already targeted elsewhere in this
finding will typically also trigger this check).

**Spatial distribution, checked before assuming a fix strategy**: 125 of
211 (59%) fall within 15mm of U5's or U6's placed center, matching the
already-documented 0.65mm-fine-pitch-package-proximity pattern. The
remaining 86 (41%) are spread across the rest of the board. This
directly answers the standing "is a U5/U6 placement change worth
attempting" question with real data rather than assumption: even a
perfect placement fix eliminating every single U5/U6-proximate instance
could only address 59% of this one category, while 41% would remain
untouched elsewhere — and the router's own lack of routing-channel/
congestion awareness (not simple component-to-component distance; U5/U6's
nearest *neighboring components* sit 11–20mm away center-to-center,
not tightly packed) is the more fundamental limitation. A placement
optimizer aware of routing congestion is itself autorouter-adjacent
work, beyond what "you don't need to build a general-purpose autorouter
from scratch" contemplates — **a U5/U6 placement redesign was
considered and explicitly declined again this round**, now with
quantified evidence rather than the prior round's qualitative risk
argument alone.

**Detour search, same validated method**: uniquely identified the
specific track object for 206 of 211 violations (net + position + track
length matching, requiring an unambiguous single match; 3 skipped as
genuinely ambiguous). Ran the same whole-board-aware collision search
(`pcbnew`'s own `SHAPE.Collide`/`SEG.Collide`, checking every candidate
detour against the board's entire other-net copper on the same layer,
not just the one pad being routed around) against all 206: found
genuinely tractable fixes for only **2 unique track objects** (~1%
yield) — one on `3V3` (its default path happened to pass under U1's own
unrelated pin 1 pad, generating 3 separate DRC entries against 3
different nearby pads simultaneously, all resolved by the one detour)
and one on `VM_MOTOR` (a different segment from the one already fixed in
the prior round). This closely matches the ~2% yield already found for
the 54-item outer-layer `shorting_items` sweep in the prior round —
**now confirmed via a second, independent, much larger-scale (206-item)
test**, strong and reproducible evidence that local single-track detour
search has genuinely hit a real ceiling for this board's routing
density, not a fluke or a search-parameter artifact specific to one
category.

**Integrated and verified**: both fixes added to `REROUTE_OVERRIDE` (5
entries total now) in `generate_pcb.py`, board regenerated, verified via
5 fresh `kicad-cli pcb drc` runs on the real committed board:

| Category | Before this round (3 runs) | After this round (5 runs) |
|---|---|---|
| Total violations | 361–378 | 350–368 |
| `shorting_items` | 56–57 | 49–50 |
| `tracks_crossing` | 72–73 | 81 |
| `clearance` | 16–17 | 16 |
| `hole_clearance` | 5–6 | 3 (reported) — **true population unchanged at 6, see correction below** |
| `solder_mask_bridge` | 209–226 | 199–217 |
| `silk_overlap` | 1 | 1 |
| `unconnected_items` | 0 | 0 |

Directly confirmed (not inferred from aggregate counts, which are
dominated by run-to-run noise larger than a 2-fix effect size) that both
specific targeted conflicts are absent from every fresh run, checked
against their exact pre-fix path signature. `shorting_items` improved
further beyond the prior round's own result (56–58 → 49–50) as a side
effect of the same detour work. The `tracks_crossing` increase (72–73 →
81) and `hole_clearance` decrease (5–6 → 3) were each individually
verified, not assumed benign: enumerated all 84 unique
`tracks_crossing`/`hole_clearance` pairs across the 5 "after" runs and
matched every one (net + position + length, and for the 3 pad-based
`hole_clearance` items, a direct pad reference/number/position lookup
since tracks-only matching can't find footprint pads) against the
pre-round board — **all 84 confirmed pre-existing/unchanged**, 0
genuinely new, including re-confirming the same 3 J1/U2-area
`hole_clearance` items already independently verified pre-existing by
Hardware Reviewer Cycle 9.

**Correction (2026-09-02, Hardware Reviewer Cycle 10 independent
verification — Finding HWR10-A, MEDIUM)**: the "`hole_clearance`: 5–6 →
3" table row above is accurate only as a description of *this round's
DRC-reported output* — it should **not** be read as "3 `hole_clearance`
defects were resolved." Cycle 10 discovered the baseline actually
carries **6** distinct `hole_clearance` pairs (not the 3 this section
originally emphasized): the 3 already covered above (J1/U2-area, already
verified pre-existing by Cycle 9) plus **3 more** — both of J1's own NPTH
mounting holes vs. a `GND` track, present in all 5 baseline runs — that
are silently **absent from all 10 of Cycle 10's own current-board runs**,
despite Cycle 10's own whole-board object diff proving **zero** track/
via/pad change exists anywhere near J1 (the only geometry this round
touched is 90mm+ away, in the `3V3`/`VM_MOTOR` regions). Cycle 10
independently re-measured these 3 pairs' true clearance directly via
`pcbnew` (bypassing DRC's own report entirely): **0.0000mm** (the GND
track literally overlaps the NPTH hole — the same pair Cycle 9 already
confirmed pre-existing on 2026-09-02, so genuinely present across at
least 3 board generations), **0.0500mm**, and **0.2232mm** — all
genuinely below the 0.25mm required hole clearance, confirming these are
**real, physically-present defects on the current board right now**, not
resolved and not a measurement artifact. What changed is that DRC's own
reporting of these 3 specific pairs stopped, for reasons Cycle 10
characterizes as a previously-undocumented DRC reporting-reliability
mode (stable-but-different reported sets between two board states
proven geometrically identical in the relevant area) rather than
anything this round's actual changes caused. **The true `hole_clearance`
population is unchanged at 6, not reduced to 3** — this does not affect
ISS-036's OPEN status (if anything it reinforces that more genuine,
unresolved defects remain than the raw current-run count alone would
suggest) but is recorded here so a future session doesn't mistake DRC's
raw category count for this board's true defect count without
cross-checking, exactly the kind of gap this correction exists to
prevent. Full detail: `validation/design-review.md` Hardware Reviewer —
Cycle 10, Finding HWR10-A.

**Net effect**: 2 more real, individually-verified fixes (7 total across
both rounds); ~350–365 total violations remain (likely a slight
undercount given HWR10-A above — DRC's own reporting is not fully
reliable across all categories). ISS-036 remains
correctly OPEN — its own "every violation individually triaged"
resolution bar is still not met, and the evidenced conclusion is now
stronger: further local-detour-based fixing has a real, reproducible,
sub-2% yield ceiling across two independent large-scale tests spanning
both major violation categories, and the U5/U6 placement question has
moved from "declined on risk grounds" to "declined with quantified
59%/41% evidence that it would not close this finding even if fully
successful." Closing the remainder would need either a
routing-congestion-aware placement/routing pass (autorouter-adjacent
scope) or a substantially more invasive full re-layout — both beyond
this round's scope. Sent for independent Hardware Reviewer verification
before any disposition claim.
