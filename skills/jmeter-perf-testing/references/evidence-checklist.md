# Evidence checklist

## Before a run

- [ ] SUT commit recorded (`docs/sut_commit.txt`)
- [ ] Local patches documented (e.g. port 3100)
- [ ] Backend started and listening; health check 200
- [ ] Dataset seeded after backend start
- [ ] DB counts recorded (users/products/orders)
- [ ] CSV SHA-256 recorded
- [ ] Lockout flags reset
- [ ] Hardware/hostname captured
- [ ] JMeter/JDK versions captured
- [ ] Output directory empty
- [ ] Power plan / background apps noted

## During a run

- [ ] Resource monitor sampling every 2 s
- [ ] JMeter non-GUI (`-n`), raw `-l`, dashboard `-e -o`
- [ ] Backend log and JMeter log retained
- [ ] Manual stop conditions watched (error %, p95, CPU)
- [ ] No GUI listener live for stress/spike

## After a run

- [ ] JTL SHA-256 recorded
- [ ] Manifest written (command, params, start/end, PIDs, counts)
- [ ] HTML dashboard generated
- [ ] Report-view screenshot captured from the saved JTL
- [ ] Resource chart/CSV retained
- [ ] Analysis script run; numbers match the JTL
- [ ] Expected negative tests separated from error %
- [ ] DB orders/lockout reset
- [ ] Real bugs/issues filed with evidence links

## Files to keep

```text
results/<scenario>/
  *.jtl
  html/
  resources.csv
  jmeter.log
  manifest.md
  manifest.json
analysis/
  <scenario>_summary.md
  <scenario>_summary.json
  <scenario>_intervals.csv
```
