#!/bin/bash
# Script khởi động Edge Water QA System

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

VENV_PY="$PROJECT_DIR/.venv/bin/python"
RUNTIME_DIR="$PROJECT_DIR/data/runtime"
mkdir -p "$RUNTIME_DIR" logs

PID_FILE="$RUNTIME_DIR/edge.pid"

if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "⚠️  Hệ thống đang chạy với PID: $(cat "$PID_FILE")"
    exit 0
fi

# Kiểm tra Mosquitto Broker
if ! ss -tulpn | grep -q ":1883"; then
    echo "=== Khởi động Mosquitto Broker... ==="
    sudo systemctl start mosquitto || mosquitto -c configs/mosquitto/local.conf -d
fi

export PYTHONPATH="$PROJECT_DIR"
echo "=== Khởi động Edge Engine & Web Server ==="
nohup setsid "$VENV_PY" -m edge all < /dev/null >> logs/edge.log 2>&1 &
EDGE_PID=$!
echo $EDGE_PID > "$PID_FILE"

sleep 2

if kill -0 $EDGE_PID 2>/dev/null; then
    echo "✅ KHỞI ĐỘNG THÀNH CÔNG (PID: $EDGE_PID)"
    echo "👉 Truy cập Dashboard tại: http://127.0.0.1:8000"
    echo "👉 Kiểm tra trạng thái: ./scripts/status.sh"
else
    echo "❌ Khởi động thất bại. Kiểm tra log tại: logs/edge.log"
    cat logs/edge.log | tail -15
    exit 1
fi
