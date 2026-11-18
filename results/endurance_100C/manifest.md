# Run manifest — Endurance

- Scenario: **Endurance**
- Started: 2026-11-18T15:47:35+07:00
- Ended: 2026-11-18T15:59:42+07:00 (elapsed 727.2 s)
- JMeter exit code: 0
- Test plan: `test-plans\23120372_Endurance_20261118.jmx` (SHA-256 `94009ca2c60c86e14bda9b7333949924683c09e9981dd5a55ebce768ebe0837c`)
- JTL: `results\endurance_100C\23120372_Endurance_20261118.jtl` (SHA-256 `b20f0b65e04a317a1fc6b1e65476367ffedf27866787f1a18317c241926f8575`)
- CSV: `data/e2e_data.csv` (SHA-256 `5ceff8eab0c3b2ceb3ac331241c80b2837f854e6b14d96024ddc1032a4a68edc`)
- Samples: 54488; failed: 0
- Avg elapsed (all samples): 10.16 ms; max: 1248.0 ms
- DB counts before: {'users': 503, 'products': 205, 'orders': 0}
- DB counts after: {'users': 503, 'products': 205, 'orders': 7734}
- Backend PID: 19200
- Host: DESKTOP-BCS88BQ — Windows-11-10.0.26200-SP0
- HW05 git commit: `fd73e49ebfa7476bd2375bd72f11ebb8fca0b48c`
- SUT commit: `85af3ba875c88283615e22cb108f13e2fccaf0e9`
- JMeter command: `cmd /c C:\HCMUS\hk7\Testing\apache-jmeter-5.6.3\bin\jmeter.bat -n -t C:\HCMUS\hk7\Testing\hw5\test-plans\23120372_Endurance_20261118.jmx -l C:\HCMUS\hk7\Testing\hw5\results\endurance_100C\23120372_Endurance_20261118.jtl -j C:\HCMUS\hk7\Testing\hw5\results\endurance_100C\jmeter.log -Jhost=localhost -Jport=3100 -Jcsv=data/e2e_data.csv -Jthreads=160 -Jduration=720 -e -o C:\HCMUS\hk7\Testing\hw5\results\endurance_100C\html`

## Resource summary

| Metric | Min | Avg | Max |
|---|---:|---:|---:|
| Backend CPU % | 0.0 | 15.143227665706052 | 26.5 |
| Backend RSS MB | 53.07 | 160.6436311239193 | 182.25 |
| JMeter CPU % | 0.0 | 6.250720461095101 | 131.4 |
| JMeter RSS MB | 8.18 | 655.8828818443804 | 813.0 |
| System CPU % | 12.8 | 36.627089337175796 | 99.7 |
| System RAM available MB | 1574.77 | 2422.973198847262 | 3195.89 |

- Backend RSS start/end: 58.21 / 179.77 MB
- Resource samples: 347

## Note

100% of stress capacity C=160 VUs
