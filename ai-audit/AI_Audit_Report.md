# AI Audit Report — HW05 Performance Testing

**Student ID:** 23120320  
**Course:** Software Testing / Performance Testing (HW05-AI)  
**System Under Test (SUT):** EShop Demo Application (Node.js Express + SQLite)

---

## Declaration of AI Tool Usage

In accordance with the HCMUS Academic Integrity & Generative AI Policy, I hereby declare that AI tools were utilized throughout this assignment for:

1. Formulating the project implementation plan and structuring the execution phases.
2. Generating and refining the reusable Agent Skill (`hw05-perf-testing`) for JMeter test automation.
3. Generating initial JMeter JMX test plans and parameter models for the Browse-to-Buy workflow.
4. Analyzing test logs (`.jtl`) and proposing performance thresholds and optimization strategies.

All AI-generated content, test plans, and analyses were rigorously reviewed, empirically verified against raw log files, and corrected by human review as documented in this report.

---

## Đề xuất Plan

- **Name of the AI tool:** Claude Sonnet 4.6
- **Date and time:** 2026-11-16 09:16:36
- **Prompt:**
  ```text
  Hãy lên kế hoạch để thực hiện bài tập này, đưa task Agent skill lên trước. Viết vào 1 file .md
  ```
- **AI Output Summary:**
  AI đề xuất lộ trình 10 Phase với trọng tâm xây dựng Agent Skill trước tại Phase 1 (`SKILL.md`, `generate_csv.py`, `analyze_jtl.py`, `run_scenario.ps1`), sau đó tiến hành sinh dữ liệu, chạy 4 kịch bản (Load, Stress, Spike, Soak), thực hiện AI Analysis & Misinterpretation Hunt (Task 2), đề xuất Continuous Performance Testing (Task 3), và hoàn thiện báo cáo.

---

## Khởi tạo Cấu trúc & Xây dựng Agent Skill

- **Name of the AI tool:** Claude Sonnet 4.6
- **Date and time:** 2026-11-16 09:27:58
- **Prompt:**
  ```text
  Đây là thư mục SUT local: "C:\Users\opmeo\OneDrive\Desktop\eshop-sut". Hãy khởi tạo giúp tôi cấu trúc thư mục như plan rồi thực hiện luôn Phase 1.
  ```
- **AI Output Summary:**
  AI đã scaffold toàn bộ cấu trúc dự án và xây dựng 5 script trong `skills/hw05-perf-testing/scripts/`:
  - `generate_csv.py`: Tạo 150 người dùng với 10% mật khẩu sai để kiểm thử Account Lockout (FR-02) và 150 sản phẩm kèm mã giảm giá.
  - `generate_jmx.py`: Tạo kịch bản JMeter 5 bước E2E Browse-to-Buy kèm trích xuất JWT Token.
  - `analyze_jtl.py`: Script phân tích log `.jtl` trích xuất min/avg/max, p50, p75, p90, p95, p99, throughput và mã lỗi HTTP.
  - `run_scenario.ps1`: Script PowerShell điều phối chạy non-GUI JMeter và sinh HTML report.

---

## Khám sát, Sinh Dữ liệu & Sửa Lỗi JMeter Template

- **Name of the AI tool:** Gemini 3.8 Flash
- **Date and time:** 2026-11-16 09:57:53
- **Prompt:**
  ```text
  Sử dụng skills đã tạo để thực hiện phase 2 trong plan.
  ```
- **Human Review & AI Flaws Detected:**
  1. _Lỗi XML Class:_ AI ban đầu sinh thẻ `JSONPathExtractor` (plugin bên thứ ba cũ không có sẵn trong JMeter 5.6.3). Con người đã phát hiện và chuyển sang component chuẩn `JSONPostProcessor`.
  2. _Lỗi HashTree pairing:_ AI bỏ sót các thẻ `<hashTree/>` đi kèm sau mỗi phần tử con, gây ra lỗi `ClassCastException` trong parser của JMeter.
  3. _Lỗi CSV Share Mode:_ AI cấu hình `shareMode.thread` khiến mọi luồng đều reset về đọc dòng 1 trong CSV. Con người đã sửa thành `shareMode.all` để chia đều 150 tài khoản cho các luồng ảo.
  4. _Lỗi Seed Database:_ SUT mặc định chỉ có 2 tài khoản, AI không tự động đồng bộ tài khoản test vào SQLite. Con người đã bổ sung logic đồng bộ 150 `perfuser` vào file `database.sqlite`.

---

## AI Phân tích Log Thô & Đề xuất Ngưỡng Hiệu Năng

- **Name of the AI tool:** Gemini 3.8 Flash / Claude 3.5 Sonnet
- **Date and time:** 2026-11-21 10:24:25
- **Prompt:**

  ```text
  Dưới đây là kết quả tóm tắt từ file log .jtl của 4 kịch bản kiểm thử hiệu năng trên hệ thống EShop (Node.js + SQLite):

  1. Load Test (50 VU, 5 phút):
     - Total: 6,739 requests, Error Rate: 6.01%, Throughput: 22.57 req/s
     - Latency: avg=4.0ms, max=50ms, p50=1ms, p90=15ms, p95=16ms, p99=19ms
     - Breakdown: Login 10% err, Products 0% err, Detail 0% err, Cart 10% err, Checkout 10.1% err.

  2. Stress Test (200 VU, 10 phút):
     - Total: 106,718 requests, Error Rate: 6.00%, Throughput: 178.12 req/s
     - Latency: avg=9.9ms, max=639ms, p50=2ms, p90=25ms, p95=35ms, p99=64ms
     - Breakdown: Login 10% err, Products 0% err, Detail 0% err, Cart 10% err, Checkout 10% err.

  3. Spike Test (500 VU, 2 phút):
     - Total: 40,562 requests, Error Rate: 6.02%, Throughput: 339.28 req/s
     - Latency: avg=934.1ms, max=5814ms, p50=378ms, p90=2811ms, p95=3410ms, p99=4612ms
     - Breakdown: Login 10% err, Products 0% err, Detail 0% err, Cart 10% err, Checkout 10% err (p95 checkout: 4,598ms).

  4. Soak Test (50 VU, 10 phút):
     - Total: 9,710 requests, Error Rate: 6.01%, Throughput: 16.29 req/s
     - Latency: avg=3.8ms, max=68ms, p50=1ms, p90=15ms, p95=15ms, p99=18ms
     - Node.js RAM: 75MB ban đầu -> 92MB sau 10 phút.

  Hãy phân tích các số liệu trên, đề xuất Service Level Objectives (SLOs) và đưa ra các khuyến nghị tối ưu hóa hệ thống.
  ```

- **AI Output Generated:**
  ```text
  [AI Analysis]
  1. Đánh giá chung: Hệ thống có độ ổn định kém và tỷ lệ lỗi cao (xấp xỉ 6.0% xuyên suốt cả 4 kịch bản). Cần xem lại tính toàn vẹn của code backend vì tỷ lệ lỗi chuẩn công nghiệp phải < 1%.
  2. Về Throughput: Hệ thống xử lý rất tốt tải đột biến, thông lượng đạt đỉnh 339.28 req/s ở kịch bản Spike, chứng tỏ ứng dụng có khả năng co giãn tốt khi có traffic dồn dập.
  3. Về Latency: Độ trễ trung bình của hệ thống ở Load (4.0ms) và Stress (9.9ms) là cực kỳ ấn tượng (dưới 10ms), đáp ứng tốt tiêu chuẩn trải nghiệm người dùng nhanh.
  4. Về Soak Test: Tiến trình Node.js có dấu hiệu rò rỉ bộ nhớ (Memory Leak) vì RAM tăng liên tục từ 75MB lên 92MB trong 10 phút.
  5. Đề xuất ngưỡng hiệu năng (SLOs):
     - Throughput: Duy trì tối thiểu 200 req/s.
     - Latency: p95 < 50ms cho mọi kịch bản.
     - Error rate: < 0.5%.
  6. Khuyến nghị tối ưu:
     - Gợi ý 1: Bật chế độ Write-Ahead Logging (WAL) cho SQLite.
     - Gợi ý 2: Thêm tầng Redis Caching cho danh mục sản phẩm.
     - Gợi ý 3: Đánh chỉ mục (Index) trên các bảng orders và coupon_usage.
     - Gợi ý 4: Thiết lập Connection Pool với 50 kết nối bằng HikariCP/pg-pool cho SQLite.
     - Gợi ý 5: Cấu hình Kubernetes Horizontal Pod Autoscaling (HPA) nhân bản từ 1 lên 10 pods khi tải tăng.
  ```

---

## Human Review — AI Hiểu Sai Số Liệu

Dưới đây là bảng đối chiếu chi tiết giữa nhận định của AI và sự thật kỹ thuật từ file log `.jtl` thô:

| #     | Khía cạnh / Chỉ số                          | Nhận định của AI (AI Claim)                                                                                            | Sự thật từ Log Thô (.jtl) & Môi trường                                                                                                                                                                            | Đánh giá & Phân tích lỗi của AI (Human Critique)                                                                                                                                                                                                     |
| ----- | ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1** | **Tỷ lệ lỗi 6.0% (Error Rate)**             | _"Hệ thống có độ ổn định kém vì tỷ lệ lỗi 6.0% quá cao so với tiêu chuẩn < 1%. Cần sửa code để loại bỏ lỗi 401/403."_  | Log JTL xác nhận: Đúng 10.0% request Login nhận 401/403. Các request Cart và Checkout tương ứng nhận 403 do không có JWT token. Tổng lỗi chính xác = $\frac{10\% + 0\% + 0\% + 10\% + 10\%}{5} = \mathbf{6.0\%}$. | **AI HIỂU SAI BẢN CHẤT TEST DATA:** AI không nhận ra tỷ lệ lỗi 6.0% là **chủ đích thiết kế** (10% tài khoản cố ý nhập sai mật khẩu để kiểm thử tính năng Account Lockout FR-02). 90% người dùng hợp lệ hoàn thành đơn hàng 100% không có lỗi.        |
| **2** | **Thông lượng Spike (Throughput Peak)**     | _"Hệ thống co giãn và xử lý tải đột biến xuất sắc vì thông lượng đạt đỉnh 339.28 req/s, cao nhất trong các bài test."_ | Log Spike JTL ghi nhận: p95 latency vọt lên **3,410 ms**, p95 của checkout lên tới **4,598 ms**, độ trễ cực đại đạt **5,814 ms**.                                                                                 | **AI BỊ BẪY BỞI CON SỐ TỔNG:** Throughput cao chỉ vì 500 thread dồn request liên tục, nhưng thực tế hệ thống đã bị **nghẽn cổ chai nghiêm trọng (performance degradation)**. Người dùng phải chờ gần 5 giây để thanh toán.                           |
| **3** | **Độ trễ trung bình (Average Latency)**     | _"Hệ thống đáp ứng cực kỳ nhanh vì độ trễ trung bình ở Stress test chỉ 9.9 ms và Load test chỉ 4.0 ms (< 10ms)."_      | Log Stress JTL: p95 là **35 ms**, max latency là **639 ms**. Log Spike: p95 là **3,410 ms**, max là **5,814 ms**.                                                                                                 | **AI MẮC LỖI THỐNG KÊ CƠ BẢN:** AI dùng giá trị trung bình (Mean) bị làm loãng bởi các request tĩnh nhanh (`GET /api/products`), che giấu hoàn toàn hiện tượng trễ đuôi dài (Tail Latency) ở các thao tác ghi CSDL.                                  |
| **4** | **RAM trong Soak Test (Memory Leak Claim)** | _"Node.js backend bị rò rỉ bộ nhớ (Memory Leak) vì dung lượng RAM tăng từ 75MB lên 92MB trong 10 phút."_               | Quan sát Task Manager: RAM tăng từ 75MB trong 3 phút đầu, sau đó ổn định đi ngang ở mức 92MB suốt 7 phút còn lại; CPU duy trì 2-5%.                                                                               | **AI KẾT LUẬN VỘI VÃ:** Việc RAM tăng ban đầu là do V8 engine cấp phát heap memory và SQLite nạp cache trang vào RAM. Khi chạm mức trần 92MB, bộ nhớ hoàn toàn đi ngang không tăng thêm (Memory Ceiling), chứng minh hệ thống không bị rò rỉ bộ nhớ. |

---

## Human Review — Đánh Giá Khuyến Nghị của AI

Phân loại 5 khuyến nghị tối ưu hóa của AI dựa trên kiến trúc thực tế của SUT (`eshop-sut` Node.js Express + SQLite):

| #     | Khuyến nghị của AI                                                    |                      Phân loại                      | Phân tích Kỹ thuật & Độ tương thích với SUT                                                                                                                                                                                                                                                         |
| ----- | --------------------------------------------------------------------- | :-------------------------------------------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1** | **Bật chế độ Write-Ahead Logging (WAL) cho SQLite**                   |       **FEASIBLE** _(Khả thi & Hiệu quả cao)_       | SQLite mặc định dùng rollback journal, khóa toàn bộ file database khi có một luồng ghi. Lệnh `PRAGMA journal_mode = WAL;` cho phép nhiều luồng đọc đồng thời với một luồng ghi, trực tiếp giải tỏa nút thắt p95 = 4.6s ở bước checkout.                                                             |
| **2** | **Thêm tầng Redis Caching cho Danh mục Sản phẩm**                     |              **FEASIBLE** _(Khả thi)_               | Endpoint `GET /api/products` và `GET /api/products/:id` chiếm 40% lưu lượng và dữ liệu ít thay đổi. Cache danh mục vào Redis giúp giảm tải đọc từ đĩa cứng, giải phóng I/O cho giao dịch đặt hàng.                                                                                                  |
| **3** | **Tạo Database Index trên bảng `orders` và `coupon_usage`**           |        **FEASIBLE** _(Khả thi & Cần thiết)_         | Khi checkout, backend thực hiện câu truy vấn kiểm tra số lần dùng coupon: `SELECT count(*) FROM coupon_usage WHERE coupon_id = ? AND user_id = ?`. Thêm composite index `(coupon_id, user_id)` sẽ loại bỏ full table scan khi đơn hàng tăng.                                                        |
| **4** | **Tạo Connection Pool 50 kết nối bằng HikariCP / pg-pool cho SQLite** |    **HALLUCINATED** _(Ảo tưởng / Sai kiến trúc)_    | SQLite là cơ sở dữ liệu nhúng (embedded file-based), không hoạt động theo mô hình Client-Server. Việc cấu hình pool kết nối mạng kiểu Postgres/MySQL cho driver `sqlite3` trong Node.js là vô nghĩa và sẽ gây lỗi `SQLITE_BUSY: database is locked`.                                                |
| **5** | **Cấu hình Kubernetes HPA nhân bản từ 1 lên 10 Pods**                 | **HALLUCINATED** _(Không khả thi với SUT hiện tại)_ | Database của SUT là file cục bộ `backend/database.sqlite`. Nếu scale horizontal ra 10 pods độc lập, mỗi pod sẽ ghi vào file riêng của nó, dẫn tới phân mảnh dữ liệu nghiêm trọng và bất nhất giỏ hàng/đơn hàng giữa các người dùng. Muốn dùng HPA bắt buộc phải di chuyển DB sang PostgreSQL trước. |

---
