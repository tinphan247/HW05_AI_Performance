# Checkout stores the client-supplied total_amount without recomputing it

<!-- labels: bug, security, severity:high -->

## Summary

`POST /api/checkout` inserts `total_amount` from the request body. The server
never recalculates the cart total, so a client can create an order for any
amount (for example 1 VND) while the cart still contains a 30,000,000 VND item.

## Steps to reproduce

1. Log in as a seeded performance user.
2. Add product `1` (`iPhone 15 Pro Max`,
   price `30000000`) to the cart.
3. Call `POST /api/checkout` with `{"total_amount": 1, "shipping_address": "..."}`.

## Observed

- Checkout response: `{"message": "Checkout successful", "orderId": 1}`
- Stored order (`GET /api/orders/1`):
  `{"id": 1, "user_id": 3, "total_amount": 1, "status": "pending", "shipping_address": "HW05 repro address", "created_at": "2026-11-18 09:00:54"}`

## Expected

The server computes the order total from the cart/product prices (and applies
coupons server-side); client input must not decide the payable amount.

## Evidence

- Raw JSON: `evidence\issues\repro_20261118_160048.json`
- Source: `backend/server.js` lines 297-306
