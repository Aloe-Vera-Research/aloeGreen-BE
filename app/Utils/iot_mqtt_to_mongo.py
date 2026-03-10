import os
import ssl
import json
import threading
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# -----------------------------
# ENV
# -----------------------------
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "aloeveradb")

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "aloeGreen/device01/data")

COLLECTION_NAME = "iot_minute_records"

if not MONGO_URI:
    raise ValueError("MONGO_URI is missing in .env")
if not MQTT_BROKER:
    raise ValueError("MQTT_BROKER is missing in .env")
if not MQTT_USERNAME:
    raise ValueError("MQTT_USERNAME is missing in .env")
if not MQTT_PASSWORD:
    raise ValueError("MQTT_PASSWORD is missing in .env")

# -----------------------------
# MongoDB
# -----------------------------
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

# -----------------------------
# Shared state
# -----------------------------
latest_payload = None
latest_payload_lock = threading.Lock()


def calculate_soil_moisture_percent(raw_value):
    """
    Convert ESP32 ADC raw value to approximate %.
    Adjust calibration later based on your actual sensor.
    """
    try:
        raw = float(raw_value)
        percent = ((4095.0 - raw) / 4095.0) * 100.0
        return max(0.0, min(100.0, percent))
    except Exception:
        return None


def normalize_payload(payload: dict) -> dict:
    """
    Normalize ESP32 MQTT payload before saving to MongoDB.
    """
    soil_raw = payload.get("soil_moisture_raw")
    now = datetime.now(timezone.utc)

    return {
        "device_id": payload.get("device_id", "device01"),
        "temperature_c": payload.get("temperature_c"),
        "humidity_pct": payload.get("humidity_pct"),
        "light_lux": payload.get("light_lux"),
        "rainfall_mm": payload.get("rainfall_mm"),
        "soil_moisture_raw": soil_raw,
        "soil_moisture_pct": calculate_soil_moisture_percent(soil_raw),
        "soil_ph": payload.get("soil_ph"),
        "soil_ec": payload.get("soil_ec"),
        "nitrogen": payload.get("nitrogen"),
        "phosphorus": payload.get("phosphorus"),
        "potassium": payload.get("potassium"),
        "dht_ok": payload.get("dht_ok"),
        "light_ok": payload.get("light_ok"),
        "modbus_ok": payload.get("modbus_ok"),
        "wifi_rssi": payload.get("wifi_rssi"),
        "uptime_ms": payload.get("uptime_ms"),
        "mqtt_topic": MQTT_TOPIC,
        "saved_at": now,
        "saved_at_iso": now.isoformat(),
    }


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to HiveMQ successfully")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect to HiveMQ, rc={rc}")


def on_message(client, userdata, msg):
    global latest_payload

    try:
        raw = msg.payload.decode("utf-8")
        parsed = json.loads(raw)

        normalized = normalize_payload(parsed)

        with latest_payload_lock:
            latest_payload = normalized

        print("MQTT message received:")
        print(normalized)

    except Exception as e:
        print("Error processing MQTT message:", e)


def write_latest_payload_every_minute():
    """
    Save only one record per minute.
    It inserts the most recent payload seen in that minute window.
    """
    global latest_payload

    while True:
        time.sleep(60)

        with latest_payload_lock:
            if latest_payload is None:
                print("No MQTT payload received yet. Skipping insert.")
                continue

            document = dict(latest_payload)

        try:
            result = collection.insert_one(document)
            print(f"Inserted 1-minute record: {result.inserted_id}")
        except Exception as e:
            print("MongoDB insert failed:", e)


def ensure_indexes():
    try:
        collection.create_index("saved_at")
        collection.create_index("device_id")
        print("MongoDB indexes ensured")
    except Exception as e:
        print("Index creation failed:", e)


def start_mqtt_to_mongo_worker():
    ensure_indexes()

    writer_thread = threading.Thread(
        target=write_latest_payload_every_minute,
        daemon=True
    )
    writer_thread.start()

    client = mqtt.Client()

    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)
    client.tls_insecure_set(False)

    client.on_connect = on_connect
    client.on_message = on_message

    print("Connecting to HiveMQ broker...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    return client