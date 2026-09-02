---
name: mechanical-visualization
description: Standard procedure for producing assembly instructions, 2D orthographic technical drawings, and an exploded/animated assembly visualization from an already-Design-Complete mechanical design (OpenSCAD source + STL exports) -- documentation of an existing, approved design, not new CAD/geometry work. Use this whenever a mechanical revision has reached Design Complete and needs buildable, visual documentation for humans to actually assemble the physical rig.
---

# Skill: Mechanical Visualization

## Purpose

Turn an already-Design-Complete mechanical design (a `.scad` file + STL
exports + dimensional-spec table, all owned by the Mechanical Lead) into
the visual and procedural documentation a human actually needs to build
the physical rig: a real, buildable assembly-instructions document, 2D
orthographic drawings of each printed piece, an exploded assembly view,
and (optionally) an assembly animation. This is the standard operating
procedure behind `.github/agents/mechanical-lead.agent.md` for the
**documentation phase**, distinct from `.github/skills/enclosure-design/SKILL.md`
(which is for *creating* the parametric CAD model from an
Electronics->Mechanical Interface contract in the first place). Run this
skill **after** a revision has already passed the Design Complete Gate —
it produces no new geometry, dimension, or design decision, only
downstream artifacts describing what already exists.

## The core distinction this skill exists to close

`enclosure-design` answers "what should this part's geometry be, and why."
This skill answers "now that the geometry is approved and final, how does
a human actually put the physical parts together, and how do we show that
clearly." Conflating the two is a real risk: a visualization/documentation
pass must **never** silently redesign, resize, reorder, or reinterpret a
dimension or assembly step while producing a drawing or animation of it —
if something looks wrong while visualizing it (parts that don't actually
align the way the spec claims, an assembly step that turns out physically
impossible), that is a **new Mechanical Reviewer finding** to report, not
something to unilaterally fix or quietly smooth over in the render.

## Preconditions

- The mechanical revision has reached **Design Complete**
  (`docs/architecture.md` §8: zero open CRITICAL findings, every HIGH
  `RESOLVED` or human `ACCEPTED-RISK`, traceability matrix
  fully-verified/waived, FMEA reviewed, an ECO entry for the revision).
  Producing polished visuals of a design that has not actually cleared this
  gate risks making an unfinished/unreviewed design look more final than it
  is — confirm the gate was actually granted (`validation/change-log.md`)
  before starting.
- Print-ready STL exports already exist (`hardware/mechanical/stl/`,
  produced by the existing `stl/export/*.scad` wrapper-script convention)
  and/or the source `.scad` file is available to isolate geometry from
  directly. If STLs don't exist yet, that is itself a prerequisite export
  step (mirroring `validation/change-log.md`'s own STL-export ECO
  precedent), not something this skill invents around.
- Never invent a dimension, fastener spec, or assembly step this skill
  can't trace to the source `.scad` file, the dimensional-spec document, an
  Evidence ID (`datasheets/evidence-log.md`), or a real BOM line item.
  Where a genuine gap exists (e.g. no torque value was ever specified
  anywhere), say `UNKNOWN` and flag it — do not fill the gap with a
  plausible-sounding number
  (`.github/instructions/mechanical-design.instructions.md`).

## Tool availability — verify each session, do not assume

Mirrors `docs/architecture.md` §5.3's own discipline: check what's actually
connected **this session** before promising an output format.

- **OpenSCAD**: this project's established CAD tool throughout its
  history — confirm with `openscad --version`, don't assume it's still on
  `PATH` in a future session.
- **Blender (via `blender-*` MCP tools)**: requires a **live, verified
  connection** (`blender-get_addon_status` and/or `blender-get_scene_info`
  actually returning a real scene) — never assumed available, and known to
  have been disconnected in earlier sessions of this same project. If
  Blender is **not** connected when this skill runs:
  - The 2D orthographic drawings (OpenSCAD-only, see Procedure step 3) and
    the written assembly-instructions document (Procedure step 2) are
    **still fully producible** without it.
  - The exploded-view render and the assembly animation (Procedure steps 4
    and 5) **cannot** be produced — say so plainly (mirrors the
    `enclosure-design` skill's own "no rendered preview unless a
    verified-connected tool actually produced it" rule) rather than
    describing a hypothetical render as if it existed.
- **`ffmpeg`** (only needed for the optional animation, step 5): check
  `ffmpeg -version` on `PATH`, and separately check whether Blender's own
  build has FFMPEG support compiled in
  (`bpy.app.build_options.codec_ffmpeg`) — both were confirmed present in
  this project's own history, but re-verify rather than assume.

## Procedure

1. **Verify tooling** (above) before promising any specific output format.
2. **Determine the real assembly order and fastener facts from existing
   source documents — never invent them.** Read the dimensional-spec
   document's own assembly-order section(s) (e.g. this project's
   `bench-imu-01-dimensional-spec.md` §14/§18.9 pattern — a Rev N base
   sequence plus later-revision addenda that explicitly say whether they
   extend or reorder the base sequence), the `.scad` file's own fastener-
   related named variables (screw counts, hole diameters, insert
   specifications), `datasheets/evidence-log.md` for any purchased
   hardware (bearings, heat-set inserts, motors), and the real BOM/fab-BOM
   for cross-checkable quantities. If a fastener count or torque value is
   asserted informally in prose somewhere but doesn't match the actual
   modeled geometry, **flag the discrepancy transparently** in the new
   document rather than silently picking one number or "correcting" the
   other document yourself (a documentation-precision note, not a new
   engineering finding, unless it turns out to reflect a real geometric
   defect — see "The core distinction" above).
3. **Write the assembly-instructions document**
   (`hardware/mechanical/assembly-instructions.md` or equivalent),
   structured as: scope/status (which revision, citing the Design Complete
   ECO), safety notices restating any existing safety-relevant disposition
   honestly (a REQ-403/`MISS-016`-class or REQ-407(b)/`MISS-023`-class
   ACCEPTED-RISK disposition must be presented as exactly that —
   defense-in-depth, not proven-adequate — never upgraded to "solved" for
   the sake of a cleaner-reading document), a parts/hardware list (printed
   pieces with STL cross-reference + purchased hardware with Evidence IDs),
   tools required, the numbered build procedure itself (extending the
   source assembly-order analysis from step 2, not reinventing it), a
   fastener summary table (size/qty/confidence/torque — mark `UNKNOWN`
   plainly if no torque spec exists anywhere, per this project's own
   `MISS-025` precedent for exactly that gap), and an explicit placeholder
   for any step that depends on a part not yet fabricated (e.g. a PCB still
   in progress on a separate branch) rather than fabricating specifics that
   don't exist yet.
4. **Generate 2D orthographic drawings.** Technique used successfully in
   this project: write small, new, `include`-only OpenSCAD wrapper scripts
   (mirroring the existing `stl/export/*.scad` convention exactly — never
   edit the source `.scad` file itself) that isolate each printed piece's
   module call(s) in its real **assembled-frame** position (the same bare,
   self-positioned calls the source file's own `show_mode == "assembled"`
   branch already uses — not the print-bed orientation the `stl/export/`
   scripts use, since some pieces are flipped for printing). Render
   top/front/side views via OpenSCAD's own orthographic camera CLI flags:
   `openscad -D 'show_mode="export"' --projection=ortho --render
   --autocenter --viewall --camera=tx,ty,tz,rx,ry,rz,dist -o out.png
   script.scad` — empirically, `rx,ry,rz = 0,0,0` gives top,
   `90,0,0` gives front, `90,0,90` gives side (verify this on your own
   OpenSCAD version before trusting it, per this project's own "prototype
   and visually verify before scaling to the full set" discipline). A pure
   top-down render legitimately cannot reveal a hidden Z-height step
   directly beneath another same-colored feature — that's what front/side
   views are for, not a defect to chase. **Visually view every rendered
   image before including it** — do not assume a non-error exit code means
   the image shows what you think it shows.
5. **Build the exploded assembly view (requires Blender).**
   - Export each printed piece (plus any bought part worth showing as
     context, e.g. a bearing — as a reference-only ghost, not counted
     among the printed pieces) as an **assembled-position** STL, using the
     same wrapper-script technique as step 4.
   - Import all parts into Blender (`bpy.ops.wm.stl_import` in Blender
     4.x/5.x; `bpy.ops.import_mesh.stl` as an older fallback).
   - **Verify the imported parts' real assembled-frame alignment before
     touching anything** — cross-check each imported mesh's bounding box
     against independently-derived data (e.g. the existing `stl/README.md`
     bounding-box table, if one exists) rather than eyeballing the
     Blender viewport. If something doesn't actually line up the way the
     spec claims, stop and report it as a potential Mechanical Reviewer
     finding — do not nudge geometry into looking right.
   - Apply artificial "explode" offsets — primarily along whatever axis
     the source design's own Z-stack (or equivalent) framing already uses,
     documenting that the offsets are for visualization only, not real
     assembly clearances. **A pure single-axis (e.g. Z-only) explode can
     make wide, lower parts invisible from any elevated camera angle**,
     purely from orthographic depth-occlusion (a taller part directly
     above can hide a wider, lower one even though they're correctly
     separated in that one axis) — add a lateral stagger with a component
     *perpendicular* to the camera's own azimuth direction to guarantee
     real, visible screen-space separation, not just correct-but-hidden 3D
     separation.
   - Also watch for a **ground-reference plane occluding low pieces** if
     you add one for shadow-catching — it must be repositioned below the
     true lowest point of the *exploded* (not pre-explode) scene, or it
     will literally bury whatever moved below its original height.
   - Render via a real `bpy.ops.render.render(write_still=True)`, not
     `get_viewport_screenshot` after a script-driven camera change — the
     interactive viewport does not reliably reflect script-driven view
     changes without extra redraw handling, while a real render always
     uses the current scene/camera state directly.
   - Color each part distinctly and add a caption/legend (a short Pillow
     (PIL) post-process onto the rendered PNG works well) so the render is
     self-explanatory without a separate cross-reference.
6. **Build the assembly animation (optional; requires Blender + a verified
   video-export path).** Extends the same exploded-view scene: keyframe
   each part's `location` from its exploded position to its assembled
   position (or the reverse), **staggered across stages that follow the
   real build order determined in step 2** — not an arbitrary order.
   - **Direction**: exploded→assembled reads as "watching it get built";
     assembled→exploded reads as a teardown/disassembly view. Either is
     valid — state which was chosen and why.
   - **Blender 4.4+/5.x moved F-curve access off the old
     `action.fcurves`** onto a new layered structure:
     `action.layers[0].strips[0].channelbags[i].fcurves`. Check which API
     your Blender version actually exposes rather than assuming the older
     path still works.
   - Set each F-curve's `extrapolation = 'CONSTANT'` so a part correctly
     holds its position before its own stage starts and after it ends,
     rather than drifting.
   - **Verify the format is actually deliverable before promising it** —
     check both a system `ffmpeg` binary and, separately, whether the
     running Blender build has FFMPEG support compiled in
     (`bpy.app.build_options.codec_ffmpeg`). If rendering via a tool with a
     practical per-call time budget, render a PNG frame sequence in chunks
     (repeatedly setting `scene.frame_start`/`frame_end` to a sub-range and
     calling `render(animation=True)` again — each frame is an independent
     file, so this resumes cleanly) rather than trying to "resume" a
     single continuous video-muxed output across multiple calls. Encode
     the finished PNG sequence to MP4/GIF with a single external `ffmpeg`
     pass afterward.
   - Render a handful of widely-spaced sample frames first and **visually
     verify** the sequence actually shows progressive motion (a pixel-diff
     between sample frames is a cheap, objective sanity check if the
     motion looks subtler than expected at a given camera framing) before
     committing to the full render.
7. **Document the methodology.** Write (or update) a `drawings/README.md`-
   style document explaining what was generated, with which tool, and the
   exact regeneration commands — this is the first time most projects will
   have done 2D drawings/exploded views/animations, so the convention needs
   to be written down, not left as tribal knowledge in a chat transcript.
   Include any real bugs hit and fixed along the way (see "Common failure
   modes" below) so a future run of this same skill doesn't rediscover them.

## Output

- `hardware/mechanical/assembly-instructions.md` (or equivalent path for a
  different board/project).
- `hardware/mechanical/drawings/scad/` — new, `include`-only OpenSCAD
  wrapper scripts (assembled-frame per-part isolation).
- `hardware/mechanical/drawings/2d/` — rendered 2D orthographic PNGs.
- `hardware/mechanical/drawings/exploded/` — exploded-view render + its
  own reproducible Blender build script.
- `hardware/mechanical/drawings/animation/` (optional) — assembly
  animation (video + reproducible build script).
- `hardware/mechanical/drawings/README.md` — the methodology/regeneration
  document from step 7.
- A `validation/change-log.md` ECO entry (documentation-only generation,
  no `.scad` geometry/dimension/module body changed — mirrors this
  project's own STL-export ECO precedent).

## Common failure modes to avoid

- Forgetting the `-D 'show_mode="export"'` (or equivalent) flag when
  isolating a single part via an `include`-only wrapper script — without
  it, the parent file's own default top-level render block executes too,
  silently superimposing the whole assembly underneath the one part you
  meant to isolate. Always visually check the render, don't just check for
  a non-error exit code.
- Treating a top-down 2D view's inability to show a hidden Z-step as a
  rendering bug — it's an inherent, correct property of flat-shaded
  orthographic top views; the front/side views carry that information
  instead.
- Exploding a scene along only one axis and assuming "no visible gap"
  means "misaligned" — check whether an elevated camera's own depth
  ordering (occlusion) is hiding an otherwise-correctly-separated part
  before concluding something is wrong.
- Trusting `get_viewport_screenshot` to reflect a script-driven camera or
  frame change — use a real render call instead.
- Presenting a restated ACCEPTED-RISK safety disposition as if this pass
  resolved or improved it — a documentation pass changes nothing about the
  underlying risk; say so plainly, every time it's mentioned.
- Silently "fixing" an apparent misalignment or inconsistency discovered
  while visualizing an already-Design-Complete design — report it as a
  potential new Mechanical Reviewer finding instead, per "The core
  distinction" above.
- Skipping the methodology write-up (step 7/Output) because the concrete
  deliverable already looks done — without it, the next person (or the
  next revision) re-derives the same technique from scratch, including its
  bugs.
