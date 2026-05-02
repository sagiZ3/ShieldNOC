import subprocess

from dataclasses import dataclass


def get_mac_addr() -> str:
    pass

def get_host() -> str:
    pass

def get_hostname() -> str:
    pass

def _run_cmd(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)
