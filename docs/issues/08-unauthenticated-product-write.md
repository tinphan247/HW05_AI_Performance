# Product create/update/delete endpoints do not require authentication

<!-- labels: bug, security, severity:critical -->

## Summary

`POST /api/products`, `PUT /api/products/:id` and `DELETE /api/products/:id` have
no `authenticateToken` middleware, unlike the admin and cart endpoints. Any
anonymous client can change the catalogue that every shopper reads.

## Steps to reproduce

1. `POST /api/products` with a JSON body and **no** Authorization header.
2. `PUT` and `DELETE` the returned id, still without a token.

## Observed

- POST -> HTTP **200**: `{"message": "Product created", "id": 206}`
- PUT -> HTTP **200**
- DELETE -> HTTP **200**

## Expected

Only an authenticated administrator can mutate products (`401`/`403` otherwise).

## Evidence

- Raw JSON: `evidence\issues\repro_20261118_160048.json`
- Source: `backend/server.js` lines 167-195
