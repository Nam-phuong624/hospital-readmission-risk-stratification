# Phase 7 Bổ Sung: Báo Cáo Kiểm Toán Công Bằng & Thiên Lệch Thuật Toán (Algorithmic Fairness & Bias Audit)
## Dự Án Giảm Tỷ Lệ Tái Nhập Viện 30 Ngày Cho Bệnh Nhân Đái Tháo Đường

---

## 1. Tuyên Bố Bối Cảnh & Đạo Đức Y Tế (Clinical Motivation & Ethics)

### 1.1. Tại sao phải kiểm toán công bằng cho mô hình y tế?
Trong triển khai trí tuệ nhân tạo y tế (Clinical AI/ML), một mô hình đạt AUC tốt trên toàn bộ tập dữ liệu (aggregate performance) vẫn có thể tiềm ẩn những bất bình đẳng nguy hại nếu hiệu năng phân hóa bất cân xứng giữa các nhóm nhân khẩu học nhạy cảm:
- **Tổn hại phân bổ nguồn lực (Allocative Harm):** Khi nguồn lực điều dưỡng theo dõi sau xuất viện bị giới hạn ở Top 20% bệnh nhân nguy cơ cao nhất, nếu mô hình bỏ sót một nhóm nhân khẩu học cụ thể (tỷ lệ Recall thấp), nhóm bệnh nhân đó sẽ bị tước đi quyền tiếp cận chăm sóc hỗ trợ phòng ngừa tái nhập viện.
- **Rủi ro dán nhãn quá mức (Over-flagging / Stigmatization):** Nếu một nhóm nhân khẩu bị phân loại nguy cơ cao với tỷ lệ vượt trội nhưng độ chính xác (Precision) thấp, họ có thể chịu những can thiệp không cần thiết hoặc gây quá tải cho bộ phận điều phối.
- **Tuân thủ đạo đức lâm sàng:** Nguyên tắc cốt lõi của y đức là **"Không gây hại" (Non-maleficence)** và **"Công bằng trong chăm sóc" (Justice)**. Việc kiểm toán thiên lệch là bước bắt buộc trước khi đưa bất kỳ công cụ phân tầng rủi ro nào vào môi trường bệnh viện.

### 1.2. Mục tiêu kỹ thuật
- Đo lường hiệu năng của mô hình XGBoost phân tầng rủi ro (đã chốt ở Phase 4, `random_state=42`) trên từng nhóm thuộc tính nhạy cảm:
  1. **Giới tính (Gender):** Nữ (Female) vs Nam (Male).
  2. **Nhóm tuổi (Age Cohorts):** `<40 tuổi`, `40–70 tuổi`, `$\ge 70$ tuổi`.
  3. **Chủng tộc (Race):** Caucasian, AfricanAmerican, Hispanic, Asian, Other, Unknown.
- Tính toán định lượng các chỉ số chênh lệch công bằng chuẩn mực:
  - **Demographic Parity Difference:** Chênh lệch tỷ lệ được chọn vào diện chăm sóc đặc biệt (Selection Rate).
  - **Equal Opportunity Difference:** Chênh lệch độ nhạy bắt ca tái nhập (Recall@Top20% hay True Positive Rate).
- Đánh giá trung thực rủi ro đạo đức và đề xuất giải pháp kỹ thuật / vận hành giảm thiểu thiên lệch.

---

## 2. Phương Pháp Luận & Khung Đánh Giá Công Bằng (Fairness Framework)

### 2.1. Thiết lập thực nghiệm
- **Tập kiểm tra độc lập:** Toàn bộ **19,802 lượt nhập viện** thuộc Test Set được phân chia theo mã định danh bệnh nhân `patient_nbr` (ngăn ngừa rò rỉ dữ liệu, tỷ lệ tái nhập nền toàn test set: $11.19\%$).
- **Ngưỡng can thiệp vận hành (Decision Threshold):** Giữ đúng ngưỡng vận hành thực tế của dự án: cắt tại **Top 20% điểm số rủi ro cao nhất** ($Score \ge 0.178553$, tương ứng 3,960 ca bệnh được gắn cờ can thiệp).
- **Thư viện thực hiện:** Tính toán độc lập và đối chiếu bằng ma trận phân loại phân tầng, tuân thủ định nghĩa chuẩn mực của thư viện `Fairlearn`.

### 2.2. Các chỉ số đo lường công bằng
1. **Selection Rate ($SR$):** Tỷ lệ bệnh nhân trong nhóm được hệ thống gắn nhãn High Risk (thuộc Top 20% toàn viện).
   $$SR_g = \frac{\sum_{i \in g} \hat{Y}_i}{N_g}$$
2. **Demographic Parity Difference ($DPD$):** Mức chênh lệch tuyệt đối lớn nhất về tỷ lệ lựa chọn giữa các nhóm:
   $$DPD = \max_{g} (SR_g) - \min_{g} (SR_g)$$
   *(Lý tưởng = 0; giá trị càng nhỏ thể hiện cơ hội được nhận hỗ trợ đồng đều giữa các nhóm).*
3. **Recall@Top20% ($TPR$ hay Equal Opportunity):** Tỷ lệ các ca tái nhập viện thực tế được mô hình phát hiện thành công trong nhóm:
   $$Recall_g = \frac{TP_g}{TP_g + FN_g}$$
4. **Equal Opportunity Difference ($EOD$):** Mức chênh lệch tuyệt đối lớn nhất về tỷ lệ bắt đúng ca giữa các nhóm:
   $$EOD = \max_{g} (Recall_g) - \min_{g} (Recall_g)$$
5. **ROC-AUC & Precision@Top20%:** Đo lường năng lực phân tách và độ chuẩn xác của mô hình trên từng nhóm.

---

## 3. Kết Quả Kiểm Toán Chi Tiết Từng Thuộc Tính Nhạy Cảm

*(Nguồn thực nghiệm: `notebooks/06_fairness.py`, Bảng dữ liệu: `outputs/tables/fairness_by_*.csv`, Biểu đồ: `outputs/figures/fairness_recall_by_group.png`)*

### 3.1. Kiểm toán theo Giới tính (Gender Audit)

| Nhóm giới tính | Cỡ mẫu ($N$) | Tỷ lệ mẫu (%) | Tỷ lệ tái nhập thực tế | Selection Rate (Gắn cờ High Risk) | ROC-AUC | Recall@Top20% | Precision@Top20% |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Nữ (Female)** | 10,645 | 53.76% | 11.16% | 20.76% | 0.6743 | 40.66% | 21.86% |
| **Nam (Male)** | 9,157 | 46.24% | 11.23% | 19.12% | 0.6590 | 36.87% | 21.64% |

- **Demographic Parity Difference (DPD):** **1.64 điểm phần trăm (pp)** ($20.76\% - 19.12\%$).
- **Equal Opportunity Difference (EOD):** **3.79 điểm phần trăm (pp)** ($40.66\% - 36.87\%$).
- **Nhận định lâm sàng & vận hành:**
  - Mô hình đạt mức độ công bằng rất cao giữa hai giới tính.
  - Tỷ lệ tái nhập viện thực tế của Nữ ($11.16\%$) và Nam ($11.23\%$) gần như trùng khớp hoàn toàn.
  - Tỷ lệ chọn (Selection Rate) lệch nhẹ 1.64 pp nghiêng về Nữ do nhóm bệnh nhân nữ có tuổi thọ bình quân cao hơn và tỷ lệ đa bệnh kèm theo nhỉnh hơn.
  - Độ chính xác (Precision) hoàn toàn tương đồng ($21.86\%$ so với $21.64\%$), đảm bảo rằng khi một cuộc gọi điều dưỡng được thực hiện, xác suất trúng ca tái nhập giữa bệnh nhân nam và nữ là như nhau.

---

### 3.2. Kiểm toán theo Nhóm tuổi (Age Audit)

| Phân nhóm tuổi | Cỡ mẫu ($N$) | Tỷ lệ mẫu (%) | Tỷ lệ tái nhập thực tế | Selection Rate (Gắn cờ High Risk) | ROC-AUC | Recall@Top20% | Precision@Top20% |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **< 40 tuổi** | 1,284 | 6.48% | 11.45% | 21.96% | **0.7710** | **60.54%** | **31.56%** |
| **40 – 70 tuổi** | 9,644 | 48.70% | 10.60% | 16.75% | 0.6667 | 35.81% | 22.66% |
| **$\ge$ 70 tuổi** | 8,874 | 44.81% | 11.80% | 23.26% | 0.6455 | 38.87% | 19.72% |

- **Demographic Parity Difference (DPD):** **6.51 điểm phần trăm (pp)** (Nhóm $\ge 70$ tuổi được chọn $23.26\%$, nhóm $40-70$ tuổi được chọn $16.75\%$).
- **Equal Opportunity Difference (EOD):** **24.73 điểm phần trăm (pp)** (Nhóm $< 40$ tuổi đạt Recall **60.54%**, trong khi nhóm $40-70$ tuổi chỉ đạt **35.81%**).
- **Đây là chênh lệch lớn nhất được ghi nhận trên toàn bộ hệ thống mô hình.**

---

### 3.3. Kiểm toán theo Chủng tộc / Dân tộc (Race Audit)

| Nhóm chủng tộc | Cỡ mẫu ($N$) | Tỷ lệ mẫu (%) | Tỷ lệ tái nhập thực tế | Selection Rate (Gắn cờ High Risk) | ROC-AUC | Recall@Top20% | Precision@Top20% |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Caucasian** | 14,886 | 75.17% | 11.47% | 20.36% | 0.6658 | 39.66% | 22.34% |
| **AfricanAmerican** | 3,707 | 18.72% | 10.68% | 20.80% | 0.6557 | 37.12% | 19.07% |
| **Hispanic** | 371 | 1.87% | 10.51% | 16.17% | 0.7638 | 41.03% | 26.67% |
| **Asian** | 122 | 0.62% | 8.20% | 11.48% | 0.6750 | 30.00% | 21.43% |
| **Other** | 298 | 1.50% | 8.72% | 14.09% | 0.7059 | 42.31% | 26.19% |
| **Unknown** | 418 | 2.11% | 9.09% | 10.29% | 0.6648 | 21.05% | 18.60% |

- **So sánh 2 nhóm chiếm đa số tuyệt đối (Caucasian vs AfricanAmerican, chiếm 93.89% tập dữ liệu):**
  - **DPD:** **0.44 pp** ($20.80\% - 20.36\%$) — *Gần như đạt mức cân bằng nhân khẩu học hoàn hảo.*
  - **EOD:** **2.54 pp** ($39.66\% - 37.12\%$) — *Khoảng cách rất nhỏ, không có dấu hiệu phân biệt đối xử hệ thống giữa 2 sắc tộc chính.*
- **So sánh trên toàn bộ các nhóm sắc tộc:**
  - **DPD (toàn bộ):** **10.51 pp** (AfricanAmerican $20.80\%$ vs Unknown $10.29\%$; tính riêng các nhóm có tên cụ thể: $9.32$ pp giữa AfricanAmerican $20.80\%$ và Asian $11.48\%$).
  - **EOD (toàn bộ):** **21.26 pp** (Other $42.31\%$ vs Unknown $21.05\%$; tính riêng các nhóm có tên cụ thể: $11.03$ pp giữa Hispanic $41.03\%$ và Asian $30.00\%$).
- **Lưu ý thống kê lâm sàng quan trọng:** Nhóm Asian ($N=122$, chỉ có 10 ca tái nhập thực tế) và Hispanic ($N=371$, 39 ca tái nhập) có cỡ mẫu rất nhỏ. Biên độ sai số chọn mẫu (sampling variance) lớn khiến các chỉ số tỷ lệ ở nhóm này có độ bất định cao, không phản ánh thiên lệch mang tính quy luật.

---

## 4. Phân Tích Chuyên Sâu: Tại Sao Có Sự Chênh Lệch Lớn Theo Nhóm Tuổi?

### 4.1. Bản chất của khoảng cách Equal Opportunity (24.73 pp)
Mô hình phát hiện được tới **60.54%** ca tái nhập ở bệnh nhân trẻ tuổi ($<40$), nhưng chỉ phát hiện được **35.81%** ở nhóm trung niên ($40-70$) và **38.87%** ở người cao tuổi ($\ge 70$). Đồng thời, AUC của nhóm trẻ tuổi đạt tới **0.7710**, vượt trội so với **0.6455** của nhóm người già.

Tại sao mô hình lại "thông minh" hơn rõ rệt khi dự báo người trẻ tuổi?

### 4.2. Cơ chế giải thích dịch tễ & lâm sàng
1. **Tính chất bệnh lý của người trẻ tuổi đái tháo đường ($<40$ tuổi):**
   - Đa số bệnh nhân nhập viện trong nhóm này là Đái tháo đường Tuýp 1 hoặc Tuýp 2 thể cấp tính với các biến chứng rầm rộ (nhiễm toan ceton do đái tháo đường - DKA, tăng áp lực thẩm thấu, hoặc hạ đường huyết nặng).
   - Tín hiệu lâm sàng trong hồ sơ bệnh án (EHR) của nhóm này rất rõ nét: số lần nhập viện cấp cứu dày đặc, phác đồ insulin liều cao hoặc thay đổi liên tục, số ngày nằm viện tập trung. Đây là các "tín hiệu mạnh" (strong acute signals) mà mô hình học máy rất dễ nhận diện, tạo ra khả năng phân tách sắc bén (AUC 0.7710).
2. **Tính chất bệnh lý của người cao tuổi ($\ge 70$ tuổi):**
   - Bệnh nhân cao tuổi đái tháo đường luôn đi kèm hội chứng **đa bệnh đồng mắc (multimorbidity)**: suy tim, bệnh thận mạn tính, tai biến mạch máu não, thoái hóa khớp, suy kiệt tuổi già.
   - Nguyên nhân tái nhập viện trong 30 ngày ở người cao tuổi thường **không nằm thuần túy ở chỉ số đường huyết**, mà bắt nguồn từ các yếu tố phi lâm sàng ngoài bệnh viện:
     - Suy giảm chức năng tự chăm sóc (ADL decline), té ngã tại nhà.
     - Thiếu hụt người chăm sóc (caregiver burden/absence).
     - Quên thuốc do suy giảm nhận thức (cognitive decline).
     - Tác dụng phụ tương tác đa thuốc (polypharmacy).
   - Những yếu tố đời sống này **hoàn toàn không được thu thập trong dữ liệu hành chính/EHR của bệnh viện** (Unobserved Confounders). Do đó, dữ liệu đầu vào chứa nhiều "nhiễu lâm sàng", kéo trần phân tách của mô hình xuống thấp (AUC 0.6455).

### 4.3. Đánh giá rủi ro thiên lệch
- **Mô hình có dìm người già không?**
  Không. Trên thực tế, tỷ lệ chọn (Selection Rate) của nhóm $\ge 70$ tuổi là **23.26%**, cao nhất trong cả 3 nhóm tuổi. Mô hình gắn cờ can thiệp cho người cao tuổi nhiều hơn vì họ tích lũy nhiều chẩn đoán và thời gian nằm viện dài hơn.
- **Rủi ro thực sự là gì?**
  Rủi ro nằm ở việc mô hình **bỏ sót 61.13% ca tái nhập ở người cao tuổi** (Recall chỉ 38.87%), trong khi đây là nhóm dễ bị tổn thương nhất. Bác sĩ và điều dưỡng nếu quá phụ thuộc vào mô hình sẽ chủ quan với những bệnh nhân cao tuổi không bị gắn cờ đỏ.

---

## 5. Rủi Ro Đạo Đức & Tác Động Vận Hành (Ethical & Operational Implications)

### 5.1. Rủi ro đối với nhóm trung niên (40–70 tuổi)
- Nhóm $40-70$ tuổi chiếm tới **48.70% toàn bộ lượt khám** (lực lượng lao động chính).
- Tuy nhiên, nhóm này có tỷ lệ được chọn thấp nhất (**16.75%**, thấp hơn mức phân bổ 20% chung) và tỷ lệ bỏ sót ca tái nhập cao nhất (**64.19%**, Recall 35.81%).
- **Rủi ro đạo đức:** Sự "bình lặng" về mặt triệu chứng lâm sàng cấp tính ở lứa tuổi này khiến thuật toán đánh giá thấp nguy cơ của họ so với người già và người trẻ cấp tính, tạo ra lỗ hổng chăm sóc dự phòng sau xuất viện.

### 5.2. Rủi ro đối với các nhóm thiểu số có mẫu nhỏ (Asian, Hispanic)
- Nhóm Asian chỉ có $N=122$ ($0.62\%$ mẫu test), selection rate chỉ đạt $11.48\%$.
- Mặc dù tỷ lệ tái nhập thực tế của nhóm Asian trong mẫu thấp hơn ($8.20\%$), việc mô hình huấn luyện trên tập dữ liệu mà $75\%$ là người da trắng (Caucasian) khiến các đặc trưng văn hóa, chế độ ăn, hoặc đáp ứng thuốc của nhóm thiểu số không được học đầy đủ.
- Việc áp dụng nguyên si mô hình này cho quần thể bệnh viện có cơ cấu nhân khẩu khác (chẳng hạn bệnh viện tại Việt Nam) sẽ gây ra sai số hệ thống nghiêm trọng.

---

## 6. Khuyến Nghị Vận Hành & Kế Hoạch Giảm Thiểu Thiên Lệch (Mitigation Strategies)

Để đảm bảo tính công bằng và an toàn người bệnh khi triển khai thực tế, chúng tôi đề xuất 3 giải pháp bổ trợ:

### 6.1. Hiệu chỉnh ngưỡng phân tầng theo nhóm tuổi (Age-Stratified Thresholding)
- Thay vì dùng một ngưỡng cắt cứng duy nhất ($Top 20\%$ toàn viện cho mọi lứa tuổi), giải pháp vận hành nên áp dụng **ngưỡng động theo nhóm tuổi**:
  - Đối với nhóm $40-70$ tuổi: Hạ nhẹ ngưỡng điểm kích hoạt can thiệp để nâng tỷ lệ chọn từ $16.75\%$ lên mức tương đương $20\%$, giúp cải thiện độ bao phủ các ca tái nhập tiềm ẩn.
  - Đối với nhóm $\ge 70$ tuổi: Bổ sung một **Quy tắc an toàn lâm sàng (Clinical Hard Rule)**: Mọi bệnh nhân $\ge 75$ tuổi có sống đơn thân hoặc có từ 2 bệnh mạn tính trở lên đều tự động được xếp vào diện theo dõi 48h, bất kể điểm số của mô hình học máy là bao nhiêu.

### 6.2. Thu thập thêm các biến số xác định sức khỏe xã hội (Social Determinants of Health - SDoH)
- Bổ sung vào hồ sơ xuất viện các trường thông tin:
  - Tình trạng người chăm sóc tại nhà (Caregiver availability: Có/Không).
  - Khả năng tự đi lại và sinh hoạt (ADL score / Barthel Index).
  - Tình trạng tài chính / bảo hiểm chi trả thuốc đái tháo đường.
- Việc bổ sung các biến số này sẽ giúp mô hình "nhìn thấy" nguyên nhân tái nhập thực sự của nhóm bệnh nhân cao tuổi, từ đó nâng trần AUC và cân bằng chỉ số Equal Opportunity.

### 6.3. Thiết lập hệ thống giám sát thuật toán định kỳ (Algorithmic Drift & Fairness Monitoring)
- Thiết lập dashboard theo dõi hàng tháng các chỉ số công bằng:
  - Giám sát tỷ lệ gắn cờ High Risk và tỷ lệ tái nhập thực tế theo từng khoa, từng nhóm tuổi, và từng giới tính.
  - Nếu khoảng cách Equal Opportunity Difference giữa các nhóm vượt quá ngưỡng cảnh báo ($>15$ pp đối với các nhóm có $N \ge 1,000$), hệ thống sẽ tự động kích hoạt quy trình xem xét lâm sàng và tái chuẩn hóa mô hình.

---

## 7. Kết Luận Kiểm Toán

1. **Về Giới tính & Sắc tộc chính:** Mô hình đạt độ công bằng cao. Khoảng cách Demographic Parity giữa Nam và Nữ chỉ **1.64 pp**, giữa Caucasian và AfricanAmerican chỉ **0.44 pp**. Không có bằng chứng về sự phân biệt đối xử hệ thống giữa hai giới hay hai sắc tộc chủ đạo.
2. **Về Nhóm tuổi:** Xuất hiện chênh lệch lớn về Equal Opportunity (**24.73 pp**). Mô hình nhạy bén vượt trội với người trẻ tuổi (Recall $60.54\%$, AUC $0.7710$) nhưng gặp khó khăn hơn ở người cao tuổi (Recall $38.87\%$, AUC $0.6455$) do hạn chế cố hữu của dữ liệu EHR hành chính thiếu các biến số xã hội và chức năng sống.
3. **Ý nghĩa vận hành:** Mô hình **an toàn để hỗ trợ phân loại**, nhưng **phải đi kèm quy tắc an toàn lâm sàng dành cho người cao tuổi** và không được dùng làm căn cứ duy nhất để từ chối dịch vụ chăm sóc sau xuất viện.
