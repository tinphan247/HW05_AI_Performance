#!/usr/bin/env python3
"""Sample backend / JMeter / system resource usage during a test run.

Writes one CSV row every --interval seconds:

    timestamp,elapsed_s,backend_pid,backend_cpu_pct,backend_rss_mb,backend_vms_mb,
    backend_threads,backend_conns,jmeter_pid,jmeter_cpu_pct,jmeter_rss_mb,
    jmeter_threads,sys_cpu_pct,sys_ram_used_mb,sys_ram_available_mb

The backend PID is resolved from the listening TCP port (default 3100). The
JMeter PID is resolved from a Java process whose command line mentions JMeter.

Usage:
    python scripts/monitor_resources.py --out results/load/resources.csv
    python scripts/monitor_resources.py --out ... --port 3100 --interval 2

Stop with Ctrl+C; the file is flushed after every sample.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import time
from pathlib import Path

import psutil

HEADER = [
    "timestamp",
    "elapsed_s",
    "backend_pid",
    "backend_cpu_pct",
    "backend_rss_mb",
    "backend_vms_mb",
    "backend_threads",
    "backend_conns",
    "jmeter_pid",
    "jmeter_cpu_pct",
    "jmeter_rss_mb",
    "jmeter_threads",
    "sys_cpu_pct",
    "sys_ram_used_mb",
    "sys_ram_available_mb",
]


def find_pid_on_port(port: int) -> int | None:
    try:
        for conn in psutil.net_connections(kind="inet"):
            if conn.status == psutil.CONN_LISTEN and conn.laddr and conn.laddr.port == port:
                return conn.pid
    except (psutil.AccessDenied, OSError):
        pass
    # Fallback: match a node process whose command line mentions server.js
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmd = " ".join(proc.info.get("cmdline") or [])
            if proc.info.get("name", "").lower().startswith("node") and "server.js" in cmd:
                return proc.info["pid"]
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None


def find_jmeter_pid() -> int | None:
    candidates: list[tuple[int, int]] = []
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmd = " ".join(proc.info.get("cmdline") or []).lower()
            name = (proc.info.get("name") or "").lower()
            if "jmeter" in cmd:
                # Prefer the actual Java process over cmd.exe / jmeter.bat wrapper
                rank = 0 if name.startswith("java") else 1
                candidates.append((rank, proc.info["pid"]))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sorted(candidates)[0][1] if candidates else None


_PROC_CACHE: dict[int, psutil.Process] = {}


def get_proc(pid: int | None) -> psutil.Process | None:
    if not pid:
        return None
    proc = _PROC_CACHE.get(pid)
    try:
        if proc is None or not proc.is_running():
            proc = psutil.Process(pid)
            proc.cpu_percent(interval=None)  # prime the delta for this handle
            _PROC_CACHE[pid] = proc
        return proc
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def safe(proc: psutil.Process | None, attr: str, default=0.0):
    if proc is None:
        return default
    try:
        value = getattr(proc, attr)() if callable(getattr(proc, attr)) else getattr(proc, attr)
        return value
    except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
        return default


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--port", type=int, default=3100)
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    psutil.cpu_percent(interval=None)  # warm-up

    start = time.time()
    with args.out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(HEADER)
        fh.flush()

        while True:
            now = time.time()
            backend_pid = find_pid_on_port(args.port)
            backend = get_proc(backend_pid)
            jmeter_pid = find_jmeter_pid()
            jmeter = get_proc(jmeter_pid)

            backend_mem = safe(backend, "memory_info")
            jmeter_mem = safe(jmeter, "memory_info")
            vm = psutil.virtual_memory()

            writer.writerow(
                [
                    dt.datetime.now().astimezone().isoformat(timespec="seconds"),
                    round(now - start, 2),
                    backend_pid or "",
                    round(safe(backend, "cpu_percent"), 2),
                    round(getattr(backend_mem, "rss", 0) / 1024 / 1024, 2),
                    round(getattr(backend_mem, "vms", 0) / 1024 / 1024, 2),
                    safe(backend, "num_threads", 0),
                    len(safe(backend, "net_connections", [])) if backend else "",
                    jmeter_pid or "",
                    round(safe(jmeter, "cpu_percent"), 2),
                    round(getattr(jmeter_mem, "rss", 0) / 1024 / 1024, 2),
                    safe(jmeter, "num_threads", 0),
                    round(psutil.cpu_percent(interval=None), 2),
                    round(vm.used / 1024 / 1024, 2),
                    round(vm.available / 1024 / 1024, 2),
                ]
            )
            fh.flush()
            time.sleep(args.interval)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("monitor stopped")
