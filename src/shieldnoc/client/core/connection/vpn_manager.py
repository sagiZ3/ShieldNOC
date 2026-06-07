import ipaddress
import re
import subprocess
import sys

from pathlib import Path
from time import sleep
from cryptography.fernet import Fernet

from shieldnoc import protocol
from shieldnoc.logging_config import logger


class VPNManager:
    WG_INTERFACE = "shieldnoc"
    CONF_FILE_PATH = "./" + WG_INTERFACE + ".conf"
    KEYS_FILE_PATH = "./wg.keys"
    FERNET_KEY = "9abCR4sczWxWhR89OwOMXLXN9VQKjZuW5lUINGR_KPQ=="
    CIPHER = Fernet(FERNET_KEY)

    def __init__(self):
        """ Initializes the VPN manager and WireGuard keys. """

        self.ensure_wg_installed()

        self._private_key, self.public_key = self._get_wg_keys()
        self._server_public_key = ""

    def _get_wg_keys(self) -> tuple[str, str]:
        """
        Loads existing WireGuard keys or generates new ones.

        :return: Tuple containing private and public WireGuard keys.
        """

        if Path(self.KEYS_FILE_PATH).exists():
            private_key, public_key = self._load_keys()
            if public_key:
                return self._decrypt_data(private_key), public_key

        private_key, public_key = self.generate_keys()

        with open(self.KEYS_FILE_PATH, 'w') as keys_file:
            keys_file.write(f"{self._encrypt_data(private_key)}:{public_key}")

        return private_key, public_key

    def _load_keys(self) -> tuple[str | None, str | None]:
        """
        Loads stored WireGuard keys from the keys file.

        :return: Tuple containing private and public keys, or None values if loading fails.
        """

        logger.info("Use WireGuard Existing Keys")
        try:
            with open(self.KEYS_FILE_PATH, 'r') as keys_file:
                private_key, public_key = keys_file.readline().strip().split(':')
                return private_key, public_key

        except Exception as e:
            logger.error("Problem with loading WireGuard existing keys:", e)
            return None, None

    def generate_keys(self) -> tuple[str, str]:
        """
        Generates a new WireGuard key pair.

        :return: Tuple containing private and public WireGuard keys.
        """

        logger.info("Generate new WireGuard Keys")

        private_key = self._run_cmd(["wg", "genkey"], capture_output=True).strip()
        public_key = self._run_cmd(["wg", "pubkey"], capture_output=True, input=private_key).strip()
        return private_key, public_key

    def connect_vpn(self, assigned_vpn_ip: str, server_public_key=None) -> None:  # TODO: check if needs to disconnect before connecting
        """ Creates the VPN config file and starts the WireGuard tunnel. """

        self._create_config(assigned_vpn_ip, server_public_key)

        conf_path = Path(self.CONF_FILE_PATH).resolve()

        self._run_cmd(["powershell", "-Command",
            f'Start-Process wireguard -ArgumentList "/installtunnelservice {conf_path}" -Verb RunAs'
        ])

    def is_vpn_up(self) -> bool:
        """
        Checks if the VPN tunnel is up.

        :return: True if VPN tunnel is up, False otherwise.
        """

        if self._run_cmd(["wg", "show"], capture_output=True):
            return True
        return False

    def _create_config(self, assigned_vpn_ip: str, server_public_key=None) -> None:
        """ Creates the WireGuard configuration file for the VPN tunnel. """

        if server_public_key:
            self._server_public_key = server_public_key

        config_content = f"""[Interface]
        PrivateKey = {self._private_key}
        Address = {assigned_vpn_ip}/32
        
        [Peer]
        PublicKey = {self._server_public_key}
        Endpoint = {protocol.SERVER_IP}:{protocol.VPN_LISTEN_PORT}
        AllowedIPs = 0.0.0.0/1, 128.0.0.0/1, {self.get_ipv4_cidrs()}
        PersistentKeepalive = 25
        """

        with open(self.CONF_FILE_PATH, "w") as conf_file:
            conf_file.write(config_content)

    def get_ipv4_cidrs(self) -> str | None:
        output = self._run_cmd(["ipconfig"], capture_output=True)

        pattern = (
            r"IPv4 Address[.\s]*:\s*([\d.]+).*?"
            r"Subnet Mask[.\s]*:\s*([\d.]+)"
        )

        cidrs = []
        for ipv4, subnet_mask in re.findall(pattern, output, re.DOTALL):
            prefix = ipaddress.IPv4Network(f"0.0.0.0/{subnet_mask}").prefixlen
            network = ipaddress.IPv4Network(f"{ipv4}/{prefix}", strict=False)
            cidrs.append(str(network))

        if not cidrs:
            return None

        return ", ".join(cidrs)

    def disconnect_vpn(self) -> None:
        """ Disconnects the active WireGuard VPN tunnel. """

        self._run_cmd(["powershell", "-Command",
            f'Start-Process wireguard -ArgumentList "/uninstalltunnelservice {self.WG_INTERFACE}" -Verb RunAs'
        ])

    def change_ip(self, code_and_response: str) -> tuple[bool, str]:
        """
        Changes the VPN IP address according to the server response.

        :return: Tuple containing status and error message.
        """

        is_ip_changed = code_and_response[0]
        response = code_and_response[1:]

        if is_ip_changed == str(int(False)):
            return False, response

        self.disconnect_vpn()
        sleep(1)
        self.connect_vpn(response)
        return True, response

    def ensure_wg_installed(self) -> None:
        """ Ensures that WireGuard is installed on the system. """

        if not self.is_wg_installed():
            logger.info("Installing WireGuard...")
            self._run_cmd(["winget", "install", "--id", "WireGuard.WireGuard", "-e", "--source", "winget"])

            if self.is_wg_installed():
                logger.info("WireGuard installed successfully")
            else:
                logger.warning("WireGuard could not be installed.\nPlease try again or install WireGuard manually.")
                sys.exit(2)

    def is_wg_installed(self) -> bool:
        """
        Checks whether WireGuard is installed on the system.

        :return: True if WireGuard is installed, otherwise False.
        """

        return self._run_cmd(["winget", "list", "wireguard"], capture_output=True) is not None

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
