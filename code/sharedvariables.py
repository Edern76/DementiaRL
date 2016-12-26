import colors, sys, os

myMap = None
color_dark_wall = colors.darkest_grey
color_light_wall = colors.darker_grey
color_dark_ground = colors.darkest_sepia
color_light_ground = colors.darker_sepia

gameState = 'playing'
playerAction = None
DEBUG = False #If true, enables debug messages

lookCursor = None
cursor = None

gameMsgs = [] #List of game messages
tilesInRange = []
explodingTiles = []
tilesinPath = []
hiroshimanNumber = 0
FOV_recompute = True
inventory = []
equipmentList = []
objects = []
stairs = None
upStairs = None
hiroshimanHasAppeared = False
player = None
dungeonLevel = 1

def findCurrentDir():
    if getattr(sys, 'frozen', False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)
    return datadir

curDir = findCurrentDir()
relDirPath = "save"
relPath = "save\\savegame"
relPicklePath = "save\\equipment"
absDirPath = os.path.join(curDir, relDirPath)
absFilePath = os.path.join(curDir, relPath)
absPicklePath = os.path.join(curDir, relPicklePath)

stairCooldown = 0
