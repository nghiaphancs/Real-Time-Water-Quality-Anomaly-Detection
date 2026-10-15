import os
import asyncio
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from edge.settings import load_settings, save_settings, get_project_root
from edge.schemas import Reading, ConfigUpdate
from edge.storage.db import Database
from edge.bus.mqtt_bus import MqttBus

root_dir = get_project_root()
settings = load_settings()
db = Database(os.path.join(root_dir, settings.storage.db_path))

# MqttBus instance to send control signals to Engine
mqtt_bus = MqttBus(settings.mqtt)

# Active WebSocket connections
active_websockets: List[WebSocket] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    mqtt_bus.connect()
    yield
    # Shutdown
    mqtt_bus.stop()

app = FastAPI(
    title="Edge Water QA API",
    version=settings.app.version,
    lifespan=lifespan,
)

# CORS Middleware with strict allow-list
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Routes -----------------

@app.get("/api/v1/schema")
def get_features_schema():
    """Single Source of Truth: Tráº£ vá» metadata 5 thÃ´ng sá»‘ cáº£m biáº¿n cho Frontend"""
    return settings.features

@app.get("/api/v1/latest")
def get_latest():
    """Láº¥y sá»‘ liá»‡u vÃ  káº¿t quáº£ suy luáº­n má»›i nháº¥t tá»« SQLite"""
    res = db.get_latest_result()
    if not res:
        return {"status": "waiting_for_data", "message": "ChÆ°a nháº­n Ä‘Æ°á»£c máº«u dá»¯ liá»‡u nÃ o tá»« nguá»“n"}
    return res

# TÆ°Æ¡ng thÃ­ch ngÆ°á»£c vá»›i endpoint cÅ© /api/latest
@app.get("/api/latest")
def get_latest_legacy():
    return get_latest()

@app.get("/api/v1/history")
def get_history(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    station: Optional[str] = None,
    prediction: Optional[str] = None,
    source: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Truy váº¥n lá»‹ch sá»­ Ä‘o cÃ³ phÃ¢n trang vÃ  bá»™ lá»c"""
    return db.query_history(
        limit=limit,
        offset=offset,
        station=station,
        prediction=prediction,
        source=source,
        start_date=start_date,
        end_date=end_date,
    )

@app.get("/api/history")
def get_history_legacy(limit: int = Query(50, ge=1, le=500)):
    return get_history(limit=limit)

@app.get("/api/v1/metrics")
def get_metrics():
    """Thá»‘ng kÃª hiá»‡u nÄƒng há»‡ thá»‘ng biÃªn (Inference Latency, E2E Latency, CPU, RAM)"""
    latest = db.get_latest_result()
    history = db.query_history(limit=100)

    if not history:
        return {"current": latest, "sample_count": 0, "avg_inference_latency_ms": 15.0}

    inf_latencies = [h["inference_latency_ms"] for h in history if "inference_latency_ms" in h]
    e2e_latencies = [h["end_to_end_latency_ms"] for h in history if "end_to_end_latency_ms" in h]
    anomalies = [h for h in history if h.get("prediction") == "ANOMALY"]

    avg_inf = round(sum(inf_latencies) / len(inf_latencies), 2) if inf_latencies else 15.0
    avg_e2e = round(sum(e2e_latencies) / len(e2e_latencies), 2) if e2e_latencies else 16.0
    anomaly_rate = round((len(anomalies) / len(history)) * 100, 2) if history else 0.0

    return {
        "current": latest,
        "sample_count": len(history),
        "anomaly_count": len(anomalies),
        "anomaly_rate_pct": anomaly_rate,
        "avg_inference_latency_ms": avg_inf,
        "avg_e2e_latency_ms": avg_e2e,
        "model_size_kb": latest.get("model_size_kb", 0.12) if latest else 0.12,
        "system_cpu_pct": latest.get("system_cpu_pct", 0.0) if latest else 0.0,
        "system_ram_pct": latest.get("system_ram_pct", 0.0) if latest else 0.0,
        "process_ram_mb": latest.get("process_ram_mb", 0.0) if latest else 0.0,
        "throughput_msg_per_sec": latest.get("throughput_msg_per_sec", 0.17) if latest else 0.17,
    }

@app.get("/api/metrics")
def get_metrics_legacy():
    return get_metrics()

@app.get("/api/v1/config")
def get_config():
    """Láº¥y cáº¥u hÃ¬nh hiá»‡n táº¡i"""
    return settings.model_dump()

@app.get("/api/config")
def get_config_legacy():
    return get_config()

@app.post("/api/v1/config")
def update_config(update: ConfigUpdate):
    """Cáº­p nháº­t cáº¥u hÃ¬nh vÃ  phÃ¡t tÃ­n hiá»‡u táº£i láº¡i nÃ³ng tá»›i Engine"""
    global settings
    if update.threshold is not None:
        settings.detector.threshold = update.threshold
    if update.window_size is not None:
        settings.detector.window_size = update.window_size
    if update.interval_sec is not None:
        settings.source.csv.interval_sec = update.interval_sec
    if update.source_mode is not None:
        settings.source.mode = update.source_mode
    if update.csv_file is not None:
        settings.source.csv.file = update.csv_file
    if update.csv_order is not None:
        settings.source.csv.order = update.csv_order
    if update.detector_type is not None:
        settings.detector.type = update.detector_type

    save_settings(settings)

    # Gá»­i tÃ­n hiá»‡u Ä‘iá»u khiá»ƒn nÃ³ng qua MQTT Bus
    mqtt_bus.publish_result(settings.mqtt.topics.control, {"action": "reload_config"})

    return {"status": "success", "applied": True, "config": settings.model_dump()}

@app.post("/api/config")
def update_config_legacy(update: ConfigUpdate):
    return update_config(update)

@app.get("/api/v1/datasets")
def list_datasets():
    """QuÃ©t thÆ° má»¥c data/datasets/ vÃ  tráº£ danh sÃ¡ch cÃ¡c tá»‡p CSV kháº£ dá»¥ng"""
    datasets_dir = os.path.join(root_dir, "data", "datasets")
    files = []
    if os.path.exists(datasets_dir):
        for f in os.listdir(datasets_dir):
            if f.endswith(".csv"):
                f_path = os.path.join(datasets_dir, f)
                files.append({
                    "name": f,
                    "size_kb": round(os.path.getsize(f_path) / 1024, 1),
                    "is_active": (f == settings.source.csv.file),
                })
    return {"datasets": files, "active": settings.source.csv.file}

@app.get("/api/v1/devices")
def list_devices():
    """Danh sÃ¡ch cÃ¡c thiáº¿t bá»‹ Raspberry Pi / IoT Ä‘Ã£ Ä‘Äƒng kÃ½"""
    return db.get_devices(timeout_sec=settings.source.device.timeout_sec)

@app.post("/api/v1/ingest")
def ingest_reading(reading: Reading):
    """KÃªnh nháº­n dá»¯ liá»‡u HTTP REST tá»« Raspberry Pi hoáº·c vi Ä‘iá»u khiá»ƒn"""
    # PhÃ¡t gÃ³i tin sang MQTT Ä‘á»ƒ Engine tiáº¿p nháº­n
    payload = reading.model_dump()
    mqtt_bus.publish_result("devices/" + reading.device_id + "/telemetry", payload)
    return {"status": "accepted", "device_id": reading.device_id, "seq": reading.seq}

@app.get("/api/v1/export")
def export_log():
    """Táº£i tá»‡p CSV benchmark_log"""
    log_path = os.path.join(root_dir, settings.storage.csv_log)
    if os.path.exists(log_path):
        return FileResponse(log_path, media_type="text/csv", filename="water_edge_benchmark_log.csv")
    raise HTTPException(status_code=404, detail="ChÆ°a cÃ³ tá»‡p benchmark_log.csv")

@app.get("/api/export")
def export_log_legacy():
    return export_log()

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.app.name,
        "version": settings.app.version,
        "mqtt_connected": mqtt_bus._connected,
    }

@app.websocket("/ws/live")
async def websocket_live_stream(ws: WebSocket):
    """KÃªnh Ä‘áº©y dá»¯ liá»‡u thá»i gian thá»±c theo chu ká»³ cho Frontend"""
    await ws.accept()
    active_websockets.append(ws)
    try:
        last_seq = None
        while True:
            latest = db.get_latest_result()
            if latest and latest.get("seq") != last_seq:
                last_seq = latest.get("seq")
                await ws.send_json(latest)
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        if ws in active_websockets:
            active_websockets.remove(ws)
    except Exception:
        if ws in active_websockets:
            active_websockets.remove(ws)

# Phá»¥c vá»¥ thÆ° má»¥c tÄ©nh Frontend Ä‘Ã£ build (pháº£i Ä‘áº·t á»Ÿ cuá»‘i cÃ¹ng Ä‘á»ƒ khÃ´ng che API routes)
dist_dir = os.path.join(root_dir, "dashboard", "dist")
if not os.path.exists(dist_dir):
    dist_dir = os.path.join(root_dir, "frontend", "dist")
if os.path.exists(dist_dir):
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="frontend")

