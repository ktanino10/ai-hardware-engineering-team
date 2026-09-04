#!/usr/bin/env python3
"""
Bench-IMU-01 -- Exploded-view legend + fastener-callout post-process (PIL).

REV 5 STALENESS NOTE (this session, MISS-034 -- read before touching
ANCHOR_PX or the world-space points below): the Bench-IMU-01 PCB was
resized from a 100x50mm proposal to the real 150x95mm board this session.
This grows the PCB lid's own bounding box and shifts `fw_cx` (53.5mm ->
78.5mm), both of which make the world-space reference points quoted in
"Regenerating anchor points" below (and therefore the derived `ANCHOR_PX`
pixel values) STALE relative to the current geometry. Blender is NOT
connected this session (`blender-get_addon_status` handshake failed,
independently re-checked, not assumed) -- so `ANCHOR_PX` below has
DELIBERATELY NOT been hand-edited or guessed at: doing so without an
actual `world_to_camera_view()` re-projection AND a visual re-confirmation
against a fresh render (this docstring's own established, more rigorous
method) would produce numbers no more trustworthy than a guess, which this
project's own conventions treat as worse than an honest, disclosed gap.
The base PNG render this script consumes is ALSO stale (see
`build_exploded_view.py` and `../README.md` Method 2's own staleness
note) -- both must be regenerated TOGETHER in a future session with
Blender connected, using the unchanged procedure below.

Takes the raw Blender render produced by `build_exploded_view.py`
(no legend, no annotations -- pure 3D render) and adds:

1. A legend strip below the render, one row per part (color swatch +
   name + one-line cross-reference), matching this project's existing
   legend convention (`drawings/README.md` Method 2's own "colors are a
   legend, not decoration" note).
2. Fastener leader-line callouts for the 3 joints named in this task's own
   request: PCB-lid corner screws, containment-cap heat-set inserts, and
   motor (M1) mount screws. Every fact in a callout label (size/qty/
   confidence) is copied verbatim from `../../assembly-instructions.md`
   Sec 5's own fastener summary table -- nothing invented here.

Anchor points for the 3 leader lines are NOT eyeballed: they were computed
once, in Blender, via `bpy_extras.object_utils.world_to_camera_view()`
against the exact same camera/scene `build_exploded_view.py` builds, from
real assembled-frame bounding-box data (independently measured from the
exported STL binaries, not read off the .scad source) plus each part's own
known OFFSETS entry. See ANCHOR_PX below for the resulting pixel
coordinates and how they were derived -- re-run the projection snippet in
this docstring's "Regenerating anchor points" section if OFFSETS/camera
ever change **(REV 5: also re-run this because `pcb_lid_screw`'s own
world-space point below and `motor_screw`'s own `fw_cx`-dependent point
are both now stale, per the note at the top of this docstring)**.

## Regenerating anchor points (if OFFSETS or the camera setup ever change)

Paste this into a Blender MCP `execute_blender_code` call (or the
Scripting tab) right after `build_exploded_view.py`'s own `main()` has run
(reuses that same scene/camera):

    import mathutils
    from bpy_extras.object_utils import world_to_camera_view
    RES_X, RES_Y = 2000, 1500
    anchors = {
        "pcb_lid_screw": mathutils.Vector((109.2, 98.6, 23.1)) + mathutils.Vector(OFFSETS["assembled-pcb-lid"]),
        "cap_heatset":   mathutils.Vector((108.2, 52.5, 43.0)) + mathutils.Vector(OFFSETS["assembled-containment-cap"]),
        "motor_screw":   mathutils.Vector((53.5, 52.5, 19.25)) + mathutils.Vector(OFFSETS["assembled-reference-motor-body"]),
    }
    for name, wp in anchors.items():
        co = world_to_camera_view(bpy.context.scene, bpy.context.scene.camera, wp)
        print(name, co.x * RES_X, (1.0 - co.y) * RES_Y)

(The 3 world-space base points above are each a real corner/centroid of
that part's own assembled-frame STL bounding box -- measured directly from
the exported binary STL, not the .scad source formula -- plus its OFFSETS
entry from `build_exploded_view.py`.)

## Regenerating this post-process
    python3 build_exploded_view_annotations.py \
        --input /tmp/bench-exploded-stl/exploded-view-render.png \
        --output ../exploded/bench-imu-01-exploded-view.png
"""

import argparse
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/System/Library/Fonts/Supplemental"
FONT_REGULAR = f"{FONT_DIR}/Arial.ttf"
FONT_BOLD = f"{FONT_DIR}/Arial Bold.ttf"

LEGEND_TITLE = "Bench-IMU-01 \u2014 Exploded Assembly View (Rev 4/4.1 mechanical scope)"

# (swatch color 0-255 RGB, label text) -- one row per part, in the same
# order as build_exploded_view.py's own PARTS/COLOR_MAP/REFERENCE_GHOST_COLORS.
LEGEND_ROWS = [
    ((89, 140, 204), "1. Base assembly \u2014 base() + bmount_flange() + rotation_index_pointer() + cable_anchor_tab()\u00d72 (ONE printed piece)"),
    ((115, 191, 115), "2. PCB lid \u2014 pcb_lid()  (M2.5 self-tap \u00d7 4 corner tabs)"),
    ((230, 140, 51),  "3. Containment cap \u2014 containment_cap()  (6\u00d7 M3 into heat-set inserts; REQ-403 safety part, installed LAST)"),
    ((140, 140, 148), "4. Stand plate \u2014 stand_plate()  (bolts to bearing's stationary plate; true system ground plane)"),
    ((204, 64, 77),   "5. Pinch guard \u2014 pinch_guard(), full ring = 4 identical printed quadrants  (REQ-407(b) partial mitigation)"),
    ((191, 194, 199), "6. BC Precision 4LS-3 bearing \u2014 REFERENCE ONLY, not printed/exported (shown translucent)"),
    ((56, 59, 69),    "7. Motor (M1), T-Motor MN2206-13 KV2000 \u2014 REFERENCE ONLY, housing/stator half (shown translucent) -- NEW this pass"),
    ((158, 46, 173),  "8. Flywheel + hub collar \u2014 REFERENCE ONLY, rotating half (shown translucent) -- NEW this pass"),
]

REVISION_NOTE = (
    "Rows 7-8 (motor + flywheel) were added this pass, reversing an earlier "
    "documentation decision to leave them out -- see drawings/README.md and "
    "assembly-instructions.md \u00a74.2/\u00a74.4 for the full disclosure."
)

# Precomputed anchor points (pixel coords in the RAW 2000x1500 render).
# `motor_screw` was derived via bpy_extras.object_utils.world_to_camera_view()
# against the real camera (see module docstring above) and visually
# confirmed to land on the motor-body ghost. `pcb_lid_screw`/`cap_heatset`
# were cross-checked two ways: the same camera-projection technique AND an
# independent per-pixel hue-cluster scan of the actual rendered PNG (finds
# each part's own real on-screen pixel region directly, not a 3D-geometry
# guess) -- the hue-cluster centroids are used here since the camera-
# projected corner points for those 2 parts landed close enough to the
# containment-cap/flywheel-rotor boundary from this camera angle to risk
# ambiguity; the hue-cluster centroids are unambiguously inside each
# part's own visible blob.
ANCHOR_PX = {
    "pcb_lid_screw": (1483, 595),
    "cap_heatset":   (1264, 497),
    "motor_screw":   (1393.8, 670.2),
}

# Callout label text + where to route the leader line's free end (in the
# RAW render's own coordinate space -- a fixed open-background corner each
# picked so the label box doesn't have to guess what's behind it; a solid
# label backing rect makes it legible either way).
CALLOUTS = [
    {
        "anchor": "pcb_lid_screw",
        "label_pos": (1560, 260),
        "text": "4\u00d7 M2.5 self-tap, 6.0mm\nPCB lid \u2192 base corner tabs\nCONFIRMED (geometry)",
    },
    {
        "anchor": "cap_heatset",
        # label_pos.x moved 1600->1490 (Mechanical Reviewer Cycle 8 fix,
        # 2nd pass): the corrected 4-line text below is wider than the
        # original 3-line text (see comment), and at x=1600 its box right
        # edge (label_pos.x + text width + padding) ran past the 2000px
        # canvas edge, clipping "Safety: ACCEPTED-RISK -- see MISS-016" to
        # "...MISS-0". Re-measured with PIL's own textlength() against the
        # actual render font/size (not eyeballed): longest line is 425.4px,
        # so x=1490 keeps the box's right edge at ~1932px, comfortably
        # on-canvas. Vertical position/leader-line anchor unchanged.
        "label_pos": (1490, 120),
        # FIXED (Mechanical Reviewer Cycle 8, MISS-031, HIGH): the previous
        # text here read "CONFIRMED -- safety joint, REQ-403", which does
        # NOT appear anywhere in assembly-instructions.md Sec 5's own table
        # (only "CONFIRMED (insert match)" does) -- it invented an unearned
        # safety-adequacy connotation for a joint whose real safety
        # disposition is HIGH/ACCEPTED-RISK, NOT proven-adequate
        # (validation/open-issues.md MISS-016). Fixed to state only what
        # the table actually confirms (the insert dimension match) plus an
        # explicit, correct cross-reference to the real safety disposition
        # -- mirrors the correct framing already used on this same part's
        # own drafting sheet (../drafting-sheets/).
        "text": "6\u00d7 M3 \u2192 Ruthex RX-M3\u00d75.7\nheat-set insert (containment cap)\nCONFIRMED (insert match)\nSafety: ACCEPTED-RISK \u2014 see MISS-016",
    },
    {
        "anchor": "motor_screw",
        "label_pos": (1120, 280),
        "text": "4\u00d7 M3 plain screws\nMotor (M1) \u2192 motor platform\nASSUMPTION, torque UNKNOWN",
    },
]


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def draw_callouts(draw, canvas_w, canvas_h):
    """Draw each fastener callout's leader line + label box.

    `canvas_w`/`canvas_h` bound the RAW render region (the label boxes must
    stay within it, not the taller legend-strip canvas below). Label
    position is clamped here -- a previous version of this function had a
    comment claiming boxes were "kept on-canvas" with no code actually
    doing it, which let a real clipping bug through undetected (Mechanical
    Reviewer Cycle 8 fix-verification pass, found while re-rendering the
    MISS-031 text fix: the longer corrected text pushed the containment-cap
    callout's right edge ~33px past the canvas edge, truncating "...MISS-016"
    to "...MISS-0"). This clamp makes that class of bug impossible instead
    of relying on manually re-measuring text width by hand each time.
    """
    label_font = load_font(FONT_REGULAR, 22)
    margin = 12
    for c in CALLOUTS:
        ax, ay = ANCHOR_PX[c["anchor"]]
        lx, ly = c["label_pos"]
        # Anchor dot
        r = 7
        draw.ellipse([ax - r, ay - r, ax + r, ay + r], fill=(20, 20, 20, 255), outline=(255, 255, 255, 255), width=2)
        # Label background + text (multi-line)
        lines = c["text"].split("\n")
        line_h = 26
        pad = 8
        max_w = max(draw.textlength(l, font=label_font) for l in lines)
        box_w = max_w + 2 * pad
        box_h = len(lines) * line_h + 2 * pad
        # Clamp so the box never runs off any edge of the raw render, no
        # matter how the label text or its length changes in the future.
        lx = max(margin + pad, min(lx, canvas_w - margin - box_w + pad))
        ly = max(margin + pad, min(ly, canvas_h - margin - box_h + pad))
        box = [lx - pad, ly - pad, lx + max_w + pad, ly + len(lines) * line_h + pad]
        # Leader line (drawn after clamping so it still points at the box
        # actually rendered, not the pre-clamp requested position).
        draw.line([(ax, ay), (lx, ly)], fill=(20, 20, 20, 255), width=3)
        draw.rectangle(box, fill=(255, 255, 255, 235), outline=(20, 20, 20, 255), width=2)
        for i, l in enumerate(lines):
            draw.text((lx, ly + i * line_h), l, font=label_font, fill=(20, 20, 20, 255))


def build(input_path, output_path):
    render = Image.open(input_path).convert("RGBA")
    w, h = render.size

    row_h = 42
    title_h = 56
    legend_h = title_h + row_h * len(LEGEND_ROWS) + 60  # +60 for the revision note

    canvas = Image.new("RGBA", (w, h + legend_h), (255, 255, 255, 255))
    canvas.paste(render, (0, 0))
    draw = ImageDraw.Draw(canvas)

    # Callouts drawn onto the render region first (so the anchor dots/lines
    # sit on top of the 3D render, not the legend strip).
    draw_callouts(draw, w, h)

    # Legend strip
    title_font = load_font(FONT_BOLD, 34)
    row_font = load_font(FONT_REGULAR, 26)
    note_font = load_font(FONT_REGULAR, 20)

    y = h + 12
    draw.text((16, y), LEGEND_TITLE, font=title_font, fill=(20, 20, 20, 255))
    y += title_h

    swatch = 28
    for color, text in LEGEND_ROWS:
        draw.rectangle([16, y + 4, 16 + swatch, y + 4 + swatch], fill=color, outline=(20, 20, 20, 255))
        draw.text((16 + swatch + 12, y + 4), text, font=row_font, fill=(20, 20, 20, 255))
        y += row_h

    y += 8
    draw.text((16, y), REVISION_NOTE, font=note_font, fill=(90, 90, 90, 255))

    canvas.convert("RGB").save(output_path)
    print(f"Wrote {output_path} ({canvas.size[0]}x{canvas.size[1]})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    build(args.input, args.output)
