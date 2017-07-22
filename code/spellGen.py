import copy
import code.custom_except
from random import randint
from code.constants import *

SPELL_GEN_DEBUG = True

class WeightedChoice:
    def __init__(self, name, prob):
        self.name = name
        self.prob = prob
        
        print("FUCKING INITIALIZED AS A {}".format(self.__class__.__name__))
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
        self.ressource = ressourceType
    
    def __str__(self):
        text = "Level {} spell costing {} {} \n \n".format(self.level, self.cost, self.ressource)
        text += "Belongs to {} type \n".format(self.type)
        if self.impure:
            text += "Is an impure spell (-1 level) \n"
        else:
            text += "Is a classic spell \n"
        text += "Targeting type =  {} \n".format(self.targeting)
        text += "Affects entities in a {} \n".format(self.zone)
        text += "Effect 1 : {} ({}) \n".format(self.eff1.name, self.eff1.amount)
        if self.eff2 is not None:
            text += "Effect 2 : {} ({}) \n".format(self.eff2.name, self.eff2.amount)
        if self.eff3 is not None:
            text += "Effect 3 : {} ({}) \n".format(self.eff3.name, self.eff3.amount)
        
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
        
    
    


'''
HOW SPELL GEN IS GOING TO WORK (Spoiler : In a way way more complex than what's needed)



                                                                                                                                      
                                                                                                                                     Pure attack ---- Roll amount
                                                                                                                                   /
                                                                                                           Bad effect (high chance)
                                                                                                          /                        \ Debuff ---- Roll turn duration
                                                                                                         /
                 Attack ---- Target/Zone choice ---- Number of effects = randint(1,3) - For each effect /
              /                                                                                         \                            Heal ---- Roll amount
             /                                                                                           \                         /
            /                                                                                             \Good effect (low chance)
           /                                                                                                                       \ Buff ---- Roll turn duration
          /
         /  
TypeSelect                        (Had lot of !!FUN!! making this)
        \    
         \                                                                                                                         Heal ---- Roll amount
          \                                                                                                                      /
           \                                                                                            Good effect (high chance)
            \                                                                                         /                          \
             \                                                                                       /                            Buff  ---- Roll turn duration
              Defense ---- Target/Zone choice ---- Number of effects = randint(1,3) - For each effect
                                                                                                    \                          Attack ---- Roll amount
                                                                                                     \                       /
                                                                                                      Bad effect (low chance)
                                                                                                                             \
                                                                                                                               Debuff ---- Roll turn duration

If a spell has an effect that doesn't fit its type (Good effect on attack spell, bad effect on defense spell), it is considered as "impure" and therefore has reduced MP and skill requirements than a normal spell.




'''
baseTypeList = BetterList("Attack", "Defense")

targetSelect = WeightedChoice("Select", 25)
targetSelf = WeightedChoice("Self", 25)
targetClosest = WeightedChoice("Closest", 25)
targetFarthest = WeightedChoice("Farthest", 25)

zoneSingle = WeightedChoice("SingleTile", 25)
zoneCross = WeightedChoice("Cross", 25)
zoneX = WeightedChoice("X", 25)
zoneAOE = WeightedChoice("AOE", 25)

attFire = WeightedChoice("FireDamage", 33)
attPhy = WeightedChoice("PhysicalDamage", 33)
attPoi = WeightedChoice("PoisonDamage", 33)

buffHunger = WeightedChoice("Hunger", 25)
buffAttack = WeightedChoice("AttackStat", 25)
buffDefense = WeightedChoice("DefenseStat", 25)
buffSpeed = WeightedChoice("Speed", 25)

baseTargetList = EvenBetterList(targetSelect, targetSelf, targetClosest, targetFarthest)
baseZoneList = EvenBetterList(zoneSingle, zoneCross, zoneX, zoneAOE)

baseAttackList = EvenBetterList(attFire, attPhy, attPoi) #Porbably want to add more stuff here
baseBuffList = EvenBetterList(buffHunger, buffAttack, buffDefense, buffSpeed) #Common list for buffs/debuffs
baseHealList = EvenBetterList(WeightedChoice("HealHP", 25), WeightedChoice("HealMP", 25), WeightedChoice("CureFire", 25), WeightedChoice("CurePoison", 25))

def createSpell():
    spellLevel = randint(1,5)
    isImpure = False
    
    typeList = copy.copy(baseTypeList)
    targetList = copy.copy(baseTargetList)
    zoneList = copy.copy(baseZoneList)
    
    attackList = copy.copy(baseAttackList)
    buffList = copy.copy(baseBuffList)
    healList = copy.copy(baseHealList)
    
    type = typeList.randFrom()
    
    if type == "Attack":
        targetList.removeFrom(targetSelf)
        zoneSingle.prob = 25
    elif type == "Defense":
        targetList.removeFrom(targetClosest)
        targetList.removeFrom(targetFarthest)
        zoneSingle.prob = 75
    else:
        print(type)
        raise ValueError("Invalid spell type")
    
    target = targetList.randFrom()
    zone = zoneList.randFrom()
    
    if spellLevel > 3:
        maxEffects = 3
    elif spellLevel >= 2:
        maxEffects = 2
    else:
        maxEffects = 1
    
    effects = [None, None, None]
    for loop in range(maxEffects):
        isBuff = False
        noOccult = False
        curEffectImpure = False
        potential = 0
        if type == "Attack":
            if maxEffects == 1:
                effectAlign = "Bad"
            else:
                dice = randint(0, 100)
                if dice < 80:
                    effectAlign = "Bad"
                else:
                    effectAlign = "Good"
                    isImpure = True
                    curEffectImpure = True
        elif type == "Defense":
            if maxEffects == 1:
                effectAlign = "Good"
            else:
                dice = randint(0, 100)
                if dice < 80:
                    effectAlign = "Good"
                else:
                    effectAlign = "Bad"
                    isImpure = True
                    curEffectImpure = True
        
        if effectAlign == "Good":
            dice = randint(0, 1)
            if dice == 0:
                eff = buffList.randFrom()
                buffList.removeFrom(eff)
                effName = eff.name
                #buffList.
                effName += "+"
                isBuff = True
            else:
                eff = healList.randFrom()
                healList.removeFrom(eff)
                effName = eff.name
                if effName == "HealHP":
                    noOccult = True
        else:
            dice = randint(0, 1)
            if dice == 0:
                eff = buffList.randFrom()
                buffList.removeFrom(eff)
                effName = eff.name
                effName += '-'
                isBuff = True
            else:
                eff = attackList.randFrom()
                attackList.removeFrom(eff)
                effName = eff.name

        
        if not isBuff:
            if not curEffectImpure:
                effAmount = randint(1, 5) * spellLevel * randint(1, 3)
            elif potential - effAmount > 0:
                effAmount = randint(1, 5) * spellLevel * randint(1, 3) * -1
            else:
                effAmount = 0
            potential += effAmount
            
        else:
            if not curEffectImpure:
                effAmount = randint(1, 2) * spellLevel * randint(1, 3)
            elif potential - effAmount > 0:
                effAmount = randint(1, 2) * spellLevel * randint(1, 3) * -1
            else:
                effAmount = 0
            potential += effAmount // 4
        
        effects[loop] = NumberedEffect(effName, effAmount)
    
    if isImpure:
        spellLevel -= 1
    
    cost = (potential // 10 + randint(1, 10)) * spellLevel
    dice = randint(0, 10)
    if dice < 8 or noOccult:
        ressource = "MP"
    else:
        ressource = "HP"
    
    resultSpell = SpellTemplate(spellLevel, cost, type, ressource)
    resultSpell.impure = isImpure
    resultSpell.eff1 = effects[0]
    resultSpell.eff2 = effects[1]
    resultSpell.eff3 = effects[2]
    
    resultSpell.targeting = target.name
    resultSpell.zone = zone.name
    
    return resultSpell


if __name__ == '__main__':
    for loop in range(10):
        print(createSpell())
        print()
    
        
        
    
    
    
    
    
    