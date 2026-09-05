#!/usr/bin/env python3
"""Validate revision-linked assembly evidence, not geometry or safety.

PR mode reuses the hardware gate's merge-base discovery, but does not change
that gate or reinterpret historical revisions. See docs/assembly-evidence.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date

from check_open_issues import REPO_ROOT, compute_pr_changed_files

MANIFEST_DIR = "hardware/mechanical/assembly-evidence/"
DESIGN_PREFIXES = ("hardware/", "bom/", "visualization/assembly-viewer/")
SOURCE_SUFFIXES = {".scad", ".kicad_pcb", ".kicad_sch", ".kicad_pro", ".kicad_mod", ".kicad_sym"}
SOURCE_FILENAMES = {"fp-lib-table", "sym-lib-table"}
ARTIFACTS = frozenset({
    "tool_preflight", "component_map", "assembly_instructions",
    "installed_assembly", "assembly_stages", "drawings",
    "native_animation", "animation_video", "independent_review",
})


class EvidenceError(ValueError):
    """An incomplete or inconsistent evidence contract."""


@dataclass
class Result:
    label: str
    state: str
    covered_paths: set[str]
    source_paths: set[str]
    outstanding: list[str]
    fingerprint: str


def require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceError(message)


def record(value: object, label: str) -> dict:
    require(isinstance(value, dict), f"{label}: expected an object")
    return value


def text(data: dict, key: str, label: str) -> str:
    value = data.get(key)
    require(isinstance(value, str) and bool(value.strip()), f"{label}.{key}: required text")
    return value


def sequence(value: object, label: str) -> list:
    require(isinstance(value, list) and bool(value), f"{label}: expected a nonempty list")
    return value


def unique_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_record(path: pathlib.Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return record(json.load(stream, object_pairs_hook=unique_keys), path.as_posix())


def local_path(root: pathlib.Path, name: str) -> pathlib.Path:
    path = pathlib.PurePosixPath(name)
    require(
        bool(name) and not path.is_absolute() and path.as_posix() == name
        and not set(path.parts).intersection({".", "..", ".git"}),
        f"not a canonical repository-relative path: {name}",
    )
    target = root
    for part in path.parts:
        target = target / part
        require(not target.is_symlink(),
                f"symlink in evidence path: {name} ({target.relative_to(root).as_posix()})")
    require(target.resolve().is_relative_to(root.resolve()), f"path escapes repository: {name}")
    return target


def digest_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_bytes(root: pathlib.Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, timeout=30, check=False,
    )
    require(result.returncode == 0, f"git {' '.join(args)}: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


def commit(root: pathlib.Path, value: object) -> str:
    require(
        isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value) is not None,
        "source_revision: a full commit hash is required",
    )
    require(git_bytes(root, "cat-file", "-t", value).strip() == b"commit", f"{value}: not a commit")
    return value


def file_reference(root: pathlib.Path, value: object, label: str, revision: str | None = None,
                   retired: bool = False) -> str:
    ref = record(value, label)
    name = text(ref, "path", label)
    path = local_path(root, name)
    digest = text(ref, "sha256", label)
    require(re.fullmatch(r"[0-9a-f]{64}", digest) is not None, f"{label}: invalid SHA-256")
    if retired:
        require(not path.exists(), f"{label}: retired source still exists: {name}")
    else:
        require(path.is_file() and path.stat().st_size > 0, f"{label}: missing/empty file: {name}")
        require(digest_file(path) == digest, f"{label}: current file hash mismatch: {name}")
    if revision:
        source = git_bytes(root, "show", f"{revision}:{name}")
        require(hashlib.sha256(source).hexdigest() == digest, f"{label}: source commit hash mismatch: {name}")
    return name


def dated_record(root: pathlib.Path, value: object, label: str) -> dict:
    data = record(value, label)
    text(data, "name", label)
    stamp = text(data, "date", label)
    try:
        date.fromisoformat(stamp)
    except ValueError as exc:
        raise EvidenceError(f"{label}.date: expected an ISO date") from exc
    text(data, "rationale", label)
    ref = record(data.get("record"), f"{label}.record")
    file_reference(root, ref, f"{label}.record")
    text(ref, "section", f"{label}.record")
    return data


def evidence_fingerprint(data: dict) -> str:
    """Bind acceptance to source and outputs, excluding the report itself."""
    evidence = {key: data[key] for key in
                ("assembly", "revision", "author", "source_revision", "sources", "animation")}
    evidence["retired_sources"] = data.get("retired_sources", [])
    evidence["artifacts"] = {key: value for key, value in data["artifacts"].items()
                             if key != "independent_review"}
    return hashlib.sha256(json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_manifest(path: pathlib.Path, root: pathlib.Path = REPO_ROOT,
                      require_approved: bool = False) -> Result:
    relative = path.relative_to(root).as_posix()
    local_path(root, relative)
    data = load_record(path)
    require(type(data.get("schema_version")) is int and data["schema_version"] == 1,
            f"{relative}: schema_version must be 1")
    assembly, revision = (text(data, key, relative) for key in ("assembly", "revision"))
    require(relative == f"{MANIFEST_DIR}{assembly}/{revision}/manifest.json",
            f"{relative}: path must match assembly/revision")
    state = text(data, "state", relative)
    require(state in {"WIP", "APPROVED"}, f"{relative}: state must be WIP or APPROVED")
    author = text(data, "author", relative)
    source_revision = commit(root, data.get("source_revision"))
    sources = sequence(data.get("sources"), f"{relative}.sources")
    covered = {file_reference(root, ref, "sources", source_revision) for ref in sources}
    require(len(covered) == len(sources), "sources: duplicate paths")
    source_paths = set(covered)
    retired = data.get("retired_sources", [])
    require(isinstance(retired, list), "retired_sources: expected a list")
    for item in retired:
        ref = record(item, "retired_sources")
        text(ref, "reason", "retired_sources")
        old_revision = commit(root, ref.get("source_revision"))
        name = file_reference(root, ref, "retired_sources", old_revision, retired=True)
        covered.add(name)
        source_paths.add(name)

    animation = record(data.get("animation"), "animation")
    workflow = text(animation, "workflow", "animation")
    require(workflow in {"FUSION", "APPROVED_ALTERNATIVE"}, "animation.workflow: invalid workflow")
    producer = "Autodesk Fusion Animation"
    if workflow == "APPROVED_ALTERNATIVE":
        alternative = dated_record(root, animation.get("alternative_approval"), "alternative_approval")
        producer = text(alternative, "workflow", "alternative_approval")
    else:
        require(animation.get("alternative_approval") is None, "FUSION cannot contain an alternative approval")

    artifacts = record(data.get("artifacts"), "artifacts")
    require(set(artifacts) == ARTIFACTS,
            f"artifacts: missing {sorted(ARTIFACTS - set(artifacts))}; unknown {sorted(set(artifacts) - ARTIFACTS)}")
    outstanding = []
    for name, value in artifacts.items():
        artifact = record(value, name)
        owner = text(artifact, "owner", name)
        status = text(artifact, "status", name)
        require(status in {"PRESENT", "PENDING", "BLOCKED"}, f"{name}: invalid status {status}")
        if status != "PRESENT":
            require("files" not in artifact, f"{name}: incomplete artifact cannot claim files as PRESENT")
            reason = text(artifact, "reason", name)
            action = text(artifact, "next_action", name)
            outstanding.append(f"{name}: {status}; owner={owner}; {reason}; next={action}")
            continue
        require(artifact.get("source_revision") == source_revision, f"{name}: stale source_revision")
        files = sequence(artifact.get("files"), f"{name}.files")
        names = {file_reference(root, ref, name) for ref in files}
        require(len(names) == len(files), f"{name}: duplicate files")
        covered.update(names)
        if name in {"native_animation", "animation_video"}:
            require(artifact.get("producer") == producer, f"{name}: producer must be {producer}")
            if workflow == "FUSION":
                suffixes = {".f3d", ".f3z"} if name == "native_animation" else {".mp4", ".avi"}
                require(any(pathlib.PurePosixPath(p).suffix.lower() in suffixes for p in names),
                        f"{name}: expected a Fusion {'archive' if name == 'native_animation' else 'published video'}")
    require(relative not in covered, "manifest cannot reference itself")
    fingerprint = evidence_fingerprint(data)
    if state == "APPROVED":
        require(not outstanding, "APPROVED requires every artifact PRESENT: " + "; ".join(outstanding))
        approval = dated_record(root, data.get("approval"), "approval")
        require(approval["name"] != author, "approval: reviewer must be independent of author")
        require(approval.get("role") == "mechanical-reviewer", "approval: mechanical-reviewer role required")
        require(approval.get("verdict") == "PASS", "approval: PASS verdict required")
        require(approval.get("source_revision") == source_revision, "approval: stale source_revision")
        require(approval.get("evidence_sha256") == fingerprint, "approval: stale evidence fingerprint")
        require(artifacts["independent_review"]["owner"] == approval["name"], "approval: reviewer identity mismatch")
        require(
            any(ref["path"] == approval["record"]["path"] and ref["sha256"] == approval["record"]["sha256"]
                for ref in artifacts["independent_review"]["files"]),
            "approval.record must reference the independent_review artifact",
        )
        for gate in ("design_complete", "safety_decisions"):
            ref = record(approval.get(gate), f"approval.{gate}")
            file_reference(root, ref, f"approval.{gate}")
            text(ref, "section", f"approval.{gate}")
    else:
        require(data.get("approval") is None, "WIP cannot claim release approval")
    require(not require_approved or state == "APPROVED", f"{relative}: WIP - NOT ASSEMBLY READY")
    return Result(f"{assembly}/{revision}", state, covered, source_paths, outstanding, fingerprint)


def is_manifest(name: str) -> bool:
    return name.startswith(MANIFEST_DIR) and name.endswith("/manifest.json")


def is_current_pointer(name: str) -> bool:
    return name.startswith(MANIFEST_DIR) and name.endswith("/current.json")


def file_references(value: object) -> list[dict]:
    if isinstance(value, dict):
        refs = [value] if isinstance(value.get("path"), str) else []
        for item in value.values():
            refs.extend(file_references(item))
        return refs
    if isinstance(value, list):
        refs = []
        for item in value:
            refs.extend(file_references(item))
        return refs
    return []


def reference_paths(value: object) -> set[str]:
    return {ref["path"] for ref in file_references(value)}


def current_manifests(root: pathlib.Path) -> dict[str, str]:
    """Explicit current pointers keep old revision evidence out of live checks."""
    current = {}
    for path in sorted((root / MANIFEST_DIR).glob("*/current.json")):
        relative = path.relative_to(root).as_posix()
        local_path(root, relative)
        data = load_record(path)
        require(type(data.get("schema_version")) is int and data["schema_version"] == 1,
                f"{relative}: schema_version must be 1")
        assembly, revision = (text(data, key, relative) for key in ("assembly", "revision"))
        require(relative == f"{MANIFEST_DIR}{assembly}/current.json", f"{relative}: assembly mismatch")
        require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", revision) is not None,
                f"{relative}: revision must be a single directory name")
        manifest = f"{MANIFEST_DIR}{assembly}/{revision}/manifest.json"
        require(local_path(root, manifest).is_file(), f"{relative}: current manifest missing: {manifest}")
        current[relative] = manifest
    return current


def check_changed_files(changed: list[str], root: pathlib.Path = REPO_ROOT,
                        added_files: set[str] | None = None) -> list[Result]:
    changed_set = set(changed)
    manifests = {name for name in changed if is_manifest(name)}
    pointers = {name for name in changed if is_current_pointer(name)}
    physical = {name for name in changed if name.startswith(DESIGN_PREFIXES)} - manifests - pointers
    for name in manifests | pointers:
        require(local_path(root, name).is_file(),
                f"cannot delete a revision manifest/current pointer: {name}; preserve historical evidence")
    current = current_manifests(root)
    require(not pointers - current.keys(), "current pointer must use <assembly>/current.json")
    historical = manifests - set(current.values())
    require(not historical - (added_files or set()),
            "preserve historical revisions unchanged; only new in-PR snapshots may become inactive")
    for name in historical:
        pointer = (pathlib.PurePosixPath(name).parent.parent / "current.json").as_posix()
        require(pointer in current, f"{name}: assembly has no current pointer")
        manifests.add(current[pointer])
        # A PR may create several revisions before merging. Retain the new
        # snapshots' own hash-bound files, but never use an inactive snapshot
        # to cover changes to live design inputs or shared output locations.
        directory = pathlib.PurePosixPath(name).parent.as_posix() + "/"
        for ref in file_references(load_record(root / name)):
            if ref["path"].startswith(directory) and ref["path"] in physical:
                file_reference(root, ref, f"{name}: preserved snapshot")
                physical.remove(ref["path"])
    manifests.difference_update(historical)
    manifests.update(current[name] for name in pointers)
    # Sources, independent reports and gate decisions may live outside the
    # physical path prefixes. Their changes still invalidate the current
    # package; inactive historical revisions deliberately do not participate.
    for name in current.values():
        references = reference_paths(load_record(root / name))
        dependencies = set(references)
        # Validate path identity before comparing literal Git paths; otherwise
        # an ancestor alias can hide target edits or link retargeting as N/A.
        for reference in references:
            local_path(root, reference)
            # Deleted ancestors no longer exist for the symlink preflight.
            dependencies.update(parent.as_posix() for parent in
                                pathlib.PurePosixPath(reference).parents if parent.parts)
        if dependencies & changed_set:
            manifests.add(name)
    if not physical and not manifests:
        return []
    require(bool(manifests), "assembly-affecting changes require an updated revision manifest")
    results = [validate_manifest(local_path(root, name), root) for name in sorted(manifests)]
    covered = set().union(*(result.covered_paths for result in results))
    require(not physical - covered, "changed paths lack source/artifact/retirement linkage: " + ", ".join(sorted(physical - covered)))
    inputs = {name for name in physical if pathlib.PurePosixPath(name).suffix in SOURCE_SUFFIXES
              or pathlib.PurePosixPath(name).name in SOURCE_FILENAMES
              or name.startswith("bom/") or name == "hardware/mechanical-interface.md"}
    sources = set().union(*(result.source_paths for result in results))
    require(not inputs - sources, "design inputs must be linked as sources, not only artifacts: " + ", ".join(sorted(inputs - sources)))
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", help="Validate one current revision, not historical records")
    parser.add_argument("--require-approved", action="store_true", help="Reject WIP; still not a safety certification")
    args = parser.parse_args(argv)
    if args.require_approved and not args.manifest:
        parser.error("--require-approved needs --manifest")
    try:
        if args.manifest:
            results = [validate_manifest(local_path(REPO_ROOT, args.manifest), REPO_ROOT, args.require_approved)]
        else:
            diff = compute_pr_changed_files()
            require(diff is not None, "no reliable PR diff; supply PR event/SHAs or --manifest (no automatic exemption)")
            # Keep both sides of renames and literal filenames; the shared
            # helper establishes the merge-base but its name-only list may
            # collapse renames or quote filenames containing special characters.
            names = git_bytes(REPO_ROOT, "diff", "--name-status", "--no-renames", "-z", diff[0], diff[1])
            fields = names.decode("utf-8").split("\0")
            require(fields[-1] == "" and len(fields[:-1]) % 2 == 0, "unexpected git name-status output")
            entries = list(zip(fields[0:-1:2], fields[1:-1:2]))
            changed = [name for _, name in entries]
            added = {name for status, name in entries if status == "A"}
            results = check_changed_files(changed, REPO_ROOT, added)
        if not results:
            print("Assembly evidence: NOT APPLICABLE - no assembly or current dependency changes; no historical retrofit.")
        for result in results:
            status = "WIP - NOT ASSEMBLY READY" if result.state == "WIP" else "APPROVED record linked"
            print(f"Assembly evidence: {result.label}: {status}")
            print(f"  evidence_sha256={result.fingerprint}")
            for item in result.outstanding:
                print(f"  {item}")
        print("Structural/provenance check only; does not certify geometry, playback, strength, safety or functionality.")
        return 0
    except (EvidenceError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Assembly evidence FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
