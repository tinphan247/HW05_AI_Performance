# Cart is never cleared after checkout and grows without bound in memory

<!-- labels: performance, memory, severity:medium -->

## Summary

`POST /api/checkout` creates the order but does not clear `userCarts[userId]`.
Repeated add-to-cart calls therefore accumulate items for the lifetime of the
process, and the cart is stored in an in-memory object rather than the database.

## Steps to reproduce

1. Log in as `perf002@eshop.test`.
2. Call `POST /api/cart` 25 times.
3. Call `GET /api/cart`.

## Observed

- Items before: 0
- Items after 25 adds: **25**
- Last item: `{"productId": 2, "price": 1, "quantity": 1}`
- After a checkout the cart size stays the same (see the checkout evidence:
  before 1, after 1).

## Expected

Checkout clears the cart; carts are persisted or bounded and do not grow with
every request.

## Evidence

- Raw JSON: `evidence\issues\repro_20261118_160048.json`
- Source: `backend/server.js` lines 14, 284-306
