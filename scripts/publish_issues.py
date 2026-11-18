#!/usr/bin/env python3
"""Publish docs/issues/*.md to GitHub Issues (idempotent by title).

Credentials: GITHUB_TOKEN env var, or the credential already stored for
github.com in git's credential helper. The token is never printed.

Usage:
    python scripts/publish_issues.py --dry-run
    python scripts/publish_issues.py
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ISSUES = ROOT / "docs" / "issues"
REPO = "tinphan247/HW05_AI_Performance"


def git_credential() -> tuple[str, str] | None:
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            text=True,
            capture_output=True,
            check=True,
        )
    except Exception:
        return None
    user = passwd = ""
    for line in proc.stdout.splitlines():
        if line.startswith("username="):
            user = line.split("=", 1)[1]
        elif line.startswith("password="):
            passwd = line.split("=", 1)[1]
    return (user, passwd) if passwd else None


def token() -> str:
    import os

    if os.environ.get("GITHUB_TOKEN"):
        return os.environ["GITHUB_TOKEN"]
    cred = git_credential()
    if cred:
        return cred[1]
    raise SystemExit("No GitHub token in GITHUB_TOKEN or git credential helper")


def api(method: str, path: str, body: dict | None = None) -> tuple[int, dict | list]:
    req = urllib.request.Request(
        "https://api.github.com" + path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
    )
    req.add_header("Authorization", f"Bearer {token()}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "HW05-issue-publisher")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode() or "{}")


def parse_issue(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    labels_match = re.search(r"<!--\s*labels:\s*(.+?)\s*-->", text)
    title = title_match.group(1).strip() if title_match else path.stem
    labels = [x.strip() for x in labels_match.group(1).split(",")] if labels_match else []
    body = re.sub(r"^#\s+.+\n+", "", text, count=1)
    body = re.sub(r"<!--\s*labels:.*?-->\n*", "", body, flags=re.DOTALL).strip()
    return {"file": path.name, "title": title, "labels": labels, "body": body}


def ensure_labels(labels: list[str]) -> None:
    status, existing = api("GET", f"/repos/{REPO}/labels?per_page=100")
    if status != 200 or not isinstance(existing, list):
        raise SystemExit(f"Cannot list labels: HTTP {status}")
    have = {item["name"] for item in existing}
    colors = {
        "severity:critical": "b60205",
        "severity:high": "d93f0b",
        "severity:medium": "fbca04",
        "severity:low": "0e8a16",
        "performance": "1d76db",
        "memory": "5319e7",
        "auth": "c2e0c6",
        "security": "ee0701",
        "api-contract": "bfdadc",
    }
    for label in labels:
        if label in have:
            continue
        code, body = api(
            "POST",
            f"/repos/{REPO}/labels",
            {"name": label, "color": colors.get(label, "ededed")},
        )
        print(f"LABEL {label}: HTTP {code}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    files = sorted(ISSUES.glob("*.md"))
    files = [f for f in files if not f.name.lower().startswith("readme")]
    if not files:
        raise SystemExit("No issue files found; run scripts/make_issues.py first")

    parsed = [parse_issue(f) for f in files]
    if not args.dry_run:
        ensure_labels(sorted({label for item in parsed for label in item["labels"]}))

    status, existing = api("GET", f"/repos/{REPO}/issues?state=all&per_page=100")
    if status != 200 or not isinstance(existing, list):
        raise SystemExit(f"Cannot list issues: HTTP {status} {existing}")
    by_title = {item["title"]: item for item in existing if "pull_request" not in item}

    results = []
    for issue in parsed:
        if issue["title"] in by_title:
            url = by_title[issue["title"]]["html_url"]
            print(f"SKIP  {issue['file']}: already {url}")
            results.append({**issue, "url": url, "action": "skipped"})
            continue
        if args.dry_run:
            print(f"DRY   {issue['file']}: {issue['title']} [{', '.join(issue['labels'])}]")
            results.append({**issue, "url": None, "action": "dry-run"})
            continue
        status, created = api(
            "POST",
            f"/repos/{REPO}/issues",
            {"title": issue["title"], "body": issue["body"], "labels": issue["labels"]},
        )
        if status not in (200, 201):
            print(f"ERROR {issue['file']}: HTTP {status} {created}")
            continue
        print(f"CREATE {issue['file']}: {created['html_url']}")
        results.append({**issue, "url": created["html_url"], "action": "created"})

    out = ISSUES / "published.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
