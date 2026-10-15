import os
import sys
import time
import json
from datetime import datetime
import yaml

# Đảm bảo import được module local
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from devices.rpi_agent.sensors.mock import MockSensor


class RpiAgent:
    def __init__(self, config_path: str = "agent.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.sensor = MockSensor()
        self.seq = 0
        self._load_seq()

    def _load_config(self) -> dict:
        default_config = {
            "device_id": "rpi_station_01",
            "interval_sec": 6.0,
            "transport": "mqtt",  # mqtt | http | serial
            "mqtt": {
                "broker": "127.0.0.1",
                "port": 1883,
                "topic": "devices/rpi_station_01/telemetry",
            },
            "http": {
                "endpoint": "http://127.0.0.1:8000/api/v1/ingest",
            },
            "serial": {
                "port": "/dev/ttyUSB0",
                "baudrate": 9600,
            },
            "meta": {
                "station": "RaspberryPi_Lab",
                "city": "HoChiMinh",
                "province": "HCM",
            }
        }
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f) or {}
                default_config.update(loaded)
        return default_config

    def _load_seq(self):
        seq_file = "seq.txt"
        if os.path.exists(seq_file):
            try:
                with open(seq_file, "r") as f:
                    self.seq = int(f.read().strip())
            except Exception:
                self.seq = 0

    def _save_seq(self):
        try:
            with open("seq.txt", "w") as f:
                f.write(str(self.seq))
        except Exception:
            pass

    def run(self):
        transport = self.config.get("transport", "mqtt")
        interval = self.config.get("interval_sec", 6.0)
        device_id = self.config.get("device_id", "rpi_station_01")
        print(f"=== KHỞI ĐỘNG RPI AGENT: {device_id} ({transport.upper()}) ===")

        # Khởi tạo client theo giao thức
        mqtt_client = None
        if transport == "mqtt":
            import paho.mqtt.client as mqtt
            mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            cfg = self.config.get("mqtt", {})
            mqtt_client.connect(cfg.get("broker", "127.0.0.1"), cfg.get("port", 1883), 60)
            mqtt_client.loop_start()

        ser = None
        if transport == "serial":
            import serial
            cfg = self.config.get("serial", {})
            ser = serial.Serial(cfg.get("port", "/dev/ttyUSB0"), cfg.get("baudrate", 9600))

        try:
            while True:
                self.seq += 1
                self._save_seq()
                now_iso = datetime.now().isoformat()
                metrics = self.sensor.read_metrics()

                payload = {
                    "device_id": device_id,
                    "seq": self.seq,
                    "ts": now_iso,
                    "values": metrics,
                    "meta": self.config.get("meta", {}),
                }

                if transport == "mqtt" and mqtt_client:
                    topic = self.config.get("mqtt", {}).get("topic", f"devices/{device_id}/telemetry")
                    mqtt_client.publish(topic, json.dumps(payload), qos=1)
                elif transport == "http":
                    import requests
                    endpoint = self.config.get("http", {}).get("endpoint", "http://127.0.0.1:8000/api/v1/ingest")
                    try:
                        requests.post(endpoint, json=payload, timeout=3.0)
                    except Exception as e:
                        print(f"[RpiAgent] Lỗi gửi HTTP: {e}")
                elif transport == "serial" and ser:
                    ser.write((json.dumps(payload) + "\n").encode("utf-8"))

                print(f"[RpiAgent #{self.seq}] Đã gửi {payload['values']} qua {transport} -> chờ {interval}s")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[RpiAgent] Đang dừng Agent...")
        finally:
            if mqtt_client:
                mqtt_client.loop_stop()
                mqtt_client.disconnect()
            if ser:
                ser.close()


if __name__ == "__main__":
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else "agent.yaml"
    agent = RpiAgent(cfg_file)
    agent.run()
