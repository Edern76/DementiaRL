import colors, copy, pdb, traceback, os, sys, time, math
from random import *
from code.custom_except import *
import tdlib as tdl
from code.classes import Tile, Rectangle
import code.experiments.newCave as caveGen

myMap = []
roomTiles = []
tunnelTiles = []

ROOM_RATIO = 0.6
MIN_ROOM_NUM = 15
TUNNEL_STEP_HOR = 50
TUNNEL_STEP_VERT = 20

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

def encaseRoom(room):
    global myMap, tunnelTiles
    leftOpen = []
    rightOpen = []
    upOpen = []
    lowOpen = []
    
    for y in range(room.y1, room.y2+1):
        if not myMap[room.x1][y].blocked and (room.x1, y) in tunnelTiles:
            leftOpen.append(y)
        if not myMap[room.x2][y].blocked and (room.x2, y) in tunnelTiles:
            rightOpen.append(y)
    
    leftOpenings = {}
    if not room.y1 in leftOpen and not room.y2 in leftOpen:
        prevY = -1
        firstY = -1
        for y in leftOpen:
            if y == prevY + 1:
                leftOpenings[firstY].append(y)
            else:
                leftOpenings[y] = [y]
                firstY = y
            prevY = y
        
        for y in leftOpenings.keys():
            openList = leftOpenings[y]
            firstY = y
            lastY = openList[len(openList)-1]
            while lastY - firstY > 1:
                myMap[room.x1][firstY].baseBlocked = True
                myMap[room.x1][lastY].baseBlocked = True
                firstY += 1
                lastY -= 1
    
    rightOpenings = {}
    if not room.y1 in rightOpen and not room.y2 in rightOpen:
        prevY = -1
        firstY = -1
        for y in rightOpen:
            if y == prevY + 1:
                rightOpenings[firstY].append(y)
            else:
                rightOpenings[y] = [y]
                firstY = y
            prevY = y
        
        for y in rightOpenings.keys():
            openList = rightOpenings[y]
            firstY = y
            lastY = openList[len(openList)-1]
            while lastY - firstY > 1:
                myMap[room.x2][firstY].baseBlocked = True
                myMap[room.x2][lastY].baseBlocked = True
                firstY += 1
                lastY -= 1
    
    for x in range(room.x1, room.x2+1):
        if not myMap[x][room.y1].blocked and (x, room.y1) in tunnelTiles:
            upOpen.append(x)
        if not myMap[x][room.y2].blocked and (x, room.y2) in tunnelTiles:
            lowOpen.append(x)
    
    upOpenings = {}
    if not room.x1 in upOpen and not room.x2 in upOpen:
        prevX = -1
        firstX = -1
        for x in upOpen:
            if x == prevX + 1:
                upOpenings[firstX].append(x)
            else:
                upOpenings[x] = [x]
                firstX = x
            prevX = x
        
        for x in upOpenings.keys():
            openList = upOpenings[x]
            firstX = x
            lastX = openList[len(openList)-1]
            while lastX - firstX > 1:
                myMap[firstX][room.y1].baseBlocked = True
                myMap[lastX][room.y1].baseBlocked = True
                firstX += 1
                lastX -= 1
    
    lowOpenings = {}
    if not room.x1 in lowOpen and not room.x2 in lowOpen:
        prevX = -1
        firstX = -1
        for x in lowOpen:
            if x == prevX + 1:
                lowOpenings[firstX].append(x)
            else:
                lowOpenings[x] = [x]
                firstX = x
            prevX = x
        
        for x in lowOpenings.keys():
            openList = lowOpenings[x]
            firstX = x
            lastX = openList[len(openList)-1]
            while lastX - firstX > 1:
                myMap[firstX][room.y2].baseBlocked = True
                myMap[lastX][room.y2].baseBlocked = True
                firstX += 1
                lastX -= 1

def checkDoors(mapToUse):
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if mapToUse[x][y].door and mapToUse[x][y].neighbors(mapToUse, True, True) != 2:
                mapToUse[x][y].door = False
    
    return mapToUse

def makeTunnelMap(messyTunnels = False, returnTunTiles = False):
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
        w = randint(6, 17)
        h = randint(6, 17)
        while w/h < ROOM_RATIO or h/w < ROOM_RATIO:
            w = randint(6, 17)
            h = randint(6, 17)
        
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
                tunnel = randint(0, 2)
                if tunnel == 0:
                    createHorizontalTunnel(previous_x, new_x, previous_y)
                    createVerticalTunnel(previous_y, new_y, new_x)
                elif tunnel == 1 and messyTunnels:
                    myMap = caveGen.createTunnel((new_x, new_y), (previous_x, previous_y), newRoom.tiles, myMap)
                else:
                    createVerticalTunnel(previous_y, new_y, previous_x)
                    createHorizontalTunnel(previous_x, new_x, new_y)
            rooms.append(newRoom)
            numberRooms += 1

    cleanTunnels()
    for room in rooms:
        openRooms(room)
        encaseRoom(room)
    placeDoors()
    myMap = checkDoors(myMap)
    
    if returnTunTiles:
        return myMap, tunnelTiles, roomTiles
    return myMap



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
    myMap = makeTunnelMap()
    while not tdl.event.is_window_closed():
        update(myMap)