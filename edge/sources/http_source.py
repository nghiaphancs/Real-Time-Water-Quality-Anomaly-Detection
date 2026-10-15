import queue
import time
from typing import Optional
from edge.sources.base import DataSource
from edge.schemas import Reading, SourceStatus


class HttpDeviceSource(DataSource):
    def __init__(self):
        self._queue: queue.Queue[Reading] = queue.Queue(maxsize=1000)
        self._running = False
        self._total_received = 0
        self._last_seen = None

    @property
    def name(self) -> str:
        return "http_device"

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def ingest(self, reading: Reading):
        """Được gọi từ route FastAPI POST /api/v1/ingest"""
        if not self._running:
            return
        if not self._queue.full():
            self._queue.put(reading)
            self._total_received += 1
            self._last_seen = reading.ts

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
            active_source="http_device",
            is_streaming=self._running,
            interval_sec=0.0,
            total_received=self._total_received,
            last_seen=self._last_seen,
            device_online_count=1 if self._queue.qsize() > 0 or self._last_seen else 0,
        )
