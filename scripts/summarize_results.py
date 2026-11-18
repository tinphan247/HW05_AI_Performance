#!/usr/bin/env python3
"""Build a compact results summary from the analyzed JSON files."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "analysis"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    lines = ["# Results summary (generated from JTL analyses)", ""]
    load_sum = load(A / "load_summary.json")
    lines += [
        "## Load",
        "",
        f"- Samples: {load_sum['rows']}, errors: {load_sum['errors']} ({load_sum['error_pct']}%)",
        f"- Throughput: {load_sum['samples_per_second']} samples/s over {load_sum['wall_seconds']} s",
        f"- Max active threads: {load_sum['max_active_threads']}",
        f"- p95/p99: {load_sum['groups']['all']['latency_ok_ms']['p95']} / "
        f"{load_sum['groups']['all']['latency_ok_ms']['p99']} ms",
        "",
        "| Label | Rows | p95 ms | p99 ms | Max ms |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, data in sorted(load_sum["labels"].items(), key=lambda kv: -kv[1]["latency_ok_ms"]["p95"]):
        lat = data["latency_ok_ms"]
        lines.append(f"| {name} | {data['rows']} | {lat['p95']} | {lat['p99']} | {lat['max']} |")

    for scen in ("stress", "spike"):
        summary = load(A / f"{scen}_summary.json")
        lines += ["", f"## {scen.capitalize()}", "", "| Group | Rows | RPS | p95 | p99 | Max threads |", "|---|---:|---:|---:|---:|---:|"]
        for name, data in summary["groups"].items():
            lat = data["latency_ok_ms"]
            lines.append(
                f"| {name} | {data['rows']} | {data['rps']} | {lat['p95']} | {lat['p99']} | {data['max_active_threads']} |"
            )

    lines += ["", "## Endurance", "", "| Level | VUs | RPS | CV30 | p95 | p99 | Errors | RSS max | CPU avg |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for label in ("50C", "75C", "100C"):
        path = A / f"endurance_{label}" / f"endurance_{label}.json"
        if not path.exists():
            lines.append(f"| {label} | missing | | | | | | | |")
            continue
        s = load(path)
        lines.append(
            f"| {label} | {s['max_active_threads']} | {s['throughput']['rps30_mean']} | "
            f"{s['throughput']['cv30_pct']}% | {s['latency_ms']['p95']} | {s['latency_ms']['p99']} | "
            f"{s['errors']['pct']}% | {s['memory_mb']['max']} MB | {s['backend_cpu_pct']['avg']}% |"
        )

    out = A / "results_summary.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
