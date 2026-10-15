import os
import yaml
from typing import List, Dict, Optional
import numpy as np
from edge.detectors.base import BaseDetector
from edge.schemas import Prediction, DetectorSummary


class OnnxDetector(BaseDetector):
    def __init__(self, model_file: str, metadata_file: str, threshold: float = 0.35):
        self.model_file = model_file
        self.metadata_file = metadata_file
        self.threshold = threshold
        self.session = None
        self.metadata = {}
        self._load_metadata()

    def _load_metadata(self):
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                self.metadata = yaml.safe_load(f) or {}

    @property
    def info(self) -> DetectorSummary:
        size_kb = 0.0
        if os.path.exists(self.model_file):
            size_kb = round(os.path.getsize(self.model_file) / 1024, 2)
        return DetectorSummary(
            name=self.metadata.get("model_name", "ONNX-WaterAnomaly"),
            type="onnx",
            version=self.metadata.get("version", "1.0.0"),
            model_size_kb=size_kb,
        )

    def warmup(self) -> None:
        try:
            import onnxruntime as ort
            if os.path.exists(self.model_file):
                opts = ort.SessionOptions()
                opts.intra_op_num_threads = 2
                self.session = ort.InferenceSession(self.model_file, opts, providers=["CPUExecutionProvider"])
                # Smoke test
                in_shape = self.metadata.get("input_shape", [1, 30, 5])
                dummy = np.zeros(in_shape, dtype=np.float32)
                in_name = self.session.get_inputs()[0].name
                self.session.run(None, {in_name: dummy})
        except Exception as e:
            print(f"[ONNX Detector] Không thể khởi tạo session: {e}")
            self.session = None

    def predict(self, window_data: np.ndarray, feature_names: List[str]) -> Prediction:
        if self.session is None:
            # Fallback if model not yet loaded
            return Prediction(score=0.20, label="NORMAL", contributions={f: 0.2 for f in feature_names})

        in_name = self.session.get_inputs()[0].name
        # Format input tensor [1, window_size, features]
        inp = np.expand_dims(window_data.astype(np.float32), axis=0)
        outputs = self.session.run(None, {in_name: inp})
        raw_out = outputs[0]

        out_type = self.metadata.get("output_type", "score")
        if out_type == "reconstruction":
            # Autoencoder: MSE loss
            mse = float(np.mean(np.square(raw_out - inp)))
            anomaly_score = min(round(mse * 2.5, 4), 1.0)
        else:
            anomaly_score = float(np.squeeze(raw_out))

        is_anomaly = anomaly_score > self.threshold
        return Prediction(
            score=round(anomaly_score, 4),
            label="ANOMALY" if is_anomaly else "NORMAL",
            contributions={f: 1.0 / len(feature_names) for f in feature_names},
        )
