import socket
import sys
import os
import time
#from Server import TCP
import socket
import struct
from threading import Thread
import select




TIMEOUT = 10
BYTES_TO_READ = 1024
destination_port = 13117
port = 2178
UDP_ip = "172.1.255.255"

class style:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


def get_from_server(tcp):
    now = time.time()
    stop = now + 10
    server_has_answered = False
    tcp.settimeout(TIMEOUT)
    readers, writers, errors = select.select([sys.stdin, tcp], [], [], TIMEOUT)
    if sys.stdin in readers:
        c = sys.stdin.readline()[0]
        try:
            c = c.encode()
            tcp.sendall(c)
        except:
            tcp.close()
            return
    if tcp in readers:
        message = tcp.recv(BYTES_TO_READ)
        message = message.decode()
        sys.stdout.write(message)
        server_has_answered = True
    if not server_has_answered:
        try:
            print(tcp.recv(BYTES_TO_READ).decode())
        except:
            pass
    tcp.close()
    