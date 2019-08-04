'''
Created on Jul 31, 2019

@author: Ethan
'''
import socket
import threading
import traceback

clients = {} #Dict of connected clients
prefix = "/" #Command prefix

#Make a socket variable
serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Make socket reusable
serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#Get desired port
port = 20#int(input("Enter port: "))
host = "localhost"

#Listen on the local IP address and the desired port
serversock.bind((host, port))

#Listen for activity on the socket
serversock.listen(5)   

#Broadcast a message to all users (except for users in the exceptions list)
def broadcastAll(msg, exceptions=[]):
    print(msg)
    for user in clients:
        if not user in exceptions:
            user.send(msg.encode("utf-8"))

#Receive typed messages from the user
def recieveMsg(sock):
    try:
        msg = sock.recv(1024).decode()
    except ConnectionResetError: #Connection closed by user
        print("Connection ended by client.")
        closeUser(sock)
        return None
    except Exception:
        traceback.print_exc()
        return None
    
    return msg

#Handle user joining
def initUser(sock):
    #Get the username of a player
    name = recieveMsg(sock)
    
    if name != None:
        #Add the user to a dict of sockets and usernames
        clients[sock] = name
        
        broadcastAll("{0} has joined the chatroom!".format(name), [sock])
        sock.send("Welcome to the chatroom, {0}!".format(name).encode("utf-8"))
        
        handleChat(sock)
    else:
        return

def closeUser(sock):
    try:
        name = clients.pop(sock)
        sock.close()
        broadcastAll("{0} has left the chatroom!".format(name))
    except IndexError:
        print("Attempted to remove a user that does not exist.")
    except Exception:
        traceback.print_exc()

def handleCmd(sock, msg):
    cmd = msg[1:]
    if cmd == "list":
        strOut = "Connected Users:"
        for user in clients:
            strOut += "\n{0}".format(clients[user])
        sock.send(strOut.encode("utf-8"))
    else:
        sock.send("That is not a command!".encode("utf-8"))

#Handle a user chatting
def handleChat(sock):
    running = True
    while running:
        msg = recieveMsg(sock)
        
        if msg != None:
            if msg[:1] == prefix:
                #Run a command
                handleCmd(sock, msg)
            else:
                #Format message
                #[username] message
                msg = "[{0}] {1}".format(clients[sock], msg)
                broadcastAll(msg, [sock])
        else:
            return
    
while True:
    #Accept join requests
    clientsock, addr = serversock.accept()
    t = threading.Thread(target=initUser, args=(clientsock,))
    t.start()