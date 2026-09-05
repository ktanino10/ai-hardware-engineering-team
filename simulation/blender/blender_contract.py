"""Dependency-free source/receipt checks shared by Blender and the encoder."""

import csv
import hashlib
import io
import json
import math
from pathlib import Path
import struct

POSE_COLUMNS = ("x_m", "y_m", "z_m", "qw", "qx", "qy", "qz",
                "wheel_x_rad", "wheel_y_rad", "wheel_z_rad")
SOURCE_FILES = ("input.json", "scenario.json", "model.xml", "trajectory.npz", "trajectory.csv", "video-frames.csv")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_source(directory):
    directory = Path(directory).resolve()
    manifest_bytes = (directory / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    outputs = manifest["outputs"]
    if not isinstance(outputs, dict) or not set(SOURCE_FILES).issubset(outputs):
        raise ValueError("Source run lacks required canonical input/model/state dependencies.")
    actual_hashes = {}
    source_bytes = {}
    for name, expected in outputs.items():
        if not isinstance(name, str) or Path(name).name != name or name in {".", "..", "manifest.json"}:
            raise ValueError("Unsafe or circular source output reference.")
        path = directory / name
        if not path.resolve().is_relative_to(directory):
            raise ValueError("Source output escapes its run directory.")
        content = path.read_bytes()
        actual_hashes[name] = hashlib.sha256(content).hexdigest()
        if expected != actual_hashes[name]:
            raise ValueError(f"Changed source {name}; refusing a stale replay/annotation.")
        if name in SOURCE_FILES:
            source_bytes[name] = content
    rows = list(csv.DictReader(io.StringIO(source_bytes["trajectory.csv"].decode("utf-8"))))
    mapping = list(csv.DictReader(io.StringIO(source_bytes["video-frames.csv"].decode("utf-8"))))
    rendering = manifest["rendering"]
    fps, count = rendering["fps"], rendering["frames"]
    if (not isinstance(fps, (int, float)) or not math.isfinite(fps) or fps <= 0
            or type(count) is not int or count != len(mapping) or count / fps < 10
            or rendering.get("playback_rate", 1) != 1):
        raise ValueError("Expected a real-time source map of at least ten seconds.")
    for frame, entry in enumerate(mapping):
        index = int(entry["sample_index"])
        if int(entry["video_frame"]) != frame or not 0 <= index < len(rows):
            raise ValueError("Invalid video frame/source-row correspondence.")
        row = rows[index]
        timestamp = float(row["time_s"])
        if (not math.isfinite(timestamp) or timestamp != float(entry["time_s"])
                or abs(timestamp - frame / fps) > 1e-8):
            raise ValueError("Source frame timestamp mismatch.")
        pose = [float(row[name]) for name in POSE_COLUMNS]
        speeds = [float(row[f"wheel_{axis}_relative_rad_s"]) for axis in "xyz"]
        if not all(math.isfinite(x) for x in pose + speeds) or abs(sum(x*x for x in pose[3:7]) - 1) > 1e-9:
            raise ValueError("Non-finite recorded pose.")
        if hashlib.sha256(struct.pack("<10d", *pose)).hexdigest() != entry["qpos_float64_le_sha256"]:
            raise ValueError("Source frame pose hash mismatch.")
    return {
        "directory": directory, "manifest": manifest, "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "config": json.loads(source_bytes["input.json"]),
        "scenario": json.loads(source_bytes["scenario.json"]),
        "rows": rows, "mapping": mapping,
        "source_files_sha256": actual_hashes,
    }


def validate_provenance(source, provenance):
    manifest, config = source["manifest"], source["config"]
    expected = {
        "schema_version": 3, "source_manifest_sha256": source["manifest_sha256"],
        "contract_sha256": sha(__file__),
        "source_files_sha256": source["source_files_sha256"],
        "trajectory_csv_sha256": source["source_files_sha256"]["trajectory.csv"],
        "frame_mapping": source["mapping"], "frames": len(source["mapping"]),
        "fps": manifest["rendering"]["fps"], "source_code_revision": manifest["source_revision"],
        "source_code_dirty": manifest["uncommitted_model_code"], "source_code_sha256": manifest["code"],
        "model_case_id": config["case_id"], "input_classification": config["classification"],
        "side_m": config["body"]["side_m"],
        "total_modeled_mass_kg": config["body"]["mass_kg"] + sum(w["mass_kg"] for w in config["wheels"]),
    }
    for key, value in expected.items():
        if provenance.get(key) != value:
            raise ValueError(f"Replay provenance mismatch: {key}")


def validate_encoding(directory, source):
    directory = Path(directory).resolve()
    if directory == source["directory"]:
        raise ValueError("Blender outputs must not overwrite the source run.")
    provenance = json.loads((directory / "provenance.json").read_text())
    validate_provenance(source, provenance)
    check = json.loads((directory / "native-check.json").read_text())
    receipt = json.loads((directory / "render-receipt.json").read_text())
    if check.get("status") != "NATIVE_REOPEN_TRANSFORMS_GEOMETRY_AND_SOURCES_MATCH":
        raise ValueError("A current complete native checker receipt is required.")
    if (check["blend_sha256"] != sha(directory / "replay.blend")
            or check["provenance_sha256"] != sha(directory / "provenance.json")
            or check["source_manifest_sha256"] != source["manifest_sha256"]
            or check["checker_sha256"] != sha(Path(__file__).with_name("check_replay.py"))
            or check["contract_sha256"] != sha(__file__)
            or check["mesh_contract_sha256"] != sha(Path(__file__).with_name("mesh_contract.py"))):
        raise ValueError("Native file/checker/source receipt changed; recheck before encoding.")
    if (receipt["blend_sha256"] != check["blend_sha256"]
            or receipt["source_manifest_sha256"] != source["manifest_sha256"]
            or receipt["provenance_sha256"] != check["provenance_sha256"]
            or receipt["renderer_sha256"] != provenance["renderer_script_sha256"]):
        raise ValueError("Renderer receipt does not describe this native file and source.")
    expected_names = {f"frame_{i:04}.png" for i in range(1, provenance["frames"] + 1)}
    if set(receipt["frame_sha256"]) != expected_names:
        raise ValueError("Incomplete or unexpected rendered frame set.")
    for name, digest in receipt["frame_sha256"].items():
        if sha(directory / "frames" / name) != digest:
            raise ValueError(f"Changed rendered image: {name}")
    return provenance, receipt
