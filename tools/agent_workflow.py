#!/usr/bin/env python3
"""Local dispatch guard, not an agent launcher or a design/safety approval gate."""
from __future__ import annotations

import argparse
import contextlib
import datetime
import hashlib
import json
import pathlib
import re
import sqlite3
import subprocess
import sys
import uuid


CONFIG_PATHS = (
    ".github", "docs/architecture.md", "docs/workflow.md",
    "docs/commands/make-circuit.md", "docs/work-execution.md",
    "tools/agent_workflow.py",
)
SHARED_LEDGERS = (
    "datasheets/evidence-log.md", "validation/open-issues.md",
    "validation/design-review.md", "validation/change-log.md",
    "requirements/traceability-matrix.md", "bom/component-selection.md",
)
TEXT_FIELDS = (
    "id", "owner", "objective", "source_revision", "config_revision",
    "done_when", "stop_when",
)
LIST_FIELDS = ("inputs", "writes", "deliverables", "depends_on")
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
COMMIT = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")


class WorkflowError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise WorkflowError(message)


def git(root: pathlib.Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True,
        timeout=30,
    ).stdout.strip()


def repo_path(root: pathlib.Path, value: str) -> pathlib.Path:
    path = pathlib.PurePosixPath(value)
    require(
        bool(path.parts) and not path.is_absolute() and path.as_posix() == value
        and not any(part in {".", "..", ".git"} for part in path.parts)
        and not any(c in value for c in "\\*?[]")
        and not any(ord(c) < 32 for c in value),
        f"invalid repository-relative path: {value!r}",
    )
    target = root / path
    require(target.resolve().is_relative_to(root.resolve()), f"path escapes worktree: {value}")
    return target


def covers(parent: str, child: str) -> bool:
    return pathlib.PurePosixPath(child).is_relative_to(parent)


def overlaps(first: str, second: str) -> bool:
    return covers(first, second) or covers(second, first)


def writes_shared_ledger(data: dict) -> bool:
    return any(overlaps(scope, ledger)
               for scope in data["writes"] for ledger in SHARED_LEDGERS)


def validate_contract(root: pathlib.Path, data: dict) -> dict[str, str]:
    require(isinstance(data, dict), "contract must be an object")
    require(set(data) == {"schema_version", *TEXT_FIELDS, *LIST_FIELDS},
            "contract has missing or unknown fields")
    require(type(data["schema_version"]) is int and data["schema_version"] == 1,
            "unsupported schema_version")
    for key in TEXT_FIELDS:
        require(isinstance(data[key], str) and bool(data[key].strip()),
                f"{key}: required text")
    for key in LIST_FIELDS:
        values = data[key]
        require(isinstance(values, list) and all(isinstance(v, str) and v.strip() for v in values),
                f"{key}: expected a list of nonempty strings")
        require(len(values) == len(set(values)), f"{key}: duplicates")
    require(data["inputs"] and data["deliverables"], "inputs and deliverables must not be empty")
    for value in (data["id"], data["owner"], *data["depends_on"]):
        require(SLUG.fullmatch(value), f"invalid task/owner identifier: {value}")
    require(data["id"] not in data["depends_on"], "a task cannot depend on itself")
    require((root / f".github/agents/{data['owner']}.agent.md").is_file(), "unknown owner role")
    for key in ("source_revision", "config_revision"):
        require(COMMIT.fullmatch(data[key]), f"{key}: use a full immutable commit ID")
        git(root, "rev-parse", "--verify", data[key] + "^{commit}")
    for name in (*data["inputs"], *data["writes"], *data["deliverables"]):
        repo_path(root, name)
    for name in data["deliverables"]:
        require(any(covers(scope, name) for scope in data["writes"]),
                f"deliverable is outside declared writes: {name}")
    if data["owner"] != "hardware-lead":
        require(not writes_shared_ledger(data),
                "shared ledger publication belongs to hardware-lead; return a proposal")
    diff = subprocess.run(
        ["git", "diff", "--quiet", data["config_revision"], "--", *CONFIG_PATHS],
        cwd=root, capture_output=True, text=True, timeout=30,
    )
    if diff.returncode not in (0, 1):
        diff.check_returncode()
    require(diff.returncode == 0 and not git(
        root, "ls-files", "--others", "--exclude-standard", "--", *CONFIG_PATHS
    ), "configuration differs from config_revision; adopt it at a safe boundary")
    inputs = {}
    for name in sorted(data["inputs"]):
        path = repo_path(root, name)
        require(path.is_file() and not path.is_symlink(), f"missing or non-regular input: {name}")
        expected = git(root, "rev-parse", "--verify", f"{data['source_revision']}:{name}")
        require(git(root, "hash-object", "--no-filters", "--", name) == expected,
                f"input differs from source_revision: {name}")
        inputs[name] = expected
    return inputs


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def state_path(root: pathlib.Path) -> pathlib.Path:
    common = git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    return pathlib.Path(common).resolve() / "agent-workflow" / "state.sqlite3"


@contextlib.contextmanager
def database(root: pathlib.Path):
    path = state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with contextlib.closing(sqlite3.connect(path, timeout=10)) as db:
        db.row_factory = sqlite3.Row
        with db:
            db.execute("""CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY, task_id TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('RUNNING', 'DONE', 'BLOCKED')),
                session_id TEXT NOT NULL, worktree TEXT NOT NULL,
                fingerprint TEXT NOT NULL, contract_json TEXT NOT NULL,
                started_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                summary TEXT NOT NULL, next_action TEXT NOT NULL,
                artifacts_json TEXT NOT NULL DEFAULT '[]'
            )""")
            db.execute("BEGIN IMMEDIATE")
            yield db


def artifacts(root: pathlib.Path, names: list[str], required: bool) -> list[dict]:
    result = []
    for name in sorted(names):
        path = repo_path(root, name)
        if not path.exists() and not required:
            continue
        require(path.is_file() and not path.is_symlink(), f"missing deliverable: {name}")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        result.append({"path": name, "sha256": digest.hexdigest()})
    return result


def start(root: pathlib.Path, data: dict, session: str) -> dict:
    require(bool(session.strip()), "session must not be empty")
    with database(root) as db:
        inputs = validate_contract(root, data)
        running = db.execute("SELECT * FROM runs WHERE state = 'RUNNING'").fetchall()
        for row in running:
            require(row["task_id"] != data["id"], f"{data['id']} already RUNNING")
            active = json.loads(row["contract_json"])
            require(not (writes_shared_ledger(data) and writes_shared_ledger(active)),
                    f"shared ledger publisher is busy: {row['task_id']}")
            require(not any(overlaps(a, b) for a in data["writes"] for b in active["writes"]),
                    f"write conflict with {row['task_id']}")
            require(not any(overlaps(a, b) for a in data["writes"] for b in active["inputs"])
                    and not any(overlaps(a, b) for a in active["writes"] for b in data["inputs"]),
                    f"input/write conflict with {row['task_id']}")
        dependencies = {}
        for task in data["depends_on"]:
            row = db.execute(
                "SELECT * FROM runs WHERE task_id = ? ORDER BY rowid DESC LIMIT 1", (task,)
            ).fetchone()
            require(row is not None and row["state"] == "DONE", f"dependency not DONE: {task}")
            recorded = json.loads(row["artifacts_json"])
            actual = artifacts(pathlib.Path(row["worktree"]), [a["path"] for a in recorded], True)
            require(actual == recorded, f"dependency artifacts changed: {task}")
            dependencies[task] = {"fingerprint": row["fingerprint"], "artifacts": actual}
        fingerprint = hashlib.sha256(json.dumps(
            {"inputs": inputs, "dependencies": dependencies}, sort_keys=True
        ).encode()).hexdigest()
        previous = db.execute(
            "SELECT state, summary FROM runs WHERE task_id = ? AND fingerprint = ? "
            "ORDER BY rowid DESC LIMIT 1", (data["id"], fingerprint),
        ).fetchone()
        require(previous is None,
                f"{data['id']}: unchanged inputs already recorded; no redispatch"
                + (f" ({previous['state']}: {previous['summary']})" if previous else ""))
        run_id, timestamp = str(uuid.uuid4()), now()
        db.execute(
            "INSERT INTO runs (run_id, task_id, state, session_id, worktree, fingerprint, "
            "contract_json, started_at, updated_at, summary, next_action) "
            "VALUES (?, ?, 'RUNNING', ?, ?, ?, ?, ?, ?, ?, ?)",
            (run_id, data["id"], session, str(root.resolve()), fingerprint,
             json.dumps(data, sort_keys=True), timestamp, timestamp,
             "Reserved; worker invocation is not yet confirmed", data["objective"]),
        )
        return {"run_id": run_id, "task_id": data["id"], "state": "RUNNING"}


def record(root: pathlib.Path, run_id: str, session: str, state: str,
           summary: str, next_action: str) -> dict:
    require(bool(summary.strip()) and bool(next_action.strip()),
            "summary and next_action must not be empty")
    with database(root) as db:
        row = db.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        require(row is not None, f"unknown run: {run_id}")
        require(row["state"] == "RUNNING", f"{run_id} is not RUNNING")
        require(row["session_id"] == session, "session does not own this run")
        require(pathlib.Path(row["worktree"]) == root.resolve(),
                "record the outcome from the reserved worktree")
        data = json.loads(row["contract_json"])
        saved = artifacts(root, data["deliverables"], state == "DONE") if state != "RUNNING" else []
        db.execute(
            "UPDATE runs SET state = ?, updated_at = ?, summary = ?, next_action = ?, "
            "artifacts_json = ? WHERE run_id = ?",
            (state, now(), summary, next_action, json.dumps(saved), run_id),
        )
        return {"run_id": run_id, "task_id": row["task_id"], "state": state, "artifacts": saved}


def finish(root: pathlib.Path, run_id: str, session: str, state: str,
           summary: str, next_action: str) -> dict:
    require(state in {"DONE", "BLOCKED"}, "finish state must be DONE or BLOCKED, not approval")
    return record(root, run_id, session, state, summary, next_action)


def status(root: pathlib.Path, history: bool = False) -> list[dict]:
    path = state_path(root)
    if not path.exists():
        return []
    with contextlib.closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as db:
        db.row_factory = sqlite3.Row
        query = "SELECT * FROM runs"
        if not history:
            query += " WHERE rowid IN (SELECT MAX(rowid) FROM runs GROUP BY task_id)"
        rows = db.execute(query + " ORDER BY rowid").fetchall()
    result = []
    for row in rows:
        data = json.loads(row["contract_json"])
        result.append({
            "task_id": row["task_id"], "run_id": row["run_id"], "owner": data["owner"],
            "state": row["state"], "session_id": row["session_id"], "worktree": row["worktree"],
            "objective": data["objective"], "summary": row["summary"],
            "next_action": row["next_action"], "depends_on": data["depends_on"],
            "source_revision": data["source_revision"], "config_revision": data["config_revision"],
            "started_at": row["started_at"], "updated_at": row["updated_at"],
            "artifacts": json.loads(row["artifacts_json"]),
        })
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=pathlib.Path, default=pathlib.Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)
    begin = commands.add_parser("start", help="Reserve a task before one worker invocation")
    begin.add_argument("contract", type=pathlib.Path)
    begin.add_argument("--session", required=True, help="Responsible coordinator session ID")
    for name in ("progress", "finish"):
        command = commands.add_parser(name)
        command.add_argument("run_id")
        command.add_argument("--session", required=True)
        command.add_argument("--summary", required=True)
        command.add_argument("--next-action", required=True)
        if name == "finish":
            command.add_argument("--state", choices=("DONE", "BLOCKED"), required=True)
    report = commands.add_parser("status", help="Recorded state, not live worker telemetry")
    report.add_argument("--history", action="store_true")
    args = parser.parse_args(argv)
    try:
        root = pathlib.Path(git(args.repo, "rev-parse", "--show-toplevel")).resolve()
        if args.command == "start":
            data = json.loads(args.contract.read_text(encoding="utf-8"))
            result = start(root, data, args.session)
        elif args.command == "finish":
            result = finish(root, args.run_id, args.session, args.state,
                            args.summary, args.next_action)
        elif args.command == "progress":
            result = record(root, args.run_id, args.session, "RUNNING",
                            args.summary, args.next_action)
        else:
            result = status(root, args.history)
        print(json.dumps({
            "notice": "Local recorded task state only; no design or physical approval.",
            "result": result,
        }, ensure_ascii=False, indent=2))
        return 0
    except (WorkflowError, OSError, sqlite3.Error, json.JSONDecodeError,
            subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        detail = exc.stderr if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        print(f"Workflow refused: {detail}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
