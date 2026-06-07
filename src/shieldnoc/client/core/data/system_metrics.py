import subprocess

import psutil
import platform

from shieldnoc.logging_config import logger


def get_mac_addr() -> str:  # TODO: edit to make a real function use
    """
    Retrieves the system MAC address.

    :return: Device MAC address.
    """

    return "AA:BB:CC:DD:EE:FF"

def get_os() -> str:  # TODO: edit to make a real function use
    """
    Retrieves the operating system name.

    :return: Operating system name.
    """

    system = platform.system()
    release = platform.release()

    return f"{system} {release}"

def get_hostname() -> str:
    """
    Retrieves the system hostname.

    :return: Device hostname.
    """

    return _run_cmd(["hostname"], capture_output=True)

def get_tcp_connections_amount() -> int:
    """
    Retrieves the amount of TCP connections.

    :return: Amount of TCP connections.
    """

    connections = psutil.net_connections(kind="tcp")
    return sum(1 for c in connections if c.status == psutil.CONN_ESTABLISHED)

def get_udp_sockets_amount() -> int:
    """
    Retrieves the amount of UDP connections.

    :return: Amount of UDP connections.
    """

    connections = psutil.net_connections(kind="udp")
    return sum(1 for _ in connections)

def _run_cmd(cmd: list[str], capture_output=False, **kwargs) -> str | None:
    """
    Runs a system command and optionally captures its output.

    :return: Command output if captured, otherwise None.
    """

    try:
        result = subprocess.run(
            cmd, check=True, text=True, capture_output=capture_output,
            encoding="utf-8", errors="replace", **kwargs
        )

    except Exception as e:
        logger.error(f"error with running the following command: '{cmd}':\n\t- {e}")
        return None

    return result.stdout.strip() if capture_output else None
