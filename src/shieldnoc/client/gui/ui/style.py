STYLE_SHEET = """
QWidget {
    background-color: #050814;
    color: #e7f0ff;
    font-family: 'Segoe UI', 'Rubik', sans-serif;
}

/* כותרות כלליות */
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

/* כרטיסים */
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

/* שדות טקסט */
QLineEdit {
    background-color: rgba(3, 6, 18, 0.9);
    border: 1px solid #2a3c5f;
    border-radius: 8px;
    padding: 6px 8px;
}
QLineEdit:focus {
    border: 1px solid #52b6ff;
    box-shadow: 0 0 12px rgba(82, 182, 255, 0.7);
}

/* צ'קבוקסים – סגנון "Toggle" קטן */
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #52b6ff;
    background-color: transparent;
}
QCheckBox::indicator:checked {
    background-color: #52b6ff;
}

/* כפתורים */
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

/* סטטוס חיבור */
#statusDisconnected {
    color: #ff7675;
    font-weight: 500;
}
#statusConnecting {
    color: #ffeaa7;
    font-weight: 500;
}
#statusConnected {
    color: #00d1a3;
    font-weight: 500;
}
#statusError {
    color: #d63031;
    font-weight: 500;
}

/* באדג' חיבור */
#badgeConnected {
    background-color: #00d1a3;
    color: #050814;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
}

/* לוג */
#logView {
    background-color: rgba(2, 6, 25, 0.85);
    border-radius: 10px;
    border: 1px solid #283458;
}

/* מדדים */
#metricLabel {
    font-size: 13px;
    color: #cbd4ff;
}
#metricValue {
    font-size: 20px;
    font-weight: 700;
    color: #f7c948;
    text-align: center;
}

/* כפתור החלפת רקע */
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

/* טקסטים כללים בקישוט ניאון קל */
QLabel {
    font-size: 12px;
}
"""
