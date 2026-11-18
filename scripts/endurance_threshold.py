#!/usr/bin/env python3
"""Apply the pre-registered endurance criteria and pick the threshold.

Reads the JSON files produced by scripts/endurance_stats.py and writes
analysis/endurance_threshold.md. The criteria are the same ones written in
PLAN.md section 5.1 before the runs:

    error < 1% | p95 < 1000 ms | p99 < 2000 ms | throughput CV (30 s) < 10%
    RSS growth after the 300 s warm-up < 10% | backend CPU average < 85%

Usage:
    python scripts/endurance_threshold.py --runs analysis/endurance_50C analysis/endurance_75C analysis/endurance_100C
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CRITERIA = [
    ("error_pct_lt_1", "Error rate < 1%"),
    ("p95_lt_1000", "p95 < 1000 ms"),
    ("p99_lt_2000", "p99 < 2000 ms"),
    ("cv30_lt_10", "30 s throughput CV < 10%"),
    ("rss_lt_10", "RSS growth after 300 s < 10%"),
    ("bcpu_lt_85", "Backend CPU average < 85%"),
]


def evaluate(s: dict) -> dict[str, bool]:
    return {
        "error_pct_lt_1": s["errors"]["pct"] < 1.0,
        "p95_lt_1000": s["latency_ms"]["p95"] < 1000.0,
        "p99_lt_2000": s["latency_ms"]["p99"] < 2000.0,
        "cv30_lt_10": s["throughput"]["cv30_pct"] < 10.0,
        "rss_lt_10": s["memory_mb"]["late_growth_pct"] < 10.0,
        "bcpu_lt_85": s["backend_cpu_pct"]["avg"] < 85.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", nargs="+", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("analysis/endurance_threshold.md"))
    args = parser.parse_args()

    runs = []
    for run in args.runs:
        run = run if run.is_absolute() else ROOT / run
        files = sorted(
            f for f in run.glob("endurance_*.json") if not f.name.endswith("_summary.json")
        )
        if not files:
            raise SystemExit(f"No endurance_*.json in {run}")
        data = json.loads(files[-1].read_text(encoding="utf-8"))
        data["_criteria"] = evaluate(data)
        data["_pass"] = all(data["_criteria"].values())
        runs.append(data)

    runs.sort(key=lambda r: r["throughput"]["rps30_mean"])
    passing = [r for r in runs if r["_pass"]]
    threshold = max(passing, key=lambda r: r["throughput"]["rps30_mean"]) if passing else None

    lines = [
        "# Endurance threshold",
        "",
        "Criteria (pre-registered in `PLAN.md` section 5.1):",
        "",
        "- error rate < 1%",
        "- p95 < 1000 ms, p99 < 2000 ms",
        "- throughput coefficient of variation over 30 s buckets < 10%",
        "- backend RSS growth after the 300 s warm-up < 10%",
        "- backend CPU average < 85%",
        "",
        "| Level | VUs | RPS (30 s mean) | CV | p95 | p99 | Error % | RSS max | RSS growth after 300 s | Backend CPU avg | Verdict |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in runs:
        lines.append(
            f"| {r['label']} | {r['max_active_threads']} | {r['throughput']['rps30_mean']} | "
            f"{r['throughput']['cv30_pct']}% | {r['latency_ms']['p95']} ms | {r['latency_ms']['p99']} ms | "
            f"{r['errors']['pct']}% | {r['memory_mb']['max']} MB | {r['memory_mb']['late_growth_pct']}% | "
            f"{r['backend_cpu_pct']['avg']}% | {'PASS' if r['_pass'] else 'FAIL'} |"
        )

    lines += ["", "## Criterion detail", ""]
    header = "| Level | " + " | ".join(name for _, name in CRITERIA) + " |"
    lines += [header, "|---|" + "---|" * len(CRITERIA)]
    for r in runs:
        cells = ["PASS" if r["_criteria"][key] else "FAIL" for key, _ in CRITERIA]
        lines.append(f"| {r['label']} | " + " | ".join(cells) + " |")

    lines += ["", "## Conclusion", ""]
    if threshold:
        lines += [
            f"**Threshold: {threshold['label']} - {threshold['max_active_threads']} VUs, "
            f"{threshold['throughput']['rps30_mean']} samples/s sustained for "
            f"{threshold['window']['duration_s']} s of steady state.**",
            "",
            f"Memory ceiling at that level: **{threshold['memory_mb']['max']} MB** backend RSS "
            f"(observed at {threshold['memory_mb']['max_at_s']} s).",
        ]
    else:
        lines.append("No level passed every criterion; the threshold is below the lowest level tested.")
    lines += [
        "",
        "The client and the SUT share one laptop, so these numbers describe this",
        "co-located configuration, not the capacity of EShop on dedicated hardware.",
        "",
    ]

    out = args.out if args.out.is_absolute() else ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
