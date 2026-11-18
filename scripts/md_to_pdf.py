#!/usr/bin/env python3
"""Convert a Markdown report to PDF using Python-Markdown + headless Chrome.

No LaTeX or pandoc required. Images referenced with relative paths are resolved
from the Markdown file's directory.

Usage:
    python scripts/md_to_pdf.py reports/Main_Report.md
    python scripts/md_to_pdf.py docs/ai_critique.md --out reports/AI_Critique.pdf
"""

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
from pathlib import Path

import markdown

CHROME_CANDIDATES = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]

CSS = """
@page { size: A4; margin: 16mm 14mm; }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 10.5pt; line-height: 1.45; color: #1a1a1a; }
h1 { font-size: 20pt; border-bottom: 2px solid #1f4e79; padding-bottom: 4px; color: #1f4e79; }
h2 { font-size: 15pt; margin-top: 22px; color: #1f4e79; border-bottom: 1px solid #d0d7de; }
h3 { font-size: 12.5pt; margin-top: 16px; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 9pt; }
th, td { border: 1px solid #b8c2cc; padding: 4px 6px; vertical-align: top; }
th { background: #eaf1f8; text-align: left; }
tr:nth-child(even) td { background: #fafcfe; }
code { background: #f2f4f7; padding: 1px 3px; border-radius: 3px; font-family: Consolas, monospace; font-size: 9pt; }
pre { background: #f6f8fa; border: 1px solid #d0d7de; padding: 10px; overflow-x: auto; page-break-inside: avoid; }
pre code { background: none; padding: 0; }
blockquote { border-left: 4px solid #1f4e79; margin: 8px 0; padding: 4px 12px; background: #f7fafd; color: #333; }
img { max-width: 100%; page-break-inside: avoid; }
.page-break { page-break-before: always; }
.small { font-size: 9pt; color: #555; }
"""


def find_chrome() -> Path:
    for path in CHROME_CANDIDATES:
        if path.exists():
            return path
    raise SystemExit("Chrome/Edge not found. Install Chrome or edit CHROME_CANDIDATES.")


def convert(md_path: Path, out_pdf: Path) -> None:
    text = md_path.read_text(encoding="utf-8")
    html_body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"],
    )
    # Allow explicit page breaks with <div class="page-break"></div> already in HTML.
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<base href="{md_path.parent.as_uri()}/">
<style>{CSS}</style></head>
<body>{html_body}</body></html>"""

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "report.html"
        html_path.write_text(html, encoding="utf-8")
        chrome = find_chrome()
        cmd = [
            str(chrome),
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--disable-extensions",
            "--no-pdf-header-footer",
            f"--print-to-pdf={out_pdf}",
            html_path.as_uri(),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise SystemExit(f"Chrome failed ({result.returncode}): {result.stderr[-2000:]}")
    if not out_pdf.exists() or out_pdf.stat().st_size == 0:
        raise SystemExit(f"PDF not created: {out_pdf}")
    print(f"Wrote {out_pdf} ({out_pdf.stat().st_size} bytes)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("md", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    out = args.out or args.md.with_suffix(".pdf")
    md_path = args.md.resolve()
    out = out.resolve()
    convert(md_path, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
