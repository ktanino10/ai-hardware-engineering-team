# Hardware artifacts: reading and regeneration

[English](hardware.md) | [日本語](hardware.ja.md) | [Guide index](README.md)

This reader guide keeps the existing schematic, PCB, mechanical and
manufacturing records at their canonical paths. It does not change
geometry, approvals, data or historical tool results. Commands below
regenerate derived files and are **not** fabrication, purchasing or
power-on instructions. Use a scoped owner task, current tool preflight and
the [assembly evidence contract](assembly-evidence.md) before changing
source-bound artifacts. Do not overwrite old evidence during exploration.

## Schematic

[Directory conventions](../hardware/schematic/README.md) /
[Bench-IMU-01 project](../hardware/schematic/bench-imu-01/README.md).

Open the real `.kicad_pro` / `.kicad_sch` together with project-local
`.kicad_sym`, `.pretty`, `sym-lib-table` and `fp-lib-table` files.
`generate_schematic.py` records how the project is produced; the separate
schematic design document remains the source for net-by-net rationale.
The README's Rev2 capture and Rev3–5 extensions are historical scope
records, not a new approval of every current requirement.

Every nontrivial design decision needs a rationale and Evidence ID.
Corrections require an ECO, not an unlogged manual schematic change.
Verify available KiCad CLI/MCP operations each session. Old connection
failures do not prove permanent absence; CLI ERC and a hypothetical ERC
MCP wrapper are different capabilities. Do not infer automated SPICE from
the presence of a bundled library. Schematic work does not acquire
mechanical or firmware ownership.

## PCB

[PCB conventions, history and regeneration](../hardware/pcb/README.md).
Per-board layout is under `hardware/pcb/<board>/`.
`generate_pcb.py` reconstructs the board from the actual schematic netlist/
BOM. Verify the bundled Python/`pcbnew` environment before authoring;
CLI export/DRC/render availability is not interactive routing support.
Recorded zone-fill failures and later successful cases are historical,
state-dependent observations, not a universal tooling wall.

Run real DRC before pre-fabrication review, keep BOM/source consistency and
provide a visual snapshot. Never turn accepted risk or open violations into
“DRC-clean.” Independent Hardware Reviewer assessment and the named human
gate remain necessary. Do not infer the current DRC total from a past
iteration section.

### Compare regeneration correctly

Regenerating a board can change UUIDs and footprint emission order without
changing the design. Do not use bare DRC differences, raw file hashes or
Gerber D-code numbers alone as geometry-equivalence tests.
Compare segment and via multisets (coordinates, width/size/drill, layer,
net), footprint sets, pad counts, top-level filled-zone vertices and
aperture-aware Gerber primitives. Resolve each `%ADDnn` code to shape and
parameters first. Do not mistake `zone_connect` inside a footprint for a
top-level zone. Exporting a fixed committed file and rebuilding a board
are different operations; their byte stability need not match.

The recorded PNG regeneration command, from the root, is:

```sh
kicad-cli pcb render hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb \
  --side top --width 1568 --height 984 --quality high --floor \
  --background opaque -o hardware/pcb/bench-imu-01/bench-imu-01-3d.png
```

The original guide discloses an actual 1544×952 canvas for those flags on
its KiCad 10.0.1 host. Requested dimensions do not prove delivered
dimensions; inspect output and camera/geometry rather than hiding a crop.

## Fabrication exports

[Canonical package guide](../hardware/pcb/bench-imu-01/fab/README.md).
The ZIP contains copper, paste, silkscreen, mask, outline, job metadata,
separate plated/non-plated drill files and drill maps. The separate
positions CSV is the assembly placement file. These are derived files;
changing the PCB requires refreshing **both** this family and public
viewer PDFs in the same scoped change. Never hand-edit an export.

The original package's DRC/accepted-risk and BOM-sourcing history is kept
in its guide and shared ledgers. “Submittable file” is not authorization
to order, a clean-DRC claim or project-wide Design Complete.

From the root, substitute a new scratch directory for `<staging-dir>`:

```sh
kicad-cli pcb export gerbers \
  --output <staging-dir> \
  --layers F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb
kicad-cli pcb export drill \
  --output <staging-dir> \
  --format excellon --excellon-separate-th --generate-map \
  hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb
kicad-cli pcb export pos \
  --output hardware/pcb/bench-imu-01/fab/bench-imu-01-positions.csv \
  --format csv --units mm --side both \
  hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb
cd <staging-dir> && zip -X -j bench-imu-01-gerbers.zip ./*
```

Keep the ZIP flat; the loose staging files are not individually committed.
Check RS-274X/Excellon headers, copper layer count, board outline versus
stroke-inclusive job dimensions, PTH/NPTH counts, position rows versus
excluded mounting holes, ZIP integrity, transferred-file equality and
absence of unintended source drift. Historical measured counts remain
historical; a new export requires its own actual results.

## Mechanical source, STL and drawings

[Mechanical conventions](../hardware/mechanical/README.md) /
[STL exports](../hardware/mechanical/stl/README.md) /
[drawings](../hardware/mechanical/drawings/README.md).

The parametric `.scad` and readable dimensional table/rationale are the
source. Dimensions need interface/evidence references or explicit
ASSUMPTION/ESTIMATE. Do not silently repair geometry in a visualization
pass; use its owner and ECO. Old “no CAD connected” and later success notes
are dated observations, not today's capabilities. Current WIP assembly
evidence starts during design, with APPROVED release separately gated.

Five distinct printed-piece exports represent base assembly, PCB lid,
containment cap, stand plate and one identical pinch-guard quadrant used
four times. The pointer and cable-anchor features are fused into the
base's combined job, not separate printed pieces. Export existence or
manifold status is not slicer, print, fit, strength or containment
qualification. The STL guide's dimensional and risk tables are
revision-specific engineering records, not updated by this reader guide.

Read [Japanese mechanical regeneration instructions](mechanical-artifacts.ja.md)
or the complete English source guides above. They retain the full STL and
2D command sequences, drafting-sheet steps and historical Blender
regeneration pipeline. Drawings methods 2/3/5/6 explicitly disclose stale
geometry; “Fusion-style” drafting sheets are not Fusion native artifacts,
and the old physics/concept demos are not the current free-body simulator.
Use [simulation](simulator.md) for computed trajectories.
