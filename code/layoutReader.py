import colors, math, textwrap, time, os, sys, code, gzip, pathlib, traceback, ffmpy, pdb, copy, queue, random, cProfile, main #Code is not unused. Importing it allows us to import the rest of our custom modules in the code package.
import tdlib as tdl
import threading, multiprocessing
import dill #THIS IS NOT AN UNUSED IMPORT. Importing this changes the behavior of the pickle module (and the shelve module too), so as we can actually save lambda expressions. EDIT : It might actually be useless to import it here, since we import it in the dilledShelve module, but it freaking finally works perfectly fine so we're not touching this.
from tdl import *
from random import randint, choice
from math import *
from code.custom_except import *
from copy import copy, deepcopy
from os import makedirs
from queue import *
from multiprocessing import freeze_support, current_process


color_light_wall = colors.white
color_dark_wall = colors.grey
color_light_ground = colors.black
color_dark_ground = colors.black
color_light_gravel = colors.white
color_dark_gravel = colors.grey



def printTileWhenWalked(tile):
    print("Player walked on tile at {};{}".format(tile.x, tile.y))

'''
class Tile:
    def __init__(self, blocked, x, y, block_sight = None, acid = False, acidCooldown = 5, character = None, fg = None, bg = None, dark_fg = None, dark_bg = None, chasm = False, wall = False, hole = False, leaves = False, moveCost = 1):
        self.blocked = blocked
        self.explored = False
        self.unbreakable = False
        self.character = character
        self.fg = fg
        self.FG = fg
        self.bg = bg
        self.BG = bg
        self.dark_fg = dark_fg
        self.DARK_FG = dark_fg
        self.dark_bg = dark_bg
        self.DARK_BG = dark_bg
        self.wall = wall
        self.chasm = chasm
        self.hole = hole
        self.x = x
        self.y = y
        self.secretWall = False
        self.pillar = False
        if block_sight is None:
            block_sight = blocked
            self.block_sight = block_sight
        else:
            self.block_sight = block_sight
        self.acid = acid
        self.baseAcidCooldown = acidCooldown
        self.curAcidCooldown = 0
        self.belongsTo = []
        self.usedForPassage = False
        if self.wall:
            self.character = '#'
            self.FG = color_light_wall
            self.fg = color_light_wall
            self.BG = color_light_ground
            self.bg = color_light_ground
            self.DARK_FG = color_dark_wall
            self.dark_fg = color_dark_wall
            self.DARK_BG = color_dark_ground
            self.dark_bg = color_dark_ground
        if self.chasm:
            self.character = None
            self.FG = colors.black
            self.fg = colors.black
            self.BG = (0, 0, 16)
            self.bg = (0, 0, 16)
            self.DARK_FG = colors.black
            self.dark_fg = colors.black
            self.DARK_BG = (0, 0, 16)
            self.dark_bg = (0, 0, 16)
        self.moveCost = moveCost
        self.djikValue = None
        self.doNotPropagateDjik = False
        self.onTriggerFunction = printTileWhenWalked
        self.leaves = leaves
        
    def neighbors(self):
        x = self.x
        y = self.y
        try:
            upperLeft = main.myMap[x - 1][y - 1]
        except IndexError:
            upperLeft = None
            
        try:
            up = main.myMap[x][y - 1]
        except IndexError:
            up = None
            
        try:
            upperRight = main.myMap[x + 1][y - 1]
        except IndexError:
            upperRight = None
            
        try:
            left = main.myMap[x - 1][y]
        except IndexError:
            left = None
            
        try:
            right = main.myMap[x + 1][y]
        except IndexError:
            right = None
            
        try:
            lowerLeft = main.myMap[x - 1][y + 1]
        except IndexError:
            lowerLeft = None
        
        try:
            low = main.myMap[x][y + 1]
        except IndexError:
            low = None

        try:
            lowerRight = main.myMap[x + 1][y + 1]
        except IndexError:
            lowerRight = None
        
        return [i for i in [upperLeft, up, upperRight, left, right, lowerLeft, low, lowerRight] if i is not None]
    
    def neighbours(self):
        result = self.neighbors()
        return result
    
    def cardinalNeighbors(self):
        x = self.x
        y = self.y
        try:
            up = main.myMap[x][y - 1]
        except IndexError:
            up = None
        try:
            left = main.myMap[x - 1][y]
        except IndexError:
            left = None
        try:
            right = main.myMap[x + 1][y]
        except IndexError:
            right = None
        try:
            low = main.myMap[x][y + 1]
        except IndexError:
            low = None
        return [i for i in [up, left, right, low] if i is not None]
    
    def cardinalNeighbours(self):
        result = self.cardinalNeighbors()
        return result

    def applyWallProperties(self):
        if not self.secretWall:
            self.wall = True
            self.character = '#'
            self.FG = color_light_wall
            self.fg = color_light_wall
            self.BG = color_light_ground
            self.bg = color_light_ground
            self.DARK_FG = color_dark_wall
            self.dark_fg = color_dark_wall
            self.DARK_BG = color_dark_ground
            self.dark_bg = color_dark_ground
    
    def applyChasmProperties(self):
        if not self.secretWall:
            self.chasm = True
            self.character = None
            self.FG = colors.black
            self.fg = colors.black
            self.BG = (0, 0, 16)
            self.bg = (0, 0, 16)
            self.DARK_FG = colors.black
            self.dark_fg = colors.black
            self.DARK_BG = (0, 0, 16)
            self.dark_bg = (0, 0, 16)
    
    def applyGroundProperties(self, explode = False, temple = False):
        if temple:
            gravelChar1 = chr(250)
            gravelChar2 = chr(254)
        else:
            gravelChar1 = chr(177)
            gravelChar2 = chr(176)
        if explode:
            if not self.chasm or self.wall:
                gravelChoice = randint(0, 5)
                self.blocked = False
                self.block_sight = False
                if gravelChoice == 0:
                    self.character = gravelChar1
                elif gravelChoice == 1:
                    self.character = gravelChar2
                else:
                    self.character = None
                self.fg = color_light_gravel
                self.bg = color_light_ground
                self.dark_fg = color_dark_gravel
                self.dark_bg = color_dark_ground
                self.wall = False
                self.chasm = False
        else:
            if not self.secretWall or self.pillar:
                gravelChoice = randint(0, 5)
                self.blocked = False
                self.block_sight = False
                if gravelChoice == 0:
                    self.character = gravelChar1
                elif gravelChoice == 1:
                    self.character = gravelChar2
                else:
                    self.character = None
                self.fg = color_light_gravel
                self.bg = color_light_ground
                self.dark_fg = color_dark_gravel
                self.dark_bg = color_dark_ground
                self.wall = False
    
    def setUnbreakable(self):
        self.blocked = True
        self.unbreakable = True
        self.wall = True
        
    def open(self):
        if not self.unbreakable:
            self.blocked = False
            self.block_sight = False
            self.wall = False
            return True
        else:
            return False
    
    def close(self, makeIndestructible = False):
        if not self.blocked:
            self.blocked = True
            self.block_sight = True
            self.wall = True
        if makeIndestructible:
            self.unbreakable = True
    
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
    
    def triggerFunc(self):
        self.onTriggerFunction(self)
'''

def findCurrentDir():
    if getattr(sys, 'frozen', False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)
    listDir = list(datadir)
    for loop in range(4):
        del listDir[len(listDir) - 1]
    print(listDir)
    dir = ''
    for loop in range(len(listDir) - 1):
        dir += listDir[loop]
    print(dir)
    return dir

curDir = findCurrentDir()
relMapsPath = "assets\\maps"
absMapsPath = os.path.join(curDir, relMapsPath)
MAP_WIDTH, MAP_HEIGHT = 140, 60

def convertColorString(string):
    color = {'r': '', 'g': '', 'b': ''}
    currentColor = 'r'
    for char in string:
        if char in '0123456789':
            color[currentColor] += char
        elif char == ',':
            if currentColor == 'r':
                currentColor = 'g'
            elif currentColor == 'g':
                currentColor = 'b'
        elif char == ')':
            return (int(color['r']), int(color['g']), int(color['b']))

def readMap(mapDir, voidChar = None):
    mapDirPath = os.path.join(absMapsPath, mapDir)
    createdMap = [[main.Tile(blocked=False, x = x, y = y, block_sight=False, fg = colors.white, bg = colors.black, dark_bg=colors.black, dark_fg=colors.grey) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]
    
    charMapPath = os.path.join(mapDirPath, 'char.txt')
    charMap = open(charMapPath, 'r')
    x, y = 0, 0
    for line in charMap:
        for char in line:
            if not (char == chr(92) and x >= MAP_WIDTH):
                if char == '.':
                    createdMap[x][y].character = voidChar
                else:
                    createdMap[x][y].character = char
                x += 1
            else:
                x = 0
                break
        y += 1
    charMap.close()
    
    blockMapPath = os.path.join(mapDirPath, 'block.txt')
    blockMap = open(blockMapPath, 'r')
    x, y = 0, 0
    for line in blockMap:
        for char in line:
            if char != chr(92):
                if char == '.':
                    createdMap[x][y].blocked = False
                    createdMap[x][y].block_sight = False
                elif char == '#':
                    createdMap[x][y].blocked = True
                    createdMap[x][y].block_sight = True
                elif char == '=':
                    createdMap[x][y].blocked = True
                    createdMap[x][y].block_sight = False
                else:
                    createdMap[x][y].blocked = False
                    createdMap[x][y].block_sight = True
                x += 1
            else:
                x = 0
                break
        y += 1
    blockMap.close()
    
    exploMapPath = os.path.join(mapDirPath, 'exploration.txt')
    exploMap = open(exploMapPath, 'r')
    x, y = 0, 0
    for line in exploMap:
        for char in line:
            if char != chr(92):
                if char == '*':
                    createdMap[x][y].explored = False
                else:
                    createdMap[x][y].explored = True
                x += 1
            else:
                x = 0
                break
        y += 1
    exploMap.close()
    
    fgMapPath = os.path.join(mapDirPath, 'fg.txt')
    fgMap = open(fgMapPath, 'r')
    x, y = 0, 0
    for line in fgMap:
        color = {'r': '', 'g': '', 'b': ''}
        currentColor = 'r'
        for char in line:
            if char != chr(92):
                if char in '0123456789':
                    color[currentColor] += char
                elif char == ',':
                    if currentColor == 'r':
                        currentColor = 'g'
                    elif currentColor == 'g':
                        currentColor = 'b'
                elif char == ')':
                    currentColor = 'r'
                    createdMap[x][y].fg = (int(color['r']), int(color['g']), int(color['b']))
                    color = {'r': '', 'g': '', 'b': ''}
                    x += 1
            else:
                x = 0
                break
        y += 1
    fgMap.close()
    
    dark_fgMapPath = os.path.join(mapDirPath, 'dark_fg.txt')
    dark_fgMap = open(dark_fgMapPath, 'r')
    x, y = 0, 0
    for line in dark_fgMap:
        color = {'r': '', 'g': '', 'b': ''}
        currentColor = 'r'
        for char in line:
            if char != chr(92):
                if char in '0123456789':
                    color[currentColor] += char
                elif char == ',':
                    if currentColor == 'r':
                        currentColor = 'g'
                    elif currentColor == 'g':
                        currentColor = 'b'
                elif char == ')':
                    currentColor = 'r'
                    createdMap[x][y].dark_fg = (int(color['r']), int(color['g']), int(color['b']))
                    color = {'r': '', 'g': '', 'b': ''}
                    x += 1
            else:
                x = 0
                break
        y += 1
    dark_fgMap.close()
    
    bgMapPath = os.path.join(mapDirPath, 'bg.txt')
    bgMap = open(bgMapPath, 'r')
    x, y = 0, 0
    for line in bgMap:
        color = {'r': '', 'g': '', 'b': ''}
        currentColor = 'r'
        for char in line:
            if char != chr(92):
                if char in '0123456789':
                    color[currentColor] += char
                elif char == ',':
                    if currentColor == 'r':
                        currentColor = 'g'
                    elif currentColor == 'g':
                        currentColor = 'b'
                elif char == ')':
                    currentColor = 'r'
                    createdMap[x][y].bg = (int(color['r']), int(color['g']), int(color['b']))
                    color = {'r': '', 'g': '', 'b': ''}
                    x += 1
            else:
                x = 0
                break
        y += 1
    bgMap.close()
    
    dark_bgMapPath = os.path.join(mapDirPath, 'dark_bg.txt')
    dark_bgMap = open(dark_bgMapPath, 'r')
    x, y = 0, 0
    for line in dark_bgMap:
        color = {'r': '', 'g': '', 'b': ''}
        currentColor = 'r'
        for char in line:
            if char != chr(92):
                if char in '0123456789':
                    color[currentColor] += char
                elif char == ',':
                    if currentColor == 'r':
                        currentColor = 'g'
                    elif currentColor == 'g':
                        currentColor = 'b'
                elif char == ')':
                    currentColor = 'r'
                    createdMap[x][y].dark_bg = (int(color['r']), int(color['g']), int(color['b']))
                    color = {'r': '', 'g': '', 'b': ''}
                    x += 1
            else:
                x = 0
                break
        y += 1
    dark_bgMap.close()
    
    objectsPath = os.path.join(mapDirPath, 'objects.txt')
    objectsMap = open(objectsPath, 'r')
    createdObjects = []
    for line in objectsMap:
        attributes = line.split(':')
        attributeList = attributes[1].split('/')
        attributeList.pop()
        colorString = attributeList.pop(4)
        attributeList.insert(4, convertColorString(colorString))
        createdObjects.append(attributeList)
    objectsMap.close()
    
    return createdMap, createdObjects

if __name__ == '__main__':
    root = tdl.init(150, 80, 'Dementia')
    myMap, objects = readMap('sample')
    while not tdl.event.is_window_closed():
        root.clear()
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                root.draw_char(x, y, myMap[x][y].character, main.myMap[x][y].fg, myMap[x][y].bg)
        tdl.flush()

