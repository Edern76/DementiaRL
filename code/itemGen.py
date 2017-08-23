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

rarityList = ['junk', 'common', 'uncommon', 'rare', 'epic', 'legendary']

class Rarity:
    def __init__(self, rarity):
        self.rarity = rarity
        self.index = rarityList.index(self.rarity)
    
    def __str__(self):
        return self.rarity
    
    def __eq__(self, string):
        return self.rarity == string
    
    def __ne__(self, string):
        return self.rarity != string
    
    def __lt__(self, string):
        return self.index < rarityList.index(string)
    
    def __le__(self, string):
        return self.index < rarityList.index(string)
    
    def __gt__(self, string):
        return self.index < rarityList.index(string)
    
    def __ge__(self, string):
        return self.index < rarityList.index(string)
    
    def __hash__(self):
        return self.index


junk = Rarity('junk')
common = Rarity('common')
uncommon = Rarity('uncommon')
rare = Rarity('rare')
epic = Rarity('epic')
legendary = Rarity('legendary')

rarity = {junk: 15, common: 50, uncommon: 15, rare: 10, epic: 7, legendary: 3}
raritySmallAdd = {'junk': -2, 'common': 0, 'uncommon': 2, 'rare': 3, 'epic': 5, 'legendary': 8}
rarityBigAdd = {'junk': -10, 'common': 0, 'uncommon': 10, 'rare': 15, 'epic': 20, 'legendary': 30}


itemTypes = ['weapon', 'potion', 'armor', 'shield', 'food', 'scroll', 'spellbook', 'ranged weapon']


weaponTypes = ['dagger', 'sword', 'axe', 'flail', 'mace', 'hammer', 'gloves', 'spear']

weaponSize = {'dagger': {'dagger': 70, 'stiletto': 15, 'misericorde': 15},
              'sword': {'shortsword': 35, 'longsword': 40, 'katana': 15, 'great sword': 10},
              'axe': {'axe': 85, 'great axe': 15},
              'flail': {'flail': 85, 'great flail': 15},
              'mace': {'mace': 85, 'great mace': 5, 'morning star': 10},
              'hammer': {'warhammer': 85, 'maul': 15},
              'gloves': {'cestus': 85, 'knuckles': 10, 'fighting claws': 5},
              'spear': {'spear': 85, 'halberd': 15}}

weaponDictTemplate = ['pow', 'arm', 'HP', 'acc', 'ev', 'crit', 'MP', 'strength', 'dex', 'vit', 'will', 'ap', 'slow', 'stam']
weaponAttributes = {'dagger': {'type': 'light', 'slot': 'one handed', 'pic': 'dagger.xp', 'pow': 6, 'acc': 10, 'ev': 5, 'weight': 0.5},
                    'stiletto': {'type': 'light', 'slot': 'one handed', 'pic': 'stiletto.xp', 'pow': 5, 'acc': 15, 'ev': 5, 'crit': 5, 'weight': 0.5},
                    'misericorde': {'type': 'light', 'slot': 'one handed', 'pic': 'dagger.xp', 'pow': 6, 'acc': 5, 'ev': 5, 'ap': 1, 'weight': 0.5}
                    }

rarityCombo = {'epic': {'2 passive': 25, '1 active': 10, 'none': 65}, 'legendary': {'2 passive': 20, '3 passive': 40, '2 passive + 1 active': 40, '1 active': 20}}
weaponAdj = {'dagger': {'junk': {'regular': 50, 'rusty': 50},
                        'common': {'regular': 80, 'rusty': 10, 'fast': 5, 'sharp': 5},
                        'uncommon': {'regular': 71, 'rusty': 5, 'fast': 17, 'sharp': 17},
                        'rare': {'regular': 50, 'rusty': 2, 'precise': 12, 'fast': 12, 'sharp': 12, 'discrete': 12}, 
                        'epic': {'regular': 30, 'precise': 9, 'fast': 9, 'sharp': 9, 'poisoned': 9, 'burning': 9, 'frost': 8, 'electric': 8, 'discrete': 9},
                        'legendary': {'deadly': 10, 'precise': 10, 'fast': 10, 'sharp': 10, 'poisoned': 10, 'leech': 10, 'burning': 10, 'frost': 10, 'electric': 10, 'discrete': 10}},
             
             'sword': {'regular': 70, 'sharp': 15, 'rusty': 15},
             
             'axe': {'regular': 70, 'sharp': 15, 'rusty': 15},
             
             'flail': {'regular': 70, 'rusty': 15, 'two-headed': 10, 'three-headed': 5},
             
             'mace': {'regular': 70, 'weighed': 15, 'rusty': 15},
             
             'hammer': {'regular': 70, 'spiked': 15, 'rusty': 15},
             
             'gloves': {'regular': 70, 'weighed': 15, 'rusty': 15},
             
             'spear': {'regular': 70, 'sharp': 15, 'rusty': 15}}


rangedWeaponTypes = ['bow', 'crossbow', 'throwing axe', 'throwing knife', 'pistol', 'rifle', 'javelin']


armorTypes = {'cloth': 25, 'leather': 40, 'chainmail': 20, 'scale': 10, 'plate': 5}
armorSlots = ['head', 'arms', 'legs', 'chest', 'feet', 'hands']


potionTypes = ['heal HP', 'heal MP', 'heal stamina', 'cure poison', 'poison', 'cure fire', 'fire', 'frost', 'speed fast', 'speed slow', 'strength', 'constitution', 'dexterity', 'willpower']


shieldTypes = ['buckler', 'round', 'heater', 'war-door']
shieldMaterials = ['leather', 'wooden', 'iron', 'steel']


foodTypes = ['bread', 'herbs', 'rMeat', 'pie', 'pasta', 'meat', 'hBaguette']

class BetterInt:
    def __init__(self, value):
        self.value = value
    
    def __int__(self):
        return self.value
    
    def __iadd__(self, other):
        self.value = self.value + other
    
    def __add__(self, other):
        return self.value + other
    
    def __str__(self):
        return str(self.value)
    
    def __lt__(self, other):
        return self.value < other
    
    def __ne__(self, other):
        return self.value != other

'''
class BetterBool:
    def __init__(self, boolean):
        self.bool = boolean
    
    def __str__(self):
        return str(self.bool)
    
    def __bool__(self):
        return self.bool

class BetterStr:
    def __init__(self, string):
        self.string = string
    
    def __str__(self):
        return self.string
'''
   
class GameObjectTemplate:
    def __init__(self, char, name, color, Item = None, Equipment = None, pName = None):
        self.name = name
        self.pName = pName
        self.char = char
        self.color = color
        self.Item = Item
        self.Equipment = Equipment
    
    def __str__(self):
        text = '{} ({} {})'.format(self.name, self.color, self.char)
        if self.Item:
            text += '\n' + str(self.Item)
        if self.Equipment:
            text += '\n' + str(self.Equipment)
        return text


class ItemTemplate:
    def __init__(self, useFunction, arg1 = None, arg2 = None, arg3 = None, stackable = False, amount = 1, weight = 0, description = 'Placeholder', pic = 'trollMace.xp', itemtype = None, useText = 'Use'):
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
        return '{} weighing {}, can be used by {} which does {}, it is described as "{}"'.format(self.itemType, str(self.weight), self.useText, str(self.useFunction), self.description)

equipmentStatsStrings = ['pow', 'arm', 'HP', 'acc', 'ev', 'crit', 'MP', 'strength', 'dex', 'vit', 'will', 'rangedPow', 'maxRange', 'ap', 'stam']


class EquipmentTemplate:
    def __init__(self, slot, type, powerBonus=0, armorBonus=0, maxHP_Bonus=0, accuracyBonus=0, evasionBonus=0, criticalBonus=0, maxMP_Bonus=0,
                strengthBonus=0, dexterityBonus=0, vitalityBonus=0, willpowerBonus=0, ranged=False, rangedPower=0, maxRange=0, ammo=None, meleeWeapon=False,
                armorPenetrationBonus=0, slow=False, enchant=None, staminaBonus=0):
        self.slot = slot
        self.type = type
        self.powerBonus = BetterInt(powerBonus)
        self.armorBonus = BetterInt(armorBonus)
        self.maxHP_Bonus = BetterInt(maxHP_Bonus)
        self.accuracyBonus = BetterInt(accuracyBonus)
        self.evasionBonus = BetterInt(evasionBonus)
        self.criticalBonus = BetterInt(criticalBonus)
        self.maxMP_Bonus = BetterInt(maxMP_Bonus)
        self.strengthBonus = BetterInt(strengthBonus)
        self.dexterityBonus = BetterInt(dexterityBonus)
        self.vitalityBonus = BetterInt(vitalityBonus)
        self.willpowerBonus = BetterInt(willpowerBonus)
        self.ranged = ranged
        self.rangedPower = BetterInt(rangedPower)
        self.maxRange = BetterInt(maxRange)
        self.ammo = ammo
        self.meleeWeapon = meleeWeapon
        self.armorPenetrationBonus = BetterInt(armorPenetrationBonus)
        self.slow = slow
        self.enchant = enchant
        self.staminaBonus = BetterInt(staminaBonus)
    
    @property
    def stats(self):
        return [self.powerBonus, self.armorBonus, self.maxHP_Bonus, self.accuracyBonus, self.evasionBonus, self.criticalBonus, self.maxMP_Bonus, self.strengthBonus, self.dexterityBonus, self.vitalityBonus, self.willpowerBonus, self.rangedPower, self.maxRange, self.armorPenetrationBonus, self.staminaBonus]
    
    def __str__(self):
        text =  'A {} equipped on {}, it is {} a melee weapon and {} a ranged weapon. It has some boni:'.format(self.type, self.slot, str(self.meleeWeapon), str(self.ranged))
        
        if self.powerBonus != 0:
            text += '\n' + str('power:' + str(self.powerBonus))
        if self.armorBonus != 0:
            text += '\n' + str('armor:' + str(self.armorBonus))
        if self.maxHP_Bonus != 0:
            text += '\n' + str('HP:' + str(self.maxHP_Bonus))
        if self.accuracyBonus != 0:
            text += '\n' + str('acc:' + str(self.accuracyBonus))
        if self.evasionBonus != 0:
            text += '\n' + str('evasion:' + str(self.evasionBonus))
        if self.criticalBonus != 0:
            text += '\n' + str('crit:' + str(self.criticalBonus))
        if self.maxMP_Bonus != 0:
            text += '\n' + str('MP:' + str(self.maxMP_Bonus))
        if self.strengthBonus != 0:
            text += '\n' + str('strength:' + str(self.strengthBonus))
        if self.dexterityBonus != 0:
            text += '\n' + str('dex:' + str(self.dexterityBonus))
        if self.vitalityBonus != 0:
            text += '\n' + str('const:' + str(self.vitalityBonus))
        if self.willpowerBonus != 0:
            text += '\n' + str('will:' + str(self.willpowerBonus))
        if self.rangedPower != 0 and self.ranged:
            text += '\n' + str('ranged power:' + str(self.rangedPower))
        if self.maxRange != 0 and self.ranged:
            text += '\n' + str('range:' + str(self.maxRange))
        if self.armorPenetrationBonus != 0:
            text += '\n' + str('AP:' + str(self.armorPenetrationBonus))
        if self.staminaBonus != 0:
            text += '\n' + str('stamina:' + str(self.staminaBonus))
        if self.slow:
            text += '\n' + str('slow!')
        
        return text

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
    
    weaponDict = weaponAttributes[weapon]
    weaponEquipment = EquipmentTemplate(weaponDict['slot'], weaponDict['type'] + ' ' + weaponType, meleeWeapon = True)
    
    weaponRarity = randomChoice(rarity)
    stringRarity = str(weaponRarity)
    print(weaponRarity)
    
    adj = []
    passiveNumber = 1
    active = False
    try:
        rareCombo = randomChoice(rarityCombo[stringRarity])
    except:
        rareCombo = 'none'
    
    if '2 passive' in rareCombo:
        passiveNumber = 2
    if '3 passive' in rareCombo:
        passiveNumber = 3
    if 'active' in rareCombo:
        active = True
    
    adjDict = weaponAdj[weaponType][stringRarity]
    for i in range(passiveNumber):
        bonus = randomChoice(adjDict)
        while bonus in adj:
            bonus = randomChoice(adjDict)
        adj.append(bonus)
    
    if active:
        weaponAbility = randItemFrom(adj)
    
    addToName = ''
    for adjective in adj:
        if adjective != 'regular':
            addToName += adjective + ' '
    
    endName = ''
    if active:
        endName = ' of ' + weaponAbility
    
    i = 0
    for stat in weaponEquipment.stats:
        moddedStat = equipmentStatsStrings[i]
        try:
            dictToUse = raritySmallAdd
            if moddedStat == 'HP' or moddedStat == 'MP' or moddedStat == 'stam':
                dictToUse = rarityBigAdd
            stat.value = weaponDict[equipmentStatsStrings[i]] + randint(-2 + dictToUse[stringRarity], 2 + dictToUse[stringRarity])
            if stat < 0:
                stat.value = 0
        except:
            pass
        i += 1
    
    try:
        weaponEquipment.slow = weaponDict['slow']
    except:
        pass
    
    if 'light' in weaponEquipment.type:
        char = '-'
    else:
        char = '/'
        
    weaponItem = ItemTemplate('Equip', weight = weaponDict['weight'], itemtype = 'weapon', useText = 'Equip')
    try:
        weaponItem.description = weaponDict['desc']
    except:
        pass
    try:
        weaponItem.pic = weaponDict['pic']
    except:
        pass
    
    weaponObject = GameObjectTemplate(char, addToName + weapon + endName, colors.silver, Item = weaponItem, Equipment = weaponEquipment)
    return weaponObject

if __name__ == '__main__':
    for loop in range(10):
        print(generateMeleeWeapon('dagger'))
        print()






