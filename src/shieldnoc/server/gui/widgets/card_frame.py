# src/shieldnoc/client/gui/widgets/card_frame.py
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel


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