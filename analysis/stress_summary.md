# JTL analysis — stress

- JTL: `results\stress\23120372_Stress_20261118.jtl`
- Rows: 48735; wall time: 718.62 s; overall 67.817 samples/s
- Errors: 0 (0.0%)
- Max active threads (allThreads): 160

## Errors by response code

No failed samples.

## Group / step summary

| Group | Rows | Errors | Error % | RPS (rows/wall) | Max threads | p50 | p95 | p99 | Avg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Stress S1 - 10 VUs | 1149 | 0 | 0.0 | 9.741 | 10 | 3.0 | 14.0 | 27.0 | 5.53 |
| Stress S2 - 20 VUs | 2311 | 0 | 0.0 | 19.336 | 20 | 2.0 | 13.0 | 26.0 | 4.49 |
| Stress S3 - 40 VUs | 4509 | 0 | 0.0 | 37.786 | 40 | 3.0 | 20.0 | 85.0 | 7.27 |
| Stress S4 - 80 VUs | 9053 | 0 | 0.0 | 75.64 | 80 | 3.0 | 40.0 | 85.0 | 7.8 |
| Stress S5 - 120 VUs | 13599 | 0 | 0.0 | 113.502 | 120 | 3.0 | 29.0 | 87.0 | 7.88 |
| Stress S6 - 160 VUs | 18114 | 0 | 0.0 | 150.978 | 160 | 4.0 | 38.0 | 116.0 | 10.24 |

## Per-label summary (successful samples only for latency)

| Label | Rows | Errors | RPS | p50 | p95 | p99 | Avg | Max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GET /api/products (list) | 7136 | 0 | 9.93 | 4.0 | 29.0 | 98.65 | 8.42 | 298.0 |
| GET /api/products?search | 7079 | 0 | 9.863 | 4.0 | 24.0 | 96.0 | 7.89 | 296.0 |
| POST /api/login | 7029 | 0 | 9.802 | 2.0 | 31.6 | 97.72 | 7.56 | 295.0 |
| GET /api/products/{id} | 6966 | 0 | 9.724 | 2.0 | 27.0 | 91.0 | 6.59 | 243.0 |
| POST /api/cart | 6904 | 0 | 9.646 | 1.0 | 4.0 | 39.0 | 2.35 | 128.0 |
| POST /api/checkout | 6845 | 0 | 9.583 | 12.0 | 81.0 | 112.0 | 19.11 | 322.0 |
| GET /api/orders/my-orders | 6776 | 0 | 9.497 | 3.0 | 31.0 | 94.0 | 7.5 | 303.0 |

30-second timeline: `analysis\stress_intervals.csv`
