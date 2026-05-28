from enum import Enum

class ClientField(Enum):
    TABLE_NAME = "clients"
    PUBLIC_KEY = "public_key"
    VPN_IP = "vpn_ip"
    MAC = "mac"
    OS = "os"
    HOSTNAME = "hostname"
    LAST_SEEN = "last_seen"
    STATUS = "status"
    IP_PREF = "ip_preference"
