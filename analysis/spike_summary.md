# JTL analysis — spike

- JTL: `results\spike\23120372_Spike_20261118.jtl`
- Rows: 23809; wall time: 898.72 s; overall 26.492 samples/s
- Errors: 0 (0.0%)
- Max active threads (allThreads): 100

## Errors by response code

No failed samples.

## Group / step summary

| Group | Rows | Errors | Error % | RPS (rows/wall) | Max threads | p50 | p95 | p99 | Avg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Spike C1 - Baseline 10 VUs | 1141 | 0 | 0.0 | 9.638 | 10 | 3.0 | 13.0 | 19.6 | 4.94 |
| Spike C1 - Spike 100 VUs | 5606 | 0 | 0.0 | 93.879 | 100 | 3.0 | 18.0 | 89.0 | 7.18 |
| Spike C1 - Recovery 10 VUs | 1175 | 0 | 0.0 | 9.919 | 10 | 3.0 | 15.0 | 28.26 | 5.52 |
| Spike C2 - Baseline 10 VUs | 1141 | 0 | 0.0 | 9.648 | 10 | 4.0 | 15.0 | 18.0 | 5.16 |
| Spike C2 - Spike 100 VUs | 5646 | 0 | 0.0 | 94.429 | 100 | 4.0 | 17.75 | 59.0 | 6.86 |
| Spike C2 - Recovery 10 VUs | 1150 | 0 | 0.0 | 9.681 | 10 | 4.0 | 15.0 | 20.0 | 5.3 |
| Spike C3 - Baseline 10 VUs | 1126 | 0 | 0.0 | 9.441 | 10 | 4.0 | 16.0 | 20.0 | 5.39 |
| Spike C3 - Spike 100 VUs | 5678 | 0 | 0.0 | 95.817 | 100 | 4.0 | 19.0 | 68.46 | 7.56 |
| Spike C3 - Recovery 10 VUs | 1146 | 0 | 0.0 | 9.642 | 10 | 4.0 | 16.0 | 81.1 | 6.42 |

## Per-label summary (successful samples only for latency)

| Label | Rows | Errors | RPS | p50 | p95 | p99 | Avg | Max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GET /api/products (list) | 3559 | 0 | 3.961 | 5.0 | 15.0 | 57.42 | 6.86 | 164.0 |
| GET /api/products?search | 3506 | 0 | 3.906 | 4.0 | 14.0 | 73.85 | 6.57 | 177.0 |
| POST /api/login | 3463 | 0 | 3.864 | 3.0 | 14.0 | 57.38 | 5.15 | 176.0 |
| GET /api/products/{id} | 3410 | 0 | 3.809 | 2.0 | 12.0 | 46.91 | 4.24 | 157.0 |
| POST /api/cart | 3348 | 0 | 3.743 | 2.0 | 3.0 | 7.0 | 1.94 | 100.0 |
| POST /api/checkout | 3289 | 0 | 3.689 | 13.0 | 34.0 | 91.0 | 17.11 | 162.0 |
| GET /api/orders/my-orders | 3234 | 0 | 3.63 | 3.0 | 13.0 | 59.67 | 5.25 | 152.0 |

30-second timeline: `analysis\spike_intervals.csv`
