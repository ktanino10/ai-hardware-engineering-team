#!/usr/bin/env python3
"""
Bench-IMU-01 -- CONCEPT attitude-hold demo frame annotation post-process
(Pillow).

Same pipeline shape as
`../physics-demo/annotate_physics_demo_frames.py`, but with CONCEPT
(not SIMULATION) framing throughout, per this task's own explicit
requirement: a CONCEPT title card at the start, a PERSISTENT on-screen
watermark for the *entire* runtime (not just the start), and `CONCEPT` in
the output filename itself.

Run standalone (no Blender needed for this step):

    python3 annotate_concept_demo_frames.py

Then encode with ffmpeg (same 2-pass MP4 + palette-GIF technique as
`../animation/build_assembly_animation.py`'s own header):

    ffmpeg -y -framerate 24 -i "final/f_%04d.png" \\
      -c:v libx264 -pix_fmt yuv420p -crf 20 -movflags +faststart \\
      bench-imu-01-attitude-hold-CONCEPT.mp4
    ffmpeg -y -framerate 24 -i "final/f_%04d.png" \\
      -vf "fps=12,scale=800:-1:flags=lanczos,palettegen=stats_mode=diff" \\
      /tmp/concept-palette.png
    ffmpeg -y -framerate 24 -i "final/f_%04d.png" -i /tmp/concept-palette.png \\
      -filter_complex "fps=12,scale=800:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3" \\
      -loop 0 bench-imu-01-attitude-hold-CONCEPT.gif
"""

import os

from PIL import Image, ImageDraw, ImageFont

RAW_DIR = "/tmp/concept-demo-frames/raw"
FINAL_DIR = "/tmp/concept-demo-frames/final"
FPS = 24
RES = (1280, 960)

FONT_DIR = "/System/Library/Fonts/Supplemental"
FONT_REGULAR = f"{FONT_DIR}/Arial.ttf"
FONT_BOLD = f"{FONT_DIR}/Arial Bold.ttf"

# --- Timeline (must match build_concept_attitude_hold_animation.py's own
# TIMELINE) -------------------------------------------------------------
def f(t_seconds):
    return 1 + round(t_seconds * FPS)

FRAME_REF_HOLD_END = f(1.5)
FRAME_DISTURB_END = f(3.0)
FRAME_DISTURBED_HOLD_END = f(4.0)
FRAME_CORRECTION_END = f(7.0)
FRAME_FINAL_HOLD_END = f(9.0)

TITLE_CARD_FRAMES = 60   # 2.5s -- a bit longer, more to read/disclose than the physics demo's title
OUTRO_CARD_FRAMES = 84   # 3.5s

WATERMARK_TEXT = "CONCEPT \u2014 NOT A LITERAL CAPABILITY OF THIS RIG"


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def text_card(lines, bg=(18, 22, 30)):
    im = Image.new("RGB", RES, bg)
    d = ImageDraw.Draw(im)
    y = RES[1] * 0.14
    for text, size, bold, color in lines:
        font = load_font(FONT_BOLD if bold else FONT_REGULAR, size)
        bbox = d.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        d.text(((RES[0] - w) / 2, y), text, font=font, fill=color)
        y += (bbox[3] - bbox[1]) + size * 0.55
    return im


def build_title_card():
    return text_card([
        ("Bench-IMU-01", 38, True, (230, 230, 235)),
        ("Reference-Attitude Hold \u2014 CONCEPT DEMONSTRATION", 30, True, (230, 230, 235)),
        ("CONCEPT \u2014 NOT A LITERAL CAPABILITY OF THIS RIG", 25, True, (255, 140, 60)),
        ("", 8, False, (0, 0, 0)),
        ("This rig rotates about exactly ONE (vertical/yaw) axis (REQ-011)", 18, False, (190, 190, 195)),
        ("\u2014 there is no pitch/roll d.o.f., so literal \"inversion\" is physically", 18, False, (190, 190, 195)),
        ("impossible on this hardware. Reinterpreted here as: a deviation", 18, False, (190, 190, 195)),
        ("from a REFERENCE ATTITUDE, corrected by the reaction wheel.", 18, False, (190, 190, 195)),
        ("", 8, False, (0, 0, 0)),
        ("Also IDEALIZED, not a specific control-law's simulated response \u2014", 18, False, (190, 190, 195)),
        ("no closed-loop controller is implemented anywhere in this project", 18, False, (190, 190, 195)),
        ("(REQ-009/REQ-014). Green mark = fixed reference attitude; the", 18, False, (190, 190, 195)),
        ("witness tab on the rotating base is rotation_index_pointer().", 18, False, (190, 190, 195)),
    ])


def build_outro_card():
    return text_card([
        ("What this CONCEPT demo does NOT claim", 30, True, (230, 230, 235)),
        ("", 8, False, (0, 0, 0)),
        ("- Does NOT show literal inversion/tumble recovery (impossible on", 18, False, (210, 210, 215)),
        ("  this single-axis rig).", 18, False, (210, 210, 215)),
        ("- Does NOT represent a specific implemented control law -- no", 18, False, (210, 210, 215)),
        ("  closed-loop attitude controller exists in this project yet.", 18, False, (210, 210, 215)),
        ("- The disturbance is external (not caused by the reaction wheel);", 18, False, (210, 210, 215)),
        ("  the wheel's spin-up/spin-down shape is an idealized ease curve,", 18, False, (210, 210, 215)),
        ("  not a measured or simulated response of any real controller.", 18, False, (210, 210, 215)),
        ("", 8, False, (0, 0, 0)),
        ("Bench-IMU-01 \u2014 ktanino10/ai-hardware-engineering-team", 16, False, (140, 140, 145)),
    ])


def stage_caption(frame_idx):
    if frame_idx < FRAME_REF_HOLD_END:
        return "REFERENCE ATTITUDE \u2014 pointer aligned with the fixed mark"
    elif frame_idx < FRAME_DISTURB_END:
        return "EXTERNAL DISTURBANCE (not caused by the reaction wheel) \u2014 platform nudged off reference"
    elif frame_idx < FRAME_DISTURBED_HOLD_END:
        return "OFF REFERENCE \u2014 pointer visibly misaligned from the fixed mark"
    elif frame_idx < FRAME_CORRECTION_END:
        return "CORRECTING \u2014 reaction wheel spins up, platform returns toward reference (idealized ease, not a specific control law)"
    else:
        return "HOLDING REFERENCE \u2014 pointer re-aligned with the fixed mark"


def draw_watermark(draw):
    font = load_font(FONT_BOLD, 19)
    bbox = draw.textbbox((0, 0), WATERMARK_TEXT, font=font)
    w = bbox[2] - bbox[0]
    pad = 10
    x0, y0 = RES[0] - w - 2 * pad - 14, 14
    x1, y1 = RES[0] - 14, 14 + (bbox[3] - bbox[1]) + 2 * pad
    draw.rectangle([x0, y0, x1, y1], fill=(255, 255, 255, 235), outline=(60, 130, 20), width=2)
    draw.text((x0 + pad, y0 + pad - 2), WATERMARK_TEXT, font=font, fill=(40, 110, 10))


def draw_caption_box(draw, text):
    font = load_font(FONT_BOLD, 19)
    pad = 12
    box_w = draw.textlength(text, font=font) + 2 * pad
    box_h = 19 + 2 * pad + 6
    x0, y0 = 14, RES[1] - box_h - 14
    draw.rectangle([x0, y0, x0 + box_w, y0 + box_h], fill=(255, 255, 255, 230), outline=(20, 20, 20), width=2)
    draw.text((x0 + pad, y0 + pad), text, font=font, fill=(20, 20, 20))


def annotate_raw_frame(path, frame_idx):
    im = Image.open(path).convert("RGB")
    draw = ImageDraw.Draw(im)
    draw_watermark(draw)
    draw_caption_box(draw, stage_caption(frame_idx))
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
