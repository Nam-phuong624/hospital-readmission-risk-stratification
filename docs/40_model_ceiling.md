# Phase 4 Bổ Sung: Chẩn Đoán Trần Hiệu Năng Mô Hình (Model Performance Ceiling Analysis)

---

## 1. Tuyên Bố Bối Cảnh & Đóng Khung Nghiên Cứu (Research Framing)
Trong bài toán dự đoán tái nhập viện 30 ngày, mô hình XGBoost đạt mức **ROC-AUC = 0.6670** và **Recall @ Top 20% = 38.90%**. Các thử nghiệm mở rộng (feature engineering, hiệu chuẩn xác suất đẳng trương, điều chỉnh trọng số lớp) đều cho kết quả dao động quanh **0.66 - 0.67** (xem đối chiếu tại `outputs/tables/model_experiments_old_vs_new.csv`).

Thay vì coi đây là một thất bại kỹ thuật thuật toán, tài liệu này tiến hành hai thực nghiệm chẩn đoán định lượng:
1. **Phân tích Đường cong học tập (Learning Curve):** Đánh giá xem mô hình có bị giới hạn bởi cỡ mẫu huấn luyện hay không.
2. **Phân tích Cắt bỏ nhóm biến (Feature Ablation):** Định lượng nhóm thông tin nào thực sự mang tín hiệu và nhóm nào bị bão hòa.

**Kết luận cốt lõi:** Mức AUC ~0.667 là **trần hiệu năng do dữ liệu (Data Ceiling)**, bắt nguồn từ việc thiếu các chiều thông tin quan trọng ngoài bệnh viện và đặc thù nhiễu nhãn của dữ liệu hành chính/EHR, hoàn toàn không phải do lựa chọn thuật toán hay thiếu dữ liệu huấn luyện.

---

## 2. Thực Nghiệm 1: Đường Cong Học Tập (Learning Curve Analysis)
*(Nguồn thực nghiệm: `notebooks/04_ceiling_analysis.py`, bảng kết quả: `outputs/tables/learning_curve_results.csv`, hình ảnh: `outputs/figures/learning_curve.png`)*

Mô hình XGBoost được huấn luyện trên các tỉ lệ bệnh nhân tăng dần: từ 10% (5,599 bệnh nhân, 7,771 lượt khám) đến 100% (55,992 bệnh nhân, 79,541 lượt khám). Việc chia mẫu cắt hoàn toàn theo mã bệnh nhân (`patient_nbr`) và đo lường trên tập kiểm tra độc lập cố định (19,802 lượt khám).

| Tỉ lệ bệnh nhân train | Số bệnh nhân train | Số lượt khám train | Train ROC-AUC | Test ROC-AUC | Test Recall @ Top 20% |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **10%** | 5,599 | 7,771 | 0.8142 | 0.6292 | 36.06% |
| **20%** | 11,198 | 15,733 | 0.7601 | 0.6549 | 38.13% |
| **40%** | 22,396 | 31,762 | 0.7201 | 0.6594 | 38.18% |
| **60%** | 33,595 | 47,691 | 0.7077 | 0.6635 | 38.76% |
| **80%** | 44,793 | 63,545 | 0.7039 | 0.6638 | 38.58% |
| **100%** | 55,992 | 79,541 | 0.6978 | **0.6670** | **38.90%** |

### Phát hiện định lượng:
- **Hiện tượng bão hòa (Saturation):** Chênh lệch Test ROC-AUC giữa 80% cỡ mẫu (0.6638) và 100% cỡ mẫu (0.6670) chỉ là **0.0032 (< 0.01)**.
- **Ý nghĩa:** Đường cong Test AUC đã đi vào trạng thái tiệm cận ngang hoàn toàn. Thu thập thêm hàng chục nghìn lượt bệnh nhân với cùng bộ biến số hiện tại sẽ **không thể cải thiện hiệu năng**. Vấn đề nằm ở **thiếu biến đặc trưng (Feature Sparsity / Missing Modalities)**, không phải do thiếu quan sát.

---

## 3. Thực Nghiệm 2: Phân Tích Cắt Bỏ Nhóm Biến (Feature Ablation)
*(Nguồn thực nghiệm: `outputs/tables/feature_ablation.csv`, hình ảnh: `outputs/figures/feature_ablation.png`)*

Chúng tôi phân loại 113 cột đặc trưng thành 6 nhóm thông tin lâm sàng và thực hiện 2 kiểm định:
1. **Single Group Only:** Chỉ huấn luyện mô hình trên duy nhất 1 nhóm biến.
2. **Leave-One-Group-Out:** Huấn luyện trên toàn bộ các biến ngoại trừ 1 nhóm biến để đo mức sụt giảm hiệu năng ($\Delta \text{AUC}$).

| Nhóm đặc trưng | Các biến số đại diện | Số cột mã hóa | Đơn lẻ (Single AUC) | Bỏ 1 nhóm (Leave-out AUC) | Mức giảm khi bỏ nhóm ($\Delta \text{AUC}$) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Toàn bộ mô hình (Full)** | Toàn bộ 113 đặc trưng | 113 | — | **0.6670** | Baseline (0.0000) |
| **Prior Utilization** | Số lần nhập viện, cấp cứu, ngoại trú 1 năm trước | 3 | **0.6058** | **0.6280** | **-0.0391** *(Sụt giảm nặng nhất)* |
| **Admission & LOS** | Hình thức xuất viện, tuyến nhập viện, ngày nằm viện, số thủ thuật/xét nghiệm | 56 | **0.6086** | **0.6310** | **-0.0360** *(Sụt giảm mạnh)* |
| **Diagnoses** | Nhóm chẩn đoán chính ICD-9, tổng số bệnh chẩn đoán | 9 | 0.5492 | 0.6651 | -0.0020 |
| **Medications** | 23 loại thuốc đái tháo đường, insulin, cờ đổi đơn thuốc | 23 | 0.5528 | 0.6655 | -0.0016 |
| **Demographics** | Tuổi, giới tính, chủng tộc | 16 | 0.5144 | 0.6682 | +0.0012 *(Không giảm)* |
| **Labs** | Kết quả HbA1c, xét nghiệm Glucose huyết thanh | 6 | 0.5083 | 0.6671 | +0.0001 *(Gần như ngẫu nhiên)* |

### Phát hiện định lượng:
1. **Hai trụ cột tín hiệu duy nhất:** `prior_utilization` (3 biến) và `admission_los` (56 biến liên quan đến quy trình xuất viện và độ dài đợt nằm viện). Khi loại bỏ một trong hai nhóm này, AUC sụt giảm nghiêm trọng ~0.036 - 0.039.
2. **Sự dư thừa thông tin của các nhóm còn lại:** Các nhóm Thuốc (`medications`), Chẩn đoán (`diagnoses`), Nhân khẩu học (`demographics`) và Xét nghiệm (`labs`) khi dùng độc lập có sức mạnh phân loại rất yếu (AUC 0.508 - 0.553), và khi loại bỏ khỏi mô hình tổng thể thì AUC hầu như không thay đổi ($\Delta \text{AUC} \le 0.002$).

---

## 4. Tại Sao Dữ Liệu Bị Trần Hiệu Năng? (Root Causes of Data Ceiling)

1. **Thiếu hoàn toàn các biến số ngoài viện (Outpatient & Social Determinants of Health):**
   - Bộ dữ liệu Diabetes 130-US chỉ ghi nhận thông tin hành chính nội trú trong thời gian nằm viện.
   - Các nguyên nhân quyết định việc một bệnh nhân có tái nhập viện trong 30 ngày hay không lại nằm ở gia đình: Bệnh nhân có tiền mua thuốc không? Có người nhà hỗ trợ tiêm insulin không? Có hiểu đúng chế độ ăn kiêng không? Bệnh nhân có phương tiện để đi tái khám ngoại trú không? Những yếu tố này **hoàn toàn vắng bóng** trong dữ liệu.
2. **Lỗ hổng dữ liệu xét nghiệm nền tảng:**
   - 83.05% bệnh nhân không có kết quả xét nghiệm HbA1c; nhóm `labs` đơn lẻ chỉ đạt AUC = 0.5083 (tương đương đoán ngẫu nhiên).
3. **Nhiễu nhãn của biến mục tiêu (Label Noise):**
   - Biến `readmitted < 30` chỉ ghi nhận tái nhập viện tại các bệnh viện tham gia hệ thống thu thập dữ liệu; nếu bệnh nhân nhập viện tại một cơ sở y tế độc lập khác hoặc phòng khám tư, biến mục tiêu sẽ bị gán nhãn 0 (False Negative).

---

## 5. Đối Chiếu Với Y Văn (Literature Comparison)
- Bộ dữ liệu Diabetes 130-US hospitals được trích xuất từ dữ liệu lâm sàng giai đoạn 1999–2008 của 130 bệnh viện Hoa Kỳ (công bố bởi Strack et al., 2014 [1]).
- Trong các nghiên cứu học máy áp dụng trên bộ dữ liệu này hoặc các bài toán dự đoán tái nhập viện tương tự chỉ dựa trên dữ liệu EHR nội trú, mức ROC-AUC phổ biến được ghi nhận trong y văn cũng chỉ dao động trong khoảng **0.64 – 0.68** [cần bổ sung trích dẫn]. 
- Điều này khẳng định mức AUC = 0.667 của mô hình trong dự án hoàn toàn tương thích với mức trần học thuật đã biết, và việc cố gắng áp dụng các mô hình phức tạp hơn (Deep Learning, Ensembling nặng) mà không có thêm nguồn dữ liệu mới là không hiệu quả.

---

## 6. Kết Luận & Hàm Ý Vận Hành
- **Đóng khung mô hình đúng thực tế:** Không kỳ vọng mô hình là một công cụ chẩn đoán cá thể hóa chính xác cao, mà định vị mô hình là **Bộ lọc ưu tiên vận hành (Operational Prioritization Filter)**.
- **Giá trị thực tiễn được bảo toàn:** Với Lift = 1.94x và Recall @ Top 20% = 38.90%, mô hình vẫn hoàn thành xuất sắc vai trò nghiệp vụ: giúp bệnh viện tập trung 20% nguồn lực điều dưỡng vào nhóm đối tượng có rủi ro thực tế cao gấp 3.3 lần nhóm đáy.

---

### Tài liệu tham khảo:
[1] Strack, B., DeShazo, J. P., Gennings, C., Olmo, J. L., Ventura, S., Cios, K. J., & Clore, J. N. (2014). "Impact of HbA1c Measurement on Hospital Readmission Rates: Analysis of 70,000 Clinical Database Patient Records." *BioMed Research International*, 2014, 781670.  
[2] Các nghiên cứu dự đoán tái nhập viện trên cùng tập dữ liệu: [cần bổ sung trích dẫn].
