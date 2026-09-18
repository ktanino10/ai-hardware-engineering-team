"""Author packaging checks only; no engineering or security acceptance."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parent
CONTEXTS = (
    "acceptance-spec.json", "firmware-authority-map.json", "driver-proposal.json",
    "driver-schematic.md", "source-proposals.json", "capacitance-correction.json",
)
PUBLIC_FILES = (
    "model.py", "sequencer.py", "scenarios.py", "cli.py", "_bootstrap.py",
    "test_sequencer.py", "test_portability.py", "README.md", "manifest.json",
    "source-selection.json", "publication-status.json", "source-context/README.md",
) + tuple("source-context/" + name for name in CONTEXTS)
RUNTIME_FILES = (
    "model.py", "sequencer.py", "scenarios.py", "cli.py", "_bootstrap.py",
) + tuple("source-context/" + name for name in CONTEXTS)


def tree_hashes(root):
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*") if p.is_file()
    }


def assert_permissions(test, value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ("actual_operation_permission", "actual_bus_permission",
                       "physical_disconnection_established"):
                test.assertIs(child, False, key)
            assert_permissions(test, child)
    elif isinstance(value, list):
        for child in value:
            assert_permissions(test, child)


class PortabilityTests(unittest.TestCase):
    def setUp(self):
        # Scratch stays inside the package/write scope, never a system temp dir.
        self.work = ROOT / (".portability-work-" + str(os.getpid())
                            + "-" + self._testMethodName)
        self.work.mkdir()
        self.addCleanup(shutil.rmtree, self.work)
        self.copy = self.work / "export copy with spaces"
        self.foreign = self.work / "foreign cwd"
        self.foreign.mkdir()
        for name in PUBLIC_FILES:
            target = self.copy / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        self.env = {
            "PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1",
            "PYTHONPATH": str(self.foreign),
            "GIT_CEILING_DIRECTORIES": str(self.work),
        }

    def run_python(self, *args):
        return subprocess.run(
            [sys.executable, "-B", *map(str, args)],
            cwd=self.foreign, env=self.env, capture_output=True, text=True,
            timeout=60, check=False,
        )

    def cli(self, scenario="normal"):
        return self.run_python(self.copy / "cli.py", scenario)

    def assert_refused(self, result, marker):
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn(marker, result.stderr)
        self.assertNotIn(str(self.work), result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_standalone_cli_all_ten_from_foreign_cwd_with_spaces(self):
        for name in ("sequencer", "scenarios", "model", "_bootstrap"):
            (self.foreign / (name + ".py")).write_text(
                "raise AssertionError('FOREIGN_MODULE_EXECUTED')\n")
        before = tree_hashes(self.work)
        result = self.cli("all")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["execution_scope"], "PUBLIC_DERIVATIVE_CURRENT_EXECUTION")
        names = {
            "normal", "held-request", "stale-high-return", "cancel", "evidence-loss",
            "unknown-C", "unknown-local", "unknown-output", "unknown-ACK", "bad-order",
        }
        self.assertEqual({s["scenario"] for s in data["scenarios"]}, names)
        self.assertEqual(len(data["source_bindings"]), 7)
        normal = next(s for s in data["scenarios"] if s["scenario"] == "normal")
        self.assertTrue(normal["final"]["synthetic_sequenced_service"])
        self.assertIn("transaction:useful-after-event:DONE",
                      normal["final"]["model"]["effects_not_rolled_back"])
        assert_permissions(self, data)
        self.assertNotIn(str(self.work), result.stdout + result.stderr)
        self.assertFalse((self.copy / ".git").exists())
        self.assertEqual(tree_hashes(self.work), before)
        for name in sorted(names):
            one = self.cli(name)
            self.assertEqual(one.returncode, 0, one.stderr)
            self.assertEqual(json.loads(one.stdout)["scenarios"][0]["scenario"], name)
        self.assertEqual(tree_hashes(self.work), before)

    def test_existing_29_tests_run_in_export_copy(self):
        result = self.run_python("-m", "unittest", "discover", "-s", self.copy,
                                 "-p", "test_sequencer.py", "-v")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Ran 29 tests", result.stderr)
        self.assertNotIn("__pycache__", " ".join(tree_hashes(self.copy)))

    def test_each_missing_or_tampered_binding_hard_fails(self):
        for name in ("model.py",) + tuple("source-context/" + n for n in CONTEXTS):
            path = self.copy / name
            original = path.read_bytes()
            for mode in ("missing", "tampered"):
                with self.subTest(file=name, mode=mode):
                    if mode == "missing":
                        path.unlink()
                    else:
                        path.write_bytes(original + b"\n")
                    self.assert_refused(self.cli(), "PUBLIC_SOURCE_")
                    path.write_bytes(original)

    def test_each_missing_or_tampered_adapter_hard_fails(self):
        for name in ("_bootstrap.py", "sequencer.py", "scenarios.py"):
            path = self.copy / name
            original = path.read_bytes()
            for mode in ("missing", "tampered"):
                with self.subTest(file=name, mode=mode):
                    if mode == "missing":
                        path.unlink()
                    else:
                        path.write_bytes(original + b"\n")
                    self.assert_refused(self.cli(), "PUBLIC_")
                    path.write_bytes(original)

    def test_symlinked_model_context_or_adapter_is_not_read(self):
        for name in ("model.py", "_bootstrap.py", "sequencer.py", "scenarios.py",
                     "source-context/acceptance-spec.json"):
            with self.subTest(file=name):
                path = self.copy / name
                original = path.read_bytes()
                external = self.foreign / "do not read"
                external.write_bytes(original)
                path.unlink()
                path.symlink_to(external)
                self.assert_refused(self.cli(), "SYMLINK")
                path.unlink()
                path.write_bytes(original)
        context = self.copy / "source-context"
        moved = self.foreign / "context not admitted"
        context.rename(moved)
        context.symlink_to(moved, target_is_directory=True)
        self.assert_refused(self.cli(), "PUBLIC_SOURCE_SYMLINK")

    def test_preloaded_modules_and_mutated_cached_bundle_are_not_reused(self):
        code = """
import json, pathlib, runpy, sys, types
root = pathlib.Path(sys.argv[1])
fake = types.ModuleType("foreign")
fake.Model = object
for name in ("model", "sequencer", "scenarios", "_bootstrap", "_rev5_1051_host_model"):
    sys.modules[name] = fake
entry = runpy.run_path(str(root / "cli.py"))
first = entry["_load_public"]()
first["sequencer"].base.Model = object
second = entry["_load_public"]()
assert second["sequencer"] is not first["sequencer"]
assert second["sequencer"].base.Model is not object
assert second["scenarios"].base is second["sequencer"].base
assert second["scenarios"].normal()["final"]["synthetic_sequenced_service"]
print(json.dumps({"fresh_bound_modules": True}))
"""
        result = self.run_python("-c", code, self.copy)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["fresh_bound_modules"])

    def test_changed_binding_after_load_cannot_hide_behind_cache(self):
        code = """
import pathlib, runpy, sys
root = pathlib.Path(sys.argv[1])
entry = runpy.run_path(str(root / "cli.py"))
first = entry["_load_public"]()
path = root / sys.argv[2]
path.write_bytes(path.read_bytes() + b"\\n")
for action in (first["sequencer"].check_bindings, entry["_load_public"]):
    try:
        action()
    except RuntimeError as error:
        assert str(error).startswith("PUBLIC_SOURCE_MISMATCH:")
    else:
        raise AssertionError("stale cache accepted changed bytes")
print("changed bytes refused")
"""
        for name in ("model.py", "source-context/acceptance-spec.json"):
            with self.subTest(file=name):
                path = self.copy / name
                original = path.read_bytes()
                result = self.run_python("-c", code, self.copy, name)
                self.assertEqual(result.returncode, 0, result.stderr)
                path.write_bytes(original)

    def test_preexisting_model_slot_is_rejected_not_trusted(self):
        code = """
import pathlib, runpy, sys, types
root = pathlib.Path(sys.argv[1])
modules = runpy.run_path(str(root / "cli.py"))["_load_public"]()
s = modules["sequencer"]
sys.modules[s.base.__name__] = types.ModuleType("wrong_bound_code")
try:
    s._load_existing_model()
except RuntimeError as error:
    assert str(error) == "PUBLIC_MODEL_MODULE_COLLISION"
else:
    raise AssertionError("existing model slot trusted")
print("model slot collision refused")
"""
        result = self.run_python("-c", code, self.copy)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_stale_bytecode_cannot_replace_checked_source(self):
        cache = self.copy / "__pycache__"
        cache.mkdir()
        for name in ("model", "sequencer", "scenarios", "_bootstrap"):
            (cache / (name + "." + sys.implementation.cache_tag + ".pyc")).write_bytes(
                b"NOT_ADMITTED_BYTECODE")
        before = tree_hashes(self.work)
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        assert_permissions(self, json.loads(result.stdout))
        self.assertEqual(tree_hashes(self.work), before)
        (self.copy / "model.py").unlink()
        self.assert_refused(self.cli(), "PUBLIC_SOURCE_UNREADABLE:model.py")

    def test_runtime_readset_and_no_writes_network_or_git(self):
        code = """
import argparse, dataclasses, enum, hashlib, json, os, pathlib, runpy
import sys, sysconfig, types
root = pathlib.Path(sys.argv[1]).resolve()
allowed = {root / p for p in json.loads(sys.argv[2])}
stdlib = pathlib.Path(sysconfig.get_path("stdlib")).resolve()
seen = set()
def audit(event, args):
    if event == "open":
        name, mode, flags = args
        if (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
            flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
        ):
            raise AssertionError("RUNTIME_WRITE")
        if isinstance(name, (str, bytes, os.PathLike)):
            path = pathlib.Path(os.fsdecode(name)).resolve()
            if path in allowed:
                seen.add(path)
            elif not path.is_relative_to(stdlib) or "site-packages" in path.parts:
                raise AssertionError("UNBOUND_RUNTIME_READ")
    elif event.startswith(("socket.", "subprocess.")) or event in (
        "os.system", "os.mkdir", "os.remove", "os.rename", "os.rmdir",
        "os.symlink", "os.link", "os.truncate", "os.chmod", "os.utime",
    ):
        raise AssertionError("RUNTIME_SIDE_EFFECT")
sys.addaudithook(audit)
sys.argv = [str(root / "cli.py"), "all"]
runpy.run_path(str(root / "cli.py"), run_name="__main__")
assert seen == allowed, "RUNTIME_READSET_CHANGED"
"""
        before = tree_hashes(self.work)
        result = self.run_python("-c", code, self.copy, json.dumps(RUNTIME_FILES))
        self.assertEqual(result.returncode, 0, result.stderr)
        assert_permissions(self, json.loads(result.stdout))
        self.assertEqual(tree_hashes(self.work), before)

    def test_manifest_matches_exported_bytes_and_no_private_identifiers(self):
        manifest = json.loads((self.copy / "manifest.json").read_text())
        self.assertEqual(set(manifest["public_allowlist"]), set(PUBLIC_FILES))
        indexed = {row["path"]: row for row in manifest["files"]}
        self.assertEqual(set(indexed), set(PUBLIC_FILES) - {"manifest.json"})
        for name, row in indexed.items():
            data = (self.copy / name).read_bytes()
            self.assertEqual(row["sha256"], hashlib.sha256(data).hexdigest(), name)
            self.assertEqual(row["bytes"], len(data), name)
        forbidden = ("/Users/", "/home/", "file://", "localhost", ".copilot/",
                     ".agent-work/", "ghp_", "github_pat_")
        for name in PUBLIC_FILES:
            if name == "test_portability.py":
                continue  # This file spells out the scanner's own deny patterns.
            text = (self.copy / name).read_text()
            for needle in forbidden:
                self.assertNotIn(needle, text, name)
        self.assertEqual(hashlib.sha256((self.copy / "model.py").read_bytes()).hexdigest(),
                         "ce496b2806b21966d68cec789ae85ec5dbdd4cf1eb7762a8d0b29fac172af447")


if __name__ == "__main__":
    unittest.main(verbosity=2)
