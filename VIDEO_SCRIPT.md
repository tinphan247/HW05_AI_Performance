# Video script - HW05 demo (6-8 phút, thuyết minh tiếng Việt)

> Mục tiêu: quay **màn hình thật** với JMeter GUI và Task Manager cạnh nhau, có giọng nói
> tiếng Việt. Video phải dài tối thiểu 6 phút và để chế độ **Unlisted** trên YouTube.
> Không cần quay camera; chỉ cần ghi màn hình + micro.
>
> Trước khi quay: backend chạy port 3100, đã seed 503 user / 205 product, thư mục
> `results/` và `analysis/` đã có sẵn. Mở sẵn: JMeter, Task Manager (tab Performance),
> PowerShell tại `C:\HCMUS\hk7\Testing\hw5`.

---

## 0:00-0:40 - Giới thiệu

**Lời nói:**

"Xin chào, em là Phan Trung Tin, MSSV 23120372, bài HW05 - Performance Testing.
Em kiểm thử hệ thống EShop, clone từ repo ttbhanh/eshop-sut, commit 85af3ba.
Bài làm có ba kịch bản Load, Stress, Spike dùng chung một workflow end-to-end:
đọc danh sách sản phẩm, tìm kiếm, đăng nhập, xem chi tiết, thêm vào giỏ, checkout
và xem đơn hàng. Em chạy JMeter 5.6.3 trên laptop Dell Latitude 7420, i5-1145G7,
16 GB RAM, Windows 11. Backend Node.js và SQLite chạy cùng máy ở cổng 3100."

**Màn hình:** mở `README.md` hoặc `Main_Report.md`, highlight workflow 7 bước.

## 0:40-1:40 - Dataset và reset

**Lời nói:**

"Trước mỗi lần chạy em reset DB và seed lại bằng script, không sửa code nghiệp vụ.
Dataset gồm 503 user, 205 product và 0 order. CSV `data/e2e_data.csv` có 500 dòng,
mỗi dòng là một user với product, giá, số lượng, keyword và địa chỉ.
Em kiểm tra lại số dòng trong SQLite và gọi thử API products."

**Màn hình:** chạy

```powershell
python scripts\seed_perf_data.py
python scripts\reset_state.py
python scripts\check_dataset.py
```

mở `data/e2e_data.csv`, sau đó mở Postman/trình duyệt gọi `http://localhost:3100/api/products`.

## 1:40-3:00 - Mở Load plan và bắt đầu chạy

**Lời nói:**

"Đây là Load plan: 30 virtual users, ramp 60 giây, chạy 10 phút, think-time 2 giây cộng trừ 1.
CSV Data Set đọc file e2e_data.csv, có ignore first line. Login dùng JSON Extractor
lấy token, các request sau gắn Bearer token. Mỗi request có assertion kiểm tra status
và body, ví dụ login phải có token, checkout phải có orderId.

Em mở Task Manager bên cạnh để thấy CPU và RAM của backend và của JMeter.
Bên phải là terminal chạy monitor tài nguyên, ghi CPU/RSS mỗi 2 giây vào resources.csv.
Em bấm Start và giữ nguyên cửa sổ này."

**Màn hình:** JMeter → mở `test-plans/23120372_Load_20261116.jmx`; mở Thread Group;
mở CSV Data Set; mở JSON Extractor; mở Assertion; Task Manager tab Performance;
chạy `python scripts\monitor_resources.py --pid <backend_pid> ...` hoặc để runner tự chạy.
Bấm Start. Trong lúc chờ, nói tiếp về workflow.

## 3:00-4:00 - Summary Report và HTML dashboard

**Lời nói:**

"Đây là Summary Report - report view chính của Load. Các cột Samples, Average, Error,
Throughput cho thấy 8.417 sample, 0 lỗi, khoảng 14 sample mỗi giây.
p95 là 11 ms, p99 là 15 ms, thấp hơn nhiều so với ngưỡng 1.000 ms em đặt trước.
File HTML dashboard có cùng số liệu, em mở tab Statistics để đối chiếu."

**Màn hình:** mở Summary Report trong JMeter, sau đó mở
`results/load/html/index.html` → Statistics.

## 4:00-5:00 - Stress và Spike

**Lời nói:**

"Với Stress, em chạy 6 mức 10, 20, 40, 80, 120, 160 virtual users, mỗi mức 2 phút.
Aggregate Report cho thấy throughput tăng gần tuyến tính từ 9,7 lên 151 sample mỗi giây,
p95 vẫn dưới 40 ms và không có lỗi. Tuy nhiên system CPU có lúc chạm 99,5% vì JMeter
và backend cùng máy, nên em không kết luận SUT chịu được hơn 160 user.

Spike test thì tăng từ 10 lên 100 user trong 5 giây, lặp 3 chu kỳ. View Results Tree
cho phép em xem từng sample; lúc spike p95 chỉ 17 đến 19 ms, sau đó throughput trở lại
bình thường ngay, không có lỗi."

**Màn hình:** mở `results/stress/html/index.html` (Statistics), sau đó
`results/spike/html/index.html` (Response Times Over Time), và mở View Results Tree
đã render từ JTL trong `screenshots/report_views/`.

## 5:00-6:00 - Endurance, issue và AI audit

**Lời nói:**

"Endurance chạy 12 phút ở 50, 75 và 100% năng lực Stress. Mức 120 user giữ 58,9 sample
mỗi giây, CV throughput 2,18%, p95 21 ms, RSS backend cao nhất 182 MB và chỉ tăng 1,3%
sau phút thứ 5. Vì vậy ngưỡng bền vững là 160 user, 150 sample mỗi giây, memory ceiling
khoảng 182 MB, trong giới hạn đã kiểm thử.

Em cũng tìm được các lỗi thật: lockout cộng 2 lượt và khóa 180 giây thay vì 1 lượt/30 giây,
checkout tin total_amount từ client, cart không xóa sau checkout, product list không phân trang,
search nối chuỗi SQL và các API product không cần đăng nhập. Mỗi issue có bước tái hiện,
log thật và file evidence trong repo.

Phần AI: em dùng OpenCode với model DeepSeek. AI hỗ trợ sinh JMX, viết tool và đọc JTL,
nhưng em kiểm tra lại từng số. Ví dụ AI nói p95 tăng ở 80 user là knee, nhưng raw log
cho thấy 120 user p95 chỉ 29 ms; AI nói RSS tăng tuyến tính, nhưng sau 300 giây gần như
đi ngang. Toàn bộ prompt và phần sửa nằm trong AI Audit Report."

**Màn hình:** mở `analysis/endurance_threshold.md`, `Main_Report.md` mục 5,
`AI_Audit_Report.md` bảng misinterpretation.

## 6:00-6:30 - Agent Skill và kết thúc

**Lời nói:**

"Cuối cùng là Agent Skill `jmeter-perf-testing`: skill nhận một REST API, sinh plan,
chạy monitor, phân tích JTL và tạo manifest. Em demo skill trên workflow này; các script
trong skill là bản sao của script đã dùng. Cảm ơn thầy/cô đã theo dõi."

**Màn hình:** mở `skills/jmeter-perf-testing/SKILL.md`, chạy thử
`python skills\jmeter-perf-testing\scripts\analyze_jtl.py --help`.

---

## Checklist trước khi upload

- [ ] Độ dài ≥ 6:00 (YouTube hiển thị thời lượng).
- [ ] Giọng nói tiếng Việt rõ, không im lặng quá 10 giây.
- [ ] JMeter và Task Manager **cùng khung hình** ít nhất một lần.
- [ ] Hiện tên file plan và số liệu khớp `Main_Report.md`.
- [ ] YouTube để **Unlisted**, dán link vào README + `Main_Report.md` mục 8.
- [ ] Không hiện token, mật khẩu, thông tin cá nhân.
