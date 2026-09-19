"""Focused public offline closure checks; no private Git, SDK or device access."""

import ast
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "docs/rev5-offline-tools-release"
FIXTURE = "docs/rev5-six-imu-fault-study-2026-09-13/author/run-001/one-bias"
STDLIB = {
    "argparse", "collections", "copy", "hashlib", "io", "json", "math",
    "pathlib", "platform", "subprocess", "sys", "tempfile", "unittest",
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Links(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs).get("href"))


class OfflinePublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.intake = load(PACKET / "intake.json")
        cls.manifest = load(PACKET / "manifest.json")
        cls.exports = {row["path"]: row for row in cls.intake["exact_export_candidates"]}

    def test_manifest_hashes_and_exact_safe_paths(self):
        entries = self.manifest["files"]
        names = {row["path"] for row in entries}
        self.assertEqual(len(entries), len(names))
        self.assertEqual(
            set(self.manifest["expected_changed_files_from_public_base"]),
            names | {"docs/rev5-offline-tools-release/manifest.json"},
        )
        for row in entries:
            name = row["path"]
            path = PurePosixPath(name)
            with self.subTest(path=name):
                self.assertFalse(path.is_absolute())
                self.assertEqual(path.as_posix(), name)
                self.assertFalse({"..", ".git", ".agent-work"} & set(path.parts))
                self.assertFalse(name.startswith(("firmware/", "hardware/", "bom/")))
                target = ROOT / path
                self.assertTrue(target.is_file())
                self.assertFalse(any(p.is_symlink() for p in (target, *target.parents)))
                data = target.read_bytes()
                self.assertEqual(len(data), row["bytes"])
                self.assertEqual(hashlib.sha256(data).hexdigest(), row["sha256"])
                self.assertNotRegex(data, rb"/(?:Users|home)/[^ \n\"'<>()]+|[.]copilot/session-state/")
                self.assertNotIn(path.suffix.lower(), {
                    ".pdf", ".stl", ".blend", ".f3d", ".elf", ".bin", ".sqlite3",
                    ".png", ".jpg", ".mp4", ".zip", ".log",
                })

    def test_eleven_exports_match_frozen_public_objects(self):
        actual = {row["path"]: row for row in self.manifest["files"]
                  if row["disposition"] == "BYTE_IDENTICAL_PUBLIC_EXPORT"}
        self.assertEqual(set(actual), set(self.exports))
        self.assertEqual(len(actual), 11)
        for name, original in self.exports.items():
            with self.subTest(path=name):
                self.assertEqual(actual[name]["source_revision"], self.intake["source_revision"])
                self.assertEqual(actual[name]["source_git_blob"], original["git_blob"])
                self.assertEqual(actual[name]["sha256"], original["sha256"])
        self.assertEqual(self.intake["source_revision"],
                         "6a86f5e71934c78435ca31f3f696da48de5ddd5a")
        self.assertFalse((ROOT / "simulation/imu_estimation/campaign.py").exists())
        self.assertFalse((ROOT / "simulation/imu_estimation/generate.py").exists())

    def test_all_python_imports_resolve_inside_export_or_stdlib(self):
        python_paths = {name for name in self.exports if name.endswith(".py")}
        modules = {name[:-3].replace("/", ".").removesuffix(".__init__")
                   for name in python_paths}
        packages = {name.rsplit(".", 1)[0] for name in modules}
        for name in python_paths:
            tree = ast.parse((ROOT / name).read_bytes(), filename=name)
            package = name.rsplit("/", 1)[0].replace("/", ".")
            for node in ast.walk(tree):
                imports = []
                if isinstance(node, ast.Import):
                    imports = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if node.level:
                        module = importlib.util.resolve_name("." * node.level + module, package)
                    imports = [module]
                    imports.extend(module + "." + alias.name for alias in node.names
                                   if module in packages)
                for module in imports:
                    with self.subTest(path=name, module=module):
                        if module.split(".")[0] != "simulation":
                            self.assertIn(module.split(".")[0], STDLIB)
                        else:
                            self.assertIn(module, modules | packages)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    self.assertNotIn(node.func.id, {"__import__", "eval", "exec"})

    def test_original_fourteen_tests_and_all_implementation_hash_inputs_exist(self):
        tests = ROOT / "simulation/imu_disagreement/tests/test_report.py"
        methods = [n.name for n in ast.walk(ast.parse(tests.read_bytes()))
                   if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
        self.assertEqual(len(methods), 14)
        from simulation.imu_disagreement.__main__ import implementation_hashes
        expected = {name: row["sha256"] for name, row in self.exports.items()
                    if name.endswith(".py") and "/tests/" not in name}
        self.assertEqual(implementation_hashes(), expected)
        self.assertEqual(len(expected), 7)

    def test_exact_synthetic_fixture_has_no_truth_sidecars(self):
        fixture = ROOT / FIXTURE
        self.assertEqual({p.name for p in fixture.iterdir()}, {"config.json", "samples.jsonl"})
        config = load(fixture / "config.json")
        self.assertEqual(config["classification"], "SYNTHETIC_REFERENCE")
        self.assertEqual(config["frames"], "RH_W_z_up_B_S_R_BS_q_WB_wxyz")
        self.assertEqual(config["units"],
                         {"time": "s", "gyro": "rad/s", "accel": "m/s^2", "position": "m"})
        self.assertEqual(len(config["sensors"]), 6)
        self.assertTrue(all(s["clock"]["provenance"] == "synthetic_exact"
                            for s in config["sensors"]))
        rows = (fixture / "samples.jsonl").read_bytes().splitlines()
        self.assertEqual(len(rows), 1201)
        for row in rows:
            self.assertEqual(set(json.loads(row)), {"t_s", "samples"})

    def test_c1_stays_only_non_orderable_aggregate(self):
        summary = load(ROOT / "docs/rev5-public-release/software-c1-summary.json")
        expected = {
            "record_type": "DERIVED_PUBLIC_SUMMARY_NOT_PRODUCTION_INPUT",
            "exact_catalogue_candidates": 10, "unknown_product_requirements": 2,
            "adopted_candidates": 0, "quantity": "UNKNOWN", "functional_gaps": 23,
            "source_observations": 103, "purchase_readiness": "CLOSED",
            "physical_permission": "NOT_GRANTED",
            "original_cohort": {"closed": 2, "unfinished": 42},
        }
        for key, value in expected.items():
            self.assertEqual(summary[key], value, key)
        self.assertFalse((ROOT / "tools/rev5_c1_readiness.py").exists())
        self.assertFalse((ROOT / "docs/rev5-c1-bom-readiness-2026-09-18/current").exists())

    def test_historical_review_is_not_reissued_or_extended(self):
        history = load(PACKET / "provenance.json")["historical_review"]
        self.assertEqual(history["public_summary"]["sha256"],
                         self.intake["historical_review_reference"]["sha256"])
        self.assertEqual(history["imu"]["acceptance"], "LIMITED_CODE_REVIEW_ONLY")
        self.assertEqual(history["imu"]["tests"], 14)
        self.assertFalse(history["imu"]["author_code_modified"])
        self.assertEqual(history["original_unit_tests_run_pass"],
                         {"c1": 18, "imu": 14, "n8r8": 4, "total": 36})
        self.assertEqual(history["historical_n8r8_dynamic_cmake_test"],
                         "NOT_RUN: reviewer host CMake unavailable")
        self.assertEqual(history["independent_sdk_build_elf_bin_device_checks"], "EXCLUDED")
        self.assertFalse(history["new_independent_review"])

    def test_isolated_closure_runs_all_original_tests_and_example(self):
        with tempfile.TemporaryDirectory(prefix="rev5-offline-") as temp:
            root = Path(temp)
            for name in self.exports:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            self.assertFalse((root / ".git").exists())
            self.assertFalse((root / "firmware").exists())
            env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            command = [sys.executable, "-B", "-S"]
            tests = subprocess.run(
                command + ["-m", "unittest", "discover", "-s",
                           "simulation/imu_disagreement/tests", "-v"],
                cwd=root, env=env, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(tests.returncode, 0, tests.stdout + tests.stderr)
            self.assertIn("Ran 14 tests", tests.stderr)
            run = subprocess.run(
                command + ["-m", "simulation.imu_disagreement",
                           "--config", FIXTURE + "/config.json",
                           "--samples", FIXTURE + "/samples.jsonl",
                           "--output-dir", "output"],
                cwd=root, env=env, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            report = load(root / "output/report.json")
            example = load(PACKET / "example-summary.json")
            for key in ("format", "scope", "limits", "errors"):
                self.assertEqual(report[key], example[key])
            summary = report["summary"]
            for key, value in example["summary"].items():
                if isinstance(value, float):
                    self.assertAlmostEqual(summary[key], value, places=12)
                else:
                    self.assertEqual(summary[key], value, key)
            self.assertEqual(report["provenance"]["implementation_sha256"],
                             example["provenance"]["implementation_sha256"])
            self.assertEqual(len(report["records"]), 1201)
            self.assertTrue((root / "output/report.md").is_file())
            (root / "simulation/imu_estimation/schema.py").unlink()
            missing = subprocess.run(
                command + ["-m", "simulation.imu_disagreement", "--help"],
                cwd=root, env=env, capture_output=True, text=True, timeout=30,
            )
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("ModuleNotFoundError", missing.stderr)

    def test_en_ja_landing_adds_tools_without_losing_v2_v3(self):
        prefix = ("https://github.com/ktanino10/ai-hardware-engineering-team/"
                  "blob/main/docs/rev5-offline-tools-release/")
        for landing, guide in (("index.html", "README.md"), ("index.ja.html", "README.ja.md")):
            text = (ROOT / "visualization" / landing).read_text(encoding="utf-8")
            links = Links(text).links
            with self.subTest(page=landing):
                self.assertIn(prefix + guide, links)
                self.assertIn("rev5-full-assembly-v3/index.html", links)
                self.assertIn("rev5-full-assembly-v2/index.html", links)
                self.assertNotIn('href="../../docs/', text)
        inventory = load(ROOT / "docs/language-coverage.json")
        entries = {row["source"]: row for row in inventory["entry_points"]}
        for source in ("docs/rev5-offline-tools-release/README.md",
                       "simulation/imu_disagreement/README.md"):
            self.assertEqual(entries[source]["ja"], "docs/rev5-offline-tools-release/README.ja.md")
        for path in ("README.md", "README.ja.md"):
            text = (PACKET / path).read_text(encoding="utf-8")
            self.assertIn("SYNTHETIC ONLY", text)
            self.assertIn("NOT_RUN", text)
            self.assertIn("software-c1-summary.json", text)

    def test_all_prior_v2_v3_bundle_files_and_six_movies_are_unchanged(self):
        for manifest, prefix in (
            ("docs/rev5-public-release/manifest.json", "visualization/rev5-full-assembly-v2/"),
            ("docs/rev5-v3-media-release/manifest.json", "visualization/rev5-full-assembly-v3/"),
        ):
            rows = [row for row in load(ROOT / manifest)["files"]
                    if row["path"].startswith(prefix)]
            self.assertTrue(rows)
            for row in rows:
                with self.subTest(path=row["path"]):
                    self.assertEqual(sha(ROOT / row["path"]), row["sha256"])
            if "v3" in prefix:
                self.assertEqual(sum(row["path"].endswith(".mp4") for row in rows), 6)

    def test_ci_keeps_existing_step_and_adds_offline_closure(self):
        text = (ROOT / ".github/workflows/simulation-check.yml").read_text(encoding="utf-8")
        self.assertIn("name: Simulation numerical and evidence regressions (not hardware approval)", text)
        self.assertIn("run: python -m unittest discover -s tests -v", text)
        self.assertIn("working-directory: simulation", text)
        self.assertIn("simulation/imu_disagreement/tests", text)
        self.assertIn("test_rev5_offline_publication.py", text)
        self.assertIn('"docs/rev5-offline-tools-release/**"', text)


if __name__ == "__main__":
    unittest.main()
