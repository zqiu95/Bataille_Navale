#!/usr/bin/python3

from game import *
import  random
import time

" ====================== TCP FUNCTIONS ================  "

def init():
    boats1 = randomConfiguration()
    boats2 = randomConfiguration()
    game = Game(boats1, boats2)
    game.shots[0]=[]
    game.shots[1]=[]
    return game


def displayConfiguration2(boats, shots=[], shots2=[]):

    W2 = (WIDTH+1)*2
    Matrix = [[" " for x in range(W2)] for y in range(W2)]
    tmp = ""
    for i  in range(1,WIDTH+1):
        Matrix[i][0] = chr(ord("A")+i-1)
        Matrix[0][i] = i
    for i in range (1,WIDTH+1):
        Matrix [WIDTH+1+i][0] = chr(ord("A")+i-1)
        Matrix [WIDTH+1][i] = i

    for i in range(NB_BOATS):
         b = boats[i]
         (w,h) = boat2rec(b)
         for dx in range(w):
             for dy in range(h):
                 Matrix[b.x+dx][b.y+dy] = str(i)

    for (x,y,stike) in shots:
        if stike:
            Matrix[x][y] = "X"
        else:
            Matrix[x][y] = "O"

    for (x,y,stike) in shots2:
        if stike:
            Matrix[WIDTH+1+x][y] = "X"
        else:
            Matrix[WIDTH+1+x][y] = "O"


    for y in range(0, WIDTH+1):
        if y == 0:
            l = "  "
        else:
            l = str(y)
            if y < 10:
                l = l + " "
        for x in range(1,(WIDTH+1)*2):
            if x==WIDTH+1:
                l = l + " || "
            if x==WIDTH+2 and y!=10:
                l = l +" "+str(Matrix[x][y])
            elif x==WIDTH+1 and y==10:
                l = l + str(Matrix[x][y])
            else:
                l = l + str(Matrix[x][y])
        tmp = tmp + l + "\n"
    return tmp

""" generate a random valid configuration """
def randomConfiguration():
    boats = [];
    while not isValidConfiguration(boats):
        boats=[]
        for i in range(5):
            x = random.randint(1,10)
            y = random.randint(1,10)
            isHorizontal = random.randint(0,1) == 0
            boats = boats + [Boat(x,y,LENGTHS_REQUIRED[i],isHorizontal)]
    return boats



def displayConfiguration(boats,boats2, shots=[], shots2=[]):

    W2 = (WIDTH+1)*2
    Matrix = [[" " for x in range(W2)] for y in range(W2)]
    tmp = ""
    for i  in range(1,WIDTH+1):
        Matrix[i][0] = chr(ord("A")+i-1)
        Matrix[0][i] = i
    for i in range (1,WIDTH+1):
        Matrix [WIDTH+1+i][0] = chr(ord("A")+i-1)
        Matrix [WIDTH+1][i] = i

    for i in range(NB_BOATS):
         b = boats[i]
         c = boats2[i]
         (w,h) = boat2rec(b)
         (w2,h2)=boat2rec(c)
         for dx in range(w):
             for dy in range(h):
                 Matrix[b.x+dx][b.y+dy] = str(i)

         for dx in range (w2):
             for dy in range (h2):
                 Matrix[c.x+dx+WIDTH+1][c.y+dy] = str(i)

    for (x,y,stike) in shots:
        if stike:
            Matrix[x][y] = "X"
        else:
            Matrix[x][y] = "O"

    for (x,y,stike) in shots2:
        if stike:
            Matrix[WIDTH+1+x][y] = "X"
        else:
            Matrix[WIDTH+1+x][y] = "O"

    for y in range(0, WIDTH+1):
        if y == 0:
            l = "  "
        else:
            l = str(y)
            if y < 10:
                l = l + " "
        for x in range(1,(WIDTH+1)*2):
            if x==WIDTH+1:
                l = l + " || "
            if x==WIDTH+2 and y!=10:
                l = l +" "+str(Matrix[x][y])
            if x==WIDTH+1 and y==10:
                l = l + str(Matrix[x][y])
            else:
                l = l + str(Matrix[x][y])
        tmp = tmp + l + "\n"
    return tmp

""" display the game viewer by the player"""
def displayGame(game, player):
    otherPlayer = (player+1)%2
    displayConfiguration2(game.boats[player],game.shots[otherPlayer],game.shots[player])


""" Play a new random shot """
def randomNewShot(shots):
    (x,y) = (random.randint(1,10), random.randint(1,10))
    while not isANewShot(x,y,shots):
        (x,y) = (random.randint(1,10), random.randint(1,10))
    return (x,y)


def main():
    boats1 = randomConfiguration()
    boats2 = randomConfiguration()
    game = Game(boats1, boats2)
    print("===========TEST===========")
    currentPlayer=0
    displayGame(game, currentPlayer)
    currentPlayer = (currentPlayer+1)%2
    displayGame(game, currentPlayer)
    currentPlayer = (currentPlayer+1)%2
    while gameOver(game) == -1:
        if currentPlayer == J0:
            print("\n\n============================ J0 ========================")
            print("== CURRENT STATE COLONEL ==       == PREVIOUS SHOTS =====")
            displayGame(game, currentPlayer)
            x_char = input ("\n Cardinal coordinates to LAUNCH THE MISSIL \n Which colon ? ")
            x_char.capitalize()
            x = ord(x_char)-ord("A")+1
            y = int(input (" Which line ? "))
        else :
            print("\n\n============================ J1 ========================")
            print("== CURRENT STATE COLONEL ==       == PREVIOUS SHOTS =====")
            displayGame(game, currentPlayer)
            x_char = input ("\n Cardinal coordinates to LAUNCH THE MISSIL \n Which colon ? ")
            x_char.capitalize()
            x = ord(x_char)-ord("A")+1
            y = int(input (" Which line ? "))
        addShot(game, x, y, currentPlayer)
        print("===== Etat des tirs ====")
        currentPlayer = (currentPlayer+1)%2
    print("game over")
    print("your grid :")
    displayGame(game, J0)
    print("the other grid :")
    displayGame(game, J1)

    if gameOver(game) == J0:
        print("You win !")
    else:
        print("you loose !")
