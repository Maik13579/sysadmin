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

from network import Connection

class Master():

    def __init__(self, ip, port):
        self.is_shutdown = False
        self.ip = ip
        self.port = port
        self.cameras = {} #key = port, value = { "conn" : Connection, "online" : Boolean}
        self.servers = {} #key = id, value = { "conn" : Connection, "ports" : [ports]}

        # RSA
        print("generate public key")
        self.secret = RSA.generate(2048)
        self.public = self.secret.publickey()

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
            for port in self.cameras.copy():
                if port in ports:
                    continue
                for id_ in self.servers.copy():
                    if len(self.servers[id_]['ports'])==0:
                        ports.append(port)
                        self.servers[id_]['ports'].append(port)
                        break

                

    def _accept_socket(self):
        print("listening on ",self.ip,":",self.port)
        while not self.is_shutdown:
            conn, addr = self.sock.accept()
            t = threading.Thread(target=self._handle_socket, args=(conn, addr, ))
            t.start()

    def _handle_socket(self, conn, addr):
        print(conn.getsockname(), " -> ", conn.getpeername(),'| new connection')  

        #send public key
        print(conn.getsockname(), " -> ", conn.getpeername(), "| send public key")
        conn.send(self.public.exportKey("PEM"))

        #first message has the encrypted key
        msg = conn.recv(10000)
        key = self._RSA_decrypt(msg)

        print(conn.getsockname(), " -> ", conn.getpeername(),"| received key")
        secure_connection = Connection(conn, key)
        msg = secure_connection.recv().decode()

        if msg == 'CAM': # its a camera
            self._handle_camera(secure_connection)
        elif msg == 'SERVER': #its a server
            id_ = 0
            while id_ in self.servers:
                id_ += 1
            self.servers[id_] = {'conn':secure_connection, 'ports':[]}
            self._handle_server(id_, secure_connection)
        else:
            print(conn.getsockname(), " -> ", conn.getpeername(),'| unknown type: ', msg)
            del secure_connection

    def _handle_camera(self, secure_connection):
        port = 4000
        while port in self.cameras: #if port is in use choose a new one
            port += 1
        self.cameras[port] = {'conn' : secure_connection.get_key().decode(), 'online' :  True }
        print(secure_connection.getsockname(), " -> ", secure_connection.getpeername(),"| register camera on port: ",port)
        secure_connection.send(str(port))

        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(10)
        sock.bind(("", port))
        cam_connection = Connection(sock, self.cameras[port]['conn'])

        while self.cameras[port]['online']:
            # check if camera is streaming
            try:
                msg = cam_connection.recv()
            except:
                break

        del secure_connection
        self.cameras.pop(port)
        print(secure_connection.getsockname(), " -> ", secure_connection.getpeername(),"| Connection to camera closed")
        return

    def _handle_server(self, id_, secure_connection):
        ports = []
        online = True

        while not self.is_shutdown and online:
            # check for new ports
            for port in self.servers[id_]['ports']:
                if port not in ports:
                    #send port and key from camera to server
                    msg = str(port)+':'+self.cameras[port]['conn']
                    print(secure_connection.getsockname(), " -> ", secure_connection.getpeername(), "| send port and camera-key")
                    secure_connection.send(msg)

                    #wait for ack msg
                    ack = secure_connection.recv().decode()
                    print(secure_connection.getsockname(), " -> ", secure_connection.getpeername(), "| received ack")
                    if ack != msg+":START":
                        print(secure_connection.getsockname(), " -> ", secure_connection.getpeername(), "| error in ack!")
                        continue
                    ports.append(port)

            # check if you shouldn't listen to a port
            for port in ports:
                if port not in self.servers[id_]['ports']:
                    #send port to server that he stop listen to it
                    msg = str(port)+':'+self.cameras[port]['conn']
                    print(secure_connection.getsockname(), " -> ", secure_connection.getpeername(), "| send port and camera-key")
                    secure_connection.send(msg)

                    #wait for ack msg
                    ack = secure_connection.recv().decode()
                    print(secure_connection.getsockname(), " -> ", secure_connection.getpeername(), "| received ack")
                    if ack != msg+":END":
                        print(addr, "| error in ack!")
                        continue
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