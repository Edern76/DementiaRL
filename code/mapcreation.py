from code.constants import *
from code.sharedvariables import *
from code.gameobject import *
from random import randint
from math import *
from code import sharedvariables

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

def secretRoomTest(startingX, endX, startingY, endY):
    for x in range(startingX, endX):
        for y in range(startingY, endY):
            if not myMap[x][y].block_sight:
                if myMap[x + 1][y].block_sight: #right of the current tile
                    intersect = False
                    for indexX in range(5):
                        for indexY in range(5):
                            if not myMap[x + 1 + indexX][y - 2 + indexY].block_sight or myMap[x + 1 + indexX][y - 2 + indexY].unbreakable:
                                intersect = True
                                break
                        break
                    if not intersect:
                        print("right")
                        return x + 1, y - 2, x + 1, y
                if myMap[x - 1][y].block_sight: #left
                    intersect = False
                    for indexX in range(5):
                        for indexY in range(5):
                            if not myMap[x - 1 - indexX][y - 2 + indexY].block_sight or myMap[x - 1 - indexX][y - 2 + indexY].unbreakable:
                                intersect = True
                                break
                        break
                    if not intersect:
                        print("left")
                        return x - 5, y - 2, x - 1, y
                if myMap[x][y + 1].block_sight: #under
                    intersect = False
                    for indexX in range(5):
                        for indexY in range(5):
                            if not myMap[x - 2 + indexX][y + 1 + indexY].block_sight or myMap[x - 2 + indexX][y + 1 + indexY].unbreakable:
                                intersect = True
                                break
                        break
                    if not intersect:
                        print("under")
                        return x - 2, y + 1, x, y + 1
                if myMap[x][y - 1].block_sight: #above
                    intersect = False
                    for indexX in range(5):
                        for indexY in range(5):
                            if not myMap[x - 2 + indexX][y - 1 - indexY].block_sight or myMap[x - 2 + indexX][y - 1 - indexY].unbreakable:
                                intersect = True
                                break
                        break
                    if not intersect:
                        print("above")
                        return x - 2, y - 5, x, y - 1

def secretRoom():
    global myMap
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
    [x, y, entryX, entryY] = secretRoomTest(minX, maxX, minY, maxY)
    if not (x == 'cancelled' or y == 'cancelled' or entryX == 'cancelled' or entryY == 'cancelled'):
        secretRoom = Rectangle(x, y, 4, 4)
        createRoom(secretRoom)
        myMap[entryX][entryY].blocked = False
        myMap[entryX][entryY].block_sight = True
        print("created secret room at x ", entryX, " y ", entryY, " in quarter ", quarter)


def makeMap():
    global myMap, stairs, objects, upStairs
    myMap = [[Tile(True) for y in range(MAP_HEIGHT)]for x in range(MAP_WIDTH)] #Creates a rectangle of blocking tiles from the Tile class, aka walls. Each tile is accessed by myMap[x][y], where x and y are the coordinates of the tile.
    rooms = []
    numberRooms = 0
    objects = [sharedvariables.player]
    
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
                sharedvariables.player.x = new_x
                sharedvariables.player.y = new_y
                if dungeonLevel > 1:
                    upStairs = GameObject(new_x, new_y, '<', 'stairs', colors.white, alwaysVisible = True, darkColor = colors.dark_grey)
                    objects.append(upStairs)
                    upStairs.sendToBack()
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
    secretRoom()
    stairs = GameObject(new_x, new_y, '>', 'stairs', colors.white, alwaysVisible = True, darkColor = colors.dark_grey)
    objects.append(stairs)
    stairs.sendToBack()

#_____________ MAP CREATION __________________

#_____________ ROOM POPULATION + ITEMS GENERATION_______________
monsterChances = {'orc': 80, 'troll': 20}
itemChances = {'potion': 35, 'scroll': 45, 'sword': 7, 'shield': 7, 'spellbook': 6}
potionChances = {'heal': 100}
spellbookChances = {'darkPact' : 100}

def createSword(x, y):
    global sword
    name = 'sword'
    sizeChance = {'short' : 40, 'long' : 60}
    sizeChoice = randomChoice(sizeChance)
    name = sizeChoice + name
    if sizeChoice == 'short':
        swordPow = 3
    else:
        swordPow = 5
    qualityChances = {'normal' : 70, 'rusty' : 20, 'sharp' : 10}
    qualityChoice = randomChoice(qualityChances)
    if qualityChoice == 'rusty':
        name = qualityChoice + ' ' + name
        swordPow -= 1
    elif qualityChoice == 'sharp':
        name = qualityChoice + ' ' + name
        swordPow += 1
    burningChances = {'yes' : 20, 'no': 80}
    burningChoice = randomChoice(burningChances)
    if burningChoice == 'yes':
        name = 'burning ' + name
        burningSword = True
    else:
        burningSword = False
    equipmentComponent = Equipment(slot='right hand', type = 'light weapon', powerBonus = swordPow, burning = burningSword)
    sword = GameObject(x, y, '/', name, colors.sky, Equipment = equipmentComponent, Item = Item())
    return sword 

def createScroll(x, y):
    global scroll
    scrollChances = {'lightning': 12, 'confuse': 12, 'fireball': 25, 'armageddon': 10, 'ice': 25, 'none': 1}
    scrollChoice = randomChoice(scrollChances)
    if scrollChoice == 'lightning':
        scroll = GameObject(x, y, '~', 'scroll of lightning bolt', colors.light_yellow, Item = Item(useFunction = castLightning), blocks = False)
    elif scrollChoice == 'confuse':
        scroll = GameObject(x, y, '~', 'scroll of confusion', colors.light_yellow, Item = Item(useFunction = castConfuse), blocks = False)
    elif scrollChoice == 'fireball':
        fireballChances = {'lesser': 20, 'normal': 50, 'greater': 20}
        fireballChoice = randomChoice(fireballChances)
        if fireballChoice == 'lesser':
            scroll = GameObject(x, y, '~', 'scroll of lesser fireball', colors.light_yellow, Item = Item(castFireball, 2, 6), blocks = False)
        elif fireballChoice == 'normal':
            scroll = GameObject(x, y, '~', 'scroll of fireball', colors.light_yellow, Item = Item(castFireball), blocks = False)
        elif fireballChoice == 'greater':
            scroll = GameObject(x, y, '~', 'scroll of greater fireball', colors.light_yellow, Item = Item(castFireball, 4, 24), blocks = False)
    elif scrollChoice == 'armageddon':
        scroll = GameObject(x, y, '~', 'scroll of armageddon', colors.red, Item = Item(castArmageddon), blocks = False)
    elif scrollChoice == 'ice':
        scroll = GameObject(x, y, '~', 'scroll of ice bolt', colors.light_cyan, Item = Item(castFreeze), blocks = False)
    elif scrollChoice == 'none':
        scroll = None
    return scroll

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
        
        if not isBlocked(x, y) and (x, y) != (sharedvariables.player.x, sharedvariables.player.y):
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
                equipmentComponent = Equipment(slot = 'right hand', type = 'heavy weapon', powerBonus = 5, accuracyBonus = -20)
                trollMace = GameObject(x, y, '/', 'troll mace', colors.darker_orange, Equipment=equipmentComponent, Item=Item())
                fighterComponent = Fighter(hp=20, armor=2, power=4, xp = 100, deathFunction = monsterDeath, accuracy = 7, evasion = 1, lootFunction=trollMace, lootRate=15)
                AI_component = BasicMonster()
                monster = GameObject(x, y, char = 'T', color = colors.darker_green,name = 'troll', blocks = True, Fighter = fighterComponent, AI = AI_component)
        
        if monster != 'cancelled' and monster != None:
            objects.append(monster)
    
    num_items = randint(0, MAX_ROOM_ITEMS)
    for i in range(num_items):
        x = randint(room.x1+1, room.x2-1)
        y = randint(room.y1+1, room.y2-1)
        item = None
        if not isBlocked(x, y):
            itemChoice = randomChoice(itemChances)
            if itemChoice == 'potion':
                potionChoice = randomChoice(potionChances)
                if potionChoice == 'heal':
                    item = GameObject(x, y, '!', 'healing potion', colors.violet, Item = Item(useFunction = castHeal), blocks = False)
            elif itemChoice == 'scroll':
                createScroll(x, y)
                item = scroll
            elif itemChoice == 'none':
                item = None
            elif itemChoice == 'sword':
                createSword(x, y)
                item = sword
            elif itemChoice == 'shield':
                equipmentComponent = Equipment(slot = 'left hand', type = 'shield', armorBonus=1)
                item = GameObject(x, y, '[', 'shield', colors.darker_orange, Equipment=equipmentComponent, Item=Item())
            elif itemChoice == 'spellbook':
                spellbookChoice = randomChoice(spellbookChances)
                if spellbookChoice == "darkPact":
                    item = GameObject(x, y, '=', 'spellbook of arcane rituals', colors.violet, Item = Item(useFunction = learnSpell, arg1 = darkPact), blocks = False)
            else:
                item = None
            if item is not None:            
                objects.append(item)
                item.sendToBack()
#_____________ ROOM POPULATION + ITEMS GENERATION_______________
