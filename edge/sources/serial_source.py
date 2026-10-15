import json
import time
import queue
import threading
from typing import Optional
from edge.sources.base import DataSource
from edge.schemas import Reading, SourceStatus


class SerialDeviceSource(DataSource):
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self._queue: queue.Queue[Reading] = queue.Queue(maxsize=1000)
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._total_received = 0
        self._last_seen = None

    @property
    def name(self) -> str:
        return "serial_device"

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _read_loop(self):
        try:
            import serial
        except ImportError:
            print("[SerialSource] pyserial chưa được cài đặt, bỏ qua lắng nghe cổng Serial")
            return

        while self._running:
            try:
                with serial.Serial(self.port, self.baudrate, timeout=2.0) as ser:
                    print(f"[SerialSource] Đã kết nối cổng {self.port} @ {self.baudrate}")
                    while self._running:
                        line = ser.readline().decode("utf-8", errors="ignore").strip()
                        if line:
                            self._parse_line(line)
            except Exception:
                # Chờ cắm thiết bị vào cổng serial
                time.sleep(5.0)

    def _parse_line(self, line: str):
        try:
            if line.startswith("{"):
                data = json.loads(line)
                reading = Reading(**data)
            else:
                # Hỗ trợ định dạng CSV: pH,DO,turbidity,EC,temperature
                parts = [float(p.strip()) for p in line.split(",") if p.strip()]
                if len(parts) >= 5:
                    reading = Reading(
                        device_id="serial_sensor",
                        seq=self._total_received + 1,
                        values={
                            "pH": parts[0],
                            "DO": parts[1],
                            "turbidity": parts[2],
                            "EC": parts[3],
                            "temperature": parts[4],
                        }
                    )
                else:
                    return

            if not self._queue.full():
                self._queue.put(reading)
                self._total_received += 1
                self._last_seen = reading.ts
        except Exception as e:
            print(f"[SerialSource] Lỗi dòng dữ liệu: {e}")

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
            active_source="serial_device",
            is_streaming=self._running,
            interval_sec=0.0,
            total_received=self._total_received,
            last_seen=self._last_seen,
            device_online_count=1 if self._last_seen else 0,
        )
