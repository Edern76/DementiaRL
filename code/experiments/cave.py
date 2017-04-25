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
reachableRooms = []
unreachableRooms = []
dispEmpty = False
dispDebug = True
state = "base"

curRoomIndex = 0

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
    
    def returnOtherOwners(self, base):
        newList = list(self.belongsTo)
        newList.remove(base)
        return newList

        
class Room:
    def __init__(self, tiles, borders = []):
        self.tiles = tiles
        self.borders = borders
        rooms.append(self)
        self.contestedTiles = []
        self.collidingRooms = []
        self.connectedRooms = []
        self.protect = False
        self.mainRoom = False
        self.reachableFromMainRoom = False
        
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
            
    def mergeWith(self, other, arbitraryTiles = []):
        self.protect = True
        if not other.protect:
            if self in self.collidingRooms:
                self.collidingRooms.remove(self)
                print("REMOVED SELF FROM COLLROOMS")
            for (x,y) in other.tiles:
                if not (x,y) in self.tiles:
                    self.tiles.append((x,y))
    
            for (x,y) in arbitraryTiles:
                if not (x,y) in self.tiles:
                    self.tiles.append((x,y))
            
            for (x,y) in other.borders:
                if not (x,y) in self.borders:
                    self.borders.append((x,y))
    
            if other in rooms:
                rooms.remove(other)
            else:
                print("Other room not in rooms")
            if other in self.collidingRooms:
                self.collidingRooms.remove(other)
            else:
                print("Other room not in colliding rooms")
            del other
        else:
            print("OTHER ROOM IS FUCKING PROTECTED, DO NOT MERGE")
            
    def setReachable(self):
        if not self.reachableFromMainRoom:
            self.reachableFromMainRoom = True
            for room in self.connectedRooms:
                room.setReachable()
        
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

def updateReachLists():
    global reachableRooms, unreachableRooms
    reachableRooms = []
    unreachableRooms = []
    for room in rooms:
        if room.reachableFromMainRoom and not room in reachableRooms:
            reachableRooms.append(room)
        else:
            if room not in unreachableRooms:
                unreachableRooms.append(room)

def connectRooms(roomList, forceAccess = False):
    roomListA = []
    roomListB = []
    
    if forceAccess:
        '''
        for room in rooms:
            if room.reachableFromMainRoom:
                roomListB.append(room)
            else:
                roomListA.append(room)
        '''
        roomListB = list(reachableRooms)
        roomListA = list(unreachableRooms)
    else:
        roomListA = list(rooms)
        roomListB = list(rooms)
    
    bestDistance = 0
    if not forceAccess:
        for roomA in roomListA:
            possibleConnectionFound = False
            if (roomA.connectedRooms and not forceAccess):
                continue
            for roomB in roomListB:
                if roomA == roomB or roomB in roomA.connectedRooms:
                    continue
                else:
                    for tileIndexA in range(0, len(roomA.borders) - 1):
                        for tileIndexB in range(0, len(roomB.borders) - 1):
                            (xA, yA) = roomA.borders[tileIndexA]
                            (xB, yB) = roomB.borders[tileIndexB]
                        distance = (xA - xB)**2 + (yA - yB)**2
                        
                        if distance < bestDistance or not possibleConnectionFound:
                            bestDistance = int(distance)
                            possibleConnectionFound = True
                            bestTileA = (int(xA), int(yA))
                            bestTileB = (int(xB), int(yB))
                            bestRoomA = roomA
                            bestRoomB = roomB
                        
            if possibleConnectionFound:
                createPassage(bestRoomA, bestRoomB, bestTileA, bestTileB)
    else:
        updateReachLists()
        while unreachableRooms:
            roomA = unreachableRooms[0]
            possibleConnectionFound = False
            reachIndex = 0
            print(reachIndex)
            if len(unreachableRooms) == 1:
                print("BREAKING")
                break
            else:
                print(len(unreachableRooms))
            for roomB in reachableRooms:
                if roomA == roomB or roomB in roomA.connectedRooms or len(roomB.connectedRooms) > 1:
                    continue
                else:
                    bestDistance = 0
                    bestRoomA = roomA
                    for tileIndexA in range(0, len(roomA.borders) - 1):
                        for tileIndexB in range(0, len(roomB.borders) - 1):
                            (xA, yA) = roomA.borders[tileIndexA]
                            (xB, yB) = roomB.borders[tileIndexB]
                        distance = (xA - xB)**2 + (yA - yB)**2
                        
                        if distance < bestDistance or not possibleConnectionFound:
                            bestDistance = int(distance)
                            possibleConnectionFound = True
                            bestTileA = (int(xA), int(yA))
                            bestTileB = (int(xB), int(yB))
                            bestRoomB = roomB
                        
            if possibleConnectionFound:
                createPassage(bestRoomA, bestRoomB, bestTileA, bestTileB)
                updateReachLists()
                reachIndex = 0
            else:
                reachIndex += 1
                updateReachLists()
            
        if len(unreachableRooms) == 1:
            updateReachLists()
            roomA = unreachableRooms[0]
            possibleConnectionFound = False
            for roomB in reachableRooms:
                if roomA == roomB or roomB in roomA.connectedRooms:
                    print("CONTIUNING")
                    continue
                else:
                    bestDistance = 0
                    bestRoomA = roomA
                    for tileIndexA in range(0, len(roomA.borders) - 1):
                        for tileIndexB in range(0, len(roomB.borders) - 1):
                            (xA, yA) = roomA.borders[tileIndexA]
                            (xB, yB) = roomB.borders[tileIndexB]
                        distance = (xA - xB)**2 + (yA - yB)**2
                        
                        if distance < bestDistance or not possibleConnectionFound:
                            bestDistance = int(distance)
                            possibleConnectionFound = True
                            bestTileA = (int(xA), int(yA))
                            bestTileB = (int(xB), int(yB))
                            bestRoomB = roomB
                    if possibleConnectionFound:
                        createPassage(bestRoomA, bestRoomB, bestTileA, bestTileB)
                        updateReachLists()
                        reachIndex = 0
                        update(mapToFuckingUse)

def linkRooms(room1, room2):
    room1.connectedRooms.append(room2)
    room2.connectedRooms.append(room1)
    
    if room1.reachableFromMainRoom:
        room2.setReachable()
    if room2.reachableFromMainRoom:
        room1.setReachable()

def createPassage(roomA, roomB, tileA, tileB):
    '''
    if not roomB in roomA.connectedRooms:
        #roomA.connectedRooms.append(roomB)
        linkRooms(roomA, roomB)
    if not roomA in roomB.connectedRooms:
        #roomB.connectedRooms.append(roomA)
        linkRooms(roomB, roomA)
    '''
    linkRooms(roomA, roomB)
    
    (xA, yA) = tileA
    (xB, yB) = tileB
    
    passage = tdl.map.bresenham(xA, yA, xB, yB)
    for (x,y) in passage:
        openTile(x,y,myMap)
                
    
    
    
def generateMap():
    global myMap, baseMap, mapToDisp, maps, visuTiles, state, visuEdges, confTiles, rooms, curRoomIndex
    myMap = [[Tile(False) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]
    visuTiles = []
    visuEdges = []
    confTiles = []
    curRoomIndex = 0
    curRoomIndex = 0
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
            #visuEdges.extend(room.borders)
            confTiles.extend(room.contestedTiles)
            update(mapToFuckingUse)
        state = "roomMergePrep"
        update(mapToFuckingUse)
        refreshEmptyTiles()
        tdl.event.key_wait()
        tempRooms = list(rooms)
        while tempRooms:
            for rum in tempRooms:
                if rum not in rooms:
                    tempRooms.remove(rum)
            room = tempRooms[0]
            oldRoomBorders = []
            if room.contestedTiles:
                for (x,y) in room.contestedTiles:
                    openTile(x,y, myMap)
                    if (x,y) in visuEdges:
                        visuEdges.remove((x,y))
                    for owner in myMap[x][y].belongsTo:
                        oldRoomBorders.append((x,y))
                        owner.borders.remove((x,y))
                        room.mergeWith(owner, oldRoomBorders)
            tempRooms.remove(room)
        
        rooms[0].mainRoom = True
        rooms[0].reachableFromMainRoom = True
        
        connectRooms(rooms)
        connectRooms(rooms, True)
        state = "normal"
        update(mapToFuckingUse)
        
        
    
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
        if state in ("floodfillPrep", "edgeDetectionPrep", "roomMergePrep"):
            drawCentered(root, 70, "Ready to continue, press a key to proceed...", fg = colors.green)
        elif state == "floodfill":
            drawCentered(root, 70, "Filling...", fg = colors.green)
        elif state == "normal":
            drawCentered(root, 70, "Done ! Press ENTER to restart or SPACE to toggle between map and canvas. ", fg = colors.green)
            for (x,y) in rooms[curRoomIndex].tiles:
                root.draw_char(x, y, None, bg = colors.yellow)
            for (x,y) in rooms[curRoomIndex].borders:
                root.draw_char(x, y, "#", fg = colors.orange)
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
        global curRoomIndex
        curRoomIndex = 0
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
                
