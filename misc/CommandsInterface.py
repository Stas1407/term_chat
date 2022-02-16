from misc.Chat import Chat
from misc.utils import clear
from texttable import Texttable
from misc.banner import banner


class CommandsInterface:
    def __init__(self, session):
        self.session = session

    def print_help(self):
        print("quit / exit / q      - disconnect end exit")
        print("join <room>          - join room")
        print("list rooms / list    - list rooms")
        print("new room / new       - create a new room")

    def join_room(self, room_name):
        # Send info to server
        self.session.send({
            "command": "join",
            "args": {"room_name": room_name}
        })

        # Check if succeed
        resp = self.session.recv()
        if "state" not in resp or resp["state"] == "failed":
            print("[-] There is no such room")
            return

        # Give control to chat interface
        chat = Chat(room_name)
        chat.run(self.session.fernet, self.session.socket.dup())
        self.session.socket.setblocking(True)

        clear()
        self.print_banner()
        self.list_rooms()

    def list_rooms(self):
        print("Available rooms:")
        self.session.send({"command": "list"})
        rooms = self.session.recv()
        t = Texttable()
        t.add_rows(rooms)
        print(t.draw())

    def print_banner(self):
        print(banner)

    def create_room(self):
        name = input("Room name: ")
        is_public = input("Public? (y/n): ")
        is_public = True if is_public.lower() == "y" else False

        self.session.send({
            "command": "new",
            "args": {
                "name": name,
                "is_public": is_public
            }
        })
        resp = self.session.recv()

        if resp["state"] != "success":
            print("[-] Room with that name already exists")
            return

        print(f"[+] Created {'public' if is_public else 'private'} room {name}")

    def run(self):
        clear()
        self.print_banner()
        self.list_rooms()
        print("Type ? or help for help")
        while True:
            command = input(">> ")
            if command == "help" or command == "?":
                self.print_help()
            elif command == "quit" or command == "exit" or command == "q":
                break
            elif command.startswith("join"):
                self.join_room(command[5:])
            elif command.startswith("list"):
                self.list_rooms()
            elif command.startswith("new"):
                self.create_room()
            else:
                print("[-] No such command")
