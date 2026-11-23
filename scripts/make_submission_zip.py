#!/usr/bin/env python3
"""Build the HW05 submission zip.

Usage:
    python scripts/make_submission_zip.py
    python scripts/make_submission_zip.py --out C:\\path\\23120372_HW05_AI_Performance.zip

The archive contains the report, PDFs, evidence, plans, scripts, analysis and
all raw JTL/HTML result folders. It excludes .git, the SUT clone, node_modules,
the assignment PDF, temporary pilot results and Python caches.
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXCLUDE_DIRS = {
    ".git",
    "sut",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "pilot",
    "video_demo",
    "video_demo2",
}
EXCLUDE_SUFFIXES = {".pyc", ".tmp", ".bak"}
EXCLUDE_FILES = {"2026.HW05.Performance Testing_En.pdf"}


def include(path: Path, rel: Path) -> bool:
    if any(part in EXCLUDE_DIRS for part in rel.parts):
        return False
    if path.name in EXCLUDE_FILES:
        return False
    if path.suffix.lower() in EXCLUDE_SUFFIXES:
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "23120372_HW05_AI_Performance.zip")
    args = parser.parse_args()
    out = args.out if args.out.is_absolute() else ROOT / args.out
    if out.exists():
        out.unlink()

    count = 0
    total = 0
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT)
            if path == out:
                continue
            if not include(path, rel):
                continue
            zf.write(path, arcname=str(Path("hw5") / rel))
            count += 1
            total += path.stat().st_size

    print(f"Wrote {out}")
    print(f"Files: {count}; uncompressed: {total / (1024 * 1024):.1f} MB; zip: {out.stat().st_size / (1024 * 1024):.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
