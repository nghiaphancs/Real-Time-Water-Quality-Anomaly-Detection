import os
import sys
import numpy as np
import csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from edge.settings import load_settings, get_project_root
from edge.detectors.rule_based import RuleBasedDetector


def calibrate():
    root = get_project_root()
    settings = load_settings()
    csv_file = os.path.join(root, "data", "datasets", "china_water_pollution_data.csv")

    if not os.path.exists(csv_file):
        print(f"Không tìm thấy file: {csv_file}")
        return

    features = list(settings.features.keys())
    detector = RuleBasedDetector(threshold=settings.detector.threshold, features_meta=settings.features)

    samples = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                sample = [
                    float(row["pH"]),
                    float(row["Dissolved_Oxygen_mg_L"]),
                    float(row["Turbidity_NTU"]),
                    float(row["Conductivity_uS_cm"]),
                    float(row["Water_Temperature_C"]),
                ]
                samples.append(sample)
            except Exception:
                continue

    data_np = np.array(samples)
    print(f"Tổng số mẫu nạp: {len(data_np)}")

    scores = []
    anomalies = 0
    for i in range(len(data_np)):
        window = data_np[max(0, i-29):i+1]
        pred = detector.predict(window, features)
        scores.append(pred.score)
        if pred.label == "ANOMALY":
            anomalies += 1

    scores = np.array(scores)
    print("=== KẾT QUẢ ĐÁNH GIÁ MÔ HÌNH RULE-BASED ===")
    print(f"Điểm Min: {scores.min():.4f}")
    print(f"Điểm Max: {scores.max():.4f}")
    print(f"Điểm Trung bình: {scores.mean():.4f}")
    print(f"Phân vị 50% (Median): {np.percentile(scores, 50):.4f}")
    print(f"Phân vị 90%: {np.percentile(scores, 90):.4f}")
    print(f"Phân vị 95%: {np.percentile(scores, 95):.4f}")
    print(f"Ngưỡng hiện tại (Threshold): {detector.threshold}")
    print(f"Số mẫu ANOMALY phát hiện: {anomalies} / {len(scores)} ({anomalies/len(scores)*100:.2f}%)")


if __name__ == "__main__":
    calibrate()
