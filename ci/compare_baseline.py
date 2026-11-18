#!/usr/bin/env python3
"""Compare a current JTL analysis summary with a committed baseline.

Exit code 0 = pass, 1 = regression gate failed, 2 = invalid input.

Thresholds (intentionally conservative to reduce false alarms):
  p95  +20% AND +200 ms absolute
  p99  +30% OR  +500 ms absolute
  error rate > 1% (expected negative tests must already be excluded)
  throughput -15%

Usage:
    python ci/compare_baseline.py --baseline ci/baseline.json --current analysis/load_summary.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    # Accept either a raw analysis summary or a baseline wrapper.
    return data.get("metrics", data)


def overall_latency(summary: dict, key: str) -> float:
    groups = summary.get("groups", {})
    if "all" in groups:
        value = groups["all"].get("latency_ok_ms", {}).get(key)
        if value is not None:
            return float(value)
    values = []
    for label in summary.get("labels", {}).values():
        value = label.get("latency_ok_ms", {}).get(key)
        if value is not None:
            values.append(float(value))
    return max(values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--max-p95-growth", type=float, default=0.20)
    parser.add_argument("--max-p95-abs-ms", type=float, default=200.0)
    parser.add_argument("--max-p99-growth", type=float, default=0.30)
    parser.add_argument("--max-p99-abs-ms", type=float, default=500.0)
    parser.add_argument("--max-error-pct", type=float, default=1.0)
    parser.add_argument("--max-rps-drop", type=float, default=0.15)
    args = parser.parse_args()

    base = load(args.baseline)
    cur = load(args.current)

    base_p95 = overall_latency(base, "p95")
    cur_p95 = overall_latency(cur, "p95")
    base_p99 = overall_latency(base, "p99")
    cur_p99 = overall_latency(cur, "p99")
    base_rps = float(base.get("samples_per_second", 0))
    cur_rps = float(cur.get("samples_per_second", 0))
    cur_err = float(cur.get("error_pct", 0))

    p95_growth = (cur_p95 - base_p95) / base_p95 if base_p95 else 0
    p99_growth = (cur_p99 - base_p99) / base_p99 if base_p99 else 0
    rps_drop = (base_rps - cur_rps) / base_rps if base_rps else 0

    failures: list[str] = []
    if p95_growth > args.max_p95_growth and (cur_p95 - base_p95) > args.max_p95_abs_ms:
        failures.append(
            f"p95 regression: {base_p95:.1f} -> {cur_p95:.1f} ms "
            f"(+{p95_growth:.1%}, threshold +{args.max_p95_growth:.0%} and +{args.max_p95_abs_ms:.0f} ms)"
        )
    if p99_growth > args.max_p99_growth or (cur_p99 - base_p99) > args.max_p99_abs_ms:
        failures.append(
            f"p99 regression: {base_p99:.1f} -> {cur_p99:.1f} ms "
            f"(+{p99_growth:.1%}, threshold +{args.max_p99_growth:.0%} or +{args.max_p99_abs_ms:.0f} ms)"
        )
    if cur_err > args.max_error_pct:
        failures.append(f"error rate {cur_err:.2f}% > {args.max_error_pct:.2f}%")
    if rps_drop > args.max_rps_drop:
        failures.append(
            f"throughput drop: {base_rps:.2f} -> {cur_rps:.2f} samples/s (-{rps_drop:.1%})"
        )

    print("## Performance gate")
    print("")
    print("| Metric | Baseline | Current | Delta |")
    print("|---|---:|---:|---:|")
    print(f"| p95 (overall) | {base_p95:.1f} ms | {cur_p95:.1f} ms | {p95_growth:+.1%} |")
    print(f"| p99 (overall) | {base_p99:.1f} ms | {cur_p99:.1f} ms | {p99_growth:+.1%} |")
    print(f"| Throughput | {base_rps:.2f} /s | {cur_rps:.2f} /s | {-rps_drop:+.1%} |")
    print(f"| Error rate | - | {cur_err:.2f}% | - |")
    print("")

    if failures:
        print("**FAIL**")
        for item in failures:
            print(f"- {item}")
        return 1

    print("**PASS** — no threshold exceeded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
