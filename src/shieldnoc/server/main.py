from shieldnoc.server.gui.main import gui_main
from shieldnoc.server.managers.connections.connection_manager import ConnectionManager


def main():
    connection_manager = ConnectionManager()
    connection_manager.start_connection()
    gui_main(connection_manager.chat_manager)  # have to run on the main thread


if __name__ == '__main__':
    main()
