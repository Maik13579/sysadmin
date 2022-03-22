import cv2
import pickle
import struct
import socket
import sys
from cryptography.fernet import Fernet
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import threading
import hashlib

from network import Connection

class Server():

    def __init__(self, name):
        self.name = name
        self.connections = {}

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
        master_key = Fernet.generate_key()
        print("generate key")

        # encrypt it with master publickey and send it to master
        msg = self._RSA_encrypt(master_key, self.master_pubkey)
        master_sock.send(msg)
        print("send key")

        self.secure_connection = Connection(master_sock, master_key)
        self.secure_connection.send("SERVER")

        print("waiting for camera connection")

        while True:
            # get port and key from master
            msg = self.secure_connection.recv().decode()
            port, key = msg.split(':')
            port = int(port)
            if port in self.connections:
                #check if key is right
                if key != self.connections[port].get_key():
                    print("wrong key: ", key)
                    continue
                # send ack. port:key
                print("send ack")
                msg+=":END"
                self.secure_connection.send(msg)
                self.connections.pop(port)
                continue

            print("received port and key")

            # send ack. port:key
            print("send ack")
            msg += ":START"
            self.secure_connection.send(msg)

            t = threading.Thread(target=self._handle_camera, args=(port, key, ))
            t.start()


    def _handle_camera(self, port, key):
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(("", port))
        secure_connection = Connection(sock, key)

        # add connection to dictionaries
        self.connections[port] = secure_connection
        print("camera connected: port=",port)

        last_frame = None

        while port in self.connections:
            msg = secure_connection.recv()
            frame = cv2.imdecode(pickle.loads(msg), cv2.IMREAD_COLOR)
            frame, last_frame = self._detect_motion(frame, last_frame)
            cv2.imshow(self.name+"| Cam on port: "+str(port), frame)
            if cv2.waitKey(1):
                pass

        del secure_connection
        cv2.destroyWindow(self.name+"| Cam on port: "+str(port))
        print("close connection to port:", port)

    def _RSA_encrypt(self, msg, key):
        cipher = PKCS1_OAEP.new(key)
        return cipher.encrypt(msg)

    def _detect_motion(self, frame, last_frame):
        #if it's the first image we can't detect changes
        if last_frame is None:
            last_frame = frame.copy()
            return frame, last_frame

        diff = cv2.absdiff(frame, last_frame)
        last_frame = frame.copy()

        diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        diff_blur = cv2.GaussianBlur(diff_gray, (5, 5),0 )
        _, thresh_bin = cv2.threshold(diff_blur, 20, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(thresh_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) > 500:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        return frame, last_frame
    

if __name__ == '__main__':
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        print("python server.py [name]")
        exit(1)

    server = Server(name)
