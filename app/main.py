"""Entry point for serial-mqtt-ui."""

import logging

from nicegui import app as nicegui_app, ui

import app.config as cfg
import app.mqtt_bridge as mqtt_bridge
import app.serial_bridge as serial_bridge
import app.ui as ui_module

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@nicegui_app.on_startup
def on_startup() -> None:
    logger.info("Starting MQTT bridge…")
    mqtt_bridge.start()
    logger.info("Starting serial bridge…")
    serial_bridge.start()


@ui.page("/")
def index() -> None:
    ui_module.build()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(host=cfg.UI_HOST, port=cfg.UI_PORT, title="serial-mqtt-ui", reload=False)
