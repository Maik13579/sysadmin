import cv2
import socket
import sys
import pickle
import struct
from cryptography.fernet import Fernet
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

from network import Connection


class Camera():

    def __init__(self):

        # Connect to Master
        master_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connected = False
        while not connected:
            try:
                master_sock.connect(("127.0.0.1", 5555))
                connected = True
            except:
                pass

        # get Master publickey
        msg = master_sock.recv(100000).decode()
        print("received public key")
        self.master_pubkey = RSA.import_key(msg)

        # generate symetric key
        self.key = Fernet.generate_key()
        print("generate key")

        # encrypt it with master publickey and send it to master
        msg = self._RSA_encrypt(self.key, self.master_pubkey)
        master_sock.send(msg)
        print("send key")

        secure_connection = Connection(master_sock, self.key)
        secure_connection.send("CAM")

        # get port to stream on
        self.port = int(secure_connection.recv())

        # Create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 10000000)
        self.sock.settimeout(0.2)

        # Video Capture
        self.vcap = cv2.VideoCapture(0)
        if not self.vcap.isOpened():
            print('no camera found!')
            exit(1)

        print("streaming on port:",self.port)

        while True:
            _, frame = self.vcap.read()
            ret, buffered = cv2.imencode(".jpg", frame,
                    [int(cv2.IMWRITE_JPEG_QUALITY),30])
            dumped = pickle.dumps(buffered)
            self.sock.sendto(self._encrypt(dumped, self.key), ('<broadcast>', self.port))
        vcap.release()


    def _RSA_encrypt(self, msg, key):
        cipher = PKCS1_OAEP.new(key)
        return cipher.encrypt(msg)


    def _encrypt(self, msg, key):
        fernet = Fernet(key)
        encrypted_msg = fernet.encrypt(msg)
        return encrypted_msg



if __name__ == '__main__':
    cam = Camera()
