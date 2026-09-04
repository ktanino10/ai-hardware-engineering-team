# Bench-IMU-01 — 2D Drawings + Exploded Assembly View + Assembly Animation + Drafting Sheets + Physics/Concept Demos (Rev 4/4.1 base, Rev 5 PCB-resize partial update)

Visual documentation of the mechanical assembly — 2D orthographic drawings of
each of the 5 printed pieces plus the full assembled unit, a Blender-built
exploded assembly view, an assembly animation, Fusion-style engineering
drafting sheets (Method 4), a physics-based conservation-of-angular-
momentum **SIMULATION** animation (Method 5), and a **CONCEPT**
reference-attitude-hold demonstration animation (Method 6).

**REV 5 STATUS (MISS-034, this session)**: the mechanical assembly was
resized to fit the real 150×95mm PCB (was a 100×50mm proposal). **Methods 1
(2D orthographic) and 4 (drafting sheets) were regenerated this session**
against the resized geometry (pure OpenSCAD CLI / OpenSCAD+matplotlib, no
Blender dependency — see each method's own section below for what changed).
**Methods 2/3/5/6 (exploded view, assembly animation, physics-demo,
concept-demo) all require Blender via the `blender-*` MCP tools, which are
NOT connected this session** (`blender-get_addon_status` → "Communication
error with Blender: name 'bl_info' is not defined", independently
re-checked this session, not assumed) — **these could not be regenerated
and remain visually stale relative to the Rev 5 geometry** (they still
depict the old, smaller PCB bay). This is a disclosed, known limitation,
not a silent gap — see the "Tooling honesty" section immediately below,
re-verified fresh this session per this project's own "per-session, not a
standing guarantee" convention, and each of Methods 2/3/5/6's own section
for the specific stale-artifact note. A future session with Blender
connected should regenerate these 4 artifacts using the same, unchanged
regeneration commands documented below.

No dimension, tolerance, or module body in `bench-imu-01-enclosure.scad`
was touched to produce any of this — every file here is either a small,
`include`-only wrapper script (same convention already established by
`hardware/mechanical/stl/export/*.scad`) or a downstream rendered image
or video.

## Tooling honesty (re-verified fresh this session — not assumed carried over)

- **OpenSCAD CLI** (v2026.08.30, `--backend=manifold`) — already this
  project's established CAD tool throughout its history. Used here for
  the STL isolation, the 2D orthographic renders, and the drafting-
  sheet DXF projections (Method 4) — all re-run successfully this session
  against the Rev 5 (resized) geometry.
- **Blender, via the `blender-*` MCP tools** — **NOT connected this
  session** (`blender-get_addon_status` returned an addon-handshake error,
  not a successful connection) — a DIFFERENT state than the immediately
  preceding session that authored Methods 2/3/5/6 (which found it
  connected, Blender 5.1.1). Per this project's own established
  convention (`docs/architecture.md` §5.3/§13, and this file's own prior
  paragraph already anticipating exactly this situation: "If Blender is
  not connected in a future session, the exploded view/animations cannot
  be regenerated until it is"), Methods 2/3/5/6 were **not** attempted
  this session — the committed artifacts for those 4 methods are
  unchanged and now stale relative to Rev 5's resized geometry.
- **matplotlib + a hand-written DXF parser** (Method 4) — confirmed
  available and used this session, re-run successfully against Rev 5
  geometry (see Method 4's own section below).
- **`trimesh` + `numpy-stl`** — confirmed available this session, used to
  independently cross-check every re-exported STL's bounding box (matching
  this project's own established verification convention).


## Directory layout

```
hardware/mechanical/drawings/
  README.md                          this file
  scad/                               new OpenSCAD wrapper scripts, one per
                                      printed piece (+ bearing/motor-body/
                                      flywheel-rotor references), each
                                      isolating that piece's exact module
                                      call(s) in its real ASSEMBLED-frame
                                      position (NOT the print_layout/
                                      print-bed position the existing
                                      hardware/mechanical/stl/export/*.scad
                                      scripts use)
  2d/                                 rendered PNGs: top/front/side for
                                      each of the 5 printed pieces, plus
                                      top/front/side/iso for the full
                                      assembled unit (19 images total)
  exploded/
    build_exploded_view.py           Blender Python script that reproduces
                                      the exploded-view scene from scratch
                                      (8 parts as of this pass -- see
                                      Method 2's own revision note)
    build_exploded_view_annotations.py  Pillow post-process: legend strip
                                      (8 rows) + 3 fastener leader-line
                                      callouts
    bench-imu-01-exploded-view.png   final rendered output (with legend +
                                      fastener callouts)
  animation/
    build_assembly_animation.py      Blender Python script that keyframes
                                      and renders the assembly animation
                                      (depends on build_exploded_view.py's
                                      own scene already existing)
    bench-imu-01-assembly-animation.mp4   final video (H.264/MPEG4, 24fps)
    bench-imu-01-assembly-animation.gif   derived GIF (12fps, palette-
                                           optimized) for inline preview
  drafting-sheets/                   NEW this pass (Method 4)
    scad/projection-*.scad           projection(cut=false) wrapper scripts
    build_drafting_sheet.py          DXF parser + matplotlib renderer
    bench-imu-01-<part>-drafting-sheet.png/.pdf   3 parts (stand-plate,
                                      containment-cap, pcb-lid)
  physics-demo/                      NEW this pass (Method 5) -- SIMULATION
    build_physics_demo_animation.py
    annotate_physics_demo_frames.py
    bench-imu-01-momentum-conservation-SIMULATION.mp4/.gif
  concept-demo/                      NEW this pass (Method 6) -- CONCEPT
    build_concept_attitude_hold_animation.py
    annotate_concept_demo_frames.py
    bench-imu-01-attitude-hold-CONCEPT.mp4/.gif
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

**REV 5 STALENESS NOTE (this session)**: `bench-imu-01-exploded-view.png`
is **NOT regenerated this session** — Blender is not connected (see
"Tooling honesty" above) — and now depicts the OLD (pre-MISS-034,
100×50mm-proposal-era) PCB bay/lid geometry, which is smaller than the
current, real, resized geometry. Do not treat this image as representative
of the current assembly. What COULD be corrected without a render — the
world-space bounding-box reference points documented in
`build_exploded_view_annotations.py`'s own docstring (`ANCHOR_PX`'s
derivation) — has been updated for the record (see that file), but the
actual pixel output (`ANCHOR_PX` itself, and the base render) requires a
real Blender render to regenerate and was NOT recomputed or guessed at.

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
bearing, motor body, and flywheel rotor (see below) are left translucent
to read as "reference, not printed."

**Revision (this pass): motor (M1) + flywheel are now shown, reversing an
earlier decision.** A prior revision of this document read here: *"the
PCBA and motor/flywheel reference geometry... are not included in the
exploded render... judged to add clutter without adding new information."*
That call is reversed as of this pass. The reason: `assembly-
instructions.md` §4.2/§4.4 documents mounting the motor and installing the
flywheel as real, load-bearing build steps, and the bearing — also a
bought, non-printed part — was already being shown as a reference ghost in
the very same render; omitting the motor/flywheel while showing the
bearing was an inconsistency, not a principled distinction, once directly
questioned. New wrapper scripts `scad/assembled-reference-motor-body.scad`
and `scad/assembled-reference-flywheel-rotor.scad` split the parent file's
existing `reference_motor_flywheel()` module (Section 4) into its
stationary (motor body/housing, bolted to the platform) and rotating
(shaft + hub collar + flywheel disk, per `assembly-instructions.md` §4.4
step 5's own "motor's exposed shaft" language) halves — deliberately
excluding that module's own rotation-clearance keep-out cylinder (a
translucent annotation volume, not a physical object; including it in an
STL export would wrongly merge it into opaque solid geometry). The
`reference_pcba()` module remains excluded (out of scope for this
revision, which was specifically about the motor/flywheel gap; the PCBA
itself is still fully documented in `bom/component-selection.md` and the
fab BOM). The 2 new ghosts needed a much larger explode offset than a
naive Z-stack interpolation would suggest, since they start out physically
inside `fw_bay_wall()`'s cylindrical wall — confirmed empirically by an
intermediate render during this pass that still looked hidden, not
assumed; see `build_exploded_view.py`'s own `OFFSETS` comment for the
fix. The flywheel-rotor ghost's color was also changed from an initial
gold (too close to `containment_cap()`'s own orange from this camera
angle, confirmed by a pixel-level comparison) to purple.

**Fastener leader-line callouts (new this pass)**: the committed PNG also
carries 3 leader-line callouts (containment-cap heat-set inserts, PCB-lid
screws, motor screws), added via `exploded/build_exploded_view_annotations.py`
(Pillow). Anchor points are **not eyeballed** — computed via
`bpy_extras.object_utils.world_to_camera_view()` against the real camera
this scene builds, from real assembled-frame STL bounding-box data; 2 of
the 3 anchors were cross-checked a second way (an independent per-pixel
hue-cluster scan of the actual rendered PNG) since the camera-projected
points for those 2 landed close enough to a part boundary from this
specific angle to risk ambiguity. Every size/qty/confidence fact in a
callout label **reflects** `../assembly-instructions.md` §5's own fastener
summary table — including that table's own already-reconciled PCB-lid
screw count (**4**, not the older, superseded "6" figure that appears in
`bench-imu-01-dimensional-spec.md`'s prose but doesn't match the actual
modeled geometry — see that table's own cross-reference note for the full
reconciliation) — with one deliberate exception, **not** a verbatim copy:
the containment-cap callout adds an explicit
`Safety: ACCEPTED-RISK — see MISS-016` line beyond the table's own
`CONFIRMED (insert match)` text, because a fastener-dimension match is a
separate fact from whether that joint's safety margin is proven adequate
(it isn't yet — `validation/open-issues.md` MISS-016 is still OPEN). An
earlier version of this callout blurred the two into one unearned
"CONFIRMED — safety joint" phrase; Mechanical Reviewer Cycle 8 (MISS-031,
HIGH) caught this and it was corrected before this PR — see
`validation/change-log.md` ECO-039 and `validation/open-issues.md` for the
full record.

### Regenerating the exploded view

1. Export the 8 assembled-position STLs (see `build_exploded_view.py`'s own
   header for the exact commands) — these are **not committed**
   (regenerable build intermediates, avoiding near-duplicate binaries next
   to the real print-ready STLs in `hardware/mechanical/stl/`).
2. Run `exploded/build_exploded_view.py` inside Blender (Scripting tab,
   `blender --background --python build_exploded_view.py`, or paste into a
   Blender MCP `execute_blender_code` call), after setting `STL_DIR` and
   `OUTPUT_PATH` at the top of the script.
3. Run `exploded/build_exploded_view_annotations.py` (plain `python3`, no
   Blender needed) to add the legend strip (8 rows) and the 3 fastener
   leader-line callouts on top of the raw render — this is the file
   actually committed as `bench-imu-01-exploded-view.png`.

## Method 3: Assembly animation (`animation/`)

**REV 5 STALENESS NOTE (this session)**: same as Method 2 above — not
regenerated (Blender not connected this session), both video files still
depict the OLD, pre-MISS-034 geometry.

An animated companion to the static exploded view, added per a follow-up
request: each part moves from its exploded position back to its true
assembled position, **staggered across 4 stages that follow the real
build order** already documented in `../assembly-instructions.md` — not an
arbitrary sequence. Direction is **exploded → assembled** ("watching it
get built"), the more intuitive framing for an assembly animation.

**Stage order** (piece — source build step):

1. PCB lid — `assembly-instructions.md` §4.1 (early core-enclosure step)
2. Containment cap — §4.4 (last of the core-enclosure steps)
3. Stand plate + pinch guard together — §4.5 (the source document places
   these "at the same assembly step," a parallel subassembly)
4. Bearing — §4.6/§4.7 (the final connecting piece; mirrors "mate the two
   halves via the bearing's captive ball race" being the last real step)

The base assembly never moves — it is the substrate/anchor everything else
attaches to, exactly as in the static exploded view. Camera and lighting
are unchanged from the static exploded-view shot (kept fixed deliberately,
to keep the viewer's focus on the part motion rather than a moving camera).
180 frames at 24fps (7.5s), with brief holds at fully-exploded, between
each stage, and fully-assembled, via `CONSTANT` F-curve extrapolation
(each part holds its position before/after its own stage, rather than
drifting).

**Format — verified, not assumed**: both `ffmpeg` (v8.1, `libx264`) and
Blender's own built-in FFMPEG render output
(`bpy.app.build_options.codec_ffmpeg == True`) were confirmed present this
session before committing to a format. The MP4 is the primary deliverable
(H.264/MPEG4, rendered from a PNG frame sequence + a single `ffmpeg`
encode pass — see `build_assembly_animation.py`'s own "Key lessons
learned" for why a PNG-sequence-then-encode pipeline was used instead of
Blender's own FFMPEG muxer directly). The GIF is derived from that same
PNG sequence via `ffmpeg`'s standard two-pass palette technique
(`palettegen`/`paletteuse`, 12fps/640px wide) specifically because GitHub
renders a committed GIF inline in markdown, unlike a committed MP4
referenced by relative path — practical value, not a redundant duplicate.

### Regenerating the assembly animation

1. Run `exploded/build_exploded_view.py` first (the animation script reuses
   that same scene — same 6 imported parts, materials, camera, lighting,
   ground plane — rather than rebuilding it from scratch).
2. Run `animation/build_assembly_animation.py` inside Blender to keyframe
   the animation and render the PNG frame sequence (chunk the render across
   multiple calls if driving Blender via a tool with a practical per-call
   time budget — see the script's own "Key lessons learned" for exactly how
   this project did that: 6 chunks of 30 frames each).
3. Encode with `ffmpeg` (exact commands in the script's own header):
   ```sh
   ffmpeg -y -framerate 24 -i "frames/f_%04d.png" \
     -c:v libx264 -pix_fmt yuv420p -crf 20 -movflags +faststart \
     bench-imu-01-assembly-animation.mp4

   ffmpeg -y -framerate 24 -i "frames/f_%04d.png" \
     -vf "fps=12,scale=640:-1:flags=lanczos,palettegen=stats_mode=diff" \
     /tmp/anim-palette.png
   ffmpeg -y -framerate 24 -i "frames/f_%04d.png" -i /tmp/anim-palette.png \
     -filter_complex "fps=12,scale=640:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3" \
     -loop 0 bench-imu-01-assembly-animation.gif
   ```
4. The rendered PNG frame sequence itself is **not committed** (same
   regenerable-intermediate convention as the exploded view's own
   assembled-position STLs) — only the two encoded output files are.

## Method 4: Fusion-style engineering drafting sheets (`drafting-sheets/`)

New this pass, added per an explicit request for a Fusion-360-style
drafting sheet — **this project does not have Fusion 360 access, and
these sheets do not claim to be Fusion output.** Every sheet's own title
block says so explicitly ("OpenSCAD-source-driven drafting sheet. NOT a
Fusion 360 drawing."), per this project's own no-overclaiming discipline.

**Pipeline**: `bench-imu-01-enclosure.scad` (unmodified) → a new,
`include`-only wrapper script per part (`drafting-sheets/scad/projection-
<part>.scad`) that feeds the SAME assembled-frame module call Method 1
already uses through OpenSCAD's `projection(cut=false)` (a top-down
**silhouette** projection — the whole solid's outer boundary collapsed
onto the XY plane, not a cross-section) → `openscad --export-format dxf`
(a regenerable intermediate, **not committed**, same convention as the
exploded view's own STLs) → `build_drafting_sheet.py`: a small,
**hand-written DXF entity parser** (per this task's own explicit "simple
parser" instruction — no `ezdxf` dependency was added) + a matplotlib
renderer.

**What the parser actually has to handle — verified, not assumed**: 3 real
test exports on this project's OpenSCAD version produced **only
`LWPOLYLINE` entities** (vertex-list circles/rectangles, no bulge/arc data
at all) — `LINE`/`CIRCLE`/`ARC` are supported defensively in case a future
OpenSCAD version's DXF exporter changes, but are unexercised by this
project's own real files.

**A real, disclosed limitation**: a BLIND hole (e.g. `stand_plate()`'s own
bearing-mount pilot holes) does not appear as a separate DXF contour — the
silhouette from directly above is unbroken wherever solid material still
exists anywhere in the part's Z extent, the exact same "a top-down view
can't show a hidden Z-step" caveat Method 1 already discloses for camera-
based top views. Fastener facts that don't survive into the DXF as real
geometry are annotated from the known, cited source values instead (with
an explicit "(blind hole, not visible in this outline-only projection)"
note), never inferred from geometry that isn't actually there.

**What is auto-measured vs. what is cited text**: overall envelope
dimensions and any cleanly-circular hole/boundary diameter are **measured
directly from the parsed DXF vertex data** (a real geometric fit-and-
check, printed to the console for cross-verification — e.g. `stand_plate`'s
inner bore auto-measured at ⌀56.0mm, matching `bmount_flange_ir`'s own
28.0mm radius exactly) — these are genuine measurements, not guesses.
Fastener callouts (size/qty/confidence) are fixed text cross-referenced to
`../assembly-instructions.md` §5's own fastener table, same convention as
Method 2's own leader-line callouts.

**3 parts covered** (not all 5 — chosen to cover the 3 fastener classes
named in the request without "drawing everything"): `stand_plate`
(bearing mounting holes — blind, see above), `containment_cap` (the
safety-relevant M3-into-heat-set-insert joint — 6 holes auto-measured at
⌀3.4mm each, matching the design's own M3-clearance convention), `pcb_lid`
(the 4 corner screw tabs).

**Output**: PNG (matches this project's existing convention) + PDF (a
near-free bonus from matplotlib — useful if a sheet is ever printed at a
stated scale, since PDF preserves vector data a raster PNG does not).

### Regenerating a drafting sheet

```sh
cd drafting-sheets/scad
openscad -D 'show_mode="export"' --export-format dxf \
  -o /tmp/<part>.dxf projection-<part>.scad
cd ..
python3 build_drafting_sheet.py --part <part> --dxf /tmp/<part>.dxf \
  --out bench-imu-01-<part>-drafting-sheet.png \
  --out-pdf bench-imu-01-<part>-drafting-sheet.pdf
```

## Method 5: Physics-based conservation-of-angular-momentum SIMULATION animation (`physics-demo/`)

**REV 5 STALENESS NOTE (this session)**: not regenerated (Blender not
connected this session). The underlying physics numbers below
(`I_wheel`/`I_platform`/rotation-rate ratio) are unaffected by the
Bench-IMU-01 PCB resize (MISS-034) — they depend only on the flywheel/
motor-platform geometry, which is formula-independent of `pcb_length`/
`pcb_width` (confirmed this session) — but the VISUAL render itself reuses
Method 2's own assembled-position STL pipeline, so it still depicts the
OLD, smaller PCB bay geometry alongside those still-valid physics numbers.

**This is a SIMULATION / PREDICTION, not a measurement.** No PCB has been
fabricated/populated yet (`../assembly-instructions.md` §4.1 placeholder;
366 unresolved DRC items on the still-open PCB-layout branch) and no
firmware has ever been flashed to real hardware — this animation cannot
be, and does not claim to be, real test data. Every physics number it
renders (`I_wheel = 4.5e-5 kg·m²`, `I_platform ≈ 6.9e-4 kg·m²`, ratio
≈1:15, and both stages' ω values) is copied verbatim from the already-
approved ESTIMATE in `bom/component-selection.md`'s own "Platform
angular-rate physics finding" — nothing here is re-derived.

**What it shows**: the same assembled-position STL pipeline as Method 2
(now including the motor-body/flywheel-rotor ghosts added this pass), but
at TRUE assembled positions (no explode offsets), grouped into 2 rigid-
body Empty pivots at the real rotation axis (`fw_cx`,`fw_cy`) via "keep
transform" parenting: **PLATFORM** (base-assembly + pcb-lid +
containment-cap + motor-body ghost — the part that actually rotates in
reaction, the real quantity of physical interest) and **WHEEL**
(flywheel-rotor ghost only). Two stages, each a LINEAR-interpolated
(exactly constant angular rate, not eased) hold: 30 RPM → platform ≈12°/s,
then 300 RPM → platform ≈117°/s — **the platform's own rate is rendered
in real time every stage** (1 animated second = 1 predicted real second),
since that is the actual quantity a conservation-of-angular-momentum demo
is about. The wheel's Stage-1 visual spin (180°/s) is ALSO true real-time
(no aliasing concern at this project's 24fps convention); Stage 2's true
rate (1800°/s = 75°/frame) would alias badly, confirmed by an intermediate
render, so the wheel's Stage-2 visual spin is a disclosed, stylized 720°/s
indicator instead — stated on-screen and here, never silently substituted.

**Labeling**: a title card, a **persistent** on-screen watermark
("SIMULATION — PREDICTION, NOT MEASURED DATA," every frame, not just the
start), a per-stage numeric caption box, and an outro card stating the
future real-hardware test's own success criteria (platform rotates
opposite the wheel; the rate ratio holds within a reasonable tolerance
across ≥2 speeds; the onboard IMU's measured rate matches the predicted
rate; repeatable across multiple trials) — framed explicitly as a bar this
animation has NOT yet been checked against.

### Regenerating the physics-demo animation

Same 3-step shape as Methods 2/3: build the scene + keyframe in Blender
(`build_physics_demo_animation.py`, chunked render — see that script's own
docstring), annotate with Pillow (`annotate_physics_demo_frames.py`,
plain `python3`, no Blender needed), then `ffmpeg` (2-pass MP4 + palette-
GIF, same technique as Method 3's own header).

## Method 6: CONCEPT reference-attitude-hold demonstration animation (`concept-demo/`)

**REV 5 STALENESS NOTE (this session)**: not regenerated (Blender not
connected this session) — same visual-only staleness as Method 5 above
(the concept being illustrated is unaffected by the PCB resize, but the
render itself would still show the old PCB bay geometry if the underlying
assembled-position STL pipeline is reused).

**This is a CONCEPT, not a literal capability of this rig.**
Bench-IMU-01 rotates about exactly ONE (vertical/yaw) axis
(`requirements/requirements.md` REQ-011, `hardware/mechanical-interface.md`)
— there is no pitch/roll degree of freedom, so literal "inversion"/tumble
recovery is physically impossible on this hardware. Per an explicit
reinterpretation: this animation instead shows a deviation from a
**reference attitude**, corrected by the reaction wheel returning the
platform to that reference — the single-axis analog of the eventual
attitude-control concept, not a demonstration of a capability this rig
actually has today.

**Also idealized, not a specific control law's simulated response**: no
closed-loop attitude controller (PID or otherwise) is implemented
anywhere in this project (REQ-009/REQ-014, explicit anti-scope
statements) — this animation cannot and does not claim to show a
particular controller's actual computed response, only an illustrative,
generic ease-in-out curve for a "disturbance → correction → hold" beat.

**Reference-attitude witness mark**: reuses the existing
`rotation_index_pointer()` feature already modeled in
`bench-imu-01-enclosure.scad` (Rev 4.1, `MISS-024` mitigation) — a
witness tab on the rotating base, already intended by its own source-file
comment to be sighted "against any convenient FIXED external landmark."
This animation adds exactly that: a fixed, bright-green reference-mark
object placed at the pointer's own real rest-position world coordinates
(measured directly from `assembled-base-assembly.stl`'s binary vertex
data — (`fw_cx`, `fw_cy`+115.5) — not guessed), so "pointer aligned with
the mark" corresponds exactly to "platform at its reference rotation."

**5-beat sequence** (EASE_IN_OUT bezier throughout — deliberately not the
physics-demo's constant-rate LINEAR keying, since nothing here is a
precise rate): (1) hold at reference; (2) an EXTERNAL disturbance (the
flywheel visibly stays at rest through this phase — the disturbance is
explicitly not wheel-caused) eases the platform to +35° off reference;
(3) hold at the disturbed attitude, pointer visibly misaligned from the
mark; (4) the flywheel eases up to a stylized spin and back down to rest
(a single ease-in-out bezier segment's own natural "zero velocity at both
endpoints, peak in the middle" shape, needing no hand-authored ramp/hold/
ramp trapezoid) while the platform eases back to exactly 0°; (5) final
hold at reference, pointer re-aligned.

**Camera note**: an early attempt reused Method 5's own camera tilt, which
left the reference mark nearly invisible/occluded from that angle —
confirmed by an intermediate render, not assumed — fixed with a much more
top-down camera specifically so the mark/pointer alignment reads clearly.

**Labeling**: a CONCEPT title card (stating the yaw-only/no-closed-loop
caveats above in full), a **persistent** on-screen watermark ("CONCEPT —
NOT A LITERAL CAPABILITY OF THIS RIG," every frame), a per-phase caption,
and an outro card restating what this demo does **not** claim.

### Regenerating the concept-demo animation

Same pipeline shape as Method 5:
`build_concept_attitude_hold_animation.py` (Blender, chunked render) →
`annotate_concept_demo_frames.py` (Pillow) → `ffmpeg` (2-pass MP4 +
palette-GIF).

## Related documents

- `hardware/mechanical/assembly-instructions.md` — the step-by-step build
  procedure these visuals support; §5's fastener summary table is the
  cited source for every fastener callout in Methods 2 and 4.
- `hardware/mechanical/stl/README.md` — the print-ready STL exports (a
  different reference frame/orientation than this directory's own
  assembled-position renders — see Method 1 above).
- `hardware/mechanical/bench-imu-01-enclosure.scad` — source geometry,
  read-only reference for every wrapper script here.
- `hardware/mechanical/bench-imu-01-dimensional-spec.md` — full rationale
  for every dimension visualized.
- `bom/component-selection.md` — the "Platform angular-rate physics
  finding" section, the sole source for every number Method 5 renders.
- `requirements/requirements.md` — REQ-011 (single-axis confirmation,
  Method 6's own premise), REQ-009/REQ-014 (no-closed-loop-controller
  anti-scope, Method 6's own "idealized, not a specific control law"
  caveat).
- `validation/change-log.md` — carries the ECO entries for this pass (see
  that file's own log for the exact ECO numbers used).
