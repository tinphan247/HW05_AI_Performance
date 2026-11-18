#!/usr/bin/env python3
"""Generate docs/task3_flow.svg (continuous performance-testing flow chart)."""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parents[1] / "docs" / "task3_flow.svg"
W, H = 1400, 1260

parts: list[str] = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    "<defs><marker id='arrow' markerWidth='10' markerHeight='8' refX='9' refY='4' orient='auto'>"
    "<path d='M0,0 L10,4 L0,8 z' fill='#333'/></marker></defs>",
    f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
    '<text x="40" y="42" font-family="Segoe UI, Arial" font-size="24" font-weight="bold" fill="#1f4e79">'
    "Continuous performance testing — PR gate, nightly and release flow</text>",
    '<text x="40" y="68" font-family="Segoe UI, Arial" font-size="13" fill="#555">'
    "Short deterministic PR gate; expensive Stress/Spike/Endurance runs move to schedules.</text>",
]


def box(x: float, y: float, w: float, h: float, text: str, fill: str = "#eaf1f8", stroke: str = "#1f4e79") -> None:
    parts.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    )
    lines = text.split("\n")
    start = y + h / 2 - (len(lines) - 1) * 9
    for idx, line in enumerate(lines):
        parts.append(
            f'<text x="{x + w / 2}" y="{start + idx * 18}" text-anchor="middle" '
            f'font-family="Segoe UI, Arial" font-size="14" fill="#111">{escape(line)}</text>'
        )


def diamond(cx: float, cy: float, rx: float, ry: float, text: str) -> None:
    points = f"{cx},{cy - ry} {cx + rx},{cy} {cx},{cy + ry} {cx - rx},{cy}"
    parts.append(f'<polygon points="{points}" fill="#fff4e0" stroke="#b36b00" stroke-width="2"/>')
    lines = text.split("\n")
    start = cy - (len(lines) - 1) * 9
    for idx, line in enumerate(lines):
        parts.append(
            f'<text x="{cx}" y="{start + idx * 18}" text-anchor="middle" '
            f'font-family="Segoe UI, Arial" font-size="13" fill="#111">{escape(line)}</text>'
        )


def arrow(x1: float, y1: float, x2: float, y2: float, label: str = "", lx: float | None = None,
          ly: float | None = None, dashed: bool = False) -> None:
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    parts.append(
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#333" stroke-width="2" '
        f'marker-end="url(#arrow)"{dash}/>'
    )
    if label:
        parts.append(
            f'<text x="{lx if lx is not None else (x1 + x2) / 2 + 8}" '
            f'y="{ly if ly is not None else (y1 + y2) / 2 - 6}" '
            f'font-family="Segoe UI, Arial" font-size="12" fill="#333">{escape(label)}</text>'
        )


box(520, 100, 360, 56, "Push / pull request")
diamond(700, 225, 190, 55, "Runtime-affecting path\nor perf:full label?")
box(90, 200, 300, 64, "Skip perf gate\nunit + functional smoke", fill="#eeeeee", stroke="#666")
box(520, 330, 360, 56, "Provision clean SUT\nfixed commit + fixed dataset")
box(520, 420, 360, 56, "Health check + seed\n500 users / 205 products")
box(520, 510, 360, 56, "Warm-up 60 s + smoke load 5 min\nsame runner, think time, dataset")
box(520, 610, 360, 70, "Collect JTL + HTML + resource CSV\nwrite SHA-256 manifest")
box(520, 720, 360, 56, "Analyse p50/p95/p99, error %, RPS\nexclude expected 4xx")
diamond(700, 865, 205, 62, "Regression vs baseline?")
box(520, 980, 360, 56, "PASS\nstore artifact, update baseline", fill="#e8f5e9", stroke="#2e7d32")
box(1030, 830, 300, 70, "FAIL gate\nPR comment + artifact links", fill="#fdecea", stroke="#c62828")
box(1030, 940, 300, 56, "Developer investigates\nre-run once to rule out noise")
diamond(1180, 1080, 150, 55, "Confirmed\ntwice?")
box(1030, 1170, 300, 56, "Block merge / open\nperformance issue", fill="#fdecea", stroke="#c62828")
box(90, 590, 300, 56, "Nightly: stress 6 steps\n+ 15 min soak", fill="#e8f0fe", stroke="#1a4d8f")
box(90, 690, 300, 56, "Weekly / release candidate:\nfull Load + Stress + Spike", fill="#e8f0fe", stroke="#1a4d8f")

arrow(700, 156, 700, 170)
arrow(510, 225, 390, 225, "No (docs only)", 400, 212)
arrow(700, 280, 700, 330, "Yes", 712, 310)
arrow(700, 386, 700, 420)
arrow(700, 476, 700, 510)
arrow(700, 566, 700, 610)
arrow(700, 680, 700, 720)
arrow(700, 776, 700, 803)
arrow(700, 927, 700, 980, "No", 712, 955)
arrow(905, 865, 1030, 865, "Yes", 930, 850)
arrow(1180, 900, 1180, 940)
arrow(1180, 996, 1180, 1025)
arrow(1180, 1135, 1180, 1170, "Yes", 1192, 1157)
arrow(1030, 1085, 880, 1010, "No: pass with warning", 760, 1055, dashed=True)
arrow(390, 618, 520, 640, "artifacts", 405, 618, dashed=True)
arrow(390, 718, 520, 665, "artifacts", 405, 700, dashed=True)

legend_y = 40
parts += [
    f'<rect x="1010" y="{legend_y}" width="350" height="80" fill="#fafafa" stroke="#ccc"/>',
    f'<text x="1025" y="{legend_y + 22}" font-family="Segoe UI" font-size="13" font-weight="bold">Legend</text>',
    f'<rect x="1025" y="{legend_y + 34}" width="18" height="14" fill="#eaf1f8" stroke="#1f4e79"/>',
    f'<text x="1052" y="{legend_y + 46}" font-family="Segoe UI" font-size="12">process</text>',
    f'<polygon points="1140,{legend_y + 34} 1158,{legend_y + 41} 1140,{legend_y + 48} 1122,{legend_y + 41}" fill="#fff4e0" stroke="#b36b00"/>',
    f'<text x="1168" y="{legend_y + 46}" font-family="Segoe UI" font-size="12">decision</text>',
    f'<line x1="1250" y1="{legend_y + 41}" x2="1300" y2="{legend_y + 41}" stroke="#333" stroke-width="2" stroke-dasharray="6 4"/>',
    f'<text x="1308" y="{legend_y + 46}" font-family="Segoe UI" font-size="12">async</text>',
    "</svg>",
]
OUT.write_text("\n".join(parts), encoding="utf-8")
print(f"Wrote {OUT}")
