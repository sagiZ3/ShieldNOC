import subprocess

from pathlib import Path

from shieldnoc import protocol
from shieldnoc.logging_config import logger


class VPNManager:
    WG_INTERFACE = "shieldnoc"
    CONF_FILE_PATH = "./" + WG_INTERFACE + ".conf"
    KEYS_FILE_PATH = "./wg.keys"

    def __init__(self):
        self._private_key, self.public_key = self._get_wg_keys()
        self._server_public_key = ""

    def _get_wg_keys(self) -> tuple[str, str]:
        if Path(self.KEYS_FILE_PATH).exists():
            private_key, public_key = self._load_keys()
            if public_key:
                return self._decrypt_data(private_key), public_key

        private_key, public_key = self.generate_keys()

        with open(self.KEYS_FILE_PATH, 'w') as keys_file:
            keys_file.write(f"{self._encrypt_data(private_key)}:{public_key}")

        return private_key, public_key

    def _load_keys(self) -> tuple[str | None, str | None]:
        logger.info("Use WireGuard Existing Keys")
        try:
            with open(self.KEYS_FILE_PATH, 'r') as keys_file:
                private_key, public_key = keys_file.readline().strip().split(':')
                return private_key, public_key

        except Exception as e:
            logger.error("Problem with loading WireGuard existing keys:", e)
            return None, None

    def generate_keys(self) -> tuple[str, str]:
        logger.info("Generate new WireGuard Keys")

        private_key = self._run_cmd(["wg", "genkey"], capture_output=True).strip()
        public_key = self._run_cmd(["wg", "pubkey"], capture_output=True, input=private_key).strip()
        return private_key, public_key

    def connect_vpn(self, assigned_vpn_ip, server_public_key=None) -> None:  # TODO: check if needs to disconnect before connecting
        self._create_config(assigned_vpn_ip, server_public_key)

        conf_path = Path(self.CONF_FILE_PATH).resolve()

        self._run_cmd(["powershell", "-Command",
            f'Start-Process wireguard -ArgumentList "/installtunnelservice {conf_path}" -Verb RunAs'
        ])

    def _create_config(self, assigned_vpn_ip, server_public_key=None) -> None:
        if server_public_key:
            self._server_public_key = server_public_key

        config_content = f"""[Interface]
        PrivateKey = {self._private_key}
        Address = {assigned_vpn_ip}/32
        
        [Peer]
        PublicKey = {self._server_public_key}
        Endpoint = {protocol.SERVER_IP}:{protocol.VPN_LISTEN_PORT}
        AllowedIPs = 0.0.0.0/0
        PersistentKeepalive = 25
        """

        with open(self.CONF_FILE_PATH, "w") as conf_file:
            conf_file.write(config_content)

    def disconnect_vpn(self) -> None:
        self._run_cmd(["powershell", "-Command",
            f'Start-Process wireguard -ArgumentList "/uninstalltunnelservice {self.WG_INTERFACE}" -Verb RunAs'
        ])

    def change_ip(self, new_ip) -> tuple[bool, str]:  # TODO: thing about a way to integrate with GUI
        if new_ip[0] == str(int(True)):
            self.disconnect_vpn()
            self.connect_vpn(new_ip[1:])
            return True, ""

        return False, new_ip[1:]

    @staticmethod
    def _run_cmd(cmd: list[str], capture_output=False, **kwargs) -> str | None:
        try:
            result = subprocess.run(cmd, check=True, text=True, capture_output=capture_output, **kwargs)

        except Exception as e:
            logger.error(f"error with running the following command: '{cmd}':\n\t- {e}")
            return None

        return result.stdout.strip() if capture_output else None

    @staticmethod
    def _encrypt_data(data: str) -> str:
        return data

    @staticmethod
    def _decrypt_data(data: str) -> str:
        return data
