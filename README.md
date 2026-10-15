# Real-Time Water Quality Anomaly Detection & Monitoring System

An **Edge–Cloud Collaborative System** for real-time water quality monitoring, anomaly detection, and Water Quality Index (WQI) forecasting.

## 📌 Architecture Overview

This project implements a multi-tier Edge-Cloud collaborative framework designed for environmental monitoring:

`	ext
[ Sensor / Device Agent / CSV Source ] ──(MQTT/HTTP/Serial)──> [ Mosquitto Broker ]
                                                                       │
                                                                       ▼
                                                             [ Edge Runtime Node ]
                                                        (Pipeline, Detector, Storage)
                                                                       │
                                      ┌────────────────────────────────┴────────────────────────┐
                                      ▼                                                         ▼
                             [ Edge Local Dashboard ]                                   [ Cloud Backend ]
                                (FastAPI + React)                                   (TimescaleDB + Cloud AI)
`

- **Edge Node (edge/):** Conducts real-time fast screening (Rule-based) and deep anomaly detection (ONNX Runtime) on sliding window telemetry. Calculates real-time WQI, triggers local responses, buffers telemetry in local SQLite (waterqa.db), and exposes REST/WebSocket APIs.
- **Web Dashboard (dashboard/):** Modern frontend built with React 19, TypeScript, Tailwind CSS, and Recharts for live telemetry visualization, real-time charts, historical review, and alert logs.
- **Hardware / Device Agent (devices/):** Edge agent running on Raspberry Pi or IoT gateways with support for MQTT, HTTP, and Serial sensor streams.
- **Cloud Backend (ackend/):** Cloud-level ingestion, historical time-series storage (TimescaleDB), long-term WQI prediction, and remote fleet management.

---

## 📂 Repository Structure

`	ext
.
├── backend/            # FastAPI Cloud Backend (Cloud AI, TimescaleDB ingestion)
├── configs/            # System & sensor configurations (app.yaml, features.yaml, mosquitto)
├── dashboard/          # React + TypeScript + Tailwind CSS Web Dashboard
├── data/               # Datasets, ONNX models, benchmark logs, and runtime data
│   ├── datasets/       # Historical telemetry CSVs (e.g. china_water_pollution_data.csv)
│   ├── models/         # Machine learning models (ONNX + metadata)
│   └── logs/           # Benchmark and performance logs
├── devices/            # IoT & Raspberry Pi agent scripts
├── edge/               # Edge AI Core (Inference Engine, Detectors, Pipeline, API)
│   ├── api/            # FastAPI REST & WebSocket server
│   ├── bus/            # MQTT Bus Client
│   ├── detectors/      # Rule-based & ONNX inference detectors
│   ├── pipeline/       # Sliding window, normalizer, WQI calculation, inference engine
│   ├── sources/        # Data sources (CSV, MQTT, HTTP, Serial) & SourceManager
│   └── storage/        # SQLite local buffer & CSV logging
├── mosquitto/          # Mosquitto MQTT Broker configuration for Docker
├── scripts/            # Management scripts (start, stop, status, calibrate, view_db)
├── tests/              # Automated pytest test suites
├── Spec/               # System Specifications & Architecture Documentation
├── docker-compose.yml  # Docker environment setup (Mosquitto MQTT & TimescaleDB)
├── Makefile            # Project automation commands
├── requirements.txt    # Unified Python dependencies
└── README.md
`

---

## 🚀 Getting Started

### Prerequisites

- [Docker & Docker Compose](https://www.docker.com/) (optional, for Mosquitto & TimescaleDB containers)
- [Python 3.10+](https://www.python.org/)
- [Node.js 18+](https://nodejs.org/) & npm

### 1. Quick Start (Edge Engine & Dashboard)

#### Setup Python Virtual Environment:
`ash
python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows PowerShell:
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
`

#### Run All Services:
`ash
# Start Edge Engine + API server (Serving on port 8000):
python -m edge all

# Or use scripts:
./scripts/start.sh
`

#### Run Frontend Dashboard (Development Mode):
`ash
cd dashboard
npm install
npm run dev
`
Open your browser at http://localhost:5173 (or http://localhost:8000 for integrated static build).

---

### 2. Run Tests

Execute the automated test suite with pytest:

`ash
pytest tests/ -v
`

---

### 3. Docker Infrastructure (Optional)

From the root directory, start the Mosquitto MQTT Broker and PostgreSQL/TimescaleDB container:

`ash
docker-compose up -d
`

---

## 🛠 Tech Stack

- **Edge AI Runtime:** Python 3.10+, ONNX Runtime, NumPy, Pydantic, SQLite, Paho-MQTT
- **Web Dashboard:** React 19, TypeScript, Vite, Tailwind CSS, Recharts, Lucide React
- **Cloud Backend:** FastAPI, SQLAlchemy, PostgreSQL / TimescaleDB
- **Broker & Protocols:** Eclipse Mosquitto, MQTT, WebSockets, HTTP, Serial

---

## 📄 License

This project is open-source and created for academic research in Edge AI and IoT water quality monitoring.
