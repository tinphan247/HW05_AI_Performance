# Endurance 50C - steady-state statistics

- Run: `results\endurance_50C`
- JTL: `results\endurance_50C\23120372_Endurance_20261118.jtl`
- Window: 90.0s to 687.8s (597.8s; warm-up 90.0s, cooldown 30.0s)

| Metric | Value |
|---|---:|
| Throughput | 39.528 samples/s, 30 s buckets (SD 0.786, CV 1.99%) |
| Throughput 1 s buckets | 39.661 samples/s (SD 5.003, CV 12.61%) |
| Throughput range (30 s) | 37.233 - 40.8 samples/s |
| p50 / p95 / p99 | 4.0 / 16.0 / 20.0 ms |
| Errors | 0 (0.0%) |
| Max active threads | 80 |
| Backend CPU avg / max | 14.25% / 28.2% |
| System CPU avg / max | 27.56% / 65.5% |
| Backend RSS start | 57.95 MB |
| Backend RSS end of warm-up | 86.3 MB |
| Backend RSS end of run | 178.76 MB |
| Backend RSS max (memory ceiling) | 179.84 MB at 672.46s |
| Backend RSS at 300 s | 176.5 MB |
| RSS growth 300 s -> end | 1.3% |
| RSS slope in steady window | 8.26 MB/min |
| RSS slope after 300 s | 0.363 MB/min |
| RSS growth warm-up -> end | 107.1% |
