import json
from typing import Callable, Optional
import paho.mqtt.client as mqtt
from edge.settings import MqttConfig


class MqttBus:
    def __init__(self, config: MqttConfig, on_telemetry_msg: Optional[Callable] = None, on_control_msg: Optional[Callable] = None):
        self.config = config
        self.on_telemetry_msg = on_telemetry_msg
        self.on_control_msg = on_control_msg

        # Dùng CallbackAPIVersion.VERSION2 cho paho-mqtt mới nhất
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.reconnect_delay_set(min_delay=1, max_delay=15)

        # Cấu hình LWT (Last Will and Testament)
        self.client.will_set("edge/status", payload=json.dumps({"status": "offline"}), qos=1, retain=True)

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self._connected = False

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self._connected = True
            print(f"[MQTT Bus] Kết nối thành công tới {self.config.broker}:{self.config.port}")
            # Đăng ký các topic cần thiết
            client.subscribe(self.config.topics.raw_telemetry)
            client.subscribe("devices/+/telemetry")
            client.subscribe(self.config.topics.control)
            # Báo trạng thái online
            client.publish("edge/status", payload=json.dumps({"status": "online"}), qos=1, retain=True)
        else:
            print(f"[MQTT Bus] Kết nối thất bại, mã lỗi: {reason_code}")

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload

        if topic == self.config.topics.control:
            if self.on_control_msg:
                self.on_control_msg(payload)
        else:
            if self.on_telemetry_msg:
                self.on_telemetry_msg(topic, payload)

    def connect(self):
        try:
            self.client.connect(self.config.broker, self.config.port, self.config.keepalive)
            self.client.loop_start()
        except Exception as e:
            print(f"[MQTT Bus] Cảnh báo không thể kết nối tới Broker: {e}")

    def publish_result(self, topic: str, payload_dict: dict):
        if self._connected:
            self.client.publish(topic, json.dumps(payload_dict, ensure_ascii=False), qos=0)

    def stop(self):
        self.client.publish("edge/status", payload=json.dumps({"status": "offline"}), qos=1, retain=True)
        self.client.loop_stop()
        self.client.disconnect()
