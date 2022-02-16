from pyDH import DiffieHellman
import json
from cryptography.fernet import Fernet
import base64
from settings import username


class Session:
    def __init__(self, socket):
        self.socket = socket
        self._dh = DiffieHellman()
        self._fernet = ""

    @property
    def fernet(self):
        return self._fernet

    def _send(self, data):
        self.socket.sendall(json.dumps(data).encode("utf-8"))

    def _recv(self):
        resp = self.socket.recv(1024)
        return json.loads(resp.decode("utf-8"))

    def send(self, data):
        data = json.dumps(data).encode("utf-8")
        self.socket.send(self._fernet.encrypt(data))

    def recv(self):
        data = self.socket.recv(1024)
        data = self._fernet.decrypt(data)
        return json.loads(data)

    def close(self):
        self.socket.close()

    def start(self):
        try:
            # Get server's public key
            server_key = self._recv()["public_key"]
        except KeyError:
            print("[-] Invalid server response")
            raise ConnectionError

        # Send my public key to the server
        pub_key = self._dh.gen_public_key()
        self._send({"public_key": pub_key})

        # Generate shared key
        shared_key = self._dh.gen_shared_key(server_key)
        shared_key = base64.b64encode(bytes.fromhex(shared_key))
        self._fernet = Fernet(shared_key)

        # Send username / test message to the server
        msg = {"username": username}
        self.send(msg)

        # Receive test message back
        msg2 = self.recv()
        if msg2 != msg:
            print("[-] Couldn't establish encrypted connection")
            raise ConnectionError
