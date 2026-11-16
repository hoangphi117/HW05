#!/usr/bin/env python3
"""
generate_jmx.py — HW05 Agent Skill
Sinh file JMeter .jmx cho Browse-to-Buy workflow trên EShop SUT.

Workflow (5 bước):
  1. POST /api/login          → Auth-heavy (FR-02) | Extract JWT token
  2. GET  /api/products        → Read-heavy (FR-05) | Extract product_id
  3. GET  /api/products/:id    → Read-heavy (FR-06)
  4. POST /api/cart            → Transactional (FR-07)
  5. POST /api/checkout        → Transactional (FR-08)

Usage:
  python generate_jmx.py --scenario load   --student-id 22127001 --date 20261116
  python generate_jmx.py --scenario stress --student-id 22127001 --date 20261116
  python generate_jmx.py --scenario spike  --student-id 22127001 --date 20261116
  python generate_jmx.py --scenario soak   --student-id 22127001 --date 20261116 --duration 900
"""
import argparse
import os
from datetime import datetime
from pathlib import Path


# ── Tham số mặc định cho từng scenario ────────────────────────────────────────
SCENARIO_DEFAULTS = {
    "load": {
        "threads":    50,
        "ramp_up":    60,      # giây
        "duration":   300,     # giây (5 phút)
        "think_min":  1000,    # ms
        "think_max":  3000,    # ms
        "listener":   "summary",   # Summary Report
        "description": "Load Test — 50 VU, ramp-up 60s, duration 5min",
    },
    "stress": {
        "threads":    200,
        "ramp_up":    120,
        "duration":   600,     # 10 phút
        "think_min":  500,
        "think_max":  1500,
        "listener":   "aggregate",  # Aggregate Report
        "description": "Stress Test — 200 VU, ramp-up 120s, duration 10min",
    },
    "spike": {
        "threads":    500,
        "ramp_up":    10,       # spike nhanh
        "duration":   120,      # 2 phút
        "think_min":  500,
        "think_max":  500,
        "listener":   "tree",   # View Results Tree
        "description": "Spike Test — 10→500→10 VU pattern, 2min hold",
    },
    "soak": {
        "threads":    30,
        "ramp_up":    60,
        "duration":   900,      # 15 phút
        "think_min":  2000,
        "think_max":  4000,
        "listener":   "summary",
        "description": "Soak/Endurance Test — 30 VU, 15min to find threshold",
    },
}

BASE_URL = "http://localhost:3000"


def build_jmx(
    scenario: str,
    student_id: str,
    date: str,
    base_url: str,
    threads: int,
    ramp_up: int,
    duration: int,
    think_min: int,
    think_max: int,
    listener: str,
    users_csv: str,
    products_csv: str,
) -> str:
    """Trả về nội dung XML của JMeter .jmx test plan."""

    plan_name   = f"{student_id}_{scenario.capitalize()}_{date}"
    description = SCENARIO_DEFAULTS.get(scenario, {}).get("description", plan_name)

    # ── Listener XML snippet ───────────────────────────────────────────────────
    listener_xml = {
        "summary": f"""
      <ResultCollector guiclass="SummaryReport" testclass="ResultCollector"
          testname="Summary Report" enabled="true">
        <boolProp name="ResultCollector.error_logging">false</boolProp>
        <objProp><name>saveConfig</name><value class="SampleSaveConfiguration">
          <time>true</time><latency>true</latency><timestamp>true</timestamp>
          <success>true</success><label>true</label><code>true</code>
          <message>true</message><threadName>true</threadName>
          <dataType>true</dataType><encoding>false</encoding>
          <assertions>true</assertions><subresults>true</subresults>
          <responseData>false</responseData><samplerData>false</samplerData>
          <xml>false</xml><fieldNames>true</fieldNames><responseHeaders>false</responseHeaders>
          <requestHeaders>false</requestHeaders><responseDataOnError>false</responseDataOnError>
          <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
          <bytes>true</bytes><sentBytes>true</sentBytes>
          <url>true</url><threadCounts>true</threadCounts><idleTime>true</idleTime>
          <connectTime>true</connectTime>
        </value></objProp>
        <stringProp name="filename"></stringProp>
      </ResultCollector>""",
        "aggregate": f"""
      <ResultCollector guiclass="StatVisualizer" testclass="ResultCollector"
          testname="Aggregate Report" enabled="true">
        <boolProp name="ResultCollector.error_logging">false</boolProp>
        <objProp><name>saveConfig</name><value class="SampleSaveConfiguration">
          <time>true</time><latency>true</latency><timestamp>true</timestamp>
          <success>true</success><label>true</label><code>true</code>
          <message>true</message><threadName>true</threadName>
          <dataType>true</dataType><encoding>false</encoding>
          <assertions>true</assertions><subresults>true</subresults>
          <responseData>false</responseData><samplerData>false</samplerData>
          <xml>false</xml><fieldNames>true</fieldNames><responseHeaders>false</responseHeaders>
          <requestHeaders>false</requestHeaders><responseDataOnError>false</responseDataOnError>
          <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
          <bytes>true</bytes><sentBytes>true</sentBytes>
          <url>true</url><threadCounts>true</threadCounts><idleTime>true</idleTime>
          <connectTime>true</connectTime>
        </value></objProp>
        <stringProp name="filename"></stringProp>
      </ResultCollector>""",
        "tree": f"""
      <ResultCollector guiclass="ViewResultsFullVisualizer" testclass="ResultCollector"
          testname="View Results Tree" enabled="true">
        <boolProp name="ResultCollector.error_logging">false</boolProp>
        <objProp><name>saveConfig</name><value class="SampleSaveConfiguration">
          <time>true</time><latency>true</latency><timestamp>true</timestamp>
          <success>true</success><label>true</label><code>true</code>
          <message>true</message><threadName>true</threadName>
          <dataType>true</dataType><encoding>false</encoding>
          <assertions>true</assertions><subresults>true</subresults>
          <responseData>true</responseData><samplerData>false</samplerData>
          <xml>false</xml><fieldNames>true</fieldNames><responseHeaders>true</responseHeaders>
          <requestHeaders>true</requestHeaders><responseDataOnError>true</responseDataOnError>
          <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
          <bytes>true</bytes><sentBytes>true</sentBytes>
          <url>true</url><threadCounts>true</threadCounts><idleTime>true</idleTime>
          <connectTime>true</connectTime>
        </value></objProp>
        <!-- Giới hạn 500 results để tránh memory leak trong JMeter GUI -->
        <stringProp name="filename"></stringProp>
        <intProp name="ResultCollector.reportSize">500</intProp>
      </ResultCollector>""",
    }.get(listener, "")

    # Spike scenario dùng Ultimate Thread Group (nếu có plugin) hoặc stepping
    # Dùng Stepping Thread Group nếu có jmeter-plugins
    spike_stepping = ""
    if scenario == "spike":
        spike_stepping = f"""
      <!-- NOTE: Spike pattern yêu cầu "Stepping Thread Group" từ JMeter Plugins Manager.
           Nếu chưa cài plugin, thay thế ThreadGroup bên dưới bằng Stepping Thread Group:
             Start: 10 threads
             Add: 490 threads trong 1 bước
             Hold: {duration}s
             Decrease: về 10 threads -->"""

    host    = base_url.replace("http://", "").replace("https://", "").split(":")[0]
    port    = base_url.split(":")[-1] if ":" in base_url else "80"
    protocol = "https" if base_url.startswith("https") else "http"

    jmx = f"""<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>

    <!-- ═══════════════════════════════════════════════════════════
         TEST PLAN: {plan_name}
         Description: {description}
         SUT: EShop — http://localhost:3000
         Workflow: Browse-to-Buy (Login→Products→Detail→Cart→Checkout)
         Generated by: hw05-perf-testing Agent Skill
         Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
         ═══════════════════════════════════════════════════════════ -->
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan"
        testname="{plan_name}" enabled="true">
      <stringProp name="TestPlan.comments">{description}</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments">
        <collectionProp name="Arguments.arguments">
          <elementProp name="BASE_URL" elementType="Argument">
            <stringProp name="Argument.name">BASE_URL</stringProp>
            <stringProp name="Argument.value">{base_url}</stringProp>
          </elementProp>
          <elementProp name="HOST" elementType="Argument">
            <stringProp name="Argument.name">HOST</stringProp>
            <stringProp name="Argument.value">{host}</stringProp>
          </elementProp>
          <elementProp name="PORT" elementType="Argument">
            <stringProp name="Argument.name">PORT</stringProp>
            <stringProp name="Argument.value">{port}</stringProp>
          </elementProp>
        </collectionProp>
      </elementProp>
    </TestPlan>

    <hashTree>

      <!-- ─── HTTP Defaults (dùng chung cho tất cả requests) ──────── -->
      <ConfigTestElement guiclass="HttpDefaultsGui" testclass="ConfigTestElement"
          testname="HTTP Request Defaults" enabled="true">
        <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
          <collectionProp name="Arguments.arguments"/>
        </elementProp>
        <stringProp name="HTTPSampler.domain">{host}</stringProp>
        <stringProp name="HTTPSampler.port">{port}</stringProp>
        <stringProp name="HTTPSampler.protocol">{protocol}</stringProp>
        <stringProp name="HTTPSampler.contentEncoding">UTF-8</stringProp>
        <boolProp name="HTTPSampler.image_parser">false</boolProp>
        <boolProp name="HTTPSampler.concurrentDwn">false</boolProp>
        <stringProp name="HTTPSampler.connect_timeout">10000</stringProp>
        <stringProp name="HTTPSampler.response_timeout">30000</stringProp>
      </ConfigTestElement>
      <hashTree/>

      <!-- ─── HTTP Header Manager (JSON Content-Type) ───────────────── -->
      <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager"
          testname="HTTP Header Manager" enabled="true">
        <collectionProp name="HeaderManager.headers">
          <elementProp name="Content-Type" elementType="Header">
            <stringProp name="Header.name">Content-Type</stringProp>
            <stringProp name="Header.value">application/json</stringProp>
          </elementProp>
        </collectionProp>
      </HeaderManager>
      <hashTree/>

      <!-- ─── CSV Dataset: users.csv ────────────────────────────────── -->
      <CSVDataSet guiclass="TestBeanGUI" testclass="CSVDataSet"
          testname="CSV Users Data" enabled="true">
        <stringProp name="filename">{users_csv}</stringProp>
        <stringProp name="fileEncoding">UTF-8</stringProp>
        <stringProp name="variableNames">email,password,expect_fail</stringProp>
        <boolProp name="ignoreFirstLine">true</boolProp>
        <stringProp name="delimiter">,</stringProp>
        <boolProp name="quotedData">false</boolProp>
        <boolProp name="recycle">true</boolProp>
        <boolProp name="stopThread">false</boolProp>
        <stringProp name="shareMode">shareMode.all</stringProp>
      </CSVDataSet>
      <hashTree/>

      <!-- ─── CSV Dataset: products.csv ─────────────────────────────── -->
      <CSVDataSet guiclass="TestBeanGUI" testclass="CSVDataSet"
          testname="CSV Products Data" enabled="true">
        <stringProp name="filename">{products_csv}</stringProp>
        <stringProp name="fileEncoding">UTF-8</stringProp>
        <stringProp name="variableNames">csv_product_id,csv_quantity,csv_coupon,csv_total</stringProp>
        <boolProp name="ignoreFirstLine">true</boolProp>
        <stringProp name="delimiter">,</stringProp>
        <boolProp name="quotedData">false</boolProp>
        <boolProp name="recycle">true</boolProp>
        <boolProp name="stopThread">false</boolProp>
        <stringProp name="shareMode">shareMode.all</stringProp>
      </CSVDataSet>
      <hashTree/>
{spike_stepping}
      <!-- ═══════ THREAD GROUP ═════════════════════════════════════════ -->
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup"
          testname="Browse-to-Buy — {scenario.upper()}" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController"
            guiclass="LoopControlPanel" testclass="LoopController">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <intProp name="LoopController.loops">-1</intProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">{threads}</stringProp>
        <stringProp name="ThreadGroup.ramp_time">{ramp_up}</stringProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>
        <stringProp name="ThreadGroup.duration">{duration}</stringProp>
        <stringProp name="ThreadGroup.delay">0</stringProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>

      <hashTree>

        <!-- ── Think Time (Uniform Random Timer) ──────────────────── -->
        <UniformRandomTimer guiclass="UniformRandomTimerGui"
            testclass="UniformRandomTimer" testname="Think Time" enabled="true">
          <stringProp name="ConstantTimer.delay">{think_min}</stringProp>
          <stringProp name="RandomTimer.range">{think_max - think_min}</stringProp>
        </UniformRandomTimer>
        <hashTree/>

        <!-- ════ STEP 1: AUTH-HEAVY — POST /api/login ═════════════════
             FR-02: Login & Account Lockout
             Dùng email/password từ CSV. 10% dòng có wrong-password
             → trigger lockout sau 3 lần fail (khóa 30s demo mode)
             → JMeter nhận 401/423, tiếp tục VU tiếp theo (on_sample_error=continue)
             ═══════════════════════════════════════════════════════════ -->
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy"
            testname="1. POST /api/login (Auth-heavy)" enabled="true">
          <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
            <collectionProp name="Arguments.arguments">
              <elementProp name="" elementType="HTTPArgument">
                <boolProp name="HTTPArgument.always_encode">false</boolProp>
                <stringProp name="Argument.value">{{
  "email": "${{email}}",
  "password": "${{password}}"
}}</stringProp>
                <stringProp name="Argument.metadata">=</stringProp>
              </elementProp>
            </collectionProp>
          </elementProp>
          <stringProp name="HTTPSampler.domain"></stringProp>
          <stringProp name="HTTPSampler.port"></stringProp>
          <stringProp name="HTTPSampler.protocol"></stringProp>
          <stringProp name="HTTPSampler.path">/api/login</stringProp>
          <stringProp name="HTTPSampler.method">POST</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
        </HTTPSamplerProxy>
        <hashTree>
          <!-- JSON Extractor: lấy JWT token từ response (native JMeter 5.x) -->
          <JSONPostProcessor guiclass="JSONPostProcessorGui"
              testclass="JSONPostProcessor" testname="Extract JWT Token" enabled="true">
            <stringProp name="JSONPostProcessor.referenceNames">jwt_token</stringProp>
            <stringProp name="JSONPostProcessor.jsonPathExprs">$.token</stringProp>
            <stringProp name="JSONPostProcessor.match_numbers">1</stringProp>
            <stringProp name="JSONPostProcessor.defaultValues">NO_TOKEN</stringProp>
          </JSONPostProcessor>
          <hashTree/>
          <!-- Response Assertion: 200 OK (normal) hoặc 401 (sai pass) hoặc 403 (lockout) -->
          <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion"
              testname="Assert Login 200/401/403" enabled="true">
            <collectionProp name="Asserion.test_strings">
              <stringProp name="49586">200</stringProp>
              <stringProp name="49587">401</stringProp>
              <stringProp name="49589">403</stringProp>
            </collectionProp>
            <stringProp name="Assertion.custom_message">Login failed unexpectedly. Check credentials CSV.</stringProp>
            <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
            <boolProp name="Assertion.assume_success">false</boolProp>
            <intProp name="Assertion.test_type">40</intProp>
          </ResponseAssertion>
          <hashTree/>
          <!-- JSR223 PostProcessor: lưu token vào thread variable -->
          <JSR223PostProcessor guiclass="TestBeanGUI" testclass="JSR223PostProcessor"
              testname="Store JWT Token" enabled="true">
            <stringProp name="cacheKey">true</stringProp>
            <stringProp name="filename"></stringProp>
            <stringProp name="parameters"></stringProp>
            <stringProp name="script">
def token = vars.get("jwt_token")
if (token != null &amp;&amp; token != "NO_TOKEN") {{
    vars.put("auth_header", "Bearer " + token)
}} else {{
    vars.put("auth_header", "")
}}
            </stringProp>
            <stringProp name="scriptLanguage">groovy</stringProp>
          </JSR223PostProcessor>
          <hashTree/>
        </hashTree>

        <!-- ════ STEP 2: READ-HEAVY — GET /api/products ═══════════════
             FR-05: Product listing & Search
             GET danh sách sản phẩm (không cần auth)
             Extract product_id đầu tiên từ response array
             ═══════════════════════════════════════════════════════════ -->
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy"
            testname="2. GET /api/products (Read-heavy)" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <stringProp name="HTTPSampler.path">/api/products</stringProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
        </HTTPSamplerProxy>
        <hashTree>
          <!-- JSON Extractor: lấy id của sản phẩm đầu tiên trong array (native JMeter 5.x) -->
          <JSONPostProcessor guiclass="JSONPostProcessorGui"
              testclass="JSONPostProcessor" testname="Extract First Product ID" enabled="true">
            <stringProp name="JSONPostProcessor.referenceNames">extracted_product_id</stringProp>
            <stringProp name="JSONPostProcessor.jsonPathExprs">$[0].id</stringProp>
            <stringProp name="JSONPostProcessor.match_numbers">1</stringProp>
            <stringProp name="JSONPostProcessor.defaultValues">${{csv_product_id}}</stringProp>
          </JSONPostProcessor>
          <hashTree/>
          <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion"
              testname="Assert Products 200" enabled="true">
            <collectionProp name="Asserion.test_strings">
              <stringProp name="49586">200</stringProp>
            </collectionProp>
            <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
            <boolProp name="Assertion.assume_success">false</boolProp>
            <intProp name="Assertion.test_type">8</intProp>
          </ResponseAssertion>
          <hashTree/>
        </hashTree>

        <!-- ════ STEP 3: READ-HEAVY — GET /api/products/:id ══════════
             FR-06: Product detail view
             Dùng product_id vừa extract từ bước 2 (hoặc fallback từ CSV)
             ═══════════════════════════════════════════════════════════ -->
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy"
            testname="3. GET /api/products/:id (Read-heavy)" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <stringProp name="HTTPSampler.path">/api/products/${{extracted_product_id}}</stringProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
        </HTTPSamplerProxy>
        <hashTree>
          <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion"
              testname="Assert Product Detail 200" enabled="true">
            <collectionProp name="Asserion.test_strings">
              <stringProp name="49586">200</stringProp>
            </collectionProp>
            <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
            <boolProp name="Assertion.assume_success">false</boolProp>
            <intProp name="Assertion.test_type">8</intProp>
          </ResponseAssertion>
          <hashTree/>
        </hashTree>

        <!-- ════ STEP 4: TRANSACTIONAL — POST /api/cart ══════════════
             FR-07: Shopping Cart
             Yêu cầu Authorization header với JWT token
             Body: id, name, price, quantity
             ═══════════════════════════════════════════════════════════ -->
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy"
            testname="4. POST /api/cart (Transactional)" enabled="true">
          <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
            <collectionProp name="Arguments.arguments">
              <elementProp name="" elementType="HTTPArgument">
                <boolProp name="HTTPArgument.always_encode">false</boolProp>
                <stringProp name="Argument.value">{{
  "id": ${{extracted_product_id}},
  "name": "Test Product ${{extracted_product_id}}",
  "price": 100000,
  "quantity": ${{csv_quantity}}
}}</stringProp>
                <stringProp name="Argument.metadata">=</stringProp>
              </elementProp>
            </collectionProp>
          </elementProp>
          <stringProp name="HTTPSampler.path">/api/cart</stringProp>
          <stringProp name="HTTPSampler.method">POST</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
        </HTTPSamplerProxy>
        <hashTree>
          <!-- Inject Bearer token (chỉ áp dụng cho request này) -->
          <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager"
              testname="Authorization Header (Cart)" enabled="true">
            <collectionProp name="HeaderManager.headers">
              <elementProp name="Authorization" elementType="Header">
                <stringProp name="Header.name">Authorization</stringProp>
                <stringProp name="Header.value">${{auth_header}}</stringProp>
              </elementProp>
            </collectionProp>
          </HeaderManager>
          <hashTree/>
          <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion"
              testname="Assert Cart 200/201" enabled="true">
            <collectionProp name="Asserion.test_strings">
              <stringProp name="49586">200</stringProp>
              <stringProp name="49587">201</stringProp>
            </collectionProp>
            <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
            <boolProp name="Assertion.assume_success">false</boolProp>
            <intProp name="Assertion.test_type">40</intProp>
          </ResponseAssertion>
          <hashTree/>
        </hashTree>

        <!-- ════ STEP 5: TRANSACTIONAL — POST /api/checkout ═════════
             FR-08: Checkout
             Yêu cầu Authorization header
             NOTE: Backend tự tính lại total_amount (FR-08), giá trị
             client gửi chỉ để request hợp lệ
             ═══════════════════════════════════════════════════════════ -->
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy"
            testname="5. POST /api/checkout (Transactional)" enabled="true">
          <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
            <collectionProp name="Arguments.arguments">
              <elementProp name="" elementType="HTTPArgument">
                <boolProp name="HTTPArgument.always_encode">false</boolProp>
                <stringProp name="Argument.value">{{
  "total_amount": ${{csv_total}},
  "shipping_address": "123 Le Loi, Q1, TP.HCM"
}}</stringProp>
                <stringProp name="Argument.metadata">=</stringProp>
              </elementProp>
            </collectionProp>
          </elementProp>
          <stringProp name="HTTPSampler.path">/api/checkout</stringProp>
          <stringProp name="HTTPSampler.method">POST</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
        </HTTPSamplerProxy>
        <hashTree>
          <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager"
              testname="Authorization Header (Checkout)" enabled="true">
            <collectionProp name="HeaderManager.headers">
              <elementProp name="Authorization" elementType="Header">
                <stringProp name="Header.name">Authorization</stringProp>
                <stringProp name="Header.value">${{auth_header}}</stringProp>
              </elementProp>
            </collectionProp>
          </HeaderManager>
          <hashTree/>
          <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion"
              testname="Assert Checkout 200/201" enabled="true">
            <collectionProp name="Asserion.test_strings">
              <stringProp name="49586">200</stringProp>
              <stringProp name="49587">201</stringProp>
            </collectionProp>
            <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
            <boolProp name="Assertion.assume_success">false</boolProp>
            <intProp name="Assertion.test_type">40</intProp>
          </ResponseAssertion>
          <hashTree/>
        </hashTree>

        <!-- ─── Listener ─────────────────────────────────────────────── -->
{listener_xml}
        <hashTree/>

      </hashTree>
      <!-- end ThreadGroup hashTree -->

    </hashTree>
    <!-- end TestPlan hashTree -->

  </hashTree>
</jmeterTestPlan>
"""
    return jmx


if __name__ == "__main__":
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
    default_out_dir = str(ROOT_DIR / "test-plans")
    default_users_csv = str(ROOT_DIR / "data" / "users.csv")
    default_products_csv = str(ROOT_DIR / "data" / "products.csv")

    parser = argparse.ArgumentParser(
        description="Generate JMeter .jmx test plan for HW05 Browse-to-Buy workflow"
    )
    parser.add_argument("--scenario",   required=True, choices=["load", "stress", "spike", "soak"])
    parser.add_argument("--student-id", required=True, help="Student ID (e.g., 22127001)")
    parser.add_argument("--date",       default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--base-url",   default=BASE_URL)
    parser.add_argument("--out-dir",    default=default_out_dir)
    # Override defaults
    parser.add_argument("--threads",    type=int, default=None)
    parser.add_argument("--ramp-up",    type=int, default=None)
    parser.add_argument("--duration",   type=int, default=None)
    parser.add_argument("--think-min",  type=int, default=None)
    parser.add_argument("--think-max",  type=int, default=None)
    parser.add_argument("--users-csv",  default=default_users_csv)
    parser.add_argument("--products-csv", default=default_products_csv)
    args = parser.parse_args()

    defaults = SCENARIO_DEFAULTS[args.scenario]
    threads   = args.threads   or defaults["threads"]
    ramp_up   = args.ramp_up   or defaults["ramp_up"]
    duration  = args.duration  or defaults["duration"]
    think_min = args.think_min or defaults["think_min"]
    think_max = args.think_max or defaults["think_max"]
    listener  = defaults["listener"]

    plan_name = f"{args.student_id}_{args.scenario.capitalize()}_{args.date}"
    out_path  = os.path.join(args.out_dir, f"{plan_name}.jmx")
    os.makedirs(args.out_dir, exist_ok=True)

    jmx_content = build_jmx(
        scenario     = args.scenario,
        student_id   = args.student_id,
        date         = args.date,
        base_url     = args.base_url,
        threads      = threads,
        ramp_up      = ramp_up,
        duration     = duration,
        think_min    = think_min,
        think_max    = think_max,
        listener     = listener,
        users_csv    = args.users_csv,
        products_csv = args.products_csv,
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(jmx_content)

    print(f"\n✅ Test plan generated → {out_path}")
    print(f"\n   Scenario  : {args.scenario.upper()}")
    print(f"   Plan name : {plan_name}")
    print(f"   Threads   : {threads}")
    print(f"   Ramp-up   : {ramp_up}s")
    print(f"   Duration  : {duration}s ({duration//60} min)")
    print(f"   Think-time: {think_min}-{think_max} ms")
    print(f"   Listener  : {listener}")
    print(f"   Users CSV : {args.users_csv}")
    print(f"   Prods CSV : {args.products_csv}")
    print(f"\n   ⚠  Human Review checklist:")
    print(f"   □ Xác nhận BASE_URL đúng: {args.base_url}")
    print(f"   □ Kiểm tra JSON extractor path: $.token (login) và $[0].id (products)")
    print(f"   □ Xác nhận cart body field names: id, name, price, quantity")
    print(f"   □ Xác nhận checkout body fields: total_amount, shipping_address")
    print(f"   □ Với Spike: cài Stepping Thread Group plugin nếu cần pattern 10→500→10")
    print(f"   □ CSV paths phải là absolute path hoặc relative từ thư mục JMeter chạy\n")

