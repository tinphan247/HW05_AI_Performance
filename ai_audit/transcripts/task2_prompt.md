# Task 2 - prompt gửi AI (nguyên văn)

**Thời điểm:** 2026-11-18 (sau khi hoàn tất các run chính thức)  
**Tool:** OpenCode subagent (general), model DeepSeek V4.1 Flash Free  
**Mục đích:** để AI đọc `.jtl` thật, tự tính metric, đề xuất threshold/bottleneck/tối ưu;
con người sẽ đối chiếu lại từng kết luận.

---

Bạn là một kỹ sư performance độc lập. Hãy phân tích các file JTL thật trong repo
`C:\HCMUS\hk7\Testing\hw5`:

- `results/load/23120372_Load_20261116.jtl`
- `results/stress/23120372_Stress_20261118.jtl`
- `results/spike/23120372_Spike_20261118.jtl`
- `results/endurance_50C/23120372_Endurance_20261118.jtl`
- `results/endurance_75C/23120372_Endurance_20261118.jtl`
- `results/endurance_100C/23120372_Endurance_20261118.jtl`
- resource: `results/<run>/resources.csv` và `manifest.md`

Ràng buộc:

1. Chỉ ĐỌC. Không sửa file trong repo, không commit, không chạy lại JMeter.
2. Không đọc thư mục `analysis/` (để tránh lặp lại kết luận có sẵn). Được phép viết
   script Python tạm trong thư mục temp để đọc JTL.
3. Không bịa số. Nếu thiếu dữ liệu thì ghi "không đủ dữ liệu".
4. Phân biệt rõ **số đo được** và **suy đoán**.

Nhiệm vụ:

1. Với mỗi scenario (Load, Stress, Spike, 3 mức Endurance), tính: số sample, error,
   p50/p95/p99, throughput; chỉ ra label có p95 cao nhất và label có max cao nhất.
2. Nêu các điểm bất thường hoặc mâu thuẫn giữa các chỉ số (nếu có).
3. Đề xuất threshold cho từng scenario và cho endurance (RPS bền vững, memory ceiling).
4. Tìm bottleneck: so CPU/RSS backend với JMeter và system CPU trong `resources.csv`.
   Kết luận bottleneck nằm ở server, client hay host; nêu bằng chứng.
5. Đề xuất 8 tối ưu cụ thể cho SUT (code/schema/hạ tầng), xếp mỗi đề xuất vào
   "feasible", "cần thêm dữ liệu" hoặc "không khả thi".
6. Nêu những chỗ bạn phải suy đoán.

Trả lời bằng tiếng Việt, có bảng, tối đa khoảng 1.200 từ. Ghi rõ file và cột nào bạn
dùng cho từng con số.
