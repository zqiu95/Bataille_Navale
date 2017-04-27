#!/usr/bin/env python
# coding: utf-8

import socket
import select
import sys
from main import *

from tkinter import *

import threading


#if(len(sys.argv) < 2) :
#       print ("\nUsage : python telnet.py hostname\n")
#       sys.exit()
# host = sys.argv[1]

def quitter():
    global socketClient
    socketClient.close()
    fen.destroy()
    sys.exit()

def callback():
    global fen2opened,fen2
    fen2opened=0
    fen2.destroy()

def sendText ():
    global chatString,entreeChat,socketClient,nickname
    tosendString = "<You> "+chatString.get()
    for i in range (9):
        lineArray[i].configure(text=lineArray[i+1]["text"])
    lineArray[9].configure(text=tosendString)
    socketClient.send((chatString.get()).encode())
    if "JOIN" in chatString.get() and nickname==1:
        startAffiche()
        fen2opened=1
    nickname=1
    entreeChat.delete(0, 'end')

def sendText2 (env):
    global chatString,entreeChat,socketClient,nickname
    tosendString = "<You> "+chatString.get()
    for i in range (9):
        lineArray[i].configure(text=lineArray[i+1]["text"])
    lineArray[9].configure(text=tosendString)
    socketClient.send((chatString.get()).encode())
    if "JOIN" in chatString.get() and nickname==1:
        startAffiche()
    nickname=1
    entreeChat.delete(0, 'end')

def joinGame ():
    global socketClient
    if nickname==1:
        socketClient.send("JOIN".encode())
    startAffiche()

def startAffiche ():
    global fen2opened,fen2,frame
    if fen2opened==0:
        fen2=Toplevel()
        fen2.title("BATTLESHIP Ver.BETA")
        fen2.resizable(width=FALSE, height=FALSE)
        fen2.protocol("WM_DELETE_WINDOW", callback)
        frame=Frame (fen2)
        fen2opened=1

def sendCord (tmp):
    global socketClient,frame
    (column,line)=tmp
    socketClient.send((chr(column+47)+str(line)).encode())
    Label(frame, text="S" , width=2, foreground = "red" ).grid(row=line,column=column)



tk_stopped=0
fen2opened = 0
nickname=0

fen = Tk()
fen.title("BATTLESHIP Ver.BETA")
fen.resizable(width=FALSE, height=FALSE)

back = Frame(master=fen, width=300, height=1, bg='white')
back.grid(row=0,column=0,columnspan=10)

mon_menu = Menu(fen)
fen.config(menu=mon_menu)

#CREATION BOUTONS
boutonQuitter=Button(fen,text="Send",command=sendText)
boutonQuitter.grid(row=11,column=11)
fen.bind('<Return>',sendText2)

boutonJoin=Button(fen,text="Join",command=joinGame)
boutonJoin.grid(row=11,column=12)


chatString = StringVar ()
entreeChat = Entry (fen,textvariable=chatString)
entreeChat.grid(row=11,column=0,sticky=W+E,columnspan=10)

lineArray = []
for i in range (10):
	lineArray = lineArray + [Label (fen,justify=LEFT)]
	lineArray[i].grid(row=i+1,column=0,sticky=W,columnspan=11)

#CREATION MENU
menu_fichier = Menu(mon_menu)
mon_menu.add_cascade(label="Fichier", menu=menu_fichier)
menu_fichier.add_command(label="Quitter", command=quitter)

HOST = "localhost"
PORT = 7777
socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def ReceiveData():
    global startGame,fen2,tk_stopped,fen,frame

    try:
        socketClient.connect((HOST, PORT))
        for i in range (9):
            lineArray[i].configure(text=lineArray[i+1]["text"])
        lineArray[9].configure(text="****** [connected to server] ******")
    except:
        for i in range (9):
            lineArray[i].configure(text=lineArray[i+1]["text"])
        lineArray[9].configure(text="[unable connected to server]")
        return

    while 1:
        if (tk_stopped==1):
            break
        try:
            data = socketClient.recv(1024)
        except:
            for i in range (9):
                lineArray[i].configure(text=lineArray[i+1]["text"])
            lineArray[9].configure(text="[partner disconnected]")
            return

        if data != '':
            if ("[88]" in str(data) and fen2opened==0):
                startAffiche()
            if ("[7]" in str(data)):
                startAffiche()

            if "[8]" in str(data) or "[88]" in str(data):
                frame.destroy()
                frame = Frame(fen2)
                frame.grid()
                griddata = data.decode()
                griddata= griddata.replace ("[8]","")
                griddata= griddata.replace ("[88]","")
                griddata= griddata.replace ("[7]","")
                if "[8]" in str(data):
                    griddata = griddata + "    <You>          <Enemy>"
                else:
                    griddata = griddata + "   <Player1>      <player2>"
                line=0
                column=0
                for i in griddata:
                    if i!= "\n" :
                            #Label(frame, text=i , width=2, fg="red" ).grid(row=line,column=column)
                        if i=="X" or i=="O":
                            if column<18:
                                Label(frame, text=i , width=2 , foreground = "red").grid(row=line,column=column)
                            else:
                                Label(frame, text=i , width=2 , foreground = "blue").grid(row=line,column=column)
                        elif line == 11:
                            if column<18:
                                Label(frame, text=i , width=2, foreground = "red" ).grid(row=line,column=column)
                            else:
                                Label(frame, text=i , width=2 , foreground = "blue").grid(row=line,column=column)

                        elif (column<18 or line==0) or "[88]" in str(data):
                            Label(frame, text=i , width=2 ).grid(row=line,column=column)
                        #lambda x=(column,line):sendCord
                        else:
                            Button(frame, text=i, activebackground = "blue",command=lambda x = (column,line):sendCord(x)).grid(row=line,column=column)
                        column += 1
                    else:
                        line+=1
                        column=0
                if "[8]" in str(data):
                    for i in range (9):
                        lineArray[i].configure(text=lineArray[i+1]["text"])
                    lineArray[9].configure(text="<Auto> Which column?")

            elif "YOU WIN ~" in str(data) or "YOU LOSE ~" in str(data) or "GAME ENDED" in str(data):
                frame.destroy()
                frame = Frame(fen2)
                frame.grid()
                griddata = data.decode()
                griddata= griddata.replace ("<Auto>","")
                Label(frame, text=griddata,font=("Courier", 20) ).grid()

                for i in range (9):
                    lineArray[i].configure(text=lineArray[i+1]["text"])
                lineArray[9].configure(text=data.decode())

            else :
                for i in range (9):
                    lineArray[i].configure(text=lineArray[i+1]["text"])
                lineArray[9].configure(text=data.decode())

            print(data.decode())


        else:
            sys.exit()
            fen.destroy()
            break

but = threading.Thread(None,ReceiveData,None,())
but.setDaemon(True)
but.start()
fen.mainloop()
tk_stopped = 1
sys.exit()
