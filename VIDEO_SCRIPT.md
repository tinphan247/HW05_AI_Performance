# Video script - HW05 demo (8:00-8:30 phút, thuyết minh tiếng Việt)

> **Yêu cầu đề:** ≥ 6 phút, unlisted trên YouTube, giọng **của chính bạn** (không TTS),
> cùng một frame phải có **tool JMeter + resource monitor**, narration tiếng Việt.
> **Không** dùng video của bài khác; quay mới.

Mục tiêu của video này: chứng minh rằng toàn bộ bằng chứng trong bài là **chạy thật**,
bắt đầu từ lúc khởi tạo backend. Video chia thành 8 phần; tổng thời lượng ~8 phút.
Nếu muốn ngắn hơn, có thể bỏ phần 6 (Task 2/3) xuống 45 s, nhưng không được dưới 6 phút.

---

## 0. Chuẩn bị trước khi bấm record (5 phút)

### 0.1. Máy và màn hình

- Dùng đúng máy **DESKTOP-BCS88BQ** (hostname phải xuất hiện trong video).
- Mở **Task Manager → tab Performance** (CPU + Memory) và để nó luôn nhìn thấy.
- Tắt thông báo Windows, trình duyệt, chat. Đóng mọi app không cần thiết.
- Độ phân giải màn hình ≥ 1920×1080; OBS/Game Bar quay full desktop.
- Micro kiểm tra bằng cách nói 5 giây rồi phát lại.

### 0.2. Bố cục cửa sổ (một màn hình)

```
+--------------------------------------------------------------+
|  Top bar: hostname DESKTOP-BCS88BQ | clock | HW05 Performance |
+---------------------------+----------------------------------+
|  Trái (55%):              |  Phải (45%):                     |
|  - Terminal JMeter        |  - Task Manager (Performance)     |
|  - hoặc JMeter GUI        |  - hoặc terminal monitor_resources |
|  - hoặc browser results   |                                  |
+---------------------------+----------------------------------+
```

Quy tắc: **luôn nhìn thấy cả JMeter và Task Manager trong cùng frame**.

### 0.3. Mở sẵn trước khi quay

```powershell
# Terminal A (sẽ dùng để chạy backend)
cd C:\HCMUS\hk7\Testing\hw5\sut\eshop-sut\backend

# Terminal B (sẽ dùng để seed / verify)
cd C:\HCMUS\hk7\Testing\hw5

# Terminal C (sẽ chạy monitor)
cd C:\HCMUS\hk7\Testing\hw5
```

Mở sẵn các cửa sổ sau (chỉ mở, chưa chạy):

- `C:\HCMUS\hk7\Testing\hw5\README.md` trong VS Code hoặc browser.
- `C:\HCMUS\hk7\Testing\hw5\results\load\html\index.html`
- `C:\HCMUS\hk7\Testing\hw5\results\stress\html\index.html`
- `C:\HCMUS\hk7\Testing\hw5\results\spike\html\index.html`
- `C:\HCMUS\hk7\Testing\hw5\screenshots\report_views\load_summary.png`
- `C:\HCMUS\hk7\Testing\hw5\screenshots\report_views\stress_aggregate.png`
- `C:\HCMUS\hk7\Testing\hw5\screenshots\report_views\spike_view_results_tree.png`
- `C:\HCMUS\hk7\Testing\hw5\skills\jmeter-perf-testing\SKILL.md`

### 0.4. Lệnh sẽ dùng trong video (copy sẵn vào Notepad)

```powershell
# 1. Khởi động backend
cd C:\HCMUS\hk7\Testing\hw5\sut\eshop-sut\backend
node server.js

# 2. Seed dữ liệu (terminal khác, sau khi backend đã listen)
cd C:\HCMUS\hk7\Testing\hw5
python scripts\seed_perf_data.py

# 3. Verify counts
python -c "import sqlite3; c=sqlite3.connect(r'sut/eshop-sut/backend/database.sqlite'); print('users', c.execute('SELECT COUNT(*) FROM users').fetchone()[0]); print('products', c.execute('SELECT COUNT(*) FROM products').fetchone()[0]); print('orders', c.execute('SELECT COUNT(*) FROM orders').fetchone()[0])"

# 4. Live smoke run (5 VUs, 60 s) - monitor ở terminal khác
python scripts\monitor_resources.py --out results\video_demo\resources.csv
cmd /c C:\HCMUS\hk7\Testing\apache-jmeter-5.6.3\bin\jmeter.bat -n -t test-plans\23120372_Load_20261116.jmx -l results\video_demo\video_load.jtl -j results\video_demo\jmeter.log -Jhost=localhost -Jport=3100 -Jcsv=data\e2e_data.csv -Jthreads=5 -Jramp=10 -Jduration=60

# 5. Skill demo
python skills\jmeter-perf-testing\scripts\analyze_jtl.py --scenario load --jtl results\load\23120372_Load_20261116.jtl
```

---

## 1. Part 0 — Giới thiệu (0:00–0:30)

**Màn hình:** Desktop, hostname **DESKTOP-BCS88BQ** nhìn thấy; Task Manager mở ở góc phải.

**Narration (tiếng Việt):**

> "Xin chào, em là Phan Trung Tin, MSSV 23120372. Đây là bài HW05 Performance Testing.
> SUT là EShop chạy tại localhost port 3100. Máy đo là laptop Dell Latitude 7420,
> CPU Intel Core i5-1145G7, 4 nhân 8 luồng, RAM 16 GB, Windows 11 Pro.
> Bài có 3 test plan Load, Stress, Spike cùng một workflow end-to-end, dữ liệu CSV,
> endurance threshold, AI audit và Agent Skill. Trong video này em bắt đầu từ lúc
> khởi tạo backend để chứng minh chạy thật."

---

## 2. Part 1 — Khởi tạo backend (0:30–1:20)

**Màn hình:** Terminal A chiếm trái, Task Manager phải.

**Thao tác:**

1. Gõ lệnh `cd .../backend` (đã mở sẵn).
2. Gõ `node server.js`.
3. Đợi output:
   ```
   Database initialized and seeded (Phase 2).
   Server is running on http://localhost:3100
   Connected to database
   ```
4. Chỉ vào Task Manager: CPU và RAM backend chỉ ~vài MB.

**Narration:**

> "Backend Express + SQLite. Khi khởi động, database.js tự DROP và seed lại DB,
> nên mọi run đều bắt đầu từ trạng thái sạch. Port là 3100 vì port 3000 đã bị Aptis backend dùng;
> đây là thay đổi harness test, không phải sửa SUT."

---

## 3. Part 2 — Seed dữ liệu và verify (1:20–2:10)

**Màn hình:** Terminal B.

**Thao tác:**

1. `python scripts\seed_perf_data.py` → output `Seed complete: ...`.
2. Chạy lệnh verify counts → `users 503, products 205, orders 0`.
3. Mở browser `http://localhost:3100/api/products` (hiện JSON, 205 sản phẩm) — không bắt buộc.

**Narration:**

> "Seed 500 perf user, 1 lockout user, 200 sản phẩm, 0 đơn hàng. Verify counts khớp manifest.
> Nếu orders khác 0 thì reset lại backend."

---

## 4. Part 3 — Walkthrough JMX plan (2:10–3:00)

**Màn hình:** Mở JMeter GUI (`jmeter.bat`) + file `23120372_Load_20261116.jmx`.

**Thao tác:**

1. Mở JMeter GUI.
2. File → Open → `test-plans\23120372_Load_20261116.jmx`.
3. Chỉ các node: Thread Group, CSV Data Set Config, 7 request, Gaussian Random Timer, JSON Extractor, Response Assertion.
4. Chỉ 3 report view đã dùng: Summary Report (Load), Aggregate Report (Stress), View Results Tree (Spike) — qua ảnh `screenshots/report_views/*.png`.

> **Tuyệt đối không bấm Save / Ctrl+S trên JMX chính thức.** JMeter GUI sẽ thêm/xóa thuộc
> tính và làm SHA-256 khác manifest của run thật. Nếu cần thêm listener để quay, dùng
> **File → Save As** thành `test-plans\video_demo.jmx`, hoặc thêm listener rồi chọn
> **Don't Save** khi đóng. Đã có `.gitattributes` khóa `*.jmx` về LF để tránh lệch hash.

**Narration:**

> "Workflow end-to-end: login, products, search, product detail, cart, checkout, my-orders.
> CSV `e2e_data.csv` cho email/password/product ID/order payload. Timer ngẫu nhiên
> 2000 ± 1000 ms, không phải delay cố định. Ba report view khác nhau cho ba scenario."

---

## 5. Part 4 — Live run ngắn có monitor (3:00–4:20)

**Màn hình:** Trái = Terminal JMeter + terminal monitor; phải = Task Manager.

**Thao tác:**

1. Terminal monitor: `python scripts\monitor_resources.py --out results\video_demo\resources.csv`
2. Terminal JMeter: lệnh smoke ở §0.4 bước 4.
3. Trong lúc chạy (60 s): chỉ vào Task Manager khi CPU/RSS backend tăng.
4. Khi kết thúc, monitor Ctrl+C, JMeter báo `summary = ... in ...s`.

**Narration:**

> "Đây là chạy thật, 5 VUs trong 60 giây, để chứng minh pipeline chạy được.
> Run chính thức dài hơn: Load 10 phút, Stress 12 phút, Spike 15 phút, Endurance 12 phút mỗi mức.
> Monitor ghi CSV mỗi 2 giây: CPU/RSS của backend, JMeter và system."

---

## 6. Part 5 — Kết quả chính thức (4:20–5:40)

**Màn hình:** Browser mở HTML dashboard + ảnh report view + terminal `manifest.md`.

**Thao tác:**

1. Mở `results\load\html\index.html` → chỉ dashboard, RPS, p95, error.
2. Mở `results\stress\html\index.html` → chỉ S1–S6 và p95.
3. Mở `results\spike\html\index.html` → chỉ spike 10→100 VUs.
4. Mở 3 ảnh `screenshots/report_views/*.png` (Summary/Aggregate/View Results Tree).
5. Chỉ `analysis/endurance_threshold.md`: 3 mức 80/120/160 VUs, tất cả PASS.

**Narration (đọc số từ manifest, không nói theo nhớ):**

> "Load: 8.417 samples, 0 lỗi, p95 11 ms. Stress: 48.735 samples, 0 lỗi,
> đỉnh 154,30 req/s tại 160 VUs, p95 38 ms. Spike: 23.809 samples, 0 lỗi,
> p95 17–19 ms. Endurance: 80, 120, 160 VUs trong 720 s, CV dưới 2,2%,
> p95 dưới 47 ms. Ngưỡng bền vững là 160 VUs – 78,89 samples/s,
> memory ceiling 182,25 MB. System CPU chạm 99,5–99,7%, nên đây là giới hạn
> của cấu hình đo, không phải capacity tuyệt đối của SUT."

---

## 7. Part 6 — Bugs + Task 2/3 (5:40–6:40)

**Màn hình:** Browser mở GitHub Issues + `Task2_AI_Analysis.md` + `docs/task3_continuous_testing.md`.

**Thao tác:**

1. Mở `https://github.com/tinphan247/HW05_AI_Performance/issues` → chỉ 8 issue, #7 và #8 critical.
2. Mở `Task2_AI_Analysis.md` → chỉ bảng feasible/hallucinated và ví dụ AI bịa JMX.
3. Mở flow chart `docs/task3_flow.svg`.

**Narration:**

> "Tìm được 8 issue thật, trong đó 2 critical: SQL injection ở search và
> endpoint product không cần auth. AI đọc số rất tốt nhưng bịa nội dung file JMX
> và suy CPU throttle từ một trường WMI sai. Task 3 đề xuất smoke gate mỗi PR,
> full suite nightly, trade-off chi phí và false alarm."

---

## 8. Part 7 — Agent Skill demo (6:40–7:40)

**Màn hình:** VS Code mở `skills/jmeter-perf-testing/SKILL.md` + terminal chạy analyze.

**Thao tác:**

1. Mở `skills\jmeter-perf-testing\SKILL.md` → chỉ workflow, references, templates.
2. Terminal: `python skills\jmeter-perf-testing\scripts\analyze_jtl.py --scenario load --jtl results\load\23120372_Load_20261116.jtl`
3. Mở `analysis\load_summary.md` → chỉ per-label p95 và error code.
4. Chỉ `skills\jmeter-perf-testing\scripts\generate_jmx.py` trong tree.

**Narration:**

> "Skill đóng gói toàn bộ quy trình: sinh JMX, chạy scenario, monitor, phân tích JTL,
> render report view. Demo chạy analyze trên chính file Load JTL đã nộp,
> kết quả trỏ về file và timestamp, không invent số."

---

## 9. Part 8 — Kết thúc (7:40–8:20)

**Màn hình:** README.md (bảng self-assessment) + repo GitHub.

**Narration:**

> "Tổng kết: Task 1 tự đánh giá 63/70, Task 2 9/10, Task 3 9/10, Agent Skill 8/10,
> tổng 89/100; trừ điểm vì chưa có video và bài cá nhân. Repo public tại
> github.com/tinphan247/HW05_AI_Performance. Zip tên 23120372_HW05_AI_Performance_089.zip.
> Cảm ơn thầy/cô và các bạn đã theo dõi."

---

## Checklist sau khi quay

- [ ] Thời lượng ≥ 6:00 (đếm từ OBS).
- [ ] Có ít nhất 1 đoạn ≥ 30 s cùng frame **JMeter + Task Manager**.
- [ ] Giọng tiếng Việt của bạn, không TTS.
- [ ] Hostname **DESKTOP-BCS88BQ** xuất hiện rõ.
- [ ] Không có thông báo riêng tư, email, token.
- [ ] Upload **Unlisted**, copy link.
- [ ] Dán link vào `README.md` (mục Demo video) và `Main_Report.md` mục 8.
- [ ] Tạo lại `reports/Main_Report.pdf`, commit/push, tạo lại zip.

## Ghi chú trung thực

- Live run ở Part 4 chỉ là **demo pipeline** (5 VUs, 60 s), **không** phải run chính thức;
  run chính thức là các file `.jtl` 10–15 phút trong `results/`. Phải nói rõ điều này trong narration
  để không bị hiểu là thay thế bằng chứng.
- Nếu backend chưa chạy thì seed sẽ fail; luôn start backend trước.
- Nếu port 3100 bị chiếm, kill process cũ trước khi quay (`netstat -ano | findstr :3100`).
- Nếu OBS không quay được âm thanh, dùng Game Bar (Win+G) hoặc ffmpeg; kiểm tra micro trước.
- Nếu PowerShell báo `Unknown arg: .csv`, nguyên nhân là gọi `jmeter.bat` trực tiếp với
  `-Jcsv=data/e2e_data.csv`. Dùng `cmd /c` và đường dẫn `data\e2e_data.csv` như lệnh mẫu.
- Không nói số liệu không có trong manifest; mở file và đọc trực tiếp.
