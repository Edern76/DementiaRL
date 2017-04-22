import tdl, colors, copy, pdb, traceback, os
from random import *
from colors import darker_sepia

WIDTH, HEIGHT, LIMIT = 150, 80, 20
MAP_WIDTH, MAP_HEIGHT = 140, 60
MID_MAP_WIDTH, MID_MAP_HEIGHT = MAP_WIDTH//2, MAP_HEIGHT//2
MID_WIDTH, MID_HEIGHT = int(WIDTH/2), int(HEIGHT/2)

CHANCE_TO_START_ALIVE = 55
DEATH_LIMIT = 3
BIRTH_LIMIT = 4
STEPS_NUMBER = 2

tilesFFed = [] #List of tuples of the coordinates of tiles already processed by the floodfill algorithm

if __name__ == '__main__':
    root = tdl.init(WIDTH, HEIGHT, 'Dementia')
    
class Tile:
    def __init__(self, blocked):
        self.blocked = blocked
        self.indestructible = False
        
    def setIndestructible(self):
        self.blocked = True
        self.indestructible = True


myMap = [[]]
baseMap = [[]]

maps = [myMap, baseMap]
mapIndex = 0

def countNeighbours(mapToUse, startX, startY):
    count = 0
    for x in range(-1, 2):
        for y in range(-1, 2):
            if x == 0 and y == 0:
                continue
            else:
                otherX = startX + x
                otherY = startY + y
                if mapToUse[otherX][otherY].blocked:
                    count += 1
    return count
            

def doStep(oldMap):
    newMap = list(copy.deepcopy(baseMap))
    for x in range(1, MAP_WIDTH - 1):
        for y in range(1, MAP_HEIGHT - 1):
            neighbours = countNeighbours(oldMap, x, y)
            if oldMap[x][y].blocked:
                if neighbours < DEATH_LIMIT:
                    newMap[x][y].blocked = False
                else:
                    newMap[x][y].blocked = True
                    print('Blocking')
            else:
                if neighbours > BIRTH_LIMIT:
                    newMap[x][y].blocked = True
                    print('Blocking')
                else:
                    newMap[x][y].blocked = False
    return newMap

def generateMap():
    global myMap, baseMap, mapToDisp, maps
    myMap = [[Tile(False) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]
    for x in range(MAP_WIDTH):
        myMap[x][0].setIndestructible()
        myMap[x][MAP_HEIGHT - 1].setIndestructible()
    for y in range(MAP_HEIGHT):
        myMap[0][y].setIndestructible()
        myMap[MAP_WIDTH - 1][y].setIndestructible()

    baseMap = list(copy.deepcopy(myMap))


    if baseMap[2][5].blocked:
        print("WTTTTTTTTTTTTTTTTTTFFFFFFFFFF")
        print(myMap[2][5].blocked)
    else:
        print("Everything is worked as intended in this part of the code")
        
    for x in range(1, MAP_WIDTH - 1):
        for y in range(1, MAP_HEIGHT - 1):
            if randint(0, 100) < CHANCE_TO_START_ALIVE:
                myMap[x][y].blocked = True

    if baseMap[2][5].blocked:
        print("WTTTTTTTTTTTTTTTTTTFFFFFFFFFF")
        print(myMap[2][5].blocked)
    else:
        print("Everything is worked as intended in this part of the code")
    for loop in range(STEPS_NUMBER):
        myMap = doStep(myMap)
    maps = [myMap, baseMap]
    
def update(mapToUse):
    root.clear()
    try:
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if mapToUse[x][y].blocked:
                    root.draw_char(x, y, char = '#', fg = colors.lighter_gray)
                else:
                    root.draw_char(x, y, char = None, bg = colors.dark_sepia)
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
                
