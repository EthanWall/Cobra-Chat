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

#Define variables
prefix = "/" #Command prefix
running = True

#Create functions
#Receive messages from the server
def recieveMsg(sock):
    global running
    
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
def listenToChat(sock, out):
    while running:
        msg = recieveMsg(sock)
         
        if msg != None:
            output(msg, out)
        else:
            return

#Sends a message to a server or client
def send(sock, data):
    try:
        sock.send(data.encode("utf-8"))
    except ConnectionResetError:
        return
    except Exception:
        traceback.print_exc()

#Write to a tkinter text element
def output(txt, dest):
    dest.configure(state="normal")
    dest.insert(tk.END, "\n{0}".format(txt))
    dest.configure(state="disable")

def handleInput(sock, widg):
    msg = widg.get()
    widg.delete(0, tk.END)
    if msg == "{0}quit".format(prefix): #Explicitly declare functionality in client for quit command
        sock.close()
        raise SystemExit
    else:
        send(sock, msg)

#Make a tkinter window
root = tk.Tk()
root.geometry("500x500")
root.title("Cobra Chat Client")

#Set style of window
style = ttk.Style()
style.theme_use("winnative")

#Make frames
loginFrame = ttk.Frame(root) #Login window
chatFrame = ttk.Frame(root) #Chat window

#Make widgets for login screen
addressLabel = ttk.Label(loginFrame, text="Server address:")
portLabel = ttk.Label(loginFrame, text="Port number:")
usernameLabel = ttk.Label(loginFrame, text="Username:")
addressInput = ttk.Entry(loginFrame)
portInput = ttk.Entry(loginFrame)
usernameInput = ttk.Entry(loginFrame)
loginButton = ttk.Button(loginFrame, text="Join", command=lambda: main(addressInput.get(), portInput.get(), usernameInput.get()))

#Pack widgets for login screen
addressLabel.pack()
addressInput.pack()
portLabel.pack()
portInput.pack()
usernameLabel.pack()
usernameInput.pack()
loginButton.pack()

#Bind keys for login screen
root.bind("<Return>", lambda _: main(addressInput.get(), portInput.get(), usernameInput.get()))

#Pack the login screen
loginFrame.pack()

#Main function
def main(address, port, username):
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
    
    #Create a socket variable
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Connect to specified IP and port
    try:
        s.connect((address, port))
    except ConnectionRefusedError:
        return
    except Exception:
        traceback.print_exc()

    #Send the desired username
    send(s, username)
    
    #Make widgets for chat screen
    chatOutput = tk.Text(chatFrame)
    chatInput = ttk.Entry(chatFrame)
    sendButton = ttk.Button(chatFrame, text="Send", command=lambda: handleInput(s, chatInput))
    
    #Pack widgets for chat screen
    chatOutput.pack()
    chatInput.pack()
    sendButton.pack()
    
    #Configure widgets for chat screen
    chatOutput.configure(state="disable")
    
    #Bind keys for chat screen
    root.bind("<Return>", lambda _: handleInput(s, chatInput))
    
    t = threading.Thread(target=listenToChat, args=(s,chatOutput,))
    t.start()
    
    #Setup frames
    loginFrame.pack_forget()
    chatFrame.pack()
    
tk.mainloop()
running = False