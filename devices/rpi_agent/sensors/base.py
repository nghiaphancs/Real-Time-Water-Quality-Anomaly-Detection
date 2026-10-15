from abc import ABC, abstractmethod
from typing import Dict


class SensorPlugin(ABC):
    @abstractmethod
    def read_metrics(self) -> Dict[str, float]:
        """
        Đọc các giá trị cảm biến hiện tại.
        Trả về dict: {"pH": 7.2, "DO": 8.1, "turbidity": 1.2, "EC": 420.0, "temperature": 22.5}
        """
        pass

    def close(self):
        pass
