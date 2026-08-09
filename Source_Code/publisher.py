"""
Smart Agriculture Monitoring - MQTT Publisher

This script simulates two virtual sensors:
1) Temperature sensor
2) Humidity sensor

It sends JSON messages every 2-3 seconds to a public MQTT broker.
"""

from __future__ import annotations

import argparse
import json
import random
import time
from datetime import datetime, timezone

try:
    import paho.mqtt.client as mqtt
except ImportError as exc:  # pragma: no cover - runtime dependency check
    raise SystemExit(
        "Missing dependency: paho-mqtt. Install it with: pip install -r requirements.txt"
    ) from exc

DEFAULT_BROKER = "broker.hivemq.com"
DEFAULT_PORT = 1883
DEFAULT_TOPIC = "iot/project/groupX/agriculture/raw"
DEFAULT_DEVICE_ID = "groupX_agri_node_01"


def create_payload(device_id: str) -> dict[str, object]:
    """Create one valid JSON-ready payload for the virtual sensor node."""
    temperature = round(random.uniform(18.0, 40.0), 2)
    humidity = random.randint(25, 90)

    return {
        "device_id": device_id,
        "temperature": temperature,
        "humidity": humidity,
        # The gateway will evaluate the final condition and replace this status.
        "status": "RAW",
        "publisher_time_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Virtual agriculture MQTT publisher")
    parser.add_argument("--broker", default=DEFAULT_BROKER, help="MQTT broker hostname")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="MQTT broker port")
    parser.add_argument("--topic", default=DEFAULT_TOPIC, help="MQTT topic for raw sensor data")
    parser.add_argument("--device-id", default=DEFAULT_DEVICE_ID, help="Virtual device identifier")
    parser.add_argument(
        "--count",
        type=int,
        default=0,
        help="Number of messages to publish. 0 means run continuously.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    client_id = f"publisher_{args.device_id}_{random.randint(1000, 9999)}"
    client = mqtt.Client(client_id=client_id)

    print("[PUBLISHER] Connecting to MQTT broker...")
    client.connect(args.broker, args.port, keepalive=60)
    client.loop_start()
    print(f"[PUBLISHER] Connected to {args.broker}:{args.port}")
    print(f"[PUBLISHER] Topic: {args.topic}")
    print(f"[PUBLISHER] Device ID: {args.device_id}")

    published = 0
    try:
        while True:
            payload = create_payload(args.device_id)
            json_payload = json.dumps(payload, ensure_ascii=False)
            result = client.publish(args.topic, json_payload, qos=0, retain=False)
            result.wait_for_publish()
            print(f"[PUBLISHER] Sent -> {json_payload}")

            published += 1
            if args.count and published >= args.count:
                break

            # Requirement: publish every 2-3 seconds.
            time.sleep(random.uniform(2.0, 3.0))
    except KeyboardInterrupt:
        print("\n[PUBLISHER] Stopped by user.")
    finally:
        client.loop_stop()
        client.disconnect()
        print("[PUBLISHER] Disconnected.")


if __name__ == "__main__":
    main()
