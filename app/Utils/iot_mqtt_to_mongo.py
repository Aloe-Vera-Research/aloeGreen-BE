import os
import ssl
import json
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# ---------------------------
# MongoDB Configuration
# ---------------------------
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "aloeveradb")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]

# Your own separate collection
environmental_logs = db["environmental_logs"]

# Good for faster history queries
environmental_logs.create_index([("device_id", 1), ("timestamp", -1)])

# ---------------------------
# MQTT / HiveMQ Configuration
# ---------------------------
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "aloeGreen/device01/data")

# Keep track of last saved minute per device
last_saved_minute = {}


def build_document(payload: dict, topic: str) -> dict:
    """
    Build one MongoDB document from incoming MQTT payload.
    This supports your AloeGreen IoT setup and 7-in-1 soil sensor fields.
    """
    now = datetime.now(timezone.utc)

    return {
        "device_id": payload.get("device_id", "device01"),
        "topic": topic,
        "timestamp": now,

        # Air / environment
        "air_temperature": payload.get("temp"),
        "air_humidity": payload.get("hum"),
        "light_lux": payload.get("lux"),
        "rainfall": payload.get("rainfall"),

        # Soil / 7-in-1 sensor
        "soil_moisture": payload.get("soil_m"),
        "soil_temperature": payload.get("soil_temp"),
        "soil_ph": payload.get("soil_ph"),
        "soil_ec": payload.get("soil_ec"),

        # NPK
        "nitrogen": payload.get("N"),
        "phosphorus": payload.get("P"),
        "potassium": payload.get("K"),

        # Flags
        "npk_available": payload.get("npk_available", False),
        "dht_available": payload.get("dht_available", False),

        # Raw backup
        "raw_payload": payload,
        "created_at": now,
    }


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to HiveMQ")
        client.subscribe(MQTT_TOPIC)
        print(f"📡 Subscribed to: {MQTT_TOPIC}")
    else:
        print(f"❌ MQTT connection failed with code {rc}")


def on_message(client, userdata, msg):
    global last_saved_minute

    try:
        payload_str = msg.payload.decode("utf-8", errors="ignore")
        payload = json.loads(payload_str)

        device_id = payload.get("device_id", "device01")
        now = datetime.now(timezone.utc)
        minute_key = now.strftime("%Y-%m-%d %H:%M")

        # Save only one document per minute per device
        if last_saved_minute.get(device_id) == minute_key:
            print(f"⏭ Skipped for {device_id} - already saved in minute {minute_key}")
            return

        document = build_document(payload, msg.topic)
        environmental_logs.insert_one(document)

        last_saved_minute[device_id] = minute_key
        print(f"✅ Inserted 1-minute environmental log for {device_id} at {minute_key}")

    except Exception as e:
        print("❌ Error processing MQTT message:", e)


def start_iot_mqtt_logger():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    # HiveMQ Cloud TLS
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    return client


def run_forever():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()


if __name__ == "__main__":
    run_forever()