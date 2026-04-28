import sqlite3

from functools import wraps

from shieldnoc.logging_config import logger
from shieldnoc.server.core.db import initializer
from shieldnoc.server.core.db.models import ClientRecord, ServerRecord
from shieldnoc.server.core.db.enums import ClientField, ServerField


def auto_commit(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self._conn.commit()
        logger.info(f"[DB COMMIT] {func.__name__}")
        return result
    return wrapper


# noinspection PyTypeChecker
class DatabaseQueries:
    def __init__(self, db_path="shieldnoc.db"):
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row

        initializer.init_schema(self._conn)

    @auto_commit
    def add_client(self, client: ClientRecord) -> None:
        self._conn.execute(
            f"""
            INSERT INTO {ClientField.TABLE_NAME.value} (
                {ClientField.PUBLIC_KEY.value},
                {ClientField.VPN_IP.value},
                {ClientField.MAC.value},
                {ClientField.HOST.value},
                {ClientField.HOSTNAME.value},
                {ClientField.STATUS.value},
                {ClientField.IP_PREF.value}
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                client.public_key,
                client.vpn_ip,
                client.mac,
                client.host,
                client.hostname,
                client.status,
                client.ip_preference
            )
        )

    def get_all_clients(self) -> list[sqlite3.Row]:
        return self._conn.execute(
            f"""
            SELECT *
            FROM {ClientField.TABLE_NAME.value}
            """
        ).fetchall()

    def get_client_by_public_key(self, public_key: str) -> sqlite3.Row | None:
        return self._conn.execute(
            f"""
            SELECT *
            FROM {ClientField.TABLE_NAME.value}
            WHERE {ClientField.PUBLIC_KEY.value} = ?
            """,
            (public_key,)
        ).fetchone()

    def get_client_by_vpn_ip(self, vpn_ip: str) -> sqlite3.Row | None:
        return self._conn.execute(
            f"""
            SELECT *
            FROM {ClientField.TABLE_NAME.value}
            WHERE {ClientField.VPN_IP.value} = ?
            """,
            (vpn_ip,)
        ).fetchone()

    @auto_commit
    def _update_client_fields(self, identifier_field: ClientField, identifier_value: str,
                              fields: dict[ClientField, str | None]) -> None:
        if not fields:
            return

        if not all(isinstance(f, ClientField) for f in fields):
            return

        set_phrase = ", ".join(f"{field.value} = ?" for field in fields.keys())
        values = list(fields.values()) + [identifier_value]

        self._conn.execute(
            f"""
            UPDATE {ClientField.TABLE_NAME.value}
            SET {set_phrase}
            WHERE {identifier_field.value} = ?
            """,
            values
        )

    def update_client_fields_by_public_key(self, public_key: str, fields: dict[ClientField, str | None]) -> None:
        self._update_client_fields(ClientField.PUBLIC_KEY, public_key, fields)

    def update_client_fields_by_vpn_ip(self, vpn_ip: str, fields: dict[ClientField, str | None]) -> None:
        self._update_client_fields(ClientField.VPN_IP, vpn_ip, fields)

    def is_client_exists_by_public_key(self, public_key: str) -> bool:
        row = self._conn.execute(
            f"""
            SELECT 1
            FROM {ClientField.TABLE_NAME.value}
            WHERE {ClientField.PUBLIC_KEY.value} = ?
            LIMIT 1
            """,
            (public_key,)
        ).fetchone()

        return row is not None

    def is_vpn_ip_in_current_use(self, vpn_ip: str) -> bool:
        row = self._conn.execute(
            f"""
            SELECT 1
            FROM {ClientField.TABLE_NAME.value}
            WHERE {ClientField.VPN_IP.value} = ?
            LIMIT 1
            """,
            (vpn_ip,)
        ).fetchone()

        return row is not None

    @auto_commit
    def delete_client_by_public_key(self, public_key: str) -> None:
        self._conn.execute(
            f"""
            DELETE FROM {ClientField.TABLE_NAME.value}
            WHERE {ClientField.PUBLIC_KEY.value} = ?
            """,
            (public_key,)
        )

    @auto_commit
    def delete_client_by_vpn_ip(self, vpn_ip: str) -> None:
        self._conn.execute(
            f"""
            DELETE FROM {ClientField.TABLE_NAME.value}
            WHERE {ClientField.VPN_IP.value} = ?
            """,
            (vpn_ip,)
        )

    @auto_commit
    def delete_all_clients(self) -> None:
        self._conn.execute("DELETE FROM clients")

    @auto_commit
    def set_server_keys(self, server: ServerRecord):
        self._conn.execute(
            f"""
            INSERT INTO {ServerField.TABLE_NAME.value} (
                {ServerField.PRIVATE_KEY.value},
                {ServerField.PUBLIC_KEY.value}
            )
            VALUES (?, ?)
            """,
            (
                server.private_key,
                server.private_key
            )
        )

    def get_server_keys(self) -> sqlite3.Row | None:
        return self._conn.execute(
            f"""
            SELECT {ServerField.PRIVATE_KEY.value}, {ServerField.PUBLIC_KEY.value}
            FROM {ServerField.TABLE_NAME.value}
            WHERE {ServerField.ID.value} = 1
            """
        ).fetchone()

    def close(self) -> None:
        self._conn.close()
