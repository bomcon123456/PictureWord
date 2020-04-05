from .core.app import App

import socket
socket.setdefaulttimeout(2)


def main():
    app = App()
    app.run()


if __name__ == '__main__':
    main()
