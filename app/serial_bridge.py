"""Serial bridge: manages three serial ports and routes data to/from MQTT."""

import logging
import threading

import serial

import app.config as cfg
import app.mqtt_bridge as mqtt_bridge
from app.models import PortConfig, PortState, PortStatus

logger = logging.getLogger(__name__)

_states: dict[str, PortState] = {}
_stop_events: dict[str, threading.Event] = {}


def _rx_topic(port_name: str) -> str:
    return f"{cfg.TOPIC_PREFIX}/{port_name}/rx"


def _tx_topic(port_name: str) -> str:
    return f"{cfg.TOPIC_PREFIX}/{port_name}/tx"


def _status_topic(port_name: str) -> str:
    return f"{cfg.TOPIC_PREFIX}/{port_name}/status"


def _read_loop(state: PortState, ser: serial.Serial, stop: threading.Event) -> None:
    """Continuously read from a serial port and publish to MQTT."""
    while not stop.is_set():
        try:
            line = ser.readline().decode(errors="replace").strip()
            if line:
                topic = _rx_topic(state.config.name)
                mqtt_bridge.publish(topic, line)
                state.rx_buffer.append(line)
        except serial.SerialException as exc:
            logger.error("Serial error on %s: %s", state.config.device, exc)
            state.status = PortStatus.ERROR
            state.last_error = str(exc)
            mqtt_bridge.publish(_status_topic(state.config.name), PortStatus.ERROR.value)
            break


def _open_port(port_cfg: PortConfig) -> None:
    state = PortState(config=port_cfg)
    _states[port_cfg.name] = state

    stop = threading.Event()
    _stop_events[port_cfg.name] = stop

    try:
        ser = serial.Serial(port_cfg.device, port_cfg.baudrate, timeout=1)
        state.status = PortStatus.ONLINE
        mqtt_bridge.publish(_status_topic(port_cfg.name), PortStatus.ONLINE.value)
        logger.info("Opened serial port %s at %d baud", port_cfg.device, port_cfg.baudrate)
    except serial.SerialException as exc:
        logger.error("Cannot open %s: %s", port_cfg.device, exc)
        state.status = PortStatus.ERROR
        state.last_error = str(exc)
        mqtt_bridge.publish(_status_topic(port_cfg.name), PortStatus.ERROR.value)
        return

    # Subscribe to TX topic so incoming MQTT commands are forwarded to the port
    def _on_tx(topic: str, payload: str) -> None:
        try:
            ser.write((payload + "\n").encode())
        except serial.SerialException as exc:
            logger.error("Write error on %s: %s", port_cfg.device, exc)

    mqtt_bridge.subscribe(_tx_topic(port_cfg.name), _on_tx)

    # Start RX reader in a daemon thread
    t = threading.Thread(target=_read_loop, args=(state, ser, stop), daemon=True)
    t.start()


def start() -> None:
    """Open all configured serial ports."""
    for port_cfg in cfg.PORTS:
        _open_port(port_cfg)
    logger.info("Serial bridge started (%d ports)", len(cfg.PORTS))


def stop() -> None:
    """Signal all RX threads to exit."""
    for event in _stop_events.values():
        event.set()
    logger.info("Serial bridge stopped")


def get_states() -> dict[str, PortState]:
    """Return current state of all ports (read-only snapshot for UI)."""
    return dict(_states)
