# Giảm Tỷ Lệ Tái Nhập Viện 30 Ngày Cho Bệnh Nhân Đái Tháo Đường
## 30-Day Readmission Reduction — Business Analysis & Clinical Solution Project

---

## 1. Tóm Tắt Dự Án (Executive Summary)
Dự án phân tích dữ liệu và thiết kế giải pháp nghiệp vụ y tế nhằm dự đoán rủi ro và tối ưu nguồn lực can thiệp giảm tỷ lệ tái nhập viện trong 30 ngày ở bệnh nhân đái tháo đường nội trú. Dựa trên dữ liệu 99,343 lượt điều trị sau khi làm sạch từ bộ dữ liệu Diabetes 130-US Hospitals (UCI id=296), dự án tập trung vào phương pháp phân tích nghiệp vụ thực tế, minh bạch về mặt thống kê và khả thi về mặt vận hành:
1. **Phân tích nguyên nhân đa biến:** Phân định rõ giữa các yếu tố nguy cơ độc lập đã được xác nhận ($p < 0.05$) và các tín hiệu đơn biến mất ý nghĩa sau khi kiểm soát biến gây nhiễu.
2. **Phân tầng rủi ro có trách nhiệm:** Xây dựng mô hình máy học chia nhóm bệnh nhân (Group-split theo mã bệnh nhân), phân tách được nhóm 20% nguy cơ cao nhất (High Risk) có tỷ lệ tái nhập thực tế **21.74%**, cao gấp **3.3 lần** nhóm nguy cơ thấp (**6.53%**).
3. **Thiết kế can thiệp chuyển tiếp (PRD):** Đề xuất quy trình chăm sóc chuyển tiếp 48 giờ (Teach-back rà soát thuốc tại giường + Cuộc gọi chuyên môn trong 48h đầu tại nhà).
4. **Kế hoạch thử nghiệm A/B:** Thiết kế thử nghiệm lâm sàng đối chứng ngẫu nhiên với cỡ mẫu 1,458 bệnh nhân để kiểm chứng hiệu quả can thiệp trên thực tế.

---

## 2. Vấn Đề Nghiệp Vụ & Bộ Chỉ Số KPI (Problem & KPIs)
- **Vấn đề cốt lõi:** Bệnh viện không thể theo dõi chuyên sâu tất cả bệnh nhân xuất viện do giới hạn nguồn lực điều dưỡng. Thiếu công cụ phân tầng rủi ro khiến nguồn lực chăm sóc sau xuất viện bị phân bổ cào bằng, bỏ sót những bệnh nhân có nguy cơ diễn tiến nặng trong 30 ngày đầu tại nhà.
- **3 Chỉ số KPI cốt lõi:**
  1. *30-Day Readmission Rate (Business Primary):* Giảm tỷ lệ tái nhập ở nhóm nguy cơ cao (Mục tiêu GIẢ ĐỊNH để thiết kế thử nghiệm: hướng tới $\le 16.0\%$ từ mức nền 21.74%).
  2. *High-Risk Capture Rate - Recall @ Top 20% (Operational/Model):* Đạt **38.90%** (bắt trúng gần 40% tổng số ca tái nhập toàn viện khi chỉ tập trung vào 20% bệnh nhân nặng nhất).
  3. *48h Follow-up Compliance Rate (Process KPI):* Đạt $\ge 85\%$ bệnh nhân nhóm High Risk hoàn thành cuộc gọi rà soát trong 48h.

---

## 3. Phát Hiện Số Liệu Chính & Diễn Giải Nghiệp Vụ (Key Findings & Business Interpretations)
*(Nguồn sự thật: `outputs/tables/root_cause_multivariate.csv` & `outputs/tables/eda_*.csv`)*

### 3.1. Các Yếu Tố Nguy Cơ Đã Xác Nhận (Confirmed Independent Drivers, $p < 0.05$)
Các biến số dưới đây duy trì mối liên hệ độc lập có ý nghĩa thống kê cao sau khi kiểm soát toàn bộ các yếu tố lâm sàng khác trong mô hình hồi quy đa biến:

| Yếu tố nguy cơ | Số liệu thống kê đa biến | Diễn giải nghiệp vụ y tế ("Nghĩa là gì với bệnh viện?") |
| :--- | :--- | :--- |
| **Tiền sử nhập viện (`num_inpatient`)** | **OR = 1.305** (95% CI: [1.249 - 1.362], **$p < 0.0001$**). Đơn biến: nhóm $\ge 4$ lần nhập viện có tỷ lệ tái nhập 31.36% vs 8.59% ở người 0 lần. | **Driver mạnh nhất:** Bệnh nhân nhập viện nhiều lần trong năm là nhóm kiểm soát ngoại trú thất bại; cần tự động kích hoạt quy trình quản lý ca bệnh (case management) ngay khi vào viện. |
| **Số bệnh đồng mắc (`number_diagnoses`)** | **OR = 1.052** (95% CI: [1.022 - 1.082], **$p = 0.0005$**). | Mỗi bệnh đồng mắc tăng 5.2% tỷ lệ chênh tái nhập; gánh nặng đa bệnh lý làm tăng độ phức tạp của đơn thuốc (polypharmacy), đòi hỏi dược sĩ lâm sàng rà soát tương tác thuốc. |
| **Bệnh nhân cao tuổi $\ge 70$ (`is_elderly_70plus`)** | **OR = 1.172** (95% CI: [1.022 - 1.344], **$p = 0.0233$**). | Người cao tuổi suy giảm trí nhớ, thị lực kém dễ tiêm sai liều insulin; quy trình xuất viện bắt buộc phải có sự tham gia và cam kết của người chăm sóc chính (caregiver). |
| **Thời gian nằm viện (`time_in_hospital`)** | **OR = 1.025** (95% CI: [1.000 - 1.050], **$p = 0.0480$**). | Thời gian nằm viện dài phản ánh tình trạng nhiễm trùng nặng hoặc suy kiệt thể trạng khi ra viện, cần hỗ trợ phục hồi chức năng và dinh dưỡng sau xuất viện. |

### 3.2. Các Yếu Tố Chỉ Là Tín Hiệu Đơn Biến (KHÔNG Còn Ý Nghĩa Thống Kê Trong Đa Biến)
- **Thay đổi liều Insulin (`insulin_down`, `insulin_up`):** Ở phân tích đơn biến, nhóm giảm liều có tỷ lệ tái nhập là 14.22% và tăng liều là 13.33% (so với 10.21% ở nhóm không dùng). Tuy nhiên trong mô hình đa biến, sau khi kiểm soát tiền sử nhập viện và bệnh đồng mắc, `insulin_down` có **$p = 0.0677$** và `insulin_up` có **$p = 0.2507$**. Do đó, sự dao động liều insulin chỉ là tín hiệu phản ánh tình trạng bệnh nặng đi kèm, **không đủ bằng chứng thống kê để khẳng định là nguyên nhân độc lập**.
- **Xét nghiệm HbA1c (`no_a1c_test`):** Cần tách bạch rõ ràng giữa thực tế quy trình và bằng chứng thống kê:
  1. *Thực tế quan sát được:* Có tới **83.05%** hồ sơ bệnh án không ghi nhận kết quả xét nghiệm HbA1c trong đợt nằm viện.
  2. *Liên hệ với tái nhập viện:* Trong hồi quy đa biến, biến số này đạt **$p = 0.1076$** (OR = 1.146, 95% CI: [0.971 - 1.352]); **chưa đủ bằng chứng thống kê** để kết luận việc không đo HbA1c làm tăng nguy cơ tái nhập. Dù vậy, chuẩn hóa đo HbA1c vẫn là khuyến cáo thực hành lâm sàng tiêu chuẩn để hỗ trợ theo dõi dài hạn.

---

## 4. Khung Đánh Giá Mô Hình Dự Báo Trung Thực (Model Performance Framework)
*(Nguồn sự thật: `outputs/tables/model_comparison.csv`)*

### 4.1. Bảng So Sánh Hiệu Năng Mô Hình
Phương pháp chia dữ liệu: Chia Train/Test (80/20) nghiêm ngặt theo **`patient_nbr`** (55,992 bệnh nhân train, 13,998 bệnh nhân test) để triệt tiêu hoàn toàn rò rỉ dữ liệu giữa các lần nhập viện của cùng một người bệnh.

| Mô hình | ROC-AUC | PR-AUC | Recall @ Top 20% | Precision @ Top 20% | Lift @ Top 20% | Brier Score (Calibration) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Baseline)** | 0.6613 | 0.2158 | 38.00% | 21.26% | 1.90x | 0.0954 |
| **XGBoost (Challenger)** | **0.6670** | **0.2312** | **38.90%** | **21.76%** | **1.94x** | **0.0944** |

### 4.2. Nhìn Nhận Thẳng Thắn Về Năng Lực Mô Hình (Model Reality Check)
- **ROC-AUC = 0.6670 là mức khiêm tốn:** Con số này phản ánh rằng dữ liệu hành chính/EHR thông thường không thể dự đoán chính xác tuyệt đối ai sẽ tái nhập viện (do thiếu các yếu tố xã hội - Social Determinants of Health, tuân thủ dinh dưỡng tại nhà).
- **Giá trị thực tế nằm ở Xếp hạng ưu tiên (Prioritization & Lift):** Giá trị cốt lõi của mô hình không phải là một bộ phân loại nhị phân hoàn hảo, mà là công cụ xếp hạng danh sách bệnh nhân xuất viện:
  - **Lift = 1.94x:** Khả năng phát hiện ca tái nhập cao gần gấp đôi so với chọn ngẫu nhiên.
  - **Phân tách rủi ro 3.3 lần:** Nhóm High Risk (Top 20%) có tỷ lệ tái nhập thực tế là **21.74%**, trong khi nhóm Low Risk (50% đáy) chỉ có **6.53%**.
- **Đánh giá Precision @ Top 20% = 21.76% (Tải False Positive):**
  - Mức Precision này đồng nghĩa với việc khoảng **78.2% bệnh nhân được gắn cờ nguy cơ cao sẽ không thực sự tái nhập viện**.
  - *Tại sao vẫn chấp nhận được trong vận hành?* Gói can thiệp đề xuất (Teach-back tại giường và cuộc gọi 5-10 phút của điều dưỡng) là các biện pháp **chi phí thấp và không xâm lấn**. Chi phí của việc gọi điện cho một bệnh nhân không tái nhập (False Positive) là rất nhỏ, trong khi lợi ích bảo vệ và bắt trúng gần 40% tổng số ca tái nhập toàn viện là vượt trội.

### 4.3. Kết Quả Thử Nghiệm Cải Thiện Mô Hình & Trần Hiệu Năng (Ceiling Analysis)
Theo yêu cầu kỹ thuật, chúng tôi đã thử nghiệm bổ sung các kỹ thuật:
- Tạo biến tổng hợp `prior_utilization` (nội trú + cấp cứu + ngoại trú), đếm số thuốc hoạt tính, cờ đa bệnh $\ge 9$ chẩn đoán, tương tác tuổi $\times$ số lần nhập viện.
- Thử nghiệm điều chỉnh trọng số lớp `scale_pos_weight` và hiệu chuẩn xác suất đẳng trương `CalibratedClassifierCV(method='isotonic')`.

*Kết quả đối chiếu (Nguồn: `outputs/tables/model_experiments_old_vs_new.csv`):*
- Feature engineering chỉ làm thay đổi ROC-AUC từ 0.6670 thành 0.6668 (-0.0002) và Recall@20% từ 38.90% thành 38.45% (-0.45%).
- `scale_pos_weight` làm tăng Brier score từ 0.0944 lên 0.2215 (làm lệch nghiêm trọng độ tin cậy của xác suất dự báo).
- `CalibratedClassifierCV` tăng nhẹ ROC-AUC lên 0.6690 (+0.0020) nhưng Recall@20% giảm nhẹ còn 38.67%.
- **Quyết định kỹ thuật:** Giữ nguyên mô hình XGBoost ban đầu đơn giản để tránh nguy cơ overfitting, đảm bảo tính giải thích cao và tuân thủ nguyên tắc Occam's Razor.
- **Chẩn đoán trần hiệu năng:** Chi tiết phân tích thực nghiệm chứng minh trần hiệu năng do dữ liệu (Learning curve bão hòa ở $N \ge 45,000$ bệnh nhân & Feature ablation chứng minh tín hiệu chủ yếu nằm ở tiền sử nhập viện và hình thức xuất viện) được trình bày tại [docs/40_model_ceiling.md](file:///home/namphuong/Documents/project_vinmec/docs/40_model_ceiling.md).

---

## 5. Can Thiệp Chăm Sóc Chuyển Tiếp (Đề Xuất Định Tính)

### 5.1. Quy Trình Chăm Sóc Chuyển Tiếp 48 Giờ (PRD Core)
1. **Teach-Back tại giường trước xuất viện:** Dược sĩ lâm sàng đối soát thuốc trực tiếp, hướng dẫn kỹ thuật tiêm insulin và nhận biết dấu hiệu hạ đường huyết.
2. **Cuộc gọi chủ động 48 giờ:** Điều dưỡng chuyên trách gọi điện thoại theo checklist 5 điểm (tuân thủ thuốc, đường huyết mao mạch, dấu hiệu cảnh báo, dinh dưỡng, hẹn tái khám).
3. **Phân luồng xử lý khẩn cấp (Escalation):** Kích hoạt can thiệp của bác sĩ trong 2h hoặc điều hướng cấp cứu nếu phát hiện chỉ số bất thường.

### 5.2. Đánh Giá Hiệu Quả Chi Phí (Cost-Benefit Consideration)
Phân tích chi phí-lợi ích cần dữ liệu viện phí nội bộ, nằm ngoài phạm vi dữ liệu hiện có; sẽ thực hiện sau khi có kết quả A/B test.

---

## 6. Kế Hoạch Thử Nghiệm Lâm Sàng Đối Chứng (A/B Testing Plan)
- **Đơn vị phân nhóm:** Ngẫu nhiên hóa theo mã bệnh nhân (`patient_nbr`) tại thời điểm xuất viện ở nhóm High Risk (Top 20%).
- **Hai nhóm thử nghiệm:** Nhóm A (Đối chứng - Chăm sóc tiêu chuẩn, $p_1 = 21.74\%$) vs Nhóm B (Can thiệp - Gói chuyển tiếp 48h).
- **Cỡ mẫu tính toán theo dải hiệu ứng (Minimum Detectable Effect - MDE):**
  Dựa trên công thức hai tỷ lệ độc lập (Two-Proportion Z-Test, $\alpha=0.05, \text{Power}=80\%$, kiểm định 2 phía) với baseline $p_1 = 21.74\%$ đo được từ tập test:

*(Nguồn xuất bản: `outputs/tables/ab_sample_size_by_effect.csv`)*

| MDE (Điểm phần trăm) | Tỷ lệ kỳ vọng sau can thiệp ($p_2$) | Cỡ mẫu mỗi nhánh ($N_{\text{arm}}$) | Tổng cỡ mẫu ($N_{\text{total}}$) | Cỡ mẫu dự phòng mất dấu 5% |
| :---: | :---: | :---: | :---: | :---: |
| **2 pp** | 19.74% | 6,448 | 12,896 | **13,575** |
| **3 pp** | 18.74% | 2,813 | 5,626 | **5,923** |
| **4 pp** | 17.74% | 1,551 | 3,102 | **3,266** |
| **5 pp** | 16.74% | 972 | 1,944 | **2,047** |
| **6 pp** | 15.74% | 661 | 1,322 | **1,392** |
| **7 pp** | 14.74% | 474 | 948 | **998** |

*Diễn giải vận hành:* Hiệu ứng can thiệp kỳ vọng càng nhỏ (MDE thấp) thì cỡ mẫu yêu cầu càng lớn và thời gian thử nghiệm càng dài; nhóm nghiên cứu sẽ căn cứ vào lưu lượng bệnh nhân thực tế của phân viện để chọn ngưỡng MDE khả thi tương ứng. Chi tiết kế hoạch tại [docs/30_ab_test_plan.md](file:///home/namphuong/Documents/project_vinmec/docs/30_ab_test_plan.md).

---

## 7. 3 Bullet CV (Problem — Solution — Impact)
*(Chỉ sử dụng các số liệu thực tế đo lường được từ dữ liệu và mô hình)*

* **Problem:** Tỷ lệ tái nhập viện 30 ngày ở bệnh nhân đái tháo đường đạt 11.39% trên 99,343 đợt điều trị nội trú; bệnh viện thiếu công cụ phân tầng rủi ro tự động dẫn đến việc phân bổ nguồn lực chăm sóc sau xuất viện bị dàn trải và bỏ sót ca bệnh phức tạp.
* **Solution:** Xây dựng mô hình phân tầng rủi ro máy học (Group-split theo bệnh nhân chống rò rỉ; AUC = 0.667 dùng để xếp hạng ưu tiên danh sách chăm sóc) và thiết kế quy trình can thiệp chuyển tiếp 48 giờ (PRD) kết hợp kế hoạch thử nghiệm lâm sàng đối chứng A/B Testing ($N=1,458$).
* **Impact:** Phân tầng thành công nhóm 20% bệnh nhân nguy cơ cao nhất với tỷ lệ tái nhập thực tế đạt 21.74% (chênh lệch rủi ro 3.3 lần so với nhóm nguy cơ thấp 6.53%), giúp đội ngũ y tế bao phủ được 38.9% tổng số ca tái nhập toàn viện khi chỉ cần tập trung vào 20% nguồn lực vận hành.

---

## 8. Cấu Trúc Thư Mục Dự Án (Project Structure)
```
├── AGENTS.md                          # Hướng dẫn & Quy tắc dự án
├── README.md                          # Báo cáo tổng kết toàn diện & 3 bullet CV
├── download_data.py                   # Script tự động tải bộ dữ liệu Diabetes UCI
├── data/
│   └── diabetic_data.csv              # File dữ liệu gốc (101,766 dòng x 50 cột)
├── src/
│   └── prep.py                        # Pipeline dùng chung: load_clean, feature_frame, split_by_patient
├── notebooks/
│   ├── 01_eda.py / 01_eda.ipynb       # Làm sạch dữ liệu theo Rules & Phân tích khám phá
│   ├── 02_causes.py / 02_causes.ipynb # Phân tích nguyên nhân & Hồi quy đa biến Odds Ratios
│   ├── 03_model.py / 03_model.ipynb   # Mô hình Logistic Regression + XGBoost & Thử nghiệm cải tiến
│   └── 04_ceiling_analysis.py / .ipynb# Chẩn đoán trần hiệu năng: Learning curve & Feature ablation
├── outputs/
│   ├── risk_scores.csv                # Điểm số rủi ro dự báo & Risk Tiers cho từng bệnh nhân test
│   ├── figures/                       # Biểu đồ trực quan hóa độ phân giải cao
│   │   ├── eda_readmission_by_age.png
│   │   ├── eda_readmission_by_specialty.png
│   │   ├── eda_readmission_by_prior_visits.png
│   │   ├── eda_readmission_by_a1c.png
│   │   ├── eda_readmission_by_stay_and_meds.png
│   │   ├── root_cause_odds_ratios.png
│   │   ├── root_cause_diagnosis_distribution.png
│   │   ├── model_roc_pr_curve.png
│   │   ├── model_calibration_curve.png
│   │   ├── model_feature_importance.png
│   │   ├── learning_curve.png
│   │   └── feature_ablation.png
│   └── tables/                        # Bảng số liệu tổng hợp định dạng CSV
│       ├── eda_summary_overall.csv
│       ├── eda_readmission_by_age.csv
│       ├── eda_readmission_by_specialty.csv
│       ├── eda_readmission_by_prior_utilization.csv
│       ├── eda_readmission_by_a1c_and_change.csv
│       ├── root_cause_diagnosis_groups.csv
│       ├── root_cause_medications.csv
│       ├── root_cause_multivariate.csv
│       ├── model_comparison.csv
│       ├── model_experiments_old_vs_new.csv
│       ├── ab_sample_size_by_effect.csv
│       ├── learning_curve_results.csv
│       └── feature_ablation.csv
└── docs/
    ├── 00_problem_framing.md          # Phase 1: Problem statement, 4 câu hỏi NV, 3 KPI
    ├── 10_root_cause_findings.md      # Phase 3: Báo cáo nguyên nhân gốc rễ & Process gaps
    ├── 20_PRD_intervention.md          # Phase 5: PRD Gói can thiệp chuyển tiếp theo dõi 48h
    ├── 30_ab_test_plan.md             # Phase 6: Kế hoạch thử nghiệm A/B Testing & Bảng cỡ mẫu
    └── 40_model_ceiling.md            # Chẩn đoán trần hiệu năng mô hình (Learning curve & Ablation)
```

---

## 9. Cảnh Báo & Giới Hạn Nghiên Cứu (Caveats)
1. **Tính chất dữ liệu:** Dữ liệu sử dụng là bộ dữ liệu từ 130 bệnh viện Hoa Kỳ (giai đoạn 1999-2008), đóng vai trò là **Proof-of-Concept (PoC)** về mặt phương pháp luận phân tích nghiệp vụ và xây dựng giải pháp y tế. **Không áp dụng trực tiếp các con số thống kê này cho môi trường bệnh viện Vinmec tại Việt Nam** mà không thông qua việc tái thẩm định trên dữ liệu nội bộ.
2. **Tương quan và Nhân quả (Correlation vs. Causation):** Các mối liên hệ được tìm thấy (ví dụ: đổi liều insulin, số lần nhập viện trước) là tương quan thống kê, không phải mối quan hệ nhân quả tất yếu.
3. **Cơ sở lâm sàng:** Mọi giải pháp can thiệp và cảnh báo rủi ro phải được đặt dưới sự giám sát và phê duyệt chuyên môn của Hội đồng Y khoa lâm sàng trước khi triển khai thực tế.
