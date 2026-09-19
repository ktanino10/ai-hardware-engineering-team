"""Report saved synthetic six-IMU disagreement without health decisions."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import platform
import sys

from simulation.imu_estimation.schema import InputError, dumps, loads
from .report import analyze, markdown


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def implementation_hashes():
    root = Path(__file__).resolve().parents[2]
    paths = [
        "simulation/imu_estimation/__init__.py",
        "simulation/imu_estimation/estimator.py",
        "simulation/imu_estimation/schema.py",
        "simulation/imu_estimation/math3d.py",
        "simulation/imu_disagreement/__init__.py",
        "simulation/imu_disagreement/report.py",
        "simulation/imu_disagreement/__main__.py",
    ]
    return {p: _sha((root / p).read_bytes()) for p in paths}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--samples", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        config_bytes = args.config.read_bytes()
        sample_bytes = args.samples.read_bytes()
        config = loads(config_bytes.decode("utf-8", errors="strict"))
        report = analyze(config, io.BytesIO(sample_bytes))
        report["provenance"] = {
            "config": {"path": str(args.config), "sha256": _sha(config_bytes)},
            "samples": {"path": str(args.samples), "sha256": _sha(sample_bytes)},
            "implementation_sha256": implementation_hashes(),
            "python": platform.python_version(),
            "time_and_calibration": "Declared synthetic assumptions; not authenticated physical facts.",
        }
        encoded = json.dumps(report, ensure_ascii=True, allow_nan=False, indent=2) + "\n"
        args.output_dir.mkdir(parents=True, exist_ok=False)
        (args.output_dir / "report.json").write_text(encoded, encoding="utf-8")
        (args.output_dir / "report.md").write_text(markdown(report), encoding="utf-8")
        unresolved = bool(report["errors"] or report["summary"]["unresolved_records"])
        print(dumps({"report": str(args.output_dir / "report.json"),
                     "unresolved": unresolved}).strip())
        return 2 if unresolved else 0
    except (InputError, UnicodeDecodeError, OSError, OverflowError, RecursionError) as exc:
        print(dumps({"status": "UNRESOLVED", "error": str(exc)}).strip(), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
