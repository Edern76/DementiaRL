import colors, copy, pdb, traceback, os, sys, time
from random import *
from code.custom_except import *
import tdlib as tdl


WIDTH, HEIGHT, LIMIT = 150, 80, 20
MAP_WIDTH, MAP_HEIGHT = 140, 60
MID_MAP_WIDTH, MID_MAP_HEIGHT = MAP_WIDTH//2, MAP_HEIGHT//2
MID_WIDTH, MID_HEIGHT = int(WIDTH/2), int(HEIGHT/2)

CHANCE_TO_START_ALIVE = 65
DEATH_LIMIT = 3
BIRTH_LIMIT = 4
STEPS_NUMBER = 2
MIN_ROOM_SIZE = 6

rooms = []
lastX = 0
lastY = 0
firstX = 0
firstY = 0

curRoomIndex = 0

sys.setrecursionlimit(3000)

if __name__ == '__main__':
    root = tdl.init(WIDTH, HEIGHT, 'Dementia')
    
class Tile:
    def __init__(self, blocked, x, y):
        self.baseBlocked = blocked
        self.x = x
        self.y = y
        self.indestructible = False
        self.belongsTo = []
        self.baseFg = colors.lighter_grey
        self.baseBg = colors.dark_sepia
        self.hole = True
        
    def setIndestructible(self):
        self.baseBlocked = True
        self.indestructible = True
        self.hole = False
        
    def open(self):
        if not self.indestructible:
            self.baseBlocked = False
            return True
        else:
            return False
    
    def close(self):
        if not self.blocked:
            self.baseBlocked = True
    
    def addOwner(self, toAdd):
        if not toAdd in self.belongsTo:
            if self.belongsTo:
                otherOwners = list(self.belongsTo)
            else:
                otherOwners = []
            self.belongsTo.append(toAdd)
            print(otherOwners)
            return otherOwners
    
    def returnOtherOwners(self, base):
        newList = list(self.belongsTo)
        newList.remove(base)
        return newList


class Rectangle:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        self.tiles = []
        
    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)
 
    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)
        
def createRoom(room):
    global myMap, roomTiles
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            myMap[x][y].baseBlocked = False
            
def createHorizontalTunnel(x1, x2, y):
    global myMap, tunnelTiles
    for x in range(min(x1, x2), max(x1, x2) + 1):
        myMap[x][y].baseBlocked = False
            
def createVerticalTunnel(y1, y2, x):
    global myMap, tunnelTiles
    for y in range(min(y1, y2), max(y1, y2) + 1):
        myMap[x][y].baseBlocked = False

def checkMap():
    global myMap
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if myMap[x][y].hole and not myMap[x][y].indestructible:
                myMap[x][y].baseBlocked = False

def createHoles(mapToUse):
    for x in range(1, MAP_WIDTH - 1):
        for y in range(1, MAP_HEIGHT - 1):
            if randint(0, 100) < CHANCE_TO_START_ALIVE:
                mapToUse[x][y].hole = False
    for loop in range(STEPS_NUMBER):
        mapToUse = doStep(mapToUse)
    
    return mapToUse
    
def makeMap():
    global myMap, rooms, firstX, firstY, lastX, lastY

    myMap = [[Tile(blocked = True, x = x, y = y) for y in range(MAP_HEIGHT)]for x in range(MAP_WIDTH)] #Creates a rectangle of blocking tiles from the Tile class, aka walls. Each tile is accessed by myMap[x][y], where x and y are the coordinates of the tile.
    rooms = []
    roomTiles = []
    tunnelTiles = []
    numberRooms = 0
    
    for x in range(MAP_WIDTH):
        myMap[x][0].setIndestructible()
        myMap[x][MAP_HEIGHT - 1].setIndestructible()
    for y in range(MAP_HEIGHT):
        myMap[0][y].setIndestructible()
        myMap[MAP_WIDTH - 1][y].setIndestructible()
 
    for r in range(30):
        w = randint(6, 10)
        h = randint(6, 10)
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
            lastCreatedRoom = newRoom
            (new_x, new_y) = newRoom.center()
            if numberRooms != 0:
                (previous_x, previous_y) = rooms[numberRooms-1].center()
                if randint(0, 1):
                    createHorizontalTunnel(previous_x, new_x, previous_y)
                    createVerticalTunnel(previous_y, new_y, new_x)
                else:
                    createVerticalTunnel(previous_y, new_y, previous_x)
                    createHorizontalTunnel(previous_x, new_x, new_y)
            else:
                firstX, firstY = new_x, new_y
            rooms.append(newRoom)
            numberRooms += 1
    lastX, lastY = new_x, new_y
    
    myMap = createHoles(myMap)
    checkMap()

myMap = [[]]

def countNeighbours(mapToUse, startX, startY):
    count = 0
    found = False
    for x in range(-1, 2):
        for y in range(-1, 2):
            if x == 0 and y == 0:
                continue
            else:
                otherX = startX + x
                otherY = startY + y
                if not mapToUse[otherX][otherY].hole:
                    count += 1
    return count

def doStep(oldMap):
    newMap = list(copy.deepcopy(oldMap))
    for x in range(1, MAP_WIDTH - 1):
        for y in range(1, MAP_HEIGHT - 1):
            neighbours = countNeighbours(oldMap, x, y)
            if not oldMap[x][y].hole:
                if neighbours < DEATH_LIMIT:
                    newMap[x][y].hole = True
                else:
                    newMap[x][y].hole = False
            else:
                if neighbours > BIRTH_LIMIT:
                    newMap[x][y].hole = False
                else:
                    newMap[x][y].hole = True
    return newMap

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
        
    except IndexError:
        traceback.print_exc()
        os._exit(-1)
        
    tdl.flush()
    
if __name__ == '__main__':
    makeMap()
    while not tdl.event.is_window_closed():
        update(myMap)
                
