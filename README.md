# HW05 — Performance Testing — EShop

**Student:** Phan Trung Tin — **MSSV:** 23120372  
**Course:** Software Testing — FIT, VNUHCM  
**SUT:** EShop — https://github.com/ttbhanh/eshop-sut  
**Submission repo:** https://github.com/tinphan247/HW05_AI_Performance

> **Status:** In progress. Preflight/setup has been completed; **no Load/Stress/Spike/Endurance run has been executed yet**.
> All result numbers will be filled only from the real `.jtl` logs, resource CSV, and screenshots.
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
  test-plans/                 # 3 JMX files
  data/                       # CSV input data
  scripts/                    # seed, reset, monitoring, analysis, PDF
  results/                    # raw .jtl + manifests + logs
  reports/                    # HTML dashboard folders
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

# 3. Seed original database
node database.js

# 4. Seed performance data (500 users + 200 products; script to be added)
# node ../../../scripts/seed_perf_data.js

# 5. Start backend (port 3000)
node server.js

# 6. Run a scenario (example; test plan not created yet)
# apache-jmeter-5.6.3\bin\jmeter.bat -n -t test-plans\...jmx -l results\...jtl -e -o reports\...\html
```

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
