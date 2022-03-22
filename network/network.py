from cryptography.fernet import Fernet


class Connection():

    def __init__(self, sock, key):
        self.sock = sock
        self.key = key
        self.fernet = Fernet(key)

    def __del__(self):
        self.sock.close()

    def _decrypt(self, msg):
        try:
            decrypted_msg = self.fernet.decrypt(msg)
        except:
            print("Can't decrypt message!")
            exit(0)
        return decrypted_msg


    def _encrypt(self, msg):
        return self.fernet.encrypt(msg)


    def send(self, msg):
        if isinstance(msg, str):
            msg = msg.encode()
        msg = self._encrypt(msg)
        self.sock.send(msg)

    def recv(self):
        return self._decrypt(self.sock.recv(100000))

    def get_key(self):
        return self.key
    
    def getsockname(self):
        return self.sock.getsockname()

    def getpeername(self):
        return self.sock.getpeername()
