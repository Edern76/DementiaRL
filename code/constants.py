import tdl
from tdl import *

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

WIDTH, HEIGHT, LIMIT = 170, 95, 20
MAP_WIDTH, MAP_HEIGHT = 140, 60
MID_WIDTH, MID_HEIGHT = int(WIDTH/2), int(HEIGHT/2)

# - GUI Constants -
BAR_WIDTH = 20

PANEL_HEIGHT = 10
PANEL_Y = HEIGHT - PANEL_HEIGHT

MSG_X = BAR_WIDTH + 10
MSG_WIDTH = WIDTH - BAR_WIDTH - 10
MSG_HEIGHT = PANEL_HEIGHT - 1

INVENTORY_WIDTH = 90

LEVEL_SCREEN_WIDTH = 40
CHARACTER_SCREEN_WIDTH = 30
# - GUI Constants -

# - Consoles -
root = tdl.init(WIDTH, HEIGHT, 'Dementia (Temporary Name) | Prototype')
con = tdl.Console(WIDTH, HEIGHT)
panel = tdl.Console(WIDTH, PANEL_HEIGHT)
# - Consoles

FOV_recompute = True
FOV_ALGO = 'BASIC'
FOV_LIGHT_WALLS = True
SIGHT_RADIUS = 10
MAX_ROOM_MONSTERS = 3
MAX_ROOM_ITEMS = 5
GRAPHICS = 'modern'
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150
NATURAL_REGEN = False

# - Spells -
LIGHTNING_DAMAGE = 20
LIGHTNING_RANGE = 5
CONFUSE_NUMBER_TURNS = 10
CONFUSE_RANGE = 8
DARK_PACT_DAMAGE = 12
# - Spells -