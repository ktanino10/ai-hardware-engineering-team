# Circuit &amp; Current-Flow Viewer (Bench-IMU-01)

An interactive block-diagram viewer for this repository's real Bench-IMU-01
schematic and firmware — not an illustrative/fabricated circuit. Open
`index.html` directly in a browser, or view it hosted on GitHub Pages.
English-only by design (a prior EN/JA version was simplified per explicit
user preference).

## What it shows

Three toggleable modes, each with an animated current/data-flow overlay on a
block diagram whose every box and wire corresponds to a real reference
designator and net name from
`hardware/schematic/bench-imu-01/bench-imu-01.kicad_sch`:

1. **Power Distribution** — USB 5V → 3.3V logic rail (MCU + IMU); external
   DC jack → fused/reverse-polarity-protected → eFuse-supervised motor rail
   → motor driver → 3-phase reaction-wheel motor.
2. **Current Behavior (implemented)** — what `firmware/bench-imu-01/src`
   *actually* does today: IMU→UART is one-way telemetry; a host operator's
   UART speed command drives the motor open-loop; the FG tachometer feeds
   back for overspeed *safety* shutdown only.
3. **Future: Closed-Loop Attitude Control** — explicitly labeled **NOT
   IMPLEMENTED**. `main.c`'s own top comment fences this out: *"any code
   path that reads the IMU and reacts by driving the motor... Control
   Engineer territory, not yet triggered."* Shown only to illustrate the
   eventual goal — do not mistake this dashed path for working behavior.

**Every component AND every wire is clickable.** Clicking a component shows
its real role, part number, and (where available) a link to its primary
datasheet. Clicking a wire shows its real net name, which two components it
connects, and — critically — a plain-language explanation of what that
specific signal actually does and why it exists, e.g. clicking `FG_TACH`
explains it is a tachometer feedback used *only* for `check_overspeed()`
safety shutdown, not for any speed/position control loop. This was added
specifically so the animated pulses are not just decorative motion —
every one of them is traceable back to a real, explained purpose.

## How this was generated

- `circuit-data.js` — component boxes + wires, hand-derived from the real
  netlist (`kicad-cli sch export netlist`) and cross-checked against
  `bom/bench-imu-01-fab-bom.csv` and the schematic's own README
  (`hardware/schematic/bench-imu-01/README.md`). No net or behavior here is
  invented; the Mode 3 path is explicitly marked future/unimplemented,
  matching `firmware/bench-imu-01/src/main.c`'s own scope-fence comment.
  Each wire's `why` field was written from a direct reading of
  `firmware/bench-imu-01/src/main.c`, `motor.h`, and `bmi270.h` — not
  inferred from the net name alone.
- `index.html` / `circuit-render.js` — a small, framework-free renderer
  (vanilla JS + inline SVG) so this page has zero build step and zero
  runtime dependencies — safe to serve as a static GitHub Pages site
  indefinitely. Wires have an invisible 14px-wide hit-path layered under
  the visible 2px stroke so they're easy to click without needing
  pixel-perfect precision. **Integration-time fix**: the visible stroke and
  the animated pulse dot both need `pointer-events:none` in `index.html`'s
  CSS, or they sit on top of (and silently swallow clicks meant for) their
  own invisible hit-path — verified with a Playwright click-dispatch pass
  across all 27 wires before/after adding this rule (0 of 3 sampled real
  clicks landed correctly before the fix; 26 of 27 after).
- `reference/bench-imu-01-schematic.pdf`, `reference/bench-imu-01-pcb.pdf` —
  the actual KiCad schematic and PCB layout, exported directly via
  `kicad-cli sch export pdf` / `kicad-cli pcb export pdf` from the real
  `.kicad_sch` / `.kicad_pcb` project files in this repo (not redrawn or
  simplified) — attached per the request for the real circuit drawings
  alongside the animated explainer.

  **These two PDFs are derived artifacts and go stale the moment their
  source `.kicad_sch` / `.kicad_pcb` is revised** — the same "stale
  load-bearing figure propagation" hazard `docs/workflow.md` §4.2
  describes, made worse here because these are republished to a *public*
  GitHub Pages site. Re-run the exact commands below (never hand-edit the
  PDFs) in the same change that revises the source, exactly as ECO-043 did
  for the schematic PDF:

  ```sh
  # Schematic — one page per sheet, no extra arguments needed
  kicad-cli sch export pdf \
    -o visualization/circuit-viewer/reference/bench-imu-01-schematic.pdf \
    hardware/schematic/bench-imu-01/bench-imu-01.kicad_sch

  # PCB — kicad-cli 10 REQUIRES an explicit --layers list; this exact
  # five-layer set is what the committed PDF was originally produced with
  # (re-derived and confirmed pixel-identical against the pre-existing file
  # before it was regenerated, so this is the real parameter set, not a guess)
  kicad-cli pcb export pdf --mode-single \
    --layers F.Cu,B.Cu,F.SilkS,B.SilkS,Edge.Cuts \
    -o visualization/circuit-viewer/reference/bench-imu-01-pcb.pdf \
    hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb
  ```

  Verify a regeneration the way this repo already verifies PDF changes —
  render both the old and new file at 150 dpi (`pdftoppm -r 150`) and diff
  the pixels, confirming the changed region is only what the source change
  should have moved.

## Known limitations (disclosed)

- Wire routing is a simplified block-diagram layout for legibility/animation,
  not a literal reproduction of the schematic's own wire paths — for the
  literal schematic, see `reference/bench-imu-01-schematic.pdf`.
- Multi-node nets (e.g. `/3V3`, `GND`) are drawn as the handful of
  edges relevant to this explainer, not every physical connection in the
  net.
- One pair of wires (both real `VBUS_5V` runs leaving J1 toward two
  different downstream chips) briefly shares the same routed segment right
  at J1's edge; clicking exactly in that shared sliver selects whichever of
  the two is drawn on top rather than reliably picking the one nearer the
  cursor. Both describe the same real net, so the info shown is never
  fabricated — just occasionally the sibling wire's explanation instead of
  the exact one clicked. Not fixed here since correcting it means
  re-routing the block-diagram layout data, not an integration change.
