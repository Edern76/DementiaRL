import tdl, colors, math, textwrap, time, os, shelve, sys, code
from tdl import *
from random import randint
from math import *
from os import makedirs
from code.constants import *
# These lines are just in case PyDev goes bananas, otherwise these are useless
from code.menu import menu
from code.menu import drawCentered
from code.menu import msgBox
# End of anti-bananas-going lines, everything below this line is essential
from code.menu import *
from code.charGen import *
from dill import objects

# Naming conventions :
# MY_CONSTANT
# myVariable
# myFunction()
# MyClass
# Not dramatic if you forget about this (it happens to me too), but it makes reading code easier

#NEVER SET AN EVASION VALUE AT ZERO, SET IT AT ONE INSTEAD#

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


pathfinder = None


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
    def __init__(self, x, y, char, name, color = colors.white, blocks = False, Fighter = None, AI = None, Player = None, Ghost = False, Item = None, alwaysVisible = False, darkColor = None, Equipment = None):
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
        self.Equipment = Equipment
        if self.Equipment:
            self.Equipment.owner = self

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
    
    def moveAstar(self, destX, destY):
        global tilesinPath, pathfinder
        self.astarPath = pathfinder.get_path(self.x, self.y, destX, destY)
        tilesinPath.extend(self.astarPath)
        if len(self.astarPath) != 0:
            if DEBUG:
                print(self.name + "'s path :", end = " ")
                for (x,y) in self.astarPath:
                    print (str(x) + "/" + str(y) + ";", end = " ", sep = " ")
                    print()
            (x, y) = self.astarPath[0]
            self.x = x
            self.y = y
            if DEBUG:
                print(self.name + " moved to " + str(self.x) + ', ' + str(self.y))
            
        else:
            self.moveTowards(destX, destY)
            if DEBUG:
                print(self.name + " found no Astar path")

class Fighter: #All NPCs, enemies and the player
    def __init__(self, hp, armor, power, accuracy, evasion, xp, deathFunction=None, maxMP = 0, knownSpells = None, critical = 5):
        self.baseMaxHP = hp
        self.hp = hp
        self.baseArmor = armor
        self.basePower = power
        self.deathFunction = deathFunction
        self.xp = xp
        self.baseAccuracy = accuracy
        self.baseEvasion = evasion
        self.baseCritical = critical
        
        self.frozen = False
        self.freezeCooldown = 0
        
        self.burning = False
        self.burnCooldown = 0
        
        self.healCountdown = 10
        self.MPRegenCountdown = 10
        
        self.baseMaxMP = maxMP
        self.MP = maxMP
        
        if knownSpells != None:
            self.knownSpells = knownSpells
        else:
            self.knownSpells = []
        
        self.spellsOnCooldown = []

    @property
    def power(self):
        bonus = sum(equipment.powerBonus for equipment in getAllEquipped(self.owner))
        return self.basePower + bonus
 
    @property
    def armor(self):
        bonus = sum(equipment.armorBonus for equipment in getAllEquipped(self.owner))
        return self.baseArmor + bonus
 
    @property
    def maxHP(self):
        bonus = sum(equipment.maxHP_Bonus for equipment in getAllEquipped(self.owner))
        return self.baseMaxHP + bonus

    @property
    def accuracy(self):
        bonus = sum(equipment.accuracyBonus for equipment in getAllEquipped(self.owner))
        return self.baseAccuracy + bonus

    @property
    def evasion(self):
        bonus = sum(equipment.evasionBonus for equipment in getAllEquipped(self.owner))
        return self.baseEvasion + bonus

    @property
    def critical(self):
        bonus = sum(equipment.criticalBonus for equipment in getAllEquipped(self.owner))
        return self.baseCritical + bonus

    @property
    def maxMP(self):
        bonus = sum(equipment.maxMP_Bonus for equipment in getAllEquipped(self.owner))
        return self.baseMaxMP + bonus
        
    def takeDamage(self, damage):
        if damage > 0:
            self.hp -= damage
        if self.hp <= 0:
            death=self.deathFunction
            if death is not None:
                death(self.owner)
            if self.owner != player:
                player.Fighter.xp += self.xp

    def toHit(self, target):
        attack = randint(1, 100)
        hit = False
        criticalHit = False
        if target.Fighter.evasion < 1:
            currentEvasion = 1
        else:
            currentEvasion = target.Fighter.evasion
        if self.accuracy < 1:
            currentAccuracy = 1
        else:
            currentAccuracy = self.accuracy
        hitRatio = int((currentAccuracy / currentEvasion) * 100)
        if DEBUG:
            message(self.owner.name.capitalize() + ' rolled a ' + str(attack) + ' over ' + str(hitRatio), colors.violet)
        if attack <= hitRatio and attack < 96:
            hit = True
            if attack <= self.critical:
                criticalHit = True
        return hit, criticalHit

    def attack(self, target):
        [hit, criticalHit] = self.toHit(target)
        if hit:
            if criticalHit:
                damage = (self.power - target.Fighter.armor) * 3
            else:
                damage = self.power - target.Fighter.armor
            if not self.frozen:
                if not self.owner.Player:
                    if damage > 0:
                        if criticalHit:
                            message(self.owner.name.capitalize() + ' critically hits you for ' + str(damage) + ' hit points!', colors.dark_orange)
                        else:
                            message(self.owner.name.capitalize() + ' attacks you for ' + str(damage) + ' hit points.', colors.orange)
                        target.Fighter.takeDamage(damage)
                    else:
                        message(self.owner.name.capitalize() + ' attacks you but it has no effect!')
                else:
                    if damage > 0:
                        if criticalHit:
                            message('You critically hit ' + target.name + ' for ' + str(damage) + ' hit points!', colors.darker_green)
                        else:
                            message('You attack ' + target.name + ' for ' + str(damage) + ' hit points.', colors.dark_green)
                        target.Fighter.takeDamage(damage)
                        weapon = getEquippedInSlot('right hand')
                        if weapon is not None:
                            if weapon.burning:
                                applyBurn(target, chance = 25)
                    
                    else:
                        message('You attack ' + target.name + ' but it has no effect!', colors.grey)
        else:
            if not self.owner.Player:
                message(self.owner.name.capitalize() + ' missed you!', colors.white)
            else:
                message('You missed ' + target.name + '!', colors.grey)
        
    def heal(self, amount):
        self.hp += amount
        if self.hp > self.maxHP:
            self.hp = self.maxHP

class BasicMonster: #Basic monsters' AI
    def takeTurn(self):
        monster = self.owner
        if (monster.x, monster.y) in visibleTiles: #chasing the player
            if monster.distanceTo(player) >= 2:
                monster.moveAstar(player.x, player.y)
            elif player.Fighter.hp > 0 and not monster.Fighter.frozen:
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
        equipment = self.owner.Equipment
        if equipment and getEquippedInSlot(equipment.slot) is None:
            equipment.equip()
    def use(self):
        if self.owner.Equipment:
            self.owner.Equipment.toggleEquip()
            return
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
        if self.owner.Equipment:
            self.owner.Equipment.unequip()
            
class Spell:
    "Class used by all active abilites (not just spells)"
    def __init__(self,  ressourceCost, cooldown, useFunction, name, ressource = 'MP', type = 'Magic', arg1 = None, arg2 = None, arg3 = None):
        self.ressource = ressource
        self.ressourceCost = ressourceCost
        self.maxCooldown = cooldown
        self.curCooldown = 0
        self.useFunction = useFunction
        self.name = name
        self.type = type
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def cast(self):
        if self.arg1 is None:
            if self.useFunction() != 'cancelled':
                return 'used'
            else:
                return 'cancelled'
        elif self.arg2 is None and self.arg1 is not None:
            if self.useFunction(self.arg1) != 'cancelled':
                return 'used'
            else:
                return 'cancelled'
        elif self.arg3 is None and self.arg2 is not None:
            if self.useFunction(self.arg1, self.arg2) != 'cancelled':
                return 'used'
            else:
                return 'cancelled'
        elif self.arg3 is not None:
            if self.useFunction(self.arg1, self.arg2, self.arg3) != 'cancelled':
                return 'used'
            else:
                return 'cancelled'
                

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
        player.Fighter.baseMaxHP += 1000
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
    elif userInput.keychar.upper() == 'F8' and DEBUG and not tdl.event.isWindowClosed():
        castCreateSword()
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == 'F9' and DEBUG and not tdl.event.isWindowClosed():
        castCreateWall()
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == "W" or userInput.keychar.upper() == 'KP5':
        if NATURAL_REGEN:
            if not player.Fighter.burning and not player.Fighter.frozen and  player.Fighter.hp != player.Fighter.maxHP:
                player.Fighter.healCountdown -= 1
                if player.Fighter.healCountdown < 0:
                    player.Fighter.healCountdown = 0
                if player.Fighter.healCountdown == 0:
                    player.Fighter.heal(1)
                    player.Fighter.healCountdown= 10
                 
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
                    '\n Attack: ' + str(player.Fighter.power) + '\n Armor: ' + str(player.Fighter.armor), [], CHARACTER_SCREEN_WIDTH)
        
    elif userInput.keychar == 'd' and gameState == 'playing':
        chosenItem = inventoryMenu('Press the key next to an item to drop it, or press any other key to cancel.')
        if chosenItem is not None:
            chosenItem.drop()
    elif userInput.keychar.upper() == 'Z' and gameState == 'playing':
        chosenSpell = spellsMenu('Press the key next to a spell to use it')
        if chosenSpell == None:
            FOV_recompute = True
            if DEBUG:
                message('No spell chosen', colors.violet)
            return 'didnt-take-turn'
        else:
            if chosenSpell.ressource == 'MP' and player.Fighter.MP < chosenSpell.ressourceCost:
                FOV_recompute = True
                message('Not enough MP to cast ' + chosenSpell.name +'.')
                return 'didnt-take-turn'
            else:
                action = chosenSpell.cast()
                if action == 'cancelled':
                    FOV_recompute = True
                    return 'didnt-take-turn'
                else:
                    FOV_recompute = True
                    player.Fighter.knownSpells.remove(chosenSpell)
                    chosenSpell.curCooldown = chosenSpell.maxCooldown
                    player.Fighter.spellsOnCooldown.append(chosenSpell)
                    if chosenSpell.ressource == 'MP':
                        player.Fighter.MP -= chosenSpell.ressourceCost
                    elif chosenSpell.ressource == 'HP':
                        player.Fighter.takeDamage(chosenSpell.ressourceCost)

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
                
        elif userInput.keychar.upper() == '<':  
            if dungeonLevel > 1:
                saveLevel()
                for object in objects:    
                    if upStairs.x == player.x and upStairs.y == player.y:
                        global dungeonLevel
                        loadLevel(dungeonLevel - 1)
                        dungeonLevel -= 1
            FOV_recompute = True
        elif userInput.keychar.upper() == '>':
            for object in objects:
                if stairs.x == player.x and stairs.y == player.y:
                    nextLevel()
        elif userInput.keychar.upper() == 'I':
            chosenItem = inventoryMenu('Press the key next to an item to use it, or any other to cancel.\n')
            if chosenItem is not None:
                using = chosenItem.use()
                if using == 'cancelled':
                    FOV_recompute = True
                    return 'didnt-take-turn'
        elif userInput.keychar.upper() == 'E':
            chosenItem = equipmentMenu('Press the key next to an equipment to unequip it')
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
    global FOV_recompute, actualPerSkills
    levelUp_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    if player.Fighter.xp >= levelUp_xp:
        player.level += 1
        player.Fighter.xp -= levelUp_xp
        message('Your battle skills grow stronger! You reached level ' + str(player.level) + '!', colors.yellow)
        
        #applying Class specific stat boosts
        player.Fighter.basePower += levelUpStats[0]
        player.Fighter.baseAccuracy += levelUpStats[1]
        player.Fighter.baseEvasion += levelUpStats[2]
        player.Fighter.baseArmor += levelUpStats[3]
        player.Fighter.baseMaxHP += levelUpStats[4]
        player.Fighter.hp += levelUpStats[4]
        player.Fighter.baseMaxMP += levelUpStats[5]
        player.Fighter.MP += levelUpStats[5]
        player.Fighter.baseCritical += levelUpStats[6]
        
        choice = None
        while choice == None:
            choice = menu('Level up! Choose a skill to raise: \n',
                ['Light Weapons (from ' + str(actualPerSkills[0]) + ')',
                 'Heavy Weapons (from ' + str(actualPerSkills[1]) + ')',
                 'Missile Weapons (from ' + str(actualPerSkills[2]) + ')',
                 'Throwing Weapons (from ' + str(actualPerSkills[3]) + ')',
                 'Magic (from ' + str(actualPerSkills[4]) + ')',
                 'Armor wielding (from ' + str(actualPerSkills[5]) + ')',
                 'Athletics (from ' + str(actualPerSkills[6]) + ')',
                 'Concentration (from ' + str(actualPerSkills[7]) + ')',
                 'Dodge (from ' + str(actualPerSkills[8]) + ')',
                 'Critical (from ' + str(actualPerSkills[9]) + ')',
                 'Accuracy (from ' + str(actualPerSkills[10]) + ')',], LEVEL_SCREEN_WIDTH)
            if choice != None:
                if actualPerSkills[choice] < 5:
                    player.Fighter.basePower += skillsBonus[choice][0]
                    player.Fighter.baseAccuracy += skillsBonus[choice][1]
                    player.Fighter.baseEvasion += skillsBonus[choice][2]
                    player.Fighter.baseArmor += skillsBonus[choice][3]
                    player.Fighter.baseMaxHP += skillsBonus[choice][4]
                    player.Fighter.hp += skillsBonus[choice][4]
                    player.Fighter.baseMaxMP += skillsBonus[choice][5]
                    player.Fighter.MP += skillsBonus[choice][5]
                    player.Fighter.baseCritical += skillsBonus[choice][6]

                    actualPerSkills[choice] += 1
                    
                    FOV_recompute = True
                    Update()
                    break
                elif actualPerSkills[choice] >= 5:
                    choice = None

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

def getMoveCost(destX, destY, sourceX, sourceY):
    if isBlocked(destX, destY):
        return None
    else:
        cost = tileDistance(destX, destY, sourceX, sourceY)
        return int(cost)
    
def castRegenMana(regenAmount):
    if player.Fighter.MP != player.Fighter.maxMP:
        player.Fighter.MP += regenAmount
        regened = regenAmount
        if player.Fighter.MP > player.Fighter.maxMP:
            overflow = player.Fighter.maxMP - player.Fighter.MP
            regened = regenAmount - overflow
            player.Fighter.MP = player.Fighter.maxMP
        message("You recovered " + str(regened) + " MP.", colors.green)
    else:
        message("Your MP are already maxed out")
        return "cancelled"

def castDarkRitual(regen, damage):
    message('You take ' + str(damage) + ' damage from the ritual !', colors.red)
    castRegenMana(regen)

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
                applyBurn(obj)

def castCreateWall():
    target = targetTile()
    if target == 'cancelled':
        return target
    else:
        (x,y) = target
        if not isBlocked(x, y):
            global myMap
            myMap[x][y].blocked = True
            myMap[x][y].block_sight = True

def applyBurn(target, chance = 50):
    if target.Fighter and randint(0, 100) > chance and not target.Fighter.burning:
        if not target.Fighter.frozen:
            target.Fighter.burning = True
            target.Fighter.burnCooldown = 4
            message('The ' + target.name + ' is set afire') 
        else:
            target.Fighter.frozen = False
            target.Fighter.freezeCooldown = 0
            message('The ' + target.name + "'s ice melts away.")

fireball = Spell(ressourceCost = 5, cooldown = 5, useFunction = castFireball, name = "Fireball", ressource = 'MP', type = 'Magic', arg1 = 3, arg2 = 12, arg3 = None)
heal = Spell(ressourceCost = 6, cooldown = 7, useFunction = castHeal, name = 'Heal self', ressource = 'MP', type = 'Magic', arg1 = 10, arg2 = None, arg3 = None)
darkPact = Spell(ressourceCost = DARK_PACT_DAMAGE, cooldown = 8, useFunction = castDarkRitual, name = "Dark ritual", ressource = 'HP', type = "Occult", arg1 = 5, arg2 = DARK_PACT_DAMAGE , arg3=None)
                
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
        fighterComponent = Fighter(hp=15, armor=0, power=3, xp = 35, deathFunction = monsterDeath, evasion = 25, accuracy = 10)
        AI_component = BasicMonster()
        monster = GameObject(x, y, char = 'o', color = colors.desaturated_green, name = 'orc', blocks = True, Fighter=fighterComponent, AI = AI_component)
        return monster
    else:
        return 'cancelled'
    
def createHiroshiman(x, y):
    if x != player.x or y != player.y:
        fighterComponent = Fighter(hp=150, armor=0, power=3, xp = 500, deathFunction = monsterDeath, accuracy = 0, evasion = 1)
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
def castCreateSword():
    target = targetTile()
    if target == 'cancelled':
        return 'cancelled'
    else:
        (x,y) = target
        sword = createSword(x, y)
        objects.append(sword)


def learnSpell(spell):
    if spell not in player.Fighter.knownSpells:
        player.Fighter.knownSpells.append(spell)
        message("You learn " + spell.name + " !", colors.green)
    else:
        message("You already know this spell")
        return "cancelled"

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
                fighterComponent = Fighter(hp=20, armor=2, power=4, xp = 100, deathFunction = monsterDeath, accuracy = 7, evasion = 1)
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

#_____________ EQUIPEMENT ________________
class Equipment:
    def __init__(self, slot, type, powerBonus=0, armorBonus=0, maxHP_Bonus=0, accuracyBonus=0, evasionBonus=0, criticalBonus = 0, maxMP_Bonus = 0, burning = False):
        self.slot = slot
        self.type = type
        self.basePowerBonus = powerBonus
        self.armorBonus = armorBonus
        self.maxHP_Bonus = maxHP_Bonus
        self.accuracyBonus = accuracyBonus
        self.evasionBonus = evasionBonus
        self.criticalBonus = criticalBonus
        self.maxMP_Bonus = maxMP_Bonus
        self.isEquipped = False
        
        self.burning = burning
 
    def toggleEquip(self):
        if self.isEquipped:
            self.unequip()
        else:
            self.equip()
 
    def equip(self):
        oldEquipment = getEquippedInSlot(self.slot)
        if oldEquipment is not None:
            oldEquipment.unequip()
        inventory.remove(self.owner)
        equipmentList.append(self.owner)
        self.isEquipped = True
        message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', colors.light_green)
 
    def unequip(self):
        if not self.isEquipped: return
        self.isEquipped = False
        equipmentList.remove(self.owner)
        if len(inventory) <= 26:
            inventory.append(self.owner)
            message('Unequipped ' + self.owner.name + ' from ' + self.slot + '.', colors.light_yellow)
        else:
            message('Not enough space in inventory to keep ' + self.owner.name + '.', colors.light_yellow)
            self.owner.x = player.x
            self.owner.y = player.y
            message('Dropped ' + self.owner.name)

    @property
    def powerBonus(self):
        if self.type == 'light weapon':
            bonus = (20 * actualPerSkills[0]) / 100
            return int(self.basePowerBonus * bonus + self.basePowerBonus)
        if self.type == 'heavy weapon':
            bonus = (20 * actualPerSkills[1]) / 100
            return int(self.basePowerBonus * bonus + self.basePowerBonus)
        if self.type == 'missile weapon':
            bonus = (20 * actualPerSkills[2]) / 100
            return int(self.basePowerBonus * bonus + self.basePowerBonus)
        if self.type == 'throwing weapon':
            bonus = (20 * actualPerSkills[3]) / 100
            return int(self.basePowerBonus * bonus + self.basePowerBonus)

def getEquippedInSlot(slot):
    for object in equipmentList:
        if object.Equipment and object.Equipment.slot == slot and object.Equipment.isEquipped:
            return object.Equipment
    return None

def getAllEquipped(object):  #returns a list of equipped items
    if object == player:
        equippedList = []
        for item in equipmentList:
            if item.Equipment and item.Equipment.isEquipped:
                equippedList.append(item.Equipment)
        return equippedList
    else:
        return []
#_____________ EQUIPEMENT ________________
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



def inventoryMenu(header):
    #show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in inventory:
            text = item.name
            if item.Equipment and item.Equipment.isEquipped:
                text = text + ' (on ' + item.Equipment.slot + ')'
            options.append(text)
    index = menu(header, options, INVENTORY_WIDTH)
    if index is None or len(inventory) == 0:
        return None
    else:
        return inventory[index].Item

def spellsMenu(header):
    #shows a menu with each known ready spell as an option
    borked = False
    if len(player.Fighter.knownSpells) == 0:
        options = []
        showableHeader = "You don't have any spells ready right now"
    else:
        options = []
        try:
            for spell in player.Fighter.knownSpells:
                text = spell.name
                options.append(text)
            showableHeader = header
        except TDLError:
            options = []
            borked = True
    index = menu(showableHeader, options, INVENTORY_WIDTH)
    if index is None or len(player.Fighter.knownSpells) == 0 or borked:
        global DEBUG
        if DEBUG:
            message('No spell selected in menu', colors.purple)
        return None
    else:
        return player.Fighter.knownSpells[index]


def equipmentMenu(header):
    if len(equipmentList) == 0:
        options = ['You have nothing equipped']
    else:
        options = []
        for item in equipmentList:
            text = item.name
            if item.Equipment and item.Equipment.isEquipped:
                powBonus = item.Equipment.basePowerBonus
                skillPowBonus = item.Equipment.powerBonus - powBonus
                hpBonus = item.Equipment.maxHP_Bonus
                defBonus = item.Equipment.armorBonus
                if powBonus != 0 or hpBonus !=0 or defBonus != 0:
                    info = '['
                    if powBonus != 0:
                        info = info + 'POWER + ' + str(powBonus) + ' + ' + str(skillPowBonus)
                    if hpBonus != 0:
                        if powBonus == 0:
                            info = info + 'HP + ' + str(hpBonus)
                        else:
                            info = info + ' HP + ' + str(hpBonus)
                    if defBonus != 0:
                        if powBonus == 0 and hpBonus == 0:
                            info = info + 'DEF + ' + str(defBonus)
                        else:
                            info = info + ' DEF + ' + str(defBonus)
                    info = info + ']'
                else:
                    info = ''
                text = text + ' ' + info + ' (on ' + item.Equipment.slot + ')'
            options.append(text)
    index = menu(header, options, INVENTORY_WIDTH)
    if index is None or len(equipmentList) == 0:
        return None
    else:
        return equipmentList[index].Item



def mainMenu():
    global playerComponent, levelUpStats, actualPerSkills, skillsBonus
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
                [playerComponent, levelUpStats, actualPerSkills, skillsBonus] = characterCreation()
                if playerComponent != 'cancelled':
                    newGame()
                    playGame()
                else:
                    mainMenu()
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
    global FOV_recompute, visibleTiles, pathfinder
    FOV_recompute = True
    visibleTiles = tdl.map.quickFOV(player.x, player.y, isVisibleTile, fov = FOV_ALGO, radius = SIGHT_RADIUS, lightWalls = FOV_LIGHT_WALLS)
    pathfinder = tdl.map.AStar(MAP_WIDTH, MAP_HEIGHT, callback = getMoveCost, advanced=True)
    con.clear()

def Update():
    global FOV_recompute
    global visibleTiles
    global tilesinPath
    con.clear()
    tdl.flush()
    player.Player.changeColor()
    if FOV_recompute:
        FOV_recompute = False
        global pathfinder
        visibleTiles = tdl.map.quickFOV(player.x, player.y, isVisibleTile, fov = FOV_ALGO, radius = SIGHT_RADIUS, lightWalls = FOV_LIGHT_WALLS)
        pathfinder = tdl.map.AStar(MAP_WIDTH, MAP_HEIGHT, callback = getMoveCost, advanced=True)
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
                if DEBUG:
                    inPath = (x,y) in tilesinPath
                    if inPath:
                        con.draw_char(x, y, 'X', fg = colors.green, bg = None)
                        tilesinPath = []
                        
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
    #panel.draw_str(1, 3, 'Dungeon level: ' + str(dungeonLevel), colors.white)
    panel.draw_str(1, 5, 'Player level: ' + str(player.level) + ' | Floor: ' + str(dungeonLevel), colors.white)
    renderBar(1, 1, BAR_WIDTH, 'HP', player.Fighter.hp, player.Fighter.maxHP, player.color, colors.dark_gray)
    renderBar(1, 3, BAR_WIDTH, 'MP', player.Fighter.MP, player.Fighter.maxMP, colors.blue, colors.dark_gray)
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
def accessMapFile(level = dungeonLevel):
    mapName = "map{}".format(level)
    mapFile = os.path.join(absDirPath, mapName)
    return mapName


def saveGame():
    
    if not os.path.exists(absDirPath):
        os.makedirs(absDirPath)
    
    file = shelve.open(absFilePath, "n")
    file["dungeonLevel"] = dungeonLevel
    file["myMap_level{}".format(dungeonLevel)] = myMap
    print("Saved myMap_level{}".format(dungeonLevel))
    file["objects_level{}".format(dungeonLevel)] = objects
    file["playerIndex"] = objects.index(player)
    file["stairsIndex"] = objects.index(stairs)
    file["inventory"] = inventory
    file["equipmentList"] = equipmentList
    file["gameMsgs"] = gameMsgs
    file["gameState"] = gameState
    if dungeonLevel > 1:
        file["upStairsIndex"] = objects.index(upStairs)
    file.close()
    
    #mapFile = open(absPicklePath, 'wb')
    #pickle.dump(myMap, mapFile)
    #mapFile.close()

def newGame():
    global objects, inventory, gameMsgs, gameState, player, dungeonLevel
    startingSpells = [fireball, heal]
    playFight = Fighter(hp = playerComponent[4], power= playerComponent[0], armor= playerComponent[3], deathFunction=playerDeath, xp=0, evasion = playerComponent[2], accuracy = playerComponent[1], maxMP= playerComponent[5], knownSpells=startingSpells, critical = playerComponent[6])
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
    equipmentComponent = Equipment(slot='right hand', type = 'light weapon', powerBonus=2)
    object = GameObject(0, 0, '-', 'dagger', colors.light_sky, Equipment=equipmentComponent, Item=Item(), darkColor = colors.darker_sky)
    inventory.append(object)
    equipmentComponent.equip()
    object.alwaysVisible = True

def loadGame():
    global objects, inventory, gameMsgs, gameState, player, dungeonLevel, myMap, equipmentList, stairs, upStairs
    
    
    #myMap = [[Tile(True) for y in range(MAP_HEIGHT)]for x in range(MAP_WIDTH)]
    file = shelve.open(absFilePath, "r")
    dungeonLevel = file["dungeonLevel"]
    myMap = file["myMap_level{}".format(dungeonLevel)]
    objects = file["objects_level{}".format(dungeonLevel)]
    player = objects[file["playerIndex"]]
    stairs = objects[file["stairsIndex"]]
    inventory = file["inventory"]
    equipmentList = file["equipmentList"]
    gameMsgs = file["gameMsgs"]
    gameState = file["gameState"]
    if dungeonLevel > 1:
        upStairs = objects[file["upStairsIndex"]]
    #mapFile = open(absPicklePath, "rb")
    #myMap = pickle.load(mapFile)
    #mapFile.close()

def saveLevel():
    #if not os.path.exists(absDirPath):
        #os.makedirs(absDirPath)
    
    #if not os.path.exists(absFilePath):
        #file = shelve.open(absFilePath, "n")
        #print()
    #else:
        #file = shelve.open(absFilePath, "w")
    mapFilePath = accessMapFile()
    mapFile = shelve.open(mapFilePath, "w")
    mapFile["myMap"] = myMap
    mapFile["objects"] = objects
    mapFile["playerIndex"] = objects.index(player)
    mapFile["stairsIndex"] = objects.index(stairs)
    if dungeonLevel > 1:
        mapFile["upStairsIndex"] = objects.index(upStairs)
    mapFile["yunowork"] = "SCREW THIS"
    mapFile.close()
    
    return "completed"

def loadLevel(level):
    global objects, player, myMap, stairs
    mapFilePath = accessMapFile(level)
    file = shelve.open(mapFilePath, "r")
    print(file["yunowork"])
    myMap = file["myMap_level{}".format(level)]
    objects = file["objects_level{}".format(level)]
    player = objects[file["playerIndex"]]
    stairs = objects[file["stairsIndex"]]
    if level > 1:
        global upStairs
        upStairs = objects[file["upStairsIndex"]]
    
    message("You climb the stairs")
    file.close()
    initializeFOV()
    

def nextLevel():
    global dungeonLevel
    returned = "borked"
    while returned != "completed":
        returned = saveLevel()
    message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', colors.red)
    dungeonLevel += 1
    tempMap = myMap
    tempObjects = objects
    tempPlayer = player
    tempStairs = stairs
    try:
        loadLevel(dungeonLevel)
        print("Loaded existing level {}".format(dungeonLevel))
    except:
        global myMap, objects, player, stairs
        myMap = tempMap
        objects = tempObjects
        player = tempPlayer
        stairs = tempStairs
        makeMap()  #create a fresh new level!
        print("Created a new level")
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
                    try:
                        object.Fighter.burnCooldown -= 1
                        object.Fighter.takeDamage(3)
                        message('The ' + object.name + ' keeps burning !')
                        if object.Fighter.burnCooldown < 0:
                            object.Fighter.burnCooldown = 0
                        if object.Fighter.burnCooldown == 0:
                            object.Fighter.burning = False
                            message(object.name.capitalize() + "'s flames die down", colors.darker_orange)
                    except AttributeError:
                        global DEBUG
                        if DEBUG:
                            message('Failed to apply burn to ' + object.name, colors.violet)
                if object.Fighter and object.Fighter.spellsOnCooldown:
                    try:
                        for spell in object.Fighter.spellsOnCooldown:
                            spell.curCooldown -= 1
                            if spell.curCooldown < 0:
                                spell.curCooldown = 0
                            if spell.curCooldown == 0:
                                object.Fighter.spellsOnCooldown.remove(spell)
                                object.Fighter.knownSpells.append(spell)
                                if object == player:
                                    message(spell.name + " is now ready.")
                    except:
                        continue
                if object.Fighter and object.Fighter.MP < object.Fighter.maxMP:
                    object.Fighter.MPRegenCountdown -= 1
                    if object.Fighter.MPRegenCountdown < 0:
                        object.Fighter.MPRegenCountdown = 0
                    if object.Fighter.MPRegenCountdown == 0:
                        object.Fighter.MPRegenCountdown = 10
                        object.Fighter.MP += 1
    DEBUG = False
    quitGame('Window has been closed')
    
mainMenu()