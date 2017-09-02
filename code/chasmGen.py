import colors, copy, pdb, traceback, os, sys, time
from random import *
from code.custom_except import *
import tdlib as tdl
from code.classes import Tile, Rectangle
import code.experiments.tunneling as tunneling


WIDTH, HEIGHT, LIMIT = 150, 80, 20
MAP_WIDTH, MAP_HEIGHT = 140, 60
MID_MAP_WIDTH, MID_MAP_HEIGHT = MAP_WIDTH//2, MAP_HEIGHT//2
MID_WIDTH, MID_HEIGHT = int(WIDTH/2), int(HEIGHT/2)

CHANCE_TO_START_ALIVE = 65
DEATH_LIMIT = 3
BIRTH_LIMIT = 4
STEPS_NUMBER = 2
MIN_ROOM_SIZE = 6

emptyTiles = [] #List of tuples of the coordinates of emptytiles not yet processed by the floodfill algorithm
rooms = []
roomTiles = []
tunnelTiles = []
unchasmable = []
lastX = 0
lastY = 0
firstX = 0
firstY = 0

curRoomIndex = 0

sys.setrecursionlimit(3000)

if __name__ == '__main__':
    root = tdl.init(WIDTH, HEIGHT, 'Dementia')

'''
def createRoom(room):
    global myMap, roomTiles
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            myMap[x][y].baseBlocked = False
            roomTiles.append((x, y))
            
def createHorizontalTunnel(x1, x2, y):
    global myMap, tunnelTiles
    for x in range(min(x1, x2), max(x1, x2) + 1):
        myMap[x][y].baseBlocked = False
        tunnelTiles.append((x, y))
            
def createVerticalTunnel(y1, y2, x):
    global myMap, tunnelTiles
    for y in range(min(y1, y2), max(y1, y2) + 1):
        myMap[x][y].baseBlocked = False
        tunnelTiles.append((x, y))
'''

def floodFill(x,y, mapToUse):
    '''
    flood fill the separate regions of the level, discard
    the regions that are smaller than a minimum size, and 
    create a reference for the rest.
    '''
    print('floodfilling')
    connected = []
    tile = (x,y)
    toBeFilled = [tile]
    while toBeFilled:
        tile = toBeFilled.pop()
        x, y = tile
        if tile not in connected:
            connected.append(tile)
            
            #myMap[x][y].baseBlocked = True
            north = (x,y-1)
            south = (x,y+1)
            east = (x+1,y)
            west = (x-1,y)
            
            for direction in [north,south,east,west]:
                newX, newY = direction
                try:
                    if not mapToUse[newX][newY].blocked:
                        if direction not in toBeFilled and direction not in connected:
                            toBeFilled.append(direction)
                except IndexError:
                    print(newX, newY)

    return connected

def unblockTunnels(mapToUse, roomTiles, tunnelTiles, unchasmable):
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if mapToUse[x][y].chasm and ((x, y) in unchasmable or ((x,y) in tunnelTiles and not (x, y) in roomTiles)):
                mapToUse[x][y].chasm = False
                mapToUse[x][y].baseFg = colors.lighter_grey
                mapToUse[x][y].baseBg = colors.darker_sepia
    return mapToUse

def checkMap():
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if myMap[x][y].chasm:
                myMap[x][y].baseFg = colors.dark_grey
                myMap[x][y].baseBg = colors.black
            else:
                myMap[x][y].baseFg = colors.lighter_grey
                myMap[x][y].baseBg = colors.dark_sepia

def createChasms(mapToUse): #, roomTiles, tunnelTiles, unchasmable):
    newMap = copy.deepcopy(mapToUse)
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if randint(0, 100) < CHANCE_TO_START_ALIVE:
                #mapToUse[x][y].baseFg = colors.lighter_grey
                #mapToUse[x][y].baseBg = colors.dark_sepia
                newMap[x][y].chasm = False
            else:
                newMap[x][y].chasm = True
    #update(newMap)
    for loop in range(STEPS_NUMBER):
        newMap = doStep(newMap)
        #update(newMap)
    #newMap = unblockTunnels(mapToUse, roomTiles, tunnelTiles, unchasmable)
    return newMap
    
def makeMap():
    global myMap, rooms, roomTiles, tunnelTiles, unchasmable, firstX, firstY, lastX, lastY
    
    myMap = tunneling.makeTunnelMap()
    myMap = makeChasmMap(myMap)
    return myMap

def makeChasmMap(mapToUse):
    state = False
    
    while not state:
        print(state, 'new iter')
        state = True
        tempMap = createChasms(mapToUse) #, roomTiles, tunnelTiles, unchasmable)
        fFX = randint(0, MAP_WIDTH - 1)
        fFY = randint(0, MAP_HEIGHT-1)
        print('flood fill coords:', fFX, fFY)
        while tempMap[fFX][fFY].blocked or tempMap[fFX][fFY].chasm:
            fFX = randint(0, MAP_WIDTH - 1)
            fFY = randint(0, MAP_HEIGHT-1)
            print('blocked, flood fill coords:', fFX, fFY)
            
        connected = floodFill(fFX, fFY, tempMap)
        print(connected)
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if not tempMap[x][y].blocked and not tempMap[x][y].chasm:
                    if not (x, y) in connected:
                        state = False
                        print('floodfill is wrong')
                        break
            if not state:
                break
    
    return tempMap
    
    '''
    for x in range(1, MAP_WIDTH - 1):
        for y in range(1, MAP_HEIGHT - 1):
            if randint(0, 100) < CHANCE_TO_START_ALIVE:
                myMap[x][y].baseFg = colors.lighter_grey
                myMap[x][y].baseBg = colors.dark_sepia
                myMap[x][y].chasm = False
    for loop in range(STEPS_NUMBER):
        myMap = doStep(myMap)
    unblockTunnels()
    '''

myMap = [[]]

def countNeighbours(mapToUse, startX, startY, stopAtFirst = False):
    count = 0
    found = False
    for x in range(-1, 2):
        for y in range(-1, 2):
            if x == 0 and y == 0:
                continue
            else:
                otherX = startX + x
                otherY = startY + y
                if not mapToUse[otherX][otherY].chasm:
                    count += 1
                    found = True
                    if stopAtFirst:
                        break
        if stopAtFirst and found:
            break
    return count

def doStep(oldMap):
    newMap = list(copy.deepcopy(oldMap))
    for x in range(1, MAP_WIDTH - 1):
        for y in range(1, MAP_HEIGHT - 1):
            neighbours = countNeighbours(oldMap, x, y)
            if not oldMap[x][y].chasm:
                if neighbours < DEATH_LIMIT:
                    #newMap[x][y].baseFg = colors.dark_grey
                    #newMap[x][y].baseBg = colors.black
                    newMap[x][y].chasm = True
                else:
                    #newMap[x][y].baseFg = colors.lighter_grey
                    #newMap[x][y].baseBg = colors.dark_sepia
                    newMap[x][y].chasm = False
            else:
                if neighbours > BIRTH_LIMIT:
                    #newMap[x][y].baseFg = colors.lighter_grey
                    #newMap[x][y].baseBg = colors.dark_sepia
                    newMap[x][y].chasm = False
                else:
                    #newMap[x][y].baseFg = colors.dark_grey
                    #newMap[x][y].baseBg = colors.black
                    newMap[x][y].chasm = True
    return newMap

'''
def update(mapToUse):
    root.clear()
    try:
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if mapToUse[x][y].blocked:
                    root.draw_char(x, y, char = '#', fg = mapToUse[x][y].fg, bg = mapToUse[x][y].bg)
                else:
                    root.draw_char(x, y, char = None, fg = mapToUse[x][y].fg, bg = mapToUse[x][y].bg)
                if (x, y) == (firstX, firstY):
                    root.draw_char(x, y, char = 'X', fg = colors.red, bg = mapToUse[x][y].bg)
                if (x, y) == (lastX, lastY):
                    root.draw_char(x, y, char = 'X', fg = colors.green, bg = mapToUse[x][y].bg)
                    
                    
        #if dispEmpty:
        #    for (x,y) in emptyTiles:
        #        root.draw_char(x, y, char= ".", bg = colors.cyan)
        #    print(len(emptyTiles))
        
    except IndexError:
        traceback.print_exc()
        #pdb.set_trace()
        os._exit(-1)
        
    tdl.flush()
'''

def update(mapToUse = myMap):
    root.clear()
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            try:
                if mapToUse[x][y].blocked:
                    root.draw_char(x, y, '#', colors.grey, colors.darker_grey)
                elif mapToUse[x][y].chasm:
                    root.draw_char(x, y, None, bg = (16, 16, 16))
                elif mapToUse[x][y].door:
                    root.draw_char(x, y, '+', colors.darker_orange, colors.sepia)
                else:
                    root.draw_char(x, y, None, bg = colors.sepia)
            except IndexError:
                print('___PROBLEM___:', x, y)
    tdl.flush()

'''
def getInput():
    global mapIndex
    key = tdl.event.key_wait()
    actualKey = key.keychar.upper()
    if actualKey == 'ENTER':
        makeMap()
    elif actualKey == 'SPACE':
        print('CHANGING')
        if mapIndex == 0:
            mapIndex = 1
        elif mapIndex == 1:
            mapIndex = 0
    elif actualKey == 'E':
        global dispEmpty
        dispEmpty = not dispEmpty
    elif actualKey == 'A':
        global dispDebug
        dispDebug = not dispDebug
    elif actualKey in ("LEFT", "RIGHT"):
        global curRoomIndex
        maxIndex = len(rooms) - 1
        if actualKey == "LEFT":
            curRoomIndex -= 1
        else:
            curRoomIndex += 1
        if curRoomIndex < 0:
            curRoomIndex = int(maxIndex)
        if curRoomIndex > maxIndex:
            curRoomIndex = 0
'''

        
    
    
if __name__ == '__main__':
    makeMap()
    while not tdl.event.is_window_closed():
        update(myMap)
        #input = getInput()
                
