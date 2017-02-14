import tdl, colors, math, textwrap, time, os, shelve, sys, code, gzip
import simpleaudio as sa
from tdl import *
from random import randint, choice
from math import *
from os import makedirs
from constants import MAX_HIGH_CULTIST_MINIONS
import nameGen
import xpLoaderPy3 as xpL
import dunbranches as dBr
from dunbranches import gluttonyDungeon

# Naming conventions :
# MY_CONSTANT
# myVariable
# myFunction()
# MyClass
# Not dramatic if you forget about this (it happens to me too), but it makes reading code easier

#NEVER SET AN EVASION VALUE AT ZERO, SET IT AT ONE INSTEAD#

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
MID_MAP_WIDTH, MID_MAP_HEIGHT = MAP_WIDTH//2, MAP_HEIGHT//2
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

CHARACTER_SCREEN_WIDTH = 50
CHARACTER_SCREEN_HEIGHT = 20
# - GUI Constants -

# - Consoles -
root = tdl.init(WIDTH, HEIGHT, 'Dementia')
con = tdl.Console(WIDTH, HEIGHT)
panel = tdl.Console(WIDTH, PANEL_HEIGHT)
# - Consoles

FOV_recompute = True
FOV_ALGO = 'BASIC'
FOV_LIGHT_WALLS = True
SIGHT_RADIUS = 10
MAX_ROOM_MONSTERS = 3
MAX_ROOM_ITEMS = 3
GRAPHICS = 'modern'
LEVEL_UP_BASE = 200 # Set to 200 once testing complete
LEVEL_UP_FACTOR = 150
NATURAL_REGEN = True

boss_FOV_recompute = True
BOSS_FOV_ALGO = 'BASIC'
BOSS_SIGHT_RADIUS = 60
bossDungeonsAppeared = {'gluttony': False}

# - Spells -
LIGHTNING_DAMAGE = 40
LIGHTNING_RANGE = 5
CONFUSE_NUMBER_TURNS = 10
CONFUSE_RANGE = 8
DARK_PACT_DAMAGE = 24
FIREBALL_SPELL_BASE_DAMAGE = 12
FIREBALL_SPELL_BASE_RADIUS = 1
FIREBALL_SPELL_BASE_RANGE = 4

RESURECTABLE_CORPSES = ["darksoul", "troll"]

BASE_HUNGER = 500
# - Spells -
#_____________ CONSTANTS __________________

myMap = None
color_dark_wall = colors.darkest_grey
color_light_wall = colors.darker_grey
color_dark_ground = colors.darkest_sepia
color_dark_gravel = (27, 20, 0)
color_light_ground = colors.darker_sepia
color_light_gravel = (50, 37, 0)

gameState = 'playing'
playerAction = None
DEBUG = False #If true, enables debug messages

lookCursor = None
cursor = None

gameMsgs = [] #List of game messages
tilesInRange = []
explodingTiles = []
tilesinPath = []
menuWindows = []
hiroshimanNumber = 0
FOV_recompute = True
inventory = []
equipmentList = []
activeSounds = []
########
# These need to be globals because otherwise Python will flip out when we try to look for some kind of stairs in the object lists.
stairs = None
upStairs = None
gluttonyStairs = None
########
hiroshimanHasAppeared = False
highCultistHasAppeared = False
player = None
currentBranch = dBr.mainDungeon #Setting this to None causes errors. It doesn't matter tough, since this gets updated on loading or starting a game.
dungeonLevel = 1

def findCurrentDir():
    if getattr(sys, 'frozen', False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)
    return datadir

def deleteSaves():
    os.chdir(absDirPath)
    saves = [save for save in os.listdir(absDirPath) if (save.endswith(".bak") or save.endswith(".dat") or save.endswith(".dir") or save.startswith("map"))]
    for save in saves:
        os.remove(save)
        print("Deleted " + str(save))

curDir = findCurrentDir()
relDirPath = "save"
relPath = "save\\savegame"
relPicklePath = "save\\equipment"
relAssetPath = "assets"
relSoundPath = "assets\\sound"
relAsciiPath = "assets\\ascii"
absDirPath = os.path.join(curDir, relDirPath)
absFilePath = os.path.join(curDir, relPath)
absPicklePath = os.path.join(curDir, relPicklePath)
absAssetPath = os.path.join(curDir, relAssetPath)
absSoundPath = os.path.join(curDir, relSoundPath)
absAsciiPath = os.path.join(curDir, relAsciiPath)

stairCooldown = 0
pathfinder = None
pathToTargetTile = []

def animStep(waitTime = .125):
    global FOV_recompute
    FOV_recompute = True
    Update()
    tdl.flush()
    time.sleep(waitTime)
    
def playWavSound(sound, forceStop = False):
    if forceStop:
        sa.stop_all()
    soundPath = os.path.join(absSoundPath, sound)
    waveObj = sa.WaveObject.from_wave_file(soundPath)
    waveObj.play()
    #TO-DO : Add an ear-rape prevention system, such as allowing sounds to be played every X milliseconds.

#_____________MENU_______________
def drawMenuOptions(y, options, window, page, width, height, headerWrapped, maxPages, pagesDisp):
    window.clear()
    for i, line in enumerate(headerWrapped):
        window.draw_str(0, 0+i, headerWrapped[i], fg = colors.yellow)
    if pagesDisp:
        window.draw_str(10, y - 2, str(page + 1) + '/' + str(maxPages + 1), fg = colors.yellow)
    letterIndex = ord('a')
    counter = 0
    for optionText in options:
        if counter >= page * 26 and counter < (page + 1) * 26:
            text = '(' + chr(letterIndex) + ') ' + optionText
            letterIndex += 1
            window.draw_str(0, y, text, bg=None)
            y += 1
        counter += 1
        
    x = MID_WIDTH - int(width/2)
    y = MID_HEIGHT - int(height/2)
    root.blit(window, x, y, width, height, 0, 0)

    tdl.flush()

def menu(header, options, width):
    global menuWindows, FOV_recompute
    page = 0
    maxPages = len(options)//26
    if maxPages <= 1:
        pagesDisp = False
    headerWrapped = textwrap.wrap(header, width)
    headerHeight = len(headerWrapped)
    if header == "":
        headerHeight = 0
    if len(options) > 26:
        height = 26 + headerHeight + 2
    else:
        height = len(options) + headerHeight + 2
    if menuWindows:
        for mWindow in menuWindows:
            mWindow.clear()
        FOV_recompute = True
        Update()
        tdl.flush()
    window = tdl.Console(width, height)
    menuWindows.append(window)
    window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)
    y = headerHeight + 2
    drawMenuOptions(y, options, window, page, width, height, headerWrapped, maxPages, pagesDisp)

    choseOrQuit = False
    while not choseOrQuit:
        choseOrQuit = True
        arrow = False
        drawMenuOptions(y, options, window, page, width, height, headerWrapped, maxPages, pagesDisp)
        key = tdl.event.key_wait()
        keyChar = key.keychar
        if keyChar == '':
            keyChar = ' '
        elif keyChar == 'RIGHT':
            page += 1
            choseOrQuit = False
            arrow = True
        elif keyChar == 'LEFT':
            page -= 1
            choseOrQuit = False
            arrow = True
        if page > maxPages:
            page = 0
        if page < 0:
            page = maxPages
        
        if not arrow:
            if keyChar in 'abcdefghijklmnopqrstuvwsyz':
                index = ord(keyChar) - ord('a')
                if index >= 0 and index < len(options):
                    return index + page * 26
            elif keyChar.upper() == "ESCAPE":
                return "cancelled"
    return None

def msgBox(text, width = 50):
    menu(text, [], width)

def drawCentered (cons = con , y = 1, text = "Lorem Ipsum", fg = None, bg = None):
    xCentered = (WIDTH - len(text))//2
    cons.draw_str(xCentered, y, text, fg, bg)

def drawCenteredOnX(cons = con, x = 1, y = 1, text = "Lorem Ipsum", fg = None, bg = None):
    centeredOnX = x - (len(text)//2)
    cons.draw_str(centeredOnX, y, text, fg, bg)
#_____________MENU_______________

#_____________SPELLS_____________
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

    def updateSpellStats(self):
        if self.name == 'Fireball':
            self.arg1 = FIREBALL_SPELL_BASE_RADIUS + player.Player.actualPerSkills[4]
            self.arg2 = FIREBALL_SPELL_BASE_DAMAGE * player.Player.actualPerSkills[4]
            self.arg3 = FIREBALL_SPELL_BASE_RANGE + player.Player.actualPerSkills[4] 

    def cast(self, caster = player, target = player):
        global FOV_recompute

        if caster == player:
            self.updateSpellStats()
        if self.ressource == 'MP' and caster.Fighter.MP < self.ressourceCost:
            FOV_recompute = True
            message(caster.name.capitalize() + ' does not have enough MP to cast ' + self.name +'.')
            return 'cancelled'

        if self.arg1 is None:
            if self.useFunction(caster, target) != 'cancelled':
                FOV_recompute = True
                caster.Fighter.knownSpells.remove(self)
                self.curCooldown = self.maxCooldown
                caster.Fighter.spellsOnCooldown.append(self)
                if self.ressource == 'MP':
                    caster.Fighter.MP -= self.ressourceCost
                elif self.ressource == 'HP':
                    caster.Fighter.takeDamage(self.ressourceCost)
                return 'used'
            else:
                return 'cancelled'
        elif self.arg2 is None and self.arg1 is not None:
            if self.useFunction(self.arg1, caster, target) != 'cancelled':
                FOV_recompute = True
                caster.Fighter.knownSpells.remove(self)
                self.curCooldown = self.maxCooldown
                caster.Fighter.spellsOnCooldown.append(self)
                if self.ressource == 'MP':
                    caster.Fighter.MP -= self.ressourceCost
                elif self.ressource == 'HP':
                    caster.Fighter.takeDamage(self.ressourceCost)
                return 'used'
            else:
                return 'cancelled'
        elif self.arg3 is None and self.arg2 is not None:
            if self.useFunction(self.arg1, self.arg2, caster, target) != 'cancelled':
                FOV_recompute = True
                caster.Fighter.knownSpells.remove(self)
                self.curCooldown = self.maxCooldown
                caster.Fighter.spellsOnCooldown.append(self)
                if self.ressource == 'MP':
                    caster.Fighter.MP -= self.ressourceCost
                elif self.ressource == 'HP':
                    caster.Fighter.takeDamage(self.ressourceCost)
                return 'used'
            else:
                return 'cancelled'
        elif self.arg3 is not None:
            if self.useFunction(self.arg1, self.arg2, self.arg3, caster, target) != 'cancelled':
                FOV_recompute = True
                caster.Fighter.knownSpells.remove(self)
                self.curCooldown = self.maxCooldown
                caster.Fighter.spellsOnCooldown.append(self)
                if self.ressource == 'MP':
                    caster.Fighter.MP -= self.ressourceCost
                elif self.ressource == 'HP':
                    caster.Fighter.takeDamage(self.ressourceCost)
                return 'used'
            else:
                return 'cancelled'

def learnSpell(spell):
    if spell not in player.Fighter.knownSpells:
        player.Fighter.knownSpells.append(spell)
        message("You learn " + spell.name + " !", colors.green)
    else:
        message("You already know this spell")
        return "cancelled"

def castRegenMana(regenAmount, caster = None, target = None):
    if caster is None:
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

def castDarkRitual(regen, damage, caster = player, target = None):
    message(caster.name.capitalize() + ' takes ' + str(damage) + ' damage from the ritual !', colors.red)
    castRegenMana(regen, caster)

def castHeal(healAmount = 10, caster = None, target = None):
    if caster is None:
        caster = player
    if caster.Fighter.hp == caster.Fighter.maxHP:
        message(caster.name.capitalize() + ' is already at full health')
        return 'cancelled'
    else:
        message(caster.name.capitalize() + ' is healed for {} HP !'.format(healAmount), colors.light_green)
        caster.Fighter.heal(healAmount)

def castLightning(caster = player, monsterTarget = player):
    if caster == player:
        target = closestMonster(LIGHTNING_RANGE)
    elif caster.distanceTo(monsterTarget) <= LIGHTNING_RANGE:
        target = monsterTarget
    if target is None:
        message(caster.name.capitalize() + "'s magic fizzles: there is no enemy near enough to strike", colors.red)
        return 'cancelled'
    message('A lightning bolt strikes the ' + target.name + ' with a heavy thunder ! It is shocked and suffers ' + str(LIGHTNING_DAMAGE) + ' shock damage.', colors.light_blue)
    target.Fighter.takeDamage(LIGHTNING_DAMAGE)

def castConfuse(caster = player, monsterTarget = None):
    message('Choose a target for your spell, press Escape to cancel.', colors.light_cyan)
    target = targetMonster(maxRange = CONFUSE_RANGE)
    if target is None:
        message('Invalid target.', colors.red)
        return 'cancelled'
    old_AI = target.AI
    target.AI = ConfusedMonster(old_AI)
    target.AI.owner = target
    message('The ' + target.name + ' starts wandering around as he seems to lose all bound with reality.', colors.light_violet)

def castFreeze(caster = player, monsterTarget = None):
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
    
def castFireball(radius = 3, damage = 24, range = 4, caster = player, monsterTarget = player):
    global explodingTiles
    if caster == player:
        message('Choose a target for your spell, press Escape to cancel.', colors.light_cyan)
        target = targetTile(maxRange = range)
    else:
        if caster.distanceTo(monsterTarget) <= range:
            target = (monsterTarget.x, monsterTarget.y)
        else:
            line = tdl.map.bresenham(caster.x, caster.y, monsterTarget.x, monsterTarget.y)
            counter = 0
            for tile in line:
                (tx, ty) = line[counter]
                if tileDistance(caster.x, caster.y, tx, ty) > range:
                    target = (tx, ty)
                    break
                else:
                    counter += 1
    #radmax = radius + 2
    if target == 'cancelled':
        message('Spell casting cancelled')
        return target
    else:
        (tx,ty) = target
        (targetX, targetY) = projectile(caster.x, caster.y, tx, ty, '*', colors.flame, passesThrough=True)
        #TODO : Make where the projectile lands actually matter (?)
        for obj in objects:
            if obj.distanceToCoords(targetX, targetY) <= radius and obj.Fighter:
                if obj != player:
                    message('The {} gets burned for {} damage !'.format(obj.name, damage), colors.light_blue)
                else:
                    message('You get burned for {} damage !'.format(damage), colors.orange)
                obj.Fighter.takeDamage(damage)
                applyBurn(obj)
        #for x in range(targetX - radmax, targetX + radmax):
            #for y in range(targetY - radmax, targetY + radmax):
                #if tileDistance(targetX, targetY, x, y) <= radius and not myMap[x][y].block_sight:
                    #explodingTiles.append((x,y))
        #explode()

def castArmageddon(radius = 4, damage = 80, caster = player, monsterTarget = None):
    global FOV_recompute
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
    for x in range (player.x - radmax, player.x + radmax):
        for y in range (player.y - radmax, player.y + radmax):
            try: #Execute code below try if no error is encountered
                if tileDistance(player.x, player.y, x, y) <= radius and not myMap[x][y].unbreakable:
                    gravelChoice = randint(0, 5)
                    myMap[x][y].blocked = False
                    myMap[x][y].block_sight = False
                    if gravelChoice == 0:
                        myMap[x][y].character = chr(177)
                    elif gravelChoice == 1:
                        myMap[x][y].character = chr(176)
                    else:
                        myMap[x][y].character = None
                    myMap[x][y].fg = color_light_gravel
                    myMap[x][y].bg = color_light_ground
                    myMap[x][y].dark_fg = color_dark_gravel
                    myMap[x][y].dark_bg = color_dark_ground
                    myMap[x][y].wall = False
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

def castEnrage(enrageTurns, caster = player, monsterTarget = None):
    player.Fighter.enraged = True
    player.Fighter.enrageCooldown = enrageTurns + 1
    player.Fighter.basePower += 10
    message('You are now enraged !', colors.dark_amber)

def castRessurect(range = 4, caster = player, monsterTarget = None):
    target = targetTile(range)
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
            global objects
            monster = None
            objects.remove(ressurectable)
            if corpseType == "darksoul":
                monster = createDarksoul(x, y, friendly = True, corpse = True)
            elif corpseType == "troll":
                monster = createTroll(x, y, friendly = True, corpse = True)
            if monster is not None:
                objects.append(monster)

fireball = Spell(ressourceCost = 7, cooldown = 5, useFunction = castFireball, name = "Fireball", ressource = 'MP', type = 'Magic', magicLevel = 1, arg1 = 1, arg2 = 12, arg3 = 4)
heal = Spell(ressourceCost = 15, cooldown = 12, useFunction = castHeal, name = 'Heal self', ressource = 'MP', type = 'Magic', magicLevel = 2, arg1 = 20)
darkPact = Spell(ressourceCost = DARK_PACT_DAMAGE, cooldown = 8, useFunction = castDarkRitual, name = "Dark ritual", ressource = 'HP', type = "Occult", magicLevel = 2, arg1 = 5, arg2 = DARK_PACT_DAMAGE)
enrage = Spell(ressourceCost = 5, cooldown = 30, useFunction = castEnrage, name = 'Enrage', ressource = 'MP', type = 'Strength', magicLevel = 0, arg1 = 5)
lightning = Spell(ressourceCost = 10, cooldown = 7, useFunction = castLightning, name = 'Lightning bolt', ressource = 'MP', type = 'Magic', magicLevel = 3)
confuse = Spell(ressourceCost = 5, cooldown = 4, useFunction = castConfuse, name = 'Confusion', ressource = 'MP', type = 'Magic', magicLevel = 1)
ice = Spell(ressourceCost = 9, cooldown = 5, useFunction = castFreeze, name = 'Ice bolt', ressource = 'MP', type = 'Magic', magicLevel = 2)
ressurect = Spell(ressourceCost = 10, cooldown = 15, useFunction=castRessurect, name = "Dark ressurection", ressource = 'MP', type = "Occult", arg1 = 4)
#_____________SPELLS_____________

#______________CHARACTER GENERATION____________
def initializeCharCreation():
    global power, accuracy, evasion, armor, maxHP, maxMP, critical, strength, dexterity, vitality, willpower, startingSpells, baseMaxLoad
    
    BASE_POWER = 0
    BASE_ACCURACY = 20
    BASE_EVASION = 0
    BASE_ARMOR = 0
    BASE_MAXHP = 0
    BASE_MAXMP = 0
    BASE_CRITICAL = 5
    BASE_STRENGTH = 0
    BASE_DEXTERITY = 0
    BASE_VITALITY = 0
    BASE_WILLPOWER = 0
    
    power = BASE_POWER
    accuracy = BASE_ACCURACY
    evasion = BASE_EVASION
    armor = BASE_ARMOR
    maxHP = BASE_MAXHP
    maxMP = BASE_MAXMP
    critical = BASE_CRITICAL
    
    strength = BASE_STRENGTH
    dexterity = BASE_DEXTERITY
    vitality = BASE_VITALITY
    willpower = BASE_WILLPOWER
    
    baseMaxLoad = 45.0

    startingSpells = []

def description(text):
    wrappedText = textwrap.wrap(text, 25)
    line = 0
    for lines in wrappedText:
        line += 1
        drawCentered(cons = root, y = 35 + line, text = lines, fg = colors.white, bg = None)

def applyBonus(list, chosenList):
    global power, accuracy, evasion, armor, maxHP, maxMP, critical, strength, dexterity, vitality, willpower
    power += list[chosenList][0]
    accuracy += list[chosenList][1]
    evasion += list[chosenList][2]
    armor += list[chosenList][3]
    maxHP += list[chosenList][4]
    maxMP += list[chosenList][5]
    critical += list[chosenList][6]
    strength += list[chosenList][7]
    dexterity += list[chosenList][8]
    vitality += list[chosenList][9]
    willpower += list[chosenList][10]

def removeBonus(list, chosenList):
    global power, accuracy, evasion, armor, maxHP, maxMP, critical, strength, dexterity, vitality, willpower
    power -= list[chosenList][0]
    accuracy -= list[chosenList][1]
    evasion -= list[chosenList][2]
    armor -= list[chosenList][3]
    maxHP -= list[chosenList][4]
    maxMP -= list[chosenList][5]
    critical -= list[chosenList][6]
    strength -= list[chosenList][7]
    dexterity -= list[chosenList][8]
    vitality -= list[chosenList][9]
    willpower -= list[chosenList][10]

#Bonus template: [power, accuracy, evasion, armor, maxHP, maxMP, critical, strength, dexterity, vitality, willpower]

def characterCreation():
    initializeCharCreation()
    baseMaxLoad = 45.0
    
    races = ['Human', 'Minotaur', 'Insectoid', 'Felis', 'Reptilian', 'Demon spawn', 'Rootling', 'Werewolf', 'Devourer', 'Virus ']
    racesDescription = ['Humans are the most common race. They have no special characteristic, and are neither better or worse at anything. However, they are good learners and gain experience faster.',
                        'Minotaurs, whose muscular bodies are topped with a taurine head, are tougher and stronger than humans, but are way less smart. They are uncontrollable and, when angered, can become a wrecking ball of muscles and thorns.',
                        'Insectoids are a rare race of bipedal insects which are stronger than human but, more importantly, very good at arcane arts. They come in all kinds of forms, from the slende mantis to the bulky beetle.',
                        'Felis, kinds of humanoid cats, are sneaky thieves and assassins. They usually move silently and can see in the dark.',
                        'Reptilians are very agile but absurdly weak. Their scaled skin, however, sometimes provides them with natural camouflage, and they might use their natural venom on their daggers or arrows to make them even more deadly.',
                        'Demon spawns, a very uncommon breed of a human and a demon, are cursed with the heritage of  their demonic parents, which will make them grow disturbing mutations as they grow older and stronger.',
                        'Rootlings, also called treants, are rare, sentient plants. They begin their life as a simple twig, but, with time, might become gigantic oaks.',
                        'Werewolves are a martyred and despised race. Very tough to kill, they are naturally stronger than basic humans and uncontrollably shapeshift more or less regularly. However, older werewolves are used to these transformations and can even use them to their interests.',
                        'Devourers are strange, dreaded creatures from another dimension. Few have arrived in ours and even fewer have been described. These animals, half mantis, half lizard, are only born to kill and consume. Some of their breeds can even, after consuming anything - even a weapon - grow an organic replica of it.',
                        'Viruses are the physically weakest race, but do not base their success on their own bodies. Indeed, they are able to infect another race, making it their host and fully controllable by the virus. What is more, the virus own physical attributes, instead of applying to it directly, rather modifies the host metabolism, potentially making it stronger or tougher. However, this take-over is very harmful for the host, who will eventually die. The virus must then find a new host to continue living.']
    racesBonus = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #Human
                  [0, 0, 0, 0, 0, 0, 0, 5, -4, 4, -3], #Minotaur
                  [0, 0, 0, 0, 0, 0, 0, 1, -1, -2, 2], #Insectoid
                  [0, 0, 0, 0, 0, 0, 0, 0, 2, 0, -2], #Felis
                  [0, 0, 10, 0, 0, 0, 0, -4, 2, 0, 0], #Reptilian
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #Demon Spawn
                  [0, 0, 0, 0, 0, 0, 0, -3, -2, -4, -3], #Rootling
                  [0, 0, 0, 0, 0, 0, 0, 2, 1, -2, -4], #Werewolf
                  [0, 0, 0, 0, 0, 0, 0, 1, 0, -2, -10], #Devourer
                  [0, 0, 999, 0, 0, 0, 0, -9, -9, -9, -9]] #Virus
    MAX_RACES = 1
    actualRaces = 0
    selectedRaces = [False, False, False, False, False, False, False, False, False, False]
    chosenRace = None
                    #after 10: 'Fast learner', 'Rage', 'Horned', 'Chitin carapace', 'Silent walk', 'Venomous glands', 'Mimesis', 'Wild instincts'
    selectableTraitsPerRaces = [[True, True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, False, False],
                                [True, True, True, True, True, True, True, True, True, True, False, True, True, False, False, False, False, False],
                                [True, True, True, True, True, True, True, True, True, True, False, False, False, True, False, False, False, False],
                                [True, True, True, True, True, True, True, True, True, True, False, False, False, False, True, False, False, False],
                                [True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, True, True, False],
                                [True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, False],
                                [True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, False],
                                [True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, True],
                                [True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, False],
                                [True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, False]]
    
    classes = ['Knight', 'Barbarian', 'Rogue', 'Mage ', 'Necromancer']
    classesDescription = ['A warrior who wears armor and yields shields',
                          'A brutal fighter who is mighty strong',
                          'A rogue who is stealthy and backstabby (probably has a french accent)',
                          'A wizard who zaps everything',
                          'A master of the occult arts who has the ability to raise and control the dead.']
    classesBonus = [[0, 0, 0, 1, 120, 30, 0, 0, 0, 0, 0], #Knight
                    [0, 0, 0, 0, 160, 30, 0, 1, 0, 0, 0], #Barbarian
                    [0, 8, 10, 0, 90, 40, 3, 0, 0, 0, 0], #Rogue
                    [0, 0, 0, 0, 70, 50, 0, 0, 0, 0, 2], #Mage
                    [0, 0, 0, 0, 100, 15, 0, 0, 0, 0, 0]] #Necromancer
    classesLevelUp = [[0, 0, 0, 1, 14, 3, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 20, 3, 0, 1, 0, 0, 0],
                      [0, 2, 1, 0, 10, 5, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 6, 7, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 4, 1, 0, 0, 0, 0, 0]]
    MAX_CLASSES = 1
    actualClasses = 0
    selectedClasses = [False, False, False, False, False]
    levelUpStats = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    classesSpells = [[], [enrage], [], [fireball], [darkPact, ressurect]]
    chosenClass = None

    attributes = ['Strength', 'Dexterity', 'Constitution', 'Willpower']
    attributesDescription = ['Strength augments the power of your attacks',
                             'Dexterity augments your accuracy and your evasion',
                             'Constitution augments your maximum health',
                             'Willpower augments your energy']
    attributesBonus = [[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0], #strength
                       [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0], #dex
                       [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], #vitality
                       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]] #willpower
    MAX_ATTRIBUTES_POINTS = 10
    MAX_PER_ATTRIBUTES = 5
    actualAttributesPoints = 0
    actualPerAttributes = [0, 0, 0, 0]
    selectedAttributes = [False, False, False, False]
    
    traits = ['Aggressive', 'Aura', 'Evasive', 'Healthy', 'Muscular', 'Natural armor', 'Strong mind', 'Agile', 'Martial training', 'Tough',
              'Fast learner', 'Rage', 'Horned', 'Chitin carapace', 'Silent walk', 'Venomous glands', 'Mimesis', 'Wild instincts']
    traitsDescription = ['Your anger is uncontrollable',
                         'You are surrounded by a potent aura',
                         'You are aware of how to stay out of trouble',
                         'You are healthy',
                         'You are very strong',
                         'Your skin is rock-hard',
                         'Your mind is fast and potent',
                         'You have incredible reflexes',
                         'You are trained to master all weapons',
                         'You can endure harm better',
                         'You are very smart and learn from your wins or losses very fast',
                         'When low on health, you will lose all control',
                         'Your horns are very large and can be used in combats',
                         'Your natural exoskeleton is very resistant',
                         'Your paws are very soft, allowing you to be very sneaky',
                         'You are able to envenom your weapons',
                         'You can mimic your environment, making it very hard to see you',
                         'Your natural transformation is even more deadly']
    traitsBonus= [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0],
                  [0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0],
                  [0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0],
                  [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                  [0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0],
                  [0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 40, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],]
    MAX_TRAITS = 2
    actualTraits = 0
    selectedTraits = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
    selectableTraits = [True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, False]
    
    skills = ['Light weapons', 'Heavy weapons', 'Missile weapons', 'Throwing weapons', 'Magic ', 'Armor wielding', 'Athletics', 'Concentration', 'Dodge ', 'Critical ', 'Accuracy']
    skillsDescription = ['+20% damage per skillpoints with light weapons',
                         '+20% damage per skillpoints with heavy weapons',
                         '+20% damage per skillpoints with missile weapons',
                         '+20% damage per skillpoints with throwing weapons',
                         'Magic ',
                         'Armor wielding',
                         '+20 HP and maximum HP per skillpoints',
                         '+20 MP and maximum MP per skillpoints',
                         '+3 evasion per skillpoints',
                         '+3 critical chance par skillpoints ',
                         '+10 accuracy per skillpoints']
    skillsBonus = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #light
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #heavy
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #missile
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #throwing
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #magic
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #armor
                   [0, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0], #athletics
                   [0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0], #concentration
                   [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0], #dodge
                   [0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0], #crit
                   [0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0]] #accuracy
    MAX_SKILLS = 2
    MAX_PER_SKILLS = 1
    actualSkills = 0
    actualPerSkills = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    selectedSkills = [False, False, False, False, False, False, False, False, False, False, False]
    
    #index
    index = 0
    leftIndexMin = 0
    leftIndexMax = leftIndexMin + len(attributes) + len(traits) + len(races) - 1
    rightIndexMin = leftIndexMax + 1
    rightIndexMax = rightIndexMin + len(skills) + len(classes) - 1
    maxIndex = len(races) + len(classes) + len(attributes) + len(traits) + len(skills) + 1
    
    while not tdl.event.isWindowClosed():
        root.clear()
        drawCentered(cons = root, y = 6, text = '--- CHARACTER CREATION ---', fg = colors.darker_red, bg = None)
        
        # Race, attributes and traits
        leftX = (WIDTH // 4)
        
        drawCenteredOnX(cons = root, x = leftX, y = 9, text = '-- RACE --', fg = colors.darker_red, bg = None)
        for choice in range(len(races)):
            if selectedRaces[choice]:
                drawCenteredOnX(cons = root, x = leftX, y = 11 + choice, text = races[choice], fg = colors.yellow, bg = None)
            else:
                drawCenteredOnX(cons = root, x = leftX, y = 11 + choice, text = races[choice], fg = colors.white, bg = None)
        
        drawCenteredOnX(cons = root, x = leftX, y = 33, text = '-- ATTRIBUTES --', fg = colors.darker_red, bg = None)
        drawCenteredOnX(cons = root, x = leftX, y = 34, text = str(actualAttributesPoints) + '/' + str(MAX_ATTRIBUTES_POINTS), fg = colors.dark_red, bg = None)
        totalAttributes = [strength, dexterity, vitality, willpower]
        for choice in range(len(attributes)):
            if selectedAttributes[choice]:
                drawCenteredOnX(cons = root, x = leftX, y = 36 + choice, text = attributes[choice], fg = colors.yellow, bg = None)
            else:
                drawCenteredOnX(cons = root, x = leftX, y = 36 + choice, text = attributes[choice], fg = colors.white, bg = None)
            drawCenteredOnX(cons = root, x = leftX - 10, y = 36 + choice, text = str(10 + totalAttributes[choice]), fg = colors.white, bg = None)

        drawCenteredOnX(cons = root, x = leftX, y = 45, text = '-- TRAITS --', fg = colors.darker_red, bg = None)
        drawCenteredOnX(cons = root, x = leftX, y = 46, text = str(actualTraits) + '/' + str(MAX_TRAITS), fg = colors.dark_red, bg = None)
        for choice in range(len(traits)):
            if selectedTraits[choice]:
                drawCenteredOnX(cons = root, x = leftX, y = 48 + choice, text = traits[choice], fg = colors.yellow, bg = None)
            elif not selectableTraits[choice]:
                drawCenteredOnX(cons = root, x = leftX, y = 48 + choice, text = traits[choice], fg = colors.grey, bg = None)
            else:
                drawCenteredOnX(cons = root, x = leftX, y = 48 + choice, text = traits[choice], fg = colors.white, bg = None)
        
        # Classes and skills
        rightX = WIDTH - (WIDTH // 4)
        
        drawCenteredOnX(cons = root, x = rightX, y = 9, text = '-- CLASS --', fg = colors.darker_red, bg = None)
        for choice in range(len(classes)):
            if selectedClasses[choice]:
                drawCenteredOnX(cons = root, x = rightX, y = 11 + choice, text = classes[choice], fg = colors.yellow, bg = None)
            else:
                drawCenteredOnX(cons = root, x = rightX, y = 11 + choice, text = classes[choice], fg = colors.white, bg = None)
        
        drawCenteredOnX(cons = root, x = rightX, y = 33, text = '-- SKILLS --', fg = colors.darker_red, bg = None)
        drawCenteredOnX(cons = root, x = rightX, y = 34, text = str(actualSkills) + '/' + str(MAX_SKILLS), fg = colors.dark_red, bg = None)
        for choice in range(len(skills)):
            if selectedSkills[choice]:
                drawCenteredOnX(cons = root, x = rightX, y = 36 + choice, text = skills[choice], fg = colors.yellow, bg = None)
            else:
                drawCenteredOnX(cons = root, x = rightX, y = 36 + choice, text = skills[choice], fg = colors.white, bg = None)
        
        drawCentered(cons = root, y = 33, text = '-- DESCRIPTION --', fg = colors.darker_red, bg = None)
        drawCentered(cons = root, y = 90, text = 'Start Game', fg = colors.white, bg = None)
        drawCentered(cons = root, y = 91, text = 'Cancel', fg = colors.white, bg = None)

        #Displaying stats
        eightScreen = WIDTH//5
        
        text = 'Power: ' + str(power + strength)
        drawCenteredOnX(cons = root, x = eightScreen * 1, y = 82, text = text, fg = colors.white, bg = None)
        X = eightScreen * 1 + ((len(text) + 1)// 2)
        root.draw_str(x = X, y = 82, string = ' + ' + str(levelUpStats[0] + levelUpStats[7]) + '/lvl', fg = colors.yellow, bg = None)
        
        text = 'Accuracy: ' + str(accuracy + 2 * dexterity)
        drawCenteredOnX(cons = root, x = eightScreen * 2, y = 82, text = text, fg = colors.white, bg = None)
        X = eightScreen * 2 + ((len(text) + 1)// 2)
        root.draw_str(x = X, y = 82, string = ' + ' + str(levelUpStats[1] + 2 * levelUpStats[8]) + '/lvl', fg = colors.yellow, bg = None)
        
        text = 'Evasion: ' + str(evasion + dexterity)
        drawCenteredOnX(cons = root, x = eightScreen * 3, y = 82, text = text, fg = colors.white, bg = None)
        X = eightScreen * 3 + ((len(text) + 1)// 2)
        root.draw_str(x = X, y = 82, string = ' + ' + str(levelUpStats[2] + levelUpStats[8]) + '/lvl', fg = colors.yellow, bg = None)
        
        text = 'Armor: ' + str(armor)
        drawCenteredOnX(cons = root, x = eightScreen * 4, y = 82, text = text, fg = colors.white, bg = None)
        X = eightScreen * 4 + ((len(text) + 1)// 2)
        root.draw_str(x = X, y = 82, string = ' + ' + str(levelUpStats[3]) + '/lvl', fg = colors.yellow, bg = None)
        
        text = 'Max HP: ' + str(maxHP + 5 * vitality)
        drawCenteredOnX(cons = root, x = eightScreen * 1, y = 84, text = text, fg = colors.white, bg = None)
        X = eightScreen * 1 + ((len(text) + 1)// 2)
        root.draw_str(x = X, y = 84, string = ' + ' + str(levelUpStats[4] + 5 * levelUpStats[9]) + '/lvl', fg = colors.yellow, bg = None)
        
        text = 'Max MP: ' + str(maxMP + 5 * willpower)
        drawCenteredOnX(cons = root, x = eightScreen * 2, y = 84, text = text, fg = colors.white, bg = None)
        X = eightScreen * 2 + ((len(text) + 1)// 2)
        root.draw_str(x = X, y = 84, string = ' + ' + str(levelUpStats[5] + 5 * levelUpStats[10]) + '/lvl', fg = colors.yellow, bg = None)
        
        text = 'Critical: ' + str(critical) + '%'
        drawCenteredOnX(cons = root, x = eightScreen * 3, y = 84, text = text, fg = colors.white, bg = None)
        X = eightScreen * 3 + ((len(text) + 1)// 2)
        root.draw_str(x = X, y = 84, string = ' + ' + str(levelUpStats[6]) + '/lvl', fg = colors.yellow, bg = None)
        
        text = 'Max load: ' + str(baseMaxLoad + 3 * strength) + ' kg'
        drawCenteredOnX(cons = root, x = eightScreen * 4, y = 84, text = text, fg = colors.white, bg = None)
        X = eightScreen * 4 + ((len(text) + 1)// 2)
        root.draw_str(x = X, y = 84, string = ' + ' + str(3 * levelUpStats[7]) + '/lvl', fg = colors.yellow, bg = None)
        
        # Selection
        if leftIndexMin <= index <= leftIndexMax:
            if index + 1 <= len(races):
                previousListLen = 0
                drawCenteredOnX(cons = root, x = leftX, y = 11 + index, text = races[index - previousListLen], fg = colors.black, bg = colors.white)
                description(racesDescription[index - previousListLen])
            elif index + 1 <= len(races) + len(attributes):
                previousListLen = len(races)
                drawCenteredOnX(cons = root, x = leftX, y = 36 - previousListLen + index, text = attributes[index - previousListLen], fg = colors.black, bg = colors.white)
                description(attributesDescription[index - previousListLen])
            else:
                previousListLen = len(races) + len(attributes)
                if selectableTraits[index - previousListLen]:
                    drawCenteredOnX(cons = root, x = leftX, y = 48 - previousListLen + index, text = traits[index - previousListLen], fg = colors.black, bg = colors.white)
                else:
                    drawCenteredOnX(cons = root, x = leftX, y = 48 - previousListLen + index, text = traits[index - previousListLen], fg = colors.black, bg = colors.grey)
                description(traitsDescription[index - previousListLen])

        if rightIndexMin <= index <= rightIndexMax:
            if index + 1 <= len(races) + len(attributes) + len(traits) + len(classes):
                previousListLen = len(races) + len(attributes) + len(traits)
                drawCenteredOnX(cons = root, x = rightX, y = 11 - previousListLen + index, text = classes[index - previousListLen], fg = colors.black, bg = colors.white)
                description(classesDescription[index - previousListLen])
            else:
                previousListLen = len(races) + len(classes) + len(attributes) + len(traits)
                drawCenteredOnX(cons = root, x = rightX, y = 36 - previousListLen + index, text = skills[index - previousListLen], fg = colors.black, bg = colors.white)
                description(skillsDescription[index - previousListLen])
        if index == maxIndex - 1:
            drawCentered(cons = root, y = 90, text = 'Start Game', fg = colors.black, bg = colors.white)
        if index == maxIndex:
            drawCentered(cons = root, y = 91, text = 'Cancel', fg = colors.black, bg = colors.white)

        tdl.flush()

        key = tdl.event.key_wait()
        if key.keychar.upper() == 'DOWN':
            index += 1
            playWavSound('select.wav', True)
        if key.keychar.upper() == 'UP':
            index -= 1
            playWavSound('select.wav', True)
        if key.keychar.upper() == 'RIGHT' and (leftIndexMin <= index <= leftIndexMax):
            if (leftIndexMin <= index <= leftIndexMax):
                if rightIndexMin <= index + len(attributes) + len(traits) + len(races) <= rightIndexMax:
                    index += len(attributes) + len(traits) + len(races)
                else:
                    index = rightIndexMax
                playWavSound('select.wav', True)
            else:
                playWavSound('error.wav', True)
        if key.keychar.upper() == 'LEFT':
            if (rightIndexMin <= index <= rightIndexMax):
                if leftIndexMin <= index - (len(attributes) + len(traits) + len(races)) <= leftIndexMax:
                    index -= (len(attributes) + len(traits) + len(races))
                else:
                    index = leftIndexMax
                playWavSound('select.wav', True)
            else:
                playWavSound('error.wav', True)

        #adding choice bonus
        if key.keychar.upper() == 'ENTER':
            if leftIndexMin <= index <= leftIndexMax:
                if index + 1 <= len(races):
                    if actualRaces < MAX_RACES:
                        previousListLen = 0
                        selectedRaces[index] = True
                        applyBonus(racesBonus, index)
                        actualRaces += 1
                        chosenRace = races[index]
                        selectableTraits = selectableTraitsPerRaces[index]
                        if selectedRaces[4]:
                            baseMaxLoad = 60.0
                elif index + 1 <= len(races) + len(attributes):
                    if actualAttributesPoints < MAX_ATTRIBUTES_POINTS:
                        previousListLen = len(races)
                        if actualPerAttributes[index - previousListLen] < MAX_PER_ATTRIBUTES:
                            applyBonus(attributesBonus, index - previousListLen)
                            selectedAttributes[index - previousListLen] = True
                            actualAttributesPoints += 1
                            actualPerAttributes[index - previousListLen] +=1
                else:
                    if actualTraits < MAX_TRAITS:
                        previousListLen = len(races) + len(attributes)
                        if not selectedTraits[index - previousListLen] and selectableTraits[index - previousListLen]:
                            selectedTraits[index - previousListLen] = True
                            applyBonus(traitsBonus, index - previousListLen)
                            actualTraits += 1

            if rightIndexMin <= index <= rightIndexMax:
                if index + 1 <= len(races) + len(attributes) + len(traits) + len(classes):
                    if actualClasses < MAX_CLASSES:
                        previousListLen = len(races) + len(attributes) + len(traits)
                        selectedClasses[index - previousListLen] = True
                        applyBonus(classesBonus, index - previousListLen)
                        levelUpStats = classesLevelUp[index - previousListLen]
                        actualClasses += 1
                        startingSpells = classesSpells[index - previousListLen]
                        chosenClass = classes[index - previousListLen]
                else:
                    if actualSkills < MAX_SKILLS:
                        previousListLen = len(races) + len(classes) + len(attributes) + len(traits)
                        if actualPerSkills[index - previousListLen] < MAX_PER_SKILLS:
                            applyBonus(skillsBonus, index - previousListLen)
                            selectedSkills[index - previousListLen] = True
                            actualSkills += 1
                            actualPerSkills[index - previousListLen] += 1

            if index == maxIndex - 1:
                if actualClasses > 0 and actualRaces > 0:
                    createdCharacter = [power, accuracy, evasion, armor, maxHP, maxMP, critical, strength, dexterity, vitality, willpower]
                    return createdCharacter, levelUpStats, actualPerSkills, skillsBonus, startingSpells, chosenRace, chosenClass, selectedTraits
            if index == maxIndex:
                return 'cancelled', 'cancelled', 'cancelled', 'cancelled', 'cancelled', 'cancelled', 'cancelled', 'cancelled'
        #removing choice bonus
        if key.keychar.upper() == 'BACKSPACE':
            if leftIndexMin <= index <= leftIndexMax:
                if index + 1 <= len(races):
                    if actualRaces > 0:
                        previousListLen = 0
                        if selectedRaces[index - previousListLen]:
                            if selectedRaces[4]:
                                baseMaxLoad = 45.0
                            selectedRaces[index - previousListLen] = False
                            removeBonus(racesBonus, index)
                            actualRaces -= 1
                            selectableTraits = [True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, False]
                            traitIndex = 0
                            for trait in selectedTraits:
                                if trait and not selectableTraits[traitIndex]:
                                    selectedTraits[traitIndex] = False
                                    removeBonus(traitsBonus, traitIndex)
                                    actualTraits -= 1
                                traitIndex += 1
                elif index + 1 <= len(races) + len(attributes):
                    if actualAttributesPoints > 0:
                        previousListLen = len(races)
                        if actualPerAttributes[index - previousListLen] > 0:
                            removeBonus(attributesBonus, index - previousListLen)
                            actualAttributesPoints -= 1
                            actualPerAttributes[index - previousListLen] -=1
                            if actualPerAttributes[index - previousListLen] == 0:
                                selectedAttributes[index - previousListLen] = False
                else:
                    if actualTraits > 0:
                        previousListLen = len(races) + len(attributes)
                        if selectedTraits[index - previousListLen]:
                            selectedTraits[index - previousListLen] = False
                            removeBonus(traitsBonus, index - previousListLen)
                            actualTraits -= 1
            if rightIndexMin <= index <= rightIndexMax:
                if index + 1 <= len(races) + len(attributes) + len(traits) + len(classes):
                    if actualClasses > 0:
                        previousListLen = len(races) + len(attributes) + len(traits)
                        if selectedClasses[index-previousListLen]:
                            selectedClasses[index - previousListLen] = False
                            removeBonus(classesBonus, index - previousListLen)
                            levelUpStats = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                            actualClasses -= 1
                            startingSpells = []
                else:
                    if actualSkills > 0:
                        previousListLen = len(races) + len(classes) + len(attributes) + len(traits)
                        if actualPerSkills[index - previousListLen] > 0:
                            removeBonus(skillsBonus, index - previousListLen)
                            selectedSkills[index - previousListLen] = False
                            actualSkills -= 1
                            actualPerSkills[index - previousListLen] -= 1
        if index > maxIndex:
            index = 0
        if index < 0:
            index = maxIndex
    
def enterName(race):
    letters = []
    while not tdl.event.isWindowClosed():
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
        if key.keychar.upper()== 'ENTER':
            if name == '':
                name = nameGen.humanLike(randint(5,8))
            return name.capitalize()
        elif key.keychar in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if len(name) < 16:
                letters.append(key.keychar)
            else:
                playWavSound('error.wav', forceStop = True)
        elif key.keychar.upper() == 'BACKSPACE':
            letters.pop()
        elif key.keychar.upper() == 'ESCAPE':
            mainMenu()
#______________CHARACTER GENERATION____________

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
    def __init__(self, x, y, char, name, color = colors.white, blocks = False, Fighter = None, AI = None, Player = None, Ghost = False, Item = None, alwaysVisible = False, darkColor = None, Equipment = None, pName = None):
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
        self.astarPath = []
        self.lastTargetX = None
        self.lastTargetY = None
        self.pluralName = pName

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
            #self.moveNextStepOnPath()
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
            self.moveNextStepOnPath()  
                
        elif fallback:
            self.moveTowards(destX, destY)
            if DEBUG:
                print(self.name + " found no Astar path")
        else:
            return "fail"

class Fighter: #All NPCs, enemies and the player
    def __init__(self, hp, armor, power, accuracy, evasion, xp, deathFunction=None, maxMP = 0, knownSpells = None, critical = 5, lootFunction = None, lootRate = 0, shootCooldown = 0, landCooldown = 0, transferDamage = None):
        self.baseMaxHP = hp
        self.BASE_MAX_HP = hp
        self.hp = hp
        self.baseArmor = armor
        self.BASE_ARMOR = armor
        self.basePower = power
        self.BASE_POWER = power
        self.deathFunction = deathFunction
        self.xp = xp
        self.baseAccuracy = accuracy
        self.BASE_ACCURACY = accuracy
        self.baseEvasion = evasion
        self.BASE_EVASION = evasion
        self.baseCritical = critical
        self.lootFunction = lootFunction
        self.lootRate = lootRate 
        
        self.frozen = False
        self.freezeCooldown = 0
        
        self.burning = False
        self.burnCooldown = 0
        
        self.enraged = False
        self.enrageCooldown = 0
        
        self.healCountdown = 25
        self.MPRegenCountdown = 10

        self.baseShootCooldown = shootCooldown
        self.curShootCooldown = 0
        self.baseLandCooldown = landCooldown
        self.curLandCooldown = 0
        
        self.acidified = False
        self.acidifiedCooldown = 0
        
        self.baseMaxMP = maxMP
        self.MP = maxMP
        self.BASE_MAX_MP = maxMP
        
        self.damageText = 'unscathed'
        
        if knownSpells != None:
            self.knownSpells = knownSpells
        else:
            self.knownSpells = []
        
        self.spellsOnCooldown = []
        
        self.transferDamage = transferDamage

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
            self.updateDamageText()
        if self.hp <= 0:
            death=self.deathFunction
            if death is not None:
                death(self.owner)
            if self.owner != player and (not self.owner.AI or self.owner.AI.__class__.__name__ != "FriendlyMonster"):
                if player.Player.race == 'Human':
                    xp = int((self.xp * 10) / 100) + self.xp
                else:
                    xp = self.xp
                player.Fighter.xp += xp

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
                if self.owner.Player and self.owner.Player.traits[0]:
                    damage = (randint(self.power - 2, self.power + 2) + 4  - target.Fighter.armor) * 3
                else:
                    damage = (randint(self.power - 2, self.power + 2) - target.Fighter.armor) * 3
            else:
                if self.owner.Player and self.owner.Player.traits[0]:
                    damage = randint(self.power - 2, self.power + 2) + 4 - target.Fighter.armor
                else:
                    damage = randint(self.power - 2, self.power + 2) - target.Fighter.armor
            if not self.frozen:
                if not self.owner.Player:
                    if damage > 0:
                        if target == player:
                            if criticalHit:
                                message(self.owner.name.capitalize() + ' critically hits you for ' + str(damage) + ' hit points!', colors.dark_orange)
                            else:
                                message(self.owner.name.capitalize() + ' attacks you for ' + str(damage) + ' hit points.', colors.orange)
                        elif self.owner.AI and self.owner.AI.__class__.__name__ == "FriendlyMonster" and self.owner.AI.friendlyTowards == player:
                            if criticalHit:
                                message('Your fellow ' + self.owner.name + ' critically hits '+ target.name +' for ' + str(damage) + ' hit points!', colors.darker_green)
                            else:
                                message('Your fellow ' + self.owner.name + ' attacks '+ target.name + ' for ' + str(damage) + ' hit points.', colors.dark_green)
                        else:
                            if criticalHit:
                                message(self.owner.name.capitalize() + ' critically hits '+ target.name +' for ' + str(damage) + ' hit points!')
                            else:
                                message(self.owner.name.capitalize() + ' attacks '+ target.name + ' for ' + str(damage) + ' hit points.')
                        target.Fighter.takeDamage(damage)
                    else:
                        if target == player:
                            message(self.owner.name.capitalize() + ' attacks you but it has no effect !')
                else:
                    if damage > 0:
                        if criticalHit:
                            message('You critically hit ' + target.name + ' for ' + str(damage) + ' hit points!', colors.darker_green)
                        else:
                            message('You attack ' + target.name + ' for ' + str(damage) + ' hit points.', colors.dark_green)
                        target.Fighter.takeDamage(damage)
                        weapons = getEquippedInHands()
                        if weapons:
                            for weapon in weapons:
                                if weapon is not None:
                                    if weapon.Equipment.burning:
                                        applyBurn(target, chance = 25)
                    
                    else:
                        message('You attack ' + target.name + ' but it has no effect!', colors.grey)
        else:
            if not self.owner.Player:
                if target == player:
                    message(self.owner.name.capitalize() + ' missed you!', colors.white)
                else:
                    message(self.owner.name.capitalize() + ' missed ' + target.name + '.')
            else:
                message('You missed ' + target.name + '!', colors.grey)
        
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

class BasicMonster: #Basic monsters' AI
    def takeTurn(self):
        monster = self.owner
        targets = []
        selectedTarget = None
        priorityTargetFound = False
        monsterVisibleTiles = tdl.map.quick_fov(x = monster.x, y = monster.y,callback = isVisibleTile , fov = FOV_ALGO, radius = SIGHT_RADIUS, lightWalls = FOV_LIGHT_WALLS)
        if not self.owner.Fighter.frozen and monster.distanceTo(player) <= 15:
            print(monster.name + " is less than 15 tiles to player.")
            for object in objects:
                if (object.x, object.y) in monsterVisibleTiles and (object == player or (object.AI and object.AI.__class__.__name__ == "FriendlyMonster" and object.AI.friendlyTowards == player)):
                    targets.append(object)
            if DEBUG:
                print(monster.name.capitalize() + " can target", end=" ")
                if targets:
                    for loop in range (len(targets)):
                        print(targets[loop].name.capitalize() + ", ", sep ="", end ="")
                else:
                    print("absolutely nothing but nothingness.", end ="")
                print()
            if targets:
                if player in targets: #Target player in priority
                    selectedTarget = player
                    del targets[targets.index(player)]
                    if monster.distanceTo(player) < 2:
                        priorityTargetFound = True
                if not priorityTargetFound:
                    for enemyIndex in range(len(targets)):
                        enemy = targets[enemyIndex]
                        if monster.distanceTo(enemy) < 2:
                            selectedTarget = enemy
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
            #elif (monster.x, monster.y) in visibleTiles and monster.distanceTo(player) >= 2:
                #monster.moveAstar(player.x, player.y)
            else:
                if not monster.Fighter.frozen and monster.distanceTo(player) >= 2:
                    pathState = "complete"
                    diagPathState = None
                    if monster.astarPath:
                        pathState = monster.moveNextStepOnPath()
                    elif not monster.astarPath or pathState == "fail":
                            if monster.distanceTo(player) <= 15 and not (monster.x == player.x and monster.y == player.y):
                                diagPathState = checkDiagonals(monster, player)
                            elif diagPathState is None or monster.distanceTo(player) > 15:
                                monster.move(randint(-1, 1), randint(-1, 1)) #wandering

class FastMonster:
    def __init__(self, speed):
        self.speed = speed
    
    def takeTurn(self):
        monster = self.owner
        for loop in range(self.speed):
            targets = []
            selectedTarget = None
            priorityTargetFound = False
            monsterVisibleTiles = tdl.map.quick_fov(x = monster.x, y = monster.y,callback = isVisibleTile , fov = FOV_ALGO, radius = SIGHT_RADIUS, lightWalls = FOV_LIGHT_WALLS)
            if not self.owner.Fighter.frozen and monster.distanceTo(player) <= 15:
                print(monster.name + " is less than 15 tiles to player.")
                for object in objects:
                    if (object.x, object.y) in monsterVisibleTiles and (object == player or (object.AI and object.AI.__class__.__name__ == "FriendlyMonster" and object.AI.friendlyTowards == player)):
                        targets.append(object)
                if DEBUG:
                    print(monster.name.capitalize() + " can target", end=" ")
                    if targets:
                        for loop in range (len(targets)):
                            print(targets[loop].name.capitalize() + ", ", sep ="", end ="")
                    else:
                        print("absolutely nothing but nothingness.", end ="")
                    print()
                if targets:
                    if player in targets: #Target player in priority
                        selectedTarget = player
                        del targets[targets.index(player)]
                        if monster.distanceTo(player) < 2:
                            priorityTargetFound = True
                    if not priorityTargetFound:
                        for enemyIndex in range(len(targets)):
                            enemy = targets[enemyIndex]
                            if monster.distanceTo(enemy) < 2:
                                selectedTarget = enemy
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
                #elif (monster.x, monster.y) in visibleTiles and monster.distanceTo(player) >= 2:
                    #monster.moveAstar(player.x, player.y)
                else:
                    if not monster.Fighter.frozen and monster.distanceTo(player) >= 2:
                        pathState = "complete"
                        diagPathState = None
                        if monster.astarPath:
                            pathState = monster.moveNextStepOnPath()
                        elif not monster.astarPath or pathState == "fail":
                                if monster.distanceTo(player) <= 15 and not (monster.x == player.x and monster.y == player.y):
                                    diagPathState = checkDiagonals(monster, player)
                                elif diagPathState is None or monster.distanceTo(player) > 15:
                                    monster.move(randint(-1, 1), randint(-1, 1)) #wandering

class Fleeing:
    def takeTurn(self):
        monster = self.owner
        monsterVisibleTiles = tdl.map.quick_fov(x = monster.x, y = monster.y,callback = isVisibleTile , fov = FOV_ALGO, radius = SIGHT_RADIUS, lightWalls = FOV_LIGHT_WALLS)
        bestX = 0
        bestY = 0
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if (x, y) in monsterVisibleTiles and monster.distanceToCoords(x, y) > monster.distanceToCoords(bestX, bestY) and not isBlocked(x, y):
                    bestX = x
                    bestY = y
        state = monster.moveAstar(bestX, bestY, fallback = False)
        if state == "fail":
            monster.moveTowards(bestX, bestY)

class hostileStationnary:
    def takeTurn(self):
        monster = self.owner
        targets = []
        selectedTarget = None
        priorityTargetFound = False
        if not self.owner.Fighter.frozen:
            for object in objects:
                if (object.x, object.y) in visibleTiles and (object == player or (object.AI and object.AI.__class__.__name__ == "FriendlyMonster" and object.AI.friendlyTowards == player)):
                    targets.append(object)
            if DEBUG:
                print(monster.name.capitalize() + " can target", end=" ")
                if targets:
                    for loop in range (len(targets)):
                        print(targets[loop].name.capitalize() + ", ", sep ="", end ="")
                else:
                    print("absolutely nothing but nothingness.", end ="")
                print()
            if targets:
                if player in targets: #Target player in priority
                    selectedTarget = player
                    del targets[targets.index(player)]
                    if monster.distanceTo(player) < 2:
                        priorityTargetFound = True
                if not priorityTargetFound:
                    for enemyIndex in range(len(targets)):
                        enemy = targets[enemyIndex]
                        if monster.distanceTo(enemy) < 2:
                            selectedTarget = enemy
                        else:
                            if selectedTarget == None or monster.distanceTo(selectedTarget) > monster.distanceTo(enemy):
                                selectedTarget = enemy
            if selectedTarget is not None:
                if monster.distanceTo(selectedTarget) < 2:
                    monster.Fighter.attack(selectedTarget)

class immobile():
    def takeTurn(self):
        monster = self.owner
        return

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
        if self.old_AI.__class__.__name__ != 'hostileStationnary' and self.old_AI.__class__.__name__ != 'immobile':
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
        if self.friendlyTowards == player and not self.owner.Fighter.frozen: #If the monster is friendly towards the player
            for object in objects:
                if (object.x, object.y) in monsterVisibleTiles and object.AI and object.AI.__class__.__name__ != "FriendlyMonster" and object.Fighter and object.Fighter.hp > 0:
                    targets.append(object)
            if DEBUG:
                print(monster.name.capitalize() + " can target", end=" ")
                if targets:
                    for loop in range (len(targets)):
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
                if not monster.Fighter.frozen and monster.distanceTo(player) >= 2:
                    if (player.x, player.y) in monsterVisibleTiles:
                        pathState = monster.moveAstar(player.x, player.y, fallback = False)
                        diagPathState = None
                        if pathState == "fail" or not monster.astarPath:
                                if monster.distanceTo(player) <= 15 and not (monster.x == player.x and monster.y == player.y):
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
    
class Spellcaster():
    def takeTurn(self):
        global FOV_recompute
        monster = self.owner
        monsterVisibleTiles = tdl.map.quick_fov(x = monster.x, y = monster.y,callback = isVisibleTile , fov = FOV_ALGO, radius = SIGHT_RADIUS, lightWalls = FOV_LIGHT_WALLS)
        
        targets = []
        selectedTarget = None
        priorityTargetFound = False
        if not self.owner.Fighter.frozen and monster.distanceTo(player) <= 15:
            print(monster.name + " is less than 15 tiles to player.")
            for object in objects:
                if (object.x, object.y) in monsterVisibleTiles and (object == player or (object.AI and object.AI.__class__.__name__ == "FriendlyMonster" and object.AI.friendlyTowards == player)):
                    targets.append(object)
            if DEBUG:
                print(monster.name.capitalize() + " can target", end=" ")
                if targets:
                    for loop in range (len(targets)):
                        print(targets[loop].name.capitalize() + ", ", sep ="", end ="")
                else:
                    print("absolutely nothing but nothingness.", end ="")
                print()
            if targets:
                if player in targets: #Target player in priority
                    selectedTarget = player
                    del targets[targets.index(player)]
                    if monster.distanceTo(player) < 2:
                        priorityTargetFound = True
                if not priorityTargetFound:
                    for enemyIndex in range(len(targets)):
                        enemy = targets[enemyIndex]
                        if monster.distanceTo(enemy) < 2:
                            selectedTarget = enemy
                        else:
                            if selectedTarget == None or monster.distanceTo(selectedTarget) > monster.distanceTo(enemy):
                                selectedTarget = enemy
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
                            break
                else:
                    choseSpell = False
                
                if not choseSpell:
                    if monster.distanceTo(selectedTarget) < 2:
                        monster.Fighter.attack(selectedTarget)
                    else:
                        state = monster.moveAstar(selectedTarget.x, selectedTarget.y, fallback = False)
                        if state == "fail":
                            diagState = checkDiagonals(monster, selectedTarget)
                            if diagState is None:
                                monster.moveTowards(selectedTarget.x, selectedTarget.y)
            #elif (monster.x, monster.y) in visibleTiles and monster.distanceTo(player) >= 2:
                #monster.moveAstar(player.x, player.y)
            else:
                if not monster.Fighter.frozen and monster.distanceTo(player) >= 2:
                    pathState = "complete"
                    diagPathState = None
                    if monster.astarPath:
                        pathState = monster.moveNextStepOnPath()
                    elif not monster.astarPath or pathState == "fail":
                            if monster.distanceTo(player) <= 15 and not (monster.x == player.x and monster.y == player.y):
                                diagPathState = checkDiagonals(monster, player)
                            elif diagPathState is None or monster.distanceTo(player) > 15:
                                monster.move(randint(-1, 1), randint(-1, 1)) #wandering
            FOV_recompute = True

class Player:
    def __init__(self, name, strength, dexterity, vitality, willpower, actualPerSkills, levelUpStats, skillsBonus, race, classes, traits, baseHunger = BASE_HUNGER):
        self.name = name
        self.strength = strength
        self.dexterity = dexterity
        self.vitality = vitality
        self.willpower = willpower
        self.baseMaxWeight = 45.0
        self.maxWeight = self.baseMaxWeight
        self.actualPerSkills = actualPerSkills
        self.levelUpStats = levelUpStats
        self.skillsBonus = skillsBonus
        self.race = race
        self.classes = classes
        self.traits = traits
        self.burdened = False
        self.hunger = baseHunger
        self.hungerStatus = "full"
        self.dualWield = False
        
        if self.race == 'Werewolf':
            self.transformCooldown = 150
            self.transformCurCooldown = self.transformCooldown
            self.transformed = False
            self.transformMaxTurns = 20
            self.transformationTime = 0
        
        if self.race == 'Virus ':
            self.HOST_DEATH = 1500
            self.hostDeath = 0
            self.inHost = False
            self.timeOutsideLeft = 50
        
        if self.race == 'Demon spawn':
            self.possibleMutations = {'extra limb': 100}
            self.mutationsGotten = []
            self.mutationLevel = [2]
        
        if DEBUG:
            print('Player component initialized')
        
    def changeColor(self):
        self.hpRatio = ((self.owner.Fighter.hp / self.owner.Fighter.maxHP) * 100)
        if self.hpRatio == 100:
            self.owner.color = (0, 210, 0)
        elif self.hpRatio < 95 and self.hpRatio >= 75:
            self.owner.color = (120, 255, 0)
        elif self.hpRatio < 75 and self.hpRatio >= 50:
            self.owner.color = (255, 255, 0)
        elif self.hpRatio < 50 and self.hpRatio >= 25:
            self.owner.color = (255, 120, 0)
        elif self.hpRatio < 25 and self.hpRatio > 0:
            self.owner.color = (255, 0, 0)
        elif self.hpRatio == 0:
            self.owner.color = (120, 0, 0)
    
    def bonusPlayerStats(self):
        #[power, accuracy, evasion, armor, maxHP, maxMP, critical]
        power = self.strength
        accuracy = 2 * self.dexterity
        evasion = self.dexterity
        maxHP = 5 * self.vitality
        maxMP = 5 * self.willpower
        return power, accuracy, evasion, maxHP, maxMP

    def updatePlayerStats(self):
        power, accuracy, evasion, maxHP, maxMP = self.bonusPlayerStats()
        object = self.owner
        object.Fighter.basePower = object.Fighter.BASE_POWER + power
        object.Fighter.baseAccuracy = object.Fighter.BASE_ACCURACY + accuracy
        object.Fighter.baseEvasion = object.Fighter.BASE_EVASION + evasion
        self.maxWeight = self.baseMaxWeight + 3 * power
        
        hpDiff = object.Fighter.baseMaxHP - object.Fighter.hp
        mpDiff = object.Fighter.baseMaxMP - object.Fighter.MP
        
        object.Fighter.baseMaxHP = object.Fighter.BASE_MAX_HP + maxHP
        object.Fighter.hp = object.Fighter.baseMaxHP - hpDiff
        object.Fighter.baseMaxMP = object.Fighter.BASE_MAX_MP + maxMP
        object.Fighter.MP = object.Fighter.baseMaxMP - mpDiff
    
    def takeControl(self, target):
        player.Fighter.hp = target.Fighter.hp
        player.Fighter.armor = target.Fighter.armor
        player.Fighter.power = target.Fighter.power
        player.Fighter.accuracy = target.Fighter.accuracy
        player.Fighter.evasion = target.Fighter.evasion
        player.Fighter.maxMP = target.Fighter.maxMP
        player.Fighter.critical = target.Fighter.critical
        
        player.x, player.y = target.x, target.y
        message('You take control of ' + target.name + '!', colors.darker_han)
        objects.remove(target)
        self.inHost = True
        self.hostDeath = self.HOST_DEATH

class Item:
    def __init__(self, useFunction = None,  arg1 = None, arg2 = None, arg3 = None, stackable = False, amount = 1, weight = 0, description = 'Placeholder.', pic = 'trollMace.xp'):
        self.useFunction = useFunction
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.stackable = stackable
        self.amount = amount
        self.weight = weight
        self.description = description
        self.pic = pic

    def pickUp(self):
        if not self.stackable:
            #if len(inventory)>=26:
                #message('Your bag already feels really heavy, you cannot pick up ' + self.owner.name + '.', colors.red)
            #else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', colors.green)
            equipment = self.owner.Equipment
            if equipment:
                handed = equipment.slot == 'one handed' or equipment.slot == 'two handed'
                if not handed and getEquippedInSlot(equipment.slot) is None:
                    equipment.equip()
        else:
            itemFound = False
            for item in inventory:
                if item.name == self.owner.name:
                    if self.amount == 1:
                        message('You picked up a' + ' ' + self.owner.name + ' !', colors.green)
                    elif self.owner.pluralName is None:
                        message('You picked up ' + str(self.amount) + ' ' + self.owner.name + 's !', colors.green)
                    else:
                        message('You picked up ' + str(self.amount) + ' ' + self.owner.pluralName + ' !', colors.green)
                    item.Item.amount += self.amount
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
                objects.remove(self.owner)
                if self.amount == 1:
                    message('You picked up a' + ' ' + self.owner.name + ' !', colors.green)
                elif self.owner.pluralName is None:
                    message('You picked up ' + str(self.amount) + ' ' + self.owner.name + 's !', colors.green)
                else:
                    message('You picked up ' + str(self.amount) + ' ' + self.owner.pluralName + ' !', colors.green)

    def use(self):
        if self.owner.Equipment:
            self.owner.Equipment.toggleEquip()
            return
        if self.useFunction is None:
            message('The ' + self.owner.name + ' cannot be used !')
            return 'cancelled'
        else:
            if self.arg1 is None:
                if self.useFunction() != 'cancelled':
                    if not self.stackable or self.amount == 0:
                        inventory.remove(self.owner)
                    else:
                        self.amount -= 1
                        if self.amount < 0:
                            self.amount = 0
                        if self.amount == 0:
                            inventory.remove(self.owner)
                        
                else:
                    return 'cancelled'
            elif self.arg2 is None and self.arg1 is not None:
                if self.useFunction(self.arg1) != 'cancelled':
                    if not self.stackable or self.amount == 0:
                        inventory.remove(self.owner)
                    else:
                        self.amount -= 1
                        if self.amount < 0:
                            self.amount = 0
                        if self.amount == 0:
                            inventory.remove(self.owner)
                else:
                    return 'cancelled'
            elif self.arg3 is None and self.arg2 is not None:
                if self.useFunction(self.arg1, self.arg2) != 'cancelled':
                    if not self.stackable or self.amount == 0:
                        inventory.remove(self.owner)
                    else:
                        self.amount -= 1
                        if self.amount < 0:
                            self.amount = 0
                        if self.amount == 0:
                            inventory.remove(self.owner)
                else:
                    return 'cancelled'
            elif self.arg3 is not None:
                if self.useFunction(self.arg1, self.arg2, self.arg3) != 'cancelled':
                    if not self.stackable or self.amount == 0:
                        inventory.remove(self.owner)
                    else:
                        self.amount -= 1
                        if self.amount < 0:
                            self.amount = 0
                        if self.amount == 0:
                            inventory.remove(self.owner)
                else:
                    return 'cancelled'
                
    def drop(self):
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        if self.stackable:
            message('You dropped ' + str(self.amount) + ' ' + self.owner.pluralName + '.', colors.yellow)
        else:
            message('You dropped a ' + self.owner.name + '.', colors.yellow)
        if self.owner.Equipment:
            self.owner.Equipment.unequip()
    
    def fullDescription(self, width):
        equipmentComp = self.owner.Equipment
        fullDesc = []
        equipmentStats = []
        fullDesc.extend(textwrap.wrap(self.description, width))
        if equipmentComp is not None:
            if equipmentComp.slot is not None:
                equipmentStats.append(equipmentComp.slot.capitalize())
            if equipmentComp.type is not None:
                equipmentStats.append(equipmentComp.type.capitalize())
            if equipmentComp.powerBonus != 0:
                equipmentStats.append('Power Bonus: ' + str(equipmentComp.powerBonus))
            if equipmentComp.armorBonus != 0:
                equipmentStats.append('Armor Bonus: ' + str(equipmentComp.armorBonus))
            if equipmentComp.maxHP_Bonus != 0:
                equipmentStats.append('HP Bonus: ' + str(equipmentComp.maxHP_Bonus))
            if equipmentComp.maxMP_Bonus != 0:
                equipmentStats.append('MP Bonus: ' + str(equipmentComp.maxMP_Bonus))
            if equipmentComp.accuracyBonus != 0:
                equipmentStats.append('Accuracy Bonus: ' + str(equipmentComp.accuracyBonus))
            if equipmentComp.evasionBonus != 0:
                equipmentStats.append('Evasion Bonus: ' + str(equipmentComp.evasionBonus))
            if equipmentComp.criticalBonus != 0:
                equipmentStats.append('Critical Bonus: ' + str(equipmentComp.criticalBonus))
            if equipmentComp.ranged:
                equipmentStats.append('Ranged damage: ' + str(equipmentComp.rangedPower))
        weightText = 'Weight: ' + str(self.weight)
        fullDesc.append(weightText)
        fullDesc.extend(equipmentStats)
        return fullDesc
    
    def display(self, options):
        global menuWindows, FOV_recompute
        asciiFile = os.path.join(absAsciiPath, self.pic)
        xpRawString = gzip.open(asciiFile, "r").read()
        convertedString = xpRawString
        attributes = xpL.load_xp_string(convertedString)
        picWidth = int(attributes["width"])
        picHeight = int(attributes["height"])
        print("Pic Height = ", picHeight)
        lData = attributes["layer_data"]
        
        width = picWidth + 16
        desc = self.fullDescription(width)
        descriptionHeight = len(desc)
        if desc == '':
            descriptionHeight = 0
        height = descriptionHeight + len(options) + 6 + int(picHeight) + 1
        if menuWindows:
            for mWindow in menuWindows:
                mWindow.clear()
                FOV_recompute = True
                Update()
                tdl.flush()
        window = tdl.Console(width, height)
        window.clear()
        
        choseOrQuit = False
        while not choseOrQuit:
            choseOrQuit = True
            
            startY = 3
            startX = 2
            layerInd = int(0)
            for layerInd in range(len(lData)):
                xpL.load_layer_to_console(window, lData[layerInd], startY, startX)
            #for line in self.pic:
                #x = 2
                #for char in line:
                    #window.draw_char(x, y, char[0], char[1], char[2])
                    #x += 1
                #y += 1
            
            
            window.draw_str(0, 0, self.owner.name.capitalize() + ':', fg = colors.yellow, bg = None)
            for i, line in enumerate(desc):
                window.draw_str(0, int(picHeight) + 4 +i, desc[i], fg = colors.white)

            y = descriptionHeight + picHeight + 5
            letterIndex = ord('a')
            counter = 0
            for optionText in options:
                text = '(' + chr(letterIndex) + ') ' + optionText
                letterIndex += 1
                window.draw_str(0, y, text, bg=None)
                y += 1
                counter += 1
                
            x = MID_WIDTH - int(width/2)
            y = MID_HEIGHT - int(height/2)
            root.blit(window, x, y, width, height, 0, 0)
        
            tdl.flush()
            
            key = tdl.event.key_wait()
            keyChar = key.keychar
            if keyChar in 'abcdefghijklmnopqrstuvwsyz':
                index = ord(keyChar) - ord('a')
                if index >= 0 and index < len(options):
                    return index
            elif keyChar.upper() == "ESCAPE":
                return "cancelled"
        return None


def quitGame(message, backToMainMenu = False):
    global objects
    global inventory
    if gameState != "dead":
        saveGame()
    for obj in objects:
        del obj
    inventory = []
    if backToMainMenu:
        mainMenu()
    else:
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
        castCreateDarksoul()
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == 'F5' and DEBUG and not tdl.event.isWindowClosed(): #Don't know if tdl.event.isWindowClosed() is necessary here but added it just to be sure
        player.Player.vitality += 1000
        player.Player.updatePlayerStats()
        player.Fighter.hp = player.Fighter.maxHP
        message('Healed player and increased their maximum HP value by 1000', colors.purple)
        FOV_recompute = True
    elif userInput.keychar.upper() == "F6" and DEBUG and not tdl.event.isWindowClosed():
        player.Fighter.xp += 1000
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
    elif userInput.keychar.upper() == 'F10' and DEBUG and not tdl.event.isWindowClosed(): #For some reason, Bad Things (tm) happen if you don't perform a tdl.event.isWindowClosed() check here. Yeah, don't ask why.
        castCreateDarksoul(friendly = True)
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == 'F11' and DEBUG and not tdl.event.isWindowClosed(): #For some reason, Bad Things (tm) happen if you don't perform a tdl.event.isWindowClosed() check here. Yeah, don't ask why.
        learnSpell(ressurect)
        FOV_recompute = True
        return 'didnt-take-turn'
    elif userInput.keychar.upper() == 'F12' and DEBUG and not tdl.event.isWindowClosed():
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                try:
                    if not myMap[x][y].block_sight: #DO NOT REMOVE THIS CHECK. Unless you'd like to see what would happen if the game was running on an actual toaster.
                        myMap[x][y].explored = True
                except:
                    pass
        FOV_recompute = True
    elif userInput.keychar == 'B' and DEBUG and not tdl.event.isWindowClosed():
        castPlaceBoss()
        FOV_recompute = True
    elif userInput.keychar == 'S' and DEBUG and not tdl.event.isWindowClosed():
        message("Force-saved level {}", colors.purple)
        saveLevel(dungeonLevel)
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
        
        width = CHARACTER_SCREEN_WIDTH
        height = CHARACTER_SCREEN_HEIGHT
        window = tdl.Console(width, height)
        window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)
        window.clear()

        while not tdl.event.isWindowClosed():
            window.draw_str(5, 1, player.Player.race + ' ' + player.Player.classes, fg = colors.yellow)
            renderBar(window, 1, 3, BAR_WIDTH, 'EXP', player.Fighter.xp, levelUp_xp, colors.desaturated_cyan, colors.dark_gray)
            renderBar(window, 1, 5, BAR_WIDTH, 'Hunger', player.Player.hunger, BASE_HUNGER, colors.desaturated_lime, colors.dark_gray)
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

            x = MID_WIDTH - int(width/2)
            y = MID_HEIGHT - int(height/2)
            root.blit(window, x, y, width, height, 0, 0)
            tdl.flush()
            
            key = tdl.event.key_wait()
            keyChar = key.keychar
            
            if keyChar == 'ESCAPE':
                break
        
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
            if chosenSpell.magicLevel > player.Player.actualPerSkills[4]:
                FOV_recompute = True
                message('Your arcane knowledge is not high enough to cast ' + chosenSpell.name + '.')
                return 'didnt-take-turn'
            else:
                action = chosenSpell.cast(caster = player)
                if action == 'cancelled':
                    FOV_recompute = True
                    return 'didnt-take-turn'
                else:
                    return
    elif userInput.keychar.upper() == 'X':
        shooting = shoot()
        if shooting == 'didnt-take-turn':
            return 'didnt-take-turn'
        else:
            return

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
                saveLevel(dungeonLevel)
                for object in objects:    
                    if upStairs.x == player.x and upStairs.y == player.y:
                        if stairCooldown == 0:
                            global stairCooldown, dungeonLevel
                            saveLevel(dungeonLevel)
                            stairCooldown = 2
                            if DEBUG:
                                message("Stair cooldown set to {}".format(stairCooldown), colors.purple)
                            toLoad = dungeonLevel - 1
                            loadLevel(toLoad, save = False)
                        else:
                            message("You're too tired to climb the stairs right now")
                        return None
            FOV_recompute = True
        elif userInput.keychar.upper() == '>':
            for object in objects:
                if stairs.x == player.x and stairs.y == player.y:
                    if stairCooldown == 0:
                        global stairCooldown
                        stairCooldown = 2
                        boss = False
                        if dungeonLevel >= 2:
                            boss = True
                        if DEBUG:
                            message("Stair cooldown set to {}".format(stairCooldown), colors.purple)
                        nextLevel(boss)
                    else:
                        message("You're too tired to climb down the stairs right now")
                elif object == gluttonyStairs and object.x == player.x and object.y == player.y:
                    if stairCooldown == 0:
                        global stairCooldown
                        stairCooldown = 2
                        boss = False
                        if DEBUG:
                            message("Stair cooldown set to {}".format(stairCooldown), colors.purple)
                        nextLevel(boss, changeBranch = dBr.gluttonyDungeon)
                    else:
                        message("You're too tired to climb down the stairs right now")
                    return None
        elif userInput.keychar.upper() == 'I':
            choseOrQuit = False
            while not choseOrQuit:
                chosenItem = inventoryMenu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosenItem is not None:
                    choseOrQuit = True
                    usage = chosenItem.display(['Use', 'Drop', 'Back'])
                    if usage == 0:
                        using = chosenItem.use()
                        if using == 'cancelled':
                            FOV_recompute = True
                            return 'didnt-take-turn'
                    elif usage == 1:
                        chosenItem.drop()
                        return None
                    elif usage == 2:
                        choseOrQuit = False
                else:
                    return 'didnt-take-turn'
        elif userInput.keychar.upper() == 'E':
            choseOrQuit = False
            while not choseOrQuit:
                choseOrQuit = True
                chosenItem = equipmentMenu('This is the equipment you are currently wielding.')
                if chosenItem is not None:
                    usage = chosenItem.display(['Unequip', 'Drop', 'Back'])
                    if usage == 0:
                        using = chosenItem.use()
                        if using == 'cancelled':
                            FOV_recompute = True
                            return 'didnt-take-turn'
                    elif usage == 1:
                        chosenItem.owner.Equipment.unequip()
                        chosenItem.drop()
                        return None
                    elif usage == 2:
                        choseOrQuit = False
                else:
                    FOV_recompute = True
                    return 'didnt-take-turn'
        else:
            FOV_recompute = True
            return 'didnt-take-turn'
    FOV_recompute = True

def projectile(sourceX, sourceY, destX, destY, char, color, continues = False, passesThrough = False, ghost = False):
    line = tdl.map.bresenham(sourceX, sourceY, destX, destY)
    (firstX, firstY)= line[1]
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
    for loop in range(len(line)):
        (x, y) = line.pop(0)
        proj.x, proj.y = x, y
        animStep(.050)
        if isBlocked(x, y) and (not passesThrough or myMap[x][y].blocked) and not ghost:
            objects.remove(proj)
            return (x,y)
            break
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
                (x, y) = line.pop(0)
                proj.x, proj.y = x, y
                animStep(.050)
                if isBlocked(x, y):
                    objects.remove(proj)
                    return (x,y)
                    break
            dx = newX - startX
            dy = newY - startY
        print("Projectile out of range")
        #message("Your arrow flies far away from your sight.")
        return (None, None)
        
def satiateHunger(amount, name = None):
    player.Player.hunger += amount
    if player.Player.hunger > BASE_HUNGER:
        player.Player.hunger = BASE_HUNGER
    if name:
        message("You eat " + name +".")

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

def moveOrAttack(dx, dy):
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
                player.Fighter.attack(target)
            else:
                player.Player.takeControl(target)
        else:
            player.Fighter.attack(target)
    else:
        if not player.Player.burdened:
            player.move(dx, dy)

def shoot():
    global FOV_recompute
    weapons = getEquippedInHands()
    if weapons is not None:
        for weapon in weapons:
            if weapon.Equipment.ranged:
                if weapon.Equipment.ammo is not None:
                    ammo = weapon.Equipment.ammo
                    for object in inventory:
                        foundAmmo = False
                        if object.name == ammo:
                            message('Choose a target for your ' + weapon.name + '.', colors.cyan)
                            aimedTile = targetTile(weapon.Equipment.maxRange, showBresenham=True)
                            if aimedTile == "cancelled":
                                FOV_recompute = True
                                message('Invalid target.')
                                return 'didnt-take-turn'
                            else:
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
                                        [hit, criticalHit] = player.Fighter.toHit(monsterTarget)
                                        if hit:
                                            if player.Player.traits[0]:
                                                damage = randint(weapon.Equipment.rangedPower - 2, weapon.Equipment.rangedPower + 2) + 4 - monsterTarget.Fighter.armor
                                            else:
                                                damage = randint(weapon.Equipment.rangedPower - 2, weapon.Equipment.rangedPower + 2) - monsterTarget.Fighter.armor
        
                                            if damage <= 0:
                                                message('You hit ' + monsterTarget.name + ' but it has no effect !')
                                            else:
                                                if criticalHit:
                                                    damage = damage * 3
                                                    message('You critically hit ' + monsterTarget.name + ' for ' + str(damage) + ' damage !', colors.darker_green)
                                                else:
                                                    message('You hit ' + monsterTarget.name + ' for ' + str(damage) + ' damage !', colors.dark_green)
                                                monsterTarget.Fighter.takeDamage(damage)
                                        else:
                                            message('You missed ' + monsterTarget.name + '!', colors.grey)
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
                    target = targetMonster(weapon.Equipment.maxRange)
                    if target is None:
                        FOV_recompute = True
                        message('Invalid target.')
                        return 'didnt-take-turn'
                    else:
                        FOV_recompute = True
                        [hit, criticalHit] = player.Fighter.toHit(target)
                        if hit:
                            damage = weapon.Equipment.rangedPower - target.Fighter.armor
                            if damage <= 0:
                                message('You hit ' + target.name + ' but it has no effect !')
                            else:
                                if criticalHit:
                                    damage = damage * 3
                                    message('You critically hit ' + target.name + ' for ' + str(damage) + ' damage !', colors.darker_green)
                                else:
                                    message('You hit ' + target.name + ' for ' + str(damage) + ' damage !', colors.dark_green)
                                target.Fighter.takeDamage(damage)
                        else:
                            message('You missed ' + target.name + '!', colors.grey)
            else:
                FOV_recompute = True
                message('You have no ranged weapon equipped.')
                return 'didnt-take-turn'
    else:
        FOV_recompute = True
        message('You have no ranged weapon equipped.')
        return 'didnt-take-turn'

def checkLevelUp():
    global FOV_recompute
    
    levelUp_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    if player.Fighter.xp >= levelUp_xp:
        player.level += 1
        player.Fighter.xp -= levelUp_xp
        message('Your battle skills grow stronger! You reached level ' + str(player.level) + '!', colors.yellow)
        
        #applying Class specific stat boosts
        player.Fighter.basePower += player.Player.levelUpStats[0]
        player.Fighter.BASE_POWER += player.Player.levelUpStats[0]
        player.Fighter.baseAccuracy += player.Player.levelUpStats[1]
        player.Fighter.BASE_ACCURACY += player.Player.levelUpStats[1]
        player.Fighter.baseEvasion += player.Player.levelUpStats[2]
        player.Fighter.BASE_EVASION += player.Player.levelUpStats[2]
        player.Fighter.baseArmor += player.Player.levelUpStats[3]
        player.Fighter.BASE_ARMOR += player.Player.levelUpStats[3]
        player.Fighter.baseMaxHP += player.Player.levelUpStats[4]
        player.Fighter.hp += player.Player.levelUpStats[4]
        player.Fighter.BASE_MAX_HP += player.Player.levelUpStats[4]
        player.Fighter.baseMaxMP += player.Player.levelUpStats[5]
        player.Fighter.MP += player.Player.levelUpStats[5]
        player.Fighter.BASE_MAX_MP += player.Player.levelUpStats[5]
        player.Fighter.baseCritical += player.Player.levelUpStats[6]
        player.Player.strength += player.Player.levelUpStats[7]
        player.Player.dexterity += player.Player.levelUpStats[8]
        player.Player.vitality += player.Player.levelUpStats[9]
        player.Player.willpower += player.Player.levelUpStats[10]
        
        if player.Player.race == 'Demon spawn':
            if player.Player.possibleMutations and player.level in player.Player.mutationLevel:
                mutation = randomChoice(player.Player.possibleMutations)
                del player.Player.possibleMutations[mutation]
                player.Player.mutationsGotten.append(mutation)
                message('You feel strange... You feel like you now have a ' + mutation +'.', colors.yellow)
            else:
                mutation = randint(1, 4)
                if mutation == 1:
                    player.Player.strength += 1
                    mutationName = 'strength'
                elif mutation == 2:
                    player.Player.dexterity += 1
                    mutationName = 'dexterity'
                elif mutation == 1:
                    player.Player.vitality += 1
                    mutationName = 'vitality'
                else:
                    player.Player.willpower += 1
                    mutationName = 'willpower'
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
                    player.Fighter.baseMaxHP += hpBonus
                    player.Fighter.hp += hpBonus
                elif choice == 1:
                    player.Player.dexterity += randint(1, 2)
                    player.Player.strength += randint(1, 2)
                elif choice == 2:
                    player.Player.willpower += randint(1, 2)
                    mpBonus = randint(0, 10)
                    player.Fighter.BASE_MAX_MP += mpBonus
                    player.Fighter.baseMaxMP += mpBonus
                    player.Fighter.MP += mpBonus
            message('You feel your wooden corpse thickening!', colors.celadon)
        
        choice = None
        while choice == None:
            choice = menu('Level up! Choose a skill to raise: \n',
                ['Light Weapons (from ' + str(player.Player.actualPerSkills[0]) + ')',
                 'Heavy Weapons (from ' + str(player.Player.actualPerSkills[1]) + ')',
                 'Missile Weapons (from ' + str(player.Player.actualPerSkills[2]) + ')',
                 'Throwing Weapons (from ' + str(player.Player.actualPerSkills[3]) + ')',
                 'Magic (from ' + str(player.Player.actualPerSkills[4]) + ')',
                 'Armor wielding (from ' + str(player.Player.actualPerSkills[5]) + ')',
                 'Athletics (from ' + str(player.Player.actualPerSkills[6]) + ')',
                 'Concentration (from ' + str(player.Player.actualPerSkills[7]) + ')',
                 'Dodge (from ' + str(player.Player.actualPerSkills[8]) + ')',
                 'Critical (from ' + str(player.Player.actualPerSkills[9]) + ')',
                 'Accuracy (from ' + str(player.Player.actualPerSkills[10]) + ')',], LEVEL_SCREEN_WIDTH)
            if choice != None:
                if player.Player.actualPerSkills[choice] < 5:
                    player.Fighter.basePower += player.Player.skillsBonus[choice][0]
                    player.Fighter.BASE_POWER += player.Player.skillsBonus[choice][0]
                    player.Fighter.baseAccuracy += player.Player.skillsBonus[choice][1]
                    player.Fighter.BASE_ACCURACY += player.Player.skillsBonus[choice][1]
                    player.Fighter.baseEvasion += player.Player.skillsBonus[choice][2]
                    player.Fighter.BASE_EVASION += player.Player.skillsBonus[choice][2]
                    player.Fighter.baseArmor += player.Player.skillsBonus[choice][3]
                    player.Fighter.BASE_ARMOR += player.Player.skillsBonus[choice][3]
                    player.Fighter.baseMaxHP += player.Player.skillsBonus[choice][4]
                    player.Fighter.hp += player.Player.skillsBonus[choice][4]
                    player.Fighter.BASE_MAX_HP += player.Player.skillsBonus[choice][4]
                    player.Fighter.baseMaxMP += player.Player.skillsBonus[choice][5]
                    player.Fighter.MP += player.Player.skillsBonus[choice][5]
                    player.Fighter.BASE_MAX_MP += player.Player.skillsBonus[choice][5]
                    player.Fighter.baseCritical += player.Player.skillsBonus[choice][6]
                    player.Player.strength += player.Player.skillsBonus[choice][7]
                    player.Player.dexterity += player.Player.skillsBonus[choice][8]
                    player.Player.vitality += player.Player.skillsBonus[choice][9]
                    player.Player.willpower += player.Player.skillsBonus[choice][10]

                    player.Player.actualPerSkills[choice] += 1
                    FOV_recompute = True
                    Update()
                    break

                elif player.Player.actualPerSkills[choice] >= 5:
                    choice = None

        player.Player.updatePlayerStats()
        if player.Player.actualPerSkills[0] >= 4 and not player.Player.dualWield:
            message('You are now proficient enough with light weapons to wield two at the same time!', colors.yellow)
            player.Player.dualWield = True

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
            myMap[x][y].blocked = True
            myMap[x][y].block_sight = True

def castCreateChasm():
    target = targetTile()
    if target == 'cancelled':
        return target
    else:
        (x,y) = target
        if not isBlocked(x, y):
            global myMap
            myMap[x][y].blocked = True
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

def applyBurn(target, chance = 30):
    if target.Fighter and randint(0, 100) > chance and not target.Fighter.burning:
        if not target.Fighter.frozen:
            target.Fighter.burning = True
            target.Fighter.burnCooldown = 4
            message('The ' + target.name + ' is set afire') 
        else:
            target.Fighter.frozen = False
            target.Fighter.freezeCooldown = 0
            message('The ' + target.name + "'s ice melts away.")
    
def monsterArmageddon(monsterName ,monsterX, monsterY, radius = 4, damage = 40, selfHit = True):
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
                                    if selfHit:
                                        message('The explosion deals {} damage to {} !'.format(damage, obj.name))
                                    elif not (obj.x == monsterX and obj.y == monsterY):
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


def castCreateDarksoul(friendly = False):
    target = targetTile()
    if target == 'cancelled':
        return 'cancelled'
    else:
        (x,y) = target
        monster = createDarksoul(x, y, friendly = friendly)
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
    def __init__(self, blocked, block_sight = None, acid = False, acidCooldown = 5, character = None, fg = None, bg = None, dark_fg = None, dark_bg = None, wall = False):
        self.blocked = blocked
        self.explored = False
        self.unbreakable = False
        self.character = character
        self.fg = fg
        self.bg = bg
        self.dark_fg = dark_fg
        self.dark_bg = dark_bg
        self.wall = wall
        if block_sight is None:
            block_sight = blocked
            self.block_sight = block_sight
        else:
            self.block_sight = block_sight
        self.acid = acid
        self.baseAcidCooldown = acidCooldown
        self.curAcidCooldown = 0
        if self.wall:
            self.character = '#'
            self.fg = color_light_wall
            self.bg = color_light_ground
            self.dark_fg = color_dark_wall
            self.dark_bg = color_dark_ground

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
            gravelChoice = randint(0, 5)
            myMap[x][y].blocked = False
            myMap[x][y].block_sight = False
            if gravelChoice == 0:
                myMap[x][y].character = chr(177)
            elif gravelChoice == 1:
                myMap[x][y].character = chr(176)
            else:
                myMap[x][y].character = None
            myMap[x][y].fg = color_light_gravel
            myMap[x][y].bg = color_light_ground
            myMap[x][y].dark_fg = color_dark_gravel
            myMap[x][y].dark_bg = color_dark_ground
            myMap[x][y].wall = False
            
def createHorizontalTunnel(x1, x2, y):
    global myMap
    for x in range(min(x1, x2), max(x1, x2) + 1):
        gravelChoice = randint(0, 5)
        myMap[x][y].blocked = False
        myMap[x][y].block_sight = False
        if gravelChoice == 0:
            myMap[x][y].character = chr(177)
        elif gravelChoice == 1:
            myMap[x][y].character = chr(176)
        else:
            myMap[x][y].character = None
        myMap[x][y].fg = color_light_gravel
        myMap[x][y].bg = color_light_ground
        myMap[x][y].dark_fg = color_dark_gravel
        myMap[x][y].dark_bg = color_dark_ground
        myMap[x][y].wall = False
            
def createVerticalTunnel(y1, y2, x):
    global myMap
    for y in range(min(y1, y2), max(y1, y2) + 1):
        gravelChoice = randint(0, 5)
        myMap[x][y].blocked = False
        myMap[x][y].block_sight = False
        if gravelChoice == 0:
            myMap[x][y].character = chr(177)
        elif gravelChoice == 1:
            myMap[x][y].character = chr(176)
        else:
            myMap[x][y].character = None
        myMap[x][y].fg = color_light_gravel
        myMap[x][y].bg = color_light_ground
        myMap[x][y].dark_fg = color_dark_gravel
        myMap[x][y].dark_bg = color_dark_ground
        myMap[x][y].wall = False

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
        myMap[entryX][entryY].character = '#'
        myMap[entryX][entryY].fg = color_light_wall
        myMap[entryX][entryY].bg = color_light_ground
        myMap[entryX][entryY].dark_fg = color_dark_wall
        myMap[entryX][entryY].dark_bg = color_dark_ground
        gravelChoice = randint(0, 5)
        if gravelChoice == 0:
            myMap[entryX][entryY].character = chr(177)
        elif gravelChoice == 1:
            myMap[entryX][entryY].character = chr(176)
        else:
            myMap[entryX][entryY].character = None
        myMap[entryX][entryY].fg = color_light_gravel
        myMap[entryX][entryY].bg = color_light_ground
        myMap[entryX][entryY].dark_fg = color_dark_gravel
        myMap[entryX][entryY].dark_bg = color_dark_ground
        myMap[x][y].wall = False
        print("created secret room at x ", entryX, " y ", entryY, " in quarter ", quarter)

def makeMap():
    global myMap, stairs, objects, upStairs, bossDungeonsAppeared
    myMap = [[Tile(True, wall = True) for y in range(MAP_HEIGHT)]for x in range(MAP_WIDTH)] #Creates a rectangle of blocking tiles from the Tile class, aka walls. Each tile is accessed by myMap[x][y], where x and y are the coordinates of the tile.
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
                    upStairs = GameObject(new_x, new_y, '<', 'stairs', currentBranch.lightStairsColor, alwaysVisible = True, darkColor = currentBranch.darkStairsColor)
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
            if r == 0:
                placeObjects(newRoom, first = True)
            else:
                placeObjects(newRoom)
            rooms.append(newRoom)
            numberRooms += 1
    secretRoom()
    stairs = GameObject(new_x, new_y, '>', 'stairs', currentBranch.lightStairsColor, alwaysVisible = True, darkColor = currentBranch.darkStairsColor)
    objects.append(stairs)
    stairs.sendToBack()
    
    for (branch, level) in currentBranch.branchesTo:
        if branch == dBr.gluttonyDungeon:
            if dungeonLevel == level and not bossDungeonsAppeared['gluttony']:
                createdStairs = False
                while not createdStairs:
                    randRoom = randint(0, len(rooms) - 1)
                    room = rooms[randRoom]
                    (x, y) = room.center()
                    wrongCentre = False
                    for object in objects:
                        if object.x == x and object.y == y:
                            wrongCentre = True
                            break
                    if not wrongCentre:
                        global gluttonyStairs
                        gluttonyStairs = GameObject(x, y, '>', 'stairs to Gluttony', branch.lightStairsColor, alwaysVisible = True, darkColor = branch.darkStairsColor)
                        objects.append(gluttonyStairs)
                        gluttonyStairs.sendToBack()
                        bossDungeonsAppeared['gluttony'] = True
                        createdStairs = True
                        print('created gluttonys stairs at ' + str(x) + ', ' + str(y))

def makeBossLevel():
    global myMap, objects, upStairs, rooms, numberRooms
    myMap = [[Tile(True, wall = True) for y in range(MAP_HEIGHT)]for x in range(MAP_WIDTH)] #Creates a rectangle of blocking tiles from the Tile class, aka walls. Each tile is accessed by myMap[x][y], where x and y are the coordinates of the tile.
    objects = [player]
    rooms = []
    numberRooms = 0
    
    for y in range (MAP_HEIGHT):
        myMap[0][y].unbreakable = True
        myMap[MAP_WIDTH-1][y].unbreakable = True
    for x in range(MAP_WIDTH):
        myMap[x][0].unbreakable = True
        myMap[x][MAP_HEIGHT-1].unbreakable = True #Borders of the map cannot be broken
 
    for r in range(5): #first rooms
        w = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        x = randint(0, 50-w-1)
        y = randint(0, 20-h-1)
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
                    upStairs = GameObject(new_x, new_y, '<', 'stairs', currentBranch.lightStairsColor, alwaysVisible = True, darkColor = currentBranch.darkStairsColor)
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
            rooms.append(newRoom)
            numberRooms += 1

    #boss room
    w = randint(25, 40)
    h = randint(20, 35)
    x = randint(50, 100-w-1)
    y = randint(20, 60-h-1)
    bossRoom = Rectangle(x, y, w, h)
    createRoom(bossRoom)
    (new_x, new_y) = bossRoom.center()
    createVerticalTunnel(previous_y, new_y, previous_x)
    createHorizontalTunnel(previous_x, new_x, new_y)
    
    bossName = None
    if dungeonLevel >= 2:
        bossName = 'High Inquisitor'

    placeBoss(bossName, new_x, y + 1)
    
    (previous_x, previous_y) = bossRoom.center()
    rooms.append(bossRoom)
    numberRooms += 1

def createEndRooms():
    global rooms, stairs, myMap, objects, numberRooms
    for r in range(4): #final rooms
        w = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
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
    stairs = GameObject(new_x, new_y, '>', 'stairs', colors.white, alwaysVisible = True, darkColor = colors.dark_grey)
    objects.append(stairs)
    stairs.sendToBack()
    
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
                lootItem(item, monster.x, monster.y)
            itemIndex += 1

    monster.char = '%'
    monster.color = colors.dark_red
    monster.blocks = False
    monster.AI = None
    monster.name = 'remains of ' + monster.name
    monster.Fighter = None
    monster.sendToBack()
    createEndRooms()

#--Gluttony--
def fatDeath(monster):
    global deathX, deathY
    monster.char = '%'
    monster.color = colors.dark_red
    monster.name = 'some mangled fat'
    monster.blocks = False
    monster.AI = None
    monster.Fighter = None
    deathX = monster.x
    deathY = monster.y

def createFat(x, y):
    fatFighterComponent = Fighter(hp = 5, armor = 0, power = 1, xp = 0, deathFunction=fatDeath, accuracy= 0, evasion=1)
    fat_AI_component = immobile()
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
        
        if not boss.Fighter.frozen:
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
                                        fighter.Fighter.takeDamage(2)
                                        message(fighter.name + " is touched by the vomit  splatters and suffers 2 damage!", color = colors.orange)
                for fighter in objects:
                    if fighter.x == object.x and fighter.y == object.y:
                        if fighter.Fighter:
                            fighter.Fighter.takeDamage(15)
                            message(fighter.name + " is hit by Gluttony's vomit and suffers 10 damage!", color = colors.orange)
                objects.remove(object)
                FOV_recompute = True
                break

        for object in objects:
            if object.name == "Gluttony's fat" and object.distanceTo(player) < 2:
                player.Fighter.takeDamage(1)
                message('The massive chunks of flesh around you start crushing you slowly! You lose 1 hit point.', colors.dark_orange)
                break

def gluttonysDeath(monster):
    message(monster.name.capitalize() + ' is dead! You have slain a boss and gain ' + str(monster.Fighter.xp) + ' XP!', colors.dark_sky)

    monster.char = '%'
    monster.color = colors.dark_red
    monster.blocks = False
    monster.AI = None
    monster.name = 'remains of ' + monster.name
    monster.Fighter = None
    monster.sendToBack()
    for object in objects:
        if object.name == "Gluttony's fat": #or (object.AI and (object.AI.__class__.__name__ == "immobile")):
            object.Fighter.hp = 0
            fatDeath(object)
    createEndRooms()
#--Gluttony--

#--Wrath--   WIP
class Wrath():
    def __init__(self):
        self.chargeCooldown = 0
        self.curChargeCooldown = 0
        self.explodeCooldown = 0
        self.flurryCooldown = 0
        self.charging = False

    def takeTurn(self):
        boss = self.owner
        bossVisibleTiles = tdl.map.quickFOV(boss.x, boss.y, isVisibleTile, fov = BOSS_FOV_ALGO, radius = BOSS_SIGHT_RADIUS, lightWalls= False)
        
        if boss.distanceTo(player) < 2 and not self.charging:
            if self.flurryCooldown <= 0:
                message('Wrath unleashes a volley of slashes at you!', colors.dark_amber)
                numberHits = randint(2, 4)
                for loop in range(numberHits):
                    boss.Fighter.attack(player)
                    print("Wrath attacked")
                self.flurryCooldown = 21
        elif (player.x, player.y) in bossVisibleTiles and self.chargeCooldown <= 0 and not self.charging:
            chargePath = tdl.map.bresenham(boss.x, boss.y, player.x, player.y)
            for y in range(MAP_HEIGHT):
                for x in range(MAP_WIDTH):
                    if (x, y) in chargePath:
                        sign = GameObject(x, y, '.', 'chargePath', color = colors.red, Ghost = True)
                        objects.append(sign)
            self.charging = True
            self.chargeCooldown = 16
            self.curChargeCooldown = 2
        else:
            boss.moveAstar(player.x, player.y, fallback = False)
#--Wrath--

#-- High Inquisitor --
class HighInquisitor:
    def takeTurn(self):
        global FOV_recompute
        monster = self.owner
        monsterVisibleTiles = tdl.map.quick_fov(x = monster.x, y = monster.y,callback = isVisibleTile , fov = FOV_ALGO, radius = SIGHT_RADIUS, lightWalls = FOV_LIGHT_WALLS)
        
        targets = []
        selectedTarget = None
        priorityTargetFound = False
        if not self.owner.Fighter.frozen and monster.distanceTo(player) <= 15:
            print(monster.name + " is less than 15 tiles to player.")
            for object in objects:
                if (object.x, object.y) in monsterVisibleTiles and (object == player or (object.AI and object.AI.__class__.__name__ == "FriendlyMonster" and object.AI.friendlyTowards == player)):
                    targets.append(object)
            if DEBUG:
                print(monster.name.capitalize() + " can target", end=" ")
                if targets:
                    for loop in range (len(targets)):
                        print(targets[loop].name.capitalize() + ", ", sep ="", end ="")
                else:
                    print("absolutely nothing but nothingness.", end ="")
                print()
            if targets:
                if player in targets: #Target player in priority
                    selectedTarget = player
                    del targets[targets.index(player)]
                    if monster.distanceTo(player) < 2:
                        priorityTargetFound = True
                if not priorityTargetFound:
                    for enemyIndex in range(len(targets)):
                        enemy = targets[enemyIndex]
                        if monster.distanceTo(enemy) < 2:
                            selectedTarget = enemy
                        else:
                            if selectedTarget == None or monster.distanceTo(selectedTarget) > monster.distanceTo(enemy):
                                selectedTarget = enemy
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
                        monsterVisibleTiles = tdl.map.quick_fov(x = monster.x, y = monster.y,callback = isVisibleTile , fov = FOV_ALGO, radius = SIGHT_RADIUS, lightWalls = FOV_LIGHT_WALLS)
                        bestX = 0
                        bestY = 0
                        for x in range(MAP_WIDTH):
                            for y in range(MAP_HEIGHT):
                                if (x, y) in monsterVisibleTiles and monster.distanceToCoords(x, y) > monster.distanceToCoords(bestX, bestY) and not isBlocked(x, y):
                                    bestX = x
                                    bestY = y
                        state = monster.moveAstar(bestX, bestY, fallback = False)
                        if state == "fail":
                            print("astar failed")
                            monster.moveTowards(bestX, bestY)
                            #diagState = checkDiagonals(monster, selectedTarget)
                            #if diagState is None:
                            #    monster.moveTowards(selectedTarget.x, selectedTarget.y)
            #elif (monster.x, monster.y) in visibleTiles and monster.distanceTo(player) >= 2:
                #monster.moveAstar(player.x, player.y)
            else:
                if not monster.Fighter.frozen and monster.distanceTo(player) >= 2:
                    pathState = "complete"
                    diagPathState = None
                    if monster.astarPath:
                        pathState = monster.moveNextStepOnPath()
                    elif not monster.astarPath or pathState == "fail":
                            if monster.distanceTo(player) <= 15 and not (monster.x == player.x and monster.y == player.y):
                                diagPathState = checkDiagonals(monster, player)
                            elif diagPathState is None or monster.distanceTo(player) > 15:
                                monster.move(randint(-1, 1), randint(-1, 1)) #wandering
        FOV_recompute = True
#-- High Inquisitor --

def placeBoss(name, x, y):
    if name == 'Gluttony':
        fighterComponent = Fighter(hp=1000, armor=6, power=8, xp = 1000, deathFunction = gluttonysDeath, accuracy = 13, evasion = 1, shootCooldown = 10, landCooldown = 4)
        AI_component = Gluttony()
        boss = GameObject(x, y, char = 'G', color = colors.darker_lime, name = name, blocks = True, Fighter = fighterComponent, AI = AI_component)
        objects.append(boss)
        
        for x in range(50, 100):
            for y in range(20, 60):
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

def createSword(x, y):
    name = 'sword'
    pic = 'trollMace.xp'
    sizeChance = {'short' : 40, 'long' : 60}
    sizeChoice = randomChoice(sizeChance)
    name = sizeChoice + name
    if sizeChoice == 'short':
        swordPow = 6
        char = '-'
        weight = 1.5
    else:
        swordPow = 10
        char = '/'
        weight = 3.5
        pic = 'longSword.xp'
    qualityChances = {'normal' : 70, 'rusty' : 20, 'sharp' : 10}
    qualityChoice = randomChoice(qualityChances)
    if qualityChoice == 'rusty':
        name = qualityChoice + ' ' + name
        swordPow -= 2
        pic = 'rustysword.xp'
    elif qualityChoice == 'sharp':
        name = qualityChoice + ' ' + name
        swordPow += 2
    burningChances = {'yes' : 20, 'no': 80}
    burningChoice = randomChoice(burningChances)
    if burningChoice == 'yes':
        name = 'burning ' + name
        burningSword = True
    else:
        burningSword = False
    equipmentComponent = Equipment(slot='one handed', type = 'light weapon', powerBonus = swordPow, burning = burningSword, meleeWeapon=True)
    sword = GameObject(x, y, char, name, colors.sky, Equipment = equipmentComponent, Item = Item(weight=weight, pic = pic))
    return sword 

def createScroll(x, y):
    scrollChances = currentBranch.scrollChances
    scrollChoice = randomChoice(scrollChances)
    if scrollChoice == 'lightning':
        scroll = GameObject(x, y, '~', 'scroll of lightning bolt', colors.light_yellow, Item = Item(useFunction = castLightning, weight = 0.3, stackable = True), blocks = False, pName = 'scrolls of lightning bolt')
    elif scrollChoice == 'confuse':
        scroll = GameObject(x, y, '~', 'scroll of confusion', colors.light_yellow, Item = Item(useFunction = castConfuse, weight = 0.3, stackable = True), blocks = False, pName = 'scrolls of confusion')
    elif scrollChoice == 'fireball':
        fireballChances = {'lesser': 20, 'normal': 50, 'greater': 20}
        fireballChoice = randomChoice(fireballChances)
        if fireballChoice == 'lesser':
            scroll = GameObject(x, y, '~', 'scroll of lesser fireball', colors.light_yellow, Item = Item(castFireball, 2, 12, weight = 0.3, stackable = True), blocks = False, pName = 'scrolls of lesser fireball')
        elif fireballChoice == 'normal':
            scroll = GameObject(x, y, '~', 'scroll of fireball', colors.light_yellow, Item = Item(castFireball, weight = 0.3, stackable = True), blocks = False, pName = 'scrolls of fireball')
        elif fireballChoice == 'greater':
            scroll = GameObject(x, y, '~', 'scroll of greater fireball', colors.light_yellow, Item = Item(castFireball, 4, 48, weight = 0.3, stackable = True), blocks = False, pName = 'scrolls of greater fireball')
    elif scrollChoice == 'armageddon':
        scroll = GameObject(x, y, '~', 'scroll of armageddon', colors.red, Item = Item(castArmageddon, weight = 0.3, stackable = True), blocks = False, pName = 'scrolls of armageddon')
    elif scrollChoice == 'ice':
        scroll = GameObject(x, y, '~', 'scroll of ice bolt', colors.light_cyan, Item = Item(castFreeze, weight = 0.3, stackable = True, amount = randint(1, 3)), blocks = False, pName = 'scrolls of ice bolt')
    elif scrollChoice == 'none':
        scroll = None
    return scroll

def createSpellbook(x, y):
    spellbookChances = currentBranch.spellbookChances
    spellbookChoice = randomChoice(spellbookChances)
    if spellbookChoice == "healSelf":
        spellbook = GameObject(x, y, '=', 'spellbook of healing', colors.violet, Item = Item(useFunction = learnSpell, arg1 = heal, weight = 1.0), blocks = False)
    elif spellbookChoice == "fireball":
        spellbook = GameObject(x, y, '=', 'spellbook of fireball', colors.violet, Item = Item(useFunction = learnSpell, arg1 = fireball, weight = 1.0), blocks = False)
    elif spellbookChoice == "lightning":
        spellbook = GameObject(x, y, '=', 'spellbook of lightning bolt', colors.violet, Item = Item(useFunction = learnSpell, arg1 = lightning, weight = 1.0), blocks = False)
    elif spellbookChoice == "confuse":
        spellbook = GameObject(x, y, '=', 'spellbook of confusion', colors.violet, Item = Item(useFunction = learnSpell, arg1 = confuse, weight = 1.0), blocks = False)
    elif spellbookChoice == "ice":
        spellbook = GameObject(x, y, '=', 'spellbook of ice bolt', colors.violet, Item = Item(useFunction = learnSpell, arg1 = ice, weight = 1.0), blocks = False)
    elif spellbookChoice == 'none':
        spellbook = None
    return spellbook

def createDarksoul(x, y, friendly = False, corpse = False):
    if x != player.x or y != player.y:
        if not corpse:
            equipmentComponent = Equipment(slot='head', type = 'armor', armorBonus = 2)
            darksoulHelmet = GameObject(x = None, y = None, char = '[', name = 'darksoul helmet', color = colors.silver, Equipment = equipmentComponent, Item = Item(weight = 2.5))
            lootOnDeath = [darksoulHelmet]
            deathType = monsterDeath
            darksoulName = "darksoul"
            color = colors.dark_grey
        else:
            darksoulName = "darksoul skeleton"
            deathType = zombieDeath
            lootOnDeath = None
            color = colors.lighter_gray
        if not friendly:
            AI_component = BasicMonster()
        else:
            AI_component = FriendlyMonster(friendlyTowards = player)
        fighterComponent = Fighter(hp=30, armor=1, power=6, xp = 35, deathFunction = deathType, evasion = 25, accuracy = 10, lootFunction = lootOnDeath, lootRate = [30])
        monster = GameObject(x, y, char = 'd', color = color, name = darksoulName, blocks = True, Fighter=fighterComponent, AI = AI_component)
        return monster
    else:
        return 'cancelled'

def createTroll(x, y, friendly = False, corpse = False):
    if x != player.x or y != player.y:
        if not corpse:
            equipmentComponent = Equipment(slot = 'two handed', type = 'heavy weapon', powerBonus = 15, accuracyBonus = -20, meleeWeapon=True)
            trollMace = GameObject(x, y, '/', 'troll mace', colors.darker_orange, Equipment=equipmentComponent, Item=Item(weight = 13.0, pic = 'trollMace.xp', description= 'A dumb weapon for dumb people.'))
            lootOnDeath = [trollMace]
            deathType = monsterDeath
            monName = "troll"
            color = colors.darker_green
        else:
            monName = "troll skeleton"
            deathType = zombieDeath
            lootOnDeath = None
            color = colors.lighter_grey
        if not friendly:
            AI_component = BasicMonster()
        else:
            AI_component = FriendlyMonster(friendlyTowards = player)
        fighterComponent = Fighter(hp=40, armor=4, power=8, xp = 100, deathFunction = deathType, accuracy = 7, evasion = 1, lootFunction=lootOnDeath, lootRate=[15])
        monster = GameObject(x, y, char = 'T', color = color, name = monName, blocks = True, Fighter=fighterComponent, AI = AI_component)
        return monster
    else:
        if corpse:
            message("You briefly feel something moving beneath your feet...")
        return 'cancelled'
    
def createHiroshiman(x, y):
    if x != player.x or y != player.y:
        fighterComponent = Fighter(hp=300, armor=0, power=6, xp = 500, deathFunction = monsterDeath, accuracy = 0, evasion = 1)
        AI_component = SplosionAI()
        monster = GameObject(x, y, char = 'H', color = colors.red, name = 'Hiroshiman', blocks = True, Fighter=fighterComponent, AI = AI_component)
        return monster
    else:
        return 'cancelled'

def createCultist(x,y):
    if x != player.x or y != player.y:
        robeEquipment = Equipment(slot = 'torso', type = 'light armor', maxHP_Bonus = 5, maxMP_Bonus = 10)
        robe = GameObject(0, 0, '[', 'cultist robe', colors.desaturated_purple, Equipment = robeEquipment, Item=Item(weight = 1.5))
        
        knifeEquipment = Equipment(slot = 'one handed', type = 'light weapon', powerBonus = 7, meleeWeapon = True)
        knife = GameObject(0, 0, '-', 'cultist knife', colors.desaturated_azure, Equipment = knifeEquipment, Item=Item(weight = 1.0))
        
        spellbook = GameObject(x, y, '=', 'spellbook of arcane rituals', colors.violet, Item = Item(useFunction = learnSpell, arg1 = darkPact, weight = 1.0, description = "A spellbook full of arcane rituals and occult incantations. Such magic is easy to learn and to use, but comes at a great price."), blocks = False)
        
        fighterComponent = Fighter(hp = 20, armor = 2, power = 6, xp = 30, deathFunction = monsterDeath, accuracy = 18, evasion = 30, lootFunction = [robe, knife, spellbook], lootRate = [60, 20, 7])
        AI_component = BasicMonster()
        monster = GameObject(x, y, char = 'c', color = colors.desaturated_purple, name = 'cultist', blocks = True, Fighter = fighterComponent, AI = AI_component)
        return monster
    else:
        return 'cancelled'

def createHighCultist(x, y):
    if x != player.x or y != player.y:
        robeEquipment = Equipment(slot = 'torso', type = 'light armor', maxHP_Bonus = 5, maxMP_Bonus = 25)
        robe = GameObject(0, 0, '[', 'high cultist robe', colors.desaturated_purple, Equipment = robeEquipment, Item=Item(weight = 1.5))
        
        flailEquipment = Equipment(slot = 'one handed', type = 'heavy weapon', powerBonus = 13, meleeWeapon = True)
        flail = GameObject(0, 0, '/', 'bloodsteel flail', colors.red, Equipment=flailEquipment, Item=Item(weight=5.5, pic = 'bloodsteelFlail.xp', description = "A heavy flail wielded by the high cultists and made of a heavy, blood-red metal."))
        
        spellbook = GameObject(x, y, '=', 'spellbook of arcane rituals', colors.violet, Item = Item(useFunction = learnSpell, arg1 = darkPact, weight = 1.0, description = "A spellbook full of arcane rituals and occult incantations. Such magic is easy to learn and to use, but comes at a great price."), blocks = False)
        
        fighterComponent = Fighter(hp = 40, armor = 2, power = 13, xp = 80, deathFunction = monsterDeath, accuracy = 20, evasion = 30, lootFunction = [robe, flail, spellbook], lootRate = [60, 25, 15])
        AI_component = BasicMonster()
        name = nameGen.humanLike()
        actualName = name + ' the high cultist'
        monster = GameObject(x, y, char = 'c', color = colors.dark_red, name = actualName, blocks = True, Fighter = fighterComponent, AI = AI_component)
        return monster
    else:
        return 'cancelled'
        
        
def createSnake(x, y):
    if x!= player.x or y != player.y:
        fighterComponent = Fighter(hp = 10, armor = 0, power = 3, xp = 10, deathFunction = monsterDeath, accuracy = 20, evasion = 70)
        AI_component = FastMonster(2)
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
    chances = chancesDictionnary.values()
    print(chances)
    for value in chances:
        if value < 0:
            print(value)
            print(chancesDictionnary.keys())
            print(chancesDictionnary)
            raise ValueError("Negative value in dict")
    strings = list(chancesDictionnary.keys())
    return strings[randomChoiceIndex(chances)]

def placeObjects(room, first = False):
    monsterChances = currentBranch.monsterChances
    itemChances = currentBranch.itemChances
    potionChances = currentBranch.potionChances
    numMonsters = randint(0, MAX_ROOM_MONSTERS)
    monster = None
    if 'troll' in monsterChances.keys():
        previousTrollChances = monsterChances['troll']
    if 'hiroshiman' in monsterChances.keys():
        previousHiroChances = monsterChances['hiroshiman']
    if 'highCultist' in monsterChances.keys():
        previousHighCultistChances = monsterChances['highCultist']
    if dungeonLevel > 2 and hiroshimanNumber == 0 and not first and 'hiroshiman' in monsterChances.keys():
        if 'troll' in monsterChances.keys():
            monsterChances['troll'] -= 50
        monsterChances['hiroshiman'] = 50
    if not highCultistHasAppeared and not first and 'highCultist' in monsterChances.keys():
        if 'troll' in monsterChances.keys():
            monsterChances['troll'] -= 50
        monsterChances['highCultist'] = 50
    
    for i in range(numMonsters):
        x = randint(room.x1+1, room.x2-1)
        y = randint(room.y1+1, room.y2-1)
        
        
        if not isBlocked(x, y) and (x, y) != (player.x, player.y):
            monsterChoice = randomChoice(monsterChances)
            if monsterChoice == 'darksoul':
                monster = createDarksoul(x, y)

            elif monsterChoice == 'hiroshiman' and hiroshimanNumber == 0 and dungeonLevel > 2:
                global hiroshimanNumber
                global monsterChances
                monster = createHiroshiman(x, y)
                hiroshimanNumber = 1
                del monsterChances['hiroshiman']
                monsterChances['troll'] = 20
                
            elif monsterChoice == 'troll':
                monster = createTroll(x, y)
            
            elif monsterChoice == 'snake':
                monster = createSnake(x, y)
            
            elif monsterChoice == 'cultist':
                monster = createCultist(x, y)
            elif monsterChoice == 'highCultist':
                global highCultistHasAppeared
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
                            
            else:
                monster = None

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
                    item = GameObject(x, y, '!', 'healing potion', colors.violet, Item = Item(useFunction = castHeal, weight = 0.4, stackable=True, amount = randint(1, 2), pic = "redpotion.xp", description = "A slighly bubbling red beverage that stimulates cell growth when ingested, which allows for wounds to heal signifcantly faster. However, it also notably increases risk of cancer, but if you're in a situation where you have to drink such a potion, this is probably one of the least of your worries."), blocks = False)
                if potionChoice == 'mana':
                    item = GameObject(x, y, '!', 'mana regeneration potion', colors.blue, Item = Item(useFunction = castRegenMana, arg1 = 10, weight = 0.4, stackable = True, pic = "smokybluepotion.xp", description = "The blueish smokes emanating from this potion scared more than one novice mage, but it actually tastes quite good and has no other short-term effect other than replenishing your life-force. However, the [PLACEHOLDER  WORLD (the 'normal' one, not Realm of Madness) NAME]'s Guild of Alchemists is still debating about whether or not it causes detrimental long-term effects."), blocks = False)
            elif itemChoice == 'scroll':
                item = createScroll(x, y)
            elif itemChoice == 'none':
                item = None
            elif itemChoice == 'sword':
                item = createSword(x, y)
            elif itemChoice == 'shield':
                equipmentComponent = Equipment(slot = 'one handed', type = 'shield', armorBonus=3)
                item = GameObject(x, y, '[', 'shield', colors.darker_orange, Equipment=equipmentComponent, Item=Item(weight = 3.0))
            elif itemChoice == 'spellbook':
                item = createSpellbook(x, y)
            elif itemChoice == "food":
                item = GameObject(x, y, ',', "slice of bread", colors.yellow, Item = Item(useFunction=satiateHunger, arg1 = 50, arg2 = "a slice of bread", weight = 0.2, stackable=True, amount = randint(1, 5), description = "This has probably been lying on the ground for ages, but you'll have to deal with it if you don't want to starve."), blocks = False, pName = "slices of bread") #50 regen might be a little overkill (or maybe not, needs playtesting). Also, ',' is the symbol that Angband uses for food, so I used it too.
            else:
                item = None
            if item is not None:            
                objects.append(item)
                item.sendToBack()
            
            if 'troll' in monsterChances.keys():
                monsterChances['troll'] = previousTrollChances
            if 'hiroshiman' in monsterChances.keys():
                monsterChances['hiroshiman'] = previousHiroChances
            if 'highCultist' in monsterChances.keys():
                monsterChances['highCultist'] = previousHighCultistChances 
#_____________ ROOM POPULATION + ITEMS GENERATION_______________

#_____________ EQUIPEMENT ________________
class Equipment:
    def __init__(self, slot, type, powerBonus=0, armorBonus=0, maxHP_Bonus=0, accuracyBonus=0, evasionBonus=0, criticalBonus = 0, maxMP_Bonus = 0, burning = False, ranged = False, rangedPower = 0, maxRange = 0, ammo = None, meleeWeapon = False):
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
        self.curSlot = None
        
        self.burning = burning
        self.ranged = ranged
        self.baseRangedPower = rangedPower
        self.maxRange = maxRange
        self.ammo = ammo
        self.meleeWeapon = meleeWeapon  
 
    def toggleEquip(self):
        if self.isEquipped:
            self.unequip()
        else:
            self.equip()

    def equip(self):
        extra = False
        handSlot = None
        oldEquipment = None
        global FOV_recompute
        
        handed = self.slot == 'one handed' or self.slot == 'two handed'
        
        if self.slot == 'one handed':
            inHands = getEquippedInHands()
            rightText = "right hand"
            leftText = "left hand"
            extra = False
            if player.Player.race == 'Demon spawn':
                if 'extra limb' in player.Player.mutationsGotten:
                    extraText = "extra arm"
                    extra = True
            for object in equipmentList:
                if object.Equipment.curSlot == "right hand":
                    rightText = rightText + " (" + object.name + ")"
                if object.Equipment.curSlot == "left hand":
                    leftText = leftText + " (" + object.name + ")"
                if object.Equipment.curSlot == 'both hands':
                    rightText = rightText + " (" + object.name + ")"
                    leftText = leftText + " (" + object.name + ")"
                if extra and object.Equipment.curSlot == 'extra arm':
                    extraText = extraText + ' (' + object.name + ')'
            if extra:
                handList = [rightText, leftText, extraText]
            else:
                handList = [rightText, leftText]
            handIndex = menu('What slot do you want to equip this ' + self.owner.name + ' in?', handList, 60)
            if handIndex == 0:
                handSlot = 'right hand'
            elif handIndex == 1:
                handSlot = 'left hand'
            elif extra and handIndex == 2:
                handSlot = 'extra arm'
            else:
                return None
        elif self.slot == 'two handed':
            handSlot = 'both hands'

        rightEquipment = None
        leftEquipment = None
        extraEquipment = None
        if handed:
            if self.meleeWeapon and handSlot == 'right hand':
                leftEquipment = getEquippedInSlot('left hand', hand = True)
                extraEquipment = getEquippedInSlot('extra arm', hand = True)
            elif self.meleeWeapon and handSlot == 'left hand':
                rightEquipment = getEquippedInSlot('right hand', hand = True)
                extraEquipment = getEquippedInSlot('extra arm', hand = True)
            elif extra and self.meleeWeapon and handSlot == 'extra arm':
                leftEquipment = getEquippedInSlot('left hand', hand = True)
                rightEquipment = getEquippedInSlot('right hand', hand = True)
        rightIsWeapon = rightEquipment and rightEquipment.meleeWeapon
        leftIsWeapon = leftEquipment and leftEquipment.meleeWeapon
        extraIsWeapon = extraEquipment and extraEquipment.meleeWeapon

        possible = True
        if rightIsWeapon or leftIsWeapon or extraIsWeapon:
            if not player.Player.dualWield:
                message('You cannot wield two weapons at the same time!', colors.yellow)
                possible = False
            else:
                if self.type == 'light weapon':
                    if rightIsWeapon and not rightEquipment.type == 'light weapon' or leftIsWeapon and not leftEquipment.type == 'light weapon' or rightIsWeapon and not rightEquipment.type == 'light weapon':
                        message('You can only wield several light weapons.', colors.yellow)
                        possible = False
        if possible:
            if not handed:
                oldEquipment = getEquippedInSlot(self.slot)
                if oldEquipment is not None:
                    oldEquipment.unequip()
            else:
                rightEquipment = None
                leftEquipment = None
                bothEquipment = None
        
                if self.slot == 'one handed':
                    bothEquipment = getEquippedInSlot('both hands', hand = True)
                    oldEquipment = getEquippedInSlot(handSlot, hand = True)
                if self.slot == 'two handed':
                    rightEquipment = getEquippedInSlot('right hand', hand = True)
                    leftEquipment = getEquippedInSlot('left hand', hand = True)
    
                if bothEquipment is not None:
                    bothEquipment.unequip()
                if rightEquipment is not None:
                    rightEquipment.unequip()
                if leftEquipment is not None:
                    leftEquipment.unequip()
                if oldEquipment is not None:
                    oldEquipment.unequip()
    
            inventory.remove(self.owner)
            equipmentList.append(self.owner)
            self.isEquipped = True
            if self.maxHP_Bonus != 0:
                player.Fighter.hp += self.maxHP_Bonus
            if self.maxMP_Bonus != 0:
                player.Fighter.MP += self.maxMP_Bonus
    
            if handed:
                self.curSlot = handSlot
                message('Equipped ' + self.owner.name + ' on ' + self.curSlot + '.', colors.light_green)
            else:
                message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', colors.light_green)
 
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

    @property
    def powerBonus(self):
        if self.type == 'light weapon':
            bonus = (20 * player.Player.actualPerSkills[0]) / 100
            return int(self.basePowerBonus * bonus + self.basePowerBonus)
        elif self.type == 'heavy weapon':
            bonus = (20 * player.Player.actualPerSkills[1]) / 100
            return int(self.basePowerBonus * bonus + self.basePowerBonus)
        elif self.type == 'throwing weapon':
            bonus = (20 * player.Player.actualPerSkills[3]) / 100
            return int(self.basePowerBonus * bonus + self.basePowerBonus)
        else:
            return self.basePowerBonus
    
    @property
    def rangedPower(self):
        if self.type == 'missile weapon':
            bonus = (20 * player.Player.actualPerSkills[2]) / 100
            return int(self.baseRangedPower * bonus + self.baseRangedPower + player.Player.dexterity)
        elif self.type == 'throwing weapon':
            bonus = (20 * player.Player.actualPerSkills[3]) / 100
            return int(self.baseRangedPower * bonus + self.baseRangedPower + player.Player.strength)
        else:
            return self.baseRangedPower

def getEquippedInSlot(slot, hand = False):
    if not hand:
        for object in equipmentList:
            if object.Equipment and object.Equipment.slot == slot and object.Equipment.isEquipped:
                return object.Equipment
    else:
        for object in equipmentList:
            if object.Equipment and object.Equipment.curSlot == slot and object.Equipment.isEquipped:
                return object.Equipment
    return None

def getEquippedInHands():
    inHands = []
    for object in equipmentList:
        if object.Equipment and (object.Equipment.slot == 'one handed' or object.Equipment.slot == 'two handed') and object.Equipment.isEquipped:
            inHands.append(object)
        return inHands

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

def getAllWeights(object):
    if object == player:
        totalWeight = 0.0
        for item in inventory:
            totalWeight = math.fsum([totalWeight, item.Item.weight])
        equippedList = getAllEquipped(player)
        for equipment in equippedList:
            item = equipment.owner
            totalWeight = math.fsum([totalWeight, item.Item.weight])
        return totalWeight
    else:
        return 0.0

def checkLoad():
    load = getAllWeights(player)
    if load > player.Player.maxWeight:
        message("You are carrying too much objects! You are burdened and can't move anymore.", colors.yellow)
        player.Player.burdened = True
    if load < player.Player.maxWeight:
        player.Player.burdened = False

def lootItem(object, x, y):
    objects.append(object)
    object.x = x
    object.y = y
    object.sendToBack()
    message('A ' + object.name + ' falls from the dead body !', colors.dark_sky)

def playerDeath(player):
    global gameState
    message('You died!', colors.red)
    gameState = 'dead'
    player.char = '%'
    player.color = colors.dark_red
    deleteSaves()
 
def monsterDeath(monster):
    message(monster.name.capitalize() + ' is dead! You gain ' + str(monster.Fighter.xp) + ' XP.', colors.dark_sky)
    
    if monster.Fighter.lootFunction is not None:
        itemIndex = 0
        for item in monster.Fighter.lootFunction:
            loot = randint(1, 100)
            if loot <= monster.Fighter.lootRate[itemIndex]:
                lootItem(item, monster.x, monster.y)
            itemIndex += 1

    monster.char = '%'
    monster.color = colors.dark_red
    monster.blocks = False
    monster.AI = None
    monster.name = 'remains of ' + monster.name
    monster.Fighter = None
    monster.sendToBack()

def zombieDeath(monster):
    global objects
    message(monster.name.capitalize() + ' is destroyed !')
    objects.remove(monster)
    monster.char = ''
    monster.color = Ellipsis
    monster.blocks = False
    monster.AI = None
    monster.name = None
    monster.Fighter = None

#_____________ GUI _______________
def renderBar(cons, x, y, totalWidth, name, value, maximum, barColor, backColor):
    barWidth = int(float(value) / maximum * totalWidth) #Width of the bar is proportional to the ratio of the current value over the maximum value
    cons.draw_rect(x, y, totalWidth, 1, None, bg = backColor)#Background of the bar
    
    if barWidth > 0:
        cons.draw_rect(x, y, barWidth, 1, None, bg = barColor)#The actual bar
        
    text = name + ': ' + str(value) + '/' + str(maximum)
    xCentered = x + (totalWidth - len(text))//2
    cons.draw_str(xCentered, y, text, fg = colors.white, bg=None)
    
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
            if item.Item.stackable:
                text = text + ' (' + str(item.Item.amount) + ')'
            options.append(text)
    index = menu(header, options, INVENTORY_WIDTH)
    if index is None or len(inventory) == 0 or index == "cancelled":
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
    if index is None or len(player.Fighter.knownSpells) == 0 or borked or index == "cancelled":
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
            options.append(text)
    index = menu(header, options, INVENTORY_WIDTH)
    if index is None or len(equipmentList) == 0 or index == "cancelled":
        return None
    else:
        return equipmentList[index].Item

def mainMenu():
    global player
    choices = ['New Game', 'Continue', 'About', 'Quit']
    index = 0
    while not tdl.event.isWindowClosed():
        root.clear()
        drawCentered(cons =  root, y = 15, text = 'Dementia', fg = colors.white, bg = None)
        drawCentered(cons = root, y = 44, text = choices[0], fg = colors.white, bg = None)
        drawCentered(cons = root, y = 45, text = choices[1], fg  = colors.white, bg = None)
        drawCentered(cons = root, y = 46, text = choices[2], fg = colors.white, bg = None)
        drawCentered(cons = root, y = 47, text = choices[3], fg = colors.white, bg = None)
        drawCentered(cons = root, y = 44 + index, text=choices[index], fg = colors.black, bg = colors.white)
        tdl.flush()
        key = tdl.event.key_wait()
        if key.keychar.upper() == "DOWN":
            index += 1
            playWavSound('select.wav', True)
        elif key.keychar.upper() == "UP":
            index -= 1
            playWavSound('select.wav', True)
        if index < 0:
            index = len(choices) - 1
        if index > len(choices) - 1:
            index = 0
        if key.keychar.upper() == "ENTER":
            if index == 0:
                (playerComponent, levelUpStats, actualPerSkills, skillsBonus, startingSpells, chosenRace, chosenClass, chosenTraits) = characterCreation()
                if playerComponent != 'cancelled':
                    name = enterName(chosenRace)
                    playComp = Player(name, playerComponent[7], playerComponent[8], playerComponent[9], playerComponent[10], actualPerSkills, levelUpStats, skillsBonus, chosenRace, chosenClass, chosenTraits)
                    playFight = Fighter(hp = playerComponent[4], power= playerComponent[0], armor= playerComponent[3], deathFunction=playerDeath, xp=0, evasion = playerComponent[2], accuracy = playerComponent[1], maxMP= playerComponent[5], knownSpells=startingSpells, critical = playerComponent[6])
                    player = GameObject(25, 23, '@', Fighter = playFight, Player = playComp, name = name, color = (0, 210, 0))
                    player.level = 1
                    player.Player.updatePlayerStats()

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
                pass
                #Credits
            elif index == 3:
                raise SystemExit("Chose Quit on the main menu")
        tdl.flush()
    
def credits():
    centerX, centerY = MID_WIDTH, MID_HEIGHT
    #drawCentered(cons, y, text, fg, bg)
#_____________ GUI _______________

def initializeFOV():
    global FOV_recompute, visibleTiles, pathfinder, menuWindows
    FOV_recompute = True
    menuWindows = []
    visibleTiles = tdl.map.quickFOV(player.x, player.y, isVisibleTile, fov = FOV_ALGO, radius = SIGHT_RADIUS, lightWalls = FOV_LIGHT_WALLS)
    pathfinder = tdl.map.AStar(MAP_WIDTH, MAP_HEIGHT, callback = getMoveCost, diagnalCost=1, advanced=False)
    print("shortName = ", currentBranch.shortName)
    con.clear()

def Update():
    global FOV_recompute
    global visibleTiles
    global tilesinPath
    con.clear()
    tdl.flush()
    player.Player.changeColor()
    checkLoad()
    if FOV_recompute:
        FOV_recompute = False
        global pathfinder
        visibleTiles = tdl.map.quickFOV(player.x, player.y, isVisibleTile, fov = FOV_ALGO, radius = SIGHT_RADIUS, lightWalls = FOV_LIGHT_WALLS)
        pathfinder = tdl.map.AStar(MAP_WIDTH, MAP_HEIGHT, callback = getMoveCost, diagnalCost=1, advanced=False)
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = (x, y) in visibleTiles
                tile = myMap[x][y]
                if not visible:
                    if tile.explored:
                        con.draw_char(x, y, tile.character, tile.dark_fg, tile.dark_bg)
                else:
                    con.draw_char(x, y, tile.character, tile.fg, tile.bg)
                    tile.explored = True
                if gameState == 'targeting':
                    inRange = (x, y) in tilesInRange
                    inPath = pathToTargetTile and (x,y) in pathToTargetTile
                    if inRange and not tile.wall:
                        con.draw_char(x, y, None, fg=None, bg=colors.darker_yellow)
                    if inPath:
                        if (x,y) != (player.x, player.y):
                            if not tile.wall:
                                con.draw_char(x, y, '.', fg = colors.dark_green, bg = None)
                            else:
                                con.draw_char(x, y, 'X', fg = colors.red, bg = None)
                        
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
    renderBar(panel, 1, 1, BAR_WIDTH, 'HP', player.Fighter.hp, player.Fighter.maxHP, player.color, colors.dark_gray)
    renderBar(panel, 1, 3, BAR_WIDTH, 'MP', player.Fighter.MP, player.Fighter.maxMP, colors.blue, colors.dark_gray)
    # Look code
    if gameState == 'looking' and lookCursor != None:
        global lookCursor
        lookCursor.draw()
        panel.draw_str(1, 0, GetNamesUnderLookCursor(), bg=None, fg = colors.yellow)
        
    root.blit(panel, 0, PANEL_Y, WIDTH, PANEL_HEIGHT, 0, 0)
    
def GetNamesUnderLookCursor():
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
    names = ', '.join(names)
    return names.capitalize()

def targetTile(maxRange = None, showBresenham = False):
    global gameState
    global cursor
    global tilesInRange
    global FOV_recompute
    global pathToTargetTile
    
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
                pathToTargetTile = []
                cursor.move(dx, dy)
                if showBresenham:
                    brLine = tdl.map.bresenham(player.x, player.y, cursor.x, cursor.y)
                    for i in range(len(brLine)):
                        pathToTargetTile.append(brLine[i])
                    #print(pathToTargetTile)
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
def accessMapFile(level = dungeonLevel, branchToDisplay = currentBranch.shortName):
    mapName = branchToDisplay + str(level)
    print(mapName)
    mapFile = os.path.join(absDirPath, mapName)
    return mapFile


def saveGame():
    
    if not os.path.exists(absDirPath):
        os.makedirs(absDirPath)
    
    file = shelve.open(absFilePath, "n")
    file["dungeonLevel"] = dungeonLevel
    file["currentBranch"] = currentBranch
    file["myMap_level{}".format(dungeonLevel)] = myMap
    print("Saved myMap_level{}".format(dungeonLevel))
    file["objects_level{}".format(dungeonLevel)] = objects
    file["playerIndex"] = objects.index(player)
    file["stairsIndex"] = objects.index(stairs)
    file["inventory"] = inventory
    file["equipmentList"] = equipmentList
    file["gameMsgs"] = gameMsgs
    file["gameState"] = gameState
    file["hiroshimanNumber"] = hiroshimanNumber
    if dungeonLevel > 1:
        file["upStairsIndex"] = objects.index(upStairs)
    gluttBrLevel = dBr.gluttonyDungeon.origDepth
    if dungeonLevel == gluttBrLevel and currentBranch == dBr.mainDungeon:
        try:
            file["gluttStairsIndex"] = objects.index(gluttonyStairs)
        except:
            print("Couldn't save Gluttony stairs")
            pass
    file.close()
    
    #mapFile = open(absPicklePath, 'wb')
    #pickle.dump(myMap, mapFile)
    #mapFile.close()

def newGame():
    global objects, inventory, gameMsgs, gameState, player, dungeonLevel, gameMsgs, equipmentList, currentBranch, bossDungeonsAppeared
    
    deleteSaves()
    bossDungeonsAppeared = {'gluttony': False}
    gameMsgs = []
    objects = [player]
    currentBranch = dBr.mainDungeon
    dungeonLevel = 1 
    makeMap()
    Update()

    inventory = []
    equipmentList = []

    FOV_recompute = True
    initializeFOV()
    message('Zargothrox says : Prepare to get lost in the Realm of Madness !', colors.dark_red)
    gameState = 'playing'
    
    equipmentComponent = Equipment(slot='one handed', type = 'light weapon', powerBonus=3, burning = False, meleeWeapon=True)
    object = GameObject(0, 0, '-', 'dagger', colors.light_sky, Equipment=equipmentComponent, Item=Item(weight = 0.8, pic = 'dagger.xp'), darkColor = colors.darker_sky)
    inventory.append(object)
    object.alwaysVisible = True
    if player.Player.classes == 'Rogue':
        equipmentComponent = Equipment(slot = 'two handed', type = 'missile weapon', powerBonus = 1, ranged = True, rangedPower = 7, maxRange = SIGHT_RADIUS, ammo = 'arrow')
        object = GameObject(0, 0, ')', 'shortbow', colors.light_orange, Equipment = equipmentComponent, Item = Item(weight = 1.0, pic = 'bow.xp'), darkColor = colors.dark_orange)
        inventory.append(object)
        object.alwaysVisible = True
        
        itemComponent = Item(stackable = True, amount = 30)
        object = GameObject(0, 0, '^', 'arrow', colors.light_orange, Item = itemComponent)
        inventory.append(object)
    
    if highCultistHasAppeared: #It's the exact contrary of the last statement yet it does the exact same thing (aside from the fact that we can have several high cultists)
        global highCultistHasAppeared
        message('You feel like somebody really wants you dead...', colors.dark_red)
        highCultistHasAppeared = False #Make so more high cultists can spawn at lower levels (still only one by floor though)

def loadGame():
    global objects, inventory, gameMsgs, gameState, player, dungeonLevel, myMap, equipmentList, stairs, upStairs, hiroshimanNumber, currentBranch, gluttonyStairs
    
    
    #myMap = [[Tile(True) for y in range(MAP_HEIGHT)]for x in range(MAP_WIDTH)]
    file = shelve.open(absFilePath, "r")
    dungeonLevel = file["dungeonLevel"]
    currentBranch = file["currentBranch"]
    myMap = file["myMap_level{}".format(dungeonLevel)]
    objects = file["objects_level{}".format(dungeonLevel)]
    player = objects[file["playerIndex"]]
    stairs = objects[file["stairsIndex"]]
    inventory = file["inventory"]
    equipmentList = file["equipmentList"]
    gameMsgs = file["gameMsgs"]
    gameState = file["gameState"]
    hiroshimanNumber = file["hiroshimanNumber"]
    if dungeonLevel > 1:
        upStairs = objects[file["upStairsIndex"]]
    gluttBrLevel = dBr.gluttonyDungeon.origDepth
    if dungeonLevel == gluttBrLevel and currentBranch == dBr.mainDungeon:
        gluttonyStairs = objects[file["gluttStairsIndex"]]
    #mapFile = open(absPicklePath, "rb")
    #myMap = pickle.load(mapFile)
    #mapFile.close()

def saveLevel(level = dungeonLevel):
    #if not os.path.exists(absDirPath):
        #os.makedirs(absDirPath)
    
    #if not os.path.exists(absFilePath):
        #file = shelve.open(absFilePath, "n")
        #print()
    #else:
        #file = shelve.open(absFilePath, "w")
    mapFilePath = accessMapFile(level)
    mapFile = shelve.open(mapFilePath, "n")
    mapFile["myMap"] = myMap
    mapFile["objects"] = objects
    mapFile["playerIndex"] = objects.index(player)
    mapFile["stairsIndex"] = objects.index(stairs)
    if dungeonLevel > 1:
        mapFile["upStairsIndex"] = objects.index(upStairs)
    gluttBrLevel = dBr.gluttonyDungeon.origDepth
    if dungeonLevel == gluttBrLevel and currentBranch == dBr.mainDungeon:
        try:
            mapFile["gluttStairsIndex"] = objects.index(gluttonyStairs)
        except:
            print("Couldn't save Gluttony Dungeon")
    mapFile["yunowork"] = "SCREW THIS"
    print("Saved level at " + mapFilePath)
    mapFile.close()
    
    return "completed"

def loadLevel(level, save = True, branch = currentBranch):
    global objects, player, myMap, stairs, dungeonLevel, gluttonyStairs
    if save:
        try:
            saveLevel(dungeonLevel)
        except:
            print("Couldn't save level " + dungeonLevel)
    mapFilePath = accessMapFile(level, branch.shortName)
    xfile = shelve.open(mapFilePath, "r")
    print(xfile["yunowork"])
    myMap = xfile["myMap"]
    objects = xfile["objects"]
    player = objects[xfile["playerIndex"]]
    stairs = objects[xfile["stairsIndex"]]
    if level > 1:
        global upStairs
        upStairs = objects[xfile["upStairsIndex"]]
    gluttBrLevel = dBr.gluttonyDungeon.origDepth
    if dungeonLevel == gluttBrLevel and branch == dBr.gluttonyDungeon:
        gluttonyStairs = objects[xfile["gluttStairsIndex"]]
    message("You climb the stairs")
    print("Loaded level " + str(level))
    xfile.close()
    dungeonLevel = level
    initializeFOV()

def nextLevel(boss = False, changeBranch = None):
    global dungeonLevel, currentBranch
    returned = "borked"
    changeToCurrent = False
    while returned != "completed":
        returned = saveLevel(dungeonLevel)
    if changeBranch is None:
        message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', colors.red)
        dungeonLevel += 1
        changeToCurrent = True
    else:
        message('You enter ' + changeBranch.name)
        dungeonLevel = 1
        currentBranch = changeBranch
    if changeToCurrent:
        changeBranch = currentBranch
    tempMap = myMap
    tempObjects = objects
    tempPlayer = player
    tempStairs = stairs
    try:
        loadLevel(dungeonLevel, save = False, branch= changeBranch)
        print("Loaded existing level {}".format(dungeonLevel))
    except:
        global myMap, objects, player, stairs
        myMap = tempMap
        objects = tempObjects
        player = tempPlayer
        stairs = tempStairs
        if not boss:
            makeMap()
        else:
            makeBossLevel()
        print("Created a new level")
    if hiroshimanNumber == 1 and not hiroshimanHasAppeared:
        global hiroshimanHasAppeared
        message('You suddenly feel uneasy.', colors.dark_red)
        hiroshimanHasAppeared = True
    if highCultistHasAppeared: #It's the exact contrary of the last statement yet it does the exact same thing (aside from the fact that we can have several high cultists)
        global highCultistHasAppeared
        message('You feel like somebody really wants you dead...', colors.dark_red)
        highCultistHasAppeared = False #Make so more high cultists can spawn at lower levels (still only one by floor though)
    initializeFOV()

def playGame():
    while not tdl.event.isWindowClosed():
        global FOV_recompute
        Update()
        checkLevelUp()
        tdl.flush()
        for object in objects:
            object.clear()
        playerAction = getInput()
        FOV_recompute = True #So as to avoid the blackscreen bug no matter which key we press
        if playerAction == 'exit':
            quitGame('Player pressed escape', True)
        if gameState == 'playing' and playerAction != 'didnt-take-turn':
            for object in objects:
                if object.AI:
                    object.AI.takeTurn()
                if object.Fighter and object.Fighter.frozen and object.Fighter is not None:
                    object.Fighter.freezeCooldown -= 1
                    if object.Fighter.freezeCooldown < 0:
                        object.Fighter.freezeCooldown = 0
                    if object.Fighter.freezeCooldown == 0:
                        object.Fighter.frozen = False
                        message(object.name.capitalize() + "'s ice shatters !", colors.light_violet)
                
                if object.Fighter and object.Fighter.baseShootCooldown > 0 and object.Fighter is not None:
                    object.Fighter.curShootCooldown -= 1
                if object.Fighter and object.Fighter.baseLandCooldown > 0 and object.Fighter is not None:
                    object.Fighter.curLandCooldown -= 1

                if object.Fighter and object.Fighter.enraged and object.Fighter is not None:
                    object.Fighter.enrageCooldown -= 1
                    if object.Fighter.enrageCooldown < 0:
                        object.Fighter.enrageCooldown = 0
                    if object.Fighter.enrageCooldown == 0:
                        object.Fighter.enraged = False
                        if object != player:
                            message(object.name.capitalize() + "is no longer enraged !", colors.amber)
                        else:
                            message('You are no longer enraged.', colors.amber)
                        object.Fighter.basePower = object.Fighter.BASE_POWER
                        if object.Player:
                            object.Player.updatePlayerStats()

                if object.Fighter and object.Fighter.burning and object.Fighter is not None:
                    try:
                        object.Fighter.burnCooldown -= 1
                        object.Fighter.takeDamage(3)
                        message('The ' + str(object.name) + ' keeps burning !')
                        if object.Fighter.burnCooldown < 0:
                            object.Fighter.burnCooldown = 0
                        if object.Fighter.burnCooldown == 0:
                            object.Fighter.burning = False
                            message(object.name.capitalize() + "'s flames die down", colors.darker_orange)
                    except AttributeError:
                        global DEBUG
                        if DEBUG:
                            message('Failed to apply burn to ' + object.name, colors.violet)

                if object.Fighter and object.Fighter.spellsOnCooldown and object.Fighter is not None:
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
                        if not player.Fighter.burning and not player.Fighter.frozen and  player.Fighter.hp != player.Fighter.maxHP and not monsterInSight:
                            player.Fighter.healCountdown -= 1
                            if player.Fighter.healCountdown < 0:
                                player.Fighter.healCountdown = 0
                            if player.Fighter.healCountdown == 0:
                                player.Fighter.heal(1)
                                player.Fighter.healCountdown= 25 - player.Player.vitality

                if object.Player and object.Player.race == 'Werewolf':
                    object.Player.transformCurCooldown -= 1
                    if object.Player.transformationTime > 0:
                        object.Player.transformationTime -= 1
                    if object.Player.transformCurCooldown <= 0:
                        message('You feel your wild instincts overwhelming you! You have turned into your wolf form!', colors.amber)
                        object.Player.transformed = True
                        object.Player.transformationTime = object.Player.transformMaxTurns
                        object.Player.strength += 5
                        object.Player.dexterity += 3
                        object.Player.vitality += 4
                        object.Player.willpower -= 5
                        object.Player.transformCurCooldown = object.Player.transformCooldown    
                        object.Player.updatePlayerStats()
                    if object.Player.transformationTime <= 0 and object.Player.transformed:
                        message('You are no longer in wolf form.', colors.amber)
                        object.Player.transformed = False
                        object.Player.transformationTime = object.Player.transformMaxTurns
                        object.Player.strength -= 5
                        object.Player.dexterity -= 3
                        object.Player.vitality -= 4
                        object.Player.willpower += 5
                        object.Player.updatePlayerStats()
                
                x = object.x
                y = object.y
                if myMap[x][y].acid and object.Fighter and object.Fighter is not None:
                    object.Fighter.takeDamage(1)
                    object.Fighter.acidified = True
                    object.Fighter.acidifiedCooldown = 6
                    curArmor = object.Fighter.armor - object.Fighter.baseArmor
                    object.Fighter.baseArmor = -curArmor
                
                if object.Fighter and object.Fighter.acidified and object.Fighter is not None:
                    object.Fighter.acidifiedCooldown -= 1
                    if object.Fighter.acidifiedCooldown <= 0:
                        object.Fighter.acidified = False
                        object.Fighter.baseArmor = object.Fighter.BASE_ARMOR

            for x in range(MAP_WIDTH):
                for y in range(MAP_HEIGHT):
                    if myMap[x][y].acid:
                        myMap[x][y].curAcidCooldown -= 1
                        if myMap[x][y].curAcidCooldown <= 0:
                            myMap[x][y].acid = False
                        
            global stairCooldown
            if stairCooldown > 0:
                stairCooldown -= 1
                if stairCooldown == 0 and DEBUG:
                    message("You're no longer tired", colors.purple)
            if stairCooldown < 0:
                stairCooldown = 0
            
            player.Player.hunger -= 1
            if player.Player.hunger > BASE_HUNGER:
                player.Player.hunger = BASE_HUNGER
            if player.Player.hunger < 0:
                player.Player.hunger = 0
            if player.Player.hunger <= BASE_HUNGER // 10:
                player.Player.hungerStatus = "starving"
                player.Fighter.takeDamage(1)
                message("You're starving !", colors.red)
            elif player.Player.hunger <= BASE_HUNGER // 2:
                prevStatus = player.Player.hungerStatus
                player.Player.hungerStatus = "hungry"
                if prevStatus == "full":
                    message("You're starting to feel a little bit hungry.", colors.yellow)
                elif prevStatus == "starving":
                    message("You're no longer starving")
            else:
                prevStatus = player.Player.hungerStatus
                player.Player.hungerStatus = "full"
                if prevStatus != "full":
                    message("You feel way less hungry")

    DEBUG = False
    quitGame('Window has been closed')
    
mainMenu()