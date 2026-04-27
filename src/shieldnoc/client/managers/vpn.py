import subprocess

from shieldnoc.logging_config import logger


class VPNManager:
    def __init__(self):
        pass

    @staticmethod
    def _run_cmd_cmd(cmd: list[str]) -> None:
        subprocess.run(cmd, check=True)
