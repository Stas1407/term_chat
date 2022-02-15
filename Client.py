import socket
import os
from banner import banner
import asyncio
import json
import readline
from Chat import Chat
from texttable import Texttable


class Client:
    def __init__(self):
        self.SERVER_IP = "127.0.0.1"
        self.SERVER_PORT = 5000
        self.socket = socket.socket()
        self.room = ""
        self.leave_room = asyncio.Event()
        self.leave_room.clear()

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[+] Connecting...")
        self.socket.connect((self.SERVER_IP, self.SERVER_PORT))
        print("[+] Connected")

    def send(self, data):
        self.socket.sendall(json.dumps(data).encode("utf-8"))

    def recv(self):
        result = self.socket.recv(1024)
        result = json.loads(result.decode("utf-8").strip())
        return result

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_banner(self):
        print(banner)

    def list_rooms(self):
        print("Available rooms:")
        self.send({"command": "list"})
        rooms = self.recv()
        t = Texttable()
        t.add_rows(rooms)
        print(t.draw())

    def print_help(self):
        print("quit / exit / q      - disconnect end exit")
        print("join <room>          - join room")
        print("list rooms / list    - list rooms")
        print("new room / new       - create a new room")

    def prepare_chat(self):
        self.clear()
        print(f"[+] Joined {self.room}")
        print("[*] Type exit/quit/q to exit room\n")

    def handle_commads_input(self):
        while True:
            command = input(">> ")
            if command == "help" or command == "?":
                self.print_help()
            elif command == "quit" or command == "exit" or command == "q":
                self.quit()
                break
            elif command.startswith("join"):
                room_name = command[5:]
                self.send({
                    "command": "join",
                    "args": {"room_name": room_name}
                })
                resp = self.recv()
                if resp["state"] == "failed":
                    print("[-] There is no such room")
                    continue

                self.room = room_name
                self.prepare_chat()

                chat = Chat(self.socket.dup(), self.room)
                chat.run()
                self.socket.setblocking(True)

                self.clear()
                self.print_banner()
                self.list_rooms()
            elif command.startswith("list"):
                self.list_rooms()
            elif command.startswith("new"):
                name = input("Room name: ")
                is_public = input("Public? (y/n): ")
                is_public = True if is_public.lower() == "y" else False

                self.send({
                    "command": "new",
                    "args": {
                        "name": name,
                        "is_public": is_public
                    }
                })
                resp = self.recv()
                print(f"[+] Created {'public' if is_public else 'private'} room {name}")
            else:
                print("[-] No such command")

    def quit(self):
        print("[+] Exiting")
        self.send({"command": "quit"})
        self.socket.close()
        print("Goodbye")

    def run(self):
        os.environ['TERM'] = 'xterm'
        self.connect()
        self.clear()
        self.print_banner()
        self.list_rooms()
        print("Type ? or help for help")
        self.handle_commads_input()


c = Client()
c.run()
