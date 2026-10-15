import time
import json
import uuid
from datetime import datetime
from typing import Optional, List
from edge.settings import Settings
from edge.sources.manager import SourceManager
from edge.pipeline.normalizer import Normalizer
from edge.pipeline.window import SlidingWindowManager
from edge.pipeline.monitor import SystemMonitor
from edge.detectors.base import BaseDetector
from edge.detectors.rule_based import RuleBasedDetector
from edge.detectors.onnx_detector import OnnxDetector
from edge.storage.db import Database
from edge.storage.csv_log import CsvLogWriter
from edge.bus.mqtt_bus import MqttBus
from edge.schemas import Result, LatencyMetrics
from edge.pipeline.wqi import calculate_wqi


class InferenceEngine:
    def __init__(
        self,
        settings: Settings,
        source_manager: SourceManager,
        db: Database,
        csv_log: CsvLogWriter,
        mqtt_bus: MqttBus,
    ):
        self.settings = settings
        self.source_manager = source_manager
        self.db = db
        self.csv_log = csv_log
        self.mqtt_bus = mqtt_bus

        self.feature_order = list(settings.features.keys())
        self.normalizer = Normalizer(settings.features)
        self.window_mgr = SlidingWindowManager(
            window_size=settings.detector.window_size,
            warmup_samples=settings.detector.warmup_samples,
        )
        self.monitor = SystemMonitor()

        # Init detector
        self.detector: BaseDetector = self._create_detector(settings.detector.type)
        self.detector.warmup()

        self._running = False

    def _create_detector(self, detector_type: str) -> BaseDetector:
        if detector_type == "onnx":
            return OnnxDetector(
                model_file=self.settings.detector.onnx.model_file,
                metadata_file=self.settings.detector.onnx.metadata_file,
                threshold=self.settings.detector.threshold,
            )
        return RuleBasedDetector(
            threshold=self.settings.detector.threshold,
            features_meta=self.settings.features,
        )

    def reload_config(self, new_settings: Settings):
        self.settings = new_settings
        self.window_mgr.set_window_size(new_settings.detector.window_size)
        self.detector = self._create_detector(new_settings.detector.type)
        self.detector.warmup()
        self.source_manager.set_mode(new_settings.source.mode)
        print("[InferenceEngine] Đã tải lại cấu hình thành công.")

    def on_control_message(self, payload_bytes: bytes):
        """Xử lý tín hiệu điều khiển nóng từ API qua MQTT"""
        try:
            msg = json.loads(payload_bytes.decode("utf-8"))
            action = msg.get("action")
            if action == "reload_config":
                from edge.settings import load_settings
                self.reload_config(load_settings())
            elif action == "set_threshold":
                th = float(msg.get("threshold", 0.35))
                self.settings.detector.threshold = th
                if hasattr(self.detector, "threshold"):
                    self.detector.threshold = th
                print(f"[InferenceEngine] Đã cập nhật ngưỡng Anomaly sang {th}")
        except Exception as e:
            print(f"[InferenceEngine] Lỗi xử lý control message: {e}")

    def run_step(self) -> Optional[Result]:
        total_start = time.perf_counter()
        reading = self.source_manager.poll_reading()
        if not reading:
            return None

        self.monitor.record_message()
        preprocess_start = time.perf_counter()

        # 1. Trích xuất & chuẩn hóa dữ liệu
        is_valid, sample, err = self.normalizer.validate_and_extract(reading, self.feature_order)
        if not is_valid:
            print(f"[InferenceEngine] Bỏ qua mẫu không hợp lệ: {err}")
            return None

        # 2. Đưa vào cửa sổ trượt theo trạm/thiết bị
        window_np = self.window_mgr.append_sample(reading.device_id, sample)
        window_status = self.window_mgr.get_status(reading.device_id)
        preprocess_ms = (time.perf_counter() - preprocess_start) * 1000

        # 3. Thực thi suy luận
        inf_start = time.perf_counter()
        prediction = self.detector.predict(window_np, self.feature_order)
        inf_ms = (time.perf_counter() - inf_start) * 1000

        # 4. Đo đạc tài nguyên & độ trễ
        e2e_ms = (time.perf_counter() - total_start) * 1000
        sys_usage = self.monitor.get_metrics()

        # Liệt kê các đặc trưng đóng góp lớn nhất vào bất thường
        sorted_contribs = sorted(prediction.contributions.items(), key=lambda x: x[1], reverse=True)
        top_contrib_features = [
            f"{k} ({(v*100):.0f}%)" for k, v in sorted_contribs if v > 0.20
        ]

        # 5. Đóng gói kết quả chuẩn Result
        meta = reading.meta or {}
        event_id = str(uuid.uuid4())[:8]
        calc_wqi, calc_level = calculate_wqi(reading.values)
        final_wqi = meta.get("wqi") if meta.get("wqi") is not None else calc_wqi
        final_level = meta.get("pollution_level") or calc_level

        result = Result(
            event_id=event_id,
            seq=reading.seq,
            source=self.source_manager._active_source_name.split()[0],
            device_id=reading.device_id,
            station=meta.get("station", reading.device_id),
            city=meta.get("city", "Ningbo"),
            province=meta.get("province", "Zhejiang"),
            ts=reading.ts,
            received_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            values=reading.values,
            wqi=final_wqi,
            pollution_level=final_level,
            remarks=meta.get("remarks", ""),
            prediction=prediction.label,
            anomaly_score=prediction.score,
            threshold=self.settings.detector.threshold,
            warming_up=window_status["warming_up"],
            contributing_features=top_contrib_features,
            detector=self.detector.info,
            latency=LatencyMetrics(
                inference_ms=round(inf_ms, 2),
                preprocess_ms=round(preprocess_ms, 2),
                e2e_ms=round(e2e_ms, 2),
            ),
            system=sys_usage,
            buffer_current=window_status["current_size"],
            buffer_max=window_status["max_size"],
        )

        # 6. Lưu trữ vào DB và CSV log
        self.db.insert_result(result)
        self.csv_log.append(result)

        # Cập nhật thông tin thiết bị
        self.db.update_device(
            device_id=reading.device_id,
            transport=result.source,
            seq=reading.seq,
            meta=meta,
        )

        # 7. Xuất bản qua MQTT bus
        result_dict = result.model_dump()
        result_dict["sensor_timestamp"] = result.ts  # Tương thích ngược với Frontend
        result_dict["inference_latency_ms"] = result.latency.inference_ms
        result_dict["end_to_end_latency_ms"] = result.latency.e2e_ms
        result_dict["model_size_kb"] = result.detector.model_size_kb
        result_dict["system_cpu_pct"] = result.system.system_cpu_pct
        result_dict["system_ram_pct"] = result.system.system_ram_pct
        result_dict["process_ram_mb"] = result.system.process_ram_mb
        result_dict["throughput_msg_per_sec"] = result.system.throughput_msg_per_sec
        for k, v in result.values.items():
            result_dict[k] = v

        self.mqtt_bus.publish_result(self.settings.mqtt.topics.result, result_dict)

        # In log ra terminal
        print(
            f"[{result.source.upper()} #{result.seq}] {result.station} ({result.ts}) -> "
            f"{result.prediction} (Score: {result.anomaly_score} / {result.threshold}) | "
            f"Inf: {result.latency.inference_ms}ms | E2E: {result.latency.e2e_ms}ms | "
            f"pH={result.values.get('pH')} DO={result.values.get('DO')} Turb={result.values.get('turbidity')}"
        )

        return result

    def loop_forever(self):
        self._running = True
        self.source_manager.start()
        print("[InferenceEngine] Đã khởi động vòng lặp suy luận biên.")
        try:
            while self._running:
                self.run_step()
                time.sleep(0.05)
        except KeyboardInterrupt:
            print("[InferenceEngine] Đang dừng vòng lặp...")
        finally:
            self.source_manager.stop()
            self.detector.close()
