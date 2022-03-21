import cv2
import pickle
import struct
import socket
import sys
import threading
from cryptography.fernet import Fernet
import Crypto
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import hashlib
import random

from network import Connection

class Master():

    def __init__(self, ip, port):
        self.is_shutdown = False
        self.ip = ip
        self.port = port
        self.cameras = {} #key = port, value = (encryption key, Online)
        self.servers = {} #key = id, value =  (Connection(),[Ports])
        self.currentID = 0

        # RSA
        self.secret = RSA.generate(2048)
        self.public = self.secret.publickey()
        print("generated public key")

        # Create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_binded = False
        while not sock_binded:
            try:
                self.sock.bind((self.ip, self.port))
                sock_binded = True
            except:
                pass
        self.sock.listen(5)

        accept_thread = threading.Thread(target=self._accept_socket)
        accept_thread.start()
        
        # main loop
        ports = []
        while not self.is_shutdown:
            for port, camera in self.cameras.items():
                if port not in ports:
                    for id_, server in self.servers.items():
                        server[1].append(port)
                    ports.append(port)


       #TODO REMOVE OFFLINE CAMS 

            
    def _accept_socket(self):
        print("listening on ",self.ip,":",self.port)
        while not self.is_shutdown:
            conn, addr = self.sock.accept()
            t = threading.Thread(target=self._handle_socket, args=(conn, addr, ))
            t.start()

    def _handle_socket(self, conn, addr):
        print('-'*15,'new connection','-'*15)  

        #send public key
        print("send public key")
        conn.send(self.public.exportKey("PEM"))

        #first message has the encrypted key
        msg = conn.recv(10000)
        key = self._RSA_decrypt(msg)

        print("received key")
        secure_connection = Connection(conn, key)
        msg = secure_connection.recv().decode()

        if msg == 'CAM': # its a camera
            self._handle_camera(secure_connection)
        elif msg == 'SERVER': #its a server
            id_ = self.currentID
            self.currentID += 1
            self.servers[id_] = (secure_connection, [])
            self._handle_server(id_, secure_connection)
        else:
            print('unknown type: ', msg)
            del secure_connection

    def _handle_camera(self, secure_connection):
        port = 4000
        while port in self.cameras: #if port is in use choose a new one
            port = random.randint(4000,5000)
        secure_connection.send(str(port))
        self.cameras[port] = (secure_connection.get_key().decode(), True)
        print("registered camera on port: ",port)

        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(("", port))
        cam_connection = Connection(sock, self.cameras[port][0])

        while self.cameras[port][1]:
            msg = cam_connection.recv()
            frame = cv2.imdecode(pickle.loads(msg), cv2.IMREAD_COLOR)

            cv2.imshow("Cam on port: "+str(port), frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.cameras[port] = (self.cameras[port][0], False)
                break

        del secure_connection
        cv2.destroyWindow("Cam on port: "+str(port))
        print("Connection to camera closed")
        return

    def _handle_server(self, id_, secure_connection):
        ports = []
        online = True

        while not self.is_shutdown and online:
            # check for new ports
            for port in self.servers[id_][1]:
                if port not in ports:
                    #send port and key from camera to server
                    msg = str(port)+':'+self.cameras[port][0]
                    print("send port and camera-key")
                    secure_connection.send(msg)

                    #wait for ack msg
                    ack = secure_connection.recv().decode()
                    if ack != msg+":START":
                        print("error in ack!")
                        continue
                    print("received ack")
                    ports.append(port)

            # check if you shouldn't listen to a port
            for port in ports:
                if port not in self.servers[id_][1]:
                    #send port to server that he stop listen to it
                    msg = str(port)+':'+self.cameras[port][0]
                    print("send port and camera-key")
                    secure_connection.send(msg)

                    #wait for ack msg
                    ack = secure_connection.recv().decode()
                    if ack != msg+":END":
                        print("error in ack!")
                        continue
                    print("received ack")
                    ports.remove(port)

        self.servers.pop(id_)
        del secure_connection


    def _RSA_decrypt(self, msg):
        cipher = PKCS1_OAEP.new(self.secret)
        return cipher.decrypt(msg)
    
if __name__ == '__main__':
    if len(sys.argv) > 2:
        ip = sys.argv[1]
        port = int(sys.argv[2])
    else:
        print("python master.py [ip] [port]")
        exit(1)
    
    master = Master(ip, port)
