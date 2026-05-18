from shieldnoc.client.gui.main import gui_main
from shieldnoc.client.core.connection.connection_manager import ConnectionManager


def main():
    """ Starts the ShieldNOC client application. """

    connection_manager = ConnectionManager()
    gui_main(connection_manager, connection_manager.chat_manager)  # have to run on the main thread


if __name__ == '__main__':
    main()
