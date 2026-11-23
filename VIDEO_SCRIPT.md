# VIDEO_SCRIPT - HW05 Performance Testing (8:00-8:30)

**Sinh viên:** Phan Trung Tin - 23120372
**Máy quay:** DESKTOP-BCS88BQ (Dell Latitude 7420, i5-1145G7, 16 GB, Windows 11 Pro)
**Yêu cầu:** ≥ 6 phút, unlisted YouTube, giọng tiếng Việt của chính bạn, **JMeter + resource monitor
trong cùng một frame**.

> Tài liệu này là hướng dẫn thao tác từng bước. Cứ làm tuần tự từ trên xuống, không cần nhớ gì.
> Các số trong ngoặc là thời lượng mục tiêu; tổng ~8:15.

---

# PHẦN A - CHUẨN BỊ TRƯỚC KHI BẤM RECORD

## A1. Kiểm tra port 3100 và backend cũ

Mở **PowerShell** tại `C:\HCMUS\hk7\Testing\hw5`:

```powershell
Get-NetTCPConnection -LocalPort 3100 -State Listen -ErrorAction SilentlyContinue
```

- Nếu **không có kết quả**: tốt, port đang trống.
- Nếu **có PID**: tắt backend cũ trước khi quay để cảnh khởi động là thật:

```powershell
$c = Get-NetTCPConnection -LocalPort 3100 -State Listen
Stop-Process -Id $c.OwningProcess -Force
```

## A2. Xóa output demo cũ (để cảnh chạy là mới)

```powershell
Remove-Item results\video_demo -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path results\video_demo | Out-Null
```

## A3. Mở sẵn các cửa sổ (chưa thao tác)

Mở theo đúng thứ tự này:

1. **Terminal A** (backend):
   ```powershell
   cd C:\HCMUS\hk7\Testing\hw5\sut\eshop-sut\backend
   ```
2. **Terminal B** (seed/verify):
   ```powershell
   cd C:\HCMUS\hk7\Testing\hw5
   ```
3. **Terminal C** (monitor):
   ```powershell
   cd C:\HCMUS\hk7\Testing\hw5
   ```
4. **Task Manager** → tab **Performance** → chuột phải CPU graph → **Show logical processors**.
5. **Chrome/Edge** mở sẵn 4 tab:
   - `results\load\html\index.html`
   - `results\stress\html\index.html`
   - `results\spike\html\index.html`
   - `https://github.com/tinphan247/HW05_AI_Performance/issues`
6. **VS Code** mở sẵn:
   - `README.md`
   - `Task2_AI_Analysis.md`
   - `docs\task3_continuous_testing.md`
   - `skills\jmeter-perf-testing\SKILL.md`
7. Mở sẵn 3 ảnh report view:
   - `screenshots\report_views\load_summary.png`
   - `screenshots\report_views\stress_aggregate.png`
   - `screenshots\report_views\spike_view_results_tree.png`

## A4. Bố cục màn hình khi quay

```
+--------------------------------------------------------------+
|  Hostname DESKTOP-BCS88BQ (mở PowerShell gõ hostname)         |
+---------------------------+----------------------------------+
|  TRÁI 55%                 |  PHẢI 45%                        |
|  Terminal / JMeter GUI    |  Task Manager (Performance)       |
|  hoặc browser kết quả     |  hoặc terminal monitor            |
+---------------------------+----------------------------------+
```

Quy tắc bắt buộc: **JMeter và Task Manager luôn nằm trong cùng frame** ở cảnh live run.

## A5. Lệnh copy sẵn (dán vào Notepad để quay nhanh)

```powershell
# 1. Backend
cd C:\HCMUS\hk7\Testing\hw5\sut\eshop-sut\backend
node server.js

# 2. Seed
cd C:\HCMUS\hk7\Testing\hw5
python scripts\seed_perf_data.py

# 3. Verify
python -c "import sqlite3; c=sqlite3.connect(r'sut/eshop-sut/backend/database.sqlite'); print('users', c.execute('SELECT COUNT(*) FROM users').fetchone()[0]); print('products', c.execute('SELECT COUNT(*) FROM products').fetchone()[0]); print('orders', c.execute('SELECT COUNT(*) FROM orders').fetchone()[0])"

# 4. Monitor
python scripts\monitor_resources.py --out results\video_demo\resources.csv

# 5. JMeter GUI (5 VUs, 60 s) - dùng cmd /c, KHÔNG gọi .bat trực tiếp
cmd /c C:\HCMUS\hk7\Testing\apache-jmeter-5.6.3\bin\jmeter.bat -t test-plans\23120372_Load_20261116.jmx -Jhost=localhost -Jport=3100 -Jcsv=data\e2e_data.csv -Jthreads=5 -Jramp=10 -Jduration=60

# 6. Skill demo
python skills\jmeter-perf-testing\scripts\analyze_jtl.py --scenario load --jtl results\load\23120372_Load_20261116.jtl
```

---

# PHẦN B - KỊCH BẢN QUAY TỪNG CẢNH

## Cảnh 1 - Intro (0:00-0:25)

**Màn hình:** Desktop, mở PowerShell gõ `hostname` để thấy `DESKTOP-BCS88BQ`; Task Manager mở bên phải.

**Thao tác:**
1. Bấm record.
2. Gõ `hostname` → Enter.
3. Chỉ vào tên máy, rồi chỉ Task Manager.

**Lời thoại:**

> "Xin chào, em là Phan Trung Tin, MSSV 23120372. Đây là bài HW05 Performance Testing.
> SUT là EShop, chạy localhost port 3100. Máy đo là DESKTOP-BCS88BQ, Dell Latitude 7420,
> Intel Core i5-1145G7, 4 nhân 8 luồng, RAM 16 GB, Windows 11 Pro.
> Video này em bắt đầu từ lúc khởi tạo backend để chứng minh toàn bộ là chạy thật."

---

## Cảnh 2 - Khởi động backend (0:25-1:15)

**Màn hình:** Terminal A bên trái, Task Manager bên phải.

**Thao tác:**
1. Chuyển sang Terminal A.
2. Gõ `node server.js` → Enter.
3. Đợi đến khi thấy đủ 3 dòng:
   ```
   Database initialized and seeded (Phase 2).
   Server is running on http://localhost:3100
   Connected to database
   ```
4. Chỉ vào Task Manager: process Node chiếm RAM rất ít (~50 MB).

**Lời thoại:**

> "Backend là Express + SQLite. Khi khởi động, file database.js tự DROP và seed lại database,
> nên mỗi run đều bắt đầu từ trạng thái sạch. Em dùng port 3100 vì port 3000 đã bị Aptis backend
> chiếm; đây là thay đổi của harness test, không phải sửa code SUT."

**Kiểm tra:** nếu terminal báo `EADDRINUSE`, quay lại A1 tắt process cũ rồi làm lại cảnh này.

---

## Cảnh 3 - Seed và verify dữ liệu (1:15-2:00)

**Màn hình:** Terminal B.

**Thao tác:**
1. Chuyển sang Terminal B.
2. Chạy `python scripts\seed_perf_data.py` → Enter.
3. Đợi dòng:
   ```
   Seed complete: {'users': 503, 'perf_users': 500, 'products': 205, 'perf_products': 200, 'orders': 0}
   ```
4. Chạy lệnh verify → Enter.
5. Đợi 3 dòng: `users 503`, `products 205`, `orders 0`.

**Lời thoại:**

> "Em seed 500 perf user, 1 lockout user, 200 sản phẩm và 0 đơn hàng.
> Verify lại đúng 503 user, 205 product, 0 order. Nếu orders khác 0 thì phải restart backend
> vì cart và order là trạng thái của run trước."

---

## Cảnh 4 - Mở JMeter GUI và xem test plan (2:00-3:00)

**Màn hình:** JMeter GUI bên trái, Task Manager bên phải.

**Thao tác:**
1. Mở **Terminal B** (hoặc PowerShell mới).
2. Chạy lệnh GUI đã copy sẵn ở A5 bước 5:
   ```powershell
   cmd /c C:\HCMUS\hk7\Testing\apache-jmeter-5.6.3\bin\jmeter.bat -t test-plans\23120372_Load_20261116.jmx -Jhost=localhost -Jport=3100 -Jcsv=data\e2e_data.csv -Jthreads=5 -Jramp=10 -Jduration=60
   ```
3. JMeter GUI mở với plan đã load.
4. Chỉ lần lượt các node:
   - **Thread Group**: `Load - ${__P(threads,30)} VUs`
   - **CSV Data Set Config**: trỏ `data/e2e_data.csv`
   - **7 request**: products → search → login → product detail → cart → checkout → my-orders
   - **Gaussian Random Timer**: 2000 ± 1000 ms
   - **JSON Extractor**: lấy token sau login
   - **Response Assertion**: kiểm tra body
5. **Không bấm Save / Ctrl+S.**

> **CẢNH BÁO:** JMeter GUI sẽ thêm/xóa thuộc tính XML và làm SHA-256 của JMX khác manifest
> của run chính thức. Năm file JMX chính thức đã được đặt **read-only** để GUI không ghi đè.
> Nếu cần thêm listener, thêm xong chọn **Don't Save** khi đóng. Nếu muốn lưu, dùng
> **File → Save As** thành `test-plans\video_demo.jmx`.

**Lời thoại:**

> "Đây là một workflow end-to-end dùng chung cho cả 3 scenario. CSV cung cấp email, password,
> product ID và order payload. Timer là GaussianRandomTimer 2000 cộng trừ 1000 ms,
> không phải delay cố định. Ba scenario dùng ba report view khác nhau: Summary Report,
> Aggregate Report và View Results Tree."

---

## Cảnh 5 - Live run có Task Manager cùng frame (3:00-4:30)

**Màn hình:** Trái = JMeter GUI, phải = Task Manager (Performance). Terminal monitor đặt phía dưới.

**Thao tác:**
1. Trong JMeter GUI, chuột phải **Test Plan** → **Add** → **Listener** → **Summary Report**.
2. Sắp xếp để thấy **JMeter + Task Manager** cùng lúc.
3. Terminal C: chạy monitor:
   ```powershell
   python scripts\monitor_resources.py --out results\video_demo\resources.csv
   ```
4. Quay lại JMeter, bấm **Start** (nút ▶ xanh).
5. Trong 60 giây:
   - Chỉ vào **Summary Report** đang cập nhật số sample.
   - Chỉ vào **Task Manager**: CPU backend tăng nhẹ, RAM ~50-60 MB.
   - Chỉ vào terminal monitor: file CSV đang được ghi.
6. Khi JMeter báo `... end of run`, chuyển sang Terminal C, bấm **Ctrl+C** để dừng monitor.
7. Chỉ dòng cuối trong Summary Report: `Err: 0 (0.00%)`.

**Lời thoại:**

> "Đây là chạy thật 5 VUs trong 60 giây, chỉ để chứng minh pipeline hoạt động.
> Run chính thức dài hơn: Load 10 phút, Stress 12 phút, Spike 15 phút,
> Endurance 12 phút mỗi mức. Monitor ghi CSV mỗi 2 giây: CPU và RSS của backend,
> JMeter và toàn hệ thống. Các run chính thức đã có sẵn trong thư mục results."

**Kiểm tra (lần chạy thử 23/11):** 129 samples, 0 lỗi, 100% HTTP 200, 16 đơn hàng,
max 96 ms, backend RSS ~53 MB. Số của bạn có thể dao động; miễn `Err: 0`.

---

## Cảnh 6 - Kết quả chính thức (4:30-5:45)

**Màn hình:** Chrome/Edge, lần lượt các tab HTML dashboard; sau đó mở 3 ảnh report view.

**Thao tác:**
1. Tab **Load** → chỉ dashboard: samples, throughput, p95, error.
2. Tab **Stress** → chỉ bảng S1-S6, p95 từng mức.
3. Tab **Spike** → chỉ đoạn spike 10 → 100 VUs.
4. Mở `screenshots\report_views\load_summary.png` → chỉ Summary Report.
5. Mở `stress_aggregate.png` → chỉ Aggregate Report.
6. Mở `spike_view_results_tree.png` → chỉ View Results Tree với sample 200 OK.
7. Mở `analysis\endurance_threshold.md` → chỉ bảng 3 mức và dòng kết luận.

**Lời thoại (đọc số từ manifest, không đọc theo trí nhớ):**

> "Load: 8.417 samples, 0 lỗi, p95 11 ms. Stress: 48.735 samples, 0 lỗi,
> đỉnh 154,30 req/s tại 160 VUs, p95 38 ms. Spike: 23.809 samples, 0 lỗi,
> p95 17 đến 19 ms. Endurance: 80, 120, 160 VUs trong 720 giây, CV dưới 2,2%,
> p95 dưới 47 ms. Ngưỡng bền vững là 160 VUs, 78,89 samples/s,
> memory ceiling 182,25 MB. System CPU chạm 99,5 đến 99,7%, nên đây là giới hạn
> của cấu hình đo, không phải capacity tuyệt đối của SUT."

---

## Cảnh 7 - Bugs, Task 2, Task 3 (5:45-6:45)

**Màn hình:** Chrome tab GitHub Issues; VS Code mở `Task2_AI_Analysis.md` và flow chart.

**Thao tác:**
1. Tab GitHub Issues → chỉ 8 issue, nhấn mạnh #7 (SQL injection) và #8 (auth).
2. VS Code `Task2_AI_Analysis.md` → chỉ bảng feasible / cần thêm dữ liệu / không khả thi / hallucinated.
3. Chỉ đoạn AI bịa nội dung JMX và đoạn AI suy CPU throttle từ WMI.
4. Mở `docs\task3_continuous_testing.md` và `docs\task3_flow.svg` → chỉ flow chart.

**Lời thoại:**

> "Em tìm được 8 issue thật, trong đó 2 critical: search dính SQL injection và
> endpoint product không cần authentication. Ở Task 2, AI đọc số rất tốt nhưng bịa nội dung
> file JMX và suy ra CPU throttle từ một trường WMI không đáng tin. Task 3 đề xuất smoke gate
> mỗi PR, full suite nightly, có phân tích trade-off chi phí và false alarm."

---

## Cảnh 8 - Demo Agent Skill (6:45-7:45)

**Màn hình:** VS Code mở `skills\jmeter-perf-testing\SKILL.md`; terminal bên cạnh.

**Thao tác:**
1. Chỉ cấu trúc skill: `SKILL.md`, `references/`, `templates/`, `scripts/`.
2. Mở `references/evidence-checklist.md` → chỉ checklist bằng chứng.
3. Chạy:
   ```powershell
   python skills\jmeter-perf-testing\scripts\analyze_jtl.py --scenario load --jtl results\load\23120372_Load_20261116.jtl
   ```
4. Mở `analysis\load_summary.md` → chỉ bảng per-label p95 và error code.
5. Chỉ `skills\jmeter-perf-testing\scripts\generate_jmx.py` trong cây thư mục.

**Lời thoại:**

> "Skill đóng gói toàn bộ quy trình: sinh JMX, chạy scenario, monitor tài nguyên,
> phân tích JTL và render report view. Demo chạy analyze trên chính file Load JTL đã nộp;
> kết quả trỏ về file và timestamp, không tự bịa số."

---

## Cảnh 9 - Kết thúc (7:45-8:15)

**Màn hình:** VS Code `README.md` phần self-assessment + tab GitHub repo.

**Thao tác:**
1. Chỉ bảng self-assessment: 27 + 18 + 18 + 9 + 9 + 8 = 89.
2. Chỉ dòng ghi chú video và lý do trừ điểm.
3. Chỉ repo `github.com/tinphan247/HW05_AI_Performance`.

**Lời thoại:**

> "Tổng kết: Task 1 tự đánh giá 63 trên 70, Task 2 9 trên 10, Task 3 9 trên 10,
> Agent Skill 8 trên 10, tổng 89 trên 100. Repo public tại
> github.com/tinphan247/HW05_AI_Performance. File nộp tên
> 23120372_HW05_AI_Performance_089.zip. Cảm ơn thầy cô và các bạn đã theo dõi."

---

# PHẦN C - CHECKLIST SAU KHI QUAY

- [ ] Video dài **≥ 6:00** (đếm trong OBS/YouTube).
- [ ] Có ít nhất **30 giây** thấy JMeter + Task Manager cùng frame.
- [ ] Giọng tiếng Việt của bạn, không TTS.
- [ ] Hostname **DESKTOP-BCS88BQ** hiện rõ.
- [ ] Không lộ email, token, thông báo riêng tư.
- [ ] Upload **Unlisted**, copy link.
- [ ] Dán link vào `README.md` (mục Demo video) và `Main_Report.md` mục 8.
- [ ] Chạy lại `python scripts\md_to_pdf.py Main_Report.md --out reports\Main_Report.pdf`.
- [ ] Commit/push, tạo lại zip bằng `python scripts\make_submission_zip.py --out 23120372_HW05_AI_Performance_089.zip`.

---

# PHẦN D - LỖI ĐÃ GẶP KHI CHẠY THỬ 23/11 VÀ CÁCH SỬA

## D1. `Unknown arg: .csv`

**Hiện tượng:** gọi trực tiếp `C:\...\jmeter.bat ... -Jcsv=data/e2e_data.csv` trong PowerShell,
JMeter báo:

```
Setting JMeter property: csv=data/e2e_data
An error occurred: Unknown arg: .csv
```

**Nguyên nhân:** PowerShell tách tham số `-Jcsv=data/e2e_data.csv` không đúng khi gọi file `.bat`.

**Cách đúng:**

```powershell
cmd /c C:\HCMUS\hk7\Testing\apache-jmeter-5.6.3\bin\jmeter.bat -n -t test-plans\23120372_Load_20261116.jmx -l results\video_demo\video_load.jtl -j results\video_demo\jmeter.log -Jhost=localhost -Jport=3100 -Jcsv=data\e2e_data.csv -Jthreads=5 -Jramp=10 -Jduration=60
```

Dùng `cmd /c` và đường dẫn **`data\e2e_data.csv`** (backslash).

## D2. JMeter GUI lưu đè JMX

**Hiện tượng:** sau khi mở/save trong GUI, SHA-256 của `23120372_Load_20261116.jmx` khác
manifest của run chính thức (`530985...`), vì GUI thêm/xóa thuộc tính XML.

**Cách sửa:**
1. Không bấm Save/Ctrl+S trên JMX chính thức.
2. Năm file JMX chính thức đã được đặt **read-only**; nếu JMeter báo không lưu được, đó là
   hành vi mong muốn. Nếu cần listener, chọn **Don't Save** khi đóng, hoặc **Save As**
   `test-plans\video_demo.jmx`.
3. Khôi phục bản gốc nếu lỡ lưu:
   ```powershell
   git checkout -- test-plans\23120372_Load_20261116.jmx
   ```
4. Kiểm tra hash khớp manifest:
   ```powershell
   python -c "import hashlib,pathlib; print(hashlib.sha256(pathlib.Path(r'test-plans/23120372_Load_20261116.jmx').read_bytes()).hexdigest())"
   ```
   Phải ra `530985258d2e8b0aec1e0a11247a83a5997c3b9c3cd78d32e9f0e8f6e66ac801`.
   Nếu ra hash khác do CRLF, chuyển file về LF (đã có `.gitattributes` khóa `*.jmx`).
5. Nếu cần sửa JMX để thử nghiệm, bỏ read-only trước:
   ```powershell
   Set-ItemProperty -Path test-plans\23120372_Load_20261116.jmx -Name IsReadOnly -Value $false
   ```

## D3. Port 3100 bận

```powershell
Get-NetTCPConnection -LocalPort 3100 -State Listen
Stop-Process -Id (Get-NetTCPConnection -LocalPort 3100 -State Listen).OwningProcess -Force
```

## D4. Seed xong nhưng counts sai

- Phải **start backend trước**, đợi `Server is running...` rồi mới seed.
- Nếu orders khác 0: restart backend (không chỉ reset), rồi seed lại.

## D5. JMeter GUI chạy 30 VUs thay vì 5

- Quên `-Jthreads=5 -Jramp=10 -Jduration=60` khi mở GUI.
- Đóng JMeter, chạy lại đúng lệnh ở A5 bước 5.

## D6. Monitor không ghi được CSV

- Kiểm tra backend đang listen port 3100.
- Chạy PowerShell **as Administrator** nếu psutil bị `AccessDenied`.
- Dừng monitor bằng **Ctrl+C**, không đóng cửa sổ bằng nút X (có thể mất sample cuối).

---

# PHẦN E - GHI CHÚ TRUNG THỰC

- Cảnh 5 là **demo pipeline** 5 VUs / 60 s, **không phải** run chính thức. Phải nói rõ trong
  narration để không bị hiểu là thay thế bằng chứng.
- Run chính thức là các file `.jtl` 10-15 phút trong `results/`; không sửa, không đổi tên,
  không chỉnh nội dung.
- Không đọc số liệu không có trong manifest/`.jtl`. Mở file và đọc trực tiếp.
- Không dùng video của bài khác; không dùng TTS.
