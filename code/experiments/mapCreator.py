import colors, math, textwrap, time, os, sys, code, gzip, pathlib, traceback, ffmpy, pdb, copy, queue, random, cProfile #Code is not unused. Importing it allows us to import the rest of our custom modules in the code package.
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
from dill import objects
from layoutReader import readMap
from main import Tile

MAP_WIDTH, MAP_HEIGHT = 140, 60
myMap = [[Tile(blocked=False, x = x, y = y, block_sight=False, fg = colors.white, bg = colors.black, character = '.', dark_fg = colors.grey, dark_bg = colors.black) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]
selectedTiles = [myMap[0][0]]
objects = []

class Cursor:
    def __init__(self):
        self.x = 0
        self.y = 0

def update(showDark = False):
    root.clear()
    
    root.draw_str(2, 62, '1: turn into wall', fg = colors.yellow)
    root.draw_str(2, 64, '2: turn into ground', fg = colors.yellow)
    root.draw_str(2, 66, '3: toggle block status', fg = colors.yellow)
    root.draw_str(2, 68, '4: toggle block LOS status', fg = colors.yellow)
    root.draw_str(2, 70, '5: toggle exploration status', fg = colors.yellow)
    root.draw_str(2, 72, '6: explore all', fg = colors.yellow)
    root.draw_str(2, 74, '7: explore None', fg = colors.yellow)
    root.draw_str(2, 76, '9: toggle lit/dark', fg = colors.yellow)
    
    root.draw_str(34, 62, 'c: copy tile', fg = colors.yellow)
    root.draw_str(34, 64, 'v: paste tile', fg = colors.yellow)
    root.draw_str(34, 66, 'w: turn all into wall', fg = colors.yellow)
    root.draw_str(34, 68, 'g: turn all into ground', fg = colors.yellow)
    root.draw_str(34, 70, 'r: load an existing map folder', fg = colors.yellow)
    root.draw_str(34, 72, 's: select a square', fg = colors.yellow)
    
    root.draw_str(70, 62, 'n: create or modify an NPC', fg = colors.yellow)
    root.draw_str(70, 64, 'd: delete an NPC', fg = colors.yellow)
    root.draw_str(70, 66, 'l: copy an NPC', fg = colors.yellow)
    root.draw_str(70, 68, 'm: paste an NPC', fg = colors.yellow)
    
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if myMap[x][y] in selectedTiles and not showDark:
                root.draw_char(x, y, myMap[x][y].character, myMap[x][y].fg, colors.dark_violet)
            elif myMap[x][y] in selectedTiles and showDark:
                root.draw_char(x, y, myMap[x][y].character, myMap[x][y].dark_fg, colors.dark_violet)
            elif not showDark:
                root.draw_char(x, y, myMap[x][y].character, myMap[x][y].fg, myMap[x][y].bg)
            else:
                root.draw_char(x, y, myMap[x][y].character, myMap[x][y].dark_fg, myMap[x][y].dark_bg)
    for object in objects:
        if myMap[object.x][object.y] in selectedTiles and not showDark:
            root.draw_char(object.x, object.y, object.char, object.color, colors.dark_violet)
        elif myMap[object.x][object.y] in selectedTiles and showDark:
            root.draw_char(object.x, object.y, object.char, object.color, colors.dark_violet)
        elif not showDark:
            root.draw_char(object.x, object.y, object.char, object.color, myMap[object.x][object.y].bg)
        else:
            root.draw_char(object.x, object.y, object.char, object.color, myMap[object.x][object.y].dark_bg)
    tdl.flush()

def openDetails(x, y):
    tile = myMap[x][y]
    width, height = 36, 19
    window = tdl.Console(width, height)
    quit = False
    index = 0
    ascii = ord(tile.character)
    fg = tile.fg
    dark_fg = tile.dark_fg
    bg = tile.bg
    dark_bg = tile.dark_bg
    blocked = tile.blocked
    block_sight = tile.block_sight
    explored = tile.explored
    baseIndex = range(-1, 7)
    Red, Green, Blue = 0, 0, 0
    while not quit:
        window.clear()
        if index == 0 or index == 7:
            window.draw_str(1, 1, 'Character:', colors.black, colors.green)
        else:
            window.draw_str(1, 1, 'Character:', colors.green)
        window.draw_char(12, 1, chr(ascii))
        window.draw_str(14, 1, str(ascii))
        
        if index == 1 or index in range(8, 11):
            window.draw_str(1, 3, 'FG (lit):', colors.black, colors.green)
        else:
            window.draw_str(1, 3, 'FG (lit):', colors.green)
        if index in range(8, 11):
            window.draw_str(12, 3, '({}, {}, {})'.format(str(Red), str(Green), str(Blue)))
            window.draw_str(30, 3, '   ', fg = None, bg = (Red, Green, Blue))
        else:
            R, G, B = fg
            window.draw_str(12, 3, '({}, {}, {})'.format(str(R), str(G), str(B)))
            window.draw_str(30, 3, '   ', fg = None, bg = (R, G, B))
        
        if index == 2 or index in range(11, 14):
            window.draw_str(1, 5, 'FG (dark):', colors.black, colors.green)
        else:
            window.draw_str(1, 5, 'FG (dark):', colors.green)
        if index in range(11, 14):
            window.draw_str(12, 5, '({}, {}, {})'.format(str(Red), str(Green), str(Blue)))
            window.draw_str(30, 5, '   ', fg = None, bg = (Red, Green, Blue))
        else:
            R, G, B = dark_fg
            window.draw_str(12, 5, '({}, {}, {})'.format(str(R), str(G), str(B)))
            window.draw_str(30, 5, '   ', fg = None, bg = (R, G, B))
        
        if index == 3 or index in range(14, 17):
            window.draw_str(1, 7, 'BG (lit):', colors.black, colors.green)
        else:
            window.draw_str(1, 7, 'BG (lit):', colors.green)
        if index in range(14, 17):
            window.draw_str(12, 7, '({}, {}, {})'.format(str(Red), str(Green), str(Blue)))
            window.draw_str(30, 7, '   ', fg = None, bg = (Red, Green, Blue))
        else:
            R, G, B = bg
            window.draw_str(12, 7, '({}, {}, {})'.format(str(R), str(G), str(B)))
            window.draw_str(30, 7, '   ', fg = None, bg = (R, G, B))
        
        if index == 4 or index in range(17, 20):
            window.draw_str(1, 9, 'BG (dark):', colors.black, colors.green)
        else:
            window.draw_str(1, 9, 'BG (dark):', colors.green)
        if index in range(17, 20):
            window.draw_str(12, 9, '({}, {}, {})'.format(str(Red), str(Green), str(Blue)))
            window.draw_str(30, 9, '   ', fg = None, bg = (Red, Green, Blue))
        else:
            R, G, B = dark_bg
            window.draw_str(12, 9, '({}, {}, {})'.format(str(R), str(G), str(B)))
            window.draw_str(30, 9, '   ', fg = None, bg = (R, G, B))
        
        if index == 5 or index == 20:
            window.draw_str(1, 11, 'Blocked:', colors.black, colors.green)
        else:
            window.draw_str(1, 11, 'Blocked:', colors.green)
        window.draw_str(12, 11, str(blocked))
        
        if index == 6 or index == 21:
            window.draw_str(1, 13, 'Block LOS:', colors.black, colors.green)
        else:
            window.draw_str(1, 13, 'Block LOS:', colors.green)
        window.draw_str(12, 13, str(block_sight))
        
        if index == -1 or index == 22:
            window.draw_str(1, 15, 'Explored', colors.black, colors.green)
        else:
            window.draw_str(1, 15, 'Explored', colors.green)
        window.draw_str(12, 15, str(explored))
        
        window.draw_str(1, 17, 'x: {}, y: {}'.format(x, y))
        
        root.blit(window, 65, 24, width, height)
        tdl.flush()
        
        userInput = tdl.event.key_wait()
        if userInput.keychar.upper() == 'ESCAPE':
            if index in baseIndex:
                quit = True
            elif index == 7:
                tile.character = chr(ascii)
                index = 0
            elif index in range(8, 11):
                index = 1
                fg = Red, Green, Blue
                tile.fg = fg
            elif index in range(11, 14):
                index = 2
                dark_fg = Red, Green, Blue
                tile.dark_fg = dark_fg
            elif index in range(14, 17):
                index = 3
                bg = Red, Green, Blue
                tile.bg = bg
            elif index in range(17, 20):
                index = 4
                dark_bg = Red, Green, Blue
                tile.dark_bg = dark_bg
            elif index == 20:
                tile.blocked = blocked
                index = 5
            elif index == 21:
                tile.block_sight = block_sight
                index = 6
            elif index == 22:
                tile.explored = explored
                index = -1
        elif userInput.keychar.upper() == 'UP':
            if index in baseIndex:
                index -= 1
                if index < -1:
                    index = 6
            elif index == 7:
                ascii += 1
                if ascii > 255:
                    ascii = 0
            elif index == 8 or index == 11 or index == 14 or index == 17: #W.H.Y ?
                Red += 1
                if Red > 255:
                    Red = 0
            elif index == 9 or index == 12 or index == 15 or index == 18:
                Green += 1
                if Green > 255:
                    Green = 0
            elif index == 10 or index == 13 or index == 16 or index == 19:
                Blue += 1
                if Blue > 255:
                    Blue = 0
            elif index == 20:
                blocked = not blocked
            elif index == 21:
                block_sight = not block_sight
            elif index == 22:
                explored = not explored
        elif userInput.keychar.upper() == 'DOWN':
            if index in baseIndex:
                index += 1
                if index > 6:
                    index = -1
            elif index == 7:
                ascii -= 1
                if ascii < 0:
                    ascii = 255
            elif index == 8 or index == 11 or index == 14 or index == 17:
                Red -= 1
                if Red < 0:
                    Red = 255
            elif index == 9 or index == 12 or index == 15 or index == 18:
                Green -= 1
                if Green < 0:
                    Green = 255
            elif index == 10 or index == 13 or index == 16 or index == 19:
                Blue -= 1
                if Blue < 0:
                    Blue = 255
            elif index == 20:
                blocked = not blocked
            elif index == 21:
                block_sight = not block_sight
            elif index == 22:
                explored = not explored
        elif userInput.keychar.upper() == 'RIGHT':
            if index in range(8, 11):
                index += 1
                if index > 10:
                    index = 8
            if index in range(11, 14):
                index += 1
                if index > 13:
                    index = 11
            if index in range(14, 17):
                index += 1
                if index > 16:
                    index = 14
            if index in range(17, 20):
                index += 1
                if index > 19:
                    index = 17
        elif userInput.keychar.upper() == 'LEFT':
            if index in range(8, 11):
                index -= 1
                if index < 8:
                    index = 10
            if index in range(11, 14):
                index -= 1
                if index < 11:
                    index = 13
            if index in range(14, 17):
                index -= 1
                if index < 14:
                    index = 16
            if index in range(17, 20):
                index -= 1
                if index < 17:
                    index = 19
        elif userInput.keychar.upper() == 'ENTER':
            if index == 0:
                index = 7
            elif index == 1:
                index = 8
                Red, Green, Blue = fg
            elif index == 2:
                index = 11
                Red, Green, Blue = dark_fg
            elif index == 3:
                index = 14
                Red, Green, Blue = bg
            elif index == 4:
                index = 17
                Red, Green, Blue = dark_bg
            elif index == 5:
                index = 20
            elif index == 6:
                index = 21
            elif index == -1:
                index = 22

class Object:
    def __init__(self, x, y, char = '@', name = 'NPC', color = colors.white, dialog = 'Sample dialog', shop = "None"):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.dialog = dialog
        self.shop = shop

def createNPC(x, y):
    global objects
    found = False
    for object in objects:
        if object.x == x and object.y == y:
            npc = object
            found = True
    if not found:
        npc = Object(x, y)
    width, height = 36, 17
    window = tdl.Console(width, height)
    quit = False
    index = 0
    ascii = ord(npc.char)
    name = npc.name
    color = npc.color
    dialog = npc.dialog
    shop = npc.shop
    baseIndex = range(-1, 4)
    Red, Green, Blue = 0, 0, 0
    while not quit:
        window.clear()
        if index == 0 or index == 4:
            window.draw_str(1, 1, 'Character:', colors.black, colors.green)
        else:
            window.draw_str(1, 1, 'Character:', colors.green)
        window.draw_char(12, 1, chr(ascii))
        
        if index == 1 or index == 5:
            window.draw_str(1, 3, 'Name:', colors.black, colors.green)
        else:
            window.draw_str(1, 3, 'Name:', colors.green)
        window.draw_str(12, 3, name)
        
        if index == 2 or index in range(6, 9):
            window.draw_str(1, 5, 'FG:', colors.black, colors.green)
        else:
            window.draw_str(1, 5, 'FG:', colors.green)
        if index in range(6, 9):
            window.draw_str(12, 5, '({}, {}, {})'.format(str(Red), str(Green), str(Blue)))
            window.draw_str(30, 5, '   ', fg = None, bg = (Red, Green, Blue))
        else:
            R, G, B = color
            window.draw_str(12, 5, '({}, {}, {})'.format(str(R), str(G), str(B)))
            window.draw_str(30, 5, '   ', fg = None, bg = (R, G, B))
        
        if index == 3 or index == 9:
            window.draw_str(1, 7, 'Dialog:', colors.black, colors.green)
        else:
            window.draw_str(1, 7, 'Dialog:', colors.green)
        window.draw_str(12, 7, dialog)
        
        if index == -1 or index == 10:
            window.draw_str(1, 9, 'Shop:', colors.black, colors.green)
        else:
            window.draw_str(1, 9, 'Shop:', colors.green)
        window.draw_str(12, 9, shop)
        
        root.blit(window, 65, 24, width, height)
        tdl.flush()
        
        userInput = tdl.event.key_wait()
        if userInput.keychar.upper() == 'ESCAPE':
            if index in baseIndex:
                quit = True
            elif index == 4:
                npc.char = chr(ascii)
                index = 0
            elif index == 5:
                npc.name = name
                index = 1
            elif index in range(6, 9):
                index = 2
                color = Red, Green, Blue
                npc.color = color
            elif index == 9:
                npc.dialog = dialog
                index = 3
            elif index == 10:
                npc.shop = shop
                index = -1
        elif userInput.keychar.upper() == 'UP':
            if index in baseIndex:
                index -= 1
                if index < -1:
                    index = 3
            elif index == 4:
                ascii += 1
                if ascii > 255:
                    ascii = 0
            elif index == 6:
                Red += 1
                if Red > 255:
                    Red = 0
            elif index == 7:
                Green += 1
                if Green > 255:
                    Green = 0
            elif index == 8:
                Blue += 1
                if Blue > 255:
                    Blue = 0
        elif userInput.keychar.upper() == 'DOWN':
            if index in baseIndex:
                index += 1
                if index > 3:
                    index = -1
            elif index == 4:
                ascii -= 1
                if ascii < 0:
                    ascii = 255
            elif index == 6:
                Red -= 1
                if Red < 0:
                    Red = 255
            elif index == 7:
                Green -= 1
                if Green < 0:
                    Green = 255
            elif index == 8:
                Blue -= 1
                if Blue < 0:
                    Blue = 255
        elif userInput.keychar.upper() == 'RIGHT':
            if index in range(6, 9):
                index += 1
                if index > 8:
                    index = 6
        elif userInput.keychar.upper() == 'LEFT':
            if index in range(6, 9):
                index -= 1
                if index < 6:
                    index = 8
        elif userInput.keychar.upper() == 'ENTER':
            if index == 0:
                index = 4
            elif index == 1:
                index = 5
            elif index == 2:
                index = 6
                Red, Green, Blue = color
            elif index == 3:
                index = 9
            elif index == -1:
                index = 10
        elif userInput.keychar in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890':
            if index == 5:
                name += userInput.keychar
            elif index == 9:
                dialog += userInput.keychar
            elif index == 10:
                shop += userInput.keychar
        elif userInput.keychar.upper() == 'SPACE':
            if index == 5:
                name += ' '
            elif index == 9:
                dialog += ' '
            elif index == 10:
                shop += ' '
        elif userInput.keychar.upper() == 'BACKSPACE':
            if index == 5 and name != '':
                nameList = list(name)
                nameList.pop()
                name = ''
                for letter in nameList:
                    name += letter
            if index == 9 and dialog != '':
                dialogList = list(dialog)
                dialogList.pop()
                dialog = ''
                for letter in dialogList:
                    dialog += letter
            if index == 10 and shop != '':
                shopList = list(shop)
                shopList.pop()
                shop = ''
                for letter in shopList:
                    shop += letter
    objects.append(npc)

def findCurrentDir():
    if getattr(sys, 'frozen', False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)
    listDir = list(datadir)
    for loop in range(16):
        listDir.pop()
    print(listDir)
    dir = ''
    for loop in range(len(listDir) - 1):
        dir += listDir[loop]
    print(dir)
    return dir

def promptFolderName(escapable=False):
    #width, height = 26, 3
    #window = tdl.Console(width, height)
    quit = False
    letters = []
    while not (quit or tdl.event.is_window_closed()):
        root.clear()
        #update()
        text = '_'
        name = ''
        for letter in letters:
            name += letter
        if len(name) < 24:
            text = name + '_'
        else:
            text = name

        root.draw_str(80, 62, text)
        #root.blit(window, 57, 39, width, height)
        tdl.flush()
        
        print(name)
        userInput = tdl.event.key_wait()
        if userInput.keychar in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890":
            if len(letters) < 24:
                letters.append(userInput.keychar)
        elif userInput.keychar.upper() == 'BACKSPACE' and len(letters) > 0:
            letters.pop()
        elif userInput.keychar.upper() == 'ENTER':
            if name == '':
                pass
            else:
                return name
        elif userInput.keychar.upper() == 'ESCAPE' and escapable:
            return

def createMap():
    curDir = findCurrentDir()
    print('Enter the folder name.')
    newDir = promptFolderName(True)
    if newDir:
        relMapsPath = "assets\\maps\\" + newDir
        absMapPath = os.path.join(curDir, relMapsPath)
        index = 1
        if os.path.exists(absMapPath):
            absMapPath += str(index)
            index += 1
            while os.path.exists(absMapPath):
                pathList = list(absMapPath)
                pathList.pop()
                absMapPath = ''
                for char in pathList:
                    absMapPath += char
                absMapPath += str(index)
                index += 1
        print(absMapPath)
        os.makedirs(absMapPath)
        
        blockPath = os.path.join(absMapPath, 'block.txt')
        blockMap = open(blockPath, 'w')
        for y in range(MAP_HEIGHT):
            line = ''
            for x in range(MAP_WIDTH):
                if myMap[x][y].blocked and myMap[x][y].block_sight:
                    line += '#'
                elif not myMap[x][y].blocked and not myMap[x][y].block_sight:
                    line += '.'
                elif myMap[x][y].blocked and not myMap[x][y].block_sight:
                    line += '='
                else:
                    line += '+'
            line += chr(92)
            line += '\n'
            blockMap.write(line)
        blockMap.close()
        
        charPath = os.path.join(absMapPath, 'char.txt')
        charMap = open(charPath, 'w')
        for y in range(MAP_HEIGHT):
            line = ''
            for x in range(MAP_WIDTH):
                line += myMap[x][y].character
            line += chr(92)
            line += '\n'
            charMap.write(line)
        charMap.close()
        
        exploPath = os.path.join(absMapPath, 'exploration.txt')
        exploMap = open(exploPath, 'w')
        for y in range(MAP_HEIGHT):
            line = ''
            for x in range(MAP_WIDTH):
                if not myMap[x][y].explored:
                    line += '*'
                else:
                    line += '.'
            line += chr(92)
            line += '\n'
            exploMap.write(line)
        exploMap.close()
        
        fgPath = os.path.join(absMapPath, 'fg.txt')
        fgMap = open(fgPath, 'w')
        for y in range(MAP_HEIGHT):
            line = ''
            for x in range(MAP_WIDTH):
                line += str(myMap[x][y].fg)
            line += chr(92)
            line += '\n'
            fgMap.write(line)
        fgMap.close()
        
        dark_fgPath = os.path.join(absMapPath, 'dark_fg.txt')
        dark_fgMap = open(dark_fgPath, 'w')
        for y in range(MAP_HEIGHT):
            line = ''
            for x in range(MAP_WIDTH):
                line += str(myMap[x][y].dark_fg)
            line += chr(92)
            line += '\n'
            dark_fgMap.write(line)
        dark_fgMap.close()
        
        bgPath = os.path.join(absMapPath, 'bg.txt')
        bgMap = open(bgPath, 'w')
        for y in range(MAP_HEIGHT):
            line = ''
            for x in range(MAP_WIDTH):
                line += str(myMap[x][y].bg)
            line += chr(92)
            line += '\n'
            bgMap.write(line)
        bgMap.close()
        
        dark_bgPath = os.path.join(absMapPath, 'dark_bg.txt')
        dark_bgMap = open(dark_bgPath, 'w')
        for y in range(MAP_HEIGHT):
            line = ''
            for x in range(MAP_WIDTH):
                line += str(myMap[x][y].dark_bg)
            line += chr(92)
            line += '\n'
            dark_bgMap.write(line)
        dark_bgMap.close()
        
        objectsPath = os.path.join(absMapPath, 'objects.txt')
        objectsMap = open(objectsPath, 'w')
        for object in objects:
            line = ''
            line += 'NPC:'
            line += str(object.x)
            line += '/'
            line += str(object.y)
            line += '/'
            line += object.char
            line += '/'
            line += object.name
            line += '/'
            line += str(object.color)
            line += '/'
            line += object.dialog
            line += '/'
            line += object.shop
            line += '/'
            line += chr(92)
            line += '\n'
            objectsMap.write(line)
        objectsMap.close()
        return 'saved'
    else:
        return 'aborted'
    
def selectSquare():
    global selectedTiles
    startingTile = myMap[cursor.x][cursor.y]
    quit = False
    while not (tdl.event.is_window_closed() or quit):
        userInput = tdl.event.key_wait()
        if userInput.keychar.upper() == 'UP':
            if cursor.y > 0:
                cursor.y -= 1
                selectedTiles = [myMap[cursor.x][cursor.y], startingTile]
        elif userInput.keychar.upper() == 'DOWN':
            if cursor.y < MAP_HEIGHT - 1:
                cursor.y += 1
                selectedTiles = [myMap[cursor.x][cursor.y], startingTile]
        elif userInput.keychar.upper() == 'LEFT':
            if cursor.x > 0:
                cursor.x -= 1
                selectedTiles = [myMap[cursor.x][cursor.y], startingTile]
        elif userInput.keychar.upper() == 'RIGHT':
            if cursor.x < MAP_WIDTH - 1:
                cursor.x += 1
                selectedTiles = [myMap[cursor.x][cursor.y], startingTile]
        elif userInput.keychar.upper() == 'ENTER':
            endTile = myMap[cursor.x][cursor.y]
            quit = True
        update(showDark)
    for x in range(min(startingTile.x, endTile.x), max(startingTile.x, endTile.x) + 1):
        for y in range(min(startingTile.y, endTile.y), max(startingTile.y, endTile.y) + 1):
            selectedTiles.append(myMap[x][y])

if __name__ == '__main__':
    root = tdl.init(150, 80, 'Map Creator')
    cursor = Cursor()
    showDark = False
    update(showDark)
    quit = False
    copy = None
    copiedNPC = None
    selectedTiles = []
    while not (tdl.event.is_window_closed() or quit):
        userInput = tdl.event.key_wait()
        if userInput.keychar.upper() == 'UP':
            if cursor.y > 0:
                cursor.y -= 1
                selectedTiles = [myMap[cursor.x][cursor.y]]
        elif userInput.keychar.upper() == 'DOWN':
            if cursor.y < MAP_HEIGHT - 1:
                cursor.y += 1
                selectedTiles = [myMap[cursor.x][cursor.y]]
        elif userInput.keychar.upper() == 'LEFT':
            if cursor.x > 0:
                cursor.x -= 1
                selectedTiles = [myMap[cursor.x][cursor.y]]
        elif userInput.keychar.upper() == 'RIGHT':
            if cursor.x < MAP_WIDTH - 1:
                cursor.x += 1
                selectedTiles = [myMap[cursor.x][cursor.y]]
        elif userInput.keychar.upper() == '1' or userInput.keychar.upper() == 'KP1':
            for tile in selectedTiles:
                tile.character = '#'
                tile.blocked = True
                tile.block_sight = True
        elif userInput.keychar.upper() == '2' or userInput.keychar.upper() == 'KP2':
            for tile in selectedTiles:
                tile.character = '.'
                tile.blocked = False
                tile.block_sight = False
        elif userInput.keychar.upper() == '9' or userInput.keychar.upper() == 'KP9':
            showDark = not showDark
        elif userInput.keychar.upper() == '3' or userInput.keychar.upper() == 'KP3':
            for tile in selectedTiles:
                tile.blocked = not tile.blocked
        elif userInput.keychar.upper() == '4' or userInput.keychar.upper() == 'KP4':
            for tile in selectedTiles:
                tile.block_sight = not tile.block_sight
        elif userInput.keychar.upper() == '5' or userInput.keychar.upper() == 'KP5':
            for tile in selectedTiles:
                tile.explored = not tile.explored
        elif userInput.keychar.upper() == '6' or userInput.keychar.upper() == 'KP6':
            selectedTiles = [myMap[cursor.x][cursor.y]]
            for x in range(MAP_WIDTH):
                for y in range(MAP_HEIGHT):
                    myMap[x][y].explored = True
        elif userInput.keychar.upper() == '7' or userInput.keychar.upper() == 'KP7':
            for x in range(MAP_WIDTH):
                for y in range(MAP_HEIGHT):
                    myMap[x][y].explored = False
            selectedTiles = [myMap[cursor.x][cursor.y]]
        elif userInput.keychar.upper() == 'ENTER':
            selectedTiles = [myMap[cursor.x][cursor.y]]
            openDetails(cursor.x, cursor.y)
        elif userInput.keychar.upper() == 'ESCAPE':
            state = createMap()
            if state == 'done':
                quit = True
        elif userInput.keychar.upper() == 'C':
            selectedTiles = [myMap[cursor.x][cursor.y]]
            copy = myMap[cursor.x][cursor.y]
        elif userInput.keychar.upper() == 'V':
            if copy is not None:
                for tile in selectedTiles:
                    tile.character = copy.character
                    tile.fg = copy.fg
                    tile.dark_fg = copy.dark_fg
                    tile.bg = copy.bg
                    tile.dark_bg = copy.dark_bg
                    tile.blocked = copy.blocked
                    tile.block_sight = copy.block_sight
                    tile.explored = copy.explored
        elif userInput.keychar.upper() == 'W':
            for x in range(MAP_WIDTH):
                for y in range(MAP_HEIGHT):
                    myMap[x][y].character = '#'
                    myMap[x][y].blocked = True
                    myMap[x][y].block_sight = True
            selectedTiles = [myMap[cursor.x][cursor.y]]
        elif userInput.keychar.upper() == 'G':
            for x in range(MAP_WIDTH):
                for y in range(MAP_HEIGHT):
                    myMap[x][y].character = '.'
                    myMap[x][y].blocked = False
                    myMap[x][y].block_sight = False
            selectedTiles = [myMap[cursor.x][cursor.y]]
        elif userInput.keychar.upper() == 'R':
            print('Enter the name of the folder to be read.')
            folder = promptFolderName(True)
            if folder:
                myMap = []
                objects = []
                myMap, objectsToCreate = readMap(folder, '.')
    
                for attributeList in objectsToCreate:
                    print(attributeList)
                    object = Object(int(attributeList[0]), int(attributeList[1]), attributeList[2], attributeList[3], attributeList[4], attributeList[5], attributeList[6])
                    print(object.dialog)
                    objects.append(object)
                selectedTiles = [myMap[cursor.x][cursor.y]]
        elif userInput.keychar.upper() == 'S':
            selectSquare()
        elif userInput.keychar.upper() == 'N':
            createNPC(cursor.x, cursor.y)
        elif userInput.keychar.upper() == 'L':
            for object in objects:
                if object.x == cursor.x and object.y == cursor.y:
                    copiedNPC = Object(0, 0, object.char, object.name, object.color, object.dialog)
        elif userInput.keychar.upper() == 'M':
            if copiedNPC:
                found = False
                for object in objects:
                    if object.x == cursor.x and object.y == cursor.y:
                        found = True
                if not found:
                    copiedNPC.x = cursor.x
                    copiedNPC.y = cursor.y
                    objects.append(copiedNPC)
                    copiedNPC = Object(0, 0, copiedNPC.char, copiedNPC.name, copiedNPC.color, copiedNPC.dialog)
        elif userInput.keychar.upper() == 'D':
            for object in objects:
                if object.x == cursor.x and object.y == cursor.y:
                    objects.remove(object)

        update(showDark)
        
        
        
        