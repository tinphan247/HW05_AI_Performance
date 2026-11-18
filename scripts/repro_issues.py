#!/usr/bin/env python3
"""Reproduce the defects reported for the EShop SUT (HW05).

Every check prints the raw request/response values to `evidence/issues/` so the
GitHub issue bodies can cite observed behaviour instead of assumptions. The
script also reads the SQLite database for the lockout counters, which are not
exposed through the API.

It assumes the backend runs on http://localhost:3100 with the performance
dataset seeded (503 users / 205 products) and no load test in progress.

Usage:
    python scripts/repro_issues.py
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import socket
import sqlite3
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "sut" / "eshop-sut" / "backend" / "database.sqlite"
BASE = "http://localhost:3100"
OUT = ROOT / "evidence" / "issues"
LOCKOUT_EMAIL = "lockout@eshop.test"


def http(method: str, path: str, body: dict | None = None, token: str | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read()
            status = resp.status
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        status = exc.code
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    text = raw.decode("utf-8", "replace")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = None
    return {
        "method": method,
        "path": path,
        "request_body": body,
        "status": status,
        "elapsed_ms": elapsed_ms,
        "bytes": len(raw),
        "body": parsed if parsed is not None else text[:2000],
    }


def login(email: str, password: str) -> dict:
    return http("POST", "/api/login", {"email": email, "password": password})


def db_row(sql: str, params: tuple = ()) -> dict | None:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(sql, params).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def reset_lockout() -> None:
    conn = sqlite3.connect(DB)
    try:
        conn.execute(
            "UPDATE users SET login_attempts = 0, locked_until = NULL WHERE email = ?",
            (LOCKOUT_EMAIL,),
        )
        conn.commit()
    finally:
        conn.close()


def csv_user(index: int = 0) -> dict:
    with (ROOT / "data" / "e2e_data.csv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return rows[index]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now().astimezone()
    report: dict = {
        "started": started.isoformat(timespec="seconds"),
        "host": socket.gethostname(),
        "base_url": BASE,
        "checks": {},
    }

    # ---------------------------------------------------------------- lockout
    reset_lockout()
    before = db_row("SELECT login_attempts, locked_until FROM users WHERE email = ?", (LOCKOUT_EMAIL,))
    attempts = []
    for _ in range(3):
        attempts.append(login(LOCKOUT_EMAIL, "DefinitelyWrong!"))
        time.sleep(1.5)
    after = db_row("SELECT login_attempts, locked_until FROM users WHERE email = ?", (LOCKOUT_EMAIL,))
    locked_seconds = None
    if after and after.get("locked_until"):
        locked_until = dt.datetime.fromisoformat(after["locked_until"].replace("Z", "+00:00"))
        locked_seconds = round((locked_until - dt.datetime.now(dt.timezone.utc)).total_seconds(), 1)
    report["checks"]["lockout_sequential"] = {
        "email": LOCKOUT_EMAIL,
        "db_before": before,
        "responses": attempts,
        "db_after": after,
        "locked_seconds_remaining": locked_seconds,
    }

    # ------------------------------------------------- async lockout race
    reset_lockout()
    race = []
    for _ in range(3):
        race.append(login(LOCKOUT_EMAIL, "DefinitelyWrong!"))
    time.sleep(1.0)
    report["checks"]["lockout_race"] = {
        "responses": race,
        "statuses": [r["status"] for r in race],
        "db_after": db_row(
            "SELECT login_attempts, locked_until FROM users WHERE email = ?", (LOCKOUT_EMAIL,)
        ),
    }
    reset_lockout()

    # ------------------------------------------------------- checkout tamper
    user = csv_user(0)
    login_res = login(user["email"], user["password"])
    token = login_res["body"].get("token") if isinstance(login_res["body"], dict) else None
    if not token:
        raise SystemExit(f"Cannot log in {user['email']}: {login_res}")
    product_id = int(user["product_id"])
    product = http("GET", f"/api/products/{product_id}")
    add = http(
        "POST",
        "/api/cart",
        {
            "productId": product_id,
            "name": user["product_name"],
            "price": float(user["price"]),
            "quantity": 1,
        },
        token,
    )
    cart_before = http("GET", "/api/cart", token=token)
    tampered_total = 1
    checkout = http(
        "POST",
        "/api/checkout",
        {"total_amount": tampered_total, "shipping_address": "HW05 repro address"},
        token,
    )
    order_id = checkout["body"].get("orderId") if isinstance(checkout["body"], dict) else None
    stored_order = http("GET", f"/api/orders/{order_id}") if order_id else None
    cart_after = http("GET", "/api/cart", token=token)
    report["checks"]["checkout_total_tamper"] = {
        "login": {k: login_res[k] for k in ("status", "elapsed_ms")},
        "product": product,
        "add_to_cart": add,
        "cart_before": cart_before,
        "requested_total_amount": tampered_total,
        "checkout": checkout,
        "stored_order": stored_order,
        "cart_after": cart_after,
    }

    # ------------------------------------------------- cart grows per request
    growth_user = csv_user(1)
    growth_login = login(growth_user["email"], growth_user["password"])
    growth_token = growth_login["body"].get("token") if isinstance(growth_login["body"], dict) else None
    if not growth_token:
        raise SystemExit(f"Cannot log in {growth_user['email']}: {growth_login}")
    before_len = len(http("GET", "/api/cart", token=growth_token)["body"] or [])
    for _ in range(25):
        http(
            "POST",
            "/api/cart",
            {"productId": int(growth_user["product_id"]), "price": 1, "quantity": 1},
            growth_token,
        )
    after_cart = http("GET", "/api/cart", token=growth_token)
    report["checks"]["cart_accumulation"] = {
        "email": growth_user["email"],
        "cart_items_before": before_len,
        "cart_items_after": len(after_cart["body"] or []),
        "sample_last_item": (after_cart["body"] or [None])[-1],
    }

    # ------------------------------------------------------------- pagination
    products = http("GET", "/api/products")
    report["checks"]["product_pagination"] = {
        "response_status": products["status"],
        "bytes": products["bytes"],
        "items": len(products["body"] or []),
        "query_supports_limit": "limit" in str(http("GET", "/api/products?limit=5")["body"]),
    }

    # ------------------------------------------------------------ price types
    odd = http("GET", "/api/products/3")
    even = http("GET", "/api/products/4")
    report["checks"]["price_type"] = {
        "id_3_price": odd["body"].get("price") if isinstance(odd["body"], dict) else odd["body"],
        "id_3_type": type(odd["body"].get("price")).__name__ if isinstance(odd["body"], dict) else None,
        "id_4_price": even["body"].get("price") if isinstance(even["body"], dict) else even["body"],
        "id_4_type": type(even["body"].get("price")).__name__ if isinstance(even["body"], dict) else None,
    }

    # ------------------------------------------------------------ SQL quoting
    report["checks"]["search_quote"] = http("GET", "/api/products?search=%27")
    report["checks"]["search_union"] = http("GET", "/api/products?search=%25%27%20UNION%20SELECT%201,2,3,4,5,6,7,8,9,10--")

    # --------------------------------------------------------- unauthenticated
    created = http(
        "POST",
        "/api/products",
        {
            "name": "HW05 unauth probe",
            "price": 123,
            "description": "created without Authorization header",
            "imageUrl": "",
            "category_id": 1,
        },
    )
    new_id = created["body"].get("id") if isinstance(created["body"], dict) else None
    updated = http("PUT", f"/api/products/{new_id}", {"name": "HW05 unauth probe updated", "price": 456}) if new_id else None
    deleted = http("DELETE", f"/api/products/{new_id}") if new_id else None
    report["checks"]["unauthenticated_product_write"] = {
        "create": created,
        "update": updated,
        "delete": deleted,
    }

    report["checks"]["db_counts"] = {
        "users": db_row("SELECT COUNT(*) AS n FROM users")["n"],
        "products": db_row("SELECT COUNT(*) AS n FROM products")["n"],
        "orders": db_row("SELECT COUNT(*) AS n FROM orders")["n"],
    }
    report["finished"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")

    stamp = started.strftime("%Y%m%d_%H%M%S")
    json_path = OUT / f"repro_{stamp}.json"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lock = report["checks"]["lockout_sequential"]
    tamper = report["checks"]["checkout_total_tamper"]
    lines = [
        "# Repro evidence",
        "",
        f"- Started: {report['started']}",
        f"- Host: `{report['host']}`",
        f"- Base URL: {BASE}",
        f"- Raw JSON: `{json_path.relative_to(ROOT)}`",
        "",
        "## 1. Failed-login lockout",
        "",
        "| Attempt | HTTP | Body |",
        "|---:|---:|---|",
    ]
    for i, resp in enumerate(lock["responses"], 1):
        lines.append(f"| {i} | {resp['status']} | `{json.dumps(resp['body'], ensure_ascii=False)}` |")
    lines += [
        "",
        f"- DB before: `{json.dumps(lock['db_before'], ensure_ascii=False)}`",
        f"- DB after: `{json.dumps(lock['db_after'], ensure_ascii=False)}`",
        f"- Lock remaining when read: **{lock['locked_seconds_remaining']} s**",
        f"- Rapid-fire variant statuses: `{report['checks']['lockout_race']['statuses']}`",
        "",
        "## 2. Checkout trusts client total_amount",
        "",
        f"- Cart size before checkout: {len(tamper['cart_before']['body'] or [])}",
        f"- Client sent `total_amount={tamper['requested_total_amount']}` for product priced "
        f"{tamper['product']['body'].get('price')}",
        f"- Checkout response: `{json.dumps(tamper['checkout']['body'], ensure_ascii=False)}`",
        f"- Stored order: `{json.dumps(tamper['stored_order']['body'], ensure_ascii=False)}`",
        f"- Cart size after checkout: {len(tamper['cart_after']['body'] or [])}",
        "",
        "## 3. Cart accumulation",
        "",
        f"- Items before: {report['checks']['cart_accumulation']['cart_items_before']}",
        f"- Items after 25 adds: {report['checks']['cart_accumulation']['cart_items_after']}",
        "",
        "## 4. Product list size",
        "",
        f"- HTTP {report['checks']['product_pagination']['response_status']}, "
        f"{report['checks']['product_pagination']['items']} items, "
        f"{report['checks']['product_pagination']['bytes']} bytes",
        "",
        "## 5. Price type by id parity",
        "",
        f"- id 3: `{report['checks']['price_type']['id_3_price']}` ({report['checks']['price_type']['id_3_type']})",
        f"- id 4: `{report['checks']['price_type']['id_4_price']}` ({report['checks']['price_type']['id_4_type']})",
        "",
        "## 6. Search quoting",
        "",
        f"- `search='` -> HTTP {report['checks']['search_quote']['status']}: "
        f"`{json.dumps(report['checks']['search_quote']['body'], ensure_ascii=False)}`",
        f"- UNION payload -> HTTP {report['checks']['search_union']['status']}: "
        f"`{json.dumps(report['checks']['search_union']['body'], ensure_ascii=False)[:400]}`",
        "",
        "## 7. Unauthenticated product write",
        "",
        f"- POST -> HTTP {report['checks']['unauthenticated_product_write']['create']['status']}: "
        f"`{json.dumps(report['checks']['unauthenticated_product_write']['create']['body'], ensure_ascii=False)}`",
        f"- PUT -> HTTP {report['checks']['unauthenticated_product_write']['update']['status']}",
        f"- DELETE -> HTTP {report['checks']['unauthenticated_product_write']['delete']['status']}",
        "",
    ]
    md_path = OUT / f"repro_{stamp}.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
