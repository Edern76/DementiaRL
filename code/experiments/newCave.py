import colors, copy, pdb, traceback, os, sys, time, math
from random import *
from colors import darker_sepia
from code.custom_except import *
import tdlib as tdl

WIDTH, HEIGHT, LIMIT = 150, 80, 20
MAP_WIDTH, MAP_HEIGHT = 140, 60
MID_MAP_WIDTH, MID_MAP_HEIGHT = MAP_WIDTH//2, MAP_HEIGHT//2
MID_WIDTH, MID_HEIGHT = int(WIDTH/2), int(HEIGHT/2)

myMap = []
caveList = []
MAX_ITER = 30000
WALL_LIMIT = 4 # number of neighboring walls for this cell to become a wall
WALL_PROB = 50

CAVE_MIN_SIZE = 16
CAVE_MAX_SIZE = 500

SMOOTH_EDGES = True
SMOOTHING = 1


if __name__ == '__main__':
    root = tdl.init(WIDTH, HEIGHT, 'Dementia')

class Tile:
    def __init__(self, x, y, blocked):
        self.x = x
        self.y = y
        self.blocked = blocked
    
    def neighbors(self, count = False, cardinal = False):
        global myMap
        x = self.x
        y = self.y
        try:
            upperLeft = myMap[x - 1][y - 1]
        except IndexError:
            upperLeft = None
        except TypeError:
            traceback.print_exc()
            print(myMap)
            print("WRONG TILE = ", end="")
            print(x,y, sep=";")
            
        try:
            up = myMap[x][y - 1]
        except IndexError:
            up = None
            
        try:
            upperRight = myMap[x + 1][y - 1]
        except IndexError:
            upperRight = None
            
        try:
            left = myMap[x - 1][y]
        except IndexError:
            left = None
            
        try:
            right = myMap[x + 1][y]
        except IndexError:
            right = None
            
        try:
            lowerLeft = myMap[x - 1][y + 1]
        except IndexError:
            lowerLeft = None
        
        try:
            low = myMap[x][y + 1]
        except IndexError:
            low = None

        try:
            lowerRight = myMap[x + 1][y + 1]
        except IndexError:
            lowerRight = None
        
        if not count and not cardinal:
            return [i for i in [upperLeft, up, upperRight, left, right, lowerLeft, low, lowerRight] if i is not None]
        elif cardinal and not count:
            return [i for i in [up, left, right, low] if i is not None]
        elif cardinal and count:
            c = 0
            for i in [up, left, right, low]:
                if i and i.blocked:
                    c += 1
            return c
        else:
            c = 0
            for i in [upperLeft, up, upperRight, left, right, lowerLeft, low, lowerRight]:
                if i and i.blocked:
                    c += 1
            return c

def randomFillMap():
    global caveList, myMap
    for x in range (1, MAP_WIDTH-1):
        for y in range (1, MAP_HEIGHT-1):
            if randint(1, 100) >= WALL_PROB:
                myMap[x][y].blocked = False
    update()


def cleanUpMap():
    global caveList, myMap
    if (SMOOTH_EDGES):
        for i in range (0, 5):
            # Look at each cell individually and check for smoothness
            for x in range(1, MAP_WIDTH-1):
                for y in range (1, MAP_HEIGHT-1):
                    if myMap[x][y].blocked and myMap[x][y].neighbors(True, True) <= SMOOTHING:
                        myMap[x][y].blocked = False
    update()

def createCaves():
    global caveList, myMap
    # ==== Create distinct caves ====
    for i in range (0, MAX_ITER):
        # Pick a random point with a buffer around the edges of the map
        tileX = randint(1, MAP_WIDTH-2) #(2,mapWidth-3)
        tileY = randint(1, MAP_HEIGHT-2) #(2,mapHeight-3)

        # if the cell's neighboring walls > self.neighbors, set it to 1
        if myMap[tileX][tileY].neighbors(True) > WALL_LIMIT:
            myMap[tileX][tileY].blocked = True
        # or set it to 0
        elif myMap[tileX][tileY].neighbors(True) < WALL_LIMIT:
            myMap[tileX][tileY].blocked = False
    update()
     

    # ==== Clean Up Map ====
    cleanUpMap()
    update()

def createTunnel(point1,point2,currentCave):
    global caveList, myMap
    # run a heavily weighted random Walk 
    # from point1 to point1
    drunkardX, drunkardY = point2
    goalX, goalY = point1
    while (drunkardX,drunkardY) not in currentCave:
        # ==== Choose Direction ====
        north = 1.0
        south = 1.0
        east = 1.0
        west = 1.0

        weight = 1

        # weight the random walk against edges
        if drunkardX < goalX: # drunkard is left of point1
            east += weight
        elif drunkardX > goalX: # drunkard is right of point1
            west += weight
        if drunkardY < goalY: # drunkard is above point1
            south += weight
        elif drunkardY > goalY: # drunkard is below point1
            north += weight

        # normalize probabilities so they form a range from 0 to 1
        total = north+south+east+west
        north /= total
        south /= total
        east /= total
        west /= total
        north*= 100
        south*= 100
        east*= 100
        west*= 100

        # choose the direction
        choice = randint(1, 100)
        if 0 <= choice < north:
            dx = 0
            dy = -1
        elif north <= choice < (north+south):
            dx = 0
            dy = 1
        elif (north+south) <= choice < (north+south+east):
            dx = 1
            dy = 0
        else:
            dx = -1
            dy = 0

        # ==== Walk ====
        # check colision at edges
        if (0 < drunkardX+dx < MAP_WIDTH-1) and (0 < drunkardY+dy < MAP_HEIGHT-1):
            drunkardX += dx
            drunkardY += dy
            if myMap[drunkardX][drunkardY].blocked:
                myMap[drunkardX][drunkardY].blocked = False
    update()

def floodFill(x,y):
    global caveList, myMap
    '''
    flood fill the separate regions of the level, discard
    the regions that are smaller than a minimum size, and 
    create a reference for the rest.
    '''
    cave = []
    tile = (x,y)
    toBeFilled = [tile]
    while toBeFilled:
        tile = toBeFilled.pop()
        x, y = tile
        if tile not in cave:
            cave.append(tile)
            
            myMap[x][y].blocked = True
            north = (x,y-1)
            south = (x,y+1)
            east = (x+1,y)
            west = (x-1,y)
            
            for direction in [north,south,east,west]:
                newX, newY = direction
                try:
                    if not myMap[newX][newY].blocked:
                        if direction not in toBeFilled and direction not in cave:
                            toBeFilled.append(direction)
                except IndexError:
                    print(newX, newY)

    if len(cave) >= CAVE_MIN_SIZE:
        caveList.append(cave)
    update()

def getCaves():
    global caveList, myMap
    # locate all the caves within myMap and stores them in caveList
    for x in range (MAP_WIDTH):
        for y in range (MAP_HEIGHT):
            if not myMap[x][y].blocked:
                floodFill(x,y)

    for cave in caveList:
        for tile in cave:
            x, y = tile
            myMap[x][y].blocked = False
    update()

def checkConnectivity(cave1, cave2):
    global caveList, myMap
    # floods cave1, then checks a point in cave2 for the flood

    connectedRegion = []
    start = cave1[randint(0, len(cave1) - 1)] # get an element from cave1
    
    toBeFilled = [start]
    while toBeFilled:
        tile = toBeFilled.pop()

        if tile not in connectedRegion:
            connectedRegion.append(tile)

            #check adjacent cells
            x, y = tile
            north = (x,y-1)
            south = (x,y+1)
            east = (x+1,y)
            west = (x-1,y)

            for direction in [north,south,east,west]:
                newX, newY = direction
                if not myMap[newX][newY].blocked:
                    if direction not in toBeFilled and direction not in connectedRegion:
                        toBeFilled.append(direction)

    end = cave2[randint(0, len(cave2) - 1)]

    if end in connectedRegion: return True

    else: return False

def distanceFormula(point1,point2):
    x1, y1 = point1
    x2, y2 = point2
    d = math.sqrt( (x2-x1)**2 + (y2 - y1)**2)
    return d

def connectCaves():
    global caveList, myMap
    # Find the closest cave to the current cave
    for currentCave in caveList:
        point1 = currentCave[randint(0, len(currentCave) - 1)]
        point2 = None
        distance = 999999999
        for nextCave in caveList:
            if nextCave != currentCave and not checkConnectivity(currentCave,nextCave):
                # choose a random point from nextCave
                nextPoint = nextCave[randint(0, len(nextCave) - 1)]
                # compare distance of point1 to old and new point2
                newDistance = distanceFormula(point1,nextPoint)
                if (newDistance < distance) or distance == None:
                    point2 = nextPoint
                    distance = newDistance

        if point2: # if all tunnels are connected, point2 == None
            createTunnel(point1, point2,currentCave)
    update()

def generateCaveLevel():
    global caveList, myMap
    # Creates an empty 2D array or clears existing array
    caveList = []

    
    myMap = [[Tile(x, y, blocked=True) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

    randomFillMap()
    
    createCaves()

    getCaves()

    connectCaves()

    cleanUpMap()

def update():
    root.clear()
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if myMap[x][y].blocked:
                root.draw_char(x, y, '#', colors.grey, colors.darker_grey)
            else:
                root.draw_char(x, y, None, bg = colors.sepia)
    tdl.flush()

if __name__ == '__main__':
    generateCaveLevel()
    while not tdl.event.is_window_closed():
        update()





