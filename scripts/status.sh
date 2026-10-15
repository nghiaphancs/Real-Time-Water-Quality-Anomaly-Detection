#!/bin/bash
# Script kiểm tra trạng thái hoạt động của hệ thống

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

RUNTIME_DIR="$PROJECT_DIR/data/runtime"
PID_FILE="$RUNTIME_DIR/edge.pid"

echo "==============================================="
echo "   KIỂM TRA TRẠNG THÁI HỆ THỐNG EDGE WATER QA  "
echo "==============================================="

if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "🟢 Edge Service: ĐANG CHẠY (PID: $(cat "$PID_FILE"))"
else
    echo "🔴 Edge Service: ĐÃ DỪNG"
fi

if ss -tulpn | grep -q ":1883"; then
    echo "🟢 Mosquitto MQTT (Port 1883): ĐANG LẮNG NGHE"
else
    echo "🔴 Mosquitto MQTT (Port 1883): CHƯA HOẠT ĐỘNG"
fi

if ss -tulpn | grep -q ":9001"; then
    echo "🟢 Mosquitto WebSockets (Port 9001): ĐANG LẮNG NGHE"
else
    echo "🔴 Mosquitto WebSockets (Port 9001): CHƯA HOẠT ĐỘNG"
fi

if ss -tulpn | grep -q ":8000"; then
    echo "🟢 API & Web Dashboard (Port 8000): SẴN SÀNG"
    curl -s http://127.0.0.1:8000/api/v1/health | head -n 5
    echo ""
else
    echo "🔴 API & Web Dashboard (Port 8000): CHƯA HOẠT ĐỘNG"
fi
echo "==============================================="
