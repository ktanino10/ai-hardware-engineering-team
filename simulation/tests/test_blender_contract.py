import copy
import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

import numpy as np

from cube_sim.model import ROOT

sys.path.insert(0, str(ROOT / "blender"))
from blender_contract import SOURCE_FILES, load_source, sha, validate_provenance
from mesh_contract import cylinder_mesh, verify_mesh
from cube_sim.geometry import annulus_mesh


class BlenderContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "source"
        self.directory.mkdir()
        original = ROOT / "evidence/startup-v3/startup-mechanism-fixture"
        manifest = json.loads((original / "manifest.json").read_text())
        for name in (*manifest["outputs"], "manifest.json"):
            shutil.copyfile(original / name, self.directory / name)

    def test_real_ten_second_source_mapping_validates(self):
        source = load_source(self.directory)
        self.assertEqual(len(source["mapping"]), 250)
        self.assertEqual(source["manifest"]["rendering"]["fps"], 25)
        self.assertEqual(set(source["source_files_sha256"]), set(source["manifest"]["outputs"]))

    def test_changed_canonical_npz_and_model_are_rejected(self):
        for name in ("trajectory.npz", "model.xml"):
            with self.subTest(source=name):
                original = (self.directory / name).read_bytes()
                if name == "trajectory.npz":
                    with np.load(self.directory / name, allow_pickle=False) as archive:
                        values = {key: archive[key].copy() for key in archive.files}
                    values["qpos"][100, 0] += .01
                    np.savez_compressed(self.directory / name, **values)
                else:
                    tree = ET.parse(self.directory / name)
                    tree.getroot().find("option").set("gravity", "0 0 -8.81")
                    tree.write(self.directory / name)
                with self.assertRaisesRegex(ValueError, f"Changed source {name}"):
                    load_source(self.directory)
                (self.directory / name).write_bytes(original)

    def test_bound_output_change_is_rejected_without_a_circular_dependency(self):
        path = self.directory / "plots.png"
        path.write_bytes(path.read_bytes() + b"changed")
        with self.assertRaisesRegex(ValueError, "Changed source plots.png"):
            load_source(self.directory)

    def test_invalid_source_output_path_is_rejected(self):
        manifest = json.loads((self.directory / "manifest.json").read_text())
        manifest["outputs"]["../outside"] = "0" * 64
        (self.directory / "manifest.json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            load_source(self.directory)

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
            validate_provenance(source, {"schema_version": 3,
                                         "contract_sha256": sha(ROOT / "blender/blender_contract.py"),
                                         "source_manifest_sha256": "0" * 64})
        manifest = copy.deepcopy(source["manifest"])
        manifest["rendering"]["fps"] = 100
        (self.directory / "manifest.json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "at least ten seconds"):
            load_source(self.directory)


class MeshContractTests(unittest.TestCase):
    def test_expected_annulus_and_cylinder_pass(self):
        for vertices, faces in (annulus_mesh(.04, .035, .004), cylinder_mesh(.002, .1)):
            self.assertEqual(verify_mesh(vertices, faces, vertices, faces, "fixture"), 0)

    def test_folded_annulus_with_unchanged_radial_bounds_is_rejected(self):
        vertices, faces = annulus_mesh(.04, .035, .004)
        folded = [(x, abs(y), z) for x, y, z in vertices]
        self.assertAlmostEqual(max(np.hypot(x, y) for x, y, z in vertices),
                               max(np.hypot(x, y) for x, y, z in folded))
        with self.assertRaisesRegex(ValueError, "mesh vertex mismatch"):
            verify_mesh(folded, faces, vertices, faces, "folded")

    def test_changed_topology_or_winding_is_rejected(self):
        vertices, faces = annulus_mesh(.04, .035, .004)
        changed = [tuple(reversed(faces[0])), *faces[1:]]
        with self.assertRaisesRegex(ValueError, "topology/winding"):
            verify_mesh(vertices, changed, vertices, faces, "reversed face")


if __name__ == "__main__":
    unittest.main()
