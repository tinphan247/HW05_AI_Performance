# Task 2 - raw evidence used for human verification

Mọi giá trị dưới đây đọc trực tiếp từ `.jtl` / `resources.csv` / `manifest.json`.
Dùng để đối chiếu với câu trả lời của AI, không dùng để AI "đoán".

## Load - `results/load/23120372_Load_20261116.jtl`

- 8.417 samples, 0 lỗi, 597,47 s, 14,088 samples/s, max active threads 30
- Overall: p50 2 ms, p95 11 ms, p99 15 ms, avg 5,17 ms, max 1.619 ms
- Max sample: `GET /api/products/{id}`, 1.619 ms, HTTP 200, timestamp `1794806733348`
  = **2026-11-16 12:25:33.348 ICT**, allThreads 30

| Label | Rows | p95 | p99 | Max |
|---|---:|---:|---:|---:|
| GET /api/products (list) | 1.214 | 5 | 8 | 1.279 |
| GET /api/products?search | 1.210 | 5 | 7,91 | 1.324 |
| POST /api/login | 1.206 | 4 | 10 | 1.385 |
| GET /api/products/{id} | 1.202 | 3 | 7 | **1.619** |
| POST /api/cart | 1.201 | 2 | 3 | 4 |
| POST /api/checkout | 1.196 | 15 | 43,15 | 1.404 |
| GET /api/orders/my-orders | 1.188 | 3 | 9 | 897 |

## Stress - `results/stress/23120372_Stress_20261118.jtl`

| Step | VUs | Rows | RPS | p95 | p99 | Avg | Max |
|---|---:|---:|---:|---:|---:|---:|---:|
| S1 | 10 | 1.149 | 9,741 | 14 | 27 | 5,53 | - |
| S2 | 20 | 2.311 | 19,336 | 13 | 26 | 4,49 | - |
| S3 | 40 | 4.509 | 37,786 | 20 | 85 | 7,27 | - |
| S4 | 80 | 9.053 | 75,640 | **40** | 85 | 7,80 | - |
| S5 | 120 | 13.599 | 113,502 | **29** | 87 | 7,88 | - |
| S6 | 160 | 18.114 | **150,978** | 38 | 116 | 10,24 | - |

- Tổng 48.735 samples, 0 lỗi, max 322 ms
- Max sample: `POST /api/checkout`, 322 ms, timestamp `1794989122443`
  = **2026-11-18 15:05:22.443 ICT**, allThreads 160
- JMeter CPU max **226%**; backend CPU max **56,2%**; system CPU max **99,5%**
  (`results/stress/manifest.json`)

## Spike - `results/spike/23120372_Spike_20261118.jtl`

| Cycle | Phase | Rows | RPS | p95 | p99 |
|---|---|---|---:|---:|---:|
| C1 | Baseline 10 | 1.141 | 9,638 | 13 | 19,6 |
| C1 | Spike 100 | 5.606 | 93,879 | 18 | 89 |
| C1 | Recovery 10 | 1.175 | 9,919 | 15 | 28,26 |
| C2 | Spike 100 | 5.646 | 94,429 | 17,75 | 59 |
| C3 | Spike 100 | 5.678 | 95,817 | 19 | 68,46 |

- Tổng 23.809 samples, 0 lỗi, max 177 ms
- Max sample: `GET /api/products?search`, 177 ms, timestamp `1794989335085`
  = **2026-11-18 15:08:55.085 ICT**, allThreads 100

## Endurance - `analysis/endurance_*/endurance_*.md`

| Level | VUs | RPS 30 s | CV 30 s | p95 | p99 | RSS max | RSS growth after 300 s | Backend CPU avg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 50C | 80 | 39,528 | 1,99% | 16 | 20 | 179,84 MB | 1,3% | 14,25% |
| 75C | 120 | 58,887 | 2,18% | 21 | 123,69 | 182,34 MB | 1,3% | 12,44% |
| 100C | 160 | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

- RSS tăng nhanh 57,95 → ~180 MB trong 5 phút đầu, sau đó gần như đi ngang.
- Slope cả cửa sổ 50C: 8,26 MB/phút; slope sau 300 s: 0,363 MB/phút.
- Không có lỗi ở cả ba mức; p99 75C 123,69 ms do một số sample hiếm > 1.000 ms.

## Code facts dùng để phân loại đề xuất tối ưu

| Quan sát | Nguồn |
|---|---|
| `POST /api/checkout` ghi SQLite, nhận `total_amount` từ client | `backend/server.js` 297-306 |
| `GET /api/products` chạy `SELECT *`, không limit/offset | `backend/server.js` 141-156 |
| Search nối chuỗi SQL `LIKE '%...%'` | `backend/server.js` 144 |
| Cart là object in-memory, không xóa sau checkout | `backend/server.js` 14, 284-306 |
| Product write không có `authenticateToken` | `backend/server.js` 167-195 |
| SQLite chạy mặc định, không thấy index tùy chỉnh cho product name | `backend/database.js` |

## Ngưỡng đã đăng ký trước (PLAN.md 5.1)

- error < 1%; p95 < 1.000 ms; p99 < 2.000 ms; CV 30 s < 10%;
- RSS tăng < 10% sau warm-up 300 s; CPU backend trung bình < 85%.
