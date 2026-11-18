# Entry 005 - Task 2: AI reads the JTL logs

**Date/time:** 2026-11-18 16:10 ICT
**Tool:** OpenCode subagent (`general`), model DeepSeek V4.1 Flash Free
**Prompt (verbatim):** `ai_audit/transcripts/task2_prompt.md`
**Constraint given to AI:** read-only; must not read `analysis/`, `Main_Report.md`, `README.md`,
or any `AI_*.md`; may write throw-away Python in the temp directory.

**Human review:** see `Task2_AI_Analysis.md`. Short version: every numeric extraction in this
output was reproducible from the raw files (checked by `scripts/verify_task2_ai.py`), but the
output contains one invented file-level claim (the JMX timer) and several causal conclusions
that the measured data cannot support.

---

## Raw AI output (verbatim, not edited)

# Báo cáo phân tích độc lập JTL – HW05 (Performance Testing)

## 0. Nguồn số liệu (chỉ đọc)
- 6 file JTL: `results/{load,stress,spike,endurance_50C,endurance_75C,endurance_100C}/*.jtl`, các cột `timeStamp`, `elapsed`, `label`, `success`, `responseCode`, `bytes`, `allThreads`.
- `results/<run>/resources.csv`: `backend_cpu_pct`, `backend_rss_mb`, `backend_threads`, `backend_conns`, `jmeter_cpu_pct`, `jmeter_rss_mb`, `jmeter_threads`, `sys_cpu_pct`, `sys_ram_available_mb`.
- `manifest.md` mỗi run, `hardware/hardware_report.md`, `test-plans/*.jmx`, `sut/eshop-sut/backend/server.js`, `database.js`.
- Thống kê do tôi tự tính bằng Python (`elapsed`, nội suy tuyến tính cho percentile), **không** dùng `analysis/`.

## 1. Số đo theo scenario

Throughput = số sample / (max(timeStamp+elapsed) − min(timeStamp)).

| Scenario | Samples | Error | p50 | p95 | p99 | Max | Throughput | Label p95 cao nhất | Label max cao nhất |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| Load | 8.417 | 0 | 2 | 11 | 15 | **1.619** | 14,09/s | POST /api/checkout (15 ms) | GET /api/products/{id} (1.619 ms) |
| Stress | 48.735 | 0 | 3 | 31 | 95 | 322 | 67,82/s (đỉnh 154/s) | POST /api/checkout (81 ms) | POST /api/checkout (322 ms) |
| Spike | 23.809 | 0 | 4 | 17 | 71 | 177 | 26,49/s | POST /api/checkout (34 ms) | GET /api/products?search (177 ms) |
| Endu 50C (80 VU) | 27.388 | 0 | 4 | 16 | 20 | **92** | 38,16/s | POST /api/checkout (20 ms) | GET /api/orders/my-orders (92 ms) |
| Endu 75C (120 VU) | 40.762 | 0 | 2 | 22 | 134 | **1.157** | 56,81/s | POST /api/checkout (78 ms) | POST /api/login (1.157 ms) |
| Endu 100C (160 VU) | 54.488 | 0 | 2 | 38 | 118 | **1.248** | 75,77/s | POST /api/checkout (80 ms) | POST /api/login (1.248 ms) |

Bổ sung đo được: Stress đạt **154 sample/s** ở phút 11 (9.258 sample/60 s, 158 VU). `allThreads` tối đa: 30/160/100/80/120/160. `backend_conns` tối đa: 32/162/102/83/123/163 ≈ số VU (keep-alive OK).

## 2. Bất thường / mâu thuẫn

1. **Run nhẹ nhất lại có max tệ nhất.** Load (30 VU) max 1.619 ms > Stress (160 VU) 322 ms. 15 sample >100 ms dồn vào t = 159,6–161,3 s và **cùng kết thúc tại ≈161,29 s** (1619→180 ms giảm dần theo thứ tự đến). Đây là **một điểm nghẽn toàn cục ~1,6 s**, không phải endpoint chậm. Cùng pattern ở Endu75 (t≈462,95/463,32 s) và Endu100 (t≈529,1–529,5 s), Stress (t≈680,4 s): mọi label xong cùng một thời điểm.
2. **CPU hệ thống không khớp CPU tiến trình.** `sys_cpu_pct` đạt 99,5/99,8/99,7% (Stress/75C/100C) trong khi `backend_cpu_pct` ≤ 56,2 và `jmeter_cpu_pct` trung bình ≤ 9% (psutil: 100% = 1 core, bằng chứng `jmeter_cpu_pct` = 279,7). Tổng công suất 2 tiến trình chỉ ~0,3–3 core/8 → **~60–80% CPU bị tiêu bởi thứ khác** (Defender/OS/process khác). Suy đoán, cần dữ liệu per-process.
3. **Không tìm thấy điểm bão hòa.** Throughput tỉ lệ tuyến tính theo VU: Stress ≈0,95 req/s/VU (10→160 VU), Endurance ≈0,474 req/s/VU (80/120/160). 0 lỗi trên 203k sample ⇒ **"C=160 VU" là tham số workload, không phải capacity đo được**; "100C" không chứng minh SUT chịu được 100% tải.
4. **"Endurance" chỉ 720 s (~12 phút)**, không phải soak test. Không thể kết luận về memory leak dài hạn.
5. **Nghịch lý p50:** Endu50 p50 = 4 ms > Endu75/100 = 2 ms, dù 50C nhẹ hơn và p95/p99 thấp hơn (16/20 vs 22/134 vs 38/118); checkout p50 14 ms vs 10 ms. Endu50 là run duy nhất **0 sample >100 ms**. Nguyên nhân: **không đủ dữ liệu**.
6. **Manifest lệch test plan:** `manifest.md` ghi "think 2000 ± 1000 ms" nhưng `23120372_Load_20261118.jmx` chỉ có `ConstantTimer.delay=2000` (không có Uniform Random Timer) ⇒ tải thực tế (14 req/s) khác mô tả.
7. **RSS backend tăng rồi chững:** 49→66 MB (Load), 53→181 (Stress), 58→180 (75C), 58→180 (100C). Từ phút ~4–6 RSS phẳng (175→180 MB trong 7 phút) ⇒ nhiều khả năng plateau heap, **không** phải leak tuyến tính; độ dốc đầu run 7–13 MB/phút là hiệu ứng warm-up/workload.
8. **JMeter là co-tenant nặng:** `jmeter_rss_mb` 8→826 MB, `jmeter_threads` 3→466, `jmeter_cpu_pct` max 226–280% (xuất hiện ở phút cuối = sinh HTML report). `sys_ram_available_mb` tụt còn 940 MB (75C) đúng lúc có stall ⇒ client gây áp lực bộ nhớ.
9. **Payload phình theo thời gian:** `bytes` trung bình của `GET /api/orders/my-orders` tăng 522 (Load) → 1.347 (Stress) → 1.475 (100C) do không phân trang; `GET /api/products` luôn ~26 KB.

## 3. Đề xuất threshold

| Scenario | p95 | p99 | Max | Error | Throughput | Ghi chú |
|---|---:|---:|---:|---:|---|---|
| Load 30 VU | ≤ 40 ms | ≤ 120 ms | ≤ 800 ms | < 0,5% | ≥ 12/s | đo 11/15/1.619 |
| Stress 160 VU | ≤ 100 ms | ≤ 250 ms | ≤ 800 ms | < 1% | ≥ 140/s @160 VU | đo 31/95/322, đỉnh 154/s |
| Spike (10→100 VU) | ≤ 60 ms trong spike | ≤ 200 ms | ≤ 800 ms | < 1% | phục hồi ≤ 60 s | đo 18 ms/71 ms |
| Endurance | ≤ 80 ms | ≤ 250 ms | ≤ 800 ms | < 0,5% | ≥ 60/s | đo 16–38/20–134 |

- **RPS bền vững:** đo được **76 req/s trong 12 phút, 0 lỗi, p95 38 ms** (Endu100); Stress cho thấy **101 req/s @121 VU vẫn p95 35 ms**. Đề xuất cam kết **100 req/s** (đã kiểm chứng gián tiếp) và **60 req/s** làm ngưỡng CI an toàn. Trần thật: **không đủ dữ liệu** (không có knee).
- **Memory ceiling:** đỉnh đo 182,3 MB (`resources.csv: backend_rss_mb`), nền 53–58 MB ⇒ **cảnh báo 220 MB, trần vận hành 250 MB**, container limit 384–512 MB; drift cho phép **≤ 5%/giờ** sau warm-up (chưa kiểm chứng vì run chỉ 12 phút).

## 4. Bottleneck

| Bằng chứng (nguồn) | Diễn giải |
|---|---|
| `resources.csv: backend_cpu_pct` max 56,2% (Stress), 24–28% (3 run endurance) | Node **chưa dùng hết 1 core** ⇒ server **không** CPU-bound |
| `backend_threads` luôn 12–16 dù `backend_conns` = 163 | Threadpool DB bị chặn trần (libuv mặc định 4) ⇒ request xếp hàng, không phải thiếu worker HTTP |
| `sys_cpu_pct` 99,5–99,8% khi 2 tiến trình chỉ ~1–3 core/8 | **Host contention** (process ngoài + CPU bị throttle: `hardware_report.md` ghi max clock 1.498 MHz vs base 2,6 GHz) |
| `sys_ram_available_mb` min 940 MB (75C), `jmeter_rss_mb` 826 MB | **Client (JMeter) trên cùng host** gây áp lực RAM |
| Stall đồng thời mọi label, xong cùng 1 mốc (JTL §2.1) | Một tài nguyên chặn chung: **event loop/DB**, không phải từng endpoint |
| `database.js` không set WAL; `PRAGMA` đọc được: `journal_mode=delete`, `synchronous=2`; chỉ index `sqlite_autoindex_coupons_1` | Mỗi INSERT checkout = tạo/xoá journal + fsync; `users.email`, `orders.user_id` **không index** ⇒ full scan |
| `server.js` dòng 46–52: login thành công vẫn `UPDATE users` | Write amplification không cần thiết |
| `jmeter_cpu_pct` trung bình ≤ 9% | Client **không** CPU-bound khi đang bơm tải |

**Kết luận:** bottleneck **chính là host** (1 laptop 4C/8T chạy chung JMeter + SUT + OS, CPU bị throttle, sys CPU ~100%, RAM còn <1 GB), **thứ cấp là SUT** ở đường ghi SQLite (journal `delete` + `synchronous=FULL` + single-writer + threadpool 4 + thiếu index). **Không phải client** (JMeter chỉ ~6–9% CPU trung bình, 0 lỗi) — trừ giai đoạn sinh report cuối run.

## 5. Tám tối ưu cho SUT

| # | Đề xuất | Phân loại | Căn cứ |
|---|---|---|---|
| 1 | `PRAGMA journal_mode=WAL; synchronous=NORMAL; busy_timeout=5000` | **feasible** | `journal_mode=delete`, `synchronous=2`; stall đồng thời |
| 2 | Thêm index `users(email)` UNIQUE, `orders(user_id, id DESC)` | **feasible** | `sqlite_master` không có index; my-orders/checkout p95 cao nhất |
| 3 | Bỏ search nội suy chuỗi, dùng tham số + FTS5 (hoặc `name LIKE 'x%'`) | **feasible** | `server.js:144`; search trả 24 KB/lần, full scan 205 row |
| 4 | Phân trang `GET /api/products` và `/api/orders/my-orders` (LIMIT/cursor) | **feasible** | `bytes` my-orders 522→1.475; products 26 KB |
| 5 | Bỏ `UPDATE` khi login thành công; prepared statement + gộp commit checkout | **feasible** | `server.js:46–52`; checkout luôn top p95 |
| 6 | Chuyển JMeter sang máy khác, giảm listener/heap, tắt sinh HTML khi đo | **feasible** | `jmeter_rss_mb` 826 MB, `jmeter_cpu_pct` 280% |
| 7 | Tăng `UV_THREADPOOL_SIZE`, tách DB sang worker thread / `better-sqlite3` + write queue | **cần thêm dữ liệu** | `backend_threads` 12–16; chưa có metric độ trễ hàng đợi threadpool |
| 8 | Chạy Node cluster nhiều process + DB server (Postgres) + container hoá, tách host | **không khả thi** trong phạm vi HW05 (đổi kiến trúc, cần host thứ 2 và thời gian) | `backend_conns` 163 vs 1 process; host 4C/8T |

(Không tính là "tối ưu" nhưng bắt buộc để số liệu hợp lệ: tắt Defender/OneDrive trên thư mục DB, cắm điện, đặt power plan hiệu năng cao.)

## 6. Chỗ tôi phải suy đoán
1. Nguyên nhân stall 0,7–1,6 s (SQLite fsync/journal delete, V8 GC, hay page-fault do thiếu RAM): bằng chứng chỉ là "mọi request xong cùng một mốc" ⇒ tôi nghiêng về **DB write path**, nhưng chưa có profile.
2. Danh tính 60–80% CPU hệ thống "mất tích" (Defender/OS/process khác) — `resources.csv` không có dữ liệu per-process.
3. Ý nghĩa `backend_cpu_pct`: tôi giả định 100% = 1 core (đúng với psutil, và khớp `jmeter_cpu_pct` = 279,7); nếu tool khác quy ước, kết luận "chưa dùng hết 1 core" phải xem lại.
4. Ảnh hưởng của CPU throttle (max clock 1.498 MHz) lên latency: **suy đoán** từ `hardware_report.md`, không có time series tần số.
5. Việc RSS plateau = "không leak": chỉ đúng trong 12 phút; dài hạn **không đủ dữ liệu**.
6. Nghịch lý p50 của Endu50: không giải thích được bằng dữ liệu hiện có.
7. "RPS bền vững 100/s" là **ngoại suy** từ Stress (101 req/s, p95 35 ms), không phải phép đo trực tiếp ở 100 req/s trong thời gian dài.
