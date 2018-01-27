
import colors, math, textwrap, time, os, sys, code, gzip, pathlib, traceback, ffmpy, pdb, copy, random, cProfile, functools #Code is not unused. Importing it allows us to import the rest of our custom modules in the code package.
import tdlib as tdl
import code.dialog as dial
import music as mus
import simpleaudio as sa
import threading, multiprocessing
import dill   #THIS IS NOT AN UNUSED IMPORT. Importing this changes the behavior of the pickle module (and the shelve module too), so as we can actually save lambda expressions. EDIT : It might actually be useless to import it here, since we import it in the dilledShelve module, but it freaking finally works perfectly fine so we're not touching this.
from tdlib import *
from random import randint, choice
from math import *
from code.custom_except import *
from copy import copy, deepcopy
from os import makedirs
from collections import deque

from code.constants import MAX_HIGH_CULTIST_MINIONS, ACTION_COSTS
import code.nameGen as nameGen
import code.xpLoaderPy3 as xpL
import code.dunbranches as dBr
import code.dilledShelve as shelve
import code.spellGen as spellGen
from code.dunbranches import gluttonyDungeon
from code.custom_except import *
from music import playWavSound
from multiprocessing import freeze_support, current_process
#import code.chasmGen as chasmGen
#import code.holeGen as holeGen
from code.classes import Tile, printTileWhenWalked, NamedConsole
import code.newFullMapGen as mapGen
import code.itemGen as itemGen
import code.mobGen as mobGen

from tkinter import *
from tkinter.messagebox import * #For making obvious freaking error boxes when the console gets too bloated to read anything useful.


if (__name__ == '__main__' or __name__ == 'main__main__'):
    import code.layoutReader as layoutReader


activeProcess = []

def notCloseImmediatelyAfterCrash(exc_type, exc_value, tb):
    '''
    Does exactly what it says on the tin : prevents the console from closing immediately after crash
    '''
    traceback.print_exception(exc_type, exc_value, tb) #Print the error message
    try:
        root.__del__() #Delete the game window
    except Exception as error:
        print('Cannot delete window')
        print('Problem = ' + str(type(error)))
        print('Details = ' + str(error.args))
    try:
        for process in activeProcess:
            process.terminate()
    except:
        print("Couldn't terminate process")
    if getattr(sys, 'frozen', False): #If we are running the frozen binaries, then we prevent the console from immediately closing
        input('Press Enter to exit') #Prevent stuff from executing further until we press Enter
    else:
        pass #If we are not running the frozen binaries, we close the program immediately, since we can read the error log in IDLE/PyDev/WhateverIDEYouAreUsing's console.
    os._exit(-1) #Exit the program
    
sys.excepthook = notCloseImmediatelyAfterCrash #We call the above defined function each time the program encounters an unhandled exception. Don't try to change this function to a simple 'pass' so as to 'fix all crashes'. This would make so a lot of stuff would break and we wouldn't know when it did break or what caused it to break.
# Naming conventions :
# MY_CONSTANT
# myVariable
# myFunction()
# MyClass
# Not dramatic if you forget about this (it happens to me too), but it makes reading code easier

def findCurrentDir():
    if getattr(sys, 'frozen', False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)
    return datadir

curDir = findCurrentDir()
relDirPath = "save"
relPath = os.path.join("save", "savegame")
relPicklePath = os.path.join("save", "equipment")
relAssetPath = "assets"
relSoundPath = os.path.join("assets", "sound")
relAsciiPath = os.path.join("assets", "ascii")
relMusicPath = os.path.join("assets", "music")
relMetaPath = os.path.join("metasave", "meta")
relMetaDirPath = "metasave"
relCodePath = "code"
absDirPath = os.path.join(curDir, relDirPath)
absFilePath = os.path.join(curDir, relPath)
absPicklePath = os.path.join(curDir, relPicklePath)
absAssetPath = os.path.join(curDir, relAssetPath)
absSoundPath = os.path.join(curDir, relSoundPath)
absMusicPath = os.path.join(curDir, relMusicPath)
absAsciiPath = os.path.join(curDir, relAsciiPath)
absMetaPath = os.path.join(curDir, relMetaPath)
absMetaDirPath = os.path.join(curDir, relMetaDirPath)
absCodePath = os.path.join(curDir, relCodePath)

class MusicThread(threading.Thread):
    def __init__(self, musicName = 'Bumpy_Roots.wav'):
        self.musicName = musicName
        self.playObj = None
        threading.Thread.__init__(self)
        self.daemon = True
    
    def run(self):
        while True:
            if self.playObj is None or not self.playObj.is_playing():
                self.playObj = playWavSound(self.musicName, forceStop=True)

def runMusic(musicName):
    print('RUNNING MUSIC')
    playObj = None
    while True:
        if playObj is None or not playObj.is_playing():
            playObj = playWavSound(musicName, forceStop=True)
'''            
class NamedConsole(tdl.Console):
    def __init__(self, name, width, height, type = 'noType'):
        self.name = name
        self.type = type
        tdl.Console.__init__(self, width, height)
'''
#_____________ CONSTANTS __________________
MOVEMENT_KEYS = {
                 #Standard arrows
                 'UP': [0, -1],
                 'DOWN': [0, 1],
                 'LEFT': [-1, 0],
                 'RIGHT': [1, 0],

                 # Diagonales (pave numerique off)
                 'HOME': [-1, -1],
                 'PAGEUP': [1, -1],
                 'PAGEDOWN': [1, 1],
                 'END': [-1, 1],

                 # Pave numerique
                 # 7 8 9
                 # 4   6
                 # 1 2 3
                 'KP1': [-1, 1],
                 'KP2': [0, 1],
                 'KP3': [1, 1],
                 'KP4': [-1, 0],
                 'KP6': [1, 0],
                 'KP7': [-1, -1],
                 'KP8': [0, -1],
                 'KP9': [1, -1],
                 
                 }

WIDTH, HEIGHT, LIMIT = 159, 80, 20 #Defaults : 150, 80, 20
MAP_WIDTH, MAP_HEIGHT = 140, 60 #Defaults : 140, 60
MID_MAP_WIDTH, MID_MAP_HEIGHT = MAP_WIDTH//2, MAP_HEIGHT//2
MID_WIDTH, MID_HEIGHT = int(WIDTH/2), int(HEIGHT/2)

# - GUI Constants -
BAR_WIDTH = 20 #Default : 20

PANEL_HEIGHT = HEIGHT - MAP_HEIGHT - 1 #Default : 10
PANEL_WIDTH = MAP_WIDTH #default: WIDTH
CON_HEIGHT = HEIGHT - PANEL_HEIGHT
MID_CON_HEIGHT = int(CON_HEIGHT // 2)
PANEL_Y = HEIGHT - PANEL_HEIGHT

LOOK_HEIGHT = PANEL_HEIGHT
LOOK_Y = PANEL_Y
LOOK_WIDTH = 21 #Default: 15
LOOK_X = MAP_WIDTH - LOOK_WIDTH + 1

SIDE_PANEL_WIDTH = WIDTH - MAP_WIDTH #Default: WIDTH - PANEL_WIDTH
SIDE_PANEL_X = MAP_WIDTH
SIDE_PANEL_Y = 0
SIDE_PANEL_MODES = ['stats', 'enemies', 'items', 'inventory', 'equipment', 'spells', 'stealth'] #, 'buffs']
currentSidepanelMode = 0
SIDE_PANEL_TEXT_WIDTH = SIDE_PANEL_WIDTH - 5
SIDE_PANEL_INFO_Y = 4 #Default: 5

MSG_X = BAR_WIDTH + 9 #Default : BAR_WIDTH + 10
MSG_WIDTH = WIDTH - BAR_WIDTH - 10 - 40 #Default : WIDTH - BAR_WIDTH - 10 - 40
MSG_HEIGHT = PANEL_HEIGHT - 2 #Default : PANEL_HEIGHT - 1

BUFF_WIDTH = 30 #Default : 30
BUFF_X = WIDTH - 35 #Default : WIDTH - 35

INVENTORY_WIDTH = 70 #Default : 70
SPELLS_MENU_WIDTH = INVENTORY_WIDTH + 4 #Default : INVETORY_WIDTH + 4 (so as to compensate for the slightly longer headers).
SPELL_MENU_WIDTH = SPELLS_MENU_WIDTH #Alias for SPELLS_MENU_WIDTH because dumbass me always types one in place of the other.

LEVEL_SCREEN_WIDTH = 40 #Default : 40

CHARACTER_SCREEN_WIDTH = 50 #Default : 50
CHARACTER_SCREEN_HEIGHT = 21 #Default : 21

DEATH_SCREEN_WIDTH = 25 #Default : 25
DEATH_SCREEN_HEIGHT = 10 #Default : 10
consolesDisplayed = False
heroName = None
FORBIDDEN_NAMES = ["Ayeth", "Pukil", "Zarg", "Guillem"]

SURPRISE_ATTACK_CRIT = 30
SPELL_INFO_WIDTH = 60 #Default : 60 / This is actually the width which we pass to textwrap when displaying the spells description (which is useless in normal circumstances), not the actual width of the menubox itself. In other terms, this is the maximum width value that the actual menubox width value can take.  
TRAIT_INFO_WIDTH = 25

CLASS_LEVEL_WIDTH = 100
CLASS_LEVEL_HEIGHT = 60

SOUND_ENABLED = True

def dialogTestFunction():
    '''
    PLEASE DO NOT DELETE, REQUIRED FOR DIALOG MODULE
    '''
    print("Successfully triggered function call on dialog screen enter")

def getHeroName():
    hiddenPath = findHiddenOptionsPath()
    if not os.path.exists(hiddenPath):
        return None
    try:
        hOptionsFilePath = os.path.join(hiddenPath, "DATA")
        hOptionsFile = open(hOptionsFilePath, "r")
        line = hOptionsFile.readline()
        splittedLine = line.split(":")
        heroName = splittedLine[1]
        return heroName
    except:
        traceback.print_exc()
        return None

def getOptionsFile():
    hPath = findHiddenOptionsPath()
    if not os.path.exists(hPath):
        os.makedirs(hPath)
    optionsPath = os.path.join(hPath, "OPTIONS")
    if not os.path.exists(optionsPath):
        optionsFile = open(optionsPath, "w")
        optionsFile.write("SOUND_ENABLED:True")
        optionsFile.close()
    return optionsPath

def splitLine(line):
    return line.split(":")[1]

def readOptions():
    optionsFile = open(getOptionsFile(), "r")
    try:
        sndLine = optionsFile.readline()
        valueStr = splitLine(sndLine)
        if valueStr == "True":
            return True
        else:
            return False
    except:
        optionsFile.close()
        return "ERROR"

def applyOptions():
    global SOUND_ENABLED
    try:
        SOUND_ENABLED = readOptions()
        if SOUND_ENABLED == "ERROR":
            raise ValueError("Error during readOptions. The options file might be corrupted.")
    except:
        import tkinter
        import tkinter.messagebox
        dummyWindow = tkinter.Tk()
        dummyWindow.withdraw()
        toDelete = tkinter.messagebox.askyesno("Error", "There has been an error processing the options file. \n Do you want to reset the options to default ? Choosing No will terminate the program.", icon = ERROR)
        if toDelete:
            try:
                os.remove(getOptionsFile())
            except Exception as e:
                tkinter.messagebox.showerror("Critical Error", "Couldn't reset options file. Try closing every running Python process running and try again. \n If that didn't fix the problem, please send a bug report at https://github.com/Edern76/DementiaRL/issues with your system specs and the following error message attached : \n \n {}".format(traceback.format_exc()))
                quitGame("Closed due to error", noSave = True)
            try:
                SOUND_ENABLED = readOptions()
            except Exception as e:
                tkinter.messagebox.showerror("Critical Error", "Could still not process options file. \n Please send a bug report at https://github.com/Edern76/DementiaRL/issues with your system specs and the following error message attached : \n \n {}".format(traceback.format_exc()))
                quitGame("Closed due to error", noSave = True)
        else:
            quitGame("Closed due to error", noSave = True)

def writeOptions(toWrite):
    optionsFile = open(getOptionsFile(), "w")
    optionsFile.write("SOUND_ENABLED:" + toWrite)
    optionsFile.close()
    
    
        
        

# - GUI Constants -

# - Consoles -
if (__name__ == '__main__' or __name__ == 'main__main__') and not consolesDisplayed and current_process().name == 'MainProcess':
    freeze_support()
    print('Displaying consoles because instance is ' + __name__)
    #tdl.set_font(os.path.join(absAsciiPath, 'terminal16x16_gs_ro.png'), greyscale=True, altLayout=False, columnFirst = False)
    root = tdl.init(WIDTH, HEIGHT, 'Dementia')
    con = NamedConsole('con', WIDTH, HEIGHT)
    panel = NamedConsole('panel', WIDTH, PANEL_HEIGHT)
    sidePanel = NamedConsole('side panel', SIDE_PANEL_WIDTH, HEIGHT)
    lookPanel = NamedConsole('look panel', LOOK_WIDTH, LOOK_HEIGHT)
    consolesDisplayed = True
else:
    print(__name__)
    root = None
    con = None
    panel = None
    sidePanel = None
    lookPanel = None
# - Consoles

FOV_recompute = True
FOV_ALGO = 'BASIC' #Default : BASIC
FOV_LIGHT_WALLS = True
SIGHT_RADIUS = 15 #Default : 10
MAX_ROOM_MONSTERS = 3 #Default : 3
MAX_ROOM_ITEMS = 3 #Default : 3
GRAPHICS = 'modern'
LEVEL_UP_BASE = 200 # Set to 200 once testing complete
LEVEL_UP_FACTOR = 150 #Default : 150
SKILLPOINTS_PER_LEVEL = 10 #Default: 2
NATURAL_REGEN = True
BASE_HIT_CHANCE = 50 #Default : 50

boss_FOV_recompute = True
BOSS_FOV_ALGO = 'BASIC' #Default : BASIC
BOSS_SIGHT_RADIUS = 20 #Default : 20
bossDungeonsAppeared = {'gluttony': False, 'greed' : False, 'wrath': False}
lastHitter = None
nemesisList = []
mobsToCalculate = []
mustCalculate = False
currentMusic = 'No_Music.wav'
detectedPlayerThisTurn = []
monstersDetected = [[],[],[],[],[]]

exploredMaps = {} #template: exploredMaps = {'main1': [(x, y, character, blocked, chasm),...], 'main1stairs': [(x, y, char, color)]}

tutorial = False
hasSpokenToGeneral = False

# - Spells -
LIGHTNING_DAMAGE = 40 #Default : 40
LIGHTNING_RANGE = 5 #Default : 5
CONFUSE_NUMBER_TURNS = 10 #Default : 10
CONFUSE_RANGE = 8 #Default: 8
DARK_PACT_DAMAGE = 24 #Default : 24
FIREBALL_SPELL_BASE_DAMAGE = 12 #Default : 12
FIREBALL_SPELL_BASE_RADIUS = 1 #Default : 1
FIREBALL_SPELL_BASE_RANGE = 4 #Default : 4

RESURECTABLE_CORPSES = ["darksoul", "ogre"]

BASE_HUNGER = 1500 #Default : 500
CRITICAL_MULTIPLIER = 3 #Default : 3

MAX_ASTAR_FAILS = 1 #Possibly unstable at 1 (but best performance), if you get weird results with Astar (aside from freezing) try bumping this number up a LITTLE bit (3 is already way overkill)
REGEN_THRESHOLD = 4000 #Number of iterations of stairs placing loop before you throw away current map and regenerates another one. Setting this too high may make map generation longer. Setting this too low may provoke infinite loops or cause the game to reject potentially valid maps (also making the map gen longer). (base : 2000)

# - Spells -
#_____________ CONSTANTS __________________

myMap = None
color_dark_wall = dBr.mainDungeon.mapGeneration['wallDarkFG']
color_light_wall = dBr.mainDungeon.mapGeneration['wallFG']
color_dark_ground = dBr.mainDungeon.mapGeneration['groundDarkBG']
color_dark_gravel = dBr.mainDungeon.mapGeneration['gravelDarkFG']
color_light_ground = dBr.mainDungeon.mapGeneration['groundBG']
color_light_gravel = dBr.mainDungeon.mapGeneration['gravelFG']
maxRooms = dBr.mainDungeon.maxRooms
roomMinSize = dBr.mainDungeon.roomMinSize
roomMaxSize = dBr.mainDungeon.roomMaxSize

gameState = 'playing'
playerAction = None
DEBUG = False #If true, enables debug messages
REVEL = False #If true, revels all items
drawDjik = False
stopBossFF = False

lookCursor = None
cursor = None
bossTiles = None
bossEntrance = None

gameMsgs = [] #List of game messages
logMsgs = []
tilesInRange = []
showTilesInRange = False
explodingTiles = []
tilesinPath = []
tilesInRect = []
menuWindows = []
hiroshimanNumber = 0
FOV_recompute = True
inventory = [] #Player inventory
equipmentList = [] #Player equipment
identifiedItems = []
activeSounds = []
spells = [] #List of all spells in the game

djikVisitedTiles = []
markers = []
visuBoss = []

########
# These need to be globals because otherwise Python will flip out when we try to look for some kind of stairs in the object lists.
stairs = None
upStairs = None
gluttonyStairs = None
townStairs = None
greedStairs = None
wrathStairs = None
########
hiroshimanHasAppeared = False
highCultistHasAppeared = False
player = None
levelAttributes = None
currentBranch = dBr.mainDungeon #Setting this to None causes errors. It doesn't matter tough, since this gets updated on loading or starting a game.
branchLevel = 1
totalLevel = 1
depthLevel = 1

########QUEST RELATED FUNCTION########
# Yes it's an awful way to do it. Yes it's only going to get worse. Yes it's absolute spaghetti code, but so is the rest of the codebase.
def flipDebug():
    global DEBUG
    DEBUG = not DEBUG

def checkDebug():
    return DEBUG

def checkStackableItemInInventory(nameToFind, amount):
    for item in inventory:
        if item.name == nameToFind:
            if item.Item.amount >= amount:
                return True
    return False

def checkQuestStarted(nameToFind):
    for quest in player.Player.questList:
        if quest.name == nameToFind and quest.state == 'active':
            return True
    return False

def startBaking():
    testQuest.take()

def checkBakingStarted():
    return checkQuestStarted("Baking 101")

def checkBakingStartable():
    return not checkBakingStarted()

def checkBakingInProgress():
    return (checkBakingStarted() and not (checkStackableItemInInventory('crawling horror heart', 1) and checkStackableItemInInventory('snake tooth', 2)))
            
def checkBakingCompletable():
    return (checkBakingStarted() and (checkStackableItemInInventory('crawling horror heart', 1) and checkStackableItemInInventory('snake tooth', 2)))

def actuallyValidBaking():
    testQuest.valid()

########
def deleteSaves():
    if not os.path.isdir(absDirPath):
        os.makedirs(absDirPath)
        print('Created save folder')
    os.chdir(absDirPath)
    saves = [save for save in os.listdir(absDirPath) if ((save.endswith(".bak") or save.endswith(".dat") or save.endswith(".dir") or save.startswith("map")) and not save.startswith('nemesis'))]
    for save in saves:
        os.remove(save)
        print("Deleted " + str(save))

stairCooldown = 0
pathfinder = None
pathToTargetTile = []

def convertMusics():
    musicList = ['Bumpy_Roots', 'Dusty_Feelings', 'Hoxton_Princess', 'Sweltering_Battle', 'hit', 'miss']
    tryPath = os.path.join(absCodePath, 'ffmpeg.exe')
    if os.path.exists(tryPath):
        executablePath = os.path.join(absCodePath, 'ffmpeg.exe')
    else:
        executablePath = os.path.join(curDir, 'ffmpeg.exe')
    for music in musicList:
        mp3Music = music + '.mp3'
        wavMusic = music + '.wav'
        mp3Path = os.path.join(absMusicPath, mp3Music)
        mp3SoundPath = os.path.join(absSoundPath, mp3Music)
        wavPath = os.path.join(absSoundPath, wavMusic)
        if os.path.exists(wavPath):
            print('MUSIC_CHK : Found {}'.format(wavPath))
        else:
            print('MUSIC_CHK_WAR : Didnt found {}'.format(wavPath))
            if os.path.exists(mp3Path):
                print('MUSIC_CONV : Converting {} to wav'.format(mp3Path))
                if sys.platform.startswith('win32') or sys.platform.startswith('win64'):
                    ff = ffmpy.FFmpeg(inputs = {mp3Path : None}, outputs= {wavPath : None}, executable= executablePath)
                else:
                    ff = ffmpy.FFmpeg(inputs = {mp3Path : None}, outputs= {wavPath : None})
                ff.run()
                print('MUSIC_CONV : Created {}'.format(wavPath))
            elif os.path.exists(mp3SoundPath):
                print('MUSIC_CONV : Converting {} to wav'.format(mp3Path))
                if sys.platform.startswith('win32') or sys.platform.startswith('win64'):
                    ff = ffmpy.FFmpeg(inputs = {mp3SoundPath : None}, outputs= {wavPath : None}, executable= executablePath)
                else:
                    ff = ffmpy.FFmpeg(inputs = {mp3SoundPath : None}, outputs= {wavPath : None})
                ff.run()
                print('MUSIC_CONV : Created {}'.format(wavPath))
            else:
                print('MUSIC_CONV_ERR : Path {} doesnt exists, skipping...'.format(mp3Path))
        print()
        
def animStep(waitTime = .01, doUpdate = True):
    global FOV_recompute
    FOV_recompute = True
    if doUpdate:
        Update()
    tdl.flush()
    time.sleep(waitTime)

#_____________MENU_______________
def drawMenuOptions(y, options, window, page, width, height, headerWrapped, maxPages, pagesDisp, selectedIndex, noItemMessage = None, displayItem = False, posX = None):
    window.clear()
    for i, line in enumerate(headerWrapped):
        window.draw_str(1, 1+i, headerWrapped[i], fg = colors.amber)
    if pagesDisp:
        window.draw_str(10, y - 2, str(page + 1) + '/' + str(maxPages + 1), fg = colors.amber)
    letterIndex = ord('a')
    counter = 0
    pageIndex = 0
    drawActualRectangle(window, width, height)
    if (noItemMessage is None or not options or options[0] != str(noItemMessage)):
        if len(options) == 1:
            print(options[0])
            print(str(noItemMessage))
        for optionText in options:
            if counter >= page * 26 and counter < (page + 1) * 26:
                text = '(' + chr(letterIndex) + ') ' + optionText
                if selectedIndex == pageIndex:
                    window.draw_str(1, y, text, fg = colors.black, bg = colors.white)
                else:
                    window.draw_str(1, y, text, bg=None)
                letterIndex += 1
                y += 1
                pageIndex += 1
            counter += 1
    else:
        window.draw_str(1, y, options[0], bg = None, fg = colors.red)
    if displayItem and not posX:
        print('displaying item')
        x = MID_WIDTH - int(width/2) - 15
    elif posX:
        x = posX
    else:
        print('not displaying item')
        x = MID_WIDTH - int(width/2)
    y = MID_HEIGHT - int(height/2)
    root.blit(window, x, y, width, height, 0, 0)
    
    if not displayItem:
        tdl.flush()
        
def drawColorMenuOptions(y, options, window, page, width, height, headerWrapped, maxPages, pagesDisp, selectedIndex, noItemMessage = None, displayItem = False, posX = None):
    window.clear()
    for i, line in enumerate(headerWrapped):
        window.draw_str(1, 1+i, headerWrapped[i], fg = colors.amber)
    if pagesDisp:
        window.draw_str(10, y - 2, str(page + 1) + '/' + str(maxPages + 1), fg = colors.amber)
    letterIndex = ord('a')
    counter = 0
    pageIndex = 0
    for k in range(width):
        window.draw_char(k, 0, chr(196))
    window.draw_char(0, 0, chr(218))
    window.draw_char(k, 0, chr(191))
    kMax = k
    for l in range(height):
        if l > 0:
            window.draw_char(0, l, chr(179))
            window.draw_char(kMax, l, chr(179))
    lMax = l
    for m in range(width):
        window.draw_char(m, lMax, chr(196))
    window.draw_char(0, lMax, chr(192))
    window.draw_char(kMax, lMax, chr(217))
    if (noItemMessage is None or not options or options[0] != str(noItemMessage)):
        if len(options) == 1:
            print(options[0])
            print(str(noItemMessage))
        for (optionText, optionColor) in options:
            if counter >= page * 26 and counter < (page + 1) * 26:
                if optionColor is None:
                    colorToDraw = colors.white
                    #colorHighlighted = colors.black
                else:
                    colorToDraw = optionColor
                    '''
                    if colorToDraw not in (colors.white, colors.grey, colors.gray, colors.dark_gray, colors.darker_gray, colors.darkest_gray, colors.light_gray, colors.lighter_gray, colors.lightest_gray, colors.grey, colors.dark_grey, colors.darker_grey, colors.darkest_grey, colors.light_grey, colors.lighter_grey, colors.lightest_grey):
                        colorHighlighted = colorToDraw
                    else:
                        colorHighlighted = colors.black
                    '''
                text = '(' + chr(letterIndex) + ') ' + optionText
                if selectedIndex == pageIndex:
                    window.draw_str(1, y, text, fg = colors.black, bg = colorToDraw)
                else:
                    window.draw_str(1, y, text, fg=colorToDraw, bg=None)
                letterIndex += 1
                y += 1
                pageIndex += 1
            counter += 1
    else:
        window.draw_str(1, y, options[0], bg = None, fg = colors.red) #Draw the no item message, which is the first element of the array options
    if displayItem and not posX:
        print('displaying item')
        x = MID_WIDTH - int(width/2) - 15
    elif posX:
        x = posX
    else:
        print('not displaying item')
        x = MID_WIDTH - int(width/2)
    y = MID_HEIGHT - int(height/2)
    root.blit(window, x, y, width, height, 0, 0)
    
    if not displayItem:
        tdl.flush()

def menu(header, options, width, usedList = None, noItemMessage = None, inGame = True, adjustHeight = True, needsInput = True, displayItem = False, name = 'noName', switchKey = None, switchHeader = None, itemDisplayed = 'item', posX = None):
    global menuWindows, FOV_recompute
    hasSwitched = False
    index = 0
    print('display item:', str(displayItem))
    page = 0
    pagesDisp = True
    maxPages = len(options)//26
    if maxPages < 1:
        pagesDisp = False
    pagesDispHeight = 0
    if pagesDisp:
        pagesDispHeight = 1
    headerWrapped = textwrap.wrap(header, width)
    headerHeight = len(headerWrapped)
    if switchHeader :
        switchHeaderWrapped = textwrap.wrap(switchHeader, width)
        switchHeaderHeight = len(switchHeaderWrapped)
    if adjustHeight:
        toAdd = 3
    else:
        toAdd = 2
    if header == "":
        headerHeight = 0
    if len(options) > 26:
        height = 26 + headerHeight + toAdd + pagesDispHeight
    else:
        height = len(options) + headerHeight + toAdd + pagesDispHeight
    if menuWindows and inGame:
        for mWindow in menuWindows:
            mWindow.clear()
    window = NamedConsole(name, width, height, 'menu')
    menuWindows.append(window)
    window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)
    if not hasSwitched:
        y = headerHeight + 2 + pagesDispHeight
        headerToDraw = headerWrapped
    else:
        y = switchHeaderHeight + 2 + pagesDispHeight
        headerToDraw = switchHeaderWrapped
    drawMenuOptions(y, options, window, page, width, height, headerToDraw, maxPages, pagesDisp, index, noItemMessage, displayItem, posX = posX)
    print('Not loop menu option draw')
    
    if displayItem and usedList:
        '''
        if menuWindows:
            for mWindow in menuWindows:
                if not mWindow.name == 'inventory' and not mWindow.type == 'menu':
                    mWindow.clear()
                    print('CLEARED {} WINDOW OF TYPE {}'.format(mWindow.name, mWindow.type))
                    if mWindow.name == 'displayItemInInventory':
                        ind = menuWindows.index(mWindow)
                        del menuWindows[ind]
                        print('Deleted')
                tdl.flush()
        '''
        if itemDisplayed == 'item':
            item = usedList[0].Item
            item.displayItem(posX = MID_WIDTH + width//2 - 15)
        elif itemDisplayed == 'spell':
            usedList[0].displayInfo(MID_WIDTH + width//2 - 15)
        elif itemDisplayed == 'weapon':
            try:
                usedList[0].Item.displayItem(posX = MID_WIDTH + width//2 - 15)
            except:
                pass
    print('Not loop item disp')
    tdl.flush()
    
    if needsInput:
        choseOrQuit = False
        index = 0
        while not choseOrQuit:
            if not hasSwitched:
                y = headerHeight + 2 + pagesDispHeight
                headerToDraw = headerWrapped
            else:
                y = switchHeaderHeight + 2 + pagesDispHeight
                headerToDraw = switchHeaderWrapped
            
            if page == maxPages:
                maxIndex = len(options) - maxPages * 26 - 1
            else:
                maxIndex = 25
            #choseOrQuit = True
            arrow = False
            drawMenuOptions(y, options, window, page, width, height, headerToDraw, maxPages, pagesDisp, index, noItemMessage, displayItem, posX = posX)
            tdl.flush()
            print('Loop menu option disp')
            key = tdl.event.key_wait_no_shift()
            keyChar = key.keychar
            if keyChar == '':
                keyChar = ' '
            elif keyChar == 'RIGHT':
                if pagesDisp:
                    index = 0
                page += 1
                choseOrQuit = False
                arrow = True
            elif keyChar == 'LEFT':
                if pagesDisp:
                    index = 0
                page -= 1
                choseOrQuit = False
                arrow = True
            elif keyChar == 'UP':
                choseOrQuit = False
                index -= 1
                arrow = True
            elif keyChar == 'DOWN':
                choseOrQuit = False
                index += 1
                arrow = True

            if page > maxPages:
                page = 0
            if page < 0:
                page = maxPages
            if index < 0:
                index = maxIndex
            if index > maxIndex:
                index = 0
            
            if displayItem and usedList:
                if itemDisplayed == 'item':
                    item = usedList[index + page * 26].Item
                    item.displayItem(posX = MID_WIDTH + width//2 - 15)
                elif itemDisplayed == 'spell':
                    usedList[index + page * 26].displayInfo(MID_WIDTH + width//2 - 15)
                elif itemDisplayed == 'weapon':
                    try:
                        usedList[index + page*26].Item.displayItem(posX = MID_WIDTH + width//2 - 15)
                    except:
                        #usedList[0+page*26].Item.displayItem(posX = MID_WIDTH + width//2 - 15)
                        pass
            print('Loop item disp')
            
            if not arrow:
                if switchKey and keyChar == switchKey:
                    hasSwitched = not hasSwitched
                    for loop in range(10):
                        print("SWITCHED")
                if keyChar in 'abcdefghijklmnopqrstuvwxyz':
                    if DEBUG:
                        message(keyChar)
                    index = ord(keyChar) - ord('a')
                    if index >= 0 and index + page * 26 < len(options):
                        if not switchKey:
                            return index + page * 26
                        else:
                            return (index + page * 26, hasSwitched)
                    elif index + page * 26 < 0:
                        index = 0
                    elif index + page * 26 >= len(options):
                        index = len(options) - 1
                elif keyChar.upper() == 'ENTER':
                    if menuWindows and inGame:
                        for mWindow in menuWindows:
                            mWindow.clear()
                            ind = menuWindows.index(mWindow)
                            del menuWindows[ind]
                    if not switchKey:
                        return index + page * 26
                    else:
                        return (index + page * 26, hasSwitched)
                elif keyChar.upper() == "ESCAPE":
                    print('Cancelled')
                    if not switchKey:
                        return "cancelled"
                    else:
                        return ("cancelled", False)
                else:
                    continue
    else:
        pass
    if not switchKey:
        return None
    else:
        return (None, False)

def colorMenu(header, options, width, usedList = None, noItemMessage = None, inGame = True, adjustHeight = True, needsInput = True, displayItem = False, name = 'noName', switchKey = None, switchHeader = None):
    global menuWindows, FOV_recompute
    hasSwitched = False
    index = 0
    print('display item:', str(displayItem))
    page = 0
    pagesDisp = True
    maxPages = len(options)//26
    if maxPages < 1:
        pagesDisp = False
    pagesDispHeight = 0
    if pagesDisp:
        pagesDispHeight = 1
    headerWrapped = textwrap.wrap(header, width)
    headerHeight = len(headerWrapped)
    if switchHeader :
        switchHeaderWrapped = textwrap.wrap(switchHeader, width)
        switchHeaderHeight = len(switchHeaderWrapped)
    if adjustHeight:
        toAdd = 3
    else:
        toAdd = 2
    if header == "":
        headerHeight = 0
    if len(options) > 26:
        height = 26 + headerHeight + toAdd + pagesDispHeight
    else:
        height = len(options) + headerHeight + toAdd + pagesDispHeight
    if menuWindows and inGame:
        for mWindow in menuWindows:
            mWindow.clear()
    window = NamedConsole(name, width, height, 'menu')
    menuWindows.append(window)
    window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)
    if not hasSwitched:
        y = headerHeight + 2 + pagesDispHeight
        headerToDraw = headerWrapped
    else:
        y = switchHeaderHeight + 2 + pagesDispHeight
        headerToDraw = switchHeaderWrapped
    drawColorMenuOptions(y, options, window, page, width, height, headerToDraw, maxPages, pagesDisp, index, noItemMessage, displayItem)
    print('Not loop menu option draw')
    
    if displayItem and usedList:
        item = usedList[0].Item
        item.displayItem(posX = MID_WIDTH + width//2 - 15)
    print('Not loop item disp')
    tdl.flush()
    
    if needsInput:
        choseOrQuit = False
        index = 0
        while not choseOrQuit:
            if not hasSwitched:
                y = headerHeight + 2 + pagesDispHeight
                headerToDraw = headerWrapped
            else:
                y = switchHeaderHeight + 2 + pagesDispHeight
                headerToDraw = switchHeaderWrapped
            
            if page == maxPages:
                maxIndex = len(options) - maxPages * 26 - 1
            else:
                maxIndex = 25
            #choseOrQuit = True
            arrow = False
            drawColorMenuOptions(y, options, window, page, width, height, headerToDraw, maxPages, pagesDisp, index, noItemMessage, displayItem)
            tdl.flush()
            print('Loop menu option disp')
            key = tdl.event.key_wait_no_shift()
            keyChar = key.keychar
            if keyChar == '':
                keyChar = ' '
            elif keyChar == 'RIGHT':
                if pagesDisp:
                    index = 0
                page += 1
                choseOrQuit = False
                arrow = True
            elif keyChar == 'LEFT':
                if pagesDisp:
                    index = 0
                page -= 1
                choseOrQuit = False
                arrow = True
            elif keyChar == 'UP':
                choseOrQuit = False
                index -= 1
                arrow = True
            elif keyChar == 'DOWN':
                choseOrQuit = False
                index += 1
                arrow = True

            if page > maxPages:
                page = 0
            if page < 0:
                page = maxPages
            if index < 0:
                index = maxIndex
            if index > maxIndex:
                index = 0
            
            if displayItem and usedList:
                item = usedList[index + page * 26].Item
                item.displayItem(posX = MID_WIDTH + width//2 - 15)
            print('Loop item disp')
            
            if not arrow:
                if switchKey and keyChar == switchKey:
                    hasSwitched = not hasSwitched
                    for loop in range(10):
                        print("SWITCHED")
                if keyChar in 'abcdefghijklmnopqrstuvwxyz':
                    if DEBUG:
                        message(keyChar)
                    index = ord(keyChar) - ord('a')
                    if index >= 0 and index + page * 26 < len(options):
                        if not switchKey:
                            return index + page * 26
                        else:
                            return (index + page * 26, hasSwitched)
                    elif index + page * 26 < 0:
                        index = 0
                    elif index + page * 26 >= len(options):
                        index = len(options) - 1
                elif keyChar.upper() == 'ENTER':
                    if menuWindows and inGame:
                        for mWindow in menuWindows:
                            mWindow.clear()
                            ind = menuWindows.index(mWindow)
                            del menuWindows[ind]
                    if not switchKey:
                        return index + page * 26
                    else:
                        return (index + page * 26, hasSwitched)
                elif keyChar.upper() == "ESCAPE":
                    print('Cancelled')
                    if not switchKey:
                        return "cancelled"
                    else:
                        return ("cancelled", False)
                else:
                    continue
    else:
        pass
    if not switchKey:
        return None
    else:
        return (None, False)


def msgBox(text, width = 50, inGame = True, adjustHeight = True, adjustWidth = False, needsInput = True):
    if adjustWidth:
        textLength = len(text)
        width = textLength + 2
    menu(text, [], width, None, inGame, adjustHeight, needsInput)

def drawCentered(cons = con , y = 1, text = "Lorem Ipsum", fg = None, bg = None):
    xCentered = (WIDTH - len(text))//2
    cons.draw_str(xCentered, y, text, fg, bg)

def drawCenteredVariableWidth(cons, y, text, fg = None, bg = None, width = WIDTH):
    xCentered = (width - len(text))//2
    cons.draw_str(xCentered, y, text, fg, bg)

def getCenterFilled(text = 'Lorem Ipsum'):
    xCentered = (WIDTH - len(text))//2
    newText = ''
    passNb = 0
    while passNb != 2:
        for x in range(xCentered):
            newText += ' '
        if passNb == 0:
            newText += text
        passNb += 1
    return newText

def getRightFilled(text = 'Lorem Ipsum'):
    newText = str(text)
    remaining = WIDTH - len(newText)
    for loop in range(remaining):
        newText += ' '
    return newText

def drawCenteredOnX(cons = con, x = 1, y = 1, text = "Lorem Ipsum", fg = None, bg = None):
    centeredOnX = x - (len(text)//2)
    cons.draw_str(centeredOnX, y, text, fg, bg)

def message(newMsg, color = colors.white):
    newMsgLines = textwrap.wrap(newMsg, MSG_WIDTH) #If message exceeds log width, split it into two or more lines
    for line in newMsgLines:
        if len(gameMsgs) == MSG_HEIGHT:
            del gameMsgs[0] #Deletes the oldest message if the log is full

        gameMsgs.append([(line, color)])
        logMsgs.append([(line, color)])

def fancyMessage(messages = ['This is a', ' test', ' message.'], color = [colors.white, colors.green, colors.white]):
    '''
    @ATTENTION: You MUST type in the whitespaces or everything will crash
    @ATTENTION: Because of how the algorithm works, entering 'this' and then 'is' as separate colors will make 'is' the same color as 'this'. Thus prefer entering 'that'
    '''
    text = ''
    for txt in messages:
        text += txt
    print(messages, text, color)
    lines = textwrap.wrap(text, MSG_WIDTH)
    for line in lines:
        if len(gameMsgs) == MSG_HEIGHT:
            del gameMsgs[0] #Deletes the oldest message if the log is full
        newLine = []
        splitted = line.split()
        for word in splitted:
            i = 0
            while word not in messages[i]:
                i += 1
            
            if word != splitted[0]:
                word = ' ' + word
            newLine.append((word, color[i]))
        gameMsgs.append(newLine)
        logMsgs.append(newLine)

#_____________MENU_______________

#_________ BUFFS ___________
def convertBuffsToNames(fighter):
    names = []
    for buff in fighter.buffList:
        names.append(buff.name)
    return names

def convertTilesToCoords(tilesList):
    newList = []
    for tile in tilesList:
        newList.append((tile.x, tile.y))
    return newList

def consumeRessource(fighter, buff, ressources = {'stamina': 1}):
    ressourcelist = list(ressources.keys())
    for ressource in ressourcelist:
        if ressource == 'stamina':
            fighter.stamina -= ressources[ressource]
            if fighter.stamina <= 0:
                fighter.stamina = 0
                buff.removeBuff()
        if ressource == 'MP':
            fighter.MP -= ressources[ressource]
            if fighter.MP <= 0:
                fighter.MP = 0
                buff.removeBuff()
        if ressource == 'HP':
            fighter.hp -= ressources[ressource]
            if fighter.hp <= 0:
                fighter.hp = 0
                buff.removeBuff()

def regenRessource(fighter, ressources = {'stamina': 1}):
    ressourcelist = list(ressources.keys())
    for ressource in ressourcelist:
        if ressource == 'stamina':
            fighter.stamina += ressources[ressource]
            if fighter.stamina > fighter.maxStamina:
                fighter.stamina = fighter.maxStamina
                #buff.removeBuff()
        if ressource == 'MP':
            fighter.MP += ressources[ressource]
            if fighter.MP > fighter.maxMP:
                fighter.MP = fighter.maxMP
                #buff.removeBuff()
        if ressource == 'HP':
            fighter.hp += ressources[ressource]
            if fighter.hp > fighter.maxHP:
                fighter.hp = fighter.maxHP
                #buff.removeBuff()

def randomDamage(name, fighter = None, chance = 33, minDamage = 1, maxDamage = 1, dmgMessage = None, dmgColor = colors.red, msgPlayerOnly = True, dmgType = {'fire': 100}):
    dice = randint(1, 100)
    if dice <= chance:
        damage = randint(minDamage, maxDamage)
        damageDict = {}
        keyList = list(dmgType.keys())
        i = 0
        for key in keyList:
            if i == len(keyList)-1:
                dmgList = [damageDict[dmgKey] for dmgKey in keyList if dmgKey != key]
                damageDict[key] = damage - sum(dmg for dmg in dmgList)
            else:
                damageDict[key] = round((dmgType[key] * damage)/100)
            i += 1
        damageTaken = fighter.takeDamage(damageDict, name)
        totalDmg = 0
        for key in list(damageTaken.keys()):
            totalDmg += damageTaken[key]
        if (dmgMessage is not None) and (fighter == player.Fighter or (not msgPlayerOnly)):
            message(dmgMessage.format(totalDmg), dmgColor)

def addSlot(fighter, slot):
    print('adding {} slot to {}'.format(slot, fighter.owner.name))
    fighter.slots.append(slot)

class Buff: #also (and mainly) used for debuffs
    def __init__(self, name, color, owner = None, cooldown = 20, showCooldown = True, showBuff = True,
                 applyFunction = None, continuousFunction = None, removeFunction = None, type = 'None',
                 strength = 0, dexterity = 0, constitution = 0, willpower = 0, hp = 0, armor = 0, power = 0, accuracy = 0, evasion = 0, maxMP = 0,
                 critical = 0, armorPenetration = 0, rangedPower = 0, stamina = 0, stealth = 0, attackSpeed = 0, moveSpeed = 0, rangedSpeed = 0,
                 resistances = {'physical': 0, 'poison': 0, 'fire': 0, 'cold': 0, 'lightning': 0, 'light': 0, 'dark': 0, 'none': 0},
                 attackTypes = {}, flight = None, resistible = True):
        '''
        Function used to initialize a new instance of the Buff class
        '''
        self.name = name
        self.color = color
        self.baseCooldown = cooldown
        self.curCooldown = cooldown
        self.applyFunction = applyFunction
        self.continuousFunction = continuousFunction
        self.removeFunction = removeFunction
        self.owner = owner
        self.showCooldown = showCooldown
        self.showBuff = showBuff
        self.type = type
        
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.willpower = willpower
        self.maxHP = hp
        self.armor = armor
        self.power = power
        self.accuracy = accuracy
        self.evasion = evasion
        self.maxMP = maxMP
        self.critical = critical
        self.armorPenetration = armorPenetration
        self.rangedPower = rangedPower
        self.stamina = stamina
        self.stealth = stealth
        self.attackSpeed = attackSpeed
        self.moveSpeed = moveSpeed
        self.rangedSpeed = rangedSpeed
        self.resistances = resistances
        self.attackTypes = attackTypes
        self.flight = flight
        self.resistible = resistible
        
        self.hpDiff = 0
        self.mpDiff = 0
    
    def applyBuff(self, target):
        '''
        Method allowing to apply the buff to target creature
        '''
        print(self.name, target.name)
        self.owner = target
        if target == player and player.Player.getTrait('trait', 'Physical withstandingness') != 'not found':
            dice = randint(1, 100)
            if dice <= player.Player.getTrait('skill', 'Endurance').amount * 5:
                message('You resist the {} condition!'.format(self.name), self.color)
                return
        if self.owner.Fighter:
            if not self.name in convertBuffsToNames(target.Fighter): #If target is not already under effect of the buff
                self.curCooldown = self.baseCooldown #Initialization of the buff cooldown
                if self.showBuff:
                    message(self.owner.name.capitalize() + ' is now ' + self.name + '!', self.color) #If it is necessary, inform the player of the buff
                if self.applyFunction is not None:
                    self.applyFunction(self.owner.Fighter) #If the applyFunction method exists, execute it
                self.owner.Fighter.buffList.append(self) #Add the buff to target's buffs list
                
                hpBonus = 0
                mpBonus = 0
                if self.owner.Player:
                    hpBonus = 5 * self.constitution
                    mpBonus = 5 * self.willpower
                self.owner.Fighter.hp += self.maxHP + hpBonus
                self.owner.Fighter.MP += self.maxMP + mpBonus
                self.owner.Fighter.stamina += self.stamina + hpBonus
                
            else: #If target is already under effect of the buff
                bIndex = convertBuffsToNames(self.owner.Fighter).index(self.name)
                target.Fighter.buffList[bIndex].curCooldown += self.baseCooldown #Extend duration of the buff
    
    def removeBuff(self):
        '''
        Method allowing to remove the buff from target creature
        '''
        if self.removeFunction is not None: #If removeFunction method exists, execute it
            self.removeFunction(self.owner.Fighter)
        self.owner.Fighter.buffList.remove(self) #Delete the buff from target creature's buffs list
        if self.owner.Fighter.buffList is None:
            self.owner.Fighter.buffList = []
        if self.showBuff:
            message(self.owner.name.capitalize() + ' is no longer ' + self.name + '.', self.color) #Inform the player
        
        hpBonus = 0
        mpBonus = 0
        if self.owner.Player:
            hpBonus = 5 * self.constitution
            mpBonus = 5 * self.willpower
        self.owner.Fighter.hp -= self.maxHP + hpBonus
        self.owner.Fighter.MP -= self.maxMP + mpBonus
        self.owner.Fighter.stamina -= self.stamina + hpBonus
    
    def passTurn(self):
        '''
        Method called each turn
        '''
        self.curCooldown -= 1 #Decrease from 1 the buff cooldown
        if self.curCooldown <= 0: #If buff reached its time, call the removeBuff method
            self.removeBuff()
        else: #If buff has not yet reached its time limit, we call the continuousFunction if it exists
            if self.continuousFunction is not None:
                self.continuousFunction(self.owner.Fighter)

class TileBuff:
    def __init__(self, name, fg = None, bg = None, char = None, owner = None, cooldown = 20, blocksTile = False, buffsWhenWalked=[], addMoveCost = 0, continuousFunc = []):
        self.name = name
        self.fg = fg
        self.bg = bg
        self.char = char
        self.owner = owner
        self.baseCooldown = cooldown
        self.curCooldown = cooldown
        self.blocksTile = blocksTile
        self.buffsWhenWalked = buffsWhenWalked
        self.addMoveCost = addMoveCost
        self.continuousFunc = continuousFunc
    
    def applyTileBuff(self, x, y):
        global myMap
        if myMap[x][y].buffList:
            myMap[x][y].buffList.append(self)
        else:
            myMap[x][y].buffList = [self]
        self.owner = myMap[x][y]
    
    def passTurn(self):
        self.curCooldown -= 1
        if self.curCooldown <= 0:
            self.owner.buffList.remove(self)
        elif self.continuousFunc:
            for func in self.continuousFunc:
                func(self.owner)
        
#_________ BUFFS ___________

#_____________SPELLS_____________

class Spell:
    "Class used by all active abilites (not just spells)"
    def __init__(self,  ressourceCost, cooldown, useFunction, name, ressource = 'MP', type = 'Magic', subtype = None, magicLevel = 0, arg1 = None, arg2 = None, arg3 = None, hiddenName = None, onRecoverLearn = [], castSpeed = 100, template = None, requirements = {}):
        self.ressource = ressource
        self.ressourceCost = ressourceCost
        self.maxCooldown = cooldown
        self.curCooldown = 0
        self.useFunction = useFunction
        self.name = name
        self.type = type
        self.subtype = subtype
        self.magicLevel = magicLevel
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        if hiddenName:
            self.hiddenName = hiddenName
        else:
            self.hiddenName = name
        self.onRecoverLearn = onRecoverLearn
        self.castSpeed = castSpeed
        self.template = template
        self.requirements = requirements
    
    def checkCast(self):
        if not self.requirements:
            return False
        for skill in self.requirements.keys():
            if player.Player.getTrait('skill', skill).amount < self.requirements[skill]:
                cannotCast = True
                break
        else:
            cannotCast = True
        return cannotCast
    
    def cast(self, caster = player, target = player):
        global FOV_recompute
        
        ressourceCost = self.ressourceCost
        maxCooldown = self.maxCooldown
        if caster == player:
            if self.checkCast():
                message('You are not skilled enough to cast {}.'.format(self.name))
                return 'cancelled'
            if (self.type == 'martial' and player.Player.getTrait('trait', 'Combat knowledge') != 'not found') or (self.type == 'physical' and player.Player.getTrait('trait', 'Greater efficiency') != 'not found'):
                ressourceCost = ressourceCost//2
                maxCooldown = maxCooldown//2
        #    self.updateSpellStats()
        if self.ressource == 'MP' and caster.Fighter.MP < ressourceCost:
            FOV_recompute = True
            message(caster.name.capitalize() + ' does not have enough MP to cast ' + self.name +'.')
            return 'cancelled'
        if self.ressource == 'Stamina' and caster.Fighter.stamina < ressourceCost:
            FOV_recompute = True
            message(caster.name.capitalize() + ' does not have enough stamina to cast ' + self.name +'.')
            return 'cancelled'

        if self.arg1 is None:
            state = self.useFunction(caster, target)
            if state != 'cancelled' and state != 'didnt-take-turn':
                caster.Fighter.actionPoints -= self.castSpeed
                FOV_recompute = True
                self.setOnCooldown(caster.Fighter, maxCooldown)
                if self.ressource == 'MP':
                    caster.Fighter.MP -= ressourceCost
                elif self.ressource == 'HP':
                    caster.Fighter.takeDamage({'none': ressourceCost}, 'your spell')
                elif self.ressource == 'Stamina':
                    caster.Fighter.stamina -= ressourceCost
                return 'used'
            else:
                return 'cancelled'
        elif self.arg2 is None and self.arg1 is not None:
            state = self.useFunction(self.arg1, caster, target)
            if state != 'cancelled' and state != 'didnt-take-turn':
                caster.Fighter.actionPoints -= self.castSpeed
                FOV_recompute = True
                self.setOnCooldown(caster.Fighter, maxCooldown)
                if self.ressource == 'MP':
                    caster.Fighter.MP -= ressourceCost
                elif self.ressource == 'HP':
                    caster.Fighter.takeDamage({'none': ressourceCost}, 'your spell')
                elif self.ressource == 'Stamina':
                    caster.Fighter.stamina -= ressourceCost
                return 'used'
            else:
                return 'cancelled'
        elif self.arg3 is None and self.arg2 is not None:
            state = self.useFunction(self.arg1, self.arg2, caster, target)
            if state != 'cancelled' and state != 'didnt-take-turn':
                caster.Fighter.actionPoints -= self.castSpeed
                FOV_recompute = True
                self.setOnCooldown(caster.Fighter, maxCooldown)
                if self.ressource == 'MP':
                    caster.Fighter.MP -= ressourceCost
                elif self.ressource == 'HP':
                    caster.Fighter.takeDamage({'none': ressourceCost}, 'your spell')
                elif self.ressource == 'Stamina':
                    caster.Fighter.stamina -= ressourceCost
                return 'used'
            else:
                return 'cancelled'
        elif self.arg3 is not None:
            state = self.useFunction(self.arg1, self.arg2, self.arg3, caster, target)
            if state != 'cancelled' and state != 'didnt-take-turn':
                caster.Fighter.actionPoints -= self.castSpeed
                FOV_recompute = True
                self.setOnCooldown(caster.Fighter, maxCooldown)
                if self.ressource == 'MP':
                    caster.Fighter.MP -= ressourceCost
                elif self.ressource == 'HP':
                    caster.Fighter.takeDamage({'none': ressourceCost}, 'your spell')
                elif self.ressource == 'Stamina':
                    caster.Fighter.stamina -= ressourceCost
                return 'used'
            else:
                return 'cancelled'
    
    def setOnCooldown(self, fighter, cooldown = -1):
        if cooldown < 0:
            cooldown = self.maxCooldown
        try:
            fighter.knownSpells.remove(self)
            self.curCooldown = cooldown
            fighter.spellsOnCooldown.append(self)
        except ValueError:
            print('SPELL {} is not in known spell list when trying to set it on cooldown'.format(self.name))

    def displayInfo(self, posX = None):
        global FOV_recompute
        FOV_recompute = True
        if self.template:
            baseWidth = SPELL_INFO_WIDTH
            desc = dial.formatText(str(self.template), baseWidth)
            header = textwrap.wrap(self.name.capitalize(), baseWidth)
            prevLine = None
            descriptionHeight = 0
            for line in desc:
                if line != "BREAK":
                    descriptionHeight += 1
                else:
                    if prevLine and prevLine == "BREAK":
                        descriptionHeight += 1
                prevLine = line
                
            height = descriptionHeight + 5
            
            curMaxWidth = 0
            for line in desc:
                if len(line) > curMaxWidth:
                    curMaxWidth = len(line)
            for line in header:
                if len(line) > curMaxWidth:
                    curMaxWidth = len(line)
            width = curMaxWidth + 3
            
            
            if menuWindows:
                for mWindow in menuWindows:
                    if not mWindow.name == 'spellMenu' and not mWindow.type == 'menu':
                        mWindow.clear()
                        print('CLEARED {} WINDOW OF TYPE {}'.format(mWindow.name, mWindow.type))
                        if mWindow.name == 'displaySpellInfo':
                            ind = menuWindows.index(mWindow)
                            del menuWindows[ind]
                            print('Deleted')
                    tdl.flush()
            FOV_recompute = True
            Update()
            window = NamedConsole('displaySpellInfo', width, height)
            print('Created disp window')
            window.clear()
            menuWindows.append(window)
    
            for k in range(width):
                window.draw_char(k, 0, chr(196))
            window.draw_char(0, 0, chr(218))
            window.draw_char(k, 0, chr(191))
            kMax = k
            for l in range(height):
                if l > 0:
                    window.draw_char(0, l, chr(179))
                    window.draw_char(kMax, l, chr(179))
            lMax = l
            for m in range(width):
                window.draw_char(m, lMax, chr(196))
            window.draw_char(0, lMax, chr(192))
            window.draw_char(kMax, lMax, chr(217))
            Y = 1
            X = 3
            prevLine = None
            for line in header:
                drawCenteredVariableWidth(window, y=Y, text = line, fg=colors.amber, width=width)
                Y+=1
            Y+=1
            for line in desc:
                if line != "BREAK":
                    if 'spell costing' in line:
                        window.draw_str(1, Y, line[:21])
                        if 'MP' in line:
                            color = colors.blue
                        elif 'HP' in line:
                            color = colors.dark_red
                        else:
                            color = colors.white
                        window.draw_str(22, Y, line[21:], fg = color)
                    else:
                        window.draw_str(1, Y, line)
                    incrementY = True
                else:
                    if prevLine and prevLine == "BREAK":
                        incrementY = True
                    else:
                        incrementY = False
                if incrementY:
                    Y += 1
                prevLine = line
            if not posX:
                posX = MID_WIDTH - width // 2
            posY = MID_HEIGHT - height//2
            root.blit(window, posX, posY, width, height, 0, 0)
        
            menuWindows.append(window)
            FOV_recompute = True
            tdl.flush()
            #tdl.event.key_wait()
            


def rSpellDamage(amount, caster, target, type, dmgTypes = {'physical': 100}):
        if caster is None:
            caster = player
        damageDict = {}
        keyList = list(dmgTypes.keys())
        i = 0
        for key in keyList:
            if i == len(keyList)-1:
                dmgList = [damageDict[dmgKey] for dmgKey in keyList if dmgKey != key]
                damageDict[key] = amount - sum(dmg for dmg in dmgList)
            else:
                damageDict[key] = round((dmgTypes[key] * amount)/100)
            i += 1
        if target != player:
            if caster == player:
                messageColor = colors.green
            else:
                messageColor = colors.white
            dmgTxtFunc = lambda damageTaken: target.Fighter.formatRawDamageText(damageTaken, "{} takes {}!", messageColor, '{} is hit by the spell but is insensible to it.', colors.white)
        else:
            dmgTxtFunc = lambda damageTaken: player.Fighter.formatRawDamageText(damageTaken, "{} take {}!", colors.red, '{} are hit by the spell but are insensible to it.', colors.white)
        
        target.Fighter.takeDamage(damageDict, "A spell", damageTextFunction = dmgTxtFunc)
        
        if target is not None and target.Fighter is not None and target.Fighter.hp > 0:
            if type == "Fire" and randint(1, 100) <= 70:
                burning = Buff('burning', colors.flame, cooldown= randint(3, 6), continuousFunction=lambda fighter: randomDamage('fire', fighter, chance = 100, minDamage=1, maxDamage=3, dmgMessage = 'You take {} damage from burning !'))
                burning.applyBuff(target)
            elif type == "Poison" and randint(1, 100) <= 70:
                poisoned = Buff('poisoned', colors.purple, owner = None, cooldown=randint(5, 10), continuousFunction=lambda fighter: randomDamage('poison', fighter, chance = 100, minDamage=1, maxDamage=10, dmgType = {'poison': 100}))
                poisoned.applyBuff(target)
            elif type == "Ice" and randint(1, 100) <= 70:
                frozen = Buff('frozen', colors.light_violet, cooldown = 4)
                frozen.applyBuff(target)
            elif type == "Lightning" and randint(1, 100) <= 70:
                stunned = Buff('stunned', colors.light_yellow, cooldown = 4)
                stunned.applyBuff(target)
        else:
            if DEBUG:
                message("Your enemy died on the spot !")

def rSpellHunger(amount, type, caster, target):
    ### HUNGER REMOVED ###
    '''
    if target == player:
        if type == "Buff":
            player.Player.hunger += amount
        else:
            player.Player.hunger -= amount
        
        if player.Player.hunger > BASE_HUNGER:
            player.Player.hunger = int(BASE_HUNGER)
        if player.Player.hunger < 0:
            player.Player.hunger = 0
    '''
    pass

def rSpellAttack(amount, type, caster, target):
    '''
    if type == "Buff":
        message(target.name.capitalize() + " should have had its attack increase. But the developper was to lazy to implement it in time !") #TO-DO
    else:
        message(target.name.capitalize() + " should have had its attack decrease. But the developper was to lazy to implement it in time !") #TO-DO
    '''
    if type == "Buff":
        enraged = Buff('strengthened', colors.dark_red, cooldown = amount, power = 10, resistible = False)
        enraged.applyBuff(target)
    else:
        enraged = Buff('weakened', colors.light_red, cooldown = amount, power = -10)
        enraged.applyBuff(target)

def rSpellDefense(amount, type, caster, target):
    '''
    if type == "Buff":
        message(target.name.capitalize() + " should have had its defense increase. But the developper was to lazy to implement it in time !") #TO-DO
    else:
        message(target.name.capitalize() + " should have had its defense decrease. But the developper was to lazy to implement it in time !") #TO-DO
    '''
    if type == "Buff":
        armor = Buff('invigorated', colors.cyan, cooldown = amount, armor = 10, resistible = False)
        armor.applyBuff(target)
    else:
        armor = Buff('vulnerable', colors.dark_cyan, cooldown = amount, armor = -10)
        armor.applyBuff(target)
        
def rSpellSpeed(amount, type, caster, target):
    if type == "Buff":
        message(target.name.capitalize() + " should have had its speed increase. But the developper was to lazy to implement it in time !") #TO-DO
    else:
        message(target.name.capitalize() + " should have had its speed decrease. But the developper was to lazy to implement it in time !") #TO-DO
        
#castHeal(amount, caster, target)

def restoreMana(amount, caster, target):
    if target.Fighter:
        target.Fighter.MP += amount
    if target.Fighter.MP > target.Fighter.maxMP:
        target.Fighter.MP = int(target.Fighter.maxMP)

def rSpellRemoveBuff(buffToRemove, caster, target):
    if target.Fighter:
        for buff in target.Fighter.buffList:
            if buff.name == buffToRemove:
                buff.removeBuff()

def targetSelf(caster, zone = None):
    if displayConfirmSpell(caster, caster, zone):
        return caster
    else:
        return 'cancelled'

def targetMonster(maxRange = None, melee = False):
    target = targetTile(maxRange, melee = melee)
    if target == 'cancelled':
        return None
    else:
        (x,y) = target
        for obj in objects:
            if obj.x == x and obj.y == y and obj.Fighter: #and obj != player:
                return obj

def targetMonsterWrapper(caster = None):
    target = targetMonster()
    return target

def doNothing(*args, **kwargs):
    pass

def createObjectFromCoords(x, y):
    return GameObject(x,y, char=None, name = None)

def targetTileWrapper(caster = None, zone = None):
    result = targetTile(styleAOE = zone)
    if result != 'cancelled':
        (x,y) = result
        return createObjectFromCoords(x, y)
    else:
        return 'cancelled'

def singleTarget(startPoint, caster, shotRange = 0):
    return [(startPoint.x, startPoint.y)]

def verticalCross(startPoint, caster, shotRange = 3):
    affectedTiles = [(startPoint.x, startPoint.y)]
    i = 1
    while i <= shotRange:
        affectedTiles.append((startPoint.x + i, startPoint.y))
        affectedTiles.append((startPoint.x - i, startPoint.y))
        affectedTiles.append((startPoint.x, startPoint.y + i))
        affectedTiles.append((startPoint.x, startPoint.y - i))
        i += 1
    return affectedTiles

def diagonalCross(startPoint, caster, shotRange = 3):
    affectedTiles = [(startPoint.x, startPoint.y)]
    i = 1
    while i <= shotRange:
        affectedTiles.append((startPoint.x + i, startPoint.y + i))
        affectedTiles.append((startPoint.x - i, startPoint.y - i))
        affectedTiles.append((startPoint.x - i, startPoint.y + i))
        affectedTiles.append((startPoint.x + i, startPoint.y - i))
        i += 1
    return affectedTiles

def raySpell(startPoint, caster, shotRange = None):
    print(startPoint, caster, shotRange)
    (sourceX, sourceY) = (caster.x, caster.y)
    (destX, destY) = (startPoint.x, startPoint.y)
    line = tdl.map.bresenham(sourceX, sourceY, destX, destY)
    newLine = []
    if len(line) > 1:
        dx = destX - sourceX
        dy = destY - sourceY
        (x, y) = line[len(line) - 1]
        counter = 0
        while counter < 25:
            newX = x + dx
            newY = y + dy
            tempLine = tdl.map.bresenham(x, y, newX, newY)
            dx = newX - x
            dy = newY - y
            x = newX
            y = newY
            counter += 1
            del tempLine[0]
            newLine.extend(tempLine)
            if newX >= MAP_WIDTH or newY >= MAP_HEIGHT or newX <= 0 or newY <= 0:
                break
    line.extend(newLine)
    tempLine = line.copy()
    for i, (x, y) in enumerate(tempLine):
        try:
            if myMap[x][y].blocked:
                for a in line[i:]:
                    line.remove(a)
                break
        except IndexError:
            for a in line[i:]:
                line.remove(a)
            break
    line.remove((sourceX, sourceY))
    return line

def areaOfEffect(startPoint, caster, shotRange = 2):
    '''    
                              X
                    X        XXX 
           X       XXX      XXXXX 
    X     XXX     XXXXX    XXXXXXX
0  X0X   XX0XX   XXX0XXX  XXXX0XXXX
    X     XXX     XXXXX    XXXXXXX 
           X       XXX      XXXXX
                    X        XXX
                              X

PSEUDOCODE IMPLEMENTATION (so as I don't forget anything while actually implementing it in Python):

If X is the number of tiles affected on the row where 0 is on each side of the 0, then to build this kind of figure you need to:

Start from the 0 tile
Go X tiles down. Add this tile to the affected tiles list
While <= x (i=1, i++):
    Go up one tile. Add it to affected tiles
    Go i tiles left and i tiles right of previous tile. Add them to affected tiles. 
    Go back to center tile
k = 1
While x-k >= 0:
    Go up one tile. Add it to affected tiles.
    Go x-k tiles left and x-k tiles right of previous tile. Add them to affected tiles.
    Go back to center tile.
    k += 1

Then find everything in affected tiles, fill in the targets list and return said list
    '''
    startX, startY = startPoint.x, startPoint.y
    bottomY = startY - shotRange
    affectedTiles = [(startX, bottomY)]
    curY = bottomY
    
    for x in range(startX - shotRange - 2, startX + shotRange + 2):
        for y in range(startY - shotRange - 2, startY + shotRange + 2):
            if tileDistance(x, y, startX, startY) <= shotRange:
                affectedTiles.append((x, y))
    '''
    i = 1
    counter = 0
    while i <= shotRange: #Using while instead of for so as to avoid range() shenanigans
        counter += 1
        if counter > 50:
            raise InfiniteLoopPrevention("First outer while in AOE. I = {} shotRange = {}".format(i, shotRange))
        curY += 1
        affectedTiles.append((startX, curY))
        moveCounter = 0
        innerCounter = 0
        while moveCounter < i:
            moveCounter += 1
            innerCounter += 1
            if innerCounter > 100:
                raise InfiniteLoopPrevention("First inner while in AOE. MoveCounter = {} I = {}".format(moveCounter, i))
            affectedTiles.append((startX - moveCounter, curY))
            affectedTiles.append((startX + moveCounter, curY))
        i += 1
    k = 1
    while (shotRange - k) >= 0:
        curY += 1
        counter += 1
        if counter > 50:
            raise InfiniteLoopPrevention("Second outer while in AOE. MoveCounter = {} shotRange = {} K = {}".format(moveCounter, shotRange, k))
        affectedTiles.append((startX, curY))
        moveCounter = 0
        innerCounter = 0
        while moveCounter < (shotRange - k):
            moveCounter += 1
            innerCounter += 1
            if innerCounter > 100:
                raise InfiniteLoopPrevention("Second inner while in AOE. MoveCounter = {} shotRange = {} K = {}".format(moveCounter, shotRange, k))
            affectedTiles.append((startX - moveCounter, curY))
            affectedTiles.append((startX + moveCounter, curY))
        k += 1
    '''
    return affectedTiles

def cleanList(entryList):
    "For when duplicates are still showing up in a list after you've tried everything else"
    cleanedList = []
    idList = []
    while entryList:
        curObj = entryList.pop(0)
        curID = id(curObj)
        if not curID in idList:
            cleanedList.append(curObj)
        idList.append(curID)
    return cleanedList

def processTiles(tileList, targetDead = False):
    targetList = []
    counter = 0
    for object in objects:
        counter += 1
        if counter > 500:
            raise InfiniteLoopPrevention("Processing tiles. Objects list = {}".format(objects))
        if (int(object.x), int(object.y)) in tileList and object.Fighter and (object.Fighter.hp > 0 or targetDead) and not object in targetList:
            targetList.append(object)
    return targetList

def rSpellExec(func1 = doNothing, func2 = doNothing, func3 = doNothing, targetFunction = targetMonsterWrapper, zoneFunction = singleTarget, color = colors.white, caster = None, target = None):
    global FOV_recompute
    if targetFunction.__name__ != 'targetSelf':
        message('Choose a target for your spell, press Escape to cancel.', colors.light_cyan)
    #if targetFunction.__name__ == 'targetTileWrapper':
    chosenTarget = targetFunction(caster, lambda start, caster: zoneFunction(start, caster, 3))
    #else:
    #    chosenTarget = targetFunction(caster)
    if chosenTarget != 'cancelled':
        print("FOOOOOOOOOOOOOOOOOOOOUNNNNNNNNNNNNNNNNNNND TARGEEEEEEEEEEEEEEEEEET")
        print("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        print(chosenTarget)
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        
        print("Before Zone")
        tilesList = zoneFunction(chosenTarget, caster, 3)
        print("After Zone, before draw")
        if len(tilesList) > 1:
            print("Draw")
            print(tilesList)
            for (x,y) in tilesList:
                if not myMap[x][y].blocked:
                    explodingTiles.append((x, y))
            explode(color)
            '''
                    con.draw_char(x,y, '*', fg = color)
            root.blit(con, 0, 0, WIDTH, HEIGHT, 0, 0)
            tdl.flush()
            time.sleep(2) #Set to .01 once testing done
            FOV_recompute = True
            Update()
            tdl.flush()
            '''
        print("After draw, before process")
        targetList = cleanList(processTiles(tilesList))
        
        print(targetList)
        
        if len(targetList) > 0:
            counter = 0
            for actualTarget in targetList:
                counter += 1
                if counter > 1000:
                    raise InfiniteLoopPrevention("Application of functions. Target list = {}".format(targetList))
                if actualTarget is not None and actualTarget.Fighter is not None and actualTarget.Fighter.hp > 0:
                    func1(caster, actualTarget)
                if actualTarget is not None and actualTarget.Fighter is not None and actualTarget.Fighter.hp > 0:
                    func2(caster, actualTarget)
                else:
                    if DEBUG:
                        message("OVERKILL !")
                if actualTarget is not None and actualTarget.Fighter is not None and actualTarget.Fighter.hp > 0:
                    func3(caster, actualTarget)
                else:
                    if DEBUG:
                        message("OVERKILL !")
        else:
            message("Your spell didn't hit anything !")
    else:
        message("You decided not to cast the spell.")
        return 'cancelled'
    
def convertRandTemplateToSpell(template = None):
    if template is None:
        template = spellGen.createSpell()
        print(template)
    

    if template.targeting == "Self":
        targetFunction = targetSelf
    elif template.targeting == "Closest":
        targetFunction = closestMonsterWrapper
    elif template.targeting == "Farthest":
        targetFunction = farthestMonsterWrapper
    else:
        targetFunction = targetTileWrapper
    
    if template.zone == "AOE":
        zoneFunction = areaOfEffect
    elif template.zone == "Cross":
        zoneFunction = verticalCross
    elif template.zone == "X":
        zoneFunction = diagonalCross
    elif template.zone == 'Line':
        zoneFunction = raySpell
    else:
        zoneFunction = singleTarget 
    zone = "SingleTile"
    #TO-DO : Implement the other zones, targeting options
    requirements = {}
    effects = [template.eff1, template.eff2, template.eff3]
    funcs = [doNothing, doNothing, doNothing]
    for i in range(len(effects)):
        #WARNING : Bad code incoming. There is probably a cleaner way to do this, but I don't see it.
        curEffect = effects[i]
        toAdd = doNothing
        if curEffect is not None:
            if curEffect.name == "Fire damage":
                amount = int(curEffect.amount)
                newFireFunc = functools.partial(rSpellDamage, amount) #Freezes the value of the amount variable into the function
                toAdd = lambda caster, target : newFireFunc(caster, target, "Fire", dmgTypes={'fire':100})
            elif curEffect.name == "Poison damage":
                amount = int(curEffect.amount)
                newPoiFunc = functools.partial(rSpellDamage, amount)
                toAdd = lambda caster, target : newPoiFunc(caster, target, "Poison", dmgTypes={'poison':100})
            elif curEffect.name == "Physical damage":
                amount = int(curEffect.amount)
                newPhyFunc = functools.partial(rSpellDamage, amount)
                toAdd = lambda caster, target : newPhyFunc(caster, target, "Physical")
            elif curEffect.name == "Ice damage":
                amount = int(curEffect.amount)
                newIceFunc = functools.partial(rSpellDamage, amount) #Freezes the value of the amount variable into the function
                toAdd = lambda caster, target : newIceFunc(caster, target, "Ice", dmgTypes={'cold':100})
            elif curEffect.name == "Lightning damage":
                amount = int(curEffect.amount)
                newElecFunc = functools.partial(rSpellDamage, amount)
                toAdd = lambda caster, target : newElecFunc(caster, target, "Lightning", dmgTypes={'lightning':100})
            elif curEffect.name.startswith("Hunger"): #SHOULD BE REMOVED
                if curEffect.name.endswith("+"):
                    type = "Buff"
                else:
                    type = "Debuff"
                
                amount = int(curEffect.amount)
                newHungFunc = functools.partial(rSpellHunger, amount, type)
                toAdd = lambda caster, target : newHungFunc(caster, target)
            elif curEffect.name.startswith("Power"):
                if curEffect.name.endswith("+"):
                    type = "Buff"
                else:
                    type = "Debuff"
                
                amount = int(curEffect.amount)
                newAttFunc = functools.partial(rSpellAttack, amount, type)
                toAdd = lambda caster, target : newAttFunc(caster, target)
            elif curEffect.name.startswith("Armor"):
                if curEffect.name.endswith("+"):
                    type = "Buff"
                else:
                    type = "Debuff"
                amount = int(curEffect.amount)
                newDefFunc = functools.partial(rSpellDefense, amount, type)
                toAdd = lambda caster, target : newDefFunc(caster, target)
            elif curEffect.name.startswith("Speed"):
                if curEffect.name.endswith("+"):
                    type = "Buff"
                else:
                    type = "Debuff"
                amount = int(curEffect.amount)
                newSpeedFunc = functools.partial(rSpellSpeed, amount, type)
                toAdd = lambda caster, target : newSpeedFunc(caster, target)
            elif curEffect.name == "Heal HP":
                amount = int(curEffect.amount)
                newHPFunc = functools.partial(castHeal, amount)
                toAdd = lambda caster, target : newHPFunc(caster, target)
            elif curEffect.name == "Heal MP":
                amount = int(curEffect.amount)
                newMPFunc = functools.partial(restoreMana, amount)
                toAdd = lambda caster, target : newMPFunc(caster, target)
            elif curEffect.name == "Cure poison":
                amount = int(curEffect.amount)
                toAdd = lambda caster, target : rSpellRemoveBuff("poisoned", caster, target)
            elif curEffect.name == "Cure fire":
                amount = int(curEffect.amount)
                toAdd = lambda caster, target : rSpellRemoveBuff("burning", caster, target)
            else:
                if DEBUG:
                    message("ERROR : CANNOT CONVERT EFFECT {}".format(curEffect.name), colors.red)
                toAdd = doNothing
        else:
            if DEBUG:
                message("Effect number {} is None".format(i + 1))
            toAdd = doNothing    
        funcs[i] = toAdd
            
        
    effect1 = funcs[0]
    effect2 = funcs[1]
    effect3 = funcs[2]
    color = template.color
    
    finalFunction = functools.partial(rSpellExec, effect1, effect2, effect3, targetFunction, zoneFunction, color)
    return Spell(ressourceCost = template.cost, cooldown = 10, useFunction = finalFunction, ressource = template.ressource, type="Magic", magicLevel=0, name = template.name, template = template) #TO-DO : Generate values for cooldown and minimum magic level
        
    #TO-DO : Finish this
    

def learnSpell(spell, silent = False):
    if not (spell in player.Fighter.knownSpells or spell.name in player.Fighter.knownSpellsToNames or spell.name in player.Fighter.allSpellsToNames):
        player.Fighter.knownSpells.append(spell)
        if not silent:
            message("You learn " + spell.name + " !", colors.green)
    else:
        if not silent:
            message("You already know this spell")
        return "cancelled"

def unlearnSpell(spell, silent = False):
    for listedSpell in player.Fighter.knownSpells:
        if spell.name == listedSpell.name:
            player.Fighter.knownSpells.remove(listedSpell)
            if not silent:
                message('You forget ' + spell.name + '!', colors.red)
            return
    for listedSpell in player.Fighter.spellsOnCooldown:
        if spell.name == listedSpell.name:
            player.Fighter.spellsOnCooldown.remove(listedSpell)
            if not silent:
                message('You forget ' + spell.name + '!', colors.red)
            return
    if not silent:
        message('You did not know this spell.', colors.white)
    return 'cancelled'
                
### GENERIC SPELLS ###

def castApplyBuff(buff, caster = None, target = None):
    if caster is None:
        caster = player
    buff.applyBuff(caster)

def castRegenMana(regenAmount, caster = None, target = None):
    if caster is None or caster == player:
        caster = player
    if caster.Fighter.MP != caster.Fighter.maxMP:
        caster.Fighter.MP += regenAmount
        regened = regenAmount
        if caster.Fighter.MP > caster.Fighter.maxMP:
            overflow = caster.Fighter.maxMP - caster.Fighter.MP
            regened = regenAmount + overflow
            caster.Fighter.MP = caster.Fighter.maxMP
        message(caster.name.capitalize() + " recovered " + str(regened) + " MP.", colors.green)
    else:
        message(caster.name.capitalize() + "'s MP are already maxed out")
        return "cancelled"

def castDarkRitual(regen, damage, caster = None, target = None):
    if caster is None or caster == player:
        caster = player
    message(caster.name.capitalize() + ' takes ' + str(damage) + ' damage from the ritual !', colors.red)
    castRegenMana(regen, caster)

def castHeal(healAmount = 10, caster = None, target = None):
    if caster is None or caster == player:
        caster = player
    if caster.Fighter.hp == caster.Fighter.maxHP:
        message(caster.name.capitalize() + ' is already at full health')
        return 'cancelled'
    else:
        message(caster.name.capitalize() + ' is healed for {} HP !'.format(healAmount), colors.light_green)
        caster.Fighter.heal(healAmount)

def castLightning(caster = None, monsterTarget = player):
    if caster is None or caster == player:
        caster = player
        target = closestMonster(LIGHTNING_RANGE)
    elif caster.distanceTo(monsterTarget) <= LIGHTNING_RANGE:
        target = monsterTarget
    if target is None:
        message(caster.name.capitalize() + "'s magic fizzles: there is no enemy near enough to strike", colors.red)
        return 'cancelled'
    else:
        dmgTxtFunc = lambda damageTaken: target.Fighter.formatRawDamageText(damageTaken, 'A lightning bolt strikes {} with a heavy thunder ! It is shocked and suffers {}.', colors.light_blue, 'Your spell has no effect on {}.', colors.grey)
        target.Fighter.takeDamage({'lightning': LIGHTNING_DAMAGE}, caster.name + "'s lightning spell", damageTextFunction = dmgTxtFunc)

def castConfuse(caster = None, monsterTarget = None):
    if caster is None or caster == player:
        caster = player
        message('Choose a target for your spell, press Escape to cancel.', colors.light_cyan)
        target = targetMonster(maxRange = CONFUSE_RANGE)
        if target is None:
            message('Invalid target.', colors.red)
            return 'cancelled'
        old_AI = target.AI
        target.AI = ConfusedMonster(old_AI)
        target.AI.owner = target
        message('The ' + target.name + ' starts wandering around as he seems to lose all bound with reality.', colors.light_violet)

def castFreeze(caster = None, monsterTarget = None):
    if monsterTarget is None:
        message('Choose a target for your spell, press Escape to cancel.', colors.light_cyan)
        target = targetMonster(maxRange = None)
    else:
        target = monsterTarget
    frozen = Buff('frozen', colors.light_violet, cooldown = 4)
    if target is None:
        message('Invalid target.', colors.red)
        return 'cancelled'
    if not 'frozen' in convertBuffsToNames(target.Fighter):
        frozen.applyBuff(target)
    else:
        message("The " + target.name + " is already frozen.")
        return 'cancelled'
    
def castFireball(radius = 3, damage = 24, shotRange = 4, caster = None, monsterTarget = player):
    global explodingTiles
    if caster is None or caster == player:
        caster = player
        message('Choose a target for your spell, press Escape to cancel.', colors.light_cyan)
        target = targetTile(maxRange = shotRange, styleAOE = 'circle', rangeAOE=radius)
    else:
        if caster.distanceTo(monsterTarget) <= shotRange:
            target = (monsterTarget.x, monsterTarget.y)
        else:
            line = tdl.map.bresenham(caster.x, caster.y, monsterTarget.x, monsterTarget.y)
            counter = 0
            for tile in line:
                (tx, ty) = line[counter]
                if tileDistance(caster.x, caster.y, tx, ty) > shotRange:
                    target = (tx, ty)
                    break
                else:
                    counter += 1
    radmax = radius + 2
    if target == 'cancelled':
        message('Spell casting cancelled')
        return target
    else:
        (tx,ty) = target
        (targetX, targetY) = projectile(caster.x, caster.y, tx, ty, '*', colors.flame, passesThrough=True)
        #TODO : Make where the projectile lands actually matter (?)
        for obj in objects:
            if obj.distanceToCoords(targetX, targetY) <= radius and obj.Fighter:
                damageTaken = obj.Fighter.takeDamage({'fire': damage}, caster.name + "'s fireball spell")
                applyBurn(obj)
                if obj != player:
                    message('{} gets burned for {} damage !'.format(obj.name.capitalize(), damageTaken['fire']), colors.light_blue)
                else:
                    message('You get burned for {} damage !'.format(damageTaken['fire']), colors.orange)
        for x in range(targetX - radmax, targetX + radmax):
            for y in range(targetY - radmax, targetY + radmax):
                if tileDistance(targetX, targetY, x, y) <= radius and not myMap[x][y].block_sight:
                    explodingTiles.append((x,y))
        explode()

def castFlamethrower(caster = None, monsterTarget = None, shotRange = 4, damage = 8):
    if caster is None or caster == player:
        caster = player
        targetZone = targetTile(SIGHT_RADIUS, AOE = True, rangeAOE = shotRange, styleAOE = 'cone', returnAOE = True)
        if targetZone != 'cancelled':
            affectedMonsters = []
            
            for object in objects:
                if (object.x, object.y) in targetZone and object.Fighter and object != caster:
                    affectedMonsters.append(object)
            for monster in affectedMonsters:
                damageDict = {'fire': damage}
                dmgTxtFunc = lambda damageTaken: object.Fighter.formatRawDamageText(damageTaken, '{} is burnt for {}!', colors.red, '', colors.orange, True)
                monster.Fighter.takeDamage(damageDict, "{}'s flamethrower".format(player.name), damageTextFunction = dmgTxtFunc)
                applyBurn(monster, 100)
            explodingTiles.extend(targetZone)
            explode(colors.flame)
        else:
            return 'didnt-take-turn'

def castShield(caster = None, monsterTarget = None, shieldType = 'Fire', explode = False):
    if caster is None:
        caster = player
    if caster == player:
        fromTrait = {'Fire': ''}
        #traitAmount = 
    #if shieldType == 'Fire':
        #buff = Buff('Fire shielded', colors.flame, cooldown = 10, power = )

def castArmageddon(radius = 4, damage = 80, caster = None, monsterTarget = None):
    global FOV_recompute
    if caster is None or caster == player:
        caster = player
    message('As you begin to read the scroll, the runes inscribed on it start emitting a very bright crimson light. Continue (Y/N)', colors.dark_red)
    FOV_recompute = True
    Update()
    tdl.flush()
    invalid = True
    while invalid:
        key = tdl.event.key_wait()
        if key.keychar.upper() in ('Y', 'N', 'SHIFT'):
            if key.keychar.upper() == 'N':
                message('Good idea.', colors.dark_red)
                FOV_recompute = True
                Update()
                return 'cancelled'
            elif key.keychar.upper() == 'Y':
                invalid = False
        else:
            message('Please press a valid key (Y or N)')
            FOV_recompute = True
            Update()
            tdl.flush()
            
    radmax = radius + 2
    global explodingTiles
    global gameState
    for x in range(player.x - radmax, player.x + radmax):
        for y in range(player.y - radmax, player.y + radmax):
            try: #Execute code below try if no error is encountered
                if tileDistance(player.x, player.y, x, y) <= radius and not myMap[x][y].unbreakable:
                    myMap[x][y].applyGroundProperties(explode = True)
                    if x in range(1, MAP_WIDTH-1) and y in range(1,MAP_HEIGHT - 1):
                        explodingTiles.append((x,y))
                    for obj in objects:
                        if obj.Fighter and obj.x == x and obj.y == y: 
                            try:
                                dmgTxtFunc = lambda damageTaken: obj.Fighter.formatRawDamageText(damageTaken, '{} smited for {}!', colors.white, '{} smited but it has no effect.', colors.white, True)
                                damageTaken = obj.Fighter.takeDamage({'fire': damage}, caster.name + "'s armaggedon spell", damageTextFunction = dmgTxtFunc) 
                            except AttributeError: #If it tries to access a non-existing object (aka outside of the map)
                                continue
            except IndexError: #If an IndexError is encountered (aka if the function tries to access a tile outside of the map), execute code below except
                continue   #Go to next loop iteration and ignore the problematic value     
    #Display explosion eye-candy, this could get it's own function
    for x in range(player.x - radmax, player.x + radmax):
        for y in range(player.y - radmax, player.y + radmax):
            try:
                myMap[x][y].clearance = checkTileClearance(myMap, x, y)
            except IndexError:
                pass
    explode()
            
def stealMoneyAndDamage(initiator, target, amount):
    # To call, add to attackFunctions : "lambda ini, target : stealMoneyAndDamage(ini, target, [ENTER_DESIRED_AMOUNT_HERE])"
    def actuallySteal(initiator, amountStolen):
        target.Player.money -= amountStolen
        addCoef = round(random.uniform(0, 0.8), 3)
        toAdd = round(amountStolen * addCoef)
        print("To add = {} (coef = {})".format(toAdd, addCoef))
        initiator.lootFunction[0].Item.amount += toAdd
        message("{} has stolen {} of your gold coins !".format(initiator.owner.name.capitalize(), amountStolen), colors.red)
    leftToSteal = round(amount)
    if target.Player.money >= leftToSteal:
        actuallySteal(initiator, amount)
    else:
        leftToSteal -= target.Player.money
        actuallySteal(initiator, target.Player.money)
        dmgTxtFunc = lambda damageTaken: initiator.formatAttackText(target, True, False, damageTaken)
        target.Fighter.takeDamage({'physical': leftToSteal // 10}, damageSource = 'greedy fiend', damageTextFunction = dmgTxtFunc)
        #message("You take {} damage from {} !".format(damageTaken['physical'], initiator.owner.name), colors.red)

def castPlaceIceWall(caster = None, monsterTarget = None):
    if caster is None or caster == player:
        caster = player
        goalX, goalY = targetTile(10)
        if (goalX, goalY) != 'cancelled':
            iceWall = TileBuff('ice wall', fg = colors.lighter_azure, bg = colors.lighter_sky, char = '#', cooldown = 10, blocksTile = True)
            iceWall.applyTileBuff(goalX, goalY)

def castBlizzard(caster = None, monsterTarget = None, shotRange = 10, tileBuffCD = 20):
    def continuousFreeze(tile, chance = 60):
        for object in objects:
            if object != player and (object.x, object.y) == (tile.x, tile.y) and object.Fighter:
                if randint(1, 100) <= chance:
                    frozen = Buff('frozen', colors.light_violet, cooldown = 4)
                    frozen.applyBuff(object)
                else:
                    slowed = Buff('slowed', colors.light_violet, cooldown = 3, moveSpeed = 50)
                    slowed.applyBuff(object)
    
    if caster is None or caster == player:
        caster = player
        orig = targetSelf(caster, lambda caster, target: areaOfEffect(caster, target, shotRange))
        if orig == 'cancelled':
            return 'didnt-take-turn'
        for (x, y) in areaOfEffect(orig, caster, shotRange):
            blizz = TileBuff('blizzard', colors.light_cyan, colors.light_violet, chr(176), cooldown = tileBuffCD, continuousFunc = [continuousFreeze])
            try:
                if not myMap[x][y].wall and not myMap[x][y].door and not myMap[x][y].chasm:
                    blizz.applyTileBuff(x, y)
            except IndexError:
                print('tile is out of map')

placeIceWall = Spell(ressourceCost=0, cooldown=0, useFunction=castPlaceIceWall, name = 'Place ice wall') 
fireball = Spell(ressourceCost = 7, cooldown = 5, useFunction = castFireball, name = "Fireball", ressource = 'MP', type = 'Fire', magicLevel = 1, arg1 = 1, arg2 = 12, arg3 = 4)
heal = Spell(ressourceCost = 15, cooldown = 12, useFunction = castHeal, name = 'Heal self', ressource = 'MP', type = 'Magic', magicLevel = 2, arg1 = 20)
darkPact = Spell(ressourceCost = DARK_PACT_DAMAGE, cooldown = 8, useFunction = castDarkRitual, name = "Dark ritual", ressource = 'HP', type = "Occult", magicLevel = 2, arg1 = 5, arg2 = DARK_PACT_DAMAGE)
lightning = Spell(ressourceCost = 10, cooldown = 7, useFunction = castLightning, name = 'Lightning bolt', ressource = 'MP', type = 'Air', magicLevel = 3)
confuse = Spell(ressourceCost = 5, cooldown = 4, useFunction = castConfuse, name = 'Confusion', ressource = 'MP', type = 'Dark', magicLevel = 1)
ice = Spell(ressourceCost = 9, cooldown = 5, useFunction = castFreeze, name = 'Ice bolt', ressource = 'MP', type = 'Water', magicLevel = 2)
blizzard = Spell(ressourceCost = 40, cooldown = 80, useFunction = castBlizzard, name = 'Blizzard', ressource = 'MP', type = 'Water')
flamethrower = Spell(ressourceCost = 5, cooldown = 20, useFunction = castFlamethrower, name = 'Flamethrower', ressource  ='MP', type = 'Fire')

### GENERIC SPELLS ###
### CLASS SPECIFIC SPELLS ###

def castEnrage(enrageTurns, caster = None, monsterTarget = None):
    if caster is None or caster == player:
        caster = player
    enraged = Buff('enraged', colors.dark_red, cooldown = enrageTurns, power = 10, resistible = False)
    enraged.applyBuff(caster)

def castRessurect(shotRange = 4, caster = None, monsterTarget = None):
    global objects
    if caster is None or caster == player:
        caster = player
    target = targetTile(shotRange)
    if target == "cancelled":
        message("Spell casting cancelled")
        return target
    else:
        (x,y) = target
        ressurectable = None
        corpseType = None
        for obj in objects:
            if obj.x == x and obj.y == y and obj.name.upper().startswith("REMAINS"):
                print("Trying to rez " + obj.name)
                convName = obj.name.split()[-1]
                corpseType = convName
                print("Corpse type = " + corpseType)
                if corpseType is not None and corpseType in RESURECTABLE_CORPSES:
                    ressurectable = obj
                    break
        if not ressurectable:
            message("There are no valid corpses on this tile")
            return "cancelled"
        else:
            monster = None
            objects.remove(ressurectable)
            if corpseType == "darksoul":
                monster = createDarksoul(x, y, friendly = True, corpse = True)
            elif corpseType == "ogre":
                monster = createOgre(x, y, friendly = True, corpse = True)
            if monster is not None:
                objects.append(monster)

ressurect = Spell(ressourceCost = 10, cooldown = 15, useFunction=castRessurect, name = "Dark ressurection", ressource = 'MP', type = "Necromancy", arg1 = 4)
enrage = Spell(ressourceCost = 5, cooldown = 30, useFunction = castEnrage, name = 'Enrage', ressource = 'MP', type = 'Class', magicLevel = 0, arg1 = 10)

### CLASS SPECIFIC SPELLS ###
### RACE SPECIFIC SPELLS ###

def castEnvenom(caster = None, monsterTarget = None):
    poisoned = Buff('poisoned', colors.purple, owner = None, cooldown=randint(5, 10), continuousFunction=lambda fighter: randomDamage('poison', fighter, chance = 100, minDamage=1, maxDamage=10, dmgType={'poison': 100}))
    for equipment in equipmentList:
        if equipment.Equipment.meleeWeapon or equipment.Equipment.ranged:
            equipment.Equipment.enchant = Enchantment('envenomed', buffOnTarget=[poisoned])

def bump(x, y, monster, damage = 0, moveContactedMob = False, destroyContactedWall = False):
    inclX = x - monster.x
    inclY = y - monster.y
    incl = (inclX, inclY)
    
    continueMovement = False
    
    if not myMap[x][y].blocked:                     #if the contact is made with a mob and not a wall
        if incl == (1, 0) or incl == (-1, 0):
            possibleKnock = [[0, -1], [0, 1]]
        elif incl == (0, 1) or incl == (0, -1):
            possibleKnock = [[1, 0], [-1, 0]]
        elif incl == (1, -1) or incl == (-1, 1):
            possibleKnock = [[-1, -1], [1, 1]]
        else:
            possibleKnock = [[1, -1], [-1, 1]]
        for object in objects:
            if object.x == x and object.y == y and object.Fighter:
                contactedMobDamageBonus = 0
                if moveContactedMob:
                    continueMovement = True
                    choice = randint(0, 1)
                    newX = x + possibleKnock[choice][0]
                    newY = y + possibleKnock[choice][1]
                    otherX = x + possibleKnock[(choice-1) ** 2][0]
                    otherY = y + possibleKnock[(choice-1) ** 2][1]
                    if not isBlocked(newX, newY):
                        object.x = newX
                        object.y = newY
                    elif not isBlocked(otherX, otherY):
                        object.x = otherX
                        object.y = otherY
                    elif myMap[newX][newY].blocked:
                        myMap[newX][newY].baseBlocked = False
                        myMap[newX][newY].block_sight = False
                        myMap[newX][newY].baseCharacter = None
                        myMap[newX][newY].wall = False
                        for cx in range(newX - 1, newX + 1):
                            for cy in range(newY -1, newY + 1):
                                myMap[cx][cy].clearance = checkTileClearance(myMap, cx, cy)
                        object.x = newX
                        object.y = newY
                        contactedMobDamageBonus = randint(object.Fighter.basePower, object.Fighter.basePower*2)
                    else:
                        myMap[otherX][otherY].baseBlocked = False
                        myMap[otherX][otherY].block_sight = False
                        myMap[otherX][otherY].baseCharacter = None
                        myMap[otherX][otherY].wall = False
                        for cx in range(otherX - 1, otherX + 1):
                            for cy in range(otherY -1, otherY + 1):
                                myMap[cx][cy].clearance = checkTileClearance(myMap, cx, cy)
                        object.x = otherX
                        object.y = otherY
                        contactedMobDamageBonus = randint(object.Fighter.basePower, object.Fighter.basePower*2)
                
                #contacted mob damage
                damageDict = {'physical': damage + randint(monster.Fighter.basePower, monster.Fighter.basePower+5) + contactedMobDamageBonus}
                dmgTxtFunc = lambda damageTaken: object.Fighter.formatRawDamageText(damageTaken, '{} slammed by ' + monster.name + ' for {}!', colors.red, '', colors.white, True)
                object.Fighter.takeDamage(damageDict, "{}'s contact".format(monster.name), damageTextFunction = dmgTxtFunc)
                
                #bumping mob damage
                damageDict = {'physical': damage + randint(monster.Fighter.basePower, monster.Fighter.basePower+5)} #here weight (and thus damage) is treated as being equal to the monster's power
                dmgTxtFunc = lambda damageTaken: monster.Fighter.formatRawDamageText(damageTaken, '{} slammed into ' + object.name + ' for {}!', colors.red, '', colors.white, True)
                monster.Fighter.takeDamage(damageDict, "{}'s contact".format(object.name), damageTextFunction = dmgTxtFunc)
                break
    else:
        if destroyContactedWall:
            myMap[x][y].baseBlocked = False
            myMap[x][y].block_sight = False
            myMap[x][y].baseCharacter = None
            myMap[x][y].wall = False
            monster.x = x
            monster.y = y
                
        #bumping mob damage
        damageDict = {'physical': damage + randint(monster.Fighter.basePower, monster.Fighter.basePower*2)}
        dmgTxtFunc = lambda damageTaken: monster.Fighter.formatRawDamageText(damageTaken, '{} slammed into the wall for {}!', colors.red, '', colors.white, True)
        monster.Fighter.takeDamage(damageDict, "wall contact".format(monster.name), damageTextFunction = dmgTxtFunc)
        
    return continueMovement

def knockBack(origX, origY, target, KBrange=1, stun=True, stunCD = 2, damage = 0, moveContactedMob = False, destroyContactedWall = False):
    destX, destY = target.x, target.y
    dx, dy = destX - origX, destY - origY
    line = tdl.map.bresenham(destX, destY, destX + dx, destY + dy)
    newLine = []
    del line[0]
    KBrange+=1
    if 1 <= len(line) < KBrange:
        dx = destX - origX
        dy = destY - origY
        (x, y) = line[len(line) - 1]
        while len(newLine) < KBrange:
            newX = x + dx
            newY = y + dy
            tempLine = tdl.map.bresenham(x, y, newX, newY)
            dx = newX - x
            dy = newY - y
            x = newX
            y = newY
            del tempLine[0]
            newLine.extend(tempLine)
            if newX >= MAP_WIDTH or newY >= MAP_HEIGHT or newX <= 0 or newY <= 0:
                break
    line.extend(newLine)
    while len(line) > KBrange:
        del line[len(line)-1]
    
    print('Knockback:', 'origin:', origX, origY, 'target:', target.x, target.y, line)
    for (x, y) in line:
        dx = x - target.x
        dy = y - target.y
        if isBlocked(x, y) and not bump(x, y, target, damage, moveContactedMob, destroyContactedWall):
            break
        target.move(dx, dy)
        animStep(.01)
    if stun:
        stunned = Buff('stunned', colors.yellow, cooldown = stunCD)
        stunned.applyBuff(target)
    

def castKnockback(caster = None, monsterTarget = None, abilityRange = 1, KBrange = 1, damage = randint(2, 7)):
    if caster is None or caster == player:
        caster = player
        melee = False
        if abilityRange == 1:
            melee = True
        target = targetMonster(abilityRange, melee = melee)
    if target:
        dmgTxtFunc = lambda damageTaken: target.Fighter.formatRawDamageText(damageTaken, 'You ram into {} for {}!', colors.yellow, 'You ram into {} for no damage.', colors.grey)
        target.Fighter.takeDamage({'physical': damage}, 'player', armored = True, damageTextFunction = dmgTxtFunc)
        #dx = target.x - caster.x
        #dy = target.y - caster.y
        #for kb in range(KBrange):
        #    target.move(dx, dy)
        knockBack(caster.x, caster.y, target, KBrange)
        return
    else:
        return 'cancelled'

def castMovement(caster = None, monsterTarget = None, tileRange = 4, ignoresChasm = True):
    if caster is None or caster == player:
        caster = player
        line = targetTile(tileRange, True, returnBresenham=True)
    if line != 'cancelled':
        if caster == player:
            message('You leap!', colors.amber)
        formerFlight = caster.flying
        if ignoresChasm:
            caster.baseFlying = True
        for (nextX, nextY) in line:
            caster.moveTo(nextX, nextY)
            animStep(0.01)
            if isBlocked(nextX, nextY):
                break
        caster.baseFlying = formerFlight
        return
    else:
        return 'cancelled'

def removeFlightBuff(fighter, spellNameToLearn):
    allSpells = []
    allSpells.extend(player.Fighter.knownSpells)
    allSpells.extend(player.Fighter.spellsOnCooldown)
    for spell in allSpells:
        if spell.name == 'Stop Flying':
            unlearnSpell(spell, True)
            break
    print(spellNameToLearn)
    for spell in fighter.hiddenSpells:
        print(spell.hiddenName)
        if spell.hiddenName == spellNameToLearn:
            fighter.knownSpells.append(spell)
            fighter.hiddenSpells.remove(spell)
            spell.setOnCooldown(player.Fighter)
            break
    player.baseFlying = player.BASE_FLYING
    if myMap[player.x][player.y].chasm and not player.flying:
        temporaryBox('You fall deeper into the dungeon...')
        if branchLevel + 1 in currentBranch.bossLevels:
            nextLevel(boss = True, fall = True)
        else:
            nextLevel(fall = True)
    return

def castStopFly(caster=None, monsterTarget=None):
    if caster is None or caster == player:
        caster = player
    
    for buff in caster.Fighter.buffList:
        if buff.name == 'flying':
            buff.removeBuff()
            return

def castFly(caster=None, monsterTarget=None, ressources = {'stamina': 1}, cooldown = 99999, evasionBonus = 10, spellHiddenName = None):
    stopFlight = Spell(ressourceCost=0, cooldown=0, useFunction=castStopFly, name='Stop Flying', type='None')
    if caster is None or caster == player:
        caster = player
        learnSpell(stopFlight, True)
        for spell in player.Fighter.knownSpells:
            if spell.hiddenName == spellHiddenName:
                caster.Fighter.knownSpells.remove(spell)
                caster.Fighter.hiddenSpells.append(spell)
                break
    
    flying = Buff('flying', colors.light_azure, cooldown = cooldown, showCooldown=False, evasion = evasionBonus, flight = True,
                  removeFunction = lambda fighter : removeFlightBuff(fighter, spellHiddenName), resistible = False)
    flying.continuousFunction = lambda fighter: consumeRessource(fighter, buff = flying, ressources = ressources)
    flying.applyBuff(caster)
    return

def castExpandRoots(caster = None, monsterTarget = None, mode = 'AOE', AOERange = 3, cooldown = 5, damage = 3, regenRatio = 5, dummySpell = 'expandRootsDummy'): #or mode = 'regen'
    global FOV_recompute, myMap
    rootedTiles = []
    rootedTilesChar = []
    rooted = Buff('rooted', colors.dark_sepia, cooldown = cooldown + 3, resistible = False)
    if caster is None or caster == player:
        caster = player
        rooted.applyBuff(caster)
        if mode == 'AOE':
            for tx in range(caster.x - AOERange - 1, caster.x + AOERange + 1):
                for ty in range(caster.y - AOERange - 1, caster.y + AOERange + 1):
                    if 0 < caster.distanceToCoords(tx, ty) <= AOERange and not myMap[tx][ty].blocked and not myMap[tx][ty].chasm:
                        rootedTiles.append((tx, ty))
                        rootedTilesChar.append(myMap[tx][ty].character)
                        myMap[tx][ty].baseCharacter = "'"
            FOV_recompute = True
            Update()
            i = 0
            for (x, y) in rootedTiles:
                myMap[x][y].baseCharacter = rootedTilesChar[i]
                i += 1
            time.sleep(0.150)
            FOV_recompute = True
            Update()
            for object in objects:
                if object.Fighter and (object.x, object.y) in rootedTiles:
                    rooted = Buff('rooted', colors.dark_sepia, cooldown = cooldown, continuousFunction=lambda fighter: randomDamage(caster.name + "'s roots", fighter, 100, damage - 1, damage + 2, dmgMessage = '{} suffers {} damage from your roots!'.format(object.name.capitalize(), '{}'), dmgColor = colors.dark_sepia, msgPlayerOnly = False, dmgType={'physical': 100}))
                    rooted.applyBuff(object)
        elif mode == 'regen':
            hpRecover = round(regenRatio * caster.Fighter.maxHP/100)
            formerHP = caster.Fighter.hp
            caster.Fighter.hp += hpRecover
            if caster.Fighter.hp > caster.Fighter.maxHP:
                hpRecover = caster.Fighter.maxHP - formerHP
                caster.Fighter.hp = caster.Fighter.maxHP
            
            mpRecover = round(regenRatio * caster.Fighter.maxMP/100)
            formerMP = caster.Fighter.MP
            caster.Fighter.MP += mpRecover
            if caster.Fighter.MP > caster.Fighter.maxMP:
                mpRecover = caster.Fighter.maxMP - formerMP
                caster.Fighter.MP = caster.Fighter.maxMP
            
            stamRecover = round(regenRatio * caster.Fighter.maxStamina/100)
            formerStam = caster.Fighter.stamina
            caster.Fighter.stamina += stamRecover
            if caster.Fighter.stamina > caster.Fighter.maxStamina:
                stamRecover = caster.Fighter.maxStamina - formerStam
                caster.Fighter.stamina = caster.Fighter.maxStamina
            
            message('You recover {} HP, {} MP and {} stamina thanks to the nutrients of the ground!'.format(str(hpRecover), str(mpRecover), str(stamRecover)), colors.light_green)
                
        for spell in caster.Fighter.allSpells:
            print(spell.name)
            if spell.name == 'Expand roots (damage)' or spell.name == 'Expand roots (regeneration)':
                if spell in caster.Fighter.knownSpells:
                    print('removing spell')
                    caster.Fighter.knownSpells.remove(spell)
                elif spell in caster.Fighter.spellsOnCooldown:
                    caster.Fighter.spellsOnCooldown.remove(spell)
        for dumSpell in spells:
            if dumSpell.hiddenName == dummySpell:
                learnSpell(dumSpell, True)
                dumSpell.setOnCooldown(caster.Fighter)
        
        return

def removeDemonBuff(fighter, spellNameToLearn):
    allSpells = []
    allSpells.extend(player.Fighter.knownSpells)
    allSpells.extend(player.Fighter.spellsOnCooldown)
    for spell in allSpells:
        if spell.name == 'Shift back to normal form':
            unlearnSpell(spell, True)
            break
    for spell in player.Fighter.hiddenSpells:
        if spell.hiddenName == spellNameToLearn:
            fighter.knownSpells.append(spell)
            fighter.hiddenSpells.remove(spell)
            spell.setOnCooldown(player.Fighter)
            break
    if myMap[player.x][player.y].chasm and not player.flying:
        temporaryBox('You fall deeper into the dungeon...')
        if branchLevel + 1 in currentBranch.bossLevels:
            nextLevel(boss = True, fall = True)
        else:
            nextLevel(fall = True)
    return

def castStopDemon(caster=None, monsterTarget=None):
    if caster is None or caster == player:
        caster = player
    
    for buff in caster.Fighter.buffList:
        if buff.name == 'in Demon form':
            buff.removeBuff()
            return 

def castDemonForm(caster=None, monsterTarget=None, ressources = {'stamina': 2, 'HP':1, 'MP': 3}, cooldown = 99999, powerBonus = 5, armorBonus = 5, accuracyBonus = 10, evasionBonus = 10, spellHiddenName = None):
    stopDemon = Spell(ressourceCost=0, cooldown=0, useFunction=castStopDemon, name='Shift back to normal form', type='None')
    if caster is None or caster == player:
        caster = player
        learnSpell(stopDemon, True)
        for spell in player.Fighter.knownSpells:
            if spell.hiddenName == spellHiddenName:
                caster.Fighter.knownSpells.remove(spell)
                caster.Fighter.hiddenSpells.append(spell)
                break
    
    demon = Buff('in Demon form', colors.dark_flame, cooldown = cooldown, showCooldown=False, power = powerBonus, armor = armorBonus, accuracy = accuracyBonus, evasion = evasionBonus, flight = True, removeFunction = lambda fighter : removeDemonBuff(fighter, spellHiddenName), resistible = False)
    demon.continuousFunction = lambda fighter: consumeRessource(fighter, buff = demon, ressources = ressources)
    demon.applyBuff(caster)
    return

envenom = Spell(ressourceCost= 10, cooldown = 20, useFunction=castEnvenom, name = 'Envenom weapons', ressource='Stamina', type = 'Racial')
demonForm = Spell(ressourceCost=10, cooldown = 150, useFunction=lambda caster, monsterTarget: castDemonForm(caster, monsterTarget, spellHiddenName = 'demonForm'), name = 'Shift to Demon form', ressource = 'MP', type = 'Occult', hiddenName='demonForm')
expandRootsDmg = Spell(ressourceCost=6, cooldown = 100, useFunction= castExpandRoots, name = 'Expand roots (damage)', ressource = 'Stamina', type = 'Racial')
expandRootsRegen = Spell(ressourceCost=6, cooldown = 100, useFunction= lambda caster, monsterTarget: castExpandRoots(caster, monsterTarget, mode = 'regen'), name = 'Expand roots (regeneration)', ressource = 'Stamina', type = 'Racial')
expandRootsDummy = Spell(ressourceCost=0, cooldown=100, useFunction = None, name = 'Expand roots', onRecoverLearn=[expandRootsDmg, expandRootsRegen], hiddenName= 'expandRootsDummy')
insectFly = Spell(ressourceCost=4, cooldown= 50, useFunction = lambda caster, monsterTarget: castFly(caster, monsterTarget, spellHiddenName = 'insectFly'), name = 'Fly', ressource='Stamina', type = 'Racial', hiddenName='insectFly')
leap = Spell(ressourceCost=5, cooldown = 30, useFunction=castMovement, name = 'Leap', ressource='Stamina', type = 'Racial')
ram = Spell(ressourceCost=15, cooldown = 20, useFunction=castKnockback, name = 'Ram', ressource = 'Stamina', type = 'Racial')

### RACE SPECIFIC SPELLS ###
### TRAITS UNLOCKABLE SPELLS ###

def castMultipleAttacks(caster = None, monsterTarget = None, attacksNum = 3):
    target = None
    if caster is None or caster == player:
        caster = player
        targetCoords = targetTile(1, melee = True)
        if targetCoords != 'cancelled':
            for object in objects:
                if (object.x, object.y) == targetCoords and object.Fighter:
                    target = object
        else: return 'didnt-take-turn'
    else:
        target = monsterTarget
    if not target:
        return
    for attack in range(attacksNum):
        caster.Fighter.attack(target, fromFreeAtk = True)
    return

def castMultipleShots(caster = None, monsterTarget = None, attacksNum = 3):
    if caster is None or caster == player:
        caster = player
        weapon = None
        for wep in getEquippedInHands():
            if wep.Equipment.ranged and 'light' in wep.Equipment.type:
                weapon = wep.Equipment
                break
        if weapon:
            line = targetTile(weapon.maxRange, showBresenham=True, returnBresenham = True)
            if line == 'cancelled':
                return 'didnt-take-turn'
        else:
            message('You have no weapons able to shoot volleys.')
            return 'didnt-take-turn'
        for attack in range(attacksNum):
            newLine = copy(line)
            weapon.shoot(newLine, False)
            
    elif caster.Ranged:
        for attack in range(attacksNum):
            caster.Ranged.shoot(monsterTarget)
    return

def castSeismicSlam(caster, monsterTarget, AOErange = 6, damage = 10, stunCooldown = 4):
    if caster is None or caster == player:
        caster = player
        targetZone = targetTile(SIGHT_RADIUS, AOE = True, rangeAOE = AOErange, styleAOE = 'cone', returnAOE = True)
        if targetZone != 'cancelled':
            affectedMonsters = []
            
            for object in objects:
                if (object.x, object.y) in targetZone and object.Fighter and object != caster:
                    affectedMonsters.append(object)
            for monster in affectedMonsters:
                knockBack(caster.x, caster.y, monster, KBrange=2, stun=True, stunCD = stunCooldown)
                monster.Fighter.takeDamage({'physical': damage}, armored = True, damageSource = 'player')
        else:
            return 'didnt-take-turn'

def castShadowStep(caster, monsterTarget, rangeTP = 10):
    if caster is None:
        caster = player
    detected = checkPlayerDetected()
    if not detected:
        goalTile = targetTile(rangeTP)
        if goalTile == 'cancelled':
            return 'didnt-take-turn'
        else:
            (goalX, goalY) = goalTile
            if not myMap[goalX][goalY].blocked and not myMap[goalX][goalY].chasm:
                player.x = goalX
                player.y = goalY
                return
            else:
                message("Cannot teleport there !", colors.red)
                return 'didnt-take-turn'
    else:
        message("You can't use Shadow step when detected!", colors.red)
        return 'didnt-take-turn'

def castThrowEnemy(caster, monsterTarget, rangeThrow = 6):
    if caster is None or caster == player:
        caster = player
        targetCoords = targetTile(1, melee = True)
        if targetCoords != 'cancelled':
            for object in objects:
                if (object.x, object.y) == targetCoords and object.Fighter:
                    target = object
                    break
            else:
                return 'didnt-take-turn'
        else: return 'didnt-take-turn'
        
        throwCoords = targetTile(rangeThrow, showBresenham = True, returnBresenham = True)
        if throwCoords == 'cancelled':
            return 'didnt-take-turn'
        for (x, y) in throwCoords:
            if isBlocked(x, y) and not bump(x, y, target, caster.Fighter.basePower):
                break
            target.x, target.y = x, y
            animStep()

def castCharge(caster = None, target = None, line = None, drag = False, freeAtk = True, maxRange = 10, useWeight = True):
    global FOV_recompute
    if caster is None:
        caster = player
    if caster == player:
        if not line:
            message('Choose a target for your charge.', colors.cyan)
            line = targetTile(maxRange, showBresenham=True, returnBresenham = True)
        if line == "cancelled":
            FOV_recompute = True
            #message('Invalid target.')
            return 'didnt-take-turn'
        else:
            try:
                line.remove((player.x, player.y))
            except:
                print('player coords not in shooting line')
        if drag:
            (firstX, firstY)= line[0]
            inclX = firstX - player.x
            inclY = firstY - player.y
            incl = (inclX, inclY)
            print(incl)
            if incl == (1, 0) or incl == (-1, 0):
                possibleKnock = [[0, -1], [0, 1]]
            elif incl == (0, 1) or incl == (0, -1):
                possibleKnock = [[1, 0], [-1, 0]]
            elif incl == (1, -1) or incl == (-1, 1):
                possibleKnock = [[-1, -1], [1, 1]]
            else:
                possibleKnock = [[1, -1], [-1, 1]]
            print(possibleKnock)
            dragging = False
            dragged = None
            bonus = 0
            for i in range(len(line)):
                (x, y) = line.pop(0)
                try:
                    (pinnedX, pinnedY) = line[0]
                except:
                    pinnedX = x + inclX
                    pinnedY = y + inclY
                for object in objects:
                    if object.x == x and object.y == y and object.Fighter and not object == player:
                        if not dragging:
                            dragging = True
                            dragged = object
                            message('You pin {}!'.format(object.name.capitalize()), colors.red)
                            dmgTxtFunc = lambda damageTaken: player.Fighter.formatAttackText(dragged, True, False, damageTaken, '{} {}tackle{} {} for {}!', '{} tackle{} {} but it has no effect.')
                        elif not object == dragged:
                            choice = randint(0, 1)
                            newX = x + possibleKnock[choice][0]
                            newY = y + possibleKnock[choice][1]
                            otherX = x + possibleKnock[(choice-1) ** 2][0]
                            otherY = y + possibleKnock[(choice-1) ** 2][1]
                            if not isBlocked(newX, newY):
                                object.x = newX
                                object.y = newY
                            elif not isBlocked(otherX, otherY):
                                object.x = otherX
                                object.y = otherY
                            else:
                                myMap[newX][newY].baseBlocked = False
                                myMap[newX][newY].block_sight = False
                                myMap[newX][newY].baseCharacter = None
                                myMap[newX][newY].wall = False
                                for cx in range(newX - 1, newX + 1):
                                    for cy in range(newY -1, newY + 1):
                                        myMap[cx][cy].clearance = checkTileClearance(myMap, cx, cy)
                                object.x = newX
                                object.y = newY
                                damageDict = player.Fighter.computeDamageDict(randint(player.Fighter.power - 5, player.Fighter.power + 5))
                                dmgTxtFunc = lambda damageTaken: object.Fighter.formatRawDamageText(damageTaken, '{} slammed into the wall for {}!', colors.red, '{} is slammed into the wall but it has no effect', colors.white, True)
                                object.Fighter.takeDamage(damageDict, "{}'s charge".format(player.name), damageTextFunction = dmgTxtFunc)
                                
                if not myMap[x][y].blocked:
                    player.x, player.y = x, y
                    if dragging:
                        dragged.x, dragged.y = pinnedX, pinnedY
                    animStep(.01)
                else:
                    if dragging:
                        print(x, y)
                        myMap[x][y].baseBlocked = False
                        myMap[x][y].block_sight = False
                        myMap[x][y].baseCharacter = None
                        myMap[x][y].wall = False
                        dragged.x = x
                        dragged.y = y
                        bonus = randint(player.Fighter.power , player.Fighter.power + 10)
                        dmgTxtFunc = lambda damageTaken: dragged.Fighter.formatRawDamageText(damageTaken, '{} slammed into the wall by the force of the charge!', colors.red, '{} slammed into the wall but it has no effect.', colors.white, True)
                    break
            if dragging:
                weight = 0
                if useWeight:
                    weight = round(getAllWeights(player, True))
                damageDict = player.Fighter.computeDamageDict(weight + bonus)
                dragged.Fighter.takeDamage(damageDict, "{}'s charge".format(player.name), damageTextFunction = dmgTxtFunc)
                
        else:
            (x, y) = line.pop(0)
            while not isBlocked(x, y) and not myMap[x][y].chasm and line:
                player.x, player.y = x, y
                animStep(0.01)
                (x, y) = line.pop(0)
            
        FOV_recompute = True
        if freeAtk:
            castMultipleAttacks(player, None, attacksNum = 1)
        return

flurry = Spell(ressourceCost=15, cooldown=50, useFunction=castMultipleAttacks, name = 'Flurry', ressource = 'Stamina', type = 'martial')
seismic = Spell(ressourceCost=20, cooldown=60, useFunction=castSeismicSlam, name='Seismic slam', ressource='Stamina', type='martial')
shadowStep = Spell(ressourceCost = 12, cooldown = 70, useFunction = castShadowStep, name = 'Shadow step', ressource = 'MP', type = 'physical')
throwEnemy = Spell(ressourceCost=23, cooldown = 40, useFunction = castThrowEnemy, name = 'Throw enemy', ressource = 'Stamina', type = 'physical')
volley = Spell(ressourceCost=20, cooldown = 50, useFunction = castMultipleShots, name = 'Volley', ressource = 'Stamina', type = 'martial')
strongCharge = Spell(ressourceCost = 50, cooldown = 100, useFunction = castCharge, name = 'Charge', ressource = 'Stamina', type = 'physical')
tackleCharge = Spell(ressourceCost = 70, cooldown = 100, useFunction = lambda caster, target: castCharge(caster, target, drag = True, freeAtk = False), name = 'Tackle', ressource = 'Stamina', type = 'physical')

### TRAITS UNLOCKABLE SPELLS ###
### DEBUG SPELLS ###

def castPlaceTag(caster = None, monsterTarget = None):
    targetedTile = targetAnyTile()
    if targetedTile != 'cancelled':
        (x, y) = targetedTile
        rawPath = os.path.join(curDir, 'tags.txt')
        filePath = pathlib.Path(os.path.join(rawPath))
        if filePath.is_file():
            textFile = open(rawPath, 'a')
        else:
            textFile = open(rawPath, 'w')
        toWrite = '(' + str(x) + ';' + str(y) + ')\n'
        textFile.write(toWrite)
        textFile.close()
    else:
        return 'cancelled'

def castDrawRectangle(caster = None, monsterTarget = None):
    startingTile = targetAnyTile()
    if startingTile != 'cancelled' :
        (startingX, startingY) = startingTile
        endTile = targetAnyTile(startingX, startingY, True)
        if endTile != 'cancelled':
            (endX, endY) = endTile
            rWidth = endY - startingY
            rHeight = endX - startingX
            rawPath = os.path.join(curDir, 'rectangles.txt')
            filePath = pathlib.Path(os.path.join(rawPath))
            if filePath.is_file():
                textFile = open(rawPath, 'a')
            else:
                textFile = open(rawPath, 'w')
            toWrite = '( Start X = ' + str(startingX) + '/ Start Y = ' + str(startingY) + '/ Width = ' + str(rWidth) + '/ Height = '+ str(rHeight) +')\n'
            textFile.write(toWrite)
            textFile.close()
        else:
            return 'cancelled'
    else:
        return 'cancelled'
        
def castAstarPath(caster = None, monsterTarget = None):
    global FOV_recompute
    (goalX, goalY) = targetAnyTile(startX = player.x, startY = player.y)
    if targetTile == 'cancelled':
        return 'cancelled'
    else:
        path = astarPath(player.x, player.y, goalX, goalY)
        print('astar path from spell:', path)
        for tile in path:
            sign = GameObject(tile.x, tile.y, '.', 'astarsign', colors.green, blocks = False, Ghost=True)
            objects.append(sign)
        FOV_recompute = True
        Update()
        return

def castTeleportTo(caster = None, monsterTarget = None):
    global FOV_recompute
    goalTile = targetAnyTile(startX = player.x, startY = player.y)
    if goalTile == ('cancelled', 'cancelled'):
        return 'cancelled'
    else:
        (goalX, goalY) = goalTile
        if not myMap[goalX][goalY].blocked and not myMap[goalX][goalY].chasm:
            player.x = goalX
            player.y = goalY
            return
        else:
            message("Cannot teleport there !", colors.red)
            return 'cancelled'
        
def castMakeTileYellow(caster = None, monsterTarget = None):
    global FOV_recompute
    (goalX, goalY) = targetAnyTile(startX = player.x, startY = player.y)
    if targetTile == 'cancelled':
        return 'cancelled'
    else:
        if not myMap[goalX][goalY].blocked and not myMap[goalX][goalY].chasm:
            tile = myMap[goalX][goalY]
            try:
                assert isinstance(tile, Tile)
            except AssertionError:
                pass #Because saving/loading breaks assertion of tiles
            tile.baseBg = colors.yellow
            tile.BG = colors.yellow
            tile.baseDark_bg = colors.dark_yellow
            tile.DARK_BG = colors.dark_yellow
            message("Made tile look yellow !")
            return
        else:
            message("Invalid tile !", colors.red)
            return 'cancelled'

def castSpawnProjectile(caster = None, monsterTarget = None):
    if caster is None:
        caster = player
    if caster == player:
        targX, targY = targetTile(SIGHT_RADIUS, True)
    else:
        targX, targY = monsterTarget.x, monsterTarget.y
    spawnedProj = Projectile(3, caster.x, caster.y, targX, targY, continues = True)
    x, y = spawnedProj.path[0]
    projObject = GameObject(x, y, spawnedProj.defineStraightChar(), name = 'projectile', color = colors.red, ProjectileComp = spawnedProj)
    objects.append(projObject)

def castConeAOE(caster = None, monsterTarget = None):
    if caster is None:
        caster = player
    
    x, y = targetTile(SIGHT_RADIUS, AOE = True, rangeAOE = 6, styleAOE = 'cone')

def resetDjik():
    global djikVisitedTiles
    djikVisitedTiles = []
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            #myMap[x][y].djikValue = None*
            tile = myMap[x][y]
            if not (tile.blocked or tile.chasm or tile.wall):
                tile.djikValue = 90000000
            tile.doNotPropagateDjik = False
    
    if bossTiles:
        for tile in bossTiles:
            tile.djikValue = 90000000
            tile.doNotPropagateDjik = False

def applyDjik(x,y, value, visible = False):
    try:
        if not isBlocked(x, y):
            myMap[x][y].djikValue = value
            if visible:
                if value >= 0:
                    if value < 10:
                        toDisp = str(value)
                    else:
                        toDisp = '+'
                else:
                    toDisp = '-'
                marker = GameObject(x,y, name = 'DEBUG : Djik Marker', char=toDisp, blocks = False, Ghost = True)
                objects.append(marker)
                markers.append(marker)
    except IndexError:
        print('Index Error')
        pass

'''
class DjikSquareMaker(threading.Thread):
    def __init__(self, x, y, value = 1):
        threading.Thread.__init__(self)
        self.x = x
        self.y = y
        self.value = value
    
    def run(self):
        turtle = GameObject(self.x, self.y, name = 'Turtle', char = None)
        turtle.y += self.value #Place the turtle Z-1 (where Z is the self.value of the variable named self.value, don't ask why -1 it doesn't work if it is not there) tiles higher than the center (given by the x and y variables)
        for i in range(self.value): #Move Z tiles left and apply wanted Djikstra self.value to them
            applyDjik(turtle.x, turtle.y, self.value, False)
            if not turtle.x < 0:
                turtle.x -= 1
        applyDjik(turtle.x, turtle.y, self.value, False)
        for loop in range(2): #Move twice 2Z times down and apply self.value to tiles
            for innerLoop in range(self.value):
                applyDjik(turtle.x, turtle.y, self.value, False)
                turtle.y -= 1
        applyDjik(turtle.x, turtle.y, self.value, False)
        #turtle.y -= 1 #Move once more down
        applyDjik(turtle.x, turtle.y, self.value, False)
        for otherLoop in range(2): #Move 2Z times right
            for otherInnerLoop in range(self.value):
                applyDjik(turtle.x, turtle.y, self.value, False)
                turtle.x += 1
            applyDjik(turtle.x, turtle.y, self.value, False)
        for yetAnotherLoop in range(2): #Move 2Z times up
            for yetAnotherInnerLoop in range(self.value):
                applyDjik(turtle.x, turtle.y, self.value, False)
                turtle.y += 1
            applyDjik(turtle.x, turtle.y, self.value, False)
        #turtle.y += 1
        applyDjik(turtle.x, turtle.y, self.value, False)
        for finalLoop in range(self.value): #Move Z times left
            applyDjik(turtle.x, turtle.y, self.value, False)
            turtle.x -= 1
        applyDjik(turtle.x, turtle.y, self.value, False)
        del turtle #RIP

'''
'''
def djikSquare(x, y, value = 1):
        turtle = GameObject(x, y, name = 'Turtle', char = None)
        turtle.y += value #Place the turtle Z-1 (where Z is the value of the variable named value, don't ask why -1 it doesn't work if it is not there) tiles higher than the center (given by the x and y variables)
        for i in range(value): #Move Z tiles left and apply wanted Djikstra value to them
            applyDjik(turtle.x, turtle.y, value, False)
            turtle.x -= 1
        applyDjik(turtle.x, turtle.y, value, False)
        for loop in range(2): #Move twice 2Z times down and apply value to tiles
            for innerLoop in range(value):
                applyDjik(turtle.x, turtle.y, value, False)
                turtle.y -= 1
        applyDjik(turtle.x, turtle.y, value, False)
        #turtle.y -= 1 #Move once more down
        applyDjik(turtle.x, turtle.y, value, False)
        for otherLoop in range(2): #Move 2Z times right
            for otherInnerLoop in range(value):
                applyDjik(turtle.x, turtle.y, value, False)
                turtle.x += 1
            applyDjik(turtle.x, turtle.y, value, False)
        for yetAnotherLoop in range(2): #Move 2Z times up
            for yetAnotherInnerLoop in range(value):
                applyDjik(turtle.x, turtle.y, value, False)
                turtle.y += 1
            applyDjik(turtle.x, turtle.y, value, False)
        #turtle.y += 1
        applyDjik(turtle.x, turtle.y, value, False)
        for finalLoop in range(value): #Move Z times left
            applyDjik(turtle.x, turtle.y, value, False)
            turtle.x -= 1
        applyDjik(turtle.x, turtle.y, value, False)
        del turtle #RIP

#        for marker in markers:
#            marker.clear()
#            try:
#                objects.remove(marker)
#            except ValueError:
#                pass
#            del marker

'''

def calcDjikPlayer(caster = None, target = None, profile = False):
    '''
    def doStuff(pX, pY, recursLevel = 1):
        if recursLevel < 500:
            tilesToDo = [myMap[pX - 1][pY], myMap[pX - 1][pY - 1], myMap[pX][pY - 1], myMap[pX + 1][pY -1], myMap[pX + 1][pY], myMap[pX + 1][pY + 1], myMap[pX][pY + 1], myMap[pX - 1][pY + 1]]
            for tile in tilesToDo:
                if not tile.blocked and not tile.wall and not tile.chasm:
                    if tile.djikValue is None:
                        tile.djikValue = recursLevel
                    else:
                        print("Already has value {}".format(tile.djikValue))
                        tile.doNotPropagateDjik = True
            for tilee in tilesToDo:
                if not tilee in djikVisitedTiles:
                    if not tilee.blocked and not tilee.wall and not tilee.chasm:
                        if not tile.doNotPropagateDjik:
                            print("Doing stuff at recursLevel {}".format(recursLevel))
                            doStuff(tilee.x, tilee.y, recursLevel + 1)
                        else:
                            print("Not propagating from there")
                            return
                    else:
                        print("Hit wall/chasm")
                    djikVisitedTiles.append(tilee)
                else:
                    print("Already visited")
        else:
            return
    
    resetDjik()
    (pX, pY) = player.x, player.y
    '''
    
        

        
    
    resetDjik()
    (pX, pY) = player.x, player.y
    myMap[pX][pY].djikValue = 0
    '''
    makers = []
    for loop in range(1, 150):
        maker = DjikSquareMaker(x = pX, y = pY, value = loop)
        makers.append(maker)
    
    for maker in makers:
        maker.start()
    for maker in makers:
        maker.join()
    '''
    
    if not profile:
        actuallyDoDjik(False)
    else:
        cProfile.run('actuallyDoDjik()', filename = os.path.join(curDir, 'djikDetail.profile'))
        
def bossFleeDjik():
    calcDjikPlayer()
    #Multiply values by -1.2 and do other stuff here
    for tile in bossTiles:
        tile.djikValue = float(tile.djikValue) * (-1.2)
    actuallyDoDjik(negative = True)
                
def getWalkableTiles():
    newList = []
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            tile = myMap[x][y]
            if tile.djikValue is not None:
                newList.append(tile)
    return newList


def actuallyDoDjik(profile = True, negative = False):
    change = True
    if not bossTiles:
        walkableTiles = getWalkableTiles()
        print("No boss room, getting walkable tiles by hand")
    else:
        walkableTiles = list(bossTiles)
        print('Found boss room !')
    while change:
        change = False
        '''
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                tile = myMap[x][y]
                if not (tile.blocked or tile.chasm or tile.wall):
                    if findNeighbouringDjikAndSetValue(x, y):
                        change = True    
        '''
        for tile in walkableTiles:
            if findTileNeighbouringDjik(tile, negative):
                change = True
                
def toggleDrawDjik(caster = None, target = None):
    global drawDjik
    drawDjik = not drawDjik

def findNeighbouringDjikAndSetValue(x,y):
    found = False
    curLow = 0
    for tile in myMap[x][y].neighbors(myMap):
        if tile.djikValue is not None and (not found or tile.djikValue < curLow):
            found = True
            curLow = tile.djikValue
    
    if myMap[x][y].djikValue - curLow >= 2:
        myMap[x][y].djikValue = curLow + 1
        return True
    else:
        return False

def findTileNeighbouringDjik(startTile, negative = False):
    found = False
    curLow = 0
    curLowTile = None
    for tile in startTile.neighbors(myMap):
        if tile is not None and not (tile.blocked or tile.chasm or tile.wall) and (not found or tile.djikValue < curLow):
            found = True
            curLow = tile.djikValue
            curLowTile = tile
    
    if startTile.djikValue - curLow >= 2: #((not negative) and startTile.djikValue - curLow >= 2): #or (negative and startTile.djikValue - curLow >= 1.2):
        startTile.djikValue = curLow + 1
        return True
    else:
        return False
        
def profileDjik(caster = None, target = None):
    cProfile.run('calcDjikPlayer()', filename = os.path.join(curDir, 'djikstra.profile'))
    
def detailedProfilerWrapperDjik(caster = None, target = None):
    calcDjikPlayer(profile = True)
    
def createHorror(caster = None, target = None):
    (x,y) = targetAnyTile(player.x, player.y)
    monster = convertMobTemplate(mobGen.generateMonster(player.level, 'horror'))
    monster.x, monster.y = x,y
    objects.append(monster)

def createSnake(caster = None, target = None):
    (x,y) = targetAnyTile(player.x, player.y)
    monster = convertMobTemplate(mobGen.generateMonster(player.level, 'snake'))
    monster.x, monster.y = x,y
    objects.append(monster)
    


drawAstarPath = Spell(ressourceCost = 0, cooldown = 1, useFunction=castAstarPath, name = 'DEBUG : Draw A* path', ressource = 'MP', type = 'Occult')
teleport = Spell(ressourceCost = 0, cooldown = 1, useFunction=castTeleportTo, name = 'DEBUG : Teleport', ressource = 'HP', type = 'Occult')
djik = Spell(ressourceCost= 0, cooldown = 1, useFunction=calcDjikPlayer, name = 'DEBUG : Calculate Djikstra Map', ressource='MP', type = 'Occult')
djikProf = Spell(ressourceCost= 0, cooldown = 1, useFunction=profileDjik, name = 'DEBUG : Calculate Djikstra Map (with Profiler)', ressource='MP', type = 'Occult')
dispDjik = Spell(ressourceCost= 0, cooldown = 1, useFunction=toggleDrawDjik, name = 'DEBUG : Draw Djikstra Map', ressource='MP', type = 'Occult')
detDjik = Spell(ressourceCost= 0, cooldown = 1, useFunction=detailedProfilerWrapperDjik, name = 'DEBUG : Calculate Djikstra Map (with detailed Profiler)', ressource='MP', type = 'Occult')
yellowify = Spell(ressourceCost= 0, cooldown = 1, useFunction=castMakeTileYellow, name = 'DEBUG : Make tile look yellow', ressource='MP', type = 'Occult')
testCone = Spell(ressourceCost= 0, cooldown = 1, useFunction=castConeAOE, name = 'DEBUG : Test cone targeting', ressource='MP', type = 'Occult')
spawnProj = Spell(ressourceCost=0, cooldown=0, useFunction=castSpawnProjectile, name = 'Spawn projectile')
placeTag = Spell(ressourceCost = 0, cooldown = 1, useFunction=castPlaceTag, name = 'DEBUG : Place tag', ressource = 'MP', type = 'Occult')
drawRect = Spell(ressourceCost = 0, cooldown = 1, useFunction=castDrawRectangle, name = 'DEBUG : Draw Rectangle', ressource = 'MP', type = 'Occult')
placeHorror = Spell(ressourceCost = 0, cooldown = 1, useFunction=createHorror, name = 'DEBUG : Place crawling horror', ressource = 'MP', type = 'Occult')
placeSnake = Spell(ressourceCost = 0, cooldown = 1, useFunction=createSnake, name = 'DEBUG : Place snake', ressource = 'MP', type = 'Occult')

### DEBUG SPELLS ###

spells.extend([fireball, heal, darkPact, enrage, lightning, confuse, ice, ressurect, placeTag, drawRect, drawAstarPath, teleport, djik, dispDjik, djikProf,
               detDjik, yellowify, ram, leap, expandRootsDmg, expandRootsDummy, expandRootsRegen, insectFly, demonForm, spawnProj, placeIceWall, testCone,
               flurry, seismic, shadowStep, throwEnemy, blizzard, flamethrower, volley, strongCharge, tackleCharge, placeHorror, placeSnake])
#_____________SPELLS_____________

#______________CHARACTER GENERATION____________
createdCharacter = {'power': 0, 'acc': 20, 'ev': 0, 'arm': 0, 'hp': 0, 'mp': 0, 'crit': 0, 'stren': 0, 'dex': 0, 'vit': 0, 'will': 0, 'ap': 0, 
                    'powLvl': 0, 'accLvl': 0, 'evLvl': 0, 'armLvl': 0, 'hpLvl': 0, 'mpLvl': 0, 'critLvl': 0, 'strLvl': 0, 'dexLvl': 0, 'vitLvl': 0, 'willLvl': 0, 'apLvl': 0,
                    'spells': [], 'load': 45.0, 'stealth': 0, 'stamina': 0, 'stamLvl': 0,
                    'dmgTypes': {'physical': 100}, 'resistances': {'physical': 0, 'poison': 0, 'fire': 0, 'cold': 0, 'lightning': 0, 'light': 0, 'dark': 0, 'none': 0},
                    'attackFuncs': [], 'buffsOnAttack': []}

class Trait():
    '''
    Actually used for everything in the character creation, from race to skills etc
    '''
    def __init__(self, name, description, type, x = 0, y = 0, underCursor = False, selectable = True, selected = False, allowsSelection = [], amount = 0, maxAmount = 1, tier = 1, power = (0, 0), acc = (0, 0), ev = (0, 0), arm = (0, 0), hp = (0, 0), mp = (0, 0), crit = (0, 0), stren = (0, 0), dex = (0, 0), vit = (0, 0), will = (0, 0), spells = None, load = 0, ap = (0, 0), stealth = 0, stam = (0, 0), bonusSkill = [], dmgTypes = {}, resistances = {}, critMult = 0, attackFuncs = [], buffsOnAttack = [], rangedAtkFuncs = []):
        self.name = name
        self.desc = description
        self.type = type
        self.x = x
        self.y = y
        self.underCursor = underCursor
        self.selectable = selectable
        self.selected = selected
        self.allowsSelection = allowsSelection
        self.amount = amount
        self.maxAmount = maxAmount
        self.power, self.powPerLvl = power
        self.acc, self.accPerLvl = acc
        self.ev, self.evPerLvl = ev
        self.arm, self.armPerLvl = arm
        self.hp, self.hpPerLvl = hp
        self.mp, self.mpPerLvl = mp
        self.crit, self.critPerLvl = crit
        self.stren, self.strPerLvl = stren
        self.dex, self.dexPerLvl = dex
        self.vit, self.vitPerLvl = vit
        self.will,self.willPerLvl = will
        self.ap, self.apPerLvl = ap
        self.stamina, self.stamPerLvl = stam
        self.load = load
        self.stealth = stealth
        self.spells = spells
        self.tier = tier
        self.owner = None
        for skill in self.allowsSelection:
            skill.owner = self
        self.bonusSkill = bonusSkill
        self.isBonus = False
        self.unlockables = []
        self.dmgTypes = dmgTypes
        self.resistances = resistances
        self.critMult = critMult
        self.attackFuncs = attackFuncs
        self.buffsOnAttack = buffsOnAttack #[[chance, name]]
        self.rangedAtkFuncs = rangedAtkFuncs
    
    def description(self):
        wrappedText = textwrap.wrap(self.desc, 25)
        line = 0
        for lines in wrappedText:
            line += 1
            drawCentered(cons = root, y = 11 + line, text = lines, fg = colors.white, bg = None)
    
    def applyBonus(self, charCreation = True, unlockSelection = True):
        if charCreation:
            global createdCharacter
            if self.amount < self.maxAmount:
                createdCharacter['power'] += self.power
                createdCharacter['acc'] += self.acc
                createdCharacter['ev'] += self.ev
                createdCharacter['arm'] += self.arm
                createdCharacter['hp'] += self.hp
                createdCharacter['mp'] += self.mp
                createdCharacter['crit'] += self.crit
                createdCharacter['stren'] += self.stren
                createdCharacter['dex'] += self.dex
                createdCharacter['vit'] += self.vit
                createdCharacter['will'] += self.will
                createdCharacter['ap'] += self.ap
                createdCharacter['stamina'] += self.stamina
                createdCharacter['stealth'] += self.stealth
                if self.spells is not None:
                    createdCharacter['spells'].extend(self.spells)
                createdCharacter['load'] += self.load
                createdCharacter['powLvl'] += self.powPerLvl
                createdCharacter['accLvl'] += self.accPerLvl
                createdCharacter['evLvl'] += self.evPerLvl
                createdCharacter['armLvl'] += self.armPerLvl
                createdCharacter['hpLvl'] += self.hpPerLvl
                createdCharacter['mpLvl'] += self.mpPerLvl
                createdCharacter['critLvl'] += self.critPerLvl
                createdCharacter['strLvl'] += self.strPerLvl
                createdCharacter['dexLvl'] += self.dexPerLvl
                createdCharacter['vitLvl'] += self.vitPerLvl
                createdCharacter['willLvl'] += self.willPerLvl
                createdCharacter['apLvl'] += self.apPerLvl
                createdCharacter['stamLvl'] += self.stamPerLvl
                
                types = createdCharacter['resistances']
                for key in list(self.resistances.keys()):
                    if key in list(types.keys()):
                        types[key] += self.resistances[key]
                    else:
                        types[key] = self.resistances[key]
            
                types = createdCharacter['dmgTypes']
                for key in list(self.dmgTypes.keys()):
                    if key in list(types.keys()):
                        types[key] = (types[key] + self.dmgTypes[key])//2
                    else:
                        types[key] = self.dmgTypes[key]//2
                
                createdCharacter['attackFuncs'].extend(self.attackFuncs)
                createdCharacter['buffsOnAttack'].extend(self.buffsOnAttack)
                
                self.amount += 1
                self.selected = True
                if unlockSelection:
                    for trait in self.allowsSelection:
                        trait.selectable = True
                for skill in self.bonusSkill:
                    skill.isBonus = True
                    skill.maxAmount += 1
                    skill.applyBonus(unlockSelection=False)
        else:
            player.Fighter.noStrengthPower += self.power
            player.Fighter.BASE_POWER += self.power
            #player.Player.levelUpStats['power'] += self.powPerLvl
            player.Fighter.noDexAccuracy += self.acc
            player.Fighter.BASE_ACCURACY += self.acc
            #player.Player.levelUpStats['acc'] += self.accPerLvl
            player.Fighter.noDexEvasion += self.ev
            player.Fighter.BASE_EVASION += self.ev
            #player.Player.levelUpStats['ev'] += self.evPerLvl
            player.Fighter.baseArmor += self.arm
            player.Fighter.BASE_ARMOR += self.arm
            #player.Player.levelUpStats['arm'] += self.armPerLvl
            player.Fighter.noVitHP += self.hp
            player.Fighter.hp += self.hp
            player.Fighter.BASE_MAX_HP += self.hp
            #player.Player.levelUpStats['hp'] += self.hpPerLvl
            player.Fighter.noWillMP += self.mp
            player.Fighter.MP += self.mp
            player.Fighter.BASE_MAX_MP += self.mp
            #player.Player.levelUpStats['mp'] += self.mpPerLvl
            player.Fighter.baseCritical += self.crit
            player.Fighter.BASE_CRITICAL += self.crit
            #player.Player.levelUpStats['crit'] += self.critPerLvl
            player.Player.baseStrength += self.stren
            player.Player.BASE_STRENGTH += self.stren
            #player.Player.levelUpStats['stren'] += self.strPerLvl
            player.Player.baseDexterity += self.dex
            player.Player.BASE_DEXTERITY += self.dex
            #player.Player.levelUpStats['dex'] += self.dexPerLvl
            player.Player.baseVitality += self.vit
            player.Player.BASE_VITALITY += self.vit
            #player.Player.levelUpStats['vit'] += self.vitPerLvl
            player.Player.baseWillpower += self.will
            player.Player.BASE_WILLPOWER += self.will
            #player.Player.levelUpStats['will'] += self.willPerLvl
            player.Fighter.baseArmorPenetration += self.ap
            player.Fighter.BASE_ARMOR_PENETRATION += self.ap
            #player.Player.levelUpStats['ap'] += self.apPerLvl
            player.Player.baseStealth += self.stealth
            player.Fighter.BASE_STAMINA += self.stamina
            player.Fighter.noConstStamina += self.stamina
            player.Fighter.critMultiplier += self.critMult
                
            types = player.Fighter.baseResistances
            for key in list(self.resistances.keys()):
                if key in list(types.keys()):
                    types[key] += self.resistances[key]
                else:
                    types[key] = self.resistances[key]
        
            types = player.Fighter.baseAttackTypes
            for key in list(self.dmgTypes.keys()):
                if key in list(types.keys()):
                    types[key] = (types[key] + self.dmgTypes[key])//2
                else:
                    types[key] = self.dmgTypes[key]//2
            
            player.Fighter.attackFunctions.extend(self.attackFuncs)
            player.Fighter.buffsOnAttack.extend(self.buffsOnAttack)
            player.Player.shootFunctions.extend(self.rangedAtkFuncs)

            self.amount += 1
            if self.spells is not None:
                for spell in self.spells:
                    learnSpell(spell)
            player.Player.baseMaxWeight += self.load
            self.selected = True
            for trait in self.allowsSelection:
                trait.selectable = True
    
    def removeBonus(self, charCreation = True, keepDependantSkills = False):
        if charCreation:
            global createdCharacter
            if self.amount > 0:
                createdCharacter['power'] -= self.power
                createdCharacter['acc'] -= self.acc
                createdCharacter['ev'] -= self.ev
                createdCharacter['arm'] -= self.arm
                createdCharacter['hp'] -= self.hp
                createdCharacter['mp'] -= self.mp
                createdCharacter['crit'] -= self.crit
                createdCharacter['stren'] -= self.stren
                createdCharacter['dex'] -= self.dex
                createdCharacter['vit'] -= self.vit
                createdCharacter['will'] -= self.will
                createdCharacter['ap'] -= self.ap
                createdCharacter['stamina'] -= self.stamina
                createdCharacter['stealth'] -= self.stealth
                if self.spells is not None:
                    for spell in self.spells:
                        createdCharacter['spells'].remove(spell)
                createdCharacter['load'] -= self.load
                createdCharacter['powLvl'] -= self.powPerLvl
                createdCharacter['accLvl'] -= self.accPerLvl
                createdCharacter['evLvl'] -= self.evPerLvl
                createdCharacter['armLvl'] -= self.armPerLvl
                createdCharacter['hpLvl'] -= self.hpPerLvl
                createdCharacter['mpLvl'] -= self.mpPerLvl
                createdCharacter['critLvl'] -= self.critPerLvl
                createdCharacter['strLvl'] -= self.strPerLvl
                createdCharacter['dexLvl'] -= self.dexPerLvl
                createdCharacter['vitLvl'] -= self.vitPerLvl
                createdCharacter['willLvl'] -= self.willPerLvl
                createdCharacter['apLvl'] -= self.apPerLvl
                createdCharacter['stamLvl'] -= self.stamPerLvl
                
                types = createdCharacter['resistances']
                for key in list(self.resistances.keys()):
                    #if key in list(types.keys()):
                    types[key] -= self.resistances[key]
                    #else:
                    #    types[key] = self.resistances[key]
            
                types = createdCharacter['dmgTypes']
                for key in list(self.dmgTypes.keys()):
                    #if key in list(types.keys()):
                    types[key] = (types[key] - self.dmgTypes[key]//2)*2
                    #else:
                    #    types[key] = self.dmgTypes[key]//2
                
                for func in self.attackFuncs:
                    try:
                        createdCharacter['attackFuncs'].remove(func)
                    except:
                        print('could not remove function from created char template:', func)
                for buff in self.buffsOnAttack:
                    try:
                        createdCharacter['buffsOnAttack'].remove(buff)
                    except:
                        print('could not remove buff on atk from created char template:', func)
                
                self.amount -= 1
                if self.amount <= 0:
                    self.selected = False
                    if self.spells is not None:
                        for spell in self.spells:
                            if spell in createdCharacter['spells']:
                                createdCharacter['spells'].remove(spell)
                    if not keepDependantSkills:
                        for trait in self.allowsSelection:
                            trait.selectable = False
                            if trait.selected: 
                                trait.amount = 0
                                trait.selected = False
                    for skill in self.bonusSkill:
                        skill.isBonus = False
                        skill.maxAmount -= 1
                        skill.removeBonus()
        else:
            player.Fighter.noStrengthPower -= self.power
            player.Fighter.BASE_POWER -= self.power
            #player.Player.levelUpStats['power'] -= self.powPerLvl
            player.Fighter.noDexAccuracy -= self.acc
            player.Fighter.BASE_ACCURACY -= self.acc
            #player.Player.levelUpStats['acc'] -= self.accPerLvl
            player.Fighter.noDexEvasion -= self.ev
            player.Fighter.BASE_EVASION -= self.ev
            #player.Player.levelUpStats['ev'] -= self.evPerLvl
            player.Fighter.baseArmor -= self.arm
            player.Fighter.BASE_ARMOR -= self.arm
            #player.Player.levelUpStats['arm'] -= self.armPerLvl
            player.Fighter.noVitHP -= self.hp
            player.Fighter.hp -= self.hp
            player.Fighter.BASE_MAX_HP -= self.hp
            #player.Player.levelUpStats['hp'] -= self.hpPerLvl
            player.Fighter.noWillMP -= self.mp
            player.Fighter.MP -= self.mp
            player.Fighter.BASE_MAX_MP -= self.mp
            #player.Player.levelUpStats['mp'] -= self.mpPerLvl
            player.Fighter.baseCritical -= self.crit
            player.Fighter.BASE_CRITICAL -= self.crit
            #player.Player.levelUpStats['crit'] -= self.critPerLvl
            player.Player.baseStrength -= self.stren
            player.Player.BASE_STRENGTH -= self.stren
            #player.Player.levelUpStats['stren'] -= self.strPerLvl
            player.Player.baseDexterity -= self.dex
            player.Player.BASE_DEXTERITY -= self.dex
            #player.Player.levelUpStats['dex'] -= self.dexPerLvl
            player.Player.baseVitality -= self.vit
            player.Player.BASE_VITALITY -= self.vit
            #player.Player.levelUpStats['vit'] -= self.vitPerLvl
            player.Player.baseWillpower -= self.will
            player.Player.BASE_WILLPOWER -= self.will
            #player.Player.levelUpStats['will'] -= self.willPerLvl
            player.Fighter.baseArmorPenetration -= self.ap
            player.Fighter.BASE_ARMOR_PENETRATION -= self.ap
            #player.Player.levelUpStats['ap'] -= self.apPerLvl
            player.Player.baseStealth -= self.stealth
            player.Fighter.noConstStamina -= self.stamina
            player.Fighter.BASE_STAMINA -= self.stamina
            player.Fighter.critMultiplier -= self.critMult
                
            types = player.Fighter.baseResistances
            for key in list(self.resistances.keys()):
                #if key in list(types.keys()):
                types[key] -= self.resistances[key]
                #else:
                #    types[key] = self.resistances[key]
        
            types = player.Fighter.baseAttackTypes
            for key in list(self.dmgTypes.keys()):
                #if key in list(types.keys()):
                types[key] = (types[key] - self.dmgTypes[key]//2)*2
                #else:
                #    types[key] = self.dmgTypes[key]//2
                
            for func in self.attackFuncs:
                try:
                    player.Fighter.attackFunctions.remove(func)
                except:
                    print('could not remove function from created char template:', func)
            for buff in self.buffsOnAttack:
                try:
                    player.Fighter.attackFunctions.remove(buff)
                except:
                    print('could not remove buff from created char template:', buff)
            for func in self.rangedAtkFuncs:
                try:
                    player.Player.shootFunctions.remove(func)
                except:
                    print('could not remove function from created char template:', func)
                
            self.amount -= 1
            player.Player.baseMaxWeight -= self.load
            if self.amount <= 0:
                self.selected = False
                if self.spells is not None:
                    for spell in self.spells:
                        unlearnSpell(spell)
                if not keepDependantSkills:
                    for trait in self.allowsSelection:
                        trait.selectable = False
                        if trait.selected:
                            player.Player.skillpoints += trait.amount 
                            trait.amount = 0
                            trait.selected = False
    
    def addTraitToPlayer(self):
        if self.type == 'skill':
            player.Player.skills.append(self)
        elif self.type == 'trait':
            player.Player.traits.append(self)
        player.Player.allTraits.append(self)
        self.applyBonus(False)
        self.selected = True
    
    def drawTrait(self, cons = root):
        if not self.underCursor:
            if self.selected:
                drawCenteredOnX(cons, self.x, self.y, self.name, fg = colors.yellow, bg = None)
            elif not self.selectable:
                drawCenteredOnX(cons, self.x, self.y, self.name, fg = colors.grey, bg = None)
            elif self.isBonus:
                drawCenteredOnX(cons, self.x, self.y, self.name, fg = colors.dark_red, bg = None)
            else:
                drawCenteredOnX(cons, self.x, self.y, self.name, fg = colors.white, bg = None)
        else:
            if self.selected:
                drawCenteredOnX(cons, self.x, self.y, self.name, fg = colors.black, bg = colors.yellow)
            elif not self.selectable:
                drawCenteredOnX(cons, self.x, self.y, self.name, fg = colors.black, bg = colors.grey)
            else:
                drawCenteredOnX(cons, self.x, self.y, self.name, fg = colors.black, bg = colors.white)
            self.description()
        
        if self.name == 'Strength' and self.type == 'attribute':
            drawCenteredOnX(cons, self.x - 10, y = self.y, text = str(10 + createdCharacter['stren']), fg = colors.white, bg = None)
        if self.name == 'Dexterity' and self.type == 'attribute':
            drawCenteredOnX(cons, self.x - 10, y = self.y, text = str(10 + createdCharacter['dex']), fg = colors.white, bg = None)
        if self.name == 'Constitution' and self.type == 'attribute':
            drawCenteredOnX(cons, self.x - 10, y = self.y, text = str(10 + createdCharacter['vit']), fg = colors.white, bg = None)
        if self.name == 'Willpower' and self.type == 'attribute':
            drawCenteredOnX(cons, self.x - 10, y = self.y, text = str(10 + createdCharacter['will']), fg = colors.white, bg = None)
        
        if self.type == 'skill' and self.tier <= 1:
            x = self.x + len(self.name)//2 + 2
            color = colors.grey
            if self.selected:
                color = colors.white
            cons.draw_str(x + 1, self.y - 2, '__', fg = color)
            cons.draw_char(x, self.y - 1, '/', fg = color)
            cons.draw_str(x, self.y, '---', fg = color)
            cons.draw_str(x, self.y + 1, chr(92) + '__', fg = color)
    
    def fullDescription(self, width):
        desc = textwrap.wrap(self.desc, width)
        stats = []
        if self.stren != 0:
            stats.append(('Strength', str(self.stren)))
        if self.dex != 0:
            stats.append(('Dexterity', str(self.dex)))
        if self.vit != 0:
            stats.append(('Constitution', str(self.vit)))
        if self.will != 0:
            stats.append(('Willpower', str(self.will)))
        if self.power != 0:
            stats.append(('Power', str(self.power)))
        if self.acc != 0:
            stats.append(('Accuracy', str(self.acc)))
        if self.ev != 0:
            stats.append(('Evasion', str(self.ev)))
        if self.arm != 0:
            stats.append(('Armor', str(self.arm)))
        if self.hp != 0:
            stats.append(('Max HP', str(self.hp)))
        if self.mp != 0:
            stats.append(('Max MP', str(self.mp)))
        if self.stamina != 0:
            stats.append(('Max Stamina', str(self.stamina)))
        if self.crit != 0:
            stats.append(('Critical', str(self.crit)))
        if self.ap != 0:
            stats.append(('Armor Penetration', str(self.ap)))
        if self.stealth != 0:
            stats.append(('Stealth', str(self.stealth)))
        
        unlock = []
        levels = []
        levelDict = {}
        for trait, level in self.unlockables:
            text = str(level) + ': ' + trait.name
            state = trait.selected
            levels.append(level)
            levelDict[level] = (text, state)
        
        levels.sort()
        for level in levels:
            unlock.append(levelDict[level])

        return desc, stats, unlock
    
    def displayTrait(self, motherWindow, fromCharCreation = False):
        global FOV_recompute, menuWindows
        
        width = TRAIT_INFO_WIDTH
        if width < len(self.name) + 3:
            width = len(self.name) + 3
        desc, stats, unlock = self.fullDescription(width - 2)
        descriptionHeight = len(desc) + len(stats) + len(unlock)
        if desc == '':
            descriptionHeight = 0
        height = descriptionHeight + 7
        #height = HEIGHT - 4
        
        if menuWindows:
            for mWindow in menuWindows:
                if not mWindow.name == 'levelUpScreen':
                    mWindow.clear()
                    print('CLEARED {} WINDOW OF TYPE {}'.format(mWindow.name, mWindow.type))
                    if mWindow.name == 'displayTrait':
                        ind = menuWindows.index(mWindow)
                        del menuWindows[ind]
                        print('Deleted')
                tdl.flush()
        FOV_recompute = True
        #if not fromCharCreation:
        #    Update()
        window = NamedConsole('displayTrait', width, height)
        print('Created disp window')
        window.clear()
        menuWindows.append(window)

        for k in range(width):
            window.draw_char(k, 0, chr(196))
        window.draw_char(0, 0, chr(218))
        window.draw_char(k, 0, chr(191))
        kMax = k
        for l in range(height):
            if l > 0:
                window.draw_char(0, l, chr(179))
                window.draw_char(kMax, l, chr(179))
        lMax = l
        for m in range(width):
            window.draw_char(m, lMax, chr(196))
        window.draw_char(0, lMax, chr(192))
        window.draw_char(kMax, lMax, chr(217))
        
        window.draw_str(1, 1, self.name + ':', fg = colors.amber, bg = None)
        for i, line in enumerate(desc):
            window.draw_str(1, 3 + i, line, fg = colors.white)
        finalI = i
        i = 0
        for i, stat in enumerate(stats):
            header, value = stat
            drawHeaderAndValue(window, 1, 5 + finalI + i, header, value, headerColor = colors.light_amber, underline = False)
        finalY = 7 + finalI + i
        for i, unlockable in enumerate(unlock):
            text, state = unlockable
            if state:
                color = colors.white
            else:
                color = colors.light_grey
            window.draw_str(1, finalY + i, text, fg = color)
        posX = WIDTH - width - 3
        motherWindow.blit(window, posX, 1, width, height, 0, 0)
        
        menuWindows.append(window)
        FOV_recompute = True
        tdl.flush()

class UnlockableTrait(Trait):
    def __init__(self, name, description, type, x = 0, y = 0, underCursor = False, selectable = False, selected = False, allowsSelection = [],
                 amount = 0, maxAmount = 1, tier = 1, power = (0, 0), acc = (0, 0), ev = (0, 0), arm = (0, 0), hp = (0, 0), mp = (0, 0), crit = (0, 0),
                  stren = (0, 0), dex = (0, 0), vit = (0, 0), will = (0, 0), spells = None, load = 0, ap = (0, 0), stealth = 0, stam = (0, 0),
                  bonusSkill = [], dmgTypes = {}, resistances = {}, critMult = 0,
                  requiredTraits = {}, attackFuncs = [], buffsOnAttack = [], rangedAtkFuncs = []): #requiredTraits = {'player level': 5, 'Light weapons': 4}
        
        Trait.__init__(self, name, description, type, x, y, underCursor, selectable, selected, allowsSelection, amount, maxAmount, tier, power, acc, ev, arm, hp, mp, crit, stren, dex, vit, will, spells, load, ap, stealth, stam, bonusSkill, dmgTypes, resistances, critMult, attackFuncs, buffsOnAttack, rangedAtkFuncs)
        self.requiredTraits = requiredTraits
    
    def checkForRequirements(self):
        if not self.selected:
            unlocked = 0
            required = list(self.requiredTraits.keys())
            
            for trait in required:
                print(trait)
                if trait == 'player level':
                    if player.level >= self.requiredTraits[trait]:
                        unlocked += 1
                elif player.Player.getTrait('skill', trait) != 'not found' and player.Player.getTrait('skill', trait).amount >= self.requiredTraits[trait]:
                    unlocked += 1
                elif player.Player.race == required:
                    unlocked += 1
                elif player.Player.getTrait('trait', trait) != 'not found':
                    unlocked += 1
            
            if unlocked == len(required):
                self.addTraitToPlayer()
                message('You gain the trait {}!'.format(self.name), colors.green)

class PlayerClass(Trait):
    def __init__(self, name, description, type, x = 0, y = 0, underCursor = False, selectable = False, selected = False, allowsSelection = [],
                 amount = 0, maxAmount = 1, tier = 1, power = (0, 0), acc = (0, 0), ev = (0, 0), arm = (0, 0), hp = (0, 0), mp = (0, 0), crit = (0, 0),
                  stren = (0, 0), dex = (0, 0), vit = (0, 0), will = (0, 0), spells = None, load = 0, ap = (0, 0), stealth = 0, stam = (0, 0),
                  bonusSkill = [], dmgTypes = {}, resistances = {}, critMult = 0, attackFuncs = [], buffsOnAttack = [],
                  trees = {}): #trees = {'class': {level: trait, etc}, 'subclass1': {level: trait, etc}, etc}
        
        Trait.__init__(self, name, description, type, x, y, underCursor, selectable, selected, allowsSelection, amount, maxAmount, tier, power, acc, ev, arm, hp, mp, crit, stren, dex, vit, will, spells, load, ap, stealth, stam, bonusSkill, dmgTypes, resistances, critMult, attackFuncs, buffsOnAttack)
        self.trees = trees
        names = self.trees.keys()
        
        self.sublcass1Name = None
        i = 0
        while not self.subclass1Name and i < len(names):
            newName = names[i]
            if newName != self.name:
                self.subclass1Name = newName
            i += 1
        
        self.sublcass2Name = None
        i = 0
        while not self.subclass2Name and i < len(names):
            newName = names[i]
            if newName != self.name and newName != self.subclass1Name:
                self.subclass2Name = newName
            i += 1
        
        self.chosenSubclass = None #will become the chosen subclass name once chosen
        
        self.uppableLevels = []
        for name in names:
            for lvl in self.tress[name].keys():
                if lvl not in self.uppableLevels:
                    self.uppableLevels.append(lvl)
        self.uppableLevels.sort()
        
        self.initTreesTraits()
    
    def initTreesTraits(self):
        names = self.trees.keys()
        maxLvl = 0
        for name in names:
            levels = self.trees[name].keys()
            innerMax = max(levels)
            if innerMax > maxLvl:
                maxLvl = innerMax
        
        width, height = CLASS_LEVEL_WIDTH, CLASS_LEVEL_HEIGHT
        xBetween = width//(len(names)+1)
        yBetween = height//(maxLvl+2)
        self.xBetween = xBetween
        self.yBetween = yBetween
        
        subclasses = [self.name, self.subclass1Name, self.subclass2Name]
        for i in range(3):
            levels = self.trees[subclasses[i]].values().sort()
            for k in range(len(levels)):
                trait = self.trees[subclasses[i]][levels[k]]
                trait.x = (1+i)*xBetween
                trait.y = (2+k)*yBetween
                if levels[k] != 1:
                    trait.selectable = False
    
    def levelUpClass(self):
        if not player.level in self.uppableLevels:
            return
        
        width, height = CLASS_LEVEL_WIDTH, CLASS_LEVEL_HEIGHT
        window = NamedConsole('classLevelUp', width, height)
        window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)
        window.clear()
        
        chosen = False
        line = 0
        column = 1
        currentTrait = None
        selected = []
        while not chosen:
            drawActualRectangle(window, width, height)
            
            names = [self.subclass1Name, self.name, self.subclass2Name]
            i = 0
            for name in names:
                color = colors.white
                if self.chosenSubclass and (name != self.chosenSubclass and name != self.name):
                    color = colors.grey
                window.draw_str(self.xBetween * (1+i) - len(name)//2, self.yBetween, name, color)
                
                j = 0
                for lvl in self.uppableLevels:
                    trait = self.trees[name][lvl]
                    color = colors.grey
                    if lvl == player.level:
                        color = colors.white
                    if trait in selected:
                        color = colors.yellow
                    if trait.selected:
                        color = colors.dark_red
                    if i == column and j == line:
                        currentTrait = trait
                        window.draw_str(self.xBetween*(1+i)-len(trait.name)//2, self.yBetween*(j+2), trait.name, fg = colors.black, bg = color)
                    else:
                        window.draw_str(self.xBetween*(1+i)-len(trait.name)//2, self.yBetween*(j+2), trait.name, fg = color)
                    
                    j+= 1
                
                i += 1
            
            x = MID_WIDTH - int(width/2)
            y = MID_HEIGHT - int(height/2)
            root.blit(window, x, y, width, height, 0, 0)
            tdl.flush()
            
            key = tdl.event.key_wait()
            if tdl.event.isWindowClosed():
                quitGame("Closed game")
            elif key.keychar.upper() == 'RIGHT':
                column += 1
                if column > 2:
                    column = 0
            elif key.keychar.upper() == 'LEFT':
                column -= 1
                if column < 0:
                    column = 2
            elif key.keychar.upper() == 'UP':
                line += 1
                if line >= len(self.uppableLevels):
                    column = 0
            elif key.keychar.upper() == 'LEFT':
                line -= 1
                if line < 0:
                    column = len(self.uppableLevels)-1
            elif key.keychar.upper() == 'ENTER':
                if currentTrait not in selected:
                    selected.append(currentTrait)
            elif key.keychar.upper() == 'BACKSPACE':
                try:
                    selected.remove(currentTrait)
                except:
                    pass
            elif key.keychar.upper() == 'ESCAPE':
                if selected:
                    for trait in selected:
                        trait.applyBonus()
                    chosen = True

def initializeTraits():
    allTraits = []
    unlockableTraits = []
    leftTraits = []
    rightTraits = []
    LEFT_X = (WIDTH // 4)
    RIGHT_X = WIDTH - (WIDTH // 4)
    RACE_Y = 11
    ATTRIBUTE_Y = 31
    TRAIT_Y = 31
    CLASS_Y = 11
    SKILL_Y = 41
    
    '''
    ## racial traits ##
    fastLearn = Trait('Fast learner', 'You are very smart and learn from your wins or losses very fast', type = 'trait', selectable = False)
    skilled = Trait('Skilled', 'You are already a skillful warrior', type = 'trait', selectable=False)
    rage = Trait('Rage', 'When low on health, you will lose all control', type = 'trait', selectable = False)
    horns = Trait('Horned', 'Your horns are very large and can be used in combats', type = 'trait', selectable = False, spells=[ram], power = (2, 0))
    carapace = Trait('Chitin carapace', 'Your natural exoskeleton is very resistant', type = 'trait', arm=(2, 0), selectable = False)
    silence = Trait('Silent walk', 'Your paws are very soft, allowing you to be very sneaky', type = 'trait', selectable = False, stealth=15)
    venom = Trait('Venomous glands', 'You are able to envenom your weapons', type = 'trait', selectable = False, spells = [envenom])
    mimesis = Trait('Mimesis', 'You can mimic your environment, making it very hard to see you', type = 'trait', selectable = False, stealth = 15)
    wild = Trait('Wild instincts', 'Your natural transformation is even more deadly', type = 'trait', selectable = False)
    optionTraits = [fastLearn, skilled, rage, horns, carapace, silence, venom, mimesis, wild]
    '''
    
    ## races ##
    human = Trait('Human', 'Humans are the most common race. They have no special characteristic, and are neither better or worse at anything. However, they are good learners and gain experience faster.', type = 'race') #, allowsSelection=[fastLearn, skilled])
    mino = Trait('Minotaur', 'Minotaurs, whose muscular bodies are topped with a taurine head, are tougher and stronger than humans, but are way less smart. They are uncontrollable and, when angered, can become a wrecking ball of muscles and thorns.', type= 'race', stren=(5, 0), dex=(-4, 0), vit=(4, 0), will=(-3, 0), spells = [ram]) #, allowsSelection=[rage, horns])
    insect = Trait('Insectoid', 'Insectoids are a rare race of bipedal insects which are stronger than human but, more importantly, very good at arcane arts. They come in all kinds of forms, from the slender mantis to the bulky beetle.', type = 'race', stren=(1, 0), dex=(-1, 0), vit=(-2, 0), will=(2, 0), spells = [insectFly]) #, allowsSelection=[carapace])
    cat = Trait('Felis', 'Felis, kinds of humanoid cats, are sneaky thieves and assassins. They usually move silently and can see in the dark.', type ='race', stren = (2, 0), vit = (-2, 0), spells = [leap], dex = (1, 0), stealth = 20) #, allowsSelection=[silence]
    rept = Trait('Reptilian', 'Reptilians are very agile but absurdly weak. Their scaled skin, however, sometimes provides them with natural camouflage, and they might use their natural venom on their daggers or arrows to make them even more deadly.', type = 'race', ev=(20, 0), stren=(-4, 0), dex=(2, 0), spells = [envenom]) #, allowsSelection=[venom, mimesis])
    demon = Trait('Demon Spawn', 'Demon spawns, a very uncommon breed of a human and a demon, are cursed with the heritage of  their demonic parents, which will make them grow disturbing mutations as they grow older and stronger.', type = 'race', spells = [demonForm])
    tree = Trait('Rootling', 'Rootlings, also called treants, are rare, sentient plants. They begin their life as a simple twig, but, with time, might become gigantic oaks.', type = 'race', stren=(-3, 0), dex=(-2, 0), vit=(-4, 0), will=(-3, 0), spells = [expandRootsDmg, expandRootsRegen])
    wolf = Trait('Werewolf', 'Werewolves are a martyred and despised race. Very tough to kill, they are naturally stronger than basic humans and unconogreably shapeshift more or less regularly. However, older werewolves are used to these transformations and can even use them to their interests.', type = 'race', stren=(2, 0), dex=(1, 0), vit=(-2, 0), will=(-4, 0)) #, allowsSelection=[wild]
    #devourer = Trait('Devourer', 'Devourers are strange, dreaded creatures from another dimension. Few have arrived in ours and even fewer have been described. These animals, half mantis, half lizard, are only born to kill and consume. Some of their breeds can even, after consuming anything - even a weapon - grow an organic replica of it.', type = 'race', vit = (-2, 0), will = (-10, 0))
    #virus = Trait('Virus ', 'Viruses are the physically weakest race, but do not base their success on their own bodies. Indeed, they are able to infect another race, making it their host and fully controllable by the virus. What is more, the virus own physical attributes, instead of applying to it directly, rather modifies the host metabolism, potentially making it stronger or tougher. However, this take-over is very harmful for the host, who will eventually die. The virus must then find a new host to continue living.', type = 'race', ev = (999, 0))
    races = [human, mino, insect, cat, rept, demon, tree, wolf]#, devourer, virus]
    allTraits.extend(races) 
    leftTraits.extend(races)
    
    counter = 0
    for race in races:
        race.x = LEFT_X
        race.y = RACE_Y + counter
        counter += 1
    
    ## attributes ##
    stren = Trait('Strength', 'Strength augments the power of your attacks', type = 'attribute', maxAmount=5, stren=(1, 0))
    dex = Trait('Dexterity', 'Dexterity augments your accuracy and your evasion', type = 'attribute', maxAmount=5, dex=(1, 0))
    const = Trait('Constitution', 'Constitution augments your maximum health and your regeneration rate.', type = 'attribute', maxAmount=5, vit=(1, 0))
    will = Trait('Willpower', 'Willpower augments your energy and the rate at which you regain it.', type = 'attribute', maxAmount=5, will=(1, 0))
    attributes = [stren, dex, const, will]
    allTraits.extend(attributes)
    leftTraits.extend(attributes)
    
    counter = 0
    for attribute in attributes:
        attribute.x = LEFT_X
        attribute.y = ATTRIBUTE_Y + counter
        counter += 1
    
    ## skills ##
    #fourthTierSkills = [fireSkill, iceSkill]
    
    light = Trait('Light weapons', '+20% damage per skillpoints with light weapons', type = 'skill', selectable = False, tier = 3, maxAmount=10)
    heavy = Trait('Heavy weapons', '+20% damage per skillpoints with heavy weapons', type = 'skill', selectable = False, tier = 3, maxAmount=10)
    lightMissile = Trait('Light ranged weapons', '+20% damage per skillpoints with light ranged weapons', type = 'skill', selectable = False, tier = 3, maxAmount=10)
    heavyMissile = Trait('Heavy ranged weapons', '+20% damage per skillpoints with heavy ranged weapons', type = 'skill', selectable = False, tier = 3, maxAmount=10)
    shield = Trait('Shield mastery', 'You trained to master shield wielding.', type = 'skill', selectable = False, tier = 3, maxAmount=10)
    armorEff = Trait('Armor efficiency', 'You know very well how to maximize the protection brought by your armor', type = 'skill', selectable = False, tier = 3, maxAmount=10)
    brawl = Trait('Brawling', 'Your consistent participation in tavern brawls have made you pretty used to unarmed combat', type = 'skill', selectable = False, tier = 3, maxAmount=10)
    dexterity = Trait('Dexterity', 'You are Dexter.', type = 'skill', selectable = False, dex=(1, 0), tier = 3, maxAmount=10)
    critical = Trait('Critical', 'You know every weaknesses of your enemies.', type = 'skill', selectable = False, crit=(3, 0), tier = 3, maxAmount=10)
    constitution = Trait('Constitution', 'You are a sturdy person', type = 'skill', hp = (15, 0), vit = (1, 0), selectable = False, tier = 3, maxAmount=10)
    hunger = Trait('Hunger management', 'You are used to starve and are now resilient to hunger.', type = 'skill', selectable=False, tier = 3, maxAmount=10)
    fireSkill = Trait('Fire', 'You master fire magic.', type = 'skill', selectable=False, tier = 3, spells = [fireball], maxAmount=10, resistances = {'fire': 5})
    iceSkill = Trait('Water', 'You master ice magic.', type = 'skill', selectable=False, tier = 3, spells = [ice], maxAmount=10, resistances = {'cold': 5})
    airSkill = Trait('Air', 'You master air magic.', type = 'skill', selectable=False, tier = 3, spells = [], maxAmount=10, resistances = {'lightning': 5})
    earthSkill = Trait('Earth', 'You master earth magic.', type = 'skill', selectable=False, tier = 3, spells = [], maxAmount=10, resistances = {'poison': 5})
    thirdTierSkills = [light, heavy, lightMissile, heavyMissile, armorEff, shield, brawl, hunger, constitution, dexterity, critical, fireSkill, iceSkill, airSkill, earthSkill]

    melee = Trait('Melee weaponry', 'You are trained to wreck your enemies at close range.', type = 'skill', selectable = False, tier = 2, allowsSelection=[light, heavy], maxAmount=10)
    ranged = Trait('Ranged weaponry', 'You shoot people in the knees.', type = 'skill', selectable = False, tier = 2, allowsSelection=[lightMissile, heavyMissile], maxAmount=10)
    armorW = Trait('Armor wearing', 'You are trained to wear several types of armor.', type = 'skill', selectable = False, tier = 2, allowsSelection=[armorEff, shield], maxAmount=10)
    endurance = Trait('Endurance', 'You are used to live in harsh conditions', type = 'skill', selectable = False, tier = 2, allowsSelection=[hunger, constitution], maxAmount=10, resistances = {'physical': 2})
    strength = Trait('Strength', 'You are as strong as a bear', type = 'skill', stren=(1, 0), selectable = False, tier = 2, maxAmount=10, allowsSelection=[brawl])
    willpower = Trait('Power of will', 'Your will is very strong', type = 'skill', mp=(5, 0), will = (1, 0), selectable = False, tier = 2, maxAmount=10)
    cunning = Trait('Cunning', 'You are cunning, and can use this to hide in the shadows in order to deliver sly but deadly attacks.', type = 'skill', selectable = False, tier = 2, allowsSelection=[dexterity, critical], maxAmount=10, stealth = 5)
    elemental = Trait('Elemental magic', 'You master the power of the four elements.', type = 'skill', selectable=False, tier = 2, allowsSelection=[fireSkill, iceSkill, airSkill, earthSkill], maxAmount=10)
    occult = Trait('Occult magic', 'The black magic cannot hide any of its dark secrets to you.', type = 'skill', selectable=False, tier = 2, maxAmount=10)
    #magic = Trait('Magic ', 'You can use the power of your mind to bind reality to your will', type = 'skill', selectable = False, tier = 2, allowsSelection=[occult, elemental], maxAmount=10)
    secondTierSkills = [melee, ranged, armorW, strength, endurance, cunning, willpower, elemental, occult]

    martial = Trait('Martial training', 'You are trained to use a wide variety of weapons', type = 'skill', acc=(10, 0), allowsSelection=[melee, ranged, armorW], maxAmount=10)
    physical = Trait('Physical training', 'You are muscular and are used to physical efforts', type = 'skill', allowsSelection=[strength, endurance, cunning], maxAmount=10, stam=(10, 0))
    mental = Trait('Mental training', 'Your mind is as fast as an arrow and as sharp as a scalpel', type = 'skill', allowsSelection=[willpower, elemental, occult], maxAmount=10)
    basicSkills = [martial, physical, mental]
    
    skills = basicSkills
    skills.extend(secondTierSkills)
    skills.extend(thirdTierSkills)
    #skills.extend(fourthTierSkills)
    
    quarterX = (WIDTH - 2)//5#6
    
    def initiateSkill(skillList, maxHeight, heightCounter, originY = 0):
        newHeight = maxHeight//len(skillList)
        mid = newHeight//2
        counter = 0
        for skill in skillList:
            skill.x = skill.tier * quarterX
            skill.y = mid + counter * newHeight + heightCounter * maxHeight + originY
            if skill.allowsSelection and len(skill.allowsSelection) > 0:
                initiateSkill(skill.allowsSelection, newHeight, counter, maxHeight * heightCounter + originY)
            counter += 1
    
    
    newHeight = 76//3
    mid = newHeight//2
    counter = 0
    for skill in basicSkills:
        if skill.tier == 1:
            skill.x = quarterX
            skill.y = mid + newHeight * counter
            if skill.allowsSelection and len(skill.allowsSelection) > 0:
                initiateSkill(skill.allowsSelection, newHeight, counter)
            counter += 1

    ## classes ##
    knight = Trait('Knight', 'A warrior who wears armor and wields shields', type ='class', arm=(1, 1), hp=(120, 14), mp=(30, 3), stam = (60, 6), bonusSkill = [armorW])
    barb = Trait('Barbarian', 'A brutal fighter who is mighty strong', type = 'class', hp=(160, 20), mp=(30, 3), stren=(1, 1), spells=[enrage], stam = (70, 10), bonusSkill = [strength])
    rogue = Trait('Rogue', 'A rogue who is stealthy and backstabby (probably has a french accent)', type = 'class', acc=(8, 4), ev=(10, 2), hp=(90, 10), mp=(40, 5), crit=(3, 0), stam = (50, 3), bonusSkill = [cunning])
    mage = Trait('Mage ', 'A wizard who zaps everything', type ='class', hp=(70, 6), mp=(50, 7), will=(2, 0), spells=[fireball], stam=(20, 1), bonusSkill = [elemental])
    necro = Trait('Necromancer', 'A master of the occult arts who has the ability to raise and control the dead.', type = 'class', hp=(100, 4), mp=(15, 1), spells=[darkPact, ressurect], stam=(50, 3), bonusSkill = [occult])
    classes = [knight, barb, rogue, mage, necro]
    allTraits.extend(classes)
    rightTraits.extend(classes)
    
    counter = 0
    for classe in classes:
        classe.x = RIGHT_X
        classe.y = CLASS_Y + counter
        counter += 1
    
    ## traits ##
    aggressive = Trait('Aggressive', 'Your anger is uncontrollable', type = 'trait')
    aura = Trait('Aura', 'You are surrounded by a potent aura', type = 'trait', mp=(20, 0))
    evasive = Trait('Evasive', 'You are aware of how to stay out of trouble', type = 'trait', ev=(10, 0))
    healthy = Trait('Healthy', 'You are healthy', type = 'trait', vit=(2, 0))
    muscular = Trait('Muscular', 'You are very strong', type = 'trait', stren=(2, 0))
    natArmor = Trait('Natural armor', 'Your skin is rock-hard', type = 'trait', arm = (1, 0))
    mind = Trait('Strong mind', 'Your mind is fast and potent', type = 'trait', will=(2, 0))
    agile = Trait('Agile', 'You have incredible reflexes', type = 'trait', dex=(2, 0))
    training = Trait('Warrior training', 'You are trained to master all weapons', type = 'trait', acc=(7, 0))
    tough = Trait('Tough', 'You can endure harm better', type = 'trait', hp=(40, 0))
    traits = [aggressive, aura, evasive, healthy, muscular, natArmor, mind, agile, training, tough]
    #traits.extend(optionTraits)
    allTraits.extend(traits)
    rightTraits.extend(traits)
    
    counter = 0
    for trait in traits:
        trait.x = RIGHT_X
        trait.y = TRAIT_Y + counter
        counter += 1
    
    def castShapeshift(caster = None, monsterTarget = None):
        caster = player
        for buff in caster.Fighter.buffList:
            if buff.name == 'in wolf form':
                caster.Player.shapeshifted = True
                caster.Player.shapeshift = 'human'
                buff.removeBuff()
                return
            elif buff.name == 'human':
                caster.Player.shapeshifted = True
                caster.Player.shapeshift = 'wolf'
                buff.removeBuff()
                return
    
    def autoKB(caster = None, target = None, fromTrait = 'Strength', maxDist = None): #caster is a fighter comp
        if fromTrait == 'Ranged heavy weapons':
            for eq in getEquippedInHands():
                if eq.Equipment.meleeWeapon or (eq.Equipment.ranged and not 'heavy' in eq.Equipment.type):
                    return
        baseChance = 12
        traitAmount = player.Player.getTrait('skill', fromTrait).amount
        chance = baseChance + (traitAmount-3) * 3
        dice = randint(1, 100)
        print('KNOCKBACK:', dice, chance)
        if dice <= chance:
            totalDist = 1 + (traitAmount-3)//2
            if maxDist and totalDist > maxDist:
                totalDist = maxDist
            message('{} is pushed back!'.format(target.name.capitalize()), colors.green)
            knockBack(player.x, player.y, target, totalDist, True, 2 + (traitAmount-3)//2)
    
    def autoStun(caster = None, target = None, fromTrait = 'Heavy weapons'): #caster is a fighter comp
        if fromTrait == 'Heavy weapons':
            for eq in getEquippedInHands():
                if eq.Equipment.ranged or (eq.Equipment.meleeWeapon and not 'heavy' in eq.Equipment.type):
                    return
        baseChance = 12
        traitAmount = player.Player.getTrait('skill', fromTrait).amount
        chance = baseChance + (traitAmount-3) * 3
        dice = randint(1, 100)
        print('STUN:', dice, chance)
        if dice <= chance:
            stunned = Buff('stunned', colors.light_yellow, cooldown = 4)
            stunned.applyBuff(target)
    
    def autoBleed(caster = None, target = None, fromTrait = 'Light ranged weapons'):
        if fromTrait == 'Ranged light weapons':
            for eq in getEquippedInHands():
                if eq.Equipment.meleeWeapon or (eq.Equipment.ranged and not 'light' in eq.Equipment.type):
                    return
        baseChance = 12
        traitAmount = player.Player.getTrait('skill', fromTrait).amount
        chance = baseChance + (traitAmount-3) * 3
        dice = randint(1, 100)
        #message('dice: {}, chance: {}'.format(str(dice), str(chance)))
        if dice <= chance:
            bleeding = Buff('bleeding', colors.red, cooldown = randint(6, 10), continuousFunction = lambda fighter: randomDamage('bleed', fighter, chance = 100, minDamage=5, maxDamage=15, dmgMessage = 'You take {} damage from bleeding !'))
            bleeding.applyBuff(target)
            
    def regen(caster = None, target = None, fromTrait = 'Constitution', ressources = ['HP'], name = 'regenerating', color = colors.green):
        #stamina without capitalization
        if caster is None:
            caster = player
        traitAmount = player.Player.getTrait('skill', fromTrait).amount
        dict = {}
        for res in ressources:
            dict[res] = 10 + (traitAmount-7)*5 #lvl7: 10, lvl8: 15, lvl9: 20, lvl10: 25
        buff = Buff(name, color, cooldown = 6, continuousFunction = lambda fighter: regenRessource(fighter, dict))
        buff.applyBuff(caster)
    
    def combatFocus(caster = None, target = None):
        if caster is None:
            caster = player
        traitAmount = player.Player.getTrait('skill', 'Martial training')
        bonus = 5 * (traitAmount - 6)
        buff = Buff('focused', colors.white, cooldown = 16, accuracy = bonus)
        buff.applyBuff(caster)
    
    def powerShot(caster = None, target = None, fromTrait = 'Heavy ranged weapons'):
        if caster is None or caster == player:
            traitAmount = player.Player.getTrait('skill', fromTrait).amount - 6
            caster = player
            weapon = None
            for wep in getEquippedInHands():
                if wep.Equipment.ranged and 'heavy' in wep.Equipment.type:
                    weapon = wep.Equipment
                    break
            if weapon:
                line = targetTile(weapon.maxRange, showBresenham=True, returnBresenham = True)
                if line == 'cancelled':
                    return 'didnt-take-turn'
            else:
                message('You have no weapons able to perform power shots.')
                return 'didnt-take-turn'
            
            weapon.baseRangedPower += 5 * traitAmount
            weapon.baseArmorPenetrationBonus += 2 * traitAmount
            weapon.shoot(line)
            weapon.baseRangedPower -= 5 * traitAmount
            weapon.baseArmorPenetrationBonus -= 2 * traitAmount
                
        elif caster.Ranged:
            caster.Ranged.shoot(target)
        return
    
    shapeshift = Spell(ressourceCost=10, cooldown = 100, useFunction=castShapeshift, name = 'Shapeshift', ressource='MP', type = 'racial')
    spellRegenStam = Spell(ressourceCost = 0, cooldown = 100, useFunction = lambda caster, target: regen(caster, target, 'Physical training', ['stamina'], 'gathering forces', colors.lighter_yellow), name = 'Gather forces', ressource = 'Stamina', type = 'physical')
    spellRegenMP = Spell(ressourceCost = 0, cooldown = 100, useFunction = lambda caster, target: regen(caster, target, 'Power of will', ['MP'], 'meditating', colors.blue), name = 'Meditate', ressource = 'MP', type = 'trait')
    spellRegenHP = Spell(ressourceCost = 0, cooldown = 100, useFunction = regen, name = 'Regenerate', ressource = 'HP', type = 'physical')
    castCombatFocus = Spell(ressourceCost = 10, cooldown = 80, useFunction = combatFocus, name = 'Combat focus', ressource = 'Stamina', type = 'martial')
    spellPowerShot = Spell(ressourceCost = 25, cooldown = 100, useFunction = powerShot, name = 'Power shot', ressource = 'Stamina', type = 'martial', castSpeed = 0)
    
    ###  race  ###
    controllableWerewolf = UnlockableTrait('Shape control', 'You are able to shapeshift at will.', type = 'trait', spells = [shapeshift], requiredTraits={'player level': 5, 'Werewolf': 1})
    
    ###  martial  ###
    combatFocusTrait = UnlockableTrait('Combat focus', 'You can focus extremely well on your fights for small amounts of time.', 'trait', requiredTraits = {'Martial training': 7}, spells = [castCombatFocus])
    combatKnowledge = UnlockableTrait('Combat knowledge', 'You are so efficient when fighting that you can better use your abilities', 'trait', requiredTraits = {'Martial training': 10})
    ## melee
    # light
    freeAtk = UnlockableTrait('Blade storm', 'You are so used to light weaponry you can sometimes attack twice in rapid succession.', 'trait', requiredTraits={'Light weapons': 4}) #, attackFuncs = [autoFreeAttack])
    flurryTrait = UnlockableTrait('Flurry', 'You unleash three deadly attacks on the target.', 'trait', requiredTraits={'Light weapons': 7}, spells = [flurry])
    dual = UnlockableTrait('Dual wield', 'Allows to wield two lights weapons at the same time.', 'trait', requiredTraits={'Light weapons': 10})
    # heavy
    autoStun = UnlockableTrait('Stunning strikes', 'You hit so hard you can stun your enemies.', 'trait', requiredTraits = {'Heavy weapons': 4}, attackFuncs = [autoStun])
    seismicTrait = UnlockableTrait('Seismic slam', 'You hit the floor in front of you, creating a shockwave in a cone.', 'trait', requiredTraits={'Heavy weapons': 7}, spells = [seismic])
    ignoreSlow = UnlockableTrait('Easy blows', 'You are used to the weight of heavy weapons and thus can strike with them at a fast speed.', 'trait', requiredTraits={'Heavy weapons': 10})
    ## ranged
    # light
    bleed = UnlockableTrait('Open wounds', 'Your shots make your enemies bleed.', 'trait', requiredTraits = {'Light ranged weapons': 4}, rangedAtkFuncs = [autoBleed])
    volleySkill = UnlockableTrait('Volley', 'You shoot three times in a row.', 'trait', requiredTraits = {'Light ranged weapons': 7}, spells = [volley])
    pistolero = UnlockableTrait('Pistolero', 'You can wield two light ranged weapons at the same time.', 'trait', requiredTraits = {'Light ranged weapons': 10})
    # heavy
    recoil = UnlockableTrait('Heavy recoil', 'You have learned to master the recoil of your weapons to your advantage.', 'trait', requiredTraits = {'Heavy ranged weapons': 4}, rangedAtkFuncs = [lambda caster, target: autoKB(caster, target, 'Heavy ranged weapons')])
    powerShotTrait = UnlockableTrait('Power shot', 'You use your gun to a new maximum.', 'trait', requiredTraits = {'Heavy ranged weapons': 7}, spells = [spellPowerShot])
    reload = UnlockableTrait('Fast reload', 'You shoot as fast with small pistols as with huge culverins.', 'trait', requiredTraits = {'Heavy ranged weapons': 10})
    ## armor wearing
    heavyDef = UnlockableTrait('Heavy defense', 'You can wear a light chest armor under a heavy one for maximum protection.', 'trait', requiredTraits = {'Armor wearing': 10})
    tackleTrait = UnlockableTrait('Tackle', 'You charge an ennemy with all your weight used as a weapon.', 'trait', requiredTraits = {'Armor wearing': 7}, spells = [tackleCharge])
    # shield
    backShield = UnlockableTrait('Back shield', 'You can wear a shield on your back for more protection.', 'trait', requiredTraits = {'Shield mastery': 10})
    
    ###  mental  ###
    ## will
    aware = UnlockableTrait('Self aware', 'Allows to see the buffs and debuffs cooldowns.', 'trait', requiredTraits={'Power of will': 4})
    regenMP = UnlockableTrait('Meditate', 'Your mental energy regenerates extremely rapidly', 'trait', requiredTraits = {'Power of will': 7}, spells = [spellRegenMP])
    
    ###  physical  ###
    regenStam = UnlockableTrait('Gather forces', 'Your stamina regenerates extremely rapidly', 'trait', requiredTraits = {'Physical training': 7}, spells = [spellRegenStam])
    efficiency = UnlockableTrait('Greater efficiency', 'You know very well your physical abilities and can use them to their best.', 'trait', requiredTraits = {'Physical training': 10})
    ## cunning
    shadowstepTrait = UnlockableTrait('Shadow step', 'When concealed, you can move through the shadows at incredible speed.', 'trait', requiredTraits={'Cunning': 7}, spells = [shadowStep])
    shadowCrit = UnlockableTrait('Surprise attack', 'When concealed, you have a greater chance to inflinct critical damage.', 'trait', requiredTraits = {'Cunning': 4})
    # crit
    greaterCrit = UnlockableTrait('Fatal precision', 'Your hits are so precise they can eviscerate your victim in one strike.', 'trait', requiredTraits = {'Critical': 4}, critMult = 1)
    ## strength
    meleeKB = UnlockableTrait('Mighty strikes', 'You smash so hard you can sometimes push back enemies', 'trait', requiredTraits = {'Strength': 4}, attackFuncs = [autoKB])
    strongChargeTrait = UnlockableTrait('Charge', 'You charge an enemy and immediatly attack.', 'trait', requiredTraits = {'Strength': 7}, spells = [strongCharge])
    ignoreTwoHanded = UnlockableTrait('Firm grip', 'You are so strong you can wield two handed weapons in only one hand.', 'trait', requiredTraits = {'Strength': 10})
    # brawl
    glovesDmg = UnlockableTrait('Fist fighter', 'You know very well how to use your hands in a fight.', 'trait', requiredTraits = {'Brawling': 4})
    throwEnemySkill = UnlockableTrait('Throw enemy', 'You can grab an enemy and throw it across rooms, sometimes into his fellow companions.', 'trait', requiredTraits = {'Brawling': 7}, spells = [throwEnemy])
    fistsOfSteel = UnlockableTrait('Fists of steel', 'You can use the weight of your armor gloves as a weapon.', 'trait', requiredTraits = {'Brawling': 10})
    ## endurance
    resistDebuff = UnlockableTrait('Physical withstandingness', 'You are used to facing harsh physical conditions and can easily resist them.', 'trait', requiredTraits = {'Endurance': 4})
    # const
    regenHP = UnlockableTrait('Regenerate', 'Your health regenerates extremely rapidly', 'trait', requiredTraits = {'Constitution': 7}, spells = [spellRegenHP])

    unlockableTraits.extend([controllableWerewolf, dual, aware, flurryTrait, seismicTrait, ignoreSlow, shadowstepTrait, shadowCrit, greaterCrit,
                             throwEnemySkill, freeAtk, glovesDmg, meleeKB, volleySkill, resistDebuff, regenStam, regenHP, regenMP, ignoreTwoHanded,
                             combatFocusTrait, combatKnowledge, heavyDef, efficiency, recoil, pistolero, strongChargeTrait, tackleTrait, reload,
                             powerShotTrait, fistsOfSteel, bleed, backShield])
    actualUnlock = [] #sorted list, in order not to mess with unlocking more advanced traits
    for skill in skills:
        for unlock in unlockableTraits:
            if skill.name in list(unlock.requiredTraits.keys()):
                actualUnlock.append(unlock)
                level = unlock.requiredTraits[skill.name]
                print(skill.name, 'can unlock', unlock.name)
                skill.unlockables.append((unlock, level))
                try:
                    for prevUnlock, prevLevel in skill.owner.unlockables:
                        if prevLevel == level - 3:
                            unlock.requiredTraits[prevUnlock.name] = 1
                    print(unlock.name, unlock.requiredTraits)
                except:
                    print(skill.name, 'is basic')
                    
    for unlock in unlockableTraits:
        if not unlock in actualUnlock:
            actualUnlock.append(unlock)
    return allTraits, leftTraits, rightTraits, races, attributes, skills, classes, traits, human, actualUnlock #unlockableTraits#skilled, human, unlockableTraits

def characterCreation():
    global createdCharacter
    createdCharacter = {'power': 0, 'acc': 20, 'ev': 0, 'arm': 0, 'hp': 0, 'mp': 0, 'crit': 0, 'stren': 0, 'dex': 0, 'vit': 0, 'will': 0, 'ap': 0, 
                    'powLvl': 0, 'accLvl': 0, 'evLvl': 0, 'armLvl': 0, 'hpLvl': 0, 'mpLvl': 0, 'critLvl': 0, 'strLvl': 0, 'dexLvl': 0, 'vitLvl': 0, 'willLvl': 0, 'apLvl': 0,
                    'spells': [], 'load': 45.0, 'stealth': 0, 'stamina': 0, 'stamLvl': 0,
                    'dmgTypes': {'physical': 100}, 'resistances': {'physical': 0, 'poison': 0, 'fire': 0, 'cold': 0, 'lightning': 0, 'light': 0, 'dark': 0, 'none': 0},
                    'attackFuncs': [], 'buffsOnAttack': []}
    #allTraits = []
    #leftTraits = []
    #rightTraits = []
    LEFT_X = (WIDTH // 4)
    RIGHT_X = WIDTH - (WIDTH // 4)
    
    allTraits, leftTraits, rightTraits, races, attributes, skills, classes, traits, human, unlockableTraits = initializeTraits() #skilled, human, unlockableTraits = initializeTraits()
    
    
    #index
    index = 0
    leftIndexMin = 0
    leftIndexMax = len(leftTraits) - 1
    rightIndexMin = leftIndexMax + 1
    rightIndexMax = rightIndexMin + len(rightTraits) - 1
    maxIndex = len(allTraits) + 2
    
    while True:
        root.clear()
        
        raceSelected = False
        for race in races:
            if race.selected:
                raceSelected = True
                break
        print(raceSelected)
        
        attributesPoints = 0
        for attribute in attributes:
            attributesPoints += attribute.amount
        print(attributesPoints)

        traitsPoints = 0
        for trait in traits:
            traitsPoints += trait.amount
        print(traitsPoints)
        
        classSelected = False
        for classe in classes:
            if classe.selected:
                classSelected = True
                break
        print(classSelected)
        
        skillsPoints = 0
        maxSkill = 1
        if human.selected:
            maxSkill=3
        for skill in skills:
            amount = skill.amount
            if skill.isBonus:
                amount -= 1
            skillsPoints += amount
        print(skillsPoints)
        
        drawCentered(cons = root, y = 6, text = '--- CHARACTER CREATION ---', fg = colors.darker_red, bg = None)
        
        drawCenteredOnX(cons = root, x = LEFT_X, y = 9, text = '-- RACE --', fg = colors.darker_red, bg = None)
        
        drawCenteredOnX(cons = root, x = LEFT_X, y = 28, text = '-- ATTRIBUTES --', fg = colors.darker_red, bg = None)
        drawCenteredOnX(cons = root, x = LEFT_X, y = 29, text = str(attributesPoints) + '/10', fg = colors.dark_red, bg = None)

        drawCenteredOnX(cons = root, x = RIGHT_X, y = 28, text = '-- TRAITS --', fg = colors.darker_red, bg = None)
        drawCenteredOnX(cons = root, x = RIGHT_X, y = 29, text = str(traitsPoints) + '/2', fg = colors.dark_red, bg = None)
        
        drawCenteredOnX(cons = root, x = RIGHT_X, y = 9, text = '-- CLASS --', fg = colors.darker_red, bg = None)
        '''
        drawCenteredOnX(cons = root, x = LEFT_X, y = 38, text = '-- SKILLS --', fg = colors.darker_red, bg = None)
        drawCenteredOnX(cons = root, x = LEFT_X, y = 39, text = str(skillsPoints) + '/' + str(maxSkill), fg = colors.dark_red, bg = None)
        '''
        drawCentered(cons = root, y = 9, text = '-- DESCRIPTION --', fg = colors.darker_red, bg = None)
        color = colors.white
        if maxSkill - skillsPoints > 0:
            color = colors.green
        drawCentered(cons = root, y = 69, text = 'Continue to skills screen', fg = color, bg = None)
        drawCentered(cons = root, y = 70, text = 'Start Game', fg = colors.white, bg = None)
        drawCentered(cons = root, y = 71, text = 'Cancel', fg = colors.white, bg = None)

        #Displaying stats
        eightScreen = WIDTH//6
        
        text = 'Power: ' + str(createdCharacter['power'] + createdCharacter['stren'])
        drawCenteredOnX(cons = root, x = eightScreen * 1, y = 74, text = text, fg = colors.white, bg = None)
        X = eightScreen * 1 + ((len(text) + 1)// 2)
        root.draw_str(x = X, y = 74, string = ' + ' + str(createdCharacter['powLvl'] + createdCharacter['strLvl']) + '/lvl', fg = colors.yellow, bg = None)
        
        text = 'Accuracy: ' + str(createdCharacter['acc'] + 2 * createdCharacter['dex'])
        drawCenteredOnX(cons = root, x = eightScreen * 2, y = 74, text = text, fg = colors.white, bg = None)
        X = eightScreen * 2 + ((len(text) + 1)// 2)
        root.draw_str(x = X, y = 74, string = ' + ' + str(createdCharacter['accLvl'] + createdCharacter['dexLvl']) + '/lvl', fg = colors.yellow, bg = None)
        
        text = 'Evasion: ' + str(createdCharacter['ev'] + createdCharacter['dex'])
        drawCenteredOnX(cons = root, x = eightScreen * 3, y = 74, text = text, fg = colors.white, bg = None)
        X = eightScreen * 3 + ((len(text) + 1)// 2)
        root.draw_str(x = X, y = 74, string = ' + ' + str(createdCharacter['evLvl'] + createdCharacter['dexLvl']) + '/lvl', fg = colors.yellow, bg = None)
        
        text = 'Armor: ' + str(createdCharacter['arm'])
        drawCenteredOnX(cons = root, x = eightScreen * 4, y = 74, text = text, fg = colors.white, bg = None)
        X = eightScreen * 4 + ((len(text) + 1)// 2)
        root.draw_str(x = X, y = 74, string = ' + ' + str(createdCharacter['armLvl']) + '/lvl', fg = colors.yellow, bg = None)
        
        text = 'Max HP: ' + str(createdCharacter['hp'] + 5 * createdCharacter['vit'])
        drawCenteredOnX(cons = root, x = eightScreen * 1, y = 76, text = text, fg = colors.white, bg = None)
        X = eightScreen * 1 + ((len(text) + 1)// 2)
        root.draw_str(x = X, y = 76, string = ' + ' + str(createdCharacter['hpLvl'] + 5 * createdCharacter['vitLvl']) + '/lvl', fg = colors.yellow, bg = None)
        
        text = 'Max MP: ' + str(createdCharacter['mp'] + 5 * createdCharacter['will'])
        drawCenteredOnX(cons = root, x = eightScreen * 2, y = 76, text = text, fg = colors.white, bg = None)
        X = eightScreen * 2 + ((len(text) + 1)// 2)
        root.draw_str(x = X, y = 76, string = ' + ' + str(createdCharacter['mpLvl'] + 5 * createdCharacter['willLvl']) + '/lvl', fg = colors.yellow, bg = None)
        
        text = 'Critical: ' + str(createdCharacter['crit']) + '%'
        drawCenteredOnX(cons = root, x = eightScreen * 3, y = 76, text = text, fg = colors.white, bg = None)
        X = eightScreen * 3 + ((len(text) + 1)// 2)
        root.draw_str(x = X, y = 76, string = ' + ' + str(createdCharacter['critLvl']) + '/lvl', fg = colors.yellow, bg = None)
        
        text = 'Max load: ' + str(createdCharacter['load'] + 3 * createdCharacter['stren']) + ' kg'
        drawCenteredOnX(cons = root, x = eightScreen * 4, y = 76, text = text, fg = colors.white, bg = None)
        X = eightScreen * 4 + ((len(text) + 1)// 2)
        root.draw_str(x = X, y = 76, string = ' + ' + str(3 * createdCharacter['strLvl']) + '/lvl', fg = colors.yellow, bg = None)
        
        text = 'Stealth: ' + str(createdCharacter['stealth'])
        drawCenteredOnX(root, x = eightScreen * 5, y = 74, text = text, fg = colors.white, bg = None)
        X = eightScreen * 5 + (len(text) + 1)//2
        
        text = 'Stamina: ' + str(createdCharacter['stamina'] + 5 * createdCharacter['vit'])
        drawCenteredOnX(cons = root, x = eightScreen * 5, y = 76, text = text, fg = colors.white, bg = None)
        X = eightScreen * 5 + ((len(text) + 1)// 2)
        root.draw_str(x = X, y = 76, string = ' + ' + str(5 * createdCharacter['vitLvl'] + createdCharacter['stamLvl']) + '/lvl', fg = colors.yellow, bg = None)

        for trait in allTraits:
            if index == allTraits.index(trait):
                trait.underCursor = True
            else:
                trait.underCursor = False
            trait.drawTrait()
        if index == maxIndex - 2:
            drawCentered(cons = root, y = 69, text = 'Continue to skills screen', fg = colors.black, bg = colors.white)
        if index == maxIndex - 1:
            drawCentered(cons = root, y = 70, text = 'Start Game', fg = colors.black, bg = colors.white)
        if index == maxIndex:
            drawCentered(cons = root, y = 71, text = 'Cancel', fg = colors.black, bg = colors.white)

        tdl.flush()

        key = tdl.event.key_wait()
        if tdl.event.isWindowClosed():
            quitGame("Closed game", noSave = True)
        if key.keychar.upper() == 'DOWN':
            index += 1
            playWavSound('selectClic.wav')
        if key.keychar.upper() == 'UP':
            index -= 1
            playWavSound('selectClic.wav')
        if key.keychar.upper() == 'RIGHT' and (leftIndexMin <= index <= leftIndexMax):
            if (leftIndexMin <= index <= leftIndexMax):
                if rightIndexMin <= index + len(leftTraits) <= rightIndexMax:
                    index += len(leftTraits)
                else:
                    index = rightIndexMax
                playWavSound('selectClic.wav')
            else:
                playWavSound('error.wav')
        if key.keychar.upper() == 'LEFT':
            if (rightIndexMin <= index <= rightIndexMax):
                if leftIndexMin <= index - len(leftTraits) <= leftIndexMax:
                    index -= len(leftTraits)
                else:
                    index = leftIndexMax
                playWavSound('selectClic.wav')
            else:
                playWavSound('error.wav',)

        #adding choice bonus
        if key.keychar.upper() == 'ENTER':
            error = False
            if index == maxIndex - 2:
                levelUpScreen(newSkillpoints=False, skillpoint=maxSkill - skillsPoints, fromCreation=True, skills=skills)
                error = True
            if index == maxIndex - 1:
                if raceSelected and classSelected:
                    allTraits.extend(skills)
                    print(createdCharacter)
                    return createdCharacter, allTraits, maxSkill - skillsPoints, unlockableTraits
                else:
                    playWavSound('error.wav')
                    error = True
            if index == maxIndex:
                return 'cancelled', 'cancelled', 'cancelled', 'cancelled'

            if not error:
                trait = allTraits[index]
                if trait.type == 'race':
                    if not raceSelected and trait.selectable:
                        trait.applyBonus()
                if trait.type == 'attribute':
                    if attributesPoints < 10 and trait.selectable:
                        trait.applyBonus()
                if trait.type == 'trait':
                    if traitsPoints < 2 and trait.selectable:
                        trait.applyBonus()
                if trait.type == 'class':
                    if not classSelected and trait.selectable:
                        trait.applyBonus()
                #if trait.type == 'skill':
                #    if skillsPoints < maxSkill and trait.selectable:
                #        trait.applyBonus()

        #removing choice bonus
        if key.keychar.upper() == 'BACKSPACE':
            if index != maxIndex and index != maxIndex - 1:
                trait = allTraits[index]
                if trait == human: # or (trait == human and skilled.selected):
                    for skill in skills:
                        if skill.selected:
                            skill.removeBonus()
                if trait.selected:
                    trait.removeBonus()
            else:
                playWavSound('error.wav')
        if index > maxIndex:
            index = 0
        if index < 0:
            index = maxIndex
        
        tdl.flush()
    
def enterName(race):
    letters = []
    while True:
        text = '_'
        name = ''
        for letter in letters:
            name += letter
        if len(name) < 16:
            text = name + '_'
        else:
            text = name

        root.clear()
        drawCentered(cons =  root, y = 25, text = 'What is your name, ' + race + ' hero ?', fg = colors.white, bg = None)
        drawCentered(cons = root, y = 26, text = 'Enter to confirm, leave blank for random name. 16 characters maximum', fg = colors.gray, bg = None)
        drawCentered(cons = root, y = 30, text = text, fg = colors.white, bg = None)
        tdl.flush()
        
        key = tdl.event.key_wait()
        if tdl.event.isWindowClosed():
            quitGame("Closed game", noSave = True)
        if key.keychar.upper()== 'ENTER':
            if name == '':
                name = nameGen.humanLike(randint(5,8))
                return name.capitalize()
            elif name in FORBIDDEN_NAMES:
                msgBox("\n Find a more original name ! \n", 33, False, False)
            elif name == heroName:
                msgBox("\n You are not worthy of that name ! \n" ,40, False, False)
            else:
                return name.capitalize()
            
        elif key.keychar in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if len(name) < 16:
                letters.append(key.keychar)
            else:
                playWavSound('error.wav')
        elif key.keychar.upper() == 'BACKSPACE':
            if letters:
                letters.pop()
            else:
                playWavSound('error.wav')
        elif key.keychar.upper() == 'ESCAPE':
            mainMenu()
#______________CHARACTER GENERATION____________

def wouldBigTouchTarget(mapToUse, bigMonster, potentialX, potentialY, targetX, targetY):
    if not bigMonster:
        return False
    if bigMonster.size < 2:
        return False
    if mapToUse[potentialX][potentialY].clearance < bigMonster.size:
        return False
    dx = potentialX - bigMonster.x
    dy = potentialY - bigMonster.y
    for monsterPart in bigMonster.sizeComponents:
        newX = monsterPart.x + dx
        newY = monsterPart.y + dy
        if math.sqrt((targetX - newX) ** 2 + (targetY - newY) ** 2) < 2 and not isBlocked(newX, newY, True, bigMonster):
            return True
    return False

def heuristic(sourceX, sourceY, targetX, targetY):
    return abs(sourceX - targetX) + abs(sourceY - targetY)

def astarPath(startX, startY, goalX, goalY, flying = False, silent = False, mapToUse = None, size = 1, bigMonster = None):
    if mapToUse is None:
        print("NO MAP TO USE IN ASTAR")
        mapToUse = myMap
    start = mapToUse[startX][startY]
    goal = mapToUse[goalX][goalY]
    if myMap is None:
        raise TypeError("Map is none, start of astar func")
    if mapToUse is None:
        raise TypeError("Map to use is None, astar func")
        traceback.print_exc()
        os._exit(-1)
    frontier = [(start, 0)]
    cameFrom = {}
    costSoFar = {}
    cameFrom[start] = None
    costSoFar[start] = 0
    '''
    allowGoalNeighbours = False
    if size > 2:
        if not silent:
            print('goal neighbors are allowed')
        allowGoalNeighbours = True
    goalNeighbors = [tile for tile in goal.neighbors(mapToUse) if not tile.blocked and (flying or not myMap[tile.x][tile.y].chasm)]
    '''
    print('frontier:', frontier)
    while len(frontier) != 0:
        prioTile = None
        lastPrio = 99999
        for tile, prio in frontier:
            if prio < lastPrio:
                lastPrio = prio
                prioTile = tile

        frontier.remove((prioTile, lastPrio))
        current = prioTile
        if not silent:
            print('tile:', prioTile.x, prioTile.y, '  prio:', lastPrio)
        if current == goal:
            if not silent:
                print('arrived to goal')
            break
        elif wouldBigTouchTarget(mapToUse, bigMonster, current.x, current.y, goalX, goalY):
            if not silent:
                print('arrived somewhere adjacent to goal')
            break
        #elif current in goalNeighbors and allowGoalNeighbours:
        #    if not silent:
        #        print('arrived to goal neighbor: ', current.x, current.y)
        #        print('goal: ', goal.x, goal.y)
        #    break
        for nextTile in current.neighbors(mapToUse):
            if not silent:
                print('neighbor:', nextTile.x, nextTile.y)
            if flying or not mapToUse[nextTile.x][nextTile.y].chasm:
                if not (isBlocked(nextTile.x, nextTile.y, ignoreSelfSize=True, bigMonster=bigMonster) or mapToUse[nextTile.x][nextTile.y].clearance < size) or ((nextTile == goal)): # or wouldBigTouchTarget(mapToUse, bigMonster, nextTile.x, nextTile.y, goalX, goalY)): # or (nextTile in goalNeighbors and allowGoalNeighbours)):
                    newCost = costSoFar[current] + mapToUse[nextTile.x][nextTile.y].moveCost(flying)
                    if nextTile not in costSoFar or newCost < costSoFar[nextTile]:
                        costSoFar[nextTile] = newCost
                        heurCost = heuristic(nextTile.x, nextTile.y, goal.x, goal.y)
                        priority = newCost + heurCost
                        if not silent:
                            print('next:', nextTile.x, nextTile.y, '  prio = G + H', '  G=', newCost, '  H=', heurCost)
                        frontier.append((nextTile, priority))
                        cameFrom[nextTile] = current
                    elif nextTile in costSoFar:
                        if not silent:
                            print('next was already explored')
                else:
                    if not silent:
                        print('next is blocked')
                        print('size:', size, ' tile clearance:', mapToUse[nextTile.x][nextTile.y].clearance)
            else:
                if not silent:
                    print("next is chasm")

    #current = goal
    path = [current]
    if not silent:
        print('path end:', current.x, current.y)
        print('start:', startX, startY, ' goal:', goalX, goalY)
    while current != start:
        former = current
        if not silent:
            print('former:', former.x, former.y)
        current = cameFrom[former]
        if not silent:
            print('current:', current.x, current.y)
        path.append(current)
    if not silent:
        print('not reversed path:')
        print([(tile.x, tile.y) for tile in path])
    path.reverse()
    if not silent:
        print('reversed path:')
        print([(tile.x, tile.y) for tile in path])
    return path

def closestMonsterWrapper(caster = None, zone = None, max_range = 8):
    #return closestMonster(max_range)
    monster = closestMonster(max_range)
    if monster != 'cancelled' and displayConfirmSpell(monster, caster, zone):
        return monster
    else:
        return 'cancelled'

def closestMonster(max_range):
    closestEnemy = None
    closestDistance = max_range + 1
    
    found = False
    for object in objects:
        if object.Fighter and not object == player and (object.x, object.y) in visibleTiles:
            dist = player.distanceTo(object)
            if dist < closestDistance:
                found = True
                closestEnemy = object
                closestDistance = dist
    if found:
        return closestEnemy
    else:
        return 'cancelled'

def farthestMonster(max_range):
    farthestEnemy = None
    farthestDistance = 0
    
    found = False
    for object in objects:
        if object.Fighter and not object == player and (object.x, object.y) in visibleTiles:
            found = True
            dist = player.distanceTo(object)
            if dist > farthestDistance:
                farthestEnemy = object
                farthestDistance = dist
    if found:
        return farthestEnemy
    else:
        return 'cancelled'

def farthestMonsterWrapper(caster = None, zone = None, max_range = 8):
    #return farthestMonster(max_range)
    monster = farthestMonster(max_range)
    if monster != 'cancelled' and displayConfirmSpell(monster, caster, zone):
        return monster
    else:
        return 'cancelled'

class Nemesis:
    def __init__(self, nemesisObject, branch, level):
        self.nemesisObject = nemesisObject
        self.branch = branch
        self.level = level

class Stairs:
    def __init__(self, climb = 'down', branchesFrom = dBr.mainDungeon, branchesTo = dBr.mainDungeon, changeBranchLevel = 1):
        self.climb = climb
        self.branchesFrom = branchesFrom                #previous floor, as in the one above
        self.branchesTo = branchesTo
        self.stairsOf = self.branchesTo.shortName
        self.stairsFrom = self.branchesFrom.shortName
        if self.branchesFrom != self.branchesTo:
            self.changeBranch = self.branchesTo
            self.changeBranchLevel = changeBranchLevel
        else:
            self.changeBranch = None
            self.changeBranchLevel = None
    
    def climbStairs(self):
        global stairCooldown, currentBranch, branchLevel, depthLevel
        if stairCooldown == 0:
            if self.climb == 'down':
                temporaryBox('Loading...')
                stairCooldown = 2
                boss = False
                if branchLevel + 1 in currentBranch.bossLevels and self.changeBranch is None:
                    boss = True
                if DEBUG:
                    message("Stair cooldown set to {}".format(stairCooldown), colors.purple)
                nextLevel(boss, changeBranch=self.changeBranch, fromStairs=self, changeBranchLevel = self.changeBranchLevel)
            elif self.climb == 'up':
                depthLevel -= 1
                if stairCooldown == 0:
                    temporaryBox('Loading...')
                    saveLevel(branchLevel)
                    stairCooldown = 2
                    previousLevel(self.changeBranch, fromStairs = self, changeBranchLevel = self.changeBranchLevel)
                else:
                    message("You're too tired to climb the stairs right now")
                        
                
                '''
                if branchLevel > 1 or currentBranch.name != 'Main':
                    depthLevel -= 1
                    print(currentBranch.name)
                    if stairCooldown == 0:
                        temporaryBox('Loading...')
                        saveLevel(branchLevel)
                        chosen = False
                        stairCooldown = 2
                        if DEBUG:
                            message("Stair cooldown set to {}".format(stairCooldown), colors.purple)
                        if branchLevel == 1 and currentBranch.name != 'Main':
                            if not chosen:
                                chosen = True
                                print('Returning to origin branch')
                                loadLevel(currentBranch.origDepth, save = False, branch = currentBranch.origBranch, fromStairs = self)
                            else:
                                print('WHY THE HECK IS THE CODE EXECUTING THIS FFS ?')
                        else:
                            if not chosen:
                                chosen = True
                                toLoad = branchLevel - 1
                                loadLevel(toLoad, save = False, branch=currentBranch, fromStairs = self)
                            else:
                                print('Chosen was equal to true. If the code ever goes here, I fucking hate all of this.')
                    else:
                        message("You're too tired to climb the stairs right now")
                    return None
                '''
        else:
            message("You're too tired to climb down the stairs right now")

class GameObject:
    "A generic object, represented by a character"
    def __init__(self, x, y, char, name, color = colors.white, blocks = False, Fighter = None, AI = None, Player = None, Ghost = False, flying = False, Item = None, alwaysVisible = False, darkColor = None, Equipment = None, pName = None, Essence = None, socialComp = None, shopComp = None, questList = [], Stairs = None, alwaysAlwaysVisible = False, size = 1, sizeChar = [], sizeColor = [], sizeDarkColor = [], smallChar = None, ProjectileComp = None, noPronoun = False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.blocks = blocks
        self.trueName = name
        self.Fighter = Fighter
        self.Player = Player
        self.ghost = Ghost
        self.Item = Item
        self.alwaysVisible = alwaysVisible
        self.alwaysAlwaysVisible = alwaysAlwaysVisible
        if self.alwaysAlwaysVisible:
            self.alwaysVisible = True
        self.darkColor = darkColor
        self.baseFlying = flying
        self.BASE_FLYING = flying
        if self.Fighter:  #let the fighter component know who owns it
            self.Fighter.owner = self
        self.AI = AI
        if self.AI:  #let the AI component know who owns it
            self.AI.owner = self
            self.AI.futureCoords = (self.x, self.y)
        if self.Player:
            self.Player.owner = self
            self.Fighter.actionPoints = 100
        if self.Item:
            self.Item.owner = self 
        self.Equipment = Equipment
        if self.Equipment:
            self.Equipment.owner = self
        self.Essence = Essence
        if self.Essence:
            self.Essence.owner = self
        self.Stairs = Stairs
        if self.Stairs:
            self.Stairs.owner = self
        self.Projectile = ProjectileComp
        if self.Projectile:
            self.Projectile.owner = self
        self.astarPath = []
        self.lastTargetX = None
        self.lastTargetY = None
        self.pName = pName
        self.socialComp = socialComp
        self.shopComp = shopComp
        self.questList = questList
        self.detectionStatus = '?'
        
        self.owner = None
        self.smallChar = smallChar
        
        self.size = size
        self.sizeChar = sizeChar#a list of characters which will form the final object. The list needs to be created with this pattern in mind, as does sizeColor:
                                #X 2 5
                                #0 3 6
                                #1 4 7
        self.sizeColor = sizeColor
        self.sizeDarkColor = sizeDarkColor
        if self.size > 1:
            global objects
            sizeCompNum = self.size * self.size - 1
            if not self.sizeChar:
                self.sizeChar = []
                for char in range(sizeCompNum):
                    self.sizeChar.append(self.char)
            if not self.sizeColor:
                self.sizeColor = []
                for color in range(sizeCompNum):
                    self.sizeColor.append(self.color)
            if not self.sizeDarkColor:
                self.sizeDarkColor = []
                for color in range(sizeCompNum):
                    self.sizeDarkColor.append(self.color)
            
            self.sizeComponents = [] #a list of gameObjects linked to the father GameObject
            maxX = self.size
            maxY = maxX
            i = 0
            for x in range(maxX):
                for y in range(maxY):
                    if (x, y) != (0, 0):
                        newComp = GameObject(self.x + x, self.y + y, char = self.sizeChar[i], name = self.name, color = self.sizeColor[i], blocks = self.blocks, Fighter = self.Fighter, AI = None, Player = None, Ghost = self.ghost, flying = self.flying, Item = None, alwaysVisible = self.alwaysAlwaysVisible, darkColor = self.sizeDarkColor, Equipment = None, pName = None, Essence = self.Essence, socialComp = self.socialComp, shopComp = self.shopComp, questList = self.questList, Stairs = None, alwaysAlwaysVisible = self.alwaysAlwaysVisible, size = 1, sizeChar = [], sizeColor = [], sizeDarkColor = [])
                        newComp.owner = self
                        self.sizeComponents.append(newComp)
                        objects.append(newComp)
                        i += 1
            
            for comp in self.sizeComponents:
                print(comp.name)
                
        else:
            self.sizeComponents = None
        
        if self.Item:
            if self.Item.useText == 'Use' and self.Equipment:
                self.Item.useText = 'Equip'
        self.noPronoun = noPronoun
    
    @property
    def name(self):
        if self.Item:
            if self.Item.identified:
                return self.trueName
            else:
                return self.Item.unIDName
        else:
            return self.trueName
    
    @property
    def pluralName(self):
        if self.Item:
            if self.Item.identified:
                if self.pName:
                    return self.pName
                else:
                    return self.name + 's'
            else:
                return self.Item.unIDpName
        else:
            if self.pName:
                return self.pName
            else:
                return self.name + 's'
    
    @property
    def flying(self):
        mightReturnTrue = False
        if self.Fighter:
            for buff in self.Fighter.buffList:
                if buff.flight is not None:
                    if not buff.flight:
                        return False
                    else:
                        mightReturnTrue = True
        return mightReturnTrue or self.baseFlying
                

    def moveTowards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)
    
    def checkForMove(self, x, y):
        if self.Fighter and (not self.Fighter.canTakeTurn or not self.Fighter.canMove):
            return False
        if self.size > 1:
            dx = x - self.x
            dy = y - self.y
            if isBlocked(x, y, True, self):
                return False
            for object in self.sizeComponents:
                if isBlocked(object.x + dx, object.y + dy, True, self):
                    return False
        return True
        
    def move(self, dx, dy):
        if not self.size > 1:
            if self.Fighter and (not self.Fighter.canTakeTurn or not self.Fighter.canMove):
                if self != player:
                    pass
                else:
                    return 'didnt-take-turn'
            elif not isBlocked(self.x + dx, self.y + dy) or self.ghost:
                self.x += dx
                self.y += dy
                if self.Player:
                    myMap[self.x][self.y].triggerFunc()
            else:
                if self.Player and self.Fighter and 'confused' in convertBuffsToNames(self.Fighter):
                    message('You bump into a wall !')
                elif self == player:
                    return 'didnt-take-turn'
        else:
            moveable = self.checkForMove(self.x + dx, self.y + dy)
            if moveable:
                self.x += dx
                self.y += dy
                for monsterPart in self.sizeComponents:
                    monsterPart.x += dx
                    monsterPart.y += dy
    
    def moveTo(self, otherX, otherY):
        if self.size <= 1:
            if self.Fighter and (not self.Fighter.canTakeTurn or not self.Fighter.canMove):
                pass
            elif not isBlocked(otherX, otherY) or self.ghost:
                self.x = int(otherX)
                self.y = int(otherY)
                if self.Player:
                    myMap[self.x][self.y].triggerFunc()
            else:
                if self.Player and self.Fighter and 'confused' in convertBuffsToNames(self.Fighter):
                    message('You bump into a wall !')
                elif self == player:
                    return 'didnt-take-turn'
        else:
            moveable = self.checkForMove(otherX, otherY)
            if moveable:
                dx = otherX - self.x
                dy = otherY - self.y
                self.x = otherX
                self.y = otherY
                for monsterPart in self.sizeComponents:
                    monsterPart.x += dx
                    monsterPart.y += dy
    
    def basicDraw(self):
        allMonstersDetected = []
        for monsters in monstersDetected:
            allMonstersDetected.extend(monsters)
        if (self.x, self.y) in visibleTiles or REVEL or self in allMonstersDetected:
            bg = None
            if self.Fighter:
                if 'frozen' in convertBuffsToNames(self.Fighter):
                    bg = colors.light_violet
            con.draw_char(self.x, self.y, self.char, self.color, bg=bg)
        elif self.alwaysAlwaysVisible:
            con.draw_char(self.x, self.y, self.char, self.darkColor, bg=None)
        elif self.alwaysVisible and myMap[self.x][self.y].explored:
            con.draw_char(self.x, self.y, self.char, self.darkColor, bg=None)

    def draw(self):
        self.basicDraw()
        if self.sizeComponents:
            for comp in self.sizeComponents:
                comp.basicDraw()
        
    def clear(self):
        con.draw_char(self.x, self.y, ' ', self.color, bg=None)

    def distanceTo(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)
    
    def distanceToCoords(self, x, y):
        dx = x - self.x
        dy = y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)
            
    def sendToBack(self): #used to make anything appear over corpses
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def moveNextStepOnPath(self):
        if self.astarPath:
            x, y = self.astarPath.pop(0)
            if isBlocked(x, y):
                self.astarPath = []
                self.lastTargetX = None
                self.lastTargetY = None
                if DEBUG:
                    print(self.name.capitalize() + " : Path blocked, deleting path")
                    return 'fail'
            else:
                self.x, self.y = x, y
                if DEBUG:
                    print(self.name.capitalize() + " : Pathing successful" + self.name + " moved to " + str(self.x) + ', ' + str(self.y))
                return "complete"
        else:
            return "fail"
    
    def moveAstar(self, destX, destY, fallback = True):
        global tilesinPath, pathfinder
        #TODO : Add another path check using another pathfinder accounting enemies as blocking (so as to try to find a way around them), then if no path is found using this way (e.g tunnel), use the normal pathfinder, and if there is still path found , use moveTowards()
        #if destX is not None and destY is not None and destX == self.lastTargetX and destY == self.lastTargetY and self.astarPath:
            #self.moveAstar()
            #print(self.name.capitalize() + " : Following old path")
        #else:
        print(self.name.capitalize() + " : No path found, trying to create new")
        self.lastTargetX = destX
        self.lastTargetY = destY
        self.astarPath = pathfinder.get_path(self.x, self.y, destX, destY)
        tilesinPath.extend(self.astarPath)
        if len(self.astarPath) != 0:
            if DEBUG:
                print(self.name + "'s path :", end = " ")
                for (x,y) in self.astarPath:
                    print (str(x) + "/" + str(y) + ";", end = " ", sep = " ")
                    print()
            #self.moveAstar()
                
        elif fallback:
            self.moveTowards(destX, destY)
            if DEBUG:
                print(self.name + " found no Astar path")
        else:
            return "fail"
        
    def duplicate(self):
        return deepcopy(self)
    
    def moveOnAstarPath(self, goal = player):
        if self.size > 1:
            self.astarPath = astarPath(self.x, self.y, goal.x, goal.y, silent = True, mapToUse = myMap, size = self.size, bigMonster=self)
        else:
            self.astarPath = astarPath(self.x, self.y, goal.x, goal.y, silent = True)
        if self.astarPath is not None:
            nextTile = self.astarPath.pop(0)
            (self.x, self.y) = (nextTile.x, nextTile.y)
            tilesinPath.extend(self.astarPath)
            print(self.name + "'s path :", end = " ")
            for (x,y) in self.astarPath:
                print (str(x) + "/" + str(y) + ";", end = " ", sep = " ")
                print()
        else:
            self.moveTowards(goal.x, goal.y)

class Projectile:
    def __init__(self, speed, sourceX, sourceY, destX, destY, explode = False, explodeRange = 0, continues = False, passesThrough = False, ghost = False):
        self.speed = speed
        self.explode = explode
        self.explodeRange = explodeRange
        self.passesThrough = passesThrough
        self.ghost = ghost
        self.dx = destX - sourceX
        self.dy = destY - sourceY
        self.continues = continues
        self.path = []
        
        i = 0
        while len(self.path) < 25:
            self.path = tdl.map.bresenham(sourceX, sourceY, destX + i * self.dx, destY + i * self.dy)
            i += 1
        
        self.origX, self.origY = self.path.pop(0) #remove the projectile coordinates
        print(self.path)
        self.PATH = list(deepcopy(self.path))
        self.relativeTravelledX = 0
        self.relativeTravelledY = 0
        self.formerX = self.origX
        self.formerY = self.origY
    
    def defineStraightChar(self):
        (firstX, firstY)= self.path[0]
        inclX = firstX - self.origX
        inclY = firstY - self.origY
        incl = (inclX, inclY)
        if incl == (1, 0) or incl == (-1, 0):
            return '-'
        elif incl == (1, -1) or incl == (-1, 1):
            return '/'
        elif incl == (0, 1) or incl == (0, -1):
            return '|'
        elif incl == (1, 1) or incl == (-1, -1):
            return chr(92)
    
    def generateNewPath(self):
        print('generating new path')
        newPath = []
        print(self.PATH)
        for (x, y) in self.PATH:
            newX = x + self.relativeTravelledX
            newY = y + self.relativeTravelledY
            print(newX, newY)
            newPath.append((x + self.relativeTravelledX, y + self.relativeTravelledY))
        self.path = newPath
        print(self.path)
            
    def moveOnPath(self, speed = None):
        global objects, FOV_recompute
        if speed is None:
            speed = self.speed
        proj = self.owner
        x = self.owner.x
        y = self.owner.y
        i = 0
        print('before loop: ', self.path)
        for i in range(speed):
            print('travelled coords:', self.relativeTravelledX, self.relativeTravelledY)
            if self.path:
                (x, y) = self.path.pop(0)
                proj.x, proj.y = x, y
                animStep(.01)
                if isBlocked(x, y) and (not self.passesThrough or myMap[x][y].blocked) and not self.ghost:
                    objects.remove(proj)
                    del proj
                    FOV_recompute = True
                    return (x, y)
                self.relativeTravelledX += x - self.formerX
                self.relativeTravelledY += y - self.formerY
                self.formerX = x
                self.formerY = y
            elif not self.continues:
                objects.remove(proj)
                del proj
                FOV_recompute = True
                return (x,y)
            else:
                print('no path')
                self.generateNewPath()
                (x, y) = self.path.pop(0)
                proj.x, proj.y = x, y
                animStep(.01)
                if isBlocked(x, y) and (not self.passesThrough or myMap[x][y].blocked) and not self.ghost:
                    objects.remove(proj)
                    del proj
                    FOV_recompute = True
                    return (x, y)
                self.relativeTravelledX += x - self.formerX
                self.relativeTravelledY += y - self.formerY
                self.formerX = x
                self.formerY = y
        FOV_recompute = True
    
def createNPCFromMapReader(attributeList):
    if attributeList[6] in ("None", "", " "):
        shop = None
    else:
        mainModule = sys.modules[__name__] #Because "main" is not defined inside itself.
        shop = getattr(mainModule, attributeList[6])
    return GameObject(int(attributeList[0]), int(attributeList[1]), attributeList[2], attributeList[3], attributeList[4], blocks = True, socialComp = getattr(dial, attributeList[5]), shopComp = shop)

class Fighter: #All NPCs, enemies and the player
    def __init__(self, hp, armor, power, accuracy, evasion, xp, deathFunction=None, maxMP = 0, knownSpells = None, critical = 5, armorPenetration = 0, lootFunction = None, lootRate = [0], shootCooldown = 0, landCooldown = 0, transferDamage = None, leechRessource = None, leechAmount = 0, buffsOnAttack = [], slots = ['head', 'torso', 'left hand', 'right hand', 'legs', 'feet'], equipmentList = [], toEquip = [], attackFunctions = [], noDirectDamage = False, pic = 'ogre.xp', description = 'Placeholder', rangedPower = 0, Ranged = None, stamina = 0, attackSpeed = 100, moveSpeed = 100, rangedSpeed = 100, resistances = {'physical': 0, 'poison': 0, 'fire': 0, 'cold': 0, 'lightning': 0, 'light': 0, 'dark': 0, 'none': 0}, attackTypes = {'physical': 100}):
        self.noVitHP = hp
        self.BASE_MAX_HP = hp
        self.hp = hp
        self.baseArmor = armor
        self.BASE_ARMOR = armor
        self.noStrengthPower = power
        self.BASE_POWER = power
        self.deathFunction = deathFunction
        self.xp = xp
        self.noDexAccuracy = accuracy
        self.BASE_ACCURACY = accuracy
        self.noDexEvasion = evasion
        self.BASE_EVASION = evasion
        self.baseCritical = critical
        self.BASE_CRITICAL = critical
        self.baseArmorPenetration = armorPenetration
        self.BASE_ARMOR_PENETRATION = armorPenetration
        self.lootFunction = lootFunction
        self.lootRate = lootRate
        self.pic = pic
        self.description = description
        self.BASE_STAMINA = stamina
        self.noConstStamina = stamina
        self.stamina = stamina
        
        self.critMultiplier = CRITICAL_MULTIPLIER
        
        self.baseAttackSpeed = attackSpeed
        self.baseMoveSpeed = moveSpeed
        self.baseRangedSpeed = rangedSpeed
        self.actionPoints = 0
        
        self.leechRessource = leechRessource
        self.leechAmount = leechAmount
        self.buffsOnAttack = buffsOnAttack
        
        self.buffList = []
        
        self.healCountdown = 25
        self.MPRegenCountdown = 10
        self.staminaRegenCountdown = 15

        self.baseShootCooldown = shootCooldown
        self.curShootCooldown = 0
        self.baseLandCooldown = landCooldown
        self.curLandCooldown = 0
        self.Ranged = Ranged
        if self.Ranged:
            Ranged.owner = self
        
        self.acidified = False
        self.acidifiedCooldown = 0

        self.noWillMP = maxMP
        self.MP = maxMP
        self.BASE_MAX_MP = maxMP
        
        self.damageText = 'unscathed'
        
        self.slots = slots
        self.equipmentList = equipmentList
        if toEquip:
            for equipment in toEquip:
                equipment.Equipment.equip(self)
                print('equipped {} on {}'.format(equipment.name, self))
        
        if knownSpells != None:
            self.knownSpells = knownSpells
            self.allSpells = knownSpells
        else:
            self.knownSpells = []
            self.allSpells = []
        
        self.hiddenSpells = []
        self.spellsOnCooldown = []
        
        self.transferDamage = transferDamage
        
        self.attackFunctions = attackFunctions
        self.noDirectDamage = noDirectDamage
        
        self.baseResistances = resistances
        self.baseAttackTypes = attackTypes

    @property
    def basePower(self):
        bonus = 0
        if self.owner == player:
            bonus = player.Player.strength
        return self.noStrengthPower + bonus
    
    @property
    def baseMaxHP(self):
        bonus = 0
        if self.owner == player:
            bonus = 5 * player.Player.vitality
        return self.noVitHP + bonus
    
    @property
    def baseAccuracy(self):
        bonus = 0
        if self.owner == player:
            bonus = 2 * player.Player.dexterity
        return self.noDexAccuracy + bonus
    
    @property
    def baseEvasion(self):
        bonus = 0
        if self.owner == player:
            bonus = player.Player.dexterity
        return self.noDexEvasion + bonus
    
    @property
    def baseMaxMP(self):
        bonus = 0
        if self.owner == player:
            bonus = 5 * player.Player.willpower
        return self.noWillMP + bonus
    
    @property
    def baseMaxStamina(self):
        bonus = 0
        if self.owner == player:
            bonus = 5* player.Player.vitality
        return self.noConstStamina + bonus
    
    @property
    def knownSpellsToNames(self, returnActualSpell=False):
        '''
        Convert list of fighter's known spells to list of names of said spells.
        This doesn't necessarily respects alphabetical order
        '''
        if returnActualSpell:
            return [spell for spell in self.knownSpells]
        else:
            return [spell.name for spell in self.knownSpells]
        
    @property
    def allSpellsToNames(self, returnActualSpell=False):
        '''
        Convert list of fighter's known spells to list of hidden names of said spells.
        This doesn't necessarily respects alphabetical order
        '''
        if returnActualSpell:
            return [spell for spell in self.allSpells]
        else:
            return [spell.name for spell in self.allSpells]

    @property
    def power(self):
        bonus = sum(equipment.powerBonus for equipment in getAllEquipped(self.owner))
        buffBonus = sum(buff.power for buff in self.buffList)
        return self.basePower + bonus + buffBonus
 
    @property
    def armor(self):
        bonus = sum(equipment.armorBonus for equipment in getAllEquipped(self.owner))
        buffBonus = sum(buff.armor for buff in self.buffList)
        return self.baseArmor + bonus + buffBonus
 
    @property
    def maxHP(self):
        bonus = sum(equipment.maxHP_Bonus for equipment in getAllEquipped(self.owner))
        buffBonus = sum(buff.maxHP for buff in self.buffList)
        return self.baseMaxHP + bonus + buffBonus

    @property
    def accuracy(self, melee = False, ranged = False):
        bonus = sum(equipment.accuracyBonus for equipment in getAllEquipped(self.owner))
        bonus += sum(buff.accuracy for buff in self.buffList)
        return self.baseAccuracy + bonus
    
    @property
    def meleeAccuracy(self):
        baseAcc = self.accuracy
        bonus = 0
        if self.owner == player:
            bonus = player.Player.getTrait('skill', 'Melee weaponry').amount * 2
        return baseAcc + bonus
    
    @property
    def rangedAccuracy(self):
        baseAcc = self.accuracy
        bonus = 0
        if self.owner == player:
            bonus = player.Player.getTrait('skill', 'Ranged weaponry').amount * 2
        return baseAcc + bonus

    @property
    def evasion(self):
        bonus = sum(equipment.evasionBonus for equipment in getAllEquipped(self.owner))
        buffBonus = sum(buff.evasion for buff in self.buffList)
        return self.baseEvasion + bonus + buffBonus

    @property
    def critical(self):
        bonus = sum(equipment.criticalBonus for equipment in getAllEquipped(self.owner))
        buffBonus = sum(buff.critical for buff in self.buffList)
        if self.owner == player and player.Player.getTrait('trait', 'Surprise attack') != 'not found' and not checkPlayerDetected():
            bonus += SURPRISE_ATTACK_CRIT
            print('player can backstab')
        return self.baseCritical + bonus + buffBonus

    @property
    def maxMP(self):
        bonus = sum(equipment.maxMP_Bonus for equipment in getAllEquipped(self.owner))
        buffBonus = sum(buff.maxMP for buff in self.buffList)
        return self.baseMaxMP + bonus + buffBonus
    
    @property
    def armorPenetration(self):
        bonus = sum(equipment.armorPenetrationBonus for equipment in getAllEquipped(self.owner))
        buffBonus = sum(buff.armorPenetration for buff in self.buffList)
        return self.baseArmorPenetration + bonus + buffBonus
    
    @property
    def maxStamina(self):
        bonus = sum(equipment.staminaBonus for equipment in getAllEquipped(self.owner))
        buffBonus = sum(buff.stamina for buff in self.buffList)
        return self.baseMaxStamina + bonus + buffBonus
    
    @property
    def resistances(self):
        types = self.baseResistances.copy()
        for equipment in getAllEquipped(self.owner):
            for key in list(equipment.resistances.keys()):
                if key in list(types.keys()):
                    types[key] += equipment.resistances[key]
                else:
                    types[key] = equipment.resistances[key]
        for buff in self.buffList:
            for key in list(buff.resistances.keys()):
                if key in list(types.keys()):
                    types[key] += buff.resistances[key]
                else:
                    types[key] = buff.resistances[key]
        return types
    
    @property
    def attackTypes(self):
        types = self.baseAttackTypes.copy()
        for equipment in getAllEquipped(self.owner):
            if equipment.slot == 'one handed' or equipment.slot == 'two handed':
                for key in list(equipment.damageTypes.keys()):
                    if key in list(types.keys()):
                        types[key] = (types[key] + equipment.damageTypes[key])//2
                    else:
                        types[key] = equipment.damageTypes[key]//2
        for buff in self.buffList:
            for key in list(buff.attackTypes.keys()):
                if key in list(types.keys()):
                    types[key] = (types[key] + buff.attackTypes[key])//2
                else:
                    types[key] = buff.attackTypes[key]//2
        return types
    
    @property
    def attackSpeed(self):
        bonus = 0
        i = 0
        for equipment in getAllEquipped(self.owner):
            if equipment.meleeWeapon and player.Player.getTrait('trait', 'Easy blows') == 'not found': #throwing weapons which can be used in melee are not considered
                i += 1
                bonus += equipment.attackSpeed
        if i <= 1:
            i = 1
        buffBonus = sum(buff.attackSpeed for buff in self.buffList)
        return self.baseAttackSpeed + round(bonus/i) + buffBonus
    
    @property
    def moveSpeed(self):
        buffBonus = sum(buff.moveSpeed for buff in self.buffList)
        return self.baseMoveSpeed + buffBonus
    
    @property
    def rangedSpeed(self):
        bonus = 0
        i = 0
        for equipment in getAllEquipped(self.owner):
            if equipment.ranged and (player.Player.getTrait('trait', 'Fast reload') == 'not found' or not equipment.attackSpeed > 0):
                i += 1
                bonus += equipment.attackSpeed
        if i <= 1:
            i = 1
        buffBonus = sum(buff.rangedSpeed for buff in self.buffList)
        return self.baseRangedSpeed + buffBonus
    
    @property
    def canTakeTurn(self):
        if not 'frozen' in convertBuffsToNames(self) and not 'stunned' in convertBuffsToNames(self):
            return True
        else:
            return False
    
    @property
    def canMove(self):
        if not 'rooted' in convertBuffsToNames(self) and not 'burdened' in convertBuffsToNames(self):
            return True
        else:
            return False
    
    def computeDamageDict(self, damage):
        damageDict = {}
        keyList = list(self.attackTypes.keys())
        i = 0
        for key in keyList:
            if i == len(keyList)-1:
                dmgList = [damageDict[dmgKey] for dmgKey in keyList if dmgKey != key]
                damageDict[key] = damage - sum(dmg for dmg in dmgList)
            else:
                damageDict[key] = round((self.attackTypes[key] * damage)/100)
            i += 1
        
        return damageDict
    
    def takeDamage(self, damageDict, damageSource, armored = False, armorPenetration=0, damageTextFunction = None):
        global lastHitter
        lastHitter = damageSource
        
        if damageTextFunction is None:
            damageTextFunction = lambda damageTaken: self.formatRawDamageText(damageTaken, '', colors.white, '', colors.white)
        
        print('DamageDict:', damageDict)
        damageTaken = {}
        keyList = list(damageDict.keys())
        for key in keyList:
            if key == 'physical' and armored:
                print('damage is armored: {} - {} + {}'.format(str(damageDict['physical']), str(self.armor), str(armorPenetration)))
                physDamage = damageDict['physical'] - (self.armor - armorPenetration)
                damageTaken[key] = physDamage - round((self.resistances[key] * physDamage)/100)
            else:
                damageTaken[key] = damageDict[key] - round((self.resistances[key] * damageDict[key])/100)
            if damageTaken[key] < 0:
                damageTaken[key] = 0
        
        damageList = [damageTaken[key] for key in keyList]
        print('damageList:', damageList)
        damage = sum(dmg for dmg in damageList)        
        #if self.owner == player and player.Player.race == 'Insectoid':
            #formerDamage = damage
        #    damage -= int(damage/10)
            #if formerDamage != damage:
            #    message('The damage was reduced to {} thanks to your chitin carapace!'.format(str(damage)), colors.sea)
        if damage > 0:
            self.hp -= damage
            self.updateDamageText()
        
        damageTextFunction(damageTaken)
        
        if self.hp <= 0:
            death=self.deathFunction
            if death is not None:
                death(self.owner)
            if self.owner != player and (not self.owner.AI or self.owner.AI.__class__.__name__ != "FriendlyMonster"):
                if player.Player.race == 'Human':
                    xp = round((self.xp * 10) / 100) + self.xp
                else:
                    xp = self.xp
                player.Fighter.xp += xp
                player.Player.baseScore += xp
        return damageTaken

    def onAttack(self, target):
        print('on attck function:', self.owner.name, target.name)
        if self.buffsOnAttack is not None:
            for buff in self.buffsOnAttack:
                dice = randint(1, 100)
                if dice <= buff[0]:
                    if buff[1] == 'burning':
                        applyBurn(target, 100)
                    if buff[1] == 'poisoned':
                        poisoned = Buff('poisoned', colors.purple, cooldown=randint(5, 10), continuousFunction=lambda fighter: randomDamage('poison', fighter, chance = 100, minDamage=1, maxDamage=10, dmgType={'poison': 100}))
                        poisoned.applyBuff(target)
        if self.leechRessource is not None:
            #hunger = self.leechRessource == 'hunger'
            HP = self.leechRessource == 'HP'
            MP = self.leechRessource == 'MP'
            #if hunger and target == player:
                #player.Player.hunger -= self.leechAmount
            if HP:
                target.Fighter.hp -= self.leechAmount
                self.heal(self.leechAmount//2)
            if MP:
                target.Fighter.MP -= self.leechAmount
                castRegenMana(self.leechAmount//2, caster = self.owner)
        if self.attackFunctions:
            for func in self.attackFunctions:
                func(self, target)
        if self.owner == player:
            print('attacker is player')
            for equipment in equipmentList:
                print(equipment.name)
                if equipment.Equipment.enchant and equipment.Equipment.enchant.functionOnAttack:
                    equipment.Equipment.enchant.functionOnAttack(target)
            
                if equipment.Equipment.enchant and equipment.Equipment.enchant.buffOnTarget:
                    for buff in equipment.Equipment.enchant.buffOnTarget:
                        print('equipment has buff:', buff.name, 'on :', target.name)
                        buff.applyBuff(target)

    def toHit(self, target, melee = False, ranged = False):
        attack = randint(1, 100)
        hit = False
        criticalHit = False
        
        statToUse = self.accuracy
        if melee:
            statToUse = self.meleeAccuracy
        elif ranged:
            statToUse = self.rangedAccuracy
        
        hitRatio = BASE_HIT_CHANCE + statToUse - target.Fighter.evasion
        if hitRatio <= 0:
            hitRatio = 1
        if hitRatio >= 96:
            hitRatio = 95

        if DEBUG:
            message(self.owner.name.capitalize() + ' rolled a ' + str(attack) + ' (target ' + str(hitRatio) + ': ' + str(BASE_HIT_CHANCE) + ' + ' + str(self.accuracy) + ' - ' + str(target.Fighter.evasion) + ')', colors.violet)

        if attack <= hitRatio:
            hit = True
            crit = randint(1, 100)
            if DEBUG:
                message(self.owner.name.capitalize() + ' rolled a ' + str(crit) + ' (target ' + str(self.critical) + ')', colors.violet)
            if crit <= self.critical:
                criticalHit = True
        return hit, criticalHit
    
    #def parry(self, attacker):
        #dice = randint(1, 100)
        #if self.owner == player and player.Player.getTrait('trait', )
    
    def formatAttackText(self, target, hit, crit, damageTaken, baseText = '{} {}hit{} {} for {}!', baseNoDmgText = '{} attack{} {} but it has no effect.'):
        textColor = {'dark_green': True, 'orange':False, 'darker_green':False, 'dark_orange':False}
        if self.owner == player:
            attackerText = 'You'
            thirdPsnAdd = ''
        elif self.owner.AI and self.owner.AI.__class__.__name__ == "FriendlyMonster" and self.owner.AI.friendlyTowards == player:
            attackerText = 'Your fellow ' + self.owner.name.capitalize()
            thirdPsnAdd = 's'
        else:
            attackerText = self.owner.name.capitalize()
            thirdPsnAdd = 's'
            textColor['orange'] = True
            textColor['dark_green'] = False
        if crit:
            critText = 'critically '
            if textColor['orange']:
                textColor['dark_orange'] = True
                textColor['orange'] = False
            else:
                textColor['darker_green'] = True
                textColor['dark_green'] = False
        else:
            critText = ''
        if target == player:
            targetText = 'you'
        else:
            targetText = target.name
        finalColor = colors.dark_green

        if hit:
            if not self.noDirectDamage:
                totalDmgText = ''
                lastDmgText = ''
                totalDamage = 0
                keyList = list(self.attackTypes.keys())
                for key in keyList:
                    if damageTaken[key] > 0:
                        if len(totalDmgText) > 0:
                            totalDmgText += lastDmgText.format(', ')
                        else:
                            totalDmgText += lastDmgText.format('')
                        lastDmgText = '{}' + str(damageTaken[key]) + ' ' + key + ' damage'
                        totalDamage += damageTaken[key]
                if len(totalDmgText) <= 0:
                    totalDmgText += lastDmgText.format('')
                else:
                    totalDmgText += lastDmgText.format(' and ')
                print(textColor)
                if totalDamage > 0:
                    for color in list(textColor.keys()):
                        if textColor[color]:
                            if color == 'dark_green':
                                finalColor = colors.dark_green
                            elif color == 'darker_green':
                                finalColor = colors.darker_green
                            elif color == 'orange':
                                finalColor = colors.orange
                            else:
                                finalColor = colors.dark_orange
                    message(baseText.format(attackerText, critText, thirdPsnAdd, targetText, totalDmgText), finalColor)
                else:
                    if self.owner == player:
                        finalColor = colors.dark_grey
                    else:
                        finalColor = colors.white
                    message(baseNoDmgText.format(attackerText, thirdPsnAdd, targetText), finalColor)
        
        else:
            if not self.owner.Player:
                if target == player:
                    message(self.owner.name.capitalize() + ' missed you!', colors.white)
                else:
                    message(self.owner.name.capitalize() + ' missed ' + target.name + '.')
            else:
                message('You missed ' + target.name + '!', colors.grey)
    
    def formatRawDamageText(self, damageTaken, text, color, noDmgText, noDmgColor, verbBe = False):
        totalDmgText = ''
        lastDmgText = ''
        totalDamage = 0
        keyList = list(damageTaken.keys())
        for key in keyList:
            if damageTaken[key] > 0:
                if len(totalDmgText) > 0:
                    totalDmgText += lastDmgText.format(', ')
                else:
                    totalDmgText += lastDmgText.format('')
                lastDmgText = '{}' + str(damageTaken[key]) + ' ' + key + ' damage'
                totalDamage += damageTaken[key]
        if len(totalDmgText) <= 0:
            totalDmgText += lastDmgText.format('')
        else:
            totalDmgText += lastDmgText.format(' and ')
        
        if self.owner == player:
            if verbBe:
                targetText = 'You are'
            else:
                targetText = 'You'
        else:
            if verbBe:
                targetText = self.owner.name.capitalize() + ' is'
            else:
                targetText = self.owner.name.capitalize()
        
        if totalDamage > 0:
            message(text.format(targetText, totalDmgText), color)
        else:
            message(noDmgText.format(targetText), noDmgColor)
    
    def attack(self, target, fromFreeAtk = False):
        global detectedPlayerThisTurn
        hit, criticalHit = self.toHit(target, melee = True)
        hitDamage = {'none': 0}
        if hit:
            if not self.noDirectDamage:
                if criticalHit:
                    if self.owner.Player and player.Player.getTrait('trait', 'Aggressive').selected:
                        damage = (randint(self.power - 2, self.power + 2) + 4) * self.critMultiplier
                    else:
                        damage = (randint(self.power - 2, self.power + 2)) * self.critMultiplier
                else:
                    if self.owner.Player and player.Player.getTrait('trait', 'Aggressive').selected:
                        damage = randint(self.power - 2, self.power + 2) + 4
                    else:
                        damage = randint(self.power - 2, self.power + 2)
                
                damageDict = self.computeDamageDict(damage)
                
                if self.canTakeTurn:
                    dmgTxtFunc = lambda damageTaken: self.formatAttackText(target, hit, criticalHit, damageTaken)
                    
                    hitDamage = target.Fighter.takeDamage(damageDict, self.owner.name, armored = True, damageTextFunction = dmgTxtFunc)
                    
            self.onAttack(target)
            if SOUND_ENABLED and self.owner != player and not player.Player.hitThisTurn and sum([hitDamage[key] for key in hitDamage.keys()]) > 0:
                player.Player.hitThisTurn = True
                playWavSound('hit.wav')
            elif self.owner == player and target.AI:
                try:
                    if not target.AI.detectedPlayer:
                        target.AI.detectedPlayer = True
                        detectedPlayerThisTurn.append(target)
                except AttributeError:
                    print('target has no detection needed')
        else:
            self.formatAttackText(target, hit, criticalHit, 0)
            if SOUND_ENABLED and self.owner == player:
                playWavSound('miss.wav')
        
        if not fromFreeAtk and self.owner == player and player.Player.getTrait('trait', 'Blade storm') != 'not found':
            traitAmount = player.Player.getTrait('skill', 'Light weapons').amount
            dice = randint(1, 100)
            onlyLight = True
            chancePerLvl = 3
            for eq in getEquippedInHands():
                if 'heavy' in eq.Equipment.type and not eq.Equipment.ranged:
                    onlyLight = False
            if dice <= (traitAmount-3)*chancePerLvl and onlyLight:
                message('You gain a free attack!', colors.green)
                castMultipleAttacks(player, None, attacksNum = 1)
            
    def heal(self, amount):
        self.hp += amount
        if self.hp > self.maxHP:
            self.hp = self.maxHP
    
    def updateDamageText(self):
        self.hpRatio = ((self.hp / self.maxHP) * 100)
        if self.hpRatio == 100:
            self.damageText = 'unscathed'
        if self.hpRatio < 95 and self.hpRatio >= 75:
            self.damageText = 'healthy'
        elif self.hpRatio < 75 and self.hpRatio >= 50:
            self.damageText = 'lightly wounded'
        elif self.hpRatio < 50 and self.hpRatio >= 25:
            self.damageText = 'wounded'
        elif self.hpRatio < 25 and self.hpRatio > 0:
            self.damageText = 'near death'
        elif self.hpRatio == 0:
            self.damageText = None
    
    def acidify(self, cooldown = 6):
        self.acidified = True
        self.acidifiedCooldown = cooldown
        curArmor = self.armor - self.baseArmor
        self.baseArmor = -curArmor
    
    def fullDescription(self, width):
        fullDesc = []
        fullDesc.extend(textwrap.wrap(self.description, width))
        fighterStats = []
        
        if self.power != 0:
            fighterStats.append('Power: ' + str(self.power))
        if self.armor != 0:
            fighterStats.append('Armor: ' + str(self.armor))
        if self.maxHP != 0:
            fighterStats.append('HP: ' + str(self.maxHP))
        if self.maxMP != 0:
            fighterStats.append('MP: ' + str(self.maxMP))
        if self.accuracy != 0:
            fighterStats.append('Accuracy: ' + str(self.accuracy))
        if self.evasion != 0:
            fighterStats.append('Evasion: ' + str(self.evasion))
        if self.critical != 0:
            fighterStats.append('Critical: ' + str(self.critical))
        if self.armorPenetration != 0:
            fighterStats.append('Armor penetration: ' + str(self.armorPenetration))
        #weightText = 'Weight: ' + str(self.weight)
        #fullDesc.append(weightText)
        fullDesc.extend(fighterStats)
        if self.buffsOnAttack:
            text = 'Attack: '
            for buff in self.buffsOnAttack:
                text += buff[1]
            fullDesc.append(text.capitalize())
        return fullDesc
    
    def displayFighter(self, posX = 0):
        global FOV_recompute, menuWindows
        '''
        asciiFile = os.path.join(absAsciiPath, self.pic)
        xpRawString = gzip.open(asciiFile, "r").read()
        convertedString = xpRawString
        attributes = xpL.load_xp_string(convertedString)
        picWidth = int(attributes["width"])
        picHeight = int(attributes["height"])
        print("Pic Height = ", picHeight)
        lData = attributes["layer_data"]
        '''
        width = 40#picWidth + 15
        if width < len(self.owner.name) + 3:
            width = len(self.owner.name) + 3
        desc = self.fullDescription(width - 2)
        descriptionHeight = len(desc)
        if desc == '':
            descriptionHeight = 0
        height = descriptionHeight + 6 #+ int(picHeight) + 1
        
        if menuWindows:
            for mWindow in menuWindows:
                mWindow.clear()
                print('CLEARED {} WINDOW OF TYPE {}'.format(mWindow.name, mWindow.type))
                ind = menuWindows.index(mWindow)
                del menuWindows[ind]
                print('Deleted')
                tdl.flush()
        FOV_recompute = True
        #Update()
        window = NamedConsole('displayFighter', width, height)
        print('Created disp window')
        window.clear()
        menuWindows.append(window)

        for k in range(width):
            window.draw_char(k, 0, chr(196))
        window.draw_char(0, 0, chr(218))
        window.draw_char(k, 0, chr(191))
        kMax = k
        for l in range(height):
            if l > 0:
                window.draw_char(0, l, chr(179))
                window.draw_char(kMax, l, chr(179))
        lMax = l
        for m in range(width):
            window.draw_char(m, lMax, chr(196))
        window.draw_char(0, lMax, chr(192))
        window.draw_char(kMax, lMax, chr(217))
        startY = 4
        startX = 3
        #layerInd = int(0)
        #for layerInd in range(len(lData)):
        #    xpL.load_layer_to_console(window, lData[layerInd], startY, startX)
        
        #for line in self.pic:
            #x = 2
            #for char in line:
                #window.draw_char(x, y, char[0], char[1], char[2])
                #x += 1
            #y += 1
        
        window.draw_str(1, 1, self.owner.name.capitalize() + ':', fg = colors.amber, bg = None)
        for i, line in enumerate(desc):
            #window.draw_str(1, int(picHeight) + 5 + i, desc[i], fg = colors.white)
            window.draw_str(1, 2 + i, desc[i], fg = colors.white)
        posY = MID_HEIGHT - height//2
        root.blit(window, posX, posY, width, height, 0, 0)
        
        menuWindows.append(window)
        FOV_recompute = True
        tdl.flush()

class RangedNPC:
    def __init__(self, shotRange, power, accuracy, critical = 5, armorPenetration = 0, buffsOnAttack = [], leechRessource = '', attackFunctions = [], shootMessage = ' shoots {} for ', projChar = '/', projColor = colors.light_orange, continues = False, passesThrough = False, ghost = False):
        self.shotRange = shotRange
        self.power = power
        self.accuracy = accuracy
        self.critical = critical
        self.armorPenetration = armorPenetration
        self.buffsOnAttack = buffsOnAttack
        self.leechRessource = leechRessource
        self.attackFunctions = attackFunctions
        self.shootMessage = shootMessage
        
        self.projChar = projChar
        self.projColor = projColor
        self.continues = continues
        self.passesThrough = passesThrough
        self.ghost = ghost
    
    def onAttack(self, target):
        print('on attck function:', self.owner.owner.name, target.name)
        if self.buffsOnAttack is not None:
            for buff in self.buffsOnAttack:
                dice = randint(1, 100)
                if dice <= buff[0]:
                    if buff[1] == 'burning':
                        applyBurn(target, 100)
                    if buff[1] == 'poisoned':
                        poisoned = Buff('poisoned', colors.purple, cooldown=randint(5, 10), continuousFunction=lambda fighter: randomDamage('poison', fighter, chance = 100, minDamage=1, maxDamage=10, dmgType={'poison': 100}))
                        poisoned.applyBuff(target)
        if self.leechRessource is not None:
            #hunger = self.leechRessource == 'hunger'
            HP = self.leechRessource == 'HP'
            MP = self.leechRessource == 'MP'
            #if hunger and target == player:
                #player.Player.hunger -= self.leechAmount
            if HP:
                target.Fighter.hp -= self.leechAmount
                self.owner.heal(self.leechAmount//2)
            if MP:
                target.Fighter.MP -= self.leechAmount
                castRegenMana(self.leechAmount//2, caster = self.owner.owner)
        if self.attackFunctions:
            for func in self.attackFunctions:
                func(self, target)

    def toHit(self, target, melee = False, ranged = False):
        attack = randint(1, 100)
        hit = False
        criticalHit = False
        
        statToUse = self.accuracy
        if melee:
            statToUse = self.meleeAccuracy
        elif ranged:
            statToUse = self.rangedAccuracy
        
        hitRatio = BASE_HIT_CHANCE + statToUse - target.Fighter.evasion
        if hitRatio <= 0:
            hitRatio = 1
        if hitRatio >= 96:
            hitRatio = 95

        if DEBUG:
            message(self.owner.owner.name.capitalize() + ' rolled a ' + str(attack) + ' (target ' + str(hitRatio) + ': ' + str(BASE_HIT_CHANCE) + ' + ' + str(self.accuracy) + ' - ' + str(target.Fighter.evasion) + ')', colors.violet)

        if attack <= hitRatio:
            hit = True
            crit = randint(1, 100)
            if DEBUG:
                message(self.owner.owner.name.capitalize() + ' rolled a ' + str(crit) + ' (target ' + str(self.critical) + ')', colors.violet)
            if crit <= self.critical:
                criticalHit = True
        return hit, criticalHit

    def shoot(self, target):
        global FOV_recompute
        [hit, criticalHit] = self.toHit(target, ranged = True)
        projectile(self.owner.owner.x, self.owner.owner.y, target.x, target.y, self.projChar, self.projColor, self.continues, self.passesThrough, self.ghost)
        FOV_recompute = True
        damageTaken = 0
        if hit:
            penetratedArmor = target.Fighter.armor - self.armorPenetration
            if penetratedArmor < 0:
                penetratedArmor = 0
            if criticalHit:
                damage = (randint(self.power - 2, self.power + 2) * self.critMultiplier)
            else:
                damage = randint(self.power - 2, self.power + 2)
            if self.owner.canTakeTurn:
                damageDict = self.owner.computeDamageDict(damage)
                dmgTxtFunc = lambda damageTaken: self.owner.formatAttackText(target, hit, criticalHit, damageTaken, baseText = '{} {}shoot{} {} for {}!', baseNoDmgText = '{} shoot{} {} but it has no effect.')
                target.Fighter.takeDamage(damageDict, self.owner.owner.name, armored = True, damageTextFunction = dmgTxtFunc)
            self.onAttack(target)
        else:
            self.owner.formatAttackText(target, hit, criticalHit, damageTaken, baseText = '{} {}shoot{} {} for {}!', baseNoDmgText = '{} shoot{} {} but it has no effect.')
        
class Pathfinder(threading.Thread):
    def __init__(self, mob, goalX, goalY, mapToUse = None):
        threading.Thread.__init__(self)
        self.mob = mob
        self.goalX = goalX
        self.goalY = goalY
        if mapToUse is None:
            self.mapToUse = myMap
            if myMap is None:
                raise TypeError("MYMAP IS NONE, PF INIT")
                traceback.print_exc()
                os._exit(-1)
        else:
            self.mapToUse = mapToUse
        
    def run(self):
        if self.mob.size > 1:
            self.mob.astarPath = astarPath(self.mob.x, self.mob.y, self.goalX, self.goalY, silent = True, mapToUse = self.mapToUse, size = self.mob.size, bigMonster=self.mob)
        else:
            self.mob.astarPath = astarPath(self.mob.x, self.mob.y, self.goalX, self.goalY, silent = True)

class TargetSelector:
    def __init__(self):
        self.selectedTarget = None
        self.targets = []
        self.detectedPlayer = False

    def setFuckingTarget(self, target, targets):
        self.selectedTarget = target
        self.targets = targets
    
    def tryDetection(self):
        global detectedPlayerThisTurn
        dice = randint(1, 100)
        playerStealth = player.Player.stealthValue(self.owner)
        if dice >= playerStealth or dice >= 96:
            if not self.detectedPlayer:
                detectedPlayerThisTurn.append(self.owner)
                #message('{} detects you!'.format(self.owner.name.capitalize()), self.owner.color)
            self.detectedPlayer = True
            return True
        else:
            return False
    
    def computeMonsterFOV(self, sightRadius = SIGHT_RADIUS):
        monster = self.owner
        size = monster.size
        if size > 2:
            monster = monster.sizeComponents[size] #taking the middlest monster part as the source of the FOV (working for sizes 3 and 4 only)
        baseVisibleTiles = tdl.map.quick_fov(x = monster.x, y = monster.y,callback = isVisibleTile , fov = FOV_ALGO, radius = SIGHT_RADIUS + size//2, lightWalls = FOV_LIGHT_WALLS)
        '''
        if monster.size <= 1:
            return baseVisibleTiles
        else:
            print('monster is big')
            print('visible tiles before iteration:', baseVisibleTiles)
            for monsterPart in monster.sizeComponents:
                newVisibleTiles = tdl.map.quick_fov(x = monster.x, y = monster.y,callback = isVisibleTile , fov = FOV_ALGO, radius = SIGHT_RADIUS, lightWalls = FOV_LIGHT_WALLS)
                for tile in newVisibleTiles:
                    print('new tile is:', tile)
                    if not tile in baseVisibleTiles:
                        print('added tile')
                        baseVisibleTiles.append(tile)
                        '''
        return baseVisibleTiles

    def selectTarget(self):
        monster = self.owner
        self.targets = []
        self.selectedTarget = None
        self.setFuckingTarget(None, [])
        priorityTargetFound = False
        
        if self.owner.Fighter.canTakeTurn and monster.distanceTo(player) <= 20:
            monsterVisibleTiles = self.computeMonsterFOV()
            #print(monster.name + " is less than 15 tiles to player.")
            for object in objects:
                if (object.x, object.y) in monsterVisibleTiles and (object == player or (object.AI and object.AI.__class__.__name__ == "FriendlyMonster" and object.AI.friendlyTowards == player)):
                    if object == player and (self.detectedPlayer or self.tryDetection()):
                        self.targets.append(object)
                    elif object != player:
                        self.targets.append(object)
                elif object == player and (not (player.x, player.y) in monsterVisibleTiles):
                    print("WAAAAARNING")
                    print("+++++++++++++++++++++++++++++++++++++++++++++++++")
                    print("-------------------------------------------------")
                    print("PLAYER NOT VISBLE FROM MONSTER !!!!!!!!!!!!!!!!!!")
                    print(monsterVisibleTiles)
                    print(player.x, player.y, sep = ";")
                    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                    self.detectedPlayer = False
            if DEBUG:
                print(monster.name.capitalize() + " can target", end=" ")
                if self.targets:
                    for loop in range(len(self.targets)):
                        pass
                        print(self.targets[loop].name.capitalize() + ", ", sep ="", end ="")
                else:
                    pass
                    print("absolutely nothing but nothingness.", end ="")
            if self.targets:
                if player in self.targets: #Target player in priority
                    self.selectedTarget = player
                    print("PLAYER IN TARGETS")
                    print(self.selectedTarget)
                    try:
                        self.targets.remove(self.targets.index(player))
                    except:
                        print("================ERROR==================")
                        for target in self.targets:
                            print(target.name)
                        print("=======================================")
                    if monster.distanceTo(player) < 2:
                        priorityTargetFound = True
                print("BEFORE PRIORITY : {}".format(self.selectedTarget.name))
                if not priorityTargetFound:
                    for enemyIndex in range(len(self.targets)):
                        enemy = self.targets[enemyIndex]
                        if monster.distanceTo(enemy) < 2:
                            print("PRIORITIZING ENEMY {}".format(enemy.name))
                            self.selectedTarget = enemy
                        else:
                            if self.selectedTarget == None or monster.distanceTo(self.selectedTarget) > monster.distanceTo(enemy):
                                self.selectedTarget = enemy
                else:
                    print("NO PRIORITY, TARGET IS {}".format(self.selectedTarget.name))

class BasicMonster(TargetSelector): #Basic monsters' AI
    def __init__(self, wanderer = True):
        TargetSelector.__init__(self)
        self.dumbCounter = 0
        self.failCounter = 0
        self.didRecalcThisTurn = False
        self.wanderer = wanderer
        self.futureCoords = (0, 0)
        #super(TargetSelector, self).__init__()
    
    def takeTurn(self):
        self.takeBasicTurn()
    
    def wander(self):
        if self.wanderer:
            monster = self.owner
            dx, dy = randint(-1, 1), randint(-1, 1)
            x, y = self.owner.x + dx, self.owner.y + dy
            print('wandering, chasm:', myMap[x][y].chasm)
            if self.owner.flying or not myMap[x][y].chasm:
                #print('moving')
                monster.move(dx, dy) #wandering
                self.futureCoords = (x, y)

    def takeBasicTurn(self):
        global mustCalculate
        monster = self.owner
        self.dumbCounter = 0
        self.failCounter = 0
        self.didRecalcThisTurn = False
        monsters = [monster]
        if monster.size > 1:
            for newM in monster.sizeComponents:
                monsters.append(newM)
        
        while monster.Fighter.actionPoints > 0:
            if self.owner.Fighter.canTakeTurn and monster.distanceTo(player) <= 20:
                self.selectTarget()
                if self.selectedTarget is not None:
                    print("SELECTED TARGET IS NOT NONE")
                    for mons in monsters:
                        dx, dy = mons.x - monster.x, mons.y - monster.y
                        fx, fy = monster.x, monster.y #self.futureCoords
                        if self.selectedTarget.distanceToCoords(fx+dx, fy+dy) < 2:
                            mons.Fighter.attack(self.selectedTarget)
                            monster.Fighter.actionPoints -= monster.Fighter.attackSpeed
                            break
                    else:
                        print("TRYING TO MOVE")
                        self.tryMove()
                        monster.Fighter.actionPoints -= monster.Fighter.moveSpeed + myMap[monster.x][monster.y].moveCost(monster.flying)
                else:
                    print("No target, still trying to move")
                    self.tryMove()
                    monster.Fighter.actionPoints -= monster.Fighter.moveSpeed + myMap[monster.x][monster.y].moveCost(monster.flying)
                    
            elif self.owner.Fighter.canTakeTurn:
                self.wander()
                monster.Fighter.actionPoints -= monster.Fighter.moveSpeed + myMap[monster.x][monster.y].moveCost(monster.flying)
            
            elif not monster.Fighter.canTakeTurn:
                monster.Fighter.actionPoints -= 100
    
    def tryMove(self):
        global mustCalculate
        monster = self.owner
        if monster.Fighter.canTakeTurn and monster.distanceTo(player) >= 2:
            #print("IN TRYMOVE BLOCK")
            print("SELECTED TARGET : {}".format(self.selectedTarget))
            pathState = "fail"
            diagPathState = None
            forceRecalculate = False
            if monster.astarPath and ((not self.selectedTarget) or self.didRecalcThisTurn):
                #print("Found astarPath")
                potentialX = int(monster.astarPath[0].x)
                potentialY = int(monster.astarPath[0].y)
                '''
                if monster.distanceToCoords(potentialX, potentialY) > monster.distanceToCoords(int(self.selectedTarget.x), int(self.selectedTarget.y)):
                    if self.dumbCounter < 1:
                        self.dumbCounter += 1
                        forceRecalculate = True
                    else:
                        message("{} was too dumb to try to find a new path.".format(monster.name))
                '''
                        
                if not monster.astarPath[0].blocked and not forceRecalculate:
                    #print("Not blocked")
                    #print("ASTARX {} | ASTARY {}".format(monster.astarPath[0].x, monster.astarPath[0].y))
                    x = int(monster.astarPath[0].x)
                    y = int(monster.astarPath[0].y)
                    if x == monster.x and y == monster.y:
                        #print("Next step is identical to monster current position")
                        if len(monster.astarPath) > 1:
                            x = int(monster.astarPath[1].x)
                            y = int(monster.astarPath[1].y)
                        else:
                            print("Astar path is way too short")
                            print(monster.astarPath)
                    monster.moveTo(x, y)
                    monster.astarPath.remove(monster.astarPath[0])
                    self.futureCoords = (x, y)

                else:
                    #print("Blocked")
                    if self.selectedTarget and self.failCounter <= MAX_ASTAR_FAILS:
                        #print("Recalculating")
                        self.didRecalcThisTurn = True
                        self.failCounter += 1
                        mustCalculate = True
                        mobsToCalculate.append(monster)
                    else:
                        self.wander()
                    
            elif not monster.astarPath or pathState == "fail":
                if self.selectedTarget and self.failCounter <= MAX_ASTAR_FAILS:
                    print("Trying to calculate")
                    mustCalculate = True
                    self.didRecalcThisTurn = True
                    self.failCounter += 1
                    mobsToCalculate.append(monster)
                else:
                    print("No target")
                    self.wander()


class Charger:
    def __init__(self):
        self.chargePath = []
        self.chargePathSigns = []
        self.charging = False
    
    def defineChargePath(self, target):
        self.charging = True
        print('creating charge path from {} to {}'.format(self.owner.name, target.name))
        monster = self.owner
        (sourceX, sourceY) = (monster.x, monster.y)
        (destX, destY) = (target.x, target.y)
        line = tdl.map.bresenham(sourceX, sourceY, destX, destY)
        newLine = []
        if len(line) > 1:
            dx = destX - sourceX
            dy = destY - sourceY
            (x, y) = line[len(line) - 1]
            counter = 0
            while counter < 25:
                newX = x + dx
                newY = y + dy
                tempLine = tdl.map.bresenham(x, y, newX, newY)
                dx = newX - x
                dy = newY - y
                x = newX
                y = newY
                counter += 1
                del tempLine[0]
                newLine.extend(tempLine)
                if newX >= MAP_WIDTH or newY >= MAP_HEIGHT or newX <= 0 or newY <= 0:
                    break
        line.extend(newLine)
        self.chargePath = line
        print('charge path of {}:'.format(self.owner.name), self.chargePath)
        for (x, y) in self.chargePath:
            if x >= MAP_WIDTH or y >= MAP_HEIGHT or x <= 0 or y <= 0:
                self.chargePath.remove((x, y))
            elif not (x, y) == (monster.x, monster.y) and not myMap[x][y].blocked:
                sign = GameObject(x, y, '.', 'chargePath', color = colors.red, Ghost = True)
                self.chargePathSigns.append(sign)
                objects.append(sign)
                sign.sendToBack()
        print('final charge path of {}:'.format(self.owner.name), self.chargePath)

    def charge(self):
        global FOV_recompute
        line = self.chargePath
        monster = self.owner
        (firstX, firstY)= line[1]
        inclX = firstX - monster.x
        inclY = firstY - monster.y
        incl = (inclX, inclY)
        print(incl)
        if incl == (1, 0) or incl == (-1, 0):
            possibleKnock = [[0, -1], [0, 1]]
        elif incl == (0, 1) or incl == (0, -1):
            possibleKnock = [[1, 0], [-1, 0]]
        elif incl == (1, -1) or incl == (-1, 1):
            possibleKnock = [[-1, -1], [1, 1]]
        else:
            possibleKnock = [[1, -1], [-1, 1]]
        print(possibleKnock)
        dragging = False
        dragged = None
        for i in range(len(line)):
            (x, y) = line.pop(0)
            (pinnedX, pinnedY) = line[0]
            for object in objects:
                if object.x == x and object.y == y and object.Fighter and not object == monster:
                    if not dragging:
                        dragging = True
                        dragged = object
                        message('{} is pinned by {}!'.format(object.name.capitalize(), monster.name), colors.red)
                    elif not object == dragged:
                        choice = randint(0, 1)
                        newX = x + possibleKnock[choice][0]
                        newY = y + possibleKnock[choice][1]
                        otherX = x + possibleKnock[(choice-1) ** 2][0]
                        otherY = y + possibleKnock[(choice-1) ** 2][1]
                        if not isBlocked(newX, newY):
                            object.x = newX
                            object.y = newY
                        elif not isBlocked(otherX, otherY):
                            object.x = otherX
                            object.y = otherY
                        else:
                            myMap[newX][newY].baseBlocked = False
                            myMap[newX][newY].block_sight = False
                            myMap[newX][newY].baseCharacter = None
                            myMap[newX][newY].wall = False
                            for cx in range(newX - 1, newX + 1):
                                for cy in range(newY -1, newY + 1):
                                    myMap[cx][cy].clearance = checkTileClearance(myMap, cx, cy)
                            object.x = newX
                            object.y = newY
                            damageDict = monster.Fighter.computeDamageDict(randint(monster.Fighter.power - 5, monster.Fighter.power + 5))
                            dmgTxtFunc = lambda damageTaken: object.Fighter.formatRawDamageText(damageTaken, '{} slammed into the wall for {}!', colors.red, '{} is slammed into the wall but it has no effect', colors.white, True)
                            object.Fighter.takeDamage(damageDict, "{}'s charge".format(monster.name), damageTextFunction = dmgTxtFunc)
                            
            if not myMap[x][y].blocked:
                monster.x, monster.y = x, y
                if dragging:
                    dragged.x, dragged.y = pinnedX, pinnedY
                animStep(.01)
            else:
                if dragging:
                    print(x, y)
                    myMap[x][y].baseBlocked = False
                    myMap[x][y].block_sight = False
                    myMap[x][y].baseCharacter = None
                    myMap[x][y].wall = False
                    dragged.x = x
                    dragged.y = y
                    damageDict = monster.Fighter.computeDamageDict(randint(monster.Fighter.power , monster.Fighter.power + 10))
                    dmgTxtFunc = lambda damageTaken: dragged.Fighter.formatRawDamageText(damageTaken, '{} slammed into the wall by the force of the charge!', colors.red, '{} slammed into the wall but it has no effect.', colors.white, True)
                    dragged.Fighter.takeDamage(damageDict, "{}'s charge".format(monster.name), damageTextFunction = dmgTxtFunc)
                    
                break

        self.chargePath = []
        for sign in self.chargePathSigns:
            if sign in objects:
                objects.remove(sign)
        self.chargePathSigns = []
        FOV_recompute = True
        self.charging = False

'''
class FastMonster(BasicMonster):
    def __init__(self, speed, wanderer = True):
        BasicMonster.__init__(self, wanderer)
        self.speed = speed
    
    def takeTurn(self):
        for loop in range(self.speed):
            self.takeBasicTurn() #for some reason when moving only one tile it won't attack as a second action
'''

class Fleeing(BasicMonster):
    def __init__(self, wanderer = True):
        BasicMonster.__init__(self, wanderer)

    def flee(self):
        monster = self.owner
        bestX = monster.x
        bestY = monster.y
        if self.owner.Fighter.canTakeTurn and monster.distanceTo(player) <= 20:
            monsterVisibleTiles = self.computeMonsterFOV()
            for x in range(monster.x - SIGHT_RADIUS - 1, monster.x + SIGHT_RADIUS + 1):
                for y in range(monster.y - SIGHT_RADIUS - 1, monster.y + SIGHT_RADIUS + 1):
                    if (x, y) in monsterVisibleTiles and player.distanceToCoords(x, y) > player.distanceToCoords(bestX, bestY) and not isBlocked(x, y):
                        bestX = x
                        bestY = y
            fleePoint = GameObject(bestX, bestY, char = None, name = 'fleePoint', color = None, Ghost = True)
            self.selectedTarget = fleePoint
            if self.selectedTarget is not None:
                print("SELECTED TARGET IS NOT NONE")
                if monster.distanceTo(self.selectedTarget) < 2:
                    monster.Fighter.attack(self.selectedTarget)
                else:
                    print("TRYING TO MOVE")
                    self.tryMove()
            else:
                print("No target, still trying to move")
                self.tryMove()
    
    def takeTurn(self):
        monster = self.owner
        if self.owner.Fighter.canTakeTurn and monster.distanceTo(player) <= 20:
            self.flee()
                
        elif self.owner.Fighter.canTakeTurn:
            self.wander()

class Shooter(Fleeing):
    def __init__(self, meleeFighter = True, wanderer = True):
        Fleeing.__init__(self, wanderer)
        self.meleeFighter = meleeFighter
    
    def takeTurn(self):
        global mustCalculate
        monster = self.owner
        rangedComp = monster.Fighter.Ranged
        self.dumbCounter = 0
        self.failCounter = 0
        self.didRecalcThisTurn = False
        
        if self.owner.Fighter.canTakeTurn and monster.distanceTo(player) <= 20:
            self.selectTarget()
            if self.selectedTarget is not None:
                print("SELECTED TARGET IS NOT NONE")
                if monster.distanceTo(self.selectedTarget) < 2:
                    if self.meleeFighter:
                        monster.Fighter.attack(self.selectedTarget)
                    else:
                        self.flee()
                elif monster.distanceTo(self.selectedTarget) <= rangedComp.shotRange:
                    line = tdl.map.bresenham(monster.x, monster.y, self.selectedTarget.x, self.selectedTarget.y)
                    obstructed = False
                    for (x, y) in line:
                        if isBlocked(x, y) and (x, y) != (monster.x, monster.y) and (x, y) != (self.selectedTarget.x, self.selectedTarget.y) and not rangedComp.passesThrough:
                            obstructed = True
                            break
                    if obstructed:
                        print('OBSTRUCTED')
                        self.flee()
                    else:
                        print("SHOOTING")
                        rangedComp.shoot(self.selectedTarget)
                elif monster.distanceTo(self.selectedTarget) > rangedComp.shotRange:
                    print("TRYING TO MOVE")
                    self.tryMove()
            else:
                print("No target, still trying to move")
                self.tryMove()
                
        elif self.owner.Fighter.canTakeTurn:
            self.wander()

class HostileStationnary(TargetSelector):
    def __init__(self):
        TargetSelector.__init__(self)

    def takeTurn(self):
        monster = self.owner
        if self.owner.Fighter.canTakeTurn:
            self.selectTarget()
            if self.selectedTarget is not None:
                if monster.distanceTo(self.selectedTarget) < 2:
                    monster.Fighter.attack(self.selectedTarget)

class Immobile:
    def takeTurn(self):
        monster = self.owner
        return

class SplosionAI:
    def takeTurn(self):
        monster = self.owner
        if (monster.x, monster.y) in visibleTiles: #chasing the player
            if monster.distanceTo(player) >= 3:
                monster.moveTowards(player.x, player.y)
            elif player.Fighter.hp > 0 and monster.Fighter.canTakeTurn:
                monsterArmageddon(monster.name, monster.x, monster.y)
        else:
            monster.move(randint(-1, 1), randint(-1, 1))

class ConfusedMonster:
    def __init__(self, old_AI, numberTurns=CONFUSE_NUMBER_TURNS):
        self.old_AI = old_AI
        self.numberTurns = numberTurns
        self.detectedPlayer = False
 
    def takeTurn(self):
        if self.old_AI.__class__.__name__ != 'HostileStationnary' and self.old_AI.__class__.__name__ != 'Immobile':
            if self.numberTurns > 0:  
                self.owner.move(randint(-1, 1), randint(-1, 1))
                self.numberTurns -= 1
            else:
                self.owner.AI = self.old_AI
                message('The ' + self.owner.name + ' is no longer confused!', colors.red)
        else:
            if self.numberTurns > 0:  
                return
            else:
                self.owner.AI = self.old_AI
                message('The ' + self.owner.name + ' is no longer confused!', colors.red)
            
class FriendlyMonster:
    def __init__(self, friendlyTowards = player):
        self.friendlyTowards = friendlyTowards
    
    def takeTurn(self):
        monster = self.owner
        targets = []
        selectedTarget = None
        monsterVisibleTiles = tdl.map.quick_fov(x = monster.x, y = monster.y,callback = isVisibleTile , fov = FOV_ALGO, radius = SIGHT_RADIUS, lightWalls = FOV_LIGHT_WALLS)
        if self.friendlyTowards == player and self.owner.Fighter.canTakeTurn: #If the monster is friendly towards the player
            for object in objects:
                if (object.x, object.y) in monsterVisibleTiles and object.AI and object.AI.__class__.__name__ != "FriendlyMonster" and object.Fighter and object.Fighter.hp > 0:
                    targets.append(object)
            if DEBUG:
                print(monster.name.capitalize() + " can target", end=" ")
                if targets:
                    for loop in range(len(targets)):
                        print(targets[loop].name.capitalize() + ", ", sep ="", end ="")
                else:
                    print("absolutely nothing but nothingness.", end ="")
                print()
            if targets:
                for enemyIndex in range(len(targets)):
                    enemy = targets[enemyIndex]
                    if monster.distanceTo(enemy) < 2:
                        selectedTarget = enemy
                        print(monster.name.capitalize() + " is targeting " + selectedTarget.name)
                    else:
                        if selectedTarget == None or monster.distanceTo(selectedTarget) > monster.distanceTo(enemy):
                            selectedTarget = enemy
            if selectedTarget is not None:
                if monster.distanceTo(selectedTarget) < 2:
                    monster.Fighter.attack(selectedTarget)
                else:
                    state = monster.moveAstar(selectedTarget.x, selectedTarget.y, fallback = False)
                    if state == "fail":
                        diagState = checkDiagonals(monster, selectedTarget)
                        if diagState is None:
                            monster.moveTowards(selectedTarget.x, selectedTarget.y)
            else:
                if monster.Fighter.canTakeTurn and monster.distanceTo(player) >= 2:
                    if (player.x, player.y) in monsterVisibleTiles:
                        pathState = monster.moveAstar(player.x, player.y, fallback = False)
                        diagPathState = None
                        if pathState == "fail" or not monster.astarPath:
                                if monster.distanceTo(player) <= 20 and not (monster.x == player.x and monster.y == player.y):
                                    oldX, oldY = monster.x, monster.y
                                    monster.moveTowards(player.x, player.y)
                                    if oldX == monster.x and oldY == monster.y: #If monster didn't move after moveTowards
                                        diagPathState = checkDiagonals(monster, player)
                                        if diagPathState is None:
                                            print(monster.name.capitalize() + " didn't manage to move at all")
                    else:                    
                        monster.move(randint(-1, 1), randint(-1, 1)) #wandering
        else:
            pass #Implement here code in case the monster is friendly towards another monster
    
class Spellcaster(Fleeing):
    def __init__(self, wanderer = True, meleeFighter = True):
        Fleeing.__init__(self, wanderer)
        self.meleeFighter = meleeFighter

    def takeTurn(self):
        global mustCalculate
        monster = self.owner
        self.dumbCounter = 0
        self.failCounter = 0
        self.didRecalcThisTurn = False
        
        if self.owner.Fighter.canTakeTurn and monster.distanceTo(player) <= 20:
            self.selectTarget()
            if self.selectedTarget is not None:
                print("SELECTED TARGET IS NOT NONE")
                choseSpell = True
                if len(monster.Fighter.knownSpells) > 0:
                    randSpell = randint(0, len(monster.Fighter.knownSpells) - 1)
                    firstSpell = randSpell
                    action = None
                    while action is None:
                        chosenSpell = monster.Fighter.knownSpells[randSpell]
                        action = chosenSpell.cast(monster, self.selectedTarget)
                        if action == 'cancelled':
                            action = None
                            randSpell += 1
                            if randSpell == firstSpell:
                                choseSpell = False
                                break
                            if randSpell >= len(monster.Fighter.knownSpells):
                                randSpell = 0
                        else:
                            break
                else:
                    choseSpell = False
                
                if not choseSpell:
                    if monster.distanceTo(self.selectedTarget) < 2 and self.meleeFighter:
                        monster.Fighter.attack(self.selectedTarget)
                    else:
                        self.flee()
            else:
                print("No target, still trying to move")
                self.tryMove()
                
        elif self.owner.Fighter.canTakeTurn:
            self.wander()

class Player:
    def __init__(self, name, strength, dexterity, vitality, willpower, load, race, classes, allTraits, levelUpStats, baseHunger = BASE_HUNGER, speed = 'average', speedChance = 5, skillpoints = 0, baseStealth=0, unlockableTraits = []):
        self.name = name

        self.baseStrength = strength
        self.BASE_STRENGTH = strength
        self.baseDexterity = dexterity
        self.BASE_DEXTERITY = dexterity
        self.baseVitality = vitality
        self.BASE_VITALITY = vitality
        self.baseWillpower = willpower
        self.BASE_WILLPOWER = willpower
        self.baseMaxWeight = load
        self.BASE_STEALTH = baseStealth
        self.baseStealth = baseStealth

        self.race = race
        self.classes = classes
        self.allTraits = allTraits
        self.levelUpStats = levelUpStats
        #self.hunger = baseHunger
        #self.hungerStatus = "full"
        self.attackedSlowly = False
        self.slowAttackCooldown = 0
        self.speed = speed #or 'slow' or 'fast'
        self.speedChance = speedChance
        self.hpTextColor = colors.darker_green
        
        self.unlockableTraits = unlockableTraits
        
        self.skills = []
        for skill in self.allTraits:
            if skill.type == 'skill':
                self.skills.append(skill)
        self.traits = []
        for trait in self.allTraits:
            if trait.type == 'trait':
                self.traits.append(trait)
        self.skillpoints = skillpoints
        
        self.essences = {'Gluttony': 0, 'Wrath': 0, 'Lust': 0, 'Pride': 0, 'Envy': 0, 'Greed': 0, 'Sloth': 0}
        
        if self.race == 'Werewolf':
            self.human = 150
            self.wolf = 30
            self.shapeshift = 'human'
            self.shapeshifted = True
        
        if self.race == 'Virus ':
            self.HOST_DEATH = 500
            self.hostDeath = 0
            self.inHost = False
            self.timeOutsideLeft = 50
        
        if self.race == 'Reptilian':
            self.reptSightRange = 20
            self.reptSightChance = 15
        
        if self.race == 'Demon Spawn':
            class Mutation:
                def __init__(self, name, effect = None):
                    self.name = name
                    self.effect = effect
                
                def mutate(self):
                    print('mutating ' + self.name)
                    del player.Player.possibleMutations[self]
                    player.Player.mutationsGotten.append(self)
            
            extra = Mutation('extra limb', effect = lambda: addSlot(player.Fighter, 'extra limb'))
            self.possibleMutations = {extra: 100}
            self.mutationsGotten = []
            self.mutationLevel = [2]
        
        self.baseSightRadius = SIGHT_RADIUS
        if self.race == 'Felis':
            self.baseSightRadius += 2
        
        self.hasDiscoveredTown = False
        self.money = 0
        self.baseScore = 0
        self.questList = []
        if DEBUG:
            print('Player component initialized')
        
        self.hitThisTurn = False
        
        self.shootFunctions = []

    @property
    def maxWeight(self):
        return round(self.baseMaxWeight + 3 * self.strength, 1)
    
    @property
    def strength(self):
        buffBonus = sum(buff.strength for buff in self.owner.Fighter.buffList)
        return sum(equipment.strengthBonus for equipment in getAllEquipped(self.owner)) + self.baseStrength + buffBonus
    
    @property
    def dexterity(self):
        buffBonus = sum(buff.dexterity for buff in self.owner.Fighter.buffList)
        return sum(equipment.dexterityBonus for equipment in getAllEquipped(self.owner)) + self.baseDexterity + buffBonus
    
    @property
    def vitality(self):
        buffBonus = sum(buff.constitution for buff in self.owner.Fighter.buffList)
        return sum(equipment.vitalityBonus for equipment in getAllEquipped(self.owner)) + self.baseVitality + buffBonus
    
    @property
    def willpower(self):
        buffBonus = sum(buff.willpower for buff in self.owner.Fighter.buffList)
        return sum(equipment.willpowerBonus for equipment in getAllEquipped(self.owner)) + self.baseWillpower + buffBonus
    
    @property
    def stealth(self):
        buffBonus = sum(buff.stealth for buff in self.owner.Fighter.buffList)
        bonus = sum(equipment.stealthBonus for equipment in getAllEquipped(self.owner))
        return self.baseStealth + bonus + buffBonus
    
    @property
    def sightRadius(self):
        return self.baseSightRadius - currentBranch.sightMalus

    def stealthValue(self, monster):
        dex = self.dexterity
        if dex < 0:
            dex = 0
        return round(5*sqrt(dex) * math.log(player.distanceTo(monster) + 1) + self.stealth)
    
    def changeColor(self):
        self.hpRatio = ((self.owner.Fighter.hp / self.owner.Fighter.maxHP) * 100)
        if self.hpRatio == 100:
            self.owner.color = (0, 210, 0)
            self.hpTextColor = colors.darker_green
        elif self.hpRatio < 95 and self.hpRatio >= 75:
            self.owner.color = colors.chartreuse
            self.hpTextColor = colors.darker_chartreuse
        elif self.hpRatio < 75 and self.hpRatio >= 50:
            self.owner.color = colors.yellow
            self.hpTextColor = colors.darker_yellow
        elif self.hpRatio < 50 and self.hpRatio >= 25:
            self.owner.color = colors.orange
            self.hpTextColor = colors.darker_orange
        elif self.hpRatio < 25 and self.hpRatio > 0:
            self.owner.color = colors.red
            self.hpTextColor = colors.darker_red
        elif self.hpRatio == 0:
            self.owner.color = colors.darker_red
            self.hpTextColor = colors.darkest_red
    
    def takeControl(self, target):
        player.Fighter.noVitHP = int(target.Fighter.BASE_MAX_HP)
        player.Fighter.hp = int(target.Fighter.hp) + 5 * self.BASE_VITALITY
        player.Fighter.baseArmor = int(target.Fighter.BASE_ARMOR)
        player.Fighter.noStrengthPower = int(target.Fighter.BASE_POWER)
        player.Fighter.noDexAccuracy = int(target.Fighter.BASE_ACCURACY)
        player.Fighter.noDexEvasion = int(target.Fighter.BASE_EVASION)
        player.Fighter.noWillMP = int(target.Fighter.BASE_MAX_MP)
        player.Fighter.MP = int(target.Fighter.MP)
        player.Fighter.baseCritical = int(target.Fighter.BASE_CRITICAL)
        player.Fighter.baseArmorPenetration = int(target.Fighter.BASE_ARMOR_PENETRATION)
        
        player.x, player.y = int(target.x), int(target.y)
        message('You take control of ' + target.name + '!', colors.han)
        objects.remove(target)
        self.inHost = True
        self.hostDeath = self.HOST_DEATH
    
    def getTrait(self, searchedType = 'all', name = 'Trait'):
        if searchedType == 'skill':
            for trait in self.skills:
                if trait.name == name:
                    return trait
        elif searchedType == 'trait':
            for trait in self.traits:
                if trait.name == name:
                    return trait
        elif searchedType == 'all':
            for trait in self.allTraits:
                if trait.name == name:
                    return trait
        return 'not found'
    
    '''
    def freeAttack(self):
        global FOV_recompute, gameState
        FOV_recompute = True
        quitAtk = False
        while not quitAtk:
            quitAtk = True
            Update()
            userInput = tdl.event.key_wait()
            if tdl.event.isWindowClosed() or (userInput.keychar.upper() == 'ESCAPE' and gameState != 'looking'):
                quitGame("Closed Game")
            if userInput.keychar.upper() in MOVEMENT_KEYS:
                keyX, keyY = MOVEMENT_KEYS[userInput.keychar.upper()]
                for object in objects:
                    if (object.x, object.y) == (player.x + keyX, player.y + keyY) and object.Fighter:
                        moveOrAttack(keyX, keyY)
                        FOV_recompute = True
                        return
            elif userInput.keychar == 'l' and gameState == 'playing':
                gameState = 'looking'
                if DEBUG == True:
                    message('Look mode', colors.purple)
                lookCursor = GameObject(x = player.x, y = player.y, char = 'X', name = 'cursor', color = colors.yellow, Ghost = True, alwaysAlwaysVisible= True, darkColor=colors.darker_yellow)
                objects.append(lookCursor)
                FOV_recompute = True
                quitAtk = False
            elif userInput.keychar.upper() == "W" or userInput.keychar.upper() == 'KP5':                 
                FOV_recompute = True
                return

            elif gameState == 'looking':
                quitAtk = False
                if userInput.keychar.upper() == 'ESCAPE':
                    gameState = 'playing'
                    objects.remove(lookCursor)
                    del lookCursor
                    message('Exited look mode', colors.purple)
                    FOV_recompute = True
                elif userInput.keychar.upper() in MOVEMENT_KEYS:
                    dx, dy = MOVEMENT_KEYS[userInput.keychar.upper()]
                    lookCursor.move(dx, dy)
                    print(lookCursor.x, lookCursor.y, sep=";")
                    FOV_recompute = True
                elif userInput.keychar.upper() == 'ENTER':
                    for object in objects:
                        if object != lookCursor and object.x == lookCursor.x and object.y == lookCursor.y:
                            print('found item under lookCursor')
                            if object.Item:
                                quit = False
                                while not quit:
                                    #root.clear()
                                    object.Item.displayItem(MID_HEIGHT)
                                    lookInput = tdl.event.key_wait()
                                    if lookInput.keychar.upper() == 'ESCAPE':
                                        quit = True
                                    #tdl.flush()
                            if object.Fighter:
                                quit = False
                                while not quit:
                                    #root.clear()
                                    object.Fighter.displayFighter(MID_HEIGHT)
                                    lookInput = tdl.event.key_wait()
                                    if lookInput.keychar.upper() == 'ESCAPE':
                                        quit = True
                                    #tdl.flush()
            else:
                return
    '''

def drawHeaderAndValue(cons, x, y, header, value, headerColor = colors.amber, valueColor = colors.white, underline = True):
    cons.draw_str(x, y, header + ':', headerColor)
    cons.draw_str(x + len(header) + 2, y, value, valueColor)
    if underline:
        for dx in range(len(header) + 1):
            cons.draw_char(x+ dx, y + 1, chr(249), headerColor)

def displayCharacter():
    levelUp_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    
    width = CHARACTER_SCREEN_WIDTH
    height = CHARACTER_SCREEN_HEIGHT
    window = NamedConsole('displayCharacter', width, height)
    window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)
    window.clear()
    page = 1

    while True:
        MAX_PAGE = 3
        for k in range(width):
            window.draw_char(k, 0, chr(196))
        window.draw_char(0, 0, chr(218))
        window.draw_char(k, 0, chr(191))
        kMax = k
        for l in range(height):
            if l > 0:
                window.draw_char(0, l, chr(179))
                window.draw_char(kMax, l, chr(179))
        lMax = l
        for m in range(width):
            window.draw_char(m, lMax, chr(196))
        window.draw_char(0, lMax, chr(192))
        window.draw_char(kMax, lMax, chr(217))
        if page == 1:
            window.draw_str(5, 1, player.Player.race + ' ' + player.Player.classes, fg = colors.amber)
            window.draw_str(width - 1, 1, chr(26), fg = colors.black, bg = colors.amber)
            renderBar(window, 1, 3, BAR_WIDTH, 'EXP', player.Fighter.xp, levelUp_xp, colors.desaturated_cyan, colors.dark_gray)
            #renderBar(window, 1, 5, BAR_WIDTH, 'Hunger', player.Player.hunger, BASE_HUNGER, colors.desaturated_lime, colors.dark_gray)
            
            drawHeaderAndValue(window, 1, 7, 'HP', str(player.Fighter.hp) +'/'+ str(player.Fighter.maxHP), underline = False)
            drawHeaderAndValue(window, 20, 7, 'MP', str(player.Fighter.MP) +'/'+ str(player.Fighter.maxMP), underline = False)
            drawHeaderAndValue(window, 1, 9, 'Armor', str(player.Fighter.armor), underline = False)
            drawHeaderAndValue(window, 13, 9, 'Accuracy', str(player.Fighter.accuracy), underline = False)
            drawHeaderAndValue(window, 30, 9, 'Evasion', str(player.Fighter.evasion), underline = False)
            drawHeaderAndValue(window, 1, 11, 'Strength', str(player.Player.strength + 10), underline = False)
            drawHeaderAndValue(window, 1, 13, 'Dexterity', str(player.Player.dexterity + 10), underline = False)
            drawHeaderAndValue(window, 1, 15, 'Vitality', str(player.Player.vitality + 10), underline = False)
            drawHeaderAndValue(window, 1, 17, 'Willpower', str(player.Player.willpower + 10), underline = False)
            drawHeaderAndValue(window, 1, 19, 'Current load', str(getAllWeights(player)), underline = False)
            drawHeaderAndValue(window, 20, 19, 'Max load', str(player.Player.maxWeight), underline = False)
            '''
            window.draw_str(1, 7, 'HP: ' + str(player.Fighter.hp) + '/' + str(player.Fighter.maxHP))
            window.draw_str(20, 7, 'MP: ' + str(player.Fighter.MP) + '/' + str(player.Fighter.maxMP))
            window.draw_str(1, 9, 'Armor: ' + str(player.Fighter.armor))
            window.draw_str(13, 9, 'Accuracy: ' + str(player.Fighter.accuracy))
            window.draw_str(30, 9, 'Evasion: ' + str(player.Fighter.evasion))
            window.draw_str(1, 11, 'Strength: ' + str(player.Player.strength + 10))
            window.draw_str(1, 13, 'Dexterity: ' + str(player.Player.dexterity + 10))
            window.draw_str(1, 15, 'Vitality: ' + str(player.Player.vitality + 10))
            window.draw_str(1, 17, 'Willpower: ' + str(player.Player.willpower + 10))
            window.draw_str(1, 19, 'Current load: ' + str(getAllWeights(player)))
            window.draw_str(20, 19, 'Max load: ' + str(player.Player.maxWeight))
            '''
        elif page == 2:
            window.draw_str(5, 1, 'Traits:', fg = colors.amber)
            window.draw_str(0, 1, chr(27), fg = colors.black, bg = colors.amber)
            window.draw_str(width - 1, 1, chr(26), fg = colors.black, bg = colors.amber)
            y = 3
            x = 1
            for trait in player.Player.traits:
                if y > height - 2:
                    y = 3
                    x = width // 2
                if trait.selected:
                    window.draw_str(x, y, trait.name)
                    y += 2
        else:
            window.draw_str(5, 1, 'Absorbed Essences:', fg = colors.amber)
            window.draw_str(0, 1, chr(27), fg = colors.black, bg = colors.amber)
            y = 3
            index = 0
            values = list(player.Player.essences.values())
            sins = list(player.Player.essences.keys())
            for sin in sins:
                if values[index] != 0:
                    window.draw_str(1, y, sin + ': ' + str(values[index]))
                    y += 2
                index += 1

        x = MID_WIDTH - int(width/2)
        y = MID_HEIGHT - int(height/2)
        root.blit(window, x, y, width, height, 0, 0)
        tdl.flush()
        
        key = tdl.event.key_wait()
        if tdl.event.isWindowClosed():
            quitGame("Closed game")
        keyChar = key.keychar
        if key.keychar.upper() == 'RIGHT':
            window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)
            window.clear()
            page += 1
        if key.keychar.upper() == 'LEFT':
            window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)
            window.clear()
            page -= 1
        if page < 1:
            page = 1
        if page > MAX_PAGE:
            page = MAX_PAGE

        if keyChar == 'ESCAPE':
            break

class Essence:
    def __init__(self, sin = None, color = None, strength = 'minor', affectedStats = None):
        self.sin = sin
        self.color = color
        self.strength = strength
        self.affectedStats = affectedStats
    
    def absorb(self):
        if self.strength == 'minor':
            bonus = 1
        else:
            bonus = 3
        player.Player.essences[self.sin] += bonus
        message('You absorbed a ' + self.strength + ' essence of ' + self.sin + '!', self.color)
        objects.remove(self.owner)
        if self.affectedStats is not None:
            for stat, boost in self.affectedStats:
                if stat == 'vitality':
                    player.Player.BASE_VITALITY += boost
                    player.Player.baseVitality += boost
                if stat == 'strength':
                    player.Player.baseStrength += boost
                    player.Player.BASE_STRENGTH += boost
                if stat == 'willpower':
                    player.Player.BASE_WILLPOWER += boost
                    player.Player.baseWillpower += boost
                if stat == 'dexterity':
                    player.Player.BASE_DEXTERITY += boost
                    player.Player.baseDexterity += boost
                if stat == 'power':
                    player.Fighter.noStrengthPower += boost
                    player.Fighter.BASE_POWER += boost
                if stat == 'accuracy':
                    player.Fighter.noDexAccuracy += boost
                    player.Fighter.BASE_ACCURACY += boost
                if stat == 'evasion':
                    player.Fighter.noDexEvasion += boost
                    player.Fighter.BASE_EVASION += boost
                if stat == 'armor':
                    player.Fighter.baseArmor += boost
                    player.Fighter.BASE_ARMOR += boost
                if stat == 'HP':
                    player.Fighter.noVitHP += boost
                    player.Fighter.hp += boost
                    player.Fighter.BASE_MAX_HP += boost
                if stat == 'mp':
                    player.Fighter.noWillMP += boost
                    player.Fighter.MP += boost
                    player.Fighter.BASE_MAX_MP += boost
                if stat == 'critical':
                    player.Fighter.baseCritical += boost
                    player.Fighter.BASE_CRITICAL += boost
                if stat == 'slow':
                    if player.Player.speed == 'fast':
                        player.Player.speed = 'average'
                    else:
                        player.Player.speed = 'slow'
                    player.Player.speedChance += boost
                if stat == 'fast':
                    if player.Player.speed == 'slow':
                        player.Player.speed = 'average'
                    else:
                        player.Player.speed = 'slow'
                    player.Player.speedChance += boost

class Item:
    def __init__(self, useFunction = None,  arg1 = None, arg2 = None, arg3 = None, stackable = False, amount = 1, weight = 0, description = 'Placeholder.', pic = 'trollMace.xp', itemtype = None, identified = True, unIDName = 'Unidentified', unIDpName = 'UnidentifiedS', unIDdesc='Unidentified placeholder.', useText = 'Use', unlimitedUses = False):
        self.useFunction = useFunction
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.stackable = stackable
        self.amount = amount
        self.baseWeight = weight
        self.desc = description
        self.pic = pic
        self.type = itemtype
        self.identified = identified
        self.unIDName = unIDName
        self.unIDpName = unIDpName
        self.unIDdesc = unIDdesc
        self.useText = useText
        self.unlimited = unlimitedUses
    
    @property
    def description(self):
        if self.identified:
            return self.desc
        else:
            return self.unIDdesc
    
    @property
    def weight(self):
        weight = self.baseWeight
        if self.owner.Equipment and 'armor' in self.owner.Equipment.type:
            traitAmount = player.Player.getTrait('skill', 'Armor wearing').amount
            weight -= weight*5*traitAmount/100
        return round(weight, 1)
    
    def identify(self):
        global identifiedItems
        self.identified = True
        identifiedItems.append(self.unIDName)
        for object in objects:
            if object.Item:
                if object.Item.unIDName == self.unIDName:
                    object.Item.identified = True
        for object in inventory:
            if object.Item:
                if object.Item.unIDName == self.unIDName:
                    object.Item.identified = True
    
    def pickUp(self, silent = False, inObjects = True):
        if not self.stackable:
            #if len(inventory)>=26:
                #message('Your bag already feels really heavy, you cannot pick up ' + self.owner.name + '.', colors.red)
            #else:
            inventory.append(self.owner)
            if inObjects:
                objects.remove(self.owner)
            if not silent:
                if not self.owner.noPronoun:
                    message('You picked up a ' + self.owner.name + '!', colors.green)
                else:
                    message('You picked up ' + self.owner.name + '!', colors.green)
            equipment = self.owner.Equipment
            if equipment:
                handed = equipment.slot == 'one handed' or equipment.slot == 'two handed'
                if not handed and getEquippedInSlot(equipment.slot) is None:
                    equipment.equip(player.Fighter, silent)
        else:
            itemFound = False
            if inObjects:
                toRemove = []
                for obj in objects:
                    if obj != self.owner and obj.x == self.owner.x and obj.y == self.owner.y and obj.name == self.owner.name:
                        self.amount += obj.Item.amount
                        toRemove.append(obj)
                for obj in toRemove:
                    objects.remove(obj)
            for item in inventory:
                if item.name == self.owner.name:
                    if not silent:
                        if self.amount == 1:
                            if not self.owner.noPronoun:
                                message('You picked up a' + ' ' + self.owner.name + ' !', colors.green)
                            else:
                                message('You picked up ' + self.owner.name + '!', colors.green)
                        elif self.owner.pluralName is None:
                            message('You picked up ' + str(self.amount) + ' ' + self.owner.name + 's !', colors.green)
                        else:
                            message('You picked up ' + str(self.amount) + ' ' + self.owner.pluralName + ' !', colors.green)
                    item.Item.amount += self.amount
                    if inObjects:
                        objects.remove(self.owner)
                    #if DEBUG:
                        #print("Amount of " + self.owner.name + " equals " + str(self.amount))
                    itemFound = True
                    break
            if not itemFound:
                #if len(inventory) >= 26:
                    #message('Your bag already feels really heavy, you cannot pick up ' + str(self.amount) + self.owner.name + 's.', colors.red)
                #else:
                inventory.append(self.owner)
                if inObjects:
                    objects.remove(self.owner)
                if not silent:
                    if self.amount == 1:
                        if not self.owner.noPronoun:
                            message('You picked up a' + ' ' + self.owner.name + ' !', colors.green)
                        else:
                            message('You picked up ' + self.owner.name + '!', colors.green)
                    elif self.owner.pluralName is None:
                        message('You picked up ' + str(self.amount) + ' ' + self.owner.name + 's !', colors.green)
                    else:
                        message('You picked up ' + str(self.amount) + ' ' + self.owner.pluralName + ' !', colors.green)

    def use(self):
        if self.owner.Equipment:
            equipping = self.owner.Equipment.toggleEquip()
            if equipping == 'didnt-take-turn' or equipping == 'cancelled':
                return 'didnt-take-turn'
            elif equipping == 'go back':
                return 'go back'
            else:
                self.identify()
                return 'Equip'
        if self.useFunction is None:
            message('The ' + self.owner.name + ' cannot be used !')
            return 'cancelled'
        else:
            if self.arg1 is None:
                if self.useFunction() != 'cancelled':
                    if not self.unlimited:
                        if not self.stackable or self.amount == 0:
                            inventory.remove(self.owner)
                        else:
                            self.amount -= 1
                            if self.amount < 0:
                                self.amount = 0
                            if self.amount == 0:
                                inventory.remove(self.owner)
                    self.identify()    
                else:
                    return 'cancelled'
            elif self.arg2 is None and self.arg1 is not None:
                if self.useFunction(self.arg1) != 'cancelled':
                    if not self.unlimited:
                        if not self.stackable or self.amount == 0:
                            inventory.remove(self.owner)
                        else:
                            self.amount -= 1
                            if self.amount < 0:
                                self.amount = 0
                            if self.amount == 0:
                                inventory.remove(self.owner)
                    self.identify()
                else:
                    return 'cancelled'
            elif self.arg3 is None and self.arg2 is not None:
                if self.useFunction(self.arg1, self.arg2) != 'cancelled':
                    if not self.unlimited:
                        if not self.stackable or self.amount == 0:
                            inventory.remove(self.owner)
                        else:
                            self.amount -= 1
                            if self.amount < 0:
                                self.amount = 0
                            if self.amount == 0:
                                inventory.remove(self.owner)
                    self.identify()
                else:
                    return 'cancelled'
            elif self.arg3 is not None:
                if self.useFunction(self.arg1, self.arg2, self.arg3) != 'cancelled':
                    if not self.unlimited:
                        if not self.stackable or self.amount == 0:
                            inventory.remove(self.owner)
                        else:
                            self.amount -= 1
                            if self.amount < 0:
                                self.amount = 0
                            if self.amount == 0:
                                inventory.remove(self.owner)
                        self.identify()
                else:
                    return 'cancelled'
                
    def drop(self):
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        if self.stackable:
            try:
                message('You dropped ' + str(self.amount) + ' ' + self.owner.pluralName + '.', colors.yellow)
            except TypeError: #Bug Theo
                message('Amount is None', colors.red)
        else:
            if not self.owner.noPronoun:
                message('You dropped a ' + self.owner.name + '.', colors.yellow)
            else:
                message('You dropped ' + self.owner.name + '.', colors.yellow)
        if self.owner.Equipment:
            self.owner.Equipment.updateState()
            if self.owner.Equipment.isEquipped:
                self.owner.Equipment.unequip()
    
    def fullDescription(self, width):
        equipmentComp = self.owner.Equipment
        fullDesc = []
        equipmentStats = {}
        fullDesc.extend(textwrap.wrap(self.description, width))
        if equipmentComp is not None:
            if equipmentComp.slot is not None:
                fullDesc.append(equipmentComp.slot.capitalize())
            if equipmentComp.type is not None:
                fullDesc.extend(textwrap.wrap(equipmentComp.type.capitalize()))
            if equipmentComp.powerBonus != 0:
                equipmentStats['Power Bonus'] = str(equipmentComp.powerBonus)
            if equipmentComp.armorBonus != 0:
                equipmentStats['Armor Bonus'] = str(equipmentComp.armorBonus)
            if equipmentComp.maxHP_Bonus != 0:
                equipmentStats['HP Bonus'] = str(equipmentComp.maxHP_Bonus)
            if equipmentComp.maxMP_Bonus != 0:
                equipmentStats['MP Bonus'] = str(equipmentComp.maxMP_Bonus)
            if equipmentComp.staminaBonus != 0:
                equipmentStats['Stamina Bonus'] = str(equipmentComp.staminaBonus)
            if equipmentComp.accuracyBonus != 0:
                equipmentStats['Accuracy Bonus'] = str(equipmentComp.accuracyBonus)
            if equipmentComp.evasionBonus != 0:
                equipmentStats['Evasion Bonus'] = str(equipmentComp.evasionBonus)
            if equipmentComp.criticalBonus != 0:
                equipmentStats['Critical Bonus'] = str(equipmentComp.criticalBonus)
            if equipmentComp.stealthBonus != 0:
                equipmentStats['Stealth Bonus'] = str(equipmentComp.stealthBonus)
            if equipmentComp.armorPenetrationBonus != 0:
                equipmentStats['Armor Penetration'] = str(equipmentComp.armorPenetrationBonus)
            if equipmentComp.strengthBonus != 0:
                equipmentStats['Strength Bonus'] = str(equipmentComp.strengthBonus)
            if equipmentComp.dexterityBonus != 0:
                equipmentStats['Dexterity Bonus'] = str(equipmentComp.dexterityBonus)
            if equipmentComp.vitalityBonus != 0:
                equipmentStats['Constitution Bonus'] = str(equipmentComp.vitalityBonus)
            if equipmentComp.willpowerBonus != 0:
                equipmentStats['Willpower Bonus'] = str(equipmentComp.willpowerBonus)
            if equipmentComp.ranged:
                equipmentStats['Ranged Damage'] = str(equipmentComp.rangedPower)
            if equipmentComp.slow:
                fullDesc.append('SLOW')
        equipmentStats['Weight'] = str(self.weight)
        return fullDesc, equipmentStats
    
    def sortFullDesc(self, statList):
        newList = ['Power Bonus', 'Armor Bonus', 'HP Bonus', 'MP Bonus', 'Stamina Bonus', 'Accuracy Bonus', 'Evasion Bonus', 'Critical Bonus', 'Stealth Bonus', 'Armor Penetration', 'Strength Bonus', 'Dexterity Bonus', 'Constitution Bonus', 'Willpower Bonus', 'Ranged Damage', 'Weight']
        toRemove = []
        for stat in newList:
            if not (stat in statList):
                toRemove.append(str(stat))
        for stat in toRemove:
            newList.remove(stat)
        return newList
        
    def displayItem(self, posX = 0, posY = 0, headerFormat = '{}:', capitalizing = True, highlightTitle = False, fromWindow = None):
        global FOV_recompute, menuWindows
        asciiFile = os.path.join(absAsciiPath, self.pic)
        xpRawString = gzip.open(asciiFile, "r").read()
        convertedString = xpRawString
        attributes = xpL.load_xp_string(convertedString)
        picWidth = int(attributes["width"])
        picHeight = int(attributes["height"])
        print("Pic Height = ", picHeight)
        lData = attributes["layer_data"]
        
        altWidth = 0
        if self.owner.Equipment:
            altWidth = len(self.owner.Equipment.type)+3
        width = max(picWidth + 15, altWidth)
        if width < len(self.owner.name) + 3:
            width = len(self.owner.name) + 3
        desc, stats = self.fullDescription(width - 2)
        headers = self.sortFullDesc(list(stats.keys()))
        descriptionHeight = len(desc) + len(headers)
        if desc == '':
            descriptionHeight = 0
        height = descriptionHeight + 6 + int(picHeight) + 1
        
        if menuWindows:
            for mWindow in menuWindows:
                if not mWindow.name == 'inventory' and not mWindow.type == 'menu' and mWindow != fromWindow and mWindow.name != 'displayItemSelected':
                    mWindow.clear()
                    print('CLEARED {} WINDOW OF TYPE {}'.format(mWindow.name, mWindow.type))
                    if mWindow.name == 'displayItemInInventory':
                        ind = menuWindows.index(mWindow)
                        del menuWindows[ind]
                        print('Deleted')
                tdl.flush()
        FOV_recompute = True
        tdl.flush()
        Update()
        window = NamedConsole('displayItemInInventory', width, height)
        print('Created disp window')
        window.clear()
        menuWindows.append(window)

        for k in range(width):
            window.draw_char(k, 0, chr(196))
        window.draw_char(0, 0, chr(218))
        window.draw_char(k, 0, chr(191))
        kMax = k
        for l in range(height):
            if l > 0:
                window.draw_char(0, l, chr(179))
                window.draw_char(kMax, l, chr(179))
        lMax = l
        for m in range(width):
            window.draw_char(m, lMax, chr(196))
        window.draw_char(0, lMax, chr(192))
        window.draw_char(kMax, lMax, chr(217))
        startY = 4
        startX = 3
        layerInd = int(0)
        for layerInd in range(len(lData)):
            xpL.load_layer_to_console(window, lData[layerInd], startY, startX)
        #for line in self.pic:
            #x = 2
            #for char in line:
                #window.draw_char(x, y, char[0], char[1], char[2])
                #x += 1
            #y += 1
        headerColor = colors.amber
        if self.owner.Equipment:
            if 'junk' in self.owner.Equipment.type:
                headerColor = itemGen.junk.color
            elif 'uncommon' in self.owner.Equipment.type:
                headerColor = itemGen.uncommon.color
            elif 'common' in self.owner.Equipment.type:
                headerColor = itemGen.common.color
            elif 'rare' in self.owner.Equipment.type:
                headerColor = itemGen.rare.color
            elif 'epic' in self.owner.Equipment.type:
                headerColor = itemGen.epic.color
            elif 'legendary' in self.owner.Equipment.type:
                headerColor = itemGen.legendary.color
        
        if capitalizing:
            name = self.owner.name.capitalize()
        else:
            name = self.owner.name
        if not highlightTitle:
            window.draw_str(1, 1, headerFormat.format(name), fg = headerColor, bg = None)
        else:
            window.draw_str(1, 1, headerFormat.format(name), fg = colors.black, bg = headerColor)
        for i, line in enumerate(desc):
            window.draw_str(1, int(picHeight) + 5 + i, desc[i], fg = colors.white)
        finalI = i
        for i, header in enumerate(headers):
            drawHeaderAndValue(window, 1, int(picHeight) + 6 + finalI + i, header, stats[header], underline = False)
        if posY == 0:
            posY = MID_HEIGHT - height//2
        root.blit(window, posX, posY, width, height, 0, 0)
        
        menuWindows.append(window)
        FOV_recompute = True
        tdl.flush()
    
    def display(self, options): #after being selected in the menu
        global menuWindows, FOV_recompute
        asciiFile = os.path.join(absAsciiPath, self.pic)
        xpRawString = gzip.open(asciiFile, "r").read()
        convertedString = xpRawString
        attributes = xpL.load_xp_string(convertedString)
        picWidth = int(attributes["width"])
        picHeight = int(attributes["height"])
        print("Pic Height = ", picHeight)
        lData = attributes["layer_data"]
        
        altWidth = 0
        if self.owner.Equipment:
            altWidth = len(self.owner.Equipment.type)+3
        width = max(picWidth + 15, altWidth)
        desc, stats = self.fullDescription(width - 2)
        headers = self.sortFullDesc(list(stats.keys()))
        descriptionHeight = len(desc) + len(headers)
        if desc == '':
            descriptionHeight = 0
        height = descriptionHeight + len(options) + 6 + int(picHeight) + 1
        if menuWindows:
            for mWindow in menuWindows:
                mWindow.clear()
                FOV_recompute = True
                Update()
                tdl.flush()
        window = NamedConsole('displayItemSelected', width, height)
        window.clear()
        menuWindows.append(window)
        
        willReplaceEq = False
        if self.owner.Equipment and not self.owner.Equipment.isEquipped and not 'handed' in self.owner.Equipment.slot:
            needSpecialTorso = self.owner.Equipment.slot == 'torso' and player.Player.getTrait('trait', 'Heavy defense') != 'not found'
            if needSpecialTorso:
                newLight = 'cloth armor' in self.owner.Equipment.type or 'leather armor' in self.owner.Equipment.type
                
                toBeReplacedEq = None
                for obj in equipmentList:
                    if obj.Equipment and obj.Equipment.slot == 'torso' and ('cloth armor' in obj.Equipment.type or 'leather armor' in obj.Equipment.type) == newLight:
                        toBeReplacedEq = obj
                        willReplaceEq = True
            
            else:
                toBeReplacedEq = getEquippedInSlot(self.owner.Equipment.slot)
                if toBeReplacedEq:
                    willReplaceEq = True
                    toBeReplacedEq = toBeReplacedEq.owner
                    
        
        choseOrQuit = False
        index = 0
        while not choseOrQuit:
            choseOrQuit = True
            for k in range(width):
                window.draw_char(k, 0, chr(196))
            window.draw_char(0, 0, chr(218))
            window.draw_char(k, 0, chr(191))
            kMax = k
            for l in range(height):
                if l > 0:
                    window.draw_char(0, l, chr(179))
                    window.draw_char(kMax, l, chr(179))
            lMax = l
            for m in range(width):
                window.draw_char(m, lMax, chr(196))
            window.draw_char(0, lMax, chr(192))
            window.draw_char(kMax, lMax, chr(217))
            startY = 4
            startX = 3
            layerInd = int(0)
            for layerInd in range(len(lData)):
                xpL.load_layer_to_console(window, lData[layerInd], startY, startX)
            #for line in self.pic:
                #x = 2
                #for char in line:
                    #window.draw_char(x, y, char[0], char[1], char[2])
                    #x += 1
                #y += 1
            headerColor = colors.amber
            if self.owner.Equipment:
                if 'junk' in self.owner.Equipment.type:
                    headerColor = itemGen.junk.color
                elif 'uncommon' in self.owner.Equipment.type:
                    headerColor = itemGen.uncommon.color
                elif 'common' in self.owner.Equipment.type:
                    headerColor = itemGen.common.color
                elif 'rare' in self.owner.Equipment.type:
                    headerColor = itemGen.rare.color
                elif 'epic' in self.owner.Equipment.type:
                    headerColor = itemGen.epic.color
                elif 'legendary' in self.owner.Equipment.type:
                    headerColor = itemGen.legendary.color
            
            window.draw_str(1, 1, self.owner.name.capitalize() + ':', fg = headerColor, bg = None)
            for i, line in enumerate(desc):
                window.draw_str(1, int(picHeight) + 5 + i, desc[i], fg = colors.white)
            finalI = i
            for i, header in enumerate(headers):
                drawHeaderAndValue(window, 1, int(picHeight) + 6 + finalI + i, header, stats[header], underline = False)

            y = descriptionHeight + picHeight + 6
            letterIndex = ord('a')
            counter = 0
            for optionText in options:
                text = '(' + chr(letterIndex) + ') ' + optionText
                letterIndex += 1
                if counter == index:
                    window.draw_str(1, y, text, fg = colors.black, bg = colors.white)
                else:
                    window.draw_str(1, y, text, fg = colors.white, bg=colors.black)
                y += 1
                counter += 1
            
            #if not willReplaceEq:
            posX = MID_WIDTH - int(width/2)
            #else:
            #    posX = MID_WIDTH - 2*int(width/3)
            posY = MID_HEIGHT - int(height/2)
            #root.blit(window, posX, posY, width, height, 0, 0)
        
            #tdl.flush()
            
            if willReplaceEq:
                toBeReplacedEq.Item.displayItem(MID_WIDTH + int(width/2) + width%2, posY, headerFormat = 'Replacing {}:', capitalizing = False, fromWindow = window)
            root.blit(window, posX, posY, width, height, 0, 0)
            
            tdl.flush()
            #Update()
            
            key = tdl.event.key_wait()
            keyChar = key.keychar
            if keyChar in 'abcdefghijklmnopqrstuvwsyz':
                ind = ord(keyChar) - ord('a')
                if ind >= 0 and ind < len(options):
                    return ind
            elif keyChar.upper() == "ESCAPE":
                return "cancelled"
            elif keyChar.upper() == 'DOWN':
                choseOrQuit = False
                index += 1
                if index >= len(options):
                    index = 0
            elif keyChar.upper() == 'UP':
                choseOrQuit = False
                index -= 1
                if index < 0:
                    index = len(options) - 1
            elif keyChar.upper() == 'ENTER':
                return index
            else:
                choseOrQuit = False
        return None

class Enchantment:
    def __init__(self, name, functionOnAttack = None, buffOnOwner = [], buffOnTarget = [], damageOnOwner = 0, damageOnTarget = 0, power = 0, acc = 0, evas = 0, arm = 0, hp = 0, mp = 0, crit = 0, ap = 0, stren = 0, dex = 0, vit = 0, will = 0, stamina = 0, stealth = 0):
        self.name = name
        self.functionOnAttack = functionOnAttack
        self.buffOnOwner = buffOnOwner
        self.buffOnTarget = buffOnTarget
        self.damageOnOwner = damageOnOwner
        self.damageOnTarget = damageOnTarget
        self.power = power
        self.acc = acc
        self.evas = evas
        self.arm = arm
        self.hp = hp
        self.mp = mp
        self.crit = crit
        self.ap = ap
        self.stren = stren
        self.dex = dex
        self.vit = vit
        self.will = will
        self.stamina = stamina
        self.stealth = stealth
    
class Equipment:
    def __init__(self, slot, type, powerBonus=0, armorBonus=0, maxHP_Bonus=0, accuracyBonus=0, evasionBonus=0, criticalBonus = 0, maxMP_Bonus = 0, strengthBonus = 0, dexterityBonus = 0, vitalityBonus = 0, willpowerBonus = 0, ranged = False, rangedPower = 0, maxRange = 0, ammo = None, meleeWeapon = False, armorPenetrationBonus = 0, slow = False, enchant = None, staminaBonus = 0, stealthBonus = 0, attackSpeed = 0, damageTypes = {'physical': 100}, resistances = {'physical': 0, 'poison': 0, 'fire': 0, 'cold': 0, 'lightning': 0, 'light': 0, 'dark': 0, 'none': 0}):
        self.baseSlot = slot
        self.type = type
        self.basePowerBonus = powerBonus
        self.baseArmorBonus = armorBonus
        self.baseMaxHP_Bonus = maxHP_Bonus
        self.baseAccuracyBonus = accuracyBonus
        self.baseEvasionBonus = evasionBonus
        self.baseCriticalBonus = criticalBonus
        self.baseMaxMP_Bonus = maxMP_Bonus
        self.isEquipped = False
        self.curSlot = None
        self.baseArmorPenetrationBonus = armorPenetrationBonus
        self.baseStrengthBonus = strengthBonus
        self.baseDexterityBonus = dexterityBonus
        self.baseVitalityBonus = vitalityBonus
        self.baseWillpowerBonus = willpowerBonus
        self.baseStaminaBonus = staminaBonus
        self.baseStealthBonus = stealthBonus
        self.baseAttackSpeed = attackSpeed
        
        self.damageTypes = damageTypes
        self.resistances = resistances
        
        self.ranged = ranged
        self.baseRangedPower = rangedPower
        self.maxRange = maxRange
        self.ammo = ammo
        self.meleeWeapon = meleeWeapon
        self.slow = slow
        self.enchant = enchant
    
    def updateState(self):
        if self.owner in equipmentList:
            print("EQUIPPED")
            self.isEquipped = True
        else:
            print("NOT EQUIPPED")
            self.isEquipped = False
    
    @property
    def slot(self):
        if self.baseSlot == 'two handed' and not 'gloves' in self.type and player.Player.getTrait('trait', 'Firm grip') != 'not found':
            return 'one handed'
        return self.baseSlot
    
    @property
    def powerBonus(self):
        multiplier = 1
        add = 0
        if 'armor' in self.type and self.slot == 'hands':
            eqList = getEquippedInHands()
            i = 0
            while i < len(eqList) and (not eqList[i].Equipment.meleeWeapon or 'gloves' in eqList[i].Equipment.type):
                i += 1
            if i == len(eqList):
                add = self.baseArmorBonus
        if 'gloves' in self.type and player.Player.getTrait('trait', 'Fist fighter') != 'not found':
            multiplier = 2
        if 'light' in self.type and self.owner in equipmentList:
            bonus = (10 * player.Player.getTrait('skill', 'Light weapons').amount) / 100
        elif 'heavy' in self.type and self.owner in equipmentList:
            bonus = (10 * player.Player.getTrait('skill', 'Heavy weapons').amount) / 100
        else:
            bonus = 0
        if self.enchant:
            return round((self.basePowerBonus * bonus + self.basePowerBonus + self.enchant.power)*multiplier + add)
        else:
            return round((self.basePowerBonus * bonus + self.basePowerBonus) * multiplier + add)
    
    @property
    def rangedPower(self):
        if 'light' in self.type and self.owner in equipmentList:
            bonus = (10 * player.Player.getTrait('skill', 'Light ranged weapons').amount) / 100
            if self.enchant:
                return round(self.baseRangedPower * bonus + self.baseRangedPower + player.Player.dexterity + self.enchant.power)
            else:
                return round(self.baseRangedPower * bonus + self.baseRangedPower + player.Player.dexterity)
        elif 'heavy' in self.type and self.owner in equipmentList:
            bonus = (10 * player.Player.getTrait('skill', 'Heavy ranged weapons').amount) / 100
            if self.enchant:
                return round(self.baseRangedPower * bonus + self.baseRangedPower + player.Player.strength + self.enchant.power)
            else:
                return round(self.baseRangedPower * bonus + self.baseRangedPower + player.Player.strength)
        else:
            if self.enchant:
                return self.baseRangedPower + self.enchant.power
            else:
                return self.baseRangedPower
    
    @property
    def accuracyBonus(self):
        if self.enchant:
            return self.baseAccuracyBonus + self.enchant.acc
        else:
            return self.baseAccuracyBonus
    
    @property
    def evasionBonus(self):
        if self.enchant:
            return self.baseEvasionBonus + self.enchant.evas
        else:
            return self.baseEvasionBonus
    
    @property
    def armorBonus(self):
        bonus = 0
        if self.type == 'shield' and self.owner in equipmentList:
            bonus = (10 * player.Player.getTrait('skill', 'Shield mastery').amount) / 100
        elif 'armor' in self.type and self.owner in equipmentList:
            bonus = (5 * player.Player.getTrait('skill', 'Armor efficiency').amount) / 100
        if self.enchant:
            return round(self.baseArmorBonus * bonus + self.baseArmorBonus + self.enchant.arm)
        else:
            return round(self.baseArmorBonus * bonus + self.baseArmorBonus)
    
    @property
    def maxHP_Bonus(self):
        if self.enchant:
            return self.baseMaxHP_Bonus + self.enchant.hp
        else:
            return self.baseMaxHP_Bonus
    
    @property
    def maxMP_Bonus(self):
        if self.enchant:
            return self.baseMaxMP_Bonus + self.enchant.mp
        else:
            return self.baseMaxMP_Bonus
    
    @property
    def criticalBonus(self):
        if self.enchant:
            return self.baseCriticalBonus + self.enchant.crit
        else:
            return self.baseCriticalBonus
    
    @property
    def armorPenetrationBonus(self):
        if self.enchant:
            return self.baseArmorPenetrationBonus + self.enchant.ap
        else:
            return self.baseArmorPenetrationBonus
    
    @property
    def strengthBonus(self):
        if self.enchant:
            return self.baseStrengthBonus + self.enchant.stren
        else:
            return self.baseStrengthBonus
    
    @property
    def dexterityBonus(self):
        if self.enchant:
            return self.baseDexterityBonus + self.enchant.dex
        else:
            return self.baseDexterityBonus
    
    @property
    def vitalityBonus(self):
        if self.enchant:
            return self.baseVitalityBonus + self.enchant.vit
        else:
            return self.baseVitalityBonus
    
    @property
    def willpowerBonus(self):
        if self.enchant:
            return self.baseWillpowerBonus + self.enchant.will
        else:
            return self.baseWillpowerBonus
    
    @property
    def staminaBonus(self):
        if self.enchant:
            return self.baseStaminaBonus + self.enchant.stamina
        else:
            return self.baseStaminaBonus
    
    @property
    def stealthBonus(self):
        if self.enchant:
            return self.baseStealthBonus + self.enchant.stealth
        else:
            return self.baseStealthBonus
    
    @property
    def attackSpeed(self):
        return self.baseAttackSpeed

    def toggleEquip(self):
        self.updateState()
        if self.isEquipped:
            self.unequip()
        else:
            equipping = self.equip()
            if equipping == 'didnt-take-turn':
                return 'didnt-take-turn'
            elif equipping == 'go back':
                return 'go back'
        return

    def equip(self, fighter = None, silent = False):
        playerEquipping = False
        if fighter is None or fighter == player.Fighter:
            playerEquipping = True
            fighter = player.Fighter
        handSlot = None
        oldEquipment = None
        global FOV_recompute
        
        if menuWindows:
            for mWindow in menuWindows:
                if not mWindow.name == 'inventory' and not mWindow.type == 'menu':
                    mWindow.clear()
                    print('CLEARED {} WINDOW OF TYPE {}'.format(mWindow.name, mWindow.type))
                    if mWindow.name == 'displayItemInInventory':
                        ind = menuWindows.index(mWindow)
                        del menuWindows[ind]
                        print('Deleted')
                tdl.flush()
        
        handed = self.slot == 'one handed' or self.slot == 'two handed'
        extra = 'extra limb' in fighter.slots
        backShield = 'shield' in self.type and player.Player.getTrait('trait', 'Back shield') != 'not found'
        
        if playerEquipping:
            print('player is equipping')
            if self.slot == 'one handed':
                inHands = [None, None, None, None]
                rightText = "right hand"
                leftText = "left hand"
                extraText = 'extra limb'
                backText = 'on your back'
                for object in equipmentList:
                    if object.Equipment.curSlot == "right hand":
                        rightText = rightText + " (" + object.name + ")"
                        inHands[0] = object
                    if object.Equipment.curSlot == "left hand":
                        leftText = leftText + " (" + object.name + ")"
                        inHands[1] = object
                    if object.Equipment.curSlot == 'both hands':
                        rightText = rightText + " (" + object.name + ")"
                        leftText = leftText + " (" + object.name + ")"
                        inHands[0] = object
                        inHands[1] = object
                    if extra and object.Equipment.curSlot == 'extra limb':
                        extraText = extraText + ' (' + object.name + ')'
                        inHands[2] = object
                    if backShield and (object.Equipment.slot == 'back' or object.Equipment.curSlot == 'back'):
                        backText = backText + ' (' + object.name + ')'
                        inHands[3] = object
                if extra and not backShield:
                    handList = [rightText, leftText, extraText, 'go back']
                    del inHands[3]
                elif backShield:
                    handList = [rightText, leftText, backText, 'go back']
                    del inHands[2]
                elif extra:
                    handList = [rightText, leftText, extraText, backText, 'go back']
                else:
                    handList = [rightText, leftText, 'go back']
                    del inHands[2]
                    del inHands[2] #because the list has changed
                handIndex = menu('What slot do you want to equip this ' + self.owner.name + ' in?', handList, 40, usedList = inHands, displayItem = True, itemDisplayed = 'weapon')
                try:
                    chosen = handList[handIndex]
                except:
                    return 'didnt-take-turn'
                if chosen == 'go back':
                    print('back from equipping prompt')
                    return 'go back'
                elif 'back' in chosen:
                    handSlot = 'back'
                    handed = False
                elif 'right' in chosen:
                    handSlot = 'right hand'
                elif 'left' in chosen:
                    handSlot = 'left hand'
                elif 'extra' in chosen:
                    handSlot = 'extra limb'
            elif self.slot == 'two handed':
                inHands = [None, None]
                rightText = "right hand"
                leftText = "left hand"
                for object in equipmentList:
                    if object.Equipment.curSlot == "right hand":
                        rightText = rightText + " (" + object.name + ")"
                        inHands[0] = object
                    if object.Equipment.curSlot == "left hand":
                        leftText = leftText + " (" + object.name + ")"
                        inHands[1] = object
                    if object.Equipment.curSlot == 'both hands':
                        rightText = rightText + " (" + object.name + ")"
                        leftText = leftText + " (" + object.name + ")"
                        inHands[0] = object
                        inHands[1] = object
                handList = [rightText, leftText, 'go back']
                handIndex = menu('Equipping this ' + self.owner.name + ' will unequip these items.', handList, 40, usedList = inHands, displayItem = True, itemDisplayed = 'weapon')
                if handIndex == 2:
                    return 'go back'
                elif handIndex != 0 and handIndex != 1:
                    return 'didnt-take-turn'
                handSlot = 'both hands'
    
            rightEquipment = None
            leftEquipment = None
            extraEquipment = None
            if handed:
                weapon = self.meleeWeapon or self.ranged
                if weapon and handSlot == 'right hand':
                    leftEquipment = getEquippedInSlot('left hand', hand = True)
                    extraEquipment = getEquippedInSlot('extra limb', hand = True)
                elif weapon and handSlot == 'left hand':
                    rightEquipment = getEquippedInSlot('right hand', hand = True)
                    extraEquipment = getEquippedInSlot('extra limb', hand = True)
                elif extra and weapon and handSlot == 'extra limb':
                    leftEquipment = getEquippedInSlot('left hand', hand = True)
                    rightEquipment = getEquippedInSlot('right hand', hand = True)
                
            rightIsWeapon = False
            leftIsWeapon = False
            extraIsWeapon = False
            if self.meleeWeapon:
                rightIsWeapon = rightEquipment and rightEquipment.meleeWeapon
                leftIsWeapon = leftEquipment and leftEquipment.meleeWeapon
                extraIsWeapon = extraEquipment and extraEquipment.meleeWeapon
            elif self.ranged:
                rightIsWeapon = rightEquipment and rightEquipment.ranged
                leftIsWeapon = leftEquipment and leftEquipment.ranged
                extraIsWeapon = extraEquipment and extraEquipment.ranged
    
            possible = True
            if rightIsWeapon or leftIsWeapon or extraIsWeapon:
                if self.meleeWeapon:
                    if player.Player.getTrait('trait', 'Dual wield') == 'not found':
                        message('You cannot wield two melee weapons at the same time!', colors.yellow)
                        possible = False
                    elif (rightIsWeapon and not 'light' in rightEquipment.type) or (leftIsWeapon and not 'light' in leftEquipment.type) or (extraIsWeapon and not 'light' in extraEquipment.type) or not 'light' in self.type:
                        message('You can only wield several light weapons.', colors.yellow)
                        possible = False
                elif self.ranged:
                    if player.Player.getTrait('trait', 'Pistolero') == 'not found':
                        message('You cannot wield two ranged weapons at the same time.', colors.yellow)
                        possible = False
                    elif (rightIsWeapon and not 'light' in rightEquipment.type) or (leftIsWeapon and not 'light' in leftEquipment.type) or (extraIsWeapon and not 'light' in extraEquipment.type) or not 'light' in self.type:
                        message('You can only wield several light ranged weapons.', colors.yellow)
                        possible = False
            if possible:
                needSpecialTorso = self.slot == 'torso' and player.Player.getTrait('trait', 'Heavy defense') != 'not found'
                if not handed and backShield:
                    oldEquipment = getEquippedInSlot('back')
                    if oldEquipment is not None:
                        oldEquipment.unequip()
                    self.curSlot = 'back'
                    message('Equipped ' + self.owner.name + ' on back.', colors.light_green)
                    silent = True
                elif not handed and not needSpecialTorso:
                    oldEquipment = getEquippedInSlot(self.slot)
                    if oldEquipment is not None:
                        oldEquipment.unequip()
                elif not handed and needSpecialTorso:
                    newLight = 'cloth armor' in self.type or 'leather armor' in self.type
                    
                    oldEquipment = None
                    for obj in equipmentList:
                        if obj.Equipment and obj.Equipment.slot == 'torso' and ('cloth armor' in obj.Equipment.type or 'leather armor' in obj.Equipment.type) == newLight:
                            oldEquipment = obj.Equipment
                    
                    if oldEquipment is not None:
                        oldEquipment.unequip()
                    otherPiece = getEquippedInSlot('torso')
                    if otherPiece and newLight and not silent:
                        message('Equipped {} on torso, under {}.'.format(self.owner.name, otherPiece.owner.name), colors.light_green)
                        silent = True
                    elif otherPiece and not silent:
                        message('Equipped {} on torso, above {}.'.format(self.owner.name, otherPiece.owner.name), colors.light_green)
                        silent = True
                else:
                    rightEquipment = None
                    leftEquipment = None 
                    bothEquipment = None
                    oldEquipment = None
            
                    if self.slot == 'one handed':
                        bothEquipment = getEquippedInSlot('both hands', hand = True)
                        oldEquipment = getEquippedInSlot(handSlot, hand = True)
                    if self.slot == 'two handed':
                        rightEquipment = getEquippedInSlot('right hand', hand = True)
                        leftEquipment = getEquippedInSlot('left hand', hand = True)
                        bothEquipment = getEquippedInSlot('both hands', hand = True)
        
                    if bothEquipment is not None:
                        bothEquipment.unequip()
                    if rightEquipment is not None:
                        rightEquipment.unequip()
                    if leftEquipment is not None:
                        leftEquipment.unequip()
                    if oldEquipment is not None:
                        oldEquipment.unequip()
                
                if self.owner in inventory:
                    inventory.remove(self.owner)
                equipmentList.append(self.owner)
                self.isEquipped = True
                if self.maxHP_Bonus != 0:
                    player.Fighter.hp += self.maxHP_Bonus
                if self.maxMP_Bonus != 0:
                    player.Fighter.MP += self.maxMP_Bonus
                
                if not silent:
                    if handed:
                        self.curSlot = handSlot
                        message('Equipped ' + self.owner.name + ' on ' + self.curSlot + '.', colors.light_green)
                    else:
                        message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', colors.light_green)
        else:
            print('monster is equipping')
            fighter.equipmentList.append(self.owner)
            self.isEquipped = True
            if self.maxHP_Bonus != 0:
                fighter.hp += self.maxHP_Bonus
            if self.maxMP_Bonus != 0:
                fighter.MP += self.maxMP_Bonus
        
        return

    def unequip(self):
        handed = self.slot == 'one handed' or self.slot == 'two handed'

        if not self.isEquipped: return
        self.isEquipped = False
        equipmentList.remove(self.owner)
        inventory.append(self.owner)
        if handed:
            message('Unequipped ' + self.owner.name + ' from ' + self.curSlot + '.', colors.light_yellow)
            self.curSlot = None
        else:
            message('Unequipped ' + self.owner.name + ' from ' + self.slot + '.', colors.light_yellow)
        if self.maxHP_Bonus != 0:
            player.Fighter.hp -= self.maxHP_Bonus
        if self.maxMP_Bonus != 0:
            player.Fighter.MP -= self.maxMP_Bonus
    
    def shoot(self, line = None, spendAtkPoints = True, shootOthers = True):
        '''
        @param: if precised, line must contain player's coords
        '''
        global FOV_recompute, explodingTiles
        
        didntTakeTurn = 'didnt-take-turn'
        if shootOthers: #only the first weapon shot will execute this part
            shot = False
            for obj in getEquippedInHands():
                if obj.Equipment != self:
                    state, line = obj.Equipment.shoot(line, spendAtkPoints, False)
                    if line == 'cancelled':
                        return 'didnt-take-turn', None
                    shot = state != 'didnt-take-turn' or shot
            if shot:
                spendAtkPoints = False
                didntTakeTurn = 'took-turn'
        
        if not self.ranged:
            return didntTakeTurn, line
        ammo = self.ammo
        weapon = self.owner
        hit = False
        if ammo != 'none':
            foundAmmo = False
            for object in inventory:
                print(object.name)
                if object.name == ammo:
                    foundAmmo = True
                    ammoObj = object
                    break
        else:
            foundAmmo = True
            ammoObj = self.owner
        
        if foundAmmo:
            itemComponent = Item(stackable = True, amount = 1)
            newAmmo = GameObject(0, 0, ammoObj.char, ammoObj.name, ammoObj.color, Item = itemComponent)
            
            if not line:
                message('Choose a target for your ' + weapon.name + '.', colors.cyan)
                line = targetTile(self.maxRange, showBresenham=True, returnBresenham = True)
            if line == "cancelled":
                FOV_recompute = True
                message('Invalid target.')
                return 'didnt-take-turn', 'cancelled'
            else:
                try:
                    line.remove((player.x, player.y))
                except:
                    print('player coords not in shooting line')
                if spendAtkPoints:
                    player.Fighter.actionPoints -= player.Fighter.rangedSpeed
                #(targetX, targetY) = projectile(player.x, player.y, aimX, aimY, '/', colors.light_orange, continues=True)
                monsterTarget = None
                for object in objects:
                    if object.Fighter and (object.x, object.y) in line:
                        monsterTarget = object
                        break
                
                newLine = copy(line)
                if monsterTarget:
                    [hit, criticalHit] = player.Fighter.toHit(monsterTarget, ranged = True)
                    dmgTxtFunc = lambda damageTaken: player.Fighter.formatAttackText(monsterTarget, hit, criticalHit, damageTaken, baseText = '{} {}shoot{} {} for {}!', baseNoDmgText = '{} shoot{} {} but it has no effect.')
                    if hit:
                        if player.Player.getTrait('trait', 'Aggressive').selected:
                            damage = randint(self.rangedPower - 2, self.rangedPower + 2) + 4
                        else:
                            damage = randint(self.rangedPower - 2, self.rangedPower + 2)

                        if criticalHit:
                            damage = damage * player.Fighter.critMultiplier
                        
                        monsterTarget.Fighter.lootFunction.append(newAmmo)
                        monsterTarget.Fighter.lootRate.append(100)
                        for func in player.Player.shootFunctions:
                            func(player, monsterTarget)
                        
                        damageDict = player.Fighter.computeDamageDict(damage)
                        try:
                            monsterTarget.Fighter.takeDamage(damageDict, player.name, armored = True, damageTextFunction = dmgTxtFunc)
                        except:
                            print('Fighter is NoneType! probably dead')
                    else:
                        possibleDeviations = [(1, 0), (1, 1), (1, -1),
                                              (-1, 0), (-1, 1), (-1, -1),
                                              (0, 1), (0, -1),]
                        deviationCoords = (monsterTarget.x, monsterTarget.y)
                        while deviationCoords in line and len(possibleDeviations) > 0:
                            deviationInd = randint(0, len(possibleDeviations)-1)
                            devX, devY = possibleDeviations[deviationInd]
                            deviationCoords = (monsterTarget.x + devX, monsterTarget.y + devY)
                            possibleDeviations.remove((devX, devY))
                        x, y = deviationCoords
                        newLine = tdl.map.bresenham(player.x, player.y, x, y)
                        newLine.remove((player.x, player.y))
                        message("Your shot didn't hit anything", colors.grey)
                else:
                    message("Your shot didn't hit anything", colors.grey)
                ammoObj.Item.amount -= 1
                foundAmmo = True
                if ammoObj.Item.amount <= 0:
                    if ammoObj.Equipment:
                        equipmentList.remove(ammoObj)
                    message('You have no more {}!'.format(ammoObj.name))
                    try:
                        inventory.remove(ammoObj)
                    except:
                        pass

            lastX, lastY = newLine[len(newLine)-1]
            dropX, dropY = projectile(player.x, player.y, lastX, lastY, '/', colors.light_orange, line = newLine)
            '''
            shot = False
            i = 0
            while not shot and i < len(objects):
                obj = objects[i]
                if obj.Fighter and obj.x == dropX and obj.y == dropY:
                    shot = True
                    monsterTarget = obj
                i+=1
            if shot:
                [hit, criticalHit] = player.Fighter.toHit(monsterTarget, ranged = True)
                dmgTxtFunc = lambda damageTaken: player.Fighter.formatAttackText(monsterTarget, True, criticalHit, damageTaken, baseText = '{} {}shoot{} {} for {}!', baseNoDmgText = '{} shoot{} {} but it has no effect.')
                if player.Player.getTrait('trait', 'Aggressive').selected: #the deviation shot automatically hits
                    damage = randint(self.rangedPower - 2, self.rangedPower + 2) + 4
                else:
                    damage = randint(self.rangedPower - 2, self.rangedPower + 2)

                if criticalHit:
                    damage = damage * player.Fighter.critMultiplier
                damageDict = player.Fighter.computeDamageDict(damage)
                monsterTarget.Fighter.takeDamage(damageDict, player.name, armored = True, damageTextFunction = dmgTxtFunc)
            '''
            if not hit:
                newAmmo.x, newAmmo.y = dropX, dropY
                objects.append(newAmmo)
                newAmmo.sendToBack()
            return None, line
        else:
            message('You have no ammunition for your ' + weapon.name + '!', colors.red)
            return didntTakeTurn, None

class Money(Item):
    def __init__(self, moneyAmount):
        self.amount = moneyAmount
        self.stackable = True
        Item.__init__(self, amount = self.amount, stackable = self.stackable)
        
    def pickUp(self):
        player.Player.money += self.amount
        objects.remove(self.owner)
        message('You pick up ' + str(self.amount) + ' gold coins !')
    
    def use(self):
        raise UnusableMethodException("Cannot 'use' a money item.")
    
    def drop(self):
        raise UnusableMethodException("Cannot 'drop' a money item.")
    
    def fullDescription(self):
        raise UnusableMethodException("Cannot 'fullDescript' a money item.")
    
    def display(self):
        raise UnusableMethodException("Cannot 'display' a money item.")

class ShopChoice:
    def __init__(self, gObject, itemComp = None, price = 0, stock = 0):
        self.object = gObject
        #assert isinstance(self.object, GameObject)
        if not self.object.Item:
            if itemComp:
                self.itemComp = itemComp
                print('Found itemComp without issues')
            else:
                print('========================================')
                print('===============WARNING !================')
                print('Assigning None itemComponent to ' + self.object.name)
                print('This is likely to cause issues !')
                print('========================================')
                print('========================================')
            self.object.Item = self.itemComp
        else:
            self.itemComp = self.object.Item
            print('Found already existing item component')
        self.price = price
        self.stock = stock
    
    def buy(self):
        if player.Player.money >= self.price:
            if self.stock > 0:
                player.Player.money -= self.price
                self.stock -= 1
                newObject = self.object.duplicate()
                newObject.Item.pickUp(silent = True, inObjects = False)
                return 'OK'
            else:
                return 'OOS' # Out of stock
        else:
            return 'NEM' #Not enough money
    
    def formatName(self):
        o = self.object
        i = o.Item
        '''
        if i != self.itemComp:
            raise NotEqualToExpectedValueException('ItemComp is different from the Item component of the actual object')
        '''
        if self.stock > 1:
            if o.pluralName:
                name = str(self.stock) + ' ' + o.pluralName
            else:
                name = str(self.stock) + ' ' + o.name + 's'
        else:
            name = 'A ' + str(o.name) #TO-DO : Insert here check for other pronouns ('an', 'the', None, etc)
        
        name = getRightFilled(name)
        priceText = str(self.price) + 'g'
        priceLength = len(priceText)
        lastNameCharacter = len(name) - 1
        startPrice = lastNameCharacter - priceLength
        name = name[:startPrice] + priceText
        return name

class Shop:
    def __init__(self, choicesList, welcomeText = 'Welcome to my shop ! What can I do for you ?'):
        self.choicesList = choicesList
        self.welcomeText = welcomeText
        
    def browse(self):
        root.clear()
        state = 'starting'
        selectedIndex = 0
        while state != 'END':
            con.clear()
            con.draw_str(0, 1, 'ITEM')
            con.draw_str(WIDTH - len('PRICE') - 1, 1, 'PRICE')
            y = 2
            for choice in self.choicesList:
                ind = self.choicesList.index(choice)
                if choice.stock > 0:
                    toDraw = choice.formatName()
                    foreground = colors.white
                else:
                    toDraw = getCenterFilled('OUT OF STOCK')
                    foreground = colors.light_gray
                if ind == selectedIndex:
                    background = colors.dark_azure
                else:
                    background = Ellipsis
                con.draw_str(0, y, toDraw, fg = foreground, bg = background)
                y += 1
            panel.clear()
            for x in range(WIDTH):
                panel.draw_char(x, 0, chr(196))
            moneyText = 'Money : ' + str(player.Player.money)
            startMoneyX = WIDTH - len(moneyText)
            panel.draw_str(startMoneyX, 1, moneyText)
            centerY = PANEL_HEIGHT // 2
            if state == 'OK':
                pMessage = 'Thanks for your purchase ! What else can I do for you ?'
            elif state == 'OOS':
                pMessage = "I'm sorry but this item is out of stock."
            elif state == 'NEM':
                pMessage = "Sorry but you can't afford this"
            elif state == 'END':
                pMessage = "Farewell. (you shouldn't see this message)"
            else:
                pMessage = self.welcomeText
            drawCentered(panel, y = centerY, text = pMessage, fg = Ellipsis, bg = Ellipsis)
            root.blit(con, 0, 0, WIDTH, HEIGHT, 0, 0)
            root.blit(panel, 0, PANEL_Y, WIDTH, PANEL_HEIGHT, 0, 0)
            tdl.flush()
            key = tdl.event.key_wait()
            actualKey = key.keychar.upper()
            if actualKey == 'ESCAPE':
                state = 'END'
            elif actualKey in ('UP', 'KP8'):
                selectedIndex -= 1
                if selectedIndex < 0:
                    selectedIndex = len(self.choicesList) - 1
                playWavSound('selectClic.wav')
            elif actualKey in ('DOWN', 'KP2'):
                selectedIndex += 1
                if selectedIndex > len(self.choicesList) - 1 :
                    selectedIndex = 0
                playWavSound('selectClic.wav')
            elif actualKey == 'ENTER':
                state = self.choicesList[selectedIndex].buy()

def vomit(amount = 30):
    ### HUNGER REMOVED ###
    message('You throw up !', colors.darker_lime)
    pass

#ISN project
def badPieEffect(): #Presentation de l'initialisation d'un buff (poison)
    message('This tasted awful !', colors.red)
    dice = randint(1, 100)
    if dice > 40:
        vomit()
    else:
        satiateHunger(randint(50, 200))
    if dice > 70:
        message("This had a very strange aftertaste...", colors.red)
        poisoned = Buff('poisoned', colors.purple, cooldown=randint(5, 10), continuousFunction=lambda fighter: randomDamage('poison', fighter, chance = 100, minDamage=1, maxDamage=10, dmgType={'poison': 100}))
        poisoned.applyBuff(player)

badPie = GameObject(None, None, ',', "awful pie", colors.dark_fuchsia, Item = Item(useFunction = lambda : badPieEffect(), weight = 0.4, stackable=True, amount = 1, description = "This pie looks barely edible. Whoever baked it deserves the title of the worst baker of all Ashotara.", itemtype = 'food', pic = 'pie.xp'), blocks = False, pName = "awful pies")
badPieChoice = ShopChoice(gObject = badPie, price = 100, stock = 20)

salad = GameObject(None, None, ',', "'herb salad", colors.green, Item = Item(useFunction = lambda : satiateHunger(100, 'the herb salad'), weight = 0.05, stackable=True, amount = 1, description = "A salad made out of the herbs that grow all arount this place. Oddly enough, this looks like it won't make you die of poisoning as soon as you eat it.", itemtype = 'food'), blocks = False, pName = "herb salads")
saladChoice = ShopChoice(gObject = salad, price = 120, stock = 10)

bread = GameObject(None, None, ',', "slice of bread", colors.yellow, Item = Item(useFunction= lambda : satiateHunger(50, 'the slice of bread'), weight = 0.2, stackable=True, amount = 1, description = "This has probably been lying on the ground for ages, but you'll have to deal with it if you don't want to starve.", itemtype = 'food'), blocks = False, pName = "slices of bread")
breadChoice = ShopChoice(gObject = bread, price = 40, stock = 5) #The amount of stock will make sense once we have a restock system implemented (you have to bake more bread to get more, and since the NPC cannot leave the town because monsters there are limited ressources, so you can't bake a lot of it in one go)

cSwordEquip = Equipment(slot = 'one handed', type = 'light weapon', powerBonus = 2, criticalBonus = 1, meleeWeapon = True)
cSwordItem = Item(weight= 0.6, description= "A sword made out of candy. Barely qualifies as a weapon.")
cSword = GameObject(None, None, char = '/', name = 'candy sword', color = colors.pink, Item = cSwordItem, Equipment = cSwordEquip, blocks = False)
cSwordChoice = ShopChoice(gObject = cSword, price = 400, stock = 1)

ayethShopChoices = [badPieChoice, saladChoice, breadChoice, cSwordChoice]
ayethShop = Shop(choicesList=ayethShopChoices)


class Quest:
    def __init__(self, name, rewardList, rewardXP):
        self.name = name
        self.description = 'Placeholder'
        self.rewardList = rewardList
        self.rewardXP = rewardXP
        self.state = 'inactive'
        self.onValid = doNothing
    
    def valid(self):
        self.onValid()
        for item in self.rewardList:
            item.pickUp()
        
        player.Fighter.xp += self.rewardXP
        message('You completed {} !'.format(self.name))
        self.state = 'completed'
        

    
    def take(self):
        message('You started a new quest ! {} added to quest log.')
        player.Player.questList.append(self)
        self.state = 'active'

def removeItem(nameToFind, amount):
    foundItem = None
    for item in inventory:
        if item.name == nameToFind:
            foundItem = item
            break
        if foundItem is None:
            for item in inventory:
                print(item.name)
            raise ValueError('No item found')
        else:
            foundItem.Item.amount -= amount
            if foundItem.Item.amount < 0:
                raise ValueError('Item in too low quantity')
            elif foundItem.Item.amount == 0:
                inventory.remove(foundItem)

def validBaking():
    removeItem('crawling horror heart', 1)
    removeItem('snake tooth', 2)

testQuestReward = [GameObject(x = None, y = None, char = '$', name = 'gold coin', color = colors.gold, Item= Money(10), blocks = False, pName = 'gold coins'), badPie]
testQuest = Quest('Baking 101', rewardList=testQuestReward, rewardXP = 200)
testQuest.description = "Ayeth asked you to find some ingredients for her 'new recipe'. You can't help but feel sorry for anyone who is gonna have to eat the final product. \n You'll need to find : \n \n    - 1 crawling horror heart \n    - 2 snake teeth "
testQuest.onValid = validBaking

def quitGame(message, backToMainMenu = False, noSave = False):
    global objects
    global inventory
    if gameState != "dead" and not noSave: #and not tutorial:
        saveGame()
    if backToMainMenu:
        for obj in objects:
            del obj
        inventory = []
        mainMenu()
    else:
        stopProcess()
        raise SystemExit(str(message))
        os._exit(-1) #In case raise SystemExit() doesn't work properly
    
def stopProcess():
    for process in activeProcess:
        process.terminate()

def getInput():
    global FOV_recompute, gameState, lookCursor, REVEL, DEBUG, currentSidepanelMode
    userInput = tdl.event.key_wait()
    if tdl.event.isWindowClosed():
        quitGame("Closed Game")
    if userInput.keychar.upper() ==  'ESCAPE' and gameState != 'looking':
        return 'exit'
    #elif userInput.keychar.upper() == 'ALT' and userInput.alt:
        #isFullscreen = tdl.getFullscreen()
        #print("Fullscreen is borked at the moment")
        #if isFullscreen :
            #set_fullscreen(False)
        #else:
            #set_fullscreen(True)
    elif userInput.keychar.upper() == 'F3' and DEBUG:
        #castFreeze(player, player)
        learnSpell(convertRandTemplateToSpell())
        '''
        global GRAPHICS
        if GRAPHICS == 'modern':
            print('Graphics mode set to classic')
            GRAPHICS = 'classic'
            FOV_recompute = True
            return 'didnt-take-turn'
        elif GRAPHICS == 'classic':
            print('Graphics mode set to modern')
            GRAPHICS = 'modern'
            FOV_recompute = True
            return 'didnt-take-turn'
        '''
    elif userInput.keychar.upper() == 'F2' and gameState != 'looking':
        #player.Fighter.takeDamage(1, 'debug damage')
        nextLevel()
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == 'F1':
        if not DEBUG:
            print('Monster turn debug is now on')
            message("This is a very long message just to test Python 3 built-in textwrap function, which allows us to do great things such as splitting very long texts into multiple lines, so as it don't overflow outside of the console. Oh and, debug mode has been activated", colors.purple)
            fancyMessage(['That', ' is', ' the', ' fabulous', ' test', ' message.'], [colors.red, colors.orange, colors.yellow, colors.green, colors.blue, colors.violet])
            DEBUG = True
            FOV_recompute = True
            return 'didnt-take-turn'
        elif DEBUG:
            print('Monster turn debug is now off')
            message('Debug mode is now off', colors.purple)
            DEBUG = False
            FOV_recompute = True
            return 'didnt-take-turn' 
        else:
            quitGame('Whatever you did, it went horribly wrong (DEBUG took an unexpected value)')    
        FOV_recompute= True
    elif userInput.keychar.upper() == 'F4' and DEBUG and not tdl.event.isWindowClosed(): #For some reason, Bad Things (tm) happen if you don't perform a tdl.event.isWindowClosed() check here. Yeah, don't ask why.
        #global dispClearance
        #dispClearance = not dispClearance
        castCreateArmor()
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == 'F5' and DEBUG and not tdl.event.isWindowClosed(): #Don't know if tdl.event.isWindowClosed() is necessary here but added it just to be sure
        player.Player.baseVitality += 1000
        player.Player.BASE_VITALITY += 1000
        player.Player.baseWillpower += 1000
        player.Player.BASE_WILLPOWER += 1000
        player.Fighter.hp = player.Fighter.maxHP
        player.Fighter.MP = player.Fighter.maxMP
        player.Fighter.stamina = player.Fighter.maxStamina
        message('Healed player and increased their maximum HP and MP value by 1000', colors.purple)
        FOV_recompute = True
    elif userInput.keychar.upper() == "F6" and DEBUG and not tdl.event.isWindowClosed():
        player.Fighter.xp += 1000
        for spell in spells:
            learnSpell(spell)
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == 'F7' and DEBUG and not tdl.event.isWindowClosed():
        expr = input()
        exec(expr, globals(), locals()) #Aka most powerful debug / cheat tool
        print(expr)
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == 'F8' and DEBUG and not tdl.event.isWindowClosed():
        castCreateWeapon()
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == 'F9' and DEBUG and not tdl.event.isWindowClosed():
        castCreateWall()
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == 'F10' and DEBUG and not tdl.event.isWindowClosed(): #For some reason, Bad Things (tm) happen if you don't perform a tdl.event.isWindowClosed() check here. Yeah, don't ask why.
        castCreateDarksoul(friendly = False)
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == 'F11' and DEBUG and not tdl.event.isWindowClosed(): #For some reason, Bad Things (tm) happen if you don't perform a tdl.event.isWindowClosed() check here. Yeah, don't ask why.
        player.Player.money += 100
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == 'F12' and DEBUG and not tdl.event.isWindowClosed():
        REVEL = True
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                try:
                    if not myMap[x][y].block_sight: #DO NOT REMOVE THIS CHECK. Unless you'd like to see what would happen if the game was running on an actual toaster.
                        myMap[x][y].explored = True
                except:
                    pass
        for spell in spells:
            learnSpell(spell)
        FOV_recompute = True
    elif userInput.keychar == 'B' and DEBUG and not tdl.event.isWindowClosed():
        castPlaceBoss()
        FOV_recompute = True
    elif userInput.keychar == 'S' and DEBUG and not tdl.event.isWindowClosed():
        message("Force-saved level {}", colors.purple)
        saveLevel(branchLevel)
    elif userInput.keychar == 'Q' and DEBUG and not tdl.event.isWindowClosed():
        FOV_recompute = True
        message("You're about to crash the game, press Y to continue.", colors.purple)
        Update()
        tdl.flush()
        keypress = False
        while not keypress:
            for event in tdl.event.get():
                if event.type == "KEYDOWN":
                    confirmKey = event
                    if confirmKey.keychar.upper() == 'Y':
                        crashVariableThatServesNoPurposeOtherThanToCrashTheGameSoIPutAVeryLongNameSoYouUnderstandThatYouMusntntUseIt = 42 / 0
                        otherCrashVariableThatPreventsCodacyFromGoingBananasBecauseUnusedVariable = crashVariableThatServesNoPurposeOtherThanToCrashTheGameSoIPutAVeryLongNameSoYouUnderstandThatYouMusntntUseIt
                        shortOtherCrash = otherCrashVariableThatPreventsCodacyFromGoingBananasBecauseUnusedVariable
                        print(shortOtherCrash)
                        keypress = True
                    elif confirmKey.keychar.upper() not in ("SHIFT", "MAJ", "LEFT SHIFT", "LSHIFT", "LEFT MAJ", 'LMAJ'):
                        keypress = True
                        message('Crash aborted', colors.purple)
                        return 'didnt-take-turn'
                    else:
                        keypress = False
    elif userInput.keychar.upper() == "W" or userInput.keychar.upper() == 'KP5':                 
        FOV_recompute = True
        return 'end turn' 
    elif userInput.keychar == 'A' and gameState == 'playing' and DEBUG and not tdl.event.isWindowClosed():
        castArmageddon()
    elif userInput.keychar == 'l' and gameState == 'playing':
        gameState = 'looking'
        if DEBUG == True:
            message('Look mode', colors.purple)
        lookCursor = GameObject(x = player.x, y = player.y, char = 'X', name = 'cursor', color = colors.yellow, Ghost = True, alwaysAlwaysVisible= True, darkColor=colors.darker_yellow)
        objects.append(lookCursor)
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar == 'L':
        displayLog(50)
    #elif userInput.keychar == 'M':
    #    displayMap()
    elif userInput.keychar == 'C':
        displayCharacter()
    elif userInput.keychar == 's':
        levelUpScreen(newSkillpoints = False)
    elif userInput.keychar == 'd' and gameState == 'playing':
        chosenItem = inventoryMenu('Press the key next to an item to drop it, or press any other key to cancel.')
        if chosenItem is not None:
            chosenItem.drop()
            return 'Drop'
        else:
            return 'didnt-take-turn'
    elif userInput.keychar.upper() == 'Z' and gameState == 'playing':
        try:
            chosenSpell, switch = spellsMenu('Press the key next to a spell to use it.')# (press ? to switch to info mode)')
        except TypeError:
            traceback.print_exc()
            print(switch)
            stopProcess()
            os._exit(-1)
            
        if chosenSpell == None:
            FOV_recompute = True
            if DEBUG:
                message('No spell chosen', colors.violet)
            return 'didnt-take-turn'
        else:
            if not switch:
                #if chosenSpell.magicLevel > player.Player.getTrait(searchedType = 'skill', name = 'Magic ').amount:
                '''
                FOV_recompute = True
                message('Your arcane knowledge is not high enough to cast ' + chosenSpell.name + '.')
                return 'didnt-take-turn'
                '''
                action = chosenSpell.cast(caster = player)
                if action == 'cancelled':
                    FOV_recompute = True
                    return 'didnt-take-turn'
                else:
                    return
                '''
                else:
                    action = chosenSpell.cast(caster = player)
                    if action == 'cancelled':
                        FOV_recompute = True
                        return 'didnt-take-turn'
                    else:
                        return
                '''
            else:
                chosenSpell.displayInfo()
    elif userInput.keychar.upper() == 'X':
        print('SHOOTING')
        #tookTurn = False
        #for obj in getEquippedInHands():
            #if obj.Equipment.ranged:
                #tookTurn = obj.Equipment.shoot() != 'didnt-take-turn' or tookTurn
        #if tookTurn:
            #player.Fighter.actionPoints -= player.Fighter.rangedSpeed
            #return
        weapons = getEquippedInHands()
        if weapons:
            shot, line = weapons[0].Equipment.shoot()
        return shot
    
    elif userInput.keychar.upper() == 'TAB':
        currentSidepanelMode += 1
        if currentSidepanelMode >= len(SIDE_PANEL_MODES):
            currentSidepanelMode = 0

    if gameState == 'looking':
        if userInput.keychar.upper() == 'ESCAPE':
            gameState = 'playing'
            objects.remove(lookCursor)
            del lookCursor
            message('Exited look mode', colors.purple)
            FOV_recompute = True
            return 'didnt-take-turn'
        elif userInput.keychar.upper() in MOVEMENT_KEYS:
            dx, dy = MOVEMENT_KEYS[userInput.keychar.upper()]
            lookCursor.move(dx, dy)
            print(lookCursor.x, lookCursor.y, sep=";")
            FOV_recompute = True
            return 'didnt-take-turn'
        elif userInput.keychar.upper() == 'ENTER':
            for object in objects:
                if object != lookCursor and object.x == lookCursor.x and object.y == lookCursor.y:
                    print('found item under lookCursor')
                    if object.Item:
                        quit = False
                        while not quit:
                            #root.clear()
                            object.Item.displayItem(MID_HEIGHT)
                            lookInput = tdl.event.key_wait()
                            if lookInput.keychar.upper() == 'ESCAPE':
                                quit = True
                            #tdl.flush()
                    if object.Fighter:
                        quit = False
                        while not quit:
                            #root.clear()
                            object.Fighter.displayFighter(MID_HEIGHT)
                            lookInput = tdl.event.key_wait()
                            if lookInput.keychar.upper() == 'ESCAPE':
                                quit = True
                            #tdl.flush()
    if gameState == 'playing':
        if userInput.keychar.upper() in MOVEMENT_KEYS:
            keyX, keyY = MOVEMENT_KEYS[userInput.keychar.upper()]
            action = moveOrAttack(keyX, keyY)
            if action == 'didnt-take-turn':
                return 'didnt-take-turn'
            FOV_recompute = True #Don't ask why, but it's needed here to recompute FOV, despite not moving, or else Bad Things (trademark) happen.
        elif userInput.keychar.upper()== 'SPACE':
            foundObj = False
            for object in objects:
                if object.x == player.x and object.y == player.y:
                    if object.Item is not None:
                        object.Item.pickUp()
                        foundObj = True
                        break
                    elif object.Essence is not None:
                        object.Essence.absorb()
                        foundObj = True
                        break
            if not foundObj:
                return 'didnt-take-turn'
            else:
                return 'Pick Up'
                
        elif userInput.keychar.upper() == '<':
            print('You pressed the freaking climb up key')
            for object in objects:
                if object.x == player.x and object.y == player.y and not object == player:
                    print('{} object is a the same place as the player.'.format(object.name))
                    if object.Stairs:
                        print('object has a stairs component')
                        if object.Stairs.climb == 'up':
                            print('stairs are to climb up')
                            object.Stairs.climbStairs()
                        else:
                            print('stairs are to climb down but you want to go up')
                    else:
                        print('object has no stairs component')
            '''
            if branchLevel > 1 or currentBranch.name != 'Main':
                #saveLevel(branchLevel)
                if upStairs.x == player.x and upStairs.y == player.y:
                    print(currentBranch.name)
                    if stairCooldown == 0:
                        global stairCooldown, branchLevel
                        temporaryBox('Loading...')
                        saveLevel(branchLevel)
                        chosen = False
                        stairCooldown = 2
                        if DEBUG:
                            message("Stair cooldown set to {}".format(stairCooldown), colors.purple)
                        if branchLevel == 1 and currentBranch.name != 'Main':
                            if not chosen:
                                chosen = True
                                print('Returning to origin branch')
                                loadLevel(currentBranch.origDepth, save = False, branch = currentBranch.origBranch)
                            else:
                                print('WHY THE HECK IS THE CODE EXECUTING THIS FFS ?')
                        else:
                            if not chosen:
                                chosen = True
                                toLoad = branchLevel - 1
                                loadLevel(toLoad, save = False)
                            else:
                                print('Chosen was equal to true. If the code ever goes here, I fucking hate all of this.')
                    else:
                        message("You're too tired to climb the stairs right now")
                    return None
            '''
            FOV_recompute = True
        elif userInput.keychar.upper() == '>':
            for object in objects:
                if object.x == player.x and object.y == player.y and not object == player:
                    print('{} object is a the same place as the player.'.format(object.name))
                    if object.Stairs:
                        print('object has a stairs component')
                        if object.Stairs.climb == 'down':
                            print('stairs are to go down')
                            object.Stairs.climbStairs()
                        else:
                            print('stairs are to climb up but you want to go down')
                    else:
                        print('object has no stairs component')
            '''
            if stairs is not None and stairs.x == player.x and stairs.y == player.y:
                if stairCooldown == 0:
                    global stairCooldown
                    temporaryBox('Loading...')
                    stairCooldown = 2
                    boss = False
                    if branchLevel + 1 in currentBranch.bossLevels:
                        boss = True
                    if DEBUG:
                        message("Stair cooldown set to {}".format(stairCooldown), colors.purple)
                    nextLevel(boss)
                else:
                    message("You're too tired to climb down the stairs right now")
            elif gluttonyStairs is not None and gluttonyStairs.x == player.x and gluttonyStairs.y == player.y:
                if stairCooldown == 0:
                    global stairCooldown
                    temporaryBox('Loading...')
                    stairCooldown = 2
                    boss = False
                    if DEBUG:
                        message("Stair cooldown set to {}".format(stairCooldown), colors.purple)
                    nextLevel(boss, changeBranch = dBr.gluttonyDungeon)
                else:
                    message("You're too tired to climb down the stairs right now")
                return None
            elif townStairs is not None and townStairs.x == player.x and townStairs.y == player.y:
                if stairCooldown == 0:
                    global stairCooldown
                    temporaryBox('Loading...')
                    stairCooldown = 2
                    boss = False
                    if DEBUG:
                        message("Stair cooldown set to {}".format(stairCooldown), colors.purple)
                    nextLevel(boss, changeBranch = dBr.hiddenTown)
                else:
                    message("You're too tired to climb down the stairs right now")
            elif greedStairs is not None and greedStairs.x == player.x and greedStairs.y == player.y:
                if stairCooldown == 0:
                    global stairCooldown
                    temporaryBox('Loading...')
                    stairCooldown = 2
                    boss = False
                    if DEBUG:
                        message("Stair cooldown set to {}".format(stairCooldown), colors.purple)
                    nextLevel(boss, changeBranch = dBr.greedDungeon)
                else:
                    message("You're too tired to climb down the stairs right now")
            elif wrathStairs is not None and wrathStairs.x == player.x and wrathStairs.y == player.y:
                if stairCooldown == 0:
                    global stairCooldown
                    temporaryBox('Loading...')
                    stairCooldown = 2
                    boss = False
                    if DEBUG:
                        message("Stair cooldown set to {}".format(stairCooldown), colors.purple)
                    nextLevel(boss, changeBranch = dBr.wrathDungeon)
                else:
                    message("You're too tired to climb down the stairs right now")
                return None
            '''
        elif userInput.keychar.upper() == 'I':
            choseOrQuit = False
            while not choseOrQuit:
                chosenItem = inventoryMenu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosenItem is not None:
                    choseOrQuit = True
                    usage = chosenItem.display([chosenItem.useText, 'Drop', 'Go back'])
                    if usage == 0:
                        using = chosenItem.use()
                        print('using:', using)
                        if using == 'cancelled' or using == 'didnt-take-turn':
                            FOV_recompute = True
                            return 'didnt-take-turn'
                        elif using == 'go back':
                            choseOrQuit = False
                        else:
                            return chosenItem.useText
                    elif usage == 1:
                        chosenItem.drop()
                        return 'Drop'
                    elif usage == 2:
                        choseOrQuit = False
                    else:
                        return 'didnt-take-turn'
                else:
                    return 'didnt-take-turn'
        elif userInput.keychar == 'e':
            chosenItem = inventoryMenu('Press the key next to an item to eat it, or any other to cancel.\n', 'food', 'You have nothing to eat')
            if chosenItem is not None:
                chosenItem.use()
                return 'Eat'
            else:
                return 'didnt-take-turn'
        elif userInput.keychar == '*':
            print('Stairs at {};{}'.format(stairs.x, stairs.y))
            if upStairs is not None:
                print('Upstairs at {};{}'.format(upStairs.x, upStairs.y))
            if gluttonyStairs is not None:
                print('Gluttony stairs at {};{}'.format(gluttonyStairs.x, gluttonyStairs.y))
            if townStairs is not None:
                print('Town stairs at {};{}'.format(townStairs.x, townStairs.y))
            print('Player at {};{}'.format(player.x, player.y))
            print('Current branch : {}'.format(currentBranch.name))
            return 'didnt-take-turn'
        elif userInput.keychar == 'E':
            choseOrQuit = False
            while not choseOrQuit:
                choseOrQuit = True
                chosenItem = equipmentMenu('This is the equipment you are currently wielding.')
                if chosenItem is not None:
                    usage = chosenItem.display(['Unequip', 'Drop', 'Go back'])
                    if usage == 0:
                        using = chosenItem.use()
                        if using == 'cancelled' or using == 'didnt-take-turn':
                            FOV_recompute = True
                            return 'didnt-take-turn'
                        return 'Unequip'
                    elif usage == 1:
                        chosenItem.owner.Equipment.unequip()
                        chosenItem.drop()
                        return 'Unequip'
                    elif usage == 2:
                        choseOrQuit = False
                    else:
                        return 'didnt-take-turn'
                else:
                    FOV_recompute = True
                    return 'didnt-take-turn'
        elif userInput.keychar == '?':
            controlBox()
            return 'didnt-take-turn'
        elif userInput.keychar == 'c':
            FOV_recompute = True
            chat()
        else:
            FOV_recompute = True
            return 'didnt-take-turn'
    FOV_recompute = True

def projectile(sourceX, sourceY, destX, destY, char, color, continues = False, passesThrough = False, ghost = False, line = None, maxRange = None):
    if line is None:
        line = tdl.map.bresenham(sourceX, sourceY, destX, destY)#.remove((sourceX, sourceY))
        line.remove((sourceX, sourceY))
        print(line)
    if len(line) > 1:
        (firstX, firstY)= line[0]
        inclX = firstX - sourceX
        inclY = firstY - sourceY
        incl = (inclX, inclY)
        dx = destX - sourceX
        dy = destY - sourceY
        if char == '/':
            print("Projectile inclination : " + "(" + str(inclX) +', '+ str(inclY) +")")
            if incl == (1, 0) or incl == (-1, 0):
                actualChar = '-'
            elif incl == (1, -1) or incl == (-1, 1):
                actualChar = '/'
            elif incl == (0, 1) or incl == (0, -1):
                actualChar = '|'
            elif incl == (1, 1) or incl == (-1, -1):
                actualChar = chr(92) #92 = ASCII code for backslash (\). Putting directly the '\' character provokes parsing errors.
        else:
            actualChar = char
        proj = GameObject(0, 0, actualChar, 'proj', color)
        objects.append(proj)
        travelledDist = 0
        x, y = firstX, firstY
        for loop in range(len(line)):
            prevX, prevY = x, y
            (x, y) = line.pop(0)
            proj.x, proj.y = x, y
            animStep(.01)
            travelledDist += 1
            if isBlocked(x, y) and (not passesThrough or myMap[x][y].blocked) and not ghost:
                objects.remove(proj)
                if myMap[x][y].blocked:
                    return (prevX, prevY)
                return (x,y)
        if not continues:
            objects.remove(proj)
            return (x,y)
        else:
            for i in range(25):
                newX = x + dx
                newY = y + dy
                startX = x
                startY = y
                line = tdl.map.bresenham(x, y, newX, newY)
                for r in range(len(line)):
                    prevX, prevY = x, y
                    (x, y) = line.pop(0)
                    proj.x, proj.y = x, y
                    animStep(.01)
                    travelledDist += 1
                    if isBlocked(x, y) or (maxRange and travelledDist >= maxRange):
                        objects.remove(proj)
                        if myMap[x][y].blocked:
                            return (prevX, prevY)
                        return (x,y)
                dx = newX - startX
                dy = newY - startY
            print("Projectile out of shotRange")
            #message("Your arrow flies far away from your sight.")
            return (None, None)
    else:
        return(sourceX, sourceY)
        
def satiateHunger(amount, name = None):
    ### HUNGER REMOVED ###
    '''
    player.Player.hunger += amount
    if player.Player.hunger > BASE_HUNGER:
        player.Player.hunger = BASE_HUNGER
    if name:
        message("You eat " + name +".")
    '''
    pass

def checkDiagonals(monster, target):
    diagonals = [(1,1), (1, -1), (-1, 1), (-1, -1)]
    sameX = monster.x == target.x
    sameY = monster.y == target.y
    oldDistance = monster.distanceTo(target)
    
    for i in range(len(diagonals)):
        nx, ny = diagonals[i]
        closerPath = ((not sameX) and monster.x + nx == target.x) or ((not sameY and monster.y + ny == target.y))
        if closerPath and not isBlocked(monster.x + nx, monster.y + ny) and tileDistance(monster.x + nx, monster.y + ny, target.x, target.y) <= oldDistance:
            monster.x += nx
            monster.y += ny
            return "complete"
            break
    return None

def moveOrAttack(dx, dy, spendAtkPoints = True):
    if not 'confused' in convertBuffsToNames(player.Fighter):
        x = player.x + dx
        y = player.y + dy
        if myMap[x][y].chasm and not myMap[x][y].wall and not player.flying and player.Fighter.canMove:
            temporaryBox('You fall deeper into the dungeon...')
            if branchLevel + 1 in currentBranch.bossLevels:
                nextLevel(boss = True, fall = True)
            else:
                nextLevel(fall = True)
    else:
        possibleDirections = [(1, 1), (1,0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]
        index = randint(0, len(possibleDirections) - 1)
        (dx, dy) = possibleDirections[index]
        x = player.x + dx
        y = player.y + dy
    
    target = None
    for object in objects:
        if object != player:
            if object.Fighter and object.x == x and object.y == y:
                target = object
                break #Since we found the target, there's no point in continuing to search for it
    
    if target is not None:
        if player.Player.race == 'Virus ':
            if player.Player.inHost:
                player.Fighter.actionPoints -= player.Fighter.attackSpeed
                player.Fighter.attack(target)
            else:
                player.Player.takeControl(target)
        else:
            if spendAtkPoints:
                player.Fighter.actionPoints -= player.Fighter.attackSpeed
            player.Fighter.attack(target)
    else:
        if not 'burdened' in convertBuffsToNames(player.Fighter):
            moving = player.move(dx, dy)
            if moving == 'didnt-take-turn':
                return 'didnt-take-turn'
            player.Fighter.actionPoints -= player.Fighter.moveSpeed + myMap[player.x][player.y].moveCost(player.flying)
        else:
            return 'didnt-take-turn'

def shoot():
    global FOV_recompute
    weapons = getEquippedInHands()
    if weapons is not None:
        for weapon in weapons:
            if DEBUG:
                print(weapon.name)
            if weapon.Equipment.ranged:
                print('Found ranged weapon')
                if weapon.Equipment.ammo is not None:
                    ammo = weapon.Equipment.ammo
                    for object in inventory:
                        print(object.name)
                        foundAmmo = False
                        if object.name == ammo:
                            message('Choose a target for your ' + weapon.name + '.', colors.cyan)
                            aimedTile = targetTile(weapon.Equipment.maxRange, showBresenham=True)
                            if aimedTile == "cancelled":
                                FOV_recompute = True
                                message('Invalid target.')
                                return 'didnt-take-turn'
                            else:
                                player.Fighter.actionPoints -= player.Fighter.rangedSpeed
                                (aimX, aimY) = aimedTile
                                (targetX, targetY) = projectile(player.x, player.y, aimX, aimY, '/', colors.light_orange, continues=True)
                                FOV_recompute = True
                                monsterTarget = None
                                if targetX is not None and targetY is not None:
                                    for thing in objects:
                                        if thing.Fighter and thing.Fighter.hp > 0 and thing.x == targetX and thing.y == targetY:
                                            monsterTarget = thing
                                            break
                                    if monsterTarget:
                                        [hit, criticalHit] = player.Fighter.toHit(monsterTarget, ranged = True)
                                        dmgTxtFunc = lambda damageTaken: player.Fighter.formatAttackText(monsterTarget, hit, criticalHit, damageTaken, baseText = '{} {}shoot{} {} for {}!', baseNoDmgText = '{} shoot{} {} but it has no effect.')
                                        if hit:
                                            if player.Player.getTrait('trait', 'Aggressive').selected:
                                                damage = randint(weapon.Equipment.rangedPower - 2, weapon.Equipment.rangedPower + 2) + 4
                                            else:
                                                damage = randint(weapon.Equipment.rangedPower - 2, weapon.Equipment.rangedPower + 2)
        
                                            if criticalHit:
                                                damage = damage * player.Fighter.critMultiplier
                                            damageDict = player.Fighter.computeDamageDict(damage)
                                            monsterTarget.Fighter.takeDamage(damageDict, player.name, armored = True, damageTextFunction = dmgTxtFunc)
                                        else:
                                            dmgTxtFunc(0)
                                    else:
                                        message("Your arrow didn't hit anything", colors.grey)
                                else:
                                    message("Your arrow didn't hit anything", colors.grey)
                                object.Item.amount -= 1
                                foundAmmo = True
                                if object.Item.amount <= 0:
                                    inventory.remove(object)
                                break
                    if not foundAmmo:
                        message('You have no ammunition for your ' + weapon.name + ' !', colors.red)
                        return 'didnt-take-turn'
                else:
                    message('Choose a target for your ' + weapon.name + '.', colors.cyan)
                    aimedTile = targetTile(weapon.Equipment.maxRange, showBresenham=True)
                    if aimedTile == "cancelled":
                        FOV_recompute = True
                        message('Invalid target.')
                        return 'didnt-take-turn'
                    else:
                        player.Fighter.actionPoints -= player.Fighter.rangedSpeed
                        (aimX, aimY) = aimedTile
                        (targetX, targetY) = projectile(player.x, player.y, aimX, aimY, '/', colors.light_orange, continues=True)
                        FOV_recompute = True
                        monsterTarget = None
                        if targetX is not None and targetY is not None:
                            for thing in objects:
                                if thing.Fighter and thing.Fighter.hp > 0 and thing.x == targetX and thing.y == targetY:
                                    monsterTarget = thing
                                    break
                            if monsterTarget:
                                [hit, criticalHit] = player.Fighter.toHit(monsterTarget, ranged = True)
                                dmgTxtFunc = lambda damageTaken: player.Fighter.formatAttackText(monsterTarget, hit, criticalHit, damageTaken, baseText = '{} {}shoot{} {} for {}!', baseNoDmgText = '{} shoot{} {} but it has no effect.')
                                if hit:
                                    if player.Player.getTrait('trait', 'Aggressive').selected:
                                        damage = randint(weapon.Equipment.rangedPower - 2, weapon.Equipment.rangedPower + 2) + 4
                                    else:
                                        damage = randint(weapon.Equipment.rangedPower - 2, weapon.Equipment.rangedPower + 2)

                                    if criticalHit:
                                        damage = damage * player.Fighter.critMultiplier
                                    damageDict = player.Fighter.computeDamageDict(damage)
                                    monsterTarget.Fighter.takeDamage(damage, player.name, armored = True, damageTextFunction = dmgTxtFunc)
                                else:
                                    dmgTxtFunc(0)
                            else:
                                message("Your arrow didn't hit anything", colors.grey)
                        else:
                            message("Your arrow didn't hit anything", colors.grey)
            else:
                FOV_recompute = True
                message('You have no ranged weapon equipped.')
                return 'didnt-take-turn'
    else:
        FOV_recompute = True
        message('You have no ranged weapon equipped.')
        return 'didnt-take-turn'

def levelUpScreen(newSkillpoints = True, skillpoint = 3, fromCreation = False, skills = None):
    global menuWindows, FOV_recompute
    quitted = False
    
    class PlaceHolderPlayer:
        def __init__(self):
            self.skillpoints = skillpoint
            self.skills = skills
    
    if not fromCreation:
        origin = player.Player
    else:
        origin = PlaceHolderPlayer()
    if newSkillpoints:
        origin.skillpoints += skillpoint
    if menuWindows:
        for mWindow in menuWindows:
            mWindow.clear()
        FOV_recompute = True
        if not fromCreation:
            Update()
        tdl.flush()
    width = WIDTH - 2
    height = HEIGHT - 2
    window = NamedConsole('levelUpScreen', width, height)
    menuWindows.append(window)
    #quarterX = width//5
    #tier1X = quarterX
    #tier2X = quarterX * 2
    #tier3X = quarterX * 3
    #tier4X = quarterX * 4
    
    notConfirmed = {}
    #tier1list = []
    #tier2list = []
    #tier3list = []
    #for skill in origin.skills:
    #    if skill.tier == 1:
    #        tier1list.append(skill)
    #    elif skill.tier == 2:
    #        tier2list.append(skill)
    #    elif skill.tier == 3:
    #        tier3list.append(skill)
    
    index = 0
    selectedSkill = origin.skills[0]
    selectedSkill.underCursor = True
    while not quitted:
        FOV_recompute = True
        window.clear()
        window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)    
        
        for k in range(width):
            window.draw_char(k, 0, chr(196))
        window.draw_char(0, 0, chr(218))
        window.draw_char(k, 0, chr(191))
        kMax = k
        for l in range(height):
            if l > 0:
                window.draw_char(0, l, chr(179))
                window.draw_char(kMax, l, chr(179))
        lMax = l
        for m in range(width):
            window.draw_char(m, lMax, chr(196))
        window.draw_char(0, lMax, chr(192))
        window.draw_char(kMax, lMax, chr(217))
        
        window.draw_str(1, 1, 'Skillpoints left: ' + str(origin.skillpoints), fg = colors.green)
        
        def drawTreeLines(origSkill):
            if origSkill.allowsSelection:
                for skill in origSkill.allowsSelection:
                    addition = 2
                    if skill.selectable and not skill.selected:
                        color = colors.white
                    elif skill.selectable and skill.selected and (skill in notConfirmed or fromCreation):
                        color = colors.yellow
                    elif skill.selectable and skill.selected and not skill in notConfirmed and not fromCreation:
                        color = colors.dark_red
                    else:
                        color = colors.grey
                        addition = 0
                    for (x, y) in tdl.map.bresenham(origSkill.x + len(origSkill.name)//2 + 2, origSkill.y, skill.x - len(skill.name)//2 - addition, skill.y):
                        window.draw_str(x, y, chr(250), color, None)
                    drawTreeLines(skill)
        #counter1 = 0
        #counter2 = 0
        #counter3 = 0
        #groupCounter2 = 0
        #groupCounter3 = 0
        for skill in origin.skills:
            if skill != selectedSkill:
                skill.underCursor = False

            toAdd = ' ' + str(skill.amount) + '/' + str(skill.maxAmount)
            if skill.isBonus:
                color = colors.dark_red
            elif skill.selectable and not skill.selected:
                color = colors.white
            elif skill.selectable and skill.selected and (skill in notConfirmed or fromCreation):
                color = colors.yellow
            elif (skill.selectable and skill.selected and not skill in notConfirmed and not fromCreation):
                color = colors.dark_red
            else:
                color = colors.grey
                toAdd = ''
            
            drawTreeLines(skill)
            print(skill.name, skill.x, skill.y)
            if not skill.underCursor:
                drawCenteredOnX(window, skill.x, skill.y, skill.name + toAdd, color)
            else:
                skill.displayTrait(window, fromCreation)
                drawCenteredOnX(window, skill.x, skill.y, skill.name + toAdd, colors.black, color)
            
            '''
            if skill.tier == 1:
                if not skill.underCursor:
                    drawCenteredOnX(window, tier1X, 7 + counter1, skill.name, color)
                else:
                    drawCenteredOnX(window, tier1X, 7 + counter1, skill.name, colors.black, color)
                drawCenteredOnX(window, tier1X, 8 + counter1, str(skill.amount)+'/'+str(skill.maxAmount), color)
                counter1 += 21
            if skill.tier == 2:
                if groupCounter2 >= 3:
                    counter2 += 6
                    groupCounter2 = 0
                if not skill.underCursor:
                    drawCenteredOnX(window, tier2X, 2 + counter2, skill.name, color)
                else:
                    drawCenteredOnX(window, tier2X, 2 + counter2, skill.name, colors.black, color)
                drawCenteredOnX(window, tier2X, 3 + counter2, str(skill.amount)+'/'+str(skill.maxAmount), color)
                groupCounter2 += 1
                counter2 += 5
            '''
        
        windowX = 1 #MID_WIDTH - int(width/2)
        windowY = 1
        root.blit(window, windowX, windowY, width, height, 0, 0)
        
        '''
        if 0 <= index < len(tier1list):
            prevList = tier2list
            currentList = tier1list
            nextList = tier2list
        elif len(tier1list) <= index < len(tier2list):
            prevList = tier1list
            currentList = tier2list
            nextList = tier1list
        '''
        
        tdl.flush()
        key = tdl.event.key_wait()
        if key.keychar.upper() == 'ESCAPE':
            #returnList = []
            #if not fromCreation:
            #    for skill in notConfirmed.keys():
            #        returnList.append(skill)
            #else:
            #    for skill in origin.skills:
            #        if skill.selected:
            #            returnList.append(skill)
            return #returnList
        elif key.keychar.upper() == 'DOWN':
            index += 1
        elif key.keychar.upper() == 'UP':
            index -= 1
        elif key.keychar.upper() == 'RIGHT':
            if origin.skills[index].allowsSelection:
                newSkill = origin.skills[index].allowsSelection[0]
            else:
                newSkill = origin.skills[index]
            index = origin.skills.index(newSkill)
        elif key.keychar.upper() == 'LEFT':
            if origin.skills[index].owner:
                newSkill = origin.skills[index].owner
            else:
                newSkill = origin.skills[index]
            index = origin.skills.index(newSkill)
        elif key.keychar.upper() == 'ENTER':
            skill = origin.skills[index]
            if skill.selectable and skill.amount < skill.maxAmount and origin.skillpoints > 0:
                formerAmount = skill.amount
                skill.selected = True
                if not skill in notConfirmed:
                    notConfirmed[skill] = skill.amount
                skill.applyBonus(fromCreation)
                origin.skillpoints -= 1
                for newSkill in skill.allowsSelection:
                    newSkill.selectable = True
        elif key.keychar.upper() == 'BACKSPACE':
            def removeSkillTree(oldSkill):
                for skill in oldSkill.allowsSelection:
                    if (skill in notConfirmed and skill.amount > notConfirmed[skill]) or fromCreation:
                        skill.selected = False
                        skill.selectable = False
                        origin.skillpoints += skill.amount
                        for loop in range(skill.amount):
                            print('removing bonus')
                            skill.removeBonus(fromCreation)
                        skill.amount = 0
                        removeSkillTree(skill)
                
            skill = origin.skills[index]
            if (skill in notConfirmed and skill.amount > notConfirmed[skill]) or (fromCreation and skill.selected):
                skill.removeBonus(fromCreation, True)
                origin.skillpoints += 1
                if not fromCreation:
                    if skill.amount == notConfirmed[skill]:
                        del notConfirmed[skill]
                if skill.amount <= 0:
                    skill.selected = False
                    removeSkillTree(skill)

        if index >= len(origin.skills):
            index = 0
        if index < 0:
            index = len(origin.skills) - 1
        selectedSkill = origin.skills[index]
        selectedSkill.underCursor = True

def checkLevelUp():
    global FOV_recompute
    
    levelUp_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    if player.Fighter.xp >= levelUp_xp:
        print('levelling up from {} to {}'.format(str(player.level), str(player.level + 1)))
        player.level += 1
        player.Player.skillpoints += SKILLPOINTS_PER_LEVEL
        player.Fighter.xp -= levelUp_xp
        message('Your battle skills grow stronger! You reached level ' + str(player.level) + '!', colors.yellow)
        
        #applying Class specific stat boosts
        player.Fighter.noStrengthPower += player.Player.levelUpStats['power']
        player.Fighter.BASE_POWER += player.Player.levelUpStats['power']
        player.Fighter.noDexAccuracy += player.Player.levelUpStats['acc']
        player.Fighter.BASE_ACCURACY += player.Player.levelUpStats['acc']
        player.Fighter.noDexEvasion += player.Player.levelUpStats['ev']
        player.Fighter.BASE_EVASION += player.Player.levelUpStats['ev']
        player.Fighter.baseArmor += player.Player.levelUpStats['arm']
        player.Fighter.BASE_ARMOR += player.Player.levelUpStats['arm']
        player.Fighter.noVitHP += player.Player.levelUpStats['hp']
        player.Fighter.hp += player.Player.levelUpStats['hp']
        player.Fighter.BASE_MAX_HP += player.Player.levelUpStats['hp']
        player.Fighter.noWillMP += player.Player.levelUpStats['mp']
        player.Fighter.MP += player.Player.levelUpStats['mp']
        player.Fighter.BASE_MAX_MP += player.Player.levelUpStats['mp']
        player.Fighter.baseCritical += player.Player.levelUpStats['crit']
        player.Fighter.BASE_CRITICAL += player.Player.levelUpStats['crit']
        player.Player.baseStrength += player.Player.levelUpStats['stren']
        player.Player.BASE_STRENGTH += player.Player.levelUpStats['stren']
        player.Player.baseDexterity += player.Player.levelUpStats['dex']
        player.Player.BASE_DEXTERITY += player.Player.levelUpStats['dex']
        player.Player.baseVitality += player.Player.levelUpStats['vit']
        player.Player.BASE_VITALITY += player.Player.levelUpStats['vit']
        player.Player.baseWillpower += player.Player.levelUpStats['will']
        player.Player.BASE_WILLPOWER += player.Player.levelUpStats['will']
        player.Fighter.baseArmorPenetration += player.Player.levelUpStats['ap']
        player.Fighter.BASE_ARMOR_PENETRATION += player.Player.levelUpStats['ap']
        player.Fighter.noConstStamina += player.Player.levelUpStats['stamina']
        player.Fighter.stamina += player.Player.levelUpStats['stamina']
        
        if player.Player.race == 'Demon Spawn':
            if player.Player.possibleMutations and player.level in player.Player.mutationLevel:
                mutation = randomChoice(player.Player.possibleMutations)
                print('mutation is possible: ' + mutation.name)
                message('You feel strange... You feel like you now have a ' + mutation.name + '.', colors.yellow)
                if mutation.effect:
                    mutation.effect()
            else:
                mutation = randint(1, 4)
                if mutation == 1:
                    player.Player.strength += 1
                    player.Player.BASE_STRENGTH += 1
                    mutationName = 'strength'
                elif mutation == 2:
                    player.Player.dexterity += 1
                    mutationName = 'dexterity'
                    player.Player.BASE_DEXTERITY += 1
                elif mutation == 1:
                    player.Player.vitality += 1
                    mutationName = 'vitality'
                    player.Player.BASE_VITALITY += 1
                else:
                    player.Player.willpower += 1
                    mutationName = 'willpower'
                    player.Player.BASE_WILLPOWER += 1
                message('You feel a strange power flowing through your body...You have gained ' + mutationName + '!', colors.yellow)
        
        if player.Player.race == 'Rootling':
            choice = None
            while choice == None:
                choice = menu('You are now able to grow one part of your wooden body:', ['Trunk', 'Branches', 'Leaves'], LEVEL_SCREEN_WIDTH)
                if choice == 0:
                    armorBonus = randint(1, 3)
                    player.Fighter.BASE_ARMOR += armorBonus
                    player.Fighter.baseArmor += armorBonus
                    hpBonus = randint(5, 15)
                    player.Fighter.BASE_MAX_HP += hpBonus
                    player.Fighter.noVitHP += hpBonus
                    player.Fighter.hp += hpBonus
                elif choice == 1:
                    dexBonus = randint(1, 2)
                    player.Player.dexterity += dexBonus
                    player.Player.BASE_DEXTERITY += dexBonus
                    strBonus = randint(1, 2)
                    player.Player.strength += strBonus
                    player.Player.BASE_STRENGTH += strBonus
                elif choice == 2:
                    willBonus = randint(1, 2)
                    player.Player.willpower += willBonus
                    player.Player.BASE_WILLPOWER += willBonus
                    mpBonus = randint(0, 10)
                    player.Fighter.BASE_MAX_MP += mpBonus
                    player.Fighter.noWillMP += mpBonus
                    player.Fighter.MP += mpBonus
            message('You feel your wooden corpse thickening!', colors.celadon)

        tdl.flush()
        FOV_recompute = True
        Update()
        FOV_recompute = True
        
        '''
        choice = None
        while choice == None:
            choice = menu('Level up! Choose a skill to raise: \n',
                ['Light Weapons (from ' + str(player.Player.getTrait(searchedType = 'skill', name = 'Light weapons').amount) + ')',
                 'Heavy Weapons (from ' + str(player.Player.getTrait(searchedType = 'skill', name = 'Heavy weapons').amount) + ')',
                 'Missile Weapons (from ' + str(player.Player.getTrait(searchedType = 'skill', name = 'Missile weapons').amount) + ')',
                 'Throwing Weapons (from ' + str(player.Player.getTrait(searchedType = 'skill', name = 'Throwing weapons').amount) + ')',
                 'Magic (from ' + str(player.Player.getTrait(searchedType = 'skill', name = 'Magic ').amount) + ')',
                 'Armor wearing (from ' + str(player.Player.getTrait(searchedType = 'skill', name = 'Armor wearing').amount) + ')',
                 'Athletics (from ' + str(player.Player.getTrait(searchedType = 'skill', name = 'Athletics').amount) + ')',
                 'Concentration (from ' + str(player.Player.getTrait(searchedType = 'skill', name = 'Concentration').amount) + ')',
                 'Dodge (from ' + str(player.Player.getTrait(searchedType = 'skill', name = 'Dodge').amount) + ')',
                 'Critical (from ' + str(player.Player.getTrait(searchedType = 'skill', name = 'Critical').amount) + ')',
                 'Accuracy (from ' + str(player.Player.getTrait(searchedType = 'skill', name = 'Accuracy').amount) + ')',], LEVEL_SCREEN_WIDTH)
            if choice != None:
                chosen = player.Player.skills[choice]
                if chosen.amount < chosen.maxAmount:
                    chosen.applyBonus(charCreation = False)
                    FOV_recompute = True
                    Update()
                    break

                else:
                    choice = None
        '''

def isVisibleTile(x, y):
    global myMap
    if x >= MAP_WIDTH or x < 0:
        return False
    elif y >= MAP_HEIGHT or y < 0:
        return False
    #elif myMap[x][y].blocked == True:
        #return False
    elif myMap[x][y].block_sight == True:
        return False
    else:
        return True

def isBlocked(x, y, ignoreSelfSize = True, bigMonster = None): #With this function, making a check such as myMap[x][y].blocked is deprecated and should not be used anymore outside of this function (or FOV related stuff), since the latter does exactly the same job in addition to checking for blocking objects.
    try:
        if myMap[x][y].blocked:
            return True #If the Tile is already set as blocking, there's no point in making further checks
    except IndexError:
        traceback.print_exc()
        '''
        print("X : {} | Y : {}".format(x,y))
        quitGame("Quitted due to error")
        '''
    
    for object in objects:
        try: #As all statements starting with this, ignore PyDev warning. However, please note that objects refers to the list of objects that we created and IS NOT defined by default in any library used (so don't call it out of the blue), contrary to object.
            if ignoreSelfSize and bigMonster is not None:
                if object == bigMonster or object in bigMonster.sizeComponents:
                    pass
                elif (object.blocks or object == player) and object.x == x and object.y == y: #With this, we're checking every single object created, which might lead to performance issue. Fixing this could be one of many possible improvements, but this isn't a priority at the moment. 
                    return True
            elif object.blocks and object.x == x and object.y == y: #With this, we're checking every single object created, which might lead to performance issue. Fixing this could be one of many possible improvements, but this isn't a priority at the moment. 
                return True
        except AttributeError:
            print(objects)
    
    return False

def tileDistance(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        return math.sqrt(dx ** 2 + dy ** 2)

def getMoveCost(destX, destY):
    if myMap[destX][destY].blocked and (player.x, player.y) != (destX, destY):
        return 0.0
    else:
        return 1.0

def castCreateWall():
    target = targetTile()
    if target == 'cancelled':
        return target
    else:
        (x,y) = target
        if not isBlocked(x, y):
            global myMap
            myMap[x][y].baseBlocked = True
            myMap[x][y].block_sight = True

def castCreateChasm():
    target = targetTile()
    if target == 'cancelled':
        return target
    else:
        (x,y) = target
        if not isBlocked(x, y):
            global myMap
            myMap[x][y].baseBlocked = True
            myMap[x][y].block_sight = False

def castPlaceBoss():
    target = targetTile()
    if target == 'cancelled':
        return target
    else:
        (x, y) = target
        if not isBlocked(x, y):
            bossList = ['Gluttony', 'Wrath', 'High Inquisitor']
            boss = menu('What boss ?', bossList, 50)
            placeBoss(bossList[boss], x, y)
        else:
            return 'cancelled'

def applyBurn(target, chance = 70):
    burning = Buff('burning', colors.flame, cooldown= randint(3, 9), continuousFunction=lambda fighter: randomDamage('fire', fighter, chance = 100, minDamage=1, maxDamage=3, dmgMessage = 'You take {} damage from burning !'))
    if target.Fighter and randint(1, 100) <= chance and not 'burning' in convertBuffsToNames(target.Fighter):
        if not 'frozen' in convertBuffsToNames(target.Fighter):
            burning.applyBuff(target)
        else:
            for buff in target.Fighter.buffList:
                if buff.name == 'frozen':
                    buff.removeBuff()
                    message('The ' + target.name + "'s ice melts away.")
    
def monsterArmageddon(monsterName, monsterX, monsterY, radius = 4, damage = 40, selfHit = True):
    radmax = radius + 2
    message(monsterName.capitalize() + ' recites an arcane formula and explodes !', colors.red)
    global explodingTile
    global gameState
    global FOV_recompute
    FOV_recompute = True
    for x in range(monsterX - radmax, monsterX + radmax):
        for y in range(monsterY - radmax, monsterY + radmax):
            try: #Execute code below try if no error is encountered
                if tileDistance(monsterX, monsterY, x, y) <= radius and not myMap[x][y].unbreakable:
                    myMap[x][y].baseBlocked = False
                    myMap[x][y].block_sight = False
                    myMap[x][y].wall = False
                    myMap[x][y].applyGroundProperties(explode=True)
                    if x in range(1, MAP_WIDTH-1) and y in range(1,MAP_HEIGHT - 1):
                        explodingTiles.append((x,y))
                    for obj in objects:
                        if obj.Fighter and obj.x == x and obj.y == y:
                            try:
                                dmgTxtFunc = lambda damageTaken: obj.Fighter.formatRawDamageText(damageTaken, '{} smited for {}!', colors.white, '{} smited but it has no effect.', colors.white, True)
                                if selfHit:
                                    obj.Fighter.takeDamage({'fire': damage}, 'an explosion', damageTextFunction = dmgTxtFunc)
                                elif not (obj.x == monsterX and obj.y == monsterY):      
                                    obj.Fighter.takeDamage({'fire': damage}, 'an explosion', damageTextFunction = dmgTxtFunc)
                            except AttributeError: #If it tries to access a non-existing object (aka outside of the map)
                                continue
            except IndexError: #If an IndexError is encountered (aka if the function tries to access a tile outside of the map), execute code below except
                continue   #Go to next loop iteration and ignore the problematic value     
    #Display explosion eye-candy, this could get it's own function
    for x in range(monsterX - radmax, monsterX + radmax):
        for y in range(monsterY - radmax, monsterY + radmax):
            myMap[x][y].clearance = checkTileClearance(myMap, x, y)
    explode()

# Add push monster spell (create an invisble projectile that pass through a monster, when the said projectile hits a wall, teleport monster to the projectile position and deal X damage to the said monster.)


def castCreateDarksoul(friendly = False):
    target = targetTile()
    if target == 'cancelled':
        return 'cancelled'
    else:
        '''
        (x,y) = target
        monster = createDarksoul(x, y, friendly = friendly)
        objects.append(monster)
        '''
        monsTemp = mobGen.generateMonster(totalLevel, player.level, 'darksoul')
        monster = convertMobTemplate(monsTemp)
        monster.x, monster.y = target
        objects.append(monster)

def castCreateHiroshiman():
    target = targetTile()
    if target == 'cancelled':
        return 'cancelled'
    else:
        (x,y) = target
        monster = createHiroshiman(x, y)
        objects.append(monster)

def castCreateWeapon():
    target = targetTile()
    if target == 'cancelled':
        return 'cancelled'
    else:
        (x,y) = target
        #weapon = createWeapon(x=x, y=y)
        if randint(0, 1):
            weapon = convertItemTemplate(itemGen.generateRangedWeapon(depthLevel, player.level))
            ammoName = weapon.Equipment.ammo
            if ammoName and ammoName != 'none':
                itemComponent = Item(stackable = True, amount = 30)
                ammo = GameObject(x, y, '^', ammoName, colors.light_orange, Item = itemComponent)
                objects.append(ammo)
        else:
            weapon = convertItemTemplate(itemGen.generateMeleeWeapon(depthLevel, player.level, 'gloves'))
        weapon.x, weapon.y = x, y
        if weapon is not None:
            objects.append(weapon)

def castCreateArmor():
    target = targetTile()
    if target == 'cancelled':
        return 'cancelled'
    else:
        (x,y) = target
        #weapon = createWeapon(x=x, y=y)
        weapon = convertItemTemplate(itemGen.generateArmor(depthLevel, player.level))
        weapon.x, weapon.y = x, y
        if weapon is not None:
            objects.append(weapon)

def explode(color = colors.red, char = '*'):
    global gameState
    global explodingTiles
    global FOV_recompute
    gameState = 'exploding'
    for obj in objects :
        obj.clear()
    con.clear()
    FOV_recompute = True
    Update(color, char)
    tdl.flush()
    time.sleep(.1) #Wait for 0.125 seconds
    explodingTiles = []
    FOV_recompute = True
    if player.Fighter.hp > 0:
        gameState = 'playing'
    else:
        gameState = 'dead'

#_____________ MAP CREATION __________________
'''
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
'''

CHANCE_TO_START_ALIVE = 55 #Default : 55
CHANCE_TO_START_ALIVE_CHASM = 65 #Default : 65
DEATH_LIMIT = 3 #Default : 3
BIRTH_LIMIT = 4 #Default : 4
STEPS_NUMBER = 2 #Default : 2
MIN_ROOM_SIZE = 6 #Default : 6

caveList = []
MAX_ITER = 30000
WALL_LIMIT = 4 # number of neighboring walls for this cell to become a wall
WALL_PROB = 50

CAVE_MIN_SIZE = 16
CAVE_MAX_SIZE = 500

SMOOTH_EDGES = True
SMOOTHING = 1

emptyTiles = [] #List of tuples of the coordinates of emptytiles not yet processed by the floodfill algorithm
rooms = []
roomTiles = []
tunnelTiles = []
visuTiles = []
visuEdges = []
confTiles = []
reachableRooms = []
unreachableRooms = []
dispEmpty = False
dispDebug = True
dispClearance = False
unchasmable = []
noCheckTiles = []

'''
def printTileWhenWalked(tile):
    print("Player walked on tile at {};{}".format(tile.x, tile.y))

class Tile:
    def __init__(self, blocked, x, y, block_sight = None, character = None, fg = None, bg = None, dark_fg = None, dark_bg = None, chasm = False, wall = False, hole = False, moveCost = 1):
        self.baseBlocked = blocked
        self.explored = False
        self.unbreakable = False
        self.baseCharacter = character
        self.baseFg = fg
        self.FG = fg
        self.baseBg = bg
        self.BG = bg
        self.baseDark_fg = dark_fg
        self.DARK_FG = dark_fg
        self.baseDark_bg = dark_bg
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
        self.belongsTo = []
        self.usedForPassage = False
        if self.wall:
            self.baseCharacter = '#'
            self.FG = color_light_wall
            self.baseFg = color_light_wall
            self.BG = color_light_ground
            self.baseBg = color_light_ground
            self.DARK_FG = color_dark_wall
            self.baseDark_fg = color_dark_wall
            self.DARK_BG = color_dark_ground
            self.baseDark_bg = color_dark_ground
        if self.chasm:
            self.baseCharacter = None
            self.FG = colors.black
            self.baseFg = colors.black
            self.BG = (0, 0, 16)
            self.baseBg = (0, 0, 16)
            self.DARK_FG = colors.black
            self.baseDark_fg = colors.black
            self.DARK_BG = (0, 0, 16)
            self.baseDark_bg = (0, 0, 16)
        self.moveCost = moveCost
        self.djikValue = None
        self.doNotPropagateDjik = False
        self.onTriggerFunction = printTileWhenWalked
        self.clearance = 1
        self.buffList = []
    
    @property
    def blocked(self):
        if self.buffList:
            for tileBuff in self.buffList:
                if tileBuff.blocksTile:
                    return True
        return self.baseBlocked
    
    @property
    def character(self):
        if self.buffList:
            for tileBuff in self.buffList:
                if tileBuff.char:
                    return tileBuff.char
        return self.baseCharacter
    
    @property
    def fg(self):
        if self.buffList:
            for tileBuff in self.buffList:
                if tileBuff.fg:
                    return tileBuff.fg
        return self.baseFg
    
    @property
    def bg(self):
        if self.buffList:
            for tileBuff in self.buffList:
                if tileBuff.bg:
                    return tileBuff.bg
        return self.baseBg
    
    @property
    def dark_fg(self):
        return self.baseDark_fg
    
    @property
    def dark_bg(self):
        return self.baseDark_bg
        
    def neighbors(self, mapToUse = None):

        global myMap
        x = self.x
        y = self.y
        try:
            upperLeft = myMap[x - 1][y - 1]
        except IndexError:
            upperLeft = None
        except TypeError:
            traceback.print_exc()
            print(myMap)
            print("WRONG TILE = ", end="")
            print(x,y, sep=";")
            
        try:
            up = myMap[x][y - 1]
        except IndexError:
            up = None
            
        try:
            upperRight = myMap[x + 1][y - 1]
        except IndexError:
            upperRight = None
            
        try:
            left = myMap[x - 1][y]
        except IndexError:
            left = None
            
        try:
            right = myMap[x + 1][y]
        except IndexError:
            right = None
            
        try:
            lowerLeft = myMap[x - 1][y + 1]
        except IndexError:
            lowerLeft = None
        
        try:
            low = myMap[x][y + 1]
        except IndexError:
            low = None

        try:
            lowerRight = myMap[x + 1][y + 1]
        except IndexError:
            lowerRight = None
        
        return [i for i in [upperLeft, up, upperRight, left, right, lowerLeft, low, lowerRight] if i is not None]

        
        return neighborsOutOfClass(int(self.x), int(self.y), mapToUse)

    def neighbours(self, mapToUse = None):
        result = self.neighbors(mapToUse = None)
        return result
    
    def cardinalNeighbors(self):
        x = self.x
        y = self.y
        try:
            up = myMap[x][y - 1]
        except IndexError:
            up = None
        try:
            left = myMap[x - 1][y]
        except IndexError:
            left = None
        try:
            right = myMap[x + 1][y]
        except IndexError:
            right = None
        try:
            low = myMap[x][y + 1]
        except IndexError:
            low = None
        return [i for i in [up, left, right, low] if i is not None]
    
    def cardinalNeighbours(self):
        result = self.cardinalNeighbors()
        return result

    def applyWallProperties(self):
        if not self.secretWall:
            self.wall = True
            self.baseCharacter = '#'
            self.FG = color_light_wall
            self.baseFg = color_light_wall
            self.BG = color_light_ground
            self.baseBg = color_light_ground
            self.DARK_FG = color_dark_wall
            self.baseDark_fg = color_dark_wall
            self.DARK_BG = color_dark_ground
            self.baseDark_bg = color_dark_ground
    
    def applyChasmProperties(self):
        if not self.secretWall:
            self.chasm = True
            self.baseCharacter = None
            self.FG = colors.black
            self.baseFg = colors.black
            self.BG = (0, 0, 16)
            self.baseBg = (0, 0, 16)
            self.DARK_FG = colors.black
            self.baseDark_fg = colors.black
            self.DARK_BG = (0, 0, 16)
            self.baseDark_bg = (0, 0, 16)
    
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
                self.baseBlocked = False
                self.block_sight = False
                if gravelChoice == 0:
                    self.baseCharacter = gravelChar1
                elif gravelChoice == 1:
                    self.baseCharacter = gravelChar2
                else:
                    self.baseCharacter = None
                self.baseFg = color_light_gravel
                self.baseBg = color_light_ground
                self.baseDark_fg = color_dark_gravel
                self.baseDark_bg = color_dark_ground
                self.wall = False
                self.chasm = False
        else:
            if not self.secretWall or self.pillar:
                gravelChoice = randint(0, 5)
                self.baseBlocked = False
                self.block_sight = False
                if gravelChoice == 0:
                    self.baseCharacter = gravelChar1
                elif gravelChoice == 1:
                    self.baseCharacter = gravelChar2
                else:
                    self.baseCharacter = None
                self.baseFg = color_light_gravel
                self.baseBg = color_light_ground
                self.baseDark_fg = color_dark_gravel
                self.baseDark_bg = color_dark_ground
                self.wall = False
    
    def setUnbreakable(self):
        self.baseBlocked = True
        self.unbreakable = True
        self.wall = True
        
    def open(self):
        if not self.unbreakable:
            self.baseBlocked = False
            self.block_sight = False
            self.wall = False
            return True
        else:
            return False
    
    def close(self, makeIndestructible = False):
        if not self.blocked:
            self.baseBlocked = True
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

class Rectangle:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        
    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)
 
    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)
    
    @property
    def tiles(self):
        tileList = [myMap[x][y] for x in range(self.x1 + 1, self.x2) for y in range(self.y1 + 1, self.y2)]
        print("PRINTING LIST")
        print("GOING TO PRINT TILES LIST")
        print("PRINTING A LOT OF CAPITALIZED MESAGE SO IM SURE I WILL SEE THEM")
        print("ACTUALLY PRINTING NEXT MESSAGE")
        print(tileList)
        print("LIST IS JUST HIGHER")
        print("LIST IS TWO MESSAGES HIGHER")
        return tileList
    
class Square:
    def __init__(self, x, y, s):
        self.x1 = x
        self.y1 = y
        self.x2 = x + s
        self.y2 = y + s
        self.s = s
    
    def tiles(self, mapToUse):
        if self.s == 0:
            tileList = [mapToUse[self.x1][self.y1]]
        else:
            tileList = [mapToUse[x][y] for x in range(self.x1, self.x2 + 1) for y in range(self.y1, self.y2 + 1)]
        return tileList

### FORMER CAVE GEN ###
class CaveRoom:
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

#def floodFill(x, y, listToAppend, edgeList):
def formerFloodFill(x, y, listToAppend, edgeList):
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

def bossFFWrapper(x,y, listToAppend, dependsOnList):
    global stopBossFF, visuBoss
    stopBossFF = False
    visuBoss = []
    bossFloodfill(x,y, listToAppend, dependsOnList)
    
def neighborsOutOfClass(x,y, mapToUse = None):
    #global myMap
    '''
    Tk().withdraw()
    showwarning("FUNC CALLED", "WE CALLED NEIGHBOURSOUTOFCLASS METHOD")
    if myMap is None:
        showwarning("MYMAP IS NOOONE", "WTFFFFFFFFFFFFFFFFFFFF")
        myMap = globals()['myMap']
        if myMap is None:
            showerror('I hate this', "Python go fucking kill yourself")
    '''
    if mapToUse is None:
        print("NOOOOOOOOOOOOOOOOOOOOOOOOOOOO MAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPPPPPPPPPPPPPP TOOOOOOOOOOOOOOOOOOO USSSSSSSSSSSSSSSSEEEEEEEEEE")
        actualMapThatTheFuncWillFuckingUseOrElseIAmThrowingMyComputerOutsideTheFuckingWindow = myMap
    else:
        actualMapThatTheFuncWillFuckingUseOrElseIAmThrowingMyComputerOutsideTheFuckingWindow = mapToUse
    try:
        upperLeft = actualMapThatTheFuncWillFuckingUseOrElseIAmThrowingMyComputerOutsideTheFuckingWindow[x - 1][y - 1]
    except IndexError:
        upperLeft = None
    except TypeError:
        traceback.print_exc()
        print(actualMapThatTheFuncWillFuckingUseOrElseIAmThrowingMyComputerOutsideTheFuckingWindow)
        print("WRONG TILE = ", end="")
        print(x,y, sep=";")
        
    try:
        up = actualMapThatTheFuncWillFuckingUseOrElseIAmThrowingMyComputerOutsideTheFuckingWindow[x][y - 1]
    except IndexError:
        up = None
        
    try:
        upperRight = actualMapThatTheFuncWillFuckingUseOrElseIAmThrowingMyComputerOutsideTheFuckingWindow[x + 1][y - 1]
    except IndexError:
        upperRight = None
        
    try:
        left = actualMapThatTheFuncWillFuckingUseOrElseIAmThrowingMyComputerOutsideTheFuckingWindow[x - 1][y]
    except IndexError:
        left = None
        
    try:
        right = actualMapThatTheFuncWillFuckingUseOrElseIAmThrowingMyComputerOutsideTheFuckingWindow[x + 1][y]
    except IndexError:
        right = None
        
    try:
        lowerLeft = actualMapThatTheFuncWillFuckingUseOrElseIAmThrowingMyComputerOutsideTheFuckingWindow[x - 1][y + 1]
    except IndexError:
        lowerLeft = None
    
    try:
        low = actualMapThatTheFuncWillFuckingUseOrElseIAmThrowingMyComputerOutsideTheFuckingWindow[x][y + 1]
    except IndexError:
        low = None

    try:
        lowerRight = actualMapThatTheFuncWillFuckingUseOrElseIAmThrowingMyComputerOutsideTheFuckingWindow[x + 1][y + 1]
    except IndexError:
        lowerRight = None
        
    return [i for i in [upperLeft, up, upperRight, left, right, lowerLeft, low, lowerRight] if i is not None]
            
        

def bossFloodfill(x,y, listToAppend, dependsOnList):
    global stopBossFF
    if not myMap[x][y].blocked:
        if (x,y) in dependsOnList:
            dependsOnList.remove((x,y))
            visuBoss.append(myMap[x][y])
            
            for tile in myMap[x][y].neighbors(myMap): #I don't know why it doesn't work with just the vanilla floodfill, but this is necessary so as to find the entrance
                if not (tile.blocked or tile in bossTiles):
                    listToAppend.append(tile)
                    stopBossFF = True
                    print("FF STOP BECAUSE {};{} NOT IN BOSS TILES".format(tile.x, tile.y))
                    return
            
            if not myMap[x][y] in bossTiles: #As said above, I don't know why but this alone doesn't work
                listToAppend.append(myMap[x][y])
                stopBossFF = True
                print("FF STOP BECAUSE {};{} NOT IN BOSS TILES".format(x,y))
                #raise ValueError('Actually found a value, stopping the program to show we found one')
                return
            elif not stopBossFF:
                bossFloodfill(x+1, y, listToAppend, dependsOnList)
                bossFloodfill(x-1, y, listToAppend, dependsOnList)
                bossFloodfill(x, y+1, listToAppend, dependsOnList)
                bossFloodfill(x, y-1, listToAppend, dependsOnList)
                bossFloodfill(x+1, y+1, listToAppend, dependsOnList)
                bossFloodfill(x-1, y+1, listToAppend, dependsOnList)
                bossFloodfill(x+1, y-1, listToAppend, dependsOnList)
                bossFloodfill(x-1, y-1, listToAppend, dependsOnList)
            else:
                print("FF STOP BECAUSE BOSS STOP {};{}".format(x,y))
            '''
            if myMap[x][y] in bossTiles:
                if not stopBossFF:
                    bossFloodfill(x+1, y, listToAppend, dependsOnList)
                    bossFloodfill(x-1, y, listToAppend, dependsOnList)
                    bossFloodfill(x, y+1, listToAppend, dependsOnList)
                    bossFloodfill(x, y-1, listToAppend, dependsOnList)
                    bossFloodfill(x+1, y+1, listToAppend, dependsOnList)
                    bossFloodfill(x-1, y+1, listToAppend, dependsOnList)
                    bossFloodfill(x+1, y-1, listToAppend, dependsOnList)
                    bossFloodfill(x-1, y-1, listToAppend, dependsOnList)
                else:
                    print("FF STOP BECAUSE BOSS STOP {};{}".format(x,y))
            else:
                global stopBossFF
                listToAppend.append(myMap[x][y])
                stopBossFF = True
                print("FF STOP BECAUSE {};{} NOT IN BOSS TILES".format(x,y))
                raise ValueError('Actually found a value, stopping the program to show we found one')
                return
            '''
                
        else:
            print("FF STOP BECAUSE {};{} NOT IN EMPTY TILES".format(x,y))
            return
    else:
        print("FF STOP BECAUSE {};{} BLOCKED".format(x,y))
        return
                
    
def countNeighbours(mapToUse, startX, startY, stopAtFirst = False, searchBlock = True, searchChasm = False):
    count = 0
    found = False
    for x in range(-1, 2):
        for y in range(-1, 2):
            if x == 0 and y == 0:
                continue
            else:
                otherX = startX + x
                otherY = startY + y
                if 0 <= otherX < MAP_WIDTH and 0 <= otherY < MAP_HEIGHT:
                    if mapToUse[otherX][otherY].blocked or mapToUse[otherX][otherY].pillar and searchBlock:
                        count += 1
                        found = True
                        if stopAtFirst:
                            break
                    if mapToUse[otherX][otherY].chasm and searchChasm:
                        count += 1
                        found = True
                        if stopAtFirst:
                            break
        if stopAtFirst and found:
            break
    return count

def countCardinalNeighbours(mapToUse, startX, startY, stopAtFirst = False, searchBlock = True, searchChasm = False):
    count = 0
    found = False
    for x in range(-1, 2):
        for y in range(-1, 2):
            if x == 0 and y == 0:
                continue
            elif x == 0 or y == 0:
                otherX = startX + x
                otherY = startY + y
                if 0 <= otherX < MAP_WIDTH and 0 <= otherY < MAP_HEIGHT:
                    if mapToUse[otherX][otherY].blocked or mapToUse[otherX][otherY].pillar and searchBlock:
                        count += 1
                        found = True
                        if stopAtFirst:
                            break
                    if mapToUse[otherX][otherY].chasm and searchChasm:
                        count += 1
                        found = True
                        if stopAtFirst:
                            break
        if stopAtFirst and found:
            break
    return count

def findNeighbours(startX, startY):
    if myMap[startX - 1][startY].blocked:
        return (startX - 1, startY)
    
    elif myMap[startX - 1][startY - 1].blocked:
        return (startX - 1, startY - 1)
    
    elif myMap[startX - 1][startY + 1].blocked:
        return (startX - 1, startY + 1)
    
    elif myMap[startX + 1][startY].blocked:
        return (startX + 1, startY)
    
    elif myMap[startX + 1][startY - 1].blocked:
        return (startX + 1, startY - 1)
    
    elif myMap[startX + 1][startY + 1].blocked:
        return (startX + 1, startY + 1)
    
    elif myMap[startX][startY - 1].blocked:
        return (startX, startY - 1)
    
    elif myMap[startX][startY + 1].blocked:
        return (startX, startY + 1)
    
def removeFromEmptyTiles(x, y):
    if (x,y) in emptyTiles:
        emptyTiles.remove((x,y))

def openTile(x, y, mapToUse):
    if mapToUse[x][y].open() and not (x,y) in emptyTiles:
        #emptyTiles.append((x,y))
        pass

def closeTile(x, y, mapToUse, makeIndestructible = False):
    mapToUse[x][y].close(makeIndestructible)
    #removeFromEmptyTiles(x,y)
    
def refreshEmptyTiles():
    global emptyTiles
    emptyTiles = []
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if not myMap[x][y].blocked:
                emptyTiles.append((x,y))
                
def updateTileCoords():
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            myMap[x][y].x = int(x)
            myMap[x][y].y = int(y)

def doStep(oldMap):
    newMap = list(deepcopy(baseMap)) #Create a new empty map (except for the borders)
    for x in range(1, MAP_WIDTH - 1):
        for y in range(1, MAP_HEIGHT - 1):
            neighbours = countNeighbours(oldMap, x, y) #Count the walls around each tile on the former map (myMap)
            if oldMap[x][y].blocked: #If said tile is blocked in the former map
                if neighbours < DEATH_LIMIT: #If it has less neighbouring walls than the limit for which we open it
                    openTile(x, y, newMap) #Open this tile in the new map
                else:
                    closeTile(x, y, newMap) #Else, ensure it stays a wall in the new map
                    print('Blocking')
            else: #If it's an empty tile
                if neighbours > BIRTH_LIMIT: #If it has more neighbouring walls than the limit for which we close it
                    closeTile(x, y, newMap) #Make it a wall in the new map
                    print('Blocking')
                else:
                    openTile(x, y, newMap) #Else, ensure it stays an empty tile in the new map
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
                            bestDistance = round(distance)
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
                            bestDistance = round(distance)
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
                        (xX, yY) = roomA.borders[tileIndexA]
                        if myMap[xX][yY].usedForPassage:
                            continue
                        for tileIndexB in range(0, len(roomB.borders) - 1):
                            (xA, yA) = roomA.borders[tileIndexA]
                            (xB, yB) = roomB.borders[tileIndexB]
                            if myMap[xB][yB].usedForPassage:
                                continue
                        distance = (xA - xB)**2 + (yA - yB)**2
                        
                        if distance < bestDistance or not possibleConnectionFound:
                            bestDistance = round(distance)
                            possibleConnectionFound = True
                            bestTileA = (int(xA), int(yA))
                            bestTileB = (int(xB), int(yB))
                            bestRoomB = roomB
                    if possibleConnectionFound:
                        createPassage(bestRoomA, bestRoomB, bestTileA, bestTileB)
                        updateReachLists()
                        reachIndex = 0
                        Update()

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
        myMap[x][y].usedForPassage = True
    
    otherTileA = findNeighbours(xA, yA)
    otherTileB = findNeighbours(xB, yB)
    bugged = False
    try:
        (xOA, yOA) = otherTileA
    except TypeError:
        traceback.print_exc()
        root.draw_char(xB, yB, char = "X", fg = colors.green)
        tdl.flush()
        bugged = True
    
    try:
        (xOB, yOB) = otherTileB
    except TypeError:
        traceback.print_exc()
        root.draw_char(xB, yB, char = "X", fg = colors.green)
        tdl.flush()
        bugged = True

        
    if not bugged:
        otherPassage = tdl.map.bresenham(xOA, yOA, xOB, yOB)
        for (x,y) in otherPassage:
            openTile(x,y,myMap)
            myMap[x][y].usedForPassage = True
                
    
    
    
def generateCave(fall = False):
    '''
    
    @author: Gawein LE GOFF
    Generates a cavern looking like map.
    
    '''
    global myMap, bossTiles, baseMap, mapToDisp, maps, visuTiles, state, visuEdges, confTiles, rooms, curRoomIndex, stairs, objects, upStairs, bossDungeonsAppeared, color_dark_wall, color_light_wall, color_dark_ground, color_light_ground, color_dark_gravel, color_light_gravel, townStairs, gluttonyStairs, stairs, upStairs, nemesisList, wrathStairs
    myMap = [[Tile(blocked=False, x = x, y = y, block_sight=False) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)] #Initialisation de la carte
    visuTiles = []
    visuEdges = []
    confTiles = []
    curRoomIndex = 0
    curRoomIndex = 0
    
    rooms = []
    
    stairs = None
    upStairs = None
    gluttonyStairs = None
    townStairs = None
    wrathStairs = None
    bossTiles = None
        
    color_dark_wall = currentBranch.color_dark_wall
    color_light_wall = currentBranch.color_light_wall
    color_dark_ground = currentBranch.color_dark_ground
    color_dark_gravel = currentBranch.color_dark_gravel
    color_light_ground = currentBranch.color_light_ground
    color_light_gravel = currentBranch.color_light_gravel

    
    numberRooms = 0
    objects = [player]
    for x in range(MAP_WIDTH):
        myMap[x][0].setUnbreakable()
        removeFromEmptyTiles(x,0)
        myMap[x][MAP_HEIGHT - 1].setUnbreakable()
        removeFromEmptyTiles(x, MAP_HEIGHT - 1)
        for y in range(MAP_HEIGHT):
            if not myMap[x][y].blocked and not (x,y) in emptyTiles:
                emptyTiles.append((x,y))
    for y in range(MAP_HEIGHT):
        myMap[0][y].setUnbreakable()
        removeFromEmptyTiles(0, y)
        myMap[MAP_WIDTH - 1][y].setUnbreakable()
        removeFromEmptyTiles(MAP_WIDTH - 1, y)

    baseMap = list(deepcopy(myMap))

        
    for x in range(1, MAP_WIDTH - 1):
        for y in range(1, MAP_HEIGHT - 1):
            myMap[x][y].djikValue = None
            if randint(0, 100) < CHANCE_TO_START_ALIVE:
                closeTile(x, y, myMap) #Place walls randomly

    for loop in range(STEPS_NUMBER):
        myMap = doStep(myMap) #Transform randomly placed walls into room
    maps = [myMap, baseMap]
    refreshEmptyTiles()
    print("Freezing")
    state = "floodfillPrep"

    if not tdl.event.is_window_closed():
        print("Continuing")
        state = "floodfill"
        while emptyTiles:
            (x,y) = emptyTiles[0]
            #time.sleep(0.05)
            newRoomTiles = [] #Tiles of the room to create
            newRoomEdges = [] #Tiles at the borders of the room to create
            try:
                floodFill(x,y, newRoomTiles, newRoomEdges) #We use the floodfill function to identify the room and to fill the newRoomTiles and newRoomEdges lists
            except RecursionError: #If a RecursionError is encountered in the try block execute the following block
                traceback.print_exc() #Print the error message
                print(sys.getrecursionlimit()) #Print the recursion limt
                os._exit(-1) #Quit the programm so as to avoid other errors that would hide this one
            newRoom = CaveRoom(newRoomTiles, borders = newRoomEdges)
            if len(newRoom.tiles) < MIN_ROOM_SIZE:
                newRoom.remove() #If room is too small, turn it back into walls
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
                        
        for room in rooms:
            room.claimBorders() #Check if the room's border aren't shared with another room, else add the contested tiles to the contestedTiles list of said room
            #visuEdges.extend(room.borders)
            confTiles.extend(room.contestedTiles) #Add this room's contested tiles to the global list of contested tiles
        state = "roomMergePrep"
        refreshEmptyTiles()
        tempRooms = list(rooms) #Working directly on the rooms list makes problems appear, so we use a copy instead
        while tempRooms:
            for rum in tempRooms: 
                if rum not in rooms:
                    tempRooms.remove(rum) #If we encounter a room in the temp list (which is supposed to have the same content as the original), that is not in the original list (yes, it actually happens because black magic I guess)
            room = tempRooms[0]
            oldRoomBorders = []
            if room.contestedTiles: #If there are conflicting tiles in the current room
                for (x,y) in room.contestedTiles:
                    openTile(x,y, myMap) #Replace contested borders by empty tiles
                    if (x,y) in visuEdges:
                        visuEdges.remove((x,y))
                    for owner in myMap[x][y].belongsTo:
                        oldRoomBorders.append((x,y))
                        owner.borders.remove((x,y)) #Remove old wall from the walls list of the rooms it used to belong to
                        room.mergeWith(owner, oldRoomBorders) #Merge room who used to share this wall
            tempRooms.remove(room)
        
        rooms[0].mainRoom = True #Make so the first room is the main room
        rooms[0].reachableFromMainRoom = True #Since it is the main room, it is reachable from the main room.
        
        connectRooms(rooms) #Connect in the first place rooms based solely on distance between them, without taking in account rechability from the main room.
        connectRooms(rooms, True) #Connect rooms between a second time, this time forcing them to be connected to either the main room or to a room reachable from the main room
        state = "normal"
        refreshEmptyTiles()
        checkMap()
        (pX, pY) = rooms[0].tiles[randint(0, len(rooms[0].tiles) - 1)]
        if not fall:
            player.x = pX
            player.y = pY
        if branchLevel > 1:
            formerBranch = currentBranch
        elif currentBranch.name != 'Main':
            formerBranch = currentBranch.origBranch
        else:
            formerBranch = None
        upStairs = GameObject(pX, pY, '<', 'stairs', currentBranch.mapGeneration['stairsColor'], alwaysVisible = True, darkColor = currentBranch.mapGeneration['stairsDarkColor'], Stairs = Stairs(climb='up', branchesFrom=formerBranch, branchesTo=currentBranch))
        objects.append(upStairs)
        upStairs.sendToBack()
        stairsRoom = rooms[randint(1, len(rooms) - 1)]
        (sX, sY) = stairsRoom.tiles[randint(0, len(stairsRoom.tiles) - 1)]
        stairs = GameObject(sX, sY, '>', 'stairs', currentBranch.mapGeneration['stairsColor'], alwaysVisible = True, darkColor = currentBranch.mapGeneration['stairsDarkColor'], Stairs = Stairs(climb='down', branchesFrom=currentBranch, branchesTo=currentBranch))
        objects.append(stairs)
        stairs.sendToBack()
        applyIdentification()
        for room in rooms:
            if room == rooms[0]:
                placeObjects(room, True)
            else:
                placeObjects(room, False)
    
        if fall:
            fallen = False
            while not fallen:
                x, y = randint(1, MAP_WIDTH - 1), randint(1, MAP_HEIGHT - 1)
                if not myMap[x][y].chasm and not isBlocked(x, y):
                    player.x, player.y = x, y
                    fallen = True
        updateTileCoords()
        myMap = clearanceMap(myMap)
        print("DONE")

        #gameState = 'dead' #What the hell ?
### END FORMER CAVE GEN ###
### NEW CAVE GEN ###
def randomFillMap():
    global caveList, myMap
    for x in range(1, MAP_WIDTH-1):
        for y in range(1, MAP_HEIGHT-1):
            if randint(1, 100) >= WALL_PROB:
                myMap[x][y].baseBlocked = False


def cleanUpMap():
    global caveList, myMap
    if (SMOOTH_EDGES):
        for i in range(0, 5):
            # Look at each cell individually and check for smoothness
            for x in range(1, MAP_WIDTH-1):
                for y in range (1, MAP_HEIGHT-1):
                    if myMap[x][y].blocked and countCardinalNeighbours(myMap, x, y) <= SMOOTHING:
                        myMap[x][y].baseBlocked = False

def createCaves():
    global caveList, myMap
    # ==== Create distinct caves ====
    for i in range(0, MAX_ITER):
        # Pick a random point with a buffer around the edges of the map
        tileX = randint(1, MAP_WIDTH-2) #(2,mapWidth-3)
        tileY = randint(1, MAP_HEIGHT-2) #(2,mapHeight-3)

        # if the cell's neighboring walls > self.neighbors, set it to 1
        if countNeighbours(myMap, tileX, tileY) > WALL_LIMIT:
            myMap[tileX][tileY].baseBlocked = True
        # or set it to 0
        elif countNeighbours(myMap, tileX, tileY) < WALL_LIMIT:
            myMap[tileX][tileY].baseBlocked = False
     

    # ==== Clean Up Map ====
    cleanUpMap()

def createTunnel(point1, point2, currentCave):
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
            if myMap[drunkardX][drunkardY].baseBlocked:
                myMap[drunkardX][drunkardY].wall = False
                myMap[drunkardX][drunkardY].baseBlocked = False

def floodFill(x,y):
    global caveList, myMap
    '''
    flood fill the separate regions of the level, discard
    the regions that are smaller than a minimum size, and 
    create a reference for the rest.
    '''
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

    if len(cave) >= CAVE_MIN_SIZE:
        caveList.append(cave)

def getCaves():
    global caveList, myMap
    # locate all the caves within myMap and stores them in caveList
    for x in range (MAP_WIDTH):
        for y in range (MAP_HEIGHT):
            if not myMap[x][y].blocked:
                floodFill(x,y)

    for cave in caveList:
        for tile in cave:
            x, y = tile
            myMap[x][y].baseBlocked = False
            myMap[x][y].wall = False

def checkConnectivity(cave1, cave2):
    global caveList, myMap
    # floods cave1, then checks a point in cave2 for the flood

    connectedRegion = []
    start = cave1[randint(0, len(cave1) - 1)] # get an element from cave1
    
    toBeFilled = [start]
    while toBeFilled:
        tile = toBeFilled.pop()

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

    end = cave2[randint(0, len(cave2) - 1)]

    if end in connectedRegion: return True

    else: return False

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
            createTunnel(point1, point2,currentCave)

def generateCaveLevel(fall = False):
    global caveList, myMap
    global myMap, bossTiles, baseMap, mapToDisp, maps, visuTiles, state, visuEdges, confTiles, rooms, curRoomIndex, stairs, objects, upStairs, bossDungeonsAppeared, color_dark_wall, color_light_wall, color_dark_ground, color_light_ground, color_dark_gravel, color_light_gravel, townStairs, gluttonyStairs, stairs, upStairs, nemesisList, wrathStairs
    # Creates an empty 2D array or clears existing array
    caveList = []
    
    stairs = None
    upStairs = None
    gluttonyStairs = None
    townStairs = None
    wrathStairs = None
    bossTiles = None
        
    color_dark_wall = currentBranch.color_dark_wall
    color_light_wall = currentBranch.color_light_wall
    color_dark_ground = currentBranch.color_dark_ground
    color_dark_gravel = currentBranch.color_dark_gravel
    color_light_ground = currentBranch.color_light_ground
    color_light_gravel = currentBranch.color_light_gravel

    print('creating cave map')
    myMap = [[Tile(True, x, y, wall = True) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]
    print('filling map')
    randomFillMap()
    print('creating caves')
    createCaves()
    print('getting caves')
    getCaves()
    print('connecting caves')
    connectCaves()
    print('cleaning up map')
    cleanUpMap()
    
    checkMap(False)

    objects = [player]

    stairsX, stairsY = 0, 0
    while myMap[stairsX][stairsY].blocked and countNeighbours(myMap, stairsX, stairsY, True) > 0:
        stairsX = randint(1, MAP_WIDTH - 2)
        stairsY = randint(1, MAP_HEIGHT - 2)
    
    if not fall:
        player.x = stairsX
        player.y = stairsY

    if branchLevel > 1:
        formerBranch = currentBranch
    elif currentBranch.name != 'Main':
        formerBranch = currentBranch.origBranch
    else:
        formerBranch = None
    upStairs = GameObject(stairsX, stairsY, '<', 'stairs', currentBranch.mapGeneration['stairsColor'], alwaysVisible = True, darkColor = currentBranch.mapGeneration['stairsDarkColor'], Stairs = Stairs(climb='up', branchesFrom=formerBranch, branchesTo=currentBranch))
    objects.append(upStairs)
    upStairs.sendToBack()
    
    sX, sY = 0, 0
    while myMap[sX][sY].blocked and countNeighbours(myMap, sX, sY, True) > 0:
        sX = randint(1, MAP_WIDTH - 2)
        sY = randint(1, MAP_HEIGHT - 2)
    stairs = GameObject(sX, sY, '>', 'stairs', currentBranch.mapGeneration['stairsColor'], alwaysVisible = True, darkColor = currentBranch.mapGeneration['stairsDarkColor'], Stairs = Stairs(climb='down', branchesFrom=currentBranch, branchesTo=currentBranch))
    objects.append(stairs)
    stairs.sendToBack()
    applyIdentification()
    for room in caveList:
        placeObjects(room, False)

    if fall:
        fallen = False
        while not fallen:
            x, y = randint(1, MAP_WIDTH - 1), randint(1, MAP_HEIGHT - 1)
            if not myMap[x][y].chasm and not isBlocked(x, y):
                player.x, player.y = x, y
                fallen = True
    updateTileCoords()
    myMap = clearanceMap(myMap)
    print("DONE")
### END NEW CAVE GEN ###
        
def createRoom(room, pillar=False):
    global myMap, roomTiles
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            myMap[x][y].applyGroundProperties(temple = pillar)
            roomTiles.append((x, y))
    if pillar:
        centerPillar = randint(0, 2)
        if centerPillar != 0:
            myMap[room.x1 + 2][room.y1 + 2].pillar = True
            myMap[room.x1 + 2][room.y1 + 2].baseBlocked = True
            myMap[room.x1 + 2][room.y1 + 2].baseCharacter = 'o'
            myMap[room.x1 + 2][room.y2 - 2].pillar = True
            myMap[room.x1 + 2][room.y2 - 2].baseBlocked = True
            myMap[room.x1 + 2][room.y2 - 2].baseCharacter = 'o'
            myMap[room.x2 - 2][room.y1 + 2].pillar = True
            myMap[room.x2 - 2][room.y1 + 2].baseBlocked = True
            myMap[room.x2 - 2][room.y1 + 2].baseCharacter = 'o'
            myMap[room.x2 - 2][room.y2 - 2].pillar = True
            myMap[room.x2 - 2][room.y2 - 2].baseBlocked = True
            myMap[room.x2 - 2][room.y2 - 2].baseCharacter = 'o'
        else:
            x, y = room.center()
            myMap[x][y].baseBlocked = True
            myMap[x][y].pillar = True
            myMap[x][y].baseCharacter = 'o'
            
def checkMap(temple = False):
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            myMap[x][y].djikCost = None
            if not (x, y) in noCheckTiles:
                if myMap[x][y].hole and not myMap[x][y].unbreakable:
                    myMap[x][y].wall = False
                    if myMap[x][y].chasm:
                        myMap[x][y].applyChasmProperties()
                    else:
                        myMap[x][y].applyGroundProperties(temple=temple)
                elif myMap[x][y].wall and not myMap[x][y].pillar:
                    myMap[x][y].applyWallProperties()
                elif myMap[x][y].chasm and not myMap[x][y].secretWall:
                    myMap[x][y].applyChasmProperties()
                    myMap[x][y].wall = False
                elif myMap[x][y].pillar:
                    myMap[x][y].baseBlocked = True
                    myMap[x][y].baseCharacter = 'o'
                    myMap[x][y].baseFg = color_light_wall
                    myMap[x][y].baseDark_fg = color_dark_wall
                elif not myMap[x][y].secretWall:
                    myMap[x][y].applyGroundProperties(temple=temple)
                    myMap[x][y].wall = False
    
    for x in range(MAP_WIDTH):
        myMap[x][0].setUnbreakable()
        myMap[x][MAP_HEIGHT - 1].setUnbreakable()
    for y in range(MAP_HEIGHT):
        myMap[0][y].setUnbreakable()
        myMap[MAP_WIDTH - 1][y].setUnbreakable()
            
            
def createHorizontalTunnel(x1, x2, y, big = False):
    global myMap, tunnelTiles
    for x in range(min(x1, x2), max(x1, x2) + 1):
        myMap[x][y].applyGroundProperties(temple=big)
        tunnelTiles.append((x, y))
    if big:
        for x in range(min(x1, x2) - 1, max(x1, x2) + 2):
            myMap[x][y + 1].applyGroundProperties(temple=big)
            tunnelTiles.append((x, y + 1))
            myMap[x][y - 1].applyGroundProperties(temple=big)
            tunnelTiles.append((x, y - 1))
            
def createVerticalTunnel(y1, y2, x, big = False):
    global myMap, tunnelTiles
    for y in range(min(y1, y2), max(y1, y2) + 1):
        myMap[x][y].applyGroundProperties(temple=big)
        tunnelTiles.append((x, y))
    if big:
        for y in range(min(y1, y2) - 1, max(y1, y2) + 2):
            myMap[x + 1][y].applyGroundProperties(temple=big)
            tunnelTiles.append((x + 1, y))
            myMap[x - 1][y].applyGroundProperties(temple=big)
            tunnelTiles.append((x - 1, y))

def secretRoomTest(startingX, endX, startingY, endY, width = 4):
    for x in range(startingX, endX):
        for y in range(startingY, endY):
            if not myMap[x][y].block_sight:
                if x >= width + 2 and x <= MAP_WIDTH - width + 2 and y >= width + 2 and y <= MAP_HEIGHT -width + 2:
                    if myMap[x + 1][y].wall: #right of the current tile
                        intersect = False
                        for indexX in range(width + 1):
                            for indexY in range(width + 1):
                                try:
                                    if not myMap[x + 1 + indexX][y - width//2 + indexY].wall:
                                        intersect = True
                                        break
                                except IndexError:
                                    intersect = True
                                    break
                        if not intersect:
                            print("right")
                            return x + 1, y - width//2, x + 1, y, 'right'
                    if myMap[x - 1][y].wall: #left
                        intersect = False
                        for indexX in range(width + 1):
                            for indexY in range(width + 1):
                                try:
                                    if not myMap[x - 1 - indexX][y - width//2 + indexY].wall:
                                        intersect = True
                                        break
                                except IndexError:
                                    intersect = True
                                    break
                        if not intersect:
                            print("left")
                            return x - (width + 1), y - width//2, x - 1, y, 'left'
                    if myMap[x][y + 1].wall: #under
                        intersect = False
                        for indexX in range(width + 1):
                            for indexY in range(width + 1):
                                try:
                                    if not myMap[x - width//2 + indexX][y + 1 + indexY].wall:
                                        intersect = True
                                        break
                                except IndexError:
                                    intersect = True
                                    break
                        if not intersect:
                            print("under")
                            return x - width//2, y + 1, x, y + 1, 'under'
                    if myMap[x][y - 1].wall: #above
                        intersect = False
                        for indexX in range(width + 1):
                            for indexY in range(width + 1):
                                try:
                                    if not myMap[x - width//2 + indexX][y - 1 - indexY].wall:
                                        intersect = True
                                        break
                                except IndexError:
                                    intersect = True
                                    break
                        if not intersect:
                            print("above")
                            return x - width//2, y - (width + 1), x, y - 1, 'above'

def secretRoom(temple):
    global myMap, unchasmable, noCheckTiles
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
    
    if temple:
        width = 8
    else:
        width = False
    x, y, entryX, entryY, side = secretRoomTest(minX, maxX, minY, maxY, width)
    if not (x == 'cancelled' or y == 'cancelled' or entryX == 'cancelled' or entryY == 'cancelled'):
        secretRoom = Rectangle(x, y, width, width)
        createRoom(secretRoom, pillar = temple)
        for X in range(secretRoom.x1, secretRoom.x2):
            for Y in range(secretRoom.y1, secretRoom.y2):
                unchasmable.append((X, Y))
                noCheckTiles.append((X, Y))
        myMap[entryX][entryY].baseBlocked = False
        myMap[entryX][entryY].block_sight = True
        myMap[entryX][entryY].baseCharacter = '#'
        myMap[entryX][entryY].baseFg = color_light_wall
        myMap[entryX][entryY].baseBg = color_light_ground
        myMap[entryX][entryY].baseDark_fg = color_dark_wall
        myMap[entryX][entryY].baseDark_bg = color_dark_ground
        myMap[entryX][entryY].secretWall = True
        myMap[entryX][entryY].wall = False
        if temple:
            for X in range(7):
                for Y in range(7):
                    if not myMap[x + 1 + X][y + 1 + Y].pillar:
                        myMap[x + 1 + X][y + 1 + Y].baseCharacter = '-'
                        myMap[x + 1 + X][y + 1 + Y].baseFg = colors.sepia
                        myMap[x + 1 + X][y + 1 + Y].baseDark_fg = colors.darker_sepia
                    else:
                        myMap[x + 1 + X][y + 1 + Y].baseFg = colors.darker_sepia
                        myMap[x + 1 + X][y + 1 + Y].baseDark_fg = colors.darkest_sepia
                    myMap[x + 1 + X][y + 1 + Y].baseBg = colors.light_sepia
                    myMap[x + 1 + X][y + 1 + Y].baseDark_bg = colors.dark_sepia
            
            if countNeighbours(myMap, x, y) == 7:
                myMap[x][y].baseCharacter = 'O'
                myMap[x][y].baseFg = colors.darker_sepia
                myMap[x][y].baseBg = colors.dark_sepia
                myMap[x][y].baseDark_fg = colors.darkest_sepia
                myMap[x][y].baseDark_bg = colors.darker_sepia
            if countNeighbours(myMap, x + 8, y) == 7:
                myMap[x + 8][y].baseCharacter = 'O'
                myMap[x + 8][y].baseFg = colors.darker_sepia
                myMap[x + 8][y].baseBg = colors.dark_sepia
                myMap[x + 8][y].baseDark_fg = colors.darkest_sepia
                myMap[x + 8][y].baseDark_bg = colors.darker_sepia
            if countNeighbours(myMap, x, y + 8) == 7:
                myMap[x][y + 8].baseCharacter = 'O'
                myMap[x][y + 8].baseFg = colors.darker_sepia
                myMap[x][y + 8].baseBg = colors.dark_sepia
                myMap[x][y + 8].baseDark_fg = colors.darkest_sepia
                myMap[x][y + 8].baseDark_bg = colors.darker_sepia
            if countNeighbours(myMap, x + 8, y + 8) == 7:
                myMap[x + 8][y + 8].baseCharacter = 'O'
                myMap[x + 8][y + 8].baseFg = colors.darker_sepia
                myMap[x + 8][y + 8].baseBg = colors.dark_sepia
                myMap[x + 8][y + 8].baseDark_fg = colors.darkest_sepia
                myMap[x + 8][y + 8].baseDark_bg = colors.darker_sepia
            
            if side != 'left':
                sideFalse = False
                for k in range(7):
                    if not 5 <= countNeighbours(myMap, x + 8, y + 1 + k) <= 6:
                        sideFalse = True
                if not sideFalse:
                    for k in range(7):
                        myMap[x + 8][y + 1 + k].baseCharacter = '='
                        myMap[x + 8][y + 1 + k].baseFg = colors.dark_sepia
                        myMap[x + 8][y + 1 + k].baseBg = colors.sepia
                        myMap[x + 8][y + 1 + k].baseDark_fg = colors.darkest_sepia
                        myMap[x + 8][y + 1 + k].baseDark_bg = colors.darker_sepia
            if side != 'right':
                sideFalse = False
                for k in range(7):
                    if not 5 <= countNeighbours(myMap, x, y + 1 + k) <= 6:
                        sideFalse = True
                if not sideFalse:
                    for k in range(7):
                        myMap[x][y + 1 + k].baseCharacter = '='
                        myMap[x][y + 1 + k].baseFg = colors.dark_sepia
                        myMap[x][y + 1 + k].baseBg = colors.sepia
                        myMap[x][y + 1 + k].baseDark_fg = colors.darkest_sepia
                        myMap[x][y + 1 + k].baseDark_bg = colors.darker_sepia
            if side != 'under':
                sideFalse = False
                for k in range(7):
                    if not 5 <= countNeighbours(myMap, x + 1 + k, y) <= 6:
                        sideFalse = True
                if not sideFalse:
                    for k in range(7):
                        myMap[x + 1 + k][y].baseCharacter = '='
                        myMap[x + 1 + k][y].baseFg = colors.dark_sepia
                        myMap[x + 1 + k][y].baseBg = colors.sepia
                        myMap[x + 1 + k][y].baseDark_fg = colors.darkest_sepia
                        myMap[x + 1 + k][y].baseDark_bg = colors.darker_sepia
            if side != 'above':
                sideFalse = False
                for k in range(7):
                    if not 5 <= countNeighbours(myMap, x + 1 + k, y + 8) <= 6:
                        sideFalse = True
                if not sideFalse:
                    for k in range(7):
                        myMap[x + 1 + k][y + 8].baseCharacter = '='
                        myMap[x + 1 + k][y + 8].baseFg = colors.dark_sepia
                        myMap[x + 1 + k][y + 8].baseBg = colors.sepia
                        myMap[x + 1 + k][y + 8].baseDark_fg = colors.darkest_sepia
                        myMap[x + 1 + k][y + 8].baseDark_bg = colors.darker_sepia
        print("created secret room at x ", entryX, " y ", entryY, " in quarter ", quarter)

def checkFile(file, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    os.chdir(folder)
    for f in os.listdir(folder):
        print(f)
        if f == file:
            return True
            break 
    return False

def removeAllChasms():
    '''
    For when they are truly making you lose your sanity and you want to erase all trace of the existence of every single of these fuckers because they are preventing you from testing what you want to test
    And then after hours of banging your head against the nearest wall you realize that chasms were never the cause of your problem. FML.
    '''
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            myMap[x][y].chasm = False

def checkTileClearance(mapToUse, x, y):
    foundBlocked = False
    clearance = -1
    while not foundBlocked and clearance <= 9:
        clearance += 1
        square = Square(x, y, clearance)
        if x + clearance < MAP_WIDTH and y + clearance < MAP_HEIGHT:
            for tile in square.tiles(mapToUse = mapToUse):
                if tile.blocked or tile.chasm:
                    foundBlocked = True
                    break
        else:
            foundBlocked = True
    return clearance

def clearanceMap(mapToUse):
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            mapToUse[x][y].clearance = checkTileClearance(mapToUse, x, y)
    return mapToUse

def makeMap(generateChasm = True, generateHole = False, fall = False, temple = False, genPlayer = True):
    global myMap, noCheckTiles, stairs, objects, upStairs, bossDungeonsAppeared, color_dark_wall, color_light_wall, color_dark_ground, color_light_ground, color_dark_gravel, color_light_gravel, townStairs, gluttonyStairs, stairs, upStairs, nemesisList, roomTiles, tunnelTiles, unchasmable, rooms, wrathStairs, maxRooms, roomMaxSize, roomMinSize, bossTiles
    regen = True
    while regen:
        regen = False
        nemesis = None
        
        found = checkFile('meta.bak', absMetaDirPath)
    
        if not found:
            file = shelve.open(absMetaPath, "c")
            print('found no nemesis file')
        else:
            print('found nemesis file')
            file = shelve.open(absMetaPath, "r")
            try:
                nemesisList = file['nemesis']
                for nemesis in nemesisList:
                    print(nemesis.branch, currentBranch.shortName)
                    print(nemesis.level, branchLevel)
                    if nemesis.branch == currentBranch.shortName and nemesis.level == branchLevel:
                        dice = randint(1, 100)
                        TARGET_CONSTANT = 5
                        target = round(TARGET_CONSTANT + (branchLevel * branchLevel) / 10)
                        print(dice, target)
                        if dice <= target:
                            break
                        nemesis = None
            except KeyError:
                print("========WARNING========")
                print('No nemesis in file')
                print("=======================")
        file.close()
        
        stairs = None
        upStairs = None
        gluttonyStairs = None
        townStairs = None
        wrathStairs = None
        bossTiles = None
        rooms = []
        roomTiles = []
        tunnelTiles = []
        unchasmable = []
        noCheckTiles = []
        numberRooms = 0
        objects = [player]
        
        myMap, rooms, roomsForStairs = mapGen.generateMap(currentBranch, branchLevel)
        '''    
        color_dark_wall = dBr.mainDungeon.mapGeneration['wallDarkFG']
        color_light_wall = dBr.mainDungeon.mapGeneration['wallFG']
        color_dark_ground = dBr.mainDungeon.mapGeneration['groundDarkBG']
        color_dark_gravel = dBr.mainDungeon.mapGeneration['gravelDarkFG']
        color_light_ground = dBr.mainDungeon.mapGeneration['groundBG']
        color_light_gravel = dBr.mainDungeon.mapGeneration['gravelFG']
        maxRooms = currentBranch.maxRooms
        roomMinSize = currentBranch.roomMinSize
        roomMaxSize = currentBranch.roomMaxSize
    
        myMap = [[Tile(True, x = x, y = y, wall = True, chasm = generateChasm, hole = generateHole) for y in range(MAP_HEIGHT)]for x in range(MAP_WIDTH)] #Creates a rectangle of blocking tiles from the Tile class, aka walls. Each tile is accessed by myMap[x][y], where x and y are the coordinates of the tile.
        #removeAllChasms()
        rooms = []
        roomTiles = []
        tunnelTiles = []
        unchasmable = []
        noCheckTiles = []
        numberRooms = 0
        objects = [player]
    
        for y in range(MAP_HEIGHT):
            myMap[0][y].unbreakable = True
            myMap[MAP_WIDTH-1][y].unbreakable = True
        for x in range(MAP_WIDTH):
            myMap[x][0].unbreakable = True
            myMap[x][MAP_HEIGHT-1].unbreakable = True #Borders of the map cannot be broken
     
        for r in range(maxRooms):
            w = randint(roomMinSize, roomMaxSize)
            h = randint(roomMinSize, roomMaxSize)
            x = randint(0, MAP_WIDTH-w-1)
            y = randint(0, MAP_HEIGHT-h-1)
            newRoom = Rectangle(x, y, w, h)
            intersection = False
            for otherRoom in rooms:
                if newRoom.intersect(otherRoom):
                    intersection = True
                    break
            if not intersection:
                createRoom(newRoom, pillar = temple)
                lastCreatedRoom = newRoom
                (new_x, new_y) = newRoom.center()
     
                if numberRooms == 0:
                    if not fall and genPlayer:
                        player.x = new_x
                        player.y = new_y
                    for x in range(newRoom.x1 + 1, newRoom.x2):
                        for y in range(newRoom.y1 + 1, newRoom.y2):
                            unchasmable.append((x, y))
                    if branchLevel > 1 or currentBranch.name != 'Main':
                        if branchLevel > 1:
                            formerBranch = currentBranch
                        elif currentBranch.name != 'Main':
                            formerBranch = currentBranch.origBranch
                        upStairs = GameObject(new_x, new_y, '<', 'stairs', currentBranch.lightStairsColor, alwaysVisible = True, darkColor = currentBranch.darkStairsColor, Stairs=Stairs(climb='up', branchesFrom=formerBranch, branchesTo=currentBranch))
                        objects.append(upStairs)
                        upStairs.sendToBack()
                else:
                    (previous_x, previous_y) = rooms[numberRooms-1].center()
                    bigTunnel = randint(0, 5)
                    big = bigTunnel == 0 or (bigTunnel <= 1 and temple)
                    if randint(0, 1):
                        createHorizontalTunnel(previous_x, new_x, previous_y, big)
                        createVerticalTunnel(previous_y, new_y, new_x, big)
                    else:
                        createVerticalTunnel(previous_y, new_y, previous_x, big)
                        createHorizontalTunnel(previous_x, new_x, new_y, big)
                rooms.append(newRoom)
                numberRooms += 1
        if temple:
            baseMap = list(deepcopy(myMap))
            for x in range(MAP_WIDTH):
                for y in range(MAP_HEIGHT):
                    if 0 <= countNeighbours(myMap, x, y) <= 2 and not myMap[x][y].pillar and not (x == 0 or x == MAP_WIDTH - 1 or y == 0 or y == MAP_HEIGHT - 1):
                        if myMap[x][y].blocked:
                            #baseMap[x][y].baseBg = colors.red
                            baseMap[x][y].wall = False
                            baseMap[x][y].baseBlocked = False
                            baseMap[x][y].baseCharacter = None
                    if countNeighbours(myMap, x, y) == 3 and not myMap[x][y].pillar and not (x == 0 or x == MAP_WIDTH - 1 or y == 0 or y == MAP_HEIGHT - 1):
                        if myMap[x][y].blocked:
                            baseMap[x][y].pillar = True
                            baseMap[x][y].baseBlocked = True
                            baseMap[x][y].baseCharacter = 'o'
            myMap = baseMap
        
        secretRoom(temple)
        stairs = GameObject(new_x, new_y, '>', 'stairs', currentBranch.lightStairsColor, alwaysVisible = True, darkColor = currentBranch.darkStairsColor, Stairs=Stairs('down', currentBranch, currentBranch))
        objects.append(stairs)
        stairs.sendToBack()
        for x in range(lastCreatedRoom.x1 + 1, lastCreatedRoom.x2):
            for y in range(lastCreatedRoom.y1 + 1, lastCreatedRoom.y2):
                unchasmable.append((x, y))
        print("BEFORE CHASM")
        
        #if generateChasm:
        #    myMap = chasmGen.createChasms(myMap, roomTiles, tunnelTiles, unchasmable)
        if generateHole:
            myMap = holeGen.createHoles(myMap)
        print("AFTER CHASM")
        checkMap(temple=temple)
        '''
        
        print("PREPING IDENTIFIYING")
        applyIdentification()
        print("DONE IDING")
        r = 0
        roomCounter = 0
        if genPlayer:
            for room in rooms:
                roomCounter += 1
                print("ROOMS LENGTH = {} AND SWE ARE AT THE {}TH TIME PLACING FREAKING OBJECTS".format(len(rooms), roomCounter))
                if r == 0:
                    placeObjects(room, True)
                else:
                    placeObjects(room)
        
        print("DONE ITEMS")
        
        if nemesis is not None:
            randRoom = randint(0, len(rooms) - 1)
            print("DONE NEM RAND")
            room = rooms[randRoom]
            print("DONE NEM ROOM")
            created = False
            counter = 0
            while not created and counter <= 25:
                counter += 1
                x = randint(room.x1 + 1, room.x2)
                y = randint(room.y1 + 1, room.y2)
                if not (isBlocked(x, y) or myMap[x][y].chasm):
                    created = True
            if created:
                print("DONE NEM COORDS")
                nemesisMonster = nemesis.nemesisObject
                print("DONE NEM")
                nemesisMonster.x = x
                nemesisMonster.y = y
                print("DONE NEM POS")
                objects.append(nemesisMonster)
                print('created nemesis', nemesisMonster.name, x, y)
        
        print("DONE NEMESIS")
        
        branches = []
        stairsRooms = []
        placedPlayer = False
        for room, branch, way in roomsForStairs:
            x, y = room.center()
            if way == 'down':
                char = '>'
                text = 'stairs to '
            else:
                player.x, player.y = x, y
                placedPlayer = True
                char = '<'
                text = 'stairs from '
            if branch.name == 'The Shrine' and way == 'down':
                changeBranchLevel = 5
            else:
                changeBranchLevel = None
            newStairs = GameObject(x, y, char, text + branch.name, branch.mapGeneration['stairsColor'], alwaysVisible = True, darkColor = branch.mapGeneration['stairsDarkColor'], Stairs=Stairs(way, currentBranch, branch, changeBranchLevel))
            objects.append(newStairs)
            newStairs.sendToBack()
            branch.appeared = True
            branches.append(branch)
            stairsRooms.append(room)
        
        while not placedPlayer:
            randRoom = rooms[randint(0, len(rooms)-1)]
            if not randRoom in stairsRooms:
                x, y = randRoom.center()
                if not myMap[x][y].blocked and not myMap[x][y].chasm:
                    player.x, player.y = x, y
                    placedPlayer = True
        '''
        branches = []
        for (branch, level) in currentBranch.branchesTo:
            print("IN BRANCH LEVEL LOOP")
            branches.append(branch)
            if branchLevel == level and not branch.appeared:
                createdStairs = False
                stairsCounter = 0
                while not createdStairs:
                    stairsCounter += 1
                    if stairsCounter > REGEN_THRESHOLD:
                        regen = True
                        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                        print("SET REGEN TO TRUE !!!!!!!!!!!!")
                        print("SEE MESSAGE ABOVE")
                        print("IMPORTANT NOTICE ABOVE")
                        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                        break
                    randRoom = randint(0, len(rooms) - 1)
                    room = rooms[randRoom]
                    chasmedRoom = False
                    '''
                    #for x in range(room.x1 + 1, room.x2):
                    #    for y in range(room.y1 + 1, room.y2):
                    #        if myMap[x][y].chasm:
                    #            chasmedRoom = True
                    #            break
                    #    if chasmedRoom:
                    #        break
        '''
                    (x, y) = room.center()
                    wrongCentre = False
                    if genPlayer:
                        for object in objects:
                            if object.x == x and object.y == y:
                                wrongCentre = True
                                break
                    if not wrongCentre and not chasmedRoom and not myMap[x][y].chasm:
                        newStairs = GameObject(x, y, '>', 'stairs to ' + branch.name, branch.mapGeneration['stairsColor'], alwaysVisible = True, darkColor = branch.mapGeneration['stairsDarkColor'], Stairs=Stairs('down', currentBranch, branch))
                        player.x, player.y = x, y #TEMPORARY, TO-DO: add smart stairs placement
                        objects.append(newStairs)
                        newStairs.sendToBack()
                        branch.appeared = True
                        createdStairs = True
                        print('created {} stairs at {}, {}'.format(branch.shortName, str(x), str(y)))
        '''        
        '''
            if branch == dBr.gluttonyDungeon:
                if branchLevel == level and not bossDungeonsAppeared['gluttony']:
                    createdStairs = False
                    while not createdStairs:
                        randRoom = randint(0, len(rooms) - 1)
                        room = rooms[randRoom]
                        chasmedRoom = False
                        for x in range(room.x1 + 1, room.x2):
                            for y in range(room.y1 + 1, room.y2):
                                if myMap[x][y].chasm:
                                    chasmedRoom = True
                                    break
                            if chasmedRoom:
                                break
                        (x, y) = room.center()
                        wrongCentre = False
                        for object in objects:
                            if object.x == x and object.y == y:
                                wrongCentre = True
                                break
                        if not wrongCentre and not chasmedRoom:
                            global gluttonyStairs
                            gluttonyStairs = GameObject(x, y, '>', 'stairs to Gluttony', branch.lightStairsColor, alwaysVisible = True, darkColor = branch.darkStairsColor)
                            objects.append(gluttonyStairs)
                            gluttonyStairs.sendToBack()
                            bossDungeonsAppeared['gluttony'] = True
                            createdStairs = True
                            print('created gluttonys stairs at ' + str(x) + ', ' + str(y))
            elif branch == dBr.greedDungeon:
                if branchLevel == level and not bossDungeonsAppeared['greed']:
                    createdStairs = False
                    while not createdStairs:
                        randRoom = randint(0, len(rooms) - 1)
                        room = rooms[randRoom]
                        chasmedRoom = False
                        for x in range(room.x1 + 1, room.x2):
                            for y in range(room.y1 + 1, room.y2):
                                if myMap[x][y].chasm:
                                    chasmedRoom = True
                                    break
                            if chasmedRoom:
                                break
                        (x, y) = room.center()
                        wrongCentre = False
                        for object in objects:
                            if object.x == x and object.y == y:
                                wrongCentre = True
                                break
                        if not wrongCentre and not chasmedRoom:
                            global greedStairs
                            greedStairs = GameObject(x, y, '>', 'stairs to Greed', branch.lightStairsColor, alwaysVisible = True, darkColor = branch.darkStairsColor)
                            objects.append(greedStairs)
                            greedStairs.sendToBack()
                            bossDungeonsAppeared['greed'] = True
                            createdStairs = True
                            print('created greeds stairs at ' + str(x) + ', ' + str(y))
                else:
                    global greedStairs
                    print('No greed stairs on this level')
                    greedStairs = None
            elif branch == dBr.hiddenTown:
                if branchLevel == level:
                    createdStairs = False
                    while not createdStairs:
                        randRoom = randint(0, len(rooms) - 1)
                        room = rooms[randRoom]
                        chasmedRoom = False
                        for x in range(room.x1 + 1, room.x2):
                            for y in range(room.y1 + 1, room.y2):
                                if myMap[x][y].chasm:
                                    chasmedRoom = True
                                    break
                            if chasmedRoom:
                                break
                        wrongCentre = False
                        for object in objects:
                            if object.x == x and object.y == y:
                                wrongCentre = True
                                break
                        (x, y) = room.center()
                        if not wrongCentre and not chasmedRoom:
                            global townStairs
                            townStairs = GameObject(x, y, '>', 'glowing portal', branch.lightStairsColor, alwaysVisible = True, darkColor = branch.darkStairsColor)
                            objects.append(townStairs)
                            gluttonyStairs.sendToBack()
                            createdStairs = True
                            print('created hidden town stairs at ' + str(x) + ', ' + str(y))
                else:
                    global townStairs
                    print('No town stairs on this level')
                    townStairs = None
            elif branch == dBr.wrathDungeon:
                if branchLevel == level and not bossDungeonsAppeared['wrath']:
                    createdStairs = False
                    while not createdStairs:
                        randRoom = randint(0, len(rooms) - 1)
                        room = rooms[randRoom]
                        chasmedRoom = False
                        for x in range(room.x1 + 1, room.x2):
                            for y in range(room.y1 + 1, room.y2):
                                if myMap[x][y].chasm:
                                    chasmedRoom = True
                                    break
                            if chasmedRoom:
                                break
                        (x, y) = room.center()
                        wrongCentre = False
                        for object in objects:
                            if object.x == x and object.y == y:
                                wrongCentre = True
                                break
                        if not wrongCentre and not chasmedRoom:
                            global wrathStairs
                            wrathStairs = GameObject(x, y, '>', 'stairs to Wrath', branch.lightStairsColor, alwaysVisible = True, darkColor = branch.darkStairsColor)
                            objects.append(wrathStairs)
                            wrathStairs.sendToBack()
                            bossDungeonsAppeared['wrath'] = True
                            createdStairs = True
                            print('created wraths stairs at ' + str(x) + ', ' + str(y))
            '''
        if not regen:
            if not dBr.hiddenTown in branches:
                print('Wrong branch for town stairs')
                townStairs = None
            if not dBr.gluttonyDungeon in branches:
                print('Wrong branch for gluttony stairs')
                gluttonyStairs = None
            if not dBr.wrathDungeon in branches:
                print('Wrong branch for wrath stairs')
                wrathStairs = None
            
            if fall:
                fallen = False
                while not fallen:
                    x, y = randint(1, MAP_WIDTH - 1), randint(1, MAP_HEIGHT - 1)
                    if not myMap[x][y].chasm and not isBlocked(x, y):
                        player.x, player.y = x, y
                        fallen = True
            updateTileCoords()
            myMap = clearanceMap(myMap)
        else:
            print("Regenerating map...")

def closeAndMakeWall(x, y, mapToUse, unbreakable):
    closeTile(x,y, mapToUse, unbreakable)
    mapToUse[x][y].applyWallProperties()

def makeBossLevel(fall = False, generateHole=False, temple = False):
    '''
    Creates boss level
    Function alias (for search function, because Edern (me) always types in makeBossRoom instead of makeBossLevel) : def makeBossRoom
    '''
    global myMap, objects, upStairs, rooms, numberRooms, bossTiles
    myMap = [[Tile(True, x = x, y = y, wall = True, hole = generateHole) for y in range(MAP_HEIGHT)]for x in range(MAP_WIDTH)] #Creates a rectangle of blocking tiles from the Tile class, aka walls. Each tile is accessed by myMap[x][y], where x and y are the coordinates of the tile.
    objects = [player]
    rooms = []
    numberRooms = 0
    
    for y in range(MAP_HEIGHT):
        myMap[0][y].unbreakable = True
        myMap[MAP_WIDTH-1][y].unbreakable = True
    for x in range(MAP_WIDTH):
        myMap[x][0].unbreakable = True
        myMap[x][MAP_HEIGHT-1].unbreakable = True #Borders of the map cannot be broken
 
    for r in range(5): #first rooms
        w = randint(roomMinSize, roomMaxSize)
        h = randint(roomMinSize, roomMaxSize)
        x = randint(0, 50-w-1)
        y = randint(0, 20-h-1)
        newRoom = Rectangle(x, y, w, h)
        intersection = False
        for otherRoom in rooms:
            if newRoom.intersect(otherRoom):
                intersection = True
                break
        if not intersection:
            createRoom(newRoom, pillar=temple)
            (new_x, new_y) = newRoom.center()
            (previous_x, previous_y) = newRoom.center()
 
            if numberRooms == 0:
                if not fall:
                    player.x = new_x
                    player.y = new_y
                if branchLevel > 1:
                    upStairs = GameObject(new_x, new_y, '<', 'stairs', currentBranch.mapGeneration['stairsColor'], alwaysVisible = True, darkColor = currentBranch.mapGeneration['stairsDarkColor'], Stairs = Stairs(climb='up', branchesFrom=currentBranch, branchesTo=currentBranch))
                    objects.append(upStairs)
                    upStairs.sendToBack()
            else:
                (previous_x, previous_y) = rooms[numberRooms-1].center()
                bigTunnel = randint(0, 4)
                big = bigTunnel == 0 and temple
                if randint(0, 1):
                    createHorizontalTunnel(previous_x, new_x, previous_y, big)
                    createVerticalTunnel(previous_y, new_y, new_x, big)
                else:
                    createVerticalTunnel(previous_y, new_y, previous_x, big)
                    createHorizontalTunnel(previous_x, new_x, new_y, big)
            rooms.append(newRoom)
            numberRooms += 1

    #boss room
    w = randint(25, 40)
    h = randint(20, 35)
    x = randint(50, 100-w-1)
    y = randint(20, 60-h-1)
    bossRoom = Rectangle(x, y, w, h)
    createRoom(bossRoom, pillar=temple)
    bossTiles = bossRoom.tiles
    print(bossTiles)
    
    refreshEmptyTiles()
    for tile in emptyTiles:
        (x,y) = tile
        print("EMPTY : {};{}".format(x, y))
    copyBoss = list(emptyTiles)
    entrance = []
    startTile = bossTiles[4]
    sX, sY = startTile.x, startTile.y
    
    (new_x, new_y) = bossRoom.center()
    bigTunnel = randint(0, 4)
    big = bigTunnel == 0 and temple
    createVerticalTunnel(previous_y, new_y, previous_x, big)   
    createHorizontalTunnel(previous_x, new_x, new_y, big)      
    levels = currentBranch.bossNames.values()
    names = list(currentBranch.bossNames.keys())
    

            
    index = 0                                             
    for level in levels:                                  
        if level == branchLevel:                         
            bossName = names[index]                       
            break
        index += 1

    placeBoss(bossName, new_x, new_y)
    
    (previous_x, previous_y) = bossRoom.center()
    rooms.append(bossRoom)
    numberRooms += 1
    if temple:
        baseMap = list(deepcopy(myMap))
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                '''
                if countNeighbours(myMap, x, y) == 7:
                    myMap[x][y].pillar = True
                    myMap[x][y].baseCharacter = 'O'
                '''
                if 0 <= countNeighbours(myMap, x, y) <= 2 and not myMap[x][y].pillar and not (x == 0 or x == MAP_WIDTH - 1 or y == 0 or y == MAP_HEIGHT - 1):
                    if myMap[x][y].blocked:
                        #baseMap[x][y].baseBg = colors.red
                        baseMap[x][y].wall = False
                        baseMap[x][y].baseBlocked = False
                        baseMap[x][y].baseCharacter = None
                if countNeighbours(myMap, x, y) == 3 and not myMap[x][y].pillar and not (x == 0 or x == MAP_WIDTH - 1 or y == 0 or y == MAP_HEIGHT - 1):
                    if myMap[x][y].blocked:
                        baseMap[x][y].pillar = True
                        baseMap[x][y].baseBlocked = True
                        baseMap[x][y].baseCharacter = 'o'
        myMap = baseMap
    if generateHole:
        myMap = holeGen.createHoles(myMap)
    checkMap()
    myMap = clearanceMap(myMap)
        
    '''
    for tile in bossTiles: #Makes the boss room look FABULOUS for testing purposes
        assert isinstance(tile, Tile)
        tile.baseBg = colors.pink
        tile.BG = colors.pink
        tile.baseDark_bg = colors.fuchsia
        tile.DARK_BG = colors.fuchsia
    '''
    
    bossFFWrapper(sX, sY, entrance, copyBoss) #PSA : It works better if you place it AFTER you create the entrance (because this function is supposed to find the entrance). I may or may not have spent one hour before figuring that out.
    for loop in range(len(entrance)):
        if loop > 0:
            if (entrance[loop].x, entrance[loop].y) == (entrance[loop - 1].x, entrance[loop - 1].y):
                print("Removed duplicated tile")
                entrance.remove(entrance[loop])
    print(entrance)
    if len(entrance) > 1:
        for tile in entrance:
            print("ERROR :")
            print(tile.x, tile.y, sep = ";")
        raise ValueError("Entrance list is {} long instead of 1".format(len(entrance)))
    else:
        global bossEntrance
        for tilE in entrance:
            print("{};{}".format(tilE.x, tilE.y))
        
        bossEntrance = entrance[0]
        #for bossEntrance in entrance:
        '''
        bossEntrance.baseCharacter = 'X'
        bossEntrance.baseFg = colors.blue
        bossEntrance.FG = colors.blue
        bossEntrance.baseBg = colors.light_pink
        bossEntrance.BG = colors.light_pink
        bossEntrance.baseDark_bg = colors.light_pink
        bossEntrance.DARK_BG = colors.light_pink
        '''
        
        for otherTile in bossEntrance.neighbors(myMap):
            if otherTile in bossTiles and not otherTile.blocked:
                try:
                    assert isinstance(otherTile, Tile)
                except:
                    pass #Cause loading shenanigans. 
                '''
                otherTile.baseCharacter = 1
                otherTile.baseBg = colors.amber
                otherTile.baseFg = colors.green
                '''
                otherTile.onTriggerFunction = lambda tile : closeAndMakeWall(bossEntrance.x, bossEntrance.y, myMap, True)
    
    
    '''        
    for stuff in visuBoss:
        stuff.baseBg = colors.light_yellow
        stuff.BG = colors.light_yellow
        stuff.baseDark_bg = colors.light_yellow
        stuff.DARK_BG = colors.light_yellow
    '''
    
    if fall:
        fallen = False
        while not fallen:
            x, y = randint(1, MAP_WIDTH - 1), randint(1, MAP_HEIGHT - 1)
            if not myMap[x][y].chasm and not isBlocked(x, y):
                player.x, player.y = x, y
                fallen = True

tutoGateOpen = False


def makeTutorialMap(level = 1):
    global myMap, objects
    def openTutorialGate(tile, startX, startY, endY, char = None, text = 'The gate opens!', endX = -1):
        global tutoGateOpen, myMap, objects
        if endX < 0:
            endX = startX + 1
        if not tutoGateOpen:
            tutoGateOpen = True
            message(text)
            for x in range(startX, endX):
                for y in range(startY, endY):
                    myMap[x][y].baseCharacter = char
                    myMap[x][y].baseBlocked = False
                    myMap[x][y].block_sight = False
        print('gate open:', tutoGateOpen)

    def closeTutorialGate(tile, startX, startY, endY, char = '/', blockLOS = True, text = 'The gate closes back!', endX = -1):
        global tutoGateOpen, myMap, objects
        if endX < 0:
            endX = startX + 1
        if tutoGateOpen:
            tutoGateOpen = False
            message(text)
            for x in range(startX, endX):
                for y in range(startY, endY):
                    myMap[x][y].baseCharacter = char
                    myMap[x][y].baseBlocked = True
                    myMap[x][y].block_sight = blockLOS
        print('gate open:', tutoGateOpen)
    
    def loadTutoLevel(tile, level):
        global myMap, objects, player
        makeTutorialMap(level)
    
    def removeItems(tile):
        global inventory, equipmentList
        inventory = []
        equipmentList = []
        message('The barrier fizzles. You notice all your equipment has vanished!', colors.light_han)
    
    class TutoLevel:
        def __init__(self, level = 1):
            self.level = level
            self.shortName = str(level)
    
    class TutoStairs(Stairs):
        def __init__(self, climb, branchesFrom, branchesTo):
            actualBranchesTo = TutoLevel(branchesTo)
            Stairs.__init__(self, climb, branchesFrom, actualBranchesTo)
        
        def climbStairs(self):
            makeTutorialMap(self.branchesTo.level)

    if level == 1:
        myMap, objectsToCreate = layoutReader.readMap('tutoFloorOne')
        for y in range(MID_MAP_HEIGHT - 3, MID_MAP_HEIGHT + 4):
            myMap[25][y].onTriggerFunction = lambda tile: closeTutorialGate(tile, 26, MID_MAP_HEIGHT - 3, MID_MAP_HEIGHT + 4)
            myMap[27][y].onTriggerFunction = lambda tile: openTutorialGate(tile, 26, MID_MAP_HEIGHT - 3, MID_MAP_HEIGHT + 4)
            myMap[11][y].onTriggerFunction = lambda tile: closeTutorialGate(tile, 12, MID_MAP_HEIGHT - 3, MID_MAP_HEIGHT + 4)
            myMap[13][y].onTriggerFunction = lambda tile: openTutorialGate(tile, 12, MID_MAP_HEIGHT - 3, MID_MAP_HEIGHT + 4)
        for y in range(MID_MAP_HEIGHT - 2, MID_MAP_HEIGHT + 3):
            myMap[0][y].baseBlocked = False
            myMap[0][y].onTriggerFunction = lambda tile: loadTutoLevel(tile, 2)
        for y in range(26, 34):
            myMap[58][y].onTriggerFunction = lambda tile: closeTutorialGate(tile, 59, 27, 33, chr(207), False, 'The magic barrier closes back behind you!', 61)
            myMap[61][y].onTriggerFunction = lambda tile: openTutorialGate(tile, 59, 27, 33, text = 'The magic barrier opens in front of you with a slight humming!', endX = 61)
            myMap[60][y].onTriggerFunction = removeItems
        for y in range(28, 33):
            myMap[95][y].onTriggerFunction = lambda tile: closeTutorialGate(tile, 96, 28, 33, chr(92), False)
            myMap[97][y].onTriggerFunction = lambda tile: openTutorialGate(tile, 96, 28, 33, '.')
        
        helmetComp = Equipment(slot = 'head', type = 'light armor', armorBonus=2, meleeWeapon=False)
        helmet = GameObject(0, 0, '[', 'helmet', colors.silver, Equipment=helmetComp, Item=Item(weight=2.0, pic = 'darksoulHelmet.xp', useText='Equip'))
        fighterComp = Fighter(hp = 20, armor = 0, power = 3, accuracy = 60, evasion = 15, xp = 350, deathFunction=monsterDeath, lootFunction= [helmet], lootRate=[100], toEquip=[helmet], description = "One of Zarg's fighters, he seems to be guarding the entrance to the tower.")
        guard = GameObject(27, MID_MAP_HEIGHT, 'g', 'guard', colors.darker_han, blocks = True, Fighter=fighterComp, AI=BasicMonster(wanderer=False))
        
        halberdComp = Equipment(slot = 'two handed', type = 'heavy weapon', powerBonus=4, meleeWeapon=True)
        halberd = GameObject(0, 0, '/', 'halberd', colors.silver, Equipment=halberdComp, Item=Item(weight=12.0, pic = 'darksoulHelmet.xp', useText='Equip'))
        fighterComp = Fighter(hp = 20, armor = 0, power = 3, accuracy = 60, evasion = 15, xp = 350, deathFunction=monsterDeath, lootFunction= [halberd], lootRate=[100], toEquip=[halberd], description = "One of Zarg's fighters, he seems to be guarding the entrance to the tower.")
        guard2 = GameObject(20, 34, 'g', 'guard', colors.darker_han, blocks = True, Fighter=fighterComp, AI=BasicMonster(wanderer=False))

        potion = GameObject(20, 24, chr(173), 'healing potion', colors.red, Item = Item(useFunction = lambda: castHeal(player.Fighter.maxHP), weight = 0.4, stackable=True, amount = 2, pic = 'redPotion.xp', description = "A potion that stimulates cell growth when ingested, which allows for wounds to heal signifcantly faster. However, it also notably increases risk of cancer, but if you're in a situation where you have to drink such a potion, this is probably one of the least of your worries.", identified=True, useText = 'Drink'), blocks = False)
        potion2 = GameObject(21, 26, chr(173), 'healing potion', colors.red, Item = Item(useFunction = lambda: castHeal(player.Fighter.maxHP), weight = 0.4, stackable=True, amount = 2, pic = 'redPotion.xp', description = "A potion that stimulates cell growth when ingested, which allows for wounds to heal signifcantly faster. However, it also notably increases risk of cancer, but if you're in a situation where you have to drink such a potion, this is probably one of the least of your worries.", identified=True, useText = 'Drink'), blocks = False)
        bread = GameObject(17, 34, ',', "slice of bread", colors.yellow, Item = Item(useFunction=satiateHunger, arg1 = 200, arg2 = "a slice of bread", weight = 0.2, stackable=True, amount = 5, description = "This has probably been lying on the ground for ages, but you'll have to deal with it if you don't want to starve.", itemtype = 'food', useText = 'Eat'), blocks = False, pName = "slices of bread") 
        
        objects = [player, guard, potion, potion2, bread, guard2]
        for attributeList in objectsToCreate:
            object = createNPCFromMapReader(attributeList)
            objects.append(object)
        
    elif level == 2:
        myMap, objectsToCreate = layoutReader.readMap('tutoFloorTwo')
        for y in range(MID_MAP_HEIGHT - 3, MID_MAP_HEIGHT + 4):
            myMap[109][y].onTriggerFunction = lambda tile: closeTutorialGate(tile, 110, MID_MAP_HEIGHT - 3, MID_MAP_HEIGHT + 4)
            myMap[111][y].onTriggerFunction = lambda tile: openTutorialGate(tile, 110, MID_MAP_HEIGHT - 3, MID_MAP_HEIGHT + 4)
        
        swordComponent = Equipment(slot='one handed', type = 'light weapon', powerBonus = 10, meleeWeapon=True)
        sword = GameObject(121, 44, '-', 'longsword', colors.light_sky, Equipment = swordComponent, Item = Item(weight=3.5, pic = 'longSword.xp', useText='Equip'))
        
        shieldComp = Equipment(slot = 'one handed', type = 'shield', armorBonus=3, meleeWeapon=False)
        shield = GameObject(0, 0, '[', 'shield', colors.darker_orange, Equipment=shieldComp, Item=Item(weight=5.0, pic = 'shield.xp', useText='Equip'))
        fighterComp = Fighter(hp = 20, armor = 0, power = 6, accuracy = 60, evasion = 15, xp = 350, deathFunction=monsterDeath, lootFunction= [shield], lootRate=[100], toEquip=[shield], description = "One of Zarg's fighters, he seems to be guarding the entrance to the tower.")
        guard = GameObject(115, 26, 'g', 'guard', colors.darker_han, blocks = True, Fighter=fighterComp, AI=BasicMonster(wanderer=False))
        
        equipmentComponent = Equipment(slot = 'two handed', type = 'missile weapon', powerBonus = 1, ranged = True, rangedPower = 7, maxRange = SIGHT_RADIUS, ammo = 'arrow')
        bow = GameObject(0, 0, ')', 'shortbow', colors.light_orange, Equipment = equipmentComponent, Item = Item(weight = 1.0, pic = 'bow.xp'))
        itemComponent = Item(stackable = True, amount = 30)
        arrows = GameObject(0, 0, '^', 'arrow', colors.light_orange, Item = itemComponent)
        shooterComp = RangedNPC(shotRange = 10, power = 6, accuracy = 60)
        fighterComp = Fighter(hp = 20, armor = 0, power = 6, accuracy = 60, evasion = 15, xp = 350, deathFunction=monsterDeath, lootFunction = [bow, arrows], lootRate = [100, 100], description = "One of Zarg's fighters, he seems to be guarding the entrance to the tower. He is equipped with a bow.", Ranged=shooterComp)
        guard2 = GameObject(115, 34, 'g', 'guard', colors.darker_han, blocks = True, Fighter=fighterComp, AI=Shooter(wanderer=False))
        
        mobFireball = Spell(ressourceCost = 0, cooldown = 10, useFunction = castFireball, name = "Fireball", ressource = 'MP', type = 'Magic', magicLevel = 1, arg1 = 3, arg2 = 10, arg3 = 10)
        spellbook = GameObject(0, 0, '=', 'spellbook of fireball', colors.darker_han, Item = Item(useFunction = learnSpell, arg1 = fireball, weight = 1.0, pic = 'spellbook.xp', description='The reading of this book will learn you how to cast mighty fireballs.', useText='Read'), blocks = False)
        fighterComponent = Fighter(hp = 30, armor = 1, power = 5, xp = 350, deathFunction = monsterDeath, accuracy = 25, evasion = 40, maxMP = 30, knownSpells=[mobFireball], description = "One of Zarg's mages.", lootFunction=[spellbook], lootRate=[100])
        mage = GameObject(MID_MAP_WIDTH, MID_MAP_HEIGHT, 'm', 'mage', colors.darker_han, blocks = True, Fighter=fighterComponent, AI=Spellcaster(wanderer=False, meleeFighter=False))
        
        upStairs = GameObject(6, 11, '<', 'stairs', colors.light_grey, alwaysVisible = True, darkColor = colors.dark_grey, Stairs = TutoStairs(climb='up', branchesFrom=2, branchesTo=3))
        
        halberdComp = Equipment(slot = 'two handed', type = 'heavy weapon', powerBonus=4, meleeWeapon=True)
        halberd = GameObject(0, 0, '/', 'halberd', colors.silver, Equipment=halberdComp, Item=Item(weight=12.0, pic = 'darksoulHelmet.xp', useText='Equip'))
        fighterComp = Fighter(hp = 20, armor = 0, power = 3, accuracy = 60, evasion = 15, xp = 350, deathFunction=monsterDeath, lootFunction= [halberd], lootRate=[100], toEquip=[halberd], description = "One of Zarg's fighters, he seems to be guarding the entrance to the tower.")
        guard3 = GameObject(10, 11, 'g', 'guard', colors.darker_han, blocks = True, Fighter=fighterComp, AI=BasicMonster(wanderer=False))
        
        objects = [player, sword, guard, guard2, upStairs, mage, guard3]
        player.x = MAP_WIDTH - 2
        for attributeList in objectsToCreate:
            object = createNPCFromMapReader(attributeList)
            objects.append(object)
    
    elif level == 3:
        myMap, objectsToCreate = layoutReader.readMap('tutoFloorThree')
        zarg = GameObject(33, 54, 'Z', 'Zarg', colors.darkest_violet, blocks = True)
        objects = [player, zarg]

def createEndRooms():
    global rooms, stairs, myMap, objects, numberRooms
    newRooms = []
    for r in range(4): #final rooms
        w = randint(roomMinSize, roomMaxSize)
        h = randint(roomMinSize, roomMaxSize)
        x = randint(100, MAP_WIDTH-w-1)
        y = randint(0, MAP_HEIGHT-h-1)
        newRoom = Rectangle(x, y, w, h)
        intersection = False
        for otherRoom in rooms:
            if newRoom.intersect(otherRoom):
                intersection = True
                break
        if not intersection:
            createRoom(newRoom)
            newRooms.append(newRoom)
            (new_x, new_y) = newRoom.center()
            (previous_x, previous_y) = rooms[numberRooms-1].center()
            if randint(0, 1):
                createHorizontalTunnel(previous_x, new_x, previous_y)
                createVerticalTunnel(previous_y, new_y, new_x)
            else:
                createVerticalTunnel(previous_y, new_y, previous_x)
                createHorizontalTunnel(previous_x, new_x, new_y)
            rooms.append(newRoom)
            numberRooms += 1
    
    branchList, origBranch = dBr.getFloorBranches(currentBranch, branchLevel)
    for i, branch in enumerate(branchList):
        x, y = newRooms[i].center()
        GameObject(new_x, new_y, '<', 'stairs', branch.mapGeneration['stairsColor'], alwaysVisible = True, darkColor = branch.mapGeneration['stairsDarkColor'], Stairs = Stairs(climb='up', branchesFrom=currentBranch, branchesTo=branch))

def makeHiddenTown(fall = False):
    global myMap, objects, upStairs, rooms, numberRooms, bossRoom
    '''
    myMap = [[Tile(True, wall = True, x = x, y = y) for y in range(MAP_HEIGHT)]for x in range(MAP_WIDTH)] #Creates a rectangle of blocking tiles from the Tile class, aka walls. Each tile is accessed by myMap[x][y], where x and y are the coordinates of the tile.
    objects = [player]
    rooms = []
    bossRoom = None
    numberRooms = 0
    
    for y in range(MAP_HEIGHT):
        myMap[0][y].unbreakable = True
        myMap[MAP_WIDTH-1][y].unbreakable = True
    for x in range(MAP_WIDTH):
        myMap[x][0].unbreakable = True
        myMap[x][MAP_HEIGHT-1].unbreakable = True #Borders of the map cannot be broken
    
    newRoom = Rectangle(10, 10, 20, 10)
    createRoom(newRoom)
    x, y = newRoom.center()
    if not fall:
        player.x, player.y = x, y
    else:
        fallen = False
        while not fallen:
            x, y = randint(1, MAP_WIDTH - 1), randint(1, MAP_HEIGHT - 1)
            if not myMap[x][y].chasm and not isBlocked(x, y):
                player.x, player.y = x, y
                fallen = True
    upStairs = GameObject(x, y, '<', 'stairs', currentBranch.lightStairsColor, alwaysVisible = True, darkColor = currentBranch.darkStairsColor, Stairs = Stairs(climb='up', branchesFrom=dBr.mainDungeon, branchesTo=dBr.hiddenTown))
    objects.append(upStairs)
    upStairs.sendToBack()
    
    pukil = GameObject(25, 15, '@', 'Pukil the Debugger', colors.purple, blocks = True, socialComp = dial.pukTree)
    ayeth = GameObject(25, 13, '@', 'Ayeth the Merchant', colors.pink, blocks = True, socialComp = dial.ayeTree, shopComp = ayethShop)
    objects.append(pukil)
    objects.append(ayeth)
    
    #Code above this must go at the end of the makeHiddenTown() function, no matter what kinds of additions you make to it
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if myMap[x][y].blocked:
                myMap[x][y].unbreakable = True #We make so we cannot destruct town walls.
    
    if not player.Player.hasDiscoveredTown:
        player.Player.hasDiscoveredTown = True
        message("You feel the walls of this place emanating a strong magical aura.")


    '''
    rooms = []
    bossRoom = None
    numberRooms = 0
    player.x = 10
    player.y = 26
    myMap, objectsToCreate = layoutReader.readMap("tempHiddenTown6")
    objects = [player]
    for attributeList in objectsToCreate:
        object = createNPCFromMapReader(attributeList)
        objects.append(object)
    upStairs = GameObject(10, 26, '<', 'stairs', currentBranch.mapGeneration['stairsColor'], alwaysVisible = True, darkColor = currentBranch.mapGeneration['stairsDarkColor'], Stairs=Stairs(climb='up', branchesFrom=dBr.hiddenTown, branchesTo=dBr.mainDungeon))
    objects.append(upStairs)
    upStairs.sendToBack()
    '''
    bigFighter = Fighter(hp = 50, armor = 0, power = 0, accuracy=0, evasion=0, xp=0, deathFunction=monsterDeath)
    bigThing = GameObject(MID_MAP_WIDTH, MID_MAP_HEIGHT, chr(179), 'The Big Fat Stuff', color = colors.blue, blocks = True, Fighter = bigFighter, AI = BasicMonster(), size = 3, sizeChar=[chr(179), chr(192), None, chr(179), '^', chr(179), chr(179), chr(217)], smallChar = 'W')
    objects.append(bigThing)
    
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            myMap[x][y].unbreakable = True
    myMap = clearanceMap(myMap)
    '''

def makeShrineMap():
    global myMap, objects, upStairs, rooms, numberRooms, bossRoom
    rooms = []
    bossRoom = None
    numberRooms = 0
    player.x = 69
    player.y = 11
    myMap, objectsToCreate = layoutReader.readMap("shrine")
    objects = [player]
    for attributeList in objectsToCreate:
        object = createNPCFromMapReader(attributeList)
        objects.append(object)
    upStairs = GameObject(69, 11, '<', 'stairs', currentBranch.mapGeneration['stairsColor'], alwaysVisible = True, darkColor = currentBranch.mapGeneration['stairsDarkColor'], Stairs=Stairs(climb='up', branchesFrom=dBr.temple, branchesTo=dBr.shrine))
    objects.append(upStairs)
    upStairs.sendToBack()
    
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            myMap[x][y].unbreakable = True
    myMap = clearanceMap(myMap)

#_____________ MAP CREATION __________________

#_____________ BOSS FIGHT __________________
deathX = 0
deathY = 0

def basicBossDeath(monster):
    message(monster.name.capitalize() + ' is dead! You gain ' + str(monster.Fighter.xp) + ' XP.', colors.dark_sky)
    
    if monster.Fighter.lootFunction is not None:
        itemIndex = 0
        for item in monster.Fighter.lootFunction:
            loot = randint(1, 100)
            if loot <= monster.Fighter.lootRate[itemIndex]:
                if loot.Item:
                    if loot.Item.amount > 0 or not loot.Item.stackable:
                        lootItem(item, monster.x, monster.y)
                else:
                    lootItem(item, monster.x, monster.y)
            itemIndex += 1
    
    for tile in bossTiles:
        try:
            assert isinstance(tile, Tile) #Just so as to have Eclipse auto-completion
        except AssertionError:
            pass #If tile is indeed a tile, but a save has been loaded, the assertion will fail. So, we just ignore the assertion error

    
    tile.onTriggerFunction = printTileWhenWalked
    bossEntrance.unbreakable = False
    bossEntrance.open()
    bossEntrance.applyGroundProperties()

    monster.char = '%'
    monster.color = colors.dark_red
    monster.blocks = False
    monster.AI = None
    monster.trueName = 'remains of ' + monster.name
    monster.Fighter = None
    monster.sendToBack()
    createEndRooms()

#--Gluttony--
def fatDeath(monster):
    global deathX, deathY
    monster.char = '%'
    monster.color = colors.dark_red
    monster.trueName = 'some mangled fat'
    monster.blocks = False
    monster.AI = None
    monster.Fighter = None
    deathX = monster.x
    deathY = monster.y

def createFat(x, y):
    fatFighterComponent = Fighter(hp = 5, armor = 0, power = 1, xp = 0, deathFunction=fatDeath, accuracy= 0, evasion=1)
    fat_AI_component = Immobile()
    fat = GameObject(x, y, char = '#', color = colors.dark_lime, name = "Gluttony's fat", blocks = True, Fighter = fatFighterComponent, AI = fat_AI_component)
    objects.append(fat)

def fatSpread(spreadRate):
    fatList = []
    for object in objects:
        if object.name == "Gluttony's fat" or object.name == 'Gluttony':
            fatList.append(object)
    chosenFat = randint(0, len(fatList) - 1)
    chosenSide = randint(0, 3)
    coords = [[0, -1], [1, 0], [0, 1], [-1, 0]]
    fatCreated = False
    rotation = 0
    for loop in range(spreadRate):
        while not fatCreated:
            fat = fatList[chosenFat]
            x = fat.x + coords[chosenSide][0]
            y = fat.y + coords[chosenSide][1]
            if not isBlocked(x, y) and x != deathX and y != deathY:
                createFat(x, y)
                fatCreated = True
                break
            else:
                chosenSide += 1
                if chosenSide > 3:
                    chosenSide = 0
                rotation += 1
                if rotation > 3:
                    chosenFat += 1
                    if chosenFat > len(fatList) - 1:
                        chosenFat = 0
                    chosenSide = randint(0, 3)
                    rotation = 0

class Gluttony():
    def takeTurn(self):
        global FOV_recompute
        boss = self.owner
        bossVisibleTiles = tdl.map.quickFOV(boss.x, boss.y, isVisibleTile, fov = BOSS_FOV_ALGO, radius = BOSS_SIGHT_RADIUS, lightWalls= False)
        
        fatSpread(1)
        
        if boss.Fighter.canTakeTurn:
            if boss.distanceTo(player) < 2:
                boss.Fighter.attack(player)
            elif (player.x, player.y) in bossVisibleTiles:
                if boss.Fighter.curShootCooldown <= 0:
                    crosshair = GameObject(player.x, player.y, 'X', 'crosshair', color = colors.red, Ghost = True)
                    objects.append(crosshair)
                    boss.Fighter.curShootCooldown = boss.Fighter.baseShootCooldown
                    boss.Fighter.curLandCooldown = boss.Fighter.baseLandCooldown
                    message('Gluttony vomits huge quantities of seemingly acid liquid up in the air, in your direction! The mixture will soon land.', colors.dark_yellow)
        else:
            pass

        for object in objects:
            if object.name == 'crosshair' and boss.Fighter.curLandCooldown <= 0:
                projectile(boss.x, boss.y, object.x, object.y, '*', colors.desaturated_chartreuse, passesThrough=True, ghost=True)
                for x in range(MAP_WIDTH):
                    for y in range(MAP_HEIGHT):
                        if not isBlocked(x, y) and object.distanceToCoords(x, y) <= 2:
                            myMap[x][y].acid = True
                            myMap[x][y].curAcidCooldown = myMap[x][y].baseAcidCooldown
                            for fighter in objects:
                                if (fighter.x == x and fighter.y == y) and not (fighter.x == object.x and fighter.y == object.y):
                                    if fighter.Fighter:
                                        dmgTextFunc = lambda damageTaken: fighter.Fighter.formatRawDamageText(damageTaken, " touched by the vomit splatters and suffers {}!", colors.orange, " touched by the vomit splatters but it has no effect.", colors.white, True)
                                        fighter.Fighter.takeDamage({'poison': 2}, "Gluttony's vomit", damageTextFunction = dmgTextFunc)
                                        fighter.Fighter.acidify()
                for fighter in objects:
                    if fighter.x == object.x and fighter.y == object.y:
                        if fighter.Fighter and not fighter == object:
                            dmgTextFunc = lambda damageTaken: fighter.Fighter.formatRawDamageText(damageTaken, " touched by the vomit splatters and suffers {}!", colors.orange, " touched by the vomit splatters but it has no effect.", colors.white, True)
                            damageTaken = fighter.Fighter.takeDamage({'poison': 15}, "Gluttony's vomit", damageTextFunction = dmgTextFunc)
                            fighter.Fighter.acidify()
                objects.remove(object)
                FOV_recompute = True
                break

        for object in objects:
            if object.name == "Gluttony's fat" and object.distanceTo(player) < 2:
                dmgTextFunc = lambda damageTaken: player.Fighter.formatRawDamageText(damageTaken, 'The massive chunks of flesh around you start crushing you slowly! {} suffer {}.', colors.dark_orange, "Gluttony's pression has no effect on you.", colors.white)
                player.Fighter.takeDamage({'physical': 1}, object.name, damageTextFunction = dmgTextFunc)
                break

def gluttonysDeath(monster):
    message(monster.name.capitalize() + ' is dead! You have slain a boss and gain ' + str(monster.Fighter.xp) + ' XP!', colors.dark_sky)

    monster.char = '%'
    monster.color = colors.dark_red
    monster.blocks = False
    monster.AI = None
    monster.trueName = 'remains of ' + monster.name
    monster.Fighter = None
    monster.sendToBack()
    for object in objects:
        if object.name == "Gluttony's fat": #or (object.AI and (object.AI.__class__.__name__ == "Immobile")):
            object.Fighter.hp = 0
            fatDeath(object)
    createEndRooms()
#--Gluttony--

#--Wrath--   WIP
class Wrath(Charger):
    def __init__(self):
        self.chargeCooldown = 0
        self.curChargeCooldown = 0
        self.explodeCooldown = 0
        self.flurryCooldown = 0
        Charger.__init__(self)

    def takeTurn(self):
        boss = self.owner
        bossVisibleTiles = tdl.map.quickFOV(boss.x, boss.y, isVisibleTile, fov = BOSS_FOV_ALGO, radius = BOSS_SIGHT_RADIUS, lightWalls= False)
        
        if (player.x, player.y) in bossVisibleTiles:
            if self.charging and self.curChargeCooldown <= 0:
                self.charge()
            elif boss.distanceTo(player) < 2 and not self.charging:
                if self.flurryCooldown <= 0:
                    message('Wrath unleashes a volley of slashes at you!', colors.amber)
                    numberHits = randint(2, 4)
                    for hit in range(numberHits):
                        boss.Fighter.attack(player)
                        print("Wrath attacked")
                    self.flurryCooldown = 21
                else:
                    boss.Fighter.attack(player)
            elif boss.distanceTo(player) <= 4:
                if self.explodeCooldown <= 0:
                    monsterArmageddon('Wrath', boss.x, boss.y, 4, 30, False)
                    self.explodeCooldown = 31
            elif self.chargeCooldown <= 0 and not self.charging:
                self.defineChargePath(player)
                self.chargeCooldown = 16
                self.curChargeCooldown = 2
            elif not self.charging:
                boss.moveAstar(player.x, player.y, fallback = True)
            
        self.chargeCooldown -= 1
        self.curChargeCooldown -= 1
        self.explodeCooldown -= 1
        self.flurryCooldown -= 1
#--Wrath--

#-- High Inquisitor --
class HighInquisitor(Spellcaster):
    def __init__(self):
        Spellcaster.__init__(self)
    
    '''
    def takeTurn(self):
        global FOV_recompute
        monster = self.owner
        selectedTarget = None
        if self.owner.Fighter.canTakeTurn and monster.distanceTo(player) <= 20:
            self.selectTarget()
            if selectedTarget is not None:
                choseSpell = True
                if len(monster.Fighter.knownSpells) > 0:
                    randSpell = randint(0, len(monster.Fighter.knownSpells) - 1)
                    firstSpell = randSpell
                    action = None
                    while action is None:
                        chosenSpell = monster.Fighter.knownSpells[randSpell]
                        action = chosenSpell.cast(monster, selectedTarget)
                        if action == 'cancelled':
                            action = None
                            randSpell += 1
                            if randSpell == firstSpell:
                                choseSpell = False
                                break
                            if randSpell >= len(monster.Fighter.knownSpells):
                                randSpell = 0
                else:
                    choseSpell = False
                
                if not choseSpell:
                    if monster.distanceTo(selectedTarget) < 2:
                        monster.Fighter.attack(selectedTarget)
                    else:
                        self.flee()
            else:
                if not 'frozen' in convertBuffsToNames(monster.Fighter) and monster.distanceTo(player) >= 2:
                    self.wander()
        elif not 'frozen' in convertBuffsToNames(monster.Fighter):
            self.wander()
        FOV_recompute = True
    '''
#-- High Inquisitor --
'''
class TestInquisitor(BasicMonster):
    def __init__(self):
        BasicMonster.__init__(self)
        
    def takeTurn(self):
        global FOV_recompute
        monster = self.owner
        if (self.owner.Fighter.canTakeTurn and ((player.x, player.y) in convertTilesToCoords(bossTiles)):
            sX, sY = self.owner.x, self.owner.y
            curDjik = myMap[sX][sY].djikValue
            if curDjik < -1.2:
                curBest = myMap[sX][sY]
                for tile in myMap[sX][sY].neighbors():
                    if not tile.blocked:
                        if tile.djikValue < curBest.djikValue:
                            curBest = tile
                if (curBest.x, curBest.y) != (sX, sY):
                    self.owner.moveTo(curBest.x, curBest.y)
            else:
                self.owner.Fighter.attack(player)
        else:
            if self.owner.Fighter.canTakeTurn:
                if not (player.x, player.y) in convertTilesToCoords(bossTiles):
                    print(player.x, player.y, sep=";")
                    print(convertTilesToCoords(bossTiles))
                self.wander()
'''    

def placeBoss(name, x, y):
    if name == 'Gluttony':
        fighterComponent = Fighter(hp=1000, armor=6, power=8, xp = 1000, deathFunction = gluttonysDeath, accuracy = 13, evasion = 1, shootCooldown = 10, landCooldown = 4)
        AI_component = Gluttony()
        boss = GameObject(x, y, char = 'G', color = colors.darker_lime, name = name, blocks = True, Fighter = fighterComponent, AI = AI_component)
        objects.append(boss)
        
        for x in range(boss.x - 5, boss.x + 5):
            for y in range(boss.y - 5, boss.y + 5):
                if not isBlocked(x, y) and boss.distanceToCoords(x, y) <= 3:
                    createFat(x, y)

    if name == 'Wrath':
        fighterComponent = Fighter(hp = 600, armor = 3, power = 18, xp = 1000, deathFunction = basicBossDeath, accuracy = 25, evasion = 15)
        AI_component = Wrath()
        boss = GameObject(x, y, char = 'W', color = colors.darker_red, name = name, blocks = True, Fighter = fighterComponent, AI = AI_component)
        objects.append(boss)
    
    if name == 'High Inquisitor':
        inquisitorFireball = Spell(ressourceCost = 0, cooldown = 4, useFunction = castFireball, name = "Fireball", ressource = 'MP', type = 'Magic', magicLevel = 1, arg1 = 0, arg2 = 20, arg3 = 6)
        fighterComponent = Fighter(hp = 300, armor = 2, power = 5, xp = 1000, deathFunction = basicBossDeath, accuracy = 75, evasion = 25, maxMP = 50, knownSpells=[inquisitorFireball])
        AI_component = HighInquisitor()
        boss = GameObject(x, y, char = 'I', color = colors.darker_magenta, name = name, blocks = True, Fighter = fighterComponent, AI = AI_component)
        objects.append(boss)
    
                
#_____________ BOSS FIGHT __________________

#_____________ ROOM POPULATION + ITEMS GENERATION_______________
potionIdentify = {}
scrollIdentify = {}
colorDict = {'blue': (colors.blue, 'smokybluepotion.xp', 'The blueish smokes emanating from this potion is not very reassuring about what effects it could bring.'), 'red': (colors.red, 'redpotion.xp', 'A slighly bubbling red beverage.'), 'violet': (colors.violet, 'violetpotion.xp', 'A slighly bubbling violet beverage.')}
nameDict = ['Ewaz', 'Vuzin', 'Armuz', 'Gowid', 'Ansuz', 'Juman', 'Ji', 'Morwen']

def convertItemTemplate(template):
    if template.Equipment:
        eq = template.Equipment
        equipmentComp = Equipment(eq.slot, eq.type, eq.powerBonus.value, eq.armorBonus.value, eq.maxHP_Bonus.value, eq.accuracyBonus.value,
                                  eq.evasionBonus.value, eq.criticalBonus.value, eq.maxMP_Bonus.value, eq.strengthBonus.value,
                                  eq.dexterityBonus.value, eq.vitalityBonus.value, eq.willpowerBonus.value, eq.ranged, eq.rangedPower.value,
                                  eq.maxRange.value, eq.ammo, eq.meleeWeapon, eq.armorPenetrationBonus.value, eq.slow, eq.enchant,
                                  eq.staminaBonus.value, eq.stealthBonus.value, eq.atkSpeed, eq.dmgType, eq.res)
    if template.Item:
        it = template.Item
        
        useFunc = None
        
        amount = it.amount
        if eq.ammo and eq.ammo == 'none': #if it is a throwing weapon
            amount = 30
        
        itemComp = Item(useFunc, it.arg1, it.arg2, it.arg3, it.stackable, amount, it.weight, it.description, it.pic, it.itemType, it.useText)
    
    return GameObject(0, 0, template.char, template.name, template.color, Item = itemComp, Equipment = equipmentComp, pName = template.pName)

def createSword(x, y):
    name = 'sword'
    pic = 'shortSword.xp'
    char = '-'
    color = colors.silver
    sizeChance = {'short' : 40, 'long' : 45, 'great ': 15}
    sizeChoice = randomChoice(sizeChance)
    name = sizeChoice + name
    type = 'light weapon'
    slot = 'one handed'
    slowness = False
    if sizeChoice == 'short':
        swordPow = 6
        weight = 1.5
    elif sizeChoice == 'long':
        swordPow = 10
        weight = 3.5
        pic = 'longSword.xp'
    else:
        swordPow = 18
        char = '/'
        weight = 10.0
        pic = 'greatSword.xp'
        type = 'heavy weapon'
        slot = 'two handed'
        slowness = True
    qualityChances = {'normal' : 70, 'rusty' : 20, 'sharp' : 10}
    qualityChoice = randomChoice(qualityChances)
    if qualityChoice == 'rusty':
        name = qualityChoice + ' ' + name
        swordPow -= 2
        if sizeChoice == 'long':
            pic = 'rustyLongSword.xp'
        elif sizeChoice == 'short':
            pic = 'rustyShortSword.xp'
        else:
            pic = 'rustyGreatSword.xp'
        color = colors.brass
    elif qualityChoice == 'sharp':
        name = qualityChoice + ' ' + name
        swordPow += 2
        color = colors.light_sky
        if sizeChoice == 'long':
            pic = 'sharpLongSword.xp'
        elif sizeChoice == 'short':
            pic = 'sharpShortSword.xp'
        else:
            pic = 'sharpGreatSword.xp'
    burningChances = {'yes' : 1120, 'no': 80}
    burningChoice = randomChoice(burningChances)
    burning = None
    if burningChoice == 'yes':
        burning = Enchantment('burning', functionOnAttack=applyBurn)
        name = 'burning ' + name

    equipmentComponent = Equipment(slot=slot, type = type, powerBonus = swordPow, meleeWeapon=True, slow= slowness, enchant=burning)
    sword = GameObject(x, y, char, name, color, Equipment = equipmentComponent, Item = Item(weight=weight, pic = pic, useText = 'Equip'))
    return sword

def createAxe(x, y):
    name = 'axe'
    pic = 'axe.xp'
    char = '-'
    color = colors.silver
    sizeChance = {'great ' : 20, '' : 80}
    sizeChoice = randomChoice(sizeChance)
    name = sizeChoice + name
    type = 'light weapon'
    slot = 'one handed'
    slow = False
    if sizeChoice == 'great ':
        axePow = 16
        weight = 15.0
        armorPenetration = 6
        type = 'heavy weapon'
        slot = 'two handed'
        pic = 'greatAxe.xp'
        slow = True
        char = '/'
    else:
        axePow = 8
        weight = 5.5
        armorPenetration = 3
    qualityChances = {'normal' : 70, 'rusty' : 20, 'sharp' : 10}
    qualityChoice = randomChoice(qualityChances)
    if qualityChoice == 'rusty':
        name = qualityChoice + ' ' + name
        axePow -= 2
        armorPenetration -= 1
        color = colors.brass
        if sizeChoice == 'great ':
            pic = 'rustyGreatAxe.xp'
        else:
            pic = 'rustyAxe.xp'
    elif qualityChoice == 'sharp':
        name = qualityChoice + ' ' + name
        axePow += 2
        armorPenetration += 1
        color = colors.light_sky
        if sizeChoice == 'great ':
            pic = 'sharpGreatAxe.xp'
        else:
            pic = 'sharpAxe.xp'
    burningChances = {'yes' : 20, 'no': 80}
    burningChoice = randomChoice(burningChances)
    burning = None
    if burningChoice == 'yes':
        burning = Enchantment('burning', functionOnAttack=applyBurn)
        name = 'burning ' + name
    equipmentComponent = Equipment(slot=slot, type = type, powerBonus = axePow, meleeWeapon=True, armorPenetrationBonus=armorPenetration, slow = slow, enchant=burning)
    axe = GameObject(x, y, char, name, color, Equipment = equipmentComponent, Item = Item(weight=weight, pic = pic, useText = 'Equip'))
    return axe

def createHammer(x, y):
    name = 'hammer'
    pic = 'hammer.xp'
    char = '-'
    color = colors.silver
    sizeChance = {'great ' : 20, '' : 80}
    sizeChoice = randomChoice(sizeChance)
    name = sizeChoice + name
    type = 'light weapon'
    slot = 'one handed'
    slow = False
    if sizeChoice == 'great ':
        hammerPow = 19
        weight = 18.0
        critBonus = 5
        type = 'heavy weapon'
        slot = 'two handed'
        pic = 'greatHammer.xp'
        slow = True
        char = '/'
    else:
        hammerPow = 11
        weight = 5.5
        critBonus = 3
    qualityChances = {'normal' : 70, 'rusty' : 20, 'heavy' : 10}
    qualityChoice = randomChoice(qualityChances)
    if qualityChoice == 'rusty':
        name = qualityChoice + ' ' + name
        hammerPow -= 2
        critBonus -= 1
        color = colors.brass
    elif qualityChoice == 'heavy':
        name = qualityChoice + ' ' + name
        hammerPow += 2
        critBonus += 1
        color = colors.light_sky
    burningChances = {'yes' : 20, 'no': 80}
    burningChoice = randomChoice(burningChances)
    burning = None
    if burningChoice == 'yes':
        burning = Enchantment('burning', functionOnAttack=applyBurn)
        name = 'burning ' + name
    equipmentComponent = Equipment(slot=slot, type = type, powerBonus = hammerPow, criticalBonus=critBonus, meleeWeapon=True, slow = slow, enchant = burning)
    hammer = GameObject(x, y, char, name, color, Equipment = equipmentComponent, Item = Item(weight=weight, pic = pic, useText = 'Equip'))
    return hammer

def createMace(x, y):
    name = 'mace'
    pic = 'mace.xp'
    color = colors.silver
    macePow = 8
    weight = 8.5
    hitBonus = 8
    qualityChances = {'normal' : 70, 'soft' : 20, 'pointy' : 10}
    qualityChoice = randomChoice(qualityChances)
    if qualityChoice == 'soft':
        name = qualityChoice + ' ' + name
        macePow -= 2
        hitBonus -= 3
        color = colors.brass
    elif qualityChoice == 'pointy':
        name = qualityChoice + ' ' + name
        macePow += 2
        hitBonus += 3
        color = colors.light_sky
    burningChances = {'yes' : 20, 'no': 80}
    burningChoice = randomChoice(burningChances)
    burning = None
    if burningChoice == 'yes':
        burning = Enchantment('burning', functionOnAttack=applyBurn)
        name = 'burning ' + name
    equipmentComponent = Equipment(slot='one handed', type = 'light weapon', powerBonus = macePow, accuracyBonus=hitBonus, meleeWeapon=True, enchant=burning)
    mace = GameObject(x, y, '-', name, color, Equipment = equipmentComponent, Item = Item(weight=weight, pic = pic, useText = 'Equip'))
    return mace

def createWeapon(x, y):
    weaponChances = currentBranch.weaponChances
    weaponChoice = randomChoice(weaponChances)
    if weaponChoice == 'sword':
        weapon = createSword(x, y)
    elif weaponChoice == 'axe':
        weapon = createAxe(x, y)
    elif weaponChoice == 'hammer':
        weapon = createHammer(x, y)
    elif weaponChoice == 'mace':
        weapon = createMace(x, y)
    weapon.Item.useText = 'Equip'
    return weapon

def createScroll(x, y):
    scrollChances = currentBranch.scrollChances
    scrollChoice = randomChoice(scrollChances)
    unIdentifiedName = 'scroll of ' + scrollIdentify[scrollChoice]
    pName = 'scrolls of ' + scrollIdentify[scrollChoice]
    identified = False
    if unIdentifiedName in identifiedItems:
        identified = True
    if scrollChoice == 'lightning':
        scroll = GameObject(x, y, '~', 'scroll of lightning bolt', colors.light_yellow, Item = Item(useFunction = lambda : castSpellAndID(scroll, castLightning), weight = 0.3, stackable = True, unIDName=unIdentifiedName, identified=identified, unIDpName=pName, pic = 'scroll.xp'), blocks = False, pName = 'scrolls of lightning bolt')
    elif scrollChoice == 'confuse':
        scroll = GameObject(x, y, '~', 'scroll of confusion', colors.light_yellow, Item = Item(useFunction = lambda : castSpellAndID(scroll, castConfuse), weight = 0.3, stackable = True, unIDName=unIdentifiedName, identified=identified, unIDpName=pName, pic = 'scroll.xp'), blocks = False, pName = 'scrolls of confusion')
    elif scrollChoice == 'fireball':
        fireballChances = {'lesser': 20, 'normal': 50, 'greater': 20}
        fireballChoice = randomChoice(fireballChances)
        if fireballChoice == 'lesser':
            scroll = GameObject(x, y, '~', 'scroll of lesser fireball', colors.light_yellow, Item = Item(lambda : castSpellAndID(scroll, castFireball, 2, 12), weight = 0.3, stackable = True, unIDName=unIdentifiedName, identified=identified, unIDpName=pName, pic = 'scroll.xp'), blocks = False, pName = 'scrolls of lesser fireball')
        elif fireballChoice == 'normal':
            scroll = GameObject(x, y, '~', 'scroll of fireball', colors.light_yellow, Item = Item(lambda : castSpellAndID(scroll, castFireball), weight = 0.3, stackable = True, unIDName=unIdentifiedName, identified=identified, unIDpName=pName, pic = 'scroll.xp'), blocks = False, pName = 'scrolls of fireball')
        elif fireballChoice == 'greater':
            scroll = GameObject(x, y, '~', 'scroll of greater fireball', colors.light_yellow, Item = Item(lambda : castSpellAndID(scroll, castFireball, 4, 48), weight = 0.3, stackable = True, unIDName=unIdentifiedName, identified=identified, unIDpName=pName, pic = 'scroll.xp'), blocks = False, pName = 'scrolls of greater fireball')
    elif scrollChoice == 'armageddon':
        scroll = GameObject(x, y, '~', 'scroll of armageddon', colors.light_yellow, Item = Item(lambda : castSpellAndID(scroll, castArmageddon), weight = 0.3, stackable = True, unIDName=unIdentifiedName, identified=identified, unIDpName=pName, pic = 'scroll.xp'), blocks = False, pName = 'scrolls of armageddon')
    elif scrollChoice == 'ice':
        scroll = GameObject(x, y, '~', 'scroll of ice bolt', colors.light_yellow, Item = Item(lambda : castSpellAndID(scroll, castFreeze), weight = 0.3, stackable = True, amount = randint(1, 3), unIDName=unIdentifiedName, identified=identified, unIDpName=pName, pic = 'scroll.xp'), blocks = False, pName = 'scrolls of ice bolt')
    elif scrollChoice == 'none':
        scroll = None
    if scroll is not None:
        scroll.Item.useText = 'Read'
    return scroll

def createPotion(x, y):
    potionChances = currentBranch.potionChances
    potionChoice = randomChoice(potionChances)
    name, color, pic, desc = potionIdentify[potionChoice]
    unIdentifiedName = name + ' potion'
    pName = name + ' potions'
    identified = False
    if unIdentifiedName in identifiedItems:
        identified = True
    if potionChoice == 'heal':
        potion = GameObject(x, y, chr(173), 'healing potion', color, Item = Item(useFunction = lambda : castSpellAndID(potion, castHeal), weight = 0.4, stackable=True, amount = randint(1, 2), pic = pic, description = "A potion that stimulates cell growth when ingested, which allows for wounds to heal signifcantly faster. However, it also notably increases risk of cancer, but if you're in a situation where you have to drink such a potion, this is probably one of the least of your worries.", unIDName=unIdentifiedName, identified=identified, unIDpName=pName, unIDdesc = desc), blocks = False)
    if potionChoice == 'mana':
        potion = GameObject(x, y, chr(173), 'mana regeneration potion', color, Item = Item(useFunction = lambda : castSpellAndID(potion, castRegenMana, 10)  ,weight = 0.4, stackable = True, pic = pic, description = "The awkward look of this potion scared more than one novice mage, but it actually tastes quite good and has no other short-term effect other than replenishing your life-force. However, the [PLACEHOLDER  WORLD (the 'normal' one, not Realm of Madness) NAME]'s Guild of Alchemists is still debating about whether or not it causes detrimental long-term effects.", unIDName=unIdentifiedName, identified=identified, unIDpName=pName, unIDdesc = desc), blocks = False)
    potion.Item.useText = 'Drink'
    return potion

def castSpellAndID(object, spell, *args):
    spell(*args)
    identifiedItems.append(object.Item.unIDName)
    object.Item.identified = True
    for other in objects:
        if other.Item and other.Item.unIDName == object.Item.unIDName:
            other.Item.identified = True
        

def createSpellbook(x, y):
    spellbookChances = currentBranch.spellbookChances
    spellbookChoice = randomChoice(spellbookChances)
    if spellbookChoice == "healSelf":
        spellbook = GameObject(x, y, '=', 'spellbook of healing', colors.violet, Item = Item(useFunction = learnSpell, arg1 = heal, weight = 1.0, pic = 'spellbook.xp'), blocks = False)
    elif spellbookChoice == "fireball":
        spellbook = GameObject(x, y, '=', 'spellbook of fireball', colors.violet, Item = Item(useFunction = learnSpell, arg1 = fireball, weight = 1.0, pic = 'spellbook.xp'), blocks = False)
    elif spellbookChoice == "lightning":
        spellbook = GameObject(x, y, '=', 'spellbook of lightning bolt', colors.violet, Item = Item(useFunction = learnSpell, arg1 = lightning, weight = 1.0, pic = 'spellbook.xp'), blocks = False)
    elif spellbookChoice == "confuse":
        spellbook = GameObject(x, y, '=', 'spellbook of confusion', colors.violet, Item = Item(useFunction = learnSpell, arg1 = confuse, weight = 1.0, pic = 'spellbook.xp'), blocks = False)
    elif spellbookChoice == "ice":
        spellbook = GameObject(x, y, '=', 'spellbook of ice bolt', colors.violet, Item = Item(useFunction = learnSpell, arg1 = ice, weight = 1.0, pic = 'spellbook.xp'), blocks = False)
    elif spellbookChoice == 'none':
        spellbook = None
    spellbook.Item.useText = 'Read'
    return spellbook

def convertMobTemplate(template):
    rangedComp = None
    fightComp = None
    globalDict = globals()
    if template.Fighter.Ranged:
        ra = template.Fighter.Ranged
        attackFunctions = []
        for string in ra.attackFunctions:
            if 'lambda' in string:
                attackFunctions.append(eval(string))
            else:
                attackFunctions.append(globalDict[string])

        rangedComp = RangedNPC(ra.shotRange, ra.power, ra.accuracy, ra.critical, ra.armorPenetration, ra.buffsOnAttack, ra.leechRessource,
                               attackFunctions, ra.shootMessage, ra.projChar, ra.projColor, ra.continues, ra.passesThrough, ra.ghost)
        
    if template.Fighter:
        fi = template.Fighter
        ## /!\ deathFunction*, knownSpells*, buffs, attackFunctions*, equipmentList*
        deathFunc = globalDict[fi.deathFunction]
        knownSpells = []
        for name in fi.knownSpells:
            if 'SpellTemplate' in name:
                knownSpells.append(convertRandTemplateToSpell(eval('spellGen.'+name)))
            else:
                try:
                    knownSpells.append(globalDict[name])
                except:
                    raise UnrecognizedElement("Spell of {} is not recognized: \n{}".format(template.name, name))
        toEquip = []
        for eq in fi.equipmentList:
            print(eq)
            if eq[1] == 'armor':
                eqTemp = itemGen.generateArmor(totalLevel, player.level, eq[2], eq[3])
                picInd = 4
            elif eq[1] == 'weapon':
                try:
                    weapon = eq[4]
                except IndexError:
                    weapon = None
                eqTemp = itemGen.generateMeleeWeapon(totalLevel, player.level, eq[2], weapon)
                picInd = 3
            try:
                equipment = convertItemTemplate(eqTemp)
            except:
                raise UnrecognizedElement("Equipment of {} is not recognized: \n{}".format(template.name, eq))
            equipment.trueName = eq[0]
            try:
                equipment.Item.pic = eq[picInd]
            except:
                pass
            toEquip.append(equipment)
        lootFunction = []
        for item in fi.lootFunction:
            if type(item) == type(1):
                lootFunction.append(toEquip[item])
            elif 'GameObjectTemplate' in item:
                lootFunction.append(convertItemTemplate(eval('itemGen.'+item)))
            elif 'GameObject' in item:
                lootFunction.append(eval(item))
            else:
                raise UnrecognizedElement("Loot of {} is not recognized: \n{}".format(template.name, item))
        attackFunctions = []
        for string in fi.attackFunctions:
            if 'lambda' in string:
                attackFunctions.append(eval(string))
            else:
                try:
                    attackFunctions.append(globalDict[string])
                except:
                    raise UnrecognizedElement("AttackFunc of {} is not recognized: \n{}".format(template.name, string))
        
        fightComp = Fighter(fi.hp, fi.armor, fi.power, fi.accuracy, fi.evasion, fi.xp, deathFunc, fi.mp, knownSpells, fi.critical,
                            fi.armorPenetration, lootFunction, fi.lootRate, 0, 0, fi.transferDamage, fi.leechRessource, fi.leechAmount,
                            fi.buffsOnAttack, fi.slots, [], toEquip, attackFunctions, fi.noDirectDamage, 'ogre.xp', fi.description, 0,
                            rangedComp, fi.stamina, fi.attackSpeed, fi.moveSpeed, fi.rangedSpeed, fi.resistances, fi.attackTypes)
    
    return GameObject(0, 0, template.char, template.name, template.color, blocks = True, Fighter = fightComp, AI = eval(template.AI),
                      flying = template.flying, size = template.size, sizeChar = template.sizeChar, sizeColor = template.sizeColor,
                      smallChar = template.smallChar)

def createDarksoul(x, y, friendly = False, corpse = False):
    if (x, y) != (player.x, player.y):
        if not corpse:
            equipmentComponent = Equipment(slot='head', type = 'armor', armorBonus = 2)
            darksoulHelmet = GameObject(x = None, y = None, char = '[', name = 'darksoul helmet', color = colors.silver, Equipment = equipmentComponent, Item = Item(weight = 2.5, pic = 'darksoulHelmet.xp'))
            money = GameObject(x = None, y = None, char = '$', name = 'gold coin', color = colors.gold, Item=Money(randint(10, 50)), blocks = False, pName = 'gold coins')
            lootOnDeath = [darksoulHelmet, money]
            deathType = monsterDeath
            darksoulName = "darksoul"
            color = colors.light_grey
            toEquip = [darksoulHelmet]
        else:
            darksoulName = "darksoul skeleton"
            deathType = zombieDeath
            lootOnDeath = None
            color = colors.lighter_gray
            toEquip = []
        if not friendly:
            AI_component = BasicMonster()
        else:
            AI_component = FriendlyMonster(friendlyTowards = player)
        fighterComponent = Fighter(hp=30, armor=0, power=6, xp = 35, deathFunction = deathType, evasion = 25, accuracy = 10, lootFunction = lootOnDeath, lootRate = [30, 20], toEquip=toEquip, moveSpeed = 150, attackSpeed = 150)
        monster = GameObject(x, y, char = 'd', color = color, name = darksoulName, blocks = True, Fighter=fighterComponent, AI = AI_component)
        return monster
    else:
        return 'cancelled'

def createOgre(x, y, friendly = False, corpse = False):
    if (x, y) != (player.x, player.y):
        if not corpse:
            equipmentComponent = Equipment(slot = 'two handed', type = 'heavy weapon', powerBonus = 15, accuracyBonus = -20, meleeWeapon=True, slow = True)
            trollMace = GameObject(x, y, '/', 'ogre mace', colors.darker_orange, Equipment=equipmentComponent, Item=Item(weight = 13.0, pic = 'trollMace.xp', description= 'A dumb weapon for dumb people.'))
            lootOnDeath = [trollMace]
            deathType = monsterDeath
            monName = "ogre"
            color = colors.lightest_yellow
        else:
            monName = "ogre skeleton"
            deathType = zombieDeath
            lootOnDeath = None
            color = colors.lighter_grey
        if not friendly:
            AI_component = BasicMonster()
        else:
            AI_component = FriendlyMonster(friendlyTowards = player)
        fighterComponent = Fighter(hp=40, armor=4, power=8, xp = 100, deathFunction = deathType, accuracy = 7, evasion = 1, lootFunction=lootOnDeath, lootRate=[15])
        monster = GameObject(x, y, char = 'O', color = color, name = monName, blocks = True, Fighter=fighterComponent, AI = AI_component)
        return monster
    else:
        if corpse:
            message("You briefly feel something moving beneath your feet...")
        return 'cancelled'

def createGreedyFiend(x, y, friendly = False, corpse = False):
    if (x, y) != (player.x, player.y):
        if not corpse:
            deathType = monsterDeath
            monName = "greedy fiend"
            color = colors.dark_orange
            money = GameObject(x = None, y = None, char = '$', name = 'gold coin', color = colors.gold, Item=Money(0), blocks = False, pName = 'gold coins')
            lootOnDeath = [money]
        else:
            monName = "YOU_SHOULDNT_SEE_THIS"
            deathType = zombieDeath
            lootOnDeath = None
            color = colors.lighter_grey
        if not friendly:
            AI_component = BasicMonster()
        else:
            AI_component = FriendlyMonster(friendlyTowards = player)
        fighterComponent = Fighter(hp=20, armor=2, power=1, xp = 30, deathFunction = deathType, accuracy = 30, evasion = 20, lootFunction=lootOnDeath, lootRate=[100], attackFunctions= [lambda ini, target : stealMoneyAndDamage(ini, target, 300)], noDirectDamage = True)
        monster = GameObject(x, y, char = 'f', color = color, name = monName, blocks = True, Fighter=fighterComponent, AI = AI_component)
        return monster
    else:
        if corpse:
            message("You briefly feel something moving beneath your feet...")
        return 'cancelled'
    
def createHiroshiman(x, y):
    if (x, y) != (player.x, player.y):
        fighterComponent = Fighter(hp=300, armor=0, power=6, xp = 500, deathFunction = monsterDeath, accuracy = 0, evasion = 1)
        AI_component = SplosionAI()
        monster = GameObject(x, y, char = 'H', color = colors.red, name = 'Hiroshiman', blocks = True, Fighter=fighterComponent, AI = AI_component)
        return monster
    else:
        return 'cancelled'

def createCultist(x,y):
    if (x, y) != (player.x, player.y):
        robeEquipment = Equipment(slot = 'torso', type = 'light armor', maxHP_Bonus = 5, maxMP_Bonus = 10)
        robe = GameObject(0, 0, '[', 'cultist robe', colors.purple, Equipment = robeEquipment, Item=Item(weight = 1.5, pic = 'cultistRobe.xp'))
        
        knifeEquipment = Equipment(slot = 'one handed', type = 'light weapon', powerBonus = 7, meleeWeapon = True)
        knife = GameObject(0, 0, '-', 'cultist knife', colors.desaturated_azure, Equipment = knifeEquipment, Item=Item(weight = 1.0))
        
        spellbook = GameObject(x, y, '=', 'spellbook of arcane rituals', colors.violet, Item = Item(useFunction = learnSpell, arg1 = darkPact, weight = 1.0, description = "A spellbook full of arcane rituals and occult incantations. Such magic is easy to learn and to use, but comes at a great price.", pic = 'spellbook.xp'), blocks = False)
        
        money = GameObject(x = None, y = None, char = '$', name = 'gold coin', color = colors.gold, Item=Money(randint(20, 300)), blocks = False, pName = 'gold coins')
        
        fighterComponent = Fighter(hp = 20, armor = 2, power = 6, xp = 30, deathFunction = monsterDeath, accuracy = 18, evasion = 30, lootFunction = [robe, knife, spellbook, money], lootRate = [60, 20, 7, 40])
        AI_component = BasicMonster()
        monster = GameObject(x, y, char = 'c', color = colors.purple, name = 'cultist', blocks = True, Fighter = fighterComponent, AI = AI_component)
        return monster
    else:
        return 'cancelled'

def createHighCultist(x, y):
    if (x, y) != (player.x, player.y):
        robeEquipment = Equipment(slot = 'torso', type = 'light armor', maxHP_Bonus = 5, maxMP_Bonus = 25)
        robe = GameObject(0, 0, '[', 'high cultist robe', colors.purple, Equipment = robeEquipment, Item=Item(weight = 1.5, pic = 'cultistRobe.xp'))
        
        flailEquipment = Equipment(slot = 'one handed', type = 'heavy weapon', powerBonus = 13, meleeWeapon = True)
        flail = GameObject(0, 0, '/', 'bloodsteel flail', colors.red, Equipment=flailEquipment, Item=Item(weight=5.5, pic = 'bloodsteelFlail.xp', description = "A heavy flail wielded by the high cultists and made of a heavy, blood-red metal."))
        
        spellbook = GameObject(x, y, '=', 'spellbook of arcane rituals', colors.violet, Item = Item(useFunction = learnSpell, arg1 = darkPact, weight = 1.0, description = "A spellbook full of arcane rituals and occult incantations. Such magic is easy to learn and to use, but comes at a great price.", pic = 'spellbook.xp'), blocks = False)
        
        fighterComponent = Fighter(hp = 40, armor = 2, power = 13, xp = 80, deathFunction = monsterDeath, accuracy = 20, evasion = 30, lootFunction = [robe, flail, spellbook], lootRate = [60, 25, 15])
        AI_component = BasicMonster()
        name = nameGen.humanLike()
        actualName = name + ' the high cultist'
        monster = GameObject(x, y, char = 'C', color = colors.dark_red, name = actualName, blocks = True, Fighter = fighterComponent, AI = AI_component)
        return monster
    else:
        return 'cancelled'

def createSnake(x, y):
    if x!= player.x or y != player.y:
        fighterComponent = Fighter(hp = 10, armor = 0, power = 3, xp = 10, deathFunction = monsterDeath, accuracy = 20, evasion = 70, buffsOnAttack=[[5, 'poisoned']], moveSpeed = 50, attackSpeed = 50)
        AI_component = BasicMonster() #FastMonster(2)
        monster = GameObject(x, y, char = 's', color = colors.light_green, name = 'snake', blocks = True, Fighter = fighterComponent, AI = AI_component)
        return monster
    else:
        return 'cancelled'

def randomChoiceIndex(chances):
    dice = randint(1, sum(chances))
    runningSum = 0
    choice = 0
    for chance in chances:
        runningSum += chance
        if dice <= runningSum:
            return choice
        choice += 1

def randomChoice(chancesDictionnary):
    strings = list(chancesDictionnary.keys())
    chances = [chancesDictionnary[key] for key in strings]
    for value in chances:
        if value < 0:
            print(value)
            print(chancesDictionnary.keys())
            print(chancesDictionnary)
            raise ValueError("Negative value in dict")
    return strings[randomChoiceIndex(chances)]

def placeObjects(room, first = False):
    global highCultistHasAppeared, hiroshimanNumber, monsterChances
    monsterChances = currentBranch.monsterChances
    itemChances = currentBranch.itemChances
    potionChances = currentBranch.potionChances
    numMonsters = randint(0, MAX_ROOM_MONSTERS)
    monster = None
    '''
    if 'ogre' in monsterChances.keys():
        previousTrollChances = int(monsterChances['ogre'])
    if 'hiroshiman' in monsterChances.keys():
        previousHiroChances = int(monsterChances['hiroshiman'])
    if 'highCultist' in monsterChances.keys():
        previousHighCultistChances = int(monsterChances['highCultist'])
        print('Previous high cultist chances {}'.format(previousHighCultistChances))
    if branchLevel > 2 and hiroshimanNumber == 0 and not first and 'hiroshiman' in monsterChances.keys():
        if 'ogre' in monsterChances.keys() and not monsterChances['ogre'] < 50:
            monsterChances['ogre'] -= 50
        monsterChances['hiroshiman'] = 50
    if not highCultistHasAppeared and not first and 'highCultist' in monsterChances.keys():
        if 'ogre' in monsterChances.keys() and not monsterChances['ogre'] < 50:
            monsterChances['ogre'] -= 50
        monsterChances['highCultist'] = 50
    '''
    
    monCount = 0
    for i in range(numMonsters):
        monCount += 1
        print("{}th ITERATION OF MONSTER LOOP WTF IS THIS FREEZING WHY DID REMOVING CHASMS MAKE THIS BREAK".format(monCount))
        try:
            print("THIS IS A RECTANGE")
            x = randint(room.x1+1, room.x2-1)
            y = randint(room.y1+1, room.y2-1)
        except:
            (x,y) = room[randint(0, len(room) - 1)]
            print("THIS IS A CAVE")
        print("X : {} | Y : {}".format(x,y))
        
        if not isBlocked(x, y) and (x, y) != (player.x, player.y) and not myMap[x][y].chasm:
            monsterChoice = randomChoice(monsterChances)
            monster = convertMobTemplate(mobGen.generateMonster(player.level, monsterChoice))
            monster.x, monster.y = x, y
            '''
            if monsterChoice == 'darksoul':
                monster = convertMobTemplate(mobGen.generateMonster(player.level, monsterChoice)) #createDarksoul(x, y)
                monster.x, monster.y = x, y

            elif monsterChoice == 'hiroshiman' and hiroshimanNumber == 0 and branchLevel > 2 and not first:
                monster = createHiroshiman(x, y)
                hiroshimanNumber = 1
                del monsterChances['hiroshiman']
                monsterChances['ogre'] = 20
                
            elif monsterChoice == 'ogre' and not first:
                monster = createOgre(x, y)
            
            elif monsterChoice == 'snake':
                monster = createSnake(x, y)
            
            elif monsterChoice == 'cultist':
                monster = createCultist(x, y)
            elif monsterChoice == 'highCultist' and not first:
                monster = createHighCultist(x, y)
                diagonals = [(x+1, y+1), (x-1, y-1), (x-1, y+1), (x+1, y-1)]
                minionNumber = 0
                for loop in range(len(diagonals)):
                    if minionNumber >= MAX_HIGH_CULTIST_MINIONS:
                        break
                    else:
                        (minionX, minionY) = diagonals[loop]
                        if not isBlocked(minionX, minionY):
                            newMinion = createCultist(minionX, minionY)
                            objects.append(newMinion)
                            minionNumber += 1
                            print("Created minion")
                if minionNumber == 0:
                    print("Couldn't create any minion")
                highCultistHasAppeared = True
            
            elif monsterChoice == 'greedyFiend':
                monster = createGreedyFiend(x, y)
                dice = randint(0, 100)
                if dice < 80:
                    print("Two for the price of one !")
                    diagonals = [(x+1, y+1), (x-1, y-1), (x-1, y+1), (x+1, y-1)]
                    created = False
                    for loop in range(len(diagonals)):
                        if created:
                            break
                        else:
                            (minionX, minionY) = diagonals[loop]
                            if not isBlocked(minionX, minionY):
                                newMinion = createGreedyFiend(minionX, minionY)
                                objects.append(newMinion)
                                created = True
                                print("Created minion")
                    if not created:
                        print("Couldn't deliver your additional greedy friend. I know you're so sad right now.") #I'll consider replacing it with a free high inquisitor so as to console you.
                
            elif monsterChoice == 'starveling':
                affectedStats = [('vitality', 1), ('slow', 1)]
                essenceComp = Essence('Gluttony', colors.darker_lime, affectedStats=affectedStats)
                gluttEssence = GameObject(0, 0, '*', 'minor essence of Gluttony', colors.darker_lime, Essence=essenceComp)
                fighterComponent = Fighter(hp=45, power=10, armor = 0, xp = 50, deathFunction = monsterDeath, evasion = 45, accuracy = 40, leechRessource='hunger', leechAmount=25, lootFunction=[gluttEssence], lootRate=[100])
                monster = GameObject(x, y, char = 'S', color = colors.lightest_yellow, name = 'starveling', blocks = True, Fighter=fighterComponent, AI = BasicMonster())
                            
            else:
                monster = None
            '''
        else:
            if isBlocked(x, y):
                print("IT IS BLOCKEEED")

        if monster != 'cancelled' and monster != None:
            objects.append(monster)

    num_items = randint(0, MAX_ROOM_ITEMS)
    itemCount = 0
    for i in range(num_items):
        itemCount += 1
        print("{}th ITERATION OF ITEM LOOP".format(itemCount))
        try:
            x = randint(room.x1+1, room.x2-1)
            y = randint(room.y1+1, room.y2-1)
            print("ITEM ROOM IS RECTANGLE")
        except:
            (x,y) = room[randint(0, len(room) - 1)]
            print("ITEM ROOM IS CAVE")
        item = None
        if not isBlocked(x, y) and not myMap[x][y].chasm:
            ammo = None
            itemChoice = randomChoice(itemChances)
            print("DONE RANDOM")
            if itemChoice == 'potion':
                item = createPotion(x, y)
                print("POT")
            elif itemChoice == 'scroll':
                item = createScroll(x, y)
                print("SCR")
            elif itemChoice == 'none':
                item = None
                print("NO")
            elif itemChoice == 'weapon':
                #item = createWeapon(x, y)
                item = convertItemTemplate(itemGen.generateMeleeWeapon(totalLevel, player.level))
                print("WEP")
            elif itemChoice == 'rangedWeapon':
                item = convertItemTemplate(itemGen.generateRangedWeapon(totalLevel, player.level))
                ammoName = item.Equipment.ammo
                if ammoName != 'none':
                    itemComponent = Item(stackable = True, amount = 30)
                    ammo = GameObject(x, y, '^', ammoName, colors.light_orange, Item = itemComponent)
                    objects.append(ammo)
                print("RANGED WEP")
            elif itemChoice == 'armor':
                item = convertItemTemplate(itemGen.generateArmor(totalLevel, player.level))
                print("ARM")
            elif itemChoice == 'money':
                item = GameObject(x, y, char = '$', name = 'gold coin', color = colors.gold, Item=Money(randint(15, 30)), blocks = False, pName = 'gold coins')
                print("MON")
            elif itemChoice == 'shield':
                #equipmentComponent = Equipment(slot = 'one handed', type = 'shield', armorBonus=3)
                item = convertItemTemplate(itemGen.generateShield(totalLevel, player.level))
                print("SHI")
            elif itemChoice == 'spellbook':
                item = createSpellbook(x, y)
                print("SPELL")
            elif itemChoice == "food":
                foodChances = currentBranch.foodChances
                foodChoice = randomChoice(foodChances)
                print("FOOD")
                if foodChoice == 'bread':
                    item = GameObject(x, y, ',', "slice of bread", colors.yellow, Item = Item(useFunction=satiateHunger, arg1 = 50, arg2 = "a slice of bread", weight = 0.2, stackable=True, amount = randint(1, 5), description = "This has probably been lying on the ground for ages, but you'll have to deal with it if you don't want to starve.", itemtype = 'food', useText = 'Eat'), blocks = False, pName = "slices of bread") 
                elif foodChoice == 'herbs':
                    item = GameObject(x, y, ',', "'edible' herb", colors.darker_lime, Item = Item(useFunction=satiateHunger, arg1 = 30, arg2 = "some weird looking herb", weight = 0.05, stackable=True, amount = randint(1, 8), description = "An oddly shapen herb, which looks 'slightly' withered. Your empty stomach makes you think this is comestible, but you're not sure about this.", itemtype = 'food', pic = 'herb.xp', useText = 'Eat'), blocks = False, pName = "'edible' herbs")
                elif foodChoice == 'rMeat':
                    def rMeatDebuff(amount, text):
                        if not 'poisoned' in convertBuffsToNames(player.Fighter):
                            poisoned = Buff('poisoned', colors.purple, cooldown=randint(5, 10), continuousFunction=lambda fighter: randomDamage('poison', fighter, chance = 100, minDamage=1, maxDamage=10, dmgType={'poison': 100}))
                            satiateHunger(amount, text)
                            dice = randint(1, 100)
                            if DEBUG:
                                message('Rancid meat dice : {}'.format(dice), colors.purple)
                            if dice <= 90:
                                message("You don't feel very good...", colors.red)
                                poisoned.applyBuff(player)
                        else:
                            message("You really don't want to take the risk of being in worse condition than you currently are.", colors.red)
                            return 'cancelled'
                            
                    item = GameObject(x, y, ',', "piece of rancid meat", colors.light_crimson, Item = Item(useFunction=lambda: rMeatDebuff(400, 'a chunk of rancid meat'), weight = 0.4, stackable=True, amount = 1, description = "'Rancid' is not the most appropriate term to describe the state of this chunk of meat, 'half-putrefacted' would be closer to the reality. Eating this is probably not a good idea", itemtype = 'food', useText = 'Eat'), blocks = False, pName = "pieces of rancid meat")
                elif foodChoice == 'pie':
                    def pieDebuff(amount, text):
                        pieChoices = {'noDebuff' : 20, 'poison' : 20, 'freeze' : 20, 'burn' : 20, 'confuse' : 20}
                        choice = randomChoice(pieChoices)
                        satiateHunger(amount, text)
                        if choice == 'poison':
                            message("This had a very strange aftertaste...", colors.red)
                            poisoned = Buff('poisoned', colors.purple, cooldown=randint(5, 10), continuousFunction=lambda fighter: randomDamage('poison', fighter, chance = 100, minDamage=1, maxDamage=10, dmgType={'poison': 100}))
                            poisoned.applyBuff(player)
                        elif choice == 'freeze':
                            if not 'burning' in convertBuffsToNames(player.Fighter):
                                message("This pie is so cold that you can feel it's coldness as it is going down your throat. Wait, actually it's your whole body that is freezing !", colors.red)
                                frozen = Buff('frozen', colors.light_violet, cooldown = 4)
                                frozen.applyBuff(player)
                            else:
                                message("For a moment, you feel like you're burning a bit less, but it's probably just your imagination. Or your senses going numb because of your imminent death. Or both.")
                        elif choice == 'burn':
                            message("This pie is so hot that your mouth is on fire ! Literally.", colors.red)
                            applyBurn(player, 100)
                        elif choice == 'confuse':
                            message("You feel funny...", colors.red)
                            confused = Buff('confused', colors.white, cooldown = randint(2,8))
                            confused.applyBuff(player)
                        else:
                            message("This didn't taste as bad as you'd expect.")
                                
                    item = GameObject(x, y, ',', "strange pie", colors.fuchsia, Item = Item(useFunction= lambda : pieDebuff(randint(200, 350), 'the pie'), weight = 0.4, stackable=True, amount = 1, description = "This looks like a pie of some sort, but for some reason it doesn't look appetizing at all. Should fill your stomach for a little while though. Wait, is that a worm you saw inside ?", itemtype = 'food', pic = 'pie.xp', useText = 'Eat'), blocks = False, pName = "strange pies")
                elif foodChoice == 'pasta':
                    item = GameObject(x, y, ',', "'plate' of pasta", colors.light_yellow, Item = Item(useFunction=satiateHunger, arg1 = 150, arg2 = "the pasta", weight = 0.3, stackable=True, amount = randint(1, 4), description = "If you exclude the fact that the 'plate' is inexistent, and therefore the pasta are spilled on the floor, this actually looks delicious.", itemtype = 'food', useText = 'Eat'), blocks = False, pName = "'plates' of pasta")
                elif foodChoice == 'meat':
                    item = GameObject(x, y, ',', "piece of cooked meat", colors.red, Item = Item(useFunction=satiateHunger, arg1 = 650, arg2 = "a chunk of edible meat (at last !)", weight = 0.4, stackable=True, amount = 1, description = "A perfectly fine-looking grilled steak. Yummy !", itemtype = 'food', useText = 'Eat'), blocks = False, pName = "cooked pieces of meat")
                elif foodChoice == 'hBaguette':
                    item = GameObject(x, y, ',', "holy baguette", colors.white, Item = Item(useFunction=satiateHunger, arg1 = 1500, arg2 = "le holy baguette", weight = 0.4, stackable=True, amount = 1, description = "HON HON HON ! Dis iz going to be le most goodest meal you iz gonna have in years !", itemtype = 'food', useText = 'Eat'), blocks = False, pName = "holy baguettes") #Easter-egg. You'll maybe want to tone down its spawn rate by a little bit. TO-DO : Add a funny effect when eating this. TO-DO : Make this illuminate the adjacent tiles (when and if we implement lighting)
                else:
                    item = None
            else:
                item = None
                
            if item is not None:
                print("ITEM NOT NONE") 
                item.x, item.y = x, y
                objects.append(item)
                item.sendToBack()
                if ammo is not None:
                    ammo.sendToBack()
            '''
            if 'ogre' in monsterChances.keys():
                print('Reverting ogre chances to previous value (current : {} / previous : {})'.format(monsterChances['ogre'], previousTrollChances))
                monsterChances['ogre'] = previousTrollChances
            if 'hiroshiman' in monsterChances.keys():
                print('Reverting hiroshiman chances to previous value (current : {} / previous : {})'.format(monsterChances['hiroshiman'], previousHiroChances))
                monsterChances['hiroshiman'] = previousHiroChances
            if 'highCultist' in monsterChances.keys():
                print('Reverting high cultist chances to previous value (current : {} / previous : {})'.format(monsterChances['highCultist'], previousHighCultistChances))
                monsterChances['highCultist'] = previousHighCultistChances 
            '''
        else:
            print("COULDNT DO ITEM BECAUSE REASONS")
            if isBlocked(x, y):
                print("ITEM IS BLOCKEEED")
            else:
                print("WAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAT")
            print("CONTINUING FUCKING LOOP BECAUSE WE ARE NOT SUPPOSED TO FREEZE THE WHOLE FUCKING PROGRAM")
            continue
            print("THIS SHOULD NOT DISPLAY")
            return 'I-am-fucking-done-with-this'

def applyIdentification():
    global potionIdentify, scrollIdentify, colorDict, nameDict
    
    for potion in currentBranch.potionChances.keys():
        if not potion in potionIdentify:
            colorName, colorPicDesc = choice(list(colorDict.items()))
            color, pic, desc = colorPicDesc
            del colorDict[colorName]
            potionIdentify[potion] = (colorName, color, pic, desc)
    
    for scroll, u in currentBranch.scrollChances.items():
        if not scroll in scrollIdentify:
            name = nameDict.pop(randint(0, len(nameDict) - 1))
            scrollIdentify[scroll] = name

#_____________ ROOM POPULATION + ITEMS GENERATION_______________

#_____________ EQUIPMENT ________________

def getEquippedInSlot(slot, hand = False):
    if not hand:
        for object in equipmentList:
            if object.Equipment and (object.Equipment.slot == slot or object.Equipment.curSlot == slot) and object.Equipment.isEquipped:
                return object.Equipment
    else:
        for object in equipmentList:
            if object.Equipment and object.Equipment.curSlot == slot and object.Equipment.isEquipped:
                return object.Equipment
    return None

def getEquippedInHands():
    inHands = []
    print('SEARCHING IN HANDS')
    for object in equipmentList:
        if object.Equipment and (object.Equipment.slot == 'one handed' or object.Equipment.slot == 'two handed') and object.Equipment.isEquipped and object.Equipment.curSlot != 'back':
            inHands.append(object)
            print('FOUND ITEM IN HANDS')
    return inHands

def getAllEquipped(object):  #returns a list of equipped items
    if object == player:
        equippedList = []
        for item in equipmentList:
            if item.Equipment and item.Equipment.isEquipped:
                equippedList.append(item.Equipment)
        return equippedList
    elif object.Fighter:
        equippedList = []
        for item in object.Fighter.equipmentList:
            if item.Equipment and item.Equipment.isEquipped:
                equippedList.append(item.Equipment)
        return equippedList
    else:
        return []

#def equipMenu(equipment):
    

#_____________ EQUIPMENT ________________
#EQUIPMENT CLASS WAS HERE, CUT PASTE AT THIS LINE IN CASE OF PROBLM

def getAllWeights(object, onlyArmor = False):
    if object == player:
        totalWeight = 0.0
        if not onlyArmor:
            for item in inventory:
                totalWeight = math.fsum([totalWeight, item.Item.weight])
        equippedList = getAllEquipped(player)
        for equipment in equippedList:
            item = equipment.owner
            if not onlyArmor or 'armor' in equipment.type:
                totalWeight = math.fsum([totalWeight, item.Item.weight])
        return round(totalWeight, 1)
    else:
        return 0.0

def checkLoad():
    load = getAllWeights(player)
    if load > player.Player.maxWeight:
        burdened = Buff('burdened', colors.yellow, 99999, showCooldown=False, resistible = False)
        burdened.applyBuff(player)
    if load <= player.Player.maxWeight and 'burdened' in convertBuffsToNames(player.Fighter):
        for buff in player.Fighter.buffList:
            if buff.name == 'burdened':
                buff.removeBuff()

def lootItem(object, x, y):
    objects.append(object)
    object.x = x
    object.y = y
    object.sendToBack()
    if object.Item and object.Item.amount <= 1:
        message('A ' + object.name + ' falls from the dead body!', colors.dark_sky)
    elif object.Item:
        message(str(object.Item.amount) + ' ' + object.pluralName + ' fall from the dead body!', colors.dark_sky)
    else:
        message('A ' + object.name + ' falls from the dead body!', colors.dark_sky)

def turnIntoNemesis():
    global lastHitter, nemesisList
    nemesis = None
    if lastHitter == 'darksoul':
        fightComp = Fighter(hp=60, armor=1, power=7, accuracy=50, evasion=15, xp=70, deathFunction=monsterDeath, armorPenetration=3, lootFunction=[], lootRate=[])
        objComp = GameObject(0, 0, 'P', nameGen.nemesisName(race = player.Player.race, classe = player.Player.classes), color = colors.light_gray, blocks=True, Fighter=fightComp, AI = BasicMonster())
        for equipment in equipmentList:
            if randint(1, 100) <= 60 and not equipment.Equipment.ranged:
                equipment.Equipment.equip(objComp.Fighter)
                objComp.Fighter.lootFunction.append(equipment)
                objComp.Fighter.lootRate.append(60)
                print('nemesis equipped ' + equipment.name)
        nemesis = Nemesis(objComp, currentBranch.shortName, branchLevel)
        print('created', objComp.name)
    if lastHitter == 'cultist':
        '''
        robeEquipment = Equipment(slot = 'torso', type = 'light armor', maxHP_Bonus = 5, maxMP_Bonus = 25)
        robe = GameObject(0, 0, '[', 'high cultist robe', colors.purple, Equipment = robeEquipment, Item=Item(weight = 1.5, pic = 'cultistRobe.xp'))
        
        flailEquipment = Equipment(slot = 'one handed', type = 'heavy weapon', powerBonus = 13, meleeWeapon = True)
        flail = GameObject(0, 0, '/', 'bloodsteel flail', colors.red, Equipment=flailEquipment, Item=Item(weight=5.5, pic = 'bloodsteelFlail.xp', description = "A heavy flail wielded by the high cultists and made of a heavy, blood-red metal."))
        
        spellbook = GameObject(x, y, '=', 'spellbook of arcane rituals', colors.violet, Item = Item(useFunction = learnSpell, arg1 = darkPact, weight = 1.0, description = "A spellbook full of arcane rituals and occult incantations. Such magic is easy to learn and to use, but comes at a great price.", pic = 'spellbook.xp'), blocks = False)
        '''
        fightComp = Fighter(hp=40, armor=2, power=13, accuracy=30, evasion=30, xp=80, deathFunction=monsterDeath, lootFunction=[], lootRate=[])
        objComp = GameObject(0, 0, 'C', nameGen.nemesisName(race = player.Player.race, classe = player.Player.classes), color = colors.dark_red, blocks=True, Fighter=fightComp, AI = BasicMonster())
        for equipment in equipmentList:
            if randint(1, 100) <= 60 and not equipment.Equipment.ranged:
                equipment.Equipment.equip(objComp.Fighter)
                objComp.Fighter.lootFunction.append(equipment)
                objComp.Fighter.lootRate.append(60)
                print('nemesis equipped ' + equipment.name)
        nemesis = Nemesis(objComp, currentBranch.shortName, branchLevel)
        print('created', objComp.name)
        
    if nemesis is not None:
        nemesisList.append(nemesis)
        print('added nemesis to list')
    
    found = checkFile('meta.bak', absMetaDirPath)

    if not found:
        file = shelve.open(absMetaPath, "c")
        print('found no nemesis file')
    else:
        print('found nemesis file')
        file = shelve.open(absMetaPath, "w")
    file['nemesis'] = nemesisList
    file.close()

class HighScore:
    def __init__(self, name, race, pClass, level, dLevel, dBranch, killer, score):
        self.name = name
        self.race = race
        self.pClass = pClass
        self.level = level
        self.dLevel = dLevel
        self.dBranch = dBranch
        self.killer = killer
        self.score = score
    
    def __lt__(self, other):
        return self.score < other.score
    def __le__(self, other):
        return self.score <= other.score
    def __eq__(self, other):
        return self.score == other.score
    def __ge__(self, other):
        return self.score >= other.score
    def __gt__(self, other):
        return self.score > other.score
    def __ne__(self, other):
        return self.score != other.score
    

    def sName(self):
        text = '{} the level {} {} {}'.format(self.name, self.level, self.race, self.pClass)
        return text

    def sDeath(self):
        text = 'Died on level {} of branch {} killed by {}'.format(self.dLevel, self.dBranch, self.killer)
        return text
    def sScore(self):
        text = 'Scored {} points'.format(self.score)
        return text
    
def placeScore(current, first = True):
    file = shelve.open(absMetaPath, "c")
    try:
        scoreList = file['scores']
    except KeyError:
        print("========WARNING========")
        print('No highscore in file')
        print("=======================")
        scoreList = []
    '''    
    for loop in range(5):
        if loop + 1:
            high = deepcopy(scoreList[loop])
        else:
            print('Score list shorter than {} ({})'.format(loop, len(scoreList)))
            scoreList.append(current)
            print('Appended score')
            file['scores'] = scoreList
            file.close()
            print('Saved score list')
            return 'short'
        print(high.name, high.score)
        if current > high:
            prevInd = loop
            scoreList[prevInd] = current
            print('Replaced score number {} (points : {}) by new high score ({})'.format(prevInd, high.score, current.score))
            placeScore(high, False)
            #nudgeDown(high, prevInd)
            print('After nudging')
            file['scores'] = scoreList
            file.close()
            print('Saved score list')
            return 'done'
    print("Couldn't place score {}".format(current.score))
    return 'tooLow'
    '''
    scoreList.append(current)
    scoreList.sort()
    scoreList.reverse()
    if len(scoreList) > 5:
        del scoreList[5]
    file['scores'] = scoreList
    file.close()
    print('Saved score list')
    return 'done'
    

def nudgeDown(score, curIndex):
    file = shelve.open(absMetaPath, "c")
    try:
        scoreList = file['scores']
    except KeyError:
        print("========WARNING========")
        print('No highscore in file')
        print("Couldnt nudge")
        print("=======================")
        return 'fail'
    normal = curIndex
    lower = curIndex + 1
    print('Starting nudging')
    if not lower > 5:
        print('Entering nudging if loop')
        if lower > len(scoreList) - 1:
            print('Need to append score !')
            leaderboard()
            print('Lower = {}'.format(lower))
            print('Max Ind = {}'.format(len(scoreList) - 1))
            scoreList.append(score)
            file['scores'] = scoreList
            print('BEFORE SYNCING')
            file.sync()
            print('Saved nudging down')
            file.close()
        else:
            print('No need to append')
            print(scoreList[lower])
            previous = deepcopy(scoreList[lower])
            print('Done deepcopying')
            scoreList[lower] = score
            print('Nudged down score {} to {}'.format(normal, lower))
            file['scores'] = scoreList
            print('BEFORE SYNCING')
            file.sync()
            print('Saved nudging down')
            file.close()
            nudgeDown(previous, lower)
        
    else:
        print('Done nudging down')
    

def getHighScore():
    def computeHighScore():
        return player.Player.baseScore + round(player.Player.money / 10)
    
    curHigh = HighScore(player.name, player.Player.race, player.Player.classes, player.level, branchLevel, currentBranch.name, lastHitter, computeHighScore())
    '''
    file = shelve.open(absMetaPath, "c")
    try:
        scoreList = file['scores']
        for high in scoreList:
            print(high.name, high.score)
            if curHigh > high:
                prevInd = scoreList.index(high)
                scoreList[prevInd] = curHigh
                inserted = True
                print('Replaced score number {} (points : {}) by new high score ({})'.format(prevInd, high.score, curHigh.score))
                break
    except KeyError:
        print("========WARNING========")
        print('No highscore in file')
        print("=======================")
        scoreList = []
    '''
    status = placeScore(curHigh)
    print(status)
    '''
    if len(scoreList) <= 5 and status != 'done':
        scoreList.append(curHigh)
        inserted = True
        print('Appended score')
    file['scores'] = scoreList
    file.close()
    '''

def playerDeath(player):
    global gameState
    if player.Player.race == 'Virus ' and player.Player.inHost:
        player.Player.inHost = False
        player.Player.timeOutsideLeft = 50
        setFighterStatsBack(player.Fighter)
        player.Fighter.hp = player.Fighter.BASE_MAX_HP
        message('Your host was killed!', colors.red)
    else:
        message('You died!', colors.red)
        gameState = 'dead'
        player.char = '%'
        player.color = colors.dark_red
        turnIntoNemesis()
        getHighScore()
        deleteSaves()
        deathMenu()

    
def monsterDeath(monster, alreadyDropped = False):
    #try:
    if monster.Fighter and not alreadyDropped:
        message(monster.name.capitalize() + ' is dead! You gain ' + str(monster.Fighter.xp) + ' XP.', colors.dark_sky) #TO-DO (PRIORITY) : Fix it so it shows only if you actually gained XP on kill
        if monster.Fighter.lootFunction is not None:
            itemIndex = 0
            for item in monster.Fighter.lootFunction:
                loot = randint(1, 100)
                if loot <= monster.Fighter.lootRate[itemIndex]:
                    lootItem(item, monster.x, monster.y)
                itemIndex += 1
    #except:
    #    pass
    monster.char = '%'
    monster.color = colors.dark_red
    monster.blocks = False
    monster.AI = None
    monster.trueName = 'remains of ' + monster.name
    monster.Fighter = None
    monster.sendToBack()
    if monster.owner and not alreadyDropped:
        monsterDeath(monster.owner, True)
        for monsterPart in monster.owner.sizeComponents:
            if monsterPart != monster:
                monsterDeath(monsterPart, True)
    if monster.sizeComponents:
        for monsterPart in monster.sizeComponents:
            monsterDeath(monsterPart, True)
        

def zombieDeath(monster):
    global objects
    message(monster.name.capitalize() + ' is destroyed !')
    objects.remove(monster)
    monster.char = ''
    monster.color = Ellipsis
    monster.blocks = False
    monster.AI = None
    monster.trueName = None
    monster.Fighter = None

#_____________ GUI _______________
def renderBar(cons, x, y, totalWidth, name, value, maximum, barColor, backColor, textColor = colors.white):
    if maximum == 0:
        trueMax = 1
        alwaysFull = True
    else:
        trueMax = maximum
        alwaysFull = False
    barWidth = round(float(value) / trueMax * totalWidth) #Width of the bar is proportional to the ratio of the current value over the maximum value
    cons.draw_rect(x + 1, y, totalWidth, 1, None, bg = backColor)#Background of the bar
    
    if barWidth > 0 and not alwaysFull:
        cons.draw_rect(x + 1, y, barWidth, 1, None, bg = barColor)#The actual bar
    elif alwaysFull:
        cons.draw_rect(x + 1, y, totalWidth, 1, None, bg = barColor)
    
    fg = backColor
    if barWidth == totalWidth or alwaysFull:
        fg = barColor
    cons.draw_char(x + totalWidth + 1, y, chr(180), fg = fg)
    
    fg = barColor
    if barWidth == 0 and not alwaysFull:
        fg = backColor
    cons.draw_char(x, y, chr(195), fg = fg)
        
    text = name + ': ' + str(value) + '/' + str(maximum)
    xCentered = x + 1 + (totalWidth - len(text))//2
    cons.draw_str(xCentered, y, text, fg = textColor, bg=None)

def displayLog(height):
    global menuWindows, FOV_recompute
    noStartMsg = True
    quitted = False
    if menuWindows:
        for mWindow in menuWindows:
            mWindow.clear()
        FOV_recompute = True
        #Update()
        tdl.flush()
    width = MSG_WIDTH + 2
    window = NamedConsole('displayLog', width, height)
    menuWindows.append(window)
    upKeys = ['UP', 'KP8', 'PAGEUP', '^']
    downKeys = ['DOWN', 'KP2', 'PAGEDOWN', 'V']
    exitKeys = ['SPACE', 'ENTER', 'ESCAPE']
    while not quitted:
        window.clear()
        window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)    
        
        for k in range(width):
            window.draw_char(k, 0, chr(196))
        window.draw_char(0, 0, chr(218))
        window.draw_char(k, 0, chr(191))
        kMax = k
        for l in range(height):
            if l > 0:
                window.draw_char(0, l, chr(179))
                window.draw_char(kMax, l, chr(179))
        lMax = l
        for m in range(width):
            window.draw_char(m, lMax, chr(196))
        window.draw_char(0, lMax, chr(192))
        window.draw_char(kMax, lMax, chr(217))
        
        if len(logMsgs) == 0:
            pass
        else:
            lastMsgIndex = len(logMsgs) - 1
            displayableHeight = height - 3
            if noStartMsg:
                if lastMsgIndex - displayableHeight <= 0:
                    startMsg = 0
                    curStartIndex = int(startMsg)
                else:
                    startMsg = lastMsgIndex - displayableHeight
                    curStartIndex = int(startMsg)
                noStartMsg = False
                print('Log start : ' + str(curStartIndex))
            if curStartIndex + displayableHeight < lastMsgIndex:
                lastDisplayedMessage = curStartIndex + displayableHeight
                print('Log end : ' + str(lastDisplayedMessage))
            else:
                lastDisplayedMessage = int(lastMsgIndex)
            y = 1
            print('curStartIndex at displaying : ' + str(curStartIndex))
            for curIndex in range(curStartIndex, lastDisplayedMessage + 1):
                msgX = 1
                for (text, color) in logMsgs[curIndex]:
                    window.draw_str(msgX, y, text, bg=None, fg = color)
                    msgX += len(text)
                y += 1
                #(line, color) = logMsgs[curIndex]
                #window.draw_str(1, y, line, fg = color, bg = Ellipsis)
                #y += 1
            
            if curStartIndex > 0:
                window.draw_char(kMax, 1, chr(24), fg = colors.black, bg = colors.amber)
            if curStartIndex + displayableHeight < lastMsgIndex:
                window.draw_char(kMax, lMax - 1, chr(25), fg = colors.black, bg = colors.amber)
        windowX = MID_WIDTH - int(width/2)
        windowY = MID_HEIGHT - int(height/2)
        root.blit(window, windowX, windowY, width, height, 0, 0)
    
        tdl.flush()
        key = tdl.event.key_wait()
        if key.keychar.upper() in upKeys:
            if curStartIndex > 0:
                print('curStartIndex before : ' + str(curStartIndex))
                curStartIndex -= 1
                print('curStartIndex after : ' + str(curStartIndex))
        elif key.keychar.upper() in downKeys:
            if curStartIndex + displayableHeight < lastMsgIndex:
                curStartIndex += 1
        elif key.keychar.upper() in exitKeys:
            quitted = True

def loadMap(level, branch):
    branchKey = branch.shortName + str(level)
    stairKey = branchKey + 'stairs'
    print(branchKey, stairKey)
    try:
        return exploredMaps[branchKey], exploredMaps[stairKey]
    except:
        print('branch isnt explored')
        return 'branch not explored'

def displayMap():
    global menuWindows, FOV_recompute
    quitted = False
    if menuWindows:
        for mWindow in menuWindows:
            mWindow.clear()
        FOV_recompute = True
        #Update()
        tdl.flush()
    width = MAP_WIDTH + 4
    height = MAP_HEIGHT + 5
    window = NamedConsole('displayMap', width, height)
    menuWindows.append(window)
    
    borderHoles = []
    displayedLevel = branchLevel
    displayedBranch = currentBranch
    
    for k in range(width):
        hole = randint(0, 4)
        if hole == 0:
            borderHoles.append((k, 0))
        hole = randint(0, 4)
        if hole == 0:
            borderHoles.append((k, height-1))
    for l in range(height):
        hole = randint(0, 4)
        if hole == 0:
            borderHoles.append((0, l))
        hole = randint(0, 4)
        if hole == 0:
            borderHoles.append((width - 1, l))
    
    while not quitted:
        possibleBranches = []
        if displayedBranch.origBranch and displayedBranch.origDepth:
            possibleBranches.append((displayedBranch.origBranch, displayedBranch.origDepth))
        for branch, lvl in displayedBranch.branchesTo:
            if lvl == displayedLevel:
                print(branch.name, 'is possible')
                possibleBranches.append((branch, 1))
                    
        window.clear()
        window.draw_rect(0, 0, width, height, None, fg=colors.sepia, bg=colors.light_sepia)
        
        for k in range(width):
            if (k, 0) in borderHoles:
                window.draw_char(k, 0, None, bg = Ellipsis)
            if (k, height - 1) in borderHoles:
                window.draw_char(k, height-1, None, bg = Ellipsis)
        for l in range(height):
            if (0, l) in borderHoles:
                window.draw_char(0, l, None, bg = Ellipsis)
            if (width-1, l) in borderHoles:
                window.draw_char(width-1, l, None, bg = Ellipsis)
        
        window.draw_str(3, 2, displayedBranch.name + ': ' + str(displayedLevel), fg = colors.darker_sepia, bg = colors.light_sepia)
        
        '''
        if displayedLevel == branchLevel and displayedBranch == currentBranch:
            mapToDisplay = myMap
            stairList = curStairList
        else:
            mapToDisplay, stairList = loadMap(displayedLevel, displayedBranch)
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if mapToDisplay[x][y].explored:
                    char = None
                    fg = colors.sepia
                    bg = colors.light_sepia
                    if mapToDisplay[x][y].blocked or mapToDisplay[x][y].character == '#':
                        char = mapToDisplay[x][y].character
                    elif mapToDisplay[x][y].chasm:
                        bg = colors.dark_sepia
                    else:
                        bg = colors.lighter_sepia
                    window.draw_char(x + 2, y + 3, char, fg, bg)
        for stair in stairList:
            if mapToDisplay[stair.x][stair.y].explored:
                window.draw_char(stair.x + 2, stair.y + 3, stair.char, fg = stair.color, bg = colors.lighter_sepia)
        '''
        
        mapToDisplay, stairList = loadMap(displayedLevel, displayedBranch)
        for x, y, character, blocked, chasm in mapToDisplay:
            char = None
            fg = colors.sepia
            bg = colors.light_sepia
            if blocked or character == '#':
                char = character
            elif chasm:
                bg = colors.dark_sepia
            else:
                bg = colors.lighter_sepia
            window.draw_char(x + 2, y + 3, char, fg, bg)
        
        if stairList:
            for x, y, char, color in stairList:
                print(x, y, char, color)
                window.draw_char(x + 2, y + 3, char, fg = color, bg = colors.lighter_sepia)
            
        
        windowX = MID_WIDTH - int(width/2)
        windowY = MID_HEIGHT - int(height/2)
        root.blit(window, windowX, windowY, width, height, 0, 0)
    
        tdl.flush()
        key = tdl.event.key_wait()
        print(displayedLevel)
        print(key.keychar.upper())
        if key.keychar.upper() == 'UP':
            print('loading above level')
            displayedLevel -= 1
            if loadMap(displayedLevel, displayedBranch) == 'branch not explored':
                displayedLevel += 1
        elif key.keychar.upper() == 'DOWN':
            print('loading below level')
            displayedLevel += 1
            if loadMap(displayedLevel, displayedBranch) == 'branch not explored':
                displayedLevel -= 1
        elif key.keychar.upper() == 'LEFT':
            tryBranch, tryLvl = possibleBranches[0]
            print('loading left level:', tryBranch.name)
            if loadMap(tryLvl, tryBranch) != 'branch not explored':
                displayedLevel = tryLvl
                displayedBranch = tryBranch
        elif key.keychar.upper() == 'RIGHT' and len(possibleBranches) > 1:
            tryBranch, tryLvl = possibleBranches[1]
            print('loading right level:', tryBranch.name)
            if loadMap(tryLvl, tryBranch) != 'branch not explored':
                displayedLevel = tryLvl
                displayedBranch = tryBranch
        elif key.keychar.upper() == 'ESCAPE':
            quitted = True

def inventoryMenu(header, invList = None, noItemMessage = 'Inventory is empty'):
    #show a menu with each item of the inventory as an option
    global inventory
    displayItem = True
    if not player.Fighter.canTakeTurn:
        message('You cannot check your inventory right now !', colors.red)
        return None
    else:
        if invList is None:
            invList = inventory
        elif invList == 'food':
            invList = [object for object in inventory if object.Item and object.Item.type == "food"]
        if len(invList) == 0:
            options = [noItemMessage]
            displayItem = False
        else:
            options = []
            for item in invList:
                text = item.name
                if item.Item.stackable:
                    text = text + ' (' + str(item.Item.amount) + ')'
                if item.Equipment and item.Equipment.type:
                    eqType = item.Equipment.type
                    if 'junk' in eqType:
                        optionColor = itemGen.junk.color
                    elif 'uncommon' in eqType:
                        optionColor = itemGen.uncommon.color
                    elif 'common' in eqType:
                        optionColor = itemGen.common.color
                    elif 'rare' in eqType:
                        optionColor = itemGen.rare.color
                    elif 'epic' in eqType:
                        optionColor = itemGen.epic.color
                    elif 'legendary' in eqType:
                        optionColor = itemGen.legendary.color
                    else:
                        optionColor = colors.white
                else:
                    optionColor = colors.white
                options.append((text, optionColor))
        index = colorMenu(header, options, INVENTORY_WIDTH, invList, noItemMessage, displayItem=displayItem, name = 'inventory')
        if index is None or len(invList) == 0 or index == "cancelled":
            return None
        else:
            return invList[index].Item

def sortSpells(spellsToSort):
    kSpells = spellsToSort
    spellNames = []
    spellNamesOrdered = []
    spellsOrdered = []
    for spell in kSpells:
        spellNames.append(spell.name)
        spellNamesOrdered.append(spell.name)
    spellNamesOrdered.sort()
    for i in spellNamesOrdered:
        unorderedIndex = spellNames.index(i)
        spellsOrdered.append(kSpells[unorderedIndex])
    return spellsOrdered
        
def spellMenu(header):
    '''
    Alias for spellsMenu. Mainly used for when Edern wants to CTRL-F this function but forgets whether or not he wrote spells in plural in the function name.
    '''
    return spellsMenu(header)

def spellsMenu(header):
    '''
    Shows a menu with each known ready spell as an option
    '''
    borked = False
    if len(player.Fighter.knownSpells) == 0:
        options = ["You don't have any spells ready right now"]
    else:
        player.Fighter.knownSpells = sortSpells(player.Fighter.knownSpells)
        options = []
        try:
            for spell in player.Fighter.knownSpells:
                text = spell.name
                options.append(text)
        except TDLError:
            options = []
            borked = True
    index = menu(header, options, SPELLS_MENU_WIDTH, noItemMessage="You don't have any spells ready right now", usedList = player.Fighter.knownSpells, displayItem = True, itemDisplayed = 'spell', name = 'spellMenu')#, switchKey = "?", switchHeader = "Select a spell to get information on (press ? to switch to cast mode)")
    #add 'switch' after index if needed
    if index is None or len(player.Fighter.knownSpells) == 0 or borked or index == "cancelled":
        global DEBUG
        if DEBUG:
            message('No spell selected in menu', colors.purple)
        return (None, False)
    else:
        return (player.Fighter.knownSpells[index], False) #, switch)


def equipmentMenu(header):
    if not player.Fighter.canTakeTurn:
        message("You cannot change your equipment right now !")
    else:
        if len(equipmentList) == 0:
            options = ['You have nothing equipped']
        else:
            options = []
            for item in equipmentList:
                text = item.name
                if item.Equipment and item.Equipment.isEquipped:
                    if item.Equipment.type:
                        eqType = item.Equipment.type
                        if 'junk' in eqType:
                            optionColor = itemGen.junk.color
                        elif 'uncommon' in eqType:
                            optionColor = itemGen.uncommon.color
                        elif 'common' in eqType:
                            optionColor = itemGen.common.color
                        elif 'rare' in eqType:
                            optionColor = itemGen.rare.color
                        elif 'epic' in eqType:
                            optionColor = itemGen.epic.color
                        elif 'legendary' in eqType:
                            optionColor = itemGen.legendary.color
                        else:
                            optionColor = colors.white
                    else:
                        optionColor = colors.white
                    #powBonus = item.Equipment.basePowerBonus
                    #skillPowBonus = item.Equipment.powerBonus - powBonus
                    #hpBonus = item.Equipment.maxHP_Bonus
                    #armBonus = item.Equipment.armorBonus
                    #if powBonus != 0 or hpBonus !=0 or armBonus != 0:
                    #    info = '['
                    #    if powBonus != 0:
                    #        info = info + 'POWER + ' + str(powBonus)
                    #        if skillPowBonus > 0:
                    #            info += ' + ' + str(skillPowBonus)
                    #    if hpBonus != 0:
                    #        if powBonus == 0:
                    #            info = info + 'HP + ' + str(hpBonus)
                    #        else:
                    #            info = info + ' HP + ' + str(hpBonus)
                    #    if armBonus != 0:
                    #        if powBonus == 0 and hpBonus == 0:
                    #            info = info + 'ARMOR + ' + str(armBonus)
                    #        else:
                    #            info = info + ' ARMOR + ' + str(armBonus)
                    #    info = info + ']'
                    #else:
                    #    info = ''
                    handed = item.Equipment.slot == 'one handed' or item.Equipment.slot == 'two handed'
                    if handed:
                        text = text + ' (on ' + item.Equipment.curSlot + ')'
                    else:
                        text = text + ' (on ' + item.Equipment.slot + ')'
                options.append((text, optionColor))
        index = colorMenu(header, options, INVENTORY_WIDTH, equipmentList, noItemMessage='You have nothing equipped', displayItem=True)
        if index is None or len(equipmentList) == 0 or index == "cancelled":
            return None
        else:
            return equipmentList[index].Item

def deathMenu():
    global FOV_recompute
    FOV_recompute = True
    Update()
    deathText = textwrap.wrap('You were killed by ' + lastHitter + '.', DEATH_SCREEN_WIDTH)
    width = DEATH_SCREEN_WIDTH + 2
    height = DEATH_SCREEN_HEIGHT + len(deathText)
    window = NamedConsole('deathMenu', width, height)
    window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)
    window.clear()
    index = 0

    while True: #not tdl.event.isWindowClosed():
        for k in range(width):
            window.draw_char(k, 0, chr(196))
        window.draw_char(0, 0, chr(218))
        window.draw_char(k, 0, chr(191))
        kMax = k
        for l in range(height):
            if l > 0:
                window.draw_char(0, l, chr(179))
                window.draw_char(kMax, l, chr(179))
        lMax = l
        for m in range(width):
            window.draw_char(m, lMax, chr(196))
        window.draw_char(0, lMax, chr(192))
        window.draw_char(kMax, lMax, chr(217))
        window.draw_str(8, 1, 'YOU DIED!', colors.red)
        y = 3
        for line in deathText:
            window.draw_str(1, y, line, fg = colors.amber)
            y += 1
        if index == 0:
            window.draw_str(7, y + 2, 'Main menu', fg = colors.black, bg = colors.white)
            window.draw_str(7, y + 4, 'Quit')
        else:
            window.draw_str(7, y + 2, 'Main menu')
            window.draw_str(7, y + 4, 'Quit', fg = colors.black, bg = colors.white)

        x = MID_WIDTH - int(width/2)
        y = MID_HEIGHT - int(height/2)
        root.blit(window, x, y, width, height, 0, 0)
        tdl.flush()
        
        key = tdl.event.key_wait()
        keyChar = key.keychar
        if tdl.event.isWindowClosed():
            quitGame("Closed game")
        if key.keychar.upper() == 'DOWN':
            index += 1
        if key.keychar.upper() == 'UP':
            index -= 1
        if index <= 0:
            index = 0
        if index > 1:
            index = 1

        if keyChar == 'ENTER':
            if index == 0:
                mainMenu()
            else:
                stopProcess()
                quitGame('Quit game from the death menu.')

def drawActualRectangle(window, width, height):
        for k in range(width):
            window.draw_char(k, 0, chr(196))
        window.draw_char(0, 0, chr(218))
        window.draw_char(k, 0, chr(191))
        kMax = k
        for l in range(height):
            if l > 0:
                window.draw_char(0, l, chr(179))
                window.draw_char(kMax, l, chr(179))
        lMax = l
        for m in range(width):
            window.draw_char(m, lMax, chr(196))
        window.draw_char(0, lMax, chr(192))
        window.draw_char(kMax, lMax, chr(217))

def temporaryBox(text, color = colors.white):
    global FOV_recompute
    FOV_recompute = True
    Update()
    width = len(text) + 2
    height = 3
    window = NamedConsole('temporaryBox', width, height)
    assert isinstance(window, tdl.Console)
    
    window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)
    window.clear()
    
    for k in range(width):
        window.draw_char(k, 0, chr(196))
    window.draw_char(0, 0, chr(218))
    window.draw_char(k, 0, chr(191))
    kMax = k
    for l in range(height):
        if l > 0:
            window.draw_char(0, l, chr(179))
            window.draw_char(kMax, l, chr(179))
    lMax = l
    for m in range(width):
        window.draw_char(m, lMax, chr(196))
    window.draw_char(0, lMax, chr(192))
    window.draw_char(kMax, lMax, chr(217))
    
    window.draw_str(1, 1, text, fg = color)
    x = MID_WIDTH - int(width/2)
    y = MID_HEIGHT - int(height/2)
    root.blit(window, x, y, width, height, 0, 0)
    tdl.flush()
    
def controlBox():
    global FOV_recompute
    FOV_recompute = True
    #Update()
    width = 45
    height = 33
    window = NamedConsole('controlBox', width, height)
    assert isinstance(window, tdl.Console)
    
    window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)
    window.clear()
    
    for k in range(width):
        window.draw_char(k, 0, chr(196))
    window.draw_char(0, 0, chr(218))
    window.draw_char(k, 0, chr(191))
    kMax = k
    for l in range(height):
        if l > 0:
            window.draw_char(0, l, chr(179))
            window.draw_char(kMax, l, chr(179))
    lMax = l
    for m in range(width):
        window.draw_char(m, lMax, chr(196))
    window.draw_char(0, lMax, chr(192))
    window.draw_char(kMax, lMax, chr(217))
    
    def displayControl(x, y, control, description):
        formattedControl = control + ' : '
        window.draw_str(x, y, formattedControl, fg = colors.green)
        ty = y + len(control)
        window.draw_str(x + len(formattedControl), y, description, fg = colors.white)
        
    displayControl(1, 1, 'Arrow keys / Numpad', 'Move / Attack')
    displayControl(1, 3, 'x', 'Fire ranged weapon')
    displayControl(1, 5, 'z', 'Use spells or abilities')
    displayControl(1, 7, 'I', 'Open inventory')
    displayControl(1, 9, 'E', 'Open equipment menu')
    displayControl(1, 11, 'd', 'Drop objects')
    displayControl(1, 13, 'e', 'Open eat menu')
    displayControl(1, 15, 'Space', 'Pick up object')
    displayControl(1, 17, 'c', 'Chat with NPC')
    displayControl(1, 19, 'C', 'Display character informations')
    displayControl(1, 21, 's', 'Open skills and level up menu')
    displayControl(1, 23, 'l', 'Enter look mode')
    displayControl(1, 25, 'L', 'Display message log')
    displayControl(1, 27, 'Tab', 'Circle through side panel informations')
    displayControl(1, 29, '>', 'Climb up stairs')
    displayControl(1, 31, '<', 'Climb down stairs')
    x = MID_WIDTH - int(width/2)
    y = MID_CON_HEIGHT - int(height/2)
    root.blit(window, x, y, width, height, 0, 0)
    tdl.flush()
    tdl.event.key_wait()

def launchTutorial(prologueEsc = True):
    global player
    showPrologue(prologueEsc)
    
    '''
    light = Trait('Light weapons', '+20% damage per skillpoints with light weapons', type = 'skill', selectable = False, tier = 3)
    heavy = Trait('Heavy weapons', '+20% damage per skillpoints with heavy weapons', type = 'skill', selectable = False, tier = 3)
    missile = Trait('Missile weapons', '+20% damage per skillpoints with missile weapons', type = 'skill', selectable = False, tier = 3)
    shield = Trait('Shield mastery', 'You trained to master shield wielding.', type = 'skill', selectable = False, tier = 3)
    armorEff = Trait('Armor efficiency', 'You know very well how to maximize the protection brought by your armor', type = 'skill', selectable = False, tier = 3)
    melee = Trait('Melee Weaponry', 'You are trained to wreck your enemies at close range.', type = 'skill', selectable = False, tier = 2, allowsSelection=[light, heavy])
    ranged = Trait('Ranged Weaponry', 'You shoot people in the knees.', type = 'skill', selectable = False, tier = 2, allowsSelection=[missile])
    armorW = Trait('Armor wearing', 'You are trained to wear several types of armor.', type = 'skill', selectable = False, tier = 2, allowsSelection=[armorEff, shield])
    martial = Trait('Martial training', 'You are trained to use a wide variety of weapons', type = 'skill', acc=(10, 0), allowsSelection=[melee, ranged, armorW])
    aggressive = Trait('Aggressive', 'You angry', type = 'trait', selectable=False, selected = False)
    traits = [martial, melee, ranged, armorW, light, heavy, missile, shield, armorEff, aggressive]
    
    def initiateSkill(skillList, maxHeight, heightCounter, originY = 0):
        newHeight = maxHeight//len(skillList)
        mid = newHeight//2
        counter = 0
        for skill in skillList:
            skill.x = skill.tier * quarterX
            skill.y = mid + counter * newHeight + heightCounter * maxHeight + originY
            print(skill.name, skill.tier, len(skill.allowsSelection), skill.x, skill.y)
            if skill.allowsSelection and len(skill.allowsSelection) > 0:
                print('initiating selectable skills of ' + skill.name)
                initiateSkill(skill.allowsSelection, newHeight, counter, maxHeight * heightCounter + originY)
            counter += 1
    
    
    newHeight = 76
    mid = newHeight//2
    counter = 0
    quarterX = (WIDTH - 2)//5
    for skill in traits:
        if skill.tier == 1:
            skill.x = quarterX
            skill.y = mid + newHeight * counter
            print(skill.name, skill.tier, len(skill.allowsSelection), skill.x, skill.y)
            if skill.allowsSelection and len(skill.allowsSelection) > 0:
                print('initiating selectable skills of ' + skill.name)
                initiateSkill(skill.allowsSelection, newHeight, counter)
            counter += 1
    '''
    
    allTraits, leftTraits, rightTraits, races, attributes, skills, classes, traits, human, unlockableTraits = initializeTraits() #skilled, human, unlockableTraits = initializeTraits()
    toUpTraits = ['Muscular', 'Skilled', 'Tough', 'Knight', 'Human', 'Martial training', 'Physical training', 'Mental training', 'Magic ', 'Melee weaponry']
    
    allTraits.extend(skills)
    for trait in allTraits:
        print(trait.name, trait.type)
        if trait.name in toUpTraits:
            trait.selected = True
            trait.amount = 1
            for newTrait in trait.allowsSelection:
                newTrait.selectable = True
        elif (trait.name == 'Strength' or trait.name == 'Constitution') and trait.type == 'attribute':
            trait.selected = True
            trait.amount = 5
            for newTrait in trait.allowsSelection:
                newTrait.selectable = True
        elif (trait.name == 'Willpower' or trait.name == 'Dexterity') and trait.type == 'attribute': 
            trait.selected = True
            trait.amount = 2
            for newTrait in trait.allowsSelection:
                newTrait.selectable = True

    LvlUp = {'power': 1, 'acc': 10, 'ev': 0, 'arm': 1, 'hp': 14, 'mp': 3, 'crit': 0, 'stren': 0, 'dex': 0, 'vit': 0, 'will': 0, 'ap': 0, 'stamina': 0}
    playerComp = Player('Angus McFife', 5, 2, 5, 2, 45.0, 'Human', 'Knight', allTraits, LvlUp, unlockableTraits=unlockableTraits
                        
                        )
    fighterComp = Fighter(hp = 160, power= 1, armor= 1, deathFunction=playerDeath, xp=0, evasion = 0, accuracy = 30, maxMP= 30, critical = 5)
    player = GameObject(MAP_WIDTH - 2, MID_MAP_HEIGHT, '@', Fighter = fighterComp, Player = playerComp, name = 'Angus McFife', color = (0, 210, 0))
    player.level = 1
    player.Fighter.hp = player.Fighter.baseMaxHP
    player.Fighter.MP = player.Fighter.baseMaxMP
    player.Fighter.stamina = player.Fighter.maxStamina
    makeTutorialMap(1)
    playTutorial()

def openOptions():
    width, height = 30, 10
    window = tdl.Console(width, height)
    soundState = readOptions()
    index = 0
    subIndex = 0
    isInMainChoice = True
    SELECTED_COLOR = colors.white
    UNSELECTED_COLOR = colors.light_gray
    BASE_X = 2
    BASE_Y = 2
    APPLY_Y = 7
    while True:
        window.clear()
        drawActualRectangle(window, width, height)

        if index == 0 and isInMainChoice:
            window.draw_str(BASE_X, BASE_Y, "Enable SFX :", fg = colors.black, bg = colors.white)
        else:
            window.draw_str(BASE_X, BASE_Y, "Enable SFX :")
        
        if not isInMainChoice:
            if subIndex == 0:
                window.draw_str(BASE_X + 13, BASE_Y, "ON", fg = colors.black, bg= colors.white)
                if not soundState:
                    window.draw_str(BASE_X + 16, BASE_Y, "OFF", fg = SELECTED_COLOR)
                else:
                    window.draw_str(BASE_X + 16, BASE_Y, "OFF", fg = UNSELECTED_COLOR)
            else:
                if soundState:
                    window.draw_str(BASE_X + 13, BASE_Y, "ON", fg = SELECTED_COLOR)
                else:
                    window.draw_str(BASE_X + 13, BASE_Y, "ON", fg = UNSELECTED_COLOR)
                window.draw_str(BASE_X + 16, BASE_Y, "OFF", fg = colors.black, bg= colors.white)
        else:
            if soundState:
                window.draw_str(BASE_X + 13, BASE_Y, "ON", fg = SELECTED_COLOR)
                window.draw_str(BASE_X + 16, BASE_Y, "OFF", fg = UNSELECTED_COLOR)
            else:
                window.draw_str(BASE_X + 13, BASE_Y, "ON", fg = UNSELECTED_COLOR)
                window.draw_str(BASE_X + 16, BASE_Y, "OFF", fg = SELECTED_COLOR)
        
        if isInMainChoice and index == 1:
            drawCenteredVariableWidth(window, y = APPLY_Y, text ="Apply changes and quit", fg = colors.black, bg = colors.white, width = width)
        else:
            drawCenteredVariableWidth(window, y = APPLY_Y, text ="Apply changes and quit", width = width)
        
        if isInMainChoice and index == 2:
            drawCenteredVariableWidth(window, y = APPLY_Y + 1 , text ="Cancel", fg = colors.black, bg = colors.white, width = width)
        else:
            drawCenteredVariableWidth(window, y = APPLY_Y + 1, text ="Cancel", width = width)
        
        root.blit(window, (WIDTH - width) // 2, (HEIGHT - height) // 2, width, height)
        tdl.flush()
        
        key = tdl.event.key_wait()
        if tdl.event.isWindowClosed():
            quitGame("Closed game", noSave = True)
        else:
            keychar = key.keychar.upper()
            if isInMainChoice:
                if keychar == "UP":
                    index -= 1
                elif keychar == "DOWN":
                    index += 1
                
                if index > 2:
                    index = 0
                if index < 0:
                    index = 2
                
                
                
                if keychar == "ESCAPE":
                    break
                elif keychar == "ENTER":
                    if index == 0:
                        isInMainChoice = False
                        subIndex = 0
                    elif index == 1:
                        writeOptions(str(soundState))
                        applyOptions()
                        break
                    elif index == 2:
                        break
                elif keychar == "RIGHT":
                    if index == 0:
                        isInMainChoice = False
                        subIndex = 0                        
            else:
                if keychar == "RIGHT":
                    subIndex += 1
                elif keychar == "LEFT":
                    subIndex -= 1
                elif keychar == "UP":
                    isInMainChoice = True
                    subIndex = 0
                    index = 2
                elif keychar == "DOWN":
                    isInMainChoice = True
                    subIndex = 0
                    index = 1
                
                if subIndex > 1:
                    subIndex = 1
                if subIndex < 0:
                    isInMainChoice = True
                    subIndex = 0
                    index = 0
                
                if keychar == "ENTER":
                    if subIndex == 0:
                        soundState = True
                    else:
                        soundState = False
                elif keychar == "ESCAPE":
                    break
                
                
        

def mainMenu():
    global myMap, player, tutorial
    def drawLogo():
        asciiFile = os.path.join(absAsciiPath, 'logo2.xp')
        xpRawString = gzip.open(asciiFile, "r").read()
        convertedString = xpRawString
        attributes = xpL.load_xp_string(convertedString)
        picHeight = int(attributes["height"])
        picWidth = int(attributes["width"])
        lData = attributes["layer_data"]
        layerInd = int(0)
        for layerInd in range(len(lData)):
            xpL.load_layer_to_console(root, lData[layerInd], WIDTH//2 - picWidth//2, 15)

            
    if (__name__ == '__main__' or __name__ == 'main__main__') and root is not None:
        global player, currentMusic, activeProcess
        choices = ['Tutorial', 'New Game', 'Continue', 'Leaderboard', 'Test Dungeon', 'About', 'Options', 'Quit']
        index = 0
        currentMusic = str('Dusty_Feelings.wav')
        stopProcess()
        print('CREATING MUSIC PROCESS')
        music = multiprocessing.Process(target = mus.runMusic, args = (currentMusic,))
        print('STARTING MUSIC PROCESS')
        music.start()
        activeProcess.append(music)
        tutorial = False
        
        while True: #not tdl.event.isWindowClosed():
            root.clear()
            drawLogo()
            for tempIndex in range(len(choices)):
                drawCentered(cons = root, y = 44 + tempIndex, text = choices[tempIndex], fg = colors.white, bg = None)
            drawCentered(cons = root, y = 44 + index, text=choices[index], fg = colors.black, bg = colors.white)
            tdl.flush()
            key = tdl.event.key_wait()
            if tdl.event.isWindowClosed():
                quitGame("Closed game", noSave = True)
            if key.keychar.upper() == "DOWN":
                index += 1
                playWavSound('selectClic.wav')
            elif key.keychar.upper() == "UP":
                index -= 1
                playWavSound('selectClic.wav')
            if index < 0:
                index = len(choices) - 1
            if index > len(choices) - 1:
                index = 0
            if key.keychar.upper() == "ENTER":
                if index == 0:
                    launchTutorial()
                elif index == 1:
                    (playerComponent, allTraits, skillpoints, unlockableTraits) = characterCreation()
                    if playerComponent != 'cancelled':
                        for trait in allTraits:
                            if trait.type == 'race' and trait.selected:
                                chosenRace = trait.name
                        for trait in allTraits:
                            if trait.type == 'class' and trait.selected:
                                chosenClass = trait.name
                        name = enterName(chosenRace)
                        LvlUp = {'power': createdCharacter['powLvl'], 'acc': createdCharacter['accLvl'], 'ev': createdCharacter['evLvl'], 'arm': createdCharacter['armLvl'], 'hp': createdCharacter['hpLvl'], 'mp': createdCharacter['mpLvl'], 'crit': createdCharacter['critLvl'], 'stren': createdCharacter['strLvl'], 'dex': createdCharacter['dexLvl'], 'vit': createdCharacter['vitLvl'], 'will': createdCharacter['willLvl'], 'ap': createdCharacter['apLvl'], 'stamina': createdCharacter['stamLvl']}
                        playComp = Player(name, playerComponent['stren'], playerComponent['dex'], playerComponent['vit'], playerComponent['will'], playerComponent['load'], chosenRace, chosenClass, allTraits, LvlUp, skillpoints=skillpoints, baseStealth=createdCharacter['stealth'], unlockableTraits=unlockableTraits)
                        playFight = Fighter(hp = playerComponent['hp'], power= playerComponent['power'], armor= playerComponent['arm'], deathFunction=playerDeath, xp=0, evasion = playerComponent['ev'], accuracy = playerComponent['acc'], maxMP= playerComponent['mp'], knownSpells=playerComponent['spells'], critical = playerComponent['crit'], armorPenetration = playerComponent['ap'], stamina=createdCharacter['stamina'])
                        player = GameObject(25, 23, '@', Fighter = playFight, Player = playComp, name = name, color = (0, 210, 0))
                        player.level = 1
                        player.Fighter.hp = player.Fighter.baseMaxHP
                        player.Fighter.MP = player.Fighter.baseMaxMP
                        player.Fighter.stamina = player.Fighter.maxStamina
    
                        newGame()
                        playGame()
                    else:
                        mainMenu()
                elif index == 2:
                    error = False
                    try:
                        loadGame()
                    except:
                        msgBox("\n No saved game to load.\n", 26, False, False)
                        error = True
                        key = None
                        continue
                    if not error:
                        playGame()
                elif index == 3:
                    leaderboard()
                elif index == 4:
                    testArena()
                    #Spawn player at 40, 25
                elif index == 5:
                    gameCredits()
                elif index == 6:
                    root.clear()
                    drawLogo()
                    openOptions()
                elif index == 7:
                    stopProcess()
                    raise SystemExit("Chose Quit on the main menu")
            tdl.flush()
        stopProcess()    
    else:
        print('Not main SO WE ARENT DOING FUCKING ANYTHING AND NOT FUCKING UP THE WHOLE PROGRAM BY OPENING INFINITE INSTANCES OF IT')

def testArena():
    global player, currentMusic, myMap, gameState, currentBranch, FOV_recompute, objects
    allTraits, leftTraits, rightTraits, races, attributes, skills, classes, traits, human, unlockableTraits = initializeTraits() #skilled, human, unlockableTraits = initializeTraits()
    allTraits.extend(skills)
    LvlUp = {'power': 1, 'acc': 10, 'ev': 0, 'arm': 1, 'hp': 14, 'mp': 3, 'crit': 0, 'stren': 0, 'dex': 0, 'vit': 0, 'will': 0, 'ap': 0, 'stamina': 0}
    playerComp = Player('You', 0, 0, 0, 0, 45.0, 'Human', 'Knight', allTraits, LvlUp, unlockableTraits=unlockableTraits)
    fighterComp = Fighter(hp = 120, power= 1, armor= 1, deathFunction=playerDeath, xp=0, evasion = 20, accuracy = 50, maxMP= 20, critical = 5)
    player = GameObject(40, 25, '@', Fighter = fighterComp, Player = playerComp, name = 'You', color = (0, 210, 0))
    player.level = 1
    player.Fighter.hp = player.Fighter.baseMaxHP
    player.Fighter.MP = player.Fighter.baseMaxMP
    player.Fighter.stamina = player.Fighter.maxStamina
    currentBranch = dBr.mainDungeon
    FOV_recompute = True
    myMap, objectsToCreate = layoutReader.readMap("testarenabigmons1")
    color_dark_wall = colors.light_grey
    color_light_wall = colors.white
    color_dark_ground = currentBranch.color_dark_ground
    color_dark_gravel = currentBranch.color_dark_gravel
    color_light_ground = currentBranch.color_light_ground
    color_light_gravel = currentBranch.color_light_gravel
    objectsToCreate.append(player)
    objects = list(objectsToCreate)
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            curTile = myMap[x][y]
            #assert isinstance(curTile, Tile)
            if curTile.blocked or curTile.character == "#":
                curTile.baseDark_fg = color_dark_wall
                curTile.DARK_FG = color_dark_wall
                curTile.baseFg = color_light_wall
                curTile.FG = color_light_wall
                curTile.baseBlocked = True
            else:
                curTile.baseDark_bg = color_dark_ground
                curTile.DARK_BG = color_dark_ground
                curTile.baseBg = color_light_ground
                curTile.BG = color_light_ground
    myMap = clearanceMap(myMap)
    gameState = "playing"
    
    bigFighter = Fighter(hp = 50, armor = 0, power = 0, accuracy=0, evasion=0, xp=0, deathFunction=monsterDeath)
    bigThing = GameObject(55, 24, chr(179), 'The Big Fat Stuff', color = colors.blue, blocks = True, Fighter = bigFighter, AI = BasicMonster(), size = 3, sizeChar=[chr(179), chr(192), None, chr(179), '^', chr(179), chr(179), chr(217)], smallChar = 'W')
    objects.append(bigThing)
    playGame(noSave = True)
    
    
    
def gameCredits():
    centerX, centerY = MID_WIDTH, MID_HEIGHT
    root.clear()
    toPrint = dial.formatText(dial.creditText, WIDTH - 40)
    inY = (HEIGHT // 2) - (len(toPrint) // 2)
    
    for line in toPrint:
        if line != 'BREAK':
            drawCentered(root, y = inY, text = line)
        inY += 1
    
    drawCentered(root, y = inY + 5, text = 'Press any key to continue', fg = colors.green)
    
    tdl.flush()
    tdl.event.key_wait()

def leaderboard():
    try:
        file = shelve.open(absMetaPath, "c")
        scoreList = file['scores']
        scoreList.sort()
        scoreList.reverse()
        root.clear()
        length = len(scoreList) * 4
        y = (HEIGHT // 2) - (length // 2)
        for score in scoreList:
            print(score.sName())
            drawCentered(root, y, score.sName())
            y += 1
            print(score.sDeath())
            drawCentered(root, y, score.sDeath())
            y += 1
            print(score.sScore())
            drawCentered(root, y, score.sScore())
            y += 2
            print()
        drawCentered(root, y + 3, text = 'Press any key to continue', fg = colors.green)
        file['scores'] = scoreList
        file.sync()
        file.close()
        tdl.flush()
        tdl.event.key_wait()
    except (KeyError, FileNotFoundError) as e:
        print('No high scores')
        msgBox(" No high scores to load.", 26, False, False)
        tdl.flush()


#_____________ GUI _______________

def checkPlayerDetected(countEnemies = False):
    detected = False
    numberEnemies = 0
    for object in objects:
        if object.AI:
            if object.AI.detectedPlayer:
                detected = True
                numberEnemies += 1
                if not countEnemies:
                    return detected
    if not countEnemies:
        return detected
    else:
        return detected, numberEnemies

def initializeFOV():
    global FOV_recompute, visibleTiles, pathfinder, menuWindows
    FOV_recompute = True
    menuWindows = []
    visibleTiles = tdl.map.quickFOV(player.x, player.y, isVisibleTile, fov = FOV_ALGO, radius = player.Player.sightRadius, lightWalls = FOV_LIGHT_WALLS)
    pathfinder = tdl.map.AStar(MAP_WIDTH, MAP_HEIGHT, callback = getMoveCost, diagnalCost=1, advanced=False)
    print("shortName = ", currentBranch.shortName)
    con.clear()
    print("FOV INITIALIZED")

def Update(explodeColor = colors.red, explodeChar = '*'):
    global FOV_recompute
    global visibleTiles
    global tilesinPath
    global tilesInRange
    global lookCursor
    global exploredMaps
    branchKey = currentBranch.shortName + str(branchLevel)
    stairKey = branchKey + 'stairs'
    exploredMaps[branchKey] = []
    exploredMaps[stairKey] = []
    con.clear()
    tdl.flush()
    player.Player.changeColor()
    checkLoad()
    if FOV_recompute:
        FOV_recompute = False
        global pathfinder
        visibleTiles = tdl.map.quickFOV(player.x, player.y, isVisibleTile, fov = FOV_ALGO, radius = player.Player.sightRadius, lightWalls = FOV_LIGHT_WALLS)
        pathfinder = tdl.map.AStar(MAP_WIDTH, MAP_HEIGHT, callback = getMoveCost, diagnalCost=1, advanced=False)
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = (x, y) in visibleTiles
                tile = myMap[x][y]
                char = tile.character
                if dispClearance:
                    if tile.clearance < 10:
                        char = str(tile.clearance)
                    else:
                        char = '+'
                if not visible:
                    if tile.explored:
                        con.draw_char(x, y, char, tile.dark_fg, tile.dark_bg)
                        tileTuple = (x, y, tile.character,tile.blocked, tile.chasm)
                        exploredMaps[branchKey].append(tileTuple)
                else:
                    con.draw_char(x, y, char, tile.fg, tile.bg)
                    tileTuple = (x, y, tile.character,tile.blocked, tile.chasm)
                    exploredMaps[branchKey].append(tileTuple)
                    tile.explored = True
                if gameState == 'targeting':
                    inRange = (x, y) in tilesInRange
                    inPath = pathToTargetTile and (x,y) in pathToTargetTile
                    inRect = tilesInRect and (x, y) in tilesInRect
                    if inRange and not tile.wall and showTilesInRange:
                        con.draw_char(x, y, None, fg=None, bg=colors.darker_yellow)
                    if inPath:
                        if (x,y) != (player.x, player.y):
                            if not tile.wall:
                                con.draw_char(x, y, '.', fg = colors.dark_green, bg = None)
                            else:
                                con.draw_char(x, y, 'X', fg = colors.red, bg = None)
                    if inRect:
                        con.draw_char(x, y, 'X', fg = colors.yellow, bg = None)
                        
                elif gameState == 'exploding':
                    exploded = (x,y) in explodingTiles
                    if exploded:
                        con.draw_char(x, y, explodeChar, fg=explodeColor, bg = None)
                if DEBUG:
                    inPath = (x,y) in tilesinPath
                    if inPath:
                        con.draw_char(x, y, 'X', fg = colors.green, bg = None)
                        tilesinPath = []
    if drawDjik:
        print("MUST DRAW")
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if myMap[x][y].djikValue is not None:
                    print("Found dValue")
                    if myMap[x][y].djikValue < 10:
                        if myMap[x][y].djikValue > 0:
                            con.draw_char(x,y, str(myMap[x][y].djikValue), fg = colors.white)
                        else:
                            djik = myMap[x][y].djikValue
                            if djik <= -10:
                                color = colors.red
                            elif djik <= -9:
                                color = colors.light_red
                            elif djik <= -8:
                                color = colors.orange
                            elif djik <= -7:
                                color = colors.light_orange
                            elif djik <= -6:
                                color = colors.yellow
                            elif djik <= -5:
                                color = colors.light_yellow
                            elif djik <= -4:
                                color = colors.light_purple
                            elif djik <= -3:
                                color = colors.lighter_purple
                            elif djik <= -2:
                                color = colors.light_blue
                            else:
                                color = colors.blue
                            con.draw_char(x,y, None, bg = color)
                    else:
                        con.draw_char(x,y,'+', fg= colors.white, bg = colors.red)
                else:
                    print("No Djik Value")

    panel.clear(fg=colors.white, bg=colors.black)
    sidePanel.clear(fg = colors.white, bg = colors.black)
    lookPanel.clear(fg = colors.white, bg = colors.black)
    
    allMonstersDetected = []
    for monsters in monstersDetected:
        allMonstersDetected.extend(monsters)
    panelY = 6
    for object in objects:
        if object != player:
            if (object.x, object.y) in visibleTiles or (object.alwaysVisible and myMap[object.x][object.y].explored) or REVEL or object in allMonstersDetected:
                object.draw()
                if object.Fighter and (SIDE_PANEL_MODES[currentSidepanelMode] == 'enemies'): #and object.owner is None
                    name = textwrap.wrap(object.name, SIDE_PANEL_TEXT_WIDTH)
                    char = object.char
                    if object.size > 1 and object.smallChar:
                        char = object.smallChar
                    if not panelY + len(name) >= HEIGHT:
                        sidePanel.draw_char(2, panelY, char, fg = object.color)
                        for line in name:
                            sidePanel.draw_str(4, panelY, line, fg = colors.white)
                            panelY += 1
                        panelY += 1
                if object.Item and SIDE_PANEL_MODES[currentSidepanelMode] == 'items':
                    name = object.name
                    if object.Item.amount > 1:
                        name += ' ({})'.format(str(object.Item.amount))
                    name = textwrap.wrap(name, SIDE_PANEL_TEXT_WIDTH)
                    if not panelY + len(name) >= HEIGHT:
                        sidePanel.draw_char(2, panelY, object.char, fg = object.color)
                        for line in name:
                            sidePanel.draw_str(4, panelY, line, fg = colors.white)
                            panelY += 1
                        panelY += 1
                if object.Stairs and myMap[object.x][object.y].explored:
                    exploredMaps[stairKey].append((object.x, object.y, object.char, object.color))
                #if object.AI and object.AI.__class__.__name__ == 'Charger' or object.AI.__class__.__name__ == 'Wrath':
                #    for sign in object.AI.chargePathSigns:
                #        sign.draw()
    player.draw()
    
    for x in range(WIDTH):
        con.draw_char(x, PANEL_Y - 1, chr(196))
    con.draw_char(MSG_X - 2, PANEL_Y - 1, chr(254), colors.amber)
    con.draw_char(MSG_X - 3, PANEL_Y - 1, chr(254), colors.amber)
    con.draw_char(MSG_X + MSG_WIDTH + 1, PANEL_Y - 1, chr(254), colors.amber)
    con.draw_char(MSG_X + MSG_WIDTH + 2, PANEL_Y - 1, chr(254), colors.amber)
    con.draw_char(0, PANEL_Y - 1, chr(254), colors.amber)
    con.draw_char(WIDTH - 1, PANEL_Y - 1, chr(254), colors.amber)
    
    con.draw_str(MSG_X + MSG_WIDTH//2 - 2, PANEL_Y - 1, 'LOG', colors.darker_amber, colors.amber)
    if gameState == 'looking':
        con.draw_str(LOOK_X + LOOK_WIDTH//2 - 2, PANEL_Y - 1, 'LOOK', colors.darker_amber, colors.amber)
    else:
        con.draw_str(LOOK_X + LOOK_WIDTH//2 - 3, PANEL_Y - 1, 'BUFFS', colors.darker_amber, colors.amber)
    con.draw_str(MSG_X//2 - 4, PANEL_Y - 1, 'STATUS', colors.darker_amber, colors.amber)
    
    for py in range(PANEL_HEIGHT):
        panel.draw_char(MSG_X - 2, py, chr(179))
        panel.draw_char(MSG_X - 3, py, chr(179))
        panel.draw_char(MSG_X + MSG_WIDTH + 1, py, chr(179))
    panel.draw_char(MSG_X - 2, PANEL_HEIGHT - 1, chr(254), colors.amber)
    panel.draw_char(MSG_X - 3, PANEL_HEIGHT - 1, chr(254), colors.amber)
    panel.draw_char(MSG_X + MSG_WIDTH + 1, PANEL_HEIGHT - 1, chr(254), colors.amber)
        
    '''
    for x in range(WIDTH):
        con.draw_char(x, PANEL_Y - 1, chr(196))
    con.draw_char(MSG_X - 2, PANEL_Y - 1, chr(217), colors.amber)
    con.draw_char(MSG_X - 3, PANEL_Y - 1, chr(192), colors.amber)
    con.draw_char(MSG_X + MSG_WIDTH + 1, PANEL_Y - 1, chr(192), colors.amber)
    con.draw_char(MSG_X + MSG_WIDTH + 2, PANEL_Y - 1, chr(217), colors.amber)
    
    con.draw_str(MSG_X + MSG_WIDTH//2 - 2, PANEL_Y - 1, 'LOG', colors.darker_amber, colors.amber)
    
    for py in range(PANEL_HEIGHT):
        panel.draw_char(MSG_X - 2, py, chr(179))
        panel.draw_char(MSG_X + MSG_WIDTH + 1, py, chr(179))
    for px in range(MSG_X - 1, PANEL_WIDTH):
        panel.draw_char(px, 0, chr(196))
        panel.draw_char(px, PANEL_HEIGHT - 1, chr(196))
    panel.draw_char(MSG_X - 2, 0, chr(217), colors.amber)
    panel.draw_char(MSG_X - 3, 0, chr(192), colors.amber)
    panel.draw_char(MSG_X - 2, PANEL_HEIGHT - 1, chr(191), colors.amber)
    panel.draw_char(MSG_X + MSG_WIDTH + 1, PANEL_HEIGHT - 1, chr(218), colors.amber)
    panel.draw_char(MSG_X + MSG_WIDTH + 1, 0, chr(192), colors.amber)
    panel.draw_str(MSG_X + MSG_WIDTH//2 - 2, 0, 'LOG', colors.darker_amber, colors.amber)
    '''
    '''
    if bossTiles:
        for tile in bossTiles:
            con.draw_char(tile.x, tile.y, 'X')
    '''
    
    root.blit(con, 0, 0, WIDTH, HEIGHT, 0, 0)
    # Draw log
    msgY = 1
    for line in gameMsgs:   #gameMsgs = [[(txt, clr), (txt, clr), ...], [(txt, clr), ...]]
        msgX = MSG_X
        for (text, color) in line:
            panel.draw_str(msgX, msgY, text, bg=None, fg = color)
            msgX += len(text)
        msgY += 1
    
    #msgY = 1
    #for (line, color) in gameMsgs:
    #    panel.draw_str(MSG_X, msgY, line, bg=None, fg = color)
    #    msgY += 1
    
    # Draw GUI
    #panel.draw_str(1, 3, 'Dungeon level: ' + str(branchLevel), colors.white)
    lvlHeaderColor = colors.amber
    lvlValueColor = colors.white
    lvlBackground = None
    if player.Player.skillpoints > 0:
        lvlHeaderColor = colors.azure
        lvlValueColor = colors.azure
        lvlBackground = colors.light_cyan
    panel.draw_str(1, 7, 'Player level:', lvlHeaderColor, lvlBackground)
    panel.draw_str(14, 7, ' ', None, lvlBackground)
    panel.draw_str(15, 7, str(player.level), lvlValueColor, lvlBackground)
    
    panel.draw_str(1, 9, 'Dungeon:', colors.amber)
    panel.draw_str(10, 9, currentBranch.name, colors.white)
    panel.draw_str(1, 11, 'Floor:', colors.amber)
    panel.draw_str(8, 11, str(branchLevel), colors.white)
    panel.draw_str(1, 13, 'Money: ', colors.amber)
    panel.draw_str(8, 13, str(player.Player.money), colors.white)
    panel.draw_str(1, 15, 'Total depth: ', colors.amber)
    panel.draw_str(14, 15, str(depthLevel), colors.white)
    panel.draw_str(1, 17, str(player.Fighter.actionPoints), colors.white)
    renderBar(panel, 1, 1, BAR_WIDTH, 'HP', player.Fighter.hp, player.Fighter.maxHP, player.color, colors.dark_gray, textColor = player.Player.hpTextColor)
    renderBar(panel, 1, 3, BAR_WIDTH, 'MP', player.Fighter.MP, player.Fighter.maxMP, colors.blue, colors.dark_gray, colors.darkest_blue)
    renderBar(panel, 1, 5, BAR_WIDTH, 'Stamina', player.Fighter.stamina, player.Fighter.maxStamina, colors.lighter_yellow, colors.dark_grey, colors.darker_yellow)

    sidePanel.draw_str(3, 1, '?: Help', colors.green)
    for y in range(HEIGHT):
        #if y == 0:
        #    sidePanel.draw_char(0, y, chr(186))
        if y != SIDE_PANEL_INFO_Y and y != PANEL_Y - 1 and y != 0:
            sidePanel.draw_char(0, y, chr(179), colors.white)
        else:
            sidePanel.draw_char(0, y, chr(254), colors.amber)
            
    # Look code
    for ly in range(LOOK_HEIGHT):
        lookPanel.draw_char(0, ly, chr(179), fg = colors.white)
        lookPanel.draw_char(LOOK_WIDTH - 1, ly, chr(179), fg = colors.white)
    lookPanel.draw_char(0, LOOK_HEIGHT - 1, chr(254), fg = colors.amber)
    lookPanel.draw_char(LOOK_WIDTH - 1, LOOK_HEIGHT - 1, chr(254), fg = colors.amber)
    
    if gameState == 'looking' and lookCursor != None:
        lookCursor.draw()
        text = GetNamesUnderLookCursor()
        print(text)
        text = textwrap.wrap(text, LOOK_WIDTH - 2)
        print(text)
        ly = 0
        for line in text:
            lookPanel.draw_str(1, 1 + ly, line, colors.white)
            ly += 1
    else:
        panelY = 1
        selfAware = player.Player.getTrait('trait', 'Self aware') != 'not found'
        for buff in player.Fighter.buffList:
            if buff.showBuff:
                if selfAware and buff.showCooldown:
                    buffText = buff.name.capitalize() + ' (' + str(buff.curCooldown) + ')'
                else:
                    buffText = buff.name.capitalize()
                text = textwrap.wrap(buffText, LOOK_WIDTH - 1)
                if not panelY + len(text) >= HEIGHT:
                    for line in text:
                        lookPanel.draw_str(2, panelY, line, buff.color)
                        panelY += 1
                    panelY += 1
    
    
    #side panel modes
    mode = SIDE_PANEL_MODES[currentSidepanelMode]
    leftX = SIDE_PANEL_WIDTH//2 - len(mode)//2
    rightX = leftX + len(mode)
    sidePanel.draw_str(leftX, SIDE_PANEL_INFO_Y, mode.upper(), fg = colors.darker_amber, bg = colors.amber)
    for sx in range(1, leftX):
        sidePanel.draw_str(sx, SIDE_PANEL_INFO_Y, chr(196), fg = colors.white)
    for sx in range(rightX, SIDE_PANEL_WIDTH):
        sidePanel.draw_str(sx, SIDE_PANEL_INFO_Y, chr(196), fg = colors.white)
    sidePanel.draw_char(SIDE_PANEL_WIDTH - 1, SIDE_PANEL_INFO_Y, chr(254), colors.amber)
        
    #for dx in range(len(mode) + 1):
    #    sidePanel.draw_char(2 + dx, 6, chr(249), colors.amber)
    '''
    if mode == 'buffs':
        panelY = 6
        selfAware = player.Player.getTrait('trait', 'Self aware') != 'not found'
        for buff in player.Fighter.buffList:
            if buff.showBuff:
                if selfAware and buff.showCooldown:
                    buffText = buff.name.capitalize() + ' (' + str(buff.curCooldown) + ')'
                else:
                    buffText = buff.name.capitalize()
                text = textwrap.wrap(buffText, SIDE_PANEL_TEXT_WIDTH)
                if not panelY + len(text) >= HEIGHT:
                    for line in text:
                        sidePanel.draw_str(2, panelY, line, buff.color)
                        panelY += 1
                    panelY += 1
    '''
    if mode == 'stats':
        panelY = 6
        f = player.Fighter
        p = player.Player
        listed = [('Power', f.power), ('Acc', f.accuracy), ('Evasion', f.evasion), ('Armor', f.armor), ('Crit', f.critical), ('Mvt spd', f.moveSpeed), ('Atk spd', f.attackSpeed)]
        for string, stat in listed:
            sidePanel.draw_str(2, panelY, string+':', colors.light_amber)
            sidePanel.draw_str(2+len(string)+2, panelY, str(stat))
            panelY += 2
        '''
        for res in list(f.resistances.keys()):
            sidePanel.draw_str(2, panelY, res+' res:', colors.light_amber)
            sidePanel.draw_str(2+len(res)+5, panelY, str(f.resistances[res]))
            panelY += 2
        '''
    elif mode == 'equipment':
        panelY = 6
        for equipment in equipmentList:
            name = textwrap.wrap(equipment.name, SIDE_PANEL_TEXT_WIDTH)
            if not panelY + len(name) >= HEIGHT:
                sidePanel.draw_char(2, panelY, equipment.char, fg = equipment.color)
                for line in name:
                    sidePanel.draw_str(4, panelY, line, fg = colors.white)
                    panelY += 1
                panelY += 1
    elif mode == 'inventory':
        panelY = 6
        for item in inventory:
            name = textwrap.wrap(item.name, SIDE_PANEL_TEXT_WIDTH)
            if not panelY + len(name) >= HEIGHT:
                sidePanel.draw_char(2, panelY, item.char, fg = item.color)
                for line in name:
                    sidePanel.draw_str(4, panelY, line, fg = colors.white)
                    panelY += 1
                panelY += 1
    elif mode == 'stealth':
        panelY = 6
        detected, numberEnemies = checkPlayerDetected(True)
        if not detected:
            sidePanel.draw_str(2, panelY, 'Concealed', fg = colors.white)
        else:
            sidePanel.draw_str(2, panelY, 'Spotted! ({})'.format(str(numberEnemies)), fg = colors.red)
    elif mode == 'spells':
        panelY = 6
        allSpells = []
        allSpells.extend(player.Fighter.knownSpells)
        allSpells.extend(player.Fighter.spellsOnCooldown)
        allSpells = sortSpells(allSpells)
        for spell in allSpells:
            color = colors.white
            text = spell.name
            if spell.curCooldown > 0:
                text += ' ({})'.format(spell.curCooldown)
                color = colors.grey
            name = textwrap.wrap(text, SIDE_PANEL_TEXT_WIDTH)
            if not panelY + len(name) >= HEIGHT:
                for line in name:
                    sidePanel.draw_str(2, panelY, line, fg = color)
                    panelY += 1
                panelY += 1
    root.blit(sidePanel, SIDE_PANEL_X, SIDE_PANEL_Y, SIDE_PANEL_WIDTH, HEIGHT, 0, 0)
    root.blit(panel, 0, PANEL_Y, PANEL_WIDTH, PANEL_HEIGHT, 0, 0)
    root.blit(lookPanel, LOOK_X, LOOK_Y, LOOK_WIDTH, LOOK_HEIGHT, 0, 0)
    
def chat():
    '''
    Meow
    '''
    target = targetDirection()
    if target == 'cancelled':
        return 'cancelled'
    else:
        (tarX, tarY) = target
        baddie = None
        item = None
        NPC = None
        for object in objects:
            if object.x == tarX and object.y == tarY:
                if object.socialComp :
                    NPC = object
                    break
                elif object.Fighter and object.AI and type(object.AI) != FriendlyMonster:
                    baddie = object
                elif object.Item:
                    item = object
        if NPC is not None:
            tree = NPC.socialComp
            #assert isinstance(tree, dial.DialogTree) #Tells PyDev that tree is an instance of the DialogTree class, so we can have auto-completion working. The side effect is that Python will throw an exception if tree isn't actually an instance of the DialogTree class (but if it isn't, you did something wrong and the rest of the code wouldn't work anyways).
            root.clear()
            tree.currentScreen = copy(tree.origScreen)
            #assert isinstance(tree.currentScreen, dial.DialogScreen)
            state = 'starting'

            while state != 'END':
                mainModule = sys.modules[__name__] #Because "main" is not defined inside itself.
                func = getattr(mainModule, tree.currentScreen.onEnterFunctionName)
                func()
                if state == 'SHOP':
                    state = 'END'
                    NPC.shopComp.browse()
                    break
                elif state != 'QUEST0':
                    #NPC.questList[0].take()
                    #tree.currentScreen = NPC.questList[0].screenGive
                    pass
                con.clear()
                drawCentered(con, y = 2, text = NPC.name, fg = NPC.color)
                dialLength = len(tree.currentScreen.dialogText) - 1
                ty = (CON_HEIGHT // 2) - (dialLength // 2)
                for line in tree.currentScreen.dialogText:
                    if line != 'BREAK':
                        drawCentered(con, y = ty, text = line.replace("[HERO_NAME]", heroName), fg = colors.light_amber)
                    ty += 1
                root.blit(con, 0, 0, WIDTH, HEIGHT, 0, 0)
                chosen = False
                selectedIndex = 0
                while not chosen:
                    #assert isinstance(panel, tdl.Console)
                    panel.clear()
                    for x in range(WIDTH):
                        panel.draw_char(x, 0, chr(196))
                    selectableChoices = [i for i in tree.currentScreen.choicesList if (i.conditionName is None or getattr(mainModule, i.conditionName)())]
                    for dchoice in selectableChoices:
                        #assert isinstance(dchoice, dial.DialogChoice)
                        ind = selectableChoices.index(dchoice)
                        showInd = ind + 1
                        prefix = str(showInd) + ') '
                        strShown = prefix + dchoice.text
                        if selectedIndex == ind:
                            background = colors.white
                            foreground = colors.black
                        else:
                            background = Ellipsis
                            foreground = colors.white
                        panel.draw_str(0, 1 + ind, prefix, fg = Ellipsis, bg = background)
                        panel.draw_str(len(prefix), 1 + ind, dchoice.text.replace("[HERO_NAME]", heroName), fg = foreground, bg = background)
                    root.blit(panel, 0, PANEL_Y, WIDTH, PANEL_HEIGHT, 0, 0)
                    tdl.flush()
                    key = tdl.event.key_wait()
                    actualKey = key.keychar.upper()
                    if actualKey == 'ESCAPE':
                        state = 'END'
                        chosen = True
                    elif actualKey in ('UP', 'KP8'):
                        selectedIndex -= 1
                        if selectedIndex < 0:
                            selectedIndex = len(tree.currentScreen.choicesList) - 1
                        playWavSound('selectClic.wav')
                    elif actualKey in ('DOWN', 'KP2'):
                        selectedIndex += 1
                        if selectedIndex > len(tree.currentScreen.choicesList) - 1 :
                            selectedIndex = 0
                        playWavSound('selectClic.wav')
                    elif actualKey == 'ENTER':
                        state = selectableChoices[selectedIndex].select()
                        chosen = True
                    
        elif baddie is not None:
            msgString = baddie.name.capitalize() + ' is too busy trying to kill you to talk to you right now.'
            message(msgString)
        elif item is not None:
            msgString = 'You receive no answer.'
            message(msgString)
        else:
            msgString = 'You start a heated philosophical debate with yourself.'
            message(msgString)

def findHiddenOptionsPath():
    if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
        basePath = os.path.expanduser("~")
        longPath = os.path.join(basePath, "DementiaRL")
        print(longPath)
        return longPath
    elif sys.platform.startswith('win32') or sys.platform.startswith('win64'):
        basePath = os.getenv("APPDATA")
        longPath = os.path.join(basePath, "DementiaRL")
        print(longPath)
        return longPath
    else:
        raise OSError("OS NOT RECOGNIZED ({})".format(sys.platform))

def showPrologue(escapable = True):
    global currentMusic, heroName
    currentMusic = str('Sweltering_Battle.wav')
    stopProcess()
    print('CREATING MUSIC PROCESS')
    music = multiprocessing.Process(target = mus.runMusic, args = (currentMusic,))
    print('STARTING MUSIC PROCESS')
    music.start()
    activeProcess.append(music)
    
    def showScreen(screenText, console, height):
        console.clear()
        screen = dial.formatText(screenText, 104)
        dialLength = len(screen) - 1
        ty = (height // 2) - (dialLength // 2)
        print(screen)
        for line in screen:
            if line != 'BREAK':
                drawCenteredVariableWidth(console, y = ty, text = line, fg = (217, 0, 0), width = 104)
            ty += 1
        root.blit(console, x= 22, y=10, width = 104, height = HEIGHT - 18, srcX = 0, srcY = 0)
        tdl.flush()
        tdl.event.key_wait()

    root.clear()
    asciiFile = os.path.join(absAsciiPath, "redframe.xp")
    xpRawString = gzip.open(asciiFile, "r").read()
    convertedString = xpRawString
    attributes = xpL.load_xp_string(convertedString)
    picWidth = int(attributes["width"])
    picHeight = int(attributes["height"])
    print("Pic Height = ", picHeight)
    lData = attributes["layer_data"]
    con = NamedConsole('con', 104, HEIGHT - 18)
    layerInd = int(0)
    xpL.load_layer_to_console(root, lData[0], offsetX=5, noBG = True)
    for scr in dial.prologueScreens:
        showScreen(scr, con, HEIGHT - 18)
    con.clear()
    midScreen = (HEIGHT - 18) // 2
    
    if heroName is None:
        name = ''
        letters = []
        hasConfirmed = False
        while True:#not tdl.event.isWindowClosed():
            text = '_'
            name = ''
            for letter in letters:
                name += letter
            if len(name) < 16:
                text = name + '_'
            else:
                text = name
    
            con.clear()
    
            drawCenteredVariableWidth(con, y = midScreen - 1, text = "And this hero's name was...", fg = (217, 0, 0), width = 104)
            drawCenteredVariableWidth(con, y = midScreen + 1, text = text, fg = (217, 0, 0), width = 104)
            root.blit(con, x= 22, y=10, width = 104, height = HEIGHT - 18, srcX = 0, srcY = 0)
            tdl.flush()
            
            key = tdl.event.key_wait()
            if tdl.event.isWindowClosed():
                quitGame("Closed game", noSave = True)
            if key.keychar.upper()== 'ENTER':
                if name == '':
                    playWavSound('error.wav')
                elif name in FORBIDDEN_NAMES:
                    msgBox("\n Find a more original name ! \n", 33, False, False)
                else:
                    hasConfirmed = True
                    break
                
            elif key.keychar in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
                if len(name) < 16:
                    letters.append(key.keychar)
                else:
                    playWavSound('error.wav')
            elif key.keychar.upper() == 'BACKSPACE':
                if letters:
                    letters.pop()
                else:
                    playWavSound('error.wav')
            elif key.keychar.upper() == 'ESCAPE' and escapable:
                quitGame("Return to MM", noSave = True, backToMainMenu= True)
        if not hasConfirmed:
            quitGame("Window closed during name enter")
        hiddenPath = findHiddenOptionsPath()
        if not os.path.exists(hiddenPath):
            os.makedirs(hiddenPath)
        hOptionsFilePath = os.path.join(hiddenPath, "DATA")
        hOptionsFile = open(hOptionsFilePath, "w")
        hOptionsFile.write("HERONAME:{}".format(name))
        hOptionsFile.close()
        heroName = name
    else:
        con.clear()
        drawCenteredVariableWidth(con, y = midScreen - 1, text = "And this hero's name was...", fg = (217, 0, 0), width = 104)
        drawCenteredVariableWidth(con, y = midScreen + 1, text = heroName, fg = (217, 0, 0), width = 104)
        root.blit(con, x= 22, y=10, width = 104, height = HEIGHT - 18, srcX = 0, srcY = 0)
        tdl.flush()
        tdl.event.key_wait()
        if tdl.event.isWindowClosed():
            quitGame("Closed game", noSave = True)


def GetNamesUnderLookCursor():
    tile = myMap[lookCursor.x][lookCursor.y]
    if tile.secretWall:
        tileDisp = 'Something is off with this wall'
    else:
        tileDisp = None
    names = [obj for obj in objects
                if obj.x == lookCursor.x and obj.y == lookCursor.y and (obj.x, obj.y in visibleTiles) and obj != lookCursor]
    for loop in range(len(names)):
        if names[loop].Fighter:
            displayName = names[loop].name + ' (' + names[loop].Fighter.damageText + ')'
        else:
            if names[loop].Item and names[loop].Item.stackable and names[loop].Item.amount > 1:
                if names[loop].pluralName:
                    displayName = str(names[loop].Item.amount) + ' ' + names[loop].pluralName
                else:
                    displayName = str(names[loop].Item.amount) + ' ' + names[loop].name + "s"
            else:
                displayName = names[loop].name
        names[loop] = displayName
    if tileDisp is not None:
        names.insert(0, tileDisp)
    names = ', '.join(names)
    return names

def arcCoordinates(r, dx, dy, pointX, arcWidth = 90):
    radArcWidth = radians(arcWidth)
    teta = atan2(dy, dx)
    x, y = pointX
    xA = round(r * cos(teta + radArcWidth/2))
    yA = round(r * sin(teta + radArcWidth/2))
    pointA = (xA + x, yA + y)
    xB = round(r * cos(teta - radArcWidth/2))
    yB = round(r * sin(teta - radArcWidth/2))
    pointB = (xB + x, yB + y)
    print(r, dy, arcWidth, pointX, xA, yA, pointA, xB, yB, pointB)
    return pointA, pointB

def sign(point1, point2, point3):
    x1, y1 = point1
    x2, y2 = point2
    x3, y3 = point3
    return (x1 - x3) * (y2 - y3) - (x2 - x3) * (y1 - y3)

def isInTriangle(pointX, point1, point2, point3):
    test1 = sign(pointX, point1, point2) < 0
    test2 = sign(pointX, point2, point3) < 0
    test3 = sign(pointX, point3, point1) < 0
    
    return test1 == test2 and test2 == test3

def displayConfirmSpell(start, caster, zone = None):
    global myMap, objects, menuWindows, FOV_recompute
    dotsAOE = []
    if zone:
        for (x, y) in zone(start, caster):
            try:
                if not myMap[x][y].blocked:
                    dot = GameObject(x = x, y = y, char = '.', name = 'AOE dot', color = colors.yellow, Ghost = True)
                    objects.append(dot)
                    dotsAOE.append(dot)
                    dot.sendToBack()
            except IndexError:
                    pass
    
    text = 'Are you sure you want to cast this spell? (Yes: Enter, No: Escape)'
    width = len(text) + 2
    height = 3
    if menuWindows:
        for mWindow in menuWindows:
            mWindow.clear()
            FOV_recompute = True
            if mWindow.name == 'spellMenu' and mWindow.type == 'menu':
                ind = menuWindows.index(mWindow)
                del menuWindows[ind]
                print('Deleted')
            tdl.flush()
    Update()
    window = NamedConsole('confirmSpellCasting', width, height)
    window.clear()
    menuWindows.append(window)
    
    choseOrQuit = False
    choice = False
    while not choseOrQuit:
        choseOrQuit = True
        for k in range(width):
            window.draw_char(k, 0, chr(196))
        window.draw_char(0, 0, chr(218))
        window.draw_char(k, 0, chr(191))
        kMax = k
        for l in range(height):
            if l > 0:
                window.draw_char(0, l, chr(179))
                window.draw_char(kMax, l, chr(179))
        lMax = l
        for m in range(width):
            window.draw_char(m, lMax, chr(196))
        window.draw_char(0, lMax, chr(192))
        window.draw_char(kMax, lMax, chr(217))
        
        window.draw_str(1, 1, text, fg = colors.white, bg = None)

        posX = MAP_WIDTH//2 - int(width/2)
        posY = MAP_HEIGHT - 3
        root.blit(window, posX, posY, width, height, 0, 0)
    
        tdl.flush()
        
        key = tdl.event.key_wait()
        keyChar = key.keychar
        if keyChar.upper() == 'ENTER':
            choice = True
        elif keyChar.upper() == "ESCAPE":
            choice = False
        else:
            choseOrQuit = False
    for dot in dotsAOE:
        objects.remove(dot)
    return choice

def targetTile(maxRange = None, showBresenham = False, unlimited = False, AOE = False, rangeAOE = 0, styleAOE = None, melee = False, returnBresenham = False, returnAOE = False):
    global gameState
    global cursor
    global tilesInRange, showTilesInRange
    global FOV_recompute
    global pathToTargetTile
    
    if maxRange == 0:
        return (player.x, player.y)
    if not (maxRange is None or unlimited or maxRange == player.Player.sightRadius):
        showTilesInRange = True
    else:
        showTilesInRange = False
    dotsAOE = []
    gameState = 'targeting'
    cursor = GameObject(x = player.x, y = player.y, char = 'X', name = 'cursor', color = colors.yellow, Ghost = True)
    objects.append(cursor)
    if not unlimited:
        if not melee:
            for (rx, ry) in visibleTiles:
                    if maxRange is None or player.distanceToCoords(rx,ry) <= maxRange:
                        tilesInRange.append((rx, ry))
        else:
            x, y = player.x, player.y
            middle = (x, y)
            up = (x, y-1)
            upR = (x+1, y-1)
            right = (x+1, y)
            downR = (x+1, y+1)
            down = (x, y+1)
            downL = (x-1, y+1)
            left = (x-1, y)
            upL = (x-1, y-1)
            tilesInRange = [middle, up, upR, right, downR, down, downL, left, upL]
    else:
        for rx in range(MAP_WIDTH):
            for ry in range(MAP_HEIGHT):
                if not myMap[rx][ry].blocked:
                    tilesInRange.append((rx, ry))
    
    FOV_recompute= True
    Update()
    tdl.flush()

    while gameState == 'targeting':
        brLine = tdl.map.bresenham(player.x, player.y, cursor.x, cursor.y)
        FOV_recompute = True
        key = tdl.event.key_wait()
        if key.keychar.upper() == 'ESCAPE':
            gameState = 'playing'
            objects.remove(cursor)
            del cursor
            tilesInRange = []
            if pathToTargetTile:
                pathToTargetTile = []
            for dot in dotsAOE:
                objects.remove(dot)
            con.clear()
            Update()
            return 'cancelled'
        elif key.keychar.upper() in MOVEMENT_KEYS:
            dx, dy = MOVEMENT_KEYS[key.keychar.upper()]
            if (cursor.x + dx, cursor.y + dy) in tilesInRange and (maxRange is None or player.distanceTo(cursor) <= maxRange):
                pathToTargetTile = []
                cursor.move(dx, dy)
                if showBresenham:
                    for i in range(len(brLine)):
                        pathToTargetTile.append(brLine[i])
                    #print(pathToTargetTile)
                for dot in dotsAOE:
                    objects.remove(dot)
                dotsAOE = []
                if styleAOE:
                    '''
                    elif styleAOE == 'cardinal cross':
                        for tx in range(cursor.x - rangeAOE, cursor.x + rangeAOE + 1):
                            try:
                                if not myMap[tx][cursor.y].blocked:
                                    dot = GameObject(x = tx, y = cursor.y, char = '.', name = 'AOE dot', color = colors.yellow, Ghost = True)
                                    objects.append(dot)
                                    dotsAOE.append(dot)
                                    dot.sendToBack()
                            except IndexError:
                                    pass
                        for ty in range(cursor.y - rangeAOE, cursor.y + rangeAOE + 1):
                            try:
                                if not myMap[cursor.x][ty].blocked:
                                    dot = GameObject(x = tx, y = cursor.y, char = '.', name = 'AOE dot', color = colors.yellow, Ghost = True)
                                    objects.append(dot)
                                    dotsAOE.append(dot)
                                    dot.sendToBack()
                            except IndexError:
                                    pass
                    '''
                    if styleAOE == 'circle':
                        for tx in range(cursor.x - rangeAOE - 1, cursor.x + rangeAOE + 1):
                            for ty in range(cursor.y - rangeAOE - 1, cursor.y + rangeAOE + 1):
                                try:
                                    if cursor.distanceToCoords(tx, ty) <= rangeAOE and not myMap[tx][ty].blocked:
                                        dot = GameObject(x = tx, y = ty, char = '.', name = 'AOE dot', color = colors.yellow, Ghost = True)
                                        objects.append(dot)
                                        dotsAOE.append(dot)
                                        dot.sendToBack()
                                except IndexError:
                                    pass
                    elif styleAOE == 'cone':
                        if not (cursor.x == player.x and cursor.y == player.y):
                            pointA, pointB = arcCoordinates(player.distanceTo(cursor), cursor.x - player.x, cursor.y - player.y, (cursor.x, cursor.y))
                            xA, yA = pointA
                            xB, yB = pointB
                            lineA = tdl.map.bresenham(player.x, player.y, xA, yA)
                            while player.distanceToCoords(xA, yA) > rangeAOE:
                                lineA.pop()
                                pointA = lineA[len(lineA) - 1]
                                xA, yA = pointA
                            lineB = tdl.map.bresenham(player.x, player.y, xB, yB)
                            while player.distanceToCoords(xB, yB) > rangeAOE:
                                lineB.pop()
                                pointB = lineB[len(lineB) - 1]
                                xB, yB = pointB
                            
                            lineAB = tdl.map.bresenham(xA, yA, xB, yB)
                                
                            '''
                            middleLine = list(deepcopy(brLine))
                            xM, yM = middleLine[len(middleLine) - 1]
                            while player.distanceToCoords(xM, yM) > rangeAOE:
                                middleLine.pop()
                                xM, yM = middleLine[len(middleLine) - 1]
                            
                            newLine = tdl.map.bresenham(xA, yA, xM, yM)
                            lines.extend(newLine)
                            newLine = tdl.map.bresenham(xB, yB, xM, yM)
                            lines.extend(newLine)
                            
                            for x, y in lines:
                                if not myMap[x][y].blocked:
                                    found = False
                                    for obj in dotsAOE:
                                        if obj.x == x and obj.y == y:
                                            found = True
                                    if not found:
                                        dot = GameObject(x = x, y = y, char = '.', name = 'AOE dot', color = colors.yellow, Ghost = True)
                                        objects.append(dot)
                                        dotsAOE.append(dot)
                                        dot.sendToBack()
                            '''
                            
                            for x in range(player.x - rangeAOE - 1, player.x + rangeAOE + 2):
                                for y in range(player.y - rangeAOE - 1, player.y + rangeAOE + 2):
                                    if (isInTriangle((x, y), (player.x, player.y), pointA, pointB) or (x, y) in lineA or (x, y) in lineB or (x, y) in lineAB) and not myMap[x][y].blocked:
                                        dot = GameObject(x = x, y = y, char = '.', name = 'AOE dot', color = colors.yellow, Ghost = True)
                                        objects.append(dot)
                                        dotsAOE.append(dot)
                                        dot.sendToBack()
                    else:
                        #try:
                        for (x, y) in styleAOE(cursor, player):
                            try:
                                if not myMap[x][y].blocked:
                                    dot = GameObject(x = x, y = y, char = '.', name = 'AOE dot', color = colors.yellow, Ghost = True)
                                    objects.append(dot)
                                    dotsAOE.append(dot)
                                    dot.sendToBack()
                            except IndexError:
                                    pass
                        #except:
                        #    raise UnrecognizedElement('targeting is neither a cone nor a known function')

                Update()
                tdl.flush()
                for object in objects:
                    object.clear
                con.clear()    
        elif key.keychar.upper() == 'ENTER':
            gameState = 'playing'
            x = cursor.x
            y = cursor.y
            tilesInRange = []
            gameState = 'playing'
            objects.remove(cursor)
            del cursor
            if pathToTargetTile:
                pathToTargetTile = []
            coordsAOE = []
            for dot in dotsAOE:
                objects.remove(dot)
                if returnAOE:
                    coordsAOE.append((dot.x, dot.y))
            con.clear()
            Update()
            if returnBresenham:
                return tdl.map.bresenham(player.x, player.y, x, y)
            elif returnAOE:
                return coordsAOE
            else:
                return (x, y)

def targetAnyTile(startX = None, startY = None, drawRectangle = False):
    global gameState, FOV_recompute, tilesInRect
    gameState = 'targeting'
    if startX is None:
        startX = player.x
    if startY is None:
        startY = player.y
    cursor = GameObject(x = startX, y = startY, char = 'X', name = 'cursor', color = colors.yellow, Ghost = True)
    objects.append(cursor)
        
    FOV_recompute= True
    Update()
    tdl.flush()

    while gameState == 'targeting':
        FOV_recompute = True
        key = tdl.event.key_wait()
        if key.keychar.upper() == 'ESCAPE':
            gameState = 'playing'
            objects.remove(cursor)
            tilesInRect = []
            del cursor
            con.clear()
            Update()
            return 'cancelled', 'cancelled'
        elif key.keychar.upper() in MOVEMENT_KEYS:
            dx, dy = MOVEMENT_KEYS[key.keychar.upper()]
            if not myMap[cursor.x + dx][cursor.y + dy].unbreakable and (not drawRectangle or (not ((cursor.x+dx) < startX) and not ((cursor.y + dy) < startY))) :
                cursor.move(dx, dy)
                if drawRectangle:
                    tilesInRect = []
                    for wx in range(startX, cursor.x + 1):
                        for wy in range(startY, cursor.y + 1):
                            tilesInRect.append((wx, wy))
                Update()
                tdl.flush()
                for object in objects:
                    object.clear
                con.clear()    
        elif key.keychar.upper() == 'ENTER':
            gameState = 'playing'
            x = cursor.x
            y = cursor.y
            tilesInRect = []
            gameState = 'playing'
            objects.remove(cursor)
            del cursor
            con.clear()
            Update()
            return (x, y)
        
def targetDirection():
    global FOV_recompute
    message('Please press a direction key')
    FOV_recompute = True
    Update()
    tdl.flush()
    key = tdl.event.key_wait()
    if key.keychar.upper() in MOVEMENT_KEYS:
        (dx, dy) = MOVEMENT_KEYS[key.keychar.upper()]
        (x, y) = (player.x + dx, player.y + dy)
        return (x, y)
    else:
        FOV_recompute = True
        message('Invalid input')
        Update()
        tdl.flush()
        return 'cancelled'


#______ INITIALIZATION AND MAIN LOOP________
def accessMapFile(level = branchLevel, branchToDisplay = currentBranch.shortName):
    mapName = branchToDisplay + str(level)
    print(mapName)
    mapFile = os.path.join(absDirPath, mapName)
    return mapFile


def saveGame():
    
    if not os.path.exists(absDirPath):
        os.makedirs(absDirPath)
    
    file = shelve.open(absFilePath, "n")
    file["branchLevel"] = branchLevel
    file["currentBranch"] = currentBranch
    file["myMap_level{}".format(branchLevel)] = myMap
    print("Saved myMap_level{}".format(branchLevel))
    file["objects_level{}".format(branchLevel)] = objects
    file["playerIndex"] = objects.index(player)
    #if currentBranch.shortName != 'town':
    #    file["stairsIndex"] = objects.index(stairs)
    file["inventory"] = inventory
    file["equipmentList"] = equipmentList
    file["gameMsgs"] = gameMsgs
    file["logMsgs"] = logMsgs
    file["gameState"] = gameState
    file["hiroshimanNumber"] = hiroshimanNumber
    file['potionIdentify'] = potionIdentify
    file['scrollIdentify'] = scrollIdentify
    file['colorDict'] = colorDict
    file['nameDict'] = nameDict
    file['currentMusic'] = currentMusic
    file['exploredMaps'] = exploredMaps
    if bossTiles is not None:
        file['bossTiles'] = bossTiles
    else:
        print("CANNOT SAVE BOSS TILES CAUSE NO BOSS TILES")
        
    if bossEntrance is not None:
        file["bossEntrance"] = bossEntrance
    else:
        print("CANNOT SAVE BOSS ENTRANCE")
    
    '''
    if branchLevel > 1 or currentBranch.name != 'Main':
        print(currentBranch.name)
        print(currentBranch.shortName)
        file["upStairsIndex"] = objects.index(upStairs)
    gluttBrLevel = dBr.gluttonyDungeon.origDepth
    townBrLevel = dBr.hiddenTown.origDepth
    greedBrLevel = dBr.greedDungeon.origDepth
    wrathBrLevel = dBr.wrathDungeon.origDepth
    if branchLevel == gluttBrLevel and currentBranch.name == 'Main':
        try:
            file["gluttStairsIndex"] = objects.index(gluttonyStairs)
            print('SAVED FUCKING GLUTTONY STAIRS AT INDEX {}'.format(objects.index(gluttonyStairs)))
        except Exception as error:
            print("===========WARNING============")
            print("Couldn't save Gluttony stairs")
            print('Error : {}'.format(type(error)))
            print('Details : {}'.format(error.args))
            print('==============================')
            pass
    else:
        print("DIDNT SAVE GLUTTONY STAIRS")
        print("branchLevel : {} / GluttonyLevel : {}".format(branchLevel, gluttBrLevel))
        print('Current branch : {}'.format(currentBranch.name))
    if branchLevel == townBrLevel and currentBranch.name == 'Main':
        try:
            file["townStairsIndex"] = objects.index(townStairs)
        except:
            print("Couldn't save Gluttony stairs")
            pass
    if branchLevel == greedBrLevel and currentBranch.name == 'Main':
        try:
            file["greedStairsIndex"] = objects.index(greedStairs)
            print('SAVED FUCKING greed STAIRS AT INDEX {}'.format(objects.index(greedStairs)))
        except Exception as error:
            print("===========WARNING============")
            print("Couldn't save greed stairs")
            print('Error : {}'.format(type(error)))
            print('Details : {}'.format(error.args))
            print('==============================')
            pass
    if branchLevel == wrathBrLevel and currentBranch.name == 'Main':
        try:
            file["wrathStairsIndex"] = objects.index(wrathStairs)
            print('SAVED FUCKING wrath STAIRS AT INDEX {}'.format(objects.index(wrathStairs)))
        except Exception as error:
            print("===========WARNING============")
            print("Couldn't save wrath stairs")
            print('Error : {}'.format(type(error)))
            print('Details : {}'.format(error.args))
            print('==============================')
            pass
    '''
    file.close()
    
    #mapFile = open(absPicklePath, 'wb')
    #pickle.dump(myMap, mapFile)
    #mapFile.close()

def reloadBossTiles():
    '''
    Alias : resetBossTiles
    '''
    newTiles = []
    if bossTiles:
        for tile in bossTiles:
            newTiles.append(myMap[tile.x][tile.y])
    return newTiles

def reloadEntrance():
    return myMap[bossEntrance.x][bossEntrance.y]

def newGame():
    global objects, inventory, gameMsgs, gameState, player, branchLevel, gameMsgs, identifiedItems, equipmentList, currentBranch, bossDungeonsAppeared, DEBUG, REVEL, logMsgs, tilesInRange, showTilesInRange, tilesinPath, tilesInRect, menuWindows, explodingTiles, hiroshimanNumber, FOV_recompute, bossTiles, bossEntrance, currentSidepanelMode, highCultistHasAppeared, exploredMaps
    DEBUG = False
    REVEL = False
    deleteSaves()
    bossDungeonsAppeared = {'gluttony': False, 'greed': False, 'wrath': False}
    dBr.reinitializeBranches()
    gameMsgs = []
    objects = [player]
    logMsgs = []
    tilesInRange = []
    showTilesInRange = False
    explodingTiles = []
    tilesinPath = []
    tilesInRect = []
    menuWindows = []
    hiroshimanNumber = 0
    FOV_recompute = True
    bossTiles = None
    bossEntrance = None
    currentSidepanelMode = 0
    exploredMaps = {}
    
    currentBranch = dBr.mainDungeon
    branchLevel = 1 
    makeMap()
    Update()

    inventory = []
    equipmentList = []
    identifiedItems = []

    FOV_recompute = True
    initializeFOV()
    message("Zarg says : 'Prepare to get lost in the Realm of Madness !'", colors.dark_violet)
    gameState = 'playing'
    
    equipmentComponent = Equipment(slot='one handed', type = 'light weapon', powerBonus=3, meleeWeapon=True)
    object = GameObject(0, 0, '-', 'dagger', colors.light_sky, Equipment=equipmentComponent, Item=Item(weight = 0.8, pic = 'dagger.xp', useText = 'Equip'), darkColor = colors.darker_sky)
    inventory.append(object)
    object.alwaysVisible = True
    if player.Player.classes == 'Rogue':
        equipmentComponent = Equipment(slot = 'two handed', type = 'missile weapon', powerBonus = 1, ranged = True, rangedPower = 7, maxRange = player.Player.sightRadius, ammo = 'arrow')
        object = GameObject(0, 0, ')', 'shortbow', colors.light_orange, Equipment = equipmentComponent, Item = Item(weight = 1.0, pic = 'bow.xp'), darkColor = colors.dark_orange)
        inventory.append(object)
        object.alwaysVisible = True
        
        itemComponent = Item(stackable = True, amount = 30)
        object = GameObject(0, 0, '^', 'arrow', colors.light_orange, Item = itemComponent)
        inventory.append(object)
    
    if highCultistHasAppeared: #It's the exact contrary of the last statement yet it does the exact same thing (aside from the fact that we can have several high cultists)
        message('You feel like somebody really wants you dead...', colors.dark_red)
        highCultistHasAppeared = False #Make so more high cultists can spawn at lower levels (still only one by floor though)

def loadGame():
    '''
    @attention : This makes so variables become exact COPIES (except for their memory adresses)of what they were at the moment they were saved
    So if you do stuff such as if X in Y, this might (read : will) break it. A workaround is not checking directly if X is in Y, but instead check if X's name is in the list of the names of the things in Y, or if X is a tile by telling Python to access the tile at (x,y) coordinates rather than accessing it directly by a variable.
    For example, this caused spells to be able to be learned multiple time after saving/loading, because we checked if the Spell object was in the spells list, though the memory adresses of the loaded Spell objects in the spell list had changed, hence why Python thought the original spells were no longer in the spells list and allowed them to be relearned.
    loadLevel() very probably has the same behaviour, though it causes less problems because we load a lesser amount of less critcal data.
    '''
    global FOV_recompute, objects, inventory, gameMsgs, gameState, player, branchLevel, myMap, equipmentList, stairs, upStairs, hiroshimanNumber, currentBranch, gluttonyStairs, logMsgs, townStairs, greedStairs, wrathStairs, potionIdentify, scrollIdentify, nameDict, colorDict, bossTiles, currentMusic, bossEntrance, exploredMaps
    
    FOV_recompute = True
    #myMap = [[Tile(True) for y in range(MAP_HEIGHT)]for x in range(MAP_WIDTH)]
    file = shelve.open(absFilePath, "r")
    branchLevel = file["branchLevel"]
    currentBranch = file["currentBranch"]
    myMap = file["myMap_level{}".format(branchLevel)]
    objects = file["objects_level{}".format(branchLevel)]
    player = objects[file["playerIndex"]]
    print(player.Fighter.knownSpells)
    #if currentBranch.shortName != 'town':
    #    stairs = objects[file["stairsIndex"]]
    inventory = file["inventory"]
    equipmentList = file["equipmentList"]
    gameMsgs = file["gameMsgs"]
    gameState = file["gameState"]
    logMsgs = file["logMsgs"]
    hiroshimanNumber = file["hiroshimanNumber"]
    potionIdentify = file['potionIdentify']
    scrollIdentify = file['scrollIdentify']
    colorDict = file['colorDict']
    nameDict = file['nameDict']
    currentMusic = file['currentMusic']
    exploredMaps = file['exploredMaps']
    try:
        bossTiles = file['bossTiles']
        bufferTiles = reloadBossTiles() #Because of the behavior described in the docstring, we need to refresh the tiles 
        bossTiles = list(bufferTiles)
    except KeyError:
        bossTiles = None
        print("NO BOSS TILES")
        
    try:
        bossEntrance = file['bossEntrance']
        bufferEntrance = reloadEntrance()
        bossEntrance = bufferEntrance
    except KeyError:
        bossEntrance = None
        print("NO BOSS ENTRANCE")
    
    '''
    if branchLevel > 1 or currentBranch.name != 'Main':
        print(currentBranch.name)
        upStairs = objects[file["upStairsIndex"]]
    gluttBrLevel = dBr.gluttonyDungeon.origDepth
    townBrLevel = dBr.hiddenTown.origDepth
    greedBrLevel = dBr.greedDungeon.origDepth
    wrathBrLevel = dBr.wrathDungeon.origDepth
    if branchLevel == gluttBrLevel and currentBranch.name == 'Main':
        gluttonyStairs = objects[file["gluttStairsIndex"]]
    if branchLevel == townBrLevel and currentBranch.name == 'Main':
        townStairs = objects[file["townStairsIndex"]]
    if branchLevel == greedBrLevel and currentBranch.name == 'Main':
        greedStairs = objects[file["greedStairsIndex"]]
    if branchLevel == wrathBrLevel and currentBranch.name == 'Main':
        greedStairs = objects[file["wrathStairsIndex"]]
    #mapFile = open(absPicklePath, "rb")
    #myMap = pickle.load(mapFile)
    #mapFile.close()
    '''


def saveLevel(level = branchLevel):
    #if not os.path.exists(absDirPath):
        #os.makedirs(absDirPath)
    
    #if not os.path.exists(absFilePath):
        #file = shelve.open(absFilePath, "n")
        #print()
    #else:
        #file = shelve.open(absFilePath, "w")
    print("=============SAVING LEVEL===============")
    print("Current branch = {}".format(currentBranch.name))
    mapFilePath = accessMapFile(level, branchToDisplay = currentBranch.shortName)
    mapFile = shelve.open(mapFilePath, "n")
    mapFile["myMap"] = myMap
    mapFile["objects"] = objects
    mapFile["playerIndex"] = objects.index(player)
    if bossTiles is not None:
        mapFile["bossTiles"] = bossTiles
    else:
        print("CANNOT SAVE BOSS TILES")
    
    if bossEntrance is not None:
        mapFile["bossEntrance"] = bossEntrance
    else:
        print("CANNOT SAVE BOSS ENTRANCE")
    '''
    if currentBranch.shortName != 'town':
        mapFile["stairsIndex"] = objects.index(stairs)
    if (level > 1 or currentBranch.name != 'Main') and upStairs in objects:
        mapFile["upStairsIndex"] = objects.index(upStairs)
        print('SAVED FREAKING UPSTAIRS')
    gluttBrLevel = dBr.gluttonyDungeon.origDepth
    townBrLevel = dBr.hiddenTown.origDepth
    greedBrLevel = dBr.greedDungeon.origDepth
    wrathBrLevel = dBr.wrathDungeon.origDepth
    if branchLevel == gluttBrLevel and currentBranch.name == 'Main':
        try:
            mapFile["gluttStairsIndex"] = objects.index(gluttonyStairs)
            print('SAVED FUCKING GLUTTONY STAIRS AT INDEX {}'.format(objects.index(gluttonyStairs)))
        except Exception as error:
            print("===========WARNING============")
            print("Couldn't save Gluttony stairs")
            print('Error : {}'.format(type(error)))
            print('Details : {}'.format(error.args))
            print('==============================')
            pass
    else:
        print("DIDNT SAVE GLUTTONY STAIRS")
        print("branchLevel : {} / GluttonyLevel : {}".format(branchLevel, gluttBrLevel))
        print('Current branch : {}'.format(currentBranch.name))
    if branchLevel == townBrLevel and currentBranch.name == 'Main':
        try:
            mapFile["townStairsIndex"] = objects.index(townStairs)
        except:
            print("Couldn't save Gluttony stairs")
            pass
    if branchLevel == greedBrLevel and currentBranch.name == 'Main':
        try:
            mapFile["greedStairsIndex"] = objects.index(greedStairs)
            print('SAVED FUCKING greed STAIRS AT INDEX {}'.format(objects.index(greedStairs)))
        except Exception as error:
            print("===========WARNING============")
            print("Couldn't save greed stairs")
            print('Error : {}'.format(type(error)))
            print('Details : {}'.format(error.args))
            print('==============================')
            pass
    if branchLevel == wrathBrLevel and currentBranch.name == 'Main':
        try:
            mapFile["wrathStairsIndex"] = objects.index(wrathStairs)
            print('SAVED FUCKING wrath STAIRS AT INDEX {}'.format(objects.index(wrathStairs)))
        except Exception as error:
            print("===========WARNING============")
            print("Couldn't save wrath stairs")
            print('Error : {}'.format(type(error)))
            print('Details : {}'.format(error.args))
            print('==============================')
            pass
    else:
        print("DIDNT SAVE wrath STAIRS")
        print("branchLevel : {} / WrathLevel : {}".format(branchLevel, wrathBrLevel))
        print('Current branch : {}'.format(currentBranch.name))
    '''
    mapFile["yunowork"] = "SCREW THIS"
    print("Saved level at " + mapFilePath)
    mapFile.sync()
    mapFile.close()
    print("========================================")
    
    return "completed"

def loadLevel(level, save = True, branch = currentBranch, fall = False, fromStairs = None, direction = 'down'):
    '''
    @attention : See loadGame() docstring
    '''
    global objects, player, myMap, stairs, branchLevel, gluttonyStairs, townStairs, currentBranch, wrathStairs, greedStairs, bossTiles, bossEntrance
    if fall:
        fromStairs = None
    if save:
        try:
            saveLevel(branchLevel)
        except:
            print("Couldn't save level " + str(branchLevel))
    mapFilePath = accessMapFile(level, branch.shortName)
    xfile = shelve.open(mapFilePath, "r")
    print(xfile["yunowork"])
    myMap = xfile["myMap"]
    newObjects = xfile["objects"]
    tempPlayer = newObjects[xfile["playerIndex"]]
    try:
        bossTiles = xfile["bossTiles"]
        bufferTiles = reloadBossTiles()
        bossTiles = list(bufferTiles)
    except KeyError:
        print("COULDNT LOAD BOSS TILES")
        bossTiles = None
        
    try:
        bossEntrance = xfile["bossEntrance"]
        bufferEntrance = reloadBossTiles()
        bossEntrance = list(bufferTiles)
    except KeyError:
        print("COULDNT LOAD BOSS ENTRANCE")
        bossEntrance = None
    #if fromStairs:
    #    for object in objects:
    #        if object.Stairs:
    #            if (object.Stairs.climb == 'up' and climbing == 'down' and object.Stairs.branchesFrom == currentBranch) or (object.Stairs.climb == 'down' and climbing == 'up' and object.Stairs.branchesTo == currentBranch): # or (changeBranch and object.Stairs.climb == 'down' and object.Stairs.branchesTo == branch):
    #                player.x, player.y = object.x, object.y
    #if not fall:
    if fromStairs:
        print('======== searching for stairs============')
        for object in newObjects:
            if object.Stairs is not None:
                print('stairs found: {}'.format(object.name))
                if (direction == 'down' and object.Stairs.stairsOf == fromStairs.stairsOf and object.Stairs.climb != fromStairs.climb) or (direction == 'up' and object.Stairs.stairsOf == fromStairs.stairsFrom and object.Stairs.climb != fromStairs.climb) :
                    print('these are the corresponding stairs')
                    player.x, player.y = object.x, object.y
    elif not fall:
        player.x = int(tempPlayer.x)
        player.y = int(tempPlayer.y)
    else:
        x, y = 1, 1
        while isBlocked(x, y) or myMap[x][y].chasm:
            x, y = randint(0, MAP_WIDTH), randint(0, MAP_HEIGHT)
        player.x, player.y = x, y
    newObjects[xfile["playerIndex"]] = player
    objects = list(newObjects)
    '''
    if branch.shortName != 'town':
        stairs = objects[xfile["stairsIndex"]]
    if level > 1 or branch.name != 'Main':
        global upStairs
        upStairs = objects[xfile["upStairsIndex"]]
    gluttBrLevel = dBr.gluttonyDungeon.origDepth
    townBrLevel = dBr.hiddenTown.origDepth
    greedBrLevel = dBr.greedDungeon.origDepth
    wrathBrLevel = dBr.wrathDungeon.origDepth
    if level == gluttBrLevel and branch.name == 'Main':
        print("Branch name is {} and gluttony stairs appear in branch Main. Moreover, we are at level {} and they appear at level {}. Therefore we are loading them and NOTHING SHOULD GO FUCKING WRONG.".format(branch.name, level, gluttBrLevel))
        gluttonyStairs = objects[xfile["gluttStairsIndex"]]
    else:
        print("We didn't load gluttony stairs because they don't exist. So the game SHOULD NOT crash at that point.")
    if level == townBrLevel and branch.name == 'Main':
        townStairs = objects[xfile["townStairsIndex"]]
    if branchLevel == greedBrLevel and currentBranch.name == 'Main':
        greedStairs = objects[xfile["greedStairsIndex"]]
    if branchLevel == wrathBrLevel and currentBranch.name == 'Main':
        wrathStairs = objects[xfile['wrathStairsIndex']]
    '''
    
    message("You climb the stairs")
    print("Loaded level " + str(level))
    xfile.close()
    branchLevel = level
    currentBranch = branch
    objects = newObjects
    initializeFOV()

def nextLevel(boss = False, changeBranch = None, fall = False, fromStairs = None, changeBranchLevel = 1):
    global branchLevel, currentBranch, currentMusic, bossTiles, myMap, objects, stairs, player, highCultistHasAppeared, hiroshimanHasAppeared, totalLevel, depthLevel
    if boss:
        currentMusic = 'Hoxton_Princess.wav'
        stopProcess()
        music = multiprocessing.Process(target = mus.runMusic, args = (currentMusic,))
        music.start()
        activeProcess.append(music)
    elif currentMusic != 'Bumpy_Roots.wav':
        currentMusic = 'Bumpy_Roots.wav'
        stopProcess()
        music = multiprocessing.Process(target = mus.runMusic, args = (currentMusic,))
        music.start()
        activeProcess.append(music)
    bossTiles = None
    returned = "borked"
    changeToCurrent = False
    while returned != "completed":
        returned = saveLevel(branchLevel)
    depthLevel += 1
    if changeBranch is None:
        message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', colors.red)
        branchLevel += 1
        changeToCurrent = True
    else:
        message('You enter ' + changeBranch.name)
        if changeBranchLevel:
            branchLevel = changeBranchLevel
        else:
            branchLevel = 1
        currentBranch = changeBranch
        if DEBUG:
            print('Changing branch...')
    if changeToCurrent:
        changeBranch = currentBranch
    tempMap = myMap
    tempObjects = objects
    tempPlayer = player
    tempStairs = stairs
    print("Before try/except block")
    try:
        loadLevel(branchLevel, save = False, branch = changeBranch, fall = fall, fromStairs=fromStairs)
        print("Loaded existing level {}".format(branchLevel))
    except Exception as error:
        if DEBUG:
            print("===========NO NEXT LEVEL============")
            print("Loading error : {}".format(type(error)))
            print("Details : {}".format(error.args))
            print("Tried to load dungeon level {} of branch {}".format(branchLevel, changeBranch.name))
            print("====================================")
        myMap = tempMap
        objects = tempObjects
        player = tempPlayer
        stairs = tempStairs
        chasmGeneration = False
        holeGeneration = False
        temple = False
        totalLevel += 1
        if not boss:
            if currentBranch.mapGeneration['fixedMap'] is None:
                #if currentBranch.genType == 'dungeon':
                makeMap(generateChasm=chasmGeneration, generateHole=holeGeneration, fall = fall, temple=temple)
                #elif currentBranch.genType == 'cave':
                #    generateCaveLevel(fall = fall)
            elif currentBranch.mapGeneration['fixedMap'] == 'town':
                makeHiddenTown(fall = fall)
            elif currentBranch.mapGeneration['fixedMap'] == 'shrine':
                makeShrineMap()
            else:
                raise ValueError('Current branch fixedMap attribute is invalid ({})'.format(currentBranch.mapGeneration['fixedMap']))
        else:
            makeBossLevel(fall = fall, generateHole = holeGeneration, temple = temple)
        print("Created a new level")
    print("After try except block")
    if hiroshimanNumber == 1 and not hiroshimanHasAppeared:
        message('You suddenly feel uneasy.', colors.dark_red)
        hiroshimanHasAppeared = True
    if highCultistHasAppeared: #It's the exact contrary of the last statement yet it does the exact same thing (aside from the fact that we can have several high cultists)
        message('You feel like somebody really wants you dead...', colors.dark_red)
        highCultistHasAppeared = False #Make so more high cultists can spawn at lower levels (still only one by floor though)
    initializeFOV()

def previousLevel(changeBranch = None, fromStairs = None, changeBranchLevel = None):
    global branchLevel, currentBranch, currentMusic, bossTiles, myMap, objects, stairs, player, highCultistHasAppeared, hiroshimanHasAppeared, totalLevel, depthLevel
    if currentMusic != 'Bumpy_Roots.wav':
        currentMusic = 'Bumpy_Roots.wav'
        stopProcess()
        music = multiprocessing.Process(target = mus.runMusic, args = (currentMusic,))
        music.start()
        activeProcess.append(music)
    returned = "borked"
    changeToCurrent = False
    while returned != "completed":
        returned = saveLevel(branchLevel)
    depthLevel -= 1
    if changeBranch is None:
        #message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', colors.red)
        branchLevel -= 1
        changeToCurrent = True
    else:
        message('You enter ' + changeBranch.name)
        if not changeBranchLevel or changeBranchLevel == 1:
            branchLevel = currentBranch.origDepth
        else:
            branchLevel = changeBranchLevel
        currentBranch = changeBranch
        if DEBUG:
            print('Changing branch...')
    if changeToCurrent:
        changeBranch = currentBranch
    tempMap = myMap
    tempObjects = objects
    tempPlayer = player
    tempStairs = stairs
    lvlToLoad = branchLevel
    #if branchLevel == 1:
    #    lvlToLoad = currentBranch.origDepth
    print("Before try/except block")
    try:
        loadLevel(lvlToLoad, save = False, branch = changeBranch, fromStairs = fromStairs, direction = 'up')
        print("Loaded existing level {}".format(branchLevel))
    except Exception as error:
        if DEBUG:
            print("===========NO PREV LEVEL============")
            print("Loading error : {}".format(type(error)))
            print("Details : {}".format(error.args))
            print("Tried to load dungeon level {} of branch {}".format(branchLevel, changeBranch.name))
            print("====================================")
        myMap = tempMap
        objects = tempObjects
        player = tempPlayer
        stairs = tempStairs
        chasmGeneration = False
        holeGeneration = False
        temple = False
        if currentBranch.mapGeneration['fixedMap'] is None:
            #if currentBranch.genType == 'dungeon':
            makeMap(generateChasm=chasmGeneration, generateHole=holeGeneration, temple=temple)
            #elif currentBranch.genType == 'cave':
            #    generateCaveLevel(fall = fall)
        elif currentBranch.mapGeneration['fixedMap'] == 'town':
            makeHiddenTown()
        else:
            raise ValueError('Current branch fixedMap attribute is invalid ({})'.format(currentBranch.fixedMap))
        print("Created a new level")
    print("After try except block")
    if hiroshimanNumber == 1 and not hiroshimanHasAppeared:
        message('You suddenly feel uneasy.', colors.dark_red)
        hiroshimanHasAppeared = True
    if highCultistHasAppeared: #It's the exact contrary of the last statement yet it does the exact same thing (aside from the fact that we can have several high cultists)
        message('You feel like somebody really wants you dead...', colors.dark_red)
        highCultistHasAppeared = False #Make so more high cultists can spawn at lower levels (still only one by floor though)
    initializeFOV()

def displayTip(text, x = 0, y = 0, arrow = True, pointedDirection = 'right'):
    global FOV_recompute
    MAX_TIP_WIDTH = 80
    if pointedDirection == 'right':
        pointChar = chr(26)
    elif pointedDirection == 'left':
        pointChar = chr(27)
    elif pointedDirection == 'up':
        pointChar = chr(24)
    elif pointedDirection == 'down':
        pointChar = chr(25)
    arrowPoint = GameObject(x, y, pointChar, 'arrow', colors.red, Ghost = True, alwaysAlwaysVisible=True, darkColor=colors.red)
    objects.append(arrowPoint)
    Update()
    tdl.flush()
    for object in objects:
        object.clear()
    width = len(text)
    if width > MAX_TIP_WIDTH:
        width = MAX_TIP_WIDTH
    msgBox(text + ' (press ESCAPE to continue)', width + 2)
    objects.remove(arrowPoint)
    FOV_recompute = True
    Update()
    tdl.flush()
    for object in objects:
        object.clear()
    FOV_recompute = True

def zargSpeech():
    def waitForWait():
        waited = False
        while not waited:
            input = tdl.event.key_wait()
            if input.keychar.upper() == 'KP5' or input.keychar.upper() == 'W':
                waited = True

    global FOV_recompute, player
    zarg = None
    for object in objects:
        if object.name == 'Zarg':
            zarg = object
            break
    
    projectile(zarg.x, zarg.y, player.x, player.y, chr(248), colors.light_han, False, True)
    player.Fighter.hp = 1
    FOV_recompute = True
    message("Zarg says: 'Ha! I was waiting for you. I thought you would represent an actual challenge? Losing this miserably to a such simple spell really shows the inferiority of the human race.'", colors.dark_violet)
    displayTip("Press 5 or 'w' to continue.", 0, 0, False)
    zarg.moveTowards(player.x, player.y)
    FOV_recompute = True
    Update()
    while zarg.distanceTo(player) > 3:
        waitForWait()
        zarg.moveTowards(player.x, player.y)
        FOV_recompute = True
        Update()
        if zarg.distanceTo(player) == 4:
            message("Zarg says: 'Now kneel before the new ruler of this world.'", colors.dark_violet)
    FOV_recompute = True
    Update()
    waitForWait()
    newGame()

def markForEquinoxDrop(*args, **kwargs):
    global hasSpokenToGeneral
    hasSpokenToGeneral = True

def playTutorial():
    global currentMusic, FOV_recompute, DEBUG, tutorial, hasSpokenToGeneral
    if currentMusic is None or currentMusic in ('No_Music.wav', 'Dusty_Feelings.wav', 'Sweltering_Battle.wav'):
        currentMusic = 'Bumpy_Roots.wav'
    stopProcess()
    music = multiprocessing.Process(target = mus.runMusic, args = (currentMusic,))
    music.start()
    activeProcess.append(music)
    
    global objects, inventory, gameMsgs, gameState, player, branchLevel, gameMsgs, identifiedItems, equipmentList, currentBranch, bossDungeonsAppeared, DEBUG, REVEL, logMsgs, tilesInRange, showTilesInRange, tilesinPath, tilesInRect, menuWindows, explodingTiles, hiroshimanNumber, FOV_recompute, bossTiles, bossEntrance
    
    DEBUG = False
    REVEL = False
    deleteSaves()
    gameMsgs = []
    logMsgs = []
    tilesInRange = []
    showTilesInRange = False
    explodingTiles = []
    tilesinPath = []
    tilesInRect = []
    menuWindows = []
    FOV_recompute = True
    bossTiles = None
    bossEntrance = None
    
    inventory = []
    equipmentList = []
    identifiedItems = []
    
    helmetComp = Equipment(slot = 'head', type = 'heavy armor', armorBonus=8, meleeWeapon=False)
    helmet = GameObject(0, 0, '[', 'paladin helm', colors.gold, Equipment=helmetComp, Item=Item(weight=5.0, pic = 'darksoulHelmet.xp'))
    breastComp = Equipment(slot = 'torso', type = 'heavy armor', armorBonus=18, meleeWeapon=False)
    breast = GameObject(0, 0, '[', 'paladin breastplate', colors.gold, Equipment=breastComp, Item=Item(weight=15.0, pic = 'darksoulHelmet.xp'))
    legsComp = Equipment(slot = 'legs', type = 'heavy armor', armorBonus=12, meleeWeapon=False)
    legs = GameObject(0, 0, '[', 'paladin greaves', colors.gold, Equipment=legsComp, Item=Item(weight=10.0, pic = 'darksoulHelmet.xp'))
    
    helmet.Equipment.equip(player.Fighter, True)
    breast.Equipment.equip(player.Fighter, True)
    legs.Equipment.equip(player.Fighter, True)

    FOV_recompute = True
    initializeFOV()
    gameState = 'playing'
    
    tutorial = True
    displayedPickUp = False
    displayedInventory = False
    displayedMonster = False
    displayedGeneral = False
    displayedChat = False
    hasSpokenToGeneral = False
    givenSword = False
    displayedLog = False
    displayedShoot = False
    displayedStairs = False
    foughtZarg = False
    displayedSpell = False
    FOV_recompute = True
    Update()
    FOV_recompute = True
    generalObject = None
    player.trueName = heroName
    
    displayTip('Move around using the directional ARROWS or the NUMPAD. Pressing 5 will pass a turn.', x = 0, y = 0, arrow = False)
    while not foughtZarg:
        Update()
        if myMap is None:
            raise TypeError("MYMAP IS NONE, PLAYTUT FUNC")
            traceback.print_exc()
            os._exit(-1)
        checkLevelUp()
        tdl.flush()
        for object in objects:
            object.clear()
        playerAction = getInput()
        '''
        if tdl.event.isWindowClosed:
            quitGame("Closed game") #already in getinput()
        '''
        if playerAction == 'exit':
            quitGame('Player pressed escape', True)
        FOV_recompute = True #So as to avoid the blackscreen bug no matter which key we press
        if gameState == 'playing' and playerAction != 'didnt-take-turn':
            global mobsToCalculate
            global mustCalculate
            mobsToCalculate = []
            for object in objects:
                if object.AI:
                    try:
                        object.AI.takeTurn()
                    except TypeError as error:
                        print("==================WARNING===================")
                        print(type(error))
                        print(error.args)
                        print(object.name)
                        traceback.print_exc()
                        try:
                            message('CRITICAL AI ERROR SEE CONSOLE FOR DETAILS', colors.red)
                        except Exception as error:
                            print("==================WARNING===================")
                            print("COULDNT PRINT MESSAGE")
                            print(type(error))
                            print(error.args)
                            print(object.name)
                            print("============================================")
                            traceback.print_exc()
                        print("============================================")
            '''
                if object.Fighter and object.Fighter.baseShootCooldown > 0 and object.Fighter is not None:
                    object.Fighter.curShootCooldown -= 1
                if object.Fighter and object.Fighter.baseLandCooldown > 0 and object.Fighter is not None:
                    object.Fighter.curLandCooldown -= 1
            '''
            
            if displayedGeneral and not displayedLog:
                displayTip('Do not forget to regularly check the message log for additional informations about your surroundings.', MSG_X + MSG_WIDTH//2 - 1, MAP_HEIGHT - 2, True, 'down')
                displayedLog = True
            for object in inventory:
                if object.Item and not displayedInventory:
                    displayTip("You can open your inventory by pressing 'i', to see what objects you have gathered. You can also check your equipment with 'E'.", 0, 0, False)
                    displayedInventory = True
            for object in objects:
                if object.name == 'guard' and (object.x, object.y) in visibleTiles and not displayedMonster and object.distanceTo(player) < 12:
                    displayedMonster = True
                    displayTip('Beware! This guard looks pretty aggressive! You can fight him by simply walking onto him.', object.x - 1, object.y, True)
                if object.Item and object.distanceTo(player) <= 8 and not displayedPickUp:
                    displayedPickUp = True
                    displayTip("This is a sword. Pick it up by pressing 'SPACEBAR' while on the same tile.", object.x - 1, object.y)
                    FOV_recompute = True
                if object.name == 'General Guillem' and (object.x, object.y) in visibleTiles and object.distanceTo(player) <= 7 and not displayedGeneral:
                    message("General Guillem shouts: 'Greetings {}! Come to me to summarize our plan!'".format(heroName), colors.gold)
                    displayedGeneral = True
                if object.name == 'General Guillem' and (object.x, object.y) in visibleTiles and object.distanceTo(player) <= 2 and not displayedChat:
                    displayTip("When right next to a NPC, press 'c' and their direction to talk to them.", object.x - 1, object.y)
                    displayedChat = True
                if object.name == 'General Guillem':
                    generalObject = object
                if object.name == 'shortbow' and not displayedShoot:
                    displayedShoot = True
                    displayTip("When equipped with a ranged weapon such as this shortbow, you can press 'x' to shoot. However, most of these weapons require ammunition, such as these arrows.", object.x - 1, object.y)
                if object.Stairs and not displayedStairs and (object.x, object.y) in visibleTiles and object.distanceTo(player) <= 10:
                    displayedStairs = True
                    displayTip("These are the stairs allowing you to climb Zarg's tower. Press '<' to climb them up.", object.x - 1, object.y)
                if object.name == 'Zarg' and (object.x, object.y) in visibleTiles and object.distanceTo(player) <= 10:
                    zargSpeech()
                    foughtZarg = True
                if object.name == 'spellbook of fireball' and not displayedSpell and object.distanceTo(player) <= 10:
                    displayedSpell = True
                    displayTip("This spellbook, when used, will learn you a new spell. In order to cast it, you have to press 'z'.", object.x - 1, object.y)
                if object.Fighter and object.Fighter.spellsOnCooldown and object.Fighter is not None:
                    try:
                        for spell in object.Fighter.spellsOnCooldown:
                            spell.curCooldown -= 1
                            if spell.curCooldown < 0:
                                spell.curCooldown = 0
                            if spell.curCooldown == 0:
                                print('{} spell is at 0 cooldown. On recover learn:'.format(spell.name), spell.onRecoverLearn)
                                if not spell.onRecoverLearn:
                                    print('spell has no onrecoverlearn')
                                    object.Fighter.spellsOnCooldown.remove(spell)
                                    object.Fighter.knownSpells.append(spell)
                                    if object == player:
                                        message(spell.name + " is now ready.")
                                else:
                                    print('spell has some recoverlearn:')
                                    if object == player:
                                        message(spell.name + " is now ready.")
                                    for newSpell in spell.onRecoverLearn:
                                        print(newSpell.name)
                                        object.Fighter.knownSpells.append(newSpell)
                                    object.Fighter.spellsOnCooldown.remove(spell)
                    except Exception as error:
                        traceback.print_exc()
                        message("OMG SPELLS NOT WORKING SEE CONSOLE", colors.red)
                        continue
                else:
                    if object.Fighter:
                        print("{} has no spell on cooldown".format(object.name))
                    
                if object.Fighter and object.Fighter is not None: #If object is a creature
                    for buff in object.Fighter.buffList:
                        buff.passTurn()
                
                if object.Fighter and object.Fighter.MP < object.Fighter.maxMP and object.Fighter is not None:
                    object.Fighter.MPRegenCountdown -= 1
                    if object.Fighter.MPRegenCountdown < 0:
                        object.Fighter.MPRegenCountdown = 0
                    if object.Fighter.MPRegenCountdown == 0:
                        if object == player:
                            regen = 10 - player.Player.willpower
                            if regen <= 0:
                                regen = 1
                            object.Fighter.MPRegenCountdown = regen
                        else:
                            object.Fighter.MPRegenCountdown = 10
                        object.Fighter.MP += 1
    
                if object.Player is not None:
                    if NATURAL_REGEN:
                        monsterInSight = False
                        for monster in objects:
                            if monster.Fighter and not monster == player and (monster.x, monster.y) in visibleTiles:
                                monsterInSight = True
                                break
                        if not 'burning' in convertBuffsToNames(player.Fighter) and not 'frozen' in convertBuffsToNames(player.Fighter) and player.Fighter.hp != player.Fighter.maxHP and not monsterInSight and not 'poisoned' in convertBuffsToNames(player.Fighter) and not 'stunned' in convertBuffsToNames(player.Fighter): #and not player.Player.hungerStatus == 'starving' 
                            player.Fighter.healCountdown -= 1
                            if player.Fighter.healCountdown < 0:
                                player.Fighter.healCountdown = 0
                            if player.Fighter.healCountdown == 0:
                                player.Fighter.heal(1)
                                player.Fighter.healCountdown= 25 - player.Player.vitality

            if hasSpokenToGeneral and not givenSword:
                swordX, swordY = player.x - 1, player.y
                while (swordX, swordY) == (generalObject.x, generalObject.y):
                    swordY += 1
                swordComponent = Equipment(slot='one handed', type = 'light weapon', powerBonus = 18, meleeWeapon=True)
                sword = GameObject(swordX, swordY, '-', 'Equinox', colors.silver, Equipment = swordComponent, Item = Item(weight=3.5, pic = 'longSword.xp', useText='Equip'), noPronoun = True) #TO-DO : Make this a true legendary unique
                objects.append(sword)
                message("General Guillem says: 'Here, take my sword. It shall help you defeat the greatest foes.'", colors.gold)
                givenSword = True  
                
            while mustCalculate:
                print("Calculating")
                if myMap is None:
                    raise TypeError("MYMAP IS NONE, PATH LOOP START")
                    traceback.print_exc()
                    os._exit(-1)
                pathfinders = []
                mustCalculate = False
                print(len(mobsToCalculate))
                for mob in mobsToCalculate:
                    if myMap is None:
                        raise TypeError("MYMAP IS NONE, BEFORE PATHFINDER CREATE START")
                        traceback.print_exc()
                        os._exit(-1)
                    newPathfinder = Pathfinder(mob, mob.AI.selectedTarget.x, mob.AI.selectedTarget.y)
                    if myMap is None:
                        raise TypeError("MYMAP IS NONE, AFTER PATHFINDER CREATE")
                        traceback.print_exc()
                        os._exit(-1)
                    pathfinders.append(newPathfinder)
                    
                for pathfind in pathfinders:
                    if myMap is None:
                        raise TypeError("MYMAP IS NONE, BEFORE PATHFIND THREAD START")
                        traceback.print_exc()
                        os._exit(-1)
                    pathfind.start()
                for pathfind in pathfinders:
                    pathfind.join()
                
                for mob in mobsToCalculate:
                    if myMap is None:
                        raise TypeError("MYMAP IS NONE, TRY MOVE START")
                        traceback.print_exc()
                        os._exit(-1)
                    mob.AI.tryMove()
                    
            global stairCooldown
            if stairCooldown > 0:
                stairCooldown -= 1
                if stairCooldown == 0 and DEBUG:
                    message("You're no longer tired", colors.purple)
            if stairCooldown < 0:
                stairCooldown = 0
                
            ### HUNGER REMOVED ###
            '''
            player.Player.hunger -= 1
            if player.Player.hunger > BASE_HUNGER:
                player.Player.hunger = BASE_HUNGER
            if player.Player.hunger < 0:
                player.Player.hunger = 0
            if player.Player.hunger <= round(BASE_HUNGER /10):
                if not player.Player.hungerStatus == 'starving':
                    starving = Buff('starving', colors.red, cooldown = 99999, showCooldown = False, continuousFunction = lambda fighter: randomDamage('starvation', fighter, chance = 33, minDamage = 1, maxDamage = 1, dmgMessage = 'You are starving!', dmgColor = colors.red, msgPlayerOnly = True, dmgType={'none': 100}))
                    starving.applyBuff(player)
                    player.Player.hungerStatus = "starving"
                #starveDamage = randint(0, 2)
                #if starveDamage == 0:
                #    player.Fighter.takeDamage(1)
                #    message("You're starving !", colors.red)
            elif player.Player.hunger <= BASE_HUNGER // 2:
                prevStatus = player.Player.hungerStatus
                player.Player.hungerStatus = "hungry"
                if prevStatus == "full":
                    message("You're starting to feel a little bit hungry.", colors.yellow)
                elif prevStatus == "starving":
                    message("You're no longer starving")
                    for buff in player.Fighter.buffList:
                        if buff.name == 'starving':
                            buff.removeBuff()
            else:
                prevStatus = player.Player.hungerStatus
                player.Player.hungerStatus = "full"
                if prevStatus != "full":
                    message("You feel way less hungry")
                if prevStatus == 'starving':
                    for buff in player.Fighter.buffList:
                        if buff.name == 'starving':
                            buff.removeBuff()
            '''

    DEBUG = False
    #quitGame('Window has been closed')
    playGame()

def drawDetectionStatus():
    global detectedPlayerThisTurn
    for monster in objects:
        if monster in detectedPlayerThisTurn:
            monster.detectionStatus = '!'
        elif monster.AI:
            if monster.AI.detectedPlayer:
                monster.detectionStatus = None
            else:
                monster.detectionStatus = '?'
        if monster.AI and (monster.x, monster.y) in visibleTiles:
            if monster.detectionStatus is None:
                fg = None
            else:
                fg = monster.color
            root.draw_char(monster.x, monster.y - 1, monster.detectionStatus, fg, None)
    tdl.flush()
    detectedPlayerThisTurn = []
    
#ISN project
def playGame(noSave = False):
    global currentMusic, monstersDetected, FOV_recompute, DEBUG, actions
    if currentMusic is None or currentMusic in ('No_Music.wav', 'Dusty_Feelings.wav'):
        currentMusic = 'Bumpy_Roots.wav'
    stopProcess()
    music = multiprocessing.Process(target = mus.runMusic, args = (currentMusic,))
    music.start()
    activeProcess.append(music)
    #actions = 1
    while True:
        #checkLevelUp()
        for trait in player.Player.unlockableTraits:
            trait.checkForRequirements()
        Update()

        if SIDE_PANEL_MODES[currentSidepanelMode] == 'stealth':
            drawDetectionStatus()
        tdl.flush()
        for object in objects:
            object.clear()
        
        endedTurn = False
        player.Player.hitThisTurn = False
        while player.Fighter.actionPoints > 0 and not endedTurn:
            playerAction = getInput()
            if bossTiles:
                bossFleeDjik()
                print("Did Boss Djik")
            FOV_recompute = True
            Update()
            checkLevelUp()
            tdl.flush()
            for object in objects:
                object.clear()
            if playerAction == 'end turn':
                endedTurn = True
                if player.Fighter.actionPoints > 0:
                    player.Fighter.actionPoints = 0
                break
            try:
                player.Fighter.actionPoints -= ACTION_COSTS[playerAction]
            except:
                pass
            if playerAction == 'exit':
                quitGame('Player pressed escape', True, noSave)
            
        '''
        if player.Player.attackedSlowly:
            message('You are too focused on recovering from your slow attack to move this turn!', colors.dark_flame)
            player.Player.slowAttackCooldown -= 1
            if player.Player.slowAttackCooldown <= 0:
                player.Player.attackedSlowly = False
        else:
            for loop in range(actions):
                playerAction = getInput()
                if bossTiles:
                    bossFleeDjik()
                    print("Did Boss Djik")
                if actions > 1:
                    FOV_recompute = True
                    Update()
                    checkLevelUp()
                    tdl.flush()
                    for object in objects:
                        object.clear()
                if playerAction == 'exit':
                    quitGame('Player pressed escape', True, noSave)
        '''
        checkLevelUp()
        FOV_recompute = True #So as to avoid the blackscreen bug no matter which key we press
        if gameState == 'playing' and playerAction != 'didnt-take-turn':
            global mobsToCalculate
            global mustCalculate
            mobsToCalculate = []
            
            newList = [[],[],[],[],[]]
            for i, list in enumerate(monstersDetected):
                if i < 4:
                    newList[i + 1] = list
            monstersDetected = newList
            
            for object in objects:
                if object.AI:
                    try:
                        object.AI.takeTurn()
                        object.Fighter.actionPoints += 100
                    except TypeError as error:
                        print("==================WARNING===================")
                        print(type(error))
                        print(error.args)
                        print(object.name)
                        try:
                            message('CRITICAL AI ERROR SEE CONSOLE FOR DETAILS', colors.red)
                        except Exception as error:
                            print("==================WARNING===================")
                            print("COULDNT PRINT MESSAGE")
                            print(type(error))
                            print(error.args)
                            print(object.name)
                            print("============================================")
                        print("============================================")
                if object.Fighter and object.Fighter.baseShootCooldown > 0 and object.Fighter is not None:
                    object.Fighter.curShootCooldown -= 1
                if object.Fighter and object.Fighter.baseLandCooldown > 0 and object.Fighter is not None:
                    object.Fighter.curLandCooldown -= 1
                
                if object.Projectile:
                    object.Projectile.moveOnPath()
    
                if object.Fighter and object.Fighter.spellsOnCooldown and object.Fighter is not None:
                    try:
                        for spell in object.Fighter.spellsOnCooldown:
                            spell.curCooldown -= 1
                            if spell.curCooldown < 0:
                                spell.curCooldown = 0
                            if spell.curCooldown == 0:
                                if not spell.onRecoverLearn:
                                    object.Fighter.spellsOnCooldown.remove(spell)
                                    object.Fighter.knownSpells.append(spell)
                                    if object == player:
                                        message(spell.name + " is now ready.")
                                else:
                                    if object == player:
                                        message(spell.name + " is now ready.")
                                    for newSpell in spell.onRecoverLearn:
                                        object.Fighter.knownSpells.append(newSpell)
                                    object.Fighter.spellsOnCooldown.remove(spell)
                    except Exception as error:
                        traceback.print_exc()
                        message("OMG SPELLS NOT WORKING SEE CONSOLE", colors.red)
                        continue
                else:
                    if object.Fighter:
                        print("{} has no spell on cooldown".format(object.name))
                
                if object.Fighter and object.Fighter.MP < object.Fighter.maxMP and object.Fighter is not None:
                    object.Fighter.MPRegenCountdown -= 1
                    if object.Fighter.MPRegenCountdown < 0:
                        object.Fighter.MPRegenCountdown = 0
                    if object.Fighter.MPRegenCountdown == 0:
                        if object == player:
                            regen = 10 - player.Player.willpower
                            if regen <= 0:
                                regen = 1
                            object.Fighter.MPRegenCountdown = regen
                        else:
                            object.Fighter.MPRegenCountdown = 10
                        object.Fighter.MP += 1
    
                if object.Fighter and object.Fighter.stamina < object.Fighter.maxStamina and object.Fighter is not None:
                    object.Fighter.staminaRegenCountdown -= 1
                    if object.Fighter.staminaRegenCountdown < 0:
                        object.Fighter.staminaRegenCountdown = 0
                    if object.Fighter.staminaRegenCountdown == 0:
                        if object == player:
                            regen = 15 - player.Player.vitality
                            if regen <= 0:
                                regen = 1
                            object.Fighter.staminaRegenCountdown = regen
                        else:
                            object.Fighter.staminaRegenCountdown = 15
                        object.Fighter.stamina += 1
                if object.Player is not None:
                    if NATURAL_REGEN:
                        monsterInSight = False
                        for monster in objects:
                            if monster.Fighter and not monster == player and (monster.x, monster.y) in visibleTiles:
                                monsterInSight = True
                                break
                        if not 'burning' in convertBuffsToNames(player.Fighter) and not 'frozen' in convertBuffsToNames(player.Fighter) and player.Fighter.hp != player.Fighter.maxHP and not monsterInSight and not 'poisoned' in convertBuffsToNames(player.Fighter): #and not player.Player.hungerStatus == 'starving' 
                            player.Fighter.healCountdown -= 1
                            if player.Fighter.healCountdown < 0:
                                player.Fighter.healCountdown = 0
                            if player.Fighter.healCountdown == 0:
                                player.Fighter.heal(1)
                                player.Fighter.healCountdown= 25 - player.Player.vitality
    
                if object.Player and object.Player.race == 'Werewolf':
                    if object.Player.shapeshifted:
                        def shapeshift(fighter, fromWolf = False, fromHuman = True):
                            if fromWolf:
                                player.Player.shapeshift = 'human'
                                player.Player.shapeshifted = True
                            if fromHuman:
                                player.Player.shapeshift = 'wolf'
                                player.Player.shapeshifted = True
                        
                        #wild = player.Player.getTrait('trait', 'Wild instincts').selected
                        wolfCooldown = player.Player.wolf
                        humanCooldown = player.Player.human
                        strenBonus = 5
                        dexBonus = 3
                        vitBonus = 4
                        willMalus = -5
                        #if wild:
                        #    wolfCooldown += randint(0, 30)
                        #    humanCooldown += randint(-75, 75)
                        #    strenBonus += randint(-3, 3)
                        #    dexBonus += randint(-2, 2)
                        #    vitBonus += randint(-3, 3)
                        #    willMalus += randint(-2, 2)
                        human = Buff('human', colors.lightest_yellow, cooldown = humanCooldown, showBuff = False, removeFunction = lambda fighter: shapeshift(fighter), resistible = False)
                        wolf = Buff('in wolf form', colors.amber, cooldown = wolfCooldown, strength = strenBonus, dexterity = dexBonus, constitution = vitBonus, willpower = willMalus, removeFunction = lambda fighter: shapeshift(fighter, fromHuman=False, fromWolf=True), resistible = False)
                        if object.Player.shapeshift == 'wolf':
                            message('You feel your wild instincts overwhelming you! You have turned into your wolf form!', colors.amber)
                            wolf.applyBuff(player)
                            learnSpell(leap, True)
                            object.Player.shapeshifted = False
                        if object.Player.shapeshift == 'human':
                            human.applyBuff(player)
                            object.Player.shapeshifted = False
                            for spell in player.Fighter.allSpells:
                                if spell.name == 'Leap':
                                    unlearnSpell(spell, True)
                
                if object.Player and object.Player.race == 'Virus ':
                    if object.Player.inHost:
                        object.Player.hostDeath -= 1
                        if object.Player.hostDeath <= 0:
                            message('Your host has died! You must quickly find another one!', colors.red)
                            object.Player.inHost = False
                            object.Player.timeOutsideLeft = 50
                    else:
                        object.Player.timeOutsideLeft -= 1
                        message('You only have {} turns left!'.format(object.Player.timeOutsideLeft), colors.red)
                        if object.Player.timeOutsideLeft <= 0:
                            object.Fighter.takeDamage(999, 'the lack of host')
                
                if object.Fighter and player.Player.race == 'Reptilian' and not (object.x, object.y) in visibleTiles:
                    print(object.name, 'is eligible for rept detection. dist = ', object.distanceTo(player))
                    dice = randint(1, 100)
                    print(dice)
                    if object.distanceTo(player) <= player.Player.reptSightRange and dice <= player.Player.reptSightChance:
                        print('monster is detected')
                        monstersDetected[0].append(object)
            #ISN project
            #for object in objects:    
                if object.Fighter and object.Fighter is not None: #If object is a creature
                    for buff in object.Fighter.buffList:
                        buff.passTurn() #Call passTurn method of each of his buffs
                
                    for tileBuff in myMap[object.x][object.y].buffList:
                        for buff in tileBuff.buffsWhenWalked:
                            buff.applyBuff(object)
    
            for x in range(MAP_WIDTH):
                for y in range(MAP_HEIGHT):
                    if myMap[x][y].buffList:
                        for tileBuff in myMap[x][y].buffList:
                            tileBuff.passTurn()
            while mustCalculate:
                print("Calculating")
                pathfinders = [] 
                mustCalculate = False
                print(len(mobsToCalculate))
                for mob in mobsToCalculate:
                    if mob.AI:
                        newPathfinder = Pathfinder(mob, mob.AI.selectedTarget.x, mob.AI.selectedTarget.y, mapToUse= myMap)
                        pathfinders.append(newPathfinder)
                    
                for pathfind in pathfinders:
                    pathfind.start()
                for pathfind in pathfinders:
                    pathfind.join()
                
                for mob in mobsToCalculate:
                    mob.AI.tryMove()
                
            global stairCooldown
            if stairCooldown > 0:
                stairCooldown -= 1
                if stairCooldown == 0 and DEBUG:
                    message("You're no longer tired", colors.purple)
            if stairCooldown < 0:
                stairCooldown = 0
            
            ### HUNGER REMOVED ###
            '''
            player.Player.hunger -= 1
            if player.Player.hunger > BASE_HUNGER:
                player.Player.hunger = BASE_HUNGER
            if player.Player.hunger < 0:
                player.Player.hunger = 0
            if player.Player.hunger <= round(BASE_HUNGER / 10):
                if not player.Player.hungerStatus == 'starving':
                    starving = Buff('starving', colors.red, cooldown = 99999, showCooldown = False, continuousFunction = lambda fighter: randomDamage('starvation', fighter, chance = 33, minDamage = 1, maxDamage = 1, dmgMessage = 'You are starving!', dmgColor = colors.red, msgPlayerOnly = True, dmgType={'none': 100}))
                    starving.applyBuff(player)
                    player.Player.hungerStatus = "starving"
                #starveDamage = randint(0, 2)
                #if starveDamage == 0:
                #    player.Fighter.takeDamage(1)
                #    message("You're starving !", colors.red)
            elif player.Player.hunger <= BASE_HUNGER // 2:
                prevStatus = player.Player.hungerStatus
                player.Player.hungerStatus = "hungry"
                if prevStatus == "full":
                    message("You're starting to feel a little bit hungry.", colors.yellow)
                elif prevStatus == "starving":
                    message("You're no longer starving")
                    for buff in player.Fighter.buffList:
                        if buff.name == 'starving':
                            buff.removeBuff()
            else:
                prevStatus = player.Player.hungerStatus
                player.Player.hungerStatus = "full"
                if prevStatus != "full":
                    message("You feel way less hungry")        
            '''

        ratioHP = round((player.Fighter.hp / player.Fighter.maxHP) * 100)
        for trait in player.Player.allTraits:
            if trait.name == 'Rage' and trait.selected:
                if ratioHP <= 25 and not 'enraged' in convertBuffsToNames(player.Fighter):
                    enraged = Buff('uncontrollable', colors.dark_red, cooldown = 99999, power = 10, resistible = False)
                    enraged.applyBuff(player)
                break
        
        if 'uncontrollable' in convertBuffsToNames(player.Fighter) and ratioHP > 25:
            buff.removeBuff()
        
        '''
        actions = 1
        if player.Player.speed == 'fast' and randint(1, 100) <= player.Player.speedChance:
            message('Your great speed allows you to take two actions this turn!', colors.green)
            actions += 1
        if player.Player.speed == 'slow' and randint(1, 100) <= player.Player.speedChance:
            message('Your incredible slowness prevents you from taking any action this turn', colors.red)
            actions -= 1
        '''
        player.Fighter.actionPoints += 100
        
    DEBUG = False
    quitGame('Window has been closed', noSave = noSave)
    
if (__name__ == '__main__' or __name__ == 'main__main__') and root is not None:
    #loadLevel('main5') #only a test
    freeze_support()
    convertMusics()
    '''
    hiddenPath = findHiddenOptionsPath()
    if not os.path.exists(hiddenPath):
        launchTutorial(False)
    '''
    tempName = getHeroName()
    if tempName is None:
        heroName = None
        launchTutorial(False)
    else:
        heroName = tempName
        
    applyOptions()
        
    mainMenu()
else:
    print(__name__)
#input()

#XXX
#XOX
#XXX

#    XXX
# X  XXX  5x5  7x7
#    XXX
