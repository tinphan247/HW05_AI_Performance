#!/usr/bin/env python3
"""Generate deterministic CSV input for the JMeter E2E workflow.

Outputs:
    data/e2e_data.csv   -- 500 rows: credentials + product + order payload
    data/lockout.csv    -- one dedicated lockout account

The script reads the seeded SQLite database, so product IDs/prices match the
actual SUT dataset. It does not invent product names or prices.

Usage:
    python scripts/generate_csv.py
    python scripts/generate_csv.py --db path/to/database.sqlite --rows 500
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "sut" / "eshop-sut" / "backend" / "database.sqlite"
E2E_CSV = ROOT / "data" / "e2e_data.csv"
LOCKOUT_CSV = ROOT / "data" / "lockout.csv"

HEADER = [
    "email",
    "password",
    "product_id",
    "product_name",
    "price",
    "quantity",
    "search_keyword",
    "shipping_address",
    "total_amount",
]

KEYWORDS = {
    "iPhone": "iPhone",
    "Samsung": "Galaxy",
    "MacBook": "MacBook",
    "Tai nghe": "AirPods",
    "Bàn phím": "Keychron",
}


def keyword_for(name: str) -> str:
    for prefix, keyword in KEYWORDS.items():
        if name.startswith(prefix):
            return keyword
    if name.startswith("Perf Product"):
        return "Perf"
    return name.split()[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--rows", type=int, default=500)
    args = parser.parse_args()

    if not args.db.exists():
        raise SystemExit(f"Database not found: {args.db}\nRun database.js + seed_perf_data.py first.")
    if args.rows < 1:
        raise SystemExit("--rows must be >= 1")

    conn = sqlite3.connect(args.db)
    try:
        users = [
            r[0]
            for r in conn.execute(
                "SELECT email FROM users WHERE email LIKE 'perf%@eshop.test' ORDER BY id"
            )
        ]
        products = [
            (r[0], r[1], r[2])
            for r in conn.execute("SELECT id, name, price FROM products ORDER BY id")
        ]
    finally:
        conn.close()

    if not users:
        raise SystemExit("No perf users found. Run seed_perf_data.py first.")
    if not products:
        raise SystemExit("No products found. Run database.js first.")

    E2E_CSV.parent.mkdir(parents=True, exist_ok=True)
    with E2E_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(HEADER)
        for i in range(args.rows):
            email = users[i % len(users)]
            product_id, product_name, price = products[i % len(products)]
            quantity = (i % 3) + 1
            total = int(price) * quantity
            address = f"{100 + (i % 800)} Nguyen Trai Q{(i % 12) + 1} HCM"
            writer.writerow(
                [
                    email,
                    "Perf1234!",
                    product_id,
                    product_name,
                    price,
                    quantity,
                    keyword_for(product_name),
                    address,
                    total,
                ]
            )

    with LOCKOUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["email", "wrong_password"])
        writer.writerow(["lockout@eshop.test", "DefinitelyWrong!123"])

    print(f"Wrote {E2E_CSV} ({args.rows} rows)")
    print(f"Wrote {LOCKOUT_CSV} (1 row)")
    print(f"Users available: {len(users)}; products available: {len(products)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
