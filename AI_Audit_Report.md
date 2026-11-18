# AI Audit Report - HW05

**Sinh viên:** Phan Trung Tin - 23120372  
**Ngày tổng hợp:** 2026-11-18  
**Công cụ AI:** OpenCode (coding agent)  
**Model:** DeepSeek V4.1 Flash Free (`opencode/deepseek-v4.1-flash-free`)  
**Múi giờ log:** Asia/Ho_Chi_Minh (UTC+7)

---

## 1. Mục đích và phạm vi

Báo cáo này liệt kê mọi tương tác AI có ảnh hưởng đến bài HW05: đọc đề, lập kế hoạch,
sinh JMX, sửa lỗi, chạy thử, phân tích `.jtl`, đề xuất tối ưu và viết tài liệu. Nguyên tắc:

1. AI **không** tạo ra số liệu. Mọi con số trong báo cáo chính đều truy vết được về
   `.jtl`, `resources.csv`, `manifest.json` hoặc output lệnh thật.
2. Mỗi prompt quan trọng được lưu nguyên văn (hoặc kèm đường dẫn transcript), cùng
   thời điểm, output thật và phần review của con người.
3. Chỗ AI sai được giữ lại trong log, không xóa; phần sửa nằm trong cột "Human review".
4. Không log token, mật khẩu thật hay dữ liệu cá nhân.

---

## 2. Tổng hợp tương tác

| Entry | Thời điểm | Việc AI làm | Output thật | Human review |
|---|---|---|---|---|
| 001 | 2026-11-16 12:00 | Đọc PDF HW05, tóm tắt yêu cầu, lập `PLAN.md`, hỏi lại các điểm chưa rõ | `ai_audit/entries/001_planning.md` | Chấp nhận cấu trúc; bổ sung quyết định port 3100, dataset 500 user, tách Lockout Probe |
| 002 | 2026-11-16 12:04 | Preflight, clone SUT, viết script seed/reset/CSV, ghi commit | `ai_audit/entries/002_setup.md` | Kiểm tra thủ công số row DB; phát hiện `database.js` drop/reseed mỗi lần start |
| 003 | 2026-11-16 12:20 | Sinh 3 JMX + runner/monitor/analyzer; chạy pilot và sửa lỗi | `ai_audit/entries/003_jmx.md` | Sửa `ignoreFirstLine`, bỏ transaction parent sample, tách lockout, tắt listener khi chạy non-GUI |
| 004 | 2026-11-18 14:40 | Chạy chính thức Stress/Spike/Endurance, đọc manifest, phát hiện host CPU cao | `ai_audit/entries/004_official_runs.md` | Kiểm tra `.jtl`/`resources.csv`; không dùng số liệu AI tự nêu |
| 005 | 2026-11-18 16:10 | Task 2: AI đọc 6 file `.jtl` + `resources.csv`, tự tính metric, đề xuất threshold/bottleneck/8 tối ưu | `ai_audit/entries/005_task2_ai.md` | Kiểm chứng bằng `scripts/verify_task2_ai.py`; sửa 1 hallucination về JMX, 1 sai số VU, 3 kết luận vượt dữ liệu; phân loại đề xuất trong `Task2_AI_Analysis.md` |
| 006 | 2026-11-18 16:40 | Viết report, Task 3, critique; rà lại số liệu | `ai_audit/entries/006_writing.md` | Chỉ giữ câu có nguồn; sửa các chỗ AI suy diễn quá mức |

> Các entry 004-006 được điền đầy đủ trong quá trình hoàn thiện; bảng này chỉ là index.

---

## 3. AI đã làm đúng

- Sinh được 5 JMX nhất quán từ một workflow, có CSV, JSON Extractor và assertion body.
- Viết runner có preflight DB, monitor tài nguyên, manifest SHA-256 và HTML dashboard.
- Phát hiện và sửa các lỗi vận hành thật: header CSV bị đọc như dữ liệu, race của
  lockout khi request quá nhanh, transaction parent sample làm sai thống kê label.
- Tự động hóa phân tích p50/p95/p99, error code và timeline 30 s từ `.jtl`.
- Ở Task 2, AI đọc đúng **toàn bộ** p50/p95/p99/max của 6 run và các cột `resources.csv`
  (kiểm chứng độc lập bằng `scripts/verify_task2_ai.py`), và tự phát hiện stall toàn cục
  ~1,6 s ở Load đúng tới mức timestamp.

## 4. AI đã sai hoặc suy diễn quá mức

Phần này chỉ trích các câu **có trong output đã lưu** (`ai_audit/entries/005_task2_ai.md`).
Mỗi câu được đối chiếu lại với file gốc; cột cuối là giá trị đúng.

| # | AI nói (nguyên văn, rút gọn) | Sai ở đâu | Giá trị đúng từ raw file |
|---|---|---|---|
| 1 | "`23120372_Load_20261118.jmx` chỉ có `ConstantTimer.delay=2000` (không có Uniform Random Timer)" | Khẳng định nội dung một file mà nó không mở | JMX dòng 107-111 có `<GaussianRandomTimer>` với `ConstantTimer.delay=2000` **và** `RandomTimer.range=1000.0` |
| 2 | "Stress đạt 154 sample/s ở phút 11 (9.258 sample/60 s, **158 VU**)" | Nhầm giá trị trung bình với giá trị lớn nhất | Bucket đó có `allThreads` max = **160**; 154,30 req/s @ 160 VU |
| 3 | "CPU bị throttle: hardware_report ghi max clock 1.498 MHz vs base 2,6 GHz" | `MaxClockSpeed` của WMI không phải xung nhịp lúc chạy; máy báo 1498 cả khi idle | Không có cột tần số trong `resources.csv` ⇒ **không đủ dữ liệu** kết luận throttle |
| 4 | "~60-80% CPU bị tiêu bởi thứ khác (Defender/OS/process khác)" | `resources.csv` chỉ đo backend, JMeter, sys; không có per-process | Chỉ được nói sys CPU > tổng CPU hai tiến trình được đo; **không quy được cho process nào** |
| 5 | "Memory ceiling: cảnh báo 220 MB, trần vận hành 250 MB"; "RPS bền vững 100/s (đã kiểm chứng gián tiếp)" | Không có phép đo tương ứng | RSS đỉnh đo được **182,34 MB** (75C) / **182,25 MB** (100C); chưa từng chạy 100 req/s dài hạn - đó là ngoại suy từ Stress |
| 6 | "Container limit 384-512 MB" | SUT chạy Node trực tiếp, không có container trong bài | Không tồn tại artifact container nào trong repo |

Ghi chú về các entry trước: trong quá trình làm, tôi đã bỏ nhiều câu AI diễn giải sai
(ví dụ gọi p95 40 ms ở 80 VUs là "knee" dù 120 VUs chỉ 29 ms; gán max 1.619 ms cho checkout
dù sample đó là `GET /api/products/{id}`; đọc 226% CPU của JMeter thành "server quá tải").
Các câu đó không được đưa vào báo cáo cuối; bảng trên chỉ giữ những câu có transcript lưu lại
để người đọc kiểm tra được.

## 5. Quyết định của con người

- Không dùng bất kỳ metric nào AI "ước lượng" khi chưa có `.jtl`.
- Đổi cách tính CV throughput từ bucket 1 s sang bucket 30 s vì 1 s dao động do
  think-time, không phản ánh instability.
- Đặt warm-up 300 s cho tiêu chí RAM và báo cáo riêng slope sau 300 s.
- Giữ kết luận "chưa thấy knee của SUT" thay vì gán bottleneck cho backend khi
  bằng chứng chỉ cho thấy host bão hòa.
- Tách Lockout Probe khỏi error rate chính.

## 6. Kết luận

AI tăng tốc đáng kể phần dựng plan, tooling và phân tích, nhưng **không thể thay thế**
việc kiểm tra raw log. Các lỗi ở mục 4 đều là lỗi diễn giải metric, không phải lỗi file;
nếu không review, báo cáo sẽ có threshold và bottleneck sai. Toàn bộ artifact và prompt
được lưu để tái kiểm tra.
