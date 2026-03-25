from shieldnoc.client.gui.main import gui_main
from shieldnoc.client.managers.chat import ChatManager
from shieldnoc.client.managers.vpn import VPNManager


def main():
    chat_manager = ChatManager()
    chat_manager.start_chat()
    gui_main(chat_manager)  # add a thread! it stuck after
    # vpn_manager = VPNManager()
    # remember to run the vpn model BEFORE the chat model because differently it can cause socket problems


if __name__ == '__main__':
    main()
