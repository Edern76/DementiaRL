import colors, copy, pdb, traceback, os, sys, time, math
from random import *
from code.custom_except import *
import tdlib as tdl
import code.dunbranches as dBr
from code.classes import Tile
import code.experiments.newCave as caveGen
import code.experiments.tunneling as tunneling
import code.chasmGen as chasmGen
import code.holeGen as holeGen
from copy import deepcopy


'''
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
'''

myMap = None
maxRooms = dBr.mainDungeon.maxRooms
roomMinSize = dBr.mainDungeon.roomMinSize
roomMaxSize = dBr.mainDungeon.roomMaxSize
roomEdges = None
tunnelEdges = None

WIDTH, HEIGHT, LIMIT = 150, 80, 20
MAP_WIDTH, MAP_HEIGHT = 140, 60
MID_MAP_WIDTH, MID_MAP_HEIGHT = MAP_WIDTH//2, MAP_HEIGHT//2
MID_WIDTH, MID_HEIGHT = int(WIDTH/2), int(HEIGHT/2)

if __name__ == '__main__':
    root = tdl.init(WIDTH, HEIGHT, 'Dementia')

myMap = []
caveList = []
MAX_ITER = 30000
WALL_LIMIT = 4 # number of neighboring walls for this cell to become a wall
WALL_PROB = 50

CAVE_MIN_SIZE = 16 #Def: 16
MINE_MIN_SIZE = 50 #Def: 100
CAVE_MAX_SIZE = 10000 #Def: 500
MINE_MAX_SIZE = 1000 #Def: 300
TOTAL_CAVE_MIN = 4000 #Def: 3000
TOTAL_MINE_MIN = 950 #Def: 2000

ROOM_MIN_SIZE = 5
ROOM_MAX_SIZE = 14
MAX_ROOMS = 12
MAX_CONFLICT_RATIO = 33 #%

roomEdges = []
tunnelEdges = []
roomList = []
caveTiles = []

SMOOTH_EDGES = True
SMOOTHING = 1

CHANCE_TO_START_ALIVE = 55 #Default : 55
CHANCE_TO_START_ALIVE_CHASM = 65 #Default : 65
DEATH_LIMIT = 3 #Default : 3
BIRTH_LIMIT = 4 #Default : 4
STEPS_NUMBER = 2 #Default : 2

emptyTiles = [] #List of tuples of the coordinates of emptytiles not yet processed by the floodfill algorithm
rooms = []
roomTiles = []
tunnelTiles = []
unchasmable = []
noCheckTiles = []

def initializeMapGen(currentBranch):
    chasms = False
    holes = False
    cave = False
    mine = False
    temple = False
    if currentBranch.mapGeneration['chasm']:
        chasms = True
    if currentBranch.mapGeneration['caves']:
        cave = True
    if currentBranch.mapGeneration['holes']:
        holes = True
    if currentBranch.mapGeneration['mines']:
        cave = True
        mine = True
    if currentBranch.mapGeneration['pillars']:
        temple = True
    
    return chasms, holes, cave, mine, temple

def generateMap(currentBranch = dBr.mainDungeon, level = 2):
    global roomEdges, tunnelEdges
    chasms, holes, cave, mine, pillars = initializeMapGen(currentBranch)
    if not cave and not mine:
        myMap, tunnelTiles, roomTiles, rooms = tunneling.makeTunnelMap(holes, True)
        if holes:
            myMap = holeGen.createHoles(myMap)
        if chasms:
            myMap = chasmGen.makeChasmMap(myMap, roomTiles, tunnelTiles)
    else:
        myMap, roomEdges, tunnelEdges, rooms = caveGen.generateCaveLevel(mine)
    
    if pillars:
        #baseMap = list(deepcopy(myMap))
        for x in range(1, MAP_WIDTH-1):
            for y in range(1, MAP_HEIGHT-1):
                if myMap[x][y].blocked and myMap[x][y].neighbours(myMap, True) == 3:
                    myMap[x][y].pillar = True
        
        for room in rooms:
            centerPillar = randint(0, 2)
            offsetW = ((room.x2 - room.x1) - 4) // 2
            offsetH = ((room.y2 - room.y1) - 4) // 2
            if centerPillar != 0:
                myMap[room.x1 + offsetW][room.y1 + offsetH].pillar = True
                myMap[room.x1 + offsetW][room.y2 - offsetH].pillar = True
                myMap[room.x2 - offsetW][room.y1 + offsetH].pillar = True
                myMap[room.x2 - offsetW][room.y2 - offsetH].pillar = True
            else:
                x, y = room.center()
                myMap[x][y].pillar = True
    
    myMap = updateTiles(myMap, currentBranch)
    
    roomsForStairs = checkStairsRooms(myMap, currentBranch, level, rooms)
    if roomsForStairs == 'abort':
        myMap, rooms, roomsForStairs = generateMap(currentBranch, level)
    
    return myMap, rooms, roomsForStairs

def updateTiles(mapToUse, branch):
    mapDict = branch.mapGeneration
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            tile = mapToUse[x][y]
            if tile.pillar and not tile.chasm:
                tile.baseCharacter = mapDict['pillarChar']
                tile.baseFg = mapDict['pillarColor']
                tile.baseBg = mapDict['groundBG']
                tile.baseDark_fg = mapDict['pillarDarkColor']
                tile.baseDark_bg = mapDict['groundDarkBG']
                tile.pillar = True
                tile.block_sight = True
            elif tile.blocked and not (x, y) in roomEdges and not (x, y) in tunnelEdges:
                tile.baseCharacter = mapDict['wallChar']
                tile.baseFg = mapDict['wallFG']
                tile.baseBg = mapDict['wallBG']
                tile.baseDark_fg = mapDict['wallDarkFG']
                tile.baseDark_bg = mapDict['wallDarkBG']
                tile.wall = True
                tile.block_sight = True
            elif tile.blocked and (x, y) in roomEdges:
                tile.baseCharacter = mapDict['wallChar']
                tile.baseFg = mapDict['mineWallFG']
                tile.baseBg = mapDict['mineWallBG']
                tile.baseDark_fg = mapDict['mineWallDarkFG']
                tile.baseDark_bg = mapDict['mineWallDarkBG']
                tile.wall = True
                tile.block_sight = True
            elif tile.blocked and (x, y) in tunnelEdges:
                tile.baseCharacter = mapDict['pillarChar']
                tile.baseFg = mapDict['pillarColor']
                tile.baseBg = mapDict['groundBG']
                tile.baseDark_fg = mapDict['pillarDarkColor']
                tile.baseDark_bg = mapDict['groundDarkBG']
                tile.pillar = True
                tile.block_sight = False
            elif tile.chasm:
                tile.baseCharacter = None
                tile.baseFg = None
                tile.baseBg = mapDict['chasmColor']
                tile.baseDark_fg = None
                tile.baseDark_bg = mapDict['chasmColor']
                tile.block_sight = False
                tile.baseBlocked = False
            elif tile.door:
                tile.baseCharacter = mapDict['doorChar']
                tile.baseFg = mapDict['doorColor']
                tile.baseBg = mapDict['groundBG']
                tile.baseDark_fg = mapDict['doorDarkColor']
                tile.baseDark_bg = mapDict['groundDarkBG']
                tile.baseBlocked = False
                tile.block_sight = True
            else:
                gravelChoice = randint(0, 20 + len(mapDict['gravelChars']))
                try:
                    tile.baseCharacter = mapDict['gravelChars'][gravelChoice]
                except:
                    tile.baseCharacter = None
                tile.baseFg = mapDict['gravelFG']
                tile.baseBg = mapDict['groundBG']
                tile.baseDark_fg = mapDict['gravelDarkFG']
                tile.baseDark_bg = mapDict['groundDarkBG']
                tile.baseBlocked = False
                tile.block_sight = False
    
    return mapToUse

'''
def update():
    root.clear()
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            tile = myMap[x][y]
            root.draw_char(x, y, tile.character, tile.fg, tile.bg)
    tdl.flush()
'''

def update(mapToUse = myMap):
    root.clear()
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            tile = mapToUse[x][y]
            try:
                root.draw_char(x, y, tile.character, tile.fg, tile.bg)
                '''
                if myMap[x][y].blocked and not (x, y) in roomEdges and not (x, y) in tunnelEdges:
                    root.draw_char(x, y, '#', colors.grey, colors.darker_grey)
                elif myMap[x][y].blocked and (x, y) in roomEdges:
                    root.draw_char(x, y, '#', colors.dark_sepia, colors.darkest_sepia)
                elif myMap[x][y].blocked and (x, y) in tunnelEdges:
                    root.draw_char(x, y, chr(254), colors.darkest_sepia, colors.sepia)
                elif mapToUse[x][y].chasm:
                    root.draw_char(x, y, None, bg = (16, 16, 16))
                elif mapToUse[x][y].door:
                    root.draw_char(x, y, '+', colors.darker_orange, colors.sepia)
                else:
                    root.draw_char(x, y, None, bg = colors.sepia)
                '''
            except IndexError:
                print('___PROBLEM___:', x, y)
    tdl.flush()
    
def checkStairsRooms(mapToUse, currentBranch, currentLevel, rooms):
    branchesToAdd = []
    for branch, level in currentBranch.branchesTo:
        if level == currentLevel:
            branchesToAdd.append((branch, 'down'))
    if currentBranch != dBr.mainDungeon or currentLevel > 1:
        if currentBranch.origBranch:
            branchesToAdd.append((currentBranch.origBranch, 'up'))
        else:
            branchesToAdd.append((currentBranch, 'up'))
    if currentLevel < currentBranch.maxDepth:
        branchesToAdd.append((currentBranch, 'down'))
    
    chosenRooms = []
    l = 0
    while len(chosenRooms) < len(branchesToAdd) and l < 300:
        curRoom = rooms[randint(0, len(rooms)-1)]
        if not curRoom in chosenRooms:
            centerX, centerY = curRoom.center()
            if not mapToUse[centerX][centerY].blocked and not mapToUse[centerX][centerY].chasm and not mapToUse[centerX][centerY].pillar:
                chosenRooms.append(curRoom)
        l += 1
    
    roomsForStairs = []
    while chosenRooms and branchesToAdd:
        randRoom = chosenRooms.pop(randint(0, len(chosenRooms)-1))
        randBranch, way = branchesToAdd.pop(randint(0, len(branchesToAdd)-1))
        roomsForStairs.append((randRoom, randBranch, way))
    
    if l >= 300:
        return 'abort'
    else:
        return roomsForStairs

if __name__ == '__main__':
    myMap, rooms, roomsForStairs = generateMap(dBr.greedDungeon)
    while not tdl.event.is_window_closed():
        update(myMap)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
