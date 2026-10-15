import os
import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from edge.schemas import Result, DeviceInfo


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    event_id TEXT PRIMARY KEY,
                    seq INTEGER,
                    source TEXT,
                    device_id TEXT,
                    station TEXT,
                    city TEXT,
                    province TEXT,
                    ts TEXT,
                    received_at TEXT,
                    pH REAL,
                    DO REAL,
                    turbidity REAL,
                    EC REAL,
                    temperature REAL,
                    wqi REAL,
                    pollution_level TEXT,
                    remarks TEXT,
                    prediction TEXT,
                    anomaly_score REAL,
                    threshold REAL,
                    warming_up INTEGER,
                    contributing_features TEXT,
                    inference_latency_ms REAL,
                    e2e_latency_ms REAL,
                    system_cpu_pct REAL,
                    system_ram_pct REAL,
                    process_ram_mb REAL,
                    throughput REAL
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_results_ts ON results(ts);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_results_station ON results(station);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_results_pred ON results(prediction);")

            conn.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    device_id TEXT PRIMARY KEY,
                    transport TEXT,
                    last_seen TEXT,
                    is_online INTEGER,
                    last_seq INTEGER,
                    sample_count INTEGER,
                    meta TEXT
                );
            """)

    def insert_result(self, res: Result):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO results (
                    event_id, seq, source, device_id, station, city, province, ts, received_at,
                    pH, DO, turbidity, EC, temperature, wqi, pollution_level, remarks,
                    prediction, anomaly_score, threshold, warming_up, contributing_features,
                    inference_latency_ms, e2e_latency_ms, system_cpu_pct, system_ram_pct,
                    process_ram_mb, throughput
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                res.event_id, res.seq, res.source, res.device_id, res.station, res.city, res.province,
                res.ts, res.received_at,
                res.values.get("pH", 0.0), res.values.get("DO", 0.0), res.values.get("turbidity", 0.0),
                res.values.get("EC", 0.0), res.values.get("temperature", 0.0),
                res.wqi, res.pollution_level, res.remarks,
                res.prediction, res.anomaly_score, res.threshold, 1 if res.warming_up else 0,
                json.dumps(res.contributing_features, ensure_ascii=False),
                res.latency.inference_ms, res.latency.e2e_ms,
                res.system.system_cpu_pct, res.system.system_ram_pct, res.system.process_ram_mb,
                res.system.throughput_msg_per_sec
            ))

    def update_device(self, device_id: str, transport: str, seq: int, meta: Dict[str, Any]):
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO devices (device_id, transport, last_seen, is_online, last_seq, sample_count, meta)
                VALUES (?, ?, ?, 1, ?, 1, ?)
                ON CONFLICT(device_id) DO UPDATE SET
                    transport = excluded.transport,
                    last_seen = excluded.last_seen,
                    is_online = 1,
                    last_seq = excluded.last_seq,
                    sample_count = sample_count + 1,
                    meta = excluded.meta;
            """, (device_id, transport, now, seq, json.dumps(meta, ensure_ascii=False)))

    def get_devices(self, timeout_sec: float = 30.0) -> List[DeviceInfo]:
        devices = []
        now = datetime.now()
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM devices ORDER BY last_seen DESC;").fetchall()
            for r in rows:
                last_seen_dt = datetime.fromisoformat(r["last_seen"])
                diff = (now - last_seen_dt).total_seconds()
                is_online = diff < timeout_sec
                devices.append(DeviceInfo(
                    device_id=r["device_id"],
                    transport=r["transport"],
                    last_seen=r["last_seen"],
                    is_online=is_online,
                    last_seq=r["last_seq"],
                    sample_count=r["sample_count"],
                    meta=json.loads(r["meta"]) if r["meta"] else {}
                ))
        return devices

    def get_latest_result(self) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM results ORDER BY seq DESC, received_at DESC LIMIT 1;").fetchone()
            if not row:
                return None
            return self._row_to_result_dict(row)

    def query_history(
        self,
        limit: int = 50,
        offset: int = 0,
        station: Optional[str] = None,
        prediction: Optional[str] = None,
        source: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        conditions = []
        params = []

        if station and station != "ALL":
            conditions.append("station = ?")
            params.append(station)
        if prediction and prediction != "ALL":
            conditions.append("prediction = ?")
            params.append(prediction)
        if source and source != "ALL":
            conditions.append("source = ?")
            params.append(source)
        if start_date:
            conditions.append("ts >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("ts <= ?")
            params.append(end_date)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"SELECT * FROM results {where_clause} ORDER BY seq DESC, received_at DESC LIMIT ? OFFSET ?;"
        params.extend([limit, offset])

        with self._get_conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_result_dict(r) for r in rows]

    def _row_to_result_dict(self, r: sqlite3.Row) -> Dict[str, Any]:
        return {
            "event_id": r["event_id"],
            "seq": r["seq"],
            "source": r["source"],
            "device_id": r["device_id"],
            "station": r["station"],
            "city": r["city"],
            "province": r["province"],
            "ts": r["ts"],
            "sensor_timestamp": r["ts"],
            "received_at": r["received_at"],
            "pH": r["pH"],
            "DO": r["DO"],
            "turbidity": r["turbidity"],
            "EC": r["EC"],
            "temperature": r["temperature"],
            "wqi": r["wqi"],
            "pollution_level": r["pollution_level"],
            "remarks": r["remarks"],
            "prediction": r["prediction"],
            "anomaly_score": r["anomaly_score"],
            "threshold": r["threshold"],
            "warming_up": bool(r["warming_up"]),
            "contributing_features": json.loads(r["contributing_features"]) if r["contributing_features"] else [],
            "inference_latency_ms": r["inference_latency_ms"],
            "end_to_end_latency_ms": r["e2e_latency_ms"],
            "system_cpu_pct": r["system_cpu_pct"],
            "system_ram_pct": r["system_ram_pct"],
            "process_ram_mb": r["process_ram_mb"],
            "throughput_msg_per_sec": r["throughput"],
        }
