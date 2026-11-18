# JTL analysis — endurance

- JTL: `results\endurance_100C\23120372_Endurance_20261118.jtl`
- Rows: 54488; wall time: 719.16 s; overall 75.766 samples/s
- Errors: 0 (0.0%)
- Max active threads (allThreads): 160

## Errors by response code

No failed samples.

## Group / step summary

| Group | Rows | Errors | Error % | RPS (rows/wall) | Max threads | p50 | p95 | p99 | Avg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 54488 | 0 | 0.0 | 75.766 | 160 | 2.0 | 38.0 | 118.0 | 10.16 |

## Per-label summary (successful samples only for latency)

| Label | Rows | Errors | RPS | p50 | p95 | p99 | Avg | Max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GET /api/products (list) | 7850 | 0 | 10.916 | 3.0 | 31.0 | 113.0 | 9.32 | 1032.0 |
| GET /api/products?search | 7832 | 0 | 10.911 | 3.0 | 28.0 | 100.69 | 9.13 | 1023.0 |
| POST /api/login | 7810 | 0 | 10.9 | 2.0 | 35.0 | 136.82 | 9.78 | 1248.0 |
| GET /api/products/{id} | 7788 | 0 | 10.895 | 1.0 | 39.0 | 151.52 | 9.9 | 1103.0 |
| POST /api/cart | 7759 | 0 | 10.881 | 1.0 | 2.0 | 46.42 | 2.92 | 617.0 |
| POST /api/checkout | 7734 | 0 | 10.878 | 10.0 | 80.0 | 151.34 | 21.76 | 1044.0 |
| GET /api/orders/my-orders | 7715 | 0 | 10.885 | 2.0 | 27.0 | 102.0 | 8.34 | 943.0 |

30-second timeline: `analysis\endurance_100C\endurance_intervals.csv`
