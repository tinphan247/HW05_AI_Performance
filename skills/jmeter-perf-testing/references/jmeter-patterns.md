# JMeter 5.6.3 patterns used in HW05

## CSV Data Set Config

```xml
<CSVDataSet guiclass="TestBeanGUI" testclass="CSVDataSet" testname="CSV E2E data" enabled="true">
  <stringProp name="delimiter">,</stringProp>
  <stringProp name="fileEncoding">UTF-8</stringProp>
  <stringProp name="filename">${__P(csv,data/e2e_data.csv)}</stringProp>
  <boolProp name="quotedData">false</boolProp>
  <boolProp name="recycle">true</boolProp>
  <stringProp name="shareMode">shareMode.all</stringProp>
  <boolProp name="stopThread">false</boolProp>
  <stringProp name="variableNames">email,password,product_id,product_name,price,quantity,search_keyword,shipping_address,total_amount</stringProp>
  <boolProp name="ignoreFirstLine">true</boolProp>
</CSVDataSet>
```

- `ignoreFirstLine=true` when the CSV has a header. Forgetting this consumes the header as the first data row and sends literal `${email}` / `product_id`.
- `shareMode.all` gives each thread a different row. `shareMode.thread` restarts at row 1 for each thread.
- Run JMeter from the repository root so a relative filename resolves.

## JSON Extractor

```xml
<JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="Extract token" enabled="true">
  <stringProp name="JSONPostProcessor.referenceNames">token</stringProp>
  <stringProp name="JSONPostProcessor.jsonPathExprs">$.token</stringProp>
  <stringProp name="JSONPostProcessor.match_numbers">1</stringProp>
  <stringProp name="JSONPostProcessor.defaultValues">NOT_FOUND</stringProp>
</JSONPostProcessor>
```

Use the extracted `${token}` in a Header Manager (`Authorization: Bearer ${token}`).

## Raw JSON body

```xml
<boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
<elementProp name="HTTPsampler.Arguments" elementType="Arguments">
  <collectionProp name="Arguments.arguments">
    <elementProp name="" elementType="HTTPArgument">
      <boolProp name="HTTPArgument.always_encode">false</boolProp>
      <stringProp name="Argument.value">{"email":"${email}","password":"${password}"}</stringProp>
      <stringProp name="Argument.metadata">=</stringProp>
    </elementProp>
  </collectionProp>
</elementProp>
```

## Assertions

- Status code: `Assertion.response_code`, `test_type=8` (equals).
- Body contains: `Assertion.response_data`, `test_type=16` (substring).
- Do not assert a numeric price: this SUT returns `price` as a string for even product IDs.

## Controllers

- `TransactionController` **always** emits a sample. `parent=true` makes it a parent of the children; `parent=false` makes it a sibling. Both appear in the JTL and inflate sample counts / include think time.
- Use `GenericController` when you only want grouping with no extra sample.
- Put the timer inside the controller; `TransactionController.includeTimers=false` does not remove wall-clock gaps from the parent sample in practice.

## Thread groups

- Load/Endurance: `scheduler=true`, `loops=-1`, `duration=<seconds>`, `ramp_time=<seconds>`.
- Stress: one thread group per step, same duration, `delay = step_index * duration`.
- Spike: baseline / burst / recovery groups with cumulative delays.
- `on_sample_error=continue` so one failed request does not stop the thread.

## Listeners

- Keep Summary/Aggregate/View Results Tree in the plan for documentation, but set `enabled="false"` for non-GUI runs.
- Write the raw log with `-l file.jtl`; generate the dashboard with `-e -o dir`.
- To inspect a saved JTL in the GUI, open JMeter and use the listener's file browser or the report dashboard; do not re-run stress with View Results Tree live.

## Useful properties

```text
-Jhost=localhost -Jport=3100 -Jcsv=data/e2e_data.csv
-Jthreads=30 -Jramp=60 -Jduration=600
```

> On Windows, `cmd` splits an **unquoted** argument at the dot, so
> `-Jcsv=data/e2e_data.csv` becomes `-Jcsv=data/e2e_data` + `.csv` and JMeter fails with
> `Unknown arg: .csv`. Either omit `-Jcsv` (the plan already defaults to
> `${__P(csv,data/e2e_data.csv)}`) or quote it: `"-Jcsv=data\e2e_data.csv"`.
> Passing args as a Python list (no shell) is unaffected.

## Common failure signatures

| Symptom | Likely cause |
|---|---|
| First iteration sends `${email}` literally | CSV header not ignored |
| All threads use the same account | `shareMode.thread` or wrong CSV path |
| 401 on every login | CSV password wrong / dataset reseeded after CSV generation |
| Lockout probe returns 401,401,401 | async SQLite update race; pace attempts |
| Transaction time much larger than child sum | parent sample includes think time |
| Error % looks high in stress | expected negative test left in main plan |
| `Unknown arg: .csv` on Windows | unquoted `-Jcsv=...csv` split by `cmd`; omit or quote it |
