#!/usr/bin/env python3
"""Run one JMeter scenario with resource monitoring and a run manifest.

The script does not start or restart the backend. Before running it verifies:

  * GET http://localhost:3100/api/products returns 200
  * DB counts match the seeded performance dataset (503 users / 205 products)
  * the DB order count is 0 (fresh state)

It then resets volatile state, starts scripts/monitor_resources.py, runs JMeter,
stops the monitor, and writes results/<scenario>/manifest.{md,json}.

Usage:
    python scripts/run_scenario.py --scenario load
    python scripts/run_scenario.py --scenario stress
    python scripts/run_scenario.py --scenario spike
    python scripts/run_scenario.py --scenario endurance --threads 30 --duration 720
    python scripts/run_scenario.py --scenario lockout --no-html

The JMX file is selected from test-plans/ using the current date unless
--plan is supplied.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import platform
import shutil
import socket
import sqlite3
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "sut" / "eshop-sut" / "backend" / "database.sqlite"
JMETER_HOME = Path(os.environ.get("JMETER_HOME", r"C:\HCMUS\hk7\Testing\apache-jmeter-5.6.3"))
JMETER = JMETER_HOME / "bin" / "jmeter.bat"
BASE_URL = "http://localhost:3100"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def db_counts() -> dict[str, int]:
    conn = sqlite3.connect(DB)
    try:
        return {
            "users": conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "products": conn.execute("SELECT COUNT(*) FROM products").fetchone()[0],
            "orders": conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
        }
    finally:
        conn.close()


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unknown"


def http_ok(url: str) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.status == 200, f"HTTP {resp.status}"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def resource_summary(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    if not rows:
        return {}

    def nums(key: str) -> list[float]:
        out = []
        for row in rows:
            try:
                out.append(float(row[key]))
            except (KeyError, ValueError):
                pass
        return out

    def stats(key: str) -> dict[str, float]:
        values = nums(key)
        if not values:
            return {}
        return {"min": min(values), "max": max(values), "avg": sum(values) / len(values)}

    backend_rss = nums("backend_rss_mb")
    backend_pid = rows[0].get("backend_pid") or None
    return {
        "samples": len(rows),
        "backend_pid": backend_pid,
        "backend_cpu_pct": stats("backend_cpu_pct"),
        "backend_rss_mb": stats("backend_rss_mb"),
        "backend_rss_start_mb": backend_rss[0] if backend_rss else None,
        "backend_rss_end_mb": backend_rss[-1] if backend_rss else None,
        "jmeter_cpu_pct": stats("jmeter_cpu_pct"),
        "jmeter_rss_mb": stats("jmeter_rss_mb"),
        "sys_cpu_pct": stats("sys_cpu_pct"),
        "sys_ram_available_mb": stats("sys_ram_available_mb"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True, choices=["load", "stress", "spike", "endurance", "lockout"])
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--date", default=dt.date.today().strftime("%Y%m%d"))
    parser.add_argument("--threads", type=int)
    parser.add_argument("--ramp", type=int)
    parser.add_argument("--duration", type=int)
    parser.add_argument("--no-html", action="store_true")
    parser.add_argument("--skip-reset", action="store_true")
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    scenario = args.scenario
    title = scenario.capitalize()

    plan = args.plan
    if plan is None:
        plan = ROOT / "test-plans" / f"23120372_{title}_{args.date}.jmx"
    if not plan.is_absolute():
        plan = ROOT / plan
    if not plan.exists():
        raise SystemExit(f"Test plan not found: {plan}")

    out_dir = ROOT / "results" / scenario
    out_dir.mkdir(parents=True, exist_ok=True)
    jtl = out_dir / f"{plan.stem}.jtl"
    log = out_dir / "jmeter.log"
    resources = out_dir / "resources.csv"
    html_dir = out_dir / "html"

    # --- preflight -------------------------------------------------------
    ok, message = http_ok(f"{BASE_URL}/api/products")
    if not ok:
        raise SystemExit(f"Backend is not reachable on 3100: {message}")
    counts = db_counts()
    if counts["users"] < 503 or counts["products"] < 205:
        raise SystemExit(f"Dataset not seeded: {counts}. Start backend, then run seed_perf_data.py.")
    if counts["orders"] != 0 and not args.skip_reset:
        print(f"Orders before reset: {counts['orders']} (will be cleared)")
    if not args.skip_reset:
        subprocess.run([sys.executable, str(ROOT / "scripts" / "reset_state.py")], check=True, cwd=ROOT)
    pre_counts = db_counts()

    # --- clean outputs ---------------------------------------------------
    if jtl.exists():
        jtl.unlink()
    if html_dir.exists():
        shutil.rmtree(html_dir)
    if resources.exists():
        resources.unlink()

    props = ["-Jhost=localhost", "-Jport=3100", "-Jcsv=data/e2e_data.csv"]
    if args.threads is not None:
        props.append(f"-Jthreads={args.threads}")
    if args.ramp is not None:
        props.append(f"-Jramp={args.ramp}")
    if args.duration is not None:
        props.append(f"-Jduration={args.duration}")

    cmd = ["cmd", "/c", str(JMETER), "-n", "-t", str(plan), "-l", str(jtl), "-j", str(log), *props]
    if not args.no_html:
        cmd += ["-e", "-o", str(html_dir)]
    print("RUN:", " ".join(cmd))

    monitor = subprocess.Popen(
        [
            sys.executable,
            str(ROOT / "scripts" / "monitor_resources.py"),
            "--out",
            str(resources),
            "--port",
            "3100",
        ],
        cwd=ROOT,
    )

    started = dt.datetime.now().astimezone()
    t0 = time.time()
    try:
        completed = subprocess.run(cmd, cwd=ROOT)
    finally:
        monitor.terminate()
        try:
            monitor.wait(timeout=10)
        except subprocess.TimeoutExpired:
            monitor.kill()
    elapsed = time.time() - t0
    ended = dt.datetime.now().astimezone()

    post_counts = db_counts()
    res = resource_summary(resources)

    # JTL summary (includes Transaction Controller parent samples; per-sampler
    # analysis is done separately in scripts/analyze_jtl.py)
    rows = list(csv.DictReader(jtl.open(encoding="utf-8", errors="replace")))
    samples = len(rows)
    failures = sum(1 for r in rows if r.get("success") != "true")
    elapsed_values = [float(r["elapsed"]) for r in rows if r.get("elapsed")]
    avg_ms = sum(elapsed_values) / len(elapsed_values) if elapsed_values else 0.0
    max_ms = max(elapsed_values) if elapsed_values else 0.0

    manifest = {
        "scenario": scenario,
        "student_id": "23120372",
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "started": started.isoformat(timespec="seconds"),
        "ended": ended.isoformat(timespec="seconds"),
        "elapsed_s": round(elapsed, 2),
        "jmeter_exit_code": completed.returncode,
        "command": " ".join(cmd),
        "plan": str(plan.relative_to(ROOT)),
        "plan_sha256": sha256(plan),
        "jtl": str(jtl.relative_to(ROOT)),
        "jtl_sha256": sha256(jtl),
        "csv": "data/e2e_data.csv",
        "csv_sha256": sha256(ROOT / "data" / "e2e_data.csv"),
        "db_counts_before": pre_counts,
        "db_counts_after": post_counts,
        "samples": samples,
        "failed_samples": failures,
        "avg_elapsed_ms_all_samples": round(avg_ms, 2),
        "max_elapsed_ms_all_samples": round(max_ms, 2),
        "resources": res,
        "backend_pid": (res or {}).get("backend_pid"),
        "app_git_commit": git_head(),
        "sut_commit": (ROOT / "docs" / "sut_commit.txt").read_text(encoding="utf-8").strip(),
        "note": args.note,
    }

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        f"# Run manifest — {title}",
        "",
        f"- Scenario: **{title}**",
        f"- Started: {manifest['started']}",
        f"- Ended: {manifest['ended']} (elapsed {manifest['elapsed_s']} s)",
        f"- JMeter exit code: {completed.returncode}",
        f"- Test plan: `{manifest['plan']}` (SHA-256 `{manifest['plan_sha256']}`)",
        f"- JTL: `{manifest['jtl']}` (SHA-256 `{manifest['jtl_sha256']}`)",
        f"- CSV: `{manifest['csv']}` (SHA-256 `{manifest['csv_sha256']}`)",
        f"- Samples: {samples}; failed: {failures}",
        f"- Avg elapsed (all samples): {manifest['avg_elapsed_ms_all_samples']} ms; max: {manifest['max_elapsed_ms_all_samples']} ms",
        f"- DB counts before: {pre_counts}",
        f"- DB counts after: {post_counts}",
        f"- Backend PID: {manifest['backend_pid']}",
        f"- Host: {manifest['hostname']} — {manifest['platform']}",
        f"- HW05 git commit: `{manifest['app_git_commit']}`",
        f"- SUT commit: `{manifest['sut_commit']}`",
        f"- JMeter command: `{manifest['command']}`",
        "",
        "## Resource summary",
        "",
    ]
    if res:
        md += [
            "| Metric | Min | Avg | Max |",
            "|---|---:|---:|---:|",
        ]
        for key, label in (
            ("backend_cpu_pct", "Backend CPU %"),
            ("backend_rss_mb", "Backend RSS MB"),
            ("jmeter_cpu_pct", "JMeter CPU %"),
            ("jmeter_rss_mb", "JMeter RSS MB"),
            ("sys_cpu_pct", "System CPU %"),
            ("sys_ram_available_mb", "System RAM available MB"),
        ):
            s = res.get(key) or {}
            md.append(f"| {label} | {s.get('min', '')} | {s.get('avg', '')} | {s.get('max', '')} |")
        md += [
            "",
            f"- Backend RSS start/end: {res.get('backend_rss_start_mb')} / {res.get('backend_rss_end_mb')} MB",
            f"- Resource samples: {res.get('samples')}",
        ]
    else:
        md.append("No resource samples captured.")

    if args.note:
        md += ["", "## Note", "", args.note]

    (out_dir / "manifest.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print("\n".join(md))
    return 0 if completed.returncode == 0 else completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
