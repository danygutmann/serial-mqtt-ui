"""NiceGUI web interface: one terminal per serial port."""

from nicegui import ui

import app.config as cfg
import app.mqtt_bridge as mqtt_bridge
import app.serial_bridge as serial_bridge


def _build_port_card(port_name: str, device: str) -> None:
    """Create a card with a read-only terminal log and a send input."""
    with ui.card().classes("w-full"):
        ui.label(f"{port_name}  ({device})").classes("font-bold")
        log = ui.log(max_lines=200).classes("w-full h-48 font-mono text-sm")
        with ui.row().classes("w-full gap-2"):
            cmd_input = ui.input(placeholder="send command…").classes("flex-1")
            send_btn = ui.button("Send")

        tx_topic = f"{cfg.TOPIC_PREFIX}/{port_name}/tx"
        status_label = ui.label("● offline").classes("text-xs text-gray-500")

        # Forward new MQTT RX messages to the log
        rx_topic = f"{cfg.TOPIC_PREFIX}/{port_name}/rx"

        def _on_rx(topic: str, payload: str) -> None:
            log.push(f"← {payload}")

        mqtt_bridge.subscribe(rx_topic, _on_rx)

        # Show status updates
        status_topic = f"{cfg.TOPIC_PREFIX}/{port_name}/status"

        def _on_status(topic: str, payload: str) -> None:
            color = "text-green-600" if payload == "online" else "text-red-500"
            status_label.set_text(f"● {payload}")
            status_label.classes(replace=f"text-xs {color}")

        mqtt_bridge.subscribe(status_topic, _on_status)

        # Send button handler
        def _send() -> None:
            text = cmd_input.value.strip()
            if text:
                mqtt_bridge.publish(tx_topic, text)
                log.push(f"→ {text}")
                cmd_input.set_value("")

        send_btn.on_click(_send)
        cmd_input.on("keydown.enter", _send)


def build() -> None:
    """Assemble the full NiceGUI page."""
    ui.page_title("serial-mqtt-ui")
    with ui.column().classes("w-full max-w-4xl mx-auto p-4 gap-4"):
        ui.label("serial-mqtt-ui").classes("text-2xl font-bold")
        ui.label("Live terminals for three serial ports via MQTT").classes("text-gray-500 mb-2")

        for port_cfg in cfg.PORTS:
            _build_port_card(port_cfg.name, port_cfg.device)

        # Placeholder panel for future macro/command tree
        with ui.expansion("Command Macros (coming soon)", icon="account_tree").classes("w-full"):
            ui.label("This panel will host a command-macro tree in a future release.").classes(
                "text-gray-400 italic"
            )
