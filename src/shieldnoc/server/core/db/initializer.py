import sqlite3

def init_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            public_key TEXT PRIMARY KEY,
            vpn_ip TEXT NOT NULL UNIQUE,
            mac TEXT DEFAULT '',
            host TEXT DEFAULT '',
            hostname TEXT DEFAULT '',
            last_seen TEXT DEFAULT '',
            status TEXT DEFAULT '',
            ip_preference TEXT DEFAULT ''
        )
        """
    )
    conn.commit()
