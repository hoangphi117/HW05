# AI Audit Report — HW05 Performance Testing

**Declaration:**
I use AI tools for the following tasks:

- Designing the project execution plan and structuring phases.
- Designing and implementing the reusable Performance Testing Agent Skill (`hw05-perf-testing`) for EShop SUT.

---

## Log Entry 1: Đề xuất Kế hoạch Thực hiện (Ưu tiên Agent Skill)

- **Name of the AI tool:** Claude Sonnet 4.6
- **Date and time:** 2026-11-16 09:16:36
- **Your prompt:**

```text
Hãy lên kế hoạch để thực hiện bài tập này, đưa task Agent skill lên trước. Viết vào 1 file .md
```

- **The AI output:**

```text
Kế hoạch đã được lưu vào PLAN.md.

---

## 🗺️ Tóm tắt kế hoạch

10 Phases, ưu tiên Agent Skill trước:

| Phase | Nội dung | Thời gian |
|-------|----------|-----------|
| Phase 0 | Setup Git + khám sát SUT endpoints | 20 phút |
| ⭐ Phase 1 | Xây Agent Skill (SKILL.md + generate_csv.py + analyze_jtl.py) | 60 phút |
| Phase 2 | Sinh CSV data + cấu hình JMeter base template với AI step-by-step | 30 phút |
| Phase 3 | Load Test (50 VU / 5 phút / Summary Report) | 40 phút |
| Phase 4 | Stress Test (200 VU / 10 phút / Aggregate Report) | 40 phút |
| Phase 5 | Spike Test (10→500→10 VU / View Results Tree) | 40 phút |
| Phase 6 | Soak Test 15 phút → xác định endurance threshold (con số cụ thể) | 20 phút |
| Phase 7 | AI Analysis → so sánh với script → viết Misinterpretation table | 40 phút |
| Phase 8 | CI/CD Proposal + flowchart + trade-offs | 20 phút |
| Phase 9 | Viết báo cáo đầy đủ + AI Critique + xuất PDF | 30 phút |
| Phase 10 | Quay video demo + đóng gói .zip + nộp Moodle | 20 phút |

Điểm nhấn trong kế hoạch:
- 🎯 Agent Skill có 2 scripts thực tế sẵn code: generate_csv.py tự động tạo 10% wrong-password để trigger lockout tự nhiên; analyze_jtl.py tính đúng p50/p90/p95/p99 để so với AI
- 📝 Mỗi AI prompt được viết từng bước riêng lẻ (không generic), sẵn sàng copy-paste
- 🗂️ Cấu trúc thư mục và tên file đúng format yêu cầu ngay từ đầu
- ✅ Final checklist đầy đủ 15 mục anti-AI-cheat
```

---

## Log Entry 2: Khởi tạo Cấu trúc Thư mục và Thực hiện Phase 1 (Xây dựng Agent Skill)

- **Name of the AI tool:** Claude Sonnet 4.6 (Thinking) via Antigravity
- **Date and time:** 2026-11-16 09:27:58 (UTC+7)
- **Your prompt:**

```text
đây là thư mục SUT local: "C:\Users\opmeo\OneDrive\Desktop\eshop-sut". Hãy khởi tạo giúp tôi cấu trúc  thư mục như plan rồi thực hiện luôn Phase 1.
```

- **The AI output:**

```text
✅ Phase 0 + Phase 1 hoàn tất! Dưới đây là tóm tắt những gì đã được tạo:

---

## 🎉 Kết quả Phase 0 & 1

### 📁 Cấu trúc thư mục — ✅ Xong
Toàn bộ 10 thư mục theo đúng PLAN.md đã được tạo.

### ⭐ Agent Skill — ✅ Xong (5 files)

| File | Chức năng |
|------|-----------|
| SKILL.md | Mô tả đầy đủ skill, endpoint mapping, lý do chọn workflow |
| generate_csv.py | Sinh 150 users (10% wrong-pwd) + 150 products |
| generate_jmx.py | Sinh JMX đầy đủ 5 bước Browse-to-Buy với JWT extraction |
| analyze_jtl.py | Tính p50/p75/p90/p95/p99 + per-label breakdown → Markdown |
| run_scenario.ps1 | Chạy JMeter non-GUI, kiểm tra SUT, auto-analyze sau khi xong |
| full_pipeline.py | Orchestrator: CSV → JMX → JMeter → Analysis một lệnh |

### 📊 Data & Test Plans — ✅ Sẵn sàng
- data/users.csv — 150 users, 15 dòng wrong-password phân bố đều
- data/products.csv — 150 rows với mixed coupons
- 3 JMX files đã sinh cho Load/Stress/Spike

### 🗂️ Git — ✅ 3 commits đúng convention
e236e58 data+plans: generate users.csv, products.csv and 3 JMX test plans
d150c04 feat(skill): Phase 1 complete — hw05-perf-testing Agent Skill
87ab3db init: HW05 project structure, plan, and gitignore

---

## ➡️ Bước tiếp theo (Phase 2)

Việc bạn cần làm ngay:
1. Thay XXXXXXXX trong tên file JMX bằng Student ID thật của bạn (rename + regenerate)
2. Cài JMeter nếu chưa có: https://jmeter.apache.org/download_jmeter.cgi
3. Mở JMeter GUI kiểm tra file XXXXXXXX_Load_20261116.jmx — verify JSON extractor paths và CSV paths
4. Chạy Phase 3 (Load Test): .\skills\hw05-perf-testing\scripts\run_scenario.ps1 -Scenario load -StudentID <ID> -Date 20261116
```


---

## Log Entry 3: Thực hiện Phase 2 — Sinh Data, Cấu hình và Xác thực JMeter Template

- **Name of the AI tool:** Gemini 3.8 Flash (Medium) via Antigravity
- **Date and time:** 2026-11-16 09:57:53 (UTC+7)
- **Your prompt:**

```text
Sử dụng skills đã tạo để thực hiện phase 2 trong plan.
```

- **The AI output:**

```text
✅ Phase 2 hoàn tất thành công!

1. Khám sát & Phát hiện quan trọng (Human Review):
   - SUT ban đầu chỉ có 2 tài khoản (admin, test). Đã nâng cấp `generate_csv.py` tự động seed 150 tài khoản virtual users vào SQLite `database.sqlite` để các request login hợp lệ.
   - Phát hiện lỗi cấu trúc XML JMeter: class `JSONPathExtractor` không thuộc bộ chuẩn JMeter 5.x -> đã chuyển sang chuẩn `JSONPostProcessor`.
   - Cấu trúc XML HashTree của JMeter yêu cầu mỗi phần tử con phải đi kèm một thẻ `<hashTree/>`.
   - Cấu hình CSV `shareMode` được điều chỉnh từ `shareMode.thread` sang `shareMode.all` để các thread phân bổ đều 150 user khác nhau thay vì tất cả cùng đọc user đầu tiên.

2. Sinh tập dữ liệu kiểm thử (Data Files):
   - `data/users.csv`: 150 virtual users (10% mật khẩu sai để kích hoạt lockout FR-02).
   - `data/products.csv`: 150 dòng tham số sản phẩm & mã giảm giá.
   - SUT SQLite Database: Đã đồng bộ 150 tài khoản người dùng tương ứng.

3. Sinh và chuẩn hóa các Test Plan (.jmx):
   - `test-plans/22127001_Load_20261116.jmx` (50 VU, 60s ramp-up, 5 min, Summary Report)
   - `test-plans/22127001_Stress_20261116.jmx` (200 VU, 120s ramp-up, 10 min, Aggregate Report)
   - `test-plans/22127001_Spike_20261116.jmx` (500 VU, 10s ramp-up, 2 min, View Results Tree)

4. Chạy thử nghiệm thực tế (Smoke Test) với JMeter 5.6.3:
   - Đã thực thi smoke test trực tiếp với SUT đang chạy tại `http://localhost:3000`.
   - Quy trình Browse-to-Buy hoạt động hoàn hảo: Login thành công -> trích xuất Bearer Token -> đọc danh sách sản phẩm -> xem chi tiết -> thêm vào giỏ hàng -> checkout.
   - Tỷ lệ lỗi ghi nhận chính xác theo thiết kế (chỉ các user có password sai mới nhận 401/403).
   - Đã dọn dẹp artifacts tạm thời và reset trạng thái CSDL sẵn sàng cho Phase 3.
```
