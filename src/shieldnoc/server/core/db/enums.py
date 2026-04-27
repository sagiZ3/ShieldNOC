from enum import Enum

class ClientField(Enum):
    PUB_KEY = "public_key"
    VPN_IP = "vpn_ip"
    MAC = "mac"
    HOST = "host"
    HOSTNAME = "hostname"
    LAST_SEEN = "last_seen"
    STATUS = "status"
    IP_PREF = "ip_preference"
