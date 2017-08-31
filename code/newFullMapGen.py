import colors, copy, pdb, traceback, os, sys, time, math
from random import *
from code.custom_except import *
import tdlib as tdl
import code.dunbranches as dBr
from code.classes import Tile
import code.experiments.newCave as caveGen


'''
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
'''

myMap = None
color_dark_wall = dBr.mainDungeon.color_dark_wall
color_light_wall = dBr.mainDungeon.color_light_wall
color_dark_ground = dBr.mainDungeon.color_dark_ground
color_dark_gravel = dBr.mainDungeon.color_dark_gravel
color_light_ground = dBr.mainDungeon.color_light_ground
color_light_gravel = dBr.mainDungeon.color_light_gravel
maxRooms = dBr.mainDungeon.maxRooms
roomMinSize = dBr.mainDungeon.roomMinSize
roomMaxSize = dBr.mainDungeon.roomMaxSize

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
    global color_dark_wall, color_light_wall, color_dark_ground, color_dark_gravel, color_light_ground, color_light_gravel, maxRooms, roomMinSize, roomMaxSize
    
    color_dark_wall = currentBranch.color_dark_wall
    color_light_wall = currentBranch.color_light_wall
    color_dark_ground = currentBranch.color_dark_ground
    color_dark_gravel = currentBranch.color_dark_gravel
    color_light_ground = currentBranch.color_light_ground
    color_light_gravel = currentBranch.color_light_gravel
    maxRooms = currentBranch.maxRooms
    roomMinSize = currentBranch.roomMinSize
    roomMaxSize = currentBranch.roomMaxSize
    
    chasms = False
    holes = False
    cave = False
    mine = False
    temple = False
    for feature in currentBranch.genFeatures:
        if feature == 'chasms':
            chasms = True
        if feature == 'cave':
            cave = True
        if feature == 'holes':
            holes = True
        if feature == 'mines':
            cave = True
            mine = True
        if feature == 'temple':
            temple = True
    
    return chasms, holes, cave, mine, temple

def generateMap(currentBranch = dBr.mainDungeon):
    chasms, holes, cave, mine, temple = initializeMapGen(currentBranch)
    if not cave and not mine:
        pass
    else:
        myMap = caveGen.generateCaveLevel(mine)
    
    return myMap

def update():
    root.clear()
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            tile = myMap[x][y]
            root.draw_char(x, y, tile.character, tile.fg, tile.bg)
    tdl.flush()

if __name__ == '__main__':
    myMap = generateMap(dBr.greedDungeon)
    while not tdl.event.is_window_closed():
        update()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
