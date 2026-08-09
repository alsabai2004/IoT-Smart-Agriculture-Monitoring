"""
Smart Agriculture Monitoring - MQTT Gateway

The gateway performs four tasks:
1) Receives raw MQTT sensor messages.
2) Validates JSON structure and data types.
3) Adds a UTC timestamp and evaluates alert rules.
4) Publishes processed data to a second MQTT topic.
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from typing import Any

try:
    import paho.mqtt.client as mqtt
except ImportError as exc:  # pragma: no cover - runtime dependency check
    raise SystemExit(
        "Missing dependency: paho-mqtt. Install it with: pip install -r requirements.txt"
    ) from exc

DEFAULT_BROKER = "broker.hivemq.com"
DEFAULT_PORT = 1883
DEFAULT_RAW_TOPIC = "iot/project/groupX/agriculture/raw"
DEFAULT_PROCESSED_TOPIC = "iot/project/groupX/agriculture/processed"
REQUIRED_FIELDS = {"device_id", "temperature", "humidity", "status"}


def is_number(value: Any) -> bool:
    """Return True for int/float values, but not for booleans."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_sensor_message(data: Any) -> tuple[bool, str]:
    """Validate the JSON object expected from the publisher."""
    if not isinstance(data, dict):
        return False, "JSON payload must be an object."

    missing = REQUIRED_FIELDS.difference(data.keys())
    if missing:
        return False, f"Missing fields: {', '.join(sorted(missing))}"

    if not isinstance(data["device_id"], str) or not data["device_id"].strip():
        return False, "device_id must be a non-empty string."
    if not is_number(data["temperature"]):
        return False, "temperature must be numeric."
    if not is_number(data["humidity"]):
        return False, "humidity must be numeric."
    if not 0 <= float(data["humidity"]) <= 100:
        return False, "humidity must be between 0 and 100."
    if not isinstance(data["status"], str):
        return False, "status must be a string."

    return True, "VALID"


def evaluate_status(temperature: float, humidity: float) -> tuple[str, str]:
    """
    Apply decision logic.

    Mandatory alert logic is implemented with multiple rules:
    - Rule 1: High temperature >= 32 C -> ALERT
    - Rule 2: High humidity >= 80% -> ALERT
    - Rule 3: Moderate heat >= 29 C or low humidity <= 35% -> WARNING
    """
    reasons: list[str] = []

    if temperature >= 32:
        reasons.append("High temperature")
    if humidity >= 80:
        reasons.append("High humidity")

    if reasons:
        return "ALERT", " + ".join(reasons)

    if temperature >= 29:
        reasons.append("Temperature above comfort range")
    if humidity <= 35:
        reasons.append("Low humidity")

    if reasons:
        return "WARNING", " + ".join(reasons)

    return "NORMAL", "Readings are within normal range"


def process_payload(raw_payload: bytes) -> dict[str, Any] | None:
    """Parse, validate, enrich, and classify one raw MQTT payload."""
    try:
        decoded = raw_payload.decode("utf-8")
        data = json.loads(decoded)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"[GATEWAY] Invalid JSON message rejected: {exc}")
        return None

    valid, message = validate_sensor_message(data)
    if not valid:
        print(f"[GATEWAY] Validation failed: {message}")
        return None

    temperature = float(data["temperature"])
    humidity = float(data["humidity"])
    status, alert_reason = evaluate_status(temperature, humidity)

    data["temperature"] = temperature
    data["humidity"] = humidity
    data["status"] = status
    data["alert_reason"] = alert_reason
    data["gateway_timestamp_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    data["gateway_id"] = "groupX_gateway_01"
    return data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MQTT gateway for Smart Agriculture Monitoring")
    parser.add_argument("--broker", default=DEFAULT_BROKER, help="MQTT broker hostname")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="MQTT broker port")
    parser.add_argument("--raw-topic", default=DEFAULT_RAW_TOPIC, help="Input topic from publisher")
    parser.add_argument(
        "--processed-topic",
        default=DEFAULT_PROCESSED_TOPIC,
        help="Output topic for processed messages",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    client_id = f"gateway_groupX_{random.randint(1000, 9999)}"
    client = mqtt.Client(client_id=client_id)

    def on_connect(client_obj: mqtt.Client, userdata: Any, flags: Any, rc: int) -> None:
        if rc == 0:
            print(f"[GATEWAY] Connected to {args.broker}:{args.port}")
            print(f"[GATEWAY] Subscribing to raw topic: {args.raw_topic}")
            client_obj.subscribe(args.raw_topic, qos=0)
        else:
            print(f"[GATEWAY] Connection failed with code {rc}")

    def on_message(client_obj: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        processed = process_payload(msg.payload)
        if processed is None:
            return

        payload = json.dumps(processed, ensure_ascii=False)
        client_obj.publish(args.processed_topic, payload, qos=0, retain=False)
        print(f"[GATEWAY] Processed -> {payload}")

    client.on_connect = on_connect
    client.on_message = on_message

    print("[GATEWAY] Connecting to MQTT broker...")
    client.connect(args.broker, args.port, keepalive=60)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[GATEWAY] Stopped by user.")
    finally:
        client.disconnect()
        print("[GATEWAY] Disconnected.")


if __name__ == "__main__":
    main()
