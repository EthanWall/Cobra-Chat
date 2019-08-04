'''
Created on Jul 31, 2019

@author: Ethan
'''
import socket
import threading
import traceback

#Define variables
prefix = "/" #Command prefix
running = True

#Create functions
#Receive messages from the server
def recieveMsg(sock):
    try:
        msg = sock.recv(1024).decode()
    except (ConnectionResetError, ConnectionAbortedError):
        print("Connection ended by server.")
        running = False
        return None
    except Exception:
        traceback.print_exc()
        return None
    
    return msg

#Outputs all messages sent to the client
def listenToChat(sock):
    while running:
        msg = recieveMsg(sock)
         
        if msg != None:
            print(msg)
        else:
            return

#Sends a message to a server or client
def send(sock, data):
    try:
        sock.send(data.encode("utf-8"))
    except ConnectionResetError:
        pass #Strait up do nothing I don't care
    except Exception:
        traceback.print_exc()

#Create a socket variable
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Get IP address and port to connect to
address = "localhost"#input("Enter server address: ")
port = 20#int(input("Enter port: "))

#Connect to specified IP and port
s.connect((address, port))

#Send the desired username
username = input("Enter your username for this session: ")
send(s, username)

t = threading.Thread(target=listenToChat, args=(s,))
t.start()

while running:
    msg = input("> ")
    if msg == "{0}quit".format(prefix): #Explicitly declare functionality in client for quit command
        s.close()
        running = False
    else:
        send(s, msg)
        
t.join()