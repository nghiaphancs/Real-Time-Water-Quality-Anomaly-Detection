# Real-Time Water Quality Anomaly Detection & Monitoring System

An **Edge-Cloud Collaborative System** for real-time water quality monitoring, anomaly detection, and Water Quality Index (WQI) forecasting.

## 📌 Architecture Overview

This project implements a multi-tier Edge-Cloud collaborative framework designed for environmental monitoring:

```text
[ Data Simulator ] --(MQTT)--> [ Mosquitto Broker ] --> [ Edge Runtime ]
                                                              │
                                                        Fast Screening & Deep Anomaly Detection
                                                              │
                                                              ▼
[ Web Dashboard ] <--(REST/WS)-- [ Cloud Backend ] <--(MQTT)--┘
```

- **Edge Node:** Conducts real-time fast screening (Isolation Forest) and deep anomaly detection (GRU Autoencoder) on sliding window telemetry. Triggers instant local responses (LED/Buzzer) and buffers data locally when offline.
- **Cloud Backend:** Ingests sensor data, calculates WQI, predicts WQI using ML models (e.g., XGBoost/LightGBM), provides REST/WebSocket APIs, and handles notifications.
- **Data Simulator:** Reads historical sensor data and simulates continuous MQTT telemetry streaming.
- **Web Dashboard:** Interactive frontend built with React, Vite, and TypeScript for real-time telemetry visualization and alert monitoring.

---

## 📁 Repository Structure

```text
.
├── backend/            # FastAPI Cloud Backend (REST APIs, Ingestion, WQI Engine)
├── dashboard/          # React + TypeScript + Vite Web Dashboard
├── edge/               # Edge Runtime Node (MQTT Client, Local SQLite Buffer, ML Inference)
├── simulator/          # MQTT Data Simulator (CSV-based streaming)
├── Dataset/            # Water Quality Datasets
├── Spec/               # System Specifications & Architecture Documentation
├── docker-compose.yml  # Docker environment setup (Mosquitto MQTT & TimescaleDB)
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- [Docker & Docker Compose](https://www.docker.com/)
- [Python 3.9+](https://www.python.org/)
- [Node.js 18+](https://nodejs.org/)

### 1. Start Infrastructure (Broker & Database)

From the root directory, start the Mosquitto MQTT Broker and PostgreSQL/TimescaleDB container:

```bash
docker-compose up -d
```

### 2. Run the Data Simulator

```bash
cd simulator
pip install -r requirements.txt
python simulate.py
```

### 3. Run the Edge Node

```bash
cd edge
pip install -r requirements.txt
python edge_node.py
```

### 4. Start Cloud Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
API Documentation will be available at `http://localhost:8000/docs`.

### 5. Launch Web Dashboard

```bash
cd dashboard
npm install
npm run dev
```

---

## 🛠 Tech Stack

- **Edge AI:** Python, ONNX Runtime / TFLite, SQLite, Paho-MQTT
- **Cloud Backend:** Python (FastAPI), PostgreSQL + TimescaleDB, Pydantic
- **Frontend Dashboard:** React, TypeScript, Vite, Charting libraries
- **Message Broker:** Eclipse Mosquitto (MQTT)
- **Containerization:** Docker & Docker Compose

---

## 📄 License

This project is open-source and created for academic research in Edge AI and IoT water quality monitoring.
