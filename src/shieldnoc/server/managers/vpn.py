import subprocess

from shieldnoc.logging_config import logger


class VPNManager:
    def __init__(self, wg_interface: str, lan_interface: str, wan_interface: str, config_path: str):
        self._wg_interface = wg_interface
        self._lan_interface = lan_interface
        self._wan_interface = wan_interface
        self._config_path = config_path

    def enable_ip_forwarding(self) -> None:
        self._run_terminal_cmd(["sysctl", "-w", "net.ipv4.ip_forward=1"])

    def disable_ip_forwarding(self) -> None:
        self._run_terminal_cmd(["sysctl", "-w", "net.ipv4.ip_forward=0"])

    def enable_nat(self) -> None:
        self._run_terminal_cmd([
            "iptables", "-A", "FORWARD",
            "-i", self._lan_interface,
            "-o", self._wan_interface,
            "-j", "ACCEPT"
        ])
        self._run_terminal_cmd([
            "iptables", "-A", "FORWARD",
            "-i", self._wan_interface,
            "-o", self._lan_interface,
            "-m", "state",
            "--state", "ESTABLISHED,RELATED",
            "-j", "ACCEPT"
        ])
        self._run_terminal_cmd([
            "iptables", "-t", "nat", "-A", "POSTROUTING",
            "-o", self._wan_interface,
            "-j", "MASQUERADE"
        ])

    def disable_nat(self) -> None:
        self._run_terminal_cmd([
            "iptables", "-D", "FORWARD",
            "-i", self._lan_interface,
            "-o", self._wan_interface,
            "-j", "ACCEPT"
        ])
        self._run_terminal_cmd([
            "iptables", "-D", "FORWARD",
            "-i", self._wan_interface,
            "-o", self._lan_interface,
            "-m", "state",
            "--state", "ESTABLISHED,RELATED",
            "-j", "ACCEPT"
        ])
        self._run_terminal_cmd([
            "iptables", "-t", "nat", "-D", "POSTROUTING",
            "-o", self._wan_interface,
            "-j", "MASQUERADE"
        ])

    def is_ip_forwarding_enabled(self) -> bool:
        result = subprocess.run(
            ["sysctl", "net.ipv4.ip_forward"],
            capture_output=True,
            text=True
        )
        return " = 1" in result.stdout

    def is_nat_enabled(self) -> bool:
        result = subprocess.run(
            ["iptables", "-t", "nat", "-S"],
            capture_output=True,
            text=True
        )
        return f"-o {self._wan_interface} -j MASQUERADE" in result.stdout

    def setup_server_networking(self) -> bool:
        self.enable_ip_forwarding()
        self.enable_nat()

        if not self.is_ip_forwarding_enabled():
            logger.error("IP forwarding is not enabled.")
            return False

        if not self.is_nat_enabled():
            logger.error("NAT is not enabled.")
            return False

        logger.info("Server networking configured successfully.")
        return True

    def teardown_server_networking(self) -> bool:
        self.disable_nat()
        self.disable_ip_forwarding()

        if self.is_ip_forwarding_enabled():
            logger.error("Problem with disable IP forwarding.")
            return False

        if self.is_nat_enabled():
            logger.error("Problem with disable NAT.")
            return False

        logger.info("Server networking teardown successfully.")
        return True

    def load_config(self) -> None:
        pass

    def save_config(self) -> None:
        pass

    def start_vpn(self) -> None:
        pass

    def stop_vpn(self) -> None:
        pass

    def restart_vpn(self) -> None:
        pass

    def is_vpn_running(self) -> bool:
        pass

    def get_vpn_status(self) -> dict:
        pass

    def add_peer(self) -> None:
        pass

    def remove_peer(self) -> None:
        pass

    def list_peers(self) -> list:
        pass


    @staticmethod
    def _run_terminal_cmd(cmd: list[str]) -> None:
        subprocess.run(cmd, check=True)
