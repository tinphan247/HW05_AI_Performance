# Run manifest — Endurance

- Scenario: **Endurance**
- Started: 2026-11-18T15:22:30+07:00
- Ended: 2026-11-18T15:34:38+07:00 (elapsed 728.39 s)
- JMeter exit code: 0
- Test plan: `test-plans\23120372_Endurance_20261118.jmx` (SHA-256 `94009ca2c60c86e14bda9b7333949924683c09e9981dd5a55ebce768ebe0837c`)
- JTL: `results\endurance_50C\23120372_Endurance_20261118.jtl` (SHA-256 `45ff21bdc72be19748df01ddab1a86032f8178bd177420156a8e6539d63062d5`)
- CSV: `data/e2e_data.csv` (SHA-256 `5ceff8eab0c3b2ceb3ac331241c80b2837f854e6b14d96024ddc1032a4a68edc`)
- Samples: 27388; failed: 0
- Avg elapsed (all samples): 5.55 ms; max: 92.0 ms
- DB counts before: {'users': 503, 'products': 205, 'orders': 0}
- DB counts after: {'users': 503, 'products': 205, 'orders': 3890}
- Backend PID: 28904
- Host: DESKTOP-BCS88BQ — Windows-11-10.0.26200-SP0
- HW05 git commit: `fd73e49ebfa7476bd2375bd72f11ebb8fca0b48c`
- SUT commit: `85af3ba875c88283615e22cb108f13e2fccaf0e9`
- JMeter command: `cmd /c C:\HCMUS\hk7\Testing\apache-jmeter-5.6.3\bin\jmeter.bat -n -t C:\HCMUS\hk7\Testing\hw5\test-plans\23120372_Endurance_20261118.jmx -l C:\HCMUS\hk7\Testing\hw5\results\endurance_50C\23120372_Endurance_20261118.jtl -j C:\HCMUS\hk7\Testing\hw5\results\endurance_50C\jmeter.log -Jhost=localhost -Jport=3100 -Jcsv=data/e2e_data.csv -Jthreads=80 -Jduration=720 -e -o C:\HCMUS\hk7\Testing\hw5\results\endurance_50C\html`

## Resource summary

| Metric | Min | Avg | Max |
|---|---:|---:|---:|
| Backend CPU % | 0.0 | 13.578106508875738 | 28.2 |
| Backend RSS MB | 52.54 | 146.0098224852071 | 179.84 |
| JMeter CPU % | 0.0 | 6.379881656804734 | 162.5 |
| JMeter RSS MB | 8.18 | 510.47133136094675 | 791.49 |
| System CPU % | 15.5 | 27.31715976331361 | 65.5 |
| System RAM available MB | 2390.57 | 2823.262278106509 | 3423.43 |

- Backend RSS start/end: 57.95 / 178.76 MB
- Resource samples: 338

## Note

50% of stress capacity C=160 VUs
