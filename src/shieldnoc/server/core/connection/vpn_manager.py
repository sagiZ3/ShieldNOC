import subprocess
import base64

from pathlib import Path
from random import randint

from shieldnoc.logging_config import logger

class VPNManager:
    WG_INTERFACE = "ShieldNOC"
    CONF_FILE_PATH = WG_INTERFACE + ".conf"
    VPN_IP_PREFIX = "10.33.33"
    VPN_LISTEN_PORT = "12345"

    def __init__(self):
        self._lan_interface = self._get_lan_interface()
        self._private_key, self._public_key = self._get_wg_keys()

    def _get_lan_interface(self):
        result = self._run_terminal_cmd(
            ["ip", "route", "get", "8.8.8.8"],
            capture_output=True
        )
        return result.split("dev")[1].split()[0]

    def _enable_ip_forwarding(self) -> None:
        self._run_terminal_cmd(["sysctl", "-w", "net.ipv4.ip_forward=1"])  # kernel level

    def _disable_ip_forwarding(self) -> None:
        self._run_terminal_cmd(["sysctl", "-w", "net.ipv4.ip_forward=0"])

    def _set_forwarding_and_nat_rules(self, action: str) -> None:
        self._run_terminal_cmd(["iptables", action, "FORWARD", "-i", self.WG_INTERFACE, "-o", self._lan_interface,
                                "-j", "ACCEPT"])  # firewall level

        self._run_terminal_cmd(["iptables", action, "FORWARD", "-i", self._lan_interface, "-o", self.WG_INTERFACE,
                                "-m", "state", "--state", "ESTABLISHED,RELATED", "-j", "ACCEPT"]),  # firewall level

        self._run_terminal_cmd(["iptables", "-t", "nat", action, "POSTROUTING", "-o",
                                self._lan_interface, "-j", "MASQUERADE"])  # enable SNAT for answer to arrive

    def _enable_forwarding_and_nat_rules(self) -> None:
        try:
            self._set_forwarding_and_nat_rules("-A")
        except Exception as e:
            logger.error("Error while setting the vpn rules:", e)

    def _disable_forwarding_and_nat_rules(self) -> None:
        try:
            self._set_forwarding_and_nat_rules("-D")
        except Exception as e:
            logger.error("Error while deleting the vpn rules:", e)

    def is_ip_forwarding_enabled(self) -> bool:
        result = self._run_terminal_cmd(
            ["sysctl", "net.ipv4.ip_forward"],
            capture_output=True
        )
        return " = 1" in result

    def is_nat_enabled(self) -> bool:
        result = self._run_terminal_cmd(
            ["iptables", "-t", "nat", "-S"],
            capture_output=True
        )
        return f"-o {self._lan_interface} -j MASQUERADE" in result

    def start_vpn(self) -> bool:
        self._enable_ip_forwarding()
        self._enable_forwarding_and_nat_rules()
        self._start_wg_interface()

        if not self.is_ip_forwarding_enabled():
            logger.error("IP forwarding is not enabled!")
            return False

        if not self.is_nat_enabled():
            logger.error("NAT is not enabled!")
            return False

        logger.info("~ Server networking configured successfully! ~")
        return True

    def stop_vpn(self) -> bool:
        self._disable_forwarding_and_nat_rules()
        self._disable_ip_forwarding()

        if self.is_ip_forwarding_enabled():
            logger.error("Problem with disable IP forwarding!")
            return False

        if self.is_nat_enabled():
            logger.error("Problem with disable NAT!")
            return False

        logger.info("~ Server networking teardown successfully! ~")
        return True

    def _create_config(self) -> None:
        config_content = f"""[Interface]
        PrivateKey = {self._private_key}
        Address = {self.VPN_IP_PREFIX}.1/24
        ListenPort = {self.VPN_LISTEN_PORT}
        """

        with open(self.CONF_FILE_PATH, "w") as conf_file:
            conf_file.write(config_content)

    def _start_wg_interface(self) -> None:
        if not Path(self.CONF_FILE_PATH).exists():
            self._create_config()

        self._run_terminal_cmd(["wg-quick", "up", self.CONF_FILE_PATH])

    def _stop_wg_interface(self):
        self._run_terminal_cmd(["wg-quick", "down", self.WG_INTERFACE])

    def _get_wg_keys(self) -> tuple:
        # TODO: check if exits in DB: False - gen key, True - return it
        if True:
            return "", ""

        private_key = self._run_terminal_cmd(["wg", "genkey"], capture_output=True)
        public_key =  self._run_terminal_cmd(["wg", "pubkey"], capture_output=True, input=private_key)

        # TODO: add keys to DB

        return private_key, public_key

    def add_peer(self, client_public_key: str) -> tuple:  # TODO: fix func
        # TODO: fix: check if the key already associated with an ip (db use)
        # TODO: fix: check if the ip in-use before adding it also if exists in db

        # TODO: db condition - client exists? - client_ip = IP_PREF
        client_ip = self._get_random_ip()
        self._add_client_to_db(client_public_key, client_ip)

        self._run_terminal_cmd(["wg", "set", self.WG_INTERFACE, "peer", client_public_key,
                                "allowed-ips", f"{client_ip}/32"])

        # mark client as active in db
        return self._public_key, client_ip

    def change_peer_ip(self, client_public_key: str, requested_ip: str) -> None:
        self._run_terminal_cmd(["wg", "set", self.WG_INTERFACE, "peer", client_public_key,
                                "allowed-ips", f"{requested_ip}/32"])

    def remove_peer(self, client_public_key: str) -> None:
        self._run_terminal_cmd(["wg", "set", self.WG_INTERFACE, "peer", client_public_key, "remove"])
        # TODO: clear VPN_IP from DB record

    def is_ip_in_current_use(self, ip: str) -> bool:
        pass  # TODO: db check

    def _add_client_to_db(self, public_key ,ip):  # TODO: maybe delete - in import db manager
        pass  # TODO: db add

    def _get_random_ip(self) -> str:
        while True:
            random_host_ip = str(randint(2, 254))
            new_ip = f"{self.VPN_IP_PREFIX}.{random_host_ip}"

            if not self.is_ip_in_current_use(new_ip):
                break

        return new_ip

    @staticmethod
    def _run_terminal_cmd(cmd: list[str], capture_output=False, **kwargs) -> str | None:
        result = subprocess.run(cmd, check=True, text=True, capture_output=capture_output, **kwargs)
        return result.stdout.strip() if capture_output else None

    @staticmethod
    def is_valid_wg_public_key(key: str) -> bool:
        """ Validate WireGuard public key (base64, 32 bytes) """
        try:
            if len(key) != 44:
                return False

            decoded = base64.b64decode(key, validate=True)
            return len(decoded) == 32
        except Exception:
            return False


# TODO: add to client (download button): subprocess.run('winget install --id WireGuard.WireGuard -e --source winget', shell=True)
#  prefer not for a button but just do a background download
