# JTL analysis — endurance

- JTL: `results\endurance_75C\23120372_Endurance_20261118.jtl`
- Rows: 40762; wall time: 717.57 s; overall 56.805 samples/s
- Errors: 0 (0.0%)
- Max active threads (allThreads): 120

## Errors by response code

No failed samples.

## Group / step summary

| Group | Rows | Errors | Error % | RPS (rows/wall) | Max threads | p50 | p95 | p99 | Avg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 40762 | 0 | 0.0 | 56.805 | 120 | 2.0 | 22.0 | 134.39 | 9.47 |

## Per-label summary (successful samples only for latency)

| Label | Rows | Errors | RPS | p50 | p95 | p99 | Avg | Max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GET /api/products (list) | 5874 | 0 | 8.188 | 3.0 | 17.0 | 121.81 | 8.51 | 1112.0 |
| GET /api/products?search | 5855 | 0 | 8.182 | 3.0 | 17.0 | 121.92 | 8.76 | 1142.0 |
| POST /api/login | 5841 | 0 | 8.171 | 2.0 | 18.0 | 146.8 | 8.36 | 1157.0 |
| GET /api/products/{id} | 5826 | 0 | 8.191 | 2.0 | 17.0 | 162.75 | 8.64 | 1096.0 |
| POST /api/cart | 5811 | 0 | 8.191 | 1.0 | 3.0 | 56.9 | 2.81 | 534.0 |
| POST /api/checkout | 5789 | 0 | 8.184 | 10.0 | 78.0 | 218.12 | 20.5 | 1015.0 |
| GET /api/orders/my-orders | 5766 | 0 | 8.179 | 2.0 | 16.75 | 138.0 | 8.75 | 1082.0 |

30-second timeline: `analysis\endurance_75C\endurance_intervals.csv`
