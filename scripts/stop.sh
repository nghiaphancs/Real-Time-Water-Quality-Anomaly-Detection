#!/bin/bash
# Script dừng toàn bộ tiến trình Edge Water QA

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

RUNTIME_DIR="$PROJECT_DIR/data/runtime"
PID_FILE="$RUNTIME_DIR/edge.pid"

echo "=== Đang dừng dịch vụ Edge Water QA ==="

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        sleep 1
        kill -9 "$PID" 2>/dev/null || true
        echo "✅ Đã dừng tiến trình Edge (PID: $PID)"
    fi
    rm -f "$PID_FILE"
fi

# Dọn dẹp bất kỳ tiến trình python edge / uvicorn / mock_sensor còn sót
pkill -f "python -m edge" 2>/dev/null || true
pkill -f "edge.api.app" 2>/dev/null || true
pkill -f "mock_sensor.py" 2>/dev/null || true

echo "✅ Hoàn tất dừng toàn bộ hệ thống."
