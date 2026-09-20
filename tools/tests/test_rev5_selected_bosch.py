"""Verify the selected public source and build binding, without private Git or SDK."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
REV5 = ROOT / "firmware/bench-imu-01-rev5"
PACKAGE = REV5 / "evaluation/bosch-reviewed-candidate"
VENDOR = REV5 / "measurement/vendor/bosch"
SELECTED = "4ad4f91eb09f380df678e2bf1098e4140092337a442390e98915f43b9b302204"
ORIGINAL = "c3f912bc3033b411fa8df67dbdf66f5b3d74cf203b2e8aa4a8c834821116c2b3"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


class SelectedBoschTests(unittest.TestCase):
    def test_selected_source_is_exact_and_not_duplicated(self):
        source = (VENDOR / "bmi2.c").read_bytes()
        binding = load(PACKAGE / "candidate.json")
        self.assertEqual(sha(source), SELECTED)
        self.assertEqual(len(source), binding["derivative"]["bytes"])
        self.assertEqual(binding["derivative"]["sha256"], SELECTED)
        self.assertEqual(source.count(b"\n"), source.count(b"\r\n"))
        self.assertEqual(binding["C3"], "OPEN_MEDIUM_EXPLICITLY_NOT_SELECTED")
        self.assertFalse((PACKAGE / "bmi2.c").exists())
        for entry in binding["test_files"]:
            self.assertEqual(sha((PACKAGE / entry["path"]).read_bytes()), entry["sha256"])

    def test_current_provenance_does_not_claim_verbatim_modified_source(self):
        provenance = load(VENDOR / "provenance.json")
        for entry in provenance["files"]:
            data = (REV5 / "measurement" / entry["path"]).read_bytes()
            self.assertEqual(sha(data), entry["sha256"])
            self.assertEqual(len(data), entry["bytes"])
            if entry["upstream_path"] == "bmi2.c":
                self.assertTrue(entry["modified"])
                self.assertEqual(entry["upstream_sha256"], ORIGINAL)
                self.assertEqual(entry["upstream_bytes"], 374283)
                self.assertTrue((VENDOR / entry["candidate_binding"]).resolve().is_file())
            else:
                self.assertFalse(entry["modified"])

    def test_exact_combined_patch_reconstructs_original_source(self):
        with tempfile.TemporaryDirectory(prefix="rev5-patch-") as temporary:
            target = Path(temporary) / "bmi2.c"
            target.write_bytes((VENDOR / "bmi2.c").read_bytes().replace(b"\r\n", b"\n"))
            result = subprocess.run(
                ["patch", "-p1", "--reverse", "--batch", "--fuzz=0",
                 "-i", str(PACKAGE / "bmi2-selected.patch")],
                cwd=temporary, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertEqual(sha(target.read_bytes().replace(b"\n", b"\r\n")), ORIGINAL)

    def test_cmake_rejects_changed_selected_driver_and_metadata(self):
        contract = REV5 / "evaluation/n8r8/source-contract.cmake"
        bindings = dict(re.findall(
            r'require_frozen_source\("([^"]+)" "([0-9a-f]{64})"\)', contract.read_text()))
        self.assertEqual(len(bindings), 11)
        self.assertEqual(bindings["measurement/vendor/bosch/bmi2.c"], SELECTED)
        with tempfile.TemporaryDirectory(dir=os.environ["REV5_EVAL_TEST_SCRATCH"]) as temporary:
            root = Path(temporary)
            for name, digest in bindings.items():
                source = REV5 / name
                self.assertEqual(sha(source.read_bytes()), digest)
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            command = [os.environ["REV5_EVAL_CMAKE"], f"-DREV5_ROOT={root}", "-P", str(contract)]
            for name in ("measurement/vendor/bosch/bmi2.c", "measurement/measurement-profile.json"):
                with self.subTest(path=name):
                    target = root / name
                    original = target.read_bytes()
                    target.write_bytes(original + b"\n")
                    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("Frozen source changed: " + name, result.stderr)
                    target.write_bytes(original)

    def test_profile_and_retained_crt_functions_match_the_binding(self):
        profile = load(REV5 / "evaluation/n8r8/evaluation-profile.json")
        self.assertEqual(profile["selected_vendor_source"]["sha256"], SELECTED)
        self.assertFalse(profile["hardware_actions_authorized"])
        source = (VENDOR / "bmi2.c").read_text()
        for name, digest in load(PACKAGE / "candidate.json")["retained_CRT_functions"].items():
            start = re.search(r"^static int8_t " + name + r"\([^;{}]*\)\n\{\n", source, re.M)
            self.assertIsNotNone(start)
            end = source.index("\n}\n", start.end()) + 3
            self.assertEqual(sha(source[start.start():end].encode()), digest)


if __name__ == "__main__":
    unittest.main()
