# JTL columns and what they mean

A JMeter CSV JTL row (default save configuration):

| Column | Meaning | Pitfall |
|---|---|---|
| `timeStamp` | request start, epoch milliseconds | Convert to seconds before computing windows |
| `elapsed` | total time from request start to response end (ms) | This is the latency users see; not the same as `Latency` |
| `label` | sampler name | Controller samples may share a transaction name |
| `responseCode` | HTTP status or JMeter error code | `Non HTTP response code: ...` means connection/DNS/timeout |
| `responseMessage` | HTTP reason / error text | Keep for error grouping |
| `threadName` | `<thread group> <n>-<iteration>` | Use the prefix to separate stress steps/cycles |
| `success` | JMeter success flag | Can be false on 4xx even when the assertion expected it |
| `failureMessage` | assertion message | Read this before blaming the server |
| `bytes` | response size | Includes headers/compression effects; not a pure payload size |
| `sentBytes` | request size | Useful for upload scenarios |
| `grpThreads` | active threads in this thread group | Distinguish from `allThreads` |
| `allThreads` | active threads in the whole test | Use for concurrency checks |
| `URL` | final URL | Empty for controller samples |
| `Latency` | time to first byte (ms) | Do not substitute for `elapsed` |
| `IdleTime` | time spent waiting inside a transaction | Usually 0 for plain HTTP samplers |
| `Connect` | TCP connect time (ms) | Keep-alive reuses connections, so many rows show 0 |

## Counting rules

- **Requests:** exclude controller parent/transaction samples. In HW05 the plans use a `GenericController`, so every row is an HTTP request.
- **Error %:** count `success=false`; report expected negative tests separately.
- **Throughput:** `rows / (last_end - first_start)` for the chosen window. State whether ramp-up is included.
- **Percentiles:** sort successful `elapsed` values; use linear interpolation; report p50/p90/p95/p99 and max.
- **Steady state:** drop the ramp-up window and the final partial iteration before comparing runs.

## What not to conclude

- A lower average with a higher p95 is often a saturation signal, not an improvement.
- `success=false` on a 401/403 probe is expected, not a server defect.
- High throughput with high JMeter CPU can mean the load generator is the bottleneck.
- `bytes` differences across runs may come from product count or error pages, not from a code change.
