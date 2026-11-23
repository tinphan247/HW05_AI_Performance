# CUE SHEET 6:10 — quay 1 lần

**Mở trên điện thoại, không mở trên màn hình đang quay.**
Bản đầy đủ 8:15 nằm ở `VIDEO_SCRIPT.md`; file này là bản rút gọn để quay nhanh.

Tổng: **6:15** (dư 15 s so với mức tối thiểu 6:00). Nếu bị chậm, xem mục **CẮT BỚT** ở cuối.

---

## TRƯỚC KHI RECORD (2 phút)

- [ ] Tắt backend cũ: `Get-NetTCPConnection -LocalPort 3100 -State Listen` → có thì `Stop-Process -Id <PID> -Force`
- [ ] `Remove-Item results\video_demo -Recurse -Force -ErrorAction SilentlyContinue`
- [ ] OBS: mic `Realtek Audio`, nói thử thấy thanh nhảy; format **mkv**, 1080p30
- [ ] Task Manager → Performance → chuột phải CPU → **Show logical processors**
- [ ] 4 tab: Load HTML, Stress HTML, Spike HTML, GitHub Issues
- [ ] VS Code: `README.md`, `Task2_AI_Analysis.md`, `docs\task3_continuous_testing.md`, `skills\jmeter-perf-testing\SKILL.md`
- [ ] 3 ảnh: `load_summary.png`, `stress_aggregate.png`, `spike_view_results_tree.png`
- [ ] 3 terminal đã `cd` (A: backend, B+C: hw5)
- [ ] Bố cục: **trái terminal/JMeter — phải Task Manager**

---

## 0:00 — C1. Intro (20 s)

**MÀN HÌNH:** Desktop + Task Manager
**LÀM:** `hostname` → Enter

**NÓI:**
> Em là Phan Trung Tin, MSSV 23120372, bài HW05 Performance Testing. SUT là EShop chạy
> localhost port 3100. Máy đo DESKTOP-BCS88BQ: i5-1145G7, 4 nhân 8 luồng, 16 GB RAM,
> Windows 11. Video bắt đầu từ lúc khởi tạo backend để chứng minh chạy thật.

**THẤY:** `DESKTOP-BCS88BQ`

---

## 0:20 — C2. Khởi động backend (35 s)

**MÀN HÌNH:** Terminal A + Task Manager
**LÀM:** `node server.js` → Enter → đợi đủ 3 dòng

**NÓI:**
> Backend là Express + SQLite. Khi khởi động, database.js tự DROP và seed lại nên mỗi run
> bắt đầu sạch. Em dùng port 3100 vì 3000 bị app khác chiếm — đây là thay đổi của harness
> test, không sửa code SUT.

**THẤY:**
```
Database initialized and seeded (Phase 2).
Server is running on http://localhost:3100
Connected to database
```
**LỖI:** `EADDRINUSE` → tắt process cũ, làm lại cảnh này.

---

## 0:55 — C3. Seed + verify (30 s)

**MÀN HÌNH:** Terminal B
**LÀM:** `python scripts\seed_perf_data.py` → Enter → chạy lệnh verify

**NÓI:**
> Em seed 500 perf user, 1 lockout user, 200 sản phẩm, 0 đơn hàng. Verify đúng 503 user,
> 205 product, 0 order. Orders khác 0 thì phải restart backend vì cart còn từ run trước.

**THẤY:** `users 503` / `products 205` / `orders 0`

---

## 1:25 — C4. JMeter GUI + test plan (50 s)

**MÀN HÌNH:** JMeter GUI + Task Manager
**LÀM:** chạy lệnh mở GUI (không `-Jcsv`):
```powershell
cmd /c C:\HCMUS\hk7\Testing\apache-jmeter-5.6.3\bin\jmeter.bat -t test-plans\23120372_Load_20261116.jmx -Jhost=localhost -Jport=3100 -Jthreads=5 -Jramp=10 -Jduration=60
```
**LÀM TIẾP:** chỉ nhanh Thread Group → CSV Data Set Config → 7 request → Timer → JSON Extractor → Response Assertion.
**KHÔNG Ctrl+S** (JMX đang read-only).

**NÓI:**
> Một workflow end-to-end dùng chung cho cả ba scenario: products, search, login, product
> detail, cart, checkout, my-orders. CSV cấp email, password, product ID. Timer Gaussian
> 2000 cộng trừ 1000 ms, không phải delay cố định. Ba scenario dùng ba report view khác
> nhau: Summary, Aggregate, View Results Tree.

---

## 2:15 — C5. Live run 5 VUs / 60 s (85 s)

**MÀN HÌNH:** JMeter trái — Task Manager phải — terminal monitor dưới
**LÀM:**
1. JMeter: chuột phải Test Plan → Add → Listener → **Summary Report**
2. Terminal C: `python scripts\monitor_resources.py --out results\video_demo\resources.csv`
3. Bấm **Start** (▶)
4. Trong lúc chạy: chỉ Summary Report đang tăng, chỉ Task Manager, chỉ CSV đang ghi
5. Xong: Ctrl+C ở Terminal C → chỉ dòng `Err: 0 (0.00%)`

**NÓI (khi bấm Start):**
> Đây là chạy thật 5 VUs trong 60 giây để chứng minh pipeline hoạt động. Run chính thức dài
> hơn: Load 10 phút, Stress 12, Spike 15, Endurance 12 phút mỗi mức. Monitor ghi CSV mỗi
> 2 giây: CPU và RSS của backend, JMeter và toàn hệ thống. Bên phải là Task Manager cùng frame.

**NÓI (khi đang chạy, ~15 s):**
> Summary Report đang tăng sample, hiện Err 0.

---

## 3:40 — C6. Kết quả chính thức (55 s)

**MÀN HÌNH:** 3 tab HTML → 3 ảnh report view → `analysis\endurance_threshold.md`
**LÀM:** chỉ số trên từng dashboard, mở 3 ảnh, chỉ bảng endurance

**NÓI (đọc từ file, không đọc theo trí nhớ):**
> Load: 8.417 samples, 0 lỗi, p95 11 ms. Stress: 48.735 samples, 0 lỗi, đỉnh 154,30 req/s
> tại 160 VUs, p95 38 ms. Spike: 23.809 samples, 0 lỗi, p95 17 đến 19 ms. Endurance 80,
> 120, 160 VUs trong 720 giây, CV dưới 2,2%, p95 dưới 47 ms. Ngưỡng bền vững là 160 VUs,
> 78,89 samples/s, memory ceiling 182,25 MB. System CPU chạm 99,5 đến 99,7%, nên đây là
> giới hạn của cấu hình đo, không phải capacity tuyệt đối của SUT.

---

## 4:35 — C7. Bugs + Task 2 + Task 3 (45 s)

**MÀN HÌNH:** GitHub Issues → `Task2_AI_Analysis.md` → `docs\task3_flow.svg`
**LÀM:** chỉ 8 issue (nhấn #7, #8) → bảng feasible/hallucinated → flow chart

**NÓI:**
> Em tìm được 8 issue thật, 2 critical: search dính SQL injection và endpoint product không
> cần authentication. Task 2: AI đọc số tốt nhưng bịa nội dung file JMX và suy ra CPU
> throttle từ một trường WMI không đáng tin. Task 3: smoke gate mỗi PR, full suite nightly,
> có phân tích trade-off chi phí và false alarm.

---

## 5:20 — C8. Demo Agent Skill (35 s)

**MÀN HÌNH:** `skills\jmeter-perf-testing\SKILL.md` + terminal
**LÀM:**
1. Chỉ cấu trúc `SKILL.md`, `references/`, `templates/`, `scripts/`
2. Chạy:
```powershell
python skills\jmeter-perf-testing\scripts\analyze_jtl.py --scenario load --jtl results\load\23120372_Load_20261116.jtl
```
3. Mở `analysis\load_summary.md` → chỉ bảng p95 theo endpoint

**NÓI:**
> Skill đóng gói toàn bộ quy trình: sinh JMX, chạy scenario, monitor tài nguyên, phân tích
> JTL và render report view. Demo chạy analyze trên chính file Load JTL đã nộp; kết quả trỏ
> về file và timestamp, không tự bịa số.

---

## 5:55 — C9. Kết thúc (20 s)

**MÀN HÌNH:** `README.md` phần self-assessment + tab repo
**LÀM:** chỉ bảng điểm

**NÓI:**
> Tổng kết: Task 1 tự đánh giá 63 trên 70, Task 2 9 trên 10, Task 3 9 trên 10, Agent Skill
> 8 trên 10, tổng 89 trên 100. Repo github.com/tinphan247/HW05_AI_Performance. File nộp
> 23120372_HW05_AI_Performance_089.zip. Cảm ơn thầy cô đã theo dõi.

---

# NẾU CHẠY QUÁ GIỜ — CẮT THEO THỨ TỰ NÀY

1. Bỏ phần "chỉ từng endpoint" ở C6, chỉ nói số tổng (tiết kiệm ~15 s).
2. Ở C7, bỏ câu Task 3 (~10 s).
3. Ở C4, không mở từng node, chỉ nói tên 7 request (~10 s).
4. **Không cắt** C5 (bắt buộc thấy JMeter + Task Manager) và C8 (demo Skill là mục riêng).

# NẾU GẶP LỖI

| Lỗi | Xử lý |
|---|---|
| `EADDRINUSE` port 3100 | `Stop-Process -Id (Get-NetTCPConnection -LocalPort 3100 -State Listen).OwningProcess -Force` rồi làm lại C2 |
| `Unknown arg: .csv` | Đã truyền `-Jcsv` không quote. Bỏ hẳn `-Jcsv` hoặc bọc `"-Jcsv=data\e2e_data.csv"` |
| JMeter không lưu được JMX | Đúng, JMX read-only. Chọn **Don't Save** |
| GUI chạy 30 VUs | Thiếu `-Jthreads=5 -Jramp=10 -Jduration=60`; đóng JMeter, chạy lại lệnh C4 |
| Monitor không ra CSV | Backend phải còn listen 3100; chạy PowerShell as Administrator |
| Seed ra orders ≠ 0 | Restart backend (không chỉ reset), seed lại |

---

# SAU KHI QUAY

- [ ] Dài **≥ 6:00**
- [ ] ≥ 30 s thấy **JMeter + Task Manager cùng frame**
- [ ] Giọng bạn, không TTS
- [ ] Hostname `DESKTOP-BCS88BQ` rõ
- [ ] Không lộ email/token
- [ ] Upload **Unlisted** → copy link
- [ ] Gửi link để cập nhật `README.md` + `Main_Report.md` §8, regen PDF, commit, rebuild zip
