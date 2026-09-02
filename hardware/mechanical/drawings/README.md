# Bench-IMU-01 — 2D Drawings + Exploded Assembly View (Rev 4/4.1, Mechanical scope)

Visual documentation of the already-Design-Complete mechanical assembly
(`validation/change-log.md` ECO-031/032) — 2D orthographic drawings of each
of the 5 printed pieces plus the full assembled unit, and a Blender-built
exploded assembly view. **This is the first time this project has
generated 2D drawings or an exploded view** — this document establishes
the convention so it is reproducible, not a one-off.

No dimension, tolerance, or module body in `bench-imu-01-enclosure.scad`
was touched to produce any of this — every file here is either a small,
new, `include`-only wrapper script (same convention already established by
`hardware/mechanical/stl/export/*.scad`) or a downstream rendered image.

## Tooling honesty (verified this session)

- **OpenSCAD CLI** (v2026.08.30, `--backend=manifold`) — already this
  project's established CAD tool throughout its history. Used here for
  both the STL isolation and the 2D orthographic renders.
- **Blender, via the `blender-*` MCP tools** — confirmed connected and
  working this session (`blender-get_addon_status`, Blender 5.1.1,
  `bpy.ops.wm.stl_import` available). This was **not** true in earlier
  sessions (`hardware/mechanical/README.md`'s own tooling-honesty note, and
  `.github/agents/mechanical-lead.agent.md`, both still correctly describe
  the *previously* verified state of "no CAD/3D modeling MCP tool
  connected" as of when they were written) — treat Blender's availability
  as **verified per-session, not a standing guarantee**
  (`docs/architecture.md` §5.3/§13's own convention). If Blender is not
  connected in a future session, the exploded view cannot be regenerated
  until it is.

## Directory layout

```
hardware/mechanical/drawings/
  README.md                          this file
  scad/                               new OpenSCAD wrapper scripts, one per
                                      printed piece (+ one for the bearing
                                      reference), each isolating that
                                      piece's exact module call(s) in its
                                      real ASSEMBLED-frame position (NOT the
                                      print_layout/print-bed position the
                                      existing hardware/mechanical/stl/
                                      export/*.scad scripts use)
  2d/                                 rendered PNGs: top/front/side for
                                      each of the 5 printed pieces, plus
                                      top/front/side/iso for the full
                                      assembled unit (19 images total)
  exploded/
    build_exploded_view.py           Blender Python script that reproduces
                                      the exploded-view scene from scratch
    bench-imu-01-exploded-view.png   final rendered output (with legend)
```

## Method 1: 2D orthographic drawings (`2d/`)

**Technique chosen**: OpenSCAD's own orthographic camera
(`--projection=ortho --camera=tx,ty,tz,rx,ry,rz,dist --autocenter
--viewall --render`), rendering each wrapper script's isolated geometry
from three fixed camera angles — **not** OpenSCAD's in-file `projection()`
module. Both were viable (the task that produced this document explicitly
left the choice open); the CLI-camera approach was chosen because it needs
no extra wrapper logic per view (just 3 different `--camera` arguments
against the *same* isolation script that also produces the STL), and it
was prototyped and visually verified correct (on `stand_plate` and the
asymmetric base assembly) before being used for the full set.

Camera angles used (verified empirically for this OpenSCAD version — the
gimbal rotation convention here has `rx=ry=rz=0` looking straight down):

| View | `--camera` rotation |
|---|---|
| Top | `0,0,0` |
| Front | `90,0,0` |
| Side | `90,0,90` |

Each of the 5 printed pieces gets its own wrapper script in `scad/`
(`assembled-<piece>.scad`), which `include`s the parent `.scad` file with
`-D 'show_mode="export"'` (so the parent file's own `assembled`/
`print_layout` top-level blocks do **not** also render — a real bug hit and
fixed while building this: forgetting that flag causes the whole assembled
scene to render underneath the isolated piece, silently). Each wrapper
calls its piece bare/self-positioned, exactly matching the parent file's
own `show_mode == "assembled"` branch — i.e. these scripts show each part
in its real installed position and orientation, **not** the print-bed
orientation `hardware/mechanical/stl/export/*.scad` uses (some pieces are
flipped for printing, e.g. the PCB lid and containment cap).

The "assembled unit" 2D views (`assembled-unit-*.png`) are rendered
directly from the unmodified `bench-imu-01-enclosure.scad` (its own
default `show_mode = "assembled"`) — no wrapper script needed for those.

**A real limitation, not a defect**: a pure top-down orthographic render
of solid, single-color CSG geometry cannot visually reveal a hidden
Z-height step directly beneath another feature at the same color (two
stacked horizontal surfaces of the same material read identically from
directly above, with no shading cue). The top views here correctly show
XY footprint and hole positions — exactly what a top view is for — while
Z-stepping (e.g. the mounting flange rising above the stand plate/pinch
guard) is what the front/side views are for. Verified by cross-checking
against the front/side renders, not assumed.

### Regenerating the 2D drawings

```sh
cd hardware/mechanical/drawings/scad
for name_script in "base-assembly:assembled-base-assembly" \
                   "pcb-lid:assembled-pcb-lid" \
                   "containment-cap:assembled-containment-cap" \
                   "stand-plate:assembled-stand-plate" \
                   "pinch-guard:assembled-pinch-guard"; do
  name="${name_script%%:*}"; script="${name_script##*:}"
  openscad -D 'show_mode="export"' --backend=manifold --projection=ortho --render \
    --autocenter --viewall --imgsize=1400,1050 --camera=0,0,0,0,0,0,300 \
    -o ../2d/${name}-top.png   ${script}.scad
  openscad -D 'show_mode="export"' --backend=manifold --projection=ortho --render \
    --autocenter --viewall --imgsize=1400,1050 --camera=0,0,0,90,0,0,300 \
    -o ../2d/${name}-front.png ${script}.scad
  openscad -D 'show_mode="export"' --backend=manifold --projection=ortho --render \
    --autocenter --viewall --imgsize=1400,1050 --camera=0,0,0,90,0,90,300 \
    -o ../2d/${name}-side.png  ${script}.scad
done

cd ../../
openscad --backend=manifold --projection=ortho --render --autocenter --viewall \
  --imgsize=1600,1200 --camera=0,0,0,0,0,0,400   -o drawings/2d/assembled-unit-top.png   bench-imu-01-enclosure.scad
openscad --backend=manifold --projection=ortho --render --autocenter --viewall \
  --imgsize=1600,1200 --camera=0,0,0,90,0,0,400  -o drawings/2d/assembled-unit-front.png bench-imu-01-enclosure.scad
openscad --backend=manifold --projection=ortho --render --autocenter --viewall \
  --imgsize=1600,1200 --camera=0,0,0,90,0,90,400 -o drawings/2d/assembled-unit-side.png  bench-imu-01-enclosure.scad
openscad --backend=manifold --projection=ortho --render --autocenter --viewall \
  --imgsize=1600,1200 --camera=0,0,0,55,0,25,400 -o drawings/2d/assembled-unit-iso.png   bench-imu-01-enclosure.scad
```

## Method 2: Exploded assembly view (`exploded/`)

OpenSCAD has no built-in "explode along an axis" primitive; Blender's
transform tools do, so this step uses the newly-verified Blender MCP
connection. Approach, in full: export each of the 5 printed pieces (plus
the bearing, as a translucent reference-only ghost — not printed, not
counted among the 5) as an **assembled-position** STL using the same
`scad/assembled-*.scad` wrapper scripts (matching the source `.scad`
file's own real global coordinates — verified, not eyeballed: every
imported mesh's bounding box was cross-checked against
`hardware/mechanical/stl/README.md`'s own independently-derived
bounding-box table and matched **exactly** on every dimension, confirming
no misalignment before any explode offset was applied), import all 6 into
Blender, then translate each one by a fixed, artificial offset to separate
them for the picture.

**Explode axis chosen**: primarily **Z**, matching the source `.scad`
file's own "Global Z-stack" framing (bottom to top: stand plate → bearing
→ base assembly (anchor) → PCB lid / containment cap), with a modest
lateral (X/Y) stagger on top of that. The lateral stagger is not
cosmetic filler — it is **necessary**: an orthographic camera at any
elevated angle will otherwise occlude the wide, lower pieces (stand plate,
pinch guard) behind the taller base assembly directly above them, purely
from simple depth-ordering, even though they are correctly positioned and
fully separated along Z. This was found and fixed during construction (see
`build_exploded_view.py`'s own "Key lessons learned" section for the full
account, including a second, sillier bug: a ground-reference plane that
ended up literally burying the lowest exploded pieces once they were
pushed below its fixed height).

**Colors are a legend, not decoration**: each of the 5 printed pieces gets
its own solid color (matching a caption baked into the final PNG); the
bearing is left translucent silver to read as "reference, not printed."

**What is deliberately left out**: the PCBA and motor/flywheel reference
geometry that also exist in the source `.scad` file (`reference_pcba()`,
`reference_motor_flywheel()`) are not included in the exploded render —
those are already documented in `bom/component-selection.md` and the
Rev 3 BOM; adding them was judged to add clutter without adding new
information for a *mechanical* exploded view.

### Regenerating the exploded view

1. Export the 6 assembled-position STLs (see `build_exploded_view.py`'s own
   header for the exact commands) — these are **not committed**
   (regenerable build intermediates, avoiding near-duplicate binaries next
   to the real print-ready STLs in `hardware/mechanical/stl/`).
2. Run `exploded/build_exploded_view.py` inside Blender (Scripting tab,
   `blender --background --python build_exploded_view.py`, or paste into a
   Blender MCP `execute_blender_code` call), after setting `STL_DIR` and
   `OUTPUT_PATH` at the top of the script.
3. The committed `bench-imu-01-exploded-view.png` additionally has a
   caption/legend strip added via a short Pillow (PIL) post-process (listing
   each part's color, name, and a one-line cross-reference) — not part of
   `build_exploded_view.py` itself; regenerate it the same way if needed
   (see the script's own render output for the un-captioned base image).

## Related documents

- `hardware/mechanical/assembly-instructions.md` — the step-by-step build
  procedure these visuals support.
- `hardware/mechanical/stl/README.md` — the print-ready STL exports (a
  different reference frame/orientation than this directory's own
  assembled-position renders — see Method 1 above).
- `hardware/mechanical/bench-imu-01-enclosure.scad` — source geometry,
  read-only reference for every wrapper script here.
- `hardware/mechanical/bench-imu-01-dimensional-spec.md` — full rationale
  for every dimension visualized.
- `validation/change-log.md` — will carry the ECO entry for this
  documentation-generation pass (no geometry changed).
