import subprocess
import base64

from pathlib import Path
from random import randint

from shieldnoc.logging_config import logger
from shieldnoc.server.core.db.enums import ServerField, ClientField
from shieldnoc.server.core.db.models import ServerRecord, ClientRecord
from shieldnoc.server.core.db.queries import DatabaseQueries


class VPNManager:
    WG_INTERFACE = "ShieldNOC"
    CONF_FILE_PATH = WG_INTERFACE + ".conf"
    VPN_IP_PREFIX = "10.33.33"
    VPN_LISTEN_PORT = "12345"

    def __init__(self, db: DatabaseQueries):
        self._db = db

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
        self._stop_wg_interface()

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
        keys = self._db.get_server_keys()
        if keys:
            return self._decrypt_data(keys[ServerField.PRIVATE_KEY.value]), keys[ServerField.PUBLIC_KEY.value]

        private_key = self._run_terminal_cmd(["wg", "genkey"], capture_output=True).strip()
        public_key =  self._run_terminal_cmd(["wg", "pubkey"], capture_output=True, input=private_key).strip()

        self._db.set_server_keys(ServerRecord(self._encrypt_data(private_key), public_key))

        return private_key, public_key

    def add_peer(self, client_initial_data: dict[ClientField, str]) -> tuple:
        client_public_key = client_initial_data[ClientField.PUBLIC_KEY.value]

        if not self._is_valid_wg_public_key(client_public_key):
            return None, None

        if self._db.is_client_exists_by_public_key(client_public_key):
            client_data = self._db.get_client_by_public_key(client_public_key)
            client_vpn_ip = client_data[ClientField.IP_PREF.value]

            if self._db.is_vpn_ip_in_current_use(client_vpn_ip):
                client_vpn_ip = self._get_random_vpn_ip()

            self._db.update_client_fields_by_public_key(client_public_key,
                {
                    ClientField.VPN_IP: client_initial_data[ClientField.VPN_IP.value],
                    ClientField.MAC: client_initial_data[ClientField.MAC.value],
                    ClientField.HOST: client_initial_data[ClientField.HOST.value],
                    ClientField.HOSTNAME: client_initial_data[ClientField.HOSTNAME.value],
                    ClientField.STATUS: "CONNECTED",
                    ClientField.IP_PREF: client_vpn_ip
                })

            return self._public_key, client_vpn_ip

        else:
            client_vpn_ip = self._get_random_vpn_ip()

        client = ClientRecord(
            public_key=client_public_key,
            vpn_ip=client_vpn_ip,
            mac=client_initial_data[ClientField.MAC.value],
            host=client_initial_data[ClientField.HOST.value],
            hostname=client_initial_data[ClientField.HOSTNAME.value],
            status="CONNECTED",
            ip_preference=client_vpn_ip
        )
        self._db.add_client(client)

        self._run_terminal_cmd(["wg", "set", self.WG_INTERFACE, "peer", client_public_key,
                                "allowed-ips", f"{client_vpn_ip}/32"])

        return self._public_key, client_vpn_ip

    def change_peer_ip(self, client_vpn_ip: str, requested_ip: str) -> tuple[bool, str]:
        client_public_key = self._db.get_client_by_vpn_ip(client_vpn_ip)[ClientField.PUBLIC_KEY.value]

        if not self.is_valid_vpn_ip(requested_ip):
            return False, "IP is not valid!\nvalid host octet range: 2-254"  # TODO: remember to integrate in client side as pop message

        if self._db.is_vpn_ip_in_current_use(requested_ip):
            return False, "This IP is currently in use!\nPlease select another IP."

        self._run_terminal_cmd(["wg", "set", self.WG_INTERFACE, "peer", client_public_key,
                                "allowed-ips", f"{requested_ip}/32"])

        self._db.update_client_fields_by_vpn_ip(client_vpn_ip, {
            ClientField.VPN_IP: requested_ip
        })
        return True, ""

    def remove_peer(self, client_vpn_ip: str) -> None:
        client_public_key = self._db.get_client_by_vpn_ip(client_vpn_ip)[ClientField.PUBLIC_KEY.value]
        self._run_terminal_cmd(["wg", "set", self.WG_INTERFACE, "peer", client_public_key, "remove"])

        self._db.update_client_fields_by_vpn_ip(client_vpn_ip,
            {
                ClientField.VPN_IP: None,
                ClientField.STATUS: "DISCONNECTED",
                ClientField.IP_PREF: client_vpn_ip
        })

    def _get_random_vpn_ip(self) -> str:
        while True:
            random_host_octet = str(randint(2, 254))
            new_ip = f"{self.VPN_IP_PREFIX}.{random_host_octet}"

            if not self._db.is_vpn_ip_in_current_use(new_ip):
                break

        return new_ip

    @staticmethod
    def _run_terminal_cmd(cmd: list[str], capture_output=False, **kwargs) -> str | None:
        result = subprocess.run(cmd, check=True, text=True, capture_output=capture_output, **kwargs)
        return result.stdout.strip() if capture_output else None

    @staticmethod
    def _is_valid_wg_public_key(key: str) -> bool:
        """ Validate WireGuard public key (base64, 32 bytes) """
        try:
            if len(key) != 44:
                return False

            decoded = base64.b64decode(key, validate=True)
            return len(decoded) == 32
        except Exception:
            return False

    @staticmethod
    def _is_valid_vpn_ip(vpn_ip: str) -> bool:
        pass

    @staticmethod
    def _encrypt_data(data: str) -> str:
        pass

    @staticmethod
    def _decrypt_data(data: str) -> str:
        pass


# TODO: add to client (download button): subprocess.run('winget install --id WireGuard.WireGuard -e --source winget', shell=True)
#  prefer not for a button but just do a background download
