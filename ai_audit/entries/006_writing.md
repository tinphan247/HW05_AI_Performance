# Entry 006 - Report, Task 3, criteria, and final fact-check

**Date/time:** 2026-11-18 16:20-17:00 ICT
**Tool:** OpenCode (coding agent), model DeepSeek V4.1 Flash Free
**Task:** draft `Main_Report.md`, `AI_Audit_Report.md`, `AI_Critique.md`, `docs/task3_continuous_testing.md`,
the flowchart SVG, and the submission zip script.

## Prompt (paraphrased)

"Viết báo cáo chính bằng tiếng Việt từ các file JTL/manifest đã có. Không điền số nào không
truy vết được. Task 3 cần flow chart và trade-off chi phí/false alarm. Sinh PDF và zip."

## AI output used

- Markdown structure and Vietnamese prose for the report.
- Mermaid/SVG flowchart generator (`scripts/make_flowchart.py`).
- CI prototype `ci/perf-gate.yml` + `ci/compare_baseline.py` + `ci/baseline.json`.
- PDF converter `scripts/md_to_pdf.py` (Python-Markdown -> headless Chrome).

## Human review / corrections

1. AI drafted the threshold section using the values it had proposed in Task 2
   (250 MB ceiling, 100 req/s). Rejected: the report keeps the pre-registered criteria and the
   measured value 182,25 MB / 78,89 samples/s. The Task 2 proposals are described as
   proposals, not results.
2. AI wrote "throughput 14,088 samples/s = 14,088 users/s". Corrected: 7 requests per
   iteration, so ~2,01 iterations/s.
3. AI attributed the Load max 1.619 ms to checkout. Corrected with the JTL: the sample is
   `GET /api/products/{id}` at 2026-11-16 12:25:33.348 ICT, and 15 slow samples share one
   global stall ending at ~161,29 s.
4. AI reported the lockout DB counter as 6. Corrected from the repro JSON: `login_attempts=4`
   after three failures (the handler adds +2 per failure and the third call locks).
5. AI produced a flow chart with a "run full stress on every PR" branch. Rejected on cost
   grounds; the final flow runs a short smoke gate per PR and full suites nightly.

## Further verification

- `scripts/verify_task2_ai.py` recomputes every percentile and per-label max from the JTLs.
- `ci/compare_baseline.py` was run against `analysis/load_summary.json`; gate result PASS with
  0 % delta (baseline equals the accepted Load run).
- All 8 issues were published through `scripts/publish_issues.py` and the URLs recorded in
  `docs/issues/published.json`; the report links to issues #1-#8.
