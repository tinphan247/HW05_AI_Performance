# AI Critique - HW05

AI là một "junior engineer" đọc số rất giỏi nhưng hay lấp chỗ trống bằng niềm tin. Trong bài
này, nó giúp tôi dựng 5 JMX từ một workflow, viết runner có manifest SHA-256, monitor tài
nguyên và parser JTL trong vài giờ. Ở Task 2, nó tự tính lại toàn bộ p50/p95/p99/max của 6
run, và tôi kiểm chứng từng con số: đều khớp. Nó còn phát hiện đúng một stall toàn cục ~1,6 s
ở Load bằng cách nhìn 15 sample chậm cùng kết thúc trong 0,24 s - đó là kết luận tôi giữ lại.

Nhưng AI cũng khẳng định nội dung file mà nó chưa mở: nó nói JMX "chỉ có ConstantTimer,
không có random timer", trong khi file có `GaussianRandomTimer`. Nó đọc `MaxClockSpeed=1498`
của WMI - trường không đáng tin - rồi kết luận CPU bị throttle. Nó tự trừ
CPU hệ thống với CPU của hai tiến trình được đo, ra "60-80% bị process khác dùng", dù
`resources.csv` không có dữ liệu per-process. Và nó biến ngoại suy thành threshold: "trần
250 MB", "100 req/s đã kiểm chứng", trong khi đỉnh đo được chỉ là 182,34 MB và chưa từng có
run 100 req/s dài hạn.

Điểm đáng khen là mục 6 của AI tự liệt kê 7 chỗ phải suy đoán. Nhưng đó cũng là bài học:
một báo cáo có mục "tôi đoán" không làm cho các con số đoán trở nên hợp lệ. Nếu tôi không
đối chiếu raw log, threshold và bottleneck trong bài đã sai theo hướng nghe rất thuyết phục.
Vì vậy tôi giữ nguyên tắc: AI được quyền đề xuất, không được quyền làm nguồn sự thật; mọi
con số cuối cùng phải trỏ được về file, dòng, timestamp.
