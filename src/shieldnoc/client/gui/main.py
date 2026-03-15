import sys

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget
)
from PySide6.QtCore import Qt, QTimer

from shieldnoc.client.gui.ui.style import STYLE_SHEET
from shieldnoc.client.gui.ui.background import BackgroundLayer
from shieldnoc.client.gui.pages.connect_page import ConnectPage
from shieldnoc.client.gui.pages.dashboard_page import DashboardPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShieldNOC Client")
        self.resize(1200, 720)

        self._is_connected = False  # שינוי: סטייט חיבור לשמירה לאורך מעבר דפים

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

        # Stack
        self.stack = QStackedWidget()
        root.addWidget(self.stack)

        self.page_settings = ConnectPage()
        self.page_dash = DashboardPage()

        self.stack.addWidget(self.page_settings)
        self.stack.addWidget(self.page_dash)

        self.btn_settings.clicked.connect(self._go_settings)
        self.btn_dash.clicked.connect(self._go_dashboard)

        # Background layer
        self.bg_layer = BackgroundLayer(self)
        self.bg_layer.lower()

        # Wiring
        self.page_settings.connect_requested.connect(self._handle_connect)
        self.page_settings.vpn_ip_changed.connect(self.page_dash.set_vpn_ip)
        self.page_settings.bg_change_requested.connect(self.bg_layer.next_background)

        # Logo path placeholder
        self.page_dash.set_logo_path("assets/ShieldNOC_logo.png")

        self.setStyleSheet(STYLE_SHEET)
        self.stack.setCurrentWidget(self.page_settings)

        # Sync initial status
        self._sync_connect_status_label()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg_layer.resize(self.size())

    def _go_settings(self):
        self.stack.setCurrentWidget(self.page_settings)
        self._sync_connect_status_label()

    def _go_dashboard(self):
        self.stack.setCurrentWidget(self.page_dash)
        self._sync_connect_status_label()

    def _sync_connect_status_label(self):
        # שינוי: כשהמשתמש חוזר לדף ההגדרות, הסטטוס נשאר נכון בהתאם לסטייט
        if self._is_connected:
            self.page_settings.set_connected(True)
        else:
            # אם לא מחובר - לא "מתחבר" סתם; תמיד נשאר "לא מחובר"
            self.page_settings.set_connected(False)

    def _handle_connect(self, ip: str, port: int):
        # שינוי: סטטוס מתעדכן מיד לדף ההגדרות וגם לדשבורד
        self.page_settings.set_connecting()
        self.page_dash.set_connection_state("connecting")

        QTimer.singleShot(450, lambda: self._after_connect(True))

    def _after_connect(self, ok: bool):
        self._is_connected = ok
        self.page_settings.set_connected(ok)

        if ok:
            self.page_dash.set_connection_state("connected")
            self.stack.setCurrentWidget(self.page_dash)
        else:
            self.page_dash.set_connection_state("disconnected")

    def closeEvent(self, event):
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()