# Run manifest — Lockout

- Scenario: **Lockout**
- Started: 2026-11-16T12:22:16+07:00
- Ended: 2026-11-16T12:22:24+07:00 (elapsed 7.55 s)
- JMeter exit code: 0
- Test plan: `test-plans\23120372_Lockout_20261116.jmx` (SHA-256 `bc992950b3ad8a67d6609640ab461c56782343eb3cfd09d97623584bf0ede249`)
- JTL: `results\lockout\23120372_Lockout_20261116.jtl` (SHA-256 `89aeafd40a29fe34281866dfbdb9cf620357687ceae455aea8c7de34ac6c801b`)
- CSV: `data/e2e_data.csv` (SHA-256 `5ceff8eab0c3b2ceb3ac331241c80b2837f854e6b14d96024ddc1032a4a68edc`)
- Samples: 3; failed: 3
- Avg elapsed (all samples): 10.67 ms; max: 25.0 ms
- DB counts before: {'users': 503, 'products': 205, 'orders': 0}
- DB counts after: {'users': 503, 'products': 205, 'orders': 0}
- Backend PID: 10440
- Host: DESKTOP-BCS88BQ — Windows-11-10.0.26200-SP0
- HW05 git commit: `54dcb5b33521f2adb849805c5090837c3575a8fe`
- SUT commit: `85af3ba875c88283615e22cb108f13e2fccaf0e9`
- JMeter command: `cmd /c C:\HCMUS\hk7\Testing\apache-jmeter-5.6.3\bin\jmeter.bat -n -t C:\HCMUS\hk7\Testing\hw5\test-plans\23120372_Lockout_20261116.jmx -l C:\HCMUS\hk7\Testing\hw5\results\lockout\23120372_Lockout_20261116.jtl -j C:\HCMUS\hk7\Testing\hw5\results\lockout\jmeter.log -Jhost=localhost -Jport=3100 -Jcsv=data/e2e_data.csv`

## Resource summary

| Metric | Min | Avg | Max |
|---|---:|---:|---:|
| Backend CPU % | 0.0 | 0.2 | 0.8 |
| Backend RSS MB | 53.2 | 53.36 | 53.48 |
| JMeter CPU % | 0.0 | 2.675 | 9.2 |
| JMeter RSS MB | 8.25 | 142.2475 | 193.9 |
| System CPU % | 22.3 | 33.875 | 57.6 |
| System RAM available MB | 3282.64 | 3327.9775 | 3442.52 |

- Backend RSS start/end: 53.48 / 53.28 MB
- Resource samples: 4

## Note

Dedicated lockout probe; expected 401/401/403
