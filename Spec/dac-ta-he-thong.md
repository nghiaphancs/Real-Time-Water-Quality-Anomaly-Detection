# ĐẶC TẢ HỆ THỐNG
## Edge–Cloud Collaborative Water Quality Monitoring & Early Warning System

**Phiên bản:** 1.0 — MVP
**Ngày:** 22/09/2026
**Phạm vi:** Đặc tả chức năng, phi chức năng, dữ liệu, kiến trúc, giải thuật, tech stack và môi trường triển khai cho hệ thống giám sát chất lượng nước kết hợp Edge AI và Cloud AI.

---

## 1. Tổng quan hệ thống

### 1.1. Mục tiêu
Xây dựng hệ thống giám sát chất lượng nước thời gian thực, trong đó:
- **Edge** phát hiện bất thường (anomaly) nhanh, phản hồi tại chỗ, không phụ thuộc hoàn toàn vào kết nối mạng.
- **Cloud** lưu trữ dữ liệu, tính toán/dự đoán WQI (Water Quality Index), phân tích xu hướng, cung cấp dashboard và gửi cảnh báo đa kênh.

### 1.2. Phạm vi MVP
Trong phạm vi MVP, hệ thống bao gồm:
1. Data Simulator sinh dữ liệu sensor + anomaly có ground truth.
2. MQTT Broker làm tầng truyền dữ liệu Simulator → Edge và Edge → Cloud.
3. Edge Runtime: validate → preprocessing → sliding window → fast detector → deep model → local response.
4. Cloud Backend: ingestion, lưu trữ, WQI calculation/prediction, dashboard API, notification.
5. Web Dashboard hiển thị trạm, telemetry, anomaly events, WQI.

Ngoài phạm vi MVP (để lại giai đoạn sau): OTA model update, quản lý nhiều tenant, mobile app riêng, retraining tự động trên Cloud.

### 1.3. Các actor chính
| Actor | Vai trò |
|---|---|
| Sensor / Simulator | Nguồn dữ liệu chất lượng nước |
| Edge Device | Phát hiện anomaly, phản hồi cục bộ, uplink dữ liệu |
| Cloud Backend | Ingestion, lưu trữ, phân tích WQI |
| Admin/Operator | Cấu hình hệ thống, xem dashboard, xử lý cảnh báo |
| End user (qua Notification) | Nhận cảnh báo Web/Mobile/Email |

---

## 2. Yêu cầu chức năng (Functional Requirements)

### 2.1. Nhóm Data & Simulation
| Mã | Yêu cầu |
|---|---|
| FR-01 | Hệ thống phải sinh được dữ liệu sensor bình thường theo chu kỳ cấu hình được (sampling interval). |
| FR-02 | Hệ thống phải hỗ trợ inject các loại anomaly: point anomaly, drift, noise burst, stuck sensor, missing/intermittent, multivariate. |
| FR-03 | Mỗi bản ghi/anomaly sinh ra phải có ground truth (nhãn) và metadata (loại anomaly, thời điểm bắt đầu/kết thúc, nguồn nhãn). |
| FR-04 | Simulator phải publish dữ liệu qua MQTT theo schema chung (mục 4). |
| FR-05 | Simulator phải có random seed để tái tạo lại cùng kịch bản kiểm thử. |

### 2.2. Nhóm Edge / IoT
| Mã | Yêu cầu |
|---|---|
| FR-06 | Edge phải subscribe dữ liệu sensor qua MQTT và validate schema trước khi xử lý. |
| FR-07 | Edge phải duy trì sliding window theo cấu hình (window size, step size). |
| FR-08 | Edge phải chạy pipeline hai tầng: fast detector (screening) → deep model (xác nhận) khi có nghi ngờ bất thường. |
| FR-09 | Edge phải tính severity (INFO/WARNING/CRITICAL) dựa trên anomaly score, độ tin cậy và thời gian kéo dài (debounce/persistence). |
| FR-10 | Edge phải kích hoạt phản hồi cục bộ (LED/Buzzer) theo policy severity, độc lập với kết nối Cloud. |
| FR-11 | Edge phải publish anomaly event lên Cloud theo event contract (mục 4.2) khi phát hiện bất thường. |
| FR-12 | Edge phải gửi telemetry định kỳ lên Cloud (không chỉ khi có anomaly). |
| FR-13 | Edge phải buffer cục bộ (queue) dữ liệu/event khi mất kết nối, và gửi lại khi kết nối được khôi phục (có giới hạn dung lượng và số lần retry). |
| FR-14 | Edge phải publish trạng thái health định kỳ (CPU, RAM, uptime, connectivity_status). |
| FR-15 (optional) | Edge phải nhận và áp dụng command cấu hình (threshold, model version) từ Cloud, kèm acknowledgment. |

### 2.3. Nhóm Cloud Backend
| Mã | Yêu cầu |
|---|---|
| FR-16 | Cloud phải nhận, validate và lưu trữ telemetry, anomaly event, health status từ Edge. |
| FR-17 | Cloud phải tính WQI theo công thức/phương pháp đã chọn (WQI Calculation) khi dữ liệu đầu vào đủ điều kiện. |
| FR-18 | Cloud phải dự đoán WQI/phân loại chất lượng nước bằng mô hình ML (WQI Prediction) khi dữ liệu đo trực tiếp không đủ. |
| FR-19 | Cloud phải phân biệt rõ `measured_or_calculated_wqi` và `predicted_wqi` kèm `model_version`, `calculation_method`, `prediction_confidence`. |
| FR-20 | Cloud phải cung cấp API cho Dashboard truy vấn: dữ liệu theo trạm, theo thời gian, danh sách anomaly event, chỉ số WQI. |
| FR-21 | Cloud phải hỗ trợ truy vấn dữ liệu trước/sau một anomaly event để phục vụ phân tích. |
| FR-22 | Cloud phải sinh notification event khi có anomaly nghiêm trọng hoặc WQI vượt ngưỡng cảnh báo. |
| FR-23 | Cloud phải gửi thông báo qua ít nhất một kênh (Web/WebSocket bắt buộc cho MVP; Email/mobile push tùy chọn mở rộng). |
| FR-24 | Cloud phải ghi nhận trạng thái gửi (thành công/thất bại) của mỗi notification. |

### 2.4. Nhóm Dashboard
| Mã | Yêu cầu |
|---|---|
| FR-25 | Dashboard phải hiển thị danh sách trạm quan trắc và trạng thái hiện tại (online/offline, WQI mới nhất). |
| FR-26 | Dashboard phải hiển thị biểu đồ telemetry theo thời gian cho từng trạm/feature. |
| FR-27 | Dashboard phải hiển thị danh sách anomaly event kèm severity, thời gian, feature liên quan. |
| FR-28 | Dashboard phải hiển thị WQI (đo/tính và dự đoán) theo thời gian, phân loại chất lượng nước. |
| FR-29 | Dashboard phải cho phép lọc theo trạm, khoảng thời gian, mức độ severity. |

---

## 3. Yêu cầu phi chức năng (Non-Functional Requirements)

| Mã | Nhóm | Yêu cầu |
|---|---|---|
| NFR-01 | Hiệu năng Edge | Fast detector phải xử lý một mẫu dữ liệu trong < 50ms trên thiết bị mục tiêu (ví dụ Raspberry Pi 4). |
| NFR-02 | Hiệu năng Edge | Deep model (khi được kích hoạt) phải hoàn thành inference trong < 300ms. |
| NFR-03 | Hiệu năng Edge | Tổng bộ nhớ tiến trình inference trên Edge không vượt quá giới hạn cấu hình (ví dụ 200MB), phải benchmark và ghi nhận. |
| NFR-04 | Độ trễ | Local alert latency (từ lúc nhận dữ liệu đến khi LED/Buzzer kích hoạt) phải được đo và báo cáo (mục tiêu < 1s). |
| NFR-05 | Độ trễ | End-to-end latency (Edge → Cloud → Notification) phải được đo và báo cáo (mục tiêu < 5s trong điều kiện mạng ổn định). |
| NFR-06 | Độ tin cậy | Hệ thống phải hoạt động độc lập (local response) khi mất kết nối Cloud tối thiểu 10 phút mà không mất dữ liệu quan trọng (nhờ buffer). |
| NFR-07 | Khả năng mở rộng | Cloud backend phải hỗ trợ nhiều trạm/nhiều Edge device đồng thời publish dữ liệu (thiết kế multi-station ngay từ đầu). |
| NFR-08 | Khả năng bảo trì | Schema dữ liệu phải có `schema_version`; thay đổi schema không được phá vỡ pipeline hiện tại (backward-compatible hoặc versioned). |
| NFR-09 | Khả năng quan sát | Toàn bộ pipeline (Edge và Cloud) phải có logging đủ để trace một message từ lúc sinh ra đến khi xử lý xong. |
| NFR-10 | Bảo mật | Kết nối MQTT (ở giai đoạn triển khai) phải hỗ trợ authentication (username/password hoặc TLS certificate); không để broker mở hoàn toàn không xác thực khi ra khỏi môi trường dev. |
| NFR-11 | Bảo mật | Cloud API phải có cơ chế xác thực (API key/JWT) cho các endpoint ghi dữ liệu và endpoint quản trị. |
| NFR-12 | Khả năng đánh giá | Mọi model (fast detector, deep model, WQI predictor) phải được benchmark với F1-score, latency, RAM, CPU, model size — không chỉ dùng Accuracy. |
| NFR-13 | Tính minh bạch dữ liệu | Mọi nhãn ground truth phải ghi rõ `ground_truth_source` (synthetic_rule / domain_verified / teacher_model / unknown). |
| NFR-14 | Khả năng dùng lại | Data contract (schema sensor, event) phải dùng chung giữa Simulator, Edge và Cloud — không được định nghĩa lại ở từng module. |
| NFR-15 | Khả năng phục hồi | Cloud ingestion phải idempotent theo `message_id`/`event_id` để tránh duplicate khi Edge gửi lại dữ liệu buffer. |

---

## 4. Data Contract dùng chung

### 4.1. Sensor Telemetry
```json
{
  "schema_version": "1.0",
  "message_id": "sensor-000001",
  "device_id": "edge-001",
  "station_id": "Ningbo_Station_2",
  "timestamp": "2023-06-01T08:30:00Z",
  "Water_Temperature_C": 22.48,
  "pH": 6.93,
  "Dissolved_Oxygen_mg_L": 9.3,
  "Conductivity_uS_cm": 652.3,
  "Turbidity_NTU": 0.85,
  "Nitrate_mg_L": 2.14,
  "Nitrite_mg_L": 0.03,
  "Ammonia_N_mg_L": 0.38,
  "Total_Phosphorus_mg_L": 0.074,
  "Total_Nitrogen_mg_L": 2.71,
  "COD_mg_L": 15.38,
  "BOD_mg_L": 1.39,
  "Heavy_Metals_Pb_ug_L": 6.9,
  "Heavy_Metals_Cd_ug_L": 0.66,
  "Heavy_Metals_Hg_ug_L": 0.02,
  "Coliform_Count_CFU_100mL": 87
}
```

### 4.2. Anomaly Event
```json
{
  "schema_version": "1.0",
  "event_id": "evt-000001",
  "event_type": "ANOMALY_DETECTED",
  "device_id": "edge-001",
  "station_id": "Ningbo_Station_2",
  "timestamp": "2023-06-01T08:30:05Z",
  "window_start": "2023-06-01T08:29:35Z",
  "window_end": "2023-06-01T08:30:05Z",
  "model_name": "lightweight_gru_ae",
  "model_version": "v1",
  "anomaly_score": 0.91,
  "severity": "WARNING",
  "anomaly_type": "unknown",
  "affected_features": ["Dissolved_Oxygen_mg_L"],
  "local_action": "LED_ON",
  "connectivity_status": "online"
}
```

### 4.3. Health Status
```json
{
  "schema_version": "1.0",
  "device_id": "edge-001",
  "station_id": "Ningbo_Station_2",
  "timestamp": "2023-06-01T08:30:00Z",
  "cpu_usage": 0.42,
  "ram_usage": 0.55,
  "uptime_seconds": 183400,
  "connectivity_status": "online",
  "buffered_messages": 0
}
```

### 4.4. MQTT Topics
| Topic | Hướng | Mục đích |
|---|---|---|
| `water_quality/{station_id}/telemetry` | Simulator → Edge | Dữ liệu sensor |
| `water_quality/{station_id}/anomaly` | Edge → Cloud | Sự kiện anomaly |
| `water_quality/{station_id}/health` | Edge → Cloud | Trạng thái Edge |
| `water_quality/{station_id}/command` | Cloud → Edge | Cấu hình (optional) |
| `water_quality/{station_id}/ack` | Edge → Cloud | Xác nhận xử lý command (optional) |

---

## 5. Thiết kế Database

### 5.1. Edge — lưu trữ cục bộ (SQLite hoặc file-based)
Mục đích: buffer khi mất kết nối, log cục bộ, không cần lưu trữ lâu dài.

**Bảng `local_telemetry_buffer`**
| Field | Type | Ghi chú |
|---|---|---|
| id | INTEGER PK | |
| message_id | TEXT | unique |
| payload_json | TEXT | toàn bộ message |
| created_at | DATETIME | |
| sync_status | TEXT | pending / sent / failed |
| retry_count | INTEGER | |

**Bảng `local_event_log`**
| Field | Type | Ghi chú |
|---|---|---|
| id | INTEGER PK | |
| event_id | TEXT | unique |
| severity | TEXT | |
| payload_json | TEXT | |
| local_action | TEXT | |
| created_at | DATETIME | |
| sync_status | TEXT | |

### 5.2. Cloud — Raw Data Store
Đề xuất dùng time-series-friendly relational DB (PostgreSQL + TimescaleDB extension) hoặc time-series DB (InfluxDB) cho telemetry, và relational DB cho metadata/quan hệ.

**Bảng `stations`**
| Field | Type | Ghi chú |
|---|---|---|
| station_id | TEXT PK | |
| province | TEXT | |
| city | TEXT | |
| name | TEXT | |
| location_lat | FLOAT | |
| location_lng | FLOAT | |
| created_at | TIMESTAMP | |

**Bảng `devices`**
| Field | Type | Ghi chú |
|---|---|---|
| device_id | TEXT PK | |
| station_id | TEXT FK → stations | |
| firmware_version | TEXT | |
| last_seen_at | TIMESTAMP | |
| status | TEXT | online/offline |

**Bảng `telemetry` (time-series, có thể partition theo thời gian)**
| Field | Type | Ghi chú |
|---|---|---|
| message_id | TEXT | unique |
| station_id | TEXT FK | index |
| device_id | TEXT FK | |
| timestamp | TIMESTAMP | index |
| Water_Temperature_C, pH, Dissolved_Oxygen_mg_L, Conductivity_uS_cm, Turbidity_NTU, Nitrate_mg_L, Nitrite_mg_L, Ammonia_N_mg_L, Total_Phosphorus_mg_L, Total_Nitrogen_mg_L, COD_mg_L, BOD_mg_L, Heavy_Metals_Pb_ug_L, Heavy_Metals_Cd_ug_L, Heavy_Metals_Hg_ug_L, Coliform_Count_CFU_100mL | FLOAT | Các thông số từ dataset |
| schema_version | TEXT | |
| ingested_at | TIMESTAMP | |

**Bảng `anomaly_events`**
| Field | Type | Ghi chú |
|---|---|---|
| event_id | TEXT PK | unique |
| station_id | TEXT FK | |
| device_id | TEXT FK | |
| timestamp | TIMESTAMP | |
| window_start / window_end | TIMESTAMP | |
| model_name / model_version | TEXT | |
| anomaly_score | FLOAT | |
| severity | TEXT | |
| anomaly_type | TEXT | |
| affected_features | JSONB | |
| local_action | TEXT | |
| connectivity_status | TEXT | |
| verified_status | TEXT | pending/confirmed_pollution/false_positive/sensor_fault |

**Bảng `wqi_results`**
| Field | Type | Ghi chú |
|---|---|---|
| id | UUID PK | |
| station_id | TEXT FK | |
| timestamp | TIMESTAMP | |
| measured_or_calculated_wqi | FLOAT | nullable |
| predicted_wqi | FLOAT | nullable |
| prediction_confidence | FLOAT | nullable |
| classification | TEXT | Excellent/Good/Poor/... |
| calculation_method | TEXT | |
| model_version | TEXT | nullable |

**Bảng `device_health`**
| Field | Type | Ghi chú |
|---|---|---|
| id | UUID PK | |
| device_id | TEXT FK | |
| timestamp | TIMESTAMP | |
| cpu_usage / ram_usage | FLOAT | |
| uptime_seconds | INTEGER | |
| connectivity_status | TEXT | |
| buffered_messages | INTEGER | |

**Bảng `notifications`**
| Field | Type | Ghi chú |
|---|---|---|
| notification_id | UUID PK | |
| event_id | TEXT FK → anomaly_events (nullable) |
| station_id | TEXT FK | |
| channel | TEXT | web/email/mobile |
| status | TEXT | sent/failed/pending |
| created_at | TIMESTAMP | |
| sent_at | TIMESTAMP | nullable |

**Bảng `model_registry`** (theo dõi phiên bản model đã benchmark/triển khai)
| Field | Type | Ghi chú |
|---|---|---|
| model_id | TEXT PK | |
| model_type | TEXT | fast_detector/deep_model/wqi_predictor |
| version | TEXT | |
| metrics_json | JSONB | F1, latency, RAM, CPU, size |
| deployed | BOOLEAN | |
| created_at | TIMESTAMP | |

---

## 6. Kiến trúc hệ thống

```
[Data Simulator] --MQTT(telemetry)--> [MQTT Broker] --> [Edge Runtime]
                                                            |
                                     Validation -> Preprocessing -> Sliding Window
                                                            |
                                            Fast Detector --(suspicious)--> Deep Model
                                                            |
                                                     Adaptive Threshold
                                                            |
                                         +------------------+------------------+
                                         |                                     |
                                  Local Response                        Event Uplink
                                 (LED / Buzzer)                    (MQTT -> Cloud Ingestion)
                                                                             |
                                                            [Cloud Ingestion & Validation]
                                                                             |
                                                        +--------------------+--------------------+
                                                        |                                         |
                                                 [Raw Data Store]                        [Stream Processor]
                                                        |                                         |
                                                        +------------------+----------------------+
                                                                           |
                                                            [WQI Analytics Service]
                                                    (Calculation | Prediction | Classification)
                                                                           |
                                            +--------------------+---------+---------+
                                            |                    |                   |
                                     [Dashboard API]     [Notification Service]  [Model Registry]
                                            |                    |
                                      [Web Dashboard]   [Web / Email / Mobile]
```

**Nguyên tắc kiến trúc:**
- Edge chỉ chịu trách nhiệm phát hiện bất thường + phản hồi tức thời; không tính WQI.
- Cloud chịu trách nhiệm xác minh, phân tích chuyên sâu, lưu trữ dài hạn, giao diện.
- Hai luồng dữ liệu độc lập nhưng bổ sung: Fast Path (cảnh báo) và Analytics Path (phân tích).
- Toàn bộ giao tiếp giữa các tầng đi qua data contract đã chuẩn hóa (mục 4).

---

## 7. Giải thuật đề xuất cho MVP

### 7.1. Edge — Anomaly Detection (kiến trúc hai tầng)

**Tầng 1 — Fast Detector (screening, chạy trên mọi sample)**
- Ứng viên: Isolation Forest (huấn luyện offline trên dữ liệu normal), hoặc statistical screening (z-score/EWMA theo từng feature trên sliding window).
- Input: vector feature hiện tại + thống kê window (mean, std, rate of change).
- Output: điểm bất thường sơ bộ (0–1) + cờ "suspicious" nếu vượt ngưỡng sơ bộ.
- Mục tiêu: chi phí tính toán cực thấp, chạy real-time trên mọi mẫu.

**Tầng 2 — Deep Model (chỉ chạy khi Tầng 1 gắn cờ suspicious)**
- Ứng viên chính: Lightweight GRU Autoencoder (GRU-AE).
  - Huấn luyện tái tạo (reconstruction) trên dữ liệu bình thường.
  - Anomaly score = reconstruction error trên cửa sổ thời gian gần nhất.
- Ứng viên đối chứng (benchmark, chưa kết luận tối ưu): Lightweight Transformer/Autoencoder biến thể nhẹ, để so sánh F1/latency/kích thước với GRU-AE.

**Adaptive Threshold**
- Không dùng ngưỡng cố định toàn cục.
- Ngưỡng theo từng trạm/feature, cập nhật theo thống kê rolling (ví dụ: mean + k·std trên cửa sổ trượt dài hạn, hoặc percentile động).
- Kết hợp với persistence/debounce: chỉ nâng severity khi anomaly lặp lại/kéo dài qua N cửa sổ liên tiếp, để giảm false positive.

**Severity Policy (pseudocode)**
```
if anomaly_score < threshold_info: severity = NONE
elif anomaly_score >= threshold_info and duration < persist_window: severity = INFO
elif anomaly_score >= threshold_warning and duration >= persist_window: severity = WARNING
elif anomaly_score >= threshold_critical: severity = CRITICAL
```

### 7.2. Cloud — WQI Calculation
- Áp dụng công thức WQI chuẩn (ví dụ NSF-WQI hoặc phương pháp được GVHD/đề tài chỉ định) trên các thông số đo được (pH, Dissolved_Oxygen_mg_L, Turbidity_NTU, Conductivity_uS_cm, Water_Temperature_C...).
- Bước xử lý: kiểm tra đầy đủ tham số bắt buộc → chuẩn hóa (sub-index) từng tham số theo bảng tra/hàm chuẩn → tổng hợp trọng số → WQI.
- Lưu kèm `calculation_method` và phiên bản công thức để có thể tái tính khi thay đổi phương pháp.

### 7.3. Cloud — WQI Prediction
- Hướng kết hợp Classification + Regression:
  - Classification: phân loại nhanh mức chất lượng nước (Excellent/Good/Poor/Very Poor...) khi thiếu tham số để tính WQI đầy đủ.
  - Regression: ước lượng giá trị WQI liên tục từ tập feature sẵn có (kể cả khi thiếu một số thông số).
- Model ứng viên: Gradient Boosting (XGBoost/LightGBM) làm baseline do hiệu quả với dữ liệu dạng bảng và hỗ trợ SHAP tốt; có thể benchmark thêm MLP nhỏ.
- Explainability: dùng SHAP để giải thích đóng góp từng feature vào kết quả dự đoán, phục vụ hiển thị trên dashboard.
- Luôn trả về `prediction_confidence` và không hiển thị predicted_wqi như số đo thực tế.

### 7.4. Benchmark bắt buộc trước khi chọn model production
Với mỗi ứng viên (fast detector, deep model, WQI predictor), đo và ghi nhận:
- F1-score (và Precision/Recall riêng theo severity nếu có thể).
- Latency inference (ms).
- RAM/CPU sử dụng khi chạy trên thiết bị Edge mục tiêu.
- Kích thước model (MB).
Kết quả lưu vào `model_registry` để tra cứu và quyết định version triển khai.

---

## 8. Tech Stack đề xuất

| Thành phần | Công nghệ đề xuất | Ghi chú |
|---|---|---|
| Data Simulator | Python (NumPy, Pandas) | Sinh dữ liệu + inject anomaly |
| Message Broker | Eclipse Mosquitto (dev) | TLS/auth khi triển khai thật |
| Edge Runtime | Python (paho-mqtt, onnxruntime hoặc tflite-runtime) | Ưu tiên inference nhẹ, export model sang ONNX/TFLite |
| Edge ML Framework (huấn luyện) | scikit-learn (Isolation Forest), PyTorch (GRU-AE) | Convert sang ONNX/TFLite để deploy |
| Edge local storage | SQLite | Buffer khi mất kết nối |
| Cloud Backend / API | Python (FastAPI) hoặc Node.js (NestJS) | REST + WebSocket cho realtime dashboard |
| Cloud Message Ingestion | MQTT consumer (paho-mqtt) hoặc Kafka nếu cần mở rộng lớn | MVP dùng MQTT consumer trực tiếp là đủ |
| Raw Data Store | PostgreSQL + TimescaleDB | Time-series + relational trong cùng hệ quản trị |
| WQI ML Service | Python (XGBoost/LightGBM, SHAP) | Tách microservice hoặc module riêng trong backend |
| Dashboard Frontend | React (Vite) + charting (Recharts/Chart.js) | Kết nối WebSocket/SSE cho cập nhật realtime |
| Notification Service | Cloud backend module + SMTP (email), Web Push/WebSocket | Mobile push để lại giai đoạn mở rộng |
| Containerization | Docker, Docker Compose | Chuẩn hóa môi trường dev/staging |
| Model tracking | MLflow (tuỳ chọn) hoặc bảng `model_registry` tự quản lý | Ghi lại metrics benchmark |
| CI/CD (tuỳ chọn) | GitHub Actions | Test + build image tự động |

---

## 9. Môi trường triển khai

### 9.1. Môi trường phát triển (Development)
- Máy chủ MQTT Broker (Mosquitto) chạy local hoặc trên 1 VM Ubuntu.
- Edge Runtime chạy giả lập trên máy dev hoặc trực tiếp trên Raspberry Pi 4 (khuyến nghị RAM ≥ 4GB) để đo benchmark thực tế.
- Cloud Backend + PostgreSQL/TimescaleDB chạy qua Docker Compose trên máy dev hoặc VM.
- Dashboard chạy dev server (Vite) kết nối trực tiếp Cloud API local.

### 9.2. Môi trường staging/triển khai thử
- Cloud Backend + DB triển khai trên VM/Cloud VPS (ví dụ Ubuntu Server), có thể dùng Docker Compose hoặc container orchestration đơn giản.
- MQTT Broker bật authentication (username/password tối thiểu, khuyến nghị TLS).
- Edge Device thực tế (Raspberry Pi) kết nối qua Wi-Fi/Ethernet tới broker qua Internet hoặc VPN nội bộ.
- Cấu hình biến môi trường riêng (`.env`) cho từng môi trường: broker URL, DB connection string, API keys.

### 9.3. Yêu cầu phần cứng tối thiểu (tham khảo)
| Thành phần | Cấu hình tối thiểu |
|---|---|
| Edge Device | Raspberry Pi 4 (4GB RAM), thẻ nhớ ≥ 16GB |
| Cloud Backend VM | 2 vCPU, 4GB RAM, 40GB disk (MVP quy mô nhỏ) |
| MQTT Broker | Có thể chạy chung VM với Cloud Backend ở MVP |

### 9.4. Cấu hình bảo mật tối thiểu khi ra khỏi môi trường dev
- MQTT: bật authentication, khuyến nghị TLS.
- Cloud API: JWT hoặc API key cho endpoint ghi dữ liệu/quản trị.
- Biến nhạy cảm (mật khẩu, secret key) không hardcode, quản lý qua biến môi trường hoặc secret manager.

---

## 10. Ghi chú triển khai

- **Xử lý dữ liệu thời gian:** Dataset hiện tại (`china_water_pollution_data.csv`) chỉ có cột `Date` mà không có `Time`. Data Simulator cần nội suy (interpolate) thời gian hoặc giả định mỗi dòng dữ liệu tương ứng với một khoảng thời gian (ví dụ 1 giờ/1 phút) để có thể tạo ra luồng dữ liệu time-series liên tục phục vụ cho việc tính toán sliding window trên Edge.
- Các điểm bắt buộc chốt trước khi code: sampling interval thực tế của dataset GVHD, danh sách feature chính thức, ngưỡng threshold ban đầu (sẽ hiệu chỉnh qua benchmark), công thức WQI được chọn.
- MVP ưu tiên hoàn thành một vòng đời end-to-end (Simulator → Edge → Cloud → Dashboard → Notification) trước khi tối ưu sâu từng thành phần.
- Mọi ngưỡng, model version, phương pháp tính đều phải được version hóa và log lại để đảm bảo khả năng truy vết (traceability) và đánh giá lại sau này.
