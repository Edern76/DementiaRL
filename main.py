import tdl
from tdl import *
from random import randint

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

WIDTH, HEIGHT, LIMIT = 120, 100, 20
MAP_WIDTH, MAP_HEIGHT = 100, 60
MID_WIDTH, MID_HEIGHT = int(WIDTH/2), int(HEIGHT/2)
root = tdl.init(WIDTH, HEIGHT, 'Dementia (Temporary Name) | Prototype')
con = tdl.Console(WIDTH, HEIGHT)

FOV_recompute = True
FOV_ALGO = 'BASIC'
FOV_LIGHT_WALLS = True
SIGHT_RADIUS = 10

myMap = [[]]
color_dark_wall = (28, 28, 28)
color_light_wall = (130, 110, 50)
color_dark_ground = (66, 66, 66)
color_light_ground = (200, 180, 50)

class GameObject:
    "A generic object, represented by a character"
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move(self, dx, dy):
        if not myMap[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy
    
    def draw(self):
        con.draw_char(self.x, self.y, self.char, self.color, bg=None)
        
    def clear(self):
        con.draw_char(self.x, self.y, ' ', self.color, bg=None)

class Player(GameObject):
    def __init__(self, x, y, char, maxHP):
        self.maxHP = maxHP
        self.hp = self.maxHP
        self.color = (0, 255, 0)
        GameObject.__init__(self, x, y, char, self.color)
        
    def changeColor(self):
        self.hpRatio = ((self.hp / self.maxHP) * 100)
        if self.hpRatio < 95 and self.hpRatio >= 75:
            self.color = (120, 255, 0)
        elif self.hpRatio < 75 and self.hpRatio >= 50:
            self.color = (255, 255, 0)
        elif self.hpRatio < 50 and self.hpRatio >= 25:
            self.color = (255, 120, 0)
        elif self.hpRatio < 25 and self.hpRatio > 0:
            self.color = (255, 0, 0)
        elif self.hpRatio == 0:
            self.color = (120, 0, 0)
    
    def takeDamage(self, damage):
        self.hp -= damage

def quitGame(message):
    raise SystemExit(str(message))

def getInput():
    global FOV_recompute
    userInput = tdl.event.key_wait()
    if userInput.keychar.upper() in MOVEMENT_KEYS:
        keyX, keyY = MOVEMENT_KEYS[userInput.keychar.upper()]
        player.move(keyX, keyY)
        FOV_recompute = True
    elif userInput.keychar.upper() ==  'ESCAPE':
        quitGame('Player pressed Escape')
    #elif userInput.keychar.upper() == 'ALT' and userInput.alt:
        #isFullscreen = tdl.getFullscreen()
        #print("Fullscreen is borked at the moment")
        #if isFullscreen :
            #set_fullscreen(False)
        #else:
            #set_fullscreen(True)
    elif userInput.keychar.upper() == 'F2':
        player.takeDamage(1)
    for event in tdl.event.get():
        if event.type == 'QUIT':
            quitGame('Window has been closed')

def isVisibleTile(x, y):
    global my_map
 
    if x >= MAP_WIDTH or x < 0:
        return False
    elif y >= MAP_HEIGHT or y < 0:
        return False
    elif myMap[x][y].blocked == True:
        return False
    elif myMap[x][y].block_sight == True:
        return False
    else:
        return True

#_____________ MAP CREATION __________________
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

class Tile:
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
        if block_sight is None:
            block_sight = blocked
            self.block_sight = block_sight

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
        
def createRoom(room):
    global myMap
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            myMap[x][y].blocked = False
            myMap[x][y].block_sight = False
            
def createHorizontalTunnel(x1, x2, y):
    global myMap
    for x in range(min(x1, x2), max(x1, x2) + 1):
        myMap[x][y].blocked = False
        myMap[x][y].block_sight = False
            
def createVerticalTunnel(y1, y2, x):
    global myMap
    for y in range(min(y1, y2), max(y1, y2) + 1):
        myMap[x][y].blocked = False
        myMap[x][y].block_sight = False
        
def makeMap():
    global myMap
    myMap = [[Tile(True) for y in range(MAP_HEIGHT)]for x in range(MAP_WIDTH)]
    rooms = []
    numberRooms = 0
 
    for r in range(MAX_ROOMS):
        w = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        x = randint(0, MAP_WIDTH-w-1)
        y = randint(0, MAP_HEIGHT-h-1)
        newRoom = Rectangle(x, y, w, h)
        intersection = False
        for otherRoom in rooms:
            if newRoom.intersect(otherRoom):
                intersection = True
                break
        if not intersection:
            createRoom(newRoom)
            (new_x, new_y) = newRoom.center()
 
            if numberRooms == 0:
                player.x = new_x
                player.y = new_y
            else:
                (previous_x, previous_y) = rooms[numberRooms-1].center()
                if randint(0, 1):
                    createHorizontalTunnel(previous_x, new_x, previous_y)
                    createVerticalTunnel(previous_y, new_y, new_x)
                else:
                    createVerticalTunnel(previous_y, new_y, previous_x)
                    createHorizontalTunnel(previous_x, new_x, new_y)
            rooms.append(newRoom)
            numberRooms += 1

#_____________ MAP CREATION __________________

def Update():
    global FOV_recompute
    global visibleTiles
    con.clear()
    tdl.flush()
    player.changeColor()
    con.draw_str(1, 1, '{} / {}'.format(player.hp, player.maxHP), fg = (255,0,0), bg = None)
    if FOV_recompute:
        FOV_recompute = False
        visibleTiles = tdl.map.quickFOV(player.x, player.y, isVisibleTile, fov = FOV_ALGO, radius = SIGHT_RADIUS, lightWalls = FOV_LIGHT_WALLS)
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = (x, y) in visibleTiles
                wall = myMap[x][y].block_sight
                if not visible:
                    if wall:
                        con.draw_char(x, y, '#', fg=color_dark_wall, bg=color_dark_ground)
                    else:
                        con.draw_char(x, y, None, fg=None, bg=color_dark_ground)
                else:
                    if wall:
                        con.draw_char(x, y, '#', fg=color_light_wall, bg=color_light_ground)
                    else:
                        con.draw_char(x, y, None, fg=None, bg=color_light_ground)
    for object in objects:
        if (object.x, object.y) in visibleTiles:
            object.draw()
    root.blit(con, 0, 0, WIDTH, HEIGHT, 0, 0)

npc = GameObject(MID_WIDTH, MID_HEIGHT, 'X', (0, 200, 255))
player = Player(25, 23, '@', 100)
objects = [npc, player]
makeMap()
Update()

FOV_recompute = True

while True :
    Update()
    tdl.flush()
    for object in objects:
        object.clear()
    getInput()

        
    
    