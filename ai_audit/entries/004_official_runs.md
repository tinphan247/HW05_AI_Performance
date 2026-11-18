# Entry 004 - Official Load / Stress / Spike / Endurance runs

**Date/time:** 2026-11-16 12:22 ICT (Load), 2026-11-18 14:53, 15:06, 15:22, 15:35, 15:47 ICT
(Stress, Spike, Endurance 50C/75C/100C)
**Tool:** OpenCode (coding agent), model DeepSeek V4.1 Flash Free
**Task:** run each scenario through `scripts/run_scenario.py`, read the resulting manifest and
resource CSV, and report the numbers.

## Prompts used (paraphrased, one per run)

- "Chạy Stress plan ngày 20261118, sau đó đọc manifest và bảng phân tích."
- "Chạy Spike plan, kiểm tra p95 lúc spike và thời gian recovery."
- "Chạy Endurance ở 80/120/160 VUs, mỗi mức 720 s, ghi ra thư mục riêng."

## AI output used

AI produced the run commands, restarted the backend between runs, and read back the manifests.
No number in the report came from the model's memory; every value was copied from
`results/*/manifest.json`, `analysis/*_summary.json` or `resources.csv`.

## Human review / corrections

1. AI initially compared Stress RPS with Endurance RPS directly. Rejected: Stress uses
   think-time 1000 ± 500 ms, Endurance uses 2000 ± 1000 ms, so 150,98 samples/s and
   78,89 samples/s are not the same workload.
2. AI reported the whole-window RSS slope (e.g. 8,26 MB/min at 50C) as a leak. Rejected:
   the slope is dominated by the first 300 s; after 300 s it is 0,363 MB/min and growth is
   1,3 %. The report uses the post-300 s figure.
3. AI read "max active threads 160" as "server capacity 160". Rejected: system CPU reached
   99,5-99,7 %, so 160 VUs is the largest *tested* point, not a measured capacity.
4. The backend must be restarted (not just reset) before each official run to clear the
   in-memory cart; AI's first suggestion to only reset was corrected by the human.

## Verified artifacts

| Run | JTL SHA-256 (from manifest) | Samples | Errors |
|---|---|---:|---:|
| Load | `d309472d...` | 8.417 | 0 |
| Stress | `e986c70a...` | 48.735 | 0 |
| Spike | see `results/spike/manifest.json` | 23.809 | 0 |
| Endurance 50C | see `results/endurance_50C/manifest.json` | 27.388 | 0 |
| Endurance 75C | `c9db4f19...` | 40.762 | 0 |
| Endurance 100C | `b20f0b65...` | 54.488 | 0 |
