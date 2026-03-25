# src/shieldnoc/client/gui/pages/dashboard_page.py
import random

from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import Qt, QTimer, QMargins
from PySide6.QtGui import QPainter, QPen, QColor, QPixmap, QFont
from PySide6.QtWidgets import ( QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QLineEdit,
                                QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView,
                                QAbstractItemView, QPushButton, QSplitter, QScrollArea,
)

from shieldnoc.client.gui.enums import General, TrafficChart
from shieldnoc.client.gui.widgets.card_frame import CardFrame
from shieldnoc.client.gui.widgets.top_processes_chart import TopProcessesChart
from shieldnoc.client.managers.chat import ChatManager


class DashboardPage(QWidget):
    def __init__(self, chat_manager: ChatManager ,parent=None):
        super().__init__(parent)

        # State
        self._connected = True
        self._vpn_ip = "10.0.0.100"
        self._connected_users = 1

        self._time = 0
        self._tcp_conns = 3
        self._udp_conns = 2

        self._chart_animation_enabled = True

        # Main layout: the whole page will be inside a scroll area for small windows
        main_scroll = QScrollArea(self)
        main_scroll.setWidgetResizable(True)
        main_scroll.setFrameShape(QScrollArea.NoFrame)
        main_layout_v = QVBoxLayout(self)
        main_layout_v.setContentsMargins(0, 0, 0, 0)
        main_layout_v.addWidget(main_scroll)

        # Container widget that holds all dashboard content
        container = QWidget()
        main_scroll.setWidget(container)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(16, 16, 16, 16)
        container_layout.setSpacing(12)

        # ========================
        # Header row with title, metric cards, and status badge
        # ========================
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        title = QLabel("Dashboard — VPN Client")
        title.setObjectName("pageTitle")
        header_layout.addWidget(title)

        # Create the three metric cards (no fixed width, they will stretch)
        self.card_status = self._metric_card("Connection Status", "Connected", min_height=80)
        self.card_vpn_ip = self._metric_card("Assigned VPN IP", self._vpn_ip, ltr=True, min_height=80)
        self.card_users = self._metric_card("Connected VPN Users", str(self._connected_users), min_height=80)

        # Allow cards to shrink and expand, but give them a stretch factor
        for card in (self.card_status, self.card_vpn_ip, self.card_users):
            card.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
            card.setMinimumWidth(120)   # prevent them from becoming too narrow

        header_layout.addWidget(self.card_status)
        header_layout.addWidget(self.card_vpn_ip)
        header_layout.addWidget(self.card_users)

        header_layout.addStretch(1)

        self.conn_badge = QLabel("Connected")
        self.conn_badge.setObjectName("badgeConnected")
        header_layout.addWidget(self.conn_badge)

        container_layout.addLayout(header_layout)

        # ========================
        # Main split (left / right) using QSplitter for user resizing
        # ========================
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setChildrenCollapsible(False)

        # Left column (will contain a vertical splitter for chart/table)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        # Vertical splitter for left column: Top Processes / Traffic / Connections
        left_v_splitter = QSplitter(Qt.Vertical)
        left_v_splitter.setChildrenCollapsible(False)

        # Top Processes chart
        self.processes_card = CardFrame("Top Processes by Connections")
        self.processes_chart = TopProcessesChart(use_demo=True)
        self.processes_card.content_layout.addWidget(self.processes_chart)
        self.processes_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_v_splitter.addWidget(self.processes_card)

        # Traffic chart
        self.traffic_card = CardFrame("Network Traffic (Packets/sec)")
        self.chart_view = self._create_line_chart("Packets")
        self.traffic_card.content_layout.addWidget(self.chart_view)
        self.traffic_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_v_splitter.addWidget(self.traffic_card)

        # Connections table
        self.connections_card = CardFrame("Connections")
        self.net_table = QTableWidget(0, 6)
        self.net_table.setHorizontalHeaderLabels(["Proto", "Local", "Remote", "State", "PID", "Process"])
        self.net_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.net_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.net_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.net_table.setMinimumHeight(120)  # allow it to be smaller
        self.net_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        header = self.net_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        self.connections_card.content_layout.addWidget(self.net_table)
        self.connections_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_v_splitter.addWidget(self.connections_card)

        # Set initial stretch factors for the vertical splitter (chart areas vs table)
        left_v_splitter.setStretchFactor(0, 2)  # Top Processes
        left_v_splitter.setStretchFactor(1, 2)  # Traffic
        left_v_splitter.setStretchFactor(2, 1)  # Connections

        left_layout.addWidget(left_v_splitter)
        main_splitter.addWidget(left_widget)

        # Right column (vertical splitter for top-right and chat)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        right_v_splitter = QSplitter(Qt.Vertical)
        right_v_splitter.setChildrenCollapsible(False)

        # Top right row (TCP/UDP and logo)
        top_right_widget = QWidget()
        top_right_layout = QHBoxLayout(top_right_widget)
        top_right_layout.setContentsMargins(0, 0, 0, 0)
        top_right_layout.setSpacing(12)

        tcp_udp_widget = QWidget()
        tcp_udp_layout = QVBoxLayout(tcp_udp_widget)
        tcp_udp_layout.setSpacing(10)
        self.card_tcp = self._metric_card("TCP Connections", str(self._tcp_conns), min_height=76)
        self.card_udp = self._metric_card("UDP Connections", str(self._udp_conns), min_height=76)
        tcp_udp_layout.addWidget(self.card_tcp)
        tcp_udp_layout.addWidget(self.card_udp)
        tcp_udp_layout.addStretch(1)

        self.logo_card = CardFrame("")
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setMinimumHeight(150)
        self.logo_card.content_layout.addStretch(1)
        self.logo_card.content_layout.addWidget(self.logo_label)
        self.logo_card.content_layout.addStretch(1)
        self.logo_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        top_right_layout.addWidget(tcp_udp_widget, 1)
        top_right_layout.addWidget(self.logo_card, 1)
        top_right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Chat card
        self.chat_manager = chat_manager

        self.chat_card = CardFrame("Chat")
        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        self.chat_view.setObjectName("chatView")

        chat_input_row = QWidget()
        chat_input_row.setObjectName("chatInputRow")
        chat_input_layout = QHBoxLayout(chat_input_row)
        chat_input_layout.setContentsMargins(0, 0, 0, 0)
        chat_input_layout.setSpacing(8)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type a message…")
        self.chat_input.setLayoutDirection(Qt.LeftToRight)
        self.chat_input.returnPressed.connect(self._send_chat_msg)

        self.chat_send_btn = QPushButton("Send")
        self.chat_send_btn.setObjectName("secondaryButton")
        self.chat_send_btn.clicked.connect(self._send_chat_msg)

        chat_input_layout.addWidget(self.chat_input, 1)
        chat_input_layout.addWidget(self.chat_send_btn)

        self.chat_card.content_layout.addWidget(self.chat_view, 1)
        self.chat_card.content_layout.addWidget(chat_input_row)
        self.chat_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add to right vertical splitter
        right_v_splitter.addWidget(top_right_widget)
        right_v_splitter.addWidget(self.chat_card)

        # Set stretch factors: top-right takes less, chat takes more
        right_v_splitter.setStretchFactor(0, 1)
        right_v_splitter.setStretchFactor(1, 2)

        right_layout.addWidget(right_v_splitter)

        # default sizes of cards
        left_v_splitter.setSizes([300, 280, 250])
        right_v_splitter.setSizes([250, 400])
        main_splitter.setSizes([800, 400])

        main_splitter.addWidget(right_widget)

        # Set stretch factors for main splitter (left column gets more space)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 1)

        container_layout.addWidget(main_splitter, 1)

        self._start_tick_iterations()

    # -----------------------------
    # Public API (unchanged)
    # -----------------------------
    def set_connection_state(self, state: str):
        state = state.lower().strip()

        if state == "connected":
            self.conn_badge.setText("Connected")
            self.conn_badge.setObjectName("badgeConnected")
            self._connected = True
            self.card_status.value_label.setText("Connected")
        elif state == "connecting":
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

        scaled = pix.scaled(220, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(scaled)

    # -----------------------------
    # UI helpers
    # -----------------------------
    def _metric_card(self, title: str, value: str, ltr: bool = False, min_height: int = 90) -> QWidget:
        card = CardFrame(title)

        value_label = QLabel(value)
        value_label.setObjectName("metricValue")
        value_label.setAlignment(Qt.AlignCenter)

        if ltr:
            value_label.setLayoutDirection(Qt.LeftToRight)

        card.content_layout.addWidget(value_label)
        card.value_label = value_label
        card.setMinimumHeight(min_height)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

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
        chart.setMargins(QMargins(8, 8, 8, 18))
        chart.legend().hide()

        axis_x = QValueAxis()
        axis_x.setRange(0, TrafficChart.TIME_WINDOW_SECONDS.value)
        axis_x.setLabelFormat("%d")
        axis_x.setTitleText("Time (s)")
        axis_x.setTickCount(6)

        axis_y = QValueAxis()
        axis_y.setRange(0, TrafficChart.PACKETS_WINDOW.value)
        axis_y.setTitleText(y_title)
        axis_y.setTickCount(6)

        label_font = QFont("Segoe UI", 7)
        title_font = QFont("Segoe UI", 8)
        title_font.setBold(True)

        axis_x.setLabelsFont(label_font)
        axis_y.setLabelsFont(label_font)
        axis_x.setTitleFont(title_font)
        axis_y.setTitleFont(title_font)

        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        self.series.attachAxis(axis_x)
        self.series.attachAxis(axis_y)

        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._traffic_chart = chart
        self._traffic_axis_x = axis_x
        self._traffic_axis_y = axis_y

        return view

    # -----------------------------
    # Chat
    # -----------------------------
    def _pull_to_chat(self):
        pull = True
        while pull:
            next_chat_msg = self.chat_manager.get_next_msg()
            if next_chat_msg:
                self._append_chat_msg(next_chat_msg)
            else:
                pull = False

    def _send_chat_msg(self):
        msg = self.chat_input.text().strip()
        if not msg:
            return

        self.chat_input.clear()
        self._scroll_chat_bottom()
        self.chat_manager.send_msg(msg)

    def _append_chat_msg(self, msg: str):
        self.chat_view.append(msg)
        self._scroll_chat_bottom()

    def _scroll_chat_bottom(self):
        sb = self.chat_view.verticalScrollBar()
        sb.setValue(sb.maximum())

    # -----------------------------
    # Table updates
    # -----------------------------
    def _update_connections(self):
        rows = []
        proto_choices = ["TCP", "UDP"]
        states_tcp = ["ESTABLISHED", "SYN_SENT", "CLOSE_WAIT", "TIME_WAIT"]
        processes = ["python.exe", "firefox.exe", "discord.exe", "chore.exe", "pycharm64.exe", "ssh.exe"]

        for _ in range(10):
            proto = random.choice(proto_choices)
            local = f"{self._vpn_ip}:{random.randint(1024, 65535)}"
            remote = f"{random.choice(['8.8.8.8', '1.1.1.1', '52.94.236.248', '172.217.22.14'])}:{random.randint(80, 65535)}"
            state = random.choice(states_tcp) if proto == "TCP" else "-"
            pid = str(random.randint(200, 12000))
            proc = random.choice(processes)

            rows.append((proto, local, remote, state, pid, proc))

        self.net_table.setRowCount(len(rows))

        for row_index, row_values in enumerate(rows):
            for col_index, value in enumerate(row_values):
                item = QTableWidgetItem(value)

                if col_index in (1, 2):
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

                self.net_table.setItem(row_index, col_index, item)

    # -----------------------------
    # tick - refresh
    # -----------------------------
    def _start_tick_iterations(self):
        self.tick_timer = QTimer(self)
        self.tick_timer.setInterval(General.TICK_PERIOD_MS.value)
        self.tick_timer.timeout.connect(self._tick)
        self.tick_timer.start()

    def _tick(self):
        new_packet_value = random.randint(10, 90) if self._connected else random.randint(0, 5)

        if self._time <= 60:
            if not self._chart_animation_enabled:
                self._traffic_chart.setAnimationOptions(QChart.SeriesAnimations)
                self._chart_animation_enabled = True
        else:
            if self._chart_animation_enabled:
                self._traffic_chart.setAnimationOptions(QChart.NoAnimation)
                self._chart_animation_enabled = False

            self._traffic_axis_x.setRange(self._time - 60, self._time)

        self.series.append(self._time, new_packet_value)

        if self.series.count() > 60:
            self.series.removePoints(0, self.series.count() - 60)

        if random.random() < 0.05:
            self._connected_users = max(1, self._connected_users + random.randint(-1, 2))
            self.card_users.value_label.setText(str(self._connected_users))

        self._tcp_conns = max(0, self._tcp_conns + random.randint(-1, 2))
        self._udp_conns = max(0, self._udp_conns + random.randint(-1, 2))

        self.card_tcp.value_label.setText(str(self._tcp_conns))
        self.card_udp.value_label.setText(str(self._udp_conns))

        self._update_connections()

        self._pull_to_chat()

        self._time += 1
