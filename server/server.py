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
along with Cobra Chat. If not, see <https://www.gnu.org/licenses/>.
'''
import socket
import threading
import traceback
import tkinter as tk

from tkinter import ttk

clients = {} #Dict of connected clients
prefix = "/" #Command prefix
running = True

#Create functions
#Broadcast a message to all users (except for users in the exceptions list)
def broadcastAll(msg, exceptions=[]):
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
def initUser(sock, sysOut):
    #Get the username of a player
    name = recieveMsg(sock)
    
    if name != None:
        #Add the user to a dict of sockets and usernames
        clients[sock] = name
        
        broadcastAll("{0} has joined the chatroom!".format(name), [sock])
        sock.send("Welcome to the chatroom, {0}!".format(name).encode("utf-8"))
        
        handleChat(sock, sysOut)
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

#Write to a tkinter text element
def output(txt, dest):
    dest.configure(state="normal")
    dest.insert(tk.END, "\n{0}".format(txt))
    dest.configure(state="disable")

#Handle a user chatting
def handleChat(sock, sysOut):
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
                
                output(msg, sysOut)
        else:
            return

def joinListener(serversock, sysOut):
    #Listen for activity on the socket
    serversock.listen(5)
    
    while running:
        #Accept join requests
        clientsock, _ = serversock.accept()
        t = threading.Thread(target=initUser, args=(clientsock, sysOut,))
        t.start() 

#Make a tkinter window
root = tk.Tk()
root.geometry("500x500")
root.title("Cobra Chat Server")

#Set style of window
style = ttk.Style()
style.theme_use("winnative")

#Make frames
setupFrame = ttk.Frame(root) #Login window
chatFrame = ttk.Frame(root) #Chat window

#Make widgets for server create screen
portLabel = ttk.Label(setupFrame, text="Port number:")
portInput = ttk.Entry(setupFrame)
startButton = ttk.Button(setupFrame, text="Start Server", command=lambda: main(portInput.get()))

#Bind keys for server create screen
root.bind("<Return>", lambda _: main(portInput.get()))

#Pack widgets for server create screen
portLabel.pack()
portInput.pack()
startButton.pack()

#Pack the server create screen
setupFrame.pack()

#Main function
def main(port):
    #Unbind the Enter key
    root.unbind("<Return>")
    
    #Convert the port to an integer
    try:
        port = int(port)
    except ValueError:
        return
    except Exception:
        traceback.print_exc()
        return
    
    #Make widgets for chat screen
    chatOutput = tk.Text(chatFrame)
    
    #Pack widgets for chat screen
    chatOutput.pack()
    
    #Configure widgets for chat screen
    chatOutput.configure(state="disable")
    
    #Pack the chat screen
    setupFrame.pack_forget()
    chatFrame.pack()
    
    #Make a socket variable
    serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Make socket reusable
    serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    host = "0.0.0.0"

    #Listen on the local IP address and the desired port
    serversock.bind((host, port))
    
    t = threading.Thread(target=joinListener, args=(serversock, chatOutput,))
    t.start() 

tk.mainloop()
running = False