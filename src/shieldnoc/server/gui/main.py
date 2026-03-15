import sys

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton
)
from PySide6.QtCore import Qt

from shieldnoc.server.gui.ui.background import BackgroundLayer
from shieldnoc.server.gui.ui.style import SERVER_STYLE_SHEET
from shieldnoc.server.gui.pages.dashboard_page import ServerDashboardPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShieldNOC Server")
        self.resize(1400, 820)

        central = QWidget()
        self.setCentralWidget(central)
        central.setAttribute(Qt.WA_StyledBackground, False)  # type: ignore
        central.setStyleSheet("background: transparent;")

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        top = QHBoxLayout()
        top.setContentsMargins(12, 8, 12, 8)
        top.setSpacing(8)

        app_label = QLabel("ShieldNOC Server")
        app_label.setObjectName("appTitle")

        btn_bg = QPushButton("Background")
        btn_bg.setObjectName("topBarButton")

        top.addWidget(app_label)
        top.addStretch(1)
        top.addWidget(btn_bg)
        root.addLayout(top)

        # dashboard page
        self.page = ServerDashboardPage()
        root.addWidget(self.page, 1)

        # רקע: Background layer
        self.bg_layer = BackgroundLayer(self)
        self.bg_layer.lower()
        btn_bg.clicked.connect(self.bg_layer.next_background)

        self.setStyleSheet(SERVER_STYLE_SHEET)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg_layer.resize(self.size())


def gui_main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    gui_main()
