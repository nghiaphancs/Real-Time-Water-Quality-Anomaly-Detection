import os
import yaml
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class FeatureMeta(BaseModel):
    key: str
    name: str
    name_vi: str
    unit: str
    min: float
    max: float
    safe_min: float
    safe_max: float
    color: str
    description: str


class CsvSourceConfig(BaseModel):
    file: str = "china_water_pollution_data.csv"
    mapping: str = "china_water"
    order: str = "sequential"
    loop: bool = True
    interval_sec: float = 6.0
    station: Optional[str] = None
    skip_invalid: bool = True


class DeviceSourceConfig(BaseModel):
    timeout_sec: float = 30.0
    telemetry_topic: str = "devices/+/telemetry"
    status_topic: str = "devices/+/status"


class SourceConfig(BaseModel):
    mode: str = "csv"
    csv: CsvSourceConfig = Field(default_factory=CsvSourceConfig)
    device: DeviceSourceConfig = Field(default_factory=DeviceSourceConfig)


class OnnxConfig(BaseModel):
    model_file: str = "data/models/anomaly.onnx"
    metadata_file: str = "data/models/model.yaml"
    intra_op_threads: int = 2


class DetectorConfig(BaseModel):
    type: str = "rule_based"
    threshold: float = 0.35
    window_size: int = 30
    warmup_samples: int = 5
    onnx: OnnxConfig = Field(default_factory=OnnxConfig)


class MqttTopics(BaseModel):
    raw_telemetry: str = "water_quality"
    result: str = "water_quality/result"
    control: str = "edge/control"


class MqttConfig(BaseModel):
    broker: str = "127.0.0.1"
    port: int = 1883
    ws_port: int = 9001
    keepalive: int = 60
    topics: MqttTopics = Field(default_factory=MqttTopics)


class ApiConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: List[str] = Field(default_factory=lambda: [
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:8000", "http://127.0.0.1:8000"
    ])


class StorageConfig(BaseModel):
    db_path: str = "data/runtime/waterqa.db"
    csv_log: str = "data/logs/benchmark_log.csv"
    schema_version: str = "2.0"
    retention_days: int = 30


class SecurityConfig(BaseModel):
    enabled: bool = False
    api_key: str = ""


class AppConfig(BaseModel):
    name: str = "Edge Water QA"
    version: str = "2.0.0"
    env: str = "local"


class Settings(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    source: SourceConfig = Field(default_factory=SourceConfig)
    detector: DetectorConfig = Field(default_factory=DetectorConfig)
    mqtt: MqttConfig = Field(default_factory=MqttConfig)
    api: ApiConfig = Field(default_factory=ApiConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    features: Dict[str, FeatureMeta] = Field(default_factory=dict)


def get_project_root() -> str:
    current = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(current, ".."))


def load_settings(config_path: Optional[str] = None) -> Settings:
    root = get_project_root()
    if config_path is None:
        config_path = os.path.join(root, "configs", "app.yaml")
    
    app_data: Dict[str, Any] = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            app_data = yaml.safe_load(f) or {}

    features_path = os.path.join(root, "configs", "features.yaml")
    features_data: Dict[str, Any] = {}
    if os.path.exists(features_path):
        with open(features_path, "r", encoding="utf-8") as f:
            features_raw = yaml.safe_load(f) or {}
            features_data = features_raw.get("features", {})

    app_data["features"] = features_data
    return Settings(**app_data)


def save_settings(settings: Settings, config_path: Optional[str] = None):
    root = get_project_root()
    if config_path is None:
        config_path = os.path.join(root, "configs", "app.yaml")
    
    data = settings.model_dump(exclude={"features"})
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
