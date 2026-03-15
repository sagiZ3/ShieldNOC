SERVER_STYLE_SHEET = """
QWidget {
    background-color: #050814;
    color: #e7f0ff;
    font-family: 'Segoe UI', 'Rubik', sans-serif;
}

/* Titles */
#appTitle {
    font-size: 20px;
    font-weight: 600;
    padding: 10px 16px;
    color: #f7c948;
    text-shadow: 0 0 10px #f7c948;
}
#pageTitle {
    font-size: 18px;
    font-weight: 600;
    color: #52b6ff;
    text-shadow: 0 0 12px #1e6fff;
}
#pageSubtitle {
    color: #a7b3d5;
    margin-bottom: 6px;
}

/* Cards */
#card {
    background-color: rgba(5, 10, 30, 0.92);
    border-radius: 16px;
    border: 1px solid #1b3358;
    box-shadow: 0 0 18px rgba(0, 200, 255, 0.12);
}
#cardTitle {
    font-size: 14px;
    font-weight: 600;
    color: #f7f9ff;
}

/* Inputs */
QLineEdit {
    background-color: rgba(3, 6, 18, 0.9);
    border: 1px solid #2a3c5f;
    border-radius: 8px;
    padding: 6px 8px;
    color: #e7f0ff;
}
QLineEdit:focus {
    border: 1px solid #52b6ff;
    box-shadow: 0 0 12px rgba(82, 182, 255, 0.7);
}

/* Buttons */
#primaryButton {
    background-color: #f7c948;
    color: #1e90ff;
    text-shadow: 0 0 10px rgba(82, 182, 255, 0.8);
    border-radius: 12px;
    padding: 10px 18px;
    font-weight: 600;
    border: 1px solid #52b6ff;
    box-shadow: 0 0 15px rgba(82, 182, 255, 0.6);
}
#primaryButton:hover {
    background-color: #ffe27a;
}
#primaryButton:pressed {
    background-color: #f1be2a;
    border: 1px solid #7cc8ff;
}

#secondaryButton {
    background-color: transparent;
    border-radius: 12px;
    padding: 10px 14px;
    font-weight: 600;
    border: 1px solid #52b6ff;
    color: #52b6ff;
}
#secondaryButton:hover {
    background-color: rgba(16, 48, 96, 0.7);
}
#secondaryButton:pressed {
    background-color: rgba(16, 48, 96, 0.95);
    border: 1px solid #9ad8ff;
}

#topBarButton {
    background-color: transparent;
    border: none;
    padding: 8px 12px;
    color: #cdd7ff;
}
#topBarButton:hover {
    background-color: rgba(15, 32, 72, 0.9);
    border-radius: 8px;
}
#topBarButton:pressed {
    background-color: rgba(15, 32, 72, 1.0);
    border-radius: 8px;
}

/* Connection badge (Dashboard) */
#badgeConnected {
    background-color: #00d1a3;
    color: #050814;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
}
#badgeConnecting {
    background-color: #ffeaa7;
    color: #050814;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
}
#badgeDisconnected {
    background-color: #ff7675;
    color: #050814;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
}

/* Settings: connect status text (requested Hebrew + persistent) */
#connectStatusDisconnected {
    color: #ff3b3b;
    font-weight: 700;
}
#connectStatusConnecting {
    color: #ffeaa7;
    font-weight: 700;
}
#connectStatusConnected {
    color: #00ff85;
    font-weight: 800;
}

/* Feedback badges (settings actions) */
#badgeInfo {
    background-color: rgba(82, 182, 255, 0.18);
    color: #cfe3ff;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    border: 1px solid rgba(82, 182, 255, 0.35);
}
#badgeOk {
    background-color: rgba(0, 209, 163, 0.22);
    color: #a9ffea;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    border: 1px solid rgba(0, 209, 163, 0.35);
}

/* Log */
#logView {
    background-color: rgba(2, 6, 25, 0.85);
    border-radius: 10px;
    border: 1px solid #283458;
}

/* Metrics */
#metricValue {
    font-size: 20px;
    font-weight: 800;
    color: #f7c948;
    text-align: center;
}
#metricLabel {
    font-size: 12px;
    color: #cbd4ff;
}

/* Switch background button */
#switchBgButton {
    background-color: transparent;
    border-radius: 999px;
    border: 1px solid #52b6ff;
    padding: 6px 12px;
    color: #52b6ff;
    font-size: 11px;
}
#switchBgButton:hover {
    background-color: rgba(16, 48, 96, 0.7);
}
#switchBgButton:pressed {
    background-color: rgba(16, 48, 96, 0.95);
    border: 1px solid #9ad8ff;
}

/* Tables */
QTableWidget {
    background-color: rgba(2, 6, 25, 0.75);
    border: 1px solid #283458;
    border-radius: 10px;
    gridline-color: #283458;
}
QHeaderView::section {
    background-color: rgba(10, 20, 50, 0.9);
    padding: 6px;
    border: none;
    color: #cfe3ff;
    font-weight: 600;
}
QTableWidget::item {
    padding: 6px;
}
QTableWidget::item:selected {
    background-color: rgba(82, 182, 255, 0.25);
}

/* Chat */
#chatView {
    background-color: rgba(2, 6, 25, 0.85);
    border-radius: 10px;
    border: 1px solid #283458;
}
#chatInputRow QPushButton {
    padding: 8px 12px;
}

/* General */
QLabel {
    font-size: 12px;
}

/* Server-specific titles */
#serverTitle {
    font-size: 18px;
    font-weight: 700;
    color: #f7c948;
    text-shadow: 0 0 12px #f7c948;
}

/* Alert badges */
#badgeCritical {
    background-color: #ff3b3b;
    color: #050814;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
}
#badgeWarn {
    background-color: #ffeaa7;
    color: #050814;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
}

/* Log view variant */
#serverLogView {
    background-color: rgba(2, 6, 25, 0.9);
    border-radius: 10px;
    border: 1px solid #283458;
}

/* Client list */
#clientList {
    background-color: rgba(2, 6, 25, 0.85);
    border-radius: 10px;
    border: 1px solid #283458;
}
"""