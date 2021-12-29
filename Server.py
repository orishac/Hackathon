import socket
import os
import time
import struct
from threading import Lock, Thread
from scapy.arch import get_if_addr
from random import randrange
from _thread import *
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

    
#to avoid hard coded things, this is how we get the addresses
port = 2008
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
TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
TCP.bind(('', port))
TCP.listen(2)


  
#setting up the basis for the game
game_lock = Lock()
already_won = False
winning_client = "no-winner"

# for a limited time of 10 seconds send broadcast through the UDP socket
def broadcastSender():
    try:
        now = time.time()
        stop = now + TIMEOUT
        while time.time() < stop:
            buffer = struct.pack('IBH', 0xabcddcba, 0x2, port)
            UDP.sendto(buffer, (UDP_ip, destination_port))
            time.sleep(1) 
    except:
        print("something went wrong in sending offers")

def decide_winner(socket, correctAns, winningName, loserName):
    global already_won
    global game_lock
    global winning_client
    data = socket.recv(BYTES_TO_RECIEVE).decode()
    game_lock.acquire()
    if already_won == False: 
        if data == str(correctAns):
            winning_client = winningName
            game_lock.release()
            already_won = True
            return
        winning_client = loserName   
        game_lock.release()
        return
    if already_won == True: 
            game_lock.release()
            already_won = True
            return


def collect_data(clientSocket1 ,clientSocket2, correctAns, clients_names):
    global already_won
    global winning_client
    #setting the global variables to default
    already_won = False
    winning_client = "no-winner"
    clientSocket1.settimeout(TIMEOUT)
    clientSocket2.settimeout(TIMEOUT)
    reads,_,_ = select.select([clientSocket1, clientSocket2], [], [], TIMEOUT)
    #the first client socket that receive answer entering the functionality that checks the answer and determine the winner
    if clientSocket1 in reads:
        decide_winner(clientSocket1, correctAns, clients_names[0], clients_names[1]) 
    if clientSocket2 in reads:
        decide_winner(clientSocket2, correctAns, clients_names[1], clients_names[0])
    return

    
                            
# The actual game start in this function
# listen on socket in order to get clients name, then sends them random math question
# in the end, detemine which client won and sent an appropiate question
def gameManager(clients, TCPsocket):
    firstClientName = clients[0][0].recv(BYTES_TO_RECIEVE).decode()
    secondClientName = clients[1][0].recv(BYTES_TO_RECIEVE).decode()
    clients[0][0].settimeout(TIMEOUT)
    clients[1][0].settimeout(TIMEOUT)
    #generate the question that will be sent to the clients
    firstNumber = randrange(5)
    secondNumber = randrange(6)
    startMessage = "Welcome to Quick Maths.\n"
    startMessage += "Player 1: " + firstClientName + '\n'
    startMessage += "Player 2: " + secondClientName + '\n'
    startMessage += "==\n"
    startMessage += "Please answer the following question as fast as you can:\n"
    startMessage += "How much is "+str(firstNumber)+"+"+str(secondNumber)+"?\n"
    sum = firstNumber + secondNumber
    message = startMessage.encode()
    #send the question to the clients through each socket
    clients[0][0].sendall(message)
    clients[1][0].sendall(message)
    namesTuple = [firstClientName, secondClientName]

    #give the responsibility for collecting the data from both users to another thread    
    receive_answer = Thread(target = collect_data,args= ((clients[0][0]), clients[1][0], sum, namesTuple)) #open thread for first client to get its answer
    receive_answer.start()
    receive_answer.join() 
        
    #generate the message taht decleres who is the winning client
    finish_game_message = "Game over!\nThe correct answer was "+ str(sum) +"!\n\n"
    winnerClient = finish_game_message + "Congratulations to the winner: "+ winning_client +"\n"
    draw_message = finish_game_message + "The game ended with a draw\n"
    if winning_client == "no-winner": 
        end_message = draw_message 
    else:
        end_message = winnerClient

    print(colors.CYAN + end_message)

    #send the results to both clients through their respective sockets
    end_message = end_message.encode()
    clients[0][0].sendall(end_message)
    clients[1][0].sendall(end_message)



 #a thread run this function to connect new clients into a list which it will be work with later       
def connect_clients(connection_client):
    global TCP
    while len(connection_client) < 2:
        try:         
            print("a")
            connection, client_address = TCP.accept()
            print("b")
            client_tuple = [connection, client_address]
            connection_client.append(client_tuple)
            print(colors.BLUE + "New Player Added To The Game")
        except:
            print("There was a problem while connecting new player to the game")


def main():
    message = "Server started, listening on IP address " + ip_address
    print(colors.CYAN + message)
    while True:
        time.sleep(1)  # reduce CPU preformence
        connected_client = [] # enpty list for adding clients later
        client_connector = Thread(target=connect_clients, args=(connected_client,))  # listen and add new client to the game
        sending = Thread(target=broadcastSender, args=())
        sending.start()
        client_connector.start()
        sending.join()
        client_connector.join()
        gameManager(connected_client, TCP)  # start the actual game function
        print("Game over, sending out offer requests...")  #END GAME


if __name__ == '__main__':
    main()