'''
Created on Jul 31, 2019

@author: Ethan

Cobra Chat is a chatroom program written in Python.
Copyright (C) 2019 Ethan Wall

This file is part of Cobra Chat.

Cobra Chat is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Cobra Chat is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Cobra Chat.  If not, see <https://www.gnu.org/licenses/>.
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
address = input("Enter server address: ")
port = int(input("Enter port: "))

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
