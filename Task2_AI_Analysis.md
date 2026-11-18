# Task 2 - AI phân tích JTL, con người kiểm chứng

**Sinh viên:** Phan Trung Tin - 23120372  
**AI dùng:** OpenCode subagent, model DeepSeek V4.1 Flash Free  
**Prompt nguyên văn:** `ai_audit/transcripts/task2_prompt.md`  
**Output nguyên văn:** `ai_audit/entries/005_task2_ai.md`  
**Script kiểm chứng:** `scripts/verify_task2_ai.py`  
**Nguyên tắc:** mọi con số dưới đây đọc lại từ `.jtl` / `resources.csv`; không dùng số AI tự nêu
nếu không tái tạo được.

---

## 1. Kết quả kiểm chứng tổng quát

Tôi chạy lại toàn bộ phép tính percentile bằng Python trên chính các file `.jtl` đã nộp
(`scripts/verify_task2_ai.py`). Kết quả:

| Scenario | AI nêu (p50/p95/p99/max) | Raw log tính lại | Khớp? |
|---|---|---|---|
| Load | 2 / 11 / 15 / 1.619 | 2 / 11 / 15 / 1.619 | Có |
| Stress | 3 / 31 / 95 / 322 | 3 / 31 / 95 / 322 | Có |
| Spike | 4 / 17 / 71 / 177 | 4 / 17 / 71 / 177 | Có |
| Endurance 50C | 4 / 16 / 20 / 92 | 4 / 16 / 20 / 92 | Có |
| Endurance 75C | 2 / 22 / 134 / 1.157 | 2 / 22 / 134,39 / 1.157 | Có (làm tròn) |
| Endurance 100C | 2 / 38 / 118 / 1.248 | 2 / 38 / 118 / 1.248 | Có |

Các con số phụ cũng khớp:

- `backend_conns` max 32 / 162 / 102 / 83 / 123 / 163 - đúng thứ tự AI nêu.
- `backend_threads` luôn 12-16 - đúng.
- `backend_rss_mb` max 65,91 / 181,37 / 122,36 / 179,84 / 182,34 / 182,25 - đúng.
- Stress: bucket 60 s cao nhất là phút 11 với 9.258 sample = **154,30 req/s** - đúng.
- Load: đúng **15 sample > 100 ms**, tất cả kết thúc trong khoảng **161,053-161,292 s**
  (rộng 0,239 s), sample 1.619 ms bắt đầu lúc ~159,67 s. Mô tả "dồn vào 159,6-161,3 s và
  cùng kết thúc ~161,29 s" là **đúng**.

Điểm đáng ghi nhận: AI tự phát hiện **stall toàn cục** (nhiều label kết thúc cùng một mốc)
thay vì đổ lỗi cho một endpoint. Đây là kết luận đúng và có giá trị, tôi giữ lại trong báo cáo.

---

## 2. Chỗ AI đọc sai hoặc bịa (citations từ raw log)

### 2.1. AI bịa nội dung file JMX (sai rõ ràng)

**AI viết** (mục 2, ý 6):

> "`manifest.md` ghi 'think 2000 ± 1000 ms' nhưng `23120372_Load_20261118.jmx` chỉ có
> `ConstantTimer.delay=2000` (không có Uniform Random Timer) ⇒ tải thực tế (14 req/s) khác mô tả."

**Raw log / file thật:** `test-plans/23120372_Load_20261118.jmx`, dòng 107-111:

```xml
<GaussianRandomTimer guiclass="GaussianRandomTimerGui" testclass="GaussianRandomTimer" testname="Think time" enabled="true">
  <stringProp name="ConstantTimer.delay">2000</stringProp>
  <stringProp name="RandomTimer.range">1000.0</stringProp>
</GaussianRandomTimer>
```

JMX **có** timer ngẫu nhiên (`GaussianRandomTimer`, mean 2000 ms, range 1000 ms), đúng như
manifest mô tả. AI không mở file nhưng khẳng định nội dung file. Đây là **hallucination**,
không phải sai số. Hệ quả: lập luận "tải thực tế khác mô tả" không có cơ sở.

### 2.2. AI nêu sai số VU ở đỉnh Stress

**AI viết:** "Stress đạt 154 sample/s ở phút 11 (9.258 sample/60 s, **158 VU**)."

**Raw log:** trong bucket 60 s đó, `allThreads` đạt **160**, không phải 158
(`max(int(allThreads)) = 160`). 158 có thể là trung bình cộng của cột, nhưng câu văn nói
"158 VU" như một giá trị đo. Sai lệch nhỏ nhưng phải sửa: **154,30 req/s @ 160 VU**.

### 2.3. AI suy ra "CPU bị throttle" từ một trường WMI

**AI viết:** "CPU bị throttle: `hardware_report.md` ghi max clock 1.498 MHz vs base 2,6 GHz."

**Raw log:** `hardware/hardware_report.md` lấy `Win32_Processor.MaxClockSpeed`. Máy này báo
`MaxClockSpeed = 1498` và `CurrentClockSpeed = 1498` **ngay cả khi idle**, trong khi tên CPU
là "11th Gen Intel Core i5-1145G7 @ 2.60GHz". Đây là hành vi quen thuộc của WMI trên laptop
(giá trị không phản ánh xung nhịp thực khi chạy). `resources.csv` **không có** cột tần số CPU,
nên không có bằng chứng throttle trong lúc test.

Kết luận đúng phải là: **không đủ dữ liệu để nói CPU bị throttle**. AI có tự ghi chú đây là
"suy đoán" ở mục 6, nhưng ở mục 4 lại dùng nó như bằng chứng - không nhất quán.

### 2.4. AI định lượng "60-80% CPU bị tiêu bởi thứ khác"

**AI viết:** "Tổng công suất 2 tiến trình chỉ ~0,3-3 core/8 → **~60-80% CPU bị tiêu bởi thứ khác**."

**Raw log:** `resources.csv` chỉ có `backend_cpu_pct`, `jmeter_cpu_pct`, `sys_cpu_pct`. Không
có dữ liệu per-process, nên **không thể** quy phần CPU còn lại cho process nào. Con số 60-80%
là phép trừ trên giả định, không phải số đo. Được phép nói "sys CPU cao hơn tổng CPU của hai
tiến trình được đo", **không** được nói ai đã dùng phần còn lại.

### 2.5. AI trộn cửa sổ đo khiến số liệu không so sánh được

AI tính throughput bằng `rows / (max(timestamp+elapsed) - min(timestamp))`, tức **cả run kể cả
ramp-up**. Vì vậy AI báo Endurance 50C = 38,16/s, 75C = 56,81/s, 100C = 75,77/s. Báo cáo chính
dùng **steady-state 30 s bucket** sau warm-up: 39,53 / 58,89 / 78,89/s. Cả hai đều đúng trên
dữ liệu thật, nhưng **chỉ số steady-state** mới dùng để kết luận threshold. Tương tự p99 75C:
AI 134,39 ms (cả run) vs 123,69 ms (steady). Đây là khác biệt phương pháp, không phải AI bịa,
nhưng nếu trộn hai cách trong một bảng thì kết luận sẽ sai.

### 2.6. AI đề xuất threshold không đo được

- "Memory ceiling: cảnh báo 220 MB, trần vận hành 250 MB" - raw log chỉ chứng minh đỉnh
  **182,34 MB**. 250 MB là biên an toàn do AI tự đặt, không phải số đo.
- "RPS bền vững 100/s (đã kiểm chứng gián tiếp)" - không có run nào chạy 100 req/s trong
  10-15 phút. Đây là **ngoại suy** từ Stress; AI tự nhận ở mục 6 nhưng vẫn gọi là "đã kiểm chứng".
- "Container limit 384-512 MB" - SUT này chạy Node trực tiếp, **không có container**. Đề xuất
  này giả định một kiến trúc không tồn tại trong bài.

---

## 3. Phân loại 8 đề xuất tối ưu của AI

| # | Đề xuất của AI | Kiểm chứng với code/DB | Phân loại |
|---|---|---|---|
| 1 | `journal_mode=WAL`, `synchronous=NORMAL`, `busy_timeout` | `PRAGMA` thật: `journal_mode=delete`, `synchronous=2`; `database.js` không set PRAGMA | **Feasible** |
| 2 | Index `users(email)`, `orders(user_id)` | `sqlite_master` chỉ có `sqlite_autoindex_coupons_1`; users/orders có **0** index | **Feasible** |
| 3 | Tham số hoá search + FTS5 | `server.js:144` nối chuỗi `LIKE '%${searchQuery}%'`; `?search='` trả HTTP 500 | **Feasible** |
| 4 | Phân trang products và my-orders | `GET /api/products` trả 205 item / 25.782 byte; my-orders bytes tăng 522 → 1.475 | **Feasible** |
| 5 | Bỏ `UPDATE` khi login thành công, prepared statement, gộp commit | `server.js:46-50` update `login_attempts=0` mỗi lần login đúng | **Feasible** |
| 6 | Chuyển JMeter sang máy khác, giảm listener, tắt HTML khi đo | Đúng là cải thiện validity, nhưng **không phải tối ưu SUT**; `jmeter_rss_mb` max 826 MB là thật | **Feasible** (ngoài phạm vi SUT) |
| 7 | Tăng `UV_THREADPOOL_SIZE`, tách DB worker / `better-sqlite3` + write queue | `backend_threads` 12-16 là thật, nhưng không có metric độ trễ hàng đợi để chứng minh đây là nút chặn | **Cần thêm dữ liệu** |
| 8 | Node cluster + Postgres + container hoá, tách host | Thay đổi kiến trúc; cần host thứ hai và thời gian không có trong HW05 | **Không khả thi trong phạm vi bài** |

Các "đề xuất" **hallucinated** (dựa trên tiền đề không tồn tại hoặc không đo được):

| Đề xuất | Vì sao hallucinated |
|---|---|
| "Container limit 384-512 MB" | SUT không chạy container; không có artifact nào chứng minh môi trường container |
| "Trần vận hành 250 MB" như một threshold | Không có run nào đo 250 MB; đỉnh thật là 182,34 MB |
| "Cam kết 100 req/s đã kiểm chứng" | Không có phép đo trực tiếp 100 req/s dài hạn; chỉ ngoại suy |
| "JMX không có random timer" | File JMX có `GaussianRandomTimer` (dẫn chứng ở 2.1) |

---

## 4. Những gì tôi giữ lại từ AI

Không phải mọi kết luận đều phải bỏ. Sau khi đối chiếu, tôi giữ:

1. **Stall toàn cục ~1,6 s ở Load** - đúng timestamp, đúng 15 sample, đúng việc nhiều label
   kết thúc cùng lúc. Tôi thêm nhận xét này vào mục 4.1 của báo cáo chính.
2. **"C=160 VUs là tham số workload, không phải capacity đo được"** - đúng và quan trọng;
   báo cáo chính đã có caveat tương tự ở mục 9, nay củng cố bằng số bucket.
3. **RSS plateau chứ không leak tuyến tính** - khớp với phân tích steady-state của tôi.
4. **SQLite `journal_mode=delete` + `synchronous=2` + thiếu index** - kiểm chứng đúng, là
   giải thích hợp lý cho chi phí ghi của checkout, dù chưa profile được.
5. **Nghịch lý p50 của Endurance 50C** (4 ms > 2 ms) - đúng là bất thường, AI chịu nói
   "không đủ dữ liệu" thay vì bịa nguyên nhân.

## 5. Kết luận của con người

AI đọc số rất tốt: 100% giá trị p50/p95/p99/max và các cột `resources.csv` tôi kiểm tra đều
tái tạo được. Nhưng nó **không phân biệt được "đọc file" với "nhớ file"**: câu về JMX là bịa
hoàn toàn, và các kết luận nhân quả (throttle, 60-80% CPU, memory ceiling 250 MB) vượt quá
dữ liệu. Vì vậy:

- Bảng threshold cuối cùng vẫn là bảng **đăng ký trước** trong `PLAN.md` 5.1, không lấy
  threshold AI đề xuất.
- Memory ceiling báo cáo là **182,25 MB** (giá trị đo lớn nhất, tại 100C), không phải 250 MB.
- Ngưỡng bền vững là **160 VUs / 78,887 samples/s** (steady-state), kèm caveat rằng host đã
  bão hòa nên đây là giới hạn của **cấu hình đo**, không phải capacity thật của SUT.
