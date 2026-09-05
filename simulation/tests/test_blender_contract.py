import copy
import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from cube_sim.model import ROOT

sys.path.insert(0, str(ROOT / "blender"))
from blender_contract import SOURCE_FILES, load_source, sha, validate_provenance


class BlenderContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "source"
        self.directory.mkdir()
        original = ROOT / "evidence/startup-v3/startup-mechanism-fixture"
        for name in (*SOURCE_FILES, "manifest.json"):
            shutil.copyfile(original / name, self.directory / name)

    def test_real_ten_second_source_mapping_validates(self):
        source = load_source(self.directory)
        self.assertEqual(len(source["mapping"]), 250)
        self.assertEqual(source["manifest"]["rendering"]["fps"], 25)

    def test_changed_csv_is_rejected_before_encoder_creates_any_output(self):
        path = self.directory / "trajectory.csv"
        with path.open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        for row in rows:
            row["wheel_x_relative_rad_s"] = "12345"
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        output = Path(self.temp.name) / "render"
        output.mkdir()
        result = subprocess.run([sys.executable, str(ROOT / "blender/encode_replay.py"),
                                 "--run", str(self.directory), "--render", str(output)],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Changed source trajectory.csv", result.stderr)
        self.assertEqual(list(output.iterdir()), [])

    def test_rehashed_bad_frame_map_still_fails_correspondence(self):
        path = self.directory / "video-frames.csv"
        with path.open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        rows[0]["sample_index"] = "1"
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        manifest = json.loads((self.directory / "manifest.json").read_text())
        manifest["outputs"]["video-frames.csv"] = sha(path)
        (self.directory / "manifest.json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "timestamp mismatch"):
            load_source(self.directory)

    def test_bad_fps_and_stale_provenance_fail_closed(self):
        source = load_source(self.directory)
        with self.assertRaisesRegex(ValueError, "provenance mismatch"):
            validate_provenance(source, {"schema_version": 1})
        with self.assertRaisesRegex(ValueError, "source_manifest_sha256"):
            validate_provenance(source, {"schema_version": 2,
                                         "contract_sha256": sha(ROOT / "blender/blender_contract.py"),
                                         "source_manifest_sha256": "0" * 64})
        manifest = copy.deepcopy(source["manifest"])
        manifest["rendering"]["fps"] = 100
        (self.directory / "manifest.json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "at least ten seconds"):
            load_source(self.directory)


if __name__ == "__main__":
    unittest.main()
