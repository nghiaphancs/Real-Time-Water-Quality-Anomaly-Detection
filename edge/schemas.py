from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class Reading(BaseModel):
    """Hợp đồng dữ liệu cảm biến đầu vào (từ CSV hoặc Thiết bị)"""
    device_id: str = "default_station"
    seq: int = 0
    ts: str = Field(default_factory=lambda: datetime.now().isoformat())
    values: Dict[str, float]
    meta: Dict[str, Any] = Field(default_factory=dict)


class LatencyMetrics(BaseModel):
    inference_ms: float = 0.0
    preprocess_ms: float = 0.0
    e2e_ms: float = 0.0


class SystemUsageMetrics(BaseModel):
    system_cpu_pct: float = 0.0
    process_cpu_pct: float = 0.0
    system_ram_pct: float = 0.0
    process_ram_mb: float = 0.0
    throughput_msg_per_sec: float = 0.0
    soc_temp_c: Optional[float] = None


class DetectorSummary(BaseModel):
    name: str = "rule_based"
    type: str = "rule_based"
    version: str = "1.0.0"
    model_size_kb: float = 0.12


class Result(BaseModel):
    """Kết quả phân tích & suy luận chuẩn hóa phát hành cho Dashboard & Lưu trữ"""
    event_id: str
    seq: int
    source: Literal["csv", "mqtt", "http", "serial"] = "csv"
    device_id: str
    station: str = "Unknown"
    city: str = "Unknown"
    province: str = "Unknown"
    ts: str
    received_at: str
    values: Dict[str, float]
    wqi: Optional[float] = 75.0
    pollution_level: Optional[str] = "Normal"
    remarks: Optional[str] = ""
    prediction: Literal["NORMAL", "ANOMALY"]
    anomaly_score: float
    threshold: float
    warming_up: bool = False
    contributing_features: List[str] = Field(default_factory=list)
    detector: DetectorSummary = Field(default_factory=DetectorSummary)
    latency: LatencyMetrics = Field(default_factory=LatencyMetrics)
    system: SystemUsageMetrics = Field(default_factory=SystemUsageMetrics)
    buffer_current: int = 1
    buffer_max: int = 30


class Prediction(BaseModel):
    score: float
    label: Literal["NORMAL", "ANOMALY"]
    contributions: Dict[str, float] = Field(default_factory=dict)


class SourceStatus(BaseModel):
    mode: Literal["csv", "device", "auto"]
    active_source: str
    is_streaming: bool
    interval_sec: float
    total_received: int
    last_seen: Optional[str] = None
    device_online_count: int = 0
    current_dataset: Optional[str] = None


class DeviceInfo(BaseModel):
    device_id: str
    transport: Literal["mqtt", "http", "serial", "csv"] = "mqtt"
    last_seen: str
    is_online: bool
    last_seq: int
    sample_count: int
    meta: Dict[str, Any] = Field(default_factory=dict)


class ConfigUpdate(BaseModel):
    threshold: Optional[float] = None
    window_size: Optional[int] = None
    interval_sec: Optional[float] = None
    source_mode: Optional[Literal["csv", "device", "auto"]] = None
    csv_file: Optional[str] = None
    csv_order: Optional[Literal["sequential", "random", "by_date"]] = None
    detector_type: Optional[Literal["rule_based", "onnx"]] = None
