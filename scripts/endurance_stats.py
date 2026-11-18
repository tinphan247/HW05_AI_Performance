#!/usr/bin/env python3
"""Steady-state endurance statistics for HW05.

Reads one endurance run directory (JTL + resources.csv) and computes the
numbers used by the endurance-threshold table:

  * steady-state window = [warmup_s, run_end - cooldown_s] relative to the
    first sample timestamp;
  * throughput mean, standard deviation and coefficient of variation;
  * p95/p99/avg latency and error rate inside that window;
  * backend RSS at start / end of warm-up / end of run / maximum;
  * backend RSS slope (MB per minute) across the steady window;
  * backend and system CPU averages/maxima.

Every value is derived from the raw files; nothing is hard-coded.

Usage:
    python scripts/endurance_stats.py --run-dir results/endurance_50C --label 50C
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_jtl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        for raw in csv.DictReader(fh):
            try:
                rows.append(
                    {
                        "ts": int(raw["timeStamp"]) / 1000.0,
                        "elapsed": float(raw["elapsed"]),
                        "ok": raw["success"].strip().lower() == "true",
                        "label": raw.get("label", ""),
                        "threads": int(float(raw.get("allThreads") or 0)),
                    }
                )
            except (KeyError, ValueError):
                continue
    return rows


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    k = (len(ordered) - 1) * pct / 100.0
    lo = int(k)
    hi = min(lo + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (k - lo)


def slope_per_minute(points: list[tuple[float, float]]) -> float:
    if len(points) < 2:
        return 0.0
    n = len(points)
    mean_x = sum(x for x, _ in points) / n
    mean_y = sum(y for _, y in points) / n
    denom = sum((x - mean_x) ** 2 for x, _ in points)
    if denom == 0:
        return 0.0
    cov = sum((x - mean_x) * (y - mean_y) for x, y in points)
    return cov / denom


def find_resource_file(run_dir: Path) -> Path:
    candidate = run_dir / "resources.csv"
    if candidate.exists():
        return candidate
    raise SystemExit(f"resources.csv not found in {run_dir}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--label", required=True, help="e.g. 50C, 75C, 100C")
    parser.add_argument("--warmup", type=float, default=90.0)
    parser.add_argument("--cooldown", type=float, default=30.0)
    parser.add_argument("--out-dir", type=Path, default=Path("analysis"))
    args = parser.parse_args()

    run_dir = args.run_dir if args.run_dir.is_absolute() else ROOT / args.run_dir
    jtl = next(run_dir.glob("*.jtl"))
    rows = read_jtl(jtl)
    if not rows:
        raise SystemExit(f"No rows in {jtl}")

    t0 = min(r["ts"] for r in rows)
    t_end = max(r["ts"] + r["elapsed"] / 1000.0 for r in rows)
    steady_start = t0 + args.warmup
    steady_end = t_end - args.cooldown
    steady = [r for r in rows if steady_start <= r["ts"] < steady_end]
    if not steady:
        raise SystemExit("Steady window is empty; adjust --warmup/--cooldown")

    per_second: dict[int, int] = {}
    for r in steady:
        per_second[int(r["ts"] - steady_start)] = per_second.get(int(r["ts"] - steady_start), 0) + 1
    rps_values = [per_second[k] for k in sorted(per_second)]
    rps_mean = statistics.fmean(rps_values)
    rps_sd = statistics.pstdev(rps_values) if len(rps_values) > 1 else 0.0
    cv_pct = (rps_sd / rps_mean * 100.0) if rps_mean else 0.0

    per_30s: dict[int, int] = {}
    for r in steady:
        bucket = int((r["ts"] - steady_start) // 30.0)
        per_30s[bucket] = per_30s.get(bucket, 0) + 1
    rps30_values = [per_30s[k] / 30.0 for k in sorted(per_30s)]
    rps30_mean = statistics.fmean(rps30_values)
    rps30_sd = statistics.pstdev(rps30_values) if len(rps30_values) > 1 else 0.0
    cv30_pct = (rps30_sd / rps30_mean * 100.0) if rps30_mean else 0.0

    lat = [r["elapsed"] for r in steady if r["ok"]]
    errors = sum(1 for r in steady if not r["ok"])
    error_pct = errors / len(steady) * 100.0

    with find_resource_file(run_dir).open(encoding="utf-8", newline="") as fh:
        res = list(csv.DictReader(fh))
    res_rows = []
    for r in res:
        try:
            res_rows.append(
                {
                    "t": float(r["elapsed_s"]),
                    "rss": float(r["backend_rss_mb"]),
                    "bcpu": float(r["backend_cpu_pct"]),
                    "scpu": float(r["sys_cpu_pct"]),
                }
            )
        except (KeyError, ValueError):
            continue
    if not res_rows:
        raise SystemExit("No usable resource rows")

    def at_or_after(seconds: float) -> dict:
        return min(res_rows, key=lambda r: abs(r["t"] - seconds))

    warm = at_or_after(args.warmup)
    end = res_rows[-1]
    steady_res = [r for r in res_rows if args.warmup <= r["t"] <= res_rows[-1]["t"] - args.cooldown]
    rss_max_row = max(res_rows, key=lambda r: r["rss"])
    rss_slope = slope_per_minute([(r["t"] / 60.0, r["rss"]) for r in steady_res]) if len(steady_res) > 1 else 0.0
    late_res = [r for r in res_rows if r["t"] >= 300.0]
    rss_slope_late = slope_per_minute([(r["t"] / 60.0, r["rss"]) for r in late_res]) if len(late_res) > 1 else 0.0
    late_start_rss = late_res[0]["rss"] if late_res else warm["rss"]

    stats = {
        "label": args.label,
        "run_dir": str(run_dir.relative_to(ROOT)) if run_dir.is_relative_to(ROOT) else str(run_dir),
        "jtl": str(jtl.relative_to(ROOT)) if jtl.is_relative_to(ROOT) else str(jtl),
        "window": {
            "warmup_s": args.warmup,
            "cooldown_s": args.cooldown,
            "steady_start": round(steady_start - t0, 1),
            "steady_end": round(steady_end - t0, 1),
            "duration_s": round(steady_end - steady_start, 1),
        },
        "throughput": {
            "rps_mean": round(rps_mean, 3),
            "rps_sd": round(rps_sd, 3),
            "cv_pct": round(cv_pct, 2),
            "rps_min": min(rps_values),
            "rps_max": max(rps_values),
            "rps30_mean": round(rps30_mean, 3),
            "rps30_sd": round(rps30_sd, 3),
            "cv30_pct": round(cv30_pct, 2),
            "rps30_min": round(min(rps30_values), 3),
            "rps30_max": round(max(rps30_values), 3),
        },
        "latency_ms": {
            "p50": round(percentile(lat, 50), 2),
            "p95": round(percentile(lat, 95), 2),
            "p99": round(percentile(lat, 99), 2),
            "avg": round(statistics.fmean(lat), 2) if lat else 0.0,
        },
        "errors": {"count": errors, "pct": round(error_pct, 4)},
        "memory_mb": {
            "start": res_rows[0]["rss"],
            "warmup_end": warm["rss"],
            "run_end": end["rss"],
            "max": rss_max_row["rss"],
            "max_at_s": rss_max_row["t"],
            "steady_slope_per_min": round(rss_slope, 3),
            "late_slope_per_min": round(rss_slope_late, 3),
            "late_start_rss": late_start_rss,
            "late_growth_pct": round((end["rss"] - late_start_rss) / late_start_rss * 100.0, 1) if late_start_rss else 0.0,
            "warmup_to_end_pct": round((end["rss"] - warm["rss"]) / warm["rss"] * 100.0, 1) if warm["rss"] else 0.0,
        },
        "backend_cpu_pct": {
            "avg": round(statistics.fmean([r["bcpu"] for r in steady_res]), 2) if steady_res else 0.0,
            "max": max(r["bcpu"] for r in res_rows),
        },
        "system_cpu_pct": {
            "avg": round(statistics.fmean([r["scpu"] for r in steady_res]), 2) if steady_res else 0.0,
            "max": max(r["scpu"] for r in res_rows),
        },
        "max_active_threads": max(r["threads"] for r in steady),
    }

    out_dir = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(stats, indent=2, ensure_ascii=False)
    (out_dir / f"endurance_{args.label}.json").write_text(payload, encoding="utf-8")

    s = stats
    md = [
        f"# Endurance {s['label']} - steady-state statistics",
        "",
        f"- Run: `{s['run_dir']}`",
        f"- JTL: `{s['jtl']}`",
        f"- Window: {s['window']['steady_start']}s to {s['window']['steady_end']}s "
        f"({s['window']['duration_s']}s; warm-up {s['window']['warmup_s']}s, cooldown {s['window']['cooldown_s']}s)",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Throughput | {s['throughput']['rps30_mean']} samples/s, 30 s buckets (SD {s['throughput']['rps30_sd']}, CV {s['throughput']['cv30_pct']}%) |",
        f"| Throughput 1 s buckets | {s['throughput']['rps_mean']} samples/s (SD {s['throughput']['rps_sd']}, CV {s['throughput']['cv_pct']}%) |",
        f"| Throughput range (30 s) | {s['throughput']['rps30_min']} - {s['throughput']['rps30_max']} samples/s |",
        f"| p50 / p95 / p99 | {s['latency_ms']['p50']} / {s['latency_ms']['p95']} / {s['latency_ms']['p99']} ms |",
        f"| Errors | {s['errors']['count']} ({s['errors']['pct']}%) |",
        f"| Max active threads | {s['max_active_threads']} |",
        f"| Backend CPU avg / max | {s['backend_cpu_pct']['avg']}% / {s['backend_cpu_pct']['max']}% |",
        f"| System CPU avg / max | {s['system_cpu_pct']['avg']}% / {s['system_cpu_pct']['max']}% |",
        f"| Backend RSS start | {s['memory_mb']['start']} MB |",
        f"| Backend RSS end of warm-up | {s['memory_mb']['warmup_end']} MB |",
        f"| Backend RSS end of run | {s['memory_mb']['run_end']} MB |",
        f"| Backend RSS max (memory ceiling) | {s['memory_mb']['max']} MB at {s['memory_mb']['max_at_s']}s |",
        f"| Backend RSS at 300 s | {s['memory_mb']['late_start_rss']} MB |",
        f"| RSS growth 300 s -> end | {s['memory_mb']['late_growth_pct']}% |",
        f"| RSS slope in steady window | {s['memory_mb']['steady_slope_per_min']} MB/min |",
        f"| RSS slope after 300 s | {s['memory_mb']['late_slope_per_min']} MB/min |",
        f"| RSS growth warm-up -> end | {s['memory_mb']['warmup_to_end_pct']}% |",
        "",
    ]
    (out_dir / f"endurance_{args.label}.md").write_text("\n".join(md), encoding="utf-8")
    print(out_dir / f"endurance_{args.label}.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
