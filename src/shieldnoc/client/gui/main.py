import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget
from PySide6.QtCore import QTimer, Qt

from src.securemesh.client.gui.ui.style import STYLE_SHEET
from src.securemesh.client.gui.ui.background import BackgroundLayer

from src.securemesh.client.gui.pages.connect_page import ConnectPage
from src.securemesh.client.gui.pages.dashboard_page import DashboardPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SecureMesh Client")
        self.resize(1200, 720)

        # מרכז – Stack למסכים
        central = QWidget()
        self.setCentralWidget(central)
        central.setAttribute(Qt.WA_StyledBackground, False)
        central.setStyleSheet("background: transparent;")

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # טופ־בר
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(12, 8, 12, 8)
        top_bar.setSpacing(8)

        app_label = QLabel("SecureMesh Client")
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

        # Stack למסכים
        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack)

        self.connect_page = ConnectPage()
        self.dashboard_page = DashboardPage()

        self.stack.addWidget(self.connect_page)
        self.stack.addWidget(self.dashboard_page)

        # כפתורים למעבר מסכים
        self.home_btn.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.connect_page)
        )
        self.dashboard_btn.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.dashboard_page)
        )

        # חיבור אירוע התחברות – בהמשך תחליף בסוקט אמיתי
        self.connect_page.connect_requested.connect(self._handle_connect)

        # שכבת רקע מתחלף
        self.bg_layer = BackgroundLayer(self)
        self.bg_layer.lower()  # מתחת לכל

        # כפתור Change Background מתוך ה־Dashboard
        self.dashboard_page.switch_bg_btn.clicked.connect(self.bg_layer.next_background)

        # סטייל גלובלי
        self.setStyleSheet(STYLE_SHEET)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg_layer.resize(self.size())

    def _handle_connect(self, ip: str, port: int, options: dict):
        # כאן – חיבור אמיתי לשרת בהמשך.
        # עכשיו – סימולציה של התחברות מוצלחת אחרי 400 מ״ש.
        QTimer.singleShot(400, lambda: self._after_connect(True))

    def _after_connect(self, success: bool):
        self.connect_page.set_connected(success)
        if success:
            self.stack.setCurrentWidget(self.dashboard_page)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
