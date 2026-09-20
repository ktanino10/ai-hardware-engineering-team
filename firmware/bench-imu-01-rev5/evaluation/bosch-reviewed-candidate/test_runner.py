"""Preflight guards only; these tests never compile or contact a device."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest


PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("selected_bosch_runner", PACKAGE / "run_host.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class RunnerGuards(unittest.TestCase):
    def test_mismatched_case_and_oracle_lengths_fail(self):
        with self.assertRaisesRegex(ValueError, "different lengths"):
            RUNNER.paired([1, 2], [1])
        self.assertEqual(list(RUNNER.paired([1], [2])), [(1, 2)])

    def test_missing_completion_is_not_a_pass(self):
        with self.assertRaisesRegex(ValueError, "Missing cases"):
            RUNNER.parse_cases(b'{"passed":true}\n', 1)

    def test_wrong_completion_count_is_not_a_pass(self):
        with self.assertRaisesRegex(ValueError, "Missing cases"):
            RUNNER.parse_cases(b'{"passed":true}\n{"cases":2}\n', 1)

    def test_changed_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory).resolve() / "input"
            path.write_bytes(b"selected")
            binding = {"bytes": 8, "sha256": hashlib.sha256(b"selected").hexdigest()}
            self.assertEqual(RUNNER.checked(path, binding), b"selected")
            path.write_bytes(b"modified")
            with self.assertRaisesRegex(ValueError, "Bound input differs"):
                RUNNER.checked(path, binding)

    def test_symlinked_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory).resolve() / "original"
            original.write_bytes(b"selected")
            link = Path(directory).resolve() / "link"
            link.symlink_to(original)
            binding = {"bytes": 8, "sha256": hashlib.sha256(b"selected").hexdigest()}
            with self.assertRaisesRegex(ValueError, "symlinked input"):
                RUNNER.checked(link, binding)


if __name__ == "__main__":
    unittest.main()
