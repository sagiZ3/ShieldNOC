from dataclasses import dataclass

@dataclass(frozen=True)
class ClientInfo:
    vpn_ip: str
    mac: str
    host: str
    hostname: str
    last_seen: str
    status: str
