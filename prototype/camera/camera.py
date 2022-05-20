import cv2
import socket
import sys
import pickle
import struct
from cryptography.fernet import Fernet
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

from network import Connection

PUBKEY = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAycTnEETL6uU8iOBFLBv8\nuxx3NtDr6XBckJ5HnB4n3Y6XsXYXIbxbD/h0MmQ8eeWX/QVoixI1JFU+9aZWIInv\nvl9E1gGWjAxU6fPkN8dnZsws8EVAdqq9LDUcOtesxBLjPvZtsO4zXDHU1BYKcEc1\n4r37owo+ACwhY6HOrM0PbegUqiXO9O0SOTPC4bZ1++DQjMK6IJpcynQibl+3cvEE\nIqsFR9AVhm5/2EG59mgW32+MP4pWTTrzhyGQJnFa8vMmovc9pYtnAUlOdFa9gLKs\nS2km0kP1plVykV4h+GK1AD7gzYHPeQmKrM4E9R77gq7u91WrWHeGR2pOSktzc0kq\nYQIDAQAB\n-----END PUBLIC KEY-----'

class Camera():

    def __init__(self):

        # Video Capture
        self.vcap = cv2.VideoCapture(0)
        if not self.vcap.isOpened():
            print('no camera found!')
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

        self.master_pubkey = RSA.import_key(PUBKEY)

        # generate symetric key
        self.key = Fernet.generate_key()
        print(master_sock.getsockname(), " -> ", master_sock.getpeername(),"| generate key")

        # encrypt it with master publickey and send it to master
        msg = self._RSA_encrypt(self.key, self.master_pubkey)
        master_sock.send(msg)
        print(master_sock.getsockname(), " -> ", master_sock.getpeername(),"| send key")

        secure_connection = Connection(master_sock, self.key)
        secure_connection.send("CAM")

        # get port to stream on
        self.port = int(secure_connection.recv())

        # Create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 10000000)


        print("streaming on port ", self.port)
    
        #get picture dump it, encrypt it and send it
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
