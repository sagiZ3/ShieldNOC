import subprocess

from shieldnoc.logging_config import logger


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)

def enable_router_nat_linux(lan_if: str, wan_if: str) -> bool:
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"])
    run(["iptables", "-A", "FORWARD", "-i", lan_if, "-o", wan_if, "-j", "ACCEPT"])
    run(["iptables", "-A", "FORWARD", "-i", wan_if, "-o", lan_if, "-m", "state",
         "--state", "ESTABLISHED,RELATED", "-j", "ACCEPT"])
    run(["iptables", "-t", "nat", "-A", "POSTROUTING", "-o", wan_if, "-j", "MASQUERADE"])

    if not is_ip_forwarding_enabled():
        return False
    logger.error("MSG")
    if not is_nat_enabled(wan_if):
        logger.error("MSG")
        return False
    logger.info("GOOD MSG")
    return True

def disable_router_nat_linux(lan_if: str, wan_if: str) -> None:
    # מוחק בדיוק את אותם חוקים (לפי סדר ההוספה)
    run(["iptables", "-D", "FORWARD", "-i", lan_if, "-o", wan_if, "-j", "ACCEPT"])
    run(["iptables", "-D", "FORWARD", "-i", wan_if, "-o", lan_if, "-m", "state",
         "--state", "ESTABLISHED,RELATED", "-j", "ACCEPT"])
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan_if, "-j", "MASQUERADE"])
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"])

def is_ip_forwarding_enabled():
    result = subprocess.run(
        ["sysctl", "net.ipv4.ip_forward"],
        capture_output=True,
        text=True
    )
    return " = 1" in result.stdout

def is_nat_enabled(wan_if):
    result = subprocess.run(
        ["iptables", "-t", "nat", "-S"],
        capture_output=True,
        text=True
    )
    return f"-o {wan_if} -j MASQUERADE" in result.stdout
