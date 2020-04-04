from .core.app import App
from google_images_download import google_images_download

import socket
socket.setdefaulttimeout(2)


def main():
    app = App()
    app.run()


if __name__ == '__main__':
    main()
