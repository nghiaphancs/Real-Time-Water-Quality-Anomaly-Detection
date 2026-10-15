import random
from typing import Dict
from devices.rpi_agent.sensors.base import SensorPlugin


class MockSensor(SensorPlugin):
    """Cảm biến giả lập chạy trên Raspberry Pi khi chưa gắn phần cứng thật"""
    def __init__(self):
        self.base_ph = 7.2
        self.base_do = 7.8
        self.base_turb = 1.2
        self.base_ec = 420.0
        self.base_temp = 23.5

    def read_metrics(self) -> Dict[str, float]:
        # Dao động ngẫu nhiên quanh mức chuẩn
        ph = round(self.base_ph + random.uniform(-0.15, 0.15), 2)
        do = round(self.base_do + random.uniform(-0.3, 0.3), 2)
        turb = round(max(0.2, self.base_turb + random.uniform(-0.2, 0.4)), 2)
        ec = round(self.base_ec + random.uniform(-10.0, 10.0), 1)
        temp = round(self.base_temp + random.uniform(-0.4, 0.4), 2)

        return {
            "pH": ph,
            "DO": do,
            "turbidity": turb,
            "EC": ec,
            "temperature": temp,
        }
