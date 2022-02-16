import socket
from misc.CommandsInterface import CommandsInterface
from misc.Session import Session
from misc.utils import *


class Client:
    def __init__(self):
        self.SERVER_IP = "127.0.0.1"
        self.SERVER_PORT = 5000
        self.socket = socket.socket()
        self.session = Session(self.socket)

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("[+] Connecting...")
        self.socket.connect((self.SERVER_IP, self.SERVER_PORT))
        print("[+] Connected")

        print("[+] Establishing encrypted session...")
        self.session = Session(self.socket)
        self.session.start()

    def quit(self):
        print("[+] Exiting")
        self.session.send({"command": "quit"})
        self.session.close()
        print("Goodbye")

    def run(self):
        os.environ['TERM'] = 'xterm'
        try:
            self.connect()
        except ConnectionError:
            self.session.close()
            return

        command_interface = CommandsInterface(self.session)
        command_interface.run()

        self.quit()


c = Client()
c.run()
