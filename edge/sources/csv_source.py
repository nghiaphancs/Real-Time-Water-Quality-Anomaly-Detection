import os
import csv
import time
import random
import yaml
from typing import Optional, List, Dict, Any
from edge.sources.base import DataSource
from edge.schemas import Reading, SourceStatus


class CsvSource(DataSource):
    def __init__(
        self,
        dataset_dir: str,
        mapping_dir: str,
        csv_file: str = "china_water_pollution_data.csv",
        mapping_name: str = "china_water",
        order: str = "sequential",
        loop: bool = True,
        interval_sec: float = 6.0,
        station_filter: Optional[str] = None,
        skip_invalid: bool = True,
    ):
        self.dataset_dir = dataset_dir
        self.mapping_dir = mapping_dir
        self.csv_file = csv_file
        self.mapping_name = mapping_name
        self.order = order
        self.loop = loop
        self.interval_sec = interval_sec
        self.station_filter = station_filter
        self.skip_invalid = skip_invalid

        self._running = False
        self._rows: List[Dict[str, str]] = []
        self._current_index = 0
        self._mapping: Dict[str, Any] = {}
        self._seq = 0
        self._last_poll_time = 0.0
        self._total_read = 0

        self._load_mapping()
        self._load_csv()

    @property
    def name(self) -> str:
        return "csv"

    def _load_mapping(self):
        map_path = os.path.join(self.mapping_dir, f"{self.mapping_name}.yaml")
        if os.path.exists(map_path):
            with open(map_path, "r", encoding="utf-8") as f:
                self._mapping = yaml.safe_load(f) or {}

    def _load_csv(self):
        csv_path = os.path.join(self.dataset_dir, self.csv_file)
        if not os.path.exists(csv_path):
            print(f"[CsvSource] Cảnh báo: Không tìm thấy tệp {csv_path}")
            return

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if self.station_filter:
            st_col = self._mapping.get("meta", {}).get("station", "Monitoring_Station")
            rows = [r for r in rows if r.get(st_col) == self.station_filter]

        if self.order == "random":
            random.seed(42)
            random.shuffle(rows)
        elif self.order == "by_date":
            ts_col = self._mapping.get("meta", {}).get("timestamp", "Date")
            rows.sort(key=lambda x: x.get(ts_col, ""))

        self._rows = rows
        self._current_index = 0
        print(f"[CsvSource] Đã nạp {len(self._rows)} mẫu từ {self.csv_file} (Thứ tự: {self.order})")

    def reload(self, csv_file: Optional[str] = None, order: Optional[str] = None, interval_sec: Optional[float] = None):
        if csv_file:
            self.csv_file = csv_file
        if order:
            self.order = order
        if interval_sec:
            self.interval_sec = interval_sec
        self._load_csv()

    def start(self) -> None:
        self._running = True
        self._last_poll_time = 0.0

    def stop(self) -> None:
        self._running = False

    def get_status(self) -> SourceStatus:
        return SourceStatus(
            mode="csv",
            active_source="csv",
            is_streaming=self._running,
            interval_sec=self.interval_sec,
            total_received=self._total_read,
            current_dataset=self.csv_file,
            device_online_count=0,
        )

    def poll_reading(self) -> Optional[Reading]:
        if not self._running or not self._rows:
            return None

        now = time.perf_counter()
        if now - self._last_poll_time < self.interval_sec:
            return None

        self._last_poll_time = now

        if self._current_index >= len(self._rows):
            if self.loop:
                self._current_index = 0
            else:
                return None

        row = self._rows[self._current_index]
        self._current_index += 1

        try:
            fields_map = self._mapping.get("fields", {
                "pH": "pH",
                "DO": "Dissolved_Oxygen_mg_L",
                "turbidity": "Turbidity_NTU",
                "EC": "Conductivity_uS_cm",
                "temperature": "Water_Temperature_C",
            })
            meta_map = self._mapping.get("meta", {
                "timestamp": "Date",
                "station": "Monitoring_Station",
                "city": "City",
                "province": "Province",
                "wqi": "Water_Quality_Index",
                "pollution_level": "Pollution_Level",
                "remarks": "Remarks",
            })

            values = {}
            for std_feat, col_name in fields_map.items():
                val_str = row.get(col_name)
                if val_str is None or val_str.strip() == "":
                    if self.skip_invalid:
                        return None
                    val = 0.0
                else:
                    val = float(val_str)
                values[std_feat] = val

            meta = {}
            for std_meta, col_name in meta_map.items():
                val = row.get(col_name)
                if val is not None:
                    if std_meta == "wqi":
                        try:
                            meta[std_meta] = float(val)
                        except ValueError:
                            meta[std_meta] = 75.0
                    else:
                        meta[std_meta] = val

            self._seq += 1
            self._total_read += 1
            station_name = meta.get("station", "Station_1")
            ts = meta.get("timestamp", time.strftime("%Y-%m-%d"))

            return Reading(
                device_id=station_name,
                seq=self._seq,
                ts=ts,
                values=values,
                meta=meta,
            )
        except Exception as e:
            if not self.skip_invalid:
                print(f"[CsvSource] Lỗi dòng {self._current_index}: {e}")
            return None
