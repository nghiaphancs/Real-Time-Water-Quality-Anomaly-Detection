import pytest
from edge.pipeline.wqi import calculate_wqi


def test_wqi_clean_water():
    """Kiểm thử tính toán WQI cho mẫu nước sạch đạt chuẩn"""
    values = {
        "pH": 7.2,
        "DO": 8.5,
        "turbidity": 1.5,
        "EC": 300.0,
        "temperature": 20.0,
    }
    wqi, level = calculate_wqi(values)
    assert wqi is not None
    assert wqi >= 80.0
    assert level == "Excellent"


def test_wqi_polluted_water():
    """Kiểm thử tính toán WQI cho mẫu nước ô nhiễm nặng"""
    values = {
        "pH": 4.0,
        "DO": 1.0,
        "turbidity": 120.0,
        "EC": 2500.0,
        "temperature": 35.0,
    }
    wqi, level = calculate_wqi(values)
    assert wqi is not None
    assert wqi < 40.0
    assert level in ["Poor", "Very Poor"]


def test_wqi_missing_parameter():
    """Kiểm thử khi thiếu một trong các thông số bắt buộc"""
    # Thiếu trường turbidity
    values = {
        "pH": 7.2,
        "DO": 8.5,
        "EC": 300.0,
        "temperature": 20.0,
    }
    wqi, level = calculate_wqi(values)
    assert wqi is None
    assert level == "Incomplete"

    # Dict rỗng
    wqi_empty, level_empty = calculate_wqi({})
    assert wqi_empty is None
    assert level_empty == "Incomplete"


def test_wqi_none_value():
    """Kiểm thử khi giá trị một thông số bị None"""
    values = {
        "pH": 7.2,
        "DO": None,
        "turbidity": 1.5,
        "EC": 300.0,
        "temperature": 20.0,
    }
    wqi, level = calculate_wqi(values)
    assert wqi is None
    assert level == "Incomplete"
