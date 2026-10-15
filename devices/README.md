# Giao thức & Kết nối Thiết bị (devices/)

Hệ thống hỗ trợ 3 giao thức để nhận số liệu trực tiếp từ Raspberry Pi hoặc vi điều khiển.

## 1. Giao thức MQTT (Khuyến nghị)
- **Broker:** `127.0.0.1:1883` (hoặc IP máy chủ khi cấu hình LAN)
- **Topic đẩy số liệu:** `devices/<device_id>/telemetry`
- **Ví dụ lệnh gửi (mosquitto_pub):**
```bash
mosquitto_pub -h 127.0.0.1 -p 1883 -t "devices/rpi_01/telemetry" -m '{
  "device_id": "rpi_01",
  "seq": 1,
  "ts": "2026-10-14T21:45:00",
  "values": {
    "pH": 7.35,
    "DO": 8.10,
    "turbidity": 1.15,
    "EC": 435.0,
    "temperature": 24.2
  },
  "meta": {
    "station": "Tram_Khao_Sat_1",
    "city": "HoChiMinh"
  }
}'
```

## 2. Giao thức HTTP REST
- **Endpoint:** `POST http://127.0.0.1:8000/api/v1/ingest`
- **Content-Type:** `application/json`
- **Ví dụ lệnh gửi (curl):**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "rpi_02",
    "seq": 1,
    "values": { "pH": 7.1, "DO": 7.9, "turbidity": 1.4, "EC": 410.0, "temperature": 23.0 },
    "meta": { "station": "Lab_Tram_2" }
  }'
```

## 3. Giao thức Serial / USB
- **Cổng:** `/dev/ttyUSB0` hoặc `/dev/ttyACM0`
- **Tốc độ (Baud):** `9600`
- Định dạng mỗi dòng: Chuỗi JSON hợp lệ hoặc chuỗi CSV `pH,DO,turbidity,EC,temperature\n`.
