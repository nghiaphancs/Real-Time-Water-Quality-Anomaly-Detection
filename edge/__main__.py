import os
import sys
import threading
import uvicorn
from edge.settings import load_settings, get_project_root
from edge.storage.db import Database
from edge.storage.csv_log import CsvLogWriter
from edge.bus.mqtt_bus import MqttBus
from edge.sources.csv_source import CsvSource
from edge.sources.mqtt_source import MqttDeviceSource
from edge.sources.http_source import HttpDeviceSource
from edge.sources.serial_source import SerialDeviceSource
from edge.sources.manager import SourceManager
from edge.pipeline.engine import InferenceEngine


def build_engine(settings=None):
    root = get_project_root()
    if settings is None:
        settings = load_settings()

    db = Database(os.path.join(root, settings.storage.db_path))
    csv_log = CsvLogWriter(os.path.join(root, settings.storage.csv_log))

    # Sources
    csv_source = CsvSource(
        dataset_dir=os.path.join(root, "data", "datasets"),
        mapping_dir=os.path.join(root, "configs", "mappings"),
        csv_file=settings.source.csv.file,
        mapping_name=settings.source.csv.mapping,
        order=settings.source.csv.order,
        loop=settings.source.csv.loop,
        interval_sec=settings.source.csv.interval_sec,
        station_filter=settings.source.csv.station,
        skip_invalid=settings.source.csv.skip_invalid,
    )
    mqtt_source = MqttDeviceSource()
    http_source = HttpDeviceSource()
    serial_source = SerialDeviceSource()

    source_manager = SourceManager(
        csv_source=csv_source,
        mqtt_source=mqtt_source,
        http_source=http_source,
        serial_source=serial_source,
        mode=settings.source.mode,
        device_timeout_sec=settings.source.device.timeout_sec,
    )

    engine_holder = []

    def on_telemetry(topic, payload):
        mqtt_source.on_mqtt_message(topic, payload)

    def on_control(payload):
        if engine_holder:
            engine_holder[0].on_control_message(payload)

    mqtt_bus = MqttBus(
        config=settings.mqtt,
        on_telemetry_msg=on_telemetry,
        on_control_msg=on_control,
    )
    mqtt_bus.connect()

    engine = InferenceEngine(
        settings=settings,
        source_manager=source_manager,
        db=db,
        csv_log=csv_log,
        mqtt_bus=mqtt_bus,
    )
    engine_holder.append(engine)
    return engine


def run_engine():
    engine = build_engine()
    engine.loop_forever()


def run_api():
    settings = load_settings()
    uvicorn.run(
        "edge.api.app:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=False,
    )


def run_all():
    """Chạy đồng thời cả Inference Engine và FastAPI Web Server"""
    settings = load_settings()
    print("=" * 60)
    print(f"🚀 KHỞI ĐỘNG HỆ THỐNG {settings.app.name} v{settings.app.version}")
    print(f"   • Chế độ nguồn dữ liệu: {settings.source.mode.upper()}")
    print(f"   • Chu kỳ làm tươi: {settings.source.csv.interval_sec} giây / mẫu")
    print(f"   • Ngưỡng phát hiện bất thường: {settings.detector.threshold}")
    print(f"   • API & Web Dashboard: http://{settings.api.host}:{settings.api.port}")
    print("=" * 60)

    engine = build_engine(settings)
    engine_thread = threading.Thread(target=engine.loop_forever, daemon=True)
    engine_thread.start()

    run_api()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "engine":
        run_engine()
    elif mode == "api":
        run_api()
    else:
        run_all()
