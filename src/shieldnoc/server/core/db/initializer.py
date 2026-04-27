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

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS server_keys (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            private_key TEXT NOT NULL,
            public_key TEXT NOT NULL,
            created_time TEXT NOT NULL
    )
    """
    )
    conn.commit()
