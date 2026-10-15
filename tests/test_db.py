import os
import pytest
from edge.storage.db import Database
from edge.schemas import Result, DetectorSummary, LatencyMetrics, SystemUsageMetrics


def test_db_insert_and_query(tmp_path):
    db_file = os.path.join(tmp_path, "test.db")
    db = Database(db_file)

    res = Result(
        event_id="test_evt_1",
        seq=1,
        source="csv",
        device_id="station_test",
        station="Station Test",
        city="Hanoi",
        province="Vietnam",
        ts="2026-10-14T20:00:00",
        received_at="2026-10-14T20:00:01",
        values={"pH": 7.3, "DO": 8.1, "turbidity": 1.2, "EC": 410.0, "temperature": 22.0},
        prediction="NORMAL",
        anomaly_score=0.21,
        threshold=0.35,
        warming_up=False,
    )

    db.insert_result(res)
    latest = db.get_latest_result()
    assert latest is not None
    assert latest["event_id"] == "test_evt_1"
    assert latest["pH"] == 7.3

    history = db.query_history(limit=10)
    assert len(history) == 1
    assert history[0]["prediction"] == "NORMAL"
