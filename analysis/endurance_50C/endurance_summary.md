# JTL analysis — endurance

- JTL: `results\endurance_50C\23120372_Endurance_20261118.jtl`
- Rows: 27388; wall time: 717.8 s; overall 38.156 samples/s
- Errors: 0 (0.0%)
- Max active threads (allThreads): 80

## Errors by response code

No failed samples.

## Group / step summary

| Group | Rows | Errors | Error % | RPS (rows/wall) | Max threads | p50 | p95 | p99 | Avg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 27388 | 0 | 0.0 | 38.156 | 80 | 4.0 | 16.0 | 20.0 | 5.55 |

## Per-label summary (successful samples only for latency)

| Label | Rows | Errors | RPS | p50 | p95 | p99 | Avg | Max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GET /api/products (list) | 3947 | 0 | 5.499 | 5.0 | 10.0 | 17.0 | 5.63 | 79.0 |
| GET /api/products?search | 3933 | 0 | 5.485 | 5.0 | 9.0 | 17.0 | 5.38 | 74.0 |
| POST /api/login | 3926 | 0 | 5.483 | 3.0 | 8.0 | 16.0 | 4.01 | 85.0 |
| GET /api/products/{id} | 3912 | 0 | 5.482 | 3.0 | 7.0 | 15.0 | 3.2 | 73.0 |
| POST /api/cart | 3903 | 0 | 5.477 | 2.0 | 3.0 | 5.0 | 1.92 | 13.0 |
| POST /api/checkout | 3890 | 0 | 5.472 | 14.0 | 20.0 | 30.22 | 14.89 | 89.0 |
| GET /api/orders/my-orders | 3877 | 0 | 5.476 | 3.0 | 7.0 | 14.0 | 3.88 | 92.0 |

30-second timeline: `analysis\endurance_50C\endurance_intervals.csv`
