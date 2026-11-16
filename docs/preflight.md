# Preflight — HW05

**Date/time:** 2026-11-16 12:01 ICT  
**Student:** Phan Trung Tin — 23120372  
**Host:** DESKTOP-BCS88BQ (confirmed by student as the machine used in previous homework)

> This document records setup verification only. **No Load/Stress/Spike/Endurance test has been run.**

## 1. Toolchain

| Tool | Version / path | Status |
|---|---|---|
| Node.js | v25.1.0 — `C:\Program Files\nodejs\node.exe` | OK |
| npm | 11.7.0 | OK |
| Java | 17.0.12 — `C:\Program Files\Java\jdk-17\bin\java.exe` | OK |
| JMeter | 5.6.3 — `C:\HCMUS\hk7\Testing\apache-jmeter-5.6.3\bin\jmeter.bat` | OK |
| Python | 3.14.2 | OK |
| psutil | 7.1.3 | OK |
| matplotlib | Not installed | Optional; CSV/Excel fallback |
| sqlite3 CLI | `C:\msys64\ucrt64\bin\sqlite3.exe` | OK |

## 2. Hardware

| Item | Value |
|---|---|
| Hostname | `DESKTOP-BCS88BQ` |
| Model | Dell Latitude 7420 |
| CPU | 11th Gen Intel Core i5-1145G7, 4 cores / 8 logical processors |
| RAM | 16 GB (8 × 2 GB, 3733 MT/s) |
| GPU | Intel Iris Xe Graphics |
| OS | Windows 11 Pro, 10.0.26200, 64-bit |
| Disk C: | 236.9 GB total, 27.4 GB free at preflight |

## 3. SUT clone

| Item | Value |
|---|---|
| Source | `https://github.com/ttbhanh/eshop-sut.git` |
| Local path | `hw5/sut/eshop-sut` (git-ignored) |
| Commit | `85af3ba875c88283615e22cb108f13e2fccaf0e9` |
| Working tree | Clean official clone (no local modifications) |
| Backend port | **3100** for this test harness (official default is 3000; see `docs/sut_port_patch.md`) |
| Dependencies | `npm ci` completed: 135 packages |

## 4. Backend smoke check

Commands:

```powershell
cd hw5\sut\eshop-sut\backend
node database.js
node server.js
```

Observed:

```text
Database initialized and seeded (Phase 2).
Connected to database
Server is running on http://localhost:3100
```

HTTP check:

```text
GET http://localhost:3100/api/products -> HTTP 200, body length 914 bytes
```

Database counts after `node database.js`:

| Table | Count |
|---|---:|
| users | 2 |
| products | 5 |
| categories | 3 |
| orders | 0 |
| coupons | 4 |

The backend process was stopped after the smoke check.

### 4.1. Critical startup behavior (found during setup)

`server.js` requires `./database`, and `database.js` calls `initDatabase()` immediately at module load. Therefore **every backend start drops and reseeds the database**. A seed performed *before* starting the backend is lost.

Verified sequence that works:

```text
start backend (auto reset: 2 users / 5 products / 0 orders)
-> wait until listening on port 3100
-> run scripts/seed_perf_data.py while backend is running
-> verify 503 users / 205 products / 0 orders
```

Verified seed counts after running the seed script against the live backend:

| Table | Count |
|---|---:|
| users | 503 (2 seed + 500 perf + 1 lockout) |
| products | 205 (5 seed + 200 perf) |
| orders | 0 |

A smoke E2E check on `perf001@eshop.test` succeeded: login → cart → checkout (`orderId=1`) → my-orders (1). The state was then reset and the backend stopped.

## 5. Source-level facts relevant to test design

| Fact | Evidence |
|---|---|
| Official backend port is 3000 | `git show HEAD:backend/server.js` → `const PORT = 3000;` |
| The old local copy in `HW2/eshop-sut` was modified to port 3001 | `git diff` showing `process.env.PORT \|\| 3001`; not used for HW05 |
| Failed login increments attempts by **2** | `const newAttempts = user.login_attempts + 2;` |
| Lock duration is **180000 ms = 180 s** | `new Date(Date.now() + 180000)` |
| SRS says +1 and 30 s | `README.md` FR-02 |
| Checkout trusts client `total_amount` | `POST /api/checkout` inserts `req.body.total_amount` |
| Cart is in-memory | `const userCarts = {};` |
| Product list has no pagination | `SELECT * FROM products` |
| Product detail makes `price` a string for even IDs | `if (row.id % 2 === 0) row.price = row.price.toString();` |

These are inputs to the human review, not performance results.

## 6. Remote repo

`git ls-remote https://github.com/tinphan247/HW05_AI_Performance.git` returned exit code 0 with no refs → the remote repo exists and is currently empty.

## 7. Not done yet

- Test plans (`.jmx`) not created.
- CSV data not generated.
- Seed/reset scripts not written.
- No JMeter run.
- No screenshots/video.
- No AI audit entries beyond the planning phase (to be added).
