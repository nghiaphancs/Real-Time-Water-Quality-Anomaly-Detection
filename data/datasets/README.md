# Thư mục Dataset Quan trắc Nước (data/datasets/)

Thư mục này dùng để lưu trữ các tệp CSV chứa dữ liệu quan trắc phục vụ chế độ phát lại (Mock Stream).

## 1. Cách sử dụng
- Để chuyển đổi hoặc thêm bộ dữ liệu mới, bạn chỉ cần **thả tệp `.csv` vào thư mục này**.
- Hệ thống (FastAPI & Web UI) sẽ tự động quét thư mục và cho phép chọn file phát lại từ dropdown trong tab **Cấu hình**.

## 2. Các cột đặc trưng chuẩn (Features)
Hệ thống chuẩn hóa 5 thông số quan trắc:
- `pH`: Độ kiềm/axit (khoảng bình thường: 6.5 - 8.5)
- `DO` hoặc `Dissolved_Oxygen_mg_L`: Oxy hòa tan (mg/L)
- `turbidity` hoặc `Turbidity_NTU`: Độ đục (NTU)
- `EC` hoặc `Conductivity_uS_cm`: Độ dẫn điện (µS/cm)
- `temperature` hoặc `Water_Temperature_C`: Nhiệt độ nước (°C)

Các cột siêu dữ liệu bổ trợ (tùy chọn):
- `Date` hoặc `timestamp`: Thời gian đo
- `Monitoring_Station` hoặc `station`: Tên trạm quan trắc
- `City` / `Province`: Vị trí địa lý
- `Water_Quality_Index` / `Pollution_Level`: Chỉ số chất lượng & phân loại

## 3. Tùy biến ánh xạ cột (Column Mapping)
Nếu tệp CSV có tên cột khác, bạn có thể tạo tệp ánh xạ trong `configs/mappings/<tên_tệp>.yaml`.
Ví dụ: xem `configs/mappings/china_water.yaml`.
