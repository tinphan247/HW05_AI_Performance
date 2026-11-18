# Product detail returns price as string for even IDs and number for odd IDs

<!-- labels: bug, api-contract, severity:low -->

## Summary

`GET /api/products/:id` converts `price` to a string only when `id % 2 === 0`.
Clients must therefore parse two different JSON types for the same field.

## Steps to reproduce

1. `GET /api/products/3`
2. `GET /api/products/4`

## Observed

- id 3: `45000000` (int)
- id 4: `"6000000"` (str)

## Expected

`price` is always a number (or always a string), with one documented contract.

## Evidence

- Raw JSON: `evidence\issues\repro_20261118_160048.json`
- Source: `backend/server.js` line 162
