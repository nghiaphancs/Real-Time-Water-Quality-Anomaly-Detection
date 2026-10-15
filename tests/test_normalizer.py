import pytest
from edge.settings import load_settings
from edge.pipeline.normalizer import Normalizer
from edge.schemas import Reading


def test_normalizer_valid():
    settings = load_settings()
    normalizer = Normalizer(settings.features)
    features = list(settings.features.keys())

    reading = Reading(
        device_id="test_sensor",
        values={"pH": 7.2, "DO": 8.0, "turbidity": 1.5, "EC": 400.0, "temperature": 22.0}
    )

    is_valid, sample, err = normalizer.validate_and_extract(reading, features)
    assert is_valid is True
    assert len(sample) == 5
    assert err == ""


def test_normalizer_missing_feature():
    settings = load_settings()
    normalizer = Normalizer(settings.features)
    features = list(settings.features.keys())

    reading = Reading(
        device_id="test_sensor",
        values={"pH": 7.2, "DO": 8.0}
    )

    is_valid, sample, err = normalizer.validate_and_extract(reading, features)
    assert is_valid is False
    assert "Thiếu đặc trưng" in err


def test_normalizer_nan():
    settings = load_settings()
    normalizer = Normalizer(settings.features)
    features = list(settings.features.keys())

    reading = Reading(
        device_id="test_sensor",
        values={"pH": float("nan"), "DO": 8.0, "turbidity": 1.5, "EC": 400.0, "temperature": 22.0}
    )

    is_valid, sample, err = normalizer.validate_and_extract(reading, features)
    assert is_valid is False
    assert "NaN/Inf" in err
