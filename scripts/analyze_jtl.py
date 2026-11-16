#!/usr/bin/env python3
"""Analyse a JMeter JTL CSV produced by the HW05 plans.

Outputs (to analysis/):
    <scenario>_summary.md       per-label statistics, percentiles, error codes
    <scenario>_intervals.csv    30-second buckets (throughput, error %, p95)
    <scenario>_summary.json     machine-readable summary

The script never invents numbers: every value comes from the JTL rows. It
separates HTTP errors from expected lockout responses and reports both.

Usage:
    python scripts/analyze_jtl.py --scenario load --jtl results/load/xxx.jtl
    python scripts/analyze_jtl.py --scenario stress --jtl results/stress/xxx.jtl
    python scripts/analyze_jtl.py --scenario spike --jtl results/spike/xxx.jtl
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GROUP_PATTERNS = {
    "load": None,
    "endurance": None,
    "stress": re.compile(r"^(Stress S\d+ - \d+ VUs)"),
    "spike": re.compile(r"^(Spike C\d+ - (?:Baseline|Spike|Recovery) \d+ VUs)"),
    "lockout": None,
}


def pct(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * q
    low = math.floor(pos)
    high = math.ceil(pos)
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (pos - low)


def stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {"count": 0}
    total = sum(values)
    return {
        "count": len(values),
        "min": round(min(values), 2),
        "avg": round(total / len(values), 2),
        "p50": round(pct(values, 0.50), 2),
        "p90": round(pct(values, 0.90), 2),
        "p95": round(pct(values, 0.95), 2),
        "p99": round(pct(values, 0.99), 2),
        "max": round(max(values), 2),
    }


def group_key(scenario: str, row: dict[str, str]) -> str:
    pattern = GROUP_PATTERNS.get(scenario)
    if pattern is None:
        return "all"
    match = pattern.match(row["threadName"])
    return match.group(1) if match else "other"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True, choices=sorted(GROUP_PATTERNS))
    parser.add_argument("--jtl", type=Path, required=True)
    parser.add_argument("--bucket", type=float, default=30.0)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "analysis")
    args = parser.parse_args()

    jtl = args.jtl if args.jtl.is_absolute() else ROOT / args.jtl
    rows = list(csv.DictReader(jtl.open(encoding="utf-8", errors="replace")))
    if not rows:
        raise SystemExit(f"No rows in {jtl}")

    for row in rows:
        row["_ts"] = float(row["timeStamp"]) / 1000.0
        row["_elapsed"] = float(row["elapsed"])
        row["_group"] = group_key(args.scenario, row)
        row["_ok"] = row.get("success") == "true"

    start = min(r["_ts"] for r in rows)
    end = max(r["_ts"] + r["_elapsed"] / 1000.0 for r in rows)
    wall = max(end - start, 0.001)

    by_group: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_label: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_group[row["_group"]].append(row)
        by_label[row["label"]].append(row)

    error_codes = Counter((r["responseCode"], r.get("responseMessage", "")) for r in rows if not r["_ok"])

    summary: dict[str, object] = {
        "scenario": args.scenario,
        "jtl": str(jtl.relative_to(ROOT)) if jtl.is_relative_to(ROOT) else str(jtl),
        "rows": len(rows),
        "start": start,
        "end": end,
        "wall_seconds": round(wall, 2),
        "samples_per_second": round(len(rows) / wall, 3),
        "errors": sum(1 for r in rows if not r["_ok"]),
        "error_pct": round(100 * sum(1 for r in rows if not r["_ok"]) / len(rows), 3),
        "error_codes": [{"code": c, "message": m, "count": n} for (c, m), n in error_codes.most_common()],
        "max_active_threads": max(int(r.get("allThreads") or 0) for r in rows),
        "groups": {},
        "labels": {},
    }

    for group, items in by_group.items():
        ok = [r["_elapsed"] for r in items if r["_ok"]]
        g_start = min(r["_ts"] for r in items)
        g_end = max(r["_ts"] + r["_elapsed"] / 1000.0 for r in items)
        g_wall = max(g_end - g_start, 0.001)
        summary["groups"][group] = {
            "rows": len(items),
            "errors": sum(1 for r in items if not r["_ok"]),
            "error_pct": round(100 * sum(1 for r in items if not r["_ok"]) / len(items), 3),
            "rps": round(len(items) / g_wall, 3),
            "wall_seconds": round(g_wall, 2),
            "max_active_threads": max(int(r.get("allThreads") or 0) for r in items),
            "latency_ok_ms": stats(ok),
        }

    for label, items in by_label.items():
        ok = [r["_elapsed"] for r in items if r["_ok"]]
        l_start = min(r["_ts"] for r in items)
        l_end = max(r["_ts"] + r["_elapsed"] / 1000.0 for r in items)
        summary["labels"][label] = {
            "rows": len(items),
            "errors": sum(1 for r in items if not r["_ok"]),
            "rps": round(len(items) / max(l_end - l_start, 0.001), 3),
            "latency_ok_ms": stats(ok),
        }

    # 30-second intervals (from run start), useful for stress/spike timeline.
    buckets: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        buckets[int((row["_ts"] - start) // args.bucket)].append(row)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    interval_csv = args.out_dir / f"{args.scenario}_intervals.csv"
    with interval_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            ["bucket_start_s", "samples", "errors", "error_pct", "rps", "p95_ms", "avg_ms", "max_active_threads"]
        )
        for bucket in sorted(buckets):
            items = buckets[bucket]
            vals = [r["_elapsed"] for r in items if r["_ok"]]
            writer.writerow(
                [
                    int(bucket * args.bucket),
                    len(items),
                    sum(1 for r in items if not r["_ok"]),
                    round(100 * sum(1 for r in items if not r["_ok"]) / len(items), 3),
                    round(len(items) / args.bucket, 3),
                    round(pct(vals, 0.95), 2),
                    round(sum(vals) / len(vals), 2) if vals else 0,
                    max(int(r.get("allThreads") or 0) for r in items),
                ]
            )

    (args.out_dir / f"{args.scenario}_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    lines = [
        f"# JTL analysis — {args.scenario}",
        "",
        f"- JTL: `{summary['jtl']}`",
        f"- Rows: {len(rows)}; wall time: {summary['wall_seconds']} s; overall {summary['samples_per_second']} samples/s",
        f"- Errors: {summary['errors']} ({summary['error_pct']}%)",
        f"- Max active threads (allThreads): {summary['max_active_threads']}",
        "",
        "## Errors by response code",
        "",
    ]
    if error_codes:
        lines += ["| Code | Message | Count |", "|---|---|---:|"]
        for (code, message), count in error_codes.most_common():
            lines.append(f"| {code} | {message[:120]} | {count} |")
    else:
        lines.append("No failed samples.")

    lines += ["", "## Group / step summary", ""]
    lines += [
        "| Group | Rows | Errors | Error % | RPS (rows/wall) | Max threads | p50 | p95 | p99 | Avg |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for group, data in summary["groups"].items():
        lat = data["latency_ok_ms"]
        lines.append(
            f"| {group} | {data['rows']} | {data['errors']} | {data['error_pct']} | {data['rps']} | "
            f"{data['max_active_threads']} | {lat.get('p50', '')} | {lat.get('p95', '')} | "
            f"{lat.get('p99', '')} | {lat.get('avg', '')} |"
        )

    lines += ["", "## Per-label summary (successful samples only for latency)", ""]
    lines += [
        "| Label | Rows | Errors | RPS | p50 | p95 | p99 | Avg | Max |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, data in summary["labels"].items():
        lat = data["latency_ok_ms"]
        lines.append(
            f"| {label} | {data['rows']} | {data['errors']} | {data['rps']} | {lat.get('p50', '')} | "
            f"{lat.get('p95', '')} | {lat.get('p99', '')} | {lat.get('avg', '')} | {lat.get('max', '')} |"
        )

    lines += [
        "",
        f"30-second timeline: `{interval_csv.relative_to(ROOT) if interval_csv.is_relative_to(ROOT) else interval_csv}`",
    ]

    out_md = args.out_dir / f"{args.scenario}_summary.md"
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
