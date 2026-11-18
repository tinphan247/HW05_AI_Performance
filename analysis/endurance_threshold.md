# Endurance threshold

Criteria (pre-registered in `PLAN.md` section 5.1):

- error rate < 1%
- p95 < 1000 ms, p99 < 2000 ms
- throughput coefficient of variation over 30 s buckets < 10%
- backend RSS growth after the 300 s warm-up < 10%
- backend CPU average < 85%

| Level | VUs | RPS (30 s mean) | CV | p95 | p99 | Error % | RSS max | RSS growth after 300 s | Backend CPU avg | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 50C | 80 | 39.528 | 1.99% | 16.0 ms | 20.0 ms | 0.0% | 179.84 MB | 1.3% | 14.25% | PASS |
| 75C | 120 | 58.887 | 2.18% | 21.0 ms | 123.69 ms | 0.0% | 182.34 MB | 1.3% | 12.44% | PASS |
| 100C | 160 | 78.887 | 1.28% | 47.0 ms | 134.69 ms | 0.0% | 182.25 MB | -0.1% | 15.86% | PASS |

## Criterion detail

| Level | Error rate < 1% | p95 < 1000 ms | p99 < 2000 ms | 30 s throughput CV < 10% | RSS growth after 300 s < 10% | Backend CPU average < 85% |
|---|---|---|---|---|---|---|
| 50C | PASS | PASS | PASS | PASS | PASS | PASS |
| 75C | PASS | PASS | PASS | PASS | PASS | PASS |
| 100C | PASS | PASS | PASS | PASS | PASS | PASS |

## Conclusion

**Threshold: 100C - 160 VUs, 78.887 samples/s sustained for 599.2 s of steady state.**

Memory ceiling at that level: **182.25 MB** backend RSS (observed at 681.02 s).

The client and the SUT share one laptop, so these numbers describe this
co-located configuration, not the capacity of EShop on dedicated hardware.
