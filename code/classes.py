import code.dunbranches as dBr
import colors, copy, pdb, traceback, os, sys, time, math
from random import randint
import code.constants as constants
import tdlib as tdl
import code.custom_except

color_dark_wall = dBr.mainDungeon.mapGeneration['wallDarkFG']
color_light_wall = dBr.mainDungeon.mapGeneration['wallFG']
color_dark_ground = dBr.mainDungeon.mapGeneration['groundDarkBG']
color_dark_gravel = dBr.mainDungeon.mapGeneration['gravelDarkFG']
color_light_ground = dBr.mainDungeon.mapGeneration['groundBG']
color_light_gravel = dBr.mainDungeon.mapGeneration['gravelFG']
maxRooms = dBr.mainDungeon.maxRooms
roomMinSize = dBr.mainDungeon.roomMinSize
roomMaxSize = dBr.mainDungeon.roomMaxSize

SPELL_GEN_DEBUG = False


def printTileWhenWalked(tile):
    print("Player walked on tile at {};{}".format(tile.x, tile.y))

class Tile:
    def __init__(self, blocked, x, y, block_sight = None, character = None, fg = None, bg = None, dark_fg = None, dark_bg = None, chasm = False, wall = False, hole = False, moveCost = 0):
        self.baseBlocked = blocked
        self.explored = False
        self.unbreakable = False
        self.baseCharacter = character
        self.baseFg = fg
        self.FG = fg
        self.baseBg = bg
        self.BG = bg
        self.baseDark_fg = dark_fg
        self.DARK_FG = dark_fg
        self.baseDark_bg = dark_bg
        self.DARK_BG = dark_bg
        self.wall = wall
        self.chasm = chasm
        self.hole = hole
        self.x = x
        self.y = y
        self.secretWall = False
        self.pillar = False
        self.door = False
        if block_sight is None:
            block_sight = blocked
            self.block_sight = block_sight
        else:
            self.block_sight = block_sight
        self.belongsTo = []
        self.usedForPassage = False
        if self.wall:
            self.baseCharacter = '#'
            self.FG = color_light_wall
            self.baseFg = color_light_wall
            self.BG = color_light_ground
            self.baseBg = color_light_ground
            self.DARK_FG = color_dark_wall
            self.baseDark_fg = color_dark_wall
            self.DARK_BG = color_dark_ground
            self.baseDark_bg = color_dark_ground
        if self.chasm:
            self.baseCharacter = None
            self.FG = colors.black
            self.baseFg = colors.black
            self.BG = (0, 0, 16)
            self.baseBg = (0, 0, 16)
            self.DARK_FG = colors.black
            self.baseDark_fg = colors.black
            self.DARK_BG = (0, 0, 16)
            self.baseDark_bg = (0, 0, 16)
        self.baseMoveCost = moveCost
        self.djikValue = None
        self.doNotPropagateDjik = False
        self.onTriggerFunction = printTileWhenWalked
        self.clearance = 1
        self.buffList = []
        self.water = False
        self.lava = False
    
    #@property
    def moveCost(self, flying=False):
        bonus = 0
        if self.buffList:
            for tileBuff in self.buffList:
                bonus += tileBuff.addMoveCost
        if self.water or self.lava:
            bonus += constants.WATER_WALK_COST
        if not flying:
            return self.baseMoveCost + bonus
        return self.baseMoveCost
    
    @property
    def blocked(self):
        if self.buffList:
            for tileBuff in self.buffList:
                if tileBuff.blocksTile:
                    return True
        return self.baseBlocked
    
    @property
    def character(self):
        if self.buffList:
            for tileBuff in self.buffList:
                if tileBuff.char:
                    return tileBuff.char
        if self.water or self.lava:
            if randint(0, 4) == 0:
                return '~'
            return None
        return self.baseCharacter
    
    @property
    def fg(self):
        if self.buffList:
            for tileBuff in self.buffList:
                if tileBuff.fg:
                    return tileBuff.fg
        if self.water:
            return colors.dark_sky
        if self.lava:
            return colors.dark_amber
        return self.baseFg
    
    @property
    def bg(self):
        if self.buffList:
            for tileBuff in self.buffList:
                if tileBuff.bg:
                    return tileBuff.bg
        if self.water:
            return colors.dark_azure
        if self.lava:
            return colors.dark_flame
        return self.baseBg
    
    @property
    def dark_fg(self):
        if self.water:
            return colors.darkest_sky
        if self.lava:
            return colors.darkest_amber
        return self.baseDark_fg
    
    @property
    def dark_bg(self):
        if self.water:
            return colors.darkest_azure
        if self.lava:
            return colors.darkest_flame
        return self.baseDark_bg
        
    def neighbors(self, mapToUse, count = False, cardinal = False):
        x = self.x
        y = self.y
        try:
            upperLeft = mapToUse[x - 1][y - 1]
        except IndexError:
            upperLeft = None
        except TypeError:
            traceback.print_exc()
            print(mapToUse)
            print("WRONG TILE = ", end="")
            print(x,y, sep=";")
            
        try:
            up = mapToUse[x][y - 1]
        except IndexError:
            up = None
            
        try:
            upperRight = mapToUse[x + 1][y - 1]
        except IndexError:
            upperRight = None
            
        try:
            left = mapToUse[x - 1][y]
        except IndexError:
            left = None
            
        try:
            right = mapToUse[x + 1][y]
        except IndexError:
            right = None
            
        try:
            lowerLeft = mapToUse[x - 1][y + 1]
        except IndexError:
            lowerLeft = None
        
        try:
            low = mapToUse[x][y + 1]
        except IndexError:
            low = None

        try:
            lowerRight = mapToUse[x + 1][y + 1]
        except IndexError:
            lowerRight = None
        
        if not count and not cardinal:
            return [i for i in [upperLeft, up, upperRight, left, right, lowerLeft, low, lowerRight] if i is not None]
        elif cardinal and not count:
            return [i for i in [up, left, right, low] if i is not None]
        elif cardinal and count:
            c = 0
            for i in [up, left, right, low]:
                if i and i.blocked:
                    c += 1
            return c
        else:
            c = 0
            for i in [upperLeft, up, upperRight, left, right, lowerLeft, low, lowerRight]:
                if i and i.blocked:
                    c += 1
            return c

    def neighbours(self, mapToUse = None, count = False, cardinal = False):
        result = self.neighbors(mapToUse, count, cardinal)
        return result
    
    def cardinalNeighbors(self, mapToUse):
        x = self.x
        y = self.y
        try:
            up = mapToUse[x][y - 1]
        except IndexError:
            up = None
        try:
            left = mapToUse[x - 1][y]
        except IndexError:
            left = None
        try:
            right = mapToUse[x + 1][y]
        except IndexError:
            right = None
        try:
            low = mapToUse[x][y + 1]
        except IndexError:
            low = None
        return [i for i in [up, left, right, low] if i is not None]
    
    def cardinalNeighbours(self, mapToUse):
        result = self.cardinalNeighbors(mapToUse)
        return result

    def applyWallProperties(self):
        if not self.secretWall:
            self.wall = True
            self.baseCharacter = '#'
            self.FG = color_light_wall
            self.baseFg = color_light_wall
            self.BG = color_light_ground
            self.baseBg = color_light_ground
            self.DARK_FG = color_dark_wall
            self.baseDark_fg = color_dark_wall
            self.DARK_BG = color_dark_ground
            self.baseDark_bg = color_dark_ground
    
    def applyChasmProperties(self):
        if not self.secretWall:
            self.chasm = True
            self.baseCharacter = None
            self.FG = colors.black
            self.baseFg = colors.black
            self.BG = (0, 0, 16)
            self.baseBg = (0, 0, 16)
            self.DARK_FG = colors.black
            self.baseDark_fg = colors.black
            self.DARK_BG = (0, 0, 16)
            self.baseDark_bg = (0, 0, 16)
    
    def applyGroundProperties(self, explode = False, temple = False):
        if temple:
            gravelChar1 = chr(250)
            gravelChar2 = chr(254)
        else:
            gravelChar1 = chr(177)
            gravelChar2 = chr(176)
        if explode:
            if not self.chasm or self.wall:
                gravelChoice = randint(0, 5)
                self.baseBlocked = False
                self.block_sight = False
                if gravelChoice == 0:
                    self.baseCharacter = gravelChar1
                elif gravelChoice == 1:
                    self.baseCharacter = gravelChar2
                else:
                    self.baseCharacter = None
                self.baseFg = color_light_gravel
                self.baseBg = color_light_ground
                self.baseDark_fg = color_dark_gravel
                self.baseDark_bg = color_dark_ground
                self.wall = False
                self.chasm = False
        else:
            if not self.secretWall or self.pillar:
                gravelChoice = randint(0, 5)
                self.baseBlocked = False
                self.block_sight = False
                if gravelChoice == 0:
                    self.baseCharacter = gravelChar1
                elif gravelChoice == 1:
                    self.baseCharacter = gravelChar2
                else:
                    self.baseCharacter = None
                self.baseFg = color_light_gravel
                self.baseBg = color_light_ground
                self.baseDark_fg = color_dark_gravel
                self.baseDark_bg = color_dark_ground
                self.wall = False
    
    def setUnbreakable(self):
        self.baseBlocked = True
        self.unbreakable = True
        self.wall = True
        
    def open(self):
        if not self.unbreakable:
            self.baseBlocked = False
            self.block_sight = False
            self.wall = False
            return True
        else:
            return False
    
    def close(self, makeIndestructible = False):
        if not self.blocked:
            self.baseBlocked = True
            self.block_sight = True
            self.wall = True
        if makeIndestructible:
            self.unbreakable = True
    
    def addOwner(self, toAdd):
        if not toAdd in self.belongsTo:
            if self.belongsTo:
                otherOwners = list(self.belongsTo)
            else:
                otherOwners = []
            self.belongsTo.append(toAdd)
            print(otherOwners)
            return otherOwners
    
    def returnOtherOwners(self, base):
        newList = list(self.belongsTo)
        newList.remove(base)
        return newList
    
    def triggerFunc(self):
        self.onTriggerFunction(self)
        

class Rectangle:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        self.tiles = []
        for x in range(self.x1 + 1, self.x2):
            for y in range(self.y1 + 1, self.y2):
                self.tiles.append((x, y))
        
    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)
 
    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)
    
    def checkForCaveIntersection(self, caveTiles):
        for tile in self.tiles:
            if tile in caveTiles:
                return False
        return True

class NamedConsole(tdl.Console):
    def __init__(self, name, width, height, type = 'noType'):
        self.name = name
        self.type = type
        tdl.Console.__init__(self, width, height)

class WeightedChoice:
    def __init__(self, name, prob):
        self.name = name
        self.prob = prob
        
        #print("FUCKING INITIALIZED AS A {}".format(self.__class__.__name__))
    '''
    def __iter__(self):
        print("Iterating")
        return iter([self.name, self.prob]) #For some reason Python wants this class to be iterable, or else it won't put it into my custom list classes. So I made it iterable, though you probably don't want to use that as an iterator ever.
    '''
    def __str__(self):
        return "{} : {} AS STRING".format(self.name, self.prob)
    
class SpellTemplate:
    def __init__(self, level = None, cost = None, type = None, ressourceType = None):
        self.type = type
        self.targeting = None
        self.zone = None
        self.eff1 = None
        self.eff2 = None
        self.eff3 = None
        self.level = level
        self.impure = False
        self.cost = cost
        self.color = None
        self.ressource = ressourceType
        self.name = None
        self.subtype = None
    
    def __str__(self):
        text = "Level {} spell costing {} {} \n \n".format(self.level, self.cost, self.ressource)
        if self.impure:
            text += "Is an impure {} and {} spell (-1 level) \n".format(self.type, str(self.subtype))
        else:
            text += "Is a classic {} and {} spell \n".format(self.type, str(self.subtype))
        text += "Targeting type: {} \n".format(self.targeting)
        text += "Affects entities in a {} \n \n".format(self.zone)
        text += "Effect 1: {} ({}) \n".format(self.eff1.name, self.eff1.amount)
        if self.eff2 is not None:
            text += "Effect 2: {} ({}) \n".format(self.eff2.name, self.eff2.amount)
        if self.eff3 is not None:
            text += "Effect 3: {} ({}) \n".format(self.eff3.name, self.eff3.amount)
        
        return text

class NumberedEffect:
    def __init__(self, name, amount):
        self.name = name
        self.amount = amount

class DoubleNumberedEffect(NumberedEffect):
    def __init__(self, name, initAmount, overtimeAmount):
        NumberedEffect.__init__(self, name, initAmount)
        self.overtimeAmount = overtimeAmount
        
class BetterList(list):
    def __init__(self, *args):
        #super(BetterList, self).__init__(args[0])
        selfList = []
        savedArgs = locals()
        for thing in savedArgs["args"]:
            selfList.append(thing)
            if SPELL_GEN_DEBUG:
                print(thing)
        list.__init__(self, selfList)
    
    def removeFrom(self, element):
        ind = self.index(element)
        self.remove(self[ind])
        
    def randFrom(self):
        ind = randint(0, len(self) - 1)
        return self[ind]

class EvenBetterList(list): #DON'T EVER MAKE THIS INHERIT FROM BETTERLIST IF YOU VALUE YOUR SANITY. (it's probably going to crash this way too though) (actually nvm it's a real pain that way too)
    def __init__(self, *args):
        self.selfList = []
        savedArgs = locals()
        for thing in savedArgs["args"]:
            self.selfList.append(thing)
            if SPELL_GEN_DEBUG:
                print(thing)
        list.__init__(self, self.selfList)
        if SPELL_GEN_DEBUG:
            print("Initialized EBL !")
            for stuffThatShouldBeAWeightedChoiceAndNotAFuckingStringIHateYouPython in self:
                print("PRINTING")
                print(stuffThatShouldBeAWeightedChoiceAndNotAFuckingStringIHateYouPython)
        for thing in self:
            if not thing.__class__.__name__ == "WeightedChoice":
                print(thing)
                print(thing.__class__.__name__)
                raise code.custom_except.WrongElementTypeException(thing)
            elif SPELL_GEN_DEBUG:
                print("{} : {}".format(thing.name, thing.prob))
    
    def removeFrom(self, element):
        ind = self.index(element)
        self.remove(self[ind])

    def randFrom(self):
        chances = []
        for choice in self:
            chances.append(choice.prob)
        dice = randint(1, sum(chances))
        runningSum = 0
        choice = 0
        for chance in chances:
            runningSum += chance
            if dice <= runningSum:
                return self[choice]
            choice += 1


