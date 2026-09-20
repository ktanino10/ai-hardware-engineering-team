import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools.public_release_manifest import CONTINUATION, current_file_record


class ReleaseContinuationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.manifest = "historical.json"
        original_bytes = b"preserved historical record\n"
        (self.root / self.manifest).write_bytes(original_bytes)
        self.original = {"path": "docs/example.md", "bytes": 3, "sha256": "old"}
        self.replacement = {
            "path": "docs/example.md", "bytes": 4, "sha256": "new",
            "supersedes": {self.manifest: "old"},
        }
        self.record = {
            "record_type": "PUBLIC_SOFTWARE_CONTINUATION",
            "historical_manifests": {
                self.manifest: hashlib.sha256(original_bytes).hexdigest(),
            },
            "files": [self.replacement],
        }

    def resolve(self):
        target = self.root / CONTINUATION
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.record), encoding="utf-8")
        return current_file_record(self.root, self.manifest, self.original)

    def test_explicit_replacement_binds_its_historical_file(self):
        self.assertEqual(self.resolve(), self.replacement)

    def test_unmodified_files_keep_the_original_record(self):
        self.record["files"] = []
        self.assertEqual(self.resolve(), self.original)

    def test_changed_historical_manifest_is_rejected(self):
        (self.root / self.manifest).write_bytes(b"rewritten history")
        with self.assertRaisesRegex(ValueError, "Historical manifest changed"):
            self.resolve()

    def test_wrong_historical_file_binding_is_rejected(self):
        self.replacement["supersedes"][self.manifest] = "unrelated"
        with self.assertRaisesRegex(ValueError, "Unbound historical file"):
            self.resolve()

    def test_duplicate_and_unsafe_replacements_are_rejected(self):
        self.record["files"].append(dict(self.replacement))
        with self.assertRaisesRegex(ValueError, "Duplicate continuation path"):
            self.resolve()
        self.record["files"].pop()
        for path in ("../secret", "/absolute", ".git/config",
                     ".agent-work/private", "docs/../secret", "docs//example.md"):
            with self.subTest(path=path):
                self.replacement["path"] = path
                with self.assertRaisesRegex(ValueError, "Unsafe continuation path"):
                    self.resolve()

    def test_unknown_record_type_is_rejected(self):
        self.record["record_type"] = "UNREVIEWED_OVERRIDE"
        with self.assertRaisesRegex(ValueError, "Unsupported public release"):
            self.resolve()

    def test_new_checker_files_are_bound_to_current_bytes(self):
        root = Path(__file__).resolve().parents[2]
        record = json.loads((root / CONTINUATION).read_bytes())
        names = [row["path"] for row in record["added_files"]]
        self.assertEqual(len(names), len(set(names)))
        self.assertIn("tools/public_release_manifest.py", names)
        self.assertIn("tools/tests/test_public_release_manifest.py", names)
        for row in record["added_files"]:
            with self.subTest(path=row["path"]):
                data = (root / row["path"]).read_bytes()
                self.assertEqual(len(data), row["bytes"])
                self.assertEqual(hashlib.sha256(data).hexdigest(), row["sha256"])
