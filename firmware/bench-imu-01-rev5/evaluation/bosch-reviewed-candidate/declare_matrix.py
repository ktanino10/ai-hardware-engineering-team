#!/usr/bin/env python3
"""Declare finite public-API inputs before compiling or executing the driver."""
import itertools
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
CRT_FIELDS = ["kind", "gyro", "spi", "aps", "initial", "requested", "fifo", "arg", "fault", "at"]
AUX_FIELDS = ["read", "spi", "aps", "length", "start", "burst", "mode", "fault", "at", "busy"]
LENGTHS = [0, 1, 2, 6, 15, 16, 17, 19, 32, 358, 448, 510, 511, 512, 65535]
STATE_LENGTHS = [0, 1, 19, 512, 65535, 32]


def declare():
    suites = {name: [] for name in ("legacy", "crt", "aux-write", "aux-read")}

    def add(suite, series, values, fields):
        if len(fields) != len(values):
            raise ValueError("Case values do not match the declared fields")
        row = dict(zip(fields, values))
        scenario = ("aux:" if fields == AUX_FIELDS else "crt:") + ",".join(map(str, values))
        suites[suite].append({
            "id": f"{series}-{len(suites[suite]):04d}", "series": series,
            "input": row, "scenario": scenario,
        })

    def crt(series, kind, gyro=0, spi=1, aps=0, initial=32, requested=32,
            fifo=1, arg=0, fault=0, at=0, suite="crt"):
        add(suite, series, [kind, gyro, spi, aps, initial, requested, fifo, arg, fault, at], CRT_FIELDS)

    # Canonical inputs for the immutable 25/36/12 tests, not a rerun of their sources.
    for length in [32, 448, 358, 2, 510, 19]:
        crt("legacy-bounds", 0, requested=length, suite="legacy")
    crt("legacy-bounds", 0, gyro=1, requested=448, suite="legacy")
    crt("legacy-bounds", 0, spi=0, requested=358, suite="legacy")
    for length in [512, 65535]:
        crt("legacy-bounds", 0, requested=length, suite="legacy")
    for initial in [19, 0, 1]:
        crt("legacy-bounds", 1, initial=initial, requested=initial, suite="legacy")
    for length in [0, 1]:
        crt("legacy-bounds", 0, requested=length, suite="legacy")
    for fault, at in [(3, 1), (4, 1), (6, 0), (5, 0)]:
        crt("legacy-bounds", 8, fault=fault, at=at, suite="legacy")
    crt("legacy-bounds", 10, suite="legacy")
    for kind in [3, 2, 4]:
        crt("legacy-bounds", kind, fifo=int(kind != 2), suite="legacy")
    crt("legacy-bounds", 5, arg=8190, suite="legacy")
    crt("legacy-bounds", 6, suite="legacy")
    for kind, gyro, length in itertools.product([2, 3, 4], range(2), STATE_LENGTHS):
        crt("legacy-state", kind, gyro=gyro, requested=length, fifo=int(kind != 2), suite="legacy")
    for gyro, length in itertools.product(range(2), STATE_LENGTHS):
        crt("legacy-initial-error", 7, gyro=gyro, requested=length, fifo=0, fault=2, suite="legacy")

    for gyro, spi in itertools.product(range(2), range(2)):
        common = {"gyro": gyro, "spi": spi}
        for length in LENGTHS:
            crt("upload", 0, requested=length, **common)
        for initial in [0, 1, 19]:
            crt("initialization-distinction", 1, initial=initial, requested=initial, **common)
        for kind, length in itertools.product([2, 3, 4], STATE_LENGTHS + [15]):
            crt("state", kind, requested=length, fifo=int(kind != 2), **common)
        for extent in [0, 6143, 6144, 8190, 8191]:
            crt("extent", 5, arg=extent, **common)
        for pointer in range(5):
            crt("null", 6, arg=pointer, **common)
        for fifo, length in itertools.product(range(2), STATE_LENGTHS):
            crt("initial-feature-error", 7, requested=length, fifo=fifo, fault=2, **common)
        for aps, fifo, length in itertools.product(range(2), range(2), [2, 15]):
            normalized = length & ~1
            crt("initial-feature-suboperation", 7, aps=aps, requested=length,
                fifo=fifo, fault=1, **common)
            for part in range((16 + normalized - 1) // normalized):
                crt("initial-feature-suboperation", 7, aps=aps, requested=length,
                    fifo=fifo, fault=2, at=part, **common)
        for fifo in range(2):
            crt("aps-initial-feature-error", 7, aps=1, fifo=fifo, fault=2, **common)
            crt("aps-success", 0 if fifo else 2, aps=1, fifo=fifo, **common)
        for chunk in [32, 6, 448]:
            full, remainder = divmod(2048, chunk)
            tail = remainder // 2
            positions = sorted({0, full - 1} | ({full, full + tail - 1} if tail else set()))
            for position, fault in itertools.product(positions, [3, 4, 5, 6]):
                crt("transfer-error", 8, requested=chunk, fault=fault, at=position, **common)
            # Exercise waits that the RETAINED source actually performs. This is
            # not an oracle for the correctness of C3's last-byte classification.
            waits = [p for p in positions if
                     (p < full and (remainder != 0 or p < full - 1)) or
                     (p >= full and tail == 1)]
            for position in waits:
                crt("existing-wait-error", 8, requested=chunk, fault=7, at=position, **common)
            if tail:
                crt("tail-maxburst-error", 9, requested=chunk, fault=1, **common)
                for part in range((16 + min(chunk, 16) - 1) // min(chunk, 16)):
                    crt("tail-maxburst-error", 9, requested=chunk, fault=2, at=part, **common)
                crt("tail-maxburst-error", 9, requested=chunk, fault=8, **common)

    def aux(series, read=0, spi=1, aps=0, length=257, start=0, burst=1,
            mode=0, fault=0, at=0, busy=0):
        add("aux-read" if read else "aux-write", series,
            [read, spi, aps, length, start, burst, mode, fault, at, busy], AUX_FIELDS)

    for spi, aps in itertools.product(range(2), range(2)):
        common = {"spi": spi, "aps": aps}
        for length, start in [(n, 0) for n in [0, 1, 2, 255, 256, 257, 65535]] + [(3, 254), (2, 255)]:
            aux("write-progression", length=length, start=start, **common)
        for fault, at in itertools.product([1, 2, 3], [0, 1, 255, 256]):
            aux("write-error", mode=1, fault=fault, at=at, **common)
        for length, burst in [(0, 1), (1, 1), (9, 8)]:
            aux("read-success", read=1, length=length, burst=burst, start=254, **common)
        for length, burst, positions in [(1, 1, [0]), (9, 8, [0, 1])]:
            for fault, at in itertools.product([1, 2, 3], positions):
                aux("read-error", read=1, length=length, burst=burst, start=254,
                    mode=1, fault=fault, at=at, **common)
        for read in range(2):
            for busy in [1, 20, 21]:
                aux("busy", read=read, length=1, mode=2, busy=busy, **common)
            aux("busy-then-error", read=read, length=1, mode=1, fault=2, busy=2, **common)
            for precondition in range(7 + read):
                aux("precondition", read=read, length=0 if precondition == 6 else 1,
                    mode=3, fault=precondition, **common)
        if aps:
            for read, operation in itertools.product(range(2), range(4)):
                aux("aps-operation-error", read=read, length=1, mode=4, fault=operation, **common)

    all_rows = [row for rows in suites.values() for row in rows]
    return {
        "schema_version": 1,
        "classification": "PREDECLARED_SELECTED_SOURCE_AUTHOR_HOST_MATRIX",
        "crt_fields": CRT_FIELDS, "aux_fields": AUX_FIELDS,
        "codebook": {
            "crt_kind": ["upload", "initialization", "no-download", "busy", "unsupported",
                         "extent", "null", "initial-feature-error", "transfer-error",
                         "tail-maxburst-error", "ready-timeout-legacy-only"],
            "crt_fault": {"1": "page-write", "2": "feature-read-part", "3": "upload-address",
                          "4": "upload-data", "5": "ready-snapshot", "6": "trigger",
                          "7": "existing-ready-wait", "8": "feature-write"},
            "crt_null_arg": ["config", "device", "read-callback", "write-callback", "delay-callback"],
            "aux_mode": ["success", "one-shot-error", "busy", "precondition", "APS-error"],
            "aux_fault": {"1": "data", "2": "status", "3": "address"},
            "aux_precondition": ["null-device", "null-data", "null-read", "null-write",
                                 "null-delay", "manual-disabled", "null-data-zero-length", "invalid-burst"],
            "aux_APS_fault": ["disable-read", "disable-write", "restore-read", "restore-write"],
        },
        "counts": {name: len(rows) for name, rows in suites.items()},
        "execution_cases": len(all_rows),
        "unique_scenarios": len({row["scenario"] for row in all_rows}),
        "identity_rule": "Exact declared input tuples, including initial/post-init lengths, transport and APS. "
                         "Repeated legacy/new tuples count as executions, not new scenarios. "
                         "Uncounted embedded legacy assertions are not extra cases.",
        "limits": [
            "C3 OPEN/MEDIUM, unselected: immediate-ready callbacks do not establish readiness protocol correctness.",
            "No CRT outer APS/status error redesign or general Aux long-read indexing claim.",
            "Fake delays only; finite callback and subprocess budgets; no device/SDK/network access.",
            "Original and historical candidate campaigns are not executed.",
        ],
        "suites": suites,
    }


if __name__ == "__main__":
    target = PACKAGE / "case-matrix.json"
    with target.open("x", encoding="ascii") as handle:
        json.dump(declare(), handle, indent=2)
        handle.write("\n")
