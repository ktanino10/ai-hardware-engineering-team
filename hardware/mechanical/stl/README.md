# Bench-IMU-01 — STL Export (Rev 5, Mechanical scope)

Print-ready STL exports of the **complete current mechanical assembly** on
this branch — Rev 3/4/4.1's enclosure topology (unchanged in kind) resized
this revision (MISS-034, CRITICAL) to fit the real 150×95mm PCB
(`hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb`, superseding a Rev 3
100×50mm PROPOSAL that was never re-handed-off after the real board was
laid out). See `validation/open-issues.md` MISS-034 and
`validation/change-log.md`'s Rev 5 ECO entry for the full re-derivation.
**Not yet independently re-reviewed as of this export** — see this
revision's own Mechanical Reviewer cycle in `validation/design-review.md`
for that pass's verdict.

**Also fixed this session, independently of and unrelated to the PCB
resize** (MISS-036, RESOLVED): the `pinch_guard()` print_layout
quadrant-cutting tool had a real, pre-existing (Rev 4.1) geometry bug that
silently clipped ~35.4% of material off each printed quadrant piece (a
triangular "chord" cutting tool that does not actually reach the ring's own
outer radius at the wedge's angular midpoint, for a 90°-wide cut). Fixed by
deriving the cutting tool's reach from the wedge's own half-angle. See
piece 5's own row below and MISS-036 in `validation/open-issues.md` for the
full re-derivation (3 independent volume-measurement methods).

## Tooling honesty

Rendered this session with the local `openscad` CLI (v2026.08.30,
`--backend=manifold`), independently re-verified — every file below is
`Status: NoError`, manifold, per OpenSCAD's own CGAL-based check (see
per-file notes). No physical printer, slicer, or fit-check was performed —
these are geometry exports only, same tooling-honesty discipline as the
rest of this repository (`docs/architecture.md` §5.3/§13). A human should
still slice and print-test before relying on these for a real build.

## The 5 distinct printed pieces

Every physically distinct printed piece has its own STL — repeated
*identical* copies of the same piece (the pinch guard) are **not**
duplicated into multiple files; see that piece's own note below.

| # | File | Source module(s) | Print qty | Orientation | Notes |
|---|---|---|---|---|---|
| 1 | `bench-imu-01-base-assembly.stl` | `base()` + `bmount_flange()` + `rotation_index_pointer()` + `cable_anchor_tab()`×2 | 1 | Floor-down (natural) | **Rev 3's `base()` fused with Rev 4's `bmount_flange()` — these print as ONE combined job**, per the source file's own print_layout comment. **Rev 5 (this revision, MISS-034)**: `base()`'s own footprint grew with the PCB resize (150×95mm real board, was a 100×50mm proposal) — see the bounding-box table below for the new measured size. Requires **slicer-generated internal support material** for the disclosed internal-overhang manufacturability finding (`bench-imu-01-dimensional-spec.md` §18.4) — a real, confirmed caveat, unaffected by this revision's own resize. `trimesh` reports `watertight=False` on this one file — already diagnosed (by the Mechanical Lead, re-confirmed independently this pass) as a benign coincident-edge-seam tessellation artifact, **not** a real manifold defect: OpenSCAD's own CGAL check independently confirms `NoError`, manifold, Genus 10 (this isolated piece). |
| 2 | `bench-imu-01-pcb-lid.stl` | `pcb_lid()` | 1 | Roof-down (flipped) | **Rev 5 (this revision, MISS-034)**: resized with the PCB bay — see bounding-box table below. |
| 3 | `bench-imu-01-containment-cap.stl` | `containment_cap()` | 1 | Dome-down (flipped) | Rev 3 geometry — **confirmed formula-independent of the PCB resize, unchanged by Rev 5**. The flywheel safety-containment piece — REQ-403/MISS-016, human ACCEPTED-RISK (Rev 3, ECO-024/025); disclosed as **defense-in-depth, not proven-adequate** containment (see that disposition for the full caveat — unchanged by this export). |
| 4 | `bench-imu-01-stand-plate.stl` | `stand_plate()` | 1 | Flat, either face down | Rev 4. Bolts to the bearing's stationary (bottom) plate; the piece that actually contacts the desk. 120mm diameter, sized via the computed CG/tip-over analysis (`bench-imu-01-dimensional-spec.md` §18.3) — **confirmed formula-independent of the PCB resize, unchanged by Rev 5**. |
| 5 | `bench-imu-01-pinch-guard-quadrant.stl` | `pinch_guard(0)` | **4** (all four quadrants are geometrically identical — verified by direct inspection of the module body, a perfectly rotationally-symmetric ring cut at four evenly-spaced 90° angles; this is not 1-of-4-different-shapes) | Flat | Rev 4.1 — the MISS-023 pinch-point-hazard mitigation. **`pinch_guard_or`=115.0mm itself is unchanged by Rev 5's PCB resize**, but the hazard radius it is measured against (`rotating_env_max_r`) grew from 126.424mm to 176.259mm as a side effect of the resize (the PCB bay is part of the rotating assembly) — coverage dropped from ≈77.7% to ≈35.0% of the (now larger) hazard band. **Not silently carried forward**: MISS-023 has been re-opened (OPEN/HIGH, was ACCEPTED-RISK) in `validation/open-issues.md` pending fresh human review of this materially changed picture. **Also fixed this session (MISS-036, RESOLVED, unrelated to the PCB resize)**: a real, pre-existing print_layout quadrant-cutting geometry bug that clipped ~35.4% of material off each quadrant (a chord-based cutting tool too small for a 90° wedge) — this STL now has the CORRECT, full-intended geometry for the first time; see MISS-036. Split into 4 quadrants deliberately, **not** because any printer-bed-size limit is known for this project (none is documented anywhere in this repo — this was not invented), but so each piece's own bounding box (~115×115mm) prints on virtually any consumer FDM printer without needing that assumption at all. |

**Not exported as separate pieces** (already part of piece 1's own combined
print job, per the source file's own module design):
`rotation_index_pointer()` and both `cable_anchor_tab()` instances are
small features fused to `base()`'s own wall — see the `.scad` file's
"Section 5" show_mode comments for exactly which calls belong to which
combined print job.

## Bounding-box sanity check (independently re-verified this revision, via `trimesh`)

| File | Bounding box (mm) | Cross-check |
|---|---|---|
| `bench-imu-01-base-assembly.stl` | 173.0 × 213.0 × 51.0 | REV 5 (was 123.0×168.0×51.0 pre-MISS-034): grew with the PCB bay's own `base_outer_x/y` (107→157mm / 57→102mm) plus the same `bmount_flange`/tab/cable-anchor-tab protrusions as before, all formula-derived, not hand-fit |
| `bench-imu-01-pcb-lid.stl` | 161.4 × 114.8 × 5.0 | REV 5 (was 111.4×69.8×5.0): X matches `lid_skirt_outer_x`=161.4mm exactly; Y (114.8mm) is larger than `lid_skirt_outer_y`=106.4mm for the same reason as before — the 4 corner tabs (`lid_tab_project`=6.8mm) project outward beyond the skirt on the north/south sides — expected, not a discrepancy |
| `bench-imu-01-containment-cap.stl` | 109.4 × 109.4 × 12.0 | UNCHANGED by Rev 5 (confirmed formula-independent of PCB size) — matches `cap_skirt_od`=109.4mm exactly |
| `bench-imu-01-stand-plate.stl` | 120.0 × 120.0 × 6.0 | UNCHANGED by Rev 5 (confirmed formula-independent of PCB size) — matches `stand_plate_or`×2=120.0mm exactly |
| `bench-imu-01-pinch-guard-quadrant.stl` | 115.0 × 115.0 × 14.9 | Footprint UNCHANGED (`pinch_guard_or`=115.0mm was deliberately NOT resized — see MISS-023's re-opened entry). Internal volume CORRECTED this session (MISS-036): 112,314.52mm³ (was a buggy 72,803.19mm³, a real ~35.4% shortfall) — now matches the analytic ideal (112,635.9mm³) to within 0.29% (expected `$fn=48` faceting). 4×112,314.52mm³×1.27g/cm³(PETG) = 570.56g, now exactly matching this design's own previously-recorded full-ring reference mass |

## Regenerating these files

Each STL has a matching wrapper script in `export/` that isolates just
that piece's module call(s) from the full `bench-imu-01-enclosure.scad`
file, without modifying it. The technique: `include` the parent file (to
get its module/variable definitions), then set `show_mode` to a value that
matches **neither** of the parent file's own `"assembled"`/`"print_layout"`
branches via `-D`, so nothing from those two branches renders — leaving
only the wrapper's own appended module call as the output. From this
directory:

```sh
cd export
openscad -D 'show_mode="export"' --backend=manifold --export-format binstl -o ../bench-imu-01-base-assembly.stl        export-base-assembly.scad
openscad -D 'show_mode="export"' --backend=manifold --export-format binstl -o ../bench-imu-01-pcb-lid.stl               export-pcb-lid.scad
openscad -D 'show_mode="export"' --backend=manifold --export-format binstl -o ../bench-imu-01-containment-cap.stl       export-containment-cap.scad
openscad -D 'show_mode="export"' --backend=manifold --export-format binstl -o ../bench-imu-01-stand-plate.stl           export-stand-plate.scad
openscad -D 'show_mode="export"' --backend=manifold --export-format binstl -o ../bench-imu-01-pinch-guard-quadrant.stl  export-pinch-guard-quadrant.scad
```

All 5 files are **binary STL** (`--export-format binstl` — OpenSCAD's ASCII
STL default is far larger for no benefit; binary is the standard format
virtually all slicers accept). Total: ≈720KB for all 5 pieces combined.

No wrapper script edits any dimension, module body, or manufactured
geometry — each one only calls the exact same module(s)/transform(s) the
parent file's own `print_layout` show_mode already uses for that piece.

## Related documents

- `hardware/mechanical/bench-imu-01-enclosure.scad` — the source geometry.
- `hardware/mechanical/bench-imu-01-dimensional-spec.md` §18 — full Rev
  4/4.1 rationale, CG/tip-over analysis, manufacturability findings.
- `hardware/mechanical-interface.md` Part C — bearing/free-rotation
  interface facts.
- `validation/open-issues.md` MISS-023 (ACCEPTED-RISK), MISS-024
  (RESOLVED), MISS-025 (OPEN, MEDIUM, non-gating — bearing-mount fastener
  load, no calc performed) — real, disclosed caveats that apply to
  pieces 1/4/5 above regardless of this export.
- `validation/change-log.md` ECO-029/030/031 — the full design + review +
  disposition history.
