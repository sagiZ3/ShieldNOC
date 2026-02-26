from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGridLayout,
    QLineEdit, QCheckBox, QHBoxLayout, QPushButton
)
from PySide6.QtCore import Signal

from src.securemesh.client.gui.widgets.card_frame import CardFrame


class ConnectPage(QWidget):
    connect_requested = Signal(str, int, dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        header = QLabel("לוח הגדרות – SecureMesh Client")
        header.setObjectName("pageTitle")
        subtitle = QLabel("הגדר שרת, בחר מנגנוני הגנה ולחץ על התחברות.")
        subtitle.setObjectName("pageSubtitle")

        main_layout.addWidget(header)
        main_layout.addWidget(subtitle)

        # כרטיס הגדרות שרת
        server_card = CardFrame("הגדרות שרת")
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(10)

        ip_label = QLabel("Server IP:")
        self.ip_edit = QLineEdit("127.0.0.1")
        port_label = QLabel("Port:")
        self.port_edit = QLineEdit("9000")

        form_layout.addWidget(ip_label, 0, 0)
        form_layout.addWidget(self.ip_edit, 0, 1)
        form_layout.addWidget(port_label, 1, 0)
        form_layout.addWidget(self.port_edit, 1, 1)

        server_card.content_layout.addLayout(form_layout)

        # כרטיס העדפות הגנה
        protections_card = CardFrame("העדפות הגנה")
        self.cb_arp = QCheckBox("הפעל הגנה מפני ARP Spoofing")
        self.cb_syn = QCheckBox("הפעל זיהוי SYN Flood")
        self.cb_logs = QCheckBox("שלח לוגים מפורטים לשרת")
        self.cb_autostart = QCheckBox("הפעל אוטומטית עם עליית המחשב")

        for cb in (self.cb_arp, self.cb_syn, self.cb_logs, self.cb_autostart):
            cb.setChecked(True)
            protections_card.content_layout.addWidget(cb)

        # שורת כפתור התחברות + סטטוס
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)

        self.status_label = QLabel("לא מחובר")
        self.status_label.setObjectName("statusDisconnected")

        self.connect_button = QPushButton("Connect to SecureMesh")
        self.connect_button.setObjectName("primaryButton")
        self.connect_button.clicked.connect(self.on_connect_clicked)

        bottom_layout.addWidget(self.status_label)
        bottom_layout.addWidget(self.connect_button)

        main_layout.addWidget(server_card)
        main_layout.addWidget(protections_card)
        main_layout.addStretch(1)
        main_layout.addLayout(bottom_layout)

    def on_connect_clicked(self):
        ip = self.ip_edit.text().strip()
        try:
            port = int(self.port_edit.text().strip())
        except ValueError:
            self._set_status("Port לא חוקי", "statusError")
            return

        options = {
            "arp": self.cb_arp.isChecked(),
            "syn": self.cb_syn.isChecked(),
            "logs": self.cb_logs.isChecked(),
            "autostart": self.cb_autostart.isChecked(),
        }

        self._set_status("מתחבר...", "statusConnecting")
        self.connect_requested.emit(ip, port, options)

    def _set_status(self, text: str, object_name: str):
        self.status_label.setText(text)
        self.status_label.setObjectName(object_name)
        # טריק קטן כדי שה־stylesheet יתעדכן
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def set_connected(self, ok: bool):
        if ok:
            self._set_status("מחובר ל־SecureMesh", "statusConnected")
        else:
            self._set_status("חיבור נכשל", "statusError")
