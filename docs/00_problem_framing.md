# Phase 1: Problem Framing — Giảm Tỷ Lệ Tái Nhập Viện 30 Ngày

## 1. Problem Statement (Tuyên bố bài toán)
Tái nhập viện ngoài kế hoạch trong vòng 30 ngày sau khi xuất viện (30-day unplanned readmission) là một chỉ dấu quan trọng phản ánh chất lượng điều trị nội trú và tính liên tục của chăm sóc y tế (care continuity). 
Đối với nhóm bệnh nhân đái tháo đường (diabetes), tái nhập viện không chỉ gây tổn hại lớn đến sức khỏe, tâm lý và gánh nặng tài chính của người bệnh mà còn gây lãng phí nguồn lực giường bệnh, tăng chi phí vận hành cho bệnh viện và nguy cơ bị phạt tài chính (theo các mô hình quản lý chất lượng bảo hiểm như HRRP tại Mỹ hoặc tiêu chuẩn JCI/quốc tế tại các hệ thống y tế như Vinmec).

**Vấn đề cốt lõi:** Bệnh viện chưa có cơ chế tự động sàng lọc và phân tầng rủi ro bệnh nhân trước thời điểm xuất viện. Đội ngũ y tế không đủ nguồn lực để theo dõi chuyên sâu tất cả bệnh nhân sau xuất viện, dẫn đến việc bỏ sót những ca có nguy cơ chuyển biến xấu trong 30 ngày đầu tại nhà.

**Mục tiêu dự án:** Xây dựng hệ thống giải pháp phân tích dữ liệu và mô hình phân tầng rủi ro (risk stratification) nhằm nhận diện sớm top 20% bệnh nhân có nguy cơ cao nhất tại thời điểm xuất viện, từ đó kích hoạt gói can thiệp chăm sóc chủ động (chăm sóc chuyển tiếp & theo dõi 48h) giúp giảm tỷ lệ tái nhập viện 30 ngày.

---

## 2. 4 Câu Hỏi Nghiệp Vụ Cốt Lõi (Business Questions)

1. **Ai là nhóm bệnh nhân có nguy cơ tái nhập viện 30 ngày cao nhất?**
   - *Diễn giải nghiệp vụ:* Đặc điểm nhân khẩu học (độ tuổi), tiền sử sử dụng dịch vụ y tế (số lần cấp cứu, số lần nhập viện trong năm qua) và mức độ phức tạp bệnh lý (số lượng chẩn đoán kèm theo, thời gian nằm viện) tác động như thế nào đến nguy cơ tái nhập viện?

2. **Chế độ điều trị và sử dụng thuốc có ảnh hưởng thế nào đến kết quả tái nhập viện?**
   - *Diễn giải nghiệp vụ:* Việc thay đổi phác đồ thuốc đái tháo đường (đặc biệt là insulin) trong đợt điều trị hoặc việc xét nghiệm HbA1c/đường huyết lúc nằm viện có liên quan đến việc bệnh nhân ổn định hay phải quay lại viện sớm hay không? Bệnh nhân có được hướng dẫn dùng thuốc đầy đủ trước khi về nhà không?

3. **Khoa lâm sàng và tuyến xuất viện nào cần ưu tiên can thiệp?**
   - *Diễn giải nghiệp vụ:* Tỷ lệ tái nhập viện phân bổ ra sao theo chuyên khoa tiếp nhận và hình thức xuất viện? Những khoa có lưu lượng bệnh nhân tiểu đường cao và tỷ lệ tái nhập cao sẽ là nơi thí điểm quy trình can thiệp đầu tiên để tối ưu hóa nguồn lực.

4. **Năng lực can thiệp của bệnh viện là bao nhiêu và ngưỡng kích hoạt (action threshold) tối ưu là gì?**
   - *Diễn giải nghiệp vụ:* Với nguồn lực điều dưỡng/chăm sóc khách hàng có hạn, bệnh viện có thể theo dõi sát tối đa bao nhiêu % bệnh nhân xuất viện? Làm thế nào để mô hình bắt trúng tối đa số ca sẽ tái nhập viện trong ngân sách vận hành cho phép (recall tại top 20% nguy cơ cao)?

---

## 3. Bộ Chỉ Số Đánh Giá (3 Core KPIs)

| KPI | Loại chỉ số | Định nghĩa & Công thức | Mục tiêu & Ý nghĩa nghiệp vụ |
| :--- | :--- | :--- | :--- |
| **1. 30-Day Readmission Rate** | Business Primary KPI | $\frac{\text{Số ca tái nhập viện không hẹn trong 30 ngày}}{\text{Tổng số ca xuất viện đủ điều kiện}} \times 100\%$ | Giảm từ baseline (dự kiến ~11-12%) xuống giảm tương đối 15-20% ở nhóm được can thiệp; phản ánh trực tiếp chất lượng chăm sóc và hiệu quả can thiệp. |
| **2. High-Risk Capture Rate (Recall @ Top 20%)** | Model / Operational KPI | $\frac{\text{Số ca tái nhập viện thực tế nằm trong Top 20% điểm rủi ro}}{\text{Tổng số ca tái nhập viện thực tế}} \times 100\%$ | Mục tiêu đạt $\ge 40-50\%$. Đảm bảo với ngân sách tập trung cho 20% bệnh nhân nặng nhất, đội ngũ y tế bao phủ được phần lớn các ca có nguy cơ phát sinh biến chứng. |
| **3. Post-Discharge 48h Contact & Follow-up Compliance** | Process KPI | $\frac{\text{Số bệnh nhân nhóm nguy cơ cao hoàn thành cuộc gọi 48h & tái khám đúng hẹn}}{\text{Tổng số bệnh nhân nhóm nguy cơ cao xuất viện}} \times 100\%$ | Mục tiêu đạt $\ge 85\%$. Đo lường mức độ tuân thủ quy trình can thiệp của điều dưỡng và sự hợp tác của người bệnh, là điều kiện tiên quyết để can thiệp thành công. |

---

## 4. Phạm vi & Giả định (Scope & Assumptions)
- **Đối tượng:** Bệnh nhân nội trú đái tháo đường xuất viện về nhà hoặc chuyển tuyến chăm sóc ban đầu. Loại trừ các trường hợp tử vong trong viện hoặc chuyển sang chăm sóc giảm nhẹ (hospice).
- **Tính chất giải pháp:** Đóng vai trò là hệ thống hỗ trợ ra quyết định lâm sàng (Clinical Decision Support), không thay thế chẩn đoán chuyên môn của bác sĩ điều trị.
- **Tính khả thi:** Dữ liệu đầu vào cho việc phân tầng rủi ro phải sẵn sàng tại thời điểm bác sĩ ký y lệnh xuất viện (Electronic Health Record - EHR).
