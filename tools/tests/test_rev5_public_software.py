"""Public export integrity and boundaries; no private Git objects, SDK or devices."""

import ast
import hashlib
import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

from tools.public_release_manifest import current_file_record


ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "docs/rev5-public-release"
N8R8 = "firmware/bench-imu-01-rev5/"


def load(name):
    return json.loads((PACKET / name).read_text(encoding="utf-8"))


class PublicSoftwareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.intake = load("software-intake.json")
        cls.manifest = load("software-manifest.json")

    def test_public_manifest_hashes_and_safe_paths(self):
        entries = self.manifest["files"]
        self.assertEqual(len(entries), len({entry["path"] for entry in entries}))
        for entry in entries:
            name = entry["path"]
            path = Path(name)
            with self.subTest(path=name):
                self.assertFalse(path.is_absolute())
                self.assertFalse(set(path.parts) & {"..", ".git", ".agent-work"})
                target = ROOT / path
                self.assertTrue(target.is_file())
                self.assertFalse(target.is_symlink())
                self.assertFalse(any(parent.is_symlink() for parent in target.parents))
                data = target.read_bytes()
                current = current_file_record(
                    ROOT, "docs/rev5-public-release/software-manifest.json", entry)
                self.assertEqual(len(data), current["bytes"])
                self.assertEqual(hashlib.sha256(data).hexdigest(), current["sha256"])
                if entry["disposition"] == "BYTE_IDENTICAL_EXPORT":
                    self.assertEqual(entry["sha256"], entry["original_sha256"])
                self.assertNotRegex(
                    data, rb"/(?:Users|home)/[^ \n\"'<>()]+|[.]copilot/session-state/")
                self.assertNotIn(path.suffix.lower(), {
                    ".pdf", ".stl", ".blend", ".f3d", ".elf", ".bin", ".sqlite3",
                    ".png", ".jpg", ".mp4", ".zip", ".log",
                })

    def test_exact_minimal_sources_match_frozen_intake(self):
        expected = {row["path"]: row for row in self.intake["sources"]
                    if row["disposition"] == "BYTE_IDENTICAL_EXPORT"}
        actual = {row["path"]: row for row in self.manifest["files"]
                  if row["disposition"] == "BYTE_IDENTICAL_EXPORT"}
        self.assertEqual(set(actual), set(expected))
        self.assertEqual(len(expected), 28)
        for path, source in expected.items():
            with self.subTest(path=path):
                self.assertEqual(actual[path]["sha256"], source["sha256"])
                self.assertEqual(actual[path]["original_revision"], source["revision"])
        self.assertFalse((ROOT / "simulation/imu_estimation/campaign.py").exists())
        self.assertFalse((ROOT / "simulation/imu_estimation/generate.py").exists())

    def test_c1_is_only_a_non_orderable_summary(self):
        summary = load("software-c1-summary.json")
        self.assertEqual(summary["record_type"], "DERIVED_PUBLIC_SUMMARY_NOT_PRODUCTION_INPUT")
        self.assertEqual(summary["exact_catalogue_candidates"], 10)
        self.assertEqual(summary["unknown_product_requirements"], 2)
        self.assertEqual(summary["adopted_candidates"], 0)
        self.assertEqual(summary["quantity"], "UNKNOWN")
        self.assertEqual(summary["functional_gaps"], 23)
        self.assertEqual(summary["source_observations"], 103)
        self.assertEqual(summary["purchase_readiness"], "CLOSED")
        self.assertEqual(summary["physical_permission"], "NOT_GRANTED")
        self.assertEqual(summary["original_cohort"], {"closed": 2, "unfinished": 42})
        self.assertFalse((ROOT / "tools/rev5_c1_readiness.py").exists())
        self.assertFalse((ROOT / "docs/rev5-c1-bom-readiness-2026-09-18/current").exists())

    def test_original_review_scope_and_not_run_are_preserved(self):
        review = load("software-review.json")
        self.assertEqual(review["new_concrete_defects"], 0)
        self.assertEqual(review["unit_tests_run_pass"],
                         {"c1": 18, "imu": 14, "n8r8": 4, "total": 36})
        self.assertEqual(len(review["packages"]), 3)
        for package in review["packages"]:
            self.assertEqual(package["verdict"], "PASS")
            self.assertEqual(package["acceptance"], "LIMITED_CODE_REVIEW_ONLY")
            self.assertEqual(package["findings"], [])
            self.assertFalse(package["author_code_modified"])
        self.assertEqual(review["historical_n8r8_dynamic_cmake_test"],
                         "NOT_RUN: reviewer host CMake unavailable")
        self.assertEqual(review["independent_sdk_build_elf_bin_device_checks"], "EXCLUDED")
        originals = {row["path"]: row["sha256"] for row in self.intake["sources"]}
        for source in review["source_bindings"]:
            self.assertEqual(source["sha256"], originals[source["path"]])

    def test_derived_pin_projection_keeps_all_full_rev5_conflicts(self):
        notes = load("software-source-notes.json")["native_pin_projection"]
        self.assertTrue(notes["not_a_complete_native_netlist"])
        self.assertTrue(notes["not_schematic_or_hardware_acceptance"])
        self.assertEqual(notes["measurement_nodes"], 11)
        self.assertEqual(notes["fg_conflict_nodes"], 3)
        self.assertEqual(len(notes["pins"]), 14)
        root = ET.parse(ROOT / notes["path"]).getroot()
        self.assertEqual(root.attrib["scope"], "DERIVED_PUBLIC_U201_PIN_REFERENCE")
        self.assertEqual(root.attrib["source_sha256"], notes["source"]["sha256"])
        self.assertEqual(len(root.findall(".//node")), 14)
        header = (ROOT / N8R8 / "preparation/generated/pin_definitions.h").read_text()
        definitions = dict(re.findall(r"^#define (REV5_PIN_\w+_GPIO) (\d+)$",
                                      header, re.MULTILINE))
        measurement = set()
        conflicts = set()
        for pin in notes["pins"]:
            with self.subTest(macro=pin["macro"]):
                self.assertEqual(int(definitions[pin["macro"]]), pin["gpio"])
                self.assertEqual(len(root.findall(
                    f".//net[@name='{pin['net']}']/node[@ref='U201'][@pin='{pin['pad']}']")), 1)
                if pin["use"] == "MEASUREMENT":
                    measurement.add(pin["gpio"])
                else:
                    self.assertEqual(pin["use"], "OUT_OF_SCOPE_FG_CONFLICT")
                    conflicts.add(pin["gpio"])
        self.assertEqual(measurement, {4, 5, 6, 7, 15, 16, 11, 12, 13, 43, 44})
        self.assertEqual(conflicts, {35, 36, 37})
        self.assertTrue(measurement.isdisjoint(conflicts))

    def test_original_dynamic_cmake_test_body_is_unchanged(self):
        witness = self.manifest["preserved_cmake_test"]
        text = (ROOT / witness["path"]).read_text()
        functions = [node for node in ast.walk(ast.parse(text))
                     if isinstance(node, ast.FunctionDef) and node.name == witness["name"]]
        self.assertEqual(len(functions), 1)
        body = ast.get_source_segment(text, functions[0]).encode()
        self.assertEqual(hashlib.sha256(body).hexdigest(), witness["sha256"])
        self.assertEqual(witness["name"], "test_cmake_guard_rejects_changed_inputs")

    def test_synthetic_fixture_is_complete_and_not_truth_input(self):
        fixture = ROOT / "docs/rev5-six-imu-fault-study-2026-09-13/author/run-001/one-bias"
        self.assertEqual({path.name for path in fixture.iterdir()}, {"config.json", "samples.jsonl"})
        config = json.loads((fixture / "config.json").read_text())
        self.assertEqual(config["classification"], "SYNTHETIC_REFERENCE")
        self.assertEqual(len(config["sensors"]), 6)
        rows = (fixture / "samples.jsonl").read_bytes().splitlines()
        self.assertEqual(len(rows), 1201)
        for row in rows:
            self.assertEqual(set(json.loads(row)), {"t_s", "samples"})

    def test_landing_links_preserve_v2_and_reach_software_guides(self):
        prefix = ("https://github.com/ktanino10/ai-hardware-engineering-team/"
                  "blob/main/docs/rev5-public-release/")
        for landing, guide in (("index.html", "software.md"),
                               ("index.ja.html", "software.ja.md")):
            with self.subTest(page=landing):
                text = (ROOT / "visualization" / landing).read_text()
                self.assertIn('href="rev5-full-assembly-v2/index.html"', text)
                self.assertIn('href="' + prefix + guide + '"', text)
                self.assertIn("NOT_FOR_FLASH", text)
                self.assertIn("35/36/37", text)
                self.assertNotIn('href="../../docs/', text)

    def test_original_v2_files_remain_byte_identical(self):
        original = load("manifest.json")
        for row in original["files"]:
            with self.subTest(path=row["path"]):
                self.assertEqual(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest(),
                                 row["sha256"])


if __name__ == "__main__":
    unittest.main()
