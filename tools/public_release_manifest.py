"""Validate current files against a preserved release and explicit continuation."""

import hashlib
import json
from pathlib import PurePosixPath


CONTINUATION = "docs/rev5-public-release/software-continuation.json"


def current_file_record(root, manifest_path, original):
    record = json.loads((root / CONTINUATION).read_text(encoding="utf-8"))
    if record["record_type"] != "PUBLIC_SOFTWARE_CONTINUATION":
        raise ValueError("Unsupported public release continuation")
    manifest_hash = hashlib.sha256((root / manifest_path).read_bytes()).hexdigest()
    if record["historical_manifests"].get(manifest_path) != manifest_hash:
        raise ValueError(f"Historical manifest changed: {manifest_path}")
    replacements = {}
    for entry in record["files"]:
        name = entry["path"]
        path = PurePosixPath(name)
        if (path.is_absolute() or path.as_posix() != name
                or {"..", ".git", ".agent-work"} & set(path.parts)):
            raise ValueError(f"Unsafe continuation path: {name}")
        if name in replacements:
            raise ValueError(f"Duplicate continuation path: {name}")
        replacements[name] = entry
    replacement = replacements.get(original["path"])
    if replacement is None:
        return original
    if replacement["supersedes"].get(manifest_path) != original["sha256"]:
        raise ValueError(f"Unbound historical file: {original['path']}")
    return replacement
