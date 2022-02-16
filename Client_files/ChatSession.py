import json


class ChatSession:
    def __init__(self, reader, writer, fernet):
        self._reader = reader
        self._writer = writer
        self._fernet = fernet

    def send(self, data):
        data = json.dumps(data).encode("utf-8")
        data = self._fernet.encrypt(data)
        self._writer.write(data)

    async def recv(self):
        resp = await self._reader.read(1024)
        resp = self._fernet.decrypt(resp)
        resp = json.loads(resp)
        return resp

    def close(self):
        self._writer.close()
