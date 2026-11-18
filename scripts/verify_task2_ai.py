#!/usr/bin/env python3
"""Fact-check the Task 2 AI analysis against the raw JTL/resource files."""

from __future__ import annotations

import csv
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = {
    "load": "results/load/23120372_Load_20261116.jtl",
    "stress": "results/stress/23120372_Stress_20261118.jtl",
    "spike": "results/spike/23120372_Spike_20261118.jtl",
    "50C": "results/endurance_50C/23120372_Endurance_20261118.jtl",
    "75C": "results/endurance_75C/23120372_Endurance_20261118.jtl",
    "100C": "results/endurance_100C/23120372_Endurance_20261118.jtl",
}


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def pct(values: list[float], p: float) -> float:
    ordered = sorted(values)
    k = (len(ordered) - 1) * p / 100.0
    lo = int(k)
    hi = min(lo + 1, len(ordered) - 1)
    return round(ordered[lo] + (ordered[hi] - ordered[lo]) * (k - lo), 2)


for name, rel in RUNS.items():
    data = rows(ROOT / rel)
    elapsed = [float(r["elapsed"]) for r in data]
    ts = [int(r["timeStamp"]) for r in data]
    t0, t1 = min(ts), max(int(r["timeStamp"]) + float(r["elapsed"]) for r in data)
    wall = (t1 - t0) / 1000.0
    print(f"\n=== {name} ===")
    print(f"rows={len(data)} wall={wall:.2f}s rps_rows_wall={len(data)/wall:.3f}")
    print(f"whole-run p50={pct(elapsed,50)} p95={pct(elapsed,95)} p99={pct(elapsed,99)} max={max(elapsed):.0f}")

    # per-label p95 and max
    labels: dict[str, list[float]] = {}
    for r in data:
        labels.setdefault(r["label"], []).append(float(r["elapsed"]))
    worst_p95 = max(labels.items(), key=lambda kv: pct(kv[1], 95))
    worst_max = max(labels.items(), key=lambda kv: max(kv[1]))
    print(f"worst p95 label={worst_p95[0]!r} p95={pct(worst_p95[1],95)}")
    print(f"worst max label={worst_max[0]!r} max={max(worst_max[1]):.0f}")

    if name == "stress":
        # 60 s buckets from first timestamp
        buckets: dict[int, list[dict]] = {}
        for r in data:
            b = int((int(r["timeStamp"]) - t0) / 60000)
            buckets.setdefault(b, []).append(r)
        best = max(buckets.items(), key=lambda kv: len(kv[1]))
        thr = len(best[1]) / 60.0
        max_threads = max(int(float(r["allThreads"])) for r in best[1])
        print(f"max 60s bucket: minute {best[0]} samples={len(best[1])} rps={thr:.2f} maxThreads={max_threads}")
        top = sorted(buckets.items(), key=lambda kv: -len(kv[1]))[:3]
        print("top 60s buckets:", [(m, len(v), round(len(v)/60, 2)) for m, v in top])

    if name == "load":
        slow = [r for r in data if float(r["elapsed"]) > 100]
        print(f"samples >100 ms: {len(slow)}")
        # end times up to 6 decimals
        ends = sorted((int(r["timeStamp"]) + float(r["elapsed"])) / 1000.0 for r in slow)
        start = t0 / 1000.0
        print("slow ends (rel s):", [round(e - start, 3) for e in ends])
        print("span:", round(ends[0] - start, 3), "->", round(ends[-1] - start, 3), "width", round(ends[-1]-ends[0], 3))
        print("distinct ends (ms):", len({round(e, 3) for e in ends}), "of", len(ends))

    # resources conns/threads
    res = rows(ROOT / rel.replace(".jtl", "") if False else ROOT / (Path(rel).parent / "resources.csv"))
    print("res samples:", len(res),
          "max backend_conns:", max(float(r["backend_conns"]) for r in res),
          "backend_threads range:", min(float(r["backend_threads"]) for r in res), "-",
          max(float(r["backend_threads"]) for r in res),
          "rss max:", max(float(r["backend_rss_mb"]) for r in res))
