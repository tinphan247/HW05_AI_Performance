# Failed login increments attempts by 2 and locks for 180 s (spec says +1 / 30 s)

<!-- labels: bug, auth, severity:high -->

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
| 1 | 401 | `{"error": "Invalid email or password"}` |
| 2 | 401 | `{"error": "Invalid email or password"}` |
| 3 | 403 | `{"error": "Tài khoản đã bị khóa. Vui lòng thử lại sau."}` |

- DB before: `{"login_attempts": 0, "locked_until": null}`
- DB after: `{"login_attempts": 4, "locked_until": "2026-11-18T09:03:50.520Z"}`
- Lock remaining when read: **177.0 s**

## Expected

- `login_attempts` increments by 1 per failure.
- Lock duration is 30 s.
- Third failure returns HTTP 403.

## Impact

A user is locked out six times longer than documented and reaches the lockout
after fewer real mistakes than the UI/spec implies. Automated clients that
retry a stale password can lock accounts much faster than expected.

## Evidence

- Raw JSON: `evidence\issues\repro_20261118_160048.json`
- Source: `backend/server.js` (`lockedUntil = new Date(Date.now() + 180000)`,
  `newAttempts = (user.login_attempts || 0) + 2`)
