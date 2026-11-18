---
name: jmeter-perf-testing
description: Plan, run, monitor and analyse JMeter Load/Stress/Spike/Endurance tests against a REST API with CSV data, real JTL evidence, resource metrics, an AI audit trail and a reusable run manifest. Use when a repository needs reproducible performance evidence rather than ad-hoc JMeter numbers.
---

# JMeter performance testing (evidence-first)

This skill turns a REST API into a reproducible performance-test package:

- three scenario families that share **one end-to-end workflow** (auth + read + transactional);
- CSV-driven virtual users and payloads;
- raw `.jtl` plus JMeter HTML dashboards;
- 2-second resource samples for backend, JMeter and the host;
- a SHA-256 run manifest and a human/AI audit trail;
- analysis from the raw log, never from memory or AI guesses.

## When to use

- The task asks for Load / Stress / Spike (and optionally Endurance) evidence.
- The SUT has login, list/search, detail, cart/checkout or similar REST endpoints.
- You must prove what was run: commands, parameters, dataset, commit, hardware, raw logs.
- An AI agent will help; every AI step must be reviewable and correctable.

Do **not** use this skill to invent metrics, to run only JMeter's GUI, or to compare runs with different datasets/durations.

## Inputs

Collect these before generating plans:

| Input | Example |
|---|---|
| Base URL / port | `http://localhost:3100` (document any non-default port) |
| Endpoint groups | auth: `POST /api/login`; read: `GET /api/products`; transactional: `POST /api/cart`, `POST /api/checkout` |
| Test accounts | CSV columns `email,password,...`; never real personal data |
| Payload data | product id/name/price/quantity, address, total |
| Scenario shape | VUs, ramp, duration, think time, step levels, spike multiplier |
| Output contract | `results/<scenario>/<plan>.jtl`, `html/`, `resources.csv`, `manifest.md` |
| SUT commit | `git -C sut rev-parse HEAD` |

## Procedure

1. **Preflight**
   - Verify Java, JMeter, Node/Python, free port, free disk.
   - Clone the official SUT at a recorded commit; do not test a modified copy without documenting the patch.
   - Record hardware and hostname.
2. **Dataset**
   - Start the backend first if it seeds/drops the DB on startup.
   - Seed deterministic users/products with an external script (no schema/business-logic edits).
   - Generate CSV from the live DB so IDs/prices match.
   - Reset volatile state (orders, lockout flags, cart by restart) before every official run.
3. **Design the shared workflow**
   - One iteration: list → search → login (extract token) → detail → cart → checkout → my-orders.
   - Put think time inside the controller; use a `GenericController` if you do not want a parent sample.
   - Assert status codes **and** key body fields (token, orderId).
   - Keep negative tests (lockout, invalid login) in a **separate plan** so expected 4xx does not inflate error rate.
4. **Generate plans**
   - Load: steady VUs + ramp + fixed duration + think time.
   - Stress: several thread groups with startup delays; increasing VUs; manual stop conditions.
   - Spike: baseline → sudden high load → recovery, repeated.
   - Endurance: parameterised 10–15 minute steady run.
   - Put listeners in the JMX for documentation but disable them for non-GUI runs; open the saved JTL in the GUI for screenshots.
5. **Run with monitoring**
   - Start the backend fresh, seed, verify counts.
   - Start the resource monitor (2 s samples).
   - Run JMeter non-GUI with `-l`, `-e -o`, `-j`.
   - Stop the monitor; record start/end, PID, exit code, DB counts.
6. **Analyse**
   - Parse the JTL: count, error %, p50/p90/p95/p99, max, throughput per label/step.
   - Exclude expected negative-test responses and controller parent samples explicitly.
   - Build 30 s buckets to find knee/recovery.
   - Compare JMeter CPU/RSS with backend CPU to detect a client bottleneck.
7. **Report**
   - Every number cites a JTL or resource CSV.
   - State validity threats: same host, SQLite, in-memory cart, dataset size.
   - Keep a misinterpretation table: AI statement vs raw value, with timestamp/file.
8. **Audit**
   - Log tool/model, UTC+7 time, verbatim prompt, output, human decision.
   - Mark unverified AI claims as “needs checking”, not as results.

## Guardrails

- Never fabricate a metric, screenshot, issue or YouTube link.
- Never use View Results Tree live for stress/spike; it consumes client memory.
- Never leave expected 401/403 in the main error rate.
- Never compare runs with different duration, dataset, think time or load generator.
- Never report throughput without stating the window (ramp-up included or steady-state).
- Never recommend Redis/PM2/cluster for an in-memory-cart + SQLite SUT without noting the refactor cost.
- Reset lockout flags and note the reset in the manifest.
- Record the SUT commit, port patch, backend PID and hardware.

## Deliverables checklist

- [ ] `test-plans/*.jmx` with shared workflow and CSV config
- [ ] `data/*.csv`
- [ ] `results/<scenario>/*.jtl`, `html/`, `resources.csv`, `manifest.md/json`
- [ ] `analysis/<scenario>_summary.md` + intervals CSV
- [ ] Screenshots of the tool, report view and resource monitor
- [ ] Hardware evidence
- [ ] GitHub issues for real bugs/perf problems
- [ ] AI audit + critique
- [ ] Continuous-testing proposal + flow chart
- [ ] This skill demo video/link

## Acceptance test

The skill is reusable if another endpoint group can be tested by editing **only** the CSV schema, endpoint paths and scenario parameters, and the result still includes a manifest, raw JTL, HTML report, resource CSV and analysis with no invented values.
