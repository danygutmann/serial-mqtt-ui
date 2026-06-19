"""MQTT bridge: connects to the broker and routes messages between serial and UI."""

import logging
import threading
from typing import Callable

import paho.mqtt.client as mqtt

import app.config as cfg

logger = logging.getLogger(__name__)

# Callbacks registered by other modules: topic -> handler(topic, payload)
_subscribers: dict[str, list[Callable[[str, str], None]]] = {}
_client: mqtt.Client | None = None
_lock = threading.Lock()


def subscribe(topic: str, handler: Callable[[str, str], None]) -> None:
    """Register a handler for the given MQTT topic (supports wildcards)."""
    with _lock:
        _subscribers.setdefault(topic, []).append(handler)
        if _client and _client.is_connected():
            _client.subscribe(topic)


def publish(topic: str, payload: str) -> None:
    """Publish a message to the broker."""
    if _client:
        _client.publish(topic, payload)
    else:
        logger.warning("MQTT client not ready, dropping message to %s", topic)


def _on_connect(client: mqtt.Client, userdata, flags, rc) -> None:
    if rc == 0:
        logger.info("Connected to MQTT broker at %s:%s", cfg.MQTT_HOST, cfg.MQTT_PORT)
        with _lock:
            for topic in _subscribers:
                client.subscribe(topic)
    else:
        logger.error("MQTT connection failed with code %d", rc)


def _on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
    topic = msg.topic
    payload = msg.payload.decode(errors="replace")
    with _lock:
        matched_handlers: list[Callable[[str, str], None]] = []
        for pattern, hlist in _subscribers.items():
            if mqtt.topic_matches_sub(pattern, topic):
                matched_handlers.extend(hlist)
    for handler in matched_handlers:
        try:
            handler(topic, payload)
        except Exception:
            logger.exception("Error in MQTT handler for topic %s", topic)


def start() -> None:
    """Connect to the MQTT broker and start the network loop in a background thread."""
    global _client
    _client = mqtt.Client()
    if cfg.MQTT_USERNAME:
        _client.username_pw_set(cfg.MQTT_USERNAME, cfg.MQTT_PASSWORD)
    _client.on_connect = _on_connect
    _client.on_message = _on_message
    _client.connect(cfg.MQTT_HOST, cfg.MQTT_PORT, keepalive=60)
    _client.loop_start()
    logger.info("MQTT bridge started")
