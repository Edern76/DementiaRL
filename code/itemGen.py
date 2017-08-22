import copy
import code.custom_except
from random import randint
from code.constants import *
import colors
import code.dunbranches as dBr
from math import *

#GameObject template: x, y, char, name, color, blocks, Fighter, AI, Player, Ghost, flying, Item, alwaysVisible, darkColor, Equipment, pName, Essence,
#                     socialComp, shopComp, questList, Stairs, alwaysAlwaysVisible, size, sizeChar, sizeColor, sizeDarkColor, smallChar, ProjectileComp

#Item template: useFunction, arg1, arg2, arg3, stackable, amount, weight, description, pic, itemtype, identified, unIDName, unIDpName, unIDdesc, useText

#Equipment template: slot, type, powerBonus, armorBonus, maxHP_Bonus, accuracyBonus, evasionBonus, criticalBonus, maxMP_Bonus, strengthBonus, dexterityBonus,
#                    vitalityBonus, willpowerBonus, ranged, rangedPower, maxRange, ammo, meleeWeapon, armorPenetrationBonus, slow, enchant, staminaBonus

rarity = {'junk': 15, 'common': 50, 'uncommon': 15, 'rare': 10, 'epic': 7, 'legendary': 3}

itemTypes = ['weapon', 'potion', 'armor', 'shield', 'food', 'scroll', 'spellbook', 'ranged weapon']

weaponTypes = ['dagger', 'sword', 'axe', 'flail', 'mace', 'hammer', 'gloves', 'spear']
weaponSize = {'dagger': {'dagger': 70, 'stiletto': 15, 'misericorde': 15}, 'sword': {'shortsword': 40, 'longsword': 45, 'great sword': 15}, 'axe': {'axe': 85, 'great axe': 15}, 'flail': {'flail': 85, 'great flail': 15}, 'mace': {'mace': 85, 'great mace': 5, 'morning star': 10}, 'hammer': {'warhammer': 85, 'maul': 15}, 'gloves': {'cestus': 85, 'knuckles': 10, 'fighting claws': 5}, 'spear': {'spear': 85, 'halberd': 15}}
weaponAdj = {'dagger': {'regular': 70, 'fast': 5, 'sharp': 10, 'rusty': 15}, 'sword': {'regular': 70, 'sharp': 15, 'rusty': 15}, 'axe': {'regular': 70, 'sharp': 15, 'rusty': 15}, 'flail': {'regular': 70, 'rusty': 15, 'two-headed': 10, 'three-headed': 5}, 'mace': {'regular': 70, 'weighed': 15, 'rusty': 15}, 'hammer': {'regular': 70, 'spiked': 15, 'rusty': 15}, 'gloves': {'regular': 70, 'weighed': 15, 'rusty': 15}, 'spear': {'regular': 70, 'sharp': 15, 'rusty': 15}}
weaponAttributes = {'dagger': ('light', {'pow': 6})}


rangedWeaponTypes = ['bow', 'crossbow', 'throwing axe', 'throwing knife', 'pistol', 'rifle', 'javelin']

armorTypes = {'cloth': 25, 'leather': 40, 'chainmail': 20, 'scale': 10, 'plate': 5}
armorSlots = ['head', 'arms', 'legs', 'chest', 'feet', 'hands']

potionTypes = ['heal HP', 'heal MP', 'heal stamina', 'cure poison', 'poison', 'cure fire', 'fire', 'frost', 'speed fast', 'speed slow', 'strength', 'constitution', 'dexterity', 'willpower']

shieldTypes = ['buckler', 'round', 'heater', 'war-door']
shieldMaterials = ['leather', 'wooden', 'iron', 'steel']

foodTypes = ['bread', 'herbs', 'rMeat', 'pie', 'pasta', 'meat', 'hBaguette']

class GameObjectTemplate:
    def __init__(self, char, name, color, Item, Equipment, pName):
        self.name = name
        self.pName = pName
        self.char = char
        self.color = color
        self.Item = Item
        self.Equipment = Equipment
    
    def __str__(self):
        print('{} ({} {})'.format(self.name, self.color, self.char))
        if self.Item:
            print(self.Item)
        if self.Equipment:
            print(self.Equipment)


class ItemTemplate:
    def __init__(self, useFunction, arg1, arg2, arg3, stackable, amount, weight, description, pic, itemtype, useText):
        self.useFunction = useFunction
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.stackable = stackable
        self.amount = amount
        self.weight = weight
        self.description = description
        self.pic = pic
        self.itemType = itemtype
        self.useText = useText
    
    def __str__(self):
        print('{} weighing {}, can be used by {} which does {}, it is described as "{}"'.format(self.itemType, str(self.wheight), self.useText, str(self.useFunction), self.description))


class EquipmentTemplate:
    def __init__(self, slot, type, powerBonus, armorBonus, maxHP_Bonus, accuracyBonus, evasionBonus, criticalBonus, maxMP_Bonus, strengthBonus, dexterityBonus,
                vitalityBonus, willpowerBonus, ranged, rangedPower, maxRange, ammo, meleeWeapon, armorPenetrationBonus, slow, enchant, staminaBonus):
        self.slot = slot
        self.type = type
        self.powerBonus = powerBonus
        self.armorBonus = armorBonus
        self.maxHP_Bonus = maxHP_Bonus
        self.accuracyBonus = accuracyBonus
        self.evasionBonus = evasionBonus
        self.criticalBonus = criticalBonus
        self.maxMP_Bonus = maxMP_Bonus
        self.strengthBonus = strengthBonus
        self.dexterityBonus = dexterityBonus
        self.vitalityBonus = vitalityBonus
        self.willpowerBonus = willpowerBonus
        self.ranged = ranged
        self.rangedPower = rangedPower
        self.maxRange = maxRange
        self.ammo = ammo
        self.meleeWeapon = meleeWeapon
        self.armorPenetrationBonus = armorPenetrationBonus
        self.slow = slow
        self.enchant = enchant
        self.staminaBonus = staminaBonus
    
    def __str__(self):
        print('A {} equipped on {}, it is {} a melee weapon and {} a ranged weapon. It has some boni:'.format(self.type, self.slot, str(self.meleeWeapon), str(self.ranged)))
        
        if self.powerBonus != 0:
            print('power:' + str(self.powerBonus))
        if self.armorBonus != 0:
            print('armor:' + str(self.armorBonus))
        if self.maxHP_Bonus != 0:
            print('HP:' + str(self.maxHP_Bonus))
        if self.accuracyBonus != 0:
            print('acc:' + str(self.accuracyBonus))
        if self.evasionBonus != 0:
            print('evasion:' + str(self.evasionBonus))
        if self.criticalBonus != 0:
            print('crit:' + str(self.criticalBonus))
        if self.maxMP_Bonus != 0:
            print('MP:' + str(self.maxMP_Bonus))
        if self.strengthBonus != 0:
            print('strength:' + str(self.strengthBonus))
        if self.dexterityBonus != 0:
            print('dex:' + str(self.dexterityBonus))
        if self.vitalityBonus != 0:
            print('const:' + str(self.constitutionBonus))
        if self.willpowerBonus != 0:
            print('will:' + str(self.willpowerBonus))
        if self.rangedPower != 0 and self.ranged:
            print('ranged power:' + str(self.rangedPower))
        if self.maxRange != 0 and self.ranged:
            print('range:' + str(self.maxRange))
        if self.armorPenetrationBonus != 0:
            print('AP:' + str(self.armorPenetrationBonus))
        if self.staminaBonus != 0:
            print('stamina:' + str(self.staminaBonus))
        if self.slow:
            print('slow!')

class EnchantmentTemplate:
    def __init__(self, name, functionOnAttack = None, buffOnOwner = [], buffOnTarget = [], damageOnOwner = 0, damageOnTarget = 0, power = 0, acc = 0, evas = 0, arm = 0, hp = 0, mp = 0, crit = 0, ap = 0, stren = 0, dex = 0, vit = 0, will = 0, stamina = 0):
        self.name = name
        self.functionOnAttack = functionOnAttack
        self.buffOnOwner = buffOnOwner
        self.buffOnTarget = buffOnTarget
        self.damageOnOwner = damageOnOwner
        self.damageOnTarget = damageOnTarget
        self.power = power
        self.acc = acc
        self.evas = evas
        self.arm = arm
        self.hp = hp
        self.mp = mp
        self.crit = crit
        self.ap = ap
        self.stren = stren
        self.dex = dex
        self.vit = vit
        self.will = will
        self.stamina = stamina


def randItemFrom(randList):
    return randList[randint(0, len(randList) - 1)]

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
    for value in chances:
        if value < 0:
            print(value)
            print(chancesDictionnary.keys())
            print(chancesDictionnary)
            raise ValueError("Negative value in dict")
    strings = list(chancesDictionnary.keys())
    return strings[randomChoiceIndex(chances)]

def generateMeleeWeapon(weaponType = None):
    if weaponType is None:
        weaponType = randItemFrom(weaponTypes)
        print(weaponType)
    
    weapon = randomChoice(weaponSize[weaponType])

if __name__ == '__main__':
    for loop in range(10):
        print(generateMeleeWeapon())
        print()






