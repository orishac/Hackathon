import random
import socket
import os
import time
import struct
from threading import Lock, Thread
from scapy.arch import get_if_addr
from random import randrange
from _thread import *

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

    
#to avoid hard coded things, this is how we get the addresses
port = 2375
ip_address = get_if_addr('eth1')
#ip_address = "0.0.0.0"
destination_port = 13117
UDP_ip = '<broadcast>'
TIMEOUT = 10
BYTES_TO_RECIEVE = 1024

#opening the UDP and TCP connections
UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
UDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
UDP.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
UDP.bind(('', port))
TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
TCP.bind(('', port))
TCP.listen()


# for a limited time of 10 seconds send broadcast through the UDP socket
def broadcastSender():
    try:
        now = time.time()
        stop = now + TIMEOUT
        while time.time() < stop:
            UDP.sendto((struct.pack('LBH', 0xabcddcba, 0x2, port)), (UDP_ip, destination_port))
            time.sleep(1)
    except:
        print("something went wrong in sending offers")

 #a thread run this function to connect new clients into a list which it will be work with later       
def connect_clients(connection_client, sock):
    while len(connection_client) < 2:
        try:
            connection, client_address = sock.accept()
            client_tuple = [connection, client_address]
            print(client_address)
            connection_client.append(client_tuple)
            print(style.BLUE + "New Player Added To The Game\n")
        except:
            ()


def main():
    message = "Server started, listening on IP address " + ip_address
    print(style.CYAN + message)
    while True:
        time.sleep(1)  # reduce CPU preformence
        connected_client = [] # enpty list for adding clients later
        client_connector = Thread(target=connect_clients, args=(connected_client, TCP,))  # listen and add new client to the game
        sending = Thread(target=broadcastSender, args=())
        sending.start()
        client_connector.start()
        sending.join()
        client_connector.join()
        gameManager(connected_client, TCP)  # start the actual game function
        print("Game over, sending out offer requests...")  #END GAME


if __name__ == '__main__