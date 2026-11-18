#!/usr/bin/env python3
"""Render a resource-monitor CSV as a dependency-free SVG chart.

Usage:
    python scripts/plot_resources.py --csv results/load/resources.csv --out results/load/resources.svg --title "Load - 30 VUs"
"""

from __future__ import annotations

import argparse
import csv
import html
from pathlib import Path

COLORS = {
    "backend_cpu_pct": "#d62728",
    "jmeter_cpu_pct": "#1f77b4",
    "sys_cpu_pct": "#7f7f7f",
    "backend_rss_mb": "#d62728",
    "jmeter_rss_mb": "#1f77b4",
    "sys_ram_available_mb": "#2ca02c",
}


def read_columns(path: Path) -> tuple[list[float], dict[str, list[float]]]:
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    x = [float(r["elapsed_s"]) for r in rows]
    series: dict[str, list[float]] = {}
    for key in COLORS:
        vals = []
        for r in rows:
            try:
                vals.append(float(r[key]))
            except (KeyError, ValueError):
                vals.append(0.0)
        series[key] = vals
    return x, series


def polyline(xs: list[float], ys: list[float], x0: float, x1: float, y0: float, y1: float,
             left: float, top: float, width: float, height: float) -> str:
    if x1 <= x0:
        return ""
    pts = []
    for x, y in zip(xs, ys):
        px = left + (x - x0) / (x1 - x0) * width
        py = top + height - (y - y0) / (y1 - y0) * height
        pts.append(f"{px:.1f},{py:.1f}")
    return " ".join(pts)


def panel(xs, series, keys, title, unit, left, top, width, height, ymax=None) -> list[str]:
    out: list[str] = []
    all_vals = [v for key in keys for v in series[key]]
    ymax = ymax or max(all_vals + [1.0]) * 1.15
    out.append(f'<text x="{left}" y="{top - 10}" font-size="15" font-weight="bold">{html.escape(title)}</text>')
    out.append(
        f'<rect x="{left}" y="{top}" width="{width}" height="{height}" fill="#ffffff" stroke="#333" stroke-width="1"/>'
    )
    for i in range(6):
        y = top + height * i / 5
        val = ymax * (1 - i / 5)
        out.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + width}" y2="{y:.1f}" stroke="#e5e5e5"/>')
        out.append(f'<text x="{left - 6}" y="{y + 4:.1f}" font-size="11" text-anchor="end">{val:.0f}</text>')
    xmax = max(xs) if xs else 1
    for i in range(6):
        x = left + width * i / 5
        out.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + height}" stroke="#f0f0f0"/>')
        out.append(
            f'<text x="{x:.1f}" y="{top + height + 16}" font-size="11" text-anchor="middle">{xmax * i / 5:.0f}</text>'
        )
    out.append(
        f'<text x="{left + width / 2:.1f}" y="{top + height + 34}" font-size="12" text-anchor="middle">elapsed seconds</text>'
    )
    out.append(
        f'<text x="{left - 46}" y="{top + height / 2:.1f}" font-size="12" text-anchor="middle" '
        f'transform="rotate(-90 {left - 46} {top + height / 2:.1f})">{html.escape(unit)}</text>'
    )
    for idx, key in enumerate(keys):
        pts = polyline(xs, series[key], 0, xmax, 0, ymax, left, top, width, height)
        out.append(f'<polyline points="{pts}" fill="none" stroke="{COLORS[key]}" stroke-width="2"/>')
        out.append(
            f'<rect x="{left + 10}" y="{top + 10 + idx * 18}" width="12" height="12" fill="{COLORS[key]}"/>'
            f'<text x="{left + 28}" y="{top + 20 + idx * 18}" font-size="12">{html.escape(key)}</text>'
        )
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--title", default="Resource monitor")
    args = parser.parse_args()

    xs, series = read_columns(args.csv)
    width, height = 1200, 760
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#fafafa"/>',
        f'<text x="30" y="34" font-size="20" font-weight="bold">{html.escape(args.title)}</text>',
        f'<text x="30" y="56" font-size="12" fill="#555">Source: {html.escape(str(args.csv))} - 2 s samples</text>',
    ]
    parts += panel(xs, series, ["backend_cpu_pct", "jmeter_cpu_pct", "sys_cpu_pct"], "CPU (%)", "%", 90, 100, 1040, 230)
    parts += panel(xs, series, ["backend_rss_mb", "jmeter_rss_mb"], "Process RSS (MB)", "MB", 90, 430, 1040, 230)
    parts.append("</svg>")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
