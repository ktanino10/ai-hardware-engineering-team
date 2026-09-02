#!/usr/bin/env python3
"""
Bench-IMU-01 -- Fusion-style engineering drafting sheet generator.

Pipeline (fully OpenSCAD-source-driven -- see module docstring end for the
explicit "not a Fusion 360 drawing" disclaimer this script also stamps onto
every sheet it produces):

    bench-imu-01-enclosure.scad (real source geometry, unmodified)
        --> scad/projection-<part>.scad (new, include-only wrapper,
            `projection(cut=false)` -- top-down SILHOUETTE, not a
            cross-section; matches this project's existing wrapper-script
            convention, see `../scad/assembled-*.scad`)
        --> OpenSCAD CLI --export-format dxf (regenerable intermediate,
            NOT committed -- same convention as the exploded view's own
            assembled-position STLs)
        --> THIS SCRIPT: a small, hand-written DXF entity parser (no
            `ezdxf` dependency, per this task's own explicit "simple
            parser" instruction) + a matplotlib renderer that draws the
            real, measured geometry at true scale inside a drafting
            border + title block, with auto-measured overall-envelope
            dimension lines and (where the parsed geometry is cleanly
            circular) auto-measured diameter callouts, plus fixed-text
            fastener callouts cross-referenced to
            `../../assembly-instructions.md` Sec 5's fastener table.

## Why a hand-written parser, and what it actually needs to handle

Empirically verified this task (`openscad --export-format dxf` on this
project's OpenSCAD 2026.08.30): every exported entity is an `LWPOLYLINE`
(group codes 90=vertex count, 70=closed flag, repeated 10/20 X/Y vertex
pairs) -- NO `LINE`/`CIRCLE`/`ARC` entities and NO bulge (group code 42)
anywhere in 3 real test exports (stand_plate, containment_cap, pcb_lid).
Circles come out as many-vertex regular polygons (e.g. 48 vertices for a
full circle), not as `CIRCLE` entities. This parser's primary path handles
`LWPOLYLINE`; `LINE`/`CIRCLE`/`ARC` are supported defensively in case a
future OpenSCAD version changes its DXF exporter, but are unexercised by
this project's own real files.

## A real, disclosed limitation of `projection(cut=false)`

A BLIND hole (e.g. `stand_plate()`'s own bearing-mount pilot holes,
`bmount_pilot_depth` -- a shallow pocket, not a full through-hole) does
NOT appear as a separate contour: the silhouette from directly above is
unbroken wherever solid material still exists anywhere in the part's Z
extent, exactly the same "a top-down view can't show a hidden Z-step"
caveat this project's own `drawings/README.md` (Method 1) already
discloses for camera-based top views. Fastener positions that don't
survive into the DXF as real geometry are annotated from the KNOWN,
cited source values instead (assembly-instructions.md / the .scad
variables) with an explicit "(blind hole, not visible in this outline-only
projection)" note -- never silently inferred from a contour that isn't
actually there.

## Regenerating a sheet end to end

    cd scad
    openscad -D 'show_mode="export"' --export-format dxf \\
        -o /tmp/<part>.dxf projection-<part>.scad
    cd ..
    python3 build_drafting_sheet.py --part <part> --dxf /tmp/<part>.dxf \\
        --out bench-imu-01-<part>-drafting-sheet.png
"""

import argparse
import math
import re
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D


# ---------------------------------------------------------------------------
# 1. Hand-written DXF entity parser (LWPOLYLINE-primary; LINE/CIRCLE/ARC as a
#    defensive fallback -- see module docstring for why LWPOLYLINE is the
#    only entity type this project's own OpenSCAD version actually emits).
# ---------------------------------------------------------------------------

def _read_group_codes(lines, start):
    """Yield (code:int, value:str) pairs from `lines` starting at `start`,
    stopping (without consuming) at the next top-level '0' group code."""
    i = start
    while i + 1 < len(lines):
        code = lines[i].strip()
        if code == "0" and i != start:
            return i
        value = lines[i + 1].strip()
        yield int(code), value
        i += 2
    return i


def parse_dxf(path):
    """Returns a list of contours; each contour is a list of (x, y) floats.
    Also returns any bare CIRCLE/ARC/LINE entities as their own contours
    (polygonized for ARC/CIRCLE) so the renderer only has to deal with one
    shape: a list of (x, y) point lists."""
    with open(path, "r") as f:
        text = f.read()
    lines = text.splitlines()

    # Isolate the ENTITIES section.
    try:
        start = lines.index("ENTITIES") + 1
    except ValueError:
        raise ValueError(f"No ENTITIES section found in {path}")
    end = len(lines)
    for i in range(start, len(lines)):
        if lines[i].strip() == "ENDSEC":
            end = i - 1  # exclude the "0" group-code marker preceding ENDSEC too
            break
    body = lines[start:end]

    contours = []
    i = 0
    while i < len(body):
        if body[i].strip() == "0" and i + 1 < len(body):
            etype = body[i + 1].strip()
            j = i + 2
            codes = []
            while j + 1 < len(body):
                if body[j].strip() == "0":
                    break
                codes.append((int(body[j].strip()), body[j + 1].strip()))
                j += 2

            if etype == "LWPOLYLINE":
                xs, ys = [], []
                pending_x = None
                for code, val in codes:
                    if code == 10:
                        pending_x = float(val)
                    elif code == 20 and pending_x is not None:
                        xs.append(pending_x)
                        ys.append(float(val))
                        pending_x = None
                if xs:
                    contours.append(list(zip(xs, ys)))
            elif etype == "LINE":
                d = {c: float(v) for c, v in codes if c in (10, 20, 11, 21)}
                if all(k in d for k in (10, 20, 11, 21)):
                    contours.append([(d[10], d[20]), (d[11], d[21])])
            elif etype == "CIRCLE":
                d = {c: float(v) for c, v in codes if c in (10, 20, 40)}
                if all(k in d for k in (10, 20, 40)):
                    cx, cy, r = d[10], d[20], d[40]
                    contours.append([
                        (cx + r * math.cos(t), cy + r * math.sin(t))
                        for t in [k * 2 * math.pi / 48 for k in range(48)]
                    ])
            elif etype == "ARC":
                d = {c: float(v) for c, v in codes if c in (10, 20, 40, 50, 51)}
                if all(k in d for k in (10, 20, 40, 50, 51)):
                    cx, cy, r, a0, a1 = d[10], d[20], d[40], math.radians(d[50]), math.radians(d[51])
                    if a1 < a0:
                        a1 += 2 * math.pi
                    steps = max(2, int(48 * (a1 - a0) / (2 * math.pi)))
                    contours.append([
                        (cx + r * math.cos(a0 + (a1 - a0) * k / steps),
                         cy + r * math.sin(a0 + (a1 - a0) * k / steps))
                        for k in range(steps + 1)
                    ])
            i = j
        else:
            i += 1
    return contours


# ---------------------------------------------------------------------------
# 2. Geometry helpers -- all real measurements derived from the parsed
#    contours themselves, never invented.
# ---------------------------------------------------------------------------

def polygon_area(pts):
    """Signed shoelace area (>0 = counter-clockwise)."""
    n = len(pts)
    a = 0.0
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return a / 2.0


def bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def bbox_of_contours(contours):
    xs0, ys0, xs1, ys1 = [], [], [], []
    for c in contours:
        x0, y0, x1, y1 = bbox(c)
        xs0.append(x0); ys0.append(y0); xs1.append(x1); ys1.append(y1)
    return min(xs0), min(ys0), max(xs1), max(ys1)


def circle_fit(pts, tol_frac=0.03):
    """If `pts` is well-approximated by a circle (every vertex within
    tol_frac of the mean radius from the centroid), return (cx, cy, r);
    else None. A real geometric check on the parsed data, not a guess."""
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    radii = [math.hypot(p[0] - cx, p[1] - cy) for p in pts]
    r_mean = sum(radii) / len(radii)
    if r_mean < 1e-6:
        return None
    if max(abs(r - r_mean) for r in radii) / r_mean > tol_frac:
        return None
    if len(pts) < 10:
        return None  # a true circle projects to a many-vertex polygon; a
        # low vertex count "circle-ish" shape is more likely a real
        # polygonal feature (e.g. a hex nut boss), not a bored hole.
    return cx, cy, r_mean


def classify_contours(contours):
    """Largest-|area| contour = outer boundary; the rest = holes/features."""
    if not contours:
        return None, []
    areas = [abs(polygon_area(c)) for c in contours]
    outer_idx = areas.index(max(areas))
    outer = contours[outer_idx]
    holes = [c for i, c in enumerate(contours) if i != outer_idx]
    return outer, holes


# ---------------------------------------------------------------------------
# 3. Drafting-sheet rendering (matplotlib).
# ---------------------------------------------------------------------------

SHEET_W_MM = 297.0   # A4 landscape, mm
SHEET_H_MM = 210.0
MARGIN_MM = 10.0
TITLE_BLOCK_W_MM = 100.0
TITLE_BLOCK_H_MM = 42.0


def add_dimension(ax, p0, p1, offset, text, extension=6.0, fontsize=8):
    """Draws a simple linear dimension: extension lines from p0/p1 out to
    an offset dimension line, arrowheads, and a centered text label --
    standard drafting-sheet convention, kept minimal (no witness-line
    gaps/tick style options), oriented horizontally or vertically only
    (matches this generator's own axis-aligned bounding-box dimensions)."""
    x0, y0 = p0
    x1, y1 = p1
    horizontal = abs(y1 - y0) < 1e-9
    if horizontal:
        y_dim = y0 + offset
        ax.add_line(Line2D([x0, x0], [y0, y_dim], color="black", lw=0.6))
        ax.add_line(Line2D([x1, x1], [y1, y_dim], color="black", lw=0.6))
        ax.annotate("", xy=(x1, y_dim), xytext=(x0, y_dim),
                    arrowprops=dict(arrowstyle="<->", color="black", lw=0.8))
        ax.text((x0 + x1) / 2, y_dim + (2.5 if offset > 0 else -2.5), text,
                ha="center", va="bottom" if offset > 0 else "top", fontsize=fontsize)
    else:
        x_dim = x0 + offset
        ax.add_line(Line2D([x0, x_dim], [y0, y0], color="black", lw=0.6))
        ax.add_line(Line2D([x1, x_dim], [y1, y1], color="black", lw=0.6))
        ax.annotate("", xy=(x_dim, y1), xytext=(x_dim, y0),
                    arrowprops=dict(arrowstyle="<->", color="black", lw=0.8))
        ax.text(x_dim + (2.5 if offset > 0 else -2.5), (y0 + y1) / 2, text,
                ha="left" if offset > 0 else "right", va="center", fontsize=fontsize, rotation=90)


def add_leader_callout(ax, anchor, text_pos, text, fontsize=8):
    ax.plot(*anchor, marker="o", markersize=3, color="black")
    ax.annotate(
        text, xy=anchor, xytext=text_pos, fontsize=fontsize,
        arrowprops=dict(arrowstyle="-", color="black", lw=0.7),
        bbox=dict(boxstyle="square,pad=0.35", fc="white", ec="black", lw=0.7),
        ha="left", va="center",
    )


def build_sheet(part_key, contours, meta, out_png, out_pdf=None):
    import textwrap

    outer, holes = classify_contours(contours)
    x0, y0, x1, y1 = bbox_of_contours(contours)
    part_w = x1 - x0
    part_h = y1 - y0

    # --- Auto-detected circular-hole diameter callouts (computed early --
    # the note-line count below needs this to size the notes area) -------
    # De-duplicated: a stepped/skirted part (e.g. containment_cap()) can
    # produce several concentric near-identical-radius contours from its
    # own real geometry (a genuine feature, not a parsing bug), which would
    # otherwise clutter the sheet with near-duplicate callouts a few tenths
    # of a mm apart. Keep only the largest-radius circle per cluster of
    # same-center, within-3%-radius contours.
    raw_circles = []
    for c in holes:
        fit = circle_fit(c)
        if fit:
            raw_circles.append(fit)
    circle_notes = []
    for ccx, ccy, r in sorted(raw_circles, key=lambda f: -f[2]):
        dup = False
        for ex, ey, er in circle_notes:
            if math.hypot(ccx - ex, ccy - ey) < 1.0 and abs(r - er) / er < 0.03:
                dup = True
                break
        if not dup:
            circle_notes.append((ccx, ccy, r))
    # Also check whether the OUTER contour itself is circular (e.g. stand_plate).
    outer_fit = circle_fit(outer) if outer else None

    # --- Fastener/measurement note lines, wrapped up front so the drawing
    # area (below) can reserve exactly the vertical space they need --
    # a real bug hit and fixed while building this: a fixed-size notes
    # strip silently let notes run off the bottom of the sheet for parts
    # with several/long notes (e.g. stand_plate's 3 notes).
    wrap_width = 100
    note_lines = []
    for note in meta.get("fastener_notes", []):
        wrapped = textwrap.wrap(note, wrap_width) or [note]
        for k, line in enumerate(wrapped):
            prefix = "\u2022 " if k == 0 else "  "
            note_lines.append((prefix + line, False))
    if outer_fit:
        wrapped = textwrap.wrap(
            f"Outer boundary measured as a circle, \u2300{2*outer_fit[2]:.1f} (auto-fit from parsed DXF vertices).",
            wrap_width) or []
        for k, line in enumerate(wrapped):
            prefix = "\u2022 " if k == 0 else "  "
            note_lines.append((prefix + line, True))
    line_h_mm = 4.6
    notes_bottom_y = MARGIN_MM + 3  # baseline of the LAST line
    notes_area_h = len(note_lines) * line_h_mm + 4  # +4mm gap above the notes

    fig_w_in = SHEET_W_MM / 25.4
    fig_h_in = SHEET_H_MM / 25.4
    fig, ax = plt.subplots(figsize=(fig_w_in, fig_h_in), dpi=200)
    ax.set_xlim(0, SHEET_W_MM)
    ax.set_ylim(0, SHEET_H_MM)
    ax.set_aspect("equal")
    ax.axis("off")

    # --- Fit the part into the remaining drawing area (compute scale first,
    # so the title block below can display it) --------------------------
    tb_x0 = SHEET_W_MM - MARGIN_MM - TITLE_BLOCK_W_MM
    tb_y0 = MARGIN_MM
    draw_x0 = MARGIN_MM + 6
    draw_x1 = tb_x0 - 30  # leave room for a right-side vertical dimension
    draw_y0 = notes_bottom_y + notes_area_h  # dynamic: clears the notes strip
    draw_y1 = SHEET_H_MM - MARGIN_MM - 10  # leave room for the title text
    avail_w = draw_x1 - draw_x0
    avail_h = draw_y1 - draw_y0

    raw_scale = min(avail_w / part_w, avail_h / part_h) * 0.72  # 0.72: leave room for dimension lines
    nice_scales = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
    scale = max([s for s in nice_scales if s <= raw_scale], default=nice_scales[0])
    meta["scale_text"] = f"{scale:g} : 1 (as printed on this sheet at 25.4px/mm; verify printer scaling before treating as physically 1:1)"

    # --- Drafting border (double frame, standard convention) -----------
    ax.add_patch(Rectangle((2, 2), SHEET_W_MM - 4, SHEET_H_MM - 4,
                            fill=False, lw=1.6, ec="black"))
    ax.add_patch(Rectangle((MARGIN_MM, MARGIN_MM),
                            SHEET_W_MM - 2 * MARGIN_MM, SHEET_H_MM - 2 * MARGIN_MM,
                            fill=False, lw=0.8, ec="black"))

    # --- Title block (bottom-right corner) ------------------------------
    ax.add_patch(Rectangle((tb_x0, tb_y0), TITLE_BLOCK_W_MM, TITLE_BLOCK_H_MM,
                            fill=False, lw=1.0, ec="black"))
    rows = [
        ("PART", meta["part_title"]),
        ("PROJECT", "Bench-IMU-01 (ktanino10/ai-hardware-engineering-team)"),
        ("SOURCE", "bench-imu-01-enclosure.scad -> OpenSCAD projection(cut=false) -> DXF"),
        ("NOTE", "OpenSCAD-source-driven drafting sheet. NOT a Fusion 360 drawing."),
        ("SCALE", meta["scale_text"]),
        ("UNITS", "mm"),
        ("REV / ECO", meta["rev_eco"]),
        ("DATE", str(date.today())),
    ]
    row_h = TITLE_BLOCK_H_MM / len(rows)
    for i, (label, value) in enumerate(rows):
        ry = tb_y0 + TITLE_BLOCK_H_MM - (i + 1) * row_h
        ax.add_line(Line2D([tb_x0, tb_x0 + TITLE_BLOCK_W_MM], [ry, ry], color="black", lw=0.4))
        ax.text(tb_x0 + 1.5, ry + row_h / 2, label, fontsize=5.0, fontweight="bold", va="center")
        ax.text(tb_x0 + 24, ry + row_h / 2, value, fontsize=5.2, va="center")

    cx_part = (x0 + x1) / 2
    cy_part = (y0 + y1) / 2
    cx_draw = (draw_x0 + draw_x1) / 2
    cy_draw = (draw_y0 + draw_y1) / 2

    def T(pt):
        return (cx_draw + (pt[0] - cx_part) * scale, cy_draw + (pt[1] - cy_part) * scale)

    # --- Draw geometry ---------------------------------------------------
    for c in contours:
        tc = [T(p) for p in c]
        xs = [p[0] for p in tc] + [tc[0][0]]
        ys = [p[1] for p in tc] + [tc[0][1]]
        ax.plot(xs, ys, color="black", lw=1.1)

    # --- Overall envelope dimensions (auto-measured from parsed geometry) --
    tx0, ty0 = T((x0, y0))
    tx1, ty1 = T((x1, y1))
    add_dimension(ax, (tx0, ty0 - 10), (tx1, ty0 - 10), 0, f"{part_w:.1f}", fontsize=7)
    add_dimension(ax, (tx1 + 10, ty0), (tx1 + 10, ty1), 0, f"{part_h:.1f}", fontsize=7)

    for idx, (ccx, ccy, r) in enumerate(circle_notes):
        anchor = T((ccx + r, ccy))
        label_pos = (anchor[0] + 14, anchor[1] + 10 + idx * 9)
        add_leader_callout(ax, anchor, label_pos, f"\u2300{2*r:.1f} (measured)", fontsize=6.5)

    # --- Fixed fastener callouts (cross-referenced text, per part), laid
    # out bottom-up from notes_bottom_y (guaranteed on-sheet -- see the
    # dynamic draw_y0 computation above). ---------------------------------
    for i, (line, italic) in enumerate(reversed(note_lines)):
        ax.text(draw_x0, notes_bottom_y + i * line_h_mm, line, fontsize=6.2, va="bottom",
                style="italic" if italic else "normal")

    ax.text(draw_x0, SHEET_H_MM - MARGIN_MM - 3,
            f"{meta['part_title']} \u2014 top-down silhouette projection (projection(cut=false))",
            fontsize=8.5, fontweight="bold", va="top")

    fig.savefig(out_png, bbox_inches=None)
    if out_pdf:
        fig.savefig(out_pdf, bbox_inches=None)
    plt.close(fig)
    print(f"Wrote {out_png}" + (f" and {out_pdf}" if out_pdf else ""))
    print(f"  overall envelope: {part_w:.2f} x {part_h:.2f} mm (measured from parsed DXF)")
    for ccx, ccy, r in circle_notes:
        print(f"  hole: center=({ccx:.2f},{ccy:.2f}) diameter={2*r:.2f}mm (measured)")
    if outer_fit:
        print(f"  outer boundary: circular, diameter={2*outer_fit[2]:.2f}mm (measured)")


PART_META = {
    "stand-plate": {
        "part_title": "STAND PLATE (Piece 4/5) -- stand_plate()",
        "rev_eco": "Rev 4/4.1 -- Design Complete GRANTED (mechanical scope)",
        "fastener_notes": [
            "4x '#6' self-tap, ~2.8mm pilot, bolt circle r=40.0mm -- bearing (stationary plate) mount.",
            "ASSUMPTION (generic bearing-class convention, DS-BRG-007) -- NOT this bearing SKU's own confirmed pattern.",
            "Pilot holes are BLIND (do not pass fully through Z) -- not visible in this outline-only projection; positions shown are computed from bmount_bolt_circle_r/bmount_pilot_dia, not read off this geometry.",
        ],
    },
    "containment-cap": {
        "part_title": "CONTAINMENT CAP (Piece 3/5) -- containment_cap()",
        "rev_eco": "Rev 3 -- Design Complete GRANTED; REQ-403 safety part",
        "fastener_notes": [
            "6x M3 -> Ruthex RX-M3x5.7 brass heat-set insert, bolt circle r=48.0mm. CONFIRMED (insert dimension match).",
            "Safety-relevant joint (REQ-403) -- ACCEPTED-RISK defense-in-depth containment, NOT proven-adequate (validation/open-issues.md MISS-016).",
        ],
    },
    "pcb-lid": {
        "part_title": "PCB LID (Piece 2/5) -- pcb_lid()",
        "rev_eco": "Rev 3 -- Design Complete GRANTED (mechanical scope)",
        "fastener_notes": [
            "4x M2.5 self-tap, 6.0mm long -- PCB lid -> base corner tabs (MH-1..4). CONFIRMED (geometry; tab_positions array).",
            "assembly-instructions.md documents this as 4x, correcting an older dimensional-spec prose figure of '6x' that did not match the modeled geometry -- see assembly-instructions.md Sec 4.1 for that reconciliation.",
        ],
    },
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True, choices=sorted(PART_META.keys()))
    ap.add_argument("--dxf", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--out-pdf", default=None)
    args = ap.parse_args()

    contours = parse_dxf(args.dxf)
    if not contours:
        raise SystemExit(f"No contours parsed from {args.dxf}")
    meta = dict(PART_META[args.part])
    build_sheet(args.part, contours, meta, args.out, args.out_pdf)


if __name__ == "__main__":
    main()
