#!/usr/bin/env python3
"""
Bench-IMU-01 -- Physics-demo frame annotation post-process (Pillow).

Takes the raw Blender-rendered frame sequence from
`build_physics_demo_animation.py` (no text at all -- pure 3D render) and
produces the final numbered sequence ffmpeg encodes, by:

1. Prepending a text-only TITLE CARD (a few seconds) stating plainly that
   this is a SIMULATION/PREDICTION, not measured data.
2. Overlaying a PERSISTENT corner watermark ("SIMULATION -- PREDICTION,
   NOT MEASURED DATA") on every single 3D-rendered frame -- always on,
   never just at the start, per this task's own explicit requirement.
3. Overlaying a per-stage caption box with the REAL numbers (verbatim from
   `bom/component-selection.md`'s own already-approved table -- nothing
   recomputed here besides simple RPM/rad-s/deg-s unit restatement that
   already matches that table's own figures): I_wheel, I_platform, the
   ratio, and each stage's omega_wheel/omega_platform.
4. Appending a text-only OUTRO CARD stating the future real-hardware
   test's success criteria (verbatim, matching the request that produced
   this animation) -- so the "success looks like this" bar is explicit,
   not left implicit.

Run standalone (no Blender needed for this step -- pure PIL):

    python3 annotate_physics_demo_frames.py

Then encode with ffmpeg (2-pass MP4 + palette GIF, same technique as
`../animation/build_assembly_animation.py`'s own header):

    ffmpeg -y -framerate 24 -i "final/f_%04d.png" \\
      -c:v libx264 -pix_fmt yuv420p -crf 20 -movflags +faststart \\
      bench-imu-01-momentum-conservation-SIMULATION.mp4
    ffmpeg -y -framerate 24 -i "final/f_%04d.png" \\
      -vf "fps=12,scale=800:-1:flags=lanczos,palettegen=stats_mode=diff" \\
      /tmp/physics-palette.png
    ffmpeg -y -framerate 24 -i "final/f_%04d.png" -i /tmp/physics-palette.png \\
      -filter_complex "fps=12,scale=800:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3" \\
      -loop 0 bench-imu-01-momentum-conservation-SIMULATION.gif
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

RAW_DIR = "/tmp/physics-demo-frames/raw"
FINAL_DIR = "/tmp/physics-demo-frames/final"
FPS = 24
RES = (1280, 960)

FONT_DIR = "/System/Library/Fonts/Supplemental"
FONT_REGULAR = f"{FONT_DIR}/Arial.ttf"
FONT_BOLD = f"{FONT_DIR}/Arial Bold.ttf"

# --- Real physics, restated (must match build_physics_demo_animation.py
# exactly -- both files derive from the same bom/component-selection.md
# source numbers). ----------------------------------------------------------
I_WHEEL = 4.5e-5
I_PLATFORM = 6.9e-4
RATIO = I_WHEEL / I_PLATFORM


def rpm_to_rads(rpm):
    return rpm * 2 * math.pi / 60.0


OMEGA_WHEEL_1 = rpm_to_rads(30)
OMEGA_PLATFORM_1 = RATIO * OMEGA_WHEEL_1
OMEGA_WHEEL_2 = rpm_to_rads(300)
OMEGA_PLATFORM_2 = RATIO * OMEGA_WHEEL_2

# --- Timeline (must match build_physics_demo_animation.py's own TIMELINE) --
def f(t_seconds):
    return 1 + round(t_seconds * FPS)

FRAME_STAGE1_START = f(0.0)
FRAME_STAGE1_END = f(4.0)
FRAME_PAUSE_END = f(5.0)
FRAME_STAGE2_END = f(9.0)
FRAME_OUTRO_END = f(12.0)

TITLE_CARD_FRAMES = 48   # 2s
OUTRO_CARD_FRAMES = 96   # 4s (success-criteria text needs time to read)

WATERMARK_TEXT = "SIMULATION \u2014 PREDICTION, NOT MEASURED DATA"


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def text_card(lines, bg=(18, 22, 30), title=False):
    im = Image.new("RGB", RES, bg)
    d = ImageDraw.Draw(im)
    y = RES[1] * 0.18
    for text, size, bold, color in lines:
        font = load_font(FONT_BOLD if bold else FONT_REGULAR, size)
        bbox = d.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        d.text(((RES[0] - w) / 2, y), text, font=font, fill=color)
        y += (bbox[3] - bbox[1]) + size * 0.55
    return im


def build_title_card():
    return text_card([
        ("Bench-IMU-01", 40, True, (230, 230, 235)),
        ("Angular-Momentum Conservation", 34, True, (230, 230, 235)),
        ("SIMULATION \u2014 PREDICTION, NOT MEASURED DATA", 26, True, (255, 140, 60)),
        ("", 10, False, (0, 0, 0)),
        ("No PCB has been fabricated/populated yet; no firmware has been", 18, False, (190, 190, 195)),
        ("flashed to real hardware. Every number below is copied from the", 18, False, (190, 190, 195)),
        ("already-approved ESTIMATE in bom/component-selection.md.", 18, False, (190, 190, 195)),
        ("", 10, False, (0, 0, 0)),
        (f"I_wheel = {I_WHEEL:.2e} kg\u00b7m\u00b2      I_platform \u2248 {I_PLATFORM:.2e} kg\u00b7m\u00b2      ratio \u2248 1:{1/RATIO:.0f}", 20, False, (210, 210, 215)),
    ])


def build_outro_card():
    return text_card([
        ("Future real-hardware test \u2014 success criteria", 32, True, (230, 230, 235)),
        ("(this animation is a PREDICTION; none of this has been measured yet)", 20, True, (255, 140, 60)),
        ("", 8, False, (0, 0, 0)),
        ("1. Platform rotates OPPOSITE the wheel (action/reaction polarity check).", 19, False, (210, 210, 215)),
        ("2. Measured rate ratio is within a reasonable tolerance of the", 19, False, (210, 210, 215)),
        ("   predicted 1:15, confirmed across multiple speeds (linearity check).", 19, False, (210, 210, 215)),
        ("3. Onboard IMU's measured platform rate matches the predicted rate", 19, False, (210, 210, 215)),
        ("   (also validates the sensor itself).", 19, False, (210, 210, 215)),
        ("4. Repeatable across multiple trials.", 19, False, (210, 210, 215)),
        ("", 8, False, (0, 0, 0)),
        ("Bench-IMU-01 \u2014 ktanino10/ai-hardware-engineering-team", 16, False, (140, 140, 145)),
    ], bg=(18, 22, 30))


def stage_caption_lines(frame_idx):
    """Returns (caption_lines, box_color) for the numeric caption box, or
    None if no stage caption applies (title/outro cards handle their own
    text)."""
    if FRAME_STAGE1_START <= frame_idx < FRAME_PAUSE_END:
        stage_no, rpm, ow, op, deg = 1, 30, OMEGA_WHEEL_1, OMEGA_PLATFORM_1, "\u224812\u00b0/s"
        note = "(wheel shown at true real-time rate)"
    else:
        stage_no, rpm, ow, op, deg = 2, 300, OMEGA_WHEEL_2, OMEGA_PLATFORM_2, "\u2248117\u00b0/s"
        note = "(wheel visual spin STYLIZED \u2014 true 1800\u00b0/s would alias at 24fps; platform rate IS real-time)"
    lines = [
        f"STAGE {stage_no}: wheel commanded to {rpm} RPM ({ow:.2f} rad/s)",
        f"predicted platform rate: {op:.3f} rad/s ({deg})  \u2014  ratio {RATIO:.4f} (\u22481:{1/RATIO:.0f})",
        note,
    ]
    return lines


def draw_watermark(draw):
    font = load_font(FONT_BOLD, 20)
    bbox = draw.textbbox((0, 0), WATERMARK_TEXT, font=font)
    w = bbox[2] - bbox[0]
    pad = 10
    x0, y0 = RES[0] - w - 2 * pad - 14, 14
    x1, y1 = RES[0] - 14, 14 + (bbox[3] - bbox[1]) + 2 * pad
    draw.rectangle([x0, y0, x1, y1], fill=(255, 255, 255, 235), outline=(200, 60, 20), width=2)
    draw.text((x0 + pad, y0 + pad - 2), WATERMARK_TEXT, font=font, fill=(180, 40, 10))


def draw_caption_box(draw, lines):
    font = load_font(FONT_REGULAR, 20)
    font_bold = load_font(FONT_BOLD, 20)
    pad = 12
    line_h = 26
    box_w = max(draw.textlength(l, font=font) for l in lines) + 2 * pad
    box_h = len(lines) * line_h + 2 * pad
    x0, y0 = 14, RES[1] - box_h - 14
    draw.rectangle([x0, y0, x0 + box_w, y0 + box_h], fill=(255, 255, 255, 230), outline=(20, 20, 20), width=2)
    for i, line in enumerate(lines):
        draw.text((x0 + pad, y0 + pad + i * line_h), line, font=font_bold if i == 0 else font, fill=(20, 20, 20))


def annotate_raw_frame(path, frame_idx):
    im = Image.open(path).convert("RGB")
    draw = ImageDraw.Draw(im)
    draw_watermark(draw)
    lines = stage_caption_lines(frame_idx)
    if lines:
        draw_caption_box(draw, lines)
    return im


def main():
    os.makedirs(FINAL_DIR, exist_ok=True)
    out_idx = 1

    title = build_title_card()
    for _ in range(TITLE_CARD_FRAMES):
        title.save(f"{FINAL_DIR}/f_{out_idx:04d}.png")
        out_idx += 1

    raw_files = sorted(f for f in os.listdir(RAW_DIR) if f.startswith("f_"))
    for fname in raw_files:
        frame_idx = int(fname[2:6])
        im = annotate_raw_frame(os.path.join(RAW_DIR, fname), frame_idx)
        im.save(f"{FINAL_DIR}/f_{out_idx:04d}.png")
        out_idx += 1

    outro = build_outro_card()
    for _ in range(OUTRO_CARD_FRAMES):
        outro.save(f"{FINAL_DIR}/f_{out_idx:04d}.png")
        out_idx += 1

    print(f"Wrote {out_idx - 1} final frames to {FINAL_DIR}")
    print(f"  Title card: frames 1-{TITLE_CARD_FRAMES}")
    print(f"  Animation:  frames {TITLE_CARD_FRAMES+1}-{TITLE_CARD_FRAMES+len(raw_files)}")
    print(f"  Outro card: frames {TITLE_CARD_FRAMES+len(raw_files)+1}-{out_idx-1}")


if __name__ == "__main__":
    main()
