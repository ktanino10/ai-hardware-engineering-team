import csv
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from cube_sim.model import ROOT, load_config
from cube_sim.runner import run
from cube_sim.scenarios import scenarios
from cube_sim.visualize import read_run, verify_current, video_samples


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "run"
        self.values, self.manifest = run(load_config(), replace(scenarios()["three-wheel"], duration_s=.2),
                                        self.path, config_path=ROOT / "models/reference.json")

    def test_csv_npz_timestamps_and_video_rows_match(self):
        _, recorded = verify_current(self.path)
        with (self.path / "trajectory.csv").open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        np.testing.assert_array_equal([float(row["time_s"]) for row in rows], recorded["time"])
        np.testing.assert_array_equal([float(row["qw"]) for row in rows], recorded["qpos"][:, 3])
        np.testing.assert_array_equal(video_samples(recorded), [0, 4, 8, 12, 16])
        self.assertEqual(self.manifest["rendering"]["status"], "NOT_RUN")

    def test_tampered_output_fails_and_cannot_be_overwritten_as_a_run(self):
        (self.path / "trajectory.csv").write_text("corrupt\n")
        with self.assertRaises(ValueError):
            read_run(self.path)
        with self.assertRaises(FileExistsError):
            run(load_config(), scenarios()["rest"], self.path)

    def test_stale_code_or_model_rejected_but_historical_output_remains_readable(self):
        manifest = json.loads((self.path / "manifest.json").read_text())
        manifest["input_model"]["sha256"] = "0" * 64
        (self.path / "manifest.json").write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            verify_current(self.path)
        read_run(self.path)
        manifest["input_model"] = self.manifest["input_model"]
        manifest["code"][next(iter(manifest["code"]))] = "0" * 64
        (self.path / "manifest.json").write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            verify_current(self.path)

    def test_video_refuses_interpolated_or_missing_timestamps(self):
        self.values["time"][4] += .002
        with self.assertRaises(ValueError):
            video_samples(self.values)


if __name__ == "__main__":
    unittest.main()
