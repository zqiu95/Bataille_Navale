#!/usr/bin/env python
# coding: utf-8

import socket
import select
import sys
import time
from main import *

#client.send(halo.encode())
#response = client.recv(255) && print (response.decode())


class Client :
    def __init__(self,socket):
        self.socketName=socket
        self.pseudoClient="unknown"
        self.status=-2 # nothing = -2; standard case when you hadn't give a valid pseudo / watcher = -1 / 1erPlayer =0 / waitingPlayer=1
        self.win=0

    def affiche(self):
        print (self.__socketName, self.pseudoClient, self.status, self.win)

    def get_socketName(self):
        return self.socketName

    # Only use when reconnection
    def set_socketName(self,s):
        self.socketName=s

    def get_pseudoClient(self):
        return self.pseudoClient
    def set_pseudoCLient(self,pseudo):
        self.pseudoClient=pseudo

    def get_status(self):
        return self.status

    def set_status(self,state):
        self.status=state

    def get_win(self):
        return self.win

    def set_win(self,nbVictory):
        self.win=self.win+nbVictory





#=== Print welcome message + create client if game not in pause
# Otherwise we'll need to look for reconnection case thanks to fun_checkReconnectionClient
def fun_msgToClient_firstConnection (mySocket):
    global l_client, l_socket,gameInPause,indexSocketDeconnected,b_newClient

    mySocket, addr = socketServeur.accept()
    if not gameInPause:
        tmp=Client(mySocket)
        l_client=l_client+[tmp]
    else :
        b_newClient=True

    mySocket.send(("\n****** WELCOME TO THE BATTLEFIELD ****** \n<Auto> Set your Nickname : ").encode())
    l_socket = l_socket + [mySocket]



#=== Get pseudo(=data) of the client and check if already exist
# > If it exist --> Msg to client
# > Else, new client --> add Pseudo to the corresponding instance of class Client
#       + if game started --> this client is watcher
def fun_msgToClient_askPseudo(mySocket,data,sockIndex):
    global l_client,s_pseudoConnected,startGame

    data=(data).replace ("\n","")
    # Pseudo already taken
    if fun_checkIfPseudoInSet(s_pseudoConnected,data):
        mySocket.send(("<Auto> Pseudo already taken. Please chose another one").encode())

    # New Client
    else:
        s_pseudoConnected.add(data)
        l_client[sockIndex].set_pseudoCLient(data)
        l_client[sockIndex].set_status(-1)
        pr = ">Player " +l_client[sockIndex].pseudoClient+" joined the server"
        print (pr)
        mySocket.send(("<Auto> User commands : CMD MSG QUIT MORE ").encode())
        if (startGame==1):
            mySocket.send(("\n<Auto> Game already started : You're watcher. ").encode())
            mySocket.send(("\n Waiting for players moves... ~").encode())



#=== Use pseudo(=data) in order to check if it's reconnection
# > Pseudo already in connected players --> msg "give another one" / Return FALSE
# > Pseudo in deconnected players --> reconnection case / Return TRUE
# > Else --> It's a new client, we create a client instance / Return FALSE
def fun_checkReconnectionClient (mySocket,data):
    global l_client,s_pseudoConnected,s_pseudoDisconnected,loopPseudo

    data=(data).replace ("\n","")

    # Pseudo already taken
    if fun_checkIfPseudoInSet(s_pseudoConnected,data):
        mySocket.send(("<Auto> Pseudo already taken. Please chose another one").encode())
        loopPseudo=1

    # Client reconnection
    elif fun_checkIfPseudoInSet(s_pseudoDisconnected,data):
        return True

    #New client
    else:
        loopPseudo=0
        newC=Client(mySocket)
        newC.set_pseudoCLient(data)
        newC.set_status(-1)
        l_client=l_client+[newC]
        print("check reco")
        print(newC.get_status())
        s_pseudoConnected.add(data)
        pr = ">Player " +newC.get_pseudoClient()+"joined the server"
        print (pr)
        mySocket.send(("<Auto> User commands : CMD MSG QUIT MORE ").encode())
    return False


# ===
# > waitingPlayer --> Waiting message
# > watcher --> grids of players
def fun_msgToOtherThanCurrentPlayer():
    global l_client
    watcher=-1
    waitingPlayer=1

    for selectedClient in l_client:
        if selectedClient.get_status() == waitingPlayer:
            selectedClient.get_socketName().send(("<Auto> Waiting opponents move [7]...").encode())
        elif selectedClient.get_status() == watcher:
            watcherGrid=displayConfiguration(myGame.boats[0],myGame.boats[1],myGame.shots[1],myGame.shots[0])
            selectedClient.get_socketName().send(("[88]"+watcherGrid).encode())


# ===
# > waitingPlayer --> Alert message "a watcher join" + Waiting message
# > watcher --> you're watcher
def fun_msgNewClientWhenGamePaused():
    global l_client
    watcher=-1

    for selectedClient in l_client:
        # We vonluntarly skip the leaving client in order to prevent bugs
        if (l_client.index(selectedClient)!=indexSocketDeconnected):
            if selectedClient.get_status() == 1 or selectedClient.get_status()== 0 :
                selectedClient.get_socketName().send(("<Auto> A watcher join the game. Waiting for player return ~...").encode())
            elif selectedClient.get_status() == watcher:
                selectedClient.get_socketName().send(("\n<Auto> You'll will be watcher if player reconnected himself \n").encode())


#=== Game initialisation
# Add player identified by socket to active players
# > If alone --> Player 0 + msg : waiting for other player
# > Else (2 players) --> Player 1 / startGame !
def fun_gameImplementation(mySocket,index):
    global startGame, playerReady, startGame, player, otherPlayer, myGame,grid

    if startGame == 0 and (not index in playerReady):
        playerReady=playerReady+[index]
        nbPlayer=len(playerReady)

        if nbPlayer == 1:
            l_client[index].set_status(0)
            print ("> "+l_client[index].pseudoClient+" joined a battle. Players count 1/2")
            mySocket.send(("<Auto> You joined a game. Waiting for opponents ~").encode())

        if nbPlayer == 2:
            l_client[index].set_status(1)
            startGame=1
            player=0
            otherPlayer=(player+1)%2
            print ("> "+l_client[index].pseudoClient+" joined a battle. Players count 2/2\n>> Starting battle between [ "+l_client[playerReady[0]].pseudoClient+"] and [ "+l_client[playerReady[1]].pseudoClient+"]")
            mySocket.send(("<Auto> You joined a game. The game will start soon ~").encode())
            copyGame = init ()
            myGame = copyGame
            grid=displayConfiguration2(myGame.boats[player],myGame.shots[otherPlayer],myGame.shots[player])

            #l_client[playerReady[0]].get_socketName().send(("<Auto> The game will start soon.\n").encode())
            l_client[playerReady[0]].get_socketName().send(("[8]"+grid).encode())
            fun_msgToOtherThanCurrentPlayer()


# === Ask current player correct x/y for the shoot
# Check if game over / Return False
# If not change current player (status client) / Return True
def fun_gameplay(mySocket,data):
    global columnLine, myGame, player, otherPlayer, startGame, x, y, grid, l_client

    data = data.replace("\n","")
    data = data.replace(" ","")

    column=0
    line=1

    if len(data)>3:
        return True

    if columnLine == column:
        if fun_checkColumn(data[0])==True:
            x = ord(data[0])-ord("A")+1
            columnLine=line
        # Wrong x given --> loop column continue
        else:
            grid=displayConfiguration2(myGame.boats[player],myGame.shots[otherPlayer],myGame.shots[player])
            mySocket.send(("[8]"+grid).encode())

    if columnLine == line:
        if len(data)==3:
            tmpdata = data[1] + data[2]
        else :
            tmpdata = data[1]
            
        if fun_checkLine(tmpdata)==True:
            y=fun_valueLine(tmpdata)
            addShot(myGame, x, y, player)

            columnLine=column
            player=otherPlayer
            otherPlayer=(player+1)%2


            if (gameOver(myGame)!=-1):
                l_client[playerReady[otherPlayer]].get_socketName().send(("<Auto> YOU WIN ~\n").encode())
                l_client[playerReady[player]].get_socketName().send(("<Auto> YOU LOSE ~\n").encode())
                l_client[playerReady[otherPlayer]].set_win(1)
                startGame=0



                for tmpSocket in l_socket:
                    indexC=fun_indexSocket(l_client,tmpSocket)
                    if (not indexC in playerReady):
                        tmpSocket.send(("<Auto> GAME ENDED, \"JOIN\" to play").encode())
                    tmpSocket.send(("<Auto> User commands : CMD JOIN MSG QUIT MORE ").encode())
                fun_resetPlayerReady()
                fun_resetStatusClient()
                return False

            #Game not over : We need to change the status of the player
            for c in l_client:
                if c.get_status()==0:
                    c.set_status(1)
                elif c.get_status()==1:
                    c.set_status(0)

            grid=displayConfiguration2(myGame.boats[player],myGame.shots[otherPlayer],myGame.shots[player])
            l_client[playerReady[player]].get_socketName().send(("[8]"+grid).encode())
            fun_msgToOtherThanCurrentPlayer()

        # Wrong y given --> loop line continue
        else:
            mySocket.send(("<Auto> Which line?").encode())
        return True


# === Reset only for client which have already given a correct pseudo (no -2 status)
def fun_resetStatusClient ():
    global l_client
    for client in l_client:
        if client.get_status()!=-2:
            client.set_status(-1)

# === As l_client and l_socket haven't same index when dealing with reconnection (but have in normal case)
# Allows to find the right index for l_socket from l_client
def fun_indexSocket(clientList,maSocket):
    index=-1
    i=0
    for c in clientList:
        if c.get_socketName()==maSocket:
            index=i
        i=i+1
    return index



# === Deal with leaving client
# > if it's Player :
#     - (1 player deco and no game launched) --> remove player from playerReady
#     - (1 player deco and game launched) --> game paused
#     - (2 players deco) --> end of game
# > if it's watcher --> deconnected him
def fun_leavingClient(maSocket,socketServeur):
    global l_socket,playerReady,startGame,l_client,s_pseudoConnected,s_pseudoDisconnected,gameInPause,indexSocketDeconnected,b_newClient

    index=fun_indexSocket(l_client,maSocket)
    pseudo=l_client[index].pseudoClient.replace ("\n"," ")

    pr = ">Player " + pseudo +" left the server"
    print (pr)

    # ===== Player deconnection ===== #
    if index in playerReady:
        # Only one player (the one which is deconnected)
        if len(playerReady)==1:
            playerReady=[]

        # ==== Two players (including the one which is deconnected)
        else :
            # == The other player is already disconnected --> END of Game
            if (len(s_pseudoDisconnected)>=1):
                # We remove the player who was already disconnected
                for c in l_client:
                    if (c.get_socketName()!=socketServeur and c.get_socketName()!=maSocket):
                        if (c.get_status()==1 or c.get_status()==0):
                            l_client.remove(c)

                # We send a message to watchers
                for c2 in l_client:
                    if (c2.get_status()==-1):
                        c2.get_socketName().send(("<Auto> Players have left the game. END OF GAME\n If you want, you can join a game \n").encode())

                # We calculate the new index
                index=fun_indexSocket(l_client,maSocket)

                fun_resetPlayerReady()
                fun_resetPseudoDisconnected()
                fun_resetStatusClient()
                startGame=0
                gameInPause=False

            # == The other player is still connected --> Game Paused
            else:
                gameInPause=True
                b_newClient=False
                for otherSocketTmp in l_socket:
                    if (otherSocketTmp != socketServeur and otherSocketTmp != maSocket and l_client[l_socket.index(otherSocketTmp)].get_status()!=-2):
                        otherSocketTmp.send(("<Auto> Player "+ pseudo + " left the game. Waiting for player reconnection\n").encode())
                        if (l_client[l_socket.index(otherSocketTmp)].get_status()==0 or l_client[l_socket.index(otherSocketTmp)].get_status()==1 ):
                            otherSocketTmp.send(("<Auto> If you don't want to wait, just leave, enter \"STOP\"\n").encode())


                #=== By passing the pseudo from Connected to Disconnected it allows us
                # to deal with intentionnal reconnection from a client with the same Pseudo
                tmpPseudo=(l_client[index].get_pseudoClient())
                s_pseudoConnected.remove(tmpPseudo)
                s_pseudoDisconnected=s_pseudoDisconnected+[tmpPseudo]
                indexSocketDeconnected=index
                l_socket.remove(maSocket)
                maSocket.close()
                return

    # ===== Watcher deconnection =====
    #else:
        # DO nothing in addition of the following lines (are common with some cases of player deconnection)

    if pseudo=='unknown':
        l_client.remove(l_client[index])
        l_socket.remove(selectedSocket)
        selectedSocket.close()

    else :
        tmpPseudo=(l_client[index].get_pseudoClient())

        s_pseudoConnected.remove(tmpPseudo)
        l_client.remove(l_client[index])
        l_socket.remove(selectedSocket)
        selectedSocket.close()

def fun_clientSTOP(maSocket,socketServeur):
    global l_client,startGame,gameInPause

    # We remove the player who was already disconnected
    for c in l_client:
        if (c.get_socketName()!=socketServeur and c.get_socketName()!=maSocket):
            if (c.get_status()==1 or c.get_status()==0):
                l_client.remove(c)
    # We send a message to watchers and to player who choose to STOP
    for c2 in l_client:
        if (c2.get_status()==-1):
            c2.get_socketName().send(("<Auto> Players have left the game. END OF GAME\n If you want, you can join a game \n").encode())
        if (c2.get_status()==0 or c2.get_status()==1):
            c2.get_socketName().send(("<Auto> You have left the game. END OF GAME\n If you want, you can join a game \n").encode())


    fun_resetPlayerReady()
    fun_resetPseudoDisconnected()
    fun_resetStatusClient()
    startGame=0
    gameInPause=False

def fun_resetPlayerReady():
    global playerReady

    playerReady=[]

def fun_resetPseudoDisconnected():
    global s_pseudoDisconnected

    s_pseudoDisconnected=[]

# === Return TRUE if Y is a line, else FALSE
def fun_checkLine(strY):
    intY = ord (strY[0])
    if len(strY)>1:
        intY2 = ord (strY[1])
        return intY == ord('1') and intY2 == ord('0')
    return intY >ord('0') and intY<=ord('9')

# === Return TRUE if Y is a 10 (special case because 10 is two char), else FALSE
def fun_lineIsA10 (data):
    return len(data)>1 and data[0]=="1" and data[1]=="0"

# === Return int value of Y
def fun_valueLine (data):
    if fun_lineIsA10(data):
        return 10
    else:
        return ord (data)-48 #Int conversion


# === TRUE if charX is a column, else FALSE
def fun_checkColumn (charX):
    column= set(('A','B','C','D','E','F','G','H','I','J'))
    return charX in column


def fun_checkIfPseudoInSet (setPseudo,pseudo):
    return pseudo in setPseudo

def fun_clientDeco():
    global s_pseudoDisconnected

    pseudoClientDeco=s_pseudoDisconnected[0]
    for c in l_client:
        if c.get_pseudoClient()==pseudoClientDeco:
            return c






###############  INIT  #################
socketServeur = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
socketServeur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socketServeur.bind(('', 7777))
socketServeur.listen(1)

########### GLOBAL VARIABLE ############

s_pseudoConnected=set()
s_pseudoDisconnected=[]


gameInPause=False
b_newClient=-1
loopPseudo=0

l_socket = []
l_client=[]
playerReady = []
grid=[]
indexSocketDeconnected=-1


startGame = 0
player=0
otherPlayer=(player+1)%2
columnLine= 0
x=-1
y=-1

delay=0


print("============= BATTLESHIP SERVER ON ==========\n")

while True:

    r,_,_ = select.select(l_socket + [socketServeur], [], [])

    for selectedSocket in r:
        if (selectedSocket == socketServeur):
            fun_msgToClient_firstConnection (selectedSocket)

        else:
            data = selectedSocket.recv(1500)
            data = data.decode()
            index=l_socket.index(selectedSocket)

            if len(data) == 0:
                fun_leavingClient(selectedSocket,socketServeur)
                break

            elif gameInPause:
                print("=======GAME IN PAUSE 2")
                #==== If it's a reconnection
                if (b_newClient or fun_indexSocket(l_client,selectedSocket)==-1) and fun_checkReconnectionClient(selectedSocket,data):

                    pseudoClientDeco=s_pseudoDisconnected[0]
                    # We recreate the socket list because we need to put it in right order
                    l_socket=[]
                    for c in l_client:
                        l_socket=l_socket + [c.get_socketName()]
                    l_socket[indexSocketDeconnected]=selectedSocket

                    for c2 in l_client:
                        if c2.get_pseudoClient()==pseudoClientDeco:
                            #== Waiting for player to reconnect
                            c2.set_socketName(selectedSocket)
                            gameInPause=False
                            s_pseudoConnected.add(pseudoClientDeco)
                            s_pseudoDisconnected=[]
                            columnLine=0

                            # If the client disconnected was the current player
                            if (c2.get_status()==0):
                                selectedSocket.send(("[8]"+grid).encode())
                                for c4 in l_client:
                                    s=c4.get_socketName()
                                    if c4.get_status()==1:
                                        s.send(("<Auto> Other player reconnected\n waiting opponents move ~ ").encode())
                                    elif c4.get_status()==-1:
                                        s.send(("<Auto> Other player reconnected\n  ").encode())
                                        watcherGrid=displayConfiguration(myGame.boats[0],myGame.boats[1],myGame.shots[1],myGame.shots[0])
                                        s.send(("[88]"+watcherGrid).encode())

                            else :
                                for c3 in l_client:
                                    # Send a message to watchers
                                    if (c3.get_status()==-1):
                                        c3.get_socketName().send(("<Auto> Other player reconnected.").encode())
                                    # Send a message to actual player
                                    elif (c3.get_status()==0):
                                        c3.get_socketName().send(("<Auto> Other player reconnected. Press a key to refresh the game").encode())
                                # Send a message to the client disconnected (waiting player) and watchers
                                fun_msgToOtherThanCurrentPlayer()


                #==== Not a reconnection
                else :
                    print("NOT A RECO")
                    # New client
                    if b_newClient and not loopPseudo:
                        print ("Pas une reco")
                        fun_msgNewClientWhenGamePaused()
                        b_newClient=False
                        loopPseudo=0
                    # Pseudo loop
                    elif loopPseudo:
                        print("loopPseudo")
                    #Player sending stuff
                    else:
                        tmpC=l_client[fun_indexSocket(l_client,selectedSocket)]
                        tmpStatus=tmpC.get_status()
                        if "STOP" in str(data) and (tmpStatus==0 or tmpStatus==1):
                            fun_clientSTOP(selectedSocket,socketServeur)


            elif l_client[index].get_pseudoClient()=="unknown":
                fun_msgToClient_askPseudo(selectedSocket,data,index)

            elif "MSG" in str(data):
                for tmpS in l_socket:
                    if tmpS!=socketServeur and tmpS!=selectedSocket:
                        iS=fun_indexSocket(l_client,selectedSocket)
                        pseudoS=l_client[iS].get_pseudoClient()
                        data = data.replace ("MSG","")
                        tmpS.send(("<"+pseudoS+"> "+data).encode())

            elif startGame == 1:
                print ("GAMEPLAY")
                if (l_client[l_socket.index(selectedSocket)].get_status() == 0):
                    if not fun_gameplay(selectedSocket,data):
                        # so game is over
                        break
                print("END GAMEPLAY")
                break

            elif "CMD" in str(data):
                selectedSocket.send(("<Auto> User commands : CMD MSG QUIT MORE ").encode())
            elif "JOIN" in str(data):
                fun_gameImplementation(selectedSocket,index)
            elif "QUIT" in str(data):
                fun_leavingClient(selectedSocket,socketServeur)
            elif "MORE" in str(data):
                selectedSocket.send(("<Auto> Commands :\n    CMD -> Show command list\n    JOIN -> Play a match\n    MSG -> Write down on the chat\n    QUIT -> Disconnect from server").encode())
