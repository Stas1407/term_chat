import asyncio
import sys
import aioconsole
import readline
import json


class Chat:
    def __init__(self, socket, room):
        self._socket = socket
        self._reader = object
        self._writer = object
        self._leave_room = object
        self._room = room

    def send(self, data):
        self._writer.write(json.dumps(data).encode("utf-8"))

    async def recv(self):
        result = await self._reader.read(1024)
        result = json.loads(result.decode("utf-8").strip())
        return result

    def print_message(self, string):
        print(f"\r                                                                         \rsender: {string}")
        sys.stdout.write(f"\r{self._room} > ")

    async def handle_chat_receiving(self):
        while True:
            data = await self.recv()
            msg = data["message"]
            if self._leave_room.is_set():
                break
            self.print_message(msg)

    async def handle_chat_sending(self):
        while True:
            msg = await aioconsole.ainput(f"{self._room} > ")
            if msg == "exit" or msg == "quit" or msg == "q":
                self._leave_room.set()
                self.send({"message": "quit"})
                break
            elif msg != "":
                self.send({"message": msg})

    async def handle_chat(self):
        self._leave_room = asyncio.Event()
        self._reader, self._writer = await asyncio.open_connection(sock=self._socket)
        await asyncio.gather(self.handle_chat_sending(), self.handle_chat_receiving())
        self._writer.close()

    def run(self):
        asyncio.run(self.handle_chat())
