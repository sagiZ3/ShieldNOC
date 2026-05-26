import psutil

def get_cpu_usage() -> str:
    """
    Retrieves the current CPU usage.

    :return: Current CPU usage value.
    """

    return str(psutil.cpu_percent())

def get_ram_usage() -> str:
    """
    Retrieves the current RAM usage.

    :return: Current RAM usage value.
    """

    return str(psutil.virtual_memory().percent)

def get_packets_per_second():
    """
    Retrieves the current network packets per second rate.

    :return: Current packets per second value.
    """

    return 2
