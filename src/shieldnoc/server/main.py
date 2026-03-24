from shieldnoc.server.gui.main import gui_main

def main():
    gui_main()
    vpn = VPNManager('wg0', 'eth0', 'path')  # change path
    # remember to run the vpn model BEFORE the chat model because differently it can cause socket problems



if __name__ == '__main__':
    main()
