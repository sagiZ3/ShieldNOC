# src/shieldnoc/server/gui/ui/style.py
from src.shieldnoc.client.gui.ui.style import STYLE_SHEET as BASE_STYLE

SERVER_STYLE_SHEET = BASE_STYLE + """

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