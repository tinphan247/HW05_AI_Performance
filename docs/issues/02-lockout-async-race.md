# Concurrent wrong-password logins bypass the expected 403 on the third attempt

<!-- labels: bug, auth, severity:medium -->

## Summary

The lockout update is asynchronous (`db.run` without serialisation), so three
rapid wrong-password requests can all return `401` instead of ending with `403`.
The account does get locked in the database, but the client never receives the
lockout response.

## Steps to reproduce

1. Reset the lockout state for `lockout@eshop.test`.
2. Fire three wrong-password logins back-to-back (no delay).

## Observed

- HTTP statuses: `[401, 401, 403]`
- DB after: `{"login_attempts": 4, "locked_until": "2026-11-18T09:03:53.551Z"}`

With 1.5 s pacing the same sequence returns `[401, 401, 403]`; only the concurrent
case loses the final 403.

## Expected

The third response is `403` regardless of request pacing.

## Evidence

- Raw JSON: `evidence\issues\repro_20261118_160048.json`
