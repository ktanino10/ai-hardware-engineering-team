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
camera path.

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
