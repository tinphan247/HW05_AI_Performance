# HW05 — Performance Testing — EShop

**Student:** Phan Trung Tin — **MSSV:** 23120372  
**Course:** Software Testing — FIT, VNUHCM  
**SUT:** EShop — https://github.com/ttbhanh/eshop-sut  
**Submission repo:** https://github.com/tinphan247/HW05_AI_Performance

> **Status:** In progress. Preflight, seed data, three JMX plans and the runner tooling are complete.
> Load/Stress/Spike/Endurance runs are being executed; **result tables below are filled only from the real `.jtl` logs, resource CSV, and screenshots**.
> The detailed plan is in `PLAN.md`.

---

## 1. Confirmed decisions

| Item | Decision |
|---|---|
| Repo | `https://github.com/tinphan247/HW05_AI_Performance` |
| Hardware | `DESKTOP-BCS88BQ` — confirmed as the machine used in previous homework |
| Seed dataset | Approved: seed additional test users/products via an external script (no SUT code changes) |
| Second load-generator machine | Not available; JMeter and backend run on the same host |
| AI tool | Declared by actual model used in the session (OpenCode / DeepSeek V4.1 Flash Free when applicable) |
| Group workflow | Student confirmed no duplicate workflow; member list still to be recorded in `docs/group_scope.md` |
| Video | Deferred; will be recorded and uploaded as unlisted YouTube before submission |
| Deadline | “Next week” (exact Moodle deadline to be added when confirmed) |

---

## 2. Repository layout

```
hw5/
  PLAN.md                     # detailed implementation plan
  README.md                   # this file
  Main_Report.md / .pdf       # final report (to be written)
  AI_Audit_Report.md / .pdf   # mandatory appendix (to be written)
  AI_Critique.md              # 200-300 words (to be written)
  test-plans/                 # Load / Stress / Spike / Endurance / Lockout JMX
  data/                       # CSV input data
  scripts/                    # seed, reset, JMX generator, runner, monitor, analysis
  results/                    # raw .jtl + HTML dashboards + resource CSV + manifests
  analysis/                   # per-scenario JTL summaries and 30-second timelines
  reports/                    # final report / submission copies of HTML dashboards
  screenshots/                # tool + resource monitor + hardware
  hardware/                   # dxdiag and spec evidence
  docs/                       # group scope, preflight, notes
  ai_audit/                   # prompt/output log
  skills/                     # Agent Skill
  ci/                         # continuous performance testing prototype
  experiments/                # optional optimization experiments (copy only)
  sut/                        # clean clone of SUT (git-ignored)
```

---

## 2.1. Test plans and shared workflow

All Load/Stress/Spike/Endurance plans run the **same end-to-end workflow**:

1. `GET /api/products` — read-heavy (product list, no pagination)
2. `GET /api/products?search=${search_keyword}` — read-heavy
3. `POST /api/login` — auth-heavy (token extracted with JSON Extractor `$.token`)
4. `GET /api/products/${product_id}` — read-heavy
5. `POST /api/cart` — transactional
6. `POST /api/checkout` — transactional (server accepts client `total_amount`)
7. `GET /api/orders/my-orders` — transactional read

A **separate Lockout plan** uses `lockout@eshop.test` with three wrong passwords and expects `401, 401, 403`; it is kept out of the main JTL so expected 4xx responses do not inflate the performance error rate.

| Plan | Shape | Report view | Notes |
|---|---|---|---|
| `23120372_Load_<date>.jmx` | 30 VUs, ramp 60 s, 600 s, think 2000 ± 1000 ms | Summary Report | Property overrides: `-Jthreads`, `-Jramp`, `-Jduration` |
| `23120372_Stress_<date>.jmx` | 6 steps: 10/20/40/80/120/160 VUs × 120 s, 10 s ramp, 120 s startup delays | Aggregate Report | Manual stop conditions: error > 5%, p95 > 2000 ms, backend CPU > 90%, JMeter CPU > 85% |
| `23120372_Spike_<date>.jmx` | 3 cycles: baseline 10 VUs/120 s → spike 100 VUs/60 s → recovery 10 VUs/120 s | View Results Tree (post-run) | 15 min total |
| `23120372_Endurance_<date>.jmx` | 12 min, parameterised 30 VUs | Summary Report | Run at 50/75/100% of stress capacity |
| `23120372_Lockout_<date>.jmx` | 1 thread, 3 attempts, 1.5 s pacing | Raw JTL | Expected `401, 401, 403` |

- Target: `${__P(host,localhost)}:${__P(port,3100)}`; CSV: `${__P(csv,data/e2e_data.csv)}`.
- Run JMeter **from the repository root** so the relative CSV path resolves.
- Report-view listeners are saved in the JMX but disabled during non-GUI runs to avoid client-side memory overhead; screenshots are taken by opening the saved `.jtl` in the JMeter GUI.
- JMeter and the backend share the same 4C/8T laptop. This is a validity threat for high-load steps and is reported with JMeter CPU/RSS measurements.

---

## 3. Test summary (to be filled after runs)

| Scenario | Endpoint groups | VUs / duration | Key result | Status |
|---|---|---|---|---|
| Load | Auth + Read + Transactional | TBD | TBD | Not run |
| Stress | Auth + Read + Transactional | TBD | TBD | Not run |
| Spike | Auth + Read + Transactional | TBD | TBD | Not run |
| Endurance | Auth + Read + Transactional | TBD | TBD | Not run |

- **Endurance threshold:** TBD (max stable RPS, p95/p99, memory ceiling).
- **Bugs / performance issues:** TBD.
- **Demo video:** TBD (unlisted YouTube link).

---

## 4. Reproduce

```powershell
# 1. Clone SUT (clean official repo)
git clone https://github.com/ttbhanh/eshop-sut.git sut/eshop-sut

# 2. Install backend dependencies
cd sut/eshop-sut/backend
npm ci

# 3. Start backend on port 3100 (official default is 3000; local port patch documented in docs/sut_port_patch.md). Important: server start DROPs and reseeds the DB.
node server.js

# 4. Wait for "Server is running on http://localhost:3100", then seed performance data.
python ..\..\..\scripts\seed_perf_data.py
python ..\..\..\scripts\generate_csv.py

# 5. Generate the plans (date = actual run date) and the CSV
python ..\..\..\scripts\generate_jmx.py --date 20261116
python ..\..\..\scripts\generate_csv.py

# 6. Return to repo root, then run a scenario with resource monitoring + manifest
cd ..\..\..
python scripts\run_scenario.py --scenario load --threads 30 --ramp 60 --duration 600
python scripts\run_scenario.py --scenario stress
python scripts\run_scenario.py --scenario spike
python scripts\run_scenario.py --scenario endurance --threads 30 --duration 720
python scripts\run_scenario.py --scenario lockout --no-html

# 7. Analyse the raw JTL
python scripts\analyze_jtl.py --scenario load --jtl results\load\23120372_Load_20261116.jtl
```

> The backend must be started again before each official scenario to clear the in-memory cart. Backend start drops/reseeds the DB, so re-run `seed_perf_data.py` after every restart.

---

## 5. Self-assessment (to be filled after evidence is complete)

| No. | Criteria | Grade | Self-assessed |
|---|---|---:|---:|
| 1 | Task 1 — Load testing | 30 | TBD |
| 2 | Task 1 — Stress testing | 20 | TBD |
| 3 | Task 1 — Spike testing | 20 | TBD |
| 4 | Task 2 — AI analysis + misinterpretation hunt | 10 | TBD |
| 5 | Task 3 — Continuous Performance Testing proposal | 10 | TBD |
| 6 | Agent Skills | 10 | TBD |
| **Total** | | **100** | **TBD** |

> Self-assessed grade is intentionally left as TBD until all required evidence exists. It must be a 3-digit number in the final zip filename.

---

## 6. AI use declaration

AI is used for test design, log analysis, and report drafting. Every AI interaction is logged in `ai_audit/` with tool/model, date/time, prompt, output, and human review. AI outputs are not treated as results; all metrics are verified against raw `.jtl` logs and resource measurements.
