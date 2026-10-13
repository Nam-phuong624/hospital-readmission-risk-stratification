# Phase 7 Bổ Sung: Giải Thích Mô Hình Phân Tầng Rủi Ro Bằng SHAP (Model Explainability Report)
## Dự Án Giảm Tỷ Lệ Tái Nhập Viện 30 Ngày Cho Bệnh Nhân Đái Tháo Đường

---

## 1. Tuyên Bố Mục Tiêu & Bối Cảnh Lâm Sàng (Clinical Motivation)

### 1.1. Tại sao điểm số rủi ro (Risk Score) đơn thuần là chưa đủ?
Trong môi trường bệnh viện, các mô hình học máy (Machine Learning) như XGBoost thường bị coi là "hộp đen" (Black-box). Khi hệ thống Bệnh án Điện tử (EHR) phát ra một cảnh báo: *"Bệnh nhân A có rủi ro tái nhập viện 21.7% (High Risk)"*, câu hỏi phản xạ đầu tiên của Bác sĩ điều trị và Điều dưỡng quản lý ca bệnh luôn là:
- **"Tại sao bệnh nhân này lại bị xếp vào nhóm nguy cơ cao?"**
- **"Yếu tố cụ thể nào đang đẩy rủi ro lên để chúng tôi tập trung can thiệp?"**

Nếu không có cơ chế giải thích rõ ràng, đội ngũ y tế sẽ rơi vào hai thái cực nguy hiểm:
1. **Thiếu tin tưởng (Distrust):** Bỏ qua cảnh báo vì không hiểu cơ chế phía sau, khiến giải pháp công nghệ bị vô hiệu hóa trên thực địa.
2. **Can thiệp dàn trải:** Biết bệnh nhân có rủi ro nhưng không biết họ yếu ở khâu nào (tiền sử nhập viện, tuân thủ thuốc, hay nơi xuất viện), dẫn đến việc can thiệp thiếu trọng tâm và lãng phí thời gian điều dưỡng.

### 1.2. Mục tiêu kỹ thuật
- **Giải thích toàn cục (Global Explainability):** Định lượng mức độ đóng góp trung bình của 113 đặc trưng lâm sàng lên quyết định phân loại của mô hình XGBoost, đối chiếu chéo với các kết quả phân tích nguyên nhân đa biến (Multivariate Odds Ratios).
- **Giải thích cục bộ (Local Explainability):** Cá thể hóa lý do gắn cờ rủi ro cho từng bệnh nhân cụ thể (thông qua biểu đồ Waterfall), hỗ trợ điều dưỡng và dược sĩ nhanh chóng nắm bắt "điểm nóng lâm sàng" của từng ca bệnh khi chuẩn bị xuất viện.

---

## 2. Phương Pháp Luận: SHAP (SHapley Additive exPlanations)

### 2.1. Cơ sở lý thuyết
Chúng tôi áp dụng phương pháp **SHAP** (Lundberg & Lee, 2017), bắt nguồn từ Lý thuyết Trò chơi Hợp tác (Cooperative Game Theory):
- Mỗi đặc trưng lâm sàng được xem như một "người chơi" tham gia vào việc dịch chuyển dự báo xác suất tái nhập viện của bệnh nhân từ mức cơ sở nền (Base Value / kỳ vọng toàn viện: $\approx -2.05$ trong không gian log-odds, tương đương $\approx 11.4\%$) lên mức xác suất cuối cùng.
- SHAP sở hữu các tính chất toán học quan trọng: **Tính cộng tính địa phương (Local Accuracy)**, **Tính nhất quán (Consistency)**, và **Tính thiếu khuyết (Missingness)**, đảm bảo việc phân bổ mức độ ảnh hưởng của từng biến là hoàn toàn công bằng và không phụ thuộc vào thứ tự đưa biến vào mô hình.

### 2.2. Thiết lập thực nghiệm
- **Mô hình giải thích:** Mô hình XGBoost Challenger nguyên bản từ `notebooks/03_model.py` (`n_estimators=120`, `max_depth=4`, `learning_rate=0.08`, `random_state=42`).
- **Thuật toán giải thích:** `shap.TreeExplainer` tối ưu hóa riêng cho cây quyết định gradient boosted trees.
- **Phạm vi tính toán:** Tính toán trên toàn bộ **19,802 lượt khám** thuộc tập kiểm tra độc lập (Test Set được chia theo mã bệnh nhân `patient_nbr` với `random_state=42` để ngăn ngừa rò rỉ dữ liệu).

---

## 3. Giải Thích Toàn Cục: Các Yếu Tố Thúc Đẩy Mô Hình (Global Feature Importance)

*(Nguồn thực nghiệm: `notebooks/05_shap_explain.py`, Bảng kết quả: `outputs/tables/shap_global_importance.csv`, Biểu đồ: `outputs/figures/shap_bar_importance.png` & `outputs/figures/shap_summary_beeswarm.png`)*

### 3.1. Bảng Top 15 Đặc Trưng Quan Trọng Nhất Theo Giá Trị SHAP Trung Bình

| Thứ hạng (Rank) | Tên biến đặc trưng (Feature) | mean(\|SHAP\|) | Nhóm thông tin lâm sàng | Diễn giải cơ chế tác động |
| :---: | :--- | :---: | :---: | :--- |
| **1** | **`number_inpatient`** | **0.3159** | Prior Utilization | **Yếu tố áp đảo hoàn toàn:** Số lần nhập viện trong 12 tháng trước kéo rủi ro lên mạnh nhất khi có giá trị cao. |
| **2** | **`discharge_disposition_id_3`** | **0.0783** | Admission & LOS | Xuất viện chuyển sang Cơ sở điều dưỡng chuyên môn (SNF): thể trạng suy yếu, rủi ro cao. |
| **3** | **`number_diagnoses`** | **0.0611** | Diagnoses | Gánh nặng đa bệnh đồng mắc: số chẩn đoán $\ge 9$ làm tăng đáng kể nguy cơ tái nhập. |
| **4** | **`discharge_disposition_id_22`** | **0.0565** | Admission & LOS | Xuất viện chuyển sang cơ sở phục hồi chức năng chuyên biệt (Rehab): bệnh lý nền nặng. |
| **5** | **`time_in_hospital`** | **0.0453** | Admission & LOS | Số ngày nằm viện đợt cấp: nằm viện kéo dài liên quan đến nhiễm trùng hoặc suy kiệt. |
| **6** | **`number_emergency`** | **0.0399** | Prior Utilization | Số lần vào phòng cấp cứu năm trước: phản ánh bệnh mạn tính không được kiểm soát tốt ngoại trú. |
| **7** | **`diabetesMed_Yes`** | **0.0364** | Medications | Có chỉ định dùng thuốc đái tháo đường: phân biệt bệnh nhân cần phác đồ điều trị hoạt tính. |
| **8** | **`num_medications`** | **0.0352** | Admission & LOS | Tổng số lượng thuốc trong đơn: chỉ báo của hội chứng đa thuốc (polypharmacy). |
| **9** | **`age_[50-60)`** | **0.0297** | Demographics | Nhóm tuổi trung niên 50-60: nhóm tuổi có tỷ lệ biến chứng lao động phổ biến. |
| **10** | **`num_lab_procedures`** | **0.0262** | Admission & LOS | Số lượng xét nghiệm lâm sàng thực hiện: mức độ theo dõi chuyên sâu của bác sĩ nội trú. |
| **11** | **`diag_1_group_Respiratory`** | **0.0261** | Diagnoses | Bệnh lý hô hấp đi kèm (viêm phổi, COPD): biến chứng cấp tính thường gặp ở người tiểu đường. |
| **12** | **`insulin_No`** | **0.0241** | Medications | Không dùng insulin: làm giảm nhẹ rủi ro tái nhập so với các phác đồ tiêm phức tạp. |
| **13** | **`A1Cresult_Unknown`** | **0.0237** | Labs | Không xét nghiệm HbA1c: đóng góp vào sự gia tăng bất định của dự báo. |
| **14** | **`discharge_disposition_id_6`** | **0.0221** | Admission & LOS | Xuất viện về nhà có dịch vụ y tế hỗ trợ (Home Health Service). |
| **15** | **`discharge_disposition_id_5`** | **0.0219** | Admission & LOS | Xuất viện chuyển tuyến chăm sóc khác. |

### 3.2. Đối chiếu chéo với Phân Tích Thống Kê & Y Văn
1. **Khớp nhất quán với Hồi quy Đa biến (`root_cause_multivariate.csv`):**
   - Biến số đứng đầu tuyệt đối trong SHAP là `number_inpatient` (mean |SHAP| = 0.3159, gấp 4 lần biến đứng thứ 2). Điều này hoàn toàn trùng khớp với phân tích hồi quy đa biến: `num_inpatient` là driver độc lập mạnh nhất với Odds Ratio = 1.305 ($p < 0.0001$).
   - Các biến nằm trong top tiếp theo như `number_diagnoses` (hạng 3), `time_in_hospital` (hạng 5) đều là các yếu tố đã được kiểm định $p < 0.05$ trong Phase 3.
2. **Khớp nhất quán với Chẩn đoán Cắt bỏ biến (`feature_ablation.csv`):**
   - Biểu đồ Beeswarm và bảng SHAP chứng minh rằng hai nhóm tín hiệu cốt lõi là **Tiền sử nhập viện (Prior Utilization)** và **Tuyến xuất viện/Thời gian nằm viện (Admission & LOS)**. Khi một bệnh nhân có lịch sử tái nhập viện dày đặc kết hợp xuất viện sang tuyến chăm sóc hỗ trợ (SNF/Rehab), mô hình sẽ ngay lập tức đẩy điểm số rủi ro vào nhóm Top 20%.

---

## 4. Giải Thích Cục Bộ: Phân Tích 3 Ca Bệnh Lâm Sàng Điển Hình (Local Explainability Cases)

*(Nguồn thực nghiệm: `outputs/tables/shap_local_cases.csv`, Hình ảnh: `outputs/figures/shap_case_1.png`, `shap_case_2.png`, `shap_case_3.png`)*

Để phục vụ đào tạo điều dưỡng và tích hợp vào giao diện hỗ trợ ra quyết định lâm sàng (CDSS), chúng tôi phân tích 3 ca bệnh tiêu biểu đại diện cho 3 trạng thái thực tế:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        3 CA BỆNH LÂM SÀNG KIỂM TRA ĐIỂN HÌNH                           │
├─────────────────────┬───────────────────────────┬──────────────────────────────────────┤
│ Case 1: True Pos    │ Encounter 174689286       │ High Risk (74.3%) → Tái nhập THẬT    │
│ Case 2: False Pos   │ Encounter 109512750       │ High Risk (51.1%) → KHÔNG tái nhập   │
│ Case 3: Low Risk    │ Encounter 2913624         │ Low Risk (2.1%)   → KHÔNG tái nhập   │
└─────────────────────┴───────────────────────────┴──────────────────────────────────────┘
```

### 4.1. Ca Bệnh 1 (True Positive) — Bệnh nhân Trẻ Tuổi Tái Nhập Nhiều Lần
- **Thông tin hồ sơ:** Encounter ID `174689286`, Mã bệnh nhân `88785891`, Độ tuổi `[20-30)`, Nằm viện 3 ngày, Đái tháo đường là chẩn đoán chính, Liều Insulin bị tăng.
- **Dự báo mô hình:** Xác suất rủi ro **74.3%** (Thuộc Top đầu nhóm High Risk).
- **Kết quả thực tế:** **Tái nhập viện trong vòng 30 ngày (Target = 1)**.
- **Phân tích đóng góp SHAP (Waterfall Plot - `shap_case_1.png`):**
  1. `number_inpatient = 11`: Đóng góp SHAP **+2.33** (yếu tố áp đảo đẩy rủi ro lên đỉnh điểm).
  2. `number_emergency = 3`: Đóng góp SHAP **+0.26**.
  3. `age_[20-30) = 1`: Đóng góp SHAP **+0.14**.
  4. `num_lab_procedures = 36`: Đóng góp SHAP **+0.07**.
  5. `num_medications = 15`: Đóng góp SHAP **+0.06**.
- **Ý nghĩa nghiệp vụ y tế:**
  Bệnh nhân trẻ tuổi nhưng đã có tiền sử 11 lần nhập viện và 3 lần cấp cứu trong năm qua. Đây là hình ảnh điển hình của bệnh nhân kiểm soát ngoại trú thất bại nặng nề (nguy cơ cao bị nhiễm toan ceton đái tháo đường - DKA hoặc không tuân thủ tiêm insulin). Mô hình xếp ca này vào nguy cơ cao nhất là hoàn toàn chính xác. Bệnh nhân này bắt buộc phải nhận gói can thiệp 48h kết hợp tư vấn tâm lý - hành vi và giám sát tiêm thuốc tại nhà.

### 4.2. Ca Bệnh 2 (False Positive) — Đa Bệnh Lý Nặng Nhưng Không Tái Nhập Đợt Này
- **Thông tin hồ sơ:** Encounter ID `109512750`, Mã bệnh nhân `19921905`, Độ tuổi `[60-70)`, Nằm viện 3 ngày, Chẩn đoán Tiêu hóa, 9 bệnh đồng mắc, Liều Insulin giữ nguyên.
- **Dự báo mô hình:** Xác suất rủi ro **51.1%** (High Risk).
- **Kết quả thực tế:** **Không tái nhập viện trong 30 ngày (Target = 0)**.
- **Phân tích đóng góp SHAP (Waterfall Plot - `shap_case_2.png`):**
  1. `number_inpatient = 10`: Đóng góp SHAP **+1.81** (lý do chính khiến mô hình gắn cờ đỏ).
  2. `number_emergency = 1`: Đóng góp SHAP **+0.16**.
  3. `num_lab_procedures = 42`: Đóng góp SHAP **+0.07**.
  4. `time_in_hospital = 3`: Đóng góp SHAP **+0.03**.
  5. `number_diagnoses = 9`: Đóng góp SHAP **+0.03**.
  6. `insulin_Steady = 1`: Đóng góp SHAP **-0.02** (kéo giảm nhẹ rủi ro).
- **Ý nghĩa nghiệp vụ y tế:**
  Mô hình dự báo rủi ro 51.1% vì bệnh nhân có tiền sử 10 lần nhập viện và mang 9 bệnh mạn tính. Mặc dù đợt này bệnh nhân không tái nhập (False Positive theo định nghĩa thống kê), nhưng về mặt quản lý vận hành lâm sàng (Case Management), **đây không phải là một sai lầm vô nghĩa**. Một bệnh nhân có thể trạng mong manh như vậy vẫn xứng đáng nhận cuộc gọi 48h của điều dưỡng để đảm bảo họ tiếp tục duy trì được sự ổn định sau xuất viện.

### 4.3. Ca Bệnh 3 (True Negative / Low Risk) — Đợt Nhập Viện Ban Đầu Đơn Giản
- **Thông tin hồ sơ:** Encounter ID `2913624`, Mã bệnh nhân `5073354`, Độ tuổi `[10-20)`, Nằm viện 1 ngày, Chỉ dùng 1 loại thuốc, Chỉ có 2 chẩn đoán, Xuất viện trực tiếp về nhà.
- **Dự báo mô hình:** Xác suất rủi ro **2.1%** (Tầng Low Risk - 50% đáy).
- **Kết quả thực tế:** **Không tái nhập viện (Target = 0)**.
- **Phân tích đóng góp SHAP (Waterfall Plot - `shap_case_3.png`):**
  1. `num_medications = 1`: Đóng góp SHAP **-0.52** (đơn thuốc cực kỳ đơn giản kéo giảm rủi ro mạnh).
  2. `number_inpatient = 0`: Đóng góp SHAP **-0.31** (không có tiền sử nhập viện).
  3. `number_diagnoses = 2`: Đóng góp SHAP **-0.24** (không có đa bệnh lý phức tạp).
  4. `age_[10-20) = 1`: Đóng góp SHAP **-0.22**.
  5. `A1Cresult_Unknown = 0`: Đóng góp SHAP **-0.13** (có hồ sơ xét nghiệm rõ ràng).
  6. `discharge_disposition_id_3 = 0`: Đóng góp SHAP **-0.11**.
- **Ý nghĩa nghiệp vụ y tế:**
  Tất cả các yếu tố của ca bệnh này đều đồng thuận kéo rủi ro xuống mức thấp nhất (2.1%). Bệnh nhân trẻ tuổi, bệnh mới khởi phát nhẹ, không có bệnh kèm. Bệnh viện hoàn toàn yên tâm áp dụng quy trình xuất viện thông thường, tiết kiệm 100% thời gian theo dõi của điều dưỡng chuyên trách.

---

## 5. Giới Hạn & Cảnh Báo Khi Sử Dụng SHAP Trong Y Tế (Clinical Limitations)

> [!WARNING]
> **Tương quan toán học $\neq$ Quan hệ nhân quả lâm sàng:**
> SHAP chỉ phản ánh cách mô hình XGBoost cân trọng số các đặc trưng để đưa ra xác suất dự báo. Một giá trị SHAP dương lớn (ví dụ `number_inpatient` cao làm tăng rủi ro) không có nghĩa là "giảm số lần nhập viện trên giấy tờ" sẽ chữa khỏi bệnh cho bệnh nhân. Mọi can thiệp điều trị phải dựa trên chẩn đoán y khoa thực chứng.

1. **Hiệu ứng tương tác phi tuyến (Feature Interactions):**
   Mô hình cây có khả năng học các tương tác phức tạp giữa liều insulin, độ tuổi và số chẩn đoán. Giá trị SHAP phân tách các tương tác này thành đóng góp cộng tính, do đó bác sĩ cần xem xét bức tranh lâm sàng tổng thể thay vì chỉ nhìn vào một đặc trưng đơn lẻ.
2. **Khuyến nghị tích hợp hệ thống EHR:**
   Khi tích hợp vào bảng giao việc của điều dưỡng (Worklist):
   - Không hiển thị toàn bộ 113 giá trị SHAP kỹ thuật.
   - Chỉ hiển thị **Top 3 lý do thúc đẩy rủi ro** dưới dạng ngôn ngữ tự nhiên thân thiện (ví dụ: *"Cảnh báo: Tiền sử 4+ lần nhập viện năm trước; 9 bệnh đồng mắc; Xuất viện sang trung tâm SNF"*).

---

## 6. Kết Luận

Phân tích SHAP đã giải mã thành công "hộp đen" của mô hình phân tầng rủi ro:
- **Độ tin cậy toàn cục:** Xác nhận mô hình đưa ra quyết định dựa trên các trụ cột lâm sàng vững chắc (tiền sử nhập viện nội trú, tình trạng xuất viện, mức độ đa bệnh lý), hoàn toàn không dựa vào nhiễu ngẫu nhiên.
- **Tính khả thi vận hành:** Cung cấp lý giải trực quan cho từng bệnh nhân cụ thể, giúp cá thể hóa quy trình chăm sóc chuyển tiếp 48 giờ và tối ưu hóa thời gian của đội ngũ y tế.

*Toàn bộ dữ liệu bảng SHAP được lưu trữ tại:* `outputs/tables/shap_global_importance.csv` và `outputs/tables/shap_local_cases.csv`.
