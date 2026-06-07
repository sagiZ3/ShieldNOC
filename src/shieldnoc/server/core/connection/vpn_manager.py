import subprocess
import base64

from random import randint
from cryptography.fernet import Fernet

from shieldnoc import protocol
from shieldnoc.logging_config import logger
from shieldnoc.server.core.db.enums import ServerField, ClientField
from shieldnoc.server.core.db.models import ServerRecord, ClientRecord
from shieldnoc.server.core.db.queries import DatabaseQueries


class VPNManager:
    WG_INTERFACE = "shieldnoc"
    CONF_FILE_PATH = "./" + WG_INTERFACE + ".conf"
    VPN_IP_PREFIX = "10.33.33"
    FERNET_KEY = "3NP2Wa_ezV7XsSl1JXkzgy0wqfh4zLaj4PK4MwVVO2g="
    CIPHER = Fernet(FERNET_KEY)

    def __init__(self, db: DatabaseQueries):
        """ Initializes the VPN manager and WireGuard server configuration. """

        self._db = db

        self._lan_interface = self._get_lan_interface()
        self._private_key, self._public_key = self._get_wg_keys()

    def _get_lan_interface(self):
        """
        Retrieves the active LAN network interface.

        :return: LAN interface name.
        """

        result = self._run_terminal_cmd(
            ["ip", "route", "get", "8.8.8.8"],
            capture_output=True
        )
        return result.split("dev")[1].split()[0]

    def _enable_ip_forwarding(self) -> None:
        """ Enables IPv4 packet forwarding on the server. """

        self._run_terminal_cmd(["sysctl", "-w", "net.ipv4.ip_forward=1"])  # kernel level

    def _disable_ip_forwarding(self) -> None:
        """ Disables IPv4 packet forwarding on the server. """

        self._run_terminal_cmd(["sysctl", "-w", "net.ipv4.ip_forward=0"])

    def _set_forwarding_and_nat_rules(self, action: str) -> None:
        """ Applies or removes forwarding and NAT firewall rules. """

        self._run_terminal_cmd(["iptables", action, "FORWARD", "-i", self.WG_INTERFACE, "-o", self._lan_interface,
                                "-j", "ACCEPT"])  # firewall level

        self._run_terminal_cmd(["iptables", action, "FORWARD", "-i", self._lan_interface, "-o", self.WG_INTERFACE,
                                "-m", "state", "--state", "ESTABLISHED,RELATED", "-j", "ACCEPT"]),  # firewall level

        self._run_terminal_cmd(["iptables", "-t", "nat", action, "POSTROUTING", "-o",
                                self._lan_interface, "-j", "MASQUERADE"])  # enable SNAT for answer to arrive

    def _enable_forwarding_and_nat_rules(self) -> None:
        """ Enables forwarding and NAT firewall rules for the VPN. """

        try:
            self._set_forwarding_and_nat_rules("-A")
        except Exception as e:
            logger.error("Error while setting the vpn rules:", e)

    def _disable_forwarding_and_nat_rules(self) -> None:
        """ Disables forwarding and NAT firewall rules for the VPN. """

        try:
            self._set_forwarding_and_nat_rules("-D")
        except Exception as e:
            logger.error("Error while deleting the vpn rules:", e)

    def is_ip_forwarding_enabled(self) -> bool:
        """
        Checks whether IPv4 forwarding is enabled.

        :return: True if IP forwarding is enabled, otherwise False.
        """

        result = self._run_terminal_cmd(
            ["sysctl", "net.ipv4.ip_forward"],
            capture_output=True
        )
        return " = 1" in result

    def is_nat_enabled(self) -> bool:
        """
        Checks whether NAT masquerading is enabled.

        :return: True if NAT is enabled, otherwise False.
        """

        result = self._run_terminal_cmd(
            ["iptables", "-t", "nat", "-S"],
            capture_output=True
        )
        return f"-o {self._lan_interface} -j MASQUERADE" in result

    def start_vpn(self) -> None:  # TODO: handle because last run crash crash - use stop_vpn and then start_vpn
        """ Starts the VPN networking services and WireGuard interface. """

        self._enable_ip_forwarding()
        self._enable_forwarding_and_nat_rules()
        self._start_wg_interface()

        is_ip_forwarding_enabled = self.is_ip_forwarding_enabled()
        is_nat_enabled = self.is_nat_enabled()

        if is_ip_forwarding_enabled and is_nat_enabled:
            logger.info("~ Server networking configured successfully! ~")
            return

        if not is_ip_forwarding_enabled:
            logger.error("Problem with enable IP forwarding!")

        if not is_nat_enabled:
            logger.error("Problem with enable NAT!")

    def stop_vpn(self) -> None:
        """ Stops the VPN networking services and WireGuard interface. """

        self._disable_forwarding_and_nat_rules()
        self._disable_ip_forwarding()
        self.remove_all_connected_peers()
        self._stop_wg_interface()

        is_ip_forwarding_disabled = not self.is_ip_forwarding_enabled()
        is_nat_disabled = not self.is_nat_enabled()

        if is_ip_forwarding_disabled and is_nat_disabled:
            logger.info("~ Server networking teardown successfully! ~")
            return

        if not is_ip_forwarding_disabled:
            logger.error("Problem with disable IP forwarding!")

        if not is_nat_disabled:
            logger.error("Problem with disable NAT!")

    def _create_config(self) -> None:
        """ Creates the WireGuard server configuration file. """

        config_content = f"""[Interface]
        PrivateKey = {self._private_key}
        Address = {self.VPN_IP_PREFIX}.1/24
        ListenPort = {protocol.VPN_LISTEN_PORT}
        """

        with open(self.CONF_FILE_PATH, "w") as conf_file:
            conf_file.write(config_content)

    def _start_wg_interface(self) -> None:
        """ Starts the WireGuard interface using the generated configuration. """

        self._create_config()

        self._run_terminal_cmd(["wg-quick", "up", self.CONF_FILE_PATH])

    def _stop_wg_interface(self):
        """ Stops the active WireGuard interface. """

        self._run_terminal_cmd(["wg-quick", "down", self.CONF_FILE_PATH])

    def _get_wg_keys(self) -> tuple:
        """
        Loads existing WireGuard keys or generates new ones.

        :return: Tuple containing private and public WireGuard keys.
        """

        keys = self._db.get_server_keys()
        if keys:
            return self._decrypt_data(keys[ServerField.PRIVATE_KEY.value]), keys[ServerField.PUBLIC_KEY.value]

        private_key, public_key = self.generate_keys()
        self._db.set_server_keys(ServerRecord(self._encrypt_data(private_key), public_key))

        return private_key, public_key

    def generate_keys(self) -> tuple[str, str]:
        """
        Generates a new WireGuard key pair.

        :return: Tuple containing private and public WireGuard keys.
        """

        private_key = self._run_terminal_cmd(["wg", "genkey"], capture_output=True).strip()
        public_key =  self._run_terminal_cmd(["wg", "pubkey"], capture_output=True, input=private_key).strip()
        return private_key, public_key

    def add_peer(self, client_initial_data: dict[ClientField, str]) -> tuple:
        """
        Adds a new WireGuard peer or reconnects an existing client.

        :return: Tuple containing server public key and assigned VPN IP.
        """

        client_public_key = client_initial_data[ClientField.PUBLIC_KEY]

        if not self._is_valid_wg_public_key(client_public_key):
            return None, None

        if self._db.is_client_exists_by_public_key(client_public_key):
            client_data = self._db.get_client_by_public_key(client_public_key)
            client_vpn_ip = client_data[ClientField.IP_PREF.value]

            if self._db.is_vpn_ip_in_current_use(client_vpn_ip):
                client_vpn_ip = self._get_random_vpn_ip()

            self._run_terminal_cmd(["wg", "set", self.WG_INTERFACE, "peer", client_public_key,
                                    "allowed-ips", f"{client_vpn_ip}/32"])

            self._db.update_client_fields_by_public_key(client_public_key,
                {
                    ClientField.VPN_IP: client_vpn_ip,
                    ClientField.MAC: client_initial_data[ClientField.MAC],
                    ClientField.OS: client_initial_data[ClientField.OS],
                    ClientField.HOSTNAME: client_initial_data[ClientField.HOSTNAME],
                    ClientField.STATUS: "CONNECTED",
                    ClientField.IP_PREF: client_vpn_ip
                })

            return self._public_key, client_vpn_ip

        else:
            client_vpn_ip = self._get_random_vpn_ip()

        client = ClientRecord(
            public_key=client_public_key,
            vpn_ip=client_vpn_ip,
            mac=client_initial_data[ClientField.MAC],
            os=client_initial_data[ClientField.OS],
            hostname=client_initial_data[ClientField.HOSTNAME],
            status="CONNECTED",
            ip_preference=client_vpn_ip
        )
        self._db.add_client(client)

        self._run_terminal_cmd(["wg", "set", self.WG_INTERFACE, "peer", client_public_key,
                                "allowed-ips", f"{client_vpn_ip}/32"])

        return self._public_key, client_vpn_ip

    def handle_peer_ip_change(self, requested_ip: str) -> tuple[bool, str]:
        """
        Validates a requested VPN IP address change.

        :return: Tuple containing validation status and response message.
        """

        if not self.is_valid_vpn_ip(requested_ip):
            return False, "IP is not valid!\nvalid host octet range: 2-254"

        if self._db.is_vpn_ip_in_current_use(requested_ip):
            return False, "This IP is currently in use!\nPlease select another IP."

        return True, requested_ip

    def change_peer_ip(self, client_vpn_ip, new_vpn_ip: str) -> None:
        """ Changes the VPN IP address of an existing WireGuard peer. """

        client_public_key = self._db.get_client_by_vpn_ip(client_vpn_ip)[ClientField.PUBLIC_KEY.value]

        self._db.update_client_fields_by_vpn_ip(client_vpn_ip, {
            ClientField.VPN_IP: new_vpn_ip
        })

        self._run_terminal_cmd(["wg", "set", self.WG_INTERFACE, "peer", client_public_key,
                                "allowed-ips", f"{new_vpn_ip}/32"])

    def remove_peer(self, client_vpn_ip) -> None:
        """ Removes a WireGuard peer from the VPN server. """

        client_public_key = self._db.get_client_by_vpn_ip(client_vpn_ip)[ClientField.PUBLIC_KEY.value]

        self._run_terminal_cmd(["wg", "set", self.WG_INTERFACE, "peer", client_public_key, "remove"])

        self._db.update_client_fields_by_vpn_ip(client_vpn_ip,
            {
                ClientField.VPN_IP: None,
                ClientField.STATUS: "DISCONNECTED",
                ClientField.IP_PREF: client_vpn_ip
        })

    def remove_all_connected_peers(self) -> None:
        for client in self._db.get_all_connected_clients():
            self.remove_peer(client[ClientField.VPN_IP.value])

    def _get_random_vpn_ip(self) -> str:
        """
        Generates a random unused VPN IP address.

        :return: Available VPN IP address.
        """

        while True:
            random_host_octet = str(randint(2, 254))
            new_ip = f"{self.VPN_IP_PREFIX}.{random_host_octet}"

            if not self._db.is_vpn_ip_in_current_use(new_ip):
                break

        return new_ip

    def is_valid_vpn_ip(self, vpn_ip: str) -> bool:
        """
        Validates a VPN IP address format and range.

        :return: True if the VPN IP is valid, otherwise False.
        """

        if not vpn_ip:
            return False

        octets = vpn_ip.split('.')

        if len(octets) != 4:
            return False

        prefix = ".".join(octets[:-1])
        host: str = octets[3]

        return prefix == self.VPN_IP_PREFIX and host.isdigit() and  2 < int(host) < 255

    @staticmethod
    def _run_terminal_cmd(cmd: list[str], capture_output=False, **kwargs) -> str | None:
        """
        Runs a terminal command and optionally captures its output.

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

    def _encrypt_data(self, data: str) -> str:
        """
        Encrypts sensitive data before storage.

        :return: Encrypted data string.
        """

        return self.CIPHER.encrypt(data.encode()).decode()

    def _decrypt_data(self, data: str) -> str:
        """
        Decrypts stored encrypted data.

        :return: Decrypted data string.
        """

        return self.CIPHER.decrypt(data.encode()).decode()

    @staticmethod
    def _is_valid_wg_public_key(key: str) -> bool:
        """
        Validates a WireGuard public key format.

        :return: True if the public key is valid, otherwise False.
        """

        """ Validate WireGuard public key (base64, 32 bytes) """
        try:
            if len(key) != 44:
                return False

            decoded = base64.b64decode(key, validate=True)
            return len(decoded) == 32
        except Exception:
            return False
