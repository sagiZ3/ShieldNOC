from shieldnoc.server.gui.main import gui_main
from shieldnoc.server.managers.chat import ChatManager
from shieldnoc.server.managers.vpn import VPNManager


def main():
    gui_main()
    vpn = VPNManager('wg0', 'eth0', 'path')  # change path
    # remember to run the vpn model BEFORE the chat model because differently it can cause socket problems

    chat_manager = ChatManager()
    chat_manager.start_chat()
    gui_main(chat_manager)  # add a thread! it stuck after


if __name__ == '__main__':
    main()
