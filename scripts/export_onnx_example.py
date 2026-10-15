import os
import yaml

metadata = {
    "model_name": "WaterQualityAutoencoder",
    "version": "1.0.0",
    "format": "onnx",
    "input_name": "sensor_window",
    "input_shape": [1, 30, 5],
    "feature_order": ["pH", "DO", "turbidity", "EC", "temperature"],
    "dtype": "float32",
    "output_name": "reconstructed_window",
    "output_type": "reconstruction",
    "threshold": 0.35,
    "description": "Mẫu siêu dữ liệu hợp đồng I/O cho mô hình Autoencoder ONNX"
}

target_yaml = os.path.join(os.path.dirname(__file__), "..", "data", "models", "model.yaml")
os.makedirs(os.path.dirname(target_yaml), exist_ok=True)
with open(target_yaml, "w", encoding="utf-8") as f:
    yaml.safe_dump(metadata, f, sort_keys=False)

print(f"Đã tạo tệp mẫu metadata hợp đồng mô hình ONNX tại: {target_yaml}")
