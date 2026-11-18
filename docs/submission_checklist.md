# Submission checklist - HW05

| Yêu cầu | Artifact | Trạng thái |
|---|---|---|
| 3 test plan Load/Stress/Spike, cùng workflow | `test-plans/23120372_{Load,Stress,Spike}_*.jmx` | Có |
| Workflow phủ auth + read + transactional | 7 request trong mục 3.1 `Main_Report.md` | Có |
| CSV cho credential/product/payload | `data/e2e_data.csv`, `data/lockout.csv` | Có |
| 3 report view khác nhau | Summary / Aggregate / View Results Tree + 3 ảnh thật | Có |
| 3 thư mục HTML report | `results/load/html`, `results/stress/html`, `results/spike/html` | Có |
| Tên file `{MSSV}_{Scenario}_{YYYYMMDD}.jmx` | `test-plans/` (ngày chạy thật 20261116 / 20261118) | Có |
| Chạy thật + raw JTL | `results/*/*.jtl` | Có |
| Resource monitor | `results/*/resources.csv`, `screenshots/resource/*.png` | Có |
| Hardware report | `hardware/hardware_report.md`, `hardware/systeminfo.txt` | Có |
| Endurance 10-15 phút + threshold | `results/endurance_*`, `analysis/endurance_threshold.md` | Có |
| Video ≥ 6 phút, tiếng Việt, unlisted | `VIDEO_SCRIPT.md` + link YouTube | **Chưa quay** |
| GitHub Issues cho bug/perf | issues #1-#8 | **Đã publish** |
| AI-first + prompt từng bước | `ai_audit/entries/001-006` | Có |
| Con người review/sửa AI | `Task2_AI_Analysis.md`, `AI_Audit_Report.md` | Có |
| AI Audit Report | `AI_Audit_Report.md` / `.pdf` | Có |
| AI Critique 200-300 từ | `AI_Critique.md` (297 từ) | Có |
| Task 2 trích đúng raw log | `Task2_AI_Analysis.md` + `analysis/task2_evidence.md` | Có |
| Task 2 phân loại feasible/hallucinated | `Task2_AI_Analysis.md` mục 3 | Có |
| Task 3 flow chart + trade-off | `docs/task3_continuous_testing.md`, `docs/task3_flow.svg` | Có |
| Agent Skill | `skills/jmeter-perf-testing/` | Có |
| Video demo skill | cuối video HW05 | **Chưa quay** |
| Git commit log | `git_commit_log.txt` | Có |
| README tự đánh giá + test summary | `README.md` (89/100) | Có |
| Repo public | `https://github.com/tinphan247/HW05_AI_Performance` | Có |
| Zip đúng tên | `23120372_HW05_AI_Performance_089.zip` | Có |
| Không số liệu bịa | mọi bảng trỏ `.jtl`/CSV/manifest | Có |

## Việc còn lại trước khi nộp

1. **Quay video** theo `VIDEO_SCRIPT.md` (≥ 6 phút, thuyết minh tiếng Việt), upload **Unlisted**,
   rồi dán link vào `README.md` và `Main_Report.md` mục 8. Không có video thì Task 1 và
   Agent Skills sẽ mất điểm.
2. **Bài làm cá nhân** đã được ghi rõ trong `docs/group_scope.md`: không có thành viên nhóm,
   không có bảng so sánh chéo và không bịa tên/ID của người khác.
3. Sau khi thêm link video: tạo lại PDF `reports/Main_Report.pdf`, commit/push, và tạo lại zip.

## Ghi chú về bằng chứng

- `dxdiag.txt` không tạo được trên máy này (dxdiag thoát mà không ghi file); hardware report
  dùng `systeminfo.txt` + WMI (`Win32_Processor`, `Win32_PhysicalMemory`, `Win32_VideoController`).
  Điều này được ghi rõ trong `hardware/hardware_report.md`.
- Ảnh report view được render lại từ JTL bằng đúng class GUI của JMeter
  (`tools/jtl_viewer/JtlScreenshot.java`), không phải ảnh chụp lúc chạy. Phương pháp và giới
  hạn nằm trong `docs/report_view_screenshots.md`.
