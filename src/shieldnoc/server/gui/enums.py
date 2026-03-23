from enum import Enum

class ImagesPaths(Enum):
    LOGO = 'gui/assets/ShieldNOC_logo.png'

    BACKGROUND1 = 'gui/assets/backgrounds/1.png'
    BACKGROUND2 = 'gui/assets/backgrounds/2.png'
    BACKGROUND3 = 'gui/assets/backgrounds/3.png'
    BACKGROUND4 = 'gui/assets/backgrounds/4.png'
    BACKGROUND5 = 'gui/assets/backgrounds/5.png'
    BACKGROUND6 = 'gui/assets/backgrounds/6.png'

    TOPOLOGY_SERVER = 'gui/assets/topology/server.png'
    TOPOLOGY_CLIENT = 'gui/assets/topology/pc.png'

class TrafficChart(Enum):
    TIME_WINDOW_SECONDS = 120  # 2 minutes window
    PACKETS_WINDOW = 1000