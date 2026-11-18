# Report-view screenshots - method and integrity

HW05 yêu cầu ba report view khác nhau. Các screenshot trong
`screenshots/report_views/` được tạo bằng **đúng class GUI của JMeter**, không phải
bảng HTML mô phỏng:

| File | JMeter class | Listener tương ứng | Nguồn dữ liệu |
|---|---|---|---|
| `load_summary.png` | `org.apache.jmeter.visualizers.SummaryReport` | Summary Report | `results/load/23120372_Load_20261116.jtl` |
| `stress_aggregate.png` | `org.apache.jmeter.visualizers.StatVisualizer` | Aggregate Report | `results/stress/23120372_Stress_20261118.jtl` |
| `spike_view_results_tree.png` | `org.apache.jmeter.visualizers.ViewResultsFullVisualizer` | View Results Tree | `results/spike/23120372_Spike_20261118.jtl` |

## Cách tạo

`tools/jtl_viewer/JtlScreenshot.java`:

1. Khởi tạo `JMeterUtils` với `JMETER_HOME` thật.
2. Tạo listener/viewer class tương ứng.
3. Gắn viewer vào `ResultCollector`.
4. Gọi `CSVSaveService.processSamples(jtl, viewer, collector)` - đây là API JMeter dùng
   khi đọc lại file kết quả.
5. Vẽ component ra `BufferedImage` và ghi PNG.

Vì dữ liệu đi qua đúng parser và đúng model của JMeter, các con số trong ảnh khớp với
`.jtl` đã nộp. Ảnh có header ghi rõ tên file JTL và thông số run.

## Lệnh tái lập

```powershell
$cp = "C:\HCMUS\hk7\Testing\apache-jmeter-5.6.3\lib\*;C:\HCMUS\hk7\Testing\apache-jmeter-5.6.3\lib\ext\*"
javac -cp $cp -d tools\jtl_viewer\classes tools\jtl_viewer\JtlScreenshot.java

java -cp "$cp;tools\jtl_viewer\classes" JtlScreenshot summary `
  results\load\23120372_Load_20261116.jtl `
  screenshots\report_views\load_summary.png `
  "Summary Report - Load - 30 VUs - results/load/23120372_Load_20261116.jtl"

java -cp "$cp;tools\jtl_viewer\classes" JtlScreenshot aggregate `
  results\stress\23120372_Stress_20261118.jtl `
  screenshots\report_views\stress_aggregate.png `
  "Aggregate Report - Stress - 10..160 VUs - results/stress/23120372_Stress_20261118.jtl"

java -cp "$cp;tools\jtl_viewer\classes" JtlScreenshot tree `
  results\spike\23120372_Spike_20261118.jtl `
  screenshots\report_views\spike_view_results_tree.png `
  "View Results Tree - Spike - results/spike/23120372_Spike_20261118.jtl"
```

## Ghi chú trung thực

- Đây không phải ảnh chụp màn hình lúc test đang chạy; chúng được render sau khi chạy từ
  JTL chính thức. Báo cáo chính ghi rõ điều này (validity threats, mục 9).
- Không chỉnh sửa số trong ảnh. Nếu mở JTL bằng cùng phiên bản JMeter, kết quả hiển thị
  giống ảnh.
- HTML dashboard (`results/*/html/`) là artifact độc lập, không thay thế ba view trên.
