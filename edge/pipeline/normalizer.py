from typing import Dict, List, Tuple
import math
from edge.schemas import Reading
from edge.settings import FeatureMeta


class Normalizer:
    def __init__(self, features_meta: Dict[str, FeatureMeta]):
        self.features_meta = features_meta

    def validate_and_extract(self, reading: Reading, feature_order: List[str]) -> Tuple[bool, List[float], str]:
        """
        Kiểm tra tính hợp lệ và trích xuất vector giá trị theo thứ tự đặc trưng.
        Trả về: (is_valid, sample_vector, error_message)
        """
        sample = []
        for feat in feature_order:
            if feat not in reading.values:
                return False, [], f"Thiếu đặc trưng bắt buộc: {feat}"
            val = reading.values[feat]
            if val is None or math.isnan(val) or math.isinf(val):
                return False, [], f"Giá trị không hợp lệ (NaN/Inf) tại: {feat}"
            sample.append(float(val))
        return True, sample, ""
