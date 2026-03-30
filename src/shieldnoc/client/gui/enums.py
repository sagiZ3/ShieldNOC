from enum import Enum

class ImagesPaths(Enum):
    LOGO = 'shieldnoc/client/gui/assets/ShieldNOC_logo.png'

    BACKGROUND1 = 'shieldnoc/client/gui/assets/backgrounds/1.png'
    BACKGROUND2 = 'shieldnoc/client/gui/assets/backgrounds/2.png'
    BACKGROUND3 = 'shieldnoc/client/gui/assets/backgrounds/3.png'
    BACKGROUND4 = 'shieldnoc/client/gui/assets/backgrounds/4.png'
    BACKGROUND5 = 'shieldnoc/client/gui/assets/backgrounds/5.png'
    BACKGROUND6 = 'shieldnoc/client/gui/assets/backgrounds/6.png'

class TrafficChart(Enum):
    TIME_WINDOW_SECONDS = 120  # 2 minutes window
    PACKETS_WINDOW = 1000

class General(Enum):
    TICK_PERIOD_MS = 1000
