import copy, inspect
import code.custom_except
from random import randint
from code.constants import *
from spellGen import WeightedChoice

SPELL_GEN_DEBUG = True
testList = [2, 5]

class WeightedChoice:
    def __init__(self, name, prob):
        self.name = name
        self.prob = prob
        
        print("FUCKING INITIALIZED AS A {}".format(self.__class__.__name__))
        
    def __iter__(self):
        print("Iterating")
        return iter([self.name, self.prob]) #For some reason Python wants this class to be iterable, or else it won't put it into my custom list classes. So I made it iterable, though you probably don't want to use that as an iterator ever.
    
    def __str__(self):
        return "{} : {} AS STRING".format(self.name, self.prob)
    
class SpellTemplate:
    def __init__(self):
        self.type = None
        self.targeting = None
        self.zone = None
        self.eff1 = None
        self.eff2 = None
        self.eff3 = None

class NumberedEffect:
    def __init__(self, name, amount):
        self.name = name
        self.amount = amount

class DoubleNumberedEffect:
    def __init__(self, name, initAmount, overtimeAmount):
        self.name = name
        self.initAmount = initAmount
        self.overtimeAmount = overtimeAmount
        
class BetterList(list):
    def __init__(self, *args):
        super(BetterList, self).__init__(args[0])
    
    def removeFrom(self, element):
        ind = self.index(element)
        self.remove(self[ind])
        
    def randFrom(self):
        ind = randint(0, len(self) - 1)
        return self[ind]

class EvenBetterList(list): #DON'T EVER MAKE THIS INHERIT FROM BETTERLIST IF YOU VALUE YOUR SANITY. (it's probably going to crash this way too though) (actually nvm it's a real pain that way too)
    def __init__(self, *args):
        selfList = []
        savedArgs = locals()
        for thing in savedArgs["args"]:
            selfList.append(thing)
            if SPELL_GEN_DEBUG:
                print(thing)
        list.__init__(self, selfList)
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
                return choice
            choice += 1
        return self[choice]
    
    

baseTypeList = BetterList("Attack", "Defense")

target1 = WeightedChoice("Select", 25)

baseTargetList = EvenBetterList(target1, WeightedChoice("Self", 25), WeightedChoice("Closest", 25), WeightedChoice("Farthest", 25))
baseZoneList = EvenBetterList(WeightedChoice("SingleTile", 25), WeightedChoice("Cross", 25), WeightedChoice("X", 25), WeightedChoice("AOE", 25))

baseAttackList = EvenBetterList(WeightedChoice("Fire", 33), WeightedChoice("Physical", 33), WeightedChoice("Poison", 33)) #Porbably want to add more stuff here
baseBuffList = BetterList(WeightedChoice("Hunger", 25), WeightedChoice("AttackStat", 25), WeightedChoice("DefenseStat", 25), WeightedChoice("Speed", 25))
baseHealList = BetterList(WeightedChoice("HP", 25), WeightedChoice("MP", 25), WeightedChoice("CureFire", 25), WeightedChoice("CurePoison", 25))

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
def createEffect():
    typeList = copy.copy(baseTypeList)
    targetList = copy.copy(baseTargetList)
    zoneList = copy.copy(baseZoneList)
    
    attackList = copy.copy(baseAttackList)
    buffList = copy.copy(baseBuffList)
    healList = copy.copy(baseHealList)
    
    type = typeList.randFrom()
    
    
    
    