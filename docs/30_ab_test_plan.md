# Phase 6: Kế Hoạch Thử Nghiệm Lâm Sàng Đối Chứng Ngẫu Nhiên (A/B Testing Plan)
# Đánh Giá Hiệu Quả Gói Can Thiệp Chăm Sóc Chuyển Tiếp & Theo Dõi 48h

---

## 1. Giả Thuyết Thống Kê (Hypothesis Formulation)
- **Giả thuyết Không ($H_0$):** Tỷ lệ tái nhập viện trong vòng 30 ngày ở nhóm bệnh nhân nguy cơ cao được can thiệp gói chăm sóc chuyển tiếp 48h ($p_{\text{Treatment}}$) không có sự khác biệt so với nhóm nhận chăm sóc tiêu chuẩn ($p_{\text{Control}}$):
  $$H_0: p_{\text{Treatment}} = p_{\text{Control}}$$
- **Giả thuyết Đối ($H_1$):** Tỷ lệ tái nhập viện trong vòng 30 ngày ở nhóm can thiệp thấp hơn có ý nghĩa thống kê so với nhóm đối chứng:
  $$H_1: p_{\text{Treatment}} < p_{\text{Control}}$$
- **Mức ý nghĩa thống kê ($\alpha$):** 0.05 (độ tin cậy 95%, kiểm định hai phía để đảm bảo tính thận trọng lâm sàng).
- **Lực kiểm định thống kê ($1 - \beta$):** 0.80 (80% Statistical Power).

---

## 2. Thiết Kế Thử Nghiệm & Chiến Lược Phân Nhóm (Experimental Design)

### 2.1. Đơn vị ngẫu nhiên hóa (Randomization Unit)
- **Đơn vị phân nhóm:** Ngẫu nhiên hóa theo **Mã bệnh nhân (`patient_nbr`)** tại thời điểm xuất viện.
- **Lý do nghiệp vụ:** Tránh hiện tượng rò rỉ can thiệp (contamination) khi cùng một bệnh nhân nhập viện nhiều lần trong giai đoạn thử nghiệm. Nếu bệnh nhân đã được chỉ định vào Nhóm B ở lần nhập viện đầu, các lần nhập viện tiếp theo (nếu có) sẽ tiếp tục duy trì phác đồ của Nhóm B.

### 2.2. Tiêu chuẩn chọn & loại trừ (Eligibility Criteria)
- **Tiêu chuẩn chọn (Inclusion):**
  1. Bệnh nhân nội trú chẩn đoán Đái tháo đường (Type 1 hoặc Type 2).
  2. Mô hình máy học phân loại vào nhóm **Nguy cơ cao (High Risk - Top 20% điểm rủi ro)** tại thời điểm ra quyết định xuất viện.
  3. Bệnh nhân hoặc người giám hộ đồng ý tham gia chương trình theo dõi sau xuất viện và có số điện thoại liên lạc hợp lệ.
- **Tiêu chuẩn loại trừ (Exclusion):**
  1. Bệnh nhân xuất viện chuyển viện cấp cứu, chuyển sang trung tâm chăm sóc giảm nhẹ (hospice) hoặc tử vong nội viện.
  2. Bệnh nhân không thể giao tiếp qua điện thoại và không có người nhà chăm sóc.

---

## 3. Mô Tả Chi Tiết Hai Nhóm Thử Nghiệm (Study Arms)

| Tiêu chí | Nhóm A: Đối chứng (Control Arm - 50%) | Nhóm B: Can thiệp (Treatment Arm - 50%) |
| :--- | :--- | :--- |
| **Quy trình xuất viện** | **Chăm sóc tiêu chuẩn (Standard of Care):** Bác sĩ ký đơn thuốc xuất viện; điều dưỡng khoa bàn giao sổ y bạ và hướng dẫn chung; hẹn tái khám thông thường sau 30 ngày. | **Gói Can Thiệp Chăm Sóc Chuyển Tiếp Tăng Cường:**<br>1. **Teach-Back tại giường:** Dược sĩ lâm sàng đối soát thuốc trực tiếp, hướng dẫn kỹ thuật tiêm insulin và nhận biết dấu hiệu hạ đường huyết.<br>2. **Sổ tay tự quản lý:** Cấp phát cẩm nang ghi chép chỉ số đường huyết mao mạch tại nhà. |
| **Theo dõi sau xuất viện** | Không có cuộc gọi chủ động (bệnh nhân tự liên hệ nếu có nhu cầu phát sinh). | **Cuộc gọi chủ động 48 giờ:** Điều dưỡng chuyên trách thực hiện cuộc gọi có cấu trúc rà soát 5 điểm kiểm tra; kích hoạt kênh hỗ trợ khẩn cấp (Fast-track escalation) nếu chỉ số đường huyết vượt ngưỡng nguy hiểm. |
| **Lịch hẹn tái khám** | Hẹn khám định kỳ sau 30 ngày. | Đặt trước lịch hẹn khám chuyên khoa sớm (ngày N+7 đến N+10) hoặc tư vấn Telehealth trực tuyến. |

---

## 4. Hệ Thống Chỉ Số Đo Lường (Metrics Framework)

### 4.1. Chỉ số chính (Primary Endpoint)
- **Tỷ lệ tái nhập viện không hẹn trước trong 30 ngày (30-Day Unplanned Readmission Rate):**
  $$\text{Readmission Rate} = \frac{\text{Số bệnh nhân tái nhập viện nội trú trong 30 ngày}}{\text{Tổng số bệnh nhân trong nhóm}} \times 100\%$$

### 4.2. Chỉ số phụ (Secondary Endpoints)
- **Tỷ lệ tuân thủ cuộc gọi 48h (48h Call Adherence Rate):** Tỷ lệ bệnh nhân nhóm can thiệp hoàn thành cuộc gọi đúng hạn (Mục tiêu $\ge 85\%$).
- **Tỷ lệ đến khám lại theo hẹn N+7 (Early Follow-up Compliance):** Đo lường sự gắn kết của bệnh nhân với hệ thống ngoại trú.
- **Thời gian trung bình đến khi tái nhập viện (Time-to-Readmission):** Phân tích xem can thiệp có giúp kéo dài khoảng thời gian an toàn của người bệnh tại nhà hay không.

### 4.3. Chỉ số bảo vệ (Guardrail Metrics)
- **Tỷ lệ đến khám Cấp cứu không nhập viện (ED Treat-and-Release Visits):** Đảm bảo cuộc gọi không làm bệnh nhân hoảng sợ và đổ xô đến phòng cấp cứu với các triệu chứng nhẹ.
- **Thời gian xử lý xuất viện trung bình (Discharge Turnaround Time):** Đảm bảo thời gian đối soát thuốc tại giường không làm chậm trễ giờ trả phòng bệnh (> 15 phút).
- **Tỷ lệ phàn nàn của khách hàng (Patient Complaint Rate):** Mục tiêu duy trì $< 1.5\%$.

---

## 5. Tính Toán Cỡ Mẫu Thống Kê Theo Dải Hiệu Ứng (Sample Size by Effect Size Table)

Cỡ mẫu được tính toán bằng mô hình hai tỷ lệ độc lập (Two-Proportion Z-Test / `statsmodels.stats.power.NormalIndPower`, kiểm định 2 phía, $\alpha = 0.05$, Power = $80\%$) dựa trên tỷ lệ nền đo được từ tập kiểm tra:
- **Baseline High-Risk Readmission Rate ($p_1$):** **21.74%** (số liệu đo được trực tiếp từ dữ liệu thực tế).
- Thay vì ấn định một mức giảm duy nhất, bảng dưới đây thể hiện cỡ mẫu cần thiết tương ứng với từng mức giảm tối thiểu có thể phát hiện (Minimum Detectable Effect - MDE) từ 2 đến 7 điểm phần trăm:

*(Nguồn xuất bản: `outputs/tables/ab_sample_size_by_effect.csv`)*

| MDE (Điểm phần trăm) | Tỷ lệ kỳ vọng sau can thiệp ($p_2$) | Cỡ mẫu mỗi nhánh ($N_{\text{arm}}$) | Tổng cỡ mẫu ($N_{\text{total}}$) | Tổng cỡ mẫu dự phòng mất dấu 5% |
| :---: | :---: | :---: | :---: | :---: |
| **2 pp** | 19.74% | 6,448 | 12,896 | **13,575** |
| **3 pp** | 18.74% | 2,813 | 5,626 | **5,923** |
| **4 pp** | 17.74% | 1,551 | 3,102 | **3,266** |
| **5 pp** | 16.74% | 972 | 1,944 | **2,047** |
| **6 pp** | 15.74% | 661 | 1,322 | **1,392** |
| **7 pp** | 14.74% | 474 | 948 | **998** |

### Diễn giải phương pháp luận:
Hiệu ứng can thiệp kỳ vọng càng nhỏ (MDE thấp) thì cỡ mẫu yêu cầu càng lớn và thời gian thử nghiệm càng kéo dài, trong khi kỳ vọng mức giảm lớn (MDE cao) đòi hỏi can thiệp lâm sàng phải đủ mạnh để tạo ra sự khác biệt. Đội ngũ nghiên cứu và ban giám đốc bệnh viện sẽ căn cứ vào lưu lượng bệnh nhân thực tế của phân viện để lựa chọn ngưỡng MDE khả thi tương ứng với nguồn lực và khung thời gian cho phép.

---

## 6. Ước Tính Thời Gian Chạy Thử Nghiệm (Duration & Timeline)

Thời gian thử nghiệm phụ thuộc trực tiếp vào ngưỡng MDE được lựa chọn và lưu lượng bệnh nhân nguy cơ cao xuất viện:
- **Nếu chọn MDE = 6 pp ($N \approx 1,392$):** Với lưu lượng ~200 ca nguy cơ cao/tháng, thời gian thu thập mẫu là khoảng **7.0 tháng**.
- **Nếu chọn MDE = 5 pp ($N \approx 2,047$):** Với lưu lượng ~200 ca nguy cơ cao/tháng, thời gian thu thập mẫu là khoảng **10.2 tháng**.
- **Nếu chọn MDE = 4 pp ($N \approx 3,266$):** Cần triển khai đa trung tâm trên toàn hệ thống viện (~350 ca/tháng) để hoàn thành trong **9.3 tháng**.
- Luôn cộng thêm **30 ngày (1 tháng)** theo dõi sau khi bệnh nhân cuối cùng xuất viện để chốt kết quả tái nhập viện 30 ngày.

---

## 7. Kế Hoạch Phân Tích Thống Kê (Statistical Analysis Plan)
1. **Kiểm định tỷ lệ chính (Primary Analysis):** Sử dụng kiểm định Chi-square ($\chi^2$) hoặc Two-proportion Z-test với phân tích theo nguyên tắc ý định điều trị (Intention-To-Treat - ITT).
2. **Hiệu chỉnh đa biến (Multivariate Adjustment):** Sử dụng hồi quy Logistic đa biến để hiệu chỉnh các yếu tố gây nhiễu tiềm tàng (tuổi, số lần nhập viện trước, số lượng bệnh đồng mắc).
3. **Phân tích thời gian sống (Survival Analysis):** Vẽ đường cong Kaplan-Meier so sánh xác suất không tái nhập viện giữa hai nhóm và áp dụng mô hình rủi ro tỷ lệ Cox (Cox Proportional Hazards Model) để ước tính Tỷ số nguy cơ (Hazard Ratio - HR).

---

## 8. Nguyên Tắc An Toàn & Đạo Đức Nghiên Cứu (Safety & Ethics)
- **Quy tắc dừng sớm (Early Stopping Rule):** Thử nghiệm sẽ được xem xét dừng sớm nếu phân tích giữa kỳ (Interim analysis tại thời điểm 50% cỡ mẫu) phát hiện tỷ lệ biến cố bất lợi nghiêm trọng ở nhóm can thiệp tăng đột biến ($p < 0.001$).
- **Bảo mật dữ liệu (HIPAA/GDPR Compliance):** Toàn bộ dữ liệu điểm số rủi ro và thông tin liên lạc được mã hóa và lưu trữ an toàn trên máy chủ bệnh viện, chỉ cấp quyền truy cập cho nhân sự tham gia trực tiếp ca bệnh.
