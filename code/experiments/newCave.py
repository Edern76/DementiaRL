import colors, copy, pdb, traceback, os, sys, time, math
from random import *
from code.custom_except import *
import tdlib as tdl
from code.classes import Tile, Rectangle

WIDTH, HEIGHT, LIMIT = 150, 80, 20
MAP_WIDTH, MAP_HEIGHT = 140, 60
MID_MAP_WIDTH, MID_MAP_HEIGHT = MAP_WIDTH//2, MAP_HEIGHT//2
MID_WIDTH, MID_HEIGHT = int(WIDTH/2), int(HEIGHT/2)

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


if __name__ == '__main__':
    root = tdl.init(WIDTH, HEIGHT, 'Dementia')

def createRoom(room):
    global myMap, roomEdges
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            myMap[x][y].baseBlocked = False
    for x in range(room.x1, room.x2 + 1):
        if myMap[x][room.y1].blocked:
            roomEdges.append(myMap[x][room.y1])
        if myMap[x][room.y2].blocked:
            roomEdges.append(myMap[x][room.y2])
    for y in range(room.y1, room.y2 + 1):
        if myMap[room.x1][y].blocked:
            roomEdges.append(myMap[room.x1][y])
        if myMap[room.x2][y].blocked:
            roomEdges.append(myMap[room.x2][y])

def createHorizontalTunnel(x1, x2, y):
    global myMap, tunnelEdges
    for x in range(min(x1, x2), max(x1, x2) + 1):
        if (x, y) in caveTiles:
            break
        myMap[x][y].baseBlocked = False
        wood = randint(0, 4)
        if wood == 0:
            if myMap[x][y-1].blocked:
                tunnelEdges.append(myMap[x][y-1])
            if myMap[x][y+1].blocked:
                tunnelEdges.append(myMap[x][y+1])
            
def createVerticalTunnel(y1, y2, x):
    global myMap, tunnelEdges
    for y in range(min(y1, y2), max(y1, y2) + 1):
        if (x, y) in caveTiles:
            break
        myMap[x][y].baseBlocked = False
        wood = randint(0, 4)
        if wood == 0:
            if myMap[x-1][y].blocked:
                tunnelEdges.append(myMap[x-1][y])
            if myMap[x+1][y].blocked:
                tunnelEdges.append(myMap[x+1][y])

def randomFillMap():
    global caveList, myMap
    for x in range (1, MAP_WIDTH-1):
        for y in range (1, MAP_HEIGHT-1):
            if randint(1, 100) >= WALL_PROB:
                myMap[x][y].baseBlocked = False
    #update()

def cleanUpMap():
    global caveList, myMap
    if (SMOOTH_EDGES):
        for i in range (0, 5):
            # Look at each cell individually and check for smoothness
            for x in range(1, MAP_WIDTH-1):
                for y in range (1, MAP_HEIGHT-1):
                    if myMap[x][y].blocked and myMap[x][y].neighbors(myMap, True, True) <= SMOOTHING and not myMap[x][y] in roomEdges:
                        myMap[x][y].baseBlocked = False
    #update()

def createCaves():
    global caveList, myMap
    # ==== Create distinct caves ====
    for i in range (0, MAX_ITER):
        # Pick a random point with a buffer around the edges of the map
        tileX = randint(1, MAP_WIDTH-2) #(2,mapWidth-3)
        tileY = randint(1, MAP_HEIGHT-2) #(2,mapHeight-3)

        # if the cell's neighboring walls > self.neighbors, set it to 1
        if myMap[tileX][tileY].neighbors(myMap, True) > WALL_LIMIT:
            myMap[tileX][tileY].baseBlocked = True
        # or set it to 0
        elif myMap[tileX][tileY].neighbors(myMap, True) < WALL_LIMIT:
            myMap[tileX][tileY].baseBlocked = False
    #update()
     

    # ==== Clean Up Map ====
    cleanUpMap()
    #update()

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
                myMap[drunkardX][drunkardY].baseBlocked = False
    #update()

def floodFill(x,y, mine = False):
    global caveList, myMap
    '''
    flood fill the separate regions of the level, discard
    the regions that are smaller than a minimum size, and 
    create a reference for the rest.
    '''
    if not mine:
        minSize = CAVE_MIN_SIZE
        maxSize = CAVE_MAX_SIZE
    else:
        minSize = MINE_MIN_SIZE
        maxSize = MINE_MAX_SIZE
        
    cave = []
    tile = (x,y)
    toBeFilled = [tile]
    while toBeFilled:
        tile = toBeFilled.pop()
        x, y = tile
        if tile not in cave:
            cave.append(tile)
            
            myMap[x][y].baseBlocked = True
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

    if maxSize >= len(cave) >= minSize:
        caveList.append(cave)
    #update()

def getCaves(mine=False):
    global caveList, myMap
    # locate all the caves within myMap and stores them in caveList
    for x in range (MAP_WIDTH):
        for y in range (MAP_HEIGHT):
            if not myMap[x][y].blocked:
                floodFill(x,y, mine)

    for cave in caveList:
        for tile in cave:
            x, y = tile
            myMap[x][y].baseBlocked = False
    #update()

def checkConnectivity(cave1, cave2):
    global caveList, myMap
    # floods cave1, then checks a point in cave2 for the flood
    connectedRegion = []
    start = cave1[randint(0, len(cave1) - 1)] # get an element from cave1
    
    toBeFilled = [start]
    found = False
    while toBeFilled:
        tile = toBeFilled.pop()
        if tile in cave2:
            found = True
            break
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
    
    return found
    #end = cave2[randint(0, len(cave2) - 1)]

    #if end in connectedRegion: return True

    #else: return False


def floodFillRoom(room):
    global caveList, myMap
    # floods cave1, then checks a point in cave2 for the flood
    allTiles = []
    allTiles.extend(caveTiles)
    for newRoom in roomList:
        if newRoom != room:
            allTiles.extend(newRoom.tiles)
    connectedRegion = []
    start = room.tiles[randint(0, len(room.tiles) - 1)] # get an element from cave1
    
    toBeFilled = [start]
    found = False
    while toBeFilled:
        tile = toBeFilled.pop()
        if tile in allTiles:
            found = True
            break
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
    
    return found

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
            createTunnel(point1, point2, currentCave)
    #update()

def makeMineLayout():
    global caveList, myMap, roomList
    
    roomList = []
    
    while len(roomList) < MAX_ROOMS:
        x = randint(1, MAP_WIDTH - 1)
        y = randint(1, MAP_HEIGHT - 1)
        
        w = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        if x + w >= MAP_WIDTH or y + h >= MAP_HEIGHT:
            continue
        newRoom = Rectangle(x, y, w, h)
        intersect = False
        for room in roomList:
            if newRoom.intersect(room) or not newRoom.checkForCaveIntersection(caveTiles):
                intersect = True
                break
        if intersect:
            continue
        createRoom(newRoom)
        
        (new_x, new_y) = newRoom.center()
        if len(roomList) == 0:
            cave = caveList[randint(0, len(caveList) - 1)]
            point = cave[randint(0, len(cave) - 1)]
            createTunnel((new_x, new_y), point, newRoom.tiles)
            (previous_x, previous_y) = newRoom.center()
        else:
            tunnel = randint(0, 2)
            if tunnel == 0:
                createHorizontalTunnel(previous_x, new_x, previous_y)
                createVerticalTunnel(previous_y, new_y, new_x)
            elif tunnel == 1:
                createVerticalTunnel(previous_y, new_y, previous_x)
                createHorizontalTunnel(previous_x, new_x, new_y)
            else:
                createTunnel((new_x, new_y), (previous_x, previous_y), newRoom.tiles)
        (previous_x, previous_y) = (new_x, new_y)
        roomList.append(newRoom)
        '''
        root.clear()
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if myMap[x][y].blocked:
                    root.draw_char(x, y, '#', colors.grey, colors.darker_grey)
                elif (x, y) in newRoom.tiles:
                    root.draw_char(x, y, None, bg = colors.red)
                else:
                    root.draw_char(x, y, None, bg = colors.sepia)
        tdl.flush()
        time.sleep(1)
        update()
        '''

    for room in roomList:
        connected = floodFillRoom(room)
        if not connected:
            center = room.center()
            best = room.center()
            minDist = 9999
            i = 0
            while i<100:
                x = randint(1, MAP_WIDTH-1)
                y = randint(1, MAP_HEIGHT-1)
                if myMap[x][y].blocked:
                    continue
                newPoint = (x, y)
                newDist = distanceFormula(center, newPoint)
                if newDist < minDist:
                    minDist = newDist
                    best = newPoint
                i += 1
            createTunnel(center, best, room)

def generateCaveLevel(mine=False):
    global caveList, myMap, caveTiles
    # Creates an empty 2D array or clears existing array
    
    if mine:
        minSize = TOTAL_MINE_MIN
    else:
        minSize = TOTAL_CAVE_MIN
    
    caveList = []

    
    myMap = [[Tile(True, x, y) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

    randomFillMap()
    
    createCaves()

    getCaves(mine)
    
    freeTiles = 0
    for cave in caveList:
        freeTiles += len(cave)
    
    if freeTiles >= minSize:
        caveTiles = []
        for cave in caveList:
            caveTiles.extend(cave)
        connectCaves()
        
        if mine:
            makeMineLayout()
    
        cleanUpMap()
    else:
        #time.sleep(2)
        generateCaveLevel(mine)
    
    return myMap

def update():
    root.clear()
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if myMap[x][y].blocked and not myMap[x][y] in roomEdges and not myMap[x][y] in tunnelEdges:
                root.draw_char(x, y, '#', colors.grey, colors.darker_grey)
            elif myMap[x][y].blocked and myMap[x][y] in roomEdges:
                root.draw_char(x, y, '#', colors.dark_sepia, colors.darkest_sepia)
            elif myMap[x][y].blocked and myMap[x][y] in tunnelEdges:
                root.draw_char(x, y, chr(254), colors.darkest_sepia, colors.sepia)
            else:
                root.draw_char(x, y, None, bg = colors.sepia)
    tdl.flush()

if __name__ == '__main__':
    myMap = generateCaveLevel(True)
    while not tdl.event.is_window_closed():
        update()





