"""Shared data models for serial-mqtt-ui."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PortStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


@dataclass
class PortConfig:
    name: str          # e.g. "port1"
    device: str        # e.g. "/dev/ttyUSB0"
    baudrate: int      # e.g. 115200


@dataclass
class SerialMessage:
    port: str          # e.g. "port1"
    direction: str     # "rx" or "tx"
    payload: str


@dataclass
class PortState:
    config: PortConfig
    status: PortStatus = PortStatus.OFFLINE
    last_error: Optional[str] = None
    rx_buffer: list = field(default_factory=list)
