import os
import csv
from edge.schemas import Result

LOG_FIELDS = [
    "received_at",
    "sensor_timestamp",
    "station",
    "city",
    "pH",
    "DO",
    "turbidity",
    "EC",
    "temperature",
    "prediction",
    "anomaly_score",
    "inference_latency_ms",
    "end_to_end_latency_ms",
    "model_size_kb",
    "system_cpu_pct",
    "system_ram_pct",
    "process_ram_mb",
    "throughput_msg_per_sec",
]


class CsvLogWriter:
    def __init__(self, log_path: str):
        self.log_path = log_path
        os.makedirs(os.path.dirname(os.path.abspath(log_path)), exist_ok=True)
        self._init_file()

    def _init_file(self):
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
                writer.writeheader()

    def append(self, res: Result):
        row = {
            "received_at": res.received_at,
            "sensor_timestamp": res.ts,
            "station": res.station,
            "city": res.city,
            "pH": res.values.get("pH", 0.0),
            "DO": res.values.get("DO", 0.0),
            "turbidity": res.values.get("turbidity", 0.0),
            "EC": res.values.get("EC", 0.0),
            "temperature": res.values.get("temperature", 0.0),
            "prediction": res.prediction,
            "anomaly_score": res.anomaly_score,
            "inference_latency_ms": res.latency.inference_ms,
            "end_to_end_latency_ms": res.latency.e2e_ms,
            "model_size_kb": res.detector.model_size_kb,
            "system_cpu_pct": res.system.system_cpu_pct,
            "system_ram_pct": res.system.system_ram_pct,
            "process_ram_mb": res.system.process_ram_mb,
            "throughput_msg_per_sec": res.system.throughput_msg_per_sec,
        }
        with open(self.log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
            writer.writerow(row)
