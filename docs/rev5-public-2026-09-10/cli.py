"""Read-only JSON CLI. Exit 0 means scenario assertions held, never permission."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


BOOTSTRAP_SHA256 = "08e87f4bb05fcd74d56f6f574f880cf320416a9b0454a896b4e78b57357fa25b"


def _load_public():
    path = Path(__file__).resolve().with_name("_bootstrap.py")
    if path.is_symlink():
        raise RuntimeError("PUBLIC_BOOTSTRAP_SYMLINK")
    try:
        data = path.read_bytes()
    except OSError:
        raise RuntimeError("PUBLIC_BOOTSTRAP_UNREADABLE") from None
    if hashlib.sha256(data).hexdigest() != BOOTSTRAP_SHA256:
        raise RuntimeError("PUBLIC_BOOTSTRAP_MISMATCH")
    namespace = {"__file__": str(path), "__name__": "_rev5_public_bootstrap"}
    exec(compile(data, "_bootstrap.py", "exec"), namespace)
    return namespace["load"]()


def main():
    modules = _load_public()
    check_bindings = modules["sequencer"].check_bindings
    SCENARIOS = modules["scenarios"].SCENARIOS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", choices=tuple(SCENARIOS) + ("all",))
    args = parser.parse_args()
    bindings = check_bindings()
    names = SCENARIOS if args.scenario == "all" else (args.scenario,)
    print(json.dumps({
        "schema_version": 1,
        "status": "NOT_INDEPENDENTLY_REVIEWED",
        "execution_scope": "PUBLIC_DERIVATIVE_CURRENT_EXECUTION",
        "source_bindings": bindings,
        "host_only": True, "actual_operation_permission": False,
        "actual_bus_permission": False,
        "physical_disconnection_established": False,
        "scenarios": [SCENARIOS[name]() for name in names],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2) from None
