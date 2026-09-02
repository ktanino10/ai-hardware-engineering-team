# Circuit &amp; Current-Flow Viewer (Bench-IMU-01)

An interactive, bilingual (EN/JA) block-diagram viewer for this repository's
real Bench-IMU-01 schematic and firmware — not an illustrative/fabricated
circuit. Open `index.html` directly in a browser, or view it hosted on
GitHub Pages once this repo's Pages workflow runs.

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

Click any component for its real role in this circuit, part number, and
(where available) a link to its primary datasheet. Toggle language with the
EN/日本語 buttons top-right.

## How this was generated

- `circuit-data.js` — component boxes + wires, hand-derived from the real
  netlist (`kicad-cli sch export netlist`) and cross-checked against
  `bom/bench-imu-01-fab-bom.csv` and the schematic's own README
  (`hardware/schematic/bench-imu-01/README.md`). No net or behavior here is
  invented; the Mode 3 path is explicitly marked future/unimplemented,
  matching `firmware/bench-imu-01/src/main.c`'s own scope-fence comment.
- `index.html` / `circuit-render.js` — a small, framework-free renderer
  (vanilla JS + inline SVG) so this page has zero build step and zero
  runtime dependencies — safe to serve as a static GitHub Pages site
  indefinitely.
- `reference/bench-imu-01-schematic.pdf`, `reference/bench-imu-01-pcb.pdf` —
  the actual KiCad schematic and PCB layout, exported directly via
  `kicad-cli sch export pdf` / `kicad-cli pcb export pdf` from the real
  `.kicad_sch` / `.kicad_pcb` project files in this repo (not redrawn or
  simplified) — attached per the request for the real circuit drawings
  alongside the animated explainer.

## Known limitations (disclosed)

- Wire routing is a simplified block-diagram layout for legibility/animation,
  not a literal reproduction of the schematic's own wire paths — for the
  literal schematic, see `reference/bench-imu-01-schematic.pdf`.
- Multi-node nets (e.g. `/3V3`, `GND`) are drawn as the handful of
  edges relevant to this explainer, not every physical connection in the
  net.
