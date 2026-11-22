# AI Critique — Reflections on AI-Assisted Performance Testing

**Student ID:** 23120320  
**Course:** Software Testing / Performance Testing (HW05-AI)

---

Việc sử dụng AI trong bài tập performance testing này đã cho thấy cả những bước nhảy vọt đáng kể về hiệu suất lẫn những điểm mù nghiêm trọng vốn có của các large language models hiện đại.

Ở mặt tích cực, AI đóng vai trò là một công cụ nhân rộng hiệu quả trong các giai đoạn dựng khung. Tạo ra phần core logic cho Agent Skill có thể tái sử dụng, các trình tạo bộ dữ liệu giả lập, và các non-GUI JMeter execution scripts chỉ trong vài phút. Việc viết thủ công các multi-step JMeter test plans trên giao diện GUI rất tẻ nhạt và dễ phát sinh lỗi; việc để AI tự động xây dựng các programmatic JMX templates và automated log parsers đã giúp đẩy nhanh chu kỳ kiểm thử lên ít nhất 70%.

Tuy nhiên, trải nghiệm này cũng nhấn mạnh lý do tại sao sự kiểm chứng có con người tham gia là điều bắt buộc trong software engineering. AI thường xuyên bộc lộ tình trạng "mù ngữ cảnh cục bộ" và sự thiếu ổn định về mặt cấu trúc. Ban đầu, nó đã tạo ra các file JMeter XML không hợp lệ khi tham chiếu đến các third-party classes (JSONPathExtractor) vốn không có sẵn trong bản JMeter 5.6.3 tiêu chuẩn và bỏ sót các thẻ <hashTree/> bắt buộc. Đáng báo động hơn, trong quá trình phân tích chỉ số (metric analysis), AI đã mắc phải những cái bẫy kinh điển về thống kê và nghiệp vụ chuyên ngành: nó phân loại nhầm các lỗi kiểm thử bảo mật có chủ đích (tình huống khóa tài khoản khi nhập sai mật khẩu chiếm tỷ lệ 10%) thành các system bugs nghiêm trọng; tán dương mức đỉnh throughput mang tính đánh lừa trong bài Spike test mà bỏ qua đợt tăng vọt p95 latency lên tới 4,6 giây mang tính thảm họa; đồng thời bịa đặt ra các giải pháp cấp doanh nghiệp không thể áp dụng như HikariCP connection pooling và Kubernetes HPA cho một cơ sở dữ liệu nhúng cục bộ.

Tóm lại, AI là một trợ lý xuất sắc cho việc sinh mã, điều phối quy trình và tổng hợp chỉ số, nhưng nó lại thiếu trực giác kiến trúc thực thụ và ngữ cảnh thực nghiệm. Lĩnh vực performance engineering đòi hỏi độ chính xác cao luôn cần các kỹ sư con người thiết lập các đường cơ sở thống kê chặt chẽ, truy vấn hành vi ở các trường hợp biên, và xác thực xem các đề xuất tối ưu hóa từ AI có phù hợp với những ràng buộc hạ tầng thực tế hay không.
