import socket
import sys
import os
import socket
import struct
from threading import Thread
import select

class colors:
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


TIMEOUT = 10
BYTES_TO_READ = 1024
destination_port = 13117
port = 2178


def get_from_server(TCP_Socket):
    got_answer = False
    TCP_Socket.settimeout(TIMEOUT)
    readers, writers, errors = select.select([sys.stdin, TCP_Socket], [], [], TIMEOUT)
    #for every objects that is ready to be read from
    #read from it as expected to read from this kind of object 
    if sys.stdin in readers:
        c = sys.stdin.readline()[0]
        try:
            c = c.encode()
            TCP_Socket.sendall(c)
        except:
            TCP_Socket.close()
            return
    if TCP_Socket in readers:
        message = TCP_Socket.recv(BYTES_TO_READ)
        message = message.decode()
        sys.stdout.write(message)
        got_answer = True
    if not got_answer:
        try:
            print(TCP_Socket.recv(BYTES_TO_READ).decode())
        except:
            pass
    TCP_Socket.close()

def main():
    print(colors.GREEN + "Client started, listening for offer requests...")
    while True:
        #opening UDP socket for broadcast and TCP socket for game
        UDP_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  
        UDP_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        UDP_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        UDP_sock.bind(('', destination_port))
        TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        data, addr = UDP_sock.recvfrom(12)
        server_ip_address = str(addr[0])
        UDP_sock.close()
        #decode the data
        try:
            cookie, message_type, server_tcp_port = struct.unpack('IBH', data)  # get message and encode it as a the given format
            if cookie == 0xabcddcba or message_type == 0x2:  # check if the message is as the expected format
                print(colors.GREEN + "Received offer from " + server_ip_address + " attempting to connect...")
            TCP_socket.connect((server_ip_address, server_tcp_port))
            nickname = input("Type In Your Nickname: ")
            nickname = nickname.encode()
            TCP_socket.sendall(nickname)
            sys.stdout.write(colors.YELLOW + TCP_socket.recv(BYTES_TO_READ).decode())  #get message of connecting to server and print it it to user
            game = Thread(target=get_from_server, args=(TCP_socket,))
            game.start() 
            game.join()
            print(colors.RED + "Server disconnected, listening for offer requests...")
        except:
            ()

            

if __name__ == '__main__':
    main()    