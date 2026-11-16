#!/usr/bin/env python3
"""Seed deterministic performance-test data into the EShop SQLite database.

This script does NOT modify SUT source code or schema. It only inserts rows
into the existing tables created by backend/database.js.

IMPORTANT: start backend/server.js first and wait until it listens. Backend
startup loads database.js, which drops and reseeds the DB. Seeding before the
backend starts will be wiped.

Usage:
    python scripts/seed_perf_data.py
    python scripts/seed_perf_data.py --db path/to/database.sqlite
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "sut" / "eshop-sut" / "backend" / "database.sqlite"

PERF_USERS = 500
PERF_PRODUCTS = 200
PASSWORD = "Perf1234!"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()

    if not args.db.exists():
        raise SystemExit(f"Database not found: {args.db}\nRun: node database.js first.")

    conn = sqlite3.connect(args.db)
    try:
        conn.execute("BEGIN")

        # Users: perf001..perf500
        for i in range(1, PERF_USERS + 1):
            email = f"perf{i:03d}@eshop.test"
            row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if row is None:
                conn.execute(
                    "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                    (f"Perf User {i:03d}", email, PASSWORD, "user"),
                )

        # Dedicated lockout account
        row = conn.execute(
            "SELECT id FROM users WHERE email = ?", ("lockout@eshop.test",)
        ).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                ("Lockout User", "lockout@eshop.test", "Lockout123!", "user"),
            )

        # Products: 200 deterministic rows, category 1..3
        existing = conn.execute(
            "SELECT COUNT(*) FROM products WHERE name LIKE 'Perf Product %'"
        ).fetchone()[0]
        for i in range(existing + 1, PERF_PRODUCTS + 1):
            name = f"Perf Product {i:03d}"
            price = 100_000 + i * 10_000
            conn.execute(
                "INSERT INTO products (name, price, description, imageUrl, category_id) "
                "VALUES (?, ?, ?, ?, ?)",
                (name, price, f"Deterministic product {i:03d}", "", (i % 3) + 1),
            )

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    conn = sqlite3.connect(args.db)
    try:
        counts = {
            "users": conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "perf_users": conn.execute(
                "SELECT COUNT(*) FROM users WHERE email LIKE 'perf%@eshop.test'"
            ).fetchone()[0],
            "products": conn.execute("SELECT COUNT(*) FROM products").fetchone()[0],
            "perf_products": conn.execute(
                "SELECT COUNT(*) FROM products WHERE name LIKE 'Perf Product %'"
            ).fetchone()[0],
            "orders": conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
        }
    finally:
        conn.close()

    print("Seed complete:", counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
