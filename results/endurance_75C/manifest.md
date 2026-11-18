# Run manifest — Endurance

- Scenario: **Endurance**
- Started: 2026-11-18T15:35:00+07:00
- Ended: 2026-11-18T15:47:07+07:00 (elapsed 727.92 s)
- JMeter exit code: 0
- Test plan: `test-plans\23120372_Endurance_20261118.jmx` (SHA-256 `94009ca2c60c86e14bda9b7333949924683c09e9981dd5a55ebce768ebe0837c`)
- JTL: `results\endurance_75C\23120372_Endurance_20261118.jtl` (SHA-256 `c9db4f190df12221c3a0951260dfb1c499172a7b2d3a373edee4aa39566daf86`)
- CSV: `data/e2e_data.csv` (SHA-256 `5ceff8eab0c3b2ceb3ac331241c80b2837f854e6b14d96024ddc1032a4a68edc`)
- Samples: 40762; failed: 0
- Avg elapsed (all samples): 9.47 ms; max: 1157.0 ms
- DB counts before: {'users': 503, 'products': 205, 'orders': 0}
- DB counts after: {'users': 503, 'products': 205, 'orders': 5789}
- Backend PID: 27004
- Host: DESKTOP-BCS88BQ — Windows-11-10.0.26200-SP0
- HW05 git commit: `fd73e49ebfa7476bd2375bd72f11ebb8fca0b48c`
- SUT commit: `85af3ba875c88283615e22cb108f13e2fccaf0e9`
- JMeter command: `cmd /c C:\HCMUS\hk7\Testing\apache-jmeter-5.6.3\bin\jmeter.bat -n -t C:\HCMUS\hk7\Testing\hw5\test-plans\23120372_Endurance_20261118.jmx -l C:\HCMUS\hk7\Testing\hw5\results\endurance_75C\23120372_Endurance_20261118.jtl -j C:\HCMUS\hk7\Testing\hw5\results\endurance_75C\jmeter.log -Jhost=localhost -Jport=3100 -Jcsv=data/e2e_data.csv -Jthreads=120 -Jduration=720 -e -o C:\HCMUS\hk7\Testing\hw5\results\endurance_75C\html`

## Resource summary

| Metric | Min | Avg | Max |
|---|---:|---:|---:|
| Backend CPU % | 0.0 | 12.071345029239765 | 24.4 |
| Backend RSS MB | 53.34 | 156.24052631578948 | 182.34 |
| JMeter CPU % | 0.0 | 6.927485380116958 | 271.2 |
| JMeter RSS MB | 40.76 | 603.0427777777778 | 813.5 |
| System CPU % | 15.4 | 46.067251461988306 | 99.8 |
| System RAM available MB | 939.82 | 2117.689385964912 | 3226.2 |

- Backend RSS start/end: 58.29 / 182.13 MB
- Resource samples: 342

## Note

75% of stress capacity C=160 VUs
