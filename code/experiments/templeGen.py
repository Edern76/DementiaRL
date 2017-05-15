import tdl, colors, copy, pdb, traceback, os, sys, time
from random import *
from custom_except import *
from copy import deepcopy


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
    def __init__(self, blocked, x, y, char = '#'):
        self.blocked = blocked
        self.x = x
        self.y = y
        self.char = char
        self.indestructible = False
        self.belongsTo = []
        self.fg = colors.lighter_grey
        self.bg = colors.grey
        self.pillar = False
        
    def setIndestructible(self):
        self.blocked = True
        self.indestructible = True

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

def findNeighbours(mapToUse, startX, startY, stopAtFirst = False, cross = False):
    found = False
    for x in range(-1, 2):
        for y in range(-1, 2):
            if x == 0 and y == 0:
                continue
            else:
                notCorner = not ((x==1 and y==1) or (x==1 and y==-1) or (x==-1 and y==-1) or (x==-1 and y==1)) 
                if not cross or notCorner:
                    otherX = startX + x
                    otherY = startY + y
                    if mapToUse[otherX][otherY].blocked:
                        found = True
                        if stopAtFirst:
                            break
        if stopAtFirst and found:
            break
    return found

def countNeighbours(mapToUse, startX, startY, stopAtFirst = False):
    found = False
    count = 0
    for x in range(-1, 2):
        for y in range(-1, 2):
            if x == 0 and y == 0:
                continue
            else:
                otherX = startX + x
                otherY = startY + y
                if 0 <= otherX < MAP_WIDTH and 0 <= otherY < MAP_HEIGHT:
                    if mapToUse[otherX][otherY].blocked:
                        found = True
                        count += 1
                        if stopAtFirst:
                            break
        if stopAtFirst and found:
            break
    return count

def createRoom(room):
    global myMap
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            myMap[x][y].blocked = False
            myMap[x][y].char = None
    centerPillar = randint(0, 2)
    if centerPillar != 0:
        myMap[room.x1 + 2][room.y1 + 2].pillar = True
        myMap[room.x1 + 2][room.y1 + 2].char = 'o'
        myMap[room.x1 + 2][room.y2 - 2].pillar = True
        myMap[room.x1 + 2][room.y2 - 2].char = 'o'
        myMap[room.x2 - 2][room.y1 + 2].pillar = True
        myMap[room.x2 - 2][room.y1 + 2].char = 'o'
        myMap[room.x2 - 2][room.y2 - 2].pillar = True
        myMap[room.x2 - 2][room.y2 - 2].char = 'o'
    else:
        x, y = room.center()
        myMap[x][y].pillar = True
        myMap[x][y].char = 'o'
            
def createHorizontalTunnel(x1, x2, y, big = False):
    global myMap
    for x in range(min(x1, x2), max(x1, x2) + 1):
        myMap[x][y].blocked = False
        if myMap[x][y].char == '#':
            myMap[x][y].char = None
    if big:
        #pillar = 0
        for x in range(min(x1, x2) - 1, max(x1, x2) + 2):
            myMap[x][y + 1].blocked = False
            if myMap[x][y + 1].char == '#':
                myMap[x][y + 1].char = None
            myMap[x][y - 1].blocked = False
            if myMap[x][y - 1].char == '#':
                myMap[x][y - 1].char = None
            #if pillar == 2:
            #    if findNeighbours(myMap, x, y - 1, True, True) and findNeighbours(myMap, x, y + 1, True, True):
            #        myMap[x][y - 1].pillar = True
            #        myMap[x][y - 1].char = 'o'
            #        myMap[x][y + 1].pillar = True
            #        myMap[x][y + 1].char = 'o'
            #        pillar = 0
            #else:
            #    pillar += 1
            
def createVerticalTunnel(y1, y2, x, big = False):
    global myMap
    for y in range(min(y1, y2), max(y1, y2) + 1):
        myMap[x][y].blocked = False
        if myMap[x][y].char == '#':
            myMap[x][y].char = None
    if big:
        #pillar = 0
        for y in range(min(y1, y2) - 1, max(y1, y2) + 2):
            myMap[x - 1][y].blocked = False
            if myMap[x - 1][y].char == '#':
                myMap[x - 1][y].char = None
            myMap[x + 1][y].blocked = False
            if myMap[x + 1][y].char == '#':
                myMap[x + 1][y].char = None
            #if pillar == 2:
            #    if findNeighbours(myMap, x - 1, y, True, True) and findNeighbours(myMap, x + 1, y, True, True):
            #        myMap[x - 1][y].pillar = True
            #        myMap[x - 1][y].char = 'o'
            #        myMap[x + 1][y].pillar = True
            #        myMap[x + 1][y].char = 'o'
            #        pillar = 0
            #else:
            #    pillar += 1

def secretRoomTest(startingX, endX, startingY, endY):
    for x in range(startingX, endX):
        for y in range(startingY, endY):
            if not myMap[x][y].blocked:
                if x >= 10 and x <= MAP_WIDTH - 10 and y >= 10 and y <= MAP_HEIGHT -10:
                    if myMap[x + 1][y].blocked: #right of the current tile
                        intersect = False
                        for indexX in range(9):
                            for indexY in range(9):
                                if not myMap[x + 1 + indexX][y - 4 + indexY].blocked:
                                    intersect = True
                                    break
                        if not intersect:
                            print("right")
                            return x + 1, y - 4, x + 1, y, 'right'
                    if myMap[x - 1][y].blocked: #left
                        intersect = False
                        for indexX in range(9):
                            for indexY in range(9):
                                if not myMap[x - 1 - indexX][y - 4 + indexY].blocked:
                                    intersect = True
                                    break
                        if not intersect:
                            print("left")
                            return x - 9, y - 4, x - 1, y, 'left'
                    if myMap[x][y + 1].blocked: #under
                        intersect = False
                        for indexX in range(9):
                            for indexY in range(9):
                                if not myMap[x - 4 + indexX][y + 1 + indexY].blocked:
                                    intersect = True
                                    break
                        if not intersect:
                            print("under")
                            return x - 4, y + 1, x, y + 1, 'under'
                    if myMap[x][y - 1].blocked: #above
                        intersect = False
                        for indexX in range(9):
                            for indexY in range(9):
                                if not myMap[x - 4 + indexX][y - 1 - indexY].blocked:
                                    intersect = True
                                    break
                        if not intersect:
                            print("above")
                            return x - 4, y - 9, x, y - 1, 'above'

def secretRoom():
    global myMap
    quarter = randint(1, 4)
    if quarter == 1:
        minX = 1
        maxX = MID_MAP_WIDTH
        minY = 1
        maxY = MID_MAP_HEIGHT 
    if quarter == 2:
        minX = MID_MAP_WIDTH + 1
        maxX = MAP_WIDTH
        minY = 1
        maxY = MID_MAP_HEIGHT
    if quarter == 3:
        minX = 1
        maxX = MID_MAP_WIDTH
        minY = MID_MAP_HEIGHT + 1
        maxY = MAP_HEIGHT
    if quarter == 4:
        minX = MID_MAP_WIDTH + 1
        maxX = MAP_WIDTH
        minY = MID_MAP_HEIGHT + 1
        maxY = MAP_HEIGHT
    x, y, entryX, entryY, side = secretRoomTest(minX, maxX, minY, maxY)
    if not (x == 'cancelled' or y == 'cancelled' or entryX == 'cancelled' or entryY == 'cancelled'):
        secretRoom = Rectangle(x, y, 8, 8)
        createRoom(secretRoom)
        myMap[entryX][entryY].blocked = False
        myMap[entryX][entryY].char = '#'
        myMap[entryX][entryY].fg = colors.red
        myMap[x][y].blocked = False
        for X in range(7):
            for Y in range(7):
                if not myMap[x + 1 + X][y + 1 + Y].pillar:
                    myMap[x + 1 + X][y + 1 + Y].char = '-'
                    myMap[x + 1 + X][y + 1 + Y].fg = colors.sepia
                else:
                    myMap[x + 1 + X][y + 1 + Y].fg = colors.darker_sepia
                myMap[x + 1 + X][y + 1 + Y].bg = colors.light_sepia
        if side != 'left':
            sideFalse = False
            for k in range(7):
                if not 5 <= countNeighbours(myMap, x + 8, y + 1 + k) <= 6:
                    sideFalse = True
            if not sideFalse:
                for k in range(7):
                    myMap[x + 8][y + 1 + k].char = '='
                    myMap[x + 8][y + 1 + k].fg = colors.dark_sepia
                    myMap[x + 8][y + 1 + k].bg = colors.sepia
        if side != 'right':
            sideFalse = False
            for k in range(7):
                if not 5 <= countNeighbours(myMap, x, y + 1 + k) <= 6:
                    sideFalse = True
            if not sideFalse:
                for k in range(7):
                    myMap[x][y + 1 + k].char = '='
                    myMap[x][y + 1 + k].fg = colors.dark_sepia
                    myMap[x][y + 1 + k].bg = colors.sepia
        if side != 'under':
            sideFalse = False
            for k in range(7):
                if not 5 <= countNeighbours(myMap, x + 1 + k, y) <= 6:
                    sideFalse = True
            if not sideFalse:
                for k in range(7):
                    myMap[x + 1 + k][y].char = '='
                    myMap[x + 1 + k][y].fg = colors.dark_sepia
                    myMap[x + 1 + k][y].bg = colors.sepia
        if side != 'above':
            sideFalse = False
            for k in range(7):
                if not 5 <= countNeighbours(myMap, x + 1 + k, y + 8) <= 6:
                    sideFalse = True
            if not sideFalse:
                for k in range(7):
                    myMap[x + 1 + k][y + 8].char = '='
                    myMap[x + 1 + k][y + 8].fg = colors.dark_sepia
                    myMap[x + 1 + k][y + 8].bg = colors.sepia
        print("created secret room at x ", entryX, " y ", entryY, " in quarter ", quarter)
                
def checkMap():
    global myMap
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if myMap[x][y].hole and not myMap[x][y].indestructible:
                myMap[x][y].blocked = False
    
def makeMap():
    global myMap, rooms, firstX, firstY, lastX, lastY

    myMap = [[Tile(blocked = True, x = x, y = y) for y in range(MAP_HEIGHT)]for x in range(MAP_WIDTH)] #Creates a rectangle of blocking tiles from the Tile class, aka walls. Each tile is accessed by myMap[x][y], where x and y are the coordinates of the tile.
    rooms = []
    numberRooms = 0
    
    for x in range(MAP_WIDTH):
        myMap[x][0].setIndestructible()
        myMap[x][MAP_HEIGHT - 1].setIndestructible()
    for y in range(MAP_HEIGHT):
        myMap[0][y].setIndestructible()
        myMap[MAP_WIDTH - 1][y].setIndestructible()
 
    for r in range(30):
        w = randint(10, 16)
        h = randint(10, 16)
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
                bigTunnel = randint(0, 4)
                big = bigTunnel == 0
                if randint(0, 1):
                    createHorizontalTunnel(previous_x, new_x, previous_y, big)
                    createVerticalTunnel(previous_y, new_y, new_x, big)
                else:
                    createVerticalTunnel(previous_y, new_y, previous_x, big)
                    createHorizontalTunnel(previous_x, new_x, new_y, big)
            else:
                firstX, firstY = new_x, new_y
            rooms.append(newRoom)
            numberRooms += 1
    lastX, lastY = new_x, new_y
    
    baseMap = list(deepcopy(myMap))
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            '''
            if countNeighbours(myMap, x, y) == 7:
                myMap[x][y].pillar = True
                myMap[x][y].char = 'O'
            '''
            if 0 <= countNeighbours(myMap, x, y) <= 2 and not myMap[x][y].pillar and not (x == 0 or x == MAP_WIDTH - 1 or y == 0 or y == MAP_HEIGHT - 1):
                if myMap[x][y].blocked:
                    #baseMap[x][y].bg = colors.red
                    baseMap[x][y].blocked = False
                    baseMap[x][y].char = None
            if countNeighbours(myMap, x, y) == 3 and not myMap[x][y].pillar and not (x == 0 or x == MAP_WIDTH - 1 or y == 0 or y == MAP_HEIGHT - 1):
                if myMap[x][y].blocked:
                    baseMap[x][y].pillar = True
                    baseMap[x][y].blocked = True
                    baseMap[x][y].char = 'o'
    myMap = baseMap
    secretRoom()
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if myMap[x][y].pillar:
                if (x, y) == (lastX, lastY) or (x, y) == (firstX, firstY):
                    myMap[x][y].blocked = False
                    myMap[x][y].pillar = False
    #checkMap()

myMap = [[]]

def update(mapToUse):
    root.clear()
    try:
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                root.draw_char(x, y, char = mapToUse[x][y].char, fg = mapToUse[x][y].fg, bg = mapToUse[x][y].bg)
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
                
