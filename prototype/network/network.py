from cryptography.fernet import Fernet

import pyDHE
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class Connection():

    def __init__(self, sock, id_ = None, key = None):
        self.sock = sock
        if not key:
            self._diffie_hellmann(id_)
        else:
            self.key = key
        self.fernet = Fernet(self.key)

    def __del__(self):
        self.sock.close()

    def _diffie_hellmann(self, id_):
        DHE = pyDHE.new()

        if not id_: #master 
            #receive msg, decode it and convert it to int
            received_public_key = int(self.sock.recv(10000).decode())

            #convert to string, encode it and send  it to master
            self.sock.send(str(DHE.getPublicKey()).encode())
        else: #peer
            #convert to string, encode it and send  it to master
            self.sock.send(str(DHE.getPublicKey()).encode())

            #receive msg, decode it and convert it to int
            received_public_key = int(self.sock.recv(10000).decode())


        key = str(DHE.update(received_public_key))


        #convert key to 32 bytes key, Base64url encoded
        backend = default_backend()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'',
            iterations=100000,
            backend=backend
        )
        self.key = base64.urlsafe_b64encode(kdf.derive(key.encode()))


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

