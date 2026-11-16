# Entry 002 — Setup and preflight

- **Date/time:** 2026-11-16 12:04 ICT (UTC+7)
- **Tool/model:** OpenCode / DeepSeek V4.1 Flash Free (`opencode/deepseek-v4.1-flash-free`)
- **Task:** Apply the student's answers, perform preflight, create seed/reset/CSV scripts, and initialise the submission repository.

## Prompt (verbatim)

> 1. ko.
> 2. https://github.com/tinphan247/HW05_AI_Performance.git
> 3. Đúng
> 4. Tuần sau.
> 5. cân nhắc sau.
> 6. Theo model
> 7. ok
> 8. ko

## AI output / actions

1. Interpreted decisions:
   - Repo: `https://github.com/tinphan247/HW05_AI_Performance`
   - Hardware hostname confirmed by student.
   - Deadline: “next week” (exact date not supplied).
   - Video: deferred (“cân nhắc sau”).
   - AI declaration: use the actual model name (`DeepSeek V4.1 Flash Free`).
   - Seed dataset approved.
   - No second load-generator machine.
   - Workflow duplicate answer “ko” interpreted as “no duplicate”; member list still missing.
2. Created `README.md`, `.gitignore`, `docs/preflight.md`, `docs/group_scope.md`, `docs/sut_commit.txt`.
3. Initialised the local Git repository, added the remote, committed, and pushed the initial commit.
4. Cloned a clean official SUT at commit `85af3ba875c88283615e22cb108f13e2fccaf0e9`; confirmed port 3000 and no local modifications.
5. Ran `npm ci` (135 packages), `node database.js`, `node server.js`; smoke check `GET /api/products` returned HTTP 200 (914 bytes).
6. Created `scripts/seed_perf_data.py`, `scripts/reset_state.py`, `scripts/generate_csv.py`.
7. Found a critical behaviour: `server.js` loads `database.js`, which drops/reseeds the DB on every backend start. Therefore seeding **before** starting the backend is wiped. Correct order: start backend → wait for listen → seed while running.
8. Verified seed counts: 503 users (2 seed + 500 perf + 1 lockout), 205 products, 0 orders.
9. Ran a single-user functional smoke E2E on `perf001@eshop.test`: login → cart → checkout (`orderId=1`) → my-orders (1); then reset state.
10. Generated `data/e2e_data.csv` (500 rows) and `data/lockout.csv` (1 row).

**No Load/Stress/Spike/Endurance test has been run.** No result metrics exist yet.

## Human review

- Student confirmed seed approval and hardware; no review of script code yet.
- The workflow non-duplication answer is accepted provisionally, but `docs/group_scope.md` still needs member names and evidence before the report can claim non-duplication.
- The startup-reset finding must be reflected in the final report and in every run manifest.
- The video is **not** produced; any report/README must keep it as TBD until a real unlisted YouTube link exists.

## Artifacts

- `README.md`, `.gitignore`
- `PLAN.md`
- `docs/preflight.md`, `docs/group_scope.md`, `docs/sut_commit.txt`
- `scripts/seed_perf_data.py`, `scripts/reset_state.py`, `scripts/generate_csv.py`
- `data/e2e_data.csv`, `data/lockout.csv`
- Git commits: `c8f2bca` (init), `fc7e3f1` (seed/CSV/startup finding)
