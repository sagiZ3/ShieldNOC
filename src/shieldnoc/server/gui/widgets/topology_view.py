import math

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QColor, QBrush, QPixmap, QPainter
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem, QGraphicsEllipseItem, QGraphicsLineItem
)


@dataclass(frozen=True)
class ClientInfo:
    key: str           # ייחודי, למשל VPN IP או MAC
    label: str = ""    # אופציונלי (לא חובה כרגע)


class TopologyView(QGraphicsView):
    def __init__(
        self,
        parent=None,
        server_icon_path="assets/server.png",
        client_icon_path="assets/pc.png",
    ):
        super().__init__(parent)

        self.setRenderHint(QPainter.Antialiasing, True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QGraphicsView.NoFrame)

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._server_pos = QPointF(0, 0)

        self._server_item = None
        self._server_fallback_circle = None

        self._client_items: dict[str, object] = {}
        self._lines: dict[str, QGraphicsLineItem] = {}

        self._line_pen = QPen(QColor("#52b6ff"))
        self._line_pen.setWidth(2)

        self._server_icon: QPixmap | None = None
        self._client_icon: QPixmap | None = None

        if server_icon_path:
            pix = QPixmap(server_icon_path)
            if not pix.isNull():
                self._server_icon = pix

        if client_icon_path:
            pix = QPixmap(client_icon_path)
            if not pix.isNull():
                self._client_icon = pix

        self._init_server()

    def _init_server(self):
        if self._server_icon is not None:
            item = QGraphicsPixmapItem(self._server_icon.scaled(
                72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            item.setOffset(-36, -36)
            item.setPos(self._server_pos)
            self._scene.addItem(item)
            self._server_item = item
            return

        circle = QGraphicsEllipseItem(-28, -28, 56, 56)
        circle.setBrush(QBrush(QColor("#f7c948")))
        circle.setPen(QPen(Qt.NoPen))
        circle.setPos(self._server_pos)
        self._scene.addItem(circle)
        self._server_fallback_circle = circle

    def set_clients(self, clients: list[ClientInfo]):
        wanted = {c.key for c in clients}
        existing = set(self._client_items.keys())

        for key in list(existing - wanted):
            self.remove_client(key)

        for c in clients:
            if c.key not in self._client_items:
                self.add_client(c)

        self._reflow()

    def add_client(self, client: ClientInfo):
        if client.key in self._client_items:
            return

        if self._client_icon is not None:
            node = QGraphicsPixmapItem(self._client_icon.scaled(
                44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            node.setOffset(-22, -22)
            self._scene.addItem(node)
            self._client_items[client.key] = node
        else:
            node = QGraphicsEllipseItem(-18, -18, 36, 36)
            node.setBrush(QBrush(QColor("#1e90ff")))
            node.setPen(QPen(Qt.NoPen))
            self._scene.addItem(node)
            self._client_items[client.key] = node

        line = QGraphicsLineItem()
        line.setPen(self._line_pen)
        self._scene.addItem(line)
        self._lines[client.key] = line

        self._reflow()

    def remove_client(self, key: str):
        node = self._client_items.pop(key, None)
        if node is not None:
            self._scene.removeItem(node)

        line = self._lines.pop(key, None)
        if line is not None:
            self._scene.removeItem(line)

        self._reflow()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit()

    def _fit(self):
        rect = self._scene.itemsBoundingRect().adjusted(-60, -60, 60, 60)
        if rect.isNull():
            return
        self.fitInView(rect, Qt.KeepAspectRatio)

    def _reflow(self):
        n = len(self._client_items)
        if n == 0:
            self._fit()
            return

        radius = 120 if n <= 8 else 160
        step = (2 * math.pi) / n

        keys = list(self._client_items.keys())
        for i, key in enumerate(keys):
            angle = i * step
            x = self._server_pos.x() + radius * math.cos(angle)
            y = self._server_pos.y() + radius * math.sin(angle)

            node = self._client_items[key]
            node.setPos(x, y)

            line = self._lines[key]
            line.setLine(self._server_pos.x(), self._server_pos.y(), x, y)

        self._fit()

    def set_icons(self, server_icon_path: str | None, client_icon_path: str | None):
        # טוען מחדש
        self._server_icon = None
        self._client_icon = None

        if server_icon_path:
            pix = QPixmap(server_icon_path)
            if not pix.isNull():
                self._server_icon = pix

        if client_icon_path:
            pix = QPixmap(client_icon_path)
            if not pix.isNull():
                self._client_icon = pix

        # מחליף את השרת
        if self._server_item is not None:
            self._scene.removeItem(self._server_item)
            self._server_item = None

        if self._server_fallback_circle is not None:
            self._scene.removeItem(self._server_fallback_circle)
            self._server_fallback_circle = None

        self._init_server()

        # מחליף את כל הלקוחות שכבר קיימים (חשוב!)
        existing = [ClientInfo(key=k, label="") for k in list(self._client_items.keys())]
        for k in list(self._client_items.keys()):
            self.remove_client(k)
        for c in existing:
            self.add_client(c)

        self._reflow()
