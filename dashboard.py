import json
import random
import re
import sys
import threading
from collections import deque
from datetime import datetime

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QLineEdit,
    QPushButton, QCheckBox, QFormLayout, QVBoxLayout, QHBoxLayout,
    QGridLayout, QTabWidget, QTextEdit, QGroupBox,
)

import paho.mqtt.client as mqtt

from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from mqtt_init import broker_ip, broker_port, username, password

try:
    import winsound

    def _beep():
        winsound.Beep(2500, 700)
except ImportError:
    def _beep():
        pass


def _make_mqtt_client(client_id):
    try:
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id, clean_session=True)
    except AttributeError:
        return mqtt.Client(client_id, clean_session=True)


DHT_TOPIC = 'pr/home/5976397/sts'
ALARM_TOPIC = 'pr/home/alarm/sts'
AC_TOPIC = 'pr/home/conditioner/sts'
PUMP_TOPIC = 'pr/home/pump/sts'

SUBSCRIBED_TOPICS = (DHT_TOPIC, ALARM_TOPIC, AC_TOPIC, PUMP_TOPIC)

SIMULATE_INTERVAL_MS = 9000

TEMP_WARNING = 28.0
TEMP_EMERGENCY = 30.0
HUMIDITY_WARNING = 74.5
HUMIDITY_EMERGENCY = 76.0

HISTORY_LEN = 30

CLIENT_NAME = "IOT_dashboard-" + str(random.randrange(1, 10_000_000))

READING_PATTERN = re.compile(
    r"Temperature:\s*(-?\d+(?:\.\d+)?).*Humidity:\s*(-?\d+(?:\.\d+)?)"
)


def parse_relay_value(payload):
    try:
        data = json.loads(payload)
        if isinstance(data, dict) and "value" in data:
            return int(data["value"])
    except (ValueError, TypeError):
        pass
    match = re.search(r'value"?\s*:\s*(-?\d+)', payload)
    return int(match.group(1)) if match else None


COLORS = {
    "bg": "#1b1e27",
    "panel": "#242836",
    "panel_alt": "#2c3142",
    "border": "#383e52",
    "text": "#e7e9f0",
    "muted": "#8a90a6",
    "accent": "#4f8cff",
    "humidity": "#7fd9c4",
    "ok": "#33c07f",
    "warning": "#f5a524",
    "danger": "#ef4c54",
    "unknown": "#5b6178",
}

STYLESHEET = f"""
* {{
    font-family: "Segoe UI", "Inter", sans-serif;
    color: {COLORS['text']};
}}
QMainWindow, QWidget#Central {{
    background-color: {COLORS['bg']};
}}
QLabel[role="title"] {{
    font-size: 18px;
    font-weight: 600;
}}
QLabel[role="subtitle"] {{
    color: {COLORS['muted']};
    font-size: 11px;
}}
QFrame#Card {{
    background-color: {COLORS['panel']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
}}
QLabel[role="cardTitle"] {{
    font-size: 13px;
    font-weight: 600;
}}
QLabel[role="icon"] {{
    font-size: 22px;
}}
QLabel[role="metric"] {{
    font-size: 26px;
    font-weight: 700;
}}
QLabel[role="metricUnit"] {{
    font-size: 12px;
    color: {COLORS['muted']};
}}
QLineEdit, QTextEdit {{
    background-color: {COLORS['panel_alt']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 5px 8px;
    selection-background-color: {COLORS['accent']};
}}
QPushButton {{
    background-color: {COLORS['accent']};
    border: none;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 600;
    color: white;
}}
QPushButton:hover {{
    background-color: #6ba0ff;
}}
QPushButton:disabled {{
    background-color: {COLORS['unknown']};
    color: {COLORS['muted']};
}}
QCheckBox {{
    spacing: 6px;
}}
QGroupBox {{
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    margin-top: 10px;
    padding-top: 12px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
}}
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    top: -1px;
}}
QTabBar::tab {{
    background: {COLORS['panel']};
    border: 1px solid {COLORS['border']};
    border-bottom: none;
    padding: 7px 18px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background: {COLORS['panel_alt']};
    color: {COLORS['accent']};
}}
QScrollBar:vertical {{
    background: {COLORS['panel']};
    width: 10px;
}}
QScrollBar::handle:vertical {{
    background: {COLORS['border']};
    border-radius: 5px;
}}
"""


def build_app_icon():
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor(COLORS["accent"]))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(2, 2, 60, 60, 16, 16)
    painter.setPen(QColor("white"))
    painter.setFont(QFont("Segoe UI Emoji", 28))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "\U0001F3E0")
    painter.end()
    return QIcon(pixmap)


class StatusPill(QFrame):
    _STYLES = {
        "unknown": (COLORS["unknown"], "●"),
        "connecting": (COLORS["warning"], "…"),
        "ok": (COLORS["ok"], "✓"),
        "warning": (COLORS["warning"], "⚠"),
        "danger": (COLORS["danger"], "⛔"),
    }

    def __init__(self, text="Unknown", level="unknown"):
        super().__init__()
        self.setObjectName("Pill")
        self._icon = QLabel()
        self._text = QLabel()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 3, 12, 3)
        layout.setSpacing(6)
        layout.addWidget(self._icon)
        layout.addWidget(self._text)
        self.set_state(text, level)

    def set_state(self, text, level="unknown"):
        color, icon = self._STYLES.get(level, self._STYLES["unknown"])
        self._icon.setText(icon)
        self._text.setText(text)
        self.setStyleSheet(f"""
            QFrame#Pill {{
                background-color: {color}26;
                border: 1px solid {color};
                border-radius: 11px;
            }}
            QLabel {{ color: {color}; font-weight: 600; font-size: 11px; }}
        """)


class Card(QFrame):
    def __init__(self, icon, title):
        super().__init__()
        self.setObjectName("Card")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(10)

        header = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setProperty("role", "icon")
        title_lbl = QLabel(title)
        title_lbl.setProperty("role", "cardTitle")
        self.pill = StatusPill("Unknown", "unknown")
        header.addWidget(icon_lbl)
        header.addWidget(title_lbl)
        header.addStretch(1)
        header.addWidget(self.pill)
        outer.addLayout(header)

        self.body = QVBoxLayout()
        self.body.setSpacing(8)
        outer.addLayout(self.body)


class ClimateCard(Card):
    def __init__(self):
        super().__init__("\U0001F321️", "Climate — DHT Sensor")

        self.temp_history = deque(maxlen=HISTORY_LEN)
        self.hum_history = deque(maxlen=HISTORY_LEN)

        metrics = QHBoxLayout()
        metrics.setSpacing(36)
        temp_box = QVBoxLayout()
        temp_box.setSpacing(2)
        self.temp_value = QLabel("--")
        self.temp_value.setProperty("role", "metric")
        temp_caption = QLabel("Temperature")
        temp_caption.setProperty("role", "metricUnit")
        temp_box.addWidget(self.temp_value)
        temp_box.addWidget(temp_caption)

        hum_box = QVBoxLayout()
        hum_box.setSpacing(2)
        self.hum_value = QLabel("--")
        self.hum_value.setProperty("role", "metric")
        hum_caption = QLabel("Humidity")
        hum_caption.setProperty("role", "metricUnit")
        hum_box.addWidget(self.hum_value)
        hum_box.addWidget(hum_caption)

        metrics.addLayout(temp_box)
        metrics.addLayout(hum_box)
        metrics.addStretch(1)
        self.body.addLayout(metrics)

        self.figure = Figure(figsize=(4, 2), facecolor=COLORS["panel"])
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(160)
        self.ax_temp = self.figure.add_subplot(111)
        self.ax_hum = self.ax_temp.twinx()
        self.temp_line, = self.ax_temp.plot([], [], color=COLORS["accent"],
                                             linewidth=2, marker="o", markersize=3)
        self.hum_line, = self.ax_hum.plot([], [], color=COLORS["humidity"],
                                           linewidth=2, marker="o", markersize=3)
        self._style_axes()
        self.body.addWidget(self.canvas)

        controls = QHBoxLayout()
        self.simulate_checkbox = QCheckBox("Simulate readings")
        self.simulate_checkbox.setChecked(True)
        topic_lbl = QLabel(f"Topic: {DHT_TOPIC}")
        topic_lbl.setProperty("role", "subtitle")
        controls.addWidget(self.simulate_checkbox)
        controls.addStretch(1)
        controls.addWidget(topic_lbl)
        self.body.addLayout(controls)

    def _style_axes(self):
        for ax in (self.ax_temp, self.ax_hum):
            ax.set_facecolor(COLORS["panel"])
            ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
            for spine in ax.spines.values():
                spine.set_color(COLORS["border"])
        self.ax_temp.tick_params(axis="x", colors=COLORS["muted"], labelsize=8)
        self.ax_temp.tick_params(axis="y", colors=COLORS["accent"], labelsize=8)
        self.ax_hum.tick_params(axis="y", colors=COLORS["humidity"], labelsize=8)
        self.ax_temp.set_ylabel("°C", color=COLORS["accent"], fontsize=9, labelpad=6)
        self.ax_hum.set_ylabel("%", color=COLORS["humidity"], fontsize=9, labelpad=12)
        self.figure.subplots_adjust(left=0.16, right=0.86, top=0.9, bottom=0.2)

    def add_reading(self, temp, hum):
        self.temp_history.append(temp)
        self.hum_history.append(hum)
        self.temp_value.setText(f"{temp:.1f}°C")
        self.hum_value.setText(f"{hum:.1f}%")
        self._redraw()

    def _redraw(self):
        xs = list(range(len(self.temp_history)))
        self.temp_line.set_data(xs, list(self.temp_history))
        self.hum_line.set_data(xs, list(self.hum_history))
        self.ax_temp.relim()
        self.ax_temp.autoscale_view()
        self.ax_hum.relim()
        self.ax_hum.autoscale_view()
        self.canvas.draw_idle()

    def set_pill_for(self, temp, hum):
        if temp >= TEMP_EMERGENCY or hum >= HUMIDITY_EMERGENCY:
            self.pill.set_state("Emergency", "danger")
        elif temp >= TEMP_WARNING or hum >= HUMIDITY_WARNING:
            self.pill.set_state("Warning", "warning")
        else:
            self.pill.set_state("Normal", "ok")


class RelayCard(Card):
    def __init__(self, icon, title, topic, active_label="Active", idle_label="Idle", on_beep=False):
        super().__init__(icon, title)
        self.topic = topic
        self.active_label = active_label
        self.idle_label = idle_label
        self.on_beep = on_beep
        self.active = False

        topic_lbl = QLabel(f"Topic: {topic}")
        topic_lbl.setProperty("role", "subtitle")
        self.last_update_lbl = QLabel("No messages yet")
        self.last_update_lbl.setProperty("role", "subtitle")
        self.body.addWidget(topic_lbl)
        self.body.addWidget(self.last_update_lbl)
        self.body.addStretch(1)

        self.set_active(False, initial=True)

    def set_active(self, active, initial=False):
        self.active = active
        if active:
            self.pill.set_state(self.active_label, "danger")
            if self.on_beep and not initial:
                threading.Thread(target=_beep, daemon=True).start()
        else:
            self.pill.set_state(self.idle_label, "ok")
        self.last_update_lbl.setText("Updated " + datetime.now().strftime("%H:%M:%S"))


class ConnectionPanel(QGroupBox):
    def __init__(self, on_connect):
        super().__init__("Connection")
        self.on_connect_callback = on_connect

        self.host_input = QLineEdit(str(broker_ip))
        self.port_input = QLineEdit(str(broker_port))
        self.port_input.setValidator(QtGui.QIntValidator())
        self.client_input = QLineEdit(CLIENT_NAME)
        self.user_input = QLineEdit(username)
        self.pass_input = QLineEdit(password)
        self.pass_input.setEchoMode(QLineEdit.Password)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self._handle_click)
        self.pill = StatusPill("Disconnected", "unknown")

        form = QFormLayout()
        form.addRow("Broker", self.host_input)
        form.addRow("Port", self.port_input)
        form.addRow("Client ID", self.client_input)
        form.addRow("Username", self.user_input)
        form.addRow("Password", self.pass_input)

        actions = QHBoxLayout()
        actions.addWidget(self.connect_btn)
        actions.addStretch(1)
        actions.addWidget(self.pill)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(actions)

    def _handle_click(self):
        try:
            port = int(self.port_input.text())
        except ValueError:
            port = 0
        self.connect_btn.setEnabled(False)
        self.pill.set_state("Connecting…", "connecting")
        self.on_connect_callback(
            self.host_input.text(), port, self.client_input.text(),
            self.user_input.text(), self.pass_input.text(),
        )

    def mark_connected(self):
        self.pill.set_state("Connected", "ok")
        self.connect_btn.setText("Reconnect")
        self.connect_btn.setEnabled(True)

    def mark_failed(self):
        self.pill.set_state("Connection failed", "danger")
        self.connect_btn.setEnabled(True)

    def mark_disconnected(self):
        self.pill.set_state("Disconnected", "unknown")
        self.connect_btn.setEnabled(True)


class EventLog(QWidget):
    _LEVEL_COLORS = {
        "info": COLORS["muted"],
        "ok": COLORS["ok"],
        "warning": COLORS["warning"],
        "danger": COLORS["danger"],
    }

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.view = QTextEdit()
        self.view.setReadOnly(True)
        layout.addWidget(self.view)

    def log(self, message, level="info"):
        color = self._LEVEL_COLORS.get(level, COLORS["muted"])
        ts = datetime.now().strftime("%H:%M:%S")
        self.view.append(
            f'<span style="color:{COLORS["muted"]}">[{ts}]</span> '
            f'<span style="color:{color}">{message}</span>'
        )


class MqttSignals(QObject):
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    connection_failed = pyqtSignal(int)
    message = pyqtSignal(str, str)


class MqttClient:
    def __init__(self):
        self.signals = MqttSignals()
        self.client = None
        self.connected = False

    def connect_to(self, host, port, client_id, user, pwd):
        self.client = _make_mqtt_client(client_id)
        self.client.username_pw_set(user, pwd)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        try:
            self.client.connect(host, port)
        except Exception as exc:
            print("Connection error:", exc)
            self.signals.connection_failed.emit(-1)
            return
        self.client.loop_start()

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            self.signals.connected.emit()
        else:
            self.signals.connection_failed.emit(rc)

    def _on_disconnect(self, client, userdata, rc=0):
        self.connected = False
        self.signals.disconnected.emit()

    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        self.signals.message.emit(msg.topic, payload)

    def subscribe(self, topic):
        if self.connected:
            self.client.subscribe(topic)

    def publish(self, topic, payload):
        if self.connected:
            self.client.publish(topic, payload)
        else:
            print("Not connected — can't publish to", topic)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Server Room Monitor")
        self.setWindowIcon(build_app_icon())
        self.resize(980, 760)

        self.mc = MqttClient()
        self.mc.signals.connected.connect(self._on_mqtt_connected)
        self.mc.signals.disconnected.connect(self._on_mqtt_disconnected)
        self.mc.signals.connection_failed.connect(self._on_mqtt_failed)
        self.mc.signals.message.connect(self._on_mqtt_message)

        self.temp_alert = False
        self.humidity_alert = False
        self.alarm_active = False

        central = QWidget()
        central.setObjectName("Central")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(14)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Server Room Monitor")
        title.setProperty("role", "title")
        subtitle = QLabel("Climate, alarm & relay control — one MQTT connection")
        subtitle.setProperty("role", "subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch(1)
        root.addLayout(header)

        self.connection_panel = ConnectionPanel(self._connect_clicked)
        root.addWidget(self.connection_panel)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)

        dashboard = QWidget()
        grid = QGridLayout(dashboard)
        grid.setSpacing(14)

        self.climate_card = ClimateCard()
        self.alarm_card = RelayCard("\U0001F6A8", "Alarm Siren", ALARM_TOPIC,
                                     "Sounding", "Idle", on_beep=True)
        self.ac_card = RelayCard("\U0001F300", "Emergency A/C", AC_TOPIC,
                                  "Engaged", "Standby")
        self.pump_card = RelayCard("\U0001F4A7", "Drain Pump", PUMP_TOPIC,
                                    "Running", "Standby")

        grid.addWidget(self.climate_card, 0, 0, 1, 2)
        grid.addWidget(self.alarm_card, 1, 0)
        grid.addWidget(self.ac_card, 1, 1)
        grid.addWidget(self.pump_card, 2, 0, 1, 2)
        grid.setRowStretch(0, 2)

        self.tabs.addTab(dashboard, "Dashboard")

        self.event_log = EventLog()
        self.tabs.addTab(self.event_log, "Event Log")

        self.simulate_timer = QTimer(self)
        self.simulate_timer.timeout.connect(self._publish_simulated_reading)
        self.simulate_timer.start(SIMULATE_INTERVAL_MS)
        self.climate_card.simulate_checkbox.stateChanged.connect(self._toggle_simulation)

        self.event_log.log("Dashboard started. Configure the broker above and press Connect.", "info")

    def _connect_clicked(self, host, port, client_id, user, pwd):
        if not host:
            self.event_log.log("Enter a broker address first.", "warning")
            self.connection_panel.mark_disconnected()
            return
        self.event_log.log(f"Connecting to {host}:{port} …", "info")
        self.mc.connect_to(host, port, client_id, user, pwd)

    def _on_mqtt_connected(self):
        self.connection_panel.mark_connected()
        for topic in SUBSCRIBED_TOPICS:
            self.mc.subscribe(topic)
        self.event_log.log("Connected to broker.", "ok")

    def _on_mqtt_disconnected(self):
        self.connection_panel.mark_disconnected()
        self.event_log.log("Disconnected from broker.", "warning")

    def _on_mqtt_failed(self, rc):
        self.connection_panel.mark_failed()
        self.event_log.log(f"Connection failed (code {rc}).", "danger")

    def _toggle_simulation(self, state):
        if state == Qt.Checked:
            self.simulate_timer.start(SIMULATE_INTERVAL_MS)
        else:
            self.simulate_timer.stop()

    def _publish_simulated_reading(self):
        if not self.climate_card.simulate_checkbox.isChecked():
            return
        temp = 22 + random.randrange(1, 100) / 10
        hum = 74 + random.randrange(1, 30) / 10
        payload = f"Temperature: {temp:.1f} Humidity: {hum:.1f}"
        self.mc.publish(DHT_TOPIC, payload)

    def _on_mqtt_message(self, topic, payload):
        if topic == DHT_TOPIC:
            self._handle_reading(payload)
        elif topic == ALARM_TOPIC:
            value = parse_relay_value(payload)
            if value is not None:
                self.alarm_card.set_active(bool(value))
        elif topic == AC_TOPIC:
            value = parse_relay_value(payload)
            if value is not None:
                self.ac_card.set_active(bool(value))
        elif topic == PUMP_TOPIC:
            value = parse_relay_value(payload)
            if value is not None:
                self.pump_card.set_active(bool(value))

    def _handle_reading(self, payload):
        match = READING_PATTERN.search(payload)
        if not match:
            return
        temp, hum = float(match.group(1)), float(match.group(2))
        self.climate_card.add_reading(temp, hum)
        self.climate_card.set_pill_for(temp, hum)
        self.event_log.log(f"Reading: {temp:.1f}°C / {hum:.1f}% RH", "info")
        self._evaluate_thresholds(temp, hum)

    def _evaluate_thresholds(self, temp, hum):
        if temp >= TEMP_EMERGENCY and not self.temp_alert:
            self.temp_alert = True
            self.event_log.log(f"⚠ Temperature emergency ({temp:.1f}°C) — engaging A/C.", "danger")
            self.mc.publish(AC_TOPIC, json.dumps({"value": 1}))
            self._raise_alarm()
        elif temp < TEMP_EMERGENCY and self.temp_alert:
            self.temp_alert = False
            self.event_log.log("Temperature back to normal.", "ok")
            self.mc.publish(AC_TOPIC, json.dumps({"value": 0}))

        if hum >= HUMIDITY_EMERGENCY and not self.humidity_alert:
            self.humidity_alert = True
            self.event_log.log(f"⚠ Leak detected ({hum:.1f}% RH) — engaging pump.", "danger")
            self.mc.publish(PUMP_TOPIC, json.dumps({"value": 1}))
            self._raise_alarm()
        elif hum < HUMIDITY_EMERGENCY and self.humidity_alert:
            self.humidity_alert = False
            self.event_log.log("Humidity back to normal.", "ok")
            self.mc.publish(PUMP_TOPIC, json.dumps({"value": 0}))

        if not self.temp_alert and not self.humidity_alert and self.alarm_active:
            self.alarm_active = False
            self.mc.publish(ALARM_TOPIC, json.dumps({"value": 0}))
            self.event_log.log("All clear — alarm silenced.", "ok")

    def _raise_alarm(self):
        if not self.alarm_active:
            self.alarm_active = True
            self.mc.publish(ALARM_TOPIC, json.dumps({"value": 1}))


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
