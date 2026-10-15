import time
from typing import Optional, Literal
from edge.sources.base import DataSource
from edge.sources.csv_source import CsvSource
from edge.sources.mqtt_source import MqttDeviceSource
from edge.sources.http_source import HttpDeviceSource
from edge.sources.serial_source import SerialDeviceSource
from edge.schemas import Reading, SourceStatus


class SourceManager:
    def __init__(
        self,
        csv_source: CsvSource,
        mqtt_source: MqttDeviceSource,
        http_source: HttpDeviceSource,
        serial_source: SerialDeviceSource,
        mode: Literal["csv", "device", "auto"] = "csv",
        device_timeout_sec: float = 30.0,
    ):
        self.csv_source = csv_source
        self.mqtt_source = mqtt_source
        self.http_source = http_source
        self.serial_source = serial_source
        self.mode = mode
        self.device_timeout_sec = device_timeout_sec

        self._last_device_time = 0.0
        self._active_source_name = "csv"

    def start(self):
        self.csv_source.start()
        self.mqtt_source.start()
        self.http_source.start()
        self.serial_source.start()

    def stop(self):
        self.csv_source.stop()
        self.mqtt_source.stop()
        self.http_source.stop()
        self.serial_source.stop()

    def set_mode(self, mode: Literal["csv", "device", "auto"]):
        self.mode = mode
        print(f"[SourceManager] Đã đổi chế độ nguồn sang: {mode}")

    def poll_reading(self) -> Optional[Reading]:
        # 1. Kiểm tra xem có thiết bị nào (MQTT, HTTP, Serial) gửi dữ liệu không
        device_reading = (
            self.mqtt_source.poll_reading()
            or self.http_source.poll_reading()
            or self.serial_source.poll_reading()
        )

        if device_reading:
            self._last_device_time = time.perf_counter()

        now = time.perf_counter()
        has_recent_device = (now - self._last_device_time) < self.device_timeout_sec

        if self.mode == "device":
            self._active_source_name = "device"
            return device_reading

        elif self.mode == "auto":
            if device_reading:
                self._active_source_name = "device"
                return device_reading
            elif has_recent_device:
                # Vẫn đang trong khoảng timeout của thiết bị, chờ thiết bị gửi tiếp
                return None
            else:
                # Quá timeout, tự động phát lại CSV
                self._active_source_name = "csv (auto-fallback)"
                return self.csv_source.poll_reading()

        else: # mode == "csv"
            self._active_source_name = "csv"
            return self.csv_source.poll_reading()

    def get_status(self) -> SourceStatus:
        now = time.perf_counter()
        device_online = (now - self._last_device_time) < self.device_timeout_sec and self._last_device_time > 0
        total = (
            self.csv_source._total_read
            + self.mqtt_source._total_received
            + self.http_source._total_received
            + self.serial_source._total_received
        )

        return SourceStatus(
            mode=self.mode,
            active_source=self._active_source_name,
            is_streaming=True,
            interval_sec=self.csv_source.interval_sec,
            total_received=total,
            last_seen=time.strftime("%Y-%m-%dT%H:%M:%S") if self._last_device_time > 0 else None,
            device_online_count=1 if device_online else 0,
            current_dataset=self.csv_source.csv_file,
        )
