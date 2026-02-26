# src/shieldnoc/client/gui/pages/dashboard_page.py
import random
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QMargins
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QLineEdit, QListWidget, QListWidgetItem,
    QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QPushButton
)
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

from src.shieldnoc.client.gui.widgets.card_frame import CardFrame


class DashboardPage(QWidget):
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

        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.conn_badge)
        root.addLayout(header)

        # Main split: Left + Right
        main = QHBoxLayout()
        main.setSpacing(10)

        # Right column: Chat + Branding
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
        self.chat_input.returnPressed.connect(self._send_chat)

        self.chat_send = QPushButton("Send")
        self.chat_send.setObjectName("secondaryButton")
        self.chat_send.clicked.connect(self._send_chat)

        cir.addWidget(self.chat_input, 1)
        cir.addWidget(self.chat_send)

        self.chat_card.content_layout.addWidget(self.chat_view, 1)
        self.chat_card.content_layout.addWidget(chat_input_row)

        # Branding: no title (Project removed)
        self.brand_card = CardFrame("")  # no title
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setMinimumHeight(170)

        self.brand_card.content_layout.addStretch(1)
        self.brand_card.content_layout.addWidget(self.logo_label)
        self.brand_card.content_layout.addStretch(1)

        right_col.addWidget(self.chat_card, 2)
        right_col.addWidget(self.brand_card, 1)

        right_wrap = QWidget()
        right_wrap.setLayout(right_col)
        right_wrap.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Left area
        left_col = QVBoxLayout()
        left_col.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        self.card_status = self._metric_card("Connection Status", "Connected")
        self.card_vpn_ip = self._metric_card("Assigned VPN IP", self._vpn_ip, ltr=True)
        self.card_users = self._metric_card("Connected VPN Users", str(self._connected_users))

        top_row.addWidget(self.card_status)
        top_row.addWidget(self.card_vpn_ip)
        top_row.addWidget(self.card_users)

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

        # Traffic + Connections
        self.traffic_card = CardFrame("Network Traffic (Packets/sec)")
        self.chart_view = self._create_line_chart("Packets/sec")
        self.traffic_card.content_layout.addWidget(self.chart_view)

        self.netstat_card = CardFrame("Connections")
        self.net_table = QTableWidget(0, 6)
        self.net_table.setHorizontalHeaderLabels(["Proto", "Local", "Remote", "State", "PID", "Process"])
        self.net_table.horizontalHeader().setStretchLastSection(True)
        self.net_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # ✅ Table read-only
        self.net_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.net_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.net_table.setSelectionMode(QAbstractItemView.SingleSelection)

        # ✅ להקטין את הטבלה חזרה (ולא לחתוך)
        self.net_table.setMinimumHeight(220)

        self.netstat_card.content_layout.addWidget(self.net_table)

        left_col.addLayout(top_row)
        left_col.addLayout(mid_row)

        # ✅ להחזיר יותר מקום לגרף (בלי לשנות גודל הכרטיס עצמו):
        #   פשוט משנים חלוקת גבהים בין שני הכרטיסים
        left_col.addWidget(self.traffic_card, 3)
        left_col.addWidget(self.netstat_card, 2)

        left_wrap = QWidget()
        left_wrap.setLayout(left_col)
        left_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main.addWidget(left_wrap, 2)
        main.addWidget(right_wrap, 1)

        root.addLayout(main, 1)

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._tick)
        self.timer.start()

        self._seed_chat()

    def set_connection_state(self, state: str):
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
            self.logo_label.setPixmap(QPixmap())
            return
        scaled = pix.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(scaled)

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

        # ✅ נותן יותר שטח "נטו" לגרף בתוך הכרטיס, בלי לשנות את גודל הכרטיס
        chart.setMargins(QMargins(6, 6, 6, 10))  # bottom קצת יותר בשביל תוויות X
        chart.legend().hide()

        axis_x = QValueAxis()
        axis_x.setRange(0, 60)
        axis_x.setLabelFormat("%d")
        axis_x.setTitleText("Time (s)")
        axis_x.setTickCount(5)

        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        axis_y.setTitleText(y_title)
        axis_y.setTickCount(5)

        # ✅ פונטים קטנים כדי שייכנסו גם בגובה נמוך, אבל עדיין קריאים
        f_lbl = QFont()
        f_lbl.setPointSize(8)
        f_ttl = QFont()
        f_ttl.setPointSize(8)
        f_ttl.setBold(True)

        axis_x.setLabelsFont(f_lbl)
        axis_y.setLabelsFont(f_lbl)
        axis_x.setTitleFont(f_ttl)
        axis_y.setTitleFont(f_ttl)

        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        self.series.attachAxis(axis_x)
        self.series.attachAxis(axis_y)

        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)

        # ✅ לא מכווץ את ה־View; נותן לו למלא את הכרטיס
        view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        view.setContentsMargins(0, 0, 0, 0)
        return view

    def _seed_chat(self):
        self.chat_view.append(f"[{self._ts()}] System: Welcome to the chat.")
        self.chat_view.append(f"[{self._ts()}] Alice: Hey everyone 👋")
        self.chat_view.append(f"[{self._ts()}] You: Connected and monitoring traffic.")
        self._scroll_chat_bottom()

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

        # ✅ חלון זז של 60 שניות כדי שתמיד יראו "הרבה נקודות"
        chart = self.chart_view.chart()
        axis_x = chart.axes(Qt.Horizontal)[0]
        axis_x.setRange(max(0, self._time - 60), self._time if self._time >= 60 else 60)

        if random.random() < 0.05:
            self._connected_users = max(1, self._connected_users + random.randint(-1, 2))
            self.card_users.value_label.setText(str(self._connected_users))

        self._tcp_conns = max(0, self._tcp_conns + random.randint(-1, 2))
        self._udp_conns = max(0, self._udp_conns + random.randint(-1, 2))
        self.card_tcp.value_label.setText(str(self._tcp_conns))
        self.card_udp.value_label.setText(str(self._udp_conns))

        packets = random.randint(10, 90) if self._connected else random.randint(0, 5)
        self.series.append(self._time, packets)
        if self.series.count() > 60:
            self.series.removePoints(0, self.series.count() - 60)

        self._update_sources()
        self._update_connections()

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
            ip = (
                f"{random.choice([8, 1, 185, 172, 192])}."
                f"{random.randint(0,255)}."
                f"{random.randint(0,255)}."
                f"{random.randint(1,254)}"
            )
            pkt = random.randint(40, 450)
            sources.append((pkt, ip))
        sources.sort(reverse=True)

        self.sources_list.clear()
        for pkt, ip in sources[:6]:
            item = QListWidgetItem(f"{ip}  —  {pkt} pkt")
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.sources_list.addItem(item)

    def _update_connections(self):
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
                if c in (1, 2):
                    it.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.net_table.setItem(r, c, it)