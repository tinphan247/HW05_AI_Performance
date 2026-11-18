# GET /api/products returns every product and ignores limit/offset

<!-- labels: performance, severity:medium -->

## Summary

The product list endpoint always runs `SELECT * FROM products`; `limit` and
`offset` are ignored. The response grows linearly with the catalogue, which
inflates the read-heavy step and the bytes transferred per virtual user.

## Steps to reproduce

1. Seed 205 products.
2. `GET /api/products`
3. `GET /api/products?limit=5`

## Observed

- `GET /api/products`: HTTP 200, **205 items**,
  **25782 bytes**
- `limit=5` does not reduce the response.

## Expected

Paginated responses (for example `?page=&limit=`) with a documented maximum.

## Evidence

- Raw JSON: `evidence\issues\repro_20261118_160048.json`
- Source: `backend/server.js` lines 141-156
