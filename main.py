import tdl, colors, math, textwrap, time, os, shelve, pickle
from tdl import *
from random import randint
from math import *
from os import makedirs
from copy import deepcopy


# Naming conventions :
# MY_CONSTANT
# myVariable
# myFunction()
# MyClass
# Not dramatic if you forget about this (it happens to me too), but it makes reading code easier

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

INVENTORY_WIDTH = 50

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

# - Spells -
LIGHTNING_DAMAGE = 20
LIGHTNING_RANGE = 5
CONFUSE_NUMBER_TURNS = 10
CONFUSE_RANGE = 8
# - Spells -

myMap = [[]]
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
hiroshimanNumber = 0
FOV_recompute = True
inventory = []
stairs = None
hiroshimanHasAppeared = False
player = None

curDir = os.path.dirname(__file__)
relDirPath = "save"
relPath = "save\\savegame"
relPicklePath = "save\\map"
absDirPath = os.path.join(curDir, relDirPath)
absFilePath = os.path.join(curDir, relPath)
absPicklePath = os.path.join(curDir, relPicklePath)


#_____________ CONSTANTS __________________
def closestMonster(max_range):
    closestEnemy = None
    closestDistance = max_range + 1

    for object in objects:
        if object.Fighter and not object == player and (object.x, object.y) in visibleTiles:
            dist = player.distanceTo(object)
            if dist < closestDistance:
                closestEnemy = object
                closestDistance = dist
    return closestEnemy

class GameObject:
    "A generic object, represented by a character"
    def __init__(self, x, y, char, name, color = colors.white, blocks = False, Fighter = None, AI = None, Player = None, Ghost = False, Item = None, alwaysVisible = False, darkColor = None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.blocks = blocks
        self.name = name
        self.Fighter = Fighter
        self.Player = Player
        self.ghost = Ghost
        self.Item = Item
        self.alwaysVisible = alwaysVisible
        self.darkColor = darkColor
        if self.Fighter:  #let the fighter component know who owns it
            self.Fighter.owner = self
        self.AI = AI
        if self.AI:  #let the AI component know who owns it
            self.AI.owner = self
        if self.Player:
            self.Player.owner = self
        if self.Item:
            self.Item.owner = self 
            
    def moveTowards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def move(self, dx, dy):
        if self.Fighter and self.Fighter.frozen:
            pass
        elif not isBlocked(self.x + dx, self.y + dy) or self.ghost:
            self.x += dx
            self.y += dy
    
    def draw(self):
        if (self.x, self.y) in visibleTiles:
            con.draw_char(self.x, self.y, self.char, self.color, bg=None)
        elif self.alwaysVisible and myMap[self.x][self.y].explored:
            con.draw_char(self.x, self.y, self.char, self.darkColor, bg=None)
        
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

class Fighter: #All NPCs, enemies and the player
    def __init__(self, hp, defense, power, xp, deathFunction=None):
        self.maxHP = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.deathFunction = deathFunction
        self.xp = xp
        
        self.frozen = False
        self.freezeCooldown = 0
        
        self.burning = False
        self.burnCooldown = 0
        
    def takeDamage(self, damage):
        if damage > 0:
            self.hp -= damage
        if self.hp <= 0:
            death=self.deathFunction
            if death is not None:
                death(self.owner)
            if self.owner != player:
                player.Fighter.xp += self.xp

    def attack(self, target):
        damage = self.power - target.Fighter.defense
 
        if not self.frozen:
            if not self.owner.Player:
                if damage > 0:
                    message(self.owner.name.capitalize() + ' attacks you for ' + str(damage) + ' hit points.', colors.orange)
                    target.Fighter.takeDamage(damage)
                else:
                    message(self.owner.name.capitalize() + ' attacks you but it has no effect!')
            else:
                if damage > 0:
                    message('You attack ' + target.name + ' for ' + str(damage) + ' hit points.', colors.dark_green)
                    target.Fighter.takeDamage(damage)
                else:
                    message('You attack ' + target.name + ' but it has no effect!', colors.lighter_grey)
        
    def heal(self, amount):
        self.hp += amount
        if self.hp > self.maxHP:
            self.hp = self.maxHP

class BasicMonster: #Basic monsters' AI
    def takeTurn(self):
        monster = self.owner
        if (monster.x, monster.y) in visibleTiles: #chasing the player
            if monster.distanceTo(player) >= 2:
                monster.moveTowards(player.x, player.y)
            elif player.Fighter.hp > 0:
                monster.Fighter.attack(player)
        else:
            monster.move(randint(-1, 1), randint(-1, 1)) #wandering

class SplosionAI:
    def takeTurn(self):
        monster = self.owner
        if (monster.x, monster.y) in visibleTiles: #chasing the player
            if monster.distanceTo(player) >= 3:
                monster.moveTowards(player.x, player.y)
            elif player.Fighter.hp > 0 and not monster.Fighter.frozen:
                monsterArmageddon(monster.name, monster.x, monster.y)
        else:
            monster.move(randint(-1, 1), randint(-1, 1))

class ConfusedMonster:
    def __init__(self, old_AI, numberTurns=CONFUSE_NUMBER_TURNS):
        self.old_AI = old_AI
        self.numberTurns = numberTurns
 
    def takeTurn(self):
        if self.numberTurns > 0:  
            self.owner.move(randint(-1, 1), randint(-1, 1))
            self.numberTurns -= 1
 
        else:
            self.owner.AI = self.old_AI
            message('The ' + self.owner.name + ' is no longer confused!', colors.red)

class Player:
    def __init__(self):
        if DEBUG:
            print('Player component initialized')
        
    def changeColor(self):
        self.hpRatio = ((self.owner.Fighter.hp / self.owner.Fighter.maxHP) * 100)
        if self.hpRatio < 95 and self.hpRatio >= 75:
            self.owner.color = (120, 255, 0)
        elif self.hpRatio < 75 and self.hpRatio >= 50:
            self.owner.color = (255, 255, 0)
        elif self.hpRatio < 50 and self.hpRatio >= 25:
            self.owner.color = (255, 120, 0)
        elif self.hpRatio < 25 and self.hpRatio > 0:
            self.owner.color = (255, 0, 0)
        elif self.hpRatio == 0:
            self.owner.color = (120, 0, 0)

class Item:
    def __init__(self, useFunction = None,  arg1 = None, arg2 = None, arg3 = None):
        self.useFunction = useFunction
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
    def pickUp(self):
        if len(inventory)>=26:
            message('Your bag already feels really heavy, you cannot pick up' + self.owner.name + '.', colors.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', colors.green)
    def use(self):
        if self.useFunction is None:
            message('The' + self.owner.name + 'cannot be used !')
            return 'cancelled'
        else:
            if self.arg1 is None:
                if self.useFunction() != 'cancelled':
                    inventory.remove(self.owner)
                else:
                    return 'cancelled'
            elif self.arg2 is None and self.arg1 is not None:
                if self.useFunction(self.arg1) != 'cancelled':
                    inventory.remove(self.owner)
                else:
                    return 'cancelled'
            elif self.arg3 is None and self.arg2 is not None:
                if self.useFunction(self.arg1, self.arg2) != 'cancelled':
                    inventory.remove(self.owner)
                else:
                    return 'cancelled'
            elif self.arg3 is not None:
                if self.useFunction(self.arg1, self.arg2, self.arg3) != 'cancelled':
                    inventory.remove(self.owner)
                else:
                    return 'cancelled'
                
    def drop(self):
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a ' + self.owner.name + '.', colors.yellow)

def quitGame(message):
    global objects
    global inventory
    saveGame()
    for obj in objects:
        del obj
    inventory = []
    raise SystemExit(str(message))

def getInput():
    global FOV_recompute
    userInput = tdl.event.key_wait()
    if userInput.keychar.upper() ==  'ESCAPE' and gameState != 'looking':
        return 'exit'
    #elif userInput.keychar.upper() == 'ALT' and userInput.alt:
        #isFullscreen = tdl.getFullscreen()
        #print("Fullscreen is borked at the moment")
        #if isFullscreen :
            #set_fullscreen(False)
        #else:
            #set_fullscreen(True)
    elif userInput.keychar.upper() == 'F3':
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
    elif userInput.keychar.upper() == 'F2' and gameState != 'looking':
        player.Fighter.takeDamage(1)
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == 'F1':
        global DEBUG
        if not DEBUG:
            print('Monster turn debug is now on')
            message("This is a very long message just to test Python 3 built-in textwrap function, which allows us to do great things such as splitting very long texts into multiple lines, so as it don't overflow outside of the console. Oh and, debug mode has been activated", colors.purple)
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
        castCreateOrc()
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == 'F5' and DEBUG and not tdl.event.isWindowClosed(): #Don't know if tdl.event.isWindowClosed() is necessary here but added it just to be sure
        player.Fighter.maxHP += 1000
        player.Fighter.hp = player.Fighter.maxHP
        message('Healed player and increased their maximum HP value by 1000', colors.purple)
        FOV_recompute = True
    elif userInput.keychar.upper() == "F6" and DEBUG and not tdl.event.isWindowClosed():
        player.Fighter.frozen = True
        player.Fighter.freezeCooldown = 3
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == 'F7' and DEBUG and not tdl.event.isWindowClosed():
        castCreateHiroshiman()
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == "W" or userInput.keychar.upper() == 'KP5':
        FOV_recompute = True
        return None 
    elif userInput.keychar == 'A' and gameState == 'playing' and DEBUG and not tdl.event.isWindowClosed():
        castArmageddon()         
    elif userInput.keychar == 'l' and gameState == 'playing':
        global gameState
        global lookCursor
        gameState = 'looking'
        if DEBUG == True:
            message('Look mode', colors.purple)
        lookCursor = GameObject(x = player.x, y = player.y, char = 'X', name = 'cursor', color = colors.yellow, Ghost = True)
        objects.append(lookCursor)
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == 'C':
        levelUp_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
        menu('Character Information \n \n Level: ' + str(player.level) + '\n Experience: ' + str(player.Fighter.xp) +
                    '\n Experience to level up: ' + str(levelUp_xp) + '\n \n Maximum HP: ' + str(player.Fighter.maxHP) +
                    '\n Attack: ' + str(player.Fighter.power) + '\n Defense: ' + str(player.Fighter.defense), [], CHARACTER_SCREEN_WIDTH)
        
    elif userInput.keychar == 'd' and gameState == 'playing':
        chosenItem = inventoryMenu('Press the key next to an item to drop it, or press any other key to cancel.')
        if chosenItem is not None:
            chosenItem.drop()
    if gameState ==  'looking':
        global lookCursor
        if userInput.keychar.upper() == 'ESCAPE':
            global gameState
            gameState = 'playing'
            objects.remove(lookCursor)
            del lookCursor
            message('Exited look mode', colors.purple)
            FOV_recompute = True
            return 'didnt-take-turn'
        elif userInput.keychar.upper() in MOVEMENT_KEYS:
            dx, dy = MOVEMENT_KEYS[userInput.keychar.upper()]
            lookCursor.move(dx, dy)
            FOV_recompute = True
            return 'didnt-take-turn'
    if gameState == 'playing':
        if userInput.keychar.upper() in MOVEMENT_KEYS:
            keyX, keyY = MOVEMENT_KEYS[userInput.keychar.upper()]
            moveOrAttack(keyX, keyY)
            FOV_recompute = True #Don't ask why, but it's needed here to recompute FOV, despite not moving, or else Bad Things (trademark) happen.
        elif userInput.keychar.upper()== 'SPACE':
            for object in objects:
                if object.x == player.x and object.y == player.y and object.Item is not None:
                    object.Item.pickUp()
                    break
                elif stairs.x == player.x and stairs.y == player.y:
                    nextLevel()
            FOV_recompute = True
        elif userInput.keychar.upper() == 'I':
            chosenItem = inventoryMenu('Press the key next to an item to use it, or any other to cancel.\n')
            if chosenItem is not None:
                using = chosenItem.use()
                if using == 'cancelled':
                    FOV_recompute = True
                    return 'didnt-take-turn'
            else:
                FOV_recompute = True
                return 'didnt-take-turn'
        else:
            FOV_recompute = True
            return 'didnt-take-turn'
    FOV_recompute = True

def moveOrAttack(dx, dy):
    global FOV_recompute
    x = player.x + dx
    y = player.y + dy
    
    target = None
    for object in objects:
        if object != player:
            if object.Fighter and object.x == x and object.y == y:
                target = object
                break #Since we found the target, there's no point in continuing to search for it
    
    if target is not None:
        player.Fighter.attack(target)
    else:
        player.move(dx, dy)

def checkLevelUp():
    global FOV_recompute
    levelUp_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    if player.Fighter.xp >= levelUp_xp:
        player.level += 1
        player.Fighter.xp -= levelUp_xp
        message('Your battle skills grow stronger! You reached level ' + str(player.level) + '!', colors.yellow)

        choice = None
        while choice == None:
            choice = menu('Level up! Choose a stat to raise: \n',
                ['Constitution (+20 HP, from ' + str(player.Fighter.maxHP) + ')',
                'Strength (+1 attack, from ' + str(player.Fighter.power) + ')',
                'Agility (+1 defense, from ' + str(player.Fighter.defense) + ')'], LEVEL_SCREEN_WIDTH)
            if choice != None:
                if choice == 0:
                    player.Fighter.maxHP += 20
                    player.Fighter.hp += 20
                elif choice == 1:
                    player.Fighter.power += 1
                elif choice == 2:
                    player.Fighter.defense += 1
                    
                FOV_recompute = True
                Update()
                break
            
 
        

def isVisibleTile(x, y):
    global myMap
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

def isBlocked(x, y): #With this function, making a check such as myMap[x][y].blocked is deprecated and should not be used anymore outside of this function (or FOV related stuff), since the latter does exactly the same job in addition to checking for blocking objects.
    if myMap[x][y].blocked:
        return True #If the Tile is already set as blocking, there's no point in making further checks
    
    for object in objects: #As all statements starting with this, ignore PyDev warning. However, please note that objects refers to the list of objects that we created and IS NOT defined by default in any library used (so don't call it out of the blue), contrary to object.
        if object.blocks and object.x == x and object.y == y: #With this, we're checking every single object created, which might lead to performance issue. Fixing this could be one of many possible improvements, but this isn't a priority at the moment. 
            return True
    
    return False

def tileDistance(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        return math.sqrt(dx ** 2 + dy ** 2)

def castHeal(healAmount = 5):
    if player.Fighter.hp == player.Fighter.maxHP:
        message('You are already at full health')
        return 'cancelled'
    else:
        message('You are healed for {} HP !'.format(healAmount), colors.light_green)
        player.Fighter.heal(healAmount)

def castLightning():
    target = closestMonster(LIGHTNING_RANGE)
    if target is None:
        message('Your magic fizzles: there is no enemy near enough to strike', colors.red)
        return 'cancelled'
    message('A lightning bolt strikes the ' + target.name + ' with a heavy thunder ! It is shocked and suffers ' + str(LIGHTNING_DAMAGE) + ' shock damage.', colors.light_blue)
    target.Fighter.takeDamage(LIGHTNING_DAMAGE)

def castConfuse():
    message('Choose a target for your spell, press Escape to cancel.', colors.light_cyan)
    target = targetMonster(maxRange = CONFUSE_RANGE)
    if target is None:
        message('Invalid target.', colors.red)
        return 'cancelled'
    old_AI = target.AI
    target.AI = ConfusedMonster(old_AI)
    target.AI.owner = target
    message('The ' + target.name + ' starts wandering around as he seems to lose all bound with reality.', colors.light_violet)

def castFreeze():
    message('Choose a target for your spell, press Escape to cancel.', colors.light_cyan)
    target = targetMonster(maxRange = None)
    if target is None:
        message('Invalid target.', colors.red)
        return 'cancelled'
    if not target.Fighter.frozen:
        target.Fighter.frozen = True
        target.Fighter.freezeCooldown = 4 #Actually 3 turns since this begins ticking down the turn the spell is casted
        message("The " + target.name + " is frozen !", colors.light_violet)
    else:
        message("The " + target.name + " is already frozen.")
        return 'cancelled'
    
def castFireball(radius = 3, damage = 12):
    message('Choose a target for your spell, press Escape to cancel.', colors.light_cyan)
    target = targetTile(maxRange = 4)
    if target == 'cancelled':
        message('Spell casting cancelled')
        return target
    else:
        (x,y) = target
        for obj in objects:
            if obj.distanceToCoords(x, y) <= radius and obj.Fighter:
                if obj != player:
                    message('The {} gets burned for {} damage !'.format(obj.name, damage), colors.light_blue)
                else:
                    message('You get burned for {} damage !'.format(damage), colors.orange)
                obj.Fighter.takeDamage(damage)
                if obj.Fighter and randint(0, 100) > 50 and not obj.Fighter.burning:
                    obj.Fighter.burning = True
                    obj.Fighter.burnCooldown = 4
                    message('The ' + obj.name + ' is set afire')
                
def castArmageddon(radius = 4, damage = 40):
    global FOV_recompute
    message('As you begin to read the scroll, the runes inscribed on it start emitting a very bright crimson light. Continue (Y/N)', colors.dark_red)
    FOV_recompute = True
    Update()
    tdl.flush()
    invalid = True
    while invalid:
        key = tdl.event.key_wait()
        if key.keychar.upper() == 'N':
            message('Good idea.', colors.dark_red)
            FOV_recompute = True
            Update()
            return 'cancelled'
        elif key.keychar.upper() == 'Y':
            invalid = False
        elif key.keychar.upper() not in ('Y', 'N'):
            message('Please press a valid key (Y or N)')#Displays regardless of if a valid hcoice has been made, to be fixed
            FOV_recompute = True
            Update()
            
    radmax = radius + 2
    global explodingTiles
    global gameState
    for x in range (player.x - radmax, player.x + radmax):
        for y in range (player.y - radmax, player.y + radmax):
            try: #Execute code below try if no error is encountered
                if tileDistance(player.x, player.y, x, y) <= radius and not myMap[x][y].unbreakable:
                    myMap[x][y].blocked = False
                    myMap[x][y].block_sight = False
                    if x in range (1, MAP_WIDTH-1) and y in range (1,MAP_HEIGHT - 1):
                        explodingTiles.append((x,y))
                    for obj in objects:
                        if obj.Fighter and obj.x == x and obj.y == y: 
                            try:
                                if obj != player:
                                    message('The {} gets smited for {} damage !'.format(obj.name, damage), colors.light_blue)
                                else:
                                    message('You get smited for {} damage !'.format(damage), colors.orange)        
                                obj.Fighter.takeDamage(damage)
                            except AttributeError: #If it tries to access a non-existing object (aka outside of the map)
                                continue
            except IndexError: #If an IndexError is encountered (aka if the function tries to access a tile outside of the map), execute code below except
                continue   #Go to next loop iteration and ignore the problematic value     
    #Display explosion eye-candy, this could get it's own function
    explode()
    
def monsterArmageddon(monsterName ,monsterX, monsterY, radius = 4, damage = 40):
    radmax = radius + 2
    message(monsterName.capitalize() + ' recites an arcane formula and explodes !', colors.red)
    global explodingTile
    global gameState
    global FOV_recompute
    FOV_recompute = True
    for x in range (monsterX - radmax, monsterX + radmax):
        for y in range (monsterY - radmax, monsterY + radmax):
            try: #Execute code below try if no error is encountered
                if tileDistance(monsterX, monsterY, x, y) <= radius and not myMap[x][y].unbreakable:
                    myMap[x][y].blocked = False
                    myMap[x][y].block_sight = False
                    if x in range (1, MAP_WIDTH-1) and y in range (1,MAP_HEIGHT - 1):
                        explodingTiles.append((x,y))
                    for obj in objects:
                        if obj.Fighter and obj.x == x and obj.y == y: 
                            try:
                                if obj != player:
                                    message('The explosion deals {} damage to {} !'.format(damage, obj.name))
                                else:
                                    message('The explosion deals {} damage to you !'.format(damage), colors.orange)        
                                obj.Fighter.takeDamage(damage)
                            except AttributeError: #If it tries to access a non-existing object (aka outside of the map)
                                continue
            except IndexError: #If an IndexError is encountered (aka if the function tries to access a tile outside of the map), execute code below except
                continue   #Go to next loop iteration and ignore the problematic value     
    #Display explosion eye-candy, this could get it's own function
    explode()
    
    
# Add push monster spell (create an invisble projectile that pass through a monster, when the said projectile hits a wall, teleport monster to the projectile position and deal X damage to the said monster.)
    
def createOrc(x, y):
    if x != player.x or y != player.y:
        fighterComponent = Fighter(hp=10, defense=0, power=3, xp = 35, deathFunction = monsterDeath)
        AI_component = BasicMonster()
        monster = GameObject(x, y, char = 'o', color = colors.desaturated_green, name = 'orc', blocks = True, Fighter=fighterComponent, AI = AI_component)
        return monster
    else:
        return 'cancelled'
    
def createHiroshiman(x, y):
    if x != player.x or y != player.y:
        fighterComponent = Fighter(hp=150, defense=0, power=3, xp = 500, deathFunction = monsterDeath)
        AI_component = SplosionAI()
        monster = GameObject(x, y, char = 'H', color = colors.red, name = 'Hiroshiman', blocks = True, Fighter=fighterComponent, AI = AI_component)
        return monster
    else:
        return 'cancelled'

def castCreateOrc():
    target = targetTile()
    if target == 'cancelled':
        return 'cancelled'
    else:
        (x,y) = target
        monster = createOrc(x, y)
        objects.append(monster)

def castCreateHiroshiman():
    target = targetTile()
    if target == 'cancelled':
        return 'cancelled'
    else:
        (x,y) = target
        monster = createHiroshiman(x, y)
        objects.append(monster)        
        

def explode():
    global gameState
    global explodingTiles
    global FOV_recompute
    gameState = 'exploding'
    for obj in objects :
        obj.clear()
    con.clear()
    FOV_recompute = True
    Update()
    tdl.flush()
    time.sleep(.125) #Wait for 0.125 seconds
    explodingTiles = []
    FOV_recompute = True
    if player.Fighter.hp > 0:
        gameState = 'playing'
    else:
        gameState = 'dead'
#_____________ MAP CREATION __________________
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

class Tile:
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
        self.explored = False
        self.unbreakable = False
        if block_sight is None:
            block_sight = blocked
            self.block_sight = block_sight
        else:
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
    global myMap, stairs, objects
    myMap = [[Tile(True) for y in range(MAP_HEIGHT)]for x in range(MAP_WIDTH)] #Creates a rectangle of blocking tiles from the Tile class, aka walls. Each tile is accessed by myMap[x][y], where x and y are the coordinates of the tile.
    rooms = []
    numberRooms = 0
    objects = [player]
    
    for y in range (MAP_HEIGHT):
        myMap[0][y].unbreakable = True
        myMap[MAP_WIDTH-1][y].unbreakable = True
    for x in range(MAP_WIDTH):
        myMap[x][0].unbreakable = True
        myMap[x][MAP_HEIGHT-1].unbreakable = True #Borders of the map cannot be broken
 
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
            placeObjects(newRoom)
            rooms.append(newRoom)
            numberRooms += 1
    stairs = GameObject(new_x, new_y, '<', 'stairs', colors.white, alwaysVisible = True, darkColor = colors.dark_grey)
    objects.append(stairs)
    stairs.sendToBack() 

#_____________ MAP CREATION __________________

#_____________ ROOM POPULATION + ITEMS GENERATION_______________
monsterChances = {'orc': 80, 'troll': 20}
itemChances = {'potion': 30, 'scroll': 65, 'none': 5}
scrollChances = {'lightning': 12, 'confuse': 12, 'fireball': 25, 'armageddon': 10, 'ice': 25, 'none': 1}
fireballChances = {'lesser': 20, 'normal': 50, 'greater': 20}
potionChances = {'heal': 100}

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
    chances = chancesDictionnary.values()
    strings = list(chancesDictionnary.keys())
    return strings[randomChoiceIndex(chances)]

def placeObjects(room):
    numMonsters = randint(0, MAX_ROOM_MONSTERS)
    if dungeonLevel > 2 and hiroshimanNumber == 0:
        global monsterChances
        monsterChances['troll'] = 15
        monsterChances['hiroshiman'] = 5
    for i in range(numMonsters):
        x = randint(room.x1+1, room.x2-1)
        y = randint(room.y1+1, room.y2-1)
        
        if not isBlocked(x, y) and (x, y) != (player.x, player.y):
            monsterChoice = randomChoice(monsterChances)
            if monsterChoice == 'orc':
                monster = createOrc(x, y)
            elif monsterChoice == 'hiroshiman' and hiroshimanNumber == 0 and dungeonLevel > 2:
                global hiroshimanNumber
                global monsterChances
                monster = createHiroshiman(x, y)
                hiroshimanNumber = 1
                del monsterChances['hiroshiman']
                monsterChances['troll'] = 20
                
            elif monsterChoice == 'troll':
                fighterComponent = Fighter(hp=16, defense=1, power=4, xp = 100, deathFunction = monsterDeath)
                AI_component = BasicMonster()
                monster = GameObject(x, y, char = 'T', color = colors.darker_green,name = 'troll', blocks = True, Fighter = fighterComponent, AI = AI_component)
        
        if monster != 'cancelled':
            objects.append(monster)
    
    num_items = randint(0, MAX_ROOM_ITEMS)
    for i in range(num_items):
        x = randint(room.x1+1, room.x2-1)
        y = randint(room.y1+1, room.y2-1)
        if not isBlocked(x, y):
            itemChoice = randomChoice(itemChances)
            if itemChoice == 'potion':
                #Spawn a potion
                potionChoice = randomChoice(potionChances)
                if potionChoice == 'heal':
                    item = GameObject(x, y, '!', 'healing potion', colors.violet, Item = Item(useFunction = castHeal), blocks = False)
            elif itemChoice == 'scroll':
                #Spawn a scroll
                scrollChoice = randomChoice(scrollChances)
                if scrollChoice == 'lightning':
                    item = GameObject(x, y, '~', 'scroll of lightning bolt', colors.light_yellow, Item = Item(useFunction = castLightning), blocks = False)
                elif scrollChoice == 'confuse':
                    item = GameObject(x, y, '~', 'scroll of confusion', colors.light_yellow, Item = Item(useFunction = castConfuse), blocks = False)
                elif scrollChoice == 'fireball':
                    fireballChoice = randomChoice(fireballChances)
                    if fireballChoice == 'lesser':
                        item = GameObject(x, y, '~', 'scroll of lesser fireball', colors.light_yellow, Item = Item(castFireball, 2, 6), blocks = False)
                    elif fireballChoice == 'normal':
                        item = GameObject(x, y, '~', 'scroll of fireball', colors.light_yellow, Item = Item(castFireball), blocks = False)
                    elif fireballChoice == 'greater':
                        item = GameObject(x, y, '~', 'scroll of greater fireball', colors.light_yellow, Item = Item(castFireball, 4, 24), blocks = False)
                elif scrollChoice == 'armageddon':
                    item = GameObject(x, y, '~', 'scroll of armageddon', colors.red, Item = Item(castArmageddon), blocks = False)
                elif scrollChoice == 'ice':
                    item = GameObject(x, y, '~', 'scroll of ice bolt', colors.light_cyan, Item = Item(castFreeze), blocks = False)
                elif scrollChoice == 'none':
                    item = None
            elif itemChoice == 'none':
                item = None
            if item is not None:            
                objects.append(item)
                item.sendToBack()
#_____________ ROOM POPULATION + ITEMS GENERATION_______________
def playerDeath(player):
    global gameState
    message('You died!', colors.red)
    gameState = 'dead'
    player.char = '%'
    player.color = colors.dark_red
 
def monsterDeath(monster):
    message(monster.name.capitalize() + ' is dead! You gain ' + str(monster.Fighter.xp) + ' XP.', colors.dark_sky)
    monster.char = '%'
    monster.color = colors.dark_red
    monster.blocks = False
    monster.AI = None
    monster.name = 'remains of ' + monster.name
    monster.Fighter = None
    monster.sendToBack()

#_____________ GUI _______________
def renderBar(x, y, totalWidth, name, value, maximum, barColor, backColor):
    barWidth = int(float(value) / maximum * totalWidth) #Width of the bar is proportional to the ratio of the current value over the maximum value
    panel.draw_rect(x, y, totalWidth, 1, None, bg = backColor)#Background of the bar
    
    if barWidth > 0:
        panel.draw_rect(x, y, barWidth, 1, None, bg = barColor)#The actual bar
        
    text = name + ': ' + str(value) + '/' + str(maximum)
    xCentered = x + (totalWidth - len(text))//2
    panel.draw_str(xCentered, y, text, fg = colors.white, bg=None)
    
def message(newMsg, color = colors.white):
    newMsgLines = textwrap.wrap(newMsg, MSG_WIDTH) #If message exceeds log width, split it into two or more lines
    for line in newMsgLines:
        if len(gameMsgs) == MSG_HEIGHT:
            del gameMsgs[0] #Deletes the oldest message if the log is full
    
        gameMsgs.append((line, color))

def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options')
    headerWrapped = textwrap.wrap(header, width)
    headerHeight = len(headerWrapped)
    if header == "":
        headerHeight = 0
    height = len(options) + headerHeight + 1
    window = tdl.Console(width, height)
    window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)
    for i, line in enumerate(headerWrapped):
        window.draw_str(0, 0+i, headerWrapped[i])

    y = headerHeight + 1
    letterIndex = ord('a')
    for optionText in options:
        text = '(' + chr(letterIndex) + ') ' + optionText
        window.draw_str(0, y, text, bg=None)
        y += 1
        letterIndex += 1
    

    x = MID_WIDTH - int(width/2)
    y = MID_HEIGHT - int(height/2)
    root.blit(window, x, y, width, height, 0, 0)

    tdl.flush()
    key = tdl.event.key_wait()
    keyChar = key.char
    if keyChar == '':
        keyChar = ' '    
    index = ord(keyChar) - ord('a')
    if index >= 0 and index < len(options):
        return index
    return None

def inventoryMenu(header):
    #show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = [item.name for item in inventory]
    index = menu(header, options, INVENTORY_WIDTH)
    if index is None or len(inventory) == 0:
        return None
    else:
        return inventory[index].Item

def msgBox(text, width = 50):
    menu(text, [], width)
    
def drawCentered (cons = con , y = 1, text = "Lorem Ipsum", fg = None, bg = None):
    xCentered = (WIDTH - len(text))//2
    cons.draw_str(xCentered, y, text, fg, bg)

def mainMenu():
    choices = ['New Game', 'Continue', 'Quit']
    index = 0
    while not tdl.event.isWindowClosed():
        root.clear()
        drawCentered(cons =  root, y = 15, text = 'Dementia', fg = colors.white, bg = None)
        drawCentered(cons = root, y = 44, text = choices[0], fg = colors.white, bg = None)
        drawCentered(cons = root, y = 45, text = choices[1], fg  = colors.white, bg = None)
        drawCentered(cons = root, y = 46, text = choices[2], fg = colors.white, bg = None)
        drawCentered(cons = root, y = 44 + index, text=choices[index], fg = colors.black, bg = colors.white)
        tdl.flush()
        key = tdl.event.key_wait()
        if key.keychar.upper() == "DOWN":
            index += 1
        elif key.keychar.upper() == "UP":
            index -= 1
        if index < 0:
            index = 2
        if index > 2:
            index = 0
        if key.keychar.upper() == "ENTER":
            if index == 0:
                newGame()
                playGame()
            elif index == 1:
                try:
                    loadGame()
                except:
                    msgBox("\n No saved game to load.\n", 24)
                    continue
                playGame()
            elif index == 2:
                raise SystemExit("Chose Quit on the main menu")
        tdl.flush()
        
#_____________ GUI _______________
def initializeFOV():
    global FOV_recompute, visibleTiles
    FOV_recompute = True
    visibleTiles = tdl.map.quickFOV(player.x, player.y, isVisibleTile, fov = FOV_ALGO, radius = SIGHT_RADIUS, lightWalls = FOV_LIGHT_WALLS)
    con.clear()

def Update():
    global FOV_recompute
    global visibleTiles
    con.clear()
    tdl.flush()
    player.Player.changeColor()
    if FOV_recompute:
        FOV_recompute = False
        visibleTiles = tdl.map.quickFOV(player.x, player.y, isVisibleTile, fov = FOV_ALGO, radius = SIGHT_RADIUS, lightWalls = FOV_LIGHT_WALLS)
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = (x, y) in visibleTiles
                wall = myMap[x][y].block_sight
                if not visible:
                    if myMap[x][y].explored:
                        if wall:
                            if GRAPHICS == 'modern':
                                con.draw_char(x, y, '#', fg=color_dark_wall, bg=color_dark_ground)
                            elif GRAPHICS == 'classic':
                                con.draw_char(x, y, '#', fg=colors.dark_gray, bg=None)
                        else:
                            if GRAPHICS == 'modern':
                                con.draw_char(x, y, None, fg=None, bg=color_dark_ground)
                            elif GRAPHICS == 'classic':
                                con.draw_char(x, y, '.', fg=colors.dark_gray, bg=None)    
                else:
                    if wall:
                        if GRAPHICS == 'modern':
                            con.draw_char(x, y, '#', fg=color_light_wall, bg=color_light_ground)
                        elif GRAPHICS == 'classic':
                            con.draw_char(x, y, '#', fg=colors.white, bg=None)
                    else:
                        if GRAPHICS == 'modern':
                            con.draw_char(x, y, None, fg=None, bg=color_light_ground)
                        elif GRAPHICS == 'classic':
                            con.draw_char(x, y, '.', fg=colors.white, bg=None)    
                    myMap[x][y].explored = True
                if gameState == 'targeting':
                    inRange = (x, y) in tilesInRange
                    if inRange and not wall:
                        con.draw_char(x, y, None, fg=None, bg=colors.darker_yellow)
                elif gameState == 'exploding':
                    exploded = (x,y) in explodingTiles
                    if exploded:
                        con.draw_char(x, y, '*', fg=colors.red, bg = None)
                        
    for object in objects:
        if object != player:
            if (object.x, object.y) in visibleTiles or (object.alwaysVisible and myMap[object.x][object.y].explored):
                object.draw()
    player.draw()
    root.blit(con, 0, 0, WIDTH, HEIGHT, 0, 0)
    panel.clear(fg=colors.white, bg=colors.black)
    # Draw log
    msgY = 1
    for (line, color) in gameMsgs:
        panel.draw_str(MSG_X, msgY, line, bg=None, fg = color)
        msgY += 1
    # Draw GUI
    panel.draw_str(1, 3, 'Dungeon level: ' + str(dungeonLevel), colors.white)
    panel.draw_str(1, 5, 'Player level: ' + str(player.level), colors.white)
    renderBar(1, 1, BAR_WIDTH, 'HP', player.Fighter.hp, player.Fighter.maxHP, player.color, colors.dark_gray)
    # Look code
    if gameState == 'looking' and lookCursor != None:
        global lookCursor
        lookCursor.draw()
        panel.draw_str(1, 0, GetNamesUnderLookCursor(), bg=None, fg = colors.yellow)
        
    root.blit(panel, 0, PANEL_Y, WIDTH, PANEL_HEIGHT, 0, 0)
    
def GetNamesUnderLookCursor():
    names = [obj.name for obj in objects
                if obj.x == lookCursor.x and obj.y == lookCursor.y and (obj.x, obj.y in visibleTiles) and obj != lookCursor]
    names = ', '.join(names)
    return names.capitalize()

def targetTile(maxRange = None):
    global gameState
    global cursor
    global tilesInRange
    global FOV_recompute
    
    if maxRange == 0:
        return (player.x, player.y)
    
    gameState = 'targeting'
    cursor = GameObject(x = player.x, y = player.y, char = 'X', name = 'cursor', color = colors.yellow, Ghost = True)
    objects.append(cursor)
    for (rx, ry) in visibleTiles:
            if maxRange is None or player.distanceToCoords(rx,ry) <= maxRange:
                tilesInRange.append((rx, ry))
    FOV_recompute= True
    Update()
    tdl.flush()
    
    
    
    while gameState == 'targeting':
        FOV_recompute = True
        key = tdl.event.key_wait()
        if key.keychar.upper() == 'ESCAPE':
            gameState = 'playing'
            objects.remove(cursor)
            del cursor
            tilesInRange = []
            con.clear()
            Update()
            return 'cancelled'
        elif key.keychar.upper() in MOVEMENT_KEYS:
            dx, dy = MOVEMENT_KEYS[key.keychar.upper()]
            if (cursor.x + dx, cursor.y + dy) in tilesInRange and (maxRange is None or player.distanceTo(cursor) <= maxRange):
                cursor.move(dx, dy)
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
            con.clear()
            Update()
            return (x, y)
        
def targetMonster(maxRange = None):
    target = targetTile(maxRange)
    if target == 'cancelled':
        return None
    else:
        (x,y) = target
        for obj in objects:
            if obj.x == x and obj.y == y and obj.Fighter and obj != player:
                return obj
               

#______ INITIALIZATION AND MAIN LOOP________
def saveGame():
    
    if not os.path.exists(absDirPath):
        os.makedirs(absDirPath)
    
    file = shelve.open(absFilePath, "n")
    file["dungeonLevel"] = dungeonLevel
    file["myMap"] = deepcopy(myMap)
    file["objects"] = objects
    file["playerIndex"] = objects.index(player)
    file["inventory"] = inventory
    file["gameMsgs"] = gameMsgs
    file["gameState"] = gameState
    file.close()
    
    #mapFile = open(absPicklePath, 'wb')
    #pickle.dump(myMap, mapFile)
    #mapFile.close()

def newGame():
    global objects, inventory, gameMsgs, gameState, player, dungeonLevel
    playFight = Fighter( hp = 100, power=5, defense=3, deathFunction=playerDeath, xp=0)
    playComp = Player()
    player = GameObject(25, 23, '@', Fighter = playFight, Player = playComp, name = 'Hero', color = (0, 210, 0))
    player.level = 1

    objects = [player]
    dungeonLevel = 1 
    makeMap()
    Update()

    inventory = []

    FOV_recompute = True
    initializeFOV()
    message('Zargothrox says : Prepare to get lost in the Realm of Madness !', colors.dark_red)

def loadGame():
    global objects, inventory, gameMsgs, gameState, player, dungeonLevel
    
    
    #myMap = [[Tile(True) for y in range(MAP_HEIGHT)]for x in range(MAP_WIDTH)]
    file = shelve.open(absFilePath, "r")
    dungeonLevel = file["dungeonLevel"]
    myMap = deepcopy(file["myMap"])
    objects = file["objects"]
    player = objects[file["playerIndex"]]
    inventory = file["inventory"]
    gameMsgs = file["gameMsgs"]
    gameState = file["gameState"]
    
    #mapFile = open(absPicklePath, "rb")
    #myMap = pickle.load(mapFile)
    #mapFile.close()
    

def nextLevel():
    global dungeonLevel
    message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', colors.red)
    dungeonLevel += 1
    makeMap()  #create a fresh new level!
    if hiroshimanNumber == 1 and not hiroshimanHasAppeared:
        global hiroshimanHasAppeared
        message('You suddenly feel uneasy.', colors.dark_red)
        hiroshimanHasAppeared = True
    initializeFOV()

def playGame():
    while not tdl.event.isWindowClosed():
        Update()
        checkLevelUp()
        tdl.flush()
        for object in objects:
            object.clear()
        playerAction = getInput()
        FOV_recompute = True #So as to avoid the blackscreen bug no matter which key we press
        if playerAction == 'exit':
            quitGame('Player pressed escape')
        if gameState == 'playing' and playerAction != 'didnt-take-turn':
            for object in objects:
                if object.AI:
                    object.AI.takeTurn()
                if object.Fighter and object.Fighter.frozen:
                    object.Fighter.freezeCooldown -= 1
                    if object.Fighter.freezeCooldown < 0:
                        object.Fighter.freezeCooldown = 0
                    if object.Fighter.freezeCooldown == 0:
                        object.Fighter.frozen = False
                        message(object.name.capitalize() + "'s ice shatters !", colors.light_violet)
                        
                if object.Fighter and object.Fighter.burning:
                    object.Fighter.burnCooldown -= 1
                    object.Fighter.takeDamage(3)
                    message('The ' + object.name + ' keeps burning !')
                    if object.Fighter.burnCooldown < 0:
                        object.Fighter.burnCooldown = 0
                    if object.Fighter.burnCooldown == 0:
                        object.Fighter.burning = False
                        message(object.name.capitalize() + "'s flames die down", colors.darker_orange)
    DEBUG = False
    quitGame('Window has been closed')
    
mainMenu()