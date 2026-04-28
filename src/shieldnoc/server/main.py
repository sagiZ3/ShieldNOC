from shieldnoc.server.core.db.queries import DatabaseQueries
from shieldnoc.server.gui.main import gui_main
from shieldnoc.server.core.connection.connection_manager import ConnectionManager


def main():
    db = DatabaseQueries()
    connection_manager = ConnectionManager(db)
    connection_manager.start_connection()
    gui_main(db, connection_manager.chat_manager)  # have to run on the main thread


if __name__ == '__main__':
    main()
