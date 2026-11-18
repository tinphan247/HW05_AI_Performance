# Endurance 75C - steady-state statistics

- Run: `results\endurance_75C`
- JTL: `results\endurance_75C\23120372_Endurance_20261118.jtl`
- Window: 90.0s to 687.6s (597.6s; warm-up 90.0s, cooldown 30.0s)

| Metric | Value |
|---|---:|
| Throughput | 58.887 samples/s, 30 s buckets (SD 1.286, CV 2.18%) |
| Throughput 1 s buckets | 59.084 samples/s (SD 6.553, CV 11.09%) |
| Throughput range (30 s) | 54.633 - 60.4 samples/s |
| p50 / p95 / p99 | 2.0 / 21.0 / 123.69 ms |
| Errors | 0 (0.0%) |
| Max active threads | 120 |
| Backend CPU avg / max | 12.44% / 24.4% |
| System CPU avg / max | 45.86% / 99.8% |
| Backend RSS start | 58.29 MB |
| Backend RSS end of warm-up | 92.57 MB |
| Backend RSS end of run | 182.13 MB |
| Backend RSS max (memory ceiling) | 182.34 MB at 660.84s |
| Backend RSS at 300 s | 179.75 MB |
| RSS growth 300 s -> end | 1.3% |
| RSS slope in steady window | 5.352 MB/min |
| RSS slope after 300 s | 0.924 MB/min |
| RSS growth warm-up -> end | 96.7% |
