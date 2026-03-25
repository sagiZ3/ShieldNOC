import subprocess

from shieldnoc.logging_config import logger

# TODO: needs to open a socket to the VPNManager with the server side for transporting related information
#  (e.g. Connected VPN Users <-> Changing the client VPN IP by request
class VPNManager:
    def __init__(self):
        pass

    @staticmethod
    def _run_cmd_cmd(cmd: list[str]) -> None:
        subprocess.run(cmd, check=True)
