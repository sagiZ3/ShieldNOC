from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel


class CardFrame(QFrame):
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        if title:
            title_label = QLabel(title)
            title_label.setObjectName("cardTitle")
            layout.addWidget(title_label)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(6)
        layout.addLayout(self.content_layout)
