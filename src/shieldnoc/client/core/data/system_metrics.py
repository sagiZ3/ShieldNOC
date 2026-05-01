import subprocess

from dataclasses import dataclass


@dataclass(frozen=True)
class ClientInfo:
    vpn_ip: str
    mac: str
    host: str
    hostname: str
    last_seen: str
    status: str


def get_mac_addr():
    pass

def _run_cmd(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)
