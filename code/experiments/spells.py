'''
This is probably a bad and unrealistic idea
'''

import colors, math, textwrap, code, copy, random, functools #Code is not unused. Importing it allows us to import the rest of our custom modules in the code package.
import tdlib as tdl
import code.dialog as dial
from tdlib import *
from random import randint, choice
from math import *
from code.custom_except import *
from copy import copy, deepcopy

import code.spellGen as spellGen
from code.classes import *

SPELL_INFO_WIDTH = 60
WIDTH, HEIGHT, LIMIT = 159, 80, 20 #Defaults : 150, 80, 20
MAP_WIDTH, MAP_HEIGHT = 140, 60 #Defaults : 140, 60
MID_MAP_WIDTH, MID_MAP_HEIGHT = MAP_WIDTH//2, MAP_HEIGHT//2
MID_WIDTH, MID_HEIGHT = int(WIDTH/2), int(HEIGHT/2)

def drawCenteredVariableWidth(cons, y, text, fg = None, bg = None, width = WIDTH):
    xCentered = (width - len(text))//2
    cons.draw_str(xCentered, y, text, fg, bg)

class Spell:
    "Class used by all active abilites (not just spells)"
    def __init__(self, ressourceCost, cooldown, useFunction, name, *args, ressource = 'MP', type = 'Magic', magicLevel = 0, hiddenName = None, onRecoverLearn = [], castSpeed = 100, template = None):
        self.ressource = ressource
        self.ressourceCost = ressourceCost
        self.maxCooldown = cooldown
        self.curCooldown = 0
        self.useFunction = useFunction
        self.name = name
        self.type = type
        self.magicLevel = magicLevel
        self.args = args
        if hiddenName:
            self.hiddenName = hiddenName
        else:
            self.hiddenName = name
        self.onRecoverLearn = onRecoverLearn
        self.castSpeed = castSpeed
        self.template = template

    def cast(self, caster = None, target = None):
        if self.ressource == 'MP' and caster.Fighter.MP < self.ressourceCost:
            return 'cancelled', caster.name.capitalize() + ' does not have enough MP to cast ' + self.name +'.'
        if self.ressource == 'Stamina' and caster.Fighter.stamina < self.ressourceCost:
            return 'cancelled', caster.name.capitalize() + ' does not have enough stamina to cast ' + self.name +'.'
        
        if self.useFunction(*self.args, caster=caster, target=target) != 'cancelled':
            caster.Fighter.actionPoints -= self.castSpeed
            self.setOnCooldown(caster.Fighter)
            if self.ressource == 'MP':
                caster.Fighter.MP -= self.ressourceCost
            elif self.ressource == 'HP':
                caster.Fighter.takeDamage({'none': self.ressourceCost}, 'your spell')
            elif self.ressource == 'Stamina':
                caster.Fighter.stamina -= self.ressourceCost
            return 'used', ''
        else:
            return 'cancelled', ''
       
    def setOnCooldown(self, fighter):
        try:
            fighter.knownSpells.remove(self)
            self.curCooldown = self.maxCooldown
            fighter.spellsOnCooldown.append(self)
        except ValueError:
            print('SPELL {} is not in known spell list when trying to set it on cooldown'.format(self.name))

    def displayInfo(self, root, menuWindows, Update, posX = None):
        if self.template:
            baseWidth = SPELL_INFO_WIDTH
            desc = dial.formatText(str(self.template), baseWidth)
            header = textwrap.wrap(self.name.capitalize(), baseWidth)
            prevLine = None
            descriptionHeight = 0
            for line in desc:
                if line != "BREAK":
                    descriptionHeight += 1
                else:
                    if prevLine and prevLine == "BREAK":
                        descriptionHeight += 1
                prevLine = line
                
            height = descriptionHeight + 5
            
            curMaxWidth = 0
            for line in desc:
                if len(line) > curMaxWidth:
                    curMaxWidth = len(line)
            for line in header:
                if len(line) > curMaxWidth:
                    curMaxWidth = len(line)
            width = curMaxWidth + 3
            
            
            if menuWindows:
                for mWindow in menuWindows:
                    if not mWindow.name == 'spellMenu' and not mWindow.type == 'menu':
                        mWindow.clear()
                        print('CLEARED {} WINDOW OF TYPE {}'.format(mWindow.name, mWindow.type))
                        if mWindow.name == 'displaySpellInfo':
                            ind = menuWindows.index(mWindow)
                            del menuWindows[ind]
                            print('Deleted')
                    tdl.flush()
            Update()
            window = NamedConsole('displaySpellInfo', width, height)
            print('Created disp window')
            window.clear()
            menuWindows.append(window)
    
            for k in range(width):
                window.draw_char(k, 0, chr(196))
            window.draw_char(0, 0, chr(218))
            window.draw_char(k, 0, chr(191))
            kMax = k
            for l in range(height):
                if l > 0:
                    window.draw_char(0, l, chr(179))
                    window.draw_char(kMax, l, chr(179))
            lMax = l
            for m in range(width):
                window.draw_char(m, lMax, chr(196))
            window.draw_char(0, lMax, chr(192))
            window.draw_char(kMax, lMax, chr(217))
            Y = 1
            #X = 3
            prevLine = None
            for line in header:
                drawCenteredVariableWidth(window, y=Y, text = line, fg=colors.amber, width=width)
                Y+=1
            Y+=1
            for line in desc:
                if line != "BREAK":
                    if 'spell costing' in line:
                        window.draw_str(1, Y, line[:21])
                        if 'MP' in line:
                            color = colors.blue
                        elif 'HP' in line:
                            color = colors.dark_red
                        else:
                            color = colors.white
                        window.draw_str(22, Y, line[21:], fg = color)
                    else:
                        window.draw_str(1, Y, line)
                    incrementY = True
                else:
                    if prevLine and prevLine == "BREAK":
                        incrementY = True
                    else:
                        incrementY = False
                if incrementY:
                    Y += 1
                prevLine = line
            if not posX:
                posX = MID_WIDTH - width // 2
            posY = MID_HEIGHT - height//2
            root.blit(window, posX, posY, width, height, 0, 0)
        
            menuWindows.append(window)
            tdl.flush()

def doNothing(*args, **kwargs):
    pass

def rSpellExec(func1 = doNothing, func2 = doNothing, func3 = doNothing, targetFunction = targetMonsterWrapper, zoneFunction = singleTarget, color = colors.white, caster = None, target = None):
    global FOV_recompute
    if targetFunction.__name__ != 'targetSelf':
        message('Choose a target for your spell, press Escape to cancel.', colors.light_cyan)
    #if targetFunction.__name__ == 'targetTileWrapper':
    chosenTarget = targetFunction(caster, lambda start, caster: zoneFunction(start, caster, 3))
    #else:
    #    chosenTarget = targetFunction(caster)
    if chosenTarget != 'cancelled':
        print("FOOOOOOOOOOOOOOOOOOOOUNNNNNNNNNNNNNNNNNNND TARGEEEEEEEEEEEEEEEEEET")
        print("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        print(chosenTarget)
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        
        print("Before Zone")
        tilesList = zoneFunction(chosenTarget, caster, 3)
        print("After Zone, before draw")
        if len(tilesList) > 1:
            print("Draw")
            print(tilesList)
            for (x,y) in tilesList:
                if not myMap[x][y].blocked:
                    explodingTiles.append((x, y))
            explode(color)
            '''
                    con.draw_char(x,y, '*', fg = color)
            root.blit(con, 0, 0, WIDTH, HEIGHT, 0, 0)
            tdl.flush()
            time.sleep(2) #Set to .125 once testing done
            FOV_recompute = True
            Update()
            tdl.flush()
            '''
        print("After draw, before process")
        targetList = cleanList(processTiles(tilesList))
        
        print(targetList)
        
        if len(targetList) > 0:
            counter = 0
            for actualTarget in targetList:
                counter += 1
                if counter > 1000:
                    raise InfiniteLoopPrevention("Application of functions. Target list = {}".format(targetList))
                if actualTarget is not None and actualTarget.Fighter is not None and actualTarget.Fighter.hp > 0:
                    func1(caster, actualTarget)
                if actualTarget is not None and actualTarget.Fighter is not None and actualTarget.Fighter.hp > 0:
                    func2(caster, actualTarget)
                else:
                    if DEBUG:
                        message("OVERKILL !")
                if actualTarget is not None and actualTarget.Fighter is not None and actualTarget.Fighter.hp > 0:
                    func3(caster, actualTarget)
                else:
                    if DEBUG:
                        message("OVERKILL !")
        else:
            message("Your spell didn't hit anything !")
    else:
        message("You decided not to cast the spell.")
        return 'cancelled'





