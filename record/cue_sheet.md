# CUE SHEET — quay 1 lần (tổng ~8:15)

**Cách dùng:** mở file này trên **điện thoại** (hoặc in ra), không mở trên màn hình đang quay.
Cột **ĐỒNG HỒ** là lúc bắt đầu cảnh. Cứ đúng cảnh, đọc phần **NÓI**, làm phần **LÀM**.

---

## TRƯỚC KHI BẤM RECORD (2 phút)

- [ ] Tắt backend cũ: `Get-NetTCPConnection -LocalPort 3100 -State Listen` → nếu có thì `Stop-Process -Id <PID> -Force`
- [ ] Xóa output cũ: `Remove-Item results\video_demo -Recurse -Force -ErrorAction SilentlyContinue`
- [ ] OBS: mic đã chọn, test nói thử, thấy thanh âm lượng nhảy
- [ ] Task Manager → Performance → chuột phải CPU → **Show logical processors**
- [ ] Mở sẵn 4 tab: Load HTML, Stress HTML, Spike HTML, GitHub Issues
- [ ] Mở sẵn VS Code: `README.md`, `Task2_AI_Analysis.md`, `docs\task3_continuous_testing.md`, `skills\jmeter-perf-testing\SKILL.md`
- [ ] Mở sẵn 3 ảnh: `screenshots\report_views\load_summary.png`, `stress_aggregate.png`, `spike_view_results_tree.png`
- [ ] 3 terminal đã `cd` đúng chỗ (A: backend, B+C: hw5)
- [ ] Bố cục: **trái = terminal/JMeter, phải = Task Manager**

---

## 0:00 — C1. Intro (25 s)

**MÀN HÌNH:** Desktop, Task Manager bên phải
**LÀM:** gõ `hostname` → Enter
**NÓI:**
> Xin chào, em là Phan Trung Tin, MSSV 23120372, bài HW05 Performance Testing.
> SUT là EShop chạy localhost port 3100. Máy đo là DESKTOP-BCS88BQ, Dell Latitude 7420,
> i5-1145G7, 4 nhân 8 luồng, RAM 16 GB, Windows 11 Pro.
> Video bắt đầu từ lúc khởi tạo backend để chứng minh toàn bộ là chạy thật.

**PHẢI THẤY:** `DESKTOP-BCS88BQ`

---

## 0:25 — C2. Khởi động backend (50 s)

**MÀN HÌNH:** Terminal A + Task Manager
**LÀM:** `node server.js` → Enter → đợi 3 dòng
**NÓI:**
> Backend là Express + SQLite. Khi khởi động, database.js tự DROP và seed lại, nên mỗi run
> đều bắt đầu sạch. Em dùng port 3100 vì 3000 đã bị app khác chiếm; đây là thay đổi của
> harness test, không phải sửa code SUT.

**PHẢI THẤY:**
```
Database initialized and seeded (Phase 2).
Server is running on http://localhost:3100
Connected to database
```
**NẾU LỖI:** `EADDRINUSE` → tắt process cũ, quay lại cảnh này.

---

## 1:15 — C3. Seed + verify (45 s)

**MÀN HÌNH:** Terminal B
**LÀM:** `python scripts\seed_perf_data.py` → Enter → rồi chạy lệnh verify
**NÓI:**
> Em seed 500 perf user, 1 lockout user, 200 sản phẩm và 0 đơn hàng.
> Verify đúng 503 user, 205 product, 0 order. Nếu orders khác 0 thì phải restart backend,
> vì cart và order là trạng thái còn lại của run trước.

**PHẢI THẤY:** `users 503` / `products 205` / `orders 0`

---

## 2:00 — C4. JMeter GUI + test plan (60 s)

**MÀN HÌNH:** JMeter GUI + Task Manager
**LÀM:** chạy lệnh mở GUI (không có `-Jcsv`):
```powershell
cmd /c C:\HCMUS\hk7\Testing\apache-jmeter-5.6.3\bin\jmeter.bat -t test-plans\23120372_Load_20261116.jmx -Jhost=localhost -Jport=3100 -Jthreads=5 -Jramp=10 -Jduration=60
```
**NÓI:**
> Đây là một workflow end-to-end dùng chung cho cả 3 scenario. CSV cấp email, password,
> product ID và order payload. Timer là GaussianRandomTimer 2000 cộng trừ 1000 ms,
> không phải delay cố định. Ba scenario dùng ba report view: Summary, Aggregate,
> View Results Tree.

**LÀM TIẾP:** chỉ lần lượt Thread Group → CSV Data Set Config → 7 request
(products → search → login → detail → cart → checkout → my-orders) → Timer → JSON Extractor → Response Assertion.
**TUYỆT ĐỐI KHÔNG Ctrl+S** (JMX đang read-only).

---

## 3:00 — C5. Live run 5 VUs / 60 s (90 s)

**MÀN HÌNH:** JMeter GUI trái, Task Manager phải, terminal monitor phía dưới
**LÀM:**
1. JMeter: chuột phải Test Plan → Add → Listener → **Summary Report**
2. Terminal C: `python scripts\monitor_resources.py --out results\video_demo\resources.csv`
3. JMeter: bấm **Start** (▶)
4. Trong 60 s: chỉ Summary Report đang tăng, chỉ Task Manager, chỉ CSV đang ghi
5. Xong: Ctrl+C ở Terminal C → chỉ dòng `Err: 0 (0.00%)`

**NÓI:**
> Đây là chạy thật 5 VUs trong 60 giây, chỉ để chứng minh pipeline hoạt động.
> Run chính thức dài hơn: Load 10 phút, Stress 12 phút, Spike 15 phút, Endurance 12 phút mỗi mức.
> Monitor ghi CSV mỗi 2 giây: CPU và RSS của backend, JMeter và toàn hệ thống.
> Các run chính thức đã có trong thư mục results.

**PHẢI THẤY:** `Err: 0 (0.00%)`. Số sample có thể dao động, miễn 0 lỗi.

---

## 4:30 — C6. Kết quả chính thức (75 s)

**MÀN HÌNH:** Browser 3 tab HTML → 3 ảnh report view → `analysis\endurance_threshold.md`
**LÀM:** chỉ số trên từng dashboard, rồi mở 3 ảnh, rồi bảng endurance
**NÓI (đọc từ file, đừng đọc theo trí nhớ):**
> Load: 8.417 samples, 0 lỗi, p95 11 ms.
> Stress: 48.735 samples, 0 lỗi, đỉnh 154,30 req/s tại 160 VUs, p95 38 ms.
> Spike: 23.809 samples, 0 lỗi, p95 17 đến 19 ms.
> Endurance: 80, 120, 160 VUs trong 720 giây, CV dưới 2,2%, p95 dưới 47 ms.
> Ngưỡng bền vững là 160 VUs, 78,89 samples/s, memory ceiling 182,25 MB.
> System CPU chạm 99,5 đến 99,7%, nên đây là giới hạn cấu hình đo, không phải capacity
> tuyệt đối của SUT.

---

## 5:45 — C7. Bugs + Task 2 + Task 3 (60 s)

**MÀN HÌNH:** GitHub Issues → VS Code `Task2_AI_Analysis.md` → flow chart
**LÀM:** chỉ 8 issue (nhấn #7 SQL injection, #8 auth) → bảng feasible/hallucinated → `docs\task3_flow.svg`
**NÓI:**
> Em tìm được 8 issue thật, 2 critical: search dính SQL injection và endpoint product không
> cần authentication. Task 2: AI đọc số rất tốt nhưng bịa nội dung file JMX và suy ra CPU
> throttle từ một trường WMI không đáng tin. Task 3 đề xuất smoke gate mỗi PR, full suite
> nightly, có phân tích trade-off chi phí và false alarm.

---

## 6:45 — C8. Demo Agent Skill (60 s)

**MÀN HÌNH:** VS Code `skills\jmeter-perf-testing\SKILL.md` + terminal
**LÀM:**
1. Chỉ cấu trúc: `SKILL.md`, `references/`, `templates/`, `scripts/`
2. Mở `references/evidence-checklist.md`
3. Chạy:
```powershell
python skills\jmeter-perf-testing\scripts\analyze_jtl.py --scenario load --jtl results\load\23120372_Load_20261116.jtl
```
4. Mở `analysis\load_summary.md` → chỉ bảng p95 theo endpoint
**NÓI:**
> Skill đóng gói toàn bộ quy trình: sinh JMX, chạy scenario, monitor tài nguyên, phân tích JTL
> và render report view. Demo chạy analyze trên chính file Load JTL đã nộp; kết quả trỏ về
> file và timestamp, không tự bịa số.

---

## 7:45 — C9. Kết thúc (30 s)

**MÀN HÌNH:** VS Code `README.md` phần self-assessment + tab repo
**LÀM:** chỉ bảng điểm và dòng ghi chú video
**NÓI:**
> Tổng kết: Task 1 tự đánh giá 63 trên 70, Task 2 9 trên 10, Task 3 9 trên 10,
> Agent Skill 8 trên 10, tổng 89 trên 100. Repo public tại
> github.com/tinphan247/HW05_AI_Performance. File nộp tên
> 23120372_HW05_AI_Performance_089.zip. Cảm ơn thầy cô và các bạn đã theo dõi.

---

# NẾU GẶP LỖI

| Lỗi | Xử lý nhanh |
|---|---|
| `EADDRINUSE` port 3100 | `Stop-Process -Id (Get-NetTCPConnection -LocalPort 3100 -State Listen).OwningProcess -Force` rồi làm lại C2 |
| `Unknown arg: .csv` | Bạn đã truyền `-Jcsv` không quote. Bỏ hẳn `-Jcsv`, hoặc bọc `"-Jcsv=data\e2e_data.csv"` |
| JMeter báo không lưu được JMX | Đúng rồi, JMX đang read-only. Chọn **Don't Save** |
| GUI chạy 30 VUs | Quên `-Jthreads=5 -Jramp=10 -Jduration=60`; đóng JMeter, chạy lại lệnh C4 |
| Monitor không ra CSV | Kiểm tra backend còn listen 3100; chạy PowerShell as Administrator |
| Seed ra orders ≠ 0 | Restart backend (không chỉ reset), rồi seed lại |

---

# SAU KHI QUAY

- [ ] Dài **≥ 6:00**
- [ ] Có ≥ 30 s thấy **JMeter + Task Manager cùng frame**
- [ ] Giọng tiếng Việt của bạn, không TTS
- [ ] Hostname `DESKTOP-BCS88BQ` hiện rõ
- [ ] Không lộ email/token/thông báo riêng tư
- [ ] Upload **Unlisted** → copy link
- [ ] Dán link vào `README.md` (mục Demo video) và `Main_Report.md` mục 8
- [ ] `python scripts\md_to_pdf.py Main_Report.md --out reports\Main_Report.pdf`
- [ ] Commit + push
- [ ] `python scripts\make_submission_zip.py --out 23120372_HW05_AI_Performance_089.zip`
