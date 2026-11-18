# Run manifest — Load

- Scenario: **Load**
- Started: 2026-11-16T12:22:49+07:00
- Ended: 2026-11-16T12:32:54+07:00 (elapsed 605.08 s)
- JMeter exit code: 0
- Test plan: `test-plans\23120372_Load_20261116.jmx` (SHA-256 `530985258d2e8b0aec1e0a11247a83a5997c3b9c3cd78d32e9f0e8f6e66ac801`)
- JTL: `results\load\23120372_Load_20261116.jtl` (SHA-256 `d309472d6a7494d836182031902adb2519a4f571ee3239e95ce6cc72defa9396`)
- CSV: `data/e2e_data.csv` (SHA-256 `5ceff8eab0c3b2ceb3ac331241c80b2837f854e6b14d96024ddc1032a4a68edc`)
- Samples: 8417; failed: 0
- Avg elapsed (all samples): 5.17 ms; max: 1619.0 ms
- DB counts before: {'users': 503, 'products': 205, 'orders': 0}
- DB counts after: {'users': 503, 'products': 205, 'orders': 1196}
- Backend PID: 4748
- Host: DESKTOP-BCS88BQ — Windows-11-10.0.26200-SP0
- HW05 git commit: `fd73e49ebfa7476bd2375bd72f11ebb8fca0b48c`
- SUT commit: `85af3ba875c88283615e22cb108f13e2fccaf0e9`
- JMeter command: `cmd /c C:\HCMUS\hk7\Testing\apache-jmeter-5.6.3\bin\jmeter.bat -n -t C:\HCMUS\hk7\Testing\hw5\test-plans\23120372_Load_20261116.jmx -l C:\HCMUS\hk7\Testing\hw5\results\load\23120372_Load_20261116.jtl -j C:\HCMUS\hk7\Testing\hw5\results\load\jmeter.log -Jhost=localhost -Jport=3100 -Jcsv=data/e2e_data.csv -Jthreads=30 -Jramp=60 -Jduration=600 -e -o C:\HCMUS\hk7\Testing\hw5\results\load\html`

## Resource summary

| Metric | Min | Avg | Max |
|---|---:|---:|---:|
| Backend CPU % | 0.0 | 3.1215488215488216 | 9.2 |
| Backend RSS MB | 48.97 | 62.29572390572391 | 65.91 |
| JMeter CPU % | 0.0 | 3.10976430976431 | 184.7 |
| JMeter RSS MB | 8.27 | 273.24781144781144 | 624.1 |
| System CPU % | 8.1 | 21.544444444444444 | 56.2 |
| System RAM available MB | 3037.04 | 3766.039023569024 | 4040.8 |

- Backend RSS start/end: 48.97 / 65.55 MB
- Resource samples: 297

## Note

Official Load run: 30 VUs, ramp 60 s, duration 600 s, think 2000 +/- 1000 ms
