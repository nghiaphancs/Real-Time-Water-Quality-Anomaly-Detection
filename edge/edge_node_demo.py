import json
import sqlite3
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
STATION_ID = "Ningbo_Station_2"
TELEMETRY_TOPIC = f"water_quality/{STATION_ID}/telemetry"
ANOMALY_TOPIC = f"water_quality/{STATION_ID}/anomaly"

# Initialize SQLite local buffer
conn = sqlite3.connect('local_buffer.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS local_telemetry_buffer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id TEXT UNIQUE,
        payload_json TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        sync_status TEXT DEFAULT 'pending',
        retry_count INTEGER DEFAULT 0
    )
''')
conn.commit()

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Edge Node Connected to MQTT Broker!")
        client.subscribe(TELEMETRY_TOPIC)
        print(f"Subscribed to {TELEMETRY_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Received message on {msg.topic}: {payload}")
    
    # Parse JSON
    try:
        data = json.loads(payload)
        
        # 1. Validation -> Preprocessing
        # 2. Sliding Window (buffer locally)
        # 3. Fast Detector -> Deep Model
        # 4. Local Response
        # 5. Cloud Uplink (Publish to Anomaly topic if anomalous)
        
        # Example of buffering locally
        cursor.execute("INSERT INTO local_telemetry_buffer (message_id, payload_json) VALUES (?, ?)", 
                       (data.get("message_id", "unknown"), payload))
        conn.commit()
        
    except json.JSONDecodeError:
        print("Invalid JSON received")
    except sqlite3.IntegrityError:
        print("Message ID already exists in buffer")

def run_edge_node():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "edge-node-001")
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except ConnectionRefusedError:
        print(f"Cannot connect to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_edge_node()
