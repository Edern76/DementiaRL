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
from code.constants import WIDTH, HEIGHT, MAP_HEIGHT, MAP_WIDTH, MID_MAP_HEIGHT, MID_MAP_WIDTH, con, root, NATURAL_REGEN, LEVEL_UP_BASE, LEVEL_UP_FACTOR, LEVEL_SCREEN_WIDTH, CONFUSE_NUMBER_TURNS, CHARACTER_SCREEN_WIDTH, MOVEMENT_KEYS, panel, MSG_WIDTH, MAX_ROOM_MONSTERS, INVENTORY_WIDTH, BAR_WIDTH, FOV_ALGO, SIGHT_RADIUS, FOV_LIGHT_WALLS, PANEL_Y, PANEL_HEIGHT, MSG_X, CONFUSE_RANGE, LIGHTNING_RANGE, LIGHTNING_DAMAGE, DARK_PACT_DAMAGE, MAX_ROOM_ITEMS, MSG_HEIGHT 
from code.charGen import characterCreation
# End of anti-bananas-going lines, everything below this line is essential
from code.menu import *
from code.charGen import *
from code.gameobject import *
from code.sharedvariables import *
from code.mapcreation import *
from code import sharedvariables

# Naming conventions :
# MY_CONSTANT
# myVariable
# myFunction()
# MyClass
# Not dramatic if you forget about this (it happens to me too), but it makes reading code easier

#NEVER SET AN EVASION VALUE AT ZERO, SET IT AT ONE INSTEAD#




#_____________ CONSTANTS __________________

class Spell:
    "Class used by all active abilites (not just spells)"
    def __init__(self,  ressourceCost, cooldown, useFunction, name, ressource = 'MP', type = 'Magic', magicLevel = 0, arg1 = None, arg2 = None, arg3 = None):
        self.ressource = ressource
        self.ressourceCost = ressourceCost
        self.maxCooldown = cooldown
        self.curCooldown = 0
        self.useFunction = useFunction
        self.name = name
        self.type = type
        self.magicLevel = magicLevel
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
        sharedvariables.player.Fighter.takeDamage(1)
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
        sharedvariables.player.Fighter.baseMaxHP += 1000
        sharedvariables.player.Fighter.hp = sharedvariables.player.Fighter.maxHP
        message('Healed sharedvariables.player and increased their maximum HP value by 1000', colors.purple)
        FOV_recompute = True
    elif userInput.keychar.upper() == "F6" and DEBUG and not tdl.event.isWindowClosed():
        sharedvariables.player.Fighter.frozen = True
        sharedvariables.player.Fighter.freezeCooldown = 3
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
    elif userInput.keychar == 'S' and DEBUG and not tdl.event.isWindowClosed():
        message("Force-saved level {}", colors.purple)
        saveLevel()
    elif userInput.keychar == 'Q' and DEBUG and not tdl.event.isWindowClosed():
        global FOV_recompute
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
        if NATURAL_REGEN:
            if not sharedvariables.player.Fighter.burning and not sharedvariables.player.Fighter.frozen and  sharedvariables.player.Fighter.hp != sharedvariables.player.Fighter.maxHP:
                sharedvariables.player.Fighter.healCountdown -= 1
                if sharedvariables.player.Fighter.healCountdown < 0:
                    sharedvariables.player.Fighter.healCountdown = 0
                if sharedvariables.player.Fighter.healCountdown == 0:
                    sharedvariables.player.Fighter.heal(1)
                    sharedvariables.player.Fighter.healCountdown= 10
                 
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
        lookCursor = GameObject(x = sharedvariables.player.x, y = sharedvariables.player.y, char = 'X', name = 'cursor', color = colors.yellow, Ghost = True)
        objects.append(lookCursor)
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == 'C':
        levelUp_xp = LEVEL_UP_BASE + sharedvariables.player.level * LEVEL_UP_FACTOR
        menu('Character Information \n \n Level: ' + str(sharedvariables.player.level) + '\n Experience: ' + str(sharedvariables.player.Fighter.xp) +
                    '\n Experience to level up: ' + str(levelUp_xp) + '\n \n Maximum HP: ' + str(sharedvariables.player.Fighter.maxHP) +
                    '\n Attack: ' + str(sharedvariables.player.Fighter.power) + '\n Armor: ' + str(sharedvariables.player.Fighter.armor), [], CHARACTER_SCREEN_WIDTH)
        
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
            if chosenSpell.magicLevel > sharedvariables.player.Player.actualPerSkills[4]:
                FOV_recompute = True
                message('Your arcane knowledge is not high enough to cast ' + chosenSpell.name + '.')
                return 'didnt-take-turn'
            else:
                if chosenSpell.ressource == 'MP' and sharedvariables.player.Fighter.MP < chosenSpell.ressourceCost:
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
                        sharedvariables.player.Fighter.knownSpells.remove(chosenSpell)
                        chosenSpell.curCooldown = chosenSpell.maxCooldown
                        sharedvariables.player.Fighter.spellsOnCooldown.append(chosenSpell)
                        if chosenSpell.ressource == 'MP':
                            sharedvariables.player.Fighter.MP -= chosenSpell.ressourceCost
                        elif chosenSpell.ressource == 'HP':
                            sharedvariables.player.Fighter.takeDamage(chosenSpell.ressourceCost)

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
                if object.x == sharedvariables.player.x and object.y == sharedvariables.player.y and object.Item is not None:
                    object.Item.pickUp()
                    break
                
        elif userInput.keychar.upper() == '<':  
            if dungeonLevel > 1:
                saveLevel()
                for object in objects:    
                    if upStairs.x == sharedvariables.player.x and upStairs.y == sharedvariables.player.y:
                        if stairCooldown == 0:
                            global stairCooldown, dungeonLevel
                            stairCooldown = 2
                            if DEBUG:
                                message("Stair cooldown set to {}".format(stairCooldown), colors.purple)
                            loadLevel(dungeonLevel - 1)
                        else:
                            message("You're too tired to climb the stairs right now")
                        return None
            FOV_recompute = True
        elif userInput.keychar.upper() == '>':
            for object in objects:
                if stairs.x == sharedvariables.player.x and stairs.y == sharedvariables.player.y:
                    if stairCooldown == 0:
                        global stairCooldown
                        stairCooldown = 2
                        if DEBUG:
                            message("Stair cooldown set to {}".format(stairCooldown), colors.purple)
                        nextLevel()
                    else:
                        message("You're too tired to climb down the stairs right now")
                    return None
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
    if sharedvariables.player.Fighter.MP != sharedvariables.player.Fighter.maxMP:
        sharedvariables.player.Fighter.MP += regenAmount
        regened = regenAmount
        if sharedvariables.player.Fighter.MP > sharedvariables.player.Fighter.maxMP:
            overflow = sharedvariables.player.Fighter.maxMP - sharedvariables.player.Fighter.MP
            regened = regenAmount - overflow
            sharedvariables.player.Fighter.MP = sharedvariables.player.Fighter.maxMP
        message("You recovered " + str(regened) + " MP.", colors.green)
    else:
        message("Your MP are already maxed out")
        return "cancelled"

def castDarkRitual(regen, damage):
    message('You take ' + str(damage) + ' damage from the ritual !', colors.red)
    castRegenMana(regen)

def castHeal(healAmount = 5):
    if sharedvariables.player.Fighter.hp == sharedvariables.player.Fighter.maxHP:
        message('You are already at full health')
        return 'cancelled'
    else:
        message('You are healed for {} HP !'.format(healAmount), colors.light_green)
        sharedvariables.player.Fighter.heal(healAmount)

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
        target.Fighter.freezeCooldown = 4 #Actually 3 turns since this begins ticking down the turn the spell is cast
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
                if obj != sharedvariables.player:
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

fireball = Spell(ressourceCost = 10, cooldown = 5, useFunction = castFireball, name = "Fireball", ressource = 'MP', type = 'Magic', magicLevel = 1, arg1 = 3, arg2 = 12, arg3 = None)
heal = Spell(ressourceCost = 15, cooldown = 12, useFunction = castHeal, name = 'Heal self', ressource = 'MP', type = 'Magic', magicLevel = 2, arg1 = 10, arg2 = None, arg3 = None)
darkPact = Spell(ressourceCost = DARK_PACT_DAMAGE, cooldown = 8, useFunction = castDarkRitual, name = "Dark ritual", ressource = 'HP', type = "Occult", magicLevel = 2, arg1 = 5, arg2 = DARK_PACT_DAMAGE , arg3=None)
                
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
        else:
            message('Please press a valid key (Y or N)')#Displays regardless of if a valid hcoice has been made, to be fixed
            FOV_recompute = True
            Update()
            
    radmax = radius + 2
    global explodingTiles
    global gameState
    for x in range (sharedvariables.player.x - radmax, sharedvariables.player.x + radmax):
        for y in range (sharedvariables.player.y - radmax, sharedvariables.player.y + radmax):
            try: #Execute code below try if no error is encountered
                if tileDistance(sharedvariables.player.x, sharedvariables.player.y, x, y) <= radius and not myMap[x][y].unbreakable:
                    myMap[x][y].blocked = False
                    myMap[x][y].block_sight = False
                    if x in range (1, MAP_WIDTH-1) and y in range (1,MAP_HEIGHT - 1):
                        explodingTiles.append((x,y))
                    for obj in objects:
                        if obj.Fighter and obj.x == x and obj.y == y: 
                            try:
                                if obj != sharedvariables.player:
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
                                if obj != sharedvariables.player:
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
    if x != sharedvariables.player.x or y != sharedvariables.player.y:
        equipmentComponent = Equipment(slot='head', type = 'armor', armorBonus = 1)
        orcHelmet = GameObject(x = None, y = None, char = '[', name = 'orc helmet', color = colors.brass, Equipment = equipmentComponent, Item = Item())
        fighterComponent = Fighter(hp=15, armor=0, power=3, xp = 35, deathFunction = monsterDeath, evasion = 25, accuracy = 10, lootFunction = orcHelmet, lootRate = 30)
        AI_component = BasicMonster()
        monster = GameObject(x, y, char = 'o', color = colors.desaturated_green, name = 'orc', blocks = True, Fighter=fighterComponent, AI = AI_component)
        return monster
    else:
        return 'cancelled'
    
def createHiroshiman(x, y):
    if x != sharedvariables.player.x or y != sharedvariables.player.y:
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
    if spell not in sharedvariables.player.Fighter.knownSpells:
        sharedvariables.player.Fighter.knownSpells.append(spell)
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
    if sharedvariables.player.Fighter.hp > 0:
        gameState = 'playing'
    else:
        gameState = 'dead'
#_____________ MAP CREATION __________________


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
            self.owner.x = sharedvariables.player.x
            self.owner.y = sharedvariables.player.y
            message('Dropped ' + self.owner.name)

    @property
    def powerBonus(self):
        if self.type == 'light weapon':
            bonus = (20 * sharedvariables.player.Player.actualPerSkills[0]) / 100
            return int(self.basePowerBonus * bonus + self.basePowerBonus)
        elif self.type == 'heavy weapon':
            bonus = (20 * sharedvariables.player.Player.actualPerSkills[1]) / 100
            return int(self.basePowerBonus * bonus + self.basePowerBonus)
        elif self.type == 'missile weapon':
            bonus = (20 * sharedvariables.player.Player.actualPerSkills[2]) / 100
            return int(self.basePowerBonus * bonus + self.basePowerBonus)
        elif self.type == 'throwing weapon':
            bonus = (20 * sharedvariables.player.Player.actualPerSkills[3]) / 100
            return int(self.basePowerBonus * bonus + self.basePowerBonus)
        else:
            return self.basePowerBonus

def getEquippedInSlot(slot):
    for object in equipmentList:
        if object.Equipment and object.Equipment.slot == slot and object.Equipment.isEquipped:
            return object.Equipment
    return None

def getAllEquipped(object):  #returns a list of equipped items
    if object == sharedvariables.player:
        equippedList = []
        for item in equipmentList:
            if item.Equipment and item.Equipment.isEquipped:
                equippedList.append(item.Equipment)
        return equippedList
    else:
        return []
#_____________ EQUIPEMENT ________________
def lootItem(object, x, y):
    objects.append(object)
    object.x = x
    object.y = y
    object.sendToBack()
    message('A ' + object.name + ' falls from the dead body !', colors.dark_sky)

def playerDeath():
    global gameState
    message('You died!', colors.red)
    gameState = 'dead'
    sharedvariables.player.char = '%'
    sharedvariables.player.color = colors.dark_red
 
def monsterDeath(monster):
    message(monster.name.capitalize() + ' is dead! You gain ' + str(monster.Fighter.xp) + ' XP.', colors.dark_sky)
    
    if monster.Fighter.lootFunction is not None:
        loot = randint(1, 100)
        if loot <= monster.Fighter.lootRate:
            lootItem(monster.Fighter.lootFunction, monster.x, monster.y)

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
    if len(sharedvariables.player.Fighter.knownSpells) == 0:
        options = []
        showableHeader = "You don't have any spells ready right now"
    else:
        options = []
        try:
            for spell in sharedvariables.player.Fighter.knownSpells:
                text = spell.name
                options.append(text)
            showableHeader = header
        except TDLError:
            options = []
            borked = True
    index = menu(showableHeader, options, INVENTORY_WIDTH)
    if index is None or len(sharedvariables.player.Fighter.knownSpells) == 0 or borked:
        global DEBUG
        if DEBUG:
            message('No spell selected in menu', colors.purple)
        return None
    else:
        return sharedvariables.player.Fighter.knownSpells[index]


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
                armBonus = item.Equipment.armorBonus
                if powBonus != 0 or hpBonus !=0 or armBonus != 0:
                    info = '['
                    if powBonus != 0:
                        info = info + 'POWER + ' + str(powBonus) + ' + ' + str(skillPowBonus)
                    if hpBonus != 0:
                        if powBonus == 0:
                            info = info + 'HP + ' + str(hpBonus)
                        else:
                            info = info + ' HP + ' + str(hpBonus)
                    if armBonus != 0:
                        if powBonus == 0 and hpBonus == 0:
                            info = info + 'ARMOR + ' + str(armBonus)
                        else:
                            info = info + ' ARMOR + ' + str(armBonus)
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
                [sharedvariables.playerComponent, levelUpStats, actualPerSkills, skillsBonus] = characterCreation()
                if sharedvariables.playerComponent != 'cancelled':
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
    visibleTiles = tdl.map.quickFOV(sharedvariables.player.x, sharedvariables.player.y, isVisibleTile, fov = FOV_ALGO, radius = SIGHT_RADIUS, lightWalls = FOV_LIGHT_WALLS)
    pathfinder = tdl.map.AStar(MAP_WIDTH, MAP_HEIGHT, callback = getMoveCost, advanced=True)
    con.clear()

def Update():
    global FOV_recompute
    global visibleTiles
    global tilesinPath
    con.clear()
    tdl.flush()
    sharedvariables.player.Player.changeColor()
    if FOV_recompute:
        FOV_recompute = False
        global pathfinder
        visibleTiles = tdl.map.quickFOV(sharedvariables.player.x, sharedvariables.player.y, isVisibleTile, fov = FOV_ALGO, radius = SIGHT_RADIUS, lightWalls = FOV_LIGHT_WALLS)
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
        if object != sharedvariables.player:
            if (object.x, object.y) in visibleTiles or (object.alwaysVisible and myMap[object.x][object.y].explored):
                object.draw()
    sharedvariables.player.draw()
    root.blit(con, 0, 0, WIDTH, HEIGHT, 0, 0)
    panel.clear(fg=colors.white, bg=colors.black)
    # Draw log
    msgY = 1
    for (line, color) in gameMsgs:
        panel.draw_str(MSG_X, msgY, line, bg=None, fg = color)
        msgY += 1
    # Draw GUI
    #panel.draw_str(1, 3, 'Dungeon level: ' + str(dungeonLevel), colors.white)
    panel.draw_str(1, 5, 'Player level: ' + str(sharedvariables.player.level) + ' | Floor: ' + str(dungeonLevel), colors.white)
    renderBar(1, 1, BAR_WIDTH, 'HP', sharedvariables.player.Fighter.hp, sharedvariables.player.Fighter.maxHP, sharedvariables.player.color, colors.dark_gray)
    renderBar(1, 3, BAR_WIDTH, 'MP', sharedvariables.player.Fighter.MP, sharedvariables.player.Fighter.maxMP, colors.blue, colors.dark_gray)
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
        return (sharedvariables.player.x, sharedvariables.player.y)
    
    gameState = 'targeting'
    cursor = GameObject(x = sharedvariables.player.x, y = sharedvariables.player.y, char = 'X', name = 'cursor', color = colors.yellow, Ghost = True)
    objects.append(cursor)
    for (rx, ry) in visibleTiles:
            if maxRange is None or sharedvariables.player.distanceToCoords(rx,ry) <= maxRange:
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
            if (cursor.x + dx, cursor.y + dy) in tilesInRange and (maxRange is None or sharedvariables.player.distanceTo(cursor) <= maxRange):
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
            if obj.x == x and obj.y == y and obj.Fighter and obj != sharedvariables.player:
                return obj
               

#______ INITIALIZATION AND MAIN LOOP________
def accessMapFile(level = dungeonLevel):
    mapName = "map{}".format(level)
    print(mapName)
    mapFile = os.path.join(absDirPath, mapName)
    return mapFile


def saveGame():
    
    if not os.path.exists(absDirPath):
        os.makedirs(absDirPath)
    
    file = shelve.open(absFilePath, "n")
    file["dungeonLevel"] = dungeonLevel
    file["myMap_level{}".format(dungeonLevel)] = myMap
    print("Saved myMap_level{}".format(dungeonLevel))
    file["objects_level{}".format(dungeonLevel)] = objects
    file["sharedvariables.playerIndex"] = objects.index(sharedvariables.player)
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
    playComp = Player(actualPerSkills, levelUpStats, skillsBonus)
    sharedvariables.player = GameObject(25, 23, '@', Fighter = playFight, Player = playComp, name = 'Hero', color = (0, 210, 0))
    sharedvariables.player.level = 1

    objects = [sharedvariables.player]
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
    sharedvariables.player = objects[file["sharedvariables.playerIndex"]]
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
    mapFile = shelve.open(mapFilePath, "n")
    mapFile["myMap"] = myMap
    mapFile["objects"] = objects
    mapFile["sharedvariables.playerIndex"] = objects.index(sharedvariables.player)
    mapFile["stairsIndex"] = objects.index(stairs)
    if dungeonLevel > 1:
        mapFile["upStairsIndex"] = objects.index(upStairs)
    mapFile["yunowork"] = "SCREW THIS"
    print("Saved level at " + mapFilePath)
    mapFile.close()
    
    return "completed"

def loadLevel(level):
    global objects, player, myMap, stairs, dungeonLevel
    try:
        saveLevel()
    except:
        print("Couldn't save level " + dungeonLevel)
    mapFilePath = accessMapFile(level)
    xfile = shelve.open(mapFilePath, "r")
    print(xfile["yunowork"])
    myMap = xfile["myMap"]
    objects = xfile["objects"]
    sharedvariables.player = objects[xfile["sharedvariables.playerIndex"]]
    stairs = objects[xfile["stairsIndex"]]
    if level > 1:
        global upStairs
        upStairs = objects[xfile["upStairsIndex"]]
    
    message("You climb the stairs")
    print("Loaded level " + str(level))
    xfile.close()
    dungeonLevel = level
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
    tempPlayer = sharedvariables.player
    tempStairs = stairs
    try:
        loadLevel(dungeonLevel)
        print("Loaded existing level {}".format(dungeonLevel))
    except:
        global myMap, objects, player, stairs
        myMap = tempMap
        objects = tempObjects
        sharedvariables.player = tempPlayer
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
        global FOV_recompute
        Update()
        checkLevelUp()
        tdl.flush()
        for object in objects:
            object.clear()
        sharedvariables.playerAction = getInput()
        FOV_recompute = True #So as to avoid the blackscreen bug no matter which key we press
        if sharedvariables.playerAction == 'exit':
            quitGame('Player pressed escape')
        if gameState == 'playing' and sharedvariables.playerAction != 'didnt-take-turn':
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
                                if object == sharedvariables.player:
                                    message(spell.name + " is now ready.")
                    except:
                        continue
                if object.Fighter and object.Fighter.MP < object.Fighter.maxMP:
                    object.Fighter.MPRegenCountdown -= 1
                    if object.Fighter.MPRegenCountdown < 0:
                        object.Fighter.MPRegenCountdown = 0
                    if object.Fighter.MPRegenCountdown == 0:
                        if object == sharedvariables.player:
                            object.Fighter.MPRegenCountdown = 10 - sharedvariables.player.Player.actualPerSkills[7]
                        else:
                            object.Fighter.MPRegenCountdown = 10
                        object.Fighter.MP += 1
            global stairCooldown
            if stairCooldown > 0:
                stairCooldown -= 1
                if stairCooldown == 0 and DEBUG:
                    message("You're no longer tired", colors.purple)
            if stairCooldown < 0:
                stairCooldown = 0
            
                            
    DEBUG = False
    quitGame('Window has been closed')
    
mainMenu()