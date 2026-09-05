# 3D Assembly &amp; Part Inspector (Bench-IMU-01)

An interactive, English-only, browser-based 3D viewer for this repository's
real Bench-IMU-01 mechanical assembly — not an illustrative model. Open
`index.html` directly in a browser, or view it hosted on GitHub Pages. No
plugin, no Unity/native runtime, and no build step: plain HTML + a single
ES-module script, using [Three.js](https://threejs.org/) loaded from a CDN.

## Why this exists (and why it isn't the Unity viewer)

An earlier pass at this same goal was built in the Unity Editor (click-to-
inspect + auto-orbiting camera, working in the Editor's Play mode). It was
never shipped because the Unity Editor connection in that session's tooling
became persistently unavailable for many hours, blocking the WebGL export
step specifically — not a decision to abandon Unity on principle. Rather
than continue waiting, this viewer reimplements the same feature set
(orbit freely, click any part, see its real data) directly in the browser,
which needed no external editor to build or to run.

## What it shows

Every part in the scene is either:
- **Real printed-part geometry** — the same OBJ files (converted from this
  repo's own `hardware/mechanical/stl/*.stl`) used to produce the mechanical
  drawings, laid out in the same order as the already-reviewed exploded view
  in `hardware/mechanical/drawings/exploded/`.
- **Real PCB geometry** — a direct `kicad-cli pcb export glb`→OBJ conversion
  of `hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb` (the same board the
  Circuit &amp; Current-Flow Viewer's reference PDF comes from), not a
  placeholder rectangle.
- **A dimensionally-accurate primitive** for the 4 purchased, non-printed
  parts that have no STL (bearing, motor, hub collar, flywheel) — real
  outer/inner diameters and thicknesses from `bench-imu-01-enclosure.scad`
  and `bom/component-selection.md`, not arbitrary placeholder sizes.
- **Screws** — small cylinder+head primitives at approximate real fastener
  locations (stand-plate, PCB-lid, containment-cap joints), per the
  fastener table in `hardware/mechanical/assembly-instructions.md` §5.

Click any part for its real name, dimensions, role in the assembly, and
source (3D-printed vs. purchased, with the relevant BOM/datasheet
citation). Drag to orbit, scroll to zoom — free 360° inspection, no fixed
camera path. Clicking also opens a **part-detail modal** (see its own
section below) with 2D drawings, a small orbitable 3D view of just that
part, and real repository links — additive to the sidebar above, not a
replacement for it.

## Assemble / Explode

The scene loads **assembled** by default: every part shown close to its
real relative position, forming one recognizable unit — not the old
default of an already-spread-out stack. A single toggle button (top-right
of the canvas) swaps between **⛶ Explode View** and **⛝ Assemble View**
(only one label is ever shown at a time, matching "an Explode button, and
an Assemble button shown once exploded"); the camera automatically re-fits
to whichever layout is now active.

- **Assembled layout**: a real-measured-height CONTACT STACK — every
  part's own actual loaded-geometry bounding-box height (not a hardcoded
  guess) is used to stack it directly against its neighbor, following the
  real build sequence in `hardware/mechanical/assembly-instructions.md`:
  a shared "spine" (Stand Plate → Bearing → Base Assembly), the Pinch
  Guard sharing the Stand Plate's own height (it is assembled "around the
  stand plate" per that document's §4.5 step 8, not near the flywheel bay
  as its large radius might suggest), and two branches rising from the
  spine's own top: the PCB bay (PCB → PCB Lid) and the flywheel bay
  (Motor → Hub Collar → Flywheel → Containment Cap). The two branches are
  separated by a small horizontal offset (~52mm) so they don't visually
  overlap — a real number, derived from `bench-imu-01-enclosure.scad`'s
  own `fw_cy`/`pcb_bay_y0`/`base_outer_y` GLOBAL-frame variables (not an
  arbitrary guess), **not** a byte-exact reconstruction (see "Known
  limitations" below for exactly what it assumes).
- **Exploded layout** is now a **horizontal single row** (a deliberate
  change from this viewer's original vertical stack, per direct human
  request) — parts spread left-to-right using each part's real measured
  width plus an artistic gap, in the same relative order as the original,
  already-reviewed exploded-view PNG (the per-part `y` value in
  `assembly-data.js` is kept byte-identical to before and still encodes
  that same order — it is just read as an ordering key now, not a literal
  world position).
- A short, smooth transition animates between the two states; this is a
  nice-to-have, not a claim of physical accuracy.

## Part-detail modal

Clicking any part opens a centered modal window with:

- The same real name/dimensions/role/source text as the sidebar, plus
  auto-linkified mentions of any repo-relative path already present in
  that text (e.g. `validation/open-issues.md`) turned into real GitHub
  links — addressing "let me jump from any displayed detail to the real
  repo location it comes from" across the *existing* info fields, not
  just the new fields below.
- **2D drawings**: real front/side/top PNGs (plus a dimensioned drafting
  sheet where one exists) for the 5 printed parts that have them (Pinch
  Guard, Stand Plate, Base Assembly, PCB Lid, Containment Cap). The other
  5 real parts — Bearing, Motor, Hub Collar, Flywheel (purchased, no
  drawing files exist for them), and the PCB (a real KiCad board, not one
  of the 5 enclosure/printed parts drawings/2d/ covers) — show an
  explicit, honest N/A note instead of a broken image, each with its own
  specific reason. **Disclosure**: this viewer has 10 real parts total,
  not a round "5 printed + 4 purchased" split — the PCB is the 10th,
  unstated case, shown as its own explicit N/A + a rendered board view
  (`hardware/pcb/bench-imu-01/bench-imu-01-3d.png`) instead.
- **A small interactive 3D mini-viewer**, freely orbitable (drag/scroll),
  showing just that one part in isolation — it reuses the exact same
  already-loaded geometry the main scene renders (no second network
  fetch), rebuilt as a fresh lightweight clone (see "Known limitations"
  for why a plain `Object3D#clone()` couldn't be used as-is).
- **Repository links**: for printed parts, the real OpenSCAD module name(s)
  in `bench-imu-01-enclosure.scad` (confirmed by reading the file, not
  guessed) plus the drafting-sheet projection script where one exists; for
  the Motor/Hub Collar/Flywheel, an honest note that they share one
  reference-only visualization stand-in module (`reference_motor_flywheel()`)
  that is **not** their own real design (they are purchased parts with no
  OpenSCAD module of their own); for the PCB, its real KiCad source file
  instead of an OpenSCAD module; for Bearing/Motor, the real purchase URL
  read from their own datasheet metadata record; for Hub Collar/Flywheel,
  an explicit "no vendor/MPN on file" disclosure (confirmed by searching
  `datasheets/evidence-log.md`, no match — not invented); and, for every
  part, a real link to its `datasheets/evidence-log.md` Evidence ID row
  where one exists, or an explicit "no Evidence ID cited" note where one
  doesn't.

A few small "browse source" links in the header (and a reference photo of
the real assembled unit in the legend) jump directly to
`hardware/mechanical/`, its `drawings/`, and its `stl/` directories on
GitHub, for the same "jump to the real repo location" reason.

## Known limitations (disclosed)

- The vertical exploded-view spacing is chosen for legibility, matching the
  real assembly *order* from the reviewed exploded-view PNG — it is not a
  literal to-scale gap distance from any source file.
- The 4 purchased parts without STL geometry are shown as simple cylinders/
  rings, not their true visual shape (e.g. the motor is not modeled with
  its actual stator/winding detail) — their *dimensions* are real, their
  *shape* is a simplified stand-in, same disclosure the Unity precursor
  carried for the same parts.
- Screw positions are illustrative of *where* fasteners join these parts,
  not measured to the millimeter against the STL/SCAD source.
- **Assembled layout is a single-axis contact stack, not a byte-exact 3D
  reconstruction.** It reuses the same "stack parts along one axis" model
  the original exploded view already used (just tighter, plus one
  horizontal split for the two bays) rather than reproducing every
  intervening `bench-imu-01-enclosure.scad` GLOBAL-frame offset by hand or
  re-running OpenSCAD to export a second, differently-posed geometry set.
  Two concrete consequences: (1) the ~52mm PCB-bay/flywheel-bay horizontal
  separation assumes Base Assembly's own *measured*-mesh bounding-box
  center coincides with the true SCAD-frame midpoint between the two
  bays' real centers — a reasonable approximation, not a derived-to-the-
  millimeter fact; (2) the PCB Lid and Containment Cap are shown stacked
  *above* their contents in real installation order, not volumetrically
  nested/enclosing around them (a real cap/lid does both — close over its
  contents *and* physically extend down around/beside them — which a
  single vertical stack can't represent).
- **The mini 3D viewer's clone is NOT `Object3D#clone(true)`.** That was
  tried first and throws inside three.js itself
  (`JSON.stringify cannot serialize cyclic structures`), because every
  mesh in the main scene carries `userData.rootWrapper` (a back-reference
  used for raycaster hit-testing) and three.js's own `Object3D.prototype.copy()`
  round-trips `userData` through `JSON.parse(JSON.stringify(...))` — found
  by direct reproduction while building this feature, not assumed from the
  (heavily redacted, cross-origin) console error alone. Fixed with a small
  hand-written recursive clone (`cloneForMiniViewer()` in
  `assembly-render.js`) that copies transform + shares geometry/material
  by reference, without touching `userData` at all.
- **Cross-folder links use `raw.githubusercontent.com`/`github.com`, not
  relative paths**, for anything outside `visualization/` — because
  `.github/workflows/deploy-pages.yml` uploads *only* the `visualization/`
  folder to GitHub Pages, so a relative link like `../../hardware/...`
  would 404 once deployed even though it resolves fine in local testing.
  This mirrors `visualization/dashboard/dashboard-live.js`'s own pre-existing
  `RAW_BASE` convention exactly, not a new pattern introduced here.
- The Evidence ID link for the motor (`DS-MTR-017`) is cross-referenced
  from that part's own datasheet metadata record (its own "Used for
  Evidence IDs" list), not copied from `assembly-data.js`'s pre-existing
  `source` field (which cites `bom/component-selection.md` instead,
  unchanged) — disclosed in the modal itself, not presented as if it were
  already there.
