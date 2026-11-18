# JTL analysis — load

- JTL: `results\load\23120372_Load_20261116.jtl`
- Rows: 8417; wall time: 597.47 s; overall 14.088 samples/s
- Errors: 0 (0.0%)
- Max active threads (allThreads): 30

## Errors by response code

No failed samples.

## Group / step summary

| Group | Rows | Errors | Error % | RPS (rows/wall) | Max threads | p50 | p95 | p99 | Avg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 8417 | 0 | 0.0 | 14.088 | 30 | 2.0 | 11.0 | 15.0 | 5.17 |

## Per-label summary (successful samples only for latency)

| Label | Rows | Errors | RPS | p50 | p95 | p99 | Avg | Max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GET /api/products (list) | 1214 | 0 | 2.033 | 3.0 | 5.0 | 8.0 | 4.36 | 1279.0 |
| GET /api/products?search | 1210 | 0 | 2.034 | 3.0 | 5.0 | 7.91 | 4.31 | 1324.0 |
| POST /api/login | 1206 | 0 | 2.032 | 2.0 | 4.0 | 10.0 | 5.53 | 1385.0 |
| GET /api/products/{id} | 1202 | 0 | 2.04 | 2.0 | 3.0 | 7.0 | 3.19 | 1619.0 |
| POST /api/cart | 1201 | 0 | 2.039 | 1.0 | 2.0 | 3.0 | 1.36 | 4.0 |
| POST /api/checkout | 1196 | 0 | 2.033 | 10.0 | 15.0 | 43.15 | 14.15 | 1404.0 |
| GET /api/orders/my-orders | 1188 | 0 | 2.022 | 2.0 | 3.0 | 9.0 | 3.29 | 897.0 |

30-second timeline: `analysis\load_intervals.csv`
