"""Load configuration from environment variables with sensible defaults."""

import os
from app.models import PortConfig


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def _int_env(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, default))
    except (TypeError, ValueError):
        return default


# MQTT
MQTT_HOST: str = _env("MQTT_HOST", "localhost")
MQTT_PORT: int = _int_env("MQTT_PORT", 1883)
MQTT_USERNAME: str = _env("MQTT_USERNAME", "")
MQTT_PASSWORD: str = _env("MQTT_PASSWORD", "")

# Topic namespace
TOPIC_PREFIX: str = _env("TOPIC_PREFIX", "serial")

# Serial ports
PORTS: list[PortConfig] = [
    PortConfig(
        name=f"port{i}",
        device=_env(f"SERIAL_PORT_{i}", f"/dev/ttyUSB{i - 1}"),
        baudrate=_int_env(f"SERIAL_BAUDRATE_{i}", 115200),
    )
    for i in range(1, 4)
]

# NiceGUI
UI_HOST: str = _env("UI_HOST", "0.0.0.0")
UI_PORT: int = _int_env("UI_PORT", 8080)
