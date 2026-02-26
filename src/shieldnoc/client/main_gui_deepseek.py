import sys
import random
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QStackedWidget, QFrame
)
from PySide6.QtCore import Qt, QTimer, QMargins, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QPixmap
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

# ----------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------
DARK_STYLE = """
QWidget {
    background-color: #050814;
    color: #e7f0ff;
    font-family: 'Segoe UI', 'Rubik', sans-serif;
}
#appTitle {
    font-size: 20px;
    font-weight: 600;
    padding: 10px 16px;
    color: #f7c948;
    text-shadow: 0 0 10px #f7c948;
}
#pageTitle {
    font-size: 18px;
    font-weight: 600;
    color: #52b6ff;
    text-shadow: 0 0 12px #1e6fff;
}
#pageSubtitle {
    color: #a7b3d5;
    margin-bottom: 6px;
}
#card {
    background-color: rgba(5, 10, 30, 0.92);
    border-radius: 16px;
    border: 1px solid #1b3358;
    box-shadow: 0 0 18px rgba(0, 200, 255, 0.12);
}
#cardTitle {
    font-size: 14px;
    font-weight: 600;
    color: #f7f9ff;
}
QLineEdit {
    background-color: rgba(3, 6, 18, 0.9);
    border: 1px solid #2a3c5f;
    border-radius: 8px;
    padding: 6px 8px;
}
QLineEdit:focus {
    border: 1px solid #52b6ff;
    box-shadow: 0 0 12px rgba(82, 182, 255, 0.7);
}
QPushButton {
    background-color: #2a2a3c;
    color: #00ffff;
    border: 1px solid #00ffff;
    border-radius: 5px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #3a3a4c;
}
QPushButton:pressed {
    background-color: #1a1a2c;
}
#primaryButton {
    background-color: #f7c948;
    color: #1e90ff;
    text-shadow: 0 0 10px rgba(82, 182, 255, 0.8);
    border-radius: 12px;
    padding: 10px 18px;
    font-weight: 600;
    border: 1px solid #52b6ff;
    box-shadow: 0 0 15px rgba(82, 182, 255, 0.6);
}
#primaryButton:hover {
    background-color: #ffe27a;
}
#topBarButton {
    background-color: transparent;
    border: none;
    padding: 8px 12px;
    color: #cdd7ff;
}
#topBarButton:hover {
    background-color: rgba(15, 32, 72, 0.9);
    border-radius: 8px;
}
#statusDisconnected {
    color: #ff7675;
    font-weight: 500;
}
#statusConnecting {
    color: #ffeaa7;
    font-weight: 500;
}
#statusConnected {
    color: #00d1a3;
    font-weight: 500;
}
#statusError {
    color: #d63031;
    font-weight: 500;
}
#badgeConnected {
    background-color: #00d1a3;
    color: #050814;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
}
#logView, #chatDisplay {
    background-color: rgba(2, 6, 25, 0.85);
    border-radius: 10px;
    border: 1px solid #283458;
    color: #e7f0ff;
}
#metricLabel {
    font-size: 13px;
    color: #cbd4ff;
}
#metricValue {
    font-size: 20px;
    font-weight: 700;
    color: #f7c948;
    text-align: center;
}
#switchBgButton {
    background-color: transparent;
    border-radius: 999px;
    border: 1px solid #52b6ff;
    padding: 6px 12px;
    color: #52b6ff;
    font-size: 11px;
}
#switchBgButton:hover {
    background-color: rgba(16, 48, 96, 0.7);
}
QTableWidget {
    background-color: rgba(2, 6, 25, 0.7);
    border: none;
    color: #cbd4ff;
    gridline-color: #1b3358;
}
QTableWidget::item {
    padding: 4px;
}
QTableWidget::item:selected {
    background-color: #1e3a5f;
}
QHeaderView::section {
    background-color: #0a0f1f;
    color: #a7b3d5;
    border: none;
    padding: 6px;
}
"""

# ----------------------------------------------------------------------
# Card Frame (reusable widget)
# ----------------------------------------------------------------------
class CardFrame(QFrame):
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        if title:
            title_label = QLabel(title)
            title_label.setObjectName("cardTitle")
            layout.addWidget(title_label)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(6)
        layout.addLayout(self.content_layout)

# ----------------------------------------------------------------------
# Background Layer (cycles through images)
# ----------------------------------------------------------------------
class BackgroundLayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.backgrounds = [
            "assets/backgrounds/1.png",
            "assets/backgrounds/2.png",
            "assets/backgrounds/3.png",
            "assets/backgrounds/4.png",
            "assets/backgrounds/5.png",
            "assets/backgrounds/6.png",
        ]
        self.index = 0
        self.opacity = 0.12
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAutoFillBackground(False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(self.opacity)
        if self.backgrounds and self.index < len(self.backgrounds):
            pix = QPixmap(self.backgrounds[self.index])
            if not pix.isNull():
                scaled = pix.scaled(
                    self.size(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
                painter.drawPixmap(0, 0, scaled)
        painter.end()

    def next_background(self):
        if self.backgrounds:
            self.index = (self.index + 1) % len(self.backgrounds)
            self.update()

# ----------------------------------------------------------------------
# Connect Page
# ----------------------------------------------------------------------
class ConnectPage(QWidget):
    connect_requested = Signal(str, int, dict)
    change_background_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        header = QLabel("ShieldNOC – Settings")
        header.setObjectName("pageTitle")
        subtitle = QLabel("Configure server and client settings.")
        subtitle.setObjectName("pageSubtitle")
        main_layout.addWidget(header)
        main_layout.addWidget(subtitle)

        # Server settings
        server_card = CardFrame("Server Settings")
        form_layout = QHBoxLayout()
        form_layout.setSpacing(10)
        form_layout.addWidget(QLabel("Server IP:"))
        self.ip_edit = QLineEdit("127.0.0.1")
        form_layout.addWidget(self.ip_edit)
        form_layout.addWidget(QLabel("Port:"))
        self.port_edit = QLineEdit("9000")
        form_layout.addWidget(self.port_edit)
        server_card.content_layout.addLayout(form_layout)
        main_layout.addWidget(server_card)

        # Client settings
        client_card = CardFrame("Client Settings")
        ip_row = QHBoxLayout()
        ip_row.addWidget(QLabel("My VPN IP:"))
        self.vpn_ip_edit = QLineEdit("10.8.0.2")
        self.change_ip_btn = QPushButton("Change IP")
        self.change_ip_btn.clicked.connect(self.on_change_ip)
        ip_row.addWidget(self.vpn_ip_edit)
        ip_row.addWidget(self.change_ip_btn)
        client_card.content_layout.addLayout(ip_row)

        self.change_bg_btn = QPushButton("Change Background")
        self.change_bg_btn.clicked.connect(self.change_background_requested.emit)
        client_card.content_layout.addWidget(self.change_bg_btn)
        main_layout.addWidget(client_card)

        main_layout.addStretch(1)

        # Bottom row
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        self.status_label = QLabel("Disconnected")
        self.status_label.setObjectName("statusDisconnected")
        self.connect_button = QPushButton("Connect to ShieldNOC")
        self.connect_button.setObjectName("primaryButton")
        self.connect_button.clicked.connect(self.on_connect_clicked)
        bottom_layout.addWidget(self.status_label)
        bottom_layout.addWidget(self.connect_button)
        main_layout.addLayout(bottom_layout)

    def on_connect_clicked(self):
        ip = self.ip_edit.text().strip()
        try:
            port = int(self.port_edit.text().strip())
        except ValueError:
            self._set_status("Invalid port", "statusError")
            return
        self._set_status("Connecting...", "statusConnecting")
        self.connect_requested.emit(ip, port, {})  # no extra options

    def on_change_ip(self):
        # Placeholder – in real app you would request IP change from server
        print(f"Request IP change to: {self.vpn_ip_edit.text()}")

    def _set_status(self, text: str, object_name: str):
        self.status_label.setText(text)
        self.status_label.setObjectName(object_name)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def set_connected(self, ok: bool):
        if ok:
            self._set_status("Connected to ShieldNOC", "statusConnected")
        else:
            self._set_status("Connection failed", "statusError")

# ----------------------------------------------------------------------
# Dashboard Page
# ----------------------------------------------------------------------
class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Top bar
        header_layout = QHBoxLayout()
        title = QLabel("ShieldNOC Dashboard")
        title.setObjectName("pageTitle")
        self.connection_label = QLabel("Status: Connected")
        self.connection_label.setObjectName("badgeConnected")
        self.switch_bg_btn = QPushButton("Change Background")
        self.switch_bg_btn.setObjectName("switchBgButton")
        header_layout.addWidget(title)
        header_layout.addStretch(1)
        header_layout.addWidget(self.switch_bg_btn)
        header_layout.addWidget(self.connection_label)
        main_layout.addLayout(header_layout)

        # Main content: left (2/3) and right (1/3)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)

        # ---------- Left panel ----------
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        # TCP / UDP cards
        counts_row = QHBoxLayout()
        self.tcp_card = self._create_metric_card("TCP Connections", "0")
        self.udp_card = self._create_metric_card("UDP Connections", "0")
        counts_row.addWidget(self.tcp_card)
        counts_row.addWidget(self.udp_card)
        left_layout.addLayout(counts_row)

        # Common source IPs
        sources_card = CardFrame("Common Source IPs")
        self.sources_label = QLabel(
            "1. 192.168.1.1 – 340 pkts\n"
            "2. 8.8.8.8 – 190 pkts\n"
            "3. 1.1.1.1 – 122 pkts"
        )
        self.sources_label.setAlignment(Qt.AlignTop)
        sources_card.content_layout.addWidget(self.sources_label)
        left_layout.addWidget(sources_card)

        # Traffic chart
        traffic_card = CardFrame("Network Traffic (Packets/sec)")
        self.traffic_chart_view = self._create_line_chart("Packets/sec")
        traffic_card.content_layout.addWidget(self.traffic_chart_view)
        left_layout.addWidget(traffic_card)

        # Status row
        status_row = QHBoxLayout()
        self.server_status_label = QLabel("Server: Connected")
        self.server_status_label.setObjectName("metricLabel")
        self.users_count_label = QLabel("Users: 3")
        self.users_count_label.setObjectName("metricLabel")
        self.my_ip_label = QLabel("My IP: 10.8.0.2")
        self.my_ip_label.setObjectName("metricLabel")
        status_row.addWidget(self.server_status_label)
        status_row.addWidget(self.users_count_label)
        status_row.addWidget(self.my_ip_label)
        status_row.addStretch(1)
        left_layout.addLayout(status_row)

        # Netstat table
        netstat_card = CardFrame("Active Connections (netstat)")
        self.netstat_table = QTableWidget(0, 4)
        self.netstat_table.setHorizontalHeaderLabels(["Protocol", "Local Address", "Remote Address", "State"])
        self.netstat_table.horizontalHeader().setStretchLastSection(True)
        self.netstat_table.setAlternatingRowColors(True)
        self.netstat_table.setObjectName("netstatTable")
        netstat_card.content_layout.addWidget(self.netstat_table)
        left_layout.addWidget(netstat_card)

        # ---------- Right panel ----------
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # Chat area (2/3 height)
        chat_card = CardFrame("Chat – Connected Users")
        chat_layout = QVBoxLayout()
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setObjectName("chatDisplay")
        chat_layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type a message...")
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.on_send_message)
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(self.send_btn)
        chat_layout.addLayout(input_layout)
        chat_card.content_layout.addLayout(chat_layout)
        right_layout.addWidget(chat_card, stretch=2)

        # Project info (1/3 height)
        info_card = CardFrame("ShieldNOC VPN")
        info_layout = QVBoxLayout()
        self.logo_label = QLabel()
        pix = QPixmap("assets/ShieldNOC_logo.png")  # use same logo or update path
        if not pix.isNull():
            pix_scaled = pix.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pix_scaled)
        self.logo_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.logo_label)
        info_layout.addStretch(1)
        info_card.content_layout.addLayout(info_layout)
        right_layout.addWidget(info_card, stretch=1)

        # Assemble
        content_layout.addWidget(left_panel, stretch=2)
        content_layout.addWidget(right_panel, stretch=1)
        main_layout.addLayout(content_layout)

        # Demo data
        self._init_demo_state()

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _create_line_chart(self, y_title: str) -> QChartView:
        self.series = QLineSeries()
        pen = QPen(QColor("#52b6ff"))
        pen.setWidth(2)
        self.series.setPen(pen)

        chart = QChart()
        chart.addSeries(self.series)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundVisible(False)
        chart.setMargins(QMargins(10, 10, 10, 10))

        axis_x = QValueAxis()
        axis_x.setRange(0, 60)
        axis_x.setLabelFormat("%d")
        axis_x.setTitleText("Time (s)")

        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        axis_y.setTitleText(y_title)

        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        self.series.attachAxis(axis_x)
        self.series.attachAxis(axis_y)

        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        view.setMinimumHeight(180)
        return view

    def _create_metric_card(self, title: str, value: str) -> QWidget:
        card = CardFrame(title)
        value_label = QLabel(value)
        value_label.setObjectName("metricValue")
        value_label.setAlignment(Qt.AlignCenter)
        card.content_layout.addWidget(value_label)
        card.setMinimumHeight(70)
        card.value_label = value_label
        return card

    def _init_demo_state(self):
        self._time = 0
        self._tcp_conns = 5
        self._udp_conns = 3
        self._users_online = 3
        self._server_status = "Connected"
        self._my_ip = "10.8.0.2"

        self._update_netstat()  # initial entries

        self.timer = QTimer(self)
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self._update_demo_data)
        self.timer.start()

    def _update_demo_data(self):
        self._time += 2
        packets = random.randint(20, 90)

        # Update graph
        self.series.append(self._time, packets)
        if self.series.count() > 60:
            self.series.removePoints(0, self.series.count() - 60)

        # Update TCP/UDP counts
        self._tcp_conns = max(0, self._tcp_conns + random.randint(-1, 2))
        self._udp_conns = max(0, self._udp_conns + random.randint(-1, 1))
        self.tcp_card.value_label.setText(str(self._tcp_conns))
        self.udp_card.value_label.setText(str(self._udp_conns))

        # Update common sources
        ips = [f"192.168.1.{random.randint(2,254)}" for _ in range(3)]
        self.sources_label.setText(
            f"1. {ips[0]} – {random.randint(100,500)} pkts\n"
            f"2. {ips[1]} – {random.randint(50,300)} pkts\n"
            f"3. {ips[2]} – {random.randint(10,200)} pkts"
        )

        # Users online
        self._users_online = max(1, self._users_online + random.randint(-1, 1))
        self.users_count_label.setText(f"Users: {self._users_online}")

        # Netstat – add a fake connection occasionally
        if random.random() < 0.3:
            self._add_fake_connection()

        # Chat – simulate incoming message
        if random.random() < 0.2:
            user = f"User{random.randint(1,5)}"
            msg = random.choice(["Hello", "Anyone there?", "ShieldNOC rocks!"])
            self.chat_display.append(f"[{user}]: {msg}")

    def _update_netstat(self):
        data = [
            ("TCP", "10.8.0.2:54321", "192.168.1.1:443", "ESTABLISHED"),
            ("TCP", "10.8.0.2:54322", "8.8.8.8:53", "ESTABLISHED"),
            ("UDP", "10.8.0.2:12345", "1.1.1.1:53", "ACTIVE"),
            ("TCP", "10.8.0.2:54323", "10.8.0.1:9000", "ESTABLISHED"),
        ]
        self.netstat_table.setRowCount(len(data))
        for i, (proto, local, remote, state) in enumerate(data):
            self.netstat_table.setItem(i, 0, QTableWidgetItem(proto))
            self.netstat_table.setItem(i, 1, QTableWidgetItem(local))
            self.netstat_table.setItem(i, 2, QTableWidgetItem(remote))
            self.netstat_table.setItem(i, 3, QTableWidgetItem(state))

    def _add_fake_connection(self):
        row = self.netstat_table.rowCount()
        self.netstat_table.insertRow(row)
        proto = random.choice(["TCP", "UDP"])
        local = f"10.8.0.2:{random.randint(10000,60000)}"
        remote = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}:{random.randint(1,65535)}"
        state = random.choice(["ESTABLISHED", "TIME_WAIT", "CLOSE_WAIT", "ACTIVE"])
        self.netstat_table.setItem(row, 0, QTableWidgetItem(proto))
        self.netstat_table.setItem(row, 1, QTableWidgetItem(local))
        self.netstat_table.setItem(row, 2, QTableWidgetItem(remote))
        self.netstat_table.setItem(row, 3, QTableWidgetItem(state))
        # Keep only last 8 rows
        if self.netstat_table.rowCount() > 8:
            self.netstat_table.removeRow(0)

    def on_send_message(self):
        msg = self.chat_input.text().strip()
        if msg:
            self.chat_display.append(f"[Me]: {msg}")
            self.chat_input.clear()

    # Public methods to update from main window
    def set_server_status(self, status: str):
        self.server_status_label.setText(f"Server: {status}")
        if status.lower() == "connected":
            self.connection_label.setText("Status: Connected")
            self.connection_label.setObjectName("badgeConnected")
        elif status.lower() == "connecting":
            self.connection_label.setText("Status: Connecting")
            self.connection_label.setObjectName("statusConnecting")
        else:
            self.connection_label.setText("Status: Disconnected")
            self.connection_label.setObjectName("statusDisconnected")
        self.connection_label.style().unpolish(self.connection_label)
        self.connection_label.style().polish(self.connection_label)

    def set_my_ip(self, ip: str):
        self._my_ip = ip
        self.my_ip_label.setText(f"My IP: {ip}")

# ----------------------------------------------------------------------
# Main Window
# ----------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShieldNOC Client")
        self.resize(1300, 800)

        # Central widget with background layer
        central = QWidget()
        self.setCentralWidget(central)
        central.setAttribute(Qt.WA_StyledBackground, False)
        central.setStyleSheet("background: transparent;")

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Top bar
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(12, 8, 12, 8)
        top_bar.setSpacing(8)

        app_label = QLabel("ShieldNOC Client")
        app_label.setObjectName("appTitle")
        top_bar.addWidget(app_label)
        top_bar.addStretch(1)

        self.home_btn = QPushButton("Settings")
        self.home_btn.setObjectName("topBarButton")
        self.dashboard_btn = QPushButton("Dashboard")
        self.dashboard_btn.setObjectName("topBarButton")
        top_bar.addWidget(self.home_btn)
        top_bar.addWidget(self.dashboard_btn)

        root_layout.addLayout(top_bar)

        # Stacked pages
        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack)

        self.connect_page = ConnectPage()
        self.dashboard_page = DashboardPage()

        self.stack.addWidget(self.connect_page)
        self.stack.addWidget(self.dashboard_page)

        # Navigation
        self.home_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.connect_page))
        self.dashboard_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.dashboard_page))

        # Connect signals
        self.connect_page.connect_requested.connect(self._handle_connect)
        self.connect_page.change_background_requested.connect(self._next_background)
        self.dashboard_page.switch_bg_btn.clicked.connect(self._next_background)

        # Background layer
        self.bg_layer = BackgroundLayer(self)
        self.bg_layer.lower()

        # Apply global style
        self.setStyleSheet(DARK_STYLE)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg_layer.resize(self.size())

    def _next_background(self):
        self.bg_layer.next_background()

    def _handle_connect(self, ip: str, port: int, options: dict):
        # Simulate connection after 400ms
        QTimer.singleShot(400, lambda: self._after_connect(True))

    def _after_connect(self, success: bool):
        self.connect_page.set_connected(success)
        if success:
            vpn_ip = self.connect_page.vpn_ip_edit.text()
            self.dashboard_page.set_my_ip(vpn_ip)
            self.dashboard_page.set_server_status("Connected")
            self.stack.setCurrentWidget(self.dashboard_page)

# ----------------------------------------------------------------------
# Run application
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())