# Product search concatenates raw input into SQL and returns 500 on a quote

<!-- labels: bug, security, severity:critical -->

## Summary

The search endpoint builds SQL with string interpolation:
`SELECT * FROM products WHERE name LIKE '%${searchQuery}%'`. A single quote
breaks the statement and a crafted payload can alter it.

## Steps to reproduce

1. `GET /api/products?search=%27` (a single quote)
2. `GET /api/products?search=%25%27%20UNION%20SELECT...`

## Observed

- `search='` -> HTTP **500**: `"<h1>Database Error</h1><p>SQLITE_ERROR: unrecognized token: \"'\"</p>"`
- UNION payload -> HTTP **500**: `"<h1>Database Error</h1><p>SQLITE_ERROR: SELECTs to the left and right of UNION do not have the same number of result columns</p>"`

## Expected

Parameterised queries (`WHERE name LIKE ?` with `%${term}%` as a bound
parameter) and a 400 for invalid input, not a database error.

## Impact

Besides the 500, the concatenation is a SQL-injection sink. Even where SQLite
blocks stacked statements, data can be exfiltrated with UNION/boolean payloads.

## Evidence

- Raw JSON: `evidence\issues\repro_20261118_160048.json`
- Source: `backend/server.js` line 144
