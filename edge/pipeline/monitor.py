import os
import time
from collections import deque
import psutil
from edge.schemas import SystemUsageMetrics


class SystemMonitor:
    def __init__(self, window_sec: float = 60.0):
        self.process = psutil.Process(os.getpid())
        self.window_sec = window_sec
        self._msg_timestamps = deque()

        # Mồi trước 1 mẫu CPU để tránh 0.0 ở lần gọi đầu
        psutil.cpu_percent(interval=None)
        self.process.cpu_percent(interval=None)

    def record_message(self):
        now = time.time()
        self._msg_timestamps.append(now)
        cutoff = now - self.window_sec
        while self._msg_timestamps and self._msg_timestamps[0] < cutoff:
            self._msg_timestamps.popleft()

    def get_throughput(self) -> float:
        if len(self._msg_timestamps) < 2:
            return 0.17 if len(self._msg_timestamps) == 1 else 0.0
        span = self._msg_timestamps[-1] - self._msg_timestamps[0]
        if span <= 0:
            return float(len(self._msg_timestamps))
        return round((len(self._msg_timestamps) - 1) / span, 2)

    def get_soc_temperature(self) -> float:
        # Hỗ trợ đọc nhiệt độ chip Raspberry Pi / Linux SoC
        temp_paths = [
            "/sys/class/thermal/thermal_zone0/temp",
            "/sys/devices/virtual/thermal/thermal_zone0/temp",
        ]
        for path in temp_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        millidegrees = int(f.read().strip())
                        return round(millidegrees / 1000.0, 1)
                except Exception:
                    pass
        return None

    def get_metrics(self) -> SystemUsageMetrics:
        system_cpu = psutil.cpu_percent(interval=None)
        try:
            proc_cpu = self.process.cpu_percent(interval=None)
        except Exception:
            proc_cpu = 0.0

        ram_info = psutil.virtual_memory()
        proc_ram_mb = self.process.memory_info().rss / (1024 * 1024)

        return SystemUsageMetrics(
            system_cpu_pct=round(system_cpu, 1),
            process_cpu_pct=round(proc_cpu, 1),
            system_ram_pct=round(ram_info.percent, 1),
            process_ram_mb=round(proc_ram_mb, 2),
            throughput_msg_per_sec=self.get_throughput(),
            soc_temp_c=self.get_soc_temperature(),
        )
