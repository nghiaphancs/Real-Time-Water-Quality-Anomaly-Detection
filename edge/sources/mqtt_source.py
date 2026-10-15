import json
import queue
import time
from typing import Optional
from edge.sources.base import DataSource
from edge.schemas import Reading, SourceStatus


class MqttDeviceSource(DataSource):
    def __init__(self):
        self._queue: queue.Queue[Reading] = queue.Queue(maxsize=1000)
        self._running = False
        self._total_received = 0
        self._last_seen = None

    @property
    def name(self) -> str:
        return "mqtt_device"

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def on_mqtt_message(self, topic: str, payload_bytes: bytes):
        """Được gọi khi có gói tin từ topic devices/+/telemetry hoặc water_quality"""
        if not self._running:
            return

        try:
            data = json.loads(payload_bytes.decode("utf-8"))
            # Hỗ trợ cả 2 định dạng: Hợp đồng chuẩn Reading hoặc định dạng phẳng
            device_id = data.get("device_id") or data.get("station") or "rpi_device"
            seq = data.get("seq", self._total_received + 1)
            ts = data.get("ts") or data.get("timestamp") or time.strftime("%Y-%m-%dT%H:%M:%S")

            if "values" in data and isinstance(data["values"], dict):
                values = {k: float(v) for k, v in data["values"].items()}
                meta = data.get("meta", {})
            else:
                # Định dạng phẳng
                known_feats = ["pH", "DO", "turbidity", "EC", "temperature"]
                values = {k: float(data[k]) for k in known_feats if k in data}
                meta = {k: v for k, v in data.items() if k not in known_feats}

            reading = Reading(
                device_id=device_id,
                seq=seq,
                ts=ts,
                values=values,
                meta=meta,
            )

            if not self._queue.full():
                self._queue.put(reading)
                self._total_received += 1
                self._last_seen = ts
        except Exception as e:
            print(f"[MqttDeviceSource] Lỗi phân tích gói tin: {e}")

    def poll_reading(self) -> Optional[Reading]:
        if not self._running:
            return None
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def get_status(self) -> SourceStatus:
        return SourceStatus(
            mode="device",
            active_source="mqtt_device",
            is_streaming=self._running,
            interval_sec=0.0,
            total_received=self._total_read if hasattr(self, '_total_read') else self._total_received,
            last_seen=self._last_seen,
            device_online_count=1 if self._queue.qsize() > 0 or self._last_seen else 0,
        )
