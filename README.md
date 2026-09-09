# Server Room Monitor

A PyQt5 dashboard for a simulated IoT server room: live temperature/humidity
readings over MQTT, with automatic emergency alarm, A/C and pump relays.

## Run it

```bash
pip install -r requirements.txt
python dashboard.py
```

Configure the broker in `mqtt_init.py`, then press **Connect** in the app.

## What's here

- `dashboard.py` — the main app: one MQTT connection, live chart, status
  cards for climate/alarm/A-C/pump, and an event log.
- `mqtt_init.py` — broker address, credentials, topics.
- `DHT.py`, `MonitorGUI.py`, `alarm.py`, `emergency air conditioner.py`,
  `pump.py` — the original standalone scripts `dashboard.py` consolidates.
- `GUI_Template/` — earlier reference/template scripts.

## How it works

`dashboard.py` simulates a DHT sensor publishing temperature/humidity
readings. Crossing 30°C or 76% humidity triggers the corresponding relay
(A/C or pump) and the alarm, all over MQTT — the same as separate physical
devices would.
