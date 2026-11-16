# HW05 – Performance Testing: Implementation Plan

> **Goal:** Hoàn thành bài tập Performance Testing cho EShop SUT — bao gồm Agent Skill (ưu tiên), 3 kịch bản test (Load/Stress/Spike) trên workflow Browse-to-Buy, AI analysis, và CI proposal.

> **Architecture:** Agent Skill được xây dựng trước để có thể tái sử dụng ngay khi chạy test. Workflow E2E duy nhất "Browse-to-Buy" (Login → Product List → Product Detail → Add to Cart → Checkout) được dùng cho cả 3 kịch bản. Toàn bộ quá trình dùng AI-first, có human review, ghi AI Audit Report.

> **Tech Stack:** JMeter, Python (data gen), AI tool (Claude/ChatGPT), Task Manager, Git, GitHub Issues, YouTube, Markdown/PDF

---

## Workflow được chọn: "Browse-to-Buy"

```
Step 1: POST /auth/login            → Auth-heavy (FR-02)
Step 2: GET  /products?page=1       → Read-heavy (FR-05)
Step 3: GET  /products/{id}         → Read-heavy (FR-06)
Step 4: POST /cart/items            → Transactional (FR-07)
Step 5: POST /orders/checkout       → Transactional (FR-08)
```

---

## 📁 Cấu trúc thư mục mục tiêu

```
hw05/
├── PLAN.md                          ← file này
├── README.md                        ← self-assessment table + test summary
├── report/
│   ├── HW05_Report.md
│   └── HW05_Report.pdf
├── skills/
│   └── hw05-perf-testing/
│       ├── SKILL.md                 ← Agent Skill definition
│       └── scripts/
│           ├── generate_csv.py
│           ├── analyze_jtl.py
│           └── run_perf_test.sh
├── test-plans/
│   ├── {StudentID}_Load_{DATE}.jmx
│   ├── {StudentID}_Stress_{DATE}.jmx
│   └── {StudentID}_Spike_{DATE}.jmx
├── data/
│   ├── users.csv
│   └── products.csv
├── results/
│   ├── load/
│   │   ├── {StudentID}_Load_{DATE}.jtl
│   │   └── html-report/
│   ├── stress/
│   │   ├── {StudentID}_Stress_{DATE}.jtl
│   │   └── html-report/
│   └── spike/
│       ├── {StudentID}_Spike_{DATE}.jtl
│       └── html-report/
├── screenshots/
│   ├── hardware_spec.png
│   ├── load_monitor.png
│   ├── stress_monitor.png
│   └── spike_monitor.png
├── ai-audit/
│   ├── AI_Audit_Report.md
│   └── AI_Audit_Report.pdf
├── ai-critique/
│   ├── AI_Critique.md
│   └── AI_Critique.pdf
└── git-log.txt
```

---

## 🗓️ Thứ tự thực hiện (Agent Skill ưu tiên)

| Phase | Task | Ước lượng |
|-------|------|-----------|
| **Phase 0** | Setup môi trường & repo | 20 phút |
| **Phase 1** | ⭐ **Xây Agent Skill** | 60 phút |
| **Phase 2** | Sinh CSV data & cấu hình JMeter base | 30 phút |
| **Phase 3** | Load Test | 40 phút |
| **Phase 4** | Stress Test | 40 phút |
| **Phase 5** | Spike Test | 40 phút |
| **Phase 6** | Endurance / Soak Test | 20 phút chạy + ghi số |
| **Phase 7** | AI Analysis + Misinterpretation Hunt | 40 phút |
| **Phase 8** | CI Proposal + Flowchart | 20 phút |
| **Phase 9** | Viết báo cáo + AI Critique | 30 phút |
| **Phase 10** | Đóng gói & nộp bài | 20 phút |
| | **Tổng** | **~6 giờ thực hiện** |

---

---

## ✅ PHASE 0 — Setup môi trường & Git repo

### Task 0.1: Khởi tạo Git repo
```bash
cd hw05
git init
git add PLAN.md README.md
git commit -m "init: HW05 project structure and plan"
```

### Task 0.2: Clone & khám sát SUT
- Mở: https://github.com/ttbhanh/eshop-sut
- Đọc README để xác định:
  - [ ] Port backend API đang chạy (vd: `localhost:8000`)
  - [ ] Endpoint chính xác cho 5 bước trong workflow
  - [ ] Cấu trúc request body của login, add-to-cart, checkout
  - [ ] Cơ chế account lockout (sau bao nhiêu lần fail?)
- Ghi lại vào `report/HW05_Report.md` → section **"4. SUT Exploration"**

### Task 0.3: Chạy SUT local và xác nhận hoạt động
```bash
# Theo hướng dẫn trong repo eshop-sut
# Kiểm tra:
curl -X POST http://localhost:PORT/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Pass@123"}'
```
- [ ] Ghi lại chính xác base URL, port, và response schema
- [ ] Commit: `git commit -m "docs: document SUT endpoints and request schemas"`

---

---

## ⭐ PHASE 1 — Xây dựng Agent Skill (ƯU TIÊN)

> **Mục tiêu:** Tạo một Agent Skill hoàn chỉnh có thể tái sử dụng để: sinh test plan, chạy JMeter, phân tích .jtl log, và xuất báo cáo tự động.

### Task 1.1: Thiết kế cấu trúc SKILL.md

Tạo file `skills/hw05-perf-testing/SKILL.md` với nội dung:

```markdown
---
name: hw05-perf-testing
description: "Performance testing skill for EShop SUT — generates JMeter test plans, runs Load/Stress/Spike scenarios, analyzes .jtl logs, and produces structured reports."
---

# HW05 Performance Testing Skill

## Overview
Skill này tự động hóa quy trình performance testing cho EShop SUT theo workflow Browse-to-Buy.
Nó bao gồm: sinh CSV data, cấu hình JMeter, chạy test, và phân tích kết quả.

## Capabilities
1. generate_test_data   — sinh users.csv và products.csv
2. generate_jmx        — tạo file .jmx cho Load/Stress/Spike
3. run_scenario        — chạy JMeter và lưu .jtl + HTML report
4. analyze_jtl         — phân tích .jtl, tính p50/p90/p95/p99, error rate
5. hunt_misinterpret   — so sánh AI analysis với raw log numbers
6. full_pipeline       — chạy toàn bộ từ 1 → 5 cho 1 endpoint group

## Usage
Kích hoạt skill này khi cần:
- Chạy performance test trên 1 endpoint group mới
- Phân tích kết quả JMeter (.jtl file)
- Tìm misinterpretation trong AI analysis

## Inputs
- endpoint_group: "read-heavy" | "auth-heavy" | "transactional" | "e2e"
- scenario: "load" | "stress" | "spike" | "soak"
- student_id: string (vd: "22127001")
- base_url: string (vd: "http://localhost:8000")

## Outputs
- .jmx test plan file
- .jtl raw log
- HTML report folder
- analysis_report.md (p50/p90/p95/p99, error rate, throughput)
- misinterpretation_report.md
```

### Task 1.2: Viết script `generate_csv.py`

Tạo `skills/hw05-perf-testing/scripts/generate_csv.py`:

```python
#!/usr/bin/env python3
"""
Generate CSV data files for HW05 Performance Testing.
Usage: python generate_csv.py --users 100 --products 50
"""
import csv
import argparse
import random

def generate_users(count: int, output: str = "data/users.csv"):
    """Generate test users including some with wrong passwords for lockout testing."""
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["email", "password", "expect_fail"])
        writer.writeheader()
        for i in range(1, count + 1):
            # 10% wrong password để trigger lockout tự nhiên
            wrong = (i % 10 == 0)
            writer.writerow({
                "email": f"testuser{i:03d}@eshop.test",
                "password": "WrongPass!" if wrong else "Pass@123",
                "expect_fail": "true" if wrong else "false"
            })
    print(f"✅ Generated {count} users → {output}")

def generate_products(count: int, output: str = "data/products.csv"):
    """Generate product IDs for read and cart testing."""
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["product_id", "quantity", "coupon_code"])
        writer.writeheader()
        for i in range(1, count + 1):
            writer.writerow({
                "product_id": random.randint(1, 50),
                "quantity": random.randint(1, 3),
                "coupon_code": "SAVE10" if i % 5 == 0 else ""
            })
    print(f"✅ Generated {count} product rows → {output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--users", type=int, default=100)
    parser.add_argument("--products", type=int, default=100)
    args = parser.parse_args()
    
    import os
    os.makedirs("data", exist_ok=True)
    generate_users(args.users)
    generate_products(args.products)
```

Chạy kiểm tra:
```bash
python skills/hw05-perf-testing/scripts/generate_csv.py --users 100 --products 100
# Expected: data/users.csv và data/products.csv được tạo
```

### Task 1.3: Viết script `analyze_jtl.py`

Tạo `skills/hw05-perf-testing/scripts/analyze_jtl.py`:

```python
#!/usr/bin/env python3
"""
Analyze JMeter .jtl log files and produce structured summary.
Usage: python analyze_jtl.py --file results/load/StudentID_Load_DATE.jtl
"""
import csv
import argparse
import statistics
from pathlib import Path
from datetime import datetime

def analyze(jtl_path: str) -> dict:
    latencies = []
    errors = 0
    total = 0
    start_ts = None
    end_ts = None

    with open(jtl_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            elapsed = int(row.get("elapsed", 0))
            ts = int(row.get("timeStamp", 0))
            success = row.get("success", "true").lower() == "true"

            latencies.append(elapsed)
            if not success:
                errors += 1
            if start_ts is None or ts < start_ts:
                start_ts = ts
            if end_ts is None or ts > end_ts:
                end_ts = ts

    if not latencies:
        print("❌ No data found in JTL file.")
        return {}

    latencies_sorted = sorted(latencies)
    duration_s = (end_ts - start_ts) / 1000 if start_ts and end_ts else 1

    def percentile(data, pct):
        idx = int(len(data) * pct / 100) - 1
        return data[max(0, idx)]

    result = {
        "file": jtl_path,
        "total_requests": total,
        "error_count": errors,
        "error_rate_pct": round(errors / total * 100, 2),
        "throughput_rps": round(total / duration_s, 2),
        "p50_ms": percentile(latencies_sorted, 50),
        "p90_ms": percentile(latencies_sorted, 90),
        "p95_ms": percentile(latencies_sorted, 95),
        "p99_ms": percentile(latencies_sorted, 99),
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "avg_ms": round(statistics.mean(latencies), 1),
        "duration_s": round(duration_s, 1),
    }

    # Print report
    print(f"\n{'='*55}")
    print(f"📊 JTL Analysis: {Path(jtl_path).name}")
    print(f"{'='*55}")
    print(f"  Total Requests : {result['total_requests']}")
    print(f"  Error Rate     : {result['error_rate_pct']}%  ({result['error_count']} errors)")
    print(f"  Throughput     : {result['throughput_rps']} req/s")
    print(f"  Duration       : {result['duration_s']}s")
    print(f"  Latency (ms)   : min={result['min_ms']}  avg={result['avg_ms']}  max={result['max_ms']}")
    print(f"  Percentiles    : p50={result['p50_ms']}  p90={result['p90_ms']}  p95={result['p95_ms']}  p99={result['p99_ms']}")
    print(f"{'='*55}\n")

    # Save markdown report
    out_path = Path(jtl_path).with_suffix(".analysis.md")
    with open(out_path, "w") as f:
        f.write(f"# JTL Analysis — {Path(jtl_path).name}\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("| Metric | Value |\n|--------|-------|\n")
        for k, v in result.items():
            if k != "file":
                f.write(f"| {k} | {v} |\n")
    print(f"✅ Analysis saved → {out_path}")
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path to .jtl file")
    args = parser.parse_args()
    analyze(args.file)
```

### Task 1.4: Commit Agent Skill

```bash
git add skills/
git commit -m "feat(skill): add hw05-perf-testing Agent Skill with generate_csv and analyze_jtl scripts"
```

---

---

## ✅ PHASE 2 — Sinh CSV data & Cấu hình JMeter base

### Task 2.1: Sinh data files
```bash
mkdir -p data
python skills/hw05-perf-testing/scripts/generate_csv.py --users 150 --products 150
# Kiểm tra: cat data/users.csv | head -5
```

### Task 2.2: Cài đặt JMeter và xác nhận hoạt động
- Tải JMeter từ: https://jmeter.apache.org/download_jmeter.cgi
- Chạy: `jmeter -v` → xác nhận phiên bản
- Mở JMeter GUI để bắt đầu tạo test plan

### Task 2.3: Tạo Thread Group template base với AI (step-by-step)

**Prompt AI (không dùng generic prompt):**

```
Prompt 1: "Tôi đang tạo JMeter test plan cho EShop SUT. 
Bước 1: hãy giúp tôi tạo Thread Group cho Load test với 50 VUs, 
ramp-up 60s, duration 5 phút. Giải thích ý nghĩa từng thông số."

Prompt 2: "Bây giờ hãy tạo HTTP Request Sampler cho bước Login 
(POST /auth/login) với CSV Dataset Config đọc từ users.csv. 
Chỉ bước này thôi."

Prompt 3: "Thêm HTTP Request Sampler cho GET /products?page=1&limit=20. 
Thêm JSON Extractor để lấy product_id đầu tiên từ response."

Prompt 4: "Thêm GET /products/${product_id} dùng biến vừa extract."

Prompt 5: "Thêm POST /cart/items và POST /orders/checkout với body 
từ CSV. Thêm Response Assertion cho mỗi request (status 200/201)."
```

- Ghi lại mỗi prompt và output của AI vào `ai-audit/AI_Audit_Report.md`

### Task 2.4: Commit data và base template
```bash
git add data/
git commit -m "data: generate users.csv and products.csv for Browse-to-Buy workflow"
```

---

---

## ✅ PHASE 3 — Load Test

**Tham số:** 50 VUs | Ramp-up 60s | Duration 5 phút | Report: Summary Report

### Task 3.1: Tạo Load test plan với AI

**Prompt AI:**
```
"Dựa trên base template, hãy điều chỉnh thành Load test plan.
Mục tiêu: 50 virtual users, ramp-up 60 giây, chạy 5 phút.
Think-time: Uniform Random Timer 1000-3000ms giữa các request.
Thêm: Summary Report listener.
Giải thích tại sao các tham số này phù hợp với Load test."
```

### Task 3.2: Human Review — sửa những gì AI sai
Kiểm tra và ghi lại:
- [ ] Think-time có hợp lý không? (phải random, không phải fixed 0)
- [ ] Thread count đúng chưa? (50, không phải 1 hay 500)
- [ ] Có assertion cho mỗi HTTP request không?
- [ ] CSV config đúng file path chưa?
- [ ] Có xử lý token từ Login response không (Bearer token)?
- Ghi vào report: **"AI sai ở chỗ X, lý do Y, tôi sửa thành Z"**

### Task 3.3: Đặt tên và lưu
- File: `test-plans/{StudentID}_Load_{YYYYMMDD}.jmx`

### Task 3.4: Chạy Load test

```bash
# Non-GUI mode (khuyến nghị)
jmeter -n \
  -t test-plans/{StudentID}_Load_{DATE}.jmx \
  -l results/load/{StudentID}_Load_{DATE}.jtl \
  -e -o results/load/html-report/
```

**Trong khi chạy:**
- [ ] Mở Task Manager → theo dõi CPU, RAM của backend process
- [ ] **Chụp màn hình: JMeter đang chạy + Task Manager cùng frame** → `screenshots/load_monitor.png`

### Task 3.5: Ghi nhận kết quả sơ bộ

```bash
python skills/hw05-perf-testing/scripts/analyze_jtl.py \
  --file results/load/{StudentID}_Load_{DATE}.jtl
```

- Ghi lại: total requests, error rate, p95, throughput

### Task 3.6: Commit
```bash
git add test-plans/ results/load/ screenshots/load_monitor.png
git commit -m "test(load): run Load scenario — 50VU 60s ramp 5min, capture .jtl and HTML report"
```

---

---

## ✅ PHASE 4 — Stress Test

**Tham số:** 200 VUs | Ramp-up 120s | Duration 10 phút | Report: Aggregate Report

### Task 4.1: Tạo Stress test plan với AI

**Prompt AI:**
```
"Từ Load test plan, hãy tạo Stress test plan.
Tăng lên 200 virtual users, ramp-up 120 giây, chạy 10 phút.
Think-time giảm xuống 500-1500ms (stress hơn).
Đổi listener sang Aggregate Report.
Account lockout xảy ra khi login fail 3 lần liên tiếp — 
hãy giúp tôi thêm logic để detect điều này và dừng lockout scenario."
```

### Task 4.2: Human Review
- [ ] AI có xử lý đúng lockout không? (thường AI bỏ qua)
- [ ] Ramp-up 120s cho 200VU có thực tế không?
- [ ] Có cần Connection timeout / Response timeout không?
- Ghi lại vào report section **"Stress Test — AI Review"**

### Task 4.3: Xử lý Account Lockout
Trước khi chạy Stress test:
- [ ] Chuẩn bị script reset lockout (hoặc reset thủ công qua admin panel)
- Ghi lại bước reset vào report

### Task 4.4: Chạy Stress test
```bash
jmeter -n \
  -t test-plans/{StudentID}_Stress_{DATE}.jmx \
  -l results/stress/{StudentID}_Stress_{DATE}.jtl \
  -e -o results/stress/html-report/
```

- [ ] Chụp: `screenshots/stress_monitor.png` (cùng frame với Task Manager)
- [ ] Nếu lockout xảy ra: chụp màn hình lockout → reset → ghi bước reset

### Task 4.5: Phân tích nhanh
```bash
python skills/hw05-perf-testing/scripts/analyze_jtl.py \
  --file results/stress/{StudentID}_Stress_{DATE}.jtl
```

### Task 4.6: Commit
```bash
git add test-plans/ results/stress/ screenshots/stress_monitor.png
git commit -m "test(stress): run Stress scenario — 200VU 120s ramp 10min, document lockout reset"
```

---

---

## ✅ PHASE 5 — Spike Test

**Tham số:** 10 → 500 → 10 VUs | Spike 10s | Report: View Results Tree

### Task 5.1: Tạo Spike test plan với AI

**Prompt AI:**
```
"Tạo Spike test plan từ template.
Pattern: 10 VU baseline → tăng đột ngột lên 500 VU trong 10 giây → 
duy trì 2 phút → giảm về 10 VU.
Think-time: 500ms (nhanh để tạo spike thực sự).
Listener: View Results Tree (giới hạn 500 results để tránh OOM).
Giải thích tại sao spike test khác với stress test."
```

### Task 5.2: Human Review
- [ ] 500 VU có quá lớn với hardware của mình không?
- [ ] Think-time 500ms có tạo spike thực sự không?
- [ ] View Results Tree có giới hạn số records không (tránh memory leak JMeter)?

### Task 5.3: Chạy Spike test
```bash
jmeter -n \
  -t test-plans/{StudentID}_Spike_{DATE}.jmx \
  -l results/spike/{StudentID}_Spike_{DATE}.jtl \
  -e -o results/spike/html-report/
```

- [ ] Chụp: `screenshots/spike_monitor.png`

### Task 5.4: Commit
```bash
git add test-plans/ results/spike/ screenshots/spike_monitor.png
git commit -m "test(spike): run Spike scenario — 10→500→10 VU pattern, capture recovery behaviour"
```

---

---

## ✅ PHASE 6 — Endurance / Soak Test

**Tham số:** 30-50 VUs | Duration 10-15 phút | Mục tiêu: tìm ngưỡng ổn định

### Task 6.1: Chạy Soak test ngắn
```bash
# Dùng lại Load test plan, tăng duration lên 15 phút
jmeter -n \
  -t test-plans/{StudentID}_Load_{DATE}.jmx \
  -Jduration=900 \
  -l results/soak/soak_15min.jtl
```

### Task 6.2: Ghi nhận ngưỡng (con số cụ thể)
Phân tích và ghi vào report:
```
Endurance Threshold:
- Maximum stable RPS: _____ req/s
- Memory ceiling: _____ MB (observed in Task Manager)
- Error rate stays below 1% at: _____ VUs
- p95 latency stable at: _____ ms
```

### Task 6.3: Chụp hardware spec
- Mở `dxdiag` (Windows) hoặc `screenfetch` (Linux/Mac)
- Chụp: `screenshots/hardware_spec.png`
- Tạo bảng spec trong report:

```markdown
| Component | Spec |
|-----------|------|
| CPU | Intel Core i7-... |
| RAM | 16 GB DDR4 |
| OS | Windows 11 |
| Hostname | LAPTOP-XXXX |  ← phải khớp HW cũ
| JMeter | 5.x |
| Java | 11 |
```

### Task 6.4: Commit
```bash
git add results/soak/ screenshots/hardware_spec.png
git commit -m "test(soak): 15-min endurance test — determined max stable RPS and memory ceiling"
```

---

---

## ✅ PHASE 7 — AI Analysis & Misinterpretation Hunt

### Task 7.1: Prompt AI phân tích .jtl logs (step-by-step)

**Prompt AI:**
```
Prompt 1: "Tôi có file .jtl với nội dung sau (paste 50 dòng đầu).
Hãy giải thích cấu trúc từng cột: timeStamp, elapsed, label, 
responseCode, success, bytes, Latency, Connect."

Prompt 2: "Dựa trên dữ liệu này, hãy tính p50, p90, p95, p99 latency 
và error rate cho từng endpoint. Đề xuất performance threshold."

Prompt 3: "Dựa trên kết quả Stress test (paste summary), 
hãy đề xuất các optimizations để cải thiện performance."
```

### Task 7.2: So sánh AI output với `analyze_jtl.py`

Dùng script để lấy con số thực:
```bash
python skills/hw05-perf-testing/scripts/analyze_jtl.py \
  --file results/load/{StudentID}_Load_{DATE}.jtl

python skills/hw05-perf-testing/scripts/analyze_jtl.py \
  --file results/stress/{StudentID}_Stress_{DATE}.jtl

python skills/hw05-perf-testing/scripts/analyze_jtl.py \
  --file results/spike/{StudentID}_Spike_{DATE}.jtl
```

### Task 7.3: Viết Misinterpretation Report

Tạo bảng trong report:
```markdown
| # | AI nói gì | Giá trị thực từ .jtl | Lý do AI sai |
|---|-----------|----------------------|--------------|
| 1 | p95 = 250ms | p95 = 487ms | AI dùng avg thay vì percentile |
| 2 | Error rate = 2% | Error rate = 8.3% | AI chỉ đọc success count, bỏ qua timeout |
| 3 | ... | ... | ... |
```

### Task 7.4: Phân loại AI recommendations

```markdown
| Optimization AI đề xuất | Phân loại | Lý do |
|--------------------------|-----------|-------|
| Thêm DB index trên product_id | ✅ Feasible | Index thực sự cải thiện query |
| Enable SQLite WAL mode | ✅ Feasible | WAL giảm write lock contention |
| Dùng Redis cache cho product listing | ✅ Feasible | Cache giảm DB load hiệu quả |
| Upgrade lên PostgreSQL cluster 32-node | ❌ Hallucinated | Overkill cho SUT nhỏ, không khả thi |
| Rewrite bằng Rust | ❌ Hallucinated | Không liên quan đến bottleneck |
```

### Task 7.5: Commit
```bash
git add ai-audit/ report/
git commit -m "docs(analysis): AI analysis of JTL logs + misinterpretation hunt with correct values"
```

---

---

## ✅ PHASE 8 — Continuous Performance Testing Proposal

### Task 8.1: Viết CI proposal với flowchart

Thêm vào report section **"Task 3 — Continuous Performance Testing"**:

```markdown
## Continuous Performance Testing Pipeline

### Flowchart

flowchart TD:
  A[Developer pushes commit] --> B{Changed files affect API?}
  B -- No --> C[Skip perf test]
  B -- Yes --> D[Trigger perf test pipeline]
  D --> E[Run Load scenario — 50VU 5min]
  E --> F{p95 regression > 20%?}
  F -- No --> G[✅ Pass — merge allowed]
  F -- Yes --> H[❌ Flag regression — block merge]
  H --> I[Notify dev + link to report]

### Trade-offs
| Yếu tố | Trade-off |
|--------|-----------|
| Cost | Chạy mỗi commit tốn CI minutes; giảm bằng cách chỉ trigger khi thay đổi file API/DB |
| False alarms | Môi trường CI không ổn định → p95 dao động → dùng rolling average 3 runs |
| Threshold | 20% regression quá chặt → nhiều false positive; 50% quá lỏng → bỏ sót issue |
| Coverage | Load test 5 phút đủ detect regression; Stress/Spike chỉ chạy weekly |
```

### Task 8.2: Commit
```bash
git commit -am "docs(proposal): continuous performance testing pipeline with flowchart and trade-offs"
```

---

---

## ✅ PHASE 9 — Viết báo cáo chính & AI Critique

### Task 9.1: Hoàn thiện `report/HW05_Report.md`

Cấu trúc report:
```
1. Introduction
2. SUT Overview & Endpoint Mapping
3. E2E Workflow Design (Browse-to-Buy)
4. Test Data (CSV structure)
5. Task 1 — Test Plans & Execution
   5.1 Load Test
   5.2 Stress Test
   5.3 Spike Test
   5.4 Endurance Threshold
6. Task 2 — AI Analysis & Misinterpretation Hunt
7. Task 3 — Continuous Testing Proposal
8. Bug Report (nếu có)
9. Conclusion
Appendix A: AI Audit Report
Appendix B: AI Critique
```

### Task 9.2: Viết AI Critique (200–300 từ)

Trả lời 3 câu hỏi:
1. AI sai/thiên lệch/thiếu ở đâu?
2. Tại sao AI không bắt được vấn đề đó?
3. Nguyên tắc gì học được về cộng tác với AI?

### Task 9.3: Xuất PDF
```bash
# Dùng Pandoc
pandoc report/HW05_Report.md -o report/HW05_Report.pdf
pandoc ai-audit/AI_Audit_Report.md -o ai-audit/AI_Audit_Report.pdf
pandoc ai-critique/AI_Critique.md -o ai-critique/AI_Critique.pdf
```

### Task 9.4: Lưu Git log
```bash
git log --oneline --graph --all > git-log.txt
git commit -am "docs: finalize report, AI critique, and git log"
```

---

---

## ✅ PHASE 10 — Quay video Demo & Đóng gói nộp bài

### Task 10.1: Quay demo video (≥ 6 phút, tiếng Việt)

Nội dung từng clip (có thể tách nhỏ):
- **Clip 1 (Load):** Chạy Load test → thấy JMeter + Task Manager cùng frame → đọc kết quả
- **Clip 2 (Stress):** Chạy Stress test → trigger lockout → reset → tiếp tục
- **Clip 3 (Spike):** Chạy Spike test → thấy spike pattern + recovery
- **Clip 4 (Agent Skill):** Demo skill analyze_jtl.py chạy end-to-end

Upload YouTube (unlisted) → lấy link → thêm vào README.md

### Task 10.2: Cập nhật README.md

```markdown
# HW05 – Performance Testing

## Self-Assessment Table
| # | Criteria | Max | Self-Assessed |
|---|----------|-----|---------------|
| 1 | Load testing | 30 | |
| 2 | Stress testing | 20 | |
| 3 | Spike testing | 20 | |
| 4 | AI analysis + misinterpretation hunt | 10 | |
| 5 | Continuous Performance Testing proposal | 10 | |
| 6 | Agent Skills | 10 | |

## Test Summary Report
- Scenarios run: Load, Stress, Spike, Soak
- Endpoint groups covered: Auth-heavy, Read-heavy, Transactional
- Endurance threshold: max ___ RPS, memory ceiling ___ MB
- Bugs / performance issues found: ___
- Demo video: [YouTube Link](https://youtube.com/...)
```

### Task 10.3: Đóng gói .zip
```bash
$STUDENT_ID = "XXXXXXXX"
$GRADE = "090"  # điền sau khi self-assess
$ZIP = "${STUDENT_ID}_HW05_AI_Performance_${GRADE}.zip"

Compress-Archive -Path @(
  "README.md",
  "report/",
  "test-plans/",
  "data/",
  "results/",
  "screenshots/",
  "ai-audit/",
  "ai-critique/",
  "git-log.txt",
  "skills/"
) -DestinationPath $ZIP
```

### Task 10.4: Final commit
```bash
git add .
git commit -m "release: HW05 final submission — all deliverables complete"
git push origin main
```

---

## 📋 Final Checklist trước khi nộp

```
✅ Nộp bài
□ 3 file .jmx đúng tên {StudentID}_{Type}_{DATE}
□ 3 file .jtl đầy đủ (không chỉ summary)
□ 3 thư mục HTML report
□ screenshots/hardware_spec.png (hostname khớp HW cũ)
□ screenshots/load_monitor.png, stress_monitor.png, spike_monitor.png (cùng frame)
□ YouTube video unlisted (≥6 phút, narration tiếng Việt)
□ AI_Audit_Report.md + .pdf
□ AI_Critique.md + .pdf (200-300 từ)
□ HW05_Report.md + .pdf
□ git-log.txt
□ README.md với self-assessment table + demo link
□ GitHub repo public
□ skills/ folder với SKILL.md + scripts
□ File .zip đúng tên format
□ Nộp lên Moodle trước deadline
```

---

*Plan created: 2026-11-16 | Workflow: Browse-to-Buy | Tool: JMeter + AI-first*

