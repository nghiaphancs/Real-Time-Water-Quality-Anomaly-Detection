import os
import json
import pytest
from edge.settings import get_project_root
from edge.schemas import Reading
from edge.sources.csv_source import CsvSource
from edge.sources.mqtt_source import MqttDeviceSource
from edge.sources.http_source import HttpDeviceSource
from edge.sources.serial_source import SerialDeviceSource
from edge.sources.manager import SourceManager


def test_source_manager_csv_mode():
    root = get_project_root()
    dataset_dir = os.path.join(root, "data", "datasets")
    mapping_dir = os.path.join(root, "configs", "mappings")

    csv = CsvSource(
        dataset_dir=dataset_dir,
        mapping_dir=mapping_dir,
        csv_file="china_water_pollution_data.csv",
        order="sequential",
        interval_sec=0.0,
    )
    mqtt = MqttDeviceSource()
    http = HttpDeviceSource()
    serial = SerialDeviceSource()

    mgr = SourceManager(csv, mqtt, http, serial, mode="csv")
    mgr.start()

    r = mgr.poll_reading()
    assert r is not None
    assert r.seq == 1
    assert mgr.get_status().mode == "csv"


def test_source_manager_auto_fallback():
    root = get_project_root()
    dataset_dir = os.path.join(root, "data", "datasets")
    mapping_dir = os.path.join(root, "configs", "mappings")

    csv = CsvSource(
        dataset_dir=dataset_dir,
        mapping_dir=mapping_dir,
        csv_file="china_water_pollution_data.csv",
        order="sequential",
        interval_sec=0.0,
    )
    mqtt = MqttDeviceSource()
    http = HttpDeviceSource()
    serial = SerialDeviceSource()

    mgr = SourceManager(csv, mqtt, http, serial, mode="auto", device_timeout_sec=0.5)
    mgr.start()

    # When no device data, falls back to CSV
    r1 = mgr.poll_reading()
    assert r1 is not None

    # When device sends telemetry via HTTP, it prioritizes device
    dev_reading = Reading(
        device_id="rpi-test",
        seq=500,
        values={"pH": 7.0, "DO": 6.0, "turbidity": 2.0, "EC": 300.0, "temperature": 22.0},
    )
    http.ingest(dev_reading)

    r2 = mgr.poll_reading()
    assert r2 is not None
    assert r2.device_id == "rpi-test"
    assert r2.seq == 500


def test_mqtt_device_source_parsing():
    mqtt_src = MqttDeviceSource()
    mqtt_src.start()

    # Raw flat dict from IoT device
    payload = json.dumps({
        "station": "rpi_lake_01",
        "seq": 99,
        "pH": 7.3,
        "DO": 8.1,
        "turbidity": 1.5,
        "EC": 250.0,
        "temperature": 19.5,
    }).encode("utf-8")

    mqtt_src.on_mqtt_message("devices/rpi_lake_01/telemetry", payload)
    reading = mqtt_src.poll_reading()

    assert reading is not None
    assert reading.device_id == "rpi_lake_01"
    assert reading.seq == 99
    assert reading.values["pH"] == 7.3
