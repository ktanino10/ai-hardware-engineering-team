import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from simulation.imu_disagreement.report import analyze
from simulation.imu_estimation.estimator import Estimator
from simulation.imu_estimation.schema import InputError


FIXTURE = Path("docs/rev5-six-imu-fault-study-2026-09-13/author/run-001/one-bias")


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((FIXTURE / "config.json").read_text())
        with (FIXTURE / "samples.jsonl").open("rb") as source:
            self.first = json.loads(next(source))

    def batch(self, k=0, rates=None, ids=None):
        batch = copy.deepcopy(self.first)
        batch["t_s"] = k / 100
        for i, row in enumerate(batch["samples"]):
            sensor = self.config["sensors"][i]
            clock = sensor["clock"]
            row.update(seq=k, t_local_s=(k / 100 - clock["offset_s"]) / clock["scale"])
            z = 0 if rates is None else rates[i]
            # Independent component expression for R_BS^T * (0,0,z).
            row["gyro"] = [sensor["R_BS"][2][axis] * z for axis in range(3)]
        if ids is not None:
            batch["samples"] = [r for r in batch["samples"] if r["id"] in ids]
        return batch

    def report(self, *batches):
        raw = b"".join(json.dumps(b).encode() + b"\n" for b in batches)
        return analyze(self.config, io.BytesIO(raw))

    def test_reuses_exact_original_results_and_preserves_inputs(self):
        batches = [self.batch(0), self.batch(1, [.12, 0, 0, 0, 0, 0])]
        original = copy.deepcopy(batches)
        config_before = copy.deepcopy(self.config)
        baseline = Estimator(self.config)
        expected = [baseline.step(b) for b in batches]
        report = self.report(*batches)
        for row, old in zip(report["records"], expected):
            self.assertEqual(row["gyro_mean_B_rad_s"], old["omega_B_rad_s"])
            self.assertEqual(row["gyro_spread_rad_s"], old["gyro_spread_rad_s"])
            self.assertEqual(row["accepted_ids"], old["accepted_ids"])
            self.assertEqual(row["rejected"], old["rejected"])
            self.assertEqual(row["upstream_status_not_health"], old["status"])
            self.assertNotIn("q_WB", row)
        self.assertEqual(batches, original)
        self.assertEqual(self.config, config_before)

    def test_signed_frames_and_residuals(self):
        row = self.report(self.batch(rates=[.12, 0, 0, 0, 0, 0]))["records"][0]
        self.assertAlmostEqual(row["gyro_mean_B_rad_s"][2], .02)
        self.assertAlmostEqual(row["gyro_spread_rad_s"], .1)
        self.assertAlmostEqual(row["residuals"]["imu0"]["vector_B_rad_s"][2], .1)
        self.assertAlmostEqual(row["residuals"]["imu5"]["vector_B_rad_s"][2], -.02)
        # Move the same body fault to a rotated sensor, without changing magnitude.
        rotated = self.report(self.batch(rates=[0, 0, 0, 0, 0, .12]))["records"][0]
        self.assertEqual(row["gyro_spread_rad_s"], rotated["gyro_spread_rad_s"])

    def test_shared_bias_and_split_have_no_health_claim(self):
        common = self.report(self.batch(rates=[.02] * 6))
        split = self.report(self.batch(rates=[.12] * 3 + [-.12] * 3))
        self.assertEqual(common["records"][0]["gyro_spread_rad_s"], 0)
        self.assertAlmostEqual(split["records"][0]["gyro_spread_rad_s"], .12)
        self.assertEqual(split["records"][0]["gyro_mean_B_rad_s"], [0, 0, 0])
        self.assertTrue(any("Shared bias" in text for text in common["limits"]))
        self.assertTrue(any("3vs3" in text for text in split["limits"]))

    def test_spread_is_euclidean_not_axis_range(self):
        b = self.batch(ids=["imu0", "imu5"])
        r = self.config["sensors"][5]["R_BS"]
        b["samples"][1]["gyro"] = [
            sum(r[j][i] * [2., 4., 6.][j] for j in range(3)) for i in range(3)]
        row = self.report(b)["records"][0]
        self.assertEqual(row["gyro_mean_B_rad_s"], [1., 2., 3.])
        self.assertAlmostEqual(row["gyro_spread_rad_s"], 14 ** .5)
        self.assertEqual(row["residuals"]["imu5"]["vector_B_rad_s"], [1., 2., 3.])
        self.assertAlmostEqual(row["residuals"]["imu0"]["norm_rad_s"], 14 ** .5)

    def test_singleton_and_zero_never_agreement(self):
        report = self.report(self.batch(ids=["imu5"]), self.batch(1, ids=[]),
                             self.batch(2))
        one, zero, latched = report["records"]
        self.assertEqual(one["accepted_count"], 1)
        self.assertEqual(one["gyro_mean_B_rad_s"], [0, 0, 0])
        self.assertIsNone(one["gyro_spread_rad_s"])
        self.assertIsNone(one["residuals"])
        for row in (zero, latched):
            self.assertIsNone(row["gyro_mean_B_rad_s"])
            self.assertIsNone(row["gyro_spread_rad_s"])
            self.assertEqual(row["comparison"], "UNRESOLVED")
        self.assertIsNone(report["summary"]["comparable_spread_mean_rad_s"])
        self.assertEqual(latched["absent_ids"], [])
        self.assertEqual(len(latched["rejected"]), 6)

    def test_presence_distinct_from_stale_rejection_duplicate(self):
        b = self.batch(1)
        b["samples"][0]["t_local_s"] -= .005
        b["samples"].pop(1)
        b["samples"].append(copy.deepcopy(b["samples"][1]))
        row = self.report(self.batch(), b)["records"][1]
        self.assertEqual(row["absent_ids"], ["imu1"])
        self.assertIn("imu0", row["input_present_ids_unvalidated"])
        self.assertNotIn("imu0", row["accepted_ids"])
        reasons = [r["reason"] for r in row["rejected"]]
        self.assertIn("stale", reasons)
        self.assertIn("duplicate_sensor", reasons)
        self.assertEqual(row["accepted_count"], 4)

    def test_clock_reset_and_nonmonotonic_batch(self):
        b = self.batch(1)
        b["samples"][0]["epoch"] = "new"
        rows = self.report(self.batch(), b, self.batch(2), self.batch(1))["records"]
        self.assertIn("clock_reset", [r["reason"] for r in rows[1]["rejected"]])
        self.assertIn("clock_quarantined", [r["reason"] for r in rows[2]["rejected"]])
        self.assertEqual(rows[3]["comparison"], "UNRESOLVED")
        self.assertEqual(rows[3]["t_s_input_label"], .01)

    def test_gap_not_interpolated(self):
        rows = self.report(self.batch(), self.batch(4), self.batch(5))["records"]
        self.assertEqual(rows[1]["comparison"], "UNRESOLVED")
        self.assertEqual(rows[2]["comparison"], "UNRESOLVED")
        self.assertIn("integration_gap", rows[1]["upstream_reasons"])

    def test_malformed_utf8_preserves_prefix_and_latches(self):
        first = json.dumps(self.batch()).encode() + b"\n"
        raw = first + b"\xff\n" + json.dumps(self.batch(2)).encode() + b"\n"
        report = analyze(self.config, io.BytesIO(raw))
        self.assertEqual(report["records"][0], analyze(self.config, [first])["records"][0])
        self.assertIsNone(report["records"][1]["absent_ids"])
        self.assertIsNone(report["records"][1]["t_s_input_label"])
        self.assertEqual(report["records"][2]["comparison"], "UNRESOLVED")
        self.assertEqual(report["summary"]["unknown_presence_records"], 1)

    def test_empty_and_malformed_json_nonfinite(self):
        self.assertEqual(analyze(self.config, [])["errors"], ["empty_stream"])
        for line in (b'{"a":NaN}\n', b"{}\n", b"not-json\n"):
            with self.subTest(line=line):
                report = analyze(self.config, [line])
                self.assertEqual(report["records"][0]["comparison"], "UNRESOLVED")
                self.assertIsNone(report["summary"]["comparable_spread_max_rad_s"])

    def test_unsupported_input_contract_refused(self):
        edits = [
            lambda c: c["units"].update(gyro="deg/s"),
            lambda c: c.update(frames="UNKNOWN"),
            lambda c: c["sensors"][0].pop("calibration"),
            lambda c: c["sensors"][0]["clock"].update(provenance="UNKNOWN"),
            lambda c: c["sensors"][0].update(R_BS=[[-1, 0, 0], [0, 1, 0], [0, 0, 1]]),
        ]
        for edit in edits:
            c = copy.deepcopy(self.config)
            edit(c)
            with self.subTest(config=c), self.assertRaises(InputError):
                analyze(c, [])

    def test_temporal_summary_is_sample_weighted_valid_only(self):
        report = self.report(self.batch(rates=[.12, 0, 0, 0, 0, 0]),
                             self.batch(1), self.batch(2, ids=["imu0"]))
        self.assertAlmostEqual(report["summary"]["comparable_spread_mean_rad_s"], .05)
        self.assertEqual(report["summary"]["comparable_records"], 2)
        self.assertEqual(report["summary"]["unresolved_records"], 1)
        self.assertEqual(report["summary"]["accepted_record_counts"]["imu0"], 3)
        self.assertEqual(report["summary"]["absent_record_counts"]["imu1"], 1)
        self.assertIn("not time-weighted", report["summary"]["weighting"])

    def test_future_cannot_change_prefix(self):
        first = self.batch()
        a = self.report(first, self.batch(1, rates=[1] * 6))
        b = self.report(first, self.batch(1, ids=[]))
        self.assertEqual(a["records"][0], b["records"][0])
        self.assertNotEqual(a["records"][1], b["records"][1])

    def test_cli_saved_output_sidecar_independence_and_exclusive_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "config.json"
            samples = root / "samples.jsonl"
            config.write_text(json.dumps(self.config))
            samples.write_text(json.dumps(self.batch()) + "\n")
            command = [sys.executable, "-B", "-m", "simulation.imu_disagreement",
                       "--config", str(config), "--samples", str(samples)]
            result = subprocess.run(command + ["--output-dir", str(root / "out")],
                                    capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((root / "out/report.md").is_file())
            first = (root / "out/report.json").read_bytes()
            (root / "truth.jsonl").write_bytes(b"\xfftruth")
            (root / "fault-labels.jsonl").write_bytes(b"misleading")
            repeat = subprocess.run(command + ["--output-dir", str(root / "repeat")],
                                    capture_output=True, timeout=30)
            self.assertEqual(repeat.returncode, 0)
            self.assertEqual(first, (root / "repeat/report.json").read_bytes())
            exists = subprocess.run(command + ["--output-dir", str(root / "out")],
                                    capture_output=True, timeout=30)
            self.assertEqual(exists.returncode, 2)
            self.assertEqual(first, (root / "out/report.json").read_bytes())
            samples.write_bytes(b"\xff\n")
            invalid = subprocess.run(command + ["--output-dir", str(root / "invalid")],
                                     capture_output=True, timeout=30)
            self.assertEqual(invalid.returncode, 2)
            report = json.loads((root / "invalid/report.json").read_text())
            self.assertEqual(report["summary"]["unresolved_records"], 1)
            config.write_bytes(b"\xff")
            refused = subprocess.run(command + ["--output-dir", str(root / "refused")],
                                     capture_output=True, timeout=30)
            self.assertEqual(refused.returncode, 2)
            self.assertEqual(json.loads(refused.stderr)["status"], "UNRESOLVED")
            self.assertFalse((root / "refused").exists())


if __name__ == "__main__":
    unittest.main()
