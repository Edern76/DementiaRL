import tdl, colors, copy, pdb, traceback, os, sys, time
from random import *
from code.custom_except import *

WIDTH, HEIGHT, LIMIT = 150, 80, 20
MAP_WIDTH, MAP_HEIGHT = 140, 60
MID_MAP_WIDTH, MID_MAP_HEIGHT = MAP_WIDTH//2, MAP_HEIGHT//2
MID_WIDTH, MID_HEIGHT = int(WIDTH/2), int(HEIGHT/2)

CHANCE_TO_START_ALIVE = 55
DEATH_LIMIT = 3
BIRTH_LIMIT = 4
STEPS_NUMBER = 10
myMap = [[]]

if __name__ == '__main__':
    root = tdl.init(150, 80, 'Dementia')

class Tile:
    def __init__(self, blocked, bg, fg, char = None):
        self.blocked = blocked
        self.unbreakable = False
        self.leaves = True
        self.fg = fg
        self.bg = bg
        self.char = char

def createLeaves(mapToUse):
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if randint(0, 100) < CHANCE_TO_START_ALIVE:
                mapToUse[x][y].leaves = False
    for loop in range(STEPS_NUMBER):
        mapToUse = doStep(mapToUse)
    
    return mapToUse

def countNeighbours(mapToUse, startX, startY):
    count = 0
    for x in range(-1, 2):
        for y in range(-1, 2):
            if x == 0 and y == 0:
                continue
            else:
                otherX = startX + x
                otherY = startY + y
                if not mapToUse[otherX][otherY].leaves:
                    count += 1
    return count

def doStep(oldMap):
    newMap = list(copy.deepcopy(oldMap))
    for x in range(1, MAP_WIDTH - 1):
        for y in range(1, MAP_HEIGHT - 1):
            neighbours = countNeighbours(oldMap, x, y)
            if not oldMap[x][y].leaves:
                if neighbours < DEATH_LIMIT:
                    newMap[x][y].leaves = True
                else:
                    newMap[x][y].leaves = False
            else:
                if neighbours > BIRTH_LIMIT:
                    newMap[x][y].leaves = False
                else:
                    newMap[x][y].leaves = True
    return newMap

def checkMap():
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if myMap[x][y].leaves:
                myMap[x][y].char = '#'
                myMap[x][y].bg = colors.darkest_green
                myMap[x][y].fg = colors.dark_green
            else:
                myMap[x][y].char = None
                myMap[x][y].bg = colors.darker_green
                myMap[x][y].fg = colors.green

def makeMap():
    global myMap
    myMap = [[Tile(False, bg = colors.darker_green, fg = colors.darker_chartreuse) for y in range(MAP_HEIGHT)]for x in range(MAP_WIDTH)] #Creates a rectangle of blocking tiles from the Tile class, aka walls. Each tile is accessed by myMap[x][y], where x and y are the coordinates of the tile.
    myMap = createLeaves(myMap)
    checkMap()

makeMap()
while not tdl.event.is_window_closed():
    root.clear()
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            root.draw_char(x, y, myMap[x][y].char, myMap[x][y].fg, myMap[x][y].bg)
    tdl.flush()






