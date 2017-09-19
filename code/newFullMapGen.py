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

def generateMap(currentBranch = dBr.mainDungeon):
    global roomEdges, tunnelEdges
    chasms, holes, cave, mine, temple = initializeMapGen(currentBranch)
    if not cave and not mine:
        if not temple:
            myMap, tunnelTiles, roomTiles = tunneling.makeTunnelMap(holes, True)
            if holes:
                myMap = holeGen.createHoles(myMap)
            if chasms:
                myMap = chasmGen.makeChasmMap(myMap, roomTiles, tunnelTiles)
    else:
        myMap, roomEdges, tunnelEdges = caveGen.generateCaveLevel(mine)
    
    return myMap

def updateTiles(mapToUse):
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            tile = mapToUse[x][y]
            if tile.blocked:
                root.draw_char(x, y, '#', colors.grey, colors.darker_grey)
            elif mapToUse[x][y].chasm:
                root.draw_char(x, y, None, bg = (16, 16, 16))
            elif mapToUse[x][y].door:
                root.draw_char(x, y, '+', colors.darker_orange, colors.sepia)
            else:
                root.draw_char(x, y, None, bg = colors.sepia)

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
            try:
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
            except IndexError:
                print('___PROBLEM___:', x, y)
    tdl.flush()

if __name__ == '__main__':
    myMap = generateMap(dBr.mainDungeon)
    while not tdl.event.is_window_closed():
        update(myMap)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
