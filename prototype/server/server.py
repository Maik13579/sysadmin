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
import time
import datetime

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


class Server():

    def __init__(self, name):
        self.name = name
        self.connections = {}
        self.recording = False
        self.filename = ""
        self.timer = None
        self.video = None

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

        self.secure_connection = Connection(master_sock)
        self.key = self.secure_connection.get_key()
        self.secure_connection.send("SERVER")

        while True:
            # get port and key from master
            msg = self.secure_connection.recv().decode()
            port, key = msg.split(':')
            port = int(port)
            if port in self.connections:
                #check if key is right
                if key != self.connections[port].get_key():
                    continue
                # send ack. port:key
                msg+=":END"
                self.secure_connection.send(msg)
                self.connections.pop(port)
                continue

            # send ack. port:key
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
        sock.settimeout(10)
        secure_connection = Connection(sock, False,  key)

        # add connection to dictionaries
        self.connections[port] = secure_connection

        last_frame = None

        while port in self.connections:
            try:
                msg = secure_connection.recv()
            except:
                print('timeout on port: '+str(port))
                del self.connections[port]
            frame = cv2.imdecode(pickle.loads(msg), cv2.IMREAD_COLOR)
            frame, last_frame = self._detect_motion(frame, last_frame)
            if self.recording:
                self.video.write(frame)
            
            cv2.imshow(self.name+"| Cam on port: "+str(port), frame)
            if cv2.waitKey(1):
                pass

        del secure_connection
        cv2.destroyWindow(self.name+"| Cam on port: "+str(port))

    #def _RSA_encrypt(self, msg, key):
    #    cipher = PKCS1_OAEP.new(key)
    #    return cipher.encrypt(msg)

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
                self.start_recording()
        return frame, last_frame
    
    def start_recording(self):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
        
        self.recording = True
        if self.timer:
            self.timer.cancel()
        else:
            self.filename = str(datetime.datetime.now()) + ".avi"
            self.video = cv2.VideoWriter(self.filename, fourcc, 20, (640, 480))
        self.timer = threading.Timer(5, self.stop_recording)
        self.timer.start()

    def stop_recording(self):
        self.recording = False
        self.filename = ""
        self.timer = None
        self.video = None

if __name__ == '__main__':
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        exit(1)

    server = Server(name)
