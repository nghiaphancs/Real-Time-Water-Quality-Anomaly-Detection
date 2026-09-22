import time
import json
import pandas as pd
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
DATASET_PATH = "../Dataset/china_water_pollution_data.csv"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

def run_simulator():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "simulator-001")
    client.on_connect = on_connect
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except ConnectionRefusedError:
        print(f"Cannot connect to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        return

    client.loop_start()

    try:
        df = pd.read_csv(DATASET_PATH)
        print(f"Loaded {len(df)} records from dataset.")
        
        for index, row in df.iterrows():
            station_id = row['Monitoring_Station']
            topic = f"water_quality/{station_id}/telemetry"
            
            # Simple payload format matching the spec
            payload = {
                "schema_version": "1.0",
                "message_id": f"msg-{index}",
                "device_id": "sim-device-01",
                "station_id": station_id,
                "timestamp": f"{row['Date']}T12:00:00Z", # Mock time
                "Water_Temperature_C": row['Water_Temperature_C'],
                "pH": row['pH'],
                "Dissolved_Oxygen_mg_L": row['Dissolved_Oxygen_mg_L'],
                "Conductivity_uS_cm": row['Conductivity_uS_cm'],
                "Turbidity_NTU": row['Turbidity_NTU'],
                # Add other fields here based on the schema...
            }
            
            payload_json = json.dumps(payload)
            print(f"Publishing to {topic}: {payload_json}")
            client.publish(topic, payload_json)
            
            time.sleep(1) # Wait 1 second between publishes (simulation interval)
            
    except FileNotFoundError:
        print(f"Dataset not found at {DATASET_PATH}")
    except KeyboardInterrupt:
        print("Simulator stopped by user.")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    run_simulator()
