from typing import List, Dict, Any
import numpy as np
from edge.detectors.base import BaseDetector
from edge.schemas import Prediction, DetectorSummary
from edge.settings import FeatureMeta


class RuleBasedDetector(BaseDetector):
    def __init__(self, threshold: float = 0.35, features_meta: Dict[str, FeatureMeta] = None):
        self.threshold = threshold
        self.features_meta = features_meta or {}
        self._param_bytes = 120

    @property
    def info(self) -> DetectorSummary:
        return DetectorSummary(
            name="RuleBased-CentroidDeviation",
            type="rule_based",
            version="2.0.0",
            model_size_kb=round(self._param_bytes / 1024, 4),
        )

    def warmup(self) -> None:
        pass

    def predict(self, window_data: np.ndarray, feature_names: List[str]) -> Prediction:
        """
        window_data: shape (N, D) where N is buffer size, D is number of features
        feature_names: order of features corresponding to columns
        """
        if window_data.size == 0:
            return Prediction(score=0.0, label="NORMAL", contributions={})

        mins = []
        maxs = []
        safe_mins = []
        safe_maxs = []

        for f in feature_names:
            meta = self.features_meta.get(f)
            if meta:
                mins.append(meta.min)
                maxs.append(meta.max)
                safe_mins.append(meta.safe_min)
                safe_maxs.append(meta.safe_max)
            else:
                mins.append(0.0)
                maxs.append(100.0)
                safe_mins.append(10.0)
                safe_maxs.append(90.0)

        mins = np.array(mins)
        maxs = np.array(maxs)
        safe_mins = np.array(safe_mins)
        safe_maxs = np.array(safe_maxs)

        # Min-Max normalization
        denom = np.where((maxs - mins) == 0, 1e-6, maxs - mins)
        norm_window = np.clip((window_data - mins) / denom, 0.0, 1.0)

        # Expected centroid of clean water normalized (around center: pH ~7.0, DO good, low turbidity)
        # reference_center: [pH: ~0.49, DO: ~0.55, Turbidity: ~0.05, EC: ~0.40, Temp: ~0.45]
        ref_center = np.array([0.49, 0.55, 0.05, 0.40, 0.45][:len(feature_names)])

        # Calculate deviation per feature
        deviations = np.abs(norm_window - ref_center)
        mean_dev_per_feature = np.mean(deviations, axis=0) # shape (D,)

        # Also check hard safe-range breaches on latest sample
        latest_sample = window_data[-1]
        breach_penalties = np.zeros(len(feature_names))
        for i, val in enumerate(latest_sample):
            if val < safe_mins[i]:
                breach_penalties[i] += (safe_mins[i] - val) / (denom[i] + 1e-6)
            elif val > safe_maxs[i]:
                breach_penalties[i] += (val - safe_maxs[i]) / (denom[i] + 1e-6)

        total_feat_scores = mean_dev_per_feature + breach_penalties * 0.8
        raw_score = float(np.mean(total_feat_scores))
        anomaly_score = min(round(raw_score * 1.8, 4), 1.0)

        # Contributions breakdown (which feature drove the score)
        sum_dev = float(np.sum(total_feat_scores)) + 1e-6
        contributions = {
            f: round(float(total_feat_scores[i] / sum_dev), 3)
            for i, f in enumerate(feature_names)
        }

        is_anomaly = anomaly_score > self.threshold
        return Prediction(
            score=anomaly_score,
            label="ANOMALY" if is_anomaly else "NORMAL",
            contributions=contributions,
        )
