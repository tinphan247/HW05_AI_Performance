#!/usr/bin/env python3
"""Turn repro_issues.py evidence into ready-to-post GitHub issue bodies.

Usage:
    python scripts/make_issues.py --evidence evidence/issues/repro_20261118_160000.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "issues"


def dump(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def write(slug: str, title: str, labels: str, body: str) -> None:
    path = OUT / f"{slug}.md"
    text = f"# {title}\n\n<!-- labels: {labels} -->\n\n{body.strip()}\n"
    path.write_text(text, encoding="utf-8")
    print(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    path = args.evidence if args.evidence.is_absolute() else ROOT / args.evidence
    ev = json.loads(path.read_text(encoding="utf-8"))
    checks = ev["checks"]
    OUT.mkdir(parents=True, exist_ok=True)

    lock = checks["lockout_sequential"]
    statuses = [r["status"] for r in lock["responses"]]
    attempts = "\n".join(
        f"| {i} | {r['status']} | `{dump(r['body'])}` |" for i, r in enumerate(lock["responses"], 1)
    )
    write(
        "01-lockout-threshold",
        "Failed login increments attempts by 2 and locks for 180 s (spec says +1 / 30 s)",
        "bug, auth, severity:high",
        f"""
## Summary

The login lockout does not match the documented behaviour: each failed attempt
adds **2** to `login_attempts` and the third failure locks the account for
**180 seconds**. The SRS/specification used for HW05 describes **+1 attempt**
and a **30-second** lock.

## Steps to reproduce

1. Ensure the backend is running with the seeded database.
2. Reset `login_attempts`/`locked_until` for `lockout@eshop.test`.
3. Send three wrong-password logins 1.5 s apart.

## Observed

| Attempt | HTTP | Body |
|---:|---:|---|
{attempts}

- DB before: `{dump(lock['db_before'])}`
- DB after: `{dump(lock['db_after'])}`
- Lock remaining when read: **{lock['locked_seconds_remaining']} s**

## Expected

- `login_attempts` increments by 1 per failure.
- Lock duration is 30 s.
- Third failure returns HTTP 403.

## Impact

A user is locked out six times longer than documented and reaches the lockout
after fewer real mistakes than the UI/spec implies. Automated clients that
retry a stale password can lock accounts much faster than expected.

## Evidence

- Raw JSON: `{path.relative_to(ROOT)}`
- Source: `backend/server.js` (`lockedUntil = new Date(Date.now() + 180000)`,
  `newAttempts = (user.login_attempts || 0) + 2`)
""",
    )

    race = checks["lockout_race"]
    write(
        "02-lockout-async-race",
        "Concurrent wrong-password logins bypass the expected 403 on the third attempt",
        "bug, auth, severity:medium",
        f"""
## Summary

The lockout update is asynchronous (`db.run` without serialisation), so three
rapid wrong-password requests can all return `401` instead of ending with `403`.
The account does get locked in the database, but the client never receives the
lockout response.

## Steps to reproduce

1. Reset the lockout state for `{lock['email']}`.
2. Fire three wrong-password logins back-to-back (no delay).

## Observed

- HTTP statuses: `{race['statuses']}`
- DB after: `{dump(race['db_after'])}`

With 1.5 s pacing the same sequence returns `{statuses}`; only the concurrent
case loses the final 403.

## Expected

The third response is `403` regardless of request pacing.

## Evidence

- Raw JSON: `{path.relative_to(ROOT)}`
""",
    )

    tamper = checks["checkout_total_tamper"]
    write(
        "03-checkout-total-tamper",
        "Checkout stores the client-supplied total_amount without recomputing it",
        "bug, security, severity:high",
        f"""
## Summary

`POST /api/checkout` inserts `total_amount` from the request body. The server
never recalculates the cart total, so a client can create an order for any
amount (for example 1 VND) while the cart still contains a 30,000,000 VND item.

## Steps to reproduce

1. Log in as a seeded performance user.
2. Add product `{tamper['product']['body'].get('id')}` (`{tamper['product']['body'].get('name')}`,
   price `{tamper['product']['body'].get('price')}`) to the cart.
3. Call `POST /api/checkout` with `{{"total_amount": 1, "shipping_address": "..."}}`.

## Observed

- Checkout response: `{dump(tamper['checkout']['body'])}`
- Stored order (`GET /api/orders/{tamper['checkout']['body'].get('orderId')}`):
  `{dump(tamper['stored_order']['body'])}`

## Expected

The server computes the order total from the cart/product prices (and applies
coupons server-side); client input must not decide the payable amount.

## Evidence

- Raw JSON: `{path.relative_to(ROOT)}`
- Source: `backend/server.js` lines 297-306
""",
    )

    cart = checks["cart_accumulation"]
    write(
        "04-cart-not-cleared",
        "Cart is never cleared after checkout and grows without bound in memory",
        "performance, memory, severity:medium",
        f"""
## Summary

`POST /api/checkout` creates the order but does not clear `userCarts[userId]`.
Repeated add-to-cart calls therefore accumulate items for the lifetime of the
process, and the cart is stored in an in-memory object rather than the database.

## Steps to reproduce

1. Log in as `{cart['email']}`.
2. Call `POST /api/cart` 25 times.
3. Call `GET /api/cart`.

## Observed

- Items before: {cart['cart_items_before']}
- Items after 25 adds: **{cart['cart_items_after']}**
- Last item: `{dump(cart['sample_last_item'])}`
- After a checkout the cart size stays the same (see the checkout evidence:
  before {len(tamper['cart_before']['body'] or [])}, after {len(tamper['cart_after']['body'] or [])}).

## Expected

Checkout clears the cart; carts are persisted or bounded and do not grow with
every request.

## Evidence

- Raw JSON: `{path.relative_to(ROOT)}`
- Source: `backend/server.js` lines 14, 284-306
""",
    )

    pag = checks["product_pagination"]
    write(
        "05-products-no-pagination",
        "GET /api/products returns every product and ignores limit/offset",
        "performance, severity:medium",
        f"""
## Summary

The product list endpoint always runs `SELECT * FROM products`; `limit` and
`offset` are ignored. The response grows linearly with the catalogue, which
inflates the read-heavy step and the bytes transferred per virtual user.

## Steps to reproduce

1. Seed 205 products.
2. `GET /api/products`
3. `GET /api/products?limit=5`

## Observed

- `GET /api/products`: HTTP {pag['response_status']}, **{pag['items']} items**,
  **{pag['bytes']} bytes**
- `limit=5` does not reduce the response.

## Expected

Paginated responses (for example `?page=&limit=`) with a documented maximum.

## Evidence

- Raw JSON: `{path.relative_to(ROOT)}`
- Source: `backend/server.js` lines 141-156
""",
    )

    price = checks["price_type"]
    write(
        "06-price-type-inconsistent",
        "Product detail returns price as string for even IDs and number for odd IDs",
        "bug, api-contract, severity:low",
        f"""
## Summary

`GET /api/products/:id` converts `price` to a string only when `id % 2 === 0`.
Clients must therefore parse two different JSON types for the same field.

## Steps to reproduce

1. `GET /api/products/3`
2. `GET /api/products/4`

## Observed

- id 3: `{dump(price['id_3_price'])}` ({price['id_3_type']})
- id 4: `{dump(price['id_4_price'])}` ({price['id_4_type']})

## Expected

`price` is always a number (or always a string), with one documented contract.

## Evidence

- Raw JSON: `{path.relative_to(ROOT)}`
- Source: `backend/server.js` line 162
""",
    )

    quote = checks["search_quote"]
    union = checks["search_union"]
    write(
        "07-search-sql-injection",
        "Product search concatenates raw input into SQL and returns 500 on a quote",
        "bug, security, severity:critical",
        f"""
## Summary

The search endpoint builds SQL with string interpolation:
`SELECT * FROM products WHERE name LIKE '%${{searchQuery}}%'`. A single quote
breaks the statement and a crafted payload can alter it.

## Steps to reproduce

1. `GET /api/products?search=%27` (a single quote)
2. `GET /api/products?search=%25%27%20UNION%20SELECT...`

## Observed

- `search='` -> HTTP **{quote['status']}**: `{dump(quote['body'])[:500]}`
- UNION payload -> HTTP **{union['status']}**: `{dump(union['body'])[:500]}`

## Expected

Parameterised queries (`WHERE name LIKE ?` with `%${{term}}%` as a bound
parameter) and a 400 for invalid input, not a database error.

## Impact

Besides the 500, the concatenation is a SQL-injection sink. Even where SQLite
blocks stacked statements, data can be exfiltrated with UNION/boolean payloads.

## Evidence

- Raw JSON: `{path.relative_to(ROOT)}`
- Source: `backend/server.js` line 144
""",
    )

    writes = checks["unauthenticated_product_write"]
    created = writes["create"]
    write(
        "08-unauthenticated-product-write",
        "Product create/update/delete endpoints do not require authentication",
        "bug, security, severity:critical",
        f"""
## Summary

`POST /api/products`, `PUT /api/products/:id` and `DELETE /api/products/:id` have
no `authenticateToken` middleware, unlike the admin and cart endpoints. Any
anonymous client can change the catalogue that every shopper reads.

## Steps to reproduce

1. `POST /api/products` with a JSON body and **no** Authorization header.
2. `PUT` and `DELETE` the returned id, still without a token.

## Observed

- POST -> HTTP **{created['status']}**: `{dump(created['body'])}`
- PUT -> HTTP **{writes['update']['status']}**
- DELETE -> HTTP **{writes['delete']['status']}**

## Expected

Only an authenticated administrator can mutate products (`401`/`403` otherwise).

## Evidence

- Raw JSON: `{path.relative_to(ROOT)}`
- Source: `backend/server.js` lines 167-195
""",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
