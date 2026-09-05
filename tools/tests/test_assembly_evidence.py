"""Synthetic contract fixtures only; no real design or safety evidence."""
import copy
import contextlib
import hashlib
import io
import json
import pathlib
import subprocess
import tempfile
import unittest
from unittest import mock

import check_assembly_evidence as checker
import check_open_issues as hardware_gate


class AssemblyEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.git("init", "-q")
        self.source = "hardware/mechanical/example.scad"
        source_ref = self.file(self.source, "synthetic geometry fixture\n")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Synthetic source snapshot")
        self.sha = self.git("rev-parse", "HEAD").strip()
        self.path = self.root / checker.MANIFEST_DIR / "example/rev1/manifest.json"
        self.data = {
            "schema_version": 1, "assembly": "example", "revision": "rev1",
            "state": "WIP", "author": "mechanical-lead:fixture", "source_revision": self.sha,
            "sources": [source_ref], "retired_sources": [],
            "animation": {"workflow": "FUSION", "alternative_approval": None},
            "artifacts": {
                name: {"status": "PENDING", "owner": "mechanical-lead:fixture",
                       "reason": "Not generated", "next_action": "Generate for this source snapshot"}
                for name in checker.ARTIFACTS
            },
            "approval": None,
        }

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              capture_output=True, text=True).stdout

    def file(self, name, contents):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
        return {"path": name, "sha256": hashlib.sha256(contents.encode()).hexdigest()}

    def write_manifest(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data), encoding="utf-8")
        pointer = self.path.parent.parent / "current.json"
        pointer.write_text(json.dumps({
            "schema_version": 1, "assembly": self.data["assembly"], "revision": self.data["revision"],
        }), encoding="utf-8")
        return self.path

    def validate(self, require_approved=False):
        return checker.validate_manifest(self.write_manifest(), self.root, require_approved)

    def present(self, name, suffix=".md"):
        ref = self.file(f"{self.path.parent.relative_to(self.root)}/{name}{suffix}", "synthetic evidence fixture\n")
        self.data["artifacts"][name] = {
            "status": "PRESENT", "owner": "mechanical-lead:fixture",
            "source_revision": self.sha, "files": [ref],
        }
        if name in {"native_animation", "animation_video"}:
            self.data["artifacts"][name]["producer"] = "Autodesk Fusion Animation"

    def approve(self):
        for name in checker.ARTIFACTS:
            suffix = {"native_animation": ".f3d", "animation_video": ".mp4"}.get(name, ".md")
            self.present(name, suffix)
        gate = self.file("validation/fixture-gates.md", "Synthetic gate record, NOT real approval\n")
        gate["section"] = "Fixture decisions"
        review = copy.deepcopy(self.data["artifacts"]["independent_review"]["files"][0])
        review["section"] = "Fixture review"
        self.data["artifacts"]["independent_review"]["owner"] = "reviewer:fixture"
        self.data["state"] = "APPROVED"
        self.data["approval"] = {
            "name": "reviewer:fixture", "role": "mechanical-reviewer", "date": "2026-09-05",
            "rationale": "Synthetic positive fixture", "record": review, "verdict": "PASS",
            "source_revision": self.sha, "design_complete": gate, "safety_decisions": gate,
            "evidence_sha256": checker.evidence_fingerprint(self.data),
        }

    def commit_fixture(self, message):
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", message)
        return self.git("rev-parse", "HEAD").strip()

    def run_pr(self, base, head):
        output, errors = io.StringIO(), io.StringIO()
        with mock.patch.dict("os.environ", {"GITHUB_EVENT_NAME": "pull_request",
                                          "PR_BASE_SHA": base, "PR_HEAD_SHA": head}), \
                mock.patch.object(checker, "REPO_ROOT", self.root), \
                mock.patch.object(hardware_gate, "REPO_ROOT", self.root), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = checker.main([])
        return status, output.getvalue(), errors.getvalue()

    def test_wip_reports_blocker_but_cannot_claim_readiness(self):
        self.data["artifacts"]["native_animation"]["status"] = "BLOCKED"
        result = self.validate()
        self.assertEqual(result.state, "WIP")
        self.assertEqual(len(result.outstanding), len(checker.ARTIFACTS))
        self.assertTrue(any("native_animation: BLOCKED" in item for item in result.outstanding))
        with self.assertRaisesRegex(checker.EvidenceError, "NOT ASSEMBLY READY"):
            self.validate(require_approved=True)

    def test_complete_approved_contract(self):
        self.approve()
        self.assertEqual(self.validate(require_approved=True).state, "APPROVED")

    def test_reexport_invalidates_acceptance_even_for_same_source_commit(self):
        self.approve()
        artifact = self.data["artifacts"]["native_animation"]
        artifact["files"][0] = self.file(artifact["files"][0]["path"], "different synthetic archive\n")
        with self.assertRaisesRegex(checker.EvidenceError, "stale evidence fingerprint"):
            self.validate()

    def test_approval_must_link_the_independent_report(self):
        self.approve()
        self.data["approval"]["record"] = self.data["approval"]["design_complete"]
        with self.assertRaisesRegex(checker.EvidenceError, "independent_review artifact"):
            self.validate()

    def test_missing_artifact_status_or_action_is_rejected(self):
        original = copy.deepcopy(self.data)
        for field, pattern in (("status", "required text"), ("owner", "required text"),
                               ("next_action", "required text")):
            with self.subTest(field=field):
                self.data = copy.deepcopy(original)
                del self.data["artifacts"]["native_animation"][field]
                with self.assertRaisesRegex(checker.EvidenceError, pattern):
                    self.validate()
        self.data = copy.deepcopy(original)
        del self.data["artifacts"]["native_animation"]
        with self.assertRaisesRegex(checker.EvidenceError, "artifacts: missing"):
            self.validate()

    def test_unrecognized_status_is_rejected(self):
        self.data["artifacts"]["animation_video"]["status"] = "looks fine"
        with self.assertRaisesRegex(checker.EvidenceError, "invalid status"):
            self.validate()

    def test_source_commit_must_match_current_source(self):
        self.data["sources"][0] = self.file(self.source, "changed source without snapshot\n")
        with self.assertRaisesRegex(checker.EvidenceError, "source commit hash mismatch"):
            self.validate()

    def test_missing_source_commit_is_rejected(self):
        self.data["source_revision"] = "0" * 40
        with self.assertRaisesRegex(checker.EvidenceError, "git cat-file"):
            self.validate()

    def test_artifact_revision_and_hash_are_checked(self):
        self.present("component_map")
        artifact = self.data["artifacts"]["component_map"]
        artifact["source_revision"] = "0" * 40
        with self.assertRaisesRegex(checker.EvidenceError, "stale source_revision"):
            self.validate()
        artifact["source_revision"] = self.sha
        artifact["files"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(checker.EvidenceError, "current file hash mismatch"):
            self.validate()
        (self.root / artifact["files"][0]["path"]).unlink()
        with self.assertRaisesRegex(checker.EvidenceError, "missing/empty file"):
            self.validate()

    def test_fusion_cannot_be_satisfied_with_another_renderer_or_still(self):
        for name, suffix in (("native_animation", ".blend"), ("animation_video", ".png")):
            with self.subTest(name=name):
                self.present(name, suffix)
                with self.assertRaisesRegex(checker.EvidenceError, "expected a Fusion"):
                    self.validate()
                self.data["artifacts"][name]["producer"] = "Blender"
                with self.assertRaisesRegex(checker.EvidenceError, "producer must be"):
                    self.validate()
                self.data["artifacts"][name] = {
                    "status": "BLOCKED", "owner": "mechanical-lead:fixture",
                    "reason": "Fusion capability missing", "next_action": "Prepare supported UI handoff",
                }

    def test_alternative_requires_named_recorded_human_decision(self):
        self.data["animation"]["workflow"] = "APPROVED_ALTERNATIVE"
        with self.assertRaisesRegex(checker.EvidenceError, "alternative_approval"):
            self.validate()
        decision = self.file("docs/fixture-decision.md", "Synthetic alternative approval\n")
        decision["section"] = "Explicit workflow choice"
        self.data["animation"]["alternative_approval"] = {
            "name": "Human fixture", "date": "2026-09-05", "rationale": "Explicit alternative",
            "workflow": "Blender", "record": decision,
        }
        self.present("native_animation", ".blend")
        self.data["artifacts"]["native_animation"]["producer"] = "Blender"
        self.assertEqual(self.validate().state, "WIP")

    def test_approval_cannot_hide_missing_evidence_or_self_review(self):
        self.data["state"] = "APPROVED"
        with self.assertRaisesRegex(checker.EvidenceError, "every artifact PRESENT"):
            self.validate()
        self.approve()
        self.data["approval"]["name"] = self.data["author"]
        with self.assertRaisesRegex(checker.EvidenceError, "independent"):
            self.validate()
        self.data["approval"]["name"] = "reviewer:fixture"
        del self.data["approval"]["safety_decisions"]
        with self.assertRaisesRegex(checker.EvidenceError, "safety_decisions"):
            self.validate()

    def test_revision_path_mismatch_and_duplicate_json_keys_fail(self):
        self.data["revision"] = "rev2"
        with self.assertRaisesRegex(checker.EvidenceError, "path must match"):
            self.validate()
        self.data["revision"] = "rev1"
        self.write_manifest()
        self.path.write_text('{"state":"WIP","state":"APPROVED"}', encoding="utf-8")
        with self.assertRaisesRegex(checker.EvidenceError, "duplicate JSON key"):
            checker.validate_manifest(self.path, self.root)

    def test_file_references_cannot_escape_repository(self):
        self.data["sources"][0]["path"] = "../outside.scad"
        with self.assertRaisesRegex(checker.EvidenceError, "repository-relative"):
            self.validate()

    def test_policy_only_diff_is_exempt_without_historical_retrofit(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("historical format intentionally not migrated", encoding="utf-8")
        self.assertEqual(checker.check_changed_files(
            ["docs/workflow.md", ".github/agents/mechanical-lead.agent.md",
             "tools/check_assembly_evidence.py"], self.root), [])

    def test_physical_change_requires_updated_linked_manifest(self):
        with self.assertRaisesRegex(checker.EvidenceError, "require an updated revision manifest"):
            checker.check_changed_files([self.source], self.root)
        self.write_manifest()
        manifest = self.path.relative_to(self.root).as_posix()
        self.assertEqual(len(checker.check_changed_files([self.source, manifest], self.root)), 1)
        with self.assertRaisesRegex(checker.EvidenceError, "lack source/artifact/retirement linkage"):
            checker.check_changed_files([manifest, "bom/unlinked.csv"], self.root)

    def test_external_current_dependency_change_is_not_exempt(self):
        self.approve()
        review = self.file("validation/fixture-review.md", "Synthetic review outside assembly directory\n")
        self.data["artifacts"]["independent_review"]["files"] = [review]
        self.data["approval"]["record"] = dict(review, section="Fixture review")
        self.write_manifest()
        for name in (review["path"], self.data["approval"]["design_complete"]["path"], self.source):
            path = self.root / name
            original = path.read_text(encoding="utf-8")
            with self.subTest(path=name):
                path.write_text(original + "changed\n", encoding="utf-8")
                with self.assertRaisesRegex(checker.EvidenceError, "current file hash mismatch"):
                    checker.check_changed_files([name], self.root)
                path.unlink()
                with self.assertRaisesRegex(checker.EvidenceError, "missing/empty file"):
                    checker.check_changed_files([name], self.root)
                path.write_text(original, encoding="utf-8")

    def symlink_report_fixture(self):
        self.approve()
        actual = "validation/reports/independent-review.md"
        report = self.file(actual, "Synthetic current report\n")
        self.data["artifacts"]["independent_review"]["files"] = [report]
        self.data["approval"]["record"] = dict(report, section="Synthetic report")
        self.assertEqual(self.validate(require_approved=True).state, "APPROVED")
        link = self.root / "validation/report-link"
        link.symlink_to("reports", target_is_directory=True)
        alias = dict(report, path="validation/report-link/independent-review.md")
        self.data["artifacts"]["independent_review"]["files"] = [alias]
        self.data["approval"]["record"] = dict(alias, section="Synthetic report")
        self.write_manifest()
        base = self.commit_fixture("Legacy current package with directory-symlink reference")
        return base, actual, link

    def test_real_pr_report_target_edit_cannot_hide_behind_parent_symlink(self):
        base, actual, _ = self.symlink_report_fixture()
        self.file(actual, "Changed actual report without refreshing the manifest\n")
        head = self.commit_fixture("Edit only the tracked report target")
        self.assertEqual(self.git("diff", "--name-only", base, head).strip(), actual)
        status, output, errors = self.run_pr(base, head)
        self.assertEqual(status, 1, output + errors)
        self.assertIn("symlink", errors)
        self.assertNotIn("NOT APPLICABLE", output)

    def test_real_pr_ancestor_symlink_retarget_cannot_receive_exemption(self):
        base, _, link = self.symlink_report_fixture()
        self.file("validation/other-reports/independent-review.md", "Different report\n")
        base = self.commit_fixture("Preexisting alternative report target")
        link.unlink()
        link.symlink_to("other-reports", target_is_directory=True)
        head = self.commit_fixture("Retarget only the tracked directory symlink")
        self.assertEqual(self.git("diff", "--name-only", base, head).strip(), "validation/report-link")
        status, output, errors = self.run_pr(base, head)
        self.assertEqual(status, 1, output + errors)
        self.assertIn("symlink", errors)
        self.assertNotIn("NOT APPLICABLE", output)

    def test_real_pr_ancestor_symlink_deletion_cannot_receive_exemption(self):
        base, _, link = self.symlink_report_fixture()
        link.unlink()
        head = self.commit_fixture("Delete only the current report's ancestor symlink")
        self.assertEqual(self.git("diff", "--name-status", base, head).strip(),
                         "D\tvalidation/report-link")
        status, output, errors = self.run_pr(base, head)
        self.assertEqual(status, 1, output + errors)
        self.assertIn("independent_review: missing/empty file: validation/report-link/independent-review.md",
                      errors)
        self.assertNotIn("NOT APPLICABLE", output)

    def test_real_pr_unrelated_prefix_sibling_does_not_select_current_evidence(self):
        self.approve()
        report = self.file("validation/reports/current.md", "Synthetic canonical current report\n")
        self.data["artifacts"]["independent_review"]["files"] = [report]
        self.data["approval"]["record"] = dict(report, section="Synthetic report")
        self.assertEqual(self.validate(require_approved=True).state, "APPROVED")
        base = self.commit_fixture("Canonical current evidence baseline")
        self.file("validation/report", "This path is a string prefix, not a path ancestor\n")
        head = self.commit_fixture("Add unrelated neighboring report path")
        with mock.patch.object(checker, "validate_manifest",
                               side_effect=AssertionError("Unrelated current evidence was selected")), \
                mock.patch.object(checker, "digest_file",
                                  side_effect=AssertionError("Unrelated current evidence was hashed")):
            status, output, errors = self.run_pr(base, head)
        self.assertEqual(status, 0, output + errors)
        self.assertIn("NOT APPLICABLE", output)

    def test_current_reference_paths_are_validated_before_unrelated_diff_exemption(self):
        self.approve()
        original = copy.deepcopy(self.data)
        report = self.file("validation/reports/shared.md", "Synthetic source/report/gate\n")
        (self.root / "validation/report-link").symlink_to("reports", target_is_directory=True)
        for dependency in ("source", "artifact", "gate"):
            for path in ("validation/report-link/shared.md", "validation/reports/../reports/shared.md"):
                with self.subTest(dependency=dependency, path=path):
                    self.data = copy.deepcopy(original)
                    ref = dict(report, path=path)
                    if dependency == "source":
                        self.data["sources"].append(ref)
                    elif dependency == "artifact":
                        self.data["artifacts"]["independent_review"]["files"] = [ref]
                    else:
                        self.data["approval"]["design_complete"] = dict(ref, section="Synthetic gate")
                    self.write_manifest()
                    with self.assertRaisesRegex(checker.EvidenceError, "symlink|repository-relative"):
                        checker.check_changed_files(["docs/unrelated.md"], self.root)

    def test_local_path_rejects_parent_terminal_and_dangling_symlinks(self):
        self.file("validation/reports/report.md", "Synthetic report\n")
        (self.root / "validation/directory-link").symlink_to("reports", target_is_directory=True)
        (self.root / "validation/file-link.md").symlink_to("reports/report.md")
        (self.root / "validation/dangling").symlink_to("missing", target_is_directory=True)
        for name in ("validation/directory-link/report.md", "validation/file-link.md",
                     "validation/dangling/report.md"):
            with self.subTest(path=name):
                with self.assertRaisesRegex(checker.EvidenceError, "symlink"):
                    checker.local_path(self.root, name)
        self.assertEqual(checker.local_path(self.root, "validation/reports/report.md"),
                         self.root / "validation/reports/report.md")

    def test_valid_current_package_still_allows_unrelated_documentation_exemption(self):
        self.approve()
        self.assertEqual(self.validate(require_approved=True).state, "APPROVED")
        self.assertEqual(checker.check_changed_files(["docs/unrelated.md"], self.root), [])

    def test_refreshed_external_report_is_checked_without_hardware_changes(self):
        self.present("independent_review")
        review = self.file("validation/current-review.md", "Refreshed synthetic WIP blocker report\n")
        self.data["artifacts"]["independent_review"]["files"] = [review]
        self.write_manifest()
        results = checker.check_changed_files([review["path"]], self.root)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].state, "WIP")

    def test_external_source_change_is_not_exempt(self):
        extra = self.file("requirements/fixture.md", "Synthetic source requirement\n")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Add requirement fixture")
        self.data["source_revision"] = self.git("rev-parse", "HEAD").strip()
        self.data["sources"].append(extra)
        self.write_manifest()
        self.file(extra["path"], "changed requirement fixture\n")
        with self.assertRaisesRegex(checker.EvidenceError, "current file hash mismatch"):
            checker.check_changed_files([extra["path"]], self.root)

    def test_current_pointer_requires_existing_manifest_and_cannot_be_deleted(self):
        self.write_manifest()
        pointer = self.path.parent.parent / "current.json"
        self.path.unlink()
        with self.assertRaisesRegex(checker.EvidenceError, "current manifest missing"):
            checker.check_changed_files([pointer.relative_to(self.root).as_posix()], self.root)
        pointer.unlink()
        with self.assertRaisesRegex(checker.EvidenceError, "cannot delete a revision manifest/current pointer"):
            checker.check_changed_files([pointer.relative_to(self.root).as_posix()], self.root)

    def test_historical_dependencies_do_not_force_retrofit(self):
        self.approve()
        old = self.file("validation/old-report.md", "Historical review fixture\n")
        self.data["artifacts"]["independent_review"]["files"] = [old]
        self.data["approval"]["record"] = dict(old, section="Old review")
        self.write_manifest()
        historical_path = self.path
        historical_bytes = self.path.read_bytes()
        self.data["revision"] = "rev2"
        self.path = self.path.parent.parent / "rev2/manifest.json"
        self.approve()
        self.write_manifest()
        self.file(old["path"], "Edited historical-only report\n")
        self.assertEqual(checker.check_changed_files([old["path"], "docs/unrelated.md"], self.root), [])
        self.assertEqual(historical_path.read_bytes(), historical_bytes)
        with self.assertRaisesRegex(checker.EvidenceError, "preserve historical revisions unchanged"):
            checker.check_changed_files([historical_path.relative_to(self.root).as_posix()], self.root)

    def test_kicad_library_inputs_require_committed_source_linkage(self):
        for name in ("hardware/pcb/example.pretty/part.kicad_mod",
                     "hardware/schematic/example.kicad_sym",
                     "hardware/pcb/fp-lib-table", "hardware/schematic/sym-lib-table"):
            with self.subTest(path=name):
                extra = self.file(name, "changed library fixture absent from source snapshot\n")
                self.data["artifacts"]["component_map"] = {
                    "status": "PRESENT", "owner": "mechanical-lead:fixture",
                    "source_revision": self.sha, "files": [extra],
                }
                self.write_manifest()
                changed = [name, self.path.relative_to(self.root).as_posix()]
                with self.assertRaisesRegex(checker.EvidenceError, "design inputs must be linked as sources"):
                    checker.check_changed_files(changed, self.root)
                self.data["sources"].append(extra)
                with self.assertRaisesRegex(checker.EvidenceError, "git show"):
                    self.validate()
                self.git("add", "--", name)
                self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                         "commit", "-qm", "Commit library source fixture")
                self.sha = self.git("rev-parse", "HEAD").strip()
                self.data["source_revision"] = self.sha
                self.data["artifacts"]["component_map"]["source_revision"] = self.sha
                self.write_manifest()
                self.assertEqual(len(checker.check_changed_files(changed, self.root)), 1)
                self.data["sources"].pop()

    def test_source_cannot_be_hidden_in_an_artifact_record(self):
        extra = self.file("hardware/mechanical/second.scad", "second source fixture\n")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Add synthetic input")
        self.data["source_revision"] = self.git("rev-parse", "HEAD").strip()
        self.data["artifacts"]["component_map"] = {
            "status": "PRESENT", "owner": "mechanical-lead:fixture",
            "source_revision": self.data["source_revision"], "files": [extra],
        }
        self.write_manifest()
        with self.assertRaisesRegex(checker.EvidenceError, "design inputs must be linked as sources"):
            checker.check_changed_files(
                [extra["path"], self.path.relative_to(self.root).as_posix()], self.root)

    def test_manifest_deletion_is_not_an_exemption(self):
        with self.assertRaisesRegex(checker.EvidenceError, "cannot delete a revision manifest/current pointer"):
            checker.check_changed_files([self.path.relative_to(self.root).as_posix()], self.root)

    def test_source_retirement_keeps_old_provenance(self):
        old = dict(self.data["sources"][0], source_revision=self.sha, reason="Replaced by new source")
        (self.root / self.source).unlink()
        new = self.file("hardware/mechanical/replacement.scad", "replacement fixture\n")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Replace synthetic source")
        self.data["source_revision"] = self.git("rev-parse", "HEAD").strip()
        self.data["sources"] = [new]
        self.data["retired_sources"] = [old]
        self.write_manifest()
        changed = [self.source, new["path"], self.path.relative_to(self.root).as_posix()]
        self.assertEqual(len(checker.check_changed_files(changed, self.root)), 1)
        self.data["retired_sources"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(checker.EvidenceError, "source commit hash mismatch"):
            self.validate()

    def test_missing_diff_context_fails_closed(self):
        with mock.patch.object(checker, "compute_pr_changed_files", return_value=None), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(checker.main([]), 1)

    def test_real_pr_diff_preserves_manifest_rename_deletion(self):
        self.write_manifest()
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Add synthetic manifest")
        base = self.git("rev-parse", "HEAD").strip()
        old_name = self.path.relative_to(self.root).as_posix()
        self.data["revision"] = "rev2"
        self.path.unlink()
        self.path = self.path.parent.parent / "rev2/manifest.json"
        self.write_manifest()
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Rename synthetic manifest")
        head = self.git("rev-parse", "HEAD").strip()
        errors = io.StringIO()
        with mock.patch.dict("os.environ", {"GITHUB_EVENT_NAME": "pull_request",
                                          "PR_BASE_SHA": base, "PR_HEAD_SHA": head}), \
                mock.patch.object(checker, "REPO_ROOT", self.root), \
                mock.patch.object(hardware_gate, "REPO_ROOT", self.root), \
                contextlib.redirect_stderr(errors):
            self.assertEqual(checker.main([]), 1)
        self.assertIn("cannot delete a revision manifest/current pointer: " + old_name, errors.getvalue())

    def test_real_pr_diff_preserves_two_new_revision_snapshots(self):
        base = self.sha
        self.present("component_map")
        self.write_manifest()
        old_manifest = self.path.relative_to(self.root).as_posix()
        old_file = self.data["artifacts"]["component_map"]["files"][0]["path"]
        old_bytes = self.path.read_bytes()
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Record first WIP snapshot")
        source_ref = self.file(self.source, "revised geometry fixture\n")
        self.git("add", "--", self.source)
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Commit second source snapshot")
        self.sha = self.git("rev-parse", "HEAD").strip()
        self.data["source_revision"] = self.sha
        self.data["sources"] = [source_ref]
        self.data["revision"] = "rev2"
        self.path = self.path.parent.parent / "rev2/manifest.json"
        self.present("component_map")
        self.write_manifest()
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Record second WIP snapshot")
        head = self.git("rev-parse", "HEAD").strip()
        output = io.StringIO()
        with mock.patch.dict("os.environ", {"GITHUB_EVENT_NAME": "pull_request",
                                          "PR_BASE_SHA": base, "PR_HEAD_SHA": head}), \
                mock.patch.object(checker, "REPO_ROOT", self.root), \
                mock.patch.object(hardware_gate, "REPO_ROOT", self.root), \
                contextlib.redirect_stdout(output):
            self.assertEqual(checker.main([]), 0)
        self.assertIn("example/rev2: WIP - NOT ASSEMBLY READY", output.getvalue())
        self.assertNotIn("example/rev1:", output.getvalue())
        self.assertEqual((self.root / old_manifest).read_bytes(), old_bytes)
        self.file(old_file, "not the preserved output\n")
        with self.assertRaisesRegex(checker.EvidenceError, "current file hash mismatch"):
            checker.check_changed_files(
                [old_manifest, old_file, self.path.relative_to(self.root).as_posix()], self.root,
                added_files={old_manifest})

    def test_inactive_snapshot_cannot_cover_live_input_changes(self):
        self.present("component_map")
        self.write_manifest()
        old_manifest = self.path.relative_to(self.root).as_posix()
        old_source = self.source
        new_source = self.file("hardware/mechanical/new.scad", "new current source fixture\n")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Commit second source")
        self.sha = self.git("rev-parse", "HEAD").strip()
        self.data["source_revision"] = self.sha
        self.data["sources"] = [new_source]
        self.data["revision"] = "rev2"
        self.path = self.path.parent.parent / "rev2/manifest.json"
        self.present("component_map")
        self.write_manifest()
        with self.assertRaisesRegex(checker.EvidenceError, "lack source/artifact/retirement linkage"):
            checker.check_changed_files(
                [old_manifest, old_source, self.path.relative_to(self.root).as_posix()], self.root,
                added_files={old_manifest})

    def test_evidence_only_pr_cannot_omit_its_assembly_pointer(self):
        base = self.sha
        self.present("component_map")
        self.data["state"] = "APPROVED"
        self.write_manifest()
        (self.path.parent.parent / "current.json").unlink()
        # A different assembly's registration must not exempt this one.
        other = copy.deepcopy(self.data)
        other.update(assembly="other", state="WIP", approval=None)
        self.file(f"{checker.MANIFEST_DIR}other/rev1/manifest.json", json.dumps(other))
        self.file(f"{checker.MANIFEST_DIR}other/current.json", json.dumps({
            "schema_version": 1, "assembly": "other", "revision": "rev1",
        }))
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Evidence-only PR with missing registration")
        head = self.git("rev-parse", "HEAD").strip()
        errors = io.StringIO()
        output = io.StringIO()
        with mock.patch.dict("os.environ", {"GITHUB_EVENT_NAME": "pull_request",
                                          "PR_BASE_SHA": base, "PR_HEAD_SHA": head}), \
                mock.patch.object(checker, "REPO_ROOT", self.root), \
                mock.patch.object(hardware_gate, "REPO_ROOT", self.root), \
                contextlib.redirect_stderr(errors), contextlib.redirect_stdout(output):
            self.assertEqual(checker.main([]), 1)
        self.assertIn("example/rev1/manifest.json: assembly has no current pointer", errors.getvalue())
        self.assertNotIn("NOT APPLICABLE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
