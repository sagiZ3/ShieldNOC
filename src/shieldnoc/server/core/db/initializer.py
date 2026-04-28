import sqlite3

from shieldnoc.server.core.db.enums import ClientField, ServerField


def init_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {ClientField.TABLE_NAME.value} (
            {ClientField.PUBLIC_KEY.value} TEXT PRIMARY KEY,
            {ClientField.VPN_IP.value} TEXT NULL UNIQUE,
            {ClientField.MAC.value} TEXT DEFAULT '',
            {ClientField.HOST.value} TEXT DEFAULT '',
            {ClientField.HOSTNAME.value} TEXT DEFAULT '',
            {ClientField.LAST_SEEN.value} TEXT DEFAULT CURRENT_TIMESTAMP,
            {ClientField.STATUS.value} TEXT DEFAULT '',
            {ClientField.IP_PREF.value} TEXT DEFAULT ''
        )
        """
    )

    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {ServerField.TABLE_NAME.value} (
            {ServerField.ID.value} INTEGER PRIMARY KEY CHECK (id = 1),
            {ServerField.PRIVATE_KEY.value} TEXT NOT NULL,
            {ServerField.PUBLIC_KEY.value} TEXT NOT NULL,
            {ServerField.LAST_UPDATED.value} TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    conn.commit()
