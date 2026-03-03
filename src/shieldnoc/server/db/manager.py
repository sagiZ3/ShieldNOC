from shieldnoc.server.db.enums import ClientField


def update_client(conn, client_id: int, fields: dict[ClientField, str]) -> int:
    """Updated client information from dictionary (key - any from enums.ClientField)
    :return: 0 if nothing has been update/client isn't exists, 1 if update successfully"""
    patch = {k: v for k, v in fields.items() if k in ClientField and v is not None}
    if not patch:
        return 0

    set_clause = ", ".join([f"{k} = ?" for k in patch.keys()])
    values = list(patch.values()) + [client_id]

    sql = f"UPDATE clients SET {set_clause} WHERE id = ?"
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    return cur.rowcount
