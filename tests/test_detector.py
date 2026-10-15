import numpy as np
import pytest
from edge.settings import load_settings
from edge.detectors.rule_based import RuleBasedDetector


def test_rule_based_detector():
    settings = load_settings()
    detector = RuleBasedDetector(threshold=0.35, features_meta=settings.features)
    features = list(settings.features.keys())

    # Normal sample window
    normal_window = np.array([
        [7.2, 8.0, 1.0, 400.0, 20.0],
        [7.1, 8.2, 1.2, 410.0, 21.0],
    ])

    pred = detector.predict(normal_window, features)
    assert pred.label == "NORMAL"
    assert pred.score < 0.35
    assert len(pred.contributions) == 5

    # Anomaly sample window (huge turbidity & extreme pH breach)
    anomaly_window = np.array([
        [2.5, 1.0, 45.0, 950.0, 35.0],
        [2.0, 0.5, 48.0, 1000.0, 36.0],
    ])

    pred_anom = detector.predict(anomaly_window, features)
    assert pred_anom.label == "ANOMALY"
    assert pred_anom.score > 0.35
