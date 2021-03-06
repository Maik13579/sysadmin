import cv2
import socket
import sys
import pickle
import struct
from cryptography.fernet import Fernet
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

from network import Connection

PUBKEY = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAx0tQNViIcbpWUEXneuTO
eUqMJGLCbqY4PeoACFtug+yjLjESik/Ry/82bKTMRZ8nCp0P3mxFYwP9a3MATTUv
BCsaO2e6EkDL3wx/iPYxL3BPDSfipG6oYTvdSPKSsETOetn1R1TXNa6cm+JJUbyL
woe5GX55tiKy5wViPfCIas4aNWmRo1nt3mb5/uUW/lzXdSUsIDp3uneK/e4mJAdp
c5yNZHM+RbrvrwGRVXIsgOZwbA6SdQMYW5cv5SbnfW4HVhX+8ryIxWfjYEg4S1A0
ZroPiNGm6QGt05LLRrWjyj2rCAJuzx+a5+9VatovvkDoLB62NOpA6H8Mo5iKzajA
LQIDAQAB
-----END PUBLIC KEY-----'''


class Camera():

    def __init__(self):

        # Video Capture
        vcap = cv2.VideoCapture(0)
        if not vcap.isOpened():
            exit(1)

        # Connect to Master
        master_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connected = False
        while not connected:
            try:
                master_sock.connect(("127.0.0.1", 55555))
                connected = True
            except:
                pass

        master_pubkey = RSA.import_key(PUBKEY)


        secure_connection = Connection(master_sock)
        key = secure_connection.get_key()
        fernet = Fernet(key)
        secure_connection.send("CAM")

        # get port to stream on
        port = int(secure_connection.recv())
        
        del secure_connection

        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 10000000)

        #get picture dump it, encrypt it and send it
        while True:
            _, frame = vcap.read()
            ret, buffered = cv2.imencode(".jpg", frame,
                    [int(cv2.IMWRITE_JPEG_QUALITY),30])
            dumped = pickle.dumps(buffered)
            sock.sendto(fernet.encrypt(dumped), ('<broadcast>', port))
        vcap.release()


    def _RSA_encrypt(self, msg, key):
        cipher = PKCS1_OAEP.new(key)
        return cipher.encrypt(msg)



if __name__ == '__main__':
    cam = Camera()
