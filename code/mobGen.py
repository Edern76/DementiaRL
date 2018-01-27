import copy
import code.custom_except
from random import randint
from code.constants import *
import code.itemGen as itemGen
import colors
#import code.dunbranches as dBr
from math import *
import os, sys

def findCurrentDir():
    if getattr(sys, 'frozen', False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)
    listDir = list(datadir)
    for loop in range(4):
        del listDir[len(listDir) - 1]
    print(listDir)
    dir = ''
    for loop in range(len(listDir) - 1):
        dir += listDir[loop]
    print(dir)
    return dir

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

curDir = findCurrentDir()
relMobsPath = "assets\\monsters"
absMobsPath = os.path.join(curDir, relMobsPath)

#GameObject template: x, y, char, name, color, blocks, Fighter, AI, Player, Ghost, flying, Item, alwaysVisible, darkColor, Equipment, pName, Essence,
#                     socialComp, shopComp, questList, Stairs, alwaysAlwaysVisible, size, sizeChar, sizeColor, sizeDarkColor, smallChar, ProjectileComp

class GameObjectTemplate:
    "A generic object, represented by a character"
    def __init__(self, name = 'name', char = 'n', color = colors.white, Fighter = None, AI = None, flying = False, size = 1, sizeChar = [], sizeColor = [], smallChar = None):
        self.name = name
        self.char = char
        self.color = color
        self.Fighter = Fighter
        self.flying = flying
        self.AI = AI
        self.smallChar = smallChar
        
        self.size = size
        self.sizeChar = sizeChar#a list of characters which will form the final object. The list needs to be created with this pattern in mind, as does sizeColor:
                                #X 2 5
                                #0 3 6
                                #1 4 7
        self.sizeColor = sizeColor
        if self.size > 1:
            sizeCompNum = self.size * self.size - 1
            if not self.sizeChar:
                self.sizeChar = []
                for char in range(sizeCompNum):
                    self.sizeChar.append(self.char)
            if not self.sizeColor:
                self.sizeColor = []
                for color in range(sizeCompNum):
                    self.sizeColor.append(self.color)
    
    def __str__(self):
        text = '{} ({} {}), of size {}, it is {} flying and has the AI {}'.format(self.name, self.color, self.char, self.size, self.flying, self.AI)
        if self.Fighter:
            text += '\n\n' + str(self.Fighter)
        if self.Ranged:
            text += '\n\n' + str(self.Ranged)
        return text

#Fighter template: hp, armor, power, accuracy, evasion, xp, deathFunction=None, maxMP = 0, knownSpells = None, critical = 5, armorPenetration = 0,
#                  lootFunction = None, lootRate = [0], shootCooldown = 0, landCooldown = 0, transferDamage = None, leechRessource = None, leechAmount = 0,
#                  buffsOnAttack = None, slots = ['head', 'torso', 'left hand', 'right hand', 'legs', 'feet'], equipmentList = [], toEquip = [],
#                  attackFunctions = [], noDirectDamage = False, pic = 'ogre.xp', description = 'Placeholder', rangedPower = 0, Ranged = None, stamina = 0,
#                  attackSpeed = 100, moveSpeed = 100, rangedSpeed = 100,
#                  resistances = {'physical': 0, 'poison': 0, 'fire': 0, 'cold': 0, 'lightning': 0, 'light': 0, 'dark': 0, 'none': 0},
#                  attackTypes = {'physical': 100}

class FighterTemplate: #All NPCs, enemies and the player
    def __init__(self, hp = 1, armor = 0, power = 1, accuracy = 0, evasion = 1, xp = 0, deathFunction=None, mp = 0, knownSpells = None, critical = 5, armorPenetration = 0, lootFunction = None, lootRate = [0], transferDamage = None, leechRessource = None, leechAmount = 0, buffsOnAttack = None, slots = ['head', 'torso', 'left hand', 'right hand', 'legs', 'feet'], equipmentList = [], attackFunctions = [], noDirectDamage = False, description = 'Placeholder', Ranged = None, stamina = 0, attackSpeed = 100, moveSpeed = 100, rangedSpeed = 100, resistances = {'physical': 0, 'poison': 0, 'fire': 0, 'cold': 0, 'lightning': 0, 'light': 0, 'dark': 0, 'none': 0}, attackTypes = {'physical': 100}):
        self.hp = hp
        self.armor = armor
        self.power = power
        self.deathFunction = deathFunction
        self.xp = xp
        self.accuracy = accuracy
        self.evasion = evasion
        self.critical = critical
        self.armorPenetration = armorPenetration
        self.lootFunction = lootFunction
        self.lootRate = lootRate
        self.description = description
        self.stamina = stamina
        
        self.attackSpeed = attackSpeed
        self.moveSpeed = moveSpeed
        self.rangedSpeed = rangedSpeed
        
        self.leechRessource = leechRessource
        self.leechAmount = leechAmount
        self.buffsOnAttack = buffsOnAttack
        
        self.Ranged = Ranged

        self.mp = mp
        
        self.slots = slots
        self.equipmentList = equipmentList
        
        if knownSpells != None:
            self.knownSpells = knownSpells
        else:
            self.knownSpells = []
        
        self.transferDamage = transferDamage
        
        self.attackFunctions = attackFunctions
        self.noDirectDamage = noDirectDamage
        
        self.resistances = resistances
        self.attackTypes = attackTypes
    
    def __str__(self):
        text =  'A monster with {}, described as {}'.format(self.slots, self.description)
        text += '\nIt is equipped with {} and can loot {}'.format(self.equipmentList, self.lootFunction)
        
        if self.power != 0:
            text += '\n' + str('power:' + str(self.power))
        if self.armor != 0:
            text += '\n' + str('armor:' + str(self.armor))
        if self.hp != 0:
            text += '\n' + str('HP:' + str(self.hp))
        if self.accuracy != 0:
            text += '\n' + str('acc:' + str(self.accuracy))
        if self.evasion != 0:
            text += '\n' + str('evasion:' + str(self.evasion))
        if self.critical != 0:
            text += '\n' + str('crit:' + str(self.critical))
        if self.mp != 0:
            text += '\n' + str('MP:' + str(self.mp))
        if self.armorPenetration != 0:
            text += '\n' + str('AP:' + str(self.armorPenetration))
        if self.stamina != 0:
            text += '\n' + str('stamina:' + str(self.stamina))
        if self.attackSpeed != 0:
            text += '\n' + str('speed:' + str(self.attackSpeed))
        if self.attackTypes:
            text += '\n' + 'Damage types:' + str(self.attackTypes)
        if self.resistances:
            text += '\n' + 'Resistances:' + str(self.resistances)
        
        return text

#RangedNPC template: shotRange, power, accuracy, critical = 5, armorPenetration = 0, buffsOnAttack = [], leechRessource = '', attackFunctions = [],
#                    shootMessage = ' shoots {} for ', projChar = '/', projColor = colors.light_orange, continues = False, passesThrough = False,
#                    ghost = False

class RangedNPCTemplate:
    def __init__(self, shotRange = 1, power = 0, accuracy = 0, critical = 5, armorPenetration = 0, buffsOnAttack = [], leechRessource = '', attackFunctions = [], shootMessage = ' shoots {} for ', projChar = '/', projColor = colors.light_orange, continues = False, passesThrough = False, ghost = False):
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

def convertColorString(string):
    color = {'r': '', 'g': '', 'b': ''}
    currentColor = 'r'
    for char in string:
        if char in '0123456789':
            color[currentColor] += char
        elif char == ',':
            if currentColor == 'r':
                currentColor = 'g'
            elif currentColor == 'g':
                currentColor = 'b'
        elif char == ')':
            return (int(color['r']), int(color['g']), int(color['b']))

def convertListString(string):
    newList = []
    text = ''
    usedString = string[1:len(string)-1]
    innerListInd = []
    inParenthesis = 0
    for i, char in enumerate(usedString):
        if i in innerListInd:
            continue
        if char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.$=_*' or (char in ''','"''' and inParenthesis >= 1):
            text += char
        elif char == ' ' and text != '':
            text += char
        elif char == '(':
            text += char
            inParenthesis += 1
        elif char == ')':
            text += char
            inParenthesis -= 1
        elif char == ',' and inParenthesis < 1:
            if text != '':
                try:
                    newList.append(int(text))
                except:
                    newList.append(text)
                text = ''
        elif char == '[' and inParenthesis < 1:
            openBracketCount = 0
            closeBracketCount = 0
            j = i
            for char in usedString[i:]:
                if char == '[':
                    closeBracketCount += 1
                elif char == ']' and closeBracketCount == openBracketCount+1:
                    break
                elif char == ']':
                    closeBracketCount += 1
                j+=1
            innerListInd = range(i+1, j+1)
            newList.append(convertListString(usedString[i:j+1]))
    
    if text != '':
        try:
            newList.append(int(text))
        except:
            newList.append(text)
    return newList

class BetterStr:
    def __init__(self, string):
        self.string = string
    
    def __str__(self):
        return self.string
    '''
    def __iadd__(self, other):
        self.string = self.string + other
    
    def __add__(self, other):
        return self.string + other
    '''
   
def convertDictString(string):
    newDict = {}
    key = BetterStr('')
    value = BetterStr('')
    usedText = key
    for char in string[1:len(string)-1]:
        if char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._*':
            usedText.string += char
        elif char == ' ' and usedText.string != '':
            usedText.string += char
        elif char == ':':
            usedText = value
        elif char == ',':
            try:
                key = int(key.string)
            except:
                key = key.string
            try:
                value = int(value.string)
            except:
                value = value.string
            newDict[key] = value
            key = BetterStr('')
            value = BetterStr('')
            usedText = key
    
    try:
        key = int(key.string)
    except:
        key = key.string
    try:
        value = int(value.string)
    except:
        value = value.string
    newDict[key] = value
    
    return newDict

def readMobFile(fileName):  #without .txt
    file = open(os.path.join(absMobsPath, fileName+'.txt'), 'r')
    
    gameObjParam = ['name', 'char', 'color', 'AI', 'flying', 'size', 'sizeChar', 'sizeColor', 'smallChar']
    kwargs = {'Fighter': None, 'AI': None, 'flying': False, 'size': 1, 'sizeChar': [], 'sizeColor': [], 'smallChar': None}
    for i, line in enumerate(file):
        if line[0] == chr(92):
            break
        charList = list(line)
        charList.remove('\n')
        line = ''
        onlyDigits = True
        for char in charList:
            line += char
            if char not in '0123456789':
                onlyDigits = False
        if i == 2:
            line = convertColorString(line)
        if line != '*':
            if line == 'True':
                line = True
            elif line == 'False':
                line = False
            elif line == 'None':
                line = None
            elif onlyDigits:
                line = int(line)
            elif line[0] == '[':
                line = convertListString(line)
            elif line[0] == '{':
                line = convertDictString(line)
            kwargs[gameObjParam[i]] = line
    
    mobObject = GameObjectTemplate(**kwargs)
    #print(mobObject, end = '\n\n')
    
    fighterParam = ['hp', 'armor', 'power', 'accuracy', 'evasion', 'xp', 'deathFunction', 'mp', 'knownSpells', 'critical', 'armorPenetration', 'lootFunction', 'lootRate', 'transferDamage', 'leechRessource', 'leechAmount', 'buffsOnAttack', 'slots', 'equipmentList', 'attackFunctions', 'noDirectDamage', 'description', 'Ranged', 'stamina', 'attackSpeed', 'moveSpeed', 'rangedSpeed', 'resistances', 'attackTypes']
    kwargs = {'deathFunction': 'monsterDeath', 'knownSpells': [], 'lootFunction': [], 'lootRate': [], 'transferDamage': None, 'leechRessource': None, 'leechAmount': 0, 'buffsOnAttack': [], 'slots': ['head', 'torso', 'left hand', 'right hand', 'legs', 'feet'], 'equipmentList': [], 'attackFunctions': [], 'noDirectDamage': False, 'description': 'Placeholder', 'Ranged': None, 'resistances': {'physical': 0, 'poison': 0, 'fire': 0, 'cold': 0, 'lightning': 0, 'light': 0, 'dark': 0, 'none': 0}, 'attackTypes': {'physical': 100}}
    for i, line in enumerate(file, 10):
        if line[0] == chr(92):
            break
        charList = list(line)
        charList.remove('\n')
        line = ''
        onlyDigits = True
        for char in charList:
            line += char
            if char not in '0123456789':
                onlyDigits = False
        if i == 2:
            line = convertColorString(line)
        if line != '*':
            if line == 'True':
                line = True
            elif line == 'False':
                line = False
            elif line == 'None':
                line = None
            elif onlyDigits:
                line = int(line)
            elif line[0] == '[':
                line = convertListString(line)
            elif line[0] == '{':
                line = convertDictString(line)
            kwargs[fighterParam[i-10]] = line
    
    mobFighter = FighterTemplate(**kwargs)
    #print(mobFighter, end = '\n\n')
    
    rangedNPCParam = ['shotRange', 'power', 'accuracy', 'critical', 'armorPenetration', 'buffsOnAttack', 'leechRessource', 'attackFunctions', 'shootMessage', 'projChar', 'projColor', 'continues', 'passesThrough', 'ghost']
    kwargs = {'buffsOnAttack': [], 'leechRessource': None, 'attackFunctions': [], 'shootMessage': ' shoots {} for ', 'projChar': '/', 'continues': False, 'passesThrough': False, 'ghost': False}
    noRanged = False
    for i, line in enumerate(file, 40):
        if line[0] == chr(92):
            break
        charList = list(line)
        charList.remove('\n')
        line = ''
        onlyDigits = False
        for char in charList:
            line += char
            if char not in '0123456789':
                onlyDigits = False
        if line == '***':
            noRanged = True
            break
        if i == 50:
            line = convertColorString(line)
        if line != '*':
            if line == 'True':
                line = True
            elif line == 'False':
                line = False
            elif line == 'None':
                line = None
            elif onlyDigits:
                line = int(line)
            elif line[0] == '[':
                line = convertListString(line)
            elif line[0] == '{':
                line = convertDictString(line)
            kwargs[rangedNPCParam[i-40]] = line
    
    if not noRanged:
        mobRanged = RangedNPCTemplate(**kwargs)
    else:
        mobRanged = None
    #print(mobRanged)
    
    mobObject.Fighter = mobFighter
    mobObject.Ranged = mobRanged
    
    return mobObject

def progressFormula(level):
    #return sigmoidProgress(level)
    return 0

def generateMonster(playerLevel, monsterName):
    monsterLevel = randint(playerLevel - 2, playerLevel+ + 2)
    monsterObj = readMobFile(monsterName)
    monster = monsterObj.Fighter
    ranged = monster.Ranged
    
    monster.hp += round(progressFormula(monsterLevel) * monster.hp * 5)
    monster.armor += round(progressFormula(monsterLevel) * monster.armor * 5)
    monster.power += round(progressFormula(monsterLevel) * monster.power * 5)
    monster.xp += round(progressFormula(monsterLevel) * monster.xp * 5)
    monster.armorPenetration += round(progressFormula(monsterLevel) * monster.armorPenetration * 5)
    monster.stamina += round(progressFormula(monsterLevel) * monster.stamina * 5)
    monster.mp += round(progressFormula(monsterLevel) * monster.mp * 5)
    
    if ranged:
        ranged.power += round(progressFormula(monsterLevel) * ranged.power * 5)
    
    return monsterObj

if __name__ == '__main__':
    for i in range(10):
        playerLevel = 1 + i*10
        monster = generateMonster(playerLevel, 'ogre')
        print('playerLvl: {}, progress percentage: {}'.format(str(playerLevel), str(progressFormula(playerLevel))), monster, sep = '\n\n', end = '\n====\n')