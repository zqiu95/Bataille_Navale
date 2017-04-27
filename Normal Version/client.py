#!/usr/bin/env python
# coding: utf-8

import socket
import select
import sys
from main import *

#client.send(halo.encode())
#response = client.recv(255) && print (response.decode())

if(len(sys.argv) < 2) :
   print ("\nUsage : python telnet.py hostname\n")
   sys.exit()
host = sys.argv[1]
#host = "localhost"
port = 7777

def prompt() :
    sys.stdout.write('<You> ')
    sys.stdout.flush()

socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketClient.connect((host, port))



while True :

    l_socket = [sys.stdin]
    r,_,_ = select.select(l_socket + [socketClient], [], [])
    tmp=0

    for selectedSocket in r:

        if (selectedSocket == socketClient):
            data = selectedSocket.recv(1500)

            if not data:
                print ("<Auto> You are disconnected from the server")
                sys.exit()

            else:
                if "yolo1234" in str(data):
                    prompt()
                elif "[88]" in str (data):
                    print(data.decode())
                else :
                    print (data.decode())
                    prompt ()
                if tmp==1:
                    tmp=0
        else:  #user entered a message
            msg = sys.stdin.readline()
            socketClient.send (msg.encode())
            if tmp==1:
                prompt ()
                tmp=0
            else:
                tmp=1
