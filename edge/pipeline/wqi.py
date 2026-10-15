from typing import Dict, Optional, Tuple

# Danh sách 5 thông số bắt buộc để tính chỉ số chất lượng nước tham khảo
REQUIRED_WQI_FEATURES = ["pH", "DO", "turbidity", "EC", "temperature"]


def calculate_wqi(values: Dict[str, float]) -> Tuple[Optional[float], str]:
    """
    Tính chỉ số chất lượng nước tổng hợp tham khảo do nhóm đề xuất (thang điểm 0 - 100)
    theo phương pháp hàm phụ có trọng số (Weighted Sub-index) lấy cảm hứng từ cấu trúc
    NSF-WQI (Brown et al., 1970) thích ứng cho 5 thông số quan trắc:
    - Oxy hòa tan (DO): Trọng số w = 0.30
    - Độ pH: Trọng số w = 0.25
    - Độ đục (Turbidity): Trọng số w = 0.20
    - Độ dẫn điện (EC): Trọng số w = 0.15
    - Nhiệt độ nước (Temperature): Trọng số w = 0.10

    Lưu ý học thuật: Đây là chỉ số tham khảo do nhóm đề xuất phục vụ kiểm thử mô phỏng,
    không phải chỉ số NSF-WQI 9 thông số chuẩn mực chính thức. Nếu thiếu bất kỳ thông số
    nào trong 5 thông số trên, hàm trả về (None, "Incomplete") để bảo đảm tính toàn vẹn.

    Trả về: (wqi_score, pollution_level)
    """
    if not values:
        return None, "Incomplete"

    for feat in REQUIRED_WQI_FEATURES:
        if feat not in values or values[feat] is None:
            return None, "Incomplete"

    # 1. Sub-index pH (Tối ưu 6.5 - 8.5)
    ph = float(values["pH"])
    if 6.5 <= ph <= 8.5:
        q_ph = 100.0 - abs(ph - 7.0) * 12.0
    elif ph < 6.5:
        q_ph = max(0.0, 94.0 - (6.5 - ph) * 26.0)
    else:  # ph > 8.5
        q_ph = max(0.0, 82.0 - (ph - 8.5) * 26.0)

    # 2. Sub-index DO (mg/L, càng cao càng tốt)
    do = float(values["DO"])
    if do >= 7.5:
        q_do = min(100.0, 90.0 + (do - 7.5) * 2.5)
    elif do >= 5.0:
        q_do = 70.0 + (do - 5.0) * 8.0
    elif do >= 2.0:
        q_do = 30.0 + (do - 2.0) * 13.33
    else:
        q_do = max(0.0, do * 15.0)

    # 3. Sub-index Turbidity (NTU, càng thấp càng tốt)
    turb = float(values["turbidity"])
    if turb <= 5.0:
        q_turb = 100.0 - turb * 2.0
    elif turb <= 20.0:
        q_turb = 90.0 - (turb - 5.0) * 2.0
    elif turb <= 50.0:
        q_turb = 60.0 - (turb - 20.0) * 1.33
    else:
        q_turb = max(0.0, 20.0 - (turb - 50.0) * 0.4)

    # 4. Sub-index EC (µS/cm, tự nhiên sạch 150 - 500)
    ec = float(values["EC"])
    if ec <= 400.0:
        q_ec = 100.0 - max(0.0, 200.0 - ec) * 0.08
    elif ec <= 800.0:
        q_ec = 90.0 - (ec - 400.0) * 0.075
    elif ec <= 1500.0:
        q_ec = 60.0 - (ec - 800.0) * 0.05
    else:
        q_ec = max(0.0, 25.0 - (ec - 1500.0) * 0.02)

    # 5. Sub-index Temperature (°C, tối ưu 15 - 25°C)
    temp = float(values["temperature"])
    if 15.0 <= temp <= 25.0:
        q_temp = 100.0 - abs(temp - 20.0) * 1.5
    elif temp < 15.0:
        q_temp = max(0.0, 92.5 - (15.0 - temp) * 3.0)
    else:
        q_temp = max(0.0, 92.5 - (temp - 25.0) * 3.5)

    # Tính tổng có trọng số
    wqi = (
        0.30 * q_do
        + 0.25 * q_ph
        + 0.20 * q_turb
        + 0.15 * q_ec
        + 0.10 * q_temp
    )
    wqi = round(max(0.0, min(100.0, wqi)), 1)

    # Phân cấp chất lượng nước đồng bộ với Dashboard (80/60/40) và dataset Trung Quốc
    if wqi >= 80.0:
        level = "Excellent"
    elif wqi >= 60.0:
        level = "Good"
    elif wqi >= 40.0:
        level = "Moderate"
    elif wqi >= 20.0:
        level = "Poor"
    else:
        level = "Very Poor"

    return wqi, level
