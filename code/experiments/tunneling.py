import colors, copy, pdb, traceback, os, sys, time, math
from random import *
from code.custom_except import *
import tdlib as tdl
from code.classes import Tile, Rectangle

myMap = []
roomTiles = []
tunnelTiles = []

ROOM_RATIO = 0.6
MIN_ROOM_NUM = 15
TUNNEL_STEP_HOR = 50
TUNNEL_STEP_VERT = 25

WIDTH, HEIGHT, LIMIT = 150, 80, 20
MAP_WIDTH, MAP_HEIGHT = 140, 60
MID_MAP_WIDTH, MID_MAP_HEIGHT = MAP_WIDTH//2, MAP_HEIGHT//2
if __name__ == '__main__':
    root = tdl.init(WIDTH, HEIGHT, 'Dementia')

def createRoom(room):
    global myMap, roomTiles
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            myMap[x][y].baseBlocked = False
            roomTiles.append((x, y))
            
def createHorizontalTunnel(x1, x2, y):
    global myMap, tunnelTiles
    print('tun len:', max(x1, x2) - min(x1, x2))
    width = (max(x1, x2) - min(x1, x2))//TUNNEL_STEP_HOR
    if width > 2:
        width = 2
    
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for wY in range(-width, width+1):
            tY = y + wY
            myMap[x][tY].baseBlocked = False
            tunnelTiles.append((x, tY))
            
def createVerticalTunnel(y1, y2, x):
    global myMap, tunnelTiles
    print('tun len:', max(y1, y2) - min(y1, y2))
    width = (max(y1, y2) - min(y1, y2))//TUNNEL_STEP_VERT
    if width > 2:
        width = 2

    for y in range(min(y1, y2), max(y1, y2) + 1):
        for wX in range(-width, width+1):
            tX = x + wX
            myMap[tX][y].baseBlocked = False
            tunnelTiles.append((tX, y))

def cleanTunnels():
    global tunnelTiles, myMap
    for (x, y) in tunnelTiles:
        for direction in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            dX, dY = direction
            try:
                if (x + 2*dX, y + 2*dY) in tunnelTiles and myMap[x+dX][y+dY].blocked and myMap[x-dX][y-dY].blocked and myMap[x+3*dX][y+3*dY].blocked:
                    myMap[x+dX][y+dY].baseBlocked = False
                    tunnelTiles.append((x+dX, y+dY))
            except IndexError:
                pass

def openRooms(room):
    global tunnelTiles, myMap
    cX, cY = room.center()
    for (x, y) in room.tiles:
        if x == cX or y == cY:
            for direction in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                dX, dY = direction
                try:
                    if (x + 2*dX, y + 2*dY) in tunnelTiles and myMap[x+dX][y+dY].blocked:
                        myMap[x+dX][y+dY].baseBlocked = False
                        myMap[x+dX][y+dY].door = True
                        print('added a door at', x+dX, y+dY)
                        tunnelTiles.append((x+dX, y+dY))
                except IndexError:
                    pass

def placeDoors(prob = 100):
    global myMap
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            neighborInRoom = False
            for neighbor in myMap[x][y].neighbors(myMap, cardinal = True):
                if (neighbor.x, neighbor.y) in roomTiles:
                    neighborInRoom = True
                    break
            
            blockedNeighbors = 0
            dX, dY = 0, 0
            for neighbor in myMap[x][y].neighbors(myMap, cardinal = True):
                ndX, ndY = neighbor.x - x, neighbor.y - y
                if neighbor.blocked and ((dX, dY) == (0, 0) or (ndX, ndY) == (-dX, -dY)):
                    blockedNeighbors += 1
                    dX, dY = ndX, ndY
            
            neighborDoor = False
            for neighbor in myMap[x][y].neighbors(myMap, cardinal = True):
                if neighbor.door:
                    neighborDoor = True
                    break
            
            if (x, y) in tunnelTiles and neighborInRoom and (x, y) not in roomTiles and blockedNeighbors == 2 and randint(1, 100) <= prob and not neighborDoor:
                myMap[x][y].door = True

'''
def encaseRoom(room):
    global myMap, tunnelTiles
    #checking right:
    
    upR, lowR = upperR, lowerR
    x, upY = upR
    x, lowY = lowR
    if myMap[x][upY].blocked and myMap[x][lowY].blocked:
        while upR != lowR and upY < lowY:
            upY += 1
            lowY -= 1
            myMap[x][upY].baseBlocked = True
            myMap[x][lowY].baseBlocked = True
            upR = (x, upY)
            lowR = (x, lowY)
        if myMap[x][upY].blocked and (x, upY) in tunnelTiles:
            myMap[x][upY].baseBlocked = False
        if myMap[x][lowY].blocked and (x, lowY) in tunnelTiles:
            myMap[x][lowY].baseBlocked = False
'''
    
def makeMap():
    global myMap, rooms, roomTiles, tunnelTiles

    myMap = [[Tile(blocked = True, x = x, y = y) for y in range(MAP_HEIGHT)]for x in range(MAP_WIDTH)] #Creates a rectangle of blocking tiles from the Tile class, aka walls. Each tile is accessed by myMap[x][y], where x and y are the coordinates of the tile.
    rooms = []
    roomTiles = []
    tunnelTiles = []
    numberRooms = 0
    
    for x in range(MAP_WIDTH):
        myMap[x][0].setUnbreakable()
        myMap[x][MAP_HEIGHT - 1].setUnbreakable()
    for y in range(MAP_HEIGHT):
        myMap[0][y].setUnbreakable()
        myMap[MAP_WIDTH - 1][y].setUnbreakable()
 
    while len(rooms) < MIN_ROOM_NUM:
        w = randint(6, 20)
        h = randint(6, 20)
        while w/h < ROOM_RATIO or h/w < ROOM_RATIO:
            w = randint(6, 20)
            h = randint(6, 20)
        
        x = randint(0, MAP_WIDTH-w-1)
        y = randint(0, MAP_HEIGHT-h-1)
        newRoom = Rectangle(x, y, w, h)
        intersection = False
        for otherRoom in rooms:
            if newRoom.intersect(otherRoom):
                intersection = True
                break
        if not intersection:
            createRoom(newRoom)
            (new_x, new_y) = newRoom.center()
            if numberRooms != 0:
                (previous_x, previous_y) = rooms[numberRooms-1].center()
                if randint(0, 1):
                    createHorizontalTunnel(previous_x, new_x, previous_y)
                    createVerticalTunnel(previous_y, new_y, new_x)
                else:
                    createVerticalTunnel(previous_y, new_y, previous_x)
                    createHorizontalTunnel(previous_x, new_x, new_y)
            rooms.append(newRoom)
            numberRooms += 1
    
    for room in rooms:
        openRooms(room)
        #encaseRoom(room)
    cleanTunnels()
    placeDoors()



def update(mapToUse = myMap):
    root.clear()
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            try:
                if mapToUse[x][y].blocked:
                    root.draw_char(x, y, '#', colors.grey, colors.darker_grey)
                elif mapToUse[x][y].door:
                    root.draw_char(x, y, '+', colors.darker_orange, colors.sepia)
                else:
                    root.draw_char(x, y, None, bg = colors.sepia)
            except IndexError:
                print('___PROBLEM___:', x, y)
    tdl.flush()

if __name__ == '__main__':
    makeMap()
    while not tdl.event.is_window_closed():
        update(myMap)