import tdl
from tdl import *

MOVEMENT_KEYS = {
                 # Fleches standard
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
myMap = [[]]
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

class Tile:
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
        if block_sight is None:
            block_sight = blocked
            self.block_sight = block_sight

def quitGame(message):
    raise SystemExit(str(message))
def getInput():
    userInput = tdl.event.key_wait()
    if userInput.keychar.upper() in MOVEMENT_KEYS:
        keyX, keyY = MOVEMENT_KEYS[userInput.keychar.upper()]
        player.move(keyX, keyY)
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
def Update():
    con.clear()
    tdl.flush()
    player.changeColor()
    con.draw_str(1, 1, '{} / {}'.format(player.hp, player.maxHP), fg = (255,0,0), bg = None)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall = myMap[x][y].block_sight
            if wall:
                con.draw_char(x, y, '#')
            else:
                con.draw_char(x, y, '.')
    for object in objects:
        object.draw()
    root.blit(con, 0, 0, WIDTH, HEIGHT, 0, 0)
def makeMap():
    global myMap
    myMap = [[Tile(False) for y in range(MAP_HEIGHT)]for x in range(MAP_WIDTH)]
    myMap[30][22].blocked = True
    myMap[30][22].block_sight = True
    myMap[50][22].blocked = True
    myMap[50][22].block_sight = True    
    
npc = GameObject(MID_WIDTH - 5, MID_HEIGHT, '@', (0, 200, 255))
player = Player(MID_WIDTH, MID_HEIGHT, '@', 100)
objects = [npc, player]
makeMap()
Update()

while True :
    Update()
    tdl.flush()
    for object in objects:
        object.clear()
    getInput()

        
    
    