# main.py
import sys
import random
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, Signal, QMargins
from PySide6.QtGui import QPainter, QPixmap, QColor, QPen
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QFrame, QGridLayout, QLineEdit, QTableWidget, QTableWidgetItem,
    QTextEdit, QListWidget, QListWidgetItem, QSizePolicy, QHeaderView
)

# QtCharts (כמו בקוד הקודם שלך)
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis


# =========================
# Style (שומר על אותו כיוון עיצובי)
# =========================

STYLE_SHEET = """
QWidget {
    background-color: #050814;
    color: #e7f0ff;
    font-family: 'Segoe UI', 'Rubik', sans-serif;
}

/* Titles */
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

/* Cards */
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

/* Inputs */
QLineEdit {
    background-color: rgba(3, 6, 18, 0.9);
    border: 1px solid #2a3c5f;
    border-radius: 8px;
    padding: 6px 8px;
    color: #e7f0ff;
}
QLineEdit:focus {
    border: 1px solid #52b6ff;
    box-shadow: 0 0 12px rgba(82, 182, 255, 0.7);
}

/* Buttons */
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
#secondaryButton {
    background-color: transparent;
    border-radius: 12px;
    padding: 10px 14px;
    font-weight: 600;
    border: 1px solid #52b6ff;
    color: #52b6ff;
}
#secondaryButton:hover {
    background-color: rgba(16, 48, 96, 0.7);
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

/* Connection badge */
#badgeConnected {
    background-color: #00d1a3;
    color: #050814;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
}
#badgeConnecting {
    background-color: #ffeaa7;
    color: #050814;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
}
#badgeDisconnected {
    background-color: #ff7675;
    color: #050814;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
}

/* Log */
#logView {
    background-color: rgba(2, 6, 25, 0.85);
    border-radius: 10px;
    border: 1px solid #283458;
}

/* Metrics */
#metricValue {
    font-size: 20px;
    font-weight: 800;
    color: #f7c948;
    text-align: center;
}
#metricLabel {
    font-size: 12px;
    color: #cbd4ff;
}

/* Switch background button */
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

/* Tables */
QTableWidget {
    background-color: rgba(2, 6, 25, 0.75);
    border: 1px solid #283458;
    border-radius: 10px;
    gridline-color: #283458;
}
QHeaderView::section {
    background-color: rgba(10, 20, 50, 0.9);
    padding: 6px;
    border: none;
    color: #cfe3ff;
    font-weight: 600;
}
QTableWidget::item {
    padding: 6px;
}
QTableWidget::item:selected {
    background-color: rgba(82, 182, 255, 0.25);
}

/* Chat */
#chatView {
    background-color: rgba(2, 6, 25, 0.85);
    border-radius: 10px;
    border: 1px solid #283458;
}
#chatInputRow QPushButton {
    padding: 8px 12px;
}
"""


# =========================
# Background Layer (Queue של תמונות)
# =========================

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
        p = QPainter(self)
        p.setOpacity(self.opacity)
        if self.backgrounds:
            pix = QPixmap(self.backgrounds[self.index])
            if not pix.isNull():
                scaled = pix.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                p.drawPixmap(0, 0, scaled)
        p.end()

    def next_background(self):
        if not self.backgrounds:
            return
        self.index = (self.index + 1) % len(self.backgrounds)
        self.update()


# =========================
# Widgets
# =========================

class CardFrame(QFrame):
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        if title:
            t = QLabel(title)
            t.setObjectName("cardTitle")
            lay.addWidget(t)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(6)
        lay.addLayout(self.content_layout)


class ConnectPage(QWidget):
    connect_requested = Signal(str, int)
    vpn_ip_changed = Signal(str)
    bg_change_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        title = QLabel("Settings — Client")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Configure server address, client VPN IP, and UI settings.")
        subtitle.setObjectName("pageSubtitle")

        root.addWidget(title)
        root.addWidget(subtitle)

        # Server settings (נשאר אותו דבר)
        server_card = CardFrame("Server Settings")
        form = QGridLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.ip_edit = QLineEdit("127.0.0.1")
        self.port_edit = QLineEdit("9000")

        form.addWidget(QLabel("Server IP:"), 0, 0)
        form.addWidget(self.ip_edit, 0, 1)
        form.addWidget(QLabel("Port:"), 1, 0)
        form.addWidget(self.port_edit, 1, 1)

        server_card.content_layout.addLayout(form)
        root.addWidget(server_card)

        # Client VPN IP + Background
        client_card = CardFrame("Client / UI")
        client_grid = QGridLayout()
        client_grid.setHorizontalSpacing(12)
        client_grid.setVerticalSpacing(10)

        self.vpn_ip_edit = QLineEdit("10.0.0.100")
        self.vpn_ip_edit.setLayoutDirection(Qt.LeftToRight)

        self.btn_apply_vpn = QPushButton("Apply Client VPN IP")
        self.btn_apply_vpn.setObjectName("secondaryButton")
        self.btn_apply_vpn.clicked.connect(self._apply_vpn_ip)

        self.btn_bg = QPushButton("Change Background")
        self.btn_bg.setObjectName("switchBgButton")
        self.btn_bg.clicked.connect(self.bg_change_requested.emit)

        client_grid.addWidget(QLabel("Client VPN IP:"), 0, 0)
        client_grid.addWidget(self.vpn_ip_edit, 0, 1)
        client_grid.addWidget(self.btn_apply_vpn, 1, 1)
        client_grid.addWidget(self.btn_bg, 2, 1)

        client_card.content_layout.addLayout(client_grid)
        root.addWidget(client_card)

        # Bottom connect row
        bottom = QHBoxLayout()
        bottom.addStretch(1)

        self.status_label = QLabel("Disconnected")
        self.status_label.setObjectName("badgeDisconnected")

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setObjectName("primaryButton")
        self.connect_btn.clicked.connect(self._connect_clicked)

        bottom.addWidget(self.status_label)
        bottom.addWidget(self.connect_btn)

        root.addStretch(1)
        root.addLayout(bottom)

    def _connect_clicked(self):
        ip = self.ip_edit.text().strip()
        try:
            port = int(self.port_edit.text().strip())
        except ValueError:
            self._set_status("Invalid Port", "badgeDisconnected")
            return

        self._set_status("Connecting…", "badgeConnecting")
        self.connect_requested.emit(ip, port)

    def _apply_vpn_ip(self):
        ip = self.vpn_ip_edit.text().strip()
        if not ip:
            return
        self.vpn_ip_changed.emit(ip)

    def set_connected(self, ok: bool):
        if ok:
            self._set_status("Connected", "badgeConnected")
        else:
            self._set_status("Connection Failed", "badgeDisconnected")

    def _set_status(self, text: str, object_name: str):
        self.status_label.setText(text)
        self.status_label.setObjectName(object_name)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)


class DashboardPage(QWidget):
    bg_change_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._connected = True
        self._vpn_ip = "10.0.0.100"
        self._connected_users = 1

        self._time = 0
        self._tcp_conns = 3
        self._udp_conns = 2

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Header
        header = QHBoxLayout()
        title = QLabel("Dashboard — VPN Client")
        title.setObjectName("pageTitle")

        self.conn_badge = QLabel("Connected")
        self.conn_badge.setObjectName("badgeConnected")

        self.btn_bg = QPushButton("Change Background")
        self.btn_bg.setObjectName("switchBgButton")
        self.btn_bg.clicked.connect(self.bg_change_requested.emit)

        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.btn_bg)
        header.addWidget(self.conn_badge)
        root.addLayout(header)

        # Main area: Left (metrics/graph/tables) + Right (chat + branding)
        main = QHBoxLayout()
        main.setSpacing(10)

        # -------- Right column (1/3 width): Chat (2/3 height) + Branding (1/3 height)
        right_col = QVBoxLayout()
        right_col.setSpacing(10)

        self.chat_card = CardFrame("Chat")
        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        self.chat_view.setObjectName("chatView")

        chat_input_row = QWidget()
        chat_input_row.setObjectName("chatInputRow")
        cir = QHBoxLayout(chat_input_row)
        cir.setContentsMargins(0, 0, 0, 0)
        cir.setSpacing(8)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type a message…")
        self.chat_input.setLayoutDirection(Qt.LeftToRight)

        self.chat_send = QPushButton("Send")
        self.chat_send.setObjectName("secondaryButton")
        self.chat_send.clicked.connect(self._send_chat)

        cir.addWidget(self.chat_input, 1)
        cir.addWidget(self.chat_send)

        self.chat_card.content_layout.addWidget(self.chat_view, 1)
        self.chat_card.content_layout.addWidget(chat_input_row)

        self.brand_card = CardFrame("Project")
        self.project_name = QLabel("ShieldNOC Client")
        self.project_name.setObjectName("metricLabel")
        self.project_name.setAlignment(Qt.AlignCenter)

        self.logo_label = QLabel("Logo Placeholder")
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setObjectName("metricLabel")
        self.logo_label.setMinimumHeight(140)

        self.brand_card.content_layout.addStretch(1)
        self.brand_card.content_layout.addWidget(self.project_name)
        self.brand_card.content_layout.addWidget(self.logo_label)
        self.brand_card.content_layout.addStretch(1)

        right_col.addWidget(self.chat_card, 2)
        right_col.addWidget(self.brand_card, 1)

        right_wrap = QWidget()
        right_wrap.setLayout(right_col)
        right_wrap.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # -------- Left area: cards + graph + sources + netstat table
        left_col = QVBoxLayout()
        left_col.setSpacing(10)

        # Top row: Connection status + VPN IP + Connected users
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        self.card_status = self._metric_card("Connection Status", "Connected")
        self.card_vpn_ip = self._metric_card("Assigned VPN IP", self._vpn_ip, ltr=True)
        self.card_users = self._metric_card("Connected VPN Users", str(self._connected_users))

        top_row.addWidget(self.card_status)
        top_row.addWidget(self.card_vpn_ip)
        top_row.addWidget(self.card_users)

        # Second row: TCP/UDP counts + Top sources
        mid_row = QHBoxLayout()
        mid_row.setSpacing(10)

        self.card_tcp = self._metric_card("TCP Connections", str(self._tcp_conns))
        self.card_udp = self._metric_card("UDP Connections", str(self._udp_conns))

        self.sources_card = CardFrame("Top Source IPs")
        self.sources_list = QListWidget()
        self.sources_list.setObjectName("logView")
        self.sources_list.setSpacing(2)
        self.sources_card.content_layout.addWidget(self.sources_list)

        mid_row.addWidget(self.card_tcp)
        mid_row.addWidget(self.card_udp)
        mid_row.addWidget(self.sources_card, 2)

        # Traffic graph
        self.traffic_card = CardFrame("Network Traffic (Packets/sec)")
        self.chart_view = self._create_line_chart("Packets/sec")
        self.traffic_card.content_layout.addWidget(self.chart_view)

        # Netstat-like table
        self.netstat_card = CardFrame("Connections (netstat)")
        self.net_table = QTableWidget(0, 6)
        self.net_table.setHorizontalHeaderLabels(["Proto", "Local", "Remote", "State", "PID", "Process"])
        self.net_table.horizontalHeader().setStretchLastSection(True)
        self.net_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.net_table.setAlternatingRowColors(False)
        self.netstat_card.content_layout.addWidget(self.net_table)

        left_col.addLayout(top_row)
        left_col.addLayout(mid_row)
        left_col.addWidget(self.traffic_card, 2)
        left_col.addWidget(self.netstat_card, 2)

        left_wrap = QWidget()
        left_wrap.setLayout(left_col)
        left_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Compose main split
        main.addWidget(left_wrap, 2)
        main.addWidget(right_wrap, 1)

        root.addLayout(main, 1)

        # Demo timer
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._tick)
        self.timer.start()

        self._seed_chat()

    def set_connection_state(self, state: str):
        # state: "connected" | "connecting" | "disconnected"
        s = state.lower().strip()
        if s == "connected":
            self.conn_badge.setText("Connected")
            self.conn_badge.setObjectName("badgeConnected")
            self._connected = True
            self.card_status.value_label.setText("Connected")
        elif s == "connecting":
            self.conn_badge.setText("Connecting…")
            self.conn_badge.setObjectName("badgeConnecting")
            self._connected = False
            self.card_status.value_label.setText("Connecting…")
        else:
            self.conn_badge.setText("Disconnected")
            self.conn_badge.setObjectName("badgeDisconnected")
            self._connected = False
            self.card_status.value_label.setText("Disconnected")

        self.conn_badge.style().unpolish(self.conn_badge)
        self.conn_badge.style().polish(self.conn_badge)

    def set_vpn_ip(self, ip: str):
        self._vpn_ip = ip
        self.card_vpn_ip.value_label.setText(ip)

    def set_logo_path(self, path: str):
        pix = QPixmap(path)
        if pix.isNull():
            self.logo_label.setText("Logo Placeholder")
            self.logo_label.setPixmap(QPixmap())
            return

        scaled = pix.scaled(220, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(scaled)
        self.logo_label.setText("")

    def _metric_card(self, title: str, value: str, ltr: bool = False) -> QWidget:
        card = CardFrame(title)
        v = QLabel(value)
        v.setObjectName("metricValue")
        v.setAlignment(Qt.AlignCenter)
        if ltr:
            v.setLayoutDirection(Qt.LeftToRight)
        card.content_layout.addWidget(v)
        card.value_label = v
        card.setMinimumHeight(90)
        return card

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
        view.setMinimumHeight(240)
        return view

    def _seed_chat(self):
        self.chat_view.append(f"[{self._ts()}] System: Welcome to the chat.")
        self.chat_view.append(f"[{self._ts()}] Alice: Hey everyone 👋")
        self.chat_view.append(f"[{self._ts()}] You: Connected and monitoring traffic.")

    def _send_chat(self):
        msg = self.chat_input.text().strip()
        if not msg:
            return
        self.chat_input.clear()
        self.chat_view.append(f"[{self._ts()}] You: {msg}")
        self._scroll_chat_bottom()

    def _scroll_chat_bottom(self):
        sb = self.chat_view.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _ts(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def _tick(self):
        self._time += 1

        # Simulate connection/user counts
        if random.random() < 0.05:
            self._connected_users = max(1, self._connected_users + random.randint(-1, 2))
            self.card_users.value_label.setText(str(self._connected_users))

        # Simulate TCP/UDP counts
        self._tcp_conns = max(0, self._tcp_conns + random.randint(-1, 2))
        self._udp_conns = max(0, self._udp_conns + random.randint(-1, 2))
        self.card_tcp.value_label.setText(str(self._tcp_conns))
        self.card_udp.value_label.setText(str(self._udp_conns))

        # Traffic graph
        packets = random.randint(10, 90) if self._connected else random.randint(0, 5)
        self.series.append(self._time, packets)
        if self.series.count() > 60:
            self.series.removePoints(0, self.series.count() - 60)

        # Top sources
        self._update_sources()

        # Netstat table
        self._update_netstat()

        # Random incoming chat
        if random.random() < 0.08:
            who = random.choice(["Alice", "Bob", "Charlie", "System"])
            txt = random.choice([
                "Handshake OK.",
                "Latency spike detected.",
                "Switching route…",
                "New client joined the VPN.",
                "Packet rate normal.",
            ])
            self.chat_view.append(f"[{self._ts()}] {who}: {txt}")
            self._scroll_chat_bottom()

    def _update_sources(self):
        sources = []
        for _ in range(6):
            ip = f"{random.choice([8, 1, 185, 172, 192])}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            pkt = random.randint(40, 450)
            sources.append((pkt, ip))
        sources.sort(reverse=True)

        self.sources_list.clear()
        for pkt, ip in sources[:6]:
            item = QListWidgetItem(f"{ip}  —  {pkt} pkt")
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.sources_list.addItem(item)

    def _update_netstat(self):
        rows = []
        proto_choices = ["TCP", "UDP"]
        states_tcp = ["ESTABLISHED", "SYN_SENT", "CLOSE_WAIT", "TIME_WAIT"]
        procs = ["python", "chrome", "discord", "steam", "svchost", "ssh"]

        for _ in range(10):
            proto = random.choice(proto_choices)
            local = f"{self._vpn_ip}:{random.randint(1024, 65535)}"
            remote = f"{random.choice(['8.8.8.8','1.1.1.1','52.94.236.248','172.217.22.14'])}:{random.randint(80, 65535)}"
            state = random.choice(states_tcp) if proto == "TCP" else "-"
            pid = str(random.randint(200, 12000))
            proc = random.choice(procs)
            rows.append((proto, local, remote, state, pid, proc))

        self.net_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                it = QTableWidgetItem(val)
                if c in (1, 2):  # IP:Port in LTR
                    it.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.net_table.setItem(r, c, it)


# =========================
# Main Window
# =========================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShieldNOC Client")
        self.resize(1200, 720)

        # Central with stack
        central = QWidget()
        self.setCentralWidget(central)
        central.setAttribute(Qt.WA_StyledBackground, False)
        central.setStyleSheet("background: transparent;")

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Top bar
        top = QHBoxLayout()
        top.setContentsMargins(12, 8, 12, 8)
        top.setSpacing(8)

        app_label = QLabel("ShieldNOC Client")
        app_label.setObjectName("appTitle")

        self.btn_settings = QPushButton("Settings")
        self.btn_settings.setObjectName("topBarButton")

        self.btn_dash = QPushButton("Dashboard")
        self.btn_dash.setObjectName("topBarButton")

        top.addWidget(app_label)
        top.addStretch(1)
        top.addWidget(self.btn_settings)
        top.addWidget(self.btn_dash)

        root.addLayout(top)

        # Stack pages
        self.stack = QStackedWidget()
        root.addWidget(self.stack)

        self.page_settings = ConnectPage()
        self.page_dash = DashboardPage()

        self.stack.addWidget(self.page_settings)
        self.stack.addWidget(self.page_dash)

        self.btn_settings.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_settings))
        self.btn_dash.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_dash))

        # Background layer
        self.bg_layer = BackgroundLayer(self)
        self.bg_layer.lower()

        # Wiring
        self.page_settings.connect_requested.connect(self._handle_connect)
        self.page_settings.vpn_ip_changed.connect(self._set_vpn_ip)
        self.page_settings.bg_change_requested.connect(self.bg_layer.next_background)

        self.page_dash.bg_change_requested.connect(self.bg_layer.next_background)

        # Default logo path placeholder (אתה תחליף נתיב)
        self.page_dash.set_logo_path("assets/ShieldNOC_logo.png")

        # Global style
        self.setStyleSheet(STYLE_SHEET)

        # Initial page
        self.stack.setCurrentWidget(self.page_settings)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg_layer.resize(self.size())

    def _set_vpn_ip(self, ip: str):
        self.page_dash.set_vpn_ip(ip)

    def _handle_connect(self, ip: str, port: int):
        # Simulate async connect flow
        self.page_dash.set_connection_state("connecting")
        QTimer.singleShot(450, lambda: self._after_connect(True))

    def _after_connect(self, ok: bool):
        self.page_settings.set_connected(ok)
        if ok:
            self.page_dash.set_connection_state("connected")
            self.stack.setCurrentWidget(self.page_dash)
        else:
            self.page_dash.set_connection_state("disconnected")


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()