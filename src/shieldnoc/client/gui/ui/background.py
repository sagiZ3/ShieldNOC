from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import Qt


class BackgroundLayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.backgrounds = [
            "assets/backgrounds/1.png",
            "assets/backgrounds/2.png",
            "assets/backgrounds/3.png",
            "assets/backgrounds/4.png",
            "assets/backgrounds/5.png",
            "assets/backgrounds/6.png",
        ]
        self.index = 0
        self.opacity = 0.12

        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAutoFillBackground(False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(self.opacity)

        if self.backgrounds:
            pix = QPixmap(self.backgrounds[self.index])
            if not pix.isNull():
                scaled = pix.scaled(
                    self.size(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
                painter.drawPixmap(0, 0, scaled)

        painter.end()

    def next_background(self):
        if self.backgrounds:
            self.index = (self.index + 1) % len(self.backgrounds)
            self.update()
