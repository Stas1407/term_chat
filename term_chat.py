import socket
from misc.CommandsInterface import CommandsInterface
from misc.Session import Session
from misc.utils import *
from settings import server_ip, server_port


class Client:
    def __init__(self):
        self.SERVER_IP = server_ip
        self.SERVER_PORT = server_port
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
