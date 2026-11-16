#!/usr/bin/env python3
"""Reset volatile test state between scenarios.

What it does:
- clears login_attempts / locked_until for every user (lockout reset)
- deletes orders created by previous runs
- deletes coupon_usage rows
- resets sqlite AUTOINCREMENT counters for orders/coupon_usage (if present)

It does NOT delete users/products and does NOT clear the backend's in-memory
cart. Restarting the backend clears the cart but also drops/reseeds the DB
(database.js runs on startup), so reseed after a restart if you need the
performance dataset.

Usage:
    python scripts/reset_state.py
    python scripts/reset_state.py --db path/to/database.sqlite
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "sut" / "eshop-sut" / "backend" / "database.sqlite"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()

    if not args.db.exists():
        raise SystemExit(f"Database not found: {args.db}")

    conn = sqlite3.connect(args.db)
    try:
        conn.execute("BEGIN")
        conn.execute("UPDATE users SET login_attempts = 0, locked_until = NULL")
        conn.execute("DELETE FROM orders")
        conn.execute("DELETE FROM coupon_usage")
        for table in ("orders", "coupon_usage"):
            if conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'"
            ).fetchone():
                conn.execute("DELETE FROM sqlite_sequence WHERE name = ?", (table,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    conn = sqlite3.connect(args.db)
    try:
        locked = conn.execute(
            "SELECT COUNT(*) FROM users WHERE locked_until IS NOT NULL"
        ).fetchone()[0]
        counts = {
            "users": conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "products": conn.execute("SELECT COUNT(*) FROM products").fetchone()[0],
            "orders": conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
            "locked_users": locked,
        }
    finally:
        conn.close()

    print("Reset complete:", counts)
    print("Reminder: restart the backend to clear the in-memory cart.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
