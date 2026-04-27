from enum import Enum

class ClientField(Enum):
    PUBLIC_KEY = "public_key"
    VPN_IP = "vpn_ip"
    MAC = "mac"
    HOST = "host"
    HOSTNAME = "hostname"
    LAST_SEEN = "last_seen"
    STATUS = "status"
    IP_PREF = "ip_preference"

class ServerField(Enum):
    ID = "id"
    PRIVATE_KEY = "private_key"
    PUBLIC_KEY = "public_key"
    LAST_UPDATED = "last_updated"
