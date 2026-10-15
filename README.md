# Real-Time Water Quality Anomaly Detection & Monitoring System

### Hệ thống Giám sát & Phát hiện Bất thường Chất lượng Nước Thời gian Thực

<p align="center">
  <a href="#-english"><b>English</b></a> •
  <a href="#-tiếng-việt"><b>Tiếng Việt</b></a>
</p>

---

# 🇬🇧 English

An **Edge–Cloud Collaborative System** for real-time water quality monitoring, rapid anomaly detection (pH, Dissolved Oxygen, Turbidity, Conductivity, Temperature), and Water Quality Index (WQI) forecasting.

---

## 1. Architecture Overview

```text
[ IoT Sensor / Raspberry Pi / CSV ] ──(MQTT / HTTP / Serial)──> [ Mosquitto Broker ]
                                                                       │
                                                                       ▼
                                                             [ Edge Runtime Node ]
                                                       (Pipeline, Detectors, Storage)
                                                                       │
                                      ┌────────────────────────────────┴────────────────────────┐
                                      ▼                                                         ▼
                             [ Local Dashboard ]                                        [ Cloud Backend ]
                           (FastAPI + React 19)                                     (TimescaleDB + Cloud AI)
```

- **Edge Runtime (`edge/`):** Performs real-time fast screening (Rule-based) and deep anomaly inference (ONNX Runtime) over sliding telemetry windows. Computes instant WQI, buffers data locally in SQLite (`waterqa.db`), and serves local REST/WebSocket APIs.
- **Web Dashboard (`dashboard/`):** Built with React 19, TypeScript, Tailwind CSS, and Recharts for live telemetry gauges, historical trends, alert logs, and operational controls.
- **Device Agent (`devices/`):** Lightweight IoT agent designed for Raspberry Pi with pluggable transport protocols (MQTT, HTTP REST, and Serial USB).
- **Cloud Backend (`backend/`):** FastAPI Cloud service for persistent telemetry aggregation, TimescaleDB integration, and long-term WQI forecasting.
- **Docker Infrastructure (`mosquitto/`, `docker-compose.yml`):** Containerized Mosquitto MQTT broker (ports 1883 & 9001 WebSockets) and TimescaleDB time-series database.

---

## 2. Worktree Layout

```text
Real-Time-Water-Quality-Anomaly-Detection/
├── backend/                  # FastAPI Cloud Backend (Cloud AI & Ingestion)
├── configs/                  # System configurations (app.yaml, features.yaml, mosquitto)
├── dashboard/                # Modern React + Vite + Tailwind CSS Web Dashboard
├── data/                     # Datasets, ONNX models, runtime databases, and logs
│   ├── datasets/             # Historical CSV datasets (china_water_pollution_data.csv)
│   ├── models/               # ONNX model files (.onnx) and model.yaml metadata
│   └── logs/                 # Benchmark and performance evaluation logs
├── devices/                  # IoT Device & Gateway Agents (Raspberry Pi agent)
├── edge/                     # Edge AI Core Runtime
│   ├── api/                  # FastAPI REST API & WebSocket server
│   ├── bus/                  # MQTT Client Bus
│   ├── detectors/            # Inference detectors: Rule-based & ONNX Runtime
│   ├── pipeline/             # Normalizer, Sliding Window, WQI Calculator, Engine
│   ├── sources/              # Data sources: CSV, MQTT, HTTP, Serial & SourceManager
│   └── storage/              # SQLite local buffer & CSV benchmark writer
├── mosquitto/                # Mosquitto MQTT Broker Docker configuration
├── scripts/                  # Operational scripts (start, stop, status, view_db...)
├── Spec/                     # System specifications & requirements document
├── tests/                    # Automated pytest test suites (13/13 passing)
├── docker-compose.yml        # Docker setup (Mosquitto Broker + TimescaleDB)
├── Makefile                  # Automation shortcuts (run, test, build-dashboard)
├── requirements.txt          # Unified Python dependencies
└── README.md
```

---

## 3. Quick Start

### Prerequisites

- **Python 3.10+** (in a virtual environment `.venv`)
- **Node.js 18+ & npm 10+**
- **Mosquitto MQTT Broker** (ports 1883 and 9001) or Docker

### Installation & Execution

```bash
# 1. Setup Python Virtual Environment
python -m venv .venv
source .venv/bin/activate       # On Linux/macOS
# or: .venv\Scripts\Activate.ps1 # On Windows PowerShell
pip install -r requirements.txt

# 2. Launch Edge Engine & Server
./start.sh
# or:
make run
```

### Accessing the Web Dashboard

- **Web Dashboard & API:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Vite Dev Server (Frontend Development):** [http://127.0.0.1:5173](http://127.0.0.1:5173)

### Service Management

```bash
./scripts/status.sh   # Check service and port status
./stop.sh             # Gracefully stop the system
```

---

## 4. Data Ingestion: CSV ⇄ IoT Devices

The system supports seamless hot-switching between data sources:

1. **CSV Mock Mode:** Reads records from `data/datasets/china_water_pollution_data.csv` with configurable intervals and playback orders (`sequential` or `random`).
2. **IoT Device Mode:** Receives telemetry from external hardware (Raspberry Pi / microcontrollers) via MQTT, HTTP POST, or Serial USB.
3. **Auto Fallback:** Prioritizes active device connections and falls back to CSV playback if no device telemetry is detected for 30 seconds.

---

## 5. Machine Learning & Anomaly Detection

- **Rule-based Detector:** Fast boundary checking calibrated via `scripts/calibrate_rule_based.py`.
- **ONNX Runtime Detector:** Deep inference engine consuming pre-trained models.
  - Drop your `.onnx` model into `data/models/`.
  - Configure tensor schemas in `data/models/model.yaml`.
  - Switch active detectors dynamically through the Web Dashboard or API:
    ```bash
    curl -X POST http://127.0.0.1:8000/api/v1/config \
      -H "Content-Type: application/json" \
      -d '{"detector_type": "onnx"}'
    ```

---

## 6. Automated Testing

Run the pytest suite covering all components (Normalizer, CSV Source, Detectors, Storage, WQI):

```bash
make test
# or:
pytest tests/ -v
```

---

<br/>

# 🇻🇳 Tiếng Việt

**Hệ thống quan trắc và suy luận trí tuệ nhân tạo biên (Edge AI)** phát hiện sớm các bất thường trong chất lượng nguồn nước (pH, Oxy hòa tan DO, Độ đục, Độ dẫn điện EC, Nhiệt độ) theo thời gian thực và dự báo chỉ số WQI.

---

## 1. Tổng quan Kiến trúc

```text
[ Cảm biến IoT / Raspberry Pi / CSV ] ──(MQTT / HTTP / Serial)──> [ Mosquitto Broker ]
                                                                         │
                                                                         ▼
                                                               [ Edge Runtime Node ]
                                                          (Pipeline, Detectors, Storage)
                                                                         │
                                        ┌────────────────────────────────┴────────────────────────┐
                                        ▼                                                         ▼
                               [ Web Dashboard ]                                          [ Cloud Backend ]
                             (FastAPI + React 19)                                     (TimescaleDB + Cloud AI)
```

- **Edge Runtime (`edge/`):** Sàng lọc nhanh (Rule-based) và suy luận mô hình học sâu (ONNX Runtime) trên cửa sổ trượt telemetry. Tự động tính toán WQI tức thời, lưu đệm cục bộ vào SQLite (`waterqa.db`), và cung cấp REST API/WebSocket.
- **Web Dashboard (`dashboard/`):** Xây dựng bằng React 19, TypeScript, Tailwind CSS và Recharts; hiển thị trực quan thông số đo, đồng hồ đo, biểu đồ thời gian thực, lịch sử và cảnh báo.
- **Agent Thiết bị (`devices/`):** Module chạy trên thiết bị ngoại vi (Raspberry Pi/vi điều khiển) hỗ trợ gửi qua MQTT, HTTP REST hoặc Serial USB.
- **Cloud Backend (`backend/`):** Dịch vụ FastAPI phía đám mây phục vụ tổng hợp dữ liệu, tích hợp cơ sở dữ liệu TimescaleDB và dự báo WQI dài hạn.
- **Hạ tầng Docker (`mosquitto/`, `docker-compose.yml`):** Mosquitto MQTT Broker (hỗ trợ cổng TCP 1883 và WebSockets 9001) và TimescaleDB lưu trữ chuỗi thời gian.

---

## 2. Cấu trúc Dự án (Worktree Layout)

```text
Real-Time-Water-Quality-Anomaly-Detection/
├── backend/                  # Mã nguồn FastAPI Cloud Backend (Cloud AI & Ingestion)
├── configs/                  # Tệp cấu hình hệ thống & cảm biến
│   ├── app.yaml              # Cấu hình chính (chế độ nguồn, detector, mqtt, api, storage)
│   ├── features.yaml         # Single Source of Truth cho 5 thông số cảm biến
│   ├── mappings/             # Bản đồ ánh xạ cột dữ liệu CSV
│   └── mosquitto/            # Cấu hình Mosquitto Broker (local & template LAN)
├── dashboard/                # Giao diện Web Dashboard (React + TypeScript + Tailwind)
├── data/                     # Thư mục dữ liệu runtime, mô hình và nhật ký
│   ├── datasets/             # Chứa tệp CSV (china_water_pollution_data.csv)
│   ├── models/               # Chứa mô hình ONNX (.onnx & model.yaml)
│   └── logs/                 # Nhật ký benchmark hiệu năng (benchmark_log.csv)
├── devices/                  # Chương trình chạy trên thiết bị ngoại vi (Raspberry Pi)
│   ├── rpi_agent/            # Agent cho Raspberry Pi (MQTT, HTTP, Serial)
│   └── README.md             # Hướng dẫn kết nối thiết bị ngoại vi
├── edge/                     # Mã nguồn lõi xử lý biên Edge AI
│   ├── api/                  # FastAPI REST API & WebSocket server
│   ├── bus/                  # MQTT Bus (paho-mqtt v2, LWT, reconnect)
│   ├── detectors/            # Bộ suy luận: Rule-based & ONNX Runtime
│   ├── pipeline/             # Chuẩn hóa, Cửa sổ trượt, Đo hiệu năng, Tính WQI, Engine
│   ├── sources/              # Nguồn dữ liệu: CSV, MQTT, HTTP, Serial & SourceManager
│   └── storage/              # SQLite DB & CSV log writer
├── mosquitto/                # Cấu hình Mosquitto Broker cho Docker
├── scripts/                  # Kịch bản vận hành & công cụ hỗ trợ
│   ├── start.sh              # Khởi động toàn bộ hệ thống
│   ├── stop.sh               # Dừng toàn bộ hệ thống
│   ├── status.sh             # Kiểm tra trạng thái cổng & dịch vụ
│   ├── calibrate_rule_based.py # Hiệu chuẩn ngưỡng & phân phối điểm số
│   └── view_db.py            # Xem nhanh số liệu lưu trữ trong SQLite
├── Spec/                     # Bản đặc tả kỹ thuật hệ thống (MVP specs)
├── tests/                    # Kiểm thử tự động (pytest)
├── docker-compose.yml        # Cấu hình khởi chạy Docker (Mosquitto + TimescaleDB)
├── Makefile                  # Lệnh tiện ích make run / make test
├── requirements.txt          # Danh sách thư viện Python toàn hệ thống
└── README.md
```

---

## 3. Khởi động Nhanh

### Yêu cầu môi trường

- **Python 3.10+** (đã tạo virtual environment tại `.venv`)
- **Node.js 18+ & npm 10+**
- **Mosquitto MQTT Broker** (lắng nghe cổng 1883 và WebSockets 9001) hoặc Docker

### Lệnh chạy

Chỉ cần thực hiện 1 lệnh:

```bash
./start.sh
# hoặc:
make run
```

### Truy cập Giao diện & API

- **Web Dashboard & API:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Vite Dev Server (khi phát triển UI):** [http://127.0.0.1:5173](http://127.0.0.1:5173)

### Kiểm tra trạng thái & Dừng

```bash
./scripts/status.sh   # Kiểm tra trạng thái dịch vụ và cổng mạng
./stop.sh             # Dừng hệ thống an toàn
```

---

## 4. Chuyển đổi Nguồn Dữ liệu: CSV ⇄ Thiết bị

Hệ thống cho phép chuyển đổi nóng nguồn cấp số liệu mà không cần khởi động lại:

### Cách 1: Chuyển đổi qua Giao diện Web

Vào tab **Cài đặt & Cấu hình (Settings)** trên Dashboard:

1. **CSV (Giả lập):** Chọn tệp CSV từ dropdown trong thư mục `data/datasets/`, chọn thứ tự phát (`sequential` từ trên xuống hoặc `random`).
2. **Thiết bị IoT:** Tiếp nhận trực tiếp số liệu từ Raspberry Pi / vi điều khiển.
3. **Tự động (Auto):** Ưu tiên thiết bị khi có kết nối; tự động chuyển sang phát lại CSV nếu mất tín hiệu quá 30 giây.

### Cách 2: Kết nối Thiết bị Thật (Raspberry Pi)

Thiết bị có thể gửi dữ liệu qua bất kỳ giao thức nào trong 3 giao thức sau:

1. **MQTT:** Gửi gói tin JSON tới topic `devices/<device_id>/telemetry`.
2. **HTTP REST:** Gửi HTTP POST tới `http://127.0.0.1:8000/api/v1/ingest`.
3. **Serial USB:** Cắm cổng `/dev/ttyUSB0` gửi mỗi dòng 1 chuỗi JSON hoặc định dạng `pH,DO,turbidity,EC,temperature`.

Chi tiết mẫu lệnh xem tại [`devices/README.md`](devices/README.md).

---

## 5. Tích hợp Mô hình AI (ONNX)

Hệ thống đã có sẵn khung `OnnxDetector` và kiểm tra hợp đồng dữ liệu tensor:

1. Thả tệp mô hình `.onnx` vào thư mục [`data/models/`](data/models/).
2. Tạo tệp `model.yaml` mô tả cấu trúc tensor đầu vào/đầu ra (mẫu tại `data/models/model.yaml`).
3. Chuyển đổi mô hình trực tiếp trên Web UI hoặc gửi API:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{"detector_type": "onnx"}'
```

---

## 6. Kiểm thử Tự động (Tests)

Chạy bộ kiểm thử tự động với 13 bài test (Normalizer, CSV Source, Detector, Database, WQI Calculation):

```bash
make test
# hoặc:
pytest tests/ -v
```
