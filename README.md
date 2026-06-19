# serial-mqtt-ui

Minimal Raspberry Pi project to bridge **3 serial ports** via **MQTT** and expose them in a **NiceGUI** web UI.

## Purpose

`serial-mqtt-ui` is designed as a modular communication hub:
- serial devices connect through a bridge process
- MQTT is the internal backbone for all data flows
- NiceGUI provides browser-based terminals

This keeps UI, serial I/O, and future automation loosely coupled.

## Features

- 3-port serial bridge (RX/TX + status)
- MQTT-based pub/sub data exchange
- NiceGUI terminal view for each port
- Docker-friendly deployment for Raspberry Pi
- Configurable via environment variables or config file
- Prepared for future command-macro tree integration

## Architecture

1. **Serial Bridge**
   - reads data from configured serial ports
   - writes inbound MQTT commands to the matching port
2. **MQTT Backbone**
   - central bus between bridge, UI, and future automation
3. **NiceGUI UI**
   - displays terminal output and sends commands via MQTT

Data flow:
- `Serial -> MQTT -> UI`
- `UI -> MQTT -> Serial`

## MQTT topic convention (3 ports)

Using prefix `serial`:

- `serial/port1/rx`, `serial/port1/tx`, `serial/port1/status`
- `serial/port2/rx`, `serial/port2/tx`, `serial/port2/status`
- `serial/port3/rx`, `serial/port3/tx`, `serial/port3/status`

Suggested meaning:
- `rx`: bytes read from serial device and published to MQTT
- `tx`: payload from MQTT written to serial device
- `status`: online/offline/errors/health state

## Configuration

You can configure by environment variables or config file.
Typical keys:

- `MQTT_HOST`, `MQTT_PORT`, `MQTT_USERNAME`, `MQTT_PASSWORD`
- `TOPIC_PREFIX` (default `serial`)
- `SERIAL_PORT_1`, `SERIAL_PORT_2`, `SERIAL_PORT_3`
- `SERIAL_BAUDRATE_1`, `SERIAL_BAUDRATE_2`, `SERIAL_BAUDRATE_3`

## Docker usage (Raspberry Pi)

Build:

```bash
docker build -t serial-mqtt-ui .
```

Run:

```bash
docker run --rm -it \
  --device=/dev/ttyUSB0 \
  --device=/dev/ttyUSB1 \
  --device=/dev/ttyUSB2 \
  -p 8080:8080 \
  -e MQTT_HOST=192.168.1.10 \
  -e MQTT_PORT=1883 \
  serial-mqtt-ui
```

## docker-compose usage (Raspberry Pi)

The provided `docker-compose.yml` includes both the app and a bundled
[Eclipse Mosquitto](https://mosquitto.org/) broker so the stack is self-contained:

```bash
docker compose up --build
```

The UI is then reachable at `http://<raspberry-pi-ip>:8080`.

To use an external broker instead, remove the `broker` service and set
`MQTT_HOST` to your broker's address.

## Intended minimal project structure

```text
serial-mqtt-ui/
├── README.md
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── app/
    ├── main.py
    ├── config.py
    ├── serial_bridge.py
    ├── mqtt_bridge.py
    ├── ui.py
    └── models.py
```

## Planned extension: command-macro tree

A future UI panel can provide a macro tree for reusable actions:
- publish macro run requests via MQTT (e.g. `serial/macros/<path>/run`)
- receive execution results (e.g. `serial/macros/<path>/result`)

## Troubleshooting

- **Serial port unavailable**: verify device path, container permissions, and exclusive device use.
- **MQTT not connecting**: verify broker host/port/credentials and network reachability.
- **No terminal data**: verify baud rate, cable/wiring, and test the port directly on host.

## Security notes

- The bundled `docker-compose.yml` configures Mosquitto with `allow_anonymous true` for
  convenience during development.  For production deployments set `MQTT_USERNAME` /
  `MQTT_PASSWORD` and enable password authentication in the broker configuration.
