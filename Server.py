import asyncio
import json
from Room import Room

TIMEOUT = 120


class Server(asyncio.Protocol):
    def __init__(self, rooms):
        # Timeout handling
        loop = asyncio.get_running_loop()
        self._timeout_handle = loop.call_later(TIMEOUT, self._quit)

        # Info
        self._ip = ""
        self._port = ""
        self._room = ""
        self._rooms_dict = rooms
        self._mode = "command"

    def _send(self, data):
        self._transport.write(json.dumps(data).encode("utf-8"))

    def _list_rooms(self):
        t = [["Room name", "People"]]
        for name, room in self._rooms_dict.items():
            if room.is_public:
                t.append([name, room.number_of_members()])

        return t

    def connection_made(self, transport):
        ip, port = transport.get_extra_info("peername")
        print(f"[+] Got a connection - {ip}:{port}")

        self._transport = transport
        self._ip = ip
        self._port = port

    def _schedule_new_timeout(self):
        self._timeout_handle.cancel()
        loop = asyncio.get_running_loop()
        self._timeout_handle = loop.call_later(TIMEOUT, self._quit)

    def data_received(self, data):
        self._schedule_new_timeout()

        data = json.loads(data.decode("utf-8"))

        if self._mode == "command":
            if data["command"] == "list":
                self._send(self._list_rooms())
            elif data["command"] == "join":
                self._room = data["args"]["room_name"]

                if self._room in self._rooms_dict:
                    self._rooms_dict[self._room].join(self)
                    self._send({"state": "success"})
                    self._mode = "text"
                else:
                    self._room = ""
                    self._send({"state": "failed"})
            elif data["command"] == "quit":
                self._quit(timeout=False)
            elif data["command"] == "new":
                name, is_public = data["args"]["name"], data["args"]["is_public"]
                room = Room(name, is_public)
                self._rooms_dict[name] = room
                self._send({"state": "success"})
        elif self._mode == "text":
            msg = data["message"]
            if msg == "quit":
                self._mode = "command"
                self._rooms_dict[self._room].leave(self)
                self._room = ""
                self._send({"message": "quit"})
            else:
                for participant in self._rooms_dict[self._room].members:
                    if participant != self:
                        participant.message_from_room(data)

    def message_from_room(self, data):
        self._send(data)

    def _quit(self, timeout=True):
        if timeout:
            print(f"[-] Timeout. Shutting down {self._ip}:{self._port}")
        else:
            print(f"[*] Closing connection {self._ip}:{self._port}")
        self._transport.close()


async def main(host, port):
    room = Room("main", True)
    rooms_dict = {"main": room}
    loop = asyncio.get_running_loop()
    print("[+] Starting server")
    server = await loop.create_server(lambda: Server(rooms_dict), host, port)
    print("[+] Listening")
    await server.serve_forever()

try:
    asyncio.run(main('127.0.0.1', 5000))
except KeyboardInterrupt:
    print("[+] Exiting")
