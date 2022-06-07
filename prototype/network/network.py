#handles the connection between two components
#uses diffie hellmann for key exchange
#TODO use digital signature for authentication

from cryptography.fernet import Fernet

import pyDHE
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class Connection():

    def __init__(self, sock, isMaster = False, key = None):
        self.sock = sock
        self.isMaster = isMaster
        if not key: #use diffie hellmann to get a key
            self._diffie_hellmann()
            print('new connection with '+str(self.getpeername()))
        else:
            self.key = key
            print('listening on port '+str(self.getsockname()[1]))
        self.fernet = Fernet(self.key)
        

    def __del__(self):
        try:
            print('close connection with '+str(self.getpeername()))
        except:
            print('close connection on port '+str(self.getsockname()[1]))
        self.sock.close()

    def _diffie_hellmann(self):
        DHE = pyDHE.new()

        self.sock.send(str(DHE.getPublicKey()).encode())
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
        #if msg is str encode it
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

