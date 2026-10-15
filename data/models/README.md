# Thư mục Mô hình Trí tuệ Nhân tạo Biên (data/models/)

Thư mục này dùng để lưu trữ các mô hình học máy dạng ONNX (.onnx) phục vụ suy luận phát hiện bất thường thời gian thực.

## 1. Cấu trúc yêu cầu
Mỗi mô hình đặt vào đây nên đi kèm tệp mô tả giao tiếp `model.yaml` (hoặc tên tương ứng `<tên_model>.yaml`):

```yaml
model_name: "water_anomaly_autoencoder"
version: "1.0.0"
format: "onnx"
input_name: "input_sensor_window"
input_shape: [1, 30, 5]    # [batch, window_size, features]
feature_order: ["pH", "DO", "turbidity", "EC", "temperature"]
dtype: "float32"
output_name: "reconstruction"
output_type: "reconstruction"  # 'score' | 'reconstruction' | 'probability'
threshold: 0.35
```

## 2. Hoán đổi mô hình nóng (Hot-Swap)
- Khi có mô hình mới từ nhóm nghiên cứu, chỉ cần thả file `.onnx` và `.yaml` vào đây.
- Kích hoạt qua giao diện Web (tab Cấu hình) hoặc API `POST /api/v1/models/activate`.
- Hệ thống sẽ chạy kiểm thử hợp đồng (smoke test) trước khi chuyển đổi mà không làm gián đoạn luồng dữ liệu.
