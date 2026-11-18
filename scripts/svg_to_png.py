#!/usr/bin/env python3
"""Rasterise an SVG chart to a real PNG using headless Chrome.

`plot_resources.py` emits SVG text (dependency-free). Browsers and Word can display
an SVG, but a file named `.png` must actually be PNG. This script keeps the two
artifacts separate: the SVG stays the editable source, the PNG is what gets embedded
in the report.

Usage:
    python scripts/svg_to_png.py screenshots/resource/load_resources.svg \
        --out screenshots/resource/load_resources.png --width 1200 --height 760
"""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

from md_to_pdf import find_chrome


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("svg", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=760)
    args = parser.parse_args()

    svg = args.svg.resolve()
    out = args.out.resolve()
    if not svg.exists():
        raise SystemExit(f"missing input: {svg}")
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()

    with tempfile.TemporaryDirectory() as tmp:
        # Screenshot writes <name>.png next to --screenshot path when a directory is given;
        # pointing at the exact path keeps the filename deterministic.
        shot = Path(tmp) / "shot.png"
        cmd = [
            str(find_chrome()),
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--disable-extensions",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            "--default-background-color=FFFFFFFF",
            f"--window-size={args.width},{args.height}",
            f"--screenshot={shot}",
            svg.as_uri(),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 or not shot.exists():
            raise SystemExit(f"Chrome failed ({result.returncode}): {result.stderr[-1500:]}")
        out.write_bytes(shot.read_bytes())

    print(f"Wrote {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
