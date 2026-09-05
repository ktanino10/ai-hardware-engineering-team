"""Label Blender-rendered PNGs using the original computed timestamps."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(Path(__file__).resolve().parent))
from blender_contract import load_source, validate_encoding


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--render", type=Path, required=True)
    args = parser.parse_args()
    source = load_source(args.run)
    provenance, _ = validate_encoding(args.render, source)
    rows, scenario = source["rows"], source["scenario"]
    font, small = ImageFont.load_default(size=19), ImageFont.load_default(size=15)
    output = args.render / "blender-motion.mp4"
    command = ["ffmpeg", "-v", "error", "-n", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", "960x720", "-r", str(provenance["fps"]), "-i", "-", "-an", "-c:v", "libx264",
               "-crf", "21", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output)]
    frame_hashes = {}
    with subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE) as encoder:
        for i, entry in enumerate(provenance["frame_mapping"], start=1):
            path = args.render / "frames" / f"frame_{i:04}.png"
            row = rows[int(entry["sample_index"])]
            frame_hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
            with Image.open(path) as raw:
                image = Image.new("RGB", (960, 720), (16, 33, 46))
                image.paste(raw.convert("RGB"), (0, 100))
            draw = ImageDraw.Draw(image)
            draw.text((20, 10), f"BLENDER {provenance['blender']} | WIP | {provenance['input_classification']}",
                      font=font, fill="#ffd08c")
            draw.text((20, 38), f"{provenance['model_case_id']} | {provenance['side_m']*1000:g} mm / {provenance['total_modeled_mass_kg']:.3f} kg",
                      font=small, fill="white")
            draw.text((20, 60), "NOT a Blender physics simulation. NOT hardware approval or Fusion assembly evidence.",
                      font=small, fill="#ffb1a1")
            code_label = provenance["source_code_revision"][:12] + ("+dirty" if provenance["source_code_dirty"] else "")
            draw.text((20, 80), f"MuJoCo source code {code_label} | {provenance['engine']}",
                      font=small, fill="#c4dce8")
            draw.text((20, 635), f"Recorded t={float(entry['time_s']):.3f} s | source row {entry['sample_index']}",
                      font=font, fill="white")
            speed = " / ".join(f"{float(row[f'wheel_{axis}_relative_rad_s']):+.1f}" for axis in "xyz")
            draw.text((20, 665), f"X red / Y green / Z blue relative wheel speed [rad/s]: {speed}",
                      font=small, fill="#c4dce8")
            draw.text((20, 692), "Calculated poses only; no hand-authored success motion. Wheel markers can alias at video frame rate.",
                      font=small, fill="#c4dce8")
            if int(entry["sample_index"]) == provenance["poster_sample_index"]:
                image.save(args.render / "preview.png")
            encoder.stdin.write(image.tobytes())
        encoder.stdin.close()
        error = encoder.stderr.read().decode()
        if encoder.wait() != 0:
            raise RuntimeError(error)
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(output), "-f", "null", "-"], check=True)
    record = {"state": "WIP_BLENDER_RENDER_OF_MUJOCO_STATES", "blender_physics": False,
              "frames": provenance["frames"], "fps": provenance["fps"],
              "duration_s": provenance["frames"] / provenance["fps"],
              "source_manifest_sha256": provenance["source_manifest_sha256"],
              "encoder_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "contract_sha256": hashlib.sha256(Path(__file__).with_name("blender_contract.py").read_bytes()).hexdigest(),
              "source_files_sha256": source["source_files_sha256"],
              "raw_frame_sha256": frame_hashes,
              "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(args.render.iterdir())
                        if p.is_file() and p.name != "manifest.json"}}
    (args.render / "manifest.json").write_text(json.dumps(record, indent=2) + "\n")
    print(str(output.resolve()))


if __name__ == "__main__":
    main()
