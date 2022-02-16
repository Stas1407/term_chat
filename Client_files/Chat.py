import asyncio
import sys
import aioconsole
import readline
from Client_files.utils import *
from Client_files.ChatSession import ChatSession


class Chat:
    def __init__(self, room):
        self._leave_room = object
        self._room = room

    def print_message(self, string, sender):
        print(f"\r                                                                         \r{sender}: {string}")
        sys.stdout.write(f"\r{self._room} > ")

    async def handle_chat_receiving(self):
        while True:
            data = await self.session.recv()
            if self._leave_room.is_set():
                break
            msg = data["message"]
            sender = data["sender"]
            self.print_message(msg, sender)

    async def handle_chat_sending(self):
        while True:
            msg = await aioconsole.ainput(f"{self._room} > ")
            if msg == "exit" or msg == "quit" or msg == "q":
                self._leave_room.set()
                self.session.send({"message": "quit"})
                break
            elif msg != "":
                self.session.send({"message": msg})

    async def handle_chat(self, fernet, socket):
        self._leave_room = asyncio.Event()
        reader, writer = await asyncio.open_connection(sock=socket)
        self.session = ChatSession(reader, writer, fernet)
        
        await asyncio.gather(self.handle_chat_sending(), self.handle_chat_receiving())
        self.session.close()

    def prepare_chat(self):
        clear()
        print(f"[+] Joined {self._room}")
        print("[*] Type exit/quit/q to exit room\n")

    def run(self, fernet, socket):
        self.prepare_chat()
        asyncio.run(self.handle_chat(fernet, socket))
