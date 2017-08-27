import colors, copy, pdb, traceback, os, sys, time, math
from random import *
from code.custom_except import *
import tdlib as tdl
from code.classes import Tile

myMap = []
WIDTH, HEIGHT, LIMIT = 150, 80, 20
MAP_WIDTH, MAP_HEIGHT = 280, 120
if __name__ == '__main__':
    root = tdl.init(WIDTH, HEIGHT, 'Dementia')

#probabilities that a baby Roomie will be born after i generations (i <=10)
#must get up to 100
#i =  0  1   2   3  4  5  6  7  8  9  10
BR = [0, 0, 50, 50, 0, 0, 0, 0, 0, 0, 0]

#probabilities that a baby Tunneler will be born after i generations
#(applicable only for those Tunnelers who are not larger than their parents -
# - for those larger than their parents, use sizeUpGenDelay)
#i =  0  1   2   3  4  5  6  7  8  9  10
BT = [0, 0, 100, 0, 0, 0, 0, 0, 0, 0, 0]

#probabilities that a baby Tunneler of generation gen will have a tunnelWidth 1 size larger than its parent
#-1 in order to repeat last value
#i <= 20
#i =  0  1   2   3  4  5  6  7  8  9  10
ZU = [0, 0, 0, 0, 0, 100, 100, 30, -1]
#prob 1 size smaller
ZD = [0, 0, 50, 100, 100, 0, 0, 70, -1]
#for every generation, 100 - (sizeUpProb(gen) + sizeDownProb(gen) = probability that size remains the same

#probability that a Tunneler will make an anteroom when changing direction or spawning, depending on tunnel width
#100 to end and repeat 0
#tunWid =  0  1  2  3  4  5  6  7  8  9  10
F = [20, 30, 0, 0, 100]

#probabilities to use a room of a certain size depending on tunnelWidth
#the first line is for rooms coming out sideways from the tunnel, the second for rooms at branching sites
#ends when large is 100, and repeats (0, 0, 100)
#tW = 0 (small, medium, large) etc
GS = [(100, 0, 0), (50, 50, 0), (0, 100, 0), (0, 0, 100)]
GB = [(100, 0, 0), (0, 100, 0), (0, 0, 100)]

#maxAge for generations of Tunneler, end with 0 to repeat last value, per generation
#gen <= 30
AT = [5, 12, 12, 15, 15, 15, 15, 15, 15, 20, 30, 10, 15, 10, 3, 20, 10, 5, 15, 10, 5, 20, 20, 20, 20, 10, 20, 5, 20, 5, 0]

#roomAspectRatio <= length/width and width/length of rooms must be larger than this
roomAspectRation = 0.4

#mutator changes Tunneler parameters between generations, less change with smaller mutator
mutator = 20

class Tunneler:
    def __init__(self, x, y, direction, intendedDir, maxAge = 12, gen = 0, tunWid = 1, stepLen = 3, straightSpawnProb = 40, turnSpawnProb = 50,
                 changeDirProb = 40, rightRoomProb = 100, leftRoomProb = 100, joinProb = 100):
        #joinProbability, high values make this Tunneler prefer to join another tunnel or open space,
        #with low values it prefers to end its run by building a room
        self.x = x
        self.y = y
        self.direction = direction
        self.intendedDir = intendedDir
        self.maxAge = maxAge
        self.gen = gen
        self.tunWid = tunWid
        self.steplen = stepLen
        self.straightSpawnProb = straightSpawnProb
        self.turnSpawnProb = turnSpawnProb
        self.changeDirProb = changeDirProb
        self.rightRoomProb = rightRoomProb
        self.leftRoomProb = leftRoomProb
        self.joinProb = joinProb

    #def run(self):
        


def run():
    global myMap
    myMap = [[Tile(True, x, y) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]
    
    

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
    run()
    while not tdl.event.is_window_closed():
        update()