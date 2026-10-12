# Phase 5: Product Requirements Document (PRD)
# Gói Can Thiệp Chăm Sóc Chuyển Tiếp & Theo Dõi 48 Giờ Cho Bệnh Nhân Đái Tháo Đường Nguy Cơ Cao (Post-Discharge 48h Transitional Care Protocol)

---

## 1. Bối Cảnh & Tuyên Bố Vấn Đề (Context & Problem Statement)
- **Vấn đề:** Phân tích dữ liệu 99,343 đợt điều trị cho thấy nhóm 20% bệnh nhân có điểm rủi ro cao nhất (High Risk) có tỷ lệ tái nhập viện lên tới **21.74%** (gấp 3.3 lần nhóm nguy cơ thấp 6.53%). 
- **Nguyên nhân gốc rễ:** Khoảng trống chăm sóc (care gap) trong 48 - 72 giờ đầu tiên sau xuất viện. Bệnh nhân về nhà bị gián đoạn giám sát y tế, gặp khó khăn trong việc thích ứng liều Insulin mới, sai sót khi dùng thuốc hoặc chế độ ăn uống không phù hợp, dẫn đến biến chứng cấp tính và phải tái nhập cấp cứu.
- **Tầm nhìn sản phẩm:** Thiết lập một quy trình chuyển tiếp chăm sóc chủ động, tích hợp cảnh báo rủi ro từ hệ thống Bệnh án Điện tử (EHR), kết hợp tư vấn đối soát thuốc tại giường và cuộc gọi chuyên môn trong vòng 48 giờ sau xuất viện, nhằm bảo vệ nhóm bệnh nhân dễ tổn thương nhất.

---

## 2. Mục Tiêu Dự Án & Chỉ Số Đo Lường (Goals & Success Metrics)

### 2.1. Mục tiêu kinh doanh (Business Goals)
- Giảm tỷ lệ tái nhập viện 30 ngày ở nhóm bệnh nhân nguy cơ cao — hiệu quả can thiệp sẽ được đo lường khách quan thông qua thử nghiệm lâm sàng đối chứng A/B test.
- Tối ưu hóa hiệu quả vận hành: Giảm thiểu các đợt nằm viện ngoài kế hoạch, gia tăng chỉ số hài lòng của người bệnh (NPS/CSAT) và nâng cao tiêu chuẩn chất lượng lâm sàng quốc tế (JCI).

### 2.2. Chỉ số thành công (Success Metrics)
| Loại chỉ số | Tên chỉ số | Hiện trạng (Baseline) | Mục tiêu (Target) | Phương pháp đo lường |
| :--- | :--- | :---: | :---: | :--- |
| **Primary KPI** | Mức giảm tương đối tỷ lệ tái nhập 30 ngày ở nhóm High Risk | 21.74% | **Đo lường bằng A/B test** *(không gắn con số đích giả định)* | So sánh tỷ lệ tái nhập 30 ngày giữa nhóm can thiệp vs đối chứng qua A/B test. |
| **Process KPI 1** | Tỷ lệ tiếp cận thành công trong 48h (48h Call Reach Rate) | 0% | **$\ge 85\%$** *(mục tiêu vận hành do nhóm đặt, không phải kết quả từ data)* | Tỷ lệ bệnh nhân nhóm High Risk hoàn thành cuộc gọi rà soát trong 48h sau xuất viện. |
| **Process KPI 2** | Tỷ lệ rà soát thuốc tại giường (Teach-Back Medication Reconciliation) | ~30% (tản mạn) | **$\ge 90\%$** *(mục tiêu vận hành do nhóm đặt, không phải kết quả từ data)* | % bệnh nhân được Dược sĩ lâm sàng xác nhận hiểu đúng phác đồ tiêm insulin trước khi rời viện. |
| **Guardrail KPI** | Thời gian chờ làm thủ tục xuất viện (Discharge Delay) | Baseline | **Không tăng quá 15 phút** *(mục tiêu vận hành do nhóm đặt)* | Đảm bảo quy trình can thiệp tại giường không gây ứ nghẽn quy trình xuất viện chung. |
| **Guardrail KPI** | Tỷ lệ bệnh nhân phàn nàn về cuộc gọi (Negative Feedback) | 0% | **$< 1.5\%$** *(mục tiêu vận hành do nhóm đặt)* | Đảm bảo tần suất và nội dung cuộc gọi tôn trọng sự riêng tư và hữu ích. |

---

## 3. Đối Tượng Người Dùng & Các Bên Liên Quan (User Personas)

1. **Bệnh nhân & Người chăm sóc (Caregiver):** 
   - Thường là người cao tuổi ($\ge 65$ tuổi), có người thân hỗ trợ tiêm thuốc, hay lo âu về biến chứng tụt đường huyết ban đêm.
   - *Nhu cầu:* Cần được hướng dẫn liều thuốc rõ ràng, có đầu mối liên hệ khẩn cấp khi thấy chóng mặt, mệt mỏi.
2. **Điều dưỡng quản lý ca bệnh (Discharge Case Manager / Nurse Navigator):**
   - Chịu trách nhiệm thực hiện cuộc gọi 48h, đánh giá triệu chứng theo kịch bản chuẩn và phân loại nguy cơ.
   - *Nhu cầu:* Cần danh sách phân tầng rủi ro rõ ràng trên hệ thống EHR mỗi sáng, form ghi nhận kết quả nhanh gọn.
3. **Dược sĩ lâm sàng (Clinical Pharmacist):**
   - Chịu trách nhiệm rà soát tương tác thuốc và trực tiếp hướng dẫn kỹ thuật tiêm insulin trước khi xuất viện.
   - *Nhu cầu:* Nhận thông báo sớm trước giờ xuất viện 2-4 tiếng đối với các ca High Risk có thay đổi liều Insulin.
4. **Bác sĩ điều trị / Bác sĩ Nội tiết:**
   - Tiếp nhận thông tin leo thang (escalation) từ điều dưỡng nếu bệnh nhân có dấu hiệu bất thường để xử lý kịp thời.

---

## 4. Mô Tả Luồng Quy Trình Can Thiệp (Intervention Workflow)

```
[Bác sĩ tạo Y lệnh Xuất viện trên EHR]
                  │
                  ▼
   [Hệ thống chạy Mô hình Phân tầng]
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
 [Low/Med Risk]      [High Risk - Top 20%]
  Quy trình          Kích hoạt Gói Can Thiệp 48h
  tiêu chuẩn                │
                            ├─────────────────────────────────────────┐
                            ▼                                         ▼
                 [Bước 1: Trước xuất viện 2-4h]            [Tự động đặt lịch hẹn]
                 Dược sĩ lâm sàng tư vấn tại giường:       Lịch tái khám N+7 ngày
                 - Hướng dẫn kỹ thuật tiêm Insulin          hoặc Telehealth
                 - Đối soát thuốc (Teach-Back method)
                 - Cấp sổ tay theo dõi đường huyết
                            │
                            ▼
                 [Bước 2: Trong vòng 48h sau xuất viện]
                 Điều dưỡng gọi điện thoại chủ động (Checklist 5 điểm):
                 1. Xác nhận đã mua đủ và uống/tiêm đúng thuốc?
                 2. Đo chỉ số đường huyết sáng nay là bao nhiêu?
                 3. Có triệu chứng hạ đường huyết (run, vã mồ hôi, đói cồn cào)?
                 4. Vết mổ/vết loét chân có dấu hiệu sưng đau, chảy dịch?
                 5. Xác nhận lại lịch tái khám tuần tới.
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
       [Bình thường]                 [Có dấu hiệu bất thường]
   Ghi chú hồ sơ; hẹn            [Bước 3: Leo thang xử lý (Escalation)]
   tái khám đúng lịch            - Báo động đỏ: Gọi Cấp cứu 115 / Đến viện ngay
                                 - Báo động vàng: Chuyển bác sĩ điều trị tư vấn
                                   điều chỉnh liều từ xa trong vòng 2 giờ
```

---

## 5. Yêu Cầu Chức Năng & Kỹ Thuật (Functional Requirements)

### 5.1. Tích Hợp Hệ Thống EHR & Phân Tầng Tự Động
- **FR-01 (Real-time Risk Scoring):** Khi bác sĩ nhấn nút "Lập kế hoạch xuất viện" (Discharge Order Initiation), hệ thống gọi API mô hình để tính toán điểm rủi ro và gán nhãn: `High Risk (Top 20%)`, `Medium Risk`, `Low Risk`.
- **FR-02 (High-Risk Banner & Alert):** Hiển thị biểu tượng cảnh báo màu đỏ kèm khuyến nghị: *"Bệnh nhân thuộc nhóm rủi ro cao tái nhập viện 30 ngày (Dự báo: 21.7%). Khuyến nghị kích hoạt Gói Chăm sóc chuyển tiếp 48h."*
- **FR-03 (Automated Task Dispatch):** Tự động tạo 2 công việc trên bảng phân công:
  1. Task gửi Dược lâm sàng: Rà soát thuốc tại giường trước khi ký giấy ra viện.
  2. Task gửi Đội ngũ Chăm sóc sau xuất viện: Cuộc gọi theo dõi vào ngày N+2 (trong 48h).

### 5.2. Công Cụ Hỗ Trợ Cuộc Gọi (Nurse Call Portal)
- **FR-04 (Interactive Call Form):** Cung cấp giao diện form điện tử gồm 5 câu hỏi trắc nghiệm chuẩn hóa (đường huyết, triệu chứng cơ năng, tuân thủ thuốc, tâm lý, dinh dưỡng).
- **FR-05 (Red Flag Auto-Trigger):** Nếu điều dưỡng tích chọn: "Đường huyết < 70 mg/dL kéo dài" hoặc "Khó thở, đau tức ngực", hệ thống ngay lập tức kích hoạt tin nhắn khẩn cấp tới Bác sĩ trực phụ trách ca.

---

## 6. Đánh Giá Hiệu Quả Chi Phí (Cost-Benefit Consideration)

Phân tích chi phí-lợi ích cần dữ liệu viện phí nội bộ, nằm ngoài phạm vi dữ liệu hiện có; sẽ thực hiện sau khi có kết quả A/B.

---

## 7. Lộ Trình Triển Khai (Rollout Plan)
- **Tuần 1 - 2:** Hoàn thiện tích hợp API chấm điểm rủi ro vào giao diện EHR thử nghiệm (Staging). Đào tạo quy trình Teach-back cho Dược sĩ lâm sàng.
- **Tuần 3 - 4:** Thí điểm giai đoạn 1 (Pilot Phase) tại 2 khoa có rủi ro cao nhất: Khoa Thận - Tiết niệu và Khoa Nội tổng quát (Family/Internal Medicine).
- **Tuần 5 - 12:** Tiến hành thử nghiệm A/B Testing có đối chứng ngẫu nhiên (Chi tiết tại Phase 6).
