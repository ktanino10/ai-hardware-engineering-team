"""Read-only observation of the existing synthetic estimator's input path."""

from collections import Counter
import json

from simulation.imu_estimation import math3d
from simulation.imu_estimation.estimator import Estimator
from simulation.imu_estimation.schema import InputError, loads


LIMITS = [
    "SYNTHETIC_REFERENCE only: declared SI, body frame and exact synthetic clocks.",
    "Format/sample validity and upstream status are not sensor health.",
    "Shared bias may have zero spread; 3vs3 cannot identify the correct group.",
    "A disappearing spike does not erase past integration error.",
    "No health thresholds, exclusion, weights, calibration or control decisions.",
    "Real calibration, clock coherence, latency and physical accuracy are UNKNOWN.",
    "Gyro residuals only; accelerometer specific-force residuals are not reported.",
]


class _ObservedEstimator(Estimator):
    """Keep the validated body vectors without changing the returned sample."""

    def __init__(self, config):
        super().__init__(config)
        self.body_gyros = {}

    def _sample(self, row, t, used):
        sample = super()._sample(row, t, used)
        self.body_gyros[sample[0]] = sample[1][:]
        return sample


def _presence(batch, sensor_ids):
    if not isinstance(batch, dict) or not isinstance(batch.get("samples"), list):
        return None, None
    present = sorted({row["id"] for row in batch["samples"]
                      if isinstance(row, dict) and isinstance(row.get("id"), str)})
    return present, [sid for sid in sensor_ids if sid not in present]


def analyze(config, binary_lines):
    """Return a JSON-serializable report; input lines are bytes, in arrival order.

    The original estimator runs privately to retain its exact validation,
    time/latch policy and mean/spread. No orientation is emitted or consumed
    by a control path. Fewer than two contributors cannot witness agreement.
    """
    observer = _ObservedEstimator(config)
    sensor_ids = list(observer.sensors)
    records = []
    for index, raw in enumerate(binary_lines, 1):
        batch = None
        observer.body_gyros.clear()
        try:
            batch = loads(raw.decode("utf-8", errors="strict"))
            result = observer.step(batch)
        except UnicodeDecodeError as exc:
            result = observer.fail(f"invalid_utf8:line={index}:byte={exc.start}")
        except (InputError, OverflowError, RecursionError) as exc:
            result = observer.fail("invalid_record:" + str(exc))
        present, absent = _presence(batch, sensor_ids)
        accepted = result["accepted_ids"]
        valid = result["status"] != "invalid"
        comparable = valid and len(accepted) >= 2
        mean = result.get("omega_B_rad_s") if valid else None
        residuals = None
        if comparable:
            residuals = {}
            for sid in accepted:
                residual = math3d.sub(observer.body_gyros[sid], mean)
                residuals[sid] = {
                    "vector_B_rad_s": residual,
                    "norm_rad_s": math3d.norm(residual),
                }
        records.append({
            "record_index": index,
            "t_s_input_label": result["t_s"],
            "upstream_status_not_health": result["status"],
            "comparison": "COMPARABLE_SYNTHETIC" if comparable else "UNRESOLVED",
            "comparison_reason": ("declared_frame_units_clock" if comparable else
                                  "insufficient_contributors" if valid else
                                  "upstream_invalid"),
            "accepted_ids": accepted,
            "accepted_count": len(accepted),
            "input_present_ids_unvalidated": present,
            "absent_ids": absent,
            "rejected": result["rejected"],
            "upstream_reasons": result["reasons"],
            "gyro_mean_B_rad_s": mean,
            "gyro_spread_rad_s": result.get("gyro_spread_rad_s") if comparable else None,
            "residuals": residuals,
        })
    if not records:
        return {
            "format": "imu-disagreement-report-v1",
            "scope": "OFFLINE_SYNTHETIC_DISAGREEMENT_NOT_HEALTH",
            "limits": LIMITS,
            "records": [],
            "summary": _summarize([], sensor_ids),
            "errors": ["empty_stream"],
        }
    return {
        "format": "imu-disagreement-report-v1",
        "scope": "OFFLINE_SYNTHETIC_DISAGREEMENT_NOT_HEALTH",
        "limits": LIMITS,
        "records": records,
        "summary": _summarize(records, sensor_ids),
        "errors": [],
    }


def _summarize(records, sensor_ids):
    values = [r["gyro_spread_rad_s"] for r in records
              if r["gyro_spread_rad_s"] is not None]
    intervals = []
    for row in records:
        signature = (row["upstream_status_not_health"], row["comparison"],
                     row["accepted_ids"], row["absent_ids"])
        if intervals and signature == intervals[-1]["signature"]:
            intervals[-1]["last_record"] = row["record_index"]
            intervals[-1]["last_input_time_label_s"] = row["t_s_input_label"]
            intervals[-1]["records"] += 1
        else:
            intervals.append({
                "signature": signature,
                "first_record": row["record_index"],
                "last_record": row["record_index"],
                "first_input_time_label_s": row["t_s_input_label"],
                "last_input_time_label_s": row["t_s_input_label"],
                "records": 1,
            })
    for interval in intervals:
        status, comparison, accepted, absent = interval.pop("signature")
        interval.update(upstream_status_not_health=status, comparison=comparison,
                        accepted_ids=accepted, absent_ids=absent)
    return {
        "weighting": "Per-record only; not time-weighted, no interpolation or duration estimate.",
        "interval_semantics": "Arrival-order runs of status/IDs; timestamps are input labels, not proven physical time.",
        "records": len(records),
        "comparable_records": len(values),
        "unresolved_records": len(records) - len(values),
        "upstream_status_counts_not_health": dict(Counter(
            r["upstream_status_not_health"] for r in records)),
        "accepted_record_counts": {sid: sum(sid in r["accepted_ids"] for r in records)
                                   for sid in sensor_ids},
        "absent_record_counts": {sid: sum(r["absent_ids"] is not None and
                                         sid in r["absent_ids"] for r in records)
                                 for sid in sensor_ids},
        "unknown_presence_records": sum(r["absent_ids"] is None for r in records),
        "comparable_spread_max_rad_s": max(values) if values else None,
        "comparable_spread_mean_rad_s": sum(v / len(values) for v in values) if values else None,
        "intervals": intervals,
    }


def markdown(report):
    summary = report["summary"]
    lines = [
        "# Offline IMU disagreement report", "",
        "**SYNTHETIC ONLY / NOT SENSOR HEALTH OR CONTROL APPROVAL**", "",
        f"Records: {summary['records']}; comparable: {summary['comparable_records']}; "
        f"unresolved: {summary['unresolved_records']}.",
        f"Maximum comparable gyro spread (rad/s): {summary['comparable_spread_max_rad_s']}.",
        f"Sample-weighted mean spread (rad/s): {summary['comparable_spread_mean_rad_s']}.",
        "", "The metric is max Euclidean distance from the existing equal body-gyro mean, "
        "not standard deviation or orientation error.",
        "Null means unavailable, never zero/healthy. See report.json for every residual, "
        "rejection reason, contributor and arrival-order interval.", "",
        summary["weighting"], summary["interval_semantics"], "",
        "## Contributor availability (record counts, not health)", "",
        "Accepted:", "```json",
        json.dumps(summary["accepted_record_counts"], ensure_ascii=True),
        "```", "Absent in parsed batches:", "```json",
        json.dumps(summary["absent_record_counts"], ensure_ascii=True),
        "```",
        f"Unknown presence records: {summary['unknown_presence_records']}.", "",
        "## Limits", "",
        *("- " + text for text in report["limits"]),
        "", "## Errors", "", *("- " + text for text in report["errors"]),
        "", "## Source binding", "",
        "Exact input and implementation SHA-256: report.json / provenance.",
    ]
    return "\n".join(lines) + "\n"
