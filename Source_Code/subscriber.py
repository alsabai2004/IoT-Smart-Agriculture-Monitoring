"""
Smart Agriculture Monitoring - MQTT Subscriber

This script listens to processed gateway output and prints real-time monitoring data.
"""

from __future__ import annotations

import argparse
import json
import random
from typing import Any

try:
    import paho.mqtt.client as mqtt
except ImportError as exc:  # pragma: no cover - runtime dependency check
    raise SystemExit(
        "Missing dependency: paho-mqtt. Install it with: pip install -r requirements.txt"
    ) from exc

DEFAULT_BROKER = "broker.hivemq.com"
DEFAULT_PORT = 1883
DEFAULT_TOPIC = "iot/project/groupX/agriculture/processed"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Real-time MQTT subscriber for processed IoT data")
    parser.add_argument("--broker", default=DEFAULT_BROKER, help="MQTT broker hostname")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="MQTT broker port")
    parser.add_argument("--topic", default=DEFAULT_TOPIC, help="Processed MQTT topic")
    return parser


def format_message(data: dict[str, Any]) -> str:
    """Create a readable real-time monitoring line."""
    status = data.get("status", "UNKNOWN")
    prefix = {
        "NORMAL": "[NORMAL]",
        "WARNING": "[WARNING]",
        "ALERT": "[ALERT]",
    }.get(status, "[UNKNOWN]")

    return (
        f"{prefix} device={data.get('device_id')} | "
        f"temp={data.get('temperature')} C | humidity={data.get('humidity')}% | "
        f"reason={data.get('alert_reason')} | time={data.get('gateway_timestamp_utc')}"
    )


def main() -> None:
    args = build_parser().parse_args()
    client_id = f"subscriber_groupX_{random.randint(1000, 9999)}"
    client = mqtt.Client(client_id=client_id)

    def on_connect(client_obj: mqtt.Client, userdata: Any, flags: Any, rc: int) -> None:
        if rc == 0:
            print(f"[SUBSCRIBER] Connected to {args.broker}:{args.port}")
            print(f"[SUBSCRIBER] Listening to processed topic: {args.topic}")
            client_obj.subscribe(args.topic, qos=0)
        else:
            print(f"[SUBSCRIBER] Connection failed with code {rc}")

    def on_message(client_obj: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        try:
            data = json.loads(msg.payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"[SUBSCRIBER] Invalid processed message: {exc}")
            return

        if isinstance(data, dict):
            print(format_message(data))
        else:
            print("[SUBSCRIBER] Ignored non-object JSON payload.")

    client.on_connect = on_connect
    client.on_message = on_message

    print("[SUBSCRIBER] Connecting to MQTT broker...")
    client.connect(args.broker, args.port, keepalive=60)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[SUBSCRIBER] Stopped by user.")
    finally:
        client.disconnect()
        print("[SUBSCRIBER] Disconnected.")


if __name__ == "__main__":
    main()
