from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QGridLayout, QPushButton
)
from PySide6.QtCore import Qt, QTimer, QMargins
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtGui import QPainter, QPen, QColor, QPixmap

import random

from src.securemesh.client.gui.widgets.card_frame import CardFrame


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # כותרת עליונה + סטטוס + כפתור החלפת רקע
        header_layout = QHBoxLayout()

        title = QLabel("לוח בקרה – תעבורת רשת SecureMesh")
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

        grid = QGridLayout()
        grid.setSpacing(10)

        # כרטיס – גרף תעבורה
        traffic_card = CardFrame("תעבורת רשת (Packets/sec)")
        self.traffic_chart_view = self._create_line_chart("Packets/sec")
        traffic_card.content_layout.addWidget(self.traffic_chart_view)

        # כרטיס – מקורות נפוצים
        sources_card = CardFrame("מקורות נפוצים")
        self.sources_label = QLabel(
            "1. 192.168.1.1 – 340 pkt\n"
            "2. 8.8.8.8 – 190 pkt\n"
            "3. 1.1.1.1 – 122 pkt"
        )
        self.sources_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        sources_card.content_layout.addWidget(self.sources_label)

        # כרטיס – אירועי אבטחה
        attacks_card = CardFrame("אירועי אבטחה")
        self.arp_alerts_label = QLabel("ARP Spoofing Attempts: 0")
        self.syn_alerts_label = QLabel("SYN Flood Alerts: 0")
        self.arp_alerts_label.setObjectName("metricLabel")
        self.syn_alerts_label.setObjectName("metricLabel")
        attacks_card.content_layout.addWidget(self.arp_alerts_label)
        attacks_card.content_layout.addWidget(self.syn_alerts_label)

        # כרטיס – לוג בזמן אמת
        log_card = CardFrame("לוג בזמן אמת")
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setObjectName("logView")
        log_card.content_layout.addWidget(self.log_edit)

        # שורת מדדים קטנים
        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)

        self.total_pkts_card = self._create_metric_card("Total Packets", "0")
        self.blocked_pkts_card = self._create_metric_card("Blocked", "0")
        self.active_conns_card = self._create_metric_card("Active Connections", "0")

        stats_row.addWidget(self.total_pkts_card)
        stats_row.addWidget(self.blocked_pkts_card)
        stats_row.addWidget(self.active_conns_card)

        stats_container = QWidget()
        stats_container.setLayout(stats_row)

        # 🔻 שורה תחתונה חדשה: לוגים משמאל, לוגו מימין 🔻
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)

        # לוגים – לוקחים יותר מקום בציר X
        log_card.setMinimumWidth(600)
        bottom_layout.addWidget(log_card, 3)

        # כרטיס תמונה ללוגו
        image_card = CardFrame("SecureMesh")
        logo_label = QLabel()

        pix = QPixmap("assets/SecureMesh_logo.png")
        if not pix.isNull():
            pix_scaled = pix.scaled(
                180, 180,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            logo_label.setPixmap(pix_scaled)

        logo_label.setAlignment(Qt.AlignCenter)

        image_card.content_layout.addStretch()
        image_card.content_layout.addWidget(logo_label)
        image_card.content_layout.addStretch()

        bottom_layout.addWidget(image_card, 1)

        # שיבוץ כל הרכיבים ב־Grid
        grid.addWidget(traffic_card, 0, 0, 2, 2)
        grid.addWidget(sources_card, 0, 2, 1, 1)
        grid.addWidget(attacks_card, 1, 2, 1, 1)
        grid.addWidget(stats_container, 2, 0, 1, 3)
        grid.addLayout(bottom_layout, 3, 0, 1, 3)

        main_layout.addLayout(grid)

        # סטייט דמו
        self._init_demo_state()

    def _create_line_chart(self, y_title: str) -> QChartView:
        self.series = QLineSeries()

        # צבע קו ניאון כחול
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
        view.setMinimumHeight(220)
        return view

    def _create_metric_card(self, title: str, value: str) -> QWidget:
        card = CardFrame(title)
        value_label = QLabel(value)
        value_label.setObjectName("metricValue")
        value_label.setAlignment(Qt.AlignCenter)
        card.content_layout.addWidget(value_label)
        card.setMinimumHeight(80)
        card.value_label = value_label
        return card

    def _init_demo_state(self):
        self._time = 0
        self._total_packets = 0
        self._blocked_packets = 0
        self._active_conns = 3
        self._arp_events = 0
        self._syn_events = 0

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._update_demo_data)
        self.timer.start()

    def _update_demo_data(self):
        self._time += 1
        packets = random.randint(10, 80)
        blocked = random.randint(0, 10)

        self._total_packets += packets
        self._blocked_packets += blocked
        self._active_conns = max(1, self._active_conns + random.randint(-1, 1))

        # עדכון גרף
        self.series.append(self._time, packets)
        if self.series.count() > 60:
            self.series.removePoints(0, self.series.count() - 60)

        # עדכון מדדים
        self.total_pkts_card.value_label.setText(str(self._total_packets))
        self.blocked_pkts_card.value_label.setText(str(self._blocked_packets))
        self.active_conns_card.value_label.setText(str(self._active_conns))

        # אירועי אבטחה דמו
        if random.random() < 0.1:
            self._arp_events += 1
            self.log_edit.append("⚠ ARP spoofing attempt detected and blocked.")
        if random.random() < 0.07:
            self._syn_events += 1
            self.log_edit.append("⚠ SYN flood pattern detected – rate limiting enabled.")

        self.arp_alerts_label.setText(f"ARP Spoofing Attempts: {self._arp_events}")
        self.syn_alerts_label.setText(f"SYN Flood Alerts: {self._syn_events}")

        # Scroll אוטומטי ללמטה בלוג
        sb = self.log_edit.verticalScrollBar()
        sb.setValue(sb.maximum())
