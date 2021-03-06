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


#TODO generate and share at setup
PUBKEY = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAx0tQNViIcbpWUEXneuTO
eUqMJGLCbqY4PeoACFtug+yjLjESik/Ry/82bKTMRZ8nCp0P3mxFYwP9a3MATTUv
BCsaO2e6EkDL3wx/iPYxL3BPDSfipG6oYTvdSPKSsETOetn1R1TXNa6cm+JJUbyL
woe5GX55tiKy5wViPfCIas4aNWmRo1nt3mb5/uUW/lzXdSUsIDp3uneK/e4mJAdp
c5yNZHM+RbrvrwGRVXIsgOZwbA6SdQMYW5cv5SbnfW4HVhX+8ryIxWfjYEg4S1A0
ZroPiNGm6QGt05LLRrWjyj2rCAJuzx+a5+9VatovvkDoLB62NOpA6H8Mo5iKzajA
LQIDAQAB
-----END PUBLIC KEY-----'''

PRIVATEKEY = '''-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAx0tQNViIcbpWUEXneuTOeUqMJGLCbqY4PeoACFtug+yjLjES
ik/Ry/82bKTMRZ8nCp0P3mxFYwP9a3MATTUvBCsaO2e6EkDL3wx/iPYxL3BPDSfi
pG6oYTvdSPKSsETOetn1R1TXNa6cm+JJUbyLwoe5GX55tiKy5wViPfCIas4aNWmR
o1nt3mb5/uUW/lzXdSUsIDp3uneK/e4mJAdpc5yNZHM+RbrvrwGRVXIsgOZwbA6S
dQMYW5cv5SbnfW4HVhX+8ryIxWfjYEg4S1A0ZroPiNGm6QGt05LLRrWjyj2rCAJu
zx+a5+9VatovvkDoLB62NOpA6H8Mo5iKzajALQIDAQABAoIBAAMoV/XUQWOTQxDV
fUOdkIZ49pQvuaveu4hZhEG8XFHcI0ieCL66Gb+de25ZKHzT/AeIBSB3KVT/cckh
Ms5OCTaL5OvTT9ICxqY5nhvWGcgzEuU+/FUjBSQvKxJDppg2NUYsdnHj9kVtv5Ks
ESBxZ3odb4KqanNWWSoYwi4o+PGg4SvCh6EoKmEsVzKf0n2RtMMs/tdUX7OQA4uO
NfsZ7Z/9pAqtvEzGKUb8HScSaop3QKsctfdVtKgGjNuUo3bV435j/TmyXnR91ot6
5TBgSx+WaoyA5vcUGFW6avBTdGR5y+9YLUgm7rWNXqL2JKAc0DDLsevrqG+MXIab
Ort3cYUCgYEA1FwkiZYlf004tALmmdilCwq8A/0Olug4Eoomm5sYg8fCS66I0vcj
jRrotvBntwAgUXj8+6uaozudPx7oZAPPcDW0wU/iOAqfAozsTQMDPypz9BReI6Yj
NwmFHjVlPgSsFcqGgxjbhahTDZ5G0njwyABkdt6gnIOgkPe5y+pN9qcCgYEA8D/O
egWLIcd9NrAIySdThZakGxvcNSycpZ3XMo+A95mhs5+QmBx9Gc/6wr/0KJTLdmHX
Ky8uzuSqmi+aRoqDrOvJYuRnqknf8hWFbgBeZgN+xMA3SkPrUgTj4qZ5VXfArgmD
0EE5RPLJvuVsG608aApsVKyIh/sc47DSZOpzgQsCgYA70bzlGOt1Ia6QXqTQv4s2
Qg7WXMloTv/EkS/w806DiJi9suuN6doU3HijV7MPhLSV3qv8xMkppBhWeIFj8wLT
C/3f2n3R5YQHNuU1iFy4xV+maLpf9mPDFCZwbQAY6T4EYWlksnLcAp9qnaQ7k5/X
5uxl466AiD+Jto6a12SgzwKBgHFQtxOIj9IT5HQp3Ur7OIK2xZpfrqKJ8yyOYRTg
6KRgGwu8xBdqwHqvRQgcP43weHLSvQkKTRqacfkdYLfK10Z1Q9xX/KkuBOmKyw9S
LzQQi/dC7hEiLdjWo6GggXQVcpTjuf889EUX+p4GWdJICEjOOcBKTG9OupaOLP4a
MvZ3AoGALx0iuU4n/78KTfxu56o+bqVyfD/cNJOrXmfXoETJJEsKwiL/96OXtofw
f8brOuPjBdWd6x243FTfaFbTV9RumGO+lVFCchumsmYbSyp4W3t0HrR0o97LJbg7
OmhNzYSFh6l1IT0bYpdljnsKoY6i+fkqG4NvkBln+EJqZCZvL+0=
-----END RSA PRIVATE KEY-----'''


class Master():

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.cameras = {} #key = port, value = { "conn" : Connection, "online" : Boolean}
        self.servers = {} #key = id, value = { "conn" : Connection, "ports" : [ports]}

        # generate RSA
        #print("generate public key")
        #self.secret = RSA.generate(2048)
        #self.public = self.secret.publickey()
        #print(self.secret.export_key('PEM'))
        #print(self.public.export_key('PEM'))

        self.secret = RSA.import_key(PRIVATEKEY)
        self.public = RSA.import_key(PUBKEY)

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
        while True:
            for port in self.cameras.copy():
                if port in ports:
                    continue
                for id_ in self.servers.copy():
                    if len(self.servers[id_]['ports'])==0:
                        ports.append(port)
                        self.servers[id_]['ports'].append(port)
                        break

                

    def _accept_socket(self):
        while True:
            conn, addr = self.sock.accept()
            t = threading.Thread(target=self._handle_socket, args=(conn, addr, ))
            t.start()

    def _handle_socket(self, conn, addr):
        secure_connection = Connection(conn, True)
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
            del secure_connection

    def _handle_camera(self, secure_connection):
        port = 4000
        while port in self.cameras: #if port is in use choose a new one
            port += 1
        self.cameras[port] = {'conn' : secure_connection.get_key().decode(), 'online' :  True }
        secure_connection.send(str(port))

        del secure_connection
        #self.cameras.pop(port)
        return

    def _handle_server(self, id_, secure_connection):
        ports = []

        while True:
            # check for new ports
            for port in self.servers[id_]['ports']:
                if port not in ports:
                    #send port and key from camera to server
                    msg = str(port)+':'+self.cameras[port]['conn']
                    secure_connection.send(msg)

                    #wait for ack msg
                    ack = secure_connection.recv().decode()
                    if ack != msg+":START":
                        continue
                    ports.append(port)

            # check if you shouldn't listen to a port
            for port in ports:
                if port not in self.servers[id_]['ports']:
                    #send port to server that he stop listen to it
                    msg = str(port)+':'+self.cameras[port]['conn']
                    secure_connection.send(msg)

                    #wait for ack msg
                    ack = secure_connection.recv().decode()
                    if ack != msg+":END":
                        continue
                    ports.remove(port)

        self.servers.pop(id_)
        del secure_connection

    #def _RSA_decrypt(self, msg):
    #    cipher = PKCS1_OAEP.new(self.secret)
    #    return cipher.decrypt(msg)
    
if __name__ == '__main__':
    if len(sys.argv) > 2:
        ip = sys.argv[1]
        port = int(sys.argv[2])
    else:
        exit(1)
    
    master = Master(ip, port)
