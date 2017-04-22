import tdl, colors, copy, pdb, traceback, os, sys, time
from random import *
from colors import darker_sepia
from custom_except import *

WIDTH, HEIGHT, LIMIT = 150, 80, 20
MAP_WIDTH, MAP_HEIGHT = 140, 60
MID_MAP_WIDTH, MID_MAP_HEIGHT = MAP_WIDTH//2, MAP_HEIGHT//2
MID_WIDTH, MID_HEIGHT = int(WIDTH/2), int(HEIGHT/2)

CHANCE_TO_START_ALIVE = 55
DEATH_LIMIT = 3
BIRTH_LIMIT = 4
STEPS_NUMBER = 2
MIN_ROOM_SIZE = 6

emptyTiles = [] #List of tuples of the coordinates of emptytiles not yet processed by the floodfill algorithm
rooms = []
visuTiles = []
visuEdges = []
confTiles = []
dispEmpty = False
dispDebug = True
state = "base"

sys.setrecursionlimit(3000)

if __name__ == '__main__':
    root = tdl.init(WIDTH, HEIGHT, 'Dementia')
    
class Tile:
    def __init__(self, blocked):
        self.blocked = blocked
        self.indestructible = False
        self.belongsTo = []
        
    def setIndestructible(self):
        self.blocked = True
        self.indestructible = True
        
    def open(self):
        if not self.indestructible:
            self.blocked = False
            return True
        else:
            return False
    
    def close(self):
        if not self.blocked:
            self.blocked = True
    
    def addOwner(self, toAdd):
        if not toAdd in self.belongsTo:
            if self.belongsTo:
                otherOwners = list(self.belongsTo)
            else:
                otherOwners = []
            self.belongsTo.append(toAdd)
            print(otherOwners)
            return otherOwners

        
class Room:
    def __init__(self, tiles, borders = []):
        self.tiles = tiles
        self.borders = borders
        rooms.append(self)
        self.contestedTiles = []
        self.collidingRooms = []
        
    def remove(self):
        for (x,y) in self.tiles:
            closeTile(x, y, myMap)
        rooms.remove(self)
        del self
        
    def claimTile(self, x, y):
        if (x,y) in self.tiles or (x,y) in self.borders:
            conflict = myMap[x][y].addOwner(self)
            if conflict:
                print("CONFLICT")
                self.contestedTiles.append((x,y))
                for contester in conflict:
                    if not contester in self.collidingRooms:
                        self.collidingRooms.append(contester)
        else:
            raise IllegalTileInvasion("At {} {}".format(x, y))
        
    def claimBorders(self):
        for (x, y) in self.borders:
            self.claimTile(x, y)
        
def floodFill(x, y, listToAppend, edgeList):
    print("{},{}".format(x, y))
    if not myMap[x][y].blocked:
        if (x,y) in emptyTiles:
            removeFromEmptyTiles(x,y)
            listToAppend.append((x,y))
            visuTiles.append((x,y))
            floodFill(x+1, y, listToAppend, edgeList)
            floodFill(x-1, y, listToAppend, edgeList)
            floodFill(x, y+1, listToAppend, edgeList)
            floodFill(x, y-1, listToAppend, edgeList)
        else:
            return
    else:
        
        edgeList.append((x,y))
        return
    

    
    

myMap = [[]]
baseMap = [[]]


maps = [myMap, baseMap]
mapIndex = 0

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
                if mapToUse[otherX][otherY].blocked:
                    count += 1
                    found = True
                    if stopAtFirst:
                        break
        if stopAtFirst and found:
            break
    return count

def drawCentered(cons = root , y = 1, text = "Lorem Ipsum", fg = None, bg = None):
    xCentered = (WIDTH - len(text))//2
    cons.draw_str(xCentered, y, text, fg, bg)

def removeFromEmptyTiles(x, y):
    if (x,y) in emptyTiles:
        emptyTiles.remove((x,y))

def openTile(x, y, mapToUse):
    if mapToUse[x][y].open() and not (x,y) in emptyTiles:
        #emptyTiles.append((x,y))
        pass

def closeTile(x, y, mapToUse):
    mapToUse[x][y].close()
    #removeFromEmptyTiles(x,y)
    
def refreshEmptyTiles():
    global emptyTiles
    emptyTiles = []
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if not myMap[x][y].blocked:
                emptyTiles.append((x,y))

def doStep(oldMap):
    newMap = list(copy.deepcopy(baseMap))
    for x in range(1, MAP_WIDTH - 1):
        for y in range(1, MAP_HEIGHT - 1):
            neighbours = countNeighbours(oldMap, x, y)
            if oldMap[x][y].blocked:
                if neighbours < DEATH_LIMIT:
                    openTile(x, y, newMap)
                else:
                    closeTile(x, y, newMap)
                    print('Blocking')
            else:
                if neighbours > BIRTH_LIMIT:
                    closeTile(x, y, newMap)
                    print('Blocking')
                else:
                    openTile(x, y, newMap)
    return newMap

def generateMap():
    global myMap, baseMap, mapToDisp, maps, visuTiles, state, visuEdges, confTiles, rooms
    myMap = [[Tile(False) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]
    visuTiles = []
    visuEdges = []
    confTiles = []
    rooms = []
    for x in range(MAP_WIDTH):
        myMap[x][0].setIndestructible()
        removeFromEmptyTiles(x,0)
        myMap[x][MAP_HEIGHT - 1].setIndestructible()
        removeFromEmptyTiles(x, MAP_HEIGHT - 1)
        for y in range(MAP_HEIGHT):
            if not myMap[x][y].blocked and not (x,y) in emptyTiles:
                emptyTiles.append((x,y))
    for y in range(MAP_HEIGHT):
        myMap[0][y].setIndestructible()
        removeFromEmptyTiles(0, y)
        myMap[MAP_WIDTH - 1][y].setIndestructible()
        removeFromEmptyTiles(MAP_WIDTH - 1, y)

    baseMap = list(copy.deepcopy(myMap))


    if baseMap[2][5].blocked:
        print("WTTTTTTTTTTTTTTTTTTFFFFFFFFFF")
        print(myMap[2][5].blocked)
    else:
        print("Everything is worked as intended in this part of the code")
        
    for x in range(1, MAP_WIDTH - 1):
        for y in range(1, MAP_HEIGHT - 1):
            if randint(0, 100) < CHANCE_TO_START_ALIVE:
                closeTile(x, y, myMap)

    if baseMap[2][5].blocked:
        print("WTTTTTTTTTTTTTTTTTTFFFFFFFFFF")
        print(myMap[2][5].blocked)
    else:
        print("Everything is worked as intended in this part of the code")
    for loop in range(STEPS_NUMBER):
        myMap = doStep(myMap)
    maps = [myMap, baseMap]
    mapToFuckingUse = maps[mapIndex]
    refreshEmptyTiles()
    update(mapToFuckingUse)
    print("Freezing")
    state = "floodfillPrep"
    update(mapToFuckingUse)
    tdl.event.key_wait()
    if not tdl.event.is_window_closed():
        print("Continuing")
        state = "floodfill"
        while emptyTiles:
            (x,y) = emptyTiles[0]
            #time.sleep(0.05)
            newRoomTiles = []
            newRoomEdges = []
            try:
                floodFill(x,y, newRoomTiles, newRoomEdges)
            except RecursionError:
                traceback.print_exc()
                print(sys.getrecursionlimit())
                os._exit(-1)
            newRoom = Room(newRoomTiles, borders = newRoomEdges)
            if len(newRoom.tiles) < MIN_ROOM_SIZE:
                newRoom.remove()
            else:
                '''
                newRoomEdges = []
                for (x,y) in newRoom.tiles:
                    if countNeighbours(myMap, x, y, stopAtFirst = True) > 0:
                        newRoomEdges.append((x,y))
                newRoom.borders = list(newRoomEdges)
                '''
                #visuEdges.extend(newRoom.borders)
                pass
                        
            update(mapToFuckingUse)
        for room in rooms:
            room.claimBorders()
            visuEdges.extend(room.borders)
            confTiles.extend(room.contestedTiles)
            update(mapToFuckingUse)
        state = "normal"
        refreshEmptyTiles()
        
    
def update(mapToUse):
    root.clear()
    try:
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if mapToUse[x][y].blocked:
                    root.draw_char(x, y, char = '#', fg = colors.lighter_gray)
                    if visuEdges and (x,y) in visuEdges and (state != 'normal' or dispDebug):
                        root.draw_char(x,y, char='#', fg = colors.purple)
                    if confTiles and (x,y) in confTiles and (state != 'normal' or dispDebug):
                        root.draw_char(x,y, char='#', fg = colors.red)
                else:
                    root.draw_char(x, y, char = None, bg = colors.dark_sepia)
                    if visuTiles and (x,y) in visuTiles and (state != 'normal' or dispDebug):
                        root.draw_char(x,y, char=None, bg = colors.red)
                    if visuEdges and (x,y) in visuEdges and (state != 'normal' or dispDebug):
                        root.draw_char(x,y, char=None, bg = colors.purple)
                    
        if dispEmpty:
            for (x,y) in emptyTiles:
                root.draw_char(x, y, char= ".", bg = colors.cyan)
            print(len(emptyTiles))
        if state in ("floodfillPrep", "edgeDetectionPrep"):
            drawCentered(root, 70, "Ready to continue, press a key to proceed...", fg = colors.green)
        elif state == "floodfill":
            drawCentered(root, 70, "Filling...", fg = colors.green)
        elif state == "normal":
            drawCentered(root, 70, "Done ! Press ENTER to restart or SPACE to toggle between map and canvas. ", fg = colors.green)
        elif state == "base":
            drawCentered(root, 70, "Loading...", fg = colors.gray)
    except IndexError:
        traceback.print_exc()
        #pdb.set_trace()
        os._exit(-1)
        
    tdl.flush()
    
def getInput():
    global mapIndex
    key = tdl.event.key_wait()
    actualKey = key.keychar.upper()
    if actualKey == 'ENTER':
        generateMap()
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
    
    
if __name__ == '__main__':
    generateMap()
    while not tdl.event.is_window_closed():
        print(mapIndex)
        mapToFuckingUse = maps[mapIndex]
        '''
        print(mapToFuckingUse)
        print("DONE")
        input()
        print(maps[mapIndex])
        print("REDONE")
        input()
        print(myMap)
        input()
        print("NOW IMA CRASH")
        '''
        
        update(mapToFuckingUse)
        input = getInput()
                
