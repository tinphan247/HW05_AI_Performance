# Run manifest — Spike

- Scenario: **Spike**
- Started: 2026-11-18T15:06:39+07:00
- Ended: 2026-11-18T15:21:51+07:00 (elapsed 911.3 s)
- JMeter exit code: 0
- Test plan: `test-plans\23120372_Spike_20261118.jmx` (SHA-256 `7dbd4eca4013a820f2da1238de5b05073dbef5efcec6d7b646c56f4dc7942fe3`)
- JTL: `results\spike\23120372_Spike_20261118.jtl` (SHA-256 `3f28109bba7b335a5c9271205ecd81ca9aaf30e2276a535da1da26bb68b6c894`)
- CSV: `data/e2e_data.csv` (SHA-256 `5ceff8eab0c3b2ceb3ac331241c80b2837f854e6b14d96024ddc1032a4a68edc`)
- Samples: 23809; failed: 0
- Avg elapsed (all samples): 6.7 ms; max: 177.0 ms
- DB counts before: {'users': 503, 'products': 205, 'orders': 0}
- DB counts after: {'users': 503, 'products': 205, 'orders': 3289}
- Backend PID: 24608
- Host: DESKTOP-BCS88BQ — Windows-11-10.0.26200-SP0
- HW05 git commit: `fd73e49ebfa7476bd2375bd72f11ebb8fca0b48c`
- SUT commit: `85af3ba875c88283615e22cb108f13e2fccaf0e9`
- JMeter command: `cmd /c C:\HCMUS\hk7\Testing\apache-jmeter-5.6.3\bin\jmeter.bat -n -t C:\HCMUS\hk7\Testing\hw5\test-plans\23120372_Spike_20261118.jmx -l C:\HCMUS\hk7\Testing\hw5\results\spike\23120372_Spike_20261118.jtl -j C:\HCMUS\hk7\Testing\hw5\results\spike\jmeter.log -Jhost=localhost -Jport=3100 -Jcsv=data/e2e_data.csv -e -o C:\HCMUS\hk7\Testing\hw5\results\spike\html`

## Resource summary

| Metric | Min | Avg | Max |
|---|---:|---:|---:|
| Backend CPU % | 0.0 | 8.734741784037558 | 45.2 |
| Backend RSS MB | 52.87 | 109.32279342723005 | 122.36 |
| JMeter CPU % | 0.0 | 6.044366197183098 | 279.7 |
| JMeter RSS MB | 8.32 | 592.8297183098591 | 798.31 |
| System CPU % | 13.7 | 28.626525821596243 | 80.1 |
| System RAM available MB | 1440.74 | 2745.6726760563383 | 3512.95 |

- Backend RSS start/end: 54.77 / 119.76 MB
- Resource samples: 426
