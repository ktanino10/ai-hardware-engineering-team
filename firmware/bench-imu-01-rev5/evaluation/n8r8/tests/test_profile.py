"""Small offline profile/wiring checks; no device, firmware execution or installation."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET

PROFILE = Path(__file__).resolve().parents[1]
REV5 = PROFILE.parents[1]
REPO = REV5.parents[1]


def settings(path):
    result = {}
    for line in path.read_text().splitlines():
        if line.startswith("CONFIG_"):
            key, value = line.split("=", 1)
            result[key] = value
        elif re.fullmatch(r"# CONFIG_\w+ is not set", line):
            result[line.split()[1]] = "n"
    return result


class ProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = json.loads((PROFILE / "evaluation-profile.json").read_text())
        cls.bindings = re.findall(
            r'require_frozen_source\("([^"]+)" "([0-9a-f]{64})"\)',
            (PROFILE / "source-contract.cmake").read_text())

    def test_frozen_inputs_and_corrected_application(self):
        self.assertEqual(len(self.bindings), 11)
        for path, expected in self.bindings:
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((REV5 / path).read_bytes()).hexdigest(), expected)
        self.assertEqual(self.profile["measurement_source"]["sha256"],
                         hashlib.sha256((REV5 / "measurement/main/main.c").read_bytes()).hexdigest())
        self.assertEqual(self.profile["measurement_source"]["corrected_source_revision"],
                         "962ce7e977c25263ca58429a62e61beb8b12a9ec")

    def test_configuration_selections_match_baseline(self):
        self.assertEqual(settings(PROFILE / "sdkconfig.defaults"),
                         settings(REV5 / "measurement/sdkconfig.defaults"))
        self.assertFalse(self.profile["selected_build"]["psram_enabled"])
        self.assertEqual(self.profile["memory_hardware"]["psram_MB"], 8)
        self.assertEqual(self.profile["memory_hardware"]["psram_interface"], "Octal SPI")
        self.assertFalse(self.profile["formal_module_adoption"])

    def test_original_component_is_reused_without_c_fork(self):
        cmake = (PROFILE / "CMakeLists.txt").read_text()
        self.assertIn('set(EXTRA_COMPONENT_DIRS "${REV5_ROOT}/measurement/main")', cmake)
        self.assertIn("project(rev5_n8r8_evaluation)", cmake)
        self.assertIn('set(PROJECT_VER "n8r8-eval-rev5-m1")', cmake)
        self.assertNotIn("COMPILE_DEFINITIONS", cmake)
        self.assertEqual(list(PROFILE.rglob("*.c")), [])
        main = (REV5 / "measurement/main/main.c").read_text()
        self.assertIn('#define PROFILE_ID "rev5-m1"', main)
        self.assertIn("#define SENSOR_COUNT 6", main)
        self.assertIn("#define SCAN_PERIOD_US UINT32_C(500000)", main)
        self.assertIn("REV5B1 ", main)

    def test_actual_gpio_subset_and_native_contract(self):
        header = (REV5 / "preparation/generated/pin_definitions.h").read_text()
        definitions = dict(re.findall(r"^#define (REV5_PIN_\w+_GPIO) (\d+)$",
                                      header, flags=re.MULTILINE))
        main = (REV5 / "measurement/main/main.c").read_text()
        used = set(re.findall(r"\bREV5_PIN_\w+_GPIO\b", main))
        pins = {int(definitions[name]) for name in used}
        self.assertEqual(pins, {4, 5, 6, 7, 15, 16, 11, 12, 13, 43, 44})
        self.assertTrue(pins.isdisjoint(self.profile["pin_subset"]["reserved_GPIO"]))
        netlist = ET.parse(PROFILE / "reference/u201-pin-reference.xml")
        for name in used:
            stem = name.removesuffix("_GPIO")
            pad = re.search(rf'^#define {stem}_PAD "([^"]+)"$', header, re.MULTILINE).group(1)
            net = re.search(rf'^#define {stem}_NET "([^"]+)"$', header, re.MULTILINE).group(1)
            nodes = netlist.findall(f".//net[@name='{net}']/node[@ref='U201'][@pin='{pad}']")
            self.assertEqual(len(nodes), 1, (name, net, pad))
        self.assertFalse(self.profile["measurement_source"]["one_sensor_profile"])

    def test_cmake_guard_rejects_changed_inputs(self):
        cmake = os.environ["REV5_EVAL_CMAKE"]
        scratch = Path(os.environ["REV5_EVAL_TEST_SCRATCH"])
        self.assertTrue(scratch.is_dir())
        with tempfile.TemporaryDirectory(prefix="profile-", dir=scratch) as temporary:
            copied = Path(temporary)
            for path, _ in self.bindings:
                target = copied / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(REV5 / path, target)
            command = [cmake, f"-DREV5_ROOT={copied}", "-P", str(PROFILE / "source-contract.cmake")]
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for path in ("measurement/main/main.c", "preparation/generated/pin_definitions.h",
                         "measurement/main/CMakeLists.txt"):
                with self.subTest(path=path):
                    target = copied / path
                    original = target.read_bytes()
                    target.write_bytes(original + b"\n")
                    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("Frozen source changed: " + path, result.stderr)
                    target.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
