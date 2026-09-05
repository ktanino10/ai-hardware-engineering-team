"""Optional compiled CERN ROOT export; never installs or repairs global ROOT."""

import argparse
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cube_sim.model import ROOT
from cube_sim.runner import sha256, write_json
from cube_sim.visualize import verify_current


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.run, args.output = args.run.resolve(), args.output.resolve()
    manifest, values = verify_current(args.run)
    root_config, compiler = shutil.which("root-config"), shutil.which("c++")
    if root_config is None or compiler is None:
        raise RuntimeError("Optional CERN ROOT export requires existing root-config and C++; no global installation attempted.")
    args.output.mkdir(parents=True, exist_ok=False)
    build = ROOT / "runs/root-build"
    build.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).with_suffix(".cxx")
    executable = build / ("export-" + sha256(source)[:12])
    flags = shlex.split(subprocess.run([root_config, "--cflags", "--libs"], check=True,
                                      capture_output=True, text=True).stdout)
    subprocess.run([compiler, str(source), *flags, "-o", str(executable)], check=True)
    result = subprocess.run([str(executable), str(args.run / "trajectory.csv"),
                             str(args.output / "trajectory.root"), str(args.output / "summary.json")],
                            capture_output=True, text=True, cwd=args.output)
    (args.output / "native-runtime.log").write_text(result.stdout + result.stderr)
    result.check_returncode()
    summary = json.loads((args.output / "summary.json").read_text())
    if summary["rows"] != len(values["time"]) or abs(summary["weighted_seconds"] - values["time"][-1] + values["time"][0]) > 1e-9:
        raise RuntimeError("ROOT round-trip summary disagrees with source trajectory.")
    write_json(args.output / "manifest.json", {
        "state": "WIP_ANALYSIS_INTEROPERABILITY_NOT_A_PHYSICS_ENGINE",
        "source_manifest_sha256": sha256(args.run / "manifest.json"),
        "source_csv_sha256": sha256(args.run / "trajectory.csv"),
        "source_revision": manifest["source_revision"],
        "source_code_dirty": manifest["uncommitted_model_code"],
        "source_code_sha256": manifest["code"],
        "model_case_id": json.loads((args.run / "input.json").read_text())["case_id"],
        "classification": manifest["classification"],
        "adapter_sha256": sha256(__file__), "cpp_sha256": sha256(source),
        "native_tree_status": summary["status"],
        "runtime_diagnostics_present": bool(result.stderr.strip()),
        "interpreter_health": "ERROR_DIAGNOSTICS_PRESENT" if "error:" in result.stderr or "unresolved" in result.stderr else "NOT_TESTED",
        "scope": "Native compiled TTree export/readback and time-weighted descriptive bins. No native graphics, Cling, PyROOT or RDataFrame execution is claimed.",
        "files": {p.name: sha256(p) for p in sorted(args.output.iterdir()) if p.is_file()},
    })
    print(args.output.resolve())


if __name__ == "__main__":
    main()
