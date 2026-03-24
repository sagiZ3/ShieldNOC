from shieldnoc.server.gui.main import gui_main
from shieldnoc.server.managers.chat import ChatManager
from shieldnoc.server.managers.vpn import VPNManager


def main():
    chat_manager = ChatManager()
    chat_manager.start_chat()
    gui_main(chat_manager)  # add a thread! it stuck after


if __name__ == '__main__':
    main()
