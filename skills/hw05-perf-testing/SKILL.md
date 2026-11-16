---
name: hw05-perf-testing
description: >
  Performance testing skill for EShop SUT (http://localhost:3000).
  Generates JMeter .jmx test plans, produces CSV test data, runs Load/Stress/Spike
  scenarios via JMeter CLI, analyzes .jtl logs (p50/p90/p95/p99, error rate,
  throughput), hunts AI misinterpretations, and writes structured Markdown reports.
  Reusable on any Browse-to-Buy endpoint group.
risk: low
source: student
date_added: "2026-11-16"
---

# HW05 Performance Testing Skill — EShop SUT

## Overview

Skill này tự động hóa toàn bộ quy trình performance testing cho EShop SUT theo
workflow **Browse-to-Buy**, bao gồm 5 bước API:

| Bước | Method | Endpoint              | Nhóm          | FR     |
|------|--------|-----------------------|---------------|--------|
| 1    | POST   | /api/login            | Auth-heavy    | FR-02  |
| 2    | GET    | /api/products         | Read-heavy    | FR-05  |
| 3    | GET    | /api/products/:id     | Read-heavy    | FR-06  |
| 4    | POST   | /api/cart             | Transactional | FR-07  |
| 5    | POST   | /api/checkout         | Transactional | FR-08  |

**Base URL:** `http://localhost:3000`  
**Auth mechanism:** JWT Bearer Token (lấy từ response login, inject vào header)  
**Account lockout:** Sau 3 lần login sai liên tiếp → khóa 30 giây (FR-02)

---

## Capabilities

### 1. `generate_test_data`
Sinh file CSV cho test data:
- `data/users.csv`     — email, password, expect_fail (10% wrong password)
- `data/products.csv`  — product_id, quantity, coupon_code

**Script:** `scripts/generate_csv.py`  
**Usage:** `python scripts/generate_csv.py --users 150 --products 150`

### 2. `generate_jmx`
Tạo file JMeter `.jmx` cho 1 trong 3 scenario (Load/Stress/Spike).  
**Script:** `scripts/generate_jmx.py`  
**Usage:** `python scripts/generate_jmx.py --scenario load --student-id XXXXXXXX --date 20261116`

Tham số mặc định:
| Scenario | Threads | Ramp-up | Duration | Think-time    | Listener          |
|----------|---------|---------|----------|---------------|-------------------|
| load     | 50      | 60s     | 300s     | 1000–3000 ms  | Summary Report    |
| stress   | 200     | 120s    | 600s     | 500–1500 ms   | Aggregate Report  |
| spike    | 500     | 10s     | 120s     | 500 ms        | View Results Tree |

### 3. `run_scenario`
Chạy JMeter non-GUI, lưu `.jtl` và sinh HTML report.  
**Script:** `scripts/run_scenario.ps1`  
**Usage:** `.\scripts\run_scenario.ps1 -Scenario load -StudentID XXXXXXXX -Date 20261116`

### 4. `analyze_jtl`
Đọc file `.jtl`, tính p50/p90/p95/p99, error rate, throughput, min/max/avg.  
Xuất bảng Markdown sang `results/<scenario>/<name>.analysis.md`.  
**Script:** `scripts/analyze_jtl.py`  
**Usage:** `python scripts/analyze_jtl.py --file results/load/XXXXXXXX_Load_20261116.jtl`

### 5. `hunt_misinterpretations`
So sánh AI analysis text với số liệu thực từ `.jtl`, tạo bảng misinterpretation.  
**Script:** `scripts/hunt_misinterpretations.py`

### 6. `full_pipeline`
Chạy tuần tự: generate_test_data → generate_jmx → run_scenario → analyze_jtl  
cho tất cả 3 scenarios trong một lần.  
**Usage:** `python scripts/full_pipeline.py --student-id XXXXXXXX --base-url http://localhost:3000`

---

## Inputs

| Tham số      | Mô tả                               | Mặc định                   |
|--------------|-------------------------------------|----------------------------|
| student_id   | Mã số sinh viên                     | (bắt buộc)                 |
| base_url     | Backend API base URL                | http://localhost:3000      |
| scenario     | load / stress / spike / soak        | load                       |
| date         | YYYYMMDD                            | ngày hiện tại              |
| users_count  | Số dòng trong users.csv             | 150                        |
| products_count | Số dòng trong products.csv        | 150                        |

---

## Outputs

| File                                       | Mô tả                              |
|--------------------------------------------|------------------------------------|
| `data/users.csv`                           | Test users (có 10% wrong password) |
| `data/products.csv`                        | Product IDs và quantities          |
| `test-plans/{id}_{type}_{date}.jmx`        | JMeter test plan                   |
| `results/{type}/{id}_{type}_{date}.jtl`    | Raw JMeter log                     |
| `results/{type}/html-report/`              | JMeter HTML dashboard              |
| `results/{type}/{name}.analysis.md`        | Bảng p50/p90/p95/p99 + metrics     |
| `ai-audit/AI_Audit_Report.md`              | AI audit log tự động               |

---

## Workflow Diagram

```
[generate_csv.py] ──► data/users.csv
                  ──► data/products.csv
                           │
                           ▼
[generate_jmx.py] ──► test-plans/{id}_{type}_{date}.jmx
                           │
                           ▼
[run_scenario.ps1] ──► results/{type}/{id}_{type}_{date}.jtl
                   ──► results/{type}/html-report/
                           │
                           ▼
[analyze_jtl.py]  ──► results/{type}/{name}.analysis.md
                           │
                           ▼
[hunt_misinterpretations.py] ──► report/misinterpretation_table.md
```

---

## Giải thích tại sao workflow Browse-to-Buy bao phủ 3 nhóm

**Auth-heavy (Bước 1 — POST /api/login):**  
Login là điểm auth duy nhất và quan trọng nhất. Với 10% wrong-password trong CSV,
Stress/Spike test tự nhiên trigger account lockout (FR-02: sau 3 lần sai → khóa 30s)
mà không cần xử lý thủ công. Token JWT từ login được extract và inject vào tất cả
các request tiếp theo.

**Read-heavy (Bước 2–3 — GET /api/products và GET /api/products/:id):**  
Đây là hai endpoint GET không có side-effect, chịu tải lớn nhất trong thực tế
(nhiều người xem sản phẩm hơn mua hàng). Tỷ lệ 2:1 so với transactional request
mô phỏng đúng traffic thực tế. Product ID được extract từ response bước 2 và
truyền vào bước 3 (dynamic path parameterization).

**Transactional (Bước 4–5 — POST /api/cart và POST /api/checkout):**  
Hai POST endpoint có write operation vào DB. Checkout xử lý state machine (FR-10).
Đây là nơi để quan sát DB lock contention và throughput dưới concurrent load.

---

## Lưu ý quan trọng

> **Account Lockout Reset:** Khi chạy Stress/Stress, nếu một user bị lockout,
> JMeter sẽ nhận response lỗi và tiếp tục với user CSV tiếp theo (nhờ CSV Dataset
> Config `Sharing mode = Current thread group`). Reset thủ công qua admin panel
> hoặc restart backend sau mỗi scenario nếu cần.

> **Token Lifetime:** JWT token của EShop không có expiry ngắn trong demo mode,
> nhưng mỗi VU nên login một lần ở đầu và reuse token trong suốt duration.

> **SQLite Concurrency:** Backend dùng SQLite — dễ gặp `SQLITE_BUSY` error dưới
> high concurrency. Đây là điểm quan sát thú vị trong Stress/Spike test.

