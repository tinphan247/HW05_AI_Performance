#!/usr/bin/env python3
"""Generate the JMeter test plans for HW05.

One shared end-to-end workflow is used by every plan:

    public product list -> public search -> login (extract token)
    -> authenticated product detail -> add to cart -> checkout
    -> my orders

A separate Lockout Probe thread group exercises the failed-login path with a
dedicated account (3 attempts: 401, 401, 403) so the main 500 users are never
locked out.

Scenarios:
    Load      -> Summary Report     (30 VUs, ramp 60 s, 10 min)
    Stress    -> Aggregate Report   (6 steps: 10/20/40/80/120/160 VUs x 2 min)
    Spike     -> View Results Tree  (baseline 10 -> spike 100 -> recovery 10, x3)
    Endurance -> Summary Report     (parameterised, 12 min default)

Usage:
    python scripts/generate_jmx.py
    python scripts/generate_jmx.py --date 20261116
    python scripts/generate_jmx.py --profile smoke --out-dir results/pilot

The generated plans use:
    ${__P(host,localhost)} and ${__P(port,3100)} for the target,
    ${__P(csv,data/e2e_data.csv)} for the CSV dataset,
    ${__P(threads,30)} / ${__P(ramp,60)} / ${__P(duration,600)} for Load/Endurance.

Run JMeter from the repository root so relative CSV paths resolve.
"""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]

STUDENT_ID = "23120372"

E2E_CSV_VARS = (
    "email,password,product_id,product_name,price,quantity,"
    "search_keyword,shipping_address,total_amount"
)

SAVE_CONFIG = """<objProp>
  <name>saveConfig</name>
  <value class="SampleSaveConfiguration">
    <time>true</time>
    <latency>true</latency>
    <timestamp>true</timestamp>
    <success>true</success>
    <label>true</label>
    <code>true</code>
    <message>true</message>
    <threadName>true</threadName>
    <dataType>true</dataType>
    <encoding>false</encoding>
    <assertions>true</assertions>
    <subresults>true</subresults>
    <responseData>false</responseData>
    <samplerData>false</samplerData>
    <xml>false</xml>
    <fieldNames>true</fieldNames>
    <responseHeaders>false</responseHeaders>
    <requestHeaders>false</requestHeaders>
    <responseDataOnError>false</responseDataOnError>
    <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
    <assertionsResultsToSave>0</assertionsResultsToSave>
    <bytes>true</bytes>
    <sentBytes>true</sentBytes>
    <url>true</url>
    <threadCounts>true</threadCounts>
    <idleTime>true</idleTime>
    <connectTime>true</connectTime>
    <hostname>false</hostname>
  </value>
</objProp>"""


def ind(level: int) -> str:
    return "  " * level


def http_defaults(level: int) -> str:
    i = ind(level)
    return f"""{i}<ConfigTestElement guiclass="HttpDefaultsGui" testclass="ConfigTestElement" testname="HTTP Request Defaults" enabled="true">
{i}  <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
{i}    <collectionProp name="Arguments.arguments"/>
{i}  </elementProp>
{i}  <stringProp name="HTTPSampler.domain">${{__P(host,localhost)}}</stringProp>
{i}  <stringProp name="HTTPSampler.port">${{__P(port,3100)}}</stringProp>
{i}  <stringProp name="HTTPSampler.protocol">http</stringProp>
{i}  <stringProp name="HTTPSampler.contentEncoding">UTF-8</stringProp>
{i}  <stringProp name="HTTPSampler.path"></stringProp>
{i}  <stringProp name="HTTPSampler.concurrentPool">6</stringProp>
{i}  <stringProp name="HTTPSampler.connect_timeout"></stringProp>
{i}  <stringProp name="HTTPSampler.response_timeout"></stringProp>
{i}</ConfigTestElement>
{i}<hashTree/>"""


def result_collector(level: int, guiclass: str, name: str, enabled: bool = False) -> str:
    i = ind(level)
    return f"""{i}<ResultCollector guiclass="{guiclass}" testclass="ResultCollector" testname="{name}" enabled="{str(enabled).lower()}">
{i}  <boolProp name="ResultCollector.error_logging">false</boolProp>
{i}  {SAVE_CONFIG.replace(chr(10), chr(10) + i + "  ")}
{i}  <stringProp name="filename"></stringProp>
{i}</ResultCollector>
{i}<hashTree/>"""


def csv_dataset(level: int, name: str, filename: str, variables: str) -> str:
    i = ind(level)
    return f"""{i}<CSVDataSet guiclass="TestBeanGUI" testclass="CSVDataSet" testname="{name}" enabled="true">
{i}  <stringProp name="delimiter">,</stringProp>
{i}  <stringProp name="fileEncoding">UTF-8</stringProp>
{i}  <stringProp name="filename">{escape(filename)}</stringProp>
{i}  <boolProp name="quotedData">false</boolProp>
{i}  <boolProp name="recycle">true</boolProp>
{i}  <stringProp name="shareMode">shareMode.all</stringProp>
{i}  <boolProp name="stopThread">false</boolProp>
{i}  <stringProp name="variableNames">{variables}</stringProp>
{i}  <boolProp name="ignoreFirstLine">true</boolProp>
{i}</CSVDataSet>
{i}<hashTree/>"""


def header_manager(level: int, with_auth: bool = True) -> str:
    i = ind(level)
    auth = ""
    if with_auth:
        auth = f"""
{i}    <elementProp name="Authorization" elementType="Header">
{i}      <stringProp name="Header.name">Authorization</stringProp>
{i}      <stringProp name="Header.value">Bearer ${{token}}</stringProp>
{i}    </elementProp>"""
    return f"""{i}<HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="HTTP Header Manager" enabled="true">
{i}  <collectionProp name="HeaderManager.headers">
{i}    <elementProp name="Content-Type" elementType="Header">
{i}      <stringProp name="Header.name">Content-Type</stringProp>
{i}      <stringProp name="Header.value">application/json</stringProp>
{i}    </elementProp>{auth}
{i}  </collectionProp>
{i}</HeaderManager>
{i}<hashTree/>"""


def think_timer(level: int, delay_ms: int, range_ms: int, name: str = "Think time") -> str:
    i = ind(level)
    return f"""{i}<GaussianRandomTimer guiclass="GaussianRandomTimerGui" testclass="GaussianRandomTimer" testname="{name}" enabled="true">
{i}  <stringProp name="ConstantTimer.delay">{delay_ms}</stringProp>
{i}  <stringProp name="RandomTimer.range">{range_ms}.0</stringProp>
{i}</GaussianRandomTimer>
{i}<hashTree/>"""


def response_assertion(level: int, name: str, code: str) -> str:
    i = ind(level)
    return f"""{i}<ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="{name}" enabled="true">
{i}  <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
{i}  <boolProp name="Assertion.assume_success">false</boolProp>
{i}  <intProp name="Assertion.test_type">8</intProp>
{i}  <stringProp name="Assertion.scope">all</stringProp>
{i}  <collectionProp name="Asserion.test_strings">
{i}    <stringProp name="{abs(hash(name + code)) % 1000000}">{code}</stringProp>
{i}  </collectionProp>
{i}  <stringProp name="Assertion.custom_message">Expected HTTP {code}</stringProp>
{i}</ResponseAssertion>
{i}<hashTree/>"""


def body_assertion(level: int, name: str, text: str) -> str:
    i = ind(level)
    safe_name = escape(name, {'"': "&quot;"})
    return f"""{i}<ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="{safe_name}" enabled="true">
{i}  <stringProp name="Assertion.test_field">Assertion.response_data</stringProp>
{i}  <boolProp name="Assertion.assume_success">false</boolProp>
{i}  <intProp name="Assertion.test_type">16</intProp>
{i}  <stringProp name="Assertion.scope">all</stringProp>
{i}  <collectionProp name="Asserion.test_strings">
{i}    <stringProp name="{abs(hash(name + text)) % 1000000}">{escape(text)}</stringProp>
{i}  </collectionProp>
{i}  <stringProp name="Assertion.custom_message">Expected body to contain {escape(text)}</stringProp>
{i}</ResponseAssertion>
{i}<hashTree/>"""


def json_extractor(level: int, name: str, ref: str, path: str) -> str:
    i = ind(level)
    return f"""{i}<JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="{name}" enabled="true">
{i}  <stringProp name="JSONPostProcessor.referenceNames">{ref}</stringProp>
{i}  <stringProp name="JSONPostProcessor.jsonPathExprs">{escape(path)}</stringProp>
{i}  <stringProp name="JSONPostProcessor.match_numbers">1</stringProp>
{i}  <stringProp name="JSONPostProcessor.defaultValues">NOT_FOUND</stringProp>
{i}  <boolProp name="JSONPostProcessor.computeConcatenation">false</boolProp>
{i}</JSONPostProcessor>
{i}<hashTree/>"""


def http_sampler(
    level: int,
    name: str,
    method: str,
    path: str,
    body: str | None = None,
    code: str = "200",
    contains: list[str] | None = None,
    extract: tuple[str, str] | None = None,
) -> str:
    i = ind(level)
    if body is None:
        arguments = f"""{i}  <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
{i}    <collectionProp name="Arguments.arguments"/>
{i}  </elementProp>"""
        raw = "false"
    else:
        arguments = f"""{i}  <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
{i}    <collectionProp name="Arguments.arguments">
{i}      <elementProp name="" elementType="HTTPArgument">
{i}        <boolProp name="HTTPArgument.always_encode">false</boolProp>
{i}        <stringProp name="Argument.value">{escape(body)}</stringProp>
{i}        <stringProp name="Argument.metadata">=</stringProp>
{i}      </elementProp>
{i}    </collectionProp>
{i}  </elementProp>"""
        raw = "true"

    children = [response_assertion(level + 1, f"Assert {code} - {name}", code)]
    if contains:
        for text in contains:
            children.append(body_assertion(level + 1, f'Assert body contains "{text}" - {name}', text))
    if extract:
        children.append(json_extractor(level + 1, f"Extract {extract[0]} - {name}", extract[0], extract[1]))

    return f"""{i}<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="{name}" enabled="true">
{i}  <boolProp name="HTTPSampler.postBodyRaw">{raw}</boolProp>
{arguments}
{i}  <stringProp name="HTTPSampler.path">{escape(path)}</stringProp>
{i}  <stringProp name="HTTPSampler.method">{method}</stringProp>
{i}  <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
{i}  <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
{i}  <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
{i}  <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
{i}  <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
{i}  <stringProp name="HTTPSampler.connect_timeout"></stringProp>
{i}  <stringProp name="HTTPSampler.response_timeout"></stringProp>
{i}</HTTPSamplerProxy>
{i}<hashTree>
{chr(10).join(children)}
{i}</hashTree>"""


def e2e_transaction(level: int, name: str, think: tuple[int, int] = (1000, 500)) -> str:
    i = ind(level)
    samplers = [
        think_timer(level + 1, think[0], think[1]),
        http_sampler(level + 1, "GET /api/products (list)", "GET", "/api/products", contains=['"name"']),
        http_sampler(level + 1, "GET /api/products?search", "GET", "/api/products?search=${search_keyword}"),
        http_sampler(
            level + 1,
            "POST /api/login",
            "POST",
            "/api/login",
            body='{"email":"${email}","password":"${password}"}',
            contains=['"token"'],
            extract=("token", "$.token"),
        ),
        http_sampler(level + 1, "GET /api/products/{id}", "GET", "/api/products/${product_id}", contains=['"id"']),
        http_sampler(
            level + 1,
            "POST /api/cart",
            "POST",
            "/api/cart",
            body='{"id":${product_id},"name":"${product_name}","price":${price},"quantity":${quantity}}',
            contains=["Added to cart"],
        ),
        http_sampler(
            level + 1,
            "POST /api/checkout",
            "POST",
            "/api/checkout",
            body='{"total_amount":${total_amount},"shipping_address":"${shipping_address}"}',
            contains=['"orderId"'],
            extract=("order_id", "$.orderId"),
        ),
        http_sampler(level + 1, "GET /api/orders/my-orders", "GET", "/api/orders/my-orders", contains=["["]),
    ]
    return f"""{i}<GenericController guiclass="LogicControllerGui" testclass="GenericController" testname="{name}" enabled="true">
{i}</GenericController>
{i}<hashTree>
{chr(10).join(samplers)}
{i}</hashTree>"""


def thread_group(
    level: int,
    name: str,
    threads: str,
    ramp: str,
    duration: str,
    delay: str,
    loops: str = "-1",
    scheduler: bool = True,
    csv: bool = True,
    think: tuple[int, int] = (1000, 500),
    tx_name: str = "E2E_Transaction",
) -> str:
    i = ind(level)
    children = []
    if csv:
        children.append(csv_dataset(level + 1, "CSV E2E data", "${__P(csv,data/e2e_data.csv)}", E2E_CSV_VARS))
    children.append(header_manager(level + 1, with_auth=True))
    children.append(e2e_transaction(level + 1, tx_name, think=think))

    return f"""{i}<ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="{name}" enabled="true">
{i}  <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
{i}  <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller" enabled="true">
{i}    <boolProp name="LoopController.continue_forever">{str(scheduler or loops == "-1").lower()}</boolProp>
{i}    <stringProp name="LoopController.loops">{loops}</stringProp>
{i}  </elementProp>
{i}  <stringProp name="ThreadGroup.num_threads">{threads}</stringProp>
{i}  <stringProp name="ThreadGroup.ramp_time">{ramp}</stringProp>
{i}  <boolProp name="ThreadGroup.scheduler">{str(scheduler).lower()}</boolProp>
{i}  <stringProp name="ThreadGroup.duration">{duration if scheduler else ""}</stringProp>
{i}  <stringProp name="ThreadGroup.delay">{delay}</stringProp>
{i}  <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
{i}</ThreadGroup>
{i}<hashTree>
{chr(10).join(children)}
{i}</hashTree>"""


def lockout_group(level: int, delay: str = "0") -> str:
    i = ind(level)
    attempts = []
    for n, code in ((1, "401"), (2, "401"), (3, "403")):
        attempts.append(
            http_sampler(
                level + 1,
                f"Lockout attempt {n} (expect {code})",
                "POST",
                "/api/login",
                body='{"email":"${email}","password":"${wrong_password}"}',
                code=code,
            )
        )
    csv = csv_dataset(level + 1, "CSV lockout account", "${__P(lockout_csv,data/lockout.csv)}", "email,wrong_password")
    headers = header_manager(level + 1, with_auth=False)
    pacing = f"""{ind(level + 1)}<ConstantTimer guiclass="ConstantTimerGui" testclass="ConstantTimer" testname="Lockout pacing (1.5 s)" enabled="true">
{ind(level + 1)}  <stringProp name="ConstantTimer.delay">1500</stringProp>
{ind(level + 1)}</ConstantTimer>
{ind(level + 1)}<hashTree/>"""
    return f"""{i}<ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Lockout Probe (dedicated account)" enabled="true">
{i}  <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
{i}  <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller" enabled="true">
{i}    <boolProp name="LoopController.continue_forever">false</boolProp>
{i}    <stringProp name="LoopController.loops">1</stringProp>
{i}  </elementProp>
{i}  <stringProp name="ThreadGroup.num_threads">1</stringProp>
{i}  <stringProp name="ThreadGroup.ramp_time">1</stringProp>
{i}  <boolProp name="ThreadGroup.scheduler">true</boolProp>
{i}  <stringProp name="ThreadGroup.duration">30</stringProp>
{i}  <stringProp name="ThreadGroup.delay">{delay}</stringProp>
{i}  <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
{i}</ThreadGroup>
{i}<hashTree>
{csv}
{headers}
{pacing}
{chr(10).join(attempts)}
{i}</hashTree>"""


def build_plan(comment: str, listeners: list[tuple[str, str]], groups: list[str]) -> str:
    body = "\n".join(groups)
    listener_xml = "\n".join(result_collector(3, gui, name) for gui, name in listeners)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="{STUDENT_ID} - EShop Performance Test" enabled="true">
      <stringProp name="TestPlan.comments">{escape(comment)}</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
{http_defaults(3)}
{listener_xml}
{body}
    </hashTree>
  </hashTree>
</jmeterTestPlan>
"""


def load_plan(smoke: bool) -> str:
    if smoke:
        groups = [thread_group(3, "Load - 1 VU smoke", "1", "1", "10", "0", think=(200, 100), tx_name="Load_E2E")]
        return build_plan(
            "SMOKE ONLY - Load plan validation. 1 VU, 10 s. The lockout probe is run as a separate plan.",
            [("SummaryReport", "Summary Report")],
            groups,
        )
    groups = [
        thread_group(
            3,
            "Load - ${__P(threads,30)} VUs",
            "${__P(threads,30)}",
            "${__P(ramp,60)}",
            "${__P(duration,600)}",
            "0",
            think=(2000, 1000),
            tx_name="Load_E2E_Transaction",
        )
    ]
    return build_plan(
        "Load test: 30 VUs (property threads), ramp 60 s, duration 600 s, think 2000 +/- 1000 ms. "
        "Shared E2E workflow: products -> search -> login -> product detail -> cart -> checkout -> my-orders. "
        "Report view: Summary Report. The lockout probe is a separate plan.",
        [("SummaryReport", "Summary Report")],
        groups,
    )


def stress_plan(smoke: bool) -> str:
    if smoke:
        groups = [
            thread_group(3, "Stress smoke - 1 VU", "1", "1", "8", "0", think=(200, 100), tx_name="Stress_E2E")
        ]
    else:
        levels = [10, 20, 40, 80, 120, 160]
        groups = []
        for idx, threads in enumerate(levels):
            delay = idx * 120
            groups.append(
                thread_group(
                    3,
                    f"Stress S{idx + 1} - {threads} VUs",
                    str(threads),
                    "10",
                    "120",
                    str(delay),
                    think=(1000, 500),
                    tx_name=f"Stress_S{idx + 1}_E2E",
                )
            )
    return build_plan(
        "Stress test: 6 steps 10/20/40/80/120/160 VUs, each 120 s duration, 10 s ramp, "
        "startup delays 0/120/240/360/480/600 s, think 1000 +/- 500 ms. "
        "Stop conditions are monitored manually (error > 5%, p95 > 2000 ms, backend CPU > 90%, "
        "backend crash, JMeter CPU > 85%). Report view: Aggregate Report. The lockout probe is a separate plan.",
        [("StatVisualizer", "Aggregate Report")],
        groups,
    )


def spike_plan(smoke: bool) -> str:
    if smoke:
        groups = [
            thread_group(3, "Spike smoke - baseline", "1", "1", "4", "0", think=(200, 100), tx_name="Spike_Baseline"),
            thread_group(3, "Spike smoke - spike", "2", "1", "4", "4", think=(200, 100), tx_name="Spike_Burst"),
            thread_group(3, "Spike smoke - recovery", "1", "1", "4", "8", think=(200, 100), tx_name="Spike_Recovery"),
        ]
    else:
        groups = []
        cycle = 0
        for c in range(3):
            base = c * 300
            cycle += 1
            groups.append(
                thread_group(
                    3,
                    f"Spike C{cycle} - Baseline 10 VUs",
                    "10",
                    "10",
                    "120",
                    str(base),
                    think=(1000, 500),
                    tx_name=f"Spike_C{cycle}_Baseline",
                )
            )
            groups.append(
                thread_group(
                    3,
                    f"Spike C{cycle} - Spike 100 VUs",
                    "100",
                    "5",
                    "60",
                    str(base + 120),
                    think=(1000, 500),
                    tx_name=f"Spike_C{cycle}_Burst",
                )
            )
            groups.append(
                thread_group(
                    3,
                    f"Spike C{cycle} - Recovery 10 VUs",
                    "10",
                    "5",
                    "120",
                    str(base + 180),
                    think=(1000, 500),
                    tx_name=f"Spike_C{cycle}_Recovery",
                )
            )
    return build_plan(
        "Spike test: 3 cycles of baseline 10 VUs (120 s) -> spike 100 VUs (60 s, 5 s ramp) "
        "-> recovery 10 VUs (120 s), think 1000 +/- 500 ms. Report view: View Results Tree "
        "(opened post-run from the saved JTL; not used live). The lockout probe is a separate plan.",
        [("ViewResultsFullVisualizer", "View Results Tree")],
        groups,
    )


def endurance_plan(smoke: bool) -> str:
    threads = "1" if smoke else "${__P(threads,30)}"
    ramp = "1" if smoke else "${__P(ramp,60)}"
    duration = "10" if smoke else "${__P(duration,720)}"
    groups = [
        thread_group(
            3,
            f"Endurance - {threads} VUs",
            threads,
            ramp,
            duration,
            "0",
            think=(2000, 1000),
            tx_name="Endurance_E2E_Transaction",
        )
    ]
    return build_plan(
        "Endurance: parameterised threads (default 30), ramp 60 s, duration 720 s (12 min). "
        "Run at 50/75/100% of stress capacity. Report view: Summary Report.",
        [("SummaryReport", "Summary Report")],
        groups,
    )


def lockout_plan(smoke: bool) -> str:
    duration = "10" if smoke else "30"
    group = lockout_group(3).replace(
        '<stringProp name="ThreadGroup.duration">30</stringProp>',
        f'<stringProp name="ThreadGroup.duration">{duration}</stringProp>',
    )
    return build_plan(
        "Lockout probe (separate run): dedicated account lockout@eshop.test, three wrong passwords "
        "paces 1.5 s apart. Expected codes 401, 401, 403. This plan is intentionally separate so "
        "expected 4xx results do not inflate the main Load/Stress/Spike error rate.",
        [("SimpleDataWriter", "Raw JTL writer")],
        [group],
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=dt.date.today().strftime("%Y%m%d"))
    parser.add_argument("--profile", choices=["full", "smoke"], default="full")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "test-plans")
    args = parser.parse_args()

    out: Path = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    smoke = args.profile == "smoke"
    suffix = "_smoke" if smoke else ""
    date = args.date

    plans = {
        f"{STUDENT_ID}_Load_{date}{suffix}.jmx": load_plan(smoke),
        f"{STUDENT_ID}_Stress_{date}{suffix}.jmx": stress_plan(smoke),
        f"{STUDENT_ID}_Spike_{date}{suffix}.jmx": spike_plan(smoke),
        f"{STUDENT_ID}_Endurance_{date}{suffix}.jmx": endurance_plan(smoke),
        f"{STUDENT_ID}_Lockout_{date}{suffix}.jmx": lockout_plan(smoke),
    }

    for name, content in plans.items():
        path = out / name
        path.write_text(content, encoding="utf-8", newline="\n")
        print(f"Wrote {path} ({len(content)} bytes)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
