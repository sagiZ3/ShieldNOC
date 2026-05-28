import subprocess

from shieldnoc.logging_config import logger


def get_mac_addr() -> str:  # TODO: edit to make a real function use
    """
    Retrieves the system MAC address.

    :return: Device MAC address.
    """

    return "B8:1E:A4:D2:3D:51"

def get_os() -> str:  # TODO: edit to make a real function use
    """
    Retrieves the operating system name.

    :return: Operating system name.
    """

    return "WINDOWS 11"

def get_hostname() -> str:
    """
    Retrieves the system hostname.

    :return: Device hostname.
    """

    return _run_cmd(["hostname"], capture_output=True)

def _run_cmd(cmd: list[str], capture_output=False, **kwargs) -> str | None:
    """
    Runs a system command and optionally captures its output.

    :return: Command output if captured, otherwise None.
    """

    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=capture_output, **kwargs)

    except Exception as e:
        logger.error(f"error with running the following command: '{cmd}':\n\t- {e}")
        return None

    return result.stdout.strip() if capture_output else None
