# Phase 3: Root Cause Analysis — Báo Cáo Phân Tích Yếu Tố Nguy Cơ Tái Nhập Viện

## 1. Tóm Tắt Điều Hành (Executive Summary)
Dựa trên phân tích hồi quy Logistic đa biến (Multivariate Logistic Regression) trên 99,343 lượt điều trị nội trú sạch, chúng tôi chỉ xác nhận các biến đạt ngưỡng ý nghĩa thống kê ($p < 0.05$) là **các yếu tố thúc đẩy độc lập (confirmed independent drivers)**.

### 4 Yếu Tố Nguy Cơ Đã Được Xác Nhận ($p < 0.05$):
1. **Tiền sử số lượt nhập viện năm trước (`num_inpatient`):** Yếu tố dự báo mạnh nhất (Odds Ratio = 1.305, 95% CI [1.249 - 1.362], $p < 0.0001$).
2. **Số lượng chẩn đoán bệnh đồng mắc (`number_diagnoses`):** Mỗi chẩn đoán tăng thêm làm tăng 5.2% rủi ro (OR = 1.052, 95% CI [1.022 - 1.082], $p = 0.0005$).
3. **Bệnh nhân cao tuổi $\ge 70$ (`is_elderly_70plus`):** Tăng 17.2% nguy cơ tái nhập (OR = 1.172, 95% CI [1.022 - 1.344], $p = 0.0233$).
4. **Thời gian nằm viện (`time_in_hospital`):** Mỗi ngày nằm viện tăng thêm làm tăng 2.5% rủi ro (OR = 1.025, 95% CI [1.000 - 1.050], $p = 0.0480$).

### Các Yếu Tố Chỉ Là Tín Hiệu Đơn Biến (Không Còn Ý Nghĩa Thống Kê Trong Đa Biến):
- **Thay đổi liều Insulin (`insulin_down`, `insulin_up`):** Ở phân tích đơn biến, nhóm giảm liều có tỷ lệ tái nhập là 14.22% và tăng liều là 13.33% (so với 10.21% ở nhóm không dùng). Tuy nhiên trong mô hình đa biến, sau khi kiểm soát tiền sử nhập viện và bệnh đồng mắc, `insulin_down` có $p = 0.0677$ và `insulin_up` có $p = 0.2507$. Do đó, đây chỉ là tín hiệu đơn biến, **không đủ bằng chứng thống kê để khẳng định là nguyên nhân độc lập**.
- **Không làm xét nghiệm HbA1c (`no_a1c_test`):**
  1. *Thực tế quan sát được:* Có tới 83.05% đợt điều trị không ghi nhận kết quả HbA1c.
  2. *Liên hệ với tái nhập:* Ở phân tích đa biến, $p = 0.1076$ (OR = 1.146, 95% CI [0.971 - 1.352]); **chưa đủ bằng chứng thống kê** để kết luận việc không đo HbA1c độc lập làm tăng nguy cơ tái nhập.

---

## 2. Bảng Phân Tích Đa Biến Chi Tiết (Nguồn: `outputs/tables/root_cause_multivariate.csv`)

| Nhóm | Biến số (Feature) | Odds Ratio (OR) | 95% CI | Giá trị p | Kết luận thống kê & Diễn giải nghiệp vụ |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **Driver xác nhận** | **Số lần nhập viện năm trước (`num_inpatient`)** | **1.305** | [1.249 - 1.362] | **< 0.0001** | **Xác nhận (p < 0.001):** Mỗi lần nhập viện trước tăng 30.5% nguy cơ. Phản ánh nhóm bệnh nhân kiểm soát ngoại trú thất bại, cần quản lý ca bệnh liên tục. |
| **Driver xác nhận** | **Số lượng chẩn đoán (`number_diagnoses`)** | **1.052** | [1.022 - 1.082] | **0.0005** | **Xác nhận (p < 0.001):** Gánh nặng đa bệnh lý (tim mạch, thận, chuyển hóa) làm tăng nguy cơ tương tác thuốc và diễn tiến nặng. |
| **Driver xác nhận** | **Tuổi cao $\ge 70$ (`is_elderly_70plus`)** | **1.172** | [1.022 - 1.344] | **0.0233** | **Xác nhận (p < 0.05):** Người cao tuổi suy giảm nhận thức và tự chăm sóc, cần sự hỗ trợ của người nhà khi quản lý thuốc. |
| **Driver xác nhận** | **Thời gian nằm viện (`time_in_hospital`)** | **1.025** | [1.000 - 1.050] | **0.0480** | **Xác nhận (p < 0.05):** Nằm viện dài ngày phản ánh tình trạng bệnh cấp tính nặng hoặc biến chứng suy kiệt thể trạng. |
| *Tín hiệu đơn biến* | Liều Insulin bị giảm (`insulin_down`) | 1.272 | [0.983 - 1.646] | 0.0677 | *Không có ý nghĩa đa biến (p > 0.05):* Đơn biến đạt 14.22% nhưng bị triệt tiêu khi kiểm soát số bệnh kèm và số lần nhập viện. |
| *Tín hiệu đơn biến* | Không xét nghiệm HbA1c (`no_a1c_test`) | 1.146 | [0.971 - 1.352] | 0.1076 | *Chưa đủ bằng chứng (p > 0.05):* Dù 83.1% không đo, chưa thể khẳng định đây là nguyên nhân độc lập gây tái nhập. |
| *Tín hiệu đơn biến* | Liều Insulin bị tăng (`insulin_up`) | 1.169 | [0.895 - 1.527] | 0.2507 | *Không có ý nghĩa đa biến (p > 0.05):* Không đủ cơ sở kết luận tăng liều độc lập thúc đẩy tái nhập. |
| *Biến kiểm soát* | Chẩn đoán chính Đái tháo đường (`diag_diabetes`) | 1.108 | [0.875 - 1.404] | 0.3951 | Không có ý nghĩa thống kê độc lập sau khi kiểm soát số chẩn đoán. |
| *Biến kiểm soát* | Chẩn đoán chính Tim mạch (`diag_circulatory`) | 1.082 | [0.926 - 1.264] | 0.3206 | Không có ý nghĩa thống kê độc lập so với nhóm tham chiếu. |
| *Biến kiểm soát* | Số lần cấp cứu năm trước (`num_emergency`) | 1.032 | [0.964 - 1.105] | 0.3595 | Không có ý nghĩa độc lập khi đã có biến `num_inpatient`. |

---

## 3. Diễn Giải Chuyên Sâu 4 Driver Đã Được Xác Nhận

### 3.1. Tiền sử nhập viện nội trú (`num_inpatient` — OR = 1.305, p < 0.0001)
- **Dữ liệu:** Tỷ lệ tái nhập tăng từ 8.59% (người 0 lần nhập viện trước) lên 13.25% (1 lần), 18.89% (2-3 lần) và đạt 31.36% (ở người có $\ge 4$ lần).
- **Ý nghĩa nghiệp vụ:** Bệnh nhân nhập viện nhiều lần trong năm là nhóm đối tượng có bệnh nền phức tạp hoặc không tuân thủ điều trị ngoại trú. Việc xác nhận đây là driver mạnh nhất chỉ ra rằng bệnh viện cần một hệ thống cảnh báo tự động gắn cờ các ca có tiền sử nội trú ngay từ thời điểm nhập viện để lập kế hoạch xuất viện sớm.

### 3.2. Số lượng bệnh đồng mắc (`number_diagnoses` — OR = 1.052, p = 0.0005)
- **Dữ liệu:** Mỗi bệnh đồng mắc bổ sung làm tăng 5.2% tỷ lệ chênh tái nhập viện. 
- **Ý nghĩa nghiệp vụ:** Bệnh nhân đái tháo đường hiếm khi đơn thuần chỉ có rối loạn đường huyết; đa số kèm theo tăng huyết áp, suy tim, bệnh thận mạn tính hoặc bệnh mạch ngoại biên. Sự kết hợp nhiều bệnh lý dẫn đến tình trạng đa thuốc (polypharmacy), làm tăng khả năng tương tác thuốc và khó khăn trong việc tự quản lý tại nhà.

### 3.3. Độ tuổi cao $\ge 70$ (`is_elderly_70plus` — OR = 1.172, p = 0.0233)
- **Dữ liệu:** Bệnh nhân từ 70 tuổi trở lên có nguy cơ tái nhập tăng 17.2% so với nhóm dưới 70 tuổi sau khi hiệu chỉnh các biến số lâm sàng khác.
- **Ý nghĩa nghiệp vụ:** Nhóm người cao tuổi đối mặt với sự suy giảm thị lực (khó đọc nhãn thuốc, khó chỉnh bút tiêm insulin), suy giảm nhận thức nhẹ và dễ bị cô lập xã hội. Quy trình xuất viện cho nhóm này bắt buộc phải có sự hiện diện và hướng dẫn trực tiếp cho người chăm sóc chính (caregiver).

### 3.4. Thời gian nằm viện (`time_in_hospital` — OR = 1.025, p = 0.0480)
- **Dữ liệu:** Mỗi ngày nằm viện tăng thêm tương ứng với mức tăng 2.5% nguy cơ tái nhập.
- **Ý nghĩa nghiệp vụ:** Số ngày nằm viện kéo dài thường liên quan đến đợt điều trị nhiễm trùng nặng, loét bàn chân khó lành hoặc biến chứng hậu phẫu, khiến thể trạng người bệnh suy yếu khi ra viện.

---

## 4. Tách Bạch Vấn Đề Xét Nghiệm HbA1c & Điều Chỉnh Thuốc

### 4.1. Thực tế xét nghiệm HbA1c: Khoảng trống quy trình vs. Bằng chứng tái nhập
1. **Thực tế quan sát được:** 83.05% hồ sơ đợt điều trị nội trú không ghi nhận kết quả xét nghiệm HbA1c. Đây là một hiện tượng quan sát được rõ ràng trên dữ liệu, phản ánh rằng quy trình lâm sàng thường chỉ tập trung kiểm soát đường huyết mao mạch cấp tính.
2. **Liên hệ thống kê với tái nhập viện:** Trong mô hình đa biến, biến `no_a1c_test` đạt $p = 0.1076$ (chưa đạt ngưỡng ý nghĩa $p < 0.05$). Do đó, **chưa đủ bằng chứng thống kê** để khẳng định việc thiếu xét nghiệm HbA1c trực tiếp gây tái nhập viện. Tuy nhiên, việc chuẩn hóa đo HbA1c vẫn là khuyến cáo thực hành lâm sàng tiêu chuẩn để hỗ trợ theo dõi ngoại trú dài hạn.

### 4.2. Biến động liều Insulin
- Mặc dù bệnh nhân giảm liều insulin có tỷ lệ tái nhập đơn biến cao nhất (14.22%), nhưng trong mô hình đa biến, biến này đạt $p = 0.0677$. Điều này cho thấy sự dao động liều insulin phần lớn là hệ quả đi kèm của bệnh nặng (ví dụ suy thận, số ngày nằm viện dài) hơn là một yếu tố nguy cơ hoàn toàn độc lập.

---

## 5. Định Hướng Can Thiệp Vận Hành
Dựa trên các yếu tố đã xác nhận:
1. **Phân tầng dựa trên tiền sử & độ phức tạp:** Tiêu chí kích hoạt can thiệp cần ưu tiên cao nhất cho bệnh nhân có tiền sử nhập viện $\ge 1$ lần trong 12 tháng qua và có đa bệnh lý ($\ge 9$ chẩn đoán hoặc $\ge 70$ tuổi).
2. **Quy trình chuyển tiếp tập trung:** Đội ngũ điều dưỡng và dược sĩ lâm sàng cần tập trung nguồn lực rà soát đơn thuốc và hướng dẫn người nhà cho nhóm bệnh nhân có các đặc điểm trên thay vì dàn trải nguồn lực.
