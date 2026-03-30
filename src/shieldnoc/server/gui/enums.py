from enum import Enum

class ImagesPaths(Enum):
    LOGO = 'shieldnoc/server/gui/assets/ShieldNOC_logo.png'

    BACKGROUND1 = 'shieldnoc/server/gui/assets/backgrounds/1.png'
    BACKGROUND2 = 'shieldnoc/server/gui/assets/backgrounds/2.png'
    BACKGROUND3 = 'shieldnoc/server/gui/assets/backgrounds/3.png'
    BACKGROUND4 = 'shieldnoc/server/gui/assets/backgrounds/4.png'
    BACKGROUND5 = 'shieldnoc/server/gui/assets/backgrounds/5.png'
    BACKGROUND6 = 'shieldnoc/server/gui/assets/backgrounds/6.png'

    TOPOLOGY_SERVER = 'shieldnoc/server/gui/assets/topology/server.png'
    TOPOLOGY_CLIENT = 'shieldnoc/server/gui/assets/topology/pc.png'

class TrafficChart(Enum):
    TIME_WINDOW_SECONDS = 120  # 2 minutes window
    PACKETS_WINDOW = 1000
