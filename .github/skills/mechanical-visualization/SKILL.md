---
name: mechanical-visualization
description: Produce early WIP assembly-process planning/animation and installed/per-stage evidence, then separately gated approved assembly documentation. Use whenever a multi-part assembly must be understood, checked or built, and whenever Fusion animation is requested; deliver genuine Autodesk Fusion native storyboards and a playable published video, not a substitute render.
---

# Skill: Mechanical Visualization

## Purpose

Make the real assembly process inspectable **during design**, not only after
approval: instructions, orthographic drawings, full installed/per-stage
geometric evidence and Autodesk Fusion Animation. Follow
`docs/assembly-evidence.md`'s two states and revision manifest:
**WIP - NOT ASSEMBLY READY** for early planning, animation and blocker review;
**APPROVED assembly documentation** only after complete evidence, independent
acceptance, Design Complete and the named safety decisions. WIP labels belong
in the artifacts/storyboards/videos as well as the manifest.

For applicable multi-part assemblies here, Fusion Animation is the standard
workflow and native/archive plus playable published video are deliverables,
mandatory when explicitly requested. Do not silently replace them with
Blender, three.js, stills, a script, or an attractive exploded view.

## The core distinction this skill exists to close

`enclosure-design` answers "what should this part's geometry be, and why."
This skill answers "can a human actually put these parts together, and how
do we show and inspect that process." Conflating the two is a real risk:
a visualization/documentation
pass must **never** silently redesign, resize, reorder, or reinterpret a
dimension or assembly step while producing a drawing or animation of it —
if something looks wrong while visualizing it (parts that don't actually
align the way the spec claims, an assembly step that turns out physically
impossible), that is a **new Mechanical Reviewer finding** to report, not
something to unilaterally fix or quietly smooth over in the render.

## Preconditions

- Identify the source revision, canonical geometry owner and available
  interface/BOM facts. **Design Complete is not an entry condition for WIP.**
  Missing source dimensions/interfaces remain UNKNOWN, with owner and source
  investigation/alternative action; continue the evidence work that does
  not depend on guessing them.
- Use existing source `.scad`/CAD and exports where available. Prepare missing
  per-part exports from that source using verified tools; do not call them
  print-ready merely because they exported successfully.
- Before APPROVED release, verify the actual Design Complete decision
  (`docs/architecture.md` §8), independent evidence acceptance and named
  safety decisions. The same five conditions and human fabrication/power/
  flashing gates still apply. Early blocker review is not final readiness.
- Never invent a dimension, fastener spec, or assembly step this skill
  can't trace to the source `.scad` file, the dimensional-spec document, an
  Evidence ID (`datasheets/evidence-log.md`), or a real BOM line item.
  Where a genuine gap exists (e.g. no torque value was ever specified
  anywhere), say `UNKNOWN` and flag it — do not fill the gap with a
  plausible-sounding number
  (`.github/instructions/mechanical-design.instructions.md`).

## Tool availability — verify each session, do not assume

Record a dated `tool_preflight` matrix, not a single "Fusion connected" flag:

| Operation | Record separately |
|---|---|
| Application/tool discovery | Installed/running version, exposed tool schema and actual connection/execution result this session |
| Model preparation/import/authoring | Supported units, physical components/occurrences, coordinate placement and observed import result |
| Animation authoring | Workspace access, storyboard creation, timed component transforms, view/visibility/callout actions; which operations were actually exercised |
| Native persistence | Save/archive format, external-reference handling, saved storyboards and actual reopen result |
| Published video | Publish path/scope/format, observed export result and real media-player playback |

For each operation distinguish **documented public API**, **documented UI**
and **agent execution availability**. Mark unexercised behavior UNCONFIRMED,
even if a version is installed or SDK symbols exist. Cite official
documentation; an absent search result proves neither support nor absence.

Official references checked 2026-09-05 (documentation, not a standing runtime
claim): [Animation workspace/storyboards/actions][fusion-animation],
[AnimationManager][animation-manager] and [Storyboard][storyboard].
The latter two say introduced May 2026: do not preserve an obsolete "no
Animation API" rule. Storyboard creation/playback/view recording do not by
themselves establish component-action authoring or video publishing.
`Occurrence.transform2` describes model placement; camera view recording is
not evidence that component transforms become animation actions. Verify
each intended API operation against its current authoritative reference
and the running version before depending on it.

Exposed `fusion_*` MCP tools marked EXPERIMENTAL/UNVERIFIED are **prohibited
for real deliverables**; the observed experimental surface does not expose
Animation authoring. This says nothing about the application's entire public
API. Use an actually available supported API execution path or documented
UI operated through approved host controls, not invented tools, undocumented
command/click macros or a shell-driven UI workaround. Do not install plugins,
create a new MCP/extension, or change user Fusion preferences to evade a
blocker; such integration work is a separate approved task.

If a required UI/API operation cannot be executed, record its exact
capability blocker and observed error/absence, prepare the source files,
component/transform map and stage plan, and hand off only the smallest missing
operation with named inputs, documented UI steps, expected outputs and a
reopen/playback check. Keep native/video status BLOCKED, not delivered.

OpenSCAD (`openscad --version`), Blender (discover its actual tools and verify
a live scene) and any `ffmpeg` export path must likewise be checked each
session before use. They can support source preparation, supplementary
drawings or explicitly allowed alternative workflows; none silently
satisfies an explicit Fusion deliverable.

[fusion-animation]: https://help.autodesk.com/cloudhelp/ENU/Fusion-Animate/files/GUID-25E6D2E0-8057-4BFF-93B3-E7AEE2C4404A.htm
[animation-manager]: https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_AnimationManager.htm
[storyboard]: https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Storyboard.htm

## Procedure

1. **Start the revision-linked WIP manifest and verify tooling** (above).
   Reconcile the complete required inventory against requirements, BOM and
   interfaces; include missing parts as gaps, not invisible omissions.
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
   structured as: scope/status (source revision and WIP label, or actual
   Design Complete/approval references for release), safety notices
   restating any existing safety-relevant disposition
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
4. **Generate 2D orthographic drawings with verified tooling.** The existing
   OpenSCAD technique is: write small, new, `include`-only wrapper scripts
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
5. **Author the requested Autodesk Fusion assembly animation.**
   - Prepare one source-linked physical component per manufactured/purchased
     part instance (including repeated fasteners and sensor modules), not a
     single anonymous mesh of the entire assembly. Map stable part/BOM IDs
     to named Fusion components/occurrences in `component_map`.
   - Export/import in the **real assembled coordinate frame**, not the
     print-bed layout. Record source files/hashes, units, axis/handedness,
     origin and each instance's installed transform. STL has no dependable
     unit metadata: specify the import units and verify known source
     dimensions. Do not silently recenter each part or apply print rotations.
   - Inspect one imported part/assembly relationship before scaling up;
     compare bounding boxes, known dimensions, part counts and transforms
     against the source, then check the whole installed assembly. Retain
     distinctions between sourced dimensions, allocations and UNKNOWNs.
     Do not move an installed pose to make a visual fit.
   - In the documented **Animation workspace**, name storyboards for the
     actual source-defined build/service sequence. At time zero or the
     scratch zone transforms set up the scene without recording actions;
     positive timeline positions capture actions (official workspace
     reference above). Use timed component, view, visibility and callout
     actions with explicit stage IDs. Use documented, runtime-confirmed API
     equivalents only where they genuinely author those actions.
   - Show real insertion, seating, fastening, connection and retention
     order, including fastener/tool approach and temporary support before
     closure. Call out hidden hardware, harness retention, sensor identity/
     orientation and safety stops; reveal views rather than hiding a
     collision with visibility changes. An exploded overview can help
     identify parts but is not a feasible path by itself.
   - For every stage and the installed state, generate the evidence in
     `docs/assembly-evidence.md`: populated/mated PCBs with mounts/insulation,
     all required electronics, motors/bells/hubs/swept envelopes, fasteners
     and retained harnesses, insertion/removal and tool access. Distinguish
     fused-print unions/bearing contacts/qualified process interference
     from forbidden separate-part overlap. Record measurements, tolerances,
     sampling and untested intervals. Animation alone proves neither
     collision-free continuous motion, support removal, strength, safety
     nor functionality.
   - Save the real Fusion design and export the supported native archive:
     `.f3d` for a self-contained design or `.f3z` for a package with external
     design references, per [Autodesk's format explanation][fusion-archives].
     Reopen the archive and verify named components, coordinate alignment,
     linked parts and the saved storyboards; a design-only archive without
     animation does not satisfy `native_animation`.
   - Use **Animation > Publish > Publish Video**, select the required
     current storyboard or whole-document scope and resolution, then save
     the actual output ([official procedure][fusion-publish]). Autodesk's
     [publish tutorial][fusion-playback] documents AVI on PC and MP4 on Mac
     and explicitly requires media-player playback. Recheck the running
     version's options, play the delivered file, inspect start/intermediate/
     end stages and record duration/scope. Keep the original published file
     and its hash if producing a separately labeled compressed derivative.
   - If an operation is unavailable, preserve prepared inputs and the precise
     supported UI/API handoff from the preflight; do not call a script,
     static model, renamed Blender video or screen still a Fusion animation.
6. **Supplementary or explicitly allowed alternative exploded view
   (Blender example, not a Fusion substitute).**
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
7. **Alternative animation only when explicitly allowed** (Blender example;
   requires a verified video-export path). An explicit Fusion request can
   change only through `animation.alternative_approval` in the manifest.
   Keyframe the source-defined stage waypoints and fastening/retention
   sequence, not arbitrary straight-line explode/home interpolation. If
   explode/home motion is used only to identify parts, label it a
   presentation view, not an assembly-feasibility demonstration.
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
8. **Document the methodology and hand off evidence.** Write (or update) a
   `drawings/README.md`-style document explaining what was generated, with which tool, and the
   exact regeneration commands — this is the first time most projects will
   have done 2D drawings/exploded views/animations, so the convention needs
   to be written down, not left as tribal knowledge in a chat transcript.
   Include source revisions, units/transforms, tool versions, generated
   hashes, stage IDs, measurements and actual capability limitations.
   Update all nine artifact statuses in the revision manifest and run
   `python3 tools/check_assembly_evidence.py --manifest <current-manifest>`.
   Request independent Mechanical Reviewer inspection now, including early
   WIP blocker review if incomplete. Only complete, independently accepted
   evidence and the existing gates permit APPROVED documentation; run
   `--require-approved` for that structural check, not as safety certification.

[fusion-archives]: https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/The-differences-between-an-f3z-and-f3d-file-in-Fusion.html
[fusion-publish]: https://help.autodesk.com/cloudhelp/ENU/Fusion-Animate/files/GUID-5C687D49-7714-469F-A8CA-FA0C5A89F823.htm
[fusion-playback]: https://help.autodesk.com/cloudhelp/ENU/Fusion-Animate/files/GUID-A3204116-91D7-4F57-B6DA-3CDF3C70C54E.htm

## Output

- `hardware/mechanical/assembly-instructions.md` (or equivalent path for a
  different board/project).
- `hardware/mechanical/drawings/scad/` — new, `include`-only OpenSCAD
  wrapper scripts (assembled-frame per-part isolation).
- `hardware/mechanical/drawings/2d/` — rendered 2D orthographic PNGs.
- `hardware/mechanical/drawings/exploded/` — exploded-view render + its
  source/tool provenance (Blender script only if that path was used).
- Revision-specific native Fusion archive and published video, with saved
  storyboards, component map and installed/per-stage evidence. Existing
  `drawings/animation/` or the manifest's revision directory may hold them;
  use unambiguous revision paths and no silent renderer substitution.
- `hardware/mechanical/assembly-evidence/<assembly>/<revision>/manifest.json`
  — WIP or APPROVED contract, exact source/artifact hashes and unresolved
  capability/input statuses (`docs/assembly-evidence.md`).
- `hardware/mechanical/drawings/README.md` — the methodology/regeneration
  document from step 8.
- A `validation/change-log.md` ECO entry (documentation-only generation,
  no `.scad` geometry/dimension/module body changed — mirrors this
  project's own STL-export ECO precedent) when generating real artifacts.
  Coordinate IDs with the integration owner; a policy-only change does not
  fabricate an artifact-generation ECO or new safety evidence.

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
- Skipping the methodology write-up (step 8/Output) because the concrete
  deliverable already looks done — without it, the next person (or the
  next revision) re-derives the same technique from scratch, including its
  bugs.
