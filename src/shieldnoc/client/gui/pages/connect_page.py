from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGridLayout,
    QLineEdit,
)

from shieldnoc.client.gui.widgets.card_frame import CardFrame
from shieldnoc import protocol


class ConnectPage(QWidget):
    connect_requested = Signal(str, int)
    vpn_ip_changed = Signal(str)
    bg_change_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Root layout
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # Header
        title = QLabel("Settings — Client")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Configure server address, client settings, and UI preferences.")
        subtitle.setObjectName("pageSubtitle")

        root.addWidget(title)
        root.addWidget(subtitle)

        # Server settings card
        server_card = CardFrame("Server Settings")
        server_form = QGridLayout()
        server_form.setHorizontalSpacing(12)
        server_form.setVerticalSpacing(10)

        self.ip_edit = QLineEdit(str(protocol.SERVER_IP))
        self.port_edit = QLineEdit(str(protocol.CONNECTION_PORT))

        self.ip_edit.setLayoutDirection(Qt.LeftToRight)
        self.port_edit.setLayoutDirection(Qt.LeftToRight)

        server_form.addWidget(QLabel("Server IP:"), 0, 0)
        server_form.addWidget(self.ip_edit, 0, 1)
        server_form.addWidget(QLabel("Port:"), 1, 0)
        server_form.addWidget(self.port_edit, 1, 1)

        server_card.content_layout.addLayout(server_form)
        root.addWidget(server_card)

        # Client settings card
        client_card = CardFrame("Client Settings")
        client_form = QGridLayout()
        client_form.setHorizontalSpacing(12)
        client_form.setVerticalSpacing(10)

        self.vpn_ip_edit = QLineEdit("10.0.0.100")
        self.vpn_ip_edit.setLayoutDirection(Qt.LeftToRight)

        self.btn_apply_vpn = QPushButton("Apply Client VPN IP")
        self.btn_apply_vpn.setObjectName("secondaryButton")
        self.btn_apply_vpn.clicked.connect(self._apply_vpn_ip)

        self.client_action_badge = QLabel("Idle")
        self.client_action_badge.setObjectName("badgeInfo")

        client_form.addWidget(QLabel("Client VPN IP:"), 0, 0)
        client_form.addWidget(self.vpn_ip_edit, 0, 1)
        client_form.addWidget(self.client_action_badge, 1, 0)
        client_form.addWidget(self.btn_apply_vpn, 1, 1)

        client_card.content_layout.addLayout(client_form)
        root.addWidget(client_card)

        # UI settings card
        ui_card = CardFrame("UI Settings")
        ui_form = QGridLayout()
        ui_form.setHorizontalSpacing(12)
        ui_form.setVerticalSpacing(10)

        self.btn_bg = QPushButton("Change Background")
        self.btn_bg.setObjectName("switchBgButton")
        self.btn_bg.clicked.connect(self._change_bg_clicked)

        self.ui_action_badge = QLabel("Idle")
        self.ui_action_badge.setObjectName("badgeInfo")

        ui_form.addWidget(QLabel("Background:"), 0, 0)
        ui_form.addWidget(self.ui_action_badge, 1, 0)
        ui_form.addWidget(self.btn_bg, 1, 1)

        ui_card.content_layout.addLayout(ui_form)
        root.addWidget(ui_card)

        # Bottom row
        bottom = QHBoxLayout()
        bottom.addStretch(1)

        self.connect_status = QLabel("לא מחובר")
        self.connect_status.setObjectName("connectStatusDisconnected")

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setObjectName("primaryButton")
        self.connect_btn.clicked.connect(self._connect_clicked)

        bottom.addWidget(self.connect_status)
        bottom.addWidget(self.connect_btn)

        root.addStretch(1)
        root.addLayout(bottom)

    def _connect_clicked(self):
        ip = self.ip_edit.text().strip()

        try:
            port = int(self.port_edit.text().strip())
        except ValueError:
            self._set_connect_status("לא מחובר", "connectStatusDisconnected")
            return

        self._set_connect_status("מתחבר...", "connectStatusConnecting")
        self.connect_requested.emit(ip, port)

    def _pop_msg(self):  # TODO: edit and integrate
        label = QLabel("Error!\nYou can't do that", self)
        label.setStyleSheet("""
            background-color: #1f2933;      /* dark modern background */
            color: #f9fafb;                 /* soft white text */
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #ef4444;      /* red accent */
            font-size: 14px;
        """)
        label.adjustSize()
        label.move(self.width() - label.width() - 500, 200)
        label.show()

        QTimer.singleShot(1500, label.deleteLater)

    def _apply_vpn_ip(self):
        ip = self.vpn_ip_edit.text().strip()
        if not ip:
            return

        self.vpn_ip_changed.emit(ip)

        self._set_badge(self.client_action_badge, "Applied", "badgeOk")
        QTimer.singleShot(1600, lambda: self._set_badge(self.client_action_badge, "Idle", "badgeInfo"))

    def _change_bg_clicked(self):
        self.bg_change_requested.emit()

        self._set_badge(self.ui_action_badge, "Background Updated", "badgeOk")
        QTimer.singleShot(1600, lambda: self._set_badge(self.ui_action_badge, "Idle", "badgeInfo"))

    def set_connected(self, ok: bool):
        if ok:
            self._set_connect_status("מחובר ל-ShieldNOC", "connectStatusConnected")
        else:
            self._set_connect_status("לא מחובר", "connectStatusDisconnected")

    def set_connecting(self):
        self._set_connect_status("מתחבר...", "connectStatusConnecting")

    def _set_connect_status(self, text: str, object_name: str):
        self.connect_status.setText(text)
        self.connect_status.setObjectName(object_name)
        self.connect_status.style().unpolish(self.connect_status)
        self.connect_status.style().polish(self.connect_status)

    def _set_badge(self, label: QLabel, text: str, object_name: str):
        label.setText(text)
        label.setObjectName(object_name)
        label.style().unpolish(label)
        label.style().polish(label)