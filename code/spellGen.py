from random import randint
from code.constants import *

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


def createEffect():
    typeList = BetterList("Attack", "Buff", "Heal")
    targetList = BetterList("Select", "Self", "Closest", "Farthest")
    zoneList = BetterList("SingleTile", "Cross", "AOE")
    
    attackList = BetterList("Fire", "Physical", "Poison")
    buffList = BetterList("Hunger", "AttackUp")
    healList = BetterList("HP", "MP", "CureFire", "CurePoison")
    