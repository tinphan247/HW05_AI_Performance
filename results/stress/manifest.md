# Run manifest — Stress

- Scenario: **Stress**
- Started: 2026-11-18T14:53:43+07:00
- Ended: 2026-11-18T15:06:09+07:00 (elapsed 745.76 s)
- JMeter exit code: 0
- Test plan: `test-plans\23120372_Stress_20261118.jmx` (SHA-256 `b4f4a87b9514a62674bad70a6ebe2ed1d43959f18d24b597db1915909c2e0bb9`)
- JTL: `results\stress\23120372_Stress_20261118.jtl` (SHA-256 `e986c70ac82601bc643e5569cd4dd6d662b41382b84ba5eb59bfa0f87465d9b2`)
- CSV: `data/e2e_data.csv` (SHA-256 `5ceff8eab0c3b2ceb3ac331241c80b2837f854e6b14d96024ddc1032a4a68edc`)
- Samples: 48735; failed: 0
- Avg elapsed (all samples): 8.47 ms; max: 322.0 ms
- DB counts before: {'users': 503, 'products': 205, 'orders': 0}
- DB counts after: {'users': 503, 'products': 205, 'orders': 6845}
- Backend PID: 1560
- Host: DESKTOP-BCS88BQ — Windows-11-10.0.26200-SP0
- HW05 git commit: `fd73e49ebfa7476bd2375bd72f11ebb8fca0b48c`
- SUT commit: `85af3ba875c88283615e22cb108f13e2fccaf0e9`
- JMeter command: `cmd /c C:\HCMUS\hk7\Testing\apache-jmeter-5.6.3\bin\jmeter.bat -n -t C:\HCMUS\hk7\Testing\hw5\test-plans\23120372_Stress_20261118.jmx -l C:\HCMUS\hk7\Testing\hw5\results\stress\23120372_Stress_20261118.jtl -j C:\HCMUS\hk7\Testing\hw5\results\stress\jmeter.log -Jhost=localhost -Jport=3100 -Jcsv=data/e2e_data.csv -e -o C:\HCMUS\hk7\Testing\hw5\results\stress\html`

## Resource summary

| Metric | Min | Avg | Max |
|---|---:|---:|---:|
| Backend CPU % | 0.0 | 16.299426934097422 | 56.2 |
| Backend RSS MB | 53.23 | 119.3922636103152 | 181.37 |
| JMeter CPU % | 0.0 | 8.40458452722063 | 226.0 |
| JMeter RSS MB | 8.31 | 487.6103151862464 | 825.98 |
| System CPU % | 14.8 | 41.22492836676218 | 99.5 |
| System RAM available MB | 1240.04 | 2332.5549283667624 | 2867.16 |

- Backend RSS start/end: 53.29 / 177.79 MB
- Resource samples: 349
