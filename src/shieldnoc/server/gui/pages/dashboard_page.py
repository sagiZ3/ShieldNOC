# TODO: add Hostname column to clients information table
# TODO: add buttons for removing or waring a client with a specific message
from datetime import datetime
import random

from PySide6.QtCore import Qt, QTimer, QMargins
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QLineEdit, QPushButton,
    QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView
)
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

from shieldnoc.server.gui.widgets.card_frame import CardFrame
from shieldnoc.server.gui.widgets.topology_view import TopologyView, ClientInfo
from shieldnoc.server.gui.enums import ImagesPaths
from shieldnoc.server.gui.enums import TrafficChart


class ServerDashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setLayoutDirection(Qt.LeftToRight)

        self._time = 0
        self._clients: list[ClientInfo] = []  # TODO: remember import for logic use

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        # ─────────────────────────────────────────────────────────────
        # Header: Title + metrics centered in same row
        # ─────────────────────────────────────────────────────────────
        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        title = QLabel("Dashboard")
        title.setObjectName("pageTitle")

        metrics_wrap = QWidget()
        metrics_layout = QHBoxLayout(metrics_wrap)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(10)

        self.card_clients = self._metric_card_small("Active Clients", "0")
        self.card_cpu = self._metric_card_small("CPU (%)", "0")
        self.card_ram = self._metric_card_small("RAM (%)", "0")

        metrics_layout.addWidget(self.card_clients)
        metrics_layout.addWidget(self.card_cpu)
        metrics_layout.addWidget(self.card_ram)

        header_row.addWidget(title)
        header_row.addStretch(1)
        header_row.addWidget(metrics_wrap)
        header_row.addStretch(1)
        root.addLayout(header_row)

        # ─────────────────────────────────────────────────────────────
        # Body: two columns (left=Traffic+Chat, right=Topology+Logo over Clients table)
        # ─────────────────────────────────────────────────────────────
        body = QHBoxLayout()
        body.setSpacing(10)

        # Left column: Traffic and Chat share height 50/50
        left_col = QVBoxLayout()
        left_col.setSpacing(10)

        self.traffic_card = CardFrame("Network Traffic (Packets/sec)")
        self.traffic_chart = self._create_line_chart("Packets")
        self.traffic_card.content_layout.addWidget(self.traffic_chart)

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

        left_col.addWidget(self.traffic_card, 1)
        left_col.addWidget(self.chat_card, 1)

        left_wrap = QWidget()
        left_wrap.setLayout(left_col)
        left_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Right column: Topology+Logo row on top, Clients table below (same width as right column)
        right_col = QVBoxLayout()
        right_col.setSpacing(10)

        topo_logo_row = QHBoxLayout()
        topo_logo_row.setSpacing(10)

        self.topology_card = CardFrame("Topology")
        self.topology = TopologyView()
        self.topology.setMinimumHeight(240)
        self.topology_card.content_layout.addWidget(self.topology)

        self.brand_card = CardFrame()
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setMinimumHeight(240)

        self.brand_card.content_layout.addStretch(1)
        self.brand_card.content_layout.addWidget(self.logo_label)
        self.brand_card.content_layout.addStretch(1)

        topo_logo_row.addWidget(self.topology_card, 3)
        topo_logo_row.addWidget(self.brand_card, 1)

        right_col.addLayout(topo_logo_row)

        self.clients_card = CardFrame("Clients")
        self.clients_table = QTableWidget(0, 5)
        self.clients_table.setLayoutDirection(Qt.LeftToRight)
        self.clients_table.setHorizontalHeaderLabels(["VPN IP", "MAC", "Host", "Last Seen", "Status"])
        self.clients_table.horizontalHeader().setStretchLastSection(True)
        self.clients_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.clients_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.clients_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.clients_table.setSelectionMode(QAbstractItemView.SingleSelection)

        self.clients_card.content_layout.addWidget(self.clients_table)

        right_col.addWidget(self.clients_card, 1)

        right_wrap = QWidget()
        right_wrap.setLayout(right_col)
        right_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        body.addWidget(left_wrap, 2)
        body.addWidget(right_wrap, 2)

        root.addLayout(body, 1)
        self.set_logo_path(ImagesPaths.LOGO.value)

        # Demo init
        self._seed_chat()
        self._seed_demo_clients()
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._tick_demo)
        self.timer.start()

    # ─────────────────────────────────────────────────────────────
    # External API
    # ─────────────────────────────────────────────────────────────
    def set_logo_path(self, path: str):
        pix = QPixmap(path)
        if pix.isNull():
            self.logo_label.setPixmap(QPixmap())
            return
        scaled = pix.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(scaled)

    def set_clients(self, clients: list[ClientInfo]):  # TODO: remember that's the client logic gateway
        self._clients = clients

        self.card_clients.value_label.setText(str(len(clients)))
        self.topology.set_clients(clients)
        self._update_clients_table_from_clients(clients)

    # ─────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────
    def _create_line_chart(self, y_title: str) -> QChartView:
        self.series = QLineSeries()
        pen = QPen(QColor("#52b6ff"))
        pen.setWidth(2)
        self.series.setPen(pen)

        chart = QChart()
        chart.addSeries(self.series)
        chart.setBackgroundVisible(False)
        chart.setMargins(QMargins(6, 6, 6, 10))
        chart.legend().hide()

        axis_x = QValueAxis()
        axis_x.setRange(0, TrafficChart.TIME_WINDOW_SECONDS.value)
        axis_x.setLabelFormat("%d")
        axis_x.setTitleText("Time (s)")
        axis_x.setTickCount(5)

        axis_y = QValueAxis()
        axis_y.setRange(0, TrafficChart.PACKETS_WINDOW.value)
        axis_y.setTitleText(y_title)
        axis_y.setTickCount(5)

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
        view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        view.setContentsMargins(0, 0, 0, 0)
        return view

    @staticmethod
    def _metric_card_small(title: str, value: str) -> QWidget:
        card = CardFrame(title)
        v = QLabel(value)
        v.setObjectName("metricValue")
        v.setAlignment(Qt.AlignCenter)
        card.content_layout.addWidget(v)
        card.value_label = v
        card.setMinimumHeight(70)
        card.setMinimumWidth(160)
        return card
    # ─────────────────────────────────────────────────────────────
    # Chat
    # ─────────────────────────────────────────────────────────────
    def _seed_chat(self):
        self.chat_view.append(f"[{self._timestamp()}] System: Server chat ready.")
        self.chat_view.append(f"[{self._timestamp()}] Admin: Watching connections…")
        self._scroll_chat_bottom()

    def _send_chat(self):
        msg = self.chat_input.text().strip()
        if not msg:
            return
        self.chat_input.clear()
        self.chat_view.append(f"[{self._timestamp()}] You: {msg}")
        self._scroll_chat_bottom()

    def _scroll_chat_bottom(self):
        sb = self.chat_view.verticalScrollBar()
        sb.setValue(sb.maximum())

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime("%H:%M:%S")

    # ─────────────────────────────────────────────────────────────
    # Clients table
    # ─────────────────────────────────────────────────────────────
    def _update_clients_table_from_clients(self, clients: list[ClientInfo]):  # TODO: add arguments in the real func
        rows = []
        for c in clients:
            vpn_ip = c.key
            mac = "AA:BB:CC:00:00:00"
            host = c.label or "CLIENT"
            last = self._timestamp()
            status = "OK"
            rows.append((vpn_ip, mac, host, last, status))

        self.clients_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                it = QTableWidgetItem(val)
                it.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.clients_table.setItem(r, c, it)

        # Demo CPU/RAM - TODO: add set_metrics(cpu, ram)
        self.card_cpu.value_label.setText(str(random.randint(5, 35)))
        self.card_ram.value_label.setText(str(random.randint(20, 70)))

    # ─────────────────────────────────────────────────────────────
    # Demo tick
    # ─────────────────────────────────────────────────────────────
    def _seed_demo_clients(self):  # TODO: remove ? use differently
        demo = [
            ClientInfo(key="10.0.0.101", label="WIN11"),  # TODO: see if needed ClientInfo & change label name
            ClientInfo(key="10.0.0.102", label="KALI"),
            ClientInfo(key="10.0.0.103", label="DESKTOP"),
        ]
        self.set_clients(demo)

    def _tick_demo(self):  # TODO: figure what the hell is that
                           # TODO: OK - add add_traffic_point(ts: int, packets_per_sec: int) (seperate)
                           # TODO: implement concept shown as below

        chart = self.traffic_chart.chart()
        chart.setAnimationOptions(QChart.AnimationOption.NoAnimation)
        axis_x = chart.axes(Qt.Horizontal)[0]
        axis_x.setRange(max(0, self._time - TrafficChart.TIME_WINDOW_SECONDS.value),
                        self._time if self._time >= TrafficChart.TIME_WINDOW_SECONDS.value else
                        TrafficChart.TIME_WINDOW_SECONDS.value
                        )

        packets = random.randint(50, 1000)  # demo
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.series.append(self._time, packets)
        if self.series.count()-1 > TrafficChart.TIME_WINDOW_SECONDS.value:
            self.series.removePoints(0, self.series.count()-1 - TrafficChart.TIME_WINDOW_SECONDS.value)

        cur = list(self._clients)
        if random.random() < 0.35 and len(cur) < 12:
            last_octet = 100 + len(cur) + 1
            cur.append(ClientInfo(key=f"10.0.0.{last_octet}", label="CLIENT"))
        elif random.random() < 0.25 and len(cur) > 1:
            cur.pop(random.randrange(0, len(cur)))

        self.set_clients(cur)

        if random.random() < 0.10:
            who = random.choice(["System", "Client-101", "Client-102"])
            txt = random.choice([
                "Connected.",
                "Keepalive OK.",
                "Latency spike detected.",
                "New client authenticated.",
            ])
            self.chat_view.append(f"[{self._timestamp()}] {who}: {txt}")
            self._scroll_chat_bottom()

        self._time += 1

            # concept:
            # def _refresh_data(self):
            #     data = self.server_manager.get_snapshot()
            #
            #     self.set_clients(data.clients)
            #     self.add_traffic_point(data.traffic)
            #     self.append_chat(...)
